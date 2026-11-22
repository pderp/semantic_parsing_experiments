"""Compare the recovered design examples with the seed parser and typed kernel."""
import io
import runpy
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace

from src.frontend import GrammarError, Item, check, forms, template
from src.reference import parse
from src.semantics import (
    E, V, P, I, ROOT, SemanticError, app, arrow, canonical, close, const, lam,
    normalize, var,
)
from tests.semantics.test_appendix_b import evaluate

# The unmodified companion runs its assertions and prints its result when executed.
with redirect_stdout(io.StringIO()) as recorded:
    author = SimpleNamespace(**runpy.run_path(str(ROOT / 'docs/pre/semantic_reference_checks.py')))


SYMBOLS = {"researcher": "Researcher", "paper": "Paper", "allE": "ForallE",
           "existsE": "ExistsE", "existsV": "ExistsV", "Imp": "Implies"}
SORTS = {author.E: E, author.V: V, author.P: P, author.I: I}


def seed_sort(sort):
    if isinstance(sort, author.Arrow):
        return arrow(seed_sort(sort.arg), seed_sort(sort.result))
    return SORTS[sort]


def seed_term(term):
    """Relabel vocabulary and constructors only. Keep all arguments and binders."""
    match term:
        case author.Var(index):
            return var(index)
        case author.Const(name):
            return const(SYMBOLS.get(name, name))
        case author.Lam(sort, body):
            return lam(seed_sort(sort), seed_term(body))
        case author.App(fun, arg):
            return app(seed_term(fun), seed_term(arg))
    raise ValueError(f"unresolved author term: {term}")


def world(model):
    facts = {SYMBOLS.get(key, key): [list(row) for row in relation]
             for key, relation in model.items() if key not in ("entities", "events")}
    return {"entities": model["entities"], "events": model["events"], "facts": facts}


def parsed_term(sentence):
    reading, = parse(sentence)["readings"]
    (_, expression), = forms(reading, sentence)
    return template(expression)


