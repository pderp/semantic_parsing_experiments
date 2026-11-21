#!/usr/bin/env python3
"""Regression: the worked examples printed in the public contract."""
import oracle

CASES = {
    "Alice left.": ["(ExistsV (lam V (And (Agent #0 alice) (And (Leave #0) (Past #0)))))"],
    "Alice did not leave.": ["(Not (ExistsV (lam V (And (Agent #0 alice) (And (Leave #0) (Past #0))))))"],
    "Every researcher promised Bob to leave.": ["(ForallE (lam E (Implies (Researcher #0) (ExistsV (lam V (And (Agent #0 #1) (And (Content #0 (Box (ExistsV (lam V (And (Agent #0 #2) (Leave #0)))))) (And (Past #0) (And (Promise #0) (Recipient #0 bob))))))))))"],
    "Alice did not review a paper.": ["(Not (ExistsE (lam E (And (ExistsV (lam V (And (Agent #0 alice) (And (Past #0) (And (Review #0) (Theme #0 #1)))))) (Paper #0)))))"],
    "Not every researcher left.": ["(Not (ForallE (lam E (Implies (Researcher #0) (ExistsV (lam V (And (Agent #0 #1) (And (Leave #0) (Past #0)))))))))"],
}

ok = True
for s, want in CASES.items():
    got = oracle.analyse(s)
    good = got["readings"] == want
    ok &= good
    print("PASS" if good else "FAIL", s)
    if not good:
        print("  want", want)
        print("  got ", got["readings"], got["diagnostic"])
assert oracle.tokenize(" ALICE reviewed Bob. ") == oracle.tokenize("alice reviewed bob") == ["alice", "reviewed", "bob"]
r = oracle.analyse("Every researcher reviewed a paper.")
assert r["decision"] == "ambiguous" and r["readings"][0].startswith("(ExistsE"), r
assert oracle.analyse(5)["construction_status"] == "error"
assert oracle.analyse("")["construction_status"] == "no_parse"
print("ALL OK" if ok else "FAILURES")
raise SystemExit(0 if ok else 1)
