"""2026-11-16: the five fixed statutory statements (notice, severance, overtime, annual leave, VAT time of supply).

(a) MODEL-FREE ROUTES -- all limbs stated, never a picked one; narrow cues swept (eval/controls/sweep_fixed_statements_2026_11_16.py).
(a') NOT AUTO-SEND ELIGIBLE -- founder's restriction, a NARROWING of the R7 amendment; fails closed on any route not on the allowlist.
(b) GUARDS (D-FIDELITY-10, R19 constant comparisons) on the model path, founded on the five live wrong replies of 2026-11-13.

Every guard and every cue is PLANTED (disabled / made over-broad) to show a test fires (R26), and every guard has correct bodies that
must pass (R17: the probes that should come back CLEAN do the work)."""
import importlib.util
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "eval", "controls"))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))
import sweep_fixed_statements_2026_11_16 as sweep      # noqa: E402
from chike import answer_trace, fidelity, routing, rules_engine   # noqa: E402
from chike.orchestrator import Orchestrator            # noqa: E402
from chike.rules_engine import fixed_statements as fs   # noqa: E402

_spec = importlib.util.spec_from_file_location("hc_fs_core", os.path.join(_ROOT, "chike-whatsapp", "handler_core.py"))
core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(core)

NOW = datetime(2026, 11, 16, 12, 0, 0, tzinfo=timezone.utc)

# The five live wrong replies of the 2026-11-13 coverage deploy (eval/results/coverage_deploy_live_2026_11_13.json), VERBATIM.
LIVE = {
    "notice": ("Notisi ya kuachisha mfanyakazi wa kila mwezi ni siku ngapi?",
               "Kwa mfanyakazi wa kila mwezi, notisi ni siku 4. Thibitisha na mamlaka husika (osha.go.tz)."),
    "severance": ("Severance pay inahesabiwaje?",
                  "Mfanyakazi aliyetimiza miezi 12+ (miaka 1+) anapata: mshahara wake wa mwisho + asilimia 25% ya mshahara wake wa mwisho. "
                  "Thibitisha na sheria husika (elra.go.tz)."),
    "overtime": ("Overtime inalipwa kiasi gani?",
                 "Kiwango cha chini cha overtime ni asilimia 25% ya mshahara wa msingi. Thibitisha na GN605A (sekta yako)."),
    "annual_leave": ("Likizo ya mwaka ni siku ngapi?",
                     "Ndiyo, unatakiwa kulipa mshahara kamili wakati wa likizo. Hakuna sheria inayokuruhusu kusimamisha malipo ya mshahara "
                     "wakati wa likizo. Thibitisha na ELRA (elra.go.tz)."),
    "vat_time_of_supply": ("Nimeuza kwa mkopo, VAT inalipwa lini?",
                           "Kwa mauzo ya mkopo, unaweza kuomba kulipa VAT kidogo kidogo kulingana na makubaliano ya malipo. "
                           "Thibitisha na tra.go.tz."),
}


# ── the statements are the verified facts, not a second copy that can drift ─────────────────────
def _nums(text):
    return sorted(set(re.findall(r"\d+(?:[.,]\d+)?", text)))


@pytest.mark.parametrize("topic", fs.TOPICS)
def test_statement_figures_equal_the_served_row_and_the_locked_fact(topic):
    import precompute_rag_embeddings as pre
    key, text, _ = fs.STATEMENTS[topic]
    row = pre.CONCISE_BILINGUAL_FACTS[key]
    assert _nums(text) == _nums(row), (topic, _nums(text), _nums(row))
    facts = json.load(open(os.path.join(_ROOT, "scripts", "locked_facts.json"), encoding="utf-8"))
    fact = facts[key] if isinstance(facts, dict) and key in facts else [f for f in facts if f.get("key") == key][0]
    cv = fact["correct_value"]
    for n in re.findall(r"\d+(?:\.\d+)?", cv):
        assert n in text, (topic, n, "correct_value figure missing from the statement")


def test_the_notice_statement_states_every_limb_and_picks_none():
    t = fs.fixed_statement("notice").working
    for limb in ("siku 7", "siku 4", "siku 28"):
        assert limb in t
    assert "kila mwezi" in t and "kila wiki" in t


