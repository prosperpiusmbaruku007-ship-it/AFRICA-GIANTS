# -*- coding: utf-8 -*-
"""THE WELCOME (founder text, 2026-11-26).

* pinned verbatim, Swahili only: no English copy, no tagline, no GN codes (the old welcome had all three);
* the example questions the welcome advertises are VERIFIED ROUTES, pinned here against the REAL orchestrator, so a later routing change cannot
  silently break the welcome's own examples, and an example added to the welcome without a pinned route fails;
* the greeting path never calls the model (real `greet_and_send`, with a model that fails the test if it is touched);
* it does not repeat the first-contact disclosure verbatim.
Plants (R26): the old text fails the content checker; a broken route fails the route pin; an unpinned example fails the coverage test; a model
that IS called is counted by the same harness (the question path), so the zero on the greeting path means something.
"""
import os
import sys
import types

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "chike-whatsapp"))
from test_evidence_guard import _load_mw as _load_mw_real, _run, _real_run, _Silent, hc  # noqa: E402  (hc: the handler_core the loaded app really uses)
from chike import routing  # noqa: E402
from chike.orchestrator import Orchestrator  # noqa: E402

WELCOME_TEXT = (
    "Habari, karibu! 👋\n\n"
    "Mimi ni *Chike*, msaidizi (AI) wa Africa Giants. Ninajibu kwa Kiswahili maswali ya kodi na kanuni za biashara Tanzania.\n\n"
    "*Ukiwa nami:*\n"
    "💡 Unajua kiasi halisi cha kulipa: PAYE, NSSF, SDL, VAT\n"
    "⏰ Unajua tarehe za mwisho, unaepuka faini\n"
    "📋 Unajua usajili na leseni unazohitaji: TRA, BRELA, NSSF, OSHA\n\n"
    "*Jaribu kuuliza, kwa mfano:*\n"
    "• Mshahara wa TZS 800,000, PAYE ni kiasi gani?\n"
    "• Leseni ya biashara inadumu muda gani?\n\n"
    "Ili upate jibu sahihi, majibu mengi hukaguliwa kwanza, kwa hiyo jibu linaweza kuchukua muda.\n\n"
    "Uliza swali lako 👇"
)

OLD_WELCOME_SNIPPET = ('Hello! Welcome. 🙏 I am *Chike* — your assistant. _Fahamu Biashara Yako, Maarifa Yako._ '
                       '• Sheria — GN 487A, vibali, leseni • Mishahara — GN 605A, WCF _⚠ Beta: verify important answers with TRA._')

# every example the welcome advertises, with the route it must take TODAY: (path, topic, text the reply must contain)
PINNED_ROUTES = {
    "Mshahara wa TZS 800,000, PAYE ni kiasi gani?": ("engine:paye", None, "78,000"),
    "Leseni ya biashara inadumu muda gani?": ("engine:fixed_statement", "business_licence_validity", "miezi 12"),
}
# NOT advertised by the welcome today (the pasted text carries two examples). Pinned anyway so adding it to the welcome is one edit.
MEDICINES_QUESTION = ("Dawa zinatozwa VAT?", ("engine:fixed_statement", "vat_medicines", "MSAMAHA"))


def _content_problems(text):
    low = text.lower()
    bad = []
    for needle in ("hello", "welcome", "your ", "ask your", "i am", "beta", "fahamu biashara", "maarifa yako", "gn 487a", "gn 605a", " gn "):
        if needle in low:
            bad.append(needle)
    return bad


def _examples(text):
    lines = text.splitlines()
    i = next(k for k, ln in enumerate(lines) if ln.startswith("*Jaribu kuuliza"))
    out = []
    for ln in lines[i + 1:]:
        if ln.startswith("• "):
            out.append(ln[2:].strip())
        elif out:
            break
    return out


# ── the text ─────────────────────────────────────────────────────────────────────────────────────────────────
def test_the_welcome_is_the_founders_text_verbatim():
    assert hc.WELCOME == WELCOME_TEXT


def test_swahili_only_no_tagline_no_gn_codes():
    assert _content_problems(hc.WELCOME) == []
    assert _content_problems(OLD_WELCOME_SNIPPET), "positive control: the old welcome IS caught by the same checker"


def test_the_first_contact_message_opens_exactly_like_the_returning_user_welcome():
    """2026-11-27: a new number gets ONE message (FIRST_CONTACT_TEXT) that replaces the disclosure AND the welcome. It must open with the welcome's own
    introduction, benefits and examples, so a new user and a returning user see the same pinned example questions."""
    intro = hc.WELCOME.split("Ili upate jibu sahihi")[0]
    assert intro and hc.FIRST_CONTACT_TEXT.startswith(intro), "the first-contact message must begin with the welcome's introduction, verbatim"


