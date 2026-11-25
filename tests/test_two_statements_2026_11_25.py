"""2026-11-25 (founder): the two model-free statement routes, MEDICINES are VAT-exempt (vat_medicines) and the PAYE BASE is employment income (paye_base).
Probes both ways (R17, 38 in eval/refusal_gate/two_statements_probes_2026_11_25.jsonl, the founding specimens VERBATIM), the statements pinned to their locked facts and to the D-FIDELITY-32 replacement copy (one string, no drift), end-to-end through the real
orchestrator with ZERO model calls, a PLANT that disables each route and must be caught (R26), pattern hygiene (R39), and the sweep artifact (every held question read)."""
import io
import json
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
from chike import clarification, routing   # noqa: E402
from chike.orchestrator import Orchestrator   # noqa: E402
from chike.rules_engine import fixed_statements as fs   # noqa: E402

_PROBES = os.path.join(_ROOT, "eval", "refusal_gate", "two_statements_probes_2026_11_25.jsonl")
_SDL_Q = "Posho ya nyumba inahesabiwa kwenye SDL, na tofauti yake na PAYE ni ipi?"


def _jl(path):
    with io.open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def _probes():
    rows = _jl(_PROBES)
    assert len(rows) == 38 and sum(r["expect"] in ("vat_medicines", "paye_base") for r in rows) >= 12 and sum(r["expect"] == "none" or r["expect"].startswith("not:") for r in rows) >= 14   # a loader returning nothing must fail (R20)
    return rows


def _verdict(q, expect):
    got = routing.fixed_statement_topic(q)
    if expect == "none":
        return got is None
    if expect.startswith("not:"):
        return got != expect[4:]
    return got == expect


@pytest.mark.parametrize("p", _probes(), ids=lambda p: p["id"])
def test_probe_routes_as_authored(p):
    assert _verdict(p["question"], p["expect"]), (routing.fixed_statement_topic(p["question"]), p["guards_against"])


def _facts():
    with io.open(os.path.join(_ROOT, "scripts", "locked_facts.json"), encoding="utf-8") as fh:
        return json.load(fh)


def test_medicines_statement_is_the_locked_fact_and_the_d32_replacement_copy():
    fact = _facts()["medicines_vat_exempt"]["fact"].split(" (English:")[0]
    st = fs.fixed_statement("vat_medicines").working
    assert st == fact == clarification.CONSTANT_RESTATEMENTS["medicines_zero_rated"]
    assert "Kifungu" not in st and "MSAMAHA wa VAT, si zero-rated" in st and "kwa matumizi ya sehemu hugawanywa kwa fomula" in st      # R44; the founder's approved apportionment clause


def test_paye_statement_is_the_locked_fact_and_the_sdl_limb_only_when_sdl_is_named():
    fact = _facts()["paye_base_employment_income"]["fact"].split(" (English:")[0]
    sdl_sentence = " Tofauti na SDL: kwa SDL faida zisizo za fedha hazijatajwa kwenye Sheria."
    base = fs.fixed_statement("paye_base").working
    assert base == fact.replace(sdl_sentence, "") and "MAPATO YA AJIRA" in base and "Kwa SDL:" not in base and "Kifungu" not in base
    assert "hadai makato wala nafuu" in base                      # the car exclusion carries its CONDITION, quoted from the Act in the fact's verified_by
    both = fs.fixed_statement("paye_base", _SDL_Q).working
    assert both.startswith(base) and "Kwa SDL:" in both and "posho zinaingia kwenye PAYE na kwenye SDL" in both and "Kifungu" not in both
    assert "Kwa SDL:" not in fs.fixed_statement("paye_base", "Bonasi na kamisheni zinaingia kwenye PAYE?").working


class _B:
    calls = 0

    def generate(self, prompt, params=None):
        _B.calls += 1
        return "SHOULD NOT BE CALLED"


def _answer(q):
    _B.calls = 0
    r = Orchestrator(_B(), retriever=lambda x: ["Ukweli."], ooc_phrases=[], in_scope_phrases=[]).answer(q)
    return r


@pytest.mark.parametrize("q,must,must_not", [
    ("Dawa zinatozwa VAT?", "MSAMAHA wa VAT, si zero-rated", "tozo 0%"),
    (_SDL_Q, "MAPATO YA AJIRA", "basic salary"),
    ("PAYE inakokotolewa kwa mshahara wa msingi tu au pamoja na posho?", "si mshahara wa msingi pekee", "SHOULD NOT"),
])
def test_end_to_end_zero_model_calls_and_the_whole_statement(q, must, must_not):
    r = _answer(q)
    assert _B.calls == 0, "a model-free route called the model"
    assert must in r.text and must_not not in r.text, r.text


def test_the_statement_route_is_never_auto_send_eligible():
    """The generic exclusion (engine:fixed_statement) covers both new routes; a route that sends unreviewed after 15 minutes would void the R7 reading (items 2c)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("hc_two_core", os.path.join(_ROOT, "chike-whatsapp", "handler_core.py"))
    handler_core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(handler_core)
    assert "engine:fixed_statement" in handler_core.AUTOSEND_EXCLUDED_ENGINE_ROUTES
    assert "engine:fixed_statement" not in handler_core.AUTOSEND_ELIGIBLE_ENGINE_ROUTES


@pytest.mark.parametrize("topic", ["vat_medicines", "paye_base"])
def test_plant_route_disabled_is_caught(monkeypatch, topic):
    """R26: with the route removed the probes that expect it MUST fail; otherwise the probe test above proves nothing."""
    monkeypatch.setattr(routing, "_FS_TOPICS", tuple(t for t in routing._FS_TOPICS if t[0] != topic))
    failed = [p for p in _probes() if p["expect"] == topic and not _verdict(p["question"], p["expect"])]
    assert len(failed) >= 5, failed


@pytest.mark.parametrize("topic", ["vat_medicines", "paye_base"])
def test_plant_veto_removed_is_caught(monkeypatch, topic):
    """R26, the other direction: with the veto emptied, the 'must not reach this route' probes MUST fail."""
    patched = tuple((n, c, nd, (__import__("re").compile(r"(?!x)x") if n == topic else v)) for n, c, nd, v in routing._FS_TOPICS)
    monkeypatch.setattr(routing, "_FS_TOPICS", patched)
    bad = [p["id"] for p in _probes() if p["expect"] in ("none",) or p["expect"] == "not:" + topic]
    assert any(not _verdict(p["question"], p["expect"]) for p in _probes() if p["id"] in bad), "removing the veto changed no probe: the veto is untested"


def test_new_patterns_contain_no_control_characters():
    """R39: a non-raw \\b is a backspace and matches nothing, invisibly."""
    for n, cue, need, veto in routing._FS_TOPICS:
        if n in ("vat_medicines", "paye_base"):
            for p in (cue, need, veto):
                if p is not None:
                    assert not any(ord(c) < 32 for c in p.pattern), (n, repr(p.pattern))
    for t in ("vat_medicines", "paye_base"):
        assert not any(ord(c) < 32 for c in routing._FS_TOPIC_ASK[t].pattern)


def test_the_sweep_artifact_is_committed_and_clean():
    d = json.load(io.open(os.path.join(_ROOT, "eval", "results", "sweep_two_statements_2026_11_25.json"), encoding="utf-8"))
    assert d["swept"] > 8000 and d["other"] == 0 and d["newly_both"] == [] and d["onto_new"] == len(d["changed"])
    assert d["membership"]["vat_medicines"] >= 10 and d["membership"]["paye_base"] >= 25
