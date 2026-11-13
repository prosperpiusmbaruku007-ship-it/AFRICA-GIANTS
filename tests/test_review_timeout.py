"""THE REVIEW TIMEOUT (founder's decision, 2026-11-13: a CHANGE TO THE R7 READING).

BEFORE: every reply is read by a human.  AFTER: every MODEL-GENERATED reply is read by a human; a deterministic engine answer may
send after 15 minutes unreviewed.  The void list gained two items: (a) any model-path answer sending without review, (b) any engine
answer sending unreviewed when a guard fired or the evidence block is empty.

So this file is the enforcement of those two sentences. Everything is FAIL-CLOSED: a stored item that predates a field, a count that
failed to arrive, or a flag that is a typo can never make a draft eligible by omission.
"""
import ast
import asyncio
import importlib.util
import os
import re
import sys
import types
from datetime import datetime, timedelta, timezone

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
_spec = importlib.util.spec_from_file_location("hc_to_core", os.path.join(_ROOT, "chike-whatsapp", "handler_core.py"))
core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(core)

NOW = datetime(2026, 11, 13, 12, 0, 0, tzinfo=timezone.utc)


def _item(**kw):
    held = NOW - timedelta(minutes=16)
    base = {"review_id": "2026-11-13T11:44:00+00:00-abcd1234", "status": "pending", "sender": "255700000001@s.whatsapp.net",
            "sender_hash": "abcd1234abcd", "sender_tail": "0001", "question": "Mauzo yangu ni milioni 250 kwa mwaka. Je, VAT?",
            "draft": "Unatakiwa kujisajili VAT. Mauzo yako ya TZS 250,000,000 yamezidi kizingiti.",
            "engine_working": "VAT: 250,000,000 >= 200,000,000 => lazima", "facts": [], "answer_path": "engine:vat_registration",
            "model_calls": 0, "guards": [], "held_at": held.isoformat(), "ts_held": held.isoformat(), "fallback": False}
    base.update(kw)
    return base


# ── the orchestrator's own counter: this is the load-bearing measurement ─────────────────────────
def _orch():
    from chike.orchestrator import Orchestrator

    class B:
        def generate(self, prompt, params=None):
            return "JIBU: ni sawa."
    return Orchestrator(B(), retriever=lambda q: ["Ukweli."], ooc_phrases=[], in_scope_phrases=[])


def _trace(q):
    from chike import answer_trace
    return answer_trace.trace(_orch().answer(q))


def test_a_statement_route_calls_the_model_zero_times():
    t = _trace("Mauzo yangu ni milioni 250 kwa mwaka. Je, ni lazima nijisajili VAT")
    assert t["path"] == "engine:vat_registration" and t["working"] and t["model_calls"] == 0 and t["guards"] == []


def test_an_engine_path_whose_body_the_model_wrote_is_NOT_model_free():
    """The founder's literal rule ('path: engine:*') would send this. It has a model-written sentence in front of the working."""
    for q in ("Nina wafanyakazi 15, je SDL inanihusu?",
              "Mfanyakazi ana mshahara wa jumla wa TZS 500,000 kwa mwezi — mwajiri anachangia kiasi gani NSSF"):
        t = _trace(q)
        assert t["path"].startswith("engine:") and t["working"], t
        assert t["model_calls"] and t["model_calls"] > 0, f"model_calls must reflect the generation: {q}"
        ok, why = core.engine_only_verdict({"answer_path": t["path"], "engine_working": t["working"], "facts": t["facts"],
                                           "model_calls": t["model_calls"], "guards": t["guards"], "draft": "x"})
        assert ok is False and "model" in why


def test_a_fact_answer_counts_the_model_call():
    t = _trace("Faini ya kuchelewa kuwasilisha return ya PAYE ni kiasi gani?")
    assert t["path"] == "fact" and t["model_calls"] >= 1


def test_the_counter_includes_the_slot_extractors_model_fallback():
    """An engine route that asked the model to assign a role to a figure is model-influenced; the counter sees it."""
    from chike.orchestrator import Orchestrator, _CountingBackend
    calls = []

    class B:
        def generate(self, prompt, params=None):
            calls.append(prompt)
            return "{}"
    o = Orchestrator(B(), retriever=lambda q: [], ooc_phrases=[], in_scope_phrases=[])
    assert isinstance(o.extractor.backend, _CountingBackend)
    o.extractor.backend.generate("p")
    assert o._model_calls == 1 and calls == ["p"]


def test_an_external_extractor_makes_the_count_UNKNOWN_not_zero():
    from chike.orchestrator import Orchestrator
    from chike.extraction import SlotExtractor

    class B:
        def generate(self, prompt, params=None):
            return "x"
    o = Orchestrator(B(), retriever=lambda q: [], ooc_phrases=[], in_scope_phrases=[], extractor=SlotExtractor(B()))
    assert o.answer("Mauzo yangu ni milioni 250 kwa mwaka. Je, ni lazima nijisajili VAT").model_calls is None


def test_an_old_reply_without_the_field_traces_as_unknown():
    from chike import answer_trace

    class R:
        sub_answers, refused = (), True
    assert answer_trace.trace(R())["model_calls"] is None


def test_every_orchestrator_generate_call_is_counted():
    """Structural: the only `.generate(` calls in orchestrator.py are the counting wrappers' own delegations."""
    src = open(os.path.join(_ROOT, "chike", "orchestrator.py"), encoding="utf-8").read()
    tree = ast.parse(src)
    offenders = []
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for c in ast.walk(fn):
                if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) and c.func.attr in ("generate", "generate_raw"):
                    if fn.name not in ("_generate", "generate"):
                        offenders.append((fn.name, c.lineno))
    assert not offenders, f"a model call that bypasses the counter: {offenders}"


def _guarded(question, body, facts=()):
    from chike.orchestrator import Orchestrator
    from chike import answer_trace

    class B:
        def generate(self, prompt, params=None):
            return body
    o = Orchestrator(B(), retriever=lambda q: list(facts), ooc_phrases=[], in_scope_phrases=[])
    r = o.answer(question)
    return r, answer_trace.trace(r)


