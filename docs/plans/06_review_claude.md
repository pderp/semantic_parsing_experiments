# Review of `05codex_plan.md`

**Reviewed:** `docs/plans/05codex_plan.md` at commit `4d3481f`, against `03codex_plan.md` and my second review (`04_review_claude.md`).

**Reviewer:** Claude (Fable 5.2), 19 November 2026. Nothing was run. I checked the split table and threshold arithmetic by hand; all of it is consistent.

## Verdict

Plan 05 adopts every point from the second review, and adopts them well. I recommend no further plan revision. Build the spike now and carry the four items below into the M01 sign-off, where they belong. A plan 07 would cost more than it returns: the spike has been specified identically three times and not yet run.

## What plan 05 settled

- **Generator independence.** D owns the generator, templates, reserved combinations, and intended meanings, with a sentinel access test.
- **Transfer as a co-primary result,** with an operational definition, disjoint development and locked signatures, and a one-shot development panel.
- **Ambiguity.** A fixed 80/20 mixture, a "correct ambiguous answer" outcome, set-valued answers for every system including the neural model, and coverage thresholds stated on single-reading inputs as well as overall.
- **Reader budget** computed from distinct outputs measured in the pilot.
- **Accuracy gate** stated as an allowed error count.
- **Tokenizer round-trip gate, control in the finite-model check, world-bank recipe, and a named natural-text source.**

## Carry into M01

### 1. The transfer panel has about as many data points as it has families

A grammar is deterministic. On an unseen combination it will usually parse every sentence of that signature or none of them. The 200 development-transfer inputs are therefore worth roughly as many independent observations as there are combination families, and the 150 locked ones likewise.

The seed fragment has few constructions: simple frames, manner, negation, two kinds of control, quantified subjects and objects, and scope. That gives perhaps 15 to 25 structurally distinct combinations in total. The plan needs two disjoint reserved sets, none seen in training, plus a fresh set for any later candidate.

With 8 families a ten-point margin cannot be resolved: one family is 12.5 points. The cluster-resampled interval will then span the margin and the decision will be "inconclusive" by construction.

**For M01:** before reserving anything, D enumerates the signature space and reports how many families each transfer panel can have. Set a minimum (I suggest 20 per panel). If the fragment cannot supply it, either widen the margin to what the family count can resolve or say in advance that the transfer comparison is descriptive only.

### 2. The reading set for a new combination must follow from a public rule

Outputs are scored against D's private "full set of licensed readings". For ordinary inputs the public contract fixes this. For transfer inputs it may not. *Every researcher did not leave* has one reading under the design's negation template and two in ordinary English. A doubly quantified control sentence has one reading under Equation 22 and arguably more.

If D decides these case by case in private, the transfer score measures whether the grammar author guessed D's choices. The plan also requires "exactly two" readings for ambiguous inputs, which presupposes such a rule.

**For M01:** the public scope policy states the reading set compositionally, for example which pairs of quantified arguments permute and how negation and control fix order. Only the list of reserved combinations stays private. A reader should be able to derive any locked item's reading set from the public policy alone.

### 3. Transfer needs an absolute floor

The transfer gate is relative: proceed if the neural model is not more than ten points ahead. If both systems score near zero on transfer, the gate passes. The coverage gate does not catch this either. A grammar with zero transfer coverage reaches 600 of 800 single-reading inputs by accepting 600 of the 640 ordinary ones.

That contradicts the plan's opening sentence, which makes new combinations the question.

**For M01:** add a minimum symbolic set-aware yield on the transfer stratum to Decision 2 and to the release gate. The number is a judgment call; 50% would be a defensible starting proposal.

### 4. Decide what "inconclusive" does

The transfer comparison has three outcomes: proceed, stop, and inconclusive. The plan gives no action for the third, and item 1 makes it the likely one. State the default. My suggestion: inconclusive means adapters are not funded, and the maintainer may commission one fresh panel.

## Smaller items

- **Exact match against D's private forms.** The co-primary yield is exact normalized agreement with forms the grammar author never sees. Any difference in convention between D's generator and the public normal-form spec counts as wrong. Publish D's forms for the 12 worked fixtures and the 100 pilot inputs as a notation reference, and have a reader resolve rows where the exact match fails but the finite-model signature matches before they count against a gate.
- **Vocabulary.** Say whether development and locked inputs use only words seen in training. If they do not, unknown words become a hidden second transfer test.
- **D's workload.** D now writes a generator that emits normalized meanings and full reading sets, which is an independent implementation of the semantics. That is valuable as a cross-check and is not in the effort estimate.
- **Three documents now govern the work** (00 superseded, 03 for milestones, 05 for protocol). At sign-off, move the binding numbers into `spec/contract.md` and `configs/pilot.yaml` and treat the plan files as history.
