# -*- coding: utf-8 -*-
"""D-FIDELITY-2 — a compute body volunteering a WRONG figure for a SIBLING levy.

R17: a sweep can only find what the corpus contains. The corpus routes only NINE questions to
two or more compute levies, and the cross-levy sweep flags exactly two of them (eval_318,
eval_320) with zero false positives — which is nowhere near enough evidence on its own. The
MUST-NOT-BLANK probes below are therefore written to CONTAIN the risky shapes in a FAITHFUL
body, because blanking a good body is this guard's real failure mode: it silently deletes the
model's Swahili explanation and leaves the user a bare calculation.

`nssf_total_when_engine_holds_the_share` is the one that changed the code. NSSF's authoritative
`amount` is the employee share in a per-employee framing (eval_320) and the 20% total in a
payroll framing (eval_318), so a faithful body quoting the total would have been blanked by the
first version of the detector. `_acceptable` exists for that row.
"""
import dataclasses
from decimal import Decimal

import pytest

from chike import fidelity
from chike.orchestrator import Orchestrator, SubAnswer
from chike.model_abstraction import ModelBackend
from chike.rules_engine.results import ComputationResult


def _r(computation, amount, working, applicable=True):
    return ComputationResult(computation=computation, applicable=applicable,
                             amount=None if amount is None else Decimal(amount),
                             working=working)


# The two real sibling sets, taken from what the engine actually produces for these rows.
SDL_NOT_APPLICABLE = _r(
    'sdl', None,
    'SDL inayolipwa ni TZS 0. Una wafanyakazi 1 (chini ya 10); SDL inahusu waajiri wenye '
    'wafanyakazi 10 au zaidi, hivyo jumla ya mishahara haibadilishi jibu.',
    applicable=False)
NSSF_SHARE = _r('nssf', 80000,
                'NSSF (sehemu ya mfanyakazi) = 10% × TZS 800,000 = TZS 80,000 — jumla ya NSSF '
                'ni 20% (mwajiri TZS 80,000 + mfanyakazi TZS 80,000)')
PAYE_78K = _r('paye', 78000,
              'PAYE = TZS 68,000 + 25% × (TZS 800,000 − TZS 760,000) = TZS 78,000')
WCF_4K = _r('wcf', 4000, 'WCF = 0.5% × TZS 800,000 = TZS 4,000')
NSSF_TOTAL = _r('nssf', 1100000,
                'NSSF = 20% × TZS 5,500,000 = TZS 1,100,000 (mwajiri TZS 550,000 + '
                'mfanyakazi TZS 550,000)')
SDL_192K = _r('sdl', 192500, 'SDL = 3.5% × TZS 5,500,000 = TZS 192,500')

ONE_EMPLOYEE = {'sdl': SDL_NOT_APPLICABLE, 'nssf': NSSF_SHARE, 'paye': PAYE_78K, 'wcf': WCF_4K}
ELEVEN_EMPLOYEES = {'sdl': SDL_192K, 'nssf': NSSF_TOTAL}


# (id, body, siblings, guards_against)
MUST_NOT_BLANK = [
    ('faithful_restates_all',
     'Kwa mfanyakazi mmoja: SDL haitozwi (TZS 0), NSSF = TZS 80,000, PAYE = TZS 78,000, '
     'WCF = TZS 4,000.',
     ONE_EMPLOYEE,
     'a body that restates every sibling CORRECTLY is the normal good case'),

    ('nssf_total_when_engine_holds_the_share',
     'NSSF kwa jumla = TZS 160,000 kwa mwezi.',
     {'nssf': NSSF_SHARE},
     'engine amount is the EMPLOYEE SHARE (80,000); the 20% TOTAL is equally correct and the '
     'working spells out the split that sums to it'),

    ('nssf_share_when_engine_holds_the_total',
     'Sehemu ya mwajiri: NSSF = TZS 550,000.',
     {'nssf': NSSF_TOTAL},
     'mirror image — engine amount is the TOTAL; a half stated in the working is not a '
     'contradiction'),

    ('sibling_named_without_a_figure',
     'SDL haitozwi kwa mwajiri mwenye wafanyakazi chini ya 10. Hii ni kanuni ya TRA.',
     ONE_EMPLOYEE,
     'naming a levy with NO attributed figure must never flag'),

    ('not_applicable_stated_as_zero',
     'SDL: TZS 0 — hauzwi kwa mfanyakazi mmoja.',
     ONE_EMPLOYEE,
     'TZS 0 is the FAITHFUL figure for a not-applicable levy'),

    ('rate_without_amount',
     'Kiwango cha SDL ni asilimia 3.5 na cha WCF ni asilimia 0.5.',
     ONE_EMPLOYEE,
     'percentages are not attributed TZS figures'),

    ('sibling_base_quoted_with_result',
     'NSSF ya mishahara ya TZS 5,500,000: TZS 1,100,000 kwa mwezi.',
     ELEVEN_EMPLOYEES,
     'the payroll BASE appears after the levy name; the correct result is also present'),

    ('own_levy_band_intermediates',
     'PAYE = TZS 68,000 + 25% × (TZS 800,000 − TZS 760,000) = TZS 78,000. NSSF = TZS 80,000.',
     {'nssf': NSSF_SHARE},
     'band bases and intermediate figures in the body must not be read as sibling results'),
]

