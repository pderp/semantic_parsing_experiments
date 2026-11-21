#!/usr/bin/env python3
"""Self-test for oracle_enum.py.  Python 3.14 stdlib only.  Run: python3 selftest_enum.py

Inputs are chosen by ClaudeOracle from the public contract's grammar; expected
reading counts come from the contract's "Reading counts" table.

Invariants checked for every input:
  I1  every witness replays (compositional interpreter over the witness tree
      alone, round-tripped through JSON) to its recorded meaning
  I2  ranking is a total order: rank tuples are pairwise comparable and
      pairwise distinct, witnesses are listed in strictly ascending order,
      and structural keys are unique
  I3  the reading set equals the set of witness meanings, is sorted by
      unsigned byte order and has no duplicates
  I4  status axes agree with the result-state table (1 -> complete/accepted,
      2 -> complete/ambiguous, 0 roots -> no_parse/abstain, failures carry a
      diagnostic and no witnesses)
  I5  min_cost is the minimum witness cost; cost = 10 x transitive lexical uses
  I6  ranked display: one entry per meaning, ordered by best witness, and the
      best witness of a meaning is its lowest-ranked witness
  I7  agreement with oracle.py (independent production-level derivation)
Plus: case/spacing duplicates give identical results; expected counts; the
frozen fixture answers; exhaustive short-sequence cross-check; budget -> truncated.
"""
import itertools
import json
import sys

import oracle
import oracle_enum as E

ONT = oracle.load_ontology()
LEX = oracle.Lexicon(ONT)
checks = 0


def ok(cond, msg):
    global checks
    checks += 1
    if not cond:
        raise AssertionError(msg)


def invariants(sentence):
    r = E.enumerate_all(sentence, ONT, LEX)
    ws = r["witnesses"]
    n = len(r["tokens"])
    status = (r["construction_status"], r["decision"])
    if not ws:
        ok(status in (("no_parse", "abstain"), ("error", "abstain")), (sentence, status))
        ok(r["diagnostic"] != "" and r["readings"] == [] and r["min_cost"] is None
           and r["ranked_meanings"] == [], sentence)
    else:
        # I1 replay, from a JSON round trip so only serialised data is used
        for w in ws:
            tree = json.loads(json.dumps(w["tree"]))
            ok(E.replay(tree, n, ONT, LEX) == w["meaning"], ("replay", sentence, w["rank"]))
            ok(E.key(tree) == w["key"], ("key from tree", sentence))
        # I2 total order
        ranks = [(w["cost"], w["object_wide_uses"], w["key"]) for w in ws]
        for a, b in itertools.combinations(range(len(ranks)), 2):
            lt, gt, eq = ranks[a] < ranks[b], ranks[a] > ranks[b], ranks[a] == ranks[b]
            ok(lt + gt + eq == 1 and lt, ("strict ascending total order", sentence, a, b))
        ok(len({json.dumps(w["key"]) for w in ws}) == len(ws), ("unique keys", sentence))
        ok([w["rank"] for w in ws] == list(range(len(ws))), sentence)
        # I3 reading set
        meanings = {w["meaning"] for w in ws}
        ok(set(r["readings"]) == meanings and len(r["readings"]) == len(meanings), sentence)
        ok(r["readings"] == sorted(r["readings"], key=lambda s: s.encode("ascii")), sentence)
        ok(all(m.isascii() and not m.endswith("\n") and "  " not in m for m in meanings), sentence)
        # I4 status axes
        want = {1: ("complete", "accepted"), 2: ("complete", "ambiguous")}.get(len(meanings))
        ok(status == want and r["diagnostic"] == "", (sentence, status))
        # I5 cost
        for w in ws:
            tv = sum(1 for l in E.leaves(w["tree"]) if l["recipe"].startswith("tv."))
            ok(w["cost"] == 10 * tv and tv <= 1, sentence)
        ok(r["min_cost"] == min(w["cost"] for w in ws) == ws[0]["cost"], sentence)
        # I6 ranked display
        rm = r["ranked_meanings"]
        ok({m["meaning"] for m in rm} == meanings and len(rm) == len(meanings), sentence)
        ok([m["best_witness_rank"] for m in rm] == sorted(m["best_witness_rank"] for m in rm), sentence)
        for m in rm:
            first = min(w["rank"] for w in ws if w["meaning"] == m["meaning"])
            ok(m["best_witness_rank"] == first, sentence)
        ok(rm[0]["best_witness_rank"] == 0, sentence)
    # I7 agreement with oracle.py
    o = oracle.analyse(sentence, ONT, LEX)
    ok((o["tokens"], o["construction_status"], o["decision"], o["readings"], o["diagnostic"])
       == (r["tokens"], r["construction_status"], r["decision"], r["readings"], r["diagnostic"]),
       ("oracle.py agreement", sentence))
    if ws:
        ok(sum(len(x["witnesses"]) for x in o["witnesses"]) == len(ws), ("witness count", sentence))
    return r


