"""2026-11-23: the model-free SDL-EXEMPTIONS statement route (founder's decision 2) and the NHIF append (decision 3). R17 probes BOTH ways (twelve of the twenty-nine exemption probes are vetoed or unrelated, the arm that does the work), the statement's content tied
to the sources, zero model calls, never auto-sent, PLANTS (R26), and the NHIF append's three probes."""
import importlib.util
import io
import json
import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
from chike import answer_trace, fidelity, routing   # noqa: E402
from chike.orchestrator import Orchestrator         # noqa: E402
from chike.rules_engine import fixed_statements as fs   # noqa: E402

_PROBES = os.path.join(_ROOT, "eval", "refusal_gate", "sdl_exemptions_probes_2026_11_23.jsonl")
TOPIC = "sdl_exemptions"


def _probes():
    with io.open(_PROBES, encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh if line.strip()]
    assert len(rows) == 29, len(rows)                         # a loader returning nothing must fail, not pass vacuously (R20)
    assert sum(1 for r in rows if r["expect"] == "statement") >= 7 and sum(1 for r in rows if r["expect"] == "not_statement") >= 10
    return rows


def _q(pid):
    return [p for p in _probes() if p["id"] == pid][0]["question"]


def _is_statement(q):
    return routing.detect_intent(q) == "fixed_statement" and routing.fixed_statement_topic(q) == TOPIC


@pytest.mark.parametrize("p", _probes(), ids=lambda p: p["id"])
def test_probe_routes_as_authored(p):
    assert _is_statement(p["question"]) == (p["expect"] == "statement"), p["guards_against"]


def test_the_statement_is_the_approved_text_tied_to_the_sources():
    t = fs.fixed_statement(TOPIC).working
    for needle in ("ruzuku ya Serikali", "balozi", "Umoja wa Mataifa", "TaESA", "mashambani", "mamlaka ya maji", "Waziri wa Fedha", "Gazeti", "taasisi za elimu zilizosajiliwa", "taasisi za dini", "mashirika ya hisani", "halmashauri"):
        assert needle in t, needle
    assert "Kifungu" not in t and "Cap" not in t                      # R44: the Act is named, no section number
    assert "tra.go.tz" in t and "10 au zaidi" in t
    assert TOPIC in fs.TOPICS and TOPIC in fs.TOPICS_NO_CONCISE_ROW


class _B:
    calls = 0

    def generate(self, prompt, params=None):
        _B.calls += 1
        return "x"


def _answer(q):
    return Orchestrator(_B(), retriever=lambda x: ["f"], ooc_phrases=[], in_scope_phrases=[]).answer(q)


@pytest.mark.parametrize("pid", ["se_01", "se_02", "se_03", "se_04", "se_14", "se_20"])
def test_the_statement_answers_list_and_category_asks_with_zero_model_calls(pid):
    _B.calls = 0
    reply = _answer(_q(pid))
    t = answer_trace.trace(reply)
    assert t["path"] == "engine:fixed_statement" and t["model_calls"] == 0 and _B.calls == 0, t
    assert fs.fixed_statement(TOPIC).working in reply.text


def test_it_is_never_auto_sent():
    spec = importlib.util.spec_from_file_location("hc_se_core", os.path.join(_ROOT, "chike-whatsapp", "handler_core.py"))
    core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)
    assert "engine:fixed_statement" in core.AUTOSEND_EXCLUDED_ENGINE_ROUTES


def test_the_guard_loop_skips_the_route_only_topic():
    assert fidelity.fixed_figure_violations(_q("se_02"), "Shule binafsi zinatozwa SDL.") == []


def test_plant_the_headcount_veto_removed_diverts_an_engine_question(monkeypatch):
    new = tuple((n, c, nd, re.compile(r"(?!x)x") if n == TOPIC else v) for n, c, nd, v in routing._FS_TOPICS)
    q = "Shule yenye wafanyakazi 15 inalipa SDL?"      # a headcount WITH a pay verb: only the veto (not the verb list) stops it -- se_09's "natakiwa kulipa" never reached the cue, a bad plant specimen
    assert routing.fixed_statement_topic(q) != TOPIC, "the headcount veto must stop it BEFORE the plant"
    monkeypatch.setattr(routing, "_FS_TOPICS", new)
    assert routing.fixed_statement_topic(q) == TOPIC, "with the vetoes removed a headcount question must wrongly reach the statement"
    assert routing.fixed_statement_topic(_q("se_15")) == TOPIC and routing.fixed_statement_topic(_q("se_17")) == TOPIC


def test_plant_the_cue_removed_loses_the_specimen(monkeypatch):
    monkeypatch.setattr(routing, "_FS_TOPICS", tuple(t for t in routing._FS_TOPICS if t[0] != TOPIC))
    assert not _is_statement(_q("se_02"))


