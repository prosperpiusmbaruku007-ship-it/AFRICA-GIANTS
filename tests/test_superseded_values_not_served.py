# -*- coding: utf-8 -*-
"""NO BUILT INDEX ROW MAY ASSERT A VALUE ITS OWN FACT DECLARES SUPERSEDED.

The durable half of the 2026-10-07 fix. The payload gate that aborted the Kaggle regen was
per-row and hand-listed: somebody had to remember to add a line for each corrected fact. Twelve
BRELA facts moved on 2026-10-06; two rows were checked by the dry run and one of the other ten was
stale — and it was caught by a gate written in the same commit as the amendment, i.e. by the one
fact whose author happened to also write its gate.

This test's population comes from the DATA: every fact carrying a `superseded_value` field, in any
domain. A thirteenth amendment enrols itself. Nobody has to remember.

⚠️ It runs the committed sweep rather than re-deriving it, because the sweep is where the polarity
device, the money boundary and the by-number comparison live, each pinned by a planted specimen
that caught a real defect in the instrument itself.
"""
import importlib.util
import json
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SWEEP_REL = "eval/index_quality/sweep_superseded_values_in_built_index.py"


def _load(relpath, name):
    path = os.path.join(REPO, *relpath.split("/"))
    assert os.path.exists(path), f"{relpath} is missing -- the sweep this test enforces is gone"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def sweep():
    cwd = os.getcwd()
    try:
        return _load(SWEEP_REL, "sweep_superseded_under_test")
    finally:
        os.chdir(cwd)


def test_the_sweep_instrument_is_sound_before_it_is_trusted(sweep):
    """Planted specimens, both directions. A broken sweep reports CLEAN and that reads as progress."""
    specimens = sweep._self_test()
    assert len(specimens) >= 10, specimens


def test_no_own_row_serves_a_superseded_value(sweep):
    cwd = os.getcwd()
    try:
        rc = sweep.main()
    finally:
        os.chdir(cwd)
    if rc:
        art = json.load(open(os.path.join(REPO, *sweep.ARTIFACT.split("/")), encoding="utf-8"))
        pytest.fail(
            "a built index row asserts a value its own fact declares superseded:\n"
            + json.dumps(art["arm1_blocking"], ensure_ascii=False, indent=2))


def test_the_population_is_data_defined_and_not_empty(sweep):
    """R20 arrival point 5: a check whose population is defined by a field name.

    If `superseded_value` is ever renamed, this test must fail rather than sweep zero facts and
    report clean. The sweep itself asserts non-emptiness; this pins the count so a population that
    SHRINKS is visible too — the 1590 -> 1589 shape, where a dropped case looks exactly like green.
    """
    facts = json.load(open(os.path.join(REPO, "scripts", "locked_facts.json"), encoding="utf-8"))
    declaring = [k for k, v in facts.items()
                 if isinstance(v, dict) and v.get("superseded_value")]
    assert len(declaring) >= 11, (
        f"only {len(declaring)} fact(s) declare a `superseded_value`; 11 did on 2026-10-07. A "
        f"shrinking population means either the field was renamed or a declaration was dropped, "
        f"and both silently remove rows from this check rather than failing it.")
