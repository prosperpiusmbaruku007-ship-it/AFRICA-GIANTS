# -*- coding: utf-8 -*-
"""R26 control-fires test for scripts/check_rag_index_freshness.py: plant the exact
staleness this script exists to catch (must FAIL) and a clean, up-to-date state (must
PASS), against a synthetic commit graph rather than live repo history -- so the test does
not depend on git state changing under it as the real repo moves forward.

The synthetic graph, as a DAG (letters are commit SHAs, '<-' is 'is a parent of'):

    A <- B <- C          A: original facts + regen both built
              |
              +-- D      D: facts edited again AFTER C (the regen), on top of C

`is_ancestor(x, y)` below encodes exactly that graph: is_ancestor('A','C') is True,
is_ancestor('D','C') is False (D is NOT an ancestor of C -- C came first).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "scripts"))

from check_rag_index_freshness import check, FRESHNESS_INPUTS, DEPLOYED_ARTIFACTS  # noqa: E402

# DAG: A is the common root; B and C descend from A in a line; D descends from C.
# is_ancestor(x, y) is True iff x precedes y on this line.
_ORDER = ["A", "B", "C", "D"]


def _is_ancestor(x, y):
    if x == y:
        return True
    return _ORDER.index(x) < _ORDER.index(y)


def _make_last_touch(shas_by_path):
    return lambda p: shas_by_path.get(p)


def _commits_since(_old, _new, _path):
    return ["<fake commit summary>"]


def test_stale_facts_after_the_regen_commit_are_caught():
    """Plant the exact incident this script was built for: locked_facts.json's last touch
    (D) is NOT an ancestor of the deployed artifacts' build commit (C) -- i.e. the fact
    changed after the index was built. Must FAIL."""
    shas = {p: "C" for p in FRESHNESS_INPUTS + DEPLOYED_ARTIFACTS}
    shas["scripts/locked_facts.json"] = "D"  # edited after the regen

    ok, report = check(
        is_ancestor_fn=_is_ancestor,
        last_touch_fn=_make_last_touch(shas),
        commits_since_fn=_commits_since,
    )
    assert ok is False, "planted staleness did not fire -- the control is INERT"
    assert "scripts/locked_facts.json" in report["stale_inputs"]


def test_artifact_directories_that_disagree_are_caught():
    """Plant a divergence between kaggle/ and chike-inference/ copies (R15's atomic-
    upload rationale exists precisely because this can happen). Must FAIL."""
    shas = {p: "C" for p in FRESHNESS_INPUTS}
    for p in DEPLOYED_ARTIFACTS:
        shas[p] = "C"
    shas["chike-inference/rag_embeddings.npy"] = "B"  # older than the others

    ok, report = check(
        is_ancestor_fn=_is_ancestor,
        last_touch_fn=_make_last_touch(shas),
        commits_since_fn=_commits_since,
    )
    assert ok is False, "planted artifact divergence did not fire -- the control is INERT"
    assert report["artifacts_diverged"] is True


def test_a_fresh_index_built_after_every_input_change_passes_clean():
    """Give it a state where the artifacts' build commit (C) already contains every
    input's last change (A, B -- both ancestors of C). Must PASS -- a control that only
    ever fires would be exactly as useless as one that never does."""
    shas = {p: "C" for p in DEPLOYED_ARTIFACTS}
    shas["scripts/locked_facts.json"] = "B"
    shas["scripts/precompute_rag_embeddings.py"] = "A"

    ok, report = check(
        is_ancestor_fn=_is_ancestor,
        last_touch_fn=_make_last_touch(shas),
        commits_since_fn=_commits_since,
    )
    assert ok is True, f"clean up-to-date state was wrongly flagged stale: {report}"
    assert report["stale_inputs"] == {}
    assert report["artifacts_diverged"] is False


def test_missing_git_history_is_reported_distinctly_from_staleness():
    """A file git has no history for (None) is a different failure than a stale one --
    conflating them would hide a real setup bug behind a staleness message."""
    shas = {p: "C" for p in FRESHNESS_INPUTS + DEPLOYED_ARTIFACTS}
    shas["scripts/locked_facts.json"] = None

    ok, report = check(
        is_ancestor_fn=_is_ancestor,
        last_touch_fn=_make_last_touch(shas),
        commits_since_fn=_commits_since,
    )
    assert ok is False
    assert report["missing_inputs"] == ["scripts/locked_facts.json"]


def test_against_live_repo_state_reports_the_known_current_gap():
    """Sanity check against the ACTUAL repo, not a synthetic graph: as of this test's
    authoring (2026-09-03) locked_facts.json has moved since the last real regen
    (b017aac, 2026-08-26) -- this must currently report NOT ok. When R15 actually runs
    and both directories are re-committed, this test will start failing and should be
    updated to assert ok=True at that point -- that flip is itself the signal the regen
    landed, not a bug in the test."""
    ok, report = check(repo_dir=REPO)
    assert ok is False, (
        "the live repo now reports FRESH -- if R15 ran and both kaggle/ and "
        "chike-inference/ were recommitted, update this test to assert ok is True")
    assert "scripts/locked_facts.json" in report["stale_inputs"]
