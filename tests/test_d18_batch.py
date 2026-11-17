"""R17 regression file for the founder's NEXT SMALL BATCH of 2026-11-17: (1) a model-free TIN-application statement route (np_14 / np_26 / s2_08), (2) the VAT engine reads an amount that carries its own period beside a bound
(np_22), (3) a practitioner FIRM named as the authority to confirm with is repaired, (4) the repeated "Thibitisha na ..." sentence, (5) the two-part licence FEE + RENEWAL question answered whole.

Probes: eval/fidelity/d18_batch_probes_2026_11_17.jsonl (founding specimens VERBATIM; the clean half is every neighbour the code must not touch). Wired through the real orchestrator with a scripted backend and PLANTED (R26).
"""
import json
import re

import pytest

from chike import answer_trace, fidelity, routing
from chike.model_abstraction import ModelBackend
from chike.orchestrator import Orchestrator
from chike.rules_engine import fixed_statements as fs

PROBES = [json.loads(l) for l in open("eval/fidelity/d18_batch_probes_2026_11_17.jsonl", encoding="utf-8") if l.strip()]
FACTS = json.load(open("scripts/locked_facts.json", encoding="utf-8"))
NEW = ("tin_apply_deadline", "business_licence_fee_and_validity")


def _verdict(p):
    g, q, b = p["guard"], p["question"], p["body"]
    if g == "vat":
        r = routing.turnover_with_local_period(q)
        return "none" if r is None else f"{int(r[0])}|{r[1]}"
    if g == "firm":
        return "repair" if fidelity.repair_firm_authority(q, b) != b else "clean"
    if g == "dedupe":
        return "dedupe" if fidelity._drop_redundant_confirm_tail(b) != b else "clean"
    if g == "licdead":
        return "repair" if fidelity.repair_licence_authority(q, b) != b else "clean"
    t = routing.fixed_statement_topic(q)
    if p["expect"] == "none_of_new":
        return "none_of_new" if t not in NEW else t
    return t if (t == p["expect"] and routing.detect_intent(q) == "fixed_statement") else str(t)


@pytest.mark.parametrize("p", PROBES, ids=[p["id"] for p in PROBES])
def test_probe(p):
    assert _verdict(p) == p["expect"], p["guards_against"]


@pytest.mark.parametrize("p", [x for x in PROBES if x["guard"] == "firm" and x["expect"] == "repair"], ids=lambda x: x["id"])
def test_firm_repair_output(p):
    out = fidelity.repair_firm_authority(p["question"], p["body"])
    assert p["contains"] in out and p["absent"].lower() not in out.lower(), out
    assert fidelity.repair_firm_authority(p["question"], out) == out, "idempotent"
    assert not re.search(r"\)\.[a-z]|\.com\)", out), "no stranded fragment of a host"


def test_the_repeated_confirm_sentence_is_dropped_and_the_dead_host_goes_too():
    p = [x for x in PROBES if x["id"] == "d18_dd_04"][0]
    out = fidelity.repair_licence_authority(p["question"], p["body"])
    assert "lga.go.tz" not in out and out.count("Thibitisha na halmashauri husika") == 1, out
    assert out == "Kupoteza leseni ni tatizo. Thibitisha na halmashauri husika ili kujua utaratibu sahihi wa kuitafuta upya.", out
    assert fidelity.repair_licence_authority(p["question"], out) == out, "idempotent"


class _S(ModelBackend):
    def __init__(self, t):
        self.t, self.calls = t, 0

    def generate(self, prompt, params=None):
        self.calls += 1
        return self.t


def _ans(q, body="JIBU LA MODELI", facts=("x",)):
    b = _S(body)
    return Orchestrator(backend=b, retriever=lambda *a, **k: list(facts), system_prompt="x").answer(q), b


def _spec(i):
    return [p for p in PROBES if p["id"] == i][0]


# ---- (2) np_22, end to end ----------------------------------------------------------------------------------------------------------------------------------------------------------
def test_np22_is_answered_by_the_engine_and_says_register():
    q = _spec("d18_vat_01")["question"]
    r, b = _ans(q)
    t = answer_trace.trace(r)
    assert t["path"].startswith("engine:vat_registration") and not t["path"].endswith(":ask"), t
    assert "110,000,000" in r.text and re.search(r"(?i)lazima|unatakiwa|ni wa lazima", r.text), r.text
    assert "niambie" not in r.text.lower(), "it must no longer ask for the sales figures"


def test_planted_the_resolver_removed_recreates_the_np22_clarification(monkeypatch):
    monkeypatch.setattr(routing, "turnover_with_local_period", lambda text: None)
    r, _ = _ans(_spec("d18_vat_01")["question"])
    assert answer_trace.trace(r)["path"].endswith(":ask"), answer_trace.trace(r)


# ---- (1) + (5): the two statements, model-free and whole -----------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("pid", ["d18_rt_01", "d18_rt_02", "d18_rt_03", "d18_rt_04"])
def test_the_tin_specimens_are_answered_model_free_with_the_whole_statement(pid):
    r, b = _ans(_spec(pid)["question"])
    t = answer_trace.trace(r)
    assert t["path"] == "engine:fixed_statement" and t["model_calls"] == 0 and b.calls == 0, t
    assert fs.fixed_statement(fs.TIN_APPLY).working in r.text and "JIBU LA MODELI" not in r.text
    assert "siku 15" in r.text and "siku 7" in r.text and "Hakuna siku maalum" not in r.text


