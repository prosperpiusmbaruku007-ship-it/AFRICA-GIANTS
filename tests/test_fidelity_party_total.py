# -*- coding: utf-8 -*-
"""D-FIDELITY-4 — the cross-party total offered as the asker's own obligation.

R17 step 3: the probes are committed as a regression file with a `guards_against` note per
row, and this test FAILS when a future change trips one. Ten of the thirteen rows are
NEGATIVES — three of them real stored generations that are CORRECT bodies — because the
measured danger here is not the miss, it is the over-broad fire: the obvious
presence-of-the-total rule was 4-for-1 against on the corpus.

The finding this guard records, and the reason it is a new rule rather than a widening:

    `body_contradicts_working` is a SET-MEMBERSHIP check, not a CONCLUSION check.

It asks whether the authoritative figure is AMONG the figures the body asserts, never whether
it is the one the body concludes with. nat_08 stated the correct share twice and led with the
total, and satisfied it.
"""
import json
import pathlib
from decimal import Decimal

import pytest

from chike import fidelity
from chike.rules_engine.results import ComputationResult

PROBES = pathlib.Path(__file__).resolve().parents[1] / (
    'eval/fidelity_gate/party_total_obligation_013.jsonl')


def _rows():
    with PROBES.open(encoding='utf-8') as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def _result(row):
    """Rebuild the ComputationResult the body was generated against.

    `cross_party_total` is None for the two rows that deliberately cannot yield a total (a
    party=total question, and a result carrying no rates), so those keep their own inputs.
    """
    inputs = {'party': row['party']}
    if row['cross_party_total'] is not None:
        inputs['employer_rate'] = Decimal('0.10')
        inputs['employee_rate'] = Decimal('0.10')
    if row['id'] == 'adv_01_total_question_untouched':
        inputs = {'party': 'total', 'employer_rate': Decimal('0.10'),
                  'employee_rate': Decimal('0.10')}
    if row['id'] == 'adv_06_no_rates_no_fire':
        inputs = {'party': 'employee'}
    return ComputationResult(
        computation=row['levy'], applicable=True,
        amount=Decimal(row['authoritative_amount']),
        working=f"{row['levy'].upper()} = TZS {row['authoritative_amount']:,}",
        inputs=inputs, note=f"party={inputs['party']}")


@pytest.mark.parametrize('row', _rows(), ids=lambda r: r['id'])
def test_party_total_obligation_probe(row):
    got = fidelity.body_offers_total_as_own_obligation(row['body'], _result(row))
    assert got == row['expect_fire'], (
        f"{row['id']}: expected fire={row['expect_fire']}, got {got}. "
        f"guards_against: {row['guards_against']}")


def test_the_probe_file_keeps_its_negatives_in_the_majority():
    """A guard whose regression file is mostly positives has stopped testing over-breadth.

    The measured risk for this rule is the false fire: three CORRECT stored bodies state the
    cross-party total, and a presence-keyed rule would blank all three.
    """
    rows = _rows()
    negatives = [r for r in rows if not r['expect_fire']]
    assert len(negatives) > len(rows) / 2, 'negatives must outnumber positives'
    assert any(r['source'].startswith('real stored') for r in negatives), (
        'at least one negative must be a REAL stored generation, not only authored probes')


def test_a_total_question_can_never_reach_this_guard():
    """The precondition is the whole safety argument.

    Firing only when a SPECIFIC party was resolved is what keeps this clear of the
    permissiveness `body_contradicts_working` is measured onto — and what excludes the two
    correct `utalipa TZS 50,000` bodies that a generic connector widening would have blanked
    (scratch/dfid4_connector_sweep.json).
    """
    total_result = ComputationResult(
        computation='nssf', applicable=True, amount=Decimal('100000'),
        working='NSSF = 20% x TZS 500,000 = TZS 100,000',
        inputs={'party': 'total', 'employer_rate': Decimal('0.10'),
                'employee_rate': Decimal('0.10')}, note='party=total')
    assert fidelity.cross_party_total(total_result) is None
    assert not fidelity.body_offers_total_as_own_obligation(
        'kwa TZS 500,000 utalipa TZS 50,000 kwa upande wa mwajiri na TZS 50,000 kwa '
        'upande wa mfanyakazi', total_result)


def test_the_total_is_computed_from_the_engine_rates_not_assumed_to_be_double():
    """A hard-coded 2x would produce a wrong total the day the rates diverge.

    The sweep instrument DID assume 2x and immediately collided with a per-employee salary
    that happened to equal it. Rates are read from `inputs`; asymmetric rates must follow.
    """
    asymmetric = ComputationResult(
        computation='nssf', applicable=True, amount=Decimal('60000'),
        working='NSSF (sehemu ya mfanyakazi) = 6% x TZS 1,000,000 = TZS 60,000',
        inputs={'party': 'employee', 'employer_rate': Decimal('0.14'),
                'employee_rate': Decimal('0.06')}, note='party=employee')
    assert fidelity.cross_party_total(asymmetric) == 200000
    assert fidelity.body_offers_total_as_own_obligation(
        'unapaswa kulipa TZS 200,000', asymmetric)
    assert not fidelity.body_offers_total_as_own_obligation(
        'unapaswa kulipa TZS 120,000', asymmetric), 'a bare doubling must not be what fires'
