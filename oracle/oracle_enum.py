#!/usr/bin/env python3
"""ClaudeOracle exhaustive enumerator for the M01 public contract (seed-0.2-draft).

Brute force: for every production of the contract's surface grammar, try every
split point of the span.  No chart, no packing, no pruning, no memoisation.
Written from inbox_v1/contract.md and inbox_v1/ontology.yaml only; reuses the
tokenizer, term constructors and canonical printer of oracle.py (unchanged).

Two independent meaning computations are kept apart on purpose:
  * enumeration time: the production-level recipes in oracle.py (root_readings)
  * replay():         a compositional interpreter over the witness tree alone
                      (lexical entries + FA/BA), which also re-checks categories
The self-test requires them to agree for every witness.

Witness shape (application-only derivation, JSON-serialisable):
  lexical: {"t":"lex","start","end","entry","recipe","cat"}
  rule:    {"t":"rule","rule":"FA"|"BA","start","end","cat","recipe":"apply","children":[l,r]}
IDs and category spellings are MINE (the public grammar bundle with stable IDs
was not part of my inputs) -- see STATUS.md, underspecification list.
"""
import json
import sys

import oracle
from oracle import And, TOP, atom, fresh

TV_COST = 10  # contract: 10 for either lexical scope recipe of any transitive frame


class Truncated(Exception):
    pass


# ---------------------------------------------------------------- categories

def VP(m):
    return "(S[%s]\\NP)" % m


def fwd(x, y):
    return "(%s/%s)" % (x, y)


def bwd(x, y):
    return "(%s\\%s)" % (x, y)


def split_cat(cat):
    """'(X/Y)' -> (X, '/', Y); atomic -> None.  Top-level slash only."""
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


# ---------------------------------------------------------------- witness nodes

def leaf(i, j, entry, recipe, cat):
    return {"t": "lex", "start": i, "end": j, "entry": entry, "recipe": recipe, "cat": cat}


def FA(l, r):
    x, slash, y = split_cat(l["cat"])
    assert slash == "/" and y == r["cat"], (l["cat"], r["cat"])
    return {"t": "rule", "rule": "FA", "start": l["start"], "end": r["end"],
            "cat": x, "recipe": "apply", "children": [l, r]}


def BA(l, r):
    x, slash, y = split_cat(r["cat"])
    assert slash == "\\" and y == l["cat"], (l["cat"], r["cat"])
    return {"t": "rule", "rule": "BA", "start": l["start"], "end": r["end"],
            "cat": x, "recipe": "apply", "children": [l, r]}


# ---------------------------------------------------------------- brute-force grammar
# Each function returns every analysis of toks[i:j] (the whole span) as a list of
# (witness_node, surface_info) pairs.  surface_info feeds oracle.py's recipes.

