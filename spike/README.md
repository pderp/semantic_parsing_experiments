# Scope spike

A disposable Python spike for the first task in `docs/plans/09codex_plan.md`. It is not the reference parser and nothing later should import it.

**Result: pass.** *Every researcher reviewed a paper* parses to one packed root with two witnessed readings, and the registered world separates them. All 13 checks pass on Python 3.14.4 with the standard library only.

## Replay

Run from the repository root:

```
python3 spike/scope_spike.py                 # prints the result record; exit 0 on pass
python3 -m unittest discover -s spike -v     # 13 checks
```

`output.json` is the saved output of the first command. It contains the readings, a derivation witness for each, the separating world, and the result digest.

## What was checked

| Requirement from the plan | Evidence |
| --- | --- |
| Tokenize; map *reviewed* to lemma *review* with a past-tense feature | `MORPHOLOGY`; `Past(e)` appears in both readings |
| Two scope recipes at one transitive category | Node `(2, 3, (S\NP)/NP)` has two lexical edges |
| One packed root, both recipes reachable | One root node with one edge; two derivations unpack from it |
| Two witnessed, distinct normalized readings | `test_two_distinct_normalized_readings`, `test_each_witness_replays_to_its_reading` |
| Separating world: researcher-wide true, paper-wide false | `test_separating_world` |
| Reversed lexical insertion order gives the same readings and tie order | Identical result under reversal and 20 seeded shuffles; digests match in `output.json` |

Extra checks, all cheap: every lexical term has the type its category requires; *Alice reviewed Bob* gives two derivations and one meaning, so the decision is `accepted`; swapping the names changes the meaning; an unparseable input reports `no_parse` and `abstain`; an ill-typed application is rejected; substitution does not capture.

The two readings, as the normalizer prints them:

```
forall x0. (Researcher(x0) -> exists x1. (exists e2. (Agent(e2, x0) & Past(e2) & Review(e2) & Theme(e2, x1)) & Paper(x1)))
exists x0. (forall x1. (Researcher(x1) -> exists e2. (Agent(e2, x1) & Past(e2) & Review(e2) & Theme(e2, x0))) & Paper(x0))
```

## Not covered

The spike has forward and backward application only. It has no composition, type raising, unary rules, negation, control, manner, `Box`, resource budgets, or `truncated` status. The chart key is span and category; there is no separate interface or control field.

## Contract questions for M01

Each of these needed a choice the plans and the design leave open. The spike's choice is noted; none is binding.

1. **Conjunct order.** The design says to sort conjuncts "by a canonical structural order" without defining it. The spike sorts by canonical text, which places a quantified conjunct before its restrictor: `exists e. (...) & Paper(x)`. The design's own Equation 18 prints the restrictor first. My first test expectation assumed the design's order and failed. The contract must define the sort key exactly, because the generator owner and the grammar author must produce identical text independently.
2. **Tie order between equal-cost readings.** Both scope recipes cost 10. The spike breaks the tie by the witness's canonical JSON text, which puts the object-wide reading first only because of how the entry names sort. The contract needs a stated tie rule, and probably a deliberate default order.
3. **Canonical serialization.** The spike uses de Bruijn indices in an s-expression (`normalized` in the output) and a separate display form with generated names (`pretty`). The contract should say which one is the compared text.
4. **Where `Past` lives.** The spike adds `Past(e)` to the verb frame from a morphological feature. An auxiliary such as *did* would have to add it through the event continuation instead. Both must normalize to the same conjunct position, which the sort in item 1 gives for free.
5. **Tokenization.** Lower-casing and stripping one final period were enough here. Names are lower-cased too, so `alice` is the constant.
6. **Restricted quantifiers.** `every` is `ForallE` over an implication and `a` is `ExistsE` over a conjunction, following the design. The existential's restrictor is therefore an ordinary conjunct and gets sorted with the scope, which is what produces item 1.
7. **Decision for two readings.** The spike returns `ambiguous` with both readings, as plan 03 proposes.
