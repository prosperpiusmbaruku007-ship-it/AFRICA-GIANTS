# -*- coding: utf-8 -*-
"""Holding-message authority (founder, 2026-11-26): football / foreign-country questions get 'mamlaka husika', never TRA's number."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chike-whatsapp"))
import handler_core as core  # noqa: E402


def _it(q, path="fact"):
    return {"question": q, "answer_path": path}


@pytest.mark.parametrize("q", [
    "Simba SC watacheza lini na Yanga? Kodi ya tiketi ni ngapi?",     # a tax word is present: the off-topic cue must still win
    "Nani atashinda kombe la dunia?",
    "Messi ana mshahara kiasi gani?",
    "Kodi ya KRA kwa biashara ndogo Kenya ni asilimia ngapi?",
    "VAT nchini Uganda ni kiasi gani?",
    "What is the corporate tax rate in the United Kingdom?",
])
def test_offtopic_questions_get_the_generic_line_and_no_authority(q):
    assert core.holding_authorities(_it(q)) == []
    t = core.holding_text(_it(q))
    assert t == core.HOLDING_TEXT and t.endswith("mamlaka husika.")
    for contact in core.AUTHORITY_CONTACTS.values():
        assert contact not in t, "no authority's contact line may appear"


def test_a_route_cannot_override_the_offtopic_rule():
    assert core.holding_text(_it("Kodi ya mapato Kenya", path="engine:paye")) == core.HOLDING_TEXT


@pytest.mark.parametrize("q,key", [
    ("Mshahara wangu ni milioni 1, PAYE ni kiasi gani?", "tra"),          # positive controls: the rule must not blank real topics
    ("Michango ya NSSF inalipwa lini?", "nssf"),
    ("Leseni ya biashara inaisha lini?", "licence"),
])
def test_CONTROL_real_topics_still_get_their_authority(q, key):
    assert core.holding_authorities(_it(q)) == [key]
    assert core.AUTHORITY_CONTACTS[key] in core.holding_text(_it(q))


def test_word_boundaries_hold():
    assert core.holding_authorities(_it("Nina kampuni ya kuagiza bidhaa, VAT inatozwa vipi?")) == ["tra"]   # 'kampuni' etc. contain no cue
