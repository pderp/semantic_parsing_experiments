#!/usr/bin/env python3
"""Generate cases_witness_v11.json: seed-1.1 cases around the article rule, with
ClaudeOracle's expected full output (oracle_v11.analyse).  Deterministic.

    python3 gen_cases_v11.py            # print to stdout
    python3 gen_cases_v11.py --write    # write cases_witness_v11.json (refuses to overwrite)
"""
import hashlib
import json
import sys

import oracle_v11 as X

BUNDLE = X.load_bundle()
ONT = X.load_ontology()

TINY = ["det.a", "det.an", "noun.editor", "noun.student", "leave.iv.past.existential"]
GRAMMARS = {
    "full": {},
    "articles": {"entries": TINY},
    "a-only": {"entries": [e for e in TINY if e != "det.an"]},
    "an-clone": {"entries": TINY, "clones": [{"id": "det.an.b", "clone_of": "det.an"}]},
}

VOCAB = "vocabulary = tokens of the grammar's own entries (not the whole ontology)"
EDGE = "edge identity and count as defined in conventions.edge_count"
CLONE = "a clone of det.a or det.an inherits its source's next_nouns list"
NOBUDGET = object()
CASES = []


def add(inp, grammar="full", max_edges=NOBUDGET, dep=(), note=""):
    CASES.append((grammar, inp, max_edges, list(dep), note))


# --- right article, every NP position
add("An editor left.", note="subject, vowel-initial noun")
add("A student left.", note="subject, other noun")
add("AN   Editor\tleft .", note="duplicate in case and spacing; rule applies after normalization")
add("an editor cited a paper", note="subject an, object a; two existentials, one reading")
add("a student cited an article", note="object, vowel-initial noun")
add("an author discussed an abstract quickly", note="both positions vowel-initial")
add("every reviewer evaluated an article", note="mixed quantifiers: two readings")
add("an analyst evaluated every proposal", note="mixed quantifiers: two readings")
add("every editor cited a paper", note="unchanged 'a'; 'every' is unaffected by the noun's initial")
add("an investigator did not arrive", note="subject of VP negation")
add("dan did not cite an article", note="object under VP negation")
add("an editor did not review a draft quickly")
add("not every scholar discussed an abstract", note="object under initial not-every")
add("not every author reviewed a manuscript quickly")
add("gia promised an author to leave", note="recipient of subject control")
add("an investigator persuaded a student to speak quickly", note="subject and recipient of object control")
add("hugo persuaded eva to review an article", note="embedded object")
add("an editor promised an analyst to cite an abstract quickly", note="subject, recipient and embedded object")
add("every professor did not persuade an investigator to evaluate an abstract quickly", note="12 tokens")
add("not every editor persuaded an author to discuss a thesis")
for noun in ("abstract", "analyst", "article", "author", "editor", "investigator"):
    add("an %s arrived" % noun, note="each vowel-initial noun")
for noun in ("paper", "researcher", "scholar", "thesis"):
    add("a %s arrived" % noun)

# --- wrong article, every NP position
add("a editor left", note="wrong article, subject")
add("an student left", note="wrong article, subject")
add("A EDITOR left.", note="wrong article in upper case")
add("an editor cited an paper", note="wrong article, object")
add("a student cited a article", note="wrong article, object")
add("every reviewer evaluated a article", note="wrong article, object; would be ambiguous otherwise")
add("a investigator did not arrive", note="wrong article, subject of VP negation")
add("dan did not cite a article", note="wrong article, object under VP negation")
add("not every scholar discussed a abstract", note="wrong article under initial not-every")
add("gia promised a author to leave", note="wrong article, recipient")
add("hugo persuaded eva to review a article", note="wrong article, embedded object")
add("an editor promised an analyst to cite a abstract quickly", note="one wrong article among three NPs")
add("a editor promised an analyst to cite an abstract quickly", note="one wrong article among three NPs")
for noun in ("abstract", "analyst", "article", "author", "editor", "investigator"):
    add("a %s arrived" % noun, note="wrong article before each vowel-initial noun")
for noun in ("paper", "researcher", "scholar", "thesis"):
    add("an %s arrived" % noun, note="wrong article")

# --- other failures around the articles
add("an alice left", note="article before a name")
add("an every editor left")
add("an an editor left")
add("a an editor left")
add("every an editor left")
add("an editor left an", note="article with nothing after it")
add("an", note="article alone")
add("editor an left")
add("not an editor left", note="initial not takes only every")
add("an apple left", note="unknown noun: lexical failure precedes the article rule")
add("an edit0r left", note="invalid token precedes the article rule")
add("an quickly left")

