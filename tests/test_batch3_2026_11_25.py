"""2026-11-25 batch 3 (founder): (1) D-FIDELITY-34, the INTERIM holding line for a foreign / expatriate employee tied to the 15% rate; (2) the guard replacement covers EVERY limb the question names (health + medicines -> the combined text; a registration limb -> the 'thibitisha usajili na TRA' hedge and nothing more);
(3) out-of-country questions never name a foreign authority or URL. Specimens are VERBATIM live replies of build 16f0a43; planted both ways (R26)."""
import io
import json
import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
from chike import clarification, fidelity, routing   # noqa: E402
from chike.model_abstraction import ModelBackend      # noqa: E402
from chike.orchestrator import Orchestrator           # noqa: E402
from chike.rules_engine import fixed_statements as fs  # noqa: E402

QF = "Does a foreign employee pay PAYE at a different rate from a citizen?"
LIVE_FOREIGN = ("Yes, there's a different treatment for foreign employees. A foreigner working as an employee pays a flat rate of 15% on their gross employment income. "
                "This is because they don't have residence status for progressive taxation. Thibitisha na TRA (tra.go.tz).")
QK = "Kiwango cha PAYE Kenya ni asilimia ngapi?"
LIVE_KENYA = ("Sina uhakika wa viwango vya kodi vya Kenya -- ninasaidia tu na maswali ya Tanzania Bara. "
              "Kwa taarifa za kodi za Kenya, thibitisha na TRA (tra.go.ke) au mshauri wa kodi wa Kenya.")
Q_PHARM = "Duka la dawa linatakiwa kusajili VAT, na dawa zinatozwa VAT gani?"
Q_HM_IMPORT = "Huduma za afya na dawa zinazoingizwa kutoka nje zinatozwa VAT?"
BAD_MED_BODY = "Dawa zinaweza kuwa zero-rated (msamaha wa VAT) au exempt (si zero-rated)."


class _S(ModelBackend):
    def __init__(self, t):
        self.t = t

    def generate(self, prompt, params=None):
        return self.t


def _ans(q, body):
    return Orchestrator(backend=_S(body), retriever=lambda *a, **k: ["x"], system_prompt="x", ooc_phrases=[], in_scope_phrases=[]).answer(q)


def _guards(r):
    return [getattr(x, "guard", "") for x in r.sub_answers]


# ---------------- (1) foreign employee tied to 15% ----------------
def test_the_foreign_question_reaches_the_model_because_the_statement_routes_veto_it():
    assert routing.fixed_statement_topic(QF) is None


def test_live_specimen_is_replaced_by_the_holding_line_end_to_end():
    r = _ans(QF, LIVE_FOREIGN)
    assert "replaced" in _guards(r)
    assert "15%" not in r.text and "UKAZI" in r.text and "uraia au kuwa mgeni peke yake si kigezo" in r.text, r.text


@pytest.mark.parametrize("q,body", [
    (QF, "Non-resident employees pay a flat 15%; a foreigner who is resident pays on the bands."),
    ("x", "Mgeni anayekaa Tanzania zaidi ya siku 183 ni mkazi na analipa kwa mabano, si 15%."),
    ("x", "Wageni hawalipi asilimia 15 tambarare."), ("x", "Foreigners do not pay a flat 15%."),
    ("Kodi ya mgeni PAYE?", "Kodi ya zuio ya gawio ni asilimia 15 kwa kampuni zisizoorodheshwa."),
    ("PAYE ni asilimia ngapi?", "Asiye mkazi analipa 15% tambarare."),
])
def test_controls_are_clean(q, body):
    assert not fidelity.foreign_status_tied_to_15pct(q, body), body


@pytest.mark.parametrize("q,body", [(QF, LIVE_FOREIGN), ("Kodi ya mgeni PAYE?", "Kiwango ni 15% tambarare kwa mgeni."), ("x", "Expatriates pay 15% on their salary."), ("x", "Mgeni analipa asilimia 15.")])
def test_specimens_flag(q, body):
    assert fidelity.foreign_status_tied_to_15pct(q, body), body


def test_holding_line_never_flags_itself_and_carries_no_section_number():
    t = clarification.CONSTANT_RESTATEMENTS["foreign_15pct"]
    assert not fidelity.body_contradicts_d16(QF, t) and "Kifungu" not in t and "s.86" not in t and "15" not in t


def test_planted_detector_disabled_lets_the_specimen_through(monkeypatch):
    monkeypatch.setattr(fidelity, "foreign_status_tied_to_15pct", lambda *a, **k: [])
    assert "15%" in _ans(QF, LIVE_FOREIGN).text


# ---------------- (2) replacement by limbs ----------------
def test_health_plus_medicines_guard_gets_the_combined_text_medical_first():
    assert routing.fixed_statement_topic(Q_HM_IMPORT) is None, "the import veto keeps this on the model path, so the GUARD is the layer under test"
    r = _ans(Q_HM_IMPORT, BAD_MED_BODY)
    assert "replaced" in _guards(r)
    t = r.text
    med, drugs = fs.fixed_statement("vat_medical_services").working, fs.fixed_statement("vat_medicines").working
    assert t == med + "\n\n" + drugs, t[:200]


