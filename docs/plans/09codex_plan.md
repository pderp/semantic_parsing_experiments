# Plan 09 · scope spike and family census

**The next implementation task is the two-day scope spike.** Claude’s 08 review found plan 07 ready to implement. This handoff settles how D will count families and what the sponsor can expect from the pilot. [Plan 07](07codex_plan.md) · [Claude’s 08 review](08_review_claude.md)

## First evidence to review

1. **Scope spike.** Parse *Every researcher reviewed a paper* into one packed root. Extract both normalized readings and a derivation witness for each. In a world with two researchers who each reviewed a different paper and no paper reviewed by both, the researcher-wide reading must be true and the paper-wide reading false. Reverse lexical insertion order and reproduce the readings and tie order. Hand off the replay command, outputs, and world, or the smallest failing example.
2. **Family census.** Before D enumerates any signatures, record the family definition below in the public M01 contract draft. Pin its revision and the seed fragment. D then runs the census on the private generator before reserving panel membership or commissioning bulk annotation.

## Count each structure once for the funding decision

Use **determiner position and construction** in the primary family key. Keep determiner identity on each example for deriving and scoring its meaning. For example, *Every researcher left* and *A researcher left* have different truth conditions. Both belong to the family with a quantified subject and an intransitive verb. A quantified object occupies a different structural position. Likewise, subject control and object control remain distinct because the selected controller changes. The unit for allocating panels and resampling outcomes is the primary family.

D computes both counts from the **same eligible signatures**. For the secondary count, refine each primary key by its ordered tuple of determiner identities. Publish the total under each definition, the number of primary families eligible for single-reading examples only, two-reading examples only, or both, and how many determiner-specific variants each primary family contributes. A family that can supply both reading strata counts once toward a panel’s minimum. Keep its variants together when allocating panels. This makes the sensitivity to determiner choice visible while preserving the structural transfer test.

In the census handoff, report whether D can allocate **20 disjoint primary families per panel** while meeting the development mixture (160 single, 40 ambiguous) and the locked mixture (120 single, 30 ambiguous). Report the largest family weight and whether component constructions remain represented in training. The two panels require at least 40 eligible primary families in total. Reserving the optional fresh panel requires at least 60. Totals alone do not establish a feasible allocation. Publish aggregate counts, allocation feasibility, and manifest digests. Keep reserved signatures private. The count ranges in review 08 are estimates pending this run.

## Sponsor decision before the pilot

The pilot can deliver the grammar-versus-neural comparison **without running MORK/MM2, PeTTa, or CeTTa**. If the census falls short, report descriptive transfer results and leave adapters unfunded. A feasible census allows the inferential test to proceed. Adapter investment still requires at least 100 correct reading sets on 200 development-transfer inputs, a conclusive pass against the neural margin, and the coverage, accuracy, parity, and CPU gates in plan 07. A failed or inconclusive result and any preregistered fresh-panel option follow that plan’s stop rules. [Decision 2 and the release criteria](07codex_plan.md)

The proposed default is a **conditional runtime comparison**. D records the sponsor’s expectation at M01 sign-off. If the sponsor requires a three-runtime comparison, surface that requirement before the pilot. Cost a wider M06 seed fragment with additional linguistic constructions, repeat the census under a versioned scope, and agree on the extra schedule before freezing the splits. A wider fragment can improve panel feasibility. An unconditional runtime deliverable also needs its own budget and authorization if the quality gates fail.

Bring the spike output, both census counts, a feasible allocation or documented shortfall, and the sponsor’s scope decision to the next review. At sign-off, record the binding rules in `spec/contract.md` and thresholds in `configs/pilot.yaml`.
