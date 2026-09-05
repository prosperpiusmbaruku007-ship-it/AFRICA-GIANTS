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
    check_facts_and_index,
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


def test_the_former_live_defect_is_now_clean_not_just_absent():
    """THIRD FORM of this test, and the flip IS the signal, exactly as its own prior
    docstring predicted. efd_not_every_business's stale CONCISE rendering (five weeks
    undetected, corrected at the source 2026-09-03/04 in 951fb67) shipped for real
    2026-09-05 -- the R15 regen ran on Kaggle (kernel prospaprospa/africa-giants-rag-regen
    v2), verified, and both directories were re-committed. Against the live repo today the
    fact must now resolve CLEAN, not merely stop appearing -- 'clean' and 'unresolved'
    are different verdicts (see check_facts_and_index's report buckets), and only 'clean'
    or a non-stale bucket actually confirms the fix shipped correctly rather than the pin
    simply going dark. The PINNED needle in check_facts_index_sync.py was updated in the
    same commit as the index files (per this session's own rule: a pin describes what's
    live, updated after ship, never before) specifically so this resolves rather than
    falling into 'unresolved'."""
    ok, report = check()
    stale_keys = {r["key"] for r in report["stale_wrong_pattern"]}
    unresolved_keys = set(report["unresolved"])
    assert "efd_not_every_business" not in stale_keys
    assert "efd_not_every_business" not in unresolved_keys, (
        "efd_not_every_business is unresolved, not clean -- the PINNED needle in "
        "check_facts_index_sync.py likely still points at stale content and needs "
        "updating to match the shipped text, same as this session already did once."
    )


def test_the_control_still_fires_on_a_planted_synthetic_defect():
    """R26, reasserted now that the REAL live specimen this test used to plant against is
    fixed: a control's fire-capability must be checked with something planted, not
    retired along with the specimen that used to demonstrate it. Constructs a minimal
    in-memory (locked, index) pair reproducing the exact shape of the original defect --
    a correction_note'd fact whose wrong_patterns regex matches its OWN resolved row with
    no negation cue nearby -- and confirms check_facts_and_index() still flags it. This is
    the synthetic replacement for the retired live-defect plant, using the SAME in-memory
    core the regen gate calls (check_facts_and_index), not the file-loading check()
    wrapper, so it needs no fixture files."""
    locked = {
        "synthetic_stale_fact": {
            "fact": "placeholder",
            "correct_value": "placeholder",
            "correction_note": "corrected 2020-01-01, superseded a since-rejected figure",
            "wrong_patterns": [r"amount charged is (11|14)"],
        }
    }
    # Deliberately contains none of _NEGATION_CUE's words (not/wrong/no/never/hakuna/si/
    # siyo/sio/haiwezekani/hairuhusiwi/haipaswi) -- an earlier draft of this test used
    # "the wrong figure is 11", which is self-defeating: the word "wrong" is itself a
    # negation cue, so the filter correctly (but uselessly, for this test's purpose)
    # treated the plant as a negated mention instead of a stale one.
    index = ["synthetic stale fact: the amount charged is 11 percent monthly, unchanged"]
    ok, report = check_facts_and_index(locked, index)
    stale_keys = {r["key"] for r in report["stale_wrong_pattern"]}
    assert "synthetic_stale_fact" in stale_keys
    assert ok is False
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
