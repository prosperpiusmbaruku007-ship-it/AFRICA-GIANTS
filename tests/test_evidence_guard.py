"""An empty evidence panel must be impossible to mistake for "nothing to check" (2026-11-12).

THE DEFECT: all 7 drafts ever held carried engine_working=null and facts=[] -- `ChikeModel.run` returned only the
reply -- and nothing said so loudly. The push printed "VIGEZO VILIVYOTUMIKA (0)" in the same quiet type as everything
else. These tests pin (1) the gate, (2) every place it must be loud, and (3) the chain that must deliver the
evidence: they FAIL if `run` ever stops returning it, and they fail in BOTH directions (a regression is loud, and a
healthy draft is not cried-wolf).
"""
import ast
import asyncio
import importlib.util
import os
import sys
import types

import pytest

from chike.model_abstraction import ModelBackend
from chike.orchestrator import Orchestrator

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("hc_evguard", os.path.join(_ROOT, "chike-whatsapp", "handler_core.py"))
hc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hc)


# ── 1. the gate, as a table ────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("item,state,loud", [
    ({"answer_path": "fact", "facts": [], "engine_working": None}, "none", True),
    ({"answer_path": None, "facts": [], "engine_working": None}, "path_missing", True),
    ({"facts": [], "engine_working": None}, "path_missing", True),                 # every one of the 7 real items
    ({"answer_path": "fact", "facts": ["F"], "engine_working": None}, "ok", False),
    ({"answer_path": "engine:sdl", "facts": [], "engine_working": "SDL = 3.5% x 6,000,000"}, "ok", False),
    ({"answer_path": "engine:vat_registration", "facts": [], "engine_working": None}, "deterministic", False),
    ({"answer_path": "engine:vat_registration:ask", "facts": [], "engine_working": None}, "deterministic", False),
    ({"answer_path": "clarification", "facts": [], "engine_working": None}, "deterministic", False),
    ({"answer_path": "refusal", "facts": [], "engine_working": None}, "deterministic", False),
    ({"fallback": True, "facts": [], "engine_working": None}, "not_applicable", False),
])
def test_the_evidence_gate(item, state, loud):
    assert hc.evidence_state(item) == state and hc.evidence_is_loud(item) is loud


def test_all_seven_real_items_that_were_held_would_have_been_loud():
    """The measured population: engine_working null, facts [], no answer_path (the field did not exist)."""
    for i in range(7):
        assert hc.evidence_is_loud({"review_id": f"r{i}", "engine_working": None, "facts": [], "draft": "Ndiyo."})


# ── 2. every place it must be loud ─────────────────────────────────────────────────────────────────
BARE = {"review_id": "r1", "question": "q", "draft": "Ndiyo, unapaswa kujiandikisha.", "sender_tail": "5913",
        "facts": [], "engine_working": None, "answer_path": "fact"}
GOOD = dict(BARE, facts=["Fact A: EFD haina kizingiti."], answer_path="fact")


def test_the_push_leads_with_the_warning_BEFORE_the_question():
    text = hc.notification_text(BARE, "https://x/d?r=1", "Prosper")
    assert hc.EVIDENCE_WARNING_SW in text and hc.EVIDENCE_WARNING_EN in text
    assert text.index(hc.EVIDENCE_WARNING_SW) < text.index("SWALI:"), "a phone reader must meet it before the draft"
    assert text.index(hc.EVIDENCE_WARNING_SW) < text.index("RASIMU:")


def test_the_push_for_a_healthy_draft_does_not_cry_wolf():
    assert hc.EVIDENCE_WARNING_SW not in hc.notification_text(GOOD, "https://x/d?r=1", "Prosper")
    assert hc.EVIDENCE_WARNING_SW not in hc.notification_text(
        dict(BARE, answer_path="engine:vat_registration"), "https://x/d?r=1", "Prosper")


def test_a_missing_path_says_the_pipeline_itself_may_be_broken():
    t = hc.notification_text(dict(BARE, answer_path=None), "https://x/d?r=1", "Prosper")
    assert hc.EVIDENCE_PATH_MISSING in t
    assert hc.EVIDENCE_PATH_MISSING not in hc.notification_text(BARE, "https://x/d?r=1", "Prosper")


def _load_mw(monkeypatch):
    from conftest import isolate_modal_stores
    for k, v in {"REVIEW_D_URL": "https://d.example", "REVIEW_CLAIM_URL": "https://c.example",
                 "REVIEW_ACT_URL": "https://a.example"}.items():
        monkeypatch.setenv(k, v)                       # read at IMPORT time
    pkg = types.ModuleType("chike_whatsapp")
    pkg.handler_core = hc
    monkeypatch.setitem(sys.modules, "chike_whatsapp", pkg)
    monkeypatch.setitem(sys.modules, "chike_whatsapp.handler_core", hc)
    spec = importlib.util.spec_from_file_location("chike_mw_evguard", os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"))
    mw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mw)
    isolate_modal_stores(mw, monkeypatch)
    monkeypatch.setenv("SENDER_SALT", "salt")
    monkeypatch.setenv("SUPERVISED", "1")
    monkeypatch.setenv("DISCLOSURE", "off")
    monkeypatch.setenv("REVIEWER_ROSTER", "+255700000011:Prosper")
    monkeypatch.setenv("REVIEW_SIGNING_KEY", "test-key")
    return mw


