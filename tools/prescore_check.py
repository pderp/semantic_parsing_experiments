#!/usr/bin/env python3
"""Pre-score check of the paired transfer comparison (review 15).

Synthetic paired rows at the registered integer panel sizes; whole-family
percentile bootstrap with the registered quantile rule (rank ceil(p*B),
one-based). No reserved panel or real output is read. Standard library only.

    python3 tools/prescore_check.py [--trials 600] [--replicates 1000]

The registered analysis uses 20,000 replicates; this check uses fewer to stay
fast in pure Python, which adds a little noise to each simulated limit.
"""
import argparse
import math
import random

MARGIN = 0.10
PANELS = {"development": [4] * 35 + [5] * 4, "locked": [3] * 36 + [4] * 3}


def trial(rng, sizes, s, t, rho, partial, replicates):
    """One synthetic panel. Returns (decision, degenerate)."""
    # Symbolic family state: full success, partial (each row 0.5), or failure.
    full = s - 0.5 * partial
    # Neural family is easy (row 0.95) or hard (row 0.05). With probability rho
    # it copies the symbolic state (partial copies as a coin flip).
    p_easy_target = (t - 0.05) / 0.90
    q = (p_easy_target - rho * s) / (1 - rho) if rho < 1 else s
    if not 0 <= q <= 1:
        raise ValueError("scenario not representable")
    d, n = [], []
    for size in sizes:
        u = rng.random()
        state = "full" if u < full else "partial" if u < full + partial else "fail"
        p_row = {"full": 1.0, "partial": 0.5, "fail": 0.0}[state]
        if rng.random() < rho:
            easy = rng.random() < p_row
        else:
            easy = rng.random() < q
        sym = sum(rng.random() < p_row for _ in range(size))
        neu = sum(rng.random() < (0.95 if easy else 0.05) for _ in range(size))
        d.append(neu - sym)
        n.append(size)
    fams = len(sizes)
    stats = []
    for _ in range(replicates):
        td = tn = 0
        for _ in range(fams):
            i = int(rng.random() * fams)
            td += d[i]
            tn += n[i]
        stats.append(td / tn)
    stats.sort()
    upper = stats[math.ceil(0.95 * replicates) - 1]
    lower = stats[math.ceil(0.05 * replicates) - 1]
    degenerate = stats[0] == stats[-1]
    if upper < MARGIN:
        return "pass", degenerate
    if lower >= MARGIN:
        return "fail", degenerate
    return "inconclusive", degenerate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=600)
    ap.add_argument("--replicates", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=20261125)
    a = ap.parse_args()
    print(f"seed {a.seed}, trials {a.trials}, replicates {a.replicates}, margin +{MARGIN:.0%}")
    print(f"Monte Carlo 95% error on a rate near 50%: +/-{196 * math.sqrt(0.25 / a.trials):.1f} points")
    print("panel        sym  neu  shared partial   pass  inconcl  fail  degenerate")
    scenarios = [(0.6, 0.7), (0.6, 0.6), (0.8, 0.8), (0.8, 0.6)]
    for panel, sizes in PANELS.items():
        for s, t in scenarios:
            for rho in (0.0, 0.5):
                for partial in (0.0, 0.2):
                    if panel == "locked" and (rho or partial):
                        continue
                    rng = random.Random(f"{a.seed}/{panel}/{s}/{t}/{rho}/{partial}")
                    out = {"pass": 0, "inconclusive": 0, "fail": 0}
                    deg = 0
                    for _ in range(a.trials):
                        decision, degenerate = trial(rng, sizes, s, t, rho, partial, a.replicates)
                        out[decision] += 1
                        deg += degenerate
                    r = lambda k: f"{out[k] / a.trials:5.0%}"
                    print(f"{panel:11s}  {s:.1f}  {t:.1f}  {rho:.1f}    {partial:.1f}     "
                          f"{r('pass')}  {r('inconclusive')}   {r('fail')}  {deg / a.trials:5.1%}", flush=True)


if __name__ == "__main__":
    main()
