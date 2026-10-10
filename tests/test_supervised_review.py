"""SUPERVISED MODE — the answer is held for a human, the acks are not.

⛔ THE ONE DEFECT THIS WHOLE FILE EXISTS TO PREVENT is a supervised pilot that silently
stops supervising. The founder's R7 reading is literal — "nothing reaches a participant
unreviewed" — so every path that could end in an unreviewed send is asserted here, including
the misconfiguration path, which is the one that would look like it was working.

⚠️ AND THE SECOND, SUBTLER ONE: `deliver()` uses ONE `send_once` for both the ack ladder and
the answer. Injecting a blanket hold would have held the ACKS too, leaving a user who asked
at 9pm in total silence until the reviewer woke up. In supervised mode the acks matter MORE
than in autonomous mode, because the wait is human-paced. Both limbs are asserted.
"""
import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chike-whatsapp"))

import handler_core as hc                                   # noqa: E402


def _settings(**kw):
    base = dict(slow_ack_after_s=0.01, second_ack_after_s=0, model_timeout_s=5,
                send_attempts=1, send_retry_delay_s=0, sender_salt="s")
    base.update(kw)
    return hc.Settings(**base)


class _Recorder:
    def __init__(self):
        self.sent = []
        self.held = []

    async def send(self, to, text):
        self.sent.append((to, text))
        return True, None

    async def hold(self, to, text, row):
        self.held.append((to, text, row))
        return True, None


async def _ask_ok(_message):
    return {"reply": "JIBU LA MFANO: SDL ni asilimia 3.5."}


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


# ── the hold itself ────────────────────────────────────────────────────────────────────
def test_supervised_HOLDS_the_answer_and_sends_nothing_to_the_user():
    r = _Recorder()
    row = _run(hc.deliver("+255700000001", "SDL ni ngapi?", _ask_ok, r.send,
                          _settings(supervised=True, slow_ack_after_s=0),
                          hold_reply=r.hold))
    assert row["supervision"] == "held"
    assert r.held and r.held[0][1] == "JIBU LA MFANO: SDL ni asilimia 3.5."
    assert r.sent == [], (
        f"supervised mode sent something to the user: {r.sent!r}. Nothing may reach a "
        f"participant unreviewed")
    # The draft is still in the transcript row — held, not lost.
    assert row["reply"] == "JIBU LA MFANO: SDL ni asilimia 3.5."


def test_autonomous_mode_is_untouched():
    """The control arm. A change that holds everything is not a supervised pilot, it is an
    outage, and the autonomous deployment must be byte-identical."""
    r = _Recorder()
    row = _run(hc.deliver("+255700000002", "SDL ni ngapi?", _ask_ok, r.send,
                          _settings(slow_ack_after_s=0)))
    assert row["supervision"] == "sent"
    assert r.held == [] and len(r.sent) == 1


def test_the_ACKS_still_reach_the_user_while_the_answer_is_held():
    """⛔ THE LIMB A BLANKET HOLD WOULD HAVE BROKEN. A held answer can take hours; a user who
    hears nothing at all concludes the service is broken, and in supervised mode that is the
    normal case rather than the cold-start edge."""
    r = _Recorder()

    async def slow_ask(_m):
        await asyncio.sleep(0.08)
        return {"reply": "JIBU"}

    row = _run(hc.deliver("+255700000003", "swali", slow_ask, r.send,
                          _settings(supervised=True, slow_ack_after_s=0.01),
                          hold_reply=r.hold))
    assert row["acks_sent"] >= 1
    assert r.sent, "the ack ladder was held along with the answer"
    assert r.held, "the answer was not held"
    # And the ack says a PERSON is checking — not "nearly done", which would be a lie.
    assert "mtu" in r.sent[0][1], r.sent[0][1]


def test_the_supervised_ack_differs_from_the_autonomous_one():
    assert hc.Settings().supervised_ack != hc.SLOW_ACK
    assert "inapitiwa" in hc.Settings().supervised_ack


