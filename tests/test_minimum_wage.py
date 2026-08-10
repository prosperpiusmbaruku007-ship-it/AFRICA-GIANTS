"""GN 605A minimum wage — the schedule, the four-outcome resolver, the frame, the verdict.

Everything in this file is deterministic string and Decimal logic, so offline is genuinely
sufficient here (unlike the wording work this replaces, where MEASUREMENT-GAP-1 applied). The
live checks that DO matter are the router firing end-to-end and the multi-part carrier; those
run against the deployed path, not here.

The probes are the file eval/accuracy_gate/minimum_wage_probes_018.jsonl, loaded below so a
future cue addition that breaks one FAILS here rather than in production (R17 step 3).
"""
import json
import pathlib
import re
from decimal import Decimal

import pytest

from chike import clarification, routing
from chike import rules_engine
from chike.rules_engine import wage_schedule as ws

PROBES = pathlib.Path("eval/accuracy_gate/minimum_wage_probes_018.jsonl")


def _probes():
    with PROBES.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


# --- the Schedule itself ----------------------------------------------------------------

def test_every_rate_figure_is_present_in_the_gazette():
    """250 hand-transcribed numbers; one wrong digit is a wrong wage told to an employer."""
    assert ws.verify_transcription() == []


def test_schedule_shape_matches_the_order():
    assert len(ws.SCHEDULE) == 50
    lettered = [r for r in ws.SCHEDULE if r[1]]
    assert len(lettered) == 46                      # 46 lettered sub-sectors
    assert len(ws.SCHEDULE) - len(lettered) == 4    # 4 unlettered sectors
    assert len({r[0] for r in ws.SCHEDULE}) == 16   # 16 sectors


def test_item_16_is_the_first_schedule_residual_rate():
    assert ws.rate(ws.ITEM_16, "monthly") == Decimal(175_000)


def test_lowest_monthly_is_the_other_domestic_rate():
    assert ws.LOWEST_MONTHLY == Decimal(80_000)


# --- the resolver: four outcomes, not two -------------------------------------------------

def test_a_row_cue_resolves_to_a_row():
    assert ws.resolve("Namlipa mfanyakazi wa shamba TZS 150,000") == (ws.ROW, (1, "a"))


def test_a_sector_cue_resolves_to_the_sector_and_not_to_one_of_its_rows():
    """'hoteli' spans 195,000..375,000 and 5 of 7 sector-only cases flip the verdict."""
    assert ws.resolve("Nina hoteli, mhudumu analipwa TZS 250,000") == (ws.SECTOR, 5)


def test_no_occupation_resolves_to_none_not_to_item_16():
    """THE CONFLATION THIS RESOLVER EXISTS TO PREVENT.

    Item 16 (TZS 175,000) is the rate for a sector the ORDER does not list. It is not the
    answer to 'the user did not say'. Returning it here would answer a question we cannot
    answer with a real gazette figure the employer could act on."""
    assert ws.resolve("Namlipa mfanyakazi wangu TZS 160,000") == (ws.NONE, None)


def test_the_unlisted_table_ships_empty_and_that_is_deliberate():
    """The Order's Interpretation clause (para 3) defines 'domestic work', 'agriculture',
    'employee', 'employer', 'private sector', 'energy' and 'mining operations' — and NOT
    'Trade and finance sector'. So whether e.g. a salon is item 16 (175,000) or sector 12(a)
    'business' (200,500) is a classification the gazette does not settle, and a wage between
    those two gets the opposite verdict either way. Populating this needs a labour-law
    source, not a cue. If a future commit fills it, this test should be rewritten with that
    source cited — not deleted."""
    assert ws._UNLISTED_CUES == []
    assert ws.resolve("Nina saluni, mfanyakazi analipwa TZS 170,000") == (ws.NONE, None)


def test_conflicting_sectors_resolve_to_none_not_first_wins():
    """'hoteli' (5c 195,000) and 'lori' (8c 398,500) give opposite verdicts at 300,000."""
    assert ws.resolve("Nina hoteli na pia nina lori, dereva analipwa TZS 300,000") == (
        ws.NONE, None)


def test_single_rate_sectors_resolve_to_a_row():
    """Sectors 13-15 carry one rate each, so a sector cue IS a row cue."""
    assert ws.resolve("Nina kiwanda kidogo") == (ws.ROW, (13, ""))


