# -*- coding: utf-8 -*-
r"""RE-DERIVE THE RETRAIN PRECONDITION FROM SCRATCH, AGAINST THE FILES THAT ACTUALLY TRAIN.

⛔ WHY THE 2026-09-01 "MET" DECLARATION CANNOT BE CARRIED FORWARD.

It was earned honestly and it is no longer true, for two independent reasons that have to be named
separately because they need different fixes:

  1. STAGE. `scripts/verify_sft_defect_free.py` swept `datasets/tier1a/sft/*.jsonl` — correctly,
     that IS what trains. But every quarantine from v6 onward targeted the AUTHORED corpus
     (`cleaned_pairs/`, `sft_shaped_pairs/`) and never re-ran the export. Five removed rows were
     still in `train_sft.jsonl` on 2026-10-06, four of them from the day before (R36). The
     declaration was true of what was swept and false of what trains, and nothing in between said
     so because the export is not a check, it is a build step nobody re-ran.
  2. NOTATION. The five swept pattern sets (v1–v5) are keyed on FIGURES, because they were derived
     from each fact's own `wrong_patterns`, which hold digits: `(11|14),?000,?000`. Swahili writes
     money both ways in the same file. A sweep for `milioni 11` found 3 rows; D-FIDELITY-7 found 7;
     a sweep keyed on the CLAIM across both notations found 14 — six in digits, six in words, two
     in both. **So a sweep built from a fact's own patterns is blind to the words by construction**,
     and every sweep in this arc inherited that blindness.

So this file does not re-check the previous verification. It rebuilds the export from the current
corpus and sweeps the result on the CLAIM, in both notations, polarity-aware.

⚠️ POLARITY IS LOAD-BEARING AND IT HAS ALREADY COST CORRECT DATA. The 2026-09-01 VAT-withholding
quarantine swept for `tarehe 20` and removed a training row that REJECTS the 20th — correct data,
deleted by a presence check, a month before mention-vs-assertion was written down. A superseded
value named in order to contradict it is a MENTION. Every alternative here is word-bounded: a bare
`si\s` matches inside the ordinary Swahili `kiasi `, and a loose mention rule does not add noise,
it DELETES FINDINGS.

⚠️ AND THE DEFECT CLASSES ARE NOT "WHAT THE QUARANTINE FILES CONTAIN". A quarantine record lists
the rows that were REMOVED; it cannot tell you whether the claim came back through a later batch,
an edit-in-place, or a regenerated export. The population here is the CLAIM, swept over the output
files, so a claim that re-enters by any route is caught by the same pass.

Usage:
  python eval/controls/rederive_retrain_precondition_2026_10_07.py              # sweep only
  python eval/controls/rederive_retrain_precondition_2026_10_07.py --rebuild    # + regenerate sft/
Artifact: eval/results/retrain_precondition_rederived_2026_10_07.json
Exit 1 if any ASSERTS finding in the exported training files.
"""
import argparse
import collections
import glob
import hashlib
import io
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(REPO)

ARTIFACT = "eval/results/retrain_precondition_rederived_2026_10_07.json"

# THE FILES THAT ACTUALLY TRAIN. kaggle/train_ddp.py:310 hardcodes
# data_files={"train": "train_sft.jsonl", "validation": "val_sft.jsonl"} -- nothing else is read.
TRAINING_FILES = ["datasets/tier1a/sft/train_sft.jsonl", "datasets/tier1a/sft/val_sft.jsonl"]
# The authored stages the export is built FROM, swept too so a defect's STAGE is visible: a hit in
# the export with no hit upstream means a stale export; a hit in both means a live authored defect.
UPSTREAM_DIRS = ["datasets/tier1a/cleaned_pairs", "datasets/tier1a/sft_shaped_pairs"]

BODY_KEYS = ("output", "answer_sw", "response")
QKEYS = ("instruction", "question_sw", "question")

# ── MENTION vs ASSERTION ────────────────────────────────────────────────────────────────
# Word-bounded on every alternative. `si` unbounded matches inside `kiasi `, which reclassified a
# genuine false positive as a mere mention and silently shrank the adjudicated set -- the opposite
# of how a filter is expected to fail, and the dangerous direction.
#
# ⛔ `\bsahihi\s+ni\b` WAS IN BOTH RULES AND IS GONE FROM BOTH. Removing it from the correction
# marker alone did nothing: the backward rule still matched "Kizingiti SAHIHI NI TZS milioni 11"
# and demoted the fabrication, because the optional `tzs\s*` tail let the cue sit right in front
# of the figure. The phrase asserts that what FOLLOWS is correct, so as a negation cue it is
# inverted in BOTH directions -- and a cue that appears twice has to be removed twice. The
# re-run after the first removal still reported the row as a wrongly-deleted one, which is the
# only reason this was found.
_NEGATION = re.compile(
    r"(?:\bsi\b|\bsio\b|\bsiyo\b|\bhakuna\b|\bhaina\b|\bhakina\b|\bhamna\b|\bhapana\b|"
    r"\bwala\b|\bbadala\s+ya\b|\bnot\b|\bno\b|\bnever\b|\binstead\b)"
    r"[\s:,—–()\-]*(?:tzs\s*|usd\s*|asilimia\s*|tarehe\s*)?$", re.IGNORECASE)
