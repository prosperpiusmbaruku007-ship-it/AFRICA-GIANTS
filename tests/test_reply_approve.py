# -*- coding: utf-8 -*-
"""REPLY-TO-APPROVE (founder amendment, 2026-11-28). A roster reviewer approves by replying exactly "TUMA" to a card, quoting it. The link + Tuma-button flow is unchanged.

The founder's five plants, each run through the REAL handler: the wrong card, a decided card, a non-roster sender, "tuma tafadhali", and no quote. In every refusal NOTHING may reach the participant,
the draft must stay pending, and a roster reviewer must be told why in one line (a stranger is told nothing). Plus: exact-match edges, an unchanged-draft check, the claim lock, a double reply
(never a duplicate send), a failed send, the model-failure card, the webhook's dispatch, and an AST proof that the reply handler cannot message a participant or edit/withhold."""
import ast
import os
import sys
import time

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "chike-whatsapp"))
import handler_core as core  # noqa: E402
from test_evidence_guard import _load_mw as _load_mw_real, _run  # noqa: E402

SRC = os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py")
PROSPER = "255700000011@s.whatsapp.net"
ASHA = "255700000012@s.whatsapp.net"
STRANGER = "255700000077@s.whatsapp.net"
PARTICIPANT = "255700000099@s.whatsapp.net"
ROSTER = core.parse_roster("+255700000011:Prosper,+255700000012:Asha")
DRAFT = "Kiwango cha PAYE kwa mshahara huo ni TZS 70,000."


def _item(rid="2026-11-28T10:00:00+00:00-abcd1234", draft=DRAFT, status="pending", **kw):
    row = {"ts": "2026-11-28T10:00:00+00:00", "sender_hash": "abcd1234ef", "sender_tail": "0099", "question": "PAYE ya 800,000?", "build": "t", "model_latency_ms": 1000}
    it = core.review_item(row=row, sender=PARTICIPANT, draft=draft, engine_working="W", facts=["F"], review_id=rid, model_calls=1, guards=[])
    it["status"] = status
    it.update(kw)
    return it


# ── the pure verdict ────────────────────────────────────────────────────────────────────────────────────────
def _v(item=None, text="TUMA", quoted="M1", sender=PROSPER, push="auto", **kw):
    it = item if item is not None else _item()
    p = core.card_push_record(it, PROSPER, 1.0) if push == "auto" else push
    return core.reply_approve_verdict(roster=ROSTER, sender=sender, text=text, quoted_id=quoted, push=p, item=it, **kw)


def test_the_happy_path_approves_and_names_the_reviewer():
    v = _v()
    assert v["action"] == "approve" and v["reviewer"] == PROSPER and v["name"] == "Prosper" and v["reply"] is None


@pytest.mark.parametrize("text", ["TUMA", "tuma", "Tuma", "  TUMA  ", "\nTuma\n", "\tTUMA"])
def test_the_word_is_case_insensitive_and_trimmed(text):
    assert _v(text=text)["action"] == "approve"


@pytest.mark.parametrize("text", ["tuma tafadhali", "TUMA!", "TUMA.", "tuma 1", "ok", "sawa", "TUMAA", "tum", "TU MA", "", None, "👍", "tuma\ntuma"])
def test_PLANT_anything_but_exactly_the_word_is_ignored_with_a_reason(text):
    v = _v(text=text)
    assert v["action"] == "ignore" and v["code"] == "not_tuma" and "TUMA peke yake" in v["reply"]


def test_PLANT_no_quote_is_ignored_and_never_means_approve_the_latest():
    v = _v(quoted=None)
    assert v["action"] == "ignore" and v["code"] == "no_quote" and "nukuu" in v["reply"]
    assert _v(quoted="")["code"] == "no_quote"


def test_PLANT_a_non_roster_sender_is_ignored_silently():
    v = _v(sender=STRANGER)
    assert v["action"] == "ignore" and v["code"] == "not_roster" and v["reply"] is None and v["reviewer"] is None


def test_PLANT_an_unknown_card_id_is_ignored():
    v = _v(push=None)
    assert v["action"] == "ignore" and v["code"] == "unknown_card"
    assert _v(push={"review_id": "", "reviewer": PROSPER})["code"] == "unknown_card"


