# ClaudeScope status log

Newest first.

## 21 November 2026 (reference parser review)

- Reviewed the reference parser and witness contract (`docs/plans/17_review_reference_claude.md`). Added `tools/fuzz_reference_vs_oracle.py`: 29,988 inputs, zero disagreements. Private scoring on 4,800 training and ordinary development rows: zero mismatches. No transfer, calibration, or locked row was run.
- Raised that the grammar's controlled results are by construction and recommended bringing the natural-text survey forward.
- Copied the witness contract and a meaning-free bundle inventory to ClaudeOracle (`inbox_v2/`).
- Sponsor has asked the design author for the original checker files.
- Mailbox cursor: last read message 52.
- **Blocked on:** sponsor decisions on *an* and on the natural-text survey.

## 21 November 2026 (corpus dry run)

- Generated the 6,000-row controlled corpus privately under the reserved panels; audit passes 26 of 26 checks, including identical reading sets from ClaudeOracle's enumerator on all 6,000 rows.
- Found the *a/an* defect (876 rows). Withheld the release; relabelled the private corpus as dry run 1; proposed `seed-1.1`. Report: `reports/corpus_dryrun1.md`.
- Recorded the `seed-1.0` digests from CodexPrime's promotion (`950e90e`).
- Mailbox cursor: last read message 51.
- **Blocked on:** sponsor decision on *an*; then regenerate and release.
- **Not yet done:** review of CodexPrime's reference parser (`4b5f637`) and `spec/witness-v1.md`.

## 21 November 2026 (stage 1 approved)

- Sponsor approved all five sign-off items. Recorded in the sign-off record and plan 11.
- Reserved the two transfer panels (private manifest, digest `75c6a719…`, read-only).
- Ran the pre-score bootstrap check (`reports/prescore_check.md`): false-pass 6–8% against a nominal 5%; otherwise as planned.
- Adopted CodexPrime's wording on the three kinds of evidence (message 48).
- Mailbox cursor: last read message 48.
- **Next:** generate the controlled corpus and targets under the reserved panels; shared finite-world evaluator.

## 21 November 2026 (reconciliation and sign-off draft)

- Sponsor finished the worksheet (`cac34b1`). Published originals and `reports/fixtures_v1_reconciliation.md`; built `fixtures/reconciled_v1.json`.
- Reviewed M02 and the M03 kernel (`docs/plans/16_review_m02_m03_claude.md`). Cross-checked CodexPrime's normalizer against the private generator: 3,400 scrambled terms, zero mismatches.
- Drafted `reports/stage1_signoff.md` with five items for the sponsor.
- Integrated ClaudeOracle's enumerator under `oracle/` (digests verified; reading sets equal the generator's on all 392 variants) and filed its 15 underspecified points. Sign-off record now states that witness identity is frozen later, with the grammar bundle.
- Mailbox cursor: last read message 43.
- **Blocked on:** sponsor approval of stage 1 before reserving panels.

## 21 November 2026 (after reboot)

- Host was rebooted; session resumed. Read mailbox messages 26–30.
- Fixtures: CodexPrime's and ClaudeOracle's sealed answers both match D's sealed answers on all 12 items (status, decision, canonical strings). Digests verified. Originals not yet published because the sponsor's worksheet is half done.
- Corrected the census power table after CodexPrime's review 15 (mislabelled equal-yield columns; overstated claim). Rerun agrees with CodexPrime's independent calculation.
- Recorded sponsor feedback on the worksheet in `docs/reading_task_guidelines.md`.
- Mailbox cursor: last read message 30.
- **Blocked on:** sponsor worksheet (F07–F12).

## 21 November 2026 (census and fixtures)

- Reviewed `seed-0.2-draft` and part 2 (`docs/plans/14_review_parts_claude.md`). The generator matches all six public canonical strings.
- Ran the census: `reports/census_seed-0.2-draft.md`. 150 primary families; allocation feasible up to 60 per panel; recommended 40 per panel because 20 gives an inconclusive comparison in most scenarios.
- Issued 12 fixture prompts (`fixtures/`), sealed D's answers privately, copied the frozen inputs to ClaudeOracle's directory, and wrote the sponsor worksheet.
- Mailbox cursor: last read message 22.
- **Blocked on:** three sets of fixture answers; CodexPrime's review of the census.

## 21 November 2026 (generator)

- Built the private generator (outside the checkout). It derives readings from the surface construction tree, with no chart. It reproduces both spike strings, *Alice left*, and *Alice did not leave* byte for byte.
- Structural check over every determiner variant: 150 primary families, 392 variants, 386 with one reading and 6 with two, in 4 primary families. This agrees with the public count script.
- Sentinel: ClaudeOracle can also read it (message 18). Separation is procedural for both other sessions.
- Sent CodexPrime the contract review (message 19). Mailbox cursor: last read message 18.
- **Blocked on:** `seed-0.2-draft` and CodexPrime's reply on the two-reading families.

## 21 November 2026 (contract review)

- Reviewed M01 draft part 1 (`6482eec`) in `docs/plans/13_review_contract_claude.md`. Added `tools/family_capacity.py`: 150 primary families, 12 with fewer than 10 distinct strings, 4 able to produce two readings.
- Sentinel: CodexPrime can read it (message 14). Sponsor confirmed two-stage sign-off.
- Mailbox cursor: last read message 15.
- **Next:** private generator; census on `seed-0.2-draft`.

## 21 November 2026 (review 12)

- Read CodexPrime's review of plan 11 (`bb53fc9`). Accepted all six points and appended them to plan 11, including a proposed two-stage sign-off.
- Created the dummy sentinel in the private directory and asked CodexPrime and ClaudeOracle to try to read it.
- Mailbox cursor: last read message 10.
- **Blocked on:** M01 draft part 1 (CodexPrime).

## 21 November 2026 (later)

- Recorded five sponsor decisions in plan 11 and on the board.
- ClaudeOracle acknowledged its lane (mailbox message 8). No reply from CodexPrime yet.
- Created the private directory outside the checkout.
- Mailbox cursor: last read message 8.
- **Blocked on:** CodexPrime's review of plan 11 and M01 draft part 1.

## 21 November 2026

- Took over project management at the sponsor's request. Wrote plan 11 (lanes, custody, working rules, route to M01 sign-off) and the status board.
- Assigned CodexPrime the review of plan 11 and M01 draft part 1; told ClaudeOracle to stand by. Both by mailbox.
- Mailbox: added the `oracle` address in `learning_mcp` (commit `5fd2582` there); round trips with CodexPrime and ClaudeOracle confirmed.
- **Blocked on:** CodexPrime's M01 draft part 1 before the census can start; four sponsor decisions listed on the board.
