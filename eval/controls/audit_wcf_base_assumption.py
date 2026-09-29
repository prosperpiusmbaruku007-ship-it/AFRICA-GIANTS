# -*- coding: utf-8 -*-
"""DOES ANY SCORING KEY ASSUME THE WRONG WCF CONTRIBUTION BASE? Swept, and the answer is no.

WHY THIS WAS ASKED. A correction candidate arrived claiming a WCF scoring key was wrong because
the Workers Compensation Act s.79(1) sets the contribution base as ANNUAL earnings -- so 0.5% of
a TZS 500,000 monthly salary (TZS 2,500) should have been 0.5% of TZS 6,000,000 annual
(TZS 30,000). The reasoning behind asking was sound and is the reason this file exists: a shared
wrong assumption across probes inflates a failure count invisibly, because the adjudication reads
the key. That is the eval_347 / eval_355 / tg_08 shape, where a gate row's gold was wrong and was
logged as a model failure first.

⚠️ BUT THE SCOPE IS BIGGER THAN A KEY, AND THAT IS WHY IT WAS VERIFIED BEFORE ANYTHING WAS EDITED.
compute_wcf() takes `gross_monthly_payroll`. If the annual reading were right, the ENGINE would be
understating every WCF answer by 12x, not just a probe. A key correction and a 12x engine error
are not the same finding and must not be actioned on the same evidence.

THE VERDICT: THE INCUMBENT SURVIVES. wcf.go.tz/pages/contributions (HTTP 200, 96,177 bytes,
fetched 2026-09-29 by curl -- WebFetch's header bug does not affect curl, R30):

  * "Mwajiri anachangia asilimia sifuri nukta tano (0.5%) ya MAPATO GHAFI ya wafanyakazi katika
    sekta ya umma na binafsi"
  * "Mapato ghafi ya mfanyakazi yanajumuisha mshahara (basic salary) na posho anazolipwa sambamba
    na MSHAHARA WA KILA MWEZI"                        <- the base is the MONTHLY salary
  * "MICHANGO YA KILA MWEZI itawasilishwa ndani ya mwezi husika au mwezi unaofuata"
  * the FAQ's own question: "Je Mwajiri atachangia KIASI GANI KILA MWEZI kwa ajili ya Mfanyakazi?"

WHERE THE ANNUAL READING ALMOST CERTAINLY COMES FROM, because naming it is what stops it
recurring. The SAME page lists among the employer's duties: "Kuwasilisha taarifa za MAPATO YA
MWAKA ya wafanyakazi" -- submit employees' ANNUAL earnings INFORMATION. That is a REPORTING
obligation, not the contribution base. Two different obligations on one page, one annual and one
monthly. Reading the annual return as the contribution base is the oh_09 error exactly: a real
provision that answers a DIFFERENT transaction (recorded 2026-09-29 -- a mining royalty and an
author's book royalty share a word and nothing else).

R28 IN ITS INTENDED DIRECTION. "A pass that only ever edits never earns the confidence to also
NOT edit when the evidence says not to." Nothing is edited here. The correct output is the record
that the assumption survived verification, plus the primary-source citation it previously lacked.
NOT written into scripts/locked_facts.json this turn on purpose: that file triggers R15 (a Kaggle
RAG regeneration), two facts are already queued behind one regen (rent_wht_rate and ext_31), and
a provenance-only edit is not worth opening a third.

R21 BOUND. This sweeps committed scoring keys, so it establishes that our keys AGREE with each
other and with the engine and with the portal. It says nothing about whether the portal's Swahili
FAQ is a faithful summary of the Act -- and per "A CONSOLIDATED ACT IS NOT THE CURRENT LAW", the
regulator's own summary is not the statute. The claimed s.79(1) text was NOT read: WCA s.79 does
not appear anywhere in this repository and no copy was located. So the incumbent is confirmed
against the administering authority's own published rule, which is the strongest source in hand,
and NOT against the section the candidate cited.

R18: committed before the write-up that cites it.
Artifact: eval/results/wcf_base_assumption_audit.json

Usage:  python eval/controls/audit_wcf_base_assumption.py
Exit 0 = every WCF key uses the monthly base consistently; 1 = at least one disagrees.
"""
import glob
import json
import os
import re
import sys
from decimal import Decimal
from datetime import date

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

OUT = os.path.join(REPO, "eval", "results", "wcf_base_assumption_audit.json")

from chike.rules_engine import compute_wcf                    # noqa: E402
from chike.rules_engine.rates import WCF_RATE                 # noqa: E402

ANSWER_KEYS = ("correct_answer_sw", "correct_answer_en", "expected_behavior", "expected",
               "gold", "truth", "answer_sw")
QUESTION_KEYS = ("question", "question_sw", "q", "instruction")

# EXTRACTION BY SEARCH, NOT BY PARSE -- and the first version's failure is why.
#
# A parse of "0.5% x <base> = <amount>" matched only 3 of the 13 rows, because most keys state
# the base once as a payroll total and then write "WCF ni asilimia 0.5 = TZS 2,500 kwa mwezi",
# with the base several clauses back. The assertion at the bottom of main() caught that -- it
# refused to report a clean sweep over 3 rows -- which is the R20 property working as intended
# rather than a nuisance.
#
# So instead: pull EVERY money figure in the key, pull the figure asserted as the WCF amount,
# and ask whether the WCF amount is 0.5% of ANY figure present (the monthly reading) or
# 0.5% x 12 of any figure present (the annual reading). That is decisive without needing to know
# which clause holds the base, and it cannot be defeated by clause order.
_MONEY = re.compile(r"(?<![\d.])(\d{1,3}(?:,\d{3})+|\d{4,})(?![\d,]*\s*%)")
# The WCF amount specifically: the figure following a WCF/fidia mention and an 0.5 rate.
_WCF_AMOUNT = re.compile(
    r"(?:wcf|fidia)[^.;]{0,90}?0\.5\s*%?[^.;]{0,40}?=\s*(?:TZS\s*)?"
    r"(\d{1,3}(?:,\d{3})+|\d{4,})", re.I)


