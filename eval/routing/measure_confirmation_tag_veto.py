# -*- coding: utf-8 -*-
"""WHY ext_56 REACHED NO ENGINE, AND THEREFORE WHY NO FIDELITY GUARD COULD FIRE ON IT.

THE FINDING. `_THRESHOLD_ASK_VETO` (chike/routing.py:587) exists to keep a question that asks
what a threshold IS on the fact path -- "kizingiti cha mauzo cha ... ni TZS ngapi". One of its
limbs is `\\bsivyo\\s*\\?`, the Swahili CONFIRMATION TAG ("..., sivyo?" = "..., right?"). A
confirmation tag is not a threshold ask. It is the marker of a FALSE-PREMISE question, which is
the highest-consequence shape in the extended probe set.

So on ext_56 -- "Mauzo yangu yamefika milioni mia moja na kumi kwa miezi sita. Bado sijafika
kiwango cha kujisajili VAT, sivyo?" -- the veto fires on `sivyo?`, the VAT/EFD arm is skipped,
the question falls to the fact path, and the model replies "Ndiyo, bado hujafika kiwango cha
kujisajili VAT" -- confirming the false premise to a trader who is liable.

BOTH ENGINE INPUTS WERE AVAILABLE. swn.sole_plausible_amount reads 110,000,000 from the spoken
numeral, routing.turnover_period reads `six_month`, and vat_registration(110_000_000,
'six_month') returns "Ndiyo, unatakiwa kujisajili VAT ... usajili ni wa LAZIMA." The right
answer was one routing decision away.

WHAT THIS CORRECTS IN THE RECORD. The 2026-09-23 adjudication records ext_56 as
`cause: "model"`, and the PROGRESS.md write-up concludes that detecting this shape "requires ...
a different rule shape from anything now built." The GUARD half of that is exactly right and is
not disturbed here: every D-FIDELITY rule compares figures, this reply asserts none, and the
wrong figure lives in the QUESTION. But the reply only had to be judged because no engine ran,
and no engine ran because of this veto limb. The cause is at least as much ROUTING as model.

⚠️ WHY THE CLEAN NUMBER BELOW IS NOT A LICENCE TO SHIP THE ONE-LINE FIX. Narrowing this limb
WIDENS a compute route, so it owes R17 step 2 (authored adversarial probes, not just this
sweep) before anything changes. And there is a second, independent hazard the sweep cannot see:
_answer_vat_registration does NOT call agree_with_negated_premise, which exists precisely
because a verdict written for the plain frame opens with the wrong polarity word under a
confirmation tag (eval_393). Route ext_56 to the engine and the reply opens "Ndiyo" to a
question whose premise was "Bado sijafika" -- a reader can take that as assent to the very
premise being refuted. THE VETO NARROWING AND THE POLARITY HANDLING ARE ONE CHANGE, OR THE FIX
TRADES ONE WRONG ANSWER FOR ANOTHER.

R21 BOUND. 14,243 questions authored from the same source families as the facts. A blast radius
of one is a LOWER BOUND on cost and an UPPER BOUND on confidence; it says the corpus contains
one such row, not that users ask only one such question. Confirmation tags are a REGISTER, and
this corpus is one-phrasing-per-question by construction (PROGRESS.md 2026-09-23).

R18: committed before the write-up that cites it.
Artifact: eval/results/confirmation_tag_veto_2026_09_29.json

Usage:  python eval/routing/measure_confirmation_tag_veto.py
"""
import glob
import json
import os
import re
import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

OUT = os.path.join(REPO, "eval", "results", "confirmation_tag_veto_2026_09_29.json")

import chike.routing as R                                   # noqa: E402
from chike import rules_engine, swahili_numbers as swn      # noqa: E402
from chike.routing import detect_intent                     # noqa: E402

QK = ("question", "question_sw", "q", "prompt", "instruction")
SKIP = ("rejected", "flagged", "quarantine", "eval_family_quarantine")

TAG = re.compile(r"\bsivyo\s*\?")
# Every OTHER limb of _THRESHOLD_ASK_VETO. A row matching one of these is held on the fact path
# whatever happens to `sivyo?`, so it is not in the blast radius. Kept as a separate literal
# rather than derived from the compiled pattern, so that a future edit to the veto shows up here
# as a mismatch instead of being silently absorbed -- see the assertion in main().
OTHER_LIMBS = (r"ni\s+tzs\s+ngapi|ni\s+kiasi\s+gani\s*\?|baada\s+ya\s+miezi\s+mingapi|"
               r"mauzo\s+ya\s+ziada|kiasi\s+gani\s+zaidi|ngapi\s+kabla|vizingiti\s+viwili|"
               r"kizingiti\s+cha\s+mauzo\s+cha|asilimia\s+ngapi")
OTHER = re.compile(OTHER_LIMBS)


