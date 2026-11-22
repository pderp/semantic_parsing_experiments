"""Supplementary semantic checks for the CCG design document; not a production parser."""
from dataclasses import dataclass
import json


@dataclass(frozen=True)
class Arrow:
    arg: object
    result: object


E, V, P, I = 'Entity', 'Event', 'Prop', 'Intension'
R = Arrow(E, P)
Q = Arrow(R, P)
VP = Arrow(Q, P)


def ft(*types):
    out = types[-1]
    for arg in reversed(types[:-1]):
        out = Arrow(arg, out)
    return out


SIG = {
    **{x: E for x in ('alice', 'bob', 'r1', 'r2', 'p1', 'p2')},
    'researcher': R, 'paper': R,
    **{x: ft(V, P) for x in ('Review', 'Leave', 'Promise', 'Persuade', 'Past', 'Quick')},
    **{x: ft(V, E, P) for x in ('Agent', 'Theme', 'Recipient')},
    'Content': ft(V, I, P), 'Box': ft(P, I),
    'And': ft(P, P, P), 'Imp': ft(P, P, P), 'Not': ft(P, P),
    'allE': ft(R, P), 'existsE': ft(R, P),
    'existsV': ft(ft(V, P), P), 'eqV': ft(V, V, P), 'Top': P,
}


@dataclass(frozen=True)
class Var:
    index: int


@dataclass(frozen=True)
class Const:
    name: str


@dataclass(frozen=True)
class Lam:
    typ: object
    body: object


@dataclass(frozen=True)
class App:
    fun: object
    arg: object


@dataclass(frozen=True)
class Named:
    name: str


@dataclass(frozen=True)
class NamedLam:
    name: str
    typ: object
    body: object


def app(fun, *args):
    if isinstance(fun, str):
        fun = Const(fun)
    for arg in args:
        fun = App(fun, arg)
    return fun


def lam(name, typ, body):
    return NamedLam(name, typ, body)


def resolve(term, env=()):
    """Named authoring convenience -> explicit de Bruijn binding; reject free names."""
    if isinstance(term, Named):
        return Var(env.index(term.name))
    if isinstance(term, NamedLam):
        return Lam(term.typ, resolve(term.body, (term.name,) + env))
    if isinstance(term, App):
        return App(resolve(term.fun, env), resolve(term.arg, env))
    if isinstance(term, Const):
        return term
    raise TypeError(term)


def infer(term, ctx=()):
    if isinstance(term, Var):
        assert 0 <= term.index < len(ctx), ('unbound', term)
        return ctx[term.index]
    if isinstance(term, Const):
        return SIG[term.name]
    if isinstance(term, Lam):
        return Arrow(term.typ, infer(term.body, (term.typ,) + ctx))
    if isinstance(term, App):
        f, a = infer(term.fun, ctx), infer(term.arg, ctx)
        assert isinstance(f, Arrow) and f.arg == a, ('bad application', f, a)
        return f.result
    raise TypeError(term)


def shift(term, amount, cutoff=0):
    if isinstance(term, Var):
        result = Var(term.index + amount) if term.index >= cutoff else term
        assert result.index >= 0
        return result
    if isinstance(term, Lam):
        return Lam(term.typ, shift(term.body, amount, cutoff + 1))
    if isinstance(term, App):
        return App(shift(term.fun, amount, cutoff), shift(term.arg, amount, cutoff))
    return term


def subst(term, index, value, depth=0):
    if isinstance(term, Var):
        return shift(value, depth) if term.index == index + depth else term
    if isinstance(term, Lam):
        return Lam(term.typ, subst(term.body, index, value, depth + 1))
    if isinstance(term, App):
        return App(subst(term.fun, index, value, depth), subst(term.arg, index, value, depth))
    return term


def norm(term):
    if isinstance(term, Lam):
        return Lam(term.typ, norm(term.body))
    if isinstance(term, App):
        f = norm(term.fun)
        if isinstance(f, Lam):
            return norm(shift(subst(f.body, 0, shift(term.arg, 1)), -1))
        return App(f, norm(term.arg))
    return term


def normalize(term):
    before = infer(term)
    out = norm(term)
    assert infer(out) == before, 'normalization changed type'
    return out


