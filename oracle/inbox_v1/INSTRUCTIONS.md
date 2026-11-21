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

