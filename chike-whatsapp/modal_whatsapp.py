"""Chike WhatsApp front door — a SEPARATE Modal app from chike-inference.

WHY A SEPARATE APP (this is not a style choice)
-----------------------------------------------
R16 REQUIRES `modal app stop chike-inference --yes` before a model redeploy, to kill
warm containers still serving old code. If the webhook lived inside that app, every
model deploy would take the WhatsApp front door down with it — and on 2026-08-10 that
window was ~2 minutes of DEAD PRODUCTION when the replacing deploy failed on a console
encoding error. Keeping the front door in its own app means a model redeploy cannot
take WhatsApp offline, and a handler redeploy cannot disturb the model. The two are
joined only by `modal.Cls.from_name`, which is a lazy lookup, not a shared lifecycle.

WHY `.spawn()` AND NOT `asyncio.create_task`
---------------------------------------------
Modal's autoscaler tracks IN-FLIGHT INPUTS. The moment the webhook function returns its
200 to Wappfly, that input is complete and the container is eligible to be frozen or
reclaimed — a background coroutine holding a 240s answer is INVISIBLE to the scheduler.
`create_task` would work most of the time, and "most of the time" is exactly the class
of silent failure this handler was rewritten to abolish.

`.spawn()` hands the job to Modal, which is then responsible for running it to
completion with its own timeout, surviving the webhook container's death entirely.
This is strictly stronger than the Railway design it replaces: the answer path is
DURABLE rather than best-effort.

WHY TRANSCRIPTS ARE A DICT AND NOT A VOLUME
--------------------------------------------
The Volume version LOST ROWS IN PRODUCTION (2026-08-14). File-per-row solved APPEND
clobbering — two containers appending to one JSONL do not interleave, and the last
committer wins — but it did NOT solve COMMIT clobbering. `volume.commit()` pushes a
container's whole filesystem view, so a container that mounted the volume BEFORE another
container's write can erase that write when it later commits. Two rejection rows were
written, committed, read back verbatim, and then vanished; only the stdout echo preserved
the diagnosis they carried.

`modal.Dict` is concurrency-safe by construction: a put is a put, with no snapshot to
clobber. This data is a key-value log, not a filesystem, and modelling it as one was the
mistake — a Volume's whole-tree commit semantics are wrong for many small independent
writes from many short-lived containers.

The transcript store is a PILOT PREREQUISITE, not an improvement: Modal's Starter plan
retains logs for ONE DAY. Without a working store, yesterday's conversations are not
merely hard to query — they are deleted.

DEPLOY (R16b — the handler is now on Modal, so R16 applies to it in full):
    python -m modal app stop chike-whatsapp --yes
    PYTHONIOENCODING=utf-8 PYTHONUTF8=1 python -m modal deploy chike-whatsapp/modal_whatsapp.py
then GET /health and confirm `build`, then the live forced-failure check.
"""

import os

import modal

_HERE = os.path.dirname(os.path.abspath(__file__))

app = modal.App("chike-whatsapp")

# BUILD is baked at deploy time so /health can prove WHICH code is serving. Modal
# injects no git SHA (Railway did, via RAILWAY_GIT_COMMIT_SHA), so the deploy command
# passes it: CHIKE_BUILD=$(git rev-parse --short HEAD) modal deploy ...
BUILD = os.environ.get("CHIKE_BUILD", "") or "dev"

# ORDER MATTERS: every build step must precede `add_local_*`, or Modal refuses the
# image outright ("tried to run a build step after using image.add_local_*"). The
# first deploy failed exactly this way with .env() placed last.
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("fastapi[standard]", "httpx")
    .env({"CHIKE_BUILD": BUILD})
    .add_local_dir(_HERE, "/root/chike_whatsapp")
)

# TRANSCRIPTS LIVE IN A DICT, NOT A VOLUME — and the Volume version lost two rows before
# this was written (2026-08-14).
#
# File-per-row solved APPEND clobbering: two containers appending to one JSONL do not
# interleave, and the last committer wins. It did NOT solve COMMIT clobbering.
# `volume.commit()` pushes a container's whole filesystem view, so a container that
# mounted the volume BEFORE another container's write can erase that write when it later
# commits. With a 1200s webhook scaledown window and repeated deploys, that is the normal
# case rather than a rare race. Two rejection rows were written, committed, read back
# verbatim — and then vanished. Only the stdout echo preserved the diagnosis they carried.
#
# `modal.Dict` is concurrency-safe by construction: a put is a put, with no snapshot to
# clobber. This data is a key-value log, not a filesystem, and modelling it as one was the
# mistake. The old Volume rows remain readable via `modal volume get chike-transcripts`.
# NAME IT IN CAPS. A module-level `transcripts` was SHADOWED by the
# `transcripts` web function below, so every write went to a Function object,
# raised AttributeError, and was swallowed by _write_row's except -- a store
# that deployed cleanly and recorded nothing. Caught by a round-trip test, not
# by the deploy.
TRANSCRIPTS = modal.Dict.from_name("chike-transcripts-kv", create_if_missing=True)

# ⛔⛔ A SEPARATE STORE FROM TRANSCRIPTS, AND THE REASON IS PII, NOT TIDINESS.
#
# A transcript row carries a SALTED HASH plus a 4-digit tail and deliberately no reachable
# identifier — that is what makes the analysis corpus safe to read, export and quote. The
# review queue CANNOT work that way: sending an approved answer needs the real number. Keeping
# both in `chike-transcripts-kv` would quietly re-introduce reachable phone numbers into the
# corpus every analysis pass reads, and nothing would announce it.
#
# So: its own Dict, behind the same ADMIN_TOKEN gate, and `/review/purge` drops the `sender`
# from decided items so the number's lifetime is the decision's lifetime and not the pilot's.
REVIEW_QUEUE = modal.Dict.from_name("chike-review-queue-kv", create_if_missing=True)

# Lazy cross-app handle — resolved on first use, so a chike-inference redeploy does not
# require a chike-whatsapp redeploy.
ChikeModel = modal.Cls.from_name("chike-inference", "ChikeModel")

SECRET = modal.Secret.from_name("chike-whatsapp")

# The exact key names this app reads from that secret. /health reports which are
# PRESENT (never their values), so a misspelling is caught by name rather than
# diagnosed later from a failure that looks identical to a wrong value.
# REVIEWER_ROSTER and REVIEW_SIGNING_KEY joined on 2026-10-10. Both are credentials in the
# sense that matters: the roster decides WHO may approve a compliance answer, and the signing
# key is what makes an approval link unforgeable. Neither belongs in code.
EXPECTED_KEYS = ("WAPPFLY_TOKEN", "WEBHOOK_TOKEN", "ADMIN_TOKEN", "SENDER_SALT",
                 "REVIEWER_ROSTER", "REVIEW_SIGNING_KEY")

# The public base URL of this app, needed to build approval links that work inside WhatsApp.
# Modal does not tell a function its own URL, so the deploy passes it.
PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "").rstrip("/")

WAPPFLY_SEND_URL = os.environ.get("WAPPFLY_SEND_URL",
                                  "https://wappfly.com/api/messages/send")


