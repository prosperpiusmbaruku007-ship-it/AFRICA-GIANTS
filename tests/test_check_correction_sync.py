"""Wires scripts/check_correction_sync.py into the normal test-suite gate, and proves it
FIRES on the exact defect it exists to catch and does NOT fire on a clean case -- R26.

Context: this checker was built 2026-09-04 after `efd_not_every_business` was found
serving stale, previously-fabricated content for five weeks with nothing catching it
(check_facts_index_sync.py verifies REACHABILITY, not content correctness, for any
fact outside FACT_GROUPS). Its first run (no negation filter) flagged 8 of 51 corrected
facts; checked by hand, 7 were false positives -- the fact's own wrong_patterns regex
matching inside a sentence that correctly NAMES the wrong claim only to reject it
("X is WRONG", "NOT X", "hakuna X"). The negation-window filter this file tests exists
because of that finding, not speculatively.
"""
import re

from scripts.check_correction_sync import (
    _has_nearby_negation,
    check,
)


def test_negation_cue_nearby_is_detected():
    """Unit-level positive control: a wrong-pattern match sitting right next to its own
    rejection ('... figures are WRONG.') must be recognised as negated."""
    text = "Both TZS 26,000 and TZS 27,000 'personal relief' figures are WRONG."
    m = re.search(r"TZS 27,000", text)
    assert _has_nearby_negation(text, m)


def test_no_negation_cue_is_the_clean_negative_control():
    """Unit-level negative control: the SAME kind of match, with no negation word
    anywhere nearby, must NOT be flagged as negated -- otherwise the filter would
    swallow every real defect along with the false positives it exists to remove."""
    text = ("biashara ndogo yenye mauzo chini ya TZS 11,000,000 kwa mwaka na "
            "isyosajiliwa VAT inaweza kutumia risiti za mkono badala ya EFD")
    m = re.search(r"chini ya TZS 11,000,000", text)
    assert not _has_nearby_negation(text, m)


def test_the_control_fires_on_the_known_live_defect():
    """R26: plant the exact thing the control exists to catch. MUST block.
    efd_not_every_business's CONCISE rendering was stale in the deployed index for five
    weeks (corrected 2026-08-29, fixed at the source 2026-09-03/04 in 951fb67, not yet
    shipped) -- as of this repo's currently-deployed kaggle/rag_facts_text.json, it is
    STILL the pre-fix text, so this MUST still be flagged today. When the 951fb67 regen
    ships, this test will start failing and should be updated -- that flip IS the
    signal, per this project's established pattern for exactly this shape of test."""
    ok, report = check()
    stale_keys = {r["key"] for r in report["stale_wrong_pattern"]}
    assert "efd_not_every_business" in stale_keys, (
        "efd_not_every_business no longer flagged -- if the 951fb67 regen shipped, this "
        "is the expected outcome and this test should be updated to confirm it does NOT "
        "appear here instead. If the regen has not shipped, the control just went inert."
    )
    assert ok is False


def test_the_control_does_not_fire_on_a_correct_rejection():
    """R26: give it a clean case. MUST pass. A control that only ever fires cannot be
    distinguished from one that is simply overbroad. paye_personal_relief's row
    explicitly says both wrong figures 'are WRONG' -- the exact shape that produced 7 of
    8 false positives on this checker's first, unfiltered run."""
    ok, report = check()
    stale_keys = {r["key"] for r in report["stale_wrong_pattern"]}
    negated_keys = {r["key"] for r in report["negated_mention"]}
    assert "paye_personal_relief" not in stale_keys
    assert "paye_personal_relief" in negated_keys


def test_all_seven_known_false_positives_are_negated_not_stale():
    """The full set found on the unfiltered first run, verified by hand -- see
    eval/results/correction_sync_negation_check_2026_09_04.json. Regression coverage
    for all seven, not just one representative, since each has a different pattern
    shape (bare figure, cross-sentence span, proximity pattern, negative lookahead,
    bare substring)."""
    ok, report = check()
    stale_keys = {r["key"] for r in report["stale_wrong_pattern"]}
    negated_keys = {r["key"] for r in report["negated_mention"]}
    known_false_positives = {
        "paye_personal_relief", "p45_not_tanzanian", "stamp_duty_property_transfer",
        "paye_nonresident_flat_rate", "wcf_disease_reporting_deadline",
        "permit_class_d_does_not_exist", "vat_threshold_200m_july2024_increase",
    }
    assert not (known_false_positives & stale_keys), (
        f"{known_false_positives & stale_keys} regressed from negated_mention back to "
        f"stale_wrong_pattern -- the negation filter stopped protecting a known case."
    )
    assert known_false_positives <= negated_keys
