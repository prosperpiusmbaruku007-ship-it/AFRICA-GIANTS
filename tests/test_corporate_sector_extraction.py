# -*- coding: utf-8 -*-
"""routing.corporate_sector() -- closes the gap found live 2026-09-05
(eval/controls/corporate_domain_live_probe_2026_09_05.json): corporate_tax_rate_statement()'s
s.4(8) AMT sector-exemption branches existed and were unit-tested since 2026-09-01, but
nothing extracted a sector from question text, so an agriculture company and a private
school were both told "yes, pay AMT" live -- wrong, both are permanently exempt.

R17 IS THE POINT OF THIS FILE, NOT A FORMALITY. kilimo/afya/elimu are common words that
already appear standalone throughout this project's own corpora for reasons that have
nothing to do with corporate AMT (GN605A minimum-wage sector lists, OOC adversarial probes).
Every positive test below uses an ENTITY-POSSESSIVE phrase ("kampuni ya kilimo", "shule
yetu"); every adversarial test below uses the SAME risky word in a sentence where the
asking company is NOT itself in that sector, and must return None.
"""
from chike import routing


# --- positive: entity-possessive phrasing for each sector ------------------------------

def test_agriculture_positive_forms():
    for q in [
        "Kampuni yetu ya kilimo imepata hasara miaka mitatu mfululizo, AMT inatumika?",
        "Shirika letu la kilimo lina hasara, tunalipa AMT?",
        "Kampuni yetu inayofanya kilimo imepata hasara miaka mitatu mfululizo.",
    ]:
        assert routing.corporate_sector(q) == "agriculture", q


def test_health_positive_forms():
    for q in [
        "Kampuni yetu ya afya imepata hasara miaka mitatu mfululizo, AMT inatumika?",
        "Hospitali yetu imepata hasara miaka mitatu mfululizo.",
        "Kituo chetu cha afya kina hasara miaka mitatu mfululizo, tunalipa AMT?",
    ]:
        assert routing.corporate_sector(q) == "health", q


def test_education_positive_forms():
    for q in [
        "Shule yetu binafsi imepata hasara miaka mitatu mfululizo, AMT inatumika?",
        "Chuo chetu kina hasara miaka mitatu mfululizo, tunalipa AMT?",
        "Kampuni yetu ya elimu imepata hasara miaka mitatu mfululizo.",
    ]:
        assert routing.corporate_sector(q) == "education", q


def test_tea_processing_positive_forms():
    for q in [
        "Kiwanda chetu cha chai kimepata hasara miaka mitatu mfululizo, AMT inatumika?",
        "Kampuni yetu ya usindikaji wa chai ina hasara miaka mitatu mfululizo.",
    ]:
        assert routing.corporate_sector(q) == "tea_processing", q


def test_no_sector_mentioned_returns_none():
    q = "Kampuni yetu ya usafirishaji imepata hasara kwa miaka mitatu mfululizo, AMT inatumika?"
    assert routing.corporate_sector(q) is None


# --- R17 adversarial: bare sector words alone, no entity-possessive framing -------------

def test_bare_sector_words_alone_do_not_trigger():
    """The exact risk this project's own corpora already demonstrate: kilimo/afya/elimu
    appear as bare, standalone words for reasons unrelated to corporate AMT. A bare mention
    with no possessive/descriptive tie to the asking company must not resolve a sector."""
    for q in [
        "Sekta ya kilimo nchini Tanzania ina wafanyakazi wengi.",
        "Wafanyakazi wa afya wanahitaji bima gani?",
        "Elimu ya ufundi stadi inasamehewa SDL.",
        "Bei ya chai imepanda mwaka huu.",
    ]:
        assert routing.corporate_sector(q) is None, q


# --- R17 adversarial: risky word present, but the ASKING company is not in that sector ---

def test_company_selling_to_a_sector_is_not_the_sector_itself():
    """s.4(8) exempts a corporation CONDUCTING agriculture/health/education, not one merely
    serving that sector as a customer base. A fertiliser distributor mentioning wakulima
    (farmers) must not be read as itself an agriculture company."""
    q = ("Kampuni yetu inauza mbolea na madawa kwa wakulima nchini kote, tumepata hasara "
         "miaka mitatu mfululizo, tunalipa AMT?")
    assert routing.corporate_sector(q) is None, q


def test_company_providing_health_insurance_benefit_is_not_a_health_company():
    """Mentioning 'afya' via an employee health-insurance benefit is a PAYE/NSSF-adjacent
    detail, not a claim that the company itself provides health services."""
    q = ("Kampuni yetu ya usafirishaji inatoa bima ya afya kwa wafanyakazi, tumepata hasara "
         "miaka mitatu mfululizo, tunalipa AMT?")
    assert routing.corporate_sector(q) is None, q


def test_company_offering_education_loans_is_not_an_education_company():
    """'mikopo ya elimu' (education loans) is a benefit the company offers, not a claim
    that the company itself is an education provider."""
    q = ("Kampuni yetu inatoa mikopo ya elimu kwa wafanyakazi wake, tumepata hasara miaka "
         "mitatu mfululizo, tunalipa AMT?")
    assert routing.corporate_sector(q) is None, q


def test_company_delivering_to_schools_and_hospitals_is_not_exempt():
    """Bare 'shule'/'hospitali' as the OBJECT of a sentence (delivered TO, not identified
    AS) must not resolve a sector -- this is the collision risk R17 exists to catch before
    shipping, not after."""
    q = ("Kampuni yetu ya usafirishaji inasafirisha bidhaa kwa shule na hospitali nchini "
         "kote, tumepata hasara miaka mitatu mfululizo, tunalipa AMT?")
    assert routing.corporate_sector(q) is None, q


def test_tea_price_mention_is_not_tea_processing():
    q = ("Kampuni yetu ya rejareja inauza chai na sukari dukani, tumepata hasara miaka "
         "mitatu mfululizo, tunalipa AMT?")
    assert routing.corporate_sector(q) is None, q


# --- \bamt\b word-boundary regression (the OTHER collision found while building this) ---

def test_amt_cue_matches_bare_mention():
    q = "Kampuni yetu imepata hasara miaka mitatu mfululizo, AMT inatumika?"
    assert routing.asks_corporate_income_tax(q.lower())


def test_amt_cue_does_not_match_inside_ordinary_verb_forms():
    """'inamtaka' (wants him/her) and 'inamtambua' (recognises him/her) both contain the
    substring 'amt' -- found by checking before adding the cue, not assumed safe, exactly
    the R17 discipline this fix is itself an instance of. A bare-substring 'amt' cue would
    have matched either verb form in ANY message that also names a corporate entity."""
    for verb in ("inamtaka", "inamtambua"):
        q = f"Kampuni yetu {verb} mfanyakazi mpya, kodi ya ajira ni ngapi?"
        assert not routing.asks_corporate_income_tax(q.lower()), q
