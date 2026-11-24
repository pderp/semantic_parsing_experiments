# ClaudeScope status log

Newest first.

## 24 November 2026 (ClaudeTrainer online)

- ClaudeTrainer sent "trainer online" (message 113). Sent its first assignment (message to `trainer`): environment report, key set-up with the sponsor, model shortlist, teacher script with cache and replay; hard rules on the public pilot answers and on never repairing labels. Lane C assigned in plan 11.
- Re-ran the revision 2 witness supplement: 111 of 111. Pushed CodexPrime's `8624810` and `6150dd2` earlier.
- World bank v2 awaits ClaudeOracle's sealed answers and verdict.
- Mailbox cursor: last read message 113.

## 22 November 2026 (supervision decision; remote agent)

- Sponsor chose the original plan: neural baseline trained on teacher labels, teacher is a non-frontier API model, work on a remote GPU machine. Recorded in plan 11 with consequences.
- Wrote the remote set-up guide (mailbox over SSH with a forced-command key); moved it to the mailbox repository at the sponsor's direction, since connection details do not belong in this repository. Added a `trainer` address to the relay (uncommitted in `learning_mcp`).
- Delivered world bank v2 blind packet to ClaudeOracle (`inbox_v5`); integrated its 111 revision 2 cases (`7c15ed4`).
- Mailbox cursor: last read message 105.

## 22 November 2026 (world-bank check; seed-1.1 gate)

- ClaudeOracle sealed its blind world-bank answers; I compared them with the shared evaluator: 52 of 52 equal. Its design review found a real gap (quantified embedded objects invisible). Report and requests: `reports/world_bank_check_v1.md`. Bank not frozen.
- Re-ran the `seed-1.1` witness gate: 80 of 80, 47 witnesses. Gate met for both protocol versions.
- CodexPrime supports the supervision amendment (message 97); it goes to the sponsor.
- Mailbox cursor: last read message 100.

## 22 November 2026 (confirmation batch; oracle seed-1.1; world-bank packet)

- Teacher batch 2 (private targets): 100 of 100, 120 of 120 readings. Report updated.
- Integrated ClaudeOracle's `seed-1.1` files (80 frozen cases). ClaudeOracle correctly declined a direct request from CodexPrime to read the shared tree.
- Verified CodexPrime's blind world-bank packet holds no expected values and delivered it to ClaudeOracle (`inbox_v4/`, message to `oracle`), with witness revision 2 for confirmation.
- CodexPrime revised the bank after my collision measurement (`d4ea4dc`): 14 of 317 down to 0.
- Mailbox cursor: last read message 91.

## 22 November 2026 (teacher pilot; gate review)

- CodexTeacher finished the 100 pilot sentences in about 5.5 minutes. Scored privately: 100 of 100 reading sets, 120 of 120 readings. Report: `reports/stage2_pilot_teacher.md`. Because the pilot targets are public, issued a confirmation batch of 100 training sentences with private targets (message 82 to `teacher`).
- Reviewed the M07–M08 gate: met for `seed-1.0` (`docs/plans/18_review_gate_claude.md`).
- Mailbox cursor: last read message 77.
- **Waiting on:** teacher batch 2; ClaudeOracle's `seed-1.1` cases and contrast-world check; CodexPrime's world-bank revision.

## 22 November 2026 (teacher set-up; scorer revision)

- Sponsor chose a fresh Codex session as pilot teacher. Prepared `/home/derp/sp/codex_teacher/` (contract, ontology, 100 inputs without targets, instructions: label by reading, no program, stay in the directory). Added a `teacher` mailbox address (`learning_mcp` commit `d882460`).
- Revised `tools/score.py` and `spec/submission.md` after CodexPrime's review (message 72): admissibility rules, per-family counts with opaque labels, single-opening rule with authorized repeats, system and targets digests in the ledger.
- First look at the candidate world bank: on the first 1,500 training sentences, 1,817 distinct readings give 1,740 distinct signatures; 36 collision groups are not explained by name aliases (some are true logical equivalences); 14 of 317 two-reading sentences have indistinguishable readings.
- Not yet reviewed: `reports/m07_m08_witness_gate.md`, witness-v1 revision 2.
- Mailbox cursor: last read message 77.

## 22 November 2026 (scorer; option a)

- Sponsor approved natural-text option (a). Recorded in plan 11.
- Wrote `spec/submission.md` and `tools/score.py`. Tested: reference parser scores 4,800 of 4,800 on training and ordinary development (accepted coverage 80% overall, 100% of single-reading rows, as the registered mixture implies); a deliberately degraded submission scores as constructed; a reserved panel cannot be scored without an explicit opening, ledger, and reason. No reserved panel has been opened.
- Read CodexPrime's messages 64–66: survey review and reconciliation of the author's 39 checks.
- Mailbox cursor: last read message 66.
- **Blocked on:** stage 2 inputs from the sponsor (teacher, budget, operator).

## 22 November 2026 (natural text; author files)

- Sponsor approved `seed-1.1` (*an*) and the natural-text survey; CodexPrime asked to draft `seed-1.1` (message 58).
- Natural-text survey done: `reports/natural_survey_v1.md`, `data/natural/`, tools `natural_snapshot.py` and `natural_survey.py`. 0 of 200 parse. Development sample (300) sealed privately, not inspected.
- Design author's files arrived in `docs/pre/`. Hashes of the three files match the author's manifest. Re-ran the checker under Python 3.14 in an empty directory: 39 of 39 pass, output byte-identical to `semantic_checks_result.json`. The PDF we hold does not match the manifest's PDF hash or size.
- `seed-1.1` arrived (`3b683f0`). Generator now reads the *a/an* rule from the ontology. Regenerated corpus v1: 26 of 26 audit checks; released training and ordinary development inputs and 100 pilot targets (`reports/corpus_v1.md`).
- Integrated ClaudeOracle's second deliverable (181 frozen cases, `oracle_witness.py`) and filed its remaining points (`reports/oracle_underspecified_v2.md`). Sent it `inbox_v3/` for `seed-1.1`.
- CodexPrime agrees with review 17 (message 57): controlled results have a design ceiling; keep every registered gate.
- Mailbox cursor: last read message 62.
- **Blocked on:** nothing. Next: shared finite-world evaluator and world bank; sponsor decisions on natural text and stage 2.

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
