#!/usr/bin/env python3
# sigrok-cli -i trace.sr -P parallel:d0=D0:d1=D1:d2=D2:d3=D3:clk=D7:clock_edge=either:endianness=little -A parallel=item > app/trace.txt

import struct
import sys

from box import Box

def parse_varint(data):
    '''Parse an integer where the top bit is the continuation bit.
    Returns value and number of parsed bytes.'''
    v = 0
    for i, b in enumerate(data):
        v |= (b & 0x7f) << (i * 7)
        if b & 0x80 == 0:
            return v, i+1
    return v, len(data)

def trace(msg):
    #print(msg, file=sys.stderr)
    pass

def debug(msg):
    print(msg, file=sys.stderr)

# Assume width of trace is no more than 8 bits
class TPIU:
    def __init__(self, data_handler, size=4):
        self.chunk_size = size
        self.chunks = []
        self.chunk_offset = 0
        self.chunks_per_byte = 8 // self.chunk_size

        self.sync = [(1 << size) - 1] * (16 // size)
        self.sync[-1] &= (0x7fff >> (16 - size))

        self.frame_offset = 0
        self._trace_id = 0

        self.data_handler = data_handler

    def write(self, chunk):
        self.chunks.append(chunk)
        self.chunk_offset += 1

        if len(self.chunks) >= len(self.sync) and self.chunks[-len(self.sync):] == self.sync:
            # Works for either full or halfword sync
            trace(f'Found sync @ chunk {self.chunk_offset}')
            self.chunks = []
            return

        if len(self.chunks) * self.chunk_size == 128:
            frame = bytearray(16)
            for i in range(16):
                b = 0
                for j in range(self.chunks_per_byte):
                    chunk = (i * self.chunks_per_byte) + j
                    b |= self.chunks[chunk] << (j * self.chunk_size)

                frame[i] = b

            self.chunks = []
            trace(f'Got frame {self.frame_offset}: {frame}')
            self._decode_frame(frame)

            self.frame_offset += 1

    def _decode_frame(self, frame):
        aux = frame[15]
        for i in range(0, 15, 2):
            deferred_id = None

            # Deal with mixed bytes first
            aux_bit = (aux >> (i // 2)) & 1
            if frame[i] & 1 == 1:
                # Frame is a new ID
                new_id = frame[i] >> 1
                if aux_bit == 0:
                    # Very next byte uses the new ID (must be data as)
                    self._trace_id = new_id
                else:
                    # Very next byte uses the old ID (next data byte uses the
                    # new ID - don't have to worry about this happening in byte
                    # 14 as it can never happen in that case)
                    deferred_id = new_id
            else:
                # Frame is data, aux it is lo bit
                self._emit_byte(frame[i] | aux_bit)

            if i != 14:
                # Plain data bytes
                self._emit_byte(frame[i+1])

            if deferred_id is not None:
                self._trace_id = deferred_id

    def _emit_byte(self, b):
        if self._trace_id == 0:
            trace(f'Got null trace byte {b:#04x}')
            return

        trace(f'Got data byte for trace ID {self._trace_id:#04x}: {b:#04x}')

        if self.data_handler:
            self.data_handler(self._trace_id, bytes([b]))

class ETM:
    def __init__(self):
        self.buf = bytearray()

        self.state = 'unknown'
        self.nonsec = False
        self.hyp = False
        self.pc = 0

    @classmethod
    def get_header_type(cls, h):
        if h == 0x00:
            return 'a_sync'
        elif h in (0x08, 0x70):
            return 'i_sync'
        elif h == 0x0c:
            return 'trigger'
        #elif h == 0x04:
        #    return 'cyclecount'
        elif h & 0x01 == 0x01:
            return 'branch'
        elif h & 0x81 == 0x80:
            return 'p_header'

        return 'unknown'

    def __handle_data(self, data):
        t = self.get_header_type(data[0])
        return getattr(self, f'_handle_{t}')(data)

    def write(self, data):
        self.buf.extend(data)

        if self.__handle_data(self.buf):
            self.buf = bytearray()

    def _handle_unknown(self, data):
        debug(f'Unknown packet header {data[0]:#04x}')
        return True

    def _handle_a_sync(self, data):
        if data[-1] == 0b10000000:
            debug(f'Got A-sync (after {len(data)-1} zeros)')
            return True

        return False

    def _handle_trigger(self, data):
        debug('ETM trigger')
        return True

    def _handle_i_sync(self, data):
        # Don't worry about Context ID
        contextid_bytes = 0
        ret = Box()

        if len(data) < 6:
            # Any I-sync must have at least 6 bytes
            return False

        if data[0] == 0x08: # No cycle count.
            ret.cycles = None
            # Index to info byte.
            info_offset = 1 + contextid_bytes
        elif data[0] == 0x70: # With cycle count.
            ret.cycles, cycles_len = parse_varint(data[1:6])
            info_offset = 1 + cycles_len + contextid_bytes

        if len(data) < info_offset + 1 + 4:
            return False

        info = data[info_offset]
        addr, = struct.unpack('<I', data[info_offset + 1:info_offset + 1 + 4])

        reason_code = (info >> 5) & 0b11
        ret.reason = ('Periodic', 'Tracing enabled', 'After overflow', 'Exit from debug')[reason_code]
        jazelle = (info >> 4) & 0b1
        nonsec = (info >> 3) & 0b1
        altisa = (info >> 2) & 0b1
        hyp = (info >> 1) & 0b1
        thumb = addr & 1
        addr &= 0xfffffffe

        self.pc = ret.pc = addr
        if jazelle:
            self.state = 'jazelle'
        elif thumb:
            if altisa:
                self.state = 'thumbee'
            else:
                self.state = 'thumb'
        else:
            self.state = 'arm'

        self.nonsec = True if nonsec else False
        self.hyp = True if hyp else False

        if info & 0x80:
            debug('Warning: LSiP I-sync unimplemented')

        debug(ret)
        return True

    def _handle_p_header(self, data):
        ret = Box()

        # Only non cycle-accurate mode supported.
        if data[0] & 0x83 == 0x80:
            # Format 1
            debug('Format 1 P-Header')
            ret.skipped = (data[0] >> 6) & 1
            ret.executed = (data[0] >> 2) & 15
        elif data[0] & 0xf3 == 0x82:
            debug('Format 2 P-Header')
            # Format 2 (bit 3 is whether or not instruction 1 executed,
            # likewise for bit 2)
            i1 = (data[0] >> 3) & 1
            i2 = (data[0] >> 2) & 1

            ret.skipped = i1 + i2
            ret.executed = 2 - ret.skipped
        else:
            debug('Warning: Unknown P-header format')

        debug(f'P-Header {ret}')

        return True

    def _handle_branch(self, data):
        ret = Box()



        return True

etm = ETM()

def handle_data(trace_id, data):
    if trace_id == 0x7d:
        print('Triggered')
    elif trace_id == 69:
        etm.write(data)
    else:
        print(f'Unknown trace ID {trace_id}')

tpiu = TPIU(handle_data, size=4)

for line in sys.stdin:
    split = line.split(' ')
    nyb = int(split[1], 16)

    tpiu.write(nyb)
