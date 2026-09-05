"""Corporate and partnership income tax — a RATE STATEMENT, like rate_statement.py, not a
turnover-to-shillings computation.

WHY THIS IS NOT A COMPUTED AMOUNT. Corporate income tax is charged on PROFIT (chargeable
income), and profit is not derivable from a turnover figure the way SDL/NSSF/WCF are derivable
from a salary. An engine that took "mauzo yangu ni milioni 50" and multiplied by 30% would be
computing a tax on the wrong base and handing the user a wrong number with the engine's
authority behind it — exactly the caution presumptive.py already codes for the schedule split,
applied here to the whole domain rather than one branch of it. So this engine states the rate
and the regime, and declines — explicitly, in the reply — to turn a turnover into a shillings
figure.

TWO SEPARATE QUESTIONS, TWO FUNCTIONS:
  - corporate_tax_rate_statement(): what rate applies to a corporation, and (only where the
    inputs support it) whether the AMT applies instead of the ordinary rate.
  - partnership_tax_statement(): a partnership is NOT itself taxed (Cap 332 s.48(1)) — this
    function's whole job is to say so and decline to name a rate, because the real rate depends
    on who the partners are, which this engine is never given.

NEVER-GUESS, IN BOTH DIRECTIONS. A DSE-listing question with no public-float figure given gets
BOTH conditions stated, not a rate asserted on an assumption. An AMT question with no loss-year
count given states the 3-consecutive-year rule and asks, rather than assuming loss-making means
AMT applies at year one.
"""

from datetime import date
from decimal import Decimal

from .rates import (
    CORPORATE_STANDARD_RATE, CORPORATE_DSE_RATE, CORPORATE_DSE_RATE_YEARS,
    CORPORATE_DSE_PUBLIC_FLOAT_CURRENT, CORPORATE_DSE_PUBLIC_FLOAT_CHANGE_DATE,
    AMT_RATE, AMT_LOSS_YEARS_REQUIRED,
    AMT_EXEMPT_SECTORS_PERMANENT, AMT_EXEMPT_SECTOR_TEA_PROCESSING,
    AMT_EXEMPT_TEA_PROCESSING_FROM, AMT_EXEMPT_TEA_PROCESSING_TO,
)
from .results import ComputationResult

_TEA_EXEMPT_FROM = date.fromisoformat(AMT_EXEMPT_TEA_PROCESSING_FROM)
_TEA_EXEMPT_TO = date.fromisoformat(AMT_EXEMPT_TEA_PROCESSING_TO)


def _pct(rate: Decimal) -> str:
    value = rate * 100
    return f"{value.normalize():f}".rstrip(".")


