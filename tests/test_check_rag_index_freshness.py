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


def test_against_live_repo_state_is_stale_pending_the_ext_31_regen():
    """Sanity check against the ACTUAL repo, not a synthetic graph. SIXTH flip, same
    mechanism as all five before it (2026-09-03 ok=False->True after efe5956; ok=True->False
    after 951fb67 changed facts with no matching regen; ok=False->True after 0be8662 shipped
    951fb67's fixes for real; ok=True->False after 9c43143/467115b staged two content fixes;
    ok=False->True after the 2026-09-24 regen shipped both at once in 1d59a06).

    THIS FLIP: ext_31's ask-alignment rewrite (2026-09-24) added
    OSHA_safety_officer_threshold to CONCISE_BILINGUAL_FACTS, so
    precompute_rag_embeddings.py is now newer than the committed index. The fact itself was
    already CORRECT -- this is a REACH defect, not a content error: the served row was the
    `key: value` fallback, English-first and label-led, measured at BOUNDARY (rank 4-16) for
    the real user phrasing while the live reply asserted exactly the phrasing the fact's own
    text forbids. Verified offline: exactly one row changes (86), 183 rows before and after,
    all 14 bucket-E needles still resolve to exactly one row.

    AND THE FLIP ITSELF IS THE POINT, AGAIN. The previous version of this test told its
    maintainer precisely what to do in this situation -- "stage it and ship it in the next
    R15 run, then flip this back to `assert ok is False` until it does" -- and it fired on a
    pre-push hook, on the push that staged the change, before anything could ship stale.
    That is the control working, not an obstacle: an oscillating assertion whose two states
    are BOTH meaningful is the opposite of the R17 hazard (a test that instructs maintainers
    not to fix a real defect). Each flip records whether a staged fix has actually reached
    the deployed artifact or is still sitting at the source -- the exact failure mode this
    check exists for, after five weeks of a stale citation hid behind three green checks.

    FLIPS BACK TO `assert ok is True` when the founder runs kaggle/regenerate_rag_e5.py and
    the index is dual-committed (R15 steps 1-4). Until then STALE is the honest state and
    this test asserting it is the only thing tracking that the rewrite is not live.
    """
    ok, report = check(repo_dir=REPO)
    assert ok is False, (
        f"the live repo reports FRESH: {report}. If the ext_31 regen has now shipped, that "
        "flip IS the signal -- update this test to assert ok is True and rename it, and "
        "confirm live that ext_31 reaches and the reply no longer says 'afisa maalum'.")
    assert "scripts/precompute_rag_embeddings.py" in report["stale_inputs"], (
        f"expected the embedding builder to be the stale input; got {report['stale_inputs']}")
    assert report["artifacts_diverged"] is False, (
        "the two index directories disagree -- a different defect from the pending regen, "
        "and one the R15 dual-commit step exists to prevent")
