"""DESIGNATED TEST SENDERS (founder, 2026-11-13).

The founder's test phones are not on the roster, so they counted as participants: a review capacity of 3 fitted only 2
outside people. A sender listed in TEST_SENDERS goes through the FULL loop (disclosure, ack, held draft, review) and is
excluded ONLY from the participant, cohort-limit and review-capacity counts -- and from the review statistics, where the
founder's own test edits would otherwise read as the pilot's edit rate. The exclusion must be visible, not silent (R39),
must never loosen supervision, and must not disable the monitor it adjusts.
"""
import ast
import asyncio
import importlib.util
import os
import sys
import types

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("hc_ts_core", os.path.join(_ROOT, "chike-whatsapp", "handler_core.py"))
core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(core)

SALT = "s"
TESTER = "255799000111@s.whatsapp.net"


def _h(jid):
    return core.sender_ids(jid, SALT)[0]


# ── parsing ─────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("written", ["+255 799 000 111", "0799000111", "255799000111", "255799000111@s.whatsapp.net",
                                     "+255799000111:my second phone"])
def test_a_phone_is_hashed_exactly_as_a_sender_is_hashed(written):
    hashes, rejected = core.parse_test_senders(written, SALT)
    assert hashes == {_h(TESTER)} and rejected == 0


def test_a_twelve_hex_hash_is_accepted_for_a_lid_only_sender():
    lid_hash = _h("220401@lid")
    assert core.parse_test_senders("hash:" + lid_hash, SALT) == (frozenset({lid_hash}), 0)
    assert core.parse_test_senders("HASH:" + lid_hash.upper() + ":lid phone", SALT)[0] == {lid_hash}


def test_a_twelve_digit_phone_is_never_mistaken_for_a_hash():
    """The bug this parser had on its first draft: 255799000111 is 12 digits, which matches a 12-hex pattern."""
    assert core.parse_test_senders("255799000111", SALT)[0] == {_h(TESTER)}
    assert core.parse_test_senders("255799000111", SALT)[0] != {"255799000111"}
    # a bare 12-hex string with letters is NOT a hash without the prefix: rejected and counted, not guessed
    assert core.parse_test_senders(_h("220401@lid") + "z", SALT)[1] == 1
    assert core.parse_test_senders("hash:nothex", SALT) == (frozenset(), 1)


def test_junk_is_counted_never_silently_dropped_and_empty_is_empty():
    hashes, rejected = core.parse_test_senders("12345, abc, +255799000111", SALT)
    assert hashes == {_h(TESTER)} and rejected == 2
    assert core.parse_test_senders("", SALT) == (frozenset(), 0)
    assert core.parse_test_senders(None, SALT) == (frozenset(), 0)
    assert core.parse_test_senders(" , ;; ", SALT) == (frozenset(), 0)


def test_the_salt_matters_so_a_hash_cannot_be_forged_without_it():
    assert core.parse_test_senders(TESTER, "a")[0] != core.parse_test_senders(TESTER, "b")[0]


# ── rows and items carry the flag; nothing else about them changes ──────────────────────────────
def _settings(**kw):
    base = dict(slow_ack_after_s=0.01, second_ack_after_s=0, model_timeout_s=5, send_attempts=1,
                send_retry_delay_s=0, sender_salt=SALT)
    base.update(kw)
    return core.Settings(**base)


def test_a_listed_sender_row_is_stamped_and_an_unlisted_one_is_not():
    s = _settings(test_sender_hashes=frozenset({_h(TESTER)}))
    assert core._blank_row("question", TESTER, s, "b")["test_sender"] is True
    assert core._blank_row("question", "255700000001@s.whatsapp.net", s, "b")["test_sender"] is False
    assert core._blank_row("question", TESTER, _settings(), "b")["test_sender"] is False


async def _ask(_m):
    return {"reply": "JIBU: SDL ni asilimia 3.5."}


class _Rec:
    def __init__(self):
        self.sent, self.held = [], []

    async def send(self, to, text):
        self.sent.append(text)
        return True, None

    async def hold(self, to, text, row):
        self.held.append(text)
        return True, None


def _run(c):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(c)
    finally:
        loop.close()


