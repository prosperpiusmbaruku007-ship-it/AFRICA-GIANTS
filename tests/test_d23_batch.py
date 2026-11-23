"""2026-11-18 batch 4 (founder): (a) a model-free fixed statement for the COMPANY annual-return deadline, (b) D-FIDELITY-23, "46" as the sub-sector count of a SINGLE sector of GN 605A.

Both ways (R17): every neighbour the route must NOT divert is a probe, and so is every correct sentence the guard must NOT flag. Plants (R26): each cue / guard is disabled or made over-broad to show a test fires.
Blast radius: eval/controls/sweep_annual_return_route_2026_11_18.py -> eval/results/sweep_annual_return_route_2026_11_18.json (19 diversions of 8,625 questions, every one a deadline question)."""
import importlib.util
import json
import os
import re
from datetime import datetime, timedelta, timezone

import pytest

from chike import answer_trace, clarification, fidelity, routing
from chike.orchestrator import Orchestrator
from chike.rules_engine import fixed_statements as fs

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("hc_d23_core", os.path.join(_ROOT, "chike-whatsapp", "handler_core.py"))
core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(core)
NOW = datetime(2026, 11, 18, 12, 0, 0, tzinfo=timezone.utc)
TOPIC = "brela_annual_return_deadline"

# the two live wrong replies of build 7b94236 (eval/results/annual_return_phrasings_live_2026_11_17.json), VERBATIM
LIVE_SIKU42 = ("Annual return ya kampuni inatakiwa kuwasilishwa ndani ya muda gani?",
               "Annual return ya kampuni inatakiwa kuwasilishwa ndani ya siku 42 tangu tarehe ya kumbukumbu ya usajili. Thibitisha na BRELA (brela.go.tz).")
LIVE_KALENDA = ("Annual return ya BRELA inapaswa kuwasilishwa lini?",
                "Annual return ya BRELA inapaswa kuwasilishwa katika mwaka wa kalenda unaofuatia tarehe ya usajili wa kampuni.")

DIVERT = [
    "Annual return ya BRELA inapaswa kuwasilishwa lini?",
    "Annual return ya kampuni inatakiwa kuwasilishwa ndani ya muda gani?",
    "Kampuni yangu ilisajiliwa Machi, annual return ni lini?",
    "Annual return ya kampuni ni ndani ya miezi 12 tangu usajili, sivyo?",
    "Je, annual return ya BRELA ni lazima iwe ifikapo 30 Septemba?",
    "Nimeambiwa annual return ya BRELA inaisha 30 Septemba — ni kweli?",
    "BRELA annual return — deadline ni wakati gani wa mwaka?",
]
CLEAN = [   # the neighbours, each with its own fact: a fee, a penalty amount, the form, how-to, a definition, strike-off, foreign, the TAX return, a registration fee
    "Annual return ya BRELA ada ni ngapi?",
    "Ada ya kuwasilisha annual return BRELA ni TZS 2,500, sivyo?",
    "Annual return ya kampuni nikichelewa adhabu ni kiasi gani?",
    "Nikichelewa kuwasilisha annual return, faini ni kiasi gani kwa mwezi?",
    "Kampuni ya kigeni ikichelewa annual return inatozwa kiasi gani kwa mwezi?",
    "Namba ya fomu ya annual return ya BRELA ni ipi?",
    "Nawezaje kuwasilisha annual return ya BRELA?",
    "Annual return ya BRELA (ripoti ya kila mwaka) ni nini?",
    "After how many years without an annual return can BRELA strike off a company?",
    "BRELA inaweza kufuta usajili wa kampuni baada ya miaka mingapi bila annual return?",
    "Return ya kodi ya mapato ya kampuni ni lini?",
    "Corporate tax annual return ni lini?",
    "Kodi ya mapato ya kampuni kwa annual return ni lini?",
    "BRELA ada ya usajili wa kampuni ni ngapi?",
    "Annual return ya kampuni ni lazima?",
    "Annual return ya BRELA inahesabiwaje?",     # only the GLOBAL ask matches ("inahesabiwaje"); no veto word: this is what the own-ask-only set exists for
    "Kampuni yangu haifanyi biashara (dormant) — je bado nawasilisha annual return?",
    "Annual return ya BRELA inawasilishwa lini na ada yake ni kiasi gani?",    # two questions: the fee limb has its own fact, so the statement must not swallow it
]


