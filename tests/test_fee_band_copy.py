# -*- coding: utf-8 -*-
"""D-FIDELITY-8's REPLACEMENT COPY, PINNED (2026-10-08).

The copy is the CONTENT DECISION that was blocking the guard's wiring: the defect lives on
the fact path, where `_render` returns the body alone, so blanking ships silence. The founder
set the shape -- replace a wrong fee with the RULE rather than a figure -- and these tests
hold it to the two properties that make it safe:

  1. EVERY FIGURE IT STATES IS IN THE SERVED INDEX. The copy is generated from
     BRELA_SHARE_CAPITAL_BANDS, and that tuple must agree with served row 181 figure for
     figure. A hand-maintained second copy of a fee table is the dual-file divergence this
     project keeps paying for.
  2. IT PERFORMS NO BAND SELECTION. Band selection is precisely what failed -- the live reply
     gave TZS 290,000 for TZS 2,000,000,000 of share capital. A copy that chose a band could
     choose the wrong one; this one hands the ladder over and asks the user to read off their
     own. That is a STRUCTURAL guarantee, not a hope, and it is what makes stating figures
     safe here while D-FIDELITY-7's copy correctly states none.
"""
import json
import os
import re
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from chike.clarification import (  # noqa: E402
    BRELA_CAPTURE_DATE, BRELA_SHARE_CAPITAL_BANDS, wrong_fee_band_withheld,
    wrong_threshold_withheld)

COPY = wrong_fee_band_withheld()


def _served_row_181():
    with open(os.path.join(REPO, "kaggle", "rag_facts_text.json"), encoding="utf-8") as fh:
        return json.load(fh)[181]


@pytest.mark.parametrize("lo,hi,fee", BRELA_SHARE_CAPITAL_BANDS)
def test_every_band_figure_is_in_the_served_index_row(lo, hi, fee):
    """⛔ THE ANTI-DRIFT ASSERTION. If the ladder is re-priced or re-scoped, this fails and
    the constant must be updated in the same commit -- exactly how EXPECTED_SERVED_SHA256 and
    EXPECTED_HEAD are handled. The ladder has ALREADY been re-scoped once: five bands with an
    open top became nine closed bands on 2026-10-06, and 'band 5' stopped meaning 'above TZS
    50,000,000'. A copy that silently kept the old shape would be the stalest kind of wrong."""
    served = _served_row_181()
    for n in (lo, hi, fee):
        if n is None:
            continue
        assert f"{n:,}" in served, (
            f"TZS {n:,} is in the replacement copy but NOT in served index row 181. The copy "
            f"and the index disagree about the fee ladder; fix the constant in "
            f"chike/clarification.py, or regenerate the index, in the SAME commit.")


def test_the_ladder_has_nine_closed_bands_with_one_open_top():
    """The re-scoping is the reason this guard exists, so its shape is asserted rather than
    assumed: nine rows, a first band with no floor, a last with no ceiling, and contiguous
    edges in between (a gap would make some share capital fall in no band at all)."""
    assert len(BRELA_SHARE_CAPITAL_BANDS) == 9
    assert BRELA_SHARE_CAPITAL_BANDS[0][0] is None, "the first band must have no floor"
    assert BRELA_SHARE_CAPITAL_BANDS[-1][1] is None, "the top band must be open"
    for (_, hi, _), (lo2, _, _) in zip(BRELA_SHARE_CAPITAL_BANDS,
                                       BRELA_SHARE_CAPITAL_BANDS[1:]):
        assert hi == lo2, f"band edges are not contiguous: {hi} then {lo2}"


def test_the_copy_states_the_RULE_before_any_figure():
    """The founder's shape: the fee depends on share capital, here are the bands, check
    BRELA. The rule must come before the ladder, or the reply reads as a list of numbers with
    no way to use it."""
    rule = COPY.index("inategemea")
    first_band = COPY.index("Ngazi za ada:")
    assert rule < first_band, "the ladder is stated before the rule that makes it usable"
    assert "MTAJI WA HISA" in COPY, "the rule does not name what the fee depends on"
    assert "si kiwango kimoja" in COPY, (
        "the copy does not say it is a ladder rather than one rate — which is the "
        "misconception that produced the wrong answer")


def test_the_copy_PERFORMS_NO_BAND_SELECTION():
    """⛔ THE STRUCTURAL GUARANTEE. Band selection is the step that failed, so the copy must
    not attempt it. No second-person fee assertion, no 'therefore', no computed total."""
    for pattern in (r"ada yako ni", r"kwa hiyo ni TZS", r"your fee is", r"jumla ni TZS",
                    r"utalipa TZS"):
        assert not re.search(pattern, COPY, re.I), (
            f"the copy selects a band ({pattern!r}) — the one thing it must not do, because "
            f"selecting is what produced TZS 290,000 for TZS 2,000,000,000")


def test_the_copy_withdraws_the_previous_figure():
    """A replacement that does not withdraw reads as an addition, leaving the wrong figure
    standing earlier in the conversation."""
    assert "siwezi kuihakikisha" in COPY and "sitalitumia" in COPY


def test_the_date_is_framed_as_an_OBSERVATION_not_an_effective_date():
    """⛔ `effective_date` is genuinely UNKNOWN for every figure on this schedule -- the
    change landed somewhere inside 2026-06-30 → 2026-10-06 and the Companies (Fees)
    Regulations have not been located. Presenting the capture date as an effective date would
    manufacture R29 mode 3: a correctly-cited figure carrying an unsourced currency date. A
    trader asking 'was I overcharged in August?' needs that distinction."""
    assert BRELA_CAPTURE_DATE in COPY
    assert "kama ilivyochapishwa" in COPY, (
        "the date is not framed as 'as published on' — it must be an observation, never an "
        "effective date")
    for claim in ("ilianza kutumika", "inatumika kuanzia", "effective from"):
        assert claim not in COPY, f"the copy asserts an effective date via {claim!r}"
    assert "thibitisha ratiba inayotumika sasa" in COPY, (
        "the copy does not ask the user to confirm the CURRENT schedule, which is the only "
        "honest move when the effective date is unknown")


def test_it_does_not_copy_D_FIDELITY_7s_no_figure_stance_by_accident():
    """The two copies are deliberately different shapes, and the difference is the finding:
    a fabricated constant has no rule to state, a misapplied lookup does. If this ever starts
    stating no figures, someone has flattened two different defects into one template."""
    assert "95,000" in COPY and "600,000" in COPY, (
        "the fee copy has stopped stating the ladder — it is not D-FIDELITY-7's case; the "
        "table here is real, published, pinned and already served")
    seven = wrong_threshold_withheld("efd")
    assert not re.search(r"\d[\d,]{4,}", seven), (
        "D-FIDELITY-7's copy has started stating a figure. It must not: it fires on a "
        "FABRICATED constant, where any number is a second guess")


def test_the_copy_is_long_and_that_is_a_recorded_trade_not_an_oversight():
    """~1,000 characters is long for a WhatsApp reply, and shortening it would mean choosing
    which bands to show — which is band selection, the thing that failed. So the length is
    the deliberate price of the structural guarantee. Asserted with a ceiling so it cannot
    grow unnoticed into something nobody reads."""
    assert 700 < len(COPY) < 1400, (
        f"the copy is {len(COPY)} characters. It is long by design (the full ladder avoids "
        f"band selection), but past ~1400 it stops being read at all, and under ~700 it has "
        f"probably lost bands — check which.")
