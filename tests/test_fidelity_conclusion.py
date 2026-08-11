# -*- coding: utf-8 -*-
"""D-FIDELITY-3 regression — the 18 R17 probes for the conclusion/intermediate-figure family.

WHAT THIS FILE PINS, AND WHY IT LOOKS ODD
-----------------------------------------
Eight of the eighteen rows assert that a body whose conclusion IS WRONG is NOT blanked. CLAUDE.md
R17's corollary warns that "a test which instructs future maintainers not to fix a real defect is
worse than no test", so read this before touching them:

  * `expect_blank` is the PINNED CONTRACT of the guard that ships today. It is not a claim that
    the body is acceptable.
  * `body_is_wrong` is authored ground truth about the text, independent of any guard.
  * Where `body_is_wrong` is true and `expect_blank` is false, the row records an OPEN defect —
    the paraphrase family, where the wrong conclusion is stated without writing the arithmetic
    out. Those rows exist so the open family is enumerated and countable, not forgotten.

  WHEN A FUTURE GUARD CLOSES ONE OF THOSE ROWS, FLIP ITS `expect_blank` TO true AND SAY SO IN
  THE COMMIT. DO NOT DELETE THE ROW. Deleting it destroys the record of what was open and when.

The nine `body_is_wrong: false` rows are the load-bearing half. They are the R17 adversarial
probes: correct answers deliberately written to END on a figure that is legitimately not the
levy — take-home pay, a band component, a worked example about a different base, a monthly
figure annualised. Two of them (neg_01, neg_02) reproduce eval_191 and eval_395 verbatim, the
rows whose protection is the entire reason `body_contradicts_working` is permissive. A widening
that trips any of these is over-broad and must not ship, however clean it looks on the corpus:
the corpus does not contain this vocabulary, which is the whole point of R17.

The rejected alternative is recorded in chike/fidelity.py — a last-asserted-figure rule and its
four cue-based narrowings, each of which relocated a failure rather than removing one.
"""
import json
import pathlib

import pytest

from chike import fidelity

PROBES = pathlib.Path(__file__).resolve().parents[1] / 'eval' / 'fidelity_gate' \
    / 'lastfig_conclusion_018.jsonl'


class _Result:
    """Minimal stand-in: the guard reads .amount, .working and .computation only."""

    def __init__(self, row):
        self.amount = row['authoritative_amount']
        self.working = row['working']
        self.computation = row['levy']


def _rows():
    with PROBES.open(encoding='utf-8') as fh:
        return [json.loads(line) for line in fh if line.strip()]


ROWS = _rows()


def test_probe_file_is_intact():
    """The file is a fixed regression corpus. Rows may be ADDED; the 18 may not be dropped."""
    assert len(ROWS) >= 18
    assert len({r['id'] for r in ROWS}) == len(ROWS), 'duplicate probe ids'
    for r in ROWS:
        assert r['guards_against'].strip(), f"{r['id']} has no guards_against note"
        assert isinstance(r['body_is_wrong'], bool)
        assert isinstance(r['expect_blank'], bool)
        if r['expect_blank']:
            assert r['body_is_wrong'], \
                f"{r['id']}: a correct body must never be pinned as must-blank"


@pytest.mark.parametrize('row', ROWS, ids=[r['id'] for r in ROWS])
def test_conclusion_guard_matches_pinned_contract(row):
    verdict = fidelity.body_reduces_authoritative_amount(row['body'], _Result(row))
    if row['expect_blank']:
        assert verdict, (
            f"{row['id']} REGRESSED: D-FIDELITY-3 no longer catches a defect it shipped "
            f"closing.\n{row['guards_against']}")
    else:
        assert not verdict, (
            f"{row['id']} is now blanked. If body_is_wrong is false this widening is "
            f"OVER-BROAD and must not ship — {row['guards_against']}\n"
            f"If body_is_wrong is true you have CLOSED an open row: flip expect_blank to "
            f"true in {PROBES.name} and say so in the commit.")


_DFID1_FALSE_POSITIVES = {'neg_05_split_total', 'neg_07_threshold_restated'}


@pytest.mark.parametrize('row', [r for r in ROWS if not r['body_is_wrong']],
                         ids=[r['id'] for r in ROWS if not r['body_is_wrong']])
def test_correct_bodies_survive_every_shipping_guard(row):
    """The negatives must survive the WHOLE render-side guard stack, not just the new rule.

    Two of them do NOT, and that is a finding these probes made rather than a defect in them —
    see test_dfidelity1_blanks_two_correct_bodies below. They are excepted here by NAME so the
    exception cannot silently widen to a third.
    """
    result = _Result(row)
    if row['id'] not in _DFID1_FALSE_POSITIVES:
        assert not fidelity.body_contradicts_working(row['body'], result), \
            f"{row['id']}: D-FIDELITY-1 now blanks a CORRECT body — {row['guards_against']}"
    assert not fidelity.body_reduces_authoritative_amount(row['body'], result)


def test_dfidelity1_blanks_two_correct_bodies():
    """A KNOWN, UNFIXED false-positive class in D-FIDELITY-1, pinned so it cannot grow.

    Found by these probes on 2026-08-11, not by the corpus — R17 exactly. The own-levy rule
    tests `amount not in results`, while the SIBLING rule tests `results & _acceptable(result)`.
    The own-levy rule never consults `_acceptable`, so neither the figures the engine's own
    working states nor the employer/employee split sum clear it — even though `_acceptable`'s
    docstring exists to say a faithful NSSF body may legitimately quote either share.

      neg_05  a correct NSSF body quoting only the 20% total     (split sum, in _acceptable)
      neg_07  a correct PAYE body whose trailing figure is the
              Band 4 threshold                                   (in the working itself)

    NOT fixed in the D-FIDELITY-3 commit: aligning the two acceptance sets changes verdicts
    across the recovered-body corpus and needs its own sweep, so it is logged as its own item.
    This test fails if the class GROWS — which is the point — and should be updated to a
    smaller set, never a larger one, when the alignment ships.
    """
    blanked = {r['id'] for r in ROWS
               if not r['body_is_wrong']
               and fidelity.body_contradicts_working(r['body'], _Result(r))}
    assert blanked == _DFID1_FALSE_POSITIVES, (
        f'the D-FIDELITY-1 false-positive class changed: {sorted(blanked)}. '
        f'Growing it means a widening blanked another correct body.')


def test_the_open_family_is_still_enumerated():
    """A count, so shrinking the open family is a visible, deliberate edit.

    This asserts the SIZE of the open set, and it is expected to fail when someone closes a
    row. That failure is the notification, not a defect: update the number in the same commit
    that flips the row, so the paraphrase family can never quietly change size.
    """
    still_open = [r['id'] for r in ROWS if r['body_is_wrong'] and not r['expect_blank']]
    assert len(still_open) == 8, (
        f'open (wrong conclusion, uncaught) rows changed: {sorted(still_open)}. '
        f'If you closed one, flip its expect_blank and update this count.')
