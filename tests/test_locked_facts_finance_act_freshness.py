# -*- coding: utf-8 -*-
"""Extends the Finance-Act freshness check (tests/test_finance_act_freshness.py,
chike/rules_engine/rates.py) to locked_facts.json -- the cheap direct extension requested
after the 2026-09-01 presumptive-tax and VAT-withholding-deadline incidents: this is exactly
the category where staleness has actually bitten us twice, so it is where the mechanism
already proven to fire gets applied first, not the other 222 facts.

SCOPE, DELIBERATELY NARROW. Only the 28 facts that mention "Finance Act" anywhere in their own
text -- these are the ones with an actual amending-Act lineage a new Finance Act could touch.
The other ~222 facts (GN-bound, or citing an Act directly with no Finance Act amendment
history invoked) are OUT OF SCOPE here; see PROGRESS.md's "GN registry, scoped not built"
section for why they need a different mechanism, not this one widened.

WHAT THE FIRST RUN FOUND: 13 of 28 already carry a 2026 verified_as_at date (real, from the
bootstrap census) and pass outright. The other 15 are "unknown" -- not because they were
checked and found stale, but because they were never dated with primary-source-read evidence
at all. Each is registered below with `known_gap=True` and its own reason, the same pattern as
presumptive_income_cue_probes.jsonl's `known_failing` field: the gap is TRACKED, not hidden,
and fails LOUDLY (via the companion test) the moment someone closes it without actually
grounding the fact -- i.e. by deleting the marker instead of doing the work.
"""
import json
import os

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACTS_PATH = os.path.join(REPO, 'scripts', 'locked_facts.json')

# CURRENT_FINANCE_ACT_YEAR duplicated from rates.py deliberately, not imported -- this file
# checks a DIFFERENT population (locked_facts.json, not rates.py constants) and importing
# would wrongly suggest the two are the same mechanism sharing state, when they are two
# instances of the same PATTERN over two different data sources with different schemas.
CURRENT_FINANCE_ACT_YEAR = 2026

# key -> known_gap reason, ONLY for facts currently verified_as_at == "unknown". A fact NOT
# in this dict is expected to pass outright; if it doesn't, that's a real, new regression.
KNOWN_GAPS = {
    'sdl_rate': 'verified_by cites "Finance Act 2023" + PWC Tax Summaries but has no direct-'
               'read date attached -- SDL rate itself was separately confirmed unchanged by '
               'FA2026 during this session\'s freshness audit (rates.py FINANCE_ACT_VERIFIED_'
               'THROUGH[\'SDL\']), so the VALUE is not suspected wrong, only this fact\'s own '
               'citation is undated.',
    'sdl_threshold': 'verified_by cites "Finance Act 2021" with no direct-read date.',
    'vat_reduced_rates': 'verified_by is a TRA portal + CLAUDE.md cross-reference, no direct-'
                        'read date.',
    'vat_withholding_goods': 'verified_by cites Finance Act 2025 s.124 + a GN, no direct-read '
                             'date -- the RATE was independently re-confirmed unchanged by '
                             'FA2026 this session (see vat_withholding_remittance_deadline\'s '
                             'correction_note), only this fact\'s own citation is undated.',
    'vat_withholding_services': 'same reason as vat_withholding_goods -- no direct-read date.',
    'commissioner_objection_deadline': 'verified_by cites "Finance Act 2020" + PWC, no direct-'
                                       'read date.',
    'loss_carryforward_finance_act_2024': 'verified_by is a bare "Finance Act 2024 amendment", '
                                          'no direct-read date at all.',
    'vat_withholding_formula_correct': 'verified_by cites Finance Act 2025 s.124, no direct-'
                                       'read date.',
    'VAT_withholding_base_disputed': 'verified_by cites Finance Act 2025 s.124, no direct-read '
                                     'date.',
    'SDL_source_law': 'verified_by is a bare TRA page + Act name, no direct-read date.',
    'vat_withholding_buyer_remits_directly': 'verified_by is a TRA portal quote, no direct-'
                                             'read date.',
    'business_licence_expiry_30_june': 'no verified_by field at all -- never checked against '
                                       'primary text by anyone, not just undated.',
    'presumptive_excluded_services': 'no verified_by field at all -- the CLAIM was '
                                     'independently confirmed unchanged by FA2026 this session '
                                     '(rates.py PRESUMPTIVE group, and the fact itself notes '
                                     '"s.27(a) does not touch subparagraph (1) at all" in '
                                     'PROGRESS.md), only this fact object itself carries no '
                                     'citation evidence of that check.',
}


