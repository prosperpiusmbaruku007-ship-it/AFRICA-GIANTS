"""Tests for compute_nssf party selection (D-NSSF-1).

The engine used to always return the 20% TOTAL as the headline `amount`, so a question asking
for the EMPLOYEE's (or EMPLOYER's) 10% share got double the correct figure. `party` now selects
the headline. Pure, deterministic — no model. `party='total'` must stay byte-identical to the
pre-fix output so total-framed questions are unchanged.
"""
from decimal import Decimal

from chike import rules_engine
from chike.rules_engine.nssf import compute_nssf


def test_employee_party_returns_ten_percent_half():
    r = compute_nssf(Decimal("800000"), party="employee")
    assert r.amount == Decimal("80000")            # 10% of 800,000, NOT the 160,000 total
    assert "80,000" in r.working
    assert "sehemu ya mfanyakazi" in r.working
    assert "jumla ya NSSF ni 20%" in r.working     # full breakdown kept for transparency


def test_employer_party_returns_ten_percent_half():
    r = compute_nssf(Decimal("1200000"), party="employer")
    assert r.amount == Decimal("120000")           # 10% of 1,200,000, NOT 240,000
    assert "120,000" in r.working
    assert "sehemu ya mwajiri" in r.working


def test_total_party_returns_twenty_percent():
    r = compute_nssf(Decimal("800000"), party="total")
    assert r.amount == Decimal("160000")           # 20% of 800,000


def test_default_party_is_total():
    # Unchanged default: no party arg == total, so any existing caller is unaffected.
    assert compute_nssf(Decimal("500000")).amount == Decimal("100000")


def test_total_working_is_byte_identical_to_pre_fix_string():
    # The pre-fix `working` was exactly this string. Total-framed questions must be unchanged.
    r = compute_nssf(Decimal("800000"), party="total")
    assert r.working == "NSSF = 20% × TZS 800,000 = TZS 160,000 (mwajiri TZS 80,000 + mfanyakazi TZS 80,000)"


def test_party_recorded_in_inputs_and_note():
    r = compute_nssf(Decimal("640000"), party="employee")
    assert r.inputs["party"] == "employee"
    assert r.note == "party=employee"


def test_dispatch_through_compute_passes_party():
    # The orchestrator calls rules_engine.compute('nssf', gross_monthly_payroll=..., party=...).
    r = rules_engine.compute("nssf", gross_monthly_payroll=Decimal("450000"), party="employee")
    assert r.amount == Decimal("45000")            # eval_330: 10% of 450,000
