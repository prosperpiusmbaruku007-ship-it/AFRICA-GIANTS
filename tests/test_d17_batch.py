"""R17 regression file for the 2026-11-17 batch the founder approved after the live check of build a2e6611: (1) unsupported personal names removed, (2) a licence validity period other than twelve months flagged,
(3) the licence-authority cue fixed for real participant phrasings, (4) tax wins over labour on a tax-ask, (5)/(6) two model-free statement routes (individual income-tax return deadline; business-licence validity), (7) lga.go.tz.

Probes: eval/fidelity/d17_batch_probes_2026_11_17.jsonl. The founding specimens are VERBATIM live replies; the clean half is the founder's list and real participant phrasings (R33). Wired through the real orchestrator with a
scripted backend and PLANTED (R26).
"""
import json
import re

import pytest

from chike import answer_trace, fidelity, routing
from chike.model_abstraction import ModelBackend
from chike.orchestrator import Orchestrator
from chike.rules_engine import fixed_statements as fs

PROBES = [json.loads(l) for l in open("eval/fidelity/d17_batch_probes_2026_11_17.jsonl", encoding="utf-8") if l.strip()]


def _verdict(p):
    g, q, b = p["guard"], p["question"], p["body"]
    if g == "names":
        out, rem = fidelity.strip_unsupported_names(b, q, p.get("supported", ""))
        return "strip" if rem else "clean"
    if g == "period":
        return "flag" if fidelity.licence_validity_period_violations(q, b) else "clean"
    if g == "licauth":
        return "repair" if fidelity.repair_licence_authority(q, b) != b else "clean"
    if g == "authtopic":
        t = fidelity.authority_topic(q)
        return t[0] if t else "none"
    if g == "authrepair":
        return "repaired" if fidelity.repair_authority(q, b) != b else "unchanged"
    if g == "gn605a":
        return "repair" if fidelity.repair_gn605a_issuer(q, b) != b else "clean"
    t = routing.fixed_statement_topic(q)
    return t if (t in (fs.INDIVIDUAL_RETURN, fs.LICENCE_VALIDITY) and routing.detect_intent(q) == "fixed_statement") else "none"


def test_probe_file_has_both_halves():
    assert len(PROBES) >= 85
    pos = sum(p["expect"] in ("strip", "flag", "repair", "repaired", "tax", "individual_income_tax_return", "business_licence_validity") for p in PROBES)
    assert pos >= 35 and sum(p["expect"] in ("clean", "unchanged", "none", "labour") for p in PROBES) >= 40


@pytest.mark.parametrize("p", PROBES, ids=[p["id"] for p in PROBES])
def test_probe(p):
    assert _verdict(p) == p["expect"], p["guards_against"]


class _S(ModelBackend):
    def __init__(self, t):
        self.t, self.calls = t, 0

    def generate(self, prompt, params=None):
        self.calls += 1
        return self.t


def _ans(q, body, facts=("x",)):
    b = _S(body)
    return Orchestrator(backend=b, retriever=lambda *a, **k: list(facts), system_prompt="x").answer(q), b


def _spec(i):
    return [p for p in PROBES if p["id"] == i][0]


def _guards(r):
    return [getattr(s, "guard", "") for s in r.sub_answers]


# ---- WIRED -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def test_wired_the_live_gn605a_reply_loses_the_person_and_the_invented_ministry():
    p = _spec("d17_nm_01")
    r, _ = _ans(p["question"], p["body"])
    assert "repaired" in _guards(r) and "Simbachawene" not in r.text and "MHE" not in r.text and "Mawasiliano" not in r.text and "Uchukuzi" not in r.text, r.text
    assert "Waziri wa Nchi, Ofisi ya Waziri Mkuu (Kazi, Vijana, Ajira na Watu Wenye Ulemavu)" in r.text, "the office the Order's own signature block names"
    assert "TanzLII" in r.text and "13 Oktoba 2025" in r.text, "the rest of the reply is untouched"


