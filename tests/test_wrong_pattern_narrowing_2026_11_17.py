# -*- coding: utf-8 -*-
"""corporate_income_tax_return.wrong_patterns[0] was NARROWED on 2026-11-17 (founder, decision 5) so that it no longer matches BRELA ANNUAL-RETURN text: it matched "annual return kila mwaka -- hasa ndani ya miezi 12"
(a stored gate reply) and a training pair that DENIES a 30 September date for BRELA returns. A negative lookbehind on "annual " removes both; the tax-return claims it exists to catch still match."""
import json
import re

FACT = json.load(open("scripts/locked_facts.json", encoding="utf-8"))["corporate_income_tax_return"]
RX = re.compile(FACT["wrong_patterns"][0], re.IGNORECASE)

MUST_MATCH = [
    "Kampuni lazima iwasilishe return ya kodi ya mapato ndani ya miezi 12 baada ya mwisho wa mwaka wake wa mapato.",      # the live wrong-topic specimen (wrongtopic_deploy_live_2026_11_17.json)
    "Return ya kampuni ni ndani ya miezi 12 baada ya mwaka wa mapato.",
    "Tamko la kodi ya kampuni ni baada ya miezi 12.",
]
MUST_NOT_MATCH = [
    "Kampuni iliyosajiliwa na BRELA inapaswa kuwasilisha annual return kila mwaka — hasa ndani ya miezi 12 kutoka tarehe ya usajili wake.",
    "Annual return ndani ya miezi 12 si tarehe ya BRELA.",
]


def test_the_tax_return_claims_still_match():
    for t in MUST_MATCH:
        assert RX.search(t), t


def test_brela_annual_return_text_no_longer_matches():
    for t in MUST_NOT_MATCH:
        assert not RX.search(t), t


def test_the_pattern_carries_no_control_character_and_still_compiles_to_a_word_boundary():
    assert chr(8) not in FACT["wrong_patterns"][0] and (chr(92) + "b") in FACT["wrong_patterns"][0]
