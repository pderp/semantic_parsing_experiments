# Controlled English semantic parser · M01 public contract

**Part 1, proposed for cross-review.** Version `seed-0.1-draft` specifies which controlled sentences and meanings the seed licenses. D can enumerate families and B can derive expected outputs from this public specification once the review is accepted. Signed run thresholds and the independent fixture readings belong to later handoffs. The spike provides a replayable example. [Seed ontology](ontology.yaml) · [Spike questions](../spike/README.md) · [Transfer protocol](../docs/plans/07codex_plan.md)

## Inputs, vocabulary and grammatical fragment

An input is one sentence without discourse context. The tokenizer removes leading and trailing ASCII whitespace, removes at most one final ASCII period, trims trailing ASCII whitespace again, folds ASCII A–Z to a–z, then splits on one or more ASCII whitespace characters. ASCII whitespace means space, tab, LF, CR, FF or VT. Tokens must match `[a-z]+`. Thus ` ALICE reviewed Bob. ` and `alice reviewed bob` have identical tokens. An empty string, unknown token or unsupported punctuation yields an exhaustive lexical failure with a named diagnostic and `no_parse/abstain`. A malformed request, such as a non-string sentence, yields `error/abstain`. Never discard an unknown word to complete an analysis.

The ontology file uses the JSON subset of YAML so every participant can load it with Python’s standard library. Its names, nouns, determiners, operators, modifiers and verb forms are the complete surface inventory. Predicate signatures list argument sorts in order and return P. Each verb has one sense/frame. `Agent` is the initiating participant, `Theme` the reviewed participant or item, `Recipient` the addressee, and `Content` the boxed infinitive meaning. `Quick` and `Past` describe events. Names are entity constants with no implicit type restrictions beyond E. Requiring a role filler to be a researcher or paper would add world knowledge. New senses require a versioned public licensing condition and contrast fixture. Every controlled evaluation surface token, lemma, sense and frame must occur in training. Preserve source label, morphology and token span on lexical edges.

The following finite surface grammar fixes the admission envelope. Brackets indicate a single optional occurrence. An indexed verb uses the corresponding surface form in the ontology. Case-insensitive example words below denote the normalized tokens.

```text
Root      ::= NP VP[past] | NP "did" "not" VP[bare] | "not" "every" N VP[past]
NP        ::= Name | Det N
Name      ::= "alice" | "bob"
Det       ::= "a" | "every"
N         ::= any noun surface in the ontology
VP[m]     ::= Simple[m] | Control[m] NP "to" Simple[bare]
Simple[m] ::= Leave[m] ["quickly"] | Transitive[m] NP ["quickly"]
Control   ::= Promise | Persuade
```

`Transitive[m]` selects a licensed transitive frame (review, cite, discuss, evaluate). `Control[m]` means either control verb inflected for m. A sentence admits at most one control complement. A final *quickly* in a control sentence attaches to the embedded simple VP. The marker *to* selects a bare VP. The auxiliary selects a bare matrix verb and supplies past tense. The third root licenses sentence-initial *not every* with finite past morphology and a single outer negation. Each production consumes its entire span. Unlisted constructions are outside this seed, including nested control, repeated adverbs, plurals, unresolved pronouns, and present-tense finite roots.

For CCG, N and NP are atomic categories and VP[m] abbreviates S[m] backslash NP for m in {fin, bare, to}. A past verb produces the finite category. A determiner selects N on the right. A transitive verb selects object NP on the right, and a control verb takes recipient NP, then VP[to], before combining with its subject on the left. Manner selects a simple VP to its left, *to* lifts a simple bare VP to VP[to], and *did not* is a lexically anchored two-token auxiliary. A checked macro may implement the sentence-initial *not every* production. License forward/backward application and degree-one harmonic forward/backward composition within the declared productions. The seed has no type-raising entries, epsilon edges or same-span unary transitions. Packing and composition must preserve the licensed surface trees and their meanings. A production state carries any feature still inspected downstream, including lexical frame, clause form, simple/control status, determiner kind, and unresolved scope choice where relevant.

## Public semantic recipes

Use the ontology’s base types. N denotes E → P, NP denotes Q = (E → P) → P, and a clause denotes H = (V → P) → P. A VP denotes Q → H. Close a clause with the event continuation `λe.Top`. `Unit(a) = λk.k(a)` lifts a name or a previously bound controller. In this section ∧, ⇒, ¬ and quantifier notation abbreviate the typed constructors below.

