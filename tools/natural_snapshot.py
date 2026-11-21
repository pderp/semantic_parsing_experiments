#!/usr/bin/env python3
"""Snapshot and sample natural English sentences from PLOS ONE (plan 05).

    python3 -I tools/natural_snapshot.py search  DIR
    python3 -I tools/natural_snapshot.py fetch   DIR [--articles 110]
    python3 -I tools/natural_snapshot.py sample  DIR OUT_SURVEY OUT_DEV

DIR holds the dated snapshot (search response and article XML) and stays outside
the repository. Standard library only. Requests carry a generic client name and
no personal details, and are spaced out.
"""
import hashlib
import json
import random
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

SEED = 20261121                      # configs/pilot.yaml: corpus.natural.sampling_seed_proposal
AGENT = "research-text-sampler/0.1"
QUERY = ('title:"peer review" OR abstract:"peer review" OR title:"scholarly publishing" OR '
         'abstract:"scholarly publishing" OR title:"research assessment" OR abstract:"research assessment"')
FILTER = 'journal_key:PLoSONE AND doc_type:full AND article_type:"Research Article"'
SURVEY_ARTICLES, DEV_ARTICLES, PER_ARTICLE = 40, 60, 5
LICENSE = "creativecommons.org/licenses/by/4.0"
SKIP = {"table-wrap", "fig", "caption", "ref-list", "supplementary-material", "disp-quote",
        "disp-formula", "inline-formula", "boxed-text", "list", "def-list", "fn", "ack"}
ABBREV = re.compile(r"\b(e\.g|i\.e|et al|Fig|Figs|vs|cf|Dr|Mr|Ms|Prof|No|approx|resp|Eq|Ref|St)\.$")


def get(url, pause=5.0):
    req = urllib.request.Request(url, headers={"User-Agent": AGENT})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    time.sleep(pause)
    return data


def search(d):
    d.mkdir(parents=True, exist_ok=True)
    docs, start = [], 0
    while True:
        qs = urllib.parse.urlencode({"q": QUERY, "fq": FILTER, "fl": "id,title,author_display,publication_date",
                                     "sort": "id asc", "rows": 500, "start": start, "wt": "json"})
        page = json.loads(get("https://api.plos.org/search?" + qs, pause=7))["response"]
        docs += page["docs"]
        start += 500
        if start >= page["numFound"]:
            break
    out = {"retrieved_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "query": QUERY,
           "filter": FILTER, "sort": "id asc", "num_found": page["numFound"], "docs": docs}
    (d / "search.json").write_text(json.dumps(out, indent=1) + "\n")
    print("found", page["numFound"], "saved", len(docs))


def order(d):
    docs = json.loads((d / "search.json").read_text())["docs"]
    ids = sorted(x["id"] for x in docs)
    random.Random(SEED).shuffle(ids)
    return ids, {x["id"]: x for x in docs}


def fetch(d, want):
    ids, _ = order(d)
    (d / "xml").mkdir(exist_ok=True)
    got = 0
    for doi in ids:
        if got >= want:
            break
        path = d / "xml" / (doi.replace("/", "_") + ".xml")
        if not path.exists():
            try:
                data = get("https://journals.plos.org/plosone/article/file?id=%s&type=manuscript" % urllib.parse.quote(doi, safe=""))
            except Exception as exc:                      # recorded, then skipped
                print("FAILED", doi, type(exc).__name__, flush=True)
                continue
            path.write_bytes(data)
        got += 1
    print("articles on disk:", got)


def paragraphs(root):
    body = root.find("body")
    if body is None:
        return

    def text(el):
        parts = [el.text or ""]
        for child in el:
            if child.tag not in SKIP and child.tag != "xref":
                parts.append(text(child))
            parts.append(child.tail or "")
        return "".join(parts)

    def walk(el):
        for child in el:
            if child.tag in SKIP:
                continue
            if child.tag == "p":
                yield text(child)
            else:
                yield from walk(child)
    yield from walk(body)


def sentences(par):
    par = re.sub(r"\s*[\[(][\s,;–-]*[\])]", "", par)        # emptied citation brackets
    par = re.sub(r"\s+", " ", par).strip()
    out, start = [], 0
    for m in re.finditer(r"[.!?](?=\s+[A-Z])", par):
        chunk = par[start:m.end()]
        if ABBREV.search(chunk):
            continue
        out.append(chunk.strip())
        start = m.end()
    if par[start:].strip():
        out.append(par[start:].strip())
    return out


def sample(d, out_survey, out_dev):
    ids, meta = order(d)
    rng = random.Random(SEED + 1)
    stats = {"articles_read": 0, "not_cc_by_4": 0, "no_usable_sentences": 0, "segments": 0, "segments_excluded": 0}
    rows = []
    for doi in ids:
        path = d / "xml" / (doi.replace("/", "_") + ".xml")
        if not path.exists() or len({r["doi"] for r in rows}) >= SURVEY_ARTICLES + DEV_ARTICLES:
            continue
        stats["articles_read"] += 1
        raw = path.read_bytes()
        root = ET.fromstring(raw)
        lic = [el.get("{http://www.w3.org/1999/xlink}href", "") for el in root.iter("license")]
        if not any(LICENSE in h for h in lic):
            stats["not_cc_by_4"] += 1
            continue
        cands = []
        for pi, par in enumerate(paragraphs(root)):
            for si, s in enumerate(sentences(par)):
                stats["segments"] += 1
                n = len(s.split())
                if 4 <= n <= 60 and s[0].isupper() and s[-1] in ".?!":
                    cands.append((pi, si, s))
                else:
                    stats["segments_excluded"] += 1
        if len(cands) < PER_ARTICLE:
            stats["no_usable_sentences"] += 1
            continue
        for pi, si, s in sorted(rng.sample(cands, PER_ARTICLE)):
            m = meta[doi]
            rows.append({"doi": doi, "title": m.get("title"), "authors": m.get("author_display"),
                         "license": next(h for h in lic if LICENSE in h), "paragraph": pi, "sentence": si,
                         "xml_sha256": hashlib.sha256(raw).hexdigest(), "text": s})
    dois = list(dict.fromkeys(r["doi"] for r in rows))
    survey = [r for r in rows if r["doi"] in set(dois[:SURVEY_ARTICLES])]
    dev = [r for r in rows if r["doi"] in set(dois[SURVEY_ARTICLES:SURVEY_ARTICLES + DEV_ARTICLES])]
    for path, part, tag in ((out_survey, survey, "NS"), (out_dev, dev, "ND")):
        for i, r in enumerate(part):
            r["id"] = f"{tag}{i:03d}"
        Path(path).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in part))
        print(tag, len(part), "sentences from", len({r["doi"] for r in part}), "articles",
              hashlib.sha256(Path(path).read_bytes()).hexdigest())
    print(stats, "seed", SEED)


if __name__ == "__main__":
    cmd, d = sys.argv[1], Path(sys.argv[2])
    if cmd == "search":
        search(d)
    elif cmd == "fetch":
        fetch(d, int(sys.argv[4]) if len(sys.argv) > 4 else 110)
    elif cmd == "sample":
        sample(d, sys.argv[3], sys.argv[4])
