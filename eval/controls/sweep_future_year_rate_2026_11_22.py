# -*- coding: utf-8 -*-
"""BLAST RADIUS (R12c step 1, R17/R21) of the 2026-11-22 future-year-rate route: `detect_intent` over every question we hold, with the topic in the table vs removed (the exact prior topic-selection state). Rows on an unchanged route cannot have
changed their answer; the changed rows are READ. A lower bound only (R21): the founding row is the only one of ~8,600 held that carries a year >= 2027 with a rate word, so authored probes carry the rest.
    python eval/controls/sweep_future_year_rate_2026_11_22.py   ->  eval/results/sweep_future_year_rate_2026_11_22.json"""
import io, json, os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO); sys.path.insert(0, HERE)
from chike import routing  # noqa: E402
from sweep_d18_routes_2026_11_17 import questions  # noqa: E402

def main():
    qs = questions()
    after = {q: routing.detect_intent(q) for q in qs}
    full = routing._FS_TOPICS
    routing._FS_TOPICS = tuple(t for t in full if t[0] != "future_year_rate")
    try:
        before = {q: routing.detect_intent(q) for q in qs}
    finally:
        routing._FS_TOPICS = full
    changed = [{"q": q, "src": qs[q], "before": before[q], "after": after[q]} for q in qs if before[q] != after[q]]
    n_topic = sum(1 for q in qs if routing.fixed_statement_topic(q) == "future_year_rate")
    print(f"{len(qs)} questions; {len(changed)} changed route; {n_topic} carry the topic")
    for c in changed:
        print(f"  {c['before']} -> {c['after']} [{c['src']}] {c['q'][:200]}")
    io.open(os.path.join(REPO, "eval", "results", "sweep_future_year_rate_2026_11_22.json"), "w", encoding="utf-8").write(json.dumps({"swept": len(qs), "changed": changed}, ensure_ascii=False, indent=1))

main()
