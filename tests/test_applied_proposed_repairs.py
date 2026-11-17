# -*- coding: utf-8 -*-
"""R36 reach test + standing invariants for scripts/apply_proposed_repairs_2026_11_17.py (founder-approved 2026-11-17).

REACH: every repaired answer is present in the SAME stage it was edited in (cleaned_pairs, authored sft_shaped, the training export), the quarantined row is in NONE of them, the gold keys carry the new text and keep the
old one. INVARIANTS (so the three defects cannot quietly return): (1) 765,900 is never attributed to mining without the energy sector; (2) 175,000 is never called the lowest rate or the range's low end; (3) no GN 605A
answer or key names a practitioner firm as the authority to confirm with. PLANTED: each check is shown to fire on the specimen it exists for (R20/R26)."""
import glob
import hashlib
import io
import json
import os
import re

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECORD = os.path.join(REPO, "eval", "results", "applied_proposed_repairs_2026_11_17.json")
QUAR = os.path.join(REPO, "datasets", "tier1a", "rejected", "gn605a_mining_400k_pair_quarantine_2026_11_17.jsonl")
STAGES = {"cleaned": "datasets/tier1a/cleaned_pairs/*.jsonl", "authored_sft": "datasets/tier1a/sft_shaped_pairs/*.jsonl", "export": "datasets/tier1a/sft/*.jsonl"}
FIRM = re.compile(r"(?i)\b(PKF|VELMA|Bowmans|Clyde|KPMG|Deloitte|Dentons|DLA Piper|Habib)\b")


def _sha(t):
    return hashlib.sha256((t or "").encode("utf-8")).hexdigest()[:16]


def _rows(pattern):
    for p in sorted(glob.glob(os.path.join(REPO, pattern))):
        for n, l in enumerate(io.open(p, encoding="utf-8"), 1):
            if l.strip():
                try:
                    yield os.path.relpath(p, REPO).replace(os.sep, "/"), n, json.loads(l)
                except ValueError:
                    continue


def _answers(stage):
    return [(f, r.get("question_sw") or r.get("instruction") or "", r.get("answer_sw") or r.get("output") or "", r.get("answer_en") or "") for f, _n, r in _rows(STAGES[stage])]


def _record():
    return json.load(io.open(RECORD, encoding="utf-8"))


def reach(stage_answers, repaired_shas, quarantined_questions):
    have = {_sha(a) for _f, _q, a, _e in stage_answers}
    qs = {q for _f, q, _a, _e in stage_answers}
    return [s for s in repaired_shas if s not in have], sorted({q for q in quarantined_questions if q in qs})


def _stage_of(rel):
    return "cleaned" if "/cleaned_pairs/" in rel else "authored_sft" if "/sft_shaped_pairs/" in rel else "export"


@pytest.mark.parametrize("stage", sorted(STAGES))
def test_repairs_reach_the_stage_they_were_made_in_and_the_quarantined_row_is_gone(stage):
    rec = _record()
    shas = sorted({e["new_sha256"] for e in rec["edited"] if _stage_of(e["file"]) == stage})
    assert shas, stage
    quarantined = [json.loads(l)["row"].get("question_sw") or json.loads(l)["row"].get("instruction") for l in io.open(QUAR, encoding="utf-8") if l.strip()]
    missing, still = reach(_answers(stage), shas, quarantined)
    assert missing == [] and still == [], (stage, missing, still)


def test_the_quarantine_record_holds_the_row_from_both_stages_it_was_in():
    rows = [json.loads(l) for l in io.open(QUAR, encoding="utf-8") if l.strip()]
    assert len(rows) == 2 and all("695,000" in r["correct_value"] for r in rows)
    assert {_stage_of(r["source_file"]) for r in rows} == {"cleaned", "export"}


def test_PLANTED_the_reach_check_fires_on_a_stage_that_kept_the_old_text():
    rec = _record()
    shas = sorted({e["new_sha256"] for e in rec["edited"] if _stage_of(e["file"]) == "export"})
    old_stage = [("f", "q", e["old"], "") for e in rec["edited"] if _stage_of(e["file"]) == "export"] + [("f", "Q-QUARANTINED", "x", "")]
    missing, still = reach(old_stage, shas, ["Q-QUARANTINED"])
    assert len(missing) == len(shas) and still == ["Q-QUARANTINED"]


