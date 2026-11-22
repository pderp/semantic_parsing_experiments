# Natural-text survey, version 1

**Run by:** ClaudeScope, 21–22 November 2026, brought forward by the sponsor's decision (plan 11). **For:** CodexPrime's review.

## Result

**The seed grammar parses none of the 200 natural sentences, and no small set of additions would change that.** Only 6% of the word tokens are in the seed vocabulary, and the typical sentence needs eight kinds of construction the seed lacks, all at once. Reaching even a quarter of these sentences needs about a dozen new construction types and an open vocabulary.

This is the first measurement in the project whose outcome was not fixed in advance. It says the natural-text coverage planned for M13 (four weekly growth rounds) will be close to zero unless the growth work is aimed very differently.

## Sample

| Item | Value |
| --- | --- |
| Source | PLOS ONE research articles whose title or abstract contains "peer review", "scholarly publishing", or "research assessment" (query in `tools/natural_snapshot.py`) |
| Search snapshot | 905 articles, retrieved 21 November 2026 17:02 UTC; `search.json` SHA-256 `95d92ad66af3ac78d041a06b7a155f54447178c63ccd0c00a96f2b6be55c5ac0` |
| Articles fetched | 125, in seeded random order (seed 20261121); 119 read; 19 dropped for lacking an explicit CC BY 4.0 licence |
| Split | By DOI: first 40 qualifying articles for the survey, next 60 for the development sample |
| Survey sample | 200 sentences, 5 per article; `data/natural/survey_v1.jsonl`, SHA-256 `00827d3f66f4ec4c8331910a208d373096caa3b087c376abdcecdccd5341277d` |
| Development sample | 300 sentences from 60 other articles; held privately by D, **not inspected**; SHA-256 `232dc5d5122e7812ae8e23e0b3363b699840e51ad726c67c35ab7bf472e0a45e` |
| Segmentation | Body paragraphs only (no tables, figures, captions, lists, references, quotations); split at sentence-final punctuation before a capital; 759 of 20,737 segments excluded for length under 4 or over 60 words or a malformed start or end |
| Sentence length | Median 24 words, range 7 to 57 |

The raw article XML is kept outside the repository. The topic query matched many health and medical articles that mention peer review only in passing, so the sample is broader than "writing about peer review".

## Seed parser on the sample

| Outcome | Sentences |
| --- | ---: |
| Parsed | 0 |
| No parse, unknown word | 180 |
| No parse, token with characters outside a–z | 20 |

Word tokens in the seed vocabulary: 306 of 4,914 (6.2%), nearly all of them *a*, *to*, and *not*.

## Constructions needed

Counts are from a mechanical word-pattern tagger (`python3 tools/natural_survey.py data/natural/survey_v1.jsonl`), not from human annotation. See "How reliable are the tags" below.

| Construction (as tagged) | Sentences | Share |
| --- | ---: | ---: |
| Prepositional phrase | 194 | 97% |
| Plural noun or -s verb form | 184 | 92% |
| Other determiner (*the, this, some*, …) | 170 | 85% |
| Adjective (by suffix; undercounts) | 134 | 67% |
| Coordination | 121 | 60% |
| Non-past tense | 100 | 50% |
| -ing form | 93 | 46% |
| Infinitive or *to*-phrase (overcounts) | 77 | 38% |
| Subordinate or complement clause | 75 | 38% |
| Passive | 73 | 36% |
| Copula | 66 | 33% |
| Numeral | 62 | 31% |
| -ly adverb | 53 | 26% |
| Modal | 48 | 24% |
| Pronoun | 47 | 24% |
| Parenthetical | 44 | 22% |
| Possessive (undercounts) | 31 | 16% |
| Negation | 29 | 14% |
| Relative clause with a wh-word (undercounts) | 22 | 11% |
| Perfect | 16 | 8% |
| Colon or semicolon | 13 | 6% |
| Question | 2 | 1% |

Every sentence has at least 3 of these; the median is 8.

## How many additions before sentences start to parse

A sentence can only parse once **every** construction in it is supported. Adding construction types in order of frequency:

| Construction types added (most frequent first) | Sentences fully covered, of 200 |
| ---: | ---: |
| 5 | 2 |
| 8 | 6 |
| 10 | 17 |
| 12 | 44 |
| 14 | 76 |
| 16 | 117 |
| 18 | 152 |
| 20 | 185 |

This is an upper bound. It assumes each tag is one construction (a "prepositional phrase" is many attachment patterns), that every word is in the lexicon, and that the constructions combine without further work.

## How reliable are the tags

I read 40 of the 200 sentences (every fifth) against their tags. The frequent tags were right in almost every case. Errors I saw:

- **Infinitive overcounts:** *to* before a noun (*related to medication*, *5 to 10 million*) is tagged as an infinitive.
- **Relative clauses undercount:** relatives introduced by *that* are tagged as subordinate clauses.
- **Adjectives undercount:** only suffixed adjectives are caught (*grey*, *main*, *new* are missed).
- **Possessives undercount:** a curly apostrophe after a plural (*authors’*) is missed.
- **Pronoun overcounts slightly:** *one* as a numeral.
- Two sampled sentences show segmentation damage (a missing subject after a removed figure reference; stray commas where citations were).

None of these changes the ranking at the top or the conclusion. The counts are agent-produced and no human has checked them.

## What this means for the plan

1. **M13 as written will report natural coverage near zero.** Four weekly rounds of patches cannot add a dozen construction types and an open lexicon.
2. **The first extensions, by frequency, are:** prepositional phrases, plural nouns, the definite article and other determiners, adjectives, coordination, present tense, and the copula. Each appears in at least a third of sentences, and most sentences need several together.
3. **An open-vocabulary policy is a precondition.** With a closed 56-word lexicon no natural sentence can parse, whatever the grammar. The contract would need a rule for unknown nouns, verbs, and adjectives (for example, typed placeholders from a tagger or from the teacher).
4. **Options for the sponsor and CodexPrime to consider:**
   - **(a)** Keep the controlled pilot as the deliverable and report natural text as a measured gap, with this survey as the evidence. Cheapest; honest; no natural-text claim.
   - **(b)** Replace M13's patch rounds with one planned extension to a "core academic English" fragment (the seven items in point 2 plus an open lexicon), with its own contract version, census, and fixtures. This is weeks of work for all three agents and still would not parse most sentences (about 17 of 200 at ten construction types).
   - **(c)** Narrow the natural target to short, simple sentences selected by a public rule (for example at most 12 words with no subordinate clause) and measure coverage on that slice. More achievable, but a weaker claim.

My recommendation is (a) for the pilot, with (c) as a possible follow-up, and I would not start (b) without the sponsor deciding it is worth the cost.
