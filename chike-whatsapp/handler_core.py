"""Chike WhatsApp conversation logic — platform-independent, and deliberately so.

WHY THIS IS A SEPARATE MODULE FROM THE MODAL WRAPPER
----------------------------------------------------
Everything here is testable without Modal, without a network, and without a GPU:
`deliver()` takes `ask` and `send` as injected coroutines, so the tests can force a
timeout, a dead model, a junk response or a failing send and assert on what the user
actually received. The Modal wrapper (modal_whatsapp.py) supplies the real `ask`
(a `.remote.aio()` call into chike-inference) and the real `send` (httpx to Wappfly).

This split is what let the handler move from Railway to Modal without re-deriving the
delivery guarantees: the platform changed, `deliver()` did not.

THE GUARANTEE
-------------
Every inbound message ends in EITHER an answer OR the FALLBACK string — never silence —
and produces exactly one transcript row. On Railway the defect was that `call_modal`
could raise inside a fire-and-forget `asyncio.create_task`, where the exception was
swallowed by the event loop and the user simply never heard back. `deliver()` cannot
raise: every path, including a bug in this file, returns a row and sends something.

ERROR CLASSES, and how they changed in the move to Modal:
  timeout         the model took longer than settings.model_timeout_s (the cold-start case)
  model_error     the remote call itself failed  (absorbs Railway's `transport` + `http_status`;
                  there is no longer a network hop or a token gate between handler and model,
                  so those two classes are no longer possible)
  bad_response    the model returned something that is not an object
  no_reply_field  the object carried no usable `reply`
  handler_bug     an exception in this code — belt and braces, must never fire
"""

import asyncio
import re
import hashlib
import hmac
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

GREETINGS = {
    "habari", "hujambo", "mambo", "hello", "hi", "hey",
    "salaam", "salam", "start", "help", "msaada",
    "chike", "karibu",
}

WELCOME = (
    "Habari! Karibu sana. 🙏\n\n"
    "Mimi ni *Chike* — msaidizi wako wa maswali ya biashara\n"
    "kutoka *Africa Giants*.\n"
    "_Fahamu Biashara Yako, Maarifa Yako._\n\n"
    "Ninakusaidia na:\n"
    "• Kodi — VAT, PAYE, SDL, EFD\n"
    "• Usajili — BRELA, TRA, NSSF, OSHA\n"
    "• Sheria — GN 487A, vibali, leseni\n"
    "• Mishahara — GN 605A, WCF\n\n"
    "Uliza swali lako sasa hivi. 👇\n\n"
    "---\n\n"
    "Hello! Welcome. 🙏\n\n"
    "I am *Chike* — your assistant for business questions\n"
    "from *Africa Giants*.\n"
    "_Understand Your Business, That Knowledge Is Yours._\n\n"
    "I can help with:\n"
    "• Tax — VAT, PAYE, SDL, EFD\n"
    "• Registration — BRELA, TRA, NSSF, OSHA\n"
    "• Law — GN 487A, permits, licences\n"
    "• Wages — GN 605A, WCF\n\n"
    "Ask your question now. 👇\n\n"
    "---\n"
    "_⚠ Beta: thibitisha majibu muhimu na TRA._\n"
    "_⚠ Beta: verify important answers with TRA._"
)

# SENT INSTEAD OF THE WELCOME WHILE A QUESTION IS PENDING (founder, 2026-11-12). A participant who says
# "habari" while waiting for a supervised answer used to get the full welcome menu, which reads as if their
# question had been forgotten. Brief on purpose: it says the answer is coming, nothing else.
PENDING_NOTICE = (
    "Swali lako limepokelewa — jibu bado linaandaliwa. Nitakutumia mara litakapokuwa tayari. 🙏\n\n"
    "Your question was received — the answer is still being prepared. I will send it as soon as it is ready."
)

FALLBACK = (
    "Samahani, Chike hakuweza kukusaidia sasa hivi. "
    "Tafadhali jaribu tena baadaye.\n\n"
    "Sorry, Chike could not help right now. "
    "Please try again shortly."
)

SLOW_ACK = (
    "Nimepokea swali lako — ninaandaa jibu. Subiri kidogo. ⏳\n"
    "Got your question — preparing an answer. One moment."
)

# THE SECOND RUNG, AND WHY IT EXISTS: the first ack became a broken promise.
#
# The one real delivery (2026-08-14, build f98fc67) acked at 12s and answered at 94.2s.
# The user sat through 82 SECONDS OF SILENCE after being told "subiri kidogo" — and at 82
# seconds "one moment" does not reassure, it reads as a system that has stopped.
#
# Three things this copy does that the first ack does not:
#   NAMES THE REASON      — "mfumo unaanza upya". A wait with a cause is a wait; a wait
#                           with no cause is a fault. The cold start is the truth and the
#                           user can hear it.
#   HEDGES THE BOUND      — "dakika moja hadi mbili", a RANGE. Deliberately not "sekunde
#                           thelathini": naming a number we cannot keep is precisely how
#                           the 12s ack broke at 82s. Observed cold completions are
#                           60.6/60.8/97.9s, so a range is the honest form.
#   ENDS ON THE ONE PROMISE THE ARCHITECTURE KEEPS — the answer will arrive here. That is
#                           not optimism: `.spawn()` makes Modal responsible for running
#                           the job to completion, and the fallback path sends something
#                           even when the model fails. It is the only guarantee we have,
#                           and it is the one the user actually needs.
SECOND_ACK = (
    "Bado ninafanya kazi kwenye swali lako. Mara ya kwanza huchukua dakika moja hadi "
    "mbili kwa sababu mfumo unaanza upya. Sitakuacha bila jibu — nitakutumia hapa hapa "
    "likiwa tayari. ⏳\n"
    "Still working on your question. The first one takes a minute or two while the "
    "system starts up. I won't leave you without an answer — it will arrive right here."
)


@dataclass
class Settings:
    """Injected rather than read from module globals, so a test states the timing it
    is exercising instead of monkeypatching a constant and hoping nothing leaks."""

    # 240s, up from Railway's 180s. Cold starts measured at 64s (2026-08-11), 92.5s
    # (2026-08-06) and up to 216s (runbook); chike-inference's own function timeout is
    # 600s, so nothing upstream cuts us off. Costs nothing: on a cold path the user
    # waits longer instead of receiving nothing, and WhatsApp is asynchronous.
    model_timeout_s: float = 240.0
    # ⛔ IN SUPERVISED MODE THE TIMEOUT IS A DIFFERENT QUESTION. A human must act on every
    # reply anyway and the participant has been told it takes time, so 240s only THROWS ANSWERS
    # AWAY: on 2026-11-11 the GPU container took ~20 minutes to start, the handler gave up at
    # 240s and sent an apology to review, and the model then answered the question correctly
    # at +21 min with nobody listening. The fallback is for a GENUINE failure (an exception),
    # not a slow start, so supervised mode waits up to this much longer limit.
    supervised_model_timeout_s: float = 1800.0
    # Re-notify at most this many times per draft, then it moves to the daily digest. Without
    # a cap an unacted draft pings the roster every renotify_after_s forever.
    max_renotifies: int = 3

    # One short "I'm working on it" if the answer is slow. A user who hears nothing for
    # three minutes concludes the service is broken; one Wappfly message is far cheaper
    # than keeping a GPU warm. 0 DISABLES THE WHOLE LADDER, second rung included — it is
    # the kill switch, so it must not leave half the acks running.
    slow_ack_after_s: float = 12.0

    # The second rung, at 45s. The band is measured, not chosen for roundness:
    #   warm p90                 9.8s  (48 questions, 2026-08-11)
    #   earliest observed cold  60.6s  (3/3 determinism run, 2026-08-14)
    # 45 is the middle of the empty band — far enough above warm p90 that a warm request
    # NEVER sees it, and below the earliest cold completion ever measured so a cold
    # request ALWAYS does. Under ~30s risks firing at a slow-warm request about to
    # answer; over 60s can land after the answer it was meant to cover. 0 disables this
    # rung only.
    second_ack_after_s: float = 45.0

    # A PROXY, not a measurement — neither Modal's response nor its Python API tells the
    # handler whether the container was cold. Warm p90 was 9.8s over 48 questions
    # (2026-08-11); cold starts 64s+. The transcript field keeps the word `suspected`.
    cold_start_suspected_s: float = 30.0

    send_attempts: int = 2
    send_retry_delay_s: float = 2.0

    sender_salt: str = ""
    # Values scrubbed out of every log line and transcript field.
    secrets: tuple = field(default_factory=tuple)

    # ── SUPERVISED MODE (2026-10-10) ────────────────────────────────────────────────────
    # When True, the ANSWER is held as a draft for human review instead of being sent.
    # The founder's R7 reading depends on this literally: "nothing reaches a participant
    # unreviewed". So the default is False and the flag is read from the environment at
    # deploy time, never inferred.
    #
    # ⛔⛔ THE ACK LADDER IS DELIBERATELY *NOT* HELD, AND THIS IS THE ONE PLACE THE DESIGN
    # COULD HAVE GONE WRONG SILENTLY. `deliver` uses ONE `send_once` for both the acks and
    # the answer, so injecting a blanket hold would have held the acks too — leaving a user
    # who asked a question at 9pm with total silence until the reviewer woke up. In
    # supervised mode the acks matter MORE than in autonomous mode, not less, because the
    # wait is now human-paced. The answer and the acks therefore travel through two
    # different callables from here on.
    supervised: bool = False
    # ⛔ THE PARTICIPANT DISCLOSURE (runbook §8a) IS PART OF THE R7 CONDITION. Default ON, and the only
    # way to turn it off is an explicit 0/false/no/off -- a TYPO STAYS ON (fail toward disclosing, the
    # opposite of how the SUPERVISED flag has to be read). /health reports it and pre-flight gate 3b
    # refuses a deploy where it is not true.
    disclosure_enabled: bool = True

    # ── THE COHORT (2026-10-10) ─────────────────────────────────────────────────────────
    # How many participants the pilot is enrolled for. A SETTING, because the right number
    # is an operational judgement that changes as review capacity changes — 1, 10 or 30 are
    # all legitimate — and hard-coding a recommendation into the handler would freeze
    # yesterday's throughput estimate into today's deployment.
    #
    # ⚠️ IT IS A MONITORED DECLARATION, NOT A GATE, AND THAT IS A DELIBERATE CHOICE WITH A
    # REASON. Enforcing it by refusing an 11th participant would be a mechanism whose
    # failure mode is BLOCKING A REAL USER — the expensive direction this project has a
    # standing rule about, priced at one frozen held-out set per iteration, and invisible to
    # us when it fires because a wrongly-refused question looks exactly like a question
    # nobody asked. So /health reports the setting ALONGSIDE the distinct participants
    # actually seen, which makes over-enrolment visible without building something that can
    # turn a real employer away. R32's line is still honoured: the number does something.
    cohort_size: int = 0

    # ── THE REVIEWER ROSTER AND THE CLAIM LOCK (2026-10-10) ─────────────────────────────
    # Review capacity scales with reviewers, not with how fast one person can read. The
    # roster lives in the Modal Secret, like every other credential — never in code.
    roster: tuple = field(default_factory=tuple)        # ((number, name), ...)

    # ── DESIGNATED TEST SENDERS (founder, 2026-11-13) ───────────────────────────────────
    # The founder's own test phones are not on the roster, so they were counted as participants and a review
    # capacity of 3 fitted only 2 outside people. Their messages go through the FULL loop (disclosure, ack, held
    # draft, review) -- only the COUNTS differ. Hashes of the senders listed in the TEST_SENDERS secret.
    test_sender_hashes: frozenset = frozenset()

    # ── THE REVIEW TIMEOUT (2026-11-13) -- see the block above `engine_only_verdict`. FAIL-CLOSED: off unless explicit.
    autosend_enabled: bool = False
    autosend_after_s: float = 900.0

    # Signs the per-(draft, reviewer) action links. SEPARATE from ADMIN_TOKEN on purpose: a
    # leaked read token must not become a forgeable action link.
    #
    # ⛔ ITS ABSENCE FAILS CLOSED, AND THAT IS THE WHOLE POINT. With no signing key no links
    # can be issued, so drafts HOLD and re-notify. They never fall through to a send.
    review_signing_key: str = ""

    # A claimed draft that is not acted on is released back to the roster after this. Long
    # enough to read and compose a correction, short enough that a reviewer who puts their
    # phone down does not strand a participant's answer.
    claim_ttl_s: float = 900.0

    # An unacted draft is re-notified this often. RE-NOTIFIED — never auto-sent.
    renotify_after_s: float = 1800.0
    # What the user is told while a human reads their answer. Held replies can take hours,
    # so the honest ack says a person is checking — not "nearly done".
    supervised_ack: str = ("Nimepata swali lako. Jibu linapitiwa na mtu kwanza ili "
                           "kuhakikisha ni sahihi — nitakujibu hivi punde. Asante kwa "
                           "kuvumilia.")


