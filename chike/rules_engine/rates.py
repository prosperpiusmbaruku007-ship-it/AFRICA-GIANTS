"""Rates and thresholds — copied verbatim from the v15 fact database.

EVERY constant here cites the source key in scripts/locked_facts.json. These are
NOT independent values: if a rate changes, it must change in the fact DB AND here
in the same commit (dual-file-sync rule, CLAUDE.md). The rules engine is only
"deterministic and correct" insofar as these match the human-verified facts.

Money is Decimal throughout — never float — because a rounding error on a
compliance figure is a wrong answer, not a cosmetic bug.

=== FINANCE-ACT FRESHNESS REGISTRY, added 2026-09-01 ===

WHY THIS EXISTS. The presumptive-tax engine (this file) served a wrong ceiling and rate for
two months after Finance Act 2026 changed them, because its own "verified through Finance Act
2020-2025" comment was true when written and became a silent trap the moment an Act outside
that fixed range came into force. A comment recording a year range is a CLAIM, not a mechanism
— nothing re-checked it against the calendar. This registry, and the test that reads it
(tests/test_finance_act_freshness.py), are that mechanism: every group of constants below
declares the last Finance Act year it was actually checked against, and the test fails the
moment CURRENT_FINANCE_ACT_YEAR moves ahead of any of them — a marker that cannot outlive its
reason, the same shape as this project's strict-xfail convention.

HOW TO USE THIS, THE NEXT TIME A FINANCE ACT IS GAZETTED:
  1. Bump CURRENT_FINANCE_ACT_YEAR. Every entry below now fails the freshness test.
  2. For each group, read the new Finance Act's relevant Part in full (not a summary) and
     confirm whether it touches that group's governing provision.
  3. Bump that group's year in FINANCE_ACT_VERIFIED_THROUGH to match, whether or not the Act
     touched it — "checked and found unchanged" is still a completed check. Update the
     constant's own value and the `evidence` string if it DID change.
  4. Do not bump a group's year without having actually read the Act. The whole point of this
     registry is that a year number is a claim someone can be asked to justify.

A group whose governing Act is CONFIRMED ABSENT from a given Finance Act's own list of
amended Acts (its table of Parts) may be marked verified through that year on that basis
alone — a Finance Act cannot silently amend an Act it does not list as one of its own Parts,
so absence from the list is itself a completed, citable check, not an assumption.

`None` in `FINANCE_ACT_VERIFIED_THROUGH` means "never independently verified against primary
statute text at all" — a different, worse status than "stale": PAYE_NONRESIDENT_RATE is the
one entry with this status, flagged during this same 2026-09-01 audit, not a new discovery
about it (it was already noted ungrounded in an earlier Tier 1 pass — see PROGRESS.md). The
freshness test does not fail on `None` entries; they are a separate, pre-existing item, not a
staleness incident, and are listed in `NEVER_GROUNDED` so they are not silently invisible to
anyone reading this registry.
"""

from decimal import Decimal

# The most recent Finance Act known to be in force. Bump this the moment a new one is gazetted
# -- see the module docstring for what happens next. 2026-09-01: Finance Act 2026 (in force
# 1 July 2026) is current.
CURRENT_FINANCE_ACT_YEAR = 2026

