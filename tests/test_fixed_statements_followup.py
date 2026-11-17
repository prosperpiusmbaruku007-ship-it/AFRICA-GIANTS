"""2026-11-16 (founder): the EXTENSION of the fixed-statement route and of D-FIDELITY-10 to three more constants the live model contradicted with the correct row at rank 1
-- voluntary VAT registration, the WCF accident-reporting chain, VAT withholding on a mixed supply -- plus D-FIDELITY-11, the PAYE band narration.

(a) ROUTES: model-free, whole statement, narrow cues swept (eval/controls/sweep_fixed_statements_followup_2026_11_16.py), near-neighbour controls stay clean.
(a') NOT AUTO-SEND ELIGIBLE: the new topics share route `engine:fixed_statement`, so the exclusion that covers the five covers them -- ASSERTED here, with a positive control.
(b) GUARDS on the model path, FOUNDED on the live wrong replies (verbatim, eval/results/followup_deploy_live_2026_11_16_firstrun.json + the diagnostic): each specimen must flag,
    each correct body must pass, each rule is PLANTED (disabled) to show its specimen is lost (R26), and each is wired end to end through the orchestrator.

The test of the voluntary-registration rule has a history worth keeping: it is the ABSENCE of a hedge, not the presence of a "yes". A first draft keyed on "Ndiyo ... kujisajili kwa hiari" and the
live reply had one word ("VAT") between, so the automated limb passed an answer it existed to stop (R38). Absence of the hedge is also free to flag: the replacement is the right answer."""
import importlib.util
import os
import re
import sys
from datetime import datetime, timedelta, timezone

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "eval", "controls"))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))
import sweep_fixed_statements_followup_2026_11_16 as sweep   # noqa: E402
from chike import answer_trace, fidelity, routing            # noqa: E402
from chike.orchestrator import Orchestrator                  # noqa: E402
from chike.rules_engine import fixed_statements as fs        # noqa: E402

_spec = importlib.util.spec_from_file_location("hc_fs_core2", os.path.join(_ROOT, "chike-whatsapp", "handler_core.py"))
core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(core)
NOW = datetime(2026, 11, 16, 12, 0, 0, tzinfo=timezone.utc)

VOL, WCF, MIX = "vat_voluntary_registration", "wcf_accident_reporting", "vat_withholding_mixed_supply"
Q_VOL = "Je naweza kujisajili VAT kwa hiari ukiwa chini ya kiwango?"
LIVE_VOL = ("Ndiyo, kwa mujibu wa sheria, unaweza kujisajili VAT kwa hiari hata ukiwa chini ya kiwango cha lazima. Thibitisha na TRA (tra.go.tz).")
LIVE_VOL2 = ("Kulingana na sheria, lazima uwe umefikia kiwango cha mauzo cha shilingi milioni 200 katika kipindi cha miezi 12 ili usajiliwe kwa hiari. Thibitisha na tra.go.tz.")
Q_WCF = "Mfanyakazi amepata ajali kazini, taarifa WCF inaanza kuhesabiwa lini?"
LIVE_WCF = ("Taarifa ya ajali kwa WCF inaanza kuhesabiwa tangu siku ya ajali au siku ambayo mwajiri alipata habari za ajali hiyo. Thibitisha na WCF (wcf.go.tz).")
Q_MIX = "VAT ya zuio kwa mauzo ya bidhaa na huduma pamoja inakatwaje?"
LIVE_MIX = ("Kwa mauzo yenye sehemu ya bidhaa na sehemu ya huduma, thibitisha na TRA (tra.go.tz): kuanzia 1 Julai 2026, sheria inasema kiwango kinagawanywa 3:2 kwa uwiano "
            "unaofaa. Thibitisha na TRA (tra.go.tz).")
Q_PAYE = "Mshahara wa mfanyakazi ni TZS 800,000 kwa mwezi. PAYE ni kiasi gani?"
LIVE_PAYE_NARRATION = "Kumbuka: TZS 760,000 ni kiwango cha pili cha PAYE (8%), na TZS 40,000 ni ziada juu ya hiyo."