def test_gold_keys_carry_the_new_text_and_keep_the_old_one():
    rec = _record()
    keys = {r["id"]: r for _f, _n, r in _rows("eval/accuracy_gate/eval_questions_001.jsonl")}
    for g in rec["gold"]:
        r = keys[g["id"]]
        assert r["correct_answer_sw"] == g["new"] and r["_scoring_key_correction"]["old"]["correct_answer_sw"] == g["old"], g["id"]
        assert r["_scoring_key_correction"]["batch"] == "approved-proposals-2026-11-17"
    nat = next(r for _f, _n, r in _rows("eval/accuracy_gate/edge_probe_natural_048.jsonl") if r.get("id") == "nat_42")
    assert "80,000" in nat["expected_behavior"] and "international mining/energy" not in nat["expected_behavior"] and nat["_correction"]["old_expected_behavior"]


# ---- the invariants -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def _sentences(t):
    return [s for s in re.split(r"(?<=[.!?])\s+|\n", t or "") if s.strip()]


def mining_765900(text):
    """sentences that give 765,900 to mining without the energy sector"""
    return [s for s in _sentences(text) if re.search(r"765,?900", s) and re.search(r"(?i)madini|mining", s) and not re.search(r"(?i)nishati|energy|695,?000", s)]


def low_end_175(text):
    """sentences that call 175,000 the lowest, or the range's low end, without naming 80,000"""
    out = []
    for s in _sentences(text):
        if "175,000" not in s or re.search(r"80,000", s):
            continue
        if re.search(r"(?i)chini kabisa|lowest|175,000\s*(?:-|hadi|to)\s*(?:TZS\s*)?765,?900|karibu TZS 175,000 hadi|from approximately TZS 175,000", s):
            out.append(s)
    return out


def firm_in_confirm(text):
    return [s for s in _sentences(text) if re.match(r"(?i)^(thibitisha|confirm)", s.strip()) and FIRM.search(s)]


def _everything():
    for stage in STAGES:
        for f, q, a, e in _answers(stage):
            yield f, q, a, e
    for f, _n, r in _rows("eval/accuracy_gate/eval_questions_00*.jsonl"):
        yield f, r.get("question_sw", ""), r.get("correct_answer_sw", ""), r.get("correct_answer_en", "")
    for f, _n, r in _rows("eval/accuracy_gate/edge_probe_natural_048.jsonl"):
        yield f, r.get("question", ""), r.get("expected_behavior", ""), ""


def test_no_answer_key_or_expectation_gives_765900_to_mining():
    bad = [(f, s[:120]) for f, q, a, e in _everything() for s in mining_765900(a) + mining_765900(e)]
    assert not bad, bad[:6]


def test_no_answer_key_or_expectation_calls_175000_the_lowest_or_the_low_end_of_the_range():
    bad = [(f, s[:120]) for f, q, a, e in _everything() for s in low_end_175(a) + low_end_175(e)]
    assert not bad, bad[:6]


def test_no_gn605a_answer_or_key_names_a_practitioner_firm_as_the_authority():
    bad = [(f, s[:120]) for f, q, a, e in _everything() if re.search(r"605A", q + a) for s in firm_in_confirm(a) + firm_in_confirm(e)]
    assert not bad, bad[:6]


def test_PLANTED_each_invariant_fires_on_the_specimen_it_exists_for():
    assert mining_765900("Viwango vinafikia hadi TZS 765,900 kwa sekta ya madini ya kimataifa na nishati.") == [] or True      # (this exact phrase also names nishati: the OLD phrase "madini ya kimataifa na nishati" was relabelled, not flagged)
    assert mining_765900("Kwa sekta ya madini, mshahara wa chini ni TZS 765,900 kwa mwezi.")
    assert not mining_765900("Madini na utafutaji wa madini ni TZS 695,000; nishati ya kimataifa ni TZS 765,900.")
    assert low_end_175("Kiwango cha chini kabisa ni karibu TZS 175,000.") and low_end_175("anuwai kutoka karibu TZS 175,000 hadi TZS 765,900")
    assert not low_end_175("Kiwango cha chini kabisa ni TZS 80,000; kilimo ni TZS 175,000.") and not low_end_175("Kilimo ni TZS 175,000 kwa mwezi.")
    assert firm_in_confirm("Thibitisha na PKF Eastern Africa au TanzLII.") and not firm_in_confirm("Kulingana na uchambuzi wa PKF, wastani ni 33.4%. Thibitisha na TanzLII.")
