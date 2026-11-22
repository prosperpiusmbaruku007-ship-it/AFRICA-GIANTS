"""2026-11-22 (founder, from the preliminary Gate 2 controls): (1a) the SDL routing gaps behind #24, (1a') the headcount extractor, (1a'') D-FIDELITY-25, (1b) the NSSF party resolution behind #22.

The preliminary Gate 2 set is BURNED (its results were read): these tests use the two founding rows ONLY as regression specimens and add other phrasings for every limb. Every neighbour the change must NOT touch is a probe (R17), every
limb is planted (R26). Blast radius: eval/controls/sweep_sdl_party_routing_2026_11_22.py and sweep_headcount_copula_2026_11_22.py (read row by row)."""
import json
import os
import re

import pytest

from chike import answer_trace, clarification, fidelity, routing
from chike import swahili_numbers as swn
from chike.orchestrator import Orchestrator

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GP24 = "Naagiza vipuri vya magari kutoka Japan na kuviuza hapa Dar. Wafanyakazi wangu ni 12, je, natakiwa kulipa SDL na inaanzia wafanyakazi wangapi?"
GP22 = "Habari, kwa mfanyakazi mmoja mwajiri anatakiwa kuchangia asilimia ngapi ya mshahara wake NSSF?"
LIVE24 = {r["id"]: r for r in json.load(open(os.path.join(_ROOT, "eval", "results", "gate2_prelim_live_2026_11_22.json"), encoding="utf-8"))["rows"]}["gp_24"]["reply"]

# ── routing ───────────────────────────────────────────────────────────────────────────────────────
SDL_ROUTES = [
    GP24,
    "Nina wafanyakazi 12, je natakiwa kulipa SDL?",
    "Tuna wafanyakazi 6, je tunatakiwa kulipa SDL?",
    "Wafanyakazi wangu ni 15, je natakiwa kulipa SDL?",
    "SDL inaanzia wafanyakazi wangapi?",
    "SDL inaanza kutozwa kwa wafanyakazi wangapi?",
    "Kizingiti cha SDL ni wafanyakazi wangapi?",
]
NOT_SDL_ROUTES = [
    "Kama mfanyakazi anafikisha umri wa miaka 60, je bado anatakiwa kuchangia NSSF?",    # THIRD person: 'anatakiwa kuchangia' contains 'natakiwa kuchangia' as a substring
    "Kama mwajiri anatakiwa kulipa SDL kwa mfanyakazi aliyestaafu, ni kiasi gani?",       # third person
    "Kizingiti cha SDL ni wafanyakazi 4, sivyo?",                                          # a premise check: the digit is the RULE being checked
    "SDL inahitajika kuanzia wafanyakazi wangapi — 5 au 10?",                              # carries digits
    "Wafanyakazi wa nyumbani (domestic workers) — wanaathiri kizingiti cha SDL?",          # about what COUNTS toward the threshold
    "Kizingiti cha wafanyakazi kwa WCF — ni 10 kama SDL au tofauti?",
    "NSSF inaanzia wafanyakazi wangapi?",                                                  # another levy: no headcount threshold, and Path 1a is SDL only
    "Wafanyakazi wangapi wanapata kima cha chini cha mshahara Tanzania?",                  # no levy named
]


@pytest.mark.parametrize("q", SDL_ROUTES)
def test_the_sdl_question_routes_to_sdl(q):
    assert routing.detect_intent(q) == "sdl", q


@pytest.mark.parametrize("q", NOT_SDL_ROUTES)
def test_every_neighbour_keeps_its_old_route(q):
    assert routing.detect_intent(q) != "sdl" or "SDL" not in q or "kulipa SDL kwa mfanyakazi aliyestaafu" in q, q
    assert routing.detect_intent(q) not in ("nssf",) or "NSSF" not in q or "anatakiwa kuchangia" not in q, q


