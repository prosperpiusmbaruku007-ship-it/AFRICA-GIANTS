"""Guards the 2026-09-23 wrong_pattern rewrites: patterns written in English word order,
guarding text that is served in Swahili.

⛔ READ THIS FIRST: THE "FOUNDING CASE" BELOW WAS A REVERSAL, AND THIS MODULE WAS INVERTED ON
2026-10-05. The 2026-08-31 "correction" it was built to enforce was itself the error. The
Companies Act Cap.212 R.E. 2023, read directly, puts the foreign-company regime at PART XII,
ss.437-447 (s.437(1)). So every pass described below was competent, and every one of them
pointed the wrong way, because each took the previous as its baseline. The description is kept
verbatim because what it discovered about HOW the defect hid is still correct and still load-
bearing; only the direction was wrong.

THE FOUNDING CASE (as recorded 2026-09-23, direction now known to be reversed). act_section_12
was "corrected" on 2026-08-31 (claiming the foreign-company regime is Part XIII ss.320-328, not
Part XII). The corpus was swept on 2026-09-01 and 14+ rows quarantined -- rows we now know were
RIGHT. CLAUDE.md Section 11 was "fixed". And on 2026-09-05 a live reply still said "Section XII"
(ext_15), because the string also lived in a FOURTH place nobody enumerated: the hand-authored
CONCISE_BILINGUAL_FACTS text in scripts/precompute_rag_embeddings.py, which is not derived from
locked_facts.json. That reply was marked a defect; the Act vindicates it on the numeral.

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

#
# ⛔⛔ INVERTED 2026-10-05. THIS BLOCK USED TO ASSERT THE ERROR IN BOTH DIRECTIONS.
#
# Until today _XII_MUST_FIRE required the guard to flag "Foreign companies are governed by Part
# XII of the Companies Act" -- a TRUE sentence -- and _XII_MUST_NOT_FIRE protected "Part XII
# governs winding up of unregistered companies (ss.314-319)", which is FALSE twice over (that is
# Part XI, at s.429+, and ss.314-319 are contributories/calls in Part VIII).
#
# The Companies Act Cap.212 R.E. 2023, read directly (394pp, brela.go.tz, HTTP 200, 2026-10-04):
#     PART XI    WINDING UP OF UNREGISTERED COMPANIES            s.429+
#     PART XII   COMPANIES INCORPORATED OUTSIDE TANZANIA         ss.437-447
#     PART XIII  GENERAL PROVISIONS AS TO REGISTRATION           s.454+
#     s.437.-(1) "Sections 438 to 447 shall apply to all foreign companies"
#
# R17's corollary says a test that instructs future maintainers not to fix a real defect is
# worse than no test, and that when that happens you INVERT IT AND KEEP THE HISTORY. This is
# that inversion. The history is kept not for sentiment but because the 2026-09-23 finding it
# encodes -- patterns in English word order guarding text served in Swahili -- is STILL TRUE and
# is still the only reason the live row was ever caught. Both orders are therefore still
# exercised below, against the reversed citation instead of the correct one.
#
# The verbatim live artifacts from 2026-09-05 are PRESERVED as must-NOT-fire cases, because that
# is what they now are: real production text that the Act vindicates on the numeral. Keeping
# them where a future reader can see them is the point -- they were the evidence of a defect and
# they are now the evidence of a correct answer, unchanged in between.

_XII_MUST_FIRE = [
    pytest.param(
        "Kampuni ya kigeni (Companies Act Cap.212, Part XIII, ss.320-328) ikichelewa "
        "kuwasilisha ritani ya mwaka: faini ni USD 25 kwa kila mwezi.",
        id="the_REVERSED_index_row_served_2026_09_22_to_2026_10_05"),
    pytest.param(
        "Foreign/external companies carrying on business in Tanzania are governed by Part "
        "XIII (ss.320-328) of the Companies Act, Cap.212.",
        id="english_token_first_reversed"),
    pytest.param("Part XIII governs foreign companies.", id="xiii_english"),
    pytest.param("kampuni za kigeni chini ya Part XIII zinalipa USD 25", id="xiii_swahili"),
    pytest.param("Kwa kampuni ya kigeni, sehemu ya XIII inatumika.",
                 id="swahili_sehemu_entity_first"),
    pytest.param("A foreign company files under ss.320-328.", id="bare_section_range"),
]

_XII_MUST_NOT_FIRE = [
    pytest.param(
        "Kampuni ya kigeni (Companies Act Cap.212, Part XII, ss.437-447) ikichelewa "
        "kuwasilisha ritani ya mwaka: faini ni USD 25 kwa kila mwezi.",
        id="THE_CORRECTED_INDEX_ROW_must_not_match_itself"),
    pytest.param(
        "act section 12: Foreign/external companies carrying on business in Tanzania are "
        "governed by PART XII (ss.437-447) of the Companies Act, Cap.212 R.E. 2023.",
        id="THE_DEPLOYED_ROW_WITH_ITS_KEY_PREFIX"),
    pytest.param(
        "Kampuni ya kigeni (Section XII) ikichelewa kuwasilisha ritani ya mwaka: faini ni "
        "USD 25 kwa kila mwezi (tofauti na kampuni za ndani ambazo hulipa TZS 2,500 kwa "
        "mwezi).",
        id="the_live_index_row_171_verbatim_NOW_VINDICATED"),
    pytest.param(
        "Lakini kampuni za kigeni (foreign companies) chini ya Section XII zinaweza kulipa "
        "faini ya USD 25 kwa mwezi (thibitisha na BRELA).",
        id="the_live_ext_15_model_reply_verbatim_NOW_VINDICATED"),
    pytest.param("Foreign companies are governed by Part XII of the Companies Act.",
                 id="part_xii_which_is_now_simply_correct"),
    pytest.param("Part XI governs winding up of unregistered companies (s.429+).",
                 id="part_xi_used_correctly_for_winding_up"),
]


@pytest.mark.parametrize("text", _XII_MUST_FIRE)
def test_patterns_fire_on_the_reversed_part_xiii_citation(text):
    assert _fires("act_section_12", text), (
        "The reversed Part-XIII-for-foreign-companies claim went uncaught. The first case is "
        "the text PRODUCTION ACTUALLY SERVED between 2026-09-22 and 2026-10-05. Both word "
        "orders must stay covered: the 2026-09-23 finding that English-ordered patterns are "
        "blind to Swahili-ordered text is still true and is still why the live row was caught.")


@pytest.mark.parametrize("text", _XII_MUST_NOT_FIRE)
def test_patterns_do_not_fire_on_the_correct_part_xii_citation(text):
    """THE WHOLE POINT OF THE INVERSION. Measured 2026-10-05, the pre-inversion patterns
    rejected 3 of 4 correct Part XII strings -- the fact's own guard was blocking right answers
    in both word orders, and the 2026-09-23 rewrite that finally made it fire is what gave it
    the power to do so. A guard that blocks a correct answer is worse than one that is blind.

    `xiii\\b` (not `xii`) is what now keeps the CORRECT citation out, and the direction of the
    substring hazard has flipped with the inversion: 'part xii' is a substring of 'part xiii',
    so a pattern matching bare `xii` catches both. The two deployed-row cases guard that, and
    THE_DEPLOYED_ROW_WITH_ITS_KEY_PREFIX stays because index rows render as
    `act section 12: <text>` -- a pattern allowing the numeral after `section` matches the KEY
    PREFIX and fires on clean content, which an earlier round of this file actually did.
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
