# -*- coding: utf-8 -*-
"""R17 / R19 / R26 regression file for D-FIDELITY-22 (founder-approved 2026-11-17): a start or deferral claim of "1 September" attached to VAT WITHHOLDING is replaced by the fixed rule. The Act (Finance Act 2025 (No. 11), edition
asserted, read 2026-11-17): s.2 commences the Act on 1 July 2025; s.124 inserts VAT Act s.5(5) (3% goods / 6% services) with no separate commencement clause; the "1st September, 2025" proviso belongs to s.5(6), the 16% rate for an
unregistered person paying electronically -- a different rule. Founding specimen: the live eval_041 reply, read from the committed targeted-verification artifact, not retyped."""
import json

import pytest

from chike import clarification, fidelity
from chike.model_abstraction import ModelBackend
from chike.orchestrator import Orchestrator

TOPIC = "vat_withholding_start_date"
Q = "Je, utaratibu wa VAT withholding wa Finance Act 2025 ulianza kutumika tangu 1 Januari 2025?"
SPEC = next(r for r in json.load(open("eval/results/targeted_gate4_2026_11_17.json", encoding="utf-8"))["rows"] if r["id"] == "eval_041")["reply"]
FACTS = json.load(open("scripts/locked_facts.json", encoding="utf-8"))


def _t(q, b):
    return [t for t, _ in fidelity.body_contradicts_d16(q, b)]


def test_the_founding_specimen_is_the_live_reply_and_it_flags():
    assert "ulicheleweshwa hadi 1 Septemba 2025" in SPEC
    assert TOPIC in _t(Q, SPEC)


FLAG = [
    (Q, "Utekelezaji wa VAT withholding ulicheleweshwa hadi 1 Septemba 2025."),
    ("VAT ya zuio ilianza lini?", "VAT ya zuio ilianza rasmi tarehe 1 Septemba 2025."),
    ("Zuio la VAT lilianza lini?", "Zuio la VAT lilianza kutumika kuanzia 1 Septemba 2025."),
    ("When did VAT withholding start?", "VAT withholding implementation was delayed until 1 September 2025."),
    ("VAT withholding ilianza lini?", "Hapana. Ilianza kuanzia 1 Julai 2025 kisha ikaahirishwa; utekelezaji wake ulianza 1 Septemba 2025."),
]
PASS = [
    (Q, "VAT ya 16% kwa malipo ya kielektroniki inaanza 1 Septemba 2025."),                                    # the B2C e-payment rule from 1 September 2025: a DIFFERENT rule
    (Q, "Kiwango cha 16% kwa mteja wa mwisho asiye na usajili kinaanza 1 Septemba 2025 (malipo ya kidijitali, B2C)."),
    (Q, "Hapana. Utaratibu wa VAT withholding ulianza tarehe 1 Julai 2025, si 1 Septemba 2025."),            # a NEGATION is a mention, not an assertion
    (Q, "Utaratibu wa VAT withholding ulianza tarehe 1 Julai 2025 (Sheria ya Fedha 2025)."),                  # the correct statement
    ("Kiwango kipya cha NSSF kinaanza lini?", "Kiwango kipya kinaanza kutumika tarehe 1 Septemba 2025."),     # an UNRELATED 1 September date
    ("Mwaka wa masomo unaanza lini?", "Unaanza 1 Septemba."),
    ("VAT ya zuio kwa mauzo ya bidhaa na huduma pamoja inakatwaje?", "Tangu 1 Julai 2026 thamani inagawanywa kwa 3:2."),   # the 2026 mixed-supply rule: no September
    (Q, "Utaratibu wa VAT withholding ni 3% kwa bidhaa na 6% kwa huduma."),                                    # no date at all
]


@pytest.mark.parametrize("q,b", FLAG)
def test_a_september_start_or_deferral_on_vat_withholding_flags(q, b):
    assert TOPIC in _t(q, b), b


@pytest.mark.parametrize("q,b", PASS)
def test_the_b2c_rule_the_correct_july_statement_negations_and_unrelated_september_dates_do_not_flag(q, b):
    assert TOPIC not in _t(q, b), b


class _S(ModelBackend):
    def __init__(self, t):
        self.t, self.calls = t, 0

    def generate(self, prompt, params=None):
        self.calls += 1
        return self.t


def _ans(q, body):
    b = _S(body)
    return Orchestrator(backend=b, retriever=lambda *a, **k: ["x"], system_prompt="x").answer(q), b


def test_wired_the_specimen_is_replaced_by_the_fixed_rule():
    r, b = _ans(Q, SPEC)
    assert b.calls >= 1 and [getattr(s, "guard", "") for s in r.sub_answers] == ["replaced"]
    assert "1 Julai 2025" in r.text and "haina kuahirishwa" in r.text and "ulicheleweshwa" not in r.text, r.text
    assert "16%" in r.text and "si ya VAT ya zuio" in r.text, "the 1 September date is named for the rule it belongs to"
    assert "Kifungu" not in r.text, "R44: no section number in served text"


def test_wired_a_correct_reply_is_left_alone():
    ok = "Hapana. Utaratibu wa VAT withholding ulianza tarehe 1 Julai 2025, si 1 Januari 2025. Thibitisha na TRA (tra.go.tz)."
    r, _ = _ans(Q, ok)
    assert r.text == ok and [getattr(s, "guard", "") for s in r.sub_answers] == [""]


def test_PLANTED_with_the_rule_removed_the_wrong_date_is_served(monkeypatch):
    monkeypatch.setattr(fidelity, "vat_withholding_start_misstated", lambda q, b: [])
    assert "ulicheleweshwa hadi 1 Septemba 2025" in _ans(Q, SPEC)[0].text


def test_the_restatement_agrees_with_the_locked_facts_it_restates():
    for k in ("vat_withholding_goods", "vat_withholding_services"):
        assert "effective 1 July 2025" in FACTS[k]["fact"], k
    t = clarification.CONSTANT_RESTATEMENTS[TOPIC]
    assert "3% kwa bidhaa" in t and "6% kwa huduma" in t and "1 Julai 2025" in t