def test_the_third_person_cue_collision_is_closed():
    assert routing.detect_intent("Kama mfanyakazi anafikisha umri wa miaka 60, je bado anatakiwa kuchangia NSSF?") == "none"
    assert routing.asks_applicability("Nina wafanyakazi 12, je natakiwa kulipa SDL?")
    assert not routing.asks_applicability("Mfanyakazi anatakiwa kulipa nini?")           # 'anatakiwa', not 'natakiwa'


def test_a_money_ask_still_wins_over_the_new_applicability_cue():
    assert not routing.asks_applicability("Natakiwa kulipa SDL kiasi gani kwa mishahara ya milioni 20?")
    assert routing.detect_intent("Natakiwa kulipa SDL kiasi gani kwa mishahara ya milioni 20?") == "sdl"      # via the amount path, unchanged


def test_plant_the_first_person_cue_removed_is_caught(monkeypatch):
    monkeypatch.setattr(routing, "_APPLICABILITY_FIRST_PERSON", re.compile(r"(?!x)x"))
    assert [q for q in SDL_ROUTES[1:4] if routing.detect_intent(q) != "sdl"]


def test_plant_the_first_person_cue_as_a_substring_is_caught(monkeypatch):
    monkeypatch.setattr(routing, "_APPLICABILITY_FIRST_PERSON", re.compile(r"natakiwa\s+(?:kulipa|kuchangia)"))
    assert routing.detect_intent("Kama mfanyakazi anafikisha umri wa miaka 60, je bado anatakiwa kuchangia NSSF?") != "none"


def test_plant_the_threshold_route_disabled_is_caught(monkeypatch):
    monkeypatch.setattr(routing, "_SDL_THRESHOLD_COUNT_ASK", re.compile(r"(?!x)x"))
    assert routing.detect_intent("SDL inaanzia wafanyakazi wangapi?") != "sdl"


def test_plant_the_threshold_route_made_to_take_digits_is_caught(monkeypatch):
    """Without the no-digit rule a premise check would be re-routed to the applicability branch."""
    monkeypatch.setattr(routing, "_has_number", lambda ql: False)
    monkeypatch.setattr(routing, "_SDL_THRESHOLD_COUNT_ASK", re.compile(r"kizingiti|wangapi", re.IGNORECASE))
    assert routing.detect_intent("Kizingiti cha SDL ni wafanyakazi 4, sivyo?") == "sdl"


# ── the headcount extractor ───────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("q,want", [
    ("Wafanyakazi wangu ni 12, je, natakiwa kulipa SDL?", 12),
    ("Wafanyakazi wetu ni 20, SDL inanihusu?", 20),
    ("Wafanyakazi wake ni 5 tu", 5),
    ("Nina wafanyakazi 12, je nalipa SDL?", 12),                                          # the old form is untouched
    ("Wafanyakazi wetu ni 10 au zaidi, SDL ni lazima?", None),                              # a RULE, not the user's count
    ("Wafanyakazi ni 12, je nalipa SDL?", None),                                            # no possessive: not read
    ("Nina wafanyakazi 8 na wafanyakazi wangu ni 12?", None),                               # two counts: the safe direction
])
def test_the_noun_first_copula_headcount(q, want):
    assert swn.sole_headcount(q) == want, q


def test_plant_the_noun_first_copula_disabled_is_caught(monkeypatch):
    monkeypatch.setattr(swn, "_NOUN_COPULA_HEADCOUNT", re.compile(r"(?!x)x"))
    assert swn.sole_headcount("Wafanyakazi wangu ni 12, je, natakiwa kulipa SDL?") is None


