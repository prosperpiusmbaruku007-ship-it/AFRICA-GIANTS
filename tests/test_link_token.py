"""ONE opaque path token instead of three joined query parameters, and the duplicate flag (founder, 2026-11-12).

Four real review links failed authentication in transit. A link of `?r=<id with + and :>&v=…&t=…` is long and punctuated
-- `&`, `=`, `+`, `%3A` are what link detection, copy-paste and in-app browsers cut, decode or 'clean'. The token is one
unbroken run of [0-9a-z2-7]. These tests pin: it round-trips, EVERY truncation fails, a forged one fails, the old query
form still opens, and a duplicate is flagged.
"""
import asyncio
import importlib.util
import os
import re
import sys
import types

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("hc_tok", os.path.join(_ROOT, "chike-whatsapp", "handler_core.py"))
hc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hc)

KEY = "test-key"
NUMBER = "255712615913@s.whatsapp.net"
OTHER = "255700000022@s.whatsapp.net"
IDS = ["2026-11-12T00:41:28+00:00-b5908217", "2026-11-12T00:42:57+00:00-b5908217",
       "2026-11-11T20:54:51+00:00-b5908217", "TEST-1791721161A"]


def _settings(*numbers):
    return hc.Settings(review_signing_key=KEY, roster=tuple((n, "R") for n in (numbers or (NUMBER,))))


# ── the envelope ─────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("rid", IDS)
def test_the_token_is_one_unbroken_lowercase_run_with_nothing_to_cut(rid):
    t = hc.review_link_token(KEY, rid, NUMBER)
    assert re.fullmatch(r"[0-9a-z2-7]+", t), t
    assert not any(c in t for c in "&=+%?:/.-_ "), "nothing a client can split, decode or strip"
    assert t == t.lower(), "a client that case-folds a path must not be able to corrupt it"


@pytest.mark.parametrize("rid", IDS)
def test_the_token_round_trips_and_authenticates_with_the_SAME_signing(rid):
    t = hc.review_link_token(KEY, rid, NUMBER)
    got_id, handle, sig = hc.parse_review_link_token(t)
    assert got_id == rid
    assert handle == hc.reviewer_id(KEY, NUMBER) and sig == hc.review_token(KEY, rid, NUMBER)
    assert hc.authenticate_reviewer(_settings(), got_id, handle, sig) == (NUMBER, "R")


def test_uppercase_and_surrounding_whitespace_are_tolerated():
    t = hc.review_link_token(KEY, IDS[0], NUMBER)
    for variant in (t.upper(), "  " + t + "\n", t.upper() + " "):
        got = hc.parse_review_link_token(variant)
        assert got and hc.authenticate_reviewer(_settings(), *[got[0], got[1], got[2]])


@pytest.mark.parametrize("rid", IDS[:2])
def test_EVERY_truncation_fails_none_authenticates_as_anything(rid):
    """The founder's property: it 'can't be partially cut'. For every cut point, the token either does not parse or
    parses to something that does NOT authenticate -- as this draft or any other."""
    t = hc.review_link_token(KEY, rid, NUMBER)
    for n in range(1, len(t)):
        parsed = hc.parse_review_link_token(t[:n])
        if parsed is None:
            continue
        assert hc.authenticate_reviewer(_settings(), *parsed) is None, f"a {n}-char prefix authenticated"


def test_a_forged_signature_a_swapped_handle_and_a_swapped_id_all_fail():
    rid = IDS[0]
    t = hc.review_link_token(KEY, rid, NUMBER)
    handle, sig, idpart = t[:10], t[10:42], t[42:]
    forged = handle + "0" * 32 + idpart
    assert hc.authenticate_reviewer(_settings(), *hc.parse_review_link_token(forged)) is None
    other_id = hc.review_link_token(KEY, IDS[1], NUMBER)[42:]
    assert hc.authenticate_reviewer(_settings(), *hc.parse_review_link_token(handle + sig + other_id)) is None
    wrong_handle = hc.reviewer_id(KEY, OTHER)
    assert hc.authenticate_reviewer(_settings(), *hc.parse_review_link_token(wrong_handle + sig + idpart)) is None
    # a token minted under ANOTHER key never authenticates under this one
    foreign = hc.review_link_token("someone-elses-key", rid, NUMBER)
    assert hc.authenticate_reviewer(_settings(), *hc.parse_review_link_token(foreign)) is None


