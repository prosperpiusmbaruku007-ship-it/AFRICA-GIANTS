"""R17 regression file for the 2026-11-16 np_ batch of guards (founder): annual leave outside 28 (np_12), severance qualifying months (np_05), licence expiry (np_13), record-keeping period (np_20),
TIN deadline (np_26), and a shilling amount derived for a payroll levy with no figure given on the FACT path (np_28 / th_22).

27 probes in eval/fidelity/constant_guards_probes_2026_11_16.jsonl: the founding specimens are VERBATIM live replies from eval/results/negated_premise_live_2026_11_16.json, and 16 are clean (R17: the half that
does the work). Wired end to end through the real orchestrator with a scripted backend, and PLANTED: each trigger is disabled and the specimen must then reach the user (R26).
"""
import json

import pytest

from chike import clarification, fidelity
from chike.model_abstraction import ModelBackend
from chike.orchestrator import Orchestrator

PROBES = [json.loads(l) for l in open("eval/fidelity/constant_guards_probes_2026_11_16.jsonl", encoding="utf-8") if l.strip()]


def _flags(p):
    g, q, b = p["guard"], p["question"], p["body"]
    if g in ("leave", "severance"):
        return bool(fidelity.fixed_figure_violations(q, b))
    if g == "constant":
        return fidelity.body_contradicts_constant(q, b)
    return fidelity.body_states_derived_levy_amount(q, b)


def test_probe_file_has_both_halves():
    assert len(PROBES) == 29 and sum(p["expect"] == "flag" for p in PROBES) == 13 and sum(p["expect"] == "clean" for p in PROBES) == 16


@pytest.mark.parametrize("p", PROBES, ids=[p["id"] for p in PROBES])
def test_probe(p):
    assert _flags(p) == (p["expect"] == "flag"), p["guards_against"]


class _Scripted(ModelBackend):
    def __init__(self, text):
        self.text = text

    def generate(self, prompt, params=None):
        return self.text


def _answer(question, body):
    return Orchestrator(backend=_Scripted(body), retriever=lambda *_a, **_k: ["x"], system_prompt="x").answer(question)


def _spec(i):
    return [p for p in PROBES if p["id"] == i][0]


def _replaced(r):
    return any(getattr(s, "guard", "") == "replaced" for s in r.sub_answers)


@pytest.mark.parametrize("pid,must_contain,must_not", [
    ("cg_03", "miezi 12", "inatakiwa kuwa updated"), ("cg_04", "miaka 5", "mitatu"), ("cg_05", "siku 15", "Hakuna siku maalum"),
])
def test_wired_constants_replace_the_specimen_with_the_locked_statement(pid, must_contain, must_not):
    p = _spec(pid)
    # 2026-11-17: the licence question itself now routes to the model-free validity statement (no guard needed); the guard is the SECOND layer for a phrasing the route declines (renewal + a late-renewal penalty in one sentence: the veto declines it).
    q = {"cg_03": "Leseni ya biashara ya LGA inaisha lini na adhabu ya kuchelewa ni ngapi?", "cg_05": "Naomba TIN baada ya kuanza biashara, adhabu ya kuchelewa ni nini?"}.get(pid, p["question"])   # cg_05: the TIN question itself routes to the model-free TIN statement since 2026-11-17
    r = _answer(q, p["body"])
    assert must_contain in r.text and must_not not in r.text and _replaced(r), r.text


def test_np_28_itself_now_routes_to_the_model_free_rate_statement():
    """The route fix (asilimia ngapi ... WCF) takes np_28's own question off the fact path entirely: no model call, so no figure can be invented. The guard below is the second layer for the th_22 phrasing."""
    p = _spec("cg_06")
    r = _answer(p["question"], p["body"])
    assert r.model_calls == 0 and "30,000" not in r.text and "0.5" in r.text, r.text


FACT_PATH_AMOUNT_Q = "Nina wafanyakazi 6, nisaidie kuelewa mchango wa WCF unavyofanya kazi"   # verified: detect_intent 'none', so it reaches the fact path the guard is wired on (th_22's own question reaches the COMPUTE path, where D-FIDELITY-9 already blanks it)


def test_wired_amount_is_replaced_with_the_rate_and_a_request_for_the_payroll():
    p = _spec("cg_06")
    r = _answer(FACT_PATH_AMOUNT_Q, p["body"])
    assert "30,000" not in r.text and "0.5" in r.text and "jumla ya mishahara" in r.text.lower() and _replaced(r), r.text


@pytest.mark.parametrize("pid", ["cg_12", "cg_18", "cg_20", "cg_24"])
def test_wired_correct_bodies_pass_through_untouched(pid):
    p = _spec(pid)
    r = _answer(p["question"], p["body"])
    assert not _replaced(r), r.text


@pytest.mark.parametrize("fn,pid", [("body_contradicts_constant", "cg_03"), ("body_contradicts_constant", "cg_04"), ("body_contradicts_constant", "cg_05"),
                                    ("body_states_derived_levy_amount", "cg_06")])
def test_planted_trigger_disabled_lets_the_specimen_through(monkeypatch, fn, pid):
    monkeypatch.setattr(fidelity, fn, lambda q, b: False)
    p = _spec(pid)
    r = _answer(FACT_PATH_AMOUNT_Q if pid == "cg_06" else p["question"], p["body"])
    assert not _replaced(r), "with the guard disabled the specimen must reach the user, or the wiring tests above prove nothing"


def test_restatements_carry_the_locked_figures_and_no_section_number():
    facts = json.load(open("scripts/locked_facts.json", encoding="utf-8"))
    facts = facts.get("facts", facts)
    facts = facts if isinstance(facts, dict) else {f["key"]: f for f in facts}
    for topic, needle in (("business_licence_expiry", "miezi 12"), ("record_keeping_period", "miaka 5"), ("tin_apply_deadline", "siku 15")):
        key = {"business_licence_expiry": "business_licence_expiry_30_june"}.get(topic, topic)
        assert needle in clarification.CONSTANT_RESTATEMENTS[topic] and needle.lower() in json.dumps(facts[key], ensure_ascii=False).lower(), topic
    for t in clarification.CONSTANT_RESTATEMENTS.values():
        assert "Kifungu" not in t and "Vifungu" not in t, "R44"
