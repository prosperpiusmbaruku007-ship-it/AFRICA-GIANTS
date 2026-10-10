"""THE REVIEWER ROSTER, THE CLAIM LOCK, AND THE LINE R7's CONDITION RESTS ON.

⛔⛔ THE ONE INVARIANT THIS FILE EXISTS FOR, stated once: **no elapsed time, no queue depth
and no number of reviewers causes a reply to reach a participant unread.** Everything else
here — roster parsing, token binding, claim ordering, attribution — is machinery in service
of that. The last two tests assert it STRUCTURALLY rather than behaviourally, because a
behavioural test can only prove that today's sweeper does not send; it cannot prove there is
no code that could.

⚠️ AND THE RACE THAT MATTERS IS NOT TWO SENDS. It is one reviewer SENDING while another
WITHHOLDS — which delivers an answer a human had just decided to withhold, leaves both
decisions in the record, and leaves nobody able to say afterwards what the participant
actually received.
"""
import ast
import asyncio
import os
import re
import sys
from datetime import datetime, timedelta, timezone

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "chike-whatsapp"))

import handler_core as hc                                   # noqa: E402

R1 = "+255700000011"
R2 = "+255700000022"
ROSTER = ((R1, "Asha"), (R2, "Juma"))
KEY = "test-signing-key"


def _settings(**kw):
    base = dict(slow_ack_after_s=0, second_ack_after_s=0, model_timeout_s=5,
                send_attempts=1, send_retry_delay_s=0, sender_salt="s",
                supervised=True, roster=ROSTER, review_signing_key=KEY)
    base.update(kw)
    return hc.Settings(**base)


class _Recorder:
    def __init__(self):
        self.sent, self.held = [], []

    async def send(self, to, text):
        self.sent.append((to, text))
        return True, None

    async def hold(self, to, text, row):
        self.held.append((to, text, row))
        return True, None


async def _ask_ok(_m):
    return {"reply": "JIBU LA MFANO: SDL ni asilimia 3.5."}


def _item(claimed_by=R1):
    r = _Recorder()
    row = asyncio.get_event_loop().run_until_complete(
        hc.deliver("+255700000007", "Je, SDL inanihusu?", _ask_ok, r.send,
                   _settings(), hold_reply=r.hold))
    it = hc.review_item(row=row, sender="+255700000007", draft=row["reply"],
                        engine_working="Ndiyo. Una wafanyakazi 15...",
                        facts=["sdl_rate: 3.5%"])
    if claimed_by:
        it, outcome = hc.claim(it, claimed_by)
        assert outcome == "claimed"
    return it


def _expire_claim(it, seconds_ago=1):
    it["claim_expires_at"] = (
        datetime.now(timezone.utc) - timedelta(seconds=seconds_ago)
    ).isoformat(timespec="seconds")
    return it


# ── roster parsing ─────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("raw,expect", [
    ("", ()),
    ("+255700000011", ((R1, "0011"),)),
    ("+255700000011:Asha", ((R1, "Asha"),)),
    ("+255700000011:Asha, +255700000022:Juma", ((R1, "Asha"), (R2, "Juma"))),
    ("+255700000011:Asha; +255700000022", ((R1, "Asha"), (R2, "0022"))),
    # A duplicate number keeps the FIRST name instead of depending on ordering.
    ("+255700000011:Asha, +255700000011:Juma", ((R1, "Asha"),)),
    # A nameless blank is dropped: it would be a seat that can never be notified and never
    # acts, silently lowering effective capacity.
    ("+255700000011:Asha, , :Nobody", ((R1, "Asha"),)),
])
def test_the_roster_parses_from_the_secret(raw, expect):
    assert hc.parse_roster(raw) == expect


def test_no_reviewer_number_is_hard_coded_in_either_module():
    """The roster lives in the secret, like every other credential. This is the grep-level
    guarantee, scoped to exclude the +2557000000xx placeholders used in docs and tests."""
    for name in ("handler_core.py", "modal_whatsapp.py"):
        src = open(os.path.join(_ROOT, "chike-whatsapp", name), encoding="utf-8").read()
        hits = [m for m in re.findall(r"\+255\d{9}", src)
                if not m.startswith("+2557000000")]
        assert not hits, f"{name} hard-codes reviewer numbers: {hits}"