def test_the_tin_statement_figures_equal_the_served_row_and_the_locked_fact():
    import sys
    sys.path.insert(0, "scripts")
    import precompute_rag_embeddings as pre
    key, text, _ = fs.STATEMENTS[fs.TIN_APPLY]
    nums = lambda x: sorted(set(re.findall(r"\d+", x)))
    assert nums(text) == nums(pre.CONCISE_BILINGUAL_FACTS[key]) == ["15", "7"]
    for n in re.findall(r"\d+", FACTS[key]["correct_value"]):
        assert n in text
    assert "Kifungu" not in text and "Vifungu" not in text, "R44"


@pytest.mark.parametrize("pid", ["d18_rf_01", "d18_rf_02", "d18_rf_03", "d18_rf_04"])
def test_the_two_part_licence_question_gets_BOTH_limbs_model_free(pid):
    r, b = _ans(_spec(pid)["question"])
    t = answer_trace.trace(r)
    assert t["path"] == "engine:fixed_statement" and t["model_calls"] == 0 and b.calls == 0, t
    assert "KITAIFA" in r.text and "halmashauri hairuhusiwi kutoza zaidi" in r.text, "the FEE limb"
    assert "miezi 12" in r.text and "miaka 3" in r.text and "kundi A" in r.text, "the RENEWAL limb"
    assert not fidelity.constant_violations("Leseni ya biashara inaisha lini?", r.text), "the statement names the old dates only under negation"


def test_the_fee_limb_is_lifted_from_the_locked_fee_fact_and_states_no_fee_figure():
    text = fs.fixed_statement(fs.LICENCE_FEE_VALIDITY).working
    fee = FACTS["business_licence_fee_national_schedule_local_collection"]["fact"]
    norm = lambda x: re.sub(r"[^a-z/]+", " ", x.lower())
    for clause in ("ada imepangwa kitaifa chini ya sheria ya leseni za biashara", "halmashauri hairuhusiwi kutoza zaidi ya ada iliyopangwa", "uliza halmashauri yako kwa ada ya aina yako"):
        assert norm(clause) in norm(fee) and norm(clause) in norm(text), clause
    assert "leseni hutolewa na kukusanywa na halmashauri" not in text, "dropped: it would contradict the Category A limb inside one answer"
    assert not re.search(r"TZS|shilingi|\d{3,}", text.split("Kuhusu muda")[0]), "no fee amount is stated"
    assert "Kifungu" not in text and "Vifungu" not in text, "R44"


def test_a_fee_only_and_a_renewal_only_question_keep_their_own_routes():
    assert routing.fixed_statement_topic("Ada ya leseni ya biashara ni kiasi gani?") is None
    assert routing.fixed_statement_topic("Leseni ya biashara inaisha lini?") == "business_licence_validity"


def test_both_new_statements_are_registered_and_excluded_from_auto_send():
    import importlib.util
    spec = importlib.util.spec_from_file_location("hc18", "chike-whatsapp/handler_core.py")
    hc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hc)
    for t in NEW:
        assert t in fs.TOPICS
    assert fs.LICENCE_FEE_VALIDITY in fs.TOPICS_NO_CONCISE_ROW and fs.TIN_APPLY not in fs.TOPICS_NO_CONCISE_ROW
    assert "engine:fixed_statement" in hc.AUTOSEND_EXCLUDED_ENGINE_ROUTES and "engine:fixed_statement" not in hc.AUTOSEND_ELIGIBLE_ENGINE_ROUTES


# ---- (3): the repair wired end to end ---------------------------------------------------------------------------------------------------------------------------------------------
def test_wired_a_firm_named_as_the_authority_is_replaced():
    p = _spec("d18_fm_01")
    r, _ = _ans(p["question"], p["body"])
    assert "VELMA" not in r.text and "Thibitisha na Ofisi ya Kazi (kazi.go.tz)" in r.text and "repaired" in [getattr(s, "guard", "") for s in r.sub_answers], r.text


def test_planted_the_firm_repair_disabled_lets_the_firm_through(monkeypatch):
    monkeypatch.setattr(fidelity, "repair_firm_authority", lambda q, b: b)
    p = _spec("d18_fm_01")
    r, _ = _ans(p["question"], p["body"])
    assert "VELMA Law" in r.text


def test_planted_routes_disabled_lose_their_specimens(monkeypatch):
    monkeypatch.setattr(routing, "_FS_TOPICS", tuple(t for t in routing._FS_TOPICS if t[0] not in NEW))
    for pid in ("d18_rt_02", "d18_rf_01"):
        assert routing.fixed_statement_topic(_spec(pid)["question"]) is None


def test_every_new_pattern_contains_no_control_characters():
    """R39."""
    pats = [fidelity._FIRM_NAMES_CI, fidelity._FIRM_EY, fidelity._CONFIRM_TAIL, fidelity._TAIL_SPLIT, routing._BOUND_VERB_RE, routing._LOWER_VERB_RE]
    pats += [re.compile(pat) for _, pat in routing._LOCAL_PERIOD_CUES]
    pats += [c for t in routing._FS_TOPICS if t[0] in NEW for c in t[1:] if c is not None]
    pats += [routing._FS_TOPIC_ASK[t] for t in NEW]
    for p in pats:
        assert not any(ord(c) < 32 for c in p.pattern), p.pattern