@dataclass(frozen=True)
class Slash:
    direction: str
    result: object
    arg: object


NP, N, SF, SB, ST = 'NP', 'N', 'S[finite]', 'S[bare]', 'S[to]'
F = lambda result, arg: Slash('/', result, arg)
B = lambda result, arg: Slash('\\', result, arg)
VF, VB, VT = B(SF, NP), B(SB, NP), B(ST, NP)


def tau(cat, sentence_type=P):
    if isinstance(cat, Slash):
        return Arrow(tau(cat.arg, sentence_type), tau(cat.result, sentence_type))
    return {NP: Q, N: R, SF: sentence_type, SB: sentence_type, ST: sentence_type}[cat]


@dataclass(frozen=True)
class Item:
    cat: object
    sem: object
    sentence_type: object = P

    def __post_init__(self):
        assert infer(self.sem) == tau(self.cat, self.sentence_type), ('category/semantics mismatch', self.cat)


def fa(left, right):
    assert left.sentence_type == right.sentence_type
    assert isinstance(left.cat, Slash) and left.cat.direction == '/' and left.cat.arg == right.cat
    return Item(left.cat.result, normalize(App(left.sem, right.sem)), left.sentence_type)


def ba(left, right):
    assert left.sentence_type == right.sentence_type
    assert isinstance(right.cat, Slash) and right.cat.direction == '\\' and right.cat.arg == left.cat
    return Item(right.cat.result, normalize(App(right.sem, left.sem)), left.sentence_type)


def compose(f, g, argtype):
    # Arguments are closed typed semantic programs. Shift also handles that invariant explicitly.
    return Lam(argtype, App(shift(f, 1), App(shift(g, 1), Var(0))))


def fc(left, right):
    assert left.sentence_type == right.sentence_type
    a, b = left.cat, right.cat
    assert isinstance(a, Slash) and isinstance(b, Slash) and a.direction == b.direction == '/'
    assert a.arg == b.result
    return Item(F(a.result, b.arg), normalize(compose(left.sem, right.sem, tau(b.arg, left.sentence_type))), left.sentence_type)


def bc(left, right):
    assert left.sentence_type == right.sentence_type
    a, b = left.cat, right.cat
    assert isinstance(a, Slash) and isinstance(b, Slash) and a.direction == b.direction == '\\'
    assert a.result == b.arg
    return Item(B(b.result, a.arg), normalize(compose(right.sem, left.sem, tau(a.arg, left.sentence_type))), left.sentence_type)


def raise_forward(np):
    assert np.cat == NP
    return Item(F(SF, VF), Lam(tau(VF, np.sentence_type), App(Var(0), shift(np.sem, 1))), np.sentence_type)


def conj(*parts):
    out = parts[-1]
    for p in reversed(parts[:-1]):
        out = app('And', p, out)
    return out


v = Named
c = Const
unit = lambda ent: lam('k', R, app(v('k'), ent))
alice = Item(NP, resolve(unit(c('alice'))))
bob = Item(NP, resolve(unit(c('bob'))))
researcher = Item(N, resolve(lam('x', E, app('researcher', v('x')))))
paper = Item(N, resolve(lam('x', E, app('paper', v('x')))))
every = Item(F(NP, N), resolve(lam('r', R, lam('k', R,
    app('allE', lam('x', E, app('Imp', app(v('r'), v('x')), app(v('k'), v('x')))))))))
a = Item(F(NP, N), resolve(lam('r', R, lam('k', R,
    app('existsE', lam('x', E, conj(app(v('r'), v('x')), app(v('k'), v('x')))))))))
every_researcher, a_paper = fa(every, researcher), fa(a, paper)


def review_body(s, o):
    return app('existsV', lam('e', V, conj(
        app('Review', v('e')), app('Agent', v('e'), s),
        app('Theme', v('e'), o), app('Past', v('e')))))


def tv(scope):
    core = review_body(v('s'), v('o'))
    if scope == 'subject':
        body = app(v('qs'), lam('s', E, app(v('qo'), lam('o', E, core))))
    else:
        body = app(v('qo'), lam('o', E, app(v('qs'), lam('s', E, core))))
    return Item(F(VF, NP), resolve(lam('qo', Q, lam('qs', Q, body))))


