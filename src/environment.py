"""Lexically nested variable bindings."""


class Environment:
    def __init__(self, parent=None, bindings=None):
        self.parent = parent
        self.bindings = {} if bindings is None else dict(bindings)

    def define(self, name, value):
        self.bindings[name] = value

    def lookup(self, name):
        if name in self.bindings:
            return self.bindings[name]
        if self.parent is not None:
            return self.parent.lookup(name)
        raise NameError(f"unknown symbol: {name}")