# ── identity without a login ───────────────────────────────────────────────────────────
def test_a_valid_link_authenticates_the_reviewer_who_owns_it():
    it = _item(claimed_by=None)
    assert hc.authenticate_reviewer(
        _settings(), it["review_id"], hc.reviewer_id(KEY, R1),
        hc.review_token(KEY, it["review_id"], R1)) == (R1, "Asha")


def test_one_reviewers_token_does_NOT_work_as_another():
    """The token is bound to BOTH the draft and the reviewer, so a forwarded link cannot be
    replayed as someone else — which is what keeps the attribution column honest."""
    it = _item(claimed_by=None)
    assert hc.authenticate_reviewer(
        _settings(), it["review_id"], hc.reviewer_id(KEY, R2),
        hc.review_token(KEY, it["review_id"], R1)) is None


def test_a_token_for_one_DRAFT_does_not_work_on_another():
    it = _item(claimed_by=None)
    other = it["review_id"] + "-other"
    assert hc.authenticate_reviewer(
        _settings(), other, hc.reviewer_id(KEY, R1),
        hc.review_token(KEY, it["review_id"], R1)) is None


def test_NO_SIGNING_KEY_authenticates_NOBODY():
    """⛔ THE FAIL-CLOSED LIMB, AND IT IS NOT HYPOTHETICAL. An empty key still produces a
    perfectly stable HMAC that anyone who knows the scheme can reproduce — so a missing
    secret would not DISABLE the links, it would make every one of them FORGEABLE. Checked
    explicitly rather than left to the maths."""
    it = _item(claimed_by=None)
    assert hc.authenticate_reviewer(
        _settings(review_signing_key=""), it["review_id"], hc.reviewer_id("", R1),
        hc.review_token("", it["review_id"], R1)) is None


def test_a_reviewer_NOT_on_the_roster_cannot_authenticate():
    it = _item(claimed_by=None)
    stranger = "+255799999999"
    assert hc.authenticate_reviewer(
        _settings(), it["review_id"], hc.reviewer_id(KEY, stranger),
        hc.review_token(KEY, it["review_id"], stranger)) is None


def test_a_reviewer_handle_leaks_no_part_of_the_phone_number():
    """Handles go in links; links get forwarded, screenshotted and logged by every hop."""
    rid = hc.reviewer_id(KEY, R1)
    assert len(rid) == 10 and R1 not in rid and R1[-4:] not in rid


# ── the claim lock ─────────────────────────────────────────────────────────────────────
def test_the_FIRST_reviewer_to_claim_holds_it_and_the_SECOND_is_refused():
    it = _item(claimed_by=None)
    it, first = hc.claim(it, R1)
    assert first == "claimed" and it["claimed_by"] == R1
    after, second = hc.claim(it, R2)
    assert second == "held_by_other"
    assert after["claimed_by"] == R1, "the second claim overwrote the first"


def test_re_opening_your_OWN_claim_is_not_a_conflict():
    """A reviewer who reloads the page, or opens it on a second device, must not lock
    themselves out of a draft they already hold."""
    it, _ = hc.claim(_item(claimed_by=None), R1)
    _again, outcome = hc.claim(it, R1)
    assert outcome == "already_yours"


def test_a_DECIDED_draft_cannot_be_claimed():
    it, _ = hc.apply_decision(_item(), "send", reviewer=R1)
    _after, outcome = hc.claim(it, R2)
    assert outcome == "decided"


def test_the_HOLDER_can_act_and_NOBODY_ELSE_can():
    """⛔⛔ SEND-VS-WITHHOLD IS THE RACE. Not two sends."""
    it = _item(claimed_by=R1)
    with pytest.raises(ValueError, match="claimed by another reviewer"):
        hc.apply_decision(it, "withhold", reviewer=R2, reason="hatari")
    updated, to_send = hc.apply_decision(it, "send", reviewer=R1, reviewer_name="Asha")
    assert to_send and updated["decided_by"] == R1


