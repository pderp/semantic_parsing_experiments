# Stage 1 sign-off record · structural freeze

**Prepared by:** ClaudeScope, 21 November 2026. **Status: approved by the sponsor on 21 November 2026** (all five items, as written). Reviewed by CodexPrime (mailbox message 48).

Stage 1 freezes the public contract and the pilot configuration and allows D to reserve the two transfer panels. It does **not** authorize bulk annotation; that is stage 2 (plan 11).

## What is being frozen

| Artifact | SHA-256 |
| --- | --- |
| `spec/contract.md` (`seed-0.2-draft`) | `e15a49cf3861728f9e3f1412005272875d64ca9f48b6a295344549c4cbcdd5c1` |
| `spec/ontology.yaml` | `eaa0e2477a6005f751187f4c234ec6586fe03f27be8bce1f8d25d910f43896ab` |
| `configs/pilot.yaml` | `634b2dd3c8721c2a44413239e2991a82505725a6d02301a73dcca7299958b25c` (at `5c3ceb0`, with the reconciled fixture digest pinned) |
| `reports/census_seed-0.2-draft.md` | `9d016a1a3e3fcbd80bedceb39a07d476494ce9b95089542484a278e4a5629c1f` |
| `fixtures/prompts_v1.json` | `1d5ecb894e4a8db14b56603530451b3517430b2d7272f0b2dedebbb8ac3392da` |
| `fixtures/reconciled_v1.json` | `79ca957a558aa1ef09d65aec1f48a47f358ac89f9bdf763c53b9ce5fccdab581` |
| Original answers | CodexPrime `47c22114…`, ClaudeOracle `32d39a42…`, D `e664a1fa…`, sponsor worksheet `8b767460…` (full values in `reports/fixtures_v1_reconciliation.md`) |
| Private generator `gen.py` | `28c809cd26eba3a13cd95c0c33a92c3b86edc5545dd400afbb4dedfde62a4886` |
| Private `structures.py` | `20106bd6beb7b5b201f4d6f5780579092b3ecbce81cc77765d0c40ccfda84000` |
| Private `census.py` | `01da2040f22b0f39465ada4abaf1315d9883fe2ed6cf2b8fab21ce97a56e3f7a` |

On approval the contract and ontology are renamed from `seed-0.2-draft` to `seed-1.0` with no other change, and the digests are updated here.

## Evidence

| Requirement (plans 03, 07, 09, 11) | Evidence | State |
| --- | --- | --- |
| Scope spike | `spike/`, 13 checks | Met |
| Public contract answering the spike's seven questions | `spec/contract.md`; reviews 13 and 14 | Met |
| Ontology with closed vocabulary | `spec/ontology.yaml`, 56 surface tokens | Met |
| Family definition and census | Census report; 150 primary families; CodexPrime's review 15 | Met |
| Feasible allocation, 40 families per panel | Census report; supported in 20 of 20 trial seeds | Met at family level; row-level support checked at corpus generation |
| Pilot configuration with checked tables | `configs/pilot.yaml`, `tools/pilot_tables.py` | Met |
| Fixtures specified independently and reconciled | Three formal specifiers agree on all 12; reconciliation report | Met |
| Two readers specify the fixtures | One human reader (the sponsor) and three agent specifiers | **Met in a weaker form:** one human, not two |
| Sentinel access test | Both other sessions can read the private directory | **Run; result is that separation is procedural only** |
| Sponsor decision on runtime comparison | Conditional (plan 11) | Met |
| Cross-review | Reviews 12–16 | Met |

## What the sponsor is approving

1. The contract, ontology, and pilot configuration above as the authority for all later work. Any later change makes a new protocol version with a recorded reason.
2. **40 families per transfer panel** (39 single-reading and one two-reading), one funding look, the paired comparison on single-reading transfer inputs, absolute floors of 100/200 and 75/150 on all transfer inputs, and two-reading transfer reported descriptively.
3. **Control sentences keep one reading** (design Equation 22), although the sponsor's own reading of fixture F09 found two. Listed as a known limitation and a candidate for a later growth round. *Alternative:* license both orders now, which reopens the contract, the census, and the fixtures.
4. **Held-out data is procedurally separated only.** CodexPrime and ClaudeOracle can read the private directory and are instructed not to. Reports will say "procedurally separated". *Alternative:* run the evaluator under a separate Unix account or on another machine before M05 stores locked data.
5. **Human reading is done by one reader.** The 20% independent human second read in plan 05 is unavailable and will be reported as such. Future reading tasks follow `docs/reading_task_guidelines.md`.

## Scope of the freeze

Stage 1 freezes **what each sentence means**: the admitted language, the reading sets, the canonical text, and the two status axes. The evidence for these is of three separate kinds, and they should not be added together:

- three formal specifications (CodexPrime, ClaudeOracle, D) agree on the 12 fixtures, including both status axes;
- D's generator and ClaudeOracle's enumerator agree on the reading sets of all 392 determiner variants (admitted sentences only);
- CodexPrime's normalizer reproduces D's canonical text on 3,400 scrambled terms.

No complete reference parser exists yet, so this is not four parsers agreeing on every input.

It does **not** yet freeze **witness identity**, the exact key used to compare derivations between the reference parser and the oracle. ClaudeOracle found 15 underspecified points in that section of the contract (`reports/oracle_underspecified_v1.md`); most are settled only when the grammar bundle publishes its entry, rule, and recipe identifiers and its derivation shapes (M06). That section is frozen with the bundle as a later protocol version. Nothing in it changes a reading set, a panel, or a threshold.

## Known limitations at freeze

- The neural comparison mainly confirms a grammar that is ahead; equal systems pass about a quarter to a third of the time (census report).
- Only four families produce two readings.
- The formalism has plain truth conditions. What negation targets and what a sentence takes for granted (fixtures F06, F10) are not modelled.
- The 39 original companion checks from the design are unavailable; a replacement suite stands in.
- All formal specifiers are language-model agents working from one contract text.

## After approval

1. D reserves the two panels with a recorded seed and publishes only the manifest digests.
2. D runs the pre-score bootstrap check from review 15.
3. CodexPrime continues M06–M08; ClaudeOracle completes the exhaustive oracle.
4. Stage 2 needs from the sponsor: a teacher model and access, a spending ceiling, and a pilot operator.

## Approval

Sponsor decision on items 1–5: **approved, all five, as written** (21 November 2026).

## Actions taken on approval

| Action | Result |
| --- | --- |
| Panels reserved | 40 development-transfer families, 40 locked-transfer families, 70 training families. One draw; all 44 components occur in a training family. Smallest reserved family has 40 distinct sentences. |
| Panel manifest (private) | SHA-256 `75c6a7199387290e0d4a634d24258721bb91dd771440d13405c050fa98ad9bbe`; seed and algorithm are recorded inside it; file set read-only. |
| `reserve.py` (private) | SHA-256 `c9efc6348cffb5111ff44c6e38c90dcc7e6011caaf50866f7380b6deed83a13c` |
| Pre-score bootstrap check | `tools/prescore_check.py`; results in `reports/prescore_check.md` |
| Promotion to `seed-1.0` | Requested from CodexPrime (version strings and pinned digests only). The panel manifest cites the `seed-0.2-draft` digests; the family keys are unaffected by the rename. |
