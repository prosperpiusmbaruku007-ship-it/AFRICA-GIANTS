"""The WhatsApp handler must never drop a user's answer in silence.

These tests FORCE the failures rather than reading the code for them. The defect they
guard against was invisible to reading: on Railway, `call_modal` looked fine and its
exception was swallowed by the event loop one frame above, so the user simply never
heard back.

`deliver()` takes `ask` and `send_once` as injected coroutines, so a timeout, a dead
model, a junk response, a failing send and a bug inside the handler are all forced at
the seam that matters — and the assertions are on what the USER RECEIVED and what
landed in the ROW, never on the code's shape.

The port from Railway to Modal changed the platform, not the guarantee: this file is
the evidence for that claim. `transport` and `http_status` are gone as error classes
because there is no longer a network hop or a token gate between handler and model.
"""
import asyncio
import importlib.util
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CORE_PATH = os.path.join(_ROOT, "chike-whatsapp", "handler_core.py")
_spec = importlib.util.spec_from_file_location("chike_handler_core", _CORE_PATH)
core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(core)

SENDER = "255712345678@s.whatsapp.net"


def settings(**over):
    base = dict(model_timeout_s=5.0, slow_ack_after_s=0, cold_start_suspected_s=30.0,
                send_attempts=1, send_retry_delay_s=0.01,
                sender_salt="test-salt", secrets=("super-secret-token-value",))
    base.update(over)
    return core.Settings(**base)


class Outbox:
    """Stands in for Wappfly. Records what the user actually received."""

    def __init__(self, fail_times=0, status=500):
        self.sent, self.fail_times, self.status = [], fail_times, status

    async def send_once(self, to, text):
        if self.fail_times > 0:
            self.fail_times -= 1
            return False, f"HTTP {self.status}: rejected"
        self.sent.append({"to": to, "text": text})
        return True, None

    @property
    def texts(self):
        return [m["text"] for m in self.sent]


def run(ask, out, **over):
    return asyncio.run(core.deliver(SENDER, "SDL ni kiasi gani?", ask,
                                    out.send_once, settings(**over), build="testbuild"))


def replying(text):
    async def ask(_message):
        return {"reply": text}
    return ask


# ---------------------------------------------------------------------------
# the happy path
# ---------------------------------------------------------------------------

def test_a_normal_answer_reaches_the_user_and_the_row():
    out = Outbox()
    row = run(replying("SDL ni asilimia 3.5."), out)
    assert out.texts == ["SDL ni asilimia 3.5."]
    assert row["fallback"] is False
    assert row["error_class"] is None
    assert row["reply"] == "SDL ni asilimia 3.5."
    assert row["question"] == "SDL ni kiasi gani?"
    assert row["send_ok"] is True
    assert row["build"] == "testbuild"
    assert row["cold_start_suspected"] is False


# ---------------------------------------------------------------------------
# THE DEFECT: a slow or broken model used to deliver nothing at all
# ---------------------------------------------------------------------------

def test_a_model_timeout_delivers_fallback_and_is_recorded_as_a_timeout():
    """The exact failure the rewrite exists for. Before it, the exception was
    swallowed inside a fire-and-forget task: no FALLBACK, no row, and no way to tell
    it apart from a slow answer."""
    async def never(_message):
        await asyncio.sleep(30)

    out = Outbox()
    row = run(never, out, model_timeout_s=0.3)
    assert out.texts == [core.FALLBACK], "the user must receive FALLBACK, not silence"
    assert row["fallback"] is True
    assert row["error_class"] == "timeout"
    assert "0.3s" in row["error_detail"]
    assert row["send_ok"] is True


def test_a_failing_model_call_is_recorded_as_model_error_not_as_a_timeout():
    """Different cause, different repair — and on Modal this absorbs what used to be
    `transport` and `http_status`, since the hop and the token gate are gone."""
    async def boom(_message):
        raise ConnectionError("chike-inference unreachable")

    out = Outbox()
    row = run(boom, out)
    assert out.texts == [core.FALLBACK]
    assert row["error_class"] == "model_error"
    assert "chike-inference unreachable" in row["error_detail"]


@pytest.mark.parametrize("result,expected", [
    ({"error": "no reply key"}, "no_reply_field"),
    ({"reply": "   "},          "no_reply_field"),
    ({"reply": ""},             "no_reply_field"),
    ("a bare string",           "bad_response"),
    (None,                      "bad_response"),
    ([{"reply": "x"}],          "bad_response"),
])
def test_every_malformed_model_response_still_answers_the_user(result, expected):
    async def ask(_message):
        return result

    out = Outbox()
    row = run(ask, out)
    assert out.texts == [core.FALLBACK]
    assert row["error_class"] == expected
    assert row["fallback"] is True


