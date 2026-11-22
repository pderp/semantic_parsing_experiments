#!/usr/bin/env python3
"""Self-test for oracle_witness.py and cases_witness_v1.json.  Stdlib only.

A  inventory conflict check: the 178 published entries equal the expansion I
   derive myself from ontology + contract (IDs, recipes, tokens, categories, costs)
B  agreement with my earlier, independently structured enumerator (oracle_enum.py,
   production-driven) on the full bundle: statuses, reading sets and the multiset
   of (cost, object-wide uses, reading) over witnesses
C  invariants on every result: each witness key replays (from JSON) to its
   reading, cost and object-wide count; rank tuples strictly ascending; keys
   unique; reading set = witness readings, byte-sorted; display order by best witness
D  subset invariant: a restricted grammar's witnesses are exactly the full
   grammar's witnesses (same rules/roots/max_tokens) that use only its entries
E  the frozen cases file is reproduced byte for byte by gen_cases_witness.py
"""
import itertools
import json
import random
import sys

import oracle
import oracle_enum as V1
import oracle_witness as W
import selftest_enum as T1
import gen_cases_witness as G

ONT = W.load_ontology()
BUNDLE = W.load_bundle()
FULL = W.make_grammar(None, BUNDLE)
LEX1 = oracle.Lexicon(ONT)
checks = 0


def ok(cond, msg):
    global checks
    checks += 1
    if not cond:
        raise AssertionError(msg)


# ------------------------------------------------------------------ A
def expected_inventory():
    kinds = ["existential", "unit", "universal"]
    inv = {}

    def put(eid, cat, recipe, tokens, cost=0):
        assert eid not in inv
        inv[eid] = {"category": cat, "cost": cost, "recipe": recipe, "tokens": tokens}

    def vp(feat, k):
        return "(S[%s]\\NP[%s])" % (feat, k)

    for n in ONT["names"]:
        put("name." + n, "NP[unit]", "name", [n])
    for n in ONT["nouns"]:
        put("noun." + n, "N", "noun", [n])
    for d, k in ONT["determiners"].items():
        put("det." + d, "(NP[%s]/N)" % k, "det", [d])
    for fid, fr in ONT["frames"].items():
        forms = [("bare", "bare", ["unit"]), ("past", "fin", kinds)]
        for m, f, subj_kinds in forms:
            for sk in subj_kinds:
                if fr["construction"] == "intransitive":
                    put("%s.%s.%s" % (fid, m, sk), vp(f + ",simple,plain", sk), "iv", [fr[m]])
                elif fr["construction"] == "transitive":
                    for okind in kinds:
                        cat = "(%s/NP[%s])" % (vp(f + ",simple,plain", sk), okind)
                        scopes = ["subject-wide"]
                        if "unit" in (sk, okind) or sk != okind:
                            scopes.append("object-wide")
                        for sc in scopes:
                            put("%s.%s.%s.%s.%s" % (fid, m, sk, okind, sc), cat, "tv." + sc, [fr[m]], 10)
                else:
                    for rk in kinds:
                        cat = "((%s/(S[to]\\NP[unit]))/NP[%s])" % (vp(f + ",control", sk), rk)
                        put("%s.%s.%s.%s" % (fid, m, sk, rk), cat, "control", [fr[m]])
    put("quickly.bare.unit", "(%s\\%s)" % (vp("bare,simple,quick", "unit"), vp("bare,simple,plain", "unit")),
        "manner", ["quickly"])
    for k in kinds:
        put("quickly.fin." + k, "(%s\\%s)" % (vp("fin,simple,quick", k), vp("fin,simple,plain", k)),
            "manner", ["quickly"])
    for inner, tag in (("bare,control", "control"), ("bare,simple,plain", "simple.plain"),
                       ("bare,simple,quick", "simple.quick")):
        for k in kinds:
            put("did-not.%s.%s" % (tag, k), "(%s/%s)" % (vp("fin,negative", k), vp(inner, "unit")),
                "negation", ["did", "not"])
        if tag != "control":
            put("to." + tag, "((S[to]\\NP[unit])/%s)" % vp(inner, "unit"), "infinitive", ["to"])
    for inner, tag in (("fin,control", "control"), ("fin,simple,plain", "simple.plain"),
                       ("fin,simple,quick", "simple.quick")):
        put("not-every." + tag, "((S[fin,not-every]/%s)/N)" % vp(inner, "universal"),
            "not-every", ["not", "every"])
    return inv


def depth(cat):
    s = W.split_cat(cat)
    return 0 if s is None else 1 + max(depth(s[0]), depth(s[2]))