def test_PLANT_a_card_pushed_to_someone_else_is_the_wrong_card():
    it = _item()
    asha_card = core.card_push_record(it, ASHA, 1.0)
    v = core.reply_approve_verdict(roster=ROSTER, sender=PROSPER, text="TUMA", quoted_id="M1", push=asha_card, item=it)
    assert v["action"] == "ignore" and v["code"] == "wrong_reviewer"


def test_PLANT_a_card_that_points_at_a_different_draft_than_the_queue_holds_is_refused():
    it = _item()
    other = _item(rid="OTHER-ID")
    v = core.reply_approve_verdict(roster=ROSTER, sender=PROSPER, text="TUMA", quoted_id="M1", push=core.card_push_record(other, PROSPER, 1.0), item=it)
    assert v["action"] == "ignore" and v["code"] == "unknown_card"


@pytest.mark.parametrize("status", ["sent", "edited", "withheld", "retried", "auto_sent"])
def test_PLANT_a_decided_card_is_ignored_and_says_who_decided(status):
    v = _v(item=_item(status=status, decided_by_name="Asha"))
    assert v["action"] == "ignore" and v["code"] == "decided" and status in v["reply"] and "Asha" in v["reply"]


def test_a_card_whose_draft_is_gone_from_the_queue_is_refused():
    it = _item()
    v = core.reply_approve_verdict(roster=ROSTER, sender=PROSPER, text="TUMA", quoted_id="M1", push=core.card_push_record(it, PROSPER, 1.0), item=None)
    assert v["code"] == "card_gone"


def test_a_model_failure_card_cannot_be_approved_by_reply():
    fb = _item(fallback=True, draft="Samahani, tatizo la kiufundi.")
    assert core.card_push_record(fb, PROSPER, 1.0) is None, "no push record is even created for a card with no draft"
    v = core.reply_approve_verdict(roster=ROSTER, sender=PROSPER, text="TUMA", quoted_id="M1", push={"review_id": fb["review_id"], "reviewer": PROSPER, "draft_sha": core.draft_digest(fb["draft"])}, item=fb)
    assert v["code"] == "no_draft"


def test_PLANT_a_draft_changed_since_the_card_was_pushed_is_refused():
    it = _item()
    push = core.card_push_record(it, PROSPER, 1.0)
    it2 = dict(it, draft=DRAFT + " (rasimu mpya)")
    v = core.reply_approve_verdict(roster=ROSTER, sender=PROSPER, text="TUMA", quoted_id="M1", push=push, item=it2)
    assert v["action"] == "ignore" and v["code"] == "draft_changed"


def test_a_draft_claimed_by_another_reviewer_is_refused_unless_the_claim_expired():
    live = _item(claimed_by=ASHA, claimed_at="2999-01-01T00:00:00+00:00", claim_expires_at="2999-01-01T00:15:00+00:00")
    v = _v(item=live)
    assert v["code"] == "held_by_other" and "Asha" in v["reply"]
    stale = _item(claimed_by=ASHA, claimed_at="2020-01-01T00:00:00+00:00", claim_expires_at="2020-01-01T00:15:00+00:00")
    assert _v(item=stale)["action"] == "approve", "an expired claim does not block"
    assert _v(item=_item(claimed_by=PROSPER, claim_expires_at="2999-01-01T00:15:00+00:00"))["action"] == "approve", "your own claim is fine"


def test_a_lid_or_formatted_sender_still_matches_the_roster_by_digits():
    assert _v(sender="255700000011")["action"] == "approve"
    assert _v(sender="999999999999@lid")["code"] == "not_roster", "an unresolved linked-id can never be matched: fail closed"
    assert _v(sender="255700000011:12@s.whatsapp.net")["code"] == "not_roster", "a device-suffixed form is not matched either (it is not a shape the bridge forwards for a direct chat): fail closed"


def test_every_refusal_has_a_swahili_reason_of_one_short_line():
    for code, text in core.REPLY_REASONS.items():
        assert "\n" not in text and len(text) < 190, code
    assert core.REPLY_APPROVED_TEXT == "Imetumwa ✓"


# ── the classifier the webhook uses ───────────────────────────────────────────────────────────────────────
def _p(sender, text, quoted=None):
    return {"kind": "question", "sender": sender, "text": text, **({"quoted_id": quoted} if quoted else {})}


