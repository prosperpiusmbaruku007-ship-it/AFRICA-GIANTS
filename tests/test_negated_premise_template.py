"""The negated-premise authoring package (2026-11-16): the TEMPLATE must fail validation (placeholders), a synthetic valid set must pass, the validator must refuse Claude Code as an author (the HARD RULE), accept an
external_model row only with its model, session, reviewer and `independence: weaker`, require `author_source` on every row, refuse a set with no source, unbalanced labels or too few forms, and a frozen set must refuse edits.
Synthetic rows are SHAPE fixtures written to a tmp dir, never to the authored file; no question in this file is a probe.

HISTORY: the first version asserted that NO authored file existed ("the assistant must not create the authored set"). The founder then supplied 29 questions written by external models (Claude in the claude.ai advisor
session; a second model named 'chartgpt') and decided (2026-11-16) that the rule is "no row authored by claude_code AND every row records its author source". That is the test below; the old one is kept here as history.
"""
import importlib.util
import json
import os

import pytest

HERE = os.path.join("eval", "fidelity", "negated_premise_heldout")
_spec = importlib.util.spec_from_file_location("vnp", os.path.join(HERE, "validate_negated_premise_set.py"))
v = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v)
AUTHORED = os.path.join(HERE, "negated_premise_AUTHORED.jsonl")


def _row(i, form="negative_verb", label="true_premise", topic="vat", author="founder", source="Act Cap.148", **extra):
    r = {"id": f"np_{i:02d}", "question": f"synthetic shape fixture number {i} {form} {label}", "negation_form": form, "premise_label": label, "correct_polarity": "YES", "topic": topic,
         "correct_answer_sw": "fixture", "source": source, "authored_by": author, "author_note": "", "seen_system_output": False, "author_source": "synthetic fixture for the validator tests"}
    if author == "external_model":
        r.update(author_model="SomeModel", author_session="a session", reviewed_by="founder", independence="weaker")
    r.update(extra)
    return r


def _valid_set(author="founder"):
    forms = ["negative_verb", "tag_question", "belief_check"]
    topics = ["vat", "paye", "sdl", "nssf", "wcf", "efd", "brela", "osha", "gn487a", "gn605a"]
    rows = [_row(i + 1, forms[i % 3], "true_premise" if i % 2 == 0 else "false_premise", topics[i % 10], author) for i in range(14)]
    rows += [_row(15 + j, "none", "true_premise", topics[(j + 3) % 10], author) for j in range(6)]
    return rows


def _write(tmp_path, rows):
    p = tmp_path / "set.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    return str(p)


def _problems(tmp_path, rows):
    return v.validate(_write(tmp_path, rows))[0]


def test_the_template_itself_fails_validation():
    problems, rows = v.validate(os.path.join(HERE, "negated_premise_TEMPLATE.jsonl"))
    assert rows and any("placeholder" in p or "missing" in p for p in problems)


@pytest.mark.parametrize("author", ["founder", "external_model"])
def test_a_valid_synthetic_set_passes(tmp_path, author):
    problems, rows = v.validate(_write(tmp_path, _valid_set(author)))
    assert not problems and len(rows) == 20


# ---- THE HARD RULE ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("field,value", [("authored_by", "claude_code"), ("authored_by", "Claude Code"), ("author_model", "Claude Code"), ("author_session", "a Claude Code session")])
def test_no_row_may_be_authored_by_claude_code(tmp_path, field, value):
    rows = _valid_set("external_model")
    rows[0][field] = value
    assert any("Claude Code" in p or "must be one of" in p for p in _problems(tmp_path, rows)), field


def test_claude_as_an_external_model_in_another_session_is_allowed(tmp_path):
    rows = _valid_set("external_model")
    rows[0].update(author_model="Claude", author_session="claude.ai advisor session")
    assert not _problems(tmp_path, rows)


# ---- external_model must be complete and labelled -----------------------------------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("missing", ["author_model", "author_session", "reviewed_by", "independence"])
def test_an_external_model_row_must_record_its_provenance(tmp_path, missing):
    rows = _valid_set("external_model")
    rows[2].pop(missing)
    assert any(missing in p for p in _problems(tmp_path, rows))


def test_an_external_model_row_must_be_labelled_weaker_independence(tmp_path):
    rows = _valid_set("external_model")
    rows[1]["independence"] = "full"
    assert any("independence: weaker" in p for p in _problems(tmp_path, rows))


def test_every_row_must_record_its_author_source(tmp_path):
    rows = _valid_set()
    rows[4]["author_source"] = ""
    assert any("no author_source" in p for p in _problems(tmp_path, rows))
    rows = _valid_set()
    rows[4].pop("author_source")
    assert any("missing" in p and "author_source" in p for p in _problems(tmp_path, rows))


