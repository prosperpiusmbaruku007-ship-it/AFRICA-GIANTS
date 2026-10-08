# -*- coding: utf-8 -*-
"""OVER-REMOVAL AUDIT, PHASE 2: THE 244 ROWS NO INSTRUMENT COULD JUDGE (2026-10-08).

Phase 1 (`audit_overremoval_by_class_2026_10_08.py`) measured the hole: of 501 removed
rows, only 257 carried a verdict. This file closes it, and the reason phase 1 could not is
worth stating because it is a design error, not a gap in effort:

  ⛔ PHASE 1 ASKED THE WRONG QUESTION. It ran the precondition classifier -- "does this row
  assert one of 17 known FIGURE defects?" A removed row can be free of all 17 and still be
  wrong for the reason it was removed, and most of the 244 are exactly that: the defect is
  MODALITY (GN487A: "may be revoked" vs "shall"), ATTACHMENT (which obligation the 20th
  belongs to), SCOPE (stamp duty's flat-vs-tiered), TERMINOLOGY (P45/P9) or TENSE (a passed
  cutoff stated as upcoming). None has a figure to key on. The right question is each row
  against ITS OWN RECORD'S STATED REASON, so that is what this does.

🔴 AND A CORRECTION TO PHASE 1's OWN HEADLINE FINDING, MADE BY READING THE RECORDS INSTEAD
OF ONE FIELD NAME. Phase 1 reported FOUR records as stating "no reason at all". That was
R34 -- a verdict inferred from metadata. The records use THREE different key names for the
same thing: `_quarantine.reasons` (a list), `reason` (a string), and `why` (a string).
Phase 1 read only the first.

  * `rent_wht_nonresident_15pct` HAS a precise reason: "asserts a 15% NON-RESIDENT rate on
    rent; Cap.332 First Schedule para 4(b)(ii) gives the non-resident limb the same TEN
    percent, and TRA's table reads 10%|10%." Phase 1's "the record is misnamed and nothing
    states what was wrong with these rows" was simply false.
  * `vat_deferment_stale_cutoff_framing` HAS one, and a better one than phase 1 credited:
    it names the UNSCOPED defect (imported vs locally manufactured) as well as the tense.
  * `efd_fabrication`, `nssf_fine`, `memorandum_articles` and `quarantine_survivors_reswept`
    all carry reasons under `why`/`reason`.

  ONLY TWO records genuinely have no reason anywhere: `sdl_tourism_levy_mislabeled` and
  `eval_contaminated`. The reason reader here walks all three key names and says which one
  it found, so the claim is checkable rather than inferred.

EVERY RULE IS QUOTED FROM THE RECORD IT TESTS. A rule invented by the auditor would be the
batch-reason failure one level up: a reason that could be true of the class rather than of
the row. Each rule below carries the record's own words in `from_reason`.

THREE OUTCOMES, AND THE THIRD IS NOT A PASS:
  ASSERTS_DEFECT   -- the row commits the thing its record names. Removal correct.
  REJECTS_DEFECT   -- the row denies it, or states the correct rule. OVER-REMOVAL.
  NOT_DETERMINABLE -- the rule cannot reach this row. Still unexamined, counted separately,
                      never folded into a "removals were correct" total. For an over-removal
                      hunt a false "that removal was fine" is the expensive error, because
                      the row is already gone and nothing will look again.

R26: every rule is planted in BOTH directions before it is trusted -- a specimen that must
flag and one that must pass. Positive-only certifies a rule that flags everything, and
negative-only is what the secret scan had.

REPORT-ONLY. This harness reads; it never edits a corpus.
"""
import collections
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
REJ = os.path.join(REPO, "datasets", "tier1a", "rejected")
OUT = os.path.join(REPO, "eval", "results", "overremoval_phase2_2026_10_08.json")

# ── WORD-BOUNDED NEGATION, 40-CHAR BACKWARD WINDOW ────────────────────────────────
# Both properties are load-bearing and both were learned the hard way: a bare `si\s`
# matches inside the ordinary Swahili word `kiasi `, and a sentence-wide marker scope
# excused a row that rejected one value while asserting another in the same sentence.
NEG = (r"(?:\bsi\b|\bsio\b|\bsiyo\b|\bhapana\b|\bhakuna\b|\bhaina\b|\bhakutakuwa\b"
       r"|\bni\s+makosa\b|\bsi\s+kweli\b|\buwongo\b|\bnot\b|\bno\b|\bincorrect\b"
       r"|\bis\s+wrong\b)")
WIN = 40


def asserts_value(pat, text):
    """Matches of `pat` NOT preceded by a negation inside WIN characters."""
    out = []
    for m in re.finditer(pat, text, re.I):
        before = text[max(0, m.start() - WIN):m.start()]
        if not re.search(NEG + r"[\s:,.;—\-\(\)]*(?:TZS\s*|asilimia\s*|tarehe\s*)?$",
                         before, re.I):
            out.append(m.group(0))
    return out


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?;\n])\s+", text) if s.strip()]


# ── RULE 1: GN487A REVOCATION MODALITY (129 rows, the largest single group) ───────
# `kunyim*` (denied/withheld) added after tier2 L54 -- "Visa vinaweza KUNYIMWA, lakini si
# lazima daima" is the defect verbatim and the first verb list could not see it. A verb
# list is exactly as complete as its author's recall (R36's worklist lesson).
_REVOCATION = re.compile(r"(?:kufutwa|kufuta|futwa|kuondolewa|kunyimwa|kunyima|nyimwa)", re.I)
_VISA = re.compile(r"(?:visa|kibali|ukaazi|ukazi|residence permit)", re.I)
_DISCRETIONARY = re.compile(
    r"\b(?:kunaweza|inaweza|linaweza|yanaweza|anaweza|huwezi|si\s+lazima"
    r"|wakati\s+mwingine|mara\s+nyingine|baadhi\s+ya\s+(?:kesi|hali)|may\b|might\b)", re.I)
_MANDATORY = re.compile(
    r"\b(?:lazima|ni\s+sharti|sharti|moja\s+kwa\s+moja|pamoja\s+na|bila\s+shaka"
    r"|hakika|automatically|shall\b|must\b)", re.I)


def rule_gn487a_visa(q, body):
    """The record: 'states visa/permit revocation as merely "possible" or "not always" --
    GN487A s.3(3)(a) makes it mandatory upon conviction ("shall be liable to ... AND
    revocation"), not discretionary.'

    So the defect is a MODAL, not a figure -- which is precisely why the figure-keyed
    classifier returned NO_VERDICT on all 129. Judged per REVOCATION SENTENCE, because a
    discretionary modal elsewhere in the row (about a court's sentencing choice, say) is
    not this defect."""
    revs = [s for s in sentences(body) if _REVOCATION.search(s) and _VISA.search(s)]
    if not revs:
        return "NOT_DETERMINABLE", "no sentence links revocation to a visa/permit"
    disc = [s for s in revs if _DISCRETIONARY.search(s)]
    mand = [s for s in revs if _MANDATORY.search(s) and not _DISCRETIONARY.search(s)]
    if disc:
        return "ASSERTS_DEFECT", f"discretionary revocation: \"{disc[0][:170]}\""
    if mand:
        return "REJECTS_DEFECT", f"mandatory revocation (correct): \"{mand[0][:170]}\""
    return "NOT_DETERMINABLE", f"revocation stated without a modal: \"{revs[0][:170]}\""


# ── RULE 2: VAT WITHHOLDING -- WHICH OBLIGATION DOES THE 20th ATTACH TO? ──────────
_D20 = re.compile(r"tarehe\s*(?:ya\s*)?20|20\s*ya\s*mwezi|\b20th\b", re.I)

