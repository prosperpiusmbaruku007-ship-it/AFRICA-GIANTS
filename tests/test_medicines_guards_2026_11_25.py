"""2026-11-25 (founder): D-FIDELITY-32b (the negation governs only the zero-rated token it is ADJACENT to) and D-FIDELITY-33 (medicines taxed at the standard rate, or a VAT amount computed on a medicines amount) -> replaced by the approved medicines statement.
Planted BOTH ways (R26): the live specimens MUST flag and each control MUST pass, the replacement happens through the real orchestrator, and disabling a detector lets the specimen through."""
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
from chike import clarification, fidelity, routing   # noqa: E402
from chike.model_abstraction import ModelBackend      # noqa: E402
from chike.orchestrator import Orchestrator           # noqa: E402

Q_LIVE = "Dawa za TZS 5,000,000 nimeuza, VAT ni ngapi?"
Q_PHARM = "Duka la dawa linatakiwa kusajili VAT, na dawa zinatozwa VAT gani?"
LIVE_MISS = "Duka la dawa lenye mauzo ya TZS 200M/miezi 12 au TZS 100M/miezi 6 linasajili VAT. Dawa zinaweza kuwa zero-rated (msamaha wa VAT) au exempt (si zero-rated). Thibitisha na TRA (tra.go.tz)."
LIVE_18 = "Kwa dawa zenye thamani ya TZS 5,000,000, kiwango cha VAT ni 18%. Thibitisha na tra.go.tz."


@pytest.mark.parametrize("q,body,topic", [
    (Q_PHARM, LIVE_MISS, "medicines_zero_rated"),                                  # the live miss: a negated AND an asserted zero-rated in ONE clause
    ("x", "Dawa nyingi za binadamu ziko katika daraja la zero-rated (tozo 0%).", "medicines_zero_rated"),
    (Q_LIVE, LIVE_18, "medicines_taxed"),
    (Q_LIVE, "VAT itakuwa TZS 900,000.", "medicines_taxed"),
    ("Dawa zinatozwa VAT?", "Dawa zinatozwa VAT ya asilimia 18.", "medicines_taxed"),
])
def test_live_specimens_flag(q, body, topic):
    assert topic in [t for t, _ in fidelity.body_contradicts_d16(q, body)], body


@pytest.mark.parametrize("q,body", [
    ("x", "Dawa si zero-rated; ni msamaha wa VAT."), ("x", "Dawa si za zero-rated."), ("x", "Medicine is exempt, not zero-rated."), ("x", "Dawa hazitozwi 0% bali ni msamaha."),
    ("x", "Mauzo ya nje ni zero-rated; dawa ni msamaha."), ("x", "Dawa zinazouzwa nje ya nchi ni zero-rated."),
    (Q_LIVE, "Dawa ni msamaha wa VAT, hakuna VAT inayotozwa."), (Q_LIVE, "VAT ya kawaida ni 18%, lakini dawa ni msamaha."), (Q_LIVE, "Dawa si 18%; ni msamaha."),
    ("VAT ni asilimia ngapi kwa bidhaa za kawaida?", "Kiwango cha kawaida cha VAT ni 18%."), ("Biashara ya nguo, VAT ni ngapi?", "VAT ni 18% ya TZS 1,000,000 = TZS 180,000."),
    ("x", "Mauzo ya dawa nje ya nchi: VAT ni 18%?"),
    (Q_PHARM, "Duka la dawa lenye mauzo ya TZS 200M/miezi 12 au TZS 100M/miezi 6 linasajili VAT."),      # a registration THRESHOLD is not a VAT amount (found by the plant test)
])
def test_controls_are_clean(q, body):
    assert not fidelity.body_contradicts_d16(q, body), body


