# Plan 11 · management, lanes, and the route to M01 sign-off

**Author:** ClaudeScope (Claude Fable 5.2), 21 November 2026. **Status:** in force for lanes and logistics; open for CodexPrime's cross-review (file `12`).

The project sponsor has asked ClaudeScope to manage the project. Planning is done jointly with CodexPrime, and each of us reviews the other's work. This file assigns lanes, sets the working rules, and orders the work up to M01 sign-off. It changes no number or rule in plans 03, 05, 07, or 09.

## Who is who

| Name | Mailbox address | Session | Working directory |
| --- | --- | --- | --- |
| ClaudeScope | `claude` | Claude Code, manager | this repository |
| CodexPrime | `codex` | Codex CLI | this repository |
| ClaudeOracle | `oracle` | Claude Code, separate session | `/home/derp/sp/oracle_checker` (outside this checkout) |
| Sponsor | `human` | the person leading the project | — |

## Lanes

The letters are the roles from plan 03.

| Lane | Owner | Owns | Reviewed by |
| --- | --- | --- | --- |
| Management and integration | ClaudeScope | Lanes, status board, milestone gates, handoff records, merging ClaudeOracle's deliverables into this repository. | CodexPrime |
| A · contract, ontology, grammar | CodexPrime | `spec/contract.md`, `spec/ontology.yaml`, `configs/pilot.yaml`, public scope policy, normal-form definition, grammar and morphology (M06). | ClaudeScope |
| B (implementation) · reference parser | CodexPrime | Semantic core (M02), checked DSL (M03), Python packed reference parser (M07–08). | ClaudeScope |
| B (validation) · exhaustive oracle | ClaudeOracle | Tiny exhaustive enumerator built from the frozen contract and fixtures only; second independent reader for the 12 fixtures. | ClaudeScope integrates; discrepancies go to CodexPrime |
| D · generator, census, evaluator custody | ClaudeScope | Private generator, family census, split manifests, locked inputs and targets, evaluator. | CodexPrime reviews public aggregates and digests only |
| C · teacher cache and baselines | Unassigned until M01 is signed | Teacher cache, neural baseline, existing-symbolic baseline, development reports. | — |

**Why ClaudeScope takes D.** Plan 03 gives D to "the repository maintainer". D needs 5–10 engineering days of implementation (plan 07 §4), so it must be an agent. D must be independent of the grammar author, who is CodexPrime. ClaudeScope wrote the disposable spike and no part of the reference parser, so that independence holds.

**A conflict to keep visible.** ClaudeScope both reviews A's public work and holds D's private data. Reviews of the grammar must therefore never draw on reserved signatures or locked targets. Review comments cite only public files.

## Custody

- **Private material** (generator templates, reserved signatures, locked inputs and targets) lives outside this checkout, under `/home/derp/sp/private_eval/`. This repository receives aggregate counts, allocation feasibility, and manifest digests only.
- **ClaudeOracle does not read this checkout.** ClaudeScope copies the frozen contract and fixtures into ClaudeOracle's directory and copies its deliverables back under `oracle/`, recording the source digest in the commit.
- All sessions run under one Unix account, so these boundaries are procedural, as plan 03 already states. The sentinel access test at M01 exit records what each session can in fact read.

## Working rules

1. **Everything public goes in this repository:** plans, specifications, code, reports, and status logs.
2. **Commit to `main`.** No branches unless the sponsor asks. Commit only files in your own lane, by explicit path (`git commit --only -- <paths>`), because two sessions share one index.
3. **Numbered plan files continue the series.** Odd-numbered and even-numbered files are no longer tied to an author; the filename carries the author (`NN_topic_author.md`).
4. **Status logs.** Each agent appends to its own file, `docs/status/<agent>.md`, newest entry first: date, what was done, evidence location, what is blocked. ClaudeScope keeps `docs/status/BOARD.md` as the one-page summary.
5. **Mailbox.** Use `learning_mailbox` for handoffs and questions. A handoff message names the commit and the files. Decisions that need the sponsor go to `human` and are recorded on the board.
6. **Cross-review before a gate.** Nothing counts toward a milestone gate until the other planner has reviewed it in a committed file or mailbox message referenced from the board.
7. **Stdlib Python only** until the sponsor approves installing anything. The host has Python 3.14 and no pip, pytest, or cargo.

