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

EFD HAS NO THRESHOLD AT ALL, AND THIS IS A CORRECTION, NOT THE ORIGINAL DESIGN (2026-08-29).
`EFD_ANNUAL = Decimal(11_000_000)` used to sit here, tested the same way as the VAT limbs above,
and it was fabricated: re-verifying the locked fact behind it against Tax Administration Act
Cap.438 s.44 ("Issuance of Fiscal Receipt", renumbered from s.36 by Finance Act 2023 s.54) found
NO turnover figure anywhere in the Act. Fiscal-receipt issuance is the DEFAULT for every supplier
of goods or services; the only exemption is a Commissioner-General public notice naming a
specific person or class (s.44(2)) -- something this engine has no digitized list to check a
turnover figure against. TZS 11,000,000 and TZS 14,000,000, both at various points treated as
"the EFD threshold" in this project, are actually adjacent band edges of the Income Tax Act's
UNRELATED presumptive-income-tax table (First Schedule para.2(3)).

So `efd_required` no longer takes or tests a turnover figure — there is nothing to compare it
against, and a function that keeps the comparison shape because the shape wants one is exactly
how a fabricated constant survives a fact correction: the number gets removed but the branch
stays, waiting to be re-filled with the next available number. `vat_registered` is kept as an
explicit ground because it is a real rule and a common way this question is asked, not because
it changes the verdict — every caller gets "required by default," and the wording, not the
outcome, is what differs.
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
# NO EFD constant here. efd_threshold_tzs_11m was corrected 2026-08-29: TAA Cap.438 s.44 sets no
# turnover figure at all, so there is nothing to lock. See efd_required()'s docstring.

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


def efd_required(vat_registered: bool = False) -> ComputationResult:
    """Does this business need an EFD machine?

    NO TURNOVER FIGURE IS ACCEPTED OR CONSULTED. TAA Cap.438 s.44 makes fiscal-receipt issuance
    the DEFAULT for every person who supplies goods or renders services -- there is no turnover
    threshold in the Act to compare against, at any level. The only exemption is a Commissioner-
    General public notice naming a specific person or class (s.44(2)); this engine has no
    digitized list of such notices, so it can never evaluate a trader's exemption status and
    must never return "no" from a number. The correct verdict is therefore the SAME for a trader
    at TZS 5,000,000 and one at TZS 50,000,000: required by default, exemption only by named CG
    notice, confirm with TRA.

    `vat_registered` is kept because it is a real rule and the single most common way this
    question is asked -- but it no longer changes the OUTCOME (`applicable` is always True),
    only the WORDING. There is exactly one ground now, not two: the default requirement.
    """
    if vat_registered:
        working = (
            "Ndiyo, unatakiwa kuwa na mashine ya EFD. Biashara iliyosajiliwa VAT inatakiwa "
            "kutumia EFD -- na hii ni sehemu ya wajibu mpana zaidi: EFD inahitajika kwa kila "
            "mfanyabiashara anayeuza bidhaa au huduma, bila kujali mauzo. Msamaha unatolewa TU "
            "na TRA kupitia taarifa rasmi (kwa jina lako au kundi lako maalum). " + _CONFIRM)
        ground = "vat_registered_and_default"
    else:
        working = (
            "Ndiyo, unatakiwa kuwa na mashine ya EFD kwa default, bila kujali kiasi cha mauzo "
            "yako -- hakuna kizingiti cha mauzo kwa EFD. Msamaha unatolewa TU na TRA kupitia "
            "taarifa rasmi (Commissioner-General public notice) inayotaja jina lako au kundi "
            "lako maalum. Thibitisha na TRA kama taarifa kama hiyo inakuhusu. " + _CONFIRM)
        ground = "default_requirement"

    return ComputationResult(
        computation=COMPUTATION_EFD, applicable=True, amount=None, working=working,
        inputs={"vat_registered": vat_registered, "ground": ground},
        note="EFD required by default for everyone; turnover is never consulted because no "
             "turnover threshold exists in the Act (TAA Cap.438 s.44). Exemption is only by "
             "Commissioner-General public notice naming a class, which this engine cannot "
             "evaluate from a turnover figure.",
    )
