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

    row = await core.deliver(sender, text, ask, _send_once, settings, BUILD)
    _write_row(row)
    return {"fallback": row["fallback"], "error_class": row["error_class"]}


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