def _settings():
    """Built inside the container, from the secret + env."""
    import sys
    sys.path.insert(0, "/root")
    from chike_whatsapp.handler_core import Settings

    return Settings(
        model_timeout_s=float(os.environ.get("MODEL_TIMEOUT_S", "240")),
        slow_ack_after_s=float(os.environ.get("SLOW_ACK_AFTER_S", "12")),
        second_ack_after_s=float(os.environ.get("SECOND_ACK_AFTER_S", "45")),
        cold_start_suspected_s=float(os.environ.get("COLD_START_SUSPECTED_S", "30")),
        send_attempts=int(os.environ.get("SEND_ATTEMPTS", "2")),
        sender_salt=os.environ.get("SENDER_SALT", ""),
        secrets=(os.environ.get("WAPPFLY_TOKEN", ""),
                 os.environ.get("WEBHOOK_TOKEN", ""),
                 os.environ.get("ADMIN_TOKEN", "")),
        # ⛔⛔ OFF BY DEFAULT, AND THE DANGEROUS DIRECTION IS THE ONE A DEFAULT CANNOT FIX.
        # A typo in SUPERVISED does not fail safe: it silently DISABLES supervision while
        # the reviewer believes every reply is being read, which is exactly the condition
        # the founder's R7 reading rests on. Defaulting to True is not the answer either —
        # that would hold every reply in the autonomous deployment and look like an outage.
        #
        # So the flag is not trusted on its own. Three things make the state checkable
        # instead of assumed, and they are the R16 pattern applied to a config-only change:
        #   1. STRICT PARSING — "1"/"true"/"yes" and nothing else; "ture" is False, loudly.
        #   2. /health REPORTS IT, so the deploy can be verified rather than hoped at.
        #   3. handler_core WITHHOLDS the answer if supervised is on and no hold_reply was
        #      wired, instead of falling through to a send.
        # The one remaining hole is a reviewer who never checks /health — which is why the
        # pilot runbook makes that the first step, not the last.
        supervised=os.environ.get("SUPERVISED", "").strip().lower() in ("1", "true", "yes"),
        # A SETTING, not a fixed number — 1, 10 or 30 are all legitimate, and the right one
        # is an operational judgement about review capacity that changes as the roster does.
        cohort_size=int(os.environ.get("COHORT_SIZE", "0") or 0),
        roster=parse_roster_env(),
        review_signing_key=os.environ.get("REVIEW_SIGNING_KEY", ""),
        claim_ttl_s=float(os.environ.get("CLAIM_TTL_S", "900")),
        renotify_after_s=float(os.environ.get("RENOTIFY_AFTER_S", "1800")),
    )


def parse_roster_env():
    """The roster, from the secret. Parsed by handler_core so the rule has one owner."""
    try:
        return _core().parse_roster(os.environ.get("REVIEWER_ROSTER", ""))
    except Exception as e:                                           # noqa: BLE001
        print(f"[roster] parse failed ({type(e).__name__}: {e}) — treating as EMPTY, which "
              f"means no links are issued and every draft HOLDS")
        return ()


def _core():
    import sys
    sys.path.insert(0, "/root")
    from chike_whatsapp import handler_core
    return handler_core


# ---------------------------------------------------------------------------
# transcripts — modal.Dict, one entry per row (see the module docstring)
# ---------------------------------------------------------------------------

def _write_row(row):
    """Never raises. Always reaches stdout, so a store failure degrades the record rather
    than losing it — though stdout itself is deleted after 1 day on Starter, which is why
    the store has to actually work."""
    core = _core()
    line = core.row_to_line(row)
    try:
        TRANSCRIPTS[core.transcript_filename(row)] = row
    except Exception as e:                                           # noqa: BLE001
        print(f"[transcript] WRITE FAILED ({type(e).__name__}: {e})")
    print("[transcript] " + line, flush=True)


# ---------------------------------------------------------------------------
# the spawned jobs — Modal owns these, they survive the webhook container
# ---------------------------------------------------------------------------

@app.function(image=image, secrets=[SECRET],
              timeout=900, retries=0)
async def answer_and_send(sender: str, text: str):
    """One question, end to end. timeout=900 leaves headroom over the 240s model wait
    plus the slow ack and two send attempts.

    retries=0 is deliberate: a retry would re-run the GPU call and could deliver the
    user a SECOND answer to the same question. Duplicate compliance answers are worse
    than one missing one, and the transcript records the failure either way.
    """
    core = _core()
    settings = _settings()

    async def ask(message):
        return await ChikeModel().run.remote.aio(message)

    # ⛔ THE ANSWER AND THE ACKS TRAVEL THROUGH DIFFERENT CALLABLES IN SUPERVISED MODE.
    # `_send_once` still carries the ack ladder — a user who asks at 9pm must not sit in
    # total silence until the reviewer wakes up, and in supervised mode the wait is
    # human-paced, so the acks matter MORE than in autonomous mode. The ANSWER goes to
    # `_hold_for_review`, which writes a draft and sends nothing.
    captured = {}

    async def ask_capturing(message):
        """The reviewer must be able to judge the draft rather than guess at it, so the
        engine's deterministic working and the facts retrieval actually served are captured
        here and stored beside it. Only wired in supervised mode — in autonomous mode this
        is pure overhead on the hot path."""
        result = await ask(message)
        if isinstance(result, dict):
            captured["working"] = (result.get("working")
                                   or result.get("computation_working"))
            facts = (result.get("facts") or result.get("retrieved_facts") or ())
            captured["facts"] = list(facts) if isinstance(facts, (list, tuple)) else []
        return result

    async def _hold_for_review(to, reply_text, row):
        item = core.review_item(row=row, sender=to, draft=reply_text,
                                engine_working=captured.get("working"),
                                facts=captured.get("facts", ()))
        try:
            REVIEW_QUEUE[item["review_id"]] = item
        except Exception as e:                                       # noqa: BLE001
            # ⚠️ A HOLD THAT CANNOT BE STORED MUST NOT REPORT SUCCESS. The answer would be
            # neither sent nor reviewable, and `send_ok: true` in the transcript would say
            # it reached the user. That is the instrument-lie shape this handler was
            # rewritten to abolish.
            return False, f"review store failed ({type(e).__name__}: {e})"
        print(f"[review] HELD {item['review_id']} from ...{item['sender_tail']} "
              f"({len(reply_text)} chars)", flush=True)
        # ⛔ PUSHED IMMEDIATELY, WHICH IS THE WHOLE POINT OF REAL-TIME REVIEW. The
        # queue-checking model made the reviewer the polling loop, and a reviewer who has to
        # remember to look IS the latency. Notifying inside the hold means the draft reaches
        # a phone within seconds of being ready.
        #
        # ⚠️ A FAILED NOTIFICATION DOES NOT FAIL THE HOLD. The draft is already stored, so
        # the sweeper will re-notify; returning False here would mark the answer as
        # undelivered when in fact it is safely pending. Two different failures, two
        # different records.
        try:
            sent = await _notify_reviewers(item)
            _mark_notified(item, sent)
        except Exception as e:                                       # noqa: BLE001
            print(f"[review] notify raised for {item['review_id']}: "
                  f"{type(e).__name__}: {e} — the draft HOLDS and will be re-notified")
        return True, None

    row = await core.deliver(
        sender, text, ask_capturing if settings.supervised else ask,
        _send_once, settings, BUILD,
        hold_reply=_hold_for_review if settings.supervised else None)
    _write_row(row)
    return {"fallback": row["fallback"], "error_class": row["error_class"],
            "supervision": row.get("supervision")}


