# -*- coding: utf-8 -*-
"""_WAGE_PAY_CUES — the employee's own side of the minimum-wage question.

th_16 from the other direction. Every cue in `_WAGE_PAY_CUES` was the EMPLOYER speaking or a
THIRD PERSON being paid, so a worker asking whether their OWN wage is lawful fell through to
fact/RAG — while the employer-side twin reached the deterministic route.

WHY THE NEGATIVES MATTER MORE THAN THE MEMBERS HERE. The first version of this list included
the noun `mshahara` and the blast sweep caught it stealing FIVE real gate questions, all GN
605A lookups where nobody is being paid anything. This is the list with a demonstrated history
of over-breadth, so the sweep was treated as mandatory rather than confirmatory, and the
protected rows below are pinned.

THE SWEEP WAS CLEAN AND THAT IS WEAK EVIDENCE, per R17. All 8 intent changes over 5,588
questions were the authored probes themselves; the 5,570 pre-existing corpus rows did not move
at all. That means the corpus does not contain the employee's side of this question — which is
the reason the gap survived, not a reason to trust the change. The probes are the evidence.
"""
import json
import pathlib

import pytest

from chike import routing

PROBES = pathlib.Path(__file__).resolve().parents[1] / (
    'eval/accuracy_gate/wage_pay_concord_018.jsonl')

# The object infix is a CLOSED class. Enumerated from the grammar, not from the cue list —
# a generative test that derives counterparts from existing members is blind to a class at 0%,
# which is how this gap and item C both reached production (finding B).
OBJECT_INFIX = {'ni': 'me (1sg)', 'ku': 'you (2sg)', 'm': 'him/her (cl.1)',
                'tu': 'us (1pl)', 'wa': 'them (cl.2)'}


def _rows():
    with PROBES.open(encoding='utf-8') as f:
        return [json.loads(ln) for ln in f if ln.strip()]


@pytest.mark.parametrize('row', _rows(), ids=lambda r: r['id'])
def test_wage_pay_probe_routes_as_expected(row):
    got = routing.detect_intent(row['question'])
    assert got == row['expected_intent'], (
        f"{row['id']}: expected {row['expected_intent']}, got {got}. "
        f"guards_against: {row['guards_against']}")


@pytest.mark.parametrize('member', sorted(OBJECT_INFIX), ids=lambda m: f'-{m}-')
def test_every_object_infix_member_reaches_the_wage_route(member):
    """The census, applied to the wage route.

    A worker asking about their own pay, with each of the five object-infix members in turn.
    Fails on any member the cue list does not carry — including one nobody has written a cue
    for yet, which is the case a counterpart-derivation test cannot see.
    """
    q = f'wana{member}lipa laki mbili kwa mwezi je ni halali kisheria'
    assert routing.detect_intent(q) == 'minimum_wage', (
        f'object infix -{member}- ({OBJECT_INFIX[member]}) does not reach the wage route')


@pytest.mark.parametrize('form', ['ninalipwa', 'tunalipwa', 'unalipwa', 'nimelipwa',
                                  'nitalipwa', 'nililipwa'])
def test_the_passive_family_carries_first_and_second_person(form):
    """`analipwa`/`wanalipwa`/`walipwa` were 3sg/3pl only — the passive family was at 0% for
    first person, the same absent-coverage shape as `_NSSF_EMPLOYEE_CUES`."""
    assert routing.detect_intent(
        f'{form} laki mbili kwa mwezi je ni halali kisheria') == 'minimum_wage'


def test_the_host_requirement_keeps_the_paid_past_tense_out():
    """`nililipa`/`tulilipa`/`walipa` are 'I/we/they PAID' — a levy statement, no object infix.

    ni+li is a valid host, but the slot after it holds `lipa`, not an infix. This is the
    discriminator that makes host qualification safe, and it is the whole reason the bare
    infix+stem form was rejected.
    """
    for q in ('nililipa PAYE ya laki mbili mwezi uliopita je nilikosea',
              'tulilipa NSSF ya laki tatu mwezi uliopita je ni sahihi',
              'mfanyakazi analipa kodi ya mapato kiasi gani kwa mshahara wa 800000',
              'je ni halali kulipa mfanyakazi laki mbili bila mkataba wa maandishi'):
        assert routing.detect_intent(q) != 'minimum_wage', q


def test_the_five_gate_questions_the_bare_noun_stole_stay_out():
    """Regression pin for the `mshahara` incident: GN 605A LOOKUPS carry a floor term and a
    TZS magnitude while nobody is being paid anything. A pay VERB is what separates them."""
    for q in ('wastani wa mshahara wa chini wa sekta binafsi ulikuwa TZS ngapi kabla ya '
              'GN 605A',
              'kima cha juu kabisa cha mshahara wa chini katika GN 605A ni TZS ngapi'):
        assert routing.detect_intent(q) == 'none', q


def test_the_probe_file_keeps_negatives_and_members_both_represented():
    rows = _rows()
    kinds = {r['kind'] for r in rows}
    assert {'member', 'adversarial_negative', 'protected'} <= kinds
    assert sum(1 for r in rows if r['kind'] != 'member') >= 6, (
        'this list has a demonstrated over-breadth history; negatives must stay substantial')
