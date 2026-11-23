"""2026-11-23: the ten model-free statement routes (SDL+NSSF+PAYE party, NSSF party, BRELA three forms, no-share-capital fee, GN 487A penalties, VAT withholding rates, VAT professional services, late annual return, SDL+PAYE deadline,
SDL audit hedge) and D-FIDELITY-29 (NSSF stated as the 7th) / D-FIDELITY-30 (a Kenyan "P9"). Probes both ways (R17), zero model calls, introspected patterns (R39), content pinned to the sources read, and PLANTS with positive controls (R26)."""
import glob
import io
import json
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
from chike import answer_trace, fidelity, routing   # noqa: E402
from chike.orchestrator import Orchestrator         # noqa: E402
from chike.rules_engine import fixed_statements as fs   # noqa: E402

NEW = ("sdl_nssf_paye_party", "nssf_party", "brela_three_forms", "brela_fee_no_share_capital", "gn487a_penalties", "vat_withholding_rates",
       "vat_professional_services", "brela_late_annual_return", "sdl_paye_deadline", "sdl_audit_hedge")
_PROBES = os.path.join(_ROOT, "eval", "refusal_gate", "ten_more_statements_probes_2026_11_23.jsonl")


def _probes():
    with io.open(_PROBES, encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh if line.strip()]
    assert len(rows) == 98, len(rows)                       # a loader returning nothing must fail, not pass vacuously (R20)
    assert sum(1 for r in rows if r["expect"] in NEW) >= 45 and sum(1 for r in rows if r["expect"] == "none") >= 25
    return rows


@pytest.mark.parametrize("p", _probes(), ids=lambda p: p["id"])
def test_probe_routes_as_authored(p):
    want = None if p["expect"] == "none" else p["expect"]
    assert routing.fixed_statement_topic(p["question"]) == want, p["guards_against"]


def test_every_new_topic_has_a_positive_probe_and_a_statement():
    rows = _probes()
    for t in NEW:
        assert t in fs.TOPICS and t in fs.TOPICS_NO_CONCISE_ROW
        assert any(r["expect"] == t for r in rows), t


