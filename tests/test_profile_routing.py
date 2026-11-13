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


# ── domestic-work sector cues (2026-11-13): GN 605A item 4 is "Domestic Work or Services"; the commonest phrasings were unmatched ─────
from chike.rules_engine import wage_schedule as _ws          # noqa: E402


@pytest.mark.parametrize("q", [
    "Kima cha chini cha mshahara kwa mfanyakazi wa nyumbani ni kiasi gani?",
    "Nalipa mfanyakazi wa nyumbani 150,000 kwa mwezi, je ni sawa?",
    "Nalipa msaidizi wa nyumbani 90,000 kwa mwezi, ni halali?",
    "Nalipa dada wa kazi za nyumbani 150,000 kwa mwezi, ni halali?",
])
def test_domestic_work_phrasings_resolve_to_the_sector_and_never_to_a_single_row(q):
    outcome, value = _ws.resolve(q)
    assert (outcome, value) == (_ws.SECTOR, 4), (outcome, value)     # sector-only: lists the four rates, picks none


def test_a_house_rent_question_is_not_read_as_domestic_work():
    assert _ws.resolve("Nyumba yangu ya kupanga inalipwa 150,000, ni halali?") == (_ws.NONE, None)


def test_the_four_domestic_rates_in_the_engine_equal_the_gazette():
    """GN 605A Second Schedule item 4, read from the TanzLII gazette text on 2026-11-13 (monthly column)."""
    assert {r[1]: r[7] for r in _ws.BY_SECTOR[4]} == {"a": 328000, "b": 265000, "c": 160000, "d": 80000}