def test_no_exception_can_escape_deliver(monkeypatch):
    """Belt and braces: a bug in THIS code, not the model, must still reach the user —
    AND must not be blamed on the model.

    This test found a real defect on its first run. `extract_reply` was being called
    inside the try that classifies model failures, so a bug in our own parsing came
    back as `error_class: model_error` — an error class lying about who failed, which
    would have sent someone debugging chike-inference for a fault in this file. The
    parse now sits outside that try.
    """
    def explode(_result):
        raise RuntimeError("simulated handler bug")

    monkeypatch.setattr(core, "extract_reply", explode)
    out = Outbox()
    row = run(replying("jibu"), out)
    assert out.texts == [core.FALLBACK], "a bug in our own code must not mean silence"
    assert row["error_class"] == "handler_bug"
    assert "simulated handler bug" in row["error_detail"]


def test_a_send_that_raises_is_caught_rather_than_killing_the_task():
    class Exploding:
        async def send_once(self, to, text):
            raise RuntimeError("wappfly client blew up")

    row = asyncio.run(core.deliver(SENDER, "swali", replying("jibu"),
                                   Exploding().send_once, settings(), "testbuild"))
    assert row["send_ok"] is False
    assert "wappfly client blew up" in row["send_error"]
    assert row["reply"] == "jibu", "the undelivered answer is still recorded"


def test_deliver_returns_a_row_even_when_the_sender_id_is_junk():
    out = Outbox()
    row = asyncio.run(core.deliver(None, "swali", replying("jibu"),
                                   out.send_once, settings(), "testbuild"))
    assert row["reply"] == "jibu"
    assert row["sender_hash"]


# ---------------------------------------------------------------------------
# secrets
# ---------------------------------------------------------------------------

def test_a_secret_never_reaches_a_transcript_row():
    """This project has leaked a token twice, and transcripts get read and pasted."""
    async def leaky(_message):
        raise RuntimeError("failed calling https://x/?token=super-secret-token-value")

    out = Outbox()
    row = run(leaky, out)
    blob = json.dumps(row, ensure_ascii=False)
    assert "super-secret-token-value" not in blob
    assert "<REDACTED>" in row["error_detail"]


# ---------------------------------------------------------------------------
# the slow-path acknowledgement
# ---------------------------------------------------------------------------

def test_a_slow_answer_gets_an_ack_first_so_the_user_is_not_left_in_silence():
    async def slow(_message):
        await asyncio.sleep(0.8)
        return {"reply": "jibu"}

    out = Outbox()
    row = run(slow, out, slow_ack_after_s=0.2)
    assert out.texts == [core.SLOW_ACK, "jibu"]
    assert row["ack_sent"] is True
    assert row["fallback"] is False


def test_a_fast_answer_gets_no_ack():
    out = Outbox()
    row = run(replying("jibu"), out, slow_ack_after_s=5.0)
    assert out.texts == ["jibu"], "a warm 6s answer must not be preceded by chatter"
    assert row["ack_sent"] is False


def test_the_ack_still_precedes_a_fallback_when_the_model_times_out():
    async def never(_message):
        await asyncio.sleep(30)

    out = Outbox()
    run(never, out, model_timeout_s=0.6, slow_ack_after_s=0.2)
    assert out.texts == [core.SLOW_ACK, core.FALLBACK]


def test_the_ack_can_be_disabled():
    async def slow(_message):
        await asyncio.sleep(0.4)
        return {"reply": "jibu"}

    out = Outbox()
    assert run(slow, out, slow_ack_after_s=0)["ack_sent"] is False
    assert out.texts == ["jibu"]


# ---------------------------------------------------------------------------
# the outbound leg
# ---------------------------------------------------------------------------

def test_a_failed_send_is_retried_then_recorded_rather_than_lost():
    out = Outbox(fail_times=1)
    row = run(replying("jibu"), out, send_attempts=2)
    assert out.texts == ["jibu"], "the retry must actually deliver"
    assert row["send_ok"] is True


