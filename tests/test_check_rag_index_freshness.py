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


def test_sha_staleness_is_still_REPORTED_but_no_longer_decides_the_verdict():
    """⛔ THIS TEST'S CONTRACT CHANGED ON 2026-10-08, DELIBERATELY, AND THE CHANGE IS WORTH
    READING BEFORE TRUSTING IT -- because "a test that used to assert False now asserts True"
    is exactly the shape of a weakened control, and this is not one.

    It used to assert `ok is False` on planted SHA staleness. The verdict is now
    CONTENT-addressed: does `build_fact_texts()` over this tree equal the served
    rag_facts_text.json? SHA staleness alone no longer turns it red, because on 2026-10-08 it
    went red on a `wrong_patterns` edit -- a field the builder does not read -- while the
    built text was BYTE-IDENTICAL to the served index. The check was reporting staleness that
    did not exist, and a check that is red when nothing is wrong teaches the reflex of
    overriding it.

    SO WHAT THIS NOW ASSERTS: the planted staleness is still fully REPORTED in
    `stale_inputs`, with the implicated commits, because that is what a reader needs once
    content IS red. The limb is preserved and demoted, not deleted.

    AND THE SCRIPT IS NOT WEAKER AGAINST ITS FOUNDING INCIDENT -- see the next test, which
    plants it. The 2026-09-03 case was a CORRECTED FACT that never reached the index; a
    corrected fact changes the built text, so the content limb catches it. It catches it
    MORE often, in fact: SHA staleness is invisible when the fact edit and the artifact land
    in the SAME commit, and a content mismatch is not.
    """
    shas = {p: "C" for p in FRESHNESS_INPUTS + DEPLOYED_ARTIFACTS}
    shas["scripts/locked_facts.json"] = "D"  # edited after the regen

    ok, report = check(
        is_ancestor_fn=_is_ancestor,
        last_touch_fn=_make_last_touch(shas),
        commits_since_fn=_commits_since,
        # ⛔ content_fn SUPPLIED SO THIS TEST ISOLATES THE LIMB IT IS ABOUT (2026-10-09). It
        # previously used the live tree, so a source change — the row-9 rewording — turned it
        # red via the CONTENT limb while its subject is the SHA limb's demotion. A test that
        # means to isolate one limb must not be failable by another limb's live state; that is
        # how a green-to-red flip gets misread as the demotion having been undone.
        content_fn=lambda: (SERVED_TEXTS, None),
    )
    assert "scripts/locked_facts.json" in report["stale_inputs"], (
        "the provenance limb has stopped reporting planted staleness — that limb is demoted, "
        "not removed, and losing it would leave a red content verdict with no way to say "
        "WHICH commits are implicated")
    assert report["stale_inputs"]["scripts/locked_facts.json"], "no implicated commits listed"
    assert report["_stale_inputs_is_provenance_only"], (
        "the provenance label is gone; without it a future reader will read stale_inputs as "
        "a verdict again, which is the conflation this redesign removed")
    # And `ok` is driven by content here, not by the planted SHA state.
    assert report["content_matches"] is True, (
        "the live tree's content does not match the served index, so this test cannot "
        "demonstrate the separation it exists for — fix the real staleness first")
    assert ok is True