_NEGATION_CHARS = 30
# A correction marker demotes a value to a MENTION even when it sits AFTER it: "Kizingiti sahihi
# ni X -- si Y" puts the negation out of a backward window's reach. So it is checked BOTH ways.
#
# ⛔⛔ TWO FAILURES OF THIS RULE, BOTH IN THE DIRECTION THAT DELETES FINDINGS — which is the
# direction a filter is NOT expected to fail, and therefore the one nobody re-checks. Both were
# found by reading the over-removal arm's output rather than by reading this code.
#
#  1. `\bmakosa\b` BARE. `makosa` is ordinary Swahili for "OFFENCES", not only "errors". The
#     sentence "Faini ya shilingi elfu mia moja (TZS 100,000) hutolewa kwa MAKOSA yanayohusu utii
#     wa sheria" ASSERTS the superseded TZS 100,000 NSSF fine ceiling, and the bare marker demoted
#     it — so the sweep reported a row stating a 100x understatement as correct data WRONGLY
#     REMOVED. Narrowed to the predicative `ni makosa` / `ni kosa`.
#  2. SENTENCE-WIDE SCOPE. One sentence can reject one value and assert another:
#     "Hapana, SI SAHIHI. EFD inahitajika kwa biashara zenye mauzo ya TZS MILIONI 11 au zaidi" —
#     correctly refuting a 40M claim while asserting the fabricated 11M. A sentence-wide marker
#     demoted BOTH figures, and the 11M assertion is the worst row in the entire EFD quarantine.
#     The marker must now sit WITHIN _MARKER_CHARS of the value it excuses.
#
# Both defects had the same signature: the finding count went DOWN, and a shorter list of findings
# is indistinguishable from progress.
_CORRECTION_MARKER = re.compile(
    # ⛔ `\bsahihi\s+ni\b` WAS HERE AND IS DELIBERATELY GONE — THIRD FALSE DEMOTION, same
    # direction as the other two. "Kizingiti SAHIHI NI TZS milioni 11 — si 40M" asserts the
    # fabrication AS the correct threshold; it is the worst single row in the EFD quarantine, and
    # `sahihi ni` sitting immediately in front of the figure excused it. The phrase marks what
    # FOLLOWS as correct, so as a demotion cue it is exactly backwards. Nothing is lost by
    # removing it: in "sahihi ni <right> — si <wrong>" the wrong value is already demoted by the
    # backward `si ` rule, which is where the polarity actually lives.
    r"\bsi\s+(?:tzs|usd|asilimia|tarehe|kweli|sahihi)\b|"
    r"\bhakuna\s+kizingiti\b|\bimefutwa\b|\bya\s+zamani\b|\bilikuwa\b|\bwas\b|\bformerly\b|"
    # ── ADDED 2026-10-07, each one from a measured false positive in the live corpus ────
    r"\bni\s+makosa\b|\bni\s+kosa\b|"                        # "...personal relief ni makosa"
    # "Kosa la 9% limetoka..." AND "Kosa HILI la asilimia 9 linaonekana..." -- the demonstrative
    # is optional and its absence was a real miss, surfaced by tightening the window above.
    r"\bkosa\s+(?:hili\s+|hilo\s+)?la\s+(?:\d|asilimia)|"
    r"\bbadala\s+ya\b|"                                      # "9% badala ya 8%"
    r"\bhaikubadilish\w*|\bhakibadilish\w*",                 # "haikubadilishwa hadi asilimia 9"
    re.IGNORECASE)
# How far a correction marker may sit from the value it excuses, in either direction. Wide enough
# for "...TZS 26,000 personal relief ni makosa", narrow enough that a leading "Hapana, si sahihi."
# cannot excuse a fabricated figure 60 characters later in the same sentence.
_MARKER_CHARS = 40


def _n(pat):
    """Digit figure with a boundary that excludes only a CONTINUATION of the number.

    ⚠️ NOT `(?![\d,.])`. That form also blocks a sentence-final period, so "SI TZS 11,000,000."
    came back CLEAN from the first EFD sweep -- a too-tight boundary DELETES findings.
    """
    return rf"(?<![\d,.]){pat}(?![\d]|,\d)"


