# Review of the submission format and raw scorer

Reviewed `spec/submission.md` and `tools/score.py` at `79b2fc9`. The reference results of 4,800/4,800 reported by D concern well-formed released-class predictions. A synthetic five-row training file exposes a validation problem for other submitters. All five rows were counted as accepted and four as correct. [Format](../spec/submission.md) · [Scorer](../tools/score.py)

| Synthetic singleton submission | Observed treatment | Requested handling |
| --- | --- | --- |
| `truncated/accepted`, `error/accepted` or `no_parse/accepted`, correct target string | Each earned accepted and correct credit | Enforce the two-axis state contract on input. Incomplete construction cannot yield an accepted answer. |
| `complete/accepted`, empty reading array | Raised accepted coverage | Reject the invalid cardinality. |
| `complete/accepted`, repeated same reading | Deduplicated and credited | Specify whether duplicate submitted readings invalidate the row. The canonical wire representation has distinct strings. |

The validation should distinguish diagnostic parser output from a scoring submission. For example, a parser retains all extra readings on `error/abstain/reading_count`, while the scoring format requests an empty array on abstention. Document the projection and the status used for a system that deliberately abstains after completing construction. Compare exact canonical strings after sorting and keep the original system output available for audit. Missing IDs already contribute an abstention to the assigned denominator.

The printed transfer summary gives counts of families with all, none or some rows correct. The promised per-family numerator and denominator for the preregistered cluster analysis still need an output under D's custody (opaque IDs suffice). For reserved panels, the code requires an explicit panel, ledger path and reason. It appends a submission digest on every invocation. Record the frozen runnable-system digest as specified, the target version, and the registered decision/cohort look. Repeated openings currently depend on D's separate custody procedure. The joint look should accommodate every preregistered system. Only free-panel rows enter the per-row output.

I exercised the existing CLI with synthetic training targets and reviewed control flow for reserved panels. No reserved data or ledger was opened. The findings were sent to D for correction before using this scorer for a gate. Raw exact match and the adjudicated result should remain separately reportable. [Preregistered scoring](../docs/plans/07codex_plan.md)

## Recheck of revision e6b7b5d

I reran the CLI on the same five synthetic training rows. The submission SHA-256 reproduced as `5cda9cdbacd088bca1ed00bfe585fe0de9057540ed103ddaaf16249625799e3d`. All **five** per-row records now have `inadmissible=true`, `accepted=false` and `correct=false`. Set-aware yield and both accepted coverage measures are **0/5**. Accepted accuracy is undefined because there were zero accepted answers. This closes the reproduced scoring defect. The previous scorer gave 4/5 correct and 5/5 accepted on those same bytes.

The revised format permits an abstaining parser to preserve diagnostic readings. Its earlier field description still says “Empty for an abstention”; refer to the admissibility paragraph for the implemented exception. A repeated reading is inadmissible even on abstention. This replay used the training CLI path and synthetic files. D retains custody of reserved-panel operation. [Revised scorer](../tools/score.py) · [Admissibility rules](../spec/submission.md)
