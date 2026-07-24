"""Tests for the applicability-only rules-engine answers (Finding 1).

These are pure, deterministic functions: 'does this levy apply?' answered from headcount
(SDL, the 10-employee threshold) or the flat no-threshold rule (NSSF/WCF), with no salary.
PAYE has no applicability entry (its applicability depends on salary vs the 270k band).
"""
import pytest

from chike import rules_engine


def test_sdl_applies_below_threshold_is_not_applicable():
    r = rules_engine.sdl_applies(employee_count=8)
    assert r.computation == "sdl"
    assert r.applicable is False
    assert r.amount is None
    assert "haihusiki" in r.working
    assert "8" in r.working


def test_sdl_applies_at_threshold_is_applicable_no_amount():
    r = rules_engine.sdl_applies(employee_count=10)
    assert r.applicable is True
    assert r.amount is None                       # applicability answer, not an amount
    assert "Ndiyo" in r.working


def test_nssf_applies_is_always_true_no_threshold():
    r = rules_engine.nssf_applies()
    assert r.computation == "nssf"
    assert r.applicable is True
    assert r.amount is None
    assert "kizingiti" in r.working.lower()       # states there is no headcount threshold


def test_wcf_applies_is_always_true_from_first_employee():
    r = rules_engine.wcf_applies()
    assert r.computation == "wcf"
    assert r.applicable is True
    assert r.amount is None


def test_applicability_dispatcher_routes_by_type():
    assert rules_engine.applicability("sdl", employee_count=12).applicable is True
    assert rules_engine.applicability("nssf").applicable is True
    assert rules_engine.applicability("wcf").applicable is True


def test_applicability_not_supported_for_paye():
    assert rules_engine.supports_applicability("paye") is False
    with pytest.raises(KeyError):
        rules_engine.applicability("paye", monthly_salary=800000)
