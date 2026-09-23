"""Regression guard for the 2026-09-23 widening of the corporate-tax route gate.

THE GATE is `is_corporate_entity(text) AND (asks_corporate_income_tax(ql) OR
is_dse_listed(text) is not None)`. Four rows of the extended-078 probe set failed it live on
2026-09-05, and the diagnosis was made PER CONJUNCT by calling the predicates on the verbatim
probe strings rather than inferred from the replies -- two different gaps, not one:

    ext_03   entity=False  tax=False  dse=True    -> ENTITY conjunct. Names no entity noun.
    ext_04   entity=True   tax=False              -> TAX conjunct. "tunadaiwa kodi gani?"
    ext_05   entity=True   tax=False              -> TAX conjunct. Plural "makampuni".
    ext_07   entity=True   tax=False              -> TAX conjunct. "kodi maalum ya makampuni".

ext_05 matters most: corporate_sector() has returned "health" for its "zahanati yetu" since
2026-09-05 and the branch was unreachable because the ROUTE never opened. R31 one level up --
a parameter given a working extractor is still unreachable if the gate in front of it is shut.
That is why test_ext_05_reaches_the_sector_branch_end_to_end asserts the route AND the sector
together: either alone passes while the capability stays dead.

THE CONSTRAINT. eval_211 asks about the LOSS-CARRYFORWARD OFFSET LIMIT, a different and
unimplemented FA2024 provision, while mentioning a company and four loss years. Routing it to
corporate_tax makes the AMT engine answer a question it was never asked -- a wrong-topic answer
with the engine's full authority. Note it fails on the TAX conjunct, NOT on the loss-year rule
the existing comment describes, so a careless tax-cue addition is exactly what breaks it and
the loss-year comment would not have caught that. It is pinned below.

Sweep: eval/routing/sweep_corporate_gate_widening_2026_09_23.py over all 1,167 committed
corpus questions -> eval/results/corporate_gate_widening_sweep_2026_09_23.json.
Result: 8 route changes, all `none -> corporate_tax`, zero diversions from any existing route.
"""
import pytest

from chike import routing

# Verbatim from eval/accuracy_gate/edge_probe_extended_078_DRAFT.jsonl. Copied byte-for-byte,
# never paraphrased -- R26 records a case where a five-word paraphrase flipped a verdict.
EXT_01 = ("Kampuni yetu inauza vifaa vya ujenzi, hatujaorodheshwa soko la hisa. Kodi ya "
          "mapato tunayolipa mwishoni mwa mwaka ni asilimia ngapi ya faida?")
EXT_02 = ("Tumeorodheshwa hivi karibuni sokoni la hisa la Dar es Salaam. Je, tunalipa kodi "
          "ya mapato kwa kiwango gani sasa?")
EXT_03 = ("Tulioorodheshwa DSE mwaka jana lakini ni asilimia 15 tu ya hisa zetu ndizo "
          "mikononi mwa umma. Tunalipa kodi ipi?")
EXT_04 = ("Kampuni yetu ya usafirishaji wa mizigo imepata hasara miaka mitatu iliyopita "
          "mfululizo. Sasa tunadaiwa kodi gani?")
EXT_05 = ("Zahanati yetu binafsi imekuwa na hasara miaka mitatu mfululizo. Tunatakiwa "
          "kulipa ile kodi ya makampuni yenye hasara?")
EXT_07 = ("Kampuni yetu imepata hasara miaka miwili mfululizo tu hadi sasa. Je, tayari "
          "tunadaiwa ile kodi maalum ya makampuni yenye hasara ya muda mrefu?")
EVAL_211 = ("Kampuni yangu imekuwa na hasara miaka 4 mfululizo — je nitaweza kupunguza "
            "mapato ya mwaka wa 5 kwa hasara zote bila kikomo?")


