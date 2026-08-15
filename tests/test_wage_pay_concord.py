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
import re

import pytest

from chike import clarification, routing
from chike.rules_engine import wage_schedule

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


# ---------------------------------------------------------------------------
# WHO IS ASKING — the clarification copy addresses somebody
# ---------------------------------------------------------------------------

WORKER_SIDE = [
    ('wananilipa laki mbili kwa mwezi je ni halali kisheria', '-ni- object infix'),
    ('ninalipwa laki moja na nusu kwa mwezi je ni halali kisheria', 'passive 1sg'),
    ('tunalipwa 170000 kwa mwezi sisi walinzi je ni halali', 'passive 1pl'),
    ('wanatulipa 180000 kila mmoja kwa mwezi je ni halali', '-tu- object infix'),
    ('mwajiri ananilipa 150000 kwa mwezi je nakiuka sheria', '-ni- with mwajiri as subject'),
    ('mshahara wangu ni 200000 je ni halali kisheria', 'possessive bound to the OWN wage'),
    ('nimelipwa laki mbili mwezi huu je ni sahihi kisheria', 'passive 1sg perfect'),
]

EMPLOYER_SIDE = [
    ('namlipa mlinzi wangu 200000 kwa mwezi je ni halali kisheria',
     'THE TRAP: `wangu` is present but it is MY GUARD, not my wage'),
    ('nimemlipa mfanyakazi wangu 150000 kwa mwezi je ni halali', 'explicit employer'),
    ('tunawalipa wafanyakazi wetu 180000 je ni halali', 'employer 1pl'),
    ('je ni halali kumlipa mfanyakazi laki mbili kwa mwezi', 'employer infinitive'),
    ('mimi ni mwajiri namlipa mpishi 190000 je ni halali', 'self-declared employer'),
    ('kima cha juu kabisa cha mshahara wa chini katika GN 605A ni TZS ngapi',
     'a LOOKUP — nobody is being paid, and it must not flip the copy'),
    ('unalipwa 190000 je hiyo ni chini ya kima cha chini',
     'BARE 2sg PASSIVE KEEPS THE EMPLOYER DEFAULT. `u-` is also the class 3/11 subject '
     'agreement — `ushuru unalipwa`, `mchango unalipwa`, `umeme unalipwa` — 28 corpus rows, '
     'none of them a person. The genuine 2sg reading is ambiguous anyway, so it takes the '
     'safe default rather than the guess'),
]


@pytest.mark.parametrize('q,why', WORKER_SIDE, ids=[w for _, w in WORKER_SIDE])
def test_worker_side_questions_are_recognised(q, why):
    assert routing.wage_asker_is_worker(q), why


@pytest.mark.parametrize('q,why', EMPLOYER_SIDE, ids=[w for _, w in EMPLOYER_SIDE])
def test_employer_side_questions_keep_the_default(q, why):
    """Employer cues WIN. The predicate flips only on positive worker evidence, never on the
    absence of employer evidence, so an ambiguous question keeps today's behaviour."""
    assert not routing.wage_asker_is_worker(q), why


def test_the_worker_copy_never_calls_the_asker_an_employer():
    """The defect this closes, stated as an assertion.

    Live after the concord fix: an employee asking `ninalipwa ... je ni halali` was answered
    'niambie MFANYAKAZI WAKO anafanya kazi ya aina gani' — tell me what YOUR EMPLOYEE does.
    """
    for text in (clarification.MIN_WAGE_NO_SECTOR_WORKER,
                 clarification.MIN_WAGE_NO_AMOUNT_WORKER):
        assert 'mfanyakazi wako' not in text
        assert 'unaomlipa' not in text


def test_the_two_copies_state_the_same_figures():
    """Only the addressee may differ. If the range is ever corrected it must be corrected in
    both, and this fails the moment they drift apart."""
    figs = re.compile(r'TZS [\d,]+|viwango \d+')
    assert (figs.findall(clarification.MIN_WAGE_NO_SECTOR)
            == figs.findall(clarification.MIN_WAGE_NO_SECTOR_WORKER))


def test_the_copy_figures_match_the_schedule_it_describes():
    """DRIFT PIN, added after the figures were queried and CLEARED.

    `TZS 80,000` is real — sector 4d, 'Other domestic workers', the genuine lowest MONTHLY
    rate in the Order — and `viwango 50` is the row count. CLAUDE.md's '~175,000 (general)'
    and '16 sectors, 46 sub-sectors' count DIFFERENT things (item 16's unlisted-sector rate,
    and BY_SECTOR/SUB_LABELS_SW), so there was never a conflict. But the prose hardcodes
    numbers the schedule owns, so this pins them together.
    """
    monthly = sorted(r[-1] for r in wage_schedule.BY_ROW.values())
    assert f'TZS {monthly[0]:,}' in clarification.MIN_WAGE_NO_SECTOR
    assert f'TZS {monthly[-1]:,}' in clarification.MIN_WAGE_NO_SECTOR
    assert f'viwango {len(wage_schedule.BY_ROW)}' in clarification.MIN_WAGE_NO_SECTOR
    assert wage_schedule.BY_ROW[(16, '')][-1] == 175000, 'item 16 = the unlisted-sector rate'


@pytest.mark.parametrize('q,expect,why', [
    ('wananilipa laki mbili je ni halali', True, '-ni-: nobody pays themselves, so worker'),
    ('wanatulipa laki mbili je ni halali', True, '-tu-: same, 1pl'),
    ('wanakulipa laki mbili je ni halali', True,
     '-ku- with a THIRD-PERSON subject: they pay you, asking on the worker behalf'),
    ('nimekulipa laki mbili je ni halali', False,
     '-ku- with a FIRST-PERSON subject: I have paid YOU — the speaker is the PAYER. The '
     'first version of the predicate flagged this worker, and the generative concord test '
     'is what surfaced it'),
    ('tumekulipa laki mbili je ni halali', False, '-ku- with a 1pl subject: we paid you'),
])
def test_the_ku_object_resolves_on_the_subject_not_the_infix(q, expect, why):
    """The object infix alone does not say who is asking; subject and object together do."""
    assert routing.wage_asker_is_worker(q) == expect, why


@pytest.mark.parametrize('q', [
    'Ushuru wa stempu unalipwa lini — kabla au baada ya kusaini mkataba?',
    'WCF mchango unalipwa TRA au WCF moja kwa moja?',
    'Mtu alisema umeme unalipwa VAT ya asilimia 10 Tanzania. Je, hii ni kweli?',
])
def test_impersonal_u_passive_is_not_a_worker(q):
    """`u-` is the class 3/11 subject agreement as well as 2sg.

    Found by the copy sweep: 28 corpus rows matched `unalipwa` and not one was a person being
    paid — `ushuru`, `mchango`, `umeme` are all class 3/11 nouns. Harmless where it was found
    (the predicate is only consulted on the wage route) and removed anyway, because a wage
    question that happens to mention `ushuru` would have picked up worker copy.
    """
    assert not routing.wage_asker_is_worker(q)
