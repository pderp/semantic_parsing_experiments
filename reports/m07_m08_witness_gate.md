# M07–M08 frozen witness comparison

**181/181 grammar/input pairs match** across 32 grammars after correcting two reference-parser defects. All 138 ordered root witnesses match on cost, object-wide count, canonical reading and full recursive structural key. The 15 convention-dependent cases are included. The remaining 166 match as well. Of the 32 grammars, 11 define 18 lexical clones. [Frozen cases](../oracle/cases_witness_v1.json) · [Comparison](../tests/reference/compare_witness_cases.py) · [Witness revision 2](../spec/witness-v1.md)

The cases SHA-256 is `68edf14dd266e3b83608084339a11ef1b9c848d464c07fe8a48744f043bc1621`. The runner verifies the historical ontology, reading contract, witness contract and meaning-free inventory against the hashes in those cases. It compiles its own meanings from the frozen seed-1.0 ontology using the reference recipes and checks all 178 public entry descriptions, rules, roots and bounds before applying each restriction. The original full-bundle digest reproduces as `af001c1b5e76ce7ead58f2ee0cb3a610bff626d1627c72181a789d9de78e45a4`. The production seed-1.1 digest remains `01ac38bec5bbc8910aa81b61c318c1c742059fdfefdd732aec46b78495ec2ed8`. This comparison uses public frozen data and no oracle implementation.

## Discrepancies before correction

The first replay used the parser logic from `5499f2b` with a loader for the declared historic grammars. The three rows below are the entire difference after lossless diagnostic-field and JSON tuple conversion. All three expected `no_parse/abstain/no_root`, empty readings, ranked readings and witnesses, and null minimum cost. Tokens matched throughout.

| Case | Before correction | Classification and resolution |
| --- | --- | --- |
| W117, `neg-root-only`, “dan arrived” | `complete/accepted`, empty diagnostic, minimum 0. One reading and witness. | Reference defect. The full grammar accepts a plain finite root. This restricted grammar admits only a negative root. Witness eligibility now uses the active root set. |
| W156, `max-tokens-3`, “alice cited bob quickly” | `complete/accepted`, empty diagnostic, minimum 10. One reading and two witnesses. | Reference defect. Four tokens exceed this bundle's three-token limit. Length checking now uses the active bound. |
| W157, same grammar and sentence, zero edge budget | `truncated/abstain/edge_budget`, empty arrays, null minimum. | Same reference length defect. Lexical validation and the length check precede any attempted edge insertion. |

The first two rows each returned one surplus reading, also the sole ranked display reading. The following records preserve the exact surplus strings and the structural keys in the order returned. W157 had no ranking or key difference.

W117

```text
(ExistsV (lam V (And (Agent #0 dan) (And (Arrive #0) (Past #0)))))
```

```json
{"cost":0,"object_wide_uses":0,"key":[1,"seed.ba",0,2,"S[fin,simple,plain]","apply",[[0,0,1,"name.dan","name"],[0,1,2,"arrive.iv.past.unit","iv"]]]}
```

W156

```text
(ExistsV (lam V (And (Agent #0 alice) (And (Cite #0) (And (Past #0) (And (Quick #0) (Theme #0 bob)))))))
```

```json
{"cost":10,"object_wide_uses":0,"key":[1,"seed.ba",0,4,"S[fin,simple,quick]","apply",[[0,0,1,"name.alice","name"],[1,"seed.ba",1,4,"(S[fin,simple,quick]\\NP[unit])","apply",[[1,"seed.fa",1,3,"(S[fin,simple,plain]\\NP[unit])","apply",[[0,1,2,"cite.tv.past.unit.unit.subject-wide","tv.subject-wide"],[0,2,3,"name.bob","name"]]],[0,3,4,"quickly.fin.unit","manner"]]]]]}
{"cost":10,"object_wide_uses":1,"key":[1,"seed.ba",0,4,"S[fin,simple,quick]","apply",[[0,0,1,"name.alice","name"],[1,"seed.ba",1,4,"(S[fin,simple,quick]\\NP[unit])","apply",[[1,"seed.fa",1,3,"(S[fin,simple,plain]\\NP[unit])","apply",[[0,1,2,"cite.tv.past.unit.unit.object-wide","tv.object-wide"],[0,2,3,"name.bob","name"]]],[0,3,4,"quickly.fin.unit","manner"]]]]]}
```

## Verification and limits

The replay compares normalized tokens, both status axes, diagnostic code and optional offending token/index, exact canonical reading arrays, minimum cost, ranked distinct readings, and every witness in order. For the 152 rows with frozen exact edge counts it also checks the uncapped chart and the number actually inserted under the request budget. Result counts are 67 accepted, 17 ambiguous, 62 no-root, 5 empty-input, 6 invalid-token, 5 unknown-token, 6 edge-budget, 8 invalid-request, 3 cost-overflow and 2 reading-count. No remaining discrepancy required an oracle change.

The normative comparison uses the common published fields. The reference includes an additional raw closure and bundle metadata. The frozen oracle nests its diagnostic code, token and index, while the reference puts the code in a string field. Revision 2 specifies both encodings and their lossless crosswalk. It also settles points the frozen rows do not distinguish, including explicit null budgets and overflowing partial derivations outside a root. New targeted tests cover both bounds of signed overflow, an overflowing competitor alongside a safe witness, a rootless chart, validation/budget ordering, and clone guard inheritance. These figures describe the seed-1.0 fixture gate. The seed-1.1 results appear below. [Additional regressions](../tests/reference/test_restrictions.py)