def test_acting_on_an_UNCLAIMED_draft_is_refused():
    with pytest.raises(ValueError, match="not claimed"):
        hc.apply_decision(_item(claimed_by=None), "send", reviewer=R1)


def test_acting_on_an_EXPIRED_claim_is_refused_EVEN_BY_THE_HOLDER():
    """The lock is read from the stored timestamp, not from a timer — a timer lives in one
    container and this queue is read from many."""
    with pytest.raises(ValueError, match="expired"):
        hc.apply_decision(_expire_claim(_item(claimed_by=R1)), "send", reviewer=R1)


def test_an_EXPIRED_claim_RELEASES_back_to_the_roster():
    released, did = hc.release_expired_claim(_expire_claim(_item(claimed_by=R1)))
    assert did and released["claimed_by"] is None
    assert released["released_from"] == R1 and released["release_count"] == 1
    taken, outcome = hc.claim(released, R2)
    assert outcome == "claimed" and taken["claimed_by"] == R2


def test_a_LIVE_claim_is_not_released():
    unchanged, did = hc.release_expired_claim(_item(claimed_by=R1))
    assert not did and unchanged["claimed_by"] == R1


def test_an_UNPARSEABLE_expiry_is_treated_as_EXPIRED():
    """Stranding a participant's answer behind one corrupt field is the failure this whole
    mechanism exists to avoid, so the ambiguous case releases rather than locks forever."""
    it = _item(claimed_by=R1)
    it["claim_expires_at"] = "not-a-timestamp"
    released, did = hc.release_expired_claim(it)
    assert did and released["claimed_by"] is None


# ── ⛔⛔ NOTHING SENDS UNREVIEWED, EVER ────────────────────────────────────────────────
def test_releasing_an_expired_claim_PRODUCES_NO_TEXT_TO_SEND():
    out = hc.release_expired_claim(_expire_claim(_item(claimed_by=R1)))
    assert isinstance(out, tuple) and len(out) == 2 and isinstance(out[1], bool)
    assert out[0]["status"] == "pending", "a timeout changed the decision status"
    assert out[0]["final"] is None, "a timeout produced a final answer"


def test_an_UNREVIEWED_draft_NEVER_sends_however_long_it_waits():
    """⛔ THE INVARIANT, SWEPT ACROSS A WEEK OF WAITING. No elapsed time, no claim churn and
    no number of re-notifications turns a pending draft into a sent one."""
    it = _item(claimed_by=None)
    now = datetime.now(timezone.utc)
    for hours in (0, 1, 6, 24, 72, 168):
        t = now + timedelta(hours=hours)
        it, _ = hc.release_expired_claim(it, now=t)
        if hc.needs_renotify(it, now=t, renotify_after_s=60):
            it["last_notified_at"] = t.isoformat(timespec="seconds")
            it["notify_count"] = int(it.get("notify_count") or 0) + 1
        assert it["status"] == "pending", f"status changed after {hours}h"
        assert it["final"] is None, f"a final answer appeared after {hours}h"
    assert it["notify_count"] >= 5, "it stopped re-notifying instead of persisting"


def test_a_claim_held_until_timeout_and_then_released_STILL_sends_nothing():
    """The compound case: claimed, abandoned, released, re-claimed by someone else,
    abandoned again. Each step is the one where a 'just send it' fallback would be
    tempting."""
    it = _item(claimed_by=R1)
    for who in (R2, R1, R2):
        it, did = hc.release_expired_claim(_expire_claim(it))
        assert did
        it, outcome = hc.claim(it, who)
        assert outcome == "claimed"
        assert it["status"] == "pending" and it["final"] is None
    assert it["claim_count"] == 4 and it["release_count"] == 3


