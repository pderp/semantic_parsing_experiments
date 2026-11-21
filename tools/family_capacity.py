#!/usr/bin/env python3
"""Count primary families and distinct surface strings licensed by the public
seed contract (spec/contract.md, spec/ontology.yaml).

This is public arithmetic from the published grammar and lexicon. It enumerates
family keys, not sentences, and reserves nothing. Run from the repository root:

    python3 tools/family_capacity.py [--names N] [--intransitives N]

The two options show how capacity changes if the lexicon were widened.
"""
import argparse
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--names", type=int)
    ap.add_argument("--intransitives", type=int)
    ap.add_argument("--per-family", type=int, default=10,
                    help="distinct strings wanted per family (200 inputs / 20 families)")
    args = ap.parse_args()
    onto = json.loads((ROOT / "spec" / "ontology.yaml").read_text())
    frames = onto["frames"].values()
    n_name = args.names or len(onto["names"])
    n_noun = len(onto["nouns"])
    n_det = len(onto["determiners"])
    n_iv = args.intransitives or sum(f["construction"] == "intransitive" for f in frames)
    n_tv = sum(f["construction"] == "transitive" for f in frames)
    n_ctl = {k: sum(f["construction"] == k for f in frames)
             for k in ("subject-control", "object-control")}

    def np(kind):                       # distinct strings for one NP slot
        return n_name if kind == "name" else n_det * n_noun

    kinds = ("name", "quantified")
    families = []                       # (key, strings, two_reading_strings, secondary_variants)
    for root in ("ordinary", "vp-negation", "not-every"):
        subj_kinds = ("quantified",) if root == "not-every" else kinds
        for subj in subj_kinds:
            # A not-every subject has its determiner fixed.
            s = n_noun if root == "not-every" else np(subj)
            s_dets = 1 if root == "not-every" or subj == "name" else n_det
            for manner in ("none", "matrix"):
                families.append(((root, "intransitive", subj, manner), s * n_iv, 0, s_dets))
                for obj in kinds:
                    strings = s * n_tv * np(obj)
                    two = 0
                    if root != "vp-negation" and subj == obj == "quantified":
                        # Mixed determiners only; like determiners are subject-wide only.
                        per_subject_det = n_noun * n_noun * n_tv
                        two = per_subject_det * (1 if root == "not-every" else 2)
                    variants = s_dets * (n_det if obj == "quantified" else 1)
                    families.append(((root, "transitive", subj, obj, manner), strings, two, variants))
            for ctl, rec in itertools.product(n_ctl, kinds):
                for manner in ("none", "embedded"):
                    base = s * n_ctl[ctl] * np(rec)
                    rec_dets = n_det if rec == "quantified" else 1
                    families.append(((root, ctl, subj, rec, "emb-intransitive", manner),
                                     base * n_iv, 0, s_dets * rec_dets))
                    for obj in kinds:
                        families.append(((root, ctl, subj, rec, "emb-transitive", obj, manner),
                                         base * n_tv * np(obj), 0,
                                         s_dets * rec_dets * (n_det if obj == "quantified" else 1)))

    want = args.per_family
    small = [f for f in families if f[1] < want]
    two = [f for f in families if f[2]]
    print(f"lexicon: {n_name} names, {n_noun} nouns, {n_det} determiners, "
          f"{n_iv} intransitive, {n_tv} transitive, control {n_ctl}")
    print(f"primary families:                 {len(families)}")
    print(f"secondary (determiner) variants:  {sum(f[3] for f in families)}")
    print(f"families that can yield two readings: {len(two)}")
    for key, strings, t, _ in two:
        print(f"    {key}: {t} two-reading strings of {strings}")
    print(f"families with fewer than {want} distinct strings: {len(small)}")
    for key, strings, _, _ in sorted(small, key=lambda f: f[1]):
        print(f"    {strings:4d}  {key}")
    by_root = {}
    for key, *_ in families:
        by_root[key[0]] = by_root.get(key[0], 0) + 1
    print("families by root operator:", by_root)


if __name__ == "__main__":
    main()
