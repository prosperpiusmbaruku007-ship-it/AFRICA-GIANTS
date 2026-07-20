"""Unit tests for chike.routing — the deterministic Candidate-C router (ADR 0001 Phase A).

Fully offline (pure string logic). Covers the two paths (explicit levy + natural inference),
the boundary discriminators that defeated the keyword/embedding candidates, and the OOC
controls that must never route to compute.
"""

from chike import routing


# --- explicit path (named levy + number) -----------------------------------

def test_explicit_levy_with_number_routes_to_that_type():
    assert routing.detect_intent("SDL kwa wafanyakazi 15 wenye jumla ya mshahara 6,750,000") == "sdl"
    assert routing.detect_intent("NSSF ya mshahara wa 800,000 ni ngapi") == "nssf"


def test_explicit_levy_without_number_does_not_force_compute():
    # A named levy but no figure is a definition/rate question -> fact.
    assert routing.detect_intent("SDL ni ngapi") == "none"


# --- natural path (Candidate C: number + payroll + money-ask) ---------------

def test_natural_compute_infers_levy_from_generic_cue():
    assert routing.detect_intent(
        "Jumla ya mishahara milioni nne, bima ya ajali kazini ninalipa kiasi gani?") == "wcf"
    assert routing.detect_intent(
        "Mshahara ni laki tano, kodi ya mapato inayokatwa ni kiasi gani?") == "paye"


def test_generic_deductions_route_ambiguous_multi():
    # 'makato yote' is compute-intent but the specific levy is unresolved.
    assert routing.detect_intent(
        "Wafanyakazi kumi na mmoja, mishahara milioni saba, makato yote ni kiasi gani?"
    ) == "ambiguous_multi"


# --- boundary discriminators (same topic, opposite route) -------------------

def test_boundary_amount_vs_threshold():
    # amount asked -> compute; yes/no threshold -> fact
    assert routing.detect_intent(
        "Nina wafanyakazi wanane, mishahara milioni tatu, nalipa kiasi gani kwa tozo la ujuzi?"
    ) == "sdl"
    assert routing.detect_intent(
        "Nina wafanyakazi tisa tu — je bado nawajibika kulipa tozo la mafunzo?") == "none"


def test_boundary_rate_only_is_fact():
    # 'asilimia ngapi' (rate only) must NOT count as a money 'how-much' ask.
    assert routing.detect_intent("Je, mchango wa mwajiri kwenye pensheni ni asilimia ngapi?") == "none"


def test_fixed_fee_decoy_is_not_compute():
    # A published fee lookup ('kiasi gani kwa kila mwezi') with no payroll context -> fact.
    assert routing.detect_intent(
        "Baada ya faili la mwaka la kampuni, tozo la kuchelewa ni kiasi gani kwa kila mwezi?"
    ) == "none"


# --- OOC controls: numeric-looking but must never route to compute ----------

def test_ooc_questions_never_route_to_compute():
    for q in [
        "Niliuza kiwanja changu kwa faida — nalipa kodi kiasi gani kwa faida hiyo?",
        "Naagiza bidhaa kutoka nje — ushuru wa forodha ni kiasi gani?",
        "Nina mgodi mdogo wa dhahabu — mrabaha wa madini ninalipa kiasi gani?",
    ]:
        assert routing.detect_intent(q) == "none"


def test_moja_kwa_moja_idiom_not_a_number():
    # 'moja kwa moja' = 'directly', not the quantity 'one'.
    assert routing._has_number("mwajiri anaweza kulipa moja kwa moja") is False


# --- invoke gate ------------------------------------------------------------

def test_invoke_gate_fires_on_payroll_or_number_only():
    assert routing.invoke_extractor("Mshahara wangu ni milioni moja na nusu, baada ya kodi") is True
    assert routing.invoke_extractor("Nina duka lenye wafanyakazi wanne") is True
    # No number, no payroll context -> gate does not fire (a fee/definition lookup).
    assert routing.invoke_extractor("BRELA ada ni ngapi?") is False
