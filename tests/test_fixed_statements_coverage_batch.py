"""2026-11-16 coverage batch (3a): WCF occupational-disease chain, NSSF split, PAYE band table as model-free statements, plus the NSSF agreed-split engine extractor (R31) and the payroll wage-evidence rule (eval_257).

Route probes: eval/fidelity/coverage_routes_probes_2026_11_16.jsonl (11 of 19 are neighbours that must NOT divert). Every statement is checked against its locked fact and, for PAYE, generated from the engine table.
Planted: each new route's cue disabled loses its founding specimen (R26), and the extractor removed re-creates the live wrong answer.
"""
import json
import re

import pytest

from chike import routing
from chike.model_abstraction import ModelBackend
from chike.orchestrator import Orchestrator
from chike.rules_engine import fixed_statements as fs
from chike.rules_engine import rates

PROBES = [json.loads(l) for l in open("eval/fidelity/coverage_routes_probes_2026_11_16.jsonl", encoding="utf-8") if l.strip()]
LOCKED = json.load(open("scripts/locked_facts.json", encoding="utf-8"))


@pytest.mark.parametrize("p", PROBES, ids=[p["id"] for p in PROBES])
def test_route_probe(p):
    if p["kind"] == "intent":
        assert routing.detect_intent(p["question"]) == p["want"], p["guards_against"]
    elif p["kind"] == "topic":
        assert routing.fixed_statement_topic(p["question"]) == p["want"], p["guards_against"]
    else:
        assert routing.fixed_statement_topic(p["question"]) is None, p["guards_against"]


def test_new_topics_are_registered_and_excluded_from_autosend():
    for t in (fs.WCF_DISEASE, fs.NSSF_SPLIT, fs.PAYE_BANDS_TOPIC):
        assert t in fs.TOPICS and t in fs.TOPICS_NO_CONCISE_ROW
        assert routing.fixed_statement_topics  # the shared cue reader exists
    # same route string as the five proven live 2026-11-16: the allowlist/exclusion work is already done for them
    import importlib.util, os
    spec = importlib.util.spec_from_file_location("hc", os.path.join("chike-whatsapp", "handler_core.py"))
    hc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hc)
    assert "engine:fixed_statement" in hc.AUTOSEND_EXCLUDED_ENGINE_ROUTES and "engine:fixed_statement" not in hc.AUTOSEND_ELIGIBLE_ENGINE_ROUTES


def test_disease_statement_is_the_two_stage_chain_from_the_locked_fact():
    text = fs.STATEMENTS[fs.WCF_DISEASE][1]
    cv = LOCKED["wcf_disease_reporting_deadline"]["fact"]
    for n in ("14", "7", "21", "12"):
        assert n in text and re.search(rf"\b{n}\b", cv), n
    assert "APOKEE" in text and "si siku 7 moja kwa moja" in text


def test_nssf_split_statement_states_the_option_and_no_exhaustive_list():
    text = fs.STATEMENTS[fs.NSSF_SPLIT][1]
    assert "asilimia 20" in text and "15% + 5%" in text and "20% + 0%" in text and "si orodha kamili" in text
    assert not re.search(r"(?i)kifungu\s+\d", text), "R44: no section number of a consolidated Act in served text"


def test_paye_statement_is_generated_from_the_engine_table():
    text = fs.STATEMENTS[fs.PAYE_BANDS_TOPIC][1]
    assert text == fs._paye_bands_text()
    for lower, rate, base in rates.PAYE_BANDS:
        assert f"{int(rate * 100)}%" in text
        if base:
            assert f"{int(base):,}" in text
    assert "kiwango cha 3: TZS 520,001 hadi TZS 760,000 = TZS 20,000 + 20%" in text, "the 20% band is band 3 (served row numbering: the 0% band is band 1)"
    assert "15% tambarare" in text and "Hakuna punguzo" in text


class _B(ModelBackend):
    def generate(self, prompt, params=None):
        raise AssertionError("a fixed statement must not call the model")


@pytest.mark.parametrize("pid,needle", [("cv_01", "siku 14 za kazi"), ("cv_08", "si mgawanyo pekee halali"), ("cv_14", "kiwango cha 3")])
def test_live_questions_are_answered_whole_with_zero_model_calls(pid, needle):
    q = next(p["question"] for p in PROBES if p["id"] == pid)
    r = Orchestrator(backend=_B(), retriever=lambda *a, **k: [], system_prompt="x").answer(q)
    assert needle in r.text and r.model_calls == 0