def test_plant_the_dini_boundary_removed_recreates_the_madini_collision(monkeypatch):
    q = "Madini inalipa SDL?"      # no employer-type noun: only the 'dini' stem could carry the category cue (se_14 is now a statement on its employer type, so it no longer isolates the boundary)
    assert routing.fixed_statement_topic(q) != TOPIC, "the word boundary must stop 'dini' matching inside 'madini' BEFORE the plant"
    new = []
    for n, c, nd, v in routing._FS_TOPICS:
        if n == TOPIC:
            nd = re.compile(nd.pattern.replace("(?<![a-z])dini", "dini"), nd.flags)
        new.append((n, c, nd, v))
    monkeypatch.setattr(routing, "_FS_TOPICS", tuple(new))
    assert routing.fixed_statement_topic(q) == TOPIC, "without the word boundary 'madini' matches 'dini'; if not, the boundary is decoration"


def test_plant_the_employer_type_cue_removed_loses_the_mining_specimen(monkeypatch):
    new = []
    for n, c, nd, v in routing._FS_TOPICS:
        if n == TOPIC:
            nd = re.compile(nd.pattern.replace("kampuni|biashara|duka|mgodi|hoteli|mgahawa|saluni|kiwanda|benki|hospitali|zahanati|ofisi|mradi|", ""), nd.flags)
        new.append((n, c, nd, v))
    monkeypatch.setattr(routing, "_FS_TOPICS", tuple(new))
    assert not _is_statement(_q("se_20")), "without the employer-type cue the mining specimen must fall off the route; if not, the widening is decoration"


def test_plant_the_widening_vetoes_removed_hijack_the_payer_and_where_to_pay_asks(monkeypatch):
    new = []
    for n, c, nd, v in routing._FS_TOPICS:
        if n == TOPIC:
            v = re.compile(v.pattern.replace(r"wapi|namna|njia|akaunti|control|malipo\s+ya|muda|baada\s+ya|mfanyakazi|kukatwa|inakatwa|anakatwa|makato|", ""), v.flags)
        new.append((n, c, nd, v))
    monkeypatch.setattr(routing, "_FS_TOPICS", tuple(new))
    assert routing.fixed_statement_topic(_q("se_24")) == TOPIC and routing.fixed_statement_topic(_q("se_27")) == TOPIC   # se_23 (who pays) moved to the sdl_payer route on 2026-11-23; the shared payer-side veto still stops it here, so it is no longer a plant specimen


def test_new_patterns_contain_no_control_characters():
    for n, cue, need, veto in routing._FS_TOPICS:
        if n == TOPIC:
            for r in (cue, need, veto, routing._FS_TOPIC_ASK[TOPIC]):
                assert not any(ord(c) < 32 and c != "\n" for c in r.pattern)


# ---- NHIF named alongside NSSF: keep the answer, APPEND one line (founder's decision 3) ----
def test_the_live_nhif_specimen_keeps_the_nssf_answer_and_gains_the_line():
    reply = _answer("NHIF inakatwa asilimia ngapi pamoja na NSSF kwenye mshahara?")
    assert not reply.refused
    assert "asilimia 10" in reply.text                                   # the NSSF answer is kept, not refused
    assert reply.text.rstrip().endswith(fidelity.NHIF_APPEND) and reply.text.count(fidelity.NHIF_APPEND) == 1


def test_an_nssf_only_question_gets_no_line():
    for q in ("NSSF ya mfanyakazi ni asilimia ngapi?", "Nina wafanyakazi 15, je natakiwa kulipa SDL?"):
        assert fidelity.NHIF_APPEND not in _answer(q).text, q


def test_an_nhif_only_verb_qualified_question_is_still_refused_by_the_ooc_list():
    from chike import classification
    ooc, ins = classification.resolve_phrases(classification.load_local_config())
    o = Orchestrator(_B(), retriever=lambda x: ["f"], ooc_phrases=ooc, in_scope_phrases=ins)
    r = o.answer("Makato ya NHIF kwa mshahara wa TZS 800,000 ni kiasi gani?")
    assert r.refused and fidelity.NHIF_APPEND not in r.text             # a refusal is left exactly as it was


def test_no_double_line_when_the_repair_note_is_already_there():
    t = "NSSF ni asilimia 10. " + fidelity.NHIF_NOT_COVERED_NOTE
    assert fidelity.append_nhif_note("NSSF na NHIF?", t) == t


def test_plant_the_append_unwired_loses_the_line(monkeypatch):
    monkeypatch.setattr(fidelity, "append_nhif_note", lambda q, t: t)
    assert fidelity.NHIF_APPEND not in _answer("NHIF inakatwa asilimia ngapi pamoja na NSSF kwenye mshahara?").text


def test_plant_the_sez_veto_removed_diverts_the_sez_question(monkeypatch):
    new = []
    for n, c, nd, v in routing._FS_TOPICS:
        if n == TOPIC:
            v = re.compile(v.pattern.replace(r"(?<![a-z])sez(?![a-z])|special\s+economic|", ""), v.flags)
        new.append((n, c, nd, v))
    monkeypatch.setattr(routing, "_FS_TOPICS", tuple(new))
    assert routing.fixed_statement_topic(_q("se_29")) == TOPIC, "without the SEZ veto the SEZ question must reach the statement; if not, the veto is decoration"