@pytest.mark.parametrize("question, why", [
    pytest.param(EXT_01, "entity noun + kodi ya mapato; routed before, pinned so the "
                         "classifier fix and this one cannot regress each other", id="ext_01"),
    pytest.param(EXT_02, "self-listing 1pl, locative 'sokoni la hisa'", id="ext_02"),
    pytest.param(EXT_03, "NO entity noun at all -- the listing verb is the only evidence",
                 id="ext_03"),
    pytest.param(EXT_04, "'tunadaiwa kodi gani' -- the register an owner actually uses",
                 id="ext_04"),
    pytest.param(EXT_05, "plural 'kodi ya makampuni', which 'kodi ya kampuni' never covered",
                 id="ext_05"),
    pytest.param(EXT_07, "'kodi maalum ya makampuni yenye hasara'", id="ext_07"),
])
def test_corporate_questions_reach_the_corporate_route(question, why):
    assert routing.detect_intent(question) == "corporate_tax", (
        f"This is a corporate-tax question that must reach the engine ({why}). "
        "Before 2026-09-23 it fell through to the fact/RAG path and was answered wrongly.")


def test_ext_05_reaches_the_sector_branch_end_to_end():
    """R31, one level up. corporate_sector() has returned 'health' for this exact string
    since 2026-09-05 via the 'zahanati yetu' cue -- the extractor was never the problem. The
    ROUTE was shut, so the s.4(8) exemption branch could not be reached from a real message
    and a loss-making clinic was told live to pay AMT it is exempt from.

    Both assertions are required. Route alone passes while the sector goes unread; sector
    alone passes while nothing ever calls it. The capability is the conjunction.
    """
    assert routing.corporate_sector(EXT_05) == "health"
    assert routing.detect_intent(EXT_05) == "corporate_tax"


def test_eval_211_still_does_not_reach_the_corporate_engine():
    """THE PIN. A loss-carryforward offset-limit question must NOT be handed to the AMT
    engine. It is blocked by the TAX conjunct -- not by the loss-year rule -- so any future
    tax-cue addition must be re-checked against this row specifically."""
    assert routing.detect_intent(EVAL_211) != "corporate_tax"


def test_the_rejected_broad_cue_is_not_present():
    """`kodi gani` reaches ext_04 and, measured over 1,167 questions, diverts nothing. It was
    still REJECTED: it is semantically the whole space of "which tax?", so any company asking
    about any tax topic would be handed to the AMT engine -- the eval_211 harm, admitted by
    the front door. A cue is judged on what it COULD capture, not only on what today's corpus
    happens to contain (R21: the sweep is a lower bound, not a safety proof)."""
    assert "kodi gani" not in routing._CORPORATE_INCOME_TAX_CUES


def test_sole_trader_asking_the_same_way_is_not_routed_to_corporate():
    """THE NEGATIVE LIMB, and the reason the gate is a conjunction. ext_08 contains the new
    `nadaiwa kodi` cue ("Ninadaiwa kodi ngapi?") but names no corporate entity -- it is a
    market trader on the presumptive path. The tax cue alone must never be enough."""
    ext_08 = "Nina duka dogo, mauzo yangu mwaka huu ni milioni tatu tu. Ninadaiwa kodi ngapi?"
    assert "nadaiwa kodi" in ext_08.lower(), "specimen no longer exercises the new cue"
    assert routing.detect_intent(ext_08) != "corporate_tax"


def test_shipped_cues_are_the_inflection_family_forms():
    """R17 step 4: one substring covering a whole inflection family, not four hand-written
    variants. If someone later replaces these with the specific forms, the cue list grows and
    the next unseen inflection is missed again."""
    assert "orodheshwa" in routing._CORPORATE_SELF_LISTING_CUES
    assert "nadaiwa kodi" in routing._CORPORATE_INCOME_TAX_CUES
    for subsumed in ("tumeorodheshwa", "tulioorodheshwa", "hatujaorodheshwa"):
        assert subsumed not in routing._CORPORATE_SELF_LISTING_CUES, (
            f"{subsumed!r} is already covered by the substring 'orodheshwa'")
    for subsumed in ("tunadaiwa kodi", "ninadaiwa kodi"):
        assert subsumed not in routing._CORPORATE_INCOME_TAX_CUES, (
            f"{subsumed!r} is already covered by the substring 'nadaiwa kodi'")
