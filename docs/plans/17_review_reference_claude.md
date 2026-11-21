# Review of the first reference parser and the witness contract

**Reviewed:** `spec/witness-v1.md` and the guard section of `spec/dsl.md` at `2f967e8`; `src/reference/`, `grammar/seed_recipes.metta`, `tests/reference/` at `4b5f637`. **Reviewer:** ClaudeScope, 21 November 2026.

## Verdict

Accepted as the first end-to-end reference parser for `seed-1.0`. I found no defect. The full M07–M08 gate (100 frozen tiny grammar and input pairs, exact witness parity with the oracle) is still open, as CodexPrime says.

## What I ran

| Check | Result |
| --- | --- |
| `python3 -m unittest discover` and the spike suite | 24 and 13 tests pass |
| `python3 -m tests.reference.compare_oracle` | 392 variants and 680 ranked witnesses match the oracle |
| **New: `python3 tools/fuzz_reference_vs_oracle.py`** | 29,988 inputs (the 392 variants, about 40 mutations of each, and 20,000 random token sequences): 671 parse, 29,317 do not; **zero disagreements** with the oracle on tokens, both status axes, reading sets, and ranked (cost, object-wide count, reading) |
| **New, private:** reference parser against D's targets | 4,800 rows (training and ordinary development of dry run 1): **zero mismatches** in status, decision, or reading set |

The fuzz check matters because the earlier comparison used only sentences that should parse. Mutated and random inputs test that the parser does not accept too much. I did not run the parser on any development-transfer, calibration, or locked row; those panels are opened once, at their gates.

## Reading the code

- The recipes in `grammar/seed_recipes.metta` match the contract: negation applies the subject once and passes a `Unit`; *not every* negates the closed inner clause; the control recipe closes the infinitive inside `Box` with the chosen controller; manner and tense wrap the event continuation.
- Guards are ground categories compared for equality, so a chart node's key decides everything about its future use. That is a clean answer to review 16's question, and it puts the guard state in the witness key as required.
- Packing is by span and ground category, edges are kept as a set, and witnesses are enumerated from the forest and sorted by the contract's tuple. Python's string order equals unsigned byte order here because all identifiers are ASCII.
- The three residual points from review 16 are implemented (saturation check, depth non-match, summed-cost overflow).

## Witness contract

`spec/witness-v1.md` answers all 15 of ClaudeOracle's points. I have copied it to ClaudeOracle with the bundle inventory. The inventory copy has the `meaning` field removed from every entry, so ClaudeOracle adopts identifiers, categories, recipe names, and costs but keeps its own semantics.

## What the controlled pilot can and cannot show

This is a finding about the plan, not about the code, and I should have raised it when plan 05 moved the corpus to a generator.

The public contract specifies the whole controlled language, and the reference grammar implements the whole contract. Every controlled input, in every split, is generated from that same contract. So:

- **The grammar's coverage and accuracy on controlled inputs are 100% by construction,** unless there is a bug. The 60% coverage gate, the 95% accuracy gate, and the 100/200 and 75/150 transfer floors cannot fail for the grammar.
- **The paired transfer comparison cannot fail either.** If the grammar is right on every held-out family, the neural model can never be ahead, so the upper limit of (neural − grammar) is at most zero and the gate passes whatever the neural model does.
- For the grammar, the held-out families are therefore a **verification** that four implementations agree, not an experiment whose outcome is uncertain.

What remains informative in the pilot:

1. **How far the neural model falls short on held-out combinations.** That is a real result about distillation into a neural model, and the design's central contrast.
2. **How well the teacher's labels match the contract** (stage 2's 100-input pilot).
3. **Serving cost** of the native parser against the neural model.
4. **Natural text.** Coverage of real sentences is where the grammar's outcome is uncertain. Plan 03 schedules a 200-sentence survey and a 300-sentence development sample (M13).

**Recommendations, for CodexPrime's view and the sponsor's decision:**

- Keep the frozen protocol; do not redesign the controlled pilot.
- State in every report that the grammar's controlled results are by construction, and present the neural shortfall as the controlled finding.
- **Bring the natural-text survey forward** to run alongside M08, since it is the first measurement whose result we do not already know. It needs the sponsor's agreement to fetch public PLOS ONE text.
- Treat Decision 2 (adapter funding) as resting in practice on the serving-cost gate and the natural-text result, and say so before the numbers arrive.

## Next

1. CodexPrime: reply on the section above; draft `seed-1.1` (*an*) if the sponsor approves; then the M07–M08 gate with ClaudeOracle's frozen pairs.
2. ClaudeOracle: adopt the published identifiers and shapes; freeze at least 100 tiny grammar and input pairs.
3. ClaudeScope: regenerate and release the corpus after the *an* decision; shared finite-world evaluator and world bank.
