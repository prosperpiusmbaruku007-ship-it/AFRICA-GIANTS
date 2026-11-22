"""Minimum wage (GN 605A) — is the wage this employer pays lawful?

THE POINT OF ROUTING THIS DETERMINISTICALLY. th_16 ("Namlipa mfanyakazi wa shamba TZS 200,000
kwa mwezi — je ni halali kisheria?") has been answered WRONG in production: paying ABOVE the
floor was called unlawful. Six candidate wordings of a locked fact were measured live and none
fixed it — supplying the correct number did not produce the correct comparison (one candidate
recited TZS 195,000 and then called TZS 180,000 higher than it). The comparison itself is what
the model gets wrong, so the comparison is what has to leave the model.

`Orchestrator._deterministic_answer` blanks the body entirely and renders `working` verbatim,
so every mechanism behind those six failures is removed structurally rather than guarded
against. That is load-bearing here in a way it is not for the levies: BOTH fidelity guards are
numeric — `body_contradicts_working` with `amount is None` requires a naive levy compute AND an
asserted `TZS N`, and `body_contradicts_siblings` windows on the four levy tokens — so a body
asserting "ni halali" with no figures in it is invisible to both. Blanking is the safety net
here because no guard can be.

THE INVERSION HAS A SECOND SOURCE. Blanking the body kills the MODEL-side inversion. It does
nothing about the QUESTION's frame: "je ni halali?" and "nakiuka sheria?" take opposite lead
words for the same facts, and the yes/no scorer reads the polarity of the first paragraph. So
the lead is chosen from (frame, compliant) — and where the frame is unmatched the answer LEADS
SUBSTANTIVELY ("Mshahara wa TZS X ... uko CHINI ya kima cha chini cha TZS Y"), which is correct
under either reading and does not depend on the detector being right. The verdict word is
derived from the compliance boolean in one place and never authored twice.

PERIODS ARE COMPARED COLUMN-TO-COLUMN, NEVER CONVERTED. The Order prescribes hourly, daily,
weekly, fortnightly and monthly rates for every row, so a wage quoted per day is compared
against the Order's DAILY figure. No division, no x26, no rounding — which removes a class of
arithmetic error instead of guarding against it, and means this does not wait on the separate
unit-normalisation item. (TZS 10,000/day against the MONTHLY agriculture floor of 175,000 would
call a lawful wage unlawful; against the daily floor of 6,731 it is lawful.)

Sector resolution, and why an unresolved sector is clarified rather than defaulted, is in
wage_schedule.py.
"""

from decimal import Decimal

from . import premise
from . import wage_schedule as ws
from .results import ComputationResult, tzs

COMPUTATION = "minimum_wage"

PERIOD_SW = {
    "hourly": "kwa saa", "daily": "kwa siku", "weekly": "kwa wiki",
    "fortnightly": "kwa wiki mbili", "monthly": "kwa mwezi",
}

_GAZETTE = "GN 605A, Jedwali la Pili"
_IN_FORCE = "inayotumika tangu 1 Januari 2026"
_CONFIRM = "Thibitisha na Ofisi ya Kazi (kazi.go.tz)."

# (frame, compliant) -> the lead. 'unknown' is absent on purpose: no lead at all, so the
# answer opens with the substantive comparison, which is right under either frame.
_LEADS = {
    ("lawful", True): "Ndiyo, ni halali.",
    ("lawful", False): "Hapana, si halali.",
    ("violation", True): "Hapana, hukiuki sheria.",
    ("violation", False): "Ndiyo, unakiuka sheria.",
}


def _direction(paid: Decimal, floor: Decimal) -> str:
    if paid < floor:
        return "CHINI ya"
    if paid == floor:
        return "SAWA na"
    return "JUU ya"


