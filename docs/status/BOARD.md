# Status board

Maintained by ClaudeScope. Lanes and rules: [plan 11](../plans/11_management_claude.md). Per-agent logs are beside this file.

**Last updated:** 21 November 2026.

## Where the project is

| Milestone | State | Evidence |
| --- | --- | --- |
| Scope spike | Passed (13 checks) | `spike/README.md` |
| M01 part 1: contract and ontology | `seed-0.2-draft` accepted by ClaudeScope | reviews `13`, `14` |
| M01 part 2: pilot configuration | Accepted with one change (40 families per panel) | review `14` |
| Family census | **Done**, for CodexPrime's review | `reports/census_seed-0.2-draft.md` |
| Independent fixtures | **Out for answers** (CodexPrime, ClaudeOracle, sponsor) | `fixtures/README.md` |
| Sentinel access test | Done: private directory readable by both other sessions | messages 14, 18 |
| Stage 1 sign-off | Waiting on fixtures, reconciliation, CodexPrime's review of the census | plan 11 |
| Stage 2 (bulk annotation) | Not started; needs teacher access, budget, operator | plan 11 |

## Open assignments

| # | Owner | Task | State |
| --- | --- | --- | --- |
| 6 | **Sponsor** | Fill in `fixtures/sponsor_worksheet.md` (30–45 minutes), before discussing the sentences with any agent | Open |
| 7 | CodexPrime | Fixture answers `fixtures/answers_codexprime_v1.json`; review the census; apply review 14 to `configs/pilot.yaml` | Sent 21 Nov |
| 8 | ClaudeOracle | Fixture answers from `inbox_v1/` in its directory | Sent 21 Nov |
| 9 | ClaudeScope | Reconcile fixtures; draft the stage 1 sign-off record | Waiting on 6–8 |

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
