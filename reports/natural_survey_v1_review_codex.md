# Review of the public natural-text survey

**Recommendation.** Choose option (a). Report the controlled pilot and the natural-text result with their own denominators. The frozen seed parsed **0 of 200** public sentences. Preserve the planned evaluation on the separately held 300 sentences and the existing Decision 2 criteria. Treat the return from four M13 growth rounds as an open empirical question. Option (b) would require a separately approved grammar, vocabulary policy and evaluation. For option (c), a preregistered short-sentence slice could accompany the full result, with both denominators visible. [Survey and options](natural_survey_v1.md) · [Management decisions](../docs/plans/11_management_claude.md)

## What reproduces

I replayed the survey against seed-1.1. The public JSONL SHA-256 is `00827d3f66f4ec4c8331910a208d373096caa3b087c376abdcecdccd5341277d`. There are 200 distinct sentences at 200 distinct source coordinates, five per DOI across 40 DOIs. Each DOI has its own source XML digest. The segment length is 7–57 whitespace-delimited words, median 24. The tagger finds at least three labels per sentence, median eight. The most frequent appear on 194 sentences (prepositions), 184 (plural noun or *-s* verb) and 170 (other determiner). The published frequency-order coverage counts reproduce for all eight cutoffs. The tagger also finds *progressive* once, bringing the label count to 23. [Survey code](../tools/natural_survey.py) · [Public rows](../data/natural/survey_v1.jsonl)

| Measure | Result on the same 200 rows | Interpretation |
| --- | ---: | --- |
| Complete seed parses | 0 | Direct end-to-end observation. |
| First lexical failure | 180 unknown, 20 invalid | The parser stops at the first failing token. Further failures can coexist. |
| Rows containing an out-of-vocabulary alphabetic word | 200 | Independent scan using the survey's word extraction. |
| Tokens in the seed vocabulary | 306 / 4,914 (6.2%) | The denominator counts tokens the survey extracts as alphabetic. Seed-1.1 has 57 surface forms. *To*, *a* and *not* account for 233 matches, and *an* adds 17. |
| Rows over the seed's 12-token cap | 180 | The parser checks vocabulary first. Even with perfect lexical and grammatical coverage, retaining the cap allows at most 20/200, or 10%, on this sample. |

The distinction matters for planning. A vocabulary expansion alone leaves a hard length limit. Changing that limit would also change the inputs on which runtime and memory need to be measured. [Reference parser](../src/reference/__init__.py) · [Seed bounds](../src/reference/seed.py)

## What the construction table measures

The survey counts sentences whose **observed tag set is contained in a chosen list**. The ten most frequent labels cover all the observed labels on 17/200 rows. Replacing *non-past tense* and *subordinate or complement clause* in those ten with *numeral* and *pronoun* raises the count to **28/200**. Only five and seven of the respective rows meet the seed token limit. These comparisons use the same tags on the same rows and require no new parser. Ranking labels by marginal frequency therefore misses some combinations that occur together. Both selections would need to be evaluated on separate articles before drawing conclusions about growth.

A tag can fire on a construction the seed already supports, such as *not*, or fire in the wrong context, such as *to* before a noun. A sentence can also require an untagged construction or a particular attachment and lexical sense. Consequently the table puts **no strict bound in either direction** on actual coverage after a grammar change. The measured result supports reporting a substantial gap. The number of grammar additions it would take to reach 25%, and the outcome of a later M13 run, remain unmeasured.

## Sampling and verification limits

The snapshot sorts article IDs, shuffles using a recorded seed, and takes five eligible body segments per qualifying article. Longer articles therefore have the same weight as shorter articles. Topic search, fetch success, licence selection, XML cleanup and segment eligibility define the population for this result. The 40-sentence qualitative check takes the first of the five sampled segments in document order from each survey article. That gives breadth across articles, but supplies no label-level precision, recall or uncertainty estimates. Any future uncertainty estimate for sentence coverage should account for clustering by DOI. [Snapshot code](../tools/natural_snapshot.py) · [Tagger and inspection selection](../tools/natural_survey.py)

I verified public metadata and the selection code. The XML licence check searches licence elements throughout the document and matches a URL substring. Raw XML, fetch totals and the separate development split remain under D's custody. Independent verification here ends at the public survey. The 300-row evaluation can retain its prospective status. [Survey provenance](natural_survey_v1.md)

Replay from the repository root.

```sh
python3 tools/natural_survey.py data/natural/survey_v1.jsonl
```
