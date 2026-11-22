# Stage 2 pilot · teacher labels on 100 sentences

**Run by:** ClaudeScope as D, 22 November 2026. **Status:** first batch scored; a confirmation batch is out. Not yet reviewed by CodexPrime.

## Result

**The teacher's reading sets match D's targets on all 100 pilot sentences, byte for byte: 120 of 120 readings, including both readings of all 20 two-reading sentences.** It reported no doubts and took about five and a half minutes.

One caveat limits what this shows, and a second batch is addressing it (below).

## Set-up

| Item | Value |
| --- | --- |
| Teacher | "CodexTeacher": a fresh Codex CLI session with no project context, started by the sponsor in its own directory. Same model family as CodexPrime, who wrote the contract; a different family from D's generator and ClaudeOracle. |
| Given | `spec/contract.md` and `spec/ontology.yaml` at `seed-1.1`, the 100 pilot inputs without targets, and written instructions (digests in the teacher's `SHA256SUMS`) |
| Instructions | Work only in its directory; label by reading the specification, with no program that derives meanings; code allowed only to check JSON and parenthesis balance; do not revise after reporting the digest |
| Answer file | SHA-256 `34c9d369979588f5d43b03489d215ab216a6f802fec00e298bb2d8653c2c53ed`, as reported by the teacher and verified on receipt |
| Targets | D's private corpus v1 (`ef705108…`); the 100 pilot rows |

## Scores

| Measure | Result |
| --- | ---: |
| Correct reading sets (exact match, right decision) | 100 of 100 |
| Target readings reproduced | 120 of 120 |
| Two-reading sentences with both readings | 20 of 20 |
| Malformed or unbalanced readings | 0 |
| Rows with a stated doubt | 0 |

By stratum: simple 32/32, manner 12/12, negation 15/15, subject control 11/11, object control 10/10, two-reading plain 11/11, two-reading with manner 9/9.

## What the teacher reported

- Start 17:36:07 UTC, finish 17:41:34 UTC; ten batches of ten. Its interface showed no token total.
- Hardest: control sentences with a quantified embedded object, where the controller's index must count four intervening binders; and swapping binder order in mixed-quantifier transitives.
- It reread its rows and fixed one missing closing parenthesis before reporting its digest.

## Caveat, and the confirmation batch

The targets for these 100 sentences are public: they are the notation reference in `data/controlled/pilot_targets_v1.jsonl`. The teacher was told not to read outside its directory, but nothing technically prevented it (the sentinel test showed that separation on this machine is by instruction only). I have no evidence that it did, and its status notes read like hand work, but a perfect score on public answers cannot rule it out.

**Confirmation batch:** 100 further training sentences (80 single-reading, 20 two-reading, seed 20261127), whose targets exist only in D's private corpus, have been given to the teacher under the same rules. Its result will be added here.

## What the pilot measures so far

| Plan 05 item | Finding |
| --- | --- |
| Teacher conflicts with targets | None in 100 |
| Reader disagreement, distinct judgments | No disputed forms, so no human adjudication was needed for this batch |
| Teacher cost | About 3.3 seconds per sentence of wall-clock time in one interactive session; token cost not visible. A bulk run of 6,200 calls through an API would need its own measurement. |
| Tokenizer round trip (neural baseline) | **Not done.** Needs the FLAN-T5 tokenizer, which is not on this machine. |
| Repeat-call consistency | Not measured in this batch |

## Limits

- One teacher session, one pass, and the specification it was given is the full contract. A cheaper prompt (ontology plus a few examples) may do worse; that is untested.
- Perfect agreement here says the contract is learnable from its text by a strong model. It does not say the controlled language is hard.
- Stage 2 authorization for bulk annotation still needs: the confirmation batch, the tokenizer check, a named teacher and budget for the bulk run, and the sponsor's approval.
