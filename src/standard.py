"""The mini-Scheme standard procedures from spec section 5."""

import math
import operator
import sys
from functools import reduce

from printer import format_value
from values import NIL, Pair, SchemeString, Symbol, is_proper_list, list_items, make_list


def truthy(value):
    return value is not False


def number(value):
    return type(value) in (int, float)


def trunc_quotient(left, right):
    quotient = abs(left) // abs(right)
    return quotient if (left < 0) == (right < 0) else -quotient


def subtract(*values):
    if len(values) == 1:
        return -values[0]
    return reduce(operator.sub, values[1:], values[0])


def divide(*values):
    if len(values) == 1:
        return 1.0 / values[0]
    result = values[0]
    for divisor in values[1:]:
        result = (trunc_quotient(result, divisor)
                  if type(result) is int and type(divisor) is int
                  else result / divisor)
    return result


def chained(comparison, *values):
    return all(comparison(left, right) for left, right in zip(values, values[1:]))


def scheme_eq(left, right):
    if left is NIL or right is NIL:
        return left is right
    if number(left) and number(right):
        return left == right
    if type(left) is Symbol and type(right) is Symbol:
        return left == right
    if type(left) is bool and type(right) is bool:
        return left == right
    return left is right


def scheme_equal(left, right):
    """Compare Scheme values without using Python recursion for pairs."""
    pending = [(left, right)]
    while pending:
        left, right = pending.pop()
        if isinstance(left, Pair) or isinstance(right, Pair):
            if not (isinstance(left, Pair) and isinstance(right, Pair)):
                return False
            pending.append((left.rest, right.rest))
            pending.append((left.first, right.first))
            continue
        if number(left) and number(right):
            equal = left == right
        elif type(left) is not type(right):
            equal = False
        elif left is NIL or right is NIL:
            equal = left is right
        elif type(left) in (bool, Symbol, SchemeString):
            equal = left == right
        else:
            equal = left is right
        if not equal:
            return False
    return True


def append(*lists):
    return make_list([item for value in lists for item in list_items(value)])


def display(value):
    sys.stdout.write(format_value(value, display=True))


def newline():
    sys.stdout.write("\n")


def procedures():
    """Return a fresh mapping of standard procedure names to callables."""
    return {
        "+": lambda *values: sum(values),
        "-": subtract,
        "*": lambda *values: math.prod(values),
        "/": divide,
        "modulo": operator.mod,
        "quotient": trunc_quotient,
        "expt": pow,
        "abs": abs,
        "=": lambda *values: chained(operator.eq, *values),
        "<": lambda *values: chained(operator.lt, *values),
        ">": lambda *values: chained(operator.gt, *values),
        "<=": lambda *values: chained(operator.le, *values),
        ">=": lambda *values: chained(operator.ge, *values),
        "not": lambda value: not truthy(value),
        "cons": Pair,
        "car": lambda value: value.first,
        "cdr": lambda value: value.rest,
        "list": lambda *values: make_list(values),
        "length": lambda value: len(list_items(value)),
        "append": append,
        "null?": lambda value: value is NIL,
        "pair?": lambda value: isinstance(value, Pair),
        "list?": is_proper_list,
        "number?": number,
        "boolean?": lambda value: type(value) is bool,
        "symbol?": lambda value: type(value) is Symbol,
        "string?": lambda value: type(value) is SchemeString,
        "procedure?": callable,
        "zero?": lambda value: value == 0,
        "even?": lambda value: value % 2 == 0,
        "odd?": lambda value: value % 2 != 0,
        "eq?": scheme_eq,
        "equal?": scheme_equal,
        "display": display,
        "newline": newline,
    }
