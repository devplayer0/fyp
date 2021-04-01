from collections.abc import Mapping
import os.path
import tempfile
import threading
import subprocess
import shutil
import pkg_resources

from box import Box
from elftools.elf.elffile import ELFFile

from .step import Step

class Build(Step):
    description = 'Build a Perfgrade firmware'

    _build_dir = None

    @classmethod
    def _get_build_dir(cls):
        makefile_path = pkg_resources.resource_filename(__name__, 'build/Makefile')
        template_path = os.path.normpath(os.path.join(makefile_path, '..'))

        build_dir = tempfile.TemporaryDirectory(suffix='.perfgrade')
        shutil.copytree(template_path, build_dir.name, dirs_exist_ok=True)
        return build_dir

    def run(self, ctx: Mapping):
        input_ = Box(self.input)
        self._build_dir = self._get_build_dir()
        build_dir = self._build_dir.name

        sources = Box(c=['src/main.c'], a=['src/util.S', 'src/uut.S'])
        if 'harness' in input_:
            if input_.harness.endswith('.c'):
                shutil.copy(input_.harness, os.path.join(build_dir, 'src/harness.c'))
                sources.c.append('src/harness.c')
            elif input_.harness.endswith(('.s', '.S')):
                shutil.copy(input_.harness, os.path.join(build_dir, 'src/harness.S'))
                sources.a.append('src/harness.S')
            else:
                raise ValueError(f'Invalid harness file {input_.harness} (must be `.c` or `.s`)')

        uut_file = 'src/uut.S'
        shutil.copy(input_.uut, os.path.join(build_dir, uut_file))

        self.output = Box(dir=build_dir, uut=uut_file, elf=os.path.join(build_dir, 'perfgrade.elf'))
        target = 'perfgrade.elf'
        if input_.get('rom', True):
            target = 'perfgrade.bin'
            self.output.rom = os.path.join(build_dir, 'perfgrade.bin')

        defines = []
        for n, v in input_.get('defines', {}).items():
            defines.append(f'-D{n}={v}')

        args = ['make', f'OPENCM3_DIR={os.path.abspath(input_.get("opencm3", "libopencm3"))}']
        args += [f'CFILES={" ".join(sources.c)}', f'AFILES={" ".join(sources.a)}']
        args += [f'CFLAGS={" ".join(defines)}', f'ASFLAGS={" ".join(defines)}']
        if input_.get('debug'):
            args.append('V=1')
        args.append(target)
        subprocess.check_call(args, cwd=build_dir)

    def close(self):
        if self._build_dir:
            self._build_dir.cleanup()

def align(n, a=0):
    if a == 0:
        return n
    return n & ~((1 << (a >> 1))-1)

class SymbolResolver:
    def __init__(self, elf: ELFFile, logger):
        self.elf = elf
        self.logger = logger

        self.lock = threading.Lock()
        self.symtab = self.elf.get_section_by_name('.symtab')
        if not self.symtab:
            raise KeyError('No symbol table in ELF')

        self._cache = {}

    def resolve_symbol(self, symbol: str, a=1):
        with self.lock:
            if not symbol:
                raise KeyError('Invalid symbol name')
            if isinstance(symbol, int):
                return symbol
            if symbol in self._cache:
                return self._cache[symbol]

            symbols = self.symtab.get_symbol_by_name(symbol)
            if not symbols:
                raise KeyError(f'No symbol "{symbol}"')

            sym = symbols[0]
            addr = align(sym.entry.st_value, a=a)
            self.logger.info(f'Resolving "{sym.name}" to {addr:#010x}')

            self._cache[symbol] = addr

            return addr

    def __getitem__(self, key):
        if isinstance(key, tuple):
            return self.resolve_symbol(key[0], a=key[1])
        return self.resolve_symbol(key)

class Symtab(Step):
    description = 'Load ELF symbol table'

    elf = None

    def run(self, ctx: Mapping):
        self.elf = ELFFile(open(self.input, 'rb'))
        self.output = SymbolResolver(self.elf, self.logger)

    def close(self):
        if self.elf:
            self.elf.stream.close()
