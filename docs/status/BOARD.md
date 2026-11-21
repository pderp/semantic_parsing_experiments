# Status board

Maintained by ClaudeScope. Lanes and rules: [plan 11](../plans/11_management_claude.md). Per-agent logs are beside this file.

**Last updated:** 21 November 2026.

## Where the project is

| Milestone | State | Evidence |
| --- | --- | --- |
| Scope spike | Passed (13 checks) | `spike/README.md` |
| M01 part 1: contract and ontology | `seed-0.2-draft` accepted by ClaudeScope | reviews `13`, `14` |
| M01 part 2: pilot configuration | 40 families per panel, single-reading estimand, one look registered (`f2f5e45`) | review `14`, review `15` |
| Family census | **Done and reviewed**; power table corrected after review 15 | `reports/census_seed-0.2-draft.md` |
| Independent fixtures | CodexPrime, ClaudeOracle, and D **agree on all 12** (status, decision, and every canonical string, byte for byte). Sponsor worksheet half done; originals stay unpublished until it is finished | `fixtures/README.md` |
| Sentinel access test | Done: private directory readable by both other sessions | messages 14, 18 |
| Stage 1 sign-off | Waiting on fixtures, reconciliation, CodexPrime's review of the census | plan 11 |
| Stage 2 (bulk annotation) | Not started; needs teacher access, budget, operator | plan 11 |

## Open assignments

| # | Owner | Task | State |
| --- | --- | --- | --- |
| 6 | **Sponsor** | Fill in `fixtures/sponsor_worksheet.md` (30–45 minutes), before discussing the sentences with any agent | Open |
| 7 | CodexPrime | Fixture answers; census review; pilot changes | **Done** (`4ee97d3`, `bebd347`, `f2f5e45`). Remaining: re-pin the corrected census report hash |
| 8 | ClaudeOracle | Fixture answers | **Done**, SHA-256 `32d39a42…`; wrote its own `oracle.py` from the contract |
| 9 | ClaudeScope | Publish originals and reconciliation; draft the stage 1 sign-off record | Waiting on 6 |

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
