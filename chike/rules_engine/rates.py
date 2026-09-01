"""Rates and thresholds — copied verbatim from the v15 fact database.

EVERY constant here cites the source key in scripts/locked_facts.json. These are
NOT independent values: if a rate changes, it must change in the fact DB AND here
in the same commit (dual-file-sync rule, CLAUDE.md). The rules engine is only
"deterministic and correct" insofar as these match the human-verified facts.

Money is Decimal throughout — never float — because a rounding error on a
compliance figure is a wrong answer, not a cosmetic bug.
"""

from decimal import Decimal

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
#   THE FINANCE ACT, 2022 (Act No. 5 of 2022) s.72(a)(ii), in force 1 July 2022.
#
# THE CONSOLIDATED STATUTE IS STALE AND WOULD HAVE GIVEN THE WRONG NUMBERS.
# Cap 332 R.E. 2019 (tra.go.tz/images/uploads/acts/CAP_332_THE_INCOME_TAX_ACT_1.pdf) still
# prints the PRE-2022 table with FIVE bands — an 11,000,001–14,000,000 band at TZS 450,000 /
# 230,000+3%, and a 14,000,001–100,000,000 band at 450,000 + 3.5% OF THE EXCESS. Encoding the
# revised edition, which is the natural thing to reach for, would have produced a wrong figure
# for every turnover above 11M. FA2022 replaced both with a single flat 3.5% OF TURNOVER.
# Every Finance Act from 2020 to 2025 was read directly: only FA2022 touches para 2(3).
#
# Each band: (upper_inclusive, no_records_spec, records_spec). A spec is one of
#   ("nil",)                          -> zero
#   ("fixed", amount)                 -> a flat shilling figure
#   ("marginal", base, rate, from_)   -> base + rate x (turnover - from_)
#   ("flat_on_turnover", rate)        -> rate x FULL turnover (NOT the excess)
# "records" = compliance with section 35 of the Tax Administration Act (the statute's own
# wording). NOTE the renumbering trap: in Cap 438 R.E. 2023 that provision is now section 43,
# "Maintenance of documents" — the First Schedule still cites the old number. User-facing copy
# must therefore describe the DUTY, never the section number.
PRESUMPTIVE_TURNOVER_CEILING = Decimal("100000000")   # para 2(2): the 100M threshold
PRESUMPTIVE_BANDS = [
    (Decimal("4000000"),   ("nil",),                  ("nil",)),
    (Decimal("7000000"),   ("fixed", Decimal("100000")),
                           ("marginal", Decimal("0"), Decimal("0.03"), Decimal("4000000"))),
    (Decimal("11000000"),  ("fixed", Decimal("250000")),
                           ("marginal", Decimal("90000"), Decimal("0.03"), Decimal("7000000"))),
    (PRESUMPTIVE_TURNOVER_CEILING, ("flat_on_turnover", Decimal("0.035")),
                                   ("flat_on_turnover", Decimal("0.035"))),
]
# para 2(1)(a) as amended by FA2022 s.72(a)(i): the business income must be
# "not including income derived by independent professionals and providers of, technical,
# management, construction and training services". TRA's own 2025/26 summary paraphrases this
# more narrowly as "professional services, construction industry and trainers" — the STATUTE
# governs, and it is the wider of the two.
PRESUMPTIVE_EXCLUDED_SERVICES = (
    "independent professional", "technical service", "management service",
    "construction service", "training service",
)

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
