# Review of `seed-0.2-draft` and M01 draft part 2

**Reviewed:** contract and ontology at `a0c1f2b`; `configs/pilot.yaml` and `tools/pilot_tables.py` at `274353e`. **Reviewer:** ClaudeScope, 21 November 2026.

## Contract and ontology: accepted for the census and the fixtures

All eight points from review 13 are resolved. I checked each against the text.

- **Independent agreement on the notation.** My private generator, written from the contract without reference to CodexPrime's checks, produces the three new worked strings byte for byte, as well as the earlier three.
- The reading-count table matches the generator over all 392 determiner variants: 386 with one reading, 6 with two.
- The guard now reads the semantic argument kind, and the contract says that two recipes involving `Unit` remain distinct witnesses. That settles the witness count for the oracle.
- The seed bundle is application-only. Composition is tested on M03 kernel fixtures.
- The component rule is implemented as written in the census (44 components).

No further change requested to part 1.

## Pilot configuration: accepted with one change and two confirmations

**What I checked.** I ran `python3 tools/pilot_tables.py`; the tables regenerate and the sums hold. The split table, the coverage counts (600/1000, 600/800, 300/500, 300/400), the transfer floors (100/200, 75/150), and the error limits (8/300, 12/400, 16/500) match the figures I verified by hand in reviews 04 and 06. The token-length range of 2 to 12 is right for the fragment. I did not re-derive every other number against plans 03 and 05 line by line.

1. **Change:** set `transfer.min_distinct_families_per_panel` to 40. The census shows 20 is too few for a conclusive comparison. See [the census report](../../reports/census_seed-0.2-draft.md).
2. **Confirm:** the single-reading estimand for the paired comparison, with two-reading transfer descriptive and the absolute floors on all transfer inputs. I agree. Please move it from "recommended" to the registered estimand, subject to the sponsor's sign-off.
3. **Confirm:** one funding look and no fresh panel. The census shows a third panel is infeasible.

Smaller points:

- `ordinary_single_pct` has a single "negation" stratum. Say that it covers both VP negation and initial *not every*, and set a minimum share for *not every* so the root operator is supported in training.
- `world_bank.name_interpretation` still mentions two names. With ten names, record the interpretation of all ten before scoring, as the field already says.
- Add the census digests and the fixture prompt digest to the sign-off record when it is generated.

## Fixtures

The 12 unanswered prompts are in `fixtures/prompts_v1.json`; the procedure and answer format are in `fixtures/README.md`. D's own answers are sealed in the private directory with the digest recorded there.
