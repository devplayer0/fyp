import abc
from collections.abc import Iterable, Mapping
import copy
import re
import queue
import time
import logging
import sched
import threading
import errno
import os
import subprocess
import tempfile
import pkg_resources

from box import Box
from usb.core import USBError
from pyocd.coresight.discovery import LOG as PyOCDDiscoveryLogger
from pyocd.probe.stlink.detect.linux import LOG as PyOCDSTLINKDetectLogger
from pyocd.core.target import Target as PyOCDTarget
from pyocd.probe.aggregator import DebugProbeAggregator
from pyocd.core.session import Session as PyOCDSession
from pyocd.flash.file_programmer import FileProgrammer as PyOCDProgrammer

from . import util
from .step import Step
from . import tracing

class TestData:
    def __init__(self, addr: int, data: bytes, when: int=None):
        self.addr = addr
        self.data = data
        self.when = when

class Evaluator(abc.ABC):
    def __init__(self, firmware: str, logger, timeout=None, test_data: dict=None, dump_ranges: Iterable=None,
            debug: bool=False):
        self.firmware = firmware
        self.logger = logger
        self.debug = debug
        self.timeout = timeout

        if test_data:
            self.test_data = TestData(test_data['addr'], test_data['data'], when=test_data.get('when'))

        self.dump_ranges = []
        if dump_ranges:
            self.dump_ranges = list(map(Box, dump_ranges))

    @abc.abstractmethod
    def run(self):
        pass

    def cleanup(self):
        pass

class Simulator(Evaluator):
    _out_dir = None

    def __init__(self, *args, gem5: str='gem5', variant: str='fast', config: str='stm32f4', extra_args: list=None, **kwargs):
        super().__init__(*args, **kwargs)

        config_path = pkg_resources.resource_filename(__name__, os.path.join('gem5_config', f'{config}.py'))
        self._out_dir = tempfile.TemporaryDirectory(suffix='.m5out')
        self._args = [os.path.join(gem5, f'build/ARM/gem5.{variant}'), '--outdir', self._out_dir.name, config_path, self.firmware]
        if self.dump_ranges:
            self._args += ['--dump-range', ','.join(map(lambda r: f'{r.start:#010x}:{r.size:#x}', self.dump_ranges))]
        if extra_args:
            self._args += extra_args

    def run(self):
        if self.test_data:
            test_file = tempfile.NamedTemporaryFile(mode='wb', suffix='.data.bin')
            test_file.write(self.test_data.data)
            test_file.flush()

            self._args += ['--test-data', test_file.name, '--test-addr', f'{self.test_data.addr:#010x}']
            if self.test_data.when is not None:
                self._args += ['--test-pc', f'{self.test_data.when:#010x}']

        try:
            kwargs = Box(timeout=self.timeout)
            if not self.debug:
                kwargs.stderr = kwargs.stdout = subprocess.DEVNULL

            subprocess.check_call(self._args, **kwargs)
        finally:
            test_file.close()

        dump_data = []
        if self.dump_ranges:
            for i in range(len(self.dump_ranges)):
                with open(os.path.join(self._out_dir.name, f'mem{i}.bin'), 'rb') as f:
                    dump_data.append(f.read())

        return dump_data, os.path.join(self._out_dir.name, 'trace.bin')

    def cleanup(self):
        if self._out_dir:
            self._out_dir.cleanup()

        super().cleanup()