Replay from the repository root.

```sh
python3 -m tests.reference.compare_witness_cases
python3 -m unittest discover -q
python3 -m unittest discover -s spike -q
```

## Seed-1.1 article gate

All **80/80** independently frozen cases match on the first reference run, including all **47 ordered witnesses** and every recursive structural key. The 66 full-bundle cases and 14 cases in three restricted grammars cover licensed articles, wrong articles, lexical failures, budget boundaries and clones. All 77 cases carrying a frozen edge count match both the uncapped edge count and the number actually inserted. All seven cases flagged for convention dependence match. There were 30 accepted and five ambiguous answers, 39 `no_root`, three `edge_budget`, two `unknown_token` and one `invalid_token`. The reference parser needed no production change. [Frozen seed-1.1 cases](../oracle/cases_witness_v11.json) · [R1–R4 decisions](../spec/witness-v1.md)

The frozen suite SHA-256 is `fe01af31dd5b1d90bf48c47f1380b2401310c9a3586c215502a344e57bc66f28`. The runner verifies the historical ontology, contract, witness contract and meaning-free inventory against the suite's hashes. Compiling the archived ontology with the reference recipes reproduces all 179 published entry descriptions, both article lists and the full bundle digest `01ac38bec5bbc8910aa81b61c318c1c742059fdfefdd732aec46b78495ec2ed8`. The comparison reads frozen data only and compares the same fields as the seed-1.0 gate. [Input manifests](../oracle/inbox_v3/SHA256SUMS) · [Replay code](../tests/reference/compare_witness_cases.py)

### Replaying the 181 seed-1.0 inputs under seed-1.1

We applied the original 32 grammar restrictions to the verified seed-1.1 bundle and compared each result with its frozen seed-1.0 expectation. **180/181 retain every expected response field**. Including auxiliary edge counts, **179/181** match throughout. Both deltas occur in the original `feature-mismatch` grammar.

| Case | Observable effect | Reason |
| --- | --- | --- |
| W069, *a editor left* | `complete/accepted` becomes `no_parse/abstain/no_root`. The single reading, ranked reading and witness disappear and minimum cost changes from 0 to null. Edges drop from 6 to 3. | The original `det.a` could form an existential NP with *editor*. Its seed-1.1 follower check now fails. |
| W073, *a every editor left* | Both versions return `no_parse/abstain/no_root` with empty results. Edges drop from 6 to 5. | Seed-1.0 anchored a standalone `det.a` before *every*. Seed-1.1 skips that edge. |

Both retain their normalized tokens. This migration comparison uses the original frozen answers. The two documented changes are explicit in a regression; the oracle fixture files remain immutable. [Migration regression](../tests/reference/test_restrictions.py)

```sh
python3 -m tests.reference.compare_witness_cases --seed seed-1.1
python3 -m tests.reference.compare_witness_cases --seed seed-1.0
python3 -m unittest tests.reference.test_restrictions -q
```

## Seed-1.1 supplement for witness revision 2

**111/111 frozen cases match on the first reference comparison.** Across 33 restrictions, 97 requests reach parsing and 14 fail at grammar construction as expected. All 35 ordered witnesses match in full, including the integer cost, object-wide count, canonical reading and recursive key. All 77 supplied exact edge counts and request-level insert counts agree. All 67 convention-dependent cases agree. The dedicated boundary block R068–R111 comprises 22 pairs (44 cases), one at the exact chart size and one a single edge below it. [Frozen supplement](../oracle/cases_witness_r2.json) · [Rerunnable comparison](../tests/reference/compare_witness_cases.py)

| Observed outcome | Cases |
| --- | ---: |
| Complete, accepted / ambiguous | 20 / 4 |
| Exhaustive failure, no root / unknown token / empty input / invalid token | 15 / 3 / 2 / 1 |
| Truncated at edge budget | 30 |
| Error, cost overflow / invalid request | 10 / 12 |
| Rejected grammar, before sentence parsing | 14 |

**Discrepancy classification.** Zero parser discrepancies, zero oracle discrepancies, and zero unresolved case differences. The older comparison harness assumed every restriction could be constructed and every explicit budget on an edge-count case was an integer. The supplemental runner records a failed restriction independently of the expected field, skips parsing such cases, passes explicit null distinctly from omission, and compares exact JSON numeric kinds. No change in parsing or ranking was needed. Invalid restriction declarations now have a named `ValueError` subclass for callers.

The frozen cases SHA-256 is `a459df6e50e8f79fa1eced8902e691e8485a6f7dc168db31b77b327e7557e4f0`. The runner verifies the seed-1.1 inventory and ontology from inbox_v3, its original reading contract, and the independently supplied revision-2 witness contract in inbox_v4 (SHA-256 `1bd28feae0e8ceef9b3123ff1d34c680549150abbd4008979f3001d6de3cfcaa`). Only frozen data are used. Revision 3 specifies the grammar-construction outcome, the unbounded nonnegative edge-budget domain and exact JSON integer versus floating-point validation. [Witness clarification](../spec/witness-v1.md)

```sh
python3 -m tests.reference.compare_witness_cases --suite seed-1.1-r2
```