class AuthorChecks(unittest.TestCase):
    def test_original_result(self):
        self.assertEqual(recorded.getvalue().encode("ascii"),
                         (ROOT / "docs/pre/semantic_checks_result.json").read_bytes())

    def test_seed_reading_sets_against_author_terms(self):
        cases = {
            "Alice reviewed Bob": (author.actual.sem,),
            "Every researcher reviewed a paper": (author.narrow, author.wide),
            "Alice promised Bob to leave": (author.prom,),
            "Alice persuaded Bob to leave": (author.pers,),
            "Every researcher promised Bob to leave": (author.prom_q,),
            "Alice persuaded every researcher to leave": (author.pers_q,),
            "Alice reviewed Bob quickly": (author.quick_expected,),
        }
        for sentence, terms in cases.items():
            with self.subTest(sentence=sentence):
                expected = sorted(canonical(normalize(seed_term(t)).normal) for t in terms)
                self.assertEqual(parse(sentence)["readings"], expected)
        witnesses = parse("Alice reviewed Bob")["witnesses"]
        self.assertEqual([w["object_wide_uses"] for w in witnesses], [0, 1])
        self.assertEqual(witnesses[0]["reading"], witnesses[1]["reading"])

    def test_seed_closure_on_author_continuations(self):
        def quantified_review(scope):
            verb = author.tv_h(scope)
            return author.ba(author.every_researcher_h, author.fa(verb, author.a_paper_h)).sem

        def control(frame, controller, subject):
            verb = author.control_h(frame, controller)
            return author.ba(subject, author.fa(author.fa(verb, author.bob_h), author.to_leave_h)).sem

        modified = author.ba(author.fa(author.tv_h("subject"), author.bob_h), author.quickly)
        negative = author.ba(author.alice_h, author.fa(author.neg_h, author.leave_h))
        cases = [
            (author.plain_h, author.actual.sem),
            (quantified_review("subject"), author.narrow),
            (quantified_review("object"), author.wide),
            (control("Promise", "s", author.alice_h), author.prom),
            (control("Persuade", "o", author.alice_h), author.pers),
            (control("Promise", "s", author.every_researcher_h), author.prom_q),
            (author.ba(author.alice_h, modified).sem, author.quick_expected),
            (negative.sem, author.negative),
        ]
        for index, (continuation, baseline) in enumerate(cases):
            with self.subTest(case=index):
                self.assertEqual(close(seed_term(continuation)).normal,
                                 normalize(seed_term(baseline)).normal)

    def test_named_binding_and_invalid_declarations(self):
        (_, expression), = forms("(fn y E ((fn x E (fn y E x)) y))", "hygiene")
        expected = lam(E, lam(E, var(1)))
        self.assertEqual(normalize(template(expression)).normal, expected)
        self.assertEqual(normalize(seed_term(author.hygiene)).normal, expected)
        for decl, message in [("(lex bad (x) N (fn x E free) () 0)", "unknown symbol"),
                              ("(lex bad (x) NP alice () 0)", "builder type")]:
            with self.subTest(decl=decl), self.assertRaisesRegex(GrammarError, message):
                check("(depth 3) " + decl)

    def test_typed_kernel_on_the_author_h_examples(self):
        declarations = r"""
(depth 4) (binary fa FA) (binary ba BA) (binary fc FC) (binary bc BC)
(unary raise.np NP (/ S[fin] (\ S[fin] NP))
  (fn q Q (fn f (-> Q H) (f q))) 0)
"""
        kernel = check(declarations, profile="kernel")
        vp = ("\\", "S[fin]", "NP")
        alice = Item(0, 1, "NP", seed_term(author.alice_h.sem))
        review = Item(1, 2, ("/", vp, "NP"), seed_term(author.tv_h("subject").sem))
        bob = Item(2, 3, "NP", seed_term(author.bob_h.sem))
        rule = kernel.unary["raise.np"]
        raised = Item(0, 1, rule.target, app(rule.builder, alice.meaning))

        ordinary = kernel.combine("ba", alice, kernel.combine("fa", review, bob))
        composed = kernel.combine("fa", kernel.combine("fc", raised, review), bob)
        expected = normalize(seed_term(author.actual.sem)).normal
        self.assertEqual(close(ordinary.meaning).normal, expected)
        self.assertEqual(close(composed.meaning).normal, expected)

        identity = Item(0, 1, ("\\", "NP", "NP"), seed_term(author.id_q.sem))
        leave = Item(1, 2, ("\\", "S[bare]", "NP"), seed_term(author.leave_h.sem))
        backward = kernel.combine("bc", identity, leave)
        self.assertEqual(close(app(backward.meaning, alice.meaning)).normal,
                         close(app(leave.meaning, alice.meaning)).normal)
        self.assertEqual(normalize(backward.meaning).normal, normalize(leave.meaning).normal)
        noun = Item(2, 3, "N", const("Researcher"))
        self.assertIsNone(kernel.combine("fa", review, noun))
        to_vp = ("\\", "S[to]", "NP")
        promise = Item(0, 1, ("/", ("/", vp, to_vp), "NP"),
                       seed_term(author.control_h("Promise", "s").sem))
        self.assertIsNone(kernel.combine("fa", promise,
                          Item(1, 3, to_vp, seed_term(author.to_leave_h.sem))))

    def test_countermodels_and_tense(self):
        separating = world(author.model)
        self.assertTrue(evaluate(seed_term(author.narrow), [separating]))
        self.assertFalse(evaluate(seed_term(author.wide), [separating]))
        for model, truth, hoisted in [(author.empty_events, True, False),
                                     (author.unrelated_event, True, True),
                                     (author.mixed_events, False, True)]:
            with self.subTest(events=model["events"]):
                sample = world(model)
                self.assertEqual(evaluate(seed_term(author.negative_h), [sample]), truth)
                self.assertEqual(evaluate(seed_term(author.hoisted), [sample]), hoisted)
                sample["facts"]["Past"] = [[e] for e in sample["events"]]
                self.assertEqual(evaluate(parsed_term("Alice did not leave"), [sample]), truth)
        nonpast = world(author.mixed_events)
        self.assertFalse(evaluate(seed_term(author.negative_h), [nonpast]))
        self.assertTrue(evaluate(parsed_term("Alice did not leave"), [nonpast]))
        partial = world(author.partial_leave)
        partial["facts"]["Past"] = [[e] for e in partial["events"]]
        for sentence, companion, expected in [
            ("Every researcher did not leave", author.q_above_not, False),
            ("Not every researcher left", author.not_above_q, True),
        ]:
            with self.subTest(sentence=sentence):
                self.assertEqual(evaluate(seed_term(companion), [partial]), expected)
                self.assertEqual(evaluate(parsed_term(sentence), [partial]), expected)

    def test_boxed_control_without_actual_leaving(self):
        model = {k: v for k, v in author.content_model.items() if k != "content_events"}
        sample = world(model)
        sample["facts"]["Content"] = [[e, (False,)] for e in author.content_model["content_events"]]
        for verb in ("promised", "persuaded"):
            with self.subTest(verb=verb):
                self.assertTrue(evaluate(parsed_term(f"Alice {verb} Bob to leave"), [sample]))
        self.assertFalse(sample["facts"]["Leave"])

    def test_manner_and_event_identity(self):
        manner = parsed_term("Alice reviewed Bob quickly")
        sample = world(author.quick_model)
        for quick_event in ("e1", "e2"):
            sample["facts"]["Quick"] = [[quick_event]]
            self.assertEqual(evaluate(manner, [sample]), quick_event == "e1")

        self.assertTrue(evaluate(normalize(seed_term(author.two_events)).normal,
                                 [world(author.one_event)]))
        with self.assertRaisesRegex(SemanticError, "unknown symbol"):
            normalize(seed_term(author.distinct_events))
