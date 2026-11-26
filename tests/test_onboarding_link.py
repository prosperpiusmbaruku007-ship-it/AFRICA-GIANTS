# -*- coding: utf-8 -*-
"""Inbound-first onboarding link (item A). Plants (R26): each limb has a positive control so a check that rejects everything cannot pass.

* The pre-filled text must reach the GREETING path (disclosure + welcome, no model call). Planted against the old GREETINGS set, where
  "Habari Chike" was classified as a QUESTION.
* The builder refuses a text that would be a question, and a malformed number.
* No phone number literal in the script (the number is supplied locally, never committed).
"""
import importlib.util
import os
import re
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "chike-whatsapp"))
import handler_core as core  # noqa: E402

_spec = importlib.util.spec_from_file_location("make_onboarding_link", os.path.join(_ROOT, "scripts", "make_onboarding_link.py"))
ol = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ol)


def _inbound(text):
    return core.parse_webhook({"event": "messages.received",
                               "data": {"messages": {"key": {"remoteJid": "255700000000@s.whatsapp.net", "fromMe": False}, "conversation": text}}})


def test_prefilled_text_is_classified_as_greeting():
    assert _inbound(ol.PREFILLED_TEXT)["kind"] == "greeting"


def test_plant_old_greetings_set_classified_it_as_a_question(monkeypatch):
    monkeypatch.setattr(core, "GREETINGS", core.GREETINGS - {"habari chike"})
    assert _inbound(ol.PREFILLED_TEXT)["kind"] == "question"       # the pre-fix behaviour this item exists to avoid


def test_positive_control_a_real_question_stays_a_question():
    assert _inbound("PAYE ni asilimia ngapi?")["kind"] == "question"


def test_link_shape_and_encoding():
    link = ol.build_link("+255 700 000 000")
    assert link == "https://wa.me/255700000000?text=Habari%20Chike"


def test_builder_refuses_a_text_that_would_be_a_question():
    with pytest.raises(ValueError, match="not a greeting"):
        ol.build_link("255700000000", "Nataka kujua VAT ni asilimia ngapi")


@pytest.mark.parametrize("bad", ["", "abc", "123", "2557000000001234567", None])
def test_builder_refuses_a_malformed_number(bad):
    with pytest.raises(ValueError):
        ol.build_link(bad)


def test_script_contains_no_phone_number_literal():
    src = open(os.path.join(_ROOT, "scripts", "make_onboarding_link.py"), encoding="utf-8").read()
    assert not re.findall(r"\b255\d{9}\b", src)
    assert re.findall(r"\b255\d{9}\b", "x 255700000000 y")        # positive control: the pattern does match a number


def test_outputs_land_in_the_gitignored_scratch_dir():
    assert ol.OUT_DIR.endswith(os.path.join("scratch", "onboarding"))
    assert "scratch/" in open(os.path.join(_ROOT, ".gitignore"), encoding="utf-8").read()


def test_link_file_is_written_without_segno(tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, "segno", None)               # simulate it not being installed
    assert ol.write_outputs(ol.build_link("255700000000"), str(tmp_path)) is False
    assert (tmp_path / "link.txt").read_text(encoding="utf-8").startswith("https://wa.me/")
