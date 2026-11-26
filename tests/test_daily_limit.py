# -*- coding: utf-8 -*-
"""PER-SENDER DAILY QUESTION LIMIT (item C, 2026-11-26 scale audit).

Default 20/day (tunable), EAT calendar day, exact under concurrency (slot claims, no read-modify-write), a polite Swahili notice ONCE per day, test
senders exempt, a reviewer-requested retry never counted, and FAIL-OPEN on a store error (a courtesy limit must not block a real user).
Plants (R26): the naive counter is shown to overshoot where the slot claim does not; with the gate removed the 4th question reaches the model.
"""
import datetime as dt
import os
import sys
import types

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "chike-whatsapp"))
import handler_core as core  # noqa: E402
from test_evidence_guard import _load_mw as _load_mw_real, _run, hc as _mw_core  # noqa: E402

UTC = dt.timezone.utc


class _Claims(dict):
    def put(self, k, v, skip_if_exists=False):
        if skip_if_exists and k in self:
            return False
        self[k] = v
        return True


def _claimer(store):
    return (lambda k, v: store.put(k, v, skip_if_exists=True)), (lambda k: store.get(k)), (lambda k, v: store.__setitem__(k, v))


# ── the pure slot logic ──────────────────────────────────────────────────────────────────────────────────────
def test_the_20th_question_is_admitted_and_the_21st_is_not():
    store = _Claims()
    c, p, w = _claimer(store)
    res = [core.claim_daily_slot(c, p, w, "S1", 20) for _ in range(21)]
    assert all(r["admitted"] for r in res[:20]) and res[20]["admitted"] is False and [r["n"] for r in res[:20]] == list(range(1, 21))


def test_each_sender_has_their_own_count():
    store = _Claims()
    c, p, w = _claimer(store)
    for _ in range(20):
        core.claim_daily_slot(c, p, w, "S1", 20)
    assert core.claim_daily_slot(c, p, w, "S2", 20)["admitted"] is True


def test_the_day_is_the_EAT_day_and_resets_at_midnight_EAT():
    store = _Claims()
    c, p, w = _claimer(store)
    before = dt.datetime(2026, 11, 26, 20, 59, tzinfo=UTC)          # 23:59 EAT
    after = dt.datetime(2026, 11, 26, 21, 1, tzinfo=UTC)            # 00:01 EAT, next day
    for _ in range(20):
        core.claim_daily_slot(c, p, w, "S1", 20, now=before)
    assert core.claim_daily_slot(c, p, w, "S1", 20, now=before)["admitted"] is False
    r = core.claim_daily_slot(c, p, w, "S1", 20, now=after)
    assert r["admitted"] is True and r["n"] == 1 and r["day"] == "2026-11-27", "a new EAT day starts from zero"
    assert core.eat_day(dt.datetime(2026, 11, 26, 21, 0, tzinfo=UTC)) == "2026-11-27" and core.eat_day(dt.datetime(2026, 11, 26, 20, 59, tzinfo=UTC)) == "2026-11-26"


def test_exact_under_concurrency_even_when_every_racer_holds_a_stale_hint():
    store = _Claims()
    c, _, w = _claimer(store)
    stale = lambda k: 0                                             # noqa: E731  every racer thinks it is the first question of the day
    res = [core.claim_daily_slot(c, stale, w, "S1", 20) for _ in range(25)]
    assert sum(1 for r in res if r["admitted"]) == 20, "never more than the limit, however stale the hints"


def test_ILLUSTRATION_a_read_then_write_counter_overshoots_under_the_same_race_which_is_why_slots_are_claimed():
    store = {"n": 0}
    snaps = [store["n"] for _ in range(5)]                          # five racers all read the count before any of them writes it back
    admitted = 0
    for seen in snaps:
        if seen < 3:
            admitted += 1
    store["n"] = max(snaps) + 1
    assert admitted == 5 > 3, "the naive counter lets all five through a limit of 3: the exact-claim test above can fail"


def test_the_limit_survives_a_hint_store_that_raises():
    store = _Claims()
    c = lambda k, v: store.put(k, v, skip_if_exists=True)           # noqa: E731

    def boom(*a):
        raise RuntimeError("hint store down")
    res = [core.claim_daily_slot(c, boom, boom, "S1", 3) for _ in range(4)]
    assert [r["admitted"] for r in res] == [True, True, True, False]


def test_a_mistyped_limit_cannot_switch_it_off_or_lock_everyone_out():
    assert core.parse_daily_limit("0") == 20 and core.parse_daily_limit("junk") == 20 and core.parse_daily_limit(None) == 20
    assert core.parse_daily_limit("3") == 3 and core.parse_daily_limit("-4") == 20


def test_the_notice_is_polite_swahili_and_carries_the_limit():
    t = core.daily_limit_text(20)
    assert "kikomo" in t and "20" in t and "kesho" in t and "Samahani" in t


