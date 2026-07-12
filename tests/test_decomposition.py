"""Tests for chike.decomposition — the ported production decompose_query.

Covers the enumeration patterns proven in v15: single-question pass-through,
'?'-splitting, 'na pia' connectors, and 'A, B, na C' enumeration lists that carry
preamble context to each item. Also pins the Q6 numbered-'?' behaviour so the
context-loss limitation is documented, not silently assumed away.
"""
from chike.decomposition import decompose_query


# --- Single question: no decomposition -------------------------------------

def test_single_question_is_not_split():
    assert decompose_query("SDL rate Tanzania ni asilimia ngapi?") == [
        "SDL rate Tanzania ni asilimia ngapi?"
    ]


def test_comma_list_without_verb_is_not_over_split():
    # Ordinary prose listing bodies, no calc/list verb -> stays whole (conservative).
    msg = "Kampuni inalipa BRELA, TRA na NSSF kila mwaka."
    assert decompose_query(msg) == [msg]


# --- '?' splitting ----------------------------------------------------------

def test_two_questions_split_on_question_marks():
    parts = decompose_query("BRELA ada ni ngapi? NSSF ni asilimia ngapi?")
    assert parts == ["BRELA ada ni ngapi?", "NSSF ni asilimia ngapi?"]


# --- 'na pia' connector -----------------------------------------------------

def test_na_pia_connector_splits_into_two():
    parts = decompose_query("Nina wafanyakazi 12, SDL inalipwa vipi na pia NSSF ninahitaji?")
    assert len(parts) == 2
    assert "SDL" in parts[0]
    assert "NSSF" in parts[1]


# --- Enumeration list carries preamble context to each item -----------------

def test_enumeration_list_carries_preamble_to_each_item():
    parts = decompose_query(
        "Nina wafanyakazi 12 wenye mshahara 600,000. Nihesabie SDL, NSSF, na PAYE."
    )
    assert len(parts) == 3
    # The employee-count/salary preamble is attached to EVERY sub-query.
    for part in parts:
        assert "wafanyakazi 12" in part
        assert "600,000" in part
    assert parts[0].endswith("SDL")
    assert parts[1].endswith("NSSF")
    assert parts[2].endswith("PAYE")


# --- Q6 numbered-'?' format: splits, but context stays only on the first part -

def test_q6_numbered_questions_split_but_only_first_keeps_context():
    q6 = (
        "Kampuni yangu ina wafanyakazi 12, mshahara wa jumla wa kila mmoja TZS 600,000. "
        "(1) Ninalipa SDL kiasi gani? (2) Ninalipa NSSF kiasi gani jumla? "
        "(3) Tarehe zote mbili za malipo ni lini?"
    )
    parts = decompose_query(q6)
    assert len(parts) == 3
    # LIMITATION (documented): the numbered-'?' format hits the '?'-split path, so the
    # "12 employees / 600,000" preamble attaches ONLY to part 1 (SDL). Parts 2 & 3 lose
    # it — this is why Q6's NSSF sub-question still lacks compute context after this port.
    assert "wafanyakazi 12" in parts[0] and "600,000" in parts[0]
    assert "600,000" not in parts[1]
    assert "600,000" not in parts[2]
