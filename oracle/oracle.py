#!/usr/bin/env python3
"""ClaudeOracle: independent reference for the M01 public contract (seed-0.2-draft).

Written from inbox_v1/contract.md and inbox_v1/ontology.yaml only.
Python 3.14 standard library only.

analyse(sentence, ontology) -> dict with tokens, construction_status,
decision, readings (sorted canonical strings), diagnostic, witnesses.
"""
import itertools
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASCII_WS = " \t\n\r\f\v"
TOKEN_RE = re.compile(r"[a-z]+\Z")
SPLIT_RE = re.compile(r"[ \t\n\r\f\v]+")
UPPER = {c: c + 32 for c in range(ord("A"), ord("Z") + 1)}


def load_ontology(path=None):
    path = Path(path) if path else HERE / "inbox_v1" / "ontology.yaml"
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- tokenizer

def tokenize(sentence):
    """Contract section 'Inputs': strip, drop one final period, rstrip, fold, split."""
    s = sentence.strip(ASCII_WS)
    if s.endswith("."):
        s = s[:-1]
    s = s.rstrip(ASCII_WS)
    s = s.translate(UPPER)  # ASCII-only case folding
    if s == "":
        return []
    return SPLIT_RE.split(s)


# ---------------------------------------------------------------- lexicon

class Lexicon:
    def __init__(self, ont):
        self.ont = ont
        self.names = set(ont["names"])
        self.nouns = dict(ont["nouns"])
        self.dets = dict(ont["determiners"])
        self.verbs = {"past": {}, "bare": {}}  # surface -> frame
        for fid, fr in ont["frames"].items():
            fr = dict(fr, id=fid)
            self.verbs["past"][fr["past"]] = fr
            self.verbs["bare"][fr["bare"]] = fr
        self.surface = (self.names | set(self.nouns) | set(self.dets)
                        | set(ont["operators"]) | set(ont["modifiers"])
                        | set(self.verbs["past"]) | set(self.verbs["bare"]))


# ---------------------------------------------------------------- surface parse
# Finite grammar; every production consumes its entire span.
#   Root      ::= NP VP[past] | NP "did" "not" VP[bare] | "not" "every" N VP[past]
#   NP        ::= Name | Det N
#   VP[m]     ::= Simple[m] | Control[m] NP "to" Simple[bare]
#   Simple[m] ::= Intransitive[m] ["quickly"] | Transitive[m] NP ["quickly"]

def parse_np(lex, toks, i):
    """Yield (np, next_index). np = ('name', n) | ('det', kind, noun_pred)."""
    if i < len(toks) and toks[i] in lex.names:
        yield ("name", toks[i]), i + 1
    if i + 1 < len(toks) and toks[i] in lex.dets and toks[i + 1] in lex.nouns:
        yield ("det", lex.dets[toks[i]], lex.nouns[toks[i + 1]]), i + 2


def parse_simple(lex, toks, i, m):
    """Yield simple VPs spanning toks[i:] exactly."""
    if i >= len(toks):
        return
    fr = lex.verbs[m].get(toks[i])
    if fr is None:
        return
    if fr["construction"] == "intransitive":
        rest = toks[i + 1:]
        if rest == []:
            yield {"kind": "simple", "frame": fr, "obj": None, "quick": False}
        elif rest == ["quickly"]:
            yield {"kind": "simple", "frame": fr, "obj": None, "quick": True}
    elif fr["construction"] == "transitive":
        for obj, j in parse_np(lex, toks, i + 1):
            rest = toks[j:]
            if rest == []:
                yield {"kind": "simple", "frame": fr, "obj": obj, "quick": False}
            elif rest == ["quickly"]:
                yield {"kind": "simple", "frame": fr, "obj": obj, "quick": True}


def parse_vp(lex, toks, i, m):
    yield from parse_simple(lex, toks, i, m)
    if i < len(toks):
        fr = lex.verbs[m].get(toks[i])
        if fr is not None and fr["construction"] in ("subject-control", "object-control"):
            for rec, j in parse_np(lex, toks, i + 1):
                if j < len(toks) and toks[j] == "to":
                    for emb in parse_simple(lex, toks, j + 1, "bare"):
                        yield {"kind": "control", "frame": fr, "rec": rec, "emb": emb}