def test_both_cards_render_the_banner_loudly_and_only_when_it_should(monkeypatch):
    mw = _load_mw(monkeypatch)
    loud = mw._evidence_banner(BARE)
    assert "HAKUNA USHAHIDI" in loud and "NO EVIDENCE" in loud and "#ff4d4d" in loud
    assert mw._evidence_banner(GOOD) == ""
    assert mw._evidence_banner(dict(BARE, answer_path="engine:sdl:ask")) == ""
    assert mw._evidence_banner({"fallback": True}) == ""
    src = open(os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"), encoding="utf-8").read()
    assert src.count("+ _evidence_banner(it)") == 2, "the overview card AND the reviewer's own /d page"
    # ...and on BOTH it must precede the question, i.e. be the first thing a reviewer meets
    for marker in ('+ "<div class=q>" + _esc(it.get("question"))', "+ '<div class=lock id=lock>"):
        assert src.index("+ _evidence_banner(it)") < src.index(marker)


def test_health_counts_pending_drafts_that_carry_no_evidence(monkeypatch):
    mw = _load_mw(monkeypatch)
    mw.REVIEW_QUEUE["a"] = dict(BARE, review_id="a", status="pending")
    mw.REVIEW_QUEUE["b"] = dict(GOOD, review_id="b", status="pending")
    mw.REVIEW_QUEUE["c"] = dict(BARE, review_id="c", status="sent")
    h = mw._review_queue_health()
    assert h["pending"] == 2 and h["pending_without_evidence"] == 1


# ── 3. the chain: `ChikeModel.run` must keep returning the evidence ─────────────────────────────────
class _Silent(ModelBackend):
    def generate(self, prompt, params=None):
        return ""


class _Says(ModelBackend):
    def generate(self, prompt, params=None):
        return "Ndiyo, hiyo ni sahihi."


def _real_run(orchestrator):
    """Compile and run the ACTUAL body of ChikeModel.run from chike-inference/modal_app.py -- not a copy, not
    a reading of its source: the deployed method, with a fake `self` whose only job is to hand it an
    orchestrator. If someone edits run() to return less, THIS is what fails."""
    path = os.path.join(_ROOT, "chike-inference", "modal_app.py")
    src = open(path, encoding="utf-8").read()
    tree = ast.parse(src)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "ChikeModel")
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "run")
    fn.decorator_list = []                                    # @modal.method() is Modal's, not ours
    ns = {"PIPELINE": "v16", "os": os, "sys": sys, "time": __import__("time")}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), path, "exec"), ns)
    fake = types.SimpleNamespace(_orchestrator=lambda: orchestrator)
    return lambda message: ns["run"](fake, message)


def test_run_returns_path_working_and_facts_for_an_ENGINE_answer():
    out = _real_run(Orchestrator(_Silent(), retriever=lambda q: [], ooc_phrases=[], in_scope_phrases=[]))(
        "Nina wafanyakazi 12, mishahara yote kwa mwezi ni milioni 6. SDL nitalipa kiasi gani?")
    assert set(out) >= {"reply", "path", "working", "facts"}, sorted(out)
    assert out["path"] == "engine:sdl" and out["working"] and "210,000" in out["working"]


def test_run_returns_path_working_and_facts_for_a_FACT_answer():
    facts = ["Fact A: EFD haina kizingiti.", "Fact B: SDL ni 3.5%."]
    out = _real_run(Orchestrator(_Says(), retriever=lambda q: facts, ooc_phrases=[], in_scope_phrases=[]))(
        "Faini ya kuchelewa kulipa NSSF ni kiasi gani?")
    assert out["path"] == "fact" and set(out["facts"]) == set(facts), out


def test_run_is_not_allowed_to_go_back_to_returning_only_the_reply():
    out = _real_run(Orchestrator(_Says(), retriever=lambda q: ["F"], ooc_phrases=[], in_scope_phrases=[]))(
        "Faini ya kuchelewa kulipa NSSF ni kiasi gani?")
    assert out != {"reply": out["reply"]}, "run() returned only the reply -- the review card would be empty again"


