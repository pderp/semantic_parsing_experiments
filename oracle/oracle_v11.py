#!/usr/bin/env python3
"""ClaudeOracle seed-1.1 support (inbox_v3).  Every v1 and v2 file is unchanged;
this module imports them and adds the article rule in two independent places.

  enumerate_all(sentence)   production-driven enumerator (oracle_enum.py lineage, my own IDs).
                            Article rule taken from the ONTOLOGY (existential_surface):
                            "an" exactly when the following noun starts with a, e, i, o or u.
  analyse(sentence, ...)    witness analyser (oracle_witness.py lineage, published IDs).
                            Article rule taken from the INVENTORY (next_nouns), checked when
                            a det.a / det.an lexical edge is anchored, before budget counting.

The self-test checks that the two sources of the rule agree.  Python 3.14 stdlib only.
"""
import json
import sys
from pathlib import Path

import oracle
import oracle_enum as V1
import oracle_witness as W
from oracle import TOP

HERE = Path(__file__).resolve().parent
INBOX = HERE / "inbox_v3"


def load_ontology(path=None):
    return json.loads(Path(path or INBOX / "ontology.yaml").read_text("utf-8"))


def load_bundle(path=None):
    return json.loads(Path(path or INBOX / "bundle_inventory_no_meanings.json").read_text("utf-8"))


# ================================================================ enumerator (own IDs)

def article_for(ont, noun):
    """Existential article required before this noun token (contract seed-1.1)."""
    es = ont["existential_surface"]
    return es["before_vowel"] if noun[0] in es["vowel_initial_letters"] else es["otherwise"]


class Enumerator(V1.Enumerator):
    # NP ::= Name | Det N, with the existential article agreeing with the noun
    def np(self, i, j):
        out = list(self.name(i, j))
        for k in range(i + 1, j):
            for d, kind in self.det(i, k):
                for n, pred in self.noun(k, j):
                    if kind == "existential" and self.toks[i] != article_for(self.lex.ont, self.toks[k]):
                        continue
                    out.append((V1.FA(d, n), ("det", kind, pred)))
        return out


def check_articles(lex, node):
    """Article rule on a witness tree (used by replay)."""
    if node["t"] == "lex":
        return
    l, r = node["children"]
    if l["t"] == "lex" and l["entry"].startswith("det:"):
        det, noun = l["entry"][4:], r["entry"].partition(":")[2]
        assert r["t"] == "lex" and r["entry"].startswith("noun:"), node
        if lex.dets[det] == "existential":
            assert det == article_for(lex.ont, noun), ("wrong article", det, noun)
    check_articles(lex, l)
    check_articles(lex, r)


def enum_replay(witness, n_tokens, ont, lex):
    check_articles(lex, witness)
    return V1.replay(witness, n_tokens, ont, lex)