class OCDSession:
    def __init__(self, manager, probe_id: str, target: str='stm32f407vg', options: dict=None, idle_time: float=20):
        self._manager = manager

        probe = DebugProbeAggregator.get_probe_with_id(probe_id)
        if not probe:
            raise KeyError(f'Failed to find probe {probe_id}')

        self._session = PyOCDSession(probe, auto_open=False, target_override=target, options=options)

        self._idle_time = idle_time
        self._idle_event = None

        self.lock = threading.Lock()

    @property
    def id(self):
        return self._session.probe.unique_id

    def __eq__(self, other):
        return other.id == self.id

    def __hash__(self):
        return hash(self.id)

    def _open(self):
        with self.lock:
            if not self._session.is_open:
                try:
                    self._session.open(init_board=True)
                except USBError as ex:
                    if ex.errno == errno.EBUSY:
                        return False
                    raise

        return True

    def _close(self, cancel_idle=True):
        with self.lock:
            if self._idle_event:
                if cancel_idle:
                    self._manager._scheduler.cancel(self._idle_event)

                self._idle_event = None

            if not self._session.is_open:
                return

            self._manager.logger.info(f'Closing probe {self.id}')
            self._session.close()

    def __idle_close(self):
        self._manager.logger.info(f'Probe {self.id} has become idle')
        self._close(cancel_idle=False)

    def __enter__(self):
        with self.lock:
            if self._idle_event:
                self._manager._scheduler.cancel(self._idle_event)

        self._session.target.reset_and_halt(reset_type=PyOCDTarget.ResetType.HW)
        self._manager._active.add(self)

        return self._session

    def __exit__(self, type_, value, tb):
        with self.lock:
            self._idle_event = self._manager._scheduler.enter(self._idle_time, 10, self.__idle_close)

        self._manager._active.remove(self)
        self._manager._all.put(self)

class OCDSessionManager:
    def __init__(self, logger):
        self.logger = logger

        # Scheduler will repeatedly call the delayfunc, we need a short sleep so
        # the scheduler will detect an updated event queue
        self._scheduler = sched.scheduler(delayfunc=util.capped_sleep(0.2))

        self._shutdown_event = self._scheduler.enterabs(threading.TIMEOUT_MAX, 100, lambda: None)

        self._sched_thread = threading.Thread(target=self._scheduler.run, name='PyOCD session pool manager')
        self._sched_thread.start()

        self._ids = set()
        self._all = queue.Queue()
        self._active = set()

        self.lock = threading.Lock()

    def __contains__(self, id_):
        return id_ in self._ids

    def add(self, probe_id: str, target: str='stm32f407vg', options: dict=None, idle_time: float=10):
        with self.lock:
            if probe_id in self:
                return

            s = OCDSession(self, probe_id, target=target, options=options, idle_time=idle_time)
            self._all.put(s)
            self._ids.add(probe_id)

    def get(self, interval: float=0.2):
        while True:
            s = self._all.get()
            if not s._open():
                time.sleep(interval)
                self._all.put(s)
                continue

            return s

    def cleanup(self):
        with self.lock:
            if not self._sched_thread:
                return

            t = self._sched_thread
            self._sched_thread = None

            while not self._all.empty():
                self._all.get_nowait()._close()
            for s in self._active:
                s._close()

            self._scheduler.cancel(self._shutdown_event)
            t.join()


