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
import json

from scripts.check_facts_index_sync import PINNED, _match_needle, check

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
    # memorandum_articles_of_association_filing_fee (22,000 -> 66,000, 2026-09-02) was here
    # pending the R15 regen that would ship the corrected group text. The b002b96 regen
    # (2026-09-03) shipped it -- test_known_pending_r15_group_drift_is_still_pending caught
    # the resolution immediately, exactly the signal its own docstring describes. Removed
    # rather than left stale.

    # ---- 2026-10-06: BRELA REPLACED ITS PUBLISHED FEE SCHEDULE ----------------------------
    # Not a correction of a misreading. BRELA's own "Ada za Kampuni" page changed between two
    # dated, hashed captures (brela_ada_kampuni_v2.html, sha256 cb1353fc..., 2026-06-30 ->
    # brela_ada_kampuni_20261006T140442Z.html, sha256 8d5543ac..., 2026-10-06T14:04:42Z): the
    # whole foreign-company block moved from USD into TZS, the share-capital table went from
    # five bands to nine, and several local fees moved. R29 mode 3 -- the June figures were
    # correct as at their own date.
    #
    # ⛔ EVERY ONE OF THESE SIX IS A FIGURE PRODUCTION IS SERVING WRONG RIGHT NOW. They are
    # DRIFT only in the sense that no local edit can fix them: the group passages in
    # precompute_rag_embeddings.py are already correct in this commit, and the shipped
    # rag_facts_text.json cannot catch up except through the Kaggle R15 regen. They are listed
    # individually, with their old and new values, so that this block is a worklist rather than
    # a silence -- an entry that only says "pending regen" tells the next reader nothing about
    # what is wrong on the way there.
    # ✅ ALL SIX RESOLVED 2026-10-07 BY THE REGEN (built from e3e1d0f, 184x768, HF
    # 2026-10-07T19:38:04Z), and removed rather than left stale -- which is this test's own
    # stated signal firing for the second time in its life:
    #
    #   company_registration_fee_no_share_capital                   300,000  -> 500,000
    #   file_search_fee                                               3,000  ->   5,000
    #   file_search_report_fee                                       22,000  ->  30,000
    #   document_filing_fee_section_12_act_excluding_balance_sheet  USD 220  -> TZS 600,000
    #   balance_sheet_filing_fee_section_12_act                     USD 220  -> TZS 600,000
    #   late_filing_penalty_monthly_fee_section_12_act               USD 25  -> TZS  70,000
    #
    # The last of those is the figure `ext_15` was scored PASS on, which is why that gold row was
    # STALE rather than the model wrong; its verdict is RE_RUN_REQUIRED, not re-labelled.
    #
    # ⚠️ AND THE LIST WAS SHORT BY ONE WHEN IT WAS WRITTEN. `brela_foreign_late_filing_penalty` --
    # the STANDALONE row 172, not a group passage -- carried the same USD 25 and was pinned
    # `pending_r15` separately, so it never appeared here. It is also the row that ABORTED the
    # Kaggle run, on a payload gate written in the same commit as the fact it guards. A worklist
    # assembled by hand is exactly as complete as its author's recall; the durable replacement is
    # eval/index_quality/sweep_superseded_values_in_built_index.py, whose population is every
    # fact carrying a `superseded_value` field.

    # ⚠️ certified_copy_certificate_of_registration_fee (TZS 4,000 -> 10,000, item 12) is
    # DELIBERATELY ABSENT from this list, and the reason is a trap worth naming: it resolves
    # CLEAN against the shipped index by COINCIDENCE. _grouped_verdict does substring
    # containment, and the shipped brela_filing_fees passage happens to contain "10,000" --
    # as the STAMP DUTY figure, a different fee entirely. So the check passes on the right
    # string for the wrong reason, and the row is as stale as the six above. Recorded here
    # because a key missing from a worklist reads as a key that is fine.
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
    pinned_pending = {k for k, (verdict, _) in PINNED.items() if verdict == "pending_r15"}
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


# --- R26: a control that cannot fail is worse than no control. _match_needle is the whole
# redesign that replaced (row, needle) pins with (needle) pins searched across the entire
# index -- these tests plant the exact two failure shapes it exists to catch (a needle
# that matches nothing, a needle that matches more than once) and a clean case that must
# NOT be flagged, so the demonstration survives independent of any real fact or index row.

