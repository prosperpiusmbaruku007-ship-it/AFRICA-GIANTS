# -*- coding: utf-8 -*-
"""SWEEP (R17) for the negated-premise / bound-amount defect, 2026-11-12.

THE DEFECT: "Mauzo yangu bado hayajafika TZS 200 milioni ... ninaweza kusajili VAT kwa hiari?" is answered
"Ndiyo, unatakiwa kujisajili VAT. Mauzo yako ya TZS 200,000,000 ... yamefikia" -- the engine reads the
THRESHOLD named inside a negated premise as the user's turnover. Same in scale-first ("TZS milioni 200").

WHAT THIS ENUMERATES (the whole population, not a sample): every committed question string that routes to
a turnover-taking engine (vat_registration, presumptive) AND carries a bound cue shortly before its amount.
For each: the cue, the amount, and the engine's CURRENT answer -- so every row can be read, and the fix is
judged against rows that exist rather than rows I imagine.

Strings are the same population as sweep_parser_scale_order_2026_11_12 (every committed corpus + test
literals). Output: eval/results/sweep_bound_premise_2026_11_12.json
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)
sys.path.insert(0, HERE)
import sweep_parser_scale_order_2026_11_12 as sw                     # noqa: E402
from chike import routing, swahili_numbers as swn                   # noqa: E402
from chike.orchestrator import ModelBackend, Orchestrator            # noqa: E402

OUT = os.path.join(REPO, "eval", "results", "sweep_bound_premise_2026_11_12.json")

# DELIBERATELY WIDE for the sweep: the point is to SEE the population, then narrow on evidence.
UPPER = re.compile(
    r"haya?ja(?:fika|fikia|vuka|zidi)|haija(?:fika|fikia|vuka|zidi)|haya?fiki|haya?zidi|haizidi|"
    r"sija(?:fika|fikia|fikisha|vuka|zidi)|siku?fiki|yasiyozidi|isiyozidi|chini\s+ya|pungufu\s+ya|"
    r"not\s+yet\s+reach|have\s*n.?t\s+reached|has\s*n.?t\s+reached|haven.?t\s+reached|below|under|less\s+than|"
    r"not\s+(?:yet\s+)?(?:reached|exceed)", re.IGNORECASE)
LOWER = re.compile(
    r"zaidi\s+ya|yamezidi|imezidi|nimezidi|yamevuka|nimevuka|imevuka|above|over|more\s+than|exceed", re.IGNORECASE)


class _Silent(ModelBackend):
    def generate(self, prompt, params=None):
        return ""


def main():
    qs, _ = sw.corpus()
    orch = Orchestrator(_Silent(), retriever=lambda x: [], ooc_phrases=[], in_scope_phrases=[])
    rows = []
    for q in qs:
        if len(q) > 400 or "\n\n" in q:
            continue
        try:
            intent = routing.detect_intent(q)
        except Exception:                                            # noqa: BLE001
            continue
        if intent not in ("vat_registration", "presumptive"):
            continue
        located = [(p, int(a)) for p, a in swn.parse_amounts_located(q) if a >= swn.MIN_PLAUSIBLE_AMOUNT]
        if len(located) != 1:
            continue
        pos, amt = located[0]
        window = q[max(0, pos - 45):pos]
        up, lo = UPPER.search(window), LOWER.search(window)
        if not (up or lo):
            continue
        try:
            ans = orch.answer(q).text
        except Exception as e:                                       # noqa: BLE001
            ans = f"ERROR {type(e).__name__}"
        rows.append({"q": q, "intent": intent, "amount": amt, "bound": "upper" if up else "lower",
                     "cue": (up or lo).group(0), "answer": ans})
    json.dump(rows, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"strings {len(qs)} | turnover-engine questions with a bound cue before the sole amount: {len(rows)}")
    return rows


if __name__ == "__main__":
    main()
