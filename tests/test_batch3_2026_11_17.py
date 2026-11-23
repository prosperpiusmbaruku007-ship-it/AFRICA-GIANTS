# -*- coding: utf-8 -*-
"""R17 / R19 / R36 regression file for the 2026-11-17 batch 3 (founder-approved after the targeted verification, PROGRESS 4ax/4ay):
  (2) the mixed-supply 3:2 statement route fires only for a question that NAMES A COMBINED goods+services sale; "do the rates differ for goods vs services?" (eval_039) goes back to its previous path -- probed both ways;
  (3) the training pair that taught "annual return ndani ya miezi 12" is repaired in the authored file AND the export (reach), and no training pair trips the D-FIDELITY-20 guard any more;
  (5) D-FIDELITY-21: a wrong GN 605A SECTOR count is corrected to 16 (the Order's First Schedule), one token, negation untouched.
Founding specimens are read from the committed artifacts, not retyped."""
import glob
import io
import json
import re

import pytest

from chike import fidelity, routing
from chike.model_abstraction import ModelBackend
from chike.orchestrator import Orchestrator

TOPIC = "vat_withholding_mixed_supply"
GOLD = {}
for _f in ("eval_questions_001", "eval_questions_002_additions", "eval_questions_003"):
    for _l in io.open(f"eval/accuracy_gate/{_f}.jsonl", encoding="utf-8"):
        if _l.strip():
            _r = json.loads(_l)
            GOLD[_r["id"]] = _r
Q039 = GOLD["eval_039"]["question_sw"]
TARGETED = {r["id"]: r for r in json.load(open("eval/results/targeted_gate4_2026_11_17.json", encoding="utf-8"))["rows"]}


class _S(ModelBackend):
    def __init__(self, t="JIBU LA MODELI"):
        self.t, self.calls = t, 0

    def generate(self, prompt, params=None):
        self.calls += 1
        return self.t


def _ans(q, body="JIBU LA MODELI"):
    b = _S(body)
    return Orchestrator(backend=b, retriever=lambda *a, **k: ["x"], system_prompt="x").answer(q), b


# ---- (2) the statement route, both ways ----------------------------------------------------------------------------------------------------------------------------------------------------------
ROUTES = [
    "VAT ya zuio inakatwaje kwenye mauzo ya bidhaa na huduma pamoja?",
    "Nauza bidhaa na huduma kwa ankara moja, VAT ya zuio inakatwaje?",
    "VAT withholding kwa mauzo mchanganyiko ya goods and services inakatwaje?",
    "Je, VAT ya zuio kwa mkataba wenye vifaa na huduma inakatwa kwa 6% kwenye thamani yote?",     # the live specimen of the original route
]
DECLINED = [
    Q039,                                                                                         # eval_039 verbatim: a plain "same for goods and services?" rate question
    "Kiwango cha VAT ya zuio kwa bidhaa na kwa huduma ni tofauti?",
    "Do the VAT withholding rates differ for goods and services?",
    "VAT ya zuio kwa bidhaa ni ngapi na kwa huduma ni ngapi?",
    "Kuhusu VAT ya zuio kwa bidhaa na huduma, niambie.",                                         # names goods and services but NOT a combined sale
]


@pytest.mark.parametrize("q", ROUTES)
def test_a_question_naming_a_combined_sale_still_routes_to_the_statement(q):
    assert routing.fixed_statement_topic(q) == TOPIC, q


@pytest.mark.parametrize("q", DECLINED)
def test_a_goods_vs_services_question_goes_back_to_its_previous_path(q):
    assert routing.fixed_statement_topic(q) != TOPIC, q
    # 2026-11-23: a pure goods-vs-services RATE question is now owned by vat_withholding_rates; the invariant (it must not reach the MIXED-supply statement) is unchanged.
    assert routing.detect_intent(q) != "fixed_statement" or routing.fixed_statement_topic(q) == "vat_withholding_rates", q


def test_wired_eval_039_is_answered_by_the_model_path_not_the_mixed_supply_statement():
    r, b = _ans(Q039, "Hapana. Bidhaa 3%, huduma 6%. Thibitisha na TRA (tra.go.tz).")
    assert b.calls >= 1 and "uwiano wa 3:2" not in r.text and r.text.startswith("Hapana"), r.text


def test_the_combined_sale_route_still_answers_model_free():
    r, b = _ans(ROUTES[1])
    assert b.calls == 0 and "uwiano wa 3:2" in r.text


def test_PLANTED_with_the_narrowing_removed_eval_039_is_diverted_again(monkeypatch):
    never = re.compile(r"(?!x)x")        # the OLD route had no 'sawa / tofauti' veto either
    topics = tuple((t[0], t[1], re.compile(r"(?=.*(?:zuio|withhold|zuia|kuzuia|zuiw|kuzuiwa))(?=.*(?:bidhaa\s+na\s+huduma|huduma\s+na\s+bidhaa|goods\s+and\s+services|mixed|mchanganyiko))", re.S), never) if t[0] == TOPIC else t
                   for t in routing._FS_TOPICS)
    monkeypatch.setattr(routing, "_FS_TOPICS", topics)
    assert routing.fixed_statement_topic(Q039) == TOPIC


# ---- (5) D-FIDELITY-21 ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Q117 = GOLD["eval_117"]["question_sw"]
LIVE117 = TARGETED["eval_117"]["reply"]


