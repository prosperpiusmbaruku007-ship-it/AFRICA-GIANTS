"""Base rejection — the deterministic ANSWER to "compute levy L from this figure", when
the figure offered is not a payroll base at all (PREREQ-1).

WHY THIS IS AN ANSWER, NOT A CLARIFICATION
Before this module, a wrong-base question produced a clarification: the extractor correctly
marked the amount LOW with reason 'wrong_base (non-payroll figure)', and
clarification.compute_clarification() then IGNORED that reason and fell through to "give me
the salary" (or, for SDL, to "how many employees?" — the missing-count branch fires first, so
the reply never even mentioned money). Asking a user for payroll when they asked whether
their electricity bill counts validates the false premise: it implies the bill IS a base and
only the salary is missing. Naming the real base is strictly more useful AND strictly more
honest, and it is fully determined by rates.py — so it is an answer.

Consequences of the answer shape (deliberate, see PROGRESS.md PREREQ-1):
  - needs_clarification is False, so these re-enter the judged denominator. The
    judge_gradeable exclusion of clarifications is exactly what made Phase D's
    judge-augmented comparison not like-for-like.
  - the orchestrator blanks the model body and renders `working` alone, so the text a user
    sees is deterministic (same discipline as D-FIDELITY-1).

EVERY rate below comes from rates.py, which cites its locked_facts key. This module encodes
NO new regulatory fact — only the Swahili framing around facts the engine already holds.
The authority URLs are the ones the eval golds and sources/whitelist.json already use.
"""

from decimal import Decimal

from .rates import (NSSF_EMPLOYEE_RATE, NSSF_TOTAL_RATE, SDL_RATE, WCF_RATE)
from .results import ComputationResult, tzs


def _pct(rate: Decimal) -> str:
    """'0.035' -> '3.5', '0.005' -> '0.5', '0.10' -> '10' — no trailing zeros."""
    return f"{rate * 100:f}".rstrip("0").rstrip(".")


# Correct base per levy, phrased for a user. Built from rates.py so a rate change in the
# fact DB propagates here automatically (dual-file-sync rule, CLAUDE.md).
def _correct_base(computation_type: str) -> str:
    return {
        "sdl": f"asilimia {_pct(SDL_RATE)} ya jumla ya mishahara ya wafanyakazi",
        "wcf": f"asilimia {_pct(WCF_RATE)} ya jumla ya mishahara ya wafanyakazi",
        "nssf": (f"asilimia {_pct(NSSF_EMPLOYEE_RATE)} ya mshahara ghafi wa mfanyakazi "
                 f"(jumla asilimia {_pct(NSSF_TOTAL_RATE)} — mwajiri na mfanyakazi)"),
        "paye": ("kodi inayokatwa kutoka mshahara wa mfanyakazi kwa mabano "
                 "(0% hadi TZS 270,000, kisha 8%, 20%, 25%, 30%)"),
    }[computation_type]


_LEVY_NAME = {"sdl": "SDL", "nssf": "NSSF", "paye": "PAYE", "wcf": "WCF"}
_AUTHORITY = {
    "sdl": "TRA (tra.go.tz)",
    "paye": "TRA (tra.go.tz)",
    "nssf": "NSSF (nssf.go.tz)",
    "wcf": "WCF (wcf.go.tz)",
}
# What to ask for, per levy, AFTER the correction. The invitation is optional copy that
# follows a mandatory correction — never a substitute for it. Matches the eval golds, 6 of
# which invite the payroll this way ("Nipe mshahara wa mfanyakazi, siyo akiba").
_INVITE = {
    "sdl": "Nipe jumla ya mishahara ya wafanyakazi kwa mwezi na idadi yao",
    "wcf": "Nipe jumla ya mishahara ya wafanyakazi kwa mwezi",
    "nssf": "Nipe mshahara wa mwezi wa mfanyakazi",
    "paye": "Nipe mshahara wa mwezi wa mfanyakazi",
}


def reject_base(computation_type: str, stated_amount=None,
                invite: bool = True) -> ComputationResult:
    """The deterministic 'that is not the base' answer for one levy.

    `stated_amount` is the figure the user offered, echoed back so the rejection is concrete
    ("TZS 6,700,000 si mshahara"); pass None when what was offered was a COUNT of non-payroll
    objects (invoices/branches/vehicles/machines) rather than a money figure.

    Leads with 'Hapana.' because every question in this class is, in substance, "does X count
    towards L?" — and the eval golds for the yes/no members lead the same way.
    """
    name = _LEVY_NAME[computation_type]
    figure = (f"Kiasi ulichotaja ({tzs(stated_amount)}) si mshahara, hivyo hakitumiki "
              f"kukokotoa {name}."
              if stated_amount is not None else
              f"Idadi uliyotaja si kiasi cha mshahara, hivyo haitumiki kukokotoa {name}.")
    ask = f" {_INVITE[computation_type]}." if invite else ""
    return ComputationResult(
        computation=computation_type,
        applicable=False,
        amount=None,
        working=(f"Hapana. {name} inatozwa kwa {_correct_base(computation_type)}. "
                 f"{figure}{ask} Thibitisha na {_AUTHORITY[computation_type]}."),
        inputs={"stated_non_payroll_figure": stated_amount},
        note="non-payroll base offered for a payroll levy",
    )
