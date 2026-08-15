# -*- coding: utf-8 -*-
"""D-FIDELITY-5 — the obligation denied without a figure.

    A CONTRADICTION DOES NOT NEED A NUMBER.

Every other D-FIDELITY rule compares FIGURES: which amounts the body asserts, and whether the
authoritative one is among them. A body that asserts NOTHING and denies the obligation in words
contradicts a positive engine amount completely, and satisfies all of them VACUOUSLY — the set
being checked is empty. Fourth instance of the presence-not-conclusion family, and the first
where the instrument passes by having nothing to look at.

SEVEN OF TEN ROWS ARE NEGATIVES, because the false-positive surface here is large and real: a
denial is the CORRECT body whenever the engine's amount is zero. Measured before the rule was
designed (scratch/dfid5_sweep.json): `hakuna paye` appears in 10 corpus bodies and ALL TEN are
amount=0 and right. The phrase can never be the discriminator; the engine amount is.
"""
import json
import pathlib
from decimal import Decimal

import pytest

from chike import fidelity
from chike.rules_engine.results import ComputationResult

PROBES = pathlib.Path(__file__).resolve().parents[1] / (
    'eval/fidelity_gate/denial_without_figure_010.jsonl')


def _rows():
    with PROBES.open(encoding='utf-8') as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def _result(row):
    amt = row['authoritative_amount']
    return ComputationResult(
        computation=row['levy'], applicable=True,
        amount=None if amt is None else Decimal(amt),
        working=f"{row['levy'].upper()} = TZS {amt or 0:,}", inputs={}, note='')


@pytest.mark.parametrize('row', _rows(), ids=lambda r: r['id'])
def test_denial_probe(row):
    got = fidelity.body_denies_a_positive_obligation(row['body'], _result(row))
    assert got == row['expect_fire'], (
        f"{row['id']}: expected fire={row['expect_fire']}, got {got}. "
        f"guards_against: {row['guards_against']}")


def test_the_negatives_outnumber_the_positives():
    rows = _rows()
    negs = [r for r in rows if not r['expect_fire']]
    assert len(negs) > len(rows) / 2, (
        'a denial is the CORRECT body whenever the engine amount is zero; the negatives are '
        'the measured risk here')


def test_a_zero_amount_can_never_fire_this_rule():
    """`body_contradicts_working` already owns the amount==0 case, and ten corpus bodies show
    a denial is then faithful. This rule must not reach them."""
    zero = ComputationResult(computation='paye', applicable=True, amount=Decimal(0),
                             working='PAYE = TZS 0', inputs={}, note='')
    for body in ('hakuna PAYE inayokatwa',
                 'hakuna PAYE ya kulipa kwa sababu kiwango cha sifuri kinatumika',
                 'hakuna cha kulipa'):
        assert not fidelity.body_denies_a_positive_obligation(body, zero)


def test_the_denial_must_name_the_computed_levy():
    """A PAYE answer may correctly say 'hakuna SDL' in the same breath. Keyed on any levy this
    rule would blank a correct body, so the pattern is built from result.computation."""
    paye = ComputationResult(computation='paye', applicable=True, amount=Decimal(103000),
                             working='PAYE = TZS 103,000', inputs={}, note='')
    assert not fidelity.body_denies_a_positive_obligation(
        'PAYE ni TZS 103,000. Una wafanyakazi 4, hivyo hakuna SDL.', paye)
    assert fidelity.body_denies_a_positive_obligation(
        'Una wafanyakazi 4, hivyo hakuna PAYE.', paye)


def test_haikatwi_is_not_a_denial_of_liability():
    """`haikatwi` denies the DEDUCTION LOCUS — 'not taken out of the wage' — a TRUE statement
    about who bears SDL. Two corpus bodies say it with a positive amount and both are correct,
    which is why it is absent from the phrase list."""
    sdl = ComputationResult(computation='sdl', applicable=True, amount=Decimal(224000),
                            working='SDL = TZS 224,000', inputs={}, note='')
    assert not fidelity.body_denies_a_positive_obligation(
        'Hii inalipwa na mwajiri peke yake - haikatwi kutoka mshahara wa mfanyakazi.', sdl)


def test_the_other_guards_are_all_blind_to_this_body():
    """The finding, kept executable: this is not a gap in one rule but in what they all check.

    nat_14's body asserts no figure, so the asserted-set is EMPTY and every figure-comparing
    rule is satisfied vacuously.
    """
    body = ('Kama mshahara wake ni TZS 350,000 tu, hakuna PAYE ya kulipa kwa sababu kiwango '
            'cha sifuri kinatumika hadi TZS 270,000.')
    res = ComputationResult(computation='paye', applicable=True, amount=Decimal(6400),
                            working='PAYE = TZS 0 + 8% x (TZS 350,000 - TZS 270,000) '
                                    '= TZS 6,400', inputs={}, note='')
    assert fidelity._asserted_results(body) == set(), 'the body asserts no figure at all'
    assert not fidelity.body_contradicts_working(body, res)
    assert not fidelity.body_reduces_authoritative_amount(body, res)
    assert not fidelity.body_offers_total_as_own_obligation(body, res)
    assert fidelity.body_denies_a_positive_obligation(body, res), (
        'D-FIDELITY-5 is the only rule that sees it')
