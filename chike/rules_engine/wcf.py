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


def wcf_applies() -> ComputationResult:
    """Applicability-only answer: WCF has NO headcount threshold — it applies to all
    employers from the first employee, so the yes/no needs neither salary nor count
    (Finding 1). amount stays None; `working` is the verdict in Swahili."""
    return ComputationResult(
        computation="wcf",
        applicable=True,
        amount=None,
        working=(
            "Ndiyo. WCF inahusu waajiri wote kutoka mfanyakazi wa kwanza — hakuna "
            "kizingiti cha idadi ya wafanyakazi. WCF ni asilimia 0.5 ya jumla ya mishahara."
        ),
        inputs={},
        note="WCF applies to all employers from first employee, no threshold",
    )