@app.function(image=image, secrets=[SECRET],
              timeout=300, retries=0)
async def greet_and_send(sender: str):
    core = _core()
    row = await core.deliver_greeting(sender, _send_once, _settings(), BUILD)
    _write_row(row)
    return {"send_ok": row["send_ok"]}


async def _send_once(to: str, text: str):
    """(ok, detail). The retry policy lives in handler_core, where it is tested."""
    import httpx
    timeout = float(os.environ.get("WAPPFLY_TIMEOUT_S", "15"))
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(
                WAPPFLY_SEND_URL,
                headers={"X-API-Token": os.environ.get("WAPPFLY_TOKEN", ""),
                         "Content-Type": "application/json"},
                json={"to": to, "text": text},
            )
        if r.status_code < 400:
            return True, None
        return False, f"HTTP {r.status_code}: {r.text[:200]}"
    except Exception as e:                                           # noqa: BLE001
        return False, f"{type(e).__name__}: {e}"


# ---------------------------------------------------------------------------
# the front door
# ---------------------------------------------------------------------------

# min_containers=0 and a long scaledown: a CPU container is ~$0.10/mo used this way
# against ~$5.68/mo always-warm, and the GPU's own cold start dwarfs the webhook's.
# Buy warmth only if the transcripts show Wappfly retrying on slow delivery — the same
# discipline as holding the GPU scaledown at 300.
@app.function(image=image, secrets=[SECRET],
              min_containers=0, scaledown_window=1200)
@modal.fastapi_endpoint(method="POST")
def webhook(item: dict, token: str = None):
    """Always returns 200. Wappfly must never see an error it might redeliver — there
    is still no dedupe on redelivery, so a retry would mean a duplicate answer."""
    try:
        core = _core()
        expected = os.environ.get("WEBHOOK_TOKEN", "")
        if expected:
            if token != expected:
                # WAS SILENT. A rejected delivery returned 200 and printed nothing, so it
                # was detectable only by noticing which log lines were ABSENT — which is
                # how 2026-08-14's fourth failed send had to be diagnosed. Record it.
                #
                # THE RECEIVED-TOKEN FINGERPRINT is the point of this block. Both ends
                # hashed to 15d40b19 and the endpoint still rejected, so the value is
                # altered in transit — but nothing could SEE the arriving value, and
                # neither party may print it. Fingerprinting what arrived turns
                # "the tokens look the same but don't match" into a comparison.
                # It goes in the ROW, not only the log: Modal Starter deletes logs after
                # one day, and this is the evidence for a vendor conversation.
                row = core.rejection_row("unauthorized", item, _settings(), BUILD)
                row["supplied_token_fingerprint"] = _fp(token)
                row["supplied_token_len"] = len(token or "")
                row["expected_token_fingerprint"] = _fp(expected)
                row["expected_token_len"] = len(expected)
                print("[webhook] REJECTED: token mismatch "
                      f"(supplied={'yes' if token else 'none'} "
                      f"fp={row['supplied_token_fingerprint']} "
                      f"len={row['supplied_token_len']} vs "
                      f"expected fp={row['expected_token_fingerprint']} "
                      f"len={row['expected_token_len']})")
                _write_row(row)
                return {"status": "unauthorized"}
        else:
            # Opt-in hardening. Unset preserves the Railway behaviour (an open webhook)
            # so switching Wappfly over cannot lock the pilot out on day one — but an
            # open webhook lets anyone who guesses the URL burn GPU. Set it.
            print("[webhook] WARNING: WEBHOOK_TOKEN unset — this endpoint is OPEN")

        parsed = core.parse_webhook(item)
        if not parsed:
            # WAS SILENT for the same reason. The recorded payload_shape (keys only, never
            # values) says WHY the parse declined — wrong event, fromMe, missing text or
            # missing JID — which settles next time what took three log-reads this time.
            print("[webhook] IGNORED: parse_webhook declined the payload")
            _write_row(core.rejection_row("ignored", item, _settings(), BUILD))
            return {"status": "ignored"}

        print(f"[chike] From: {parsed['sender']} — {parsed['text'][:80]}")
        if parsed["kind"] == "greeting":
            greet_and_send.spawn(parsed["sender"])
        else:
            answer_and_send.spawn(parsed["sender"], parsed["text"])
        return {"status": "ok"}

    except Exception as e:                                           # noqa: BLE001
        print(f"[webhook] Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error"}


# ---------------------------------------------------------------------------
# SUPERVISED REVIEW — the queue the founder clears from a phone
# ---------------------------------------------------------------------------
# ⚠️ DESIGNED FOR ONE THUMB AND A BAD CONNECTION, because that is where it will be used. No
# framework, no external asset, no JS beyond one fetch — a review queue that needs a good
# connection is a review queue that gets skipped, and this one runs over the same Tanzanian
# link that has dropped three measurement runs this month.
#
# ⛔ AND IT SHOWS THE EVIDENCE, NOT JUST THE DRAFT. The engine's deterministic working and the
# facts retrieval served sit under the reply, because a reviewer shown only the Swahili prose
# is being asked to judge it against memory — which is exactly how two of my own adjudications
# went wrong this week by reading the gold instead of the served index.


def _admin_ok(token):
    expected = os.environ.get("ADMIN_TOKEN", "")
    return bool(expected) and token == expected


def _queue_items():
    out = []
    try:
        for k in REVIEW_QUEUE.keys():
            try:
                out.append(REVIEW_QUEUE[k])
            except Exception:                                        # noqa: BLE001
                continue
    except Exception as e:                                           # noqa: BLE001
        print(f"[review] queue read failed ({type(e).__name__}: {e})")
    return sorted(out, key=lambda i: i.get("ts_held") or "")


