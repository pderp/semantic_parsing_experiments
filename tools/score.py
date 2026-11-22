#!/usr/bin/env python3
"""Score a submission against D's targets (spec/submission.md). Standard library only.

    python3 tools/score.py --targets CORPUS.jsonl --submission SUB.jsonl \
        --splits training,development-ordinary [--rows OUT.jsonl]
    python3 tools/score.py ... --open development-transfer --ledger LEDGER.jsonl --reason "Decision 2"

Reserved panels (development-transfer, calibration, locked-ordinary, locked-transfer)
are scored only when named with --open, and each opening is appended to the ledger.
"""
import argparse
import hashlib
import json
import sys
import time
from collections import Counter, defaultdict

FREE = {"training", "development-ordinary"}
RESERVED = {"development-transfer", "calibration", "locked-ordinary", "locked-transfer"}
STATUS = {"complete", "truncated", "no_parse", "error"}
DECISION = {"accepted", "ambiguous", "abstain"}


def panel(row):
    if row["split"] in ("training", "calibration"):
        return row["split"]
    return row["split"] + ("-transfer" if row["cell"].startswith("transfer") else "-ordinary")


def load_submission(path, known):
    out = {}
    for n, line in enumerate(open(path, encoding="utf-8"), 1):
        if not line.strip():
            continue
        try:
            r = json.loads(line)
            ok = (isinstance(r["id"], str) and r["construction_status"] in STATUS and r["decision"] in DECISION
                  and isinstance(r["readings"], list) and all(isinstance(x, str) for x in r["readings"]))
        except (ValueError, KeyError, TypeError):
            ok = False
        if not ok:
            sys.exit(f"invalid submission: malformed line {n}")
        if r["id"] in out:
            sys.exit(f"invalid submission: duplicate id {r['id']}")
        if r["id"] not in known:
            sys.exit(f"invalid submission: unknown id {r['id']}")
        out[r["id"]] = r
    return out


def admissible(answer):
    """A row is admissible when its status, decision and number of distinct readings fit together."""
    n = len(answer["readings"])
    if len(set(answer["readings"])) != n:
        return False
    if answer["decision"] == "abstain":
        return True                      # any status; readings kept for diagnosis are ignored
    if answer["construction_status"] != "complete":
        return False
    return n == (1 if answer["decision"] == "accepted" else 2)


def judge(target, answer):
    """Return (accepted, correct, inadmissible) for one input."""
    if answer is None:
        return False, False, False
    if not admissible(answer):
        return False, False, True        # counted, never credited
    if answer["decision"] == "abstain":
        return False, False, False
    got = sorted(answer["readings"], key=lambda s: s.encode("utf-8"))
    return answer["decision"] == "accepted", got == target["readings"], False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", required=True)
    ap.add_argument("--submission", required=True)
    ap.add_argument("--splits", default="")
    ap.add_argument("--open", default="")
    ap.add_argument("--ledger")
    ap.add_argument("--reason")
    ap.add_argument("--rows")
    ap.add_argument("--system-digest", help="digest of the frozen system that produced the submission")
    ap.add_argument("--repeat-authorized", help="reason a panel already in the ledger may be opened again")
    a = ap.parse_args()
    free = {s for s in a.splits.split(",") if s}
    opened = {s for s in a.open.split(",") if s}
    if free - FREE:
        sys.exit(f"--splits accepts only {sorted(FREE)}; reserved panels need --open")
    if opened - RESERVED:
        sys.exit(f"--open accepts only {sorted(RESERVED)}")
    if opened and not (a.ledger and a.reason and a.system_digest):
        sys.exit("opening a reserved panel needs --ledger, --reason and --system-digest")
    targets = [json.loads(l) for l in open(a.targets, encoding="utf-8")]
    by_id = {t["id"]: t for t in targets}
    sub = load_submission(a.submission, by_id)
    digest = hashlib.sha256(open(a.submission, "rb").read()).hexdigest()
    targets_digest = hashlib.sha256(open(a.targets, "rb").read()).hexdigest()
    if opened:
        try:
            earlier = [json.loads(l) for l in open(a.ledger, encoding="utf-8")]
        except FileNotFoundError:
            earlier = []
        again = sorted(p for p in opened if any(p in e["opened"] for e in earlier))
        if again and not a.repeat_authorized:
            sys.exit(f"already opened once: {again}. A further look needs --repeat-authorized with the reason.")
        with open(a.ledger, "a", encoding="utf-8") as f:
            f.write(json.dumps({"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "opened": sorted(opened),
                                "submission_sha256": digest, "system_digest": a.system_digest,
                                "targets_sha256": targets_digest, "reason": a.reason,
                                "repeat_authorized": a.repeat_authorized}) + "\n")
    rows_out = []
    print(f"submission sha256 {digest}")
    print("panel                  inputs  yield(set-aware)   accepted/all   accepted/single   accepted accuracy   inadmissible rows")
    for p in sorted(free | opened):
        ts = [t for t in targets if panel(t) == p]
        n = len(ts)
        acc = cor = acc_single = acc_cor = bad = 0
        single = sum(len(t["readings"]) == 1 for t in ts)
        fam = defaultdict(lambda: [0, 0])
        cells = Counter()
        for t in ts:
            accepted, correct, inadmissible = judge(t, sub.get(t["id"]))
            bad += inadmissible
            acc += accepted
            cor += correct
            acc_cor += accepted and correct
            acc_single += accepted and len(t["readings"]) == 1
            f = fam[tuple(t["family"])]
            f[0] += 1
            f[1] += correct
            cells[(t["cell"], correct)] += 1
            if p in FREE:
                rows_out.append({"id": t["id"], "accepted": accepted, "correct": correct, "inadmissible": inadmissible})
        pct = lambda x, y: f"{x}/{y} ({x / y:.1%})" if y else "n/a"
        print(f"{p:22s} {n:6d}  {pct(cor, n):18s} {pct(acc, n):14s} {pct(acc_single, single):17s} {pct(acc_cor, acc):19s} {bad}")
        if p.endswith("transfer"):
            full = sum(1 for k, (m, c) in fam.items() if c == m)
            none = sum(1 for k, (m, c) in fam.items() if c == 0)
            print(f"    families: {len(fam)}; all rows correct in {full}, none correct in {none}, mixed in {len(fam) - full - none}")
            # Opaque labels: stable for one targets file, and they do not reveal the family.
            label = lambda k: hashlib.sha256((targets_digest + json.dumps(k)).encode()).hexdigest()[:8]
            print("    per family (label correct/rows): " + " ".join(
                f"{label(k)} {c}/{m}" for k, (m, c) in sorted(fam.items(), key=lambda kv: label(kv[0]))))
            for cell in ("transfer_single", "transfer_ambiguous"):
                c, w = cells[(cell, True)], cells[(cell, False)]
                print(f"    {cell}: {c}/{c + w} correct")
    if a.rows:
        with open(a.rows, "w", encoding="utf-8") as f:
            for r in rows_out:
                f.write(json.dumps(r) + "\n")


if __name__ == "__main__":
    main()
