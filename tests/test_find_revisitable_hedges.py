# -*- coding: utf-8 -*-
"""Regression tests for scripts/find_revisitable_hedges.py.

test_pension_substring_does_not_misroute_a_suspension_mention is the specific bug found live
2026-09-02: a bare `kw in blob` check matched the nssf keyword 'pension' inside the word
"suspension" in efd_tra_closure_authority's own fact text, routing a pure TRA/EFD fact to the
nssf topic directory. Fixed with a leading-word-boundary regex; this test is the proof it stays
fixed.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, 'scripts'))

import find_revisitable_hedges as h  # noqa: E402


def test_pension_substring_does_not_misroute_a_suspension_mention():
    topic = h._guess_topic(
        'efd_tra_closure_authority',
        'Enforcement actions can include suspension of EFD device/licence, and closure of '
        'business premises.')
    assert topic == 'tra', (
        f'expected tra (the real topic), got {topic!r} -- "pension" matched inside '
        f'"suspension" again')


def test_a_real_standalone_pension_mention_still_routes_to_nssf():
    topic = h._guess_topic('some_fact_key', 'employer must remit the employee pension share')
    assert topic == 'nssf'


def test_underscore_prefix_keywords_still_match_at_string_start():
    # 'vat_', 'efd_', 'company_' are intentional PREFIX matches (no trailing boundary, since
    # `_` and the following letter are both \w characters and would never satisfy trailing \b).
    assert h._guess_topic('vat_registration_threshold', '') == 'tra'
    assert h._guess_topic('company_registration_fee_1', '') == 'brela'


def test_no_topic_returns_none_not_a_wrong_guess():
    assert h._guess_topic('totally_unrelated_key', 'nothing matches any keyword here') is None


def test_section_403_does_not_false_trigger_the_blocked_signal():
    # The second bug found live 2026-09-02, same session: brela_striking_off_non_filing's own
    # verified_by says "R.E.2023 renumbers to s.403" -- a bare '403' substring check flagged an
    # already well-cited, non-blocked fact as a tooling-blocked hedge.
    assert h._BLOCKED_SIGNAL.search('R.E.2023 renumbers to s.403 (section number)') is None


def test_real_403_forbidden_phrasings_still_match():
    for text in ("tanzlii.org 403'd on automated fetch",
                 'not a 403 or a timeout',
                 "direct TanzLII PDF fetch 403'd; recommend re-confirming",
                 'HTTP 403 Forbidden'):
        assert h._BLOCKED_SIGNAL.search(text), f'should have matched: {text!r}'
