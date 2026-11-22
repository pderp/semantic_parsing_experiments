# Quantified objects inside control clauses · v2 candidate

The v1 blind evaluation matched **52/52** sealed values. ClaudeOracle then found a separate problem with the bank: it could evaluate the embedded reading in *Alice promised Bob to review every paper*, but no event could store that reading as its content. Candidate v2 includes all **1,440** licensed embedded payloads, of which **1,280** have a quantified object. The build checks that every full-bank vector is distinct, nonconstant and stored by at least one event. The 256 worlds have exactly the same extensional facts as v1. Only their Content interpretation changes. [Independent v1 review](world_bank_check_v1.md) · [v2 specification and encoding](../spec/world-bank.md)

## Controlled comparisons

For each matrix verb (Promise, Persuade) and ordered pair of **distinct entity slots**, fix the matrix agent and recipient. Cross four bare transitive verbs with all 20 noun predicates, both object determiners and the two manner settings. Test the matrix truth vector alone. This isolates the Content relation: a different boxed payload table cannot make an otherwise indistinguishable matrix pass the comparison.

| Diagnostic counted | v1 | v2 |
| --- | ---: | ---: |
| Controller swaps giving identical matrix vectors | 7,680 / 7,680 | **0 / 7,680** |
| Determiner substitutions giving identical matrix vectors with the licensed controller | 3,840 / 3,840 | **0 / 3,840** |
| Licensed matrices constant across all worlds | 7,680 / 7,680 | **0 / 7,680** |

In eight designated sampled worlds, changing either the controller or the object determiner of *review a/every paper* alone changes whether the sole eligible matrix event stores the resulting vector. H14 and H15 also test sharing the controller under a quantified matrix subject or recipient. Both banks still distinguish all 6,400 mixed-scope comparisons for ordinary transitive sentences. [Hand probes and regression tests](../tests/semantics/test_world_bank.py) · [Audit program](../tools/world_bank_collisions.py)

## Residual collisions on public inputs

I parsed the 392 public determiner variants and all 4,000 released training input strings (SHA-256 `9867f655097d7271a3ced2d4c868cb3e82e1d60ede0050733a04fde88bd9ea5c`). The unit below is a **distinct exact reading**. The numerator counts readings sharing their complete matrix-and-payload signature with at least one other exact reading in the same stratum. The quantified-object row is a subset of control. The training inputs differ from ClaudeOracle’s independently sampled sentences, so the before/after columns use our same fixed inputs on both banks. [Public construction variants](../tests/reference/test_seed.py) · [Training release](corpus_v1.md)

| Inputs and reading stratum | v1 sharing a signature | v2 sharing a signature | Constant matrices, v1 → v2 |
| --- | ---: | ---: | ---: |
| 392 variants, control | 116/336 (34.52%) | 96/336 (28.57%) | 104 → 0 |
| 392 variants, control with quantified embedded object | 64/168 (38.10%) | 48/168 (28.57%) | 64 → 0 |
| 392 variants, non-control | 16/62 (25.81%) | 16/62 (25.81%) | 0 → 0 |
| 4,000 training inputs, control | 219/1,491 (14.69%) | **22/1,491 (1.48%)** | 445 → 1 |
| 4,000 training inputs, control with quantified embedded object | 90/828 (10.87%) | **4/828 (0.48%)** | **320 → 0** |
| 4,000 training inputs, non-control | 561/3,309 (16.95%) | 561/3,309 (16.95%) | 0 → 0 |

- The 96 control readings in the public variants form 48 pairs. Each pairs *a researcher did not …* with *not every researcher …* with the same positive control VP. In this fragment ∃x [Researcher(x) ∧ ¬P(x)] and ¬∀x [Researcher(x) → P(x)] have the same truth conditions. All six ambiguous public sentences and all 800 ambiguous training sentences still have two distinct signatures within the sentence.
- The 22 training control readings form 11 pairs. Replacing each name by the representative of its fixed entity slot and renormalizing makes both readings in each pair identical. In v1 there were 102 colliding control groups, of which 94 survived that alias check. For quantified embedded objects the number of groups surviving it fell from 41 to zero. These classifications concern the evaluated rows only.
- One training control still has an always-false matrix on v2: C2287, *A scientist persuaded every scientist to leave quickly.* Its embedded VP is intransitive. This is a limit of the finite sample even with a complete payload catalogue. Distinct canonical readings retain separate raw exact scores.

**Name decision (B4).** Keep the four entity slots in the signed pilot. Across the ten names, eight of 45 distinct unordered name pairs share a slot. A wrong name substitution within one class is inherently invisible to this bank. Exact-string evaluation exposes it, and finite agreement alone cannot earn credit. Ten distinct name slots would answer a stronger name-discrimination question and require a separately versioned world design. [Registered bank dimensions](../configs/pilot.yaml) · [Name interpretation](../spec/world-bank.md)

## New blind check

Candidate bank SHA-256 `2911d66da3d5888c34072d33b01a08587f20758948889db577c26a55ac13d0b6`. Probe SHA-256 `0e908cd93c73d2902e9afdebf5e93165f896827b3f06855c7f8a052f2433dc4b`. The released v1 inputs and sealed answers keep their original identity. A local replay reproduces all 52 previous values on v2. The new packet asks for 82 Boolean responses and 16 controller-slot vectors. ClaudeScope confirmed delivery of the three checksummed files to ClaudeOracle’s isolated inbox. Independent v2 answers and freeze are pending. [v2 bank](../fixtures/world_bank_v2.json) · [Answer-free probes](../fixtures/world_bank_blind_probes_v2.json) · [Ontology](../spec/ontology.yaml)

```sh
python3 tools/build_world_bank.py --check
python3 -m unittest tests.semantics.test_world_bank -v
python3 tools/world_bank_collisions.py --bank fixtures/world_bank_v1.json --training
python3 tools/world_bank_collisions.py --bank fixtures/world_bank_v2.json --training
```
