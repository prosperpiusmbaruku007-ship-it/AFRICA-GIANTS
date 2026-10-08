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

    ⭐ ELEVENTH FLIP, back to `assert ok is True`. The row-57 regen ran (built from 59cf784,
    184x768, correction_sync=CLEAN) and its artifacts are dual-committed. EXACTLY ONE ROW
    changed, verified against the fetched file before commit:

        57  'mauzo ya TZS 11,000,000 (milioni kumi na moja) kwa mwaka'
         -> 'EFD haina kizingiti cha mauzo kwa mwaka. ... Na SI TZS 11,000,000.'

    The figure still appears, under a negation, deliberately -- corpus rows assert it, so an
    explicit contradiction is what overrides the trained prior where a bare restatement merely
    competes with it. Polarity-checked, not presence-checked, in three places now: the regen's
    payload gate, the dry run, and the deploy verification.

    FLIPS BACK TO `assert ok is False` the next time a fact or the builder changes without a
    matching regen. Three flips in two days is three correction cycles, not churn -- and the
    False states did the work: each one named which input was unshipped and why.

    ⭐ TWELFTH FLIP, back to `assert ok is False`. BOTH inputs are stale this time, and the
    pending change is not a correction of ours at all -- IT IS A CHANGE IN THE LAW'S OWN
    PUBLISHED SCHEDULE, which is a shape none of the eleven previous flips had.

    BRELA replaced its company fee schedule between two dated, sha256-pinned captures:
    `brela_ada_kampuni_v2.html` (cb1353fc..., 2026-06-30) and
    `brela_ada_kampuni_20261006T140442Z.html` (8d5543ac..., fetched 2026-10-06T14:04:42Z). The
    whole foreign-company block moved from USD into TZS, the share-capital ladder went from five
    bands to nine, and several local fees moved. R29 mode 3: the June figures were CORRECT AS AT
    THEIR OWN DATE, so this is a supersession and not a defect anyone introduced.

    PENDING, and what is live and wrong on the way there:

        row 182  brela_filing_fees   USD 220 / USD 220 / USD 25  ->  TZS 600,000 / 600,000 /
                 70,000, with "SI USD 220 na SI USD 25" added. These USD figures are the ones
                 ext_15 was scored against, which is why that gold row is STALE, not the model
                 wrong.
        row 181  company_registration_ladder   the open-ended "zaidi ya TZS 50,000,000 ni TZS
                 440,000" -> five closed bands ending at 1,000,000, and no-share-capital
                 300,000 -> 500,000.
        + 12 locked facts amended, 1 re-authored (company_registration_fee_bands, which joins
          the ladder group rather than adding a row).

    ⚠️ BOTH INPUTS ARE STALE, and that is the correct reading rather than a worse one: unlike the
    eleventh flip (where only the builder moved, because the FACT was already right) and unlike
    the tenth, here the facts and the rendering changed together, because the underlying published
    figure changed. A flip that names WHICH inputs moved is doing more work than one that says
    "stale" -- this is the first flip where the answer is "both, and for the same reason".

    rag_fact_count does NOT move (184 -> 184), so there is no window in which the config and the
    index can disagree. Local dry run: eval/index_quality/dryrun_regen_2026_10_06.py -> SAFE TO
    RUN, 0 displacement regressions across 40 committed guards, both new guards at rank 2 and
    rank 1, both changed rows self-retrieving. Notably nat_34's displacement guard still passes
    with the ladder grown by four bands -- the dilution risk row 57 priced yesterday did not
    materialise, because the measured SHORT lead was left byte-identical.

    ⭐ THIRTEENTH FLIP, back to `assert ok is True`. The BRELA regen ran (built from e3e1d0f,
    184x768, correction_sync=CLEAN, HF 2026-10-07T19:38:04Z) and its artifacts are
    dual-committed. What shipped, named rather than implied:

        row 172  brela_foreign_late_filing_penalty   "faini ni USD 25" -> "faini ni TZS 70,000
                 kwa kila mwezi au sehemu ya mwezi". SAME INDEX POSITION before and after.
        row 182  brela_filing_fees   USD 220 / USD 220 / USD 25 -> TZS 600,000 / 600,000 /
                 70,000, with "SI USD 220 na SI USD 25".
        row 181  company_registration_ladder   five bands -> nine; no-share-capital 300,000 ->
                 500,000.

    ⚠️ THE TWELFTH FLIP'S PENDING LIST WAS INCOMPLETE AND THE REGEN IS WHY WE KNOW. It named rows
    181 and 182 and not row 172 -- the standalone row -- which is the row that then ABORTED the
    Kaggle run on a payload gate written in the same commit as the fact it guards. A flip that
    names which inputs moved is doing more work than one that says "stale"; it is still a list
    somebody wrote from memory, and this one was short by the row that mattered. The durable fix
    is not a better list: it is
    `eval/index_quality/sweep_superseded_values_in_built_index.py`, whose population is every
    fact carrying a `superseded_value` field.

    Verified, not assumed -- `eval/controls/verify_rag_fetch_2026_10_07.py` ->
    `eval/results/rag_fetch_verification_2026_10_07.json`, VERDICT VERIFIED, 11 payload gates
    re-executed against the SERVED index by IMPORT (not re-implementation), and the served text
    asserted BYTE-IDENTICAL to `build_fact_texts()` -- which is what actually establishes the
    index was built from this tree, rather than the HF commit title, which is a claim the
    uploader made about itself.

    ⭐ FOURTEENTH FLIP, back to `assert ok is False`, AND THIS ONE IS A DIFFERENT KIND OF STALE
    FROM EVERY FLIP BEFORE IT -- which is why it is spelled out rather than logged as "stale".

    PENDING INPUT, named: `scripts/locked_facts.json`, moved by 6e65097. The change is a
    `wrong_patterns` fix on `rent_wht_rate` -- its two ENGLISH patterns carried a bare `rent`,
    which matches inside the ordinary English word "diffe-RENT", and flagged
    `tier1a_wht_deep_035`, a row about DIRECTOR FEES whose claims are both correct.

    ⛔ THE SERVED INDEX CONTENT IS UNAFFECTED, AND THAT IS MEASURED, NOT ASSUMED.
    `build_fact_texts()` run against this tree returns 184 rows BYTE-IDENTICAL to the committed
    `kaggle/rag_facts_text.json`, because `wrong_patterns` is not an input to the index text at
    all -- it is authored for matching GENERATED output. So this is PROVENANCE staleness, not
    CONTENT staleness: no regen is owed to make the served index correct, and the next reader
    does not have to re-derive that.

    IT STILL FLIPS, AND IT SHOULD. The check's contract is over INPUT SHAs, deliberately coarse,
    because it cannot know which fields of locked_facts.json reach the index -- and a check that
    tried to know would be a second, divergent copy of the builder's field selection. Silencing
    it here on "the content is fine" would be exactly the reasoning that makes a freshness check
    useless the one time the content is NOT fine. The honest state is: red, with the reason and
    the measurement attached.

    CLEARS on the next regen that bakes this `locked_facts.json`, or on any commit that reverts
    it. Flip back to `assert ok is True` then -- and re-assert the specifics, because `ok is
    True` alone would also pass if `check()` started returning True for an unrelated reason.
    """
    ok, report = check(repo_dir=REPO)
    assert ok is False, (
        f"the live repo now reports FRESH: {report}. If the regen has shipped, flip this back to "
        "`assert ok is True` and re-assert the specifics below. Do NOT silence it in either "
        "direction: the state is the whole signal.")
    # THE NEGATIVE STATE GETS ITS SPECIFICS ASSERTED TOO, for the same reason the positive one
    # does: `ok is False` alone would pass if the check went stale for a reason that has nothing
    # to do with this edit -- including a missing file, which is a setup bug and not a stale
    # index. Naming the pending input is what makes the red state carry information.
    assert set(report["stale_inputs"]) == {"scripts/locked_facts.json"}, (
        f"the pending inputs are not the ones this flip was written for: "
        f"{list(report['stale_inputs'])}. If the BUILDER (precompute_rag_embeddings.py) has also "
        f"moved, that is a content change and needs its own note -- a `wrong_patterns` edit does "
        f"not touch index text, but a builder change does.")
    assert not report["missing_inputs"] and not report["missing_artifacts"], (
        f"a missing file is a setup bug, not a stale index: {report}")
    assert report["artifacts_diverged"] is False, (
        "the two index directories disagree -- a different defect from a pending regen, and "
        "one the R15 dual-commit step exists to prevent")
