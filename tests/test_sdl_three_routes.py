"""2026-11-23: the three model-free SDL statement routes (premise-correcting, filing/payment, SDL+NSSF party). R17 probes BOTH ways (18 of 38 must NOT reach them), zero model calls, never auto-sent, mutual exclusion with the other SDL routes
over every probe file held, introspected patterns (R39), content (the form name is NOT asserted), and PLANTS (R26) for the limbs the first corpus sweep forced."""
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

_GATE = os.path.join(_ROOT, "eval", "refusal_gate")
_PROBES = os.path.join(_GATE, "sdl_three_routes_probes_2026_11_23.jsonl")
NEW = ("sdl_employee_premise", "sdl_how_to_file_pay", "sdl_nssf_party")
SDL_TOPICS = ("sdl_payer", "sdl_exemptions") + NEW
EXPECT = {"premise": "sdl_employee_premise", "filing": "sdl_how_to_file_pay", "nssf_party": "sdl_nssf_party", "payer": "sdl_payer", "none": None,
          # 2026-11-23 (ten more statements): three of the none-probes now reach their OWN new routes (see each probe's expect_history); they must still reach none of the three SDL routes above.
          "audit_hedge": "sdl_audit_hedge", "paye_party": "sdl_nssf_paye_party", "nssf_only": "nssf_party", "sdl_base": "sdl_base"}


def _load(path):
    with io.open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def _probes():
    rows = _load(_PROBES)
    assert len(rows) == 38, len(rows)                          # a loader returning nothing must fail, not pass vacuously (R20)
    assert sum(1 for r in rows if r["expect"] == "none") >= 14 and sum(1 for r in rows if r["expect"] in ("premise", "filing", "nssf_party")) >= 19   # 18 -> 14 (n_03 moved to sdl_base on 2026-11-24): three moved to their own routes (expect_history)
    return rows


def _q(pid):
    return [p for p in _probes() if p["id"] == pid][0]["question"]


@pytest.mark.parametrize("p", _probes(), ids=lambda p: p["id"])
def test_probe_routes_as_authored(p):
    assert routing.fixed_statement_topic(p["question"]) == EXPECT[p["expect"]], p["guards_against"]


def test_none_probes_reach_no_new_route_via_the_intent_either():
    for p in _probes():
        if p["expect"] == "none":
            assert routing.fixed_statement_topic(p["question"]) not in NEW, p["id"]


class _B:
    calls = 0

    def generate(self, prompt, params=None):
        _B.calls += 1
        return "x"


def _answer(q):
    return Orchestrator(_B(), retriever=lambda x: ["f"], ooc_phrases=[], in_scope_phrases=[]).answer(q)


@pytest.mark.parametrize("pid,topic", [("pe_01", "sdl_employee_premise"), ("pe_05", "sdl_employee_premise"), ("fp_01", "sdl_how_to_file_pay"), ("fp_02", "sdl_how_to_file_pay"),
                                       ("np_01", "sdl_nssf_party"), ("np_04", "sdl_nssf_party")])
def test_each_route_answers_with_zero_model_calls(pid, topic):
    _B.calls = 0
    reply = _answer(_q(pid))
    t = answer_trace.trace(reply)
    assert t["path"] == "engine:fixed_statement" and t["model_calls"] == 0 and _B.calls == 0, t
    assert fs.fixed_statement(topic).working in reply.text


def test_the_premise_statement_corrects_first_then_states_the_filing():
    t = fs.fixed_statement("sdl_employee_premise").working
    assert t.startswith("SDL hulipwa na MWAJIRI pekee")
    assert t.index("Haikatwi kwenye mshahara wa mfanyakazi") < t.index("IDRAS")
    assert fs.fixed_statement("sdl_how_to_file_pay").working in t


def test_the_filing_statement_asserts_what_the_sources_state_and_does_not_name_a_form():
    t = fs.fixed_statement("sdl_how_to_file_pay").working
    for needle in ("tarehe 7", "IDRAS", "Mkoa wa Kodi", "Kamishna", "tra.go.tz", "havijathibitishwa"):
        assert needle in t, needle
    assert "ITX" not in t and "300.01" not in t, "the live TRA pages name no form: it must not be asserted (R29 mode 3)"
    assert "Kifungu" not in t and "Cap" not in t               # R44


