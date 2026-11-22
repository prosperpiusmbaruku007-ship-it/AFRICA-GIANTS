"""2026-11-22 (founder, option A): D-FIDELITY-24 -- another sector's minimum wage (765,900, energy / international companies) stated as a MINING rate under GN 605A.

The founding specimen is the live reply VERBATIM (eval/results/batch4_deploy_live_2026_11_18.json). Probes both ways (R17): every correct sentence the guard must NOT flag is a probe, including each of the four mining
rates and a correct energy answer. Plants (R26): each limb is disabled to show a test fires. The replacement text is GENERATED from the transcribed schedule and asserted equal to it, so it cannot drift."""
import json
import os
import re

import pytest

from chike import answer_trace, clarification, fidelity
from chike.orchestrator import Orchestrator
from chike.rules_engine import wage_schedule as ws

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Q = "Mshahara wa chini wa sekta ya madini ni kiasi gani kwa mujibu wa GN 605A?"
LIVE_ROW = next(r for r in json.load(open(os.path.join(_ROOT, "eval", "results", "batch4_deploy_live_2026_11_18.json"), encoding="utf-8"))["rows"] if r["q"] == Q)
LIVE = LIVE_ROW["reply"]
MINING = {"brokers": 333_500, "primary licence": 397_600, "dealer": 595_000, "mining and prospecting": 695_000}

FLAG = [
    (Q, LIVE),                                                          # the founding specimen, verbatim
    (Q, "Madini ni TZS 765,900 kwa mwezi."),
    (Q, "Madini na nishati ni TZS 765,900."),
    (Q, "Kima cha chini cha sekta ya uchimbaji madini ni TZS 765,900 kwa mwezi."),
    (Q, "Mining sector minimum wage is TZS 765,900 per month under GN 605A."),
    ("Mchimbaji analipwa kiasi gani kima cha chini?", "Mchimbaji madini anastahili angalau 297,000 kwa mwezi."),      # the domestic-energy rate, same defect
]
PASS = [
    (Q, "Sekta ya madini: TZS 695,000 kwa mwezi (uchimbaji na utafutaji wa madini)."),
    (Q, "Leseni ya madalali (brokers) ni TZS 333,500 kwa mwezi."),
    (Q, "Leseni ya msingi ya uchimbaji madini ni TZS 397,600 kwa mwezi."),
    (Q, "Leseni ya wauzaji wa madini (dealer) ni TZS 595,000 kwa mwezi."),
    (Q, "Madini ina viwango vinne: 333,500; 397,600; 595,000 na 695,000 kwa mwezi, kulingana na aina ya leseni."),
    ("Kima cha chini cha nishati ni kiasi gani?", "Kwa sekta ya nishati, kampuni za kimataifa ni TZS 765,900 na za ndani TZS 297,000."),   # a CORRECT energy answer
    (Q, "Madini: 695,000; nishati: 765,900."),                          # both sectors, each figure after its own subject
    (Q, "Sekta ya madini ni 695,000, wakati nishati (kampuni za kimataifa) ni 765,900."),
    (Q, "Si TZS 765,900 kwa madini; hiyo ni nishati."),                 # a negation
    (Q, "Kiwango cha madini si TZS 765,900; hiyo ni nishati."),         # a negation AFTER the mining cue: only the negation veto saves it (the line above has no cue before its figure)
    ("Mrabaha wa madini ni asilimia ngapi?", "Mrabaha wa madini unalipwa kwa mauzo ya TZS 765,900 na zaidi."),   # not about the minimum wage at all
    ("Kima cha chini cha mshahara kwa mlinzi ni kiasi gani?", "Mlinzi wa kampuni binafsi: TZS 330,000 kwa mwezi."),
]


@pytest.mark.parametrize("q,b", FLAG)
def test_another_sectors_figure_stated_for_mining_is_flagged(q, b):
    assert fidelity.mining_wage_misattributed(q, b), b


@pytest.mark.parametrize("q,b", PASS)
def test_a_correct_or_unrelated_sentence_is_not_flagged(q, b):
    assert fidelity.mining_wage_misattributed(q, b) == [], b


def test_the_founding_specimen_is_the_live_reply_and_names_the_wrong_figure():
    assert "765,900" in LIVE and "madini na nishati" in LIVE and LIVE_ROW.get("path") == "fact"


