"""Wires scripts/check_facts_index_sync.py into the normal test-suite gate.

Context: three matchers (key-slug prefix, key-slug-exact-plus-figure-regex, embedding
cosine score) were each published as "the" answer to whether locked_facts.json is
reachable through the RAG index, and each was wrong in a way the next one caught --
except the last one, which was corrected by the SCRIPT this test imports, not by a
fourth ad hoc pass. See scripts/check_facts_index_sync.py's module docstring for the
full account, including why a cosine-score threshold cannot be the check (the
'present_elsewhere' and 'absent' score distributions overlap).

This test is the check becoming permanent rather than a one-off scan: it runs on every
`pytest`, so a locked fact added without an index entry -- or an index edit that quietly
invalidates a PINNED present_elsewhere row -- fails the suite instead of waiting for
someone to go looking for a different thing, which is how all three prior gaps were
actually found.
"""
import pytest

from scripts.check_facts_index_sync import PINNED, check


@pytest.mark.xfail(
    strict=True,
    reason=(
        "EXPECTED RED since commit 0e08cd4 (2026-08-26, fee consolidation). PINNED in "
        "scripts/check_facts_index_sync.py was re-adjudicated against the PROSPECTIVE "
        "post-regen index (precompute_rag_embeddings.build_fact_texts(), 187 rows) rather "
        "than the CURRENTLY SHIPPED kaggle/rag_facts_text.json (still 221 rows, "
        "pre-consolidation) -- deliberately, in the same commit as the index-composition "
        "change rather than after the regen ships (see PROGRESS.md, 'FEE CONSOLIDATION "
        "APPLIED IN CODE ... A hidden dependency surfaced'). Against today's shipped index "
        "this test genuinely fails on 13 present_elsewhere pins whose row numbers now point "
        "at the future index, not the live one.\n"
        "UNBLOCK CONDITION: once the R15 regen actually runs (kaggle/regenerate_rag_e5.py, "
        "packaged in commit 76897e3) and the resulting rag_embeddings.npy / "
        "rag_facts_text.json (187 rows) are committed to both kaggle/ and chike-inference/, "
        "this test starts PASSING again. strict=True turns that XPASS into a hard FAILURE "
        "on the next run, so the marker cannot be forgotten -- remove this decorator in the "
        "SAME commit that lands the regen artifacts, not a follow-up."
    ),
)
def test_every_locked_fact_is_exact_sibling_or_pinned():
    ok, report = check()
    assert not report["drift_unpinned"], (
        f"{len(report['drift_unpinned'])} locked fact(s) are not exact/sibling-matched "
        f"against the RAG index and have no PINNED verdict: {report['drift_unpinned']}. "
        "Adjudicate each by reading the index for the content (not just the key), then "
        "add it to PINNED in scripts/check_facts_index_sync.py as present_elsewhere "
        "(with the row + a substring), absent, fragment, or pending_r15."
    )
    assert not report["drift_pin_stale"], (
        f"{len(report['drift_pin_stale'])} PINNED present_elsewhere row(s) no longer "
        f"match the current index content -- the index changed under the pin: "
        f"{report['drift_pin_stale']}. Re-adjudicate and update PINNED."
    )
    assert ok


def test_pending_r15_keys_are_still_pending():
    """A sanity check on the pin set itself: every key pinned pending_r15 in PINNED
    really is still unreachable via exact/sibling match. check() only consults PINNED
    for a key AFTER exact/sibling match has failed, so a key that regenerated into the
    index would simply resolve as 'exact' and vanish from report['pending_r15'] --
    silently correct in behaviour, but leaving a stale, misleading pin behind in the
    source. This test catches that directly by checking PINNED's pending_r15 keys
    against exact/sibling match itself, not against check()'s report bucket."""
    _, report = check()
    reachable = set(report["exact"]) | set(report["sibling"])
    pinned_pending = {k for k, (verdict, _, _) in PINNED.items() if verdict == "pending_r15"}
    regenerated = pinned_pending & reachable
    assert not regenerated, (
        f"{regenerated} now resolve via exact/sibling match -- the R15 regen most "
        "likely ran. Remove these keys' entries from PINNED in "
        "scripts/check_facts_index_sync.py so the pin set stays honest."
    )
