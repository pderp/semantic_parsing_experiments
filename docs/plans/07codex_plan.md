# Plan 07 · from the scope spike to M01 sign-off

**Build the two-day scope spike first.** Its acceptance test is one packed root for *Every researcher reviewed a paper*, two witnessed meanings, and a world that separates them. Reversing lexical insertion order must preserve both meanings and their tie order. The next decision is whether the pilot contains enough genuinely different combinations to test transfer. Make that decision before reserving any examples or buying bulk annotations. [Scope spike and evaluation protocol](05codex_plan.md) · [Claude’s 06 review](06_review_claude.md)

## 1. Count transfer families before promising a comparison

D, the maintainer who holds the private generator, enumerates the finite construction signatures admitted by the public grammar fragment. A family is a combination of structural choices such as a control frame, the position of a quantifier, or the attachment of a modifier. Changing a name, lemma, inflection, or paraphrase of the same structure leaves its family ID unchanged.

For each candidate family, D verifies that all its component constructions can appear in training while the combination itself is withheld. Before assigning splits, publish the **counts** of eligible single-reading and two-reading families, feasible allocations, and the largest proposed family weight. Keep the signature-to-panel mapping private. Exclude families with shared structural signatures across transfer panels. Record the generator and census digests.

| Panel | Inputs | Proposed minimum for an inferential comparison |
| --- | ---: | --- |
| Development transfer | 200 (160 single, 40 ambiguous) | 20 distinct eligible families |
| Locked transfer | 150 (120 single, 30 ambiguous) | 20 further families, disjoint from development |
| Optional fresh development panel | 200 with the same mixture | 20 additional disjoint families, if available and reserved at sign-off |

The primary panels therefore require at least **40 eligible families** between them. A repeat option requires at least **60**. Balance family sizes as closely as the fixed 80/20 mixture permits. At equal weight, one family accounts for 12.5 percentage points with eight families and 5 points with twenty. Twenty is an eligibility floor. At M01, check the expected interval width under plausible family-level disagreements and record how unequal weights affect it. Resample paired systems by whole family, preserving the mixture, and publish family-level outcomes alongside the input-weighted estimates.

If either primary panel falls short, preregister transfer as **descriptive only** for this pilot. Publish the observed yields and family counts, keep the proposed ten-point margin, and leave adapter work unfunded. Additional sentences from an existing family improve the description of that family. They do not increase the independent family count.

## 2. Publish how to derive the complete reading set

A writes the public scope policy. D implements it independently in the private generator. Both work from the same ontology, licensed frame inventory, and versioned exact normalizer. A reader must be able to start with the words of a new sentence, apply the licensed recipes, close the clause, normalize each result, and deduplicate the set. The following rules define the proposed pilot policy, using §§5.4–5.7 of the design.

| Construction | Public rule and worked consequence |
| --- | --- |
| Simple transitives | Only frames licensed for the two local scope recipes may order subject over object or object over subject (Eqs. 16–17). *Every researcher reviewed a paper* yields both orders. With named participants the recipes can normalize to one meaning. |
| Negation | VP negation opens the subject once and places negation outside the VP’s event existential (Eq. 21). *Every researcher did not leave* has the every–not reading. The surface construction *Not every researcher left*, where licensed, places negation outside the universal. |
| Control | The selected promise and persuasion frames bind the matrix subject, then the recipient, then the matrix event (Eq. 22). The embedded subject reuses the bound matrix subject for *promise* and the recipient for *persuade*. With both arguments quantified, this frame licenses one matrix order. Keep embedded quantification inside its box. |
| Manner and composition | Apply the modifier to the event of the VP it attaches to. Licensed combinations inherit the child recipes and the parent’s binding rules. An additional scope order or attachment requires an explicit public license. |

D checks that the resulting normalized set has size one or two before assigning it to a mixture cell. Log out-of-fragment cases and their reason before sealing the manifest. After sealing, preserve every row and log any target defect. D publishes canonical target **sets** and derivations for all 12 worked fixtures and canonical sets for all 100 training-only pilot inputs. Both grammar and baseline builders receive the same notation reference. Bulk private targets and reserved combinations stay with D. Teacher supervision for model training follows the registered training policy.

