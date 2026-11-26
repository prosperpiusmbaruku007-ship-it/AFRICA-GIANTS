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

import re
from decimal import Decimal

from .results import ComputationResult

# The single statutory rate. Named so a future reader looking for a resident/non-resident
# pair finds this instead and reads why there isn't one.
RENT_WHT_RATE_BOTH_RESIDENCIES = 0.10
# R44 (2026-11-26, founder-approved): served Swahili text names the Act, never a chapter or paragraph number of a consolidated Act (they renumber between
# editions). The paragraph lives in `ComputationResult.note` (metadata, not rendered into the reply).
_CITATION = "Sheria ya Kodi ya Mapato (ITA), Jedwali la Kwanza"

# The conditional computed line (founder-approved 2026-11-26). The marker is ALSO held, verbatim, in chike-whatsapp/handler_core.py
# (AMOUNT_BEARING_RENT_MARKERS) so an amount-bearing rent reply is never auto-sent; tests/test_rent_wht_amount_line.py asserts the two agree.
AMOUNT_BEARING_MARKER = "Ikiwa wewe ni wakala wa kuzuia: 10% ×"

_RENT_WORD = re.compile(r"pango|(?<![a-z])rent(?![a-z])|kodi\s+ya\s+(?:nyumba|jengo|ofisi|duka|fremu|chumba)|mwenye\s+nyumba|landlord", re.I)
_NOT_RENT_FIGURE = re.compile(r"mauzo|mapato|turnover|faida|mtaji|mshahara|salary|mkopo|deni|bei", re.I)
_RENT_AMOUNT_REACH = 60      # characters between the figure and the nearest rent word


def rent_amount(text):
    """The ONE rent figure in the question, or None. Declines (None) unless there is exactly one plausible amount AND a rent word within
    60 characters of it AND no turnover/income/salary/price word immediately before it: a lone figure that is not the rent must never be multiplied
    (Guard B). Pure."""
    from .. import swahili_numbers as swn
    located = [(pos, a) for pos, a in swn.parse_amounts_located(text) if a >= swn.MIN_PLAUSIBLE_AMOUNT]
    if len(located) != 1:
        return None
    pos, amount = located[0]
    if not any(abs(m.start() - pos) <= _RENT_AMOUNT_REACH for m in _RENT_WORD.finditer(text)):
        return None
    if _NOT_RENT_FIGURE.search(text[max(0, pos - 40):pos]):
        return None
    return amount


def _fmt(d):
    d = Decimal(d)
    return f"{int(d):,}" if d == d.to_integral_value() else f"{d.quantize(Decimal('0.01')):,.2f}"

_RATE_SENTENCE = (
    "Kodi ya zuio kwenye PANGO ni asilimia 10 — kiwango kimoja kwa wakaazi wa kikodi NA wasio wakaazi wa kikodi "
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
                       payer_is_withholding_agent=None, rent_amount=None) -> ComputationResult:
    """State the rent WHT rate and its precondition. Never computes an amount.

    `payer_is_withholding_agent=None` is the NORMAL case, not a degraded one: nothing
    extracts it from a question, so the default states both limbs. It is accepted as a
    parameter only so a caller that genuinely knows (a confirmed agent) can narrow the
    prose — it must never be inferred from the question text.
    """
    inputs = {"letting_is_commercial": letting_is_commercial,
              "payer_is_withholding_agent": payer_is_withholding_agent,
              "rent_amount": None if rent_amount is None else str(rent_amount)}

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

    if rent_amount is not None:
        # CONDITIONAL, never an obligation: the payer's agent status is never inferred, so the sum is stated under the "if". `amount` stays None (R19).
        withheld = Decimal(rent_amount) * Decimal(str(RENT_WHT_RATE_BOTH_RESIDENCIES))
        parts.append(f"{AMOUNT_BEARING_MARKER} TZS {_fmt(rent_amount)} = TZS {_fmt(withheld)}.")

    return ComputationResult(
        computation="rent_wht",
        applicable=True,
        amount=None,          # R19: a rate statement, never a derived amount.
        working=" ".join(parts),
        inputs=inputs,
        note=("Cap.332 First Schedule para 4(b)(ii) — 10% for BOTH residencies; obligation "
              "is conditional on withholding-agent status, which is never inferred"),
    )