def compare_to_floor(paid, sector_no, sub, period="monthly",
                     frame="unknown") -> ComputationResult:
    """The verdict for a wage whose Schedule ROW is determined.

    `paid` is compared against the Order's figure for the SAME period column. `applicable`
    carries the compliance boolean — for this computation type that is the deterministic
    yes/no the result exists to state, the same role it plays in sdl_applies. `amount` stays
    None: nothing is owed here, the floor is a comparison operand and lives in `inputs`.
    """
    row = ws.BY_ROW[(sector_no, sub)]
    floor = ws.rate(row, period)
    paid = Decimal(paid)
    compliant = paid >= floor                       # the ONE place the verdict is decided
    per = PERIOD_SW[period]
    label = ws.label_sw(sector_no, sub)

    core = (f"Mshahara wa {tzs(paid)} {per} uko {_direction(paid, floor)} kima cha chini cha "
            f"{label}, ambacho ni {tzs(floor)} {per} ({_GAZETTE}, {_IN_FORCE}).")
    if compliant:
        tail = ("Kifungu cha 4(3) cha GN 605A kinaruhusu mwajiri kulipa mfanyakazi kiasi "
                "ZAIDI ya kima cha chini kilichowekwa.")
    else:
        tail = (f"Unatakiwa kupandisha mshahara hadi angalau {tzs(floor)} {per}.")

    lead = _LEADS.get((frame, compliant))
    body = f"{lead} {core}" if lead else core
    return ComputationResult(
        computation=COMPUTATION,
        applicable=compliant,
        amount=None,
        working=f"{body} {tail} {_CONFIRM}",
        inputs={"paid": paid, "floor": floor, "period": period,
                "sector": sector_no, "sub_sector": sub, "frame": frame},
        note="wage at or above the GN 605A floor" if compliant
             else "wage below the GN 605A floor",
        # ⛔ DECLARED ONLY WHEN A LEAD WAS ACTUALLY WRITTEN. `frame="unknown"` emits no
        # particle at all (by design — the comparison is right under either frame), so there
        # is nothing for the premise resolver to re-lead and claiming one would invite it to
        # prepend a particle to an answer that deliberately has none.
        #
        # ⚠️ THE TRUTH IS THE RAW LAWFULNESS, NOT THE FRAME-ADJUSTED LEAD. _LEADS above
        # already resolves the `violation` frame's inversion ("Hapana, hukiuki sheria" for a
        # COMPLIANT wage), and premise.detect reports the same inversion independently from
        # the question. Declaring the frame-adjusted value here would apply the inversion
        # twice and answer every lawfulness question backwards.
        lead_claim=(premise.WAGE_IS_LAWFUL, compliant) if lead else None,
    )


def sector_rates_statement(sector_no, paid, period="monthly") -> ComputationResult:
    """A sector was identified but not the SUB-sector — state every candidate rate and ask which.

    NOT a guess and NOT a bare refusal. 12 of the 16 sectors carry more than one rate and 5 of
    7 sector-only cases flip the verdict across their candidates, so picking one returns the
    OPPOSITE legal answer. Listing the Order's own rates for the sector is fully sourced, lets
    the employer resolve it themselves, and is what a competent advisor would ask back.

    No verdict is stated, so there is no lead word and the frame is irrelevant here. The copy
    also avoids every word in the lawful/violation cue vocabulary — the first wording said
    "siwezi kusema kama TZS 250,000 ... NI HALALI bila kujua aina ya kazi", which states a
    refusal but contains the affirmative cue, and a yes/no scorer reading the polarity of the
    first paragraph can credit it as a lawful verdict. Rephrased rather than guarded: the
    substring is gone, not handled. `test_no_clarification_reads_as_a_verdict` pins it by
    asserting wage_question_frame() sees 'unknown' in every clarification this module emits.
    """
    rows = ws.BY_SECTOR[sector_no]
    per = PERIOD_SW[period]
    options = "; ".join(
        f"{ws.SUB_LABELS_SW.get((r[0], r[1]), r[2])} {tzs(ws.rate(r, period))}" for r in rows)
    lo = min(ws.rate(r, period) for r in rows)
    hi = max(ws.rate(r, period) for r in rows)
    return ComputationResult(
        computation=COMPUTATION,
        applicable=True,
        amount=None,
        working=(
            f"Sekta ya {ws.SECTOR_NAMES_SW[sector_no]} ina viwango zaidi ya kimoja, kuanzia "
            f"{tzs(lo)} hadi {tzs(hi)} {per} ({_GAZETTE}, {_IN_FORCE}), hivyo siwezi "
            f"kulinganisha {tzs(Decimal(paid))} {per} bila kujua aina ya kazi hasa. "
            f"Viwango ni: {options}. Niambie ni kipi kinakuhusu nami nitalinganisha. {_CONFIRM}"
        ),
        inputs={"paid": Decimal(paid), "period": period, "sector": sector_no,
                "candidate_low": lo, "candidate_high": hi},
        note="sector identified, sub-sector unresolved — rates stated, no verdict",
    )


