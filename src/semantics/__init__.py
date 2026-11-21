"""Exact, simply typed terms for seed-1.0. Bound references count every lambda."""
from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
import re
from types import MappingProxyType

ROOT = Path(__file__).resolve().parents[2]
NORMALIZER_VERSION = "seed-1.0"
E, V, P, I = "E", "V", "P", "I"


def arrow(domain, result):
    return ("->", domain, result)


R = arrow(E, P)
Q = arrow(R, P)
K = arrow(V, P)
H = arrow(K, P)


def parse_type(text):
    """Read base sorts and right-associative arrows from the ontology."""
    tokens = re.findall(r"->|[A-Za-z]+|[^\s]", text)
    pos = 0

    def read():
        nonlocal pos
        if pos == len(tokens):
            raise ValueError(f"incomplete type {text!r}")
        token = tokens[pos]
        pos += 1
        if token == "(":
            result = read()
            if tokens[pos:pos + 1] != [")"]:
                raise ValueError(f"missing ')' in {text!r}")
            pos += 1
        elif token in (E, V, P, I):
            result = token
        else:
            raise ValueError(f"unknown sort {token!r}")
        if tokens[pos:pos + 1] == ["->"]:
            pos += 1
            result = arrow(result, read())
        return result

    result = read()
    if pos != len(tokens):
        raise ValueError(f"trailing type tokens in {text!r}")
    return result


@lru_cache(maxsize=1)
def signature():
    ontology = json.loads((ROOT / "spec/ontology.yaml").read_bytes())
    symbols = {name: parse_type(sort) for name, sort in ontology["names"].items()}
    for name, args in ontology["predicates"].items():
        result = P
        for arg in reversed(args):
            result = arrow(parse_type(arg), result)
        symbols[name] = result
    symbols.update({name: parse_type(sort) for name, sort in ontology["constructors"].items()})
    return MappingProxyType(symbols)


# The public spike uses the same immutable term constructors. Applications
# are curried internally and printed as a single left-associated spine.
def var(index):
    return ("var", index)


def const(name):
    return ("const", name)


def lam(sort, body):
    return ("lam", sort, body)


def app(function, *arguments):
    for argument in arguments:
        function = ("app", function, argument)
    return function


def call(symbol, *arguments):
    return app(const(symbol), *arguments)


def valid_sort(sort):
    return sort in (E, V, P, I) or (
        isinstance(sort, tuple) and len(sort) == 3 and sort[0] == "->"
        and valid_sort(sort[1]) and valid_sort(sort[2])
    )


class SemanticError(ValueError):
    """A malformed, open, or ill-typed term."""


def typeof(term, context=()):
    """Type a term with nearest enclosing sort first, rejecting negative indices."""
    def infer(node, env):
        if isinstance(node, tuple):
            match node:
                case ("var", index):
                    if type(index) is not int or not 0 <= index < len(env):
                        raise SemanticError(f"unbound de Bruijn index {index!r} at depth {len(env)}")
                    return env[index]
                case ("const", str(name)):
                    if name not in signature():
                        raise SemanticError(f"unknown symbol {name!r}")
                    return signature()[name]
                case ("lam", sort, body):
                    if not valid_sort(sort):
                        raise SemanticError(f"invalid binder sort {sort!r}")
                    return arrow(sort, infer(body, (sort,) + env))
                case ("app", function, argument):
                    f, a = infer(function, env), infer(argument, env)
                    if not isinstance(f, tuple) or f[1] != a:
                        raise SemanticError(f"cannot apply {f!r} to {a!r}")
                    return f[2]
        raise SemanticError(f"invalid term {node!r}")

    if not all(valid_sort(sort) for sort in context):
        raise SemanticError("invalid sort in binding context")
    return infer(term, tuple(context))


def shift(term, distance, cutoff=0):
    match term:
        case ("var", index) if index >= cutoff:
            return var(index + distance)
        case ("lam", sort, body):
            return lam(sort, shift(body, distance, cutoff + 1))
        case ("app", fn, arg):
            return app(shift(fn, distance, cutoff), shift(arg, distance, cutoff))
    return term


