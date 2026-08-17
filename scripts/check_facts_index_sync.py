#!/usr/bin/env python3
"""
FACTS <-> RAG INDEX SYNC CHECK.
Usage: python scripts/check_facts_index_sync.py
Exit code: 0 = every locked fact is verifiably reachable, 1 = unpinned drift found

WHY THIS EXISTS (2026-08-17). Three matchers were tried in one afternoon to answer
"is locked_facts.json a projection of the RAG index":

  v1  key-slug PREFIX match             -> "57 of 247 missing" (23%)   WRONG
  v2  key-slug EXACT + figure-in-blob   -> "28 of 247 missing" (11%)   WRONG, quoted
      to the founder as a correction before being checked
  v3  embedding cosine, then EVERY ROW READ BY HAND -> 13 genuinely missing (5%)

v1 and v2 both flagged `efd_threshold_tzs_11m` and `sdl_threshold` as absent when both
are in the index, in Swahili, under a different key. v2's failure mode was specific:
its "value figure appears in the index" fallback used a 3-character regex, so a value
written as words ("10 employees", "TZS 11 million") produced no marks and fell straight
into the unreachable bucket. v1 and v2 were BOTH published before being checked against
each other; v2 corrected v1's number and was never itself subjected to the check it was
built to perform. That is the failure mode this script exists to close.

THE EMBEDDING SCORE CANNOT BE THE CUT POINT EITHER — measured, not assumed. In the v3
adjudication (scratch/factpath_sync_gap_v2.json), the 'absent' bucket's best cosine score
reaches 0.886 and the 'present_elsewhere' bucket's lowest is 0.851: the two distributions
OVERLAP. A threshold that excludes every false positive also excludes true positives.
This is the same shape as the similarity-floor finding for the retrieval gate itself
(PROGRESS.md, "THE FLOOR CANNOT BE AN ABSOLUTE SCORE") — the two findings are the same
fact about this embedding space, discovered independently twice in one day.

SO THIS CHECK DOES NOT SCORE. It resolves each locked fact one of three ways:
  1. EXACT key match against an index row's key prefix       -> automatic pass
  2. SIBLING key match (index carries a versioned variant,
     e.g. sdl_rate -> sdl_rate_2025)                          -> automatic pass
  3. a PINNED, human-verified verdict below, re-checked EVERY RUN against the CURRENT
     index content (not trusted blindly forever) — present_elsewhere / absent /
     fragment / pending_r15

Anything that resolves NONE of these three ways is DRIFT: a new locked fact, or an
edit to an existing one, that nobody has looked at against the index. The check FAILS.
This is deliberately more work than a score threshold — that is the point. A key
someone has not read cannot be marked safe by a number.

Run this whenever locked_facts.json OR kaggle/rag_facts_text.json changes. Wire it in
next to check_locked_facts.py per CLAUDE.md's "before writing any pair to disk" skill.
"""
import argparse
import json
import os
import sys

_HERE = os.path.dirname(__file__)
_REPO = os.path.normpath(os.path.join(_HERE, ".."))

FACTS_PATH = os.path.join(_REPO, "scripts", "locked_facts.json")
INDEX_PATH = os.path.join(_REPO, "kaggle", "rag_facts_text.json")

