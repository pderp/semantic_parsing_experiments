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

Revised candidate bank SHA-256 is `a431af772c4c6486c1ca32569126c82a6ce17afe6e4e6e92f3747b1569085f10`. The byte encoding is compact, ASCII, key-sorted JSON with one trailing newline. The file contains the ontology digest, fixed names and explicit world facts and content vectors. ClaudeScope has the revised bank and a [blind question sheet](../fixtures/world_bank_blind_probes_v1.json) to deliver to ClaudeOracle's separate, checksummed inbox. The 22 questions request 44 H-world truth values and two four-slot payload tables. Independent review is pending. [Bank](../fixtures/world_bank_v1.json) · [Generator](../tools/build_world_bank.py) · [Hand probes](../tests/semantics/test_world_bank.py)

Each extensional predicate is a bit mask. Unary bit j denotes slot j of its declared sort. Role bit 4v+e denotes event v and entity e. Missing predicates have empty extensions. For sampled world attempt n, starting at zero, take SHA-256 of the ASCII string `20261119/n/label`, where n is its decimal representation. Interpret the digest as an unsigned little-endian integer. For an extensional predicate, label is its case-sensitive name and the low 4, 3 or 12 bits give its initial mask. Two draws receive the scope conditions below. Reject a duplicate extensional fact set and advance the attempt. Also verify uniqueness of the 256 completed worlds including content.

Content descriptors are sorted by verb predicate in ASCII order, then by the agent slot, then the theme slot for transitive verbs, then the Quick flag (false before true). Only the four simple intransitive and four simple transitive frames enter this 160-item catalog. Descriptors require a matching event, agent, optional theme and optional Quick anywhere in the world. Bare payloads impose no Past condition. For sampled event v, draw two catalog indices using labels `content/v/0` and `content/v/1` and reduce modulo 160. Store the set of their distinct full-bank vectors. Exhaustive worlds store no content. Hand worlds use the explicit descriptors above. Candidate submissions play no role in world or payload selection.

## Scope separation and remaining collisions

Of the 176 sampled worlds, 174 retain their original extensional draw. Condition the **first two draws with neither Past nor Quick present** (S065 and S091). These otherwise offer no past event witness for a finite positive matrix. Select one unordered entity-slot pair from the six lexicographic pairs using the draw with attempt 0 and label `scope/slots`, modulo six. For both worlds the pair is {2,3}. Give every noun these two members. Give all four transitive predicates, Past and Quick to events 0 and 1 only. Assign each event one distinct agent from the pair. In S065 each event has its own agent as its sole theme. In S091 both events have both themes. Other predicates and the content descriptor draws follow the original recipe. Content vector values throughout the file are regenerated against the revised bank.

For any ordered pair of noun restrictors, including two uses of the same noun, S065 makes “each x has some y” true and “some y works for every x” false. With an existential subject and universal object the two truth values switch. In S091 both orders are true. Quick and Past on both events give the same contrasts for modified finite verbs. Taking the outer negation preserves every distinction. The 174 unconditioned draws retain their independent variation in noun extensions and verb relations.

| Public diagnostic | First candidate | Revised candidate |
| --- | ---: | ---: |
| Two readings within one of the 392 public variant sentences collapse to one signature | 0/6 ambiguous sentences (0%) | 0/6 (0%) |
| Distinct exact sentence-level reading sets in shared-signature groups | 128/392 (32.65%), 64 pairs | 128/392 (32.65%), the same 64 pairs |
| Distinct individual readings in shared-signature groups across all variants | 132/398 (33.17%), 66 groups | 132/398 (33.17%), 66 groups |
| Indistinguishable scope pairs across the entire transitive noun grid | 323/6,400 (5.05%) | 0/6,400 (0%) |
| Indistinguishable pairs among the first 1,500 released training inputs | 14/317 ambiguous sentences (4.42%) | 0/317 (0%) |

The 392-variant suite uses one lexical realization per construction/determiner variant. It has 386 singleton and six ambiguous sentences. Across all sentences, both banks yield 328 behavioral reading sets for 392 exact sets and 332 behavioral signatures for 398 distinct exact readings. Cross-sentence collisions include differences the bank misses in boxed control. For example, “Alice did not persuade a reviewer to cite Bob” and “every researcher did not promise Bob to cite Bob” still share a signature. Such a collision cannot justify scoring those answers as interchangeable. The grid separately checks 20 subject nouns × 20 object nouns × four transitive predicates × two determiner orders × two manner settings, using the event relations from the serialized bank. The 1,500-row recheck used public input strings and reference parses only. These are diagnostics used during design; none is a held-out estimate.

I also evaluated a separate pair of conditioned worlds for each verb at the end of the sampled block. It separated the full grid but increased the number of colliding sentence-set groups from 64 to 66. The chosen two shared worlds preserve more of the original sample. Counts and exact denominators can be replayed for either stored revision. [Measurement tool](../tools/world_bank_collisions.py) · [Public variant definitions](../tests/reference/test_seed.py)

```sh
python3 tools/world_bank_collisions.py
old_bank=$(mktemp)
git show fa23b6e:fixtures/world_bank_v1.json > "$old_bank"
python3 tools/world_bank_collisions.py --bank "$old_bank"
rm "$old_bank"
```

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
