# -*- coding: utf-8 -*-
"""RENT CONDITIONAL-LINE SWEEP (2026-11-26). READ-ONLY. Over every corpus question: those that route to rent_wht (the route itself is NOT changed by this build),
split into WITH the conditional "Ikiwa wewe ni wakala wa kuzuia: 10% × X = Y" line and WITHOUT; plus every question that has exactly one plausible amount and a rent word
but is DECLINED by the proximity / not-a-rent-figure guards. Every row is printed: read each (R12c). Also asserts the R44 paragraph is gone from every rendered working.
  python eval/routing/sweep_rent_amount_line_2026_11_26.py -> eval/results/sweep_rent_amount_line_2026_11_26.json"""
import glob
import io
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
from chike import routing, swahili_numbers as swn  # noqa: E402
from chike.rules_engine import rent_wht_statement  # noqa: E402
from chike.rules_engine import rent_wht as rw  # noqa: E402

OUT = os.path.join(REPO, "eval", "results", "sweep_rent_amount_line_2026_11_26.json")
KEYS = ("question_sw", "question", "q", "instruction", "prompt", "text")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    seen, qs = set(), []
    for f in sorted(glob.glob(os.path.join(REPO, "eval", "**", "*.jsonl"), recursive=True) + glob.glob(os.path.join(REPO, "datasets", "**", "*.jsonl"), recursive=True)):
        for ln in io.open(f, encoding="utf-8", errors="replace"):
            try:
                o = json.loads(ln)
            except Exception:
                continue
            if isinstance(o, dict):
                q = next((o[k] for k in KEYS if isinstance(o.get(k), str) and o[k].strip()), None)
                if q and q not in seen:
                    seen.add(q)
                    qs.append((os.path.relpath(f, REPO).replace("\\", "/"), o.get("id") or "", q))
    art = {"population": len(qs), "routed": [], "declined_single_figure": [], "r44_violations": []}
    for f, i, q in qs:
        if routing.detect_intent(q) == "rent_wht":
            amt = rw.rent_amount(q)
            w = rent_wht_statement(letting_is_commercial=routing.rent_letting_is_commercial(q), rent_amount=amt).working
            if "4(b)(ii)" in w or "Cap." in w:
                art["r44_violations"].append(q)
            art["routed"].append({"file": f, "id": i, "question": q, "amount": None if amt is None else str(amt), "line": w[w.find(rw.AMOUNT_BEARING_MARKER):] if amt is not None else None})
        else:
            ps = [a for a in swn.parse_amounts(q) if a >= swn.MIN_PLAUSIBLE_AMOUNT]
            if len(ps) == 1 and rw._RENT_WORD.search(q) and rw.rent_amount(q) is None:
                art["declined_single_figure"].append({"file": f, "id": i, "question": q})
    json.dump(art, io.open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    w = [r for r in art["routed"] if r["amount"]]
    print(f"population {len(qs)} | routed to rent_wht {len(art['routed'])} | WITH the line {len(w)} | R44 violations {len(art['r44_violations'])} | single-figure rent-word questions declined {len(art['declined_single_figure'])}")
    for r in art["routed"]:
        print(f"  ROUTED {'LINE' if r['amount'] else 'stmt'} {r['file']} {r['id']} | {r['question'][:100]} | {r['line'] or ''}")
    for r in art["declined_single_figure"]:
        print(f"  DECLINED {r['file']} {r['id']} | {r['question'][:120]}")
    return 1 if art["r44_violations"] else 0


if __name__ == "__main__":
    sys.exit(main())
