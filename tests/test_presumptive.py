# -*- coding: utf-8 -*-
"""Presumptive income tax — the first route added to close a COVERAGE gap, not a wrong answer.

THE STATUTE IS THE ORACLE, AND THE CONSOLIDATED STATUTE IS NOT THE STATUTE. Every figure
asserted here comes from the Income Tax Act Cap 332 First Schedule para 2(3) AS SUBSTITUTED BY
the Finance Act 2022 (Act No. 5 of 2022) s.72(a)(ii). The R.E. 2019 consolidation still prints
the pre-2022 five-band table, and reaching for it — the natural thing to do, since it is the
Act — gives a different answer for every turnover above TZS 11,000,000.
`test_the_stale_consolidated_table_would_have_been_wrong` keeps that live rather than in a
comment, because a comment cannot fail.

The 20 authored probes are the load-bearing instrument here and not a ritual: the 5,595-row
sweep produced ZERO intent changes after narrowing, which is R17's own warning in its purest
form — the corpus was written before this domain existed and cannot exercise it.
"""
import json
import pathlib
from decimal import Decimal

import pytest

from chike import clarification, routing
from chike.rules_engine import rates
from chike.rules_engine.presumptive import compute_presumptive, records_status_matters

PROBES = pathlib.Path(__file__).resolve().parents[1] / (
    'eval/accuracy_gate/presumptive_tax_probes_020.jsonl')


def _rows():
    with PROBES.open(encoding='utf-8') as f:
        rows = [json.loads(ln) for ln in f if ln.strip()]
    # NON-EMPTY ASSERTION (2026-08-22, dead-anchor census) — see test_minimum_wage._probes.
    # This one also feeds a @parametrize, where an empty list yields ZERO test cases.
    assert rows, f"{PROBES} is empty — the tests looping over it would pass vacuously"
    return rows


@pytest.mark.parametrize('row', _rows(), ids=lambda r: r['id'])
def test_probe_routes_as_specified(row):
    got = routing.detect_intent(row['question'])
    assert got == row['expect_intent'], (
        f"{row['id']}: expected {row['expect_intent']}, got {got}. "
        f"guards_against: {row['guards_against']}")


# --- the statutory table, cell by cell ------------------------------------------------
# (annual_turnover, keeps_records, expected_amount)
_STATUTORY_CELLS = [
    (0, False, 0), (0, True, 0),
    (4_000_000, False, 0), (4_000_000, True, 0),            # "does not exceed" — inclusive
    (4_000_001, False, 100_000),
    (5_000_000, True, 30_000),                              # 3% x (5,000,000 - 4,000,000)
    (7_000_000, False, 100_000),
    (7_000_000, True, 90_000),                              # 3% x 3,000,000
    (7_000_001, False, 250_000),
    (9_000_000, True, 150_000),                             # 90,000 + 3% x 2,000,000
    (11_000_000, False, 250_000),
    (11_000_000, True, 210_000),                            # 90,000 + 3% x 4,000,000
    (11_000_001, False, 385_000),                           # 3.5% of FULL turnover
    (11_000_001, True, 385_000),
    (30_000_000, False, 1_050_000), (30_000_000, True, 1_050_000),
    (100_000_000, True, 3_500_000),
]


@pytest.mark.parametrize('turnover,records,expected', _STATUTORY_CELLS)
def test_every_cell_of_the_statutory_table(turnover, records, expected):
    result = compute_presumptive(turnover, records)
    assert result.applicable is True
    assert result.amount == Decimal(expected), result.working


def test_the_stale_consolidated_table_would_have_been_wrong():
    """Cap 332 R.E. 2019 prints an 11,000,001-14,000,000 band and a 14,000,001-100,000,000
    band at 450,000 + 3.5% OF THE EXCESS. FA2022 replaced both with 3.5% of turnover.

    Kept executable because the failure mode is silent: both tables are 'the statute', both
    look authoritative, and only the amending Act distinguishes them.
    """
    stale_at_50m = Decimal("450000") + Decimal("0.035") * (Decimal("50000000")
                                                           - Decimal("14000000"))
    assert stale_at_50m == Decimal("1710000")
    assert compute_presumptive(50_000_000, True).amount == Decimal("1750000")
    assert compute_presumptive(50_000_000, True).amount != stale_at_50m

    stale_at_12m = Decimal("230000") + Decimal("0.03") * (Decimal("12000000")
                                                          - Decimal("11000000"))
    assert stale_at_12m == Decimal("260000")
    assert compute_presumptive(12_000_000, True).amount == Decimal("420000")