# ⛔ THE FIRST VERSION OF THIS RULE WAS WRONG AND IT FAILED IN THE DELETING DIRECTION.
# It asked `_REMIT` in a 90-char window BEFORE the 20th (so it missed every Swahili word
# order that puts the subject first -- "VAT withholding INALIPWA TRA tarehe 20"), and then
# fell through to a REJECTS branch that fired if the word "return" appeared ANYWHERE in the
# sentence. Those rows routinely say both things in one breath ("...tarehe 20 -- siku ile
# ile ya VAT return ya kawaida"), so 28 ASSERTING rows were scored as over-removals: not
# noise, but false accusations against the remediation, which is the worse failure because
# a shorter finding list reads as progress and an accusation gets ACTED ON (R26's asymmetry).
#
# It was R33 in my own instrument. The rule had ONE assert-specimen and I had written it in
# the exact phrasing the regex was built around, so the specimen could only agree with it.
# Every specimen below is now VERBATIM from the record, including the word orders that broke
# version 1.
#
# THE SUBJECT, order-independent: what is being paid.
_WITHHELD = re.compile(
    r"(?:VAT\s+withholding|VAT\s+iliyokatwa|VAT\s+iliyozuiliwa|VAT\s+ya\s+zuio"
    r"|VAT\s+ya\s+kuzuia|kiasi\s+kilichokatwa|kiasi\s+kilichozuiliwa|kodi\s+iliyozuiliwa"
    r"|withheld\s+VAT|zuio\s+la\s+VAT|fedha\s+ulizoshikilia|fedha\s+zilizoshikiliwa"
    r"|hizo\s+fedha)", re.I)
# THE ACT: remitting it to TRA. Covers lipa/lipwa/hulipwa/kilipwa/inalipwa/peleka/apeleke.
_PAY_TRA = re.compile(r"(?:\w*lip\w*|\w*pelek\w*|\w*wasilish\w*|\w*rejesh\w*"
                      r"|remit\w*)", re.I)
_TRA = re.compile(r"\bTRA\b", re.I)
_RETURN = re.compile(r"(?:return\w*|ritani)\s+(?:yako\s+|yake\s+)?(?:ya\s+)?VAT"
                     r"|VAT\s+return|return\s+ya\s+kawaida", re.I)


def _clause_of(sentence, idx):
    """The clause the 20th sits in. Split on clause boundaries only -- NOT on bare `na`,
    which is also an ordinary conjunction inside a single clause."""
    left = sentence[:idx]
    return re.split(r"[,;:—]|\s+--\s+|\bambayo\b|\bna\s*\(\d\)", left)[-1]


def rule_vatwh_20th(q, body):
    """The record: 'asserts VAT withholding is remitted/paid to TRA by the 20th of the
    following month. Finance Act 2026 s.95 ... repealed and replaced VAT Act s.71(5): the
    deadline is now within 10 days after the end of the tax period.'

    THE DEFECT IS ATTACHMENT, NOT PRESENCE. The 20th IS the correct VAT RETURN filing
    deadline -- CLAUDE.md states the distinction in terms ('the 20th is the return filing
    deadline, a different obligation') -- and this record has already produced two confirmed
    over-removals on exactly that confusion (train_sft:3196, and the row restored
    2026-10-08). So a row attaching the 20th to the RETURN ONLY is correct; a row attaching
    it to the REMITTANCE commits the defect, even if it mentions the return in the same
    sentence.

    ORDER OF TESTS MATTERS AND IS DELIBERATE: the remittance attachment is checked FIRST
    and across the whole row, so a row that commits the defect cannot be excused by also
    saying something true about the return."""
    hits = [s for s in sentences(body) if _D20.search(s)]
    if not hits:
        return "NOT_DETERMINABLE", "no 20th-of-the-month claim in the body"

    # 1. Does the row attach the 20th to the REMITTANCE anywhere? Subject + payment verb in
    #    the same clause as the 20th, in either order.
    for s in hits:
        for m in _D20.finditer(s):
            clause = _clause_of(s, m.start())
            scope = clause if len(clause) > 12 else s
            if _WITHHELD.search(scope) and _PAY_TRA.search(scope):
                neg = re.search(NEG + r"[\s:,.;—\-]*(?:tarehe\s*)?$",
                                s[max(0, m.start() - WIN):m.start()], re.I)
                if not neg:
                    return ("ASSERTS_DEFECT",
                            f"20th attached to the REMITTANCE: \"{s[:190]}\"")

    # 1b. ⛔ THE ANAPHORIC TRANSFER, which version 2 of this rule still missed and which
    #     changed a verdict. "Return ya VAT ... kufikia tarehe 20 ... Ni TAREHE HIYOHIYO ya
    #     kuwasilisha VAT ya kuzuia (withholding)." The second sentence attaches the 20th to
    #     the REMITTANCE without containing a date token at all, so every rule above -- all
    #     of which look for a date and then ask what it attaches to -- is blind to it by
    #     construction. Found by reading the rows the rule called over-removals (record
    #     lines 14/32), i.e. by the discipline of not trusting an adverse verdict.
    _ANAPHORA = re.compile(
        r"(?:tarehe\s+hiyo\s*hiyo|tarehe\s+hiyohiyo|tarehe\s+hiyo|siku\s+ile\s+ile"
        r"|siku\s+hiyo\s*hiyo|hiyohiyo|same\s+(?:date|day))", re.I)
    if re.search(r"tarehe\s*(?:ya\s*)?20|20\s*ya\s*mwezi", body, re.I):
        for s in sentences(body):
            if _ANAPHORA.search(s) and _WITHHELD.search(s):
                return ("ASSERTS_DEFECT",
                        f"20th transferred to the REMITTANCE anaphorically: \"{s[:190]}\"")

    # 2. Does it deny the 20th for the certificate/remittance outright? ("si tarehe ya 20")
    for s in hits:
        for m in _D20.finditer(s):
            if re.search(NEG + r"[\s:,.;—\-]*(?:tarehe\s*(?:ya\s*)?)?$",
                         s[max(0, m.start() - WIN):m.start()], re.I):
                return ("REJECTS_DEFECT",
                        f"explicitly denies the 20th for this obligation: \"{s[:190]}\"")

    # 3. Only now: the 20th attached to the RETURN with no remittance attachment anywhere.
    for s in hits:
        if _RETURN.search(s):
            return ("REJECTS_DEFECT",
                    f"20th attached to the RETURN only, which is correct: \"{s[:190]}\"")
    return "NOT_DETERMINABLE", f"20th present, attachment unresolved: \"{hits[0][:190]}\""


# ── RULE 3: STAMP DUTY -- FLATNESS CLAIM vs AN INCIDENTAL 1% MENTION ─────────────
_FLATNESS = re.compile(
    r"\b(?:bapa|flat)\b|hakuna\s+(?:mfumo\s+wa\s+)?ngazi|hakuna\s+(?:kiwango\s+cha\s+)?ngazi"
    r"|si\s+(?:mfumo\s+wa\s+)?ngazi|kiwango\s+kimoja|thamani\s+yote", re.I)
_TIERED_OK = re.compile(r"asilimia\s*0[.,]5[^.]{0,60}(?:100,?000|kwanza)"
                        r"|0[.,]5%[^.]{0,60}(?:100,?000|first)", re.I)


