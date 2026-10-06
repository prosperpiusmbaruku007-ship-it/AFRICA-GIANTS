# -*- coding: utf-8 -*-
"""THE EDITION CONTRACT MUST BLOCK WHAT IT EXISTS TO BLOCK -- and pass a clean tree.

WHY THIS EXISTS. `fine_limit` asserted TZS 100,000 for months because it was read from
data/source_documents/nssf/nssf_act_cap50.pdf, which is REVISED EDITION 2015. R.E.2023 s.76(1)
reads ten million. Nothing in the filename, the fact's `source` field, or any check said which
edition those bytes were.

And the dangerous half is not that the check was absent -- it is that performing it against the
wrong edition RETURNS A CONFIDENT CONFIRMATION. Cap.50's offences clause is s.72 in R.E.2015
and s.76 in R.E.2023, and R.E.2015's own s.76 is a different provision ("Protection of
contributions"). So a reader who looks up "s.76(1)" in the cached PDF reads a real section of a
real Act and comes away satisfied. A citation checked against a cached PDF can CERTIFY AN ERROR.

R26 both directions, because positive-only certifies a control that blocks everything and
negative-only is what the secret scan had: a correct assertion must pass, a wrong edition must
raise, an unknown file must raise, and a file swapped under its own name must raise.
"""
import importlib.util
import json
import os
import shutil
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location(
    "check_source_editions", os.path.join(REPO, "scripts", "check_source_editions.py"))
cse = importlib.util.module_from_spec(_spec)
sys.modules["check_source_editions"] = cse
_spec.loader.exec_module(cse)

NSSF = "nssf/nssf_act_cap50.pdf"

# ⛔ THE CACHED DOCUMENTS ARE GITIGNORED (`data/**/*`); ONLY THE MANIFEST IS COMMITTED.
#
# Found 2026-10-06, the same day this file was written and reported as shipped: MANIFEST.json
# was swallowed by that same rule, so the edition contract existed on one laptop only. This
# test suite was committed and PASSED here while it would have failed in any fresh clone with
# "no MANIFEST.json" -- the suite's green was a property of this machine. Closed by un-ignoring
# the manifest (two lines: git does not descend into an excluded DIRECTORY, so un-ignoring only
# the file has no effect).
#
# The documents themselves stay ignored on purpose -- large and re-fetchable. So in a fresh
# clone the manifest is present and the bytes are not, and the byte-level limbs below CANNOT
# run. They are SKIPPED WITH A REASON rather than silently passing, per R26's rule that a
# census which quietly omits what it cannot exercise reports a cleaner result than it earned.
CORPUS_PRESENT = os.path.isdir(cse.ROOT) and os.path.exists(os.path.join(cse.ROOT, NSSF))
needs_corpus = pytest.mark.skipif(
    not CORPUS_PRESENT,
    reason="cached source documents are gitignored and absent in this checkout; the manifest "
           "is committed but its bytes are not, so byte-level verification cannot run here")


# --- limbs that work EVERYWHERE, manifest-only --------------------------------------------

def test_the_manifest_is_committed_and_readable():
    """The defect this caught: the manifest was ignored, so nothing below it could ever run in
    a clone. If this fails, the un-ignore in .gitignore was reverted."""
    man = cse.load_manifest()
    assert man["files"], "the manifest has no file entries"
    assert man["counts"]["files"] == len(man["files"])


# --- the CLEAN case ------------------------------------------------------------------------

@needs_corpus
def test_the_live_manifest_verifies():
    """A control that cannot pass a clean tree is not a control, it is an outage."""
    assert cse.check() == 0


@needs_corpus
def test_a_correct_edition_assertion_PASSES():
    entry = cse.assert_edition(NSSF, "R.E. 2015")
    assert entry["superseded"] is True
    assert "2015" in entry["edition"]


# --- and each limb, planted ---------------------------------------------------------------

@needs_corpus
def test_asserting_the_WRONG_edition_RAISES():
    """The founding case. Asking this file for R.E.2023 must fail loudly, because reading
    R.E.2015 while believing it is R.E.2023 is exactly how the 100x error was produced AND
    confirmed."""
    with pytest.raises(AssertionError) as e:
        cse.assert_edition(NSSF, "R.E. 2023")
    msg = str(e.value)
    assert "R.E. 2015" in msg
    assert "fine_limit" in msg or "100x" in msg, (
        "the failure message must say WHY this matters -- a bare mismatch invites the reader "
        "to loosen the assertion rather than go find the right edition")


