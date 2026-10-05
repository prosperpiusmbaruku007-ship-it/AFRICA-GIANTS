# -*- coding: utf-8 -*-
"""THE DATASET GATE MUST BLOCK WHAT IT CLAIMS TO BLOCK — and must PASS a clean corpus.

WHY THIS EXISTS. Until 2026-10-05 `scripts/validate_dataset.py` reported 46,881 errors across
4,416 pairs and exited 1 on EVERY invocation. CLAUDE.md Section 9 makes it blocking ("must exit 0
before any pair advances"), so in practice it was ignored — and an ignored blocking gate is an
absent one. It is the same inert-control shape as the pre-push hook that scanned zero files
(R26), arriving in a validator rather than a hook.

R26 says a control is not working until you have watched it block the thing it exists to block,
AND pass a clean case. Positive-only certifies a gate that blocks everything, which is exactly
what this gate had become; negative-only is what the secret scan had. Both directions, five
planted failures, one clean pass.

The diagnosis the rewrite rests on, re-derived here rather than trusted: the 18-field schema is
NOT wrong — 1,715 pairs in `batch_NNN_cleaned.jsonl` satisfy it. 2,705 rows in
`cleaned_pairs_batch_NNN.jsonl` are SFT-shaped and carry no provenance at all. Two pipeline
generations, one directory, a filename convention between them.
"""
import json
import os
import subprocess
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VALIDATOR = os.path.join(REPO, "scripts", "validate_dataset.py")
sys.path.insert(0, os.path.join(REPO, "scripts"))


def _run(datasets_root):
    """Run the real validator against a planted datasets tree, in a subprocess, so the exit
    code is the thing under test rather than an exception we interpret."""
    code = (
        "import json,sys,pathlib;"
        f"sys.path.insert(0,{os.path.join(REPO, 'scripts')!r});"
        "import validate_dataset as v;"
        f"v.DATASETS_ROOT=pathlib.Path({str(datasets_root)!r});"
        "v.main()")
    return subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def _good_pair():
    with open(os.path.join(REPO, "schema", "pair_schema.json"), encoding="utf-8") as fh:
        schema = json.load(fh)
    allowed = schema["allowed_values"]
    pair = {}
    for f in schema["required"]:
        if f in allowed:
            pair[f] = allowed[f][0]
        elif f == "primary_source_url":
            pair[f] = "https://www.tra.go.tz/page/pay-as-you-earn"
        else:
            pair[f] = "x"
    return pair


