"""R42: every link we send through a chat app is ONE unbroken alphanumeric token (founder, 2026-11-12).

`+` (2026-11-10) and `:` (2026-11-12) are the same bug: a character LEGAL in a URL that something treats specially. Escaping
one at a time is a list the next character is not on. So the shape is asserted -- here, and at runtime inside `_draft_link`,
which fails CLOSED. The guard is only worth having if it REJECTS the two real failures, so those are planted as specimens.
"""
import asyncio
import ast
import importlib.util
import os
import re
import sys
import types

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("hc_chatsafe", os.path.join(_ROOT, "chike-whatsapp", "handler_core.py"))
hc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hc)

KEY = "test-key"
HOST = "https://prosperpiusmbaruku007--chike-whatsapp-d.modal.run"
NUMBER = "255712615913@s.whatsapp.net"
URL_RE = re.compile(r"https?://\S+")


def _urls(text):
    return URL_RE.findall(text)


# ── the check, as a table ──────────────────────────────────────────────────────────────────────────
GOOD = [HOST + "/" + "a1" * 40, HOST + "/abc123", "https://d.example/0f0f0f"]
BAD = [
    (HOST + "?r=2026-11-12T00%3A41%3A28%2B00%3A00-b5908217&v=206bae78f2&t=9b56ff732aab", "a query string"),
    (HOST + "/abc?x=1", "a query string"),
    (HOST + "/2026-11-12T00:41:28", "a colon"),
    (HOST + "/abc+def", "a plus"),
    (HOST + "/abc%3Adef", "percent-encoding"),
    (HOST + "/abc-def", "a hyphen"),
    (HOST + "/abc.def", "a dot"),
    (HOST + "/ABC123", "'A'"),
    (HOST + "/abc#frag", "a fragment"),
    (HOST + "/abc def", "whitespace"),
    ("http://d.example/abc", "is not https"),
    (HOST, "has no path token"),
    (HOST + "/", "has no path token"),
    ("", "is not https"),
]


@pytest.mark.parametrize("url", GOOD)
def test_a_single_alphanumeric_token_link_is_safe(url):
    assert hc.chat_link_problems(url) == [] and hc.assert_chat_safe_link(url) == url


@pytest.mark.parametrize("url,reason", BAD)
def test_anything_else_is_refused_with_the_reason(url, reason):
    problems = hc.chat_link_problems(url)
    assert problems and any(reason in p for p in problems), (url, problems)
    with pytest.raises(ValueError):
        hc.assert_chat_safe_link(url)


def test_PLANTED_the_two_real_failures_are_both_refused():
    """R26: a guard that cannot block the thing it exists to block is decoration. These are the actual links."""
    rid = "2026-11-12T00:41:28+00:00-b5908217"
    # 2026-11-10: the raw '+'
    raw_plus = f"{HOST}?r={rid}&v=206bae78f2&t=9b56ff732aab0ef62595875d9fba4f38"
    # 2026-11-12: the percent-encoded form that was then CUT at the first colon by whatever displayed it
    encoded = f"{HOST}?r=2026-11-12T00%3A41%3A28%2B00%3A00-b5908217&v=206bae78f2&t=9b56ff732aab0ef62595875d9fba4f38"
    for link in (raw_plus, encoded):
        assert hc.chat_link_problems(link), link
    assert any("query string" in p for p in hc.chat_link_problems(encoded))
    assert any("percent" in p for p in hc.chat_link_problems(encoded))


# ── the single builder, swept over adversarial ids ─────────────────────────────────────────────────
ADVERSARIAL_IDS = [
    "2026-11-12T00:41:28+00:00-b5908217", "2026-11-11T20:54:51+00:00-220401cb", "TEST-1791721161A", "TEST-does-not-exist-404probe",
    "a" * 200, "id with spaces & symbols = ? # % + : / \\ ' \"", "ünïcödé-ïd-日本語", "0", "x-y_z.w",
    "2026-11-12T00:41:28.123456+03:00-b5908217",
]


@pytest.mark.parametrize("rid", ADVERSARIAL_IDS)
def test_whatever_the_review_id_the_link_is_one_alphanumeric_token(rid):
    t = hc.review_link_token(KEY, rid, NUMBER)
    link = f"{HOST}/{t}"
    assert hc.chat_link_problems(link) == [], (rid, hc.chat_link_problems(link))
    assert re.fullmatch(r"[a-z0-9]+", t)
    # and it still round-trips to the SAME id (the envelope loses nothing, whatever the characters)
    assert hc.parse_review_link_token(t)[0] == rid


def _load_mw(monkeypatch):
    from conftest import isolate_modal_stores
    for k, v in {"REVIEW_D_URL": HOST, "REVIEW_CLAIM_URL": "https://c.example", "REVIEW_ACT_URL": "https://a.example"}.items():
        monkeypatch.setenv(k, v)
    pkg = types.ModuleType("chike_whatsapp")
    pkg.handler_core = hc
    monkeypatch.setitem(sys.modules, "chike_whatsapp", pkg)
    monkeypatch.setitem(sys.modules, "chike_whatsapp.handler_core", hc)
    spec = importlib.util.spec_from_file_location("chike_mw_chatsafe", os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"))
    mw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mw)
    isolate_modal_stores(mw, monkeypatch)
    monkeypatch.setenv("SENDER_SALT", "salt")
    monkeypatch.setenv("REVIEWER_ROSTER", "+255712615913:Prosper")
    monkeypatch.setenv("REVIEW_SIGNING_KEY", KEY)
    return mw