# ── THE DEFECT CLASSES, KEYED ON THE CLAIM ──────────────────────────────────────────────
#
# ⛔ THE FIRST DRAFT OF THIS TABLE RAISED SEVEN CLASSES AND FIVE WERE BAD SPECIMENS. It is kept
# as a worked example of R26's second half, because reported unchecked it would have been WORSE
# THAN NO SWEEP: a false defect gets ACTED ON, and the "fix" lands in correct data. The 2026-09-01
# VAT-withholding quarantine is what that looks like after the fact — it removed a correct row for
# rejecting the 20th.
#
#   `faini|adhabu` as a row subject for the NSSF fine     -> matched every OSHA per-day fine
#   `asilimia 30` anywhere near `dse`                     -> matched the 30% CORPORATE RATE, which
#                                                            is correct, in a correct answer
#   `personal relief` as the wrong CLAIM                  -> matched rows SAYING THERE IS NONE
#   the 9% band and a two-option DSE question             -> matched the QUESTION of adversarial
#                                                            pairs, where a wrong premise is the
#                                                            entire design
#   `asilimia 1` near `stempu`                            -> 1% IS lawful for several instruments
#
# Three structural rules follow, and they are what the table now encodes:
#
#   1. SWEEP THE ANSWER BODY, NEVER THE QUESTION. An adversarial pair states the defect in its
#      question on purpose. Sweeping question+body together converts the corpus's best rows into
#      findings. The question is used only to establish what a row is ABOUT.
#   2. THE CLAIM AND ITS CUE MUST SHARE A SENTENCE. A figure elsewhere in a long answer is not
#      this claim. `claim_cue` is the thing the wrong value is being asserted OF.
#   3. A TERM IS NOT A CLAIM. `punguzo la kibinafsi` is vocabulary; `punguzo la kibinafsi TZS
#      26,000` is the defect. Match the value, not the topic.
#
# And a fourth, recorded rather than worked around: some defect classes are NOT FIGURE-TESTABLE
# AT ALL (NOT_FIGURE_TESTABLE below). The stamp-duty defect was "stated as a FLAT 1%" — a claim
# about SCOPE, where 1% is itself a lawful rate. That is R19's Guard B line: no figure test can
# separate a wrong scope from a right rate, and pretending otherwise produces 14 findings against
# correct rows.
CLASSES = [
    {"id": "paye_phantom_personal_relief",
     "subject": r"\bpaye\b|kodi\s+ya\s+mshahara",
     "claim_cue": r"punguzo\s+la\s+kibinafsi|personal\s+relief|msamaha\s+wa\s+kibinafsi",
     "wrong": [_n(r"26[,.]?000"), r"elfu\s+ishirini\s+na\s+sita"],
     "correct": "Tanzania has NO personal relief; the 0% first band (TZS 270,000/mo) IS the "
                "tax-free threshold (CLAUDE.md s.11). Only a FIGURE attached to the relief is "
                "testable -- a row that merely uses the term is usually denying it exists."},
    {"id": "paye_band2_at_9pct",
     "subject": r"\bpaye\b|kodi\s+ya\s+mshahara",
     "claim_cue": r"bendi|kanda|kiwango\s+cha\s+pili|band\s*2|pili",
     "wrong": [r"asilimia\s+9\b", r"\b9\s*%", r"asilimia\s+tisa\b"],
     "correct": "Band 2 (270,001-520,000) is 8% on the excess, not 9%."},
    {"id": "nssf_retirement_mining_fabrication",
     "subject": r"\bnssf\b|kustaafu|retirement",
     "claim_cue": r"kustaafu|retirement|umri",
     "wrong": [r"\bmadini\b", r"\bmining\b", r"\bmchimba\w*"],
     "correct": "No mining-specific retirement age exists in the NSSF Act."},
    {"id": "efd_threshold_fabrication",
     "subject": r"\befd\b|mashine\s+ya\s+risiti|fiscal\s+receipt",
     "claim_cue": r"kizingiti|threshold|anza\s+kutumia|lazima|inatakiwa|mauzo",
     "wrong": [_n(r"11[,.]?000[,.]?000"), _n(r"14[,.]?000[,.]?000"),
               r"milioni\s+11\b", r"milioni\s+14\b",
               r"milioni\s+kumi\s+na\s+moja", r"milioni\s+kumi\s+na\s+nne",
               r"\b11\s*M\b", r"\b14\s*M\b"],
     "correct": "TAA Cap.438 R.E.2023 s.44(1): EFD is the DEFAULT for every supplier. No "
                "turnover figure appears anywhere in the Act."},
    {"id": "gn487a_visa_revocation_softened",
     "subject": r"gn\s*487|raia\s+wa\s+kigeni|non-?citizen",
     "claim_cue": r"visa|kibali\s+cha\s+ukaazi|kufut\w+|revok\w+",
     "wrong": [r"\binawezekana\b", r"\byawezekana\b", r"\bpossibl\w+",
               r"\bmay\s+be\s+revoked\b"],
     "correct": "Visa revocation is MANDATORY on conviction, not possible."},
    {"id": "paye_p9_31_march",
     "subject": r"\bp\s*9\b|\bp9a?\b|fomu\s+ya\s+p",
     "claim_cue": r"\bp\s*9\b|\bp9\b|inawasilishwa|inatakiwa|kufikia|ifikapo",
     "wrong": [r"31\s+machi", r"31\s+march", r"tarehe\s+31\s+machi"],
     "correct": "ITA s.85(3)(b): 30 January. 'Form P9' is Kenyan KRA terminology; the TZ "
                "instrument is the s.85(3)(b) withholding certificate."},
    {"id": "vat_threshold_dated_2024",
     "subject": r"\bvat\b",
     "claim_cue": r"kizingiti|threshold|200[,.]?000[,.]?000",
     "wrong": [r"julai\s+2024", r"july\s+2024", r"1\s+julai\s+2024"],
     "correct": "GN 448Y/2023, effective 1 July 2023."},
    {"id": "patent_flat_20_years",
     "subject": r"\bpatent\w*|hataza",
     "claim_cue": r"muda|kipindi|hudumu|term|inadumu|years|miaka",
     "wrong": [r"miaka\s+20\b", r"miaka\s+ishirini\b", r"\b20\s+years\b"],
     "correct": "10-year base plus two discretionary 5-year extensions."},
    {"id": "foreign_company_part_xiii_reversed",
     "subject": r"kampuni\s+ya\s+kigeni|foreign\s+compan|cap\.?\s*212",
     "claim_cue": r"part|sehemu|kifungu|\bss?\.",
     "wrong": [r"part\s*xiii\b", r"sehemu\s+ya\s+xiii\b", r"ss?\.?\s*320\s*[-–]\s*328"],
     "correct": "Cap.212 R.E.2023 PART XII, ss.437-447 (s.437(1)). The 2026-08-31 "
                "'correction' to Part XIII was itself the error and was reversed 2026-10-05."},
    {"id": "osha_course_fee_250k",
     "subject": r"\bosha\b",
     "claim_cue": r"kozi|mafunzo|course|ada\s+ya\s+mafunzo",
     "wrong": [_n(r"250[,.]?000"), r"laki\s+mbili\s+na\s+nusu"],
     # ⚠️ ECHOING THE USER'S OWN FIGURE IS NOT ASSERTING A FEE. train_sft:3150 answers "the OSH
     # training you paid 250,000 TZS for..." -- the number came from the question. Flagging it
     # would have sent someone to edit a row that states no fee at all.
     # ⚠️ SPELLED OUT, NOT CONSTRUCTED. My first attempt built this from optional morphemes
     # (`u(?:li)?(?:ya)?lipi?a`) and generated "uliyalipia" -- the live row says "uliyolipia",
     # with an O. The pattern matched nothing, the specimen came back ASSERTS, and the demotion
     # rule was decoration. A Swahili relative-verb form is not reliably assembled from optional
     # groups; list the forms and let a missing one fail visibly.
     "lawful_attachment": r"\b(?:uliyolipia|uliyolipa|ulilipia|ulilipa|nilizolipia|"
                          r"niliyolipia|nililipia|nililipa|alilipia|walilipia)\b",
     "correct": "Every sampled OSHA course is TZS 300,000."},
    {"id": "dse_stale_30pct_float",
     "subject": r"\bdse\b|soko\s+la\s+hisa\s+la\s+dar",
     # THE FLOAT, not the rate. 30% IS the standard corporate rate and appears correctly in
     # DSE answers -- the first draft flagged one of those, in a fully correct reply.
     "claim_cue": r"public\s+float|hisa\s+za\s+umma|kiasi\s+cha\s+hisa|float|"
                  r"kuorodhesha.{0,30}umma",
     "wrong": [r"asilimia\s+30\b", r"\b30\s*%", r"asilimia\s+thelathini\b"],
     "correct": "FA2025 s.60(d)(i) lowered the public-float threshold to 25%. ⚠️ The REDUCED "
                "CORPORATE RATE is also 25% and the STANDARD rate is 30% -- coincident numbers, "
                "different provisions, which is the whole reason this class is hard to sweep."},
    {"id": "presumptive_stale_ceiling_and_rate",
     "subject": r"makadirio|presumptive",
     "claim_cue": r"kikomo|ceiling|juu|kizingiti|kiwango|asilimia|mauzo",
     "wrong": [_n(r"100[,.]?000[,.]?000"), r"milioni\s+mia\s+moja\b",
               r"asilimia\s+3[.,]5\b", r"\b3[.,]5\s*%"],
     "correct": "FA2026 s.27(a): ceiling TZS 200,000,000, top band 4.0% of turnover."},
    {"id": "memorandum_articles_fee_22k",
     "subject": r"memorandum|katiba\s+ya\s+kampuni|articles\s+of\s+association",
     "claim_cue": r"ada|fee|kuwasilisha|filing",
     "wrong": [_n(r"22[,.]?000"), r"elfu\s+ishirini\s+na\s+mbili\b"],
     "correct": "Absent from the 2026-10-06 BRELA schedule. Absence is not a value "
                "(_unresolved_items.brela_vanished_fee_line_items)."},
    {"id": "nssf_fine_ceiling_100k",
     # NSSF ONLY. `faini|adhabu` as a row subject matched every OSHA per-day fine in the corpus,
     # and the OSHA TZS 100,000/day figure is CORRECT.
     "subject": r"\bnssf\b|sheria\s+ya\s+nssf|cap\.?\s*50\b",
     "claim_cue": r"faini|adhabu|fine|penalty",
     "wrong": [_n(r"100[,.]?000"), r"laki\s+moja\b", r"one\s+hundred\s+thousand"],
     # ⚠️ A WORKED EXAMPLE'S CONTRIBUTION AMOUNT IS NOT THE ACT'S FINE CEILING. train_sft:2977
     # reads "NSSF TZS 100,000 haijalipwa kwa miezi 3 -> faini = 5% x 100,000 x 3 = TZS 15,000"
     # -- the 100,000 is the UNPAID CONTRIBUTION, the row is correct, and it even states the
     # one-month deadline correctly. The cue `faini` is in the sentence; the figure attaches to
     # something else, which no quantity pattern can see.
     "lawful_attachment": r"mchango|contribution|haijalipwa|kisicholipwa|×|\bx\s*\d|\d\s*×",
     "correct": "Cap.50 R.E.2023 s.76(1): ten million shillings. TZS 100,000 is R.E.2015 "
                "s.72(1) -- a 100x understatement."},
    {"id": "rent_wht_nonresident_15pct",
     "subject": r"\bpango\b|kodi\s+ya\s+pango|\brent\b",
     "claim_cue": r"zuio|withhold|kuzuia|wakala",
     "wrong": [r"asilimia\s+15\b", r"\b15\s*%", r"asilimia\s+kumi\s+na\s+tano\b"],
     "correct": "10% on rent for BOTH parties -- there is no residency split."},
    {"id": "vat_withholding_deadline_20th",
     # THE CERTIFICATE, not the return. The return IS due on the 20th and the corpus says so
     # correctly in many rows; the defect was attaching the 20th to the CERTIFICATE.
     "subject": r"\bvat\b",
     "claim_cue": r"cheti|certificate",
     "wrong": [r"tarehe\s+20\b", r"tarehe\s+ishirini\b", r"\bthe\s+20th\b"],
     # ⚠️ THE 20TH IS CORRECT FOR THE RETURN AND FOR REMITTANCE. Five rows mention a certificate
     # and the 20th in one sentence and every one of them is right: "omba kabla ya kuwasilisha
     # return ifikapo tarehe 20", "kupeleka VAT iliyokatwa TRA ifikapo tarehe 20". The defect was
     # attaching the 20th to the CERTIFICATE'S ISSUANCE, which is a syntactic relation no regex
     # resolves -- so the honest rule is to demote whenever a lawful holder of the deadline is
     # named in the window, and accept that a genuine defect co-naming a return is demoted too.
     # Recorded as a known limit rather than papered over.
     "lawful_attachment": r"\breturn\b|kupeleka|kuwasilisha|\bremit\w*|kulipa\s+vat|kudai",
     "correct": "The certificate is issued by the day VAT becomes payable. The 20th is the "
                "RETURN filing deadline -- a different obligation."},
]