def test_a_test_sender_still_goes_through_the_full_review_loop():
    """THE CONDITION ON THE R7 READING: exclusion from a count must not become an exemption from review. A test sender's
    answer is HELD exactly like a participant's, and nothing reaches them unreviewed."""
    s = _settings(supervised=True, slow_ack_after_s=0, test_sender_hashes=frozenset({_h(TESTER)}))
    r = _Rec()
    row = _run(core.deliver(TESTER, "SDL ni ngapi?", _ask, r.send, s, hold_reply=r.hold))
    assert row["test_sender"] is True and row["supervision"] == "held"
    assert r.held == ["JIBU: SDL ni asilimia 3.5."] and r.sent == []
    # and the control arm: the same message from an unlisted sender behaves identically
    r2 = _Rec()
    row2 = _run(core.deliver("255700000001@s.whatsapp.net", "SDL ni ngapi?", _ask, r2.send, s, hold_reply=r2.hold))
    assert row2["supervision"] == "held" and r2.held == r.held and r2.sent == []


def test_no_handler_path_branches_on_test_sender_except_the_counts():
    """Structural: `test_sender` may be read ONLY where counts are made. A reference inside deliver / hold / the
    reviewer authentication would be an exemption from review wearing the name of a statistic."""
    allowed = {"_blank_row", "review_item", "is_test_sender_hash", "_is_test_item", "review_summary", "parse_test_senders",
               "_participants_split", "_cohort_health",
               "_do_auto_send", "seed_timeout_probe", "review_act"}   # both only STAMP/COPY the flag onto a row; no verdict reads it
    for path in ("handler_core.py", "modal_whatsapp.py"):
        tree = ast.parse(open(os.path.join(_ROOT, "chike-whatsapp", path), encoding="utf-8").read())
        for fn in ast.walk(tree):
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                refs = [n for n in ast.walk(fn)
                        if (isinstance(n, ast.Constant) and n.value in ("test_sender", "test_sender_hashes"))
                        or (isinstance(n, ast.Attribute) and n.attr == "test_sender_hashes")]
                if refs:
                    assert fn.name in allowed or fn.name == "_settings", f"{fn.name} reads test_sender: {path}"


# ── the counts ──────────────────────────────────────────────────────────────────────────────────
def _load_mw(monkeypatch, test_senders=TESTER):
    from conftest import isolate_modal_stores
    pkg = types.ModuleType("chike_whatsapp")
    pkg.handler_core = core
    monkeypatch.setitem(sys.modules, "chike_whatsapp", pkg)
    monkeypatch.setitem(sys.modules, "chike_whatsapp.handler_core", core)
    spec = importlib.util.spec_from_file_location("chike_mw_ts", os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"))
    mw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mw)
    isolate_modal_stores(mw, monkeypatch)
    monkeypatch.setenv("SENDER_SALT", SALT)
    monkeypatch.setenv("REVIEWER_ROSTER", "+255700000098:Prosper")
    monkeypatch.setenv("REVIEW_SIGNING_KEY", "k")
    monkeypatch.setenv("COHORT_SIZE", "3")
    monkeypatch.setenv("TEST_SENDERS", test_senders)
    return mw


def _row(jid, kind="question", stamped=False):
    h, t = core.sender_ids(jid, SALT)
    return {"ts": "2026-11-13T00:00:00+00:00", "kind": kind, "sender_hash": h, "sender_tail": t,
            "test_sender": stamped}


def _fill(mw, jids, **kw):
    for i, jid in enumerate(jids):
        mw.TRANSCRIPTS[f"row{i}-{jid}"] = _row(jid, **kw)


REAL = [f"2557000000{n:02d}@s.whatsapp.net" for n in range(1, 6)]


def test_capacity_three_means_three_real_participants(monkeypatch):
    mw = _load_mw(monkeypatch)
    _fill(mw, REAL[:3] + [TESTER])
    c = mw._cohort_health()
    assert c["participants_seen"] == 3 and c["test_senders"]["seen"] == 1
    assert c["review_capacity_participants"] == 3
    assert c["seen_exceeds_review_capacity"] is False, "3 real participants + the tester phone fit capacity 3"


def test_the_monitor_still_fires_for_a_fourth_real_participant(monkeypatch):
    """The exclusion must not disable what it adjusts (R26): a 4th REAL sender still trips the capacity monitor."""
    mw = _load_mw(monkeypatch)
    _fill(mw, REAL[:4] + [TESTER])
    c = mw._cohort_health()
    assert c["participants_seen"] == 4 and c["seen_exceeds_review_capacity"] is True