leave_named = lam('q', Q, app(v('q'), lam('x', E,
    app('existsV', lam('el', V, conj(app('Leave', v('el')), app('Agent', v('el'), v('x'))))))))
leave = Item(VB, resolve(leave_named))
to = Item(F(VT, VB), resolve(lam('vp', VP, v('vp'))))
to_leave = fa(to, leave)


def control(kind, controller):
    event = app('existsV', lam('e', V, conj(
        app(kind, v('e')), app('Agent', v('e'), v('s')),
        app('Recipient', v('e'), v('o')), app('Past', v('e')),
        app('Content', v('e'), app('Box', app(v('vp'), unit(v(controller))))))))
    body = app(v('qs'), lam('s', E, app(v('qo'), lam('o', E, event))))
    return Item(F(F(VF, VT), NP), resolve(lam('qo', Q, lam('vp', VP, lam('qs', Q, body)))))


def control_expected(kind, controller, subject_every=False, object_every=False):
    subj = v('s') if subject_every else c('alice')
    obj = v('o') if object_every else c('bob')
    target = subj if controller == 's' else obj
    inner = app('existsV', lam('el', V, conj(app('Leave', v('el')), app('Agent', v('el'), target))))
    body = app('existsV', lam('e', V, conj(app(kind, v('e')), app('Agent', v('e'), subj),
        app('Recipient', v('e'), obj), app('Past', v('e')), app('Content', v('e'), app('Box', inner)))))
    if object_every:
        body = app('allE', lam('o', E, app('Imp', app('researcher', v('o')), body)))
    if subject_every:
        body = app('allE', lam('s', E, app('Imp', app('researcher', v('s')), body)))
    return normalize(resolve(body))


def count_const(term, name):
    if isinstance(term, Const):
        return int(term.name == name)
    if isinstance(term, Lam):
        return count_const(term.body, name)
    if isinstance(term, App):
        return count_const(term.fun, name) + count_const(term.arg, name)
    return 0


@dataclass(frozen=True)
class Quoted:
    formula: object
    environment: tuple


def curried_relation(facts, arity, args=()):
    if len(args) == arity:
        return args in facts
    return lambda x: curried_relation(facts, arity, args + (x,))


def evaluate(term, model, env=()):
    if isinstance(term, Var):
        return env[term.index]
    if isinstance(term, Lam):
        return lambda x: evaluate(term.body, model, (x,) + env)
    if isinstance(term, App):
        if term.fun == Const('Box'):
            return Quoted(term.arg, env)  # Quotation is intentionally non-eager.
        return evaluate(term.fun, model, env)(evaluate(term.arg, model, env))
    name = term.name
    constants = {
        'Top': True,
        'And': lambda x: lambda y: x and y,
        'Imp': lambda x: lambda y: (not x) or y,
        'Not': lambda x: not x,
        'allE': lambda f: all(f(x) for x in model['entities']),
        'existsE': lambda f: any(f(x) for x in model['entities']),
        'existsV': lambda f: any(f(x) for x in model['events']),
        'eqV': lambda x: lambda y: x == y,
        # Uninterpreted content relation: does not assert/evaluate its boxed proposition.
        'Content': lambda e: lambda q: e in model.get('content_events', set()) and isinstance(q, Quoted),
    }
    if name in constants:
        return constants[name]
    if SIG[name] == E:
        return name
    arity, typ = 0, SIG[name]
    while isinstance(typ, Arrow):
        arity += 1
        typ = typ.result
    return curried_relation(model.get(name, set()), arity)


checks = []


def check(name, condition):
    assert condition, name
    checks.append(name)


def rejects(fn):
    try:
        fn()
    except (AssertionError, ValueError):
        return True
    return False


