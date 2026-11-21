import unittest
from pathlib import Path

from src.frontend import GrammarError, Item, check
from src.semantics import K, R, V, app, call, const, lam, normalize, var

KERNEL = r"""
(depth 3)
(field frame simple control)
(binary fa FA)
(binary ba BA)
(binary fc FC)
(binary bc BC)
(lex noun (paper) N Paper ((frame simple)) (if frame simple 2 6))
(lex negf (without) (/ N N) (lam (-> E P) (lam E (Not (#1 #0)))) () 0)
(lex negb (without) (\ N N) (lam (-> E P) (lam E (Not (#1 #0)))) () 0)
(lex addf (both) (/ N N) (lam (-> E P) (lam E (And (Researcher #0) (#1 #0)))) () 0)
(lex addb (both) (\ N N) (lam (-> E P) (lam E (And (Researcher #0) (#1 #0)))) () 0)
"""


class KernelTests(unittest.TestCase):
    def setUp(self):
        self.grammar = check(KERNEL, "example.metta", "kernel")

    def item(self, name, start):
        e = self.grammar.entries[name]
        return Item(start, start + len(e.surface), e.category, e.meaning)

    def test_four_combinators_preserve_direction_types_and_meaning(self):
        noun, negf, negb = self.item("noun", 1), self.item("negf", 0), self.item("negb", 2)
        for item in (self.grammar.combine("fa", negf, noun), self.grammar.combine("ba", noun, negb)):
            actual = normalize(app(item.meaning, const("alice"))).normal
            self.assertEqual(actual, call("Not", call("Paper", const("alice"))))
        fwd = self.grammar.combine("fc", negf, self.item("addf", 1))
        bwd = self.grammar.combine("bc", self.item("addb", 1), negb)
        alice = const("alice")
        expected = call("Not", call("And", call("Paper", alice), call("Researcher", alice)))
        for composed in (fwd, bwd):
            self.assertEqual(normalize(app(composed.meaning, const("Paper"), alice)).normal, expected)
        self.assertEqual(fwd.category, negf.category)
        self.assertEqual((bwd.start, bwd.end, bwd.category), (1, 3, negb.category))

    def test_span_direction_and_category_mismatches(self):
        noun = self.item("noun", 0)
        self.assertIsNone(self.grammar.combine("ba", noun, self.item("negb", 2)))
        self.assertIsNone(self.grammar.combine("fa", noun, self.item("negf", 1)))
        self.assertIsNone(self.grammar.combine("fc", self.item("negf", 0), self.item("addb", 1)))
        self.assertIsNone(self.grammar.combine("fa", self.item("negf", 0), self.item("negb", 1)))
        with self.assertRaisesRegex(GrammarError, "example.metta:.*fa: child meaning"):
            self.grammar.combine("fa", self.item("negf", 0), Item(1, 2, "N", const("alice")))

    def test_finite_cost_observations(self):
        entry = self.grammar.entries["noun"]
        self.assertEqual((entry.fields, entry.cost), ((("frame", "simple"),), 2))
        with self.assertRaises(TypeError):
            self.grammar.entries["noun"] = entry

    def test_seed_profile_and_explicit_unary_order(self):
        kernel = Path("grammar/kernel.metta")
        self.assertEqual({kind for kind, _ in check(kernel.read_text()).binary.values()}, {"FA", "BA"})
        with self.assertRaisesRegex(GrammarError, "seed.fc: composition"):
            check("(depth 3)\n(binary seed.fc FC)")
        unary = "(unary lift N S[bare] (lam (-> E P) (lam (-> V P) Top)) 1)"
        grammar = check("(depth 3)\n" + unary, profile="kernel")
        self.assertLess(grammar.unary_order.index("N"), grammar.unary_order.index("S[bare]"))
        with self.assertRaisesRegex(GrammarError, "lift: same-span"):
            check("(depth 3)\n" + unary)
        reverse = "(unary drop S[bare] N (lam (-> (-> V P) P) Paper) 1)"
        with self.assertRaisesRegex(GrammarError, r"lift.*drop.*unary cycle"):
            check("(depth 3)\n" + unary + "\n" + reverse, profile="kernel")

    def test_concrete_type_raising_preserves_its_input(self):
        decl = r"""(depth 3)
(unary raise.n N (/ S[fin] (\ S[fin] N))
  (lam (-> E P) (lam (-> (-> E P) (-> (-> V P) P)) (#0 #1))) 0)
"""
        rule = check(decl, profile="kernel").unary["raise.n"]
        continuation = lam(R, lam(K, app(var(1), const("bob"))))
        result = app(rule.builder, const("Paper"), continuation, lam(V, const("Top")))
        self.assertEqual(normalize(result).normal, call("Paper", const("bob")))

    def test_source_located_rejection_fixtures(self):
        cases = [
            ("(lex bad () N Paper () 0)", "empty"),
            ("(raise bad any)", "unlicensed"),
            ("(lex bad (x) (/ N (/ N N)) Paper () 0)", "depth"),
            ("(lex bad (x) $any Paper () 0)", "unbounded category"),
            ("(lex bad (x) S[present] Top () 0)", "unknown"),
            ("(lex bad (x) N alice () 0)", "builder type"),
            ("(lex bad (x) N (exec alice) () 0)", "unknown symbol"),
            ("(lex bad (x) N Paper ((frame missing)) 0)", "undeclared field"),
            ("(lex bad (x) N Paper () (if frame simple 0 1))", "undeclared score observation"),
            ("(lex bad (x) N Paper () 9223372036854775808)", "overflow"),
            ("(lex bad (x) N #0 () 0)", "unbound de Bruijn"),
            ("(binary bad FX)", "unlicensed"),
        ]
        for decl, reason in cases:
            with self.subTest(decl=decl), self.assertRaisesRegex(
                    GrammarError, f"invalid.metta:3:1 bad: .*{reason}"):
                check("(depth 1)\n(field frame simple)\n" + decl, "invalid.metta", "kernel")
        with self.assertRaisesRegex(GrammarError, "duplicate declaration"):
            check("(depth 2) (binary dup FA) (binary dup BA)")
        with self.assertRaisesRegex(GrammarError, "unclosed declaration"):
            check("(depth 2)\n(lex bad")