def corporate_tax_rate_statement(is_dse_listed=None, meets_public_float=None,
                                 loss_years=None, sector=None,
                                 today=None) -> ComputationResult:
    """State the corporate income tax rate. Never computes a TZS amount — see module docstring.

    `is_dse_listed`: True/False/None (unstated) — whether the corporation is listed on the DSE.
    `meets_public_float`: True/False/None — whether it meets the current 25% public-float
        condition (para 3(2)(a)). Only meaningful when `is_dse_listed` is True.
    `loss_years`: an int, or None — consecutive years of perpetual unrelieved tax loss, if the
        question is really about the AMT rather than the ordinary rate.
    `sector`: a free-text sector hint (e.g. "agriculture", "tea_processing"), or None.
    `today`: a `date`, or None to use the real current date — injectable so the
        time-bounded tea-processing exemption (2024-07-01..2027-06-30) is testable on both
        sides of its own boundary without mocking the clock. Never passed by production
        callers; exists for tests only.
    """
    inputs = {"is_dse_listed": is_dse_listed, "meets_public_float": meets_public_float,
              "loss_years": loss_years, "sector": sector}
    if today is None:
        today = date.today()

    # AMT branch — only entered when the question actually supplies a loss-year count. This is
    # never-guess: a corporation asking "kiwango cha kodi ya kampuni ni ngapi" with no loss
    # history mentioned gets the ordinary-rate branch below, not an AMT tangent.
    if loss_years is not None:
        exempt_permanent = sector in AMT_EXEMPT_SECTORS_PERMANENT
        # TIME-BOUNDED, checked against `today`, not just narrated in the reply text — a
        # sector match alone used to return this branch unconditionally forever, which would
        # have kept stating the tea exemption as active long after it lapses on 2027-06-30
        # (found 2026-09-05: the reply text already named the sunset date but the CODE never
        # checked it against the clock, so the exemption would have silently outlived its own
        # stated window). Outside the window, exempt_tea is False and execution falls through
        # to the ordinary AMT-applies logic below, same as any other non-exempt sector.
        exempt_tea = (sector == AMT_EXEMPT_SECTOR_TEA_PROCESSING
                      and _TEA_EXEMPT_FROM <= today <= _TEA_EXEMPT_TO)
        if exempt_permanent:
            working = (
                f"Hapana, AMT haitumiki. Kampuni zinazofanya kilimo, afya au elimu ZIMESAMEHEWA "
                f"AMT kabisa (Sheria ya Kodi ya Mapato Kifungu 4(8)), hata kama zina hasara "
                f"miaka {loss_years} mfululizo. Kodi ya kawaida ya asilimia "
                f"{_pct(CORPORATE_STANDARD_RATE)} inatumika kwa faida (si AMT).")
            return ComputationResult(
                computation="corporate_tax", applicable=True, amount=None, working=working,
                inputs=inputs, note="s.4(8) — permanent sector exemption from AMT")
        if exempt_tea:
            working = (
                f"Hapana, AMT haitumiki kwa sasa. Kampuni za usindikaji chai ZIMESAMEHEWA AMT "
                f"kwa kipindi maalum tu — {AMT_EXEMPT_TEA_PROCESSING_FROM} hadi "
                f"{AMT_EXEMPT_TEA_PROCESSING_TO} (Sheria ya Fedha 2024 Kifungu 34, ikiongeza "
                f"msamaha huu kwenye Kifungu 4(8)). Nje ya kipindi hicho, AMT ya asilimia "
                f"{_pct(AMT_RATE)} ya mauzo ya mwaka wa tatu inatumika kama kwa kampuni "
                f"nyingine yoyote yenye hasara miaka {AMT_LOSS_YEARS_REQUIRED} mfululizo.")
            return ComputationResult(
                computation="corporate_tax", applicable=True, amount=None, working=working,
                inputs=inputs,
                note="s.4(8) as amended by FA2024 s.34 — time-limited tea-processing exemption")
        if loss_years < AMT_LOSS_YEARS_REQUIRED:
            working = (
                f"Bado hapana. AMT inatumika tu baada ya miaka {AMT_LOSS_YEARS_REQUIRED} "
                f"mfululizo ya hasara isiyopunguzwa (First Schedule para 3(3)) — umetaja miaka "
                f"{loss_years}. Kodi ya kawaida ya asilimia {_pct(CORPORATE_STANDARD_RATE)} "
                f"inatumika kwa faida kwa sasa.")
            return ComputationResult(
                computation="corporate_tax", applicable=False, amount=None, working=working,
                inputs=inputs, note="First Schedule para 3(3) — loss-year count below threshold")
        working = (
            f"Ndiyo, AMT inatumika. Kampuni yenye hasara isiyopunguzwa kwa miaka "
            f"{AMT_LOSS_YEARS_REQUIRED} mfululizo hulipa AMT ya asilimia {_pct(AMT_RATE)} ya "
            f"mauzo (turnover) ya mwaka wa tatu wa hasara — SI faida, SI kodi ya kawaida ya "
            f"asilimia {_pct(CORPORATE_STANDARD_RATE)} (First Schedule para 3(3), Sheria ya "
            f"Fedha 2025 Kifungu 60(d)(ii)). Kiasi halisi kinahitaji mauzo ya mwaka huo — "
            f"thibitisha na TRA.")
        return ComputationResult(
            computation="corporate_tax", applicable=True, amount=None, working=working,
            inputs=inputs, note="First Schedule para 3(3) — AMT applies, amount needs turnover")

    # Ordinary rate branch.
    if is_dse_listed is True:
        if meets_public_float is True:
            working = (
                f"Kiwango cha kodi ya kampuni yako ni asilimia {_pct(CORPORATE_DSE_RATE)} kwa "
                f"miaka {CORPORATE_DSE_RATE_YEARS} tangu tarehe ya kuorodheshwa DSE (First "
                f"Schedule para 3(2)(a)) — kwa sababu umetaja kufikia kigezo cha hisa kwa umma. "
                f"Baada ya miaka {CORPORATE_DSE_RATE_YEARS}, kiwango cha kawaida cha asilimia "
                f"{_pct(CORPORATE_STANDARD_RATE)} kinarudi kutumika.")
        elif meets_public_float is False:
            working = (
                f"Kiwango cha kawaida cha asilimia {_pct(CORPORATE_STANDARD_RATE)} kinatumika, "
                f"SI asilimia {_pct(CORPORATE_DSE_RATE)}. Kuorodheshwa DSE peke yake hakutoshi — "
                f"lazima angalau asilimia {_pct(CORPORATE_DSE_PUBLIC_FLOAT_CURRENT)} ya hisa "
                f"ziwe kwa umma (First Schedule para 3(2)(a), kigezo hiki kilipunguzwa kutoka "
                f"asilimia 30 hadi 25 na Sheria ya Fedha 2025 Kifungu 60(d)(i), tangu "
                f"{CORPORATE_DSE_PUBLIC_FLOAT_CHANGE_DATE}) — umetaja huwezi kufikia kigezo hicho.")
        else:
            working = (
                f"Kampuni zilizoorodheshwa DSE zinapata asilimia {_pct(CORPORATE_DSE_RATE)} kwa "
                f"miaka {CORPORATE_DSE_RATE_YEARS} — LAKINI kwa sharti kwamba angalau asilimia "
                f"{_pct(CORPORATE_DSE_PUBLIC_FLOAT_CURRENT)} ya hisa ziwe kwa umma (First "
                f"Schedule para 3(2)(a), kigezo hiki tangu {CORPORATE_DSE_PUBLIC_FLOAT_CHANGE_DATE} "
                f"— kilikuwa asilimia 30 kabla ya hapo). Je, sehemu ya hisa kwa umma inafikia "
                f"kiwango hicho? Bila hilo, kiwango cha kawaida cha asilimia "
                f"{_pct(CORPORATE_STANDARD_RATE)} ndicho kinachotumika.")
        return ComputationResult(
            computation="corporate_tax", applicable=True, amount=None, working=working,
            inputs=inputs, note="First Schedule para 3(1)/3(2)(a) — DSE-listed rate branch")

    working = (
        f"Kiwango cha kawaida cha kodi ya mapato ya kampuni Tanzania ni asilimia "
        f"{_pct(CORPORATE_STANDARD_RATE)} ya faida inayotozwa kodi (First Schedule para 3(1)). "
        f"Kampuni zilizoorodheshwa DSE zenye angalau asilimia "
        f"{_pct(CORPORATE_DSE_PUBLIC_FLOAT_CURRENT)} ya hisa kwa umma hulipa asilimia "
        f"{_pct(CORPORATE_DSE_RATE)} kwa miaka {CORPORATE_DSE_RATE_YEARS} tangu kuorodheshwa "
        f"(para 3(2)(a)). Hii ni kiwango — SI hesabu ya TZS kutoka mauzo: faida (si mauzo) "
        f"ndiyo msingi wa kodi hii, na faida haiwezi kupatikana kutoka mauzo peke yake.")
    return ComputationResult(
        computation="corporate_tax", applicable=True, amount=None, working=working,
        inputs=inputs, note="First Schedule para 3(1) — standard rate, no DSE/AMT facts given")