# Capture avoidance, category/semantic agreement, and the four binary combinators.
hygiene = resolve(lam('y', E, app(lam('x', E, lam('y', E, v('x'))), v('y'))))
check('de Bruijn beta reduction avoids capture under a shadowing binder', normalize(hygiene) == Lam(E, Lam(E, Var(1))))
check('unbound named semantic variable rejected', rejects(lambda: resolve(v('free'))))
check('entity cannot be used directly as an NP semantic value', rejects(lambda: Item(NP, c('alice'))))
actual = ba(alice, fa(tv('subject'), bob))
check('FA then BA gives Alice reviewed Bob with correct roles', actual.sem == normalize(resolve(review_body(c('alice'), c('bob')))))
check('FC with licensed forward raising preserves the same sentence meaning', fa(fc(raise_forward(alice), tv('subject')), bob).sem == actual.sem)
id_q = Item(B(NP, NP), resolve(lam('q', Q, v('q'))))
check('BC has the correct order f(g(x)) and semantic type', bc(id_q, leave).sem == normalize(leave.sem))
check('incompatible FA categories rejected', rejects(lambda: fa(tv('subject'), researcher)))

# Both local quantifier scope templates; beta-equivalent name cases merge.
narrow = ba(every_researcher, fa(tv('subject'), a_paper)).sem
wide = ba(every_researcher, fa(tv('object'), a_paper)).sem
expected_narrow = app('allE', lam('s', E, app('Imp', app('researcher', v('s')),
    app('existsE', lam('o', E, conj(app('paper', v('o')), review_body(v('s'), v('o'))))))))
expected_wide = app('existsE', lam('o', E, conj(app('paper', v('o')),
    app('allE', lam('s', E, app('Imp', app('researcher', v('s')), review_body(v('s'), v('o'))))))))
check('every researcher / a paper subject-wide normal form exact', narrow == normalize(resolve(expected_narrow)))
check('every researcher / a paper object-wide normal form exact', wide == normalize(resolve(expected_wide)))
check('two scope templates agree for proper names', ba(alice, fa(tv('object'), bob)).sem == actual.sem)
model = {
    'entities': ['r1', 'r2', 'p1', 'p2'], 'events': ['e1', 'e2'],
    'researcher': {('r1',), ('r2',)}, 'paper': {('p1',), ('p2',)},
    'Review': {('e1',), ('e2',)}, 'Past': {('e1',), ('e2',)},
    'Agent': {('e1', 'r1'), ('e2', 'r2')}, 'Theme': {('e1', 'p1'), ('e2', 'p2')},
}
check('finite model: each researcher has a paper, so subject-wide is true', evaluate(narrow, model) is True)
check('finite model: no shared paper, so object-wide is false', evaluate(wide, model) is False)

# Control argument order and identity, including quantifiers opened exactly once.
promised, persuaded = control('Promise', 's'), control('Persuade', 'o')
prom = ba(alice, fa(fa(promised, bob), to_leave)).sem
pers = ba(alice, fa(fa(persuaded, bob), to_leave)).sem
check('promise object-then-VP argument order and subject control exact', prom == control_expected('Promise', 's'))
check('persuade object-then-VP argument order and object control exact', pers == control_expected('Persuade', 'o'))
check('control verb rejects a VP in its NP argument slot', rejects(lambda: fa(promised, to_leave)))
prom_q = ba(every_researcher, fa(fa(promised, bob), to_leave)).sem
check('quantified control subject reference shared without requantification', prom_q == control_expected('Promise', 's', subject_every=True) and count_const(prom_q, 'allE') == 1)
pers_q = ba(alice, fa(fa(persuaded, every_researcher), to_leave)).sem
check('quantified controlled object reference shared without requantification', pers_q == control_expected('Persuade', 'o', object_every=True) and count_const(pers_q, 'allE') == 1)
content_model = {
    'entities': ['alice', 'bob'], 'events': ['e1'], 'Promise': {('e1',)}, 'Persuade': {('e1',)},
    'Agent': {('e1', 'alice')}, 'Recipient': {('e1', 'bob')}, 'Past': {('e1',)},
    'Leave': set(), 'content_events': {'e1'},
}
check('promise can hold when no leaving event exists', evaluate(prom, content_model) is True)
check('persuade can hold when no leaving event exists', evaluate(pers, content_model) is True)