def rule_stamp_duty_flat(q, body):
    """The record: 'asserts a flat 1% stamp duty on land/building transfer -- Stamp Duty Act
    Cap.189 Schedule Art.22(b) sets a TIERED rate (0.5% on first TZS 100,000, then 1% on the
    excess).'

    Phase 1 found by hand that this ONE reason was applied to TWO kinds of row. The rule is
    therefore three-way on purpose: the FLATNESS claim is the defect, a bare 1% mention is
    not. Stamp duty is in NOT_FIGURE_TESTABLE precisely because 1% is lawful (R19's Guard B
    line), so a figure test cannot make this distinction and never could."""
    if _TIERED_OK.search(body):
        return "REJECTS_DEFECT", "states the tiered 0.5%-then-1% rule correctly"
    flat = [s for s in sentences(body) if _FLATNESS.search(s)
            and re.search(r"stempu|stamp", s, re.I)]
    if flat:
        return "ASSERTS_DEFECT", f"asserts flatness: \"{flat[0][:180]}\""
    if re.search(r"stempu|stamp", body, re.I) and re.search(r"asilimia\s*1\b|\b1%", body):
        return ("NOT_DETERMINABLE",
                "mentions a 1% stamp duty WITHOUT a flatness claim -- removable by repair "
                "rather than deletion; this is the WEAK-removal bucket phase 1 found by hand")
    return "NOT_DETERMINABLE", "no stamp-duty rate claim found"


# ── RULE 4: PATENT TERM -- FLAT 20 YEARS vs 10 + TWO 5-YEAR EXTENSIONS ───────────
def rule_patent_20flat(q, body):
    """The record: 'states patent term as a flat 20 years with no extension mechanism --
    Patents (Registration) Act Cap.217 s.39(1) sets a 10-year BASE term, extendable via two
    discretionary 5-year extensions to a maximum of 20.' So 20 is a lawful MAXIMUM and the
    defect is omitting the base term -- another scope defect wearing a figure."""
    if re.search(r"miaka\s*10|10\s*years|kuongeza|extension|nyongeza", body, re.I):
        return "REJECTS_DEFECT", "names the 10-year base term or the extension mechanism"
    if asserts_value(r"miaka\s*20|20\s*years", body):
        return "ASSERTS_DEFECT", "asserts a 20-year term with no base term or extension"
    return "NOT_DETERMINABLE", "no patent-term claim found"


# ── RULE 5: P9 / P45 TERMINOLOGY ─────────────────────────────────────────────────
def rule_p9_terminology(q, body):
    """The records: '"P9" is Kenyan (KRA) terminology, not a Tanzanian TRA form' and 'names
    "P9" as the Tanzanian alternative to a UK P45'. A pure terminology defect with NO figure
    -- NOT_FIGURE_TESTABLE says so in terms. A row is correct if it says P9 is Kenyan or
    names the real mechanism (the annual withholding certificate)."""
    if re.search(r"kenya|KRA", body, re.I) and re.search(r"\bP9\b", body, re.I):
        return "REJECTS_DEFECT", "identifies P9 as Kenyan/KRA terminology"
    if re.search(r"cheti\s+cha\s+(?:makato|mwaka|ajira)|withholding\s+certificate", body, re.I) \
            and not re.search(r"\bP9\b", body, re.I):
        return "REJECTS_DEFECT", "names the annual withholding certificate without using P9"
    if re.search(r"\bP9\b", body, re.I):
        return "ASSERTS_DEFECT", "uses 'P9' as a Tanzanian form without flagging it as Kenyan"
    return "NOT_DETERMINABLE", "no P9 reference in the body"


# ── RULE 6: A PASSED CUTOFF STATED AS UPCOMING (R32's shape in the corpus) ────────
_FUTURE = re.compile(r"\b(?:hadi|mpaka|inaruhusiwa\s+hadi|unaisha|itaisha|ni\s+tarehe"
                     r"|ya\s+mwisho|ukomo)\b", re.I)
_PAST_MARK = re.compile(r"\b(?:ilikuwa|imepita|ilipita|tarehe\s+iliyopita|zamani"
                        r"|haitumiki\s+sasa|was\b|expired|has\s+passed)\b", re.I)


def rule_vat_deferment_tense(q, body):
    """The record: 'STALE_CUTOFF_UNSCOPED: states "30 June 2026" as the deferment end date
    with no scope (imported vs. locally manufactured) and no indication the date has already
    passed.' Today is after 30 June 2026, so a FUTURE framing is now wrong -- the date is
    right and the tense is not."""
    hits = [s for s in sentences(body)
            if re.search(r"30\s*Juni\s*2026|Juni\s*30,?\s*2026|30\s*June\s*2026", s, re.I)]
    if not hits:
        # ⛔ A DATELESS PRESENT-TENSE LIMB, added after record L5, whose own reason is
        # "STALE_CUTOFF_PRESENT_TENSE_SCOPED_WRONG" -- it describes the scheme as CURRENTLY
        # available ("ni mfumo unaokuruhusu...", "Unaruhusiwa...") and never names the date
        # at all. A rule that keys on the date cannot see the tense defect when the date is
        # absent, which is the same blind spot as the anaphoric transfer above: both defects
        # are about a date the sentence does not contain.
        if re.search(r"\b(?:ni\s+mfumo\s+unaokuruhusu|unaruhusiwa|inaruhusiwa|unaweza\s+"
                     r"kuahirisha|kuahirisha\s+malipo)\b", body, re.I) \
                and re.search(r"deferment|kuahirisha", body, re.I) \
                and not _PAST_MARK.search(body):
            return ("ASSERTS_DEFECT",
                    "describes VAT deferment as CURRENTLY available, present tense, with no "
                    "date and no past marker -- the cutoff passed on 30 June 2026")
        return "NOT_DETERMINABLE", "no 30 June 2026 claim and no present-tense availability"
    for s in hits:
        if _PAST_MARK.search(s):
            return "REJECTS_DEFECT", f"marks the cutoff as past: \"{s[:170]}\""
    for s in hits:
        if _FUTURE.search(s):
            return "ASSERTS_DEFECT", f"states a passed cutoff as upcoming: \"{s[:170]}\""
    return "NOT_DETERMINABLE", f"cutoff stated without tense: \"{hits[0][:170]}\""


# ── RULE 7: RENT WHT -- A NON-RESIDENT RATE OTHER THAN 10% ───────────────────────
def rule_rent_wht(q, body):
    """The record: 'asserts a 15% NON-RESIDENT rate on rent; Cap.332 First Schedule para
    4(b)(ii) gives the non-resident limb the same TEN percent, and TRA's table reads
    10%|10%.' Phase 1 called this record misnamed; it is not -- the reason is exact and
    sits under `reason`, which phase 1 did not read."""
    # ⛔ RENT CONTEXT IS ESTABLISHED AT ROW LEVEL, THEN RATE CLAIMS ARE TESTED PER
    #    SENTENCE -- not both in the same sentence, which is what the first version did and
    #    why it could not reach record L5. There the rent subject is in sentence 1 ("Kodi ya
    #    zuio kwenye PANGO ... ni asilimia 10, si asilimia 15") and the defect is in sentence
    #    2 ("Kwa asiye mkazi, kiwango ni asilimia 15"), which contains no rent word at all.
    #    Requiring subject and claim in one sentence is a narrower version of the same
    #    mistake as requiring a date and its attachment in one sentence (see the anaphoric
    #    transfer above): the row says one thing across two sentences.
    if not re.search(r"pango|rent", body, re.I):
        return "NOT_DETERMINABLE", "the row is not about rent"
    _NONRES = (r"wasio\s+wakaz|asiye\s+mkazi|asio\s+mkazi|si\s+mkazi|non-?resident"
               r"|nje\s+ya\s+nchi|10\s*/\s*20|10%\s*/\s*20%")
    for s in sentences(body):
        bad = asserts_value(r"asilimia\s*(?:15|20)\b|\b(?:15|20)%", s)
        if bad and re.search(_NONRES, s, re.I):
            return "ASSERTS_DEFECT", f"non-resident rent at {bad[0]}: \"{s[:170]}\""
    for s in sentences(body):
        if re.search(r"asilimia\s*10|\b10%", s) and re.search(
                r"wote|sawa|both|wakazi\s+na\s+wasio", s, re.I):
            return "REJECTS_DEFECT", f"states the single 10% rate: \"{s[:170]}\""
    return ("NOT_DETERMINABLE",
            f"rent row, rate claim unresolved: \"{sentences(body)[0][:170]}\"")