def _esc(x):
    return str(x or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _draft_link(settings, item, number):
    """The per-(draft, reviewer) link. No phone number in the URL — a reviewer handle."""
    core = _core()
    rid = core.reviewer_id(settings.review_signing_key, number)
    tok = core.review_token(settings.review_signing_key, item["review_id"], number)
    base = PUBLIC_BASE_URL or ""
    return (f"{base}/d?r={item['review_id']}&v={rid}&t={tok}")


async def _notify_reviewers(item, *, renotify=False):
    """Push one draft to every reviewer on the roster, each with their own link.

    ⛔⛔ IF THE ROSTER IS EMPTY OR THE SIGNING KEY IS MISSING, NOTHING IS SENT AND THE DRAFT
    HOLDS. It is never auto-approved, never auto-sent and never discarded — it stays pending
    and the sweeper keeps re-notifying. A misconfigured roster must cost a delay, never an
    unreviewed answer.

    ⚠️ IT NOTIFIES EVERY REVIEWER RATHER THAN ONE, AND THE CLAIM LOCK IS WHAT MAKES THAT
    SAFE. Round-robin would be cheaper on notifications and far worse in practice: a
    reviewer who is asleep, driving or out of signal silently becomes a queue of one. The
    lock means whoever opens first owns it, so capacity is whoever is actually awake.
    """
    core = _core()
    settings = _settings()
    if not settings.roster or not settings.review_signing_key:
        print(f"[review] NOT NOTIFIED {item['review_id']} — "
              f"roster={len(settings.roster)} signing_key="
              f"{bool(settings.review_signing_key)}. The draft HOLDS.", flush=True)
        return 0
    if not PUBLIC_BASE_URL:
        print(f"[review] NOT NOTIFIED {item['review_id']} — PUBLIC_BASE_URL is unset, so "
              f"any link would be relative and unusable inside WhatsApp. The draft HOLDS.",
              flush=True)
        return 0
    ok_count = 0
    for number, name in settings.roster:
        text = core.notification_text(
            item, _draft_link(settings, item, number), reviewer_name=name,
            renotify=renotify)
        ok, detail = await _send_once(number, text)
        if ok:
            ok_count += 1
        else:
            print(f"[review] notify FAILED to ...{number[-4:]} for "
                  f"{item['review_id']}: {detail}", flush=True)
    return ok_count


def _mark_notified(item, sent_count, *, renotify=False):
    from datetime import datetime, timezone
    item["last_notified_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    item["notify_count"] = int(item.get("notify_count") or 0) + 1
    item["last_notify_recipients"] = sent_count
    if renotify:
        item["renotify_count"] = int(item.get("renotify_count") or 0) + 1
    try:
        REVIEW_QUEUE[item["review_id"]] = item
    except Exception as e:                                           # noqa: BLE001
        print(f"[review] could not record notification for {item['review_id']}: {e}")


def _participants_seen():
    """Distinct participants in the transcript store — the number the cohort SETTING is
    monitored against. Reviewer notifications are not transcript rows, so they cannot
    inflate this."""
    try:
        seen = set()
        for k in TRANSCRIPTS.keys():
            try:
                row = TRANSCRIPTS[k]
            except Exception:                                        # noqa: BLE001
                continue
            if isinstance(row, dict) and row.get("kind") in ("question", "greeting"):
                if row.get("sender_hash"):
                    seen.add(row["sender_hash"])
        return len(seen)
    except Exception:                                                # noqa: BLE001
        return None


def _cohort_health():
    size = int(os.environ.get("COHORT_SIZE", "0") or 0)
    seen = _participants_seen()
    return {"declared_size": size, "participants_seen": seen,
            "over_capacity": (None if (seen is None or not size) else seen > size),
            "_note": "a MONITOR, not a gate — see the comment at the call site"}


def _roster_health():
    try:
        settings = _settings()
    except Exception as e:                                           # noqa: BLE001
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}
    core = _core()
    key = settings.review_signing_key
    return {
        "ok": True,
        "reviewers": len(settings.roster),
        # Handles, not numbers. Lets a reviewer confirm their own link belongs to them
        # without publishing anyone's phone number.
        "reviewer_ids": [core.reviewer_id(key, n) for n, _name in settings.roster] if key
                        else [],
        "names": [name for _n, name in settings.roster],
        "signing_key_set": bool(key),
        "claim_ttl_s": settings.claim_ttl_s,
        "renotify_after_s": settings.renotify_after_s,
        "public_base_url_set": bool(PUBLIC_BASE_URL),
        # ⛔ THE ONE LINE THAT SAYS WHETHER REVIEW CAN HAPPEN AT ALL. Any of these three
        # missing means no links are issued, which means drafts HOLD — safe, and silent
        # unless something reports it.
        "can_issue_links": bool(settings.roster and key and PUBLIC_BASE_URL),
    }


def _supervision_health():
    """{supervised, supervised_raw_env} — or supervised=None when it cannot be determined.

    Calls `_settings()` so the parse rule has ONE owner: a /health that re-parsed SUPERVISED
    itself could agree with itself while disagreeing with the handler, which is the dual-file
    divergence CLAUDE.md warns about arriving in the one endpoint built to detect it.
    """
    raw = os.environ.get("SUPERVISED", "")
    try:
        return {"supervised": _settings().supervised, "supervised_raw_env": raw}
    except Exception as e:                                           # noqa: BLE001
        return {"supervised": None, "supervised_raw_env": raw,
                "supervised_error": f"{type(e).__name__}: {e}"}


def _review_queue_health():
    """Queue depth for /health. A supervised pilot's one operational risk is a queue nobody
    is clearing, and a pending count that nothing reports is a queue nobody is watching."""
    try:
        items = _queue_items()
    except Exception as e:                                           # noqa: BLE001
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}
    pending = [i for i in items if i.get("status") == "pending"]
    oldest = min((i.get("ts_held") or "" for i in pending), default=None)
    return {"ok": True, "total": len(items), "pending": len(pending),
            "oldest_pending_ts": oldest}


@app.function(image=image, secrets=[SECRET])
@modal.fastapi_endpoint(method="GET")
def review(token: str = None):
    """The queue, as a phone-sized page. Disabled entirely when ADMIN_TOKEN is unset."""
    from fastapi.responses import HTMLResponse, JSONResponse
    if not _admin_ok(token):
        return JSONResponse({"status": "not found"}, status_code=404)
    core = _core()
    items = _queue_items()
    pending = [i for i in items if i.get("status") == "pending"]
    summary = core.review_summary(items)
    cards = []
    for it in pending:
        rid = _esc(it["review_id"])
        facts_html = "".join(
            "<li>" + _esc(f)[:400] + "</li>" for f in (it.get("facts") or []))
        working = it.get("engine_working")
        work_html = (
            "<div class=w><b>Engine working</b><br>" + _esc(working) + "</div>" if working
            else "<div class=w><i>no deterministic working &mdash; this answer came from "
                 "the model and the index alone, so it carries no arithmetic to check "
                 "against</i></div>")
        flags = ""
        if it.get("fallback"):
            flags += " &middot; <b>FALLBACK</b>"
        if it.get("error_class"):
            flags += " &middot; <b>" + _esc(it.get("error_class")) + "</b>"
        cards.append(
            "<div class=c>"
            "<div class=m>..." + _esc(it.get("sender_tail")) + " &middot; "
            + _esc(it.get("ts_held")) + " &middot; "
            + _esc(it.get("model_latency_ms")) + "ms" + flags + "</div>"
            "<div class=q>" + _esc(it.get("question")) + "</div>"
            '<textarea id="t-' + rid + '" rows=9>' + _esc(it.get("draft")) + "</textarea>"
            + work_html
            + ("<div class=f><b>Facts served</b><ul>" + facts_html + "</ul></div>"
               if facts_html else "")
            + ("<div class=o>claimed by " + _esc(it.get("claimed_by") and "a reviewer")
               + " until " + _esc(it.get("claim_expires_at")) + "</div>"
               if it.get("claimed_by") else "<div class=o>unclaimed</div>")
            + "<div class=o>notified " + str(it.get("notify_count") or 0) + "x</div>"
            "</div>")
    body = "".join(cards) or "<p class=z>Queue empty.</p>"
    head = (
        "<!doctype html><meta name=viewport "
        'content="width=device-width,initial-scale=1">'
        "<title>Chike review (" + str(len(pending)) + ")</title><style>"
        "body{font:16px/1.45 system-ui,sans-serif;margin:0;padding:10px;background:#111;"
        "color:#eee}"
        "h1{font-size:17px;margin:4px 0 8px}"
        ".c{background:#1c1c1e;border-radius:12px;padding:12px;margin:0 0 14px}"
        ".m{font-size:12px;color:#9a9a9f;margin-bottom:6px}"
        ".q{font-weight:600;margin-bottom:8px}"
        "textarea,input{width:100%;box-sizing:border-box;font:15px/1.4 inherit;"
        "background:#2a2a2d;color:#eee;border:1px solid #3a3a3d;border-radius:8px;"
        "padding:8px;margin-bottom:8px}"
        ".w,.f{font-size:13px;color:#b9b9be;background:#17171a;border-radius:8px;"
        "padding:8px;margin-bottom:8px;white-space:pre-wrap}"
        ".f ul{margin:4px 0 0 16px;padding:0}"
        ".b{display:flex;gap:8px}"
        "button{flex:1;padding:14px 0;font-size:15px;font-weight:600;border:0;"
        "border-radius:10px;color:#fff}"
        ".s{background:#1f7a3a}.e{background:#8a5a00}.x{background:#7a1f1f}"
        ".o{font-size:13px;margin-top:8px;color:#9ad}.z{color:#9a9a9f}"
        ".t{font-size:12px;color:#9a9a9f;margin-bottom:12px}"
        "</style>")
    stats = ("<h1>Chike review &mdash; " + str(len(pending)) + " pending</h1>"
             "<div class=t>decided " + str(summary["decided"])
             + " &middot; edit/withhold rate " + str(summary["edit_or_withhold_rate"])
             + " &middot; median decision "
             + str(summary["median_decision_latency_s"]) + "s</div>")
    # ⛔ READ-ONLY. There are no action buttons here any more, and that is the design:
    # `apply_decision` refuses an unattributed decision, so an ADMIN_TOKEN holder acting
    # from this page would either be impossible or would have to be given a fake reviewer
    # identity — and a fake identity in the attribution column is worse than no column.
    # Decisions happen on /d, from a reviewer's own signed link. This page is the overview:
    # what is waiting, who holds what, how often it has been notified.
    script = ("<div class=t>Read-only. Decisions are taken from a reviewer's own link "
              "(/d), so every decision carries a reviewer.</div>")
    return HTMLResponse(head + stats + body + script)


