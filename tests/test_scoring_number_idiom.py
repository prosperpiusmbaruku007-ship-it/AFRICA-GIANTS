"""Tests for the 'moja kwa moja' idiom guard in chike.scoring.extract_numbers.

'moja kwa moja' is the Swahili idiom for "directly", not the quantity one. Before the
guard, the '\\bmoja\\b' numeral match injected a spurious '1' into any answer carrying the
idiom — a junk numeric key that did the same two kinds of damage as the old '000' fragment
bug (documented in scoring.extract_numbers and PROGRESS.md):

  (a) it suppressed the qualitative_number_no_numeric_key reliability exclusion, turning
      genuine "no fixed figure" answers into false FAILs (eval_134, eval_217); and
  (b) because the model's own answer often repeats the idiom, gold and output collided on
      the bare '1' and scored a coincidental false PASS verifying no real content (eval_037).

The fix blanks the fixed trigram before numeral extraction, so it can only ever REMOVE a
spurious key, never add one. These tests lock: the idiom yields no numeral; a genuine
standalone 'moja' still yields 1 (no over-strip); and the three real eval_* cases land in
the qualitative_number_no_numeric_key exclusion bucket. Cases mirror the actual findings so
a regression re-introducing the junk key fails here.
"""
from chike.scoring import extract_numbers, scorer_reliability, score_question


# --- extract_numbers: idiom yields no numeral, genuine 'moja' still does ------

def test_idiom_moja_kwa_moja_yields_no_numeral():
    # "...pays TRA directly..." — the idiom must not contribute the numeral 1.
    assert '1' not in extract_numbers("mnunuzi anailipa TRA moja kwa moja")


def test_standalone_moja_still_counts_as_one():
    # Guard against over-stripping: a genuine quantity 'moja' must still yield 1.
    assert '1' in extract_numbers("mwaka moja tu")


def test_idiom_and_genuine_moja_coexist():
    # The idiom is blanked but a separate genuine 'moja' in the same text still counts.
    nums = extract_numbers("analipa moja kwa moja, lakini ana mtoto moja")
    assert '1' in nums


def test_idiom_does_not_disturb_other_numbers():
    # Real figures elsewhere in the same text are untouched.
    nums = extract_numbers("anakata asilimia 3 na kuipeleka TRA moja kwa moja")
    assert '3' in nums
    assert '1' not in nums


# --- reliability: the three real eval_* cases now classify honestly ----------

def test_eval_134_qualitative_penalty_flagged_unreliable():
    # eval_134: the authoritative answer is qualitative ("fines + interest, confirm with
    # TRA — amounts change each Finance Act"). Its only numeral key was the idiom '1'.
    q = {
        "answer_type": "penalty",
        "correct_answer_sw": ("TRA inatoza faini na riba kwenye SDL iliyochelewa. Kiasi "
                              "maalum kinapaswa kuthibitishwa moja kwa moja na TRA kwenye "
                              "tra.go.tz kwani kinaweza kubadilika baada ya Finance Act ya "
                              "kila mwaka. Lipa SDL ikiwa na PAYE ifikapo siku ya 7."),
        "correct_answer_en": "",
    }
    reliable, reason = scorer_reliability(q, "TRA inaweza kuongeza riba. Thibitisha na TRA.")
    assert reliable is False
    assert reason == 'qualitative_number_no_numeric_key'


def test_eval_217_no_fixed_number_flagged_unreliable():
    # eval_217: "the exact headcount is not officially confirmed — don't rely on a number."
    q = {
        "answer_type": "number",
        "correct_answer_sw": ("Kiwango kamili cha idadi ya wafanyakazi kinachohitaji afisa "
                              "maalum wa usalama hakijathibitishwa rasmi kutoka vyanzo vya "
                              "OSHA. Usitegemee namba maalum — thibitisha mahitaji yako "
                              "moja kwa moja na OSHA (osha.go.tz)."),
        "correct_answer_en": "",
    }
    reliable, reason = scorer_reliability(q, "OSHA haiweki kiwango maalum. Thibitisha na OSHA.")
    assert reliable is False
    assert reason == 'qualitative_number_no_numeric_key'


def test_eval_037_entity_answer_no_longer_junk_passes():
    # eval_037: the answer is an ENTITY ("qualifying buyer"), mislabeled 'number'. Before
    # the guard, gold and model both carried the idiom and "matched" on the junk '1' — a
    # false PASS. Now it is honestly excluded as unscorable by number-overlap.
    q = {
        "answer_type": "number",
        "correct_answer_sw": ("Mnunuzi anayehitimu (qualifying buyer). Mnunuzi anakata "
                              "sehemu ya VAT kutoka malipo na anailipa TRA moja kwa moja, "
                              "bila kupitia msambazaji. Msambazaji anapokea tu sehemu "
                              "iliyobaki ya VAT."),
        "correct_answer_en": "",
    }
    gen = "Mnunuzi anayehitimu ndiye anayepeleka VAT iliyozuiwa moja kwa moja kwa TRA."
    reliable, reason = scorer_reliability(q, gen)
    assert reliable is False
    assert reason == 'qualitative_number_no_numeric_key'
