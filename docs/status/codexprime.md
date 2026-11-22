# CodexPrime status

## 2026-11-22 · bank scope separation, scorer retest and teacher pilot review

Two conditioned draws separate all 6,400 public mixed-scope configurations. Original and revised banks both distinguish all six ambiguous sentences in the 392 variants. On the same 317 ambiguous released training inputs the collapse count fell from 14 to zero. ClaudeScope has the revised digest and a blind packet for delivery to ClaudeOracle. Independent sign-off is pending. The revised scorer correctly flags all five synthetic rows. D reports 100/100 exact pilot answers, with public targets and unknown independent repeatability. [Bank and full collision rates](../../spec/world-bank.md) · [Scorer retest](../../reports/scoring_review_codex.md) · [Teacher review](../../reports/stage2_pilot_teacher_review_codex.md)

## 2026-11-22 · finite bank candidate and scorer review

Built the proposed 64/16/176-world bank and a shared typed evaluator. The candidate digest and hand contrast table are ready for independent verification before scoring. Reviewed submission validation with five invented rows. The current scorer awarded correctness to incomplete states; findings went to D. [Bank, schema and replay](../../spec/world-bank.md) · [Scoring review](../../reports/scoring_review_codex.md)

## 2026-11-22 · M07–M08 frozen witness gate

All 181 pairs across 32 grammars match, including 138 ranked structural keys and all 15 cases flagged for convention dependence. The first run exposed three discrepancies caused by global root and token bounds. Added restricted bundle support, clarified all 15 follow-up conventions and checked chart-wide signed overflow. [Gate and complete discrepancy record](../../reports/m07_m08_witness_gate.md) · [Witness contract](../../spec/witness-v1.md)

## 2026-11-22 · recovered M02 companion

Replayed 39/39 author checks byte-identically and reconciled all 39 with the original M02 suite. Eight new regression methods compare the seed parser, typed kernel, and countermodels to the recovered terms, including quantified object control and the finite versus tenseless negation distinction. The original normalizer and ontology remain the published baseline. [Crosswalk and comparison limits](../../reports/m02_author_checks.md) · [Provenance and replay](../../spec/normalization.md)

## 2026-11-22 · natural survey cross-review

Reproduced the public 0/200 result. All 200 rows contain an unknown alphabetic word, and 180 also exceed the 12-token limit. Ten labels cover all observed tags on 17 or 28 sentences depending on the selection. Recommend option (a), retaining the planned separate 300-row evaluation. [Review and replay](../../reports/natural_survey_v1_review_codex.md)

## 2026-11-21 · seed-1.1 article agreement

Applied the sponsor-approved existential article rule after the dry run found 876 affected sentences. The bundle exposes 57 tokens and 179 lexical entries. Both articles use the same existential recipe. Tested the required and rejected spelling for all 20 nouns in four NP positions. A cross-version replay also checked all 12 reconciled fixtures and 392 public variants, including ranked witnesses. Public capacity remains 150 primary families and 392 determiner variants. Review of the controlled-pilot interpretation and release scope went to ClaudeScope in MCP message 57. D owns regeneration and corpus release. [Protocol](../../spec/contract.md) · [Witness inventory rules](../../spec/witness-v1.md)

## 2026-11-21 · stage 1 promotion and first end-to-end reference parser

Verified the reconciled fixtures, reviewed the sign-off record, and promoted the sponsor-approved contract, ontology and configuration to `seed-1.0` in `950e90e`. The fixture artifacts retain their original draft identity. The [witness contract revision](../../spec/witness-v1.md) answers all 15 open questions separately from the reading freeze.

The [reference parser](../../src/reference/__init__.py) builds a packed chart from 178 checked ground entries covering the 56 surface tokens. It matches all 12 reconciled fixtures on normalized tokens, status, decision and exact reading set. The output-only comparison with ClaudeOracle matches those fields on all 392 public determiner variants and matches cost, object-wide count and canonical reading for all 680 ranked witnesses. Exact structural-key comparison awaits use of the same bundle identifiers by the oracle. The bundle and sample parse replay byte-identically across three Python hash seeds. This is the first M06/M07 end-to-end checkpoint; cross-review and the full M07/M08 tiny-grammar gate are pending.

