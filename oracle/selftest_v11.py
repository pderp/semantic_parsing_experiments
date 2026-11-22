#!/usr/bin/env python3
"""Self-test for seed-1.1 (oracle_v11.py, cases_witness_v11.json).  Stdlib only.

A  inventory: v1.1 entries = v1 entries + det.an; next_nouns equals the rule I
   derive from the ontology's existential_surface; 57 surface tokens
B  the two seed-1.1 implementations agree on the full bundle (enumerator with the
   rule from the ontology vs witness analyser with the rule from next_nouns)
C  backward compatibility: for a seed-1.0 sentence, correcting each "a" before a
   vowel-initial noun to "an" gives, under seed-1.1, exactly the seed-1.0 result
   (statuses, readings, costs, keys up to det.a -> det.an); leaving a wrong
   article in gives no_root
D  frozen seed-1.1 case file: reproduced byte for byte; every witness replays
E  the 181 frozen seed-1.0 cases re-run under seed-1.1: list every change
"""
import itertools
import json
import random
import sys

import oracle
import oracle_witness as W
import oracle_v11 as X
import gen_cases_v11 as G

ONT0, BUNDLE0 = W.load_ontology(), W.load_bundle()
ONT, BUNDLE = X.load_ontology(), X.load_bundle()
FULL0 = W.make_grammar(None, BUNDLE0)
FULL = X.make_grammar(None, BUNDLE)
LEX = oracle.Lexicon(ONT)
VOWEL_NOUNS = sorted(n for n in ONT["nouns"] if n[0] in "aeiou")
checks = 0


def ok(cond, msg):
    global checks
    checks += 1
    if not cond:
        raise AssertionError(msg)


def tup(key):
    return tuple(tup(x) if isinstance(x, list) else x for x in key)


# ------------------------------------------------------------------ A
def test_inventory():
    e0, e1 = BUNDLE0["entries"], BUNDLE["entries"]
    ok(set(e1) - set(e0) == {"det.an"} and set(e0) <= set(e1), "only det.an is new")
    ok(all(e1[k] == e0[k] for k in e0), "old entries unchanged")
    ok(e1["det.an"] == {"category": "(NP[existential]/N)", "cost": 0, "recipe": "det", "tokens": ["an"]},
       "det.an as described in witness-v1")
    ok(e1["det.an"] == dict(e1["det.a"], tokens=["an"]), "det.an mirrors det.a")
    mine = {"det.a": sorted(n for n in ONT["nouns"] if X.article_for(ONT, n) == "a"),
            "det.an": sorted(n for n in ONT["nouns"] if X.article_for(ONT, n) == "an")}
    ok(BUNDLE["next_nouns"] == mine, ("next_nouns vs my rule", BUNDLE["next_nouns"], mine))
    ok(mine["det.an"] == VOWEL_NOUNS and len(VOWEL_NOUNS) == 6, "six vowel-initial nouns")
    ok(len(LEX.surface) == 57 == len({t for e in e1.values() for t in e["tokens"]}), "57 surface tokens")
    ok({k: v for k, v in ONT.items() if k not in ("version", "existential_surface", "determiners")} ==
       {k: v for k, v in ONT0.items() if k not in ("version", "determiners")}, "ontology otherwise unchanged")
    ok(ONT["determiners"] == dict(ONT0["determiners"], an="existential"), "determiners")
    for k in ("depth", "roots", "rules", "max_tokens"):
        ok(BUNDLE[k] == BUNDLE0[k], k)
    import hashlib
    ok(hashlib.sha256((X.INBOX / "ontology.yaml").read_bytes()).hexdigest() == BUNDLE["ontology_sha256"],
       "ontology digest recorded in the bundle")


# ------------------------------------------------------------------ invariants
def invariants(r, grammar, label):
    ws = r["witnesses"]
    code = r["diagnostic"]["code"]
    status = (r["construction_status"], r["decision"])
    if not ws:
        ok(code != "" and r["readings"] == [] and r["ranked_readings"] == [] and r["min_cost"] is None, label)
        want = {"empty_input": "no_parse", "invalid_token": "no_parse", "unknown_token": "no_parse",
                "no_root": "no_parse", "edge_budget": "truncated", "invalid_request": "error"}[code]
        ok(status == (want, "abstain"), (label, status, code))
        return
    prev = None
    for w in ws:
        key = json.loads(json.dumps(w["key"]))
        cat, reading, cost, ow = X.replay(key, grammar, ONT, r["tokens"])
        ok((reading, cost, ow) == (w["reading"], w["cost"], w["object_wide_uses"]), ("replay", label))
        rank = (w["cost"], w["object_wide_uses"], tup(key))
        ok(prev is None or prev < rank, ("strict order", label))
        prev = rank
    meanings = {w["reading"] for w in ws}
    ok(r["readings"] == sorted(meanings, key=lambda s: s.encode("ascii")), label)
    first = []
    for w in ws:
        if w["reading"] not in first:
            first.append(w["reading"])
    ok(r["ranked_readings"] == first and r["min_cost"] == ws[0]["cost"], label)
    want = {1: ("complete", "accepted", ""), 2: ("complete", "ambiguous", "")}.get(len(meanings))
    ok(status + (code,) == want, (label, status, code))


