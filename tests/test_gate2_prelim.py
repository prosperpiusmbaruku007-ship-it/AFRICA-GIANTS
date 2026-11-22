"""The PRELIMINARY Gate 2 set (eval/refusal_gate/preliminary/): a SEPARATE profile from the formal held-out set. These tests pin three things: the committed set validates; once frozen its bytes never change
(a frozen set is never edited); and the profile REFUSES what it exists to refuse -- an assistant-authored question, a formal_set flag, a control with no answer or source. Each rule is PLANTED (R26): a bad row is
fed to the validator and must be reported. Also pins that the formal held-out template is untouched and still invalid (it is not this set)."""
import copy
import hashlib
import importlib.util
import io
import json
import os

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PRE = os.path.join(_ROOT, "eval", "refusal_gate", "preliminary")
_spec = importlib.util.spec_from_file_location("vps_test", os.path.join(_PRE, "validate_prelim_set.py"))
vps = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vps)
ROWS = [json.loads(l) for l in io.open(vps.SET, encoding="utf-8") if l.strip()]


def _problems(rows, tmp_path):
    p = tmp_path / "set.jsonl"
    p.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
    return vps.validate(str(p))[0]


def test_the_committed_set_validates_and_has_the_agreed_shape():
    problems, rows = vps.validate(vps.SET)
    assert problems == [] and len(rows) == 26
    assert [sum(1 for r in rows if r["limb"] == k) for k in ("ooc", "hedge", "control")] == [19, 1, 6]


def test_the_set_is_frozen_and_unchanged():
    assert vps.check_frozen(vps.SET) == []
    rec = json.load(io.open(vps.FROZEN, encoding="utf-8"))
    assert rec["formal_set"] is False and rec["rows"] == 26 and rec["sha256"] == hashlib.sha256(io.open(vps.SET, "rb").read()).hexdigest()


def test_every_row_records_the_weaker_independence_and_no_system_output():
    for r in ROWS:
        assert r["authored_by"] == "external_model:ChatGPT" and "weaker independence" in r["independence"]
        assert r["seen_system_output"] is False and r["formal_set"] is False


def test_the_six_controls_carry_a_filled_answer_and_the_licence_row_says_twelve_months():
    ctl = [r for r in ROWS if r["limb"] == "control"]
    assert len(ctl) == 6 and all(r["filled_by"] == "claude_code" and r["correct_answer"] and r["source"] for r in ctl)
    c23 = next(r for r in ctl if r["n"] == 23)
    assert "12 months from the date of issue" in c23["correct_answer"] and "September NEXT YEAR" in c23["correct_answer"]


def test_a_frozen_set_edited_by_one_byte_is_reported(tmp_path):
    copy_path = tmp_path / "set.jsonl"
    copy_path.write_bytes(io.open(vps.SET, "rb").read() + b" ")
    assert vps.check_frozen(str(copy_path))


@pytest.mark.parametrize("mutate,needle", [
    (lambda r: r.update(authored_by="claude_code"), "authored_by"),
    (lambda r: r.update(authored_by="assistant"), "authored_by"),
    (lambda r: r.update(formal_set=True), "formal_set"),
    (lambda r: r.update(seen_system_output=True), "seen_system_output"),
    (lambda r: r.update(independence="fully independent"), "independence"),
    (lambda r: r.update(expect="ANSWER"), "expect"),
    (lambda r: r.update(axis="other_jurisdiction"), "axis"),                  # OFF_TOPIC must map to not_compliance
    (lambda r: r.update(question="<<WRITE YOUR OWN QUESTION HERE>>"), "question"),
])
def test_plant_the_profile_rejects_a_bad_ooc_row(mutate, needle, tmp_path):
    rows = copy.deepcopy(ROWS)
    mutate(rows[0])
    assert any(needle in p for p in _problems(rows, tmp_path))


@pytest.mark.parametrize("drop", ["correct_answer", "source"])
def test_plant_a_control_without_an_answer_or_source_is_rejected(drop, tmp_path):
    rows = copy.deepcopy(ROWS)
    next(r for r in rows if r["limb"] == "control").pop(drop)
    assert _problems(rows, tmp_path)


def test_plant_a_control_filled_by_someone_else_is_rejected(tmp_path):
    rows = copy.deepcopy(ROWS)
    next(r for r in rows if r["limb"] == "control")["filled_by"] = "founder"
    assert any("filled_by" in p for p in _problems(rows, tmp_path))


def test_plant_a_wrong_row_count_or_duplicate_is_rejected(tmp_path):
    assert any("26" in p for p in _problems(ROWS[:-1], tmp_path))
    dup = copy.deepcopy(ROWS)
    dup[1]["question"] = dup[0]["question"]
    assert any("duplicate" in p for p in _problems(dup, tmp_path))


def test_the_formal_heldout_template_is_untouched_and_still_not_a_valid_set():
    """The formal set still needs 60 ooc + 30 controls from a human author: its template must be unchanged and must NOT validate."""
    spec = importlib.util.spec_from_file_location("vho_test", os.path.join(_ROOT, "eval", "refusal_gate", "validate_heldout_set.py"))
    vho = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vho)
    tpl = os.path.join(_ROOT, "eval", "refusal_gate", "heldout", "heldout_outofscope_TEMPLATE.jsonl")
    assert vho.validate(tpl)[0]                                        # a template with placeholders is invalid
    assert not os.path.exists(vho.AUTHORED) and not os.path.exists(vho.FROZEN)
