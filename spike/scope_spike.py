#!/usr/bin/env python3
"""Disposable scope spike for plan 09 (standard library only).

Parses a sentence with a tiny typed CCG (forward and backward application),
packs alternatives into a chart, extracts every derivation, builds and
normalizes each meaning, and evaluates the meanings in small finite worlds.

Replay:  python3 spike/scope_spike.py
Tests:   python3 -m unittest discover -s spike -v
"""
import hashlib
import json
import sys

# --------------------------------------------------------------------------
# Types and terms. Terms use de Bruijn indices so alpha-equivalent terms are
# identical tuples.
# --------------------------------------------------------------------------

E, V, P = "E", "V", "P"


def arrow(a, b):
    return ("->", a, b)


R = arrow(E, P)   # entity predicate
Q = arrow(R, P)   # generalized quantifier (every NP)
K = arrow(V, P)   # event continuation
H = arrow(K, P)   # clause meaning

SIGNATURE = {
    "Top": P,
    "And": arrow(P, arrow(P, P)),
    "Implies": arrow(P, arrow(P, P)),
    "ForallE": Q,
    "ExistsE": Q,
    "ExistsV": H,
    "Researcher": R,
    "Paper": R,
    "Review": K,
    "Past": K,
    "Agent": arrow(V, arrow(E, P)),
    "Theme": arrow(V, arrow(E, P)),
    "alice": E,
    "bob": E,
}


def var(i):
    return ("var", i)


def const(name):
    return ("const", name)


def lam(ty, body):
    return ("lam", ty, body)


def app(f, *args):
    for a in args:
        f = ("app", f, a)
    return f


def named(term, env=()):
    """Convert a term written with named binders into de Bruijn form.

    Named form: ("v", name) | ("fn", name, type, body) | ("app", f, a) | const.
    A free name is an error, so templates cannot capture by accident.
    """
    tag = term[0]
    if tag == "v":
        return var(env.index(term[1]))
    if tag == "fn":
        return lam(term[2], named(term[3], (term[1],) + env))
    if tag == "app":
        return ("app", named(term[1], env), named(term[2], env))
    return term


def v(name):
    return ("v", name)


def fn(name, ty, body):
    return ("fn", name, ty, body)


def typeof(term, ctx=()):
    tag = term[0]
    if tag == "var":
        return ctx[term[1]]
    if tag == "const":
        return SIGNATURE[term[1]]
    if tag == "lam":
        return arrow(term[1], typeof(term[2], (term[1],) + ctx))
    f, a = typeof(term[1], ctx), typeof(term[2], ctx)
    if f[0] != "->" or f[1] != a:
        raise TypeError(f"cannot apply {f} to {a}")
    return f[2]


def shift(term, d, cutoff=0):
    tag = term[0]
    if tag == "var":
        return var(term[1] + d) if term[1] >= cutoff else term
    if tag == "lam":
        return lam(term[1], shift(term[2], d, cutoff + 1))
    if tag == "app":
        return ("app", shift(term[1], d, cutoff), shift(term[2], d, cutoff))
    return term


def subst(term, j, s):
    tag = term[0]
    if tag == "var":
        return s if term[1] == j else term
    if tag == "lam":
        return lam(term[1], subst(term[2], j + 1, shift(s, 1)))
    if tag == "app":
        return ("app", subst(term[1], j, s), subst(term[2], j, s))
    return term


def beta(term):
    """Full beta normalization (terminates: the calculus is simply typed)."""
    tag = term[0]
    if tag == "lam":
        return lam(term[1], beta(term[2]))
    if tag == "app":
        f, a = beta(term[1]), beta(term[2])
        if f[0] == "lam":
            return beta(shift(subst(f[2], 0, shift(a, 1)), -1))
        return ("app", f, a)
    return term


# --------------------------------------------------------------------------
# Exact normalization of formulas: flatten directly nested conjunctions,
# drop Top, sort conjuncts, rebuild right-associated. Nothing crosses a
# quantifier or an implication. Repeated conjuncts are kept.
# --------------------------------------------------------------------------

def spine(term):
    args = []
    while term[0] == "app":
        args.append(term[2])
        term = term[1]
    return term, args[::-1]