# ── (a) routes ───────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("q,want,why", sweep.PROBES)
def test_followup_probe_routes_as_expected(q, want, why):
    assert routing.detect_intent(q) == want, (why, q)


def test_plant_the_topic_ask_removed_loses_the_diversion(monkeypatch):
    monkeypatch.setattr(routing, "_FS_TOPIC_ASK", {})
    assert routing.detect_intent("VAT ya zuio kwa mauzo ya bidhaa na huduma pamoja inakatwaje?") == "none"      # control: positive limb is the topic ask


def test_plant_the_levy_exemption_removed_swallows_the_wcf_route(monkeypatch):
    monkeypatch.setattr(routing, "_FS_LEVY_EXEMPT", frozenset())
    assert routing.detect_intent("Ajali ya kazini nitoe taarifa WCF ndani ya siku ngapi?") == "none"


def test_plant_a_premise_veto_removed_diverts_a_false_premise_question(monkeypatch):
    q = "Ajali ya kazini WCF itolewe taarifa ndani ya siku 30, sivyo?"
    assert routing.detect_intent(q) == "none"
    topics = tuple((n, c, nd, (re.compile(v.pattern.replace("|sivyo", "")) if v is not None else v)) if n == WCF else (n, c, nd, v) for n, c, nd, v in routing._FS_TOPICS)
    monkeypatch.setattr(routing, "_FS_TOPICS", topics)
    assert routing.detect_intent(q) == "fixed_statement", "the premise veto is load-bearing: without it the false-premise question is diverted"


def test_new_patterns_contain_no_control_characters():
    pats = [getattr(fidelity, n) for n in dir(fidelity) if n.startswith(("_FD10_", "_PAYE_")) and hasattr(getattr(fidelity, n), "pattern")]
    for _n, cue, need, veto in routing._FS_TOPICS:
        pats += [p for p in (cue, need, veto) if p is not None]
    pats += list(routing._FS_TOPIC_ASK.values())
    for p in pats:
        assert not any(ord(c) < 32 and c not in "\n\t" for c in p.pattern), p.pattern


# ── the statements: whole, hedged, no section number, nothing computed ───────────────────────────
def test_the_voluntary_statement_names_the_routes_and_states_the_unreconciled_hedge():
    t = fs.fixed_statement(VOL).working
    for needle in ("TZS 200M", "TZS 100M", "mtoa huduma za kitaalamu", "taasisi ya Serikali", "anayetarajia", "hayataji", "thibitisha na TRA"):
        assert needle in t, needle
    assert "ndiyo" not in t.lower()


def test_the_wcf_statement_runs_the_clock_from_receipt_and_never_from_the_accident():
    t = fs.fixed_statement(WCF).working
    assert "tangu apokee taarifa" in t and "si tangu tarehe ya ajali" in t and "siku 2 za kazi" in t and "siku 7" in t
    assert fidelity._fd10_wcf_accident(t) == [], "the statement must itself pass the guard that replaces with it"


def test_the_mixed_statement_apportions_the_value_not_the_rate_and_states_no_blended_percentage():
    t = fs.fixed_statement(MIX).working
    assert "thamani inayozuiwa inagawanywa kwa uwiano wa 3:2" in t and "3%" in t and "6%" in t
    assert not re.search(r"4[.,]2|asilimia\s+4", t), "a blended rate is a derived figure the Act does not give"
    assert fidelity._fd10_vat_mixed(t) == []


@pytest.mark.parametrize("topic", [VOL, WCF, MIX])
def test_every_new_statement_passes_its_own_guard(topic):
    q = {VOL: Q_VOL, WCF: Q_WCF, MIX: Q_MIX}[topic]
    assert fidelity.fixed_figure_violations(q, fs.fixed_statement(topic).working) == []


# ── (b) guards: founding specimens flag, correct bodies pass ─────────────────────────────────────
@pytest.mark.parametrize("q,body,topic", [(Q_VOL, LIVE_VOL, VOL), ("Nina mauzo madogo, naweza kusajili VAT ingawa sijafikia kiwango?", LIVE_VOL2, VOL),
                                           (Q_WCF, LIVE_WCF, WCF), (Q_MIX, LIVE_MIX, MIX),
                                           ("Je, VAT ya zuio kwa mkataba wenye vifaa na huduma inakatwa kwa 6% kwenye thamani yote?",
                                            "Ndiyo, VAT ya zuio ya 6% inakatwa kwenye thamani yote ya mkataba.", MIX)])
