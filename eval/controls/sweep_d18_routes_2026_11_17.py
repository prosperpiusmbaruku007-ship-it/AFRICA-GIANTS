# -*- coding: utf-8 -*-
"""SWEEP EVERY QUESTION WE HOLD for what the two 2026-11-17 statement routes would divert (individual income-tax return deadline; business-licence validity), so each diversion can be READ (R17/R21: a sweep over our own
corpora is a LOWER BOUND -- authored probes carry the rest). Populations: gate + refusal corpora, every stored live question, the training corpora's questions.
    python eval/controls/sweep_d18_routes_2026_11_17.py  ->  eval/results/sweep_d18_routes_2026_11_17.json"""
import glob
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, REPO)
from chike import routing  # noqa: E402

NEW = {"tin_apply_deadline", "business_licence_fee_and_validity"}
QK = ("question_sw", "q", "question", "prompt", "instruction", "question_en")


def questions():
    seen = {}
    pats = ["eval/accuracy_gate/*.jsonl", "eval/refusal_gate/*.jsonl", "eval/fidelity/**/*.jsonl", "datasets/tier1a/cleaned_pairs/*.jsonl", "datasets/tier1a/sft_shaped_pairs/*.jsonl", "datasets/tier1a/sft/*.jsonl"]
    for pat in pats:
        for f in glob.glob(os.path.join(REPO, pat), recursive=True):
            for l in io.open(f, encoding="utf-8", errors="replace"):
                try:
                    o = json.loads(l)
                except Exception:                                        # noqa: BLE001
                    continue
                if isinstance(o, dict):
                    for k in QK:
                        if isinstance(o.get(k), str) and 8 < len(o[k]) < 600:
                            seen.setdefault(o[k].strip(), os.path.relpath(f, REPO).replace("\\", "/"))
                            break
    for f in glob.glob(os.path.join(REPO, "eval", "results", "*.json")):
        try:
            d = json.load(io.open(f, encoding="utf-8"))
        except Exception:                                                # noqa: BLE001
            continue
        rows = d.get("rows") if isinstance(d, dict) else d
        if isinstance(rows, list):
            for r in rows:
                if isinstance(r, dict):
                    for k in QK:
                        if isinstance(r.get(k), str) and 8 < len(r[k]) < 600:
                            seen.setdefault(r[k].strip(), "results/" + os.path.basename(f))
                            break
    return seen


def main():
    qs = questions()
    hits = {}
    for q, src in qs.items():
        t = routing.fixed_statement_topic(q)
        if t in NEW and routing.detect_intent(q) == "fixed_statement":
            hits.setdefault(t, []).append((q, src))
    print(f"{len(qs)} distinct questions swept")
    for t in sorted(NEW):
        print(f"\n== {t}: {len(hits.get(t, []))} diverted")
        for q, src in hits.get(t, []):
            print(f"   [{src}] {q[:150]}")
    json.dump({"swept": len(qs), "hits": {t: [{"q": q, "src": s} for q, s in v] for t, v in hits.items()}}, io.open(os.path.join(REPO, "eval", "results", "sweep_d18_routes_2026_11_17.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