# ⛔ RECORDED, NOT SWEPT. Listing these is the point: a census that silently omits what it cannot
# test reports a cleaner result than it earned.
NOT_FIGURE_TESTABLE = [
    {"id": "stamp_duty_flat_1pct",
     "why": "The defect is SCOPE, not value: 1% is a lawful stamp-duty rate (Cap.189 Art.22(b) "
            "is tiered 0.5%/1%), and the defect was asserting it as FLAT. A figure test flagged "
            "14 rows, including correct share-transfer and land-transfer answers. R19's Guard B "
            "line -- find the constant underneath the claim, or do not build the check."},
    {"id": "wcf_disease_reporting_flat_7_days",
     "why": "The true rule is a CHAIN (14 days to the employer, then 7 to WCF) and the defect "
            "was collapsing it to a flat 7. '7 working days' is correct for the accident-"
            "reporting obligation, so the figure appears lawfully in adjacent rows. Needs a "
            "structure test, not a value test."},
    {"id": "p45_p9_conflation",
     "why": "A TERMINOLOGY defect with no figure. Caught by the p9 class above only where a "
            "date is attached; a row that uses 'P9' as a label with no deadline is not "
            "distinguishable by any pattern from one that explains the term is Kenyan."},
    {"id": "nssf_or_tz_dead_domain",
     "why": "Fixed by in-place REWRITE, not quarantine (R25 containment) -- 1,374 occurrences. "
            "Nothing to sweep for; the string is gone by construction. The upstream defect "
            "(the model emitting it) is tracked separately."},
]



