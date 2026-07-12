"""SDL — Skills Development Levy. 3.5% of gross payroll, employers with 10+ employees."""

from decimal import Decimal

from .rates import SDL_RATE, SDL_MIN_EMPLOYEES
from .results import ComputationResult, to_shillings, tzs


def compute_sdl(gross_monthly_payroll, employee_count: int) -> ComputationResult:
    """SDL = 3.5% of total gross monthly payroll, but ONLY for 10+ employees.

    Below the threshold there is no SDL obligation — this returns applicable=False
    with an explanatory note, which is the correct answer (the illustrative
    single-employee fact example is about the rate, not a real obligation).
    """
    gross = Decimal(gross_monthly_payroll)
    inputs = {"gross_monthly_payroll": gross, "employee_count": employee_count}

    if employee_count < SDL_MIN_EMPLOYEES:
        return ComputationResult(
            computation="sdl",
            applicable=False,
            amount=None,
            working=(
                f"SDL haihusiki: una wafanyakazi {employee_count} "
                f"(chini ya {SDL_MIN_EMPLOYEES}). SDL inahusu waajiri wenye "
                f"wafanyakazi {SDL_MIN_EMPLOYEES} au zaidi."
            ),
            inputs=inputs,
            note="below SDL 10-employee threshold",
        )

    amount = to_shillings(gross * SDL_RATE)
    return ComputationResult(
        computation="sdl",
        applicable=True,
        amount=amount,
        working=f"SDL = 3.5% × {tzs(gross)} = {tzs(amount)}",
        inputs=inputs,
    )
