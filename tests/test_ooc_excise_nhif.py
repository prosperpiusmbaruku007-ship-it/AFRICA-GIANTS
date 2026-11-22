"""2026-11-22 OOC additions: excise duty and VERB-QUALIFIED NHIF only (founder's decision). R17: the probes run both ways -- in-scope questions that contain the risky vocabulary must NOT be refused,
the out-of-scope specimens MUST be. A bare `nhif` and `bima ya afya` are deliberately absent from the list and pinned absent here."""
import json
import os
import sys

_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, _ROOT)
from chike import classification  # noqa: E402

_PROBES = os.path.join(_ROOT, "eval", "refusal_gate", "ooc_excise_nhif_probes_2026_11_22.jsonl")


def _probes():
    with open(_PROBES, encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh if line.strip()]
    assert len(rows) == 17, len(rows)           # a loader that silently returned nothing must fail, not pass vacuously (R20)
    assert any(r["expected_refusal"] for r in rows) and any(not r["expected_refusal"] for r in rows)
    return rows


def _phrases():
    return classification.resolve_phrases(classification.load_local_config())


def test_in_scope_probes_are_not_refused_and_specimens_are():
    ooc, in_scope = _phrases()
    wrong = [(p["id"], p["question"]) for p in _probes()
             if classification.classify(p["question"], ooc, in_scope) == p["expected_refusal"]]
    assert not wrong, wrong


def test_the_phrases_that_must_never_be_listed_are_absent():
    ooc, _ = _phrases()
    for banned in ("nhif", "bima ya afya", "bima za afya", "makato ya", "ushuru wa", "bidhaa", "afya"):
        assert banned not in ooc, banned


def test_the_added_phrases_are_present_with_the_orthographic_variant():
    ooc, _ = _phrases()
    for want in ("excise duty", "ushuru wa bidhaa", "ushuru wa bizaa", "makato ya nhif", "nhif ya wafanyakazi", "nhif ya mwajiri"):
        assert want in ooc, want


def test_known_limit_a_bare_nhif_question_is_not_caught():
    """RECORDED LIMIT, not a goal: with no verb-qualified form a bare NHIF question still reaches the model. Pinned so widening it is a visible, deliberate change (R17: a bare `nhif` would refuse the mixed NSSF/NHIF question)."""
    ooc, in_scope = _phrases()
    assert classification.classify("NHIF inakatwa kiasi gani kwenye mshahara?", ooc, in_scope) is True