**Vocabulary rule.** All controlled development, calibration, and locked inputs draw their surface vocabulary, lemmas, senses, and frames from training, including proper names. Pin tokenization and case handling, and require zero out-of-vocabulary entries on these splits before sealing. Transfer can still combine known items in new ways. Report lexical gaps separately on the natural-text sample.

**Scoring a disputed form.** Preserve the raw exact normalized set-match result. If it fails but the candidate and target sets agree on the frozen finite-model signatures, send the sentence, complete sets, and derivations where available to a reader blinded to system identity before finalizing the gate. The reader applies the public scope and normalization policy and records an accepted equivalent notation, a generator error, a system error, or an unresolved case. Finite-bank agreement alone cannot authorize credit. Keep raw and adjudicated yields side by side. Apply documented target corrections to every system and occurrence, and compute conservative bounds on unresolved cases.

## 3. Require transfer to succeed in absolute and relative terms

Set-aware symbolic yield counts correct singleton answers plus correct complete ambiguous sets, divided by **all assigned transfer inputs**. Abstentions and incomplete reading sets earn zero. Use the adjudicated treatment above consistently for both systems. Record threshold decisions from unrounded counts.

| Decision | Absolute symbolic floor | Other evidence required |
| --- | --- | --- |
| Fund adapters at Decision 2 | **≥100/200** correct transfer answers (50%) | Pass the family census, the paired neural comparison, and plan 05’s overall coverage, audited accuracy, native parity, and CPU gates. |
| Qualify the controlled-domain release at M14/M15 | **≥75/150** correct locked transfer answers (50%) | Pass the overall and single-reading coverage gates, the adjudicated accepted-accuracy lower bound, and the native resource gate. A claim of transfer within the neural margin also requires the independent locked comparison to pass. |

For the paired comparison, let the gap be neural yield minus symbolic yield on the same inputs. Keep the **+10 percentage point** margin. An upper one-sided limit below +10 passes the relative check. A lower limit at or above +10 fails it. For example, if both systems answer 30/200 correctly, their observed gap is zero and the symbolic system still fails the absolute floor.

**Inconclusive means no adapter funding.** If the interval straddles or touches the decision boundary without establishing either result, or the evidence leaves a pass unresolved, publish the primary study and defer M09–M12. The maintainer may commission **one** fresh development panel only if its families, size, and analysis were reserved at M01. Keep both candidates, scoring policy, and margin frozen. If two funding looks are authorized, use 97.5% one-sided limits at each look to allow for both opportunities to pass. A single preregistered look uses 95%. The fresh panel must independently pass the absolute and relative checks. A second inconclusive result closes the funding decision for this pilot. A definite failure stops this route immediately. Preserve the locked panel for its one release evaluation, including when funding stops.

## 4. Sign one executable contract

Allow **5–10 additional engineering days for D** to enumerate signatures, implement independent generation of readings, reconcile the public examples, and test the private evaluator. Track actual effort separately from reader-hours. After the 100-input pilot, revise the estimate using measured generation, disagreement, and adjudication costs. The spike, census, and pilot handoffs each record what ran, the evidence location, and outstanding defects.

At M01 sign-off, put the public semantic, vocabulary, custody, and adjudication rules in `spec/contract.md`. Put every binding count, mixture, seed, threshold, budget, interval method, and permitted number of looks in `configs/pilot.yaml`. Include the split and audit budgets from plan 05 and the resource and qualification gates from plan 03. Generate the numeric tables in the sign-off record from the configuration and check their sums and feasible allocations. Record a shared protocol version and both file digests in each run manifest. Subsequent implementations and evaluators use that signed pair as their authority. Archive the numbered plans as the history of the decisions. [Milestones and engineering gates](03codex_plan.md) · [Sampling and measurement protocol](05codex_plan.md)
