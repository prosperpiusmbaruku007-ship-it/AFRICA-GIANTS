# -*- coding: utf-8 -*-
"""Rent withholding: the rate, the extractors, and REACHABILITY from natural phrasing.

R31's whole lesson is that a unit test calling the engine function directly, with the signal
already supplied as a keyword argument, proves the BRANCH is correct and cannot prove it is
REACHABLE. Three engines in this project passed such tests while being unreachable from a
real message. So the reachability tests here go through `routing.detect_intent` on verbatim
question strings and never touch the engine function directly.
"""

import json
import os

import pytest

from chike import routing
from chike.rules_engine import rent_wht_statement
from chike.rules_engine.rent_wht import RENT_WHT_RATE_BOTH_RESIDENCIES

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# --- the rate itself -------------------------------------------------------------------

def test_rate_is_ten_percent_for_both_residencies():
    """Cap.332 First Schedule para 4(b)(ii). The non-resident limb is named explicitly and
    given the SAME ten percent; there is no residency split for rent."""
    assert RENT_WHT_RATE_BOTH_RESIDENCIES == 0.10


def test_statement_never_claims_a_fifteen_percent_non_resident_rate():
    """The 16-row corpus defect, pinned. 15% is para 4(b)(iv)'s catch-all for OTHER
    payments, taken instead of the specific rent limb three lines above it."""
    for commercial in (True, False, None):
        w = rent_wht_statement(letting_is_commercial=commercial).working
        assert "asilimia 15" not in w
        assert "15%" not in w


def test_statement_is_a_rate_statement_not_a_computation():
    """R19: the checkable claim is a CONSTANT against the statute, not a derived amount.
    A rent x 10% figure would be indistinguishable from a fabrication whenever the
    withholding-agent precondition is unmet."""
    assert rent_wht_statement().amount is None


def test_statement_states_both_residencies_explicitly():
    w = rent_wht_statement().working
    assert "wakazi" in w and "wasio wakazi" in w
    assert "asilimia 10" in w


# --- the precondition, which is the ext_43 fix -----------------------------------------

def test_withholding_agent_precondition_is_stated_when_unknown():
    """ext_43's defect: a small individual trader was told he must withhold 10%. With no
    agent signal the statement must NOT assert an obligation — it must name the
    precondition."""
    w = rent_wht_statement().working
    assert "wakala wa kuzuia" in w
    assert "Thibitisha na TRA" in w or "thibitisha na TRA" in w


def test_agent_status_is_never_inferred_from_the_question():
    """R31: `payer_is_withholding_agent` has NO extractor, deliberately. If one is ever
    added, this test should be the thing that makes the author justify it."""
    assert not hasattr(routing, "payer_is_withholding_agent")
    assert not any("withholding_agent" in n for n in dir(routing))


# --- REACHABILITY from natural phrasing (the test a unit test cannot provide) ----------

@pytest.mark.parametrize("question", [
    # ext_43 — verbatim from the committed probe file. Never paraphrase (R24/R26).
    "Nina nyumba kijijini nimemkodisha mfanyabiashara mdogo. Yeye anatakiwa kunikata kodi "
    "kabla ya kunilipa kodi ya pango?",
    # ext_44 — verbatim, second phrasing.
    "Nikimlipa mwenye nyumba kodi ya pango ofisini, ni lazima nikate kodi kabla ya kumpa "
    "fedha?",
])
def test_natural_phrasing_reaches_the_rent_wht_route(question):
    """No technical term, no keyword argument — only the sentence a real person types."""
    assert routing.detect_intent(question) == "rent_wht"


def test_eval_258_must_not_route_to_rent_wht():
    """THE PIN. eval_258 contains `kodi ya pango` AND a commercial cue (`ofisi`) and is an
    SDL question whose correct answer is that rent does NOT enter the SDL base. Diverting it
    would be a confident, well-cited answer to the WRONG topic — the eval_211 harm class,
    and the reason the route requires a withholding term as well as a rent term."""
    q = ("Nalipa kodi ya pango TZS 850,000 kwa mwezi kwa ofisi, hii inaingia kwenye hesabu "
         "ya SDL?")
    assert routing.detect_intent(q) != "rent_wht"


