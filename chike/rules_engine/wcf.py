"""WCF — Workers Compensation Fund. 0.5% of gross payroll, ALL employers, no threshold."""

from decimal import Decimal

from .rates import WCF_RATE
from .results import ComputationResult, to_shillings, tzs


def compute_wcf(gross_monthly_payroll) -> ComputationResult:
    """WCF = 0.5% of gross cash emoluments. Applies from the first employee (no threshold)."""
    gross = Decimal(gross_monthly_payroll)
    amount = to_shillings(gross * WCF_RATE)
    return ComputationResult(
        computation="wcf",
        applicable=True,
        amount=amount,
        working=f"WCF = 0.5% × {tzs(gross)} = {tzs(amount)}",
        inputs={"gross_monthly_payroll": gross},
        note="all employers, from first employee",
    )
