"""The Gate 2 held-out set is authored by someone other than the assistant (founder's decision, 2026-11-16). The validator checks SHAPE and PROVENANCE only.

R26 both directions: the template must FAIL (placeholders), an assistant-authored set must FAIL, a short set must FAIL, a well-formed set written by a person must PASS, and a frozen set
that is edited must be CAUGHT. The synthetic rows below are SHAPE FIXTURES with filler text, not questions: nothing here is a candidate for the real set."""
import importlib.util
import json
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("hv", os.path.join(_ROOT, "eval", "refusal_gate", "validate_heldout_set.py"))
hv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hv)


def _write(tmp_path, rows):
    p = tmp_path / "set.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    return str(p)


def _valid_rows(author="other_person"):
    rows, n = [], 0
    for ax in hv.AXES:
        for i in range(hv.MIN_PER_AXIS):
            n += 1
            rows.append({"id": f"ho_{n:03d}", "limb": "ooc", "axis": ax, "question": f"shape fixture ooc {ax} number {i} filler", "expect": "REFUSE", "topic": f"t{n // 3}",
                         "authored_by": author, "author_note": "", "seen_system_output": False})
    for i in range(hv.MIN_CONTROL - 0):
        n += 1
        rows.append({"id": f"ho_{n:03d}", "limb": "control", "axis": "control", "question": f"shape fixture control number {i} filler", "expect": "ANSWER", "topic": f"c{i // 3}",
                     "authored_by": author, "author_note": "", "seen_system_output": False})
    # ooc total = 5 axes * 8 = 40 < 60: top up
    while sum(1 for r in rows if r["limb"] == "ooc") < hv.MIN_OOC:
        n += 1
        rows.append({"id": f"ho_{n:03d}", "limb": "ooc", "axis": hv.AXES[n % 5], "question": f"shape fixture extra ooc number {n} filler", "expect": "REFUSE", "topic": f"x{n // 3}",
                     "authored_by": author, "author_note": "", "seen_system_output": False})
    return rows


def test_the_template_fails_validation():
    problems, _ = hv.validate(os.path.join(_ROOT, "eval", "refusal_gate", "heldout", "heldout_outofscope_TEMPLATE.jsonl"))
    assert any("placeholder" in p for p in problems) and any("ooc rows" in p for p in problems)


def test_a_well_formed_set_by_a_person_passes(tmp_path):
    problems, rows = hv.validate(_write(tmp_path, _valid_rows()))
    assert problems == [] and len(rows) >= hv.MIN_OOC + hv.MIN_CONTROL


def test_plant_an_assistant_authored_set_is_rejected(tmp_path):
    for who in ("assistant", "claude", "Claude Sonnet", "gpt-4", "bot"):
        problems, _ = hv.validate(_write(tmp_path, _valid_rows(author=who)))
        assert any("may not author" in p for p in problems), who


def test_plant_a_short_set_a_wrong_expect_a_duplicate_and_an_overfull_topic_are_each_caught(tmp_path):
    rows = _valid_rows()
    assert any("ooc rows" in p for p in hv.validate(_write(tmp_path, rows[:20]))[0])
    bad = [dict(r) for r in rows]
    bad[0]["expect"] = "ANSWER"
    assert any("does not match limb" in p for p in hv.validate(_write(tmp_path, bad))[0])
    dup = [dict(r) for r in rows]
    dup[1]["question"] = dup[0]["question"]
    assert any("duplicate questions" in p for p in hv.validate(_write(tmp_path, dup))[0])
    hot = [dict(r) for r in rows]
    for r in hot[:5]:
        r["topic"] = "same theme"
    assert any("at most" in p for p in hv.validate(_write(tmp_path, hot))[0])


def test_a_seen_system_output_true_is_recorded_not_rejected(tmp_path):
    rows = _valid_rows()
    rows[0]["seen_system_output"] = True
    assert hv.validate(_write(tmp_path, rows))[0] == []


def test_plant_editing_a_frozen_set_is_caught(tmp_path, monkeypatch):
    p = _write(tmp_path, _valid_rows())
    monkeypatch.setattr(hv, "HELD", str(tmp_path))
    fz = tmp_path / "FROZEN.json"
    monkeypatch.setattr(hv, "FROZEN", str(fz))
    assert hv.main(["--file", p, "--freeze"]) == 0 and fz.exists()
    assert hv.main(["--file", p, "--check-frozen"]) == 0
    with open(p, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"id": "ho_999"}) + "\n")
    assert hv.main(["--file", p, "--check-frozen"]) == 1
    assert hv.main(["--file", p, "--freeze"]) == 1, "a set is frozen once"


def test_the_real_authored_file_if_it_exists_is_unchanged_since_it_was_frozen():
    authored = os.path.join(_ROOT, "eval", "refusal_gate", "heldout", "heldout_outofscope_AUTHORED.jsonl")
    if os.path.exists(authored) and os.path.exists(hv.FROZEN):
        assert hv.check_frozen(authored) == []