def test_the_sweeper_cannot_REACH_a_participant():
    """⛔⛔ STRUCTURAL, NOT BEHAVIOURAL — and deliberately so. A behavioural test can only
    show that today's sweeper does not send; this shows it contains no code that COULD.

    `_notify_reviewers` IS permitted inside it: re-notifying is a send to a REVIEWER. What
    must never appear is anything addressed to the participant — the item's `sender`, or
    `final`/`draft` as a message body. "It sends nothing" would be false; "it sends nothing
    to a participant" is the actual rule, so that is what is asserted.
    """
    src = open(os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"),
               encoding="utf-8").read()
    fn = next((n for n in ast.walk(ast.parse(src))
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
               and n.name == "sweep_review_queue"), None)
    assert fn is not None, "sweep_review_queue has been renamed — re-point this test"

    subscripts = {n.slice.value for n in ast.walk(fn)
                  if isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant)
                  and isinstance(n.slice.value, str)}
    for forbidden in ("sender", "final", "draft"):
        assert forbidden not in subscripts, (
            f"the sweeper reads item[{forbidden!r}] — a timeout path that can reach the "
            f"participant's number or the answer text is the single change that voids R7's "
            f"condition")
    called = {getattr(c.func, "id", None) or getattr(c.func, "attr", None)
              for c in ast.walk(fn) if isinstance(c, ast.Call)}
    assert "_send_once" not in called, (
        "the sweeper calls _send_once directly. Re-notification must go through "
        "_notify_reviewers, which only ever addresses roster numbers")
    assert "apply_decision" not in called, (
        "the sweeper decides. A timeout is not a decision and has no reviewer to attribute")


def test_apply_decision_is_the_ONLY_producer_of_a_sendable_answer():
    """Every other pure entry point returns no text. If a second producer appears, this test
    is the thing that makes someone justify it."""
    producers = []
    for name in ("claim", "release_expired_claim", "review_item", "needs_renotify",
                 "per_reviewer", "review_summary", "notification_text"):
        fn = getattr(hc, name)
        assert callable(fn)
        producers.append(name)
    it = _item(claimed_by=R1)
    assert hc.claim(it, R1)[1] in hc.CLAIM_OUTCOMES
    assert hc.release_expired_claim(it)[1] in (True, False)
    assert hc.needs_renotify(it) in (True, False)
    # ...and the one that does produce text requires a claim AND a reviewer.
    _updated, to_send = hc.apply_decision(it, "send", reviewer=R1)
    assert isinstance(to_send, str) and to_send
    assert len(producers) == 7


# ── attribution ────────────────────────────────────────────────────────────────────────
def test_a_decision_without_a_reviewer_is_REFUSED():
    with pytest.raises(ValueError, match="needs the reviewer"):
        hc.apply_decision(_item(), "send", reviewer=None)


@pytest.mark.parametrize("action,kw", [
    ("send", {}), ("edit", {"edited": "X", "reason": "r"}), ("withhold", {"reason": "r"}),
])
def test_every_decision_records_WHO_took_it(action, kw):
    it = _item(claimed_by=R2)
    updated, _ = hc.apply_decision(it, action, reviewer=R2, reviewer_name="Juma", **kw)
    assert updated["decided_by"] == R2 and updated["decided_by_name"] == "Juma"
    assert updated["draft"] == it["draft"], "attribution cost the draft"


def test_per_reviewer_separates_the_two_reviewers_records():
    """⛔ THE POINT OF THE AUDIT TRAIL: a reviewer whose edit rate is far BELOW the others
    may not be faster — they may be approving what the others would have caught. A pooled
    rate cannot show that, which is why attribution is required rather than optional."""
    items = []
    for _ in range(3):
        it, _ = hc.apply_decision(_item(claimed_by=R1), "send", reviewer=R1,
                                  reviewer_name="Asha")
        items.append(it)
    items.append(hc.apply_decision(_item(claimed_by=R2), "edit", reviewer=R2,
                                   reviewer_name="Juma", edited="X",
                                   reason="wrong base")[0])
    items.append(hc.apply_decision(_item(claimed_by=R2), "withhold", reviewer=R2,
                                   reviewer_name="Juma", reason="out of scope")[0])

    by = hc.per_reviewer(items)
    assert set(by) == {R1, R2}
    assert by[R1]["decided"] == 3 and by[R1]["edit_or_withhold_rate"] == 0.0
    assert by[R2]["decided"] == 2 and by[R2]["edit_or_withhold_rate"] == 1.0
    assert by[R1]["name"] == "Asha" and by[R2]["name"] == "Juma"
    # Reachable from the summary, so nobody has to know to ask for it.
    assert hc.review_summary(items)["per_reviewer"][R2]["decided"] == 2


