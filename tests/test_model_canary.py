"""2026-11-22: the DAILY MODEL CANARY (founder-approved). One fixed question per day, at 05:00 UTC (08:00 EAT), through the MODEL path; its outcome pings its OWN healthchecks.io check.

R26: a canary that can pass while testing nothing is worse than none, so every limb of the verdict is PLANTED (a model-free reply, an unknown call count, an error, an empty reply, a wrong figure must each FAIL) and the positive control is the
real specimen (the live reply of 2026-11-22). The scheduling is pure and exactly-once by `put(skip_if_exists=True)` (R43). It must NOT take a scheduled-function slot (workspace limit 5, this app held to 4), must have no send path and no queue access
(asserted by AST, the same structural guarantee the poll and the sweeper carry), and its ping must go to its OWN env key, never the bridge heartbeat's."""
import ast
import datetime
import importlib.util
import os
import re

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("hc_canary_core", os.path.join(_ROOT, "chike-whatsapp", "handler_core.py"))
core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(core)
_SRC = open(os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"), encoding="utf-8").read()
_TREE = ast.parse(_SRC)

# the live reply, VERBATIM (production build 7643e18, 2026-11-22, run twice, byte-identical)
LIVE = {"reply": "Ada ya kuwasilisha annual return kwa kampuni ya ndani ni TZS 22,000. Thibitisha na BRELA Official (brela.go.tz).", "path": "fact", "model_calls": 1, "guards": []}


def _ts(h, m=0, day=22, month=11):
    return datetime.datetime(2026, month, day, h, m, tzinfo=datetime.timezone.utc).timestamp()


# ── the verdict ───────────────────────────────────────────────────────────────────────────────────
def test_the_live_reply_is_ok():
    assert core.canary_verdict(LIVE) == ("ok", "")


@pytest.mark.parametrize("out,needle", [
    (None, "no response"),
    ("a string", "no response"),
    ({"error": "TimeoutError"}, "errored"),
    ({**LIVE, "reply": ""}, "empty"),
    ({**LIVE, "reply": "   "}, "empty"),
    ({k: v for k, v in LIVE.items() if k != "reply"}, "empty"),
    ({**LIVE, "model_calls": 0}, "model-free"),
    ({**LIVE, "model_calls": None}, "not an integer"),
    ({k: v for k, v in LIVE.items() if k != "model_calls"}, "not an integer"),
    ({**LIVE, "model_calls": "1"}, "not an integer"),
    ({**LIVE, "model_calls": True}, "not an integer"),
    ({**LIVE, "reply": "Ada ya kuwasilisha annual return ni TZS 2,500. Thibitisha na BRELA."}, "expected figure"),
    ({**LIVE, "reply": "Samahani, swali hili liko nje ya mada yangu."}, "expected figure"),
])
def test_every_way_of_testing_nothing_is_a_fail(out, needle):
    kind, reason = core.canary_verdict(out)
    assert kind == "fail" and needle in reason, (kind, reason)


def test_plant_the_model_call_requirement_removed_is_caught(monkeypatch):
    """If the verdict stopped requiring a model call, a model-free reply carrying the figure would pass -- exactly the canary that tests nothing."""
    assert core.canary_verdict({**LIVE, "model_calls": 0})[0] == "fail"
    src = open(os.path.join(_ROOT, "chike-whatsapp", "handler_core.py"), encoding="utf-8").read()
    mutated = src.replace("if calls < 1:", "if False:")
    assert mutated != src
    ns = {}
    exec(compile(mutated, "mutated_core", "exec"), ns)
    assert ns["canary_verdict"]({**LIVE, "model_calls": 0})[0] == "ok"      # the plant: without the rule it passes, and the real rule above is what blocks it


def test_the_canary_question_and_figure_are_the_ones_verified_live():
    assert core.CANARY_QUESTION == "Ada ya annual return BRELA ni shilingi ngapi?" and core.CANARY_EXPECT == ("22,000",)


# ── the schedule: a window, exactly once ──────────────────────────────────────────────────────────
@pytest.mark.parametrize("h,m,want", [(5, 0, True), (5, 4, True), (5, 29, True), (5, 30, False), (4, 59, False), (0, 0, False), (12, 0, False), (23, 59, False)])
def test_canary_due_only_inside_the_window(h, m, want):
    assert core.canary_due(_ts(h, m), False) is want


def test_a_claimed_day_is_never_due_again():
    assert core.canary_due(_ts(5, 10), True) is False


def test_garbage_time_is_not_due():
    assert core.canary_due(None, False) is False and core.canary_due("x", False) is False


def test_every_five_minute_tick_lands_inside_the_window():
    """The scheduler ticks every 5 minutes; the 30-minute window must contain at least one tick whatever the phase."""
    for offset in range(0, 300, 7):
        ticks = [t for t in range(core.CANARY_WINDOW_START_S + offset, core.CANARY_WINDOW_END_S, 300)]
        assert ticks, offset


def test_the_date_key_is_the_utc_date():
    assert core.canary_date(_ts(5, 10)) == "2026-11-22" and core.canary_date(_ts(23, 59, 21)) == "2026-11-21"


# ── the structure ─────────────────────────────────────────────────────────────────────────────────
def _fn(name):
    return next(n for n in ast.walk(_TREE) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name)


def _calls(node):
    out = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            f = n.func
            out.add(f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else ""))
    return out


