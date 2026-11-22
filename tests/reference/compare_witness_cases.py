"""Replay the frozen M07/M08 cases from either seed release without importing the oracle."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from src.reference import parse
from src.reference.restrictions import InvalidRestriction, restrict_bundle
from src.reference.seed import compile_seed

ROOT = Path(__file__).resolve().parents[2]
SUITES = {
    # Cases, base grammar snapshot, witness contract snapshot, frozen case digest.
    "seed-1.0": ("cases_witness_v1.json", "inbox_v2", "inbox_v2",
                 "68edf14dd266e3b83608084339a11ef1b9c848d464c07fe8a48744f043bc1621"),
    "seed-1.1": ("cases_witness_v11.json", "inbox_v3", "inbox_v3",
                 "fe01af31dd5b1d90bf48c47f1380b2401310c9a3586c215502a344e57bc66f28"),
    "seed-1.1-r2": ("cases_witness_r2.json", "inbox_v3", "inbox_v4",
                    "a459df6e50e8f79fa1eced8902e691e8485a6f7dc168db31b77b327e7557e4f0"),
}
WITNESS_FIELDS = ("cost", "object_wide_uses", "key", "reading")


def read_checked(path, digest):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != digest:
        raise ValueError(f"{path.name}: SHA-256 mismatch")
    return raw


def read_suite(seed):
    filename, _, _, digest = SUITES[seed]
    return json.loads(read_checked(ROOT / "oracle" / filename, digest))


def frozen_inputs(seed="seed-1.0"):
    suite = read_suite(seed)
    package = ROOT / "oracle" / SUITES[seed][1]
    ontology = read_checked(package / "ontology.yaml", suite["ontology_sha256"])
    inventory = json.loads(read_checked(package / "bundle_inventory_no_meanings.json", suite["inventory_sha256"]))
    contract_digest = suite.get("contract_sha256")
    if contract_digest is None:
        # The revision-2 supplement inherits the original seed-1.1 reading contract.
        contract_digest = read_suite("seed-1.1")["contract_sha256"]
    read_checked(package / "contract.md", contract_digest)
    witness_package = ROOT / "oracle" / SUITES[seed][2]
    read_checked(witness_package / "witness-v1.md", suite["witness_contract_sha256"])
    base = compile_seed(ontology)
    actual = base.inventory()
    for entry in actual["entries"].values():
        del entry["meaning"]
    if json.loads(json.dumps(actual)) != inventory or base.version != suite["bundle"]:
        raise ValueError("reference compilation differs from the frozen meaning-free inventory")
    bundles = {}
    for name, spec in suite["grammars"].items():
        try:
            bundles[name] = restrict_bundle(base, spec)
        except InvalidRestriction as error:
            bundles[name] = error
    return suite["cases"], bundles


def field_differences(expected, actual):
    # JSON spelling distinguishes 1, 1.0 and true, which Python equality conflates.
    return {k: (expected.get(k), actual.get(k)) for k in expected.keys() | actual.keys()
            if k not in expected or k not in actual
            or json.dumps(expected[k], sort_keys=True) != json.dumps(actual[k], sort_keys=True)}


def compare(case, bundle):
    expected = case["expected"]
    if isinstance(bundle, InvalidRestriction):
        actual = {"grammar_rejected": True}
        return actual, field_differences(expected, actual)
    options = {"max_edges": case["max_edges"]} if "max_edges" in case else {}
    result = parse(case["input"], bundle=bundle, **options)
    diagnostic = {"code": result["diagnostic"]}
    if "token" in result or "token_index" in result:
        diagnostic.update(token=result["token"], index=result["token_index"])
    actual = {k: result[k] for k in ("tokens", "construction_status", "decision", "readings",
                                      "min_cost", "ranked_readings")}
    actual["diagnostic"] = diagnostic
    actual["witnesses"] = [{k: w[k] for k in WITNESS_FIELDS} for w in result["witnesses"]]
    differences = field_differences(expected, actual)
    if "edge_count" in case:
        cap = options.get("max_edges")
        exact = result if cap is None else parse(case["input"], bundle=bundle)
        if exact["edges"] != case["edge_count"]:
            differences["exact_edge_count"] = case["edge_count"], exact["edges"]
        expected_inserted = case["edge_count"] if cap is None else min(case["edge_count"], cap)
        if result["edges"] != expected_inserted:
            differences["inserted_edges"] = expected_inserted, result["edges"]
    return result, differences


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", "--suite", choices=SUITES, default="seed-1.0")
    args = parser.parse_args()
    cases, bundles = frozen_inputs(args.seed)
    outcomes, mismatches = Counter(), {}
    witnesses = 0
    for case in cases:
        result, differences = compare(case, bundles[case["grammar"]])
        if result.get("grammar_rejected"):
            outcomes["grammar_rejected"] += 1
        else:
            outcomes[result["diagnostic"] or result["decision"]] += 1
            witnesses += len(result["witnesses"])
        if differences:
            mismatches[case["id"]] = differences
    print(json.dumps({"cases": len(cases), "grammars": len(bundles), "witnesses": witnesses,
                      "outcomes": outcomes, "mismatches": mismatches}, sort_keys=True, indent=2))
    return bool(mismatches)


if __name__ == "__main__":
    raise SystemExit(main())