def test_wired_a_name_the_served_facts_carry_is_kept():
    p = _spec("d17_nm_15")
    r, _ = _ans(p["question"], p["body"], facts=(p["supported"],))
    assert "Kassim Majaliwa" in r.text, r.text


def test_wired_the_period_specimen_is_replaced_by_the_locked_statement():
    p = _spec("d17_pd_01")
    # the route declines the TWO-PART phrasing, so the guard is what the user depends on
    r, b = _ans("Nahitaji leseni ya biashara, inagharimu kiasi gani na inaisha lini?", p["body"])
    assert "replaced" in _guards(r) and "siku 90" not in r.text and "miezi 12" in r.text, r.text


def test_wired_the_severance_tax_question_keeps_the_tax_authority():
    p = _spec("d17_tx_06")
    r, _ = _ans(p["question"], "Malipo yanaweza kuwa sehemu ya mapato ya ajira. Thibitisha na TRA (tra.go.tz).")
    assert "kazi.go.tz" not in r.text and "tra.go.tz" in r.text, r.text
    r2, _ = _ans(p["question"], p["body"])
    assert "kazi.go.tz" not in r2.text and "tra.go.tz" in r2.text, r2.text


@pytest.mark.parametrize("pid", ["d17_rt_01", "d17_rt_07", "d17_rt_08", "d17_rt_09"])
def test_the_routed_specimens_are_answered_model_free_with_the_whole_statement(pid):
    p = _spec(pid)
    r, b = _ans(p["question"], "JIBU LA MODELI")
    t = answer_trace.trace(r)
    topic = p["expect"]
    assert t["path"] == "engine:fixed_statement" and t["model_calls"] == 0 and b.calls == 0, t
    assert fs.fixed_statement(topic).working in r.text and "JIBU LA MODELI" not in r.text


def test_the_individual_return_statement_says_six_months_and_30_june_and_no_cag_limb():
    t = fs.fixed_statement(fs.INDIVIDUAL_RETURN).working
    assert "miezi 6" in t and "30 Juni" in t and "CAG" not in t and "miezi 9" not in t
    assert "Kifungu" not in t and "Vifungu" not in t, "R44"


def test_the_licence_statement_says_twelve_months_and_both_authorities_and_no_section_number():
    t = fs.fixed_statement(fs.LICENCE_VALIDITY).working
    assert "miezi 12" in t and "miaka 3" in t and "halmashauri" in t and "BRELA" in t and "kundi A" in t and "Gazeti" in t
    assert "Kifungu" not in t and "Vifungu" not in t, "R44"
    # it names the OLD dates only under negation, so it cannot trip the very guard it sits beside
    assert not fidelity.constant_violations("Leseni ya biashara inaisha lini?", t)
    assert not fidelity.licence_validity_period_violations("Leseni ya biashara inaisha lini?", t)


def test_both_new_statements_are_registered_and_excluded_from_auto_send():
    import importlib.util
    spec = importlib.util.spec_from_file_location("hc17", "chike-whatsapp/handler_core.py")
    hc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hc)
    for t in (fs.INDIVIDUAL_RETURN, fs.LICENCE_VALIDITY):
        assert t in fs.TOPICS and "engine:fixed_statement" in hc.AUTOSEND_EXCLUDED_ENGINE_ROUTES
    assert "engine:fixed_statement" not in hc.AUTOSEND_ELIGIBLE_ENGINE_ROUTES
    r, _ = _ans("Leseni ya biashara inaisha lini?", "x")
    ok, why = hc.engine_only_verdict({"answer_path": "engine:fixed_statement", "engine_working": fs.fixed_statement(fs.LICENCE_VALIDITY).working, "model_calls": 0, "guards": [], "facts": ["f"], "fallback": False})
    assert ok is False and "excluded" in why, why


