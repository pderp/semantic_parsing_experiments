#!/usr/bin/env python3
"""Generate cases_witness_r2.json: extra seed-1.1 cases for the witness-v1 revision 2
rules that my earlier frozen files do not exercise.  ClaudeOracle, stdlib only.

    python3 gen_cases_r2.py            # print to stdout
    python3 gen_cases_r2.py --write    # write cases_witness_r2.json (refuses to overwrite)
    python3 gen_cases_r2.py --check    # self-test: invariants + byte-for-byte reproduction

Rules covered (witness-v1.md revision 2, inbox_v4):
  item 1  edge counts at many more thresholds (cap = count completes, count - 1 truncates)
  item 2  precedence: a truncated chart yields no cost result
  item 4  budget type: null = exact mode; 5.0 and other floats invalid
  item 7  overflow scope: subtree overflow that an ancestor would cancel; overflow in a
          combination outside any root; one overflowing witness invalidates safe ones
  item 8  full signed 64-bit range legal, bounds inclusive; out-of-range lexical cost is
          rejected when the bundle is built
  item 13 empty roots list
  item 15 restriction format: empty entries / rules lists, max_tokens 0, malformed specs

Earlier files are unchanged; this module only adds validate_spec() on top of oracle_v11.
"""
import hashlib
import json
import re
import sys

import oracle_witness as W
import oracle_v11 as X

BUNDLE = X.load_bundle()
ONT = X.load_ontology()
PUB = BUNDLE["entries"]
I64MAX, I64MIN = 2 ** 63 - 1, -2 ** 63
P62 = 2 ** 62
WORD = re.compile(r"[a-z]+\Z")


class Rejected(Exception):
    """The restriction spec is not a valid bundle (revision 2 items 8 and 15)."""


def validate_spec(spec):
    """My reading of the constraints revision 2 item 15 places on a restriction."""
    def is_int(x):
        return isinstance(x, int) and not isinstance(x, bool)
    for field, universe in (("entries", PUB), ("rules", BUNDLE["rules"]), ("roots", BUNDLE["roots"])):
        if field in spec:
            vals = spec[field]
            if not isinstance(vals, list) or len(set(vals)) != len(vals) or any(v not in universe for v in vals):
                raise Rejected("%s must be distinct existing values" % field)
    if "max_tokens" in spec:
        m = spec["max_tokens"]
        if not is_int(m) or not (0 <= m <= BUNDLE["max_tokens"]):
            raise Rejected("max_tokens must be an integer from 0 to the base limit")
    seen = set()
    for c in spec.get("clones", []):
        if c.get("clone_of") not in PUB:
            raise Rejected("clone_of must be a published entry")
        cid = c.get("id")
        if not isinstance(cid, str) or not cid.isascii() or cid == "" or cid in PUB or cid in seen:
            raise Rejected("clone id must be a fresh ASCII identifier")
        seen.add(cid)
        if "tokens" in c:
            t = c["tokens"]
            if not isinstance(t, list) or not t or not all(isinstance(x, str) and WORD.match(x) for x in t):
                raise Rejected("tokens must be a nonempty list of lower-case ASCII words")
        if "cost" in c and (not is_int(c["cost"]) or not (I64MIN <= c["cost"] <= I64MAX)):
            raise Rejected("lexical cost outside the signed 64-bit range")


def clone(new_id, of, **kw):
    return dict({"id": new_id, "clone_of": of}, **kw)


SW = "cite.tv.past.unit.unit.subject-wide"


def money(a, c, b, extra=()):
    """alice / cited / bob with the given lexical costs (subject-wide entry only)."""
    return {"entries": [], "clones": [clone("name.alice.c", "name.alice", cost=a),
                                      clone("cite.c", SW, cost=c),
                                      clone("name.bob.c", "name.bob", cost=b)] + list(extra)}


