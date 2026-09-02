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
from scripts.check_facts_index_sync import PINNED, check

# GROUP-member drift cannot be silenced via PINNED (PINNED is only consulted for keys NOT in
# _GROUP_MEMBERS -- see check()'s branch order): a group member's verdict comes from
# _grouped_verdict() comparing the locked fact's figure against the SHIPPED index's group
# passage, and there is no dict to pin it in. Same shape as PINNED's "pending_r15" verdict,
# same reason (the SHIPPED rag_facts_text.json has not caught up with a locked_facts.json
# edit and can only catch up via the Kaggle R15 regen, not a local edit), applied to the one
# path PINNED does not cover.
#
# key -> reason. A key here is DRIFT, not a real regression, until the R15 regen ships and
# test_known_pending_r15_group_drift_is_still_pending (below) starts failing -- that failure
# IS the signal to delete the entry, per this file's own test_pending_r15_keys_are_still_pending
# precedent for the PINNED-dict version of the same pattern.
KNOWN_PENDING_R15_GROUP_DRIFT = {
    "memorandum_articles_of_association_filing_fee": (
        "2026-09-02: corrected 22,000 -> 66,000 (direct read of BRELA's fee page named the "
        "Memorandum and Articles filing fee specifically, distinct from the generic "
        "22,000-per-document rate -- see PROGRESS.md and the fact's own correction_note). The "
        "group text in precompute_rag_embeddings.py's FACT_GROUPS['brela_filing_fees'] was "
        "updated in the same commit, but the SHIPPED rag_facts_text.json still carries the old "
        "22,000 figure until the next R15 regen runs on Kaggle."
    ),
}


def test_every_locked_fact_is_exact_sibling_or_pinned():
    ok, report = check()
    assert not report["drift_unpinned"], (
        f"{len(report['drift_unpinned'])} locked fact(s) are not exact/sibling-matched "
        f"against the RAG index and have no PINNED verdict: {report['drift_unpinned']}. "
        "Adjudicate each by reading the index for the content (not just the key), then "
        "add it to PINNED in scripts/check_facts_index_sync.py as present_elsewhere "
        "(with the row + a substring), absent, fragment, or pending_r15."
    )
    unexpected_stale = [d for d in report["drift_pin_stale"]
                        if d["key"] not in KNOWN_PENDING_R15_GROUP_DRIFT]
    assert not unexpected_stale, (
        f"{len(unexpected_stale)} PINNED/grouped row(s) no longer match the current index "
        f"content -- the index changed under the pin: {unexpected_stale}. Re-adjudicate and "
        f"update PINNED, or add a reasoned entry to KNOWN_PENDING_R15_GROUP_DRIFT if this is "
        f"expected pending an R15 regen."
    )


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


def test_known_pending_r15_group_drift_is_still_pending():
    """Companion to KNOWN_PENDING_R15_GROUP_DRIFT, same shape as
    test_pending_r15_keys_are_still_pending for the PINNED-dict version: fails the moment a
    tracked group-drift entry starts resolving cleanly (the R15 regen shipped), which is the
    GOOD outcome and must be an explicit KNOWN_PENDING_R15_GROUP_DRIFT edit, not a silent one."""
    _, report = check()
    still_stale = {d["key"] for d in report["drift_pin_stale"]}
    resolved = set(KNOWN_PENDING_R15_GROUP_DRIFT) - still_stale
    assert not resolved, (
        f"{resolved} no longer appear in drift_pin_stale -- the R15 regen most likely ran. "
        f"Remove these keys from KNOWN_PENDING_R15_GROUP_DRIFT in this file now."
    )