# ── NEGATIVE SPECIMENS SOURCED FROM THE LIVE CORPUS, READ FROM DISK ─────────────────────
# Every one is a row an earlier draft of this sweep FLAGGED and that is in fact CORRECT.
#
# ⛔ KEYED ON CONTENT, NOT ON file:line — AND THE FIRST VERSION WAS KEYED ON file:line, WHICH
# BROKE WITHIN THE HOUR. These were pinned into datasets/tier1a/sft/*.jsonl, a file
# generate_sft.py REGENERATES AND RESHUFFLES (seeded, but the seed is over the whole set, so one
# added pair moves everything). Running --rebuild moved every line and all eleven pins failed at
# once. They failed LOUDLY, because each carried a required substring — which is the stale-pin
# lesson working rather than a new instance of it — but the right fix is not to re-pin the
# numbers: a line number in a generated file is not an identity. The CONTENT is.
#
# So each specimen is located by a substring unique within the AUTHORED corpus (cleaned_pairs/,
# sft_shaped_pairs/), which is hand-edited and stable, and the lookup asserts it resolves.
#
# `expect` distinguishes the two non-defect outcomes, because they are different claims:
#   None                      -- the class never considered the row (subject/cue did not match)
#   MENTIONS_UNDER_NEGATION   -- the row WAS considered and a demotion rule fired
# Pinning which one means a removed demotion rule fails here rather than reappearing as a finding.
CORPUS_NEGATIVES = [
    {"must_contain": "kila siku kosa linaendelea",
     "class": "nssf_fine_ceiling_100k", "expect": None,
     "why": "the OSHA per-day fine IS TZS 100,000. A row subject of `faini|adhabu` matched every "
            "fine in the corpus; it must be NSSF only"},
    {"must_contain": "haijaorodhesha DSE",
     "class": "dse_stale_30pct_float", "expect": None,
     "why": "a FULLY CORRECT answer. 30% is the standard corporate rate; 25% is both the reduced "
            "rate and the float threshold -- coincident numbers, and the first draft read the "
            "correct rate as a stale float"},
    {"must_contain": "NDIYO punguzo la ufanisi",
     "class": "paye_phantom_personal_relief", "expect": None,
     "why": "the row SAYS THERE IS NONE. A term is not a claim -- only a FIGURE attached to the "
            "relief is testable"},
    {"must_contain": "kosa hili ni la kawaida",
     "class": "paye_band2_at_9pct", "expect": "MENTIONS_UNDER_NEGATION",
     "why": "an adversarial pair: the defect is in the QUESTION by design and the answer refutes "
            "it twice ('asilimia 8, si 9'). ⚠️ I first labelled this `None` from a paraphrase I "
            "had retyped; the real row names 9 under negation, so the correct expectation is a "
            "FIRED DEMOTION -- a stronger pin, because it fails if the negation rule is removed "
            "rather than passing by the class happening not to match"},
    {"must_contain": "kodi ya stempu",
     "class": "stamp_duty_flat_1pct", "expect": None,
     "why": "CORRECT -- 1% is lawful for a share transfer. The class is in NOT_FIGURE_TESTABLE "
            "and must never be swept; this fails loudly if someone adds it back"},
    {"must_contain": "5% × 100,000 × 3",
     "class": "nssf_fine_ceiling_100k", "expect": "MENTIONS_UNDER_NEGATION",
     "why": "the 100,000 is the UNPAID CONTRIBUTION in a worked example, not the Act's fine "
            "ceiling. The row is correct and even states the one-month deadline correctly"},
    {"must_contain": "uliyolipia 250,000 TZS",
     "class": "osha_course_fee_250k", "expect": "MENTIONS_UNDER_NEGATION",
     "why": "the figure came from the QUESTION and is echoed back; the answer asserts no fee"},
    {"must_contain": "9% badala ya 8%",
     "class": "paye_band2_at_9pct", "expect": "MENTIONS_UNDER_NEGATION",
     "why": "CORRECT. 'badala ya' is a CONTRAST marker and a backward negation window reaches "
            "nothing in front of it"},
    {"must_contain": "Kosa la 9% limetoka",
     "class": "paye_band2_at_9pct", "expect": "MENTIONS_UNDER_NEGATION",
     "why": "CORRECT. The wrong value is the SUBJECT of a noun phrase naming it as an error"},
    {"must_contain": "personal relief ni makosa",
     "class": "paye_phantom_personal_relief", "expect": "MENTIONS_UNDER_NEGATION",
     "why": "CORRECT. The correction is stated AFTER the figure ('ni makosa'), which is where a "
            "backward window cannot look"},
    {"must_contain": "haikubadilishwa hadi asilimia 9",
     "class": "paye_band2_at_9pct", "expect": "MENTIONS_UNDER_NEGATION",
     "why": "CORRECT -- it DENIES the 9% change. A negative verb form, which the threshold guard "
            "deliberately does NOT treat as a negation; here it is one, and the difference is "
            "whether the verb negates the CLAIM or the user's position"},
]


def _corpus_negatives():
    """Locate each negative specimen BY CONTENT in the authored corpus and load it verbatim."""
    paths = sorted(p for d in UPSTREAM_DIRS
                   for p in glob.glob(os.path.join(REPO, *d.split("/"), "*.jsonl")))
    assert paths, "no authored corpus files found -- cannot load the negative specimens"
    rows = []
    for path in paths:
        rel = os.path.relpath(path, REPO).replace(os.sep, "/")
        for n, obj in _rows(path):
            q, body = _text(obj)
            if body:
                rows.append((f"{rel}:{n}", q, body))

    out = []
    for spec in CORPUS_NEGATIVES:
        needle = spec["must_contain"]
        found = [(at, q, b) for at, q, b in rows if needle in b or needle in q]
        assert found, (
            f"negative specimen {needle!r} is no longer anywhere in the authored corpus. It is a "
            f"row an earlier draft of this sweep wrongly FLAGGED; if it has been edited or "
            f"removed, re-read it and re-adjudicate rather than deleting the specimen -- a "
            f"removed false-positive specimen is how an over-broad rule comes back.")
        at, q, body = found[0]
        out.append((q, body, spec["class"], spec["expect"],
                    f"{at} ({len(found)} match) -- {spec['why']}"))
    return out


def _rows(path):
    with io.open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield n, json.loads(line)
            except Exception:
                continue


def _text(obj):
    if isinstance(obj.get("row"), dict):
        obj = obj["row"]
    q = next((obj[k] for k in QKEYS if isinstance(obj.get(k), str)), "")
    b = next((obj[k] for k in BODY_KEYS if isinstance(obj.get(k), str)), "")
    return q, b