@pytest.mark.parametrize("junk", [None, "", "favicon.ico", "robots.txt", "x" * 30, "../etc/passwd", "0" * 42,
                                  "0" * 42 + "!!!!!!!!", "g" * 60, "<script>"])
def test_junk_never_parses_and_never_raises(junk):
    assert hc.parse_review_link_token(junk) is None


def test_no_two_drafts_share_a_token_and_a_reviewer_cannot_use_anothers():
    a = hc.review_link_token(KEY, IDS[0], NUMBER)
    b = hc.review_link_token(KEY, IDS[1], NUMBER)
    c = hc.review_link_token(KEY, IDS[0], OTHER)
    assert len({a, b, c}) == 3
    got = hc.parse_review_link_token(c)
    assert hc.authenticate_reviewer(_settings(NUMBER, OTHER), *got) == (OTHER, "R")
    assert hc.authenticate_reviewer(_settings(NUMBER), *got) is None, "not on THIS roster"


# ── the routes: the real ASGI app ────────────────────────────────────────────────────────────────
def _load_mw(monkeypatch):
    from conftest import isolate_modal_stores
    for k, v in {"REVIEW_D_URL": "https://d.example", "REVIEW_CLAIM_URL": "https://c.example",
                 "REVIEW_ACT_URL": "https://a.example"}.items():
        monkeypatch.setenv(k, v)
    pkg = types.ModuleType("chike_whatsapp")
    pkg.handler_core = hc
    monkeypatch.setitem(sys.modules, "chike_whatsapp", pkg)
    monkeypatch.setitem(sys.modules, "chike_whatsapp.handler_core", hc)
    spec = importlib.util.spec_from_file_location("chike_mw_tok", os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"))
    mw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mw)
    isolate_modal_stores(mw, monkeypatch)
    monkeypatch.setenv("SENDER_SALT", "salt")
    monkeypatch.setenv("REVIEWER_ROSTER", "+255712615913:Prosper")
    monkeypatch.setenv("REVIEW_SIGNING_KEY", KEY)
    return mw


def _client(mw):
    from fastapi.testclient import TestClient
    return TestClient(mw.d.get_raw_f()())


def _store(mw, rid, **kw):
    base = {"review_id": rid, "ts_held": rid[:25], "question": "Mauzo yangu ni milioni 250. Je, ni lazima nisajili VAT",
            "draft": "Ndiyo.", "status": "pending", "sender_tail": "5913", "sender_hash": "abc", "facts": ["F"],
            "engine_working": "W", "answer_path": "engine:vat_registration"}
    base.update(kw)
    mw.REVIEW_QUEUE[rid] = base
    return base


def test_the_path_link_opens_the_draft_and_embeds_its_credentials_for_the_page_js(monkeypatch):
    mw = _load_mw(monkeypatch)
    _store(mw, IDS[0])
    number = mw._settings().roster[0][0]
    resp = _client(mw).get("/" + hc.review_link_token(KEY, IDS[0], number))
    assert resp.status_code == 200 and "Ndiyo." in resp.text
    assert "location.search" not in resp.text, "the JS must not read a query string that no longer exists"
    assert IDS[0] in resp.text and hc.reviewer_id(KEY, number) in resp.text
    assert hc.review_token(KEY, IDS[0], number) in resp.text


def test_the_OLD_query_link_still_opens_so_links_already_on_a_phone_keep_working(monkeypatch):
    from urllib.parse import urlencode
    mw = _load_mw(monkeypatch)
    _store(mw, IDS[0])
    number = mw._settings().roster[0][0]
    q = urlencode({"r": IDS[0], "v": hc.reviewer_id(KEY, number), "t": hc.review_token(KEY, IDS[0], number)})
    resp = _client(mw).get("/?" + q)
    assert resp.status_code == 200 and "Ndiyo." in resp.text


