# Checked CCG declarations

Run `python3 -m src.frontend grammar/kernel.metta` from the repository root to check the seed's binary rule inventory. Run `python3 -m unittest discover -s tests/frontend -v` for typed application and composition examples, with source-located rejection fixtures.

The reader accepts parenthesized declarations and semicolon-to-end-of-line comments. The first declaration sets a finite slash depth. Atomic categories are `N`, `NP`, `S[fin]`, `S[bare]` and `S[to]`. A slash category is `(/ result argument)` or `(\ result argument)`. All categories in a source declaration are ground. Each declaration has a unique identifier within the file.

```lisp
(depth 4)
(field determiner unit universal existential)
(binary seed.fa FA)
(lex alice.name (alice) NP (lam (-> E P) (#0 alice)) ((determiner unit)) 0)
```

A lexical entry supplies its ID, nonempty token sequence, category, semantic template, field assignments and local cost. Templates support ontology symbols, indexed variables, typed lambdas and application. The checker resolves every symbol and requires the closed template to have the category's semantic type. Field declarations enumerate allowed values. Lexical costs are signed 64-bit integers or a single `(if field value yes-cost no-cost)` expression. Such an observation requires an assigned field with a declared value. Each checked lexical entry retains its published state, resolved cost and source location.

The seed profile admits FA and BA. For separate kernel tests, `--profile kernel` also admits degree-one harmonic FC and BC. `Grammar.combine(rule_id, left, right)` checks spans, slash direction and argument categories. Applicable rules return a typed parent meaning covering both children. Kernel tests also allow concrete `(unary id source-category target-category builder cost)` declarations. A unary builder must map the source meaning type to the target type. The checker topologically orders the category graph and reports the locations of declarations participating in a cycle.

The checked-in kernel contains the two seed rules. The full seed lexicon and construction-specific guards are later integration work. A successful check here covers declaration structure and types. End-to-end coverage of licensed sentences belongs to the grammar and parser suites.

## Seed guards and the packing key

The seed specializes lexical templates into finite **ground categories** before chart construction. Application compares those categories for exact equality. A chart node carries its span and the entire ground category. Its future applicability depends only on this key. Recipe and token provenance live on the lexical alternatives inside the node.

- An NP is `NP[unit]`, `NP[universal]` or `NP[existential]`. A simple past VP selecting a universal subject might be `(S[fin,simple,plain]\NP[universal])`. The ground transitive entry selects its object kind on the right and its subject kind on the left. The expander emits an object-wide entry only for different quantified kinds or at least one Unit. All surviving choices pack together as soon as their remaining categories agree.
- A simple VP has a plain or quick manner value. Postposed *quickly* maps plain to quick at the same clause form and subject kind. Control produces `S[fin,control]` or `S[bare,control]`. The infinitive marker consumes a simple bare VP at a Unit subject and produces `(S[to]\NP[unit])`. Both control frames use that complement. Their templates choose the already bound subject or recipient.
- The two-token *did not* selects a bare VP at Unit and produces a finite negative VP for the actual surface subject kind. The two-token *not every* selects N and then a positive finite VP at a universal subject, producing `S[fin,not-every]`. Each has one fixed binarisation. Neither can license a second application of its own operator.

The instantiated category in a rule witness is the complete result category including these annotations. The specialization choices are also part of lexical entry IDs. The grammar inventory and [witness contract revision](witness-v1.md) specify the encoding.
