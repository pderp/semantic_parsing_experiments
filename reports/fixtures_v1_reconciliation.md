# Fixture reconciliation · fixtures version 1

**By:** ClaudeScope as D, 21 November 2026. **For:** CodexPrime's review and the sponsor's stage 1 decision.

## Result

1. **The three formal specifiers agree completely.** CodexPrime, ClaudeOracle, and D each derived the 12 answers independently from the contract. They agree on every construction status, every decision, and every canonical string, byte for byte. No contract rule had to change.
2. **The human reader agrees with the contract on some sentences and not on others.** On the number of readings, the sponsor matches the contract on 4 of the 10 parsable sentences, is compatible or unsure on 2, and differs on 4. The differences are about what English allows, not about mistakes by anyone. They raise one decision for the sponsor (control sentences, below) and change how future human audits should be asked.

## Originals

All originals are published unchanged.

| Specifier | File | SHA-256 |
| --- | --- | --- |
| CodexPrime | `fixtures/answers_codexprime_v1.json` | `47c221145772e7e8b03999dd3d1eedce4beb825b574186ea50523bddfb5aab16` |
| ClaudeOracle | `fixtures/originals/answers_oracle_v1.json` | `32d39a420f80e069d6f67c778d818e5fd5dc97327ad33f1c65e3e5fa13580872` |
| D (sealed before the others answered) | `fixtures/originals/answers_d_v1.json` | `e664a1fab940997d183006e8d7e0ecfcda4d308389ae8bb1a1669966592bc125` |
| Sponsor | `fixtures/sponsor_worksheet.md` at commit `cac34b1` | `8b767460f0239bb442fec322da9dca87d88763bbf3748ebab6910061f41de90f` |
| Reconciled set | `fixtures/reconciled_v1.json` | `79ca957a558aa1ef09d65aec1f48a47f358ac89f9bdf763c53b9ce5fccdab581` |

Each agent's digest matches the one it sent by mailbox before any exchange (messages 26 and 30). D's digest was published in `fixtures/README.md` before either agent answered.

**Independence.** CodexPrime and ClaudeOracle each wrote their own code from the contract. D's generator builds readings from the construction tree with no chart. ClaudeOracle has never read this repository. All three share one model family or one contract text, so agreement shows the contract is unambiguous to these readers; it does not show the contract matches English.

## Formal answers and the sponsor's reading

"Contract" is the reconciled formal answer. The sponsor's column uses the second-pass answer (B2) where one was given; first-pass answers are in the worksheet.

| Item | Sentence | Contract | Sponsor: number of readings | Comparison |
| --- | --- | --- | --- | --- |
| F01 | Bob cited Ava. | 1 reading | One | Agree |
| F02 | A student evaluated every thesis. | 2 readings: one student for all theses; for each thesis, some student | One (one student for all) | **Differ.** The sponsor does not get the reading where the students vary. |
| F03 | Every editor discussed every report quickly. | 1 | One | Agree |
| F04 | Dan did not arrive. | 1 | One | Agree. The sponsor notes the time is unspecified; the contract records only that the event is past. |
| F05 | A scholar did not cite every dataset. | 1: some scholar failed to cite all of them | Unsure | Compatible. The sponsor's paraphrase is the contract's reading. |
| F06 | Not every analyst evaluated a proposal quickly. | 2: the two scope orders of *every analyst* and *a proposal* under the negation | One | **Differ.** The sponsor reads it as "all evaluated, some not quickly". That situation makes the contract's readings true, but the contract does not require that every analyst evaluated anything. |
| F07 | Not every reviewer discussed every abstract. | 1 | One | Agree |
| F08 | Gia promised a student to speak quickly. | 1: Gia is to speak; the speaking is quick | Unsure | Compatible. The sponsor has Gia speaking quickly. |
| F09 | Every investigator persuaded a scientist to leave. | 1: for each investigator, some scientist | Two: one particular scientist, or different scientists | **Differ.** The contract fixes the order in control sentences (design Equation 22). |
| F10 | Hugo did not persuade Eva to review every preprint quickly. | 1: no such persuading happened | Two | **Differ.** Both of the sponsor's readings assume some persuading happened and locate the negation on *every* or on *quickly*. The contract has neither. Both sides agree no reviewing follows. |
| F11 | Cara reviewed the article. | No parse: *the* is not in the vocabulary | Fits the language: yes | Differ on question C only (provisional; see below). |
| F12 | Finn quickly arrived. | No parse: *quickly* must come last | Fits the language: no | Agree |

Counts on the number of readings, 10 parsable sentences: agree 4, compatible or unsure 2, differ 4. Question C was declared provisional before these answers were compared, because the worksheet's description of the language was unclear (`docs/reading_task_guidelines.md`), so F11 is not counted.

## What the differences mean

1. **Inverse scope (F02).** The contract licenses both orders for a mixed pair of quantifiers on a simple transitive verb, as the design does (Equations 16–17). The sponsor accepted this for the worksheet's own example (*every … a*) but did not find the second reading for *a … every*. This is a well-known asymmetry in English judgments. No change proposed: the contract follows the design.
2. **Control (F09).** The sponsor finds two readings where the contract allows one. Review 06 already noted that such sentences "arguably" have more readings than Equation 22 gives. **Decision for the sponsor:** keep the single reading for this pilot (recommended, since it is the design's rule and the census and configuration are built on it) or license both orders, which changes the contract, adds two-reading families, and repeats the census. If kept, it is listed as a known limitation and a candidate for a growth round.
3. **What negation targets (F06, F10).** The sponsor reads *not … quickly* as denying the speed while taking the event for granted. The formalism has plain truth conditions and no notion of what a sentence takes for granted. This is outside the pilot's scope and is recorded as a limitation.
4. **Human audits cannot ask "how many readings?".** One careful reader's count differs from the public scope policy on 4 of 10 sentences. Plan 07 already says a reader applies the public policy and does not substitute their own judgment. Future reading tasks therefore ask concrete questions the reader can answer from the sentence (who did it, to whom, who is to act in the embedded clause, what is negated, whether the event is said to have happened), and conformity to the scope policy is checked mechanically by the independent implementations.

## Reading cost

The sponsor took 32 minutes for the first six sentences under unclear instructions and 31 minutes for the remaining six plus second-pass answers: about 63 minutes for 12 sentences. The worksheet estimated 30–45. Per-sentence time after guidance was about 4 minutes. This is the first measurement for the reader budget in plan 05.

## Worksheet defects (ClaudeScope's)

- The language description was unlabelled and used undefined notation.
- "Meaning" was not defined; vagueness and distinct readings were not separated.
- Two prompts were printed inside answer slots (F08 and F09, question D). The sponsor reasonably wondered whether they had leaked from elsewhere. They were in the original file (commit `285294b`).

Rules covering all three are in `docs/reading_task_guidelines.md`.
