# -*- coding: utf-8 -*-
"""Structural invariants for the 2026-09-01 verified_as_at bootstrap census
(scripts/bootstrap_verified_as_at.py). Does NOT re-verify any fact's legal content -- only
guards the field the census wrote so a future edit cannot silently drop or corrupt it. The
census itself is a one-time bootstrap (populate honestly or mark unknown), not a standing
check; this is the minimum tripwire that makes its result durable rather than a snapshot that
quietly rots the moment someone next edits locked_facts.json by hand.
"""
import json
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACTS_PATH = os.path.join(REPO, 'scripts', 'locked_facts.json')

_ISO_DATE = re.compile(r'^20\d{2}-\d{2}-\d{2}$')
_MONTH_YEAR = re.compile(r'^20\d{2}-[A-Z][a-z]{2}$')


def _dict_facts():
    with open(FACTS_PATH, encoding='utf-8') as f:
        d = json.load(f)
    return {k: v for k, v in d.items() if isinstance(v, dict) and not k.startswith('_')}


def test_every_dict_shaped_fact_carries_verified_as_at():
    facts = _dict_facts()
    missing = [k for k, v in facts.items() if 'verified_as_at' not in v]
    assert not missing, (
        f'{len(missing)} dict-shaped fact(s) have no verified_as_at field: {missing[:10]}... '
        f'-- every dict-shaped fact must carry one, even if the value is "unknown".')


def test_verified_as_at_is_either_unknown_or_a_real_date_shape():
    facts = _dict_facts()
    bad = []
    for k, v in facts.items():
        val = v.get('verified_as_at')
        if val == 'unknown':
            continue
        if not (isinstance(val, str) and (_ISO_DATE.match(val) or _MONTH_YEAR.match(val))):
            bad.append((k, val))
    assert not bad, (
        f'{len(bad)} fact(s) have a verified_as_at value that is neither "unknown" nor a '
        f'recognisable date shape (YYYY-MM-DD or YYYY-Mon): {bad}')


def test_a_verified_as_at_date_actually_appears_in_the_facts_own_verified_by_text():
    """The census's core honesty guarantee: a date is never accepted from anywhere but the
    verified_by string it claims to summarise. Re-derives it independently rather than
    trusting the field was written correctly the one time the census ran."""
    facts = _dict_facts()
    mismatched = []
    for k, v in facts.items():
        val = v.get('verified_as_at')
        if val == 'unknown':
            continue
        vb = v.get('verified_by', '') or ''
        if _ISO_DATE.match(val):
            if val not in vb:
                mismatched.append((k, val, vb[:100]))
        elif _MONTH_YEAR.match(val):
            year, mon = val.split('-')
            if mon.lower() not in vb.lower() or year not in vb:
                mismatched.append((k, val, vb[:100]))
    assert not mismatched, (
        f'{len(mismatched)} fact(s) have a verified_as_at date not actually present in their '
        f'own verified_by text -- the census must never infer a date from elsewhere: {mismatched}')
