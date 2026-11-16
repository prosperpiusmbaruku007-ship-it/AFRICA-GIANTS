"""R17 regression file for D-FIDELITY-15 (2026-11-17, set #2): WCF described as deducted from the employee's wage (s2_04) and input VAT on a passenger car described as claimable (s2_17). 16 probes in
eval/fidelity/d15_constant_probes_2026_11_17.jsonl (founding specimens VERBATIM from the live run; 4 flag, 12 clean). Wired through the real orchestrator and PLANTED (R26)."""
import json

import pytest

from chike import fidelity
from chike.model_abstraction import ModelBackend
from chike.orchestrator import Orchestrator

PROBES = [json.loads(l) for l in open("eval/fidelity/d15_constant_probes_2026_11_17.jsonl", encoding="utf-8") if l.strip()]


def test_probe_file_has_both_halves():
    assert len(PROBES) == 16 and sum(p["expect"] == "flag" for p in PROBES) == 4 and sum(p["expect"] == "clean" for p in PROBES) == 12


@pytest.mark.parametrize("p", PROBES, ids=[p["id"] for p in PROBES])
def test_probe(p):
    assert bool(fidelity.body_contradicts_d15(p["question"], p["body"])) == (p["expect"] == "flag"), p["guards_against"]


class _S(ModelBackend):
    def __init__(self, t):
        self.t = t

    def generate(self, prompt, params=None):
        return self.t


def _ans(q, body):
    return Orchestrator(backend=_S(body), retriever=lambda *a, **k: ["x"], system_prompt="x").answer(q)


def _spec(i):
    return [p for p in PROBES if p["id"] == i][0]


def _replaced(r):
    return any(getattr(s, "guard", "") == "replaced" for s in r.sub_answers)


def test_wired_wcf_deduction_is_replaced_by_the_locked_statement():
    p = _spec("d15_01")
    r = _ans(p["question"], p["body"])
    assert _replaced(r) and "kuikata" not in r.text and "HAIKATWI" in r.text and "kosa" in r.text, r.text


def test_wired_car_vat_claim_is_replaced_by_the_locked_statement():
    p = _spec("d15_02")
    r = _ans(p["question"], p["body"])
    assert _replaced(r) and "unaweza kudai" not in r.text and "haidaiwi" in r.text and "isipokuwa" in r.text, r.text


@pytest.mark.parametrize("pid", ["d15_05", "d15_10"])
def test_wired_correct_bodies_pass_through(pid):
    p = _spec(pid)
    assert not _replaced(_ans(p["question"], p["body"]))


@pytest.mark.parametrize("pid", ["d15_01", "d15_02"])
def test_planted_trigger_disabled_lets_the_specimen_through(monkeypatch, pid):
    monkeypatch.setattr(fidelity, "body_contradicts_d15", lambda q, b: [])
    p = _spec(pid)
    assert not _replaced(_ans(p["question"], p["body"])), "with the guard disabled the specimen must reach the user, or the wiring tests above prove nothing"
