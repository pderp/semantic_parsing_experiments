#!/usr/bin/env python3
"""Generate cases_witness_v1.json: tiny grammar/input pairs with ClaudeOracle's
expected full output (oracle_witness.py).  Deterministic; rerun to reproduce.

    python3 gen_cases_witness.py            # print to stdout
    python3 gen_cases_witness.py --write    # write cases_witness_v1.json (refuses to overwrite)
"""
import hashlib
import json
import sys

import oracle_witness as W

BUNDLE = W.load_bundle()
ONT = W.load_ontology()
PUB = BUNDLE["entries"]


def sel(*prefixes, without=()):
    return sorted(e for e in PUB if e.startswith(prefixes) and not e.endswith(tuple(without) or ("\0",)))


def clone(new_id, of, **kw):
    return dict({"id": new_id, "clone_of": of}, **kw)


OW = (".object-wide",)
SW = (".subject-wide",)
EU = "evaluate.tv.past.existential.universal."
DU = "discuss.tv.past.existential.universal."
SCOPE_BASE = ["det.a", "det.every", "noun.student", "noun.thesis"]
NEG = (["name.alice", "name.dan", "det.a", "det.every", "noun.scholar", "noun.dataset",
        "arrive.iv.bare.unit", "arrive.iv.past.unit", "quickly.bare.unit"]
       + sel("did-not.") + sel("cite.tv.bare."))
CONTROL = (["name.gia", "name.hugo", "name.eva", "det.a", "det.every", "noun.student",
            "noun.preprint", "noun.investigator", "noun.scientist", "leave.iv.bare.unit",
            "speak.iv.bare.unit", "quickly.bare.unit"]
           + sel("promise.sc.") + sel("persuade.oc.") + sel("to.") + sel("review.tv.bare.")
           + sel("did-not.") + sel("not-every."))
NOTEVERY = (["det.a", "det.every", "noun.reviewer", "noun.abstract", "noun.proposal",
             "speak.iv.past.universal", "speak.iv.bare.unit"]
            + sel("not-every.") + sel("discuss.tv.past.universal.") + sel("quickly.fin.") + sel("did-not."))
TVU = ["name.alice", "name.bob"] + sel("cite.tv.past.unit.unit.")
BIG = 2 ** 62

