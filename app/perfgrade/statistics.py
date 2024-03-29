from collections.abc import Mapping
import math
import string
import html

from box import Box
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex as c_to_css

from .step import Step

class CycleCount(Step):
    description = 'Count ticks / cycles from evaluation traces'

    def run(self, ctx: Mapping):
        first_pc = self.input.get('first_pc')
        last_pc = self.input.get('last_pc')

        first_tick, first_cycle = 0, 0
        last_tick, last_cycle = 0, 0
        for i, trace in enumerate(self.input['traces']):
            if (first_pc is not None and trace.pc == first_pc) or i == 0:
                first_tick = trace.tick
                first_cycle = trace.cycle

            last_tick = trace.tick
            last_cycle = trace.cycle
            if last_pc is not None and trace.pc == last_pc:
                break

        self.output = Box(ticks=last_tick - first_tick, cycles=last_cycle - first_cycle)

class Heatmap(Step):
    description = 'Generate program heatmap'


    cmap = plt.get_cmap('Wistia')
    row_template = string.Template('''    <tr>
        <td>$i</td>
        <td><code>$line</code></td>
        <td>$count</td>
        <td style="background-color: $color;">$cycles</td>
    </tr>
''')
    html_template = string.Template('''<!DOCTYPE html>
<html>
<head>
    <title>Heatmap</title>
    <style>
        body {
            width: 110em;
            margin: 0 auto;
            font-family: Tahoma, Verdana, Arial, sans-serif;
        }
    </style>
</head>
<body>
    <h1>Heatmap for <code>$source_file</code></h1>
    <table>
        <tr>
            <th>Line</th>
            <th>Source</th>
            <th>Count</th>
            <th>Cycles</th>
        </tr>

        $rows
    </table>
</body>
</html>
''')

    def run(self, ctx: Mapping):
        infos = []
        with open(self.input['source']) as f:
            for line in f:
                infos.append(Box(line=line.rstrip(), count=0, cycles=0))

        prev_cycle = 0
        for t in self.input['traces']:
            if t.orig.HasField('upc'):
                continue

            cycles = t.orig.cycle - prev_cycle
            prev_cycle = t.orig.cycle
            if t.filename != self.input.get('compilation_unit', self.input['source']) or t.line is None:
                continue

            info = infos[t.line-1]
            info.count += 1
            info.cycles += cycles

        rows = []
        for i, info in enumerate(infos):
            color = 'inherit'
            if 'total_cycles' in self.input:
                color = c_to_css(self.cmap(info.cycles / self.input['total_cycles']))

            rows.append(self.row_template.substitute(i=i+1, line=html.escape(info.line), count=info.count, cycles=info.cycles, color=color))

        self.output = self.html_template.substitute(source_file=self.input['source'], rows='\n'.join(rows))
        if self.input.get('html_out'):
            with open(self.input['html_out'], 'w') as f:
                f.write(self.output)

class CurveGuess(Step):
    description = 'Find closest function to data'

    def run(self, ctx: Mapping):
        import scipy.optimize

        input_ = Box(self.input)
        xdata = np.array(input_.data.x)
        ydata = np.array(input_.data.y)
        self.output = Box(function=None, error=math.inf)
        for name, f in input_.functions.items():
            popt, pcov = scipy.optimize.curve_fit(f, xdata, ydata)
            perr = np.sqrt(np.diag(pcov))

            error = abs(perr[0] + perr[1])
            if error < self.output.error:
                self.output.function = name
                self.output.error = error
                self.output.params = popt
