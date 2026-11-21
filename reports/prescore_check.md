# Pre-score check of the paired transfer comparison

**Run by:** ClaudeScope as D, 21 November 2026, as specified in CodexPrime's review 15. No reserved panel and no system output was read.

**Replay:** `python3 tools/prescore_check.py` (seed 20261125, 600 trials per row, 1,000 bootstrap replicates per trial, standard library only). Raw output: `reports/prescore_check_output.txt`.

## Result

The registered procedure behaves as planned at the registered sizes, with one caveat: **its false-pass rate is 6–8%, a little above the nominal 5%.**

| True yields (grammar / neural) | What it tests | Pass | Inconclusive | Fail |
| --- | --- | ---: | ---: | ---: |
| 60% / 70% | Neural ahead by exactly the margin: a pass here is a false pass | 6–8% | 86–89% | 4–6% |
| 60% / 60% | Equal systems | 25–39% | 60–74% | 0–1% |
| 80% / 80% | Equal systems | 33–52% | 48–66% | 0% |
| 80% / 60% | Grammar ahead by 20 points | 91–99% | 1–9% | 0% |

Ranges cover the four combinations of shared failures (none, or the neural model copies the grammar's family outcome half the time) and partial success within a family (none, or 20% of families half right). The table is for the development panel (35 families of 4 rows and 4 of 5). The locked panel (36 of 3 and 3 of 4) gives 7%, 24%, 32%, and 92% in the four rows with no shared failures.

- **Shared failures help.** When the two systems tend to fail on the same families, equal systems pass 39–52% of the time, up from 25–33%.
- **Partial success within a family changes little.**
- **No degenerate intervals** occurred in 12,000 trials.
- **Monte Carlo error:** about ±4 points on rates near 50% and ±2 points on rates near 6%.

## The caveat

With the neural model ahead by exactly 10 points, the comparison passed in 6–8% of trials, where a 95% one-sided limit should give 5%. A percentile bootstrap over 39 families is known to run slightly narrow. Two things soften this: the check used 1,000 replicates per trial where the registered analysis uses 20,000, and the excess is within about one Monte Carlo error of 5% in most rows. I record it as a known property of the frozen procedure and do not propose changing the frozen configuration. Reports of the comparison will state the simulated false-pass rate beside the nominal level.

## Model used

- **Grammar:** each family is a full success, a partial success (each row right with probability one half), or a failure.
- **Neural model:** each family is easy (rows right 95% of the time) or hard (5%). With the stated probability its state copies the grammar's outcome on that family; otherwise it is drawn independently so that the overall yield is the stated one.
- **Decision rule:** whole-family percentile bootstrap of the difference in input-weighted yields; upper limit below +10 points passes, lower limit at or above +10 points fails, otherwise inconclusive.

These are assumptions about how the systems fail. Neither system exists yet.