# ------------------------------------------------------------------ inputs
# (sentence, expected distinct readings, expected witnesses); 0 = failure
CASES = []


def add(sentence, readings, witnesses):
    CASES.append((sentence, readings, witnesses))


SUBJ = {"unit": "Ava", "existential": "a student", "universal": "every editor"}
OBJ = {"unit": "Ben", "existential": "a report", "universal": "every thesis"}


def tv_counts(sk, ok_):
    """(readings, witnesses) for a transitive with these semantic argument kinds."""
    if "unit" in (sk, ok_):
        return 1, 2
    return (2, 2) if sk != ok_ else (1, 1)


for q in ("", " quickly"):
    # ordinary root
    for sk, s in SUBJ.items():
        add("%s arrived%s." % (s, q), 1, 1)
        for ok_, o in OBJ.items():
            add("%s cited %s%s." % (s, o, q), *tv_counts(sk, ok_))
    # VP negation: inner subject is Unit
    for sk, s in SUBJ.items():
        add("%s did not wait%s." % (s, q), 1, 1)
        for ok_, o in OBJ.items():
            add("%s did not discuss %s%s." % (s, o, q), 1, 2)
    # initial not every: subject universal
    add("Not every scholar spoke%s." % q, 1, 1)
    for ok_, o in OBJ.items():
        add("Not every scholar evaluated %s%s." % (o, q), *tv_counts("universal", ok_))
    # control, both frames, three roots; embedded subject is Unit
    for verb, bare in (("promised", "promise"), ("persuaded", "persuade")):
        for rk, rec in OBJ.items():
            add("%s %s %s to leave%s." % (SUBJ["universal"], verb, rec.replace("report", "author").replace("thesis", "analyst"), q), 1, 1)
        add("Gia %s a professor to review every draft%s." % (verb, q), 1, 2)
        add("A scientist %s Dan to cite a dataset%s." % (verb, q), 1, 2)
        add("Every investigator %s every reviewer to evaluate Cara%s." % (verb, q), 1, 2)
        add("Hugo did not %s Eva to speak%s." % (bare, q), 1, 1)
        add("Every researcher did not %s a student to discuss every abstract%s." % (bare, q), 1, 2)
        add("Not every author %s a professor to wait%s." % (verb, q), 1, 1)
        add("Not every author %s Finn to review a manuscript%s." % (verb, q), 1, 2)

# every verb form at least once
for fr in ONT["frames"].values():
    if fr["construction"] == "intransitive":
        add("Alice %s." % fr["past"], 1, 1)
        add("Alice did not %s." % fr["bare"], 1, 1)
    elif fr["construction"] == "transitive":
        add("A researcher %s every paper." % fr["past"], 2, 2)
        add("A researcher did not %s every paper." % fr["bare"], 1, 2)

