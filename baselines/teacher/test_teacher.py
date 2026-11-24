#!/usr/bin/env python3
"""Offline tests for teacher.py. The network function is replaced; no request leaves the machine.

    python3 -m unittest baselines/teacher/test_teacher.py
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import teacher

GOOD = '{"construction_status": "complete", "decision": "accepted", "readings": ["(X  y)"]}'
SECRET = "TARGET-TEXT-THAT-MUST-NOT-BE-SENT"


def api_reply(content, finish="stop"):
    return 200, json.dumps({"model": "m", "provider": "p",
                            "choices": [{"message": {"role": "assistant", "content": content}, "finish_reason": finish}],
                            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "cost": 0.001}})


class TeacherTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.inputs = self.dir / "in.jsonl"
        self.inputs.write_text("".join(json.dumps({"id": f"T{i}", "input": f"Alice left {i}.", "readings": [SECRET]}) + "\n"
                                       for i in range(4)))
        self.sent = []

    def tearDown(self):
        self.tmp.cleanup()

    def run_teacher(self, replies, *extra):
        """Run main() with call_api replaced. Returns (exit code, run.json, submission rows)."""
        def fake(body, key, timeout):
            self.sent.append(body)
            return replies(body) if callable(replies) else replies
        argv = ["teacher.py", "--model", "m", "--inputs", str(self.inputs), "--out-dir", str(self.dir / "out"),
                "--cache-dir", str(self.dir / "cache"), "--workers", "1", *extra]
        code = 0
        with mock.patch.object(teacher, "call_api", fake), mock.patch.object(teacher.time, "sleep", lambda s: None), \
                mock.patch.object(sys, "argv", argv), mock.patch.dict(os.environ, {"OPENROUTER_API_KEY": "k"}), \
                mock.patch("builtins.print"):
            try:
                teacher.main()
            except SystemExit as e:
                code = e.code
        run = json.loads((self.dir / "out" / "run.json").read_text())
        sub = [json.loads(l) for l in (self.dir / "out" / "submission.jsonl").read_text().splitlines()]
        return code, run, sub

    def test_label_is_copied_unchanged_and_targets_are_not_sent(self):
        code, run, sub = self.run_teacher(api_reply(GOOD), "--max-calls", "10")
        self.assertEqual(code, 0)
        self.assertEqual(len(self.sent), 4)
        self.assertEqual([r["readings"] for r in sub], [["(X  y)"]] * 4)     # double space kept: no normalization
        self.assertNotIn(SECRET, json.dumps(self.sent))
        self.assertEqual(self.sent[0]["temperature"], 0)
        self.assertEqual(run["usage_totals_over_labelled_rows"]["prompt_tokens"], 40)

    def test_replay_makes_no_call_and_reproduces_the_submission(self):
        _, first, sub1 = self.run_teacher(api_reply(GOOD), "--max-calls", "10")
        self.sent.clear()
        code, second, sub2 = self.run_teacher(api_reply("SHOULD NOT BE USED"), "--max-calls", "10", "--replay")
        self.assertEqual((code, self.sent, sub2), (0, [], sub1))
        self.assertEqual(second["submission_sha256"], first["submission_sha256"])
        self.assertEqual(second["counts"]["from_cache"], 4)

    def test_replay_with_empty_cache_makes_no_call(self):
        code, run, sub = self.run_teacher(api_reply(GOOD), "--max-calls", "10", "--replay")
        self.assertEqual((code, self.sent, sub), (3, [], []))
        self.assertEqual(run["counts"]["no_response"], 4)

    def test_max_calls_is_a_hard_stop(self):
        code, run, sub = self.run_teacher(api_reply(GOOD), "--max-calls", "2")
        self.assertEqual((code, len(self.sent), len(sub)), (3, 2, 2))
        self.assertEqual(run["network_attempts_this_run"], 2)

    def test_malformed_output_is_recorded_as_error_abstain_with_raw_text_kept(self):
        fenced = "```json\n" + GOOD + "\n```"
        for content in (fenced, "not json", '{"decision": "accepted"}', '["x"]', None,
                        '{"construction_status": "complete", "decision": "sure", "readings": []}'):
            self.assertEqual(teacher.label_from(content)[0],
                             {"construction_status": "error", "decision": "abstain", "readings": []})
        _, run, sub = self.run_teacher(api_reply(fenced), "--max-calls", "10")
        self.assertEqual(run["counts"]["malformed"], 4)
        self.assertEqual(sub[0], {"id": "T0", "construction_status": "error", "decision": "abstain", "readings": []})
        raw = [json.loads(l) for l in (self.dir / "out" / "raw.jsonl").read_text().splitlines()]
        self.assertEqual(raw[0]["content"], fenced)

    def test_malformed_answer_is_cached_and_not_asked_again(self):
        self.run_teacher(api_reply("not json"), "--max-calls", "10")
        self.sent.clear()
        _, run, _ = self.run_teacher(api_reply(GOOD), "--max-calls", "10")
        self.assertEqual((self.sent, run["counts"]["malformed"]), ([], 4))

    def test_transport_failure_is_retried_but_not_cached(self):
        code, run, sub = self.run_teacher((429, '{"error": {"message": "rate limited"}}'), "--max-calls", "100")
        self.assertEqual((code, sub, len(self.sent)), (3, [], 4 * teacher.ATTEMPTS))
        self.assertEqual(list((self.dir / "cache").glob("??/*.json")), [])
        self.assertEqual(len((self.dir / "out" / "transport_failures.jsonl").read_text().splitlines()), 12)

    def test_key_file_readable_by_others_is_refused(self):
        key = self.dir / "key"
        key.write_text("k")
        key.chmod(0o644)
        with mock.patch.dict(os.environ, {}, clear=True), self.assertRaises(SystemExit):
            teacher.read_key(str(key))
        key.chmod(0o600)
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(teacher.read_key(str(key)), "k")


if __name__ == "__main__":
    unittest.main()