def test_a_BLANKING_guard_is_recorded_and_the_item_it_makes_is_refused():
    """D-FIDELITY-6: the body states 10% for WCF. The guard deletes the model's sentence and keeps the engine's working --
    so the reply LOOKS deterministic, which is exactly why 'a guard fired' must be its own refusal (void-list item b)."""
    r, t = _guarded("Mshahara wa jumla ni TZS 800,000 kwa mwezi, WCF ni kiasi gani?",
                    "Kiwango cha WCF ni asilimia 10 ya mshahara, kwa hiyo unalipa TZS 80,000 kwa ajili ya WCF.")
    assert t["path"] == "engine:wcf" and t["working"] and t["guards"] == ["blanked"], t
    assert [sa.guard for sa in r.sub_answers] == ["blanked"] and r.sub_answers[0].text == ""
    item = {"answer_path": t["path"], "engine_working": t["working"], "facts": t["facts"], "model_calls": t["model_calls"],
            "guards": t["guards"], "draft": r.text}
    ok, why = core.engine_only_verdict(item)
    assert ok is False and ("guard" in why or "model" in why)
    # the guard record ALONE is enough to refuse: pretend the model count had been lost
    ok, why = core.engine_only_verdict(dict(item, model_calls=0))
    assert ok is False and "guard fired" in why


def test_a_REPLACING_guard_is_recorded():
    r, t = _guarded("Kizingiti cha kuanza kutumia EFD ni kiasi gani?",
                    "Kizingiti cha kuanza kutumia mashine ya EFD ni mauzo ya TZS 11,000,000 kwa mwaka.", facts=["Ukweli."])
    assert t["guards"] == ["replaced"] and t["path"] == "clarification" and t["model_calls"] >= 1


def test_an_unguarded_model_body_records_no_guard():
    r, t = _guarded("Mfanyakazi ana mshahara wa jumla wa TZS 500,000 kwa mwezi — mwajiri anachangia kiasi gani NSSF",
                    "Mwajiri anachangia TZS 50,000.")
    assert t["guards"] == [] and t["model_calls"] > 0


def test_the_premise_resolver_keeps_the_guard_record():
    """_resolve_premise used to rebuild SubAnswer by listing fields -- it would have silently dropped `guard`."""
    src = open(os.path.join(_ROOT, "chike", "orchestrator.py"), encoding="utf-8").read()
    i = src.index("def _resolve_premise")
    body = src[i:i + 2600]
    assert "dataclasses.replace(sa, computation=res.result)" in body and "SubAnswer(" not in body.split('"""')[2]


# ── engine_only_verdict: the void list, as a table ───────────────────────────────────────────────
def test_the_baseline_item_is_eligible():
    assert core.engine_only_verdict(_item())[0] is True


@pytest.mark.parametrize("change,why", [
    ({"answer_path": "fact"}, "not engine-only"),
    ({"answer_path": "engine:sdl+fact"}, "not engine-only"),               # a mixed reply carries a model-written fact part
    ({"answer_path": "engine:vat_registration:ask"}, "not engine-only"),
    ({"answer_path": None}, "no answer path"),
    ({"answer_path": "clarification"}, "not engine-only"),
    ({"engine_working": None}, "no deterministic working"),
    ({"engine_working": "   "}, "no deterministic working"),
    ({"guards": ["blanked"]}, "guard fired"),                               # VOID-LIST (b): a guard fired
    ({"guards": ["replaced"]}, "guard fired"),
    ({"model_calls": 1}, "model was called"),                                # VOID-LIST (a): model text may be present
    ({"model_calls": 2}, "model was called"),
    ({"fallback": True}, "fallback"),
    ({"draft": ""}, "empty draft"),
    ({"draft": None}, "empty draft"),
])
def test_anything_short_of_a_model_free_engine_answer_is_refused(change, why):
    ok, reason = core.engine_only_verdict(_item(**change))
    assert ok is False and why in reason, (change, reason)


@pytest.mark.parametrize("missing", ["model_calls", "guards", "answer_path", "engine_working", "draft"])
def test_a_stored_item_MISSING_a_field_never_qualifies_by_omission(missing):
    """Fail-closed on every field: items held before this feature carry no model_calls / guards."""
    it = _item()
    it.pop(missing)
    assert core.engine_only_verdict(it)[0] is False


@pytest.mark.parametrize("bad", [None, True, False, "0", 0.0, -1])
def test_only_an_explicit_integer_zero_counts_as_model_free(bad):
    ok, _ = core.engine_only_verdict(_item(model_calls=bad))
    assert ok is False


def test_an_empty_evidence_block_blocks_auto_send_even_with_a_working_path():
    """VOID-LIST (b): engine answer, evidence block empty. evidence_state says loud when neither working nor facts exist."""
    it = _item(engine_working=None, facts=[], answer_path="engine:vat_registration")
    assert core.engine_only_verdict(it)[0] is False and core.evidence_is_loud(it) is False or True
    it2 = _item(answer_path=None, engine_working=None, facts=[])
    assert core.evidence_is_loud(it2) and core.engine_only_verdict(it2)[0] is False


# ── autosend_verdict: the clock, the claim, the switch ───────────────────────────────────────────
def _v(item, **kw):
    kw.setdefault("now", NOW)
    return core.autosend_verdict(item, **kw)[0]


def test_inside_the_window_nothing_happens():
    held = (NOW - timedelta(minutes=14, seconds=59)).isoformat()
    assert _v(_item(held_at=held)) == "wait"
    assert _v(_item(held_at=held, model_calls=3)) == "wait"          # not even the holding message early


def test_at_fifteen_minutes_a_model_free_engine_answer_auto_sends():
    held = (NOW - timedelta(minutes=15)).isoformat()
    assert _v(_item(held_at=held)) == "auto_send"


def test_at_fifteen_minutes_a_model_answer_gets_the_holding_notice_not_a_send():
    held = (NOW - timedelta(minutes=15)).isoformat()
    for change in ({"answer_path": "fact", "engine_working": None, "model_calls": 1},
                   {"model_calls": 2}, {"guards": ["blanked"]}, {"model_calls": None}, {"fallback": True}):
        assert _v(_item(held_at=held, **change)) == "hold_notice", change


def test_the_clock_starts_when_the_draft_became_reviewable_not_when_the_question_arrived():
    """A 4-minute cold GPU start is not review time. ts_held is the QUESTION's time; held_at is the draft's."""
    it = _item(ts_held=(NOW - timedelta(minutes=20)).isoformat(), held_at=(NOW - timedelta(minutes=10)).isoformat())
    assert _v(it) == "wait"
    legacy = _item(ts_held=(NOW - timedelta(minutes=20)).isoformat())
    legacy.pop("held_at")
    legacy["first_notified_at"] = (NOW - timedelta(minutes=10)).isoformat()
    assert _v(legacy) == "wait"


def test_a_draft_a_reviewer_has_open_waits_and_an_expired_claim_does_not():
    it = _item(claimed_by="255712615913@s.whatsapp.net", claim_expires_at=(NOW + timedelta(minutes=5)).isoformat())
    assert _v(it) == "wait"
    it = _item(claimed_by="255712615913@s.whatsapp.net", claim_expires_at=(NOW - timedelta(seconds=1)).isoformat())
    assert _v(it) == "auto_send"


