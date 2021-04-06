from collections.abc import Mapping
import importlib.util
import io
import os

from box import Box
from elftools.elf.elffile import ELFFile
from google.protobuf.internal.decoder import _DecodeVarint32 as decodeVarint32
from google.protobuf.internal.encoder import _VarintBytes as encodeVarint

from .step import Step

def get_pb(gem5: str):
    path = os.path.join(gem5, 'build/ARM/perfgrade/proto/trace_pb2.py')
    spec = importlib.util.spec_from_file_location('trace_pb2', path)
    pb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pb)

    return pb

# Utility method to generate fake trace data that will produce a valid cycle count
def generate_dummy_cycles(f: io.IOBase, gem5: str, start: int=0, stop: int=0, cycles: int=0):
    pb = get_pb(gem5)
    stream = TraceStream(f, pb, write=True)

    header = pb.Header()
    header.tick_freq = 1000000
    stream.write_message(header)

    a = pb.ExecTrace()
    a.tick = a.cycle = 0
    a.pc = start
    a.predicate = True
    stream.write_message(a)

    b = pb.ExecTrace()
    b.tick = b.cycle = cycles
    b.pc = stop
    b.predicate = True
    stream.write_message(b)

class TraceStream:
    MAGIC = b'gem5'

    def __init__(self, f: io.IOBase, pb, write=False):
        self._fd = f
        self.pb = pb

        if write:
            self._fd.write(self.MAGIC)
        else:
            if self._fd.read(4) != TraceStream.MAGIC:
                raise ValueError('Invalid magic')

            self.header = self._read_message(self.pb.Header)

    def _read_varint32(self):
        """Read a varint from file, parse it, and return the decoded integer.
        """
        buff = self._fd.read(1)
        if buff == b'':
            return 0

        while (bytearray(buff)[-1] & 0x80) >> 7 == 1:  # while the MSB is 1
            new_byte = self._fd.read(1)
            if new_byte == b'':
                raise EOFError("unexpected EOF")
            buff += new_byte

        varint, _ = decodeVarint32(buff, 0)

        return varint

    def _read_message(self, cls):
        size = self._read_varint32()
        if size == 0:
            return None

        data = self._fd.read(size)
        return cls.FromString(data)

    def reset(self):
        self._fd.seek(4, os.SEEK_SET)

    def traces(self):
        self.reset()
        while t := self._read_message(self.pb.ExecTrace):
            yield t

    def __iter__(self):
        return self.traces()

    def _write_varint(self, v):
        data = encodeVarint(v)
        self._fd.write(data)

    def write_message(self, msg):
        data = msg.SerializeToString()

        self._write_varint(len(data))
        self._fd.write(data)

class AugmentedTraceStream:
    def __init__(self, stream: TraceStream, elf_file: io.IOBase, basedir: str=''):
        self.stream = stream
        self.basedir = basedir

        self.cache = {}
        elf = ELFFile(elf_file)
        if not elf.has_dwarf_info():
            raise ValueError(f'ELF file {elf} has no DWARF info')

        self.dwarf = elf.get_dwarf_info()

    def _lpe_filename(self, line_prog, file_index):
        # Retrieving the filename associated with a line program entry
        # involves two levels of indirection: we take the file index from
        # the LPE to grab the file_entry from the line program header,
        # then take the directory index from the file_entry to grab the
        # directory name from the line program header. Finally, we
        # join the (base) filename from the file_entry to the directory
        # name to get the absolute filename.
        lp_header = line_prog.header
        file_entries = lp_header['file_entry']

        # File and directory indices are 1-indexed.
        file_entry = file_entries[file_index - 1]
        dir_index = file_entry['dir_index']

        # A dir_index of 0 indicates that no absolute directory was recorded during
        # compilation; return just the basename.
        if dir_index == 0:
            path = file_entry.name.decode('utf8')
        else:
            directory = lp_header['include_directory'][dir_index - 1]
            path = os.path.join(directory, file_entry.name).decode('utf8')

        return os.path.normpath(os.path.join(self.basedir, path))

    def _addr_to_line(self, addr):
        if addr in self.cache:
            return self.cache[addr]

        for cu in self.dwarf.iter_CUs():
            line_prog = self.dwarf.line_program_for_CU(cu)
            prev_state = None
            for e in line_prog.get_entries():
                if e.state is None:
                    continue
                if e.state.end_sequence:
                    prev_state = None
                    continue

                if prev_state and prev_state.address <= addr < e.state.address:
                    filename = self._lpe_filename(line_prog, prev_state.file)
                    line = prev_state.line

                    self.cache[addr] = (filename, line)
                    return filename, line

                prev_state = e.state

        return None, None

    def traces(self):
        for t in self.stream:
            filename, line = self._addr_to_line(t.pc)
            yield Box(orig=t, filename=filename, line=line)

    def __iter__(self):
        return self.traces()

class Traces(Step):
    description = 'Load gem5 traces'

    _trace_file = None

    def run(self, ctx: Mapping):
        self._trace_file = open(self.input['file'], 'rb')
        self.output = TraceStream(self._trace_file, get_pb(self.input['gem5']))

    def close(self):
        if self._trace_file:
            self._trace_file.close()

class AugmentTraces(Step):
    description = 'Augment trace information'

    _elf_file = None

    def run(self, ctx: Mapping):
        self._elf_file = open(self.input['elf'], 'rb')
        self.output = AugmentedTraceStream(self.input['traces'], self._elf_file, self.input.get('basedir', ''))

    def close(self):
        if self._elf_file:
            self._elf_file.close()
