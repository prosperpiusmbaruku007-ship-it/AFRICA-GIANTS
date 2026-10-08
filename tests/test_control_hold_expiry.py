# -*- coding: utf-8 -*-
"""A HOLD WITHOUT AN EXPIRY IS A DECISION NOBODY IS MAKING — enforced, not remembered.

THE INCIDENT. D-FIDELITY-7 was recorded `NOT_WIRED` on 2026-08-24 with the note "Held for one
R16 cycle by decision." One cycle. Nothing came due, so nobody re-opened it, and on 2026-10-06 —
six weeks later — `eval_347` served the fabricated TZS 11,000,000 EFD threshold live, with the
corrected index row at rank 1 for both phrasings. No retrieval or content change could have
reached it; the guard layer was the only one that could, and the guard had been built and unwired
the whole time.

THE HOLD WAS NOT OVERRULED. IT LAPSED. That needs a date, not better judgement — the same remedy
R30 states for a diagnosis ("not done when it is written down, done when it is impossible for the
next session to not know it") and R18 states for a harness. A note that is re-printed on every
audit run and acted on by nobody is an unenforced convention.

THIS TEST IS THE ENFORCEMENT. It fails when a HELD control's own expiry passes, so the hold
surfaces by itself. It is deliberately cheap and deliberately annoying: the only ways to make it
green are to resolve the hold or to take the decision again, on the record, with a new date.
"""
import datetime
import importlib.util
import json
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_spec = importlib.util.spec_from_file_location(
    "audit_control_fires", os.path.join(REPO, "eval", "controls", "audit_control_fires.py"))
_mod = importlib.util.module_from_spec(_spec)
# The harness chdirs and runs an audit at import if executed as __main__; loading the module is
# safe because every audit call sits under `if __name__ == '__main__'`. Guarded anyway by
# restoring cwd, since an import that silently changes the working directory would break every
# relative path in the rest of the suite.
_cwd = os.getcwd()
sys.modules["audit_control_fires"] = _mod
_spec.loader.exec_module(_mod)
os.chdir(_cwd)

HOLDS = _mod.HOLDS


def test_the_registry_is_not_empty_and_contains_the_specimen():
    """R20: a registry with no rows passes every check below vacuously. And the one hold that
    LAPSED stays in it — a registry that drops its only failure reads as though the rule were
    free."""
    assert HOLDS, "the hold registry is empty, so every assertion below is vacuous"
    assert "D-FIDELITY-7" in HOLDS, (
        "the lapsed hold was removed from the registry. It is the specimen that produced this "
        "rule; deleting it deletes the evidence that holds lapse.")
    assert HOLDS["D-FIDELITY-7"].get("resolved"), (
        "D-FIDELITY-7 is in the registry without a `resolved` date. It was wired 2026-10-06.")


@pytest.mark.parametrize("cid", sorted(HOLDS))
def test_every_held_control_declares_a_state_and_a_reason(cid):
    h = HOLDS[cid]
    # WIRED_PENDING_LIVE_VERIFY added 2026-10-08 for D-FIDELITY-8, and it is a PENDING state,
    # not a resolved one: the guard is in the orchestrator and its copy is approved, but
    # nothing is proven about PRODUCTION until the R16 deploy and live verify run. It
    # therefore keeps its expiry and is treated exactly like HELD by the tests below --
    # the whole point of retaining the date is that the undone half cannot go quiet, which
    # is how D-FIDELITY-7 lapsed for six weeks while sitting built.
    assert h.get("state") in ("DISABLED", "HELD", "LAPSED_THEN_WIRED",
                              "WIRED_PENDING_LIVE_VERIFY"), (
        f"{cid}: unknown state {h.get('state')!r}")
    assert h.get("decided"), f"{cid}: no decision date — an undated decision cannot expire"
    assert len(h.get("why", "")) > 40, (
        f"{cid}: no real reason recorded. 'Held' with no reason is indistinguishable from "
        f"forgotten, which is exactly what D-FIDELITY-7 turned out to be.")


