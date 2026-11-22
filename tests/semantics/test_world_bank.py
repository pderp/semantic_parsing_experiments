"""Direct hand-written probes; no parser, private evaluator or submission is used."""
import hashlib
import json
import unittest

from src.semantics import SemanticError
from src.semantics.world_bank import BANK_FILE, BANK_SHA256, FULL, load_bank
from tools.build_world_bank import build, canonical


def conjunction(*parts):
    result = parts[-1]
    for part in reversed(parts[:-1]):
        result = f"(And {part} {result})"
    return result


def event(kind, agent, *other, tense=True):
    facts = [f"({kind} e)", f"(Agent e {agent})", *other]
    if tense:
        facts.append("(Past e)")
    return f"(ExistsV (fn e V {conjunction(*facts)}))"


def every(var, body):
    return f"(ForallE (fn {var} E (Implies (Researcher {var}) {body})))"


def paper(var, body):
    return f"(ExistsE (fn {var} E (And (Paper {var}) {body})))"


def control(kind, agent, recipient, controller, quick=False):
    extra = ["(Quick e)"] if quick else []
    payload = event("Leave", controller, *extra, tense=False)
    return event(kind, agent, f"(Recipient e {recipient})", f"(Content e (Box {payload}))")


class WorldBankTests(unittest.TestCase):
    def setUp(self):
        self.bank = load_bank()

    def check_hand(self, n, sentence, expected):
        sig = self.bank.signature(sentence)
        value = (int(sig["matrix"], 16) >> (64 + n)) & 1
        self.assertEqual(bool(value), expected, (n, sentence))

    def test_identity_regeneration_and_domain_coverage(self):
        actual = BANK_FILE.read_bytes()
        self.assertEqual(actual, (canonical(build()) + "\n").encode("ascii"))
        self.assertEqual(hashlib.sha256(actual).hexdigest(), BANK_SHA256)
        self.assertEqual(self.bank.ids[63:65], ("E63", "H00"))
        self.assertEqual(self.bank.ids[79:81], ("H15", "S000"))
        self.assertEqual(self.bank.ids[-1], "S175")
        worlds = json.loads(actual)["worlds"]
        self.assertEqual(len({canonical([w["facts"], w["content"]]) for w in worlds}), 256)
        for name, sorts in self.bank.sorts.items():
            if name == "Content":
                continue
            width = {("E",): 4, ("V",): 3, ("V", "E"): 12}[tuple(sorts)]
            for bit in range(width):
                values = {bool(w["facts"].get(name, 0) & (1 << bit)) for w in worlds[80:]}
                self.assertEqual(values, {False, True}, (name, bit))
        self.assertEqual(int(self.bank.signature("Top")["matrix"], 16), FULL)
        with self.assertRaises(ValueError):
            self.bank.signature("(Leave alice)")
        with self.assertRaises(SemanticError):
            self.bank.signature("(Researcher #0)")

    def test_scope_and_reversal(self):
        review = event("Review", "x", "(Theme e y)")
        sw, ow = every("x", paper("y", review)), paper("y", every("x", review))
        mask = (1 << 64) - 1
        self.assertEqual(int(self.bank.signature(sw)["matrix"], 16) & mask, 1 << 63)
        self.assertEqual(int(self.bank.signature(ow)["matrix"], 16) & mask, 0)
        for n, agent, theme in [(0, "alice", "bob"), (1, "bob", "alice")]:
            self.check_hand(n, event("Review", agent, f"(Theme e {theme})"), True)
            self.check_hand(n, event("Review", theme, f"(Theme e {agent})"), False)
        for n in (2, 3):
            self.check_hand(n, sw, True)
            self.check_hand(n, ow, n == 3)

    def test_mixed_scope_strata(self):
        probes = json.loads(BANK_FILE.with_name("world_bank_blind_probes_v1.json").read_bytes())
        self.assertEqual(probes["bank_sha256"], BANK_SHA256)
        by_id = {w["id"]: w for w in json.loads(BANK_FILE.read_bytes())["worlds"]}
        for world, themes in [("S065", 132), ("S091", 204)]:
            facts = by_id[world]["facts"]
            for noun, sorts in self.bank.sorts.items():
                if sorts == ["E"]:
                    self.assertEqual(facts[noun], 12, (world, noun))
            for pred in ("Cite", "Discuss", "Evaluate", "Review", "Past", "Quick"):
                self.assertEqual(facts[pred], 3, (world, pred))
            self.assertEqual((facts["Agent"], facts["Theme"]), (132, themes))
        body = event("Discuss", "x", "(Theme e y)", "(Quick e)")
        subject = every("x", paper("y", body))
        obj = paper("y", every("x", body))
        for name, values in [("S065", [True, False]), ("S091", [True, True])]:
            bit = 1 << self.bank.ids.index(name)
            self.assertEqual([bool(int(self.bank.signature(r)["matrix"], 16) & bit)
                              for r in (subject, obj)], values)

    def test_polarity_event_attachment_and_aliases(self):
        alice, bob = event("Leave", "alice"), event("Leave", "bob")
        for n, a, b in [(4, False, False), (5, True, False), (6, False, True)]:
            self.check_hand(n, alice, a)
            self.check_hand(n, bob, b)
            self.check_hand(n, f"(Not {alice})", not a)
        self.check_hand(5, every("x", "(Not " + event("Leave", "x") + ")"), False)
        self.check_hand(5, "(Not " + every("x", event("Leave", "x")) + ")", True)
        for n in (7, 8):
            self.check_hand(n, alice, True)
            self.check_hand(n, event("Leave", "alice", "(Quick e)"), n == 7)
        self.check_hand(9, event("Leave", "alice", tense=False), True)
        self.check_hand(9, f"(Not {alice})", True)
        self.assertEqual(self.bank.signature_set([alice, alice]),
                         self.bank.signature_set([event("Leave", "cara")]))

    def test_content_uses_the_same_outer_assignment(self):
        for n, frame, right, wrong, matches in [(10, "Promise", "alice", "bob", True),
                                                 (11, "Persuade", "bob", "alice", True),
                                                 (12, "Promise", "alice", "bob", False),
                                                 (13, "Persuade", "bob", "alice", False)]:
            self.check_hand(n, control(frame, "alice", "bob", right), matches)
            self.check_hand(n, control(frame, "alice", "bob", wrong), not matches)
            self.check_hand(n, "(ExistsV (fn e V (Leave e)))", False)
        self.check_hand(10, control("Promise", "alice", "bob", "alice", quick=True), False)
        for n, frame, agent, recipient, wrong in [(14, "Promise", "x", "bob", "bob"),
                                                   (15, "Persuade", "alice", "x", "alice")]:
            test = every("x", control(frame, agent, recipient, "x"))
            self.check_hand(n, test, True)
            self.check_hand(n, every("x", control(frame, agent, recipient, wrong)), False)
            table, = self.bank.signature(test)["payloads"]
            self.assertEqual(table["binder_sorts"], ["V", "E"])
            self.assertEqual(len(table["vectors"]), 12)
            for event_slot in range(3):
                for entity, name in enumerate(("alice", "bob", "ava", "ben")):
                    expected = self.bank.signature(event("Leave", name, tense=False))["matrix"]
                    self.assertEqual(table["vectors"][event_slot * 4 + entity], expected)

    def test_matching_matrices_can_have_different_boxed_payloads(self):
        sentences = [conjunction("(Not Top)", control("Promise", "alice", "bob", who))
                     for who in ("alice", "bob")]
        signatures = [self.bank.signature(s) for s in sentences]
        self.assertEqual([int(s["matrix"], 16) for s in signatures], [0, 0])
        self.assertNotEqual(signatures[0]["payloads"], signatures[1]["payloads"])
        self.assertEqual(len(self.bank.signature_set(sentences)), 2)