@pytest.mark.parametrize("q", DIVERT)
def test_the_deadline_question_routes_to_the_statement(q):
    assert routing.fixed_statement_topic(q) == TOPIC and routing.detect_intent(q) == "fixed_statement"


@pytest.mark.parametrize("q", CLEAN)
def test_every_neighbour_is_left_alone(q):
    # 2026-11-23: a LATE-return PENALTY question is now owned by brela_late_annual_return; the invariant here (it must not reach the DEADLINE statement) is unchanged.
    assert routing.fixed_statement_topic(q) != TOPIC and (routing.detect_intent(q) != "fixed_statement" or routing.fixed_statement_topic(q) == "brela_late_annual_return"), q


def test_plant_the_own_ask_cue_disabled_is_caught(monkeypatch):
    monkeypatch.setitem(routing._FS_TOPIC_ASK, TOPIC, re.compile(r"(?!x)x"))
    assert [q for q in DIVERT if routing.fixed_statement_topic(q) != TOPIC]


def test_plant_the_own_ask_made_universal_is_caught(monkeypatch):
    monkeypatch.setitem(routing._FS_TOPIC_ASK, TOPIC, re.compile(r""))
    assert [q for q in CLEAN if routing.fixed_statement_topic(q) == TOPIC]


def test_plant_the_global_ask_let_back_in_is_caught(monkeypatch):
    """The first sweep (27 diversions) showed the global ask ("ni nini", "ngapi", "kiasi gani") admits wrong-topic questions; the own-ask-only set is what stops it."""
    monkeypatch.setattr(routing, "_FS_OWN_ASK_ONLY", frozenset())
    assert [q for q in CLEAN if routing.fixed_statement_topic(q) == TOPIC]


def test_plant_the_veto_removed_is_caught(monkeypatch):
    topics = tuple((n, c, nd, (re.compile(r"(?!x)x") if n == TOPIC else v)) for n, c, nd, v in routing._FS_TOPICS)
    monkeypatch.setattr(routing, "_FS_TOPICS", topics)
    assert [q for q in CLEAN if routing.fixed_statement_topic(q) == TOPIC]


def test_the_patterns_contain_no_control_characters():
    """R39: a non-raw escape compiles to a backspace and matches nothing, invisibly."""
    pats = [routing._FS_TOPIC_ASK[TOPIC]] + [p for n, *ps in routing._FS_TOPICS if n == TOPIC for p in ps]
    pats += [fidelity._D23_COUNT, fidelity._D23_CTX, fidelity._D23_SINGLE, fidelity._D23_Q_SINGLE, fidelity._D23_TOTAL]
    assert len(pats) >= 8
    for p in pats:
        assert not any(ord(c) < 32 for c in p.pattern), p.pattern


# ── the statement is the served row, whole ────────────────────────────────────────────────────────
def test_the_statement_states_the_rule_and_denies_both_wrong_values():
    t = fs.fixed_statement(TOPIC).working
    assert "maadhimisho" in t and "siku 28" in t and "Si miezi 12" in t and "si 30 Septemba" in t
    assert "Kifungu" not in t and "Vifungu" not in t       # R44
    assert "siku 42" not in t and "mwaka wa kalenda" not in t


def test_the_statement_matches_the_restatement_the_guard_uses():
    """D-FIDELITY-20's replacement text and this statement say the same rule: same figures, so the two cannot contradict inside one reply."""
    a, b = fs.fixed_statement(TOPIC).working, clarification.CONSTANT_RESTATEMENTS[TOPIC]
    assert re.findall(r"\d+", b) == ["28"] and "28" in a and "maadhimisho" in b and "maadhimisho" in a


class _Backend:
    def __init__(self, reply="JIBU."):
        self.reply, self.calls = reply, 0

    def generate(self, prompt, params=None):
        self.calls += 1
        return self.reply


def _orch(reply="JIBU.", facts=("Ukweli.",)):
    b = _Backend(reply)
    return Orchestrator(b, retriever=lambda q: list(facts), ooc_phrases=[], in_scope_phrases=[]), b