def parse_root(lex, toks):
    """Yield surface trees: {'root': ordinary|vpneg|notevery, 'subj', 'vp'}."""
    for subj, i in parse_np(lex, toks, 0):
        for vp in parse_vp(lex, toks, i, "past"):
            yield {"root": "ordinary", "subj": subj, "vp": vp}
        if toks[i:i + 2] == ["did", "not"]:
            for vp in parse_vp(lex, toks, i + 2, "bare"):
                yield {"root": "vpneg", "subj": subj, "vp": vp}
    if toks[:2] == ["not", "every"] and len(toks) > 2 and toks[2] in lex.nouns:
        subj = ("det", "universal", lex.nouns[toks[2]])
        for vp in parse_vp(lex, toks, 3, "past"):
            yield {"root": "notevery", "subj": subj, "vp": vp}


# ---------------------------------------------------------------- semantics
# Formulas are built with named bound variables, then printed with de Bruijn
# indices.  Term forms:
#   ('v', n)                       bound variable
#   'alice'                        constant
#   ('Top',)
#   ('And', a, b) ('Implies', a, b) ('Not', a) ('Box', a)
#   ('ForallE'|'ExistsE'|'ExistsV', ('v', n), body)
#   ('atom', Pred, arg...)

_fresh = itertools.count()


def fresh():
    return ("v", next(_fresh))


TOP = ("Top",)


def And(*xs):
    out = xs[-1]
    for x in reversed(xs[:-1]):
        out = ("And", x, out)
    return out


def atom(pred, *args):
    return ("atom", pred) + args


# An argument is (kind, Q) with kind in unit|universal|existential and
# Q : (entity -> formula) -> formula.

def unit(entity):
    return ("unit", lambda k: k(entity))


def np_arg(np):
    if np[0] == "name":
        return unit(np[1])
    _, kind, pred = np
    if kind == "universal":
        def q(k):
            x = fresh()
            return ("ForallE", x, ("Implies", atom(pred, x), k(x)))
    else:
        def q(k):
            x = fresh()
            return ("ExistsE", x, And(atom(pred, x), k(x)))
    return (kind, q)


def simple_readings(vp, subj, k):
    """Readings of a simple VP applied to subject argument with event continuation k.

    Yields (recipe_id, formula).  k : event -> formula.
    """
    fr = vp["frame"]
    pred = fr["predicate"]
    if vp["quick"]:
        k0 = k
        k = lambda e: And(atom("Quick", e), k0(e))
    skind, sq = subj
    if vp["obj"] is None:
        def body(s):
            e = fresh()
            return ("ExistsV", e, And(atom(pred, e), atom("Agent", e, s), k(e)))
        yield "default", sq(body)
        return
    okind, oq = np_arg(vp["obj"])

    def body(s, o):
        e = fresh()
        return ("ExistsV", e, And(atom(pred, e), atom("Agent", e, s),
                                  atom("Theme", e, o), k(e)))
    yield "subject-wide", sq(lambda s: oq(lambda o: body(s, o)))
    both = "unit" in (skind, okind) or skind != okind
    if both:
        yield "object-wide", oq(lambda o: sq(lambda s: body(s, o)))


def vp_readings(vp, subj, k):
    """Readings of any VP applied to a subject argument; k is the matrix event continuation."""
    if vp["kind"] == "simple":
        yield from simple_readings(vp, subj, k)
        return
    fr = vp["frame"]
    pred = fr["predicate"]
    _, sq = subj
    _, rq = np_arg(vp["rec"])
    emb = vp["emb"]
    # enumerate embedded recipes first so each matrix formula is built fresh
    emb_ids = [rid for rid, _ in simple_readings(emb, unit("x"), lambda e: TOP)]
    for idx, rid in enumerate(emb_ids):
        def matrix(s, r, idx=idx):
            controller = s if fr["controller"] == "subject" else r
            inner = list(simple_readings(emb, unit(controller), lambda e: TOP))[idx][1]
            e = fresh()
            return ("ExistsV", e, And(atom(pred, e), atom("Agent", e, s),
                                      atom("Recipient", e, r),
                                      atom("Content", e, ("Box", inner)), k(e)))
        yield "control/" + rid, sq(lambda s: rq(lambda r: matrix(s, r)))


def past(k):
    return lambda e: And(atom("Past", e), k(e))


def root_readings(tree):
    """Yield (witness_id, closed formula) for each licensed derivation."""
    close = lambda e: TOP
    vp = tree["vp"]
    if tree["root"] == "ordinary":
        for rid, f in vp_readings(vp, np_arg(tree["subj"]), past(close)):
            yield "ordinary/" + rid, f
    elif tree["root"] == "notevery":
        for rid, f in vp_readings(vp, np_arg(tree["subj"]), past(close)):
            yield "notevery/" + rid, ("Not", f)
    else:  # vpneg: subject Q applied once to  \s. not VP(Unit(s))(past . close)
        _, sq = np_arg(tree["subj"])
        ids = [rid for rid, _ in vp_readings(vp, unit("x"), past(close))]
        for idx, rid in enumerate(ids):
            def inner(s, idx=idx):
                return ("Not", list(vp_readings(vp, unit(s), past(close)))[idx][1])
            yield "vpneg/" + rid, sq(inner)


