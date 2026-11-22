#!/usr/bin/env python3
"""ClaudeOracle witness enumerator, bundle seed-witness-v1 (contract seed-1.0).

Adopts from inbox_v2 ONLY: entry IDs, recipe names, tokens, ground categories and
costs (bundle_inventory_no_meanings.json); rule IDs, derivation shapes, category
spelling, diagnostic codes, budget and 3+ readings rule (witness-v1.md).
The semantics are my own (written from contract.md), keyed by recipe name.

Method: brute force.  derive(i, j) lists EVERY derivation of the span: each
lexical entry whose tokens equal the span, plus, for every split point, every
pair of sub-derivations that combine by a licensed binary rule under exact
category equality.  Nothing is packed or pruned; derive() results are cached
per span only to avoid recomputing the same full list.

A grammar is a dict:
  {"entries": {id: {"recipe","tokens","category","cost","sem"}},
   "rules": {id: [kind, recipe]}, "roots": [...], "max_tokens": int}
built by make_grammar() from a spec (see its docstring).  Python 3.14 stdlib only.
"""
import json
import sys
from pathlib import Path

import oracle
from oracle import And, TOP, atom, fresh

HERE = Path(__file__).resolve().parent
INBOX = HERE / "inbox_v2"
INT64_MAX = 2 ** 63 - 1
INT64_MIN = -2 ** 63


class Overflow(Exception):
    pass


# ---------------------------------------------------------------- grammar

def load_bundle(path=None):
    return json.loads(Path(path or INBOX / "bundle_inventory_no_meanings.json").read_text("utf-8"))


def load_ontology(path=None):
    return json.loads(Path(path or INBOX / "ontology.yaml").read_text("utf-8"))


def make_grammar(spec=None, bundle=None):
    """Build a grammar from a spec over the published bundle.

    spec keys (all optional):
      "entries":    "all" (default) or a list of published entry IDs
      "clones":     [{"id": new, "clone_of": published id, "cost"?: int, "tokens"?: [..]}]
                    a clone keeps the source's recipe, category and meaning
      "rules":      list of rule IDs (default: all published)
      "roots":      list of root categories (default: all published)
      "max_tokens": int (default: published)
    """
    spec = spec or {}
    bundle = bundle or load_bundle()
    pub = bundle["entries"]
    ids = spec.get("entries", "all")
    ids = sorted(pub) if ids == "all" else list(ids)
    assert len(set(ids)) == len(ids), "duplicate entry id in grammar spec"
    entries = {}
    for eid in ids:
        e = pub[eid]
        entries[eid] = dict(e, sem={"recipe": e["recipe"], "tokens": e["tokens"], "category": e["category"]})
    for c in spec.get("clones", []):
        src = pub[c["clone_of"]]
        assert c["id"] not in entries, "clone id collides"
        entries[c["id"]] = {"recipe": src["recipe"], "category": src["category"],
                            "tokens": list(c.get("tokens", src["tokens"])),
                            "cost": c.get("cost", src["cost"]),
                            "sem": {"recipe": src["recipe"], "tokens": src["tokens"],
                                    "category": src["category"]}}
    rules = {r: bundle["rules"][r] for r in spec.get("rules", sorted(bundle["rules"]))}
    return {"entries": entries, "rules": rules,
            "roots": list(spec.get("roots", bundle["roots"])),
            "max_tokens": spec.get("max_tokens", bundle["max_tokens"])}


# ---------------------------------------------------------------- categories

def split_cat(cat):
    """'(X/Y)' -> (X, '/', Y); atomic category -> None.  Top-level slash only."""
    if not cat.startswith("("):
        return None
    depth = 0
    for i, ch in enumerate(cat):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch in "/\\" and depth == 1:
            return cat[1:i], ch, cat[i + 1:-1]
    raise ValueError("bad category %r" % cat)


def combine(kind, left_cat, right_cat):
    """Result category of a binary rule kind (FA or BA), or None.  Exact equality."""
    if kind == "FA":
        s = split_cat(left_cat)
        if s and s[1] == "/" and s[2] == right_cat:
            return s[0]
    elif kind == "BA":
        s = split_cat(right_cat)
        if s and s[1] == "\\" and s[2] == left_cat:
            return s[0]
    return None


# ---------------------------------------------------------------- semantics (mine)
# Values are Python closures; application is Python application.
#   NP: ("np", kind, Q)      N: predicate name      VP: subj -> (k -> formula)
#   S:  k -> formula          k: event -> formula

def _np(kind, q):
    return ("np", kind, q)


def _unit(entity):
    return _np("unit", lambda k: k(entity))


def _quant(kind, pred):
    if kind == "universal":
        def q(k):
            x = fresh()
            return ("ForallE", x, ("Implies", atom(pred, x), k(x)))
    else:
        def q(k):
            x = fresh()
            return ("ExistsE", x, And(atom(pred, x), k(x)))
    return _np(kind, q)


def _frame(ont, surface):
    for fr in ont["frames"].values():
        if surface == fr["past"]:
            return fr, "past"
        if surface == fr["bare"]:
            return fr, "bare"
    raise KeyError(surface)