# --- PINNED VERDICTS, adjudicated by hand 2026-08-17 (scratch/factpath_sync_gap_v3.py) ---
# present_elsewhere: (index_row, a short substring of that row's CURRENT text — if the
#   substring stops matching, the index changed under this pin and the check must FAIL
#   rather than trust a stale row number).
# absent / fragment / pending_r15: no index_row — genuinely not there, by different reasons.
PINNED = {
    "sdl_threshold": ("present_elsewhere", 7, "wafanyakazi 10 au zaidi"),
    "sdl_employee_threshold": ("present_elsewhere", 7, "wafanyakazi 10 au zaidi"),
    "efd_threshold_tzs_11m": ("present_elsewhere", 58, "TZS 11,000,000"),
    "osha_registration_threshold_b004": ("present_elsewhere", 53, "bila kikomo"),
    "small_headcount_still_register": ("present_elsewhere", 72, "OSHA husajili maeneo YOTE"),
    "OSHA_annual_inspection": ("present_elsewhere", 88, "ukaguzi wa lazima kila mwaka"),
    "legal_citation_sdl": ("present_elsewhere", 91, "Section 14"),
    "gn487a_prohibited_activity_3": ("present_elsewhere", 182, "kielektroniki"),
    "order_made_under_section": ("present_elsewhere", 178, "section 14A(2)"),

    "legal_citation_tax_administration": ("absent", None, None),
    "legal_citation_amendment_act_sdl": ("absent", None, None),
    "workers_compensation_act_citation": ("absent", None, None),
    "exemption_category_government_departments": ("absent", None, None),
    "exemption_category_diplomatic_missions": ("absent", None, None),
    "exemption_category_un_and_agencies": ("absent", None, None),
    "exemption_category_international_organizations_aid": ("absent", None, None),
    "exemption_category_religious_institutions": ("absent", None, None),
    "exemption_category_charitable_organizations": ("absent", None, None),
    "exemption_category_educational_institutions": ("absent", None, None),
    "exemption_category_local_government_authorities": ("absent", None, None),
    "exemption_category_trainees_under_TAESA": ("absent", None, None),
    "exemption_category_farm_employers_agriculture": ("absent", None, None),

    "workers_compensation_act_section": ("fragment", None, None),
    "workers_compensation_rules_section": ("fragment", None, None),
    "workers_compensation_amendment_rules_section": ("fragment", None, None),
    "offence_penalty_mention": ("fragment", None, None),

    # Written 2026-08-16 for the presumptive-tax coverage item; absent BY DESIGN until
    # the R15 regen runs. If this script is still reporting them PENDING long after that
    # regen shipped, the regen silently missed them -- that is exactly the drift this
    # check exists to catch, so do not raise this to "absent" or "present" without
    # re-running the regen and re-verifying against the live index.
    "business_licence_expiry_30_june": ("pending_r15", None, None),
    "presumptive_excluded_services": ("pending_r15", None, None),
    "presumptive_tax_bands_2022": ("pending_r15", None, None),
    "presumptive_tax_ceiling_100m": ("pending_r15", None, None),

    # --- Second pass, 2026-08-17: this script's own first run found 20 MORE unpinned
    # keys the earlier v1/v2/v3 investigation never touched -- v3 only re-checked the 28
    # keys v2 had flagged, so it inherited v2's blind spot for everything v2 got right by
    # accident. Adjudicated the same way: read the locked value, search the index by
    # content, confirm by eye. ---
    "gn487a_penalty_noncitizen": ("present_elsewhere", 20, "10,000,000"),
    "gn487a_penalty_citizen_facilitator": ("present_elsewhere", 94, "5,000,000"),
    "gn487a_license_lending_is_facilitation": ("present_elsewhere", 94, "lending their name"),
    "efd_not_every_business": ("present_elsewhere", 59, "Si lazima"),
    "wcf_rate_0_5_percent_confirmed": ("present_elsewhere", 69, "asilimia 0.5"),
    "osha_vs_wcf_roles": ("present_elsewhere", 71, "taasisi mbili tofauti"),
    "sdl_payment_deadline": ("present_elsewhere", 98, "siku ya 7"),
    "annual_return_filing_fee": ("present_elsewhere", 44, "22,000"),
    "osiha_act_citation": ("present_elsewhere", 71, "Na.5 ya 2003"),
    "health_and_safety_act_citation": ("present_elsewhere", 71, "Na.5 ya 2003"),
    "business_licensing_act_citation": ("present_elsewhere", 178, "Cap. 101"),
    "business_licensing_act_chapter": ("present_elsewhere", 178, "Cap. 101"),
    "tanzania_citizenship_act_reference": ("present_elsewhere", 93, "Cap.357"),
    "paye_bands_with_examples": ("present_elsewhere", 214, "TZS 800,000"),
    "sdl_calculation_example": ("present_elsewhere", 215, "Mfano wa hesabu"),

    # gn487a_marriage_no_exemption: row 93 covers dual-nationality/naturalisation under
    # Cap.357 but never mentions marriage. A materially different claim -- genuinely absent.
    "gn487a_marriage_no_exemption": ("absent", None, None),
    # gn487a_signatory: "Jafo" (the minister) has zero hits anywhere in the index.
    "gn487a_signatory": ("absent", None, None),
    # prohibited_business_activities_for_non_citizens_order_year: value is the bare year
    # "2025". Row 19 states GN487A's effective date is 28 July 2025, so the YEAR is not
    # unretrievable -- but "2025" alone is too common a substring to pin reliably (it
    # would silently match almost any row a future index edit introduces), so this is
    # kept as a fragment rather than a fragile present_elsewhere pin.
    "prohibited_business_activities_for_non_citizens_order_year": ("fragment", None, None),
}