def sector_wage_statement(text) -> ComputationResult:
    """THE NO-FIGURE ASK: "Kima cha chini cha mshahara kwa mfanyakazi wa nyumbani ni kiasi gani?" (2026-11-22, preliminary Gate 2). Every monthly rate of the asked sector, from the transcribed Schedule, no model.

    WHY A STATEMENT AND NOT A CLARIFICATION. There was no route at all: the two no-figure phrasings fell to the model, which answered "karibu TZS 80,000" -- the LOWEST of the four domestic-work rates, stated as if it were the
    rate. The four rates turn on who the employer is and whether the worker lives in the household, so the answer is the whole table with none selected -- the same discipline as the other fixed statements. Where the question
    names a work that settles the row, that row is stated first AND the sector's others follow, so a reader who is in a different row is not left holding the wrong figure.

    Never auto-sent (it travels as the `fixed_statement` route, which handler_core excludes). Raises on a question whose sector does not resolve: a statement route with nothing to state must not guess (R31)."""
    outcome, value = ws.resolve(text)
    if outcome not in (ws.SECTOR, ws.ROW):
        raise ValueError("no sector resolves from the question")
    sector_no, sub = (value, None) if outcome == ws.SECTOR else value
    rows = ws.BY_SECTOR[sector_no]
    name = ws.SECTOR_NAMES_SW[sector_no]
    tail = f"Chanzo: {_GAZETTE}, {_IN_FORCE}. Viwango vya kwa saa, siku na wiki pia vimo kwenye Agizo hilo. {_CONFIRM}"
    if len(rows) == 1:
        working = f"Kima cha chini cha mshahara kwa sekta ya {name} ni {tzs(ws.rate(rows[0]))} kwa mwezi. {tail}"
    else:
        options = "; ".join(f"{ws.SUB_LABELS_SW.get((r[0], r[1]), r[2])} {tzs(ws.rate(r))}" for r in rows)
        lead = ""
        advice = " Kiwango kinachokuhusu kinategemea aina ya kazi, kwa hiyo usichukue kimoja bila kujua kipi ni chako."
        if sub is not None and (sector_no, sub) in ws.BY_ROW:
            row = ws.BY_ROW[(sector_no, sub)]
            lead = f"Kwa kazi uliyotaja ({ws.SUB_LABELS_SW.get((row[0], row[1]), row[2])}) kiwango ni {tzs(ws.rate(row))} kwa mwezi. "
            advice = ""                                  # a row IS settled: the "do not pick one" caution would contradict the sentence above it
        working = f"{lead}Sekta ya {name} ina viwango zaidi ya kimoja kwa mwezi: {options}.{advice} {tail}"
    return ComputationResult(
        computation="fixed_statement", applicable=True, amount=None, working=working,
        inputs={"topic": "sector_minimum_wage", "sector": sector_no, "sub": sub},
        note="GN 605A sector rates stated whole from the transcribed Schedule (wage_schedule.SCHEDULE); no figure asked, none computed",
    )
