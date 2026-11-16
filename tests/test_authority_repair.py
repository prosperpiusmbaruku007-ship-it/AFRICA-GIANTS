"""R17 regression file for D-FIDELITY-14 (wrong authority, repaired): 21 probes in eval/fidelity/authority_repair_probes_2026_11_16.jsonl -- 8 REPAIRS (the live specimens verbatim) and 13 that must come back BYTE-IDENTICAL
(TanzLII on GN 487A, KRA in a refusal, a multi-authority answer, a two-topic question, the correct authority, no host). Wired through the real orchestrator and PLANTED (R26)."""
import json

import pytest

from chike import fidelity
from chike.model_abstraction import ModelBackend
from chike.orchestrator import Orchestrator

PROBES = [json.loads(l) for l in open("eval/fidelity/authority_repair_probes_2026_11_16.jsonl", encoding="utf-8") if l.strip()]


def test_probe_file_has_both_halves():
    assert len(PROBES) == 21 and sum(p["expect"] is not None for p in PROBES) == 8 and sum(p["expect"] is None for p in PROBES) == 13


@pytest.mark.parametrize("p", PROBES, ids=[p["id"] for p in PROBES])
def test_probe(p):
    out = fidelity.repair_authority(p["question"], p["body"])
    if p["expect"] is None:
        assert out == p["body"], p["guards_against"]
    else:
        assert out != p["body"] and p["expect"] in out and fidelity.repair_authority(p["question"], out) == out, p["guards_against"]


class _S(ModelBackend):
    def __init__(self, t):
        self.t = t

    def generate(self, prompt, params=None):
        return self.t


def _ans(q, body):
    return Orchestrator(backend=_S(body), retriever=lambda *a, **k: ["x"], system_prompt="x").answer(q)


Q = "Mfanyakazi akijifungua, likizo ya uzazi ni siku ngapi?"      # verified: reaches the model path
BAD = "Kwa mujibu wa sheria, likizo ya uzazi ni siku 84. Thibitisha na https://immigration.go.tz."


def test_wired_end_to_end_repairs_the_specimen():
    r = _ans(Q, BAD)
    assert "immigration.go.tz" not in r.text and "kazi.go.tz" in r.text and any(getattr(s, "guard", "") == "repaired" for s in r.sub_answers), r.text


def test_wired_correct_body_is_untouched():
    good = "Likizo ya uzazi ni siku 84 zenye malipo. Thibitisha na Ofisi ya Kazi (kazi.go.tz)."
    assert _ans(Q, good).text.count("kazi.go.tz") == 1 and "repaired" not in [getattr(s, "guard", "") for s in _ans(Q, good).sub_answers]


def test_planted_repair_disabled_lets_the_specimen_through(monkeypatch):
    monkeypatch.setattr(fidelity, "repair_authority", lambda q, b: b)
    assert "immigration.go.tz" in _ans(Q, BAD).text