@pytest.mark.parametrize("sector_no", sorted(ws.BY_SECTOR))
def test_every_sector_can_state_its_options(sector_no):
    assert ws.sector_options_sw(sector_no)


def test_duka_la_dawa_is_a_pharmacy_not_a_shop():
    """A pharmacy (2e, 240,000) contains 'duka' (12a, 200,500). Both cues firing makes the
    sectors conflict and turns a resolvable question into a clarification."""
    assert ws.resolve("Nina duka la dawa, mfanyakazi analipwa TZS 250,000") == (ws.ROW, (2, "e"))
    assert ws.resolve("Nina duka la nguo, muuzaji analipwa TZS 250,000") == (ws.ROW, (12, "a"))


# --- R17: the cue table checked against itself, exhaustively -------------------------------

_GROUP = re.compile(r"\((?:\?:)?([^()]*)\)")


def _cue_literals(pattern):
    """Every literal phrase a cue claims to match, expanding nested groups as a cross-product.

    Flattening nested groups instead of expanding them manufactures false findings: it turns
    'dereva wa (?:lori|basi)' into the bare literal 'basi', which the table correctly does not
    match, and then reports that as a defect."""
    variants = [pattern.replace(r"\b", "")]
    while any(_GROUP.search(v) for v in variants):
        expanded = []
        for v in variants:
            g = _GROUP.search(v)
            if g is None:
                expanded.append(v)
                continue
            expanded += [v[:g.start()] + alt + v[g.end():] for alt in g.group(1).split("|")]
        variants = expanded
    out = []
    for v in variants:
        for alt in v.split("|"):
            alt = alt.replace("\\", "").replace("?", "").strip()
            if alt and not alt.startswith("!") and not any(c in alt for c in "[]{}^$*+!"):
                out.append(alt)
    return out


def _all_cue_literals():
    return [(lit, no, sub) for pat, no, sub in ws._CUES for lit in _cue_literals(pat)]


def test_no_cue_phrase_is_claimed_by_two_different_sectors():
    """The collision shape authoring does not find: two cues that are each correct alone.

    A cross-sector collision resolves to NONE, so a perfectly answerable question gets the
    'tell me what work' clarification instead of its rate. This is exhaustive over the table
    so that a future cue addition fails HERE rather than silently in production."""
    offenders = []
    for lit, _no, _sub in _all_cue_literals():
        sectors = {n for p, n, _s in ws._CUES if re.search(p, lit)}
        if len(sectors) > 1:
            offenders.append((lit, sorted(sectors)))
    assert offenders == []


def test_every_cue_lands_where_the_table_declares():
    misroutes = []
    for lit, no, sub in _all_cue_literals():
        q = f"Nina {lit}, mfanyakazi wangu analipwa TZS 250,000 kwa mwezi — je ni halali?"
        expected = (ws.ROW, (no, sub)) if sub is not None else (ws.SECTOR, no)
        if ws.resolve(q) != expected:
            misroutes.append((lit, expected, ws.resolve(q)))
    assert misroutes == []


# --- the frame: the inversion's second source ---------------------------------------------

@pytest.mark.parametrize("question,expected", [
    ("Namlipa mfanyakazi TZS 200,000 — je ni halali kisheria?", "lawful"),
    ("Namlipa mfanyakazi TZS 200,000 — hii inaruhusiwa?", "lawful"),
    ("Namlipa mfanyakazi TZS 200,000 — nakiuka sheria?", "violation"),
    ("Namlipa mfanyakazi TZS 200,000 — ni kinyume cha sheria?", "violation"),
    ("Namlipa mfanyakazi TZS 200,000 kwa mwezi.", "unknown"),
])
def test_frame_detection(question, expected):
    assert routing.wage_question_frame(question) == expected


def test_both_frames_in_one_question_is_unknown():
    """Leading neutrally is right when the question asks it both ways."""
    assert routing.wage_question_frame(
        "Je ni halali au nakiuka sheria nikimlipa TZS 200,000?") == "unknown"


def test_the_same_verdict_takes_opposite_leads_under_the_two_frames():
    """The inversion that blanking the model body does NOT fix."""
    compliant_lawful = rules_engine.compare_to_floor(200_000, 1, "a", "monthly", "lawful")
    compliant_violation = rules_engine.compare_to_floor(200_000, 1, "a", "monthly", "violation")
    assert compliant_lawful.applicable is compliant_violation.applicable is True
    assert compliant_lawful.working.startswith("Ndiyo, ni halali.")
    assert compliant_violation.working.startswith("Hapana, hukiuki sheria.")