class PyOCD(Evaluator):
    _dap_probe_ignore_err_regex = re.compile(r'^Exception (while probing AP|reading AP)')
    _stlink_detect_ignore_err_regex = re.compile(r'^Could not get .+ devices by id')
    _overridable_sesson_options = {
        'connect_mode': 'under-reset',
        'hide_programming_progress': True,
    }

    _global_lock = threading.Lock()
    _manager = None
    _trace_file = None

    @classmethod
    def _filter_dap_discovery(cls, record: logging.LogRecord):
        # DAP discovery spews exceptions that don't prevent debugging from working
        if cls._dap_probe_ignore_err_regex.match(record.getMessage()):
            return False
        return True
    @classmethod
    def _filter_stlink_detect(cls, record: logging.LogRecord):
        # In a Docker container /dev/*/by-id won't exist
        if cls._stlink_detect_ignore_err_regex.match(record.getMessage()):
            return False
        return True

    @staticmethod
    def await_halt(session: PyOCDSession, interval: float=0.1, timeout: int=None):
        start = time.monotonic()
        while session.target.get_state() != PyOCDTarget.State.HALTED:
            time.sleep(interval)

            if timeout and time.monotonic() - start >= timeout:
                raise TimeoutError('Timed out waiting for CPU halt')

    def __init__(self, *args, probes: Iterable=None, target: str='stm32f407vg', start_addr: int=0, done_addr: int=None,
            extra_options: dict=None, cycles_addr: int=0xe0001004, gem5: str=None, **kwargs):
        super().__init__(*args, **kwargs)

        with self._global_lock:
            if not self._manager:
                # Take this opportunity to filter out Debug Access Port probing errors
                PyOCDDiscoveryLogger.addFilter(self._filter_dap_discovery)
                PyOCDSTLINKDetectLogger.addFilter(self._filter_stlink_detect)

                PyOCD._manager = OCDSessionManager(self.logger)

        self.start_addr = start_addr
        self.done_addr = done_addr
        if self.done_addr is None:
            raise KeyError('done_addr is required')

        self.cycles_addr = cycles_addr
        self._gem5 = gem5

        if probes:
            if not extra_options:
                extra_options = {}
            options = copy.deepcopy(self._overridable_sesson_options)
            options.update(extra_options)

            for p in probes:
                try:
                    self._manager.add(p, target=target, options=options)
                except KeyError as ex:
                    self.logger.warn(str(ex))

    def run(self):
        if len(self._manager._ids) == 0:
            self.logger.warn('No probes configured, probably going to be stuck forever')

        cycles = 0
        with self._manager.get() as session:
            target = session.target

            self.logger.info(f'Flashing {self.firmware} to board on probe {session.probe.unique_id}')
            PyOCDProgrammer(session).program(self.firmware)
            target.reset_and_halt()
            self.logger.info('Firmware loaded')

            if self.test_data:
                if self.test_data is not None:
                    if self.debug:
                        self.logger.info(f'Waiting for test data breakpoint {self.test_data.when:#010x}')
                    target.set_breakpoint(self.test_data.when)
                    target.resume()

                    self.await_halt(session, timeout=self.timeout)
                    assert target.read_core_register('pc') == self.test_data.when
                    target.remove_breakpoint(self.test_data.when)

                target.write_memory_block8(self.test_data.addr, self.test_data.data)

            if self.debug:
                self.logger.info(f'Waiting for test completion breakpoint {self.done_addr:#010x}')
            target.set_breakpoint(self.done_addr)
            target.resume()

            self.await_halt(session, timeout=self.timeout)
            assert target.read_core_register('pc') == self.done_addr
            target.remove_breakpoint(self.done_addr)

            if self.cycles_addr:
                cycles = target.read32(self.cycles_addr)

            dump_data = []
            if self.dump_ranges:
                for r in self.dump_ranges:
                    dump_data.append(bytes(target.read_memory_block8(r.start, r.size)))

            if self.debug:
                self.logger.info('Hardware evaluation done!')

        trace_filename = None
        if self._gem5:
            self._trace_file = tempfile.NamedTemporaryFile(mode='wb', suffix='.faketraces.bin')

            tracing.generate_dummy_cycles(self._trace_file, self._gem5, start=self.start_addr, stop=self.done_addr, cycles=cycles)
            self._trace_file.flush()

            trace_filename = self._trace_file.name

        return dump_data, trace_filename

    def cleanup(self):
        if self._trace_file:
            self._trace_file.close()

        if self._manager:
            self._manager.cleanup()

        super().cleanup()

class Evaluate(Step):
    description = 'Run evaluation'
    evaluators = {
        'simulation': Simulator,
        'hardware': PyOCD,
    }

    _eval = None

    def run(self, ctx: Mapping):
        s_cls = self.evaluators[self.input['type']]
        del self.input['type']

        fw = self.input['firmware']
        del self.input['firmware']
        self._eval = s_cls(fw, self.logger, **self.input)

        dump, traces = self._eval.run()
        self.output = Box(dump=dump, traces=traces)

    def close(self):
        if self._eval:
            self._eval.cleanup()