# ── SIMPLE VALUE RULES, polarity-aware ───────────────────────────────────────────
def _value_rule(pat, ctx, label):
    def f(q, body):
        if ctx and not re.search(ctx, body + " " + q, re.I):
            return "NOT_DETERMINABLE", f"row is not about {label}"
        bad = asserts_value(pat, body)
        if bad:
            return "ASSERTS_DEFECT", f"asserts {bad[0]!r}"
        if re.search(pat, body, re.I):
            return "REJECTS_DEFECT", f"names {label} only under a negation"
        return "NOT_DETERMINABLE", f"no {label} claim in the body"
    return f


def rule_personal_relief(q, body):
    """The record: 'asserts a TZS 26,000/27,000 personal relief -- CLAUDE.md s.11: "Any pair
    mentioning TZS 26,000 personal relief is WRONG"'. Tanzania has no separate personal
    relief; the 0% band on the first TZS 270,000/month IS the tax-free amount."""
    rel = [s for s in sentences(body)
           if re.search(r"punguzo\s+la\s+kibinafsi|personal\s+relief|punguzo\s+binafsi", s, re.I)]
    if not rel:
        if asserts_value(r"26,?000|27,?000", body) and re.search(
                r"paye|kodi\s+ya\s+mapato", body, re.I):
            return "ASSERTS_DEFECT", f"a bare 26,000/27,000 deduction in a PAYE context"
        return "NOT_DETERMINABLE", "no personal-relief claim in the body"
    for s in rel:
        if re.search(r"\b(?:hakuna|haipo|haupo|hamna|no\s+separate|does\s+not\s+exist"
                     r"|si\s+kweli)\b", s, re.I):
            return "REJECTS_DEFECT", f"states there is NO personal relief: \"{s[:170]}\""
    for s in rel:
        if asserts_value(r"26,?000|27,?000|312,?000", s):
            return "ASSERTS_DEFECT", f"asserts the phantom relief: \"{s[:170]}\""
    return "NOT_DETERMINABLE", f"relief mentioned without a figure: \"{rel[0][:170]}\""


def rule_nssf_mining_55(q, body):
    """The record: 'asserts NSSF has a mining-specific 55-year retirement provision -- NSSF
    Act Cap.50 Part V has no such provision; 55 is a GENERAL early-retirement age for any
    insured person (ss.25(c),29). Fabricated during authoring.'

    So 55 itself is lawful -- it is the MINING ATTRIBUTION that is fabricated. Another scope
    defect wearing a figure, which is exactly why a figure sweep returned NO_VERDICT on all
    17."""
    hits = [s for s in sentences(body) if re.search(r"\b55\b|miaka\s*55", s)]
    if not hits:
        return "NOT_DETERMINABLE", "no retirement-age 55 claim"
    for s in hits:
        if re.search(r"madini|mining|uchimbaji|mchimbaji", s, re.I):
            if re.search(r"\b(?:hakuna|si\s+kweli|hapana|haipo)\b", s, re.I):
                return "REJECTS_DEFECT", f"denies the mining-specific provision: \"{s[:170]}\""
            return "ASSERTS_DEFECT", f"attributes 55 to mining: \"{s[:170]}\""
    for s in hits:
        if re.search(r"kustaafu\s+mapema|early\s+retirement|mtu\s+yeyote|wote", s, re.I):
            return ("REJECTS_DEFECT",
                    f"55 stated as general early retirement, which is correct: \"{s[:170]}\"")
    return "NOT_DETERMINABLE", f"55 present, attribution unresolved: \"{hits[0][:170]}\""


def rule_wcf_disease_flat7(q, body):
    """The record: 'asserts occupational disease must reach WCF within a flat 7 working days
    of diagnosis -- GN 185/2016 Reg.16 is a two-stage chain (employee-to-employer 14 working
    days, then employer-to-WCF 7 more); true worst case is 21 working days.'

    '7 working days' is CORRECT for the accident-reporting obligation, so the figure appears
    lawfully in adjacent rows -- NOT_FIGURE_TESTABLE names this one explicitly. The defect is
    collapsing a CHAIN, so the test is for the chain's presence, not for the number."""
    dis = [s for s in sentences(body)
           if re.search(r"ugonjwa|disease|magonjwa", s, re.I) and re.search(r"\b7\b|siku\s*7", s)]
    if not dis:
        return "NOT_DETERMINABLE", "no occupational-disease 7-day claim"
    if re.search(r"\b14\b|siku\s*14|\b21\b|siku\s*21", body):
        return "REJECTS_DEFECT", "names the 14-day or 21-day limb of the chain"
    return "ASSERTS_DEFECT", f"flat 7 days for disease, chain collapsed: \"{dis[0][:170]}\""


# ⛔ KEYED ON THE STATED REASON, NOT ON (record, declared_class) -- AND THAT WAS A REAL
# DEFECT IN VERSION 1 OF THIS FILE, NOT A REFINEMENT. One rule per record is the BATCH-REASON
# ERROR, which is the thing this whole audit exists to find: `paye_defect` carries TWO
# distinct per-row reasons (11 rows "band 2 at 9%", 64 rows "TZS 26,000 personal relief") and
# `fabrication_and_deadline` carries two more. Keying by record applied the 9% rule to 45
# rows whose own reason was the phantom relief, and they came back NOT_DETERMINABLE -- the
# instrument reproducing the error it was built to detect. The records are better documented
# than my first rule table assumed: 44 distinct reason signatures, and
# efd_fabrication_all_notations carries a separate reason for every one of its 14 rows.
REASON_RULES = [
    ("TZS 26,000/27,000 personal relief", rule_personal_relief),
    ("mining-specific 55-year retirement", rule_nssf_mining_55),
    ("occupational disease must reach WCF within a flat 7", rule_wcf_disease_flat7),
]