GRAMMARS = {
    "full": {},
    "tiny-iv": {"entries": ["name.alice", "name.bob", "leave.iv.past.unit", "arrive.iv.past.unit"]},
    "feature-mismatch": {"entries": ["det.every", "det.a", "noun.editor", "name.alice",
                                     "leave.iv.past.unit", "leave.iv.past.existential"]},
    "tv-unit": {"entries": TVU},
    "tv-unit-sw": {"entries": ["name.alice", "name.bob", "cite.tv.past.unit.unit.subject-wide"]},
    "tv-unit-ow": {"entries": ["name.alice", "name.bob", "cite.tv.past.unit.unit.object-wide"]},
    "scope": {"entries": SCOPE_BASE + sel("evaluate.tv.past.") + sel("quickly.fin.")},
    "scope-sw": {"entries": SCOPE_BASE + sel("evaluate.tv.past.", without=OW)},
    "scope-ow": {"entries": SCOPE_BASE + sel("evaluate.tv.past.", without=SW)},
    "scope-one-pair": {"entries": SCOPE_BASE + sel("evaluate.tv.past.universal.existential.")},
    "neg": {"entries": NEG},
    "neg-plain-only": {"entries": ["name.dan", "did-not.simple.plain.unit", "arrive.iv.bare.unit",
                                   "quickly.bare.unit"]},
    "neg-wrong-kind": {"entries": ["name.dan", "did-not.simple.plain.universal", "arrive.iv.bare.unit"]},
    "neg-root-only": {"entries": NEG, "roots": ["S[fin,negative]"]},
    "not-every": {"entries": NOTEVERY},
    "not-every-plain-only": {"entries": ["not-every.simple.plain", "noun.reviewer",
                                         "speak.iv.past.universal", "quickly.fin.universal"]},
    "control": {"entries": CONTROL},
    "control-to-plain-only": {"entries": [e for e in CONTROL if e != "to.simple.quick"]},
    "fa-only": {"entries": TVU + ["leave.iv.past.unit"], "rules": ["seed.fa"]},
    "ba-only": {"entries": TVU + ["leave.iv.past.unit"], "rules": ["seed.ba"]},
    "max-tokens-3": {"entries": TVU + ["quickly.fin.unit"], "max_tokens": 3},
    "dup-name": {"entries": TVU + ["leave.iv.past.unit"],
                 "clones": [clone("name.alice.b", "name.alice")]},
    "multiword-clones": {"entries": ["name.dan", "arrive.iv.bare.unit", "arrive.iv.past.unit",
                                     "did-not.simple.plain.unit"],
                         "clones": [clone("did-not.simple.plain.unit.oneword", "did-not.simple.plain.unit",
                                          tokens=["didnt"]),
                                    clone("name.dan.twoword", "name.dan", tokens=["dan", "dan"])]},
    "cost-flip": {"entries": SCOPE_BASE + [EU + "subject-wide"],
                  "clones": [clone(EU + "object-wide.cheap", EU + "object-wide", cost=5)]},
    "cost-equal": {"entries": SCOPE_BASE,
                   "clones": [clone(EU + "subject-wide.c7", EU + "subject-wide", cost=7),
                              clone(EU + "object-wide.c7", EU + "object-wide", cost=7)]},
    "cost-negative": {"entries": SCOPE_BASE + [EU + "subject-wide"],
                      "clones": [clone(EU + "object-wide.neg", EU + "object-wide", cost=-3)]},
    "key-tiebreak": {"entries": SCOPE_BASE,
                     "clones": [clone(EU + "subject-wide.y", EU + "subject-wide"),
                                clone(EU + "subject-wide.x", EU + "subject-wide")]},
    "overflow": {"entries": ["cite.tv.past.unit.unit.subject-wide"],
                 "clones": [clone("name.alice.big", "name.alice", cost=BIG),
                            clone("name.bob.big", "name.bob", cost=BIG)]},
    "overflow-edge": {"entries": [],
                      "clones": [clone("name.alice.big", "name.alice", cost=BIG),
                                 clone("name.bob.big", "name.bob", cost=BIG - 1),
                                 clone("cite.free", "cite.tv.past.unit.unit.subject-wide", cost=0)]},
    "three-readings": {"entries": SCOPE_BASE + [EU + "subject-wide", EU + "object-wide"],
                       "clones": [clone(DU + "subject-wide.as-evaluated", DU + "subject-wide",
                                        tokens=["evaluated"])]},
    "four-readings": {"entries": SCOPE_BASE + [EU + "subject-wide", EU + "object-wide"],
                      "clones": [clone(DU + "subject-wide.as-evaluated", DU + "subject-wide", tokens=["evaluated"]),
                                 clone(DU + "object-wide.as-evaluated", DU + "object-wide", tokens=["evaluated"])]},
    "two-senses": {"entries": SCOPE_BASE + [EU + "subject-wide"],
                   "clones": [clone(DU + "subject-wide.as-evaluated", DU + "subject-wide", tokens=["evaluated"])]},
}

VOCAB = "vocabulary = tokens of the grammar's own entries (not the whole ontology)"
EDGE = "edge identity and count as defined in conventions.edge_count"
BOOLB = "a JSON boolean max_edges is malformed"
BUDTOK = "malformed max_edges returns an empty token list"
OVF = "cost_overflow returns empty result arrays"

CASES = []  # (grammar, input, max_edges or absent, depends_on, note)
NOBUDGET = object()


def add(grammar, inp, max_edges=NOBUDGET, dep=(), note=""):
    CASES.append((grammar, inp, max_edges, list(dep), note))


# --- full bundle: the 12 public fixtures and their duplicates
for s in ["Bob cited Ava.", "A student evaluated every thesis.",
          "Every editor discussed every report quickly.", "Dan did not arrive.",
          "A scholar did not cite every dataset.", "Not every analyst evaluated a proposal quickly.",
          "Not every reviewer discussed every abstract.", "Gia promised a student to speak quickly.",
          "Every investigator persuaded a scientist to leave.",
          "Hugo did not persuade Eva to review every preprint quickly.",
          "Cara reviewed the article.", "Finn quickly arrived."]:
    add("full", s)
add("full", "  A   STUDENT\tevaluated  EVERY thesis .  ", note="duplicate of fixture F02 in case and spacing")
add("full", "a student evaluated every thesis", note="duplicate of F02")
add("full", "\nbob\r\nCITED\fava.\v", note="duplicate of F01, all six ASCII whitespace characters")
add("full", "Every editor did not persuade every analyst to review every thesis quickly.",
    note="12 tokens: the longest licensed sentence")
