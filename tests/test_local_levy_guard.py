# -*- coding: utf-8 -*-
"""R17 step 3: wire the local-levy probes so a future narrowing cannot silently break the guard.

TWO NARROWINGS HAPPENED ON 2026-08-25 and each one could have gone too far. This file pins both
directions so the next person to touch `minimum_turnover_tax`'s wrong_patterns finds out
immediately.

  1. The bare `0.3%` / `asilimia 0.3` / `0.3 percent` patterns matched with NO topical scoping, so
     a CORRECT council-service-levy body quoting the statutory 0.3% CAP (Cap 290 s.7(1)(u)) was
     flagged as a minimum-turnover-tax violation. Narrowed to turnover-tax context.
  2. Found by probe llp_08 in the same session: the 0.5 patterns escaped only "kutoka asilimia
     0.5" / "from 0.5", not **"ilikuwa asilimia 0.5"** — the plainest Swahili way to say "it WAS
     0.5%", which is what the locked fact itself asserts. A correct historical statement was being
     flagged.

**A narrowing that only proves the false positive is gone is indistinguishable from disabling the
guard.** llp_09 and llp_10 exist for exactly that: a plain present-tense "is 0.5%" must still fire.
"""
import json
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, 'scripts'))
PROBES = os.path.join(REPO, 'eval', 'fidelity', 'local_levy_probes.jsonl')


def _rows():
    rows = [json.loads(l) for l in open(PROBES, encoding='utf-8') if l.strip()]
    assert rows, 'local_levy_probes.jsonl loaded ZERO rows — a silent empty load would make every '\
                 'test below vacuously pass (R20)'
    return rows


def _facts():
    import check_locked_facts
    return check_locked_facts.load_locked_facts(
        os.path.join(REPO, 'scripts', 'locked_facts.json'))


@pytest.mark.parametrize('row', _rows(), ids=lambda r: r['id'])
def test_local_levy_probe_behaves_as_specified(row):
    import check_locked_facts
    flags = check_locked_facts.check_pair(row, _facts())
    if row['expect'] == 'flag':
        assert flags, (
            f"{row['id']} MUST flag and did not — the guard has been narrowed into uselessness. "
            f"{row['guards_against']}")
    else:
        assert not flags, (
            f"{row['id']} must stay CLEAN and was flagged by "
            f"{[f['wrong_pattern'] for f in flags]}. {row['guards_against']}")


def test_both_directions_are_represented():
    """Positive-only certifies a guard that flags everything; negative-only certifies one that
    flags nothing. R26 requires both, so the file itself is checked for both."""
    rows = _rows()
    assert sum(1 for r in rows if r['expect'] == 'flag') >= 2
    assert sum(1 for r in rows if r['expect'] == 'clean') >= 2


def test_the_five_local_levy_facts_are_present_and_state_no_amount():
    """The reclassification: a council-set fee has no national amount, so the fact names the
    office and the rule. If someone later encodes a market-dues or licence AMOUNT, this fails."""
    facts = json.load(open(os.path.join(REPO, 'scripts', 'locked_facts.json'), encoding='utf-8'))
    for key in ('council_service_levy_is_a_cap_not_a_rate',
                'council_service_levy_non_corporate_conflict',
                'market_dues_no_national_amount', 'market_dues_exemptions',
                'business_licence_fee_national_schedule_local_collection'):
        assert key in facts, f'{key} missing from locked_facts.json'
        assert facts[key].get('primary_source'), f'{key} has no primary_source'

    # Market dues and licence fees must carry NO figure — naming the office is the answer.
    for key in ('market_dues_no_national_amount',
                'business_licence_fee_national_schedule_local_collection'):
        text = facts[key]['fact']
        assert 'TZS' not in text, (
            f'{key} states a TZS amount. A council-set fee has no national amount; encoding one '
            f'would be wrong for every district but at most one.')
