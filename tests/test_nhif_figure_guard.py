"""2026-11-22 D-FIDELITY-26: a figure attached to NHIF is removed (no NHIF rate is held). Founding specimen = the live mixed NSSF/NHIF reply. R17 probes both ways (seven of twelve are CLEAN or keep-the-other-levy, the arm that does the work), the
REAL orchestrator path with the specimen as the model's output, idempotence, and PLANTS (R26)."""
import io
import json
import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
from chike import fidelity                      # noqa: E402
from chike.orchestrator import Orchestrator    # noqa: E402

_PROBES = os.path.join(_ROOT, "eval", "fidelity", "nhif_figure_probes_2026_11_22.jsonl")
SPECIMEN_Q = "NSSF na NHIF — ni mifumo tofauti au moja?"


def _probes():
    with io.open(_PROBES, encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh if line.strip()]
    assert len(rows) == 13, len(rows)                         # a loader returning nothing must fail, not pass vacuously (R20)
    assert sum(1 for r in rows if r["removed"]) >= 5 and sum(1 for r in rows if not r["removed"]) >= 5
    return rows


@pytest.mark.parametrize("p", _probes(), ids=lambda p: p["id"])
def test_probe(p):
    out, removed = fidelity.repair_nhif_figures(p["body"])
    assert len(removed) == p["removed"], p["why"]
    for k in p["keep"]:
        assert k in out, (k, out)
    for g in p["gone"]:
        assert g not in out, (g, out)
    if p["removed"]:
        assert fidelity.NHIF_NOT_COVERED_NOTE in out
    else:
        assert out == p["body"]                                # a clean body is returned byte-identical


def test_the_repair_is_idempotent():
    for p in _probes():
        once, _ = fidelity.repair_nhif_figures(p["body"])
        twice, removed = fidelity.repair_nhif_figures(once)
        assert twice == once and removed == [], p["id"]


class _Backend:
    def __init__(self, reply):
        self.reply = reply

    def generate(self, prompt, params=None):
        return self.reply


def test_the_real_orchestrator_path_removes_the_figure_and_keeps_the_nssf_part():
    body = _probes()[0]["body"]
    o = Orchestrator(_Backend(body), retriever=lambda q: ["NSSF: asilimia 10 mwajiri na asilimia 10 mfanyakazi."], ooc_phrases=[], in_scope_phrases=[])
    reply = o.answer(SPECIMEN_Q)
    assert "0.5" not in reply.text and "NHIF: hutoa" not in reply.text
    assert "NSSF: hutoa pensheni" in reply.text and fidelity.NHIF_NOT_COVERED_NOTE in reply.text


def test_a_reply_that_mentions_nhif_without_a_figure_reaches_the_user_unchanged():
    body = "NHIF ni bima ya afya, si pensheni. NSSF ni asilimia 10 kwa mwajiri."
    o = Orchestrator(_Backend(body), retriever=lambda q: ["NSSF: asilimia 10."], ooc_phrases=[], in_scope_phrases=[])
    assert o.answer(SPECIMEN_Q).text.strip().startswith("NHIF ni bima ya afya")


def test_plant_the_repair_unwired_lets_the_specimen_through(monkeypatch):
    monkeypatch.setattr(fidelity, "repair_nhif_figures", lambda body: (body, []))
    body = _probes()[0]["body"]
    o = Orchestrator(_Backend(body), retriever=lambda q: ["NSSF: asilimia 10."], ooc_phrases=[], in_scope_phrases=[])
    assert "asilimia 0.5" in o.answer(SPECIMEN_Q).text, "with the repair unwired the invented NHIF rate must reach the user; if not, the real-path test above proves nothing"


def test_plant_the_connector_split_removed_deletes_the_other_levys_figure(monkeypatch):
    monkeypatch.setattr(fidelity, "_NHIF_CLAUSE", re.compile(r"((?<=[.!?])\s+|\n+)"))
    out, _ = fidelity.repair_nhif_figures("NSSF ni asilimia 10 na NHIF ni asilimia 3 ya mshahara.")
    assert "asilimia 10" not in out, "without the clause split the NSSF figure is lost with the NHIF clause; the split is load-bearing"


def test_new_patterns_contain_no_control_characters():
    for r in (fidelity._NHIF, fidelity._NHIF_OTHER, fidelity._NHIF_FIG, fidelity._NHIF_CLAUSE, fidelity._NHIF_BACK):
        assert not any(ord(c) < 32 and c != "\n" for c in r.pattern)
