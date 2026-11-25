# -*- coding: utf-8 -*-
"""PRICE THE TWO 2026-11-25 MEDICINES GUARD CHANGES BEFORE THEY GO ANYWHERE (R22/R25; LOCAL ONLY, nothing pushed or deployed):
  D-FIDELITY-32b  negation scope: a negation governs only the zero-rated token it is ADJACENT to, not the whole clause (the live miss: "...kuwa zero-rated (msamaha wa VAT) au exempt (si zero-rated)").
  D-FIDELITY-33   medicines taxed at the standard rate (18%) or a VAT amount computed on a medicines amount (the live "Dawa za TZS 5,000,000 ... kiwango cha VAT ni 18%").
Populations, each WITH ITS QUESTION (D-FIDELITY-33 needs it): STORED = every (question, reply) pair recorded under eval/results; GOLD = every (question, gold answer) in eval/accuracy_gate + eval/refusal_gate; TRAINING = every (question, answer) pair under datasets/; INDEX = the prospective 224 rows (no question).
OLD = the D-FIDELITY-32 that is LIVE (chike/fidelity.py at git ff68073), loaded from git, so the diff is code against code. PLANTS (R26): the live specimens MUST flag, the controls MUST NOT, both directions, or the run exits 1.
    python eval/fidelity/price_d32b_d33_2026_11_25.py  ->  eval/results/price_d32b_d33_2026_11_25.json"""
import glob
import io
import json
import os
import subprocess
import sys
import types

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from chike import fidelity as NEW  # noqa: E402


def _old_module(ref="ff68073"):
    src = subprocess.run(["git", "show", f"{ref}:chike/fidelity.py"], cwd=REPO, capture_output=True, check=True).stdout.decode("utf-8")
    mod = types.ModuleType("chike._fidelity_old")
    mod.__package__ = "chike"
    mod.__file__ = os.path.join(REPO, "chike", "_fidelity_old.py")
    exec(compile(src, mod.__file__, "exec"), mod.__dict__)
    return mod


OLD = _old_module()
Q_LIVE = "Dawa za TZS 5,000,000 nimeuza, VAT ni ngapi?"
SPECIMENS = [   # (question, body, which detector must flag)
    ("Duka la dawa linatakiwa kusajili VAT, na dawa zinatozwa VAT gani?", "Dawa zinaweza kuwa zero-rated (msamaha wa VAT) au exempt (si zero-rated).", "d32"),
    ("Dawa zinatozwa VAT?", "Dawa nyingi za binadamu ziko katika daraja la zero-rated (tozo 0%).", "d32"),
    (Q_LIVE, "Kwa dawa zenye thamani ya TZS 5,000,000, kiwango cha VAT ni 18%.", "d33"),
    (Q_LIVE, "VAT itakuwa TZS 900,000.", "d33"),
    ("Dawa zinatozwa VAT?", "Dawa zinatozwa VAT ya asilimia 18.", "d33"),
]
CONTROLS = [
    ("x", "Dawa si zero-rated; ni msamaha wa VAT."), ("x", "Dawa si za zero-rated."), ("x", "Medicine is exempt, not zero-rated."), ("x", "Dawa hazitozwi 0% bali ni msamaha."),
    ("x", "Mauzo ya nje ni zero-rated; dawa ni msamaha."), ("x", "Dawa zinazouzwa nje ya nchi ni zero-rated."),
    (Q_LIVE, "Dawa ni msamaha wa VAT, hakuna VAT inayotozwa."), (Q_LIVE, "VAT ya kawaida ni 18%, lakini dawa ni msamaha."), (Q_LIVE, "Dawa si 18%; ni msamaha."),
    ("VAT ni asilimia ngapi kwa bidhaa za kawaida?", "Kiwango cha kawaida cha VAT ni 18%."), ("Biashara ya nguo, VAT ni ngapi?", "VAT ni 18% ya TZS 1,000,000 = TZS 180,000."),
    ("x", "Mauzo ya dawa nje ya nchi: VAT ni 18%?"),
    ("Duka la dawa linatakiwa kusajili VAT, na dawa zinatozwa VAT gani?", "Duka la dawa lenye mauzo ya TZS 200M/miezi 12 au TZS 100M/miezi 6 linasajili VAT."),   # a registration THRESHOLD is not a VAT amount
]


def flag(mod, q, b, which):
    if which == "d32":
        return bool(mod.medicines_called_zero_rated(q, b))
    f = getattr(mod, "medicines_taxed_at_standard_rate", None)
    return bool(f(q, b)) if f else False


def _walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values():
            yield from _walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from _walk(v)


