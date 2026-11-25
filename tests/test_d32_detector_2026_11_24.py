"""D-FIDELITY-32 DETECTOR (medicines called zero-rated). NOT WIRED: no replacement copy until the founder approves the medicines_vat_exempt text. Planted both ways (R26): specimens flag, controls (negation, contrast clause, export, exempt wording) stay clean."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from chike import fidelity  # noqa: E402

FLAG = ["Dawa nyingi za binadamu ziko katika daraja la zero-rated (tozo 0%).", "Kwa mfano, vifaa tiba (zero-rated) na dawa vinaweza kudai input VAT.", "Medicines are zero-rated in Tanzania."]
CLEAN = ["Dawa si zero-rated; ni msamaha wa VAT.", "Mauzo ya nje ni zero-rated; dawa ni msamaha.", "Dawa zinazouzwa nje ya nchi ni zero-rated.", "Mauzo ya nje yana tozo 0%.", "Dawa zimesamehewa VAT.", "Medicine is exempt, not zero-rated."]


@pytest.mark.parametrize("t", FLAG)
def test_specimen_flags(t):
    assert fidelity.medicines_called_zero_rated("", t)


@pytest.mark.parametrize("t", CLEAN)
def test_control_is_clean(t):
    assert not fidelity.medicines_called_zero_rated("", t)


from chike import clarification  # noqa: E402
from chike.model_abstraction import ModelBackend  # noqa: E402
from chike.orchestrator import Orchestrator  # noqa: E402


class _S(ModelBackend):
    def __init__(self, t):
        self.t = t

    def generate(self, prompt, params=None):
        return self.t


def _ans(q, body):
    return Orchestrator(backend=_S(body), retriever=lambda *a, **k: ["x"], system_prompt="x").answer(q)


def test_wired_specimen_is_replaced_by_the_locked_statement():
    r = _ans("Dawa zinatozwa VAT?", "Dawa nyingi za binadamu ziko katika daraja la zero-rated (tozo 0%).")
    assert "replaced" in [getattr(x, "guard", "") for x in r.sub_answers]
    assert "MSAMAHA wa VAT, si zero-rated" in r.text and "tozo 0%" not in r.text, r.text


def test_replacement_copy_is_the_locked_fact_and_does_not_flag_itself():
    import json
    fact = json.load(open("scripts/locked_facts.json", encoding="utf-8"))["medicines_vat_exempt"]["fact"]
    copy = clarification.CONSTANT_RESTATEMENTS["medicines_zero_rated"]
    assert fact.startswith(copy) and not fidelity.body_contradicts_d16("Dawa zinatozwa VAT?", copy)
    assert "Kifungu" not in copy and "s.74" not in copy          # R44


@pytest.mark.parametrize("body", ["Dawa zinazouzwa nje ya nchi ni zero-rated.", "Dawa si zero-rated; ni msamaha wa VAT.", "Mauzo ya nje ni zero-rated; dawa ni msamaha."])
def test_correct_bodies_pass_through_untouched(body):
    r = _ans("Dawa zinatozwa VAT?", body)
    assert not any(getattr(x, "guard", "") in ("replaced", "repaired") for x in r.sub_answers), r.text


def test_planted_trigger_disabled_lets_the_specimen_through(monkeypatch):
    """R26: with the detector disabled the specimen must reach the user, or the wiring test above proves nothing."""
    monkeypatch.setattr(fidelity, "medicines_called_zero_rated", lambda q, b: [])
    r = _ans("Dawa zinatozwa VAT?", "Dawa nyingi za binadamu ziko katika daraja la zero-rated (tozo 0%).")
    assert "tozo 0%" in r.text