@needs_corpus
def test_an_UNKNOWN_file_RAISES_rather_than_being_skipped():
    """An undeclared cached source has no known edition, and 'no known edition' is precisely
    the state fine_limit was verified against. Skipping it would reproduce that state while
    reporting success."""
    with pytest.raises(AssertionError) as e:
        cse.assert_edition("nssf/not_a_real_cached_file.pdf", "R.E. 2023")
    assert "not in the source manifest" in str(e.value)


@needs_corpus
def test_a_file_SWAPPED_UNDER_ITS_NAME_RAISES(tmp_path):
    """The edition is a claim about BYTES, not about a path. If the file changes, the declared
    edition stops being a statement about what is there -- and a stale declaration is worse
    than none, because it is trusted.

    Planted by overwriting the real file and restoring it afterwards, so this exercises the
    actual hash comparison rather than a mock of it.
    """
    full = os.path.join(cse.ROOT, NSSF)
    backup = tmp_path / "backup.pdf"
    shutil.copy2(full, backup)
    try:
        with open(full, "ab") as fh:
            fh.write(b"\n%planted-byte-for-the-swap-test\n")
        with pytest.raises(AssertionError) as e:
            cse.assert_edition(NSSF, "R.E. 2015")
        assert "FILE CHANGED UNDER ITS NAME" in str(e.value)
    finally:
        shutil.copy2(backup, full)
    # and the restore must leave the tree clean, or this test has broken the repo
    cse.assert_edition(NSSF, "R.E. 2015")


# --- the declarations themselves -----------------------------------------------------------

@needs_corpus
def test_the_superseded_act_names_its_replacement_and_the_renumbering():
    """A 'superseded' flag with no pointer sends the reader looking. The replacement's routes
    and the renumbering offsets are the two things they will need."""
    entry = cse.assert_edition(NSSF, "R.E. 2015")
    assert "R.E. 2023" in entry["superseded_by"]
    assert "oagmis" in entry["superseded_by"] or "nssf.go.tz" in entry["superseded_by"]
    dnv = entry["do_not_verify_against"]
    assert "s.76" in dnv and "s.72" in dnv, (
        "the s.72/s.76 shift is the specific trap this file carries; naming it is the point")


def test_the_empty_cached_source_is_DECLARED_not_silently_present():
    """nssf_ulipaji_mchango.txt is 0 bytes. Anything 'verified against' it was verified against
    nothing, and that verification would have looked exactly like a successful one -- R26's
    inert control, in the source layer. It must be declared, not merely tolerated."""
    man = cse.load_manifest()["files"]
    e = man["nssf/nssf_ulipaji_mchango.txt"]
    assert e["bytes"] == 0
    assert "0 BYTES" in e["edition"]


def test_NOTHING_is_verified_against_the_zero_byte_source():
    """⭐ THE CENSUS CAME BACK EMPTY, AND THAT IS THE FINDING -- recorded as an assertion so it
    stays true rather than as a grep that was run once.

    `nssf/nssf_ulipaji_mchango.txt` is 0 bytes, and the fear was obvious: anything "verified
    against" it was verified against nothing, and that verification would have looked exactly
    like a successful one. So the question was which facts rested on it.

    THE ANSWER IS NONE, and the pipeline is why. `data/raw/processed_files.json` records
    `"zero_facts": true` for this path and the extraction record carries `"content": ""` with
    md5 d41d8cd98f00b204e9800998ecf8427e -- the md5 of the empty string. The extractor saw an
    empty file, derived nothing, and said so. Zero locked facts cite it; zero corpus or gold
    rows cite it.

    Worth stating plainly rather than manufacturing a worklist: the control that mattered here
    WORKED, and the honest report is a clean one. What remains is not a verification defect but
    a COVERAGE gap -- that page's content was never captured -- and it is now moot, because
    s.14(1) is grounded directly in Cap.50 R.E.2023 and two other captures of the equivalent
    portal page exist.

    The one residual blemish: the extraction record cites `source_url: "nssf.or.tz"`, the
    DNS-failing domain the corpus-wide rewrite exists for. Noted, not load-bearing, since no
    fact descends from it.
    """
    facts = json.load(open(os.path.join(REPO, "scripts", "locked_facts.json"),
                           encoding="utf-8"))
    citing = [k for k, v in facts.items()
              if isinstance(v, dict) and "ulipaji_mchango" in json.dumps(v, ensure_ascii=False)]
    assert not citing, (
        f"{citing} now cite the ZERO-BYTE source data/source_documents/nssf/"
        f"nssf_ulipaji_mchango.txt. A fact resting on an empty file is unverified no matter "
        f"what its status field says -- re-check the claim against Cap.50 R.E.2023 and cite "
        f"that, or mark the fact unverified. Do NOT point it at the empty file.")

    # And no training pair or gold row may cite it either.
    import glob
    offenders = []
    for pat in ("datasets/tier1a/**/*.jsonl", "eval/**/*.jsonl"):
        for p in glob.glob(os.path.join(REPO, pat), recursive=True):
            body = open(p, encoding="utf-8", errors="replace").read()
            if "ulipaji_mchango" in body or "ulipaji-mchango" in body:
                offenders.append(os.path.relpath(p, REPO))
    assert not offenders, (
        f"{offenders} cite the zero-byte source. Same reasoning as above.")


