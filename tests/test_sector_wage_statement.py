"""2026-11-22: the no-figure sector-wage statement (PROGRESS 5, domestic workers) and the pay cues `anayelipwa` / `nampa`. R17 probes BOTH WAYS (the vetoed asks are the measured wrong-topic diversions), statement figures tied to the transcribed
Schedule, zero model calls, never auto-sent, and PLANTS (R26) showing each limb is load-bearing."""
import importlib.util
import json
import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
from chike import answer_trace, fidelity, routing, rules_engine   # noqa: E402
from chike.orchestrator import Orchestrator                        # noqa: E402
from chike.rules_engine import wage_schedule as ws                 # noqa: E402

_PROBES = os.path.join(_ROOT, "eval", "refusal_gate", "sector_wage_statement_probes_2026_11_22.jsonl")
TOPIC = "sector_minimum_wage"


def _probes():
    with open(_PROBES, encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh if line.strip()]
    assert len(rows) == 20, len(rows)                         # a loader returning nothing must fail, not pass vacuously (R20)
    assert {r["expect"] for r in rows} == {"statement", "minimum_wage", "neither"}
    return rows


def _q(pid):
    return [p for p in _probes() if p["id"] == pid][0]["question"]


def _is_statement(q):
    return routing.detect_intent(q) == "fixed_statement" and routing.fixed_statement_topic(q) == TOPIC


@pytest.mark.parametrize("p", _probes(), ids=lambda p: p["id"])
def test_probe_routes_as_authored(p):
    q, want = p["question"], p["expect"]
    if want == "statement":
        assert _is_statement(q), p["guards_against"]
    elif want == "minimum_wage":
        assert routing.detect_intent(q) == "minimum_wage" and not _is_statement(q), p["guards_against"]
    else:
        assert not _is_statement(q) and routing.detect_intent(q) != "minimum_wage", p["guards_against"]


class _B:
    calls = 0

    def generate(self, prompt, params=None):
        _B.calls += 1
        return "x"


def _answer(q):
    return Orchestrator(_B(), retriever=lambda q: ["f"], ooc_phrases=[], in_scope_phrases=[]).answer(q)


@pytest.mark.parametrize("q", [p["question"] for p in _probes() if p["expect"] == "statement"])
def test_the_statement_states_every_rate_of_the_sector_with_zero_model_calls(q):
    _B.calls = 0
    reply = _answer(q)
    t = answer_trace.trace(reply)
    assert t["path"] == "engine:fixed_statement" and t["model_calls"] == 0 and _B.calls == 0, t
    kind, value = ws.resolve(q)
    no = value if kind == ws.SECTOR else value[0]
    for row in ws.BY_SECTOR[no]:
        assert f"{int(ws.rate(row)):,}" in reply.text, (no, row[1])         # every monthly rate of the sector, taken from the transcribed Schedule
    assert "karibu" not in reply.text.lower()                              # never an approximation: the specimen's own word


def test_the_domestic_worker_statement_states_all_four_rates_and_selects_none():
    t = rules_engine.sector_wage_statement("Kima cha chini cha mshahara kwa mfanyakazi wa nyumbani ni kiasi gani?").working
    for n in ("80,000", "160,000", "265,000", "328,000"):
        assert n in t
    assert "usichukue kimoja" in t and "GN 605A" in t and "Kifungu" not in t


def test_a_settled_row_is_stated_first_and_does_not_contradict_itself():
    t = rules_engine.sector_wage_statement("Kima cha chini cha mshahara kwa mfanyakazi wa duka ni kiasi gani?").working
    assert t.startswith("Kwa kazi uliyotaja") and "200,500" in t and "usichukue kimoja" not in t


def test_an_unresolvable_sector_raises_instead_of_guessing():
    with pytest.raises(ValueError):
        rules_engine.sector_wage_statement("Kima cha chini cha mshahara ni kiasi gani?")


def test_the_route_is_never_auto_sent_and_the_guard_loop_skips_it():
    spec = importlib.util.spec_from_file_location("hc_sw_core", os.path.join(_ROOT, "chike-whatsapp", "handler_core.py"))
    core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)
    assert "engine:fixed_statement" in core.AUTOSEND_EXCLUDED_ENGINE_ROUTES
    q = "Kima cha chini cha mshahara kwa mfanyakazi wa nyumbani ni kiasi gani?"
    assert fidelity.fixed_figure_violations(q, "karibu TZS 80,000") == []   # route-only: the guard loop must not fall through to the VAT rule


def test_plant_the_vetoes_removed_lets_the_premise_check_through(monkeypatch):
    # sw_10 carries a how-much ask AND a veto ("sekta ndogo"); the premise check sw_07 has no ask at all, so removing vetoes could never make it fire (a bad plant specimen, R26b)
    monkeypatch.setattr(routing, "_SECTOR_WAGE_VETO", re.compile(r"(?!x)x"))
    assert routing.asks_sector_wage_statement(_q("sw_10")), "with the vetoes removed the count question must wrongly fire; if not, the vetoes are decoration"


def test_plant_the_money_gate_removed_lets_a_figure_question_through(monkeypatch):
    monkeypatch.setattr(routing.swn, "parse_amounts", lambda ql: [])
    assert routing.asks_sector_wage_statement(_q("sw_20"))


def test_plant_the_worker_noun_removed_recreates_the_efd_false_positive(monkeypatch):
    monkeypatch.setattr(routing, "_WAGE_WORKER_NOUN", re.compile(r"(?=)"))
    assert routing.detect_intent(_q("sw_17")) == "minimum_wage"


def test_plant_the_new_pay_cues_removed_loses_the_two_specimens(monkeypatch):
    monkeypatch.setattr(routing, "_WAGE_PAY_CUES", [c for c in routing._WAGE_PAY_CUES if c not in ("anayelipwa", "wanaolipwa")])
    monkeypatch.setattr(routing, "_WAGE_NAMPA", re.compile(r"(?!x)x"))
    for pid in ("sw_15", "sw_16"):
        assert routing.detect_intent(_q(pid)) != "minimum_wage", pid


def test_the_two_figure_bearing_specimens_now_name_the_sector():
    for pid in ("sw_15", "sw_16"):
        q = _q(pid)
        assert ws.resolve(q) == (ws.SECTOR, 4), pid
        reply = _answer(q)
        assert "328,000" in reply.text and "80,000" in reply.text, pid          # all four domestic-work rates, no verdict picked


def test_new_patterns_contain_no_control_characters():
    for r in (routing._SECTOR_WAGE_ASK, routing._SECTOR_WAGE_VETO, routing._WAGE_WORKER_NOUN, routing._WAGE_NAMPA):
        assert not any(ord(c) < 32 and c != "\n" for c in r.pattern)
