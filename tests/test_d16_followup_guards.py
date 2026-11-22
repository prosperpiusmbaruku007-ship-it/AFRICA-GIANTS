"""R17 regression file for the 2026-11-17 follow-up (founder-approved): licence validity CORRECTED (a fixed calendar date is wrong; Business Licensing Act Cap.101 R.E.2023 s.7(1) says twelve months from
issuance), D-FIDELITY-16 (a non-resident dividend at 15%, a company return deadline of 12 months / 30 September, a flat 15% on severance), two single-clause repairs (PKF named as the issuer of GN 605A; a business-licence
citation that is BRELA alone or a non-licence authority), plus the locked facts and prospective index rows they rest on.

41 probes in eval/fidelity/d16_followup_probes_2026_11_17.jsonl: the founding specimens are VERBATIM live replies; the clean half is the must-pass list the founder named. Wired through the real orchestrator with a
scripted backend and PLANTED (R26): each trigger is disabled and the specimen must then reach the user.
"""
import json
import re

import pytest

from chike import clarification, fidelity
from chike.model_abstraction import ModelBackend
from chike.orchestrator import Orchestrator

PROBES = [json.loads(l) for l in open("eval/fidelity/d16_followup_probes_2026_11_17.jsonl", encoding="utf-8") if l.strip()]
FACTS = json.load(open("scripts/locked_facts.json", encoding="utf-8"))


def _verdict(p):
    g, q, b = p["guard"], p["question"], p["body"]
    if g == "licence":
        return "flag" if fidelity.constant_violations(q, b) else "clean"
    if g in ("dividend", "return", "severance"):
        return "flag" if fidelity.body_contradicts_d16(q, b) else "clean"
    if g == "pkf":
        return "repair" if fidelity.repair_gn605a_issuer(q, b) != b else "clean"
    return "repair" if fidelity.repair_licence_authority(q, b) != b else "clean"


def test_probe_file_has_both_halves():
    assert len(PROBES) == 41
    assert sum(p["expect"] in ("flag", "repair") for p in PROBES) == 14 and sum(p["expect"] == "clean" for p in PROBES) == 27


@pytest.mark.parametrize("p", PROBES, ids=[p["id"] for p in PROBES])
def test_probe(p):
    assert _verdict(p) == p["expect"], p["guards_against"]


class _S(ModelBackend):
    def __init__(self, t):
        self.t = t

    def generate(self, prompt, params=None):
        return self.t


def _ans(q, body):
    return Orchestrator(backend=_S(body), retriever=lambda *a, **k: ["x"], system_prompt="x").answer(q)


def _spec(i):
    return [p for p in PROBES if p["id"] == i][0]


def _guard(r):
    return [getattr(s, "guard", "") for s in r.sub_answers]


@pytest.mark.parametrize("pid,must,must_not", [
    ("d16_lic_01", "miezi 12", "ifikapo tarehe 30 Juni"),
    ("d16_div_01", "5% (kampuni iliyoorodheshwa", "15% kwa wasio wakazi"),
    ("d16_ret_01", "ndani ya miezi 6", "ndani ya miezi 12"),
    ("d16_sev_01", "hakuna kiwango maalum cha asilimia 15", "inatozwa kodi ya asilimia 15"),
])
def test_wired_specimen_is_replaced_by_the_locked_statement(pid, must, must_not):
    p = _spec(pid)
    # 2026-11-17: the licence question routes to the model-free statement now; the guard is the second layer for a phrasing the route declines (renewal + a late-renewal penalty in one sentence).
    q = "Leseni ya biashara ya LGA inaisha lini na adhabu ya kuchelewa ni ngapi?" if pid == "d16_lic_01" else p["question"]
    r = _ans(q, p["body"])
    assert "replaced" in _guard(r) and must_not not in r.text and (must in r.text or must.replace("ro", "r") in r.text), r.text


def test_wired_pkf_is_repaired_not_replaced():
    p = _spec("d16_pkf_01")
    r = _ans(p["question"], p["body"])
    assert "repaired" in _guard(r) and "PKF" not in r.text and "lililotolewa na Serikali" in r.text and "kazi.go.tz" in r.text, r.text


def test_wired_licence_authority_is_repaired():
    p = _spec("d16_auth_01")
    r = _ans(p["question"], p["body"])
    assert "repaired" in _guard(r) and "halmashauri yako, au BRELA kwa kundi A" in r.text, r.text


@pytest.mark.parametrize("pid", ["d16_lic_04", "d16_div_05", "d16_ret_06", "d16_sev_05", "d16_pkf_03", "d16_auth_03"])
def test_wired_correct_bodies_pass_through_untouched(pid):
    p = _spec(pid)
    r = _ans(p["question"], p["body"])
    assert not any(g in ("replaced", "repaired") for g in _guard(r)), r.text