- **Determiners.** `every(N)(k) = ∀x.(N(x) ⇒ k(x))` and `a(N)(k) = ∃x.(N(x) ∧ k(x))`. Each quantifier ranges over E. Its restrictor stays within the binder.
- **Simple clauses.** For *leave*, apply the subject NP to `λs.∃e.(Leave(e) ∧ Agent(e,s) ∧ k(e))`. For each transitive frame, use its ontology event predicate, Agent(e,s), Theme(e,o), and k(e) inside the event existential. The two licensed scopes are `Qs(λs.Qo(λo.body(s,o)))` and `Qo(λo.Qs(λs.body(s,o)))`, with the event existential inside both. License both orders for mixed universal/existential arguments and for arguments involving Unit. Unit can collapse both derivations to one meaning. For two universals or two existentials, license subject-wide only. This explicit seed choice avoids counting equivalent permutations of like quantifiers as scope ambiguity. The local interface must expose the argument kinds for this guard.
- **Control.** Apply the matrix subject quantifier, then the recipient quantifier, then bind the matrix event. Assert its frame, Agent, Recipient, Content and event continuation. The Content argument is `Box(Close(embeddedVP(Unit(controller))))`. *Promise* chooses the matrix subject as controller and *persuade* the recipient. Pass the existing bound entity into the infinitive. Preserve its enclosing binder through Box. The matrix order is fixed even for mixed quantified arguments. An actual leaving or reviewing event never follows from the box alone.
- **Tense and manner.** Past morphology supplies `λe.(Past(e) ∧ k(e))` as the head-event continuation. *Did* supplies the same wrapper on the matrix bare verb, exactly once. Bare infinitives contribute no past tense. *Quickly* supplies `λe.(Quick(e) ∧ k(e))` on the licensed VP. Multiple properties constrain the same event. Fresh bound variables alone imply no inequality.
- **Negation.** For *NP did not VP*, apply the subject Q once to `λs.¬VP(Unit(s))(λe.(Past(e) ∧ k(e)))`, then close the root. Thus *Every researcher did not leave* has every > not > event. For *Not every N VP[past]*, negate the closed ordinary *Every N VP[past]* proposition, once per licensed reading. In *Not every researcher left* the negation scopes over the universal. Scope never crosses a negation or Box by a normalization rewrite.

## Normal form and exact equality

1. Type-check the chosen recipe, perform capture-avoiding substitution, close the root, beta-normalize, and represent all bound references with **zero-based mixed-sort de Bruijn indices**. Index 0 denotes the nearest enclosing lambda of any sort. Validate the sort at that distance. Lower the restricted quantifiers to `ForallE (lam E ...)` with Implies and `ExistsE (lam E ...)` with And. An event existential is `ExistsV (lam V ...)`. Keep both the raw closed formula and the normalization version.
2. The canonical text is ASCII. A constant or symbol uses its exact ontology spelling. A bound variable is `#` followed by its unsigned decimal index with no leading zeros. A lambda is `(lam SORT BODY)`. A saturated symbol application is `(SYMBOL ARG1 ... ARGn)`. Use one ASCII space between fields, no extra whitespace, no trailing newline in the compared value. After full root reduction only base-sort logical lambdas remain. Human-readable names, Unicode pretty printing, hashes, and JSON quoting are outside the compared value.
3. Recursively normalize each child. At each And flatten its immediately nested And nodes, remove Top operands, retain duplicates, and sort by **unsigned lexicographic order of the canonical ASCII bytes of each normalized operand in its current binding environment**. Equal bytes are interchangeable. Rebuild a right-associated binary And, with Top for zero children and the child itself for one. Never lift an operand out of a binder, Not, Implies or Box. Normalize inside a box under this same restricted rule set. Keep binder order and predicate arguments fixed. Thus `(ExistsV ...)` sorts before `(Paper #0)`; the order of restrictors in displayed mathematical prose has no effect.
4. The canonical target set is a list of distinct canonical strings sorted by that same unsigned byte order. For byte comparisons of a whole set, encode this array as compact UTF-8 JSON with no line ending (stdlib equivalent: `json.dumps(strings, ensure_ascii=True, separators=(",", ":")).encode("ascii")`). Two derivations may contribute one string. Record the input/context identity, ontology and grammar bundle digests, normalizer version, both status axes, diagnostics and witnesses alongside the target or output. Raw exact set match compares the lists. A finite-model signature and any adjudicated exception use separate result fields under the plan 07 dispute procedure.

