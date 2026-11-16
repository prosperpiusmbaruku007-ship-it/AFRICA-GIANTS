"""R17 regression file for D-FIDELITY-12 -- a turnover above the VAT threshold told it need not register (eval_318's VAT limb, 2026-11-16).

Sixteen probes in eval/fidelity/vat_denial_probes_2026_11_16.jsonl; TEN of them are deliberately clean (R17: the half that does the work). The founding specimen is verbatim from the gate. Wired end to
end through the real orchestrator with a scripted backend, and PLANTED: the trigger is disabled and the specimen must then reach the user (R26: a control is not working until watched to block).
"""
import json

import pytest

from chike import fidelity
from chike.model_abstraction import ModelBackend
from chike.orchestrator import Orchestrator

PROBES = [json.loads(l) for l in open("eval/fidelity/vat_denial_probes_2026_11_16.jsonl", encoding="utf-8") if l.strip()]
# 2026-11-16: the founding question ("je nasajili VAT kama mapato ni TZS 205,000,000?") now ROUTES TO THE VAT ENGINE (3c: "nasajili" and "kama mapato ni" were router gaps), so it no longer reaches the fact-path
# guard this file wires. The guard stays as the second layer for the phrasings the router still misses; this question is one of them (verified `none`), and the specimen body is unchanged.
FACT_PATH_Q = "Kampuni yenye mapato ya TZS 205,000,000 inahitaji kusajili VAT?"
ETHEL = "Nina wafanyakazi 11 na mishahara TZS 5,500,000 na nataka kujua SDL na NSSF na pia je nasajili VAT kama mapato ni TZS 205,000,000?"
SPECIMEN = [p for p in PROBES if p["id"] == "vd_01"][0]["body"]


def test_probe_file_is_not_empty_and_has_both_halves():
    assert len(PROBES) == 16
    assert sum(p["expect"] == "flag" for p in PROBES) >= 4 and sum(p["expect"] == "clean" for p in PROBES) >= 10


@pytest.mark.parametrize("p", PROBES, ids=[p["id"] for p in PROBES])
def test_probe(p):
    assert fidelity.body_denies_vat_registration_above_threshold(p["question"], p["body"]) == (p["expect"] == "flag"), p["guards_against"]


class _Scripted(ModelBackend):
    def __init__(self, text):
        self.text = text

    def generate(self, prompt, params=None):
        return self.text


def _answer(body, question=ETHEL):
    return Orchestrator(backend=_Scripted(body), retriever=lambda *_a, **_k: ["Kizingiti cha kusajili VAT: mauzo ya TZS 200,000,000 kwa miezi 12."], system_prompt="x").answer(question)


def test_wired_end_to_end_replaces_the_specimen():
    r = _answer(SPECIMEN, FACT_PATH_Q)
    assert "huhitajiwi" not in r.text.lower()
    assert "TZS 200,000,000" in r.text and "ni lazima ujisajili VAT" in r.text
    assert any(getattr(s, "guard", "") == "replaced" for s in r.sub_answers)


def test_wired_correct_body_passes_through_untouched():
    good = "Ndiyo. Mapato ya TZS 205,000,000 yamezidi kizingiti cha TZS 200,000,000, hivyo lazima ujisajili VAT."
    r = _answer(good, FACT_PATH_Q)
    assert "yamezidi kizingiti" in r.text and not any(getattr(s, "guard", "") == "replaced" for s in r.sub_answers)


def test_planted_trigger_disabled_lets_the_specimen_through(monkeypatch):
    monkeypatch.setattr(fidelity, "vat_denial_above_threshold", lambda q, b: None)
    r = _answer(SPECIMEN, FACT_PATH_Q)
    assert "huhitajiwi" in r.text.lower(), "with the guard disabled the specimen must reach the user, or the wiring test above proves nothing"
