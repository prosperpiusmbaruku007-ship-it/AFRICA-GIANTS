# -*- coding: utf-8 -*-
"""R1 / R2 ROUTE RECALL (founder, 2026-11-26): no-figure "kiasi gani" asks about foreign-employee PAYE and director's-fee WHT reach their statements;
a question WITH an amount is unchanged; a FIRST-PERSON amount ask keeps the salary clarification, which adds ONE line when it also names mgeni / foreign.
Plants (R26): reinstating the veto, and the over-broad first-person veto the first build had, must each FAIL a limb here."""
import re

import pytest

from chike import clarification, routing
from chike.model_abstraction import FakeBackend
from chike.orchestrator import Orchestrator

R1 = "Mfanyakazi mgeni analipa PAYE kiasi gani?"
R2 = "Ada ya mkurugenzi inakatwa kodi ya zuio kiasi gani?"
REGIME_FIRST_PERSON = "Nikikaa nchini siku 183, PAYE yangu ni ya mkazi au asiye mkazi?"       # rs_04: first person, a REGIME question
FIRST_PERSON_AMOUNT = "Mshahara wa mgeni ni mkubwa, nikatwe PAYE kiasi gani mimi?"


def test_R1_and_R2_reach_their_statements():
    assert routing.detect_intent(R1) == "fixed_statement" and routing.fixed_statement_topic(R1) == "paye_residency"
    assert routing.detect_intent(R2) == "fixed_statement" and routing.fixed_statement_topic(R2) == "director_fees_wht"


@pytest.mark.parametrize("q,intent", [
    ("Mfanyakazi mgeni analipwa TZS 2,000,000, PAYE kiasi gani?", "paye"),
    ("Mfanyakazi mgeni analipwa milioni mbili, PAYE kiasi gani?", "paye"),
    ("Ada ya mkurugenzi ni TZS 5,000,000, WHT ni kiasi gani?", "none"),
])
def test_a_question_with_an_amount_is_unchanged(q, intent):
    assert routing.detect_intent(q) == intent and routing.fixed_statement_topic(q) is None


def test_a_first_person_amount_ask_stays_off_the_statement_route_but_a_first_person_regime_question_keeps_it():
    assert routing.fixed_statement_topic(FIRST_PERSON_AMOUNT) is None
    assert routing.fixed_statement_topic(REGIME_FIRST_PERSON) == "paye_residency", "the over-broad first draft removed this (found by the build sweep)"


def _veto_of(name):
    return next(v for n, _, _, v in routing._FS_TOPICS if n == name)


def _with_table(monkeypatch, patch):
    monkeypatch.setattr(routing, "_FS_TOPICS", [(n, c, nd, patch(n, v)) for n, c, nd, v in routing._FS_TOPICS])


def test_PLANT_reinstating_kiasi_gani_in_the_vetoes_loses_both_routes(monkeypatch):
    _with_table(monkeypatch, lambda n, v: re.compile(v.pattern + r"|kiasi\s+gani", v.flags) if n in ("paye_residency", "director_fees_wht") else v)
    assert routing.fixed_statement_topic(R1) is None and routing.fixed_statement_topic(R2) is None


def test_PLANT_a_bare_first_person_veto_removes_the_regime_question(monkeypatch):
    _with_table(monkeypatch, lambda n, v: re.compile(v.pattern + r"|(?<![a-z])yangu(?![a-z])", v.flags) if n == "paye_residency" else v)
    assert routing.fixed_statement_topic(REGIME_FIRST_PERSON) is None, "plant: the broad veto must lose rs_04, or the narrowing test above proves nothing"


def test_the_extra_residency_line_only_for_first_person_foreign_paye_with_no_figure():
    L = clarification.PAYROLL_AMOUNT_RESIDENCY_LINE
    assert clarification.payroll_amount_for(FIRST_PERSON_AMOUNT) == clarification.PAYROLL_AMOUNT + L
    assert clarification.payroll_amount_for("PAYE yangu kama mgeni ni kiasi gani?") == clarification.PAYROLL_AMOUNT + L
    for q in ("Nikatwe PAYE kiasi gani mimi?", R1, "Mgeni PAYE kiasi gani mimi, mshahara 2,000,000?", "", "SDL yangu ni kiasi gani mimi?"):
        assert clarification.payroll_amount_for(q) == clarification.PAYROLL_AMOUNT, q
    assert "UKAAZI WA KIKODI" in L and "si uraia" in L


def test_PAYROLL_AMOUNT_itself_is_unchanged_for_dual_file_parity():
    assert clarification.PAYROLL_AMOUNT.endswith("kisha nitakuletea hesabu kamili.") and clarification.PAYROLL_AMOUNT_RESIDENCY_LINE not in clarification.PAYROLL_AMOUNT


def test_end_to_end_orchestrator_first_person_foreign_gets_the_clarification_plus_line_and_never_the_model():
    fake = FakeBackend(scripted_reply="SHOULD NOT BE CALLED")
    reply = Orchestrator(backend=fake, retriever=lambda q: []).answer(FIRST_PERSON_AMOUNT)
    assert reply.needs_clarification is True and fake.call_count == 0
    assert reply.text == clarification.PAYROLL_AMOUNT + clarification.PAYROLL_AMOUNT_RESIDENCY_LINE


def test_end_to_end_orchestrator_R1_and_R2_are_model_free_statements():
    for q, needle in ((R1, "UKAAZI WA KIKODI"), (R2, "asilimia 15")):
        fake = FakeBackend(scripted_reply="SHOULD NOT BE CALLED")
        reply = Orchestrator(backend=fake, retriever=lambda q: []).answer(q)
        assert fake.call_count == 0 and needle in reply.text, q