## Order of work to M01 sign-off

| Step | Owner | Deliverable | Depends on |
| --- | --- | --- | --- |
| 1 | CodexPrime | Review of this file (`12`). | — |
| 2 | CodexPrime | **M01 draft, part 1:** in `spec/contract.md`, the seed fragment (constructions, closed vocabulary, licensed frames), the family definition from plan 09, the public scope policy from plan 07 §2, and the normal form, answering the seven questions in `spike/README.md`. `spec/ontology.yaml` for the seed vocabulary. | — |
| 3 | ClaudeScope | Review of part 1. | 2 |
| 4 | ClaudeScope (D) | Private generator for the seed fragment; **family census** under both family counts; public census report. | 3 |
| 5 | CodexPrime | **M01 draft, part 2:** `configs/pilot.yaml` with every binding count, mixture, seed, threshold, budget, interval method, and number of looks from plans 03, 05, 07, and 09; a stdlib script that regenerates the tables and checks sums. | can run alongside 4 |
| 6 | ClaudeScope | Review of part 2; expected interval width at the census's family counts. | 4, 5 |
| 7 | CodexPrime and ClaudeOracle | 12 worked fixtures: each specifies expected meanings and both status axes independently; CodexPrime resolves disagreements into versioned examples. | 3 |
| 8 | ClaudeScope | Sentinel access test; M01 sign-off record with both file digests. | 4–7 |
| 9 | Sponsor | Sign-off. | 8 |

After sign-off: M02–M03 and M06–M08 (CodexPrime), the exhaustive oracle (ClaudeOracle), M04–M05 corpus (ClaudeScope as D), and assignment of lane C.

## Sponsor decisions, 21 November 2026

1. **Runtime comparison is conditional.** MORK/MM2, PeTTa, and CeTTa are run only if the pilot passes the gates in plan 07. The seed fragment is not widened for their sake.
2. **The sponsor does all reading for now** (fixture specification, blinded audits, adjudication). ClaudeScope prepares each reading task with explicit written instructions. The sponsor may later move some or all reading to agents; that change gets a dated entry here and a note in every affected report. With one human reader there is no second human reader or backup; ClaudeOracle remains the independent second specifier for the 12 fixtures.
3. **Private directory confirmed:** `/home/derp/sp/private_eval/`, the one exception to "everything goes in the repository".
4. **Pushing.** ClaudeScope pushes `main` after each commit. Other agents commit locally and ClaudeScope's push carries their commits.
5. **GPU work runs on another machine.** This host has no GPU. The sponsor will set up Claude or Codex sessions on a remote machine for the neural baseline. Proposed mailbox link: the remote client registers the mailbox as a command run over SSH (`ssh <this-host> /usr/bin/python3 /home/derp/sp/learning_mcp/relay.py serve <address>`), which carries the stdio connection without a tunnel or an open port. It needs a new mailbox address and an SSH key restricted to that command. To be set up when lane C is assigned, after M01 sign-off.

## Still open

- Teacher model, API credentials, and spending limit. Not needed before M01 sign-off.

## Changes accepted from CodexPrime's review (file 12), 21 November 2026

All six points in [review 12](12_review_codex.md) are accepted. They change the plan as follows.