def _item(**kw):
    held = NOW - timedelta(minutes=16)
    base = {"review_id": "2026-11-18T11:44:00+00:00-abcd1234", "status": "pending", "sender": "255700000001@s.whatsapp.net",
            "sender_hash": "abcd1234abcd", "sender_tail": "0001", "question": "q", "draft": "Jibu la injini.", "engine_working": "working",
            "facts": [], "answer_path": "engine:vat_registration", "model_calls": 0, "guards": [], "held_at": held.isoformat(),
            "ts_held": held.isoformat(), "fallback": False}
    base.update(kw)
    return base


@pytest.mark.parametrize("q", [LIVE_SIKU42[0], LIVE_KALENDA[0]])
def test_the_live_question_is_answered_model_free_and_never_auto_sent(q):
    o, b = _orch(reply=LIVE_SIKU42[1])
    reply = o.answer(q)
    t = answer_trace.trace(reply)
    assert t["path"] == "engine:fixed_statement" and t["model_calls"] == 0 and b.calls == 0, t
    assert fs.fixed_statement(TOPIC).working in reply.text and "siku 42" not in reply.text and "mwaka wa kalenda" not in reply.text
    # POSITIVE CONTROL: the same item on an allowed route IS eligible, so the False below is the exclusion and not a broken item (R43)
    assert core.engine_only_verdict(_item())[0] is True
    it = _item(answer_path=t["path"], engine_working=t["working"], facts=["x"], model_calls=0, guards=[])
    assert core.engine_only_verdict(it)[0] is False
    assert core.autosend_verdict(it, now=NOW, after_s=900.0)[0] != "auto_send"


def test_the_tax_return_question_still_goes_to_the_model_and_is_not_confused_with_brela():
    o, b = _orch(reply="Ndani ya miezi 6 baada ya mwisho wa mwaka wa mapato.")
    reply = o.answer("Return ya kodi ya mapato ya kampuni ni lini?")
    assert answer_trace.trace(reply)["path"] != "engine:fixed_statement" and "maadhimisho" not in reply.text


# ── D-FIDELITY-23 ─────────────────────────────────────────────────────────────────────────────────
Q_MINING = "Sekta ya madini ina sekta ndogo ngapi kwenye GN 605A?"
LIVE_46 = "Kulingana na GN 605A, kuna sekta ndogo 46 katika sekta ya madini peke yake. Thibitisha na TanzLII."     # VERBATIM, eval/results/batch6_deploy_live_2026_11_17.json

FLAG = [
    (Q_MINING, LIVE_46),
    (Q_MINING, "Sekta ya madini ina sekta ndogo 46."),
    ("Sekta ya kilimo ina sekta ndogo ngapi kwenye GN 605A?", "Sekta ya kilimo ina sekta ndogo 46."),
    ("Madini yana sekta ndogo ngapi kwenye kima cha chini cha mshahara?", "Katika sekta ya madini kuna 46 sekta ndogo."),
]
PASS = [   # the probes that should come back CLEAN do the work (R17)
    (Q_MINING, "Sekta ya madini ina vipengele vinne: uchimbaji na utafutaji wa madini, leseni ya msingi, dealer na madalali."),
    ("GN 605A inashughulikia sekta ngapi?", "GN 605A inashughulikia sekta 16 na sekta ndogo 46 kwa ujumla."),
    ("GN 605A inashughulikia sekta ngapi?", "GN 605A inashughulikia sekta 16 na sekta ndogo 46."),                   # the overall total, no caveat
    ("Kuna sekta ndogo ngapi kwenye GN 605A?", "Kuna sekta ndogo 46 (takwimu ya PKF; Agizo lenyewe halithibitishi idadi hiyo)."),   # the total WITH its source caveat
    ("Kuna sekta ndogo ngapi kwenye kima cha chini cha mshahara?", "Kulingana na PKF, kuna sekta ndogo 46 kwa sekta zote."),
    (Q_MINING, "Si sekta ndogo 46 katika sekta ya madini; ina vipengele vinne."),                                      # a negation
    ("Sekta ya madini ina wafanyakazi wangapi?", "Kuna sekta ndogo 46 katika sekta ya madini peke yake."),            # not the minimum-wage Order at all
    ("Sekta ya kilimo kwenye GN 605A ina sekta ndogo ngapi?", "Kuna sekta ndogo 3."),
    ("GN 605A inashughulikia sekta ngapi?", "GN 605A inashughulikia sekta 16."),
    (Q_MINING, "Kuna sekta ndogo 46 kwa jumla (PKF), na sekta ya madini ni sehemu yake."),                            # the total, in an answer to a single-sector question: only the total veto saves it
]


