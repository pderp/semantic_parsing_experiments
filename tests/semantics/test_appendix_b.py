"""Independent replacement cases derived from the design PDF, Appendix B, Table 8."""
import json
import random
import unittest

from src.semantics import (
    E, V, I, P, K, Q, ROOT, SemanticError, app, arrow, call, canonical, close, const,
    lam, normalize, parse_type, reading_set, spine, typeof, var,
)
from spike import scope_spike as spike


def both(*parts):
    result = const("Top")
    for part in reversed(parts):
        result = call("And", part, result)
    return result


def event(body):
    return call("ExistsV", lam(V, body))


def evaluate(term, worlds, index=0, env=()):
    """Small countermodels. Box is a truth vector at the same outer assignment."""
    world = worlds[index]
    head, args = spine(term)
    if head[0] == "var":
        return env[head[1]]
    name = head[1]
    def ev(node):
        return evaluate(node, worlds, index, env)
    if name == "Top":
        return True
    if name in ("ExistsE", "ForallE", "ExistsV"):
        domain = world["events" if name == "ExistsV" else "entities"]
        values = (evaluate(args[0][2], worlds, index, (item,) + env) for item in domain)
        return all(values) if name == "ForallE" else any(values)
    if name == "Box":
        return tuple(evaluate(args[0], worlds, i, env) for i in range(len(worlds)))
    if name == "Not":
        return not ev(args[0])
    if name == "Implies":
        return not ev(args[0]) or ev(args[1])
    if name == "And":
        return ev(args[0]) and ev(args[1])
    if not args:
        return name
    return [ev(arg) for arg in args] in world["facts"].get(name, [])


def controller_event(frame, controller):
    embedded = event(both(call("Leave", var(0)), call("Agent", var(0), controller)))
    # This helper is called under a matrix event and an outer subject binder.
    return event(both(call(frame, var(0)), call("Agent", var(0), var(1)),
                      call("Recipient", var(0), const("bob")), call("Past", var(0)),
                      call("Content", var(0), call("Box", embedded))))


class AppendixBReplacement(unittest.TestCase):
    def test_binding_types_application_and_licensed_raising_shape(self):
        term = app(lam(E, lam(V, var(1))), var(0))
        self.assertEqual(normalize(term, (E,)).normal, lam(V, var(1)))
        raised = lam(arrow(E, P), app(var(0), const("alice")))
        self.assertEqual(typeof(raised), Q)
        self.assertEqual(normalize(app(raised, const("Researcher"))).normal,
                         call("Researcher", const("alice")))
        for invalid in [var(0), var(-1), var(True), call("Leave", const("alice")),
                        call("Content", const("alice"), const("Top")), const("Unlicensed")]:
            with self.subTest(invalid=invalid), self.assertRaises(SemanticError):
                normalize(invalid)

    def test_mixed_quantifier_scope_against_public_bytes_and_worlds(self):
        expected = json.loads((ROOT / "spike/output.json").read_text())["readings"]
        def review(subject, obj):
            return event(both(call("Review", var(0)), call("Agent", var(0), var(subject)),
                              call("Past", var(0)), call("Theme", var(0), var(obj))))
        def researcher(body):
            return call("ForallE", lam(E, call("Implies", call("Researcher", var(0)), body)))
        def paper(body):
            return call("ExistsE", lam(E, both(call("Paper", var(0)), body)))
        forms = [normalize(researcher(paper(review(2, 1)))).normal,
                 normalize(paper(researcher(review(1, 2)))).normal]
        self.assertEqual(reading_set(forms + forms),
                         json.dumps(sorted(item["normalized"] for item in expected),
                                    separators=(",", ":")).encode("ascii"))
        self.assertEqual(sorted(evaluate(f, [spike.SEPARATING_WORLD]) for f in forms), [False, True])
        self.assertTrue(all(evaluate(f, [spike.SHARED_PAPER_WORLD]) for f in forms))

    def test_quantified_controller_and_argument_order(self):
        subject = call("ForallE", lam(E, call("Implies", call("Researcher", var(0)),
                                              controller_event("Promise", var(2)))))
        text = canonical(normalize(subject).normal)
        self.assertIn('\n' + text + '\n', (ROOT / "spec/contract.md").read_text())
        recipient = app(lam(E, controller_event("Persuade", const("bob"))), const("alice"))
        self.assertIn("(Box (ExistsV (lam V (And (Agent #0 bob) (Leave #0)))))",
                      canonical(normalize(recipient).normal))
        self.assertNotEqual(call("Agent", var(0), const("bob")), call("Agent", var(0), const("alice")))

    def test_boxed_control_can_hold_without_actual_leaving(self):
        for frame, controller in [("Promise", const("alice")), ("Persuade", const("bob"))]:
            term = app(lam(E, controller_event(frame, controller)), const("alice"))
            world = {"events": ["v"], "entities": ["alice", "bob"],
                     "facts": {frame: [["v"]], "Past": [["v"]], "Agent": [["v", "alice"]],
                               "Recipient": [["v", "bob"]], "Content": [["v", (False,)]]}}
            self.assertTrue(evaluate(normalize(term).normal, [world]))
            self.assertFalse(evaluate(event(call("Leave", var(0))), [world]))
        self.assertEqual(typeof(call("Box", const("Top"))), I)

    def test_negation_distinguishes_hoisted_event(self):
        negated = call("Not", event(call("Leave", var(0))))
        hoisted = event(call("Not", call("Leave", var(0))))
        empty = {"events": [], "entities": [], "facts": {}}
        self.assertTrue(evaluate(normalize(negated).normal, [empty]))
        self.assertFalse(evaluate(normalize(hoisted).normal, [empty]))

    def test_fresh_binders_do_not_require_distinct_events(self):
        term = event(event(both(call("Review", var(1)), call("Past", var(0)))))
        world = {"events": ["v"], "entities": [], "facts": {"Review": [["v"]], "Past": [["v"]]}}
        self.assertTrue(evaluate(normalize(term).normal, [world]))
        self.assertFalse(any(x != y for x in world["events"] for y in world["events"]))
        with self.assertRaisesRegex(SemanticError, "unknown symbol"):
            typeof(event(event(call("UnequalV", var(1), var(0)))))

    def test_head_continuation_closure_tense_and_manner(self):
        clause = lam(K, event(both(call("Leave", var(0)), call("Past", var(0)),
                                   call("Agent", var(0), const("alice")), app(var(1), var(0)))))
        plain = close(clause)
        self.assertEqual(canonical(plain.normal),
                         "(ExistsV (lam V (And (Agent #0 alice) (And (Leave #0) (Past #0)))))")
        manner = normalize(app(clause, const("Quick"))).normal
        world = {"events": ["v", "w"], "entities": ["alice"], "facts": {
            "Leave": [["v"]], "Past": [["v"]], "Agent": [["v", "alice"]], "Quick": [["w"]]}}
        self.assertTrue(evaluate(plain.normal, [world]))
        self.assertFalse(evaluate(manner, [world]))
        world["facts"]["Quick"].append(["v"])
        self.assertTrue(evaluate(manner, [world]))