def test_above_the_ceiling_presumptive_does_not_apply():
    result = compute_presumptive(100_000_001, True)
    assert result.applicable is False and result.amount is None
    assert "100,000,000" in result.working


def test_an_excluded_professional_is_outside_the_regime_whatever_the_turnover():
    """A professional told they owe presumptive tax gets a wrong answer carrying the engine's
    authority — and wrong in the dangerous direction, since they are taxed on the ordinary
    individual rates instead."""
    for turnover in (3_000_000, 9_000_000, 60_000_000):
        result = compute_presumptive(turnover, True, excluded_service=True)
        assert result.applicable is False and result.amount is None


def test_the_records_axis_matters_only_between_4m_and_11m():
    """The window is the whole justification for withholding the records clarification
    elsewhere. If this ever widens, the orchestrator would start answering with a default."""
    assert not records_status_matters(4_000_000)
    assert records_status_matters(4_000_001)
    assert records_status_matters(11_000_000)
    assert not records_status_matters(11_000_001)
    for turnover in (1_000_000, 4_000_000, 11_000_001, 40_000_000):
        assert (compute_presumptive(turnover, True).amount
                == compute_presumptive(turnover, False).amount), turnover
    for turnover in (5_000_000, 9_000_000):
        assert (compute_presumptive(turnover, True).amount
                != compute_presumptive(turnover, False).amount), turnover


def test_unstated_records_is_never_silently_read_as_no_records():
    """The no-records column is the EXPENSIVE one at low turnover (TZS 100,000 against TZS
    30,000 at 5M). A default would overstate the bill for the trader least able to check it."""
    assert routing.keeps_records("mauzo yangu ni milioni 5 kwa mwaka") is None
    assert routing.keeps_records("mauzo yangu ni milioni 5, natunza kumbukumbu") is True
    assert routing.keeps_records("mauzo yangu ni milioni 5, situnzi kumbukumbu") is False


def test_the_transport_schedule_is_vetoed_rather_than_answered_wrongly():
    """para 2(5) is a per-vehicle table this engine does not implement. The corpus row that
    exposed it quotes TZS 250,000 — a TAX figure — and computing on it returns TZS 0."""
    q = ("Chike, hii 'presumptive tax rate class a' kwa magari ya abiria inayosema "
         "TZS 250,000 inamaanisha nini kwangu kama mmiliki wa daladala?")
    assert routing.detect_intent(q) == 'none'
    assert compute_presumptive(250_000, False).amount == Decimal(0), (
        'the wrong answer this veto prevents')


def test_mapato_is_not_mauzo():
    """`mapato` can mean profit; the bands run on turnover. 3.5% of profit is not 3.5% of
    turnover, so the presumptive ownership gate takes turnover vocabulary only — unlike the
    VAT arm's, which is deliberately NOT reused here."""
    assert "mapato yangu" in routing._OWN_TURNOVER_CUES
    assert "mapato yangu" not in routing._PRESUMPTIVE_TURNOVER_CUES


def test_the_clarification_copy_never_states_a_figure_it_has_not_computed():
    """A clarification says what is missing. The moment it volunteers a shilling amount it is
    answering, and it is answering without the input it just said it needed — which is the
    `body volunteers a figure where the engine declined` family already on the board."""
    import re as _re
    allowed = {'100,000,000'}                       # the statutory ceiling, structural only
    for copy in (clarification.PRESUMPTIVE_NO_TURNOVER,
                 clarification.PRESUMPTIVE_PERIOD_IS_A_RATE,
                 clarification.PRESUMPTIVE_NO_RECORDS_STATUS):
        figures = set(_re.findall(r'\d[\d,]{3,}', copy))
        assert figures <= allowed, f'clarification states an uncomputed figure: {figures}'
    # And each must name the thing it is asking for, or the user cannot answer it.
    assert 'mauzo' in clarification.PRESUMPTIVE_NO_TURNOVER.lower()
    assert 'mwaka' in clarification.PRESUMPTIVE_PERIOD_IS_A_RATE.lower()
    assert 'kumbukumbu' in clarification.PRESUMPTIVE_NO_RECORDS_STATUS.lower()


def test_rates_table_matches_the_finance_act_2022_shape():
    """Four bands, ceiling 100M. The pre-2022 table had five."""
    assert len(rates.PRESUMPTIVE_BANDS) == 4
    assert rates.PRESUMPTIVE_TURNOVER_CEILING == Decimal("100000000")
    uppers = [b[0] for b in rates.PRESUMPTIVE_BANDS]
    assert uppers == sorted(uppers), 'bands must be in ascending order for the lookup to work'
    assert Decimal("14000000") not in uppers, (
        'a 14,000,000 boundary means the STALE R.E.2019 table has been re-encoded')