def canonical(term):
    """Deterministic s-expression; identical for alpha-equivalent terms."""
    tag = term[0]
    if tag == "var":
        return f"#{term[1]}"
    if tag == "const":
        return term[1]
    if tag == "lam":
        return f"(lam {type_name(term[1])} {canonical(term[2])})"
    head, args = spine(term)
    return "(" + " ".join(canonical(t) for t in [head] + args) + ")"


def type_name(ty):
    return ty if isinstance(ty, str) else f"({type_name(ty[1])}->{type_name(ty[2])})"


def conjuncts(term):
    head, args = spine(term)
    if head == const("And") and len(args) == 2:
        return conjuncts(args[0]) + conjuncts(args[1])
    return [term]


def normalize(term):
    tag = term[0]
    if tag == "lam":
        return lam(term[1], normalize(term[2]))
    if tag != "app":
        return term
    head, args = spine(term)
    if head == const("And") and len(args) == 2:
        parts = [normalize(c) for c in conjuncts(term)]
        parts = [c for c in parts if c != const("Top")]
        parts.sort(key=canonical)
        if not parts:
            return const("Top")
        out = parts[-1]
        for c in reversed(parts[:-1]):
            out = app(const("And"), c, out)
        return out
    return app(head, *[normalize(a) for a in args])


def close(h):
    """Root closure: apply a clause meaning to the always-true continuation."""
    return app(h, lam(V, const("Top")))


def meaning_of(clause_term):
    raw = beta(close(clause_term))
    if typeof(raw) != P:
        raise TypeError("closed clause is not a proposition")
    return raw, normalize(raw)


def pretty(term, names=()):
    tag = term[0]
    if tag == "var":
        return names[term[1]]
    if tag == "const":
        return term[1]
    head, args = spine(term)
    name = head[1] if head[0] == "const" else None
    if name in ("ForallE", "ExistsE", "ExistsV") and args[0][0] == "lam":
        binder = ("e" if args[0][1] == V else "x") + str(len(names))
        word = "forall" if name == "ForallE" else "exists"
        return f"{word} {binder}. {pretty(args[0][2], (binder,) + names)}"
    if name == "And":
        return "(" + " & ".join(pretty(c, names) for c in conjuncts(term)) + ")"
    if name == "Implies":
        return f"({pretty(args[0], names)} -> {pretty(args[1], names)})"
    return f"{pretty(head, names)}(" + ", ".join(pretty(a, names) for a in args) + ")"


# --------------------------------------------------------------------------
# Finite-model evaluation of a normalized closed proposition.
# --------------------------------------------------------------------------

def evaluate(term, world, env=()):
    head, args = spine(term)
    name = head[1]
    if name == "Top":
        return True
    if name == "And":
        return evaluate(args[0], world, env) and evaluate(args[1], world, env)
    if name == "Implies":
        return (not evaluate(args[0], world, env)) or evaluate(args[1], world, env)
    if name in ("ForallE", "ExistsE", "ExistsV"):
        domain = world["events"] if name == "ExistsV" else world["entities"]
        results = (evaluate(args[0][2], world, (d,) + env) for d in domain)
        return all(results) if name == "ForallE" else any(results)
    values = [env[a[1]] if a[0] == "var" else a[1] for a in args]
    return values in world["facts"].get(name, [])


# Two researchers each reviewed a different paper; no paper has both.
SEPARATING_WORLD = {
    "entities": ["r1", "r2", "p1", "p2"],
    "events": ["e1", "e2"],
    "facts": {
        "Researcher": [["r1"], ["r2"]],
        "Paper": [["p1"], ["p2"]],
        "Review": [["e1"], ["e2"]],
        "Past": [["e1"], ["e2"]],
        "Agent": [["e1", "r1"], ["e2", "r2"]],
        "Theme": [["e1", "p1"], ["e2", "p2"]],
    },
}

# Both researchers reviewed the same paper.
SHARED_PAPER_WORLD = dict(
    SEPARATING_WORLD,
    facts=dict(SEPARATING_WORLD["facts"], Theme=[["e1", "p1"], ["e2", "p1"]]),
)

# --------------------------------------------------------------------------
# Categories, lexicon and morphology.
# --------------------------------------------------------------------------

N, NP, S = "N", "NP", "S[fin]"


def fwd(x, y):
    return ("/", x, y)      # X/Y: seeks Y to the right


def bwd(x, y):
    return ("\\", x, y)     # X\Y: seeks Y to the left


