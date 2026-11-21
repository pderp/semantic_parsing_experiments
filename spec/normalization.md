# Exact semantics for seed-0.2-draft

The reference implementation reads the sort of every symbol from the [public ontology](ontology.yaml). A term is an immutable tagged tuple. Use `const(name)`, `var(index)`, `lam(sort, body)` and `app(function, *arguments)`. In an open template, pass `typeof` and `normalize` the same tuple of free-variable sorts, nearest enclosing binder first. A call without a context checks that the term is closed. See the [contract](contract.md) for the semantic recipes and exact byte order.

`close(clause)` checks the root type and applies the always-true event continuation. `normalize(term)` retains the original term, its normal form, the protocol version and an ordered rewrite trace. To replay a step, follow its tuple offsets from the current root and replace the recorded before-term with its after-term. `reading_set(terms)` validates closed propositions and emits the canonical sorted, deduplicated JSON array as ASCII bytes. Constructors such as `Box` remain inert data.

## Regression provenance

The workspace supplied the design PDF, SHA-256 `ce8f47176d1bdfaca3b63dfde6850838f00ac330027c2cd3766ce3c1141e1b56`. Its Appendix B, Table 8, describes seven families and gives counts for 39 companion checks. The author's checker, recorded result and LaTeX source have been requested through ClaudeScope. The [replacement suite](../tests/semantics/test_appendix_b.py) derives its own examples for each family. Its finite-world evaluator is a test helper. The public spike supplies two known scope outputs and separating worlds. The public contract supplies the quantified-controller regression. Binding stress uses the count and seed from the pilot configuration.

Run these suites from the repository root.

```sh
python3 -m unittest discover -s tests/semantics -v
python3 -m unittest discover -s spike -v
```