def _sentences(text):
    return [s for s in re.split(r"(?<=[.!?;])\s+|\n+", text or "") if s.strip()]


def classify(q, body):
    """Return [(class_id, verdict, hits)] for every class the row's ANSWER asserts.

    ⛔ THE QUESTION IS CONTEXT ONLY. It establishes what the row is about and is never searched
    for the wrong claim. An adversarial pair states the defect in its question BY DESIGN -- that
    is the row doing its job -- and sweeping question+body together turns the corpus's most
    valuable rows into findings. Four of the first draft's seven classes were this error.

    The claim and its cue must share a SENTENCE: a figure elsewhere in a long answer is not the
    claim under test.
    """
    out = []
    about = f"{q}\n{body}"
    for cls in CLASSES:
        if not re.search(cls["subject"], about, re.IGNORECASE):
            continue
        hits, mentions = [], []
        sents = _sentences(body)
        for i, sent in enumerate(sents):
            # ⚠️ A TWO-SENTENCE WINDOW, NOT ONE, and the reason is a blind spot the planted
            # specimens exposed: "Hakuna kizingiti cha EFD. SI TZS 11,000,000." splits so that
            # the FIGURE sentence carries no cue at all, and a one-sentence rule skips it
            # entirely. The outcome happened to be right here (not flagged) for the wrong reason
            # -- an ASSERTION in a cue-less continuation sentence would have been missed the same
            # way. The cue may be established by the preceding sentence; the VALUE must still be
            # in this one.
            window = (sents[i - 1] + " " + sent) if i else sent
            if not re.search(cls["claim_cue"], window, re.IGNORECASE):
                continue
            lawful = cls.get("lawful_attachment")
            for alt in cls["wrong"]:
                for m in re.finditer(alt, sent, re.IGNORECASE):
                    before = sent[max(0, m.start() - _NEGATION_CHARS):m.start()]
                    near = sent[max(0, m.start() - _MARKER_CHARS):m.end() + _MARKER_CHARS]
                    demoted = bool(_NEGATION.search(before)) or \
                        bool(_CORRECTION_MARKER.search(near)) or \
                        bool(lawful and re.search(lawful, sent, re.IGNORECASE))
                    (mentions if demoted else hits).append(
                        {"matched": m.group(0), "sentence": sent.strip()[:300]})
        if hits:
            out.append((cls["id"], "ASSERTS", hits))
        elif mentions:
            out.append((cls["id"], "MENTIONS_UNDER_NEGATION", mentions))
    return out


