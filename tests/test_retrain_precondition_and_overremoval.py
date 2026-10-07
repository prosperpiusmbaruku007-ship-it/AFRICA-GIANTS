# -*- coding: utf-8 -*-
"""THE RETRAIN PRECONDITION AND THE OVER-REMOVAL AUDIT, BOTH PINNED SO THEY CANNOT LAPSE.

R35's lesson applied to a measurement instead of a control: the 2026-09-01 "MET" declaration was
true when written, carried forward on prose, and was false within hours — a quarantine fired
upstream of the export and nothing came due. So the state is asserted by a test, not recorded in a
paragraph.

⚠️ THE PRECONDITION TEST IS DELIBERATELY NOT `assert MET`. It is currently NOT MET (9 asserting
rows across 3 classes, all of them live in the authored corpus). Asserting MET would turn a known,
measured, unfixed defect into a red suite, which is how a test ends up instructing maintainers to
work around a real finding (R20 arrival point 2). It asserts instead that the COUNT HAS NOT GROWN
and that the instrument still works — and it fails loudly if someone fixes the rows without
updating the number, which is the direction worth being told about.
"""
import importlib.util
import json
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRECOND = "eval/controls/rederive_retrain_precondition_2026_10_07.py"
OVERREM = "eval/controls/audit_edit_in_place_and_overremoval_2026_10_07.py"

# Measured 2026-10-07 against the export rebuilt from the current corpus.
# 5 x paye_p9_31_march + 3 x osha_course_fee_250k + 1 x vat_threshold_dated_2024.
EXPECTED_ASSERTS = {
    "paye_p9_31_march": 5,
    "osha_course_fee_250k": 3,
    "vat_threshold_dated_2024": 1,
}
# 3 distinct correct rows, 9 quarantine-record lines, 2 quarantines.
EXPECTED_OVER_REMOVALS = 9


def _load(relpath, name):
    path = os.path.join(REPO, *relpath.split("/"))
    assert os.path.exists(path), f"{relpath} is missing"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    cwd = os.getcwd()
    try:
        spec.loader.exec_module(mod)
    finally:
        os.chdir(cwd)
    return mod


@pytest.fixture(scope="module")
def precond():
    return _load(PRECOND, "precond_under_test")


def test_the_claim_classifier_passes_its_own_specimens(precond):
    """26 planted specimens, both directions. 8 of them are rows an earlier draft wrongly flagged."""
    specimens = precond._self_test()
    assert len(specimens) >= 26, len(specimens)


def test_the_negative_specimens_are_loaded_from_the_corpus_not_retyped(precond):
    """A retyped specimen lost the only mention of its own row's subject and guarded nothing."""
    loaded = precond._corpus_negatives()
    assert len(loaded) >= 11, loaded
    for _q, body, _cls, _expect, why in loaded:
        assert body, why
        assert "cleaned_pairs" in why or "sft_shaped_pairs" in why, (
            f"a negative specimen resolved outside the AUTHORED corpus: {why}. "
            f"datasets/tier1a/sft/ is regenerated and reshuffled -- a specimen pinned there "
            f"moves on every export.")


def test_the_defect_count_in_the_training_files_has_not_grown(precond):
    """⚠️ NOT an `assert MET`. The precondition is NOT MET and that is a recorded finding."""
    art = os.path.join(REPO, *precond.ARTIFACT.split("/"))
    if not os.path.exists(art):
        pytest.skip("artifact absent; run the harness to produce it")
    got = json.load(open(art, encoding="utf-8"))
    counts = {k: len(v) for k, v in got["asserts_in_training_files"].items()}
    assert got["verdict"] == "NOT MET", (
        "the artifact now says MET. If the 9 rows have genuinely been fixed, update "
        "EXPECTED_ASSERTS to {} and this assertion with them -- do not leave a stale expectation "
        "asserting a defect that is gone.")
    new = {k: n for k, n in counts.items() if n > EXPECTED_ASSERTS.get(k, 0)}
    assert not new, (
        f"a defect class grew or appeared in the EXPORTED TRAINING FILES: {new}. Expected at "
        f"most {EXPECTED_ASSERTS}. Either a new batch reintroduced a known-wrong claim or the "
        f"export was rebuilt from a corpus that still carries one.")


def test_no_quarantine_has_removed_more_correct_rows_than_we_know_about():
    art = os.path.join(REPO, "eval", "results",
                       "edit_in_place_and_overremoval_audit_2026_10_07.json")
    if not os.path.exists(art):
        pytest.skip("artifact absent; run the harness to produce it")
    got = json.load(open(art, encoding="utf-8"))
    n = got["totals"]["over_removals"]
    assert n <= EXPECTED_OVER_REMOVALS, (
        f"{n} quarantined rows now read as CORRECT (expected at most "
        f"{EXPECTED_OVER_REMOVALS}). A rising count means another quarantine removed correct "
        f"data -- the one failure mode nothing downstream can report, because the row is gone "
        f"and the count going down looks like progress.")
    assert got["totals"]["edited_in_place_defect_survived"] == 0, (
        "a defect survived an edit-in-place: the opening sentence was repaired and the claim "
        "left standing further down. R25's containment shape -- the symptom goes, the defect "
        "stays, and no later sweep is looking.")
    assert got["totals"]["invisible_edit_defect_survived"] == 0, got["totals"]