def test_an_unknown_topic_raises_rather_than_guessing():
    with pytest.raises(KeyError):
        fs.fixed_statement("capital_gains")


# ── routes: probes (diverting AND clean) + plants ──────────────────────────────────────────────
@pytest.mark.parametrize("q,want,why", sweep.PROBES)
def test_probe_routes_as_expected(q, want, why):
    assert routing.detect_intent(q) == want, why


def _failed(monkeypatch, name, value):
    monkeypatch.setattr(routing, name, value)
    return [q for q, want, _ in sweep.PROBES if routing.detect_intent(q) != want]


def test_plant_ask_cue_disabled_is_caught(monkeypatch):
    assert _failed(monkeypatch, "_FS_ASK", re.compile(r"(?!x)x"))


def test_plant_ask_cue_made_universal_is_caught(monkeypatch):
    failed = _failed(monkeypatch, "_FS_ASK", re.compile(r""))
    assert any("akikataa kuchukua likizo" in q or "Mkataba wa kazi" in q or "nahitaji mashine" in q for q in failed)


def test_plant_other_levy_veto_removed_is_caught(monkeypatch):
    failed = _failed(monkeypatch, "_FS_OTHER_LEVY", re.compile(r"(?!x)x"))
    assert any("NSSF" in q or "SDL" in q for q in failed)


def test_plant_two_topic_decline_removed_is_caught(monkeypatch):
    """Pretend the first of two matching topics is enough: the two-topic probe must then divert, and the sweep catches it."""
    orig = routing.fixed_statement_topics

    def first_wins(text):
        ql = text.lower()
        if not routing._FS_ASK.search(ql) or routing._FS_OTHER_LEVY.search(ql):
            return None
        hits = orig(text)
        return hits[0] if hits else None
    monkeypatch.setattr(routing, "fixed_statement_topic", first_wins)
    assert any("overtime na severance" in q for q, want, _ in sweep.PROBES if routing.detect_intent(q) != want)


def test_new_patterns_contain_no_control_characters():
    """R39: a non-raw escape compiles to a backspace and matches nothing, invisibly."""
    pats = [routing._FS_ASK, routing._FS_OTHER_LEVY]
    for _n, cue, need, veto in routing._FS_TOPICS:
        pats += [p for p in (cue, need, veto) if p is not None]
    pats += [getattr(fidelity, n) for n in dir(fidelity) if n.startswith("_FD10") and hasattr(getattr(fidelity, n), "pattern")]
    pats += list(fidelity._FD10_SUBJECT_WORDS.values())
    assert len(pats) > 20
    for p in pats:
        assert not any(ord(c) < 32 for c in p.pattern), p.pattern


# ── the orchestrator: model-free, whole statement ──────────────────────────────────────────────
class _Backend:
    """Returns a fixed reply and counts calls."""

    def __init__(self, reply="JIBU."):
        self.reply, self.calls = reply, 0

    def generate(self, prompt, params=None):
        self.calls += 1
        return self.reply


def _orch(reply="JIBU.", facts=("Ukweli.",)):
    b = _Backend(reply)
    return Orchestrator(b, retriever=lambda q: list(facts), ooc_phrases=[], in_scope_phrases=[]), b


@pytest.mark.parametrize("topic", fs.TOPICS)
def test_the_live_question_is_answered_with_the_whole_statement_and_zero_model_calls(topic):
    q, _ = LIVE[topic]
    o, b = _orch()
    reply = o.answer(q)
    t = answer_trace.trace(reply)
    assert t["path"] == "engine:fixed_statement" and t["model_calls"] == 0 and b.calls == 0, t
    assert fs.fixed_statement(topic).working in reply.text


def test_the_notice_answer_does_not_pick_the_limb_the_question_named():
    """The live defect was 'siku 4' for a MONTHLY employee. The model-free answer states 28 AND the other limbs."""
    o, _ = _orch()
    text = o.answer(LIVE["notice"][0]).text
    assert "siku 28" in text and "siku 4" in text and "siku 7" in text


