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

SO THIS CHECK DOES NOT SCORE. It resolves each locked fact one of four ways:
  1. EXACT key match against an index row's key prefix       -> automatic pass
  2. SIBLING key match (index carries a versioned variant,
     e.g. sdl_rate -> sdl_rate_2025)                          -> automatic pass
  3. GROUPED: the key is a member of a FACT_GROUPS consolidation (2026-08-25), so it has
     no row of its own by design. Verified BY CONTENT, every run: the group's passage must
     be in the index AND must still contain this key's own figure. Not a row-number pin --
     R18's first incident was exactly that, verdicts pinned to row numbers that decayed
     silently when the index moved underneath them.
  4. a PINNED, human-verified verdict below, re-checked EVERY RUN against the CURRENT
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
#
# RE-ADJUDICATED WHOLESALE, same day, after the R15 regen actually ran and deployed.
# Every present_elsewhere row number above was resolved against the OLD 217-row index;
# inserting/deleting keys mid-file shifted almost every row after the edit point in the
# NEW 221-row index, so 23 of 26 present_elsewhere pins went stale in one regen — this is
# exactly what drift_pin_stale exists to catch, and it caught all 23 the first run after
# deploy. Re-located each by searching the new index for its (still-correct) substring,
# disambiguating by content where a figure recurs (22,000/5,000,000/asilimia 3.5 all hit
# multiple rows — see PROGRESS's "R15 CYCLE DEPLOYED" entry). The 3 pending_r15 keys from
# the C4 cycle are promoted to present_elsewhere here since the regen that was pending has
# now happened. Two new drift_unpinned keys (sdl_rate, GN605A_sector_count) surfaced
# separately: their round-2 CONCISE rewrites lead with a conversational Swahili clause
# before the first colon, so split(":")[0] no longer yields "sdl rate" / "gn605a sector
# count" — a checker-matcher gap the readability-over-key-shape tradeoff will keep
# producing, not a one-off.
PINNED = {
    "sdl_threshold": ("present_elsewhere", 7, "wafanyakazi 10 au zaidi"),
    # sdl_employee_threshold pin removed 2026-08-17 -- the key itself was deleted
    # (merged into sdl_threshold, duplicate-key sweep; see PROGRESS "C4 applied").
    "efd_threshold_tzs_11m": ("present_elsewhere", 57, "TZS 11,000,000"),
    "osha_registration_threshold_b004": ("present_elsewhere", 52, "kila mwajiri lazima asajili"),

    # RE-ADJUDICATED WHOLESALE, 2026-09-03, after the fc9b0c8 -> b002b96 double regen
    # (electrical-fee merge + 2 noise drops + 2 NSSF rewrites) actually ran and deployed.
    # This is the THIRD time this file has had to do this (see the 2026-08-17 note below,
    # "23 of 26 present_elsewhere pins went stale in one regen") -- confirms the pattern is
    # structural, not a one-off: any regen that inserts/deletes ANY per-key row before a
    # pinned row shifts every row number after it, since build_fact_texts() emits rows in
    # locked_facts.json's key-insertion order, not alphabetically or by content. Re-located
    # each by searching the ACTUAL deployed kaggle/rag_facts_text.json for its CONCISE
    # source text (scripts/precompute_rag_embeddings.py's CONCISE_BILINGUAL_FACTS dict is
    # the ground truth for what each key's row actually says now), then verified the chosen
    # needle is BOTH present at that row AND unique across the full 183-row index --
    # several of the old needles ('USD 25', 'asilimia 0.5') are no longer unique now that
    # rows moved next to different neighbours.
    #
    # SEVEN of the twenty-five were not actually stale-but-relocatable -- they were
    # NOISE-DROPPED. is_noise_key()'s shape patterns (`_act_citation$`, `_act_chapter$`,
    # `_act_reference$`, `^order_made_under_section$`) already matched these seven keys;
    # they have not had a standalone row for some time, and the OLD pins were only ever
    # coincidentally "valid" because a stale row number happened to still contain matching
    # citation text left over from a much earlier index layout. Reclassified "absent"
    # rather than re-pinned present_elsewhere, since there is no row to point at going
    # forward and is_noise_key() will keep dropping them on every future regen too.
    "small_headcount_still_register": ("present_elsewhere", 68, "OSHA husajili maeneo YOTE"),
    "OSHA_annual_inspection": ("present_elsewhere", 84, "ukaguzi wa lazima kila mwaka"),
    "gn487a_prohibited_activity_3": ("present_elsewhere", 134, "Prohibited activity 3"),
    "osiha_act_citation": ("absent", None, None),  # noise-dropped, see block comment above
    "health_and_safety_act_citation": ("absent", None, None),  # noise-dropped
    "legal_citation_sdl": ("absent", None, None),  # noise-dropped
    "business_licensing_act_citation": ("absent", None, None),  # noise-dropped
    "order_made_under_section": ("absent", None, None),  # noise-dropped
    "business_licensing_act_chapter": ("absent", None, None),  # noise-dropped
    "tanzania_citizenship_act_reference": ("absent", None, None),  # noise-dropped

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

    # Written 2026-08-16 for the presumptive-tax coverage item, pending_r15 until the R15
    # regen ran. It ran on 2026-08-17 (the natural48 entry, PROGRESS.md) and all four keys
    # now resolve by EXACT key match against the new index -- confirmed via check(), not
    # assumed -- so their pins are removed rather than converted (exact match already
    # covers them; a redundant pending_r15 entry would just be stale weight). This is
    # test_pending_r15_keys_are_still_pending catching exactly what it was built to catch.

    # Third pass, 2026-08-17, same day: tightening the sibling matcher (see
    # _is_sibling's docstring -- a single-word slug like 'nssf' or 'brela' was letting
    # unrelated keys ride on the SAME row) demoted 5 real, already-indexed keys out of
    # "sibling" into unpinned drift. Re-verified each against its OWN correct row by
    # reading the index directly (scratch/local_regen_verify.py's sibling-audit pass).
    "nssf_employer_rate": ("present_elsewhere", 9, "mwajiri analipa asilimia 10"),
    "nssf_total_rate": ("present_elsewhere", 10, "jumla: asilimia 20"),
    "nssf_payment_deadline": ("present_elsewhere", 61, "ifikapo tarehe 10"),  # re-adjudicated 2026-09-03, was row 62
    "nssf_calculation_example": ("present_elsewhere", 166, "SI TZS 120,000"),  # re-adjudicated 2026-09-03, was row 171
    "brela_striking_off_non_filing": ("present_elsewhere", 44, "kufuta, kufunga au kuondoa"),

    # ---- The three council-fee domains reclassified from COVERAGE GAP to ANSWERED
    # (scripts/add_local_levy_facts.py) were pinned pending_r15 here 2026-08-25, then
    # REMOVED 2026-08-26 once the batched R15 regen (packaged in 76897e3, run and shipped
    # after the nat_34 fix) made all five retrievable via exact/sibling match --
    # test_pending_r15_keys_are_still_pending caught it immediately, exactly the signal its
    # docstring describes. This is the second reachability cycle these pins were meant to
    # close (the first is the C4 cycle below); no PINNED entry needed now that they resolve
    # on their own.

    # C4 reachability cycle, 2026-08-17 -- three new keys written that cycle, PENDING_R15
    # at the time because the regen had not yet run. The regen ran the same day (R15
    # deploy entry, PROGRESS.md) and all three are now indexed -- promoted to
    # present_elsewhere below with their real rows. brela_foreign_late_filing_penalty is
    # the one the tightened sibling matcher above caught falsely riding on 'brela' before
    # the regen; it is genuinely indexed now.
    # re-adjudicated 2026-09-03 (was rows 176/177/178): 'USD 25' alone is no longer unique
    # (the brela_filing_fees GROUP passage at row 181 also states the same figure) --
    # narrowed to the fuller phrase that is unique to this key's own standalone row.
    "brela_foreign_late_filing_penalty": ("present_elsewhere", 171, "faini ni USD 25 kwa kila mwezi"),
    "osha_registration_before_operations": ("present_elsewhere", 172, "Kifungu 16(2)"),
    "sdl_exemption_categories": ("present_elsewhere", 173, "zisizolipa SDL"),

    # late_filing_penalty_monthly_fee: found 2026-08-26, by the sibling-match audit the fee
    # consolidation prompted (eval/results/sibling_match_audit.json). This key was NEVER
    # actually verified -- it was silently riding _is_sibling's match against
    # `late_filing_penalty_monthly_fee_section_12_act`'s row purely because the two slugs
    # share a multi-word prefix ("late filing penalty monthly fee"). The two facts are
    # UNRELATED: this one is the TZS 2,500/month domestic BRELA late-filing fee; the sibling
    # it was riding is the USD 25/month foreign-company (Section XII) fee. Consolidating the
    # foreign-company key into the brela_filing_fees group deletes its standalone row and
    # the coincidental sibling match with it -- exposing that this key's OWN row (a
    # CONCISE_BILINGUAL_FACTS Swahili sentence that does not slug-match its own key) was
    # never independently confirmed. Row verified against the PROSPECTIVE post-regen index
    # (build_fact_texts(), row 98) since this pin is being added in the same commit as the
    # consolidation it depends on. Re-adjudicated 2026-09-03: row shifted 98 -> 97 (it
    # swapped positions with annual_return_filing_fee, below, in the fc9b0c8/b002b96 regen).
    "late_filing_penalty_monthly_fee": ("present_elsewhere", 97, "TZS 2,500 kwa kila mwezi"),

    # --- Second pass, 2026-08-17: this script's own first run found 20 MORE unpinned
    # keys the earlier v1/v2/v3 investigation never touched -- v3 only re-checked the 28
    # keys v2 had flagged, so it inherited v2's blind spot for everything v2 got right by
    # accident. Adjudicated the same way: read the locked value, search the index by
    # content, confirm by eye. ---
    # needle tightened 2026-08-26: bare "10,000,000" also matches vat_deferment_minimum_value's
    # row in the post-consolidation index (the sibling-match audit's disambiguation pass found
    # this collision while relocating pins) -- "(milioni kumi)" is unique to this fact's text.
    "gn487a_penalty_noncitizen": ("present_elsewhere", 20, "10,000,000 (milioni kumi)"),
    "gn487a_penalty_citizen_facilitator": ("present_elsewhere", 21, "5,000,000 (milioni tano)"),
    # re-adjudicated 2026-09-03 (row numbers below were 91/58/66/68/95/99 -- all stale
    # after the fc9b0c8/b002b96 regen; the osiha/health_and_safety/business_licensing x2/
    # tanzania_citizenship pins formerly here were REMOVED, not relocated -- see the
    # "SEVEN of the twenty-five" comment near the top of PINNED, they are noise-dropped
    # and pinned "absent" up there instead).
    "gn487a_license_lending_is_facilitation": ("present_elsewhere", 22, "leseni yake kwa mgeni"),
    "efd_not_every_business": ("present_elsewhere", 57, "Si lazima"),
    # needle narrowed: bare 'asilimia 0.5' is no longer unique (row 67, osha_vs_wcf_roles,
    # also now states the WCF rate inline as part of its own explanation).
    "wcf_rate_0_5_percent_confirmed": ("present_elsewhere", 65, "asilimia 0.5 ya jumla"),
    "osha_vs_wcf_roles": ("present_elsewhere", 67, "taasisi mbili tofauti"),
    "sdl_payment_deadline": ("present_elsewhere", 94, "siku ya 7"),
    "annual_return_filing_fee": ("present_elsewhere", 98, "ada ya kuwasilisha ritani"),
    "paye_bands_with_examples": ("present_elsewhere", 164, "TZS 800,000"),
    "sdl_calculation_example": ("present_elsewhere", 165, "Mfano wa hesabu"),
    # sdl_rate / GN605A_sector_count: drift found post-R15-regen, 2026-08-17 (the natural48
    # re-run entry, PROGRESS.md). Both rewritten this cycle into conversational Swahili
    # lead-ins ('SDL, ambayo huitwa pia "mafunzo": ...', 'Kima cha chini cha mshahara (GN
    # 605A): ...') that no longer split(":")[0] into "sdl rate" / "gn605a sector count" --
    # exactly the citation-clutter-adjacent tradeoff the readability rule accepts. Content
    # verified correct and present; needles chosen to avoid the OTHER row that shares the
    # same generic figure (row 212's SDL worked example also says "asilimia 3.5").
    "sdl_rate": ("present_elsewhere", 5, "Si asilimia 4, si asilimia 2"),
    # GN605A_sector_count re-adjudicated 2026-09-03: row 72 -> 71, needle narrowed --
    # bare 'sekta 16' risked ambiguity as the index grows, 'sekta 16 na sekta ndogo' is
    # unique to this row specifically.
    "GN605A_sector_count": ("present_elsewhere", 71, "sekta 16 na sekta ndogo"),

    # maternity_cash_benefit_rate / unpaid_contribution_penalty_rate: promoted from
    # "not pinned, still exact-matching the old bare form" (see b002b96) to
    # present_elsewhere now that the b002b96 regen actually shipped their ask-aligned
    # CONCISE rewrites -- the old bare-form exact match is gone, this checker correctly
    # reported both as drift_unpinned, and this is that promotion, exactly as predicted.
    "maternity_cash_benefit_rate": ("present_elsewhere", 154, "likizo ya uzazi"),
    "unpaid_contribution_penalty_rate": ("present_elsewhere", 148, "ASILIMIA 5"),

    # gn487a_marriage_no_exemption: row 93 covers dual-nationality/naturalisation under
    # Cap.357 but never mentions marriage. A materially different claim -- genuinely absent.
    "gn487a_marriage_no_exemption": ("absent", None, None),
    # gn487a_signatory: "Jafo" (the minister) has zero hits anywhere in the index.
    "gn487a_signatory": ("absent", None, None),

    # --- Fragment-displacement fixes, 2026-09-03 (re-adjudicating nat_27/nat_36 after the
    # fc9b0c8 regen -- see PROGRESS.md). Both were old-schema bare "key: value" duplicates of
    # an existing, better-formed CONCISE fact, deliberately dropped from the index as noise
    # (_NOISE_KEYS_REVIEWED in precompute_rag_embeddings.py carries the full R25 justification
    # for each). Pinned absent here rather than left to fall into drift_unpinned.
    "contribution_rate_emplyees": ("absent", None, None),
    "penalty_fine_non_citizen": ("absent", None, None),

    # electrical_test_fee_reduction_initial / _final: NOT pinned here -- both were converted
    # to FACT_GROUPS members in the same commit (merged, self-retrieval-failure fix), so they
    # resolve automatically via _grouped_verdict, the same as every other FACT_GROUPS member.

    # corporate_tax_rate / minimum_turnover_tax: the corporate-tax source pass (4974cbc,
    # 2026-09-01) moved both into CONCISE_BILINGUAL_FACTS, so their slugs stopped exact-
    # matching -- never adjudicated by this checker until now (it predates the fc9b0c8 regen
    # that actually shipped them). Confirmed present and RANK 1 in the real deployed index by
    # the Kaggle regen's own guard queries ('Corporate tax rate (ask-aligned)', 'AMT loss-
    # making corporation (ask-aligned)' in kaggle/regenerate_rag_e5.py), and row-located
    # directly against the fetched, deployed rag_facts_text.json (2026-09-03).
    "corporate_tax_rate": ("present_elsewhere", 36, "asilimia 30 kwa kampuni"),
    "minimum_turnover_tax": ("present_elsewhere", 27, "hasara miaka mitatu mfululizo"),
    # prohibited_business_activities_for_non_citizens_order_year: value is the bare year
    # "2025". Row 19 states GN487A's effective date is 28 July 2025, so the YEAR is not
    # unretrievable -- but "2025" alone is too common a substring to pin reliably (it
    # would silently match almost any row a future index edit introduces), so this is
    # kept as a fragment rather than a fragile present_elsewhere pin.
    "prohibited_business_activities_for_non_citizens_order_year": ("fragment", None, None),
}


