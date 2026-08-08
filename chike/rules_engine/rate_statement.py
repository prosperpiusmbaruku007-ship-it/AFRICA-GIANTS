"""'Kiwango cha <levy> ni asilimia ngapi?' — the RATE is the answer, not a computed amount.

eval_305 ("Kiwango cha SDL ni ngapi kwa mtu mwenye mshahara wa TZS 480,000?") was answered with
"niambie idadi ya wafanyakazi" — a question, for a levy whose rate the asker could have been
told outright. The rate does not depend on the salary; that INVARIANCE is the substance of the
answer, and every gold in this family states it before applying anything (eval_111 and eval_112
already prove the shape on the fact path).

SDL IS APPLIED TO NOTHING HERE, DELIBERATELY. It is charged on the TOTAL payroll of an employer
with 10+ staff, so "3.5% of this one person's TZS 480,000" is not a smaller version of the right
answer — it is a different and wrong one, and eval_305's gold says so explicitly ("SDL siyo
per-mtu"). NSSF and WCF are genuine per-employee percentages, so for those the figure is stated.

PAYE is absent: it is banded, not a flat rate, so "the rate" has no single value. VAT
withholding (eval_315) is absent too — it is not in rules_engine.SUPPORTED and has no constant
in rates.py, and inventing one here would breach the dual-file-sync rule with locked_facts.json.
"""

from decimal import Decimal

from .rates import (SDL_RATE, SDL_MIN_EMPLOYEES, NSSF_TOTAL_RATE,
                    NSSF_EMPLOYER_RATE, NSSF_EMPLOYEE_RATE, WCF_RATE)
from .results import ComputationResult, to_shillings, tzs

_PCT = {"sdl": SDL_RATE, "nssf": NSSF_TOTAL_RATE, "wcf": WCF_RATE}


def _pct_text(rate: Decimal) -> str:
    value = rate * 100
    return f"{value.normalize():f}".rstrip(".")


def supports(computation_type: str) -> bool:
    return computation_type in _PCT


def levy_rate_statement(computation_type: str, amount=None) -> ComputationResult:
    """State the levy's rate, its invariance to the salary, and — where the levy really is a
    per-employee percentage — what it comes to on the figure given."""
    if computation_type not in _PCT:
        raise ValueError(
            f"levy_rate_statement: {computation_type!r} has no single flat rate "
            "(PAYE is banded; VAT withholding is not a supported computation)")

    rate = _PCT[computation_type]
    pct = _pct_text(rate)

    if computation_type == "sdl":
        working = (f"Kiwango cha SDL ni asilimia {pct} — hakitegemei mshahara wa mtu mmoja. "
                   f"SDL hutozwa kwa JUMLA ya mishahara ya wafanyakazi wote, na tu kwa mwajiri "
                   f"mwenye wafanyakazi {SDL_MIN_EMPLOYEES} au zaidi. Hivyo hakuna SDL ya "
                   f"kila mtu; nipe jumla ya mishahara na idadi ya wafanyakazi ili nihesabu.")
        return ComputationResult(
            computation="sdl", applicable=True, amount=None, working=working,
            inputs={"rate": rate},
            note="rate question — SDL is charged on the whole payroll, never per person")

    lines = [f"Kiwango cha {computation_type.upper()} ni asilimia {pct} ya mshahara ghafi — "
             f"hakibadiliki kwa ukubwa wa mshahara."]
    if computation_type == "nssf":
        lines[0] += (f" (asilimia {_pct_text(NSSF_EMPLOYER_RATE)} mwajiri + "
                     f"asilimia {_pct_text(NSSF_EMPLOYEE_RATE)} mfanyakazi).")
    computed = None
    if amount is not None:
        gross = Decimal(amount)
        computed = to_shillings(gross * rate)
        lines.append(f"Kwa {tzs(gross)}, ni asilimia {pct} = {tzs(computed)} kwa mwezi.")

    return ComputationResult(
        computation=computation_type, applicable=True, amount=computed,
        working=" ".join(lines),
        inputs={"rate": rate, "gross_monthly_payroll": amount},
        note="rate question — the rate is invariant to the salary")