def test_the_duplicate_brela_capture_is_declared_as_one_capture_not_two():
    """`brela_ada_kampuni_v2.html` is BYTE-IDENTICAL to `brela_ada_kampuni.html`. The '_v2'
    suffix asserts a second observation that does not exist, and the BRELA fee dispute turns on
    whether the page was read twice. Reading the filename instead of the bytes is R34."""
    man = cse.load_manifest()["files"]
    a = man["brela/brela_ada_kampuni.html"]
    b = man["brela/brela_ada_kampuni_v2.html"]
    assert a["sha256"] == b["sha256"]
    assert "BYTE-IDENTICAL" in b["edition"]


@needs_corpus
def test_no_fact_rests_ONLY_on_a_superseded_cached_source():
    """⛔ THE WIRING THAT MAKES THE MANIFEST DO SOMETHING. A manifest nothing consults is a
    document, not a control (R26: the index contract fired on all three limbs and production
    never imported it).

    14 locked facts still name data/source_documents/nssf/nssf_act_cap50.pdf -- the R.E.2015
    copy -- in their legacy `source` field. That field is kept deliberately (R27: a correction
    amends the fields the defect requires and leaves provenance alone), and on its own it is
    harmless history. What is NOT harmless is a fact whose ONLY basis is that file, because
    that is precisely the state `fine_limit` was in: a real citation to a real document, read
    confidently, 100x wrong, with the error undetectable from the fact object.

    So the invariant is not "never mention the superseded file" -- it is "never rest on it
    alone". A fact naming it must also carry a current primary_source or verified_by naming
    R.E.2023. A NEW NSSF fact sourced only to the cached PDF fails here.
    """
    facts = json.load(open(os.path.join(REPO, "scripts", "locked_facts.json"),
                           encoding="utf-8"))
    man = cse.load_manifest()["files"]
    superseded_paths = [p for p, e in man.items() if e["superseded"]]
    assert superseded_paths, "no source is flagged superseded -- this test would be vacuous"
    basenames = [p.split("/")[-1] for p in superseded_paths]

    naming, resting_only = [], []
    for key, v in facts.items():
        if not isinstance(v, dict):
            continue
        blob = json.dumps(v, ensure_ascii=False)
        if not any(b in blob for b in basenames):
            continue
        naming.append(key)
        current = f"{v.get('primary_source') or ''} {v.get('verified_by') or ''}"
        if "R.E.2023" not in current and "R.E. 2023" not in current:
            resting_only.append(key)

    assert naming, (
        "no fact names the superseded cached source any more. If the legacy `source` fields "
        "were cleaned up, delete this test rather than leaving it to pass vacuously.")
    assert not resting_only, (
        f"{len(resting_only)} fact(s) rest on the SUPERSEDED R.E.2015 cached PDF with no "
        f"current R.E.2023 citation: {resting_only}. That is the exact state fine_limit was in "
        f"-- and reading a renumbered edition returns a confident WRONG confirmation, not an "
        f"error. Re-read the provision in Cap.50 R.E.2023 (see the manifest's superseded_by "
        f"routes) and cite it, rather than removing the `source` field.")


def test_undeclared_sources_are_COUNTED_so_the_gap_cannot_go_quiet():
    """52 of 61 cached sources have no edition marker in them at all. That is the honest number
    and it must stay visible: a manifest that reported only the 9 declared files would read as
    complete coverage. This asserts the count is tracked, and SHRINKS-ONLY -- declaring more is
    progress, silently dropping one from the census is not.
    """
    man = cse.load_manifest()
    undeclared = man["counts"]["undeclared"]
    assert man["counts"]["files"] == 62, (
        f"the source tree changed size ({man['counts']['files']} files) -- rebuild the manifest "
        f"and re-derive this number rather than editing it")
    assert undeclared <= 52, (
        f"{undeclared} undeclared sources, up from 52. A new cached source must arrive WITH its "
        f"edition read from the document, not be added and declared later.")
