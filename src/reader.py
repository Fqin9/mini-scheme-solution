"""Tokenize source text and parse it into nested expression lists."""

from values import SchemeString, Symbol


_ESCAPES = {"n": "\n", "t": "\t", '"': '"', "\\": "\\"}


def tokenize(source):
    tokens = []
    i = 0
    while i < len(source):
        char = source[i]
        if char.isspace():
            i += 1
        elif char == ";":
            end = source.find("\n", i)
            i = len(source) if end < 0 else end + 1
        elif char in "()'":
            tokens.append(char)
            i += 1
        elif char == '"':
            i += 1
            chars = []
            while i < len(source) and source[i] != '"':
                if source[i] == "\\":
                    i += 1
                    if i == len(source) or source[i] not in _ESCAPES:
                        raise SyntaxError("invalid string escape")
                    chars.append(_ESCAPES[source[i]])
                else:
                    chars.append(source[i])
                i += 1
            if i == len(source):
                raise SyntaxError("unterminated string")
            tokens.append(SchemeString("".join(chars)))
            i += 1
        else:
            end = i
            while end < len(source) and not source[end].isspace() and source[end] not in "();'\"":
                end += 1
            tokens.append(Symbol(source[i:end]))
            i = end
    return tokens


def _atom(token):
    if isinstance(token, SchemeString):
        return token
    if token == "#t":
        return True
    if token == "#f":
        return False
    try:
        return int(token)
    except ValueError:
        return Symbol(token)


def parse(source):
    """Parse all top-level expressions from source."""
    tokens = tokenize(source)
    position = 0

    def expression():
        nonlocal position
        if position >= len(tokens):
            raise SyntaxError("unexpected end of input")
        token = tokens[position]
        position += 1
        if type(token) is str and token == "(":
            items = []
            while position < len(tokens) and not (type(tokens[position]) is str and tokens[position] == ")"):
                items.append(expression())
            if position == len(tokens):
                raise SyntaxError("missing closing parenthesis")
            position += 1
            return items
        if type(token) is str and token == "'":
            return [Symbol("quote"), expression()]
        if type(token) is str and token == ")":
            raise SyntaxError("unexpected closing parenthesis")
        return _atom(token)

    expressions = []
    while position < len(tokens):
        expressions.append(expression())
    return expressions