def enumerate_all(sentence, ont=None, lex=None, budget=None):
    """Same contract and output shape as oracle_enum.enumerate_all, for seed-1.1."""
    ont = ont or load_ontology()
    lex = lex or oracle.Lexicon(ont)
    if not isinstance(sentence, str):
        return V1._result([], "error", "abstain", "malformed request: sentence is not a string")
    toks = oracle.tokenize(sentence)
    if not toks:
        return V1._result(toks, "no_parse", "abstain", "lexical failure: empty input")
    for t in toks:  # left to right, spelling before vocabulary (witness-v1 item 14)
        if not oracle.TOKEN_RE.match(t):
            return V1._result(toks, "no_parse", "abstain", "lexical failure: unsupported token %r" % t)
        if t not in lex.surface:
            return V1._result(toks, "no_parse", "abstain", "lexical failure: unknown token %r" % t)
    try:
        roots = Enumerator(lex, toks, budget).root()
    except V1.Truncated:
        return V1._result(toks, "truncated", "abstain", "resource budget exhausted (%d steps)" % budget)
    if not roots:
        return V1._result(toks, "no_parse", "abstain", "no licensed derivation: zero roots")
    witnesses = []
    for node, surf, recipe in roots:
        ids = {wid.rsplit("/", 1)[-1]: f for wid, f in oracle.root_readings(surf)}
        formula = ids[recipe]
        oracle.check_sorts(ont, formula)
        witnesses.append({"cost": V1.cost(node), "object_wide_uses": V1.object_wide_uses(node),
                          "key": V1.key(node), "meaning": oracle.canon(formula), "tree": node})
    witnesses.sort(key=lambda w: (w["cost"], w["object_wide_uses"], w["key"]))
    ranked, seen = [], set()
    for idx, w in enumerate(witnesses):
        w["rank"] = idx
        if w["meaning"] not in seen:
            seen.add(w["meaning"])
            ranked.append({"meaning": w["meaning"], "best_witness_rank": idx})
    readings = sorted(seen, key=lambda s: s.encode("ascii"))
    if len(readings) == 1:
        status, decision, diag = "complete", "accepted", ""
    elif len(readings) == 2:
        status, decision, diag = "complete", "ambiguous", ""
    else:
        status, decision = "error", "abstain"
        diag = "contract discrepancy: %d distinct meanings (set preserved)" % len(readings)
    return V1._result(toks, status, decision, diag, readings, witnesses, ranked, witnesses[0]["cost"])


# ================================================================ witness analyser (published IDs)

def make_grammar(spec=None, bundle=None):
    """As oracle_witness.make_grammar, over the seed-witness-v1.1 bundle.

    Adds grammar["next"]: entry ID -> allowed immediately following tokens, from the
    inventory's next_nouns.  A clone of det.a or det.an inherits its source's list.
    """
    spec = spec or {}
    bundle = bundle or load_bundle()
    g = W.make_grammar(spec, bundle)
    nxt = {eid: list(v) for eid, v in bundle["next_nouns"].items() if eid in g["entries"]}
    for c in spec.get("clones", []):
        if c["clone_of"] in bundle["next_nouns"]:
            nxt[c["id"]] = list(bundle["next_nouns"][c["clone_of"]])
    g["next"] = nxt
    return g


def anchors(grammar, eid, toks, i, j):
    """Does lexical entry eid anchor at toks[i:j]?  Includes the article condition."""
    e = grammar["entries"][eid]
    if e["tokens"] != toks[i:j]:
        return False
    if eid in grammar["next"]:
        return j < len(toks) and toks[j] in grammar["next"][eid]
    return True


class Search(W.Search):
    def derive(self, i, j):
        if (i, j) in self.cache:
            return self.cache[(i, j)]
        out = []
        for eid in sorted(self.g["entries"]):
            if anchors(self.g, eid, self.toks, i, j):
                e = self.g["entries"][eid]
                W.check_cost(e["cost"])
                out.append(((0, i, j, eid, e["recipe"]), e["category"],
                            W.lexical_value(self.ont, e["sem"]), e["cost"],
                            1 if e["recipe"] == "tv.object-wide" else 0))
        for k in range(i + 1, j):
            for lk, lc, lv, lcost, low in self.derive(i, k):
                for rk, rc, rv, rcost, row in self.derive(k, j):
                    for rid in sorted(self.g["rules"]):
                        kind, recipe = self.g["rules"][rid]
                        cat = W.combine(kind, lc, rc)
                        if cat is None:
                            continue
                        value = lv(rv) if kind == "FA" else rv(lv)
                        out.append(((1, rid, i, j, cat, recipe, (lk, rk)), cat, value,
                                    W.check_cost(lcost + rcost), low + row))
        self.cache[(i, j)] = out
        return out