@app.function(image=image, secrets=[SECRET])
@modal.fastapi_endpoint(method="GET")
def d(r: str = None, v: str = None, t: str = None):
    """One draft, opened from a WhatsApp link. GET is READ-ONLY by design.

    ⛔⛔ NOTHING ON THIS PAGE ACTS ON A GET, AND THE REASON IS WHATSAPP'S OWN LINK PREVIEW.
    WhatsApp fetches the URL to render a preview card the moment the notification is
    delivered. A GET that claimed, sent or withheld would therefore fire before any human
    saw it — and "approve by tapping a link" is exactly the design that invites it. The
    claim is a POST issued by this page's JavaScript on load, and the three actions are
    POSTs from buttons; a preview crawler executes neither.
    """
    from fastapi.responses import HTMLResponse, JSONResponse
    core = _core()
    settings = _settings()
    who = core.authenticate_reviewer(settings, r, v, t)
    if not who:
        # Deliberately a 404 with no detail: a bad token and an unknown draft look the
        # same from outside, so the page cannot be used to enumerate either.
        return JSONResponse({"status": "not found"}, status_code=404)
    _number, name = who
    try:
        it = REVIEW_QUEUE[r]
    except Exception:                                                # noqa: BLE001
        return JSONResponse({"status": "not found"}, status_code=404)

    facts_html = "".join("<li>" + _esc(f)[:600] + "</li>" for f in (it.get("facts") or []))
    working = it.get("engine_working")
    work_html = ("<div class=w><b>Hesabu ya mfumo</b><br>" + _esc(working) + "</div>"
                 if working else
                 "<div class=w><i>Hakuna hesabu ya mfumo — jibu hili limetoka kwa modeli "
                 "na kumbukumbu pekee, hivyo hakuna hesabu ya kuthibitisha.</i></div>")
    decided = it.get("status") != "pending"
    banner = ""
    if decided:
        banner = ("<div class=dec><b>Imeshaamuliwa:</b> " + _esc(it.get("status"))
                  + " &middot; " + _esc(it.get("decided_by_name"))
                  + " &middot; " + _esc(it.get("decided_ts")) + "</div>")
    head = (
        "<!doctype html><meta name=viewport "
        'content="width=device-width,initial-scale=1">'
        "<title>Chike &mdash; rasimu</title><style>"
        "body{font:16px/1.45 system-ui,sans-serif;margin:0;padding:12px;background:#111;"
        "color:#eee}"
        ".m{font-size:12px;color:#9a9a9f;margin-bottom:6px}"
        ".q{font-weight:600;margin-bottom:10px}"
        "textarea,input{width:100%;box-sizing:border-box;font:15px/1.45 inherit;"
        "background:#2a2a2d;color:#eee;border:1px solid #3a3a3d;border-radius:8px;"
        "padding:9px;margin-bottom:10px}"
        ".w,.f{font-size:13px;color:#b9b9be;background:#17171a;border-radius:8px;"
        "padding:9px;margin-bottom:10px;white-space:pre-wrap}"
        ".f ul{margin:4px 0 0 16px;padding:0}"
        ".b{display:flex;gap:8px}"
        "button{flex:1;padding:16px 0;font-size:15px;font-weight:600;border:0;"
        "border-radius:10px;color:#fff}"
        "button:disabled{opacity:.45}"
        ".s{background:#1f7a3a}.e{background:#8a5a00}.x{background:#7a1f1f}"
        ".o{font-size:14px;margin-top:10px;color:#9ad;min-height:1.4em}"
        ".lock{font-size:13px;padding:9px;border-radius:8px;margin-bottom:10px;"
        "background:#2a2320;color:#e8c89a}"
        ".dec{font-size:13px;padding:9px;border-radius:8px;margin-bottom:10px;"
        "background:#20262a;color:#9ad}"
        "</style>")
    body = (
        "<div class=m>" + _esc(name) + " &middot; mteja ...“"
        + _esc(it.get("sender_tail")) + "” &middot; " + _esc(it.get("ts_held")) + "</div>"
        + banner
        + '<div class=lock id=lock>Inashikiliwa&hellip;</div>'
        "<div class=q>" + _esc(it.get("question")) + "</div>"
        '<textarea id=t rows=10 '
        + ("disabled" if decided else "") + ">" + _esc(it.get("draft")) + "</textarea>"
        + work_html
        + ("<div class=f><b>Vigezo vilivyotumika (" + str(len(it.get("facts") or []))
           + ")</b><ul>" + facts_html + "</ul></div>" if facts_html else "")
        + '<input id=reason placeholder="sababu (lazima kwa kuhariri au kuzuia)" '
        + ("disabled" if decided else "") + ">"
        "<div class=b>"
        '<button class=s id=bs onclick="act(\'send\')" disabled>Tuma</button>'
        '<button class=e id=be onclick="act(\'edit\')" disabled>Tuma iliyohaririwa</button>'
        '<button class=x id=bx onclick="act(\'withhold\')" disabled>Zuia</button>'
        "</div><div class=o id=o></div>")
    script = (
        "<script>"
        "var P=new URLSearchParams(location.search);"
        "var B={review_id:P.get('r'),v:P.get('v'),t:P.get('t')};"
        "function en(on){['bs','be','bx'].forEach(function(i){"
        "document.getElementById(i).disabled=!on;});}"
        # ⛔ THE CLAIM IS POSTED FROM JS ON LOAD. A link preview crawler never reaches here,
        # so WhatsApp's own prefetch cannot lock a draft to a reviewer who has not read it.
        "async function claim(){"
        "try{var r=await fetch('review_claim',{method:'POST',"
        "headers:{'Content-Type':'application/json'},body:JSON.stringify(B)});"
        "var j=await r.json();var L=document.getElementById('lock');"
        "if(j.outcome==='decided'){L.textContent='Imeshaamuliwa.';en(false);}"
        "else if(j.ok){L.textContent='Umeishikilia hadi '+(j.claim_expires_at||'')"
        "+' — wewe tu unaweza kuamua.';en(true);}"
        "else{L.textContent='Inashikiliwa na '+(j.held_by||'mtu mwingine')"
        "+' hadi '+(j.claim_expires_at||'')+'. Hauwezi kuamua sasa.';en(false);}"
        "}catch(e){document.getElementById('lock').textContent='Imeshindikana: '+e;}}"
        "async function act(a){var o=document.getElementById('o');"
        "o.textContent='inatuma...';en(false);"
        "var b=Object.assign({},B,{action:a,"
        "edited:document.getElementById('t').value,"
        "reason:document.getElementById('reason').value});"
        "try{var r=await fetch('review_act',{method:'POST',"
        "headers:{'Content-Type':'application/json'},body:JSON.stringify(b)});"
        "var j=await r.json();"
        "if(j.ok){o.textContent=j.status.toUpperCase()+(j.send_ok===false?"
        "' LAKINI KUTUMA KUMESHINDIKANA: '+(j.send_error||''):' — imekamilika');}"
        "else{o.textContent='HITILAFU: '+(j.detail||r.status);en(true);}"
        "}catch(e){o.textContent='HITILAFU: '+e;en(true);}}"
        + ("" if decided else "claim();")
        + "</script>")
    return HTMLResponse(head + body + script)


