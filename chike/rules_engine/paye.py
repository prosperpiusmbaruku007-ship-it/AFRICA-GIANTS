"""PAYE — employment income tax. Progressive monthly bands (resident) or flat 15% (non-resident).

PAYE is inherently PER EMPLOYEE — the bands are progressive on an individual salary,
so it cannot be computed on an aggregate payroll the way SDL/NSSF/WCF can.
"""

from decimal import Decimal

from .rates import PAYE_BANDS, PAYE_NONRESIDENT_RATE
from .results import ComputationResult, to_shillings, tzs


def compute_paye(monthly_salary, resident: bool = True) -> ComputationResult:
    """PAYE on one employee's monthly salary.

    Resident: progressive bands (no personal relief — the 0% band is the tax-free
    amount). Non-resident: flat 15% final withholding, NOT the progressive bands.
    """
    salary = Decimal(monthly_salary)
    inputs = {"monthly_salary": salary, "resident": resident}

    if not resident:
        amount = to_shillings(salary * PAYE_NONRESIDENT_RATE)
        return ComputationResult(
            computation="paye",
            applicable=True,
            amount=amount,
            working=(
                f"PAYE (asiye mkazi) = 15% × {tzs(salary)} = {tzs(amount)} "
                f"(kodi ya mwisho, si mabano ya kupanda)"
            ),
            inputs=inputs,
            note="non-resident flat rate, final withholding",
        )

    # Resident: pick the highest band whose lower bound the salary exceeds.
    lower, rate, base = PAYE_BANDS[0]
    for b_lower, b_rate, b_base in PAYE_BANDS:
        if salary > b_lower:
            lower, rate, base = b_lower, b_rate, b_base

    amount = to_shillings(base + rate * (salary - lower))
    if rate == 0:
        working = f"PAYE = TZS 0 (mshahara {tzs(salary)} uko ndani ya bendi ya 0%)"
    else:
        working = (
            f"PAYE = {tzs(base)} + {rate * 100:.0f}% × ({tzs(salary)} − {tzs(lower)}) "
            f"= {tzs(amount)}"
        )
    return ComputationResult(
        computation="paye",
        applicable=True,
        amount=amount,
        working=working,
        inputs=inputs,
        note="per-employee, resident progressive bands",
    )
