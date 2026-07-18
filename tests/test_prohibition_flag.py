"""Tests for the high-stakes prohibition polarity safety flag (chike.scoring).

Reporting-only safety mechanism added after the 400-question run surfaced two dangerous
GN487A prohibition inversions (eval_317 salon, eval_332 wholesale) that scorer_reliability
had EXCLUDED as yes_no_polarity_unverifiable — hiding them from the reliable-subset
headline. These tests lock in that:
  - hard-prohibition / absolute-obligation yes-no questions are tagged deterministically,
  - a polarity that disagrees with the reference answer is flagged as a candidate inversion
    REGARDLESS of scorer_reliability,
  - and the refinements that removed the real-data false alarms hold (clarification/refusal
    is not an inversion; a 'both'/ambiguous parse is surfaced but not counted; a neutral
    factual yes-no in an obligation subdomain is not over-tagged).
Cases mirror the actual eval_* findings so a regression re-introducing the hole fails here.
"""
from chike.scoring import high_stakes_prohibition, prohibition_polarity_review


# --- high_stakes_prohibition tagging -----------------------------------------

def test_gn487a_yes_no_is_high_stakes():
    q = {"answer_type": "yes_no", "subdomain": "gn487a",
         "question_sw": "Kama mgeni je naweza kufungua saluni Tanzania?"}
    assert high_stakes_prohibition(q) == (True, "gn487a")


def test_obligation_subdomain_needs_a_marker():
    # A neutral factual yes-no about a rate must NOT be tagged (no prohibition/obligation
    # marker) — otherwise the review section over-surfaces.
    neutral = {"answer_type": "yes_no", "subdomain": "nssf_contributions",
               "question_sw": "Je, kiwango cha NSSF ni asilimia 20?"}
    assert high_stakes_prohibition(neutral) == (False, "")
    # With an obligation marker it IS high-stakes.
    obliged = {"answer_type": "yes_no", "subdomain": "nssf_contributions",
               "question_sw": "Je, nalazimika kulipa NSSF kwa mfanyakazi mmoja?"}
    assert high_stakes_prohibition(obliged)[0] is True


def test_non_yes_no_and_out_of_scope_subdomain_not_tagged():
    assert high_stakes_prohibition(
        {"answer_type": "number", "subdomain": "gn487a", "question_sw": "adhabu ni ngapi?"}
    ) == (False, "")
    assert high_stakes_prohibition(
        {"answer_type": "yes_no", "subdomain": "vat_registration",
         "question_sw": "Je, nimefikia kizingiti cha VAT?"}
    )[1] != "gn487a"


def test_min_wage_floor_caught_by_marker():
    q = {"answer_type": "yes_no", "subdomain": "sdl_compliance",
         "question_sw": "Naweza kulipa chini ya kima cha chini cha mshahara?"}
    assert high_stakes_prohibition(q) == (True, "min_wage_floor")


# --- prohibition_polarity_review inversion detection -------------------------

def test_flags_salon_inversion_like_eval_317():
    q = {"id": "eval_317", "answer_type": "yes_no", "subdomain": "gn487a",
         "question_sw": "Nina mtaji wa TZS 100,000,000, kama mgeni je naweza kufungua saluni?",
         "correct_answer_sw": "Hapana. Chini ya GN 487A, saluni imezuiliwa kwa wasio raia."}
    gen = ("Kulingana na taarifa rasmi, mtu asiye raia anaweza kuendesha saluni "
           "ikiwa atakuwa na mtaji wa chini ya milioni 100.")
    rev = prohibition_polarity_review(q, gen)
    assert rev["candidate_inversion"] is True
    assert rev["gold_polarity"] == "no" and rev["model_polarity"] == "yes"


def test_correct_prohibition_answer_not_flagged():
    # eval_148-shape: correct 'Ndiyo, imekatazwa' — model agrees with gold, no flag.
    q = {"id": "eval_148", "answer_type": "yes_no", "subdomain": "gn487a",
         "question_sw": "Biashara ya jumla imekatazwa kwa wageni?",
         "correct_answer_sw": "Ndiyo. Biashara ya jumla imekatazwa kwa wageni chini ya GN 487A."}
    gen = "GN487A inakataza shughuli 15 kwa wasio raia; jumla ni miongoni mwa zilizokatazwa."
    rev = prohibition_polarity_review(q, gen)
    assert rev["candidate_inversion"] is False


def test_clarification_is_not_an_inversion():
    # eval_343 was a false alarm: the sentinel's affirmative default != gold 'no'.
    q = {"id": "eval_343", "answer_type": "yes_no", "subdomain": "wcf_compliance",
         "question_sw": "Ajali lazima itolewe taarifa ndani ya siku 30, sivyo? Nalazimika?",
         "correct_answer_sw": "Hapana. Ajali lazima itolewe taarifa ndani ya siku 7."}
    rev = prohibition_polarity_review(q, "<CLARIFICATION_NEEDED>")
    assert rev["candidate_inversion"] is False
    assert rev["status"] == "clarified_or_refused"


def test_ambiguous_both_parse_is_surfaced_not_counted():
    # eval_182-shape: model is CORRECT ('mandatory; there is no optional version') but the
    # 'lazima' + negation combo parses as 'both' — must not be a candidate inversion.
    q = {"id": "eval_182", "answer_type": "yes_no", "subdomain": "osha_registration",
         "question_sw": "Ukaguzi wa OSHA ni wa lazima au wa hiari?",
         "correct_answer_sw": "Ni wa lazima. Ukaguzi wa kila mwaka ni sharti la OSHA."}
    gen = "Ukaguzi wa OSHA ni WA LAZIMA. Hakuna cheti cha ukaguzi wa hiari kinachotolewa."
    rev = prohibition_polarity_review(q, gen)
    assert rev["candidate_inversion"] is False
    assert rev["status"] == "polarity_ambiguous"


def test_returns_none_when_not_high_stakes():
    q = {"id": "eval_001", "answer_type": "number", "subdomain": "vat_registration",
         "question_sw": "Kizingiti cha VAT ni ngapi?", "correct_answer_sw": "TZS 200,000,000."}
    assert prohibition_polarity_review(q, "TZS 200,000,000") is None