def _self_test():
    """R26 both directions, before the sweep is trusted. Each specimen is a real shape."""
    cases = [
        ("PAYE ya mwezi", "Baada ya punguzo la kibinafsi TZS 26,000, PAYE = TZS 0.",
         "paye_phantom_personal_relief", "ASSERTS",
         "the exact quarantined 2026-08-25 body"),
        ("PAYE ya mwezi", "Hakuna punguzo la kibinafsi Tanzania; kanda ya 0% ni kizingiti.",
         "paye_phantom_personal_relief", None,
         "a row that REJECTS the relief must not be flagged -- the shape the 2026-09-01 "
         "'tarehe 20' sweep deleted as if it were a defect. ⚠️ EXPECTED `None`, NOT "
         "`MENTIONS_UNDER_NEGATION`, and the change is the narrowing working: the row carries "
         "no FIGURE, so it is not a candidate at all rather than a demoted one. Relying on the "
         "negation rule to rescue a term-only row is one rule away from flagging it"),
        ("Kizingiti cha EFD", "Kizingiti ni mauzo ya TZS 11,000,000 kwa mwaka.",
         "efd_threshold_fabrication", "ASSERTS", "the fabrication in DIGITS"),
        ("Kizingiti cha EFD", "Kizingiti ni mauzo ya milioni 11 kwa mwaka.",
         "efd_threshold_fabrication", "ASSERTS",
         "THE SAME CLAIM IN WORDS. Every figure-keyed sweep in this arc missed this form, "
         "because the fact's own wrong_patterns hold digits"),
        ("Kizingiti cha EFD", "Hakuna kizingiti cha EFD. SI TZS 11,000,000.",
         "efd_threshold_fabrication", "MENTIONS_UNDER_NEGATION",
         "SENTENCE-FINAL negated figure -- the boundary that blocked a trailing '.' reported "
         "this CLEAN and removed a real finding"),
        ("Cheti cha VAT ya zuio", "Cheti hutolewa siku VAT inapodaiwa, SI tarehe 20.",
         "vat_withholding_deadline_20th", "MENTIONS_UNDER_NEGATION",
         "train_sft:3196 verbatim shape -- the row the 2026-09-01 sweep removed for "
         "REJECTING the 20th. Correct data, deleted by a presence check"),
        ("Faini ya NSSF", "Faini ya juu ni TZS 100,000 kwa mujibu wa sheria.",
         "nssf_fine_ceiling_100k", "ASSERTS", "a 100x understatement, asserted"),
        ("Faini ya NSSF", "Faini ya juu ni TZS 10,000,000 -- si laki moja.",
         "nssf_fine_ceiling_100k", "MENTIONS_UNDER_NEGATION",
         "the correction's own text, in words. A sweep that flags this flags the fix"),

        # ── THE TWO FALSE DEMOTIONS, PINNED AS POSITIVES ────────────────────────────────
        # Both are rows that genuinely ASSERT a defect and were excused by an over-broad
        # correction marker. They are the dangerous direction -- a demotion rule that is too
        # generous does not add noise, it DELETES FINDINGS -- so they are pinned as MUST-ASSERT.
        ("Hii faini ya laki moja inawahusu nani?",
         "Faini ya shilingi elfu mia moja (TZS 100,000) hutolewa kwa makosa yanayohusu utii wa "
         "sheria. Thibitisha na NSSF (nssf.go.tz).",
         "nssf_fine_ceiling_100k", "ASSERTS",
         "`makosa` here means OFFENCES, not errors. A bare `\\bmakosa\\b` correction marker "
         "demoted this to a mention -- so the over-removal arm reported a row asserting a 100x "
         "understatement as correct data wrongly removed. Narrowed to the predicative "
         "`ni makosa`"),
        ("Nimeambiwa EFD ni kwa wafanyabiashara wa TZS 40M au zaidi — sahihi?",
         "Hapana, si sahihi. EFD inahitajika kwa biashara zenye mauzo ya TZS milioni 11 au zaidi "
         "kwa mwaka.",
         "efd_threshold_fabrication", "ASSERTS",
         "ONE SENTENCE REJECTING ONE VALUE AND ASSERTING ANOTHER -- it refutes 40M correctly and "
         "asserts the fabricated 11M, which is the worst row in the whole EFD quarantine. A "
         "sentence-wide correction marker excused BOTH figures; the marker now has to sit within "
         "_MARKER_CHARS of the value it excuses"),
        ("Nimeambiwa EFD ni kwa wafanyabiashara wa TZS 40M au zaidi — sahihi?",
         "VAT registered businesses ZOTE lazima zitumie EFD bila kujali kiasi cha mauzo. "
         "Kizingiti sahihi ni TZS milioni 11 — si 40M.",
         "efd_threshold_fabrication", "ASSERTS",
         "`sahihi ni` DIRECTLY IN FRONT OF THE FABRICATION, asserting it AS the correct "
         "threshold. The cue was in BOTH the negation rule and the correction marker, and "
         "removing it from one left the other demoting this row -- so the sweep still reported "
         "the worst row in the EFD quarantine as correct data wrongly deleted. A cue that "
         "appears in two rules has to be removed from two rules"),

        # ── THE BAD SPECIMENS ARE LOADED VERBATIM, NOT RETYPED — see CORPUS_NEGATIVES ────
        # ⛔ MY FIRST ATTEMPT AT THEM WAS A PARAPHRASE AND TWO OF THEM SILENTLY STOPPED TESTING
        # ANYTHING. I shortened each row by hand for readability. One lost the trailing
        # "Thibitisha na OSHA (osha.go.tz)" -- the only occurrence of the row SUBJECT -- and one
        # lost its "PAYE" mention, so both specimens fell out of their own class and returned
        # "no verdict" for a reason that had nothing to do with the rule under test. They would
        # have passed as `None` forever while guarding nothing. R26 says use the verbatim
        # committed text; this is what happens when you don't, in the very file quoting the rule.
        # ── THE OLD INLINE SPECIMENS BELOW ARE SYNTHETIC BY DESIGN (they test the rules, not
        #    the corpus); the corpus-sourced ones live in CORPUS_NEGATIVES and are read from disk.
        # Each is a VERBATIM live corpus row the first draft flagged. They are kept because a
        # false defect is more expensive than a missed one: only the false positive generates an
        # edit, and that edit lands in correct data. Measured 2026-10-07, 5 of 7 classes.
        ("Kama kosa la OSHA litaendelea nini?",
         "Kama kosa la OSHA litaendelea, unatozwa faini ya TZS 100,000 kwa kila siku kosa "
         "linaendelea.",
         "nssf_fine_ceiling_100k", None,
         "train_sft:395 verbatim. The OSHA per-day fine IS TZS 100,000. A row subject of "
         "`faini|adhabu` matched every fine in the corpus; it must be NSSF only"),
        ("Kampuni ya Uingereza inatumia asilimia 25 au 30?",
         "Kiwango cha asilimia 25 kinatokana na ORODHA ya hisa kwenye DSE kwa umma Tanzania. "
         "Kampuni ambayo haijaorodhesha DSE inalipa kiwango cha kawaida cha asilimia 30.",
         "dse_stale_30pct_float", None,
         "train_sft:25 verbatim, a FULLY CORRECT answer. 30% is the standard corporate rate and "
         "25% is both the reduced rate and the float threshold -- coincident numbers, and the "
         "first draft read the correct rate as a stale float"),
        ("'personal relief' kwenye PAYE maana yake nini?",
         "Hakuna punguzo la kibinafsi (personal relief) tofauti — kizingiti cha 0% "
         "(TZS 270,000) NDIYO punguzo la ufanisi.",
         "paye_phantom_personal_relief", None,
         "train_sft:731 verbatim. The row SAYS THERE IS NONE. A term is not a claim -- only a "
         "FIGURE attached to the relief is testable"),
        ("Bendi ya pili ya PAYE Tanzania ni asilimia 9 — ni kweli?",
         "Hapana. Bendi ya pili (TZS 270,001-520,000) ni asilimia 8 ya kiasi kinachozidi "
         "TZS 270,000.",
         "paye_band2_at_9pct", None,
         "train_sft:1173's shape: the DEFECT IS IN THE QUESTION, by design, and the answer "
         "corrects it. Sweeping question+body together converts adversarial pairs -- the best "
         "rows in the corpus -- into findings"),
        ("Kodi ya stempu kwenye uhamishaji wa hisa ni ngapi?",
         "Kiwango cha kodi ya stempu kwenye uhamishaji wa hisa ni asilimia 1 ya thamani ya hisa.",
         "stamp_duty_flat_1pct", None,
         "train_sft:208 verbatim, and CORRECT -- 1% is lawful for this instrument. The class is "
         "in NOT_FIGURE_TESTABLE and must never be swept; this specimen fails loudly if someone "
         "adds it back"),
    ]
    cases = cases + _corpus_negatives()
    bad = []
    for q, body, cid, want, why in cases:
        got = {c: v for c, v, _ in classify(q, body)}
        if got.get(cid) != want:
            bad.append({"q": q, "body": body, "class": cid, "expected": want,
                        "got": got.get(cid), "all_verdicts": got, "why": why})
    assert not bad, ("THE INSTRUMENT IS BROKEN, NOT THE CORPUS:\n"
                     + json.dumps(bad, ensure_ascii=False, indent=2))
    return [{"q": q, "body": body, "class": c, "expected": w, "why_this_case_exists": y}
            for q, body, c, w, y in cases]


