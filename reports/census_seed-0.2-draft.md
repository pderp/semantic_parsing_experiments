# Family census · `seed-0.2-draft`

**Run by:** ClaudeScope as D, 21 November 2026. **Status:** for CodexPrime's review. No panel has been reserved and no held-out data exists yet.

## Result

The fragment has enough families: 150 primary families, far above the 40 needed. Two findings change the plan:

1. **Twenty families per panel is too few.** With 20 families the paired comparison with the neural model passes only about 70% of the time even when the grammar leads by 20 points. I recommend **40 families per panel**.
2. **Each panel can hold only one two-reading family**, and no third panel is possible under the 80/20 mixture.

## Inputs

| Item | Value |
| --- | --- |
| Contract | `spec/contract.md`, SHA-256 `e15a49cf3861728f9e3f1412005272875d64ca9f48b6a295344549c4cbcdd5c1` |
| Ontology | `spec/ontology.yaml`, SHA-256 `eaa0e2477a6005f751187f4c234ec6586fe03f27be8bce1f8d25d910f43896ab` |
| Private generator | `gen.py` `28c809cd26eba3a1…`, `structures.py` `20106bd6beb7b5b2…`, `census.py` `01da2040f22b0f39…` (SHA-256 prefixes) |
| Public cross-check | `python3 tools/family_capacity.py` gives the same 150, 392, and 4 |

**Generator check.** The generator builds each reading from the sentence's construction tree, with no chart. It reproduces, byte for byte, all six public canonical strings: the two spike readings, *Alice left*, and the three worked regressions in the contract. *Alice did not leave* also matches the contract's rule.

## Counts

| Quantity | Count |
| --- | ---: |
| Primary families (determiner position and construction) | 150 |
| Secondary families (refined by determiner identities) | 392 |
| Primary families with single-reading sentences only | 146 |
| Primary families with two-reading sentences only | 0 |
| Primary families with both | 4 |
| Determiner variants with two readings | 6 of 392 |
| Components (attribute values and directly connected pairs) | 44 |

Variants per primary family: 36 families have 1, 66 have 2, 40 have 4, and 8 have 8.

| Root | Intransitive | Transitive | Subject control | Object control | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Ordinary | 4 | 8 | 24 | 24 | 60 |
| VP negation | 4 | 8 | 24 | 24 | 60 |
| Initial *not every* | 2 | 4 | 12 | 12 | 30 |

Control families are 120 of the 150. Distinct sentences per family: minimum 40, median 6,400, so no family is short of text.

The four two-reading families are the ordinary transitive and the *not every* transitive with two quantified arguments, each with and without *quickly*. Each also contains single-reading variants (like determiners).

## Allocation feasibility

`configs/pilot.yaml` puts both ordinary two-reading families (plain and with manner) in training. That leaves the two *not every* families: one for the development transfer panel and one for the locked panel.

I searched for two disjoint panels such that every one of the 44 components still occurs in a training family. The search used throwaway seeds; none of these allocations is kept.

| Families per panel | Supported allocation found | Training families left | Single rows per family (development / locked) |
| ---: | --- | ---: | --- |
| 20 | 20 of 20 seeds | 110 | 8.4 / 6.3 |
| 30 | 20 of 20 seeds | 90 | 5.5 / 4.1 |
| 40 | 20 of 20 seeds | 70 | 4.1 / 3.1 |
| 50 | 20 of 20 seeds | 50 | 3.3 / 2.4 |
| 60 | 20 of 20 seeds | 30 | 2.7 / 2.0 |

- **Largest family weight:** 20% in every case. It is the panel's single two-reading family, which carries all 40 (or 30) two-reading rows. A balanced single-reading family at 40 per panel weighs about 2%.
- **Fresh panel:** infeasible with an 80/20 mixture, because no two-reading family remains. `fresh_panel_reserved: false` is correct.
- **Not yet checked:** support is checked here at the family level. The contract requires it against actual training rows, which do not exist until the corpus is generated.

## Will the comparison be conclusive?

The gate passes when the one-sided 95% upper limit of (neural yield − symbolic yield) is below +10 points. A grammar parses all or none of a family, so the family is the unit of evidence.

I simulated the single-reading comparison. Assumptions: the grammar succeeds on a whole family with probability *p*<sub>sym</sub>; the neural model is "easy" or "hard" per family (row success 95% or 5%) with probability *p*<sub>neu</sub> of easy, independently of the grammar; equal family sizes; 4,000 trials; normal approximation to the whole-family bootstrap. These assumptions are mine and are not measurements.

| Single-reading families | Equal at 60% | Equal at 80% | Grammar ahead 70 v 60 | Ahead 80 v 60 | Ahead 90 v 60 | Neural ahead 70 v 60 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 19 | 18% | 23% | 40% | 70% | 93% | 5% |
| 29 | 23% | 28% | 54% | 84% | 99% | 6% |
| 39 | 24% | 33% | 61% | 92% | 100% | 6% |
| 49 | 28% | 37% | 69% | 96% | 100% | 5% |
| 59 | 31% | 42% | 76% | 98% | 100% | 5% |

Each cell is the chance of a pass; the figures are true yields (grammar v neural). Monte Carlo error is about ±1.5 points. At 19 families the half-width of the interval is 20 to 25 points, twice the margin. The last column is the false-pass rate when the neural model leads by exactly the margin; it sits at the nominal 5%. If the two systems tend to fail on the same families, pass rates rise; that dependence is unmeasured.

**Correction, 21 November 2026.** The first version of this table mislabelled its columns. Its parameter was the share of "easy" neural families, which gives neural yields of 59% and 77%, not 60% and 80%, so the "equal" columns favoured the grammar by one to three points. CodexPrime found this in [review 15](../docs/plans/15_review_census_codex.md). The table above is rerun with truly equal yields and agrees with CodexPrime's independent calculation (24%, 33%, and 93% at 39 families). The first version also said that no feasible panel size passes more often than not for equal systems; that was stated too strongly and is replaced below.

**Reading.** Equal systems pass in roughly a quarter to a third of cases at 39 families. The test mainly confirms a grammar that is ahead: at 40 families per panel a 20-point lead passes about 92% of the time, against 70% at 20 families.

## Recommendations

1. **Set `min_distinct_families_per_panel` to 40** (39 single-reading families and one two-reading family per panel). Training keeps 70 families. Development has about 4 single rows per family and locked about 3.
2. **Adopt the single-reading estimand** for the paired comparison, as `configs/pilot.yaml` proposes, and report two-reading transfer descriptively. The absolute floors stay on all transfer inputs.
3. **Say in the contract what the comparison can show:** a pass is likely only if the grammar leads on unseen combinations; "inconclusive" is the expected outcome for equal systems and means no adapter funding.
4. **One funding look, no fresh panel.**

## Not done

- No panel is reserved. Reservation happens at stage 1 sign-off, with a recorded seed.
- Support against actual training rows, duplicate and group controls, and mixture cells per construction quota are checked when the corpus is generated (M04–M05).
- The power figures use a normal approximation and assumed behaviour. The registered analysis is the whole-family bootstrap in `configs/pilot.yaml`. Before any scoring, D runs the check CodexPrime specified in review 15: synthetic paired rows at the registered integer sizes with the percentile rule, varying shared failures and partial symbolic success, with the seed recorded.
