"""2026-11-24 follow-up: the medical-VAT fact + statement route, the P45 / GN 487A fact corrections (served rows included), D-FIDELITY-31 (a compute-body figure no engine produced), the corpus repairs' reach (R36) and the eval_203 sidecar.
Probes both ways (R17), zero model calls, content pinned to the sources read, PLANTS with positive controls (R26)."""
import hashlib
import importlib.util
import io
import json
import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "scripts"))
from chike import answer_trace, fidelity, routing   # noqa: E402
from chike.orchestrator import Orchestrator         # noqa: E402
from chike.rules_engine import fixed_statements as fs   # noqa: E402

_PROBES = os.path.join(_ROOT, "eval", "refusal_gate", "medical_vat_probes_2026_11_24.jsonl")


def _jl(path):
    with io.open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def _facts():
    with io.open(os.path.join(_ROOT, "scripts", "locked_facts.json"), encoding="utf-8") as fh:
        return json.load(fh)


# ── medical VAT ─────────────────────────────────────────────────────────────────────────────────
def _probes():
    rows = _jl(_PROBES)
    assert len(rows) == 14 and sum(1 for r in rows if r["expect"] == "vat_medical_services") >= 7       # a loader returning nothing must fail (R20)
    return rows


@pytest.mark.parametrize("p", _probes(), ids=lambda p: p["id"])
def test_medical_probe_routes_as_authored(p):
    assert routing.fixed_statement_topic(p["question"]) == (None if p["expect"] == "none" else p["expect"]), p["guards_against"]


class _B:
    calls = 0

    def generate(self, prompt, params=None):
        _B.calls += 1
        return "Ndiyo, daktari anatakiwa kusajili VAT."          # the live wrong reply


def test_the_live_doctor_question_is_answered_by_the_statement_not_the_model():
    _B.calls = 0
    o = Orchestrator(_B(), retriever=lambda q: ["Ukweli."], ooc_phrases=[], in_scope_phrases=[])
    r = o.answer("Daktari anayetoa huduma za kitaalamu anatakiwa kusajili VAT?")
    t = answer_trace.trace(r)
    assert t["path"] == "engine:fixed_statement" and t["model_calls"] == 0 and _B.calls == 0
    assert not r.text.startswith("Ndiyo") and "MSAMAHA" in r.text


def test_medical_statement_has_both_limbs_and_hedges_registration():
    w = fs.fixed_statement("vat_medical_services").working
    for needle in ("MSAMAHA", "taasisi iliyoidhinishwa na Serikali", "NA (b)", "YOTE MAWILI", "HAIJATHIBITISHWA", "tra.go.tz"):
        assert needle in w, needle
    assert not re.search(r"kipengele|Kifungu|Jedwali", w), "R44: no section or item number in the answer text"
    assert "Ndiyo" not in w


def test_medical_fact_and_the_two_new_index_rows():
    import precompute_rag_embeddings as p
    f = _facts()["medical_services_vat_exempt"]
    assert f["status"] == "CONFIRMED" and "HAIJATHIBITISHWA" in f["fact"] and "Part I" in f["primary_source"] and "R.E. 2023" in f["verified_by"]
    texts, keys, _ = p.build_fact_texts()
    assert len(texts) == 220 and keys[-2:] == ["sdl_base_includes_allowances", "medical_services_vat_exempt"]
    assert "msamaha" in texts[-1].lower() and len(texts[-1]) < 260


def test_the_professional_route_still_vetoes_doctors_and_the_two_routes_are_exclusive():
    q = "Daktari anayetoa huduma za kitaalamu anatakiwa kusajili VAT?"
    assert routing.fixed_statement_topics(q) == ["vat_medical_services"]


# ── fact corrections (item 4), served rows included ─────────────────────────────────────────────
def test_p45_fact_has_the_section_in_metadata_only_and_the_r2023_number():
    f = _facts()["p45_not_tanzanian"]
    assert "s.85" not in f["fact"] and "s.85" not in f["correct_value"]
    assert "R.E.2023 s.110(3)(b)" in f["primary_source"] and "R.E.2015" in f["primary_source"]


def test_gn487a_noncitizen_fact_and_both_served_rows_follow_the_order():
    import precompute_rag_embeddings as p
    f = _facts()["gn487a_penalty_noncitizen"]
    assert "AND/OR" not in f["fact"] and "OR imprisonment" in f["fact"] and "NO maximum" in f["fact"] and "DIRECT READ" in f["verified_by"]
    texts, keys, _ = p.build_fact_texts()
    r20, r21 = texts[keys.index("gn487a_penalty_noncitizen")], texts[keys.index("gn487a_penalty_citizen_facilitator")]
    assert "na/au" not in r20 and "AU kifungo" in r20 and "hakijatajwa" in r20
    assert "si zaidi ya TZS 5,000,000" not in r21 and "faini ya TZS 5,000,000" in r21 and "AU kifungo" in r21


# ── D-FIDELITY-31 ───────────────────────────────────────────────────────────────────────────────
Q = "Nina wafanyakazi 15 na mishahara jumla TZS 6,000,000 kwa mwezi. SDL na NSSF ni kiasi gani?"
W = "SDL = 3.5% × TZS 6,000,000 = TZS 210,000 NSSF = 20% × TZS 6,000,000 = TZS 1,200,000 (mwajiri TZS 600,000 + mfanyakazi TZS 600,000)"


