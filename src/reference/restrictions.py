"""Construct tiny grammars from a checked seed bundle and a JSON restriction."""
from dataclasses import replace
import re
from types import MappingProxyType

from src.frontend import IDENTIFIER
from .seed import make_bundle


def select(spec, field, available):
    if field not in spec:
        return available
    keys = spec[field]
    if (not isinstance(keys, list) or not all(isinstance(k, str) and k in available for k in keys)
            or len(set(keys)) != len(keys)):
        raise ValueError(f"expected distinct published {field}")
    return keys


def restrict_bundle(base, spec):
    """Clone source entries from the full base, even if their originals are excluded."""
    if not isinstance(spec, dict) or spec.keys() - {"entries", "clones", "rules", "roots", "max_tokens"}:
        raise ValueError("invalid bundle restriction")
    if not spec:
        return base
    sources = base.grammar.entries
    entries = {k: sources[k] for k in select(spec, "entries", sources)}
    recipes = {k: base.recipes[k] for k in entries}
    followers = {k: base.next_nouns[k] for k in entries if k in base.next_nouns}
    clones = spec.get("clones", [])
    if not isinstance(clones, list):
        raise ValueError("expected a list of clones")
    for clone in clones:
        if (not isinstance(clone, dict) or not {"id", "clone_of"} <= clone.keys()
                or clone.keys() - {"id", "clone_of", "tokens", "cost"}):
            raise ValueError("invalid clone declaration")
        key, source = clone["id"], clone["clone_of"]
        if (not isinstance(key, str) or not IDENTIFIER.fullmatch(key) or key in sources or key in entries
                or key in base.grammar.binary or not isinstance(source, str) or source not in sources):
            raise ValueError("invalid clone or source ID")
        original = sources[source]
        surface = clone.get("tokens", original.surface)
        if (not isinstance(surface, (tuple, list)) or not surface
                or not all(isinstance(t, str) and re.fullmatch(r"[a-z]+", t) for t in surface)):
            raise ValueError("invalid clone tokens")
        cost = clone.get("cost", original.cost)
        if type(cost) is not int or not -(2**63) <= cost < 2**63:
            raise ValueError("expected a signed 64-bit lexical cost")
        entries[key] = replace(original, surface=tuple(surface), cost=cost)
        recipes[key] = base.recipes[source]
        if source in base.next_nouns:
            followers[key] = base.next_nouns[source]

    binary = {k: base.grammar.binary[k] for k in select(spec, "rules", base.grammar.binary)}
    roots = select(spec, "roots", base.roots)
    limit = spec.get("max_tokens", base.max_tokens)
    if type(limit) is not int or not 0 <= limit <= base.max_tokens:
        raise ValueError("max_tokens must lie within the base bundle limit")
    grammar = replace(base.grammar, entries=MappingProxyType(entries), binary=MappingProxyType(binary))
    return make_bundle(grammar, recipes, followers, base.ontology_sha256, base.version, roots, limit)
