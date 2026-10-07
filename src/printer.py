"""Convert Scheme values to the specified external representation."""

from values import NIL, Pair, SchemeString, Symbol


def format_value(value, display=False):
    if value is NIL:
        return "()"
    if value is True:
        return "#t"
    if value is False:
        return "#f"
    if isinstance(value, Pair):
        parts = []
        while isinstance(value, Pair):
            parts.append(format_value(value.first))
            value = value.rest
        if value is NIL:
            return "(" + " ".join(parts) + ")"
        return "(" + " ".join(parts) + " . " + format_value(value) + ")"
    if isinstance(value, SchemeString):
        if display:
            return str(value)
        escaped = (str(value).replace("\\", "\\\\").replace('"', '\\"')
                   .replace("\n", "\\n").replace("\t", "\\t"))
        return '"' + escaped + '"'
    if isinstance(value, Symbol):
        return str(value)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    return "#<procedure>"