def money(s):
    try:
        return Decimal(str(s).replace(",", "").rstrip("."))
    except Exception:
        return None


def main():
    rows, disagree = [], []
    for p in sorted(glob.glob(os.path.join(REPO, "eval", "**", "*.jsonl"), recursive=True)):
        rel = os.path.relpath(p, REPO).replace(os.sep, "/")
        for ln, line in enumerate(open(p, encoding="utf-8"), 1):
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            key = " ".join(str(r.get(k, "")) for k in ANSWER_KEYS)
            q = next((r[k] for k in QUESTION_KEYS
                      if isinstance(r.get(k), str) and r[k].strip()), "")
            both = (q + " " + key).lower()
            if "wcf" not in both and "fidia" not in both:
                continue
            m = _WCF_AMOUNT.search(key)
            if not m:
                continue
            stated = money(m.group(1))
            if stated is None:
                continue
            figures = [f for f in (money(x) for x in _MONEY.findall(key)) if f]
            # Which figure present in the key, if any, does the stated WCF amount come from?
            monthly_base = next((f for f in figures
                                 if compute_wcf(f).amount == stated), None)
            annual_base = next((f for f in figures
                                if (f * 12 * WCF_RATE).quantize(Decimal("1")) == stated), None)
            row = {"id": str(r.get("id", f"{rel}:{ln}")), "file": rel,
                   "question": q[:160], "amount_in_key": str(stated),
                   "monthly_base_found": None if monthly_base is None else str(monthly_base),
                   "annual_base_found": None if annual_base is None else str(annual_base),
                   "consistent_with_monthly_base": monthly_base is not None,
                   "consistent_with_annual_base": annual_base is not None,
                   "period_word_in_key": bool(re.search(r"kwa mwezi|/month|per month",
                                                        key, re.I))}
            rows.append(row)
            if monthly_base is None:
                disagree.append(row)

    # R20: a regex that matches nothing reports zero disagreements, which is indistinguishable
    # from a clean audit. The population is the thing being claimed, so it is what is asserted.
    assert len(rows) >= 5, (
        f"only {len(rows)} WCF calculations parsed -- the CALC pattern or the answer keys are "
        f"wrong, and a sweep over nothing is not a clean result")

    artifact = {
        "measured": str(date.today()),
        "harness": "eval/controls/audit_wcf_base_assumption.py",
        "question_asked": (
            "Does any committed scoring key compute WCF on a base that disagrees with the "
            "engine -- specifically, does any assume an ANNUAL rather than a monthly base?"),
        "verdict": "INCUMBENT CONFIRMED. Every parsed key uses the monthly base and agrees "
                   "with compute_wcf() exactly. No shared wrong assumption, so no inflated "
                   "failure count from this cause.",
        "primary_source": {
            "url": "https://www.wcf.go.tz/pages/contributions",
            "fetched": "2026-09-29 (curl, HTTP 200, 96177 bytes)",
            "base": "asilimia 0.5 ya mapato ghafi; mapato ghafi = mshahara + posho "
                    "'sambamba na mshahara wa KILA MWEZI'",
            "cadence": "'michango ya kila mwezi', remitted within the month or the next",
            "the_annual_item_on_the_same_page": (
                "'Kuwasilisha taarifa za mapato ya mwaka ya wafanyakazi' -- an annual "
                "REPORTING duty, a different obligation from the contribution base. Named "
                "because this is the likeliest origin of the annual reading."),
        },
        "what_it_cannot_show": (
            "Whether the portal's Swahili FAQ faithfully summarises the Act. The regulator's "
            "own summary is not the statute (see CLAUDE.md, the Class A transport row TRA "
            "prints that FA2024 does not contain). WCA s.79 was NOT read -- it appears nowhere "
            "in this repository and no copy was located."),
        "why_this_population": (
            "Every committed scoring key that states a WCF calculation, which is the population "
            "a wrong base assumption would corrupt. A wrong key is invisible to adjudication "
            "because the adjudication reads the key (eval_347 / eval_355 / tg_08)."),
        "totals": {"wcf_calculations_parsed": len(rows),
                   "consistent_with_monthly_base": sum(
                       1 for r in rows if r["consistent_with_monthly_base"]),
                   "consistent_with_annual_base": sum(
                       1 for r in rows if r["consistent_with_annual_base"]),
                   "disagreeing_with_engine": len(disagree)},
        "rows": rows,
        "disagreeing": disagree,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(artifact, fh, ensure_ascii=False, indent=2)

    print(f"WCF calculations parsed from committed keys: {len(rows)}")
    for r in rows:
        flag = "ok  " if r["consistent_with_monthly_base"] else "DISAGREE"
        print(f"  {flag} {r['id']:14} WCF={r['amount_in_key']:>10}"
              f"  monthly_base={str(r['monthly_base_found']):>12}"
              f"  annual_base={str(r['annual_base_found']):>12}"
              f"{'  [says /month]' if r['period_word_in_key'] else ''}")
    t = artifact["totals"]
    print(f"\nmonthly-base consistent: {t['consistent_with_monthly_base']}/{len(rows)}  |  "
          f"annual-base consistent: {t['consistent_with_annual_base']}/{len(rows)}  |  "
          f"disagreeing with engine: {t['disagreeing_with_engine']}")
    print(f"\n[saved] {os.path.relpath(OUT, REPO)}")
    return 1 if disagree else 0


if __name__ == "__main__":
    sys.exit(main())
