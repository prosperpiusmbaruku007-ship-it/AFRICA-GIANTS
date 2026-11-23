"""2026-11-23: the model-free SDL-PAYER statement route (who pays SDL / is it deducted from the employee). R17 probes BOTH ways (14 of 21 are vetoed or belong to another route: the arm that does the work), zero model calls,
never auto-sent, mutual exclusion with the exemptions route, PLANTS (R26) for each limb including the NARROWING that the first corpus sweep forced."""
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

_PROBES = os.path.join(_ROOT, "eval", "refusal_gate", "sdl_payer_probes_2026_11_23.jsonl")
_EX_PROBES = os.path.join(_ROOT, "eval", "refusal_gate", "sdl_exemptions_probes_2026_11_23.jsonl")
TOPIC = "sdl_payer"


def _load(path):
    with io.open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def _probes():
    rows = _load(_PROBES)
    assert len(rows) == 21, len(rows)                          # a loader returning nothing must fail, not pass vacuously (R20)
    assert sum(1 for r in rows if r["expect"] == "payer") >= 7 and sum(1 for r in rows if r["expect"] == "not_payer") >= 10
    return rows


def _q(pid):
    return [p for p in _probes() if p["id"] == pid][0]["question"]


def _is_payer(q):
    return routing.detect_intent(q) == "fixed_statement" and routing.fixed_statement_topic(q) == TOPIC


def _with_topic_patterns(monkeypatch, fn):
    new = []
    for n, c, nd, v in routing._FS_TOPICS:
        if n == TOPIC:
            c, nd, v = fn(c, nd, v)
        new.append((n, c, nd, v))
    monkeypatch.setattr(routing, "_FS_TOPICS", tuple(new))


@pytest.mark.parametrize("p", _probes(), ids=lambda p: p["id"])
def test_probe_routes_as_authored(p):
    assert _is_payer(p["question"]) == (p["expect"] == "payer"), p["guards_against"]


def test_the_statement_says_employer_only_not_deducted_and_not_a_penalty():
    t = fs.fixed_statement(TOPIC).working
    for needle in ("MWAJIRI pekee", "si adhabu", "Haikatwi kwenye mshahara wa mfanyakazi", "tra.go.tz"):
        assert needle in t, needle
    assert "Kifungu" not in t and "Cap" not in t               # R44
    assert not re.search(r"\d", t)                             # no figure: rate / threshold asks are vetoed off this route
    assert TOPIC in fs.TOPICS and TOPIC in fs.TOPICS_NO_CONCISE_ROW


def test_the_statement_is_the_locked_fact_sdl_payer():
    facts = json.load(open(os.path.join(_ROOT, "scripts", "locked_facts.json"), encoding="utf-8"))
    facts = facts.get("facts", facts)
    f = facts[fs.STATEMENTS[TOPIC][0]]
    assert f["status"] == "CONFIRMED" and "BY THE EMPLOYER" in f["primary_source"] and "NOT deducted" in f["fact"]


class _B:
    calls = 0

    def generate(self, prompt, params=None):
        _B.calls += 1
        return "x"


def _answer(q):
    return Orchestrator(_B(), retriever=lambda x: ["f"], ooc_phrases=[], in_scope_phrases=[]).answer(q)


@pytest.mark.parametrize("pid", ["pp_01", "pp_02", "pp_03", "pp_04", "pp_05", "pp_06", "pp_07"])
def test_the_statement_answers_with_zero_model_calls(pid):
    _B.calls = 0
    reply = _answer(_q(pid))
    t = answer_trace.trace(reply)
    assert t["path"] == "engine:fixed_statement" and t["model_calls"] == 0 and _B.calls == 0, t
    assert fs.fixed_statement(TOPIC).working in reply.text


def test_it_is_never_auto_sent():
    spec = importlib.util.spec_from_file_location("hc_pp_core", os.path.join(_ROOT, "chike-whatsapp", "handler_core.py"))
    core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)
    assert "engine:fixed_statement" in core.AUTOSEND_EXCLUDED_ENGINE_ROUTES


def test_the_guard_loop_skips_the_route_only_topic():
    assert fidelity.fixed_figure_violations(_q("pp_01"), "Mwajiri analipa SDL. Ni adhabu kwa mwajiri.") == []


def test_the_two_sdl_statement_routes_are_mutually_exclusive_over_every_probe_held():
    qs = [p["question"] for p in _probes()] + [p["question"] for p in _load(_EX_PROBES)]
    assert len(qs) == 50
    for q in qs:
        hits = [t for t in routing.fixed_statement_topics(q) if t in ("sdl_payer", "sdl_exemptions")]
        assert len(hits) <= 1, (q, hits)


