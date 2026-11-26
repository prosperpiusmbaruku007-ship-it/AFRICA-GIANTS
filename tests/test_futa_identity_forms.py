# -*- coding: utf-8 -*-
"""FUTA ACROSS IDENTITY FORMS (2026-11-26). A participant's records are keyed by a salted hash of the exact string the sender arrived as, so the same
person stored as 255..., +255..., 0..., with a @c.us suffix, or under a linked-ID is several different hashes. A deletion that handled only the request's
own string would leave the rest behind and still say "done".

The residue scan here is INDEPENDENT of the code under test: it derives the forms and hashes itself, so a purge that forgets a form cannot also forget to
look for it. Plants: a purge limited to the primary hash leaves residue and "done" is withheld; a linked-ID with no recorded pair is NOT found (pinned,
so the documented limitation stays documented); the pair store is deleted with the person.
"""
import json
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "chike-whatsapp"))
import handler_core as core  # noqa: E402
from test_evidence_guard import _run, hc  # noqa: E402
from test_futa import mw, _futa_all, A, B, A_DIGITS, B_DIGITS  # noqa: E402,F401  (the fixture seeds both senders under their primary form)
from test_archive_core import item, NOW  # noqa: E402

LID = "9988776655@lid"
UNKNOWN_LID = "1122334455@lid"
FORMS_A = ["255700000099", "+255700000099", "0700000099", "255700000099@c.us", "+255700000099@s.whatsapp.net", "0700000099@s.whatsapp.net"]
ALL_A_STRINGS = FORMS_A + [A, LID]


def hash_of(s):
    return core.sender_ids(s, "salt")[0]


def _seed_forms(m):
    """One transcript row, one review item, one disclosure key and one ARCHIVED item for A under every other form and under the linked-ID."""
    for i, f in enumerate(FORMS_A + [LID]):
        h = hash_of(f)
        m.TRANSCRIPTS[f"2026-11/form-{h}.json"] = {"ts": "2026-11-26T08:00:00+00:00", "kind": "question", "sender_hash": h, "sender_tail": "0099", "question": f"FORM-{i}"}
        rid = f"2026-11-26T08:00:0{i % 10}+00:00-{h[:8]}"
        m.REVIEW_QUEUE[rid] = {"review_id": rid, "status": "pending", "sender": f, "sender_hash": h, "question": "q", "ts_held": "2026-11-26T08:00:00+00:00"}
        m.DISCLOSURES[h] = {"state": "delivered"}
        old = item(50 + i, "sent", days_ago=9, sh=h)
        core.archive_run(review_items={old["review_id"]: old}, transcripts={}, store=m.vol, signing_key="k", now=NOW)
    m.BRIDGE_LEDGER["LED-DEV"] = {"to": "255700000099:12@s.whatsapp.net", "ts": 1, "rank": 3}        # a device-suffixed address
    m.BRIDGE_LEDGER["LED-LOCAL"] = {"to": "0700000099@s.whatsapp.net", "ts": 1, "rank": 3}
    assert m._record_alias(A, LID) is True


def residue(m):
    """{what: [...]}: every Dict record and archive file that still mentions this person under ANY form, found without using the code under test."""
    hashes = {hash_of(s) for s in ALL_A_STRINGS}
    needles = hashes | {"255700000099", "0700000099"}
    dict_hits = []
    for name, d in m._futa_stores().items():
        for k in list(d.keys()):
            try:
                v = d[k]
            except Exception:                                        # noqa: BLE001
                continue
            if any(n in str(k) for n in needles) or any(n in json.dumps(v, default=str) for n in needles):
                dict_hits.append((name, str(k)[:40]))
    arch_hits = []
    for dp, _, fs in os.walk(m.vol.root):
        for f in fs:
            p = os.path.join(dp, f)
            if os.sep + "tombstones" + os.sep in p:
                continue
            if any(n in p or n in open(p, "rb").read().decode("utf-8", "replace") for n in needles):
                arch_hits.append(p)
    return {"dicts": dict_hits, "archive": arch_hits}


@pytest.fixture
def seeded(mw):
    _seed_forms(mw)
    return mw


# ── pure ─────────────────────────────────────────────────────────────────────────────────────────────────────
def test_every_form_of_a_number_normalises_to_the_same_canonical_digits():
    for f in FORMS_A + ["255700000099:12@s.whatsapp.net", A]:
        assert core.canonical_tz_digits(f) == "255700000099", f
    assert core.canonical_tz_digits("0799000111") == B_DIGITS and core.canonical_tz_digits(B) == B_DIGITS
    assert core.canonical_tz_digits("0700000099") != core.canonical_tz_digits(B), "two different people stay different"
    assert core.canonical_tz_digits("") == "" and core.canonical_tz_digits(None) == ""


def test_the_form_list_has_every_base_and_suffix_and_nothing_for_an_empty_number():
    forms = core.futa_identity_forms(A)
    assert len(forms) == 9 and set(FORMS_A) <= set(forms) and A in forms
    assert core.futa_identity_forms("") == [] and core.futa_identity_forms("abc") == []


def test_alias_hashes_follow_a_pair_from_either_end_and_ignore_junk_keys():
    ph, lh = hash_of(A), hash_of(LID)
    keys = [core.alias_pair_key(ph, lh), "not-a-pair", "xx:yy"]
    assert core.alias_hashes(keys, [ph]) == {lh} and core.alias_hashes(keys, [lh]) == {ph} and core.alias_hashes(keys, ["cccccccccccc"]) == set()


