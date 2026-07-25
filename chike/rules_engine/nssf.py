"""NSSF — National Social Security Fund. 20% of gross wage (10% employer + 10% employee)."""

from decimal import Decimal

from .rates import NSSF_EMPLOYER_RATE, NSSF_EMPLOYEE_RATE
from .results import ComputationResult, to_shillings, tzs


def compute_nssf(
    gross_monthly_payroll,
    party="total",
    employer_rate=NSSF_EMPLOYER_RATE,
    employee_rate=NSSF_EMPLOYEE_RATE,
) -> ComputationResult:
    """NSSF total = 20% of gross wage, on the WHOLE payroll (not one employee).

    Splits default to 10%/10%; other valid splits (15/5, 20/0) keep the 20% total.
    For an N-employee payroll pass the summed gross so the total scales correctly —
    this is exactly the 120,000-vs-1,440,000 bug the fact rewrite targeted.

    `party` selects which figure is the HEADLINE (D-NSSF-1): 'employee' and 'employer'
    each return that party's 10% share; 'total' returns the 20% both-parties figure.
    Before the fix the engine ALWAYS returned `total`, so a question asking "how much is
    deducted from the EMPLOYEE's salary" (correct = the 10% half) got the 20% total —
    double the right figure, masked by number-overlap scorer leniency. The full 10/10
    breakdown is kept in `working` for transparency regardless of party. `party='total'`
    is the default and its `working` string is byte-identical to the pre-fix output, so
    total-framed questions are unchanged; the caller (orchestrator) resolves party from
    the question via routing.nssf_party."""
    gross = Decimal(gross_monthly_payroll)
    total = to_shillings(gross * (employer_rate + employee_rate))
    employer = to_shillings(gross * employer_rate)
    employee = to_shillings(gross * employee_rate)
    breakdown = f"(mwajiri {tzs(employer)} + mfanyakazi {tzs(employee)})"

    if party == "employee":
        amount = employee
        pct = int(employee_rate * 100)
        working = (f"NSSF (sehemu ya mfanyakazi) = {pct}% × {tzs(gross)} = {tzs(employee)} "
                   f"— jumla ya NSSF ni 20% {breakdown}")
    elif party == "employer":
        amount = employer
        pct = int(employer_rate * 100)
        working = (f"NSSF (sehemu ya mwajiri) = {pct}% × {tzs(gross)} = {tzs(employer)} "
                   f"— jumla ya NSSF ni 20% {breakdown}")
    else:  # 'total' (default) — unchanged, byte-identical to the pre-fix string
        amount = total
        working = f"NSSF = 20% × {tzs(gross)} = {tzs(total)} {breakdown}"

    return ComputationResult(
        computation="nssf",
        applicable=True,
        amount=amount,
        working=working,
        inputs={
            "gross_monthly_payroll": gross,
            "party": party,
            "employer_rate": employer_rate,
            "employee_rate": employee_rate,
        },
        note=f"party={party}",
    )


def nssf_applies() -> ComputationResult:
    """Applicability-only answer: NSSF has NO headcount threshold — it applies to every
    employer from the first employee, so the yes/no needs neither salary nor count
    (Finding 1). amount stays None; `working` is the verdict in Swahili."""
    return ComputationResult(
        computation="nssf",
        applicable=True,
        amount=None,
        working=(
            "Ndiyo. NSSF haina kizingiti cha idadi ya wafanyakazi — inahusu mwajiri "
            "kutoka mfanyakazi wa kwanza. NSSF ni asilimia 20 ya mshahara ghafi "
            "(10% mwajiri + 10% mfanyakazi)."
        ),
        inputs={},
        note="NSSF applies from first employee, no headcount threshold",
    )
