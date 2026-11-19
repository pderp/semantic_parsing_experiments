# Sign-off on `09codex_plan.md` and spike result

**Reviewed:** `docs/plans/09codex_plan.md` at commit `0a870f1`.

**Reviewer:** Claude (Fable 5.2), 19 November 2026.

## Sign-off

Plan 09 is approved for implementation. It settles both points from my fourth review: the family key is determiner position and construction, with the determiner-identity count reported beside it, and the sponsor is asked before the pilot whether the runtime comparison is conditional. I have no further changes to request.

## Spike result

I built the scope spike, since it was the next task and needed no decisions. It passes.

- **Location:** `spike/`, with replay commands and evidence in `spike/README.md` and saved output in `spike/output.json`.
- **Outcome:** one packed root, two witnessed normalized readings, separated by the registered world; identical results under reversed and shuffled lexical insertion order. 13 checks pass.
- **Scope:** application rules only. The spike is disposable and is not the reference parser.

## What the spike found for M01

Seven contract questions are listed in `spike/README.md`. Two matter most:

1. **Conjunct sort order is undefined.** Sorting by canonical text puts a quantified conjunct before its restrictor, the reverse of the order the design prints in Equation 18. My own first test expectation got this wrong. Exact-match scoring depends on the generator owner and the grammar author producing identical text independently, so the contract must define the sort key precisely.
2. **The tie rule between equal-cost readings is arbitrary.** The spike's rule orders the readings by how the entry names happen to sort. The contract needs a stated rule.

## A note on roles

Plan 03 proposes a fresh Claude session as the independent author of the tiny exhaustive oracle. I wrote this spike, so that oracle should come from a different session that has not read `spike/`, to keep the independence the plan relies on.

## Next

The family census (D), then the M01 contract draft using the questions above.
