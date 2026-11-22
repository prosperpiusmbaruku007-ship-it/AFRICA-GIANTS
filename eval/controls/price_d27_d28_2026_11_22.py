# -*- coding: utf-8 -*-
"""PRICING of D-FIDELITY-27 (SDL scope by premises) and D-FIDELITY-28 (NSSF contributions tied to age 60) over every text we hold. READ every hit (R37/R39): on the fact path a hit REPLACES the whole body.
    python eval/controls/price_d27_d28_2026_11_22.py  ->  eval/results/price_d27_d28_2026_11_22.json"""
import glob, io, json, os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
from chike import fidelity  # noqa: E402


def texts():
    for f in sorted(glob.glob(os.path.join(REPO, "eval", "results", "*.json"))):
        try:
            d = json.load(io.open(f, encoding="utf-8"))
        except Exception:                                                # noqa: BLE001
            continue
        rows = d.get("rows", []) if isinstance(d, dict) else []
        for r in rows if isinstance(rows, list) else []:
            if isinstance(r, dict):
                for k in ("generated", "reply"):
                    if isinstance(r.get(k), str):
                        yield "reply:" + os.path.basename(f), r.get("question_sw") or r.get("q") or "", r[k]
    for f in sorted(glob.glob(os.path.join(REPO, "eval", "accuracy_gate", "eval_questions_00*.jsonl"))):
        for line in io.open(f, encoding="utf-8"):
            if line.strip():
                o = json.loads(line); yield "gold:" + o["id"], o.get("question_sw", ""), o.get("correct_answer_sw", "")
    for pat in ("datasets/tier1a/cleaned_pairs/*.jsonl", "datasets/tier1a/sft_shaped_pairs/*.jsonl", "datasets/tier1a/sft/*.jsonl"):
        for f in glob.glob(os.path.join(REPO, pat)):
            for line in io.open(f, encoding="utf-8", errors="replace"):
                try:
                    o = json.loads(line)
                except Exception:                                        # noqa: BLE001
                    continue
                if isinstance(o, dict) and isinstance(o.get("answer_sw"), str):
                    yield "train:" + os.path.basename(f), o.get("question_sw", ""), o["answer_sw"]


def main():
    n, hits = 0, []
    for tag, q, a in texts():
        n += 1
        for name, fn in (("D27", fidelity.sdl_scope_by_premises), ("D28", fidelity.nssf_contributions_tied_to_age_60)):
            h = fn(q, a)
            if h:
                hits.append({"rule": name, "src": tag, "q": q[:120], "flagged": h})
    print(f"{n} texts swept; {len(hits)} hits")
    for h in hits:
        print(" ", h["rule"], h["src"], "|", h["q"][:80], "|", h["flagged"])
    io.open(os.path.join(REPO, "eval", "results", "price_d27_d28_2026_11_22.json"), "w", encoding="utf-8").write(json.dumps({"swept": n, "hits": hits}, ensure_ascii=False, indent=1))

main()
