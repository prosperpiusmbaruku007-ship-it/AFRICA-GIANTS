"""2026-11-28 (founder): in supervised mode a HELD question gets THE ack once, however fast the draft was; and the pending notice is Swahili only.

Found live: pre-warm made the draft beat the 12 s threshold, the ladder stayed quiet, and the participant heard nothing until review."""
import asyncio
import importlib.util
import os

_p = os.path.join(os.path.dirname(__file__), "..", "chike-whatsapp", "handler_core.py")
_s = importlib.util.spec_from_file_location("hc_held_ack", _p)
hc = importlib.util.module_from_spec(_s)
_s.loader.exec_module(hc)


def _settings(**kw):
    base = dict(slow_ack_after_s=5.0, model_timeout_s=5, supervised_model_timeout_s=5, supervised=True)
    base.update(kw)
    return hc.Settings(**base)


class _R:
    def __init__(self, hold_ok=True):
        self.sent, self.held, self.hold_ok = [], [], hold_ok

    async def send(self, to, text):
        self.sent.append(text)
        return True, None

    async def hold(self, to, text, row):
        self.held.append(text)
        return (True, None) if self.hold_ok else (False, "put failed")


async def _fast(_m):
    return {"reply": "JIBU"}


def _run(c):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(c)
    finally:
        loop.close()


def test_fast_draft_still_gets_exactly_one_ack_when_held():
    r = _R()
    row = _run(hc.deliver("255700000001", "swali", _fast, r.send, _settings(), hold_reply=r.hold))
    assert r.held == ["JIBU"] and r.sent == [hc.ACK_TEXT], "a held question must get the ack once, even though the draft beat the threshold"
    assert row["acks_sent"] == 1 and row["ack_sent"] is True


def test_slow_draft_is_not_acked_twice():
    r = _R()

    async def slow(_m):
        await asyncio.sleep(0.1)
        return {"reply": "JIBU"}

    row = _run(hc.deliver("255700000001", "swali", slow, r.send, _settings(slow_ack_after_s=0.01), hold_reply=r.hold))
    assert r.sent == [hc.ACK_TEXT] and row["acks_sent"] == 1, "the ladder's ack and the held ack must not both go"


def test_no_ack_when_nothing_was_held():
    r = _R(hold_ok=False)
    _run(hc.deliver("255700000001", "swali", _fast, r.send, _settings(), hold_reply=r.hold))
    assert r.sent == [], "the hold failed: no promise that a reviewed answer is coming"


def test_kill_switch_still_disables_the_ack():
    r = _R()
    _run(hc.deliver("255700000001", "swali", _fast, r.send, _settings(slow_ack_after_s=0), hold_reply=r.hold))
    assert r.sent == []


def test_unsupervised_fast_answer_gets_no_ack_it_is_delivered_within_the_threshold():
    r = _R()
    row = _run(hc.deliver("255700000001", "swali", _fast, r.send, _settings(supervised=False)))
    assert r.sent == ["JIBU"] and row["acks_sent"] == 0 and row["ack_sent"] is False


def test_pending_notice_is_swahili_only():
    assert "Swali lako limepokelewa" in hc.PENDING_NOTICE
    for w in ("Your question", "answer is still", "I will send"):
        assert w not in hc.PENDING_NOTICE
