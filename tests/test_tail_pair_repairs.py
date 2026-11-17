# -*- coding: utf-8 -*-
"""R36 reach test for scripts/repair_tail_pairs_2026_11_17.py: the repairs must be in BOTH the authored sft_shaped_pairs and the exported sft/ files (a fix that reaches only the authored stage has not touched
the bytes that train), the quarantined pair must be in NEITHER, and the check is PLANTED so it cannot pass vacuously (R20/R26)."""
import glob
import hashlib
import io
import json
import os

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAGES = {"authored": "datasets/tier1a/sft_shaped_pairs/*.jsonl", "export": "datasets/tier1a/sft/*.jsonl"}
RESULT = os.path.join(REPO, "eval", "results", "tail_pair_repairs_2026_11_17.json")
QUAR = os.path.join(REPO, "datasets", "tier1a", "rejected", "gn605a_mining_765900_pair_quarantine_2026_11_17.jsonl")


def _answers(pattern):
    out = []
    for p in sorted(glob.glob(os.path.join(REPO, pattern))):
        for l in io.open(p, encoding="utf-8"):
            if l.strip():
                try:
                    r = json.loads(l)
                except ValueError:
                    continue
                out.append((r.get("instruction") or "", r.get("output") or r.get("answer_sw") or ""))
    return out


def _sha(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()[:16]


def reach(stage_answers, repaired_shas, quarantined_questions):
    """-> (repairs missing from the stage, quarantined questions still present)"""
    have = {_sha(a) for _, a in stage_answers}
    questions = {q for q, _ in stage_answers}
    return [s for s in repaired_shas if s not in have], sorted({q for q in quarantined_questions if q in questions})


def _record():
    return json.load(io.open(RESULT, encoding="utf-8"))


def _final_shas(stage_filter=None):
    """the sha256 of each repaired answer AS IT STANDS NOW: a later approved batch (apply_proposed_repairs_2026_11_17) edits some of these same answers again, so each repair is followed along its chain"""
    later = {}
    later_path = os.path.join(REPO, "eval", "results", "applied_proposed_repairs_2026_11_17.json")
    if os.path.exists(later_path):
        for e in json.load(io.open(later_path, encoding="utf-8"))["edited"]:
            later[e["old_sha256"]] = e["new_sha256"]
    out = set()
    for e in _record()["edited"]:
        h = e["new_sha256"]
        while h in later:
            h = later[h]
        out.add(h)
    return sorted(out)


def _quarantined_questions():
    return [json.loads(l)["row"]["instruction"] for l in io.open(QUAR, encoding="utf-8") if l.strip()]


@pytest.mark.parametrize("stage", sorted(STAGES))
def test_repairs_reach_every_stage_and_the_quarantined_pair_is_gone(stage):
    shas = _final_shas()
    assert len(shas) == 13, len(shas)
    missing, still = reach(_answers(STAGES[stage]), shas, _quarantined_questions())
    assert missing == [], f"{stage}: repaired answers not found: {missing}"
    assert still == [], f"{stage}: quarantined question still present: {still}"


def test_the_quarantine_record_holds_the_pair_from_both_stages():
    rows = [json.loads(l) for l in io.open(QUAR, encoding="utf-8") if l.strip()]
    assert len(rows) == 2 and {"sft_shaped_pairs" in r["source_file"] or "/sft/" in r["source_file"] for r in rows} == {True}
    assert all(r["defect"] and "695,000" in r["correct_value"] for r in rows)


def test_PLANTED_the_reach_check_blocks_a_stage_that_missed_the_edit():
    shas = _final_shas()
    qs = _quarantined_questions()
    # a stage holding the OLD answers and the quarantined question: both limbs must fire
    old = [(e["old"] and "q", e["old"]) for e in _record()["edited"]] + [(qs[0], "x")]
    missing, still = reach(old, shas, qs)
    assert len(missing) == 13 and still == sorted({qs[0]})


def test_repaired_texts_carry_no_firm_authority_no_605b_negative_and_no_sector_conflation():
    for e in _record()["edited"]:
        n = e["new"]
        assert "PKF" not in n and "VELMA" not in n and "MLYWF" not in n, n[-120:]
        assert "GN 605B haipo" not in n and "GN 605B haipatikani" not in n and "Agizo la Serikali" not in n, n[-120:]
        assert not ("765,900" in n and "madini ya kimataifa na nishati" in n), n[:120]
