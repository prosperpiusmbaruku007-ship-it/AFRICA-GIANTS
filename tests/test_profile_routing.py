"""2026-11-13 routing batch (coverage survey): minimum wage 'Nalipa <worker> N, ni halali?' / 'inatosha kisheria', and presumptive
'kodi ya makadirio kwa mauzo ya milioni N'. The probes live in eval/controls/sweep_profile_routing_2026_11_13.py (one list, two users).
Every probe that must DIVERT is paired with probes that contain the same vocabulary and must stay CLEAN (R17); and each new cue is
PLANTED (disabled) to show a test fires (R26)."""
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "eval", "controls"))
import sweep_profile_routing_2026_11_13 as sweep          # noqa: E402
from chike import routing                                  # noqa: E402

PROBES = sweep.PROBES


@pytest.mark.parametrize("q,want,why", PROBES)
def test_probe_routes_as_expected(q, want, why):
    assert routing.detect_intent(q) == want, why


def _fails_any(monkeypatch, name, value):
    monkeypatch.setattr(routing, name, value)
    return [q for q, want, _ in PROBES if routing.detect_intent(q) != want]


def test_plant_nalipa_worker_cue_disabled_is_caught(monkeypatch):
    assert any("nalipa" in q.lower() for q in _fails_any(monkeypatch, "_WAGE_NALIPA_WORKER", re.compile(r"(?!x)x")))


def test_plant_named_turnover_cue_disabled_is_caught(monkeypatch):
    assert any("makadirio" in q.lower() or "presumptive" in q.lower()
               for q in _fails_any(monkeypatch, "_PRESUMPTIVE_NAMED_TURNOVER", re.compile(r"(?!x)x")))


def test_plant_nalipa_cue_made_too_broad_is_caught(monkeypatch):
    """Over-broad: any 'nalipa' counts as a pay cue. The 'kodi ya mapato' / 'ada ya leseni' clean probes must catch it."""
    failed = _fails_any(monkeypatch, "_WAGE_NALIPA_WORKER", re.compile(r"(?<![a-z])nalipa\b"))
    assert any("kodi ya mapato" in q or "leseni" in q for q in failed)


def test_plant_veto_removed_is_caught(monkeypatch):
    failed = _fails_any(monkeypatch, "_PRESUMPTIVE_VETO", re.compile(r"(?!x)x"))
    assert any("daladala" in q or "Kampuni" in q or "mfumo wa kawaida" in q for q in failed)


def test_new_patterns_contain_no_control_characters():
    """R39: a non-raw escape compiles to a backspace and matches nothing, invisibly."""
    for name in ("_WAGE_NALIPA_WORKER_PATTERN", "_PRESUMPTIVE_NAMED_TURNOVER_PATTERN"):
        assert not re.search(r"[\x00-\x1f]", getattr(routing, name)), name
