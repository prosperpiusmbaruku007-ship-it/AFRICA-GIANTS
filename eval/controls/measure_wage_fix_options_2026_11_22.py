# -*- coding: utf-8 -*-
"""READ-ONLY sizing of the two candidate fixes for the mining-vs-energy minimum-wage miss (PROGRESS 5 OPEN, 4ba). Nothing here changes behaviour.
  OPTION B (a model-free sector-wage statement route): which questions we hold are a minimum-wage question with NO wage figure that names a GN 605A sector?
  OPTION A (a guard): among stored replies to such questions, how many state a schedule monthly figure that belongs to a DIFFERENT sector than the one asked about?
    python eval/controls/measure_wage_fix_options_2026_11_22.py  ->  eval/results/wage_fix_options_2026_11_22.json"""
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, HERE)
from chike import routing  # noqa: E402
from chike.rules_engine import wage_schedule as ws  # noqa: E402
from sweep_d18_routes_2026_11_17 import questions  # noqa: E402

# the cue the resolver LACKS today for the two sectors of the founding miss ("sekta ya madini" / "sekta ya nishati"); added here only to size what adding it would reach
EXTRA = [(re.compile(r"\bsekta ya madini\b"), 10), (re.compile(r"\bsekta ya nishati\b"), 7)]
FIG = re.compile(r"\d{1,3}(?:,\d{3})+")
MONTHLY = {}
for r in ws.SCHEDULE:
    MONTHLY.setdefault(int(r[-1]), set()).add(r[0])          # monthly figure -> the sector(s) that own it


def sector_of(q):
    kind, val = ws.resolve(q)
    if kind in ("sector", "row"):
        return val if kind == "sector" else (val[0] if isinstance(val, (tuple, list)) else val)
    for pat, no in EXTRA:
        if pat.search(q.lower()):
            return no
    return None


def main():
    qs = questions()
    mw = [q for q in qs if any(c in q.lower() for c in routing._MIN_WAGE_CUES)]
    nofig = [q for q in mw if not routing._has_money_magnitude(q.lower())]
    with_sector_now = [q for q in nofig if ws.resolve(q)[0] in ("sector", "row")]
    with_sector_extra = [q for q in nofig if sector_of(q) is not None]
    print(f"{len(qs)} questions; {len(mw)} carry a minimum-wage cue; {len(nofig)} of those carry NO wage figure")
    print(f"OPTION B reach: {len(with_sector_now)} would divert on today's resolver cues; {len(with_sector_extra)} if 'sekta ya madini/nishati' cues are added")
    for q in with_sector_extra:
        print("   B-divert:", q[:150])
    # OPTION A: stored replies (eval/results rows) whose question is a no-figure minimum-wage question naming a sector
    wanted = {q: sector_of(q) for q in with_sector_extra}
    bad, seen = [], 0
    import glob
    for f in glob.glob(os.path.join(REPO, "eval", "results", "*.json")):
        try:
            d = json.load(io.open(f, encoding="utf-8"))
        except Exception:                                            # noqa: BLE001
            continue
        rows = d.get("rows") if isinstance(d, dict) else d
        for r in rows if isinstance(rows, list) else []:
            if not isinstance(r, dict):
                continue
            q = next((r[k] for k in ("q", "question", "question_sw") if isinstance(r.get(k), str)), None)
            rep = next((r[k] for k in ("reply", "generated", "answer") if isinstance(r.get(k), str)), None)
            if q in wanted and rep:
                seen += 1
                figs = {int(x.replace(",", "")) for x in FIG.findall(rep)}
                owned = {x for x in figs if x in MONTHLY}
                wrong = {x for x in owned if wanted[q] not in MONTHLY[x]}
                if wrong:
                    bad.append({"src": os.path.basename(f), "q": q, "figures_of_other_sectors": sorted(wrong), "asked_sector": wanted[q], "reply": rep[:300]})
    print(f"OPTION A population: {seen} stored replies to those questions; {len(bad)} state a schedule figure belonging to a different sector")
    for b in bad:
        print("   A-flag:", b["src"], b["q"][:80], b["figures_of_other_sectors"], "|", b["reply"][:140])
    json.dump({"questions": len(qs), "min_wage_cue": len(mw), "no_figure": len(nofig), "B_today": with_sector_now, "B_with_extra_cues": with_sector_extra,
               "A_replies_seen": seen, "A_flags": bad}, io.open(os.path.join(REPO, "eval", "results", "wage_fix_options_2026_11_22.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
