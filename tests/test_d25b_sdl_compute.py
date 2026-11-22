"""2026-11-22 D-FIDELITY-25b: D-FIDELITY-25 extended to the SDL COMPUTE path, under the founder's three conditions (unnegated applicability questions only; compare against the engine's BOOLEAN, not its lead word; blank the BODY only).
The stored population holds no true positive (priced: 52 SDL-routed replies, 0 flagged), so the specimens are PLANTED and each condition and veto is proved to matter (R26). Probes that should come back CLEAN do the work (R17)."""
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
from chike import fidelity, rules_engine          # noqa: E402
from chike.orchestrator import Orchestrator      # noqa: E402

YES = rules_engine.compute_sdl(5_000_000, 15)     # engine: SDL applies
NO = rules_engine.compute_sdl(3_000_000, 6)       # engine: SDL does not apply
Q15 = "Nina wafanyakazi 15, je natakiwa kulipa SDL?"
Q6 = "Nina wafanyakazi 6, je natakiwa kulipa SDL?"

FLAG = [
    (Q15, "Hapana, hauhitaji kulipa SDL kwa sababu ni duka dogo.", YES, "denied although the engine says it applies"),
    (Q15, "Hapana, huna wajibu wa kulipa SDL.", YES, "a second denial form"),
    (Q6, "Ndiyo, unatakiwa kulipa SDL.", NO, "affirmed although the engine says it does not apply"),
]
CLEAN = [
    (Q15, "Ndiyo, unatakiwa kulipa SDL asilimia 3.5 ya mishahara.", YES, "agrees with the engine"),
    (Q6, "Hapana, una chini ya 10, hulipi SDL.", NO, "agrees with the engine (below threshold)"),
    (Q15, "Mwajiri mwenye wafanyakazi chini ya 10 hana wajibu wa kulipa SDL.", YES, "a below-threshold RULE sentence is correct, not a verdict on this employer"),
    ("Nina shule yenye wafanyakazi 15, je natakiwa kulipa SDL?", "Hapana, hauhitaji kulipa SDL.", YES, "EXEMPT category in the question: the engine knows only the headcount, so its boolean can be the wrong half"),
    ("Je, SDL si lazima kwa wafanyakazi 15, sivyo?", "Hapana, haihitaji kulipa SDL.", YES, "NEGATED question (eval_394): never judged"),
    (Q15, "PAYE hukatwa kwenye mshahara; hauhitaji kulipa kodi ya majengo.", YES, "a denial that does not name SDL"),
    (Q15, "Hapana, huna wajibu wa kulipa SDL.", None, "no engine result: the fact-path rule (D-FIDELITY-25) owns that case"),
]


@pytest.mark.parametrize("q,body,comp,why", FLAG)
def test_flagged(q, body, comp, why):
    assert fidelity.sdl_body_contradicts_verdict(q, body, comp), why


@pytest.mark.parametrize("q,body,comp,why", CLEAN)
def test_clean(q, body, comp, why):
    assert fidelity.sdl_body_contradicts_verdict(q, body, comp) == [], why


class _B:
    def __init__(self, r):
        self.r = r

    def generate(self, prompt, params=None):
        return self.r


def _answer(q, body):
    return Orchestrator(_B(body), retriever=lambda x: [], ooc_phrases=[], in_scope_phrases=[]).answer(q).text


def test_real_path_blanks_the_body_and_keeps_the_working():
    t = _answer(Q15, "Hapana, hauhitaji kulipa SDL kwa sababu ni duka dogo.")
    assert "hauhitaji" not in t and "Ndiyo" in t and "15" in t     # the contradicting sentence is gone; the engine's verdict and working render


def test_real_path_leaves_an_agreeing_body_alone():
    assert "Ndiyo, unatakiwa kulipa SDL" in _answer(Q15, "Ndiyo, unatakiwa kulipa SDL asilimia 3.5 ya mishahara.")


def test_plant_unwired_lets_the_contradiction_through(monkeypatch):
    monkeypatch.setattr(fidelity, "sdl_body_contradicts_verdict", lambda q, b, c: [])
    assert "hauhitaji kulipa SDL" in _answer(Q15, "Hapana, hauhitaji kulipa SDL kwa sababu ni duka dogo."), "unwired, the contradiction must reach the user; else the real-path test proves nothing"


def test_plant_condition_1_removed_judges_a_negated_question(monkeypatch):
    import re
    monkeypatch.setattr(fidelity, "_D25B_NEGATED_Q", re.compile(r"(?!x)x"))
    assert fidelity.sdl_body_contradicts_verdict("Nina wafanyakazi 15, je natakiwa kulipa SDL, au SDL si lazima kwangu?", "Hapana, haihitaji kulipa SDL.", YES), "condition 1 (unnegated only) is load-bearing"


def test_plant_the_exempt_veto_removed_judges_an_exempt_employer(monkeypatch):
    import re
    monkeypatch.setattr(fidelity, "_D25_EXEMPT", re.compile(r"(?!x)x"))
    assert fidelity.sdl_body_contradicts_verdict("Nina shule yenye wafanyakazi 15, je natakiwa kulipa SDL?", "Hapana, hauhitaji kulipa SDL.", YES)


def test_condition_2_compares_the_boolean_not_the_lead_word():
    """The engine's lead can be wrong; its boolean is the comparison. A computation with applicable=True but a misleading working text still judges by the boolean."""
    import dataclasses
    odd = dataclasses.replace(YES, working="Hapana. (a lead that disagrees with its own boolean)")
    assert fidelity.sdl_body_contradicts_verdict(Q15, "Hapana, hauhitaji kulipa SDL.", odd)


def test_new_patterns_contain_no_control_characters():
    for r in (fidelity._D25B_NEGATED_Q, fidelity._D25B_AFFIRM, fidelity._D25B_NEG_IN_SENTENCE):
        assert not any(ord(c) < 32 and c != "\n" for c in r.pattern)