# ── NSSF party ────────────────────────────────────────────────────────────────────────────────────
PARTY = [
    (GP22, "employer"),
    ("Kwa mfanyakazi mmoja, mwajiri anapaswa kuchangia kiasi gani NSSF?", "employer"),
    ("Mwajiri anachangia asilimia ngapi NSSF?", "employer"),
    ("Mchango wa mwajiri kwa NSSF ni asilimia ngapi?", "employer"),
    ("Mwajiri anachangia na mfanyakazi anachangia asilimia ngapi NSSF?", "total"),          # both parties named as contributors: the total
    ("NSSF ya mfanyakazi ni asilimia ngapi?", "employee"),
    ("Mchango wake wa NSSF ni asilimia ngapi?", "employee"),
    ("Nilipe SDL, NSSF, PAYE na WCF kwa mfanyakazi mmoja mwenye TZS 800,000 — nionyeshe vyote.", "total"),   # 'kwa mfanyakazi' is a preposition + noun, not an employee cue
    ("Kwa mfanyakazi mmoja NSSF inakatwa kiasi gani?", "employee"),                       # 'inakatwa' is a real employee concord and still counts
]


@pytest.mark.parametrize("q,want", PARTY)
def test_nssf_party_resolution(q, want):
    assert routing.nssf_party(q) == want, q


def test_kwa_mfanyakazi_is_no_longer_an_employee_cue():
    assert routing.nssf_party("Kwa mfanyakazi mmoja NSSF ni asilimia ngapi?") == "total"
    assert routing._has_word_cue("ya mfanyakazi", "wa mfanyakazi") is False and routing._has_word_cue("mchango wa mfanyakazi", "wa mfanyakazi")


def test_plant_the_substring_match_restored_is_caught(monkeypatch):
    monkeypatch.setattr(routing, "_has_word_cue", lambda ql, cue: cue in ql)
    assert routing.nssf_party("Nilipe SDL, NSSF, PAYE na WCF kwa mfanyakazi mmoja mwenye TZS 800,000 — nionyeshe vyote.") == "employee"


def test_plant_the_employer_verb_cue_removed_is_caught(monkeypatch):
    monkeypatch.setattr(routing, "_NSSF_EMPLOYER_VERB", re.compile(r"(?!x)x"))
    assert routing.nssf_party(GP22) != "employer"


def test_plant_the_employee_window_allowed_to_cross_the_employer_is_caught(monkeypatch):
    """The first draft: 'mfanyakazi mmoja mwajiri anatakiwa kuchangia' let the EMPLOYEE verb window swallow the employer's verb, so the question resolved to 'total'."""
    monkeypatch.setattr(routing, "_NSSF_EMPLOYEE_VERB", re.compile(r"(?<![a-z])mfanyakazi\s+(?:\w+\s+){0,2}?(?:anatakiwa\s+kuchangia|kuchangia)(?![a-z])"))
    assert routing.nssf_party(GP22) == "total"


