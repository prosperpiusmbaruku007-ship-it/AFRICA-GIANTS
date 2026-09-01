"""Presumptive income tax — the tax a small trader actually pays.

Income Tax Act Cap 332, First Schedule para 2, as substituted by the Finance Act 2022
(Act No. 5 of 2022) s.72, in force 1 July 2022, AS FURTHER AMENDED BY the Finance Act 2026
s.27(a), in force 1 July 2026. See rates.PRESUMPTIVE_BANDS for the full provenance, why the
CONSOLIDATED statute (R.E. 2019) would have given wrong numbers, and the 2026-09-01
stale-constant incident this engine's own build (2026-08-16) fell into.

WHY THIS IS AN ENGINE AND NOT A FACT: it is a band table with marginal arithmetic in two
bands, exactly the shape paye.py already handles, and an engine answer bypasses generation
entirely — so it is immune to whatever the fact path is doing wrong.

THE EXCLUSIONS ARE AS LOAD-BEARING AS THE BANDS. An independent professional told they owe
TZS 250,000 of presumptive tax has been given a wrong answer carrying the engine's authority,
and it is wrong in the dangerous direction: they are outside the regime altogether and are
taxed on the ordinary individual rates. `applicable=False` is that answer, and it is a
correct answer, not an error.

THE NEW-BUSINESS FIRST-YEAR EXEMPTION (FA2026 s.27(a)(ii)-(iii)) IS NEVER GUESSED EITHER
DIRECTION. It turns on TWO independent facts no question states by default: the date a TIN
was obtained "for purposes of commencing a business", and whether the Commissioner has
GRANTED an application for the exemption (para 2(4) — it is not self-executing). Asserting
TZS 0 without confirmation would be as wrong as asserting the ordinary band figure while
ignoring a real possibility of TZS 0. `new_business_exemption_granted=None` (the default)
computes the ordinary band figure — still the correct fallback answer — and states the
exemption's possible applicability explicitly rather than silently, so the reply neither
over- nor under-claims.
"""

from decimal import Decimal

from .rates import (
    PRESUMPTIVE_BANDS,
    PRESUMPTIVE_TURNOVER_CEILING,
)
from .results import ComputationResult, to_shillings, tzs

# Where the two columns of the statutory table DIFFER. Outside this window the answer is the
# same whether or not the trader keeps records — below 4M it is nil either way, and above 11M
# it is 4% of turnover either way (was 3.5%, FA2026 s.27(a)(ii) — the RATE changed, this WINDOW
# did not: confirmed by direct comparison of the amended table, the 4M-11M bands are untouched).
# Callers use this to avoid asking a question whose answer cannot change the figure: a
# never-guess contract requires asking when the input MATTERS, not asking whenever an input is
# absent. Five of the six CLARIFY rows in the 48-question set are delivery failures of exactly
# that kind.
_RECORDS_MATTER_ABOVE = Decimal("4000000")
_RECORDS_MATTER_UPTO = Decimal("11000000")


def records_status_matters(annual_turnover) -> bool:
    """True only where the records-kept axis changes the figure (4,000,001–11,000,000)."""
    turnover = Decimal(annual_turnover)
    return _RECORDS_MATTER_ABOVE < turnover <= _RECORDS_MATTER_UPTO


def _apply(spec, turnover: Decimal):
    """Evaluate one cell of the statutory table. Returns (amount, working_fragment)."""
    kind = spec[0]
    if kind == "nil":
        return Decimal("0"), "TZS 0"
    if kind == "fixed":
        return spec[1], tzs(spec[1])
    if kind == "marginal":
        base, rate, from_ = spec[1], spec[2], spec[3]
        amount = to_shillings(base + rate * (turnover - from_))
        lead = f"{tzs(base)} + " if base else ""
        return amount, (f"{lead}{rate * 100:.0f}% × ({tzs(turnover)} − {tzs(from_)}) "
                        f"= {tzs(amount)}")
    if kind == "flat_on_turnover":
        rate = spec[1]
        amount = to_shillings(rate * turnover)
        return amount, f"{rate * 100:.1f}% × {tzs(turnover)} = {tzs(amount)}"
    raise ValueError(f"unknown presumptive spec kind: {kind!r}")


_NEW_BUSINESS_NOTE = (
    " Kumbuka: kama umepata TIN mara ya kwanza kwa ajili ya kuanzisha biashara hii ndani ya "
    "miezi 12 iliyopita, huenda ukastahili msamaha wa TZS 0 kwa mwaka wa kwanza — LAKINI hii "
    "SI ya moja kwa moja: lazima uombe kwa Kamishna na aidhinishe (First Schedule para 2(4)). "
    "Bila kuidhinishwa, kiasi hapo juu ndicho kinachotumika. Thibitisha na TRA.")


