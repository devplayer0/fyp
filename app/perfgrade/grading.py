from collections.abc import Mapping
import difflib

from box import Box
import numpy as np
import matplotlib.pyplot as plt

from .step import Step

class BucketGrade(Step):
    description = 'Grade a cycle count by buckets with different functions'

    def run(self, ctx: Mapping):
        input_ = Box(self.input)

        fig, ax = plt.subplots()
        ax.set_title(input_.get('title', 'Grade curve'))
        ax.set_ylabel('Grade')
        if input_.get('xlabel'):
            ax.set_xlabel(input_.xlabel)

        for i, bucket in enumerate(input_.buckets):
            if i == 0:
                prev_max = bucket.max
                max_grade = 1
            else:
                max_grade = bucket.max_grade
                prev_max = input_.buckets[i-1].max

            if i == len(input_.buckets) - 1:
                next_max_grade = 0
            else:
                next_max_grade = input_.buckets[i+1].max_grade

            # f should map 0-1 -> 0-1
            f = bucket.get('f', lambda x: x)
            # f_bucket maps 0-1 -> grade in the bucket
            f_bucket = lambda x: f(x) * (max_grade - next_max_grade) + next_max_grade

            global_space = np.linspace(prev_max, bucket.max, num=64)
            bucket_space = np.linspace(1, 0, num=64)
            ax.plot(global_space, f_bucket(bucket_space), color='m')

            ax.plot([bucket.max]*2, [0, 1], label=bucket.get('label'))

            if self.output is None:
                x = input_.value
                grade = None
                if x < bucket.max:
                    if i == 0:
                        grade = 1.0
                    else:
                        # x_bucket is input absolute value mapped to 0-1 between the bucket max/min
                        x_bucket = 1 - ((x - prev_max) / (bucket.max - prev_max))
                        grade = f_bucket(x_bucket)
                elif i == len(input_.buckets) - 1:
                    grade = 0.0

                if grade is not None:
                    ax.scatter(x, grade, color='r', label='Your grade')
                    ax.annotate(f'{grade:.2}', (x, grade), xytext=(4, 4), textcoords='offset points')

                    self.output = grade

        ax.legend()
        if input_.get('graph_file'):
            fig.savefig(input_.graph_file)

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
