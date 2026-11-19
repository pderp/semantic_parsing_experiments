# Critical review of `00_initial_codex.md`

**Reviewed:** `docs/plans/00_initial_codex.md` at commit `569da59`, against its source, *Distilling Semantic Parsing into a CCG Rule System* v1.1 (63 pages, sha256 `ce8f4717…1e1b56`). Section and milestone numbers below refer to that PDF.

**Reviewer:** Claude (Fable 5.2), 19 November 2026. I read both documents in full. I did not run anything: there is no code in the repository yet, and the design's companion checker was not supplied.

## Verdict

The plan is an accurate compression of the design's Appendix A. I checked every milestone's dependencies, owner, and gate against the PDF and found no misstatement. It also keeps the design's most valuable disciplines: two status axes, separation of teacher agreement from adjudicated correctness, and reporting of failed and unsupported runs.

Its weakness is that it is a summary rather than a plan for this repository. It inherits the design's sequencing, staffing assumptions, and open questions without adapting them, and it leaves out several things the design does specify. The most serious problems are:

1. The three-runtime comparison sits on the critical path ahead of any evidence that the grammar approach reaches useful coverage.
2. The seed fragment is too narrow to parse natural text, so the first coverage numbers will be near zero for reasons unrelated to the hypothesis.
3. Exact-match teacher agreement will mostly measure whether the teacher follows the project's notation conventions, and the predicate vocabulary that makes exact match possible has no owner or deliverable.
4. No gate has a number, and M01 is told both to preregister targets and to leave them open.

I recommend revising the plan before M01 starts. The changes are listed at the end.

## What the plan gets right

- **Faithful to the source.** Milestones M01–M16, their dependencies, and their leads all match Appendix A. The scope example, the control fixtures, and the negation countermodel are stated correctly.
- **Honest about status.** It says the 39 checks in Appendix B were not reproduced and that all paths and commands are planned, not existing.
- **Failure modes are distinguished.** The "first end-to-end parse" section separates a ranking loss, a packing loss, and a budget loss, each with a different fix. That is the most useful paragraph in the plan.
- **Benchmark hygiene.** Full-population denominators, host and transport time included, pruning reported as a separate approximate policy.

## Major problems

### 1. The runtime comparison blocks the main question

The plan's research question is the quality, coverage, and cost of a CCG parser against a task-distilled neural model. Answering it needs the reference parser, a native CPU implementation, a teacher corpus, and the neural baseline. It does not need MORK/MM2, PeTTa, or CeTTa.

Yet M14 and M15 depend on M12, which depends on three adapters (M09–M11) for three young runtimes, one of them pinned to a personal repository snapshot. That is the largest and least predictable block of engineering in the plan, and it comes before the first learning curve. If the grammar approach stalls at low coverage, the adapter work will have been spent on a parser nobody wants to run.

The design half-acknowledges this in §14.3 ("after lowering to each runtime, optimize only qualified configurations") but still orders the work adapters-first. The plan copies that order.

**Change:** split the programme into two tracks with separate questions. Track 1 is M01–M08, then grammar growth and the neural comparison on the reference and native parsers. Track 2 is M09–M12 and the runtime benchmarks. Track 2 starts only after Track 1 passes a stated coverage gate. M13 already depends only on M05 and M08–M09, so this is mostly a change to M14 and M15's dependencies.

### 2. The seed fragment cannot parse natural text

M06 covers names, common nouns, determiners, transitive and intransitive verbs, simple tense, manner adverbs, negation, two scope readings, and control. Later extensions add passives, questions, coordination, statives, and tense/aspect.

Neither the plan nor the design mentions adjectives, prepositional phrases, relative clauses, pronouns, plurals, or possessives. (I searched the PDF text: none of those words occurs.) Copular sentences are deferred as "statives". A fragment without *is*, *and*, *of*, *the red*, or *it* will reject nearly every sentence of ordinary prose or technical documentation.

This matters because M05 asks for "naturalistic domain examples" and M13 clusters failures by cause. On natural text almost every failure will be "missing construction", which tells us nothing. The first coverage experiment (100–200 templates, 5,000–10,000 lexical records) is two orders of magnitude beyond the seed, and the plan gives no route from one to the other.

**Change:** M01 must either choose a controlled-language domain where the fragment is plausibly sufficient, or declare that the pilot corpus is synthetic and that natural-text coverage is not measured until a named later point. It should also list the missing constructions explicitly and rank them by frequency in the chosen domain.

### 3. Exact-match agreement measures notation, and the vocabulary has no owner

The headline metric is exact agreement between the parser's normalized form and the teacher's. The exact normalizer equates only alpha-renaming, beta-reduction, and conjunction reordering (§6.1). It deliberately preserves binder order.

So *A researcher left* written as `∃x(R(x) ∧ ∃e(…))` and as `∃e∃x(…)` are logically equivalent and count as a disagreement. The teacher will match only if its prompt pins every such convention by example. At that point the metric measures how well a language model imitates the grammar's output format.

The same applies to predicate names. For exact match, the teacher and the lexicon must use the same symbol for every word sense. The design's records carry an `ontology_digest`, but the plan never mentions an ontology, and M01's deliverables do not include one. If the teacher invents symbols, the lexicon memorizes the mapping and "agreement" is a lookup score.

