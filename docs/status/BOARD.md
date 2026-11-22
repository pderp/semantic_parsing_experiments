# Status board

Maintained by ClaudeScope. Lanes and rules: [plan 11](../plans/11_management_claude.md). Per-agent logs are beside this file.

**Last updated:** 22 November 2026.

## Where the project is

| Milestone | State | Evidence |
| --- | --- | --- |
| Scope spike | Passed | `spike/README.md` |
| M01 contract, ontology, pilot configuration | Reviewed and accepted by both planners | reviews `13`–`15` |
| Family census | Done and reviewed | `reports/census_seed-0.2-draft.md` |
| Independent fixtures | **Reconciled.** Three formal specifiers agree on all 12; the sponsor's reading differs on 4 of 10 | `reports/fixtures_v1_reconciliation.md` |
| **Stage 1 sign-off** | **Approved by the sponsor, 21 November 2026.** Panels reserved (manifest digest in the record). Promotion of version strings to `seed-1.0` requested from CodexPrime | `reports/stage1_signoff.md` |
| Pre-score bootstrap check | Done: false-pass 6–8% (nominal 5%), 91–99% pass with a 20-point lead | `reports/prescore_check.md` |
| M02 semantic core | Accepted; normalizer cross-checked on 3,400 terms with zero mismatches | review `16` |
| M03 checked DSL | First kernel accepted; guard mechanism to be specified | review `16` |
| M06–M08 grammar, reference parser, oracle | Reference parser reviewed and accepted (review `17`). **M07–M08 gate met for `seed-1.0`** (`ee5bd76`, reviewed in `18`): all 181 of ClaudeOracle's frozen cases and 138 ranked witness keys match after three reference-parser fixes. To be repeated on the `seed-1.1` cases | `reports/m07_m08_witness_gate.md` |
| World bank and shared evaluator | Candidate revised by CodexPrime (`d4ea4dc`) after ClaudeScope's measurement: indistinguishable scope pairs fell from 14 to 0 of 317 on training sentences and from 323 to 0 of 6,400 on a full grid. Blind packet delivered to ClaudeOracle for an independent check; not yet frozen | `spec/world-bank.md` |
| Stage 2 pilot | **Teacher matches D's targets on 200 of 200 sentences** (240 of 240 readings) across two batches; the second batch's targets were never public. Tokenizer check not done | `reports/stage2_pilot_teacher.md` |
| M04–M05 controlled corpus | **Version 1 generated under `seed-1.1` and released**: 4,000 training inputs, 800 ordinary development inputs, 100 pilot targets. 26 of 26 audit checks pass | `reports/corpus_v1.md` |
| Stage 2 (bulk annotation) | Not started; needs teacher access, budget, operator | plan 11 |

## Open assignments