def test_mutual_exclusion_over_every_question_in_every_probe_file():
    n = 0
    for f in glob.glob(os.path.join(_ROOT, "eval", "refusal_gate", "*.jsonl")):
        with io.open(f, encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                q = json.loads(line).get("question")
                if q:
                    n += 1
                    hits = routing.fixed_statement_topics(q)
                    assert len(hits) <= 1 or not set(hits) & set(NEW), (q, hits)
    assert n > 300, n


def test_new_patterns_contain_no_control_characters():
    """R39: a non-raw escape compiles to a backspace and matches nothing, invisibly (one was found in this very change: \\b written through a non-raw string)."""
    for name in NEW:
        entry = [e for e in routing._FS_TOPICS if e[0] == name]
        assert len(entry) == 1, name
        for p in list(entry[0][1:]) + [routing._FS_TOPIC_ASK[name]]:
            if p is not None:
                assert not any(ord(c) < 32 for c in p.pattern), (name, p.pattern[:80])
    for n in dir(fidelity):
        if n.startswith(("_D29", "_D30")) and hasattr(getattr(fidelity, n), "pattern"):
            assert not any(ord(c) < 32 for c in getattr(fidelity, n).pattern), n


class _B:
    calls = 0

    def generate(self, prompt, params=None):
        _B.calls += 1
        return "JIBU."


@pytest.mark.parametrize("p", [r for r in _probes() if r["expect"] in NEW], ids=lambda p: p["id"])
def test_positive_probe_is_answered_by_the_whole_statement_with_zero_model_calls(p):
    _B.calls = 0
    o = Orchestrator(_B(), retriever=lambda q: ["Ukweli."], ooc_phrases=[], in_scope_phrases=[])
    reply = o.answer(p["question"])
    t = answer_trace.trace(reply)
    assert t["path"] == "engine:fixed_statement" and t["model_calls"] == 0 and _B.calls == 0, t
    assert fs.fixed_statement(p["expect"]).working in reply.text


def _w(t):
    return fs.fixed_statement(t).working


def test_gn487a_statement_follows_the_gazetted_order_not_the_practitioner_wording():
    w = _w("gn487a_penalties")
    for needle in ("10,000,000", "5,000,000", "miezi 6", "miezi 3", "15", "28 Julai 2025", "kiwango cha CHINI", "haitaji kiwango cha juu", "au kifungo"):
        assert needle in w, needle
    assert "faini na kifungo" not in w and "TZS 10M" not in w


def test_fee_statement_says_the_effective_date_is_unknown_and_names_both_dates():
    w = _w("brela_fee_no_share_capital")
    for needle in ("500,000", "HAIJULIKANI", "2026-10-06", "2026-06-30", "300,000"):
        assert needle in w, needle


def test_vat_withholding_statement_has_both_rates_the_year_and_the_split():
    w = _w("vat_withholding_rates")
    for needle in ("Sheria ya Fedha 2025", "asilimia 3", "asilimia 6", "asilimia 18", "asilimia 15", "asilimia 12", "Huduma za IT"):
        assert needle in w, needle


def test_forms_statement_does_not_assert_payroll_or_any_unsourced_duty():
    w = _w("brela_three_forms")
    assert "payroll" not in w.lower() and "mshahara" not in w.lower() and "SI idadi ya wafanyakazi" in w and "TATU" in w


def test_deadline_statement_gives_nssf_one_month_not_the_7th():
    w = _w("sdl_paye_deadline")
    assert "tarehe 7" in w and "NSSF si tarehe 7" in w and "mwezi mmoja" in w
    assert fidelity.nssf_deadline_misstated("q", w) == []          # the statement must pass its own guard


def test_late_return_statement_is_scoped_to_the_penalty_and_hedges_the_rest():
    w = _w("brela_late_annual_return")
    for needle in ("siku 28", "2,500", "22,000", "hayajathibitishwa"):
        assert needle in w, needle


def test_audit_statement_invents_no_procedure_and_names_no_kenyan_form():
    w = _w("sdl_audit_hedge")
    assert "Sina utaratibu uliothibitishwa" in w and "P9" not in w and "(1)" not in w


def test_party_statements_state_the_employee_nssf_is_deducted_and_paye_is_the_employees():
    for t in ("sdl_nssf_paye_party", "nssf_party"):
        w = _w(t)
        assert "HUKATWA" in w and "asilimia 20" in w and "asilimia 10" in w, t
    w = _w("sdl_nssf_paye_party")
    assert "MWAJIRI pekee" in w and "PAYE" in w and "MFANYAKAZI" in w


def test_professional_statement_gives_no_invented_reason_and_does_not_cover_doctors():
    assert "bila kutoa sababu" in _w("vat_professional_services")
    # 2026-11-24: the doctor question is now owned by vat_medical_services (it must NOT be the professional-services statement)
    assert routing.fixed_statement_topic("Daktari anayetoa huduma za kitaalamu anatakiwa kusajili VAT?") == "vat_medical_services"


# ── D-FIDELITY-29: NSSF stated as due by the 7th ───────────────────────────────────────────────
SPECIMEN_D29 = ("Kwa SDL: 3.5% ya TZS 6,000,000 = TZS 210,000. Kwa NSSF: 20% ya TZS 6,000,000 = TZS 1,200,000. "
                "Zote mbili zinalipwa ndani ya siku 7 za kwanza za mwezi unaofuata. Thibitisha na TRA.")


def test_d29_flags_the_live_specimen_and_the_direct_forms():
    assert fidelity.nssf_deadline_misstated("q", SPECIMEN_D29)
    for t in ("NSSF na SDL zinalipwa tarehe 7", "Wasilisha PAYE, NSSF, WCF ifikapo tarehe 7", "NSSF inalipwa ndani ya siku 7."):
        assert fidelity.nssf_deadline_misstated("q", t), t


@pytest.mark.parametrize("t", [
    "NSSF ni ndani ya mwezi mmoja; SDL na PAYE tarehe 7.", "NSSF si tarehe 7.", "tarehe 7 (SDL + PAYE + WCF) | tarehe 9 ya mwezi ujao (NSSF)",
    "PAYE na NSSF huwasilishwa kwa mamlaka husika, PAYE kufikia tarehe 7.", "hayapo katika taarifa niliyopewa na nssf.go.tz, kabla ya tarehe 7",
    "SDL na PAYE zote zinalipwa tarehe 7. NSSF ni 20%."])
def test_d29_leaves_the_correct_forms_alone(t):
    assert fidelity.nssf_deadline_misstated("q", t) == [], t


def test_d29_blanks_the_compute_body_and_a_plant_restores_it(monkeypatch):
    q = "Nina wafanyakazi 15 na mishahara jumla TZS 6,000,000 kwa mwezi. SDL na NSSF ni kiasi gani?"

    class B:
        def generate(self, prompt, params=None):
            return SPECIMEN_D29
    def run():
        return Orchestrator(B(), retriever=lambda x: ["Ukweli."], ooc_phrases=[], in_scope_phrases=[]).answer(q).text
    assert "siku 7 za kwanza" not in run()
    monkeypatch.setattr(fidelity, "nssf_deadline_misstated", lambda *a, **k: [])
    assert "siku 7 za kwanza" in run(), "positive control: without the guard the wrong sentence ships"


def test_d29_replaces_on_the_fact_path_and_a_plant_restores_the_error(monkeypatch):
    q = "Michango ya NSSF inalipwa wakati gani kila mwezi?"

    class B:
        def generate(self, prompt, params=None):
            return "Michango ya NSSF inalipwa ifikapo tarehe 7 ya mwezi unaofuata."
    def run():
        return Orchestrator(B(), retriever=lambda x: ["Ukweli."], ooc_phrases=[], in_scope_phrases=[]).answer(q).text
    assert "mwezi mmoja baada ya mwisho wa mwezi" in run()
    monkeypatch.setattr(fidelity, "nssf_deadline_misstated", lambda *a, **k: [])
    assert "ifikapo tarehe 7" in run()


# ── D-FIDELITY-30: a Kenyan "P9" ───────────────────────────────────────────────────────────────
def test_d30_repairs_p9_in_paye_context_and_drops_it_elsewhere():
    assert "P9" not in fidelity.repair_p9("The auditor will ask to see: payslips, P9 forms, SDL returns.")
    assert "vyeti vya zuio" in fidelity.repair_p9("The auditor will ask to see: payslips, P9 forms, SDL returns.")
    assert "cheti cha zuio" in fidelity.repair_p9("Kwa mshahara, wasilisha taarifa kwa TRA kupitia fomu ya P9.")
    out = fidelity.repair_p9("Usajili wa NSSF unahitaji: picha, fomu ya NSSF P9, na kitambulisho.")
    assert "P9" not in out and "cheti cha zuio" not in out, out      # a withholding certificate would keep a false claim here


@pytest.mark.parametrize("t", ["P9 ni neno la Kenya; TRA haina fomu hiyo.", "Tanzania has no P9 form (it is a KRA term)."])
def test_d30_leaves_a_sentence_that_says_p9_is_not_tanzanian(t):
    assert fidelity.repair_p9(t) == t and fidelity.p9_asserted(t) == []


def test_d30_is_idempotent_and_wired_with_a_plant(monkeypatch):
    t = "Onyesha payslips na fomu za P9 kwa TRA."
    assert fidelity.repair_p9(fidelity.repair_p9(t)) == fidelity.repair_p9(t)

    class B:
        def generate(self, prompt, params=None):
            return t
    def run():
        return Orchestrator(B(), retriever=lambda x: ["Ukweli."], ooc_phrases=[], in_scope_phrases=[]).answer("Mwajiri anaonyesha nini kwa TRA wakati wa ukaguzi wa PAYE?").text
    assert "P9" not in run()
    monkeypatch.setattr(fidelity, "repair_p9", lambda b: b)
    assert "P9" in run(), "positive control"
