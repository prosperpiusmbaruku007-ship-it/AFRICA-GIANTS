# -*- coding: utf-8 -*-
"""BACKFILL PASS 1: attach a source-register key to every gate gold answer whose claim has been
read against a primary source, and report disagreements WITHOUT changing them.

WHY, measured not assumed (eval/results/gold_answer_provenance_audit.json): 73 of 276 gold
answers assert a figure, rate or deadline a statute could confirm and cite NOTHING -- all 73 in
the 78 and the 48, whose schemas had no source field at all. A wrong gold answer is booked as a
model failure forever, because the adjudication reads the key.

SOURCED AGAINST THE REGULATOR OR THE STATUTE, NOT AGAINST locked_facts.json. Checking a gold
answer against our own fact store compares us to ourselves: efd_threshold_tzs_11m was fabricated
and sat in locked_facts for months while eval_355's gold matched it, and a consistency check
would have called that pair clean. Every entry in eval/accuracy_gate/gold_source_register.json
was fetched directly, with HTTP status and byte count recorded.

⛔ THIS PASS DOES NOT CHANGE A SINGLE GOLD ANSWER. A gold answer that disagrees with the source
is a SCORING-KEY CORRECTION, and a scoring-key correction moves a failure count -- so each one is
reported for a decision, never absorbed into a backfill commit. The repository has 6 such
corrections and every one was found by accident; they are visible precisely because they were
recorded as corrections rather than edited away. `DISAGREEMENTS` below is the report.

MATCHING IS CONSERVATIVE AND THAT IS DELIBERATE. A row is sourced only when its gold answer
asserts the register entry's quantity in a form this script can confirm -- the figure AND the
subject. A row whose gold merely mentions a levy is left PENDING with the instrument that would
settle it named. Over-assigning a source is worse than leaving a row pending: a wrong citation
reads as verified and is the CITED-AND-CONTRADICTED shape this project already found once
(tier1a_wh_009, a 10%/15% claim citing the page that says 10%/10%).

Usage:  python eval/controls/backfill_gold_provenance.py           (report only)
        python eval/controls/backfill_gold_provenance.py --write   (apply source fields)
Artifact: eval/results/gold_provenance_backfill_pass1.json
"""
import json
import os
import re
import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REGISTER = os.path.join(REPO, "eval", "accuracy_gate", "gold_source_register.json")
OUT = os.path.join(REPO, "eval", "results", "gold_provenance_backfill_pass1.json")
AUDIT = os.path.join(REPO, "eval", "results", "gold_answer_provenance_audit.json")

FIXTURES = ("eval/accuracy_gate/edge_probe_extended_078_DRAFT.jsonl",
            "eval/accuracy_gate/edge_probe_natural_048.jsonl")
GOLD_KEYS = ("expected_behavior", "correct_answer_sw", "correct_answer_en")

# claim key -> (subject pattern, quantity pattern). BOTH must match the gold answer. The subject
# limb is what stops a bare figure match: "500,000" is a salary in four rows and a BRELA fee in
# none of them.
RULES = {
    "sdl_rate_and_threshold": (r"\bSDL\b|mafunzo|skills? development",
                               r"3\.5\s*%|asilimia\s+3\.5"),
    "vat_registration_threshold": (r"VAT|usajili|registration|kizingiti",
                                   r"200[,\s]?000[,\s]?000|200\s*(?:million|milioni)|"
                                   r"100[,\s]?000[,\s]?000|100\s*(?:million|milioni)"),
    "vat_standard_rate": (r"\bVAT\b", r"\b18\s*%|asilimia\s+18"),
    "paye_nonresident_flat_rate": (r"non-?resident|si\s+mkazi|mgeni",
                                   r"\b15\s*%|asilimia\s+15"),
    "wcf_rate_and_base": (r"\bWCF\b|fidia", r"0\.5\s*%|asilimia\s+0\.5"),
    # SUBJECT NARROWED after the dry run assigned this to nat_24, a payroll-levy triage row
    # (SDL/WCF/NSSF) with no rental content at all -- the old subject limb accepted a bare
    # "withhold" and the quantity limb found a 10%. A rent-WHT citation on a payroll row is the
    # CITED-AND-CONTRADICTED shape this project already found once (tier1a_wh_009: a 10%/15%
    # claim citing the page that says 10%/10%). Rent must be the SUBJECT, not an adjacent word.
    "rent_wht_rate": (r"\bpango\b|\brental\b|\brent\b", r"\b10\s*%|asilimia\s+10"),
    "brela_annual_return_and_penalties": (r"BRELA|annual return|taarifa ya mwaka|"
                                          r"late[- ]filing|kuchelewesha",
                                          r"22,000|2,500|95,000"),
}

