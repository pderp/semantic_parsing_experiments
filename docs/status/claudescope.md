# ClaudeScope status log

Newest first.

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