@pytest.mark.parametrize("pid,attr", [("d16_lic_01", "constant_violations"), ("d16_div_01", "body_contradicts_d16"), ("d16_ret_01", "body_contradicts_d16"), ("d16_sev_01", "body_contradicts_d16")])
def test_planted_trigger_disabled_lets_the_specimen_through(monkeypatch, pid, attr):
    """With the guard disabled the specimen must reach the user, or the wiring tests above prove nothing (R26)."""
    monkeypatch.setattr(fidelity, attr, lambda q, b: [])
    if attr == "constant_violations":
        monkeypatch.setattr(fidelity, "body_contradicts_constant", lambda q, b: False)
    p = _spec(pid)
    assert "replaced" not in _guard(_ans(p["question"], p["body"]))


@pytest.mark.parametrize("pid,fn", [("d16_pkf_01", "repair_gn605a_issuer"), ("d16_auth_01", "repair_licence_authority")])
def test_planted_repair_disabled_lets_the_specimen_through(monkeypatch, pid, fn):
    monkeypatch.setattr(fidelity, fn, lambda q, b: b)
    p = _spec(pid)
    r = _ans(p["question"], p["body"])
    assert "repaired" not in _guard(r)


@pytest.mark.parametrize("pid,fn", [("d16_pkf_01", fidelity.repair_gn605a_issuer), ("d16_pkf_02", fidelity.repair_gn605a_issuer), ("d16_auth_01", fidelity.repair_licence_authority), ("d16_auth_02", fidelity.repair_licence_authority)])
def test_repairs_are_idempotent(pid, fn):
    p = _spec(pid)
    once = fn(p["question"], p["body"])
    assert fn(p["question"], once) == once


def test_the_restatements_do_not_trip_their_own_guards_and_carry_no_section_number():
    for topic in ("business_licence_expiry", "dividend_nonresident_rate", "corporate_return_deadline", "severance_flat_15"):
        t = clarification.CONSTANT_RESTATEMENTS[topic]
        assert "Kifungu" not in t and "Vifungu" not in t, f"R44: {topic}"
    assert not fidelity.constant_violations("Leseni ya biashara inaisha lini?", clarification.CONSTANT_RESTATEMENTS["business_licence_expiry"])
    assert not fidelity.body_contradicts_d16("Gawio kwa mgeni linakatwa kiasi gani?", clarification.CONSTANT_RESTATEMENTS["dividend_nonresident_rate"])
    assert not fidelity.body_contradicts_d16("Muda wa mwisho wa return ya kodi ya mapato ya kampuni ni lini?", clarification.CONSTANT_RESTATEMENTS["corporate_return_deadline"])
    assert not fidelity.body_contradicts_d16("Severance inakatwa kodi gani?", clarification.CONSTANT_RESTATEMENTS["severance_flat_15"])


def test_restatements_carry_the_figures_the_locked_facts_state():
    pairs = {"business_licence_expiry": ("business_licence_expiry_30_june", ["miezi 12", "miaka 3"]),
             "dividend_nonresident_rate": ("dividend_withholding_rate", ["5%", "10%"]),
             "corporate_return_deadline": ("corporate_income_tax_return", ["miezi 6", "30 Juni", "miezi 9", "TZS 100,000,000"]),
             "severance_flat_15": ("severance_pay_income_tax", ["asilimia 15"])}
    for topic, (key, needles) in pairs.items():
        for n in needles:
            assert n in clarification.CONSTANT_RESTATEMENTS[topic] and n in FACTS[key]["fact"], (topic, n)


# ---- the locked facts ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
def test_licence_fact_states_twelve_months_and_records_the_superseded_value():
    f = FACTS["business_licence_expiry_30_june"]
    assert "miezi 12" in f["fact"] and "CORRECTED" in f["status"] and f["superseded_value"] and f["verified_by"]
    assert "Cap.101 R.E.2023" in f["primary_source"] and "s.7" in f["primary_source"]
    # the fact may NAME 30 June only as the rejected value
    for m in re.finditer(r"30 Juni|30 June", f["fact"]):
        assert re.search(r"(SI|si|was replaced|former)[^.]{0,40}$", f["fact"][max(0, m.start() - 60):m.end() + 40]) or "ilibadilishwa" in f["fact"], f["fact"]