add("full", "Every editor did not persuade every analyst to review every thesis quickly quickly.",
    note="13 known tokens: no_root by length")
add("full", "Alice left Bob left.")
add("full", "Alice promised Bob to persuade Cara to leave.", note="nested control")
add("full", "Alice left quickly quickly.", note="repeated adverb")
add("full", "Not every researcher did not leave.", note="both two-token edges; not-every needs a positive VP")
add("full", "Every researcher did not leave.", note="every > not > event")
add("full", "Not every researcher left.")
add("full", "Alice did not review a paper.")
add("full", "Every researcher promised Bob to leave.")

# --- budget on the full bundle
S = "Every researcher reviewed a paper."
N = W.count_edges(W.make_grammar(), ["every", "researcher", "reviewed", "a", "paper"])
add("full", S, 0, note="any valid sentence needs at least one edge")
add("full", S, N, [EDGE], "budget exactly at my edge count")
add("full", S, N - 1, [EDGE], "one below my edge count")
add("full", S, 10 ** 6)
add("full", S, -1, [BUDTOK], "malformed budget")
add("full", S, "5", [BUDTOK], "malformed budget")
add("full", S, 1.5, [BUDTOK], "malformed budget")
add("full", S, True, [BUDTOK, BOOLB], "malformed budget")
add("full", "Finn quickly arrived.", 0, note="no root exists, but the budget is hit first")
add("full", "Finn quickly arrived.", 1000, note="no root, budget not reached")
add("full", "Cara reviewed the article.", 0, note="lexical failure precedes the budget")
add("full", "", 0, note="empty input precedes the budget")
add("full", "Every editor did not persuade every analyst to review every thesis quickly quickly.", 0,
    note="more than 12 tokens: no_root before any edge")
add("full", 7, -1, note="non-string sentence and malformed budget")

# --- requests and tokens
for g in ("tiny-iv",):
    add(g, "Alice left.")
    add(g, "ALICE   left", note="duplicate in case and spacing")
    add(g, " alice\tLEFT . ", note="duplicate; whitespace before the final period")
    add(g, "bob arrived")
    add(g, "alice bob", note="repeated category NP[unit], nothing to combine")
    add(g, "left alice")
    add(g, "alice left left")
    add(g, "alice")
    add(g, "left")
    add(g, "alice left quickly", dep=[VOCAB], note="quickly is in the ontology, not in this grammar")
    add(g, "alice leave", dep=[VOCAB])
    add(g, "")
    add(g, ".")
    add(g, " . ")
    add(g, "   \t\n")
    add(g, "alice left..", note="only one final period is removed")
    add(g, "al1ce left")
    add(g, "the al1ce", note="first offending token wins: unknown before a later invalid one")
    add(g, "al1ce the", note="first offending token wins: invalid before a later unknown one")
    add(g, "alice, left")
    add(g, "Alïce left.", note="non-ASCII letter")
    add(g, "alice left", note="NBSP is not ASCII whitespace")
    add(g, 5)
    add(g, None)
    add(g, ["alice", "left"])
    add(g, "alice left", 3, [EDGE], "2 lexical + 1 binary edge")
    add(g, "alice left", 2, [EDGE])
    add(g, "alice left", 0)

# --- incompatible features
add("feature-mismatch", "every editor left", note="universal NP, no universal-subject VP entry")
add("feature-mismatch", "a editor left")
add("feature-mismatch", "alice left")
add("feature-mismatch", "editor left", note="bare N cannot be a subject")
add("feature-mismatch", "every alice left")
add("feature-mismatch", "a every editor left")

# --- repeated categories, Unit collapse
add("tv-unit", "alice cited bob", note="two NP[unit]; two witnesses, one reading")
add("tv-unit", "alice cited alice", note="same token twice")
add("tv-unit", "ALICE cited\tBOB.", note="duplicate in case and spacing")
add("tv-unit", "alice cited")
add("tv-unit", "cited alice bob")
add("tv-unit", "alice bob cited")
add("tv-unit-sw", "alice cited bob")
add("tv-unit-ow", "alice cited bob", note="only the object-wide entry: one witness with one object-wide use")