# ---------------------------------------------------------------- normal form

def canon(t, env=()):
    """Canonical ASCII text (contract 'Normal form' steps 1-3). env: innermost first."""
    if isinstance(t, str):
        return t
    tag = t[0]
    if tag == "v":
        return "#%d" % env.index(t)
    if tag == "Top":
        return "Top"
    if tag == "And":
        leaves, stack = [], [t]
        while stack:
            x = stack.pop()
            if not isinstance(x, str) and x[0] == "And":
                stack.append(x[2])
                stack.append(x[1])
            else:
                leaves.append(x)
        parts = [canon(x, env) for x in leaves]
        parts = [p for p in parts if p != "Top"]
        parts.sort(key=lambda p: p.encode("ascii"))
        if not parts:
            return "Top"
        out = parts[-1]
        for p in reversed(parts[:-1]):
            out = "(And %s %s)" % (p, out)
        return out
    if tag == "Implies":
        return "(Implies %s %s)" % (canon(t[1], env), canon(t[2], env))
    if tag in ("Not", "Box"):
        return "(%s %s)" % (tag, canon(t[1], env))
    if tag in ("ForallE", "ExistsE", "ExistsV"):
        sort = tag[-1]
        return "(%s (lam %s %s))" % (tag, sort, canon(t[2], (t[1],) + env))
    if tag == "atom":
        return "(%s)" % " ".join([t[1]] + [canon(a, env) for a in t[2:]])
    raise ValueError("unknown term %r" % (t,))


def check_sorts(ont, t, env=()):
    """Light type check: predicate argument sorts and arity against the ontology."""
    if isinstance(t, str) or t[0] in ("v", "Top"):
        return
    tag = t[0]
    if tag == "atom":
        sig = ont["predicates"][t[1]]
        assert len(sig) == len(t) - 2, t
        sorts = dict(env)
        for want, a in zip(sig, t[2:]):
            if want == "I":
                assert a[0] == "Box", t
                check_sorts(ont, a, env)
            elif isinstance(a, str):
                assert ont["names"][a] == want, t
            else:
                assert sorts[a] == want, t
    elif tag in ("ForallE", "ExistsE", "ExistsV"):
        check_sorts(ont, t[2], ((t[1], tag[-1]),) + env)
    else:
        for c in t[1:]:
            check_sorts(ont, c, env)


# ---------------------------------------------------------------- driver

def result(tokens, status, decision, readings=(), diagnostic="", witnesses=()):
    return {"tokens": list(tokens), "construction_status": status,
            "decision": decision, "readings": list(readings),
            "diagnostic": diagnostic, "witnesses": list(witnesses)}


def analyse(sentence, ont=None, lex=None):
    ont = ont or load_ontology()
    lex = lex or Lexicon(ont)
    if not isinstance(sentence, str):
        return result([], "error", "abstain", diagnostic="malformed request: sentence is not a string")
    toks = tokenize(sentence)
    if not toks:
        return result(toks, "no_parse", "abstain", diagnostic="lexical failure: empty input")
    bad = [t for t in toks if not TOKEN_RE.match(t)]
    if bad:
        return result(toks, "no_parse", "abstain",
                      diagnostic="lexical failure: unsupported token %r" % bad[0])
    unknown = [t for t in toks if t not in lex.surface]
    if unknown:
        return result(toks, "no_parse", "abstain",
                      diagnostic="lexical failure: unknown token %r" % unknown[0])
    meanings = {}
    for tree in parse_root(lex, toks):
        for wid, f in root_readings(tree):
            check_sorts(ont, f)
            meanings.setdefault(canon(f), []).append(wid)
    if not meanings:
        return result(toks, "no_parse", "abstain",
                      diagnostic="no licensed derivation: zero roots")
    readings = sorted(meanings, key=lambda s: s.encode("ascii"))
    wit = [{"reading": r, "witnesses": meanings[r]} for r in readings]
    if len(readings) == 1:
        return result(toks, "complete", "accepted", readings, witnesses=wit)
    if len(readings) == 2:
        return result(toks, "complete", "ambiguous", readings, witnesses=wit)
    return result(toks, "error", "abstain", readings,
                  "contract discrepancy: %d readings" % len(readings), wit)


if __name__ == "__main__":
    for s in sys.argv[1:]:
        print(json.dumps(analyse(s), indent=1))
