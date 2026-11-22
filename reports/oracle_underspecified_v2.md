# ClaudeOracle: points still underspecified after `spec/witness-v1.md`

Copied unchanged from ClaudeOracle's STATUS.md on 22 November 2026 (mailbox message 62). Written against the seed-1.0 inputs in `oracle/inbox_v2/`.

### Deliverable: still underspecified in witness-v1.md
1. **Edge identity (item 11).** "Distinct lexical and binary edges" is not defined: per entry or per category for lexical edges; per (rule, left, right) or per parent node for binary edges; what a "duplicate" is; whether every span is built or only goal-directed ones. Thresholds depend on this. My reading is in the cases file under conventions.edge_count.
2. **Order of request checks.** Malformed max_edges versus a non-string sentence, empty input or a lexical failure: which code wins is not stated. I check sentence type, then budget shape, then tokens.
3. **Tokens on a malformed budget.** Item 14 gives an empty token list only for a non-string sentence. I return an empty list for a malformed budget too.
4. **What counts as malformed.** Negative and non-integer are clear. JSON true/false, 5.0 and null are not. I treat booleans as malformed and absent as "no cap"; I did not test 5.0 or null.
5. **Diagnostic record shape.** Item 14 requires the offending token and index but names no fields. I use {code, token, index}.
6. **Vocabulary for unknown_token.** The ontology's surface inventory or the tokens of the loaded bundle? Identical for the full bundle; different for any restricted grammar. I use the grammar's own tokens.
7. **Overflow scope (item 10).** "Check every sum": does a sum on an edge outside any root count? What if only some root witnesses overflow? Are result arrays empty? In what order are partial sums taken when costs are negative? I check every sum I form, including non-root ones, and return empty arrays.
8. **Negative lexical costs.** Signed integers are allowed, so presumably yes; not stated. One case uses -3.
9. **Witness record shape.** Field names, and whether a witness carries a tree as well as its key, are not given. I emit cost, object_wide_uses, key, reading.
10. **Display order as a field.** Item 8 fixes the order but not whether a separate ranked reading list is output. I emit ranked_readings.
11. **Result arrays on reading_count.** Item 12 keeps readings and witnesses; min cost and display order are not mentioned. I keep them.
12. **Rule costs.** Stated as zero in prose; the inventory's rules carry no cost field.
13. **Root set.** witness-v1 says "finite root" without listing categories; only the inventory lists the five roots.
14. **engine_error.** No condition that produces it can be constructed from the public inputs, so it is untested.
15. **Tiny grammars.** Nothing defines how a restricted or modified grammar is presented to the reference. My cases use restrictions and clones of published entries; that format is mine.

## 2026-11-21 16:33 UTC — results back, standing by (msg 46)
- The 15 underspecified points are filed and sent to CodexPrime (contract owner). Points 1-5, 7, 8, 12, 13 need a contract revision plus the published grammar bundle; structural keys stay out of comparisons until then. My invented IDs and error/abstain for 3+ meanings stand for now.
- Next (not started, waiting on inbox_v2/): (a) adopt published IDs and derivation shapes; (b) freeze at least 100 tiny grammar/input pairs for comparison with the reference parser.

## 2026-11-21 — exhaustive enumerator delivered (msg 37)
### Deliverable: underspecified points in "Selection, tie order and result states"
1. **Public IDs are not published.** Tie-order item 3 needs "stable, unique public entry/rule/recipe IDs from the same versioned grammar bundle". No bundle was in my inputs, so I invented IDs (`name:bob`, `verb:cite.tv:past`, `op:did_not`, `tv.object-wide`, `FA`, ...). My structural keys cannot be byte-compared with anyone else's until the bundle is published; only cost, object-wide count and the resulting order relations are comparable.
2. **Derivation shape is not fixed.** The key depends on the tree, but the contract gives an n-ary surface grammar plus a prose CCG sketch. Open: binarisation of the control VP (I used ((verb NP) (to VP))), whether "did not" is one two-token lexical edge (I did that, span length 2), and whether "not every" is a macro edge or two edges (contract says a macro "may" implement it; I used one two-token edge of category ((S[fin]/(S[fin]\NP))/N)).
3. **Category spelling.** "Fully parenthesized" does not say whether the outermost complex category is parenthesised (I wrote `((S[fin]\NP)/NP)`), nor whether VP[m] is spelled out as `(S[m]\NP)` in keys. Form names: the grammar says VP[past], the CCG paragraph says m in {fin, bare, to}; I used fin/bare/to. Unclear whether downstream features (simple/control status, determiner kind, unresolved scope choice) belong in instantiatedCategory; I left them out.
4. **Where the scope choice lives.** Item 1 calls it a "lexical scope recipe" of the transitive frame; the recipes section says to inspect argument kinds "at this transitive application" (a rule). I put it in the verb's lexical recipeID. This changes the key and which edge carries the cost.
5. **recipeID of a rule key.** No rule recipes are named; I used the constant `apply` for FA and BA.
6. **Cost is inert in the seed.** Every witness of one sentence has the same number of transitive uses (0 or 1), so cost is always 0 or 10 and never separates two witnesses. All ordering is done by the object-wide count and the key. Also unstated: that an embedded transitive costs 10 too (I assumed any transitive use does).
7. **Unlicensed recipe vs absent recipe.** For like quantifiers only subject-wide is licensed; not stated whether the object-wide edge exists and is filtered, or never exists. No effect on meanings, but it affects witness counts and "exhaustive" comparisons.
8. **Witness count for Unit cases.** With a Unit argument there are two witnesses with one meaning. "complete/accepted with a witness" does not say whether one (the best) or all are reported. I report all, ranked.
9. **Identifier comparison across types.** Rules say integers by integer order and identifiers by ASCII bytes; a lexical key (0,...) and a rule key (1,...) differ at field 0, so mixed-type comparison never arises in my shape, but that depends on point 2.
10. **Overflow.** "Report overflow as a named error" gives no integer width or error name. Python integers do not overflow; I report none.
11. **Truncation budget.** No unit or limit for the resource budget, and no diagnostic name. I count enumeration steps against an optional cap.
12. **Out-of-design reading sets.** A complete set with 3+ meanings is "an observable contract discrepancy" but the table gives it no status pair. I return error/abstain with the whole set preserved; complete/ambiguous would be the other defensible choice. Cannot occur in this fragment (max 2).
13. **Diagnostic names.** "Named diagnostic" and "named cause" are required but no names are listed, so diagnostics cannot be compared exactly. Mine: "lexical failure: empty input / unsupported token / unknown token", "no licensed derivation: zero roots", "malformed request: ...".
14. **Lexical failure vs zero roots.** Both give no_parse/abstain; the contract does not say whether tokens are reported, or which of several bad tokens is named (I name the first, checking pattern before vocabulary).
15. **Empty-after-period inputs.** "." tokenizes to nothing; I treat it as the empty-string lexical failure. " . " likewise.