# ── D-FIDELITY-25 ─────────────────────────────────────────────────────────────────────────────────
Q12 = "Nina wafanyakazi 12. Je, nalipa SDL?"
FLAG = [
    (GP24, LIVE24),                                                                      # the founding specimen, verbatim (both of its sentences)
    (Q12, "Hapana. Kwa wafanyakazi 12 huna wajibu wa kulipa SDL."),
    (Q12, "SDL haitozwi kwa biashara yako."),
    ("Wafanyakazi wangu ni 20, je, natakiwa kulipa SDL?", "Hauhitaji kulipa SDL kwa sasa."),
    ("Nina wafanyakazi 15 kwenye duka langu. SDL inanihusu?", "SDL haikuhusu kwa kuwa biashara yako ni ndogo."),
]
PASS = [   # the probes that should come back CLEAN do the work
    (Q12, "Ndiyo. Una wafanyakazi 12 (10 au zaidi), hivyo SDL inatozwa — asilimia 3.5 ya jumla ya mishahara."),
    (Q12, "Mwajiri mwenye wafanyakazi 10 au zaidi ana wajibu wa kulipa SDL. Mwenye wafanyakazi chini ya 10 hana wajibu wa kulipa SDL."),                 # the engine's own statement
    (Q12, "Si kweli kwamba huna wajibu wa kulipa SDL; unalipa."),                                                                                              # a negated denial
    ("Nina wafanyakazi 6, je nalipa SDL?", "Hapana. SDL haihusiki: una wafanyakazi 6 (chini ya 10)."),                                                         # below the threshold
    ("Nina wafanyakazi 12 wa shule ya msingi iliyosajiliwa. Je, nalipa SDL?", "Shule zilizosajiliwa zimesamehewa SDL, hivyo hulipi."),                     # an exempt employer
    ("Nina wafanyakazi 12 shambani. Je, nalipa SDL?", "Waajiri wa mashamba hawalipi SDL kwa wafanyakazi wa kilimo tu."),                                      # an exempt employer, vetoed in the question
    ("Kizingiti cha SDL ni wafanyakazi 10 au ni kulingana na mapato ya biashara?", "A large business with only 9 employees is not required to pay SDL."),    # a question about the RULE
    ("Msimu wa mavuno nina wafanyakazi 12, msimu mwingine 6 — nalipaje SDL?", "Kwa miezi yenye 6 huna wajibu wa SDL."),                                      # a second, smaller count
    ("Nina wafanyakazi 12, je nalipa NSSF?", "NSSF haina kizingiti: unalipa tangu mfanyakazi wa kwanza, hakuna haja ya SDL hapa."),                          # not an SDL question
    ("Nina wafanyakazi 12. Je, nalipa SDL?", "Ndiyo, unalipa SDL."),
    # protected ONLY by the threshold-question veto (no small digit anywhere): a plant removing that veto must flip it
    ("Kizingiti cha SDL ni wafanyakazi 10 au ni kulingana na mapato ya biashara?", "Biashara kubwa yenye wafanyakazi wachache haitakiwi kulipa SDL."),
]


@pytest.mark.parametrize("q,b", FLAG)
def test_sdl_denied_for_a_stated_headcount_at_or_above_ten_is_flagged(q, b):
    assert fidelity.sdl_denied_above_threshold(q, b), b


@pytest.mark.parametrize("q,b", PASS)
def test_a_correct_or_unrelated_sentence_is_not_flagged(q, b):
    assert fidelity.sdl_denied_above_threshold(q, b) == [], b


def test_the_specimen_is_the_live_reply_and_both_sentences_flag():
    assert "haihitaji malipo ya SDL" in LIVE24 and len(fidelity.sdl_denied_above_threshold(GP24, LIVE24)) == 2


def test_the_restatement_never_trips_its_own_guard_and_states_the_rule():
    t = clarification.CONSTANT_RESTATEMENTS["sdl_applies_at_threshold"]
    assert "10 au zaidi" in t and "3.5" in t and "Kifungu" not in t
    assert fidelity.sdl_denied_above_threshold(GP24, t) == [] and fidelity.body_contradicts_d16(GP24, t) == []


@pytest.mark.parametrize("name,pattern", [("_D25_EXEMPT", r"(?!x)x"), ("_D25_BELOW", r"(?!x)x"), ("_D25_NEGATED_DENIAL", r"(?!x)x"), ("_D25_THRESHOLD_Q", r"(?!x)x"), ("_D25_SMALL_NUMBER", r"(?!x)x")])
def test_plant_each_veto_removed_is_caught(monkeypatch, name, pattern):
    monkeypatch.setattr(fidelity, name, re.compile(pattern))
    assert [1 for q, b in PASS if fidelity.sdl_denied_above_threshold(q, b)], name


def test_plant_the_denial_cue_removed_is_caught(monkeypatch):
    monkeypatch.setattr(fidelity, "_D25_DENY", re.compile(r"(?!x)x"))
    assert [1 for q, b in FLAG if not fidelity.sdl_denied_above_threshold(q, b)]


