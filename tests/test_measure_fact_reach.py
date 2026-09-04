"""Regression coverage for eval/grounding/measure_fact_reach.py -- the AST extraction and
categorization logic, which are the two things most likely to silently break (a renamed
`critical_queries` variable, a rank-boundary off-by-one) without a runtime error.

Does NOT test the actual retrieval measurement (needs e5-base + the deployed index --
covered by running the script directly, see its own docstring for the committed artifacts).
"""
from eval.grounding.measure_fact_reach import (
    EXTRA_BOUNDARY_PROBES,
    _categorize,
    load_probes,
)


def test_load_probes_extracts_without_importing_the_regen_script():
    """AST extraction must find critical_queries and append the boundary probes, without
    triggering kaggle/regenerate_rag_e5.py's own import-time side effects (Kaggle auth,
    network fetches, EXPECTED_HEAD ancestry check) -- if this test hangs or raises a
    network error, the extraction silently started importing the module instead."""
    probes = load_probes()
    assert len(probes) >= 34 + len(EXTRA_BOUNDARY_PROBES)
    names = [p[0] for p in probes]
    assert len(names) == len(set(names)), "duplicate probe names"
    for name, question, expected in probes:
        assert isinstance(name, str) and name
        assert isinstance(question, str) and question
        assert isinstance(expected, (list, tuple)) and expected


def test_extra_boundary_probes_are_present_in_the_loaded_set():
    """The whole reason EXTRA_BOUNDARY_PROBES exists: without it, the BOUNDARY category
    would be vacuous on the real 34-probe fixture (see module docstring). If these two
    silently stopped being appended, that regression would go unnoticed."""
    probes = load_probes()
    names = {p[0] for p in probes}
    for name, _, _ in EXTRA_BOUNDARY_PROBES:
        assert name in names


def test_categorize_boundaries():
    assert _categorize(1) == 'IN_TOP3'
    assert _categorize(3) == 'IN_TOP3'
    assert _categorize(4) == 'BOUNDARY'
    assert _categorize(16) == 'BOUNDARY'
    assert _categorize(17) == 'DEEP'
    assert _categorize(None) == 'ABSENT'