def load():
    rows = []
    for pat in ("eval/**/*.jsonl", "datasets/**/*.jsonl"):
        for p in sorted(glob.glob(os.path.join(REPO, pat), recursive=True)):
            rel = os.path.relpath(p, REPO).replace(os.sep, "/")
            if any("/" + d + "/" in "/" + rel for d in SKIP):
                continue
            for ln, line in enumerate(open(p, encoding="utf-8"), 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except Exception:
                    continue
                q = next((row[k] for k in QK
                          if isinstance(row.get(k), str) and row[k].strip()), None)
                if q:
                    rows.append({"id": str(row.get("id", f"{rel}:{ln}")),
                                 "file": rel, "question": q})
    return rows


def main():
    # R26: the veto limb must actually be IN the live pattern, and the other-limbs literal must
    # still match it. If someone edits the veto, this fails loudly rather than measuring a
    # pattern that no longer exists.
    assert r"\bsivyo\s*\?" in R._THRESHOLD_ASK_VETO.pattern, (
        "the `sivyo?` limb is no longer in _THRESHOLD_ASK_VETO -- this harness is measuring a "
        "veto that has changed under it")
    assert OTHER_LIMBS in R._THRESHOLD_ASK_VETO.pattern.replace(r"\bsivyo\s*\?|", ""), (
        "_THRESHOLD_ASK_VETO's other limbs have changed; OTHER_LIMBS here is stale and the "
        "blast radius would be computed against the wrong baseline")

    rows = load()
    assert len(rows) > 5000, f"corpus loader returned only {len(rows)} questions"

    tagged = [r for r in rows if TAG.search(r["question"].lower())]
    moved = []
    for r in rows:
        ql = r["question"].lower()
        vat = any(c in ql for c in R._VAT_REG_CUES)
        efd = any(c in ql for c in R._EFD_CUES)
        if not (vat or efd) or not TAG.search(ql):
            continue
        if OTHER.search(ql) or R._FOREIGN_CURRENCY.search(ql):
            continue
        own = any(c in ql for c in R._OWN_TURNOVER_CUES)
        if not ((own and R._has_money_magnitude(ql))
                or (efd and R.states_vat_registered(r["question"]))):
            continue
        new = "efd_requirement" if efd else "vat_registration"
        amount = swn.sole_plausible_amount(r["question"])
        period = R.turnover_period(r["question"])
        engine = None
        if new == "vat_registration" and amount is not None and period is not None:
            res = rules_engine.vat_registration(amount, period)
            engine = {"applicable": res.applicable, "working": res.working, "note": res.note}
        moved.append({"id": r["id"], "file": r["file"], "question": r["question"],
                      "route_now": detect_intent(r["question"]), "route_if_narrowed": new,
                      "amount_parsed": None if amount is None else str(amount),
                      "period_parsed": period,
                      "engine_would_say": engine})

    distinct = sorted({m["question"] for m in moved})
    artifact = {
        "measured": str(date.today()),
        "harness": "eval/routing/measure_confirmation_tag_veto.py",
        "what_this_measures": (
            "How many committed questions would change route if the `sivyo?` confirmation-tag "
            "limb left _THRESHOLD_ASK_VETO -- i.e. the blast radius of the routing decision "
            "that sent ext_56 to the fact path, where no engine ran and so no figure-comparing "
            "fidelity guard could fire."),
        "what_it_cannot_show": (
            "R21: whether users ask confirmation-tag questions more often than this corpus "
            "does. A confirmation tag is a REGISTER, and these corpora are "
            "one-phrasing-per-question by construction, so a blast radius of one is a statement "
            "about the corpus, not about traffic. And it cannot see the polarity hazard at all: "
            "_answer_vat_registration does not call agree_with_negated_premise, so a row routed "
            "to the engine would open 'Ndiyo' to a 'sivyo?' question."),
        "why_this_population": (
            "Every committed question in eval/ and datasets/ (quarantines excluded), which is "
            "the population a route change can move. It is NOT the population a false-premise "
            "question is drawn from in production (R22)."),
        "totals": {"questions": len(rows), "rows_with_confirmation_tag": len(tagged),
                   "rows_whose_route_would_change": len(moved),
                   "distinct_questions_affected": len(distinct)},
        "rows": moved,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(artifact, fh, ensure_ascii=False, indent=2)

    print(f"population: {len(rows)} questions")
    print(f"rows carrying a `sivyo?` confirmation tag: {len(tagged)}")
    print(f"rows whose ROUTE would change: {len(moved)}  "
          f"({len(distinct)} distinct question(s))")
    for m in moved:
        print(f"  {m['id']:40} {m['route_now']} -> {m['route_if_narrowed']}")
        print(f"      {m['question'][:130]}")
        print(f"      parsed: amount={m['amount_parsed']} period={m['period_parsed']}")
        if m["engine_would_say"]:
            print(f"      engine: {m['engine_would_say']['working'][:150]}")
    print(f"\n[saved] {os.path.relpath(OUT, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
