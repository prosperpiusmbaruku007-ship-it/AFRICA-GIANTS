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


# --- net-take-home router extension (rc_11: replaces the retired LLM backstop) ---------

def test_net_take_home_phrasing_routes_to_paye_deterministically():
    # rc_11: number + payroll + a PAYE cue, but NO explicit 'kiasi gani' — the money ask is
    # the net-take-home phrasing ('kitakachobaki mkononi baada ya kodi ya mshahara'). This is
    # the case the extractor-emitted-intent backstop targeted and failed on real weights; the
    # deterministic router now handles it, no model call.
    q = ("Mshahara wangu wa mwezi ni milioni moja na nusu. Nataka kujua kitakachobaki "
         "mkononi baada ya kodi ya mshahara.")
    assert routing.detect_intent(q) == "paye"


def test_take_home_cue_needs_payroll_and_number_to_route_compute():
    # 'baada ya kodi' alone, with no payroll context or number, is not a compute route.
    assert routing.detect_intent("Bei ya bidhaa baada ya kodi ni ipi?") == "none"


# --- fabrication guard: is_uncomputable_payroll_amount --------------------------------

def test_guard_fires_on_payroll_amount_ask_with_no_salary():
    # rc_22: payroll context + generic levy ('makato ya mshahara') + money ask ('kiasi gani')
    # but no monetary figure -> guard True (clarify, never fabricate).
    q = ("Nina duka lenye wafanyakazi wanne. Makato ya mshahara ninayotakiwa kulipa "
         "kila mwezi ni kiasi gani?")
    assert routing.detect_intent(q) == "none"          # router abstains (no amount)
    assert routing.is_uncomputable_payroll_amount(q) is True


def test_guard_does_not_fire_on_fee_lookup_or_rate_or_computable_question():
    # Fixed-fee lookup (no payroll context) -> not the guard's business.
    assert routing.is_uncomputable_payroll_amount("BRELA ada ya mwaka ni ngapi?") is False
    # Rate/definition question ('asilimia ngapi' is a non-money ask) stays on the fact path.
    assert routing.is_uncomputable_payroll_amount(
        "Kodi ya mapato kwa mshahara ni asilimia ngapi?") is False
    # A computable payroll question (amount present) routes to compute, never reaches the guard.
    assert routing.is_uncomputable_payroll_amount(
        "Nihesabie SDL kwa wafanyakazi 15 wenye jumla ya mshahara 6,750,000?") is False