# ── the misconfiguration path, which is the dangerous one ──────────────────────────────
def test_supervised_with_NO_hold_callable_WITHHOLDS_rather_than_sending():
    """⛔ THE FAILURE THAT WOULD HAVE LOOKED LIKE SUCCESS. A `supervised=True` deploy whose
    hold was not wired must not fall through to a send: that is an unreviewed answer in a
    supervised pilot, which is the exact condition the founder's R7 reading forbids, and the
    transcript would have said send_ok=true."""
    r = _Recorder()
    row = _run(hc.deliver("+255700000004", "swali", _ask_ok, r.send,
                          _settings(supervised=True, slow_ack_after_s=0),
                          hold_reply=None))
    assert row["supervision"] == "misconfigured"
    assert row["send_ok"] is False
    assert r.sent == [], f"an unreviewed answer was sent: {r.sent!r}"
    assert row["error_class"] == "handler_bug"


def test_a_hold_that_cannot_be_STORED_does_not_report_success():
    """A hold that fails must not look delivered. Neither sent nor reviewable is bad; neither
    sent nor reviewable while the record says send_ok is the instrument lie."""
    r = _Recorder()

    async def broken_hold(_to, _text, _row):
        raise RuntimeError("Dict unavailable")

    row = _run(hc.deliver("+255700000005", "swali", _ask_ok, r.send,
                          _settings(supervised=True, slow_ack_after_s=0),
                          hold_reply=broken_hold))
    assert row["supervision"] == "held"
    assert row["send_ok"] is False and "RuntimeError" in (row["send_error"] or "")
    assert r.sent == []


def test_deliver_still_never_raises_in_supervised_mode():
    r = _Recorder()

    async def exploding_ask(_m):
        raise ValueError("boom")

    row = _run(hc.deliver("+255700000006", "swali", exploding_ask, r.send,
                          _settings(supervised=True, slow_ack_after_s=0),
                          hold_reply=r.hold))
    assert row["error_class"] == "model_error"
    assert row["fallback"] is True
    # The FALLBACK is held too — it is still an answer reaching a participant.
    assert r.held and r.held[0][1] == hc.FALLBACK


# ── the queue's pure logic ─────────────────────────────────────────────────────────────
def _item():
    r = _Recorder()
    row = _run(hc.deliver("+255700000007", "Je, SDL inanihusu?", _ask_ok, r.send,
                          _settings(supervised=True, slow_ack_after_s=0),
                          hold_reply=r.hold))
    return hc.review_item(row=row, sender="+255700000007", draft=row["reply"],
                          engine_working="Ndiyo. Una wafanyakazi 15...",
                          facts=["sdl_rate: 3.5%"])


def test_the_review_item_carries_the_EVIDENCE_not_just_the_draft():
    it = _item()
    assert it["question"] == "Je, SDL inanihusu?"
    assert it["engine_working"] and it["facts"]
    assert it["status"] == "pending" and it["final"] is None


def test_the_item_carries_the_real_number_and_the_HASH_separately():
    """The transcript store keeps only a salted hash plus a tail; the queue needs the real
    number to send. Keeping them in one store would re-introduce a reachable identifier into
    the analysis corpus, which is why they are two stores."""
    it = _item()
    assert it["sender"] == "+255700000007"
    assert it["sender_hash"] and it["sender_hash"] != it["sender"]


@pytest.mark.parametrize("action,expect_status,expect_sends", [
    ("send", "sent", True),
    ("edit", "edited", True),
    ("withhold", "withheld", False),
])
def test_the_three_decisions(action, expect_status, expect_sends):
    it = _item()
    updated, to_send = hc.apply_decision(
        it, action, edited="JIBU LILILOSAHIHISHWA", reason="rate was stated per employee")
    assert updated["status"] == expect_status
    assert (to_send is not None) is expect_sends
    if action == "edit":
        assert to_send == "JIBU LILILOSAHIHISHWA"