# The consolidation is DEFINED in precompute_rag_embeddings.py -- the module that builds the
# index -- and imported here rather than restated. A second copy of the group membership would
# drift from the first, and this check would then certify an index it no longer describes.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from precompute_rag_embeddings import (  # noqa: E402
    FACT_GROUPS as _FACT_GROUPS,
    _GROUP_MEMBERS,
    _figure_of,
    fact_value as _fact_value,
)


def _key_slug(key):
    return key.replace("_", " ").strip().lower()


def _is_sibling(key_slug, index_slug):
    """A genuine sibling is a versioned variant (sdl_rate -> 'sdl rate 2025'), not any
    shared word. Found 2026-08-17: a raw startswith() let a single generic label --
    'nssf', 'brela', from CONCISE text like 'NSSF: ...' / 'BRELA: ...' -- silently
    verify FOUR different nssf_* keys against the SAME row (only one was actually it)
    and let a brand-new, not-yet-indexed key (brela_foreign_late_filing_penalty) pass
    as if it were already reachable. Requiring the SHORTER slug to carry at least 2
    words closes that: single-word index labels can no longer anchor a false sibling
    match, while genuine versioned pairs (which always share a multi-word stem) still
    match."""
    if not (index_slug.startswith(key_slug) or key_slug.startswith(index_slug)):
        return False
    shorter = key_slug if len(key_slug) <= len(index_slug) else index_slug
    return len(shorter.split()) >= 2


