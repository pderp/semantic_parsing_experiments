import argparse
from pathlib import Path

from . import GrammarError, check


def main():
    parser = argparse.ArgumentParser(description="Check typed CCG declarations")
    parser.add_argument("path", type=Path)
    parser.add_argument("--profile", choices=("seed", "kernel"), default="seed")
    args = parser.parse_args()
    try:
        grammar = check(args.path.read_text(), str(args.path), args.profile)
    except (OSError, GrammarError) as exc:
        parser.exit(1, f"{exc}\n")
    print(f"{args.profile}: {len(grammar.entries)} lexical entries, "
          f"{len(grammar.binary)} binary and {len(grammar.unary)} unary rules")


if __name__ == "__main__":
    main()