# Disagreements found while sourcing. REPORTED, NOT APPLIED -- each is a scoring-key or
# locked-fact correction and moves a number, so it is the founder's call (Gate 2 sign-off is
# blocking; no automation substitute).
DISAGREEMENTS = [
    {
        "what": "🔴 SETTLED AGAINST US BY THE STATUTE. CLAUDE.md Section 11 and ext_15's gold "
                "cite the foreign-company provisions as 'Companies Act Cap.212, Part XIII, "
                "ss.320-328', and Section 11 adds 'NOT \"Section XII\"; corrected 2026-08-31'. "
                "BOTH LIMBS ARE WRONG AND THE 2026-08-31 'correction' INTRODUCED THE ERROR.",
        "source_says": "Companies Act, Revised Edition 2023, read directly (394pp, 3.2MB PDF "
                       "hosted on brela.go.tz, HTTP 200, fetched 2026-10-04): 'PART XII "
                       "COMPANIES INCORPORATED OUTSIDE TANZANIA', opening at s.437 whose own "
                       "text reads 'Sections 438 to 447 shall apply to all foreign companies'. "
                       "PART XIII is 'GENERAL PROVISIONS AS TO REGISTRATION' (ss.454+). "
                       "ss.320-328 are WINDING-UP provisions -- orders against contributories, "
                       "the official receiver, fraud in winding up -- and have nothing to do "
                       "with foreign companies.",
        "so_the_correct_citation_is": "Cap.212 R.E. 2023, Part XII, ss.437-447",
        "affects_a_gate_gold": True,
        "affected_rows": ["ext_15"],
        "assessment": "THE REGULATOR'S PAGE WAS RIGHT AND WE OVERRULED IT. Disagreement 3 below "
                      "originally recorded BRELA's 'Sehemu ya XII' as regulator imprecision and "
                      "said DO NOT FLIP, on the correct general principle that a portal summary "
                      "is not the statute. Reading the statute reversed it. The principle held; "
                      "the application was wrong, and only the primary text could show which.",
        "renumbering_trap": "The Act's own source note on s.437 reads '[s. 433]' -- R.E. 2023 "
                            "renumbered Cap.212 throughout. CLAUDE.md documents this trap for "
                            "Cap.332/Cap.438 ('s.35 -> s.43'); this is the same trap in Cap.212, "
                            "and it is the likeliest origin of a stale section range.",
        "status": "REPORTED_NOT_CHANGED -- a citation correction is still a scoring-key "
                  "correction and still moves a verdict's basis; founder's call.",
    },
    {
        "what": "⛔ AFFECTS A GATE GOLD ANSWER, AND IS NOT SETTLEABLE FROM THE ACT. ext_15's "
                "gold asserts a foreign company's late-filing penalty is USD 25 per month. "
                "CLAUDE.md Section 11 says the same.",
        "source_says": "TZS 70,000 per month or part month. brela.go.tz/pages/tozo-za-kampuni "
                       "item 15(iv), under 'Ada chini ya Masharti ya Sehemu ya XII ya Sheria "
                       "(Makampuni ya Nje)': 'Kwa kutowasilisha au kuchelewesha kuwasilisha "
                       "hati yoyote inayotakiwa kuwasilishwa kwa Msajili, kwa kila mwezi au "
                       "sehemu ya mwezi wa kuchelewa. 70,000/='",
        "fetched": "2026-10-04 (HTTP 200, 57,804 bytes)",
        "affects_a_gate_gold": True,
        "affected_rows": ["ext_15"],
        "assessment": "THIS IS A SCORING-KEY CORRECTION CANDIDATE AND IT MOVES A FAILURE COUNT, "
                      "so it is reported and not applied. ext_15 is currently adjudicated WRONG "
                      "with cause=model; if the gold is wrong the row's verdict is unsafe in "
                      "either direction until a human decides. NOTE THE R29 SHAPE: USD 25 is "
                      "roughly TZS 65,000-70,000 at current rates, so the likeliest reading is "
                      "CORRECTLY-CITED-BUT-SUPERSEDED -- a real earlier fee schedule denominated "
                      "in dollars, replaced by a shilling figure. That is mode 3, the one no "
                      "check in this project would have caught, and it is why the fee schedule "
                      "needs reading rather than the Act alone: Cap.212 may still say USD 25 "
                      "while the current GN fee schedule says 70,000.",
        "what_would_settle_it": "ONLY the Companies (Fees) Regulations. THE ACT CANNOT SETTLE "
                                "IT, now established rather than assumed: s.458 reads 'The "
                                "Minister may by regulations require the payment to the "
                                "Registrar of such fees as may be specified in the "
                                "regulations', and s.489(3) 'The fees to be paid under this Act "
                                "shall be as the Minister may prescribe in regulations'. The "
                                "Act contains no fee amounts at all.",
        "search_performed": "brela.go.tz/pages/sheria-na-kanuni and /pages/machapisho both "
                            "HTTP 500; tanzlii.org/search is a client-rendered SPA returning no "
                            "results to curl; two web searches surfaced only practitioner "
                            "summaries and fee-aggregator blogs (one gives USD 220 filing / USD "
                            "25 per delayed month, consistent with our record but secondary and "
                            "undated as to which schedule it describes -- R29's exact trap). "
                            "The Regulations' own text was NOT located.",
        "currency_caveat_accepted": "The earlier 'USD 25 is roughly TZS 65-70k' note is an "
                                    "INFERENCE and is withdrawn as evidence. A change of "
                                    "denomination is a substantive amendment, not a rounding, "
                                    "and two figures being numerically close is not grounds to "
                                    "treat one as the other.",
        "status": "UNRESOLVED -- GOLD UNCHANGED. The honest state: BRELA's published schedule "
                  "says TZS 70,000, our record says USD 25, the Act delegates the question, and "
                  "the instrument that would answer it was not found. Recorded as a standing "
                  "disagreement with both sources named rather than resolved in either "
                  "direction.",
    },
    {
        "what": "locked fact / CLAUDE.md Section 11 -- 'Company without share capital: "
                "TZS 300,000 registration fee'",
        "source_says": "TZS 500,000. brela.go.tz/pages/tozo-za-kampuni item 2: 'Usajili wa "
                       "Kampuni ambayo haina mtaji wa hisa 500,000/='",
        "fetched": "2026-10-04 (HTTP 200, 57,804 bytes)",
        "affects_a_gate_gold": False,
        "checked": "No row among the 73 asserts this figure -- searched for '300,000' and for "
                   "share-capital subject terms across both fixtures. The three '300,000' and "
                   "four '500,000' matches are all wages or salaries in other rows.",
        "recommendation": "HOLD. Same reasoning as the USD-25 row and the same instrument: the "
                          "Act sets no fee amounts (s.458, s.489(3)), so only the Companies "
                          "(Fees) Regulations can confirm 500,000, and they were not located. "
                          "A figure is not flipped onto a source already shown unreliable on a "
                          "neighbouring point -- and on the Part XII/XIII point that same page "
                          "turned out to be RIGHT, which cuts both ways: it is unreliable in "
                          "neither direction predictably, so it needs the gazette either way. "
                          "No gate number moves, so there is no cost to waiting; when the "
                          "Regulations are read, fold any change into the queued R15 regen as a "
                          "third fact behind rent_wht_rate and ext_31 -- one cycle, not two.",
        "status": "UNRESOLVED -- UNCHANGED",
    },
    {
        "what": "BRELA's own fee page labels the foreign-company part of the Companies Act "
                "'Sehemu ya XII'",
        "source_says": "'15 Ada chini ya Masharti ya Sehemu ya XII ya Sheria (Makampuni ya "
                       "Nje)' -- i.e. Part XII",
        "our_record": "CLAUDE.md Section 11 says Part XIII, ss.320-328, and explicitly 'NOT "
                      "\"Section XII\"; corrected 2026-08-31'. ext_15's gold cites Part XIII.",
        "affects_a_gate_gold": True,
        "affected_rows": ["ext_15"],
        "assessment": "DO NOT FLIP. The 2026-08-31 correction was made against the Act; this is "
                      "the regulator's own page being imprecise, which CLAUDE.md already "
                      "documents as a known failure mode ('The regulator's own summary is not "
                      "the statute either'). Recorded because it is almost certainly the ORIGIN "
                      "of the original Part XII error, and because a future reader fetching "
                      "this page will hit the same contradiction and needs to find this note "
                      "rather than re-derive it.",
        "status": "REPORTED_NOT_CHANGED",
    },
]


