"""Pattern F2 — one levy, one payroll, a headcount that differs BY NAMED MONTH.

eval_329: "Mwezi JANUARI nilikuwa na watu 9, FEBRUARI nikaongeza mmoja kufikia 10, mishahara
ni TZS 3,000,000 kila mwezi — SDL ya Januari na Februari?" The correct answer is two answers:
January is below the 10-employee threshold and owes nothing; February has crossed it and owes
3.5% of the payroll. Collapsing that into one figure is wrong whichever figure is chosen, and
the previous behaviour — a single clarification asking for "the" headcount — asked for
something the question had already given twice.

SDL ONLY, deliberately. It is the only levy whose answer depends on the headcount, so it is
the only one where splitting by period changes anything. NSSF and WCF would repeat the same
figure per month, which is noise rather than an answer, and PAYE is per-employee and banded.
Narrowest form that closes the case.
"""

from decimal import Decimal

from .rates import SDL_RATE, SDL_MIN_EMPLOYEES
from .results import ComputationResult, to_shillings, tzs

_MONTH_LABEL = {
    "januari": "Januari", "februari": "Februari", "machi": "Machi", "aprili": "Aprili",
    "mei": "Mei", "juni": "Juni", "julai": "Julai", "agosti": "Agosti",
    "septemba": "Septemba", "oktoba": "Oktoba", "novemba": "Novemba", "desemba": "Desemba",
}


def sdl_by_month(periods, gross_monthly_payroll) -> ComputationResult:
    """SDL for each (month, employee_count), sharing one monthly payroll.

    `periods` is [(month_key, count), ...] in the order the question stated them, as returned
    by swahili_numbers.parse_month_headcounts. Raises on fewer than two periods — a single
    period is the ordinary compute path and must not be routed here.
    """
    if len(periods) < 2:
        raise ValueError(
            "sdl_by_month: fewer than two periods — a single month is the ordinary SDL path, "
            "not a per-period split")

    gross = Decimal(gross_monthly_payroll)
    lines, total, any_due = [], Decimal(0), False
    for month, count in periods:
        label = _MONTH_LABEL.get(month, month.capitalize())
        if count < SDL_MIN_EMPLOYEES:
            lines.append(f"{label}: SDL ni TZS 0 — wafanyakazi {count} (chini ya "
                         f"{SDL_MIN_EMPLOYEES}), hivyo SDL haitozwi.")
            continue
        amount = to_shillings(gross * SDL_RATE)
        any_due = True
        total += amount
        lines.append(f"{label}: SDL = 3.5% × {tzs(gross)} = {tzs(amount)} "
                     f"(wafanyakazi {count}).")

    if len(periods) > 1 and any_due:
        lines.append(f"Jumla ya miezi {len(periods)}: {tzs(total)}.")

    return ComputationResult(
        computation="sdl",
        applicable=any_due,
        amount=total if any_due else Decimal(0),
        working="\n".join(lines),
        inputs={"gross_monthly_payroll": gross,
                "periods": [(m, c) for m, c in periods]},
        note=("headcount crosses the SDL threshold between the stated months — answered per "
              "month, not as one figure"),
    )
