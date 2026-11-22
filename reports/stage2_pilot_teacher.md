# Stage 2 pilot · teacher labels on 100 sentences

**Run by:** ClaudeScope as D, 22 November 2026. **Status:** both batches scored. First batch reviewed by CodexPrime (`reports/stage2_pilot_teacher_review_codex.md`).

## Result

**The teacher's reading sets match D's targets on all 100 pilot sentences, byte for byte: 120 of 120 readings, including both readings of all 20 two-reading sentences.** It reported no doubts and took about five and a half minutes.

**The confirmation batch, whose targets were never public, is also perfect: 100 of 100 sentences and 120 of 120 readings.** Across both batches the teacher produced 240 of 240 target readings with no error and no stated doubt.

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

**Confirmation batch:** 100 further training sentences (80 single-reading, 20 two-reading, seed 20261127), whose targets exist only in D's private corpus, were given to the teacher under the same rules, with the instruction to keep its first answer file closed.

| Measure | Batch 2 result |
| --- | ---: |
| Correct reading sets | 100 of 100 |
| Target readings reproduced | 120 of 120 |
| Rows with a stated doubt | 0 |
| Time | 17:49:32 to 17:54:51 UTC, about 5.3 minutes |
| Answer file SHA-256 | `16dae7cd04741af2e1495feb2f0d71768465c6e815f2cee39cb374ce6e91f5ca` |

By stratum: simple 17/17, manner 19/19, negation 18/18, subject control 11/11, object control 15/15, two-reading plain 13/13, two-reading with manner 7/7.

This removes the public-answers explanation for the first batch. What remains is weaker: D's private corpus sits on the same machine and is readable by any session under this account, so isolation is still by instruction. The teacher states that it worked by hand from the contract.

## What the pilot measures so far

| Plan 05 item | Finding |
| --- | --- |
| Teacher conflicts with targets | None in 200 |
| Reader disagreement, distinct judgments | No disputed forms, so no human adjudication was needed for this batch |
| Teacher cost | About 3.3 seconds per sentence of wall-clock time in one interactive session; token cost not visible. A bulk run of 6,200 calls through an API would need its own measurement. |
| Tokenizer round trip (neural baseline) | **Not done.** Needs the FLAN-T5 tokenizer, which is not on this machine. |
| Repeat-call consistency | Not measured in this batch |

## Limits

- One teacher session, one pass, and the specification it was given is the full contract. A cheaper prompt (ontology plus a few examples) may do worse; that is untested.
- Perfect agreement here says the contract is learnable from its text by a strong model. It does not say the controlled language is hard.
- CodexPrime's review adds: the scores are D-reported and not independently replayed; one interactive session; no human timing or second ratings; repeatability, tokenizer behaviour, and API cost are unmeasured.
- Stage 2 authorization for bulk annotation still needs: the tokenizer check, a named teacher and budget for the bulk run, and the sponsor's approval.

## A question the result raises

The plan's bulk step has the teacher label about 6,000 sentences so that the neural model can be trained on teacher labels. On this evidence the teacher's labels equal D's generated targets. For the controlled corpus, training the neural model on D's targets directly would give the same data at no teacher cost, with the 200-sentence pilot as the evidence that a teacher reproduces them. That would be a protocol change (plan 05 registers teacher supervision) and needs CodexPrime's view and the sponsor's decision.
