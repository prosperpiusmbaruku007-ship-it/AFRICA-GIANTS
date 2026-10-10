"""D-FIDELITY-9 — a money figure nothing in the exchange can support.

⛔ THE RULE THAT WAS **NOT** BUILT IS THE POINT OF THIS FILE. The obvious form — flag any money
figure in the body that is absent from the engine's working — was priced first over every
stored reply this project holds, and it is **1/14 precise**. It deletes `eval_092`'s per-head
breakdown and `eval_395`'s NET PAY, the latter being the exact quantity its question asked for
and one the working structurally cannot contain. Wiring it would be D-FIDELITY-7's
gold-destruction shape repeated knowingly.

The adjudication produced the discriminator and it is R19's line: all 13 false positives derive
from a figure THE QUESTION SUPPLIED. `th_22` — the one true positive, live, judged CORRECT 5/5
— differs in that its question supplies none, so no lawful transformation of the user's numbers
reaches TZS 50,000 because there are no numbers. A CONSTANT comparison, not a derived one.

R17 in full: the probes live in eval/fidelity/unsupported_figure_probes.jsonl, both directions,
and **eight of the eleven are `clean`** — the arm that does the work. The flag-expecting probes
passed the loose rule too; only the clean ones separate the two rules.
"""
import io
import json
import os

import pytest

from chike import fidelity
from chike.model_abstraction import FakeBackend
from chike.orchestrator import Orchestrator

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBES = os.path.join(REPO, "eval", "fidelity", "unsupported_figure_probes.jsonl")


