"""2026-11-24: a context-free follow-up fragment ("Na dawa je?") is MERGED into the part before it and is never sent to the model alone. Probes both ways (R17), pattern hygiene (R39), an end-to-end orchestrator check with a PLANT that restores the live defect (R26),
and a pin on WHY only chike/decomposition.py changed (the live definition) and not the frozen v15 arm / kaggle/eval.py."""
import io
import json
import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
from chike import decomposition                                  # noqa: E402
from chike.orchestrator import Orchestrator                      # noqa: E402

_PROBES = os.path.join(_ROOT, "eval", "decomposition_gate", "fragment_merge_probes_2026_11_24.jsonl")


def _probes():
    with io.open(_PROBES, encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh if line.strip()]
    assert len(rows) == 15 and sum(1 for r in rows if r["parts"] == 1) >= 8 and sum(1 for r in rows if r["parts"] == 2) >= 5      # a loader returning nothing must fail (R20)
    return rows


@pytest.mark.parametrize("p", _probes(), ids=lambda p: p["id"])
def test_probe_decomposes_as_authored(p):
    assert len(decomposition.decompose_query(p["message"])) == p["parts"], p["guards_against"]


def test_new_patterns_contain_no_control_characters():
    """R39: a non-raw \\b is a backspace and matches nothing, invisibly. THREE patterns written for this change had exactly that, through a patch script."""
    for name in ("_FOLLOWUP_TAIL", "_FOLLOWUP_LEAD", "_OWN_ASK"):
        pat = getattr(decomposition, name).pattern
        assert not any(ord(c) < 32 for c in pat), (name, repr(pat))


def test_a_merged_message_is_returned_whole_and_unmodified():
    m = "Huduma za afya zinatozwa VAT? Na dawa je?"
    assert decomposition.decompose_query(m) == [m]


def test_a_fragment_is_never_the_first_part():
    assert decomposition._merge_dependent_fragments(["Na dawa je?", "VAT ni asilimia ngapi?"]) == ["Na dawa je?", "VAT ni asilimia ngapi?"]


class _Echo:
    seen = []

    def generate(self, prompt, params=None):
        _Echo.seen.append(prompt)
        return "JIBU."


def _sub_questions(question):
    _Echo.seen = []
    o = Orchestrator(_Echo(), retriever=lambda q: ["Ukweli."], ooc_phrases=[], in_scope_phrases=[])
    o.answer(question)
    return _Echo.seen


_FRAG_Q = "Msingi wa kukokotoa SDL ni nini \u2014 posho zinaingia? Na mgahawa je?"


def test_the_live_specimen_never_reaches_the_model_as_a_bare_fragment():
    """2026-11-25: the ORIGINAL live specimen ("Huduma za afya zinatozwa VAT? Na dawa je?") is now owned by the model-free vat_health_and_medicines route, so it never reaches the model at all (the stronger fix: tests/test_three_routes_2026_11_25.py).
    The merge is a general property of the decomposer, so it is exercised on the SAME SHAPE with a first part a statement route owns (the SDL base) and a context-free 'Na X je?' second part: with the merge the fragment is never a model prompt on its own."""
    from chike import routing
    assert routing.fixed_statement_topic("Huduma za afya zinatozwa VAT? Na dawa je?") == "vat_health_and_medicines"
    prompts = _sub_questions(_FRAG_Q)
    assert not any("Na mgahawa je?" in pr and "Msingi wa kukokotoa SDL" not in pr for pr in prompts), "a prompt carries the fragment WITHOUT its topic"


def test_plant_without_the_merge_the_fragment_reaches_the_model_alone(monkeypatch):
    """POSITIVE CONTROL: remove the merge and the bare fragment is a model prompt again, the live defect."""
    monkeypatch.setattr(decomposition, "_merge_dependent_fragments", lambda parts: parts)
    prompts = _sub_questions(_FRAG_Q)
    assert any("Na mgahawa je?" in pr and "Msingi wa kukokotoa SDL" not in pr for pr in prompts), prompts


def test_only_the_live_decomposer_changed_and_the_frozen_v15_arm_was_left_alone():
    """The repo's own header (chike/decomposition.py) states there is NO dual-file sync for changes here: production runs this module through chike.orchestrator, modal_app.py carries no decompose copy, and kaggle/eval.py loads the
    FROZEN chike/decomposition_v15.py, which must not gain v16 capabilities. This pins that fact so a later session does not 'port' the merge into the frozen arm (tests/test_pipeline_v15.py enumerates its intended divergences)."""
    v15 = open(os.path.join(_ROOT, "chike", "decomposition_v15.py"), encoding="utf-8").read()
    ev = open(os.path.join(_ROOT, "kaggle", "eval.py"), encoding="utf-8").read()
    modal = open(os.path.join(_ROOT, "chike-inference", "modal_app.py"), encoding="utf-8").read()
    assert "_merge_dependent_fragments" not in v15 and "_FOLLOWUP_TAIL" not in v15
    assert "_fetch_chike_module('decomposition_v15')" in ev and "def decompose_query" not in ev
    assert "def decompose_query" not in modal and "from chike.orchestrator import Orchestrator" in modal
    orch = open(os.path.join(_ROOT, "chike", "orchestrator.py"), encoding="utf-8").read()
    assert "decomposition.decompose_query(question)" in orch
