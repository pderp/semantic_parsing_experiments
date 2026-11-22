# Exact semantics for seed-1.0

The reference implementation reads the sort of every symbol from the [public ontology](ontology.yaml). A term is an immutable tagged tuple. Use `const(name)`, `var(index)`, `lam(sort, body)` and `app(function, *arguments)`. In an open template, pass `typeof` and `normalize` the same tuple of free-variable sorts, nearest enclosing binder first. A call without a context checks that the term is closed. See the [contract](contract.md) for the semantic recipes and exact byte order.

`close(clause)` checks the root type and applies the always-true event continuation. `normalize(term)` retains the original term, its normal form, the protocol version and an ordered rewrite trace. To replay a step, follow its tuple offsets from the current root and replace the recorded before-term with its after-term. `reading_set(terms)` validates closed propositions and emits the canonical sorted, deduplicated JSON array as ASCII bytes. Final reading serialization checks saturation and requires an explicit base-sort lambda at every logical quantifier. Functional partial applications remain available in intermediate templates. Constructors such as `Box` remain inert data.

## Regression provenance

The design author's [checker](../docs/pre/semantic_reference_checks.py), [recorded result](../docs/pre/semantic_checks_result.json) and [LaTeX source](../docs/pre/ccg_semantic_parser_design.tex) arrived in commit `cb37eff`. Their sizes and SHA-256 digests match the [manifest](../docs/pre/validation_manifest.json). An isolated Python 3.14.4 replay reproduced the recorded JSON byte for byte with all 39 checks passing. The manifest records Python 3.12.14. The planning PDF has a different digest from the manifest PDF. A targeted comparison found agreement on the Appendix B families and the M02/M03 scope. The [39-row reconciliation](../reports/m02_author_checks.md) records the two PDF identities, each coverage decision, and the differences in notation, normalization, tense and model interpretation.

The [independent replacement suite](../tests/semantics/test_appendix_b.py) predates recovery. It covers 10 named properties, partially checks 16, and omits 12. The remaining author case uses event equality outside the seed ontology. Its finite-world evaluator, the public spike's scope examples and the 1,000 configured binding stress cases remain independent checks. The [recovered-case regressions](../tests/semantics/test_author_checks.py) translate the author's terms structurally, compare complete seed reading sets, and exercise the typed kernel, H closure and selected countermodels. Both suites use the same seed normalization protocol. The released seed-1.1 article revision retains the seed-1.0 normalizer.

Run from the repository root.

```sh
python3 -I docs/pre/semantic_reference_checks.py | cmp - docs/pre/semantic_checks_result.json
python3 -m unittest discover -s tests/semantics -v
python3 -m unittest discover -s spike -v
```
