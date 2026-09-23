"""Guards the 2026-09-23 wrong_pattern rewrites: patterns written in English word order,
guarding text that is served in Swahili.

THE FOUNDING CASE. act_section_12 was corrected on 2026-08-31 (the foreign-company regime is
Companies Act Cap.212 Part XIII ss.320-328, not Part XII). The corpus was swept on 2026-09-01
and 14+ rows quarantined. CLAUDE.md Section 11 was fixed. And on 2026-09-05 a live reply
still said "Section XII" (ext_15), because the string also lived in a FOURTH place nobody
enumerated: the hand-authored CONCISE_BILINGUAL_FACTS text in
scripts/precompute_rag_embeddings.py, which is not derived from locked_facts.json.

WHY THREE STANDING CHECKS ALL PASSED ON IT -- the part worth keeping:
  * check_facts_index_sync.py  is CONTENT-shaped: "is this key's figure reachable?" USD 25
    was present, so CLEAN.
  * check_rag_index_freshness.py is TIME-shaped: "was the index rebuilt after the fact
    changed?" It was -- the string survived a regeneration, so CLEAN on that input.
  * check_correction_sync.py exists for precisely this ("does a corrected fact's own
    wrong_patterns match its deployed rendering?") and reported STRONG MATCH 0 -- because all
    four patterns required <part|section> FIRST and <foreign company> SECOND, and the Swahili
    row puts the entity first: "Kampuni ya kigeni (Section XII) ikichelewa...". The guard was
    correct English and blind to the language it guards.

A pattern in the wrong language is indistinguishable from a working pattern by every check
that only asks whether a guard FIRES -- because it never fires, on anything, and neither does
a guard with nothing to catch. Only planting a specimen in the served language separates them.

THE SECOND INSTANCE, found by the sweep rather than by accident: presumptive_tax_ceiling_100m.
Its guards against the stale TZS 100,000,000 ceiling covered two orderings and missed the two
most natural Swahili ones -- including the construction the fact's own text uses. See
eval/controls/scan_wrong_pattern_language_assumption.py and its artifact.
"""
import json
import os
import re

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_FACTS = os.path.join(_ROOT, "scripts", "locked_facts.json")


def _patterns(key):
    with open(_FACTS, encoding="utf-8") as fh:
        facts = json.load(fh)
    pats = facts[key]["wrong_patterns"]
    assert pats, f"{key} has no wrong_patterns -- this whole module would assert nothing"
    return pats


def _fires(key, text):
    return any(re.search(p, text, re.I) for p in _patterns(key))


# --- act_section_12 ---------------------------------------------------------

_XII_MUST_FIRE = [
    pytest.param(
        "Kampuni ya kigeni (Section XII) ikichelewa kuwasilisha ritani ya mwaka: faini ni "
        "USD 25 kwa kila mwezi (tofauti na kampuni za ndani ambazo hulipa TZS 2,500 kwa "
        "mwezi).",
        id="the_live_index_row_171_verbatim"),
    pytest.param(
        "Lakini kampuni za kigeni (foreign companies) chini ya Section XII zinaweza kulipa "
        "faini ya USD 25 kwa mwezi (thibitisha na BRELA).",
        id="the_live_ext_15_model_reply_verbatim"),
    pytest.param("Foreign companies are governed by Part XII of the Companies Act.",
                 id="english_token_first"),
    pytest.param("Under Section XII, a foreign company must file.", id="english_section"),
    pytest.param("Kwa kampuni ya kigeni, kifungu XII kinatumika.", id="swahili_kifungu"),
    pytest.param("Part 12 applies to external companies.", id="numeral_part_12"),
]

_XII_MUST_NOT_FIRE = [
    pytest.param(
        "act section 12: Foreign/external companies carrying on business in Tanzania are "
        "governed by Part XIII (ss.320-328) of the Companies Act, Cap.212 -- NOT Part XII, "
        "which governs winding up of unregistered companies (ss.314-319).",
        id="THE_DEPLOYED_ROW_WITH_ITS_KEY_PREFIX"),
    pytest.param(
        "Foreign/external companies carrying on business in Tanzania are governed by Part "
        "XIII (ss.320-328) of the Companies Act, Cap.212.",
        id="the_CORRECTED_fact_text_must_not_match_itself"),
    pytest.param(
        "Kampuni ya kigeni (Companies Act Cap.212, Part XIII, ss.320-328) ikichelewa "
        "kuwasilisha ritani ya mwaka: faini ni USD 25 kwa kila mwezi.",
        id="the_corrected_index_row_must_not_match_itself"),
    pytest.param("Part XIII governs foreign companies.", id="xiii_english"),
    pytest.param("kampuni za kigeni chini ya Part XIII zinalipa USD 25", id="xiii_swahili"),
    pytest.param("Part XII governs winding up of unregistered companies (ss.314-319).",
                 id="part_xii_used_correctly_for_winding_up"),
]