def test_the_founding_specimen_is_the_live_reply_and_is_repaired_to_16():
    assert "sekta 15" in LIVE117
    out = fidelity.repair_gn605a_sector_count(Q117, LIVE117)
    assert "sekta 16" in out and "sekta 15" not in out and "sekta ndogo 46" in out
    assert fidelity.repair_gn605a_sector_count(Q117, out) == out, "idempotent"


@pytest.mark.parametrize("body,expect", [
    ("GN 605A ina 17 sekta na sekta ndogo 46.", "16 sekta"),
    ("GN 605A inashughulikia sekta 12 kwa jumla.", "sekta 16"),
])
def test_a_wrong_count_is_corrected(body, expect):
    assert expect in fidelity.repair_gn605a_sector_count(Q117, body)


@pytest.mark.parametrize("body", [
    "GN 605A inashughulikia sekta 16 na sekta ndogo 46.",                # already right
    "Si sekta 15, ni sekta 16.",                                          # a NEGATION: rewriting its number would turn a denial into a falsehood
    "GN 605A ina sekta 16; sekta ndogo ni 46 na sekta ndogo 12 ni za kilimo.",   # sub-sector numbers are never matched
    "Kiwango cha mshahara ni TZS 175,000 kwa sekta 3.",                   # not a count question: see the next test
])
def test_correct_denied_or_sub_sector_text_is_untouched(body):
    assert fidelity.repair_gn605a_sector_count(Q117, body) == body


def test_a_question_that_does_not_ask_for_the_sector_count_is_untouched():
    assert fidelity.repair_gn605a_sector_count("Mshahara wa chini wa sekta ya madini ni ngapi?", "Sekta 15 zinahusika.") == "Sekta 15 zinahusika."
    assert fidelity.repair_gn605a_sector_count("Mshahara wa chini wa GN 605A kwa sekta ya madini (sekta 10) ni ngapi?", "Sekta 10 ni madini: TZS 695,000.") == "Sekta 10 ni madini: TZS 695,000."
    assert fidelity.repair_gn605a_sector_count("PAYE ni ngapi?", "sekta 15") == "sekta 15"


def test_wired_the_specimen_is_repaired_through_the_real_orchestrator():
    r, b = _ans(Q117, LIVE117)
    assert b.calls == 1 and "sekta 16" in r.text and "sekta 15" not in r.text and "repaired" in [getattr(s, "guard", "") for s in r.sub_answers], r.text


def test_PLANTED_with_the_repair_removed_the_wrong_count_is_served(monkeypatch):
    monkeypatch.setattr(fidelity, "repair_gn605a_sector_count", lambda q, b: b)
    assert "sekta 15" in _ans(Q117, LIVE117)[0].text


# ---- (3) the training pair, REACH (R36) --------------------------------------------------------------------------------------------------------------------------------------------------------------
REC = json.load(open("eval/results/annual_return_pair_repair_2026_11_17.json", encoding="utf-8"))
OLD_SENTENCE = "Kanuni ya jumla: wasilisha annual return ndani ya miezi 12 ya mwisho wa mwaka wa biashara wako."
Q_PAIR = "Annual return ya BRELA inapaswa kuwasilishwa kabla ya tarehe gani kila mwaka?"


def _stage(pattern):
    out = []
    for p in sorted(glob.glob(pattern)):
        for l in io.open(p, encoding="utf-8"):
            if l.strip():
                try:
                    r = json.loads(l)
                except ValueError:
                    continue
                out.append((r.get("instruction") or r.get("question_sw") or "", r.get("output") or r.get("answer_sw") or ""))
    return out


@pytest.mark.parametrize("pattern", ["datasets/tier1a/sft_shaped_pairs/*.jsonl", "datasets/tier1a/sft/*.jsonl"])
def test_the_repaired_pair_is_in_each_stage_and_the_contradicting_sentence_is_in_neither(pattern):
    rows = _stage(pattern)
    mine = [a for q, a in rows if q == Q_PAIR]
    assert len(mine) == 1, len(mine)
    assert OLD_SENTENCE not in mine[0] and "miezi 12" not in mine[0] and "siku 28" in mine[0] and "anniversary date" in mine[0]
    assert not any(OLD_SENTENCE in a for _q, a in rows)


def test_the_record_holds_both_copies():
    assert len(REC["edited"]) == 2 and {e["new_sha256"] for e in REC["edited"]} == {e["new_sha256"] for e in REC["edited"][:1]}


def test_no_training_pair_trips_the_annual_return_guard_any_more():
    """the standing invariant behind item 3: D-FIDELITY-20 priced 2 training hits (the pair above, authored + export); after the repair it must price 0 over all three corpora of training text"""
    flagged = [(q[:60], s) for pat in ("datasets/tier1a/cleaned_pairs/*.jsonl", "datasets/tier1a/sft_shaped_pairs/*.jsonl", "datasets/tier1a/sft/*.jsonl")
               for q, a in _stage(pat) for t, s in fidelity.body_contradicts_d16(q, a) if t == "brela_annual_return_deadline"]
    assert flagged == [], flagged[:3]


def test_PLANTED_the_invariant_fires_on_the_old_pair_text():
    old = "Hakuna tarehe maalum ya 30 Septemba kwa annual returns za BRELA. " + OLD_SENTENCE
    assert [t for t, _ in fidelity.body_contradicts_d16(Q_PAIR, old)] == ["brela_annual_return_deadline"]