def test_the_FOUNDING_INCIDENT_is_still_caught_by_the_content_limb():
    """The incident this whole script was written for (2026-09-03): `efd_threshold_tzs_11m`
    was corrected off an invented threshold, and the correction never reached the deployed
    index -- served ~111 times. Planted as a CONTENT divergence, which is what that incident
    actually was: the built text and the served text disagree.

    This is the test that makes the redesign safe. Without it, demoting the SHA limb would be
    a weakening with nothing to show the capability survived."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_fresh_founding", os.path.join(REPO, "scripts", "check_rag_index_freshness.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_fresh_founding"] = mod
    spec.loader.exec_module(mod)
    texts, err = mod.built_fact_texts(REPO)
    assert err is None, err
    # A corrected fact: the served index still carries a value the current facts reject.
    stale_served = list(texts)
    hit = next((i for i, t in enumerate(stale_served) if "EFD" in t or "efd" in t), None)
    assert hit is not None, "no EFD row found — re-point this specimen"
    stale_served[hit] = stale_served[hit] + " Kizingiti ni TZS 11,000,000."
    ok, report = check(repo_dir=REPO, content_fn=lambda: (stale_served, None))
    assert ok is False, (
        "a built text that disagrees with the served index did not turn the check red — the "
        "content limb is INERT and the founding incident would recur unseen")
    assert report["content_matches"] is False
    rows = [r for info in report["diverging"].values() for r in info.get("rows", [])]
    assert any(r["index"] == hit for r in rows), report["diverging"]


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
        # content_fn supplied so the SHA limb is isolated -- see _served_texts(). Without it
        # this test went red on a live source change, for a reason unrelated to its subject.
        content_fn=lambda: (SERVED_TEXTS, None),
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

    ⭐ FIFTEENTH FLIP, back to `assert ok is True` — AND THE CHECK ITSELF CHANGED, WHICH IS WHY
    THIS IS THE LAST FLIP OF ITS KIND. The fourteenth flip was red on a `wrong_patterns` edit
    while `build_fact_texts()` was BYTE-IDENTICAL to the served index: the check was reporting
    staleness that did not exist, because it asked which FILE was touched rather than whether
    the SERVED TEXT is what this tree builds.

    Leaving it red was the wrong call, for a reason worth keeping: a check that is red when
    nothing is wrong teaches the reflex of overriding it, and that reflex is spent the one time
    it is red because something IS wrong. Silencing it would have been worse. The fix was to
    make the VERDICT content-addressed -- same principle as /health reporting a digest rather
    than a row count, and for the same reason: the count was unchanged at 184 across a regen
    that changed what was served.

    So `ok` now means: build_fact_texts() over this tree equals the served rag_facts_text.json
    row for row, in BOTH deploy dirs, and the embedding matrix has one row per text. The git-SHA
    limb is KEPT and demoted to PROVENANCE -- it still answers "which commits are implicated"
    once content is red, and still catches the two deploy dirs being committed separately.

    THE CONSEQUENCE FOR FUTURE FLIPS: this test should now flip FAR LESS OFTEN, and when it does
    it means something served actually changed. A fact edit, a builder change or a row
    reordering turns it red; a `wrong_patterns` or `verified_by` edit does not.

    ⭐ SIXTEENTH FLIP, back to `assert ok is False`, AND IT IS THE FIRST FLIP CAUSED BY A ROW
    THAT WAS NOT WRONG. Every previous flip pended a CORRECTION — a fabricated threshold, a
    100x understated fine, a reversed citation. This one pends a REWORDING: `nssf_employer_rate`
    read "mwajiri analipa asilimia 10 YA MSHAHARA WA MFANYAKAZI", which is true as a statement
    of the BASE and reads in Swahili as a statement of SOURCE — the opposite of the employer's
    obligation. eval_086 then served, live in the 2026-10-09 gate, "Kiasi kinachokatwa na
    mwajiri KWENYE MSHAHARA wa mfanyakazi ... ni asilimia 10": rate right, party inverted, close
    enough to the row's phrasing to be an echo of it. An employer following it deducts 10% from
    wages unlawfully, on top of the employee's own 10%.

    ⛔ WHY THAT DISTINCTION IS WORTH A FLIP OF ITS OWN. The 2026-10-09 closability pass
    classified eval_086 by asking "is the governing fact in the index?" — it was, so the row was
    called a MODEL defect. The fact was ALSO complicit. **"Is the governing fact present" is not
    the same question as "does the governing fact say it unambiguously",** and only the second
    one predicts whether the model can get it wrong. A true fact whose wording is ambiguous in
    the one dimension the question turns on is a corpus defect that no presence check can see.

    Exactly one row changes (9), 184 before and after. Flip back to `assert ok is True` once the
    R15 regen has run and the artifacts are dual-committed — and re-assert the specifics then,
    because `ok is True` alone does not establish that the intended row is the one that moved.
    """
    ok, report = check(repo_dir=REPO)
    assert ok is False, (
        "the live repo now reports FRESH. If the row-9 rewording regen has shipped, flip this "
        "and test_content_limb_passes_on_the_real_built_texts back to True and re-assert the "
        "specifics; if it has not, something else has made the built index match again and "
        "that needs explaining before this is flipped.")
    assert report["content_matches"] is False, report
    assert report["content_build_error"] is None, report
    rows = report["diverging"]["kaggle/rag_facts_text.json"]["rows"]
    assert [r["index"] for r in rows] == [9], (
        f"the pending divergence is no longer row 9 alone — a second change has been staged "
        f"without this note being updated: {rows}")
    assert "HAIKATWI" in rows[0]["built"] and "ikihesabiwa" in rows[0]["built"], (
        "the pending row no longer separates the BASE from the SOURCE, which is the entire "
        "point of the rewording")
    assert report["embedding_rows_match"] is True, report
    assert report["built_rows"] == 184, report["built_rows"]
    # ⛔ AND THE PROVENANCE LIMB IS STILL RED HERE, DELIBERATELY ASSERTED. This is the whole
    # point of the redesign: `scripts/locked_facts.json` HAS moved since the artifacts were
    # committed (the 6e65097 wrong_patterns fix), and the check is GREEN anyway because nothing
    # served changed. If this assertion ever fails because stale_inputs is empty, the two limbs
    # have stopped disagreeing and this test no longer demonstrates the distinction it was
    # rewritten to prove -- re-point it at whatever input has moved instead of deleting it.
    assert report["stale_inputs"], (
        "stale_inputs is empty, so this test no longer exercises the case it exists for: an "
        "input moved WITHOUT changing a served row. The content limb is still asserted above; "
        "re-point this at the current provenance state rather than dropping it.")
    assert not report["missing_inputs"] and not report["missing_artifacts"], (
        f"a missing file is a setup bug, not a stale index: {report}")
    assert report["artifacts_diverged"] is False, (
        "the two index directories disagree -- a different defect from a pending regen, and "
        "one the R15 dual-commit step exists to prevent")