def lexical_value(ont, sem):
    """Meaning of a lexical entry from its recipe name, surface and category."""
    recipe, (tok, *_), cat = sem["recipe"], sem["tokens"], sem["category"]
    if recipe == "name":
        assert ont["names"][tok] == "E"
        return _unit(tok)
    if recipe == "noun":
        return ont["nouns"][tok]
    if recipe == "det":
        kind = ont["determiners"][tok]
        return lambda pred: _quant(kind, pred)
    if recipe == "manner":
        pred = ont["modifiers"][tok]
        return lambda vp: lambda subj: lambda k: vp(subj)(lambda e: And(atom(pred, e), k(e)))
    if recipe == "infinitive":
        return lambda vp: vp
    if recipe == "negation":  # "did not": subject opened once, inner subject Unit, past once
        def aux(vp):
            return lambda subj: lambda k: subj[2](
                lambda s: ("Not", vp(_unit(s))(lambda e: And(atom("Past", e), k(e)))))
        return aux
    if recipe == "not-every":  # negate the closed ordinary "every N VP" proposition
        return lambda pred: lambda vp: lambda k: ("Not", vp(_quant("universal", pred))(lambda e: TOP))
    fr, m = _frame(ont, tok)
    pred = fr["predicate"]

    def tense(k):
        return (lambda e: And(atom("Past", e), k(e))) if m == "past" else k

    if recipe == "iv":
        def iv(subj):
            def h(k):
                def body(s):
                    e = fresh()
                    return ("ExistsV", e, And(atom(pred, e), atom("Agent", e, s), tense(k)(e)))
                return subj[2](body)
            return h
        return iv
    if recipe in ("tv.subject-wide", "tv.object-wide"):
        def tv(obj):
            def with_subj(subj):
                def h(k):
                    def body(s, o):
                        e = fresh()
                        return ("ExistsV", e, And(atom(pred, e), atom("Agent", e, s),
                                                  atom("Theme", e, o), tense(k)(e)))
                    if recipe == "tv.subject-wide":
                        return subj[2](lambda s: obj[2](lambda o: body(s, o)))
                    return obj[2](lambda o: subj[2](lambda s: body(s, o)))
                return h
            return with_subj
        return tv
    if recipe == "control":
        def ctrl(rec):
            def with_inf(vpto):
                def with_subj(subj):
                    def h(k):
                        def body(s, r):
                            c = s if fr["controller"] == "subject" else r
                            e = fresh()
                            content = ("Box", vpto(_unit(c))(lambda e2: TOP))
                            return ("ExistsV", e, And(atom(pred, e), atom("Agent", e, s),
                                                      atom("Recipient", e, r),
                                                      atom("Content", e, content), tense(k)(e)))
                        return subj[2](lambda s: rec[2](lambda r: body(s, r)))
                    return h
                return with_subj
            return with_inf
        return ctrl
    raise ValueError("no semantics for recipe %r" % recipe)


# ---------------------------------------------------------------- brute-force derivations

class Search:
    def __init__(self, grammar, ont, toks):
        self.g, self.ont, self.toks = grammar, ont, toks
        self.cache = {}

    def derive(self, i, j):
        """Every derivation of toks[i:j]: list of (key, category, value, cost, ow_uses)."""
        if (i, j) in self.cache:
            return self.cache[(i, j)]
        out = []
        for eid in sorted(self.g["entries"]):
            e = self.g["entries"][eid]
            if e["tokens"] == self.toks[i:j]:
                check_cost(e["cost"])
                out.append(((0, i, j, eid, e["recipe"]), e["category"],
                            lexical_value(self.ont, e["sem"]), e["cost"],
                            1 if e["recipe"] == "tv.object-wide" else 0))
        for k in range(i + 1, j):
            for lk, lc, lv, lcost, low in self.derive(i, k):
                for rk, rc, rv, rcost, row in self.derive(k, j):
                    for rid in sorted(self.g["rules"]):
                        kind, recipe = self.g["rules"][rid]
                        cat = combine(kind, lc, rc)
                        if cat is None:
                            continue
                        value = lv(rv) if kind == "FA" else rv(lv)
                        out.append(((1, rid, i, j, cat, recipe, (lk, rk)), cat, value,
                                    check_cost(lcost + rcost), low + row))
        self.cache[(i, j)] = out
        return out


def check_cost(c):
    if not (INT64_MIN <= c <= INT64_MAX):
        raise Overflow()
    return c


def count_edges(grammar, toks):
    """Distinct edges of a packed bottom-up chart (my reading of witness-v1 item 11).

    node          = (start, end, ground category)
    lexical edge  = (start, end, entry ID)
    binary edge   = (rule ID, left node, right node)
    Every span is built, whether or not it can reach a root.
    """
    n = len(toks)
    nodes = {}
    edges = 0
    for i in range(n):
        for j in range(i + 1, n + 1):
            for e in grammar["entries"].values():
                if e["tokens"] == toks[i:j]:
                    edges += 1
                    nodes.setdefault((i, j), set()).add(e["category"])
    for width in range(2, n + 1):
        for i in range(0, n - width + 1):
            j = i + width
            new = set()
            for k in range(i + 1, j):
                for lc in sorted(nodes.get((i, k), ())):
                    for rc in sorted(nodes.get((k, j), ())):
                        for kind, _ in grammar["rules"].values():
                            cat = combine(kind, lc, rc)
                            if cat is not None:
                                edges += 1
                                new.add(cat)
            if new:
                nodes.setdefault((i, j), set()).update(new)
    return edges


