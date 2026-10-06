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


def test_against_live_repo_state_is_fresh_after_the_part_xii_regen():
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

    ⭐ SEVENTH FLIP, 2026-10-05, AND THIS IS THE ONE THE CHECK WAS BUILT FOR. The R15 regen
    ran (184 facts, (184, 768), 0 self-retrieval failures, all 36 critical queries, every
    anchor unique) and the index was dual-committed in 7d46df1, which carries ext_31's
    rewrite AND the Part XII citation reversal AND rent_wht_rate.

    The Part XII row is the reason this matters: production served the REVERSED citation from
    2026-08-31 to 2026-10-05 -- five weeks -- and for most of that time this very check was
    the only thing asserting the index did not reflect its own sources.

    AND THE FLIP FIRED ON THE PRE-PUSH HOOK AGAIN, which is worth recording precisely because
    it looks like noise: `pytest tests/` passed locally BEFORE the ship commit and failed on
    push. Not a flake -- the freshness verdict is derived from `git log` of the artifacts'
    last-touch commit, so while the new index sat uncommitted in the working tree the repo
    still read STALE and this test still passed. It could only flip once the commit existed.
    A test whose state depends on committed history must be exercised by a hook that runs at
    push time; a pre-commit run cannot see it.

    ⭐ EIGHTH FLIP, SAME DAY, back to `assert ok is False`. 2ee38f8 amended 20 Cap.50 facts
    against the NSSF Act R.E.2023 and rewrote three CONCISE_BILINGUAL_FACTS entries, so both
    inputs are newer than the 184-row artifacts shipped in 7d46df1. PENDING, and the pending
    content is exactly what makes this flip worth reading rather than acknowledging:

      fine_limit            TZS 100,000 -> TEN MILLION (Cap.50 R.E.2023 s.76(1)). The deployed
                            index row 159 reads `fine limit: one hundred thousand TZS` -- a
                            100x understatement, LIVE, and a faithful copy of R.E.2015 s.72(1).
      nssf_payment_deadline the 10th -> within one month after month-end (s.14(1)). Deployed
                            row 63 reads `NSSF inalipwa ifikapo tarehe 10`, which appears in NO
                            source -- the fact's own verified_by says so, and had said so since
                            2026-09-02 while this row kept serving it.
      imprisonment_term_limit  new ask-led row, same statutory sentence as the fine.

    So the previous flip's lesson repeats with a second instance: a fact corrected in
    locked_facts.json while its EMBEDDED TEXT keeps the superseded value is not a one-off that
    Part XII happened to hit -- it is the default outcome of correcting a fact, and this check
    is what makes the gap visible between the correction and the regen that ships it.

    ⭐ NINTH FLIP, back to `assert ok is True`. The Cap.50 regen ran (184 facts, (184, 768), 0
    self-retrieval failures, every anchor across 38 guards unique, all 38 critical queries
    passing including both new ones, rank gate 38/16/6, correction_sync=CLEAN) and the artifacts
    were dual-committed. Exactly SIX rows changed, all intended, verified against the fetched
    files before they were committed:

        63   deadline: "ifikapo tarehe 10" -> "ndani ya MWEZI MMOJA baada ya mwisho wa mwezi"
        78   split triggers: enumeration -> the s.12(2) rule
        84   registration deadline: hedge -> within one month
        152  health insurance: "3 months" -> NOT SETTLEABLE FROM Cap.50
        159  fine: "one hundred thousand TZS" -> ten million, with the old value negated
        160  imprisonment: bare "two years" -> ask-led row

    And `one hundred thousand` / `ifikapo tarehe 10` now appear in ZERO rows of the shipped
    index. (`part xiii` still matches row 102 -- that is the CORRECT disambiguation clause, not
    a survival of the reversal, already adjudicated as a bad specimen in its own right.)

    rag_fact_count did NOT move (184 -> 184), so unlike the previous ship there was no window
    in which the config and the index could disagree.

    ⭐ TENTH FLIP, back to `assert ok is False`, and the pending change is a SINGLE ROW.

    897e0e2 rewrote index row 57. It had asserted a FABRICATED TZS 11,000,000 "EFD turnover
    threshold" -- re-verified against TAA Cap.438 R.E.2023 s.44 on 2026-08-29 and found
    invented, since s.44(1) makes fiscal-receipt issuance the default for everyone and s.44(2)
    allows exemption only by a Commissioner-General notice. It stayed live for five and a half
    weeks after that finding, defended by three separate things: the row, a critical query
    anchored on the fabricated figure itself, and a comment instructing maintainers not to
    change the row.

    ⚠️ NOTE WHICH INPUT IS STALE AND WHICH IS NOT. Only
    `scripts/precompute_rag_embeddings.py` is ahead of the artifacts this time;
    `scripts/locked_facts.json` is NOT, because the LOCKED FACT WAS ALREADY CORRECT. The defect
    was entirely in the embedded rendering. That is the sync gap in its purest form -- the fact
    said the right thing on 2026-08-29 and the text served to users said the opposite until
    today -- and this check is the only thing in the repo that makes the window visible.

    FLIPS BACK TO `assert ok is True` when the regen ships row 57 and its artifacts are
    dual-committed.
    """
    ok, report = check(repo_dir=REPO)
    assert ok is False, (
        f"the live repo reports FRESH: {report}. If the row-57 regen has shipped and its "
        "artifacts are dual-committed, flip this to `assert ok is True`, record the flip with "
        "the shipping commit, and re-assert `not report['stale_inputs']`. Do NOT silence it in "
        "either direction: both states are meaningful, and the state is the whole signal.")
    # WHICH input is stale is the assertion, not just THAT one is. Here it is the builder ALONE
    # -- if locked_facts.json also appears, a second pending change is hiding behind this one.
    assert set(report["stale_inputs"]) == {"scripts/precompute_rag_embeddings.py"}, (
        f"a DIFFERENT input is stale than the row-57 fix accounts for: "
        f"{sorted(report['stale_inputs'])}. The locked facts were already correct in this "
        f"cycle, so locked_facts.json appearing here means a separate unshipped change.")
    assert report["artifacts_diverged"] is False, (
        "the two index directories disagree -- a different defect from a pending regen, "
        "and one the R15 dual-commit step exists to prevent")
