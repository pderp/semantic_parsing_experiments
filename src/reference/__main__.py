"""Parse one sentence or print the complete public seed inventory as JSON."""
import argparse
import json

from . import load_seed, parse


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("sentence", nargs="?")
    choice.add_argument("--bundle", action="store_true")
    parser.add_argument("--max-edges", type=int)
    args = parser.parse_args()
    result = load_seed().inventory() if args.bundle else parse(args.sentence, max_edges=args.max_edges)
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))


if __name__ == "__main__":
    main()
