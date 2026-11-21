# Status board

Maintained by ClaudeScope. Lanes and rules: [plan 11](../plans/11_management_claude.md). Per-agent logs are beside this file.

**Last updated:** 21 November 2026.

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
| M06–M08 grammar, reference parser, oracle | CodexPrime reports a first reference parser (`4b5f637`) matching the 12 fixtures and the oracle on 392 variants; **not yet reviewed by ClaudeScope**. Witness-key answers in `spec/witness-v1.md` | messages 49, 51 |
| M04–M05 controlled corpus | **Dry run passes all 26 audit checks; not released.** Found: the language has *a* but no *an* (876 of 6,000 sentences affected) | `reports/corpus_dryrun1.md` |
| Stage 2 (bulk annotation) | Not started; needs teacher access, budget, operator | plan 11 |

## Open assignments

| # | Owner | Task | State |
| --- | --- | --- | --- |
| 10 | **Sponsor** | Approve or amend the five items in `reports/stage1_signoff.md` | **Approved** |
| 11 | **Sponsor** | Say whether the design author's `semantic_reference_checks.py`, its result file, and the LaTeX source can be supplied | Open |
| 12 | CodexPrime | Review the sign-off record; pin the reconciled fixture digest; specify the guard mechanism and resolve the oracle's 15 points on witness keys; seed lexicon (M06) and reference parser (M07) with the reconciled fixtures as first target | Sent 21 Nov |
| 13 | ClaudeOracle | Exhaustive enumerator | **Done**: `oracle/`, self-test passes, reading sets match the generator on all 392 variants; 15 underspecified contract points filed in `reports/oracle_underspecified_v1.md` |
| 14 | ClaudeScope | Reserve panels; pre-score bootstrap check | **Done** |
| 15 | ClaudeScope | Controlled corpus | Dry run done; regenerate and release after the *a/an* decision. Then: review the reference parser; shared finite-world evaluator and world bank |
| 17 | **Sponsor** | Approve protocol change `seed-1.1`: add *an* before vowel-initial nouns (recommended) | Open |
| 18 | CodexPrime | Draft `seed-1.1` (*an*) in contract, ontology, lexicon; send ClaudeOracle's bundle inputs | Sent 21 Nov |
| 16 | **Sponsor** | For stage 2: choose the teacher model, give API access and a spending ceiling, name who runs the 100-input pilot | Open, not yet blocking |

## Sponsor decisions

Recorded in plan 11: runtime comparison conditional; sponsor does all reading for now; private directory confirmed; ClaudeScope pushes after each commit; GPU work on a remote machine, set up after sign-off.

Two-stage sign-off confirmed by the sponsor on 21 November.

**Still open:** teacher model, credentials, spending limit, and a pilot operator, needed for stage 2 only.

## Known issues

- **The neural comparison is weakly powered.** With 20 families per panel it would almost always be inconclusive; the census recommends 40. Even then it can only confirm a grammar that is ahead (census report).
- **Only four families can produce two readings.** Each transfer panel holds one; two-reading transfer is reported descriptively.
- **CodexPrime and ClaudeOracle can both read the private directory.** Separation between grammar author and evaluator is by procedure, not by access control. Stronger separation needs a separate Unix account or machine for the evaluator.

- `gh` cannot write to this repository or see `peep-sys/learning_mcp`; pushes go over SSH.
- The mailbox cannot wake an idle session. The sponsor prompts an idle agent to check its inbox.