def _plant(tmp_path, filename, rows):
    d = tmp_path / "tier1a" / "cleaned_pairs"
    d.mkdir(parents=True, exist_ok=True)
    with open(d / filename, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    return tmp_path


# --- the CLEAN case first. A gate that blocks everything passes every planted test. ---------

def test_a_clean_schema_shaped_corpus_PASSES(tmp_path):
    root = _plant(tmp_path, "batch_001_cleaned.jsonl", [_good_pair(), _good_pair()])
    r = _run(root)
    assert r.returncode == 0, (
        f"a fully compliant corpus was rejected — the gate is overbroad.\n{r.stdout}\n{r.stderr}")
    assert "VALIDATION PASSED" in r.stdout


# --- and now each limb, planted. ------------------------------------------------------------

def test_a_missing_required_field_BLOCKS(tmp_path):
    bad = _good_pair()
    del bad["verified_by"]
    root = _plant(tmp_path, "batch_001_cleaned.jsonl", [_good_pair(), bad])
    r = _run(root)
    assert r.returncode == 1, f"R3 violation not blocked:\n{r.stdout}"
    assert "Missing field: verified_by" in r.stdout


def test_an_unwhitelisted_domain_BLOCKS(tmp_path):
    bad = _good_pair()
    bad["primary_source_url"] = "https://example-not-a-regulator.com/page"
    root = _plant(tmp_path, "batch_001_cleaned.jsonl", [bad])
    r = _run(root)
    assert r.returncode == 1, f"an unapproved source domain was accepted:\n{r.stdout}"
    assert "not whitelisted" in r.stdout


def test_a_www_prefixed_whitelisted_domain_is_ACCEPTED(tmp_path):
    """The validator bug that produced 58 of the 110 original errors.

    `sources/whitelist.json` stores `tanzlii.org` bare while storing 17 other hosts WITH a
    `www.` prefix, so exact netloc comparison rejected `www.tanzlii.org` — a host CLAUDE.md
    Section 4 names as a Tier 1A TRAINING source. The pairs were right; the comparison was
    wrong. This asserts the fix, so a future "tightening" that restores exact matching fails
    here instead of silently rejecting 58 correct pairs again.
    """
    ok = _good_pair()
    ok["primary_source_url"] = "https://www.tanzlii.org/tz/legislation/act/2019/11"
    r = _run(_plant(tmp_path, "batch_001_cleaned.jsonl", [ok]))
    assert r.returncode == 0, f"www.tanzlii.org rejected again:\n{r.stdout}"


def test_a_NEW_sft_shaped_file_BLOCKS(tmp_path):
    """The SFT exception may only shrink. A new metadata-free file in cleaned_pairs/ is an R3
    violation, not a new normal — otherwise the exception becomes the place pairs go to escape
    the schema, which is the forgetting failure it exists to prevent."""
    sft = {"instruction": "swali", "input": "", "output": "jibu", "system": "s"}
    root = _plant(tmp_path, "cleaned_pairs_batch_099.jsonl", [sft])
    r = _run(root)
    assert r.returncode == 1, f"a new SFT-shaped file was accepted:\n{r.stdout}"
    assert "NEW SFT-SHAPED FILE" in r.stdout


def test_a_GROWN_sft_file_BLOCKS(tmp_path, monkeypatch):
    """A frozen count that is not actually compared is the vacuous shape (R20).

    SFT_SHAPED_EXCEPTION is EMPTY since the 2026-10-05 move (all 8 files went to
    sft_shaped_pairs/), so the growth limb has nothing live to exercise it — exactly the
    mis-composed-fixture shape R20 warns about, where a check runs on every invocation and can
    never report anything. A listed file is injected here so the comparison itself is proven to
    work, and would be the limb that fires if a future decision ever re-lists one.
    """
    sft = {"instruction": "swali", "input": "", "output": "jibu", "system": "s"}
    root = _plant(tmp_path, "cleaned_pairs_batch_009.jsonl", [dict(sft) for _ in range(3)])
    code = (
        "import json,sys,pathlib;"
        f"sys.path.insert(0,{os.path.join(REPO, 'scripts')!r});"
        "import validate_dataset as v;"
        "v.SFT_SHAPED_EXCEPTION={'cleaned_pairs_batch_009.jsonl': 2};"
        f"v.DATASETS_ROOT=pathlib.Path({str(root)!r});"
        "v.main()")
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    assert r.returncode == 1, f"a grown SFT file was accepted:\n{r.stdout}"
    assert "GREW" in r.stdout


def test_the_exception_is_empty_so_ANY_sft_file_in_cleaned_pairs_blocks():
    """The move's protection, asserted. With SFT_SHAPED_EXCEPTION empty, every SFT-shaped file
    in cleaned_pairs/ is unlisted and therefore blocks — so the two pipeline generations cannot
    silently re-merge into one directory, which is the confusion the move resolved."""
    import validate_dataset as v
    assert v.SFT_SHAPED_EXCEPTION == {}, (
        "the SFT exception is no longer empty. If a file was deliberately re-listed, say why at "
        "the site; if one reappeared in cleaned_pairs/, that is the regression this guards.")


def test_a_row_matching_NEITHER_shape_BLOCKS(tmp_path):
    """A third pipeline generation would arrive looking exactly like this, and the whole defect
    being fixed was two generations sharing one directory unnoticed."""
    root = _plant(tmp_path, "batch_001_cleaned.jsonl", [{"q": "swali", "a": "jibu"}])
    r = _run(root)
    assert r.returncode == 1, f"an unrecognised row shape was accepted:\n{r.stdout}"
    assert "NEITHER SHAPE" in r.stdout


def test_an_EMPTY_corpus_exits_2_and_is_not_read_as_a_pass(tmp_path):
    """Cannot-evaluate is not passed. Exit 2 so an `&&` chain cannot mistake it for success —
    the same fix already applied to run_eval.py's empty-corpus path, which used to exit 0."""
    (tmp_path / "tier1a" / "cleaned_pairs").mkdir(parents=True)
    r = _run(tmp_path)
    assert r.returncode == 2, f"an empty corpus did not exit 2:\n{r.stdout}"
    assert "GATE NOT RUN" in r.stdout and "NOT a pass" in r.stdout


def test_the_real_corpus_currently_passes_and_its_exceptions_are_unchanged():
    """The live state, asserted so a regression in the compliant half is loud.

    This is the assertion that was IMPOSSIBLE before the rewrite: the gate failed on everything,
    so it could not distinguish a regression from the status quo.
    """
    r = subprocess.run([sys.executable, VALIDATOR], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=REPO)
    assert r.returncode == 0, (
        f"the real corpus no longer passes the dataset gate:\n{r.stdout[-3000:]}")
    assert "schema-shaped: 1715 pairs, 0 errors" in r.stdout, (
        f"the schema-shaped corpus changed size or cleanliness; re-derive before updating this "
        f"number:\n{r.stdout[-1500:]}")


# --- the deliberately-unsourced exception, both directions ----------------------------------

def test_an_UNLISTED_pair_with_a_blank_source_BLOCKS(tmp_path):
    """The 12 blanked GN 605A pairs are excused by ID. An unlisted pair must not be.

    Without this the exception is a hole rather than a worklist: any pair could acquire a blank
    primary_source_url and pass. The 12 exist because their citation pointed at a host with no
    DNS record and there is no live destination to repoint to -- a specific, recorded situation,
    not a general licence to drop provenance.
    """
    bad = _good_pair()
    bad["id"] = "not_on_the_unsourced_list"
    bad["primary_source_url"] = ""
    bad["primary_source_name"] = ""
    r = _run(_plant(tmp_path, "batch_001_cleaned.jsonl", [bad]))
    assert r.returncode == 1, f"an unlisted pair with a blank source was accepted:\n{r.stdout}"
    assert "Empty field: primary_source_url" in r.stdout


def test_a_LISTED_pair_with_a_blank_source_PASSES(tmp_path):
    """And the listed ones must pass, or the gate is back to failing on everything -- the state
    it was rewritten today to escape."""
    import validate_dataset as v
    listed = sorted(v.UNSOURCED_PAIR_EXCEPTION)[0]
    ok = _good_pair()
    ok["id"] = listed
    ok["primary_source_url"] = ""
    ok["primary_source_name"] = ""
    r = _run(_plant(tmp_path, "batch_001_cleaned.jsonl", [ok]))
    assert r.returncode == 0, (
        f"a listed deliberately-unsourced pair was rejected:\n{r.stdout}")


def test_the_unsourced_exception_excuses_ONLY_the_source_fields(tmp_path):
    """A listed pair is excused on provenance, NOT on the rest of the 18-field contract.

    This is the limb that keeps the exception narrow. If being on the list excused any empty
    field, the 12 would become 12 rows exempt from the schema entirely -- which is how a
    tracked exception quietly becomes an untracked one.
    """
    import validate_dataset as v
    listed = sorted(v.UNSOURCED_PAIR_EXCEPTION)[0]
    bad = _good_pair()
    bad["id"] = listed
    bad["primary_source_url"] = ""
    bad["primary_source_name"] = ""
    bad["verified_by"] = ""          # NOT a source field; must still fail
    r = _run(_plant(tmp_path, "batch_001_cleaned.jsonl", [bad]))
    assert r.returncode == 1, (
        f"a listed pair was excused on a NON-source field:\n{r.stdout}")
    assert "Empty field: verified_by" in r.stdout
    assert "Empty field: primary_source_url" not in r.stdout