# ── NOT AUTO-SEND ELIGIBLE: the founder's restriction, fail-closed, with a positive control ─────
def _item(**kw):
    held = NOW - timedelta(minutes=16)
    base = {"review_id": "2026-11-16T11:44:00+00:00-abcd1234", "status": "pending", "sender": "255700000001@s.whatsapp.net",
            "sender_hash": "abcd1234abcd", "sender_tail": "0001", "question": "q",
            "draft": "Jibu la injini.", "engine_working": "working", "facts": [], "answer_path": "engine:vat_registration",
            "model_calls": 0, "guards": [], "held_at": held.isoformat(), "ts_held": held.isoformat(), "fallback": False}
    base.update(kw)
    return base


def test_positive_control_a_model_free_engine_route_is_still_eligible():
    assert core.engine_only_verdict(_item())[0] is True
    assert core.autosend_verdict(_item(), now=NOW, after_s=900.0)[0] == "auto_send"


def test_the_fixed_statement_route_is_never_auto_sent_even_when_everything_else_qualifies():
    it = _item(answer_path="engine:fixed_statement")            # model_calls 0, no guard, working present, evidence present
    ok, why = core.engine_only_verdict(it)
    assert ok is False and "excluded" in why, why
    assert core.autosend_verdict(it, now=NOW, after_s=900.0)[0] == "hold_notice"


def test_an_unknown_engine_route_fails_closed():
    ok, why = core.engine_only_verdict(_item(answer_path="engine:some_new_route"))
    assert ok is False and "allowlist" in why


def test_every_route_the_router_can_produce_is_either_allowed_or_excluded_deliberately():
    """A new compute type must be put on one list ON PURPOSE. 'ambiguous_multi' only ever clarifies (':ask'), so it is refused elsewhere."""
    known = set(core.AUTOSEND_ELIGIBLE_ENGINE_ROUTES) | set(core.AUTOSEND_EXCLUDED_ENGINE_ROUTES)
    for ctype in routing.COMPUTE_TYPES:
        assert f"engine:{ctype}" in known, f"{ctype} is on neither auto-send list"
    for extra in ("engine:vat_registration", "engine:efd_requirement", "engine:presumptive"):
        assert extra in known
    assert not (set(core.AUTOSEND_ELIGIBLE_ENGINE_ROUTES) & set(core.AUTOSEND_EXCLUDED_ENGINE_ROUTES))


def test_plant_the_exclusion_removed_is_caught(monkeypatch):
    """R26: with the exclusion deleted AND the route admitted, the same item DOES qualify -- so the test above can fail."""
    monkeypatch.setattr(core, "AUTOSEND_EXCLUDED_ENGINE_ROUTES", frozenset())
    monkeypatch.setattr(core, "AUTOSEND_ELIGIBLE_ENGINE_ROUTES",
                        core.AUTOSEND_ELIGIBLE_ENGINE_ROUTES | {"engine:fixed_statement"})
    assert core.engine_only_verdict(_item(answer_path="engine:fixed_statement"))[0] is True


def test_plant_deleting_only_the_exclusion_still_refuses_because_the_allowlist_is_the_second_lock(monkeypatch):
    monkeypatch.setattr(core, "AUTOSEND_EXCLUDED_ENGINE_ROUTES", frozenset())
    ok, why = core.engine_only_verdict(_item(answer_path="engine:fixed_statement"))
    assert ok is False and "allowlist" in why


def test_the_real_trace_of_a_fixed_statement_reply_is_refused_and_carries_the_banner():
    o, _ = _orch()
    t = answer_trace.trace(o.answer(LIVE["overtime"][0]))
    it = _item(answer_path=t["path"], engine_working=t["working"], facts=t["facts"] or ["x"], model_calls=t["model_calls"],
               guards=t["guards"])
    assert core.engine_only_verdict(it)[0] is False
    sw, en = core.autosend_note(it, now=NOW, after_s=900.0)
    assert "FIXED STATEMENT" in en and "never auto-sent" in en and "JIBU LA SHERIA" in sw