def test_inventory():
    mine, pub = expected_inventory(), BUNDLE["entries"]
    ok(set(mine) == set(pub), ("entry ids differ", sorted(set(mine) ^ set(pub))[:10]))
    for eid in pub:
        ok(mine[eid] == pub[eid], ("entry differs", eid, mine[eid], pub[eid]))
    ok(len(pub) == 178, "178 entries")
    ok(all(depth(e["category"]) <= BUNDLE["depth"] for e in pub.values()), "slash depth")
    ok(BUNDLE["rules"] == {"seed.ba": ["BA", "apply"], "seed.fa": ["FA", "apply"]}, "rules")
    surface = {t for e in pub.values() for t in e["tokens"]}
    ok(surface == LEX1.surface, "bundle surface inventory equals the ontology's")
    import hashlib
    ok(hashlib.sha256((W.INBOX / "ontology.yaml").read_bytes()).hexdigest() == BUNDLE["ontology_sha256"],
       "ontology digest recorded in the bundle")


# ------------------------------------------------------------------ C
def invariants(r, grammar, label):
    ws = r["witnesses"]
    code = r["diagnostic"]["code"]
    status = (r["construction_status"], r["decision"])
    if not ws:
        ok(code != "" and r["readings"] == [] and r["ranked_readings"] == [] and r["min_cost"] is None, label)
        want = {"empty_input": "no_parse", "invalid_token": "no_parse", "unknown_token": "no_parse",
                "no_root": "no_parse", "edge_budget": "truncated", "invalid_request": "error",
                "cost_overflow": "error"}[code]
        ok(status == (want, "abstain"), (label, status, code))
        return
    toks = r["tokens"]
    prev = None
    for w in ws:
        key = json.loads(json.dumps(w["key"]))
        cat, reading, cost, ow = W.replay(key, grammar, ONT, toks)
        ok((reading, cost, ow) == (w["reading"], w["cost"], w["object_wide_uses"]), ("replay", label))
        rank = (w["cost"], w["object_wide_uses"], V1_tuple(key))
        if prev is not None:
            ok(prev < rank and not (rank < prev) and prev != rank, ("strict order", label))
        prev = rank
    ok(len({json.dumps(w["key"]) for w in ws}) == len(ws), ("unique keys", label))
    meanings = {w["reading"] for w in ws}
    ok(set(r["readings"]) == meanings and len(r["readings"]) == len(meanings), label)
    ok(r["readings"] == sorted(r["readings"], key=lambda s: s.encode("ascii")), label)
    first = []
    for w in ws:
        if w["reading"] not in first:
            first.append(w["reading"])
    ok(r["ranked_readings"] == first, ("display order", label))
    ok(r["min_cost"] == min(w["cost"] for w in ws) == ws[0]["cost"], label)
    want = {1: ("complete", "accepted", ""), 2: ("complete", "ambiguous", "")}.get(
        len(meanings), ("error", "abstain", "reading_count"))
    ok(status + (code,) == want, (label, status, code))


def V1_tuple(key):
    return tuple(V1_tuple(x) if isinstance(x, list) else x for x in key)


# ------------------------------------------------------------------ B
def agree_with_v1(sentence):
    r = W.analyse(sentence, FULL, ONT)
    v = V1.enumerate_all(sentence, ONT, LEX1)
    label = ("v1 agreement", sentence)
    ok(r["tokens"] == v["tokens"], label)
    ok((r["construction_status"], r["decision"], r["readings"]) ==
       (v["construction_status"], v["decision"], v["readings"]), label)
    ok(sorted((w["cost"], w["object_wide_uses"], w["reading"]) for w in r["witnesses"]) ==
       sorted((w["cost"], w["object_wide_uses"], w["meaning"]) for w in v["witnesses"]), label)
    ok(r["ranked_readings"] == [m["meaning"] for m in v["ranked_meanings"]], label)
    invariants(r, FULL, sentence)
    return r


def random_sentence(rng):
    """A random licensed sentence from the contract grammar (or a mutation of one)."""
    names, nouns = sorted(ONT["names"]), sorted(ONT["nouns"])
    frames = list(ONT["frames"].values())

    def np():
        return [rng.choice(names)] if rng.random() < 0.4 else [rng.choice(["a", "every"]), rng.choice(nouns)]

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
        toks = np() + vp("past")
    elif root < 0.7:
        toks = np() + ["did", "not"] + vp("bare")
    else:
        toks = ["not", "every", rng.choice(nouns)] + vp("past")
    return toks