RULES = {
    ("tier2_confirmed_wrong_quarantine_2026_08_31.jsonl", "GN487A_VISA"): (
        rule_gn487a_visa, 'states visa/permit revocation as merely "possible" or "not '
                          'always" -- GN487A s.3(3)(a) makes it mandatory upon conviction'),
    ("vat_withholding_deadline_stale_quarantine_2026_09_01.jsonl",
     "VATWH_REMITTANCE_STALE_20TH"): (
        rule_vatwh_20th, "asserts VAT withholding is remitted/paid to TRA by the 20th ... "
                         "FA2026 s.95 ... now within 10 days after the end of the tax period"),
    ("tier2_confirmed_wrong_quarantine_2026_08_31.jsonl", "STAMP_DUTY_FLAT1"): (
        rule_stamp_duty_flat, "asserts a flat 1% stamp duty ... Cap.189 Art.22(b) sets a "
                              "TIERED rate (0.5% on first TZS 100,000, then 1%)"),
    ("tier2_confirmed_wrong_quarantine_2026_08_31.jsonl", "PATENT_20FLAT"): (
        rule_patent_20flat, "states patent term as a flat 20 years ... Cap.217 s.39(1) sets "
                            "a 10-year BASE term, extendable to a maximum of 20"),
    ("tier2_confirmed_wrong_quarantine_2026_08_31.jsonl", "PAYE_P9_31MARCH"): (
        _value_rule(r"31\s*Machi|31\s*March", r"\bP9\b|cheti", "the 31 March P9 deadline"),
        'asserts Form "P9" due 31 March ... the obligation is due 30 January'),
    ("tier2_confirmed_wrong_quarantine_2026_08_31.jsonl", "VAT_JULY2024"): (
        _value_rule(r"Julai\s*2024|July\s*2024", r"vat|kizingiti", "the July 2024 date"),
        "dates the VAT 100M->200M increase to July 2024 -- GN 448Y/2023 commenced 1 July 2023"),
    ("precondition_confirmed_wrong_quarantine_2026_10_08.jsonl", "paye_p9_31_march"): (
        _value_rule(r"31\s*Machi|31\s*March", r"\bP9\b|cheti", "the 31 March P9 deadline"),
        "asserts the certificate is due 31 March; Cap.332 R.E.2023 s.110(3)(b) says 30 January"),
    ("precondition_confirmed_wrong_quarantine_2026_10_08.jsonl", "vat_threshold_dated_2024"): (
        _value_rule(r"Julai\s*2024|July\s*2024", r"vat|kizingiti", "the July 2024 date"),
        "dates the threshold increase to July 2024; GN 448Y/2023 commenced 1 July 2023"),
    ("presumptive_stale_ceiling_rate_quarantine_2026_09_01.jsonl",
     "PRESUMPTIVE_STALE_CEILING_OR_RATE"): (
        _value_rule(r"100,?000,?000|milioni\s+100|asilimia\s*3[.,]5|3[.,]5%",
                    r"makisio|presumptive", "the stale ceiling or 3.5% rate"),
        "states the pre-FA2026 ceiling (TZS 100,000,000) and/or top-band rate (3.5%) as "
        "current; FA2026 s.27(a) raised the ceiling to 200,000,000 and the rate to 4.0%"),
    ("dse_stale_float_quarantine_2026_09_01.jsonl", "DSE_STALE_FLOAT_30"): (
        _value_rule(r"asilimia\s*30\s*ya\s*hisa|30\s*(?:per ?cent|%)\s*(?:of\s*)?(?:its\s*)?"
                    r"shares|angalau\s+asilimia\s+30", r"dse|soko\s+la\s+hisa|listed",
                    "the 30% public-float condition"),
        "asserts a >=30% public-float condition; FA2025 s.60(d)(i) lowered it to 25%"),
    ("tier3_confirmed_wrong_quarantine_2026_09_01.jsonl", "P45_P9_CONFLATION"): (
        rule_p9_terminology, 'names "P9" as the Tanzanian alternative to a UK P45'),
    ("tier3_confirmed_wrong_quarantine_2026_09_01.jsonl", "COURSE_FEE_250K"): (
        _value_rule(r"250,?000", r"osha|mafunzo|kozi", "the 250,000 OSHA course fee"),
        "states an OSHA training-course fee of TZS 250,000 with no identified course"),
    ("osha_course_fee_removed_pending_confirmation_2026_10_08.jsonl", "osha_course_fee_250k"): (
        _value_rule(r"250,?000", r"osha|mafunzo|kozi", "the 250,000 OSHA course fee"),
        "asserts an OSHA course fee of TZS 250,000 as a plain fact; course_fee is a HEDGE"),
    ("vat_deferment_stale_cutoff_framing_quarantine_2026_09_02.jsonl", None): (
        rule_vat_deferment_tense,
        'STALE_CUTOFF_UNSCOPED: states "30 June 2026" as the deferment end date with no '
        "scope and no indication the date has already passed"),
    ("rent_wht_nonresident_15pct_quarantine_2026_09_26.jsonl", None): (
        rule_rent_wht, "asserts a 15% NON-RESIDENT rate on rent; Cap.332 First Schedule "
                       "para 4(b)(ii) gives the non-resident limb the same TEN percent"),
    ("paye_defect_quarantine_2026_08_25.jsonl", None): (
        _value_rule(r"\b9%|asilimia\s*9\b", r"paye|bendi|band", "PAYE band 2 at 9%"),
        "computes PAYE band 2 at 9%; the locked rate is 8%"),
    ("efd_threshold_fabrication_quarantine_2026_08_29.jsonl", None): (
        # ⛔ THE `11M` ABBREVIATION IS A THIRD NOTATION, after digits and spelled-out
        # words. R36 recorded that a sweep built from a fact's own `wrong_patterns` is
        # blind to the WORDS because the patterns hold digits; this record writes the same
        # claim a third way ("TZS 11M+"), and 10 of its 14 rows use ONLY that form.
        #
        # ⚠️ AND THIS LINE CARRIED A SILENT NO-OP FOR ONE ITERATION. A patch script wrote
        # its word-boundary escapes inside a NON-RAW Python string, so they compiled to
        # literal BACKSPACE characters (0x08) and the pattern demanded a backspace after
        # the M, matching nothing. (The first version of THIS COMMENT reproduced the same
        # bug: writing the escape literally in the patch script put two more backspaces
        # into the explanation. Describe such an escape in words, never by embedding it.)
        # backspace after the M, so it matched nothing. The self-test did not catch it
        # because no specimen used the `11M` form -- the same shape as R37's constructed
        # `lawful_attachment` pattern that matched nothing and left its escape as
        # decoration. Found only by introspecting the compiled closure.
        _value_rule(r"11,?000,?000|milioni\s+kumi\s+na\s+moja|milioni\s*11|11\s*milioni"
                    r"|TZS\s*11\s*M|11\s*M\+|11M",
                    r"efd|risiti|mashine", "the fabricated 11M EFD threshold"),
        "asserts a TZS 11,000,000 EFD turnover threshold; TAA Cap.438 s.44(1) sets none"),
    ("efd_fabrication_all_notations_quarantine_2026_10_06.jsonl", None): (
        _value_rule(r"11,?000,?000|milioni\s+kumi\s+na\s+moja|milioni\s*11|11\s*milioni"
                    r"|TZS\s*11\s*M|11\s*M\+|11M",
                    r"efd|risiti|mashine", "the fabricated 11M EFD threshold"),
        "the same fabrication in WORDS as well as digits -- a sweep keyed on digits is "
        "blind to 'milioni 11' by construction"),
    ("nssf_fine_stale_100k_quarantine_2026_10_05.jsonl", None): (
        _value_rule(r"100,?000(?![,.\d])|laki\s+moja|elfu\s+mia\s+moja",
                    r"nssf|faini|adhabu", "the stale TZS 100,000 NSSF fine ceiling"),
        "asserts TZS 100,000 as the current statutory fine; Cap.50 R.E.2023 s.76(1) reads "
        "ten million -- a 100x understatement"),
    ("memorandum_articles_fee_stale_22000_quarantine_2026_09_02.jsonl", None): (
        _value_rule(r"22,?000", r"memorandum|articles|katiba", "the stale 22,000 memo fee"),
        "asserts the generic 22,000-per-document rate for Memorandum and Articles "
        "specifically; BRELA's own fee page names a different figure"),
    ("fabrication_and_deadline_defect_quarantine_2026_08_29.jsonl", None): (
        _value_rule(r"11,?000,?000|milioni\s*11|31\s*Machi|100,?000(?![,.\d])",
                    None, "a fabricated figure or stale deadline"),
        "mixed fabrication and deadline defects (see per-row reasons in the record)"),
}

