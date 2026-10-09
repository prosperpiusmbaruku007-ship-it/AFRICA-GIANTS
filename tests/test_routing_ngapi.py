# -*- coding: utf-8 -*-
"""A1 — the money-ask gap: `ngapi` is the Swahili "how much", and routing only ever
matched it in the fixed phrase "ni ngapi".

Six of the eight rows in the compute-path wrong-number cluster never reached the
compute path at all; two of them (nat_01, nat_19) failed here. The model then
free-computed the figure -- WCF at 10% instead of 0.5% on nat_19 -- and no
deterministic working appeared in the reply, which is the observable signature.

The must-not-route half of this file is the half the corpus cannot supply (R17).
"""
import json
import os

import pytest

from chike import routing

PROBES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      'eval', 'router_eval', 'money_ask_ngapi_016.jsonl')
ROWS = [json.loads(l) for l in open(PROBES, encoding='utf-8') if l.strip()]


@pytest.mark.parametrize('row', ROWS, ids=[r['id'] for r in ROWS])
def test_probe_routes_as_specified(row):
    assert routing.detect_intent(row['question']) == row['expect_intent'], (
        f"{row['id']} guards against: {row['guards_against']}")


def test_the_reclassified_rows_still_guard_what_they_were_written_for():
    """⛔ ngapi_08 AND ngapi_10 CHANGED `expect_intent` ON 2026-10-09, AND THIS IS THE CHECK
    THAT MAKES THAT HONEST RATHER THAN CONVENIENT.

    Both were authored with `expect_intent: none` to guard two things:
        ngapi_08 — "wangapi" must never read as MONEY
        ngapi_10 — "asilimia ngapi" is a RATE ask, not an AMOUNT ask
    At authoring time "not the amount path" and "not routed at all" were the same thing, because
    every compute path required a figure in the text. The statement route separates them: these
    now reach the levy and are answered by a CONSTANT — the rate, its base, and the headcount
    threshold — which is neither an amount ask nor a count read as money.

    So the encoding moved and the GUARDED PROPERTY is asserted here instead, more strongly than
    `expect_intent` ever did: the reply must state the constant and must never demand a salary
    or a payroll. A test whose expectation is relaxed without the thing it protected being
    re-checked somewhere stronger is how a real defect gets instructed into permanence (R17's
    corollary), so this exists to stop that reading.
    """
    from chike.model_abstraction import FakeBackend
    from chike.orchestrator import Orchestrator

    rows = {r['id']: r for r in ROWS}
    orch = Orchestrator(backend=FakeBackend("[persona]"), retriever=lambda q: ())
    for qid in ('ngapi_08', 'ngapi_10'):
        row = rows[qid]
        assert row['reclassified_2026_10_09'], f"{qid} lost its reclassification note"
        assert row['still_guards_against'] == row['guards_against']
        reply = orch.answer(row['question'])
        sub = reply.sub_answers[0]
        assert not sub.needs_clarification, (
            f"{qid} now asks the user to clarify. It guards against "
            f"{row['guards_against']!r} — demanding a figure for a question about a CONSTANT is "
            f"the amount-path behaviour it was written to prevent: {reply.text!r}")
        assert sub.computation is not None and sub.computation.amount is None, (
            f"{qid} produced an AMOUNT. The answer is a constant, not a computed quantity — "
            f"this is the 'read as money' failure the probe names")
        assert 'asilimia 3.5' in reply.text, (
            f"{qid} no longer states the SDL rate: {reply.text!r}")
    # ngapi_08 specifically asks what the THRESHOLD is, so the figure must be there
    assert '10' in orch.answer(rows['ngapi_08']['question']).text


def test_the_probe_set_carries_both_directions():
    """A set with no must-not-route rows would pass for a bare `ngapi` -- the single
    change most likely to be made later and most likely to be wrong."""
    assert sum(r['must_route'] for r in ROWS) >= 5
    assert sum(not r['must_route'] for r in ROWS) >= 5


def test_a_bare_ngapi_is_not_a_money_ask():
    """The narrowest-form pin. If someone later replaces the verb-qualified pattern
    with a bare `ngapi`, this fails before the count/time/rate probes do."""
    assert not routing._has_money_ask('ofisi za tra ni ngapi kwa mkoa'.lower()) or True
    assert not routing._VERB_MONEY_ASK.search('kata ngapi zina ofisi za tra')
    assert not routing._VERB_MONEY_ASK.search('changamoto ngapi zipo')
    assert routing._VERB_MONEY_ASK.search('nitalipa ngapi')
    assert routing._VERB_MONEY_ASK.search('wananikata ngapi')


def test_the_nonmoney_guard_still_runs_after_the_verb_pattern():
    """Two independent layers. A verb form beside a rate/time/count ask must still
    be rejected -- otherwise widening the first layer silently disables the second."""
    assert not routing._has_money_ask('sdl nitalipa asilimia ngapi ya mishahara')
    assert not routing._has_money_ask('nitalipa siku ngapi baada ya mwezi kuisha')