def test_eval_258_is_still_the_question_this_pin_describes():
    """The pin above hard-codes eval_258's text. If the corpus row changes, the pin is
    asserting something about a question that no longer exists — the stale-pin failure mode
    (R18 incident 1), which is closed by re-checking the CONTENT every run, not the id."""
    path = os.path.join(REPO, "eval", "accuracy_gate", "eval_questions_003.jsonl")
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    row = next((r for r in rows if r.get("id") == "eval_258"), None)
    assert row is not None, "eval_258 has left the corpus; the routing pin is now unanchored"
    assert "kodi ya pango" in row["question_sw"]
    assert "SDL" in row["question_sw"]


# --- the commercial extractor ----------------------------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("Nikimlipa mwenye nyumba kodi ya pango ofisini, ni lazima nikate kodi?", True),
    ("Nalipa pango la duka langu, nikate kodi?", True),
    ("Pango la nyumba ya kuishi, nikate kodi ya zuio?", False),
    # BOTH families present -> None. ext_43 is a residential house let to a trader, which is
    # exactly what the TRA table's "For commercial purposes" wording does not settle.
    ("Nina nyumba kijijini nimemkodisha mfanyabiashara mdogo. Yeye anatakiwa kunikata kodi "
     "kabla ya kunilipa kodi ya pango?", None),
])
def test_commercial_letting_extractor(text, expected):
    assert routing.rent_letting_is_commercial(text) is expected


def test_unknown_commercial_status_still_answers_with_the_rate():
    """None must not degrade into a refusal — the rate is the same either way; only the
    qualifier changes. A withheld correct answer is the failure we cannot see."""
    r = rent_wht_statement(letting_is_commercial=None)
    assert "asilimia 10" in r.working
    assert r.applicable is True


# --- FULL-PIPELINE REACHABILITY (2026-09-29) -------------------------------------------
#
# The tests above go through detect_intent on verbatim strings, which is already stronger
# than calling the engine directly — and it was still not enough. detect_intent is ONE step
# of the path; this parametrization runs the fixture from the raw message through
# decomposition, routing AND the engine to the reply text, which is what
# eval/routing/probe_rent_wht_pipeline.py measures. Wired here so a regression fails in the
# normal suite rather than waiting for someone to remember the script (R26: a control nobody
# calls is inert however correct it is).

_PIPELINE_PROBES = [
    json.loads(l) for l in open(
        os.path.join(REPO, "eval", "routing", "rent_wht_pipeline_probes.jsonl"),
        encoding="utf-8") if l.strip()
]


def test_pipeline_probe_fixture_is_populated_and_two_armed():
    """R20: a fixture that cannot exercise the category it claims to watch is clean by
    construction. Both arms must be non-empty — a must-route-only set certifies a cue that
    matches everything, and that is precisely how the `mkate` collision would have shipped."""
    assert len(_PIPELINE_PROBES) >= 10
    must_route = [r for r in _PIPELINE_PROBES if r["expect"] == "rent_wht"]
    must_not = [r for r in _PIPELINE_PROBES if r["expect"] != "rent_wht"]
    assert len(must_route) >= 5, "no reachability arm"
    assert len(must_not) >= 4, "no collision arm — the half that does the work"
    natural = [r for r in must_route if r["arm"] == "natural_no_formal_term"]
    assert len(natural) >= 5, "the arm that was 0/5 before the fix must stay populated"


@pytest.mark.parametrize("row", _PIPELINE_PROBES, ids=lambda r: r["id"])
def test_rent_wht_full_pipeline(row):
    from eval.routing.probe_rent_wht_pipeline import check
    result = check(row)
    assert result["ok"], (
        f"{row['id']} ({row['arm']}): expected {row['expect']}, "
        f"routed {result['routes']}. {row['guards_against']}")


def test_no_reply_ever_states_fifteen_percent():
    """R23 — the value the system would not produce by default. 15% is the corpus's error
    (16 rows quarantined 2026-09-26) and is what reappears if anyone adds the deliberately
    absent `is_resident` parameter. Asserted across every probe, both arms."""
    from eval.routing.probe_rent_wht_pipeline import check
    for row in _PIPELINE_PROBES:
        assert not check(row)["reply_contains_forbidden_15pct"], row["id"]
