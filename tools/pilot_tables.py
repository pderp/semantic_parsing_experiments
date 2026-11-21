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
    rows, ordinary, negation, total_by_split = [], [], [], {}
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
        single_quota = dict(zip(c["ordinary_single_pct"], apportion(osingle, c["ordinary_single_pct"])))
        ordinary.append([name, *single_quota.values(), *apportion(oamb, c["ordinary_ambiguous_pct"])])
        negation_n = single_quota["negation"]
        roots = c["ordinary_single_negation"]
        min_not_every = ceil(negation_n * rate(roots["min_not_every_pct"]))
        min_vp = count(roots["min_vp_negation_rows_per_split"])
        require(min_not_every > 0 and min_vp > 0 and min_not_every + min_vp <= negation_n,
                f"{name}: negation quota cannot support both root operators")
        negation.append([name, negation_n, min_not_every, min_vp])
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
    require(count(looks) == 1 and t["fresh_panel_reserved"] is False, "registered design has one funding look")
    min_families = count(t["min_distinct_families_per_panel"])
    single_families = count(t["families_per_panel"]["single_only"])
    ambiguous_families = count(t["families_per_panel"]["two_reading"])
    per_panel = single_families + ambiguous_families
    require(single_families > 0 and ambiguous_families == 1 and per_panel == min_families,
            "registered allocation must match the family floor and include one two-reading family per panel")
    panels = ("development", "locked")
    total_families = count(t["public_census_primary_families"])
    capable = count(t["two_reading_capable_families"])
    require(len(panels) * single_families <= total_families - capable,
            "insufficient disjoint single-only families")
    require(len(panels) * ambiguous_families + count(t["min_ambiguous_families_for_ordinary_training"]) <= capable,
            "insufficient disjoint two-reading families")
    require(t["registered_relative_cell"] == "transfer_single", "relative comparison requires single-reading transfer")
    require(rate(t["funding_one_sided_confidence_pct"]) == rate(t["locked_one_sided_confidence_pct"]) == rate(95),
            "registered funding and locked analyses use one-sided 95% limits")
    allocation = []
    for name in panels:
        relative_n = splits[name][t["registered_relative_cell"]]
        ambiguous_n = splits[name]["transfer_ambiguous"]
        require(relative_n >= single_families and ambiguous_n >= ambiguous_families,
                f"{name}: too few rows to represent the registered families")
        base, extra = divmod(relative_n, single_families)
        sizes = f"{single_families - extra} × {base}"
        if extra:
            sizes += f", {extra} × {base + 1}"
        allocation.append([name, relative_n, sizes, ambiguous_n, ambiguous_families])

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
        ["distinct reserved families in the design (development + locked)", len(panels) * per_panel],
        ["families available for training and ordinary evaluation", total_families - len(panels) * per_panel],
        ["funding looks / one-sided confidence", f'{looks} / {t["funding_one_sided_confidence_pct"]}%'],
        ["natural development audit", a["natural_dev"]], ["locked controlled audit", a["locked"]],
        ["benchmark blocks per local configuration, minimum", config["runtime"]["timing_blocks_min"]]
    ]
    return "\n\n".join([
        table("Controlled split", ["Split", *CELLS, "Total"], rows),
        table("Ordinary construction quotas", ["Split", *("single " + k for k in c["ordinary_single_pct"]), *("ambiguous " + k for k in c["ordinary_ambiguous_pct"])], ordinary),
        table("Ordinary single-reading negation", ["Split", "Negated rows", "Minimum initial not every", "Minimum VP negation"], negation),
        table("Transfer family allocation", ["Panel", "Relative comparison rows", "Single-only families × rows each", "Two-reading rows", "Two-reading families"], allocation),
        table("Minimum correct or accepted counts", ["Phase", "Accepted/all", "Accepted/single-reading", "Correct set/transfer"], quotas),
        table("Controlled development audit", ["Sample", "Single", "Ambiguous", "Total"], audit_rows),
        table("Independent equal-probability accuracy examples", ["Audited accepted", "Maximum errors", "Observed accuracy"], examples),
        table("Design arithmetic", ["Quantity", "Proposed value"], budgets)
    ])


def sign_off_table(record):
    rows = []
    for path, expected in record["reviewed_sha256"].items():
        actual = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        require(actual == expected, f"reviewed SHA-256 differs for {path}")
        rows.append([path, actual])
    return table("Stage 1 public evidence", ["Artifact", "SHA-256"], rows) + "\n\n" + record["custodian_evidence"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "pilot.yaml")
    args = parser.parse_args()
    try:
        raw = args.config.read_bytes()
        cfg = json.loads(raw)
        ontology = json.loads((ROOT / cfg["ontology"]).read_bytes())
        tables = render(cfg, ontology)
        evidence = sign_off_table(cfg["sign_off"])
    except (OSError, KeyError, TypeError, ValueError, ArithmeticError) as exc:
        print(f"Pilot configuration invalid: {exc}", file=sys.stderr)
        return 1
    print(f'# Pilot tables · {cfg["protocol"]}\n\nConfiguration SHA-256: `{hashlib.sha256(raw).hexdigest()}`\n')
    print(tables)
    print("\n" + evidence)
    return 0


if __name__ == "__main__":
    sys.exit(main())
