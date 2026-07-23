"""Tests for chike.clarification — reason-aware never-guess clarification copy.

These pin that the copy is real, actionable Swahili (never the bare '<CLARIFICATION_NEEDED>'
sentinel) and that it adapts to the specific blocker the extractor reported.
"""
from chike import clarification
from chike.orchestrator import CLARIFICATION_PENDING


def test_constants_are_real_swahili_not_the_sentinel():
    for txt in (clarification.PAYROLL_AMOUNT, clarification.AMBIGUOUS_LEVY):
        assert txt.strip()
        assert CLARIFICATION_PENDING not in txt
        assert "mshahara" in txt.lower()


def test_payroll_amount_matches_production_constant_text():
    # Dual-file parity: chike.clarification.PAYROLL_AMOUNT must equal modal_app's
    # PAYROLL_CLARIFICATION verbatim (both fire on is_uncomputable_payroll_amount).
    expected = (
        "Ili nikuhesabie makato ya mshahara (kama PAYE, NSSF, SDL) kwa usahihi, nahitaji "
        "kiasi cha mshahara au jumla ya mishahara kwa mwezi. Tafadhali niambie mshahara ni "
        "shilingi ngapi, kisha nitakuletea hesabu kamili."
    )
    assert clarification.PAYROLL_AMOUNT == expected


def test_foreign_currency_reason_asks_for_tzs_conversion():
    copy = clarification.compute_clarification(
        "paye", ["monthly_salary: low (amount in foreign currency (not TZS) — needs conversion)"])
    assert "TZS" in copy or "shilingi za Tanzania" in copy
    assert "PAYE" in copy


def test_gross_net_reason_asks_gross_or_net():
    copy = clarification.compute_clarification(
        "paye", ["monthly_salary: low (allowance/gross-net/VAT base ambiguous)"])
    assert "ghafi" in copy.lower() or "mkononi" in copy.lower()


def test_period_reason_asks_for_monthly_or_days():
    copy = clarification.compute_clarification(
        "nssf", ["gross_monthly_payroll: low (period=week needs days/weeks worked)"])
    assert "mwezi" in copy.lower()


def test_missing_employee_count_only_asks_for_headcount():
    copy = clarification.compute_clarification("sdl", ["employee_count: missing"])
    assert "wafanyakazi" in copy.lower()
    assert "SDL" in copy


def test_both_missing_asks_for_payroll_and_count():
    copy = clarification.compute_clarification(
        "sdl", ["gross_monthly_payroll: missing", "employee_count: missing"])
    assert "mishahara" in copy.lower() and "wafanyakazi" in copy.lower()


def test_vague_amount_falls_back_to_generic_salary_ask():
    # An unrecognised blocker -> the generic PAYROLL_AMOUNT (still names the salary need).
    copy = clarification.compute_clarification("paye", ["monthly_salary: low (model)"])
    assert copy == clarification.PAYROLL_AMOUNT


def test_ambiguous_levy_lists_the_four_levies():
    for levy in ("PAYE", "NSSF", "SDL", "WCF"):
        assert levy in clarification.AMBIGUOUS_LEVY