def test_the_nssf_party_statement_states_both_halves():
    t = fs.fixed_statement("sdl_nssf_party").working
    for needle in ("MWAJIRI pekee", "asilimia 20", "asilimia 10 mwajiri na asilimia 10 mfanyakazi", "HUKATWA"):
        assert needle in t, needle
    assert t.index("MWAJIRI pekee") < t.index("NSSF:") and "Kifungu" not in t


def test_every_new_statement_is_registered_route_only_and_excluded_from_auto_send():
    for topic in NEW:
        assert topic in fs.TOPICS and topic in fs.TOPICS_NO_CONCISE_ROW
        assert topic in routing._FS_OWN_ASK_ONLY and topic in routing._FS_LEVY_EXEMPT and topic in routing._FS_TOPIC_ASK
    spec = importlib.util.spec_from_file_location("hc_three_core", os.path.join(_ROOT, "chike-whatsapp", "handler_core.py"))
    core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)
    assert "engine:fixed_statement" in core.AUTOSEND_EXCLUDED_ENGINE_ROUTES


def test_the_guard_loop_skips_the_route_only_topics():
    for pid in ("pe_01", "fp_01", "np_01"):
        assert fidelity.fixed_figure_violations(_q(pid), "Mwajiri analipa SDL. Ni adhabu kwa mwajiri.") == []


def test_the_five_sdl_routes_are_mutually_exclusive_over_every_probe_file_held():
    qs = []
    for name in sorted(os.listdir(_GATE)):
        if name.startswith("sdl_") and name.endswith(".jsonl"):
            qs += [p["question"] for p in _load(os.path.join(_GATE, name))]
    assert len(qs) >= 88, len(qs)
    for q in qs:
        hits = [t for t in routing.fixed_statement_topics(q) if t in SDL_TOPICS]
        assert len(hits) <= 1, (q, hits)


def test_patterns_contain_no_control_characters_and_no_empty_alternative():
    pats = [routing._SDL_FILE_ASK, routing._SDL_PAY_OR_FILE_VERB, routing._SDL_FILE_NEIGHBOURS, routing._SDL_EMPLOYEE_SELF, routing._SDL_PAYER_ASK]
    for n, cue, need, veto in routing._FS_TOPICS:
        if n in SDL_TOPICS:
            pats += [r for r in (cue, need, veto) if r is not None]
    pats += [routing._FS_TOPIC_ASK[t] for t in NEW]
    assert len(pats) >= 20
    for r in pats:
        assert not any(ord(c) < 32 and c != "\n" for c in r.pattern), r.pattern[:60]
        assert "||" not in r.pattern and not r.pattern.startswith("|") and not r.pattern.endswith("|") and "(|" not in r.pattern and "|)" not in r.pattern, (r.pattern[:80], "an empty alternative matches everything")


# ---- PLANTS (R26): each limb removed must wrongly change a probe, or the limb is decoration ----
def _with_topic(monkeypatch, topic, fn):
    new = []
    for n, c, nd, v in routing._FS_TOPICS:
        if n == topic:
            c, nd, v = fn(c, nd, v)
        new.append((n, c, nd, v))
    monkeypatch.setattr(routing, "_FS_TOPICS", tuple(new))


def test_plant_the_pay_or_file_verb_requirement_removed_hijacks_where_the_money_goes(monkeypatch):
    for pid in ("n_01", "n_04"):
        assert routing.fixed_statement_topic(_q(pid)) is None, pid
    _with_topic(monkeypatch, "sdl_how_to_file_pay", lambda c, nd, v: (c, routing._SDL_FILE_ASK, re.compile(r"[0-9]")))
    assert routing.fixed_statement_topic(_q("n_01")) == "sdl_how_to_file_pay" or routing.fixed_statement_topic(_q("n_04")) == "sdl_how_to_file_pay", "the verb limb and the neighbours veto are what keep these off the filing statement"