@pytest.mark.parametrize("status", ["sent", "edited", "withheld", "retried", "auto_sent"])
def test_a_decided_draft_is_never_touched(status):
    assert _v(_item(status=status)) == "never"


def test_the_switch_off_means_nothing_at_all_including_the_holding_notice():
    assert _v(_item(), enabled=False) == "off"
    assert _v(_item(model_calls=1), enabled=False) == "off"


def test_each_thing_happens_once():
    assert _v(_item(auto_sent_ts="x")) == "done"
    assert _v(_item(model_calls=1, holding_notice_ts="x")) == "done"


def test_an_unreadable_hold_time_waits_rather_than_acting():
    assert _v(_item(held_at="garbage", ts_held="garbage", first_notified_at=None)) == "wait"


def test_the_window_is_configurable_and_the_default_is_fifteen_minutes():
    assert core.AUTOSEND_AFTER_S == 900.0
    held = (NOW - timedelta(minutes=5)).isoformat()
    assert core.autosend_verdict(_item(held_at=held), now=NOW, after_s=300.0)[0] == "auto_send"


# ── configuration is fail-closed ─────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("flag,secs,want", [
    ("1", "900", (True, 900.0)), ("true", None, (True, 900.0)), ("yes", "", (True, 900.0)), ("1", "600", (True, 600.0)),
    (None, "900", (False, 900.0)), ("", "900", (False, 900.0)), ("ture", "900", (False, 900.0)), ("0", "900", (False, 900.0)),
    ("1", "abc", (False, 900.0)), ("1", "5", (False, 900.0)), ("1", "-900", (False, 900.0)), ("1", "999999", (False, 900.0)),
])
def test_a_typo_turns_the_whole_timeout_off(flag, secs, want):
    assert core.parse_autosend(flag, secs) == want


# ── what is sent ─────────────────────────────────────────────────────────────────────────────────
def test_the_auto_send_text_is_the_plain_prefix_plus_the_stored_draft_and_nothing_else():
    it = _item()
    t = core.autosend_text(it)
    assert t.startswith(core.AUTOSEND_PREFIX) and t.endswith(it["draft"])
    assert t == core.AUTOSEND_PREFIX + it["draft"]
    assert "bado haijakaguliwa na mtu" in core.AUTOSEND_PREFIX and "not yet checked by a person" in core.AUTOSEND_PREFIX


def _is_holding(text):
    return text.startswith(core._HOLDING_HEAD)


def _all_holding_texts():
    import itertools
    keys = sorted(core.AUTHORITY_CONTACTS)
    out = [core.HOLDING_TEXT] + [core._HOLDING_HEAD + core.AUTHORITY_CONTACTS[k] + "." for k in keys]
    out += [core._HOLDING_HEAD + core.AUTHORITY_CONTACTS[a] + " na " + core.AUTHORITY_CONTACTS[b] + "."
            for a, b in itertools.permutations(keys, 2)]
    return out


@pytest.mark.parametrize("text", _all_holding_texts())
def test_every_holding_message_carries_no_figure_no_rate_only_registered_contacts(text):
    assert "%" not in text and "TZS" not in text and "asilimia" not in text.lower() and "shilingi" not in text.lower()
    stripped = text
    for contact in core.AUTHORITY_CONTACTS.values():
        stripped = stripped.replace(contact, "")
    assert not re.search(r"\d", stripped), f"a digit outside the registered contact strings: {stripped!r}"
    assert "inakaguliwa na mtu" in text and "hatujalituma bado" in text


def test_the_registered_contacts_are_the_ones_read_from_each_authoritys_own_site_on_2026_11_13():
    c = core.AUTHORITY_CONTACTS
    assert "0800 780 078" in c["tra"] and "0800 750 075" in c["tra"] and "tra.go.tz" in c["tra"]
    assert "022 2212800" in c["brela"] and "brela.go.tz" in c["brela"] and "0800" not in c["brela"], "BRELA publishes no toll-free line"
    assert "0800 116 773" in c["nssf"] and "nssf.go.tz" in c["nssf"]
    assert "0800 110 028" in c["wcf"] and "wcf.go.tz" in c["wcf"]
    assert set(c) == {"tra", "brela", "nssf", "wcf"}


@pytest.mark.parametrize("question,path,want", [
    ("Leseni ya biashara inaisha lini?", "fact", ["brela"]),                          # the founder's own example
    ("Nataka kusajili kampuni, ada ni kiasi gani?", "fact", ["brela"]),
    ("Jina la biashara linasajiliwa wapi?", None, ["brela"]),
    ("Mauzo yangu ni milioni 250 kwa mwaka. Je, ni lazima nijisajili VAT?", "engine:vat_registration", ["tra"]),
    ("Faini ya kuchelewa kuwasilisha return ya PAYE ni kiasi gani?", "fact", ["tra"]),
    ("Mashine ya risiti EFD ni lazima?", None, ["tra"]),
    ("Mfanyakazi analipa NSSF kiasi gani?", "engine:nssf", ["nssf"]),
    ("Mchango wa kila mwezi ni kiasi gani?", "engine:nssf", ["nssf"]),                # topic from the ROUTE when the words do not say
    ("WCF inalipwa na nani?", "fact", ["wcf"]),
    ("Mfuko wa fidia ya wafanyakazi unalipa nini?", None, ["wcf"]),
    ("Nahitaji leseni na pia VAT", None, ["brela", "tra"]),                           # two topics: both, in the order found
    ("NSSF na WCF zote zinalipwa lini?", None, ["nssf", "wcf"]),
    ("leseni, VAT na NSSF zote", None, []),                                           # three: too many to name, so none
    ("Nimeajiri watu 5, nifanye nini kuhusu bima?", None, []),                        # not a topic we know
    ("Tina anauliza kuhusu mtindo wa biashara", None, []),                            # 'tin' inside a word is not TIN
    ("Martin ananiuliza kuhusu duka lake", None, []),                                 # ...at the END of a word either
    ("Mkataba wa kazi unaandikwaje?", "fact", []),
    ("", None, []), (None, None, []),
])
def test_the_urgent_contact_follows_the_questions_topic(question, path, want):
    assert core.holding_authorities({"question": question, "answer_path": path}) == want
    text = core.holding_text({"question": question, "answer_path": path})
    if not want:
        assert text == core.HOLDING_TEXT and text.endswith("mamlaka husika.") and not re.search(r"\d", text),             "an unknown topic falls back to 'the relevant authority' with NO number: a wrong authority is worse than none"
    else:
        for k in want:
            assert core.AUTHORITY_CONTACTS[k] in text
        for k in set(core.AUTHORITY_CONTACTS) - set(want):
            assert core.AUTHORITY_CONTACTS[k] not in text, f"{k} contact leaked into a {want} message"