def cat_name(c):
    return c if isinstance(c, str) else f"({cat_name(c[1])}{c[0]}{cat_name(c[2])})"


def sem_type(c):
    if isinstance(c, str):
        return {N: R, NP: Q, S: H}[c]
    return arrow(sem_type(c[2]), sem_type(c[1]))


def quantifier(binder, connective):
    return named(fn("r", R, fn("k", R, ("app", const(binder), fn(
        "x", E, app(const(connective), ("app", v("r"), v("x")), ("app", v("k"), v("x"))))))))


def unit(name):
    return named(fn("k", R, ("app", v("k"), const(name))))


def transitive(predicate, tense, subject_wide):
    """Transitive verb frame; syntactic arguments arrive object first."""
    frame = [app(const(predicate), v("e")), app(const("Agent"), v("e"), v("s")),
             app(const("Theme"), v("e"), v("o"))]
    if tense == "past":
        frame.append(app(const("Past"), v("e")))
    body = ("app", v("k"), v("e"))
    for part in reversed(frame):
        body = app(const("And"), part, body)
    event = ("app", const("ExistsV"), fn("e", V, body))
    if subject_wide:
        core = ("app", v("qs"), fn("s", E, ("app", v("qo"), fn("o", E, event))))
    else:
        core = ("app", v("qo"), fn("o", E, ("app", v("qs"), fn("s", E, event))))
    return named(fn("qo", Q, fn("qs", Q, fn("k", K, core))))


# surface form -> (lemma, features)
MORPHOLOGY = {
    "every": ("every", {}), "a": ("a", {}),
    "researcher": ("researcher", {}), "paper": ("paper", {}),
    "alice": ("alice", {}), "bob": ("bob", {}),
    "reviewed": ("review", {"tense": "past"}),
}

TV = fwd(bwd(S, NP), NP)

# Each entry: (source id, lemma, category, cost, builder(features) -> term)
LEXICON = [
    ("every.det", "every", fwd(NP, N), 0, lambda f: quantifier("ForallE", "Implies")),
    ("a.det", "a", fwd(NP, N), 0, lambda f: quantifier("ExistsE", "And")),
    ("researcher.n", "researcher", N, 0, lambda f: const("Researcher")),
    ("paper.n", "paper", N, 0, lambda f: const("Paper")),
    ("alice.name", "alice", NP, 0, lambda f: unit("alice")),
    ("bob.name", "bob", NP, 0, lambda f: unit("bob")),
    ("review.tv.subject-wide", "review", TV, 10,
     lambda f: transitive("Review", f.get("tense"), True)),
    ("review.tv.object-wide", "review", TV, 10,
     lambda f: transitive("Review", f.get("tense"), False)),
]


def tokenize(text):
    return text.strip().rstrip(".").lower().split()


# --------------------------------------------------------------------------
# Packed chart. A node is (start, end, category). Edges are alternatives.
# --------------------------------------------------------------------------

def build_chart(tokens, lexicon):
    """Return (chart, lexical). chart maps node -> list of distinct edges."""
    chart, lexical = {}, {}

    def add(node, edge):
        edges = chart.setdefault(node, [])
        if edge not in edges:           # reinsertion is idempotent
            edges.append(edge)

    for i, token in enumerate(tokens):
        if token not in MORPHOLOGY:
            continue
        lemma, feats = MORPHOLOGY[token]
        for source, entry_lemma, category, cost, build in lexicon:
            if entry_lemma == lemma:
                term = build(feats)
                if typeof(term) != sem_type(category):
                    raise TypeError(f"{source}: term does not match {cat_name(category)}")
                lexical[(source, i)] = (term, cost)
                add((i, i + 1, category), ("lex", source, i))

    n = len(tokens)
    for width in range(2, n + 1):
        for i in range(n - width + 1):
            j = i + width
            for k in range(i + 1, j):
                lefts = [nd for nd in list(chart) if nd[0] == i and nd[1] == k]
                rights = [nd for nd in list(chart) if nd[0] == k and nd[1] == j]
                for left in lefts:
                    for right in rights:
                        lc, rc = left[2], right[2]
                        if not isinstance(lc, str) and lc[0] == "/" and lc[2] == rc:
                            add((i, j, lc[1]), ("FA", left, right))
                        if not isinstance(rc, str) and rc[0] == "\\" and rc[2] == lc:
                            add((i, j, rc[1]), ("BA", left, right))
    return chart, lexical


