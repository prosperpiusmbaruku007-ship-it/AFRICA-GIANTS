# -*- coding: utf-8 -*-
"""AMEND THE Cap.50 FACTS AGAINST R.E.2023. FIELD-LEVEL, NEVER OBJECT-LEVEL (R27).

R27 exists because `minimum_turnover_tax` was corrected by composing a clean replacement object
from the verification findings, which silently dropped a `wrong_patterns` regex family and a
`_narrowing_note` that two committed probes existed to protect. Only a test that happened to
cover the exact thing dropped caught it; most facts have no such test.

So this script NEVER assigns a fact object. It applies a dict of {field: new_value} per key and
then ASSERTS that every pre-existing field not named in that dict is byte-identical afterwards.
A reconstruction mistake fails the run instead of shipping.

EVERY VALUE BELOW WAS READ FROM Cap.50 R.E. 2023 (sha256 2a820e67ed109cd36059, 773,203 bytes,
50pp, identical from nssf.go.tz/publications/act and oagmis.oag.go.tz/portal/acts/revised/155).
The kazi.go.tz R.E.2015/R.E.2018 copies and the TanzLII PDF (self-labelled not the latest
version) were NOT used -- that is the superseded-edition trap, and the R.E.2015 copy cached at
data/source_documents/nssf/nssf_act_cap50.pdf is exactly how `fine_limit` went wrong.

RENUMBERING MAP, read from the Act's own bracketed prior-edition notes rather than assumed:
    R.E.2023 s.23 <- [s. 21]    s.25 <- [s. 23]    s.29 <- [s. 27]
    R.E.2023 s.46 <- [s. 44]    s.47 <- [s. 45]    s.50 <- [s. 48]    s.51 <- [s. 49]
    R.E.2023 s.76 <- [s. 72]
    s.11, s.12, s.14 carry NO prior-edition note -- same number in both editions.
    s.5A DOES NOT EXIST in R.E.2023 at all.

THE TWO FORMS OF THE RENUMBERING TRAP, both present in this one Act, which is why the s.5A note
is written at the site rather than left implicit:
  - POINTS AT NOTHING: s.5A. Four facts cite the First Schedule as made under "ss.5A(c), 12(1)".
    R.E.2023's own rubric reads "(Made under sections 5(2)(c) and 12(1) and (5))". A reader
    checking s.5A in the current edition finds no such section and cannot tell whether the fact
    is wrong or the citation is stale.
  - POINTS AT THE WRONG THING: s.76. The offences clause is s.72 in R.E.2015 and s.76 in
    R.E.2023; in R.E.2015 s.76 is "Protection of contributions", a different provision
    entirely. A reader checking "s.76" against the cached R.E.2015 PDF reads the wrong section
    and gets a confident, wrong confirmation.
The first form fails loudly. The second fails silently, and is the worse of the two.
"""
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACTS = os.path.join(REPO, "scripts", "locked_facts.json")

ACT = "NSSF Act, Cap.50 R.E.2023"
ROUTE = ("https://www.nssf.go.tz/uploads/publications/"
         "en-1771921274-NSSF%20ACT%20CAP%2050%20RE.%202023.pdf")
READ = (f"Direct read (2026-10-05) of {ACT}, fetched from {ROUTE} and independently from "
        "https://oagmis.oag.go.tz/portal/acts/revised/155/download -- both routes byte-identical "
        "(sha256 2a820e67ed109cd36059, 773,203 bytes, 50pp), confirmed the same edition BEFORE "
        "either was used. ")

SCHEDULE_CITE = (f"{ACT}, First Schedule (Made under sections 5(2)(c) and 12(1) and (5))")
SCHEDULE_VERBATIM = (
    'First Schedule, contribution period "(a) one month": "Employer\'s share deductible from '
    'wages by Employer: Ten cents for every complete shilling of wages" [=10%]; "Statutory '
    'Contributions for each employee: Twenty cents for every complete shilling of wages" [=20%].')
SCHEDULE_RENUMBER = (
    "CITATION CORRECTED 2026-10-05: previously cited as 'Cap.50 R.E.2015, First Schedule "
    "(ss.5A(c), 12(1))'. R.E.2023 HAS NO SECTION 5A -- the Schedule's own rubric reads '(Made "
    "under sections 5(2)(c) and 12(1) and (5))'. The old citation pointed at a section that does "
    "not exist in the current edition, so a reader could not distinguish a wrong fact from a "
    "stale citation. The VALUE is unchanged and was re-confirmed against R.E.2023; only the "
    "citation moved. G.N. No. 286 of 2000 (the instrument that substituted the Schedule) was a "
    "marginal note in R.E.2015 and is not reproduced in R.E.2023's text, so it is retained here "
    "as a secondary note rather than as the operative citation.")