**Change:** add a predicate and role inventory, with a sense-assignment policy, to M01's deliverables. Add a second agreement metric that checks equivalence on small finite models, so that convention mismatches can be told apart from meaning mismatches. The design's micro-model already contains a finite-model evaluator that could be the basis.

### 4. Gates have no numbers, and M01 contradicts itself

M01's table requires `configs/pilot.yaml` "with preregistered targets and denominators". The next paragraph says to "leave teacher selection, numerical targets, and runtime build identities open". The design puts preregistration in M01 (step 4). As written, M01 cannot pass, or it passes with nothing preregistered.

Elsewhere the gates are qualitative: "reviewers agree", "resolve every mismatch", "report all preregistered objectives". M15's gate is satisfied by reporting, whatever the result. Nothing in the plan says what outcome would stop the project. The design does (§14.3: continue past the seed only if the contrast suite passes, and revise the architecture if a distilled model dominates at the relevant quality and cost), and the plan reduces this to the two words "or stopping".

**Change:** give each gate a count and a threshold, even a provisional one. State a deadline for the deferred targets, no later than the M05 split. Restore §14.3's three decision gates as explicit go/no-go points.

### 5. The roles assume four independent parties

The plan assigns work to owners A, B, C, and D and relies on their independence: B validates A's semantics, D holds the locked test away from the grammar authors, "two reviewers" agree on M01 fixtures. The repository does not say who fills these roles.

If they are coding agents sharing one checkout and one human, the separation is procedural only. The design says so itself (§10.2: a withheld set must be "inaccessible to rule-writing agents, rather than merely stored in a file called test"). The plan says "document actual access boundaries" but proposes none.

**Change:** name the people or agent configurations behind A–D. Decide where the locked test lives (a separate private repository or an evaluator service) before M05 creates it.

### 6. Three large deliverables are hidden inside M14

- **The distilled neural baseline.** Training an open-weight model on teacher data needs a model choice, a compute budget, and enough data. The plan never sizes the teacher corpus. A grammar can be built from hundreds of examples; a fair neural baseline probably needs thousands.
- **The native CPU parser.** This is a second full implementation of the parser. It appears once, in passing.
- **The existing symbolic baseline.** §11.3 lists four baselines. The plan drops this one without saying why.

Independent adjudication has the same problem. Showing 98% accepted accuracy (the design's illustrative figure) with zero observed errors needs at least 150 adjudicated examples for a 95% bound, and several hundred once any errors appear. Adjudicators must read scoped logical forms. No size, cost, or person is given.

**Change:** promote the two implementations to their own milestones. Size the teacher corpus and the adjudicated set in M01. Either restore the fourth baseline or record the decision to drop it.

## Smaller issues

- **The contract is frozen before anything runs.** M01 fixes the result schema, chart interface, and normalization policy before a single sentence has been parsed. The "first end-to-end parse" is the right de-risking exercise, but it is not a milestone and spans M02, M03, M06, M07, and M08. Build it first as a throwaway slice, then freeze M01.
- **The 39 checks have no recovery step.** The plan notes the checker was not supplied and stops there. Table 8 gives only family counts, so the checks cannot be rebuilt from the PDF. Ask the author for `semantic_reference_checks.py` and the LaTeX source, or make re-deriving the checks the first task of M02.
- **Scope selection is a per-verb constant.** Scope readings are separate lexical entries with fixed local costs, so the preferred reading for a given verb never varies with context. Every doubly quantified sentence is either always resolved the same way or always `ambiguous`. The plan should state the default and how it counts toward coverage. Sentences with names also yield two derivations with one meaning, so acceptance must be decided on normalized meanings.
- **M13 has no exit condition.** M14 needs "a frozen M13 candidate", but nothing says when growth stops. Benchmarks on a seed-sized grammar would measure marshalling overhead on ten-node forests.
- **M12 can stall.** If one runtime never qualifies, it is unclear whether M12 has passed. Define passing as every profile reaching a terminal status (qualified, or blocked with evidence) within a time box.
- **"One observation per runtime/input pair"** contradicts the repeated, blocked measurement protocol of §11.5. It should say at least one record per runtime, input, and repetition.
- **Dropped without comment:** the ablations (§11.10), the break-even cost model (§11.8), and the rule that formulas stored in a reasoning space must not assert content under negation or `Box` (§5.10). The last one matters for the MORK adapter.
- **The source document is not pinned.** The plan cites a filename and the README a Drive link. A plan that demands content digests for everything should record the digest of its own basis.
- **No implementation language** is chosen for the reference parser or the native one, and morphology (`reviewed` → `Review` + `Past`) is not mentioned.
- **No effort or calendar estimate** appears anywhere, so the plan cannot be used to decide what to cut.

## Recommended changes, in order

1. Build the single-sentence slice (*Every researcher reviewed a paper*, both readings, one finite-model check) as a spike. Use it to draft the M01 contract.
2. In M01: choose the domain with the fragment's limits in view, add the predicate inventory, fix numeric targets or a date for them, name the role-holders, and size the teacher corpus and adjudicated set.
3. Recover or re-derive the 39 checks as the first tests of M02.
4. Re-sequence so that grammar growth and the neural comparison run on the reference and native parsers first, with a stated coverage gate before any runtime adapter work.
5. Add a finite-model equivalence metric beside exact match.
6. Give every gate a threshold and restore the stop conditions from §14.3.
7. Give the native CPU parser and the neural baseline their own milestones.

Items 1–3 are cheap and can start now. Item 4 is the one that most changes the cost of the programme.