def pairs_stored():
    for path in glob.glob(os.path.join(REPO, "eval", "results", "**", "*.json"), recursive=True):
        try:
            blob = json.load(io.open(path, encoding="utf-8"))
        except Exception:                                                  # noqa: BLE001
            continue
        for it in _walk(blob):
            q = next((it[k] for k in ("question", "question_sw", "q", "instruction") if isinstance(it.get(k), str)), "")
            r = next((it[k] for k in ("generated", "reply", "answer", "output") if isinstance(it.get(k), str) and it[k].strip()), "")
            if r:
                yield os.path.relpath(path, REPO).replace("\\", "/"), q, r


def _jsonl(path):
    for n, line in enumerate(io.open(path, encoding="utf-8", errors="replace"), 1):
        if line.strip():
            try:
                yield n, json.loads(line)
            except ValueError:
                pass


def pairs_gold():
    for path in glob.glob(os.path.join(REPO, "eval", "accuracy_gate", "*.jsonl")) + glob.glob(os.path.join(REPO, "eval", "refusal_gate", "*.jsonl")):
        for n, o in _jsonl(path):
            q = o.get("question_sw") or o.get("question") or ""
            for k in ("correct_answer_sw", "expected_answer_sw", "answer_sw", "gold_sw", "correct_answer_en", "answer_en"):
                if isinstance(o.get(k), str):
                    yield "%s:%d#%s" % (os.path.basename(path), n, k), q, o[k]


def pairs_training():
    for path in glob.glob(os.path.join(REPO, "datasets", "**", "*.jsonl"), recursive=True):
        for n, o in _jsonl(path):
            q = o.get("question_sw") or o.get("instruction") or ""
            for k in ("answer_sw", "answer_en", "output", "response"):
                if isinstance(o.get(k), str):
                    yield "%s:%d#%s" % (os.path.relpath(path, REPO).replace("\\", "/"), n, k), q, o[k]


def pairs_index():
    import precompute_rag_embeddings as p
    texts, keys, _ = p.build_fact_texts()
    for i, t in enumerate(texts):
        yield "index_row_%d(%s)" % (i, keys[i]), "", t


def main():
    plant_fail = []
    for q, b, which in SPECIMENS:
        if not flag(NEW, q, b, which):
            plant_fail.append(("SPECIMEN NOT FLAGGED", which, b))
    for q, b in CONTROLS:
        if flag(NEW, q, b, "d32") or flag(NEW, q, b, "d33"):
            plant_fail.append(("CONTROL FLAGGED", q, b))
    # the OLD guard must MISS the live neg-scope specimen (else this change fixes nothing)
    if flag(OLD, SPECIMENS[0][0], SPECIMENS[0][1], "d32"):
        plant_fail.append(("OLD ALREADY FLAGGED THE LIVE MISS", "", SPECIMENS[0][1]))
    print("plants: %d specimens, %d controls, failures %d" % (len(SPECIMENS), len(CONTROLS), len(plant_fail)))
    for f in plant_fail:
        print("  PLANT FAILED:", f)
    res = {"plants": {"failed": [list(map(str, f)) for f in plant_fail]}, "populations": {}}
    for name, gen in (("stored", pairs_stored), ("gold", pairs_gold), ("training", pairs_training), ("index", pairs_index)):
        n, rows = 0, []
        for src, q, text in gen():
            n += 1
            o32, n32 = flag(OLD, q, text, "d32"), flag(NEW, q, text, "d32")
            n33 = flag(NEW, q, text, "d33")
            if o32 or n32 or n33:
                rows.append({"src": src, "q": q[:140], "reply": text[:260], "old_d32": o32, "new_d32": n32, "new_d33": n33})
        assert n > 0, name                                                   # R20
        seen, uniq = set(), []
        for r in rows:
            k = (r["q"], r["reply"])
            if k not in seen:
                seen.add(k)
                uniq.append(r)
        gained = [r for r in uniq if r["new_d32"] and not r["old_d32"]]
        lost = [r for r in uniq if r["old_d32"] and not r["new_d32"]]
        d33 = [r for r in uniq if r["new_d33"]]
        res["populations"][name] = {"pairs": n, "distinct_flagged": len(uniq), "d32_gained_vs_live": len(gained), "d32_lost_vs_live": len(lost), "d33_flags": len(d33), "rows": uniq[:80]}
        print("%-9s pairs=%6d distinct flagged=%3d | D32 gained vs live %2d, lost %2d | D33 %2d" % (name, n, len(uniq), len(gained), len(lost), len(d33)))
        for r in gained + lost + d33:
            tag = "GAINED" if r in gained else "LOST" if r in lost else "D33"
            print("   %-6s %s | Q: %s | %s" % (tag, r["src"][-48:], r["q"][:60], r["reply"][:150]))
    res["decision_rule"] = "wire ONLY if plants pass AND gold flags == 0 for BOTH detectors AND index flags == 0 AND every stored/training gain and D33 flag has been READ and is a genuine defect"
    json.dump(res, io.open(os.path.join(REPO, "eval", "results", "price_d32b_d33_2026_11_25.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 1 if plant_fail else 0


if __name__ == "__main__":
    sys.exit(main())