@pytest.mark.parametrize("rid", ADVERSARIAL_IDS)
def test_draft_link_itself_returns_a_chat_safe_link(monkeypatch, rid):
    mw = _load_mw(monkeypatch)
    link = mw._draft_link(mw._settings(), {"review_id": rid}, mw._settings().roster[0][0])
    assert hc.chat_link_problems(link) == [] and link.startswith(HOST + "/")


def test_draft_link_FAILS_CLOSED_when_the_token_would_contain_a_boundary_character(monkeypatch):
    """The guard runs inside the builder: a future change that sneaks a ':' or '+' back in raises -- no unsafe link ships."""
    mw = _load_mw(monkeypatch)
    for evil in ("abc:def", "abc+def", "abc%3Adef", "ABC", "abc?x=1", "abc-def"):
        monkeypatch.setattr(hc, "review_link_token", lambda *a, _e=evil, **k: _e)
        with pytest.raises(ValueError):
            mw._draft_link(mw._settings(), {"review_id": "x"}, mw._settings().roster[0][0])


def test_an_unsafe_link_means_NO_push_goes_out_and_the_draft_still_holds(monkeypatch):
    mw = _load_mw(monkeypatch)
    sent = []

    async def fake_send(to, text):
        sent.append(text)
        return True, None
    monkeypatch.setattr(mw, "_send_once", fake_send)
    monkeypatch.setattr(hc, "review_link_token", lambda *a, **k: "abc:def")
    item = {"review_id": "2026-11-12T00:41:28+00:00-b5908217", "question": "q", "draft": "d", "sender_tail": "5913",
            "facts": ["F"], "answer_path": "fact", "status": "pending"}
    loop = asyncio.new_event_loop()
    try:
        with pytest.raises(ValueError):
            loop.run_until_complete(mw._notify_reviewers(item))
    finally:
        loop.close()
    assert sent == [], "an unsafe link must not reach a message"


# ── every text builder: every link in every message ────────────────────────────────────────────────
def _safe_link(rid):
    return f"{HOST}/{hc.review_link_token(KEY, rid, NUMBER)}"


ITEM = {"review_id": "2026-11-12T00:41:28+00:00-b5908217", "question": "q?", "draft": "d", "sender_tail": "5913",
        "facts": ["F"], "engine_working": "W", "answer_path": "engine:vat_registration", "sender_hash": "abc",
        "status": "pending"}


def test_every_link_in_every_message_we_build_is_chat_safe():
    texts = [
        hc.notification_text(ITEM, _safe_link(ITEM["review_id"]), "Prosper"),
        hc.notification_text(ITEM, _safe_link(ITEM["review_id"]), "Prosper", renotify=True),
        hc.notification_text(dict(ITEM, fallback=True), _safe_link(ITEM["review_id"]), "Prosper"),
        hc.notification_text(dict(ITEM, duplicates_pending=["r0"]), _safe_link(ITEM["review_id"]), "Prosper"),
        hc.notification_text(dict(ITEM, facts=[], engine_working=None, answer_path="fact"),
                             _safe_link(ITEM["review_id"]), "Prosper"),
        hc.digest_text([ITEM, dict(ITEM, review_id="2026-11-12T00:42:57+00:00-b5908217")],
                       lambda it: _safe_link(it["review_id"])),
    ]
    seen = 0
    for text in texts:
        for u in _urls(text):
            seen += 1
            assert hc.chat_link_problems(u) == [], (u, text[:80])
    assert seen >= 6, "the sweep found no links to check -- it would pass on anything"


def test_the_sweep_would_CATCH_an_unsafe_link_in_a_message():
    """R26 for the sweep itself: plant the old link in a real message and watch the check fail."""
    bad = f"{HOST}?r=2026-11-12T00%3A41%3A28%2B00%3A00-b5908217&v=206bae78f2&t=9b56ff732aab"
    text = hc.notification_text(ITEM, bad, "Prosper")
    found = [u for u in _urls(text) if hc.chat_link_problems(u)]
    assert found, "the sweep failed to see a planted unsafe link"


def test_the_welcome_and_fixed_messages_contain_no_link_we_construct():
    """Static domain mentions (tra.go.tz) are text, not credentials; nothing fixed in the handler carries a URL."""
    for name in ("WELCOME", "PENDING_NOTICE", "FALLBACK", "DISCLOSURE_TEXT"):
        assert not _urls(getattr(hc, name)), name


# ── the source: ONE builder ─────────────────────────────────────────────────────────────────────────
def test_the_review_host_is_only_ever_turned_into_a_link_by_the_one_guarded_builder():
    src = open(os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"), encoding="utf-8").read()
    tree = ast.parse(src)
    users = set()
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if any(isinstance(n, ast.Name) and n.id == "REVIEW_D_URL" for n in ast.walk(fn)):
                users.add(fn.name)
    assert users <= {"_draft_link", "_d_origin", "_review_urls_set"}, \
        f"a new function builds from REVIEW_D_URL -- it must go through _draft_link and the chat-safe guard: {users}"
    assert "urlencode(" not in src, "a query-string builder is back in the handler"
    draft_link = next(f for f in ast.walk(tree) if isinstance(f, ast.FunctionDef) and f.name == "_draft_link")
    assert "assert_chat_safe_link" in ast.unparse(draft_link)