# ------------------------------------------------------------------ B
def agree(sentence):
    r = X.analyse(sentence, FULL, ONT)
    v = X.enumerate_all(sentence, ONT, LEX)
    label = ("enumerator vs analyser", sentence)
    ok(r["tokens"] == v["tokens"], label)
    ok((r["construction_status"], r["decision"], r["readings"]) ==
       (v["construction_status"], v["decision"], v["readings"]), label)
    ok(sorted((w["cost"], w["object_wide_uses"], w["reading"]) for w in r["witnesses"]) ==
       sorted((w["cost"], w["object_wide_uses"], w["meaning"]) for w in v["witnesses"]), label)
    ok(r["ranked_readings"] == [m["meaning"] for m in v["ranked_meanings"]], label)
    for w in v["witnesses"]:
        ok(X.enum_replay(json.loads(json.dumps(w["tree"])), len(v["tokens"]), ONT, LEX) == w["meaning"], label)
    invariants(r, FULL, sentence)
    return r


def random_tokens(rng, article):
    """A random sentence of the contract grammar; article(noun) picks the existential form."""
    names, nouns = sorted(ONT["names"]), sorted(ONT["nouns"])
    frames = list(ONT["frames"].values())

    def np():
        if rng.random() < 0.3:
            return [rng.choice(names)]
        noun = rng.choice(nouns)
        return ["every", noun] if rng.random() < 0.4 else [article(noun), noun]

    def simple(m):
        fr = rng.choice([f for f in frames if f["construction"] in ("intransitive", "transitive")])
        out = [fr[m]] + (np() if fr["construction"] == "transitive" else [])
        return out + (["quickly"] if rng.random() < 0.4 else [])

    def vp(m):
        if rng.random() < 0.35:
            fr = rng.choice([f for f in frames if f["construction"].endswith("control")])
            return [fr[m]] + np() + ["to"] + simple("bare")
        return simple(m)

    root = rng.random()
    if root < 0.4:
        return np() + vp("past")
    if root < 0.7:
        return np() + ["did", "not"] + vp("bare")
    return ["not", "every", rng.choice(nouns)] + vp("past")


def test_agreement():
    n = 0
    vocab = ["alice", "a", "an", "every", "paper", "editor", "left", "leave", "reviewed", "review",
             "promised", "did", "not", "to", "quickly"]
    for length in range(1, 5):
        for seq in itertools.product(vocab, repeat=length):
            agree(" ".join(seq))
            n += 1
    rng = random.Random(2026112211)
    surface = sorted(LEX.surface)
    right = lambda noun: X.article_for(ONT, noun)
    anyart = lambda noun: rng.choice(["a", "an"])
    admitted = 0
    for i in range(3000):
        toks = random_tokens(rng, right if i % 2 == 0 else anyart)
        if rng.random() < 0.2:
            toks[rng.randrange(len(toks))] = rng.choice(surface)
        elif rng.random() < 0.1 and len(toks) > 1:
            del toks[rng.randrange(len(toks))]
        admitted += bool(agree(" ".join(toks))["witnesses"])
        n += 1
    return n, admitted


# ------------------------------------------------------------------ C
def demote(key):
    """Map a seed-1.1 key onto seed-1.0 naming: det.an -> det.a."""
    if key[0] == 0:
        return [0, key[1], key[2], "det.a" if key[3] == "det.an" else key[3], key[4]]
    return key[:6] + [[demote(key[6][0]), demote(key[6][1])]]


def test_backward():
    rng = random.Random(2026112212)
    n = changed = 0
    for _ in range(3000):
        toks = random_tokens(rng, lambda noun: "a")          # seed-1.0 spelling
        if rng.random() < 0.15:
            toks[rng.randrange(len(toks))] = rng.choice(sorted(LEX.surface - {"an"}))
        old = W.analyse(" ".join(toks), FULL0, ONT0)
        fixed = [("an" if t == "a" and i + 1 < len(toks) and toks[i + 1] in VOWEL_NOUNS else t)
                 for i, t in enumerate(toks)]
        new = X.analyse(" ".join(fixed), FULL, ONT)
        ok((old["construction_status"], old["decision"], old["diagnostic"], old["readings"],
            old["ranked_readings"], old["min_cost"]) ==
           (new["construction_status"], new["decision"], new["diagnostic"], new["readings"],
            new["ranked_readings"], new["min_cost"]), ("backward", toks))
        ok([(w["cost"], w["object_wide_uses"], w["reading"], w["key"]) for w in old["witnesses"]] ==
           [(w["cost"], w["object_wide_uses"], w["reading"], demote(w["key"])) for w in new["witnesses"]],
           ("backward keys", toks))
        n += 1
        if fixed != toks:
            changed += 1
            same = X.analyse(" ".join(toks), FULL, ONT)
            ok(same["diagnostic"]["code"] == "no_root" and same["witnesses"] == [], ("wrong article", toks))
    return n, changed


