"""Regression guard for the 2026-09-05 TypeError: `KNOWN_FAILING = { <comments only> }`
is an empty DICT literal in Python (no `key: value` pairs, no bare elements -> dict, not
set), which broke `KNOWN_FAILING - _known_fail_seen` in kaggle/regenerate_rag_e5.py the
instant the last tracked name was removed -- and nothing caught it locally because no
dry-run script executes that file's own KNOWN_FAILING/_orphans logic; it was only found
by actually running the kernel on Kaggle (R18/R24: a check never run is not a check that
passed).

AST-extracts the value rather than importing the module (importing it has Kaggle-auth /
network side effects at import time, same reason eval/grounding/measure_fact_reach.py
uses AST for `critical_queries`).
"""
import ast
import os

REGEN_SCRIPT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             'kaggle', 'regenerate_rag_e5.py')


def _known_failing_value():
    with open(REGEN_SCRIPT, encoding='utf-8') as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        target = getattr(node, 'target', None) or (node.targets[0] if isinstance(
            node, ast.Assign) else None)
        if getattr(target, 'id', None) == 'KNOWN_FAILING':
            return ast.literal_eval(node.value)
    raise AssertionError('KNOWN_FAILING assignment not found -- has it been renamed?')


def test_known_failing_is_a_set_not_a_dict():
    """The exact bug: an empty `{}` with no elements parses as dict in Python. Whatever
    is currently in KNOWN_FAILING (empty or not), it must be a set -- `KNOWN_FAILING -
    _known_fail_seen` in regenerate_rag_e5.py requires it."""
    value = _known_failing_value()
    assert isinstance(value, set), (
        f"KNOWN_FAILING is a {type(value).__name__}, not a set -- this is exactly the "
        f"2026-09-05 bug: an empty `{{}}` with only comments inside parses as a dict. "
        f"Use `KNOWN_FAILING: set = set()` when emptying it, never a bare `{{}}`.")