# ── 4. the handler end to end: a bare-reply model is LOUD, an evidence-bearing one is not ───────────
def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _drive(mw, monkeypatch, model_result):
    pushes = []

    async def fake_send(to, text):
        pushes.append(text)
        return True, None
    monkeypatch.setattr(mw, "_send_once", fake_send)

    class _Remote:
        @staticmethod
        async def aio(message):
            return model_result

    class _Model:
        run = types.SimpleNamespace(remote=_Remote)
    monkeypatch.setattr(mw, "ChikeModel", _Model)
    _run(mw.answer_and_send.get_raw_f()("255700000099@s.whatsapp.net", "Swali la mtihani"))
    items = list(mw.REVIEW_QUEUE.values())
    assert len(items) == 1, items
    return items[0], pushes


def test_a_model_that_returns_only_the_reply_produces_a_LOUD_item_and_a_LOUD_push(monkeypatch):
    """The 2026-11-11 state, reproduced: this is exactly what the reviewer received for all 7 drafts."""
    mw = _load_mw(monkeypatch)
    item, pushes = _drive(mw, monkeypatch, {"reply": "Ndiyo, unapaswa kujiandikisha."})
    assert hc.evidence_is_loud(item) and item["facts"] == [] and item["engine_working"] is None
    assert pushes and all(hc.EVIDENCE_WARNING_SW in p for p in pushes), "the reviewer's push must lead with it"
    assert hc.EVIDENCE_PATH_MISSING in pushes[0], "no path at all = the pipeline itself is broken"


def test_a_model_that_returns_evidence_produces_a_card_with_it_and_a_quiet_push(monkeypatch):
    mw = _load_mw(monkeypatch)
    item, pushes = _drive(mw, monkeypatch, {"reply": "Ndiyo.", "working": "SDL = 3.5% x 6,000,000 = 210,000",
                                            "facts": ["Fact A"], "path": "engine:sdl"})
    assert item["engine_working"].startswith("SDL = 3.5%") and item["facts"] == ["Fact A"]
    assert item["answer_path"] == "engine:sdl" and not hc.evidence_is_loud(item)
    assert pushes and all(hc.EVIDENCE_WARNING_SW not in p for p in pushes)
    assert any("Fact A" in p and "SDL = 3.5%" in p for p in pushes), "the push must carry the evidence itself"


def test_a_fact_path_answer_that_retrieved_nothing_is_loud_even_though_the_path_is_recorded(monkeypatch):
    """The model answered from NOTHING. The path says so; the card must not read as 'nothing to check'."""
    mw = _load_mw(monkeypatch)
    item, pushes = _drive(mw, monkeypatch, {"reply": "Ndiyo.", "working": None, "facts": [], "path": "fact"})
    assert hc.evidence_state(item) == "none" and hc.EVIDENCE_PATH_MISSING not in pushes[0]
    assert all(hc.EVIDENCE_WARNING_SW in p for p in pushes)


# ── 5. the REAL /d page, rendered: the banner is on the page a reviewer actually opens ──────────────
def _render_d(mw, item):
    key = "test-key"
    number = mw._settings().roster[0][0]      # the roster's NORMALISED JID, not the raw "+255..." string
    mw.REVIEW_QUEUE[item["review_id"]] = item
    rid = hc.reviewer_id(key, number)
    tok = hc.review_token(key, item["review_id"], number)
    resp = mw._d_page(item["review_id"], rid, tok)
    return resp.body.decode("utf-8") if hasattr(resp, "body") else str(resp)


def _item(**kw):
    base = {"review_id": "2026-11-12T00:00:00+00:00-abcd1234", "ts_held": "2026-11-12T00:00:00+00:00",
            "question": "Mauzo yangu ni milioni 250 kwa mwaka. Je, ni lazima nijisajili VAT",
            "draft": "Ndiyo, unapaswa kujiandikisha kwa ajili ya VAT.", "status": "pending", "sender_tail": "5913",
            "sender_hash": "abc", "facts": [], "engine_working": None, "answer_path": "fact"}
    base.update(kw)
    return base


def test_the_real_reviewer_page_shows_the_loud_block_for_a_bare_draft(monkeypatch):
    mw = _load_mw(monkeypatch)
    html = _render_d(mw, _item())
    assert "HAKUNA USHAHIDI" in html and "NO EVIDENCE" in html and "#ff4d4d" in html
    assert html.index("HAKUNA USHAHIDI") < html.index("Ndiyo, unapaswa"), "the warning must come BEFORE the draft"


def test_the_real_reviewer_page_for_an_engine_draft_shows_working_and_path_and_no_alarm(monkeypatch):
    mw = _load_mw(monkeypatch)
    html = _render_d(mw, _item(answer_path="engine:vat_registration",
                               engine_working="Mauzo TZS 250,000,000 >= TZS 200,000,000 (miezi 12)"))
    assert "HAKUNA USHAHIDI" not in html
    assert "engine:vat_registration" in html and "250,000,000" in html


def test_the_real_reviewer_page_flags_a_missing_path_as_a_broken_pipeline(monkeypatch):
    mw = _load_mw(monkeypatch)
    html = _render_d(mw, _item(answer_path=None))
    assert "HAKUNA USHAHIDI" in html and "evidence pipeline itself may be broken" in html
