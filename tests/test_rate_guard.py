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


# ---------------------------------------------------------------------------------------------
# THE STAGE QUESTION, SETTLED 2026-10-05 BY MEASUREMENT RATHER THAN BY ARGUMENT.
# ---------------------------------------------------------------------------------------------
# A 2026-09-29 audit found a FIFTH R26 shape in this guard: not inert, not unwired, not
# overbroad -- CHECKED AT THE WRONG STAGE. Orchestrator._validate_and_clean runs it on `cleaned`
# (the model body), while what ships is _render's `body + "\n" + working`. The obvious fix is to
# run it on the rendered reply instead.
#
# ⛔ THE OBVIOUS FIX IS WRONG, AND THESE TESTS EXIST TO STOP SOMEONE APPLYING IT.
# Measured: eval/fidelity/measure_rate_guard_stage.py ->
# eval/results/rate_guard_stage_measurement.json, over the 16 committed probes paired with REAL
# engine workings from the production compute functions.
#
#     flagged pre-render   4   (exactly the four `flag` probes -- correct)
#     flagged post-render  6
#     verdicts moved       2   -- BOTH FALSE POSITIVES ON CORRECT BODIES
#     new catches          0
#
# WHY. The rule is a +/-60-character proximity window, so concatenation puts the END of the body
# within 60 characters of the START of the working. The working names its levy; the body's
# trailing rate then attaches to a levy it was never about:
#
#     rg_09  "VAT withholding kwa huduma ni asilimia 6, na kwa bidhaa ni asilimia 3."
#            + SDL working  ->  attributes ('sdl', 3) and ('sdl', 6). Both wrong for SDL; both
#            CORRECT for VAT withholding, and sourced today against tra.go.tz.
#     rg_10  "Kiwango cha kawaida cha VAT ni asilimia 18."
#            + SDL working  ->  attributes ('sdl', 18).
#
# These attributions exist in NEITHER SEGMENT ALONE. They are manufactured by the seam. And this
# guard BLANKS, so moving the stage would delete two correct answers to catch nothing -- the
# expensive direction, on a mechanism whose cost lands on a user.
#
# THE REAL LIMB WORTH CLOSING is the other one: the working was never checked at all. It is
# closed below as a STATIC test over the two constant tables, not as a runtime guard -- it is a
# property of `rates.py` vs `fidelity._LEVY_RATES`, so it cannot vary per request and has no
# false-positive surface facing a user. `working_alone_flags` measured 0: the tables agree today.

_SEAM_FALSE_POSITIVES = [
    pytest.param('rg_09',
                 'VAT withholding kwa huduma ni asilimia 6, na kwa bidhaa ni asilimia 3.',
                 id='rg_09_correct_vat_withholding_rates'),
    pytest.param('rg_10',
                 'Kiwango cha kawaida cha VAT ni asilimia 18. Hakijabadilika tangu 2015.',
                 id='rg_10_correct_vat_standard_rate'),
]


@pytest.mark.parametrize('probe_id,body', _SEAM_FALSE_POSITIVES)
def test_concatenating_the_working_manufactures_a_false_positive(probe_id, body):
    """The measurement, pinned. If this ever stops holding, re-run the measurement before
    concluding the seam risk is gone -- it may instead mean the attribution window changed."""
    from chike.rules_engine.sdl import compute_sdl
    from decimal import Decimal

    working = compute_sdl(Decimal('15000000'), 25).working
    rendered = f'{body.strip()}\n{working}'

    assert not fidelity.body_states_wrong_levy_rate(body), (
        f'{probe_id} is a CORRECT body and must be clean at the stage production uses')
    assert fidelity.body_states_wrong_levy_rate(rendered), (
        f'{probe_id}: the seam no longer manufactures an attribution. That may be good news, '
        f'but it invalidates the measurement that decided this guard\'s stage -- re-run '
        f'eval/fidelity/measure_rate_guard_stage.py before moving the stage on the strength of '
        f'this test passing.')

    # The attribution is created by the seam: present in the concatenation, in neither part.
    attr = set(map(tuple, fidelity.attributed_levy_rates(rendered)))
    attr -= set(map(tuple, fidelity.attributed_levy_rates(body)))
    attr -= set(map(tuple, fidelity.attributed_levy_rates(working)))
    assert attr, f'{probe_id}: expected a seam-created attribution, found none'


def test_the_guard_runs_on_the_model_body_not_the_rendered_reply():
    """Pins the stage in the production call site, so a well-meaning edit has to read the
    reasoning above before changing it."""
    import inspect

    from chike import orchestrator

    src = inspect.getsource(orchestrator.Orchestrator._validate_and_clean)
    assert 'body_states_wrong_levy_rate(cleaned)' in src, (
        'D-FIDELITY-6 is no longer called on `cleaned`. If it was moved to the rendered reply, '
        'see test_concatenating_the_working_manufactures_a_false_positive: that change was '
        'measured on 2026-10-05 to blank two CORRECT answers and catch nothing new.')


def test_every_engine_working_attributes_only_statutory_rates():
    """THE LIMB THAT WAS GENUINELY OPEN -- closed statically, not at runtime.

    D-FIDELITY-6 never saw the engine's own working, because the guard runs before _render
    appends it. That is worth closing: `rates.py`'s constants and `fidelity._LEVY_RATES` are two
    independent tables that must agree, and nothing compared them. A disagreement would mean the
    engine emits a rate its own fidelity guard considers non-statutory.

    Static by design. This is a property of two constant tables, so it cannot vary per request --
    checking it here costs nothing and risks nothing, where checking it at runtime would put a
    blanking mechanism in front of authoritative output. R19: a constant comparison, not a
    derived quantity.

    The grid spans each levy's applicability boundary (SDL's 10-employee threshold, PAYE's five
    bands) so the workings exercised are not all from one branch.
    """
    from decimal import Decimal

    from chike.rules_engine.nssf import compute_nssf
    from chike.rules_engine.paye import compute_paye
    from chike.rules_engine.sdl import compute_sdl
    from chike.rules_engine.wcf import compute_wcf

    results = []
    for payroll in ('3000000', '15000000', '120000000'):
        for headcount in (1, 9, 10, 25):
            results.append(compute_sdl(Decimal(payroll), headcount))
        results.append(compute_wcf(Decimal(payroll)))
        results.append(compute_nssf(Decimal(payroll)))
    for salary in ('250000', '350000', '650000', '900000', '1500000'):
        results.append(compute_paye(Decimal(salary)))

    assert results, 'no engine results built — this test would pass vacuously'

    offenders = []
    for r in results:
        if not r.working:
            continue
        if fidelity.body_states_wrong_levy_rate(r.working):
            offenders.append((r.computation, r.working[:140],
                              fidelity.attributed_levy_rates(r.working)))
    assert not offenders, (
        'an engine working attributes a rate that fidelity._LEVY_RATES does not allow for that '
        f'levy -- rates.py and fidelity.py disagree: {offenders}')