# ---- polarity OPEN, forms, caps, balance ----------------------------------------------------------------------------------------------------------------------------------------------------------
def test_an_open_row_is_valid_only_in_its_own_shape(tmp_path):
    rows = _valid_set()
    rows[16].update(correct_polarity="OPEN", premise_label="not_applicable", answer_kind="open")
    assert not _problems(tmp_path, rows)
    rows[16]["premise_label"] = "true_premise"
    assert any("OPEN row needs" in p for p in _problems(tmp_path, rows))
    rows = _valid_set()
    rows[3]["premise_label"] = "not_applicable"
    assert any("not_applicable is only for OPEN" in p for p in _problems(tmp_path, rows))


def test_belief_check_is_an_accepted_form_and_counts_as_a_form(tmp_path):
    rows = _valid_set()
    assert any(r["negation_form"] == "belief_check" for r in rows) and not _problems(tmp_path, rows)
    for r in rows:
        if r["negation_form"] == "belief_check":
            r["negation_form"] = "tag_question"
    assert any("different negation forms" in p for p in _problems(tmp_path, rows))


def test_topic_caps_default_4_vat_5_labour_6(tmp_path):
    rows = _valid_set()
    for r in rows:
        r["topic"] = "efd"
    assert any("topic 'efd'" in p and "at most 4" in p for p in _problems(tmp_path, rows))
    for cap, topic in ((5, "vat"), (6, "labour")):
        rows = _valid_set()
        for r in rows[:cap]:
            r["topic"] = topic
        for r in rows[cap:]:
            r["topic"] = "paye" if r["id"] < "np_13" else "nssf"
        rows = [r for r in rows]
        assert not any(f"topic {topic!r}" in p for p in _problems(tmp_path, rows)), topic
        rows[cap]["topic"] = topic
        assert any(f"topic {topic!r}" in p and f"at most {cap}" in p for p in _problems(tmp_path, rows)), topic


def test_a_row_without_a_source_is_refused(tmp_path):
    rows = _valid_set()
    rows[3]["source"] = ""
    assert any("no source" in p for p in _problems(tmp_path, rows))


@pytest.mark.parametrize("mutate,needle", [
    (lambda rows: [r.update(premise_label="true_premise") for r in rows if r["negation_form"] != "none"], "false_premise rows"),
    (lambda rows: [r.update(negation_form="negative_verb") for r in rows if r["negation_form"] != "none"], "different negation forms"),
    (lambda rows: rows.pop(), "plain control rows"),
])
def test_balance_rules_are_enforced(tmp_path, mutate, needle):
    rows = _valid_set()
    mutate(rows)
    assert any(needle in p for p in _problems(tmp_path, rows)), needle


def test_a_frozen_set_refuses_edits(tmp_path, monkeypatch):
    path = _write(tmp_path, _valid_set())
    monkeypatch.setattr(v, "FROZEN", str(tmp_path / "FROZEN.json"))
    assert v.main(["--file", path, "--freeze"]) == 0
    assert v.main(["--file", path, "--check-frozen"]) == 0
    with open(path, "a", encoding="utf-8") as fh:
        fh.write("\n")
    assert v.main(["--file", path, "--check-frozen"]) == 1


# ---- the REAL authored file (replaces "no authored file exists yet") ------------------------------------------------------------------------------------------------------------------------------
def test_the_real_authored_set_has_no_claude_code_author_and_every_row_records_its_author_source():
    if not os.path.exists(AUTHORED):
        pytest.skip("no authored set yet")
    rows = [json.loads(l) for l in open(AUTHORED, encoding="utf-8") if l.strip()]
    assert rows
    for r in rows:
        assert not v.CLAUDE_CODE.search(json.dumps({k: r.get(k) for k in ("authored_by", "author_model", "author_session")})), r["id"]
        assert str(r.get("author_source", "")).strip(), f"{r['id']} records no author_source"
        assert r["authored_by"] == "external_model" and r.get("independence") == "weaker" and r.get("author_model") and r.get("author_session"), r["id"]
    problems, _ = v.validate(AUTHORED)
    assert not problems, problems[:3]


def test_np_24_is_dropped_with_its_reason_on_record():
    if not os.path.exists(AUTHORED):
        pytest.skip("no authored set yet")
    assert "np_24" not in {json.loads(l)["id"] for l in open(AUTHORED, encoding="utf-8") if l.strip()}
    rec = json.load(open(os.path.join(HERE, "DROPPED.json"), encoding="utf-8"))
    assert rec[0]["id"] == "np_24" and "AMBIGUOUS POLARITY" in rec[0]["reason"] and rec[0]["decided_by"] == "founder"