def test_v1_agreement():
    n = 0
    for s, _, _ in T1.CASES:
        agree_with_v1(s)
        n += 1
    vocab = ["alice", "a", "every", "paper", "editor", "left", "leave", "reviewed", "review",
             "promised", "persuade", "did", "not", "to", "quickly"]
    for length in range(1, 5):
        for seq in itertools.product(vocab, repeat=length):
            agree_with_v1(" ".join(seq))
            n += 1
    rng = random.Random(20261121)
    surface = sorted(LEX1.surface)
    admitted = 0
    for _ in range(3000):
        toks = random_sentence(rng)
        mode = rng.random()
        if mode < 0.25 and len(toks) > 1:      # delete a token
            del toks[rng.randrange(len(toks))]
        elif mode < 0.4:                       # replace a token
            toks[rng.randrange(len(toks))] = rng.choice(surface)
        elif mode < 0.5:                       # insert a token
            toks.insert(rng.randrange(len(toks) + 1), rng.choice(surface))
        elif mode < 0.55:                      # swap neighbours
            i = rng.randrange(len(toks) - 1)
            toks[i], toks[i + 1] = toks[i + 1], toks[i]
        admitted += bool(agree_with_v1(" ".join(toks))["witnesses"])
        n += 1
    for _ in range(1500):
        agree_with_v1(" ".join(rng.choice(surface) for _ in range(rng.randrange(1, 8))))
        n += 1
    return n, admitted


# ------------------------------------------------------------------ D, E
def test_cases_file():
    doc = G.build()
    text = G.dumps(doc)
    path = W.HERE / "cases_witness_v1.json"
    frozen = path.exists()
    if frozen:
        ok(path.read_text() == text, "cases_witness_v1.json is reproduced byte for byte")
    ok(json.loads(text) == doc, "JSON round trip")
    cases = doc["cases"]
    ok(len(cases) >= 100, "at least 100 cases")
    ok(len({(c["grammar"], json.dumps(c["input"]), json.dumps(c.get("max_edges", "-"))) for c in cases})
       == len(cases), "cases are distinct")
    grammars = {name: W.make_grammar(spec, BUNDLE) for name, spec in doc["grammars"].items()}
    subset_checked = 0
    for c in cases:
        g, exp = grammars[c["grammar"]], c["expected"]
        invariants(exp, g, c["id"])
        spec = doc["grammars"][c["grammar"]]
        if "edge_count" in c and "max_edges" in c and isinstance(c["max_edges"], int) \
                and not isinstance(c["max_edges"], bool) and c["max_edges"] >= 0:
            ok((exp["diagnostic"]["code"] == "edge_budget") == (c["edge_count"] > c["max_edges"]), c["id"])
        # D: subset invariant (no clones, no budget, string input that reached the search)
        if "clones" not in spec and "max_edges" not in c and "edge_count" in c:
            sup = W.make_grammar({k: v for k, v in spec.items() if k != "entries"}, BUNDLE)
            full = W.analyse(c["input"], sup, ONT)
            keep = set(g["entries"])

            def uses(key):
                return {key[3]} if key[0] == 0 else uses(key[6][0]) | uses(key[6][1])
            want = [w["key"] for w in full["witnesses"] if uses(w["key"]) <= keep]
            ok(want == [w["key"] for w in exp["witnesses"]], ("subset invariant", c["id"]))
            subset_checked += 1
    # groups of duplicates in case and spacing give identical expected output
    by_tokens = {}
    for c in cases:
        if isinstance(c["input"], str) and "max_edges" not in c:
            by_tokens.setdefault((c["grammar"], tuple(c["expected"]["tokens"])), []).append(c)
    dup_groups = [v for v in by_tokens.values() if len(v) > 1]
    for group in dup_groups:
        for c in group[1:]:
            ok(c["expected"] == group[0]["expected"], ("duplicate", c["id"]))
    # full-bundle cases agree with the frozen v1 fixture answers
    answers = {tuple(a["tokens"]): a for a in json.load(open(W.HERE / "answers_oracle_v1.json"))}
    hit = 0
    for c in cases:
        a = answers.get(tuple(c["expected"]["tokens"]))
        if a and c["grammar"] == "full" and "max_edges" not in c:
            ok((a["construction_status"], a["decision"], a["readings"]) ==
               (c["expected"]["construction_status"], c["expected"]["decision"], c["expected"]["readings"]),
               ("fixture", c["id"]))
            hit += 1
    ok(hit >= 12, "all 12 fixtures present")
    codes = {c["expected"]["diagnostic"]["code"] for c in cases}
    ok(codes == {"", "empty_input", "invalid_token", "unknown_token", "no_root", "invalid_request",
                 "cost_overflow", "edge_budget", "reading_count"}, ("codes covered", codes))
    return len(cases), subset_checked, len(dup_groups), frozen


def main():
    test_inventory()
    print("A inventory: 178 published entries equal my own expansion")
    n, admitted = test_v1_agreement()
    print("B/C agreement with oracle_enum.py on the full bundle: %d inputs (%d of 3000 generated sentences admitted)"
          % (n, admitted))
    ncases, nsub, ndup, frozen = test_cases_file()
    print("D/E cases: %d (%d subset-invariant checks, %d duplicate groups); frozen file %s"
          % (ncases, nsub, ndup, "reproduced byte for byte" if frozen else "NOT WRITTEN YET"))
    print("checks passed: %d" % checks)
    print("SELFTEST OK")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as exc:
        print("SELFTEST FAILED:", exc)
        sys.exit(1)