def test_the_exemptions_probe_that_asks_who_pays_now_reaches_the_payer_statement():
    # se_23 was the exemptions route's veto specimen ('not_statement'); it is now the payer route's founding specimen
    q = [p for p in _load(_EX_PROBES) if p["id"] == "se_23"][0]["question"]
    assert _is_payer(q) and routing.fixed_statement_topic(q) != "sdl_exemptions"


def test_patterns_contain_no_control_characters_and_no_empty_alternative():
    for n, cue, need, veto in routing._FS_TOPICS:
        if n in (TOPIC, "sdl_exemptions"):
            for r in (cue, need, veto):
                assert not any(ord(c) < 32 and c != "\n" for c in r.pattern)
                assert "||" not in r.pattern and not r.pattern.startswith("|") and not r.pattern.endswith("|"), (n, "an empty alternative matches everything")
    for r in (routing._SDL_PAYER_ASK, routing._FS_TOPIC_ASK[TOPIC]):
        assert not any(ord(c) < 32 for c in r.pattern) and "||" not in r.pattern


# ---- PLANTS (R26): each limb removed must wrongly change a probe, or the limb is decoration ----
def test_plant_the_cue_removed_loses_the_specimen(monkeypatch):
    monkeypatch.setattr(routing, "_FS_TOPICS", tuple(t for t in routing._FS_TOPICS if t[0] != TOPIC))
    assert not _is_payer(_q("pp_01"))


def test_plant_the_vetoes_removed_hijack_digit_household_deadline_and_other_levy(monkeypatch):
    for pid in ("pp_09", "pp_10", "pp_12", "pp_13", "pp_15", "pp_20"):
        assert not _is_payer(_q(pid)), pid
    _with_topic_patterns(monkeypatch, lambda c, nd, v: (c, nd, re.compile(r"(?!x)x")))
    hijacked = [pid for pid in ("pp_09", "pp_10", "pp_12", "pp_13", "pp_15", "pp_20") if TOPIC in routing.fixed_statement_topics(_q(pid))]   # membership: with every veto removed a neighbouring route can ALSO match, and the route then declines
    assert len(hijacked) >= 5, hijacked


def test_plant_the_narrow_payer_ask_replaced_by_the_loose_first_draft_hijacks_the_compute_and_disability_questions(monkeypatch):
    for pid in ("pp_16", "pp_17"):
        assert not _is_payer(_q(pid)), pid
    loose = re.compile(r"(?=.*(?:(?<![a-z])mfanyakazi|(?<![a-z])mshahara))", re.S)
    _with_topic_patterns(monkeypatch, lambda c, nd, v: (c, loose, v))
    # 2026-11-24: pp_17 (an allowance question) now ALSO matches sdl_base, so the topic LIST (not the single resolved topic) is what shows the plant works
    assert TOPIC in routing.fixed_statement_topics(_q("pp_16")) and TOPIC in routing.fixed_statement_topics(_q("pp_17")), "the narrowing is what keeps these off the statement; if not, it is decoration"


def test_plant_the_compute_stem_veto_removed_hijacks_the_two_part_question(monkeypatch):
    assert not _is_payer(_q("pp_08"))
    _with_topic_patterns(monkeypatch, lambda c, nd, v: (c, nd, re.compile(v.pattern.replace("hesab|kokot|", ""), v.flags)))
    assert routing.fixed_statement_topic(_q("pp_08")) == TOPIC, "without the 'hesab' stem veto the two-part question reaches the statement and its compute half is dropped"


def test_plant_the_shared_payer_veto_removed_from_the_exemptions_route_makes_both_match(monkeypatch):
    q = "Nani analipa SDL, mwajiri?"      # pp_01 also carries the exemptions route's older 'mfanyakazi' veto, so it cannot isolate the shared one; this question is stopped on the exemptions side ONLY by the shared payer cue
    assert routing.fixed_statement_topics(q) == [TOPIC]
    new = []
    for n, c, nd, v in routing._FS_TOPICS:
        if n == "sdl_exemptions":
            v = re.compile(v.pattern.replace(routing._SDL_PAYER_ASK.pattern + "|", ""), v.flags)
        new.append((n, c, nd, v))
    monkeypatch.setattr(routing, "_FS_TOPICS", tuple(new))
    assert sorted(routing.fixed_statement_topics(q)) == sorted(["sdl_exemptions", TOPIC]), "without the exemptions-side veto both routes match (which declines): the veto is what keeps them exclusive"
    assert routing.fixed_statement_topic(q) is None