# group name -> (last Finance Act year checked, which governing Act/provision, how the check
# was done this session). Every SDL_*/NSSF_*/WCF_*/PAYE_BANDS/PRESUMPTIVE_*/CORPORATE_*/AMT_*/
# PARTNERSHIP_IS_TRANSPARENT constant belongs to exactly one group below.
FINANCE_ACT_VERIFIED_THROUGH = {
    'SDL': (2026, 'Vocational Education and Training Act Cap.82 s.14',
            'FA2026 Part XXVII (ss.97-98) read in full: touches only s.19 (funding-source '
            'wording), not s.14 (the SDL rate). Confirmed unchanged.'),
    'NSSF': (2026, 'National Social Security Fund Act',
             'NSSF Act is ABSENT from Finance Act 2026\'s own list of 28 amended Acts (Parts '
             'I-XXVIII) -- confirmed by reading that list in full. A Finance Act cannot amend '
             'an Act it does not list as one of its own Parts.'),
    'WCF': (2026, 'Workers Compensation Act / Workers Compensation Regulations 2016',
            'Same basis as NSSF: absent from FA2026\'s Parts list entirely.'),
    'PAYE_BANDS': (2026, 'Income Tax Act Cap.332 First Schedule para 1',
                   'FA2026 Part IX (ss.20-27) read in full: para 1 (individual PAYE table) is '
                   'not touched by s.27(a) at all -- confirmed directly, not inferred from the '
                   'paragraph-2/3/4 changes it does make. Second band (8%) separately '
                   're-confirmed against Finance Act 2021 s.25\'s own verbatim text.'),
    'PAYE_NONRESIDENT_RATE': (None, 'Income Tax Act Cap.332 (specific section not identified)',
                              'NEVER GROUNDED to primary statute text at any point -- verified_'
                              'by is a PwC portal page only (locked_facts.json, paye_nonresident'
                              '_flat_rate). Flagged in an earlier Tier 1 pass as ungrounded, '
                              're-flagged here rather than silently carried forward as if this '
                              'freshness registry had checked it. Needs its own primary-source '
                              'read, not a Finance-Act diff.'),
    'PRESUMPTIVE': (2026, 'Income Tax Act Cap.332 First Schedule para 2',
                    'THE 2026-09-01 INCIDENT ITSELF. FA2026 s.27(a) read verbatim in full and '
                    'the engine corrected the same session -- see the section below for the '
                    'complete change log. This is the freshest entry in this registry precisely '
                    'because it is the one that was found stale.'),
    'CORPORATE_AND_PARTNERSHIP': (2026, 'Income Tax Act Cap.332 First Schedule para 3, s.4(8), '
                                  'ss.48-51',
                                  'Corporate/partnership tax source pass (2026-09-01) read every '
                                  'Finance Act 2019-2026 for para 3 and ss.48-51 individually; '
                                  'this session\'s freshness audit additionally confirmed FA2026 '
                                  's.27(a) does not touch para 3 (only paras 2 and 4) by reading '
                                  'the full text, not inferring it from the paragraph-2 changes.'),
}
# Groups whose FINANCE_ACT_VERIFIED_THROUGH entry is None -- listed explicitly so this status
# is visible without scanning the dict above for the sentinel value.
NEVER_GROUNDED = tuple(g for g, (year, *_rest) in FINANCE_ACT_VERIFIED_THROUGH.items()
                       if year is None)

# SDL — Skills Development Levy (collected by TRA)
SDL_RATE = Decimal("0.035")           # sdl_rate / sdl_rate_2025 : 3.5% of gross cash emoluments
SDL_MIN_EMPLOYEES = 10                # sdl_threshold / sdl_employee_threshold : 10+ employees

# NSSF — National Social Security Fund
NSSF_TOTAL_RATE = Decimal("0.20")     # nssf_total_rate : 20% of gross wage
NSSF_EMPLOYER_RATE = Decimal("0.10")  # nssf_employer_rate : standard 10% employer
NSSF_EMPLOYEE_RATE = Decimal("0.10")  # nssf_total_rate : standard 10% employee
# NSSF_split_triggers documents non-standard splits (15/5, 20/0); total is ALWAYS 20%.

# WCF — Workers Compensation Fund
WCF_RATE = Decimal("0.005")           # wcf_rate_0_5_percent_confirmed : 0.5% of gross cash emoluments
WCF_MIN_EMPLOYEES = 1                 # wcf_threshold_no_minimum : from the first employee, no threshold