def _instantiate(term, argument, depth=0):
    """Remove one binder, lifting its replacement over intervening lambdas."""
    match term:
        case ("var", index) if index == depth:
            return shift(argument, depth)
        case ("var", index) if index > depth:
            return var(index - 1)
        case ("lam", sort, body):
            return lam(sort, _instantiate(body, argument, depth + 1))
        case ("app", fn, arg):
            return app(_instantiate(fn, argument, depth), _instantiate(arg, argument, depth))
    return term


def spine(term):
    args = []
    while term[0] == "app":
        args.append(term[2])
        term = term[1]
    return term, tuple(reversed(args))


def type_text(sort):
    if isinstance(sort, str):
        return sort
    return f"({type_text(sort[1])}->{type_text(sort[2])})"


def canonical(term):
    """Serialize a checked term. Comparison uses the normalized result."""
    match term:
        case ("const", name):
            return name
        case ("var", index):
            return f"#{index}"
        case ("lam", sort, body):
            return f"(lam {type_text(sort)} {canonical(body)})"
    head, args = spine(term)
    return "(" + " ".join(map(canonical, (head, *args))) + ")"


@dataclass(frozen=True)
class Rewrite:
    rule: str
    path: tuple
    before: tuple
    after: tuple


@dataclass(frozen=True)
class Normalization:
    raw: tuple
    normal: tuple
    trace: tuple
    version: str = NORMALIZER_VERSION


def normalize(term, context=()):
    """Type-check before any reduction. Record local replacements in replay order."""
    original_type = typeof(term, context)
    trace = []

    def beta(node, path):
        match node:
            case ("lam", sort, body):
                return lam(sort, beta(body, path + (2,)))
            case ("app", fn, arg):
                fn = beta(fn, path + (1,))
                arg = beta(arg, path + (2,))
                if fn[0] == "lam":
                    result = _instantiate(fn[2], arg)
                    trace.append(Rewrite("beta", path, app(fn, arg), result))
                    return beta(result, path)
                return app(fn, arg)
        return node

    def operands(node):
        head, args = spine(node)
        if head == const("And") and len(args) == 2:
            yield from operands(args[0])
            yield from operands(args[1])
        elif node != const("Top"):
            yield node

    def conjunctions(node, path):
        match node:
            case ("lam", sort, body):
                return lam(sort, conjunctions(body, path + (2,)))
            case ("app", fn, arg):
                node = app(conjunctions(fn, path + (1,)), conjunctions(arg, path + (2,)))
                head, args = spine(node)
                if head == const("And") and len(args) == 2:
                    parts = sorted(operands(node), key=canonical)
                    result = parts.pop() if parts else const("Top")
                    for part in reversed(parts):
                        result = call("And", part, result)
                    if result != node:
                        trace.append(Rewrite("conjunction", path, node, result))
                    return result
        return node

    normal = conjunctions(beta(term, ()), ())
    if typeof(normal, context) != original_type:
        raise AssertionError("normalization changed the semantic type")
    return Normalization(term, normal, tuple(trace))


def close(clause):
    if typeof(clause) != H:
        raise SemanticError("root closure expects a closed event-continuation clause")
    return normalize(app(clause, lam(V, const("Top"))))


def reading_text(normal):
    """Check the base-sort, saturated surface form of a normalized proposition."""
    if typeof(normal) != P:
        raise SemanticError("a reading must be a closed proposition")

    def check_form(node):
        head, args = spine(node)
        if head[0] == "var" and not args:
            return
        if head[0] != "const":
            raise SemanticError("unexpected logical head in a closed reading")
        name = head[1]
        ty = signature()[name]
        for arg in args:
            if not isinstance(ty, tuple):
                raise SemanticError(f"oversaturated symbol {name}")
            domain, ty = ty[1:]
            if isinstance(domain, tuple):
                if arg[0] != "lam" or arg[1] not in (E, V):
                    raise SemanticError(f"{name} requires an explicit logical binder")
                check_form(arg[2])
            else:
                check_form(arg)
        if isinstance(ty, tuple):
            raise SemanticError(f"unsaturated symbol {name}")

    check_form(normal)
    return canonical(normal)


def reading_set(terms):
    """Canonical compact JSON bytes for a collection of closed propositions."""
    readings = set()
    for term in terms:
        if typeof(term) != P:
            raise SemanticError("a reading must be a closed proposition")
        readings.add(reading_text(normalize(term).normal))
    return json.dumps(sorted(readings), ensure_ascii=True, separators=(",", ":")).encode("ascii")