def test_unknown_frame_leads_substantively_with_no_yes_or_no():
    """The fallback must be correct under EITHER reading, so it asserts neither."""
    working = rules_engine.compare_to_floor(150_000, 1, "a", "monthly", "unknown").working
    assert working.startswith("Mshahara wa TZS 150,000")
    assert not working.startswith(("Ndiyo", "Hapana"))


def test_verdict_word_is_derived_from_the_boolean_not_authored_twice():
    """A 'CHINI ya' body may never carry a compliant lead, in any frame."""
    for frame in ("lawful", "violation", "unknown"):
        for paid, sector, sub in ((150_000, 1, "a"), (350_000, 5, "a"), (10_000, 12, "a")):
            r = rules_engine.compare_to_floor(paid, sector, sub, "monthly", frame)
            assert r.applicable is False
            assert "CHINI ya" in r.working
            assert "Ndiyo, ni halali." not in r.working
            assert "Hapana, hukiuki sheria." not in r.working


# --- the comparison ------------------------------------------------------------------------

@pytest.mark.parametrize("paid,expected_compliant,direction", [
    (174_999, False, "CHINI ya"),
    (175_000, True, "SAWA na"),        # at the floor is lawful: >= not >
    (175_001, True, "JUU ya"),
])
def test_the_boundary(paid, expected_compliant, direction):
    r = rules_engine.compare_to_floor(paid, 1, "a", "monthly", "lawful")
    assert r.applicable is expected_compliant
    assert direction in r.working


def test_paying_above_the_floor_is_stated_as_permitted():
    """th_16's substance: GN 605A para 4(3) expressly allows paying above the minimum."""
    assert "4(3)" in rules_engine.compare_to_floor(
        200_000, 1, "a", "monthly", "lawful").working


def test_a_large_wage_can_still_be_below_its_own_floor():
    """mw_04, the sharpest probe in the set: TZS 350,000 is double the agriculture floor and
    UNLAWFUL for a four-star hotel. Any answer carrying one remembered figure gets this wrong."""
    r = rules_engine.compare_to_floor(350_000, 5, "a", "monthly", "lawful")
    assert r.applicable is False
    assert "TZS 375,000" in r.working


def test_periods_are_compared_column_to_column_never_converted():
    """TZS 10,000/day is lawful against the daily floor of 6,731 and would be called unlawful
    against the monthly 175,000. No division happens anywhere in this path."""
    daily = rules_engine.compare_to_floor(10_000, 1, "a", "daily", "lawful")
    assert daily.applicable is True
    assert "TZS 6,731" in daily.working and "kwa siku" in daily.working
    monthly = rules_engine.compare_to_floor(10_000, 1, "a", "monthly", "lawful")
    assert monthly.applicable is False


@pytest.mark.parametrize("period", ws.PERIODS)
def test_every_period_column_is_reachable_for_every_row(period):
    for no, sub in ws.BY_ROW:
        r = rules_engine.compare_to_floor(1, no, sub, period, "lawful")
        assert r.applicable is False        # TZS 1 is below every rate in the Order


def test_amount_is_none_because_nothing_is_owed():
    """The floor is a comparison operand, not a sum due. Keeping it out of `amount` also
    keeps it out of fidelity._acceptable, which treats `amount` as an authoritative levy
    figure."""
    assert rules_engine.compare_to_floor(200_000, 1, "a").amount is None


def test_sector_statement_lists_every_candidate_and_states_no_verdict():
    r = rules_engine.sector_rates_statement(5, 250_000, "monthly")
    for row in ws.BY_SECTOR[5]:
        assert f"{int(ws.rate(row, 'monthly')):,}" in r.working
    assert "halali" not in r.working.replace("ni halali bila kujua", "")


# --- the router -------------------------------------------------------------------------

def test_router_reaches_minimum_wage_for_a_lawfulness_question_with_a_wage():
    assert routing.detect_intent(
        "Namlipa mfanyakazi wa shamba TZS 150,000 kwa mwezi — je ni halali kisheria?"
    ) == "minimum_wage"