def _digest(path):
    if not os.path.exists(path):
        return {"path": path, "exists": False}
    data = io.open(path, "rb").read()
    n = sum(1 for line in data.decode("utf-8").splitlines() if line.strip())
    return {"path": path, "exists": True, "rows": n, "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest()}


def _sweep(paths, label):
    findings = collections.defaultdict(list)
    rows = 0
    for path in paths:
        rel = os.path.relpath(path, REPO).replace(os.sep, "/")
        for n, obj in _rows(path):
            rows += 1
            q, body = _text(obj)
            for cid, verdict, hits in classify(q, body):
                findings[(cid, verdict)].append(
                    {"at": f"{rel}:{n}", "question": q[:160],
                     "matched": sorted({h["matched"] for h in hits}),
                     "sentence": hits[0]["sentence"]})
    print(f"\n{label}: {rows} rows, {len(paths)} file(s)")
    return rows, findings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild", action="store_true",
                    help="run the mandatory pre-checks and regenerate datasets/tier1a/sft/")
    args = ap.parse_args()

    specimens = _self_test()
    print(f"instrument exercised: {len(specimens)} planted specimens, both directions\n")

    before = [_digest(os.path.join(REPO, *p.split("/"))) for p in TRAINING_FILES]
    for d in before:
        print(f"  BEFORE {d['path']}: {d.get('rows')} rows  sha256 {str(d.get('sha256'))[:12]}")

    precheck = {}
    if args.rebuild:
        # CLAUDE.md s.9 mandatory pre-task checks, run and RECORDED -- not assumed.
        for name, cmd in [("clean_temp_files",
                           [sys.executable, "scripts/clean_temp_files.py", "--scan"]),
                          ("check_eval_split",
                           [sys.executable, "scripts/check_eval_split.py"])]:
            p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                               errors="replace")
            precheck[name] = {"exit": p.returncode, "tail": (p.stdout or "")[-600:]}
            print(f"\n[{name}] exit {p.returncode}")
            assert p.returncode == 0, (
                f"{name} exited {p.returncode}. CLAUDE.md s.9: fix the issue before "
                f"proceeding, do not bypass.\n{p.stdout}\n{p.stderr}")
        p = subprocess.run([sys.executable, "scripts/generate_sft.py"], capture_output=True,
                           text=True, encoding="utf-8", errors="replace")
        precheck["generate_sft"] = {"exit": p.returncode, "tail": (p.stdout or "")[-1500:]}
        print(f"\n[generate_sft] exit {p.returncode}\n{(p.stdout or '')[-900:]}")
        assert p.returncode == 0, p.stderr

    after = [_digest(os.path.join(REPO, *p.split("/"))) for p in TRAINING_FILES]
    for d in after:
        print(f"  AFTER  {d['path']}: {d.get('rows')} rows  sha256 {str(d.get('sha256'))[:12]}")

    train_rows, train_f = _sweep(
        [os.path.join(REPO, *p.split("/")) for p in TRAINING_FILES],
        "EXPORTED TRAINING FILES (what train_ddp.py reads)")
    up_paths = sorted(p for d in UPSTREAM_DIRS
                      for p in glob.glob(os.path.join(REPO, *d.split("/"), "*.jsonl")))
    up_rows, up_f = _sweep(up_paths, "UPSTREAM AUTHORED CORPUS (what the export is built from)")

    asserts = {f"{c}": v for (c, verdict), v in train_f.items() if verdict == "ASSERTS"}
    mentions = {f"{c}": len(v) for (c, verdict), v in train_f.items()
                if verdict == "MENTIONS_UNDER_NEGATION"}
    up_asserts = {f"{c}": len(v) for (c, verdict), v in up_f.items() if verdict == "ASSERTS"}

    print("\n" + "=" * 78)
    print("ASSERTS in the EXPORTED TRAINING FILES — this is the precondition:")
    if not asserts:
        print("  none")
    for cid, rows in sorted(asserts.items(), key=lambda kv: -len(kv[1])):
        print(f"  ⛔ {cid}: {len(rows)} row(s)")
        for r in rows[:4]:
            print(f"       {r['at']}  {r['matched']}")
            print(f"         {r['sentence'][:150]}")
    print("\nMENTIONS under negation in the training files (NOT defects, counted for the record):")
    for cid, n in sorted(mentions.items()):
        print(f"  ~ {cid}: {n}")
    print("\nASSERTS still upstream (cleaned_pairs/ + sft_shaped_pairs/):")
    if not up_asserts:
        print("  none")
    for cid, n in sorted(up_asserts.items()):
        print(f"  {cid}: {n}")

    out = {
        "_what": "The retrain precondition re-derived from scratch: the export rebuilt from the "
                 "current corpus, then swept on the CLAIM in both notations, polarity-aware.",
        "_why_this_population": (
            "The 2026-09-01 declaration swept the right files with figure-keyed patterns derived "
            "from each fact's own wrong_patterns, and was then invalidated by quarantines that "
            "fired one stage upstream of the export. This sweep's population is the CLAIM over "
            "the OUTPUT, so neither notation nor stage can hide a row."),
        "_what_this_cannot_show": (
            "Realism. Which claims a trained model actually reproduces is a weights question, not "
            "a corpus question. And a clean sweep is a LOWER BOUND on what was looked for (R21): "
            "17 classes are checked, every one previously found; a defect class nobody has "
            "discovered yet is not in this list."),
        "rebuilt": bool(args.rebuild),
        "precheck": precheck,
        "before": before,
        "after": after,
        "training_rows_swept": train_rows,
        "upstream_rows_swept": up_rows,
        "defect_classes_checked": [c["id"] for c in CLASSES],
        "defect_classes_NOT_figure_testable": NOT_FIGURE_TESTABLE,
        "asserts_in_training_files": {k: v for k, v in asserts.items()},
        "mentions_under_negation_in_training_files": mentions,
        "asserts_still_upstream": up_asserts,
        "planted_specimens": specimens,
        "verdict": "NOT MET" if asserts else "MET",
    }
    os.makedirs(os.path.dirname(os.path.join(REPO, ARTIFACT)), exist_ok=True)
    with io.open(os.path.join(REPO, ARTIFACT), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print(f"\nartifact: {ARTIFACT}")
    print(f"VERDICT: {out['verdict']}")
    return 1 if asserts else 0


if __name__ == "__main__":
    raise SystemExit(main())
