# -*- coding: utf-8 -*-
"""BLAST RADIUS (R12c step 1, R17/R21) of the 2026-11-22 domestic-worker/sector-wage changes: (1) the no-figure sector-wage STATEMENT topic; (2) the missing pay cues (`anayelipwa`, `wanaolipwa`, `nampa`/`nawapa`) that let figure-bearing
wage questions reach the minimum-wage engine. `detect_intent` and the fixed-statement topics over every question we hold, before vs after. Run once on the pre-change tree with --record; run on the changed tree to diff. Changed rows are READ.
    python eval/controls/sweep_wage_routing_2026_11_22.py --record   ->  eval/results/sweep_wage_routing_baseline_2026_11_22.json
    python eval/controls/sweep_wage_routing_2026_11_22.py            ->  eval/results/sweep_wage_routing_2026_11_22.json"""
import io, json, os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO); sys.path.insert(0, HERE)
from chike import routing  # noqa: E402
from sweep_d18_routes_2026_11_17 import questions  # noqa: E402
BASE = os.path.join(REPO, "eval", "results", "sweep_wage_routing_baseline_2026_11_22.json")
OUT = os.path.join(REPO, "eval", "results", "sweep_wage_routing_2026_11_22.json")


def snapshot():
    return {q: {"src": s, "intent": routing.detect_intent(q), "topics": routing.fixed_statement_topics(q)} for q, s in questions().items()}


def main():
    snap = snapshot()
    if "--record" in sys.argv:
        io.open(BASE, "w", encoding="utf-8").write(json.dumps(snap, ensure_ascii=False)); print(f"baseline recorded: {len(snap)}"); return 0
    base = json.load(io.open(BASE, encoding="utf-8"))
    changed = [{"q": q, "src": n["src"], "intent": [base[q]["intent"], n["intent"]], "topics": [base[q]["topics"], n["topics"]]}
               for q, n in snap.items() if q in base and (base[q]["intent"] != n["intent"] or base[q]["topics"] != n["topics"])]
    print(f"{len(snap)} swept (baseline {len(base)}); {len(changed)} changed")
    for c in changed:
        print(f"  {c['intent'][0]}->{c['intent'][1]} topics {c['topics'][0]}->{c['topics'][1]} [{c['src']}] {c['q'][:170]}")
    io.open(OUT, "w", encoding="utf-8").write(json.dumps({"swept": len(snap), "changed": changed}, ensure_ascii=False, indent=1)); return 0

sys.exit(main())