def test_a_truncated_or_forged_path_link_gets_the_invalid_link_page_never_not_found(monkeypatch, capsys):
    mw = _load_mw(monkeypatch)
    _store(mw, IDS[0])
    number = mw._settings().roster[0][0]
    t = hc.review_link_token(KEY, IDS[0], number)
    for bad in (t[:-3], t[:60], t[:42], "0" * len(t), t.replace(t[10:42], "0" * 32)):
        resp = _client(mw).get("/" + bad)
        assert resp.status_code == 404
        assert "not found" not in resp.text.lower() and "HAIMAANISHI rasimu imepotea" in resp.text
    out = capsys.readouterr().out
    assert "reason=auth_failed via=path" in out or "reason=malformed_token via=path" in out
    assert t not in out and hc.review_token(KEY, IDS[0], number) not in out, "a credential reached the log"


def test_crawler_noise_gets_the_same_page_and_is_not_logged_as_a_link_failure(monkeypatch, capsys):
    mw = _load_mw(monkeypatch)
    for path in ("/favicon.ico", "/robots.txt"):
        assert _client(mw).get(path).status_code == 404
    assert "reason=" not in capsys.readouterr().out


def test_a_path_link_for_a_draft_that_is_gone_says_so_only_when_authenticated(monkeypatch):
    mw = _load_mw(monkeypatch)                                   # nothing stored
    number = mw._settings().roster[0][0]
    resp = _client(mw).get("/" + hc.review_link_token(KEY, IDS[0], number))
    assert resp.status_code == 404 and "Rasimu haipatikani" in resp.text


# ── duplicates ───────────────────────────────────────────────────────────────────────────────────
Q2 = "Mauzo yangu ni milioni 250 kwa mwaka. Je, ni lazima nisajili VAT"
Q3 = "Mauzo yangu ni milioni 250 kwa mwaka. Je, ni lazima nijiandikishe VAT"


def _it(rid, q, sender="s1", status="pending"):
    return {"review_id": rid, "question": q, "sender_hash": sender, "status": status}


@pytest.mark.parametrize("a,b,dup", [
    (Q2, Q2, True),                                            # the re-send: identical
    (Q2, Q3, True),                                            # the pair that differs by ONE word
    (Q2, "Mauzo yangu ni milioni 250 kwa mwaka. Je, ni lazima nisajili VAT?", True),   # punctuation only
    (Q2, "Faini ya kuchelewa kuwasilisha return ya PAYE ni kiasi gani?", False),
    (Q2, "SDL ni asilimia ngapi?", False),
    (Q2, "", False),
])
def test_near_identical_questions_from_one_sender_are_flagged(a, b, dup):
    assert bool(hc.pending_duplicates(_it("r1", a), [_it("r1", a), _it("r2", b)])) is dup


def test_only_PENDING_drafts_from_the_SAME_sender_count_and_a_draft_is_not_its_own_duplicate():
    me = _it("r1", Q2)
    assert hc.pending_duplicates(me, [me]) == []
    assert hc.pending_duplicates(me, [me, _it("r2", Q2, sender="someone-else")]) == [], "another participant"
    assert hc.pending_duplicates(me, [me, _it("r2", Q2, status="sent")]) == [], "already decided"
    assert hc.pending_duplicates(me, [me, _it("r2", Q2, status="withheld")]) == []
    assert hc.pending_duplicates(me, [me, _it("r2", Q2), _it("r3", Q3)]) == ["r2", "r3"]


def test_the_push_carries_the_duplicate_warning_only_when_there_is_one():
    base = {"review_id": "r1", "question": Q2, "draft": "Ndiyo.", "sender_tail": "5913", "facts": ["F"],
            "engine_working": "W", "answer_path": "engine:vat_registration"}
    quiet = hc.notification_text(base, "https://x/abc", "Prosper")
    loud = hc.notification_text(dict(base, duplicates_pending=["r0"]), "https://x/abc", "Prosper")
    assert "MARUDIO" not in quiet and "DUPLICATE" not in quiet
    assert hc.DUPLICATE_WARNING_SW.format(n=1) in loud and hc.DUPLICATE_WARNING_EN.format(n=1) in loud
    assert loud.index("MARUDIO") < loud.index("SWALI:"), "before the question"


