# -*- coding: utf-8 -*-
"""Withholding tax on rent — a RATE STATEMENT with a hard precondition, not a computation.

THE RATE (Income Tax Act Cap.332 R.E.2023, First Schedule para 4(b)(ii)):

    "in the case of interest, rent or a commuted pension paid to a resident withholdee
     or interest or rent paid to a non-resident withholdee - ten percent"

TEN PERCENT FOR BOTH RESIDENTS AND NON-RESIDENTS. There is NO residency split for rent.
This is not drafting silence — the non-resident limb is named explicitly and given the same
figure. The discriminating evidence is the adjacent contrast: the SAME paragraph writes a
real residency split for service fees at para 4(c)(i), "five percent for a resident and
fifteen percent for a non-resident". The Act uses that form where a split exists and does
not use it here.

WHY THERE IS NO `is_resident` PARAMETER, AND WHY THAT IS THE POINT. The corpus taught
10%-resident / 15%-non-resident in 16 rows (quarantined 2026-09-26), sourced to a TRA page
that states 10%/10% — the cited-and-contradicted shape. The 15% is para 4(b)(iv)'s
catch-all, "in the case of other payments - fifteen percent", taken instead of the specific
rent limb three lines above it. An `is_resident` parameter here would encode the corpus's
error into code and hand a confident 15% to non-resident landlords. THE ABSENT PARAMETER IS
THE FIX. Do not add one without re-reading para 4(b)(ii).

R31 PARAMETER/EXTRACTOR INVENTORY — required before shipping, one row per parameter:

  parameter                    | extractor                              | reachable?
  -----------------------------|----------------------------------------|------------
  letting_is_commercial        | routing.rent_letting_is_commercial()   | YES, natural
  payer_is_withholding_agent   | NONE, deliberately — see below         | N/A by design

`payer_is_withholding_agent` has NO extractor and never will, and that is a THREE-STATE
DESIGN in the documented sense (cf. compute_presumptive's `new_business_exemption_granted`,
which R31 checked and REJECTED as an instance for exactly this reason). Whether a payer is
a withholding agent is a fact about the payer's own tax status that no question states, and
guessing it is how ext_43 went wrong: it told a small individual trader renting a village
house that he must withhold 10%, when an ordinary individual tenant is not automatically a
withholding agent at all. `None` therefore states BOTH limbs explicitly and refuses to
decide — it narrows the EXPLANATION only, and never turns into "yes, withhold".

This is why the module is a STATEMENT and not a computation: under R19 the checkable claim
here is a CONSTANT (the 10% rate against the statute), not a derived amount. Multiplying
rent by 10% would produce a figure indistinguishable from a fabrication whenever the
precondition is unmet — the Guard B shape.
"""

from .results import ComputationResult

# The single statutory rate. Named so a future reader looking for a resident/non-resident
# pair finds this instead and reads why there isn't one.
RENT_WHT_RATE_BOTH_RESIDENCIES = 0.10
_CITATION = "Sheria ya Kodi ya Mapato Cap.332, Jedwali la Kwanza aya 4(b)(ii)"

_RATE_SENTENCE = (
    "Kodi ya zuio kwenye PANGO ni asilimia 10 — kiwango kimoja kwa wakazi NA wasio wakazi "
    f"({_CITATION}). Hakuna tofauti ya kiwango kwa sababu ya makao ya mwenye nyumba."
)

# The precondition, stated in both directions because the engine is never told which holds.
_AGENT_SENTENCE = (
    "LAKINI kukata kodi hii ni WAJIBU WA WAKALA WA KUZUIA (withholding agent) tu. Mtu wa "
    "kawaida anayelipa pango si wakala wa kuzuia kwa sababu ya kulipa pango peke yake — "
    "wajibu huu unamhusu anayefanya biashara/ana wajibu huo kisheria. Kama hujui kama wewe "
    "ni wakala wa kuzuia, thibitisha na TRA (tra.go.tz) KABLA ya kukata."
)

_COMMERCIAL_NOTE = (
    "Kiwango hiki cha asilimia 10 kinatajwa kwa pango la KIBIASHARA kwenye jedwali la TRA."
)
_RESIDENTIAL_NOTE = (
    "Kwa pango la nyumba ya kuishi (si biashara), thibitisha na TRA — jedwali la TRA "
    "linataja 'Rental Income (For commercial purposes)', kwa hiyo sina uhakika kiwango hiki "
    "kinatumika vivyo hivyo hapa."
)


def rent_wht_statement(letting_is_commercial=None,
                       payer_is_withholding_agent=None) -> ComputationResult:
    """State the rent WHT rate and its precondition. Never computes an amount.

    `payer_is_withholding_agent=None` is the NORMAL case, not a degraded one: nothing
    extracts it from a question, so the default states both limbs. It is accepted as a
    parameter only so a caller that genuinely knows (a confirmed agent) can narrow the
    prose — it must never be inferred from the question text.
    """
    inputs = {"letting_is_commercial": letting_is_commercial,
              "payer_is_withholding_agent": payer_is_withholding_agent}

    parts = [_RATE_SENTENCE]

    if letting_is_commercial is False:
        parts.append(_RESIDENTIAL_NOTE)
    elif letting_is_commercial is True:
        parts.append(_COMMERCIAL_NOTE)
    else:
        # Unknown: say which case the figure is stated for rather than assuming commercial.
        parts.append(_COMMERCIAL_NOTE)

    if payer_is_withholding_agent is True:
        parts.append("Kwa kuwa wewe ni wakala wa kuzuia, unatakiwa kukata asilimia 10 na "
                     "kuiwasilisha TRA ndani ya siku 7 baada ya mwisho wa mwezi.")
    elif payer_is_withholding_agent is False:
        parts.append("Kwa kuwa wewe si wakala wa kuzuia, HUNA wajibu wa kukata kodi hii "
                     "kwenye pango unalolipa.")
    else:
        parts.append(_AGENT_SENTENCE)

    return ComputationResult(
        computation="rent_wht",
        applicable=True,
        amount=None,          # R19: a rate statement, never a derived amount.
        working=" ".join(parts),
        inputs=inputs,
        note=("Cap.332 First Schedule para 4(b)(ii) — 10% for BOTH residencies; obligation "
              "is conditional on withholding-agent status, which is never inferred"),
    )