def test_a_send_that_never_succeeds_is_recorded_as_such():
    """If Wappfly rejects every attempt the user got nothing — precisely the case a
    pilot must be able to see afterwards."""
    out = Outbox(fail_times=99)
    row = run(replying("jibu"), out, send_attempts=2)
    assert out.texts == []
    assert row["send_ok"] is False
    assert "500" in row["send_error"]
    assert row["reply"] == "jibu", "the answer we failed to deliver must still be recorded"


# ---------------------------------------------------------------------------
# cold start is a proxy and must keep saying so
# ---------------------------------------------------------------------------

def test_a_cold_start_is_flagged_as_suspected_not_measured():
    """Neither Modal's response nor its Python API tells the handler whether the
    container was cold. The field name has to keep carrying that caveat."""
    async def slow(_message):
        await asyncio.sleep(0.4)
        return {"reply": "jibu"}

    out = Outbox()
    row = run(slow, out, cold_start_suspected_s=0.2)
    assert row["cold_start_suspected"] is True
    assert "cold_start" not in row


# ---------------------------------------------------------------------------
# senders
# ---------------------------------------------------------------------------

def test_the_row_pseudonymises_the_number_but_keeps_it_correlatable():
    out = Outbox()
    a = asyncio.run(core.deliver("255712345678@s.whatsapp.net", "q", replying("r"),
                                 out.send_once, settings(), "b"))
    b = asyncio.run(core.deliver("255712345678@s.whatsapp.net", "q", replying("r"),
                                 out.send_once, settings(), "b"))
    c = asyncio.run(core.deliver("255787654321@s.whatsapp.net", "q", replying("r"),
                                 out.send_once, settings(), "b"))
    assert a["sender_hash"] == b["sender_hash"] != c["sender_hash"]
    assert a["sender_tail"] == "5678" and c["sender_tail"] == "4321"
    assert "255712345678" not in json.dumps([a, b, c]), "no raw phone numbers"


def test_the_salt_changes_the_hash():
    h1, _ = core.sender_ids(SENDER, "salt-a")
    h2, _ = core.sender_ids(SENDER, "salt-b")
    assert h1 != h2


# ---------------------------------------------------------------------------
# webhook parsing
# ---------------------------------------------------------------------------

def _delivery(text, from_me=False):
    return {"event": "messages.received",
            "data": {"messages": {"conversation": text,
                                  "remoteJid": SENDER, "fromMe": from_me}}}


def test_parse_webhook_routes_greetings_and_questions():
    assert core.parse_webhook(_delivery("Habari"))["kind"] == "greeting"
    assert core.parse_webhook(_delivery("SDL ni ngapi?"))["kind"] == "question"


@pytest.mark.parametrize("body", [
    {}, None, "nonsense",
    {"event": "messages.sent", "data": {"messages": {"conversation": "hi",
                                                     "remoteJid": SENDER}}},
    _delivery("hi", from_me=True),
    _delivery("   "),
    {"event": "messages.received", "data": {"messages": {"conversation": "hi"}}},
])
def test_parse_webhook_ignores_what_it_should(body):
    assert core.parse_webhook(body) is None


# ---------------------------------------------------------------------------
# transcript file naming — the Modal Volume hazard
# ---------------------------------------------------------------------------

def test_two_rows_from_the_same_sender_in_the_same_second_get_different_files():
    """Modal Volumes are not a POSIX shared filesystem: two containers appending to
    one JSONL do not interleave, the last committer wins, and the other row is GONE.
    One file per row is the mitigation — so filenames must not collide either."""
    row = {"ts": "2026-08-14T09:15:00+00:00", "sender_hash": "abc123def456"}
    names = {core.transcript_filename(row) for _ in range(200)}
    assert len(names) == 200


def test_the_transcript_filename_is_month_partitioned_and_path_safe():
    name = core.transcript_filename({"ts": "2026-08-14T09:15:00+00:00",
                                     "sender_hash": "abc"}, unique="zzz")
    assert name.startswith("2026-08/")
    assert ":" not in name, "colons are not legal in filenames on every platform"
    assert name.endswith("-abc-zzz.json")


# ---------------------------------------------------------------------------
# the real Wappfly leg, over real HTTP
# ---------------------------------------------------------------------------

class _Stub:
    def __init__(self):
        self.received, self.status = [], 200
        outer = self

        class H(BaseHTTPRequestHandler):
            def do_POST(self):                                  # noqa: N802
                n = int(self.headers.get("Content-Length", 0))
                outer.received.append(self.rfile.read(n).decode("utf-8") if n else "")
                self.send_response(outer.status)
                self.send_header("Content-Length", "2")
                self.end_headers()
                self.wfile.write(b"{}")

            def log_message(self, *a):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}/"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()