def partnership_tax_statement(partner_is_individual=None) -> ComputationResult:
    """A partnership is NOT itself liable for income tax (Cap 332 s.48(1)). Declines to name a
    rate because the real one depends on who the partner is, which this function is never given
    enough to determine on its own — `partner_is_individual` narrows the EXPLANATION only, it
    never turns into a computed rate here."""
    inputs = {"partner_is_individual": partner_is_individual}
    working = (
        "Ubia (partnership) wenyewe HAULIPI kodi ya mapato ya jumla yake (Sheria ya Kodi ya "
        "Mapato Kifungu 48(1)) — si kama kampuni. Badala yake, faida au hasara ya ubia "
        "hugawanywa kwa kila mshirika kulingana na sehemu yake (Vifungu 49-50), na KILA "
        "MSHIRIKA analipa kodi mwenyewe juu ya sehemu yake, kwa kiwango kinachomhusu YEYE — "
        "viwango vya mtu binafsi kama mshirika ni mtu, au asilimia 30 kama mshirika ni kampuni. "
        "Sina taarifa ya kutosha kutaja kiwango bila kujua mshirika ni nani. Thibitisha na TRA "
        "(tra.go.tz).")
    return ComputationResult(
        computation="partnership_tax", applicable=True, amount=None, working=working,
        inputs=inputs, note="ss.48-51 — partnership is tax-transparent, never-guess the rate")