def _probes():
    with io.open(PROBES, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


ALL = _probes()


def test_the_probe_set_is_not_one_sided():
    """R33: a probe set authored by whoever wrote the rule will agree with it. The only arm
    that can disagree is the CLEAN one, so it must dominate — the flag arm passed the loose
    rule too and therefore distinguishes nothing."""
    clean = [p for p in ALL if p["expect"] == "clean"]
    flag = [p for p in ALL if p["expect"] == "flag"]
    cost = [p for p in ALL if p["expect"] == "flag_but_correct"]
    assert len(flag) >= 3, "the rule must still be shown to fire"
    assert len(clean) > len(flag), (
        f"{len(clean)} clean vs {len(flag)} flag — the set has drifted toward confirming the "
        f"rule, which is the composition R33 warns produces a green suite over an open gap")
    assert cost, (
        "the set has lost its `flag_but_correct` arm. That arm is the only place the rule's "
        "COST is recorded as a test rather than as prose, and it is what keeps the fact-path "
        "hold evidenced")
    assert {"clean", "flag", "flag_but_correct"} >= {p["expect"] for p in ALL}
    assert all(p.get("guards_against", "").strip() for p in ALL), (
        "every probe states what it guards against, or a later reader cannot tell a measured "
        "specimen from a guess")


@pytest.mark.parametrize("probe", ALL, ids=[p["id"] for p in ALL])
def test_every_probe_behaves_as_recorded(probe):
    hits = fidelity.unsupported_body_figures(
        probe["question_sw"], probe["body_sw"], probe["working_sw"])
    if probe["expect"] in ("flag", "flag_but_correct"):
        assert hits, (f"{probe['id']} must flag and did not — {probe['guards_against'][:140]}")
    else:
        assert not hits, (
            f"{probe['id']} was flagged and must not be: {hits}. "
            f"{probe['guards_against'][:200]}")


def test_the_FOUNDING_SPECIMEN_is_the_real_live_reply_and_still_fires():
    """R26: plant the exact thing the rule exists to catch, read out of the committed artifact
    rather than retyped, and watch it block. A clean sweep from an inert rule is byte-identical
    to a clean sweep from a sound one."""
    art = json.load(io.open(os.path.join(
        REPO, "eval", "results", "targeted_route_verification_2026_10_09.json"),
        encoding="utf-8"))
    row = next(r for r in art["rows"] if r.get("id") == "th_22")
    live = row["reply"]
    assert "TZS 50,000" in live, (
        f"the artifact's th_22 reply no longer contains the fabrication, so this test is "
        f"pinned to the wrong specimen: {live!r}")
    assert row["judge"]["verdict"] == "correct", (
        "the judge no longer credits this fabrication. That is good news and it also removes "
        "this test's whole argument — re-read it rather than deleting the assertion")
    body = live.split("\n")[0]
    working = live.split("\n", 1)[1]
    assert fidelity.unsupported_body_figures(row["question"], body, working)


def test_the_LOOSE_rule_would_have_destroyed_two_correct_answers():
    """⛔ THE MEASUREMENT, AS A STANDING ASSERTION. If this ever stops holding, the narrowing's
    justification has changed and the scoping must be re-read before the rule is widened."""
    loose = []
    for probe in ALL:
        if probe["expect"] != "clean" or not probe["working_sw"]:
            continue
        body_f = fidelity._figures(probe["body_sw"])
        work_f = fidelity._figures(probe["working_sw"])
        if body_f - work_f:
            loose.append(probe["id"])
    assert "ufp_02" in loose and "ufp_03" in loose, (
        f"the loose rule no longer flags the per-head breakdown and the net-pay answer "
        f"({loose}), so the 1/14 precision figure this narrowing rests on needs re-measuring")
    for pid in ("ufp_02", "ufp_03"):
        p = next(x for x in ALL if x["id"] == pid)
        assert not fidelity.unsupported_body_figures(
            p["question_sw"], p["body_sw"], p["working_sw"]), (
            f"{pid} is flagged by the NARROWED rule too — the discriminator has stopped "
            f"discriminating")


def test_the_rule_stands_down_entirely_when_the_question_carries_a_figure():
    """The gate, asserted as an outcome rather than as a precondition: the same body that
    flags on a figure-free question must go clean the moment the question supplies one."""
    body = "WCF yako ni TZS 50,000 kwa mwaka."
    working = "Ndiyo. WCF inahusu waajiri wote kutoka mfanyakazi wa kwanza."
    assert fidelity.unsupported_body_figures("Je, nalipa WCF?", body, working)
    assert not fidelity.unsupported_body_figures(
        "Mishahara yangu ni TZS 9,000,000 — je nalipa WCF?", body, working)


def test_BOTH_notations_are_the_same_claim():
    """R36: a sweep keyed on digits is blind to the words by construction, and this corpus
    writes money both ways in one file."""
    working = "Ndiyo. WCF inahusu waajiri wote."
    for body in ("WCF ni TZS 1,000,000 kwa mwaka.", "WCF ni milioni 1 kwa mwaka.",
                 "WCF ni elfu 500 kwa mwaka."):
        assert fidelity.unsupported_body_figures("Je, nalipa WCF?", body, working), body


def test_a_rate_is_not_a_money_claim():
    """If percentages crossed the money floor the rule would blank nearly every correct
    applicability answer, which is the failure mode that looks like the guard working."""
    assert fidelity._figures("asilimia 0.5 na asilimia 20 na 3.5%") == set()
    assert fidelity._figures("mwaka 2026, wafanyakazi 10, tarehe 7") == set()


def test_the_guard_is_WIRED_on_the_compute_path_and_NOT_on_the_fact_path():
    """⛔ R26's wiring limb. Both inert controls of 2026-08-24 had perfect logic and were
    reached by nothing, and the question that finds them is 'what does the deployed path call',
    not 'does the rule work'. Driven end to end through the real orchestrator."""
    fake = FakeBackend(
        scripted_reply="Ndiyo, WCF inakuhusu. Kwa mfanyakazi mmoja ni TZS 50,000 kwa mwaka.")
    orch = Orchestrator(backend=fake, retriever=lambda _q: [])
    reply = orch.answer("Nina mfanyakazi mmoja tu — je nalipa WCF?")
    assert "50,000" not in reply.text, (
        f"the fabricated figure survived the compute path: {reply.text!r}")
    assert "WCF inahusu waajiri wote" in reply.text, (
        f"the engine's working must still render — blanking the body may never ship silence "
        f"where a working exists: {reply.text!r}")
    assert fake.call_count == 1, "the model was in the loop, so this exercised the real path"


def test_the_FACT_path_is_deliberately_untouched_and_the_probe_says_why():
    """ufp_11 is a CORRECT locked constant (the GN 605A minimum wage) on a figure-free
    question, with no working — exactly what this rule would destroy on the fact path, where
    blanking returns an empty reply. It is the measured reason the widening is HELD rather than
    merely unbuilt, so the hold has a specimen and not just a date."""
    p = next(x for x in ALL if x["id"] == "ufp_11")
    assert p["expect"] == "flag_but_correct"
    assert p["working_sw"] == "", "ufp_11's whole point is that there is no working"
    # The rule DOES fire on it. Only the orchestrator's compute-path gating keeps that
    # firing away from a correct answer, which is the whole content of the hold.
    assert fidelity.unsupported_body_figures(p["question_sw"], p["body_sw"], ""), (
        "ufp_11 no longer demonstrates the fact-path cost, so the hold has lost its evidence")
    # And end to end the fact path is untouched: the body survives intact.
    fake = FakeBackend(scripted_reply=p["body_sw"])
    reply = Orchestrator(backend=fake, retriever=lambda _q: []).answer(p["question_sw"])
    assert "358,322" in reply.text, (
        f"a correct locked constant was removed from a FACT-path answer — D-FIDELITY-9 has "
        f"leaked off the compute path: {reply.text!r}")


def test_the_scoping_artifact_records_the_pricing_this_rule_rests_on():
    """R18: the claim and its evidence one lookup apart, and the gold arm is the blocking one —
    D-FIDELITY-7's pricing pass found three golds the unnarrowed rule would have destroyed."""
    a = json.load(io.open(os.path.join(
        REPO, "eval", "results", "render_disagreement_scoping_2026_10_10.json"),
        encoding="utf-8"))
    assert a["detector_orphan_figure_flags"] == 14
    assert a["detector_unsupported_figure_flags"] == 1
    assert a["gold_answers_flagged"] == 0, (
        f"the narrowed rule now flags {a['gold_answers_flagged']} GOLD answer(s). A guard that "
        f"destroys a human-asserted-correct answer is not ready at any precision — unwire it "
        f"and re-narrow before touching this test")
    assert a["gold_answers_checked_with_a_working"] >= 50
