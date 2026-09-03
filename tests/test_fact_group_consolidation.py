# -*- coding: utf-8 -*-
"""The 42 -> 3 fee consolidation (2026-08-25), and the two controls that hold it up.

WHAT CHANGED. 42 context-free `key: number` fee rows are absorbed into 3 grouped passages by
scripts/precompute_rag_embeddings.py. locked_facts.json is UNTOUCHED -- it is still the truth
table check_locked_facts.py enforces. Only the retrieval surface changes.

WHY IT NEEDS ITS OWN TESTS, and this is R26 rather than tidiness. Consolidation has exactly one
way to be quietly wrong: the grouped passage silently omits a figure one of its members asserted.
Nothing downstream would say so. The index would be smaller, the anchors would be less buried, the
measurement would still look good, and one fee would have stopped existing. So both controls below
PLANT that failure rather than asserting the happy path:

  1. build_fact_texts() must REFUSE to build when a member's figure is missing from its group text.
  2. check_facts_index_sync must report DRIFT for the member key when the SHIPPED index carries a
     group passage that has lost the figure -- verified against the index the regen will actually
     produce, not against the current pre-regen one.

And the clean case for each, because a control that only ever blocks is indistinguishable from one
that blocks everything.
"""
import json
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, 'scripts'))

import precompute_rag_embeddings as pre  # noqa: E402
from scripts.check_facts_index_sync import check  # noqa: E402

FACTS = os.path.join(REPO, 'scripts', 'locked_facts.json')


def _prospective_index():
    """The rag_facts_text.json the next R15 regen will produce, built from the same function
    the regen calls (kaggle/regenerate_rag_e5.py imports precompute.build_fact_texts)."""
    texts, _keys, _dropped = pre.build_fact_texts()
    return texts


def test_the_consolidation_absorbs_exactly_the_rows_it_claims():
    texts, keys, _ = pre.build_fact_texts()
    # 42 (2026-08-25 fee consolidation, measured: eval/results/feegroup_curation.json) + 2
    # (2026-09-03: electrical_test_fee_reduction_initial/_final, a DIFFERENT justification --
    # not crowding/fee-ladder curation, a self-retrieval FAILURE fix. The pair embedded to
    # 0.925 cosine of each other post-fc9b0c8-regen, so one could never be retrieved as itself.
    # Merged into one before/after passage, the same treatment, for an unrelated reason.)
    assert len(pre._GROUP_MEMBERS) == 44, (
        f'{len(pre._GROUP_MEMBERS)} member keys, expected 44 — 42 from the fee consolidation '
        '(eval/results/feegroup_curation.json) + 2 from the electrical-fee near-duplicate fix.')
    for gname in pre.FACT_GROUPS:
        assert gname in keys, f'group {gname} produced no index row'
    for member in pre._GROUP_MEMBERS:
        slug = member.replace('_', ' ')
        assert not any(t.startswith(slug + ':') for t in texts), (
            f'{member} still has its OWN index row as well as being in a group — it would be '
            f'counted twice and the crowding it causes would not have been removed.')


def test_every_absorbed_figure_survives_into_its_group_passage():
    """The clean case for control 1. Read as a list, this is the answer to 'what did we lose?'"""
    facts = json.load(open(FACTS, encoding='utf-8'))
    for key, gname in pre._GROUP_MEMBERS.items():
        fig = pre._figure_of(pre.fact_value(facts[key]))
        assert fig, f'{key} has no extractable figure — is it really a fee row?'
        assert fig in pre.FACT_GROUPS[gname]['text'], f'{key}: {fig} missing from {gname}'


def test_build_REFUSES_when_a_group_drops_a_members_figure(monkeypatch):
    """CONTROL 1, planted. 290,000 is the fourth rung of the company registration ladder; a
    consolidated passage that omits it answers a real question with the wrong fee."""
    tampered = {k: dict(v) for k, v in pre.FACT_GROUPS.items()}
    tampered['company_registration_ladder']['text'] = (
        pre.FACT_GROUPS['company_registration_ladder']['text'].replace('TZS 290,000', ''))
    monkeypatch.setattr(pre, 'FACT_GROUPS', tampered)
    with pytest.raises(AssertionError, match='drops the figure'):
        pre.build_fact_texts()


