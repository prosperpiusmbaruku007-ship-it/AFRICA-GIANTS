# -*- coding: utf-8 -*-
"""Corporate/partnership income tax engine and its router path (path 1b, routing.py).

Two things this file exists to pin, both found live rather than assumed:

1. REACHABILITY over PAYE's bare `kodi ya mapato` natural-path claim (path 2). An entity-named
   question must win regardless of payroll context also being present in the same message —
   see eval/routing/sweep_corporate_tax_routing.py for the full-corpus sweep this is the
   targeted regression pin for.
2. The loss-years NON-trigger. eval_211 ("Kampuni yangu imekuwa na hasara miaka 4 mfululizo —
   je nitaweza kupunguza mapato ya mwaka wa 5 kwa hasara zote bila kikomo?") is about the
   loss-carryforward OFFSET LIMIT, an unimplemented provision — not AMT applicability. The
   first version of path 1b routed it to corporate_tax on the loss-year mention alone and the
   engine answered AMT with full authority to a question that was never asked. Fixed by
   requiring an income-tax/DSE cue to trigger the route; loss-years only ever REFINES an
   already-triggered corporate_tax answer. This test asserts the fix holds.
"""
from decimal import Decimal

from chike import routing, rules_engine


def test_entity_plus_bare_income_tax_cue_routes_corporate_even_with_payroll_context():
    """The exact reachability case: PAYE's path 2 would otherwise claim this on the
    {number + payroll context + money-ask} test alone."""
    q = "Kampuni yangu ina wafanyakazi 20, kodi ya mapato ni ngapi?"
    assert routing.detect_intent(q) == "corporate_tax"


def test_partnership_entity_routes_to_partnership_tax():
    q = "Ubia wetu una mauzo ya milioni 50, kodi ya mapato ni ngapi?"
    assert routing.detect_intent(q) == "partnership_tax"


def test_plain_paye_question_unaffected():
    q = "Mshahara wangu ni TZS 800,000, kodi ya mapato inakatwa kiasi gani?"
    assert routing.detect_intent(q) == "paye"


def test_eval_258_kodi_ya_pango_sdl_collision_still_routes_sdl():
    """Named check point from the corporate/partnership build plan: the rent/SDL collision
    (eval_258) must not be diverted by the new entity-gated path. No entity word, no
    income-tax cue in eval_258's text, so it was never at risk, but this pins it explicitly
    rather than relying on it being absent from the sweep's unexpected_changes."""
    q = ("Nalipa kodi ya pango TZS 850,000 kwa mwezi kwa ofisi, hii inaingia kwenye "
         "hesabu ya SDL?")
    assert routing.detect_intent(q) == "sdl"


def test_loss_years_alone_does_not_trigger_the_route():
    """CONTROL for the eval_211 fix. No income-tax/DSE cue in this sentence at all, so the
    loss-year mention must NOT be enough on its own."""
    q = ("Kampuni yangu imekuwa na hasara miaka 4 mfululizo — je nitaweza kupunguza mapato "
         "ya mwaka wa 5 kwa hasara zote bila kikomo?")
    assert routing.detect_intent(q) == "none"


def test_loss_years_still_read_once_an_income_tax_question_triggers_the_route():
    """The other half of the same control: loss-years must still REFINE the answer once the
    route is triggered by a real cue — the fix narrows the TRIGGER, not the field read."""
    q = "Kampuni yangu ina hasara miaka 3 mfululizo, kodi ya mapato ninalipa kiasi gani?"
    assert routing.detect_intent(q) == "corporate_tax"
    assert routing.corporate_loss_years(q) == 3


def test_standard_rate_statement_states_both_figures():
    r = rules_engine.corporate_tax_rate_statement()
    assert r.applicable
    assert r.amount is None
    assert "asilimia 30" in r.working
    assert "asilimia 25" in r.working


def test_dse_listed_meeting_public_float_gives_25_percent():
    r = rules_engine.corporate_tax_rate_statement(is_dse_listed=True, meets_public_float=True)
    assert "asilimia 25" in r.working
    assert r.amount is None


def test_dse_listed_not_meeting_public_float_falls_back_to_standard_rate():
    r = rules_engine.corporate_tax_rate_statement(is_dse_listed=True, meets_public_float=False)
    assert "asilimia 30" in r.working
    assert "SI asilimia 25" in r.working


def test_dse_listed_with_unstated_float_asks_rather_than_guesses():
    r = rules_engine.corporate_tax_rate_statement(is_dse_listed=True, meets_public_float=None)
    assert "LAKINI" in r.working or "sharti" in r.working
    assert r.amount is None


def test_amt_applies_at_exactly_three_loss_years():
    r = rules_engine.corporate_tax_rate_statement(loss_years=3)
    assert r.applicable
    assert "AMT inatumika" in r.working
    assert r.amount is None


def test_amt_does_not_apply_below_three_loss_years():
    r = rules_engine.corporate_tax_rate_statement(loss_years=2)
    assert r.applicable is False
    assert "AMT" in r.working


def test_amt_permanent_sector_exemption_agriculture():
    r = rules_engine.corporate_tax_rate_statement(loss_years=5, sector="agriculture")
    assert "ZIMESAMEHEWA AMT" in r.working
    assert "kilimo" in r.working


def test_amt_tea_processing_exemption_states_explicit_sunset():
    r = rules_engine.corporate_tax_rate_statement(loss_years=5, sector="tea_processing")
    assert "2024-07-01" in r.working
    assert "2027-06-30" in r.working
    assert "kipindi maalum" in r.working


def test_partnership_is_never_itself_taxed_and_declines_to_guess_a_rate():
    r = rules_engine.partnership_tax_statement()
    assert r.applicable
    assert r.amount is None
    assert "HAULIPI" in r.working
    assert "Sina taarifa ya kutosha" in r.working


def test_never_computes_a_tzs_amount_from_turnover():
    """The whole reason this is a rate-statement engine and not presumptive.py's shape:
    profit is not derivable from turnover, so amount must stay None on every branch."""
    for kwargs in ({}, {"is_dse_listed": True, "meets_public_float": True},
                   {"loss_years": 3}, {"loss_years": 5, "sector": "health"}):
        r = rules_engine.corporate_tax_rate_statement(**kwargs)
        assert r.amount is None, f"{kwargs} produced a TZS amount — profit isn't derivable " \
                                  f"from turnover"
