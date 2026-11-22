import unittest

from src.reference import load_seed, parse
from src.reference.restrictions import restrict_bundle
from .compare_witness_cases import compare, frozen_inputs


class RestrictedGrammarTests(unittest.TestCase):
    def test_frozen_cases(self):
        cases, bundles = frozen_inputs()
        for case in cases:
            with self.subTest(case=case["id"]):
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
