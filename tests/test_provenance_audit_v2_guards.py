# -*- coding: utf-8 -*-
"""Regression test for the stale-override guard added to
scripts/audit_locked_facts_verification_provenance_v2.py on 2026-09-02, after
`_MANUAL_KEEP_SUMMARY_ONLY['gn487a_mgeni_cap357_definition']` was found pinned to a citation
that had been replaced 9 days earlier -- the same failure shape as the 2026-08-17 stale-pins
incident (R18), just for a manual grounding override instead of an index row. The fix makes
each override carry a `guard` fragment re-checked against the CURRENT field text every run;
a guard that no longer matches must raise, not silently keep the old verdict.

Per R23/R26: a control is not trusted until proven to actually fire on the failure it exists to
catch, and to stay quiet on a case that hasn't decayed.
"""
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, 'scripts'))

import audit_locked_facts_verification_provenance_v2 as v2  # noqa: E402


def _facts():
    with open(os.path.join(REPO, 'scripts', 'locked_facts.json'), encoding='utf-8') as f:
        return json.load(f)


def test_live_guard_passes_on_the_real_current_facts():
    # Must not raise: the guards on file today are checked against the real corpus.
    live = v2._live_manual_overrides(_facts())
    assert set(live) == set(v2._MANUAL_KEEP_SUMMARY_ONLY)


def test_stale_guard_raises_instead_of_silently_passing():
    facts = _facts()
    original = dict(v2._MANUAL_KEEP_SUMMARY_ONLY['gn605a_average_increase'])
    try:
        v2._MANUAL_KEEP_SUMMARY_ONLY['gn605a_average_increase']['guard'] = (
            'this exact phrase will never appear in any verified_by field')
        try:
            v2._live_manual_overrides(facts)
            assert False, 'stale guard must raise, not silently pass'
        except AssertionError as e:
            assert 'STALE OVERRIDE' in str(e)
    finally:
        v2._MANUAL_KEEP_SUMMARY_ONLY['gn605a_average_increase'] = original


def test_override_naming_a_missing_key_raises():
    facts = _facts()
    v2._MANUAL_KEEP_SUMMARY_ONLY['__no_such_fact__'] = {
        'reason': 'planted', 'guard': 'anything'}
    try:
        try:
            v2._live_manual_overrides(facts)
            assert False, 'an override naming a nonexistent key must raise'
        except AssertionError:
            pass
    finally:
        del v2._MANUAL_KEEP_SUMMARY_ONLY['__no_such_fact__']


def test_gn487a_mgeni_cap357_definition_is_no_longer_forced_summary_only():
    """The specific decayed pin this fix closed: the fact's citation was upgraded 2026-08-31
    (direct read of GN487A s.2 and Cap.357 ss.3(1), 8-12, 30(1)(b)) but the override still said
    'verified_by is a law firm's article' for 9 more days. Confirms it is gone, not just that
    the mechanism that would catch its return exists."""
    assert 'gn487a_mgeni_cap357_definition' not in v2._MANUAL_KEEP_SUMMARY_ONLY