def test_classification_table():
    c = core.classify_reviewer_reply
    assert c(_p(PROSPER, "TUMA", "M1"), ROSTER, True) == "review"
    assert c(_p(PROSPER, "TUMA"), ROSTER, False) == "review", "a roster 'TUMA' is never a question to the model, quoted or not"
    assert c(_p(PROSPER, "tuma tafadhali", "M1"), ROSTER, True) == "review", "any text quoting one of our cards is a review interaction"
    assert c(_p(PROSPER, "Habari, nina swali la VAT"), ROSTER, False) == "none", "a roster number chatting normally is untouched"
    assert c(_p(PROSPER, "ok", "QUOTING-SOMETHING-ELSE"), ROSTER, False) == "none"
    assert c(_p(STRANGER, "TUMA", "M1"), ROSTER, True) == "drop"
    assert c(_p(STRANGER, "TUMA"), ROSTER, False) == "none", "a non-roster 'TUMA' is just a participant message"
    assert c(_p(STRANGER, "Habari"), ROSTER, False) == "none"


def test_parse_webhook_carries_the_quoted_id_only_when_present():
    base = {"event": "messages.received", "data": {"messages": {"key": {"remoteJid": PROSPER, "fromMe": False}, "conversation": "TUMA"}}}
    assert "quoted_id" not in core.parse_webhook(base)
    base["data"]["messages"]["quotedId"] = "3EB0AAAA"
    assert core.parse_webhook(base)["quoted_id"] == "3EB0AAAA"
    base["data"]["messages"]["quotedId"] = "   "
    assert "quoted_id" not in core.parse_webhook(base)
    base["data"]["messages"]["quotedId"] = 12345
    assert "quoted_id" not in core.parse_webhook(base), "a non-string id is ignored, never coerced"


# ── through the REAL handler ──────────────────────────────────────────────────────────────────────────────
@pytest.fixture
def mw(monkeypatch):
    m = _load_mw_real(monkeypatch)
    monkeypatch.setenv("REVIEWER_ROSTER", "+255700000011:Prosper,+255700000012:Asha")
    m.sent = []

    async def fake_send(to, text):
        m.sent.append((to, text))
        return True, None
    monkeypatch.setattr(m, "_send_once", fake_send)
    return m


def _hold(m, mid="M1", reviewer=PROSPER, **kw):
    it = _item(**kw)
    m.REVIEW_QUEUE[it["review_id"]] = it
    rec = core.card_push_record(it, reviewer, time.time())
    if rec:
        m.REVIEW_PUSHES[mid] = rec
    return it


def _reply(m, text="TUMA", quoted="M1", sender=PROSPER):
    return _run(m.review_reply_and_act.get_raw_f()(sender, text, quoted))


def _to(m, who):
    return [t for to, t in m.sent if to == who]


def test_approval_sends_the_draft_to_the_participant_once_confirms_to_the_reviewer_and_records_how(mw):
    it = _hold(mw)
    out = _reply(mw)
    assert out == {"approved": True, "code": "approve"}
    done = mw.REVIEW_QUEUE[it["review_id"]]
    assert done["status"] == "sent" and done["final"] == DRAFT and done["draft"] == DRAFT
    assert done["decided_by"] == PROSPER and done["decided_by_name"] == "Prosper" and done["decided_via"] == "whatsapp_reply"
    assert _to(mw, PARTICIPANT) == [DRAFT], "the participant gets the draft exactly once"
    assert _to(mw, PROSPER) == ["Imetumwa ✓"]
    assert done["send_state"] == "delivered" and done["send_returned_ts"] and isinstance(done["send_ms"], int), "the delivery stamp is recorded"
    row = [r for r in mw.TRANSCRIPTS.values() if r.get("kind") == "review"][0]
    assert row["decided_via"] == "whatsapp_reply" and row["decided_by_name"] == "Prosper" and row["send_returned_ts"]


def test_the_page_flow_is_unchanged_and_records_page(mw):
    it = _hold(mw)
    claimed, _ = core.claim(mw.REVIEW_QUEUE[it["review_id"]], PROSPER, ttl_s=900)
    mw.REVIEW_QUEUE[it["review_id"]] = claimed
    body, code = _run(mw._decide_and_send(it["review_id"], claimed, PROSPER, "Prosper", "send", None, None, "page"))
    assert code == 200 and body["ok"] is True
    assert mw.REVIEW_QUEUE[it["review_id"]]["decided_via"] == "page" and _to(mw, PARTICIPANT) == [DRAFT]