For example, the canonical text for *Alice left* is exactly:

```text
(ExistsV (lam V (And (Agent #0 alice) (And (Leave #0) (Past #0)))))
```

For *Alice did not leave*, wrap that entire text in `(Not ...)`. Past remains under Not. For the two scope-spike readings, the `normalized` strings in the saved public result illustrate this byte convention. The spike’s `pretty` and `raw` fields are explanatory. [Scope spike output](../spike/output.json)

## Selection, tie order and result states

Build the full acyclic forest for the admitted fragment. Keep canonical ordered edges, recipes, local costs, and source provenance. Root witnesses are ranked by the following ascending tuple, applied identically by reference, compiler, and oracle.

1. Total additive integer cost. For the seed fixture bundle, use 10 for either lexical scope recipe of any transitive frame and zero for all other lexical and combinatory edges. Report overflow as a named error.
2. Total number of object-wide transitive recipe uses. At equal cost, the subject-wide witness sorts first even if its source ID sorts later. This secondary order chooses the first witness for display. It never suppresses an alternative.
3. Structural witness key. Compare recursively using integer order for numeric fields, unsigned ASCII bytes for identifiers, and lexicographic sequence order with a shorter equal prefix first. A lexical key is `(0, start, end, entryID, recipeID)`. A rule key is `(1, ruleID, start, end, instantiatedCategory, recipeID, childKeys)`, with children in surface order and zero-based half-open token spans. Use stable, unique public entry/rule/recipe IDs from the same versioned grammar bundle for both implementations. Include each locally distinct licensed choice in those IDs. Category spelling uses N, NP, S[form] and fully parenthesized ASCII slash or backslash categories without spaces. Identical keys identify the same witness under this contract.

Within each meaning, its first witness is the best under that tuple. For ranked display, order distinct meanings by their best witnesses. The set serialized for evaluation uses canonical text order. Thus *Every researcher reviewed a paper* displays the subject-wide witness first, while the canonical set begins with the object-wide ExistsE form.

| Construction outcome | Interpretation decision |
| --- | --- |
| Complete exact search, one distinct meaning | `complete/accepted` with a witness |
| Complete exact search, two distinct meanings | `complete/ambiguous` with both meanings and witnesses |
| Exhausted licensed search, zero roots | `no_parse/abstain` with a diagnostic |
| Resource budget exhausted before completeness | `truncated/abstain` even if a candidate is available |
| Invalid request, unsupported runtime operation, or inconsistent engine result | `error/abstain` with a named cause |

A complete seed reading set outside the registered one/two-reading design is an observable contract discrepancy. Preserve the entire set and diagnostic for review. No selection, calibration or fallback may turn an incomplete or extra set into a correct complete answer by omitting readings.

## Census and cross-system identity

Derive a primary family key from the **surface construction tree**. Record root operator (ordinary, VP negation, or initial not-every), matrix frame kind (intransitive, transitive, subject control, object control), NP kind at each ordered argument position (name or quantified), embedded simple frame/arguments when present, and manner attachment site (none, matrix, embedded). The obligatory subject of initial not-every counts as quantified. The embedded controller is an inherited reference. Frame kind identifies argument structure and controller choice. The primary key excludes determiner identity, noun/name/verb spelling, tense inflection, paraphrase, derivation bracketing and selected scope reading. One structure with two readings counts once. The secondary count refines the primary key with ordered determiner identities in surface argument order, including the initial every. Distinct variants of one primary family must remain in the same transfer panel. Structural eligibility, observed training support for components, duplicate/group controls, and mixture feasibility each require separate checks.

The spike’s two nouns and single transitive predicate would provide just eight mixed-determiner plain transitives, against 400 training slots alone. This draft therefore gives existing constructions a closed review-domain lexicon. Ten person nouns, ten artifact nouns, four transitive predicates and two mixed-determiner orders allow 800 distinct plain strings even in the person-subject/artifact-object slice. The same sentences can take the licensed manner modifier. These are potential surface counts. They add zero structural families and do not certify a group-disjoint allocation. D reports distinct available texts, independent groups, feasible mixtures and any shortfall before sealing the manifests.
