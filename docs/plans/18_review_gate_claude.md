# Review of the M07–M08 witness gate

**Reviewed:** `reports/m07_m08_witness_gate.md`, `tests/reference/compare_witness_cases.py`, `src/reference/restrictions.py`, and `spec/witness-v1.md` revision 2 at `ee5bd76`. **Reviewer:** ClaudeScope, 22 November 2026.

## Verdict

**The gate is met for `seed-1.0`.** Plan 03 asks for at least 100 frozen tiny grammar and input pairs with zero unexplained discrepancies in derivations, witnesses, minimum costs, ties, and distinct meanings. There are 181 pairs over 32 grammars, frozen by ClaudeOracle before any comparison, and the reference parser now matches all of them, including all 138 ranked witness keys.

## What I checked

- The case file's digest is the one ClaudeOracle sent before the comparison (`68edf14d…`).
- I re-ran `python3 -m tests.reference.compare_witness_cases`: 181 of 181, 138 witnesses.
- The comparison reads the frozen JSON and the meaning-free inventory only. Neither it nor `src/reference/restrictions.py` imports any oracle code.
- All repository tests pass.

## The three initial mismatches

All three were defects in the reference parser, not in the oracle, and all concern restricted grammars: a root category excluded by the tiny grammar was still accepted (W117), and the global 12-token limit was used where the tiny grammar set 3 (W156, W157). None affects the full seed grammar, which is why the earlier 29,988-input fuzz comparison did not see them. This is what the tiny-grammar gate is for, and the report records the surplus readings and keys exactly.

## Remaining items

1. **The gate is for `seed-1.0`.** ClaudeOracle is freezing a `seed-1.1` case file for the article rule. The gate is repeated on it when it arrives.
2. **Fifteen cases depended on open conventions.** Revision 2 of the witness contract settles them and all 15 match. ClaudeOracle should confirm that revision 2 says what its cases assumed, so that the match is agreement and not coincidence.
3. The fuzz tool compares against the seed-1.0 enumerator and does not know *an*. It needs the seed-1.1 enumerator before it is run again.

## Next

Native CPU port: scope agreed in outline (CodexPrime's message 77). It starts after the world bank is frozen. D selects the 200 ordinary-development inputs for parity at that point.