@app.function(image=image, secrets=[SECRET], timeout=60)
@modal.fastapi_endpoint(method="POST")
def review_claim(item: dict):
    """Lock one draft to the reviewer whose link this is.

    ⛔⛔ CLAIMING IS A **POST**, FIRED BY THE PAGE'S JAVASCRIPT ON LOAD — AND THAT IS NOT A
    STYLE CHOICE, IT IS THE DEFENCE AGAINST WHATSAPP ITSELF. WhatsApp fetches a link to
    render its preview card. A GET that claimed would therefore be triggered the instant the
    notification was DELIVERED, locking every draft to whichever reviewer's client previewed
    it first — someone who has not read a word of it — and the draft would then sit until the
    claim timed out. Crawlers do not execute JavaScript; a human opening the page does.

    This is the same hazard class as a side effect on import (R40): the action runs regardless
    of whether anyone asked for it, because something other than the user triggered the path.
    """
    from fastapi.responses import JSONResponse
    core = _core()
    settings = _settings()
    rid = (item or {}).get("review_id")
    who = core.authenticate_reviewer(settings, rid, (item or {}).get("v"),
                                     (item or {}).get("t"))
    if not who:
        return JSONResponse({"ok": False, "detail": "not found"}, status_code=404)
    number, name = who
    try:
        existing = REVIEW_QUEUE[rid]
    except Exception:                                                # noqa: BLE001
        return JSONResponse({"ok": False, "detail": "unknown draft"}, status_code=404)
    # Release first, so a stale claim does not block a reviewer who is here now.
    existing, released = core.release_expired_claim(existing)
    updated, outcome = core.claim(existing, number, ttl_s=settings.claim_ttl_s)
    if outcome in ("claimed", "already_yours") or released:
        try:
            REVIEW_QUEUE[rid] = updated
        except Exception as e:                                       # noqa: BLE001
            return JSONResponse({"ok": False, "detail": f"store failed: {e}"},
                                status_code=500)
    holder_name = None
    if outcome == "held_by_other":
        holder = updated.get("claimed_by")
        holder_name = next((n for num, n in settings.roster if num == holder), "mtu mwingine")
    print(f"[review] CLAIM {outcome} {rid} by ...{number[-4:]} ({name})"
          f"{' (released a stale claim)' if released else ''}", flush=True)
    return {"ok": outcome in ("claimed", "already_yours"), "outcome": outcome,
            "reviewer": name, "held_by": holder_name,
            "claim_expires_at": updated.get("claim_expires_at"),
            "status": updated.get("status")}


@app.function(image=image, secrets=[SECRET], timeout=120)
@modal.fastapi_endpoint(method="POST")
async def review_act(item: dict):
    """Take one decision. The rules live in handler_core.apply_decision — pure, and tested
    without Modal — so this function only does I/O.

    ⛔ AUTHENTICATED BY THE REVIEWER'S OWN LINK TOKEN, NOT BY ADMIN_TOKEN. There is no longer
    any way to decide without being a named reviewer on the roster: `apply_decision` refuses
    an unattributed decision outright, because a roster whose weakest reviewer is invisible
    is not an auditable roster. The admin page is read-only for the same reason.

    ⛔ THE REASON AND THE CLAIM ARE BOTH ENFORCED IN apply_decision, NOT HERE. A check in the
    HTTP layer is bypassed by the first curl and leaves the pure function usable without it
    by the next caller — and the next caller is a sweeper or a backfill script."""
    from fastapi.responses import JSONResponse
    core = _core()
    settings = _settings()
    rid = (item or {}).get("review_id")
    who = core.authenticate_reviewer(settings, rid, (item or {}).get("v"),
                                     (item or {}).get("t"))
    if not who:
        return JSONResponse({"ok": False, "detail": "not found"}, status_code=404)
    number, name = who
    try:
        existing = REVIEW_QUEUE[rid]
    except Exception:                                                # noqa: BLE001
        return JSONResponse({"ok": False, "detail": f"unknown review_id {rid!r}"},
                            status_code=404)
    existing, _released = core.release_expired_claim(existing)
    try:
        updated, to_send = core.apply_decision(
            existing, (item or {}).get("action"), reviewer=number, reviewer_name=name,
            edited=(item or {}).get("edited"), reason=(item or {}).get("reason"))
    except ValueError as e:
        return JSONResponse({"ok": False, "detail": str(e)}, status_code=409)

    # ⚠️ STORE THE DECISION BEFORE SENDING. A stored decision with send_ok=false is
    # recoverable; a successful send with no stored decision is a message the user has and
    # the record does not — and the same answer can then be sent twice, which this app's own
    # `retries=0` comment already names as worse than one missing answer.
    send_ok, send_error = None, None
    try:
        REVIEW_QUEUE[rid] = updated
    except Exception as e:                                           # noqa: BLE001
        return JSONResponse({"ok": False, "detail": f"store failed: {e}"}, status_code=500)
    if to_send:
        send_ok, send_error = await _send_once(existing["sender"], to_send)
        updated["send_ok"], updated["send_error"] = send_ok, send_error
        try:
            REVIEW_QUEUE[rid] = updated
        except Exception as e:                                       # noqa: BLE001
            print(f"[review] send result recorded only in logs ({e})")

    # The decided item also lands in the TRANSCRIPT store, so the analysis corpus holds
    # draft / final / edit_reason as three separate fields without a manual export.
    _write_row({
        "ts": updated["decided_ts"], "build": updated.get("build"), "kind": "review",
        "sender_hash": updated["sender_hash"], "sender_tail": updated.get("sender_tail"),
        "sender_domain": None, "question": updated.get("question"),
        "reply": updated.get("final"), "reply_chars": len(updated.get("final") or ""),
        "model_latency_ms": updated.get("model_latency_ms"), "total_latency_ms": None,
        "fallback": updated.get("fallback"), "error_class": updated.get("error_class"),
        "error_detail": None, "cold_start_suspected": False, "ack_sent": False,
        "acks_sent": 0, "send_ok": send_ok, "send_error": send_error,
        "supervision": updated["status"],
        "draft": updated["draft"], "final": updated.get("final"),
        "edit_reason": updated.get("edit_reason"),
        "decision_latency_s": updated.get("decision_latency_s"),
        # ⛔ WHO decided, in the analysis corpus too — not only in the queue, which gets
        # purged. Per-reviewer corrections are the signal that shows one reviewer approving
        # what another would have caught, and it cannot be recovered later.
        "decided_by_name": updated.get("decided_by_name"),
        "claim_count": updated.get("claim_count"),
        "release_count": updated.get("release_count"),
        "notify_count": updated.get("notify_count"),
    })
    print(f"[review] {updated['status'].upper()} {rid} by {name} "
          f"latency={updated.get('decision_latency_s')}s "
          f"reason={updated.get('edit_reason')!r}", flush=True)
    return {"ok": True, "status": updated["status"], "by": name, "send_ok": send_ok,
            "send_error": send_error}


