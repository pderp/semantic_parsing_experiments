#!/usr/bin/env python3
"""Teacher labels from an API model through OpenRouter. Standard library only.

    python3 baselines/teacher/teacher.py --model VENDOR/MODEL \
        --inputs data/controlled/pilot_targets_v1.jsonl \
        --out-dir baselines/teacher/runs/pilot100/NAME --max-calls 110
    python3 baselines/teacher/teacher.py ... --replay        # zero network calls

One request per sentence at temperature 0. The prompt is the fixed instructions in this
directory, then spec/contract.md, then spec/ontology.yaml, then the sentence. Only the
"id" and "input" fields of an input row are read; every other field is dropped at load,
so targets stored beside the inputs never reach a prompt.

A label is exactly what the model returned. The returned text is parsed as JSON and
copied to the submission row unchanged when it has the three fields of spec/submission.md
with valid types and values. Any other text is recorded as construction_status "error",
decision "abstain", readings [], and the raw text is kept in raw.jsonl. This script does
not check readings against the grammar, the reference parser, or any target.

Cache: one file per request under --cache-dir, named by the SHA-256 of the request body
(model, messages, temperature, max_tokens, response_format). A request already in the
cache is never sent again. The system prompt is stored once under cache/prompts/ and
referenced by digest from each entry.

Key: environment variable OPENROUTER_API_KEY, or a file readable only by its owner
(--key-file, default ~/.config/openrouter/key). The key is sent only in the
Authorization header and is never written to disk by this script.
"""
import argparse
import concurrent.futures
import hashlib
import json
import os
import stat
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