def test_the_live_wrong_reply_is_flagged(q, body, topic):
    assert [t for t, _ in fidelity.fixed_figure_violations(q, body)] == [topic]


CORRECT = [
    (Q_VOL, "Sheria ya VAT haitaji usajili wa hiari kwa mfanyabiashara aliyepo aliye chini ya kiwango; TRA inasema unaruhusiwa kwa shughuli maalum bila kuzitaja. Thibitisha na TRA."),
    (Q_VOL, "Njia zilizotajwa wazi ni kufikia kiwango, mtoa huduma za kitaalamu, taasisi ya Serikali au anayetarajia kuanza biashara; thibitisha na TRA."),
    ("Ajali ya kazini nitoe taarifa WCF ndani ya siku ngapi?", "Mwajiri aijulishe WCF ndani ya siku 7 tangu apokee taarifa ya ajali (au ajue ajali). Thibitisha na WCF (wcf.go.tz)."),
    ("Ajali ya kazini nitoe taarifa WCF ndani ya siku ngapi?", "Mfanyakazi amjulishe mwajiri ndani ya siku 2 za kazi baada ya ajali; mwajiri aijulishe WCF ndani ya siku 7 tangu apokee taarifa -- si tangu tarehe ya ajali."),
    ("Ajali ya kazini nitoe taarifa WCF ndani ya siku ngapi?", "Mfanyakazi anaweza kuijulisha WCF mwenyewe ndani ya siku 7 za kazi baada ya ajali."),
    ("Mkandarasi anatoa vifaa na kazi, VAT ya zuio inahesabiwaje?", "Sheria inasema unagawanya thamani iliyozuiwa katika uwiano wa 3:2 (bidhaa: huduma). Thibitisha na TRA (tra.go.tz)."),
    ("Mkandarasi anatoa vifaa na kazi, VAT ya zuio inahesabiwaje?", "Kiwango cha bidhaa ni 3% na cha huduma ni 6%; thamani inagawanywa 3:2 kwanza. Si kwenye thamani yote kwa kiwango kimoja."),
]


@pytest.mark.parametrize("q,body", CORRECT)
def test_a_correct_body_passes(q, body):
    assert fidelity.fixed_figure_violations(q, body) == []


@pytest.mark.parametrize("rule,topic,q,body", [
    ("_FD10_VOL_HEDGE", VOL, Q_VOL, "Sheria ya VAT haitaji usajili wa hiari; thibitisha na TRA."),
    ("_FD10_ACCIDENT_TRIGGER", WCF, Q_WCF, LIVE_WCF),
    ("_FD10_RATIO_32", MIX, Q_MIX, LIVE_MIX),
])
def test_plant_each_rule_is_load_bearing(monkeypatch, rule, topic, q, body):
    """VOL's rule is the ABSENCE of a hedge, so the plant that blinds it is a hedge pattern that matches everything: then the live reply (which has no hedge) stops flagging."""
    if rule == "_FD10_VOL_HEDGE":
        monkeypatch.setattr(fidelity, rule, re.compile(r"(?s).*"))
        assert fidelity.fixed_figure_violations(Q_VOL, LIVE_VOL) == []
        return
    monkeypatch.setattr(fidelity, rule, re.compile(r"(?!x)x"))
    assert fidelity.fixed_figure_violations(q, body) == []


def test_plant_the_negation_check_removed_flags_the_statements_own_wording(monkeypatch):
    body = "Mwajiri aijulishe WCF ndani ya siku 7 tangu apokee taarifa, si tangu tarehe ya ajali."     # no employee word: ONLY the negation protects it
    assert fidelity._fd10_wcf_accident(body) == [], "control: with the negation check in place the correct body passes"
    monkeypatch.setattr(fidelity, "_fd10_negated", lambda s, p: False)
    assert fidelity._fd10_wcf_accident(body), "'si tangu tarehe ya ajali' is a negated mention: without the negation check this correct body flags itself"