# ---------------------------------------------------------------- driver

def jsonable(key):
    return [jsonable(x) if isinstance(x, tuple) else x for x in key]


def _result(tokens, status, decision, code, token=None, index=None,
            readings=(), witnesses=(), ranked=(), min_cost=None):
    diag = {"code": code}
    if token is not None:
        diag["token"], diag["index"] = token, index
    return {"tokens": list(tokens), "construction_status": status, "decision": decision,
            "diagnostic": diag, "readings": list(readings), "min_cost": min_cost,
            "ranked_readings": list(ranked), "witnesses": list(witnesses)}


def analyse(sentence, grammar=None, ont=None, max_edges=None):
    """Full expected output for one request.  See witness-v1.md for the codes."""
    grammar = grammar or make_grammar()
    ont = ont or load_ontology()
    if not isinstance(sentence, str):
        return _result([], "error", "abstain", "invalid_request")
    if max_edges is not None and (isinstance(max_edges, bool) or not isinstance(max_edges, int)
                                  or max_edges < 0):
        return _result([], "error", "abstain", "invalid_request")
    toks = oracle.tokenize(sentence)
    if not toks:
        return _result(toks, "no_parse", "abstain", "empty_input")
    vocab = {t for e in grammar["entries"].values() for t in e["tokens"]}
    for idx, t in enumerate(toks):  # left to right; spelling before vocabulary
        if not oracle.TOKEN_RE.match(t):
            return _result(toks, "no_parse", "abstain", "invalid_token", t, idx)
        if t not in vocab:
            return _result(toks, "no_parse", "abstain", "unknown_token", t, idx)
    if len(toks) > grammar["max_tokens"]:
        return _result(toks, "no_parse", "abstain", "no_root")
    if max_edges is not None and count_edges(grammar, toks) > max_edges:
        return _result(toks, "truncated", "abstain", "edge_budget")
    try:
        all_spans = Search(grammar, ont, toks).derive(0, len(toks))
    except Overflow:
        return _result(toks, "error", "abstain", "cost_overflow")
    roots = [d for d in all_spans if d[1] in grammar["roots"]]
    if not roots:
        return _result(toks, "no_parse", "abstain", "no_root")
    witnesses = []
    for key, cat, value, cost, ow in roots:
        formula = value(lambda e: TOP)  # root closure: no edge, no key
        oracle.check_sorts(ont, formula)
        witnesses.append({"cost": cost, "object_wide_uses": ow, "key": key,
                          "reading": oracle.canon(formula)})
    witnesses.sort(key=lambda w: (w["cost"], w["object_wide_uses"], w["key"]))
    ranked = []
    for idx, w in enumerate(witnesses):
        w["rank"] = idx
        w["key"] = jsonable(w["key"])
        if w["reading"] not in ranked:
            ranked.append(w["reading"])
    readings = sorted(ranked, key=lambda s: s.encode("ascii"))
    extra = dict(readings=readings, witnesses=witnesses, ranked=ranked, min_cost=witnesses[0]["cost"])
    if len(readings) == 1:
        return _result(toks, "complete", "accepted", "", **extra)
    if len(readings) == 2:
        return _result(toks, "complete", "ambiguous", "", **extra)
    return _result(toks, "error", "abstain", "reading_count", **extra)


# ---------------------------------------------------------------- replay

def replay(key, grammar, ont, toks):
    """Recompute (category, reading, cost, ow_uses) from a JSON witness key alone."""
    def go(k):
        if k[0] == 0:
            _, i, j, eid, recipe = k
            e = grammar["entries"][eid]
            assert e["tokens"] == toks[i:j] and e["recipe"] == recipe, k
            return i, j, e["category"], lexical_value(ont, e["sem"]), e["cost"], int(recipe == "tv.object-wide")
        _, rid, i, j, cat, recipe, (lk, rk) = k
        kind, rrecipe = grammar["rules"][rid]
        li, lj, lc, lv, lcost, low = go(lk)
        ri, rj, rc, rv, rcost, row = go(rk)
        assert (li, lj, rj) == (i, ri, j) and recipe == rrecipe and combine(kind, lc, rc) == cat, k
        return i, j, cat, (lv(rv) if kind == "FA" else rv(lv)), lcost + rcost, low + row
    i, j, cat, value, cost, ow = go(key)
    assert (i, j) == (0, len(toks)) and cat in grammar["roots"]
    return cat, oracle.canon(value(lambda e: TOP)), cost, ow


if __name__ == "__main__":
    for s in sys.argv[1:]:
        print(json.dumps(analyse(s), indent=1))
