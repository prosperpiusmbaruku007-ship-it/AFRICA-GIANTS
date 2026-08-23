"""The coverage gate: its mechanics, its per-part contract, and the fact that it ships OFF.

WHY IT SHIPS OFF, in one paragraph, because a future reader will otherwise turn it on. The gate's
SHAPE is sound — per-part, fact-path only, consulting no similarity score, a constant comparison
in R19's sense, with a refusal that routes the user to the right authority instead of dead-ending
them. Its SIGNAL is not. Measured on `eval/coverage/coverage_gate_heldout_040.jsonl`, a probe set
authored and frozen at c8b46a9 BEFORE `chike/coverage.py` existed:

    of 21 realistic questions about topics the corpus DOES hold, the gate refuses 15,
    and only 2 of the 6 that pass do so by matching the right topic.

The same mechanism costs 8 false refusals across 411 corpus questions — 1.9%. **That 1.9% was a
fit.** The gate corpora were authored from the same source families as the facts and therefore
share their vocabulary; the held-out set was not, and it is the measurement. A hand-authored cue
list cannot cover paraphrase space — the three-axes problem at corpus scale.

DO NOT DEFAULT `coverage_gate` TO True TO MAKE A FUTURE TEST PASS. If the signal improves, it
must be re-measured on a FRESH held-out set: this one is burned, because its results have now
been read.
"""
import json
import os

import pytest

from chike import coverage
from chike.orchestrator import Orchestrator
from chike.model_abstraction import FakeBackend

HELDOUT = os.path.join('eval', 'coverage', 'coverage_gate_heldout_040.jsonl')


def _heldout():
    with open(HELDOUT, encoding='utf-8') as fh:
        rows = [json.loads(line) for line in fh if line.strip()]
    assert len(rows) == 40, f'held-out set has {len(rows)} rows, expected 40'
    return rows


HELDOUT_ROWS = _heldout()


# ── it ships off, and off means byte-identical ───────────────────────────────────

def test_the_gate_is_off_by_default():
    """The load-bearing assertion of this file. See the module docstring for the measurement."""
    orch = Orchestrator(backend=FakeBackend(scripted_reply='ok'), retriever=lambda q: [])
    assert orch.coverage_gate is False


def test_with_the_gate_off_an_uncovered_question_still_reaches_the_model():
    """Off must mean OFF — not 'refuses a bit less'. A question with no covered topic at all
    goes to the model exactly as it did before the gate existed."""
    fake = FakeBackend(scripted_reply='jibu la kawaida')
    orch = Orchestrator(backend=fake, retriever=lambda q: [])
    reply = orch.answer('ushuru wa soko kwa genge langu ni kiasi gani kwa siku')
    assert fake.call_count == 1
    assert reply.refused is False
    assert 'jibu la kawaida' in reply.text
    assert not any(sa.coverage_refused for sa in reply.sub_answers)


def test_with_the_gate_on_the_same_question_is_refused_without_a_model_call():
    fake = FakeBackend(scripted_reply='should never be returned')
    orch = Orchestrator(backend=fake, retriever=lambda q: [], coverage_gate=True)
    reply = orch.answer('ushuru wa soko kwa genge langu ni kiasi gani kwa siku')
    assert fake.call_count == 0, 'a refused part must cost no generation'
    assert reply.refused is True
    assert all(sa.coverage_refused for sa in reply.sub_answers)
    assert 'sina uhakika' in reply.text.lower()


# ── the copy ─────────────────────────────────────────────────────────────────────

def test_the_refusal_names_the_topic_and_the_authority_and_offers_no_figure():
    text = coverage.refusal_text('nataka kuweka bango la matangazo nje ya duka langu, '
                                 'halmashauri inatoza kiasi gani?')
    assert 'halmashauri' in text                       # the authority
    assert 'ada ya matangazo' in text                  # the topic, named
    assert 'sitakupa kiwango wala kiasi' in text       # the figure, explicitly withheld
    assert text.startswith('Sina uhakika')             # the project's own referral formula


def test_the_refusal_formula_is_one_the_refusal_gate_recognises():
    """`Sina uhakika` is in REFUSAL_PHRASES. A refusal the gate scores as a wrong answer is
    worse than no refusal, because it would show up as an accuracy regression."""
    from chike import classification
    cfg = classification.load_local_config()
    # The key is lower-case `refusal_phrases` in chike_config.json. The first version of this
    # test read `REFUSAL_PHRASES`, got [], and the non-empty guard below caught it immediately —
    # without that guard the loop would have iterated zero times and PASSED, asserting nothing.
    # R20 doing its job inside the file that cites R20.
    phrases = [p.lower() for p in cfg.get('refusal_phrases', [])]
    assert phrases, 'config carries no refusal_phrases — this test would be vacuous'
    for probe in ('ushuru wa mazao ni asilimia ngapi', 'nahitaji ruhusa ya maji'):
        body = coverage.refusal_text(probe).lower()
        assert any(p in body for p in phrases), probe


