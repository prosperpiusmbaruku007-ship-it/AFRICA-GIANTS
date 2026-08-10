"""VAT registration and EFD — is this trader over the threshold?

WHY THIS IS A ROUTE. Same argument as minimum_wage, measured on a second levy family: SAFETY-3
found production reciting `200,000,000` correctly **in the sentence where it misapplied it**.
The threshold was never the problem; the comparison was. So the comparison leaves the model.

THE TWO VAT LIMBS ARE INDEPENDENT TESTS, AND THIS IS THE WHOLE DIFFICULTY.
Registration is compulsory on EITHER:
    limb A — turnover of TZS 200,000,000 or more in a 12-month period, OR
    limb B — turnover of TZS 100,000,000 or more in ANY rolling 6-month period.

A figure stated for one period carries NO information about the other. "TZS 150M kwa mwaka" is
below limb A and is entirely consistent with TZS 120M in one half-year, which is ABOVE limb B
and registrable. So the natural answer — "150M < 200M, hapana" — is not a conservative
approximation, it is the SAFETY-3 shape with a different number: right figure, wrong test.

BOTH BOUNDARIES ARE INCLUSIVE, and this is not a stylistic choice — it was written strict
(`>`) first and the corpus corrected it. eval_351 asks about turnover of "TZS 200,000,000
kamili" and its gold is explicit: *"Kufikia TZS 200,000,000 kwa mwaka (SIYO TU KUZIDI)
kunalazimisha usajili"* — reaching the figure, not only exceeding it, triggers registration.
The row is tagged `_why_hard: exactly at 200M — inclusive boundary`, i.e. it exists to catch
precisely this. `>=` is therefore load-bearing on both limbs and on EFD; a future edit to `>`
re-breaks a gate row that was authored to detect it.

Hence the contract, which is the founder's Option 1:
    * test the limb the stated period actually addresses;
    * when that limb does NOT establish registration, the answer CARRIES the other limb as an
      explicit conditional, because the question genuinely is not settled;
    * when it DOES establish registration, there is no conditional — one limb crossing is
      sufficient and the other is moot.

THE CONDITIONAL IS DERIVED, NEVER AUTHORED. `_LIMBS` is the data; `_untested_limb` picks the
one not addressed; the clause is emitted from that. The same rule as the minimum-wage verdict
word: a sentence that could drift out of agreement with the verdict beside it must not be
written twice. There is no code path that can emit a conditional for a limb that WAS tested,
or omit one for a limb that was not.

A MONTHLY FIGURE IS A RATE, NOT A PERIOD TOTAL — and it is never annualised here. "Milioni 25
kila mwezi" implies 300M/year only if the rate holds for twelve months, which is an assumption
about the trader's future, not an arithmetic step. Turnover is seasonal for exactly the traders
this product serves. So a monthly figure declines to a never-guess exit that states both
thresholds and asks for the actual period total. That is the same never-guess-as-infrastructure
rule C4 established: the decline is a code path, not a sentence the model is asked to obey.

EFD IS NOT A SECOND COPY OF THE SAME COMPARISON. Its threshold is annual turnover TZS 11M, but
it has an OVERRIDE that has no analogue in VAT: a VAT-registered person needs an EFD regardless
of turnover. So `efd_required` tests the override FIRST and the turnover second, and below the
threshold the derived conditional is the VAT-registration one — again from state, not authored.
"""

from decimal import Decimal

from .results import ComputationResult, tzs

COMPUTATION_VAT = "vat_registration"
COMPUTATION_EFD = "efd_requirement"

# Locked: vat_threshold_200m_july2024_increase / vat_registration_threshold_annual /
# vat_registration_threshold_six_months. Zanzibar's separate TZS 100M is a DIFFERENT
# jurisdiction and is out of corpus — never reachable from here.
VAT_ANNUAL = Decimal(200_000_000)
VAT_SIX_MONTH = Decimal(100_000_000)
# Locked: efd_threshold_tzs_11m.
EFD_ANNUAL = Decimal(11_000_000)

ANNUAL, SIX_MONTH, MONTHLY = "annual", "six_month", "monthly"

_SOURCE = "TRA (tra.go.tz)"
_CONFIRM = f"Thibitisha na {_SOURCE}."

# period -> (limb threshold, Swahili name of the period the limb tests). The ONLY place the
# two limbs are described; every verdict and every conditional reads from here.
_LIMBS = {
    ANNUAL: (VAT_ANNUAL, "miezi 12"),
    SIX_MONTH: (VAT_SIX_MONTH, "miezi 6 mfululizo"),
}


def _untested_limb(period: str) -> str:
    """The limb the stated period does NOT address. Derived, so it cannot disagree."""
    return SIX_MONTH if period == ANNUAL else ANNUAL


def _conditional_clause(period: str) -> str:
    """The other limb, stated as the open condition it actually is.

    Emitted ONLY when the tested limb did not establish registration — see vat_registration.
    Written as an explicit condition ('IKIWA ... basi ...') and never as a bare fact, because
    a reader must not be able to take it as the verdict. `reads_as_unconditional` in routing
    is asserted over this copy for exactly that reason.
    """
    other = _untested_limb(period)
    threshold, window = _LIMBS[other]
    return (f"LAKINI hili halijamalizika: usajili wa VAT ni wa lazima pia IKIWA mauzo "
            f"yamefikia {tzs(threshold)} katika {window}. Sijui mauzo yako ya {window}, "
            f"hivyo kama yamefikia kiasi hicho, unatakiwa kujisajili. Niambie mauzo ya "
            f"{window} nami nitathibitisha.")


