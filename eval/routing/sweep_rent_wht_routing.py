# -*- coding: utf-8 -*-
"""Sweep the rent-WHT extractors over every corpus BEFORE the route is wired.

R31 step 2: an extractor is written narrow-by-construction and swept for collisions BEFORE
shipping, not narrowed afterwards. A wider net reaches more phrasings AND more accidental
matches; both risks are checked together.

WHAT A COLLISION COSTS HERE, so the pass/fail bar is not arbitrary. A question that is
diverted to the rent-WHT engine gets a confident, well-cited answer about withholding on
rent. If the question was actually about something else, that is a WRONG-TOPIC answer
delivered with full engine authority -- the eval_211 harm class, which is the reason the
corporate gate was not widened further on its first pass.

THE NAMED PIN IS eval_258:
    "Nalipa kodi ya pango TZS 850,000 kwa mwezi kwa ofisi, hii inaingia kwenye hesabu ya SDL?"
It contains `kodi ya pango` AND a commercial cue (`ofisi`) and is an SDL question whose
correct answer is that rent does NOT enter the SDL base (_target: extraction:wrong_base).
IT MUST NOT ROUTE. The run FAILS if it does.

R21 BOUND, stated rather than implied: this sweeps OUR corpora, which share vocabulary with
our facts by construction. A clean sweep is a LOWER BOUND on collision cost and says nothing
about paraphrase space. The authored probes below are the partial remedy and they are authored
by the same person who wrote the cues (R33), so they are not independent either.

Usage:  python eval/routing/sweep_rent_wht_routing.py
"""

import glob
import json
import os
import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
OUT = os.path.join(REPO, "eval", "results", "rent_wht_routing_sweep_2026_09_26.json")

from chike.routing import (asks_rent_withholding, rent_letting_is_commercial)  # noqa: E402

# id -> must_route. Rows whose verdict we assert explicitly.
PINS = {
    "eval_258": False,   # SDL question containing `kodi ya pango` + `ofisi`. THE pin.
}

# R17 probes. The must-NOT-route half is the half that does the work.
PROBES = [
    ("Nina nyumba kijijini nimemkodisha mfanyabiashara mdogo. Yeye anatakiwa kunikata kodi "
     "kabla ya kunilipa kodi ya pango?", True, "ext_43 -- the real question, must route"),
    ("Nikimlipa mwenye nyumba kodi ya pango ofisini, ni lazima nikate kodi kabla ya kumpa "
     "fedha?", True, "ext_44 -- second phrasing, must route"),
    ("Kiwango cha kodi ya zuio ya pango la kibiashara ni asilimia ngapi?", True,
     "the direct rate question, must route"),
    # must NOT route
    ("Nalipa kodi ya pango TZS 850,000 kwa mwezi kwa ofisi, hii inaingia kwenye hesabu ya "
     "SDL?", False, "eval_258 verbatim -- SDL question, MUST NOT route"),
    ("Kodi ya pango ninayolipa kwa ofisi yangu naweza kuikata kama gharama ya biashara?",
     False, "rent as a DEDUCTIBLE EXPENSE -- an income-tax question, not withholding"),
    ("Kodi ya pango ya ofisi yangu imepanda, nifanye nini?", False,
     "rent with no withholding sense at all"),
    ("Mshahara wa mfanyakazi wangu, kodi inakatwa vipi?", False,
     "PAYE deduction -- has the withholding verb, NO rent term"),
    ("Nalipa pango la duka langu kila mwezi. Nahitaji risiti ya EFD?", False,
     "rent + EFD -- no withholding sense"),
]


def main():
    art = {"measured": str(date.today()),
           "harness": "eval/routing/sweep_rent_wht_routing.py",
           "what_a_collision_costs": ("a diverted question receives a confident, well-cited "
                                      "answer about the WRONG topic -- the eval_211 class"),
           "r21_bound": ("swept over OUR corpora, which share vocabulary with our facts by "
                         "construction. LOWER BOUND on collision cost; says nothing about "
                         "paraphrase space."),
           "probe_failures": [], "pin_failures": [], "corpus_matches": []}

    for q, expect, why in PROBES:
        got = asks_rent_withholding(q)
        if got != expect:
            art["probe_failures"].append({"why": why, "expected": expect, "got": got,
                                          "question": q})

    corpora = sorted(glob.glob(os.path.join(REPO, "eval", "**", "*.jsonl"), recursive=True))
    scanned = 0
    for fp in corpora:
        for line in open(fp, encoding="utf-8"):
            if not line.strip():
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            q = (d.get("question_sw") or d.get("question") or d.get("instruction") or "")
            if not q:
                continue
            scanned += 1
            rid = d.get("id")
            routes = asks_rent_withholding(q)
            if rid in PINS and routes != PINS[rid]:
                art["pin_failures"].append({"id": rid, "expected_route": PINS[rid],
                                            "got": routes, "question": q[:200],
                                            "file": os.path.relpath(fp, REPO)})
            if routes:
                art["corpus_matches"].append({
                    "id": rid, "file": os.path.relpath(fp, REPO).replace("\\", "/"),
                    "question": q[:200],
                    "letting_is_commercial": rent_letting_is_commercial(q)})

    art["questions_scanned"] = scanned
    art["corpus_match_count"] = len(art["corpus_matches"])
    art["verdict"] = ("CLEAN" if not art["probe_failures"] and not art["pin_failures"]
                      else "FAILED")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(art, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print(f"questions scanned : {scanned}")
    print(f"probes            : {len(PROBES) - len(art['probe_failures'])}/{len(PROBES)} pass"
          f"  ({sum(1 for p in PROBES if not p[1])} must-NOT-route)")
    print(f"pins              : {len(PINS) - len(art['pin_failures'])}/{len(PINS)} hold")
    print(f"corpus matches    : {len(art['corpus_matches'])}")
    for m in art["corpus_matches"]:
        print(f"    {m['id']}  commercial={m['letting_is_commercial']}  {m['question'][:90]}")
    for f in art["probe_failures"] + art["pin_failures"]:
        print("  !! ", json.dumps(f, ensure_ascii=False)[:220])
    print(f"\nVERDICT: {art['verdict']}")
    print("artifact:", OUT)
    return 0 if art["verdict"] == "CLEAN" else 2


if __name__ == "__main__":
    sys.exit(main())
