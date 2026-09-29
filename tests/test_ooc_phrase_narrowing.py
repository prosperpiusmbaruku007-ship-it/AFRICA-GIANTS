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


# --- mining-royalty narrowing (2026-09-29) ---------------------------------------------
#
# Same shape as the `soko la hisa` narrowing above: a bare OOC phrase refusing questions the
# system holds the answer to. `mrabaha` is royalty, but only MINING royalty is out of scope --
# `royalties_wht_rate` is a locked fact at 15% default / 10% film / 5% approved sports bodies.
# Replaced by the OOC_CONJUNCTIONS `mining_royalty` rule rather than deleted, because the one
# genuinely-OOC corpus row states its limbs non-adjacently ("Shirika la madini linanipa
# mrabaha") and no substring phrase reaches it.

_MRN_PROBES = [
    json.loads(l) for l in open(
        os.path.join(_ROOT, "eval", "refusal_gate",
                     "mining_royalty_narrowing_probes_010.jsonl"), encoding="utf-8")
    if l.strip()
]


def test_mining_royalty_probe_fixture_has_all_four_arms():
    """R20: a fixture that cannot exercise a category reports clean by construction. The
    `mining_word_alone_is_not_ooc` arm is the one most likely to be dropped as redundant and
    is the only thing pricing the mining limb -- without it, promoting `madini` to a bare OOC
    phrase would look free."""
    arms = {r["arm"] for r in _MRN_PROBES}
    assert {"false_refusal_closed", "oo_scope_held",
            "pre_existing_refusal_unchanged", "mining_word_alone_is_not_ooc"} <= arms
    for arm in ("false_refusal_closed", "oo_scope_held", "mining_word_alone_is_not_ooc"):
        assert sum(1 for r in _MRN_PROBES if r["arm"] == arm) >= 2, f"{arm} is under-populated"


@pytest.mark.parametrize("row", [r for r in _MRN_PROBES if r["expect"] != "LEAK_KNOWN"],
                         ids=lambda r: r["id"])
def test_mining_royalty_narrowing(row):
    ooc, in_scope = classification.resolve_phrases(classification.load_local_config())
    in_scope_verdict = classification.classify(row["question_sw"], ooc, in_scope)
    expected = row["expect"] == "ANSWER"
    assert in_scope_verdict is expected, (
        f"{row['id']} ({row['arm']}): expected {row['expect']}. {row['guards_against']}")


def test_bare_mrabaha_is_gone_but_the_qualified_forms_remain():
    """The narrowing itself. `mrabaha wa madini` must survive independently of the
    conjunction -- mrn_07 is refused by BOTH mechanisms, so removing either alone must not
    silently drop it."""
    ooc, _ = classification.resolve_phrases(classification.load_local_config())
    assert "mrabaha" not in ooc, "the bare over-broad form is back"
    assert "mrabaha wa madini" in ooc, "the qualified form was removed along with the bare one"


def test_the_conjunction_can_only_narrow_never_widen():
    """THE SAFETY ARGUMENT, asserted rather than left in a comment.

    The standing rule above R17 prices any mechanism that can refuse a user at one frozen
    held-out set, because a wrongly-refused question is invisible. This rule is exempt only
    because every conjunction's first limb is a term that was ALREADY an active bare OOC
    phrase, making the set it refuses a strict subset of what the gate refused before. If a
    future conjunction breaks that property, the exemption no longer applies and this test
    fails -- which is the point.
    """
    removed_bare_phrases = {"mrabaha"}
    for rule in classification.OOC_CONJUNCTIONS:
        limbs = [v for k, v in rule.items() if k != "name"]
        assert any(set(limb) <= removed_bare_phrases for limb in limbs), (
            f"conjunction {rule['name']} has no limb that was previously a bare OOC phrase, "
            "so it can refuse questions the gate did not refuse before. It owes a frozen "
            "held-out set (R21) before it ships.")


def test_known_leak_row_is_recorded_and_still_leaks():
    """oh_09 is in the fixture as LEAK_KNOWN and is NOT asserted as refused. Pinned as still
    leaking so that if some future change happens to close it, this test fails and the row is
    re-adjudicated deliberately rather than the fixture quietly becoming stale."""
    row = next(r for r in _MRN_PROBES if r["expect"] == "LEAK_KNOWN")
    ooc, in_scope = classification.resolve_phrases(classification.load_local_config())
    assert classification.classify(row["question_sw"], ooc, in_scope) is True, (
        "oh_09 no longer leaks -- re-adjudicate the row instead of leaving it marked LEAK_KNOWN")