@app.function(image=image, secrets=[SECRET])
@modal.fastapi_endpoint(method="GET")
def review_queue(token: str = None, include_sender: bool = False):
    """The queue as JSON, for analysis. `sender` is withheld unless explicitly requested, so
    the default export carries no reachable identifier — matching the transcript store."""
    if not _admin_ok(token):
        return {"status": "not found"}
    core = _core()
    items = _queue_items()
    if not include_sender:
        items = [{k: v for k, v in i.items() if k != "sender"} for i in items]
    return {"count": len(items), "summary": core.review_summary(items), "items": items}


# ⛔⛔ THE SWEEPER, AND THE ONE PROPERTY THAT MATTERS ABOUT IT: IT HAS NO SEND PATH.
#
# Grep this function for `_send_once` on a participant. It appears exactly nowhere — it can
# only RELEASE an expired claim and RE-NOTIFY the roster. No elapsed time, no queue depth and
# no number of reviewers causes a reply to reach a participant unread, and that is not a
# policy written in a comment: there is no line of code here that could do it.
#
# This is the line R7's condition rests on. A "send after N minutes if nobody objects"
# fallback is the single change that would void the founder's reading, and it is exactly the
# change that looks reasonable at 2am when a queue has backed up — so it is ruled out
# structurally rather than left to judgement.
@app.function(image=image, secrets=[SECRET], timeout=600,
              schedule=modal.Period(minutes=3))
async def sweep_review_queue():
    """Release expired claims; re-notify unclaimed drafts. Never sends to a participant."""
    core = _core()
    settings = _settings()
    released, renotified, pending = 0, 0, 0
    for it in _queue_items():
        if it.get("status") != "pending":
            continue
        pending += 1
        it, was_released = core.release_expired_claim(it)
        if was_released:
            released += 1
            try:
                REVIEW_QUEUE[it["review_id"]] = it
            except Exception as e:                                   # noqa: BLE001
                print(f"[sweep] release not stored for {it['review_id']}: {e}")
            print(f"[sweep] RELEASED {it['review_id']} from "
                  f"...{(it.get('released_from') or '')[-4:]} — back to the roster, "
                  f"NOT sent", flush=True)
        if core.needs_renotify(it, renotify_after_s=settings.renotify_after_s):
            sent = await _notify_reviewers(it, renotify=True)
            _mark_notified(it, sent, renotify=True)
            renotified += 1
            print(f"[sweep] RENOTIFIED {it['review_id']} to {sent} reviewer(s) — "
                  f"still pending, still unsent", flush=True)
    if pending or released or renotified:
        print(f"[sweep] pending={pending} released={released} renotified={renotified}",
              flush=True)
    return {"pending": pending, "released": released, "renotified": renotified,
            "sent_to_participants": 0}


@app.function(image=image, secrets=[SECRET], timeout=120)
async def seed_test_draft(label: str = "seed"):
    """Put ONE synthetic draft in the queue, for verifying the roster mechanics live.

    ⛔⛔ A MODAL FUNCTION, NOT A WEB ENDPOINT, AND THAT IS THE SECURITY PROPERTY. Reaching
    this requires Modal CLI credentials (`modal run ...::seed_test_draft`); there is NO public
    route that can place a draft in the review queue. A `/review_seed?token=` endpoint would
    have been easier to call from a test script and would also have been a way to make a
    reviewer approve text that no participant ever asked for.

    ⚠️ THE SENDER IS A DOCUMENTED UNROUTABLE TEST NUMBER. Even a successful send cannot reach
    a person — but the verification asserts the send was never ATTEMPTED, which is the
    stronger claim and the one R7's condition actually needs.
    """
    from datetime import datetime, timezone
    core = _core()
    settings = _settings()
    now = datetime.now(timezone.utc)
    sender = "+255700000000"          # reserved test number, routes nowhere
    sender_hash, sender_tail = core.sender_ids(sender, settings.sender_salt)
    row = {
        "ts": now.isoformat(timespec="seconds") + f"-{label}",
        "build": BUILD, "kind": "question",
        "sender_hash": sender_hash, "sender_tail": sender_tail,
        "question": f"[MTIHANI {label}] Nina wafanyakazi 15 — je SDL inanihusu?",
        "model_latency_ms": 0, "fallback": False, "error_class": None,
    }
    item = core.review_item(
        row=row, sender=sender,
        draft=f"[MTIHANI {label}] Ndiyo. Una wafanyakazi 15 (10 au zaidi), hivyo SDL "
              f"inatozwa — asilimia 3.5 ya jumla ya mishahara.",
        engine_working="Ndiyo. Una wafanyakazi 15 (10 au zaidi), hivyo SDL inatozwa.",
        facts=["sdl_rate: SDL ni asilimia 3.5 ya jumla ya mishahara."],
        review_id=f"TEST-{label}")
    REVIEW_QUEUE[item["review_id"]] = item
    sent = await _notify_reviewers(item)
    _mark_notified(item, sent)
    print(f"SEEDED {item['review_id']}", flush=True)
    return item["review_id"]


@app.function(image=image, secrets=[SECRET])
@modal.fastapi_endpoint(method="POST")
def review_purge(token: str = None):
    """Drop the real number from every DECIDED item, keeping everything else.

    The number's lifetime should be the decision's lifetime, not the pilot's. Pending items
    are untouched — purging one would make its answer undeliverable."""
    if not _admin_ok(token):
        return {"status": "not found"}
    purged = 0
    for it in _queue_items():
        if it.get("status") != "pending" and it.get("sender"):
            it["sender"] = None
            it["sender_purged"] = True
            try:
                REVIEW_QUEUE[it["review_id"]] = it
                purged += 1
            except Exception as e:                                   # noqa: BLE001
                print(f"[review] purge failed for {it['review_id']}: {e}")
    return {"purged": purged}