# ---------------------------------------------------------------------------------------------
# 🔴 A TOOL THAT ATTACHES EVIDENCE IS A TOOL THAT CAN FABRICATE EVIDENCE.
#
# Its own finding, recorded here rather than in a commit message, because it is a property of
# this CLASS of tool and the next provenance pass will have it too.
#
# This script exists to prevent CITED-AND-CONTRADICTED gold answers -- the fourth citation shape
# (2026-09-26): a claim that names a source which does not support it, invisible to every
# provenance check we own because they all verify a citation is PRESENT and WELL-FORMED, never
# that it SUPPORTS the claim. tier1a_wh_009 is the known instance: a 10%/15% rent-WHT assertion
# citing the TRA page whose table reads 10%/10%.
#
# THE FIRST DRY RUN OF THIS SCRIPT WOULD HAVE MANUFACTURED THREE OF THEM:
#
#   nat_24  <- rent_wht_rate       a payroll-levy TRIAGE row (SDL/WCF/NSSF, 9 employees) with no
#                                  rental content whatsoever. The subject limb accepted a bare
#                                  "withhold" and the quantity limb found a 10% belonging to
#                                  NSSF. A rent-WHT citation would have been stamped on it.
#   ext_15  <- brela_...penalties  matched on a "2,500" the gold mentions only as the CONTRAST
#                                  it is refuting. Its actual claim -- the foreign company's
#                                  USD 25/month -- is the one figure in this whole pass that the
#                                  source CONTRADICTS, so the citation would have pointed at a
#                                  page saying something else.
#   ext_58/59, nat_23/24           would have read as fully sourced while asserting an NSSF 20%
#                                  split that nothing in the register covers.
#
# NONE OF IT REACHED A FILE, and the reason is structural rather than careful: the script has a
# REPORT_ONLY default and writes only under --write, so every assignment was printed and read
# before anything was stamped. That is the dry-run-before-write rule doing the work, not
# vigilance -- vigilance is what fails on the twentieth row.
#
# THE ASYMMETRY THAT MAKES THIS WORSE THAN A MISSING CITATION: an absent source is VISIBLE and
# was in fact the finding that started this work (73 rows, counted). A WRONG source is invisible
# and actively misleading -- it reads as verified, and the next reader has no reason to re-check
# it. So a provenance tool's false positives cost more than its false negatives, which is R26's
# asymmetry arriving in the evidence layer instead of the audit layer.
#
# CONSEQUENCE FOR PASS 2 AND AFTER: a claim rule must match the SUBJECT, not merely a number
# near a keyword; a quantity the register cannot settle must surface as `source_partial` rather
# than be silently covered by a sibling claim; and no pass writes until its dry run is read in
# full. Three of twenty-one assignments were wrong on the first attempt -- a 14% error rate on
# a mechanical pass, which is the rate to expect next time, not an anomaly.
# ---------------------------------------------------------------------------------------------


