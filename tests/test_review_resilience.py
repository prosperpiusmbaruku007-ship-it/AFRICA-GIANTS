"""Supervised mode waits for a slow model, a model FAILURE reads as one, reminders are capped,
decision latency counts from the push, and a late receipt reaches the record.

Born of 2026-11-11: the GPU took ~20 min to start, the handler gave up at 240s and sent an
apology to review, and the model then answered correctly at +21 min with nobody listening.
"""
import asyncio
import importlib.util
import os
from datetime import datetime, timedelta, timezone

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location(
    "chike_core_rr", os.path.join(_ROOT, "chike-whatsapp", "handler_core.py"))
core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(core)


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _settings(**kw):
    base = dict(supervised=True, slow_ack_after_s=0, second_ack_after_s=0,
                model_timeout_s=0.05, supervised_model_timeout_s=2.0,
                cold_start_suspected_s=30, sender_salt="")
    base.update(kw)
    return core.Settings(**base)


def _deliver(ask, settings):
    held = {}

    async def hold(to, reply, row):
        held["reply"], held["row"] = reply, row
        return True, None

    async def send_once(to, text):
        return True, None
    row = _run(core.deliver("255700000001@s.whatsapp.net", "swali", ask, send_once, settings,
                            "t", hold_reply=hold if settings.supervised else None))
    return row, held


# -- supervised mode waits ---------------------------------------------------------------
def test_supervised_mode_waits_past_the_short_timeout_for_a_slow_model():
    async def slow(q):
        await asyncio.sleep(0.3)           # 6x the unsupervised limit, well inside the supervised one
        return {"reply": "Jibu sahihi"}
    row, held = _deliver(slow, _settings())
    assert held["reply"] == "Jibu sahihi", "the slow answer must reach review, not an apology"
    assert row["fallback"] is False and row["error_class"] is None
    assert row["model_timeout_s"] == 2.0


def test_the_same_slow_model_still_times_out_when_unsupervised():
    async def slow(q):
        await asyncio.sleep(0.3)
        return {"reply": "Jibu"}
    row, _ = _deliver(slow, _settings(supervised=False))
    assert row["fallback"] is True and row["error_class"] == "timeout"


def test_a_genuine_failure_still_falls_back_in_supervised_mode():
    async def boom(q):
        raise RuntimeError("inference exploded")
    row, held = _deliver(boom, _settings())
    assert row["fallback"] is True and row["error_class"] == "model_error"
    assert held["reply"].startswith("Samahani")


def test_even_the_long_limit_ends_in_a_fallback_not_an_endless_wait():
    async def forever(q):
        await asyncio.sleep(5)
    row, held = _deliver(forever, _settings(supervised_model_timeout_s=0.1))
    assert row["error_class"] == "timeout" and row["fallback"] is True


# -- the re-notify cap and the daily digest ----------------------------------------------
def _pending(**kw):
    it = {"status": "pending", "ts_held": "2026-11-11T17:34:48+00:00", "renotify_count": 0,
          "last_notified_at": "2026-11-11T17:35:00+00:00", "sender_tail": "9070",
          "question": "swali"}
    it.update(kw)
    return it


NOW = datetime(2026, 11, 11, 20, 0, tzinfo=timezone.utc)


def test_renotify_stops_after_the_cap():
    assert core.needs_renotify(_pending(renotify_count=2), now=NOW) is True
    assert core.needs_renotify(_pending(renotify_count=3), now=NOW) is False
    assert core.needs_renotify(_pending(renotify_count=9), now=NOW) is False


def test_the_cap_is_a_setting_not_a_constant():
    assert core.needs_renotify(_pending(renotify_count=3), now=NOW, max_renotifies=5) is True


def test_capped_drafts_go_to_the_digest_and_nothing_else_does():
    items = [_pending(renotify_count=3), _pending(renotify_count=1),
             _pending(renotify_count=3, status="withheld")]
    assert core.digest_candidates(items) == [items[0]]


