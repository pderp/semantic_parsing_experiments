# Independent exhaustive oracle

Written by ClaudeOracle from `spec/contract.md` and `spec/ontology.yaml` (`seed-0.2-draft`) only. ClaudeOracle has not read this repository. ClaudeScope copies its files here unchanged; the working copy is in ClaudeOracle's own directory.

| File | SHA-256 (as sent by ClaudeOracle, mailbox message 43; verified on copy) |
| --- | --- |
| `oracle.py` | `6c0f76eda64f9228264573df911573035dc6b90940b36b99ddd8ecffdb776558` |
| `oracle_enum.py` | `5171f9ba5ce3528a3530e0e274e3a750575043a679229ccedce8ba3ff9455fab` |
| `selftest_enum.py` | `22f0f713b1b97f1cdb50fd27833d6100963f0843a7dcd9c8009bbe90dea26d4c` |
| `test_contract_examples.py` | `833ff2072bf277e980e3bb07596cca181b9841443926cccd496c84a57f0bbc03` |

Run from this directory: `python3 selftest_enum.py` (prints `SELFTEST OK`; 182 inputs, 57,191 checks).

**Checked by ClaudeScope on receipt:** the self-test passes, and the enumerator's reading set equals the private generator's for all 392 determiner variants of the 150 families.

**For CodexPrime:** to keep the reference parser independent, do not copy from these files. Compare outputs only. The enumerator's witness keys use identifiers ClaudeOracle invented; they become comparable once the grammar bundle publishes its identifiers (see `reports/oracle_underspecified_v1.md`).
The `inbox_v1/` folder holds the frozen inputs ClaudeOracle was given; its code reads the ontology from there.

## Second deliverable (22 November 2026, mailbox message 62)

| File | SHA-256 |
| --- | --- |
| `cases_witness_v1.json` (frozen: 181 grammar and input pairs over 32 grammars) | `68edf14dd266e3b83608084339a11ef1b9c848d464c07fe8a48744f043bc1621` |
| `oracle_witness.py` | `33b7ee9a6d357f0925ef0b7a084eda41bd6634ca69e1951dd5ffdea372828421` |
| `gen_cases_witness.py` | `d8b7f0aa1f3f1d0c0f55a0b7a7b0585bd91505b7609bc626cc1663a7404896c2` |
| `selftest_witness.py` | `8ab8be427d2ba746c5484a426a313f18271cf6a0de32778f1834f0fd2273516f` |

`oracle_witness.py` adopts the published entry and rule identifiers, derivation shapes, category spelling, and diagnostic codes from `spec/witness-v1.md`, so its witness keys are meant to be byte-comparable with the reference parser's. Its semantics remain ClaudeOracle's own. `inbox_v2/` holds the inputs it was given (seed-1.0; the bundle inventory has the semantic templates removed). `python3 selftest_witness.py` prints `SELFTEST OK` here.

The cases were frozen before any comparison with the reference parser. Fifteen cases carry a `depends_on` note: they rest on a convention the witness contract leaves open, so a mismatch there may be a convention and not a defect. These files predate `seed-1.1` (*an*).

## Third deliverable: `seed-1.1` (22 November 2026, mailbox message 82)

| File | SHA-256 |
| --- | --- |
| `cases_witness_v11.json` (frozen: 80 cases around the article rule) | `fe01af31dd5b1d90bf48c47f1380b2401310c9a3586c215502a344e57bc66f28` |
| `oracle_v11.py` | `e9d853e057136eb5a249db2fd9bb1ce0fd28c51386650cf8ab336a2ba7bad284` |
| `gen_cases_v11.py` | `a4998e2cc7477effd47106a886a74475549e9a7a2979c449ca4bb2d3e05763db` |
| `selftest_v11.py` | `c08841cbc0ad41cae6e469bd4e0bc35a38c6f9dd0229214bcfd2ecbe9a8f3cec` |

Frozen before any comparison with the reference parser. Of the 181 seed-1.0 cases, 180 keep their expected output under `seed-1.1`; W069 ("a editor left") changes from accepted to no parse. `inbox_v3/` holds the inputs. `python3 selftest_v11.py` prints `SELFTEST OK` here.

## Fourth deliverable: world-bank check (22 November 2026, mailbox messages 96 and 100)

`answers_worldbank_v1.json` (sealed before any expected value was seen), `world_eval.py`, `world_review.py`; inputs in `inbox_v4/`. Result and design review: `reports/world_bank_check_v1.md`.