def derivations(node, chart):
    """Every derivation tree below a node, as JSON-friendly witnesses."""
    out = []
    for edge in chart[node]:
        if edge[0] == "lex":
            out.append({"lex": edge[1], "at": edge[2]})
        else:
            for left in derivations(edge[1], chart):
                for right in derivations(edge[2], chart):
                    out.append({"rule": edge[0], "span": [node[0], node[1]],
                                "category": cat_name(node[2]), "children": [left, right]})
    return out


def best_cost(node, chart, lexical):
    """Minimum cost computed on the packed chart, without unpacking."""
    costs = []
    for edge in chart[node]:
        if edge[0] == "lex":
            costs.append(lexical[(edge[1], edge[2])][1])
        else:
            costs.append(best_cost(edge[1], chart, lexical) + best_cost(edge[2], chart, lexical))
    return min(costs)


def replay(witness, tokens, lexicon=None):
    """Rebuild (term, cost) from a witness alone, without the chart."""
    lexicon = LEXICON if lexicon is None else lexicon
    if "lex" in witness:
        _, feats = MORPHOLOGY[tokens[witness["at"]]]
        for source, _, _, cost, build in lexicon:
            if source == witness["lex"]:
                return build(feats), cost
        raise KeyError(witness["lex"])
    (lt, lcost), (rt, rcost) = (replay(c, tokens, lexicon) for c in witness["children"])
    term = ("app", lt, rt) if witness["rule"] == "FA" else ("app", rt, lt)
    return term, lcost + rcost


def witness_key(witness):
    return json.dumps(witness, sort_keys=True)


def parse(text, lexicon=None):
    """Parse a sentence and return a result record."""
    lexicon = LEXICON if lexicon is None else lexicon
    tokens = tokenize(text)
    chart, lexical = build_chart(tokens, lexicon)
    root = (0, len(tokens), S)
    result = {"input": text, "tokens": tokens, "nodes": len(chart),
              "edges": sum(len(e) for e in chart.values())}
    if root not in chart:
        return dict(result, construction_status="no_parse", decision="abstain", readings=[])

    readings = {}
    for witness in derivations(root, chart):
        term, cost = replay(witness, tokens, lexicon)
        raw, norm = meaning_of(term)
        reading = readings.setdefault(canonical(norm), {
            "normalized": canonical(norm), "pretty": pretty(norm),
            "raw": canonical(raw), "derivations": [], "_term": norm})
        reading["derivations"].append({"cost": cost, "witness": witness})

    # Tie policy: lower cost first, then the witness's canonical JSON text.
    for reading in readings.values():
        reading["derivations"].sort(key=lambda d: (d["cost"], witness_key(d["witness"])))
        reading["cost"] = reading["derivations"][0]["cost"]
    ordered = sorted(readings.values(), key=lambda r: (
        r["cost"], witness_key(r["derivations"][0]["witness"])))

    assert ordered[0]["cost"] == best_cost(root, chart, lexical)
    return dict(result, construction_status="complete",
                decision="accepted" if len(ordered) == 1 else "ambiguous",
                root=[0, len(tokens), S], root_edges=len(chart[root]),
                best_cost=ordered[0]["cost"], readings=ordered)


def public(result):
    """The record without internal term objects, ready for JSON."""
    out = dict(result)
    out["readings"] = [{k: val for k, val in r.items() if k != "_term"}
                       for r in result["readings"]]
    return out


def digest(result):
    text = json.dumps(public(result), sort_keys=True)
    return hashlib.sha256(text.encode()).hexdigest()


def main():
    sentence = "Every researcher reviewed a paper"
    result = parse(sentence)
    reversed_result = parse(sentence, LEXICON[::-1])
    report = public(result)
    report["worlds"] = {
        name: {r["pretty"]: evaluate(r["_term"], world) for r in result["readings"]}
        for name, world in (("separating", SEPARATING_WORLD), ("shared_paper", SHARED_PAPER_WORLD))
    }
    report["separating_world"] = SEPARATING_WORLD
    report["digest"] = digest(result)
    report["digest_with_reversed_lexicon"] = digest(reversed_result)
    json.dump(report, sys.stdout, indent=2)
    print()
    return 0 if report["digest"] == report["digest_with_reversed_lexicon"] else 1


if __name__ == "__main__":
    sys.exit(main())