def test_router_requires_a_pay_cue_not_merely_an_employee():
    """A contract question that mentions an employee is not a wage-floor question."""
    assert routing.detect_intent(
        "Je ni halali kumwajiri mfanyakazi bila mkataba wa maandishi?") == "none"


def test_router_requires_a_money_magnitude():
    assert routing.detect_intent(
        "Je mshahara wa mfanyakazi wangu ni halali?") == "none"


def test_an_explicitly_named_levy_still_wins():
    """Path 3 is placed LAST, so by construction it can only capture questions that route to
    fact today. A wage figure plus 'ni halali' plus a named levy stays on the levy route."""
    assert routing.detect_intent(
        "Namlipa mfanyakazi wangu TZS 800,000 kwa mwezi — je ni halali kukata PAYE ya "
        "TZS 78,000?") == "paye"


def test_lawfulness_wording_alone_does_not_route_to_minimum_wage():
    """R17: 'ni halali' is in-scope vocabulary for GN 487A too."""
    assert routing.detect_intent(
        "Je ni halali kwa raia wa kigeni kufanya biashara ya rejareja Tanzania?") == "none"


@pytest.mark.parametrize("question,expected", [
    ("Namlipa TZS 10,000 kwa siku", "daily"),
    ("Namlipa TZS 60,000 kwa wiki", "weekly"),
    ("Namlipa TZS 120,000 kwa wiki mbili", "fortnightly"),
    ("Namlipa TZS 1,500 kwa saa", "hourly"),
    ("Namlipa TZS 200,000 kwa mwezi", "monthly"),
    ("Namlipa TZS 200,000", None),
])
def test_period_detection(question, expected):
    assert routing.wage_period(question) == expected


def test_fortnight_is_matched_before_week():
    """'kwa wiki mbili' contains 'kwa wiki'; ordering is what keeps them apart."""
    assert routing.wage_period("analipwa TZS 120,000 kwa wiki mbili") == "fortnightly"


def test_employment_status_cues():
    assert routing.wage_status_unclear("Nina bodaboda anayenifanyia kazi") is True
    assert routing.wage_status_unclear("Nina mfanyakazi wa shamba") is False


# --- the guards cannot be the safety net here ----------------------------------------------

def test_both_fidelity_guards_are_blind_to_a_verdict_with_no_figures():
    """Why blanking the body is load-bearing rather than one option among several.

    `body_contradicts_working` with amount=None needs a naive levy compute AND an asserted
    figure; `body_contradicts_siblings` windows on the four levy tokens. A body asserting
    'ni halali' with no numbers in it is invisible to both, so there is no guard that could
    catch a wrong verdict word after the fact."""
    from chike import fidelity
    result = rules_engine.compare_to_floor(150_000, 1, "a", "monthly", "lawful")
    lying_body = "Ndiyo, ni halali kabisa kumlipa mfanyakazi wako kiasi hicho."
    assert fidelity.body_contradicts_working(lying_body, result) is False
    assert fidelity.body_contradicts_siblings(
        lying_body, {"minimum_wage": result}) is False


def test_a_minimum_wage_sibling_cannot_disturb_the_cross_levy_guard():
    """D-FIDELITY-2 inherited nothing here: `_levy_windows` only tokenises sdl/nssf/paye/wcf,
    so a 'minimum_wage' entry in the siblings map yields no windows and is a no-op."""
    from chike import fidelity
    mw = rules_engine.compare_to_floor(150_000, 1, "a", "monthly", "lawful")
    body = "SDL = 3.5% × TZS 5,000,000 = TZS 175,000"
    assert fidelity.body_contradicts_siblings(body, {"minimum_wage": mw}) is False


# --- the probe file is the regression contract (R17 step 3) --------------------------------

def test_probe_file_loads_and_covers_every_never_guess_exit():
    probes = _probes()
    assert len(probes) == 20
    shapes = {p["shape"] for p in probes}
    for required in ("never_guess_no_sector", "never_guess_sector_only",
                     "never_guess_period", "never_guess_employment_status",
                     "violation_frame_compliant", "row_below_different_sector",
                     "conflicting_sectors", "multipart_carrier_compute_then_wage"):
        assert required in shapes, required


