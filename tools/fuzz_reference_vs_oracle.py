#!/usr/bin/env python3
"""Compare the reference parser with ClaudeOracle's enumerator on near-miss and
random inputs, where over- or under-generation would show.

    python3 tools/fuzz_reference_vs_oracle.py [--per-sentence 40] [--random 20000]

Inputs: the 392 public variants, mutations of each (delete, duplicate, swap,
substitute, insert a vocabulary token), and random token sequences. Compared:
tokens, both status axes, the reading set, and the ranked list of
(cost, object-wide uses, reading). Diagnostic codes and structural keys are not
compared. Uses public files only. Standard library only.
"""
import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "oracle"))

from src.reference import parse, tokenize            # noqa: E402
from tests.reference.test_seed import public_variants  # noqa: E402
import oracle_enum                                      # noqa: E402


def mutate(tokens, vocab, rng):
    t = list(tokens)
    op = rng.choice(("delete", "duplicate", "swap", "substitute", "insert"))
    i = rng.randrange(len(t))
    if op == "delete" and len(t) > 1:
        del t[i]
    elif op == "duplicate":
        t.insert(i, t[i])
    elif op == "swap" and len(t) > 1:
        j = min(i + 1, len(t) - 1)
        t[i], t[j] = t[j], t[i]
    elif op == "substitute":
        t[i] = rng.choice(vocab)
    else:
        t.insert(i, rng.choice(vocab))
    return t


def view(result, reading_field):
    return (result["tokens"], result["construction_status"], result["decision"], list(result["readings"]),
            [(w["cost"], w["object_wide_uses"], w[reading_field]) for w in result["witnesses"]])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-sentence", type=int, default=40)
    ap.add_argument("--random", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=20261126)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    onto = json.loads((ROOT / "spec/ontology.yaml").read_text())
    vocab = sorted(set(onto["names"]) | set(onto["nouns"]) | set(onto["determiners"]) | set(onto["operators"])
                   | set(onto["modifiers"]) | {f[k] for f in onto["frames"].values() for k in ("bare", "past")})
    inputs = set()
    base = [tuple(tokenize(s)) for s in public_variants()]
    inputs.update(base)
    for toks in base:
        for _ in range(a.per_sentence):
            m = list(toks)
            for _ in range(rng.choice((1, 1, 1, 2))):
                m = mutate(m, vocab, rng)
            inputs.add(tuple(m))
    for _ in range(a.random):
        inputs.add(tuple(rng.choice(vocab) for _ in range(rng.randint(1, 8))))
    status = Counter()
    bad = []
    for toks in sorted(inputs):
        sentence = " ".join(toks)
        ref = view(parse(sentence), "reading")
        ora = view(oracle_enum.enumerate_all(sentence), "meaning")
        status[ref[1]] += 1
        if ref != ora:
            bad.append(sentence)
    print(f"vocabulary {len(vocab)} tokens; inputs compared: {len(inputs)}")
    print("reference statuses:", dict(status))
    print(f"disagreements: {len(bad)}")
    for s in bad[:20]:
        print("   ", s)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
