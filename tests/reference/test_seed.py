from dataclasses import replace
import json
import unittest

from src.frontend import binary_category
from src.reference import Node, PackedForest, parse
from src.reference.seed import load_seed
from src.semantics import ROOT, SemanticError, call, const, reading_set


def public_variants():
    """One lexical realization per public determiner variant; no split assignment."""
    subjects = ("Alice", "a researcher", "every researcher")
    objects = ("Bob", "a paper", "every paper")
    recipients = ("Bob", "a reviewer", "every reviewer")
    for root in ("ordinary", "negative", "not-every"):
        for subject in subjects if root != "not-every" else ("not every researcher",):
            prefix = subject + (" did not " if root == "negative" else " ")
            finite = root != "negative"
            for suffix in ("", " quickly"):
                yield prefix + ("left" if finite else "leave") + suffix
                for obj in objects:
                    yield prefix + ("reviewed " if finite else "review ") + obj + suffix
                for control in (("promised", "promise"), ("persuaded", "persuade")):
                    for recipient in recipients:
                        matrix = prefix + control[0 if finite else 1] + " " + recipient + " to "
                        yield matrix + "arrive" + suffix
                        for obj in objects:
                            yield matrix + "cite " + obj + suffix


class SeedTests(unittest.TestCase):
    def test_existential_articles(self):
        nouns = json.loads((ROOT / "spec/ontology.yaml").read_text())["nouns"]
        vowel_nouns = {"abstract", "analyst", "article", "author", "editor", "investigator"}
        bundle = load_seed()
        self.assertEqual(set(bundle.inventory()["next_nouns"]["det.an"]), vowel_nouns)
        self.assertEqual(set(bundle.next_nouns["det.a"]), set(nouns) - vowel_nouns)
        for noun, predicate in nouns.items():
            article, wrong = ("an", "a") if noun in vowel_nouns else ("a", "an")
            for frame in ("{} left.", "Bob reviewed {}.", "Alice promised {} to leave.",
                          "Bob did not persuade Alice to cite {}."):
                with self.subTest(noun=noun, frame=frame):
                    result = parse(frame.format(f"{article} {noun}"))
                    self.assertEqual(result["decision"], "accepted")
                    self.assertIn("ExistsE", result["readings"][0])
                    self.assertIn("(" + predicate + " #0)", result["readings"][0])
                    rejected = parse(frame.format(f"{wrong} {noun}"))
                    self.assertEqual((rejected["construction_status"], rejected["decision"],
                                      rejected["diagnostic"], rejected["witnesses"]),
                                     ("no_parse", "abstain", "no_root", []))
            self.assertEqual(parse(f"Every {noun} left.")["decision"], "accepted")
        upper = parse(" AN\tEDITOR left. ")
        key = upper["witnesses"][0]["key"]
        self.assertEqual(key[6][0][6][0], (0, 0, 1, "det.an", "det"))
        self.assertEqual(upper["readings"], parse("an editor left")["readings"])

    def test_reconciled_fixtures(self):
        prompts = json.loads((ROOT / "fixtures/prompts_v1.json").read_text())["prompts"]
        gold = {row["id"]: row for row in json.loads((ROOT / "fixtures/reconciled_v1.json").read_text())["fixtures"]}
        self.assertEqual(set(gold), {p["id"] for p in prompts})
        for prompt in prompts:
            with self.subTest(id=prompt["id"]):
                result = parse(prompt["input"])
                for key in ("tokens", "construction_status", "decision", "readings"):
                    self.assertEqual(result[key], gold[prompt["id"]][key])

    def test_public_family_reading_counts(self):
        variants = list(public_variants())
        self.assertEqual(len(set(variants)), 392)
        counts = {1: 0, 2: 0}
        for sentence in variants:
            result = parse(sentence)
            self.assertEqual(result["construction_status"], "complete", sentence)
            counts[len(result["readings"])] += 1
        self.assertEqual(counts, {1: 386, 2: 6})

    def test_scope_filters_and_shared_packed_edges(self):
        for text, witnesses, meanings in [
            ("Alice reviewed Bob", 2, 1),
            ("Every researcher cited every paper quickly", 1, 1),
            ("A reviewer did not cite a manuscript", 2, 1),
            ("A reviewer persuaded every student to cite a paper", 2, 1),
            ("Not every researcher reviewed a paper", 2, 2),
        ]:
            with self.subTest(text=text):
                result = parse(text)
                self.assertEqual((len(result["witnesses"]), len(result["readings"])), (witnesses, meanings))
                self.assertEqual([w["object_wide_uses"] for w in result["witnesses"]], list(range(witnesses)))
                self.assertEqual({w["cost"] for w in result["witnesses"]}, {10})
        forest = PackedForest(load_seed())
        forest.build(["alice", "reviewed", "bob"])
        node = Node(1, 3, ("\\", "S[fin,simple,plain]", "NP[unit]"))
        self.assertEqual(len(forest.edges[node]), 1)  # both costs/recipes packed in its lexical child
        lexical, _ = next(iter(forest.edges[node])).children
        self.assertEqual(len(forest.edges[lexical]), 2)
        old_count = forest.edge_count
        forest.insert(lexical, next(iter(forest.edges[lexical])))
        self.assertEqual(forest.edge_count, old_count)
        witness = parse("Alice reviewed Bob")["witnesses"][0]["key"]
        self.assertEqual(witness[:6], (1, "seed.ba", 0, 3, "S[fin,simple,plain]", "apply"))
        self.assertEqual(witness[6][0], (0, 0, 1, "name.alice", "name"))

    def test_close_contrasts(self):
        for sentence in ("Alice left quickly quickly", "Alice promised Bob to leave quickly quickly",
                         "Alice promised Bob to promise Dan to wait", "Alice to leave", "Bob leave",
                         "Not every researcher did not leave", "A paper did not left",
                         "Alice quickly reviewed Bob", "Alice promised Bob leave"):
            with self.subTest(sentence=sentence):
                self.assertEqual(parse(sentence)["diagnostic"], "no_root")
        self.assertNotEqual(parse("Alice cited Bob")["readings"], parse("Bob cited Alice")["readings"])
        for verb, who in (("promised", "alice"), ("persuaded", "bob")):
            text, = parse(f"Alice {verb} Bob to speak quickly")["readings"]
            self.assertIn(f"(Box (ExistsV (lam V (And (Agent #0 {who})", text)
            self.assertIn("(Quick #0)", text)

    def test_all_lexical_frames_and_morphology(self):
        ontology = json.loads((ROOT / "spec/ontology.yaml").read_text())
        for frame in ontology["frames"].values():
            tail = {"intransitive": "", "transitive": " Bob", "subject-control": " Bob to leave",
                    "object-control": " Bob to leave"}[frame["construction"]]
            for auxiliary, verb in (("", frame["past"]), ("did not ", frame["bare"])):
                sentence = "Alice " + auxiliary + verb + tail
                with self.subTest(sentence=sentence):
                    result = parse(sentence)
                    self.assertEqual(result["decision"], "accepted")
                    reading, = result["readings"]
                    self.assertIn("(" + frame["predicate"] + " #0)", reading)
                    self.assertEqual(reading.count("(Past "), 1)
                    self.assertEqual(reading.startswith("(Not "), bool(auxiliary))

    def test_tokenization_and_budget(self):
        for text in ("", ".", " \t. \r"):
            self.assertEqual(parse(text)["diagnostic"], "empty_input")
        self.assertEqual(parse(" BOB\vLEFT . ")["tokens"], ["bob", "left"])
        bad = parse("ALICE xyz bób.")
        self.assertEqual((bad["token_index"], bad["tokens"], bad["diagnostic"]),
                         (1, ["alice", "xyz", "bób"], "unknown_token"))
        self.assertEqual(parse("alice\N{NO-BREAK SPACE}left")["diagnostic"], "invalid_token")
        self.assertEqual(parse("alice " * 1000)["diagnostic"], "no_root")
        for value in (-1, 0.5, True):
            self.assertEqual(parse("Alice left", max_edges=value)["diagnostic"], "invalid_request")
        self.assertEqual(parse(None)["diagnostic"], "invalid_request")
        unlimited = parse("Alice left")
        self.assertEqual(parse("Alice left", max_edges=unlimited["edges"]), unlimited)
        limited = parse("Alice left", max_edges=unlimited["edges"] - 1)
        self.assertEqual((limited["construction_status"], limited["decision"], limited["diagnostic"],
                          limited["readings"], limited["witnesses"]),
                         ("truncated", "abstain", "edge_budget", [], []))

    def test_overflow_and_out_of_design(self):
        seed = load_seed()
        entries = dict(seed.grammar.entries)
        verb = "leave.iv.past.unit"
        entries[verb] = replace(entries[verb], cost=2**63 - 1)
        entries["name.alice"] = replace(entries["name.alice"], cost=1)
        custom = replace(seed, grammar=replace(seed.grammar, entries=entries))
        self.assertEqual(parse("alice left", bundle=custom)["diagnostic"], "cost_overflow")
        # Add two otherwise valid lexical alternatives to the same anchored node.
        surface = dict(seed.by_surface)
        alternatives = ("arrive.iv.past.unit", "wait.iv.past.unit")
        surface[("left",)] += alternatives
        custom = replace(seed, by_surface=surface)
        result = parse("alice left", bundle=custom)
        self.assertEqual((result["diagnostic"], result["construction_status"], result["decision"],
                          len(result["readings"]), len(result["witnesses"])),
                         ("reading_count", "error", "abstain", 3, 3))

    def test_saturation_and_depth_nonmatch(self):
        with self.assertRaisesRegex(SemanticError, "explicit logical binder"):
            reading_set([call("ForallE", const("Paper"))])
        counters = {}
        self.assertIsNone(binary_category("FC", ("/", ("/", "N", "N"), "NP"),
                                          ("/", "NP", "N"), 1, counters))
        self.assertEqual(counters, {"depth_rejections": 1})
