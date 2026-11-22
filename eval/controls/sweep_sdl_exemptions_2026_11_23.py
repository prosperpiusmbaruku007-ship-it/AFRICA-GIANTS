# -*- coding: utf-8 -*-
"""BLAST RADIUS (R12c step 1, R17/R21) of the 2026-11-23 SDL-exemptions statement route: `detect_intent` over every question we hold, with the topic in the table vs removed. Rows on an unchanged route cannot have changed their answer; the changed rows are READ.
    python eval/controls/sweep_sdl_exemptions_2026_11_23.py   ->  eval/results/sweep_sdl_exemptions_2026_11_23.json"""
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
    routing._FS_TOPICS = tuple(t for t in full if t[0] != "sdl_exemptions")
    try:
        before = {q: routing.detect_intent(q) for q in qs}
    finally:
        routing._FS_TOPICS = full
    changed = [{"q": q, "src": qs[q], "before": before[q], "after": after[q]} for q in qs if before[q] != after[q]]
    n_topic = sum(1 for q in qs if routing.fixed_statement_topic(q) == "sdl_exemptions")
    print(f"{len(qs)} questions; {len(changed)} changed route; {n_topic} carry the topic")
    for c in changed:
        print(f"  {c['before']} -> {c['after']} [{c['src']}] {c['q'][:200]}")
    io.open(os.path.join(REPO, "eval", "results", "sweep_sdl_exemptions_2026_11_23.json"), "w", encoding="utf-8").write(json.dumps({"swept": len(qs), "changed": changed}, ensure_ascii=False, indent=1))

main()
