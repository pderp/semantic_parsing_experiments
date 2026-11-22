# M02 reconciliation with the design author's 39 checks

The original checker passed **39/39**, and its standard output matched the author's recorded JSON byte for byte. The independent M02 replacement suite exercised all seven families. Its clearest gaps were category-level composition with a raised NP, full object-control binding with a quantified recipient, two nonempty negation countermodels, and the quantified negation scope contrast. The recovered cases now run alongside the independent tests. Seven sentences also have an executable comparison between the author's propositions and the seed parser's complete reading sets. [Original checker](../docs/pre/semantic_reference_checks.py) · [Recorded names and results](../docs/pre/semantic_checks_result.json) · [New comparisons](../tests/semantics/test_author_checks.py)

## How to read the crosswalk

The middle column grades the **pre-recovery M02 replacement suite**, at its original checkpoint. *Covered* means it asserted the same semantic property, possibly with different predicates or a separately constructed formula. *Partial* identifies the exact weaker check. *Missing* means the replacement had no assertion for the named behavior. *Outside seed* marks a deliberate ontology difference. The last column identifies executable evidence from this reconciliation and, where relevant, a pre-existing spike or frontend test. FA and BA apply a function forward and backward. FC and BC compose two functions in the respective direction. In the companion, P is a proposition and H is a clause awaiting an event continuation. [Replacement suite](../tests/semantics/test_appendix_b.py) · [Frontend kernel](../tests/frontend/test_kernel.py) · [Scope spike](../spike/test_scope_spike.py)