class Enumerator:
    def __init__(self, lex, toks, budget=None):
        self.lex, self.toks, self.budget, self.steps = lex, toks, budget, 0

    def tick(self):
        self.steps += 1
        if self.budget is not None and self.steps > self.budget:
            raise Truncated()

    # -- terminals ---------------------------------------------------------
    def name(self, i, j):
        self.tick()
        if j - i == 1 and self.toks[i] in self.lex.names:
            t = self.toks[i]
            return [(leaf(i, j, "name:" + t, "name.unit", "NP"), ("name", t))]
        return []

    def det(self, i, j):
        self.tick()
        if j - i == 1 and self.toks[i] in self.lex.dets:
            t = self.toks[i]
            kind = self.lex.dets[t]
            return [(leaf(i, j, "det:" + t, "det." + kind, fwd("NP", "N")), kind)]
        return []

    def noun(self, i, j):
        self.tick()
        if j - i == 1 and self.toks[i] in self.lex.nouns:
            t = self.toks[i]
            return [(leaf(i, j, "noun:" + t, "noun.pred", "N"), self.lex.nouns[t])]
        return []

    def word(self, i, j, words, entry, recipe, cat):
        self.tick()
        if self.toks[i:j] == words:
            return [leaf(i, j, entry, recipe, cat)]
        return []

    def verb(self, i, j, m, constructions):
        self.tick()
        if j - i != 1:
            return []
        fr = self.lex.verbs[m].get(self.toks[i])
        if fr is None or fr["construction"] not in constructions:
            return []
        return [fr]

    # -- NP ::= Name | Det N ---------------------------------------------
    def np(self, i, j):
        out = list(self.name(i, j))
        for k in range(i + 1, j):
            for d, kind in self.det(i, k):
                for n, pred in self.noun(k, j):
                    out.append((FA(d, n), ("det", kind, pred)))
        return out

    # -- Simple[m] ::= Intransitive[m] ["quickly"] | Transitive[m] NP ["quickly"]
    def core(self, i, j, m, subj_kind):
        """Simple VP without the optional adverb."""
        f = "fin" if m == "past" else "bare"
        out = []
        for fr in self.verb(i, j, m, ("intransitive",)):
            node = leaf(i, j, "verb:%s:%s" % (fr["id"], m), "iv.default", VP(f))
            out.append((node, {"kind": "simple", "frame": fr, "obj": None, "quick": False}, "default"))
        for k in range(i + 1, j):
            for fr in self.verb(i, k, m, ("transitive",)):
                for o, osurf in self.np(k, j):
                    okind = "unit" if osurf[0] == "name" else osurf[1]
                    for recipe in fr["scope"]:
                        # licence: both orders for mixed universal/existential and for
                        # anything involving Unit; like quantifiers subject-wide only
                        if recipe == "object-wide" and not (
                                "unit" in (subj_kind, okind) or subj_kind != okind):
                            continue
                        v = leaf(i, k, "verb:%s:%s" % (fr["id"], m), "tv." + recipe,
                                 fwd(VP(f), "NP"))
                        out.append((FA(v, o), {"kind": "simple", "frame": fr, "obj": osurf,
                                               "quick": False}, recipe))
        return out

    def simple(self, i, j, m, subj_kind):
        f = "fin" if m == "past" else "bare"
        out = list(self.core(i, j, m, subj_kind))
        for k in range(i + 1, j):
            for q in self.word(k, j, ["quickly"], "mod:quickly", "manner.quick",
                               bwd(VP(f), VP(f))):
                for c, surf, recipe in self.core(i, k, m, subj_kind):
                    out.append((BA(c, q), dict(surf, quick=True), recipe))
        return out

    # -- VP[m] ::= Simple[m] | Control[m] NP "to" Simple[bare] --------------
    def vp(self, i, j, m, subj_kind):
        f = "fin" if m == "past" else "bare"
        out = list(self.simple(i, j, m, subj_kind))
        for a in range(i + 1, j):
            for fr in self.verb(i, a, m, ("subject-control", "object-control")):
                for b in range(a + 1, j):
                    for r, rsurf in self.np(a, b):
                        for c in range(b + 1, j):
                            for to in self.word(b, c, ["to"], "op:to", "to.lift",
                                                fwd(VP("to"), VP("bare"))):
                                # embedded subject is Unit(controller) for either frame
                                for e, esurf, recipe in self.simple(c, j, "bare", "unit"):
                                    v = leaf(i, a, "verb:%s:%s" % (fr["id"], m),
                                             "control." + fr["controller"],
                                             fwd(fwd(VP(f), VP("to")), "NP"))
                                    node = FA(FA(v, r), FA(to, e))
                                    out.append((node, {"kind": "control", "frame": fr,
                                                       "rec": rsurf, "emb": esurf}, recipe))
        return out

    # -- Root ::= NP VP[past] | NP "did" "not" VP[bare] | "not" "every" N VP[past]
    def root(self):
        n = len(self.toks)
        out = []
        for a in range(1, n):
            for s, ssurf in self.np(0, a):
                skind = "unit" if ssurf[0] == "name" else ssurf[1]
                for v, vsurf, recipe in self.vp(a, n, "past", skind):
                    out.append((BA(s, v), {"root": "ordinary", "subj": ssurf, "vp": vsurf}, recipe))
                for b in range(a + 1, n):
                    for aux in self.word(a, b, ["did", "not"], "op:did_not", "aux.neg-past",
                                         fwd(VP("fin"), VP("bare"))):
                        # VP negation supplies Unit(s) to the inner VP
                        for v, vsurf, recipe in self.vp(b, n, "bare", "unit"):
                            out.append((BA(s, FA(aux, v)),
                                        {"root": "vpneg", "subj": ssurf, "vp": vsurf}, recipe))
        for a in range(1, n):
            for mac in self.word(0, a, ["not", "every"], "op:not_every", "macro.not-every",
                                 fwd(fwd("S[fin]", VP("fin")), "N")):
                for b in range(a + 1, n):
                    for nn, pred in self.noun(a, b):
                        for v, vsurf, recipe in self.vp(b, n, "past", "universal"):
                            out.append((FA(FA(mac, nn), v),
                                        {"root": "notevery",
                                         "subj": ("det", "universal", pred), "vp": vsurf}, recipe))
        return out