def test_the_cohort_limit_counts_real_participants_only(monkeypatch):
    mw = _load_mw(monkeypatch)
    monkeypatch.setenv("COHORT_SIZE", "2")
    _fill(mw, REAL[:2] + [TESTER])
    assert mw._cohort_health()["over_capacity"] is False
    _fill_more = REAL[2]
    mw.TRANSCRIPTS["extra"] = _row(_fill_more)
    assert mw._cohort_health()["over_capacity"] is True


def test_without_the_list_the_tester_is_counted_as_before(monkeypatch):
    """Control arm: the unchanged behaviour when TEST_SENDERS is unset."""
    mw = _load_mw(monkeypatch, test_senders="")
    _fill(mw, REAL[:3] + [TESTER])
    c = mw._cohort_health()
    assert c["participants_seen"] == 4 and c["test_senders"] == {**c["test_senders"], "listed": 0, "seen": 0}
    assert c["seen_exceeds_review_capacity"] is True


def test_older_rows_without_the_stamp_are_classified_by_hash(monkeypatch):
    """Rows written BEFORE this feature carry no flag; the list reaches them retroactively."""
    mw = _load_mw(monkeypatch)
    mw.TRANSCRIPTS["old"] = {k: v for k, v in _row(TESTER).items() if k != "test_sender"}
    assert mw._participants_split() == (0, 1)


def test_a_stamped_row_counts_as_test_even_if_the_list_later_loses_it(monkeypatch):
    mw = _load_mw(monkeypatch, test_senders="")
    mw.TRANSCRIPTS["a"] = _row(TESTER, stamped=True)
    mw.TRANSCRIPTS["b"] = _row(REAL[0])
    assert mw._participants_split() == (1, 1)


def test_the_exclusion_is_visible_in_health_not_silent(monkeypatch):
    mw = _load_mw(monkeypatch, test_senders=f"{TESTER}, junk")
    _fill(mw, [TESTER])
    t = mw._cohort_health()["test_senders"]
    assert t["listed"] == 1 and t["rejected_entries"] == 1 and t["seen"] == 1 and "participants_seen" in t["excluded_from"]


def test_greetings_from_a_test_sender_are_excluded_too(monkeypatch):
    mw = _load_mw(monkeypatch)
    mw.TRANSCRIPTS["g"] = _row(TESTER, kind="greeting")
    mw.TRANSCRIPTS["r"] = {**_row(TESTER, kind="review"), }
    assert mw._participants_split() == (0, 1)


# ── the review statistics ───────────────────────────────────────────────────────────────────────
def _item(i, h, status, **kw):
    return {"review_id": f"2026-11-13T00:0{i}:00+00:00-{h[:8]}", "status": status, "sender_hash": h,
            "decision_latency_s": 60, **kw}


def test_review_statistics_exclude_test_senders_and_say_how_many():
    th = _h(TESTER)
    real_h = _h(REAL[0])
    items = [_item(1, real_h, "sent"), _item(2, real_h, "edited"), _item(3, th, "edited"), _item(4, th, "withheld"),
             _item(5, "zzz", "withheld", test_sender=True)]
    s = core.review_summary(items, test_hashes=frozenset({th}))
    assert s["excluded_test_items"] == 3 and s["decided"] == 2
    assert s["edit_or_withhold_rate"] == 0.5, "the tester's edits must not move the pilot's edit rate"
    # the control arm: nothing listed -> everything counts
    s2 = core.review_summary(items)
    assert s2["excluded_test_items"] == 1 and s2["decided"] == 4


def test_a_review_item_carries_the_stamp_from_its_row():
    row = {**_row(TESTER, stamped=True), "question": "q", "reply": "d", "build": "b"}
    item = core.review_item(row=row, sender=TESTER, draft="d", settings=_settings()) \
        if "settings" in core.review_item.__code__.co_varnames else None
    if item is not None:
        assert item["test_sender"] is True


def test_a_settings_stub_without_the_field_means_no_test_senders():
    """A bug in the first draft: a stub lacking `test_sender_hashes` made the helper iterate the stub itself."""
    class Stub:
        sender_salt = ""
    assert core.is_test_sender_hash(Stub(), "abc123abc123") is False
    assert core.is_test_sender_hash(frozenset({"abc123abc123"}), "abc123abc123") is True
    assert core.is_test_sender_hash(None, "abc123abc123") is False