def scrub(text, secrets=()) -> str:
    """Strip credentials from anything bound for a log or a transcript.

    Kept even though the Modal move removed the token between handler and model:
    WAPPFLY_TOKEN still travels on every outbound send and lands in httpx error
    strings, and this project has leaked a token twice.
    """
    s = "" if text is None else str(text)
    for secret in secrets:
        if secret and len(secret) >= 6:
            s = s.replace(secret, "<REDACTED>")
    return s


# ---------------------------------------------------------------------------
# WAPPFLY SESSION HEALTH — pure; the poll in modal_whatsapp.py does the I/O
# ---------------------------------------------------------------------------
# Wappfly accepted every send while delivering nothing ("Proxy pool exhausted"), and has now
# stopped forwarding inbound while its dashboard said connected. `/api/status` is therefore a
# NECESSARY signal and never a SUFFICIENT one: it catches a dropped session within minutes
# and says nothing about forwarding. The round-trip canary is the only check on that, and it
# needs a second number.

def wappfly_status_verdict(http_status, body):
    """('connected' | 'disconnected' | 'error', detail). Only an explicit 200 carrying
    status == 'connected' is connected: an unreadable body, a non-200, or a missing field is
    NOT a pass -- cannot evaluate is not passed."""
    if http_status != 200:
        return "error", f"HTTP {http_status}"
    if not isinstance(body, dict) or not isinstance(body.get("status"), str):
        return "error", "no status field in response"
    st = body["status"].strip().lower()
    return ("connected", "connected") if st == "connected" else ("disconnected", st[:40])


def advance_session_health(prev, verdict, detail, now, *, fail_threshold=2,
                           realert_after_s=6 * 3600):
    """(new_state, events). `events` is a list of 'down' | 'still_down' | 'recovered'.

    Two consecutive non-connected readings (10 minutes at the 5-minute cadence) raise 'down':
    one blip is a network hiccup, and an alert that cries wolf gets filtered, which is how a
    real one is missed. 'still_down' repeats at most every `realert_after_s`. A recovery is
    reported only if a 'down' was, so there is never a 'recovered' for an outage nobody heard
    about. `last_ok_ts` is when it was last seen connected -- the number a human asks for."""
    st = dict(prev or {})
    events = []
    st["last_check_ts"] = now
    st["last_verdict"] = verdict
    st["last_detail"] = detail
    if verdict == "connected":
        if st.get("alerted_down"):
            events.append("recovered")
        st.update(consecutive_failures=0, alerted_down=False, last_ok_ts=now,
                  last_alert_ts=st.get("last_alert_ts"))
        return st, events
    st["consecutive_failures"] = int(st.get("consecutive_failures", 0)) + 1
    if st["consecutive_failures"] >= fail_threshold:
        if not st.get("alerted_down"):
            events.append("down")
            st["alerted_down"] = True
            st["last_alert_ts"] = now
        elif now - float(st.get("last_alert_ts") or 0) >= realert_after_s:
            events.append("still_down")
            st["last_alert_ts"] = now
    return st, events


def model_watch_problem(w, now, window_s=6 * 3600.0):
    """A string when REAL model calls are failing, else None. `w` is {consecutive_failures, last_ok_ts, last_err_ts,
    last_error} kept by the handler on every answered question. Failing = two or more in a row, no success since the
    last failure, the last failure within `window_s`. Honest limit: with no traffic a dead GPU path is invisible here
    (a shallow web-tier check cannot see it); a failure ages out after `window_s` and a real or tester question that
    succeeds clears it at once."""
    w = w or {}
    try:
        fails = int(w.get("consecutive_failures") or 0)
        err_ts = float(w.get("last_err_ts") or 0)
        ok_ts = float(w.get("last_ok_ts") or 0)
    except (TypeError, ValueError):
        return None
    if fails >= 2 and err_ts and ok_ts < err_ts and (now - err_ts) <= window_s:
        return f"the last {fails} real questions failed at the model ({w.get('last_error')}) with no success since"
    return None


def heartbeat_decision(verdict, detail, state, threshold, pending_kind=None, extra_problems=()):
    """('ok' | 'fail' | 'skip', reason) -- what the watcher tells the dead-man's-switch this poll.

    ok   = the bridge is connected, one lease holder, and no send is stuck past the ceiling with NOTHING receipted.
    fail = a problem the founder must hear about NOW: two sockets, sends stuck while no receipt has arrived for ANY
           message (`bridge_suspect`), or a non-connected reading that has repeated `threshold` times.
    skip = ONE non-connected reading -- neither ok nor fail. A blip must not page, and must not be reported healthy.
           (Silence is safe: the check's period is longer than several polls.)
    A recipient whose phone is merely off (`bridge_recipient_offline`) is NOT a problem here: other messages are being
    receipted, so the bridge works, and a page for it would teach the founder to ignore pages."""
    extra = [str(p) for p in (extra_problems or ()) if p]

    def _verdict():
        if str(detail or "").startswith("TWO_SOCKETS"):
            return "fail", f"TWO SOCKETS: {detail}"
        if pending_kind == "bridge_suspect":
            return "fail", "sends past the receipt ceiling and NO receipt for any message since"
        if verdict != "connected":
            if int((state or {}).get("consecutive_failures", 0)) >= int(threshold):
                return "fail", f"bridge {verdict} ({detail})"
            return "skip", f"one non-connected reading ({verdict}); debounce"
        return "ok", ""
    d, why = _verdict()
    if extra:           # a problem in ANOTHER watched system (chike-inference) fails the same check, whatever the bridge says
        return "fail", "; ".join(([why] if d == "fail" else []) + extra)
    return d, why


def poll_age_verdict(state, now, *, max_age_s=15 * 60):
    """The poll's OWN heartbeat. A poll that stopped running reports nothing and alerts
    nobody, so absence is a finding: never polled, or older than `max_age_s`, is stale."""
    ts = (state or {}).get("last_check_ts")
    if ts is None:
        return {"age_s": None, "stale": True, "reason": "never polled"}
    age = max(0.0, float(now) - float(ts))
    return {"age_s": int(age), "stale": age > max_age_s,
            "reason": None if age <= max_age_s else f"last poll {int(age)}s ago"}


PENDING_RECEIPT = "PENDING_RECEIPT"


def is_pending_receipt(detail):
    """WhatsApp ACCEPTED the message but no delivery receipt has arrived. Not a failure and not a
    delivery, and above all NOT retryable: resending would duplicate a message that may be on
    its way. The bridge's pending ceiling is what stops this becoming a silent loss."""
    return str(detail or "").startswith(PENDING_RECEIPT)


def send_state(ok, detail=None):
    """delivered | pending_receipt | failed. None when no send was attempted."""
    if ok is None:
        return None
    if ok:
        return "delivered"
    return "pending_receipt" if is_pending_receipt(detail) else "failed"


def reply_address_kind(jid):
    """Which kind of address a reply was sent to: phone | lid | other. Recorded on every row so
    that if the phone-number path ever fails it is visible at once, not inferred later."""
    d = sender_domain(jid)
    return "phone" if d == "s.whatsapp.net" else ("lid" if d == "lid" else "other")


def bridge_verdict(rec, alive, now, *, max_age_s=90, fresh_s=30):
    """(verdict, detail) from the bridge's OWN published state -- its library events, never an
    inference from a vendor dashboard. `connected` requires every one of: a fresh heartbeat,
    the socket open, and this container holding the lease. Two lease-holders is reported with
    the TWO_SOCKETS prefix so the caller can alert on the first sighting."""
    if not isinstance(rec, dict) or not isinstance(rec.get("node"), dict):
        return "error", "no heartbeat from the bridge"
    age = now - float(rec.get("ts") or 0)
    if age > max_age_s:
        return "error", f"bridge heartbeat stale ({int(age)}s)"
    holders = [k for k, v in (alive or {}).items()
               if isinstance(v, dict) and now - float(v.get("ts") or 0) < fresh_s and v.get("holding")]
    if len(holders) > 1:
        return "error", f"TWO_SOCKETS: {len(holders)} containers hold the lease"
    node = rec["node"]
    conn = node.get("connection")
    if conn == "open" and rec.get("holding_lease"):
        return "connected", "open"
    if conn == "logged_out":
        return "disconnected", "logged out: the session must be re-paired (QR)"
    last = node.get("last_disconnect") or {}
    return "disconnected", (f"{conn}; last_event={node.get('last_event')}; "
                            f"last_close={last.get('name')}; holding_lease={rec.get('holding_lease')}")


def pending_alert_kind(node):
    """Why sends are sitting past the receipt ceiling -- the distinction that stops the alert
    crying wolf every night. Receipts track whether the RECIPIENT'S PHONE is reachable, so a
    send with no receipt is only worth waking someone for if nothing else has been receipted
    since it was sent.

      bridge_suspect    no receipt of ANY message has arrived since the oldest unreceipted send:
                        the bridge or WhatsApp may be broken
      recipient_offline other sends HAVE been receipted since: those phones are reachable and
                        this recipient's is probably off. Low priority, once a day.
      None              nothing is past the ceiling

    LIMIT, stated: with a single recipient the two are indistinguishable (nothing else can be
    receipted), so a lone unreceipted send reads as bridge_suspect. The split only starts to
    work with several recipients, which is what a pilot is."""
    out = (node or {}).get("outbound") or {}
    if not int(out.get("flagged_no_receipt") or 0):
        return None
    oldest = float(out.get("oldest_pending_s") or 0)
    since = (node or {}).get("since_receipt_s")
    if since is None or float(since) > oldest:
        return "bridge_suspect"
    return "recipient_offline"


def pending_alert_due(prev_ts, flagged, now, *, every_s=3600):
    """True when sends have waited past the receipt ceiling and the last such email is old."""
    return bool(flagged) and (not prev_ts or now - float(prev_ts) >= every_s)


_MSG_ID = re.compile(r"id=([A-Za-z0-9]+)")


def pending_message_id(row):
    """The WhatsApp message id inside a PENDING_RECEIPT detail, or None."""
    m = _MSG_ID.search(str(row.get("send_error") or ""))
    return m.group(1) if m else None