@pytest.mark.parametrize("cid", sorted(HOLDS))
def test_a_pending_hold_carries_an_expiry(cid):
    """`HELD` means a decision is pending, so it must come due. `DISABLED` means the decision was
    taken on evidence with no review pending — demanding an expiry there would manufacture
    busywork and train people to bump dates, which is how an expiry stops meaning anything."""
    h = HOLDS[cid]
    if h["state"] in ("HELD", "WIRED_PENDING_LIVE_VERIFY"):
        assert h.get("expires"), (
            f"{cid} is HELD with no expiry. That is the D-FIDELITY-7 defect exactly: a hold "
            f"nothing brings due is not a hold, it is a thing that was forgotten on purpose.")
    if h["state"] == "DISABLED":
        assert h.get("expires") is None, (
            f"{cid} is DISABLED but carries an expiry. Pick one: decided (no expiry) or pending "
            f"(HELD, with one).")


@pytest.mark.parametrize("cid", sorted(HOLDS))
def test_no_hold_is_past_its_own_expiry(cid):
    """⛔ THE ONE THAT FAILS ON ITS OWN. Nothing has to be remembered for this to fire."""
    overdue, note = _mod.hold_overdue(cid)
    assert not overdue, (
        f"{cid}: {note}. Either resolve it or take the decision again with a new expiry and a "
        f"recorded reason. Letting it stand silently is what cost six weeks of a live "
        f"fabricated threshold.")


def test_the_expiry_check_actually_fires_when_a_date_passes():
    """R26 both directions: a check that cannot fail is worse than the gap it replaced. Planted
    against a FUTURE date so it does not depend on today, and given a clean case too."""
    HOLDS["_planted_overdue"] = {
        "state": "HELD", "decided": "2026-01-01", "expires": "2026-01-08",
        "why": "planted specimen for the expiry check -- removed in the same test",
    }
    HOLDS["_planted_current"] = {
        "state": "HELD", "decided": "2026-01-01", "expires": "2099-01-01",
        "why": "planted specimen for the expiry check -- removed in the same test",
    }
    try:
        overdue, note = _mod.hold_overdue("_planted_overdue", today="2026-02-01")
        assert overdue and "EXPIRED" in note, f"the expiry check did not fire: {note!r}"
        clean, _ = _mod.hold_overdue("_planted_current", today="2026-02-01")
        assert not clean, "the expiry check fired on a hold that is still current"
        # and a resolved hold whose expiry is long past must NOT fire -- otherwise the registry
        # can never record history and the first resolution makes the suite permanently red
        assert not _mod.hold_overdue("D-FIDELITY-7", today="2099-01-01")[0]
    finally:
        HOLDS.pop("_planted_overdue", None)
        HOLDS.pop("_planted_current", None)


def test_the_audit_artifact_records_no_unwired_control():
    """The census, joined to this rule. A control recorded NOT_WIRED with no registry row is a
    hold nobody took — worse than a lapsed one, because there is no date to expire."""
    path = os.path.join(REPO, "eval", "results", "control_fire_audit.json")
    blob = json.load(open(path, encoding="utf-8"))
    bad = [c for c in blob["controls"]
           if c["verdict"] in ("NOT_WIRED", "INERT", "INERT_IN_PRODUCTION", "HOLD_OVERDUE",
                              "ERROR")
           and c["id"] not in HOLDS]
    assert not bad, (
        f"{len(bad)} control(s) are not in force and not in the hold registry: "
        f"{[c['id'] for c in bad]}. Either fix them or record the hold WITH AN EXPIRY.")
    # and the artifact must be recent enough to be about today's code
    audited = blob.get("audited", "")
    assert audited >= "2026-10-06", (
        f"the control audit artifact is from {audited}. Re-run "
        f"eval/controls/audit_control_fires.py — a stale census is the one thing worse than none, "
        f"because it is read as current.")


def test_today_is_not_somehow_before_the_registry_was_written():
    """Guards against a clock/timezone surprise making every expiry check vacuous."""
    assert datetime.date.today().isoformat() >= "2026-08-24"