# --- budget: an unanchored article is not an edge
G = X.make_grammar(GRAMMARS["articles"], BUNDLE)
good = X.count_edges(G, ["an", "editor", "left"])
bad = X.count_edges(G, ["a", "editor", "left"])
add("an editor left", "articles", note="tiny grammar")
add("a editor left", "articles", note="tiny grammar, wrong article")
add("a student left", "articles")
add("an student left", "articles")
add("an editor left", "articles", good, [EDGE], "budget exactly at my edge count")
add("an editor left", "articles", good - 1, [EDGE])
add("a editor left", "articles", bad, [EDGE], "the wrong article anchors no edge: only noun and verb count")
add("a editor left", "articles", bad - 1, [EDGE])
add("a editor left", "articles", 0, note="budget is hit before no_root is known")
add("a editor left", "full", 10 ** 6, note="budget not reached: no_root")

# --- restricted and cloned grammars
add("a student left", "a-only")
add("a editor left", "a-only", note="no det.an entry, and det.a may not precede editor")
add("an editor left", "a-only", dep=[VOCAB], note="'an' is not a token of this grammar")
add("an editor left", "an-clone", dep=[CLONE], note="two article entries: two witnesses, one reading")
add("an student left", "an-clone", dep=[CLONE], note="the clone is bound by the same list")

CONVENTIONS = {
    "base": "Same format as cases_witness_v1.json, over bundle seed-witness-v1.1 (inbox_v3).",
    "grammar_spec": "'entries' lists published entry IDs (absent = all 179). 'clones' keep the source's "
                    "recipe, ground category, meaning and, for det.a / det.an, its next_nouns list. "
                    "'rules', 'roots', 'max_tokens' default to the published values.",
    "article_rule": "A det.a or det.an lexical edge anchors only if the immediately following token is in "
                    "the inventory's next_nouns list for that entry. An unanchored article contributes no "
                    "edge, no node and no budget use.",
    "expected": "tokens, construction_status, decision, diagnostic {code[, token, index]}, readings, "
                "min_cost, ranked_readings, witnesses in rank order (cost, object_wide_uses, key, reading).",
    "edge_count": "Packed bottom-up chart over all spans; node = (start, end, ground category); lexical "
                  "edge = (start, end, entry ID); binary edge = (rule ID, left node, right node). "
                  "Truncated iff edge_count > max_edges.",
    "depends_on": "Conventions the published texts leave open; a mismatch on such a case may be a "
                  "difference of convention rather than a defect.",
}


def build():
    grammars = {name: X.make_grammar(spec, BUNDLE) for name, spec in GRAMMARS.items()}
    cases = []
    for idx, (gname, inp, budget, dep, note) in enumerate(CASES, 1):
        g = grammars[gname]
        case = {"id": "A%03d" % idx, "grammar": gname, "input": inp}
        kwargs = {}
        if budget is not NOBUDGET:
            case["max_edges"] = kwargs["max_edges"] = budget
        exp = X.analyse(inp, g, ONT, **kwargs)
        for w in exp["witnesses"]:
            del w["rank"]
        case["expected"] = exp
        if isinstance(inp, str) and exp["diagnostic"]["code"] in ("", "no_root", "edge_budget") \
                and len(exp["tokens"]) <= g["max_tokens"]:
            case["edge_count"] = X.count_edges(g, exp["tokens"])
        case["depends_on"] = dep
        case["note"] = note
        cases.append(case)
    sha = lambda p: hashlib.sha256((X.INBOX / p).read_bytes()).hexdigest()
    return {"format": "claudeoracle-witness-cases-v1", "bundle": BUNDLE["version"],
            "inventory_sha256": sha("bundle_inventory_no_meanings.json"),
            "ontology_sha256": sha("ontology.yaml"), "contract_sha256": sha("contract.md"),
            "witness_contract_sha256": sha("witness-v1.md"),
            "conventions": CONVENTIONS, "grammars": GRAMMARS, "cases": cases}


def dumps(doc):
    return json.dumps(doc, indent=1, ensure_ascii=True) + "\n"


if __name__ == "__main__":
    text = dumps(build())
    if "--write" in sys.argv:
        with open(X.HERE / "cases_witness_v11.json", "x") as fh:
            fh.write(text)
    else:
        sys.stdout.write(text)
