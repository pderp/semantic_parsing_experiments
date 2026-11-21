# Review of M02 (semantic core) and the first M03 kernel

**Reviewed:** `src/semantics/`, `spec/normalization.md`, `tests/semantics/` at `8cb67ed`; `src/frontend/`, `spec/dsl.md`, `grammar/kernel.metta`, `tests/frontend/` at `05e0078`. **Reviewer:** ClaudeScope, 21 November 2026.

## What I ran

- `python3 -m unittest discover -v`: 16 tests pass. `python3 -m unittest discover -s spike`: 13 pass.
- **An independent cross-check of the normalizer.** For every determiner variant of every family (392 sentences, 680 readings), I took the reading built by D's generator, scrambled each conjunction (random order, random nesting, up to two added `Top` operands), converted it to `src.semantics` terms, and normalized it with CodexPrime's code. I repeated this five times per reading: 3,400 terms. Every canonical string equals the one D's own printer produces, and every reading set equals D's. Zero mismatches.
- I read both modules in full.

## M02: accepted

- Substitution, shifting, and beta reduction are standard and capture-safe; typing is checked before any reduction and again after.
- Conjunction handling matches the contract: maximal flattening, `Top` removed, duplicates kept, sort by canonical text, right-associated rebuild, and no movement across a binder, `Not`, `Implies`, or `Box`. Sorting Python strings equals unsigned byte order because the text is ASCII.
- `reading_set` produces the byte encoding the contract specifies.

Limits to record, none blocking:

1. The suite is a replacement for the design's 39 companion checks, which are not available. `spec/normalization.md` says so. The gate in plan 03 is met in its "if unavailable" form. I have asked the sponsor whether the author's checker and result file can be supplied.
2. The finite-world evaluator lives in the tests. The world bank needs one in `src/` that all systems share; schedule it with M04–M05.
3. Partial application of `And` (one argument) is left untouched by flattening. No seed recipe produces it. Say in the spec that constructors must be saturated in a closed reading, and reject otherwise in `reading_set`.

## M03 kernel: accepted as a first kernel, with one design question before the seed lexicon

The checker does what `spec/dsl.md` says: finite depth, typed templates, unique identifiers, source-located rejections, composition only under the kernel profile, unary cycle detection, bounded integer costs.

1. **How do guards travel?** Lexical entries carry field assignments, but `Grammar.combine` does not read them, and categories have no features beyond the clause form. The contract needs three things that depend on such state: the like-quantifier guard reads the semantic argument kinds (unit, universal, existential) at the transitive application; *quickly* attaches to a simple VP and never to a control VP; and *not every* is a checked macro. Please specify the mechanism before writing the lexicon: for example NP subcategories for the three kinds, a simple/control mark on VP categories, or state carried on chart items with declared propagation rules. Whatever is chosen must appear in the witness key's `instantiatedCategory`, since ClaudeOracle compares witnesses exactly.
2. **Depth errors in `combine`.** A composition whose result exceeds the depth bound raises `GrammarError`. For a parser that tries every pair, an over-deep result should be a non-match (`None`) with a counter, not an exception.
3. **Costs.** Entry costs are bounded, but the contract also requires a named error on overflow of the summed cost. Add it where costs are summed.

## Next for CodexPrime

The seed lexicon and guards (M06), then the packed reference parser (M07). The first end-to-end target is the reconciled fixture set, `fixtures/reconciled_v1.json`: all 12 statuses, decisions, and reading sets.
