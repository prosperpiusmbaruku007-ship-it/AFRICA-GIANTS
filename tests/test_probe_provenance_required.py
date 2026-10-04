# -*- coding: utf-8 -*-
"""EVERY PROBE ASSERTING A CHECKABLE QUANTITY MUST CITE A SOURCE.

WHY THIS TEST EXISTS. A gold answer is a CLAIM ABOUT THE LAW, and every failure count this
project quotes is the model measured against those claims. Measured 2026-09-29
(eval/results/gold_answer_provenance_audit.json): of 276 gold answers in the three corpora the
counts come from, 73 assert a figure, rate or deadline that a statute could confirm AND CITE
NOTHING -- all 73 in edge_probe_extended_078_DRAFT.jsonl and edge_probe_natural_048.jsonl, whose
schemas had no source field at all. Not blank: absent.

The corroborating detail is what makes this a test rather than a note: eval_questions_003.jsonl
DOES carry source_url on all 150 rows, and 4 of the 6 scoring-key corrections in the whole
repository live there. A cited key can be checked, and was. An uncited one cannot be, so a wrong
key is booked as a model failure forever -- the adjudication reads the key.

WHAT THIS ASSERTS, and it is deliberately scoped to what is enforceable:
  * a row whose gold answer asserts a checkable quantity must carry a non-empty source field
  * a row whose gold is pure rubric prose ("must not fabricate an issuer") needs none, because
    there is no quantity to check -- R20: "no assertion needed here" is a valid recorded outcome
  * GRANDFATHERING IS EXPLICIT AND SHRINKING. The 73 rows measured on 2026-09-29 are listed in
    PENDING_BACKFILL by id. A row leaves that list when it gets a source; a NEW row may never
    join it. So this test fails for any probe added from today without provenance, while the
    backfill proceeds against a list that can only get smaller.

R26: both directions are exercised below -- a planted uncited quantitative row MUST fail the
check, and a cited one MUST pass. A test that only ever passes on the current corpus is the
vacuous shape this project keeps finding.
"""
import json
import os
import re

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FIXTURES = ("eval/accuracy_gate/edge_probe_extended_078_DRAFT.jsonl",
            "eval/accuracy_gate/edge_probe_natural_048.jsonl")
GOLD_KEYS = ("expected_behavior", "correct_answer_sw", "correct_answer_en")
SOURCE_KEYS = ("source", "source_url", "primary_source", "statute", "verified_against")

_MONEY = re.compile(r"(?:TZS|USD)\s*[\d,]{3,}|\b\d{1,3}(?:,\d{3}){1,}\b")
_RATE = re.compile(r"\b\d{1,2}(?:\.\d)?\s*%|asilimia\s+[\w\s\.]{1,20}")
_DEADLINE = re.compile(r"\b(?:siku|days?|miezi|months?|mwaka|years?)\s+\d{1,3}|"
                       r"\b\d{1,3}\s+(?:siku|days?|miezi|months?|mwaka|years?)", re.I)

# The uncited quantitative rows STILL outstanding. Started at 73 (measured 2026-09-29);
# pass 1 on 2026-10-04 sourced 21 against primary sources, leaving 52.
# A BACKFILL WORKLIST, NOT AN EXEMPTION: ids leave as each gets a source, and nothing may be
# added -- test_backfill_worklist_only_shrinks enforces both directions.
PENDING_BACKFILL = {
    "ext_01", "ext_02", "ext_03", "ext_04", "ext_07", "ext_08", "ext_09", "ext_10", "ext_13",
    "ext_14", "ext_18", "ext_19", "ext_20", "ext_22", "ext_23", "ext_29", "ext_30", "ext_32",
    "ext_50", "ext_54", "ext_56", "ext_63", "ext_68", "ext_69", "ext_71", "ext_72", "ext_73",
    "ext_75", "ext_76", "ext_78", "nat_06", "nat_07", "nat_08", "nat_09", "nat_11", "nat_12",
    "nat_13", "nat_14", "nat_15", "nat_17", "nat_18", "nat_20", "nat_22", "nat_25", "nat_26",
    "nat_28", "nat_29", "nat_31", "nat_34", "nat_36", "nat_42", "nat_44"
}


def _rows():
    out = []
    for rel in FIXTURES:
        path = os.path.join(REPO, rel)
        with open(path, encoding="utf-8") as fh:
            for ln, line in enumerate(fh, 1):
                if line.strip():
                    out.append((rel, ln, json.loads(line)))
    return out


def asserts_checkable_quantity(row):
    gold = " ".join(str(row.get(k, "")) for k in GOLD_KEYS)
    return bool(_MONEY.search(gold) or _RATE.search(gold) or _DEADLINE.search(gold))


def has_source(row):
    return any(str(row.get(k, "")).strip() for k in SOURCE_KEYS)


def test_no_new_probe_asserts_a_quantity_without_a_source():
    """A probe added from 2026-10-04 on must cite what settles its gold answer."""
    offenders = [(rel, ln, r.get("id")) for rel, ln, r in _rows()
                 if asserts_checkable_quantity(r) and not has_source(r)
                 and r.get("id") not in PENDING_BACKFILL]
    assert not offenders, (
        "these probes assert a figure/rate/deadline with no source field, and are not on the "
        f"2026-09-29 backfill worklist: {offenders}. A gold answer is a claim about the law; an "
        "uncited one cannot be checked, so a wrong key is booked as a model failure forever.")


def test_backfill_worklist_only_shrinks():
    """Every id on the worklist must still exist and must still lack a source.

    An id that has GAINED a source has to leave the list -- otherwise the list becomes a
    permanent exemption rather than a worklist, and the census it feeds reports work remaining
    that is already done (the stale-pin decay shape).
    """
    by_id = {r.get("id"): r for _, _, r in _rows()}
    unknown = sorted(i for i in PENDING_BACKFILL if i not in by_id)
    assert not unknown, f"worklist names ids that no longer exist: {unknown}"
    now_sourced = sorted(i for i in PENDING_BACKFILL if has_source(by_id[i]))
    assert not now_sourced, (
        f"these ids now HAVE a source and must be removed from PENDING_BACKFILL: {now_sourced}")


def test_the_check_itself_fires_and_is_not_overbroad():
    """R26 both directions. A planted uncited quantitative row must fail; a cited one must pass.

    Without this, the two tests above pass trivially on any corpus whose rows all happen to be
    grandfathered -- which is exactly the state the corpus is in today.
    """
    uncited = {"id": "planted_x1",
               "expected_behavior": "The fee is TZS 22,000 per annum."}
    cited = {"id": "planted_x2",
             "expected_behavior": "The fee is TZS 22,000 per annum.",
             "source": "brela.go.tz/pages/tozo-za-kampuni"}
    prose = {"id": "planted_x3",
             "expected_behavior": "Must not fabricate an issuing office."}

    assert asserts_checkable_quantity(uncited) and not has_source(uncited)   # would FAIL
    assert asserts_checkable_quantity(cited) and has_source(cited)           # would PASS
    assert not asserts_checkable_quantity(prose)                             # needs no source


@pytest.mark.parametrize("rel", FIXTURES)
def test_fixture_declares_the_source_field_in_its_schema(rel):
    """At least one row in each fixture must carry the field, so the schema is not merely
    documented as required while being absent everywhere -- which is the state that produced
    73 uncited rows."""
    rows = [r for f, _, r in _rows() if f == rel]
    assert any(has_source(r) for r in rows), (
        f"{rel} has no row carrying any of {SOURCE_KEYS}. The field must exist in the schema, "
        f"not only in this test's expectations.")
