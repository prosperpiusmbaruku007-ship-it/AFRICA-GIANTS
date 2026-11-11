"""A threshold named inside a NEGATED PREMISE is a bound, not the user's figure (2026-11-12).

"Mauzo yangu bado hayajafika TZS 200 milioni ... kwa hiari?" was answered "Ndiyo, unatakiwa kujisajili VAT".
The corpora hold ONE such question in 8,086 strings (eval/results/sweep_bound_premise_2026_11_12.json), so the
probes are AUTHORED, in both directions: `bound` rows must not use the amount as turnover; `figure` rows --
including four traps that carry a cue and one amount but are NOT bounds -- must still compute on it.
Expectations were written from the rules, not from the code's output.
"""
import json
import pathlib

import pytest

from chike import routing
from chike.orchestrator import ModelBackend, Orchestrator

PROBES = [json.loads(l) for l in (pathlib.Path(__file__).resolve().parents[1] / "eval" / "accuracy_gate" /
                                  "bound_premise_probes_2026_11_12.jsonl").open(encoding="utf-8") if l.strip()]


class _Silent(ModelBackend):
    def generate(self, prompt, params=None):
        return ""


def _answer(q):
    return Orchestrator(_Silent(), retriever=lambda x: [], ooc_phrases=[], in_scope_phrases=[]).answer(q).text


def test_the_probe_file_has_both_directions_and_the_traps():
    kinds = {p["kind"] for p in PROBES}
    assert kinds == {"bound", "figure"}
    assert sum(p["kind"] == "figure" for p in PROBES) >= 7 and sum(p["kind"] == "bound" for p in PROBES) >= 9
    assert {"fg_02", "fg_03", "fg_05"} <= {p["id"] for p in PROBES}        # the three TRAPS


@pytest.mark.parametrize("p", PROBES, ids=[p["id"] for p in PROBES])
def test_probe(p):
    if p.get("detector_only"):
        assert p.get("detector_only_reason"), "a detector-only probe must say why it cannot reach the engine"
        pytest.skip("detector-only probe: " + p["detector_only_reason"][:60])
    text = _answer(p["question"])
    for needle in p["must_contain"]:
        assert needle.lower() in text.lower(), (p["id"], needle, text)
    for needle in p["must_not_contain"]:
        assert needle.lower() not in text.lower(), (p["id"], needle, text)


@pytest.mark.parametrize("p", [p for p in PROBES if p["kind"] == "bound"], ids=lambda p: p["id"])
def test_a_bound_is_detected_as_one(p):
    assert routing.upper_bound_amount(p["question"]) is not None


@pytest.mark.parametrize("p", [p for p in PROBES if p["kind"] == "figure"], ids=lambda p: p["id"])
def test_a_figure_is_not_mistaken_for_a_bound(p):
    assert routing.upper_bound_amount(p["question"]) is None


@pytest.mark.parametrize("a,b", [
    ("Mauzo yangu bado hayajafika TZS 200 milioni kwa mwaka. Ninaweza kusajili VAT kwa hiari?",
     "Mauzo yangu bado hayajafika TZS milioni 200 kwa mwaka. Ninaweza kusajili VAT kwa hiari?"),
    ("Mauzo yangu ya mwaka hayajafika TZS 150 milioni, je nisajili VAT?",
     "Mauzo yangu ya mwaka hayajafika TZS milioni 150, je nisajili VAT?"),
])
def test_the_two_spellings_of_a_bound_get_the_same_answer(a, b):
    assert _answer(a) == _answer(b)


def test_a_bound_is_never_returned_when_there_are_two_amounts():
    """Two amounts: one may be the bound and one the figure -- not decidable here, so no bound is claimed
    (the existing never-guess path asks)."""
    assert routing.upper_bound_amount(
        "Mauzo yangu ya mwaka ni TZS 150 milioni, hayajafika TZS 200 milioni.") is None


def test_the_compiled_cue_patterns_contain_no_control_characters():
    for n in ("_BOUND_VERB_RE", "_BOUND_PREP_RE"):
        assert not any(ord(c) < 32 for c in getattr(routing, n).pattern), n
