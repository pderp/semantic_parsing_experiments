# Initial implementation plan for the CCG semantic parser

**Research question.** At what semantic accuracy and coverage can a typed Combinatory Categorial Grammar (CCG) reproduce a versioned frontier teacher’s interpretations on a CPU? Compare its serving and lifetime costs with a task-distilled open-weight model on the same inputs, context, and target meanings. A successful experiment yields a reproducible quality–coverage–cost comparison, including the cases where the symbolic parser abstains.

**Basis.** This plan follows *Distilling Semantic Parsing into a CCG Rule System*, v1.1, 18 November 2026 (`ccg_semantic_parser_design.pdf`). Milestone numbers match Appendix A. Appendix B reports 39 checks from a companion semantic micro-model. The workspace supplied the PDF alone. Reproducing those checks and validating the parser are future work. [Design document linked by the repository](https://drive.google.com/file/d/1rDD3drbD1KOxNMZs-C-P_8ypoj9uLRcz/view)

## First deliverable · M01 pilot contract

Start by writing a contract that two reviewers can apply to the same sentence without consulting parser internals. Resolve these project choices with the owners before collecting labels or implementing the grammar.

| Decision to record | First artifact |
| --- | --- |
| Which English domain and root meanings count, how tokenization works, what context the parser receives, and when a reference may stay unresolved | `spec/contract.md` and `schemas/request.json` |
| Which categories, features, unary conversions, semantic constructors, and exact normalization identities the pilot licenses | `spec/grammar_fragment.md` |
| How to return one meaning, competing readings, missing material, or an exhausted search, with witnesses and named diagnostics | `schemas/result.json` and worked request/result fixtures |
| What counts as teacher agreement and independently judged correctness, and what coverage, latency, memory, and CPU budget the pilot must meet | `configs/pilot.yaml` with preregistered targets and denominators |
| How to identify an input, context, grammar, compiled bundle, runtime build, policy, and run reproducibly | `run_manifest.schema.json`, serialization rules, and dependency lock |

For the first review, ask each reviewer to specify the licensed readings of “Every researcher reviewed a paper,” the agent of “leave” in “Alice promised Bob to leave,” and the result of interrupting a search before it finds a root. Resolve disagreements in the contract. Leave teacher selection, numerical targets, and runtime build identities open until their respective choices can be recorded.

## The first end-to-end parse

Use **Every researcher reviewed a paper** throughout implementation (§13). Give *reviewed* two typed lexical recipes under the same transitive category. Forward application builds the subject NP *every researcher*, the object NP *a paper*, and the VP *reviewed a paper*. Backward application combines the subject and VP into a finite clause. A single root can retain both readings through its children.

| Reading | One finite-model check |
| --- | --- |
| For each researcher, there is a paper that researcher reviewed. | True when two researchers each reviewed a different paper. |
| There is a paper that every researcher reviewed. | False in that same model if neither reviewed the other’s paper. |

Require two distinct normalized meanings, a replayable derivation for each, and a deterministic best derivation under fixed costs. If the preferred reading survives in the forest but loses on cost, investigate ranking. If an exact run loses a lexical alternative during packing, reduce the failure to a forest fixture. If a budget removes it, record the stage and candidate loss. These outcomes require different fixes.

## Contracts shared by every implementation

- **Offline and online work.** Cache raw teacher responses, validated targets, and optional alignment or derivation hints separately. Check proposed derivations against the grammar. At serving time, lexicalize the request, build the forest, score it, construct the selected meanings, and return normalized output with provenance. The symbolic core runs on CPU without a model call. An optional external fallback records its own output, routing rate, latency, and cost.
- **Finite grammar.** Compile a checked, MeTTa-shaped authoring language. Admit forward and backward application and degree-one forward and backward harmonic composition over adjacent nonempty spans. Bound category depth and features. License type raising explicitly and order same-span unary conversions acyclically. Compile only reachable, licensed transitions and reject unbounded growth, epsilon entries, unary cycles, and effectful builders.
- **Typed meanings.** Use entity references `E`, event references `V`, symbolic propositions `P`, and intensional contents `I`. Nouns denote predicates `E → P`, NPs denote generalized quantifiers `(E → P) → P`, and clauses accept a head-event continuation `(V → P) → P`. Lift names into the NP interface. Close the clause by applying it to the always-true event predicate. Use capture-avoiding substitution and keep logical binders distinct from runtime pattern variables.
- **Exact normalization.** Preserve the raw meaning and a versioned transformation trace. Canonicalize binding, beta-reduce typed construction terms, and flatten and order conjunctions only where the declared theory licenses it. Preserve role direction, repeated conjuncts, quantifier order, negation, and content boundaries. A boxed proposition retains its binding environment. Give learned SENF paraphrase consolidation its own policy and provenance. Store knowledge enrichment separately from sentence assertions.
- **Packed forest and selection.** Key each node by sentence, span, instantiated category and features, observable semantic interface, and finite control history. Every future local guard and score must see what it needs in that key. Put the recipe, ordered children, rule or lexical choice, and cost on each edge. Reinsertion of an identical edge is idempotent. Build by span and unary order, finish the forest, then minimize additive fixed-point costs with checked arithmetic and structural ties. Materialize meanings from witnessed derivations. Derivation cost, probability mass over equivalent outputs, and calibrated acceptance are distinct quantities.
- **Result contract.** Return a construction status (`complete`, `truncated`, `no_parse`, `error`) and an interpretation decision (`accepted`, `ambiguous`, `abstain`). Exhaustive search with no licensed root yields `no_parse`. A resource limit yields `truncated` even if a candidate exists. An unsupported runtime operation yields a named diagnostic with `error` and `abstain`. Return input, context, and bundle identifiers alongside the results.

## Delivery sequence and acceptance gates

Roles follow Appendix A. **A** owns language and semantics. **B** owns the reference parser and independent validation. **C** owns data and evaluation. **D** owns integration, compilation, adapters, and releases. The paths and `ccgdistill` commands below name planned deliverables.

| Milestone | Depends on · lead | Deliverable and evidence required to pass |
| --- | --- | --- |
| M01 · Pilot contract | Start · D with A and C | Produce the contract and fixtures above. Reviewers agree on expected outputs and both status axes. |
| M02 · Semantic interpreter | M01 · A, reviewed by B | Build `src/semantics/`, a typed AST schema, `sem-check`, and `sem-normalize`. Test capture avoidance, type rejection, alpha-equivalence, idempotence, and the separating examples below. |
| M03 · Grammar checker | M01–02 · A, reviewed by B | Define the DSL and implement `ccgdistill check`. Accept the seed declarations. Reject forbidden rules, type mismatches, and hidden scoring dependencies with a source location and named error. |
| M04 · Teacher and cache | M01–02 · C, alongside M03 | Pin the teacher configuration, prompt, schema, decoding, and context. Replay cached annotations without model calls. Keep invalid, uncertain, ambiguous, and conflicting responses. Repeat a declared sample to measure instability. |
| M05 · Dataset splits | M02, M04 · C | Group by document, paraphrase, semantic template, and generation family before splitting. Run a leakage audit, retain independent adjudications, and give D custody of the locked test. Document actual access boundaries. |
| M06 · Seed grammar | M03, M05 training split · A | Cover names, nouns, determiners, event frames, simple tense, manner, negation, both local scope readings, and subject/object control. Each family gets stable source IDs, positive and contrast fixtures, and an inventory count. |
| M07 · Exact reference | M02–03, M06 · B | Implement the packed reference parser and a separately written exhaustive tree enumerator for tiny grammars. Compare derivations and meanings, including lexical ambiguity, multiword spans, feature conflicts, and duplicates. Resolve every mismatch. |
| M08 · Ranking and extraction | M07 · B | Match exhaustive minimum costs and structural ties. Emit raw and normalized meanings plus witnesses. Compare top-1 with exhaustive coverage on tiny fixtures. For larger inputs report the candidate budget and oracle-at-`k` as a lower bound. |
| M09 · Common parser IR | M03, M06–08 · D | Compile categories, interfaces, transitions, recipes, costs, unary order, source maps, and normalization metadata into one immutable bundle. Rebuild to identical bytes. Compare source-driven and compiled reference forests on the independent suite. Specify matching, enumeration, barriers, export, and failure behavior. |
| M10 · Runtime probes | M09 · D, reviewed by B | Pin MORK/MM2, PeTTa, and CeTTa builds. Probe each required operation and retain raw evidence. Mark capabilities as verified native, verified host, unsupported, or unverified. A profile proceeds when each operation it needs has a verified implementation. |
| M11 · Three adapters | M09–10 · D | Implement `parse --backend mork`, `petta`, and `cetta` from the same IR. Demonstrate complete phase barriers, late data handling, alternative enumeration, interruption, and sentence isolation. Export canonical records and disclose the host/runtime partition per profile. |
| M12 · Four-way qualification | M11 · B | Freeze the mandatory finite exact suite before tuning. Compare each adapter to the reference on nodes, edges, roots, costs, ties, meanings, and both status axes. Every mandatory case must finish with the expected complete result or justified `no_parse`. Minimize discrepancies and report qualification per profile. |
| M13 · Grammar growth | M05, M08–09 · C with A and D | Cluster failures by cause. Issue bounded proposals with a reusable patch, positive and negative examples, a new combination, and inventory and ambiguity deltas. Independently review regressions and resource use. Use M12 to distinguish backend defects and rerun it for each claimed grammar/profile combination. |
| M14 · Matched benchmarks | M12, frozen M13 candidate · C with B and D | Run the two comparison tracks below alongside a native CPU parser and a task-distilled open-weight model. Publish raw observations, support matrix, hardware manifests, and quality and cost denominators. |
| M15 · Locked evaluation | M13–14 · C, test held by D | Fit acceptance on development/calibration data. Freeze grammar, builds, thresholds, budgets, and evaluator before opening the test. Report all preregistered objectives, sample counts and uncertainty, including abstentions and failed runs. |
| M16 · Reproducible release | M15 · D with A–C | Package grammar, IR, build locks, conformance fixtures, support matrix, raw measurements, limitations, and replay instructions. Reproduce a symbolic sample in a clean environment for each claimed profile. Resume interrupted jobs from verified checkpoints without duplicating committed observations. |

## Semantic fixtures that constrain the seed

| Contrast | What the checker must establish |
| --- | --- |
| *Alice reviewed Bob* / *Bob reviewed Alice* | Swapping participants reverses Agent and Theme and changes exact output. |
| *Alice promised Bob to leave* / *Alice persuaded Bob to leave* | The promise frame binds Alice as the embedded agent. The persuasion frame binds Bob. Both embed a boxed proposition and permit a model in which nobody left. |
| *Every researcher promised Bob to leave* | One bound researcher fills the matrix and embedded agent roles. Independently quantifying a second researcher fails this fixture. |
| *Alice did not leave* | The leaving-event existential stays inside negation. A model with one leaving event and one unrelated event distinguishes the correct form from an existential hoisted outside negation. |
| *Every researcher did not leave* / *Not every researcher left* | A model in which only some researchers left separates the designated every–not and not–every readings. |
| *Alice reviewed Bob quickly* | The manner predicate applies to the review event itself. Distinct event variables elsewhere imply unequal events only with an explicit distinctness constraint. |

## Runtime and evaluation protocol

For M10–12, identify evaluator, backing store, language profile, build, extensions, adapter commit, and host responsibilities. Use MORK/MM2, PeTTa with a non-MORK space, and CeTTa with its native evaluator and store as primary configurations. Report MORK bridges, CeTTa’s MORK-delegating `--lang mm2`, and optional Prolog assistance as named variants. Probe MORK’s consumed `exec` after an early failed match. Probe PeTTa’s load order and complete answer enumeration. For CeTTa, verify that a requested operation performs its effects and distinguishes an empty answer stream from an inert expression. Check all three against late writes, duplicate records, and incomplete phases.

For M14, **Track A** uses the same IR, deductions, phase order, scoring policy, search policy, and host partition across primary profiles. **Track B** allows documented runtime-specific indexing, scheduling, and storage. Requalify each exact optimization at M12. Report pruning as a separate approximate search policy with its candidate loss. A runtime used only for storage is identified as such.

Benchmark fixed workloads on matched hardware, cores, memory, batching, and time budgets. Include primitive probes, controlled changes in ambiguity and length, and held-out application inputs. Measure startup/load, cold and warm p50/p95/p99 latency, throughput, CPU-seconds, and peak process-group memory. Time tokenization through serialization, including host and transport work. Retain one observation per runtime/input pair, including unsupported, truncated, and failed cases. Any paired timing on common completions gets an explicit denominator alongside full-population results.

Report exact teacher agreement, independently adjudicated semantic accuracy, accepted coverage and selective error, ambiguity, and contrast performance. Compare the neural baseline using the same teacher data, context, target representation, and quality requirement. Account for annotation and construction costs separately from per-request serving and fallback costs. Choose a backend only for an operating point supported by these measurements.

## Evidence and next decisions

At each handoff, record the base commit, input and bundle digests, configurations, checks run or skipped, raw results, unresolved counterexamples, and gate decision. Keep teacher labels, parser outputs, and adjudications in separate versioned records. Checkpoint annotation batches, proposals, and benchmark observations atomically. Resume from verified manifests and replay an interrupted sentence from its immutable input.

The design proposes a first coverage experiment around **100–200 reusable templates and 5,000–10,000 lexical records**. Track source templates, lexical senses/frames, compiled transitions, and active alternatives separately. At that point, use the observed error mixture to choose between lexical growth, a grammar or ranking change, an explicit context extension, or stopping. Passive alternations, questions, coordination, statives, and broader tense/aspect each need their own typed contract and renewed conformance checks. The larger inventory estimates in §12 are planning ranges. Only held-out quality, coverage, and measured cost justify expansion.
