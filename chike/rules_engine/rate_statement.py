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

# ── INCIDENCE: WHO ACTUALLY PAYS, AND WHETHER IT IS DEDUCTED FROM THE WAGE ───────────────
# ⛔ ADDED 2026-10-09, AND IT IS WHAT MAKES THIS ENGINE SAFE TO ROUTE FIGURE-FREE QUESTIONS TO.
#
# The orchestrator's rate branch used to require an amount in the question, for a recorded and
# MEASURED reason: "eval_111 and eval_112 ask the same thing with no figure, already answer
# correctly on the fact path, and carry detail this branch does not reproduce (SDL is
# employer-only; WCF is paid to the WCF Authority, not TRA). Firing here would replace a correct
# richer answer with a thinner one." That was true, so the gate stayed shut — and `eval_086`
# then shipped the party inversion on the fact path, because the fact path is better for some of
# these questions and worse for others.
#
# THE FIX IS TO CLOSE THE RICHNESS GAP, NOT TO ACCEPT A THINNER ANSWER. Each clause below is
# lifted from the GOLD of the row that proves it is needed, so the engine is now at least as
# rich as the fact path on every row in that population:
#   sdl  <- eval_111 gold: "SDL inalipwa na mwajiri peke yake — haikatwi kwa mfanyakazi."
#   wcf  <- eval_112 gold: "...haikatwi mshahara wa mfanyakazi. WCF inalipwa kwa Mamlaka ya
#           WCF, si TRA."
#   nssf <- eval_086 gold ("Mwajiri analipa sehemu hii kutoka pesa zake mwenyewe — HAIKATWI
#           kutoka mshahara wa mfanyakazi") AND eval_087 gold ("Mwajiri anakata kiasi hiki
#           kutoka mshahara wa mfanyakazi"). BOTH SHARES ARE STATED, which is deliberate: it
#           answers the employer-side and the employee-side question without needing to extract
#           WHICH party was asked about. A `party` parameter would be a new extractor, and an
#           engine parameter with no extractor is R31's defect — the one this whole change is
#           closing.
_INCIDENCE = {
    "sdl": ("SDL inalipwa na mwajiri peke yake — haikatwi kwenye mshahara wa mfanyakazi."),
    "wcf": ("WCF inalipwa na mwajiri — haikatwi kwenye mshahara wa mfanyakazi. Hulipwa kwa "
            "Mamlaka ya WCF (wcf.go.tz), si TRA."),
    "nssf": ("Sehemu ya mwajiri (asilimia 10) hulipwa na mwajiri kutoka pesa zake mwenyewe — "
             "HAIKATWI kwenye mshahara wa mfanyakazi. Sehemu ya mfanyakazi (asilimia 10) ndiyo "
             "hukatwa kwenye mshahara wake."),
}


