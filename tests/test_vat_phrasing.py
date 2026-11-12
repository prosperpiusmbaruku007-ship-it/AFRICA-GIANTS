"""First-person VAT-registration phrasings reach the engine (2026-11-12).

"Mauzo yangu ni milioni 250 kwa mwaka. Je, ni lazima nijisajili VAT" returned intent `none` and was answered on the
fact path -- a bare "Ndiyo", no figure, no working. The cue list knew only the infinitive. Measured: 4 of 7 natural
phrasings of that one question missed the engine. The probes are authored in BOTH directions: the phrasings must
route, and the collisions (BRELA / TIN / a rate question / an approximate figure / a threshold lookup / someone
else's turnover / no figure) must not -- a cue list that widens is only as good as what it still refuses.
"""
import json
import pathlib

import pytest

from chike import routing
from chike.model_abstraction import ModelBackend
from chike.orchestrator import Orchestrator

PROBES = [json.loads(l) for l in (pathlib.Path(__file__).resolve().parents[1] / "eval" / "accuracy_gate" /
                                  "vat_phrasing_probes_2026_11_12.jsonl").open(encoding="utf-8") if l.strip()]


class _Silent(ModelBackend):
    def generate(self, prompt, params=None):
        return ""


def _answer(q):
    return Orchestrator(_Silent(), retriever=lambda x: [], ooc_phrases=[], in_scope_phrases=[]).answer(q).text


def test_both_directions_are_present():
    assert {p["kind"] for p in PROBES} == {"route", "noroute"}
    assert sum(p["kind"] == "route" for p in PROBES) >= 9 and sum(p["kind"] == "noroute" for p in PROBES) >= 8


@pytest.mark.parametrize("p", [p for p in PROBES if p["kind"] == "route"], ids=lambda p: p["id"])
def test_the_phrasing_reaches_the_vat_engine_and_states_the_working(p):
    assert routing.detect_intent(p["question"]) == "vat_registration", p["question"]
    text = _answer(p["question"])
    for needle in p["must_contain"]:
        assert needle.lower() in text.lower(), (p["id"], needle, text)


@pytest.mark.parametrize("p", [p for p in PROBES if p["kind"] == "noroute"], ids=lambda p: p["id"])
def test_the_collision_does_not_reach_the_vat_engine(p):
    assert routing.detect_intent(p["question"]) != "vat_registration", p["question"]


def test_the_two_spellings_of_the_amount_get_the_same_answer():
    a = _answer("Mauzo yangu ni milioni 250 kwa mwaka. Je, ni lazima nijisajili VAT")
    b = _answer("Mauzo yangu ni TZS milioni 250 kwa mwaka. Je, ni lazima nijisajili VAT")
    c = _answer("Mauzo yangu ni 250 milioni kwa mwaka. Je, ni lazima nijisajili VAT")
    assert a == b == c


def test_the_infinitive_forms_still_route_exactly_as_before():
    for q in ("Mauzo yangu ni milioni 250 kwa mwaka. Je, ni lazima kujisajili VAT?",
              "Mauzo yangu ni milioni 250 kwa mwaka. Je, ni lazima kusajili VAT?"):
        assert routing.detect_intent(q) == "vat_registration"


def test_the_compiled_cue_pattern_contains_no_control_characters():
    """R39: a regex patched in through a generating script can compile `\\b` to a backspace. Compile, don't read."""
    for pat in (routing._VAT_REG_RE.pattern, routing._THRESHOLD_ASK_VETO.pattern):
        assert not any(ord(c) < 32 for c in pat), repr(pat)


def test_the_founding_question_is_no_longer_a_known_gap():
    """This was a strict-xfail in tests/test_card_evidence.py until the cue list learned the subjunctive."""
    assert routing.detect_intent("Mauzo yangu ni milioni 250 kwa mwaka. Je, ni lazima nijisajili VAT") \
        == "vat_registration"