def _grouped_verdict(key, locked, index):
    """GROUPED, verified by content. Returns ('grouped', None) | ('drift', reason).

    Two ways this fails loudly, and both are real regressions rather than bookkeeping:
      - the group's passage is not in the index at all (a regen that did not run, or ran
        against a stale commit -- R15's CDN-cache trap);
      - the passage is there but no longer carries THIS member's figure, i.e. somebody
        edited the consolidated text and dropped a fee. That is the failure the whole
        consolidation is exposed to and the only automatic thing that would catch it.
    """
    spec = _FACT_GROUPS[_GROUP_MEMBERS[key]]
    stem = spec["text"][:40]
    rows = [r for r in index if r.startswith(stem)]
    if not rows:
        return "drift", f"group passage '{stem}...' is not in the index"
    fig = _figure_of(_fact_value(locked[key]))
    if fig and not any(fig in r for r in rows):
        return "drift", f"group passage no longer contains this key's figure {fig!r}"
    return "grouped", None


def check(facts_path=FACTS_PATH, index_path=INDEX_PATH):
    locked = json.load(open(facts_path, encoding="utf-8"))
    index = json.load(open(index_path, encoding="utf-8"))
    index_slugs = [f.split(":")[0].strip().lower() for f in index]

    report = {
        "exact": [], "sibling": [], "grouped": [], "present_elsewhere": [],
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
        if any(_is_sibling(slug, s) for s in index_slugs):
            report["sibling"].append(key)
            continue
        if key in _GROUP_MEMBERS:
            verdict, reason = _grouped_verdict(key, locked, index)
            if verdict == "grouped":
                report["grouped"].append(key)
            else:
                report["drift_pin_stale"].append(
                    {"key": key, "pinned_row": None, "expected_substring": reason,
                     "row_now": None})
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
    print(f"  grouped (consolidated)   {len(report['grouped'])}")
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
