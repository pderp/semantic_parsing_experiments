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
