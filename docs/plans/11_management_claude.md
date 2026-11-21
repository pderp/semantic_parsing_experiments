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

## Decisions needed from the sponsor

1. **Runtime comparison.** Plan 09 proposes that MORK/MM2, PeTTa, and CeTTa are run only if the pilot's gates pass. Accept that, or require the three-runtime comparison regardless (which means a wider seed fragment, a repeated census, and its own budget).
2. **Human readers.** Plans 03 and 05 call for readers blinded to system identity, an adjudicator, and a backup reader. Say how much of your own time is available and whether anyone else can read. If none, the fallback is agent readers in fresh sessions with the sponsor as final adjudicator, and the reports will say so.
3. **Spending.** The teacher (a frontier model through an API) and the neural baseline (up to 48 GPU-hours) need credentials, a budget, and hardware. Nothing is needed before M01 sign-off.
4. **Private directory.** Confirm `/home/derp/sp/private_eval/` as the one exception to "everything goes in the repository".
