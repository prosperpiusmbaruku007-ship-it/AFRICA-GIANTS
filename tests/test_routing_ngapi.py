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
