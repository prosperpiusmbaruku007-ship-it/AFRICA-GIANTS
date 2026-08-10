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
    )


def sector_rates_statement(sector_no, paid, period="monthly") -> ComputationResult:
    """A sector was identified but not the SUB-sector — state every candidate rate and ask which.

    NOT a guess and NOT a bare refusal. 12 of the 16 sectors carry more than one rate and 5 of
    7 sector-only cases flip the verdict across their candidates, so picking one returns the
    OPPOSITE legal answer. Listing the Order's own rates for the sector is fully sourced, lets
    the employer resolve it themselves, and is what a competent advisor would ask back.

    No verdict is stated, so there is no lead word and the frame is irrelevant here.
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
            f"{tzs(lo)} hadi {tzs(hi)} {per} ({_GAZETTE}, {_IN_FORCE}), hivyo siwezi kusema "
            f"kama {tzs(Decimal(paid))} {per} ni halali bila kujua aina ya kazi hasa. "
            f"Viwango ni: {options}. Niambie ni kipi kinakuhusu nami nitalinganisha. {_CONFIRM}"
        ),
        inputs={"paid": Decimal(paid), "period": period, "sector": sector_no,
                "candidate_low": lo, "candidate_high": hi},
        note="sector identified, sub-sector unresolved — rates stated, no verdict",
    )
