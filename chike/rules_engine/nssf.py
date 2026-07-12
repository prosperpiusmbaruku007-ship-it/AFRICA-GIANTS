"""NSSF — National Social Security Fund. 20% of gross wage (10% employer + 10% employee)."""

from decimal import Decimal

from .rates import NSSF_EMPLOYER_RATE, NSSF_EMPLOYEE_RATE
from .results import ComputationResult, to_shillings, tzs


def compute_nssf(
    gross_monthly_payroll,
    employer_rate=NSSF_EMPLOYER_RATE,
    employee_rate=NSSF_EMPLOYEE_RATE,
) -> ComputationResult:
    """NSSF total = 20% of gross wage, on the WHOLE payroll (not one employee).

    Splits default to 10%/10%; other valid splits (15/5, 20/0) keep the 20% total.
    For an N-employee payroll pass the summed gross so the total scales correctly —
    this is exactly the 120,000-vs-1,440,000 bug the fact rewrite targeted.
    """
    gross = Decimal(gross_monthly_payroll)
    total = to_shillings(gross * (employer_rate + employee_rate))
    employer = to_shillings(gross * employer_rate)
    employee = to_shillings(gross * employee_rate)

    return ComputationResult(
        computation="nssf",
        applicable=True,
        amount=total,
        working=(
            f"NSSF = 20% × {tzs(gross)} = {tzs(total)} "
            f"(mwajiri {tzs(employer)} + mfanyakazi {tzs(employee)})"
        ),
        inputs={
            "gross_monthly_payroll": gross,
            "employer_rate": employer_rate,
            "employee_rate": employee_rate,
        },
        note="total across all employees",
    )