URL = "https://openrouter.ai/api/v1/chat/completions"
HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
STATUS = {"complete", "truncated", "no_parse", "error"}
DECISION = {"accepted", "ambiguous", "abstain"}
ATTEMPTS = 3          # network attempts per sentence in one invocation


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def canonical(obj):
    return json.dumps(obj, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")


def load_inputs(path):
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            rows.append({"id": r["id"], "input": r["input"]})
    return rows


def system_prompt():
    parts = [(HERE / "instructions.txt").read_text(encoding="utf-8"),
             "===== spec/contract.md =====\n" + (REPO / "spec/contract.md").read_text(encoding="utf-8"),
             "===== spec/ontology.yaml =====\n" + (REPO / "spec/ontology.yaml").read_text(encoding="utf-8")]
    return "\n\n".join(parts)


def request_body(model, system, sentence, max_tokens, response_format):
    body = {"model": model,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": "Sentence: " + sentence}],
            "temperature": 0,
            "max_tokens": max_tokens}
    if response_format == "json_object":
        body["response_format"] = {"type": "json_object"}
    return body


def read_key(key_file):
    key = os.environ.get("OPENROUTER_API_KEY")
    if key:
        return key.strip()
    path = Path(key_file).expanduser()
    if not path.exists():
        sys.exit(f"no key: set OPENROUTER_API_KEY or create {path} with mode 600")
    if stat.S_IMODE(path.stat().st_mode) & 0o077:
        sys.exit(f"refusing key file {path}: readable by group or others; run chmod 600 on it")
    return path.read_text(encoding="utf-8").strip()


def call_api(body, key, timeout):
    """One network attempt. Returns (http_status, response_text)."""
    req = urllib.request.Request(URL, data=json.dumps(body).encode("utf-8"), method="POST",
                                 headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        return 0, repr(e)


def model_answered(http_status, text):
    """True when the response carries a model message. Only such responses are cached."""
    if http_status != 200:
        return False
    try:
        return isinstance(json.loads(text)["choices"][0]["message"], dict)
    except (ValueError, KeyError, IndexError, TypeError):
        return False


def label_from(content):
    """Return (submission fields, parse note). No repair of any kind."""
    malformed = {"construction_status": "error", "decision": "abstain", "readings": []}
    if not isinstance(content, str):
        return malformed, "malformed: no text content"
    try:
        r = json.loads(content)
    except ValueError:
        return malformed, "malformed: not JSON"
    if not isinstance(r, dict):
        return malformed, "malformed: not a JSON object"
    try:
        ok = (r["construction_status"] in STATUS and r["decision"] in DECISION
              and isinstance(r["readings"], list) and all(isinstance(x, str) for x in r["readings"]))
    except (KeyError, TypeError):
        ok = False
    if not ok:
        return malformed, "malformed: fields missing or invalid"
    return {k: r[k] for k in ("construction_status", "decision", "readings")}, "ok"


class Budget:
    """Hard stop on network attempts in this invocation."""

    def __init__(self, limit):
        self.limit, self.used, self.lock = limit, 0, threading.Lock()

    def take(self):
        with self.lock:
            if self.used >= self.limit:
                return False
            self.used += 1
            return True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True)
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--max-calls", type=int, required=True, help="hard stop on network attempts in this invocation")
    ap.add_argument("--replay", action="store_true", help="read the cache only; make zero network calls")
    ap.add_argument("--limit", type=int, help="label only the first N inputs")
    ap.add_argument("--cache-dir", default=str(HERE / "cache"))
    ap.add_argument("--key-file", default="~/.config/openrouter/key")
    ap.add_argument("--max-tokens", type=int, default=8000)
    ap.add_argument("--response-format", choices=["none", "json_object"], default="none")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=300, help="seconds per network attempt")
    args = ap.parse_args()

    rows = load_inputs(args.inputs)[:args.limit]
    system = system_prompt()
    system_digest = sha256(system.encode("utf-8"))
    cache = Path(args.cache_dir)
    (cache / "prompts").mkdir(parents=True, exist_ok=True)
    (cache / "prompts" / (system_digest + ".txt")).write_text(system, encoding="utf-8")
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    key = None if args.replay else read_key(args.key_file)
    budget = Budget(0 if args.replay else args.max_calls)
    failures = open(out_dir / "transport_failures.jsonl", "a", encoding="utf-8")
    failures_lock = threading.Lock()

    def entry_for(row):
        """Return the cache entry for one input, calling the API if allowed and needed."""
        body = request_body(args.model, system, row["input"], args.max_tokens, args.response_format)
        digest = sha256(canonical(body))
        path = cache / digest[:2] / (digest + ".json")
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8")), True
        for _ in range(ATTEMPTS):
            if not budget.take():
                return None, False
            http_status, text = call_api(body, key, args.timeout)
            if model_answered(http_status, text):
                stored = dict(body, messages=[{"role": "system", "content_sha256": system_digest}, body["messages"][1]])
                entry = {"request_sha256": digest, "request": stored, "response_text": text,
                         "received_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
                path.parent.mkdir(exist_ok=True)
                tmp = path.with_suffix(".tmp")
                tmp.write_text(json.dumps(entry, ensure_ascii=False), encoding="utf-8")
                tmp.replace(path)
                return entry, False
            with failures_lock:
                failures.write(json.dumps({"id": row["id"], "request_sha256": digest, "http_status": http_status,
                                           "response_text": text[:2000],
                                           "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}) + "\n")
                failures.flush()
            time.sleep(5)
        return None, False

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(entry_for, rows))
    failures.close()

    totals = {"prompt_tokens": 0, "completion_tokens": 0, "reasoning_tokens": 0, "cost": 0.0}
    counts = {"inputs": len(rows), "labelled": 0, "malformed": 0, "no_response": 0, "from_cache": 0}
    with open(out_dir / "submission.jsonl", "w", encoding="utf-8") as sub, \
            open(out_dir / "raw.jsonl", "w", encoding="utf-8") as raw:
        for row, (entry, cached) in zip(rows, results):
            if entry is None:
                counts["no_response"] += 1      # no row: the scorer counts a missing ID as an abstention
                continue
            resp = json.loads(entry["response_text"])
            choice = resp["choices"][0]
            content = choice["message"].get("content")
            label, note = label_from(content)
            usage = resp.get("usage") or {}
            reasoning = (usage.get("completion_tokens_details") or {}).get("reasoning_tokens") or 0
            totals["prompt_tokens"] += usage.get("prompt_tokens") or 0
            totals["completion_tokens"] += usage.get("completion_tokens") or 0
            totals["reasoning_tokens"] += reasoning
            totals["cost"] += usage.get("cost") or 0
            counts["labelled"] += 1
            counts["malformed"] += note != "ok"
            counts["from_cache"] += cached
            sub.write(json.dumps({"id": row["id"], **label}, ensure_ascii=False) + "\n")
            raw.write(json.dumps({"id": row["id"], "request_sha256": entry["request_sha256"], "parse": note,
                                  "content": content, "finish_reason": choice.get("finish_reason"),
                                  "returned_model": resp.get("model"), "provider": resp.get("provider"),
                                  "usage": usage, "received_utc": entry["received_utc"]}, ensure_ascii=False) + "\n")

    run = {"model": args.model, "inputs_file": args.inputs,
           "inputs_sha256": sha256(Path(args.inputs).read_bytes()),
           "system_prompt_sha256": system_digest,
           "instructions_sha256": sha256((HERE / "instructions.txt").read_bytes()),
           "contract_sha256": sha256((REPO / "spec/contract.md").read_bytes()),
           "ontology_sha256": sha256((REPO / "spec/ontology.yaml").read_bytes()),
           "script_sha256": sha256(Path(__file__).read_bytes()),
           "temperature": 0, "max_tokens": args.max_tokens, "response_format": args.response_format,
           "replay": args.replay, "max_calls": args.max_calls, "network_attempts_this_run": budget.used,
           "counts": counts, "usage_totals_over_labelled_rows": totals,
           "submission_sha256": sha256((out_dir / "submission.jsonl").read_bytes())}
    (out_dir / "run.json").write_text(json.dumps(run, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(run, indent=1))
    if counts["no_response"]:
        sys.exit(3)


if __name__ == "__main__":
    main()
