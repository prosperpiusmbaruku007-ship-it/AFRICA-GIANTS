# -*- coding: utf-8 -*-
"""R22/R25 pricing of D-FIDELITY-23 (46 as the sub-sector count of ONE GN 605A sector): run the guard over every stored reply, gold answer and training answer we hold and list every flag, so each can be read.
    python eval/controls/price_d23_2026_11_18.py  ->  eval/results/price_d23_2026_11_18.json"""
import glob
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, REPO)
from chike import fidelity  # noqa: E402

QK = ("question_sw", "q", "question", "prompt", "instruction", "question_en")
AK = ("answer_sw", "reply", "generated", "answer", "gold", "output", "response", "answer_en", "text")


def pairs():
    for pat in ["eval/accuracy_gate/*.jsonl", "eval/refusal_gate/*.jsonl", "eval/fidelity/**/*.jsonl", "datasets/tier1a/cleaned_pairs/*.jsonl", "datasets/tier1a/sft_shaped_pairs/*.jsonl", "datasets/tier1a/sft/*.jsonl"]:
        for f in glob.glob(os.path.join(REPO, pat), recursive=True):
            for l in io.open(f, encoding="utf-8", errors="replace"):
                try:
                    o = json.loads(l)
                except Exception:                                                # noqa: BLE001
                    continue
                if isinstance(o, dict):
                    q = next((o[k] for k in QK if isinstance(o.get(k), str)), "")
                    for k in AK:
                        if isinstance(o.get(k), str):
                            yield os.path.relpath(f, REPO).replace("\\", "/"), q, o[k]
    for f in glob.glob(os.path.join(REPO, "eval", "results", "*.json")):
        try:
            d = json.load(io.open(f, encoding="utf-8"))
        except Exception:                                                        # noqa: BLE001
            continue
        rows = d.get("rows") if isinstance(d, dict) else d
        if isinstance(rows, list):
            for r in rows:
                if isinstance(r, dict):
                    q = next((r[k] for k in QK if isinstance(r.get(k), str)), "")
                    for k in AK:
                        if isinstance(r.get(k), str):
                            yield "results/" + os.path.basename(f), q, r[k]


def main():
    n, flags, mention = 0, [], 0
    for src, q, a in pairs():
        n += 1
        if fidelity._D23_COUNT.search(a):
            mention += 1
        for s in fidelity.gn605a_subsector_count_misstated(q, a):
            flags.append({"src": src, "q": q[:200], "sentence": s[:300]})
    print(f"{n} (question, answer) texts priced; {mention} state a 46 sub-sector count; {len(flags)} flagged")
    for f in flags:
        print(f"  [{f['src']}] Q: {f['q'][:110]}\n       -> {f['sentence'][:200]}")
    json.dump({"priced": n, "state_46_subsector": mention, "flags": flags}, io.open(os.path.join(REPO, "eval", "results", "price_d23_2026_11_18.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