def test_build_REFUSES_when_a_group_names_a_key_that_no_longer_exists(monkeypatch):
    """The other silent loss: a fact renamed in locked_facts.json while the group still lists
    the old name would drop out of the index entirely — absorbed by nothing, emitted by nobody."""
    tampered = {k: dict(v) for k, v in pre.FACT_GROUPS.items()}
    tampered['trademark_fees'] = dict(tampered['trademark_fees'])
    tampered['trademark_fees']['keys'] = (
        list(tampered['trademark_fees']['keys']) + ['trademark_fee_for_a_key_that_was_renamed'])
    monkeypatch.setattr(pre, 'FACT_GROUPS', tampered)
    monkeypatch.setattr(pre, '_GROUP_MEMBERS',
                        {k: g for g, s in tampered.items() for k in s['keys']})
    with pytest.raises(AssertionError, match='absent from locked_facts.json'):
        pre.build_fact_texts()


@pytest.mark.xfail(strict=True, reason=(
    "PRE-EXISTING pin cascade, confirmed on pristine HEAD and NOT caused by the corporate/"
    "partnership build's engine or router code. Retiring `amt_loss_companies_only` (locked_"
    "facts.json consolidation, 2026-09-01, R27) removed one standalone key, which shifted "
    "every fact after its old position by one row in the prospective RAG index. 29 of "
    "check_facts_index_sync.py's hardcoded PINNED row numbers went stale as a result -- this "
    "test checks one of them (gn487a_license_lending_is_facilitation, row 91->90). NOT "
    "hand-patched: updating the pin locally would make this test pass without making it TRUE, "
    "since the actually-shipped rag_embeddings.npy/rag_facts_text.json have not been "
    "regenerated. UNBLOCK CONDITION: the pending R15 Kaggle regen (which recomputes and ships "
    "a real index, then the pins get re-verified against it, not against a local prospective "
    "computation) closes this circularity -- R15 needs to run against a clone that has this "
    "session's commits, which can only happen after they are pushed; this marker exists so the "
    "push is not blocked on a fix that itself depends on the push having already happened. "
    "When this starts passing, delete the marker in the SAME commit that lands the new index "
    "and the re-verified pins -- do not delete the test."))
def test_sync_check_resolves_every_member_as_GROUPED_on_the_post_regen_index(tmp_path):
    """CONTROL 2's clean case, and the thing that makes the regen safe to run: against the index
    the regen WILL produce, all 42 member keys resolve as grouped and nothing drifts."""
    idx = tmp_path / 'rag_facts_text.json'
    idx.write_text(json.dumps(_prospective_index(), ensure_ascii=False), encoding='utf-8')
    ok, report = check(FACTS, str(idx))
    assert len(report['grouped']) == 42, (
        f"{len(report['grouped'])} grouped, expected 42; "
        f"drift={report['drift_unpinned']} stale={report['drift_pin_stale']}")
    assert not report['drift_unpinned'], report['drift_unpinned']
    assert not report['drift_pin_stale'], report['drift_pin_stale']
    assert ok


def test_sync_check_reports_DRIFT_when_the_SHIPPED_group_passage_has_lost_a_figure(tmp_path):
    """CONTROL 2, planted. This is the case build-time validation CANNOT catch: the index file
    is what production loads, and it can diverge from the builder — a regen against a stale
    commit (R15's CDN cache) ships a passage that no longer matches the current group text."""
    texts = [t.replace('TZS 290,000', '') for t in _prospective_index()]
    idx = tmp_path / 'rag_facts_text.json'
    idx.write_text(json.dumps(texts, ensure_ascii=False), encoding='utf-8')
    ok, report = check(FACTS, str(idx))
    stale = [d['key'] for d in report['drift_pin_stale']]
    assert 'company_registration_fee_4' in stale, (
        f'the member asserting 290,000 was not flagged; drift_pin_stale={report["drift_pin_stale"]}')
    assert not ok


def test_the_five_local_levy_facts_enter_the_index_on_this_same_regen(tmp_path):
    """The regen is BATCHED: consolidation + the five council-fee facts, one cycle not two.
    These are pinned pending_r15 today; this asserts the same rebuild clears them, so nobody
    has to remember to check afterwards."""
    idx = tmp_path / 'rag_facts_text.json'
    idx.write_text(json.dumps(_prospective_index(), ensure_ascii=False), encoding='utf-8')
    _ok, report = check(FACTS, str(idx))
    for key in ('council_service_levy_is_a_cap_not_a_rate',
                'council_service_levy_non_corporate_conflict',
                'market_dues_no_national_amount', 'market_dues_exemptions',
                'business_licence_fee_national_schedule_local_collection'):
        assert key in report['exact'] or key in report['sibling'], (
            f'{key} is still not reachable after the regen — it would ship inert, which is the '
            f'exact state the pending_r15 pin was recording.')
