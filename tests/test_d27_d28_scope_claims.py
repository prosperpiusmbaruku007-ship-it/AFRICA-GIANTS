"""2026-11-22 D-FIDELITY-27 (SDL scope stated by premises) and D-FIDELITY-28 (NSSF contributions tied to age 60): founding specimens are the two LIVE replies of build a78f5d0. R17: the probes that should come back CLEAN do the work (a denial of
the rule, pension-eligibility and early-retirement sentences, a sentence denying the age tie). Real orchestrator path, replacement copy, and PLANTS (R26)."""
import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
from chike import clarification, fidelity           # noqa: E402
from chike.orchestrator import Orchestrator        # noqa: E402

Q27 = "Wafanyakazi wa nyumbani (domestic workers) — wanaathiri kizingiti cha SDL?"
SPEC27 = ("Hapana — wafanyakazi wa nyumbani (domestic workers) hawamo katika kizingiti cha SDL. SDL inalenga waajiri wenye wafanyakazi 10+ katika MAENEO YA BIASHARA (commercial premises). "
          "Wafanyakazi wa nyumbani wanaofanya kazi nyumbani kwa familia moja (si ofisi ya biashara) hawaingii kwenye kizingiti cha SDL. Thibitisha na TRA (tra.go.tz).")
Q28 = "Kama mfanyakazi anafikisha umri wa miaka 60, je bado anatakiwa kuchangia NSSF?"
SPEC28 = "Ndiyo, kwa mujibu wa sheria, michango ya NSSF huendelea hadi umri wa miaka 60. Thibitisha na NSSF (nssf.go.tz)."

CLEAN27 = ["SDL haitegemei maeneo ya biashara; inategemea idadi ya wafanyakazi.",
           "SDL hutozwa kwa kila mwajiri mwenye wafanyakazi 10 au zaidi.",
           "Kizingiti cha SDL ni wafanyakazi 10 au zaidi."]
CLEAN28 = ["Pensheni ya uzee hupatikana ukifikisha miaka 60 na michango 180.",
           "Kustaafu mapema kunawezekana kuanzia miaka 55.",
           "Michango haikomi ukifika miaka 60; haitegemei umri.",
           "Si kweli kwamba michango ya NSSF huendelea hadi umri wa miaka 60.",
           "Ukifikisha miaka 60 unaweza kudai pensheni.",
           "Mwajiri analipa michango ya NSSF kila mwezi kwa mfanyakazi."]


def test_specimens_are_flagged():
    assert fidelity.sdl_scope_by_premises(Q27, SPEC27)
    assert fidelity.nssf_contributions_tied_to_age_60(Q28, SPEC28)
    assert fidelity.nssf_contributions_tied_to_age_60("q", "Ukifikisha miaka 60 huhitaji kuchangia NSSF tena.")


@pytest.mark.parametrize("body", CLEAN27)
def test_clean_27(body):
    assert fidelity.sdl_scope_by_premises(Q27, body) == []


@pytest.mark.parametrize("body", CLEAN28)
def test_clean_28(body):
    assert fidelity.nssf_contributions_tied_to_age_60(Q28, body) == []


def test_both_are_routed_through_the_d16_family_with_a_restatement():
    assert ("sdl_scope_by_premises", fidelity.sdl_scope_by_premises(Q27, SPEC27)[0]) in fidelity.body_contradicts_d16(Q27, SPEC27)
    assert [t for t, _ in fidelity.body_contradicts_d16(Q28, SPEC28)] == ["nssf_contributions_age_60"]
    for t in ("sdl_scope_by_premises", "nssf_contributions_age_60"):
        assert t in clarification.CONSTANT_RESTATEMENTS


def test_the_restatements_hedge_and_claim_nothing_the_sources_do_not_say():
    sdl = clarification.CONSTANT_RESTATEMENTS["sdl_scope_by_premises"]
    age = clarification.CONSTANT_RESTATEMENTS["nssf_contributions_age_60"]
    assert "hakuna kinachotuonyesha kwa uhakika" in sdl and "tra.go.tz" in sdl and "10 au zaidi" in sdl
    assert "Kifungu" not in sdl + age                                       # R44: no section number in served text
    assert "umri wa pensheni" in age and "180" in age and "nssf.go.tz" in age
    assert not re.search(r"michango (?:huendelea|inaendelea|inakoma|huisha) (?:hadi|baada)", age)   # asserts neither "continue" nor "stop"


class _B:
    def __init__(self, r):
        self.r = r

    def generate(self, prompt, params=None):
        return self.r


def _answer(q, body):
    return Orchestrator(_B(body), retriever=lambda x: ["f"], ooc_phrases=[], in_scope_phrases=[]).answer(q).text


def test_real_path_replaces_each_specimen_with_its_restatement():
    assert clarification.CONSTANT_RESTATEMENTS["sdl_scope_by_premises"] in _answer(Q27, SPEC27)
    t = _answer(Q28, SPEC28)
    assert clarification.CONSTANT_RESTATEMENTS["nssf_contributions_age_60"] in t and "huendelea hadi" not in t


def test_real_path_leaves_a_clean_body_alone():
    assert "SDL haitegemei maeneo ya biashara" in _answer(Q27, CLEAN27[0])
    assert "Pensheni ya uzee hupatikana" in _answer(Q28, CLEAN28[0])


def test_plant_unwired_lets_the_specimens_through(monkeypatch):
    monkeypatch.setattr(fidelity, "sdl_scope_by_premises", lambda q, b: [])
    monkeypatch.setattr(fidelity, "nssf_contributions_tied_to_age_60", lambda q, b: [])
    assert "MAENEO YA BIASHARA" in _answer(Q27, SPEC27) and "huendelea hadi umri wa miaka 60" in _answer(Q28, SPEC28)


def test_plant_the_negation_vetoes_removed_flag_the_denials(monkeypatch):
    monkeypatch.setattr(fidelity, "_D27_NEG", re.compile(r"(?!x)x"))
    monkeypatch.setattr(fidelity, "_D28_NEG", re.compile(r"(?!x)x"))
    assert fidelity.sdl_scope_by_premises(Q27, CLEAN27[0])
    assert fidelity.nssf_contributions_tied_to_age_60(Q28, CLEAN28[3]), "the denial must match the claim pattern so the veto alone is what protects it"


def test_plant_the_contribution_word_requirement_removed_flags_pension_eligibility(monkeypatch):
    monkeypatch.setattr(fidelity, "_D28_CONTRIB", re.compile(r"(?=)"))
    assert fidelity.nssf_contributions_tied_to_age_60(Q28, "Pensheni huendelea kulipwa hadi umri wa miaka 60 kwa wengine.")


def test_new_patterns_contain_no_control_characters():
    for r in (fidelity._D27_SDL, fidelity._D27_PREMISES, fidelity._D27_NEG, fidelity._D28_CONTRIB, fidelity._D28_AGE60_CLAIM, fidelity._D28_NEG):
        assert not any(ord(c) < 32 and c != "\n" for c in r.pattern)