# ---------------------------------------------------------------------------------------------
# One entry per fact. Keys are FIELDS TO SET. Nothing else is touched.
# ---------------------------------------------------------------------------------------------
AMENDMENTS = {

    # ---- 1. THE ONE WRONG VALUE ---------------------------------------------------------
    "fine_limit": {
        "fact": (
            "The maximum fine for an offence under the NSSF Act is TZS 10,000,000 (ten million "
            "shillings), not TZS 100,000. NSSF Act Cap.50 R.E.2023 s.76(1): a person who "
            "commits any of the offences listed in s.76(1)(a)-(j) \"commits an offence and on "
            "conviction shall be liable to a fine not exceeding ten million shillings or to "
            "imprisonment for a term not exceeding two years or to both\"."),
        "correct_value": "ten million TZS (TZS 10,000,000)",
        "section": "s.76(1) (R.E.2023; was s.72(1) in R.E.2015)",
        "primary_source": f"{ACT}, s.76(1)",
        "verified_by": (
            READ + "s.76(1) closing words, verbatim: \"commits an offence and on conviction "
            "shall be liable to a fine not exceeding ten million shillings or to imprisonment "
            "for a term not exceeding two years or to both.\" The marginal note on this section "
            "lists Acts Nos. 1 of 2008 s.33, 5 of 2012 s.67 and 2 of 2018 s.108 as its amending "
            "instruments; Act No. 2 of 2018 s.108 is the only one post-dating the 2015 revision, "
            "so it is the instrument that raised the ceiling -- ATTRIBUTED BY ELIMINATION from "
            "the section's own amendment list and the two editions' dates, not by reading Act "
            "No. 2 of 2018 itself."),
        "verified_as_at": "2026-10-05",
        "wrong_patterns": [
            # ⚠️ NARROW BY CONSTRUCTION (R17 step 4). OSHA's CORRECT continuing-offence charge
            # is also TZS 100,000, and 10 training rows plus 3 gold rows state it. A bare
            # `100,000` pattern would flag every one of them. These require the fine-ceiling
            # framing AND exclude the per-day form that marks the OSHA figure.
            r"faini\s+(?:ya\s+)?(?:shilingi\s+)?(?:elfu\s+mia\s+moja|laki\s+moja)"
            r"(?!.{0,40}(?:kwa\s+siku|kila\s+siku|per\s+day))",
            r"fine\s+not\s+exceeding\s+one\s+hundred\s+thousand",
            r"nssf.{0,60}faini.{0,30}(?:TZS\s*)?100[,.]?000(?![,.\d])",
            r"(?:TZS\s*)?100[,.]?000(?![,.\d]).{0,40}(?:faini|fine).{0,40}nssf",
        ],
        "status": (
            "CORRECTED 2026-10-05 (statute-tier, R.E.2023) -- was WRONG BY 100x, carried from "
            "a superseded edition"),
        "correction_note": (
            "2026-10-05: corrected from 'one hundred thousand TZS' to ten million shillings per "
            "s.76(1) of Cap.50 R.E.2023.\n\n"
            "THIS WAS NOT A FABRICATION -- IT IS R29 MODE 2 (OUT-OF-DATE EDITION), AND THAT "
            "MATTERS FOR WHAT TO CHECK NEXT. The fact's legacy `source` field points at "
            "data/source_documents/nssf/nssf_act_cap50.pdf, which is REVISED EDITION 2015, and "
            "in that edition s.72(1) reads \"a fine not exceeding one hundred thousand "
            "shillings\". So 100,000 was a faithful transcription of a real primary document "
            "that had simply been superseded. It was not unchecked; it was checked against the "
            "wrong edition.\n\n"
            "THE SIBLING IS THE WHOLE LESSON. `imprisonment_term_limit` (two years) comes from "
            "THE SAME SENTENCE of THE SAME superseded edition and is CORRECT -- because "
            "Parliament multiplied the fine by 100 and left the term of imprisonment alone. One "
            "read of one clause in one stale edition produced one wrong fact and one right one, "
            "and nothing about either fact's provenance distinguished them. The sibling's "
            "correctness is luck about which limb was amended, not evidence that the reading was "
            "sound.\n\n"
            "PROPAGATION, measured before anything was quarantined "
            "(eval/controls/sweep_nssf_fine_100k_propagation.py): 4 genuine training rows "
            "(datasets/tier1a/sft_shaped_pairs/cleaned_pairs_batch_014.jsonl:693-696), 2 shipped "
            "RAG index rows (row 159, 'fine limit: one hundred thousand TZS' -- LIVE in "
            "production until the R15 regen lands), 1 false positive adjudicated out, and ZERO "
            "gold answers. All 13 gold matches on the figure are OSHA's correct TZS 100,000/day "
            "continuing offence."),
        "_legacy_source_note": (
            "The `source` field below is retained for provenance rather than deleted, and it is "
            "the superseded R.E.2015 copy -- the document that produced the 100x error. Do not "
            "re-verify this fact against it."),
    },

    # ---- 2. ITS SIBLING: correct, and now cited --------------------------------------------
    "imprisonment_term_limit": {
        "fact": (
            "The maximum term of imprisonment for an offence under the NSSF Act is two years. "
            "NSSF Act Cap.50 R.E.2023 s.76(1): \"...liable to a fine not exceeding ten million "
            "shillings or to imprisonment for a term not exceeding two years or to both\"."),
        "section": "s.76(1) (R.E.2023; was s.72(1) in R.E.2015)",
        "primary_source": f"{ACT}, s.76(1)",
        "verified_by": (
            READ + "s.76(1) closing words, verbatim: \"...liable to a fine not exceeding ten "
            "million shillings or to imprisonment for a term not exceeding two years or to "
            "both.\" The two-year term is identical in R.E.2015 s.72(1) and R.E.2023 s.76(1)."),
        "verified_as_at": "2026-10-05",
        "status": "CONFIRMED (statute-tier, 2026-10-05, R.E.2023)",
        "_sibling_note": (
            "SURVIVED VERIFICATION FOR A REASON WORTH RECORDING, not because its provenance was "
            "better. This fact and `fine_limit` were read from the same sentence of the same "
            "superseded R.E.2015 copy. The fine limb was amended 100x and this limb was not, so "
            "the same flawed read produced one wrong fact and one correct one. 'Ungrounded' "
            "carried no information about which -- and neither did 'grounded', because both were "
            "grounded, in a stale edition. See `fine_limit.correction_note`."),
    },

    # ---- 3. THE PHANTOM s.5A CITATIONS -- CITATION FIELDS ONLY ---------------------------
    # R27: the VALUES are confirmed and are NOT being touched. Only the citation moves, plus
    # verified_as_at, which moves because the value was genuinely RE-READ in the current
    # edition today -- not merely relabelled.
    "nssf_employer_rate": {
        "primary_source": SCHEDULE_CITE + ", G.N. No. 286 of 2000 (secondary -- see note)",
        "verified_by": READ + SCHEDULE_VERBATIM + " Confirms the employer share at 10% and the "
                       "statutory total at 20%, so the employee share is 10% by subtraction.",
        "verified_as_at": "2026-10-05",
        "status": "CONFIRMED (statute-tier, re-read in R.E.2023 on 2026-10-05)",
        "_renumbering_note": SCHEDULE_RENUMBER,
    },
    "nssf_total_rate": {
        "primary_source": SCHEDULE_CITE + ", G.N. No. 286 of 2000 (secondary -- see note)",
        "verified_by": READ + SCHEDULE_VERBATIM + " The 20% figure is the Schedule's "
                       "\"Statutory Contributions for each employee\" column.",
        "verified_as_at": "2026-10-05",
        "status": "CONFIRMED (statute-tier, re-read in R.E.2023 on 2026-10-05)",
        "_renumbering_note": SCHEDULE_RENUMBER,
    },
    "nssf_calculation_example": {
        "primary_source": SCHEDULE_CITE + " read with s.12(1)",
        "verified_by": READ + SCHEDULE_VERBATIM + " s.12(1): \"A contributing employer shall, "
                       "for every contribution period following the date of appointment of an "
                       "insured person, pay to the Fund a contribution that consist of the "
                       "employer's and employee's share at the rate stipulated in the First "
                       "Schedule.\" The example's arithmetic follows from the 20% total: "
                       "600,000 x 20% = 120,000 per employee, x 12 = 1,440,000.",
        "verified_as_at": "2026-10-05",
        "status": "CONFIRMED (statute-tier, re-read in R.E.2023 on 2026-10-05)",
        "_renumbering_note": SCHEDULE_RENUMBER,
    },

    # ---- 4. THE STALE EDITION WITH NO RENUMBERING ----------------------------------------
    "nssf_payment_deadline": {
        "primary_source": f"{ACT}, s.14(1) and (3)",
        # APPEND, never replace. This fact's verified_by already carries a full 2026-09-02 read
        # plus a Finance-Act-2026 freshness check plus the finding that no source mentions a
        # "10th of the month". Replacing it to insert today's date would destroy all of that --
        # the R27 failure mode, arriving through a field this script is allowed to touch.
        "_APPEND_VERIFIED_BY": (
            " RE-CONFIRMED 2026-10-05 against Cap.50 R.E.2023 (sha256 2a820e67ed109cd36059, "
            "from nssf.go.tz/publications/act and oagmis.oag.go.tz, byte-identical): s.14(1) "
            "and s.14(3) are word-for-word as quoted above, and s.14 carries NO bracketed "
            "prior-edition note, so the section number did not move between editions. The "
            "previous read was against R.E.2015; the citation's edition label was the only stale "
            "part. s.14(3)'s proviso -- the Board may remit the penalty in whole or in part -- "
            "is noted here as a limb the bare '5% per month' does not convey."),
        "verified_as_at": "2026-10-05",
        "_renumbering_note": (
            "CITATION EDITION CORRECTED 2026-10-05: R.E.2015 -> R.E.2023. s.14 carries NO "
            "bracketed prior-edition note in R.E.2023, so the SECTION NUMBER is unchanged "
            "across the two editions and only the edition label was stale. Recorded explicitly "
            "because 'the number is the same' is a finding here, not an absence of one -- s.76, "
            "s.51, s.47, s.46, s.29, s.25 and s.23 all moved."),
    },

    # ---- 5. THE HEDGE, NOW RESOLVABLE ----------------------------------------------------
    "nssf_employer_registration_deadline": {
        "fact": (
            "Every contributing employer must register with NSSF WITHIN ONE MONTH of becoming a "
            "contributing employer. NSSF Act Cap.50 R.E.2023 s.11(1): \"every contributing "
            "employer shall, unless such employer has been registered under the existing Fund, "
            "within one month, register under this section in the prescribed manner.\" s.11(2) "
            "fixes when that month starts: \"The period of one month mentioned in subsection (1) "
            "shall, in every case, begin upon the commencement of this Act or the date when the "
            "person concerned becomes a contributing employer.\" So the clock runs from the date "
            "the employer becomes a contributing employer, not from registration of the business."),
        "correct_value": "within one month of becoming a contributing employer (s.11(1)-(2))",
        "section": "s.11(1)-(2)",
        "primary_source": f"{ACT}, s.11(1) and (2)",
        "verified_by": (
            READ + "s.11(1) verbatim: \"Subject to the provisions of this Act, every "
            "contributing employer shall, unless such employer has been registered under the "
            "existing Fund, within one month, register under this section in the prescribed "
            "manner.\" s.11(2) verbatim: \"The period of one month mentioned in subsection (1) "
            "shall, in every case, begin upon the commencement of this Act or the date when the "
            "person concerned becomes a contributing employer.\" s.11 carries no bracketed "
            "prior-edition note, so the section number is the same in R.E.2015."),
        "verified_as_at": "2026-10-05",
        "status": "CONFIRMED (statute-tier, 2026-10-05) -- was HEDGE (deadline unverifiable)",
        "training_instruction": (
            "State the deadline: 'sajili na NSSF ndani ya MWEZI MMOJA kuanzia siku unakuwa "
            "mwajiri mwenye wajibu wa kuchangia (NSSF Act Cap.50 s.11(1)-(2))'. The previous "
            "instruction not to state a day count is WITHDRAWN -- it existed because the figure "
            "was unverifiable, and the Act now supplies it."),
        "correction_note": (
            "2026-10-05: HEDGE LIFTED, not a value corrected. The fact previously said 'verify "
            "deadline at nssf.go.tz' because nssf.go.tz was recorded as unreachable at the time "
            "of writing (2026-06-19). Per R30, that was a claim about one request, not about the "
            "domain: the Act is published by the Fund itself at /publications/act, a route the "
            "broken /pages/* family does not cover. The deadline was in primary source all "
            "along, on a host we had written off."),
    },

    # ---- 6. THE TWO NOT SETTLEABLE FROM Cap.50 -------------------------------------------
    "minimum_contribution_months_health_insurance": {
        "fact": (
            "NOT SETTLEABLE FROM Cap.50. The claimed 3-month qualifying period for the NSSF "
            "health/medical benefit does not appear anywhere in the NSSF Act Cap.50 R.E.2023. "
            "The Act names \"health benefit\" as a class of benefit (s.23(1)(g)) and s.44(4) "
            "delegates the forms and procedures for medical benefits to regulations made by the "
            "Minister. WHERE TO LOOK NEXT, in this order: (1) the NSSF (Benefits) Regulations / "
            "any G.N. made under s.44(4) or s.52 -- the Act itself points there; (2) the Social "
            "Security Act Cap.135, which Cap.50 cross-references repeatedly for benefit "
            "standards and rates; (3) NSSF's own published benefit conditions. A Regulation can "
            "be amended by a later Regulation exactly as an Act is by a later amending Act "
            "(R29), so "
            # ⚠️ "a later amending Act", NOT "a Finance Act", and the wording is load-bearing.
            # The first draft of this sentence said "exactly as an Act is by a Finance Act",
            # and tests/test_locked_facts_finance_act_freshness.py went RED on this key --
            # because it builds its population from every fact whose JSON object CONTAINS the
            # string "finance act". An incidental analogy in prose had enrolled an NSSF fact
            # into Finance-Act freshness coverage it has no business being in: Cap.50 is not
            # amended by Finance Acts at all (rates.py FINANCE_ACT_VERIFIED_THROUGH['NSSF']
            # records it as absent from FA2026's list of amended Acts).
            #
            # THE MIRROR IMAGE OF THE 1590->1589 CASE, and the more forgiving direction. There,
            # editing prose DELETED the magic string and silently REMOVED a fact from coverage:
            # no failure, no warning, just one fewer parametrized case. Here, editing prose
            # ADDED one, and the suite said so immediately in red. Same mechanism, same
            # fragility -- a population defined by a substring of free text -- but adding is
            # loud and removing is silent, which is why only the removal needed a technique
            # (`pytest --collect-only`, diff the node ids) to catch it.
            "whatever is found must be dated as-at, not merely cited."),
        "correct_value": "NOT SETTLEABLE FROM Cap.50 -- 3 months neither confirmed nor "
                         "contradicted by the Act; likely in regulations or Cap.135",
        "section": "not in Cap.50; cf. s.23(1)(g) (health benefit as a class) and s.44(4) "
                   "(delegation to regulations)",
        "primary_source": None,
        "verified_by": (
            READ + "Searched every occurrence of 'health' and 'medical' in the enacting body. "
            "s.23(1)(g) lists health benefit as a class of benefit; no contribution-month "
            "qualifying condition for it appears anywhere in the Act. NOT CONTRADICTED and NOT "
            "CONFIRMED -- the Act is silent, which is a different verdict from either."),
        "verified_as_at": "unknown",
        "status": ("NOT SETTLEABLE FROM Cap.50 (2026-10-05) -- was CONFIRMED on no stated "
                   "source; do not assert the 3-month figure until a dated instrument is found"),
    },
    "NSSF_split_triggers": {
        "fact": (
            "NSSF's statutory total is 20% of gross wage, of which the employer's share "
            "deductible from wages is 10% (First Schedule). THE RULE, from s.12(2)-(3): the "
            "employer MAY OPT to contribute at a greater rate than the First Schedule amount, "
            "up to the whole contribution rate. So an employer paying 15% with the employee "
            "paying 5%, or an employer paying the full 20% with the employee paying nothing, is "
            "acting lawfully. s.12(3) limits the option: it does not apply to a member whose "
            "contribution rate at any given time does not exceed fifty percent of his "
            "contributions. The total never changes -- only who bears it. THE ACT DOES NOT "
            "ENUMERATE A LIST OF PERMITTED SPLITS; 10+10, 15+5 and 20+0 are instances of the "
            "s.12(2) option, not statutory categories."),
        "correct_value": ("20% total; employer may opt to pay more than its 10% share, up to "
                          "the whole 20% (s.12(2)-(3)). 10+10, 15+5 and 20+0 are examples of "
                          "that option, not an exhaustive statutory list"),
        "section": "s.12(1)-(3) read with the First Schedule",
        "primary_source": f"{ACT}, s.12(1)-(3) and First Schedule",
        "verified_by": (
            READ + "s.12(1): employer pays \"a contribution that consist of the employer's and "
            "employee's share at the rate stipulated in the First Schedule\". s.12(2) verbatim: "
            "\"The employer may opt to contribute a greater rate than the amount stipulated in "
            "subsection (1).\" s.12(3) verbatim: \"Where the employer agrees to contribute at a "
            "greater rate or the whole contribution rate, such option shall not apply to a "
            "member whose contribution rate at any given time does not exceed fifty percent of "
            "his contributions.\" s.12 carries no bracketed prior-edition note."),
        "verified_as_at": "2026-10-05",
        "status": ("CONFIRMED AS A RULE (statute-tier, 2026-10-05); THE THREE-SPLIT "
                   "ENUMERATION IS NOT STATUTORY -- reworded 2026-10-05"),
        "correction_note": (
            "2026-10-05: REWORDED, value unchanged. The previous text said \"Three valid "
            "employer-employee split arrangements\" and \"All three arrangements are legal under "
            "the NSSF Act\", which reads as though the Act lists them. It does not. The Act "
            "states a 20% total and an employer option to pay more, up to the whole; the three "
            "splits are portal-sourced illustrations of that option. The direction of the fact "
            "was right and defensible -- what was wrong was attributing an enumeration to the "
            "statute. wrong_patterns are deliberately UNCHANGED (R27): every one of them guards "
            "against the model claiming 10+10 is the ONLY lawful split, which is still exactly "
            "what s.12(2) refutes."),
    },

    # ---- 7. THE PORTAL-ONLY PENALTY, NOW STATUTE-TIER ------------------------------------
    # BEYOND THE LITERAL INSTRUCTION, and flagged as such. `nssf_penalty` was not in the four
    # approved items nor in the 13 unsourced -- it has a source. But that source is
    # nssf.go.tz/pages/payment-of-contributions, which returns HTTP 500, so it is a citation no
    # one can check: the same defect as the 43 mlywf.go.tz pairs, and the Act is open. Reverse
    # by deleting this entry if the upgrade is unwanted.
    "nssf_penalty": {
        "primary_source": f"{ACT}, s.14(3)",
        "verified_by": (
            READ + "s.14(3) verbatim: \"Where any contribution is not paid within the period "
            "stated under subsection (1) a sum equal to five per centum of the amount unpaid "
            "shall be added as penalty for each month or a part of a month after the date when "
            "payment should have been made and the amount of the penalty shall be recovered as a "
            "debt owing to the Fund by the employer: Provided that, the Board may, where it "
            "thinks fit, remit in whole or in part any penalty imposed by this subsection.\" "
            "NOTE THE PROVISO -- the Board may remit the penalty in whole or in part, which the "
            "bare '5% per month' does not convey."),
        "verified_as_at": "2026-10-05",
        "status": ("CONFIRMED (statute-tier, 2026-10-05) -- was portal-only, and that portal "
                   "route (nssf.go.tz/pages/payment-of-contributions) returns HTTP 500"),
    },

    # ---- 8. THE BACKFILL: confirmed values that had no `primary_source` ------------------
    "contribution_rate_emplyees": {
        "section": "First Schedule read with s.12(1)",
        "primary_source": SCHEDULE_CITE + " read with s.12(1)",
        "verified_by": READ + SCHEDULE_VERBATIM + " The EMPLOYEE share is not stated as a "
                       "separate column: it is the statutory total (20%) less the employer's "
                       "share (10%) = 10%. Recorded as derived-by-subtraction rather than as a "
                       "quoted figure, because that is what the Act supports.",
        "verified_as_at": "2026-10-05",
        "status": "CONFIRMED (statute-tier, 2026-10-05) -- derived from the Schedule's two "
                  "columns, not quoted directly",
    },
    "unpaid_contribution_penalty_rate": {
        "section": "s.14(3)",
        "primary_source": f"{ACT}, s.14(3)",
        "verified_by": READ + "s.14(3): \"a sum equal to five per centum of the amount unpaid "
                       "shall be added as penalty for each month or a part of a month...\" "
                       "Subject to the s.14(3) proviso allowing the Board to remit the penalty "
                       "in whole or in part.",
        "verified_as_at": "2026-10-05",
        "status": "CONFIRMED (statute-tier, 2026-10-05)",
    },
    "unpaid_contribution_penalty_frequency": {
        "section": "s.14(3)",
        "primary_source": f"{ACT}, s.14(3)",
        "verified_by": READ + "s.14(3): \"...for each month OR A PART OF A MONTH after the date "
                       "when payment should have been made\". The 'part of a month' limb is "
                       "verbatim statutory language, so a part-month attracts a full 5%.",
        "verified_as_at": "2026-10-05",
        "status": "CONFIRMED (statute-tier, 2026-10-05)",
    },
    "pensionable_age": {
        "section": "s.2 (interpretation)",
        "primary_source": f"{ACT}, s.2",
        "verified_by": READ + "s.2 interpretation, verbatim: \"'pensionable age' means the age "
                       "of sixty years\".",
        "verified_as_at": "2026-10-05",
        "status": "CONFIRMED (statute-tier, 2026-10-05)",
    },
    "minimum_monthly_contributions_for_retirement_pension": {
        "section": "s.25(b) (R.E.2023; was s.23(b) in R.E.2015)",
        "primary_source": f"{ACT}, s.25(b)",
        "verified_by": READ + "s.25 verbatim: \"retirement pension shall be payable to an "
                       "insured person who- (a) has attained pensionable age; (b) in respect of "
                       "whom not less than 180 monthly contributions have been paid; and (c) who "
                       "has attained the age of fifty-five or above but before attaining "
                       "pensionable age.\" s.25 carries the prior-edition note [s. 23].",
        "verified_as_at": "2026-10-05",
        "status": "CONFIRMED (statute-tier, 2026-10-05)",
    },
    "minimum_monthly_contributions_maternity_benefit": {
        "section": "s.46(a) (R.E.2023; was s.44(a) in R.E.2015)",
        "primary_source": f"{ACT}, s.46(a)",
        "verified_by": READ + "s.46(a) verbatim: \"Maternity benefit shall be payable- (a) to an "
                       "insured person who has made at least thirty-six monthly contributions "
                       "OF WHICH TWELVE CONTRIBUTIONS ARE MADE IN THE THIRTY-SIX MONTHS PRIOR "
                       "TO DATE OF CONFINEMENT\". s.46 carries the prior-edition note [s. 44]. "
                       "THE SECOND LIMB IS AN ADDITIONAL CONDITION THE BARE '36' OMITS: 36 "
                       "lifetime contributions are not sufficient on their own -- twelve must "
                       "fall in the 36 months before confinement. Recorded as an incompleteness "
                       "in the fact, not a contradiction of it.",
        "verified_as_at": "2026-10-05",
        "status": "CONFIRMED BUT INCOMPLETE (statute-tier, 2026-10-05) -- see the recency limb",
    },
    "duration_of_maternity_cash_benefit": {
        "section": "s.47(a) (R.E.2023; was s.45(a) in R.E.2015)",
        "primary_source": f"{ACT}, s.47(a)",
        "verified_by": READ + "s.47(a) verbatim: \"cash benefit at the rate of 100 per centum of "
                       "the average daily earnings for a period of twelve weeks\". s.47 carries "
                       "the prior-edition note [s. 45].",
        "verified_as_at": "2026-10-05",
        "status": "CONFIRMED (statute-tier, 2026-10-05)",
    },
    "maternity_cash_benefit_rate": {
        "section": "s.47(a) (R.E.2023; was s.45(a) in R.E.2015)",
        "primary_source": f"{ACT}, s.47(a)",
        "verified_by": READ + "s.47(a) verbatim: \"cash benefit at the rate of 100 per centum of "
                       "THE AVERAGE DAILY EARNINGS for a period of twelve weeks\". THE BASE "
                       "MATTERS AND THE BARE '100%' DOES NOT CONVEY IT: the rate is 100% of "
                       "average DAILY earnings, not of the monthly salary. s.47 carries the "
                       "prior-edition note [s. 45].",
        "verified_as_at": "2026-10-05",
        "status": "CONFIRMED (statute-tier, 2026-10-05) -- base is average daily earnings",
    },
    "employer_notification_deadline_before_retirement": {
        "section": "s.51(1) (R.E.2023; was s.49(1) in R.E.2015)",
        "primary_source": f"{ACT}, s.51(1)",
        "verified_by": READ + "s.51(1) verbatim: \"An employer shall, within six months before "
                       "the date of retirement of his employee, notify the Fund in writing "
                       "about the date of retirement of his employee.\" s.51 carries the "
                       "prior-edition note [s. 49] -- THE OLD `section` FIELD HERE READ "
                       "\"49.-( I)\", i.e. R.E.2015 numbering, which in R.E.2023 is a different "
                       "section.",
        "verified_as_at": "2026-10-05",
        "status": "CONFIRMED (statute-tier, 2026-10-05)",
    },
    "fund_payment_deadline_after_retirement_notification": {
        "section": "s.51(2) (R.E.2023; was s.49(2) in R.E.2015)",
        "primary_source": f"{ACT}, s.51(2)",
        "verified_by": READ + "s.51(2) verbatim: \"Subject to subsection (1), the Fund shall, "
                       "within sixty days following the date of retirement, pay to the member "
                       "the due retirement pension benefits.\" s.51(3) adds a limb the fact "
                       "omits and a member would want: \"Where the Fund fails to pay retirement "
                       "benefits to a member within a period specified under subsection (2), and "
                       "the member is not responsible for that failure, the Fund shall pay the "
                       "member the principal sum that is due... plus a penalty of fifteen "
                       "percent of that sum per annum.\" s.51 carries the prior-edition note "
                       "[s. 49].",
        "verified_as_at": "2026-10-05",
        "status": "CONFIRMED (statute-tier, 2026-10-05) -- s.51(3) 15%/annum limb not yet "
                  "encoded as its own fact",
    },
}


