"""2026-11-22: the future-year-rate fixed statement (preliminary Gate 2 #20). R17 probes both ways, figures tied to the locked facts, zero model calls, and PLANTS (R26) showing each limb is load-bearing."""
import json
import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
from chike import answer_trace, routing, fidelity   # noqa: E402
from chike.orchestrator import Orchestrator         # noqa: E402
from chike.rules_engine import fixed_statements as fs   # noqa: E402

_PROBES = os.path.join(_ROOT, "eval", "refusal_gate", "future_year_rate_probes_2026_11_22.jsonl")
TOPIC = "future_year_rate"


def _probes():
    with open(_PROBES, encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh if line.strip()]
    assert len(rows) == 18, len(rows)                      # a loader returning nothing must fail, not pass vacuously (R20)
    assert any(r["expect_route"] == TOPIC for r in rows) and any(r["expect_route"] != TOPIC for r in rows)
    return rows


def _fires(q):
    return routing.detect_intent(q) == "fixed_statement" and routing.fixed_statement_topic(q) == TOPIC


@pytest.mark.parametrize("p", _probes(), ids=lambda p: p["id"])
def test_probe_routes_as_authored(p):
    assert _fires(p["question"]) == (p["expect_route"] == TOPIC), p["guards_against"]


def test_the_statement_figures_are_the_locked_facts():
    facts = json.load(open(os.path.join(_ROOT, "scripts", "locked_facts.json"), encoding="utf-8"))
    facts = facts.get("facts", facts)
    assert "18%" in facts["vat_standard_rate"]["fact"] and "3.5%" in facts["sdl_rate"]["fact"] and "Finance Act 2023" in facts["sdl_rate"]["fact"]
    t = fs.fixed_statement(TOPIC).working
    assert "asilimia 18" in t and "asilimia 3.5" in t and "Sheria ya Fedha 2023" in t
    assert not re.search(r"asilimia 16|Kifungu|Kifungu", t)          # the secondary-only 16% carve-out is deliberately not stated; R44: no section number
    assert "hakijulikani" in t                                       # the unknown limb is the point


def test_the_answer_is_the_whole_statement_with_zero_model_calls():
    class B:
        calls = 0

        def generate(self, prompt, params=None):
            B.calls += 1
            return "x"
    o = Orchestrator(B(), retriever=lambda q: ["f"], ooc_phrases=[], in_scope_phrases=[])
    for q in ("Kiwango cha SDL itakuwa ngapi mwaka 2027?", _probes()[0]["question"]):
        reply = o.answer(q)
        t = answer_trace.trace(reply)
        assert t["path"] == "engine:fixed_statement" and t["model_calls"] == 0 and B.calls == 0, t
        assert fs.fixed_statement(TOPIC).working in reply.text


def test_the_guard_loop_does_not_fall_through_to_the_vat_rule():
    """Without the explicit skip, an unknown topic reaches `_fd10_vat`; this topic names VAT, so a correct statement-like body must not be judged by it."""
    q = _probes()[0]["question"]
    assert fidelity.fixed_figure_violations(q, fs.fixed_statement(TOPIC).working) == []


def test_plant_cue_removed_loses_the_specimen(monkeypatch):
    monkeypatch.setattr(routing, "_FS_TOPICS", tuple(t for t in routing._FS_TOPICS if t[0] != TOPIC))
    assert not _fires(_probes()[0]["question"])


def test_plant_path0_removed_sends_the_sdl_question_to_the_sdl_statement(monkeypatch):
    real = routing.fixed_statement_topic
    monkeypatch.setattr(routing, "fixed_statement_topic", lambda text: None if real(text) == TOPIC else real(text))
    assert routing.detect_intent("Kiwango cha SDL itakuwa ngapi mwaka 2027?") == "sdl"


def test_plant_the_veto_removed_is_caught_by_the_threshold_probe(monkeypatch):
    new = tuple((n, c, nd, None) if n == TOPIC else (n, c, nd, v) for n, c, nd, v in routing._FS_TOPICS)
    monkeypatch.setattr(routing, "_FS_TOPICS", new)
    q = [p for p in _probes() if p["id"] == "fy_11"][0]["question"]
    assert _fires(q), "with the veto removed the registration-threshold question must wrongly fire; if not, the veto is decoration"


def test_the_route_is_never_auto_sent():
    spec_ok = "engine:fixed_statement"
    import importlib.util
    spec = importlib.util.spec_from_file_location("hc_fyr_core", os.path.join(_ROOT, "chike-whatsapp", "handler_core.py"))
    core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)
    assert spec_ok in core.AUTOSEND_EXCLUDED_ENGINE_ROUTES and spec_ok not in core.AUTOSEND_ELIGIBLE_ENGINE_ROUTES


def test_new_patterns_contain_no_control_characters():
    for n, cue, need, veto in routing._FS_TOPICS:
        if n == TOPIC:
            for r in (cue, need, veto, routing._FS_TOPIC_ASK[TOPIC]):
                assert not any(ord(c) < 32 and c != "\n" for c in r.pattern)
