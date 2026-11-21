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
| 1 | CodexPrime | Review plan 11 (file `12`) | Sent 21 Nov, no reply yet |
| 2 | CodexPrime | M01 draft part 1: `spec/contract.md`, `spec/ontology.yaml` | Sent 21 Nov, no reply yet |
| 3 | ClaudeOracle | Stand by for the frozen contract and fixtures | Acknowledged 21 Nov |
| 4 | ClaudeScope | Review part 1, then private generator and census | Waiting on 2 |

## Sponsor decisions

Recorded in plan 11: runtime comparison conditional; sponsor does all reading for now; private directory confirmed; ClaudeScope pushes after each commit; GPU work on a remote machine, set up after sign-off.

**Still open:** teacher model, credentials, and spending limit (not needed before sign-off).

## Known issues

- `gh` cannot write to this repository or see `peep-sys/learning_mcp`; pushes go over SSH.
- The mailbox cannot wake an idle session. The sponsor prompts an idle agent to check its inbox.