GRAMMARS = {
    "full": {},
    # item 7 / 8: order of summation, subtree overflow, inclusive bounds
    "sub-overflow-cancelled": money(-P62, P62, P62),
    "left-sum-would-overflow": money(P62, P62, -P62),
    "min-exact": money(-P62, -P62, 0),
    "min-minus-one": money(-P62, -P62, -1),
    "max-exact": money(P62, P62 - 1, 0),
    "max-plus-one": money(P62, P62, 0),
    "lexical-bounds": money(I64MAX, 0, I64MIN),
    "negative-sub-underflow-cancelled": money(P62, -P62, -P62 - 1),
    # item 7: overflow in a combination that is in no root; safe witnesses invalidated
    "overflow-outside-root": money(0, 0, P62, [clone("cite.dead", "cite.tv.past.universal.unit.subject-wide",
                                                     cost=P62)]),
    "outside-root-safe": money(0, 0, P62, [clone("cite.dead", "cite.tv.past.universal.unit.subject-wide",
                                                 cost=P62 - 1)]),
    "one-witness-overflows": money(0, 0, P62, [clone("cite.dear", SW, cost=P62)]),
    "one-witness-at-max": money(0, 0, P62, [clone("cite.dear", SW, cost=P62 - 1)]),
    # item 13 / 15: degenerate restrictions
    "no-roots": {"roots": []},
    "no-rules": {"rules": []},
    "no-entries": {"entries": []},
    "max-tokens-0": {"max_tokens": 0},
    "max-tokens-12": {"max_tokens": 12},
    "one-root": {"roots": ["S[fin,control]"]},
    # item 8 / 15: rejected at bundle construction
    "bad-cost-high": money(I64MAX + 1, 0, 0),
    "bad-cost-low": money(0, I64MIN - 1, 0),
    "bad-cost-float": money(0, 10.0, 0),
    "bad-max-tokens": {"max_tokens": 13},
    "bad-max-tokens-negative": {"max_tokens": -1},
    "bad-duplicate-entry": {"entries": ["name.alice", "name.alice", "leave.iv.past.unit"]},
    "bad-unknown-entry": {"entries": ["name.alice", "name.zed"]},
    "bad-unknown-root": {"roots": ["S[fin]"]},
    "bad-unknown-rule": {"rules": ["seed.fc"]},
    "bad-clone-id-published": {"entries": ["leave.iv.past.unit"],
                               "clones": [clone("name.bob", "name.alice")]},
    "bad-clone-id-repeated": {"entries": ["leave.iv.past.unit"],
                              "clones": [clone("x", "name.alice"), clone("x", "name.bob")]},
    "bad-clone-source": {"clones": [clone("x", "name.zed")]},
    "bad-clone-tokens-empty": {"clones": [clone("x", "name.alice", tokens=[])]},
    "bad-clone-tokens-case": {"clones": [clone("x", "name.alice", tokens=["Alice"])]},
}

EDGE = "exact edge count (revision 2 item 1)"
REJ = "a spec violating revision 2 item 8 or 15 is rejected when the bundle is built; no parse result exists"
REJ15 = "revision 2 item 15 states the constraint but not that a violation is rejected"
NOBUDGET = object()
CASES = []


def add(grammar, inp, max_edges=NOBUDGET, dep=(), note=""):
    CASES.append((grammar, inp, max_edges, list(dep), note))


A = "alice cited bob"
add("sub-overflow-cancelled", A, note="(cited bob) = 2^63 overflows; adding alice = -2^62 would bring the total to 2^62")
add("left-sum-would-overflow", A, note="tree order: (cited bob) = 0, total 2^62; a left-to-right token sum would pass 2^63")
add("min-exact", A, note="total is exactly -2^63: legal")
add("min-minus-one", A, note="total -2^63 - 1")
add("max-exact", A, note="total is exactly 2^63 - 1: legal")
add("max-plus-one", A, note="total 2^63")
add("lexical-bounds", A, note="lexical costs at both bounds; (cited bob) = -2^63, total -1")
add("negative-sub-underflow-cancelled", A, note="(cited bob) = -2^63 - 1 underflows; alice = 2^62 would cancel")
add("overflow-outside-root", A, note="cite.dead + bob overflows in a VP for a universal subject, which is in no root")
add("overflow-outside-root", "cited bob", note="rootless input whose only combination overflows")
add("outside-root-safe", A, note="same shape, dead combination at exactly 2^63 - 1: two edges more, result unaffected")
add("one-witness-overflows", A, note="one root witness totals 2^62, the other 2^63: the whole result is invalid")
add("one-witness-at-max", A, note="second witness totals 2^63 - 1: both reported, cheaper first")
# item 2: budget before costs
for g in ("sub-overflow-cancelled", "overflow-outside-root", "one-witness-overflows"):
    n = X.count_edges(X.make_grammar(GRAMMARS[g], BUNDLE), A.split())
    add(g, A, n, [EDGE], "chart completes at the cap, then the overflow is found")
    add(g, A, n - 1, [EDGE], "truncated chart yields no cost result")
    add(g, A, 0, note="budget precedes costs")

# item 4: budget type
S = "an editor cited every article"
add("full", S, None, note="null budget = exact mode")
for bad in (5.0, 0.0, 1e3, -0.0, 2.5, "0", [], {}, [5]):
    add("full", S, bad, note="malformed budget")
