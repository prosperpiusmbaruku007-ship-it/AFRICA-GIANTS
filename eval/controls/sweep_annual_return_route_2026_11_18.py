# -*- coding: utf-8 -*-
"""Blast radius of the 2026-11-18 annual-return statement route (R12c step 1): every question we hold that the new route would divert, so each can be READ (R17/R21: a lower bound; authored probes carry the rest).
    python eval/controls/sweep_annual_return_route_2026_11_18.py  ->  eval/results/sweep_annual_return_route_2026_11_18.json"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, HERE)
from chike import routing  # noqa: E402
from sweep_d18_routes_2026_11_17 import questions  # noqa: E402

NEW = "brela_annual_return_deadline"


def main():
    qs = questions()
    hits = [(q, s) for q, s in qs.items() if routing.fixed_statement_topic(q) == NEW and routing.detect_intent(q) == "fixed_statement"]
    # a question that mentions the subject at all, diverted or not: the population the route's vetoes had to decide
    near = [(q, s) for q, s in qs.items() if "annual return" in q.lower() and (q, s) not in hits]
    print(f"{len(qs)} distinct questions swept; {len(hits)} diverted; {len(near)} mention 'annual return' and were NOT diverted")
    for q, s in hits:
        print(f"  DIVERTED [{s}] {q[:170]}")
    for q, s in near:
        print(f"  kept     [{s}] {q[:170]}")
    json.dump({"swept": len(qs), "diverted": [{"q": q, "src": s} for q, s in hits], "mention_not_diverted": [{"q": q, "src": s} for q, s in near]},
              io.open(os.path.join(REPO, "eval", "results", "sweep_annual_return_route_2026_11_18.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
