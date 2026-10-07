"""Command-line entry point for mini-Scheme."""

import sys
from pathlib import Path

from evaluator import evaluate, initial_environment
from printer import format_value
from reader import parse


def run(source, environment):
    for expression in parse(source):
        value = evaluate(expression, environment)
        if value is not None:
            sys.stdout.write(format_value(value) + "\n")


def main(arguments):
    environment = initial_environment()
    if arguments:
        for filename in arguments:
            run(Path(filename).read_text(encoding="utf-8"), environment)
    else:
        run(sys.stdin.read(), environment)


if __name__ == "__main__":
    main(sys.argv[1:])