def _assert_refused_cleanly(m, it, who=PROSPER, told=True):
    assert m.REVIEW_QUEUE[it["review_id"]]["status"] == "pending", "the draft must stay pending"
    assert _to(m, PARTICIPANT) == [], "NOTHING reaches the participant"
    if told:
        assert len(_to(m, who)) == 1 and "Imetumwa" not in _to(m, who)[0], "the reviewer is told why, in one message, and not told it was sent"
    else:
        assert m.sent == [], "a stranger is sent nothing at all"


def test_PLANT_wrong_card_a_card_pushed_to_the_other_reviewer(mw):
    it = _hold(mw, reviewer=ASHA)
    assert _reply(mw)["code"] == "wrong_reviewer"
    _assert_refused_cleanly(mw, it)


def test_PLANT_unknown_card_id(mw):
    it = _hold(mw)
    assert _reply(mw, quoted="NOT-A-CARD")["code"] == "unknown_card"
    _assert_refused_cleanly(mw, it)


def test_PLANT_decided_card_sends_nothing_again(mw):
    it = _hold(mw, status="sent", decided_by_name="Asha", final=DRAFT)
    assert _reply(mw)["code"] == "decided"
    assert _to(mw, PARTICIPANT) == [], "approving a decided card must never send a second copy"
    assert "Asha" in _to(mw, PROSPER)[0]
    assert mw.REVIEW_QUEUE[it["review_id"]]["status"] == "sent"


def test_PLANT_non_roster_sender(mw):
    it = _hold(mw)
    assert _reply(mw, sender=STRANGER)["code"] == "not_roster"
    _assert_refused_cleanly(mw, it, told=False)


def test_PLANT_tuma_tafadhali(mw):
    it = _hold(mw)
    assert _reply(mw, text="tuma tafadhali")["code"] == "not_tuma"
    _assert_refused_cleanly(mw, it)


def test_PLANT_no_quote(mw):
    it = _hold(mw)
    assert _reply(mw, quoted=None)["code"] == "no_quote"
    _assert_refused_cleanly(mw, it)


def test_a_second_TUMA_after_the_first_does_not_send_a_duplicate(mw):
    it = _hold(mw)
    assert _reply(mw)["approved"] is True
    assert _reply(mw)["code"] == "decided"
    assert _to(mw, PARTICIPANT) == [DRAFT], "exactly one send across two replies"


def test_the_other_reviewer_cannot_approve_a_draft_the_first_reviewer_holds(mw):
    it = _hold(mw)
    held = dict(mw.REVIEW_QUEUE[it["review_id"]], claimed_by=ASHA, claimed_at="2999-01-01T00:00:00+00:00", claim_expires_at="2999-01-01T00:15:00+00:00")
    mw.REVIEW_QUEUE[it["review_id"]] = held
    assert _reply(mw)["code"] == "held_by_other"
    _assert_refused_cleanly(mw, it)


def test_a_draft_changed_after_the_card_was_pushed_is_refused_through_the_handler(mw):
    it = _hold(mw)
    mw.REVIEW_QUEUE[it["review_id"]] = dict(mw.REVIEW_QUEUE[it["review_id"]], draft=DRAFT + " Imebadilishwa.")
    assert _reply(mw)["code"] == "draft_changed"
    assert _to(mw, PARTICIPANT) == []


def test_a_failed_participant_send_is_recorded_and_the_reviewer_is_not_told_it_was_sent(mw, monkeypatch):
    it = _hold(mw)

    async def failing(to, text):
        mw.sent.append((to, text))
        return (False, "bridge HTTP 502: send_threw") if to == PARTICIPANT else (True, None)
    monkeypatch.setattr(mw, "_send_once", failing)
    out = _reply(mw)
    assert out["approved"] is True and out["code"] == "send_failed"
    done = mw.REVIEW_QUEUE[it["review_id"]]
    assert done["status"] == "sent" and done["send_state"] == "failed", "the decision is stored; the failure is visible"
    assert "Imetumwa ✓" not in _to(mw, PROSPER) and core.REPLY_REASONS["send_failed"] in _to(mw, PROSPER)