# ---------------------------------------------------------------- cost and tie order

def leaves(node):
    if node["t"] == "lex":
        yield node
    else:
        for c in node["children"]:
            yield from leaves(c)


def cost(node):
    return sum(TV_COST for l in leaves(node) if l["recipe"].startswith("tv."))


def object_wide_uses(node):
    return sum(1 for l in leaves(node) if l["recipe"] == "tv.object-wide")


def key(node):
    """Structural witness key (contract, tie order item 3)."""
    if node["t"] == "lex":
        return (0, node["start"], node["end"], node["entry"], node["recipe"])
    return (1, node["rule"], node["start"], node["end"], node["cat"], node["recipe"],
            tuple(key(c) for c in node["children"]))


def rank(node):
    return (cost(node), object_wide_uses(node), key(node))


# ---------------------------------------------------------------- replay
# Compositional interpretation of a witness tree: lexical lambda terms (as
# Python closures) combined by forward/backward application only.

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


def _past(m, k):
    return (lambda e: And(atom("Past", e), k(e))) if m == "past" else k


def lexical_value(lex, node):
    kind, _, rest = node["entry"].partition(":")
    recipe = node["recipe"]
    if kind == "name":
        assert rest in lex.names and recipe == "name.unit"
        return _unit(rest)
    if kind == "noun":
        return lex.nouns[rest]
    if kind == "det":
        dk = lex.dets[rest]
        assert recipe == "det." + dk
        return lambda pred: _quant(dk, pred)
    if kind == "mod":
        assert rest == "quickly"
        return lambda vp: lambda subj: lambda k: vp(subj)(lambda e: And(atom("Quick", e), k(e)))
    if kind == "op" and rest == "to":
        return lambda vp: vp
    if kind == "op" and rest == "did_not":
        def aux(vp):
            def with_subj(subj):
                return lambda k: subj[2](lambda s: ("Not", vp(_unit(s))(_past("past", k))))
            return with_subj
        return aux
    if kind == "op" and rest == "not_every":
        # negate the closed ordinary 'every N VP' proposition
        return lambda pred: lambda vp: lambda k: ("Not", vp(_quant("universal", pred))(lambda e: TOP))
    if kind == "verb":
        fid, _, m = rest.rpartition(":")
        fr = lex.ont["frames"][fid]
        pred = fr["predicate"]
        if recipe == "iv.default":
            def iv(subj):
                def h(k):
                    kk = _past(m, k)

                    def body(s):
                        e = fresh()
                        return ("ExistsV", e, And(atom(pred, e), atom("Agent", e, s), kk(e)))
                    return subj[2](body)
                return h
            return iv
        if recipe in ("tv.subject-wide", "tv.object-wide"):
            def tv(obj):
                def with_subj(subj):
                    kinds = (subj[1], obj[1])
                    if recipe == "tv.object-wide" and not ("unit" in kinds or kinds[0] != kinds[1]):
                        raise ValueError("unlicensed object-wide recipe for kinds %r" % (kinds,))

                    def h(k):
                        kk = _past(m, k)

                        def body(s, o):
                            e = fresh()
                            return ("ExistsV", e, And(atom(pred, e), atom("Agent", e, s),
                                                      atom("Theme", e, o), kk(e)))
                        if recipe == "tv.subject-wide":
                            return subj[2](lambda s: obj[2](lambda o: body(s, o)))
                        return obj[2](lambda o: subj[2](lambda s: body(s, o)))
                    return h
                return with_subj
            return tv
        if recipe in ("control.subject", "control.recipient"):
            assert recipe == "control." + fr["controller"]

            def ctrl(rec):
                def with_inf(vpto):
                    def with_subj(subj):
                        def h(k):
                            kk = _past(m, k)

                            def body(s, r):
                                c = s if recipe == "control.subject" else r
                                e = fresh()
                                content = ("Box", vpto(_unit(c))(lambda e2: TOP))
                                return ("ExistsV", e, And(atom(pred, e), atom("Agent", e, s),
                                                          atom("Recipient", e, r),
                                                          atom("Content", e, content), kk(e)))
                            return subj[2](lambda s: rec[2](lambda r: body(s, r)))
                        return h
                    return with_subj
                return with_inf
            return ctrl
    raise ValueError("unknown lexical entry %r / %r" % (node["entry"], recipe))


