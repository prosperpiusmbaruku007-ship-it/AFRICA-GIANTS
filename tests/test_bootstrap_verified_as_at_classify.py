# -*- coding: utf-8 -*-
"""Known-good/known-bad fixture for scripts/bootstrap_verified_as_at.py's classify() function.

WHY THIS EXISTS. Twice in two commits (2026-09-02) the census under-counted a CORRECT fact for
a pure formatting reason: paye_personal_relief's verified_by said "direct primary-text read"
-- the regex requires "direct" immediately followed by "read" (whitespace only in between), so
the extra words broke the match and the fact was silently bucketed into 'unknown' despite being
genuinely statute-grounded. It was caught only because a DIFFERENT test
(test_locked_facts_finance_act_freshness.py) happened to fail downstream. The classifier itself
had never been tested against a fixture of facts already known to be correctly grounded -- only
ever debugged reactively, off whichever miss a different test's failure happened to surface.

This is the standing control test R26 asks for on every control: plant what it should catch
(known-good primary-source language, several real phrasings actually used in this corpus) and
confirm it FIRES (returns 'primary_verified' with the right date); plant a clean case (secondary-
only citations, a bare verified_date with no verified_by primary-read language) and confirm it
does NOT fire. A checker debugged only off real misses will keep having this shape -- this
fixture is what lets it be debugged off its own logic instead, before the next fact hits it.

Fixtures are literal strings, several copied verbatim from real locked_facts.json entries as of
2026-09-02, not paraphrased -- a paraphrase can silently drift from what the regex actually needs
to match (see R26's "verbatim, never a paraphrase" note on probe hygiene).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, 'scripts'))

from bootstrap_verified_as_at import classify  # noqa: E402

# Each row: (verified_by text, expected verified_as_at date or None if it must stay 'unknown')
# `None` for the date on a positive case is not used -- every KNOWN_GOOD row must extract a date,
# since a primary-read match with no extractable date is a THIRD, deliberately unknown outcome
# (covered separately below, not conflated with the "no primary-read language at all" case).
KNOWN_GOOD = [
    # "direct read" -- the plain, most common phrasing in this corpus.
    ("Direct read (2026-09-02) of Tax Administration Act Cap.438 R.E.2023 PDF, s.62(2)-(3) -- "
     "confirms the core claim at statute-tier.", "2026-09-02"),
    # "direct verbatim read" -- the _PRIMARY_READ pattern's optional "verbatim" branch.
    ("Direct verbatim read of Finance Act 2026 s.27(a), 2026-09-01, fetched in full (not "
     "summarised).", "2026-09-01"),
    # lowercase "direct read" -- re.I must actually be doing its job.
    ("direct read of BRELA's own business-name fee page, 2026-09-01: 'Ada ya maombi: "
     "15,000.00'", "2026-09-01"),
    # "read ... verbatim" with a few words between -- the second alternation branch, distinct
    # from "direct read". The regex caps the gap at 40 non-period characters, so this fixture
    # is deliberately short rather than a natural-sounding long sentence -- a longer, equally
    # plausible phrasing FAILED here on first write (see git history of this file), which is
    # exactly the kind of gap this fixture exists to surface.
    ("The Act's s.44 was read and quoted verbatim, 2026-08-31.",
     "2026-08-31"),
    # "quoted verbatim" standalone.
    ("GN 448Y s.4 quoted verbatim, 2026-08-31: 'deleting the phrase one hundred million "
     "shillings...'", "2026-08-31"),
    # "fetched in full".
    ("Finance Act 2023 fetched in full via curl on 2026-09-02, searched for 'deferment'.",
     "2026-09-02"),
    # "read in full" (also matches "read full" is NOT required -- "in" is optional per regex).
    ("The Tax Administration Act was read in full on 2026-08-25 for the objection provisions.",
     "2026-08-25"),
    # Month-YYYY date form instead of ISO -- the _MONTH_YEAR fallback path.
    ("Direct read of the gazette notice, August 2026, confirming the wage order text.",
     "2026-Aug"),
]

# Primary-read language IS present, but with no extractable date in the same string -- must stay
# 'unknown', not silently default to today or to a sibling field's date.
KNOWN_GOOD_BUT_UNDATED = [
    "Direct read of the Companies Act confirming s.197's minimum age requirement.",
    "Quoted verbatim from the current consolidation, exact fetch date not recorded.",
]

# No primary-source-engagement language at all -- portal/secondary citations, exactly the
# population this census is designed to leave honestly unknown rather than overclaim.
KNOWN_BAD = [
    "PWC Tax Summaries Tanzania (reviewed Jan 2026); Habib Advisory Tax Guide 2025/26",
    "TRA official SDL page",
    "WCF official website, Jun 2026",
    "Tanzania Immigration Department official website",
    "ARIPO; WIPO; US Trade.gov Tanzania IP report; IBA",
]

# THE REGRESSION CASE ITSELF, kept verbatim from the 2026-09-02 incident (see module docstring).
# This is NOT a bug fixture -- it documents that the regex's strictness is a known, ACCEPTED
# constraint (this project's own fix was to reword the fact, not loosen the regex: "An honest
# small number beats a populated field nobody can trust"). If someone widens _PRIMARY_READ later,
# this test will start failing and force them to notice they changed the census's own honesty
# bar, rather than let the change go unnoticed.
KNOWN_GOTCHA_STAYS_UNKNOWN = (
    "Direct primary-text read (2026-09-02) of the Income Tax Act's personal relief provisions."
)


def test_known_good_primary_read_phrasings_are_classified_primary_verified():
    fires, missed = [], []
    for text, expected_date in KNOWN_GOOD:
        status, date, _reason = classify({'verified_by': text})
        if status == 'primary_verified' and date == expected_date:
            fires.append(text)
        else:
            missed.append((text, expected_date, status, date))
    assert not missed, (
        f'{len(missed)} known-good primary-read phrasing(s) did NOT classify as '
        f'primary_verified with the expected date -- the classifier is INERT on text it should '
        f'fire on: {missed}')


def test_primary_read_language_without_a_date_stays_unknown_not_defaulted():
    for text in KNOWN_GOOD_BUT_UNDATED:
        status, date, reason = classify({'verified_by': text})
        assert status == 'unknown' and date is None, (
            f'{text!r} has primary-read language but no date in the same string -- must stay '
            f'unknown (never inferred/defaulted), got status={status!r} date={date!r}')
        assert 'no explicit date' in reason


def test_secondary_only_citations_are_not_classified_primary_verified():
    overbroad = []
    for text in KNOWN_BAD:
        status, _date, _reason = classify({'verified_by': text})
        if status == 'primary_verified':
            overbroad.append(text)
    assert not overbroad, (
        f'{len(overbroad)} secondary-only citation(s) were WRONGLY classified as '
        f'primary_verified -- the classifier is OVERBROAD, treating a portal/secondary source '
        f'as if it were a direct primary-text read: {overbroad}')


def test_missing_verified_by_field_is_unknown():
    status, date, reason = classify({})
    assert status == 'unknown' and date is None
    assert 'no verified_by' in reason


def test_the_paye_personal_relief_gotcha_still_reproduces_as_documented():
    """Confirms the KNOWN, ACCEPTED constraint that caused the 2026-09-02 incident still holds
    -- this is not asserting correct behaviour, it is asserting the DOCUMENTED behaviour, so a
    future change to _PRIMARY_READ's strictness is a deliberate, visible decision and not a
    silent side effect of an unrelated edit."""
    status, date, _reason = classify({'verified_by': KNOWN_GOTCHA_STAYS_UNKNOWN})
    assert status == 'unknown' and date is None, (
        'The extra-words-between-"direct"-and-"read" gotcha no longer reproduces -- if '
        '_PRIMARY_READ was deliberately widened, update this test to match and note the '
        'decision; if not, something changed the regex by accident.')