# --- scope
for s in ["a student evaluated every thesis", "every student evaluated a thesis",
          "every student evaluated every thesis", "a student evaluated a thesis",
          "a student evaluated every thesis quickly", "every thesis evaluated a student quickly",
          "a student quickly evaluated every thesis", "a student evaluated quickly every thesis"]:
    add("scope", s)
add("scope-sw", "a student evaluated every thesis", note="object-wide entries removed: one reading")
add("scope-sw", "every student evaluated every thesis")
add("scope-ow", "a student evaluated every thesis", note="subject-wide entries removed")
add("scope-ow", "every student evaluated every thesis", note="like quantifiers have no object-wide entry")
add("scope-one-pair", "every student evaluated a thesis")
add("scope-one-pair", "a student evaluated every thesis", note="only the universal/existential entries exist")
add("scope-one-pair", "every student evaluated every thesis")

# --- VP negation and the two-token auxiliary
for s in ["dan did not arrive", "dan did not arrive quickly", "a scholar did not cite every dataset",
          "every scholar did not cite a dataset quickly", "alice did not cite dan", "dan arrived",
          "dan did arrive", "dan not arrive", "dan did not arrived", "dan did not did not arrive",
          "did not arrive", "dan did not", "dan did not arrive did not", "not dan arrived",
          "dan did did not arrive", "did dan not arrive"]:
    add("neg", s)
add("neg-plain-only", "dan did not arrive")
add("neg-plain-only", "dan did not arrive quickly", note="no auxiliary entry selects a quick VP")
add("neg-wrong-kind", "dan did not arrive", note="auxiliary entry exists only for a universal subject")
add("neg-root-only", "dan did not arrive")
add("neg-root-only", "dan arrived", note="S[fin,simple,plain] is derivable but is not a root here")

# --- sentence-initial not every
for s in ["not every reviewer spoke", "not every reviewer spoke quickly",
          "not every reviewer discussed a proposal", "not every reviewer discussed every abstract",
          "not every reviewer discussed a proposal quickly", "every reviewer spoke",
          "not a reviewer spoke", "not every reviewer did not speak", "every reviewer did not speak",
          "not every spoke", "not reviewer spoke", "every not reviewer spoke", "not every reviewer",
          "not not every reviewer spoke", "not every every reviewer spoke"]:
    add("not-every", s)
add("not-every-plain-only", "not every reviewer spoke")
add("not-every-plain-only", "not every reviewer spoke quickly", note="no macro entry selects a quick VP")

# --- control
for s in ["gia promised a student to speak quickly", "every investigator persuaded a scientist to leave",
          "hugo did not persuade eva to review every preprint quickly",
          "not every investigator promised eva to leave", "gia promised eva to review hugo",
          "gia persuaded eva to review eva", "gia promised to leave", "gia promised eva leave",
          "gia promised eva to promise hugo to leave", "gia promised eva quickly to leave",
          "gia persuaded eva to to leave", "gia promised eva to",
          "every investigator did not promise every student to review every preprint quickly",
          "every investigator did not promise every student to review every preprint quickly quickly"]:
    add("control", s)
add("control-to-plain-only", "gia promised eva to speak")
add("control-to-plain-only", "gia promised eva to speak quickly", note="no infinitive entry selects a quick VP")

# --- rule and length restrictions
add("fa-only", "alice left", note="subject needs backward application")
add("fa-only", "alice cited bob")
add("ba-only", "alice left")
add("ba-only", "alice cited bob", note="object needs forward application")
add("max-tokens-3", "alice cited bob")
add("max-tokens-3", "alice cited bob quickly", note="4 tokens > max_tokens 3")
add("max-tokens-3", "alice cited bob quickly", 0, note="length check precedes the budget")

# --- duplicate entries (clones)
add("dup-name", "alice left", note="two entries for one token and category: two witnesses, one reading")
add("dup-name", "bob left")
add("dup-name", "alice cited alice", note="2 x 2 x 2 witnesses, one reading")
add("dup-name", "alice cited bob")
E3 = W.count_edges(W.make_grammar(GRAMMARS["dup-name"]), ["alice", "left"])
add("dup-name", "alice left", E3, [EDGE], "3 lexical edges + 1 binary edge (one packed NP[unit] node)")
add("dup-name", "alice left", E3 - 1, [EDGE])
add("multiword-clones", "dan didnt arrive", note="one-token clone of the auxiliary")
add("multiword-clones", "dan did not arrive")
add("multiword-clones", "dan dan arrived", note="two-token name clone")
add("multiword-clones", "dan dan did not arrive")
add("multiword-clones", "dan dan dan arrived")
add("multiword-clones", "dan didnt didnt arrive")