# ── THE CONTENT LIMB, PLANTED IN EVERY DIRECTION (added 2026-10-08) ─────────────────────────
# R26: a control is not working until it has been watched to block the thing it exists to block
# AND to pass a clean case. `content_fn` is injectable precisely so these four arms can be run
# against synthetic state rather than against whatever the tree happens to contain -- the same
# reason the git calls were made injectable when this file was first written.

def _real_texts():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_fresh_mod", os.path.join(REPO, "scripts", "check_rag_index_freshness.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_fresh_mod"] = mod
    spec.loader.exec_module(mod)
    texts, err = mod.built_fact_texts(REPO)
    assert err is None, f"the builder itself failed, so these arms cannot run: {err}"
    assert texts and len(texts) == 184, f"unexpected builder output: {texts and len(texts)}"
    return texts


REAL_TEXTS = _real_texts()


def _served_texts():
    """The COMMITTED index, i.e. what the content limb compares against.

    ⛔ ADDED 2026-10-09 TO DECOUPLE THE SHA-LIMB TESTS FROM LIVE FRESHNESS. Two tests whose
    subject is limb SEPARATION (`test_sha_staleness_is_still_REPORTED_but_no_longer_decides_
    the_verdict` and `test_a_fresh_index_built_after_every_input_change_passes_clean`) were
    calling `check()` with the REAL builder output, so they went red the moment a source change
    made the live content diverge — for a reason that has nothing to do with what they assert.
    A test that intends to isolate one limb must not be failable by another limb's live state;
    feeding it a content_fn that matches by construction is what makes the isolation real.
    """
    import json
    with open(os.path.join(REPO, "kaggle", "rag_facts_text.json"), encoding="utf-8") as fh:
        return json.load(fh)


SERVED_TEXTS = _served_texts()


