# -*- coding: utf-8 -*-
"""Separator resolution in `parse_amounts` — parametrised over the probe corpus.

R17 step 3: the probes are a committed regression file, and this test FAILS when a future
change to the number parser trips one. Each probe carries its own `guards_against`, which
is printed on failure so the reason the row exists is never lost.

The corpus contained ZERO comma-decimal figures when this shipped. That is precisely why
the probes had to be authored: a sweep can only find what the corpus contains.
"""
import json
import pathlib
from decimal import Decimal

import pytest

from chike.swahili_numbers import ambiguous_scale_figures, parse_amounts

PROBES = pathlib.Path(__file__).resolve().parents[1] / \
    "eval/accuracy_gate/decimal_separator_probes_019.jsonl"

ROWS = [json.loads(ln) for ln in PROBES.read_text(encoding="utf-8").splitlines() if ln.strip()]


@pytest.mark.parametrize("row", ROWS, ids=[r["id"] for r in ROWS])
def test_probe_amounts(row):
    got = [Decimal(str(x)) for x in parse_amounts(row["question_sw"])]
    want = [Decimal(x) for x in row["expect_amounts"]]
    assert got == want, (
        f"\n{row['id']} ({row['family']}): {row['question_sw']}"
        f"\n  parsed   {[str(x) for x in got]}"
        f"\n  expected {row['expect_amounts']}"
        f"\n  GUARDS AGAINST: {row['guards_against']}")


@pytest.mark.parametrize("row", ROWS, ids=[r["id"] for r in ROWS])
def test_probe_ambiguity_flag(row):
    got = ambiguous_scale_figures(row["question_sw"])
    assert got == row["expect_ambiguous"], (
        f"\n{row['id']}: {row['question_sw']}"
        f"\n  flagged  {got}"
        f"\n  expected {row['expect_ambiguous']}"
        f"\n  GUARDS AGAINST: {row['guards_against']}")


def test_the_probe_file_covers_both_conventions_and_the_decline():
    """A regression file that only tests one convention would pass the half-fix that
    declines the comma and still guesses the dot."""
    families = {r["family"] for r in ROWS}
    for required in ("comma_decimal", "dot_decimal", "ambiguous_decline",
                     "unchanged_control", "bare_comma_decimal"):
        assert required in families, f"probe corpus lost its {required} rows"
    assert sum(r["family"] == "unchanged_control" for r in ROWS) >= 5, \
        "negatives outnumbering positives is what makes an over-broad fix visible"


def test_a_declined_figure_is_flagged_rather_than_silently_dropped():
    """The two states are indistinguishable in `parse_amounts` alone, and only one of
    them deserves a clarification. If the flag is ever dropped, a user who wrote an
    ambiguous figure gets an answer computed on the OTHER numbers in their question."""
    q = "mishahara ni milioni 1,500 na nina wafanyakazi 12"
    assert Decimal("12") in parse_amounts(q), "the unambiguous figure must survive"
    assert not any(a > 1000 for a in parse_amounts(q)), "the ambiguous figure must not"
    assert ambiguous_scale_figures(q) == ["milioni 1,500"]


def test_the_three_digit_decline_is_scoped_to_scale_words_only():
    """Applying it to bare figures would reread every 'TZS 500,000' in the corpus."""
    assert parse_amounts("TZS 500,000") == [Decimal("500000")]
    assert parse_amounts("milioni 1,500") == []


# --- the decline reaches the USER, not just the parser ------------------------------

def _orch():
    from chike.model_abstraction import FakeBackend
    from chike.orchestrator import Orchestrator
    fake = FakeBackend(scripted_reply="A NUMBER THE MODEL INVENTED")
    return Orchestrator(backend=fake, retriever=lambda q: []), fake


def test_an_unreadable_figure_produces_a_clarification_and_never_calls_the_model():
    """Half a never-guess contract is worse than none. If the parser declines and the
    question goes on without the figure, the model generates free-hand next to a number
    it never received — which is the fabrication the decline was meant to prevent."""
    orch, fake = _orch()
    reply = orch.answer("mishahara jumla ni milioni 1,500 kwa mwezi, SDL ni ngapi")
    assert fake.call_count == 0, "the model must not be asked about a figure we cannot read"
    assert "milioni 1,500" in reply.text, "quote the user's own text back"
    assert "A NUMBER THE MODEL INVENTED" not in reply.text


def test_the_clarification_fires_on_the_fact_route_too():
    """The ambiguity belongs to the question, not the route: the same sentence with a levy
    ask routes to `sdl` and without one routes to `none`. A guard inside the compute path
    only would miss the second."""
    orch, fake = _orch()
    reply = orch.answer("mishahara jumla ni milioni 1,500 kwa mwezi")
    assert fake.call_count == 0
    assert "milioni 1,500" in reply.text


def test_it_names_both_readings_rather_than_picking_the_likelier_one():
    from chike import clarification
    copy = clarification.ambiguous_figure("milioni 1,500")
    assert "1,500,000" in copy and "1,500,000,000" in copy, \
        "naming both readings is what lets the next message resolve it"


def test_a_readable_figure_is_not_intercepted():
    """THE NEGATIVE. The guard sits above the compute/fact fork, so an over-broad
    ambiguity test would silence every computation in the product."""
    orch, fake = _orch()
    reply = orch.answer("nina wafanyakazi 12 mishahara jumla milioni 5,5, SDL ni ngapi")
    assert "192,500" in reply.text, f"expected the SDL working, got: {reply.text}"
    assert "5,500,000" in reply.text, "and computed on the payroll the user actually stated"


def test_naming_the_rate_does_not_stop_the_computation():
    """THE REGRESSION THAT BLOCKED THIS COMMIT, at the level the user experiences it.

    `parse_amounts` returning an extra figure is not itself visible; what is visible is
    that stating the rate you are asking about turns a computed answer into a
    clarification. The parse-level probes (ds_22..ds_24) pin the cause; this pins the
    effect, because the two could be decoupled by a later change to _amount_field.

    The headcount is present because SDL needs it independently — without it BOTH forms
    clarify, and the test would pass while proving nothing.
    """
    orch, _ = _orch()
    with_rate = orch.answer(
        "nina wafanyakazi 12 mishahara jumla TZS 5,000,000, SDL ya 3.5% ni ngapi")
    without = orch.answer(
        "nina wafanyakazi 12 mishahara jumla TZS 5,000,000, SDL ni ngapi")
    assert "175,000" in with_rate.text, \
        f"naming the rate must not cost the computation, got: {with_rate.text}"
    assert "175,000" in without.text, "and the control must still compute"
    assert not with_rate.needs_clarification


def test_the_10x_reading_is_gone_from_the_computed_working():
    """The regression this whole change exists to prevent: 3.5% of the CONCATENATED
    55,000,000 is TZS 1,925,000 — a demand ten times what is owed, presented in the
    deterministic working format that makes it maximally credible."""
    orch, _ = _orch()
    reply = orch.answer("nina wafanyakazi 12 mishahara jumla milioni 5,5, SDL ni ngapi")
    assert "1,925,000" not in reply.text
    assert "55,000,000" not in reply.text
