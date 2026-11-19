"""Acceptance checks for the scope spike. Run from the repository root:

    python3 -m unittest discover -s spike -v
"""
import random
import unittest

import scope_spike as sp

SENTENCE = "Every researcher reviewed a paper"
SUBJECT_WIDE = "review.tv.subject-wide"
OBJECT_WIDE = "review.tv.object-wide"


def lexical_ids(witness):
    if "lex" in witness:
        return [witness["lex"]]
    return [i for child in witness["children"] for i in lexical_ids(child)]


def reading_using(result, source):
    found = [r for r in result["readings"]
             if source in lexical_ids(r["derivations"][0]["witness"])]
    assert len(found) == 1
    return found[0]


class ScopeSpike(unittest.TestCase):
    def setUp(self):
        self.result = sp.parse(SENTENCE)

    def test_lexical_terms_match_their_categories(self):
        for source, lemma, category, _, build in sp.LEXICON:
            for feats in ({}, {"tense": "past"}):
                self.assertEqual(sp.typeof(build(feats)), sp.sem_type(category), source)

    def test_one_packed_root_keeps_both_recipes(self):
        tokens = sp.tokenize(SENTENCE)
        chart, _ = sp.build_chart(tokens, sp.LEXICON)
        roots = [n for n in chart if n[0] == 0 and n[1] == len(tokens)]
        self.assertEqual(roots, [(0, 5, sp.S)])
        self.assertEqual(len(chart[roots[0]]), 1)            # one packed root edge
        self.assertEqual(len(chart[(2, 3, sp.TV)]), 2)       # two verb recipes, one node
        self.assertEqual(len(chart[(2, 5, sp.bwd(sp.S, sp.NP))]), 1)
        self.assertEqual(len(sp.derivations(roots[0], chart)), 2)

    def test_two_distinct_normalized_readings(self):
        self.assertEqual(self.result["construction_status"], "complete")
        self.assertEqual(self.result["decision"], "ambiguous")
        normalized = [r["normalized"] for r in self.result["readings"]]
        self.assertEqual(len(normalized), 2)
        self.assertEqual(len(set(normalized)), 2)

    def test_each_witness_replays_to_its_reading(self):
        tokens = self.result["tokens"]
        for reading in self.result["readings"]:
            for derivation in reading["derivations"]:
                term, cost = sp.replay(derivation["witness"], tokens)
                _, norm = sp.meaning_of(term)
                self.assertEqual(sp.canonical(norm), reading["normalized"])
                self.assertEqual(cost, derivation["cost"])

    def test_separating_world(self):
        subject = reading_using(self.result, SUBJECT_WIDE)
        obj = reading_using(self.result, OBJECT_WIDE)
        self.assertTrue(sp.evaluate(subject["_term"], sp.SEPARATING_WORLD))
        self.assertFalse(sp.evaluate(obj["_term"], sp.SEPARATING_WORLD))
        # Sanity: with one shared paper both readings hold.
        self.assertTrue(sp.evaluate(subject["_term"], sp.SHARED_PAPER_WORLD))
        self.assertTrue(sp.evaluate(obj["_term"], sp.SHARED_PAPER_WORLD))

    def test_lexical_insertion_order_does_not_matter(self):
        expected = sp.public(self.result)
        self.assertEqual(sp.public(sp.parse(SENTENCE, sp.LEXICON[::-1])), expected)
        rng = random.Random(20261119)
        for _ in range(20):
            lexicon = sp.LEXICON[:]
            rng.shuffle(lexicon)
            self.assertEqual(sp.public(sp.parse(SENTENCE, lexicon)), expected)

    def test_expected_formulas(self):
        # Conjuncts are sorted by their canonical text, so a quantified
        # conjunct sorts before the restrictor ("(ExistsV" < "(Paper").
        self.assertEqual(
            reading_using(self.result, SUBJECT_WIDE)["pretty"],
            "forall x0. (Researcher(x0) -> exists x1. (exists e2. "
            "(Agent(e2, x0) & Past(e2) & Review(e2) & Theme(e2, x1)) & Paper(x1)))")
        self.assertEqual(
            reading_using(self.result, OBJECT_WIDE)["pretty"],
            "exists x0. (forall x1. (Researcher(x1) -> exists e2. "
            "(Agent(e2, x1) & Past(e2) & Review(e2) & Theme(e2, x0))) & Paper(x0))")

    def test_normalization_is_idempotent_and_drops_top(self):
        for reading in self.result["readings"]:
            term = reading["_term"]
            self.assertEqual(sp.normalize(term), term)
            self.assertNotIn("Top", reading["normalized"])
            self.assertIn("Top", reading["raw"])


class NamesAndFailures(unittest.TestCase):
    def test_names_give_two_derivations_and_one_meaning(self):
        result = sp.parse("Alice reviewed Bob")
        self.assertEqual(result["decision"], "accepted")
        self.assertEqual(len(result["readings"]), 1)
        self.assertEqual(len(result["readings"][0]["derivations"]), 2)

    def test_role_reversal_changes_the_meaning(self):
        ab = sp.parse("Alice reviewed Bob")["readings"][0]["normalized"]
        ba = sp.parse("Bob reviewed Alice")["readings"][0]["normalized"]
        self.assertNotEqual(ab, ba)

    def test_no_parse_is_reported_as_such(self):
        result = sp.parse("researcher every reviewed")
        self.assertEqual(result["construction_status"], "no_parse")
        self.assertEqual(result["decision"], "abstain")

    def test_ill_typed_application_is_rejected(self):
        with self.assertRaises(TypeError):
            sp.typeof(sp.app(sp.const("Researcher"), sp.const("Paper")))

    def test_substitution_avoids_capture(self):
        # (lam y. lam x. y) applied to a free variable must not capture it.
        term = sp.app(sp.lam(sp.E, sp.lam(sp.E, sp.var(1))), sp.var(0))
        self.assertEqual(sp.beta(term), sp.lam(sp.E, sp.var(1)))


if __name__ == "__main__":
    unittest.main()
