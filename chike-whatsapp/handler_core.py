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
import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

GREETINGS = {
    "habari", "hujambo", "mambo", "hello", "hi", "hey",
    "salaam", "salam", "start", "help", "msaada",
    "chike", "karibu",
}

WELCOME = (
    "Habari! Karibu sana. 🙏\n\n"
    "Mimi ni *Chike* — mshauri wako wa biashara\n"
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
    "I am *Chike* — your business adviser\n"
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


@dataclass
class Settings:
    """Injected rather than read from module globals, so a test states the timing it
    is exercising instead of monkeypatching a constant and hoping nothing leaks."""

    # 240s, up from Railway's 180s. Cold starts measured at 64s (2026-08-11), 92.5s
    # (2026-08-06) and up to 216s (runbook); chike-inference's own function timeout is
    # 600s, so nothing upstream cuts us off. Costs nothing: on a cold path the user
    # waits longer instead of receiving nothing, and WhatsApp is asynchronous.
    model_timeout_s: float = 240.0

    # One short "I'm working on it" if the answer is slow. A user who hears nothing for
    # three minutes concludes the service is broken; one Wappfly message is far cheaper
    # than keeping a GPU warm. 0 disables.
    slow_ack_after_s: float = 12.0

    # A PROXY, not a measurement — neither Modal's response nor its Python API tells the
    # handler whether the container was cold. Warm p90 was 9.8s over 48 questions
    # (2026-08-11); cold starts 64s+. The transcript field keeps the word `suspected`.
    cold_start_suspected_s: float = 30.0

    send_attempts: int = 2
    send_retry_delay_s: float = 2.0

    sender_salt: str = ""
    # Values scrubbed out of every log line and transcript field.
    secrets: tuple = field(default_factory=tuple)


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


def sender_ids(sender: str, salt: str = ""):
    """Pseudonymous, stable, and still correlatable to a known pilot user.

    A transcript file that is a raw dump of phone numbers is a liability; one that
    cannot be tied back to the user who reported a bad answer is useless. The hash
    groups a conversation; the last four digits identify a tester you already know.
    """
    digits = "".join(c for c in str(sender).split("@")[0] if c.isdigit())
    h = hashlib.sha256((salt + str(sender)).encode("utf-8")).hexdigest()[:12]
    return h, digits[-4:]


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
    return {"kind": kind, "sender": sender, "text": text}


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
        "send_ok": None,
        "send_error": None,
    }


async def deliver(sender, text, ask, send_once, settings, build="dev"):
    """Answer one question. MUST NOT RAISE.

    `ask` is an async callable taking the message and returning the model's dict.
    `send_once` is an async callable (to, text) -> (ok, detail).
    Returns the transcript row; the caller persists it.
    """
    t0 = time.monotonic()
    row = _blank_row("question", sender, settings, build)
    row["question"] = text
    try:
        answered = asyncio.Event()
        state = {"ack_sent": False}

        async def slow_ack():
            if settings.slow_ack_after_s <= 0:
                return
            try:
                await asyncio.wait_for(answered.wait(),
                                       timeout=settings.slow_ack_after_s)
                return                     # the answer beat the ack — stay quiet
            except asyncio.TimeoutError:
                pass
            state["ack_sent"] = True
            await send_with_retry(send_once, sender, SLOW_ACK, settings)

        ack_task = asyncio.create_task(slow_ack())
        m0 = time.monotonic()
        reply = error_class = detail = None
        result = None
        try:
            result = await asyncio.wait_for(ask(text),
                                            timeout=settings.model_timeout_s)
        except asyncio.TimeoutError:
            error_class = "timeout"
            detail = f"no reply after {settings.model_timeout_s}s"
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
        row["ack_sent"] = state["ack_sent"]
        row["error_class"] = error_class
        row["error_detail"] = detail

        if reply is None:
            row["fallback"] = True
            reply = FALLBACK
            print(f"[chike] FALLBACK to {row['sender_hash']} — {error_class}: {detail}")

        row["reply"] = reply
        row["reply_chars"] = len(reply)
        ok, send_error = await send_with_retry(send_once, sender, reply, settings)
        row["send_ok"] = ok
        row["send_error"] = send_error

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


async def deliver_greeting(sender, send_once, settings, build="dev"):
    """Same guarantee as deliver(), for the welcome path."""
    t0 = time.monotonic()
    row = _blank_row("greeting", sender, settings, build)
    row["reply"] = "WELCOME"
    row["reply_chars"] = len(WELCOME)
    try:
        ok, send_error = await send_with_retry(send_once, sender, WELCOME, settings)
        row["send_ok"], row["send_error"] = ok, send_error
    except Exception as e:                                           # noqa: BLE001
        row["send_ok"] = False
        row["error_class"] = "handler_bug"
        row["error_detail"] = scrub(f"{type(e).__name__}: {e}", settings.secrets)
    finally:
        row["total_latency_ms"] = int((time.monotonic() - t0) * 1000)
    return row


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
