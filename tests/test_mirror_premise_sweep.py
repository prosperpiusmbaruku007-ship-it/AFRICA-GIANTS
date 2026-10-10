"""THE MIRROR SWEEP'S CLASSIFIER, AND A SHRINK-ONLY FLOOR ON WHAT IT FOUND.

⚠️ WHAT THIS DELIBERATELY DOES NOT DO: assert the current 37 same-lead pairs. Those are
DEFECTS, reported and not yet fixed, and a test that pins them would be the R17 corollary's
worst form — *"a test that instructs future maintainers not to fix a real defect is worse
than no test"*. So the direction is one-way: the finding counts may FALL freely and may not
RISE. A fix makes this file go red only by making it stale, which is the right failure.

What IS asserted is the instrument, because the instrument is the part that fails silently: a
transform that stops matching, a narrowing that empties the population, or a severity rule
that demotes everything all produce FEWER findings, and fewer findings in a defect hunt reads
as progress (R39).
"""
import io
import json
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "eval", "controls"))

import mirror_premise_sweep_2026_10_10 as ms            # noqa: E402

ART = os.path.join(REPO, "eval", "results", "mirror_premise_sweep_2026_10_10.json")


def _art():
    return json.load(io.open(ART, encoding="utf-8"))


# ── the classifier, both limbs (R26) ────────────────────────────────────────────────────
def test_the_founding_specimen_is_flagged_and_a_flipping_pair_is_not():
    assert ms.classify(ms.PLANTED_PRE_FIX["lead_q"],
                       ms.PLANTED_PRE_FIX["lead_m"]) == "SAME_LEAD"
    assert ms.classify(ms.PLANTED_CLEAN["lead_q"], ms.PLANTED_CLEAN["lead_m"]) == "FLIPS"
    assert ms.classify("Ndiyo", None) == "MIRROR_LEFT_THE_ENGINE"


def test_the_transform_reproduces_the_founding_mirror_verbatim():
    out, frame, _ask = ms.mirror(ms.PLANTED_PRE_FIX["question"])
    assert out == ms.PLANTED_PRE_FIX["mirror"]
    assert frame == "is-voluntary"


@pytest.mark.parametrize("question,expect_frame", [
    # The real row that produced a false finding before the ask-clause narrowing. Its yes/no
    # lead comes from base_rejection and its ask is "ni ngapi?" — flipping `tunalipa` in the
    # first clause asks nothing different, so the identical lead is CORRECT.
    ("Uzalishaji tunalipa jumla milioni nne, mauzo tunalipa jumla milioline tatu, "
     "SDL ya kampuni nzima ni ngapi?", None),
    ("Nimesajili VAT na nalipa SDL — je naweza kufuta VAT?", None),
    # ...and the limb in the other direction, without which the narrowing could empty the
    # population and still pass.
    ("Je, mwajiri mwenye wafanyakazi 8 ana wajibu wa kulipa SDL?", "has-a-duty"),
    ("Je, NSSF si ya hiari kwa mwajiri anayestahili?", "is-voluntary"),
    ("nina wafanyakazi 15 je SDL inanihusu", "applies-to-me"),
])
def test_the_frame_must_sit_in_the_clause_that_carries_the_ask(question, expect_frame):
    assert ms.mirror(question)[1] == expect_frame


def test_the_confirmation_tag_is_stripped_not_treated_as_the_ask():
    """eval_393 ends ", sivyo?" — the tag is part of the ask, and splitting on it drops the
    row out of the population it belongs to. The tag must survive into the mirror."""
    out, frame, _ = ms.mirror("Kampuni yenye wafanyakazi 9 haitakiwi kulipa SDL, sivyo?")
    assert frame == "it-is-required"
    assert out == "Kampuni yenye wafanyakazi 9 inatakiwa kulipa SDL, sivyo?"


def test_a_money_comma_does_not_split_the_ask_clause():
    out, frame, _ = ms.mirror("Namlipa dereva TZS 450,000 kwa mwezi — nakiuka sheria?")
    assert frame == "i-am-breaking" and "TZS 450,000" in out


# ── the severity axis, which DEMOTES and therefore fails silently ───────────────────────
def test_severity_flags_the_founding_specimen_and_spares_a_self_correcting_reply():
    assert ms.severity("is-voluntary", ms.PLANTED_PRE_FIX["reply"])[0] == "UNCORRECTED"
    verdict, token = ms.severity(
        "applies-to-me", "Ndiyo. Una wafanyakazi 15 (10 au zaidi), hivyo SDL inatozwa.")
    assert verdict == "CORRECTED" and token == "inatozwa"


def test_the_optionality_frames_are_NOT_merged_into_the_obligation_family():
    """The merge would be the R20 borrowed-detector defect: a reply saying the levy APPLIES
    does not address whether it is OPTIONAL, and conflating the two is precisely eval_394."""
    appl_only = "Ndiyo. NSSF inahusu mwajiri kutoka mfanyakazi wa kwanza, inatozwa."
    assert ms.severity("is-voluntary", appl_only)[0] == "UNCORRECTED"
    assert ms.severity("i-pay", appl_only)[0] == "CORRECTED"