def test_the_headcount_floor_is_load_bearing_once_the_small_number_veto_is_off(monkeypatch):
    """A digit count below ten always trips the small-number veto first, so the floor is defence in depth: prove it works on its own by switching that veto off, then switch the floor off too."""
    q, b = "Nina wafanyakazi 8, je nalipa SDL?", "Huna wajibu wa kulipa SDL."
    monkeypatch.setattr(fidelity, "_D25_SMALL_NUMBER", re.compile(r"(?!x)x"))
    assert fidelity.sdl_denied_above_threshold(q, b) == []                       # the floor alone holds
    monkeypatch.setattr(swn, "sole_headcount", lambda t: 99)
    assert fidelity.sdl_denied_above_threshold(q, b)                             # plant: the floor removed -> it flags


def test_the_patterns_contain_no_control_characters():
    for p in (fidelity._D25_Q_SDL, fidelity._D25_EXEMPT, fidelity._D25_DENY, fidelity._D25_BELOW, fidelity._D25_NEGATED_DENIAL, fidelity._D25_THRESHOLD_Q, fidelity._D25_SMALL_NUMBER,
              routing._APPLICABILITY_FIRST_PERSON, routing._SDL_THRESHOLD_COUNT_ASK, routing._NSSF_EMPLOYER_VERB, routing._NSSF_EMPLOYEE_VERB, swn._NOUN_COPULA_HEADCOUNT):
        assert not any(ord(c) < 32 for c in p.pattern), p.pattern


# ── end to end ────────────────────────────────────────────────────────────────────────────────────
class _Backend:
    def __init__(self, reply="MODEL-REPLY."):
        self.reply, self.calls = reply, 0

    def generate(self, prompt, params=None):
        self.calls += 1
        return self.reply


def _orch(reply="MODEL-REPLY."):
    b = _Backend(reply)
    return Orchestrator(b, retriever=lambda q: ["Kizingiti cha SDL ni wafanyakazi 10 au zaidi."], ooc_phrases=[], in_scope_phrases=[]), b


def test_gp24_is_now_answered_on_the_sdl_engine_and_the_engines_verdict_names_the_stated_count():
    """With the noun-first copula read, the stated 12 reaches the applicability branch: the engine's verdict ('Ndiyo. Una wafanyakazi 12 (10 au zaidi)...') is appended to a model-written body. The model body is the open
    question this test cannot settle offline (a model can still write 'Hapana' above it): the targeted live check reads it."""
    o, b = _orch("MODEL-REPLY.")
    r = o.answer(GP24)
    t = answer_trace.trace(r)
    assert t["path"] == "engine:sdl", t
    assert "Una wafanyakazi 12 (10 au zaidi)" in r.text and "SDL inatozwa" in r.text, r.text


def test_gp22_is_now_the_employer_share_model_free():
    o, b = _orch("MODEL-REPLY.")
    r = o.answer(GP22)
    t = answer_trace.trace(r)
    assert t["path"] == "engine:nssf" and t["model_calls"] == 0 and b.calls == 0, t
    assert "Sehemu ya mwajiri ni asilimia 10" in r.text and "HAIKATWI" in r.text and "Sehemu ya mfanyakazi" not in r.text


def test_the_guard_replaces_the_wrong_reply_on_a_phrasing_the_route_still_misses():
    q = "Nina wafanyakazi 12 dukani. Naomba kujua kuhusu SDL."
    assert routing.detect_intent(q) == "none", "this phrasing must MISS the route, or it is not exercising the guard"
    o, b = _orch(LIVE24)
    r = o.answer(q)
    t = answer_trace.trace(r)
    assert b.calls >= 1 and t["guards"] == ["replaced"], t
    assert clarification.CONSTANT_RESTATEMENTS["sdl_applies_at_threshold"] in r.text and "haihitaji malipo ya SDL" not in r.text


def test_a_correct_model_reply_on_that_phrasing_is_untouched():
    q = "Nina wafanyakazi 12 dukani. Naomba kujua kuhusu SDL."
    o, _ = _orch("Ndiyo, una wafanyakazi 12 (10 au zaidi), hivyo unalipa SDL. Thibitisha na TRA.")
    r = o.answer(q)
    assert answer_trace.trace(r)["guards"] == [] and "unalipa SDL" in r.text
