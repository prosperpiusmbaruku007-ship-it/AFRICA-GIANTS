# -*- coding: utf-8 -*-
"""BLAST RADIUS (R12c step 1, R17/R21) of the 2026-11-23 SDL-PAYER statement route: `detect_intent` over every question we hold, with the topic in the table vs removed; and the exemptions route's membership
with and without the payer-side vetoes that were added to it (so the second change is measured, not assumed).
    python eval/controls/sweep_sdl_payer_2026_11_23.py   ->  eval/results/sweep_sdl_payer_2026_11_23.json"""
import io, json, os, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO); sys.path.insert(0, HERE)
from chike import routing  # noqa: E402
from sweep_d18_routes_2026_11_17 import questions  # noqa: E402

NEW_VETO = "(?<![a-z])mshahara|nimeajiriwa|"   # the head of the alternatives appended to the exemptions veto

def main():
    qs = questions()
    after = {q: routing.detect_intent(q) for q in qs}
    full = routing._FS_TOPICS
    routing._FS_TOPICS = tuple(t for t in full if t[0] != "sdl_payer")
    try:
        before = {q: routing.detect_intent(q) for q in qs}
    finally:
        routing._FS_TOPICS = full
    changed = [{"q": q, "src": qs[q], "before": before[q], "after": after[q]} for q in qs if before[q] != after[q]]
    payer = [q for q in qs if routing.fixed_statement_topic(q) == "sdl_payer"]
    ex_now = {q for q in qs if routing.fixed_statement_topic(q) == "sdl_exemptions"}
    # exemptions membership WITHOUT the new vetoes: strip the appended line from the veto
    old = []
    for n, c, nd, v in full:
        if n == "sdl_exemptions":
            i = v.pattern.index(routing._SDL_PAYER_ASK.pattern)
            j = i + len(routing._SDL_PAYER_ASK.pattern) + 1   # + the "|" that follows it
            v = re.compile(v.pattern[:i] + v.pattern[j:], v.flags)
        old.append((n, c, nd, v))
    routing._FS_TOPICS = tuple(old)
    try:
        ex_old = {q for q in qs if routing.fixed_statement_topic(q) == "sdl_exemptions"}
    finally:
        routing._FS_TOPICS = full
    lost = sorted(ex_old - ex_now)
    both = [q for q in qs if len([t for t in routing.fixed_statement_topics(q) if t in ("sdl_payer", "sdl_exemptions")]) > 1]
    print(f"{len(qs)} questions; {len(changed)} changed route (payer topic in/out); {len(payer)} carry sdl_payer; exemptions {len(ex_old)} -> {len(ex_now)} ({len(lost)} lost to the new vetoes); both-topics {len(both)}")
    for c in changed:
        print(f"  {c['before']} -> {c['after']} [{c['src']}] {c['q'][:200]}")
    for q in lost:
        print(f"  EXEMPTIONS LOST: {q[:200]}")
    for q in both:
        print(f"  BOTH: {q[:200]}")
    io.open(os.path.join(REPO, "eval", "results", "sweep_sdl_payer_2026_11_23.json"), "w", encoding="utf-8").write(json.dumps({"swept": len(qs), "changed": changed, "exemptions_lost": lost, "both": both}, ensure_ascii=False, indent=1))

main()