@pytest.fixture()
def wappfly_stub():
    s = _Stub()
    try:
        yield s
    finally:
        s.stop()


def test_the_real_send_reports_success_and_failure_over_real_http(wappfly_stub,
                                                                 monkeypatch):
    """`_send_once` lives in the Modal wrapper, so it is the one piece the injected
    tests above cannot reach. Its status-code handling is what decides whether the
    retry in handler_core ever fires."""
    monkeypatch.setenv("WAPPFLY_TOKEN", "t")
    spec = importlib.util.spec_from_file_location(
        "chike_modal_whatsapp", os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"))
    mw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mw)
    monkeypatch.setattr(mw, "WAPPFLY_SEND_URL", wappfly_stub.url)

    ok, detail = asyncio.run(mw._send_once("255700000001@s.whatsapp.net", "jibu"))
    assert ok is True and detail is None
    assert json.loads(wappfly_stub.received[0])["text"] == "jibu"

    wappfly_stub.status = 500
    ok, detail = asyncio.run(mw._send_once("255700000001@s.whatsapp.net", "jibu"))
    assert ok is False and "500" in detail

    monkeypatch.setattr(mw, "WAPPFLY_SEND_URL", "http://127.0.0.1:1/")
    ok, detail = asyncio.run(mw._send_once("255700000001@s.whatsapp.net", "jibu"))
    assert ok is False and detail, "an unreachable Wappfly must report, not raise"


def test_every_secret_key_the_app_reads_is_declared_in_expected_keys():
    """A misnamed key in a Modal Secret and a wrong value fail IDENTICALLY at the
    endpoint. /health reports presence by name so the ambiguity is resolved before
    anyone starts debugging a value — but only if EXPECTED_KEYS actually lists every
    key the code reads, which is what this pins."""
    import re
    spec = importlib.util.spec_from_file_location(
        "chike_modal_whatsapp_keys",
        os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"))
    mw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mw)
    src = open(os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"),
               encoding="utf-8").read()

    read = set(re.findall(r'os\.environ\.get\(\s*"([A-Z_]+)"', src))
    # Tunables carry safe defaults and are not secret material; CHIKE_BUILD is baked
    # at deploy time, not stored in the secret.
    tunables = {"CHIKE_BUILD", "WAPPFLY_SEND_URL", "MODEL_TIMEOUT_S", "SLOW_ACK_AFTER_S",
                "COLD_START_SUSPECTED_S", "SEND_ATTEMPTS", "WAPPFLY_TIMEOUT_S"}
    assert read - tunables == set(mw.EXPECTED_KEYS), (
        "a secret key is read but not reported by /health, or vice versa")


def test_health_reports_key_presence_without_leaking_values(monkeypatch):
    spec = importlib.util.spec_from_file_location(
        "chike_modal_whatsapp_health",
        os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"))
    mw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mw)
    monkeypatch.setenv("WAPPFLY_TOKEN", "a-real-looking-token-value")
    monkeypatch.delenv("SENDER_SALT", raising=False)

    h = mw.health.get_raw_f()()
    assert h["secret_keys_present"]["WAPPFLY_TOKEN"] is True
    assert "SENDER_SALT" in h["secret_keys_missing"]
    assert "a-real-looking-token-value" not in json.dumps(h), "presence only, no values"


def test_the_modal_app_declares_a_separate_app_and_spawns_rather_than_tasks():
    """Two structural guarantees worth pinning, because breaking either is silent:
    a shared app would let an R16 `modal app stop chike-inference` take WhatsApp down,
    and `asyncio.create_task` would let Modal reclaim the container mid-answer."""
    src = open(os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"),
               encoding="utf-8").read()
    assert 'modal.App("chike-whatsapp")' in src
    assert "answer_and_send.spawn(" in src
    # The call form, not the words: the module docstring explains at length why
    # create_task is wrong here, and a prose mention must not fail the pin.
    assert "asyncio.create_task(" not in src
    assert "retries=0" in src, "a retry would deliver a second answer to one question"


def test_the_sender_domain_is_recorded_and_is_not_pii():
    assert core.sender_domain("255712345678@s.whatsapp.net") == "s.whatsapp.net"
    assert core.sender_domain("12345@lid") == "lid"
    assert core.sender_domain("nodomain") == ""
    out = Outbox()
    row = run(replying("jibu"), out)
    assert row["sender_domain"] == "s.whatsapp.net"
    assert "255712345678" not in json.dumps(row)


