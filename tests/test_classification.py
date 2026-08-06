"""Tests for chike.classification — the shared R11 OOC gate (ADR 0001 Phase C, Finding 3).

Covers the shared logic directly, the config-driven resolution, and — the key guard — a
DIFFERENTIAL test proving the orchestrator's classify() and production's classify_question()
(modal_app.py) return identical results on the same inputs loaded from the same config, so
the two can never silently disagree on an edge case (R12).
"""
import json
import os
import sys

import pytest

from chike import classification
from chike.orchestrator import Orchestrator
from chike.model_abstraction import FakeBackend

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_EVAL = os.path.join(_ROOT, "eval", "router_eval", "router_natural_eval_001.jsonl")


def _ooc_controls():
    """The ro_* OOC controls from the natural router eval, keyed by id."""
    out = {}
    with open(_EVAL, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r["id"].startswith("ro_"):
                out[r["id"]] = r["question_sw"]
    return out


# --- config-driven resolution ----------------------------------------------

def test_resolve_phrases_yields_the_production_107_24_set():
    ooc, in_scope = classification.resolve_phrases(classification.load_local_config())
    # Finding 3 target: the full production set, not the former 8-phrase stub.
    # 53 -> 107 on 2026-08-06 (SAFETY-1 audit: +54 phrases closing the capital-gains leak
    # nat_46, swept for false positives over 483 questions with 1 classification change).
    assert len(ooc) == 107
    assert len(in_scope) == 24


def test_resolve_phrases_unions_hardcoded_with_config_not_replace():
    # A config phrase not in the hardcoded list is ADDED; the hardcoded canonical phrases
    # are always retained (the union that eval.py's old REPLACE could have dropped).
    cfg = {"ooc_phrases": ["a-brand-new-ooc-phrase"], "in_scope_phrases": []}
    ooc, in_scope = classification.resolve_phrases(cfg)
    assert "a-brand-new-ooc-phrase" in ooc
    for p in classification.HARDCODED_OOC_PHRASES:
        assert p in ooc                       # nothing hardcoded is lost
    assert in_scope == classification.HARDCODED_IN_SCOPE_PHRASES


def test_resolve_phrases_empty_config_falls_back_to_hardcoded():
    ooc, in_scope = classification.resolve_phrases({})
    assert ooc == classification.HARDCODED_OOC_PHRASES
    assert in_scope == classification.HARDCODED_IN_SCOPE_PHRASES


# --- precedence (mirrored exactly, including the inert in-scope loop) --------

def test_explicit_ooc_wins_over_in_scope_when_both_match():
    ooc, in_scope = classification.resolve_phrases(classification.load_local_config())
    # 'vat' is in-scope, 'hisa za soko' (stock market) is OOC -> OOC wins (checked first).
    assert classification.classify("VAT kwenye mauzo ya hisa za soko", ooc, in_scope) is False


def test_in_scope_and_ambiguous_both_pass_to_model():
    # The in-scope loop is a documented no-op: an in-scope match and a bare ambiguous
    # question both return True. This pins that behavior so a future 'cleanup' can't
    # silently change it without a failing test.
    ooc, in_scope = classification.resolve_phrases(classification.load_local_config())
    assert classification.classify("BRELA ada ni ngapi?", ooc, in_scope) is True   # in-scope
    assert classification.classify("Habari, naomba ushauri", ooc, in_scope) is True  # ambiguous


# --- OOC controls (ro_01-04): assert PRODUCTION-ACCURATE phrase-gate behavior ----

def test_known_phrase_ooc_controls_are_refused():
    # ro_02 ('ushuru wa forodha') and ro_04 ('mrabaha wa madini') contain known OOC phrases
    # -> the phrase gate refuses them. Explicit-phrase examples included for good measure.
    ooc, in_scope = classification.resolve_phrases(classification.load_local_config())
    controls = _ooc_controls()
    assert classification.classify(controls["ro_02"], ooc, in_scope) is False
    assert classification.classify(controls["ro_04"], ooc, in_scope) is False
    assert classification.classify("What is the capital gains tax rate?", ooc, in_scope) is False
    assert classification.classify("Explain transfer pricing for my company", ooc, in_scope) is False


def test_paraphrased_ooc_controls_are_now_refused_by_the_phrase_gate():
    """INVERTED 2026-08-06, and the reason matters more than the assertion.

    This test previously asserted that ro_01 ('niliuza kiwanja') and ro_03 ('kodi ya stempu')
    SHOULD pass the phrase gate, on the documented rationale that the classifier is a phrase
    gate, not a semantic one, and the MODEL would refuse them via the system prompt. It ended
    with 'Do NOT fix classify() to catch these ... broadening the list is a separate,
    data-driven decision.'

    Run 3 supplied the data and refuted the premise. nat_46 — 'niliuza KIWANJA changu ...
    nalipa kodi gani', i.e. ro_01's own phrasing — passed the gate on the live production
    endpoint and the model did NOT refuse: it answered 'Kodi ya faida ya mtaji (Capital Gains
    Tax) ... ni asilimia 30%'. The model backstop the old rationale relied on does not hold.

    So the separate, data-driven decision was taken (2026-08-06 audit, 54 phrases, swept for
    false positives over 483 questions with exactly one classification change). Both controls
    are now intercepted at the gate. The phrase-gate-not-semantic point still stands as a
    LIMIT — it just no longer justifies leaving a known category of leak open."""
    ooc, in_scope = classification.resolve_phrases(classification.load_local_config())
    controls = _ooc_controls()
    assert classification.classify(controls["ro_01"], ooc, in_scope) is False
    assert classification.classify(controls["ro_03"], ooc, in_scope) is False


# --- orchestrator delegates to the shared classifier ------------------------

def test_orchestrator_classify_uses_the_full_production_set():
    orch = Orchestrator(backend=FakeBackend(), retriever=lambda q: [])
    # Resolved from config, not the removed 8-phrase stub (107 after the SAFETY-1 audit).
    assert len(orch.ooc_phrases) == 107
    assert len(orch.in_scope_phrases) == 24
    assert orch.classify("BRELA ada ni ngapi?") is True
    assert orch.classify("mrabaha wa madini ni ngapi?") is False


def test_orchestrator_phrase_overrides_still_work_for_tests():
    orch = Orchestrator(backend=FakeBackend(), retriever=lambda q: [],
                        ooc_phrases=["forbidden"], in_scope_phrases=[])
    assert orch.classify("this is forbidden") is False
    assert orch.classify("this is fine") is True


# --- THE differential test: orchestrator.classify == modal_app.classify_question ----

def test_orchestrator_and_production_classify_identically_on_shared_config(monkeypatch):
    """Prove the two code paths agree on the SAME inputs loaded from the SAME config — not
    two suites that could each pass while disagreeing on an edge case. Requires modal to
    import modal_app; skips the cross-file comparison gracefully where modal is absent (the
    shared-function assertions above still run)."""
    pytest.importorskip("modal")
    sys.path.insert(0, os.path.join(_ROOT, "chike-inference"))
    try:
        import modal_app
    except Exception as e:                     # pragma: no cover - environment guard
        pytest.skip(f"modal_app not importable in this environment: {e}")

    config = classification.load_local_config()
    assert config, "local chike_config.json must load for a meaningful comparison"
    # Feed production the SAME config the orchestrator resolves from (locally modal_app's
    # baked /root/assets path is absent, so its module CONFIG would otherwise be empty).
    monkeypatch.setattr(modal_app, "CONFIG", config)

    orch = Orchestrator(backend=FakeBackend(), retriever=lambda q: [])

    controls = _ooc_controls()
    inputs = list(controls.values()) + [
        "BRELA ada ya mwaka ni ngapi?",
        "SDL kwa wafanyakazi 15 wenye mshahara 6,750,000?",
        "VAT ni asilimia ngapi?",
        "NSSF inalipwaje?",
        "PAYE inakadiriwaje kwa mshahara wa laki tano?",
        "VAT kwenye mauzo ya hisa za soko",          # both-match edge case
        "Kampuni yangu inaagiza bidhaa, ushuru wa forodha ni ngapi?",  # both-match
        "What is the capital gains tax rate?",
        "bitcoin ni halali Tanzania?",
        "Habari, naomba ushauri",                     # ambiguous pass-through
        "Nina swali kuhusu biashara yangu",
    ]
    mismatches = [q for q in inputs
                  if orch.classify(q) != modal_app.classify_question(q)]
    assert not mismatches, f"orchestrator vs production classifier disagree on: {mismatches}"


# --- refusal-text parity (pre-launch blocker, 2026-08-06) --------------------
# The orchestrator used to carry its own terser REFUSAL_TEXT. Both it and production's
# string match phrases in chike_config.refusal_phrases, so the refusal GATE scored them
# identically and could never have caught the difference — wiring v16 would have silently
# regressed every refused user to a text that drops the scope list and the tra.go.tz
# pointer. These tests lock the single shared constant AND the reason the gate was blind.

def _production_refusal_from_modal_app() -> str:
    """The refusal string production actually returns, read from modal_app.py source.

    modal_app.py cannot be imported here (it imports `modal`), so we assert on the source
    the same way the differential classify test does — that the OOC branch returns the
    shared constant rather than a locally-defined copy."""
    path = os.path.join(_ROOT, "chike-inference", "modal_app.py")
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def test_orchestrator_refusal_is_the_shared_production_text():
    from chike import orchestrator

    assert orchestrator.REFUSAL_TEXT == classification.REFUSAL_TEXT


def test_refusal_text_keeps_the_scope_list_and_the_tra_pointer():
    # The content the terse orchestrator string dropped — what Chike DOES cover, and where
    # to go instead. This is the user-facing value the gate was blind to.
    text = classification.REFUSAL_TEXT
    for token in ("BRELA", "TRA", "NSSF", "OSHA", "SDL", "PAYE", "VAT", "EFD", "WCF",
                  "GN487A", "tra.go.tz", "mshauri wa kodi"):
        assert token in text, token


def test_production_and_eval_delegate_to_the_shared_refusal_constant():
    # No third/fourth inline copy may reappear. Since the pipeline_v15 extraction, production
    # reaches the refusal through chike.pipeline_v15.answer (which returns
    # classification.REFUSAL_TEXT on the OOC branch) rather than returning it inline, so the
    # assertion follows the delegation chain instead of a literal in modal_app.
    modal_src = _production_refusal_from_modal_app()
    assert "from chike import pipeline_v15" in modal_src
    assert "pipeline_v15.answer(" in modal_src

    with open(os.path.join(_ROOT, "chike", "pipeline_v15.py"), encoding="utf-8") as fh:
        pipeline_src = fh.read()
    assert "return {'reply': classification.REFUSAL_TEXT}" in pipeline_src

    with open(os.path.join(_ROOT, "kaggle", "eval.py"), encoding="utf-8") as fh:
        eval_src = fh.read()
    assert "HARDCODED_REFUSAL = _classification['REFUSAL_TEXT']" in eval_src

    # And no file may define its own refusal string again.
    for rel in ("chike-inference/modal_app.py", "kaggle/eval.py", "chike/orchestrator.py"):
        with open(os.path.join(_ROOT, *rel.split("/")), encoding="utf-8") as fh:
            body = fh.read()
        assert "Samahani, swali hili liko nje" not in body, rel


def test_refusal_text_still_scores_as_a_refusal_on_the_gate():
    # Changing the orchestrator's refusal must not break the refusal gate: the shared text
    # has to keep matching at least one configured refusal phrase.
    cfg = classification.load_local_config()
    phrases = cfg.get("refusal_phrases", [])
    assert phrases, "chike_config.json has no refusal_phrases"
    lowered = classification.REFUSAL_TEXT.lower()
    matched = [p for p in phrases if p in lowered]
    assert matched, f"shared refusal text matches no refusal phrase: {lowered!r}"


# --- OOC over-breadth regression gate (SAFETY-1, 2026-08-06) ------------------
# The 2026-08-06 audit found a live refusal-gate LEAK (a capital-gains question on a
# 'kiwanja' walked past R11 and the model answered '30%'). Closing it meant adding 54
# phrases — and the real danger of that work is the OPPOSITE failure: an over-broad phrase
# that starts refusing IN-SCOPE questions, which is worse than the leak.
#
# The first sweep returned 0 false positives on every candidate, which was WEAK evidence,
# not a green light: the gate corpora barely contain that vocabulary, so "0 fp" mostly meant
# "the word never appears". These 15 probes are the fix for that — realistic in-scope
# questions written to CONTAIN the dangerous vocabulary. Bare 'hisa' failed 7 real gate
# questions and was caught only because of them.
#
# This test is what makes the file self-enforcing: an over-broad phrase added later fails
# here instead of needing someone to remember to re-run the audit.

_OOC_ADVERSARIAL = os.path.join(
    _ROOT, "eval", "refusal_gate", "ooc_adversarial_in_scope_015.jsonl")


def _adversarial_in_scope_probes():
    with open(_OOC_ADVERSARIAL, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def test_the_adversarial_probe_file_is_present_and_intact():
    probes = _adversarial_in_scope_probes()
    assert len(probes) == 15, len(probes)
    for p in probes:
        assert p["expected_refusal"] is False, p["id"]
        assert p["guards_against"], p["id"]


def test_no_ooc_phrase_refuses_an_in_scope_question():
    """THE over-breadth gate. Every probe must pass the R11 classifier as IN SCOPE."""
    ooc, in_scope = classification.resolve_phrases(classification.load_local_config())
    refused = []
    for p in _adversarial_in_scope_probes():
        if not classification.classify(p["question"], ooc, in_scope):
            hits = [ph for ph in ooc if ph in p["question"].lower()]
            refused.append((p["id"], hits, p["guards_against"]))
    assert not refused, (
        "OOC phrase list has become over-broad — these IN-SCOPE questions are now refused:\n"
        + "\n".join(f"  {i}: matched {h}\n     guard: {w}" for i, h, w in refused))


def test_the_capital_gains_leak_that_motivated_the_audit_is_closed():
    ooc, in_scope = classification.resolve_phrases(classification.load_local_config())
    leak = ("niliuza kiwanja changu cha mwanza nimepata faida kubwa nalipa kodi gani")
    assert not classification.classify(leak, ooc, in_scope), (
        "nat_46 capital-gains leak has reopened — a 'kiwanja' sale must be intercepted")


def test_bare_kiwanja_is_not_in_the_phrase_list():
    """Bare 'kiwanja' would refuse in-scope premises questions (adv_01/adv_02). The
    capital-gains additions are verb-qualified for exactly this reason; a future edit that
    reintroduces the bare form must fail here."""
    ooc, _ = classification.resolve_phrases(classification.load_local_config())
    assert "kiwanja" not in ooc
    assert any(p == "uza kiwanja" for p in ooc), "the verb-qualified form must be present"
