# -*- coding: utf-8 -*-
"""D-FIDELITY-7 IS WIRED — watched blocking, and watched NOT blocking (R26, both directions).

THE HOLD LAPSED RATHER THAN WAS DECIDED, and that is why this file exists.

`eval/results/control_fire_audit.json` recorded the guard as `NOT_WIRED` on 2026-08-24 with the
note *"Held for one R16 cycle by decision — but note eval_208 shows the exact defect it targets,
LIVE."* One cycle. It was never revisited. Six weeks later, on 2026-10-06, `eval_347` showed the
same defect live again — a fabricated TZS 11,000,000 EFD threshold, with the corrected index row
at rank 1 for both phrasings, i.e. with no index-side headroom left to take.

A hold with no expiry is a decision nobody is making. It does not get re-opened, because nothing
about it comes due. The structural half of this lesson is in `tests/test_control_fire_audit.py`:
any control recorded as held must carry an expiry date, and the audit fails once it passes.

R26's test, applied here:
  1. PLANT the exact thing it exists to catch — on BOTH paths, which behave differently.
  2. GIVE IT A CLEAN CASE — including the three GOLD answers the unnarrowed rule would have
     destroyed. Positive-only certifies a control that blocks everything.
  3. ASSERT BOTH, in a committed test, so the demonstration survives the session.

THE PATH ASYMMETRY IS THE WHOLE DESIGN and it is what makes this wiring different from
D-FIDELITY-6's. On the compute path the body is BLANKED, because `_render` still emits the
engine's authoritative working. On the fact path `_render` returns the body alone, so blanking
would return an EMPTY REPLY — GUARD A's note governs, silence is worse than a wrong answer — and
the body is REPLACED with copy that states no figure at all.
"""
import json
import os

import pytest

from chike import clarification, fidelity, orchestrator

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The live reply, 2026-10-06, verbatim from the committed verification artifact rather than from
# memory (R24 — provenance named, not recalled).
LIVE_WRONG_FACT_REPLY = (
    "Hapana. Kizingiti cha kuanza kutumia EFD ni mauzo ya TZS 11,000,000 (TZS 10M +). "
    "Si TZS 200,000,000. Thibitisha na TRA (tra.go.tz)."
)
LIVE_ARTIFACT = "eval/results/row57_deploy_verification_2026_10_06.json"


def _sub(text, computation=None):
    sq = orchestrator.SubQuestion(text="Kizingiti cha EFD ni kiasi gani?",
                                  kind="compute" if computation else "fact")
    return orchestrator.SubAnswer(sub_question=sq, text=text, computation=computation)


def _clean(sub):
    """Run the real production stage. `Orchestrator._validate_and_clean` is an instance method
    that touches only `self.stop_strings`, so a bare object with that attribute is enough — and
    calling the REAL method is the point: a reimplementation would test the reimplementation."""
    class _Stub:
        stop_strings = ()
    return orchestrator.Orchestrator._validate_and_clean(_Stub(), sub)


# --- the live reply is in the committed artifact, not reconstructed from memory ---------------

def test_the_planted_reply_is_the_one_production_actually_served():
    """R24: a specimen quoted from memory is a specimen nobody can check. This asserts the exact
    string is in the committed verification artifact, so if the artifact is ever re-run and the
    reply changes, this test says so rather than silently guarding a historical string."""
    path = os.path.join(REPO, *LIVE_ARTIFACT.split("/"))
    blob = json.load(open(path, encoding="utf-8"))
    replies = [r.get("reply", "") for r in blob["rows"]]
    assert any(LIVE_WRONG_FACT_REPLY.split("(TZS 10M +)")[0].strip() in r for r in replies), (
        f"the planted live reply is not in {LIVE_ARTIFACT}. Re-read the artifact before changing "
        f"this test: the specimen, not the guard, is the first thing to suspect (R26).")


# --- 1. IT MUST BLOCK, on both paths ---------------------------------------------------------

