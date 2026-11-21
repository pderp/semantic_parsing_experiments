# Independent fixtures, version 1

Twelve fresh sentences, chosen by D. None is a public worked example. Three specifiers answer without seeing each other's answers or D's: CodexPrime, ClaudeOracle, and the sponsor.

| File | SHA-256 |
| --- | --- |
| `fixtures/prompts_v1.json` | `1d5ecb894e4a8db14b56603530451b3517430b2d7272f0b2dedebbb8ac3392da` |
| `spec/contract.md` | `e15a49cf3861728f9e3f1412005272875d64ca9f48b6a295344549c4cbcdd5c1` |
| `spec/ontology.yaml` | `eaa0e2477a6005f751187f4c234ec6586fe03f27be8bce1f8d25d910f43896ab` |
| D's sealed answers (private) | `e664a1fab940997d183006e8d7e0ecfcda4d308389ae8bb1a1669966592bc125` |

## Agents (CodexPrime, ClaudeOracle)

Work from the contract and ontology only. Do not run or read any parser, the spike, or another specifier's answers. Derive each answer by hand or with code you write for this purpose from the contract.

Write `answers_<name>_v1.json`: a JSON list with one object per prompt, in prompt order.

```json
{"id": "F01",
 "tokens": ["..."],
 "construction_status": "complete | no_parse | truncated | error",
 "decision": "accepted | ambiguous | abstain",
 "readings": ["canonical strings, sorted by unsigned byte order"],
 "diagnostic": "for a failure, the reason in a few words; otherwise empty",
 "note": "anything in the contract you found unclear for this item"}
```

CodexPrime commits its file under `fixtures/`. ClaudeOracle leaves its file in its own directory and ClaudeScope collects it. Send ClaudeScope the SHA-256 of your file by mailbox when done. Do not revise after sending.

## Sponsor

Use `fixtures/sponsor_worksheet.md`.

## Reconciliation

After all three are in, ClaudeScope unseals D's answers and publishes all four originals unchanged under `fixtures/originals/`, with a table of agreements. Each disagreement is traced to the contract: a specifier's error, D's error, or an unclear rule (which becomes a contract change). The reconciled set becomes `fixtures/reconciled_v1.json`.