def _names(node):
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)} | {n.attr for n in ast.walk(node) if isinstance(n, ast.Attribute)}


FORBIDDEN_CALLS = {"_send_once", "_send_once_bridge", "answer_and_send", "greet_and_send", "send_text", "_notify_reviewers", "_send_digest", "apply_decision", "put_item"}
FORBIDDEN_STORES = {"TRANSCRIPTS", "REVIEW_QUEUE", "PENDING_ROWS", "INFLIGHT", "DISCLOSURES", "AUTOSEND", "BRIDGE_LEDGER"}


def test_the_canary_function_has_no_send_path_and_touches_no_participant_store():
    fn = _fn("run_model_canary")
    assert not (_calls(fn) & FORBIDDEN_CALLS), _calls(fn) & FORBIDDEN_CALLS
    assert not (_names(fn) & FORBIDDEN_STORES), _names(fn) & FORBIDDEN_STORES


def test_the_canary_makes_exactly_one_model_call_and_one_ping():
    fn = _fn("run_model_canary")
    remote = [n for n in ast.walk(fn) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "remote"]
    pings = [n for n in ast.walk(fn) if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "_ping_healthcheck"]
    assert len(remote) == 1 and len(pings) == 1
    kw = {k.arg: ast.unparse(k.value) for k in pings[0].keywords}
    assert kw.get("url_env") == "'HEALTHCHECK_CANARY_URL'", "the canary must ping its OWN check, never the bridge heartbeat's"


def test_the_spawner_only_spawns_and_claims_exactly_once_with_put_skip_if_exists():
    fn = _fn("_maybe_spawn_canary")
    assert not (_calls(fn) & FORBIDDEN_CALLS) and not (_names(fn) & FORBIDDEN_STORES)
    puts = [n for n in ast.walk(fn) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "put"]
    assert len(puts) == 1 and any(k.arg == "skip_if_exists" and ast.unparse(k.value) == "True" for k in puts[0].keywords), "R43: the once-a-day decision is put(skip_if_exists=True), not a read-then-write"
    assert "spawn" in _calls(fn)


def test_the_canary_takes_no_scheduled_function_slot():
    """The workspace limit is 5 and tests/test_review_timeout.py holds this app to 4: the canary rides the existing 5-minute tick."""
    fn = _fn("run_model_canary")
    deco = " ".join(ast.unparse(d) for d in fn.decorator_list)
    assert "schedule" not in deco and "timeout=1800" in deco
    assert len(re.findall(r"schedule=_sched\(", _SRC)) <= 4


def test_the_reconcile_tick_calls_the_spawner_inside_a_try_so_it_can_never_break_reconciliation():
    fn = _fn("reconcile_receipts")
    tries = [n for n in ast.walk(fn) if isinstance(n, ast.Try)]
    assert any("_maybe_spawn_canary" in ast.unparse(t.body) for t in tries)


def test_health_reports_the_canary_without_leaking_the_url(monkeypatch):
    spec = importlib.util.spec_from_file_location("chike_modal_whatsapp_canary_health", os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"))
    mw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mw)
    from conftest import isolate_modal_stores
    isolate_modal_stores(mw, monkeypatch)
    monkeypatch.setenv("HEALTHCHECK_CANARY_URL", "https://hc-ping.example/very-secret-uuid")
    h = mw._model_canary_health()
    assert h["configured"] is True and "very-secret-uuid" not in repr(h)
    monkeypatch.delenv("HEALTHCHECK_CANARY_URL")
    assert mw._model_canary_health()["configured"] is False


def test_the_ping_helper_still_defaults_to_the_bridge_heartbeat_key():
    fn = _fn("_ping_healthcheck")
    assert [ast.unparse(d) for d in fn.args.defaults][-1] == "'HEALTHCHECK_PING_URL'"