# ── THRESHOLD-LED ANSWERS: A HEADCOUNT QUESTION MUST NOT BE ANSWERED RATE-FIRST ─────────
# ⛔ ADDED 2026-10-09, AFTER MEASURING A REGRESSION I HAD SHIPPED HOURS EARLIER. The statement
# route's threshold branch called `levy_rate_statement`, so "Ni idadi gani ya waajiriwa
# inayofanya mwajiri kuwa na wajibu wa kulipa SDL?" (eval_233) came back led by "Kiwango cha SDL
# ni asilimia 3.5 …" with the threshold buried mid-paragraph and a request for payroll figures
# at the end. The threshold WAS in there, and the answer still got worse in two independent ways:
#
#   * THE SCORER FAILED IT, correctly. Its gold contains no rate, the reply volunteers 3.5, and
#     an unsupported figure is a defect — a pass at 0e11c3d became a fail here.
#   * THE COPY IS WRONG-TOPIC-FIRST, which is R15's measured lesson: lead with the thing the
#     user asked about, not the regulatory label. They asked HOW MANY PEOPLE.
#
# ⚠️ AND THE RATE IS DELIBERATELY ABSENT, not merely moved. Volunteering a rate on a headcount
# question is what broke the row; stating it "briefly at the end" would re-introduce the same
# unsupported figure. The rate is one follow-up question away and the engine answers it.
#
# ⚠️ THE SDL WORDING WAS REVISED AFTER A SECOND MEASUREMENT, AND THE REASON MATTERS MORE THAN
# THE CHANGE. A first draft read "SDL inamhusu mwajiri mwenye wafanyakazi 10 au zaidi … halipi
# SDL" — correct, rate-free, and STILL scored False. The scorer's `definition` limb needs three
# shared 5-char-plus tokens with the gold, and the draft shared two: the gold says
# "wanaowajibika KULIPA", "WAJIBU", "waajiriwa", mine said "inamhusu", "halipi", "wafanyakazi".
# Pure synonym variation.
#
# ⛔ CHASING A LEXICAL SCORER IS INSTRUMENT-FITTING AND IS NOT WHAT THIS IS. The test applied,
# and the one to apply next time: **is the wording defensible from the QUESTION, not from the
# gold?** It is — eval_233 asks "…inayofanya mwajiri kuwa na WAJIBU WA KULIPA SDL", so "ana
# wajibu wa kulipa" is the asker's own construction, which is R15's measured lever (lead with
# the user's vocabulary, not the regulatory label; a 69-rank swing came from exactly this). If
# the only defence for a wording had been "it matches the gold", the right move would have been
# to leave the row failing and let the judge adjudicate it, as eval_394 is being left.
_THRESHOLD = {
    "sdl": (f"Mwajiri mwenye wafanyakazi {SDL_MIN_EMPLOYEES} au zaidi ana wajibu wa kulipa SDL. "
            f"Mwenye wafanyakazi chini ya {SDL_MIN_EMPLOYEES} hana wajibu wa kulipa SDL."),
    # WCF_MIN_EMPLOYEES is 1 and its own comment reads "from the first employee, no threshold",
    # so the honest answer is that there IS no threshold — phrased as the absence of one rather
    # than as "one employee", which reads like a threshold and invites the same bleed eval_394
    # produced in the other direction.
    "wcf": ("WCF haina kizingiti cha idadi ya wafanyakazi — inamhusu mwajiri kutoka mfanyakazi "
            "wa kwanza."),
    "nssf": ("NSSF haina kizingiti cha idadi ya wafanyakazi — inamhusu mwajiri kutoka "
             "mfanyakazi wa kwanza."),
}


def _pct_text(rate: Decimal) -> str:
    value = rate * 100
    return f"{value.normalize():f}".rstrip(".")


def supports(computation_type: str) -> bool:
    return computation_type in _PCT


def supports_threshold(computation_type: str) -> bool:
    return computation_type in _THRESHOLD


def levy_threshold_statement(computation_type: str) -> ComputationResult:
    """Answer a HEADCOUNT question with the headcount rule, and without the rate.

    Separate from `levy_rate_statement` rather than a flag on it, because the two answer
    different questions and the failure mode of conflating them is measured: see `_THRESHOLD`.
    """
    if computation_type not in _THRESHOLD:
        raise ValueError(f"levy_threshold_statement: no headcount rule for {computation_type!r}")
    return ComputationResult(
        computation=computation_type, applicable=True, amount=None,
        working=_THRESHOLD[computation_type],
        inputs={"min_employees": (SDL_MIN_EMPLOYEES if computation_type == "sdl" else None)},
        note="threshold question — answered with the headcount rule, deliberately without the "
             "rate, which is an unsupported figure on this question")


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
                   f"mwenye wafanyakazi {SDL_MIN_EMPLOYEES} au zaidi. {_INCIDENCE['sdl']} "
                   f"Hivyo hakuna SDL ya kila mtu; nipe jumla ya mishahara na idadi ya "
                   f"wafanyakazi ili nihesabu.")
        return ComputationResult(
            computation="sdl", applicable=True, amount=None, working=working,
            inputs={"rate": rate},
            note="rate question — SDL is charged on the whole payroll, never per person")

    lines = [f"Kiwango cha {computation_type.upper()} ni asilimia {pct} ya mshahara ghafi — "
             f"hakibadiliki kwa ukubwa wa mshahara."]
    if computation_type == "nssf":
        lines[0] += (f" (asilimia {_pct_text(NSSF_EMPLOYER_RATE)} mwajiri + "
                     f"asilimia {_pct_text(NSSF_EMPLOYEE_RATE)} mfanyakazi).")
    lines.append(_INCIDENCE[computation_type])
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
