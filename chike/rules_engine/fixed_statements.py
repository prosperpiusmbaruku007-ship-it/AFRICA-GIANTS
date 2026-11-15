# -*- coding: utf-8 -*-
"""Fixed statutory statements — five questions whose answer is a CONSTANT, stated whole, no model.

WHY THIS EXISTS (2026-11-16). The live check of the 2026-11-13 coverage deploy found five answers wrong with the
correct fact at rank 1 (notice "siku 4" vs 28; severance "+25%"; overtime "25%" vs 1.5x; annual leave a non-answer;
VAT on credit sales "kidogo kidogo"). Rank 1 is the ceiling of retrieval, so no index edit reaches it: the model was
handed the fact and contradicted it. These are CONSTANTS (R19), so the cure is to state the constant without the model.

THE DISCIPLINE, and the reason each text is a whole fact and not a picked limb:
  * Each statement is the verified fact text, ALL limbs. The notice question is the sharpest case: the answer is a
    table (first month 7 days; then 4 for daily/weekly paid; 28 for monthly paid), and the asker rarely says which row
    they are in. Picking one would be a confident answer to a question they did not ask, which is exactly how "siku 4"
    reached a monthly employee. The statement never selects a limb.
  * The text is NOT a second copy that can drift: `tests/test_fixed_statements.py` asserts each statement is a
    substring of the corresponding row of `precompute_rag_embeddings.CONCISE_BILINGUAL_FACTS` (the text the index
    serves) and that every figure in it equals the locked fact's `correct_value`.
  * Nothing here computes an amount. "Severance for 5 years at 500,000" is a derived quantity (R19's Guard B): the
    statement gives the rule and leaves the arithmetic to the reader or the reviewer.

⛔ NOT AUTO-SEND ELIGIBLE (founder's decision, 2026-11-16; CLAUDE.md, the R7 amendment, recorded as a NARROWING).
These answers are model-free, so under `model_calls == 0` they would qualify for the 15-minute unreviewed send. They
must not during the pilot: they go to review like any model answer, but with a CORRECT draft. The exclusion lives in
`handler_core.engine_only_verdict` and fails closed on any route not explicitly allowed.
"""

from .results import ComputationResult

NOTICE = "notice"
SEVERANCE = "severance"
OVERTIME = "overtime"
ANNUAL_LEAVE = "annual_leave"
VAT_TIME_OF_SUPPLY = "vat_time_of_supply"

# topic -> (locked-fact key, the statement, citation note). Statement text is lifted from the served concise row with
# the leading question sentence removed (the user has just asked it).
STATEMENTS = {
    NOTICE: (
        "termination_notice_period",
        "Notisi ya kuacha au kuachishwa kazi: mwezi wa kwanza ni siku 7. Baada ya hapo: siku 4 kwa mfanyakazi wa kila siku "
        "au kila wiki, siku 28 kwa wa kila mwezi. Mkataba unaweza kuweka muda mrefu zaidi ikiwa ni sawa kwa mwajiri na "
        "mfanyakazi. Notisi iandikwe ikitaja sababu na tarehe; mwajiri anaweza kulipa mshahara wa kipindi cha notisi "
        "badala yake (ELRA, Kifungu 41).",
        "ELRA Cap.366, notice of termination (s.41 R.E.2019; TanzLII s.42) — all three limbs stated, none selected",
    ),
    SEVERANCE: (
        "severance_pay",
        "Malipo ya kuachishwa kazi (severance pay): mfanyakazi aliyetimiza miezi 12 mfululizo na akaachishwa anapata "
        "angalau mshahara wa msingi wa siku 7 kwa kila mwaka kamili, hadi miaka 10. Hayalipwi kwa kuachishwa kihalali kwa "
        "utovu wa nidhamu, au anayekataa kazi mbadala bila sababu, au aliyestaafu au mkataba kuisha (ELRA, Kifungu 42).",
        "ELRA Cap.366, severance pay (s.42 R.E.2019; TanzLII s.43) — a rule, never an amount",
    ),
    OVERTIME: (
        "overtime_pay_rate",
        "Overtime (saa za ziada) inalipwa angalau mara 1.5 ya mshahara wa msingi. Overtime ni kwa makubaliano tu, na "
        "isizidi saa 50 kwa kila wiki 4 (ELRA, Kifungu 19).",
        "ELRA Cap.366, hours of work (s.19 R.E.2019; TanzLII s.20)",
    ),
    ANNUAL_LEAVE: (
        "annual_leave_days",
        "Likizo ya mwaka ni angalau siku 28 mfululizo kwa kila mzunguko wa likizo (sikukuu zilizo ndani zinahesabiwa), na "
        "mfanyakazi analipwa mshahara wake. Mwajiri apange ichukuliwe ndani ya miezi 6 baada ya mzunguko, au miezi 12 kwa "
        "ridhaa ya mfanyakazi na sababu ya kiutendaji (ELRA, Kifungu 31).",
        "ELRA Cap.366, annual leave (s.31 R.E.2019; TanzLII s.32)",
    ),
    VAT_TIME_OF_SUPPLY: (
        "vat_credit_sale_timing",
        "VAT inakuwa inadaiwa mapema zaidi kati ya: siku ya kutoa invoice, siku ya kupokea malipo (hata sehemu), au wakati "
        "wa usambazaji. Hivyo ukitoa invoice, VAT inadaiwa hata mteja asipolipa bado. Return ya VAT ni tarehe 20 ya mwezi "
        "unaofuata (Sheria ya VAT, Vifungu 15 na 70).",
        "VAT Act Cap.148 R.E.2023, s.15(a)-(c) and s.70(1) — time of supply is the earliest of the three events",
    ),
}

TOPICS = tuple(STATEMENTS)


def fixed_statement(topic) -> ComputationResult:
    """The whole statement for `topic`. An unknown topic raises: a statement route with no statement must never fall back to
    generation or to a guess (R31: a branch with no extractor is a capability that does not exist)."""
    if topic not in STATEMENTS:
        raise KeyError(f"no fixed statement for topic {topic!r}")
    key, text, note = STATEMENTS[topic]
    return ComputationResult(
        computation="fixed_statement",
        applicable=True,
        amount=None,                      # R19: a constant, never a derived amount.
        working=text,
        inputs={"topic": topic, "fact": key},
        note=note,
    )