| # | Author's check, in recorded order | Earlier M02 coverage | Comparison now |
| ---: | --- | --- | --- |
| 1 | de Bruijn beta reduction avoids capture under a shadowing binder | Partial. Open substitution across differently typed binders. | The named frontend and translated author term both reduce to two E lambdas whose body is #1. |
| 2 | unbound named semantic variable rejected | Partial. Rejected a dangling index and an unknown constant. | A free identifier in a named frontend declaration fails symbol checking. |
| 3 | entity cannot be used directly as an NP semantic value | Missing. Checked a raised name's type only. | An NP lexical entry with bare entity meaning fails category typing. |
| 4 | FA then BA gives Alice reviewed Bob with correct roles | Missing. No named transitive FA/BA derivation. | The seed parse and typed H kernel recover the author’s Agent and Theme. |
| 5 | FC with licensed forward raising preserves the same sentence meaning | Partial. Raised-name shape only. | A licensed forward NP raise followed by FC and FA recovers the same closed sentence in the kernel. |
| 6 | BC has the correct order f(g(x)) and semantic type | Missing. No BC in M02. | The H kernel composes the author's NP identity and bare VP. The earlier frontend also checks order with noncommuting functions. |
| 7 | incompatible FA categories rejected | Missing. Wrong semantic application type only. | The kernel rejects FA of a transitive verb and N in the NP slot. |
| 8 | every researcher / a paper subject-wide normal form exact | Covered. Exact subject-wide form in the pair. | The parser's two-element set equals both mapped author forms. The H subject-wide term closes to this member. |
| 9 | every researcher / a paper object-wide normal form exact | Covered. Exact object-wide form in the pair. | The H object-wide term closes to the other member. The earlier spike also identifies each lexical witness. |
| 10 | two scope templates agree for proper names | Missing. Repeated a formula to test serialization only. | The two lexical scope witnesses for names have the same seed reading and match the companion. |
| 11 | finite model: each researcher has a paper, so subject-wide is true | Partial. The two truth values were sorted before assertion. | The mapped subject-wide term is true in the author's separating world. The earlier spike also labels it. |
| 12 | finite model: no shared paper, so object-wide is false | Partial. Same unordered truth-value check. | The mapped object-wide term is false in that world. The earlier spike also labels it. |
| 13 | promise object-then-VP argument order and subject control exact | Partial. Built subject-control terms without applying the lexical slots. | The parsed named promise sentence has the exact mapped recipient and boxed subject. |
| 14 | persuade object-then-VP argument order and object control exact | Partial. Checked the embedded recipient as a substring. | The parsed named persuade sentence matches the whole proposition, including both matrix roles. |
| 15 | control verb rejects a VP in its NP argument slot | Missing. No category rejection for this slot. | Passing a to-VP as the control verb's first complement fails FA. |
| 16 | quantified control subject reference shared without requantification | Covered. Full quantified subject formula matched the public contract. | The parsed quantified promise sentence equals the author's single-universal formula. |
| 17 | quantified controlled object reference shared without requantification | Missing. The earlier recipient was a name. | The quantified persuade recipient scopes once and is shared inside Box. The entire parsed term matches. |
| 18 | promise can hold when no leaving event exists | Covered. Promise held with a false embedded proposition. | The parsed promise sentence holds in the seed evaluator with a boxed false value and no Leave facts. |
| 19 | persuade can hold when no leaving event exists | Covered. Persuade held in the same countermodel. | The parsed persuade sentence holds in that model as well. |
| 20 | negative event statement true with no event witness | Covered. Negated event existential true on an empty domain. | The author term and finite seed parse give true there. |
| 21 | hoisting event existential across negation changes truth | Covered. Hoisted existential false on an empty domain. | The translated hoisted term gives false in the same seed evaluator. |
| 22 | negative statement true with nonempty event domain but no leaving witness | Missing. Only the empty domain was exercised. | The negated statement holds with one unrelated event. |
| 23 | existential hoisting also fails in a nonempty event-domain countermodel | Missing. No mixed countermodel. | With a leaving and an unrelated event, the negative is false and its hoisted counterpart true. |
| 24 | two fresh event binders may denote the same event | Covered. Two binders could share one event. | The translated Review/Leave formula holds with exactly one event. |
| 25 | explicit event inequality forces distinct denotations | Outside seed. Used host inequality and rejected an unlicensed symbol. | The original Not(eqV) check passes. The seed rejects this exact eqV term as an unknown symbol. |
| 26 | H: FA/BA, types and root closure recover baseline sentence exactly | Partial. Closed an H intransitive only. | The project's close on H and the typed FA/BA derivation both recover the mapped P transitive. |
| 27 | H: FC with licensed raising recovers baseline sentence | Missing. No H raised/composed derivation. | The project kernel raises the NP, composes, applies the object and closes to the P baseline. |
| 28 | H: BC remains correctly typed | Missing. No H backward composition. | The project kernel returns the right type and the original VP normal form after BC. |
| 29 | H: subject-wide quantified closure recovers baseline exactly | Partial. Expected closed form only. | Project closure on the author's subject-wide H term reproduces the separate P baseline. |
| 30 | H: object-wide quantified closure recovers baseline exactly | Partial. Expected closed form only. | Project closure on the author's object-wide H term reproduces the separate P baseline. |
| 31 | H: subject control closes embedded event continuation inside Box | Partial. Asserted properties of an already constructed box. | Closing the complete H promise example matches P, including closure inside Box. |
| 32 | H: object control closes embedded event continuation inside Box | Partial. Checked the boxed named controller. | Same comparison for persuade, with the object as the embedded agent. |
| 33 | H: quantified controller is still opened once | Partial. Compared the closed quantified formula only. | H promise closes to the single-universal P result. The independent seed parse has those same bytes. |
| 34 | H: manner constraint is inside the same event binder | Partial. Tested manner on Leave via a supplied continuation. | Closing the author's modified H review and parsing the full sentence both recover the exact same-binder expression. |
| 35 | H: a different quick event cannot satisfy the modifier | Covered. A distinct quick event failed for Leave. | The parsed modified review fails with a different quick event. |
| 36 | H: same review event satisfies its manner modifier | Covered. Same-event Quick succeeded for Leave. | The parsed modified review holds when its review event is quick. |
| 37 | H: negation preserves its event existential and root closure | Partial. Tested P negation but did not close a negative H. | Project closure on the author's negative H equals its tenseless P baseline. |
| 38 | H: negative statement needs no actual head-event witness | Partial. Tested the empty-domain P property only. | The translated closed H and the finite seed negative are both true on the empty domain. |
| 39 | H: every-not and not-every remain distinct scope readings | Missing. No partial-leaving world contrasting the two operators. | Both seed parses and both mapped companion terms distinguish the two orders on that world when the leaving event is past. |

