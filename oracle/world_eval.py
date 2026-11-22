#!/usr/bin/env python3
"""ClaudeOracle world-bank evaluator.  Written from the "interpretation" block of
inbox_v4/world_bank_blind_probes_v1.json and the seed-1.1 ontology only.
Python 3.14 stdlib only.

    python3 world_eval.py            # print the answers document
    python3 world_eval.py --write    # write answers_worldbank_v1.json (refuses to overwrite)

Model, as I read the interpretation block:
  * 4 entity slots (0-3), 3 event slots (0-2), 256 worlds in array order.
  * world["facts"][P] is an integer bit mask, absent = 0.
      unary P over E or V: bit j set  <=>  P holds of slot j
      binary role P(v, e): bit 4*v+e set  <=>  P holds of event v and entity e
  * names denote the entity slot given in bank["names"].
  * ForallE / ExistsE range over the 4 entity slots, ExistsV over the 3 event slots.
  * (Box phi) denotes the 256-bit vector whose bit w is the value of phi in world w
    under the SAME slot assignment; written as 64 lower-case hex digits of the
    integer with world 0 at the least significant bit.
  * (Content v (Box phi)) is true in world w  <=>  that hex string is in
    worlds[w]["content"][v].
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
INBOX = HERE / "inbox_v4"
N_ENTITY, N_EVENT = 4, 3


# ---------------------------------------------------------------- reader

def parse(text):
    """Canonical reading text -> nested lists of str."""
    toks = text.replace("(", " ( ").replace(")", " ) ").split()
    pos = 0

    def node():
        nonlocal pos
        t = toks[pos]
        pos += 1
        if t != "(":
            assert t != ")", "unbalanced"
            return t
        out = []
        while toks[pos] != ")":
            out.append(node())
        pos += 1
        return out
    tree = node()
    assert pos == len(toks), "trailing text"
    return tree


def unparse(t):
    return t if isinstance(t, str) else "(" + " ".join(unparse(x) for x in t) + ")"


# ---------------------------------------------------------------- evaluator

class Bank:
    def __init__(self, bank, ont):
        self.worlds = bank["worlds"]
        self.names = bank["names"]
        self.sig = ont["predicates"]
        self.index = {w["id"]: i for i, w in enumerate(self.worlds)}
        assert len(self.worlds) == 256 and len(self.index) == 256
        self.box_cache = {}

    def slot(self, arg, env, sort):
        """Slot denoted by a term of base sort E or V.  env: innermost binder first."""
        if arg.startswith("#"):
            s, value = env[int(arg[1:])]
            assert s == sort, ("sort mismatch", arg, s, sort)
            return value
        assert sort == "E", ("constant in event position", arg)
        return self.names[arg]

    def box_vector(self, phi, env):
        """256-bit integer: bit w = value of phi in world w under the same assignment."""
        key = (unparse(phi), tuple(env))
        if key not in self.box_cache:
            v = 0
            for w in range(len(self.worlds)):
                if self.holds(phi, w, env):
                    v |= 1 << w
            self.box_cache[key] = v
        return self.box_cache[key]

    def holds(self, t, w, env=()):
        if t == "Top":
            return True
        head = t[0]
        if head == "And":
            return self.holds(t[1], w, env) and self.holds(t[2], w, env)
        if head == "Implies":
            return (not self.holds(t[1], w, env)) or self.holds(t[2], w, env)
        if head == "Not":
            return not self.holds(t[1], w, env)
        if head in ("ForallE", "ExistsE", "ExistsV"):
            lam, sort, body = t[1]
            assert lam == "lam" and sort == head[-1], t
            domain = range(N_ENTITY if sort == "E" else N_EVENT)
            results = (self.holds(body, w, ((sort, x),) + tuple(env)) for x in domain)
            return all(results) if head == "ForallE" else any(results)
        sig = self.sig[head]
        assert len(sig) == len(t) - 1, ("arity", t)
        facts = self.worlds[w]["facts"].get(head, 0)
        if head == "Content":
            assert sig == ["V", "I"] and t[2][0] == "Box", t
            v = self.slot(t[1], env, "V")
            return hexvec(self.box_vector(t[2][1], env)) in self.worlds[w]["content"][v]
        if len(sig) == 1:
            return bool(facts >> self.slot(t[1], env, sig[0]) & 1)
        assert sig == ["V", "E"], sig
        v, e = self.slot(t[1], env, "V"), self.slot(t[2], env, "E")
        return bool(facts >> (4 * v + e) & 1)


def hexvec(v):
    return "%064x" % v


# ---------------------------------------------------------------- answers

BARE_LEAVING = "(ExistsV (lam V (And (Agent #0 #1) (Leave #0))))"  # #1 = the controller slot


def build():
    bank_bytes = (INBOX / "world_bank_v1.json").read_bytes()
    probe_bytes = (INBOX / "world_bank_blind_probes_v1.json").read_bytes()
    ont = json.loads((INBOX / "ontology.yaml").read_text("utf-8"))
    bank = Bank(json.loads(bank_bytes), ont)
    probes = json.loads(probe_bytes)
    assert probes["bank_sha256"] == hashlib.sha256(bank_bytes).hexdigest()
    answers = []
    for p in probes["probes"]:
        tree = parse(p["reading"])
        assert unparse(tree) == p["reading"]
        row = {"id": p["id"],
               "values": [{"world": wid, "value": bank.holds(tree, bank.index[wid])} for wid in p["worlds"]]}
        if p["id"] in ("Q19", "Q21"):
            body = parse(BARE_LEAVING)
            row["boxed_bare_leaving_by_controller_slot"] = [
                {"slot": s, "vector": hexvec(bank.box_vector(body, (("E", s),)))}
                for s in range(N_ENTITY)]
        answers.append(row)
    return {"format": "claudeoracle-worldbank-answers-v1", "seed": ont["version"],
            "bank_sha256": hashlib.sha256(bank_bytes).hexdigest(),
            "probes_sha256": hashlib.sha256(probe_bytes).hexdigest(),
            "ontology_sha256": hashlib.sha256((INBOX / "ontology.yaml").read_bytes()).hexdigest(),
            "vector_encoding": "64 lower-case hex digits of the 256-bit integer, world 0 = least significant bit",
            "answers": answers}


def dumps(doc):
    return json.dumps(doc, indent=1, ensure_ascii=True) + "\n"


if __name__ == "__main__":
    text = dumps(build())
    if "--write" in sys.argv:
        with open(HERE / "answers_worldbank_v1.json", "x") as fh:
            fh.write(text)
    else:
        sys.stdout.write(text)