def test_pharmacy_registration_limb_gets_the_hedge_and_nothing_more():
    assert routing.fixed_statement_topic(Q_PHARM) is None
    r = _ans(Q_PHARM, BAD_MED_BODY)
    assert "replaced" in _guards(r)
    drugs = fs.fixed_statement("vat_medicines").working
    assert r.text == drugs + "\n\n" + clarification.REGISTRATION_LIMB_HEDGE
    assert clarification.REGISTRATION_LIMB_HEDGE == "Kuhusu usajili wa VAT: thibitisha usajili na TRA (tra.go.tz)."
    assert not re.search(r"kizingiti|threshold|200", clarification.REGISTRATION_LIMB_HEDGE)       # NO figure or rule: only the pointer (the threshold sub-limb is PROPOSED, not built)


def test_a_plain_medicines_question_gets_the_medicines_text_only():
    r = _ans("Dawa za TZS 5,000,000 nimeuza, VAT ni ngapi?", "Kwa dawa zenye thamani ya TZS 5,000,000, kiwango cha VAT ni 18%.")
    assert "replaced" in _guards(r) and r.text == fs.fixed_statement("vat_medicines").working


def test_planted_limbs_disabled_gives_the_single_limb_text(monkeypatch):
    monkeypatch.setattr(clarification, "_HEALTH_Q", re.compile(r"(?!x)x"))
    r = _ans(Q_HM_IMPORT, BAD_MED_BODY)
    assert r.text == fs.fixed_statement("vat_medicines").working


# ---------------- (3) out-of-country questions never name a foreign authority or URL ----------------
def test_kenya_live_reply_is_repaired_end_to_end():
    r = _ans(QK, LIVE_KENYA)
    assert "tra.go.ke" not in r.text and "TRA" not in r.text.split("Bara.")[-1] and "wasiliana na mamlaka ya kodi ya nchi husika" in r.text
    assert r.text.startswith("Sina uhakika wa viwango vya kodi vya Kenya"), "the correct refusal sentence is KEPT; only the authority sentence is replaced"


@pytest.mark.parametrize("q,body", [
    ("Cheti cha P9 ni nini?", "'P9' si neno la Tanzania: ni la Kenya (KRA) na TRA haina fomu yenye jina hilo."),         # D-FIDELITY-30's own copy: no foreign country in the question, no foreign domain
    ("Kodi ya PAYE ni nini?", "Thibitisha na TRA (tra.go.tz)."),
    ("Tofauti ya Kenya na Tanzania kwenye PAYE?", "Nchini Tanzania, thibitisha na TRA (tra.go.tz). Kenya ina mfumo wake."),   # a comparison sentence naming Tanzania is left alone
])
def test_tanzanian_and_comparison_answers_are_untouched(q, body):
    assert fidelity.repair_foreign_authority(q, body) == body


@pytest.mark.parametrize("q,body", [
    ("Kodi ya kampuni?", "Kwa taarifa zaidi tembelea kra.go.ke."), ("Kiwango cha kodi Kenya?", "Kenya Revenue Authority (KRA) inasema kiwango ni 30%."),
    ("Kodi Uganda ni ngapi?", "Thibitisha na TRA kwa maswali ya Uganda."),
])
def test_foreign_authority_or_domain_is_replaced(q, body):
    assert fidelity.repair_foreign_authority(q, body) != body
    assert "wasiliana na mamlaka ya kodi ya nchi husika" in fidelity.repair_foreign_authority(q, body)


def test_planted_repair_disabled_lets_the_kenya_reply_through(monkeypatch):
    monkeypatch.setattr(fidelity, "repair_foreign_authority", lambda q, b: b)
    assert "tra.go.ke" in _ans(QK, LIVE_KENYA).text


# ---------------- (4) the two probe errors are fixed and the history is kept ----------------
def test_the_two_probe_errors_are_fixed_in_the_live_script():
    src = io.open(os.path.join(_ROOT, "eval", "controls", "verify_five_fixes_deploy_live_2026_11_25.py"), encoding="utf-8").read()
    assert "PROBE ERROR FIXED" in src and src.count("PROBE ERROR FIXED") == 2
    assert 'r"(?i)punguzo"],' not in src and "[], [NOT_MED_STMT], \"engine:fixed_statement\"" in src      # the China-import row keeps NOT_MED_STMT only in the Kenya-style rows below it, never as the import row's must_not
    art = json.load(io.open(os.path.join(_ROOT, "eval", "results", "five_fixes_deploy_live_2026_11_25.json"), encoding="utf-8"))
    assert sum(1 for r in art["rows"] if r.get("ok") is False) == 0, "the verdicts were RE-DERIVED over the stored replies with the corrected probes"


def test_new_patterns_contain_no_control_characters():
    for n in ("_D34_FOREIGN", "_D34_RESIDENCY", "_D34_FIFTEEN", "_D34_PAYE_Q", "_D34_NEG", "_FA_COUNTRY", "_FA_DOMAIN", "_FA_NAME", "_FA_CONFIRM_TRA", "_FA_TANZANIA"):
        assert not any(ord(c) < 32 for c in getattr(fidelity, n).pattern), n
    for n in ("_HEALTH_Q", "_REGISTRATION_Q"):
        assert not any(ord(c) < 32 for c in getattr(clarification, n).pattern), n