def test_content_limb_passes_on_the_real_built_texts():
    """⭐ SIXTEENTH FLIP, to `assert ok is False` — PENDING THE ROW-9 REWORDING REGEN.

    `nssf_employer_rate` was reworded on 2026-10-09 because its text INVITED the defect it
    existed to prevent. It read "mwajiri analipa asilimia 10 YA MSHAHARA WA MFANYAKAZI" — true
    as a statement of the BASE, and readable in Swahili as a statement of SOURCE, which is the
    opposite of the employer's obligation. eval_086 then served "Kiasi kinachokatwa na mwajiri
    KWENYE MSHAHARA wa mfanyakazi ... ni asilimia 10" live in the 2026-10-09 gate: the rate
    right, the party inverted, close enough to the row's own phrasing to be an echo of it. An
    employer following it deducts 10% from wages unlawfully, on top of the employee's own 10%.

    EXACTLY ONE ROW CHANGES (9), 184 before and after, verified by this check's own diff. Flip
    back to `assert ok is True` once the R15 regen has run on Kaggle and the artifacts are
    dual-committed to kaggle/ and chike-inference/ — and re-assert the specifics then, because
    `ok is True` alone does not establish that the intended row is the one that moved.
    """
    ok, rep = check(repo_dir=REPO, content_fn=lambda: (REAL_TEXTS, None))
    assert ok is False, (
        "the built index now matches the served one — if the row-9 regen has shipped, flip "
        "this and the three siblings back and re-assert the specifics")
    assert rep["content_matches"] is False
    diverging = rep["diverging"]["kaggle/rag_facts_text.json"]["rows"]
    assert [r["index"] for r in diverging] == [9], (
        f"the pending divergence is no longer row 9 alone: {diverging}")
    assert "HAIKATWI" in diverging[0]["built"], (
        "the pending row no longer states that the employer's share is NOT deducted, which is "
        "the whole point of the rewording")


def test_content_limb_BLOCKS_a_single_changed_row():
    """THE SPECIMEN THIS REDESIGN EXISTS FOR. One row altered -- row 181, the share-capital
    ladder, with 600,000 swapped for the 290,000 the model wrongly served on 2026-10-08 -- and
    the check must go red and NAME the row. The old SHA limb could not see this at all if the
    change arrived in the same commit as the artifacts."""
    tampered = list(REAL_TEXTS)
    tampered[181] = tampered[181].replace("TZS 600,000", "TZS 290,000")
    assert tampered != REAL_TEXTS, "the planted edit did not change anything — bad specimen"
    ok, rep = check(repo_dir=REPO, content_fn=lambda: (tampered, None))
    assert ok is False, "a changed served row did not turn the check red"
    assert rep["content_matches"] is False
    rows = [r for info in rep["diverging"].values() for r in info.get("rows", [])]
    assert any(r["index"] == 181 for r in rows), (
        f"the check went red but did not name the changed row: {rep['diverging']}")


def test_cannot_evaluate_is_NOT_a_pass():
    """If the builder cannot be imported or run, `ok` must be False with a distinct reason --
    never True by omission. Same rule that made run_eval.py's empty-corpus path exit 2."""
    ok, rep = check(repo_dir=REPO, content_fn=lambda: (None, "ImportError: planted"))
    assert ok is False
    assert rep["content_build_error"] == "ImportError: planted"
    assert rep["content_matches"] is None, "a failed build must not report a content verdict"


def test_a_row_count_mismatch_with_the_embeddings_BLOCKS():
    """A half-shipped index: the text file and the embedding matrix disagreeing on how many
    rows there are. Checkable locally even though the embeddings themselves cannot be rebuilt
    here, and it is the one property a content change would always break."""
    short = list(REAL_TEXTS)[:-1]
    ok, rep = check(repo_dir=REPO, content_fn=lambda: (short, None))
    assert ok is False
    assert rep["embedding_rows_match"] is False, rep["embedding_rows"]


def test_the_provenance_limb_is_labelled_as_not_decisive():
    """The SHA limb must survive as provenance and must not be able to decide the verdict --
    that conflation is what produced the fourteenth flip's false red."""
    import inspect
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_fresh_src", os.path.join(REPO, "scripts", "check_rag_index_freshness.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    src = inspect.getsource(mod.check)
    assert "content_matches is True" in src, "content no longer decides `ok`"
    assert "stale_inputs" not in src.split("ok = (")[1].split(")")[0], (
        "stale_inputs is back in the verdict expression; it is provenance only")