add("full", S, 2 ** 63, ["revision 2 item 4 puts no upper bound on an integer budget"],
    "integer budget above 64 bits is still a nonnegative JSON integer")
add("full", 12, None, note="non-string sentence with a null budget")
add("full", "", 5.0, note="budget is validated before tokenizing, so not empty_input")
add("full", "an apple left", "x", note="budget is validated before the lexical scan")

# item 13 / 15: degenerate restrictions
add("no-roots", "alice left", note="no category can finish a witness")
add("no-roots", "alice left", 0, note="edges are still inserted, so the budget is hit")
add("no-roots", "alice the", note="lexical failure is unaffected")
add("no-rules", "alice left", note="lexical edges only")
add("no-rules", "alice", note="NP[unit] is not a root")
add("no-rules", "alice left", 4, [EDGE], "four lexical edges (one name, three verb entries), no binary edge")
add("no-rules", "alice left", 3, [EDGE])
add("no-entries", "alice left", note="empty vocabulary: first token is unknown")
add("no-entries", "", note="empty input is still empty input")
add("no-entries", "al1ce", note="spelling is checked before vocabulary")
add("max-tokens-0", "alice", note="one token exceeds a zero bound")
add("max-tokens-0", "alice", 0, note="length rejection precedes a zero budget")
add("max-tokens-0", "", note="empty input precedes the length bound")
add("max-tokens-0", "zed", note="lexical failure precedes the length bound")
add("max-tokens-12", "every editor did not persuade every analyst to review every thesis quickly")
add("one-root", "alice left", note="S[fin,simple,plain] is derivable but inactive")
add("one-root", "alice promised bob to leave")

# item 8 / 15: rejected bundles
for g, dep in (("bad-cost-high", [REJ]), ("bad-cost-low", [REJ]), ("bad-cost-float", [REJ, REJ15]),
               ("bad-max-tokens", [REJ, REJ15]), ("bad-max-tokens-negative", [REJ, REJ15]),
               ("bad-duplicate-entry", [REJ, REJ15]), ("bad-unknown-entry", [REJ, REJ15]),
               ("bad-unknown-root", [REJ, REJ15]), ("bad-unknown-rule", [REJ, REJ15]),
               ("bad-clone-id-published", [REJ, REJ15]), ("bad-clone-id-repeated", [REJ, REJ15]),
               ("bad-clone-source", [REJ, REJ15]), ("bad-clone-tokens-empty", [REJ, REJ15]),
               ("bad-clone-tokens-case", [REJ, REJ15])):
    add(g, "alice left", dep=dep)

# item 1: edge counts at more thresholds, full seed-1.1 bundle
THRESHOLD = [
    "alice left", "an editor left", "a editor left", "every editor left quickly",
    "bob cited ava", "a student evaluated every thesis", "an author discussed an abstract quickly",
    "dan did not arrive", "an investigator did not cite every dataset quickly",
    "not every reviewer spoke", "not every analyst evaluated a proposal quickly",
    "gia promised an author to leave", "hugo persuaded eva to review an article quickly",
    "every professor did not persuade an investigator to evaluate an abstract quickly",
    "not every editor persuaded an author to discuss a thesis",
    "finn quickly arrived", "alice promised bob to persuade cara to leave",
    "not every researcher did not leave", "to to to", "quickly", "did not", "not every",
]
FULLG = X.make_grammar({}, BUNDLE)
for s in THRESHOLD:
    n = X.count_edges(FULLG, s.split())
    add("full", s, n, [EDGE], "cap equal to my edge count")
    if n > 0:
        add("full", s, n - 1, [EDGE], "one below my edge count")

CONVENTIONS = {
    "base": "Same format as cases_witness_v1.json and cases_witness_v11.json, over bundle "
            "seed-witness-v1.1, read with witness-v1.md revision 2.",
    "grammar_spec": "A restriction as in revision 2 item 15: optional entries, rules, roots, max_tokens, clones.",
    "max_edges": "Absent = no budget passed. JSON null is passed as an explicit null budget.",
    "grammar_rejected": "expected = {\"grammar_rejected\": true} means the restriction itself is invalid and "
                        "must be refused when the bundle is built; no sentence is parsed. Revision 2 gives no "
                        "error name for this, so none is compared.",
    "edge_count": "Edges of the complete chart as in revision 2 item 1. Present whenever lexical and length "
                  "checks pass, including on overflow and rootless inputs.",
    "depends_on": "Where a case rests on something revision 2 does not state outright.",
}


