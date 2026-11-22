"""Measure scope visibility on the public variants and the complete transitive noun grid."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.reference import parse
from src.semantics.world_bank import BANK_FILE, FULL, WorldBank
from tests.reference.test_seed import public_variants


def variant_counts(bank):
    meanings, sets = {}, {}
    ambiguous = collapsed = inputs = 0
    for sentence in public_variants():
        readings = tuple(parse(sentence)["readings"])
        if not readings:
            raise ValueError(f"no public reading for {sentence}")
        for r in readings:
            if r not in meanings:
                (meanings[r],) = bank.signature_set([r])
        sig = frozenset(meanings[r] for r in readings)
        sets[readings] = sig
        inputs += 1
        ambiguous += len(readings) == 2
        collapsed += len(sig) < len(readings)
    def totals(values):
        counts = Counter(values)
        return {"distinct_exact": sum(counts.values()), "distinct_behavioral": len(counts),
                "collision_groups": sum(n > 1 for n in counts.values()),
                "members_in_collision_groups": sum(n for n in counts.values() if n > 1)}
    return {"inputs": inputs, "ambiguous": ambiguous, "within_sentence_collapses": collapsed,
            "readings": totals(meanings.values()), "sentence_sets": totals(sets.values())}


def grid_counts(bank, ontology):
    # Each integer contains truth at all 256 worlds. Construct the event relation
    # directly from the public predicate masks, independently of the reference parser.
    entities, events = range(4), range(3)
    def fact(name, bit):
        return bank.truth.get((name, bit), 0)
    nouns = {name: [fact(name, e) for e in entities] for name in ontology["nouns"].values()}
    verbs = sorted(f["predicate"] for f in ontology["frames"].values() if f["construction"] == "transitive")
    counts = Counter()
    for verb in verbs:
        for quick in (False, True):
            relation = [[0] * 4 for _ in entities]
            for v in events:
                active = fact(verb, v) & fact("Past", v)
                if quick:
                    active &= fact("Quick", v)
                for x in entities:
                    for y in entities:
                        relation[x][y] |= active & fact("Agent", 4*v+x) & fact("Theme", 4*v+y)
            for subject in nouns.values():
                for obj in nouns.values():
                    # Compare forall x exists y with exists y forall x, then reverse
                    # the determiner order, retaining the Agent/Theme argument order.
                    forall_exists, exists_forall = FULL, 0
                    exists_forall_rev, forall_exists_rev = 0, FULL
                    for x in entities:
                        some_y, every_y = 0, FULL
                        for y in entities:
                            some_y |= obj[y] & relation[x][y]
                            every_y &= (FULL ^ obj[y]) | relation[x][y]
                        forall_exists &= (FULL ^ subject[x]) | some_y
                        exists_forall_rev |= subject[x] & every_y
                    for y in entities:
                        every_x, some_x = FULL, 0
                        for x in entities:
                            every_x &= (FULL ^ subject[x]) | relation[x][y]
                            some_x |= subject[x] & relation[x][y]
                        exists_forall |= obj[y] & every_x
                        forall_exists_rev &= (FULL ^ obj[y]) | some_x
                    counts["pairs"] += 2
                    counts["indistinguishable"] += (forall_exists == exists_forall) + (exists_forall_rev == forall_exists_rev)
    return dict(counts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bank", type=Path, default=BANK_FILE)
    args = parser.parse_args()
    raw = args.bank.read_bytes()
    data = json.loads(raw)
    ontology = (ROOT / "spec/ontology.yaml").read_bytes()
    if data["ontology_sha256"] != hashlib.sha256(ontology).hexdigest():
        raise ValueError("bank and ontology differ")
    ontology = json.loads(ontology)
    bank = WorldBank(data, ontology)
    print(json.dumps({"sha256": hashlib.sha256(raw).hexdigest(), "variants": variant_counts(bank),
                      "scope_grid": grid_counts(bank, ontology)}, indent=2))


if __name__ == "__main__":
    main()