def test_digest_is_due_once_a_day():
    assert core.digest_due(None, 1000.0) is True
    assert core.digest_due(1000.0, 1000.0 + 3600) is False
    assert core.digest_due(1000.0, 1000.0 + 86400) is True


def test_digest_text_is_roster_only_and_carries_each_link_and_the_failure_tag():
    items = [_pending(renotify_count=3, fallback=True, review_id="r1")]
    t = core.digest_text(items, lambda it: "https://x/d?r=" + it["review_id"], now=NOW)
    assert "https://x/d?r=r1" in t and "MODELI IMESHINDWA" in t and "...9070" in t
    assert "Hakuna jibu linalotumwa" in t


# -- decision latency counts from the PUSH -----------------------------------------------
def _claimed(**kw):
    it = {"review_id": "r", "status": "pending", "draft": "d", "sender": "s",
          "ts_held": "2026-11-11T19:03:59+00:00", "first_notified_at": "2026-11-11T19:08:00+00:00",
          "claimed_by": "rev", "claim_expires_at": "2026-11-11T19:30:00+00:00"}
    it.update(kw)
    return it


def test_latency_counts_from_the_push_not_the_question():
    now = datetime(2026, 11, 11, 19, 9, 16, tzinfo=timezone.utc)
    out, _ = core.apply_decision(_claimed(), "send", reviewer="rev", now=now)
    assert out["decision_latency_s"] == 76, "the reviewer's time, not the model's wait"
    assert out["time_from_question_s"] == 317, "the old figure is kept, under its true name"


def test_latency_falls_back_to_the_question_when_no_push_time_was_recorded():
    now = datetime(2026, 11, 11, 19, 9, 16, tzinfo=timezone.utc)
    out, _ = core.apply_decision(_claimed(first_notified_at=None), "send", reviewer="rev", now=now)
    assert out["decision_latency_s"] == 317


# -- retry: sends nothing, needs the claim, needs no reason ------------------------------
def test_retry_sends_nothing_and_is_not_counted_as_an_edit():
    now = datetime(2026, 11, 11, 19, 9, 16, tzinfo=timezone.utc)
    out, to_send = core.apply_decision(_claimed(fallback=True), "retry", reviewer="rev", now=now)
    assert to_send is None and out["status"] == "retried" and out["final"] is None
    s = core.review_summary([out])
    assert s["decided"] == 0, "a retry is neither an approval nor a correction"


def test_retry_still_needs_the_claim():
    with pytest.raises(ValueError):
        core.apply_decision(_claimed(claimed_by=None), "retry", reviewer="rev")


# -- the model-failure push --------------------------------------------------------------
def _failed():
    return {"sender_tail": "9070", "question": "SDL ni ngapi?", "fallback": True,
            "error_class": "timeout", "draft": "Samahani, Chike hakuweza kukusaidia sasa hivi."}


def test_a_model_failure_push_says_so_and_offers_the_four_choices_with_no_draft():
    t = core.notification_text(_failed(), "https://x/d", reviewer_name="Prosper")
    assert t.startswith("⛔ MODELI IMESHINDWA")
    assert "RASIMU MPYA" not in t and "RASIMU:" not in t
    assert "HAKUNA RASIMU YA JIBU" in t
    for choice in ("JARIBU TENA", "ANDIKA MWENYEWE", "TUMA SAMAHANI", "ZUIA"):
        assert choice in t
    assert "https://x/d" in t


def test_an_ordinary_draft_push_is_unchanged():
    item = _failed()
    item.update(fallback=False, error_class=None, draft="Jibu la kawaida")
    t = core.notification_text(item, "https://x/d")
    assert "RASIMU MPYA" in t and "RASIMU: Jibu la kawaida" in t and "MODELI IMESHINDWA" not in t


