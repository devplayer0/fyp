import argparse
import sys
import os
import os.path

import yaml

from . import pipeline

def main():
    parser = argparse.ArgumentParser(description='Perfgrade')
    parser.add_argument('pipeline', help='Path to pipeline file')
    args = parser.parse_args()

    with open(args.pipeline) as f:
        pipeline_input = yaml.safe_load(f)

    pipeline_dir = os.path.dirname(args.pipeline)
    if pipeline_dir:
        os.chdir(pipeline_dir)

    with pipeline.Pipeline('root', pipeline_input) as p:
        p.run({})

if __name__ == '__main__':
    sys.exit(main())
