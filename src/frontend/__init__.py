"""Check finite CCG declarations as data and instantiate their typed binary rules."""
from dataclasses import dataclass
from graphlib import CycleError, TopologicalSorter
import re
from types import MappingProxyType

from src.semantics import E, H, I, K, P, Q, R, V, app, arrow, const, lam, typeof, var

ATOMS = {"N": R, "NP": Q, "S[fin]": H, "S[bare]": H, "S[to]": H}
NP_KINDS = ("unit", "universal", "existential")
VP_CLASSES = ("simple,plain", "simple,quick", "control")
ATOMS.update({f"NP[{kind}]": Q for kind in NP_KINDS})
ATOMS.update({f"S[{form},{kind}]": H for form in ("fin", "bare") for kind in VP_CLASSES})
ATOMS.update({"S[fin,negative]": H, "S[fin,not-every]": H})
SORT_ALIASES = {"R": R, "Q": Q, "K": K, "H": H, "VP": arrow(Q, H)}
TOKEN = re.compile(r";[^\n]*|[()]|[^\s();]+")
IDENTIFIER = re.compile(r"[A-Za-z][A-Za-z0-9_.-]*")


class GrammarError(ValueError):
    """Declaration or application error with a source location."""


def forms(source, filename):
    """Read parenthesized declarations. Preserve the start of each declaration."""
    stack = []
    start = None
    for line_no, line in enumerate(source.splitlines(), 1):
        for match in TOKEN.finditer(line):
            token = match[0]
            if token.startswith(";"):
                break
            location = f"{filename}:{line_no}:{match.start() + 1}"
            if token == "(":
                if not stack:
                    start = location
                stack.append([])
            elif token == ")":
                if not stack:
                    raise GrammarError(f"{location}: unexpected ')'")
                node = tuple(stack.pop())
                if stack:
                    stack[-1].append(node)
                else:
                    yield start, node
            elif stack:
                stack[-1].append(token)
            else:
                raise GrammarError(f"{location}: expected a parenthesized declaration")
    if stack:
        raise GrammarError(f"{start}: unclosed declaration")


def sort(expr):
    if expr in SORT_ALIASES:
        return SORT_ALIASES[expr]
    if expr in (E, V, P, I):
        return expr
    match expr:
        case ("->", domain, result):
            return arrow(sort(domain), sort(result))
    raise ValueError(f"unknown semantic sort {expr!r}")


def template(expr, names=()):
    if isinstance(expr, str):
        if expr in names:
            return var(names.index(expr))
        if re.fullmatch(r"#(0|[1-9][0-9]*)", expr):
            return var(int(expr[1:]))
        return const(expr)
    match expr:
        case ("fn", str(name), ty, body) if IDENTIFIER.fullmatch(name):
            return lam(sort(ty), template(body, (name,) + names))
        case ("lam", ty, body):
            return lam(sort(ty), template(body, (None,) + names))
        case (head, arg, *rest):
            return app(template(head, names), template(arg, names), *(template(a, names) for a in rest))
    raise ValueError(f"invalid semantic template {expr!r}")


def category_type(cat, depth):
    if cat in ATOMS:
        return ATOMS[cat]
    match cat:
        case ("/" | "\\", result, argument):
            if depth < 1:
                raise ValueError(f"category depth exceeds bound at {cat!r}")
            return arrow(category_type(argument, depth - 1), category_type(result, depth - 1))
    raise ValueError(f"unknown or unbounded category {cat!r}")


def cost(expr):
    if not isinstance(expr, str) or not re.fullmatch(r"-?(0|[1-9][0-9]*)", expr):
        raise ValueError("expected integer cost")
    value = int(expr)
    if not -(2**63) <= value < 2**63:
        raise ValueError("integer cost overflow")
    return value


def lexical_state(assignments, fields):
    if not isinstance(assignments, tuple):
        raise ValueError("expected a list of field assignments")
    state = {}
    for assignment in assignments:
        match assignment:
            case (str(key), str(value)) if value in fields.get(key, ()):
                if key in state:
                    raise ValueError(f"duplicate field {key}")
                state[key] = value
            case _:
                raise ValueError(f"undeclared field or value in {assignment!r}")
    return state


def lexical_cost(expr, state, fields):
    match expr:
        case ("if", str(key), value, yes, no):
            if key not in state or value not in fields[key]:
                raise ValueError(f"undeclared score observation {key}={value}")
            yes, no = cost(yes), cost(no)
            return yes if state[key] == value else no
    return cost(expr)


@dataclass(frozen=True)
class Entry:
    surface: tuple
    category: object
    meaning: tuple
    fields: tuple
    cost: int
    location: str


@dataclass(frozen=True)
class Unary:
    source: object
    target: object
    builder: tuple
    cost: int
    location: str


@dataclass(frozen=True)
class Item:
    start: int
    end: int
    category: object
    meaning: tuple


def category_depth(cat):
    return 0 if isinstance(cat, str) else 1 + max(category_depth(cat[1]), category_depth(cat[2]))


