"""Evaluate expressions using special forms and lexical closures."""

from dataclasses import dataclass

from standard import procedures, truthy
from environment import Environment
from values import NIL, SchemeString, Symbol, make_list


@dataclass(eq=False)
class Closure:
    parameters: list
    body: list
    environment: Environment

    def __call__(self, *arguments):
        if len(arguments) != len(self.parameters):
            raise TypeError("wrong number of arguments")
        local = Environment(self.environment, zip(self.parameters, arguments))
        return evaluate_sequence(self.body, local)


def initial_environment():
    return Environment(bindings=procedures())


def quote(datum):
    if isinstance(datum, list):
        if len(datum) >= 3 and type(datum[-2]) is Symbol and datum[-2] == ".":
            return make_list([quote(item) for item in datum[:-2]], quote(datum[-1]))
        return make_list([quote(item) for item in datum])
    return datum


def evaluate_sequence(expressions, env):
    result = None
    for expression in expressions:
        result = evaluate(expression, env)
    return result


def evaluate(expression, env):
    if isinstance(expression, Symbol):
        return env.lookup(expression)
    if not isinstance(expression, list):
        return expression
    if not expression:
        raise SyntaxError("empty application")

    head, *rest = expression
    form = head if type(head) is Symbol else None
    if form == "quote":
        return quote(rest[0])
    if form == "if":
        return (evaluate(rest[1], env) if truthy(evaluate(rest[0], env))
                else evaluate(rest[2], env) if len(rest) > 2 else None)
    if form == "cond":
        for clause in rest:
            test = True if type(clause[0]) is Symbol and clause[0] == "else" else evaluate(clause[0], env)
            if truthy(test):
                return evaluate_sequence(clause[1:], env) if len(clause) > 1 else test
        return None
    if form == "and":
        result = True
        for item in rest:
            result = evaluate(item, env)
            if not truthy(result):
                return result
        return result
    if form == "or":
        for item in rest:
            result = evaluate(item, env)
            if truthy(result):
                return result
        return False
    if form == "define":
        target = rest[0]
        if isinstance(target, list):
            name = target[0]
            value = Closure(target[1:], rest[1:], env)
        else:
            name = target
            value = evaluate(rest[1], env)
        env.define(name, value)
        return name
    if form == "lambda":
        return Closure(rest[0], rest[1:], env)
    if form == "let":
        bindings = [(name, evaluate(value, env)) for name, value in rest[0]]
        return evaluate_sequence(rest[1:], Environment(env, bindings))
    if form == "begin":
        return evaluate_sequence(rest, env)

    procedure = evaluate(head, env)
    arguments = [evaluate(argument, env) for argument in rest]
    if not callable(procedure):
        raise TypeError("attempted to call a non-procedure")
    return procedure(*arguments)