def build():
    cases = []
    built = {}
    for idx, (gname, inp, budget, dep, note) in enumerate(CASES, 1):
        spec = GRAMMARS[gname]
        case = {"id": "R%03d" % idx, "grammar": gname, "input": inp}
        if budget is not NOBUDGET:
            case["max_edges"] = budget
        try:
            validate_spec(spec)
        except Rejected:
            case["expected"] = {"grammar_rejected": True}
        else:
            if gname not in built:
                built[gname] = X.make_grammar(spec, BUNDLE)
            g = built[gname]
            exp = X.analyse(inp, g, ONT, **({} if budget is NOBUDGET else {"max_edges": budget}))
            for w in exp["witnesses"]:
                del w["rank"]
            case["expected"] = exp
            if isinstance(inp, str) and exp["diagnostic"]["code"] in (
                    "", "no_root", "edge_budget", "cost_overflow", "reading_count") \
                    and len(exp["tokens"]) <= g["max_tokens"] and exp["tokens"]:
                case["edge_count"] = X.count_edges(g, exp["tokens"])
        case["depends_on"] = dep
        case["note"] = note
        cases.append(case)
    sha = lambda d, p: hashlib.sha256((X.HERE / d / p).read_bytes()).hexdigest()
    return {"format": "claudeoracle-witness-cases-v1", "bundle": BUNDLE["version"],
            "inventory_sha256": sha("inbox_v3", "bundle_inventory_no_meanings.json"),
            "ontology_sha256": sha("inbox_v3", "ontology.yaml"),
            "witness_contract_sha256": sha("inbox_v4", "witness-v1.md"),
            "conventions": CONVENTIONS, "grammars": GRAMMARS, "cases": cases}, built


def dumps(doc):
    return json.dumps(doc, indent=1, ensure_ascii=True) + "\n"


def check(doc, built):
    n = 0

    def ok(cond, msg):
        nonlocal n
        n += 1
        assert cond, msg
    cases = doc["cases"]
    ok(len({(c["grammar"], json.dumps(c["input"]), json.dumps(c.get("max_edges", "-"))) for c in cases})
       == len(cases), "cases are distinct")
    ok(json.loads(dumps(doc)) == doc, "JSON round trip keeps every integer and float")
    for c in cases:
        exp = c["expected"]
        if exp.get("grammar_rejected"):
            ok(c["grammar"].startswith("bad-"), c["id"])
            continue
        ok(not c["grammar"].startswith("bad-"), c["id"])
        g = built[c["grammar"]]
        prev = None
        for w in exp["witnesses"]:
            cat, reading, cost, ow = X.replay(json.loads(json.dumps(w["key"])), g, ONT, exp["tokens"])
            ok((reading, cost, ow) == (w["reading"], w["cost"], w["object_wide_uses"]), ("replay", c["id"]))
            ok(I64MIN <= cost <= I64MAX, c["id"])
            rank = (cost, ow, json.dumps(w["key"]))
            ok(prev is None or prev[:2] <= rank[:2], ("order", c["id"]))
            prev = rank
        ok(exp["readings"] == sorted({w["reading"] for w in exp["witnesses"]}, key=str.encode), c["id"])
        budget = c.get("max_edges")
        valid_budget = isinstance(budget, int) and not isinstance(budget, bool) and budget >= 0
        if "max_edges" in c and budget is not None and not valid_budget:
            ok(exp["diagnostic"]["code"] == "invalid_request" and exp["tokens"] == [], c["id"])
        if "edge_count" in c and valid_budget:
            ok((exp["diagnostic"]["code"] == "edge_budget") == (c["edge_count"] > budget), c["id"])
    codes = {c["expected"].get("diagnostic", {}).get("code") for c in cases}
    ok({"", "cost_overflow", "edge_budget", "invalid_request", "no_root", "unknown_token",
        "invalid_token", "empty_input"} <= codes, codes)
    path = X.HERE / "cases_witness_r2.json"
    frozen = path.exists()
    if frozen:
        ok(path.read_text() == dumps(doc), "frozen file reproduced byte for byte")
    print("cases: %d (%d rejected grammars, %d with depends_on); checks passed: %d; frozen file %s"
          % (len(cases), sum(1 for c in cases if c["expected"].get("grammar_rejected")),
             sum(1 for c in cases if c["depends_on"]), n,
             "reproduced byte for byte" if frozen else "NOT WRITTEN YET"))
    print("SELFTEST OK")


if __name__ == "__main__":
    doc, built = build()
    if "--write" in sys.argv:
        with open(X.HERE / "cases_witness_r2.json", "x") as fh:
            fh.write(dumps(doc))
    elif "--check" in sys.argv:
        check(doc, built)
    else:
        sys.stdout.write(dumps(doc))