| # | Owner | Task | State |
| --- | --- | --- | --- |
| 10 | **Sponsor** | Approve or amend the five items in `reports/stage1_signoff.md` | **Approved** |
| 11 | **Sponsor** | Design author's checker, result file, LaTeX source | **Received** in `docs/pre/` (`cb37eff`). ClaudeScope re-ran the checker: 39 of 39 pass, output byte-identical to the recorded result |
| 12 | CodexPrime | Review the sign-off record; pin the reconciled fixture digest; specify the guard mechanism and resolve the oracle's 15 points on witness keys; seed lexicon (M06) and reference parser (M07) with the reconciled fixtures as first target | Sent 21 Nov |
| 13 | ClaudeOracle | Exhaustive enumerator | **Done**: `oracle/`, self-test passes, reading sets match the generator on all 392 variants; 15 underspecified contract points filed in `reports/oracle_underspecified_v1.md` |
| 14 | ClaudeScope | Reserve panels; pre-score bootstrap check | **Done** |
| 15 | ClaudeScope | Controlled corpus | **Released** (`reports/corpus_v1.md`). Next: shared finite-world evaluator and world bank |
| 17 | **Sponsor** | Protocol change `seed-1.1` (*an*) | **Approved** |
| 18 | CodexPrime | Draft `seed-1.1` (*an*) | **Done** at `3b683f0` |
| 24 | CodexPrime | M07–M08 gate: run the reference parser on ClaudeOracle's 181 frozen cases (`oracle/cases_witness_v1.json`), report every mismatch, resolve the open conventions in `reports/oracle_underspecified_v2.md` | Sent 22 Nov |
| 19 | **Sponsor** | Natural-text survey brought forward; PLOS ONE fetch | **Approved** |
| 21 | ClaudeScope | Natural-text survey | **Done**: 0 of 200 sentences parse; 6% of words in vocabulary; median 8 missing construction types per sentence (`reports/natural_survey_v1.md`). 300-sentence development sample sealed, not inspected |
| 22 | CodexPrime | Survey review; reconciliation of the author's 39 checks | **Done** (`179f77c`, `b0dfaf2`): 39 of 39 replay; earlier suite covered 10, partly covered 16, missed 12; gaps now tested |
| 25 | ClaudeScope | Scoring tool and submission format | **Done and revised** after CodexPrime's review (`reports/scoring_review_codex.md`): inadmissible rows counted and never credited; per-family counts under opaque labels; one opening per reserved panel unless a repeat is authorized |
| 26 | CodexPrime | World bank and shared finite-model evaluator for `seed-1.1` (plan 05: 256 worlds), after the M07–M08 gate | Sent 22 Nov |
| 23 | **Sponsor** | Natural-text option | **(a) approved**: controlled pilot is the deliverable; natural text reported as a measured gap |
| 20 | ClaudeOracle | Frozen cases | **Done**: 181 cases (`seed-1.0`) and 80 cases (`seed-1.1`), in `oracle/`. Now: blind world-bank check and confirmation of witness revision 2 (`inbox_v4/`) |
| 27 | CodexPrime | Repeat the witness gate on the 80 `seed-1.1` cases; reply on training the neural model on D's targets | Sent 22 Nov |
| 28 | **Sponsor** | Decide whether bulk teacher annotation is still wanted, given 200 of 200 agreement (see `reports/stage2_pilot_teacher.md`) | Open |
| 16 | **Sponsor** | Stage 2 teacher | Pilot teacher chosen: a fresh Codex session ("CodexTeacher"), instructed by ClaudeScope. Teacher and budget for any bulk run still to be decided after the pilot |

## Sponsor decisions

Recorded in plan 11: runtime comparison conditional; sponsor does all reading for now; private directory confirmed; ClaudeScope pushes after each commit; GPU work on a remote machine, set up after sign-off.

Two-stage sign-off confirmed by the sponsor on 21 November.

**Still open:** teacher model, credentials, spending limit, and a pilot operator, needed for stage 2 only.

## Known issues

- **Natural text is far out of reach of the seed grammar** (survey v1). M13 as planned would report coverage near zero.
- **The design PDF in use differs from the author's manifest.** The manifest lists a 575,223-byte PDF with SHA-256 `f94cd589…`; the PDF the plans cite is 725,632 bytes with SHA-256 `ce8f4717…`. Both say version 1.1, 18 November 2026. The LaTeX source and checker match the manifest.

- **The grammar's controlled results are 100% by construction** (review 17). The controlled pilot's gates cannot fail for the grammar; the informative results are the neural shortfall on held-out families, teacher agreement, serving cost, and natural text. Recommendation: bring the natural-text survey forward.

- **The neural comparison is weakly powered.** With 20 families per panel it would almost always be inconclusive; the census recommends 40. Even then it can only confirm a grammar that is ahead (census report).
- **Only four families can produce two readings.** Each transfer panel holds one; two-reading transfer is reported descriptively.
- **CodexPrime and ClaudeOracle can both read the private directory.** Separation between grammar author and evaluator is by procedure, not by access control. Stronger separation needs a separate Unix account or machine for the evaluator.

- `gh` cannot write to this repository or see `peep-sys/learning_mcp`; pushes go over SSH.
- The mailbox cannot wake an idle session. The sponsor prompts an idle agent to check its inbox.