# duplicates: same sentence in different case and spacing must give identical results
DUPLICATES = [
    ["Every researcher reviewed a paper.", "every researcher reviewed a paper",
     "  EVERY   Researcher\treviewed  A paper .  ", "\nEvery researcher\r\nreviewed a paper.\n",
     "eVeRy ReSeArChEr ReViEwEd A pApEr.\f\v"],
    ["Alice left.", "ALICE LEFT", " alice\tleft .", "alice left. "],
    ["Not every analyst evaluated a proposal quickly.", "NOT EVERY ANALYST EVALUATED A PROPOSAL QUICKLY",
     "not   every analyst  evaluated a\tproposal quickly ."],
    ["Finn quickly arrived.", "finn  QUICKLY arrived"],
]
for group in DUPLICATES:
    for s in group:
        CASES.append((s, None, None))

# failures
FAILURES = [
    ("", "lexical"), ("   ", "lexical"), (".", "lexical"), (" . ", "lexical"),
    ("Cara reviewed the article.", "lexical"),          # unknown word
    ("Alice left..", "lexical"),                        # only one final period removed
    ("Alice left!", "lexical"), ("Alice, Bob left.", "lexical"), ("Alice's paper left.", "lexical"),
    ("Alice reviewed 2 papers.", "lexical"), ("Alice reviews Bob.", "lexical"),  # present tense
    ("Alice reviewed papers.", "lexical"),              # plural
    ("Alïce left.", "lexical"), (" Alice left.", "lexical"),  # non-ASCII letter / NBSP
    ("İstanbul left.", "lexical"),                 # no Unicode case folding
    ("Alice. left", "lexical"),
    ("Finn quickly arrived.", "roots"), ("Alice left quickly quickly.", "roots"),
    ("Quickly Alice left.", "roots"), ("Alice", "roots"), ("left", "roots"), ("Alice Bob.", "roots"),
    ("Alice reviewed.", "roots"), ("Alice left Bob.", "roots"), ("Alice leave.", "roots"),
    ("Alice did leave.", "roots"), ("Alice did not left.", "roots"), ("Alice not left.", "roots"),
    ("Alice did not not leave.", "roots"), ("Not Alice left.", "roots"),
    ("Not a researcher left.", "roots"), ("Not every researcher did not leave.", "roots"),
    ("Not every researcher leave.", "roots"), ("Every left.", "roots"), ("Researcher left.", "roots"),
    ("A every researcher left.", "roots"), ("Every Alice left.", "roots"),
    ("Alice promised to leave.", "roots"), ("Alice promised Bob leave.", "roots"),
    ("Alice promised Bob to left.", "roots"), ("Alice promised Bob.", "roots"),
    ("Alice promised Bob to persuade Cara to leave.", "roots"),   # nested control
    ("Alice promised Bob quickly to leave.", "roots"),           # manner on matrix control
    ("Alice quickly promised Bob to leave.", "roots"),
    ("Alice reviewed Bob to leave.", "roots"), ("Alice left to leave.", "roots"),
    ("Alice reviewed quickly Bob.", "roots"), ("Alice reviewed Bob Cara.", "roots"),
    ("Alice reviewed a.", "roots"), ("Alice reviewed every.", "roots"),
    ("to leave", "roots"), ("did not leave", "roots"), ("Alice did not.", "roots"),
    ("Alice left and Bob left.", "lexical"), ("Alice left Bob left.", "roots"),
    ("every researcher", "roots"), ("not every researcher", "roots"), ("quickly", "roots"),
]
for s, _ in FAILURES:
    CASES.append((s, 0, 0))


