# ClaudeTrainer status

Lane C: teacher script and cache, bulk labelling, tokenizer check, neural baseline. Newest entry first.

## 2026-11-24 · set-up, model shortlist, teacher script

**Done**

- Mailbox link confirmed with ClaudeScope. Clone fast-forwarded to `d7ddd35`. Read plan 11, the board, the contract, the ontology, the submission format, the stage 2 pilot report and the corpus release note.
- Machine report sent to ClaudeScope: NVIDIA GeForce RTX 4060 Laptop GPU with 8 GB; 8-core, 16-thread CPU; 60 GiB RAM; 892 GB free disk; Python 3.14.10 with working pip and venv. torch and transformers are not installed; a pip dry run in a virtual environment resolves torch 2.15.0 and transformers 5.24.0. Whether that torch build runs CUDA on this GPU is not yet checked. openrouter.ai and huggingface.co both answer.
- Shortlist of six low-cost models from six vendors, with one spare, sent to ClaudeScope from the public OpenRouter model list. No keyed API call has been made.
- Teacher script written: `baselines/teacher/teacher.py`, fixed instructions in `baselines/teacher/instructions.txt`, offline tests in `baselines/teacher/test_teacher.py` (8 tests pass; the network function is replaced in every test). Standard library only.

**How the script meets the lane rules**

- It reads only the `id` and `input` fields of an input row. A test places a marker string in a `readings` field and asserts that it is absent from every request body.
- A submission row is the model's JSON copied unchanged when it has the three fields of `spec/submission.md` with valid values. Any other text becomes `error`/`abstain` with empty readings, and the raw text is kept in `raw.jsonl`. There is no repair step: a JSON answer wrapped in a code fence is recorded as malformed.
- Each request is cached under the SHA-256 of its body (model, messages, temperature 0, `max_tokens`, response format). A cached request is never sent again, including one whose answer was malformed. `--replay` sets the call allowance to zero.
- `--max-calls` is required and counts every network attempt in the invocation.
- A response without a model message (HTTP error, rate limit, timeout) is not a label: it is logged to `transport_failures.jsonl`, not cached, and retried up to three attempts per sentence per invocation.

**Open with ClaudeScope**

- Whether hidden reasoning tokens are left at each model's default, and the value of `max_tokens` (draft default 8,000).
- Whether to request `response_format: json_object` (draft default: no).
- Review of the wording in `instructions.txt` before any trial call, since the wording is part of the cache key.
- Whether provider routing should be pinned.

**Blocked**

- Step 2 (key and test call) waits for the sponsor to create an OpenRouter key with a credit limit. The script reads it from the environment variable `OPENROUTER_API_KEY` or from `~/.config/openrouter/key`, and refuses a key file that group or others can read.
- The 100-sentence trial waits for ClaudeScope's choice of models and the sponsor's approval.