# Negation must preserve the existential inside its scope.
negative = normalize(app('Not', ba(alice, leave).sem))
empty_events = {'entities': ['alice'], 'events': []}
hoisted = normalize(resolve(app('existsV', lam('e', V, app('Not', conj(app('Leave', v('e')), app('Agent', v('e'), c('alice'))))))))
check('negative event statement true with no event witness', evaluate(negative, empty_events) is True)
check('hoisting event existential across negation changes truth', evaluate(hoisted, empty_events) is False)
unrelated_event = {'entities': ['alice'], 'events': ['e'], 'Leave': set(), 'Agent': set()}
check('negative statement true with nonempty event domain but no leaving witness', evaluate(negative, unrelated_event) is True)
mixed_events = {'entities': ['alice'], 'events': ['leave_event', 'other_event'],
    'Leave': {('leave_event',)}, 'Agent': {('leave_event', 'alice')}}
check('existential hoisting also fails in a nonempty event-domain countermodel',
    evaluate(negative, mixed_events) is False and evaluate(hoisted, mixed_events) is True)

# Fresh binders do not entail distinct denotations; an explicit inequality does.
two_events = resolve(app('existsV', lam('e1', V, app('existsV', lam('e2', V,
    conj(app('Review', v('e1')), app('Leave', v('e2'))))))))
distinct_events = resolve(app('existsV', lam('e1', V, app('existsV', lam('e2', V,
    conj(app('Review', v('e1')), app('Leave', v('e2')), app('Not', app('eqV', v('e1'), v('e2')))))))))
one_event = {'entities': ['alice'], 'events': ['e'], 'Review': {('e',)}, 'Leave': {('e',)}}
check('two fresh event binders may denote the same event', evaluate(normalize(two_events), one_event) is True)
check('explicit event inequality forces distinct denotations', evaluate(normalize(distinct_events), one_event) is False)

# Separate H refinement: sentence values expose a scoped event continuation.
# The original S=Prop tests above remain intact; NP and N retain exactly their types.
K = ft(V, P)
H = ft(K, P)
VP_H = ft(Q, H)


def strip_top(term):
    if isinstance(term, Lam):
        return Lam(term.typ, strip_top(term.body))
    if isinstance(term, App):
        f, a0 = strip_top(term.fun), strip_top(term.arg)
        if isinstance(f, App) and f.fun == c('And'):
            if a0 == c('Top'):
                return f.arg
            if f.arg == c('Top'):
                return a0
        return App(f, a0)
    return term


def close_h(term):
    assert infer(term) == H
    out = strip_top(normalize(app(term, Lam(V, c('Top')))))
    assert infer(out) == P
    return out


def named_close(term):
    return app(term, lam('_ignored_event', V, c('Top')))


def h_item(old):
    return Item(old.cat, old.sem, H)  # Only NP/N items are reusable unchanged.


alice_h, bob_h = h_item(alice), h_item(bob)
every_researcher_h, a_paper_h = h_item(every_researcher), h_item(a_paper)


def tv_h(scope):
    core = app('existsV', lam('e', V, conj(app('Review', v('e')),
        app('Agent', v('e'), v('s')), app('Theme', v('e'), v('o')),
        app('Past', v('e')), app(v('k'), v('e')))))
    if scope == 'subject':
        body = app(v('qs'), lam('s', E, app(v('qo'), lam('o', E, core))))
    else:
        body = app(v('qo'), lam('o', E, app(v('qs'), lam('s', E, core))))
    return Item(F(VF, NP), resolve(lam('qo', Q, lam('qs', Q, lam('k', K, body)))), H)


leave_core_h = app('existsV', lam('el', V, conj(app('Leave', v('el')),
    app('Agent', v('el'), v('x')), app(v('k'), v('el')))))
leave_h = Item(VB, resolve(lam('q', Q, lam('k', K,
    app(v('q'), lam('x', E, leave_core_h))))), H)
to_h = Item(F(VT, VB), resolve(lam('vp', VP_H, v('vp'))), H)
to_leave_h = fa(to_h, leave_h)


def control_h(kind, controller):
    embedded = app('Box', named_close(app(v('vp'), unit(v(controller)))))
    core = app('existsV', lam('e', V, conj(app(kind, v('e')),
        app('Agent', v('e'), v('s')), app('Recipient', v('e'), v('o')),
        app('Past', v('e')), app('Content', v('e'), embedded), app(v('k'), v('e')))))
    body = app(v('qs'), lam('s', E, app(v('qo'), lam('o', E, core))))
    return Item(F(F(VF, VT), NP), resolve(lam('qo', Q, lam('vp', VP_H,
        lam('qs', Q, lam('k', K, body))))), H)


