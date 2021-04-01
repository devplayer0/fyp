from collections.abc import Mapping
import string
import html
import os

from box import Box

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

    row_template = string.Template('''    <tr>
        <td>$i</td>
        <td><code>$line</code></td>
        <td>$count</td>
        <td>$cycles</td>
    </tr>
''')
    html_template = string.Template('''<!DOCTYPE html>
<html>
<head>
    <title>Heatmap</title>
    <style>
        body {
            width: 75em;
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
        with open(os.path.join(self.input.get('basedir', ''), self.input['source'])) as f:
            for line in f:
                infos.append(Box(line=line.rstrip(), count=0, cycles=0))

        last_info = None
        prev_cycle = None
        for t in self.input['traces']:
            # If last iteration we were looking at an in-scope line, figure out
            # how many cycles it's been
            if last_info:
                last_info.cycles += t.orig.cycle - prev_cycle
                last_info = None
            prev_cycle = t.orig.cycle

            if t.filename != self.input['source'] or t.line is None:
                continue

            info = infos[t.line-1]
            info.count += 1
            last_info = info

        rows = []
        for i, info in enumerate(infos):
            rows.append(self.row_template.substitute(i=i, line=html.escape(info.line), count=info.count, cycles=info.cycles))

        self.output = self.html_template.substitute(source_file=self.input['source'], rows='\n'.join(rows))
        if self.input.get('html_out'):
            with open(self.input['html_out'], 'w') as f:
                f.write(self.output)