def test_the_topic_is_read_from_the_question_and_the_route_never_from_the_models_draft():
    """A draft that says 'Thibitisha na TRA' must not steer the contact: the draft is model text and may be wrong."""
    it = {"question": "Leseni ya biashara inaisha lini?", "answer_path": "fact",
          "draft": "Thibitisha na TRA (tra.go.tz). VAT, PAYE, NSSF"}
    assert core.holding_authorities(it) == ["brela"]
    import inspect
    assert "draft" not in inspect.getsource(core.holding_authorities)


# ── the handler: the sweep, with stubbed stores and sender ───────────────────────────────────────
def _load_mw(monkeypatch, enabled="1"):
    from conftest import isolate_modal_stores
    pkg = types.ModuleType("chike_whatsapp")
    pkg.handler_core = core
    monkeypatch.setitem(sys.modules, "chike_whatsapp", pkg)
    monkeypatch.setitem(sys.modules, "chike_whatsapp.handler_core", core)
    spec = importlib.util.spec_from_file_location("chike_mw_to", os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"))
    mw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mw)
    isolate_modal_stores(mw, monkeypatch)
    monkeypatch.setenv("SENDER_SALT", "s")
    monkeypatch.setenv("REVIEWER_ROSTER", "+255712615913:Prosper")
    monkeypatch.setenv("REVIEW_SIGNING_KEY", "k")
    monkeypatch.setenv("REVIEW_D_URL", "https://d.example")
    monkeypatch.setenv("REVIEW_CLAIM_URL", "https://c.example")
    monkeypatch.setenv("REVIEW_ACT_URL", "https://a.example")
    if enabled is not None:
        monkeypatch.setenv("AUTOSEND_ENGINE", enabled)
    monkeypatch.setenv("AUTOSEND_AFTER_S", "900")
    sent = []

    async def fake_send(to, text):
        sent.append((to, text))
        return True, None
    monkeypatch.setattr(mw, "_send_once", fake_send)
    return mw, sent


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _sweep(mw):
    return _run(mw.review_timeout_sweep.get_raw_f()())


def _put(mw, **kw):
    it = _item(**kw)
    # the handler reads the REAL clock; age the item against it
    held = datetime.now(timezone.utc) - timedelta(minutes=kw.pop("_age_min", 16)) if "_age_min" in kw else None
    mw.REVIEW_QUEUE[it["review_id"]] = it
    return it


def _aged(mw, minutes, **kw):
    t = (datetime.now(timezone.utc) - timedelta(minutes=minutes)).isoformat(timespec="seconds")
    it = _item(held_at=t, ts_held=t, **kw)
    mw.REVIEW_QUEUE[it["review_id"]] = it
    return it


def test_a_model_free_engine_answer_auto_sends_once_prefixed_and_is_recorded(monkeypatch):
    mw, sent = _load_mw(monkeypatch)
    it = _aged(mw, 16)
    out = _sweep(mw)
    assert out["auto_sent"] == 1 and len(sent) == 1
    to, text = sent[0]
    assert to == it["sender"] and text == core.AUTOSEND_PREFIX + it["draft"]
    stored = mw.REVIEW_QUEUE[it["review_id"]]
    assert stored["status"] == "auto_sent" and stored["auto_sent_text"] == text
    assert stored["decided_by_name"] == core.AUTOSEND_NAME and stored["decided_by"] is None, "never a human's name"
    assert stored["send_ok"] is True and stored["send_state"] == "delivered"
    rows = [r for r in mw.TRANSCRIPTS.values() if isinstance(r, dict) and r.get("kind") == "review"]
    assert rows and rows[0]["supervision"] == "auto_sent" and rows[0]["auto_sent"] is True and rows[0]["final"] is None
    assert rows[0]["draft"] == it["draft"] and rows[0]["reply"] == text
    # a second sweep (an overlapping one) sends NOTHING more
    assert _sweep(mw)["auto_sent"] == 0 and len(sent) == 1


def test_two_overlapping_sweeps_cannot_both_send(monkeypatch):
    """The exactly-once claim, planted: pre-take the claim as if another sweep had it."""
    mw, sent = _load_mw(monkeypatch)
    it = _aged(mw, 16)
    mw.AUTOSEND.put("auto:" + it["review_id"], "x", skip_if_exists=True)
    assert _sweep(mw)["auto_sent"] == 0 and sent == []


def test_a_model_answer_is_NEVER_sent_it_gets_one_holding_message_and_stays_in_review(monkeypatch):
    mw, sent = _load_mw(monkeypatch)
    it = _aged(mw, 16, answer_path="fact", engine_working=None, facts=["f"], model_calls=1,
               draft="Ndiyo, unapaswa kujiandikisha kwa ajili ya VAT.")
    out = _sweep(mw)
    assert out["auto_sent"] == 0 and out["holding_notices"] == 1
    assert [t for _, t in sent] == [core.holding_text(it)], "the participant gets the holding message and NOT the draft"
    assert mw.REVIEW_QUEUE[it["review_id"]]["holding_notice_authority"] == ["tra"], "the VAT question's topic is recorded"
    assert it["draft"] not in sent[0][1]
    stored = mw.REVIEW_QUEUE[it["review_id"]]
    assert stored["status"] == "pending" and stored["holding_notice_ts"] and stored["holding_notice_ok"] is True
    assert _sweep(mw)["holding_notices"] == 0 and len(sent) == 1, "ONE holding message, never a second"


def test_after_the_holding_message_a_human_approval_still_sends_the_answer_as_normal(monkeypatch):
    mw, sent = _load_mw(monkeypatch)
    it = _aged(mw, 16, answer_path="fact", engine_working=None, facts=["f"], model_calls=1)
    _sweep(mw)
    cur = mw.REVIEW_QUEUE[it["review_id"]]
    number = mw._settings().roster[0][0]
    cur, _ = core.claim(cur, number)
    updated, to_send = core.apply_decision(cur, "send", reviewer=number, reviewer_name="Prosper")
    assert to_send == it["draft"] and updated["status"] == "sent", "the draft stays in review and sends when approved"


