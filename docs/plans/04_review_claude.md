# Review of `03codex_plan.md` before implementation

**Reviewed:** `docs/plans/03codex_plan.md` at commit `c0d4855`, against my earlier review (`01_critical_review_claude.md`) and the v1.1 design PDF.

**Reviewer:** Claude (Fable 5.2), 19 November 2026. Nothing was run except a check of the plan's statistics.

## Verdict

Start the spike now. The revised plan resolves all six major problems and nearly all the smaller ones from the first review, and nothing below changes the spike.

Four things should be settled in M01, before bulk annotation, because each one affects what the Decision 2 and release thresholds mean. They are listed in order of importance. A short list of smaller items follows.

## What the revision fixed

| Issue from the first review | Status in `03` |
| --- | --- |
| Runtime adapters ahead of coverage evidence | Fixed. Two workstreams; M09–M12 open only after Decision 2. |
| Seed fragment cannot parse natural text | Fixed. Controlled synthetic pilot, a 200-sentence survey of missing constructions, natural coverage reported separately. |
| Exact match measures notation; no vocabulary owner | Fixed. `spec/ontology.yaml` owned by A, plus a finite-model agreement metric. |
| Gates without numbers; M01 self-contradiction | Fixed. Thresholds for Decisions 1–3 and the release; targets approved before bulk annotation. |
| Unassigned roles | Fixed as a proposal, with a private evaluator outside the checkout. |
| Hidden deliverables | Fixed. Native, neural, and existing-symbolic baselines each have a row, and corpus and adjudication are sized. |
| Smaller items | Spike first, checker recovery, scope default, M13 exit, M12 time box, repetitions, ablations, break-even, storage rule, source digest, and effort estimate are all addressed. |

The statistics hold up. I recomputed the 149-case claim (zero errors in 149 gives an exact one-sided 95% lower bound of 98.0%) and the 960 readings and 80 reader-hours.

## Settle in M01

### 1. Whoever writes the grammar must not write the generator

The pilot corpus is produced by a generator over researchers, papers, and review events. If the grammar author also writes or reads that generator, the grammar becomes its inverse, and Decision 2's "600 of 1,000 accepted" measures bookkeeping. The plan assigns the locked portion to D but does not say who owns the generator or whether A can see its templates.

The same structure makes the neural comparison uninformative on the main sample. A fine-tuned sequence model will fit template-generated text almost perfectly, so on quality and coverage it will likely match or beat the grammar. On CPU latency it will likely lose. Neither outcome tests the hypothesis.

The stratum that does test it is the one the plan already reserves: combinations of known constructions that are absent from training. That is where a compositional grammar should transfer and a sequence model often does not.

**Proposed changes:**

- C or D owns the generator. A sees its output on the training and development splits, never its source or template list.
- Give the held-out-combination stratum a registered size (for example 200 development and 150 locked inputs) and make it a co-primary result for both the grammar and the neural model.
- Have the generator record its own intended meaning for each sentence, held by D. This gives a free check on the teacher for every input and reduces reliance on human reading.

### 2. The ambiguity rule and the 60% threshold are coupled through the mixture

By default every sentence with two scope-distinct readings is `ambiguous` and counts as zero accepted coverage. The share of such sentences in the generator mixture therefore caps accepted coverage. A mixture with 45% doubly quantified sentences makes the 60% gate unreachable; a mixture with 5% makes it easy. As written, the gate can be passed or failed by choosing the mixture.

Three things are also unspecified:

- **Credit for a correct ambiguous answer.** Returning both licensed readings for a truly ambiguous sentence is the right behaviour and currently scores the same as abstaining.
- **How the neural model is scored on those inputs.** It emits one answer. It needs the same option to return a set, or the comparison is unequal.
- **What the teacher's target is.** A set, a preference, or both; the plan allows either.

**Proposed changes:** fix the mixture, including the share of scope-ambiguous inputs, before approving the thresholds. Add a fourth reported outcome, "ambiguous with the correct reading set", beside accepted, abstained, and wrong. State the threshold on unambiguous inputs and on the full population separately.

### 3. The reading budget covers one system

The 960 readings count one output per sampled input. The plan adjudicates at least three systems on those inputs (grammar, neural model, teacher) and possibly the ERG mapping, and it re-audits the same 200 development inputs at up to four growth checkpoints.

Identical outputs can share a reading, so the multiplier is below the system count, but 80 hours is probably low by a factor of two to four.

**Proposed change:** in the 100-input pilot, measure how often systems disagree and how many outputs change between checkpoints. Size the budget from that. If hours are fixed, cut the audited sample, not the number of systems.

### 4. The 95% bound implies about 97% observed accuracy

The release requires a one-sided 95% lower bound of at least 95% on accepted accuracy. With 300 accepted cases, which is the minimum the coverage threshold allows, that permits at most 8 errors (97.3% observed). With all 500 accepted it permits 16 (96.8%). Family-aware intervals will tighten this further.

This is a reasonable bar. It should be written down as the number of errors allowed, so that nobody reads the requirement as "95% correct".

## Smaller items

- **Target serialization and the FLAN-T5 tokenizer.** The T5 vocabulary is known to lack several characters common in logical forms, including curly braces and `<`. They become unknown tokens and cannot be generated. Before training, round-trip every training target through the tokenizer and require an exact match. Otherwise the baseline's malformed-output count is an artefact of notation.
- **Control sentences get no model-based score.** The finite-model metric marks intensional phenomena as unscored. Control is two of the six core contrasts. One option: treat a boxed payload as its truth vector across the world bank, which is the design's own reading of `Box` (§5.8), so two control outputs agree when their matrix clauses and payload vectors agree.
- **World bank size.** State how many worlds, how they are generated, and the seed. Exhaustive enumeration is feasible for domains of two or three entities and events.
- **Source of natural sentences.** The 200-sentence survey and 300-sentence sample need a named source and licence. "Domain sentences" for a synthetic researcher-and-paper domain could mean several things.
- **Decision 2 will rarely be decided by the neural comparison.** Clause (iv) only requires that it be measured, and the stop rule needs the neural model to win on all four of quality, coverage, latency, and cost. Given the latency gap on CPU, that is unlikely. If the intent is that a much better neural result should stop adapter work, say what margin on the held-out-combination stratum would do so.

## Suggested order

1. Run the spike as written.
2. In M01, assign generator ownership, fix the mixture, and register the held-out-combination stratum (items 1 and 2).
3. Run the 100-input pilot and use it to size the reading budget and check tokenizer round-tripping (item 3 and the first smaller item).
4. Approve thresholds, with the allowed error count stated (item 4).