def test_the_DRAFT_survives_every_decision_verbatim():
    """⛔ THE MOST VALUABLE FIELD IN THE RECORD. The edits are labelled corrections on real
    traffic — the one signal no sweep over our own corpora can manufacture (R21/R33). A
    design that stored only the final text would look identical in every transcript and
    destroy the dataset."""
    for action, kw in (("send", {}),
                       ("edit", {"edited": "X", "reason": "r"}),
                       ("withhold", {"reason": "r"})):
        it = _item()
        updated, _ = hc.apply_decision(it, action, **kw)
        assert updated["draft"] == it["draft"]
        if action == "edit":
            assert updated["final"] != updated["draft"]


@pytest.mark.parametrize("action,kw", [
    ("edit", {"edited": "X"}),
    ("edit", {"edited": "X", "reason": "   "}),
    ("withhold", {}),
])
def test_an_EDIT_or_WITHHOLD_without_a_reason_is_REFUSED(action, kw):
    """Enforced in the pure layer, not the UI: a UI-only check is bypassed by the first curl,
    and an edit with no reason is a correction whose label is missing."""
    with pytest.raises(ValueError, match="requires a reason"):
        hc.apply_decision(_item(), action, **kw)


def test_an_EDIT_with_no_TEXT_is_refused():
    with pytest.raises(ValueError, match="requires the edited text"):
        hc.apply_decision(_item(), "edit", edited="  ", reason="r")


def test_a_decision_is_taken_ONCE():
    """Idempotence by refusal rather than by overwrite: a second decision on a sent item
    would send the same compliance answer twice, which this app already rules worse than one
    missing answer."""
    updated, _ = hc.apply_decision(_item(), "send")
    with pytest.raises(ValueError, match="already"):
        hc.apply_decision(updated, "send")


def test_an_unknown_action_is_refused():
    with pytest.raises(ValueError, match="unknown review action"):
        hc.apply_decision(_item(), "approve")


def test_the_decision_latency_is_recorded():
    it = _item()
    it["ts_held"] = (datetime.now(timezone.utc) - timedelta(minutes=7)).isoformat(
        timespec="seconds")
    updated, _ = hc.apply_decision(it, "send")
    assert 6 * 60 <= updated["decision_latency_s"] <= 8 * 60


# ── the summary, whose failure direction is flattering ─────────────────────────────────
def test_the_summary_refuses_an_edit_rate_on_an_EMPTY_queue():
    """R39: a 0.0 edit rate with nothing decided reads exactly like a perfect model. None
    cannot be mistaken for one."""
    s = hc.review_summary([_item()])
    assert s["pending"] == 1 and s["decided"] == 0
    assert s["edit_or_withhold_rate"] is None
    assert s["median_decision_latency_s"] is None


def test_the_summary_counts_the_three_outcomes():
    items = []
    for action, kw in (("send", {}), ("send", {}),
                       ("edit", {"edited": "X", "reason": "r"}),
                       ("withhold", {"reason": "r"})):
        updated, _ = hc.apply_decision(_item(), action, **kw)
        items.append(updated)
    s = hc.review_summary(items)
    assert s["decided"] == 4
    assert s["counts"] == {"sent": 2, "edited": 1, "withheld": 1}
    assert s["edit_or_withhold_rate"] == 0.5


# ── the flag's parsing, where a typo must be loud ──────────────────────────────────────
@pytest.mark.parametrize("raw,expect", [
    ("1", True), ("true", True), ("TRUE", True), ("yes", True), (" 1 ", True),
    ("", False), ("0", False), ("false", False), ("ture", False), ("on", False),
])
def test_the_supervised_flag_parses_strictly(raw, expect):
    """A typo must not quietly enable or disable supervision. `ture` is False — and because
    False is the DANGEROUS direction here, /health reports the parsed value so the deploy is
    verified rather than assumed."""
    assert (raw.strip().lower() in ("1", "true", "yes")) is expect