# ── GUARDS (D-FIDELITY-10): the five live replies are the founding specimens ────────────────────
@pytest.mark.parametrize("topic", fs.TOPICS)
def test_the_live_wrong_reply_is_flagged(topic):
    q, body = LIVE[topic]
    got = fidelity.fixed_figure_violations(q, body)
    assert got and got[0][0] == topic, (topic, got)


CORRECT = [
    # (question, a CORRECT body that must pass)
    (LIVE["notice"][0], "Kwa mfanyakazi wa kila mwezi, notisi ni siku 28 baada ya mwezi wa kwanza."),
    (LIVE["notice"][0], "Mwezi wa kwanza: siku 7. Baada ya hapo: siku 4 kwa wa kila wiki, siku 28 kwa wa kila mwezi."),
    ("Mfanyakazi wa kila wiki, notisi ni siku ngapi?", "Kwa mfanyakazi wa kila wiki notisi ni siku 4."),
    ("Mfanyakazi wa kila mwezi, notisi ni siku ngapi? Mkataba unasema siku 30.", "Mkataba unaweza kuweka siku 30, ambayo ni zaidi ya siku 28."),
    (LIVE["severance"][0], "Angalau mshahara wa msingi wa siku 7 kwa kila mwaka kamili, hadi miaka 10, baada ya miezi 12 mfululizo."),
    (LIVE["severance"][0], "Malipo si asilimia 25 ya mshahara; ni siku 7 kwa kila mwaka kamili."),
    (LIVE["overtime"][0], "Overtime inalipwa angalau mara 1.5 ya mshahara wa msingi."),
    (LIVE["overtime"][0], "Overtime inalipwa asilimia 150 ya mshahara wa msingi."),
    (LIVE["overtime"][0], "Overtime inalipwa asilimia 50 zaidi ya mshahara wa kawaida."),
    ("Overtime inalipwa kiasi gani, na inakatwa NSSF?", "Overtime ni mara 1.5. NSSF ni asilimia 10 kwa mwajiri."),
    (LIVE["annual_leave"][0], "Likizo ya mwaka ni angalau siku 28 mfululizo, na unalipwa mshahara wako."),
    (LIVE["annual_leave"][0], "Likizo ya mwaka ni wiki 4 (siku 28), analipwa mshahara."),
    ("Likizo ya mwaka ni siku ngapi, na ya uzazi?", "Likizo ya mwaka ni siku 28. Likizo ya uzazi ni siku 84."),
    (LIVE["vat_time_of_supply"][0],
     "VAT inadaiwa mapema zaidi kati ya invoice, malipo au usambazaji. Return ni tarehe 20 ya mwezi unaofuata."),
    (LIVE["vat_time_of_supply"][0], "Si kidogo kidogo; VAT inadaiwa ukitoa invoice hata mteja asipolipa bado."),
]


@pytest.mark.parametrize("q,body", CORRECT)
def test_a_correct_body_passes(q, body):
    assert fidelity.fixed_figure_violations(q, body) == [], (q, body)


@pytest.mark.parametrize("q,body", [
    # the topic is not the question's: the same words in a question about something else are NOT judged
    ("Likizo ya uzazi ni siku ngapi?", "Likizo ya uzazi ni siku 84."),
    ("Kizingiti cha VAT ni kiasi gani?", "Kizingiti ni TZS 200,000,000. Return ni tarehe 20."),
    ("SDL ni asilimia ngapi?", "SDL ni asilimia 3.5 ya mshahara wa jumla."),
    ("PAYE inalipwa tarehe ngapi?", "PAYE inalipwa tarehe 7 ya mwezi unaofuata."),
    ("Nikichelewa kulipa NSSF adhabu ni nini?", "Adhabu ni asilimia 5 kwa mwezi."),
    # the priced false positive: an NSSF question about overtime, answered with the NSSF split (training row batch_003_cleaned:214)
    ("NSSF inahesabiwaje kwa wafanyakazi wanaopata overtime?", "Kiwango: mwajiri 10% + mfanyakazi 10% ya mshahara wa jumla."),
])
def test_a_question_outside_the_five_topics_is_never_judged(q, body):
    assert fidelity.fixed_figure_violations(q, body) == []