1. **D's reviews of A.** A review comment by ClaudeScope must be reproducible from public material. ClaudeScope does not propose new public examples chosen for their resemblance to a reserved case. Private discrepancies go into the evaluator ledger in the private directory; A receives only the preregistered aggregates. If a private case has to be exposed for a fix, the exposure is recorded and that family is retired from later confirmation.
2. **Sentinel before held-out data.** No held-out material is stored until the dummy sentinel test has run from each author environment and the result is recorded on the board. Sentinel: `/home/derp/sp/private_eval/sentinel/SENTINEL.txt`, SHA-256 `f9196f27cdf884f6f1ab21b3ff8265c86cb2ac7c9ead2c7c2e008f2eb25b9132`. If an author session can read it, reports describe the holdout as *procedurally separated*, and the sponsor is told what stronger separation would need (a separate Unix account or machine for the evaluator).
3. **Blind fixture exchange.** Step 7 becomes: ClaudeScope sends the frozen contract, the ontology, and the 12 *unanswered* fixture prompts, with digests, to CodexPrime, ClaudeOracle, and the sponsor. Each records expected meanings and both status axes without seeing the others' answers or the spike's outputs. ClaudeScope collects all three, then they are exchanged and reconciled against the contract. Every original is kept.
4. **One human reader.** Reports state the number of human readers (one). Agent specification is reported separately from human adjudication. The 20% independent human second read in plan 05 is unavailable and is reported as such. Sponsor hours are estimated from measured judgments and reconciliation time.
5. **Two-stage sign-off (confirmed by the sponsor, 21 November 2026).**
   - **Stage 1, structural freeze:** contract, ontology, family definition, scope policy, normal form, pilot configuration, reconciled fixtures, sentinel result, census. This is enough to reserve panels.
   - **Stage 2, authorization for bulk annotation:** adds plan 05's 100-input pilot (teacher cost and conflicts, tokenizer round trip, reading time, distinct judgments). It needs a pilot operator, teacher access, and a capped budget. Bulk annotation waits for stage 2.
6. **Publication.** CodexPrime reviews D's public methodology, aggregates, feasibility, and digests. ClaudeScope's push carries CodexPrime's commits.

## Stage 1 approved, 21 November 2026

The sponsor approved all five items in `reports/stage1_signoff.md`: the frozen contract, ontology, and pilot configuration; 40 families per panel with one funding look and the single-reading comparison; one reading for control sentences; procedural separation of held-out data; one human reader. Later changes to any of these need a new protocol version with a recorded reason.

## Sponsor decisions after stage 1, 21 November 2026

1. **Protocol `seed-1.1` approved:** add the surface form *an* for the existential determiner before vowel-initial nouns. Reason: 876 of 6,000 sentences in corpus dry run 1 read "a editor" and the like (`reports/corpus_dryrun1.md`). No meaning, family, panel, or fixture changes.
2. **Natural-text survey brought forward** to run alongside M08, and fetching public PLOS ONE text approved. Reason: review 17 found that the grammar's controlled results are by construction, so natural text is the first measurement with an uncertain outcome. ClaudeScope runs it.
3. The sponsor has asked the design author for the original companion checker, its result file, and the LaTeX source.

## Sponsor decision on natural text, 22 November 2026

**Option (a) approved:** the controlled pilot remains the deliverable, and natural text is reported as a measured gap with its own denominator (`reports/natural_survey_v1.md`). CodexPrime's review (`reports/natural_survey_v1_review_codex.md`) recommends the same. Consequences:

- No grammar extension toward natural text is planned for this pilot. Options (b) and (c) are not started; (c) may be proposed later as a prespecified secondary slice.
- The sealed 300-sentence development sample is still measured once, at M13, as registered.
- Decision 2 keeps its registered criteria. No natural-text threshold is added.
- Reports present the controlled results (with the note that the grammar's are by construction), the neural shortfall, teacher agreement, serving cost, and natural coverage as separate findings.

## Sponsor decision on supervision, 22 November 2026

The sponsor was offered four options (ClaudeScope's and CodexPrime's recommendation was to train the neural baseline on D's targets) and chose **the original plan (B): the neural baseline is trained on teacher labels**, with these particulars:

- The teacher is a **non-frontier model called through an API**, for cost reasons. It is not the Codex session used in the 200-sentence pilot.
- The work runs on **another machine**, which has the GPU this host lacks. The sponsor sets up an agent there; it joins the mailbox as `trainer` (`docs/remote_agent_setup.md`).

Consequences recorded now:

1. **The pilot must be repeated for the actual teacher.** The 200 of 200 result belongs to a different, stronger model. Stage 2 authorization for the bulk run rests on a 100-sentence pilot with the chosen API model and prompt, including cost per call.
2. **Teacher errors are now expected,** and the plan's handling applies: conflicts with D's targets are counted, validated labels are distinguished from raw ones, and the training policy (which labels the neural model sees) is fixed before the bulk run.
3. **Lane C is assigned to the remote agent:** teacher prompt and cache, the bulk labelling, the tokenizer round-trip check, and the neural baseline.
4. **Reserved inputs.** Whether the teacher labels the reserved panels, and from which machine, is decided before any reserved sentence leaves this host.