def test_the_replacement_is_one_string_and_never_flags_itself():
    a, b = clarification.CONSTANT_RESTATEMENTS["medicines_zero_rated"], clarification.CONSTANT_RESTATEMENTS["medicines_taxed"]
    assert a is b or a == b
    for q in (Q_LIVE, Q_PHARM, "Dawa zinatozwa VAT?"):
        assert not fidelity.body_contradicts_d16(q, a)


class _S(ModelBackend):
    def __init__(self, t):
        self.t = t

    def generate(self, prompt, params=None):
        return self.t


def _ans(q, body):
    return Orchestrator(backend=_S(body), retriever=lambda *a, **k: ["x"], system_prompt="x").answer(q)


@pytest.mark.parametrize("q,body", [(Q_PHARM, LIVE_MISS), (Q_LIVE, LIVE_18)])
def test_end_to_end_the_specimen_is_replaced_by_the_medicines_statement(q, body):
    assert routing.fixed_statement_topic(q) is None, "the question must reach the model for the guard to be the layer under test"
    r = _ans(q, body)
    assert "replaced" in [getattr(x, "guard", "") for x in r.sub_answers]
    assert "MSAMAHA wa VAT, si zero-rated" in r.text and "18%" not in r.text and "(si zero-rated)" not in r.text.split("MSAMAHA wa VAT, si zero-rated")[0], r.text


@pytest.mark.parametrize("attr,q,body", [("medicines_called_zero_rated", Q_PHARM, LIVE_MISS), ("medicines_taxed_at_standard_rate", Q_LIVE, LIVE_18)])
def test_planted_detector_disabled_lets_the_specimen_through(monkeypatch, attr, q, body):
    """R26: with the detector disabled the specimen must reach the user, or the end-to-end test above proves nothing."""
    monkeypatch.setattr(fidelity, attr, lambda *a, **k: [])
    r = _ans(q, body)
    assert "linasajili VAT" in r.text or "18%" in r.text, r.text


def test_the_old_negation_rule_would_have_missed_the_live_reply():
    """The founding fact of 32b: a clause-wide negation veto lets the live miss through. Pinned so a later 'simplification' back to the clause-wide rule fails here."""
    import re
    clause = "Dawa zinaweza kuwa zero-rated (msamaha wa VAT) au exempt (si zero-rated)."
    assert re.search(r"(?<![a-z])(?:si|siyo|sio|haziko|haiko|hazina|haina|hakuna|not|no|never|isipokuwa)(?![a-z])", clause), "the old whole-clause cue matches this sentence (so it vetoed it)"
    assert fidelity.medicines_called_zero_rated("", clause)


def test_new_patterns_contain_no_control_characters():
    for n in ("_D32_NEG_ADJ", "_D32_CLAUSE_VETO", "_D33_STD", "_D33_VAT_AMOUNT", "_D33_SAFE", "_D33_VAT"):
        assert not any(ord(c) < 32 for c in getattr(fidelity, n).pattern), n


def test_two_topics_carrying_one_string_print_it_once():
    """FOUND LIVE 2026-11-25 (build c50345c, 'Dawa zinazoingizwa kutoka China zinatozwa VAT?'): D-FIDELITY-32 and D-FIDELITY-33 both fired, and the replacement printed the medicines statement TWICE."""
    both = clarification.constants_restated(["medicines_zero_rated", "medicines_taxed"])
    one = clarification.CONSTANT_RESTATEMENTS["medicines_zero_rated"]
    assert both == one and both.count("MSAMAHA wa VAT, si zero-rated") == 1
    body = "Dawa zinaweza kuwa zero-rated (msamaha wa VAT) au exempt (si zero-rated). VAT ni asilimia 18."
    q = "Dawa zinazoingizwa kutoka China zinatozwa VAT?"
    assert {t for t, _ in fidelity.body_contradicts_d16(q, body)} == {"medicines_zero_rated", "medicines_taxed"}, "the specimen must trigger BOTH guards"
    assert _ans(q, body).text.count("MSAMAHA wa VAT, si zero-rated") == 1
