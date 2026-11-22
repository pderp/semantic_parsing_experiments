"""Measure scope and control collisions on public inputs and exhaustive contrast grids."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from itertools import permutations
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.reference import parse
from src.semantics import normalize, reading_text
from src.semantics.world_bank import BANK_FILE, FULL, WorldBank, formula
from tests.reference.test_seed import public_variants


def variant_counts(bank, sentences=None):
    if sentences is None:
        sentences = public_variants()
    meanings, sets = {}, {}
    ambiguous = collapsed = inputs = 0
    for sentence in sentences:
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
    representative = {slot: min(name for name, i in bank.names.items() if i == slot) for slot in range(4)}
    pattern = re.compile(r"\b(?:" + "|".join(map(re.escape, bank.names)) + r")\b")

    def alias_key(reading):
        folded = pattern.sub(lambda m: representative[bank.names[m[0]]], reading)
        return reading_text(normalize(formula(folded)).normal)

    def detail(items):
        groups = defaultdict(list)
        for r, sig in items.items():
            groups[sig].append(r)
        alias_only = mixed = 0
        for rows in groups.values():
            if len(rows) > 1:
                if len({alias_key(r) for r in rows}) == 1:
                    alias_only += 1
                else:
                    mixed += 1
        return {**totals(items.values()), "alias_only_groups": alias_only, "other_groups": mixed,
                "constant_matrix": sum(int(sig[0], 16) in (0, FULL) for sig in items.values())}

    controls = {r: sig for r, sig in meanings.items() if "(Content " in r}
    quantified = {r: sig for r, sig in controls.items() if "(Box (ExistsE " in r or "(Box (ForallE " in r}
    return {"inputs": inputs, "ambiguous": ambiguous, "within_sentence_collapses": collapsed,
            "readings": totals(meanings.values()), "sentence_sets": totals(sets.values()),
            "control": detail(controls), "quantified_object_control": detail(quantified),
            "non_control": detail({r: sig for r, sig in meanings.items() if r not in controls})}


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


def control_grid(bank, ontology):
    # Use actual ground controller slots and the shared evaluator's Box-value
    # semantics. Check matrix truth by itself so different payload tables alone
    # cannot conceal a Content relation which is always false.
    names = [next(name for name, i in bank.names.items() if i == slot) for slot in range(4)]
    verbs = sorted(f["predicate"] for f in ontology["frames"].values() if f["construction"] == "transitive")
    counts = Counter()
    def matrix(frame, subject, recipient, vector):
        truth = 0
        for v in range(3):
            truth |= (bank.truth.get((frame, v), 0) & bank.truth.get(("Past", v), 0)
                      & bank.truth.get(("Agent", 4*v + subject), 0)
                      & bank.truth.get(("Recipient", 4*v + recipient), 0)
                      & bank.content.get((v, vector), 0))
        return truth
    for verb in verbs:
        for quick in (False, True):
            for noun in ontology["nouns"].values():
                payloads = []
                for name in names:
                    body = f"(And ({verb} e) (And (Agent e {name}) (Theme e y)))"
                    if quick:
                        body = f"(And (Quick e) {body})"
                    event = f"(ExistsV (fn e V {body}))"
                    formulas = (f"(ExistsE (fn y E (And ({noun} y) {event})))",
                                f"(ForallE (fn y E (Implies ({noun} y) {event})))")
                    payloads.append([int(bank.signature(f)["matrix"], 16) for f in formulas])
                for subject, recipient in permutations(range(4), 2):
                    for frame, right, wrong in [("Promise", subject, recipient), ("Persuade", recipient, subject)]:
                        pair = [matrix(frame, subject, recipient, v) for v in payloads[right]]
                        counts["determiner_pairs"] += 1
                        counts["indistinguishable_determiners"] += pair[0] == pair[1]
                        for truth, v in zip(pair, payloads[wrong]):
                            counts["controller_pairs"] += 1
                            counts["indistinguishable_controllers"] += truth == matrix(frame, subject, recipient, v)
                            counts["constant_correct_matrices"] += truth in (0, FULL)
    return dict(counts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bank", type=Path, default=BANK_FILE)
    parser.add_argument("--training", action="store_true", help="also audit the 4,000 released training inputs")
    args = parser.parse_args()
    raw = args.bank.read_bytes()
    data = json.loads(raw)
    ontology = (ROOT / "spec/ontology.yaml").read_bytes()
    if data["ontology_sha256"] != hashlib.sha256(ontology).hexdigest():
        raise ValueError("bank and ontology differ")
    ontology = json.loads(ontology)
    bank = WorldBank(data, ontology)
    result = {"sha256": hashlib.sha256(raw).hexdigest(), "variants": variant_counts(bank, public_variants()),
              "scope_grid": grid_counts(bank, ontology), "control_grid": control_grid(bank, ontology)}
    if args.training:
        path = ROOT / "data/controlled/train_inputs_v1.jsonl"
        with path.open() as rows:
            result["training"] = variant_counts(bank, (json.loads(row)["input"] for row in rows))
        result["training_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