# -- the late receipt reaches the record -------------------------------------------------
def test_pending_message_id_is_read_from_the_detail():
    row = {"send_error": "PENDING_RECEIPT: id=3EB0B4EAD1A1B78BE0F208 status=server_ack"}
    assert core.pending_message_id(row) == "3EB0B4EAD1A1B78BE0F208"
    assert core.pending_message_id({"send_error": "bridge not connected"}) is None


def _pending_row():
    return {"send_state": "pending_receipt", "send_ok": False,
            "send_error": "PENDING_RECEIPT: id=ABC status=server_ack"}


def test_a_late_receipt_corrects_the_row_and_keeps_the_original_state():
    out = core.reconcile_row(_pending_row(), {"rank": 3, "ts": 1000, "receipt_ts": 1178})
    assert out["send_state"] == "delivered" and out["send_ok"] is True
    assert out["send_state_at_send"] == "pending_receipt" and out["receipt_lag_s"] == 178


def test_no_receipt_or_a_server_ack_only_leaves_the_row_alone():
    assert core.reconcile_row(_pending_row(), {"rank": 2, "ts": 1000}) is None
    assert core.reconcile_row(_pending_row(), None) is None
    assert core.reconcile_row({"send_state": "delivered"}, {"rank": 3, "ts": 1, "receipt_ts": 2}) is None


# -- structural: wiring that unit tests on pure functions cannot see ----------------------
def _src(name):
    return open(os.path.join(_ROOT, "chike-whatsapp", name), encoding="utf-8").read()


def test_review_act_retry_spawns_the_question_again_with_retry_of_and_never_sends():
    src = _src("modal_whatsapp.py")
    assert "answer_and_send.spawn(existing[\"sender\"], existing.get(\"question\") or \"\", rid)" in src
    assert "retry_of: str = None" in src and "slow_ack_after_s=0" in src, "a retry must not re-ack"


def test_the_sweeper_still_has_no_send_path_after_the_digest_was_added():
    import ast
    tree = ast.parse(_src("modal_whatsapp.py"))
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef)
              and n.name == "sweep_review_queue")
    called = {getattr(c.func, "id", None) or getattr(c.func, "attr", None)
              for c in ast.walk(fn) if isinstance(c, ast.Call)}
    assert "_send_once" not in called and "spawn" not in called and "answer_and_send" not in called
    subs = {n.slice.value for n in ast.walk(fn) if isinstance(n, ast.Subscript)
            and isinstance(n.slice, ast.Constant) and isinstance(n.slice.value, str)}
    assert not subs & {"sender", "final", "draft"}


def test_the_handler_function_outlives_the_long_supervised_wait():
    src = _src("modal_whatsapp.py")
    assert "timeout=2400, retries=0)\nasync def answer_and_send" in src.replace("\r\n", "\n")
    assert core.Settings().supervised_model_timeout_s < 2400


# -- an unreceipted send: bridge broken, or that recipient's phone is off? ---------------
def _node(flagged, oldest, since):
    return {"since_receipt_s": since, "outbound": {"flagged_no_receipt": flagged,
                                                   "oldest_pending_s": oldest}}


def test_nothing_past_the_ceiling_is_no_alert_of_either_kind():
    assert core.pending_alert_kind(_node(0, 0, 5)) is None
    assert core.pending_alert_kind({}) is None and core.pending_alert_kind(None) is None


def test_other_sends_receipted_since_means_the_recipient_is_offline_not_the_bridge():
    # oldest unreceipted send is 7200s old, but a receipt arrived 300s ago for someone else
    assert core.pending_alert_kind(_node(1, 7200, 300)) == "recipient_offline"


def test_no_receipt_of_any_message_since_the_send_means_the_bridge_is_suspect():
    assert core.pending_alert_kind(_node(1, 7200, 9000)) == "bridge_suspect"
    assert core.pending_alert_kind(_node(2, 7200, None)) == "bridge_suspect"


def test_the_offline_class_is_daily_and_the_bridge_class_is_hourly():
    src = _src("modal_whatsapp.py")
    assert 'every_s=3600 if kind == "bridge_suspect" else 86400' in src