@app.function(image=image, secrets=[SECRET])
@modal.fastapi_endpoint(method="GET")
def health():
    """The deploy check. `build` is the git SHA baked at deploy time — Modal can serve
    a warm container running OLD code (R16), so confirming this against the commit you
    just pushed is the only proof the deploy took."""
    try:
        keys = list(TRANSCRIPTS.keys())
        store = {"ok": True, "backend": "modal.Dict", "rows": len(keys),
                 "months": sorted({str(k).split("/")[0] for k in keys})}
    except Exception as e:                                           # noqa: BLE001
        store = {"ok": False, "backend": "modal.Dict",
                 "error": f"{type(e).__name__}: {e}"}
    return {
        "status": "ok",
        "product": "Chike by Africa Giants",
        "tagline": "Fahamu Biashara Yako, Maarifa Yako",
        "build": os.environ.get("CHIKE_BUILD", "dev"),
        "app": "chike-whatsapp",
        "model_timeout_s": float(os.environ.get("MODEL_TIMEOUT_S", "240")),
        "slow_ack_after_s": float(os.environ.get("SLOW_ACK_AFTER_S", "12")),
        # Reported so the live check can prove WHICH ack timing is serving. R16: a
        # config-only change has no code diff to remind you a deploy happened, and a
        # warm container will happily keep the old value.
        "second_ack_after_s": float(os.environ.get("SECOND_ACK_AFTER_S", "45")),
        "webhook_token_set": bool(os.environ.get("WEBHOOK_TOKEN", "")),
        "transcripts_endpoint": bool(os.environ.get("ADMIN_TOKEN", "")),
        "transcript_store": store,
        # ⛔⛔ THE SUPERVISION STATE, REPORTED FROM THE SAME FUNCTION THE HANDLER USES.
        #
        # This is the field the founder's R7 reading rests on: "nothing reaches a
        # participant unreviewed". A typo in SUPERVISED does not fail safe — it silently
        # turns supervision OFF while the reviewer believes every reply is being read — so
        # the state has to be CHECKABLE rather than assumed, and the pilot runbook makes
        # reading this the first step after any deploy, not the last.
        #
        # ⚠️ IT CALLS `_settings().supervised` RATHER THAN RE-READING THE ENV VAR. Re-parsing
        # it here would be a second copy of the parse rule, and a /health that agreed with
        # itself while disagreeing with the handler is the dual-file divergence CLAUDE.md
        # warns about, in the one place built to detect divergence.
        # ⚠️ AND IF IT CANNOT BE DETERMINED, /health SAYS SO RATHER THAN GUESSING. `None` is
        # not `False`: reporting False on a failed lookup would read as "supervision is off"
        # when the truth is "this endpoint could not tell", and the whole point of the field
        # is that the reviewer can trust what it says. /health is the diagnostic of last
        # resort, so it must degrade rather than raise — a 500 here tells you nothing about
        # anything. (It broke two tests the moment it could raise, which is how this was
        # caught rather than discovered live.)
        **_supervision_health(),
        "review_endpoint": bool(os.environ.get("ADMIN_TOKEN", "")),
        "review_queue": _review_queue_health(),
        # ── THE COHORT, REPORTED BESIDE THE SUPERVISION FLAG (asked for explicitly) ──
        # `cohort_size` is the declared enrolment; `participants_seen` is how many distinct
        # people have actually messaged. Reporting both is what stops the setting being
        # decoration (R32: a number the code never compares to anything is not a rule).
        # It MONITORS rather than gates, because refusing an 11th participant is a mechanism
        # whose failure lands on a real user and is invisible to us when it fires.
        "cohort": _cohort_health(),
        # Roster SIZE and reviewer HANDLES, never the numbers. A /health that printed the
        # roster would publish the reviewers' phone numbers to anyone who can read it, and
        # the handles are what the links carry anyway.
        "roster": _roster_health(),
        # PRESENCE BY NAME, never values. A misnamed key in the secret and a wrong
        # value produce identical failures at the endpoint — that ambiguity cost hours
        # on `modal-api-token`. This makes "is the key even there, spelled that way?"
        # answerable from outside, before anyone starts debugging a value.
        "secret_keys_present": {k: bool(os.environ.get(k, "")) for k in EXPECTED_KEYS},
        "secret_keys_missing": [k for k in EXPECTED_KEYS if not os.environ.get(k, "")],
        # THE CHECK WE NEVER HAD. Three Wappfly 401s and two token rotations failed to
        # converge because nothing could compare the secret's VALUE against the token
        # proven to work — and neither party may print it. A truncated SHA-256 is
        # comparable without being reversible; the length and whitespace flags catch a
        # trailing newline on paste, which Wappfly would see as a different string.
        # EVERY credential, not just the one in dispute. WAPPFLY_TOKEN's mismatch cost
        # three days; WEBHOOK_TOKEN's is suspected of costing the next send, one
        # credential over and within days -- "present is not correct" twice, with
        # nothing able to see either. A credential failure during a pilot is
        # indistinguishable from a product failure without this.
        "credentials": {k: _token_fingerprint(k) for k in EXPECTED_KEYS},
        # Kept flat as well: the WAPPFLY_TOKEN comparison that settled 2026-08-14 was
        # quoted from these key names, and a diagnostic people have used should not
        # move out from under them.
        **_token_fingerprint_flat("WAPPFLY_TOKEN"),
    }


def _fp(value) -> str:
    """sha256[:8] of a value we must never print. Same construction as the credential
    fingerprints, applied to a string in hand rather than one read from the environment."""
    import hashlib
    if not value:
        return None
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:8]


def _token_fingerprint(key: str) -> dict:
    """Comparable, never reversible, and it never returns the value.

    Truncated SHA-256 is safe to publish and safe to paste into a support ticket, which
    is what makes a credential checkable by two parties who must both never print it.
    `length` catches truncation and stray wrapping characters (WAPPFLY_TOKEN was stored
    at 66 chars against a real 64); `has_whitespace` catches a trailing newline on paste,
    which the far end sees as a different string.
    """
    import hashlib
    raw = os.environ.get(key, "")
    return {
        "fingerprint": hashlib.sha256(raw.encode("utf-8")).hexdigest()[:8] if raw else None,
        "len": len(raw),
        "has_whitespace": raw != raw.strip(),
    }


def _token_fingerprint_flat(key: str) -> dict:
    fp = _token_fingerprint(key)
    return {f"{key.lower()}_fingerprint": fp["fingerprint"],
            f"{key.lower()}_len": fp["len"],
            f"{key.lower()}_has_whitespace": fp["has_whitespace"]}


@app.function(image=image, secrets=[SECRET])
@modal.fastapi_endpoint(method="GET")
def transcripts(token: str = None, n: int = 50):
    """Read the pilot's record. Disabled entirely when ADMIN_TOKEN is unset — an open
    endpoint here would publish every user's questions."""
    expected = os.environ.get("ADMIN_TOKEN", "")
    if not expected or token != expected:
        return {"status": "not found"}
    try:
        keys = sorted(TRANSCRIPTS.keys())
    except Exception as e:                                           # noqa: BLE001
        return {"status": "error", "detail": f"{type(e).__name__}: {e}"}
    keys = keys[-max(1, min(int(n), 500)):]
    rows = []
    for k in keys:
        try:
            rows.append(TRANSCRIPTS[k])
        except Exception as e:                                       # noqa: BLE001
            rows.append({"unreadable": str(k), "error": f"{type(e).__name__}: {e}"})
    return {"count": len(rows), "backend": "modal.Dict", "rows": rows}
