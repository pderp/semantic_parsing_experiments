"""Expand public seed recipes into finite, type-checked lexical alternatives."""
from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
from types import MappingProxyType

from src.frontend import Grammar, NP_KINDS, VP_CLASSES, check, forms
from src.semantics import ROOT, canonical

VERSION = "seed-witness-v1.1"
MAX_TOKENS = 12  # Longest seed root: quantified subject, auxiliary, control and modified embedded TV.
ROOTS = frozenset(f"S[fin,{kind}]" for kind in (*VP_CLASSES, "negative", "not-every"))


def category_text(category):
    if isinstance(category, str):
        return category
    slash, result, argument = category
    return f"({category_text(result)}{slash}{category_text(argument)})"


def sexpr(tree, parameters):
    if isinstance(tree, str):
        return parameters[tree[1:]] if tree.startswith("@") else tree
    return "(" + " ".join(sexpr(child, parameters) for child in tree) + ")"


def np(kind):
    return f"NP[{kind}]"


def vp(form, kind, subject):
    return ("\\", f"S[{form},{kind}]", np(subject))


INF = ("\\", "S[to]", np("unit"))


@dataclass(frozen=True)
class SeedBundle:
    grammar: Grammar
    recipes: object
    by_surface: object
    next_nouns: object
    vocabulary: frozenset
    ontology_sha256: str
    sha256: str

    def inventory(self):
        return inventory(self.grammar, self.recipes, self.ontology_sha256, self.next_nouns)


def inventory(grammar, recipes, ontology_hash, next_nouns):
    return {
        "version": VERSION, "ontology_sha256": ontology_hash, "depth": grammar.depth, "max_tokens": MAX_TOKENS,
        "next_nouns": dict(next_nouns),
        "roots": sorted(ROOTS), "rules": {key: [kind, "apply"] for key, (kind, _) in grammar.binary.items()},
        "entries": {key: {"tokens": entry.surface, "category": category_text(entry.category),
                          "recipe": recipes[key], "cost": entry.cost, "meaning": canonical(entry.meaning)}
                    for key, entry in sorted(grammar.entries.items())},
    }


@lru_cache(maxsize=1)
def load_seed():
    ontology_bytes = (ROOT / "spec/ontology.yaml").read_bytes()
    ontology = json.loads(ontology_bytes)
    templates = {}
    for location, declaration in forms((ROOT / "grammar/seed_recipes.metta").read_text(), "seed_recipes.metta"):
        match declaration:
            case ("recipe", str(name), body) if name not in templates:
                templates[name] = body
            case _:
                raise ValueError(f"{location}: invalid or duplicate recipe")

    declarations = [(ROOT / "grammar/kernel.metta").read_text()]
    recipes = {}

    def emit(entry_id, surface, cat, recipe, price=0, **parameters):
        meaning = sexpr(templates[recipe], parameters)
        declarations.append(f"(lex {entry_id} ({surface}) {sexpr(cat, {})} {meaning} () {price})")
        recipes[entry_id] = recipe

    for word in ontology["names"]:
        emit(f"name.{word}", word, np("unit"), "name", symbol=word)
    article = ontology["existential_surface"]
    followers = {f"det.{word}": [] for word, kind in ontology["determiners"].items() if kind == "existential"}
    for word, predicate in ontology["nouns"].items():
        emit(f"noun.{word}", word, "N", "noun", symbol=predicate)
        form = article["before_vowel"] if word[0] in article["vowel_initial_letters"] else article["otherwise"]
        followers[f"det.{form}"].append(word)
    next_nouns = MappingProxyType({key: tuple(sorted(words)) for key, words in followers.items()})
    for word, kind in ontology["determiners"].items():
        quant, join = ("ForallE", "Implies") if kind == "universal" else ("ExistsE", "And")
        emit(f"det.{word}", word, ("/", np(kind), "N"), "det", quant=quant, join=join)

    for frame_id, frame in ontology["frames"].items():
        for form, morphology in (("fin", "past"), ("bare", "bare")):
            tail = "(fn ev V (fn p P (And (Past ev) p)))" if form == "fin" else "(fn ev V (fn p P p))"
            parameters = {"tense": tail, "pred": frame["predicate"]}
            for subject in NP_KINDS if form == "fin" else ("unit",):
                prefix = f"{frame_id}.{morphology}.{subject}"
                simple = vp(form, "simple,plain", subject)
                word = frame[morphology]
                if frame["construction"] == "intransitive":
                    emit(prefix, word, simple, "iv", **parameters)
                elif frame["construction"] == "transitive":
                    for obj in NP_KINDS:
                        for scope in frame["scope"]:
                            if scope == "object-wide" and subject == obj != "unit":
                                continue
                            emit(f"{prefix}.{obj}.{scope}", word, ("/", simple, np(obj)),
                                 "tv." + scope, 10, **parameters)
                else:
                    control = ("/", vp(form, "control", subject), INF)
                    controller = {"subject": "s", "recipient": "r"}[frame["controller"]]
                    for recipient in NP_KINDS:
                        emit(f"{prefix}.{recipient}", word, ("/", control, np(recipient)),
                             "control", controller=controller, **parameters)

    for form in ("fin", "bare"):
        for subject in NP_KINDS if form == "fin" else ("unit",):
            emit(f"quickly.{form}.{subject}", "quickly",
                 ("\\", vp(form, "simple,quick", subject), vp(form, "simple,plain", subject)), "manner")
    for kind in VP_CLASSES:
        suffix = kind.replace(",", ".")
        bare = vp("bare", kind, "unit")
        if kind != "control":
            emit(f"to.{suffix}", "to", ("/", INF, bare), "infinitive")
        for subject in NP_KINDS:
            emit(f"did-not.{suffix}.{subject}", "did not",
                 ("/", vp("fin", "negative", subject), bare), "negation")
        positive = vp("fin", kind, "universal")
        emit(f"not-every.{suffix}", "not every", ("/", ("/", "S[fin,not-every]", positive), "N"),
             "not-every")

    grammar = check("\n".join(declarations), "expanded-seed.metta")
    index = defaultdict(list)
    for key, entry in sorted(grammar.entries.items()):
        index[entry.surface].append(key)
    ontology_hash = hashlib.sha256(ontology_bytes).hexdigest()
    serialized = json.dumps(inventory(grammar, recipes, ontology_hash, next_nouns), sort_keys=True, separators=(",", ":"))
    return SeedBundle(grammar, MappingProxyType(recipes),
                      MappingProxyType({surface: tuple(keys) for surface, keys in index.items()}), next_nouns,
                      frozenset(token for surface in index for token in surface), ontology_hash,
                      hashlib.sha256(serialized.encode("ascii")).hexdigest())