def test_the_fact_path_REPLACES_the_wrong_threshold_body():
    out = _clean(_sub(LIVE_WRONG_FACT_REPLY))
    assert out.needs_clarification, "the fact path did not intervene at all"
    assert out.text, "a fact answer was BLANKED — _render would emit nothing and silence ships"
    assert "11,000,000" not in out.text and "11M" not in out.text, (
        f"the replacement copy still carries the fabricated figure: {out.text!r}")
    assert out.raw_text == LIVE_WRONG_FACT_REPLY, "raw_text must preserve the generation"


def test_the_replacement_copy_states_no_figure_at_all():
    """Following a caught fabrication with a different number from the same generation is a
    second guess, not a correction.

    ⚠️ STILL TRUE AFTER THE 2026-10-09 RULE ADDITION, and that is the point of keeping it: for
    EFD the copy now STATES THE STATUTORY POSITION — that no threshold exists — which is the
    ABSENCE of a figure, not a different one. If this test ever fails on `efd`, someone has put
    a number back into the one copy that fires on a fabricated number."""
    import re
    for subject in ("efd", "vat_registration", "presumptive", "unknown_subject"):
        copy = clarification.wrong_threshold_withheld(subject)
        assert not re.search(r"\d{1,3}(?:,\d{3})+|\bmilioni\b|\bTZS\s*\d", copy), (
            f"{subject}: replacement copy contains a figure: {copy!r}")
        assert "tra.go.tz" in copy, f"{subject}: copy does not point at the authority"


def test_the_copy_does_NOT_apologise_for_a_reply_the_user_never_SAW():
    """⛔ THE SAME CONTRACT AS `wrong_fee_band_withheld`, APPLIED HERE 2026-10-09 AFTER eval_347
    SERVED THE APOLOGY LIVE IN THE FULL GATE.

    On the fact path the guard REPLACES the body before `_render` returns, so the user never
    received the original. "Samahani — jibu langu la awali lilitoa kiwango..." therefore
    apologises for a reply they never saw and reads as though something went wrong that they
    should worry about — anxiety manufactured about an error the system successfully prevented.

    The earlier note recorded this as a DELIBERATE divergence between the two guards
    ("D-FIDELITY-7 fires where there is no rule to state, so withdrawal is the whole of its
    message"). That was wrong: the reasoning is a property of the FACT PATH, which both guards
    share, so it was never a legitimate difference. Pinned for every subject, not just efd."""
    for subject in ("efd", "vat_registration", "presumptive", "unknown_subject"):
        copy = clarification.wrong_threshold_withheld(subject)
        for apology in ("Samahani", "samahani", "jibu langu la awali", "Pole", "pole kwa"):
            assert apology not in copy, (
                f"{subject}: the copy apologises ({apology!r}) for a reply the guard replaced "
                f"before the user could see it: {copy!r}")


def test_efd_STATES_THE_RULE_while_a_real_threshold_subject_only_withholds():
    """⛔ A2 WORK, AND THE PER-SUBJECT SPLIT IS THE WHOLE SAFETY OF IT.

    D-FIDELITY-7 turned eval_347's fabricated threshold into a non-answer — the safe direction,
    still a gate miss, because the user did not get their answer. For EFD the answer is
    available and is not a second guess: s.44(1) makes EFD the default regardless of turnover,
    which index row 57 already serves.

    But `vat_registration` and `presumptive` HAVE statutory thresholds, so a generic "there is
    no threshold" sentence would be a worse defect than the apology it replaced. The rule table
    is therefore per-subject, and this test is what stops it being generalised."""
    efd = clarification.wrong_threshold_withheld("efd")
    assert "haina kizingiti" in efd, (
        "the EFD copy no longer states that no threshold exists — it is back to withholding "
        "only, which leaves eval_347's answer owed")
    assert "Kamishna Mkuu" in efd, "the only route to an exemption is no longer named"
    for subject in ("vat_registration", "presumptive"):
        copy = clarification.wrong_threshold_withheld(subject)
        assert "haina kizingiti" not in copy, (
            f"{subject} HAS a statutory threshold, and this copy now claims there is none — "
            f"the rule table has been generalised past its evidence")
        assert "siwezi kuthibitisha" in copy.lower(), (
            f"{subject}: the withhold-only form has lost its own opening")