def rows_of(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def gold_of(row):
    return " ".join(str(row.get(k, "")) for k in GOLD_KEYS)


# Quantities asserted by gate gold answers for which NO register entry exists yet. A row whose
# gold asserts one of these is PARTIALLY sourced at best, and saying "sourced" would overstate it
# -- the row would read as provenanced while half its claim rests on nothing. ext_58 is the case
# that forced this: its gold asserts SDL 3.5% (sourced today) AND NSSF 20% (not sourced -- the
# NSSF Act was not read, and nssf.go.tz/pages/contributions returns HTTP 500 on retry).
UNSOURCED_CLAIMS = {
    "nssf_contribution_split": (r"\bNSSF\b|uzeeni|pension",
                                r"\b20\s*%|asilimia\s+20|\b10\s*%\s*(?:x|×)|employee 10%"),
    "presumptive_schedule": (r"presumptive|makadirio", r"\d"),
    # ext_15 forced this one. The register's BRELA entry covers the LOCAL 2,500/month penalty;
    # ext_15's actual claim is the FOREIGN company's USD 25/month, which the live fee schedule
    # CONTRADICTS at TZS 70,000 (see DISAGREEMENTS). The gold mentions 2,500 only as a contrast,
    # so matching the entry on it would have put a citation on a contested claim -- the
    # CITED-AND-CONTRADICTED shape, manufactured by my own matcher.
    "foreign_company_late_filing_penalty": (r"foreign compan|kampuni ya (?:ki)?geni|tawi",
                                            r"USD\s*25|\b25\s*(?:per|kwa|/)"),
    "corporate_rate_or_amt": (r"corporate|kampuni|AMT|alternative minimum",
                              r"\b30\s*%|\b25\s*%|\b1\s*%|\b0\.5\s*%"),
    "paye_resident_bands": (r"\bPAYE\b", r"270,000|520,000|760,000|128,000|68,000"),
}


def match_claims(gold):
    out = []
    for key, (subject, quantity) in RULES.items():
        if re.search(subject, gold, re.I) and re.search(quantity, gold, re.I):
            out.append(key)
    return out


def unsourced_residue(gold):
    """Claims in this gold answer that no register entry can settle yet."""
    return [k for k, (subject, quantity) in UNSOURCED_CLAIMS.items()
            if re.search(subject, gold, re.I) and re.search(quantity, gold, re.I)]


def main():
    write = "--write" in sys.argv
    register = json.load(open(REGISTER, encoding="utf-8"))
    pending_ids = {r["id"] for r in json.load(open(AUDIT, encoding="utf-8"))["rows"]
                   if r["gold_is_checkable"] and not r["has_source"]}

    # R20: the matcher must be able to match. A rule set that matches nothing would report a
    # clean "0 sourced" and look like honest conservatism.
    assert register and all(k in register for k in RULES), (
        "RULES names claim keys absent from the register")

    sourced, still_pending, changed_files = [], [], {}
    for rel in FIXTURES:
        rows = rows_of(rel)
        dirty = False
        for row in rows:
            rid = row.get("id")
            if rid not in pending_ids:
                continue
            gold = gold_of(row)
            claims = match_claims(gold)
            residue = unsourced_residue(gold)
            if claims:
                sourced.append({"id": rid, "file": rel, "claims": claims,
                                "urls": [register[c]["url"] for c in claims],
                                "fully_sourced": not residue,
                                "claims_still_unsourced": residue,
                                "gold": gold[:200]})
                if write:
                    row["source"] = claims if len(claims) > 1 else claims[0]
                    # A row whose gold also asserts something no register entry covers must say
                    # so IN THE ROW. Otherwise `source` reads as a full warranty on a gold
                    # answer that is half unverified, which is worse than no source at all.
                    if residue:
                        row["source_partial"] = residue
                    dirty = True
            else:
                still_pending.append({"id": rid, "file": rel,
                                      "claims_still_unsourced": residue,
                                      "gold": gold[:200]})
        if write and dirty:
            changed_files[rel] = rows

    if write:
        for rel, rows in changed_files.items():
            with open(os.path.join(REPO, rel), "w", encoding="utf-8") as fh:
                for row in rows:
                    fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    artifact = {
        "measured": str(date.today()),
        "harness": "eval/controls/backfill_gold_provenance.py",
        "register": "eval/accuracy_gate/gold_source_register.json",
        "pass": 1,
        "mode": "WRITE" if write else "REPORT_ONLY",
        "what_this_does": ("Attaches a source-register key to gate gold answers whose claim has "
                           "been read against a primary source. Changes no gold answer."),
        "sourced_against": "the regulator's own page or the statute, fetched directly -- never "
                           "locked_facts.json, which would compare us to ourselves",
        "totals": {"rows_needing_provenance_at_pass_start": len(pending_ids),
                   "sourced_this_pass": len(sourced),
                   "still_pending": len(still_pending),
                   "fully_sourced": sum(1 for s_ in sourced if s_["fully_sourced"]),
                   "partially_sourced": sum(1 for s_ in sourced
                                            if not s_["fully_sourced"]),
                   "register_entries": len(register) - 5},
        "disagreements_reported_not_changed": DISAGREEMENTS,
        "sourced": sourced,
        "still_pending": still_pending,
        "what_remains": ("Rows still pending need instruments not yet read directly: the "
                         "presumptive First Schedule as amended (FA2022 s.72, FA2026 s.27(a)), "
                         "Cap.332 s.4 for the corporate rate and the AMT, the NSSF Act for the "
                         "20% split (nssf.go.tz/pages/contributions returns HTTP 500 -- a real "
                         "block, retried, not a tool fault), Cap.297 for OSHA, Cap.408 s.17 for "
                         "TRAB, and GN 605A. Named per row rather than left as a count."),
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(artifact, fh, ensure_ascii=False, indent=2)

    t = artifact["totals"]
    print(f"mode: {artifact['mode']}")
    print(f"rows needing provenance:     {t['rows_needing_provenance_at_pass_start']}")
    print(f"sourced this pass:           {t['sourced_this_pass']}")
    print(f"still pending:               {t['still_pending']}")
    print()
    for s in sourced:
        tag = "" if s["fully_sourced"] else f"   PARTIAL, unsourced: {s['claims_still_unsourced']}"
        print(f"  {s['id']:8} <- {', '.join(s['claims'])}{tag}")
    print()
    print(f"DISAGREEMENTS REPORTED (not changed): {len(DISAGREEMENTS)}")
    for d in DISAGREEMENTS:
        print(f"  * {d['what'][:88]}")
        print(f"    source says: {d['source_says'][:96]}")
        print(f"    affects a gate gold: {d['affects_a_gate_gold']}")
    print(f"\n[saved] {os.path.relpath(OUT, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