# --- end to end, no model -----------------------------------------------------------
# The genitive-period bug is the reason these exist: `turnover_period` matched only
# `kwa mwaka` and not `ya mwaka`, every affected row ROUTED correctly, and the defect was
# invisible to the router sweep because it lived in the NEXT stage. A stage-level check
# cannot see a stage-level gap.

def test_the_presumptive_path_never_calls_the_model():
    """An engine answer is immune to whatever the fact path is doing wrong — but only if no
    generation is on the path. One model call means that property is gone."""
    from chike.model_abstraction import FakeBackend
    from chike.orchestrator import Orchestrator
    for row in _rows():
        if row['expect_intent'] != 'presumptive':
            continue
        fake = FakeBackend(scripted_reply="MODEL TEXT THAT MUST NOT APPEAR")
        orch = Orchestrator(backend=fake, retriever=lambda q: [])
        reply = orch.answer(row['question'])
        assert fake.call_count == 0, row['id']
        assert "MODEL TEXT THAT MUST NOT APPEAR" not in reply.text, row['id']


@pytest.mark.parametrize('row', [r for r in _rows() if 'expect_amount' in r],
                         ids=lambda r: r['id'])
def test_the_figure_actually_reaches_the_reply(row):
    from chike.model_abstraction import FakeBackend
    from chike.orchestrator import Orchestrator
    orch = Orchestrator(backend=FakeBackend(scripted_reply="X"), retriever=lambda q: [])
    reply = orch.answer(row['question'])
    assert f"{row['expect_amount']:,}" in reply.text, (
        f"{row['id']}: {row['expect_amount']:,} missing from -> {reply.text}")


@pytest.mark.parametrize('row', [r for r in _rows() if r.get('expect_clarifies')],
                         ids=lambda r: r['id'])
def test_the_clarifying_probes_clarify_and_state_no_amount(row):
    from chike.model_abstraction import FakeBackend
    from chike.orchestrator import Orchestrator
    orch = Orchestrator(backend=FakeBackend(scripted_reply="X"), retriever=lambda q: [])
    reply = orch.answer(row['question'])
    assert reply.sub_answers[0].needs_clarification is True, row['id']
    # pt_14's annualised figure (2M x 12 = 24M -> 840,000) must not appear anywhere.
    assert "840,000" not in reply.text, row['id']


@pytest.mark.parametrize('row', [r for r in _rows() if r.get('expect_applicable') is False],
                         ids=lambda r: r['id'])
def test_the_not_applicable_probes_state_no_amount(row):
    from chike.model_abstraction import FakeBackend
    from chike.orchestrator import Orchestrator
    orch = Orchestrator(backend=FakeBackend(scripted_reply="X"), retriever=lambda q: [])
    reply = orch.answer(row['question'])
    assert "Hapana" in reply.text, row['id']


# --- a PRE-EXISTING defect this route walked into, recorded rather than absorbed ---------

@pytest.mark.xfail(strict=True, reason=(
    "PRE-EXISTING decomposition defect, confirmed on pristine HEAD (05e68b5) and NOT caused "
    "by the presumptive route. When this starts passing, someone has fixed decomposition: "
    "delete the marker, do not delete the test."))
def test_the_comma_enumeration_split_corrupts_this_question():
    """`decompose_query` turns

        'Mauzo yangu ya mwaka ni milioni 9, sina kumbukumbu za mahesabu. Kodi ya makadirio?'

    into TWO fragments, of which the second is text the user never wrote —
    'Mauzo yangu ya mwaka ni milioni sina kumbukumbu' — while 'Kodi ya makadirio?', the
    actual question, DISAPPEARS. The unit preamble ('milioni') is carried onto a comma
    clause that is not an enumeration item.

    This is worse than the documented preamble-drop: it does not merely lose a sub-question,
    it FABRICATES one. The PAYE and SDL analogues ('Mshahara wangu ni 900000, sina mkataba
    wa ajira. PAYE ni ngapi?') are untouched, so the trigger is narrow.
    """
    from chike import decomposition
    q = ("Mauzo yangu ya mwaka ni milioni 9, sina kumbukumbu za mahesabu. "
         "Kodi ya makadirio?")
    parts = decomposition.decompose_query(q)
    joined = " ".join(parts)
    assert "sina kumbukumbu za mahesabu" in joined, 'the records clause was mangled'
    assert "Kodi ya makadirio" in joined, 'the actual question was dropped'
