"""Truth vectors for the seed-1.1 bank. Bit i denotes truth in its ith world."""
from functools import lru_cache
import hashlib
import json
from itertools import product

from src.frontend import forms, template
from src.semantics import E, V, ROOT, SemanticError, normalize, reading_text, spine

BANK_FILE = ROOT / "fixtures/world_bank_v2.json"
BANK_SHA256 = "2911d66da3d5888c34072d33b01a08587f20758948889db577c26a55ac13d0b6"
DOMAINS = {E: range(4), V: range(3)}
FULL = (1 << 256) - 1


def formula(text):
    """Parse a single closed meaning; also admit a propositional atom such as Top."""
    wrapped = list(forms("(" + text + ")", "<reading>"))
    if len(wrapped) != 1 or len(wrapped[0][1]) != 1:
        raise SemanticError("expected one reading")
    return template(wrapped[0][1][0])


class WorldBank:
    def __init__(self, bank, ontology):
        if bank["format"] not in ("seed-world-bank-v1", "seed-world-bank-v2") or len(bank["worlds"]) != 256:
            raise ValueError("unexpected finite-world bank format")
        vectors = None
        if bank["format"] == "seed-world-bank-v2":
            vectors = tuple(int(v, 16) for v in bank["content_vectors"])
        self.names = bank["names"]
        self.ids = tuple(w["id"] for w in bank["worlds"])
        self.sorts = ontology["predicates"]
        self.truth = {}
        self.content = {}
        for i, world in enumerate(bank["worlds"]):
            for name, mask in world["facts"].items():
                for bit in range(mask.bit_length()):
                    if mask & (1 << bit):
                        key = (name, bit)
                        self.truth[key] = self.truth.get(key, 0) | (1 << i)
            for event, stored in enumerate(world["content"]):
                if vectors is None:
                    payloads = (int(value, 16) for value in stored)
                else:
                    mask = int(stored, 16)
                    if mask.bit_length() > len(vectors) or len(stored) != (len(vectors) + 3) // 4:
                        raise ValueError("content mask does not fit the vector dictionary")
                    # Decode once at load. Outer assignments still pass actual vectors to Content.
                    bits = mask.to_bytes((len(vectors) + 7) // 8, "little")
                    payloads = (v for j, v in enumerate(vectors) if bits[j // 8] & (1 << (j % 8)))
                for payload in payloads:
                    key = (event, payload)
                    self.content[key] = self.content.get(key, 0) | (1 << i)

    def signature(self, reading):
        """Return the matrix vector and every Box vector at every enclosing assignment."""
        term = normalize(formula(reading) if isinstance(reading, str) else reading).normal
        reading_text(term)
        observations = {}

        def evaluate(node, env, sorts, path):
            head, args = spine(node)
            if head[0] == "var":
                return env[head[1]]
            name = head[1]
            if name == "Top":
                return FULL
            if name in self.names:
                return self.names[name]
            if name in ("ForallE", "ExistsE", "ExistsV"):
                _, sort, body = args[0]
                universal = name == "ForallE"
                value = FULL if universal else 0
                for slot in DOMAINS[sort]:
                    part = evaluate(body, (slot,) + env, (sort,) + sorts, path + (0,))
                    value = value & part if universal else value | part
                return value

            values = [evaluate(arg, env, sorts, path + (i,)) for i, arg in enumerate(args)]
            if name == "Box":
                value, = values
                observations.setdefault((path, sorts), {})[env] = value
                return value
            if name == "Content":
                return self.content.get(tuple(values), 0)
            if name == "Not":
                return FULL ^ values[0]
            if name == "Implies":
                return (FULL ^ values[0]) | values[1]
            if name == "And":
                return values[0] & values[1]
            if name not in self.sorts:
                raise SemanticError(f"unsupported finite-model symbol {name}")
            bit = values[0] if len(values) == 1 else 4 * values[0] + values[1]
            return self.truth.get((name, bit), 0)

        matrix = evaluate(term, (), (), ())
        payloads = []
        for (path, sorts), table in sorted(observations.items()):
            assignments = product(*(DOMAINS[s] for s in sorts))
            payloads.append({"path": list(path), "binder_sorts": list(sorts),
                             "vectors": [format(table[a], "064x") for a in assignments]})
        return {"matrix": format(matrix, "064x"), "payloads": payloads}

    def signature_set(self, readings):
        """Comparable matrix/payload signatures; occurrence paths are diagnostic metadata."""
        out = set()
        for reading in readings:
            sig = self.signature(reading)
            tables = tuple(sorted((tuple(t["binder_sorts"]), tuple(t["vectors"])) for t in sig["payloads"]))
            out.add((sig["matrix"], tables))
        return tuple(sorted(out))


@lru_cache(maxsize=1)
def load_bank():
    raw = (ROOT / "spec/ontology.yaml").read_bytes()
    serialized = BANK_FILE.read_bytes()
    if hashlib.sha256(serialized).hexdigest() != BANK_SHA256:
        raise ValueError("world bank digest mismatch")
    bank = json.loads(serialized)
    if hashlib.sha256(raw).hexdigest() != bank["ontology_sha256"]:
        raise ValueError("ontology digest differs from the bank")
    return WorldBank(bank, json.loads(raw))