@pytest.mark.parametrize("q,b", FLAG)
def test_a_46_stated_for_one_sector_is_flagged(q, b):
    assert fidelity.gn605a_subsector_count_misstated(q, b), b


@pytest.mark.parametrize("q,b", PASS)
def test_a_correct_or_unrelated_sentence_is_not_flagged(q, b):
    assert fidelity.gn605a_subsector_count_misstated(q, b) == [], b


def test_plant_the_total_veto_removed_is_caught(monkeypatch):
    monkeypatch.setattr(fidelity, "_D23_TOTAL", re.compile(r"(?!x)x"))
    assert [1 for q, b in PASS if fidelity.gn605a_subsector_count_misstated(q, b)]


def test_plant_the_single_sector_limb_removed_is_caught(monkeypatch):
    monkeypatch.setattr(fidelity, "_D23_SINGLE", re.compile(r"(?!x)x"))
    monkeypatch.setattr(fidelity, "_D23_Q_SINGLE", re.compile(r"(?!x)x"))
    assert [1 for q, b in FLAG if not fidelity.gn605a_subsector_count_misstated(q, b)]


def test_plant_the_context_requirement_removed_is_caught(monkeypatch):
    monkeypatch.setattr(fidelity, "_D23_CTX", re.compile(r""))
    assert [1 for q, b in PASS if fidelity.gn605a_subsector_count_misstated(q, b)]


def test_the_live_wrong_reply_is_replaced_with_the_restated_constant_end_to_end():
    o, b = _orch(reply=LIVE_46)
    reply = o.answer(Q_MINING)
    t = answer_trace.trace(reply)
    assert b.calls >= 1 and t["guards"] == ["replaced"], t
    assert "sekta ndogo 46 katika sekta ya madini" not in reply.text
    assert clarification.CONSTANT_RESTATEMENTS["gn605a_mining_subsector_count"] in reply.text
    it = _item(answer_path=t["path"], engine_working=t["working"], facts=["x"], model_calls=t["model_calls"], guards=t["guards"])
    assert core.engine_only_verdict(it)[0] is False        # a model-path reply: never auto-sent


def test_a_correct_model_reply_to_the_same_question_is_untouched():
    o, _ = _orch(reply="Sekta ya madini ina vipengele vinne katika GN 605A. Thibitisha na kazi.go.tz.")
    reply = o.answer(Q_MINING)
    assert answer_trace.trace(reply)["guards"] == [] and "vipengele vinne" in reply.text


def test_the_replacement_states_only_what_the_order_settles():
    """GN 605A (kazi.go.tz official copy, edition asserted): sixteen sectors; item 10 Mining Sector has four rows (a)-(d). The 46 is attributed to PKF and not asserted as the Order's."""
    import sys
    sys.path.insert(0, os.path.join(_ROOT, "scripts"))
    from check_source_editions import assert_edition
    rel = "labour/gn605a_2025_kazi_go_tz_official.pdf"
    man = json.load(open(os.path.join(_ROOT, "data", "source_documents", "MANIFEST.json"), encoding="utf-8"))
    entry = man.get("files", man)[rel]
    assert_edition(os.path.join(_ROOT, "data", "source_documents", rel), entry["edition"])      # the read of the Order this text rests on is of the edition the manifest declares
    t = clarification.CONSTANT_RESTATEMENTS["gn605a_mining_subsector_count"]
    assert "sekta 16" in t and "vipengele vinne" in t and "PKF" in t and "Kifungu" not in t
    assert fidelity.gn605a_subsector_count_misstated(Q_MINING, t) == []     # the replacement never trips its own guard
    for row in ("uchimbaji na utafutaji wa madini", "leseni ya msingi ya uchimbaji", "leseni ya wauzaji", "leseni za madalali"):
        assert row in t


def test_the_replacement_text_does_not_trip_the_other_d16_rules():
    t = clarification.CONSTANT_RESTATEMENTS["gn605a_mining_subsector_count"]
    assert fidelity.body_contradicts_d16(Q_MINING, t) == []