# PAYE — Pay As You Earn (employment income tax)
PAYE_NONRESIDENT_RATE = Decimal("0.15")  # paye_nonresident_flat_rate : flat 15%, final withholding
# paye_bands_monthly_2025_26 / paye_all_bands_sequence.
# Each tuple: (lower_bound_exclusive, marginal_rate, cumulative_tax_at_lower_bound).
# NOTE: Tanzania has NO personal relief deduction (paye_personal_relief) — the 0%
# band IS the tax-free amount.
PAYE_BANDS = [
    (Decimal("0"),        Decimal("0.00"), Decimal("0")),
    (Decimal("270000"),   Decimal("0.08"), Decimal("0")),
    (Decimal("520000"),   Decimal("0.20"), Decimal("20000")),
    (Decimal("760000"),   Decimal("0.25"), Decimal("68000")),
    (Decimal("1000000"),  Decimal("0.30"), Decimal("128000")),
]

# === PRESUMPTIVE INCOME TAX — individuals, annual TURNOVER (not profit, not monthly) ===
#
# SOURCE, AND READ THIS BEFORE CHANGING ANY FIGURE BELOW:
#   Income Tax Act Cap 332, First Schedule para 2(3), AS SUBSTITUTED BY
#   THE FINANCE ACT, 2022 (Act No. 5 of 2022) s.72(a)(ii), in force 1 July 2022,
#   AS FURTHER AMENDED BY THE FINANCE ACT, 2026, s.27(a), in force 1 July 2026.
#
# THE CONSOLIDATED STATUTE IS STALE AND WOULD HAVE GIVEN THE WRONG NUMBERS.
# Cap 332 R.E. 2019 (tra.go.tz/images/uploads/acts/CAP_332_THE_INCOME_TAX_ACT_1.pdf) still
# prints the PRE-2022 table with FIVE bands — an 11,000,001–14,000,000 band at TZS 450,000 /
# 230,000+3%, and a 14,000,001–100,000,000 band at 450,000 + 3.5% OF THE EXCESS. Encoding the
# revised edition, which is the natural thing to reach for, would have produced a wrong figure
# for every turnover above 11M. FA2022 replaced both with a single flat 3.5% OF TURNOVER.
#
# ⛔ PROVEN STALE 2026-09-01, FOUND WHILE VERIFYING AN UNRELATED PAYE FACT, NOT BY DESIGN.
# This engine was built 2026-08-16 on "every Finance Act 2020-2025 read directly" — a comment
# that was true when written but became a silent trap the moment Finance Act 2026 (enacted 30
# June 2026, in force 1 July 2026 — BEFORE this engine's own 2026-08-16 build date) touched this
# same paragraph and nobody re-checked. The build-time verification checked a FIXED historical
# year range instead of "every Finance Act gazetted as of today", so a Finance Act that already
# existed at build time was never read. Root-cause and the general lesson for every other
# constant in this file: PROGRESS.md, "PRESUMPTIVE ENGINE STALE-CONSTANT INCIDENT", 2026-09-01.
#
# FA2026 s.27(a), read verbatim in full (not just the first change found) precisely because a
# ceiling change + a rate change + a new exemption arriving in one amendment is where a fourth
# change hides -- checked, and there IS a fourth: s.27(c) touches paragraph 4 (withholding
# rates), unrelated to this engine, not actioned here.
#   (i)   para 2(2): ceiling "100,000,000" -> "200,000,000".
#   (ii)  para 2(3): the table's top band -- "11,000,001 but does not exceed 200,000,000" (was
#         "...100,000,000") -- rate "4.0% of turnover" (was 3.5%). The 4M-7M and 7M-11M bands
#         are UNCHANGED, confirmed by direct comparison, not assumed: same fixed/marginal specs,
#         same boundaries. The RECORDS-KEPT axis (s.43 TAA compliance) therefore still only
#         matters in the SAME 4,000,001-11,000,000 window it always did -- FA2026 did not move
#         it, because it did not touch the two bands where it applies.
#   (iii) para 2(3), NEW row 2, inserted BEFORE the renumbered rows 3-5 (which keep their
#         original 4M-7M/7M-11M/11M+ turnover ranges despite the row-number shift): an
#         individual's turnover 4,000,001-200,000,000 is NIL for the first 12 months from the
#         date they obtained a TIN "for purposes of commencing a business" -- IF granted.
#   (iv)  NEW para 2(4): this exemption is NOT automatic. The individual must APPLY to the
#         Commissioner, who GRANTS it only "where he is satisfied that the applicant fulfils
#         the specified conditions". An unstated TIN date is therefore not the only missing
#         fact -- an unstated application/grant status is a SECOND, independent unknown, and
#         both must be treated as never-guess (see compute_presumptive's new_business handling).
#   (v)   para 2(5) Class A (transport schedule, not implemented by this engine): "including
#         three wheelers" added to item 1 -- noted, not actioned, out of this engine's scope.
#
# Each band: (upper_inclusive, no_records_spec, records_spec). A spec is one of
#   ("nil",)                          -> zero
#   ("fixed", amount)                 -> a flat shilling figure
#   ("marginal", base, rate, from_)   -> base + rate x (turnover - from_)
#   ("flat_on_turnover", rate)        -> rate x FULL turnover (NOT the excess)
# "records" = compliance with section 35 of the Tax Administration Act (the statute's own
# wording, unchanged by FA2026's amended table which still prints "SECTION 43", confirming the
# renumbering already tracked here). NOTE the renumbering trap: in Cap 438 R.E. 2023 that
# provision is now section 43, "Maintenance of documents" — the First Schedule still cites the
# old number. User-facing copy must therefore describe the DUTY, never the section number.
PRESUMPTIVE_TURNOVER_CEILING = Decimal("200000000")   # para 2(2): 200M, WEF 2026-07-01 (was 100M)
PRESUMPTIVE_BANDS = [
    (Decimal("4000000"),   ("nil",),                  ("nil",)),
    (Decimal("7000000"),   ("fixed", Decimal("100000")),
                           ("marginal", Decimal("0"), Decimal("0.03"), Decimal("4000000"))),
    (Decimal("11000000"),  ("fixed", Decimal("250000")),
                           ("marginal", Decimal("90000"), Decimal("0.03"), Decimal("7000000"))),
    (PRESUMPTIVE_TURNOVER_CEILING, ("flat_on_turnover", Decimal("0.04")),
                                   ("flat_on_turnover", Decimal("0.04"))),
]
# para 2(1)(a) as amended by FA2022 s.72(a)(i): the business income must be
# "not including income derived by independent professionals and providers of, technical,
# management, construction and training services". TRA's own 2025/26 summary paraphrases this
# more narrowly as "professional services, construction industry and trainers" — the STATUTE
# governs, and it is the wider of the two. Confirmed UNCHANGED by FA2026 -- s.27(a) does not
# touch subparagraph (1) at all (verified against the full verbatim text, not assumed from the
# ceiling/table changes alone).
PRESUMPTIVE_EXCLUDED_SERVICES = (
    "independent professional", "technical service", "management service",
    "construction service", "training service",
)