# Records deliberately NOT given a content rule, each with the reason stated at the site.
# R20: "no assertion needed here" is a valid, recordable outcome -- and inventing a rule
# for these would manufacture verdicts on a question they do not answer.
NO_RULE = {
    "eval_contaminated.jsonl":
        "NOT A CORRECTNESS QUESTION. These 9 rows were removed under R6 to preserve the "
        "training/eval split, and phase 1 read 4 of them and found them CORRECT (two sound "
        "OOC refusals, a PAYE computation on TZS 800,000 exactly right against the locked "
        "bands, a GN 605A row stating 33.4%). Correctness was never the removal criterion, "
        "so neither ASSERTS nor REJECTS means anything here. This record genuinely carries "
        "no stated reason anywhere -- one of only TWO that do not.",
    "sdl_tourism_levy_mislabeled.jsonl":
        "NO STATED REASON ANYWHERE -- the other of the two. Adjudicated by hand in phase 1: "
        "all 3 rows assert a 'tourism development levy' of 1% under subdomain "
        "sdl_compliance, no such levy is a locked fact, and one computes 1% x TZS 50,000,000 "
        "= 500,000 confidently. Removal correct, but the only account of WHY is the filename, "
        "which cannot be checked against any row.",
    "quarantine_survivors_reswept_2026_10_06.jsonl":
        "NOT A CONTENT CLAIM. Its `why` reads 'already quarantined in "
        "nssf_fine_stale_100k... and STILL LIVE in sft_EXPORTED_TRAINING -- the quarantine "
        "was pointed at the authored corpus'. These rows were re-removed because an earlier "
        "quarantine did not REACH the export (R36). The content verdict already exists in "
        "the original record; re-judging it here would double-count.",
}

# ── HAND ADJUDICATION OF THE RESIDUAL 8 LINES (= 3 DISTINCT ROWS), 2026-10-08 ────
# Read individually, because a rule that could reach them would have to be loose enough to
# reach the rows next to them too. Recorded here rather than converted into rules, which is
# the honest end state for a residue of three: a rule written to make a census look complete
# is R20's vacuous check.
HAND_ADJUDICATED_RESIDUE = [
    {
        "rows": "stamp_duty_138 (tier2 L7/L60/L74/L180 -- 4 lines, 1 row)",
        "verdict": "WEAK REMOVAL -- repairable, not deletable",
        "basis": "The row's SUBJECT is first-time-buyer relief and its answer is correct: "
                 "Tanzania has no such relief, unlike the UK or Australia. The 1% appears "
                 "once, in passing, with no flatness claim. Its record's reason -- 'asserts "
                 "a flat 1% stamp duty' -- is true of stamp_duty_101 and _108, which "
                 "explicitly deny tiering, and NOT of this row. Striking one word would have "
                 "kept it. Not scored as an over-removal because the word is still wrong; "
                 "not scored as a correct removal because the stated reason is not true of "
                 "it.",
    },
    {
        "rows": "the VAT_JULY2024 row (tier2 L53/L124 -- 2 lines, 1 row)",
        "verdict": "OVER-REMOVAL on the record's own reason",
        "basis": "The record's reason is 'dates the VAT 100M->200M increase to July 2024'. "
                 "THE ROW STATES NO DATE AT ALL: 'Hicho kiasi cha TZS 200M au TZS 100M ni "
                 "kiwango cha mauzo kinachosababisha usajili wa lazima kwa ajili ya VAT.' "
                 "Both figures are correct (200M/12mo, 100M/6mo) and the row cannot commit a "
                 "dating defect it never commits to a date. Removed on a batch reason that "
                 "was true of its siblings.",
    },
    {
        "rows": "the 'tarehe muafaka' row (vat_withholding L12/L36 -- 2 lines, 1 row)",
        "verdict": "OVER-REMOVAL on the record's own reason",
        "basis": "'Ndiyo, kuna adhabu ya riba au tozo endapo utashindwa kuwasilisha VAT "
                 "withholding ifikapo TAREHE MUAFAKA' -- 'by the appropriate date', naming "
                 "no date. The record's reason is specifically that the row asserts the "
                 "20th. It does not, and what it does say (that late remittance draws "
                 "interest or a penalty) is true under FA2026 s.95 as much as before it. "
                 "Vague, and vagueness is not a removable defect.",
    },
]