def vat_registration(turnover, period: str) -> ComputationResult:
    """Is VAT registration compulsory, on the limb this period addresses?

    `period` must be ANNUAL or SIX_MONTH — a monthly rate does not address either limb and is
    the caller's never-guess exit, not a computation. `applicable` carries the compulsory-
    registration verdict; `amount` stays None, since nothing is owed by registering.
    """
    if period not in _LIMBS:
        raise ValueError(
            f"vat_registration: period {period!r} addresses neither statutory limb. A monthly "
            "rate is not a period total and must not be annualised — route it to the "
            "never-guess exit instead.")
    turnover = Decimal(turnover)
    threshold, window = _LIMBS[period]
    over = turnover >= threshold                     # the ONE place the verdict is decided
    #      ^^ INCLUSIVE — see the module docstring; eval_351 is exactly at the figure
    other = _untested_limb(period)

    if over:
        # One limb crossing is sufficient; the other limb is moot, so NO conditional.
        # 'yamefikia au kuzidi' — the wording has to hold at the boundary too, where the
        # turnover has REACHED the figure without exceeding it and registration is still due.
        working = (
            f"Ndiyo, unatakiwa kujisajili VAT. Mauzo yako ya {tzs(turnover)} kwa {window} "
            f"yamefikia au kuzidi kizingiti cha {tzs(threshold)}, hivyo usajili ni wa LAZIMA. "
            f"Hatua ya kwanza ni kuomba usajili wa VAT TRA. {_CONFIRM}")
    else:
        working = (
            f"Kwa upande wa {window}: hapana, mauzo yako ya {tzs(turnover)} hayajafikia "
            f"kizingiti cha {tzs(threshold)}. {_conditional_clause(period)} {_CONFIRM}")

    return ComputationResult(
        computation=COMPUTATION_VAT,
        applicable=over,
        amount=None,
        working=working,
        inputs={"turnover": turnover, "period": period, "threshold": threshold,
                "limb_tested": period, "limb_untested": None if over else other},
        note=("over the VAT threshold on the limb tested" if over else
              f"below the {period} limb; {other} limb untested and stated conditionally"),
    )


def efd_required(turnover=None, period: str = ANNUAL,
                 vat_registered: bool = False) -> ComputationResult:
    """Does this business need an EFD machine?

    Two independent grounds, tested in the order that lets the stronger one short-circuit:
      1. VAT-registered -> YES regardless of turnover. No threshold comparison happens at all,
         so no conditional is emitted; there is nothing left open.
      2. annual turnover above TZS 11M -> YES.
    Below the threshold and not VAT-registered the answer is no — but VAT registration would
    change it, so THAT is the derived conditional here. Same rule as the VAT limbs: the open
    condition is emitted from what was not established, not authored alongside it.
    """
    if vat_registered:
        return ComputationResult(
            computation=COMPUTATION_EFD, applicable=True, amount=None,
            working=("Ndiyo, unatakiwa kuwa na mashine ya EFD. Biashara iliyosajiliwa VAT "
                     "inatakiwa kutumia EFD bila kujali kiasi cha mauzo. " + _CONFIRM),
            inputs={"vat_registered": True, "ground": "vat_registered"},
            note="EFD required on VAT registration alone — turnover not consulted")

    if turnover is None:
        raise ValueError("efd_required: no turnover and not VAT-registered — nothing to test; "
                         "this is the caller's clarification case, not a computation")
    if period != ANNUAL:
        raise ValueError(
            f"efd_required: the EFD threshold is an ANNUAL turnover test; {period!r} does not "
            "address it and must not be annualised — route to the never-guess exit.")

    turnover = Decimal(turnover)
    over = turnover >= EFD_ANNUAL                    # the ONE place the verdict is decided
    if over:
        working = (f"Ndiyo, unatakiwa kuwa na mashine ya EFD. Mauzo yako ya mwaka ya "
                   f"{tzs(turnover)} yamefikia au kuzidi kizingiti cha {tzs(EFD_ANNUAL)}. "
                   f"{_CONFIRM}")
    else:
        working = (
            f"Kwa upande wa mauzo: hapana, mauzo yako ya mwaka ya {tzs(turnover)} hayajafikia "
            f"kizingiti cha EFD cha {tzs(EFD_ANNUAL)}, hivyo unaweza kutumia risiti za "
            f"kuandika kwa mkono. LAKINI hili halijamalizika: IKIWA umesajiliwa VAT, EFD ni "
            f"ya lazima bila kujali mauzo. Niambie kama umesajiliwa VAT nami nitathibitisha. "
            f"{_CONFIRM}")

    return ComputationResult(
        computation=COMPUTATION_EFD, applicable=over, amount=None, working=working,
        inputs={"turnover": turnover, "period": ANNUAL, "threshold": EFD_ANNUAL,
                "vat_registered": False,
                "ground": "turnover" if over else None,
                "condition_open": None if over else "vat_registration"},
        note=("annual turnover at or above the EFD threshold" if over else
              "below the EFD turnover threshold; VAT registration stated conditionally"),
    )
