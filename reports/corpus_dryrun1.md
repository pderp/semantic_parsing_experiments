# Controlled corpus · dry run 1

**Run by:** ClaudeScope as D, 21 November 2026. **Status: dry run, not released.** The generation and audit work; the run exposed one defect in the language (below), so no data has been published and the corpus will be regenerated after that is settled.

## Result

The private generator produced all 6,000 controlled inputs with D's target reading sets under the reserved panels, and the audit passed all 26 checks. **876 of the 6,000 sentences contain "a" before a vowel-initial noun** ("a editor", "A abstract"), because the frozen vocabulary has *a* and no *an*.

## The defect and the proposed fix

Six nouns start with a vowel: *editor, author, analyst, investigator, article, abstract*. The contract's only existential determiner is *a*.

This matters for three reasons: the teacher and the neural baseline would be trained and scored on ungrammatical English; the existing-symbolic baseline (ACE/ERG) is likely to reject such sentences; and the natural-text comparison becomes harder to interpret.

**Proposed change (`seed-1.1`), for CodexPrime to draft and the sponsor to approve:** add the surface form *an* for the existential determiner. *An* is required before a noun beginning with a vowel letter and *a* before any other noun; the wrong form gives no parse. The meaning, the family keys, the census, the reserved panels, and all 12 fixtures are unchanged (no fixture has *a* before a vowel-initial noun). The vocabulary grows from 56 to 57 surface tokens.

*Alternative:* replace the six nouns with consonant-initial ones. That adds no rule, but it invalidates five of the twelve reconciled fixtures, which use those nouns.

## What the audit checked (all passed)

| Check | Result |
| --- | --- |
| Cell counts equal the configuration | 6,000 rows: training 4,000; development 1,000; calibration 500; locked 500 |
| Ordinary strata quotas in every split | Exact (for training: simple 960, manner 640, negation 640, subject control 480, object control 480, two-reading plain 400, two-reading manner 400) |
| *Not every* is at least 25% of each negation stratum, and VP negation is present | 213/640, 42/128, 26/80, 18/56 |
| No duplicate inputs or token sequences | 0 duplicates |
| Groups never cross splits | 804 groups (a group is a determiner variant with its verbs) |
| Transfer families absent from all ordinary rows; panels disjoint; 40 families each | Yes |
| Transfer rows balanced | Development 4–5 rows per single-reading family (largest share 5/160); locked 3–4 (largest 4/120); one two-reading family per panel |
| Every evaluation token occurs in training | 56 of 56 tokens |
| Every component of every transfer family occurs in a training row | 44 of 44 |
| Token lengths | 2 to 12 |
| Reading-set size matches the cell | Yes |
| Pilot subset | 100 training rows, 20 with two readings |
| **Independent targets:** ClaudeOracle's enumerator gives the same reading set | 6,000 of 6,000 rows |

## Two things to know about the ordinary strata

- After the panels were reserved, the "simple" stratum rests on 5 training families and "manner" on 3 (the fragment has only 6 of each). Together they are half of the ordinary single-reading rows. The quotas in `configs/pilot.yaml` were set before the reservation; they are met, but a reader should not take 1,600 training rows as 1,600 independent structures.
- To keep small groups large enough, one noun draw in four ignores the person/thing distinction ("A paper waited"). The grammar licenses these and the meaning is well defined.

## Release plan (unchanged by the defect)

Grammar and model authors receive the training inputs and the ordinary development inputs, without targets, plus D's canonical targets for the 100 pilot rows as the notation reference. Development-transfer, calibration, and locked rows and all other targets stay with D.

## Private evidence

| File (private) | SHA-256 |
| --- | --- |
| Panel manifest | `75c6a7199387290e0d4a634d24258721bb91dd771440d13405c050fa98ad9bbe` |
| Dry-run corpus | `be3c64eba5d8d7f47b8009a264c7cc9b01376209eca11979fdc0123c2b685301` |
| `corpus.py` | `8dab490d01c10d0555fed5fbd4408c2f73ab2416b677ee3f9b1f8b7d910a87dd` |
| `audit_corpus.py` | `f05b9cf55fd3fbf8dabca2d20adeb4cba3308f634052419964bed8e8db4f9956` |
