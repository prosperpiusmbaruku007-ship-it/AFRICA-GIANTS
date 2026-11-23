"""2026-11-24: the SDL-base statement, the two THREE-LEVY statements (rate, deadline), the GN 487A premise opener ("Hapana"), the SDL-base locked fact + the sdl_rate wording correction, and the widened D-FIDELITY-29
("PAYE na michango ya NSSF" list shapes, sentences run together with no space). Probes both ways (R17), zero model calls, content pinned to the Act text read, PLANTS with positive controls (R26)."""
import io
import json
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
from chike import answer_trace, fidelity, routing   # noqa: E402
from chike.orchestrator import Orchestrator         # noqa: E402
from chike.rules_engine import fixed_statements as fs   # noqa: E402

NEW = ("sdl_base", "levy_rates_three", "levy_deadlines_three")
_PROBES = os.path.join(_ROOT, "eval", "refusal_gate", "three_more_statements_probes_2026_11_24.jsonl")


def _probes():
    with io.open(_PROBES, encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh if line.strip()]
    assert len(rows) == 31, len(rows)                         # a loader returning nothing must fail, not pass vacuously (R20)
    assert sum(1 for r in rows if r["expect"] in NEW) >= 14
    return rows


@pytest.mark.parametrize("p", _probes(), ids=lambda p: p["id"])
def test_probe_routes_as_authored(p):
    assert routing.fixed_statement_topic(p["question"]) == (None if p["expect"] == "none" else p["expect"]), p["guards_against"]


def test_new_patterns_contain_no_control_characters():
    for name in NEW:
        entry = [e for e in routing._FS_TOPICS if e[0] == name]
        assert len(entry) == 1 and name in fs.TOPICS and name in fs.TOPICS_NO_CONCISE_ROW
        for p in list(entry[0][1:]) + [routing._FS_TOPIC_ASK[name]]:
            if p is not None:
                assert not any(ord(c) < 32 for c in p.pattern), (name, p.pattern[:80])


class _B:
    calls = 0

    def generate(self, prompt, params=None):
        _B.calls += 1
        return "JIBU."


@pytest.mark.parametrize("p", [r for r in _probes() if r["expect"] in NEW], ids=lambda p: p["id"])
def test_positive_probe_is_answered_by_the_whole_statement_with_zero_model_calls(p):
    _B.calls = 0
    o = Orchestrator(_B(), retriever=lambda q: ["Ukweli."], ooc_phrases=[], in_scope_phrases=[])
    reply = o.answer(p["question"])
    t = answer_trace.trace(reply)
    assert t["path"] == "engine:fixed_statement" and t["model_calls"] == 0 and _B.calls == 0, t
    assert fs.fixed_statement(p["expect"]).working in reply.text


def _w(t):
    return fs.fixed_statement(t).working


def test_sdl_base_statement_follows_s14_3_and_asserts_nothing_about_benefits_in_kind():
    w = _w("sdl_base")
    for needle in ("JUMLA YA MISHAHARA GHAFI YA MWEZI", "POSHO ZOTE", "ZIMO kwenye msingi", "HAIJATHIBITISHWA", "asilimia 3.5", "kiinua mgongo"):
        assert needle in w, needle
    assert "cash" not in w.lower() and "taslimu" not in w.lower()
    for forbidden in ("faida zisizo za fedha zinahesabiwa", "faida zisizo za fedha hazihesabiwi", "makazi yanahesabiwa", "gari linahesabiwa"):
        assert forbidden not in w                            # benefits in kind: asserted NEITHER way (founder's instruction)


def test_three_levy_rate_statement_has_no_summed_employer_rate_and_says_paye_has_no_single_rate():
    w = _w("levy_rates_three")
    for needle in ("asilimia 3.5", "asilimia 20", "HAINA kiwango kimoja", "kiwango cha 1", "kiwango cha 5"):
        assert needle in w, needle
    assert "14%" not in w and "asilimia 14" not in w and "0.5%" not in w         # the live reply's invented sum "NSSF 10% + SDL 3.5% + PAYE 0.5%"


def test_three_levy_deadline_statement_gives_nssf_one_month_and_passes_its_own_guard():
    w = _w("levy_deadlines_three")
    for needle in ("tarehe 7", "TOFAUTI", "mwezi mmoja", "si tarehe 7", "asilimia 5"):
        assert needle in w, needle
    assert fidelity.nssf_deadline_misstated("q", w) == []


# ── locked facts ────────────────────────────────────────────────────────────────────────────────
def _facts():
    with io.open(os.path.join(_ROOT, "scripts", "locked_facts.json"), encoding="utf-8") as fh:
        return json.load(fh)


def test_sdl_rate_no_longer_says_cash_and_the_base_fact_quotes_the_act():
    f = _facts()
    assert "cash" not in f["sdl_rate"]["fact"].lower() and "total gross monthly emoluments" in f["sdl_rate"]["fact"] and "correction_note" in f["sdl_rate"]
    assert "wrong_patterns" in f["sdl_rate"] and len(f["sdl_rate"]["wrong_patterns"]) >= 10         # R27: the fields the correction did not touch survive
    assert "cash" not in f["SDL_source_law"]["fact"].lower()
    b = f["sdl_base_includes_allowances"]
    for needle in ("subsistence, travelling, entertainment or other allowance", "gratuity", "includes", "NOT settled", "s.14(3)"):
        assert needle in b["fact"], needle
    assert b["status"] == "CONFIRMED" and b["verified_date"] == "2026-11-24" and "R.E.2023" in b["primary_source"]


