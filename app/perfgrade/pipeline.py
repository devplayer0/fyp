from collections.abc import Mapping
import copy
import concurrent.futures
import os.path
import shutil

from box import Box
import yaml

from . import util
from .step import Step
from .build import Build, Symtab
from .evaluate import Evaluate
from .tracing import Traces, AugmentTraces
from .statistics import CycleCount, Heatmap, CurveGuess
from .grading import BucketGrade, Diff

class Exec(Step):
    description = 'Arbitrary Python execution'

    def run(self, ctx: Mapping):
        code = compile(self.input, f'<Exec {self.id}>', 'exec')
        exec(code, self.GLOBALS, ctx)

class Passthrough(Step):
    description = 'Pass evaluated input through to output'

    def run(self, ctx: Mapping):
        self.output = self.input

class Copy(Step):
    description = 'Copy files'

    def run(self, ctx: Mapping):
        input_ = self.input
        if not isinstance(self.input, list):
            input_ = [self.input]

        for i in input_:
            if os.path.isdir(i['src']):
                shutil.copytree(i['src'], i['dst'])
            else:
                shutil.copy(i['src'], i['dst'])

class Pipeline(Step):
    description = 'Step pipeline'
    input_no_eval = {'input.steps'}

    @classmethod
    def make_step(cls, i: int, s: Box, logger: util.Logger):
        id_ = s.get('id')
        if not id_:
            id_ = f's{i}'

        s_cls = STEPS[s.type]
        return s_cls(id_, s.input, description=s.get('description'), logger=logger)

    def run(self, ctx: Mapping):
        self.input = Box(self.input)
        self.steps = []
        for i, s in enumerate(self.input.steps):
            step = self.make_step(i, s, self.logger.child(f'⚗️ {i+1}/{len(self.input.steps)} '))
            self.steps.append(step)

        for i, step in enumerate(self.steps):
            ctx['self'] = step
            local_ctx = step._eval_input(ctx)
            step.run(local_ctx)
            self.logger.info(f'✔️ {i+1}/{len(self.steps)} {str(step)}')
            ctx[step.id] = step.output

        self.output = Box(ctx)

    def close(self):
        for s in self.steps:
            s.close()

class Mapped(Step):
    description = 'Map a step over a list and collect the outputs'
    input_no_eval = {'input.step'}

    steps = []

    def _do_step(self, i, ctx):
        step = self.steps[i]
        step.run(ctx)
        return i, step.output

    def run(self, ctx: Mapping):
        self.steps = []
        futures = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.input.get('parallel', 1)) as executor:
            for i, item in enumerate(self.input['items']):
                s = copy.deepcopy(self.input['step'])
                step = Pipeline.make_step(i, s, self.logger.child(f'🔁 {i+1}/{len(self.input["items"])} '))
                self.steps.append(step)

                i_ctx = step._eval_input({**ctx, 'self': step, 'i': i, 'item': item})
                futures.append(executor.submit(self._do_step, i, i_ctx))

            self.output = [None] * len(self.steps)
            for f in concurrent.futures.as_completed(futures):
                i, output = f.result()
                self.logger.info(f'✔️ {i+1} completed')
                self.output[i] = output

    def close(self):
        for s in self.steps:
            s.close()

class Include(Step):
    _step = None

    def run(self, ctx: Mapping):
        with open(self.input) as f:
            step_input = Box(yaml.safe_load(f))
        step_input.id = self.id

        self._step = Pipeline.make_step(-1, step_input, self.logger)
        s_ctx = self._step._eval_input({**ctx, 'self': self._step})

        self._step.run(s_ctx)
        self.output = self._step.output

    def __str__(self):
        return str(self._step)

STEPS = {
    'exec': Exec,
    'passthrough': Passthrough,
    'copy': Copy,

    'build': Build,
    'symtab': Symtab,

    'evaluate': Evaluate,

    'load_traces': Traces,
    'augment_traces': AugmentTraces,

    'cycle_count': CycleCount,
    'heatmap': Heatmap,
    'curve_guess': CurveGuess,

    'bucket_grade': BucketGrade,
    'diff': Diff,

    'pipeline': Pipeline,
    'mapped': Mapped,
    'include': Include,
}