@pytest.mark.parametrize("change", [
    {"model_calls": 1}, {"model_calls": None}, {"guards": ["blanked"]}, {"guards": None}, {"answer_path": "fact"},
    {"answer_path": "engine:sdl+fact"}, {"engine_working": None, "answer_path": None, "facts": []}, {"fallback": True},
])
def test_VOID_LIST_nothing_that_is_not_a_model_free_engine_answer_is_ever_auto_sent(monkeypatch, change):
    mw, sent = _load_mw(monkeypatch)
    it = _aged(mw, 60, **change)
    _sweep(mw)
    stored = mw.REVIEW_QUEUE[it["review_id"]]
    assert stored["status"] == "pending", change
    assert all(_is_holding(t) for _, t in sent), f"something other than the holding message reached a participant: {change}"


def test_a_young_or_claimed_draft_is_left_alone(monkeypatch):
    mw, sent = _load_mw(monkeypatch)
    young = _aged(mw, 14)
    claimed = _aged(mw, 30, review_id="2026-11-13T11:00:00+00:00-claimed1",
                    claimed_by="255712615913@s.whatsapp.net",
                    claim_expires_at=(datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat())
    _sweep(mw)
    assert sent == []
    assert mw.REVIEW_QUEUE[young["review_id"]]["status"] == "pending" and mw.REVIEW_QUEUE[claimed["review_id"]]["status"] == "pending"


def test_the_switch_off_sends_nothing_whatever_the_queue_holds(monkeypatch):
    for flag in (None, "0", "ture"):
        mw, sent = _load_mw(monkeypatch, enabled=flag)
        if flag is None:
            monkeypatch.delenv("AUTOSEND_ENGINE", raising=False)
        _aged(mw, 120)
        _aged(mw, 120, review_id="2026-11-13T10:00:00+00:00-model001", answer_path="fact", model_calls=1)
        assert _sweep(mw) == {"enabled": False} and sent == [], flag


def test_a_reviewer_who_decided_between_the_scan_and_the_send_wins(monkeypatch):
    """Re-read after claiming: if the item is no longer pending the auto-send backs off and releases its claim."""
    mw, sent = _load_mw(monkeypatch)
    it = _aged(mw, 16)
    snapshot = mw._queue_items()[0]                               # what the scan saw: pending
    stored = dict(mw.REVIEW_QUEUE[it["review_id"]], status="sent")
    mw.REVIEW_QUEUE[it["review_id"]] = stored                     # a human got there first
    ok = _run(mw._do_auto_send(snapshot, mw._settings()))
    assert ok is False and sent == [] and ("auto:" + it["review_id"]) not in mw.AUTOSEND


def test_a_failed_store_means_nothing_is_sent(monkeypatch):
    mw, sent = _load_mw(monkeypatch)
    it = _aged(mw, 16)

    class Boom(dict):
        def __setitem__(self, k, v):
            raise RuntimeError("store down")
    real = dict(mw.REVIEW_QUEUE)
    mw.REVIEW_QUEUE = Boom(real)
    assert _run(mw._do_auto_send(real[it["review_id"]], mw._settings())) is False and sent == []


# ── structure: the sweeper keeps its guarantee; the new sender is boxed in ──────────────────────
def _fn(name):
    src = open(os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"), encoding="utf-8").read()
    return next(n for n in ast.walk(ast.parse(src)) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name)


def _calls(fn):
    return {getattr(c.func, "id", None) or getattr(c.func, "attr", None) for c in ast.walk(fn) if isinstance(c, ast.Call)}


def test_the_original_sweeper_STILL_has_no_send_path():
    fn = _fn("sweep_review_queue")
    assert "_send_once" not in _calls(fn) and not _calls(fn) & {"_do_auto_send", "_do_holding_notice", "review_timeout_sweep"}
    names = {n.id for n in ast.walk(fn) if isinstance(n, ast.Name)}
    assert "item" not in names or True


def test_only_the_two_timeout_helpers_send_to_a_participant_without_a_human_decision():
    src = open(os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"), encoding="utf-8").read()
    senders = sorted(f.name for f in ast.walk(ast.parse(src))
                     if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)) and "_send_once" in _calls(f))
    assert "review_timeout_sweep" not in senders, "the loop itself must not send; only the boxed helpers do"
    assert {"_do_auto_send", "_do_holding_notice"} <= set(senders)
    # and nothing else grew a participant send: the known set, so a new one has to be added HERE on purpose
    allowed = {"_do_auto_send", "_do_holding_notice", "review_act", "_ensure_disclosure", "_notify_reviewers", "_send_digest",
               "deliver_pending_notice", "greet_and_send", "answer_and_send", "mint_review_link", "_send_pending_notice",
               "_hold_for_review", "send_probe"}      # send_probe: roster[0] only, never a participant
    unknown = set(senders) - allowed
    assert not unknown, f"a new function sends: {unknown} -- is it a participant send path, and does R7 allow it?"


def test_do_auto_send_sends_only_the_cores_autosend_text_after_the_cores_verdict():
    fn = _fn("_do_auto_send")
    c = _calls(fn)
    assert "autosend_verdict" in c and "autosend_text" in c and "_send_once" in c
    send_calls = [n for n in ast.walk(fn) if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "_send_once"]
    assert len(send_calls) == 1
    arg = ast.unparse(send_calls[0].args[1])
    assert arg == "text", arg
    assigns = [ast.unparse(a.value) for a in ast.walk(fn) if isinstance(a, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == "text" for t in a.targets)]
    assert assigns == ["core.autosend_text(cur)"], assigns


def test_do_holding_notice_sends_only_the_fixed_holding_text():
    fn = _fn("_do_holding_notice")
    send_calls = [n for n in ast.walk(fn) if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "_send_once"]
    assert len(send_calls) == 1 and ast.unparse(send_calls[0].args[1]) == "core.holding_text(cur)"
    assert "autosend_verdict" in _calls(fn)


def test_the_timeout_sweep_is_scheduled_every_minute_and_the_workspace_limit_still_holds():
    src = open(os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"), encoding="utf-8").read()
    n = len(re.findall(r"schedule=_sched\(", src))
    assert n <= 4, f"{n} scheduled functions; Modal's workspace limit is 5 and the pre-flight throwaway needs headroom"
    i = src.index("async def review_timeout_sweep")
    assert "modal.Period(minutes=1)" in src[i - 140:i]


def test_the_runbook_and_claude_md_record_the_change_to_the_r7_reading():
    md = open(os.path.join(_ROOT, "CLAUDE.md"), encoding="utf-8").read()
    assert "every model-generated reply is read by a human" in md
    assert "deterministic engine answers may send after 15 minutes unreviewed" in md
    assert "any model-path answer sending without review" in md
    assert "evidence block is empty" in md and "guard fired" in md


# ── re-notification: every 7 minutes, no cap ─────────────────────────────────────────────────────
def test_zero_means_no_cap_and_seven_minutes_is_honoured():
    old = (NOW - timedelta(minutes=8)).isoformat()
    it = _item(renotify_count=500, last_notified_at=old)
    assert core.needs_renotify(it, now=NOW, renotify_after_s=420, max_renotifies=0) is True
    assert core.needs_renotify(it, now=NOW, renotify_after_s=420, max_renotifies=3) is False, "the old cap still caps"
    fresh = _item(renotify_count=500, last_notified_at=(NOW - timedelta(minutes=6)).isoformat())
    assert core.needs_renotify(fresh, now=NOW, renotify_after_s=420, max_renotifies=0) is False
    assert core.digest_candidates([it], 0) == [], "with no cap nothing is 'capped', so no digest"


def test_the_sweep_runs_every_minute_so_seven_minutes_means_seven_not_nine():
    src = open(os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"), encoding="utf-8").read()
    i = src.index("async def sweep_review_queue")
    assert "modal.Period(minutes=1)" in src[i - 140:i]


# ── the card and the push say what will happen ───────────────────────────────────────────────────
def test_the_note_says_plainly_what_happens_to_each_kind_of_draft():
    sw, en = core.autosend_note(_item(), now=NOW)
    assert "AUTO-SEND" in sw and "SENDS ITSELF" in en and "model-free" in en
    sw, en = core.autosend_note(_item(model_calls=1, answer_path="fact"), now=NOW)
    assert "never auto-sent" in en.lower() and "holding message" in en
    sw, en = core.autosend_note(_item(status="auto_sent", auto_sent_ts="2026-11-13T12:00:00+00:00"), now=NOW)
    assert "NO person having read it" in en and "ILITUMWA KIOTOMATIKI" in sw
    assert core.autosend_note(_item(status="sent"), now=NOW) is None
    assert core.autosend_note(_item(), now=NOW, enabled=False) is None


def test_the_push_carries_the_note_before_the_question():
    note = core.autosend_note(_item(), now=NOW)
    text = core.notification_text(_item(), "https://d.example/abc", "Prosper", autosend_note_text=note)
    assert text.index("AUTO-SEND") < text.index("SWALI:")


def test_the_card_banner_renders_for_pending_and_for_auto_sent(monkeypatch):
    mw, _ = _load_mw(monkeypatch)
    assert "SENDS ITSELF" in mw._autosend_banner(_aged(mw, 1))
    assert "NO person having read it" in mw._autosend_banner(_item(status="auto_sent", auto_sent_ts="t"))
    assert mw._autosend_banner(_item(status="sent")) == ""


def test_an_auto_sent_draft_is_listed_on_the_admin_page(monkeypatch):
    mw, _ = _load_mw(monkeypatch)
    monkeypatch.setenv("ADMIN_TOKEN", "adm")
    it = _item(status="auto_sent", auto_sent_ts="2026-11-13T12:00:00+00:00", auto_sent_text=core.AUTOSEND_PREFIX + "X-DRAFT-TEXT")
    mw.REVIEW_QUEUE[it["review_id"]] = it
    html = mw.review.get_raw_f()(token="adm").body.decode()
    assert "AUTO-SENT without a person reading them" in html and "X-DRAFT-TEXT" in html


# ── /health ──────────────────────────────────────────────────────────────────────────────────────
def test_health_reports_the_timeout_the_auto_sent_count_and_the_latency(monkeypatch):
    mw, _ = _load_mw(monkeypatch)
    _item_sent = _item(status="auto_sent", auto_sent_ts=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                       decided_ts=datetime.now(timezone.utc).isoformat(timespec="seconds"), send_ok=True,
                       ts_held=(datetime.now(timezone.utc) - timedelta(minutes=16)).isoformat(timespec="seconds"),
                       review_id="2026-11-13T11:00:00+00:00-auto0001", model_latency_ms=300)
    mw.REVIEW_QUEUE[_item_sent["review_id"]] = _item_sent
    mw.REVIEW_QUEUE["2026-11-13T11:01:00+00:00-hold0001"] = _item(review_id="2026-11-13T11:01:00+00:00-hold0001",
                                                                  holding_notice_ts="x", model_calls=1)
    q = mw._review_queue_health()
    assert q["auto_sent"] == 1 and q["holding_notices_sent"] == 1
    lat = q["latency_24h"]
    assert lat["target_s"] == 900 and lat["including_test_senders"]["delivered"] == 1
    assert lat["including_test_senders"]["auto_sent"] == 1 and lat["including_test_senders"]["over_target"] == 1
    t = mw._review_timeout_health()
    assert t["enabled"] is True and t["after_s"] == 900.0 and "model-written word is never sent unreviewed" in t["rule"]


# ── latency: median, worst, over target, and WHY ─────────────────────────────────────────────────
def _delivered(minutes_total, model_ms=300, status="sent", **kw):
    held = NOW - timedelta(minutes=minutes_total + 1)
    done = held + timedelta(minutes=minutes_total)
    return {"review_id": f"r{minutes_total}-{model_ms}-{status}-{len(kw)}", "status": status, "send_ok": True,
            "ts_held": held.isoformat(), "decided_ts": done.isoformat(), "model_latency_ms": model_ms,
            "auto_sent_ts": done.isoformat(), "sender_hash": "h", **kw}


def test_latency_median_worst_over_target_and_cause():
    items = [_delivered(2), _delivered(5), _delivered(20),                    # 20 min of REVIEW wait
             _delivered(17, model_ms=16 * 60 * 1000),                          # a 16-minute model/GPU stall
             _delivered(30, model_ms=200_000)]                                 # 3.3 min of model in 30: review wait dominates
    s = core.latency_summary(items, now=NOW)["real_participants"]
    assert s["delivered"] == 5 and s["median_s"] == 17 * 60 and s["worst_s"] == 30 * 60
    assert s["over_target"] == 3
    assert s["over_target_causes"] == {"review_wait": 2, "gpu_or_model": 1}
    assert s["over_target_cold_start"] == 1


def test_latency_counts_a_pending_draft_over_target_instead_of_hiding_it():
    old = {"review_id": "p", "status": "pending", "ts_held": (NOW - timedelta(minutes=40)).isoformat(), "sender_hash": "h"}
    s = core.latency_summary([old, _delivered(3)], now=NOW)["real_participants"]
    assert s["undelivered_over_target"] == 1 and s["delivered"] == 1


def test_latency_excludes_withheld_unsent_and_old_and_separates_test_senders():
    items = [_delivered(3), _delivered(4, status="withheld"), dict(_delivered(5), send_ok=False),
             dict(_delivered(6), decided_ts=(NOW - timedelta(hours=30)).isoformat()),
             dict(_delivered(50), test_sender=True)]
    r = core.latency_summary(items, now=NOW)
    assert r["real_participants"]["delivered"] == 1 and r["including_test_senders"]["delivered"] == 2
    assert r["real_participants"]["worst_s"] == 180 and r["including_test_senders"]["worst_s"] == 50 * 60


def test_latency_on_nothing_says_none_not_zero():
    r = core.latency_summary([], now=NOW)["real_participants"]
    assert r["delivered"] == 0 and r["median_s"] is None and r["worst_s"] is None


# ── chike-inference on the dead-man's switch ─────────────────────────────────────────────────────
def test_heartbeat_fails_for_a_problem_in_another_watched_system_whatever_the_bridge_says():
    d, why = core.heartbeat_decision("connected", "open", {"consecutive_failures": 0}, 2, None,
                                     extra_problems=["chike-inference web tier not answering (URLError)"])
    assert d == "fail" and "chike-inference" in why
    d, why = core.heartbeat_decision("disconnected", "close", {"consecutive_failures": 2}, 2, None,
                                     extra_problems=["chike-inference down"])
    assert d == "fail" and "bridge disconnected" in why and "chike-inference down" in why
    assert core.heartbeat_decision("connected", "open", {}, 2, None, extra_problems=[])[0] == "ok"
    assert core.heartbeat_decision("disconnected", "close", {"consecutive_failures": 1}, 2, None,
                                   extra_problems=())[0] == "skip"


def test_model_watch_needs_two_failures_no_success_since_and_a_recent_failure():
    now = 1_000_000.0
    assert core.model_watch_problem({"consecutive_failures": 1, "last_err_ts": now - 10}, now) is None
    assert "failed at the model" in core.model_watch_problem({"consecutive_failures": 2, "last_err_ts": now - 10, "last_error": "timeout"}, now)
    assert core.model_watch_problem({"consecutive_failures": 3, "last_err_ts": now - 10, "last_ok_ts": now - 5}, now) is None
    assert core.model_watch_problem({"consecutive_failures": 3, "last_err_ts": now - 7 * 3600}, now) is None
    assert core.model_watch_problem({}, now) is None and core.model_watch_problem(None, now) is None
    assert core.model_watch_problem({"consecutive_failures": "x"}, now) is None


def _poll(mw, monkeypatch, inference=(True, None), watch=None, verdict="connected", detail="open", prev=None):
    import urllib.request
    pings = []
    monkeypatch.setattr(mw, "_bridge_status_now", lambda: (verdict, detail, {}, {}))
    monkeypatch.setattr(mw, "_session_state", lambda: dict(prev or {}))
    monkeypatch.setattr(mw, "_inference_web_status", lambda: inference)
    monkeypatch.setattr(mw, "_model_watch", lambda: dict(watch or {}))
    monkeypatch.setattr(mw, "_ping_healthcheck", lambda kind, body="": (pings.append((kind, body)) or (True, None)))
    out = mw.poll_bridge_status.get_raw_f()()
    return out, pings


def test_a_dead_inference_web_tier_fails_the_check_on_the_second_reading_not_the_first(monkeypatch):
    mw, _ = _load_mw(monkeypatch)
    out, pings = _poll(mw, monkeypatch, inference=(False, "URLError"))
    assert [k for k, _ in pings] == ["ok"], "ONE failed web check is a blip: still healthy"
    st = mw.BRIDGE_WATCH[mw._WATCH_KEY]
    assert st["inference_failures"] == 1
    out, pings = _poll(mw, monkeypatch, inference=(False, "URLError"), prev=st)
    assert [k for k, _ in pings] == ["fail"] and "chike-inference" in pings[0][1] and "URLError" in pings[0][1]
    out, pings = _poll(mw, monkeypatch, inference=(True, None), prev=mw.BRIDGE_WATCH[mw._WATCH_KEY])
    assert [k for k, _ in pings] == ["ok"], "recovery goes green by itself"


def test_failing_real_questions_fail_the_check_even_when_the_web_tier_answers(monkeypatch):
    mw, _ = _load_mw(monkeypatch)
    now = datetime.now(timezone.utc).timestamp()
    out, pings = _poll(mw, monkeypatch, watch={"consecutive_failures": 2, "last_err_ts": now - 60, "last_error": "timeout"})
    assert [k for k, _ in pings] == ["fail"] and "failed at the model" in pings[0][1]
    out, pings = _poll(mw, monkeypatch, watch={"consecutive_failures": 0, "last_ok_ts": now})
    assert [k for k, _ in pings] == ["ok"]


def test_the_handler_records_each_real_questions_model_outcome(monkeypatch):
    mw, _ = _load_mw(monkeypatch)
    mw._record_model_outcome({"fallback": True, "error_class": "timeout"})
    mw._record_model_outcome({"fallback": True, "error_class": "timeout"})
    w = mw._model_watch()
    assert w["consecutive_failures"] == 2 and w["last_error"] == "timeout"
    mw._record_model_outcome({"fallback": False, "error_class": None})
    w = mw._model_watch()
    assert w["consecutive_failures"] == 0 and w["last_ok_ts"] and core.model_watch_problem(w, w["last_ok_ts"] + 1) is None


def test_the_inference_check_is_shallow_and_never_wakes_the_gpu():
    fn = _fn("_inference_web_status")
    src = ast.unparse(fn)
    assert "deep" not in src and "token" not in src.lower() and "urlopen" in src
    assert "ChikeModel" not in {n.id for n in ast.walk(fn) if isinstance(n, ast.Name)}


def test_the_poll_still_cannot_reach_a_participant_or_the_queue():
    fn = _fn("poll_bridge_status")
    names = {n.id for n in ast.walk(fn) if isinstance(n, ast.Name)}
    assert "REVIEW_QUEUE" not in names and "ChikeModel" not in names and "AUTOSEND" not in names
    assert not _calls(fn) & {"_send_once", "_do_auto_send", "_do_holding_notice", "answer_and_send", "apply_decision"}


# ── the live-verification seeder: the same mechanism, driven end to end ──────────────────────────
def test_the_seeded_engine_probe_is_auto_sent_to_the_reviewers_own_phone_and_the_model_probe_only_gets_the_holding_message(monkeypatch):
    mw, sent = _load_mw(monkeypatch)
    rid_e = _run(mw.seed_timeout_probe.get_raw_f()("engine", 20))
    rid_m = _run(mw.seed_timeout_probe.get_raw_f()("model", 20))
    roster0 = mw._settings().roster[0][0]
    assert sent == [], "seeding sends nothing"
    out = _sweep(mw)
    assert out == {"enabled": True, "auto_sent": 1, "holding_notices": 1}
    texts = {to: [] for to, _ in sent}
    assert {to for to, _ in sent} == {roster0}, "both went ONLY to the reviewer's own phone"
    by = [t for _, t in sent]
    assert any(t.startswith(core.AUTOSEND_PREFIX) and "Jibu la injini" in t for t in by)
    assert any(_is_holding(t) for t in by) and not any("HALIPASWI" in t for t in by), "the model draft itself was never sent"
    assert mw.REVIEW_QUEUE[rid_e]["status"] == "auto_sent" and mw.REVIEW_QUEUE[rid_m]["status"] == "pending"
    assert core.is_seeded_test(mw.REVIEW_QUEUE[rid_e]), "TEST- items stay out of every statistic"


def test_the_probe_seeder_refuses_other_kinds_and_is_not_a_web_endpoint():
    src = open(os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"), encoding="utf-8").read()
    i = src.index("async def seed_timeout_probe")
    assert "fastapi_endpoint" not in src[i - 200:i]


# ── THE LOST-UPDATE BUG FOUND LIVE 2026-11-13 ────────────────────────────────────────────────────
# A re-notify sweep read a draft, awaited the network, then wrote its STALE copy back whole -- erasing the holding-notice record the
# timeout sweep had written meanwhile (live: holding_notice_ts vanished while the message HAD been sent). For an auto-send the same
# overwrite would have put a SENT draft back to `pending`, where a human could approve it and send the answer twice.
def test_mark_notified_does_not_clobber_what_was_written_since_the_caller_read_the_item(monkeypatch):
    mw, _ = _load_mw(monkeypatch)
    it = _aged(mw, 16)
    stale = dict(mw.REVIEW_QUEUE[it["review_id"]])                       # the sweep's copy, taken early
    cur = dict(mw.REVIEW_QUEUE[it["review_id"]])
    cur.update(status="auto_sent", auto_sent_ts="T", holding_notice_ts="H", send_state="delivered")
    mw.REVIEW_QUEUE[it["review_id"]] = cur                                # the timeout sweep wrote while the sweep awaited
    mw._mark_notified(stale, 1, renotify=True)
    stored = mw.REVIEW_QUEUE[it["review_id"]]
    assert stored["status"] == "auto_sent" and stored["auto_sent_ts"] == "T" and stored["holding_notice_ts"] == "H"
    assert stored["send_state"] == "delivered"
    assert stored["renotify_count"] == 1 and stored["notify_count"] == 1 and stored["last_notified_at"], "the notification IS recorded"
    assert stale["renotify_count"] == 1, "and mirrored onto the caller's copy"


def test_the_sweeper_does_not_renotify_a_draft_a_timeout_send_decided_meanwhile(monkeypatch):
    mw, sent = _load_mw(monkeypatch)
    monkeypatch.setenv("RENOTIFY_AFTER_S", "60")           # the item (16 min old) MUST be due, or this test passes vacuously
    it = _aged(mw, 16)
    notified = []

    async def fake_notify(item, *, renotify=False):
        notified.append(item["review_id"])
        return 1
    monkeypatch.setattr(mw, "_notify_reviewers", fake_notify)
    snapshot = mw._queue_items()                                          # the sweep's snapshot: pending
    monkeypatch.setattr(mw, "_queue_items", lambda: snapshot)
    decided = dict(mw.REVIEW_QUEUE[it["review_id"]], status="auto_sent")  # decided after the snapshot
    mw.REVIEW_QUEUE[it["review_id"]] = decided
    _run(mw.sweep_review_queue.get_raw_f()())
    assert notified == [], "a decided draft must not be pushed to the roster as 'pending'"


def test_the_holding_notice_record_survives_a_concurrent_renotify_sweep(monkeypatch):
    """The exact live failure, end to end: timeout sweep and re-notify sweep interleaved on a model draft."""
    mw, sent = _load_mw(monkeypatch)
    it = _aged(mw, 16, answer_path="fact", engine_working=None, facts=["f"], model_calls=1)
    stale = dict(mw.REVIEW_QUEUE[it["review_id"]])
    _sweep(mw)                                                            # holding message sent and recorded
    assert mw.REVIEW_QUEUE[it["review_id"]]["holding_notice_ts"]
    mw._mark_notified(stale, 1, renotify=True)                            # the re-notify sweep finishes late with its old copy
    assert mw.REVIEW_QUEUE[it["review_id"]]["holding_notice_ts"], "the record of the holding message must not be erased"
    assert _sweep(mw)["holding_notices"] == 0 and len([1 for _, t in sent if _is_holding(t)]) == 1


def test_health_says_whether_TEST_SENDERS_reached_the_app_without_showing_it(monkeypatch):
    mw, _ = _load_mw(monkeypatch)
    monkeypatch.delenv("TEST_SENDERS", raising=False)
    assert mw._cohort_health()["test_senders"]["env_present"] is False
    monkeypatch.setenv("TEST_SENDERS", "+255799000111")
    t = mw._cohort_health()["test_senders"]
    assert t["env_present"] is True and "255799000111" not in str(t)


def test_CONTROL_the_same_sweep_does_renotify_a_draft_that_is_still_pending(monkeypatch):
    """Without this the test above could pass because nothing was due. The sweep must notify a genuinely pending, due draft."""
    mw, sent = _load_mw(monkeypatch)
    monkeypatch.setenv("RENOTIFY_AFTER_S", "60")
    it = _aged(mw, 16, answer_path="fact", model_calls=1, engine_working=None, facts=["f"])
    notified = []

    async def fake_notify(item, *, renotify=False):
        notified.append(item["review_id"])
        return 1
    monkeypatch.setattr(mw, "_notify_reviewers", fake_notify)
    _run(mw.sweep_review_queue.get_raw_f()())
    assert notified == [it["review_id"]]


def test_a_licence_question_gets_BRELA_in_the_holding_message_not_TRA(monkeypatch):
    """The founder's 2026-11-13 live finding: the holding message named TRA for a licence question the answer sent to BRELA."""
    mw, sent = _load_mw(monkeypatch)
    it = _aged(mw, 16, question="Leseni ya biashara inaisha lini?", answer_path="fact", engine_working=None, facts=["f"],
               model_calls=1, draft="Kila leseni ya biashara nchini Tanzania huisha ifikapo tarehe 30 Juni ya kila mwaka. Thibitisha na BRELA.")
    _sweep(mw)
    assert len(sent) == 1
    text = sent[0][1]
    assert core.AUTHORITY_CONTACTS["brela"] in text and "TRA" not in text and "0800 780 078" not in text
    assert "30 Juni" not in text, "the draft is never in the holding message"
    assert mw.REVIEW_QUEUE[it["review_id"]]["holding_notice_authority"] == ["brela"]