@pytest.mark.parametrize("text", _XII_MUST_FIRE)
def test_section_xii_patterns_fire_on_the_stale_citation(text):
    assert _fires("act_section_12", text), (
        "A stale Part-XII-for-foreign-companies claim went uncaught. The first two cases are "
        "VERBATIM live artifacts from 2026-09-05 -- if either stops firing, the guard has "
        "regressed to the English-word-order form that missed them originally.")


@pytest.mark.parametrize("text", _XII_MUST_NOT_FIRE)
def test_section_xii_patterns_do_not_fire_on_correct_text(text):
    """`xii\\b(?!i)` is what keeps XIII out; an edit that drops it makes the corrected fact
    match its own wrong_pattern.

    THE_DEPLOYED_ROW_WITH_ITS_KEY_PREFIX is the case that matters most and it is here because
    the first version of this rewrite failed it. Deployed index rows are rendered
    `act section 12: <text>`, so a pattern that allowed the NUMERAL after `section` matched
    the KEY PREFIX and fired on the correct row -- turning check_correction_sync.py red on
    clean content. The first round's specimens omitted the prefix and passed, which is the
    whole lesson: a guard must be tested against the string as DEPLOYED, not against the
    sentence as authored.
    """
    assert not _fires("act_section_12", text)


# --- presumptive_tax_ceiling_100m -------------------------------------------

_CEIL_MUST_FIRE = [
    pytest.param("Kikomo cha makadirio ni TZS 100,000,000.",
                 id="swahili_genitive_order_the_original_blind_spot"),
    pytest.param("Kikomo cha kodi ya makadirio ni TZS 100,000,000 kwa mwaka.",
                 id="genitive_with_kodi_ya"),
    pytest.param("Ukomo wa makadirio ni TZS 100,000,000.", id="ukomo_synonym"),
    pytest.param("Mauzo yasiyozidi TZS 100,000,000 hutumia kodi ya makadirio.",
                 id="the_construction_the_facts_OWN_text_uses"),
]

_CEIL_MUST_NOT_FIRE = [
    pytest.param("Kikomo cha makadirio ni TZS 200,000,000.",
                 id="the_CORRECT_current_ceiling"),
    pytest.param("Mauzo yasiyozidi TZS 200,000,000 hutumia kodi ya makadirio.",
                 id="correct_ceiling_in_the_facts_own_construction"),
    pytest.param("Kikomo cha makadirio kilikuwa TZS 100,000,000 hapo awali.",
                 id="historical_kilikuwa"),
    pytest.param("Kikomo cha makadirio kiliongezwa kutoka TZS 100,000,000 hadi TZS "
                 "200,000,000.", id="historical_kutoka_hadi"),
    pytest.param("Ilikuwa TZS 100,000,000 lakini sasa ni TZS 200,000,000 kwa makadirio.",
                 id="historical_ilikuwa_leading"),
]


@pytest.mark.parametrize("text", _CEIL_MUST_FIRE)
def test_presumptive_ceiling_patterns_fire_on_the_stale_100m(text):
    assert _fires("presumptive_tax_ceiling_100m", text), (
        "The stale TZS 100,000,000 ceiling went uncaught. It was doubled to 200,000,000 by "
        "Finance Act 2026 s.27(a)(i), verified verbatim 2026-09-01.")


@pytest.mark.parametrize("text", _CEIL_MUST_NOT_FIRE)
def test_presumptive_ceiling_patterns_spare_correct_and_historical_text(text):
    assert not _fires("presumptive_tax_ceiling_100m", text), (
        "The guard flagged correct or correctly-historical text. Stating what the ceiling "
        "USED to be is not an error, and a guard that forbids saying so makes the model "
        "unable to explain a change it is right about.")
