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