def reconcile_row(row, ledger_row, source="reconcile_receipts"):
    """The row as it should read once the late delivery receipt has arrived, or None.

    `source` is RECORDED (`reconciled_by`, `reconciled_ts`): a row corrected after the fact must say
    that it was, and by what, or the corrected state is indistinguishable from the original.

    A pending row is true at the moment of sending and stale afterwards: on 2026-11-11 the
    reply read `pending_receipt` for ever although WhatsApp returned the receipt 178s later.
    The original state is KEPT beside the corrected one, never overwritten, so the record
    shows both that the receipt was slow and by how much."""
    if row.get("send_state") != "pending_receipt":
        return None
    if not ledger_row or int(ledger_row.get("rank") or 0) < 3 or not ledger_row.get("receipt_ts"):
        return None
    out = dict(row)
    out["send_state_at_send"] = "pending_receipt"
    out["send_ok_at_send"] = row.get("send_ok")
    out["send_state"] = "delivered"
    out["send_ok"] = True
    out["receipt_lag_s"] = int(ledger_row["receipt_ts"] - ledger_row["ts"])
    out["reconciled_by"] = source
    out["reconciled_ts"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return out


def bridge_send_result(code, body):
    """(ok, detail) from the bridge's /send response. ok is True ONLY for a delivery receipt.
    Pending (accepted, not receipted) carries PENDING_RECEIPT and is never retried; a clean
    refusal that sent nothing (not connected, bad auth) is an ordinary, retryable failure."""
    b = body if isinstance(body, dict) else {}
    if code == 200 and b.get("ok") is True:
        return True, None
    if code == 200 and b.get("pending"):
        return False, f"{PENDING_RECEIPT}: id={b.get('id')} status={b.get('status')}"
    if code == 503:
        return False, f"bridge not connected ({b.get('connection')})"
    if code == 401:
        return False, "bridge rejected the send token"
    return False, f"bridge HTTP {code}: {str(b.get('error') or body)[:120]}"


def sender_ids(sender: str, salt: str = ""):
    """Pseudonymous, stable, and still correlatable to a known pilot user.

    A transcript file that is a raw dump of phone numbers is a liability; one that
    cannot be tied back to the user who reported a bad answer is useless. The hash
    groups a conversation; the last four digits identify a tester you already know.
    """
    digits = "".join(c for c in str(sender).split("@")[0] if c.isdigit())
    h = hashlib.sha256((salt + str(sender)).encode("utf-8")).hexdigest()[:12]
    return h, digits[-4:]


def sender_domain(sender) -> str:
    """The part after '@' — `s.whatsapp.net`, `lid`, `g.us`. Not PII, and it decides
    whether a send can land at all: Baileys-based gateways sometimes deliver a LINKED-ID
    (`@lid`) form instead of the phone JID, and replying to that address is a
    delivery-into-the-void that looks like SUCCESS rather than an error. Recorded so the
    question is answerable from the transcript rather than from a live experiment."""
    s = str(sender)
    return s.split("@", 1)[1] if "@" in s else ""


def parse_webhook(body):
    """Wappfly delivery -> {kind, sender, text} or None to ignore. Pure; no I/O."""
    if not isinstance(body, dict):
        return None
    if body.get("event", "") != "messages.received":
        return None
    messages = (body.get("data") or {}).get("messages") or {}
    if messages.get("fromMe") or (messages.get("key") or {}).get("fromMe"):
        return None
    text = (messages.get("conversation")
            or messages.get("messageBody")
            or messages.get("text") or "").strip()
    sender = (messages.get("remoteJid")
              or (messages.get("key") or {}).get("remoteJid") or "")
    if not text or not sender:
        return None
    kind = "greeting" if text.lower() in GREETINGS else "question"
    out = {"kind": kind, "sender": sender, "text": text}
    if sender.endswith("@lid"):
        # A linked-ID is not a phone number. Wappfly also sends the phone in
        # `cleanedSenderPn` / `senderPn` (seen 2026-11-10), and a phone JID is the address
        # whose delivery is PROVEN, so reply there and keep the linked-ID for the record.
        # Digits are validated rather than trusted: a malformed field falls back to the
        # linked-ID, which is what shipped before and is known to deliver.
        key = messages.get("key") or {}
        for field in ("cleanedSenderPn", "senderPn"):
            raw = key.get(field) or messages.get(field) or ""
            digits = "".join(c for c in str(raw).split("@")[0] if c.isdigit())
            if 7 <= len(digits) <= 15:
                out["sender"] = digits + "@s.whatsapp.net"
                out["sender_lid"] = sender
                break
    return out


def extract_reply(result):
    """(reply, error_class, detail). The model's contract is {"reply": str}."""
    if not isinstance(result, dict):
        return None, "bad_response", f"expected object, got {type(result).__name__}"
    reply = (result.get("reply") or "").strip()
    if not reply:
        return None, "no_reply_field", f"keys={sorted(result)[:8]}"
    return reply, None, None


async def send_with_retry(send_once, to, text, settings):
    """Never raises. Returns (ok, error_detail).

    A dropped send is indistinguishable from a dropped answer as far as the user is
    concerned, so the outbound leg gets the same treatment as the inbound one.
    """
    attempts = max(1, settings.send_attempts)
    last = None
    for attempt in range(1, attempts + 1):
        try:
            ok, detail = await send_once(to, text)
            if ok:
                return True, None
            last = detail
            if is_pending_receipt(detail):
                # Accepted, not yet receipted: a second send could duplicate a message that is
                # on its way. Stop here; the bridge's pending ceiling flags it if it never lands.
                print(f"[send] pending receipt, NOT retrying -- {scrub(last, settings.secrets)}")
                return False, scrub(last, settings.secrets)
        except Exception as e:                                       # noqa: BLE001
            last = f"{type(e).__name__}: {e}"
        last = scrub(last, settings.secrets)
        print(f"[send] attempt {attempt}/{attempts} failed — {last}")
        if attempt < attempts:
            await asyncio.sleep(settings.send_retry_delay_s)
    return False, last


def _blank_row(kind, sender, settings, build):
    sender_hash, sender_tail = sender_ids(sender, settings.sender_salt)
    return {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "build": build,
        "kind": kind,
        "sender_hash": sender_hash,
        "sender_tail": sender_tail,
        "sender_domain": sender_domain(sender),
        # A designated test sender (TEST_SENDERS): full loop, excluded from the participant counts.
        "test_sender": is_test_sender_hash(settings, sender_hash),
        # The address REPLIES go to: phone | lid | other. send_state: delivered | pending_receipt
        # | failed (None until a send is attempted).
        "reply_address_kind": reply_address_kind(sender),
        "send_state": None,
        "question": None,
        "reply": None,
        "reply_chars": 0,
        "model_latency_ms": None,
        "total_latency_ms": None,
        "fallback": False,
        "error_class": None,
        "error_detail": None,
        "cold_start_suspected": False,
        "ack_sent": False,
        "acks_sent": 0,
        "send_ok": None,
        "send_error": None,
        # 'sent' | 'held' | 'misconfigured'. None on rows written before supervised mode
        # existed, which is why every reader must treat None as 'sent' explicitly rather
        # than letting a missing key default silently.
        "supervision": None,
    }


async def deliver(sender, text, ask, send_once, settings, build="dev",
                  hold_reply=None):
    """Answer one question. MUST NOT RAISE.

    `ask` is an async callable taking the message and returning the model's dict.
    `send_once` is an async callable (to, text) -> (ok, detail).
    `hold_reply` is an async callable (to, text, row) -> (ok, detail) used for the ANSWER
    ONLY when `settings.supervised` is on — it stores a draft instead of sending it. The ack
    ladder keeps `send_once` regardless, which is the whole reason this is a second
    parameter and not a substitution of the first. Note the THIRD argument: a reviewer needs
    the row, and a (to, text) hold cannot see it.

    Returns the transcript row; the caller persists it.
    """
    t0 = time.monotonic()
    row = _blank_row("question", sender, settings, build)
    row["question"] = text
    try:
        answered = asyncio.Event()
        state = {"acks_sent": 0}

        async def ack_ladder():
            """Walk the rungs, stop the moment the answer lands.

            ONE COROUTINE, NOT ONE TIMER PER RUNG. Two independent timers can BOTH be in
            flight when the answer arrives, and the loser then reassures a user who has
            already been answered — "still working on it" delivered after the reply is
            worse than the silence it was meant to fill. A single sequential walker
            cannot do that: it re-checks `answered` before every rung and returns.

            THE CAP IS STRUCTURAL, NOT A COUNTER. The ladder is a two-element list and
            the loop cannot outlive it, so there is no failure mode — no retry, no
            timeout, no exception path — that ends with a user being pinged indefinitely.

            Delays are computed from ELAPSED time rather than by sleeping each gap in
            turn: `send_with_retry` on rung one can itself take seconds, and nominal
            bookkeeping would push rung two past the cold-start window it exists to cover.
            """
            if settings.slow_ack_after_s <= 0:
                return                     # kill switch — the whole ladder, not half of it
            # In supervised mode the first rung says a PERSON is checking the answer,
            # because that is true and because the wait is now human-paced rather than
            # GPU-paced. "Nearly done" would be a lie at 2am.
            first = settings.supervised_ack if settings.supervised else SLOW_ACK
            rungs = [(settings.slow_ack_after_s, first)]
            if settings.second_ack_after_s > settings.slow_ack_after_s:
                rungs.append((settings.second_ack_after_s, SECOND_ACK))
            t_ack = time.monotonic()
            for after_s, message in rungs:
                delay = max(0.0, after_s - (time.monotonic() - t_ack))
                try:
                    await asyncio.wait_for(answered.wait(), timeout=delay)
                    return                 # the answer beat this rung — stay quiet
                except asyncio.TimeoutError:
                    pass
                state["acks_sent"] += 1
                await send_with_retry(send_once, sender, message, settings)

        ack_task = asyncio.create_task(ack_ladder())
        m0 = time.monotonic()
        reply = error_class = detail = None
        result = None
        limit_s = (settings.supervised_model_timeout_s if settings.supervised
                   else settings.model_timeout_s)
        row["model_timeout_s"] = limit_s
        try:
            result = await asyncio.wait_for(ask(text), timeout=limit_s)
        except asyncio.TimeoutError:
            error_class = "timeout"
            detail = f"no reply after {limit_s}s"
        except Exception as e:                                       # noqa: BLE001
            error_class = "model_error"
            detail = scrub(f"{type(e).__name__}: {e}", settings.secrets)
        finally:
            answered.set()
            try:
                await ack_task
            except Exception as e:                                   # noqa: BLE001
                print(f"[ack] failed — {scrub(e, settings.secrets)}")

        # DELIBERATELY OUTSIDE the try above. When this parse sat inside it, a bug in
        # OUR OWN code was caught by the model's `except Exception` and recorded as
        # `model_error` — an error class that lies about who failed, which is the exact
        # instrument-lie pattern this project keeps catching. A test forces it.
        if error_class is None:
            reply, error_class, detail = extract_reply(result)

        model_s = time.monotonic() - m0
        row["model_latency_ms"] = int(model_s * 1000)
        row["cold_start_suspected"] = model_s >= settings.cold_start_suspected_s
        # `ack_sent` KEEPS ITS NAME AND ITS MEANING. It is already in the pilot's
        # transcript rows and in the analysis quoted in PROGRESS; renaming it would
        # silently break every reader of the record. `acks_sent` is added alongside,
        # because "was the user reassured" and "how many times" are now different
        # questions — and the second is what tells us whether 45s was the right band.
        row["acks_sent"] = state["acks_sent"]
        row["ack_sent"] = state["acks_sent"] > 0
        row["error_class"] = error_class
        row["error_detail"] = detail

        if reply is None:
            row["fallback"] = True
            reply = FALLBACK
            print(f"[chike] FALLBACK to {row['sender_hash']} — {error_class}: {detail}")

        row["reply"] = reply
        row["reply_chars"] = len(reply)
        # ⛔ THE ONE BRANCH SUPERVISION ADDS. `supervised` with no `hold_reply` supplied
        # must NOT silently fall back to sending: that is the failure direction that
        # breaks the founder's R7 condition while looking like it works, so it is recorded
        # as a handler bug and the answer is withheld.
        if settings.supervised and hold_reply is None:
            row["supervision"] = "misconfigured"
            row["error_class"] = row["error_class"] or "handler_bug"
            row["error_detail"] = ("supervised=True with no hold_reply — the answer was "
                                   "WITHHELD rather than sent unreviewed")
            row["send_ok"] = False
            row["send_error"] = "withheld: supervision misconfigured"
            print("[chike] SUPERVISION MISCONFIGURED — answer withheld, not sent")
        elif settings.supervised:
            # ⛔ THE HOLD TAKES THE ROW AND DOES **NOT** GO THROUGH `send_with_retry`, for
            # two reasons that are easy to get wrong in opposite directions:
            #
            #   THE SIGNATURE. A hold needs the row — the queue entry carries the question,
            #   the latency and the error class so the reviewer can judge the draft instead
            #   of guessing at it. My first attempt kept the (to, text) shape and closed over
            #   a mutable dict to smuggle the row in; the row does not EXIST until deliver()
            #   returns, so that closure would have read an empty dict and raised inside the
            #   one path that must never raise. Three arguments, no smuggling.
            #
            #   NO RETRY. `send_attempts=2` is right for a flaky HTTP send and wrong for a
            #   key-value put: a put that appears to fail but landed would be retried into a
            #   DUPLICATE queue entry, and the reviewer would send the same answer twice —
            #   which `answer_and_send`'s own `retries=0` comment already names as worse
            #   than one missing answer.
            row["supervision"] = "held"
            try:
                ok, send_error = await hold_reply(sender, reply, row)
            except Exception as e:                                   # noqa: BLE001
                ok, send_error = False, scrub(f"{type(e).__name__}: {e}", settings.secrets)
            row["send_ok"] = ok
            row["send_error"] = send_error
            # `reply` here is the DRAFT, not what the user received. Renaming the field
            # would break every existing transcript reader, so the distinction is carried
            # by `supervision` — and a reader that ignores it will over-count deliveries,
            # which is why review_summary() below refuses to compute a delivery rate
            # without it.
        else:
            row["supervision"] = "sent"
            ok, send_error = await send_with_retry(send_once, sender, reply, settings)
            row["send_ok"] = ok
            row["send_error"] = send_error
            row["send_state"] = send_state(ok, send_error)

    except Exception as e:                                           # noqa: BLE001
        # Reaching here means a bug in the code above, not a model failure. The user
        # still gets an answer and we still get a row — the whole point of the rewrite.
        row["fallback"] = True
        row["error_class"] = row["error_class"] or "handler_bug"
        row["error_detail"] = scrub(f"{type(e).__name__}: {e}", settings.secrets)
        print(f"[chike] HANDLER BUG — {row['error_detail']}")
        try:
            ok, send_error = await send_with_retry(send_once, sender, FALLBACK, settings)
            row["reply"], row["send_ok"], row["send_error"] = FALLBACK, ok, send_error
        except Exception as e2:                                      # noqa: BLE001
            row["send_ok"] = False
            row["send_error"] = scrub(e2, settings.secrets)
    finally:
        row["total_latency_ms"] = int((time.monotonic() - t0) * 1000)
    return row


# ---------------------------------------------------------------------------
# SUPERVISED REVIEW — the queue's pure logic (2026-10-10)
# ---------------------------------------------------------------------------
# ⛔⛔ DRAFT, EDIT AND FINAL ARE THREE SEPARATE FIELDS AND ARE NEVER COLLAPSED. This is the
# founder's own requirement and it is the most valuable thing the pilot produces: the edits
# are LABELLED CORRECTIONS on real traffic, which is precisely what no sweep over our own
# corpora can manufacture (R21/R33 — our corpora share vocabulary with our facts by
# construction, and what real users type is a traffic claim no offline instrument can settle).
#
# A design that stored only the final text would destroy the dataset while appearing to work:
# every transcript would look like a correct answer, the queue would look healthy, and the
# one irreplaceable signal — WHAT the model got wrong and HOW a human fixed it — would be
# gone. So `draft` is immutable once written, `final` is what was sent, and `edit_reason` is
# required whenever they differ.
REVIEW_ACTIONS = ("send", "edit", "withhold", "retry")


# ---------------------------------------------------------------------------
# THE ROSTER, AND IDENTITY WITHOUT A LOGIN
# ---------------------------------------------------------------------------
WA_USER_DOMAIN = "s.whatsapp.net"
_DEFAULT_COUNTRY_CODE = "255"          # Tanzania
_MIN_PHONE_DIGITS = 9


def number_tail(number, n=4):
    """Last n DIGITS of a number or JID. `number[-4:]` on a JID returns 'z.net'."""
    digits = "".join(c for c in str(number or "").split("@")[0] if c.isdigit())
    return digits[-n:]


def normalize_reviewer_number(raw):
    """A phone number as a person writes it -> the WhatsApp ID form that is proven to send.

    "+255 754 123 456", "0754123456", "255754123456" and "255754123456@s.whatsapp.net" all
    become "255754123456@s.whatsapp.net" — the form that sent successfully on 2026-08-15.
    A leading 0 on a ten-digit number is Tanzanian national format and becomes 255.
    Returns None when there are too few digits to be a phone number: a junk seat that can
    never be notified is worse than a refused one, and /health's reviewer count shows it.
    """
    digits = "".join(c for c in str(raw or "").split("@")[0] if c.isdigit())
    if len(digits) == 10 and digits.startswith("0"):
        digits = _DEFAULT_COUNTRY_CODE + digits[1:]
    if len(digits) < _MIN_PHONE_DIGITS:
        return None
    return f"{digits}@{WA_USER_DOMAIN}"


_HASH12_RE = re.compile(r"^[0-9a-f]{12}$")


def parse_test_senders(raw, salt=""):
    """TEST_SENDERS -> (frozenset of sender hashes, number of entries rejected).

    Each comma/semicolon-separated entry is EITHER a phone number (any way a person writes it; hashed exactly as a
    sender is hashed, `sender_ids(<normalised JID>, salt)`) OR `hash:<12 hex>`, a sender hash as shown in /health and
    the transcripts -- the second form exists because a participant who arrives only as a `@lid` address cannot be
    reached from a phone number. THE `hash:` PREFIX IS REQUIRED, not decoration: a Tanzanian number written
    255XXXXXXXXX is exactly 12 digits, i.e. a valid-looking 12-hex string, and the first draft of this parser read it
    as a hash and hashed NOTHING (caught by a test, 2026-11-13). An optional `:label` after a phone is ignored. A rejected entry is COUNTED, never silently
    dropped (a typo that quietly leaves a test phone counted is the failure this must make visible)."""
    hashes, rejected = set(), 0
    for chunk in (raw or "").replace(";", ",").split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if chunk.lower().startswith("hash:"):
            h = chunk[5:].strip().partition(":")[0].strip().lower()
            if _HASH12_RE.match(h):
                hashes.add(h)
            else:
                rejected += 1
            continue
        entry = chunk.partition(":")[0].strip()
        jid = normalize_reviewer_number(entry)
        if jid is None:
            rejected += 1
            continue
        hashes.add(sender_ids(jid, salt)[0])
    return frozenset(hashes), rejected


def is_test_sender_hash(settings_or_hashes, sender_hash):
    # A settings-like object without the field (older stubs) means "no test senders", never "iterate the object".
    hashes = (settings_or_hashes if isinstance(settings_or_hashes, (set, frozenset, tuple, list))
              else getattr(settings_or_hashes, "test_sender_hashes", ()))
    return bool(sender_hash) and sender_hash in (hashes or ())


def parse_roster(raw):
    """"+255 700 000 001:Asha, 0700000002" -> (("255700000001@s.whatsapp.net", "Asha"), ...).

    Numbers are NORMALISED to WhatsApp ID form (see normalize_reviewer_number), so the roster
    can be written the way a person writes a phone number, and the same person written two
    ways is one seat.

    ⚠️ ORDER AND DUPLICATES ARE PRESERVED-THEN-DEDUPED BY NUMBER, not silently collapsed: a
    roster with the same number twice under two names is a configuration mistake, and
    keeping the FIRST name makes the behaviour predictable rather than dependent on dict
    ordering. An entry with no usable number is dropped, because a nameless blank would
    otherwise become a reviewer who can never be notified and never acts — i.e. a phantom
    seat that quietly lowers effective capacity.
    """
    out, seen = [], set()
    for chunk in (raw or "").replace(";", ",").split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        number, _, name = chunk.partition(":")
        number = normalize_reviewer_number(number)
        if not number or number in seen:
            continue
        seen.add(number)
        out.append((number, name.strip() or number_tail(number)))
    return tuple(out)


def reviewer_id(signing_key, number):
    """A stable, non-reversible handle for one reviewer.

    ⛔ USED IN LINKS INSTEAD OF THE PHONE NUMBER. A link is pasted into WhatsApp, forwarded,
    screenshotted and logged by every hop in between; putting a reviewer's number in a query
    string publishes it to all of them for no benefit, since the roster can map the handle
    back locally.
    """
    return hmac.new(_key(signing_key), f"rid|{number}".encode("utf-8"),
                    hashlib.sha256).hexdigest()[:10]


# ── ONE OPAQUE STRING IN THE PATH, NOT THREE JOINED QUERY PARAMETERS (founder, 2026-11-12) ────────────────────────
#
# Four real links failed authentication (measured: the 404s ran in ~75 ms, before any queue read) although the same
# container built and checked every one and the ids round-trip. Whatever damaged them in transit, a link made of
# `?r=<id with + and :>&v=<handle>&t=<token>` is a LONG, PUNCTUATED string: `&`, `=`, `+` and `%3A` are exactly what link
# detectors, copy-paste and in-app browsers cut, decode or "clean" (`t` and `v` are even well-known tracking-parameter
# names). A path token has none of that: ONE unbroken run of [0-9a-z2-7], no `&`, no `=`, no `+`, no `%`, nothing to
# split on, and lower-case only, so a client that case-folds a path cannot corrupt it.
#
#     token = handle(10 hex) + signature(32 hex) + base32(review_id)      fixed-width fields, then the id
#
# The SIGNING IS UNCHANGED: `signature` is review_token(key, review_id, number), the handle is reviewer_id(key, number),
# and authenticate_reviewer is the same function -- the token is only a different ENVELOPE for the same three facts, so
# a forged token still fails, and a TRUNCATED one either fails to decode or decodes to a different id whose HMAC does not
# match. The envelope reveals nothing readable (the id is base32, not text).
import base64 as _b64
import re as _re_tok

# The id part is >= 1 char: whatever review_link_token MINTS must parse back (a builder and a parser that disagree about
# the shortest legal token is a latent defect). Junk is rejected by the fixed-width hex prefix and the alphabet, not by length.
_TOKEN_RE = _re_tok.compile(r"^[0-9a-f]{10}[0-9a-f]{32}[a-z2-7]+$")


# ── THE RULE, ENFORCED (founder, 2026-11-12): A LINK SENT THROUGH A CHAT APP IS ONE UNBROKEN ALPHANUMERIC TOKEN ──────
#
# Two bugs, one class. `+` (2026-11-10): legal in a URL, decoded to a SPACE by a query parser, so every real draft's link
# returned 404. `:` (2026-11-12): legal in a URL, treated as a BOUNDARY by whatever displayed the link, so the URL arrived
# cut at the first colon of the review id and lost the rest of the id, the `+`, `&v=` and `&t=`. Different characters,
# same mechanism: a character that is LEGAL in a URL but means something to the thing that DISPLAYS it. Escaping fixes
# one character at a time; the only robust form is a token with NO character that anything treats specially.
#
# So the shape is checked, not remembered: `https://<host>/<[a-z0-9]+>` -- no query, no fragment, no percent-encoding,
# no punctuation in the path. `_draft_link` calls this before returning, so a future change that sneaks a `?`, `&`, `=`,
# `+`, `%`, `:` or `-` into a link we send FAILS CLOSED (no push goes out) instead of shipping a link that dies in transit.
_CHAT_LINK_RE = _re_tok.compile(r"^https://[a-z0-9][a-z0-9.-]*/[a-z0-9]+$")


def chat_link_problems(url):
    """[] if `url` is safe to send through a chat app; otherwise the reasons (one per offending character class)."""
    u = str(url or "")
    if _CHAT_LINK_RE.match(u):
        return []
    out = []
    if not u.startswith("https://"):
        out.append("is not https")
    rest = u.split("://", 1)[-1]
    names = {"?": "a query string", "&": "an ampersand", "=": "an equals sign", "+": "a plus", "%": "percent-encoding",
             "#": "a fragment", " ": "whitespace"}
    for ch, why in names.items():                   # anywhere after the scheme: host, path or query
        if ch in rest:
            out.append("contains " + why)
    host, _, path = rest.partition("/")
    more = {":": "a colon", "-": "a hyphen", ".": "a dot", "_": "an underscore"}
    for ch in sorted(set(path)):
        if ch in names:
            continue
        if not (ch.isascii() and (ch.islower() or ch.isdigit())):
            out.append("path contains " + more.get(ch, repr(ch)))
    if "/" not in rest or not path:
        out.append("has no path token")
    if not out:
        out.append("does not match https://<host>/<[a-z0-9]+>")
    return out


def assert_chat_safe_link(url):
    """Fail closed: raise rather than let an unsafe link into a message."""
    problems = chat_link_problems(url)
    if problems:
        raise ValueError("unsafe chat link (" + "; ".join(problems) + ")")
    return url


def review_link_token(signing_key, review_id, number):
    handle = reviewer_id(signing_key, number)
    sig = review_token(signing_key, review_id, number)
    idpart = _b64.b32encode(str(review_id).encode("utf-8")).decode("ascii").lower().rstrip("=")
    return handle + sig + idpart


def parse_review_link_token(token):
    """(review_id, handle, signature) or None. Never raises; says nothing about WHETHER it will authenticate."""
    if not token:
        return None
    t = str(token).strip().lower()
    if not _TOKEN_RE.match(t):
        return None
    handle, sig, idpart = t[:10], t[10:42], t[42:]
    try:
        raw = _b64.b32decode(idpart.upper() + "=" * (-len(idpart) % 8))
        review_id = raw.decode("utf-8")
    except Exception:                                                # noqa: BLE001
        return None
    return review_id, handle, sig


def normalise_review_id(review_id):
    """A review id as stored. A raw `+` in a query string arrives as a SPACE, and the ids
    minted before links were URL-encoded carry `+00:00` — those notifications are already on
    a reviewer's phone. Review ids never contain whitespace by construction (isoformat ts +
    `-` + hex), so mapping a space back is lossless, and the HMAC still binds the exact id:
    this widens what is ACCEPTED as the id, never who is authenticated."""
    return None if review_id is None else str(review_id).replace(" ", "+")


def review_token(signing_key, review_id, number):
    """The per-(draft, reviewer) action token. HMAC, so it cannot be constructed without the
    key, and bound to BOTH the draft and the reviewer so one reviewer's link cannot act on
    another's draft or be replayed as someone else."""
    return hmac.new(_key(signing_key), f"tok|{review_id}|{number}".encode("utf-8"),
                    hashlib.sha256).hexdigest()[:32]


def _key(signing_key):
    return (signing_key or "").encode("utf-8")


def authenticate_reviewer(settings, review_id, rid, token):
    """(number, name) for a valid link, else None.

    ⛔ FAILS CLOSED WITH NO SIGNING KEY. An empty key would make `hmac` produce a perfectly
    stable digest that anyone who knows the scheme can reproduce — so a missing secret would
    not disable the links, it would make every one of them forgeable. That is the direction
    that matters here, so it is checked first and explicitly.

    ⚠️ CONSTANT-TIME COMPARISON. The tokens are short-lived and low-value, and
    `compare_digest` costs nothing; a `==` here would be the one timing side channel in a
    path that authorises sending a compliance answer to a stranger.
    """
    if not settings.review_signing_key:
        return None
    if not (review_id and rid and token):
        return None
    for number, name in settings.roster:
        if hmac.compare_digest(reviewer_id(settings.review_signing_key, number), str(rid)):
            expected = review_token(settings.review_signing_key, review_id, number)
            if hmac.compare_digest(expected, str(token)):
                return number, name
            return None
    return None


# ---------------------------------------------------------------------------
# THE CLAIM LOCK — two reviewers must not both act
# ---------------------------------------------------------------------------
# ⛔⛔ THE RACE THIS EXISTS FOR IS NOT "TWO SENDS". It is one reviewer SENDING while another
# WITHHOLDS, which would deliver an answer a human had just decided to withhold — and the
# record would hold both decisions, so even afterwards it would not be clear what the
# participant received. A single-decision lock makes that unreachable rather than unlikely.
CLAIM_OUTCOMES = ("claimed", "already_yours", "held_by_other", "decided")


def claim(item, reviewer_number, *, now=None, ttl_s=900.0):
    """(item, outcome). Pure, so the lock's rules are testable without Modal.

    A claim is granted when the draft is unclaimed OR its claim has EXPIRED. Expiry is read
    from the stored timestamp rather than tracked by a timer, because a timer lives in one
    container and the queue is read from many.
    """
    now = now or datetime.now(timezone.utc)
    if item.get("status") != "pending":
        return item, "decided"
    held_by = item.get("claimed_by")
    if held_by and not _claim_expired(item, now):
        return (item, "already_yours") if held_by == reviewer_number else (item,
                                                                          "held_by_other")
    out = dict(item)
    out["claimed_by"] = reviewer_number
    out["claimed_at"] = now.isoformat(timespec="seconds")
    out["claim_expires_at"] = (
        now + timedelta(seconds=float(ttl_s))).isoformat(timespec="seconds")
    out["claim_count"] = int(item.get("claim_count") or 0) + 1
    return out, "claimed"


def _claim_expired(item, now):
    exp = item.get("claim_expires_at")
    if not exp:
        return True
    try:
        return datetime.fromisoformat(exp) <= now
    except Exception:                                                # noqa: BLE001
        # An unparseable expiry is treated as EXPIRED, which releases the draft to the
        # roster. The alternative — treating it as valid forever — would strand a
        # participant's answer behind one corrupt field, and stranding is the failure this
        # whole mechanism is built to avoid.
        return True


def release_expired_claim(item, *, now=None):
    """(item, released). Releasing is the ONLY thing a timeout does.

    ⛔⛔ THERE IS NO SEND PATH IN THIS FUNCTION, OR IN ANY TIMEOUT PATH, ANYWHERE. A draft
    whose claim expires goes back to the roster; a draft nobody ever claims stays pending and
    is re-notified. R7's condition rests on exactly this: no elapsed time, no queue depth and
    no number of reviewers causes a reply to reach a participant unread.
    """
    now = now or datetime.now(timezone.utc)
    if item.get("status") != "pending" or not item.get("claimed_by"):
        return item, False
    if not _claim_expired(item, now):
        return item, False
    out = dict(item)
    out["released_from"] = item.get("claimed_by")
    out["released_at"] = now.isoformat(timespec="seconds")
    out["claimed_by"] = None
    out["claimed_at"] = None
    out["claim_expires_at"] = None
    out["release_count"] = int(item.get("release_count") or 0) + 1
    return out, True


def renotify_exhausted(item, max_renotifies=3):
    """True once a draft has used its re-notifications. It then goes to the daily digest."""
    if int(max_renotifies) <= 0:           # 0 = NO CAP (founder, 2026-11-13: re-notify every N minutes, no cap)
        return False
    return int(item.get("renotify_count") or 0) >= int(max_renotifies)


def digest_candidates(items, max_renotifies=3):
    """Pending drafts that have used up their re-notifications, oldest first."""
    out = [i for i in items if i.get("status") == "pending"
           and renotify_exhausted(i, max_renotifies)]
    return sorted(out, key=lambda i: i.get("ts_held") or "")


def digest_due(last_digest_ts, now_ts, *, every_s=86400.0):
    return not last_digest_ts or (now_ts - float(last_digest_ts)) >= every_s


def digest_text(items, link_for, *, now=None, max_items=5):
    """The once-a-day roster message for drafts that stopped being re-notified. Names the
    customer by tail only; each line carries that reviewer's own link. Roster-only: nothing
    here is, or can become, a participant message."""
    now = now or datetime.now(timezone.utc)
    lines = [f"📋 MUHTASARI WA KILA SIKU — rasimu {len(items)} bado zinasubiri "
             f"(zimeacha kukumbushwa)"]
    for it in items[:max_items]:
        try:
            age_h = int((now - datetime.fromisoformat(it["ts_held"])).total_seconds() // 3600)
        except Exception:                                            # noqa: BLE001
            age_h = "?"
        tag = " [MODELI IMESHINDWA]" if it.get("fallback") else ""
        lines += ["", f"• ...{it.get('sender_tail') or '????'} · saa {age_h} zilizopita{tag}",
                  f"  {(it.get('question') or '')[:80]}", f"  {link_for(it)}"]
    if len(items) > max_items:
        lines.append(f"…na {len(items) - max_items} zaidi")
    lines += ["", "Hakuna jibu linalotumwa mpaka mtu abonyeze. Zuia rasimu za majaribio."]
    return "\n".join(lines)


def needs_renotify(item, *, now=None, renotify_after_s=1800.0, max_renotifies=3):
    """True when an UNCLAIMED pending draft has gone unanswered long enough to re-notify.

    A claimed, unexpired draft is NOT re-notified — someone is reading it, and pinging the
    whole roster about a draft already in hand is how a roster learns to ignore the
    notifications. And never more than `max_renotifies` times: after that the draft is in
    the daily digest, because an uncapped reminder is a ping every half hour for ever."""
    now = now or datetime.now(timezone.utc)
    if item.get("status") != "pending":
        return False
    if renotify_exhausted(item, max_renotifies):
        return False
    if item.get("claimed_by") and not _claim_expired(item, now):
        return False
    stamp = item.get("last_notified_at") or item.get("ts_held")
    if not stamp:
        return True
    try:
        return (now - datetime.fromisoformat(stamp)).total_seconds() >= float(
            renotify_after_s)
    except Exception:                                                # noqa: BLE001
        return True


def review_item(row, sender, draft, engine_working=None, facts=(), review_id=None, model_calls=None, guards=None):
    """A queue entry. `sender` is the REAL number, which the transcript deliberately does not
    store — so this lives in its own store, behind its own token, and is purged on decision.

    ⚠️ THAT ASYMMETRY IS DELIBERATE AND WORTH STATING: transcripts keep a salted hash plus a
    4-digit tail precisely so the analysis corpus carries no reachable identifier. The review
    queue CANNOT work that way, because sending the approved answer needs the number. Keeping
    them in one store would quietly re-introduce the identifier into the analysis corpus.
    """
    return {
        "review_id": review_id or row["ts"] + "-" + row["sender_hash"][:8],
        "ts_held": row["ts"],
        "build": row.get("build"),
        "sender": sender,
        "sender_hash": row["sender_hash"],
        "sender_tail": row.get("sender_tail"),
        "test_sender": bool(row.get("test_sender")),
        "question": row.get("question"),
        # IMMUTABLE. The model's own words, kept whatever the reviewer does next.
        "draft": draft,
        # The evidence the reviewer needs in order to judge the draft rather than guess at
        # it: the engine's deterministic working and the facts retrieval actually served.
        "engine_working": engine_working,
        # How many times the model was called for this reply (0 = no model-written word) and which guards acted. None =
        # unknown, which the review timeout treats as NOT eligible. `held_at` = when the draft became reviewable.
        "model_calls": model_calls,
        "guards": (list(guards) if guards is not None else None),
        "held_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "facts": list(facts),
        "model_latency_ms": row.get("model_latency_ms"),
        "fallback": row.get("fallback"),
        "error_class": row.get("error_class"),
        "status": "pending",
        "final": None,
        "edit_reason": None,
        "decided_ts": None,
        "decision_latency_s": None,
        # ── the claim lock ──
        "claimed_by": None,
        "claimed_at": None,
        "claim_expires_at": None,
        "claim_count": 0,
        "release_count": 0,
        "last_notified_at": None,
        "notify_count": 0,
        "renotify_count": 0,
        # When the reviewer was FIRST pushed. decision_latency_s counts from here: counting from
        # the question folded the model's own wait into the reviewer's time (317s reported
        # for a 76s review on 2026-11-11).
        "first_notified_at": None,
        "retry_of": None,
        # ⛔ ATTRIBUTION. WHO decided, recorded beside WHAT they decided, so each reviewer's
        # corrections can be read separately — which is the only way to notice that one
        # reviewer is approving what another would have caught. A roster without per-reviewer
        # attribution is a roster whose weakest reviewer is invisible.
        "decided_by": None,
        "decided_by_name": None,
    }


def apply_decision(item, action, *, reviewer=None, edited=None, reason=None,
                   reviewer_name=None, now=None):
    """(updated item, text to send or None). Pure — no I/O, so the rules are testable.

    ⛔ A REASON IS REQUIRED FOR EVERY DEPARTURE FROM THE DRAFT, and the requirement is
    enforced here rather than in the UI. A UI-only check is bypassed by the first curl, and
    an edit with no reason is a correction whose *label* is missing — which is the entire
    value of the edit. `send` needs no reason: agreeing with the draft is the null decision.

    ⛔⛔ AND THE CLAIM IS REQUIRED, CHECKED HERE RATHER THAN AT THE ENDPOINT. The race that
    matters is not two sends — it is one reviewer SENDING while another WITHHOLDS, which
    delivers an answer a human had just decided to withhold. Checking the lock in the HTTP
    layer would leave `apply_decision` usable without it by the next caller, and the next
    caller is a sweeper, a backfill script or a test.
    """
    if item.get("status") != "pending":
        raise ValueError(f"review {item.get('review_id')} is already "
                         f"{item.get('status')!r} — a decision is taken once")
    if action not in REVIEW_ACTIONS:
        raise ValueError(f"unknown review action {action!r}; expected one of {REVIEW_ACTIONS}")
    if not reviewer:
        raise ValueError("a decision needs the reviewer who took it — an unattributed "
                         "decision cannot be read back per reviewer, which is the whole "
                         "reason a roster is auditable")
    now = now or datetime.now(timezone.utc)
    holder = item.get("claimed_by")
    if not holder or _claim_expired(item, now):
        raise ValueError(f"review {item.get('review_id')} is not claimed (or the claim has "
                         f"expired) — claim it before acting, so two reviewers cannot both "
                         f"decide")
    if holder != reviewer:
        raise ValueError(f"review {item.get('review_id')} is claimed by another reviewer "
                         f"until {item.get('claim_expires_at')} — only the holder may act")
    if action in ("edit", "withhold") and not (reason or "").strip():
        raise ValueError(f"action {action!r} requires a reason — the reason is the label on "
                         f"the correction and is the most valuable field in the record")
    if action == "edit" and not (edited or "").strip():
        raise ValueError("action 'edit' requires the edited text")

    out = dict(item)
    out["status"] = {"send": "sent", "edit": "edited", "withhold": "withheld",
                     "retry": "retried"}[action]
    out["decided_by"] = reviewer
    out["decided_by_name"] = reviewer_name or number_tail(reviewer)
    out["decided_ts"] = now.isoformat(timespec="seconds")
    out["edit_reason"] = (reason or "").strip() or None
    if action == "send":
        out["final"] = item["draft"]
    elif action == "edit":
        out["final"] = edited.strip()
    else:
        out["final"] = None        # withhold and retry send NOTHING to the participant
    try:
        decided = datetime.fromisoformat(out["decided_ts"])
        held = datetime.fromisoformat(item["ts_held"])
        pushed = datetime.fromisoformat(item["first_notified_at"])             if item.get("first_notified_at") else held
        out["decision_latency_s"] = int((decided - pushed).total_seconds())       # from the PUSH
        out["time_from_question_s"] = int((decided - held).total_seconds())      # the old figure
    except Exception:                                                # noqa: BLE001
        out["decision_latency_s"] = None
    # `draft` is never touched. Asserted here rather than trusted, because a dict copy that
    # later grows an in-place edit somewhere would destroy the dataset silently.
    assert out["draft"] == item["draft"], "the draft must survive every decision verbatim"
    return out, out["final"]


_PUSH_FACTS_MAX = 5
_PUSH_FACT_CHARS = 180


# ── A PARTICIPANT WHO RE-SENDS A QUESTION CREATES A SECOND DRAFT (founder, 2026-11-12) ────────────────────────
#
# When two review links failed the participant re-sent both questions, and four drafts -- two PAIRS -- were pending for
# one person. Approving both of a pair delivers the same answer twice. Nothing on the card said so. The flag is a pure
# function over the queue: another PENDING draft from the SAME sender whose question is the same or near-identical.
# Word-set Jaccard, because the pairs differ by one word ("nisajili" vs "nijiandikishe") as often as by none -- and a
# near-identical question is exactly the one a reviewer should not answer twice.
DUPLICATE_THRESHOLD = 0.75


def _qwords(q):
    return set(_re_tok.findall(r"[a-z0-9']+", str(q or "").lower()))


def question_similarity(a, b) -> float:
    wa, wb = _qwords(a), _qwords(b)
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)


def pending_duplicates(item, items, threshold=DUPLICATE_THRESHOLD):
    """review_ids of OTHER pending drafts from the same sender with a same / near-identical question."""
    out = []
    for o in items:
        if o.get("review_id") == item.get("review_id") or o.get("status") != "pending":
            continue
        if o.get("sender_hash") != item.get("sender_hash") or not item.get("sender_hash"):
            continue
        if question_similarity(o.get("question"), item.get("question")) >= threshold:
            out.append(o.get("review_id"))
    return out


DUPLICATE_WARNING_SW = ("⚠️ MARUDIO: swali linalofanana au linalokaribia kufanana kutoka kwa mteja huyu tayari "
                        "linasubiri ({n}). Usijibu kitu kimoja mara mbili — zuia rasimu moja.")
DUPLICATE_WARNING_EN = ("DUPLICATE: a same or near-identical question from this sender is already pending ({n}). "
                        "Do not answer the same thing twice -- withhold one draft.")


# ── AN EMPTY EVIDENCE PANEL MUST BE IMPOSSIBLE TO MISTAKE FOR "NOTHING TO CHECK" (2026-11-12) ──────────────
#
# Every one of the first 7 drafts ever held reached the reviewer with NO engine working and NO facts -- the panel
# was empty because ChikeModel.run returned only the reply -- and nothing said so loudly. The push did print
# "VIGEZO VILIVYOTUMIKA (0)" and "HESABU YA MFUMO: hakuna", in the same quiet type as everything else: the
# information was technically present and visually identical to a draft that simply had nothing to check.
#
# So the rule is stated as a pure function, used by the push, BOTH cards and /health, and pinned by tests:
#   ok             the draft carries engine working or retrieved facts
#   deterministic  the text is the engine's / canned copy (path engine:*, clarification, refusal): there is no
#                  model-written claim on the card to verify, so an empty panel is the correct state
#   none           a MODEL answer (path 'fact') with no facts and no working: nothing to check it against
#   path_missing   no path recorded at all -- the signature of the evidence pipeline being broken again
#   not_applicable the model failed and this is the canned apology
EVIDENCE_LOUD = ("none", "path_missing")

EVIDENCE_WARNING_SW = ("⚠️⚠️ HAKUNA USHAHIDI — rasimu hii haina hesabu ya mfumo wala vigezo vilivyotumika. "
                       "HAKUNA CHOCHOTE cha kuilinganisha nacho. Usiidhinishe kwa sababu inasomeka vizuri: "
                       "izuie, au ithibitishe mwenyewe na TRA.")
EVIDENCE_WARNING_EN = ("NO EVIDENCE: this draft has no engine working and no retrieved facts, so there is "
                       "NOTHING on this card to check it against. Do not approve it because it reads well "
                       "-- withhold it, or verify it against TRA yourself.")
EVIDENCE_PATH_MISSING = ("(The answer path was not recorded at all -- the evidence pipeline itself may be "
                         "broken. Tell the developer.)")


def evidence_state(item) -> str:
    if item.get("fallback"):
        return "not_applicable"
    if item.get("engine_working") or item.get("facts"):
        return "ok"
    path = item.get("answer_path")
    if path and (str(path).startswith("engine:") or path in ("clarification", "coverage_refusal", "refusal")):
        return "deterministic"
    return "none" if path else "path_missing"


def evidence_is_loud(item) -> bool:
    return evidence_state(item) in EVIDENCE_LOUD


# ── THE REVIEW TIMEOUT (founder's decision, 2026-11-13 -- a CHANGE TO THE R7 READING, recorded in CLAUDE.md) ─────────
#
# BEFORE: every reply is read by a human. AFTER: every MODEL-GENERATED reply is read by a human; a deterministic engine
# answer may send after 15 minutes unreviewed. A draft not reviewed within `after_s` of becoming reviewable is either
#   * AUTO-SENT, prefixed plainly as an automated calculation not yet checked by a person -- ONLY if NO MODEL-WRITTEN
#     WORD IS IN IT (see engine_only_verdict), or
#   * left in review, and the participant gets ONE holding message (no figures, no rates) with TRA's contact.
#
# ⛔ "path: engine:*" IS NOT THE SAME AS "NO MODEL TEXT". On the compute path the reply is a MODEL-WRITTEN body with the
# engine's working appended (Orchestrator._render), and the fidelity guards exist precisely because that body can be wrong.
# Measured over the 400 gate questions (eval/controls/measure_autosend_population_2026_11_13.py): the literal rule would
# match 99 and 81 of them contain a model-written sentence; only 18 are model-free. The rule the founder stated -- "model-path
# answers never send unreviewed" -- is enforced on `model_calls == 0`, an explicit ZERO from the orchestrator's own counter.
# Anything else (missing, None, unknown, > 0) fails CLOSED.
AUTOSEND_AFTER_S = 900.0
AUTOSEND_NAME = "AUTO-SEND (engine answer, no person read it)"
AUTOSEND_PREFIX = ("Hii ni hesabu ya kiotomatiki ya mfumo — bado haijakaguliwa na mtu. "
                   "(Automated calculation, not yet checked by a person.)\n\n")
# THE URGENT-CONTACT LINE FOLLOWS THE QUESTION'S TOPIC (founder, 2026-11-13: the first version always named TRA, even for a licence
# question the answer itself sent to BRELA). Every contact below was READ FROM THE AUTHORITY'S OWN SITE on 2026-11-13 (R30: curl, not
# a guess), and nothing else is ever put in this message: a holding message that carried a figure or a rate would be an answer nobody
# reviewed (asserted in tests -- digits are allowed ONLY inside these registered contact strings).
#   TRA    tra.go.tz  (home + /index.php/contact-us): toll-free 0800 750 075, 0800 780 078, 0800 110 016; call centre 08:00-19:00 EAT Mon-Fri
#   BRELA  brela.go.tz (home + /pages/contact-us): Simu +255 (0) 22 2212800 / +255 (0) 22 2180113   -- no toll-free line is published
#   NSSF   nssf.go.tz (home): 0800116773 (toll free), (255)(22) 2200037, customercare@nssf.go.tz
#   WCF    wcf.go.tz (home): 0800110028, +255 222 926 108 / 107, working hours 2:00 asubuhi - 11:00 jioni (08:00-17:00)
AUTHORITY_CONTACTS = {
    "tra": "TRA: piga bila malipo 0800 780 078 au 0800 750 075 (Jumatatu–Ijumaa, 08:00–19:00), au tembelea tra.go.tz",
    "brela": "BRELA: piga 022 2212800 au 022 2180113, au tembelea brela.go.tz",
    "nssf": "NSSF: piga bila malipo 0800 116 773, au tembelea nssf.go.tz",
    "wcf": "WCF: piga bila malipo 0800 110 028 (08:00–17:00), au tembelea wcf.go.tz",
}
_HOLDING_HEAD = ("Jibu la swali lako bado linakaguliwa na mtu kabla ya kutumwa, kwa hiyo hatujalituma bado. "
                 "Tutakutumia mara litakapokaguliwa. Kwa jambo la dharura, wasiliana moja kwa moja na ")
# The generic form, used when the topic is not known: NO number, because naming a wrong authority is worse than naming none.
HOLDING_TEXT = _HOLDING_HEAD + "mamlaka husika."

# Topic -> authority. Deterministic and CONSERVATIVE: question text and the engine route only -- never the model's draft.
_WB = r"(?<![a-z0-9])"
_WE = r"(?![a-z0-9])"
_TOPIC_RES = {
    "nssf": _re_tok.compile(_WB + r"(nssf|mfuko wa hifadhi|hifadhi ya jamii|michango ya nssf)" + _WE, _re_tok.I),
    "wcf": _re_tok.compile(_WB + r"(wcf|mfuko wa fidia|fidia ya wafanyakazi|workers.? compensation)" + _WE, _re_tok.I),
    "brela": _re_tok.compile(_WB + r"(brela|leseni|licen[cs]e|jina la biashara|business name|usajili wa (kampuni|biashara)|"
                             r"kusajili (kampuni|biashara)|annual return|ritani ya mwaka)" + _WE, _re_tok.I),
    "tra": _re_tok.compile(_WB + r"(vat|paye|sdl|efd|tra|tin|kodi|ushuru|risiti|withholding|wht|presumptive|makadirio|"
                           r"income tax|skills development levy)" + _WE, _re_tok.I),
}
_PATH_TOPICS = {"nssf": "nssf", "wcf": "wcf", "sdl": "tra", "paye": "tra", "vat_registration": "tra", "efd_requirement": "tra",
                "presumptive": "tra", "corporate_tax": "tra", "partnership_tax": "tra", "rent_wht": "tra"}


def holding_authorities(item):
    """Ordered list of authority keys for the holding message; [] when the topic is not known (or is more than two things)."""
    found = []
    for part in str(item.get("answer_path") or "").split("+"):
        if part.startswith("engine:"):
            k = _PATH_TOPICS.get(part.split(":")[1])
            if k and k not in found:
                found.append(k)
    q = str(item.get("question") or "")
    for k in ("nssf", "wcf", "brela", "tra"):
        if _TOPIC_RES[k].search(q) and k not in found:
            found.append(k)
    return found if 1 <= len(found) <= 2 else []


def holding_text(item):
    """The ONE holding message for `item`: fixed text + the contact line of the topic's authority (or 'mamlaka husika')."""
    keys = holding_authorities(item)
    if not keys:
        return HOLDING_TEXT
    return _HOLDING_HEAD + " na ".join(AUTHORITY_CONTACTS[k] for k in keys) + "."


def parse_autosend(flag, after_s):
    """(enabled, after_s). FAIL-CLOSED: the timeout is ON only for an explicit "1"/"true"/"yes" AND a sane positive
    number of seconds; a typo in either turns the WHOLE timeout OFF (every draft then simply waits for a human, which
    is the safe direction). /health reports the parsed result."""
    on = str(flag or "").strip().lower() in ("1", "true", "yes")
    try:
        secs = float(after_s) if after_s not in (None, "") else AUTOSEND_AFTER_S
    except (TypeError, ValueError):
        return False, AUTOSEND_AFTER_S
    if not (60.0 <= secs <= 24 * 3600.0):
        return False, AUTOSEND_AFTER_S
    return on, secs


def engine_only_verdict(item):
    """(bool, reason). True ONLY for a reply with no model-written word in it.

    Every condition is positive and explicit, so a stored item that predates a field (or a field that failed to arrive)
    can never qualify by omission: missing = no."""
    if item.get("fallback"):
        return False, "fallback reply"
    path = str(item.get("answer_path") or "")
    if not path:
        return False, "no answer path recorded"
    for part in path.split("+"):
        if not part.startswith("engine:") or part.endswith(":ask"):
            return False, f"path {path!r} is not engine-only"
    if not str(item.get("engine_working") or "").strip():
        return False, "no deterministic working"
    if evidence_is_loud(item):
        return False, "the evidence block is empty"
    guards = item.get("guards")
    if not isinstance(guards, list):
        return False, "guard record missing"
    if guards:
        return False, f"a guard fired ({', '.join(map(str, guards))})"
    calls = item.get("model_calls")
    if isinstance(calls, bool) or not isinstance(calls, int):
        return False, "model-call count unknown"
    if calls != 0:
        return False, f"the model was called {calls} time(s): a model-written sentence may be in the reply"
    if not str(item.get("draft") or "").strip():
        return False, "empty draft"
    return True, "engine-only, model-free, no guard, evidence present"


def _held_clock(item):
    """When the draft became REVIEWABLE (not when the question arrived: a cold GPU start is not review time)."""
    for k in ("held_at", "first_notified_at", "ts_held"):
        v = item.get(k)
        if v:
            try:
                d = datetime.fromisoformat(v)
                return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
            except Exception:                                        # noqa: BLE001
                continue
    return None


def autosend_verdict(item, now=None, after_s=AUTOSEND_AFTER_S, enabled=True):
    """(action, reason): 'off' | 'never' | 'wait' | 'auto_send' | 'hold_notice' | 'done'. Pure.

    A claimed, unexpired draft WAITS (a person has it open: acting under them is a race, and they are by definition
    reviewing). Nothing here ever returns auto_send for a draft that engine_only_verdict rejects."""
    if not enabled:
        return "off", "review timeout is off"
    if item.get("status") != "pending":
        return "never", "not pending"
    now = now or datetime.now(timezone.utc)
    held = _held_clock(item)
    if held is None:
        return "wait", "no usable hold time"
    if (now - held).total_seconds() < float(after_s):
        return "wait", "inside the review window"
    if item.get("claimed_by") and not _claim_expired(item, now):
        return "wait", "a reviewer has it open"
    ok, why = engine_only_verdict(item)
    if ok:
        return ("done", "already auto-sent") if item.get("auto_sent_ts") else ("auto_send", why)
    if item.get("holding_notice_ts"):
        return "done", "holding notice already sent"
    return "hold_notice", why


def autosend_text(item):
    """EXACTLY what an auto-send sends: the plain prefix + the stored draft. Nothing else, no model call."""
    return AUTOSEND_PREFIX + str(item.get("draft") or "").strip()


def autosend_note(item, now=None, after_s=AUTOSEND_AFTER_S, enabled=True):
    """(sw, en) banner for a card / push, or None. Says plainly what will happen to this draft if nobody acts."""
    if item.get("status") == "auto_sent":
        return ("⚠️ ILITUMWA KIOTOMATIKI saa " + str(item.get("auto_sent_ts") or "?")
                + " bila mtu kuisoma — iangalie sasa.",
                "AUTO-SENT at " + str(item.get("auto_sent_ts") or "?") + " with NO person having read it -- check it now.")
    if not enabled or item.get("status") != "pending":
        return None
    held = _held_clock(item)
    when = ((held + timedelta(seconds=float(after_s))).strftime("%H:%M UTC") if held else "?")
    ok, why = engine_only_verdict(item)
    if ok:
        return (f"⏱️ AUTO-SEND: jibu hili la injini (halina maneno ya modeli) litatumwa lenyewe saa {when} usipoliangalia.",
                f"AUTO-SEND: this model-free engine answer SENDS ITSELF at {when} unless you act.")
    return (f"⏱️ JIBU LA MODELI: halitatumwa bila kukaguliwa. Saa {when} mteja atapata ujumbe wa kusubiri tu.",
            f"MODEL ANSWER: never auto-sent. At {when} the participant gets a holding message only ({why}).")


def latency_summary(items, now=None, window_s=86400.0, target_s=900.0, test_hashes=()):
    """Question-to-delivery over the last `window_s`, median and worst, how many exceeded `target_s`, and WHY.

    Delivery = the moment the answer was handed to WhatsApp and accepted (`decided_ts`; for an auto-send, `auto_sent_ts`).
    Cause of an over-target answer: `gpu_or_model` when the model's own time was at least as long as the human wait, else
    `review_wait`; `cold_start` is the subset where the model took >= 30 s. Withheld drafts are not deliveries. Pending
    drafts older than the target are counted separately (`undelivered_over_target`) -- they are the worst latencies and
    must not vanish from a figure computed over delivered answers only. Test senders are reported in `including_test`."""
    now = now or datetime.now(timezone.utc)

    def one(rows):
        totals, over, causes, cold, autos, undeliv = [], 0, {"review_wait": 0, "gpu_or_model": 0}, 0, 0, 0
        for i in rows:
            held0 = None
            try:
                held0 = datetime.fromisoformat(i.get("ts_held"))
                held0 = held0 if held0.tzinfo else held0.replace(tzinfo=timezone.utc)
            except Exception:                                        # noqa: BLE001
                held0 = None
            if held0 is None:
                continue
            if i.get("status") == "pending":
                if (now - held0).total_seconds() > target_s and (now - held0).total_seconds() <= window_s * 7:
                    undeliv += 1
                continue
            if i.get("status") not in ("sent", "edited", "auto_sent") or i.get("send_ok") is not True:
                continue
            stamp = i.get("auto_sent_ts") if i.get("status") == "auto_sent" else i.get("decided_ts")
            try:
                done = datetime.fromisoformat(stamp)
                done = done if done.tzinfo else done.replace(tzinfo=timezone.utc)
            except Exception:                                        # noqa: BLE001
                continue
            if (now - done).total_seconds() > window_s:
                continue
            total = max(0.0, (done - held0).total_seconds())
            totals.append(total)
            autos += 1 if i.get("status") == "auto_sent" else 0
            if total > target_s:
                over += 1
                model_s = float(i.get("model_latency_ms") or 0) / 1000.0
                if model_s >= total - model_s:
                    causes["gpu_or_model"] += 1
                    cold += 1 if model_s >= 30 else 0
                else:
                    causes["review_wait"] += 1
        totals.sort()
        return {"delivered": len(totals),
                "median_s": (int(totals[len(totals) // 2]) if totals else None),
                "worst_s": (int(totals[-1]) if totals else None),
                "over_target": over, "over_target_causes": causes, "over_target_cold_start": cold,
                "auto_sent": autos, "undelivered_over_target": undeliv}

    # classify by the flag AND by the designated test-sender hashes, so rows written before TEST_SENDERS existed are not read as
    # real participants (2026-11-13: an old tester row made `real_participants` show one delivery with a 21-hour latency).
    real = [i for i in items if not _is_test_item(i, test_hashes)]
    return {"window_hours": window_s / 3600.0, "target_s": target_s,
            "real_participants": one(real), "including_test_senders": one(list(items)),
            "_note": ("question-to-delivery; the question time is the row timestamp, the delivery time is when WhatsApp accepted "
                      "the send (receipt lag is separate). An over-target answer is `review_wait` if the human wait was longer "
                      "than the model's own time, else `gpu_or_model`.")}


def notification_text(item, link, reviewer_name=None, renotify=False, autosend_note_text=None):
    """The WhatsApp push a reviewer receives the moment a draft is ready.

    ⚠️ THE DRAFT IS INCLUDED IN FULL AND THE EVIDENCE IS SUMMARISED, NOT OMITTED. A
    notification that only says "a draft is waiting" makes the reviewer open a page before
    they know whether they can act now — which on a bad connection means they do not, and
    the draft waits for the next person. Median reply is 197 characters, so the whole thing
    fits in a WhatsApp message comfortably.

    The ENGINE WORKING is quoted because it is the one part a reviewer can check arithmetic
    against. The FACTS SERVED are quoted too, truncated and capped — a reviewer who can only
    see a count is being asked to approve the draft without seeing what it was grounded in,
    which is the rubber-stamping the R7 condition exists to prevent. The link carries them
    in full.

    ONE LINK, NOT THREE. Approve / edit / withhold are buttons on the page the link opens,
    and each is a POST. Three separate GET links would each be fetched by WhatsApp's own link
    preview the moment the message is delivered, so an "approve" link would fire before any
    human saw it.
    """
    if item.get("fallback"):
        return _model_failure_text(item, link, reviewer_name, renotify)
    head = ("🔁 KUPITIA TENA (bado hakuna aliyeshughulikia)" if renotify
            else "📋 RASIMU MPYA — inahitaji kupitiwa")
    who = f" · {reviewer_name}" if reviewer_name else ""
    lines = [f"{head}{who}"]
    dups = item.get("duplicates_pending") or []
    if dups:
        lines += [DUPLICATE_WARNING_SW.format(n=len(dups)), DUPLICATE_WARNING_EN.format(n=len(dups)), ""]
    if autosend_note_text:
        lines += [autosend_note_text[0], autosend_note_text[1], ""]
    if evidence_is_loud(item):
        # FIRST, before the question: a reviewer reading on a phone must meet this before the draft.
        lines += [EVIDENCE_WARNING_SW, EVIDENCE_WARNING_EN]
        if evidence_state(item) == "path_missing":
            lines.append(EVIDENCE_PATH_MISSING)
        lines.append("")
    lines += [f"Mteja: ...{item.get('sender_tail') or '????'}",
              "",
              f"SWALI: {item.get('question') or '(hakuna)'}",
             "",
             f"RASIMU: {item.get('draft') or '(hakuna)'}"]
    if item.get("engine_working"):
        lines += ["", f"HESABU YA MFUMO: {item['engine_working']}"]
    else:
        lines += ["", "HESABU YA MFUMO: hakuna — jibu hili limetoka kwa modeli na "
                      "kumbukumbu pekee, hivyo hakuna hesabu ya kuthibitisha."]
    facts = [str(f) for f in (item.get("facts") or [])]
    lines += [f"VIGEZO VILIVYOTUMIKA ({len(facts)}):"]
    for f in facts[:_PUSH_FACTS_MAX]:
        lines.append("• " + (f if len(f) <= _PUSH_FACT_CHARS else f[:_PUSH_FACT_CHARS] + "…"))
    if len(facts) > _PUSH_FACTS_MAX:
        lines.append(f"• …na {len(facts) - _PUSH_FACTS_MAX} zaidi kwenye kiungo")
    if item.get("fallback"):
        lines += ["⚠️ FALLBACK — modeli haikujibu."]
    if item.get("error_class"):
        lines += [f"⚠️ {item['error_class']}"]
    lines += ["", "Fungua ili kuthibitisha, kuhariri au kuzuia:", link,
              "", "Hakuna jibu linalotumwa mpaka mtu abonyeze. Likikaa bila kushughulikiwa, "
                  "nitakumbusha tena."]
    return "\n".join(lines)


def _model_failure_text(item, link, reviewer_name=None, renotify=False):
    """THE MODEL FAILED, so there is no draft answer and this must not look like one. The old
    push put the apology under a 'RASIMU MPYA' header, so approving it read as approving
    Chike's answer when it sent the participant an apology instead of one."""
    head = ("🔁 KUPITIA TENA — MODELI IMESHINDWA" if renotify else "⛔ MODELI IMESHINDWA")
    who = f" · {reviewer_name}" if reviewer_name else ""
    lines = [f"{head}{who}",
             f"Mteja: ...{item.get('sender_tail') or '????'}",
             "",
             f"SWALI: {item.get('question') or '(hakuna)'}",
             "",
             f"HAKUNA RASIMU YA JIBU. Modeli haikujibu ({item.get('error_class') or 'hitilafu'}).",
             "",
             "Chagua kwenye kiungo:",
             "1) JARIBU TENA — swali linaulizwa tena, rasimu mpya inakuja kwako",
             "2) ANDIKA MWENYEWE — unaandika jibu, linatumwa baada ya kubonyeza",
             "3) TUMA SAMAHANI — mteja anapata: " + (item.get("draft") or "")[:70] + "…",
             "4) ZUIA — hakuna kinachotumwa",
             "", link,
             "", "Hakuna kinachotumwa mpaka mtu abonyeze."]
    return "\n".join(lines)


_REVIEWER_FIELDS = ("claimed_by", "decided_by", "released_from")


def reviewer_handle(signing_key, number):
    """What the ADMIN view shows for a reviewer: the same 10-hex handle their link carries, or -- if no
    signing key is configured -- an obviously-masked tail. NEVER the number: the admin JSON is pasted
    into tickets and chats, and a reviewer's phone number is not ours to publish."""
    if not number:
        return number
    if signing_key:
        return reviewer_id(signing_key, number)
    return "..." + number_tail(number)


def public_review_items(items, signing_key=None):
    """`items` safe to show an admin: reviewer numbers -> handles, participant `sender` removed.
    Applied to a COPY -- the stored queue is untouched."""
    out = []
    for i in items:
        j = {k: v for k, v in i.items() if k != "sender"}
        for f in _REVIEWER_FIELDS:
            if j.get(f):
                j[f] = reviewer_handle(signing_key, j[f])
        out.append(j)
    return out


def per_reviewer(items, signing_key=None):
    """Each reviewer's decisions, separately.

    Keyed by HANDLE (`reviewer_handle`), not by the reviewer's JID.

    ⛔ THE POINT OF A ROSTER'S AUDIT TRAIL. Aggregate numbers hide the one thing worth
    watching: a reviewer whose edit rate is far BELOW the others is not necessarily faster,
    they may be approving what the others would have caught. That cannot be seen in a pooled
    rate, and it is invisible without per-decision attribution — which is why `decided_by`
    is required rather than optional.
    """
    out = {}
    for i in items:
        who = i.get("decided_by")
        if not who or i.get("status") not in ("sent", "edited", "withheld"):
            continue
        who = reviewer_handle(signing_key, who)
        row = out.setdefault(who, {"name": i.get("decided_by_name"), "sent": 0, "edited": 0,
                                   "withheld": 0, "latencies": []})
        row[i["status"]] += 1
        if isinstance(i.get("decision_latency_s"), int):
            row["latencies"].append(i["decision_latency_s"])
    for who, row in out.items():
        n = row["sent"] + row["edited"] + row["withheld"]
        row["decided"] = n
        row["edit_or_withhold_rate"] = (
            None if not n else round((row["edited"] + row["withheld"]) / n, 3))
        lat = sorted(row.pop("latencies"))
        row["median_decision_latency_s"] = (None if not lat else lat[len(lat) // 2])
    return out


# How many participants ONE reviewer can supervise without review turning into skimming. Source:
# SUPERVISED_PILOT_RUNBOOK.md section 0 / eval/results/review_throughput_estimate_2026_10_10.json --
# "3 x 2 questions/day ~ 6 min/day to clear" is the row that fits "a few minutes a day" for one reviewer;
# 5 x 2 is ~10 and 10 x 2 is ~21. A planning figure, not a limit: /health MONITORS against it.
PARTICIPANTS_PER_REVIEWER = 3


def cohort_capacity(declared_size, reviewers):
    """What the declared cohort size implies about the roster. Pure, so /health and tests share it."""
    import math
    need = math.ceil(declared_size / PARTICIPANTS_PER_REVIEWER) if declared_size else 0
    capacity = reviewers * PARTICIPANTS_PER_REVIEWER
    return {
        "roster_reviewers": reviewers,
        "participants_per_reviewer": PARTICIPANTS_PER_REVIEWER,
        "sized_for_reviewers": need,
        # What THIS ROSTER can review properly, beside the declared ceiling -- the gap between the two is
        # the number the founder asked to keep visible (cap 15, one reviewer -> 3).
        "review_capacity_participants": capacity,
        "within_review_capacity": (None if not declared_size else need <= reviewers),
        "capacity_note": (
            None if not declared_size else
            (f"cohort of {declared_size} is sized for {need} reviewer(s); the roster has {reviewers}. "
             "Growing the cohort needs more reviewers on the roster FIRST (review depth is never the lever)."
             if need <= reviewers else
             f"the declared CEILING of {declared_size} is OVER what {reviewers} reviewer(s) can review "
             f"properly ({capacity} participants): invite only as many people as the roster can review, "
             f"and add reviewers before growing. Reviewing more than that starts to skim, which voids the "
             f"R7 reading.")),
    }


# ── THE PARTICIPANT DISCLOSURE: sent ONCE, AUTOMATICALLY, BEFORE THE ACK (founder, 2026-11-12) ───────
#
# "A disclosure that depends on me remembering will eventually be skipped, and dropping it voids the R7
# reading." So it is not a runbook step; it is code, and it is VERBATIM the founder's text (the runbook's
# §8a copy is asserted equal to this constant in tests, so the two cannot drift apart).
DISCLOSURE_TEXT = (
    "Karibu kwenye majaribio ya Chike. Chike ni msaidizi wa maswali ya kodi na sheria za biashara Tanzania. Kwa sasa ni jaribio linalosimamiwa: kila jibu linasomwa na mtu kabla ya kutumwa kwako, hivyo jibu linaweza kuchukua muda — wakati mwingine saa kadhaa. Majibu ni mwongozo, si ushauri rasmi wa kisheria; kwa maamuzi muhimu, thibitisha na TRA au mamlaka husika. Usitume taarifa binafsi zisizo za lazima. Asante kwa kutusaidia kuiboresha Chike.")

# States in which the participant HAS been told (or the message is on its way and must never be repeated).
DISCLOSURE_OK = ("delivered", "pending_receipt", "already")
_DISCLOSURE_WAIT_S = 30.0          # a second message racing the first waits for the first send to settle
_DISCLOSURE_STALE_S = 60.0         # a claim older than this is a crash, not a send in flight
_DISCLOSURE_POLL_S = 1.0


def parse_disclosure_flag(value) -> bool:
    """ON unless explicitly switched off. "ture" stays ON: a typo must not silently drop the disclosure."""
    return str(value or "").strip().lower() not in ("0", "false", "no", "off")


async def ensure_disclosure(sender, send_once, claim, peek, finish, release, settings, build="dev",
                            alias=None):
    """Send the disclosure to `sender` if -- and only if -- nobody has yet. Returns the row fields.

    NEVER TWICE: `claim(key, record)` is an ATOMIC put-if-absent (modal.Dict.put(skip_if_exists=True)),
    taken BEFORE the send, so two messages arriving together cannot both send. The loser waits (bounded)
    for the winner's send to settle, so its own ack cannot overtake the disclosure.
      * delivered / pending_receipt -> recorded, and never sent again. PENDING_RECEIPT is "accepted, not
        yet receipted" -- resending a message that may be on its way is how a duplicate is made.
      * a CLEAN failure (nothing reached them) -> the claim is RELEASED so the participant's next message
        retries; the reply to THIS message still goes to review (every reply is human-read), and the
        row says `failed` so the reviewer sees the disclosure did not land.
      * the store cannot be read -> `unknown`, and NOTHING is sent: a missing disclosure is flagged, a
        duplicate one is not undoable.
    Keyed by sender hash (no raw number is stored), and by the PHONE whenever the payload carries one:
    parse_webhook already swaps a linked-ID sender for its `senderPn` phone JID, so the primary key IS the
    phone. `alias` is the linked-ID that phone arrived as; it is recorded beside the phone key and checked
    first, so one person who reaches us as @lid and as a phone is told ONCE, in either order."""
    import asyncio
    key, _tail = sender_ids(sender, settings.sender_salt)
    alias_key = sender_ids(alias, settings.sender_salt)[0] if alias else None
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if alias_key and alias_key != key:
        try:
            prior = peek(alias_key)
        except Exception:                                            # noqa: BLE001
            prior = None
        if prior and prior.get("state") in ("delivered", "pending_receipt", "sending", "alias"):
            try:
                claim(key, {"state": "alias", "ts": prior.get("ts") or ts, "via": "lid", "build": build})
            except Exception:                                        # noqa: BLE001
                pass
            return {"disclosure_state": "already", "disclosure_ts": prior.get("ts")}
    try:
        claimed = claim(key, {"state": "sending", "ts": ts, "build": build})
    except Exception as e:                                           # noqa: BLE001
        return {"disclosure_state": "unknown", "disclosure_detail": f"store: {type(e).__name__}"}
    if not claimed:
        waited = 0.0
        while waited < _DISCLOSURE_WAIT_S:
            try:
                rec = peek(key) or {}
            except Exception:                                        # noqa: BLE001
                break
            if rec.get("state") != "sending":
                break
            # Only a FRESH claim is worth waiting for. A 'sending' record older than a minute is a crash
            # (or a failed record write) -- waiting 30 s on it would delay EVERY later message from this
            # participant for a send that will never settle. It is not resent (never twice); it is
            # counted in /health as `stuck_sending`.
            try:
                age = (datetime.now(timezone.utc) - datetime.fromisoformat(rec["ts"])).total_seconds()
            except Exception:                                        # noqa: BLE001
                age = 1e9
            if age > _DISCLOSURE_STALE_S:
                break
            await asyncio.sleep(_DISCLOSURE_POLL_S)
            waited += _DISCLOSURE_POLL_S
        try:
            ts_prev = (peek(key) or {}).get("ts")
        except Exception:                                            # noqa: BLE001
            ts_prev = None
        return {"disclosure_state": "already", "disclosure_ts": ts_prev}
    try:
        ok, detail = await send_with_retry(send_once, sender, DISCLOSURE_TEXT, settings)
    except Exception as e:                                           # noqa: BLE001
        ok, detail = False, f"{type(e).__name__}: {e}"
    if ok or is_pending_receipt(detail):
        state = "delivered" if ok else "pending_receipt"
        try:
            finish(key, {"state": state, "ts": ts, "build": build,
                         "message_id": None if ok else pending_message_id({"send_error": detail})})
        except Exception:                                            # noqa: BLE001
            pass                                  # it WAS sent; losing the record must not trigger a resend
        if alias_key and alias_key != key:
            try:                                  # so a later message under the linked-ID alone is covered
                finish(alias_key, {"state": "alias", "ts": ts, "via": "phone", "build": build})
            except Exception:                                        # noqa: BLE001
                pass
        return {"disclosure_state": state, "disclosure_ts": ts}
    try:
        release(key)
    except Exception:                                                # noqa: BLE001
        pass
    return {"disclosure_state": "failed", "disclosure_ts": ts,
            "disclosure_detail": scrub(str(detail), settings.secrets)[:160]}


def is_seeded_test(item) -> bool:
    """A `TEST-` review id is a labelled live-verification seed (mint_review_link serves ONLY
    these). 15 of them sit in the production queue from 2026-10-11 and, uncounted-for, they made
    the pilot's edit rate 9/15 before a single participant had been served. They are kept as
    evidence that the review flow was verified live -- and excluded from every statistic."""
    return str(item.get("review_id") or "").startswith("TEST-")


def _is_test_item(item, test_hashes=()):
    return bool(is_seeded_test(item) or item.get("test_sender")
                or (item.get("sender_hash") and item.get("sender_hash") in (test_hashes or ())))


def review_summary(items, signing_key=None, test_hashes=()):
    """The throughput and quality numbers the pilot exists to produce.

    ⚠️ SEEDED `TEST-` ITEMS ARE EXCLUDED (and counted in `excluded_test_items`, so the exclusion
    is visible rather than silent -- an exclusion that cannot be seen is R39's shrinking count).

    ⚠️ IT REFUSES TO REPORT AN EDIT RATE UNTIL AT LEAST ONE DECISION EXISTS, rather than
    returning 0.0 — a zero edit rate on an empty queue is indistinguishable from a perfect
    model, and that is the direction this project keeps getting wrong (R39).
    """
    excluded = sum(1 for i in items if _is_test_item(i, test_hashes))
    items = [i for i in items if not _is_test_item(i, test_hashes)]
    decided = [i for i in items if i.get("status") in ("sent", "edited", "withheld")]
    counts = {a: sum(1 for i in decided if i["status"] == a)
              for a in ("sent", "edited", "withheld")}
    lat = [i["decision_latency_s"] for i in decided
           if isinstance(i.get("decision_latency_s"), int)]
    return {
        "excluded_test_items": excluded,
        "pending": sum(1 for i in items if i.get("status") == "pending"),
        "decided": len(decided),
        "counts": counts,
        "auto_sent": sum(1 for i in items if i.get("status") == "auto_sent"),   # no human decision: NOT in the rate below
        "edit_or_withhold_rate": (
            None if not decided
            else round((counts["edited"] + counts["withheld"]) / len(decided), 3)),
        "median_decision_latency_s": (None if not lat else sorted(lat)[len(lat) // 2]),
        "claimed_now": sum(1 for i in items
                           if i.get("status") == "pending" and i.get("claimed_by")),
        "per_reviewer": per_reviewer(items, signing_key),
        "_why_no_rate_on_an_empty_queue": (
            "a 0.0 edit rate with nothing decided reads exactly like a perfect model; None "
            "cannot be mistaken for one"),
    }


async def deliver_greeting(sender, send_once, settings, build="dev"):
    """Same guarantee as deliver(), for the welcome path."""
    t0 = time.monotonic()
    row = _blank_row("greeting", sender, settings, build)
    row["reply"] = "WELCOME"
    row["reply_chars"] = len(WELCOME)
    try:
        ok, send_error = await send_with_retry(send_once, sender, WELCOME, settings)
        row["send_ok"], row["send_error"] = ok, send_error
        row["send_state"] = send_state(ok, send_error)
    except Exception as e:                                           # noqa: BLE001
        row["send_ok"] = False
        row["error_class"] = "handler_bug"
        row["error_detail"] = scrub(f"{type(e).__name__}: {e}", settings.secrets)
    finally:
        row["total_latency_ms"] = int((time.monotonic() - t0) * 1000)
    return row


async def deliver_pending_notice(sender, send_once, settings, build="dev"):
    """Same guarantee as deliver_greeting(), for a greeting that arrives while a question is pending."""
    t0 = time.monotonic()
    row = _blank_row("greeting_pending", sender, settings, build)
    row["reply"] = "PENDING_NOTICE"
    row["reply_chars"] = len(PENDING_NOTICE)
    try:
        ok, send_error = await send_with_retry(send_once, sender, PENDING_NOTICE, settings)
        row["send_ok"], row["send_error"] = ok, send_error
        row["send_state"] = send_state(ok, send_error)
    except Exception as e:                                           # noqa: BLE001
        row["send_ok"] = False
        row["error_class"] = "handler_bug"
        row["error_detail"] = scrub(f"{type(e).__name__}: {e}", settings.secrets)
    finally:
        row["total_latency_ms"] = int((time.monotonic() - t0) * 1000)
    return row


def payload_shape(body) -> dict:
    """The SHAPE of an inbound delivery — keys and which extraction candidates were
    present — never the values. Enough to settle "did parse_webhook reject this, and
    why", without putting message text or phone numbers in a rejection record."""
    if not isinstance(body, dict):
        return {"type": type(body).__name__}
    # `data` is not guaranteed to be an object. A malformed delivery must produce a
    # RECORD, not an exception -- an exception here would be caught by the webhook's
    # outer handler and lose the very row this function exists to write.
    data = body.get("data")
    messages = data.get("messages") if isinstance(data, dict) else None
    shape = {
        "top_keys": sorted(body)[:12],
        "event": body.get("event"),
        "data_keys": sorted(data)[:12] if isinstance(data, dict) else None,
        "messages_keys": sorted(messages)[:20] if isinstance(messages, dict) else None,
    }
    if isinstance(messages, dict):
        shape["text_field_present"] = [k for k in ("conversation", "messageBody", "text")
                                       if str(messages.get(k) or "").strip()]
        shape["jid_field_present"] = (
            [k for k in ("remoteJid",) if messages.get(k)]
            + (["key.remoteJid"] if (messages.get("key") or {}).get("remoteJid") else []))
        shape["from_me"] = bool(messages.get("fromMe")
                                or (messages.get("key") or {}).get("fromMe"))
    return shape


def rejection_row(reason: str, body, settings, build="dev") -> dict:
    """A delivery the webhook REFUSED, recorded rather than inferred.

    Both refusal branches used to return 200 and print nothing, so a rejected
    delivery was invisible — indistinguishable from a message that never arrived, and
    detectable only by noticing which log lines were ABSENT. That is the same
    silent-drop class the rest of this module exists to abolish, surviving in the one
    function `deliver()`'s guarantee does not cover.
    """
    return {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "build": build,
        "kind": "rejected",
        "reject_reason": reason,          # 'unauthorized' | 'ignored'
        "payload_shape": payload_shape(body),
        "sender_hash": None,
        "sender_tail": None,
        "sender_domain": None,
        "question": None,
        "reply": None,
        "fallback": False,
        "error_class": reason,
        "error_detail": None,
        "send_ok": None,
    }


def row_to_line(row) -> str:
    return json.dumps(row, ensure_ascii=False)


def transcript_filename(row, unique=None) -> str:
    """`<month>/<ts>-<sender_hash>-<unique>.json` — ONE FILE PER ROW.

    Never append to a shared file on a Modal Volume: two containers appending do not
    interleave, the last committer's version wins, and the other user's row is gone.
    The `unique` suffix exists because two rows from the same sender can share a
    second, and a filename collision is a silently lost row — the same failure in
    miniature that this whole module is built to prevent.
    """
    import uuid
    month = str(row.get("ts", ""))[:7] or "unknown"
    stamp = str(row.get("ts", "")).replace(":", "")
    suffix = unique or uuid.uuid4().hex[:6]
    return f"{month}/{stamp}-{row.get('sender_hash', 'anon')}-{suffix}.json"