# ── PLANTED SPECIMENS, BOTH DIRECTIONS, FOR EVERY RULE (R26) ─────────────────────
SPECIMENS = [
    (rule_gn487a_visa, "kufutwa kwa visa na kibali cha ukaazi kunaweza kutokea kama sehemu "
                       "ya adhabu.", "ASSERTS_DEFECT", "verbatim from the record, line 12"),
    (rule_gn487a_visa, "Mahakama itaamua adhabu rasmi (faini AU kifungo) PAMOJA NA kufutwa "
                       "kwa visa.", "REJECTS_DEFECT", "verbatim from the record, line 16 -- "
                                                      "mandatory framing, correct"),
    (rule_gn487a_visa, "Faini ni TZS milioni 10 kwa mgeni anayeendesha saluni.",
     "NOT_DETERMINABLE", "no revocation sentence -- must not be judged"),
    # ⛔ ALL SIX VERBATIM FROM THE RECORD. Version 1 of this rule had ONE assert-specimen,
    # written by me in the phrasing the regex was built around, and it passed while the rule
    # inverted 28 asserting rows into over-removals (R33). The five asserting shapes below
    # are exactly the word orders that broke it: subject-first, passive, and numbered-list.
    (rule_vatwh_20th, "VAT withholding inalipwa TRA tarehe 20 ya mwezi unaofuata — siku ile "
                      "ile ya VAT return ya kawaida.", "ASSERTS_DEFECT",
     "record line 2/3 verbatim. SUBJECT-FIRST passive, AND it mentions the return in the "
     "same breath -- the shape that version 1 scored as an over-removal"),
    (rule_vatwh_20th, "Withholding agent lazima apeleke VAT iliyokatwa TRA ifikapo tarehe 20 "
                      "ya mwezi unaofuata mwezi wa manunuzi.", "ASSERTS_DEFECT",
     "record line 4 verbatim -- 'apeleke', which version 1's verb list missed"),
    (rule_vatwh_20th, "Tarehe 20 ya mwezi unaofuata ni tarehe ya: (1) kuwasilisha VAT return "
                      "ya kawaida na (2) kulipa TRA kiasi cha VAT withholding kilichokatwa.",
     "ASSERTS_DEFECT", "record line 6 verbatim -- a numbered list where limb (1) is correct "
                       "and limb (2) is the defect; a sentence-wide rule excuses both"),
    (rule_vatwh_20th, "Kiasi cha VAT withholding kilipwa TRA ifikapo tarehe 20 ya mwezi "
                      "unaofuata tarehe ya muamala.", "ASSERTS_DEFECT",
     "record line 7 verbatim -- 'kilipwa', past passive"),
    (rule_vatwh_20th, "Kodi ya VAT withholding hulipwa kabla au ifikapo tarehe 20 ya mwezi "
                      "unaofuata wa makato.", "ASSERTS_DEFECT",
     "record line 8 verbatim -- 'hulipwa', habitual; version 1 returned NOT_DETERMINABLE"),
    (rule_vatwh_20th, "Lazima utoe hati ya zuio la VAT kwa msambazaji siku ambayo VAT "
                      "inastahili kulipwa — si tarehe ya 20.", "REJECTS_DEFECT",
     "record line 1 verbatim -- the row ALREADY in ADJUDICATED_KEEPS as a known "
     "over-removal. It denies the 20th outright, and version 1 scored it NOT_DETERMINABLE"),
    (rule_vatwh_20th, "unatumia cheti kudai kiasi kilichozuiliwa kama input credit kwenye "
                      "return yako ya VAT, inayowasilishwa kufikia tarehe 20.",
     "REJECTS_DEFECT", "verbatim from the row RESTORED on 2026-10-08 -- the 20th on the "
                       "RETURN only. The specimen that must not flag"),
    (rule_vatwh_20th, "Return ya VAT inawasilishwa na kulipwa kufikia tarehe 20 ya mwezi "
                      "unaofuata mwezi wa biashara husika. Ni tarehe hiyohiyo ya kuwasilisha "
                      "VAT ya kuzuia (withholding).", "ASSERTS_DEFECT",
     "record lines 14/32 verbatim. THE ANAPHORIC TRANSFER: the second sentence attaches the "
     "20th to the remittance while containing no date token, so a rule that finds a date and "
     "asks what it attaches to cannot see it. Versions 1 AND 2 both called this an "
     "over-removal; reading it is what caught them"),
    (rule_stamp_duty_flat, "Ushuru wa stempu ni BAPA asilimia 1 kwenye thamani yote — "
                           "hakuna mfumo wa ngazi.", "ASSERTS_DEFECT", "flatness asserted"),
    (rule_stamp_duty_flat, "Ushuru wa stempu ni asilimia 0.5 kwa TZS 100,000 ya kwanza, "
                           "kisha asilimia 1.", "REJECTS_DEFECT", "the tiered rule, correct"),
    (rule_stamp_duty_flat, "Tanzania haina msamaha wa ushuru wa stempu kwa wanunuzi wa mara "
                           "ya kwanza; asilimia 1 inatumika kwa wote.", "NOT_DETERMINABLE",
     "stamp_duty_138's shape -- a bare 1% mention in a correct answer about something else; "
     "the WEAK-removal bucket, which must not be scored as a correct removal"),
    (rule_patent_20flat, "Hati miliki ya patent Tanzania ina muda wa miaka 20.",
     "ASSERTS_DEFECT", "flat 20 with no base term"),
    (rule_patent_20flat, "Patent ina muda wa msingi wa miaka 10, inayoweza kuongezwa mara "
                         "mbili kwa miaka 5 hadi miaka 20.", "REJECTS_DEFECT", "correct"),
    (rule_p9_terminology, "Fomu ya P9 ni ya usuluhishi wa mwaka wa PAYE Tanzania.",
     "ASSERTS_DEFECT", "P9 used as a Tanzanian form"),
    (rule_p9_terminology, "'P9' ni istilahi ya Kenya (KRA); Tanzania haina fomu hiyo.",
     "REJECTS_DEFECT", "correctly flags it as Kenyan"),
    (rule_vat_deferment_tense, "Mpango wa VAT deferment unaruhusiwa hadi tarehe 30 Juni 2026.",
     "ASSERTS_DEFECT", "a passed cutoff stated as upcoming"),
    (rule_vat_deferment_tense, "Tarehe ya mwisho ya VAT deferment ILIKUWA 30 Juni 2026 na "
                               "imepita.", "REJECTS_DEFECT", "correctly marked past"),
    (rule_rent_wht, "WHT kwa malipo ya nje: kodi ya pango asilimia 20 kwa wasio wakazi.",
     "ASSERTS_DEFECT", "a non-resident rent rate other than 10%"),
    (rule_rent_wht, "Kodi ya pango ni asilimia 10 kwa wakazi na wasio wakazi wote.",
     "REJECTS_DEFECT", "the single 10% rate, correct"),
    (rule_personal_relief, "Punguzo la kibinafsi ni TZS 26,000 kwa mwezi (TZS 312,000 kwa "
                           "mwaka).", "ASSERTS_DEFECT", "record line 7 verbatim"),
    (rule_personal_relief, "Tanzania HAKUNA punguzo la kibinafsi tofauti; kanda ya 0% ya "
                           "TZS 270,000 ndiyo kiwango kisicholipiwa kodi.", "REJECTS_DEFECT",
     "the correct statement -- must not be removed"),
    (rule_nssf_mining_55, "Umri wa kustaafu wa NSSF ni miaka 60 (au miaka 55 kwa sekta ya "
                          "madini).", "ASSERTS_DEFECT",
     "record line 5 verbatim -- 55 attributed to mining"),
    (rule_nssf_mining_55, "Miaka 55 ni umri wa kustaafu mapema kwa mtu yeyote aliyewekwa "
                          "bima chini ya NSSF.", "REJECTS_DEFECT",
     "55 as GENERAL early retirement is correct (ss.25(c),29) -- the figure is lawful and "
     "only the mining attribution is fabricated, so a figure test cannot tell them apart"),
    (rule_wcf_disease_flat7, "Ugonjwa wa kazi lazima uripotiwe WCF ndani ya siku 7 za kazi "
                             "kutoka siku ya utambuzi.", "ASSERTS_DEFECT",
     "flat 7 for disease, the chain collapsed"),
    (rule_wcf_disease_flat7, "Mfanyakazi anaripoti ugonjwa kwa mwajiri ndani ya siku 14 za "
                             "kazi, kisha mwajiri anaripoti WCF ndani ya siku 7.",
     "REJECTS_DEFECT", "names the two-stage chain, correct"),
    # ── SPECIMENS PINNING THE FOUR LIST WIDENINGS, each verbatim from the row that
    #    exposed the gap. Without these, a later tidy-up could narrow any of the four
    #    lists back and the rule would silently stop reaching these rows again.
    (rule_gn487a_visa, "Visa vinaweza kunyimwa, lakini si lazima daima.", "ASSERTS_DEFECT",
     "tier2 L54 verbatim -- `kunyimwa`, which the first revocation verb list missed"),
    (rule_vatwh_20th, "Unatakiwa kutoa cheti cha VAT withholding siku ambayo VAT inakuwa "
                      "inalipwa, huku ukirejesha hizo fedha ulizoshikilia ifikapo tarehe 20 "
                      "ya mwezi unaofuata.", "ASSERTS_DEFECT",
     "record L13 verbatim -- 'fedha ulizoshikilia' is the withheld amount under another "
     "name, which the first subject list missed"),
    (rule_rent_wht, "Hapana. Kodi ya zuio kwenye pango la ardhi au mali isiyohamishika "
                    "inayolipwa kwa mkazi Tanzania ni asilimia 10, si asilimia 15. Kwa "
                    "asiye mkazi, kiwango ni asilimia 15.", "ASSERTS_DEFECT",
     "record L5 verbatim, BOTH sentences. My first attempt at this specimen was the last "
     "sentence alone -- it lost the only mention of `pango`, fell out of the rule's own "
     "class, and returned NOT_DETERMINABLE for a reason unrelated to the rule under test. "
     "Caught by the self-test, which is what it is for (R26: use the verbatim text)."),
    (rule_vat_deferment_tense, "VAT Deferment ni mfumo unaokuruhusu kuahirisha malipo ya VAT "
                               "kwa bidhaa unazoingiza nchini, kwa muda fulani. Unaruhusiwa "
                               "kuuza bidhaa hizo kabla ya kulipa VAT.", "ASSERTS_DEFECT",
     "record L5 verbatim -- present-tense availability with NO date at all"),
]


def _self_test():
    bad, ran = [], []
    for fn, text, expect, why in SPECIMENS:
        got, detail = fn("", text)
        ran.append({"rule": fn.__name__, "expect": expect, "got": got, "why": why})
        if got != expect:
            bad.append({"rule": fn.__name__, "text": text[:120], "expect": expect,
                        "got": got, "detail": detail, "why": why})
    assert not bad, ("planted specimens failed -- the rules are not trustworthy yet:\n"
                     + json.dumps(bad, ensure_ascii=False, indent=2))
    return ran


