import time
import sys

import yaml

def capped_sleep(cap: float=0):
    def sleep(secs: float):
        if cap != 0 and cap < secs:
            secs = cap
        time.sleep(secs)
    return sleep

class Expression(yaml.YAMLObject):
    yaml_tag = '!expr'

    def __init__(self, value: str):
        self._value = value

    def compile(self, loc: str):
        return compile(self._value, loc, 'eval')

    @classmethod
    def from_yaml(cls, loader: yaml.Loader, node: yaml.Node):
        return cls(node.value)

    @classmethod
    def to_yaml(cls, dumper: yaml.Dumper, data):
        return dumper.represent_scalar(cls.yaml_tag, data._value)

yaml.SafeLoader.add_constructor('!expr', Expression.from_yaml)
yaml.SafeDumper.add_multi_representer(Expression, Expression.to_yaml)

class Logger:
    def __init__(self, out=sys.stderr, prefix=''):
        self.out = out
        self.prefix = prefix

    def child(self, prefix):
        return Logger(out=self.out, prefix=f'{self.prefix}{prefix}')

    def info(self, msg):
        print(f'{self.prefix}{msg}', file=self.out)

    def warn(self, msg):
        print(f'{self.prefix}{msg}', file=self.out)