def test_an_accepted_but_not_yet_receipted_send_counts_as_sent_to_the_reviewer(mw, monkeypatch):
    it = _hold(mw)

    async def pending(to, text):
        mw.sent.append((to, text))
        return (False, f"{core.PENDING_RECEIPT}: id=ABC status=server_ack") if to == PARTICIPANT else (True, None)
    monkeypatch.setattr(mw, "_send_once", pending)
    assert _reply(mw)["code"] == "approve"
    assert "Imetumwa ✓" in _to(mw, PROSPER)


# ── the webhook's dispatch, through the real function ────────────────────────────────────────────────────────
def _payload(sender, text, quoted=None):
    msgs = {"key": {"remoteJid": sender, "fromMe": False}, "conversation": text}
    if quoted:
        msgs["quotedId"] = quoted
    return {"event": "messages.received", "data": {"messages": msgs}}


@pytest.fixture
def hook(mw, monkeypatch):
    calls = {"reply": [], "answer": [], "greet": [], "futa": []}

    class Spy:
        def __init__(self, k):
            self.k = k

        def spawn(self, *a, **kw):
            calls[self.k].append((a, kw))
    monkeypatch.setattr(mw, "review_reply_and_act", Spy("reply"))
    monkeypatch.setattr(mw, "answer_and_send", Spy("answer"))
    monkeypatch.setattr(mw, "greet_and_send", Spy("greet"))
    monkeypatch.setattr(mw, "futa_request", Spy("futa"))
    monkeypatch.delenv("WEBHOOK_TOKEN", raising=False)
    mw.REVIEW_PUSHES["M1"] = {"review_id": "r", "reviewer": PROSPER, "draft_sha": "x", "ts": time.time(), "kind": "card"}
    return mw, calls


def _fire(h, sender, text, quoted=None):
    mw, calls = h
    mw.webhook.get_raw_f()(_payload(sender, text, quoted))
    return {k: len(v) for k, v in calls.items()}


def test_dispatch_a_roster_TUMA_quoting_a_card_goes_to_the_reply_handler_and_never_to_the_model(hook):
    n = _fire(hook, PROSPER, "TUMA", "M1")
    assert n == {"reply": 1, "answer": 0, "greet": 0, "futa": 0}
    (a, kw), = hook[1]["reply"]
    assert a == (PROSPER, "TUMA", "M1") and "sender_lid" in kw


def test_dispatch_a_roster_TUMA_with_no_quote_is_still_a_review_interaction_not_a_question(hook):
    assert _fire(hook, PROSPER, "TUMA")["answer"] == 0 and hook[1]["reply"], "it would otherwise become a question to the model"


def test_dispatch_other_text_quoting_a_card_is_a_review_interaction(hook):
    n = _fire(hook, ASHA, "tuma tafadhali", "M1")
    assert n["reply"] == 1 and n["answer"] == 0


def test_dispatch_a_non_roster_sender_quoting_a_card_is_dropped(hook):
    assert _fire(hook, STRANGER, "TUMA", "M1") == {"reply": 0, "answer": 0, "greet": 0, "futa": 0}


def test_dispatch_ordinary_messages_are_untouched(hook):
    def delta(sender, text, quoted=None):
        before = {k: len(v) for k, v in hook[1].items()}
        _fire(hook, sender, text, quoted)
        return {k: len(v) - before[k] for k, v in hook[1].items()}
    assert delta(PARTICIPANT, sorted(core.GREETINGS)[0]) == {"reply": 0, "answer": 0, "greet": 1, "futa": 0}
    assert delta(PARTICIPANT, "Mshahara wa 800,000, PAYE ni kiasi gani?") == {"reply": 0, "answer": 1, "greet": 0, "futa": 0}
    assert delta(STRANGER, "TUMA") == {"reply": 0, "answer": 1, "greet": 0, "futa": 0}, "a non-roster 'TUMA' with no card is just a participant message"
    assert delta(PROSPER, "Nina swali kuhusu VAT") == {"reply": 0, "answer": 1, "greet": 0, "futa": 0}, "a roster number chatting normally is untouched"
    assert delta(PROSPER, "ok", "NOT-A-CARD") == {"reply": 0, "answer": 1, "greet": 0, "futa": 0}, "quoting something that is not one of our cards is an ordinary message"


# ── structure: what the handler can and cannot do, proved from the source ────────────────────────────────────────
def _fn(name):
    tree = ast.parse(open(SRC, encoding="utf-8").read())
    return next(n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name)


