# -*- coding: utf-8 -*-
"""BLAST RADIUS (R12c step 1, R17/R21) of the 2026-11-22 routing changes, measured BEFORE and AFTER over every question we hold (the same 8,6xx population the 2026-11-17/18 sweeps use):
  (1) `detect_intent`: the first-person applicability cues ("natakiwa kulipa") and a bare SDL THRESHOLD ask ("SDL inaanzia wafanyakazi wangapi?") that had no route;
  (2) `nssf_party` / `levy_party`: the employee cue "wa mfanyakazi" matched INSIDE "kwa mfanyakazi", and "mwajiri anatakiwa kuchangia" had no employer cue.
Run once on the pre-change tree with --record to write the baseline; run on the changed tree to diff against it. A lower bound only: authored probes carry the rest.
    python eval/controls/sweep_sdl_party_routing_2026_11_22.py --record   ->  eval/results/sweep_sdl_party_routing_baseline_2026_11_22.json
    python eval/controls/sweep_sdl_party_routing_2026_11_22.py            ->  eval/results/sweep_sdl_party_routing_2026_11_22.json  (every changed row, to be READ)"""
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

BASE = os.path.join(REPO, "eval", "results", "sweep_sdl_party_routing_baseline_2026_11_22.json")
OUT = os.path.join(REPO, "eval", "results", "sweep_sdl_party_routing_2026_11_22.json")


def snapshot():
    qs = questions()
    snap = {}
    for q, src in qs.items():
        snap[q] = {"src": src, "intent": routing.detect_intent(q), "nssf_party": routing.nssf_party(q)}
    return snap


def main():
    snap = snapshot()
    if "--record" in sys.argv:
        io.open(BASE, "w", encoding="utf-8").write(json.dumps(snap, ensure_ascii=False))
        print(f"baseline recorded: {len(snap)} questions")
        return 0
    base = json.load(io.open(BASE, encoding="utf-8"))
    changed = []
    for q, now in snap.items():
        was = base.get(q)
        if was is None:
            continue
        if was["intent"] != now["intent"] or was["nssf_party"] != now["nssf_party"]:
            changed.append({"q": q, "src": now["src"], "intent": [was["intent"], now["intent"]], "nssf_party": [was["nssf_party"], now["nssf_party"]]})
    missing = [q for q in base if q not in snap]
    print(f"{len(snap)} questions swept (baseline {len(base)}; {len(missing)} no longer present); {len(changed)} changed")
    for c in changed:
        print(f"  intent {c['intent'][0]}->{c['intent'][1]} party {c['nssf_party'][0]}->{c['nssf_party'][1]} [{c['src']}] {c['q'][:140]}")
    io.open(OUT, "w", encoding="utf-8").write(json.dumps({"swept": len(snap), "changed": changed}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