# para 2(3) new row 2 + para 2(4), Finance Act 2026 s.27(a)(ii)-(iii): a new individual business
# turnover exemption, NOT self-executing -- see the module-level note above for the two
# independent unknowns (TIN-date, application/grant status) that make this a never-guess field,
# never a default.
PRESUMPTIVE_NEW_BUSINESS_EXEMPT_UPPER = PRESUMPTIVE_TURNOVER_CEILING   # 200M, same ceiling
PRESUMPTIVE_NEW_BUSINESS_EXEMPT_MONTHS = 12

# === CORPORATE / PARTNERSHIP INCOME TAX ===
#
# SOURCE (corporate/partnership tax source pass, 2026-09-01):
#   Income Tax Act Cap 332, First Schedule para 3 (rates); s.4(8) (AMT exemptions);
#   Subdivision A "Partnerships", ss.48-51 (transparency).
# R.E.2019 baseline read in full; every Finance Act 2020-2026 checked individually against it.
# Scoping note, preserved because a wrong instruction was caught here rather than assumed
# correct: corporate RATES live in the FIRST Schedule, not the Third (which is capital
# allowances/depreciation — a different topic). s.4(3)(a) cross-references "paragraph 1, 3(1)
# or 3(3) of the First Schedule" explicitly.
#
# corporate_tax_rate : 30% standard (First Schedule para 3(1)) — unchanged 2019-2026.
CORPORATE_STANDARD_RATE = Decimal("0.30")