# --- ranking by cost, object-wide count and key
T = "a student evaluated every thesis"
add("cost-flip", T, note="cheaper object-wide witness ranks first")
add("cost-equal", T, note="equal cost: subject-wide first")
add("cost-negative", T, note="negative lexical cost")
add("key-tiebreak", T, note="equal cost and object-wide count: entry ID decides; one reading")
add("two-senses", T, note="two readings from two frames, equal cost and object-wide count: key decides display order")
add("three-readings", T, note="three distinct readings")
add("four-readings", T, note="four distinct readings")

# --- cost overflow
add("overflow", "alice cited bob", dep=[OVF], note="2^62 + 2^62 + 10 exceeds signed 64-bit")
add("overflow", "alice cited alice", dep=[OVF])
add("overflow-edge", "alice cited bob", note="total is exactly 2^63 - 1: no overflow")
add("overflow-edge", "alice cited alice", dep=[OVF], note="2^62 + 2^62 overflows by one")
add("overflow-edge", "bob cited bob", note="total 2^63 - 2")

CONVENTIONS = {
    "grammar_spec": "Each grammar is a restriction of the published bundle seed-witness-v1. "
                    "'entries' lists published entry IDs (absent = all 178). 'clones' add an entry that "
                    "keeps its source's recipe, ground category and meaning, with a new id and optionally "
                    "new cost or tokens. 'rules', 'roots', 'max_tokens' default to the published values.",
    "input": "The JSON value passed as the sentence. Non-strings are deliberate.",
    "max_edges": "Present only when the request carries a budget.",
    "expected": "tokens, construction_status, decision, diagnostic {code[, token, index]}, readings "
                "(canonical set, byte order), min_cost, ranked_readings (display order by best witness), "
                "witnesses in rank order with cost, object_wide_uses, key (JSON arrays for the contract's "
                "tuples) and the reading each supports.",
    "edge_count": "My count of distinct edges in exact mode for inputs that pass lexical and length "
                  "checks: packed bottom-up chart over all spans; node = (start, end, ground category); "
                  "lexical edge = (start, end, entry ID); binary edge = (rule ID, left node, right node). "
                  "Truncated iff edge_count > max_edges.",
    "depends_on": "Readings of points witness-v1.md leaves open. A mismatch on a case with a non-empty "
                  "depends_on list may be a difference of convention rather than a defect.",
}


def build():
    grammars = {name: W.make_grammar(spec, BUNDLE) for name, spec in GRAMMARS.items()}
    cases = []
    for idx, (gname, inp, budget, dep, note) in enumerate(CASES, 1):
        g = grammars[gname]
        case = {"id": "W%03d" % idx, "grammar": gname, "input": inp}
        kwargs = {}
        if budget is not NOBUDGET:
            case["max_edges"] = budget
            kwargs["max_edges"] = budget
        exp = W.analyse(inp, g, ONT, **kwargs)
        for w in exp["witnesses"]:
            del w["rank"]  # position in the list is the rank
        case["expected"] = exp
        if isinstance(inp, str) and exp["diagnostic"]["code"] in ("", "no_root", "edge_budget",
                                                                  "cost_overflow", "reading_count") \
                and len(exp["tokens"]) <= g["max_tokens"]:
            case["edge_count"] = W.count_edges(g, exp["tokens"])
        case["depends_on"] = dep
        case["note"] = note
        cases.append(case)
    sha = lambda p: hashlib.sha256((W.INBOX / p).read_bytes()).hexdigest()
    return {"format": "claudeoracle-witness-cases-v1", "bundle": BUNDLE["version"],
            "inventory_sha256": sha("bundle_inventory_no_meanings.json"),
            "ontology_sha256": sha("ontology.yaml"), "contract_sha256": sha("contract.md"),
            "witness_contract_sha256": sha("witness-v1.md"),
            "conventions": CONVENTIONS, "grammars": GRAMMARS, "cases": cases}


def dumps(doc):
    return json.dumps(doc, indent=1, ensure_ascii=True) + "\n"


if __name__ == "__main__":
    text = dumps(build())
    if "--write" in sys.argv:
        with open(W.HERE / "cases_witness_v1.json", "x") as fh:
            fh.write(text)
    else:
        sys.stdout.write(text)
