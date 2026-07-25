"""Tests for compute_paye residency selection (D-PAYE-1).

A non-resident employee pays a flat 15% final withholding, NOT the resident progressive
bands. The engine already supported resident=False; the orchestrator never set it, so every
PAYE compute got progressive bands (eval_367: a non-resident on TZS 5,000,000 was billed the
1,328,000 progressive figure instead of the flat 750,000). Pure, deterministic — no model.
resident=True (the default) must stay byte-identical to the pre-fix output.
"""
from decimal import Decimal

from chike import rules_engine
from chike.rules_engine.paye import compute_paye


def test_nonresident_is_flat_fifteen_percent():
    r = compute_paye(Decimal("5000000"), resident=False)
    assert r.amount == Decimal("750000")           # 15% of 5,000,000, eval_367 gold
    assert "15%" in r.working
    assert "asiye mkazi" in r.working
    assert "si mabano" in r.working                # explicitly NOT the progressive bands


def test_resident_default_uses_progressive_bands():
    # Same salary, resident: the top-band progressive figure, unchanged.
    r = compute_paye(Decimal("5000000"))           # default resident=True
    assert r.amount == Decimal("1328000")          # 128,000 + 30% × (5,000,000 − 1,000,000)
    assert "asiye mkazi" not in r.working


def test_resident_working_is_byte_identical_to_pre_fix_string():
    # The pre-fix `working` for a resident salary was exactly this. Resident-framed questions
    # must be completely unchanged by D-PAYE-1 (uses U+2212 minus, as the engine does).
    r = compute_paye(Decimal("800000"))
    assert r.working == "PAYE = TZS 68,000 + 25% × (TZS 800,000 − TZS 760,000) = TZS 78,000"


def test_resident_recorded_in_inputs():
    assert compute_paye(Decimal("800000"), resident=False).inputs["resident"] is False
    assert compute_paye(Decimal("800000")).inputs["resident"] is True


def test_dispatch_through_compute_passes_resident():
    # The orchestrator calls rules_engine.compute('paye', monthly_salary=..., resident=...).
    r = rules_engine.compute("paye", monthly_salary=Decimal("5000000"), resident=False)
    assert r.amount == Decimal("750000")           # eval_367 end-to-end via the dispatch