plain_h = ba(alice_h, fa(tv_h('subject'), bob_h)).sem
check('H: FA/BA, types and root closure recover baseline sentence exactly', close_h(plain_h) == actual.sem)
check('H: FC with licensed raising recovers baseline sentence', close_h(fa(fc(raise_forward(alice_h), tv_h('subject')), bob_h).sem) == actual.sem)
check('H: BC remains correctly typed', bc(h_item(id_q), leave_h).sem == normalize(leave_h.sem))
check('H: subject-wide quantified closure recovers baseline exactly', close_h(ba(every_researcher_h, fa(tv_h('subject'), a_paper_h)).sem) == narrow)
check('H: object-wide quantified closure recovers baseline exactly', close_h(ba(every_researcher_h, fa(tv_h('object'), a_paper_h)).sem) == wide)
prom_h = close_h(ba(alice_h, fa(fa(control_h('Promise', 's'), bob_h), to_leave_h)).sem)
pers_h = close_h(ba(alice_h, fa(fa(control_h('Persuade', 'o'), bob_h), to_leave_h)).sem)
check('H: subject control closes embedded event continuation inside Box', prom_h == prom)
check('H: object control closes embedded event continuation inside Box', pers_h == pers)
prom_q_h = close_h(ba(every_researcher_h, fa(fa(control_h('Promise', 's'), bob_h), to_leave_h)).sem)
check('H: quantified controller is still opened once', prom_q_h == prom_q and count_const(prom_q_h, 'allE') == 1)

# Manner adds a constraint to exactly the exported head-event continuation.
quick_k = lam('e', V, conj(app('Quick', v('e')), app(v('k'), v('e'))))
quick_sem = resolve(lam('vp', VP_H, lam('q', Q, lam('k', K, app(v('vp'), v('q'), quick_k)))))
quickly = Item(B(VF, VF), quick_sem, H)
quick_sentence = close_h(ba(alice_h, ba(fa(tv_h('subject'), bob_h), quickly)).sem)
quick_expected = normalize(resolve(app('existsV', lam('e', V, conj(app('Review', v('e')),
    app('Agent', v('e'), c('alice')), app('Theme', v('e'), c('bob')),
    app('Past', v('e')), app('Quick', v('e')))))))
check('H: manner constraint is inside the same event binder', quick_sentence == quick_expected)
quick_model = {'entities': ['alice', 'bob'], 'events': ['e1', 'e2'], 'Review': {('e1',)},
    'Agent': {('e1', 'alice')}, 'Theme': {('e1', 'bob')}, 'Past': {('e1',)}, 'Quick': {('e2',)}}
check('H: a different quick event cannot satisfy the modifier', evaluate(quick_sentence, quick_model) is False)
quick_model['Quick'] = {('e1',)}
check('H: same review event satisfies its manner modifier', evaluate(quick_sentence, quick_model) is True)

# Subject-wide VP negation keeps the event continuation under negation.
neg_body = app(v('q'), lam('s', E, app('Not', app(v('vp'), unit(v('s')), v('k')))))
neg_h = Item(F(VB, VB), resolve(lam('vp', VP_H, lam('q', Q, lam('k', K, neg_body)))), H)
negative_h = close_h(ba(alice_h, fa(neg_h, leave_h)).sem)
check('H: negation preserves its event existential and root closure', negative_h == negative)
check('H: negative statement needs no actual head-event witness', evaluate(negative_h, empty_events) is True)
q_above_not = close_h(ba(every_researcher_h, fa(neg_h, leave_h)).sem)
not_above_q = normalize(app('Not', close_h(ba(every_researcher_h, leave_h).sem)))
partial_leave = {'entities': ['r1', 'r2'], 'events': ['el'], 'researcher': {('r1',), ('r2',)},
    'Leave': {('el',)}, 'Agent': {('el', 'r1')}}
check('H: every-not and not-every remain distinct scope readings',
    evaluate(q_above_not, partial_leave) is False and evaluate(not_above_q, partial_leave) is True)
print(json.dumps({'status': 'pass', 'checks_passed': len(checks), 'checks': checks}, indent=2))