def test_an_unmapped_topic_still_refuses_but_with_the_generic_copy():
    """The authority map may only ever IMPROVE a refusal, never cause or prevent one."""
    assert coverage.uncovered_authority('swali lisilo na ramani yoyote hapa') is None
    text = coverage.refusal_text('swali lisilo na ramani yoyote hapa')
    assert text.startswith('Sina uhakika')
    assert 'sitakupa kiwango wala kiasi' in text


# ── per-part, which is the whole reason it is not a message-level check ──────────

def test_a_mixed_message_answers_the_covered_part_and_refuses_the_other():
    """Wholesale refusal discards a correct answer; wholesale answering is the nat_23 failure
    of shipping half an answer with no sign the other half went missing. Both are cured by
    being explicit per part."""
    fake = FakeBackend(scripted_reply='Kiwango cha VAT ni asilimia 18.')
    orch = Orchestrator(backend=fake, retriever=lambda q: [], coverage_gate=True)
    reply = orch.answer('Kiwango cha VAT ni asilimia ngapi? '
                        'Na kodi ya pango la ardhi nalipa lini?')
    kinds = [sa.coverage_refused for sa in reply.sub_answers]
    assert True in kinds and False in kinds, (
        f'expected one answered part and one refused part, got {kinds}')
    assert reply.refused is False, 'a message with an answered half is not a refusal'
    assert 'asilimia 18' in reply.text
    assert 'Sina uhakika' in reply.text


def test_a_compute_part_is_never_gated():
    """An engine result is grounded by construction, not by retrieval, so the gate has no
    business inspecting it — and 18 of the 29 correct rows on the natural set come from that
    deterministic surface."""
    extraction = ('{"gross_monthly_payroll": {"value": 6000000, "confidence": "high"}, '
                  '"employee_count": {"value": 14, "confidence": "high"}}')
    fake = FakeBackend(replies=[extraction, 'Hii ndio hesabu yako ya SDL:'])
    orch = Orchestrator(backend=fake, retriever=lambda q: [], coverage_gate=True)
    reply = orch.answer('nina wafanyakazi 14 mishahara yote milioni 6, SDL ni kiasi gani')
    assert not any(sa.coverage_refused for sa in reply.sub_answers)
    assert 'TZS 210,000' in reply.text


# ── the measured result, pinned so it cannot be quietly forgotten ────────────────

def test_the_heldout_set_is_intact_and_still_covers_all_four_arms():
    arms = {}
    for r in HELDOUT_ROWS:
        arms[r['arm']] = arms.get(r['arm'], 0) + 1
        assert len(r['guards_against']) > 60, f"{r['id']} has no real guards_against note"
    assert arms == {'A_covered_must_pass': 21, 'B_uncovered_must_refuse': 10,
                    'C_mixed_answer_and_refuse': 5,
                    'D_wrong_topic_match_must_refuse': 4}, arms


@pytest.mark.parametrize('probe', [r for r in HELDOUT_ROWS
                                   if r['arm'] == 'A_covered_must_pass'],
                         ids=[r['id'] for r in HELDOUT_ROWS
                              if r['arm'] == 'A_covered_must_pass'])
def test_arm_a_records_the_measured_state_rather_than_the_desired_one(probe):
    """These rows are the reason the gate is off, so they assert WHAT IS, not what should be.

    A row flipping to covered is a genuine improvement and must be an explicit edit — the same
    known-failing discipline used for nat_44/nat_28 and for pic_05, which exists so a defect
    cannot be parked by relaxing an expectation.
    """
    measured_pass = {'hoA_sdl', 'hoA_nssf', 'hoA_trademark', 'hoA_osha',
                     'hoA_permit', 'hoA_filing'}
    is_covered = coverage.is_covered(probe['question'])
    assert is_covered == (probe['id'] in measured_pass), (
        f"{probe['id']} changed: covered={is_covered}. If the cue list genuinely improved, "
        f"update `measured_pass` in the same commit AND re-measure on a FRESH held-out set — "
        f"this one is burned, its results have been read.")


def test_only_two_of_the_six_arm_a_passes_match_their_true_topic():
    """The finding that matters most, and the one a summary count hides: four of the six
    'passes' are accidents — SDL and NSSF pass on `mfanyakazi` (topic `employment`), permit and
    filing on `kampuni` (topic `brela_company`). A gate that passes a question for the wrong
    reason has a latent false negative, which is exactly what the 2026-08-23 canary caught in
    production when `kodi ya mapato` matched `paye` for four different obligations."""
    right = []
    for r in HELDOUT_ROWS:
        if r['arm'] != 'A_covered_must_pass':
            continue
        topics = coverage.covered_topics(r['question'])
        if topics and r['true_topic'] in topics:
            right.append(r['id'])
    assert sorted(right) == ['hoA_osha', 'hoA_trademark'], right
