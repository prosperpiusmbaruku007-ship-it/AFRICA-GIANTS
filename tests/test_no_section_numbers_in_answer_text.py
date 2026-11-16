"""R44: served Swahili text names a consolidated Act without a section number; numbers live in source metadata only.

Enforced on the prospective index (built from source), the five fixed statements and every rule-engine string. Planted
(R26): the checker must flag a real citation, must pass the amending-Act form ("2025, Kifungu 8") and a clean sentence.
"""
import importlib.util
import os

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("sweep_sc", os.path.join(REPO, "eval", "controls", "sweep_section_citations_2026_11_16.py"))
sweep = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sweep)


def test_plant_a_consolidated_act_citation_is_flagged():
    assert sweep.served_swahili_violations([("x", "Notisi ni siku 28 (ELRA, Kifungu 41).")])
    assert sweep.served_swahili_violations([("x", "(Sheria ya VAT, Vifungu 15 na 70)")])
    assert sweep.served_swahili_violations([("x", "chini ya Cap.297 kifungu 66(2)")])


def test_control_amending_act_and_clean_text_pass():
    assert not sweep.served_swahili_violations([("x", "(ELRA, kilichoongezwa na Sheria ya Marekebisho ya Sheria za Kazi, 2025, Kifungu 8)")])
    assert not sweep.served_swahili_violations([("x", "Notisi ni siku 28 (ELRA).")])
    assert not sweep.served_swahili_violations([("x", "Sheria ya Fedha 2024 Kifungu 34")])


def test_the_shipped_pre_strip_index_would_have_failed():
    """Positive control on the real population: the checker is not inert against the index it exists to police."""
    import json
    rows = json.load(open(os.path.join(REPO, "chike-inference", "rag_facts_text.json"), encoding="utf-8"))
    if len(rows) == 208 and any("ELRA, Kifungu" in r for r in rows):
        assert len(sweep.served_swahili_violations(list(enumerate(rows)))) >= 29
    else:
        pytest.skip("shipped index already regenerated without citations")


def test_served_swahili_text_has_no_consolidated_act_section_numbers():
    cwd = os.getcwd()
    try:
        bad = sweep.prove()
    finally:
        os.chdir(cwd)
    assert not bad, bad[:5]


def test_schedule_paragraph_numbers_follow_the_same_rule_and_the_checker_is_not_inert():
    """Founder's decision 2026-11-16: 'First Schedule para N' of a consolidated Act is stripped from served text like a section number."""
    assert sweep.schedule_violations([("x", "lazima aombe kwa Kamishna (First Schedule para 2(4), mpya).")])
    assert not sweep.schedule_violations([("x", "lazima aombe kwa Kamishna na aidhinishwe.")])
    import json
    rows = json.load(open(os.path.join(REPO, "chike-inference", "rag_facts_text.json"), encoding="utf-8"))
    if len(rows) == 208 and "aidhinishwe (First Schedule para 2(4), mpya)" in rows[169]:
        assert any(i == 169 for i, _ in sweep.schedule_violations(list(enumerate(rows)))), "the shipped presumptive row must be flagged"
    assert {"royalties_wht_rate", "paye_nonresident_flat_rate"} == set(sweep.ENGLISH_KEY_SCHEDULE_EXEMPT), "the exemption list changed: justify it"