def test_it_fits_a_whatsapp_message_and_carries_no_link():
    assert len(hc.WELCOME) < 4096 and "http" not in hc.WELCOME and "wa.me" not in hc.WELCOME


# ── the examples are verified routes ─────────────────────────────────────────────────────────────────────────
def _run_orch(q):
    return _real_run(Orchestrator(_Silent(), retriever=lambda x: [], ooc_phrases=[], in_scope_phrases=[]))(q)


def test_every_example_in_the_welcome_has_a_pinned_route():
    ex = _examples(hc.WELCOME)
    assert ex, "positive control: the extractor found the examples"
    assert set(ex) == set(PINNED_ROUTES), f"welcome examples {ex} vs pinned {list(PINNED_ROUTES)}: pin a route for every example"


def test_the_extractor_sees_an_added_example():
    extra = hc.WELCOME.replace("• Leseni ya biashara inadumu muda gani?", "• Leseni ya biashara inadumu muda gani?\n• Dawa zinatozwa VAT?")
    assert set(_examples(extra)) != set(PINNED_ROUTES), "plant: an unpinned third example is caught by the coverage test"


def _route_problems(question):
    """What is wrong with how `question` routes, against its pin. [] means it routes as pinned."""
    path, topic, needle = PINNED_ROUTES[question]
    out = _run_orch(question)
    bad = []
    if out["path"] != path:
        bad.append(f"path {out['path']!r} != {path!r}")
    if needle not in out["reply"]:
        bad.append(f"reply lacks {needle!r}")
    if topic and topic not in routing.fixed_statement_topics(question):
        bad.append(f"topic {topic!r} not matched")
    return bad


@pytest.mark.parametrize("question", sorted(PINNED_ROUTES))
def test_each_welcome_example_routes_as_it_does_today(question):
    assert _route_problems(question) == []


def test_the_medicines_fixed_statement_route_is_pinned_too():
    q, (path, topic, needle) = MEDICINES_QUESTION
    out = _run_orch(q)
    assert out["path"] == path and needle in out["reply"] and topic in routing.fixed_statement_topics(q)


def test_PLANT_a_routing_regression_is_caught_by_the_same_check(monkeypatch):
    q = "Leseni ya biashara inadumu muda gani?"
    assert _route_problems(q) == [], "positive control: it routes as pinned before the regression"
    monkeypatch.setattr(routing, "fixed_statement_topics", lambda text: [])      # what a routing regression looks like
    assert _route_problems(q), "the SAME check now reports the broken example"


# ── the greeting path never touches the model ────────────────────────────────────────────────────────────────
@pytest.fixture
def mw(monkeypatch):
    m = _load_mw_real(monkeypatch)
    monkeypatch.setenv("DISCLOSURE", "off")
    m.sent, m.model_calls = [], []

    async def fake_send(to, text):
        m.sent.append(text)
        return True, None
    monkeypatch.setattr(m, "_send_once", fake_send)

    class _Remote:
        @staticmethod
        async def aio(message):
            m.model_calls.append(message)
            return {"reply": "Ndiyo.", "working": "W", "facts": ["F"], "path": "engine:vat_registration"}

    class _Model:
        run = types.SimpleNamespace(remote=_Remote)
    monkeypatch.setattr(m, "ChikeModel", _Model)
    return m


def test_the_greeting_sends_the_welcome_and_never_calls_the_model_or_makes_a_card(mw):
    out = _run(mw.greet_and_send.get_raw_f()("255700000099@s.whatsapp.net"))
    assert out["send_ok"] is True and mw.sent == [hc.WELCOME]
    assert mw.model_calls == [] and len(mw.REVIEW_QUEUE) == 0


def test_positive_control_a_question_through_the_same_harness_DOES_call_the_model(mw):
    _run(mw.answer_and_send.get_raw_f()("255700000099@s.whatsapp.net", "Swali"))
    assert len(mw.model_calls) == 1, "so the zero above is a measurement, not an inert stub"


def test_the_onboarding_prefill_still_lands_on_this_path():
    ev = hc.parse_webhook({"event": "messages.received", "data": {"messages": {"key": {"remoteJid": "255700000099@s.whatsapp.net", "fromMe": False},
                                                                                "conversation": "Habari Chike"}}})
    assert ev["kind"] == "greeting"