def test_every_routing_probe_routes_as_the_probe_file_says():
    for p in _probes():
        if p["shape"].startswith("multipart_"):
            continue                    # routed per decomposed part, see the test below
        intent = routing.detect_intent(p["question_sw"])
        if p["truth"] == "not_minimum_wage":
            assert intent != "minimum_wage", p["id"]
        else:
            assert intent == "minimum_wage", p["id"]


def test_multipart_probes_reach_the_wage_route_on_their_own_part():
    """The carrier probes are decomposed first, so the whole-question intent is the OTHER
    part's. What must hold is that exactly one decomposed part routes to minimum_wage."""
    from chike import decomposition
    for p in _probes():
        if not p["shape"].startswith("multipart_"):
            continue
        parts = decomposition.decompose_query(p["question_sw"])
        assert sum(routing.detect_intent(s) == "minimum_wage" for s in parts) == 1, p["id"]


def test_the_probe_that_could_not_reach_the_stage_it_tested():
    """mw_15's first authoring used 'na pia', a decomposition connector, so the clause was
    split before the resolver ever saw two sectors — the conflict check it existed to test was
    unreachable. Pinned here because that failure mode is invisible in a unit test of
    resolve(): the resolver was always correct; the probe never got to it."""
    from chike import decomposition
    mw_15 = next(p for p in _probes() if p["id"] == "mw_15")
    assert len(decomposition.decompose_query(mw_15["question_sw"])) == 1
    assert ws.resolve(mw_15["question_sw"]) == (ws.NONE, None)


def test_every_row_probe_gets_the_verdict_the_probe_file_asserts():
    for p in _probes():
        if p["truth"] not in ("lawful", "unlawful"):
            continue
        no, sub = (int(p["sector"][:-1]), p["sector"][-1]) if p["sector"][-1].isalpha() \
            else (int(p["sector"]), "")
        period = "daily" if p["shape"] == "period_daily" else "monthly"
        r = rules_engine.compare_to_floor(
            p["paid"], no, sub, period, routing.wage_question_frame(p["question_sw"]))
        assert r.applicable is (p["truth"] == "lawful"), p["id"]
        assert int(r.inputs["floor"]) == p["floor"], p["id"]


def test_never_guess_copy_names_what_is_missing_and_states_no_rate():
    """C4: never-guess copy is returned by the deterministic path, never written into a fact
    and handed to the model. It must also not leak a figure the user could act on."""
    assert "175,000" not in clarification.MIN_WAGE_NO_SECTOR
    assert "Sura 366" in clarification.MIN_WAGE_STATUS_UNCLEAR
    for copy in (clarification.MIN_WAGE_NO_SECTOR, clarification.MIN_WAGE_NO_AMOUNT,
                 clarification.MIN_WAGE_PERIOD_UNCLEAR,
                 clarification.MIN_WAGE_STATUS_UNCLEAR):
        assert copy.strip() and copy.strip()[-1] in ".?"


def test_no_clarification_reads_as_a_verdict():
    """A clarification must be scored as NEITHER lawful nor unlawful, not merely be one.

    Found live: `sector_rates_statement` refused correctly but did it with the words "siwezi
    kusema kama TZS 250,000 ... NI HALALI bila kujua aina ya kazi hasa". The refusal is plain
    to a reader and invisible to a yes/no scorer reading the polarity of the first paragraph,
    which sees the affirmative cue and can credit a verdict that was never given.

    `wage_question_frame` IS that polarity reader, so running it over our own output is the
    scorer's own view of it. 'unknown' is the assertion: no lawful cue, no violation cue.
    Every sector is checked, not one — the copy interpolates sub-sector labels, and a future
    label containing 'ni sawa' would reintroduce this on one sector only.
    """
    for copy in (clarification.MIN_WAGE_NO_SECTOR, clarification.MIN_WAGE_NO_AMOUNT,
                 clarification.MIN_WAGE_PERIOD_UNCLEAR,
                 clarification.MIN_WAGE_STATUS_UNCLEAR):
        assert routing.wage_question_frame(copy) == "unknown", copy[:60]
    for sector_no in ws.BY_SECTOR:
        text = rules_engine.sector_rates_statement(sector_no, 250_000).working
        assert routing.wage_question_frame(text) == "unknown", sector_no

    # And the verdict path must still read as a verdict — otherwise this test would pass on
    # a build that had stopped stating verdicts at all.
    assert routing.wage_question_frame(
        rules_engine.compare_to_floor(200_000, 1, 'a', frame="lawful").working) == "lawful"
