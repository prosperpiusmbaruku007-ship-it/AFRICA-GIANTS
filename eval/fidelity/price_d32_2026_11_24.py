# -*- coding: utf-8 -*-
"""PRICE D-FIDELITY-32 (medicines / medical equipment called zero-rated) BEFORE any wiring (R22, R25). Founder's condition (2026-11-24): wire ONLY if GOLD shows 0 flags and the export / negation controls still pass; otherwise report.
Populations, each named with why: STORED = every model reply recorded anywhere under eval/results (the only real model prose; where a flag can be read against a verdict); GOLD = every answer in eval/accuracy_gate + eval/refusal_gate (a human asserted it right: a flag is the
over-breadth alarm); TRAINING = every answer in datasets/ jsonl (the prose the model learned from); INDEX = the served RAG rows (what the model is handed: a flag would mean the index itself says it).
PLANTS (R26): the three live specimens MUST flag; the controls (negation, contrast clause, export, exempt wording, English) MUST NOT. Either failure exits 1.
    python eval/fidelity/price_d32_2026_11_24.py  ->  eval/results/price_d32_2026_11_24.json
"""
import glob
import io
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from chike import fidelity  # noqa: E402

SPECIMENS = [
    "Dawa nyingi za binadamu ziko katika daraja la zero-rated (tozo 0%).",
    "Kwa mfano, vifaa tiba (zero-rated) na dawa vinaweza kudai input VAT.",
    "Medicines are zero-rated in Tanzania, so you can claim input VAT.",
    "Dawa (zero-rated) hazitozwi VAT.",
]
CONTROLS = [
    "Dawa si zero-rated; ni msamaha wa VAT.",
    "Mauzo ya nje ni zero-rated; dawa ni msamaha.",
    "Dawa zinazouzwa nje ya nchi ni zero-rated, kwa sababu bidhaa yenye msamaha na zero-rating inakuwa zero-rated.",
    "Mauzo ya nje yana tozo 0%.",
    "Dawa na vifaa tiba vilivyoidhinishwa na Waziri vimesamehewa VAT.",
    "Medicine is exempt, not zero-rated.",
    "Huduma za afya ni msamaha wa VAT, si zero-rated.",
    "Dawa zinazosafirishwa nje zina tozo 0%.",
    "Zero-rated ni mauzo ya nje; dawa hazimo.",
]


def _walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values():
            yield from _walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from _walk(v)


def _texts_of(obj, keys):
    for item in _walk(obj):
        for k in keys:
            v = item.get(k)
            if isinstance(v, str) and v.strip():
                yield k, v


def _jsonl(path):
    for n, line in enumerate(io.open(path, encoding="utf-8", errors="replace"), 1):
        if line.strip():
            try:
                yield n, json.loads(line)
            except ValueError:
                pass


def main():
    plant_fail = [t for t in SPECIMENS if not fidelity.medicines_called_zero_rated("", t)] + [t for t in CONTROLS if fidelity.medicines_called_zero_rated("", t)]
    print("plants: specimens flag %d/%d, controls clean %d/%d" % (len(SPECIMENS) - sum(t in plant_fail for t in SPECIMENS), len(SPECIMENS),
                                                                     len(CONTROLS) - sum(t in plant_fail for t in CONTROLS), len(CONTROLS)))
    for t in plant_fail:
        print("  PLANT FAILED:", t)
    pops = {"stored": [], "gold": [], "training": [], "index": []}
    for path in glob.glob(os.path.join(REPO, "eval", "results", "**", "*.json"), recursive=True):
        try:
            blob = json.load(io.open(path, encoding="utf-8"))
        except Exception:                                                 # noqa: BLE001
            continue
        for k, v in _texts_of(blob, ("generated", "reply", "answer", "output", "text")):
            pops["stored"].append((os.path.relpath(path, REPO) + "#" + k, v))
    for path in glob.glob(os.path.join(REPO, "eval", "accuracy_gate", "*.jsonl")) + glob.glob(os.path.join(REPO, "eval", "refusal_gate", "*.jsonl")):
        for n, o in _jsonl(path):
            for k in ("correct_answer_sw", "expected_answer_sw", "answer_sw", "gold_sw", "correct_answer_en", "answer_en"):
                if isinstance(o.get(k), str):
                    pops["gold"].append(("%s:%d#%s" % (os.path.basename(path), n, k), o[k]))
    for path in glob.glob(os.path.join(REPO, "datasets", "**", "*.jsonl"), recursive=True):
        for n, o in _jsonl(path):
            for k in ("answer_sw", "answer_en", "output", "response"):
                if isinstance(o.get(k), str):
                    pops["training"].append(("%s:%d#%s" % (os.path.relpath(path, REPO), n, k), o[k]))
            for m in o.get("messages") or []:
                if isinstance(m, dict) and m.get("role") == "assistant" and isinstance(m.get("content"), str):
                    pops["training"].append(("%s:%d#assistant" % (os.path.relpath(path, REPO), n), m["content"]))
    rag = json.load(io.open(os.path.join(REPO, "chike-inference", "rag_facts_text.json"), encoding="utf-8"))
    for i, t in enumerate(rag if isinstance(rag, list) else list(rag.values())):
        pops["index"].append(("index_row_%d" % i, t if isinstance(t, str) else json.dumps(t, ensure_ascii=False)))
    res = {"plants": {"specimens": len(SPECIMENS), "controls": len(CONTROLS), "failed": plant_fail}, "populations": {}}
    for name, rows in pops.items():
        assert rows, name                                                 # R20: an empty loader must fail
        flags = []
        for src, text in rows:
            for s in fidelity.medicines_called_zero_rated("", text):
                flags.append({"src": src, "sentence": s[:300]})
        seen, uniq = set(), []
        for f in flags:
            if f["sentence"] not in seen:
                seen.add(f["sentence"]); uniq.append(f)
        res["populations"][name] = {"texts": len(rows), "flags": len(flags), "distinct_sentences": len(uniq), "rows": uniq[:60]}
        print("%-9s texts=%6d flags=%4d distinct=%4d" % (name, len(rows), len(flags), len(uniq)))
        for f in uniq[:25]:
            print("   ", f["src"][-60:], "|", f["sentence"][:170])
    res["decision_rule"] = "wire ONLY if plants pass AND gold flags == 0 AND index flags == 0 AND every stored/training flag has been read"
    json.dump(res, io.open(os.path.join(REPO, "eval", "results", "price_d32_2026_11_24.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 1 if plant_fail else 0


if __name__ == "__main__":
    sys.exit(main())
