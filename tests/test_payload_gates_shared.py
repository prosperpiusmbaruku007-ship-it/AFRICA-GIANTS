# -*- coding: utf-8 -*-
"""THE DRY RUN MUST EXECUTE THE GATES THE REAL RUN ENFORCES — watched failing, both directions.

⛔ WHAT WENT WRONG, 2026-10-06. The local dry run reported `VERDICT: SAFE TO RUN`. The Kaggle
regen, on the same commit, aborted before uploading anything:

    [FATAL] brela_foreign_late_filing_penalty ASSERTS the superseded value ['USD 25']

The dry run did not execute the regen's payload gates. It re-implemented a subset of them — five
hand-written assertions about the two rows whoever wrote it remembered changing, while twelve
facts had been amended. R33 in the validator layer.

R26 is the standard this file is held to: a control is not working until you have watched it block
the thing it exists to block, AND pass a clean case. So:

  * the clean case is the repo as it stands — eleven gates, all green;
  * the blocking case plants THE EXACT PRE-FIX ROW TEXT and asserts the shared gate raises, which
    is the same abort Kaggle produced. Watched, not reasoned about.
  * and both call sites are asserted to CALL the shared module rather than name it in a comment,
    by reading code lines only — three separate checks in the 2026-08-24 control audit matched the
    COMMENT explaining why a defect had been removed.
"""
import importlib.util
import io
import os
import re
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATES_REL = "scripts/rag_payload_gates.py"
REGEN_REL = "kaggle/regenerate_rag_e5.py"
DRYRUN_REL = "eval/index_quality/dryrun_regen_2026_10_06.py"

# The row text as it stood at d1523e9 — the commit the Kaggle run aborted on. Kept verbatim so the
# planted specimen is the real defect and not a paraphrase of it (R26: a five-word paraphrase was
# enough to flip a correct body into a flagged one).
PRE_FIX_ROW = ('Kampuni ya kigeni (Companies Act Cap.212, Part XII, ss.437-447) ikichelewa '
               'kuwasilisha ritani ya mwaka: faini ni USD 25 kwa kila mwezi (tofauti na kampuni '
               'za ndani ambazo hulipa TZS 2,500 kwa mwezi).')


def _load(relpath, name):
    path = os.path.join(REPO, *relpath.split("/"))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _code_lines(relpath):
    """Source with comments stripped, so a check cannot pass on the prose that explains it."""
    src = io.open(os.path.join(REPO, *relpath.split("/")), encoding="utf-8").read()
    return "\n".join(line.split("#", 1)[0] for line in src.splitlines())


@pytest.fixture(scope="module")
def built():
    pc = _load("scripts/precompute_rag_embeddings.py", "precompute_for_gate_test")
    texts, keys, _dropped = pc.build_fact_texts()
    return keys, texts


@pytest.fixture(scope="module")
def gates():
    return _load(GATES_REL, "rag_payload_gates_under_test")


def test_the_shared_gates_pass_on_the_repo_as_it_stands(built, gates):
    """THE CLEAN CASE. Positive-only certifies a control that blocks everything."""
    keys, texts = built
    n = gates.run_payload_gates(keys, texts)
    assert n >= 11, (
        f"only {n} gates ran. Five bespoke + six table rows = eleven. A gate list that shrinks "
        f"silently is R20's check that cannot fail.")


def test_the_shared_gates_BLOCK_the_exact_row_that_aborted_kaggle(built, gates):
    """THE BLOCKING CASE, with the pre-fix bytes — this is the demonstration, not the reasoning."""
    keys, texts = built
    i = keys.index("brela_foreign_late_filing_penalty")
    planted = list(texts)
    planted[i] = PRE_FIX_ROW
    with pytest.raises(AssertionError) as exc:
        gates.run_payload_gates(keys, planted)
    msg = str(exc.value)
    assert "ASSERTS the superseded value" in msg and "USD 25" in msg, (
        f"it raised, but not for the reason Kaggle did. Got:\n{msg}")


