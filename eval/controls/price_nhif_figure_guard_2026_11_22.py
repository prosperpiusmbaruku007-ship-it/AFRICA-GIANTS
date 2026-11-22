# -*- coding: utf-8 -*-
"""PRICING of D-FIDELITY-26 (a figure attached to NHIF is removed) over every text we hold: stored gate replies, gold answers, training answers. READ every clause it would remove (R37/R39: a repair's false positives are deleted text).
    python eval/controls/price_nhif_figure_guard_2026_11_22.py  ->  eval/results/price_nhif_figure_guard_2026_11_22.json"""
import glob, io, json, os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
from chike import fidelity  # noqa: E402


def texts():
    for f in sorted(glob.glob(os.path.join(REPO, "eval", "results", "gate_production_*.json"))):
        try:
            for r in json.load(io.open(f, encoding="utf-8")).get("rows", []):
                if isinstance(r.get("generated"), str):
                    yield "gate_reply:" + os.path.basename(f) + ":" + str(r.get("id")), r["generated"]
        except Exception:                                                # noqa: BLE001
            continue
    for f in sorted(glob.glob(os.path.join(REPO, "eval", "accuracy_gate", "eval_questions_00*.jsonl"))):
        for line in io.open(f, encoding="utf-8"):
            if line.strip():
                o = json.loads(line); yield "gold:" + o["id"], o.get("correct_answer_sw", "")
    for pat in ("datasets/tier1a/cleaned_pairs/*.jsonl", "datasets/tier1a/sft_shaped_pairs/*.jsonl"):
        for f in glob.glob(os.path.join(REPO, pat)):
            for line in io.open(f, encoding="utf-8", errors="replace"):
                try:
                    o = json.loads(line)
                except Exception:                                        # noqa: BLE001
                    continue
                if isinstance(o, dict) and isinstance(o.get("answer_sw"), str):
                    yield "train:" + os.path.basename(f), o["answer_sw"]


def main():
    n = 0; hits = []
    for tag, t in texts():
        n += 1
        out, rm = fidelity.repair_nhif_figures(t)
        if rm:
            hits.append({"src": tag, "removed": rm, "text": t[:300]})
    print(f"{n} texts swept; {len(hits)} would lose a clause")
    for h in hits:
        print(" ", h["src"], "|", h["removed"])
    io.open(os.path.join(REPO, "eval", "results", "price_nhif_figure_guard_2026_11_22.json"), "w", encoding="utf-8").write(json.dumps({"swept": n, "hits": hits}, ensure_ascii=False, indent=1))

main()