def compute_presumptive(annual_turnover, keeps_records: bool,
                        excluded_service: bool = False,
                        new_business_exemption_granted: bool = None) -> ComputationResult:
    """Presumptive income tax on ONE resident individual's ANNUAL TURNOVER.

    `annual_turnover` is turnover — gross sales — not profit and not a monthly figure.
    `keeps_records` is compliance with the Tax Administration Act's maintenance-of-documents
    duty (s.35 in the First Schedule's own cross-reference; s.43 in Cap 438 R.E. 2023).
    `excluded_service` marks an independent professional or a provider of technical,
    management, construction or training services — outside the regime by para 2(1)(a).
    `new_business_exemption_granted` — True/False/None (default). True ONLY when the caller has
    confirmed BOTH that the individual is within 12 months of a TIN obtained to commence this
    business AND that the Commissioner has actually granted the para 2(4) exemption (it is not
    automatic). False means confirmed NOT eligible or NOT granted. None (the default, and the
    only safe value absent explicit confirmation of BOTH facts) computes the ordinary band
    figure as the fallback answer and states the exemption's possible applicability rather than
    silently omitting it — never-guess applies to this exemption exactly as to a rate.
    """
    turnover = Decimal(annual_turnover)
    inputs = {"annual_turnover": turnover, "keeps_records": bool(keeps_records),
              "excluded_service": bool(excluded_service),
              "new_business_exemption_granted": new_business_exemption_granted}

    if excluded_service:
        return ComputationResult(
            computation="presumptive", applicable=False, amount=None,
            working=(
                "Hapana. Kodi ya makadirio (presumptive) haitumiki kwa wataalamu huru wala "
                "watoa huduma za kitaalamu, uendeshaji, ujenzi na mafunzo. Biashara ya aina "
                "hii inatozwa kodi ya mapato kwa viwango vya kawaida vya mtu binafsi, si "
                "jedwali la makadirio."),
            inputs=inputs,
            note="First Schedule para 2(1)(a) as amended by FA2022 s.72(a)(i) — excluded service")

    if turnover > PRESUMPTIVE_TURNOVER_CEILING:
        return ComputationResult(
            computation="presumptive", applicable=False, amount=None,
            working=(
                f"Hapana. Mauzo ya {tzs(turnover)} yamezidi kikomo cha "
                f"{tzs(PRESUMPTIVE_TURNOVER_CEILING)} kwa mwaka, hivyo kodi ya makadirio "
                f"haitumiki. Kodi hupigwa kwa viwango vya kawaida vya mtu binafsi kwa faida "
                f"halisi, si kwa mauzo."),
            inputs=inputs,
            note="First Schedule para 2(2) — above the 200M presumptive threshold (WEF "
                 "2026-07-01, FA2026 s.27(a)(i); was 100M)")

    # NEW-BUSINESS EXEMPTION, CONFIRMED GRANTED. The only state that can assert TZS 0 outright —
    # everything else falls through to the ordinary band table below, which is still the
    # correct answer to state when the exemption is unconfirmed (see _NEW_BUSINESS_NOTE).
    if (new_business_exemption_granted is True
            and Decimal("4000000") < turnover <= PRESUMPTIVE_TURNOVER_CEILING):
        return ComputationResult(
            computation="presumptive", applicable=True, amount=Decimal("0"),
            working=(
                f"Kodi ya makadirio = TZS 0. Umeidhinishwa msamaha wa mwaka wa kwanza wa "
                f"biashara mpya (First Schedule para 2(3)-(4), TIN mpya kwa ajili ya kuanzisha "
                f"biashara, ndani ya miezi 12) — msamaha huu unatumika hadi "
                f"{tzs(PRESUMPTIVE_TURNOVER_CEILING)} za mauzo."),
            inputs=inputs,
            note="First Schedule para 2(3) new row 2 + para 2(4), FA2026 s.27(a)(ii)-(iii) — "
                 "new-business exemption, confirmed granted")

    for upper, no_records_spec, records_spec in PRESUMPTIVE_BANDS:
        if turnover <= upper:
            spec = records_spec if keeps_records else no_records_spec
            amount, fragment = _apply(spec, turnover)
            break
    else:                                                    # pragma: no cover - unreachable
        raise AssertionError("turnover within the ceiling matched no band")

    if amount == 0:
        working = (f"Kodi ya makadirio = TZS 0 (mauzo ya {tzs(turnover)} kwa mwaka yako "
                   f"ndani ya kiwango cha sifuri hadi TZS 4,000,000)")
    else:
        working = f"Kodi ya makadirio = {fragment}"
        if not records_status_matters(turnover):
            working += " (kiwango hiki ni kile kile ukiwa unatunza kumbukumbu au la)"
        elif keeps_records:
            working += " (kwa mfanyabiashara anayetunza kumbukumbu za mahesabu)"
        else:
            working += " (kwa asiyetunza kumbukumbu za mahesabu)"

    # NEVER-GUESS ON THE EXEMPTION, THE UNCONFIRMED CASE. `amount == 0` already covers the
    # sub-4M band's own unconditional NIL, so this note only fires where it can change anything
    # — turnover ABOVE 4M (where the ordinary table would otherwise charge something) and the
    # exemption status is genuinely unknown, never when it has been ruled out.
    if (new_business_exemption_granted is None and amount > 0
            and turnover <= PRESUMPTIVE_TURNOVER_CEILING):
        working += _NEW_BUSINESS_NOTE

    return ComputationResult(
        computation="presumptive", applicable=True, amount=amount, working=working,
        inputs=inputs,
        note="annual turnover, individual presumptive schedule (FA2022 s.72, FA2026 s.27(a))")