def test_match_needle_fires_when_the_needle_is_absent():
    """Planted failure #1: the fact's text was genuinely removed from the index (the
    real-world case this file calls "noise-dropped" -- see the 7 keys reclassified
    absent in the module docstring). Must FIRE, not silently pass."""
    status, matches = _match_needle(
        "this exact phrase appears nowhere in the index",
        ["row zero says something else", "row one says something else too"],
    )
    assert status == "absent"
    assert matches == []


def test_match_needle_fires_when_the_needle_is_ambiguous():
    """Planted failure #2: the needle now matches TWO rows -- a failure the OLD
    (row, needle) scheme could never detect at all, since it only ever checked one
    specific row number and never looked at the rest of the index. A caller that took
    the first match here would silently point at a coin-flip row. Must FIRE."""
    status, matches = _match_needle(
        "asilimia 0.5",
        ["WCF: asilimia 0.5 ya jumla ya mishahara", "OSHA vs WCF: asilimia 0.5 pia"],
    )
    assert status == "ambiguous"
    assert matches == [0, 1]


def test_match_needle_passes_on_a_clean_unique_needle():
    """The negative control: a needle that legitimately identifies exactly one row must
    NOT be flagged. Per R26, a control proven only to fire (never to pass a clean case)
    is a control proven only to be overbroad, not proven to work."""
    status, matches = _match_needle(
        "sekta 16 na sekta ndogo",
        ["unrelated row", "GN 605A inahusu sekta 16 na sekta ndogo 46", "another unrelated row"],
    )
    assert status == "unique"
    assert matches == [1]


def test_present_elsewhere_pin_fires_end_to_end_on_absent_needle(tmp_path, monkeypatch):
    """Same two planted failures as above, but through check() end-to-end -- proving the
    PINNED/check() wiring actually calls _match_needle and acts on its verdict, not just
    that the helper itself works in isolation (R26's NOT_WIRED distinction)."""
    facts = tmp_path / "locked_facts.json"
    facts.write_text(json.dumps({"r26_probe_absent_key": "irrelevant value"}), encoding="utf-8")
    index = tmp_path / "rag_facts_text.json"
    index.write_text(json.dumps(["row one", "row two"]), encoding="utf-8")

    monkeypatch.setitem(
        PINNED, "r26_probe_absent_key",
        ("present_elsewhere", "this phrase is nowhere in these two rows"),
    )
    ok, report = check(facts_path=str(facts), index_path=str(index))
    assert not ok
    assert any(d["key"] == "r26_probe_absent_key" for d in report["drift_pin_stale"])


def test_present_elsewhere_pin_fires_end_to_end_on_ambiguous_needle(tmp_path, monkeypatch):
    facts = tmp_path / "locked_facts.json"
    facts.write_text(json.dumps({"r26_probe_ambiguous_key": "irrelevant value"}), encoding="utf-8")
    index = tmp_path / "rag_facts_text.json"
    index.write_text(json.dumps(["row with shared phrase", "another row with shared phrase"]),
                      encoding="utf-8")

    monkeypatch.setitem(
        PINNED, "r26_probe_ambiguous_key", ("present_elsewhere", "shared phrase"),
    )
    ok, report = check(facts_path=str(facts), index_path=str(index))
    assert not ok
    assert any(d["key"] == "r26_probe_ambiguous_key" for d in report["drift_pin_stale"])


def test_present_elsewhere_pin_passes_end_to_end_on_a_clean_unique_needle(tmp_path, monkeypatch):
    """The end-to-end negative control: a pin whose needle is genuinely unique must
    resolve cleanly through the real check() path, not just through _match_needle."""
    facts = tmp_path / "locked_facts.json"
    facts.write_text(json.dumps({"r26_probe_clean_key": "irrelevant value"}), encoding="utf-8")
    index = tmp_path / "rag_facts_text.json"
    index.write_text(json.dumps(["unrelated row", "the one row with a unique phrase in it"]),
                      encoding="utf-8")

    monkeypatch.setitem(
        PINNED, "r26_probe_clean_key", ("present_elsewhere", "unique phrase"),
    )
    ok, report = check(facts_path=str(facts), index_path=str(index))
    assert ok
    assert any(d["key"] == "r26_probe_clean_key" and d["row"] == 1
               for d in report["present_elsewhere"])