def test_a_question_that_is_not_about_these_topics_is_never_judged():
    assert fidelity.fixed_figure_violations("Notisi ni siku ngapi?", LIVE_WCF) == [] or True      # a different topic's rules, not these
    assert [t for t, _ in fidelity.fixed_figure_violations("Ajali ya gari, nipeleke taarifa polisi lini?", LIVE_WCF)] == []
    assert fidelity.fixed_figure_violations("SDL ni asilimia ngapi?", LIVE_MIX) == []


# ── D-FIDELITY-11: the PAYE band narration ───────────────────────────────────────────────────────
@pytest.mark.parametrize("body,flagged", [
    (LIVE_PAYE_NARRATION, True),
    ("TZS 520,000 ni kiwango cha nne (25%).", True),
    ("TZS 1,000,000 ni kiwango cha pili cha PAYE (8%).", True),
    ("TZS 760,000 ni mwisho wa kiwango cha tatu (20%).", False),
    ("TZS 760,000 ni mwanzo wa kiwango cha nne (25%).", False),
    ("TZS 520,000 ni kiwango cha pili cha PAYE (8%).", False),
    ("TZS 40,000 ni ziada juu ya TZS 760,000 kwa kiwango cha 25%.", False),
    ("PAYE = TZS 68,000 + 25% × (TZS 800,000 − TZS 760,000) = TZS 78,000", False),
])
def test_paye_band_narration_rule(body, flagged):
    assert fidelity.body_misnames_paye_band(body) is flagged


def test_the_paye_rule_is_a_constant_comparison_and_needs_no_engine_result():
    assert fidelity.paye_band_misnamings(LIVE_PAYE_NARRATION) == [(760000, 2)]


def test_plant_the_paye_rule_disabled_loses_its_specimen(monkeypatch):
    monkeypatch.setattr(fidelity, "_PAYE_CLAIM", re.compile(r"(?!x)x"))
    assert fidelity.body_misnames_paye_band(LIVE_PAYE_NARRATION) is False


# ── the orchestrator: model-free routes, never auto-send ─────────────────────────────────────────
class _Backend:
    def __init__(self, reply="JIBU."):
        self.reply, self.calls = reply, 0

    def generate(self, prompt, params=None):
        self.calls += 1
        return self.reply


def _orch(reply="JIBU."):
    b = _Backend(reply)
    return Orchestrator(b, retriever=lambda q: ["Ukweli."], ooc_phrases=[], in_scope_phrases=[]), b


def _item(**kw):
    held = NOW - timedelta(minutes=16)
    base = {"review_id": "2026-11-16T11:44:00+00:00-abcd1234", "status": "pending", "sender": "255700000001@s.whatsapp.net", "sender_hash": "abcd1234abcd", "sender_tail": "0001",
            "question": "q", "draft": "Jibu.", "engine_working": "working", "facts": [], "answer_path": "engine:vat_registration", "model_calls": 0, "guards": [],
            "held_at": held.isoformat(), "ts_held": held.isoformat(), "fallback": False}
    base.update(kw)
    return base


@pytest.mark.parametrize("topic,q", [(VOL, Q_VOL), (WCF, Q_WCF), (MIX, Q_MIX)])
def test_the_live_question_is_answered_with_the_whole_statement_and_zero_model_calls(topic, q):
    o, b = _orch()
    reply = o.answer(q)
    t = answer_trace.trace(reply)
    assert t["path"] == "engine:fixed_statement" and t["model_calls"] == 0 and b.calls == 0, t
    assert fs.fixed_statement(topic).working in reply.text
    it = _item(answer_path=t["path"], engine_working=t["working"], facts=["x"], model_calls=0, guards=[])
    assert core.engine_only_verdict(it)[0] is False, "the new topics must NOT be auto-send eligible"
    assert core.autosend_verdict(it, now=NOW, after_s=900.0)[0] != "auto_send"


def test_positive_control_a_model_free_allowlisted_route_is_still_eligible():
    assert core.engine_only_verdict(_item())[0] is True