def _key_slug(key):
    return key.replace("_", " ").strip().lower()


def check(facts_path=FACTS_PATH, index_path=INDEX_PATH):
    locked = json.load(open(facts_path, encoding="utf-8"))
    index = json.load(open(index_path, encoding="utf-8"))
    index_slugs = [f.split(":")[0].strip().lower() for f in index]

    report = {
        "exact": [], "sibling": [], "present_elsewhere": [],
        "absent": [], "fragment": [], "pending_r15": [],
        "drift_unpinned": [], "drift_pin_stale": [],
    }

    for key in locked:
        if key.startswith("_"):
            continue
        slug = _key_slug(key)

        if slug in index_slugs:
            report["exact"].append(key)
            continue
        if any(s.startswith(slug) or slug.startswith(s) for s in index_slugs):
            report["sibling"].append(key)
            continue

        pin = PINNED.get(key)
        if pin is None:
            report["drift_unpinned"].append(key)
            continue

        verdict, row, needle = pin
        if verdict == "present_elsewhere":
            if row is None or row >= len(index) or needle not in index[row]:
                report["drift_pin_stale"].append(
                    {"key": key, "pinned_row": row, "expected_substring": needle,
                     "row_now": index[row] if row is not None and row < len(index) else None})
            else:
                report["present_elsewhere"].append({"key": key, "row": row})
        elif verdict in ("absent", "fragment", "pending_r15"):
            report[verdict].append(key)
        else:  # pragma: no cover -- guards a typo in PINNED itself
            report["drift_unpinned"].append(key)

    ok = not report["drift_unpinned"] and not report["drift_pin_stale"]
    return ok, report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--facts", default=FACTS_PATH)
    ap.add_argument("--index", default=INDEX_PATH)
    args = ap.parse_args()

    ok, report = check(args.facts, args.index)

    print(f"locked facts checked: {sum(len(v) for v in report.values())}")
    print(f"  exact key match          {len(report['exact'])}")
    print(f"  sibling key match        {len(report['sibling'])}")
    print(f"  pinned present_elsewhere {len(report['present_elsewhere'])}")
    print(f"  pinned absent (known)    {len(report['absent'])}")
    print(f"  pinned fragment (n/a)    {len(report['fragment'])}")
    print(f"  pinned pending_r15       {len(report['pending_r15'])}")
    print()

    if report["drift_unpinned"]:
        print(f"DRIFT -- {len(report['drift_unpinned'])} key(s) not exact/sibling-matched "
              f"and not in PINNED:")
        for k in report["drift_unpinned"]:
            print(f"    {k}")
        print("  Adjudicate each: is the content in the index under a different key/language "
              "(add to PINNED as present_elsewhere with the row + a substring), genuinely "
              "absent, a non-retrievable fragment, or pending an R15 regen? Then re-run.")
        print()

    if report["drift_pin_stale"]:
        print(f"DRIFT -- {len(report['drift_pin_stale'])} PINNED present_elsewhere row(s) "
              f"no longer match the current index (the index changed under the pin):")
        for r in report["drift_pin_stale"]:
            print(f"    {r['key']}: expected row {r['pinned_row']} to contain "
                  f"{r['expected_substring']!r}, found {r['row_now']!r}")
        print("  Re-adjudicate: find the fact's new location (or confirm it is now genuinely "
              "absent) and update PINNED.")
        print()

    if ok:
        print("CLEAN -- every locked fact is exact-matched, sibling-matched, or a "
              "human-verified pin.")
    else:
        print("FAIL -- unadjudicated drift between locked_facts.json and the RAG index.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