def test_base_fact_wrong_patterns_catch_the_live_error_and_spare_the_statement():
    import re
    pats = [re.compile(p, re.IGNORECASE) for p in _facts()["sdl_base_includes_allowances"]["wrong_patterns"]]
    live = "Msingi wa SDL ni gross payroll (cash basis), si pamoja na posho za fedha."   # the patterns now require SDL in the sentence (a PAYE row about allowances is not this error)
    assert any(p.search(live) for p in pats)
    assert not any(p.search(_w("sdl_base")) for p in pats), "the correct statement must not trip its own wrong_patterns (a mention is not an assertion)"


# ── GN 487A premise opener ──────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("q", [
    "Adhabu ya raia wa Tanzania anayemsaidia mgeni chini ya GN 487A ni TZS 10,000,000, sivyo?",
    "The penalty for a Tanzanian who assists a foreigner under GN 487A is TZS 10,000,000, right?",
    "Faini ya chini kabisa anayotozwa asiye raia kwa kukiuka GN 487A ni TZS milioni 8, sivyo?",
    "Msaidizi wa GN 487A anaweza kupata faini ya TZS milioni 10 kama mgeni?"])
def test_a_contradicted_figure_opens_with_an_explicit_hapana(q):
    o = Orchestrator(_B(), retriever=lambda x: ["Ukweli."], ooc_phrases=[], in_scope_phrases=[])
    assert routing.fixed_statement_topic(q) == "gn487a_penalties", q
    t = o.answer(q).text
    assert t.startswith("Hapana") and "5,000,000" in t and "10,000,000" in t, t


@pytest.mark.parametrize("q", [
    "Adhabu ya GN 487A kwa raia wa Tanzania anayemsaidia mgeni ni TZS 5,000,000, sivyo?",
    "Adhabu ya mgeni chini ya GN 487A ni faini ya TZS 10,000,000, sivyo?",
    "What is the penalty under GN 487A for a non-citizen?",
    "Adhabu ya raia wa Tanzania anayemsaidia mgeni chini ya GN 487A ni miezi 3?"])
def test_a_correct_or_absent_figure_gets_the_bare_statement(q):
    assert fs.gn487a_premise_opening(q) == ""
    o = Orchestrator(_B(), retriever=lambda x: ["Ukweli."], ooc_phrases=[], in_scope_phrases=[])
    assert not o.answer(q).text.startswith("Hapana")


def test_the_opener_is_for_this_statement_only():
    assert fs.fixed_statement("sdl_payer", "Mshahara wa TZS 8 milioni, hii ni sahihi?").working == fs.fixed_statement("sdl_payer").working


def test_plant_the_opener_disabled_loses_the_hapana(monkeypatch):
    q = "Adhabu ya raia wa Tanzania anayemsaidia mgeni chini ya GN 487A ni TZS 10,000,000, sivyo?"
    monkeypatch.setattr(fs, "gn487a_premise_opening", lambda question: "")
    o = Orchestrator(_B(), retriever=lambda x: ["Ukweli."], ooc_phrases=[], in_scope_phrases=[])
    assert not o.answer(q).text.startswith("Hapana"), "positive control: without the opener the premise is answered without a no"


# ── D-FIDELITY-29 widened ───────────────────────────────────────────────────────────────────────
LIVE_DEADLINE = ("SDL inalipwa ifikapo siku ya 7 ya mwezi unaofuata. Thibitisha na TRA (tra.go.tz).NSSF inalipwa ndani ya mwezi mmoja baada ya mwisho wa mwezi wa mishahara — thibitisha na NSSF (nssf.go.tz)."
                 "PAYE inalipwa pamoja na PAYE, ikijumuisha malipo ya PAYE na michango ya NSSF, ifikapo tarehe 7 ya mwezi unaofuata. Thibitisha na TRA (tra.go.tz).")


def test_d29_flags_the_live_three_levy_reply_with_run_together_sentences_and_a_noun_phrase_in_the_list():
    got = fidelity.nssf_deadline_misstated("q", LIVE_DEADLINE)
    assert got and "michango ya NSSF" in got[0] and "mwezi mmoja" not in got[0], got


def test_d29_widening_leaves_the_correct_run_together_form_alone():
    ok = "NSSF inalipwa ndani ya mwezi mmoja baada ya mwisho wa mwezi (nssf.go.tz).PAYE inalipwa ifikapo tarehe 7."
    assert fidelity.nssf_deadline_misstated("q", ok) == []
    assert fidelity.nssf_deadline_misstated("q", _w("levy_deadlines_three")) == []


def test_d29_widening_plant_old_splitter_misses_the_live_reply(monkeypatch):
    import re
    monkeypatch.setattr(fidelity, "_D29_SENT", fidelity._SENTENCE_SPLIT)
    assert fidelity.nssf_deadline_misstated("q", LIVE_DEADLINE) == [], "positive control: with the old splitter the live reply escapes (the month guard excused it)"