def test_each_of_the_four_mining_rates_is_in_the_schedule_and_none_is_flagged():
    got = {int(r[-1]) for r in ws.SCHEDULE if r[0] == 10}
    assert got == set(MINING.values())
    for name, amount in MINING.items():
        assert fidelity.mining_wage_misattributed(Q, f"Madini ({name}): TZS {amount:,} kwa mwezi.") == [], name
    assert 765_900 in fidelity._d24_non_mining_figures() and not (set(MINING.values()) & fidelity._d24_non_mining_figures())


def test_765900_is_the_energy_international_row():
    assert [(r[0], r[1]) for r in ws.SCHEDULE if int(r[-1]) == 765_900] == [(7, "a")]


def test_the_replacement_is_generated_from_the_schedule_and_holds_all_four_rates():
    t = clarification.CONSTANT_RESTATEMENTS["gn605a_mining_wage"]
    for amount in MINING.values():
        assert f"{amount:,}" in t
    assert "765,900" in t and "nishati" in t and "Kifungu" not in t and "Vifungu" not in t      # R44
    assert fidelity.mining_wage_misattributed(Q, t) == [] and fidelity.body_contradicts_d16(Q, t) == []     # never trips a guard of its own


# ── plants (R26) ──────────────────────────────────────────────────────────────────────────────────
def test_plant_the_conflation_rule_removed_is_caught(monkeypatch):
    monkeypatch.setattr(fidelity, "_D24_COORD", re.compile(r"(?!x)x"))
    assert [1 for q, b in FLAG if not fidelity.mining_wage_misattributed(q, b)]


def test_plant_the_nearest_subject_rule_made_blind_is_caught(monkeypatch):
    """If every cue counted as mining, the correct per-subject list and the correct energy answer would be flagged."""
    monkeypatch.setattr(fidelity, "_D24_OTHER", r"(?!x)x")
    monkeypatch.setattr(fidelity, "_D24_SUBJECT", re.compile(r"(?P<mining>madini|nishati|energy|mgodi)|(?P<other>(?!x)x)", re.IGNORECASE))
    assert [1 for q, b in PASS if fidelity.mining_wage_misattributed(q, b)]


def test_plant_the_context_requirement_removed_is_caught(monkeypatch):
    monkeypatch.setattr(fidelity, "_D24_CTX", re.compile(r""))
    assert [1 for q, b in PASS if fidelity.mining_wage_misattributed(q, b)]


def test_plant_the_negation_veto_removed_is_caught(monkeypatch):
    monkeypatch.setattr(fidelity, "_D16_NEG", re.compile(r"(?!x)x"))
    assert [1 for q, b in PASS if fidelity.mining_wage_misattributed(q, b)]


def test_plant_every_figure_judged_is_caught(monkeypatch):
    """If the four mining rates were judged too, the correct mining answers would flag."""
    monkeypatch.setattr(fidelity, "_d24_non_mining_figures", lambda: {int(r[-1]) for r in ws.SCHEDULE})
    assert [1 for q, b in PASS if fidelity.mining_wage_misattributed(q, b)]


def test_the_patterns_contain_no_control_characters():
    for p in (fidelity._D24_CTX, fidelity._D24_SUBJECT, fidelity._D24_FIGURE, fidelity._D24_COORD):
        assert not any(ord(c) < 32 for c in p.pattern), p.pattern


# ── wired end to end ──────────────────────────────────────────────────────────────────────────────
class _Backend:
    def __init__(self, reply):
        self.reply, self.calls = reply, 0

    def generate(self, prompt, params=None):
        self.calls += 1
        return self.reply


def _orch(reply):
    b = _Backend(reply)
    return Orchestrator(b, retriever=lambda q: ["Ukweli."], ooc_phrases=[], in_scope_phrases=[]), b


def test_the_live_wrong_reply_is_replaced_end_to_end():
    o, b = _orch(LIVE)
    reply = o.answer(Q)
    t = answer_trace.trace(reply)
    assert b.calls >= 1 and t["guards"] == ["replaced"], t
    assert "madini na nishati ni karibu" not in reply.text
    assert clarification.CONSTANT_RESTATEMENTS["gn605a_mining_wage"] in reply.text
    assert t["model_calls"] and t["model_calls"] > 0          # a model-path reply: never auto-send eligible


@pytest.mark.parametrize("body", ["Sekta ya madini ina viwango vinne vya kima cha chini kwa mwezi: 333,500 hadi 695,000, kulingana na aina ya leseni. Thibitisha na kazi.go.tz.",
                                  "Madini: 695,000; nishati: 765,900."])
def test_a_correct_model_reply_to_the_same_question_is_untouched(body):
    o, _ = _orch(body)
    reply = o.answer(Q)
    assert answer_trace.trace(reply)["guards"] == [] and body.split(".")[0][:30] in reply.text
