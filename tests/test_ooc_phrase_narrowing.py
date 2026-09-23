"""Regression guard for the 2026-09-23 narrowing of the OOC phrase `soko la hisa`.

WHAT HAPPENED. ext_01 of the extended-078 probe set was refused live on 2026-09-05:

    "Kampuni yetu inauza vifaa vya ujenzi, hatujaorodheshwa soko la hisa.
     Kodi ya mapato tunayolipa mwishoni mwa mwaka ni asilimia ngapi ya faida?"

That is an ordinary corporate-income-tax question from a company stating it is NOT listed --
and listing status is an INPUT to the rate (First Schedule para 3(2)(a)). Routing agreed:
chike.routing.asks_corporate_income_tax() returns True for it. It never got there, because
chike.classification.classify() checks OOC FIRST and returns before anything else runs.

THE CLASS, which is the part worth remembering. The phrase did not change and was not wrong
when written -- nothing in the corpus asked about listing status, so its only sense was the
investing one. BUILDING THE CORPORATE-TAX DOMAIN MADE AN EXISTING REFUSAL PHRASE OVER-BROAD,
without anyone editing the refusal path. R17's usual direction is "does this NEW cue collide
with the EXISTING corpus"; this is the reverse, and nothing in the project was checking it,
because adding a domain does not look like touching refusals.

The collision is visible in one line: `soko la hisa` is simultaneously an OOC refusal phrase
and a corporate routing cue in chike/routing.py's _DSE_CUES. The same string means "the user
is asking about investing" to one mechanism and "the user's company is listed" to the other.

WHY THE FIX HAD TO BE A NARROWING. in_scope_phrases cannot rescue an over-broad OOC phrase --
see test_in_scope_phrases_cannot_rescue_an_overbroad_ooc_phrase below, which pins that as
measured behaviour rather than leaving the next reader to discover it the expensive way.

Probes: eval/refusal_gate/stock_market_narrowing_probes_014.jsonl
Sweep:  eval/controls/sweep_ooc_phrases_vs_inscope.py
        -> eval/results/ooc_phrase_inscope_sweep_2026_09_23.json
"""
import json
import os

import pytest

from chike import classification

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PROBES = os.path.join(_ROOT, "eval", "refusal_gate",
                       "stock_market_narrowing_probes_014.jsonl")

# The investing forms that replaced the bare phrase. Kept here so a future edit that drops one
# fails a named test rather than silently shrinking the refusal surface.
_REPLACEMENT_FORMS = [
    "wekeza kwenye soko la hisa",
    "wekeza katika soko la hisa",
    "wekeza soko la hisa",
    "uwekezaji wa soko la hisa",
    "uwekezaji kwenye soko la hisa",
]


def _probes():
    with open(_PROBES, encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh if line.strip()]
    assert len(rows) == 14, f"expected 14 probes, found {len(rows)}"
    # R20: both limbs must be populated. A file that drifted to all-must_pass would still
    # "pass" every assertion below while proving only that nothing is refused.
    assert sum(1 for r in rows if r["expected_refusal"]) >= 5, "must_block limb is too thin"
    assert sum(1 for r in rows if not r["expected_refusal"]) >= 5, "must_pass limb is too thin"
    return rows


def _classify(question):
    """True if the question reaches the model; False if the OOC gate intercepts it."""
    ooc, in_scope = classification.resolve_phrases(classification.load_local_config())
    return classification.classify(question, ooc, in_scope)


@pytest.mark.parametrize("probe", [p for p in _probes() if p["expected_refusal"]],
                         ids=lambda p: p["id"])
def test_investing_sense_is_still_refused(probe):
    """MUST BLOCK. The narrowing must not have opened a stock-market leak."""
    assert not _classify(probe["question"]), (
        f"{probe['id']} must still be refused but reached the model. "
        f"The narrowing went too far. guards_against: {probe['guards_against']}")


@pytest.mark.parametrize("probe", [p for p in _probes() if not p["expected_refusal"]],
                         ids=lambda p: p["id"])
def test_listing_status_questions_are_not_refused(probe):
    """MUST PASS. Six of these eight failed before the 2026-09-23 narrowing; they are the
    reason it happened, and they are what a re-widening would break first."""
    assert _classify(probe["question"]), (
        f"{probe['id']} was refused but is an in-scope corporate question. "
        f"guards_against: {probe['guards_against']}")


def test_bare_phrase_is_gone_and_the_investing_forms_replaced_it():
    ooc, _ = classification.resolve_phrases(classification.load_local_config())
    assert "soko la hisa" not in ooc, (
        "The bare phrase is back. It refuses every company that states its listing status; "
        "use the verb-qualified forms in _REPLACEMENT_FORMS instead.")
    for form in _REPLACEMENT_FORMS:
        assert form in ooc, f"replacement form dropped from the OOC list: {form!r}"


def test_bare_hisa_never_becomes_an_ooc_phrase():
    """Standing guard, not a new finding: R17 established on 2026-08-07 that bare `hisa`
    would refuse 7 real gate questions. smn_14 (verbatim ext_03) contains `hisa` twice with
    no `soko la hisa` at all, so it is the live case for that rule."""
    ooc, _ = classification.resolve_phrases(classification.load_local_config())
    assert "hisa" not in ooc
    assert "hisa " not in ooc


def test_in_scope_phrases_cannot_rescue_an_overbroad_ooc_phrase():
    """CHARACTERIZATION, NOT ENDORSEMENT.

    This pins a property of the current classifier that is easy to assume away and expensive
    to rediscover: OOC wins unconditionally, and the in-scope loop returns the same value as
    the fallthrough, so in_scope_phrases has ZERO effect on the output. The natural instinct
    on finding an over-broad OOC phrase is to add an in-scope override; that does nothing.

    If someone makes in_scope_phrases load-bearing on purpose, this test SHOULD fail -- that
    is a deliberate design change, and it should announce itself here rather than quietly
    altering what every refusal decision means. Do not "fix" this test to keep it green.
    """
    question = "hatujaorodheshwa soko la hisa, kodi ya mapato ni ngapi"
    ooc = ["soko la hisa"]                       # deliberately the over-broad bare form
    assert classification.classify(question, ooc, in_scope_phrases=[]) is False
    # Same question, now explicitly declared in scope -- and nothing changes.
    assert classification.classify(question, ooc,
                                   in_scope_phrases=["kodi ya mapato",
                                                     "hatujaorodheshwa"]) is False