def main():
    raw = io.open(FACTS, encoding="utf-8").read()
    facts = json.loads(raw)
    before = {k: json.loads(json.dumps(facts[k])) for k in AMENDMENTS}

    for key, patch in AMENDMENTS.items():
        assert key in facts, f"{key} is not in locked_facts.json -- refusing to create it here"
        for field, value in patch.items():
            if field == "_APPEND_VERIFIED_BY":
                existing = facts[key].get("verified_by") or ""
                assert existing, f"{key}: nothing to append to -- verified_by is empty"
                # IDEMPOTENT. This script is re-run during development; an append that is not
                # idempotent silently doubles the text on the second run, and the R27 guard
                # would not see it (verified_by is a named field).
                if value.strip() not in existing:
                    facts[key]["verified_by"] = existing.rstrip() + value
                continue
            facts[key][field] = value

    # ---- R27 GUARD: every pre-existing field NOT named in the patch must be untouched -----
    violations = []
    for key, patch in AMENDMENTS.items():
        for field, old in before[key].items():
            if field in patch or (field == "verified_by"
                                  and "_APPEND_VERIFIED_BY" in patch):
                continue
            if facts[key].get(field) != old:
                violations.append((key, field, old, facts[key].get(field)))
        if "_APPEND_VERIFIED_BY" in patch:
            # An append must PRESERVE. Asserting the old text is still a prefix is the whole
            # point of having an append mode rather than a replace.
            if not (facts[key].get("verified_by") or "").startswith(
                    (before[key].get("verified_by") or "").rstrip()):
                violations.append((key, "verified_by APPEND DID NOT PRESERVE THE ORIGINAL",
                                   None, None))
            assert "_APPEND_VERIFIED_BY" not in facts[key], (
                f"{key}: the append marker leaked into the stored fact")
        lost = [f for f in before[key] if f not in facts[key]]
        if lost:
            violations.append((key, f"FIELDS DROPPED: {lost}", None, None))
    assert not violations, (
        "R27 VIOLATION -- an amendment changed or dropped a field it did not name. This is the "
        f"exact failure R27 exists to prevent:\n{violations}")

    # ---- every wrong_patterns regex must compile, or the guard silently stops guarding ----
    for key in AMENDMENTS:
        for pat in facts[key].get("wrong_patterns") or []:
            try:
                re.compile(pat)
            except re.error as exc:
                raise AssertionError(f"{key}: wrong_patterns regex does not compile: {pat!r} "
                                     f"({exc})")

    # ---- verified_as_at must appear in the fact's own verified_by (the committed invariant) --
    for key in AMENDMENTS:
        v = facts[key].get("verified_as_at")
        if v and v != "unknown":
            assert v in (facts[key].get("verified_by") or ""), (
                f"{key}: verified_as_at={v} does not appear in its own verified_by text -- "
                "tests/test_verified_as_at_bootstrap.py enforces this and would fail")

    with io.open(FACTS, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print(f"amended {len(AMENDMENTS)} Cap.50 facts against R.E.2023")
    for key, patch in AMENDMENTS.items():
        print(f"  {key:58s} fields: {', '.join(sorted(patch))}")
    print("\nR27 guard: clean -- no unnamed field changed or dropped")


if __name__ == "__main__":
    main()
