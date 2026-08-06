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

def test_resolve_phrases_yields_the_production_53_24_set():
    ooc, in_scope = classification.resolve_phrases(classification.load_local_config())
    # Finding 3 target: the full production set, not the former 8-phrase stub.
    assert len(ooc) == 53
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


def test_paraphrased_ooc_controls_pass_the_phrase_gate_to_the_model():
    # ro_01 ('niliuza kiwanja', not the listed 'niliuza ardhi/nyumba') and ro_03 ('kodi ya
    # stempu', not the listed 'ushuru wa stempu') are OOC in MEANING but use paraphrases the
    # substring gate does not carry, so classify() passes them to the model (which refuses via
    # the system prompt). This is production-accurate: the classifier is a phrase gate, not a
    # semantic one. Do NOT 'fix' classify() to catch these — the phrase-gate + model-backstop
    # split is deliberate; broadening the list is a separate, data-driven decision.
    ooc, in_scope = classification.resolve_phrases(classification.load_local_config())
    controls = _ooc_controls()
    assert classification.classify(controls["ro_01"], ooc, in_scope) is True
    assert classification.classify(controls["ro_03"], ooc, in_scope) is True


# --- orchestrator delegates to the shared classifier ------------------------

def test_orchestrator_classify_uses_the_full_production_set():
    orch = Orchestrator(backend=FakeBackend(), retriever=lambda q: [])
    # Resolved from config, not the removed 8-phrase stub.
    assert len(orch.ooc_phrases) == 53
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
