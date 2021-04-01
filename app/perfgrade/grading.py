from collections.abc import Mapping
import math
import difflib

from box import Box
import numpy as np
#import matplotlib.pyplot as plt

from .step import Step

class CurveGuess(Step):
    description = 'Find closest function to data'

    def run(self, ctx: Mapping):
        import scipy.optimize

        input_ = Box(self.input)
        xdata = np.array(input_.data.x)
        ydata = np.array(input_.data.y)
        self.output = Box(function=None, error=math.inf)
        for name, f in input_.functions.items():
            _popt, pcov = scipy.optimize.curve_fit(f, xdata, ydata)
            perr = np.sqrt(np.diag(pcov))

            error = abs(perr[0] + perr[1])
            if error < self.output.error:
                self.output.function = name
                self.output.error = error

class BucketGrade(Step):
    description = 'Grade a cycle count by buckets with different functions'

    def run(self, ctx: Mapping):
        input_ = Box(self.input)
        for i, bucket in enumerate(input_.buckets):
            if input_.value < bucket.max:
                if i == 0:
                    prev_max = 0
                    max_grade = 1
                else:
                    max_grade = bucket.max_grade
                    prev_max = input_.buckets[i-1].max

                if i == len(input_.buckets) - 1:
                    next_max_grade = 0
                else:
                    next_max_grade = input_.buckets[i+1].max_grade

                x = 1 - ((input_.value - prev_max) / (bucket.max - prev_max))
                f = bucket.get('f', lambda x: x)
                self.output = f(x) * (max_grade - next_max_grade) + next_max_grade
                return

        self.output = 0

class DiffException(Exception):
    pass

class Diff(Step):
    description = 'Check for differences in output'

    def run(self, ctx: Mapping):
        f = lambda i: f'{i}\n'
        a = list(map(f, self.input['a']))
        b = list(map(f, self.input['b']))

        self.output = Box()
        self.output.diff_list = difflib.unified_diff(a, b, fromfile='expected', tofile='got')
        self.output.diff = ''.join(self.output.diff_list)
