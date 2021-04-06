import abc
from collections.abc import Mapping
import struct
import sys
import os
import os.path

from box import Box
import numpy as np
import matplotlib.pyplot as plt

from . import util

class Step(abc.ABC):
    GLOBALS = {
        'sys': sys,
        'os': os,
        'path': os.path,

        'Box': Box,
        'struct': struct,
        'np': np,
        'plt': plt,
    }

    description = None
    input_no_eval = set()

    def __init__(self, id_: str, input_, description=None, logger=None):
        self.id = id_
        self.input = input_
        if description:
            self.description = description
        if logger:
            self.logger = logger
        else:
            self.logger = util.Logger()

        self.ctx = {'self': self}
        self.output = None

    def _eval_input_recurse(self, ctx, v, path='input'):
        if path in self.input_no_eval:
            return v

        if isinstance(v, util.Expression):
            expr = v.compile(f'<Step {self.id} {path}>')
            v = eval(expr, self.GLOBALS, ctx)

        if isinstance(v, Step):
            v = v.output

        if isinstance(v, list):
            for i, v2 in enumerate(v):
                npath = f'{path}[{i}]'
                v[i] = self._eval_input_recurse(ctx, v2, npath)
        elif isinstance(v, Mapping):
            for k, v2 in v.items():
                npath = f'{path}.{k}'
                v[k] = self._eval_input_recurse(ctx, v2, npath)

        return v

    def _eval_input(self, ctx: dict):
        ctx = {**self.ctx, **ctx}
        self.input = self._eval_input_recurse(ctx, self.input)

        if isinstance(self.description, util.Expression):
            self.description = eval(self.description.compile('<Step {self.id} description>'), self.GLOBALS, ctx)

        return ctx

    @abc.abstractmethod
    def run(self, ctx: Mapping):
        pass

    def close(self):
        pass

    def __str__(self):
        if self.description:
            return f'{self.description} ({self.id})'

        return self.id

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        self.logger.info('🧹 Cleaning up')
        self.close()