def test_plant_the_neighbours_veto_removed_hijacks_audit_and_calculation(monkeypatch):
    for pid in ("n_02", "n_03"):
        assert routing.fixed_statement_topic(_q(pid)) not in NEW, pid      # n_02 now reaches sdl_audit_hedge, a different route
    base = "|".join([routing._SDL_PAY_OR_FILE_VERB.pattern, routing._SDL_FILE_ASK.pattern])
    _with_topic(monkeypatch, "sdl_how_to_file_pay", lambda c, nd, v: (c, re.compile(r"(?=.*(?:" + routing._SDL_FILE_ASK.pattern + r"))"), re.compile(r"(?!x)x")))
    assert "sdl_how_to_file_pay" in routing.fixed_statement_topics("Where does SDL money go and what is it used for?"), "without the verb limb and vetoes a where-the-money-goes question reaches the filing statement"
    assert base


def test_plant_the_vetoes_removed_hijack_figure_rate_penalty_household_and_other_levy(monkeypatch):
    ids = ("n_05", "n_06", "n_07", "n_08", "n_09")
    for pid in ids:
        assert routing.fixed_statement_topic(_q(pid)) is None, pid
    _with_topic(monkeypatch, "sdl_how_to_file_pay", lambda c, nd, v: (c, nd, re.compile(r"(?!x)x")))
    assert len([pid for pid in ids if routing.fixed_statement_topic(_q(pid)) == "sdl_how_to_file_pay"]) >= 4


def test_plant_the_nssf_party_vetoes_removed_hijack_the_third_levy_and_the_figure(monkeypatch):
    for pid in ("n_12", "n_13", "n_14", "n_15", "n_19"):
        assert routing.fixed_statement_topic(_q(pid)) not in NEW, pid      # n_14 now reaches sdl_nssf_paye_party, a different route
    _with_topic(monkeypatch, "sdl_nssf_party", lambda c, nd, v: (c, re.compile(r"(?=.*(?<![a-z])nssf(?![a-z]))(?=.*(?:kat|lipa))", re.S), re.compile(r"(?!x)x")))
    got = [pid for pid in ("n_14", "n_15", "n_19") if routing.fixed_statement_topic(_q(pid)) == "sdl_nssf_party"]
    assert len(got) >= 2, got


def test_plant_the_file_veto_removed_from_the_payer_route_makes_two_routes_match(monkeypatch):
    q = "SDL inakatwa kwa mfanyakazi, nalipa wapi?"
    assert routing.fixed_statement_topics(q) == ["sdl_employee_premise"]
    _with_topic(monkeypatch, "sdl_payer", lambda c, nd, v: (c, nd, re.compile(v.pattern.replace(routing._SDL_FILE_ASK.pattern + "|", ""), v.flags)))
    assert "sdl_payer" in routing.fixed_statement_topics("SDL inakatwa benki gani kwa mfanyakazi?"), "without the shared file veto the payer route also claims these (and the routes decline)"
    assert routing.fixed_statement_topic("SDL inakatwa benki gani kwa mfanyakazi?") is None


def test_plant_the_premise_route_removed_loses_the_founding_specimen(monkeypatch):
    monkeypatch.setattr(routing, "_FS_TOPICS", tuple(t for t in routing._FS_TOPICS if t[0] != "sdl_employee_premise"))
    assert routing.fixed_statement_topic(_q("pe_01")) is None


def test_the_multi_levy_fan_out_does_not_split_a_fixed_statement():
    # live, a67462c: "SDL na NSSF zinakatwa kwa mfanyakazi?" was fanned out into an SDL compute and an NSSF compute (the decomposer itself does not split it)
    o = Orchestrator(_B(), retriever=lambda x: ["f"], ooc_phrases=[], in_scope_phrases=[])
    routed = o._fan_out_multi_levy([o.route(_q("np_01"))])
    assert len(routed) == 1 and routed[0].computation_type == "fixed_statement"


def test_plant_the_old_fan_out_splits_the_founding_specimen_and_calls_the_model(monkeypatch):
    import dataclasses

    def old_fan_out(routed):
        out = []
        for sq in routed:
            if sq.kind == "compute":
                levies = routing.all_compute_levies(sq.text)
                if len(levies) >= 2:
                    out.extend(dataclasses.replace(sq, computation_type=lv) for lv in levies)
                    continue
            out.append(sq)
        return out
    monkeypatch.setattr(Orchestrator, "_fan_out_multi_levy", staticmethod(old_fan_out))
    _B.calls = 0
    t = answer_trace.trace(_answer(_q("np_01")))
    assert t["path"] != "engine:fixed_statement", t