# ---- PLANTED (R26): with each trigger disabled the specimen must reach the user --------------------------------------------------------------------------------------------------------
def test_planted_name_guard_disabled_lets_the_name_through(monkeypatch):
    monkeypatch.setattr(fidelity, "strip_unsupported_names", lambda body, q="", s="": (body, []))
    monkeypatch.setattr(fidelity, "repair_gn605a_issuer", lambda q, b: b)
    p = _spec("d17_nm_01")
    r, _ = _ans(p["question"], p["body"])
    assert "Simbachawene" in r.text


def test_planted_period_guard_disabled_lets_siku_90_through(monkeypatch):
    monkeypatch.setattr(fidelity, "licence_validity_period_violations", lambda q, b: [])
    r, _ = _ans("Nahitaji leseni ya biashara, inagharimu kiasi gani na inaisha lini?", _spec("d17_pd_01")["body"])
    assert "siku 90" in r.text


def test_planted_routes_disabled_lose_their_specimens(monkeypatch):
    for pid in ("d17_rt_01", "d17_rt_07"):
        monkeypatch.setattr(routing, "_FS_TOPICS", tuple(t for t in routing._FS_TOPICS if t[0] not in ("individual_income_tax_return", "business_licence_validity")))
        assert routing.fixed_statement_topic(_spec(pid)["question"]) is None


def test_planted_tax_priority_removed_recreates_the_wrong_authority(monkeypatch):
    monkeypatch.setattr(fidelity, "_AUTH_TAX_ASK", re.compile(r"(?!x)x"))
    p = _spec("d17_tx_06")
    assert fidelity.repair_authority(p["question"], "Thibitisha na TRA (tra.go.tz).") != "Thibitisha na TRA (tra.go.tz)."


def test_planted_licence_cue_reverted_recreates_the_np13_miss(monkeypatch):
    monkeypatch.setattr(fidelity, "_D16_LICENCE_Q", re.compile(r"leseni\s+(?:ya|yangu|za)\s*(?:biashara|duka)|business\s+licen[cs]e", re.IGNORECASE))
    p = _spec("d17_cue_01")
    assert fidelity.repair_licence_authority(p["question"], p["body"]) == p["body"]


def test_every_new_pattern_contains_no_control_characters():
    """R39: a non-raw `\\b` is a backspace and the source still LOOKS right."""
    pats = [fidelity._NAME_AFTER_HONORIFIC, fidelity._NAME_AFTER_OFFICE, fidelity._NAME_PAREN, fidelity._OFFICE_WORD, fidelity._C17_VALIDITY_S, fidelity._C17_SKIP_S, fidelity._C17_PERIOD, fidelity._D16_LICENCE_Q,
            fidelity._D16_GN605A_MINISTER, fidelity._AUTH_TAX_ASK]
    pats += [c for t in routing._FS_TOPICS if t[0] in ("individual_income_tax_return", "business_licence_validity") for c in t[1:] if c is not None]
    pats += [routing._FS_TOPIC_ASK["individual_income_tax_return"], routing._FS_TOPIC_ASK["business_licence_validity"]]
    for p in pats:
        assert not any(ord(c) < 32 for c in p.pattern), p.pattern


def test_the_name_guard_is_idempotent():
    for p in [x for x in PROBES if x["guard"] == "names"]:
        once, _ = fidelity.strip_unsupported_names(p["body"], p["question"], p.get("supported", ""))
        twice, rem = fidelity.strip_unsupported_names(once, p["question"], p.get("supported", ""))
        assert twice == once and not rem, p["id"]


def test_the_licence_authority_repair_is_idempotent_and_never_names_lga():
    for pid in ("d17_cue_01", "d17_cue_09", "d17_cue_10"):
        p = _spec(pid)
        once = fidelity.repair_licence_authority(p["question"], p["body"])
        assert fidelity.repair_licence_authority(p["question"], once) == once
        assert "lga.go.tz" not in once and "mlywf.go.tz" not in once
