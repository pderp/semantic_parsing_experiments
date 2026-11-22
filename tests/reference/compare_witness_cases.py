"""Replay the frozen M07/M08 cases from either seed release without importing the oracle."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from src.reference import parse
from src.reference.restrictions import restrict_bundle
from src.reference.seed import compile_seed

ROOT = Path(__file__).resolve().parents[2]
SUITES = {
    "seed-1.0": ("cases_witness_v1.json", "inbox_v2",
                 "68edf14dd266e3b83608084339a11ef1b9c848d464c07fe8a48744f043bc1621"),
    "seed-1.1": ("cases_witness_v11.json", "inbox_v3",
                 "fe01af31dd5b1d90bf48c47f1380b2401310c9a3586c215502a344e57bc66f28"),
}
WITNESS_FIELDS = ("cost", "object_wide_uses", "key", "reading")


def read_checked(path, digest):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != digest:
        raise ValueError(f"{path.name}: SHA-256 mismatch")
    return raw


def read_suite(seed):
    filename, _, digest = SUITES[seed]
    return json.loads(read_checked(ROOT / "oracle" / filename, digest))


def frozen_inputs(seed="seed-1.0"):
    suite = read_suite(seed)
    package = ROOT / "oracle" / SUITES[seed][1]
    ontology = read_checked(package / "ontology.yaml", suite["ontology_sha256"])
    inventory = json.loads(read_checked(package / "bundle_inventory_no_meanings.json", suite["inventory_sha256"]))
    read_checked(package / "contract.md", suite["contract_sha256"])
    read_checked(package / "witness-v1.md", suite["witness_contract_sha256"])
    base = compile_seed(ontology)
    actual = base.inventory()
    for entry in actual["entries"].values():
        del entry["meaning"]
    if json.loads(json.dumps(actual)) != inventory or base.version != suite["bundle"]:
        raise ValueError("reference compilation differs from the frozen meaning-free inventory")
    bundles = {name: restrict_bundle(base, spec) for name, spec in suite["grammars"].items()}
    return suite["cases"], bundles


def compare(case, bundle):
    result = parse(case["input"], bundle=bundle, max_edges=case.get("max_edges"))
    expected = case["expected"]
    diagnostic = {"code": result["diagnostic"]}
    if "token" in result or "token_index" in result:
        diagnostic.update(token=result["token"], index=result["token_index"])
    actual = {k: result[k] for k in ("tokens", "construction_status", "decision", "readings",
                                      "min_cost", "ranked_readings")}
    actual["diagnostic"] = diagnostic
    actual["witnesses"] = [{k: w[k] for k in WITNESS_FIELDS} for w in result["witnesses"]]
    # Make tuples JSON arrays, preserving child order, all witness fields, and multiplicity.
    actual = json.loads(json.dumps(actual))
    differences = {k: (expected.get(k), actual.get(k)) for k in expected.keys() | actual.keys()
                   if k not in expected or k not in actual or expected[k] != actual[k]}
    if "edge_count" in case:
        exact = parse(case["input"], bundle=bundle) if "max_edges" in case else result
        if exact["edges"] != case["edge_count"]:
            differences["exact_edge_count"] = case["edge_count"], exact["edges"]
        expected_inserted = min(case["edge_count"], case.get("max_edges", case["edge_count"]))
        if result["edges"] != expected_inserted:
            differences["inserted_edges"] = expected_inserted, result["edges"]
    return result, differences


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", choices=SUITES, default="seed-1.0")
    args = parser.parse_args()
    cases, bundles = frozen_inputs(args.seed)
    outcomes, mismatches = Counter(), {}
    witnesses = 0
    for case in cases:
        result, differences = compare(case, bundles[case["grammar"]])
        outcomes[result["diagnostic"] or result["decision"]] += 1
        witnesses += len(result["witnesses"])
        if differences:
            mismatches[case["id"]] = differences
    print(json.dumps({"cases": len(cases), "grammars": len(bundles), "witnesses": witnesses,
                      "outcomes": outcomes, "mismatches": mismatches}, sort_keys=True, indent=2))
    return bool(mismatches)


if __name__ == "__main__":
    raise SystemExit(main())
