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
EXPECTED_KEYS = ("WAPPFLY_TOKEN", "WEBHOOK_TOKEN", "ADMIN_TOKEN", "SENDER_SALT")

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
    )


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
            + '<input id="r-' + rid + '" placeholder="reason (required to edit or '
              'withhold)">'
            "<div class=b>"
            "<button class=s onclick=\"act('" + rid + "','send')\">Send</button>"
            "<button class=e onclick=\"act('" + rid + "','edit')\">Send edit</button>"
            "<button class=x onclick=\"act('" + rid + "','withhold')\">Withhold</button>"
            "</div>"
            '<div class=o id="o-' + rid + '"></div>'
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
    script = (
        "<script>async function act(id,action){"
        "var out=document.getElementById('o-'+id);out.textContent='working...';"
        "var tok=new URLSearchParams(location.search).get('token');"
        "try{var r=await fetch('review_act?token='+encodeURIComponent(tok),"
        "{method:'POST',headers:{'Content-Type':'application/json'},"
        "body:JSON.stringify({review_id:id,action:action,"
        "edited:document.getElementById('t-'+id).value,"
        "reason:document.getElementById('r-'+id).value})});"
        "var j=await r.json();"
        "out.textContent=j.ok?(j.status+(j.send_ok===false?' BUT SEND FAILED: '+"
        "(j.send_error||''):'')):('ERROR: '+(j.detail||r.status));"
        "}catch(e){out.textContent='ERROR: '+e;}}</script>")
    return HTMLResponse(head + stats + body + script)


@app.function(image=image, secrets=[SECRET], timeout=120)
@modal.fastapi_endpoint(method="POST")
async def review_act(item: dict, token: str = None):
    """Take one decision. The rules live in handler_core.apply_decision — pure, and tested
    without Modal — so this function only does I/O.

    ⛔ THE REASON REQUIREMENT IS ENFORCED IN apply_decision, NOT HERE. A UI-only check is
    bypassed by the first curl, and an edit with no reason is a correction whose LABEL is
    missing, which is the whole value of the edit."""
    from fastapi.responses import JSONResponse
    if not _admin_ok(token):
        return JSONResponse({"status": "not found"}, status_code=404)
    core = _core()
    rid = (item or {}).get("review_id")
    try:
        existing = REVIEW_QUEUE[rid]
    except Exception:                                                # noqa: BLE001
        return JSONResponse({"ok": False, "detail": f"unknown review_id {rid!r}"},
                            status_code=404)
    try:
        updated, to_send = core.apply_decision(
            existing, (item or {}).get("action"),
            edited=(item or {}).get("edited"), reason=(item or {}).get("reason"))
    except ValueError as e:
        return JSONResponse({"ok": False, "detail": str(e)}, status_code=400)

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
    })
    print(f"[review] {updated['status'].upper()} {rid} "
          f"latency={updated.get('decision_latency_s')}s "
          f"reason={updated.get('edit_reason')!r}", flush=True)
    return {"ok": True, "status": updated["status"], "send_ok": send_ok,
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
