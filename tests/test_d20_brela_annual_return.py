# -*- coding: utf-8 -*-
"""R17 / R19 / R26 regression file for D-FIDELITY-20 (founder-approved 2026-11-17): the company annual-return deadline is a CONSTANT -- each return is made up to the anniversary of incorporation and delivered within 28 days of that return
date (Companies Act Cap.212 R.E.2023, edition asserted, PROGRESS 4aw). The founding specimen is the stored gate reply to eval_072, read from the committed artifact, not retyped."""
import json

import pytest

from chike import clarification, fidelity
from chike.model_abstraction import ModelBackend
from chike.orchestrator import Orchestrator

GATE = json.load(open("eval/results/gate_production_c2143c0.json", encoding="utf-8"))["rows"]
ROW = next(r for r in GATE if r["id"] == "eval_072")
Q, SPEC = ROW["question_sw"], ROW["generated"]
TOPIC = "brela_annual_return_deadline"
FACTS = json.load(open("scripts/locked_facts.json", encoding="utf-8"))


def _topics(q, b):
    return [t for t, _ in fidelity.body_contradicts_d16(q, b)]


def test_the_founding_specimen_is_the_stored_reply_and_it_flags():
    assert "miezi 12" in SPEC and "tarehe ya usajili" in SPEC
    assert TOPIC in _topics(Q, SPEC)


FLAG = [
    (Q, "Annual return inapaswa kuwasilishwa ndani ya miezi 12 baada ya kusajiliwa."),
    ("Annual return ya BRELA inapaswa kuwasilishwa kabla ya tarehe gani kila mwaka?", "Kanuni ya jumla: wasilisha annual return ndani ya miezi 12 ya mwisho wa mwaka wa biashara wako."),     # the TRAINING sentence that teaches it
    ("Kampuni inatakiwa kuwasilisha ritani ya mwaka lini?", "Ritani ya mwaka huwasilishwa kufikia 30 Septemba kila mwaka."),
    ("When must a company file its annual return with BRELA?", "A company must file its annual return within 12 months of registration."),
]
PASS = [
    (Q, "Hakuna tarehe maalum ya 30 Septemba kwa annual returns za BRELA — tarehe inategemea tarehe ya kumbukumbu ya usajili (anniversary date)."),                    # a NEGATION is a mention, not an assertion
    (Q, "Kila return hutayarishwa hadi tarehe ya maadhimisho ya kuanzishwa kwa kampuni; ukichelewa zaidi ya siku 28 kuna faini."),                                       # the right frame
    (Q, "Annual return huwasilishwa mara moja kwa mwaka. Thibitisha na BRELA (brela.go.tz)."),                                                                            # no figure
    ("Return ya kodi ya mapato ya kampuni ni lini?", "Annual return ya kodi ni ndani ya miezi 6 baada ya mwaka wa mapato."),                                                 # a TAX question: not this guard (the corporate-return guard owns it)
    ("Kizingiti cha VAT cha miezi 12 ni kiasi gani?", "Kizingiti cha VAT ni TZS 200,000,000 katika miezi 12."),                                                            # no annual-return subject
    (Q, "Ada ya annual return ni TZS 22,000 na adhabu ya kuchelewa ni TZS 2,500 kwa kila mwezi."),                                                                          # fee and penalty, no 12-month / 30-September figure
]


@pytest.mark.parametrize("q,b", FLAG)
def test_a_misstated_deadline_flags(q, b):
    assert TOPIC in _topics(q, b), b


@pytest.mark.parametrize("q,b", PASS)
def test_correct_denied_or_unrelated_text_does_not_flag(q, b):
    assert TOPIC not in _topics(q, b), b


class _S(ModelBackend):
    def __init__(self, t):
        self.t = t

    def generate(self, prompt, params=None):
        return self.t


def _ans(q, body):
    return Orchestrator(backend=_S(body), retriever=lambda *a, **k: ["x"], system_prompt="x").answer(q)


def test_wired_the_specimen_is_replaced_by_the_locked_statement_and_names_28_days():
    r = _ans(Q, SPEC)
    assert "miezi 12" not in r.text and "siku 28" in r.text and "maadhimisho" in r.text and "BRELA" in r.text, r.text
    assert [getattr(s, "guard", "") for s in r.sub_answers] == ["replaced"]
    assert r.model_calls and "Kifungu" not in r.text, "model path (never auto-send eligible); R44: no section number in served text"


def test_PLANTED_with_the_rule_removed_the_wrong_deadline_is_served(monkeypatch):
    monkeypatch.setattr(fidelity, "brela_annual_return_deadline_misstated", lambda q, b: [])
    assert "miezi 12" in _ans(Q, SPEC).text


def test_the_restatement_agrees_with_the_locked_fact_it_restates():
    fact = json.dumps(FACTS["annual_return_form_number"], ensure_ascii=False)
    assert "28-day" in fact and "return date" in fact
    assert "siku 28" in clarification.CONSTANT_RESTATEMENTS[TOPIC]