def test_every_transform_frame_has_a_severity_subject():
    missing = sorted({t[2] for t in ms.TRANSFORMS} - set(ms._FRAME_SUBJECT))
    assert not missing, f"frames with no severity subject fall to UNKNOWN_FRAME: {missing}"


# ── the artifact, shrink-only ──────────────────────────────────────────────────────────
def test_the_findings_may_fall_but_not_rise():
    """⛔ A RATCHET, TIGHTENED WHEN THE CLASS FIX LANDED. The bounds were 37/2/27 when the
    sweep first ran and are 1/0/11 now, because premise.py closed 36 of the 37 same-lead
    pairs and the negated cue lists closed 16 of the 27 route asymmetries. Leaving the old
    bounds in place would have kept the test green through a total regression of the fix,
    which is the stale-pin shape: an assertion that was once meaningful and now cannot fail.

    The remaining 1 is `edge_p08`/`is-it-true`, the frame premise.py DELIBERATELY excludes —
    it asserts no proposition of its own, so the claim being confirmed sits in an embedded
    clause the resolver does not parse. Left visible in the finding list rather than removed
    from the population along with the fix.

    The remaining 11 asymmetries are the OTHER two cue systems (the vat/efd turnover gate and
    the minimum-wage cue list); `predicates_that_flip` names the blocker per row."""
    a = _art()
    assert a["verdicts"]["SAME_LEAD"] <= 1, (
        "the same-lead population has GROWN. A new engine lead has been added that answers "
        "both premises identically, or the resolver stopped reaching one — re-read the sweep "
        "before shipping it")
    assert a["severity"]["UNCORRECTED_same_lead"] == 0, (
        "a pair is back to answering a proposition the verdict never evaluated — the "
        "eval_394 class. This is the one count that should never be non-zero again")
    assert a["verdicts"]["MIRROR_LEFT_THE_ENGINE"] <= 11
    assert a["verdicts"]["FLIPS"] >= 51, (
        "fewer pairs flip correctly than before the class fix — the ratchet runs both ways, "
        "because a resolver that stops resolving shows up as FEWER findings AND fewer "
        "flips, and only the second is unambiguous (R39)")


def test_the_positive_limb_is_recorded_and_is_the_row_fixed_by_hand():
    """⛔ THE POPULATION IS CHECKED BY ITS POSITIVE LIMB; ITS FINDINGS CANNOT CHECK IT. If
    this list empties, the harness has stopped being able to report health at all and every
    finding count it prints becomes uninterpretable."""
    flips = _art()["pairs_that_flip_correctly"]
    assert flips, "no pair flips — the harness can no longer distinguish health from defect"
    assert any(r["id"] == "eval_394" for r in flips), (
        "eval_394 was the ONLY polarity-correct pair in the population when this sweep first "
        "ran, and it is the one that was fixed by hand on 2026-10-10. It is now one of 51. "
        "Losing it is a regression in the fix, not in this test")


def test_the_narrowing_keeps_its_itemised_receipt():
    """R39: a count that falls must say which rows and why, per row. Ten rows left the
    finding list when the ask-clause narrowing landed and each is named with the frame that
    was found outside its ask."""
    rejected = _art()["rejected_frame_outside_the_ask"]
    assert len(rejected) >= 10
    assert all(r.get("frame_found_outside_the_ask") and r.get("ask_clause")
               for r in rejected)
    assert any(r["id"] == "extract_087" for r in rejected)


def test_the_frame_table_has_ONE_owner():
    """The sweep must not be able to disagree with the resolver about what a polarity pair IS.
    A sweep with a narrower table than the resolver reports a CLEAN population while rows go
    unresolved — the R39 direction, in the instrument rather than the rule."""
    from chike.rules_engine import premise
    owned = {(p, n, f) for p, n, f, _prop, _inv in premise.FRAMES}
    swept = {(p, n, f) for p, n, f, _src in ms.TRANSFORMS}
    assert owned <= swept, f"the resolver carries frames the sweep cannot see: {owned - swept}"
    extra = {f for _p, _n, f in swept - owned}
    assert extra == {"is-it-true"}, (
        f"the sweep carries frames the resolver does not, beyond the one deliberately "
        f"excluded: {extra}")
    assert ms._ask_clause("Je, NSSF si ya hiari?")[0] == premise.ask_clause(
        "Je, NSSF si ya hiari?")[0]


def test_the_dead_and_shadowed_transforms_are_reported_separately():
    """They are different facts: absent means the form appears nowhere in 2,484 questions;
    shadowed means the row IS in the population under another frame. Reporting both as
    'dead' sends someone hunting a Swahili form that is actually in use."""
    a = _art()
    assert "transforms_absent_from_the_corpus" in a
    assert "transforms_shadowed_by_another_frame_in_the_same_row" in a
    assert len(a["transforms_absent_from_the_corpus"]) <= 1
