# Seed-1.1 finite-world bank

This public bank gives a behavioral diagnostic for disagreements on exact reading sets. Exact match, human adjudication, and the investment rules retain the definitions in the signed pilot. The finite signatures cannot distinguish all formulas. [Pilot configuration](../configs/pilot.yaml) · [Scoring procedure](../docs/plans/07codex_plan.md)

## Fixed interpretation and ordering

Every world has entity slots 0–3 and event slots 0–2. Names have fixed denotations across worlds. Slot 0 denotes Alice, Cara and Gia. Slot 1 denotes Bob, Dan and Hugo. Slot 2 denotes Ava and Eva. Slot 3 denotes Ben and Finn. Those aliases necessarily agree on this bank, even where their canonical strings differ. All 20 noun predicates range over all four slots. All ten verb predicates, Past and Quick range over all three event slots. Agent, Theme and Recipient range over all 12 ordered event/entity pairs. Any combination consistent with those sorts is eligible.

The ordered bank starts with 64 exhaustive worlds, followed by 16 contrast worlds and 176 distinct sampled worlds. In the exhaustive block, Researcher holds of 0 and 1, Paper of 2 and 3, and Past of events 0 and 1. For event i in {0,1}, bits 3i, 3i+1 and 3i+2 of the world number set Review(i), Agent(i,i), and Theme(i,i+2). All other facts are empty.

## Contrast worlds for independent review

For these 16 worlds Researcher holds of 0 and 1 and Paper of 2 and 3. All listed verbs belong to the indicated event. A finite event has Past only when specified. Agent and Theme in the review rows are ordered. A listed content descriptor means that the matrix event stores the full-bank vector for that payload. Unlisted facts are false.

| ID | Additional facts | Expected observations |
| --- | --- | --- |
| H00 | Past review by Alice of Bob | Alice reviewed Bob true, Bob reviewed Alice false. |
| H01 | Past review by Bob of Alice | Same two propositions false, true. |
| H02 | Past reviews by slots 0 and 1 of papers 2 and 3 respectively. Event 2 is also Past. | Each researcher reviewed a paper true, a shared paper false. |
| H03 | Past reviews by slots 0 and 1, both of paper 2 | Both scope readings true. |
| H04 | No event facts | Neither Alice nor Bob left. Both their finite negative clauses hold. |
| H05 | Alice alone left in the past | Every researcher did not leave false, not every researcher left true. |
| H06 | Bob alone left in the past | Alice left false, Bob left true. |
| H07 | A single past quick leaving by Alice | Alice left quickly true. |
| H08 | A past leaving by Alice and a different quick event | Alice left true, Alice left quickly false. |
| H09 | A leaving by Alice without Past | Bare leaving has a witness. Alice left false, Alice did not leave true. |
| H10 | A quick past promise by Alice to Bob, with bare leaving by slot 0 as content | Promise true with no actual leaving. Embedded quickly false despite Quick on the matrix event. |
| H11 | Past persuasion by Alice of Bob with bare leaving by slot 1 as content | Persuade true with no actual leaving. Subject-control substitution fails. |
| H12 | Same promise roles as H10, content for slot 1 instead, no Quick | The subject-control promise is false. |
| H13 | Same persuasion roles as H11, content for slot 0 instead | The object-control persuasion is false. |
| H14 | Two past promises, one by each researcher to Bob, each storing its own agent's leaving | Every researcher promised Bob to leave true. Substituting Bob for both boxed controllers is false. |
| H15 | Two past persuasions by Alice, one of each researcher, each storing its recipient's leaving | Alice persuaded every researcher to leave true. Substituting Alice for both boxed controllers is false. |

Content is fixed independently of submitted formulas. For each descriptor, compute the truth of its specified simple event condition in every world at the named slots. Its 256-bit vector is the intensional value stored by the specified matrix event. A candidate Box computes its payload at the same outer assignment in each world. Content compares the resulting vector for equality. Matrix evaluation and payload evaluation leave every world's event facts unchanged. [Original bank recipe](../docs/plans/05codex_plan.md)

## Reproduce the bank

Candidate bank SHA-256 is `88c1d18d63d46a52e9bb2167b7f7539481238b253a3296c9ce28c413a91cc025`. The byte encoding is compact, ASCII, key-sorted JSON with one trailing newline. The file contains the ontology digest, fixed names and explicit world facts and content vectors. The hand contrast specification and bank digest have been submitted for independent review. Scoring can reference the signed-off digest once that check returns. [Bank](../fixtures/world_bank_v1.json) · [Generator](../tools/build_world_bank.py) · [Hand probes](../tests/semantics/test_world_bank.py)

Each extensional predicate is a bit mask. Unary bit j denotes slot j of its declared sort. Role bit 4v+e denotes event v and entity e. Missing predicates have empty extensions. For sampled world attempt n, starting at zero, take SHA-256 of the ASCII string `20261119/n/label`, where n is its decimal representation. Interpret the digest as an unsigned little-endian integer. For an extensional predicate, label is its case-sensitive name and the low 4, 3 or 12 bits give its mask. Reject a duplicate extensional fact set and advance the attempt. Also verify uniqueness of the 256 completed worlds including content.

Content descriptors are sorted by verb predicate in ASCII order, then by the agent slot, then the theme slot for transitive verbs, then the Quick flag (false before true). Only the four simple intransitive and four simple transitive frames enter this 160-item catalog. Descriptors require a matching event, agent, optional theme and optional Quick anywhere in the world. Bare payloads impose no Past condition. For sampled event v, draw two catalog indices using labels `content/v/0` and `content/v/1` and reduce modulo 160. Store the set of their distinct full-bank vectors. Exhaustive worlds store no content. Hand worlds use the explicit descriptors above. Candidate submissions play no role in world or payload selection.

## Evaluate a meaning

The Python API accepts a closed seed term or a string. It normalizes and type-checks the reading. The matrix value is a 64-digit lowercase hex string, with bit i denoting truth in world i (world zero is the least significant bit). Each Box also emits its normalized argument path and its payload vectors at all assignments to enclosing binders. Binder sorts are nearest-first. Assignments run in lexicographic order of slot indices. This preserves bound controllers when evaluating a payload in a different world. [Shared evaluator](../src/semantics/world_bank.py)

```python
from src.semantics.world_bank import load_bank
bank = load_bank()
signature = bank.signature("(ExistsV (lam V (And (Leave #0) (Agent #0 alice))))")
behavioral_set = bank.signature_set(["(Researcher alice)", "(Researcher bob)"])
```

`signature_set` pairs each matrix vector with sorted payload tables, including their enclosing binder sorts and assignment order. Reordering siblings does not change a table solely because its occurrence path moved. Formulas with different binder structures can have incomparable payload tables, even if their matrices agree. Preserve both original readings and signatures for blinded adjudication. An unknown symbol, ill-typed term, or open reading yields a validation error. No automatic credit follows from equality on the bank. All seed-1.1 predicate signatures and logical constructors have an interpretation, including Box and Content. No candidate eligibility rate has been measured.

```sh
python3 tools/build_world_bank.py --check
python3 -m unittest tests.semantics.test_world_bank -v
```
