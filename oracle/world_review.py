#!/usr/bin/env python3
"""Design-review measurements for the world bank (inbox_v4), by ClaudeOracle.

Uses my own seed-1.1 analyser for readings and my own evaluator for truth.
Prints facts only; the judgement is in STATUS.md.   python3 world_review.py
"""
import collections
import itertools
import json
import random
import re

import oracle_v11 as X
import world_eval as WE
import selftest_v11 as T

ONT = X.load_ontology()
FULL = X.make_grammar()
bank_doc = json.loads((WE.INBOX / "world_bank_v1.json").read_text())
B = WE.Bank(bank_doc, ONT)
NW = len(B.worlds)
ALL = (1 << NW) - 1


def signature(reading):
    tree = WE.parse(reading)
    v = 0
    for w in range(NW):
        if B.holds(tree, w):
            v |= 1 << w
    return v


def dealias(reading):
    """Replace each name by its slot, so alias-equivalent readings become equal strings."""
    return re.sub(r"\b(%s)\b" % "|".join(B.names), lambda m: "@%d" % B.names[m.group(1)], reading)


def main():
    # 1. bank shape
    kinds = collections.Counter(w["id"][0] for w in B.worlds)
    print("worlds by id prefix:", dict(kinds))
    classes = collections.defaultdict(list)
    for n, s in sorted(B.names.items()):
        classes[s].append(n)
    print("name aliasing:", dict(classes))
    nonzero = collections.Counter()
    for w in B.worlds:
        for p, v in w["facts"].items():
            nonzero[p] += bool(v)
    never = sorted(set(ONT["predicates"]) - set(nonzero) - {"Content"})
    print("predicates with a fact in no world:", never)
    print("worlds with a non-empty content list: %d" % sum(any(c) for w in B.worlds for c in [w["content"]]))

    # 2. embedded contents: are their vectors distinct, and which occur in the bank?
    strings = collections.Counter(h for w in B.worlds for c in w["content"] for h in c)
    frames = ONT["frames"].values()
    ivs = [f["predicate"] for f in frames if f["construction"] == "intransitive"]
    tvs = [f["predicate"] for f in frames if f["construction"] == "transitive"]
    nouns = sorted(set(ONT["nouns"].values()))
    contents = {}  # label -> vector

    def vec(text, env):
        return B.box_vector(WE.parse(text), env)

    for c in range(4):
        for q in ("", " (Quick #0)"):
            for p in ivs:
                inner = "(And (Agent #0 #1) (And (%s #0)%s))" % (p, q) if q else "(And (Agent #0 #1) (%s #0))" % p
                contents[("iv", p, bool(q), c)] = vec("(ExistsV (lam V %s))" % inner.replace(")%s" % q, ")" + q), (("E", c),))
            for p in tvs:
                tail = "(And (%s #0) (And (Quick #0) (Theme #0 #2)))" % p if q else "(And (%s #0) (Theme #0 #2))" % p
                ev = "(ExistsV (lam V (And (Agent #0 #1) %s)))" % tail          # #1 controller, #2 object
                for o in range(4):
                    contents[("tv-unit", p, bool(q), c, o)] = vec(ev, (("E", c), ("E", o)))
                ev2 = "(ExistsV (lam V (And (Agent #0 #2) %s)))" % tail.replace("#2", "#1")  # #1 object, #2 controller
                for n in nouns:
                    contents[("tv-every", p, bool(q), c, n)] = vec(
                        "(ForallE (lam E (Implies (%s #0) %s)))" % (n, ev2), (("E", c),))
                    contents[("tv-a", p, bool(q), c, n)] = vec(
                        "(ExistsE (lam E (And %s (%s #0))))" % (ev2, n), (("E", c),))
    by_vec = collections.defaultdict(list)
    for label, v in contents.items():
        by_vec[v].append(label)
    coll = [ls for ls in by_vec.values() if len(ls) > 1]
    print("licensed embedded contents (by controller slot): %d, distinct vectors: %d, colliding groups: %d"
          % (len(contents), len(by_vec), len(coll)))
    for ls in coll[:6]:
        print("   collision:", ls[:4], "..." if len(ls) > 4 else "")
    present = collections.Counter()
    total = collections.Counter()
    for label, v in contents.items():
        total[label[0]] += 1
        present[label[0]] += WE.hexvec(v) in strings
    for k in total:
        print("   content kind %-9s: %4d of %4d vectors occur in some world's content list" % (k, present[k], total[k]))
    known = {WE.hexvec(v) for v in contents.values()}
    print("   bank content strings: %d distinct, %d explained by a licensed content" % (len(strings), sum(h in known for h in strings)))
    const = sum(1 for v in by_vec if v in (0, ALL))
    print("   content vectors that are constant across the bank: %d" % const)

    # 3. discrimination on sampled licensed sentences
    rng = random.Random(2026112220)
    right = lambda noun: X.article_for(ONT, noun)
    readings = {}       # reading -> signature
    amb_min = []
    amb_same = 0
    n_sent = 0
    by_family = collections.Counter()
    while n_sent < 4000:
        toks = T.random_tokens(rng, right)
        r = X.analyse(" ".join(toks), FULL, ONT)
        if not r["witnesses"]:
            continue
        n_sent += 1
        sigs = []
        for rd in r["readings"]:
            if rd not in readings:
                readings[rd] = signature(rd)
            sigs.append(readings[rd])
        if len(sigs) == 2:
            d = bin(sigs[0] ^ sigs[1]).count("1")
            amb_min.append(d)
            amb_same += d == 0
    print("sampled licensed sentences: %d, distinct readings: %d" % (n_sent, len(readings)))
    if amb_min:
        amb_min.sort()
        print("two-reading sentences: %d; worlds separating the two readings: min %d, median %d; "
              "not separated by any world: %d" % (len(amb_min), amb_min[0], amb_min[len(amb_min) // 2], amb_same))
    const = [rd for rd, s in readings.items() if s in (0, ALL)]
    kind = collections.Counter("control" if "Content" in rd else "other" for rd in const)
    print("readings with the same truth value in all 256 worlds: %d of %d %s"
          % (len(const), len(readings), dict(kind)))
    ctrl = [rd for rd in readings if "Content" in rd]
    print("   control readings sampled: %d, constant: %d" % (len(ctrl), kind["control"]))
    groups = collections.defaultdict(list)
    for rd, s in readings.items():
        groups[s].append(rd)
    alias_only = other = 0
    examples = []
    for s, rds in groups.items():
        if len(rds) < 2:
            continue
        if len({dealias(rd) for rd in rds}) == 1:
            alias_only += 1
        else:
            other += 1
            if s not in (0, ALL) and len(examples) < 4:
                examples.append(rds[:2])
    print("signature classes holding 2+ distinct readings: %d explained purely by name aliasing, %d not"
          % (alias_only, other))
    nonconst_other = sum(1 for s, rds in groups.items()
                         if len(rds) > 1 and s not in (0, ALL) and len({dealias(rd) for rd in rds}) > 1)
    print("   of the unexplained classes, %d are non-constant signatures" % nonconst_other)
    for a, b in examples:
        print("   e.g.\n     %s\n     %s" % (a, b))


if __name__ == "__main__":
    main()


def collisions_detail():
    """Classify bank-indistinguishable reading pairs: control vs not; and for the
    non-control ones, whether fresh random dense worlds separate them."""
    rng = random.Random(2026112220)
    right = lambda noun: X.article_for(ONT, noun)
    readings, n = {}, 0
    while n < 4000:
        toks = T.random_tokens(rng, right)
        r = X.analyse(" ".join(toks), FULL, ONT)
        if r["witnesses"]:
            n += 1
            for rd in r["readings"]:
                readings.setdefault(rd, None)
    for rd in readings:
        readings[rd] = signature(rd)
    groups = collections.defaultdict(list)
    for rd, s in readings.items():
        groups[s].append(rd)
    # fresh dense random worlds (no content): 2 x 256
    rr = random.Random(7)
    fresh = []
    for _ in range(2):
        worlds = []
        for i in range(256):
            facts = {}
            for p, sig in ONT["predicates"].items():
                if p == "Content":
                    continue
                bits = 12 if len(sig) == 2 else (4 if sig == ["E"] else 3)
                facts[p] = rr.getrandbits(bits) | (rr.getrandbits(bits) if rr.random() < 0.5 else 0)
            worlds.append({"id": "R%03d" % i, "facts": facts, "content": [[], [], []]})
        fresh.append(WE.Bank({"worlds": worlds, "names": B.names}, ONT))

    def fresh_sig(rd):
        tree = WE.parse(rd)
        return tuple(b.holds(tree, w) for b in fresh for w in range(256))

    ctrl_classes = plain_equiv = plain_bank_only = 0
    ctrl_const = 0
    shown = 0
    for s, rds in groups.items():
        forms = {dealias(rd) for rd in rds}
        if len(forms) < 2:
            continue
        if any("Content" in rd for rd in rds):
            ctrl_classes += 1
            ctrl_const += s in (0, ALL)
            continue
        fs = {fresh_sig(rd) for rd in rds}
        if len(fs) == 1:
            plain_equiv += 1
        else:
            plain_bank_only += 1
            if shown < 3:
                shown += 1
                print("   bank cannot separate (non-control):\n     %s\n     %s" % (rds[0], rds[1]))
    print("unexplained classes: %d involve control (%d constant), %d are non-control and also agree on 512 "
          "fresh random worlds (logical equivalents such as exists-not / not-every), %d are non-control and "
          "separated by fresh worlds (bank gap)" % (ctrl_classes, ctrl_const, plain_equiv, plain_bank_only))
    # how many control readings are separated from every other control reading?
    ctrl = [rd for rd in readings if "Content" in rd]
    quant_obj = [rd for rd in ctrl if re.search(r"Box \((ForallE|ExistsE)", rd)]
    const_q = sum(readings[rd] in (0, ALL) for rd in quant_obj)
    print("control readings: %d; with a quantified embedded object: %d, of which constant across the bank: %d"
          % (len(ctrl), len(quant_obj), const_q))
    uniq = sum(1 for rd in ctrl if len({dealias(x) for x in groups[readings[rd]]}) == 1)
    print("control readings whose signature is shared only with alias variants: %d of %d" % (uniq, len(ctrl)))


if __name__ == "__main__":
    print("--- collision detail")
    collisions_detail()
