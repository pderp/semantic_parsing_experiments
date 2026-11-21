#!/usr/bin/env python3
"""Validate the public M01 pilot configuration and print its Markdown tables."""
import argparse
from fractions import Fraction
import hashlib
import json
from math import ceil, comb
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SPLITS = ("training", "development", "calibration", "locked")
CELLS = ("ordinary_single", "ordinary_ambiguous", "transfer_single", "transfer_ambiguous")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def count(value):
    require(type(value) is int and value >= 0, f"expected nonnegative count, got {value!r}")
    return value


def rate(percent):
    value = Fraction(str(percent)) / 100
    require(0 <= value <= 1, f"invalid percentage {percent}")
    return value


def apportion(n, percents):
    require(sum(map(rate, percents.values())) == 1, "mixture percentages must sum to 100")
    quotas = [n * rate(p) for p in percents.values()]
    require(all(q.denominator == 1 for q in quotas), f"nonintegral target in mixture of {n}")
    return [int(q) for q in quotas]


def table(title, headers, rows):
    lines = [f"## {title}", "", "| " + " | ".join(headers) + " |",
             "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(map(str, row)) + " |")
    return "\n".join(lines)


def error_allowance(n, min_accuracy, confidence):
    """Largest errors e such that P(errors <= e | accuracy=min_accuracy) <= alpha."""
    tail = Fraction(0)
    for e in range(n + 1):
        tail += comb(n, e) * (1 - min_accuracy) ** e * min_accuracy ** (n - e)
        if tail > 1 - confidence:
            return e - 1
    return n


def render(config, ontology):
    c = config["corpus"]
    t = config["transfer"]
    a = config["audit"]
    g = config["gates"]
    splits = c["split_cells"]
    require(config["protocol"] == ontology["version"], "contract/ontology version mismatch")
    require(set(splits) == set(SPLITS), "expected four named splits")
    rows, ordinary, total_by_split = [], [], {}
    for name in SPLITS:
        split = splits[name]
        require(set(split) == set(CELLS), f"{name}: missing or unexpected cell")
        osingle, oamb, tsingle, tamb = [count(split[k]) for k in CELLS]
        total = sum(split.values())
        require(total > 0, f"{name}: empty split")
        require(oamb == (osingle + oamb) * rate(c["ambiguous_pct"]), f"{name}: ordinary ambiguity mix")
        require(tamb == (tsingle + tamb) * rate(c["ambiguous_pct"]), f"{name}: transfer ambiguity mix")
        if name in ("training", "calibration"):
            require(tsingle + tamb == 0, f"{name}: transfer data leakage")
        else:
            require(tsingle > 0 and tamb > 0, f"{name}: incomplete transfer panel")
        total_by_split[name] = total
        rows.append([name, osingle, oamb, tsingle, tamb, total])
        ordinary.append([name, *apportion(osingle, c["ordinary_single_pct"]),
                         *apportion(oamb, c["ordinary_ambiguous_pct"])])
    require(sum(total_by_split.values()) == c["total"], "split totals differ from corpus total")
    teacher = config["teacher"]
    require(teacher["initial_annotations"] == c["total"], "initial annotation budget differs from population")
    require(0 < teacher["pilot_within_training"] <= total_by_split["training"], "pilot outside training")
    require(teacher["pilot_ambiguous"] == teacher["pilot_within_training"] * rate(c["ambiguous_pct"]),
            "pilot ambiguity mix")
    world = config["world_bank"]
    exhaustive = 2 ** count(world["exhaustive_bits"])
    require(exhaustive + world["hand_checked"] + world["sampled_distinct"] == world["worlds"],
            "world-bank total differs from component counts")

    quotas = []
    dev = splits["development"]
    phases = [("M13 early freeze", dev["ordinary_single"] + dev["ordinary_ambiguous"], dev["ordinary_single"], 0)]
    for phase in ("development", "locked"):
        panel = splits[phase]
        singles = panel["ordinary_single"] + panel["transfer_single"]
        transfer_n = panel["transfer_single"] + panel["transfer_ambiguous"]
        phases.append((phase, total_by_split[phase], singles, transfer_n))
    for phase, n, singles, transfer_n in phases:
        overall_min = ceil(n * rate(g["overall_singleton_coverage_pct"]))
        single_min = ceil(singles * rate(g["single_reading_singleton_coverage_pct"]))
        yield_min = ceil(transfer_n * rate(t["absolute_set_yield_floor_pct"]))
        quotas.append([phase, f"{overall_min}/{n}", f"{single_min}/{singles}",
                       f"{yield_min}/{transfer_n}" if transfer_n else "not opened"])

    looks = t["funding_looks"]
    require(type(looks) is int and looks in (1, 2), "funding looks must be one or two")
    require(t["fresh_panel_reserved"] == (looks == 2), "second look needs its own reserved panel")
    min_families = count(t["min_distinct_families_per_panel"])
    require(min_families > 0, "empty family floor")
    require(t["two_reading_capable_families"] >= t["min_ambiguous_families_for_ordinary_training"] + looks + 1,
            "insufficient distinct ambiguous families for training, funding and locked panels")
    bounds = t["one_sided_confidence_pct_by_looks"]
    require(looks * (1 - rate(bounds[str(looks)])) <= 1 - rate(bounds["1"]), "funding looks exceed alpha budget")

    audit_rows = []
    for kind in ("ordinary", "transfer"):
        n = count(a["controlled_dev_" + kind])
        ambiguous = n * rate(a["controlled_dev_ambiguous_pct"])
        require(ambiguous.denominator == 1, "nonintegral audit cell")
        for reading, audited in [("single", n - int(ambiguous)), ("ambiguous", int(ambiguous))]:
            require(audited <= splits["development"][kind + "_" + reading], "audit cell exceeds available population")
        audit_rows.append(["controlled development " + kind, n - int(ambiguous), int(ambiguous), n])
    require(a["locked"] <= total_by_split["locked"] and a["natural_dev"] <= c["natural"]["development"],
            "audit exceeds source population")
    require(g["dev_min_audited_accepted"] <= sum(row[-1] for row in audit_rows), "accepted audit threshold unreachable")
    require(a["human_readers"] >= 2 or a["independent_second_human_read_pct"] == 0, "second reader unavailable")
    examples = []
    for n in g["independent_case_examples_n"]:
        allowed = error_allowance(n, rate(g["locked_min_accepted_accuracy_lower_pct"]),
                                  rate(g["locked_one_sided_confidence_pct"]))
        examples.append([n, allowed if allowed >= 0 else "unattainable",
                         f"{100*(n-allowed)/n:.2f}%" if allowed >= 0 else "—"])
    budgets = [
        ["teacher calls (initial + repeats, pilot included)", teacher["initial_annotations"] + teacher["repeat_calls"]],
        ["world bank (exhaustive + hand-checked + sampled)", f'{exhaustive} + {world["hand_checked"]} + {world["sampled_distinct"]} = {world["worlds"]}'],
        ["minimum distinct families (funding panels + locked)", (looks + 1) * min_families],
        ["funding looks / one-sided confidence", f'{looks} / {bounds[str(looks)]}%'],
        ["natural development audit", a["natural_dev"]], ["locked controlled audit", a["locked"]],
        ["benchmark blocks per local configuration, minimum", config["runtime"]["timing_blocks_min"]]
    ]
    return "\n\n".join([
        table("Controlled split", ["Split", *CELLS, "Total"], rows),
        table("Ordinary construction quotas", ["Split", *("single " + k for k in c["ordinary_single_pct"]), *("ambiguous " + k for k in c["ordinary_ambiguous_pct"])], ordinary),
        table("Minimum correct or accepted counts", ["Phase", "Accepted/all", "Accepted/single-reading", "Correct set/transfer"], quotas),
        table("Controlled development audit", ["Sample", "Single", "Ambiguous", "Total"], audit_rows),
        table("Independent equal-probability accuracy examples", ["Audited accepted", "Maximum errors", "Observed accuracy"], examples),
        table("Design arithmetic", ["Quantity", "Proposed value"], budgets)
    ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "pilot.yaml")
    args = parser.parse_args()
    try:
        raw = args.config.read_bytes()
        cfg = json.loads(raw)
        ontology = json.loads((ROOT / cfg["ontology"]).read_bytes())
        tables = render(cfg, ontology)
    except (OSError, KeyError, TypeError, ValueError, ArithmeticError) as exc:
        print(f"Pilot configuration invalid: {exc}", file=sys.stderr)
        return 1
    print(f'# Pilot tables · {cfg["protocol"]}\n\nConfiguration SHA-256: `{hashlib.sha256(raw).hexdigest()}`\n')
    print(tables)
    return 0


if __name__ == "__main__":
    sys.exit(main())