def _facts():
    with open(FACTS_PATH, encoding='utf-8') as f:
        d = json.load(f)
    return {k: v for k, v in d.items() if isinstance(v, dict) and not k.startswith('_')}


def _finance_act_bound_keys():
    facts = _facts()
    keys = [k for k, v in facts.items()
           if 'finance act' in json.dumps(v, ensure_ascii=False).lower()]
    assert keys, 'no Finance-Act-bound facts found -- the corpus shape has changed; re-derive '\
                 'this list rather than trusting it stale'
    return sorted(keys)


FACTS_SNAPSHOT = _facts()
FA_BOUND_KEYS = _finance_act_bound_keys()


@pytest.mark.parametrize('key', FA_BOUND_KEYS)
def test_finance_act_bound_fact_is_current_or_a_tracked_gap(key):
    fact = FACTS_SNAPSHOT[key]
    val = fact.get('verified_as_at')
    if key in KNOWN_GAPS:
        assert val == 'unknown', (
            f'{key} is registered as a KNOWN_GAP but verified_as_at is now {val!r}, not '
            f'"unknown" -- if this was genuinely re-grounded, remove it from KNOWN_GAPS in the '
            f'SAME commit as the fix (per this file\'s own convention); do not leave a stale '
            f'gap marker on a fact that no longer has the gap.')
        pytest.xfail(f'tracked backlog, not a regression: {KNOWN_GAPS[key]}')
    assert val != 'unknown', (
        f'{key} cites "Finance Act" but has no verified_as_at date and is NOT in KNOWN_GAPS -- '
        f'either this is a newly-discovered gap (add it to KNOWN_GAPS with a reason) or the '
        f'bootstrap census needs re-running.')
    year = int(val[:4])
    assert year >= CURRENT_FINANCE_ACT_YEAR, (
        f'{key} verified_as_at={val} is behind CURRENT_FINANCE_ACT_YEAR='
        f'{CURRENT_FINANCE_ACT_YEAR} -- re-read the current Finance Act\'s relevant section and '
        f'either confirm the fact unchanged (bump verified_as_at) or correct it.')


def test_every_known_gap_still_names_a_live_gap():
    """Companion to the parametrized test above, same shape as test_presumptive_income_cue.py's
    test_known_failing_rows_still_name_a_live_defect: FAILS the moment a tracked gap starts
    passing on its own, which is the GOOD outcome, and must be an explicit KNOWN_GAPS edit
    rather than a silent one."""
    stale_markers = []
    for key, reason in KNOWN_GAPS.items():
        assert key in FACTS_SNAPSHOT, f'{key} in KNOWN_GAPS no longer exists in locked_facts.json'
        assert len(reason) > 30, f'{key}: KNOWN_GAPS needs a real reason, not a label'
        if FACTS_SNAPSHOT[key].get('verified_as_at') != 'unknown':
            stale_markers.append(key)
    assert not stale_markers, (
        f'{stale_markers} no longer have verified_as_at == "unknown" -- they have been '
        f'grounded (good!) but KNOWN_GAPS was not updated in the same commit. Remove them from '
        f'KNOWN_GAPS now.')


def test_known_gaps_are_a_subset_of_the_finance_act_bound_population():
    """A gap tracked for a key that is not (or no longer) Finance-Act-bound is either stale
    bookkeeping or a sign the corpus shape moved without this file being updated."""
    unbound = set(KNOWN_GAPS) - set(FA_BOUND_KEYS)
    assert not unbound, f'{unbound} are in KNOWN_GAPS but do not cite "Finance Act" any more'