# ------------------------------------------------------------------ D
def test_cases_file():
    doc = G.build()
    text = G.dumps(doc)
    path = X.HERE / "cases_witness_v11.json"
    frozen = path.exists()
    if frozen:
        ok(path.read_text() == text, "cases_witness_v11.json is reproduced byte for byte")
    cases = doc["cases"]
    ok(len(cases) >= 30, "at least 30 cases")
    ok(len({(c["grammar"], json.dumps(c["input"]), json.dumps(c.get("max_edges", "-"))) for c in cases})
       == len(cases), "cases are distinct")
    grammars = {name: X.make_grammar(spec, BUNDLE) for name, spec in doc["grammars"].items()}
    for c in cases:
        invariants(c["expected"], grammars[c["grammar"]], c["id"])
        if "edge_count" in c and "max_edges" in c:
            ok((c["expected"]["diagnostic"]["code"] == "edge_budget") == (c["edge_count"] > c["max_edges"]), c["id"])
        if c["grammar"] == "full" and isinstance(c["input"], str) and "max_edges" not in c:
            agree(c["input"])
    return len(cases), frozen


# ------------------------------------------------------------------ E
def a_before_vowel_noun(tokens):
    return any(t == "a" and i + 1 < len(tokens) and tokens[i + 1] in VOWEL_NOUNS
               for i, t in enumerate(tokens))


def test_v1_cases():
    doc = json.loads((X.HERE / "cases_witness_v1.json").read_text())
    grammars = {name: X.make_grammar(spec, BUNDLE) for name, spec in doc["grammars"].items()}
    out_changed, edge_changed = [], []
    for c in doc["cases"]:
        g = grammars[c["grammar"]]
        kwargs = {"max_edges": c["max_edges"]} if "max_edges" in c else {}
        new = X.analyse(c["input"], g, ONT, **kwargs)
        for w in new["witnesses"]:
            del w["rank"]
        toks = c["expected"]["tokens"]
        if new != c["expected"]:
            out_changed.append((c["id"], c["grammar"], c["input"], c["expected"]["diagnostic"]["code"]
                                or c["expected"]["decision"], new["diagnostic"]["code"] or new["decision"]))
            ok(a_before_vowel_noun(toks), ("output changed without 'a' before a vowel-initial noun", c["id"]))
        else:
            ok(True, c["id"])
        if "edge_count" in c:
            ec = X.count_edges(g, toks)
            if ec != c["edge_count"]:
                edge_changed.append((c["id"], c["grammar"], c["input"], c["edge_count"], ec))
    involve = [c["id"] for c in doc["cases"] if a_before_vowel_noun(c["expected"]["tokens"])]
    return len(doc["cases"]), out_changed, edge_changed, involve


def main():
    test_inventory()
    print("A inventory: v1.1 = v1 + det.an; next_nouns equals my rule; 57 surface tokens")
    n, admitted = test_agreement()
    print("B enumerator vs witness analyser under seed-1.1: %d inputs agree (%d of 3000 generated admitted)"
          % (n, admitted))
    n, changed = test_backward()
    print("C backward compatibility: %d seed-1.0 sentences, %d needed an article correction" % (n, changed))
    ncases, frozen = test_cases_file()
    print("D seed-1.1 cases: %d; frozen file %s"
          % (ncases, "reproduced byte for byte" if frozen else "NOT WRITTEN YET"))
    total, out_changed, edge_changed, involve = test_v1_cases()
    print("E seed-1.0 cases under seed-1.1: %d cases, %d expected outputs changed, %d edge counts changed"
          % (total, len(out_changed), len(edge_changed)))
    print("  cases with 'a' before a vowel-initial noun:", involve)
    for row in out_changed:
        print("  OUTPUT  %s [%s] %r: %s -> %s" % row)
    for row in edge_changed:
        print("  EDGES   %s [%s] %r: %d -> %d" % row)
    print("checks passed: %d" % checks)
    print("SELFTEST OK")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as exc:
        print("SELFTEST FAILED:", exc)
        sys.exit(1)
