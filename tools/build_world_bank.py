"""Regenerate the public seed-1.1 finite bank from its declared interpretation."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "fixtures/world_bank_v1.json"
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


def sampled(attempt, predicates, catalog):
    facts = {}
    for name, sorts in sorted(predicates.items()):
        if name == "Content":
            continue
        width = {("E",): 4, ("V",): 3, ("V", "E"): 12}[tuple(sorts)]
        mask = draw(attempt, name) & ((1 << width) - 1)
        if mask:
            facts[name] = mask
    content = []
    for event in range(3):
        # Two independent draws with replacement from the pinned finite catalog.
        ids = {draw(attempt, f"content/{event}/{i}") % len(catalog) for i in range(2)}
        content.append([catalog[j] for j in sorted(ids)])
    return facts, content


def matches(facts, description):
    verb, agent, theme, quick = description
    for event in range(3):
        bit = 1 << event
        if not (facts.get(verb, 0) & bit and facts.get("Agent", 0) & (1 << (4 * event + agent))):
            continue
        if theme is not None and not facts.get("Theme", 0) & (1 << (4 * event + theme)):
            continue
        if not quick or facts.get("Quick", 0) & bit:
            return True
    return False


def build():
    raw = (ROOT / "spec/ontology.yaml").read_bytes()
    ontology = json.loads(raw)
    if ontology["version"] != "seed-1.1" or set(ontology["names"]) != set(NAMES):
        raise ValueError("bank requires the seed-1.1 name interpretation")
    catalog = []
    for frame in sorted(ontology["frames"].values(), key=lambda f: f["predicate"]):
        kind = frame["construction"]
        if kind in ("intransitive", "transitive"):
            for agent in range(4):
                for theme in ([None] if kind == "intransitive" else range(4)):
                    for quick in (False, True):
                        catalog.append((frame["predicate"], agent, theme, quick))
    designs = [exhaustive(n) for n in range(64)] + [contrast(n) for n in range(16)]
    seen = {canonical(f) for f, _ in designs}
    # Contrast pairs can deliberately have the same extensional facts and different content.
    attempt = 0
    while len(designs) < 256:
        facts, content = sampled(attempt, ontology["predicates"], catalog)
        attempt += 1
        key = canonical(facts)
        if key not in seen:
            seen.add(key)
            designs.append((facts, content))
    vectors = {d: format(sum(1 << w for w, (facts, _) in enumerate(designs) if matches(facts, d)), "064x")
               for d in catalog}
    worlds = []
    for i, (facts, content) in enumerate(designs):
        name = f"E{i:02}" if i < 64 else (f"H{i-64:02}" if i < 80 else f"S{i-80:03}")
        worlds.append({"id": name, "facts": facts, "content": [sorted({vectors[d] for d in ds}) for ds in content]})
    if len({canonical([w["facts"], w["content"]]) for w in worlds}) != 256:
        raise ValueError("duplicate world in bank")
    return {"format": "seed-world-bank-v1", "ontology_sha256": hashlib.sha256(raw).hexdigest(),
            "names": NAMES, "seed": SEED, "worlds": worlds}


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