def count_edges(grammar, toks):
    """As oracle_witness.count_edges; an unanchored article contributes no edge."""
    n = len(toks)
    nodes, edges = {}, 0
    for i in range(n):
        for j in range(i + 1, n + 1):
            for eid in grammar["entries"]:
                if anchors(grammar, eid, toks, i, j):
                    edges += 1
                    nodes.setdefault((i, j), set()).add(grammar["entries"][eid]["category"])
    for width in range(2, n + 1):
        for i in range(0, n - width + 1):
            j = i + width
            new = set()
            for k in range(i + 1, j):
                for lc in nodes.get((i, k), ()):
                    for rc in nodes.get((k, j), ()):
                        for kind, _ in grammar["rules"].values():
                            cat = W.combine(kind, lc, rc)
                            if cat is not None:
                                edges += 1
                                new.add(cat)
            if new:
                nodes.setdefault((i, j), set()).update(new)
    return edges


def analyse(sentence, grammar=None, ont=None, max_edges=None):
    """As oracle_witness.analyse, for seed-1.1."""
    grammar = grammar or make_grammar()
    ont = ont or load_ontology()
    R = W._result
    if not isinstance(sentence, str):
        return R([], "error", "abstain", "invalid_request")
    if max_edges is not None and (isinstance(max_edges, bool) or not isinstance(max_edges, int)
                                  or max_edges < 0):
        return R([], "error", "abstain", "invalid_request")
    toks = oracle.tokenize(sentence)
    if not toks:
        return R(toks, "no_parse", "abstain", "empty_input")
    vocab = {t for e in grammar["entries"].values() for t in e["tokens"]}
    for idx, t in enumerate(toks):
        if not oracle.TOKEN_RE.match(t):
            return R(toks, "no_parse", "abstain", "invalid_token", t, idx)
        if t not in vocab:
            return R(toks, "no_parse", "abstain", "unknown_token", t, idx)
    if len(toks) > grammar["max_tokens"]:
        return R(toks, "no_parse", "abstain", "no_root")
    if max_edges is not None and count_edges(grammar, toks) > max_edges:
        return R(toks, "truncated", "abstain", "edge_budget")
    try:
        spans = Search(grammar, ont, toks).derive(0, len(toks))
    except W.Overflow:
        return R(toks, "error", "abstain", "cost_overflow")
    roots = [d for d in spans if d[1] in grammar["roots"]]
    if not roots:
        return R(toks, "no_parse", "abstain", "no_root")
    witnesses = []
    for key, cat, value, cost, ow in roots:
        formula = value(lambda e: TOP)
        oracle.check_sorts(ont, formula)
        witnesses.append({"cost": cost, "object_wide_uses": ow, "key": key,
                          "reading": oracle.canon(formula)})
    witnesses.sort(key=lambda w: (w["cost"], w["object_wide_uses"], w["key"]))
    ranked = []
    for idx, w in enumerate(witnesses):
        w["rank"] = idx
        w["key"] = W.jsonable(w["key"])
        if w["reading"] not in ranked:
            ranked.append(w["reading"])
    readings = sorted(ranked, key=lambda s: s.encode("ascii"))
    extra = dict(readings=readings, witnesses=witnesses, ranked=ranked, min_cost=witnesses[0]["cost"])
    if len(readings) == 1:
        return R(toks, "complete", "accepted", "", **extra)
    if len(readings) == 2:
        return R(toks, "complete", "ambiguous", "", **extra)
    return R(toks, "error", "abstain", "reading_count", **extra)


def replay(key, grammar, ont, toks):
    """Recompute (category, reading, cost, ow_uses) from a JSON key; re-checks anchoring."""
    def lex_ok(k):
        if k[0] == 0:
            assert anchors(grammar, k[3], toks, k[1], k[2]), ("not anchored", k)
        else:
            lex_ok(k[6][0])
            lex_ok(k[6][1])
    lex_ok(key)
    return W.replay(key, grammar, ont, toks)


if __name__ == "__main__":
    for s in sys.argv[1:]:
        print(json.dumps(analyse(s), indent=1))