def test_the_current_row_states_the_figure_brela_publishes(built):
    """The fix itself, pinned to the figure rather than to 'not USD 25'."""
    keys, texts = built
    row = texts[keys.index("brela_foreign_late_filing_penalty")]
    assert "TZS 70,000" in row, row
    assert not re.search(r"USD\s*25\b", row, re.I), row
    # ⚠️ AND IT MUST STAY SHORT. The row-57 measurement: 415 chars -> rank 4, 172 -> rank 1, same
    # content. The group passage brela_filing_fees carries the explicit "SI USD 25" contradiction
    # for the trained prior, so this row does not need one and must not grow one.
    assert len(row) <= 240, (
        f"{len(row)} chars. Length is what costs rank, not correctness -- if this row needs to "
        f"grow, re-measure it (eval/index_quality/) rather than assuming the cost is zero.")


def test_the_regen_CALLS_the_shared_gates_and_refuses_to_run_without_them():
    code = _code_lines(REGEN_REL)
    assert "run_payload_gates(fact_keys, fact_texts_to_embed)" in code, (
        "the regen no longer calls the shared gates. Naming the module in a comment is not "
        "calling it.")
    assert GATES_REL in code, f"{GATES_REL} is not referenced in the regen's code lines"
    assert "raise SystemExit(" in code and "os.path.exists(_gates_path)" in code, (
        "the regen must ABORT when the gates module is absent. A run with no payload gates "
        "succeeds, prints nothing missing, and uploads whatever it built.")
    # And the raw-fetch path must bring the file, or the Kaggle no-checkout path has no gates.
    assert f"'{GATES_REL}'," in code, (
        f"{GATES_REL} is not in SOURCE_FILES. On the raw-fetch path the file would be absent and "
        f"the run would abort -- loudly, but needlessly.")


def test_the_dryrun_CALLS_the_shared_gates_instead_of_re_deriving_them():
    code = _code_lines(DRYRUN_REL)
    assert "run_payload_gates(keys, texts)" in code, (
        "the dry run does not execute the shared gates. This is the exact defect of 2026-10-06: "
        "it re-implemented a subset and reported SAFE TO RUN on a package the real run refused.")
    assert "n_gates >= 11" in code, (
        "the dry run must assert the gate COUNT too. Executing a shrunken gate list is the same "
        "failure in slower motion.")
    # The hand-written subset must be GONE, not merely supplemented -- two sources of truth is
    # how they drift apart again.
    for stale in ('"hadi TZS 100,000,000 ni TZS 400,000" in _ladder',
                  '"faini ya kuchelewa TZS 70,000" in _filing'):
        assert stale not in code, (
            f"the re-implemented assertion {stale!r} is still in the dry run. Keeping both a "
            f"copy and the shared call recreates the divergence this fix removes.")


def test_the_move_was_pure_the_gate_bodies_are_the_bytes_that_ran_on_kaggle():
    """The gates were MOVED, not rewritten. Spot-check the load-bearing literals survived.

    Not a full diff — the extractor asserted the block referenced no free name beyond the two
    parameters, and this pins the pieces a careless re-indent would drop.
    """
    code = _code_lines(GATES_REL)
    for needle in [
        "r'part\\s*xiii\\b|ss?\\.?\\s*320\\s*[-–]\\s*328'",   # the inverted Part XII gate
        "'minimum_turnover_tax'",
        "'OSHA_safety_officer_threshold'",
        "'rent_wht_rate'",
        "_require_contradiction",                              # the fifth tuple element
        "(?:\\bsi\\b|\\bnot\\b|\\bsio\\b|\\bhapana\\b)",       # the polarity device
    ]:
        assert needle in code, (
            f"{needle!r} is missing from {GATES_REL}. The move was supposed to be verbatim; a "
            f"gate that lost its pattern is worse than one that was never moved.")
