"""REGEN BLOCKER, ENFORCED NOT REMEMBERED (R35; founder 2026-11-25, kaggle/NEXT_REGEN_QUEUE.md section 6).

The served index rows and the locked_facts text still use the bare tax-residence words ("mkazi", "wakazi"); the founder queued widening them to "mkaazi / wakaazi wa kikodi" for the NEXT regen. 17 `wrong_patterns` in scripts/locked_facts.json NAME the old wording. The moment a SERVED row says
"kikodi", every one of those patterns is BLIND to the model's new wording ("mkazi" is not a substring of "mkaazi"), and the correction-sync gate would read CLEAN while checking nothing.

THE RULE THIS FILE ENFORCES: if ANY served index row carries the widened wording, then NO wrong_pattern may still name the bare wording literally; each must accept both spellings (`mka{1,2}zi`, `waka{1,2}zi`). Today no row is widened, so the test passes; the regen that widens the rows FAILS it until the patterns move with them.
Planted both ways (R26): a widened row + an old pattern MUST be a violation; a widened row + a flexible pattern MUST NOT."""
import io
import json
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BARE_IN_PATTERN = re.compile(r"(?<![a-z])(?:mkazi|wakazi|ukazi)(?![a-z])", re.IGNORECASE)
_WIDENED_ROW = re.compile(r"(?:mkaazi|wakaazi|ukaazi) wa kikodi", re.IGNORECASE)


def blocker_violations(rows, patterns):
    """[(fact_key, pattern)] that still name the bare wording, ONLY once at least one served row carries the widened wording. Pure."""
    if not any(_WIDENED_ROW.search(r) for r in rows):
        return []
    return [(k, p) for k, p in patterns if _BARE_IN_PATTERN.search(p)]


def _patterns():
    facts = json.load(io.open(os.path.join(_ROOT, "scripts", "locked_facts.json"), encoding="utf-8"))
    return [(k, p) for k, v in facts.items() if isinstance(v, dict) for p in (v.get("wrong_patterns") or []) if _BARE_IN_PATTERN.search(p)]


def _rows():
    return json.load(io.open(os.path.join(_ROOT, "kaggle", "rag_facts_text.json"), encoding="utf-8"))


def test_the_blocker_is_recorded_in_the_queue_with_its_enforcement():
    q = io.open(os.path.join(_ROOT, "kaggle", "NEXT_REGEN_QUEUE.md"), encoding="utf-8").read()
    i = q.index("## 6.")
    sec = q[i:]
    assert "REGEN BLOCKER" in sec and "tests/test_regen_blocker_wording_2026_11_25.py" in sec and "17" in sec


def test_plant_a_widened_row_with_an_old_pattern_is_a_violation():
    rows = ["Ada ya mkurugenzi kwa asiye mkaazi wa kikodi ni asilimia 15."]
    assert blocker_violations(rows, [("wht_director_fees", "mkurugenzi.*asiye mkazi.*asilimia 20")])


def test_plant_a_widened_row_with_a_flexible_pattern_is_clean():
    rows = ["Ada ya mkurugenzi kwa asiye mkaazi wa kikodi ni asilimia 15."]
    assert not blocker_violations(rows, [("wht_director_fees", "mkurugenzi.*asiye mka{1,2}zi.*asilimia 20")])


def test_plant_no_widened_row_means_no_violation_even_with_old_patterns():
    assert not blocker_violations(["Ada ya mkurugenzi kwa asiye mkazi ni asilimia 15."], [("wht_director_fees", "asiye mkazi")])


def test_the_live_state_rows_and_patterns_move_together():
    """Today: no served row is widened (so no violation) and the 17 old-wording patterns are still there (so this test WILL turn red the day a regen widens a row and forgets them)."""
    pats = _patterns()
    assert len(pats) >= 1, "the 17 patterns are the population this blocker guards; an empty list would make the test vacuous (R20)"
    assert blocker_violations(_rows(), pats) == [], blocker_violations(_rows(), pats)[:3]