@pytest.mark.parametrize("topic,pid", [("wcf_disease_reporting", "cv_01"), ("nssf_split", "cv_08"), ("paye_band_table", "cv_14")])
def test_planted_cue_disabled_loses_the_specimen(monkeypatch, topic, pid):
    topics = tuple((n, c, nd, v) if n != topic else (n, re.compile(r"(?!x)x"), nd, v) for n, c, nd, v in routing._FS_TOPICS)
    monkeypatch.setattr(routing, "_FS_TOPICS", topics)
    assert routing.fixed_statement_topic(next(p["question"] for p in PROBES if p["id"] == pid)) is None


def test_new_patterns_contain_no_control_characters():
    for n, cue, need, veto in routing._FS_TOPICS:
        for rx in (cue, need, veto):
            if rx is not None:
                assert not [c for c in rx.pattern if ord(c) < 32 and c not in "\n\t"], n
    for k, rx in routing._FS_TOPIC_ASK.items():
        assert not [c for c in rx.pattern if ord(c) < 32], k


# ---- NSSF agreed split (R31) -------------------------------------------------------------------------------------------------------------------------------------------------------------
class _Empty(ModelBackend):
    def generate(self, prompt, params=None):
        return ""


def _answer(q):
    return Orchestrator(backend=_Empty(), retriever=lambda *a, **k: [], system_prompt="x").answer(q).text


def test_agreed_split_is_honoured_by_the_engine():
    t = _answer("Mshahara ni TZS 700,000 na tumekubaliana mgao wa 15% mwajiri na 5% mfanyakazi — kila upande ni ngapi?")
    assert "mwajiri TZS 105,000" in t and "mfanyakazi TZS 35,000" in t and "TZS 140,000" in t


def test_split_20_0_and_the_default_unchanged():
    assert "mwajiri TZS 140,000 + mfanyakazi TZS 0" in _answer("Mshahara ni TZS 700,000, NSSF — mwajiri 20% na mfanyakazi 0%, kila upande ni ngapi?")
    assert "mwajiri TZS 80,000 + mfanyakazi TZS 80,000" in _answer("Mshahara wa mfanyakazi ni TZS 800,000 kwa mwezi, NSSF ni ngapi?")


def test_an_unsatisfiable_split_declines_instead_of_guessing():
    t = _answer("Mshahara ni TZS 700,000, NSSF — mwajiri 10% na mfanyakazi 5%, kila upande ni ngapi?")
    assert "haujumlishi asilimia 20" in t and "TZS 70,000" not in t


@pytest.mark.parametrize("q,want", [("mwajiri 15% na mfanyakazi 5%", (0.15, 0.05)), ("mwajiri asilimia 20, mfanyakazi asilimia 0", (0.20, 0.0)), ("mwajiri 10% na mfanyakazi 5%", "invalid"),
                                    ("Mwajiri analipa asilimia 10 ya mshahara wa mfanyakazi", None), ("NSSF ni asilimia 20", None)])
def test_split_extractor(q, want):
    got = routing.nssf_agreed_split(q)
    assert (got == "invalid") if want == "invalid" else (got is None if want is None else tuple(float(x) for x in got) == want)


def test_planted_extractor_removed_recreates_the_live_wrong_answer(monkeypatch):
    monkeypatch.setattr(routing, "nssf_agreed_split", lambda text: None)
    t = _answer("Mshahara ni TZS 700,000, NSSF — mwajiri 15% na mfanyakazi 5%, kila upande ni ngapi?")
    assert "mwajiri TZS 70,000 + mfanyakazi TZS 70,000" in t, "with no extractor the engine states the default 10/10 over a split the user supplied"


# ---- payroll wage evidence (eval_257) ----------------------------------------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("q", ["Mapato ya biashara yangu yalifika TZS 12,300,000 mwezi jana, NSSF ya jumla ni ngapi?", "Nina amana ya TZS 15,000,000, NSSF ni ngapi?",
                               "Nimekopa benki mkopo wa TZS 20,000,000, WCF ni ngapi?", "Mteja amenilipa TZS 6,000,000 kwa oda, PAYE ni ngapi?"])
def test_a_non_wage_figure_is_never_computed_as_payroll(q):
    t = _answer(q)
    assert not re.search(r"=\s*TZS\s*[\d,]+", t) or "si mshahara" in t or "kuthibitisha" in t, t


@pytest.mark.parametrize("q", ["Mshahara wa mfanyakazi ni TZS 800,000 kwa mwezi, NSSF ni ngapi?", "Mapato yangu ya ajira ni TZS 800,000 kwa mwezi, PAYE ni ngapi?",
                               "Watu 5 wanapata 700,000, watu 4 wanapata 550,000, watu 6 wanapata 300,000 — NSSF ya jumla ni ngapi?"])
def test_controls_with_wage_evidence_still_compute(q):
    assert re.search(r"=\s*TZS\s*[\d,]+", _answer(q))


