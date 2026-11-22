#!/usr/bin/env python3
"""First-pass construction survey of the natural-text sample (plan 03, M01 row
"Natural English"). Mechanical word-pattern tags; see reports/natural_survey_v1.md
for their measured error. Standard library only.

    python3 tools/natural_survey.py data/natural/survey_v1.jsonl [--show N]
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

W = lambda s: set(s.split())
DET = W("the this these those some all each most many several no any both another other such")
PRON = W("it they we he she i you them us him me one itself themselves who")
POSS = W("their its our his her my your")
PREP = W("of in on for with by from at as between among across through during within without against about "
         "into over under after before towards toward via per including regarding among upon despite than")
COORD = W("and or but nor")
REL = W("which who whom whose where")
SUB = W("that whether if because although though while since when whereas unless so")
BE = W("is are was were be been being am")
MODAL = W("can could may might must should would will shall cannot")
NEG = W("not no never neither nor none")
HAVE = W("have has had having")
IRREG = W("been done made given taken shown found known seen held kept left written drawn chosen led built "
          "sent paid put set read understood undertaken")


def tags(text):
    words = re.findall(r"[A-Za-z]+(?:[’'][a-z]+)?|\d[\d.,]*%?|[^\sA-Za-z\d]", text)
    low = [w.lower() for w in words]
    t = set()
    participle = lambda w: (w.endswith("ed") and len(w) > 4) or w in IRREG
    for i, w in enumerate(low):
        nxt = [x for x in low[i + 1:i + 4] if x.isalpha()]
        if w in DET: t.add("other determiner (the, this, some, ...)")
        if w in PRON: t.add("pronoun")
        if w in POSS or w.endswith("'s") or w.endswith("’s") or w.endswith("s'"): t.add("possessive")
        if w in PREP: t.add("prepositional phrase")
        if w in COORD: t.add("coordination")
        if w in REL: t.add("relative clause (wh-)")
        if w in SUB: t.add("subordinate or complement clause (that, because, ...)")
        if w in MODAL: t.add("modal")
        if w in NEG or w.endswith("n't"): t.add("negation")
        if w in BE:
            if any(participle(x) for x in nxt[:2]): t.add("passive")
            elif nxt and nxt[0].endswith("ing"): t.add("progressive")
            else: t.add("copula")
        if w in HAVE and any(participle(x) for x in nxt[:2]): t.add("perfect")
        if w in W("is are has have do does am") or (w in MODAL): t.add("non-past tense")
        if w == "to" and nxt and not (nxt[0] in DET or nxt[0] in POSS): t.add("infinitive or to-phrase")
        if w.endswith("ing") and len(w) > 5: t.add("-ing form")
        if re.fullmatch(r"[a-z]{3,}(al|ive|ous|ic|able|ible|ful|less|ary)", w): t.add("adjective (by suffix)")
        if re.fullmatch(r"[a-z]{4,}ly", w): t.add("-ly adverb")
        if re.fullmatch(r"[a-z]{3,}[^su]s", w) and w not in BE | HAVE | {"this", "does", "towards", "perhaps", "whereas", "across", "analysis", "thus", "its"}:
            t.add("plural noun or -s verb")
        if w[0].isdigit(): t.add("numeral")
        if w in "()[]": t.add("parenthetical")
        if w in ":;": t.add("colon or semicolon")
    if text.rstrip().endswith("?"): t.add("question")
    return t, low


def main():
    path = sys.argv[1]
    show = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    rows = [json.loads(l) for l in open(path, encoding="utf-8")]
    from src.reference import parse
    onto = json.loads((ROOT / "spec/ontology.yaml").read_text())
    vocab = set(onto["names"]) | set(onto["nouns"]) | set(onto["determiners"]) | set(onto["operators"]) | set(onto["modifiers"]) \
        | {f[k] for f in onto["frames"].values() for k in ("bare", "past")}
    count, per, status, lens, known, total = Counter(), [], Counter(), [], 0, 0
    for r in rows:
        t, low = tags(r["text"])
        count.update(t)
        per.append(len(t))
        res = parse(r["text"])
        status[(res["construction_status"], res["diagnostic"])] += 1
        alpha = [w for w in low if w.isalpha()]
        lens.append(len(r["text"].split()))
        known += sum(w in vocab for w in alpha)
        total += len(alpha)
        if show and r["id"].endswith(("0", "5")) and int(r["id"][2:]) < show * 5:
            print(r["id"], "|", r["text"], "\n     ", "; ".join(sorted(x.split(" (")[0] for x in t)))
    lens.sort()
    print(f"\nsentences {len(rows)} | articles {len({r['doi'] for r in rows})} | words per sentence: median {lens[len(lens)//2]}, range {lens[0]}-{lens[-1]}")
    print(f"seed parser result: {dict(status)}")
    print(f"word tokens in the seed vocabulary: {known} of {total} ({known / total:.1%})")
    print(f"tags per sentence: median {sorted(per)[len(per)//2]}, min {min(per)}")
    for name, n in count.most_common():
        print(f"{n:4d}  {n / len(rows):5.0%}  {name}")


if __name__ == "__main__":
    main()