def test_d31_flags_the_founding_specimen():
    got = fidelity.unproduced_figures(Q, "SDL ni TZS 210,000 (TZS 150,000 kwa mwajiri).", W)
    assert [a for a, _ in got] == [150000]


@pytest.mark.parametrize("q,body,work", [
    (Q, "SDL ni TZS 210,000 na NSSF ni TZS 1,200,000 (TZS 600,000 kwa mwajiri).", W),                                                  # sibling working figures
    ("Mshahara TZS 800,000, makato?", "Mshahara TZS 800,000 ukitoa PAYE TZS 78,000 unabaki TZS 722,000.", "PAYE = TZS 78,000"),         # net pay: one-step difference
    ("Siku 26 kwa TZS 18,000 kwa siku", "TZS 18,000 × 26 = TZS 468,000.", "Mshahara wa mwezi TZS 468,000"),                                # daily wage product
    ("Mishahara TZS 1,500,000 kwa wafanyakazi 5, SDL?", "Wastani ni TZS 300,000 kwa mfanyakazi.", "SDL: wafanyakazi chini ya 10"),    # per-head via a stated COUNT ('5,' with a comma)
    ("Mshahara TZS 800,000, PAYE?", "Bendi ya kwanza ni hadi TZS 270,000; ya pili TZS 270,001 hadi TZS 520,000.", "PAYE = TZS 78,000"),   # statutory band edges
    ("Mishahara TZS 4,800,000", "NSSF = 20% × TZS 4,800,000 = TZS 960,000.", "SDL: TZS 168,000")])                                  # a rate stated in the SAME sentence
def test_d31_leaves_one_step_derivations_alone(q, body, work):
    assert fidelity.unproduced_figures(q, body, work) == [], body


def test_d31_known_limit_a_two_step_annual_figure_is_flagged():
    """PRICED AND STATED: x * r * 12 is not one step. The action is body-only blanking, so the cost is one sentence."""
    assert fidelity.unproduced_figures(Q, "SDL kwa mwaka ni TZS 2,520,000.", W)


def test_d31_negated_mention_is_not_an_assertion():
    assert fidelity.unproduced_figures(Q, "SDL si TZS 150,000; ni TZS 210,000.", W) == []


def test_d31_wired_blanks_the_live_specimen_body_and_a_plant_restores_it(monkeypatch):
    class B:
        def generate(self, prompt, params=None):
            return "SDL ni TZS 210,000 (TZS 150,000 kwa mwajiri). NSSF ni TZS 1,200,000."

    def run():
        return Orchestrator(B(), retriever=lambda x: ["Ukweli."], ooc_phrases=[], in_scope_phrases=[]).answer(Q).text
    t = run()
    assert "150,000" not in t and "TZS 210,000" in t and "TZS 1,200,000" in t          # the working still renders
    monkeypatch.setattr(fidelity, "body_states_unproduced_figure", lambda *a, **k: False)
    assert "150,000" in run(), "positive control: without the guard the invented figure ships"


def test_d31_never_touches_a_model_free_statement():
    r = Orchestrator(_B(), retriever=lambda q: ["x"], ooc_phrases=[], in_scope_phrases=[]).answer("SDL, NSSF na PAYE ni asilimia ngapi?")
    assert answer_trace.trace(r)["path"] == "engine:fixed_statement" and "HAINA kiwango kimoja" in r.text


def test_d31_priced_over_the_corpus_and_the_artifact_says_zero_gold_flags():
    d = json.load(io.open(os.path.join(_ROOT, "eval", "results", "price_d31_2026_11_24.json"), encoding="utf-8"))
    assert d["gold_flags"] == 0 and d["founding_specimen_flags_150000"] is True and d["population"]["gold_checked"] >= 200 and d["population"]["with_body_and_working"] >= 50


# ── corpus repairs reach (R36) and the sidecar ──────────────────────────────────────────────────
def test_the_corpus_repairs_reached_the_export():
    spec = importlib.util.spec_from_file_location("_reach", os.path.join(_ROOT, "eval", "controls", "assert_export_reach_2026_11_24.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    assert m.main() == 0


def test_the_eval_203_sidecar_pins_the_untouched_gate_file():
    side = json.load(io.open(os.path.join(_ROOT, "eval", "accuracy_gate", "eval_questions_002_additions.SIDECAR_2026_11_24.json"), encoding="utf-8"))
    raw = open(os.path.join(_ROOT, "eval", "accuracy_gate", "eval_questions_002_additions.jsonl"), "rb").read()
    assert hashlib.sha256(raw).hexdigest() == side["frozen_sha256"], "the frozen gate file was edited: correct it through the sidecar, not in place"
    c = side["corrections"][0]
    assert c["id"] == "eval_203" and "P9" in c["original"]["correct_answer_sw"] and "fomu ya P9" not in c["corrected"]["correct_answer_sw"]
    assert "cheti cha zuio" in c["corrected"]["correct_answer_sw"]
