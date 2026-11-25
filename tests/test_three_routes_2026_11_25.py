"""2026-11-25 (founder, items 2, 4, 5): three more model-free statement routes, the PAYE RATE (paye_rate), the COMBINED health-services + medicines question (vat_health_and_medicines) and the WCF BASE (wcf_base).
Probes both ways (R17, eval/refusal_gate/three_routes_probes_2026_11_25.jsonl, the founding specimens VERBATIM from the live replies of build ff68073), statements pinned to the locked facts / the existing statements (one string, no drift), end to end with ZERO model calls,
PLANTS (R26), pattern hygiene (R39) and the sweep artifact (every held question read; four wrong-topic classes found by it are probes now)."""
import importlib.util
import io
import json
import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
from chike import routing   # noqa: E402
from chike.orchestrator import Orchestrator   # noqa: E402
from chike.rules_engine import fixed_statements as fs   # noqa: E402

_PROBES = os.path.join(_ROOT, "eval", "refusal_gate", "three_routes_probes_2026_11_25.jsonl")
NEW = ("paye_rate", "vat_health_and_medicines", "wcf_base")


def _probes():
    with io.open(_PROBES, encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh if line.strip()]
    assert len(rows) == 42 and sum(r["expect"] in NEW for r in rows) >= 14 and sum(r["expect"] == "none" or r["expect"].startswith("not:") for r in rows) >= 15   # a loader returning nothing must fail (R20)
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


def test_paye_rate_statement_is_the_generated_band_table_and_says_there_is_no_single_rate():
    t = fs.fixed_statement("paye_rate").working
    assert t.startswith("PAYE HAINA kiwango kimoja") and fs._paye_bands_text() in t and "Asiye mkazi analipa 15%" in t and "Kifungu" not in t
    assert "asilimia 30" not in t.split("HAINA kiwango kimoja")[0]            # the live reply's opening claim must not be this statement's opening


def test_combined_statement_is_the_two_single_limb_statements_unchanged_and_in_order():
    a, b = fs.fixed_statement("vat_medical_services").working, fs.fixed_statement("vat_medicines").working
    both = fs.fixed_statement("vat_health_and_medicines").working
    assert both == a + "\n\n" + b and both.index("YOTE MAWILI") < both.index("MSAMAHA wa VAT, si zero-rated")


def test_wcf_base_statement_quotes_the_facts_own_wording_on_fixed_allowances():
    fact = _facts()["wcf_contribution_base"]["fact"].split(" (English:")[0]
    t = fs.fixed_statement("wcf_base").working
    assert t == fact and "ZISIZOBADILIKA zinazolipwa kila mwezi pamoja na mshahara" in t and "haruhusiwi kukata mchango huu" in t and "Kifungu" not in t
    assert not re.search(r"(?i)gross\s+cash|cash\s+emoluments", t)


class _B:
    calls = 0

    def generate(self, prompt, params=None):
        _B.calls += 1
        return "SHOULD NOT BE CALLED"


def _answer(q):
    _B.calls = 0
    return Orchestrator(_B(), retriever=lambda x: ["Ukweli."], ooc_phrases=[], in_scope_phrases=[]).answer(q)


@pytest.mark.parametrize("q,must,must_not", [
    ("PAYE ni asilimia ngapi?", "PAYE HAINA kiwango kimoja", "asilimia 30, lakini"),
    ("Huduma za afya zinatozwa VAT? Na dawa je?", "YOTE MAWILI", "SHOULD NOT"),
    ("WCF inakatwa kwenye nini, mshahara wa msingi tu au pamoja na posho?", "ZISIZOBADILIKA", "SHOULD NOT"),
])
def test_end_to_end_zero_model_calls_and_the_whole_statement(q, must, must_not):
    r = _answer(q)
    assert _B.calls == 0, "a model-free route called the model"
    assert must in r.text and must_not not in r.text, r.text
    if "afya" in q:
        assert "MSAMAHA wa VAT, si zero-rated" in r.text, "BOTH limbs must be in the one reply (the live reply answered the medicines limb only)"


def test_the_routes_are_never_auto_send_eligible():
    spec = importlib.util.spec_from_file_location("hc_three_core", os.path.join(_ROOT, "chike-whatsapp", "handler_core.py"))
    hc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hc)
    assert "engine:fixed_statement" in hc.AUTOSEND_EXCLUDED_ENGINE_ROUTES and "engine:fixed_statement" not in hc.AUTOSEND_ELIGIBLE_ENGINE_ROUTES


@pytest.mark.parametrize("topic", NEW)
def test_plant_route_disabled_is_caught(monkeypatch, topic):
    """R26: with the route removed the probes that expect it MUST fail."""
    monkeypatch.setattr(routing, "_FS_TOPICS", tuple(t for t in routing._FS_TOPICS if t[0] != topic))
    failed = [p for p in _probes() if p["expect"] == topic and not _verdict(p["question"], p["expect"])]
    assert len(failed) >= 3, failed


def test_plant_paye_rate_veto_removed_is_caught(monkeypatch):
    """R26, the other direction: with the PAYE-rate veto emptied, the Kenya / foreign / arithmetic-trap / figure probes MUST fail (they are what the veto exists for)."""
    patched = tuple((n, c, nd, (re.compile(r"(?!x)x") if n == "paye_rate" else v)) for n, c, nd, v in routing._FS_TOPICS)
    monkeypatch.setattr(routing, "_FS_TOPICS", patched)
    failed = {p["id"] for p in _probes() if not _verdict(p["question"], p["expect"])}
    assert {"pr_15", "pr_16", "pr_17"} <= failed, failed


def test_exclusivity_each_single_limb_route_still_owns_its_own_question():
    assert routing.fixed_statement_topic("Huduma za afya zinatozwa VAT?") == "vat_medical_services"
    assert routing.fixed_statement_topic("Dawa zinatozwa VAT?") == "vat_medicines"
    assert routing.fixed_statement_topic("Bendi za PAYE ni zipi?") == "paye_band_table"
    assert routing.fixed_statement_topic("PAYE inakokotolewa kwa mshahara wa msingi tu?") == "paye_base"


def test_new_patterns_contain_no_control_characters():
    """R39: a non-raw escape compiles to a backspace and matches nothing, invisibly."""
    for n, cue, need, veto in routing._FS_TOPICS:
        if n in NEW:
            for p in (cue, need, veto):
                if p is not None:
                    assert not any(ord(c) < 32 for c in p.pattern), (n, repr(p.pattern))
    for t in NEW:
        assert not any(ord(c) < 32 for c in routing._FS_TOPIC_ASK[t].pattern)


def test_the_sweep_artifact_is_committed_and_clean():
    d = json.load(io.open(os.path.join(_ROOT, "eval", "results", "sweep_three_routes_2026_11_25.json"), encoding="utf-8"))
    assert d["swept"] > 8000 and d["other"] == 0 and d["newly_both"] == [] and d["onto_new"] == len(d["changed"])
    assert d["membership"]["paye_rate"] >= 10 and d["membership"]["vat_health_and_medicines"] >= 5 and d["membership"]["wcf_base"] >= 4