# corporate_tax_rate : 25% for a company newly listed on the DSE (para 3(2)(a)), for THREE
# CONSECUTIVE YEARS from the listing date. The rate itself has never changed.
CORPORATE_DSE_RATE = Decimal("0.25")
CORPORATE_DSE_RATE_YEARS = 3

# dse_25_rate_three_years_only / corporate_tax_rate : the PUBLIC-FLOAT condition attached to
# para 3(2)(a) — a DIFFERENT number from the rate above, and the one that actually changed.
# Finance Act 2025 s.60(d)(i), quoted verbatim: "deleting the words 'thirty percent' appearing
# in subparagraph (2)(a) and substituting for them the words 'twenty five percent'", effective
# 1 July 2025. Before that date the float threshold was 30%; the coincidence that it now equals
# the RATE (25%) is exactly the trap a corpus sweep found live (2026-09-01, v6 quarantine) —
# never state these as the same number by construction, only as two numbers that currently
# happen to match.
CORPORATE_DSE_PUBLIC_FLOAT_CURRENT = Decimal("0.25")     # WEF 2025-07-01
CORPORATE_DSE_PUBLIC_FLOAT_BEFORE = Decimal("0.30")      # before 2025-07-01
CORPORATE_DSE_PUBLIC_FLOAT_CHANGE_DATE = "2025-07-01"

# minimum_turnover_tax : Alternative Minimum Tax on a corporation with THREE CONSECUTIVE YEARS
# of perpetual unrelieved tax loss (First Schedule para 3(3)). 1% of the turnover of the third
# such year, raised from 0.5% by Finance Act 2025 s.60(d)(ii), effective 1 July 2025.
AMT_RATE = Decimal("0.01")                                # WEF 2025-07-01
AMT_LOSS_YEARS_REQUIRED = 3

# s.4(8), as amended by Finance Act 2024 s.34: sectors EXEMPT from the AMT above regardless of
# loss history. Agriculture/health/education have no sunset; tea processing is time-limited —
# the proviso states the window explicitly, it is not an inference from "recently added".
AMT_EXEMPT_SECTORS_PERMANENT = ("agriculture", "health", "education")
AMT_EXEMPT_SECTOR_TEA_PROCESSING = "tea_processing"
AMT_EXEMPT_TEA_PROCESSING_FROM = "2024-07-01"
AMT_EXEMPT_TEA_PROCESSING_TO = "2027-06-30"

# ss.48-51: a partnership is NOT itself liable for income tax (s.48(1), explicit) — partnership
# income/loss is allocated to and taxed on each PARTNER individually (s.49-50), at whatever
# rate applies to THAT partner (individual bands, presumptive, or corporate — depends who the
# partner is). Confirmed unchanged against every Finance Act 2020-2026 read for this pass — a
# targeted grep for "section 48" inside each Act's OWN Income Tax Act amendment block (not the
# table-of-contents listing, which repeats every Act name including unrelated ones — FA2022's
# TOC "PART XVIII" entry is not where its amendments live, its real heading is ~1300 lines
# later, and a bare "section 48" grep without that distinction found a Copyright Act amendment
# instead, a renumbering-adjacent trap of its own kind).
PARTNERSHIP_IS_TRANSPARENT = True
