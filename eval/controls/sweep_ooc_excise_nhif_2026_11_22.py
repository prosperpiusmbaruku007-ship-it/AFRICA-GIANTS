# -*- coding: utf-8 -*-
"""R17/R21 collision sweep for the 2026-11-22 OOC additions (excise duty, verb-qualified NHIF). Lists every held question containing each candidate phrase or its bare stem so each can be READ.
A lower bound only (R21): authored probes in eval/refusal_gate/ooc_excise_nhif_probes_2026_11_22.jsonl carry the rest.
    python eval/controls/sweep_ooc_excise_nhif_2026_11_22.py   ->  eval/results/sweep_ooc_excise_nhif_2026_11_22.json"""
import io, json, os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
from sweep_d18_routes_2026_11_17 import questions  # noqa: E402

CANDIDATES = ["excise duty", "ushuru wa bidhaa", "ushuru wa bizaa", "makato ya nhif", "nhif ya wafanyakazi", "nhif ya mwajiri", "nhif ya waajiriwa"]
STEMS = ["excise", "ushuru wa bi", "nhif", "bima ya afya", "bima za afya", "afya"]

def main():
    qs = questions(); rows = {"n_questions": len(qs), "candidates": {}, "stems": {}}
    for kind, terms in (("candidates", CANDIDATES), ("stems", STEMS)):
        for t in terms:
            hits = [{"q": q, "src": s} for q, s in qs.items() if t in q.lower()]
            rows[kind][t] = {"n": len(hits), "hits": hits}
            print(f"{kind[:4]} {t!r}: {len(hits)}")
            if kind == "candidates" or t in ("nhif", "ushuru wa bi", "excise"):
                for h in hits[:40]:
                    print("    ", h["src"], "|", h["q"][:150])
    io.open(os.path.join(REPO, "eval", "results", "sweep_ooc_excise_nhif_2026_11_22.json"), "w", encoding="utf-8").write(json.dumps(rows, ensure_ascii=False, indent=1))

main()