def test_the_token_fingerprint_is_comparable_but_not_reversible(monkeypatch):
    """Three Wappfly 401s and two rotations failed to converge because nothing could
    compare the secret's value against the token proven to work, and neither party may
    print it. Truncated SHA-256 is comparable without being reversible."""
    spec = importlib.util.spec_from_file_location(
        "chike_modal_whatsapp_fp",
        os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"))
    mw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mw)

    monkeypatch.setenv("WAPPFLY_TOKEN", "abc123")
    fp = mw._token_fingerprint("WAPPFLY_TOKEN")
    import hashlib
    assert fp["fingerprint"] == hashlib.sha256(b"abc123").hexdigest()[:8]
    assert fp["len"] == 6
    assert fp["has_whitespace"] is False
    assert "abc123" not in json.dumps(fp), "the value must never appear"

    monkeypatch.setenv("WAPPFLY_TOKEN", "abc123" + chr(10))
    assert mw._token_fingerprint("WAPPFLY_TOKEN")["has_whitespace"] is True


def test_every_credential_is_fingerprinted_not_just_the_one_in_dispute(monkeypatch):
    """WAPPFLY_TOKEN's mismatch cost three days; WEBHOOK_TOKEN's is suspected of costing
    the next send -- one credential over, within days, with nothing able to see either."""
    spec = importlib.util.spec_from_file_location(
        "chike_modal_whatsapp_all",
        os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"))
    mw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mw)
    for k in mw.EXPECTED_KEYS:
        monkeypatch.setenv(k, "value-for-" + k)
    h = mw.health.get_raw_f()()
    assert set(h["credentials"]) == set(mw.EXPECTED_KEYS)
    for k in mw.EXPECTED_KEYS:
        assert h["credentials"][k]["fingerprint"]
        assert "value-for-" not in json.dumps(h["credentials"][k])
    assert h["wappfly_token_fingerprint"] == h["credentials"]["WAPPFLY_TOKEN"]["fingerprint"]


def test_a_rejected_delivery_is_recorded_rather_than_inferred_from_missing_prints():
    """Both refusal branches returned 200 and printed nothing, so a rejected delivery was
    indistinguishable from one that never arrived -- diagnosable only by noticing which
    log lines were ABSENT. Same silent-drop class the rest of the module abolishes."""
    body = {"event": "messages.sent",
            "data": {"messages": {"conversation": "habari", "remoteJid": SENDER}}}
    row = core.rejection_row("ignored", body, settings(), "b")
    assert row["kind"] == "rejected"
    assert row["reject_reason"] == "ignored"
    assert row["error_class"] == "ignored"
    assert row["payload_shape"]["event"] == "messages.sent"
    assert row["payload_shape"]["text_field_present"] == ["conversation"]
    assert row["payload_shape"]["jid_field_present"] == ["remoteJid"]


def test_a_rejection_row_records_shape_but_never_content():
    body = {"event": "messages.received",
            "data": {"messages": {"conversation": "mshahara wangu ni 900000",
                                  "remoteJid": "255712345678@s.whatsapp.net"}}}
    blob = json.dumps(core.rejection_row("unauthorized", body, settings(), "b"))
    assert "255712345678" not in blob, "no phone numbers in a rejection record"
    assert "900000" not in blob, "no message content in a rejection record"
    assert "conversation" in blob, "but the SHAPE must be there"


def test_payload_shape_survives_junk():
    for junk in (None, "string", 42, [], {"event": "x", "data": "not-a-dict"}):
        core.payload_shape(junk)


def test_the_received_token_is_fingerprinted_not_printed():
    """Both ends hashed to 15d40b19 and the endpoint still rejected, so the value is
    altered in transit -- and nothing could SEE the arriving value. Fingerprinting what
    ARRIVED turns "they look the same but don't match" into a comparison."""
    spec = importlib.util.spec_from_file_location(
        "chike_modal_whatsapp_fp2",
        os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"))
    mw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mw)
    import hashlib
    assert mw._fp("abc") == hashlib.sha256(b"abc").hexdigest()[:8]
    assert mw._fp("") is None and mw._fp(None) is None
    assert "abc" not in str(mw._fp("abc"))
    # A percent-encoded arrival must fingerprint DIFFERENTLY from its decoded form --
    # that difference is the whole diagnostic.
    assert mw._fp("a-b_c") != mw._fp("a%2Db%5Fc")