def binary_category(kind, left, right, depth, counters=None):
    """Pure local rule used by the typed kernel and the seed packed chart."""
    direction = "/" if kind in ("FA", "FC") else "\\"
    fn, arg = (left, right) if direction == "/" else (right, left)
    if not isinstance(fn, tuple) or fn[0] != direction:
        return None
    result, expected = fn[1:]
    if kind in ("FC", "BC"):
        if not isinstance(arg, tuple) or arg[:2] != (direction, expected):
            return None
        result = (direction, result, arg[2])
        if category_depth(result) > depth:
            if counters is not None:
                counters["depth_rejections"] = counters.get("depth_rejections", 0) + 1
            return None
    elif expected != arg:
        return None
    return result


@dataclass(frozen=True)
class Grammar:
    depth: int
    fields: object
    entries: object
    binary: object
    unary: object
    unary_order: tuple

    def combine(self, rule_id, left, right, counters=None):
        """Return a checked result for contiguous children, or None if inapplicable."""
        kind, location = self.binary[rule_id]
        if not 0 <= left.start < left.end == right.start < right.end:
            return None
        fun, argument = (left, right) if kind in ("FA", "FC") else (right, left)
        result = binary_category(kind, left.category, right.category, self.depth, counters)
        if result is None:
            return None
        try:
            for child in (left, right):
                if typeof(child.meaning) != category_type(child.category, self.depth):
                    raise ValueError("child meaning disagrees with category")
            if kind in ("FC", "BC"):
                # Both input meanings were checked closed, so the fresh binder is hygienic.
                meaning = lam(category_type(argument.category[2], self.depth),
                              app(fun.meaning, app(argument.meaning, var(0))))
            else:
                meaning = app(fun.meaning, argument.meaning)
            if typeof(meaning) != category_type(result, self.depth):
                raise ValueError("result meaning disagrees with category")
        except ValueError as exc:
            raise GrammarError(f"{location} {rule_id}: {exc}") from exc
        return Item(left.start, right.end, result, meaning)


def check(source, filename="<grammar>", profile="seed"):
    if profile not in ("seed", "kernel"):
        raise ValueError("unknown grammar profile")
    depth = None
    fields, entries, binary, unary = {}, {}, {}, {}
    ids = set()
    dependencies = {}
    for location, form in forms(source, filename):
        name = ""
        try:
            if depth is None:
                match form:
                    case ("depth", str(value)) if re.fullmatch(r"[0-9]+", value):
                        depth = int(value)
                        continue
                raise ValueError("first declaration must set a finite category depth")
            if len(form) < 2 or not isinstance(form[1], str) or not IDENTIFIER.fullmatch(form[1]):
                raise ValueError("expected a stable declaration identifier")
            name = form[1]
            if name in ids:
                raise ValueError("duplicate declaration identifier")
            ids.add(name)
            match form:
                case ("field", _, *values) if values and all(isinstance(v, str) for v in values):
                    if len(set(values)) != len(values):
                        raise ValueError("duplicate field value")
                    fields[name] = tuple(values)
                case ("binary", _, kind) if kind in ("FA", "BA", "FC", "BC"):
                    if profile == "seed" and kind in ("FC", "BC"):
                        raise ValueError("composition outside seed profile")
                    binary[name] = (kind, location)
                case ("lex", _, tokens, cat, builder, assignments, score):
                    if not isinstance(tokens, tuple) or not tokens:
                        raise ValueError("empty or malformed lexical span")
                    if not all(isinstance(t, str) and re.fullmatch("[a-z]+", t) for t in tokens):
                        raise ValueError("invalid lexical token")
                    ty = category_type(cat, depth)
                    meaning = template(builder)
                    if typeof(meaning) != ty:
                        raise ValueError("builder type disagrees with lexical category")
                    state = lexical_state(assignments, fields)
                    entries[name] = Entry(tokens, cat, meaning, tuple(sorted(state.items())),
                                          lexical_cost(score, state, fields), location)
                case ("unary", _, src, dst, builder, score):
                    if profile == "seed":
                        raise ValueError("same-span unary outside seed profile")
                    ty = arrow(category_type(src, depth), category_type(dst, depth))
                    meaning = template(builder)
                    if typeof(meaning) != ty:
                        raise ValueError("unary builder type disagrees with categories")
                    unary[name] = Unary(src, dst, meaning, cost(score), location)
                    dependencies.setdefault(dst, {})[src] = None
                case _:
                    raise ValueError("unlicensed declaration or malformed fields")
        except ValueError as exc:
            raise GrammarError(f"{location} {name}: {exc}") from exc
    if depth is None:
        raise GrammarError(f"{filename}:1:1: missing category depth")
    try:
        order = tuple(TopologicalSorter(dependencies).static_order())
    except CycleError as exc:
        cycle = exc.args[1]
        edges = set(zip(cycle, cycle[1:]))
        causes = [f"{rule.location} {name}" for name, rule in unary.items()
                  if (rule.source, rule.target) in edges]
        raise GrammarError(f"{', '.join(causes)}: unary cycle") from exc
    return Grammar(depth, MappingProxyType(fields), MappingProxyType(entries),
                   MappingProxyType(binary), MappingProxyType(unary), order)