def _value(lex, node):
    if node["t"] == "lex":
        return lexical_value(lex, node)
    l, r = node["children"]
    assert l["end"] == r["start"] and node["start"] == l["start"] and node["end"] == r["end"]
    if node["rule"] == "FA":
        x, slash, y = split_cat(l["cat"])
        assert slash == "/" and y == r["cat"] and x == node["cat"], node
        return _value(lex, l)(_value(lex, r))
    if node["rule"] == "BA":
        x, slash, y = split_cat(r["cat"])
        assert slash == "\\" and y == l["cat"] and x == node["cat"], node
        return _value(lex, r)(_value(lex, l))
    raise ValueError("unlicensed rule %r" % node["rule"])


def replay(witness, n_tokens, ont=None, lex=None):
    """Recompute the canonical meaning from the witness tree alone."""
    ont = ont or oracle.load_ontology()
    lex = lex or oracle.Lexicon(ont)
    assert witness["cat"] == "S[fin]" and witness["start"] == 0 and witness["end"] == n_tokens
    formula = _value(lex, witness)(lambda e: TOP)
    oracle.check_sorts(ont, formula)
    return oracle.canon(formula)


# ---------------------------------------------------------------- driver

def _result(tokens, status, decision, diagnostic="", readings=(), witnesses=(), ranked=(), min_cost=None):
    return {"tokens": list(tokens), "construction_status": status, "decision": decision,
            "diagnostic": diagnostic, "readings": list(readings), "min_cost": min_cost,
            "ranked_meanings": list(ranked), "witnesses": list(witnesses)}


def enumerate_all(sentence, ont=None, lex=None, budget=None):
    """Exhaustive analysis of one request.

    witnesses: every licensed witness, in rank order (cost, object-wide uses, key).
    ranked_meanings: distinct meanings in display order (by best witness).
    readings: the canonical target set (distinct meanings in byte order).
    budget: optional cap on enumeration steps -> truncated/abstain.
    """
    ont = ont or oracle.load_ontology()
    lex = lex or oracle.Lexicon(ont)
    if not isinstance(sentence, str):
        return _result([], "error", "abstain", "malformed request: sentence is not a string")
    toks = oracle.tokenize(sentence)
    if not toks:
        return _result(toks, "no_parse", "abstain", "lexical failure: empty input")
    bad = [t for t in toks if not oracle.TOKEN_RE.match(t)]
    if bad:
        return _result(toks, "no_parse", "abstain", "lexical failure: unsupported token %r" % bad[0])
    unknown = [t for t in toks if t not in lex.surface]
    if unknown:
        return _result(toks, "no_parse", "abstain", "lexical failure: unknown token %r" % unknown[0])
    try:
        roots = Enumerator(lex, toks, budget).root()
    except Truncated:
        return _result(toks, "truncated", "abstain", "resource budget exhausted (%d steps)" % budget)
    if not roots:
        return _result(toks, "no_parse", "abstain", "no licensed derivation: zero roots")

    witnesses = []
    for node, surf, recipe in roots:
        ids = {wid.rsplit("/", 1)[-1]: f for wid, f in oracle.root_readings(surf)}
        formula = ids[recipe]  # KeyError here = licence disagreement with oracle.py
        oracle.check_sorts(ont, formula)
        witnesses.append({"cost": cost(node), "object_wide_uses": object_wide_uses(node),
                          "key": key(node), "meaning": oracle.canon(formula), "tree": node})
    witnesses.sort(key=lambda w: (w["cost"], w["object_wide_uses"], w["key"]))
    for idx, w in enumerate(witnesses):
        w["rank"] = idx
    ranked, seen = [], set()
    for w in witnesses:  # first witness of each meaning is its best
        if w["meaning"] not in seen:
            seen.add(w["meaning"])
            ranked.append({"meaning": w["meaning"], "best_witness_rank": w["rank"]})
    readings = sorted(seen, key=lambda s: s.encode("ascii"))
    min_cost = witnesses[0]["cost"]
    if len(readings) == 1:
        status, decision, diag = "complete", "accepted", ""
    elif len(readings) == 2:
        status, decision, diag = "complete", "ambiguous", ""
    else:
        status, decision = "error", "abstain"
        diag = "contract discrepancy: %d distinct meanings (set preserved)" % len(readings)
    return _result(toks, status, decision, diag, readings, witnesses, ranked, min_cost)


def target_bytes(readings):
    """Contract normal form item 4: compact JSON bytes of the canonical set."""
    return json.dumps(readings, ensure_ascii=True, separators=(",", ":")).encode("ascii")


if __name__ == "__main__":
    for s in sys.argv[1:]:
        print(json.dumps(enumerate_all(s), indent=1))