def test_both_cards_flag_a_live_duplicate_and_the_reviewers_own_page_is_computed_against_the_queue(monkeypatch):
    mw = _load_mw(monkeypatch)
    a = _store(mw, IDS[0], question=Q2)
    b = _store(mw, IDS[1], question=Q3)
    assert "MARUDIO" in mw._duplicate_banner(a, [a, b]) and "DUPLICATE" in mw._duplicate_banner(b, [a, b])
    assert mw._duplicate_banner(a, [a]) == ""
    number = mw._settings().roster[0][0]
    page = _client(mw).get("/" + hc.review_link_token(KEY, IDS[1], number)).text
    assert "MARUDIO" in page and page.index("MARUDIO") < page.index("<textarea"), "above the draft"
    # a pair flags BOTH ways: the other draft's own page warns about this one too
    other = _client(mw).get("/" + hc.review_link_token(KEY, IDS[0], number)).text
    assert "MARUDIO" in other and other.index("MARUDIO") < other.index("<textarea")
    # and a draft with NO near-identical pending sibling is not flagged
    _store(mw, "2026-11-12T01:00:00+00:00-b5908217", question="SDL ni asilimia ngapi?")
    solo = _client(mw).get("/" + hc.review_link_token(KEY, "2026-11-12T01:00:00+00:00-b5908217", number)).text
    assert "MARUDIO" not in solo


def test_once_one_of_a_pair_is_decided_the_other_is_no_longer_flagged(monkeypatch):
    mw = _load_mw(monkeypatch)
    a = _store(mw, IDS[0], question=Q2)
    b = _store(mw, IDS[1], question=Q3)
    b["status"] = "withheld"
    mw.REVIEW_QUEUE[IDS[1]] = b
    assert mw._duplicate_banner(a, [a, b]) == ""


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def test_a_re_sent_question_through_the_real_handler_marks_the_second_draft_and_its_push(monkeypatch):
    mw = _load_mw(monkeypatch)
    monkeypatch.setenv("SUPERVISED", "1")
    monkeypatch.setenv("DISCLOSURE", "off")
    pushes = []

    async def fake_send(to, text):
        pushes.append(text)
        return True, None
    monkeypatch.setattr(mw, "_send_once", fake_send)

    class _Remote:
        @staticmethod
        async def aio(message):
            return {"reply": "Ndiyo.", "working": "W", "facts": ["F"], "path": "engine:vat_registration"}

    class _Model:
        run = types.SimpleNamespace(remote=_Remote)
    monkeypatch.setattr(mw, "ChikeModel", _Model)
    sender = "255700000099@s.whatsapp.net"
    import time as _t
    _run(mw.answer_and_send.get_raw_f()(sender, Q2))
    _t.sleep(1.1)                                              # review ids are second-resolution
    _run(mw.answer_and_send.get_raw_f()(sender, Q3))
    items = sorted(mw.REVIEW_QUEUE.values(), key=lambda i: i["ts_held"])
    assert len(items) == 2
    assert items[0].get("duplicates_pending") == [] and items[1]["duplicates_pending"] == [items[0]["review_id"]]
    assert "MARUDIO" not in pushes[0] and "MARUDIO" in pushes[1]


def test_a_RENOTIFICATION_of_a_draft_held_before_the_flag_existed_still_warns_about_its_duplicate(monkeypatch):
    """The three drafts pending when the flag shipped have NO stored `duplicates_pending`. The push must compute it now."""
    mw = _load_mw(monkeypatch)
    pushes = []

    async def fake_send(to, text):
        pushes.append(text)
        return True, None
    monkeypatch.setattr(mw, "_send_once", fake_send)
    a = _store(mw, IDS[0], question=Q2, sender_hash="s1")
    b = _store(mw, IDS[1], question=Q3, sender_hash="s1")
    assert "duplicates_pending" not in a and "duplicates_pending" not in b
    _run(mw._notify_reviewers(a, renotify=True))
    assert "MARUDIO" in pushes[-1] and "DUPLICATE" in pushes[-1]
    assert pushes[-1].index("MARUDIO") < pushes[-1].index("SWALI:")
    # a draft with no pending sibling is NOT cried-wolf, and a decided sibling stops flagging
    c = _store(mw, "2026-11-12T01:00:00+00:00-b5908217", question="SDL ni asilimia ngapi?", sender_hash="s1")
    _run(mw._notify_reviewers(c, renotify=True))
    assert "MARUDIO" not in pushes[-1]
    b["status"] = "withheld"
    mw.REVIEW_QUEUE[IDS[1]] = b
    _run(mw._notify_reviewers(a, renotify=True))
    assert "MARUDIO" not in pushes[-1]