Run `python3 -m src.reference 'Every researcher reviewed a paper.'` or `python3 -m src.reference --bundle` from the root. Reproduce the checks with `python3 -m unittest discover -v`, `python3 -m unittest discover -s spike -v` and `python3 -m tests.reference.compare_oracle`.

## 2026-11-21 · first M03 kernel

Added the [checked declaration reader](../../src/frontend/__init__.py) and the [seed binary inventory](../../grammar/kernel.metta). All four kernel combinators pass typed direction and scope-of-application checks. Six frontend tests cover source-located rejection, finite field and score checks, unary ordering, typed raising and cycle rejection, and the seed's application-only restriction. The seed lexicon and construction-specific guards await integration. [DSL and replay](../../spec/dsl.md)

## 2026-11-21 · first M02 suite

Verified the corrected census hash in commit `5eb4104` and regenerated identical pilot tables twice. Implemented typed seed terms, capture-safe beta reduction, exact conjunction normalization, canonical sets and replayable traces. Ten semantic tests pass, covering the seven Appendix B families and 1,000 seeded binding cases. The original companion files are outstanding. [Replay and provenance](../../spec/normalization.md)

## 2026-11-21 · sealed fixtures and stage 1 configuration

Sealed all 12 independent fixture answers in `4ee97d3` and sent the SHA-256 to ClaudeScope before reviewing the census. The [census review](../plans/15_review_census_codex.md) supports 40 families per panel. It identifies a difference between the simulated easy-family probability and expected neural yield. Under true equality at 60%, an independent approximation gives a 24% chance of passing on 39 single-reading development families.

The [pilot configuration](../../configs/pilot.yaml) registers the paired comparison on single-reading transfer, with one funding look. Each panel has 39 single-only families and one family for its two-reading rows. I set a minimum of 25% initial *not every* within each ordinary single-reading negation stratum, with VP negation represented in every split. That gives at least 160 training and 14 locked examples of the initial operator. The [table generator](../../tools/pilot_tables.py) verifies the reviewed public hashes and emits the evidence table for D's sign-off record. Deterministic replay passed, as did checks of the quota and gate rows and rejection of 13 invalid configurations. D owns reconciliation and the final record. Sponsor approval remains pending.

## 2026-11-21 · M01 part 2 ready for cross-review

Added the [draft pilot configuration](../../configs/pilot.yaml) and [stdlib table generator](../../tools/pilot_tables.py). Run `python3 tools/pilot_tables.py` from the repository root. Verified deterministic replay, split/mixture/gate arithmetic, independent-case error limits, and ten rejected invalid configurations. The configuration distinguishes the plan 07 comparison from the proposed single-reading estimand, uses one funding look, and leaves operational facts awaiting their owners as null. Stage 1 still needs census, review, fixture reconciliation and sponsor sign-off.

## 2026-11-21 · part 1 revision for census and fixtures

Reviewed ClaudeScope’s eight findings and revised the [contract](../../spec/contract.md) and [ontology](../../spec/ontology.yaml) to seed-0.2-draft. Public capacity check: 150 primary families, 392 determiner variants, four families capable of two readings, zero families below ten strings. Checked binding, types and canonical conjunct order in four published notation examples. All 13 spike tests pass. Recommended descriptive two-reading transfer and a separately labeled single-reading comparison, pending census and sign-off.

## 2026-11-21 · custody sentinel

At D’s request I read only eight characters of the designated dummy sentinel under normal workspace-write restrictions and reported that it was readable (MCP message 14). A and D therefore have procedural separation in this environment. I consulted the published scope-spike outputs to validate part 1. For step 7, classify overlapping public examples as known regressions and use fresh unanswered prompts for an independent reading.

## 2026-11-21 · M01 part 1 ready for cross-review

Drafted the [public contract](../../spec/contract.md) and [closed seed ontology](../../spec/ontology.yaml). Verified 42 distinct surface tokens, seven lexical frames, predicate/role sorts, 800 distinct plain mixed-scope sample strings in the person/artifact slice, and byte agreement for both published spike normal forms. All 13 spike tests pass. Counts establish lexical capacity only. Awaiting ClaudeScope’s contract review before the private census, pilot configuration and independent fixture exchange.

## 2026-11-21 · plan 11 cross-review

Approved the lanes and proposed specific custody, independent-fixture and pilot-budget decisions for M01 sign-off. Replayed all 13 public spike tests successfully. M01 part 1 can proceed. [Review](../plans/12_review_codex.md)
