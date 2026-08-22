# -*- coding: utf-8 -*-
"""D-FIDELITY-6 — wrong statutory rate for a levy (2026-08-22).

Specified by nat_24's live WCF body ("10% ... kwa ajili ya WCF"), which three existing
mechanisms all missed. The authored probes are the load-bearing half: 12 of the 16 are CORRECT
bodies written to break an over-broad version, and two of them already have — a nearest-wins
attribution rule and a proximity-only rule were both killed by probes here before the guard was
written into chike/fidelity.py.
"""
import json
import os

import pytest

from chike import fidelity

PROBES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      'eval', 'fidelity', 'rate_guard_probes.jsonl')


def _probes():
    with open(PROBES, encoding='utf-8') as f:
        rows = [json.loads(line) for line in f if line.strip()]
    assert rows, 'probe file is empty — this test would otherwise pass vacuously'
    return rows


PROBE_ROWS = _probes()


@pytest.mark.parametrize('probe', PROBE_ROWS, ids=[p['id'] for p in PROBE_ROWS])
def test_authored_rate_probes(probe):
    got = 'flag' if fidelity.body_states_wrong_levy_rate(probe['body']) else 'clean'
    assert got == probe['expect'], (
        f"{probe['id']} expected {probe['expect']}, got {got}. "
        f"guards_against: {probe['guards_against']}")


def test_the_live_defect_that_specified_this_guard():
    """nat_24, verbatim from the 2026-08-22 canary."""
    body = ('Kwa mujibu wa taarifa ulizonipa, unatakiwa kulipa 10% ya jumla ya mishahara '
            'kwa ajili ya WCF. Thibitisha na WCF (wcf.go.tz).')
    assert fidelity.body_states_wrong_levy_rate(body)


def test_needs_no_computation_result():
    """The whole point: it reaches the case every figure-comparing rule cannot.

    nat_24's WCF sub-answer was an applicability verdict with amount=None, which made
    D-FIDELITY-1/2/3/5 vacuous. This rule compares against the STATUTE, not against a working.
    """
    import inspect
    sig = inspect.signature(fidelity.body_states_wrong_levy_rate)
    assert list(sig.parameters) == ['body']


def test_a_preceding_levy_beats_a_nearer_following_one():
    """rg_01's rule, pinned: nearest-wins flagged a correct three-levy breakdown."""
    body = 'SDL ni asilimia 3.5 ya jumla ya mishahara, NSSF ni asilimia 20, na WCF ni asilimia 0.5.'
    assert not fidelity.body_states_wrong_levy_rate(body)
    assert dict(fidelity.attributed_levy_rates(body)).keys() >= {'sdl', 'nssf', 'wcf'}


def test_an_explicit_attachment_beats_a_stray_preceding_levy():
    """Found in real output: a leftover 'fidia' captured NSSF's correct 10%."""
    body = ('unapaswa kulipa asilimia 0.5% ya jumla ya mishahara kwa ajili ya mafunzo ya '
            'fidia, pamoja na asilimia 10% kwa ajili ya NSSF.')
    pairs = fidelity.attributed_levy_rates(body)
    assert ('nssf', __import__('decimal').Decimal('10')) in pairs


def test_contrast_clauses_are_not_the_bodys_own_claim():
    """The 18%-substring false-PASS precedent, one layer down."""
    assert not fidelity.body_states_wrong_levy_rate(
        'WCF ni asilimia 0.5 ya mishahara, si asilimia 10 kama NSSF.')


def test_zero_is_lawful_for_every_levy():
    """A non-liability claim is D-FIDELITY-5's business, not this rule's.

    Caught as the sweep's only false positive on real output: nat_24's live reply says
    'unatakiwa kulipa asilimia 0% ya SDL kwa kuwa una chini ya wafanyakazi 10', which is
    correct.
    """
    for levy in ('SDL', 'NSSF', 'WCF', 'PAYE'):
        assert not fidelity.body_states_wrong_levy_rate(f'{levy} ni asilimia 0.')


def test_a_body_with_no_levy_mention_is_never_flagged():
    assert not fidelity.body_states_wrong_levy_rate('Kiwango ni asilimia 47 ya kitu fulani.')