# ── through the real functions ───────────────────────────────────────────────────────────────────────────────
def test_before_the_deletion_the_independent_scan_finds_the_person_under_every_form(seeded):
    r = residue(seeded)
    transcripts = {k for n, k in r["dicts"] if n == "transcripts"}
    for f in FORMS_A + [LID]:
        assert any(hash_of(f) in k for k in transcripts), f"positive control: the scan finds a transcript under {f!r}"
    assert len(r["archive"]) >= len(FORMS_A) + 1, "and an archived record under each form and the linked-ID"


def test_a_confirmed_deletion_removes_the_person_under_every_form_and_the_linked_id_and_nobody_else(seeded):
    b_before = [h for h in seeded.TRANSCRIPTS.keys() if hash_of(B) in str(h)]
    out = _futa_all(seeded, A)
    assert out["status"] == "done", out
    assert residue(seeded) == {"dicts": [], "archive": []}, residue(seeded)
    assert [h for h in seeded.TRANSCRIPTS.keys() if hash_of(B) in str(h)] == b_before and b_before, "the other person is untouched"
    assert seeded.sent[-1] == core.FUTA_DONE_TEXT


@pytest.mark.parametrize("form", FORMS_A + [LID])
def test_each_single_form_is_deleted(mw, form):
    """One form at a time, so a failure names the form that leaks."""
    h = hash_of(form)
    mw.TRANSCRIPTS[f"2026-11/solo-{h}.json"] = {"ts": "2026-11-26T08:00:00+00:00", "kind": "question", "sender_hash": h, "question": "SOLO"}
    mw.DISCLOSURES[h] = {"state": "delivered"}
    assert mw._record_alias(A, LID) is True
    assert _futa_all(mw, A)["status"] == "done"
    assert f"2026-11/solo-{h}.json" not in mw.TRANSCRIPTS and h not in mw.DISCLOSURES, f"records under {form!r} survived"


def test_device_suffixed_and_local_format_ledger_addresses_are_purged_by_canonical_digits(seeded):
    _futa_all(seeded, A)
    assert "LED-DEV" not in seeded.BRIDGE_LEDGER and "LED-LOCAL" not in seeded.BRIDGE_LEDGER


def test_every_form_hash_gets_a_tombstone_so_none_can_be_re_archived(seeded):
    _futa_all(seeded, A)
    for s in [A] + FORMS_A + [LID]:
        assert core.is_tombstoned(seeded.vol, hash_of(s)), s


def test_PLANT_a_purge_that_handles_only_the_primary_hash_leaves_residue_and_done_is_withheld(seeded, monkeypatch):
    real = core.futa_purge
    monkeypatch.setattr(hc, "futa_purge", lambda stores, hashes, digits: real(stores, list(hashes)[:1], ""))       # the pre-fix behaviour
    out = _futa_all(seeded, A)
    assert out["status"] == "incomplete" and core.FUTA_DONE_TEXT not in seeded.sent and seeded.sent[-1] == core.FUTA_INCOMPLETE_TEXT
    log = [v for k, v in seeded.ARCHIVE_STATE.items() if str(k).startswith("futa:")][0]
    assert log["verified"] is False and "transcripts" in log["residue_stores"]
    assert residue(seeded)["dicts"], "and the independent scan agrees that something is left"


def test_the_pair_is_recorded_from_a_real_inbound_carrying_both_and_deleted_with_the_person(mw, monkeypatch):
    import types
    payload = {"event": "messages.received", "data": {"messages": {"conversation": "Habari", "remoteJid": LID,
               "key": {"remoteJid": LID, "senderPn": A}}}}
    with monkeypatch.context() as mp:                                                # the spawn stubs apply to the webhook calls ONLY
        for name in ("futa_request", "futa_confirm", "answer_and_send", "greet_and_send"):
            mp.setitem(mw.__dict__, name, types.SimpleNamespace(spawn=lambda *a, **k: None))
        mw.webhook.get_raw_f()(payload)
        mw.webhook.get_raw_f()(payload)                                              # the same pair again: still one key
    pair = core.alias_pair_key(hash_of(A), hash_of(LID))
    assert list(mw.IDENTITY_ALIASES.keys()) == [pair]
    assert str(A.split("@")[0]) not in pair and "9988776655" not in pair, "the pair holds hashes, never a number"
    assert _futa_all(mw, A)["counts"]["aliases"] == 1 and list(mw.IDENTITY_ALIASES.keys()) == []


def test_a_linked_id_with_no_recorded_pair_is_NOT_found__a_documented_limit(mw):
    """PINNED so the limitation stays visible: a linked-ID cannot be derived from the phone number. Rows stored under one that was never paired with the
    phone are not reachable by a deletion, and the runbook's privacy notes say so."""
    h = hash_of(UNKNOWN_LID)
    mw.TRANSCRIPTS[f"2026-11/unknown-{h}.json"] = {"ts": "2026-11-26T08:00:00+00:00", "kind": "question", "sender_hash": h, "question": "UNPAIRED"}
    assert _futa_all(mw, A)["status"] == "done"
    assert f"2026-11/unknown-{h}.json" in mw.TRANSCRIPTS


def test_the_daily_run_keeps_the_alias_pairs_alive(seeded, monkeypatch):
    import datetime as dt
    seeded.old = item(1, "sent", days_ago=9)
    out = seeded.run_archive.get_raw_f()()
    assert out["alias_keys_touched"] == len(list(seeded.IDENTITY_ALIASES.keys())) == 1
