# Review of `07codex_plan.md`

**Reviewed:** `docs/plans/07codex_plan.md` at commit `f4d4358`, against my third review (`06_review_claude.md`).

**Reviewer:** Claude (Fable 5.2), 19 November 2026. Nothing was run.

## Verdict

Plan 07 is ready. It adopts all four items from the third review and all four smaller ones, and I found no errors in its numbers or rules. There is nothing left that should be settled on paper before code exists.

**Build the spike next.** This is the fourth plan and the repository still contains no code. Further review of plans will return little until the spike and the family census produce facts to review.

## What plan 07 settled

| Item from the third review | Resolution |
| --- | --- |
| Transfer panel has few independent data points | Family census before any reservation; minimum of 20 families per panel; resampling by whole family; descriptive-only fallback. |
| Reading sets must follow from a public rule | Public scope policy per construction, tied to the design's Equations 16–17, 21, and 22; only the reserved combinations stay private. |
| No absolute floor on transfer | At least 100 of 200 at Decision 2 and 75 of 150 at release, as well as the relative margin. |
| No action for "inconclusive" | No adapter funding; one fresh panel only if reserved at sign-off, with 97.5% limits for two looks. |
| Smaller items | Notation reference published for the fixtures and pilot; closed vocabulary; reader step for disputed forms; D's effort estimated; one signed contract and configuration. |

## Two things to decide when the census runs

Neither needs a plan revision. Both belong in the census handoff.

### 1. Whether determiner choice makes a new family

The plan says a name, lemma, or inflection change keeps the family and that "the position of a quantifier" changes it. It does not say whether swapping *every* for *a* in the same position is a new family.

The answer decides the count. If determiner identity is structural, the seed fragment yields well over 60 families. If it is not, my estimate is 15 to 25, short of the 40 required. The first definition makes the minimum easy to meet with families that differ only slightly, and such families tend to pass or fail together, which weakens the independence the interval relies on.

**Suggestion:** fix the definition in the public contract before D counts. Report the count both ways.

### 2. The likely outcome is that adapters are not funded in this pilot

If the census falls short, transfer becomes descriptive and adapter work stays unfunded. If it passes, adapters still require a 50% transfer yield, a conclusive comparison with the neural model, and the coverage, accuracy, and CPU gates.

That is a defensible position. The design document, though, is largely about comparing MORK/MM2, PeTTa, and CeTTa, and this protocol makes it probable that the pilot ends before any of them is run. Whoever sponsors the runtime comparison should know that now. If it must happen regardless, the option is to widen the seed fragment before the pilot so that more families exist, at the cost of a longer M06.