def test_the_compute_path_BLANKS_rather_than_replaces():
    """On the compute path the engine's working still renders, so losing the sentence costs the
    user nothing. Blanking and replacing are not interchangeable and the branch must pick right."""
    from decimal import Decimal

    from chike.rules_engine.sdl import compute_sdl
    result = compute_sdl(Decimal("15000000"), 25)
    out = _clean(_sub("Kizingiti cha kuanza kutumia EFD ni mauzo ya TZS 11,000,000 kwa mwaka.",
                      computation=result))
    assert out.text == "", "the compute path should blank a flagged body"
    assert not out.needs_clarification, "the compute path must not route to clarification copy"


def test_the_guard_is_reachable_from_the_production_call_site():
    """⛔ NOT_WIRED IS THE DEFECT THIS FILE CLOSES, so the wiring itself is asserted — by reading
    the deployed method's source for CODE, the way the 2026-08-24 audit learned to: three of its
    own checks matched the COMMENT explaining why a defect had been removed."""
    import inspect
    src = inspect.getsource(orchestrator.Orchestrator._validate_and_clean)
    code = "\n".join(line.split("#", 1)[0] for line in src.splitlines())
    assert "fidelity.body_states_wrong_threshold(cleaned)" in code, (
        "D-FIDELITY-7 is not called from the orchestrator. It was NOT_WIRED from 2026-08-23 to "
        "2026-10-06 on a hold that was meant to last one R16 cycle.")
    assert code.count("fidelity.body_states_wrong_threshold(cleaned)") >= 2, (
        "only one path calls the guard. Both are needed and they do different things: the "
        "compute path blanks, the fact path replaces (blanking a fact answer ships silence).")
    assert "clarification.wrong_threshold_withheld" in code, (
        "the fact path has no replacement copy, so it is blanking — which returns an empty reply")


# --- 2. AND IT MUST NOT BLOCK CORRECT ANSWERS ------------------------------------------------
#
# These three are the reason the guard was NARROWED before wiring. Unnarrowed, it flagged all of
# them, and on the fact path a flag on a gold answer means an EMPTY REPLY to a question whose
# correct answer we hold. eval_347 is the row the wiring exists for.

def _gold(qid):
    path = os.path.join(REPO, "eval", "accuracy_gate", "eval_questions_003.jsonl")
    for line in open(path, encoding="utf-8"):
        obj = json.loads(line)
        if obj["id"] == qid:
            return obj["correct_answer_sw"]
    raise AssertionError(f"{qid} not in eval_questions_003.jsonl — re-point this specimen")


@pytest.mark.parametrize("qid", ["eval_347", "eval_355", "eval_331"])
def test_a_gold_answer_passes_through_the_production_stage_untouched(qid):
    gold = _gold(qid)
    assert not fidelity.body_states_wrong_threshold(gold), (
        f"{qid}'s GOLD answer is flagged: {fidelity.stated_wrong_thresholds(gold)}")
    out = _clean(_sub(gold))
    assert not out.needs_clarification, f"{qid}: a correct answer was routed to clarification"
    assert out.text.strip(), f"{qid}: a correct answer was blanked"


def test_the_prewiring_measurement_artifact_is_committed_and_shows_zero_gold_flags():
    """R18: the harness and its artifact are committed before the result is cited, and the result
    is cited here rather than only in prose — so the claim and its evidence are one lookup apart.
    """
    path = os.path.join(REPO, "eval", "results",
                        "threshold_guard_prewiring_2026_10_06.json")
    blob = json.load(open(path, encoding="utf-8"))
    t = blob["totals"]
    assert t["rows_swept"] > 5000, "the sweep population shrank; re-read before trusting it"
    assert t["flagged_in_GOLD"] == 0, (
        f"{t['flagged_in_GOLD']} gold answers are flagged — the narrowing regressed. Re-run "
        f"eval/fidelity/price_threshold_guard_before_wiring.py and read the flags individually.")