def test_the_reply_handler_can_message_only_a_reviewer_and_only_through_tell():
    fn = _fn("review_reply_and_act")
    direct = [n for n in ast.walk(fn) if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "_send_once" and not _inside(fn, n, "tell")]
    assert direct == [], "the only _send_once in this handler is the one inside tell()"
    tells = [n for n in ast.walk(fn) if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "tell"]
    assert tells, "setup: tell() is used"
    for c in tells:
        assert ast.unparse(c.args[0]).replace("'", '"') in ('verdict["reviewer"]', "number"), f"tell() may only be given the reviewer's number, got {ast.unparse(c.args[0])}"


def _inside(root, node, fname):
    for f in ast.walk(root):
        if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)) and f.name == fname and node in list(ast.walk(f)):
            return True
    return False


def test_the_reply_handler_can_only_ever_take_the_send_action():
    fn = _fn("review_reply_and_act")
    calls = [n for n in ast.walk(fn) if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "_decide_and_send"]
    assert len(calls) == 1
    args = [ast.unparse(a).replace("'", '"') for a in calls[0].args]
    assert args[4:] == ['"send"', "None", "None", '"whatsapp_reply"'], f"a reply approves; it can never edit, withhold or retry: {args}"


def test_a_decision_is_only_reached_after_the_pure_verdict_and_a_claim():
    fn = _fn("review_reply_and_act")
    body = ast.Module(body=[n for n in fn.body if not (isinstance(n, ast.Expr) and isinstance(getattr(n, "value", None), ast.Constant))], type_ignores=[])   # the docstring names these on purpose
    src = ast.unparse(body)
    assert src.index("reply_approve_verdict") < src.index("core.claim") < src.index("_decide_and_send")


def test_the_page_and_the_reply_share_one_decision_function_not_two_copies():
    def called(fn):
        return {(getattr(n.func, "attr", None) or getattr(n.func, "id", None)) for n in ast.walk(fn) if isinstance(n, ast.Call)}
    assert "_decide_and_send" in called(_fn("review_act")) and "_decide_and_send" in called(_fn("review_reply_and_act"))
    assert "apply_decision" not in called(_fn("review_act")), "review_act must not re-implement the decision"
    assert "apply_decision" not in called(_fn("review_reply_and_act")), "nor may the reply handler"
    assert "apply_decision" in called(_fn("_decide_and_send"))


def test_the_reply_handler_never_logs_the_text_or_the_draft():
    src = ast.unparse(_fn("review_reply_and_act"))
    for line in [l for l in src.splitlines() if "print(" in l]:
        for bad in ("text", "draft", "question", "sender"):
            assert bad not in line.replace("[review/reply]", ""), f"a log line names {bad}: {line}"


# ── the record: the amendment and its void-list item must stay in the file that decides what later sessions believe ──────────────────────────
def test_claude_md_records_the_amendment_and_the_void_list_item():
    md = open(os.path.join(_ROOT, "CLAUDE.md"), encoding="utf-8").read()
    assert "AMENDMENT 2026-11-28 — A REVIEWER MAY APPROVE BY A QUOTED WHATSAPP REPLY OF EXACTLY `TUMA`" in md
    assert "A person still reads the draft" in md and "nothing sends" in md and "unreviewed" in md
    for safeguard in ("quotes a specific card", "exactly `TUMA`", "unchanged since that card was pushed", "no other reviewer holds the claim", "SAME decision function as the page"):
        assert safeguard in md, safeguard
    assert "7. **a reply-approve that approves without a quote of a specific pending card" in md


def test_the_runbook_documents_every_refusal_the_code_can_give():
    rb = open(os.path.join(_ROOT, "chike-whatsapp", "SUPERVISED_PILOT_RUNBOOK.md"), encoding="utf-8").read()
    assert "### 3a. Approving by WhatsApp reply" in rb and "chike-whatsapp` first, then `chike-bridge`" in rb
    for code in ("no_quote", "not_tuma", "unknown_card", "wrong_reviewer", "decided", "draft_changed", "held_by_other", "no_draft"):
        assert code in core.REPLY_REASONS
    for fragment in ("kuinukuu", "TUMA peke yake", "si kadi", "haikutumwa kwako", "imeshaamuliwa", "rasimu imebadilika", "inashikiliwa na", "modeli ilishindwa"):
        assert fragment in rb, fragment