@pytest.mark.parametrize("key", ["corporate_income_tax_return", "business_licence_authority", "gn605a_issuer", "severance_pay_income_tax", "business_licence_expiry_30_june", "dividend_withholding_rate"])
def test_followup_facts_carry_primary_source_and_verification(key):
    f = FACTS[key]
    assert f.get("primary_source") and f.get("verified_by") and f.get("verified_as_at") == "2026-11-17", key
    for w in f.get("wrong_patterns", []):
        assert not re.search(w, f["fact"], re.IGNORECASE | re.DOTALL), f"{key}: the fact's own text matches its wrong_pattern {w!r} (R20, the borrowed-detector arrival)"


def test_corporate_return_fact_includes_the_amending_acts_and_the_renumbering():
    f = FACTS["corporate_income_tax_return"]
    s = f["primary_source"]
    assert "Finance Act 2024" in s and "Finance Act 2025" in s and "nine-month" in s and "one hundred million" in s and "renumbers" in s


def test_gn605a_fact_records_that_the_average_rests_on_press_sources():
    assert "NOT on the Order" in FACTS["gn605a_issuer"]["verified_by"]
    assert "NOT in GN 605A" in FACTS["gn605a_average_increase"]["_source_tier_note"]


def test_licence_authority_fact_says_portal_tier():
    f = FACTS["business_licence_authority"]
    assert "PORTAL TIER" in f["verified_by"] and "Gazette" in f["primary_source"] and "portal tier" in f["status"]


def test_dividend_fact_carries_the_treaty_caveat_and_no_section_number_in_served_text():
    f = FACTS["dividend_withholding_rate"]["fact"]
    assert "mkataba" in f.lower() and "asiye mkazi" in f and "15% si kiwango cha gawio" in f
    assert "Kifungu" not in f


# ---- the prospective index rows ------------------------------------------------------------------------------------------------------------------------------------------------------------
def test_prospective_index_rows_carry_the_corrected_content_and_clear_their_own_wrong_patterns():
    import sys
    sys.path.insert(0, "scripts")
    import precompute_rag_embeddings as p
    texts, keys, _ = p.build_fact_texts()
    by = dict(zip(keys, texts))
    assert "halali kwa miezi 12 tangu tarehe ilipotolewa" in by["business_licence_expiry_30_june"] and not by["business_licence_expiry_30_june"].lower().startswith("business licence expiry 30 june")
    assert "ni vilevile kwa mpokeaji asiye mkazi" in by["dividend_withholding_rate"]
    assert "kampuni ya kawaida (mwaka wa kalenda) kufikia 30 Juni" in by["corporate_income_tax_return"]
    assert "leseni za kundi A" in by["business_licence_authority"] and "Si PKF" in by["gn605a_issuer"] and "hakuna kiwango maalum cha asilimia 15" in by["severance_pay_income_tax"]
    for k in ("business_licence_expiry_30_june", "dividend_withholding_rate", "corporate_income_tax_return", "business_licence_authority", "gn605a_issuer", "severance_pay_income_tax"):
        for w in FACTS[k].get("wrong_patterns", []):
            assert not re.search(w, by[k], re.IGNORECASE | re.DOTALL), f"index row {k} matches its own wrong_pattern {w!r}"
        assert "Kifungu" not in by[k] and "Vifungu" not in by[k], f"R44 {k}"
    # the four NEW rows trail the index: no existing row number moves
    assert keys[211:215] == ["corporate_income_tax_return", "business_licence_authority", "gn605a_issuer", "severance_pay_income_tax"]    # 2026-11-17 batch 3 appended row 215 after these four (company_annual_return_deadline), so "the last four" is now an explicit slice
    assert keys[215:] == ["company_annual_return_deadline", "sdl_domestic_workers_scope", "nssf_contributions_age_60"]   # 2026-11-23 appended rows 216 and 217 (PENDING the Kaggle regen)
    assert keys.index("business_licence_expiry_30_june") == 168


def test_sources_are_declared_in_the_manifest_with_their_editions():
    m = json.load(open("data/source_documents/MANIFEST.json", encoding="utf-8"))["files"]
    for path, edition in (("brela/business_licensing_act_cap101_re2023.pdf", "R.E. 2023"), ("tra/finance_act_2025_no11.pdf", "Finance Act 2025"), ("tra/finance_act_2024_no6.pdf", "Finance Act 2024"),
                          ("labour/gn605a_2025_minimum_wage_order.pdf", "GN No. 605A")):
        assert edition in m[path]["edition"] and not m[path]["superseded"], path
    old = m["brela/business_licensing_act_cap208_2002_tanzlii.pdf"]
    assert old["superseded"] and "Cap. 101 R.E. 2023" in old["superseded_by"] and "30 JUNE ERROR" in old["do_not_verify_against"]