MUST_BLANK = [
    ('eval_320_sdl_asserted_for_one_employee',
     'PAYE (TZS 800,000, 8%): TZS 64,000. WCF (0.5%): TZS 4,000. '
     'SDL (3.5%, wafanyakazi ≥10): TZS 28,000.',
     ONE_EMPLOYEE,
     'THE ROW THIS GUARD EXISTS FOR — SDL charged to a ONE-employee payroll, colon-attributed '
     'with no multiplication shown'),

    ('eval_318_nssf_off_by_a_factor_of_ten',
     'Kwa SDL: TZS 5,500,000 × 3.5% = TZS 192,500. Kwa NSSF: wafanyakazi 11 → '
     'TZS 5,500,000 × 20% = TZS 110,000.',
     ELEVEN_EMPLOYEES,
     'second real instance found by the sweep: NSSF 110,000 where the engine says 1,100,000'),

    ('paye_via_the_phantom_26000_relief',
     'PAYE = 8% × TZS 800,000 − TZS 26,000 = TZS 64,000.',
     ONE_EMPLOYEE,
     'the TZS 26,000 personal relief does not exist in Tanzania (CLAUDE.md section 11)'),

    ('nonzero_for_a_not_applicable_sibling',
     'SDL = TZS 28,000.',
     ONE_EMPLOYEE,
     'bare assertion against a not-applicable verdict, no working shown'),

    ('wrong_wcf_alongside_correct_own_levy',
     'NSSF = TZS 80,000. WCF: TZS 40,000.',
     ONE_EMPLOYEE,
     'own levy correct is exactly what let eval_320 through the per-levy guard'),
]


@pytest.mark.parametrize('probe_id,body,siblings,guards_against',
                         MUST_NOT_BLANK, ids=[p[0] for p in MUST_NOT_BLANK])
def test_faithful_body_is_not_blanked(probe_id, body, siblings, guards_against):
    assert fidelity.body_contradicts_siblings(body, siblings) is False, guards_against


@pytest.mark.parametrize('probe_id,body,siblings,guards_against',
                         MUST_BLANK, ids=[p[0] for p in MUST_BLANK])
def test_contradicting_body_is_blanked(probe_id, body, siblings, guards_against):
    assert fidelity.body_contradicts_siblings(body, siblings) is True, guards_against


def test_no_siblings_is_never_a_contradiction():
    assert fidelity.body_contradicts_siblings('SDL = TZS 28,000.', {}) is False


def test_empty_body_is_never_a_contradiction():
    assert fidelity.body_contradicts_siblings('', ONE_EMPLOYEE) is False


# --- orchestrator wiring ---------------------------------------------------------------

class _Silent(ModelBackend):
    def generate(self, prompt, params=None):
        return ''


def _sub(computation, text):
    from chike.orchestrator import SubQuestion
    sq = SubQuestion(text='x', kind='compute', computation_type=computation.computation)
    return SubAnswer(sub_question=sq, text=text, computation=computation)


def test_guard_blanks_only_the_offending_sub_answer():
    orch = Orchestrator(_Silent(), retriever=lambda q: [], ooc_phrases=[], in_scope_phrases=[])
    good = _sub(NSSF_SHARE, 'NSSF = TZS 80,000 kwa mwezi.')
    bad = _sub(WCF_4K, 'WCF: TZS 4,000. SDL (3.5%): TZS 28,000.')
    out = orch._cross_levy_guard([good, bad, _sub(SDL_NOT_APPLICABLE, 'SDL haitozwi.')])
    assert out[0].text == 'NSSF = TZS 80,000 kwa mwezi.'   # untouched
    assert out[1].text == ''                                # blanked whole
    assert out[2].text == 'SDL haitozwi.'                   # untouched


def test_single_levy_question_is_untouched():
    """A lone compute sub-answer has no siblings, so the guard must be a strict no-op."""
    orch = Orchestrator(_Silent(), retriever=lambda q: [], ooc_phrases=[], in_scope_phrases=[])
    only = _sub(SDL_192K, 'SDL = TZS 192,500. Pia NSSF ni TZS 1.')
    assert orch._cross_levy_guard([only])[0].text == only.text


def test_clarification_sub_answer_is_never_blanked():
    orch = Orchestrator(_Silent(), retriever=lambda q: [], ooc_phrases=[], in_scope_phrases=[])
    sq = _sub(WCF_4K, 'SDL = TZS 28,000.')
    clar = dataclasses.replace(sq, needs_clarification=True)
    out = orch._cross_levy_guard([clar, _sub(SDL_NOT_APPLICABLE, 'SDL haitozwi.')])
    assert out[0].text == 'SDL = TZS 28,000.'
