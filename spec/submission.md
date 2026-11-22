# Submitting outputs for scoring

**Owner:** ClaudeScope as D. Applies to every system: reference parser, native parser, neural model, teacher, and any baseline.

## File

One JSON object per line, one line per input ID, UTF-8.

```json
{"id": "C0042", "construction_status": "complete", "decision": "accepted", "readings": ["(ExistsV (lam V ...))"]}
```

- `id`: the input's ID from the released files.
- `construction_status`: `complete`, `truncated`, `no_parse`, or `error`.
- `decision`: `accepted` (one reading), `ambiguous` (the complete set of two), or `abstain`.
- `readings`: canonical strings as defined in `spec/contract.md`. Order does not matter; the scorer sorts them. Normally empty for an abstention; readings kept there for diagnosis are ignored.

A missing ID counts as an abstention. A duplicated ID, an unknown ID, or a malformed line makes the whole file invalid.

**Admissible rows.** `accepted` needs status `complete` and exactly one reading. `ambiguous` needs status `complete` and exactly two distinct readings. `abstain` may carry any status; readings kept for diagnosis (for example with diagnostic `reading_count`) are ignored. A row that breaks these rules, or repeats a reading, is **inadmissible**: it is counted in its own column and earns neither coverage nor credit.

## What is scored

Scoring follows plan 07 §3 and `configs/pilot.yaml`. An answer is **correct** when its decision is `accepted` or `ambiguous` and its set of readings equals D's target set exactly. Abstentions, partial sets, and extra readings are not correct.

| Measure | Definition |
| --- | --- |
| Set-aware yield | correct answers ÷ all assigned inputs |
| Accepted coverage (all) | `accepted` answers ÷ all inputs |
| Accepted coverage (single-reading) | `accepted` answers on single-reading inputs ÷ single-reading inputs |
| Accepted accuracy | correct `accepted` answers ÷ `accepted` answers (raw exact match; the audited figure comes from human adjudication) |
| Transfer yield | set-aware yield on transfer inputs, with per-family outcomes |

These are raw exact-match figures. The finite-model signature and the adjudication of disputed forms (plan 07 §2) are added when the world bank exists.

## Which inputs can be scored, and when

| Inputs | Who has them | Scoring |
| --- | --- | --- |
| Training, ordinary development | Released | Any time, as often as wanted. D returns per-row results. |
| Development transfer | D only | **Once**, at Decision 2, on frozen candidates. D returns aggregates and per-family counts. |
| Calibration | D only until M14 | For fitting acceptance policies at M14. |
| Locked | D only | **Once**, at M14/M15, on frozen systems. |

For a reserved panel the submitter gives D a frozen, runnable system or a command; D runs it on the hidden inputs. Opening a reserved panel is recorded in D's custody ledger with the date, the frozen system's digest, the submission and targets digests, and the reason. The scorer refuses to score a reserved panel unless the opening is named explicitly, and refuses a second opening of the same panel unless a repeat is authorized with a recorded reason. The ledger is D's record; the one-look rule itself rests on D following the registered protocol, since D holds the data.

For a transfer panel D returns counts per family under opaque labels, as well as the totals.

## Tool

`python3 tools/score.py --targets <D's corpus file> --submission <file> --splits training,development-ordinary`

The code is public; the targets file is not.
