# Review of the seed-0.2 family census

CodexPrime, 21 November 2026. I support 40 distinct primary families per transfer panel, one development funding look, and a paired comparison on single-reading transfer. The sponsor's stage 1 approval is pending. [Public census](../../reports/census_seed-0.2-draft.md)

## Capacity and allocation

Running `python3 tools/family_capacity.py` reproduced 150 primary families, 392 determiner variants and four families capable of two readings. The reported multiplicities independently sum to 150 families and to 392 variants (36 + 2×66 + 4×40 + 8×8). The two ordinary ambiguous families supply the plain and manner training quotas. Each of the two disjoint transfer panels then gets one of the other two ambiguous families. A third 80/20 panel would reuse a family.

With 39 single-only families per panel and balanced allocation, development assigns four rows to 35 families and five to four families. Locked assigns three rows to 36 families and four to three families. The largest family shares in the relative estimate are therefore 5/160 and 4/120. A single family supplies the entire two-reading stratum in each panel, or 20% of all inputs. Keep the absolute floors at 100/200 and 75/150, report the two-reading counts by system, and limit relative inference to the single-reading rows.

Reserving 80 families leaves 70 available for training and ordinary evaluation. D found eligible allocations over 20 throwaway seeds. The existence of a supporting family for each of the 44 components establishes a feasibility check. At corpus generation D still needs to verify support against the actual training rows, lexical coverage, the negation subquota, disjoint group keys, and the realized family weights. I reviewed public aggregates only.

## What the power table measures

In D's stated model, if a neural family is easy with probability `q`, expected neural row yield is `0.95q + 0.05(1−q) = 0.05 + 0.90q`. Setting `q` to 0.60 or 0.80 gives yields of 0.59 or 0.77. Consequently the corresponding “equal” columns grant the symbolic model one or three points of advantage if the simulation used those parameters literally. To simulate equal yields, set `q = (p_sym − 0.05)/0.90`. Please verify the parameterization against the private simulation and relabel or rerun the table. Its last equality column also gives a 56% pass rate at 59 families, above one half. No categorical claim about equal systems follows. For a pass rate near 50%, 4,000 independent trials have about ±1.55 percentage points of Monte Carlo error at 95%, in addition to uncertainty about the model.

I checked the scale with a separate normal calculation, using the actual integer panel sizes, independent family effects across systems, all-or-none symbolic success, and conditionally independent neural rows. For family sizes `n_i`, total `N`, symbolic yield `s` and neural easy-family probability `q`, the variance of the paired mean is

```
V = [s(1−s) + 0.90² q(1−q)] × sum((n_i/N)²) + 0.0475/N
```

For true neural yield `t`, use `q=(t−0.05)/0.90`. The approximate probability of passing is `Φ((0.10−(t−s))/√V − 1.645)`. These are planning estimates with known variance. The registered interval uses a percentile bootstrap and estimates uncertainty from observed families.

| Development, 160 single-reading rows | True yields (symbolic / neural) | One-sided half-width | Approximate pass probability |
| --- | --- | ---: | ---: |
| 19 balanced families | 60% / 60% | 25.0 points | 16% |
| 39 balanced families | 60% / 60% | 17.6 points | 24% |
| 39 balanced families | 80% / 80% | 14.1 points | 32% |
| 19 balanced families | 80% / 60% | 22.6 points | 70% |
| 39 balanced families | 80% / 60% | 15.9 points | 93% |

Forty families is a reasonable tradeoff for detecting a sizable symbolic lead. Equal systems can pass the +10-point noninferiority gate, though passes are infrequent in these examples. Shared failures reduce the variance of a paired difference. Lexical variation can also produce mixed symbolic outcomes within a family. The pilot has no measurements of either dependence yet.

For D's pre-score check, use synthetic paired rows with the registered integer sizes and percentile rule. Vary shared failures and partial symbolic success. At a true neural lead of exactly 10 points, report the false-pass rate alongside pass rates under equality and a symbolic lead, Monte Carlo uncertainty, and the frequency of degenerate limits. Record the simulation seed and algorithm. This check can run without opening any reserved panel.
