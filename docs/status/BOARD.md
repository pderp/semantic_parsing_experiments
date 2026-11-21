# Status board

Maintained by ClaudeScope. Lanes and rules: [plan 11](../plans/11_management_claude.md). Per-agent logs are beside this file.

**Last updated:** 21 November 2026.

## Where the project is

| Milestone | State | Evidence |
| --- | --- | --- |
| Scope spike | Passed (13 checks) | `spike/README.md`, commit `5749166` |
| Plans 00–09 | Converged; plan 09 signed off | `docs/plans/10_review_claude.md` |
| M01 contract freeze | **In progress** — draft part 1 assigned to CodexPrime | plan 11, steps 1–9 |
| Family census | Waiting on M01 draft part 1 | — |
| M02 onward | Not started | — |

## Open assignments

| # | Owner | Task | State |
| --- | --- | --- | --- |
| 1 | CodexPrime | Review plan 11 (file `12`) | **Done**, `bb53fc9`; all six points accepted into plan 11 |
| 2 | CodexPrime | M01 draft part 1: `spec/contract.md`, `spec/ontology.yaml` | Draft `6482eec` reviewed in file `13`; revision to `seed-0.2-draft` requested |
| 5 | CodexPrime, ClaudeOracle | Sentinel access test | CodexPrime: **readable** (held-out data is procedurally separated only). ClaudeOracle: no reply yet |
| 3 | ClaudeOracle | Stand by for the frozen contract and fixtures | Acknowledged 21 Nov |
| 4 | ClaudeScope | Private generator and census | Generator in progress; census waits for `seed-0.2-draft` |

## Sponsor decisions

Recorded in plan 11: runtime comparison conditional; sponsor does all reading for now; private directory confirmed; ClaudeScope pushes after each commit; GPU work on a remote machine, set up after sign-off.

Two-stage sign-off confirmed by the sponsor on 21 November.

**Still open:** teacher model, credentials, spending limit, and a pilot operator, needed for stage 2 only.

## Known issues

- **Only four families can produce two readings** under the draft contract (review 13, item 2). Each transfer panel's two-reading stratum would be one family. Decision after the census.
- **CodexPrime can read the private directory.** Separation between grammar author and evaluator is by procedure, not by access control. Stronger separation needs a separate Unix account or machine for the evaluator.

- `gh` cannot write to this repository or see `peep-sys/learning_mcp`; pushes go over SSH.
- The mailbox cannot wake an idle session. The sponsor prompts an idle agent to check its inbox.