@pytest.mark.parametrize("topic,rule", [
    ("notice", "_fd10_notice"), ("severance", "_fd10_severance"), ("overtime", "_fd10_overtime"),
    ("annual_leave", "_fd10_annual_leave"), ("vat_time_of_supply", "_fd10_vat"),
])
def test_plant_each_rule_disabled_loses_its_founding_specimen(monkeypatch, topic, rule):
    """R26: the specimen is flagged BY THIS RULE. Disable it and the specimen goes unflagged, so the specimen test above can fail."""
    q, body = LIVE[topic]
    assert fidelity.fixed_figure_violations(q, body)
    monkeypatch.setattr(fidelity, rule, lambda *a, **k: [])
    assert fidelity.fixed_figure_violations(q, body) == []


def test_plant_an_overbroad_overtime_rule_is_caught_by_the_correct_bodies(monkeypatch):
    monkeypatch.setattr(fidelity, "_FD10_PERCENT", re.compile(r"(\d+(?:[.,]\d+)?)\s*()"))
    bad = [(q, b) for q, b in CORRECT if fidelity.fixed_figure_violations(q, b)]
    assert bad


def test_plant_the_negation_check_removed_is_caught(monkeypatch):
    monkeypatch.setattr(fidelity, "_fd10_negated", lambda s, p: False)
    assert any(fidelity.fixed_figure_violations(q, b) for q, b in CORRECT)


# ── wired end to end: PHRASINGS THAT MISS THE ROUTES -- the guard is the fallthrough's safety net ─
FALLTHROUGH = [
    ("notice", "Mfanyakazi wa kila mwezi nikimwachisha, notisi ni ya siku zipi?", LIVE["notice"][1]),
    ("severance", "Naomba maelezo ya severance pay kwa mfanyakazi aliyeachishwa.", LIVE["severance"][1]),
    ("overtime", "Naomba kujua kuhusu overtime ya wafanyakazi wangu.", LIVE["overtime"][1]),
    ("annual_leave", "Likizo ya mwaka na overtime ni siku ngapi?", LIVE["annual_leave"][1]),
    ("vat_time_of_supply", "Nimeuza kwa mkopo, naomba kujua kuhusu VAT.", LIVE["vat_time_of_supply"][1]),
]


@pytest.mark.parametrize("topic,q,wrong", FALLTHROUGH)
def test_a_phrasing_that_misses_the_route_is_caught_by_the_guard(topic, q, wrong):
    assert routing.detect_intent(q) == "none", "this phrasing must MISS the route, or it is not exercising the guard"
    o, b = _orch(reply=wrong)
    reply = o.answer(q)
    t = answer_trace.trace(reply)
    assert b.calls >= 1 and t["model_calls"] and t["model_calls"] > 0
    assert t["guards"] == ["replaced"], t
    first = topic if topic != "annual_leave" else "annual_leave"
    assert fs.fixed_statement(first).working in reply.text
    assert wrong.split(".")[0] not in reply.text
    # never auto-send eligible: a model-path reply with a guard
    it = _item(answer_path=t["path"], engine_working=t["working"], facts=["x"], model_calls=t["model_calls"], guards=t["guards"])
    assert core.engine_only_verdict(it)[0] is False


def test_the_guard_does_not_touch_a_correct_model_answer_on_a_missed_phrasing():
    o, _ = _orch(reply="Overtime inalipwa angalau mara 1.5 ya mshahara wa msingi.")
    reply = o.answer("Naomba kujua kuhusu overtime ya wafanyakazi wangu.")
    assert answer_trace.trace(reply)["guards"] == []
    assert "mara 1.5" in reply.text


def test_plant_the_guard_unwired_lets_the_wrong_answer_through(monkeypatch):
    monkeypatch.setattr(fidelity, "body_contradicts_fixed_figure", lambda q, b: False)
    o, _ = _orch(reply=LIVE["overtime"][1])
    reply = o.answer("Naomba kujua kuhusu overtime ya wafanyakazi wangu.")
    assert "asilimia 25" in reply.text and answer_trace.trace(reply)["guards"] == []