# ── through the REAL handler ────────────────────────────────────────────────────────────────────────────────
@pytest.fixture
def mw(monkeypatch):
    m = _load_mw_real(monkeypatch)
    monkeypatch.setenv("DAILY_QUESTION_LIMIT", "3")
    monkeypatch.setenv("DIGEST_ONLY_ABOVE", "100000")
    m.sent, m.model_calls = [], []

    async def fake_send(to, text):
        m.sent.append((to, text))
        return True, None
    monkeypatch.setattr(m, "_send_once", fake_send)

    class _Remote:
        @staticmethod
        async def aio(message):
            m.model_calls.append(message)
            return {"reply": "Ndiyo.", "working": "W", "facts": ["F"], "path": "engine:vat_registration"}

    class _Model:
        run = types.SimpleNamespace(remote=_Remote)
    monkeypatch.setattr(m, "ChikeModel", _Model)
    return m


def _ask(m, sender="255700000099@s.whatsapp.net", text="Swali", **kw):
    return _run(m.answer_and_send.get_raw_f()(sender, text, **kw))


def _notices(m):
    return [t for _, t in m.sent if "kikomo" in t]


def test_three_questions_are_answered_the_fourth_is_not_and_gets_one_polite_notice(mw):
    for i in range(3):
        _ask(mw, text=f"Swali {i}")
    assert len(mw.model_calls) == 3 and not _notices(mw), "positive control: the first 3 reach the model, no notice"
    out = _ask(mw, text="Swali 4")
    assert len(mw.model_calls) == 3, "the 4th never reached the model"
    assert out.get("daily_limit") is True and len(_notices(mw)) == 1
    _ask(mw, text="Swali 5")
    _ask(mw, text="Swali 6")
    assert len(mw.model_calls) == 3 and len(_notices(mw)) == 1, "one notice a day, not one per message"


def test_the_notice_row_records_no_question_text_and_the_blocked_question_makes_no_review_card(mw):
    for i in range(3):
        _ask(mw, text=f"Swali {i}")
    cards_before = len(mw.REVIEW_QUEUE)
    _ask(mw, text="SIRI-YA-MSHAHARA-12345")
    rows = [r for r in mw.TRANSCRIPTS.values() if r.get("kind") == "daily_limit"]
    assert rows and rows[0]["notice_sent"] is True and "SIRI-YA-MSHAHARA-12345" not in str(list(mw.TRANSCRIPTS.values()))
    assert len(mw.REVIEW_QUEUE) == cards_before, "a refused question costs no reviewer attention"


def test_PLANT_without_the_gate_the_fourth_question_reaches_the_model(mw, monkeypatch):
    async def never(sender, settings):
        return False
    monkeypatch.setattr(mw, "_daily_limit_gate", never)
    for i in range(4):
        _ask(mw, text=f"Swali {i}")
    assert len(mw.model_calls) == 4, "the limit test above can fail"


def test_senders_have_independent_limits(mw):
    for i in range(3):
        _ask(mw, sender="255700000099@s.whatsapp.net", text=f"a{i}")
    _ask(mw, sender="255700000099@s.whatsapp.net", text="a-over")
    _ask(mw, sender="255799000111@s.whatsapp.net", text="b0")
    assert len(mw.model_calls) == 4, "the second participant is unaffected by the first one's limit"


def test_a_designated_test_sender_is_exempt(mw, monkeypatch):
    monkeypatch.setenv("TEST_SENDERS", "+255799000111")
    for i in range(6):
        _ask(mw, sender="255799000111@s.whatsapp.net", text=f"t{i}")
    assert len(mw.model_calls) == 6 and not _notices(mw)


def test_a_reviewer_requested_retry_does_not_count_and_is_never_blocked(mw):
    for i in range(3):
        _ask(mw, text=f"q{i}")
    _ask(mw, text="retry of an earlier question", retry_of="rid-1")
    assert len(mw.model_calls) == 4 and not _notices(mw), "a retry is the system re-asking, not the participant"


def test_FAIL_OPEN_a_counter_store_error_admits_the_question(mw, monkeypatch):
    class _Dead(dict):
        def put(self, *a, **k):
            raise RuntimeError("store down")
    monkeypatch.setattr(mw, "DAILY_LIMIT", _Dead())
    for i in range(5):
        _ask(mw, text=f"q{i}")
    assert len(mw.model_calls) == 5 and not _notices(mw), "a hiccup in the counter must never refuse a real participant"


def test_health_reports_the_limit_without_the_package_import(monkeypatch):
    monkeypatch.setenv("DAILY_QUESTION_LIMIT", "7")
    m = _load_mw_real(monkeypatch)
    assert m._health_daily_limit() == 7
    monkeypatch.setenv("DAILY_QUESTION_LIMIT", "junk")
    assert m._health_daily_limit() == 20
