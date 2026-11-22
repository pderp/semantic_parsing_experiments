"""Regenerate the public seed-1.1 finite bank from its declared interpretation."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "fixtures/world_bank_v2.json"
NAMES = {"alice": 0, "cara": 0, "gia": 0, "bob": 1, "dan": 1, "hugo": 1,
         "ava": 2, "eva": 2, "ben": 3, "finn": 3}
SEED = 20261119


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=True, separators=(",", ":"))


def set_fact(facts, name, slot, entity=None):
    bit = slot if entity is None else 4 * slot + entity
    facts[name] = facts.get(name, 0) | (1 << bit)


def exhaustive(n):
    facts = {"Researcher": 3, "Paper": 12, "Past": 3}
    for event in range(2):
        for i, (relation, arg) in enumerate([("Review", None), ("Agent", event), ("Theme", event + 2)]):
            if n & (1 << (event * 3 + i)):
                set_fact(facts, relation, event, arg)
    return facts, [[], [], []]


def contrast(n):
    facts, content = {"Researcher": 3, "Paper": 12}, [[], [], []]
    if n < 4:
        roles = [[(0, 1)], [(1, 0)], [(0, 2), (1, 3)], [(0, 2), (1, 2)]][n]
        for i, (agent, theme) in enumerate(roles):
            for name, entity in [("Review", None), ("Past", None), ("Agent", agent), ("Theme", theme)]:
                set_fact(facts, name, i, entity)
        if n == 2:
            set_fact(facts, "Past", 2)
    elif 5 <= n <= 9:
        set_fact(facts, "Leave", 0)
        set_fact(facts, "Agent", 0, int(n == 6))
        if n != 9:
            set_fact(facts, "Past", 0)
        if n in (7, 8):
            set_fact(facts, "Quick", int(n == 8))
    elif n >= 10:
        promise = n in (10, 12, 14)
        for i in range(2 if n >= 14 else 1):
            agent = i if n == 14 else 0
            recipient = i if n == 15 else 1
            for name, entity in [("Promise" if promise else "Persuade", None), ("Past", None),
                                 ("Agent", agent), ("Recipient", recipient)]:
                set_fact(facts, name, i, entity)
            controller = agent if promise else recipient
            if n in (12, 13):
                controller = 1 - controller
            content[i].append(("Leave", controller, None, False))
        if n == 10:
            set_fact(facts, "Quick", 0)
    return facts, content


def draw(attempt, label):
    raw = f"{SEED}/{attempt}/{label}".encode("ascii")
    return int.from_bytes(hashlib.sha256(raw).digest(), "little")


def sampled(attempt, predicates, payload_count):
    facts = {}
    for name, sorts in sorted(predicates.items()):
        if name == "Content":
            continue
        width = {("E",): 4, ("V",): 3, ("V", "E"): 12}[tuple(sorts)]
        mask = draw(attempt, name) & ((1 << width) - 1)
        if mask:
            facts[name] = mask
    content = []
    width = (payload_count + 7) // 8
    for event in range(3):
        key = f"{SEED}/content-v2/{attempt}/{event}".encode("ascii")
        bits = int.from_bytes(hashlib.shake_256(key).digest(width), "little")
        content.append(bits & ((1 << payload_count) - 1))
    return facts, content


def scope_stratum(facts, index, verbs, nouns):
    """Condition one seeded world on a diagonal or a complete two-slot relation."""
    # Choose one of six unordered pairs, independent of any evaluation data.
    pairs = [(x, y) for x in range(4) for y in range(x + 1, 4)]
    slots = pairs[draw(0, "scope/slots") % len(pairs)]
    # Give every restrictor the same two members in this stratum. This also
    # handles identical restrictors and both orders of the mixed determiners.
    members = (1 << slots[0]) | (1 << slots[1])
    facts.update({noun: members for noun in nouns})
    facts.update({verb: 3 for verb in verbs})
    facts["Past"] = facts["Quick"] = 3
    facts["Agent"] = (1 << slots[0]) | (1 << (4 + slots[1]))
    facts["Theme"] = facts["Agent"] if index == 0 else members | (members << 4)


def matches(facts, description):
    verb, agent, theme, quick = description
    active = facts.get(verb, 0)
    if quick:
        active &= facts.get("Quick", 0)
    themes = 0
    for event in range(3):
        if active & (1 << event) and facts.get("Agent", 0) & (1 << (4 * event + agent)):
            if theme is None:
                return True
            themes |= (facts.get("Theme", 0) >> (4 * event)) & 15
    if theme is None:
        return False
    if isinstance(theme, int):
        return bool(themes & (1 << theme))
    quantifier, noun = theme
    restrictor = facts.get(noun, 0)
    if quantifier == "every":
        return (restrictor & themes) == restrictor
    return bool(restrictor & themes)


def payload_catalog(ontology):
    catalog = []
    quantified = [(q, noun) for q in ("a", "every") for noun in sorted(ontology["nouns"].values())]
    for frame in sorted(ontology["frames"].values(), key=lambda f: f["predicate"]):
        kind = frame["construction"]
        if kind in ("intransitive", "transitive"):
            themes = [None] if kind == "intransitive" else [*range(4), *quantified]
            for agent in range(4):
                for theme in themes:
                    for quick in (False, True):
                        catalog.append((frame["predicate"], agent, theme, quick))
    return catalog


def control_contrasts(designs, index):
    # In each designated world only one matrix event has the required named
    # roles. Condition four payload memberships at that event, leaving all
    # other memberships and the original extensional draw intact.
    probes = [index[("Review", slot, (quant, "Paper"), False)]
              for slot in (0, 1) for quant in ("a", "every")]
    clear = sum(1 << i for i in probes)
    used = set()
    for frame in ("Promise", "Persuade"):
        n = 0
        for w in range(80, len(designs)):
            facts, masks = designs[w]
            active = facts.get(frame, 0) & facts.get("Past", 0)
            events = [v for v in range(3) if active & (1 << v)
                      and facts.get("Agent", 0) & (1 << (4*v))
                      and facts.get("Recipient", 0) & (2 << (4*v))]
            if w in used or len(events) != 1:
                continue
            event, = events
            masks[event] = (masks[event] & ~clear) | (1 << probes[n])
            used.add(w)
            n += 1
            if n == len(probes):
                break
        if n != len(probes):
            raise ValueError(f"missing quantified-object contrasts for {frame}")


def build():
    raw = (ROOT / "spec/ontology.yaml").read_bytes()
    ontology = json.loads(raw)
    if ontology["version"] != "seed-1.1" or set(ontology["names"]) != set(NAMES):
        raise ValueError("bank requires the seed-1.1 name interpretation")
    catalog = payload_catalog(ontology)
    index = {d: i for i, d in enumerate(catalog)}
    designs = []
    for i in range(80):
        facts, content = exhaustive(i) if i < 64 else contrast(i - 64)
        if i in (78, 79):  # H14/H15: content shared with the bound matrix participant.
            quant = "a" if i == 78 else "every"
            for event in range(2):
                content[event].append(("Review", event, (quant, "Paper"), False))
        masks = [sum(1 << index[d] for d in ds) for ds in content]
        designs.append((facts, masks))
    verbs = sorted(f["predicate"] for f in ontology["frames"].values() if f["construction"] == "transitive")
    strata = 0
    seen = {canonical(f) for f, _ in designs}
    # Contrast pairs can deliberately have the same extensional facts and different content.
    attempt = 0
    while len(designs) < 256:
        facts, content = sampled(attempt, ontology["predicates"], len(catalog))
        attempt += 1
        condition = strata < 2 and not facts.get("Past") and not facts.get("Quick")
        if condition:
            scope_stratum(facts, strata, verbs, ontology["nouns"].values())
        key = canonical(facts)
        if key not in seen:
            seen.add(key)
            designs.append((facts, content))
            strata += int(condition)
    if strata != 2:
        raise ValueError("two scope strata required")
    control_contrasts(designs, index)
    vectors = [sum(1 << w for w, (facts, _) in enumerate(designs) if matches(facts, d)) for d in catalog]
    if len(vectors) != 1440 or len(set(vectors)) != len(vectors) or {0, (1 << 256) - 1}.intersection(vectors):
        raise ValueError("expected 1,440 distinct, nonconstant payload vectors")
    coverage = 0
    width = (len(vectors) + 3) // 4
    worlds = []
    for i, (facts, masks) in enumerate(designs):
        for mask in masks:
            coverage |= mask
        name = f"E{i:02}" if i < 64 else (f"H{i-64:02}" if i < 80 else f"S{i-80:03}")
        worlds.append({"id": name, "facts": facts, "content": [format(mask, f"0{width}x") for mask in masks]})
    if coverage != (1 << len(vectors)) - 1:
        raise ValueError("a licensed payload is absent from every event's content")
    if len({canonical([w["facts"], w["content"]]) for w in worlds}) != 256:
        raise ValueError("duplicate world in bank")
    return {"format": "seed-world-bank-v2", "ontology_sha256": hashlib.sha256(raw).hexdigest(),
            "names": NAMES, "seed": SEED, "content_vectors": [format(v, "064x") for v in vectors],
            "worlds": worlds}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    raw = (canonical(build()) + "\n").encode("ascii")
    if args.check:
        if OUTPUT.read_bytes() != raw:
            raise SystemExit("bank differs from its generator")
    else:
        OUTPUT.write_bytes(raw)
    print(hashlib.sha256(raw).hexdigest())


if __name__ == "__main__":
    main()
