"""Expand public seed recipes into finite, type-checked lexical alternatives."""
from collections import defaultdict
from dataclasses import dataclass
from functools import cached_property, lru_cache
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
    version: str
    roots: frozenset
    max_tokens: int

    def inventory(self):
        grammar = self.grammar
        result = {
            "version": self.version, "ontology_sha256": self.ontology_sha256,
            "depth": grammar.depth, "max_tokens": self.max_tokens, "roots": sorted(self.roots),
            "rules": {key: [kind, "apply"] for key, (kind, _) in grammar.binary.items()},
            "entries": {key: {"tokens": entry.surface, "category": category_text(entry.category),
                              "recipe": self.recipes[key], "cost": entry.cost, "meaning": canonical(entry.meaning)}
                        for key, entry in sorted(grammar.entries.items())},
        }
        if self.version != "seed-witness-v1":
            result["next_nouns"] = dict(self.next_nouns)
        return result

    @cached_property
    def sha256(self):
        serialized = json.dumps(self.inventory(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("ascii")).hexdigest()

    @cached_property
    def largest_absolute_cost(self):
        return max((abs(entry.cost) for entry in self.grammar.entries.values()), default=0)


def make_bundle(grammar, recipes, followers, ontology_hash, version, roots, max_tokens):
    index = defaultdict(list)
    for key, entry in sorted(grammar.entries.items()):
        index[entry.surface].append(key)
    return SeedBundle(grammar, MappingProxyType(recipes),
                      MappingProxyType({surface: tuple(keys) for surface, keys in index.items()}),
                      MappingProxyType(followers), frozenset(token for surface in index for token in surface),
                      ontology_hash, version, frozenset(roots), max_tokens)


@lru_cache(maxsize=1)
def load_seed():
    return compile_seed((ROOT / "spec/ontology.yaml").read_bytes())


def compile_seed(ontology_bytes):
    """Compile the published ontology version with the reference's checked recipes."""
    ontology = json.loads(ontology_bytes)
    version = {"seed-1.0": "seed-witness-v1", "seed-1.1": VERSION}[ontology["version"]]
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
    article = ontology.get("existential_surface")
    followers = {f"det.{word}": [] for word, kind in ontology["determiners"].items() if kind == "existential"}
    for word, predicate in ontology["nouns"].items():
        emit(f"noun.{word}", word, "N", "noun", symbol=predicate)
        if article is not None:
            form = article["before_vowel"] if word[0] in article["vowel_initial_letters"] else article["otherwise"]
            followers[f"det.{form}"].append(word)
    next_nouns = {key: tuple(sorted(words)) for key, words in followers.items() if words}
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
    return make_bundle(grammar, recipes, next_nouns, hashlib.sha256(ontology_bytes).hexdigest(),
                       version, ROOTS, MAX_TOKENS)
