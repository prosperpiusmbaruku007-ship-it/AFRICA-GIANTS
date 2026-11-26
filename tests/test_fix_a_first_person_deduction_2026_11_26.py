# -*- coding: utf-8 -*-
"""FIX A (founder-approved, 2026-11-26): a FIRST-PERSON, figure-free ask for one's own PAYE gets the salary clarification instead of reaching the model, which invented
"TZS 800,000 -> 78,000" (live, 066a995). `PAYE` counts on its own; the generic `kodi` counts ONLY with a deduction verb. The must-not-change half does the work (R17).
Plants (R26): dropping each of the three conjuncts must flip a must-not-change probe, or the matching test proves nothing."""
import re

import pytest

from chike import clarification, routing
from chike.model_abstraction import FakeBackend
from chike.orchestrator import Orchestrator

MUST_CLARIFY = [
    "Nikatwe PAYE kiasi gani mimi?",
    "Nikatwe PAYE kiasi gani?",
    "PAYE yangu ni kiasi gani?",
    "Ninakatwa kodi kiasi gani mimi?",
]
SHOP_OWNER_KODI = "Nilipe kodi kiasi gani mimi?"                                   # FOUNDER MUST-NOT: kodi, no deduction verb
RS_04 = "Nikikaa nchini siku 183, PAYE yangu ni ya mkazi au asiye mkazi?"          # first person, PAYE, a REGIME question: no money ask (and a digit: two limbs protect it)
REGIME_NO_DIGIT = "Nikikaa nchini muda mrefu, PAYE yangu ni ya mkazi au asiye mkazi?"   # the same question with NO digit, so ONLY the money-ask limb protects it
GENERIC_PAYE = "PAYE ni kiasi gani?"                                               # money ask, PAYE, NOT first person
MUST_NOT = [
    SHOP_OWNER_KODI, REGIME_NO_DIGIT, "Nilipe kodi ya duka kiasi gani?", "Ninalipa kodi ya pango kiasi gani?", "Nilipe VAT kiasi gani mimi?", RS_04,
    "PAYE yangu ni asilimia ngapi?", "Nikichelewa kulipa PAYE yangu nitatozwa faini kiasi gani?", "Nikatwe PAYE kiasi gani mimi, mshahara 800,000?",
    "Mfanyakazi mgeni analipa PAYE kiasi gani?", "PAYE inakatwa lini?", GENERIC_PAYE,
]


@pytest.mark.parametrize("q", MUST_CLARIFY)
def test_first_person_no_figure_paye_is_uncomputable(q):
    assert routing.detect_intent(q) == "none" and routing.is_uncomputable_payroll_amount(q), q


@pytest.mark.parametrize("q", MUST_NOT)
def test_must_not_change_probes_are_not_clarified(q):
    # the WHOLE predicate: the penalty / no-employees exclusions live in its caller, ahead of this clause
    assert routing.is_uncomputable_payroll_amount(q) is False, q


def test_a_shop_owners_kodi_without_a_deduction_verb_is_not_told_to_supply_a_salary():
    assert routing.is_uncomputable_payroll_amount(SHOP_OWNER_KODI) is False


def test_a_figure_still_routes_to_the_engine():
    assert routing.detect_intent("Nikatwe PAYE kiasi gani mimi, mshahara 800,000?") == "paye"


def test_the_regime_question_keeps_its_statement_route():
    assert routing.fixed_statement_topic(RS_04) == "paye_residency"


def test_PLANT_dropping_the_deduction_verb_requirement_clarifies_the_shop_owner(monkeypatch):
    monkeypatch.setattr(routing, "_FP_DEDUCTION_VERB", re.compile(r""))
    assert routing.first_person_deduction_ask_no_figure(SHOP_OWNER_KODI) is True, "plant: without the verb limb the founder's must-not probe flips"


def test_PLANT_dropping_the_first_person_requirement_clarifies_a_generic_question(monkeypatch):
    monkeypatch.setattr(routing, "_FP_FIRST_PERSON", re.compile(r""))
    assert routing.first_person_deduction_ask_no_figure(GENERIC_PAYE) is True


def test_PLANT_dropping_the_money_ask_requirement_clarifies_the_regime_question(monkeypatch):
    monkeypatch.setattr(routing, "_has_money_ask", lambda ql: True)
    assert routing.first_person_deduction_ask_no_figure(REGIME_NO_DIGIT) is True


def test_patterns_hold_no_control_characters():
    for pat in (routing._FP_DEDUCTION_VERB, routing._FP_KODI_WORD):
        assert not re.search(r"[\x00-\x08]", pat.pattern), pat.pattern     # R39: a non-raw \b is a backspace


@pytest.mark.parametrize("q", MUST_CLARIFY)
def test_end_to_end_the_specimen_gets_the_clarification_and_never_the_model(q):
    fake = FakeBackend(scripted_reply="Kwa mshahara wa TZS 800,000, PAYE ni TZS 78,000.")
    reply = Orchestrator(backend=fake, retriever=lambda x: []).answer(q)
    assert reply.needs_clarification is True and fake.call_count == 0
    assert reply.text == clarification.PAYROLL_AMOUNT, "no residency line: these are not foreign"


def test_end_to_end_the_shop_owner_still_reaches_the_model_path():
    fake = FakeBackend(scripted_reply="MODEL")
    reply = Orchestrator(backend=fake, retriever=lambda x: []).answer(SHOP_OWNER_KODI)
    assert fake.call_count >= 1 and not reply.needs_clarification