## Conventions that affect comparisons

- Both systems use de Bruijn indices after named binding resolution. The test adapter maps Entity/Event/Prop/Intension to E/V/P/I, transfers arrow types recursively, and preserves all indices, arguments and lambdas. The symbol map is researcher → Researcher, paper → Paper, allE → ForallE, existsE → ExistsE, existsV → ExistsV and Imp → Implies. The author's finite-world individuals r1, r2, p1 and p2 are domain values in the comparison.
- The author checks beta-normal trees and strips conjunctions with Top on H closure. The seed additionally flattens maximal conjunctions, removes Top, keeps multiplicity, sorts conjuncts by canonical ASCII text and right-associates. Each side of a formula comparison uses the seed convention before byte comparison. The original checker's recorded JSON is compared directly, without conversion.
- Checks 1–25 use an S=P baseline. Checks 26–39 refine S to H, while NP stays a generalized quantifier. The seed has H-valued clauses and closes a completed root with an always-true event continuation. Its typed kernel admits FC, BC and an explicit NP-raising rule in the regression. The released seed grammar uses application only.
- The author's negation micro-model uses untensed *leave*. Finite seed *did not* contributes Past below Not. In an empty world, or a world where every event is past, the selected tests agree. With only a nonpast Alice-leaving event, the author negative is false and the seed's *Alice did not leave* is true. The regression demonstrates this difference directly.
- The author evaluates Box as a quoted term and environment. Its Content relation accepts quoted content on designated events. The seed normalizer preserves Box as a constructor. The independent M02 test evaluator represents a box by its truth values across the supplied worlds at the same outer assignment. The promise and persuade tests establish nonveridicality in their respective models. Arbitrary intensional equality remains outside this comparison.
- The seed ontology omits event equality. It expresses two fresh binders that can denote one event. The author's additional object-language inequality in check 25 has no seed spelling. The checker and the seed's rejection both have regression coverage. [Seed semantics and ontology](../spec/normalization.md) · [Seed contract](../spec/contract.md)

## Source and reproduction

The recovered TeX, checker and JSON match all three corresponding byte lengths and SHA-256 entries in the author's manifest. An isolated run under Python 3.14.4 reproduced the JSON SHA-256 `885180a670d259170fff2e6e009bd16cddee3f63828f2a4e10b7cecfc5f737a7`. The manifest records Python 3.12.14 for the author run. [Manifest](../docs/pre/validation_manifest.json)

Both document records identify v1.1 of 18 November. The planning PDF is 725,632 bytes (SHA-256 `ce8f47176d1bdfaca3b63dfde6850838f00ac330027c2cd3766ce3c1141e1b56`). The manifest lists a 575,223-byte PDF (`f94cd589059cff3ecd83b409bc1c8e0eba187863d8c55b5faa5c4eba3f19029b`). A targeted comparison of the planning PDF text and the recovered TeX found the same Appendix B family counts (7, 5, 5, 2, 4, 2, 14), the same P-to-H division and the same M02/M03 division between semantic reference and checked rule kernel. These sections support the existing plan. The cause of the different PDF bytes and equivalence of the complete documents remain undetermined. [Recovered TeX](../docs/pre/ccg_semantic_parser_design.tex)

Run from the repository root.

```sh
python3 -I docs/pre/semantic_reference_checks.py | cmp - docs/pre/semantic_checks_result.json
python3 -m unittest discover -s tests/semantics -v
python3 -m unittest tests.frontend.test_kernel tests.reference.test_seed -v
python3 -m unittest discover -s spike -v
```