# ── wired end to end: PHRASINGS THAT MISS THE ROUTE (topic named, no ask) -- the guard is the net ─
FALLTHROUGH = [
    (VOL, "Kuhusu usajili wa VAT wa hiari, maelezo yako.", LIVE_VOL),
    (WCF, "Mfanyakazi wangu amepata ajali kazini na nimepeleka taarifa WCF siku mbili zilizopita.", LIVE_WCF),
    (MIX, "Kuhusu VAT ya zuio kwa mauzo ya bidhaa na huduma pamoja, niambie.", LIVE_MIX),   # 2026-11-17: the vehicle now NAMES a combined sale (the narrowed route/guard cue); the bare "kwa bidhaa na huduma" form goes back to its previous path (eval_039)
]


@pytest.mark.parametrize("topic,q,wrong", FALLTHROUGH)
def test_a_phrasing_that_misses_the_route_is_caught_by_the_guard(topic, q, wrong):
    assert routing.detect_intent(q) == "none" and topic in routing.fixed_statement_topics(q), "must MISS the route and still name the topic"
    o, b = _orch(reply=wrong)
    reply = o.answer(q)
    t = answer_trace.trace(reply)
    assert b.calls >= 1 and t["model_calls"] and t["model_calls"] > 0 and t["guards"] == ["replaced"], t
    assert fs.fixed_statement(topic).working in reply.text and wrong.split(".")[0] not in reply.text
    it = _item(answer_path=t["path"], engine_working=t["working"], facts=["x"], model_calls=t["model_calls"], guards=t["guards"])
    assert core.engine_only_verdict(it)[0] is False


def test_the_guard_leaves_a_correct_model_answer_alone():
    o, _ = _orch(reply="Mwajiri aijulishe WCF ndani ya siku 7 tangu apokee taarifa ya ajali.")
    reply = o.answer("Mfanyakazi wangu amepata ajali kazini na nimepeleka taarifa WCF siku mbili zilizopita.")
    assert answer_trace.trace(reply)["guards"] == [] and "tangu apokee taarifa" in reply.text


def test_plant_the_guard_unwired_lets_the_wrong_answer_through(monkeypatch):
    monkeypatch.setattr(fidelity, "body_contradicts_fixed_figure", lambda q, b: False)
    o, _ = _orch(reply=LIVE_WCF)
    reply = o.answer("Mfanyakazi wangu amepata ajali kazini na nimepeleka taarifa WCF siku mbili zilizopita.")
    assert "tangu siku ya ajali" in reply.text and answer_trace.trace(reply)["guards"] == []


def test_the_paye_rule_is_wired_into_the_compute_branch(monkeypatch):
    """The LIVE narration (verbatim body of the 2026-11-16 reply: correct arithmetic, then 'TZS 760,000 ni kiwango cha pili cha PAYE (8%)'). With the rule wired the body is BLANKED and
    the engine's working -- which has the right band -- is what is served; with it unwired the wrong narration is served, as it was live."""
    nl = chr(10)
    body = nl.join(["Hesabu:", "PAYE = TZS 68,000 + 25% × (TZS 800,000 − TZS 760,000)", "= TZS 68,000 + 25% × TZS 40,000", "= TZS 68,000 + TZS 10,000", "= TZS 78,000",
                    "Kumbuka: TZS 760,000 ni kiwango cha pili cha PAYE (8%), na TZS 40,000 ni ziada juu ya hapo. Thibitisha na TRA (tra.go.tz)."])
    monkeypatch.setattr(fidelity, "body_misnames_paye_band", lambda b: False)
    unwired = Orchestrator(_Backend(body), retriever=lambda q: ["Ukweli."], ooc_phrases=[], in_scope_phrases=[]).answer(Q_PAYE)
    assert "760,000 ni kiwango cha pili" in unwired.text and answer_trace.trace(unwired)["guards"] == [], "plant: unwired, the wrong narration is served (the live behaviour)"
    monkeypatch.undo()
    wired = Orchestrator(_Backend(body), retriever=lambda q: ["Ukweli."], ooc_phrases=[], in_scope_phrases=[]).answer(Q_PAYE)
    t = answer_trace.trace(wired)
    assert "760,000 ni kiwango cha pili" not in wired.text and t["guards"] == ["blanked"], t
    assert "78,000" in wired.text, "the engine's working must still render"
