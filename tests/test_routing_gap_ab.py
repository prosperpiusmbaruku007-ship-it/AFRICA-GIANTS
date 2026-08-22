# -*- coding: utf-8 -*-
"""ROUTING-GAP-A and ROUTING-GAP-B — regression guards (2026-08-22).

R17 step 3: the authored probes are committed as a regression file
(eval/routing/nickname_probes.jsonl, with a `guards_against` note per row) and wired to a test
that FAILS when a future cue addition trips one.

The negative controls are the load-bearing half. Gap C (relaxing the `_has_number` gate) was
measured to be unsafe precisely because it would capture nick_15 and nick_16 — a training-as-a-
service question and a compensation-claim question, both of which merely CONTAIN a levy cue
word. Those two are the reason gap C stayed shut, so they are asserted here rather than left
as prose in a PROGRESS entry.
"""
import json
import os

import pytest

from chike import routing

PROBES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      'eval', 'routing', 'nickname_probes.jsonl')


def _probes():
    with open(PROBES, encoding='utf-8') as f:
        rows = [json.loads(line) for line in f if line.strip()]
    assert rows, 'probe file is empty — this test would otherwise pass vacuously'
    return {r['id']: r for r in rows}


PROBE = _probes()


def _q(pid):
    return PROBE[pid]['question']


# --- GAP A: the fan-out can now see nicknamed levies -------------------------

@pytest.mark.parametrize('pid, expected', [
    ('nick_04', ['nssf', 'sdl']),          # nat_23 verbatim: "ile ya mafunzo na ile ya uzeeni"
    ('nick_11', ['sdl', 'wcf']),           # "ile ya mafunzo na ile ya fidia"
])
def test_nicknamed_multi_levy_questions_enumerate_every_levy(pid, expected):
    """Before this change all_compute_levies did not exist and the fan-out used
    all_explicit_levies, which returns [] for nicknames — so nat_23 computed NSSF correctly
    and dropped SDL silently, live, on the deployed pipeline."""
    assert routing.all_compute_levies(_q(pid)) == expected


def test_explicit_levy_questions_are_byte_identical_to_before():
    """A question naming its levies outright must produce exactly the list it did before
    all_compute_levies existed — explicit names lead, so this ordering is preserved."""
    q = _q('nick_05')                       # "...kwenye SDL na NSSF"
    assert routing.all_compute_levies(q) == routing.all_explicit_levies(q) == ['sdl', 'nssf']


def test_single_levy_questions_do_not_fan_out():
    for pid in ('nick_08', 'nick_09', 'nick_10'):
        assert len(routing.all_compute_levies(_q(pid))) == 1


# --- GAP B: the ask-shape gates recognise real asks --------------------------

@pytest.mark.parametrize('pid, expected_intent', [
    ('nick_02', 'sdl'),    # "je nalipa ile ya mafunzo"  — nicknamed
    ('nick_03', 'sdl'),    # "je nalipa SDL"             — EXPLICIT, and it missed too
    ('nick_06', 'nssf'),   # nat_24: "nilipe nini kati ya ... na ..."
    ('nick_07', 'sdl'),    # nat_05: "asilimia tatu na nusu ya nini"
])
def test_gap_b_ask_shapes_now_reach_compute(pid, expected_intent):
    assert routing.detect_intent(_q(pid)) == expected_intent


def test_gap_b_is_not_a_nickname_gap():
    """nick_03 names SDL outright and still routed to fact before this change.

    This is the assertion that keeps the workstream honestly framed: calling it 'nicknamed
    multi-levy decomposition' would have fixed gap A and left this untouched."""
    q = _q('nick_03')
    assert routing._explicit_levy(q.lower()) == 'sdl'
    assert routing._natural_levy(q.lower()) is None      # no nickname involved at all
    assert routing.detect_intent(q) == 'sdl'


# --- NEGATIVE CONTROLS: the R17 probes that keep gap C shut ------------------

@pytest.mark.parametrize('pid', ['nick_13', 'nick_14', 'nick_15', 'nick_16'])
def test_adversarial_and_negative_controls_stay_off_the_compute_path(pid):
    """These MUST stay 'none'.

    nick_15 contains 'mafunzo' meaning TRAINING AS A SERVICE, and nick_16 contains 'fidia'
    meaning a COMPENSATION CLAIM. Both resolve a levy cue and are held off compute only by the
    `_has_number` gate. Relaxing that gate — the obvious fix for the number-free probes — was
    measured to capture both, which is why gap C stayed shut. If a future change makes either
    of these route to compute, that change is over-broad and this test is the alarm.
    """
    assert routing.detect_intent(_q(pid)) == 'none', (
        f"{pid} reached the compute path: {PROBE[pid].get('guards_against', '')}")


def test_gap_c_number_gate_is_still_shut():
    """The number requirement on paths 2/2b is load-bearing, not incidental."""
    for pid in ('nick_01', 'nick_12', 'nick_15', 'nick_16'):
        ql = _q(pid).lower()
        assert not routing._has_number(ql), f'{pid} unexpectedly carries a number'
        assert routing.detect_intent(_q(pid)) == 'none'


# --- the sweep's own blast radius, pinned ------------------------------------

def test_gap_b_cue_list_is_separately_addressable():
    """_GAP_B_APPLICABILITY_CUES must stay a distinct list that a sweep can subtract.

    The first version of the blast-radius sweep inlined these cues and therefore could not
    switch them off, reporting a zero blast radius for this form — a false clean sweep. Keeping
    the set separately named is what makes the before-state reconstructable.
    """
    assert routing._GAP_B_APPLICABILITY_CUES
    for cue in routing._GAP_B_APPLICABILITY_CUES:
        assert cue in routing._APPLICABILITY_CUES
        assert cue.startswith('je '), 'gap B cues are question-particle qualified by design'