# ---- 3c ROUTE misses (2026-11-16): eval_208 / eval_318's VAT limb / eval_108 / eval_376 ---------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("q,want", [
    ("Biashara yangu imepata mauzo ya TZS milioni 95 katika miezi 6 — je nimevuka kizingiti cha lazima cha VAT?", "vat_registration"),   # eval_208
    ("je nasajili VAT kama mapato ni TZS 205,000,000?", "vat_registration"),                                                                # eval_318's VAT limb
    ("Mapato yangu ni TZS 205,000,000 kwa mwaka — je nasajili VAT?", "vat_registration"),
    ("Kizingiti cha lazima cha VAT ni TZS ngapi?", "none"),                      # a LOOKUP must not become a verdict
    ("Rafiki yangu anauza milioni 250 kwa mwaka, je nasajili VAT?", "none"),     # not the user's own turnover
    ("Je nasajili VAT?", "none"),                                                # no figure
])
def test_vat_route_gaps(q, want):
    assert routing.detect_intent(q) == want


def test_a_penalty_question_and_a_no_employees_question_are_not_salary_requests():
    assert routing.is_uncomputable_payroll_amount("NSSF inatoza riba kiasi gani kwenye michango iliyochelewa ya mwajiri?") is False
    assert routing.is_uncomputable_payroll_amount("Mimi ni mjasiriamali peke yangu, sina wafanyakazi kabisa — SDL yangu ni ngapi?") is False


def test_planted_the_salary_request_predicate_is_restored_for_a_wage_question_without_a_figure():
    """Positive control: a genuine 'which amount' question with payroll context and NO figure must still be caught -- the two vetoes must not have disabled the predicate."""
    assert routing.is_uncomputable_payroll_amount("Wafanyakazi wangu wamepokea mishahara mwezi huu, NSSF yao ni kiasi gani?") is True


def test_the_unrouted_vat_limb_no_longer_yields_a_wrong_verdict():
    t = _answer("Nina wafanyakazi 11 na mishahara TZS 5,500,000 na nataka kujua SDL na NSSF na pia je nasajili VAT kama mapato ni TZS 205,000,000?")
    assert "TZS 192,500" in t and "TZS 1,100,000" in t
    assert "huhitajiwi" not in t.lower() and "hayazidi" not in t.lower()


# ---- the MODEL-FALLBACK extractor (founder, 2026-11-16): a figure the parser cannot read ("800k") falls to the model, and its amount used to bypass every base check -----------------------------------
from chike.extraction import SlotExtractor


class _ModelExtracts(ModelBackend):
    """Plays the model: answers the extraction prompt with a confident payroll of 800,000 (what a model does with '800k'); any other prompt gets ''. Counts extraction calls."""

    def __init__(self):
        self.extractions = 0

    def generate(self, prompt, params=None):
        if "Toa sehemu hizi" in prompt:
            self.extractions += 1
            return '{"gross_monthly_payroll": {"value": 800000, "confidence": "high"}, "employee_count": {"value": 1, "confidence": "high"}}'
        return ""


def _fallback_answer(q):
    b = _ModelExtracts()
    t = Orchestrator(backend=b, retriever=lambda *a, **k: [], system_prompt="x", extractor=SlotExtractor(b)).answer(q).text
    return t, b.extractions


@pytest.mark.parametrize("q", ["Nina amana ya 800k, NSSF ni ngapi?", "Nimekopa 800k kutoka benki, WCF ni ngapi?", "Mteja amenilipa 800k kwa oda, PAYE ni ngapi?",
                               "Mapato ya biashara yangu yalikuwa 800k mwezi jana, NSSF ni ngapi?"])
def test_a_non_wage_figure_the_parser_cannot_read_is_not_computed_by_the_model_fallback(q):
    t, n = _fallback_answer(q)
    assert n >= 1, "the specimen must actually reach the model fallback, or this test proves nothing (R26)"
    assert not re.search(r"=\s*TZS\s*[\d,]+", t) or "si mshahara" in t or "kuthibitisha" in t, t


def test_the_control_with_wage_evidence_still_computes_through_the_model_fallback():
    t, n = _fallback_answer("Mshahara wa mfanyakazi ni 800k kwa mwezi, NSSF ni ngapi?")
    assert n >= 1 and re.search(r"=\s*TZS\s*[\d,]+", t), t


def test_planted_fallback_check_removed_lets_the_loan_through(monkeypatch):
    from chike import swahili_numbers as swn
    monkeypatch.setattr(swn, "detect_wrong_base", lambda *a, **k: False)
    monkeypatch.setattr(swn, "detect_unanchored_payroll_base", lambda *a, **k: False)
    t, n = _fallback_answer("Nina amana ya 800k, NSSF ni ngapi?")
    assert n >= 1 and re.search(r"=\s*TZS\s*[\d,]+", t), "with both checks disabled the model-fallback amount must be computed (the live risk), or the tests above prove nothing"