def reason_of(o):
    """⛔ WALKS ALL THREE KEY NAMES. Phase 1 read only `_quarantine.reasons` and therefore
    reported four records as having no reason at all; two of them had precise ones under
    `reason`, and two more under `why`. Returns the key it found, so the claim 'this record
    states no reason' is checkable instead of inferred (R34)."""
    qn = o.get("_quarantine") or {}
    if qn.get("reasons"):
        return "_quarantine.reasons", (qn["reasons"] or [None])[0]
    for k in ("reason", "why"):
        if isinstance(o.get(k), str) and o[k].strip():
            return k, o[k]
    return None, None


def body_of(o):
    for k in ("output", "answer_sw", "response"):
        if isinstance(o.get(k), str) and o[k].strip():
            return o[k]
    if isinstance(o.get("row"), dict):
        return body_of(o["row"])
    return ""


def q_of(o):
    for k in ("instruction", "question_sw", "question"):
        if isinstance(o.get(k), str) and o[k].strip():
            return o[k]
    if isinstance(o.get("row"), dict):
        return q_of(o["row"])
    return ""


def meta_of(o):
    src = o["row"] if isinstance(o.get("row"), dict) else o
    return {"id": src.get("id"), "subdomain": src.get("subdomain"),
            "pair_type": src.get("pair_type")}


IS_ADV = re.compile(r"adversarial", re.I)


def main():
    specimens = _self_test()
    print(f"rules exercised: {len(specimens)} planted specimens across "
          f"{len({s['rule'] for s in specimens})} rules, all three outcomes\n")

    records = sorted(f for f in os.listdir(REJ) if f.endswith(".jsonl"))
    assert records, "no quarantine records read -- a census of nothing reports clean"
    out_rows, per_rec = [], []
    tot = collections.Counter()

    for name in records:
        rows = []
        for ln, line in enumerate(open(os.path.join(REJ, name), encoding="utf-8"), 1):
            if line.strip():
                rows.append((ln, json.loads(line)))
        verdicts = collections.Counter()
        over, undet = [], []
        no_rule_reason = NO_RULE.get(name)
        for ln, o in rows:
            dc = (o.get("_quarantine") or {}).get("defect_class") or o.get("defect_class")
            rk, reason = reason_of(o)
            # The row's OWN reason wins over any record-level rule.
            rule = None
            for sig, fn in REASON_RULES:
                if reason and sig in reason:
                    rule = (fn, reason[:200])
                    break
            rule = rule or RULES.get((name, dc)) or RULES.get((name, None))
            m = meta_of(o)
            entry = {"record": name, "line": ln, "id": m["id"],
                     "subdomain": m["subdomain"], "pair_type": m["pair_type"],
                     "declared_class": dc, "reason_key": rk,
                     "stated_reason": (reason or "")[:300],
                     "question": q_of(o)[:140], "body": body_of(o)[:360]}
            if no_rule_reason:
                entry["verdict"] = "NOT_A_CORRECTNESS_QUESTION"
                entry["detail"] = no_rule_reason
            elif not rule:
                entry["verdict"] = "NO_RULE"
                entry["detail"] = f"no rule defined for class {dc!r} in {name}"
            else:
                fn, from_reason = rule
                v, detail = fn(q_of(o), body_of(o))
                entry.update({"verdict": v, "detail": detail,
                              "rule": fn.__name__, "from_reason": from_reason})
            verdicts[entry["verdict"]] += 1
            tot[entry["verdict"]] += 1
            if entry["verdict"] == "REJECTS_DEFECT":
                over.append(entry)
            if entry["verdict"] == "NOT_DETERMINABLE":
                undet.append(entry)
            out_rows.append(entry)
        per_rec.append({"record": name, "rows": len(rows), "verdicts": dict(verdicts),
                        "over_removals": over, "still_not_determinable": undet})

    adv = [e for e in out_rows if IS_ADV.search(e.get("subdomain") or "")
           or IS_ADV.search(e.get("pair_type") or "")]
    judged = sum(v for k, v in tot.items()
                 if k in ("ASSERTS_DEFECT", "REJECTS_DEFECT"))
    total = sum(tot.values())

    payload = {
        "_what": "Phase 2: the 244 removed rows no instrument could judge, tested against "
                 "each record's OWN stated reason instead of against 17 figure patterns.",
        "_why_phase_1_could_not": "It asked whether a row asserts one of 17 known FIGURE "
                                  "defects. Most of these defects have no figure: modality "
                                  "(GN487A), attachment (which obligation the 20th belongs "
                                  "to), scope (stamp duty flat-vs-tiered), terminology "
                                  "(P45/P9), tense (a passed cutoff stated as upcoming).",
        "_correction_to_phase_1": "Phase 1 reported FOUR records as stating no reason at all. "
                                  "It read only `_quarantine.reasons`; the records use THREE "
                                  "key names (`_quarantine.reasons`, `reason`, `why`). "
                                  "rent_wht and vat_deferment have PRECISE reasons under "
                                  "`reason`, and efd_fabrication/nssf_fine/memorandum/"
                                  "survivors_reswept have them under `why`. ONLY TWO records "
                                  "genuinely have none: sdl_tourism_levy_mislabeled and "
                                  "eval_contaminated. Phase 1's claim was R34 -- a verdict "
                                  "inferred from one field name.",
        "_third_outcome_is_not_a_pass": "NOT_DETERMINABLE means the rule cannot reach the row. "
                                        "It is counted separately and never folded into a "
                                        "'removals were correct' total: for an over-removal "
                                        "hunt a false 'that removal was fine' is the expensive "
                                        "error, because the row is already gone.",
        "_rules_quoted_from_the_records": {f"{k[0]}::{k[1]}": v[1] for k, v in RULES.items()},
        "_records_with_no_content_rule": NO_RULE,
        "hand_adjudicated_residue": HAND_ADJUDICATED_RESIDUE,
        "_residue_note": "8 lines = 3 distinct rows, read individually. TWO are over-removals on their own records' reasons (a VAT row removed for dating an increase it never dates, and a row removed for asserting the 20th while saying 'tarehe muafaka' and naming no date); one is a WEAK removal repairable by striking a single word. A rule loose enough to reach these three would reach their correct neighbours too -- R20: inventing one to complete a census is the vacuous check.",
        "planted_specimens": specimens,
        "totals": dict(tot),
        "rows_total": total,
        "rows_judged": judged,
        "coverage_pct": round(100.0 * judged / total, 1) if total else None,
        "over_removals": [e for e in out_rows if e["verdict"] == "REJECTS_DEFECT"],
        "adversarial_rows": len(adv),
        "adversarial_over_removals": [e for e in adv if e["verdict"] == "REJECTS_DEFECT"],
        "per_quarantine_record": per_rec,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)

    print(f"{'record':58s} {'rows':>4s} {'ASRT':>5s} {'OVER':>5s} {'UNDET':>6s} {'other':>6s}")
    for r in per_rec:
        v = r["verdicts"]
        other = r["rows"] - v.get("ASSERTS_DEFECT", 0) - v.get("REJECTS_DEFECT", 0) \
            - v.get("NOT_DETERMINABLE", 0)
        flag = "  <-- OVER-REMOVAL" if v.get("REJECTS_DEFECT") else ""
        print(f"{r['record'][:58]:58s} {r['rows']:4d} {v.get('ASSERTS_DEFECT',0):5d} "
              f"{v.get('REJECTS_DEFECT',0):5d} {v.get('NOT_DETERMINABLE',0):6d} "
              f"{other:6d}{flag}")
    print(f"\n{dict(tot)}")
    print(f"PHASE 2 COVERAGE: {payload['coverage_pct']}% judged "
          f"({judged} of {total}); phase 1 was 51.3%")
    print(f"over-removals found: {len(payload['over_removals'])} "
          f"(adversarial: {len(payload['adversarial_over_removals'])} of {len(adv)})")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
