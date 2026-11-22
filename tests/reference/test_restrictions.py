import unittest

from src.reference import load_seed, parse
from src.reference.restrictions import restrict_bundle
from .compare_witness_cases import SUITES, compare, frozen_inputs, read_suite


class RestrictedGrammarTests(unittest.TestCase):
    def test_frozen_cases(self):
        for seed in SUITES:
            cases, bundles = frozen_inputs(seed)
            for case in cases:
                with self.subTest(seed=seed, case=case["id"]):
                    _, differences = compare(case, bundles[case["grammar"]])
                    self.assertEqual(differences, {})

    def test_seed_1_0_cases_under_seed_1_1(self):
        legacy = read_suite("seed-1.0")
        _, current = frozen_inputs("seed-1.1")
        bundles = {key: restrict_bundle(current["full"], spec) for key, spec in legacy["grammars"].items()}
        for case in legacy["cases"]:
            with self.subTest(case=case["id"]):
                if case["id"] == "W069":
                    expected = dict(case["expected"], construction_status="no_parse", decision="abstain",
                                    diagnostic={"code": "no_root"}, readings=[], ranked_readings=[],
                                    witnesses=[], min_cost=None)
                    case = dict(case, expected=expected, edge_count=3)
                elif case["id"] == "W073":
                    case = dict(case, edge_count=5)
                _, differences = compare(case, bundles[case["grammar"]])
                self.assertEqual(differences, {})

    def test_chart_wide_overflow_and_precedence(self):
        # A second name entry keeps a safe root available. Its competitor
        # overflows at the verb-object combination even outside all active roots.
        seed = load_seed()
        for limit, delta in [(2**63 - 1, 1), (-2**63, -1)]:
            spec = {"entries": ["name.alice", "name.bob"], "clones": [
                {"id": "bob.cost", "clone_of": "name.bob", "cost": delta},
                {"id": "verb.cost", "clone_of": "cite.tv.past.unit.unit.subject-wide", "cost": limit},
            ]}
            for roots in [list(seed.roots), []]:
                bundle = restrict_bundle(seed, dict(spec, roots=roots))
                result = parse("alice cited bob", bundle=bundle)
                self.assertEqual((result["diagnostic"], result["witnesses"], result["min_cost"]),
                                 ("cost_overflow", [], None))
                self.assertEqual(parse("alice cited bob", bundle=bundle, max_edges=1)["diagnostic"],
                                 "edge_budget")

    def test_request_shape_and_clone_guards(self):
        base = load_seed()
        spec = {"entries": ["noun.editor", "leave.iv.past.existential"], "clones": [
            {"id": "det.vowel", "clone_of": "det.an", "tokens": ["one"]}]}
        bundle = restrict_bundle(base, spec)
        self.assertEqual(parse("one editor left", bundle=bundle)["decision"], "accepted")
        self.assertEqual(parse("one left", bundle=bundle)["edges"], 1)
        for value in (True, False, 5.0, "5", -1):
            self.assertEqual(parse("unknown", max_edges=value)["tokens"], [])
        self.assertEqual(parse("alice left", max_edges=None), parse("alice left"))
        for change in [{"entries": ["outside"]}, {"roots": ["NP"]}, {"max_tokens": True},
                       {"clones": [{"id": "name.alice", "clone_of": "name.alice"}]},
                       {"clones": [{"id": "new", "clone_of": "name.alice", "cost": 2**63}]}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                restrict_bundle(base, change)
