# -*- coding: utf-8 -*-
"""ALL 21 Cap.50 FACTS CHECKED AGAINST THE NSSF ACT R.E. 2023. Report only; no fact edited.

THE ACT, AND BOTH ROUTES CONFIRMED TO BE THE SAME FILE BEFORE EITHER WAS USED:
  https://www.nssf.go.tz/uploads/publications/en-1771921274-NSSF%20ACT%20CAP%2050%20RE.%202023.pdf
  https://oagmis.oag.go.tz/portal/acts/revised/155/download
Both HTTP 200, both 773,203 bytes, 50pp, **sha256 identical** (2a820e67ed109cd36059...), cover
"CHAPTER 50 THE NATIONAL SOCIAL SECURITY FUND ACT [PRINCIPAL LEGISLATION] ... CAP. 50 R.E. 2023",
same OAG 2025 compilation series as Cap.212/332/438. Deliberately NOT the kazi.go.tz copies
(R.E.2015 / R.E.2018) or the TanzLII PDF that labels itself not-the-latest -- that is the
superseded-edition trap this project has now been caught by twice.

⚠️ WHY THE EARLIER SEARCH FAILED, recorded because the lesson is the opposite of what I concluded.
Eight hosts were tried and I reported the Act "not located". It was on nssf.go.tz the whole
time -- at `/publications/act`, a route the broken `/pages/*` family does not cover. My evidence
was accurate (the homepage links nothing matching publication|act across its 41 links -- verified
again) but my CONCLUSION from it was too strong: **a homepage that does not link a route is not
evidence the route does not exist.** "The administering body hosts its own Act" held perfectly;
the search stopped one subdomain short of the AG's `oagmis` and one route short of the Fund's own.

⭐ R.E. 2023 RENUMBERED Cap.50, which is exactly the Cap.212 trap and exactly what to check first.
The Act carries 81 bracketed prior-edition notes. Confirmed offsets: s.25 <- [s. 23],
s.47 <- [s. 45], s.50 <- [s. 48], s.51 <- [s. 49], s.23 <- [s. 21]. So a citation taken from
R.E.2015 lands roughly 2-3 sections low in the current text.

**AND s.5A DOES NOT EXIST IN R.E.2023 AT ALL.** Four facts cite the First Schedule as made under
"ss.5A(c), 12(1)". The Schedule's own rubric reads "(Made under sections 5(2)(c) and 12(1) and
(5))". So that limb of the citation points at a provision the current edition does not contain.

R34 IN FORCE: every verdict below was reached by reading the fact's own text AND the cited
provision in the Act body -- never from a filename, an edition year or a field. The extractor
reads the ENACTING BODY only; its first version took the last `N.-(1)` match in the file and
reported s.2 as "members of the Board" (a Schedule provision) when s.2 is the interpretation
section. That error was caught and fixed before any verdict was recorded.
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ACT = os.path.join(
    r"C:\Users\jhjh\AppData\Local\Temp\claude\C--Users-jhjh-AFRICA-GIANTS"
    r"\d8f91321-e9cf-4aa8-a380-2afc9441133f\scratchpad", "acts", "nssf_cap50_fund.txt")
OUT = os.path.join(REPO, "eval", "results", "cap50_facts_vs_re2023.json")

ACT_META = {
    "edition": "Cap.50 R.E. 2023 (OAG 2025 compilation)",
    "routes": ["https://www.nssf.go.tz/uploads/publications/"
               "en-1771921274-NSSF%20ACT%20CAP%2050%20RE.%202023.pdf",
               "https://oagmis.oag.go.tz/portal/acts/revised/155/download"],
    "bytes": 773203, "pages": 50,
    "sha256_both_routes": "2a820e67ed109cd36059",
    "same_file": True,
    "rejected_sources": "kazi.go.tz copies (R.E.2015 and R.E.2018) and the TanzLII PDF that "
                        "labels itself not the latest version -- the superseded-edition trap",
    "renumbering_confirmed": {"s.25": "[s. 23]", "s.47": "[s. 45]", "s.50": "[s. 48]",
                              "s.51": "[s. 49]", "s.23": "[s. 21]"},
    "s5A_exists_in_re2023": False,
}

# Each row: the fact key, the claim as the fact states it, the provision that settles it, the
# VERBATIM text, and the verdict. Verbatim quotes are the evidence -- R34's "if the write-up
# cannot quote it, the verdict is an inference".
FINDINGS = [
    # --- values CONFIRMED by the statute ---------------------------------------------------
    {"key": "nssf_employer_rate", "claim": "10% employer share",
     "provision": "First Schedule, item (a) one month",
     "verbatim": "Employer's share deductible from wages by Employer: Ten cents for every "
                 "complete shilling of wages",
     "verdict": "VALUE CONFIRMED", "citation_issue": "stale_edition_and_phantom_section"},
    {"key": "nssf_total_rate", "claim": "20% total (10+10)",
     "provision": "First Schedule, item (a) one month",
     "verbatim": "Statutory Contributions for each employee: Twenty cents for every complete "
                 "shilling of wages",
     "verdict": "VALUE CONFIRMED", "citation_issue": "stale_edition_and_phantom_section"},
    {"key": "contribution_rate_emplyees", "claim": "10% employee share",
     "provision": "First Schedule read with s.12(1)",
     "verbatim": "a contribution that consist of the employer's and employee's share at the "
                 "rate stipulated in the First Schedule (total 20%, employer limb 10%)",
     "verdict": "VALUE CONFIRMED (by subtraction, 20% total less the 10% employer limb)",
     "citation_issue": "no_source_at_all"},
    {"key": "nssf_calculation_example",
     "claim": "12 employees at 600,000 = TZS 1,440,000 total, not 120,000",
     "provision": "First Schedule + s.12(1)",
     "verbatim": "20% of 12 x 600,000 = 1,440,000 (arithmetic on the confirmed statutory rate)",
     "verdict": "VALUE CONFIRMED", "citation_issue": "stale_edition_and_phantom_section"},
    {"key": "nssf_penalty", "claim": "5% per month",
     "provision": "s.14(3)",
     "verbatim": "a sum equal to five per centum of the amount unpaid shall be added as penalty "
                 "for each month or a part of a month after the date when payment should have "
                 "been made",
     "verdict": "VALUE CONFIRMED -- UPGRADE AVAILABLE: currently cited only to the "
                "nssf.go.tz/pages/payment-of-contributions portal page, which returns HTTP 500. "
                "Now sourceable at statute tier.",
     "citation_issue": "portal_only_and_that_portal_route_is_down"},
    {"key": "unpaid_contribution_penalty_rate", "claim": "five %",
     "provision": "s.14(3)", "verbatim": "a sum equal to five per centum of the amount unpaid",
     "verdict": "VALUE CONFIRMED", "citation_issue": "no_source_at_all"},
    {"key": "unpaid_contribution_penalty_frequency", "claim": "each month or a part of a month",
     "provision": "s.14(3)", "verbatim": "for each month or a part of a month after the date "
                                         "when payment should have been made",
     "verdict": "VALUE CONFIRMED -- verbatim, including the 'part of a month' limb",
     "citation_issue": "no_source_at_all"},
    {"key": "nssf_payment_deadline",
     "claim": "within one month after the payroll month ends; 5%/month if late",
     "provision": "s.14(1) and s.14(3)",
     "verbatim": "within one month after the end of the month in respect of which the "
                 "contributions are due and payable",
     "verdict": "VALUE CONFIRMED", "citation_issue": "stale_edition"},
    {"key": "nssf_retirement_age",
     "claim": "60 pensionable; 55 = early retirement within 5 years of pensionable age",
     "provision": "s.2 (interpretation), s.25(c), s.29(1)",
     "verbatim": "\"pensionable age\" means the age of sixty years | 25.(c) who has attained the "
                 "age of fifty-five or above but before attaining pensionable age | 29.-(1) An "
                 "insured person who is within five retirement years of the pensionable age and "
                 "has paid contributions for at least 180 months, may claim early retirement",
     "verdict": "VALUE CONFIRMED -- and this is the ONE Cap.50 fact already citing R.E.2023",
     "citation_issue": "none"},
    {"key": "pensionable_age", "claim": "60 years",
     "provision": "s.2 (interpretation)",
     "verbatim": "\"pensionable age\" means the age of sixty years",
     "verdict": "VALUE CONFIRMED", "citation_issue": "no_source_at_all"},
    {"key": "minimum_monthly_contributions_for_retirement_pension", "claim": "180",
     "provision": "s.25(b)",
     "verbatim": "in respect of whom not less than 180 monthly contributions have been paid",
     "verdict": "VALUE CONFIRMED", "citation_issue": "no_source_at_all"},
    {"key": "minimum_monthly_contributions_maternity_benefit", "claim": "36",
     "provision": "s.46(a)",
     "verbatim": "to an insured person who has made at least thirty-six monthly contributions "
                 "of which twelve contributions are made in the th[irty-six months...]",
     "verdict": "VALUE CONFIRMED -- with an ADDITIONAL statutory condition the fact omits: "
                "twelve of the thirty-six must fall in the recent window. Not a contradiction; "
                "an incompleteness worth recording.",
     "citation_issue": "no_source_at_all"},
    {"key": "duration_of_maternity_cash_benefit", "claim": "12 weeks",
     "provision": "s.47(a)",
     "verbatim": "cash benefit at the rate of 100 per centum of the average daily earnings for "
                 "a period of twelve weeks",
     "verdict": "VALUE CONFIRMED", "citation_issue": "no_source_at_all"},
    {"key": "maternity_cash_benefit_rate", "claim": "100 %",
     "provision": "s.47(a)",
     "verbatim": "100 per centum of the average DAILY earnings",
     "verdict": "VALUE CONFIRMED -- note the base is average DAILY earnings, which the bare "
                "'100%' does not convey",
     "citation_issue": "no_source_at_all"},
    {"key": "employer_notification_deadline_before_retirement", "claim": "6 months",
     "provision": "s.51(1)",
     "verbatim": "An employer shall, within six months before the date of retirement of his "
                 "employee, notify the Fund in writing about the date of retirement",
     "verdict": "VALUE CONFIRMED", "citation_issue": "no_source_at_all"},
    {"key": "fund_payment_deadline_after_retirement_notification", "claim": "60 days",
     "provision": "s.51(2)",
     "verbatim": "the Fund shall, within sixty days following the date of retirement, pay to "
                 "the member the due retirement pension benefits",
     "verdict": "VALUE CONFIRMED -- and s.51(3) adds a limb worth having: if the Fund misses "
                "that deadline through no fault of the member it owes the principal plus a "
                "penalty of fifteen percent per annum.",
     "citation_issue": "no_source_at_all"},
    {"key": "imprisonment_term_limit", "claim": "two years",
     "provision": "s.76(1) closing words",
     "verbatim": "or to imprisonment for a term not exceeding two years or to both",
     "verdict": "VALUE CONFIRMED", "citation_issue": "no_source_at_all"},

    # --- the disagreement ------------------------------------------------------------------
    {"key": "fine_limit", "claim": "one hundred thousand TZS",
     "provision": "s.76(1) closing words",
     "verbatim": "commits an offence and on conviction shall be liable to a fine not exceeding "
                 "TEN MILLION SHILLINGS or to imprisonment for a term not exceeding two years "
                 "or to both",
     "verdict": "🔴 WRONG VALUE -- the Act says TEN MILLION shillings, the fact says one "
                "hundred thousand. A 100x understatement of the maximum fine, on a fact that "
                "had primary_source: None and so was never checked by anyone.",
     "citation_issue": "no_source_at_all"},

    # --- not settleable from this Act -------------------------------------------------------
    {"key": "minimum_contribution_months_health_insurance", "claim": "3 months",
     "provision": "NOT IN Cap.50",
     "verbatim": "s.23(1)(g) lists 'health benefit' as a class of benefit; NO contribution-month "
                 "condition for it appears anywhere in the Act body",
     "verdict": "⚠️ UNVERIFIABLE FROM Cap.50 -- searched every occurrence of 'health' in the "
                "enacting body; the 3-month qualifying period is not there. It is presumably in "
                "regulations or the Social Security Act. NOT contradicted, NOT confirmed.",
     "citation_issue": "no_source_at_all"},
    {"key": "NSSF_split_triggers", "claim": "three valid splits: 10+10, 15+5, 20+0",
     "provision": "s.12(1)-(3)",
     "verbatim": "12.-(2) The employer may opt to contribute a greater rate than the amount "
                 "stipulated in subsection (1). (3) Where the employer agrees to contribute at "
                 "a greater rate or the whole contribution rate, such option shall not apply to "
                 "a member whose contribution rate ... does not exceed fifty percent",
     "verdict": "⚠️ CONCEPT CONFIRMED, ENUMERATION NOT. The Act establishes the 20% total and "
                "that an employer MAY opt to pay a greater share up to the whole, which makes "
                "15+5 and 20+0 lawful. It does not enumerate those three splits -- that framing "
                "is portal-sourced. Defensible, but the fact should not imply the statute lists "
                "them.",
     "citation_issue": "portal_only"},
    {"key": "nssf_employer_registration_deadline",
     "claim": "register at or shortly after commencement of business -- verify at nssf.go.tz",
     "provision": "s.11(1)-(2)",
     "verbatim": "every contributing employer shall, unless such employer has been registered "
                 "under the existing Fund, within one month, register under this section in the "
                 "prescribed manner | (2) The period of one month ... shall, in every case, "
                 "begin upon the commencement of this Act or the date when the person concerned "
                 "becomes a contributing employer",
     "verdict": "⭐ HEDGE NOW RESOLVABLE. The fact currently says 'verify deadline at "
                "nssf.go.tz' and is marked unverifiable. The Act gives a precise answer: WITHIN "
                "ONE MONTH of becoming a contributing employer. This is an upgrade from a hedge "
                "to a statute-grounded value, not a correction of a wrong one.",
     "citation_issue": "unverifiable_hedge"},
]


def main():
    assert os.path.exists(ACT), f"Act text missing at {ACT}"
    raw = open(ACT, encoding="utf-8").read()
    raw = raw[raw.index("1. This Act may be cited"):]
    # ⚠️ WHITESPACE-NORMALISE BEFORE MATCHING. The first run of this harness asserted against
    # the RAW pdf text and reported 10 of 14 decisive strings "NOT in the Act" -- including
    # phrases quoted verbatim from this very file. The cause is pypdf's extraction: line breaks
    # and stray spaces land inside phrases ("issu e fiscal receipt" is a real example from the
    # Cap.438 text). The assertion was RIGHT to fire -- it refused to let CONFIRMED verdicts
    # rest on strings that had not actually been matched in the file -- and the bad specimen was
    # my anchor list, normalised where the text was not. Collapse whitespace on both sides.
    body = " ".join(raw.split())

    # R20: the Act text must actually contain the decisive strings, or every "CONFIRMED" below
    # is an unchecked assertion typed by hand. These are the load-bearing ones.
    anchors = {
        "ten cents": "Ten cents for every complete shilling",
        "twenty cents": "Twenty cents for every complete shilling",
        "five per centum": "five per centum of the amount unpaid",
        "one month deadline": "within one month after the end of the month",
        "180": "not less than 180 monthly contributions",
        "sixty years": "the age of sixty years",
        "thirty-six": "at least thirty-six monthly contributions",
        "twelve weeks": "a period of twelve weeks",
        "six months before": "within six months before the date of retirement",
        "sixty days": "within sixty days following the date of retirement",
        "ten million": "ten million shillings",
        "two years": "imprisonment for a term not exceeding two years",
        "one month registration": "within one month, register under this section",
        "schedule rubric": "Made under sections 5(2)(c) and 12(1) and (5)",
    }
    missing = {k: v for k, v in anchors.items() if v.lower() not in body.lower()}
    assert not missing, (
        f"these decisive strings are NOT in the Act text, so the verdicts citing them are "
        f"unverified: {missing}")
    assert "\n 5A." not in body and "\n5A." not in body, "an s.5A appears after all -- re-check"

    by = {}
    for f in FINDINGS:
        v = f["verdict"]
        tag = ("WRONG_VALUE" if v.startswith("🔴")
               else "NOT_SETTLEABLE" if v.startswith("⚠️")
               else "HEDGE_RESOLVABLE" if v.startswith("⭐")
               else "VALUE_CONFIRMED")
        f["bucket"] = tag
        by[tag] = by.get(tag, 0) + 1
    cites = {}
    for f in FINDINGS:
        cites[f["citation_issue"]] = cites.get(f["citation_issue"], 0) + 1

    payload = {
        "_what": "All 21 Cap.50 facts checked against the NSSF Act R.E.2023, read directly.",
        "_mode": "REPORT ONLY -- no fact edited. Disagreements reported for decision first.",
        "act": ACT_META,
        "anchor_strings_verified_present": len(anchors),
        "totals": by, "citation_issues": cites,
        "findings": FINDINGS,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)

    print(f"Act: {ACT_META['edition']}, {ACT_META['pages']}pp, both routes sha-identical")
    print(f"decisive strings verified present in the Act text: {len(anchors)}/{len(anchors)}")
    print(f"\nverdicts: {by}")
    print(f"citation issues: {cites}\n")
    for f in FINDINGS:
        if f["bucket"] != "VALUE_CONFIRMED":
            print(f"[{f['bucket']}] {f['key']}  ({f['provision']})")
            print(f"    claim : {f['claim']}")
            print(f"    Act   : {f['verbatim'][:190]}")
            print(f"    -> {f['verdict'][:220]}\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
