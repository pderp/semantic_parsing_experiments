"""Compare public parser outputs using the independent oracle's process interface."""
import json
from pathlib import Path
import subprocess
import sys

from src.reference import parse
from .test_seed import public_variants

ROOT = Path(__file__).resolve().parents[2]


def main():
    witnesses = 0
    sentences = list(public_variants())
    for sentence in sentences:
        raw = subprocess.check_output([sys.executable, "oracle_enum.py", sentence], cwd=ROOT / "oracle")
        other = json.loads(raw)
        result = parse(sentence)
        for field in ("tokens", "construction_status", "decision", "readings"):
            if result[field] != other[field]:
                raise ValueError(f"{field} mismatch for {sentence!r}")
        local = [(w["cost"], w["object_wide_uses"], w["reading"]) for w in result["witnesses"]]
        independent = [(w["cost"], w["object_wide_uses"], w["meaning"]) for w in other["witnesses"]]
        if local != independent:
            raise ValueError(f"ranked witness cost, scope or reading mismatch for {sentence!r}")
        witnesses += len(local)
    print(f"Matched tokens, status, decision and reading sets on {len(sentences)} public variants.")
    print(f"Matched {witnesses} ranked witnesses on cost, object-wide count and canonical reading.")


if __name__ == "__main__":
    main()
