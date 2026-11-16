"""The negated-premise authoring package (2026-11-16): the TEMPLATE must fail validation (placeholders), a synthetic valid set must pass, the validator must refuse an assistant author, a set with no source,
and unbalanced labels, and a frozen set must refuse edits. Synthetic rows here are SHAPE fixtures written to a tmp dir, never to the authored file; no question in this file is a probe."""
import importlib.util
import json
import os

import pytest

HERE = os.path.join("eval", "fidelity", "negated_premise_heldout")
_spec = importlib.util.spec_from_file_location("vnp", os.path.join(HERE, "validate_negated_premise_set.py"))
v = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v)


def _row(i, form="si_kweli", label="true_premise", topic="vat", author="founder", source="Act Cap.148"):
    return {"id": f"np_{i:02d}", "question": f"synthetic shape fixture number {i} {form} {label}", "negation_form": form, "premise_label": label, "correct_polarity": "YES", "topic": topic,
            "correct_answer_sw": "fixture", "source": source, "authored_by": author, "author_note": "", "seen_system_output": False}


def _valid_set():
    forms = ["si_kweli", "negative_verb", "tag_question"]
    topics = ["vat", "paye", "sdl", "nssf", "wcf", "efd", "brela", "osha", "gn487a", "gn605a"]
    rows = []
    for i in range(14):
        rows.append(_row(i + 1, forms[i % 3], "true_premise" if i % 2 == 0 else "false_premise", topics[i % 10]))
    for j in range(6):
        rows.append(_row(15 + j, "none", "true_premise", topics[(j + 3) % 10]))
    return rows


def _write(tmp_path, rows):
    p = tmp_path / "set.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    return str(p)


def test_the_template_itself_fails_validation():
    problems, rows = v.validate(os.path.join(HERE, "negated_premise_TEMPLATE.jsonl"))
    assert rows and any("placeholder" in p for p in problems)


def test_a_valid_synthetic_set_passes(tmp_path):
    problems, rows = v.validate(_write(tmp_path, _valid_set()))
    assert not problems and len(rows) == 20


def test_the_assistant_may_not_author(tmp_path):
    rows = _valid_set()
    rows[0]["authored_by"] = "claude"
    assert any("may not author" in p for p in v.validate(_write(tmp_path, rows))[0])


def test_a_row_without_a_source_is_refused(tmp_path):
    rows = _valid_set()
    rows[3]["source"] = ""
    assert any("no source" in p for p in v.validate(_write(tmp_path, rows))[0])


@pytest.mark.parametrize("mutate,needle", [
    (lambda rows: [r.update(premise_label="true_premise") for r in rows if r["negation_form"] != "none"], "false_premise rows"),
    (lambda rows: [r.update(topic="vat") for r in rows], "topic 'vat'"),
    (lambda rows: [r.update(negation_form="si_kweli") for r in rows if r["negation_form"] != "none"], "different negation forms"),
    (lambda rows: rows.pop(), "plain control rows"),
])
def test_balance_rules_are_enforced(tmp_path, mutate, needle):
    rows = _valid_set()
    mutate(rows)
    assert any(needle in p for p in v.validate(_write(tmp_path, rows))[0]), needle


def test_a_frozen_set_refuses_edits(tmp_path, monkeypatch):
    path = _write(tmp_path, _valid_set())
    monkeypatch.setattr(v, "FROZEN", str(tmp_path / "FROZEN.json"))
    assert v.main(["--file", path, "--freeze"]) == 0
    assert v.main(["--file", path, "--check-frozen"]) == 0
    with open(path, "a", encoding="utf-8") as fh:
        fh.write("\n")
    assert v.main(["--file", path, "--check-frozen"]) == 1


def test_no_authored_file_exists_yet_so_nothing_has_been_measured():
    assert not os.path.exists(os.path.join(HERE, "negated_premise_AUTHORED.jsonl")), "the assistant must not create the authored set"
