# -*- coding: utf-8 -*-
"""TEST-FILE-MUTATION-1 guard (founder, 2026-11-26). On 2026-11-26 a killed bare `pytest` left tests/test_routing.py and tests/test_terminology_2026_11_25.py EMPTY and added a duplicated key to
tests/test_fixed_statements.py (the cause: scratch/test_fixes_b4.py and b6.py, patch scripts named test_*.py that a bare `pytest` collects and EXECUTES on import). Nothing was red: a damaged suite just collected
fewer tests, so the only trace was a count (4,986 -> 4,943). Two checks, both OFFLINE, both planted (R26):
  1. the number of tests COLLECTED under tests/ may not fall below a pinned FLOOR (shrink-only is a finding; raise the floor consciously when tests are ADDED, never lower it to make a red go green);
  2. no TRACKED file under tests/ may be empty (a truncated test file collects zero tests and looks like a clean one).
The floor is COLLECTED (passed + skipped + xfailed), not "passed": 4,986 on 2026-11-26 = 4,967 passed + 5 skipped + 14 xfailed."""
import os
import re
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLLECTED_FLOOR = 4986                                   # tests collected under tests/ at 2026-11-26, BEFORE this file's own tests were added. Raise it; never lower it.
EMPTY_BY_DESIGN = {".gitkeep", "__init__.py"}            # basenames of tracked files that are legitimately empty (2 exist today)


def parse_collected(output: str) -> int:
    """`4986/4992 tests collected (6 deselected)` or `4986 tests collected`. Raises when it cannot read a count: cannot-evaluate is not a pass."""
    m = re.search(r"(\d+)(?:/\d+)? tests? collected", output)
    if not m:
        raise AssertionError("could not read a collected count from pytest's output; a guard that cannot evaluate must not pass")
    return int(m.group(1))


def floor_problem(collected: int, floor: int = COLLECTED_FLOOR):
    return None if collected >= floor else f"collected {collected} tests, below the pinned floor {floor}: a test file was emptied, truncated or removed"


def empty_tracked_files(paths):
    """Paths (absolute) that exist and are 0 bytes, minus the by-design empties. A path that does not exist is reported too (a tracked file that vanished)."""
    out = []
    for p in paths:
        if os.path.basename(p) in EMPTY_BY_DESIGN:
            continue
        if not os.path.exists(p) or os.path.getsize(p) == 0:
            out.append(p)
    return out


def tracked_test_files():
    out = subprocess.check_output(["git", "ls-files", "tests"], cwd=ROOT).decode("utf-8").splitlines()
    return [os.path.join(ROOT, f) for f in out if f.strip()]


def test_the_tracked_listing_is_not_vacuous():
    assert len(tracked_test_files()) > 100, "git ls-files returned almost nothing: the empty-file check below would pass on nothing (R20)"


def test_no_tracked_file_under_tests_is_empty():
    assert empty_tracked_files(tracked_test_files()) == []


def test_the_collected_count_is_at_or_above_the_floor():
    proc = subprocess.run([sys.executable, "-m", "pytest", "tests", "--collect-only", "-q", "-p", "no:cacheprovider"], cwd=ROOT, capture_output=True, text=True, timeout=300)
    n = parse_collected(proc.stdout + proc.stderr)
    assert floor_problem(n) is None, floor_problem(n)


# ---- plants: each check must be shown to fire, and to pass a clean case ----------------------------------------------------------------------------------------------------------------------------
def test_PLANT_a_count_below_the_floor_is_a_problem_and_at_or_above_is_not():
    assert floor_problem(COLLECTED_FLOOR - 1) is not None and floor_problem(COLLECTED_FLOOR) is None and floor_problem(COLLECTED_FLOOR + 40) is None
    assert floor_problem(4943) is not None, "the real 2026-11-26 damage (4,943 collected) must be caught"


def test_PLANT_an_emptied_file_is_flagged_and_a_clean_or_by_design_empty_file_is_not(tmp_path):
    emptied, clean = tmp_path / "test_x.py", tmp_path / "test_y.py"
    emptied.write_text("")
    clean.write_text("def test_a():\n    pass\n")
    keep, init = tmp_path / ".gitkeep", tmp_path / "__init__.py"
    keep.write_text("")
    init.write_text("")
    gone = tmp_path / "test_vanished.py"
    assert empty_tracked_files([str(emptied), str(clean), str(keep), str(init), str(gone)]) == [str(emptied), str(gone)]


def test_PLANT_the_parser_reads_both_summary_forms_and_refuses_garbage():
    assert parse_collected("4986/4992 tests collected (6 deselected) in 3.6s") == 4986
    assert parse_collected("120 tests collected in 0.1s") == 120
    with pytest.raises(AssertionError):
        parse_collected("ERROR collecting tests/test_x.py")