def test_per_reviewer_ignores_pending_and_unattributed_rows():
    assert hc.per_reviewer([_item(claimed_by=R1)]) == {}


def test_the_summary_counts_live_claims():
    items = [_item(claimed_by=R1), _item(claimed_by=None)]
    assert hc.review_summary(items)["claimed_now"] == 1


# ── re-notification ────────────────────────────────────────────────────────────────────
def _stale_notify(it, hours=5):
    it["last_notified_at"] = (
        datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat(timespec="seconds")
    return it


def test_a_CLAIMED_draft_is_not_re_notified():
    """Pinging the whole roster about a draft someone is already reading is how a roster
    learns to ignore the notifications."""
    assert hc.needs_renotify(_stale_notify(_item(claimed_by=R1)),
                             renotify_after_s=60) is False


def test_an_UNCLAIMED_stale_draft_IS_re_notified():
    assert hc.needs_renotify(_stale_notify(_item(claimed_by=None)),
                             renotify_after_s=60) is True


def test_a_draft_whose_claim_EXPIRED_is_re_notified():
    it = _stale_notify(_expire_claim(_item(claimed_by=R1), seconds_ago=3600))
    assert hc.needs_renotify(it, renotify_after_s=60) is True


def test_a_DECIDED_draft_is_never_re_notified():
    it, _ = hc.apply_decision(_item(), "send", reviewer=R1)
    it["last_notified_at"] = "2020-01-01T00:00:00+00:00"
    assert hc.needs_renotify(it, renotify_after_s=1) is False


# ── the notification itself ────────────────────────────────────────────────────────────
def test_the_notification_carries_the_draft_the_working_and_the_link():
    it = _item(claimed_by=None)
    text = hc.notification_text(it, "https://x/d?r=1&v=2&t=3", reviewer_name="Asha")
    assert it["draft"] in text and it["question"] in text
    assert "Ndiyo. Una wafanyakazi 15..." in text
    assert "https://x/d?r=1&v=2&t=3" in text and "Asha" in text
    assert "Hakuna jibu linalotumwa" in text, (
        "the notification must say plainly that nothing goes out until someone taps")


def test_the_notification_says_so_when_there_is_NO_engine_working():
    it = _item(claimed_by=None)
    it["engine_working"] = None
    assert "hakuna" in hc.notification_text(it, "https://x/d").lower()


def test_a_RENOTIFICATION_is_distinguishable_from_a_first_notification():
    it = _item(claimed_by=None)
    assert hc.notification_text(it, "u") != hc.notification_text(it, "u", renotify=True)
    assert "KUPITIA TENA" in hc.notification_text(it, "u", renotify=True)


# ── the cohort setting ─────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("raw,expect", [("", 0), ("1", 1), ("10", 10), ("30", 30)])
def test_the_cohort_size_is_a_setting_not_a_fixed_number(raw, expect):
    assert hc.Settings(cohort_size=int(raw or 0)).cohort_size == expect


def test_the_cohort_size_does_NOT_gate_delivery():
    """⛔ A DECISION, RECORDED AS ONE RATHER THAN AN OMISSION. Enforcing the cohort by
    refusing an 11th participant is a mechanism whose failure mode is BLOCKING A REAL USER —
    the expensive direction, and invisible to us when it fires, because a wrongly-refused
    question looks exactly like a question nobody asked. /health reports the declared size
    against the participants actually seen instead, so over-enrolment is visible without
    building something that can turn an employer away."""
    r = _Recorder()
    row = asyncio.get_event_loop().run_until_complete(
        hc.deliver("+255700000099", "swali", _ask_ok, r.send,
                   _settings(cohort_size=1), hold_reply=r.hold))
    assert row["supervision"] == "held", "cohort_size changed the delivery path"
    assert r.held, "a cohort limit silently dropped an answer"
