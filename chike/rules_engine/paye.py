"""PAYE — employment income tax. Progressive monthly bands (resident) or flat 15% (non-resident).

PAYE is inherently PER EMPLOYEE — the bands are progressive on an individual salary,
so it cannot be computed on an aggregate payroll the way SDL/NSSF/WCF can.
"""

from decimal import Decimal

from .rates import PAYE_BANDS, PAYE_NONRESIDENT_RATE
from .results import ComputationResult, to_shillings, tzs


def compute_paye_each(salaries, resident: bool = True) -> ComputationResult:
    """PAYE for each of several INDIVIDUALS, answered separately (PREREQ-2, eval_399).

    "Watu wawili: mmoja anapata TZS 400,000 na mwingine TZS 1,200,000 — PAYE ya KILA MMOJA?"
    is not a group-payroll question. Because the bands are progressive, summing the two
    salaries is not a different presentation of the same answer — it is arithmetically wrong:
    one salary of 1,600,000 yields TZS 308,000, while the true answer is 10,400 + 188,000 =
    TZS 198,400. So this enumerates per-person results instead of aggregating.

    `amount` is the TOTAL PAYE across the individuals (what the employer remits); each
    person's figure is spelled out in `working`, which is what the user asked for.
    """
    results = [compute_paye(s, resident=resident) for s in salaries]
    total = sum(r.amount for r in results)
    lines = [f"Mfanyakazi {i}: {r.working}" for i, r in enumerate(results, start=1)]
    return ComputationResult(
        computation="paye",
        applicable=True,
        amount=total,
        working=" ".join(lines) + f" Jumla ya PAYE = {tzs(total)}.",
        inputs={"salaries": [Decimal(s) for s in salaries], "resident": resident},
        note="per-individual PAYE (progressive bands are not additive across people)",
    )


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
