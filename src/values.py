"""Runtime values shared by the reader, evaluator, and printer."""

from dataclasses import dataclass


class Symbol(str):
    """A Scheme name, distinct from a Scheme string."""


class SchemeString(str):
    """A Scheme string literal."""


class EmptyList:
    pass


NIL = EmptyList()


@dataclass(eq=False)
class Pair:
    first: object
    rest: object


def make_list(items, tail=NIL):
    """Build a pair chain, optionally ending in a non-list tail."""
    for item in reversed(items):
        tail = Pair(item, tail)
    return tail


def list_items(value):
    """Return members of a proper list or raise ValueError."""
    items = []
    while isinstance(value, Pair):
        items.append(value.first)
        value = value.rest
    if value is not NIL:
        raise ValueError("expected a proper list")
    return items


def is_proper_list(value):
    while isinstance(value, Pair):
        value = value.rest
    return value is NIL