def main():
    results = {}
    for s, want_r, want_w in CASES:
        r = invariants(s)
        results[s] = r
        if want_r is not None:
            ok(len(r["readings"]) == want_r and len(r["witnesses"]) == want_w,
               ("expected counts", s, want_r, want_w, len(r["readings"]), len(r["witnesses"])))
    n_inputs = len(CASES)
    n_distinct = len({s for s, _, _ in CASES})
    ok(n_distinct >= 100, "need at least 100 inputs")

    for s, kind in FAILURES:
        d = results[s]["diagnostic"]
        ok(d.startswith("lexical failure") == (kind == "lexical"), ("failure kind", s, d))
    ok(E.enumerate_all(None)["construction_status"] == "error", "non-string")
    ok(E.enumerate_all(["alice", "left"])["decision"] == "abstain", "non-string list")
    ok(E.enumerate_all(b"alice left")["construction_status"] == "error", "bytes")

    # duplicates: identical tokens, statuses, readings, witnesses and keys
    for group in DUPLICATES:
        base = json.dumps(results[group[0]], sort_keys=True)
        for s in group[1:]:
            ok(json.dumps(results[s], sort_keys=True) == base, ("duplicate", s))

    # contract examples
    r = results["Every researcher reviewed a paper."]
    ok(r["ranked_meanings"][0]["meaning"].startswith("(ForallE") and r["readings"][0].startswith("(ExistsE"),
       "display order vs canonical set order")
    ok(r["witnesses"][0]["object_wide_uses"] == 0 and r["witnesses"][1]["object_wide_uses"] == 1, "sw first")
    ok(E.target_bytes(r["readings"]).startswith(b'["(ExistsE'), "target bytes")
    ok(results["Alice left."]["readings"] ==
       ["(ExistsV (lam V (And (Agent #0 alice) (And (Leave #0) (Past #0)))))"], "Alice left")

    # frozen fixture answers (answers_oracle_v1.json, not modified)
    answers = json.load(open(oracle.HERE / "answers_oracle_v1.json"))
    prompts = json.load(open(oracle.HERE / "inbox_v1" / "prompts_v1.json"))["prompts"]
    for p, a in zip(prompts, answers):
        r = invariants(p["input"])
        ok((r["tokens"], r["construction_status"], r["decision"], r["readings"])
           == (a["tokens"], a["construction_status"], a["decision"], a["readings"]), ("fixture", p["id"]))

    # witness census over the positive cases: at most 2 witnesses, reading design 1/2
    ok(all(len(r["witnesses"]) <= 2 for r in results.values()), "at most two witnesses")

    # exhaustive cross-check: every token sequence up to length 4 over a
    # representative vocabulary; enumerator and oracle.py must agree exactly.
    vocab = ["alice", "a", "every", "paper", "editor", "left", "leave", "reviewed", "review",
             "promised", "persuade", "did", "not", "to", "quickly"]
    total = accepted = 0
    for n in range(1, 5):
        for seq in itertools.product(vocab, repeat=n):
            s = " ".join(seq)
            r = E.enumerate_all(s, ONT, LEX)
            o = oracle.analyse(s, ONT, LEX)
            total += 1
            accepted += bool(r["witnesses"])
            ok((r["construction_status"], r["decision"], r["readings"])
               == (o["construction_status"], o["decision"], o["readings"]), ("exhaustive", s))
            for w in r["witnesses"]:
                ok(E.replay(w["tree"], n, ONT, LEX) == w["meaning"], ("exhaustive replay", s))

    # budget -> truncated/abstain, even though a candidate exists
    t = E.enumerate_all("Every researcher reviewed a paper.", ONT, LEX, budget=3)
    ok((t["construction_status"], t["decision"], t["readings"]) == ("truncated", "abstain", []), "budget")

    pos = sum(1 for r in results.values() if r["witnesses"])
    print("inputs: %d (%d distinct strings; %d with witnesses, %d failures)"
          % (n_inputs, n_distinct, pos, n_distinct - pos))
    print("exhaustive short sequences: %d checked, %d admitted" % (total, accepted))
    print("checks passed: %d" % checks)
    print("SELFTEST OK")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as exc:
        print("SELFTEST FAILED:", exc)
        sys.exit(1)
