"""R17 regression file for the D-FIDELITY-7 subject fallback (2026-11-16, eval_355): a body that never names its subject inherits the QUESTION's subject. Ten of fourteen probes are clean; the founding specimen is verbatim from the gate and
the correct answer to it is a probe too. Planted: with the fallback removed (question not passed) the specimen is NOT flagged -- which is exactly the live miss."""
import json

import pytest

from chike import fidelity

P = [json.loads(l) for l in open("eval/fidelity/threshold_subject_fallback_probes_2026_11_16.jsonl", encoding="utf-8") if l.strip()]


def test_shape():
    assert len(P) == 14 and sum(p["expect"] == "flag" for p in P) == 4


@pytest.mark.parametrize("p", P, ids=[p["id"] for p in P])
def test_probe(p):
    assert fidelity.body_states_wrong_threshold(p["body"], p["question"]) == (p["expect"] == "flag"), p["guards_against"]


def test_the_specimen_is_the_miss_without_the_question():
    s = P[0]
    assert fidelity.body_states_wrong_threshold(s["body"]) is False, "the live miss: with no question the body names no subject"
    assert fidelity.body_states_wrong_threshold(s["body"], s["question"]) is True


def test_no_flag_changes_when_the_body_names_its_own_subject():
    body = "Hapana, EFD ina kizingiti cha TZS 11M."
    assert fidelity.stated_wrong_thresholds(body) == fidelity.stated_wrong_thresholds(body, "Mauzo yangu ni TZS 5,000,000, je EFD ni lazima?")
