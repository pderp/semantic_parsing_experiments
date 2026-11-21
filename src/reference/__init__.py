"""Bottom-up exact seed parser. Packed nodes retain every licensed incoming edge."""
from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
from itertools import product
import re
import string

from src.frontend import binary_category
from src.semantics import NORMALIZER_VERSION, SemanticError, app, canonical, close, reading_text
from .seed import MAX_TOKENS, ROOTS, VERSION, category_text, load_seed

WHITESPACE = " \t\n\r\f\v"
LOWER = str.maketrans(string.ascii_uppercase, string.ascii_lowercase)


def tokenize(sentence):
    text = sentence.strip(WHITESPACE).removesuffix(".").rstrip(WHITESPACE).translate(LOWER)
    return re.split(r"[ \t\n\r\f\v]+", text) if text else []


@dataclass(frozen=True)
class Node:
    start: int
    end: int
    category: object


@dataclass(frozen=True)
class Edge:
    source: str
    children: tuple = ()


class EdgeBudget(Exception):
    pass


class PackedForest:
    def __init__(self, bundle, max_edges=None):
        self.bundle = bundle
        self.max_edges = max_edges
        self.edges = {}
        self.spans = defaultdict(dict)
        self.edge_count = 0

    def insert(self, node, edge):
        if node in self.edges and edge in self.edges[node]:
            return
        if self.max_edges is not None and self.edge_count >= self.max_edges:
            raise EdgeBudget
        if node not in self.edges:
            self.spans[node.start, node.end][node.category] = node
            self.edges[node] = set()
        self.edges[node].add(edge)
        self.edge_count += 1

    def build(self, tokens):
        grammar = self.bundle.grammar
        # Lexical anchoring includes the two two-token operators. Each nonempty
        # child of a binary parent is strictly shorter, so width is a topological order.
        for width in range(1, len(tokens) + 1):
            for start in range(len(tokens) - width + 1):
                end = start + width
                for entry_id in self.bundle.by_surface.get(tuple(tokens[start:end]), ()):
                    entry = grammar.entries[entry_id]
                    self.insert(Node(start, end, entry.category), Edge(entry_id))
                for split in range(start + 1, end):
                    for left in self.spans[start, split].values():
                        for right in self.spans[split, end].values():
                            for rule_id, (kind, _) in grammar.binary.items():
                                cat = binary_category(kind, left.category, right.category, grammar.depth)
                                if cat is not None:
                                    self.insert(Node(start, end, cat), Edge(rule_id, (left, right)))

    def witnesses(self, length):
        bundle = self.bundle
        grammar = bundle.grammar

        @lru_cache(maxsize=None)
        def expand(node):
            choices = []
            for edge in self.edges[node]:
                if not edge.children:
                    entry = grammar.entries[edge.source]
                    recipe = bundle.recipes[edge.source]
                    key = (0, node.start, node.end, edge.source, recipe)
                    choices.append((entry.cost, int(recipe == "tv.object-wide"), key, entry.meaning))
                    continue
                kind, _ = grammar.binary[edge.source]
                for left, right in product(*(expand(child) for child in edge.children)):
                    fn, arg = (left, right) if kind == "FA" else (right, left)
                    total = left[0] + right[0]
                    if not -(2**63) <= total < 2**63:
                        raise OverflowError("cost_overflow")
                    key = (1, edge.source, node.start, node.end, category_text(node.category),
                           "apply", (left[2], right[2]))
                    choices.append((total, left[1] + right[1], key, app(fn[3], arg[3])))
            return choices

        witnesses = []
        for cat, root in self.spans[0, length].items():
            if cat in ROOTS:
                witnesses.extend(expand(root))
        return sorted(witnesses, key=lambda witness: witness[:3])


def parse(sentence, *, max_edges=None, bundle=None):
    """Return exact reading sets and ranked witnesses for the full input."""
    bundle = load_seed() if bundle is None else bundle
    result = {"input": sentence if isinstance(sentence, str) else None, "tokens": [],
              "bundle_version": VERSION, "bundle_sha256": bundle.sha256,
              "ontology_sha256": bundle.ontology_sha256, "normalizer": NORMALIZER_VERSION,
              "readings": [], "ranked_readings": [], "witnesses": [], "min_cost": None, "nodes": 0, "edges": 0}

    def finish(status, decision, diagnostic=""):
        result.update(construction_status=status, decision=decision, diagnostic=diagnostic)
        return result

    if not isinstance(sentence, str) or (max_edges is not None and
                                         (type(max_edges) is not int or max_edges < 0)):
        return finish("error", "abstain", "invalid_request")
    tokens = result["tokens"] = tokenize(sentence)
    if not tokens:
        return finish("no_parse", "abstain", "empty_input")
    for index, token in enumerate(tokens):
        spelling_ok = re.fullmatch("[a-z]+", token)
        if not spelling_ok or token not in bundle.vocabulary:
            result.update(token_index=index, token=token)
            code = "unknown_token" if spelling_ok else "invalid_token"
            return finish("no_parse", "abstain", code)
    if len(tokens) > MAX_TOKENS:
        return finish("no_parse", "abstain", "no_root")
    forest = PackedForest(bundle, max_edges)
    try:
        forest.build(tokens)
        witnesses = []
        for cost, object_wide, key, term in forest.witnesses(len(tokens)):
            proof = close(term)
            witnesses.append({"cost": cost, "object_wide_uses": object_wide, "key": key,
                              "raw": canonical(proof.raw), "reading": reading_text(proof.normal)})
        result["witnesses"] = witnesses
        result["ranked_readings"] = list(dict.fromkeys(w["reading"] for w in witnesses))
        result["readings"] = sorted(result["ranked_readings"])
        result["min_cost"] = witnesses[0]["cost"] if witnesses else None
    except EdgeBudget:
        return finish("truncated", "abstain", "edge_budget")
    except OverflowError:
        return finish("error", "abstain", "cost_overflow")
    except SemanticError:
        return finish("error", "abstain", "engine_error")
    finally:
        result.update(nodes=len(forest.edges), edges=forest.edge_count)
    n = len(result["readings"])
    if n == 0:
        return finish("no_parse", "abstain", "no_root")
    if n > 2:
        return finish("error", "abstain", "reading_count")
    return finish("complete", "accepted" if n == 1 else "ambiguous")