class NormalForm(unittest.TestCase):
    def test_full_conjunction_and_replayable_trace(self):
        p = call("Paper", const("alice"))
        q = call("Researcher", const("bob"))
        raw = app(lam(P, both(q, both(var(0), q))), p)
        result = normalize(raw)
        self.assertEqual(result.normal, call("And", p, call("And", q, q)))
        def replace(term, path, before, after):
            if not path:
                self.assertEqual(term, before)
                return after
            i = path[0]
            return (*term[:i], replace(term[i], path[1:], before, after), *term[i+1:])
        replay = result.raw
        for step in result.trace:
            replay = replace(replay, step.path, step.before, step.after)
        self.assertEqual(replay, result.normal)
        self.assertEqual(normalize(result.normal).trace, ())

    def test_ontology_signatures_and_closed_readings(self):
        self.assertEqual(parse_type("(E -> P) -> P"), Q)
        self.assertEqual(typeof(const("Content")), arrow(V, arrow(I, P)))
        self.assertEqual(reading_set([]), b"[]")
        with self.assertRaises(SemanticError):
            reading_set([const("alice")])
        for source in ("P E", "Unknown", "(E -> V", "P ->"):
            with self.assertRaises(ValueError):
                parse_type(source)

    def test_registered_stress_binding_and_idempotence(self):
        config = json.loads((ROOT / "configs/pilot.yaml").read_text())["semantic_gates"]
        rng = random.Random(config["stress_seed_proposal"])
        for _ in range(config["well_typed_stress_cases"]):
            outer = tuple(rng.choice((E, V, P, I)) for _ in range(rng.randint(1, 7)))
            chosen = rng.randrange(len(outer))
            sort = outer[chosen]
            inner = [rng.choice((E, V, P, I)) for _ in range(rng.randint(0, 6))]
            body, expected = var(len(inner)), var(chosen + len(inner))
            for binder in reversed(inner):
                body, expected = lam(binder, body), lam(binder, expected)
            raw = app(lam(sort, body), var(chosen))
            for _ in range(rng.randrange(4)):
                raw = app(lam(typeof(raw, outer), var(0)), raw)
            normal = normalize(raw, outer).normal
            self.assertEqual(normal, expected)
            self.assertEqual(normalize(normal, outer).normal, normal)
            self.assertEqual(typeof(normal, outer), typeof(raw, outer))
