# -*- coding: utf-8 -*-
"""D-FIDELITY-8 — THE FEE-BAND GUARD, WIRED 2026-10-08.

THE DEFECT, measured live against the deployed index:

    Q: "Mtaji wa hisa wa kampuni yangu ni TZS 2,000,000,000. Ada ya kusajili ni ngapi?"
    A: "Ada ya kusajili kampuni yenye mtaji wa hisa unaozidi TZS 5,000,000 ni TZS 290,000."

The ladder gives TZS 600,000 for that share capital. The reply returned the >20M-50M band and
misstated its floor as 5,000,000.

WHY ONLY A GUARD REACHES IT: row 181 measured at RANK 1 (0.9167) for that exact query, rank 3
on a paraphrase, rank 1 on the sibling ask. The correct ladder was IN CONTEXT. At rank 1-3
with a wrong answer the defect is in GENERATION (CLAUDE.md step zero), and staleness is ruled
out from inside the live harness — the no-share-capital probe reads the SAME row 181 and
returns the NEW TZS 500,000.

⛔ EVERY SPECIMEN BELOW EXISTS BECAUSE THE FIRST VERSION OF THIS RULE WAS INERT ON ITS OWN
FOUNDING DEFECT. It used a proximity window for the fee cue, reported 0 flags across 13,632
rows, and returned a verdict of "SAFE TO PROPOSE FOR WIRING". A clean sweep from an inert rule
is byte-identical to a clean sweep from a sound one (R39). The replacement separates fee from
band edge GRAMMATICALLY — a fee follows the predicative `ni`, an edge follows a comparative —
and the defective sentence contains both.
"""
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from chike import clarification, fidelity  # noqa: E402

Q2B = "Mtaji wa hisa wa kampuni yangu ni TZS 2,000,000,000. Ada ya kusajili ni ngapi?"

# (id, question, body, must_flag, why)
SPECIMENS = [
    ("the_live_defect", Q2B,
     "Ada ya kusajili kampuni yenye mtaji wa hisa unaozidi TZS 5,000,000 ni TZS 290,000. "
     "Thibitisha na BRELA (brela.go.tz).", True,
     "THE FOUNDING SPECIMEN, verbatim from the 2026-10-08 live run. 290,000 is lawful for "
     "the >20M-50M band and wrong here; the 5,000,000 in the same sentence is a BAND EDGE "
     "and must not be read as the fee. If this ever stops flagging, the guard is inert on "
     "the only defect it was built for — which is the state version 1 shipped in."),
    ("the_correct_answer", Q2B,
     "Ada ya kusajili kwa mtaji wa hisa wa TZS 2,000,000,000 ni TZS 600,000.", False,
     "THE SPECIMEN THAT MATTERS MOST. A guard that replaces the correct answer is worse "
     "than no guard, and this is the fact path, where replacement is the whole mechanism."),
    ("same_fee_its_own_band", "Mtaji wa hisa ni TZS 30,000,000. Ada ni ngapi?",
     "Ada ya kusajili ni TZS 290,000.", False,
     "THE SAME FIGURE, 290,000, now correct because the capital falls in ITS band. This is "
     "what makes it a TABLE guard rather than a value check — and it is why a sweep for the "
     "figure 290,000 would have been useless."),
    ("no_share_capital_untouched",
     "Kampuni yangu haina mtaji wa hisa. Ada ya kusajili ni shilingi ngapi?",
     "Kampuni bila mtaji wa hisa (assetless company) inasajiliwa kwa ada ya TZS 500,000.",
     False,
     "THE SIBLING THE FOUNDER NAMED. This answer was CORRECT in the same live run (500,000, "
     "superseding 300,000) and reads the SAME index row 181. The guard must not touch it — "
     "the question states no share-capital AMOUNT, so there is no band to be wrong about."),
    ("ladder_recital", "Ada ya kusajili kampuni ni ngapi kwa mtaji wa hisa wa TZS 2,000,000,000?",
     "Ngazi za ada: hadi TZS 1,000,000 ni TZS 95,000; zaidi ya TZS 1,000,000 hadi TZS "
     "5,000,000 ni TZS 175,000; zaidi ya TZS 5,000,000 hadi TZS 20,000,000 ni TZS 260,000; "
     "zaidi ya TZS 20,000,000 hadi TZS 50,000,000 ni TZS 290,000; zaidi ya TZS 50,000,000 "
     "hadi TZS 100,000,000 ni TZS 400,000.", False,
     "A body reciting the ladder is answering WITH THE TABLE, not choosing a band, so it has "
     "not committed the defect. Without this exclusion the guard's own replacement copy "
     "would flag itself."),
    ("polarity", Q2B,
     "Ada ni TZS 600,000 — SI TZS 290,000, hiyo ni kwa mtaji mdogo.", False,
     "N4. The correct answer names the wrong value in order to reject it. A presence check "
     "fails exactly the rows that carry the correction — the deleting-direction failure in "
     "reverse (R39)."),
    ("unlawful_figure", Q2B, "Ada ya kusajili ni TZS 777,777.", True,
     "A figure in no band at all. Still a wrong fee for the stated capital, and worth "
     "catching even though it is not a misapplied band."),
    ("band_edge_is_not_a_fee", Q2B,
     "Kampuni yenye mtaji unaozidi TZS 50,000,000 inalipa ada ya usajili. "
     "Ada ni TZS 600,000.", False,
     "N3 both ways in one body: 50,000,000 follows a comparative (edge, ignored) and 600,000 "
     "follows `ni` (fee, correct). Version 1's proximity window could not make this "
     "distinction and that is why it fired on nothing."),
]


@pytest.mark.parametrize("sid,q,body,must_flag,why",
                         SPECIMENS, ids=[s[0] for s in SPECIMENS])
def test_each_specimen_behaves_as_specified(sid, q, body, must_flag, why):
    got = fidelity.stated_wrong_fee_band(q, body)
    if must_flag:
        assert got is not None, f"{sid} MUST flag and did not.\n  {why}"
    else:
        assert got is None, f"{sid} must NOT flag but did ({got}).\n  {why}"


def test_the_specimen_set_covers_both_directions():
    """R26/R39: positive-only certifies a rule that flags everything; negative-only is what
    the secret scan had. Six of the eight here must come back CLEAN, and those are the half
    that does the work."""
    flag = [s for s in SPECIMENS if s[3]]
    clean = [s for s in SPECIMENS if not s[3]]
    assert len(flag) >= 2 and len(clean) >= 5
    for s in SPECIMENS:
        assert len(s[4]) > 90, f"{s[0]} has no stated reason"


@pytest.mark.parametrize("capital,fee", [
    (500_000, 95_000), (1_000_000, 95_000), (1_000_001, 175_000),
    (20_000_000, 260_000), (20_000_001, 290_000), (50_000_000, 290_000),
    (2_000_000_000, 600_000), (10_000_000_000, 600_000), (10_000_000_001, 1_000_000),
])
def test_the_lookup_is_correct_at_every_band_EDGE(capital, fee):
    """⛔ EDGES, NOT MIDPOINTS. The live defect was a band-boundary error, and the ladder was
    RE-SCOPED on 2026-10-06 (five bands with an open top became nine closed ones, so 'band 5'
    stopped meaning 'above TZS 50,000,000'). An off-by-one on an inclusive upper bound is
    exactly the shape that survives midpoint testing."""
    assert fidelity.expected_share_capital_fee(capital) == fee


def test_the_guard_and_the_copy_read_ONE_table():
    """A second copy of a fee table in the guard layer is the dual-file divergence this
    project keeps paying for. `expected_share_capital_fee` must read clarification's tuple,
    which is the same one the replacement copy is generated from."""
    import inspect
    src = inspect.getsource(fidelity.expected_share_capital_fee)
    assert "clarification.BRELA_SHARE_CAPITAL_BANDS" in src, (
        "the guard has its own copy of the ladder; it must read clarification's")
    for _, _, fee in clarification.BRELA_SHARE_CAPITAL_BANDS:
        assert f"{fee:,}" in clarification.wrong_fee_band_withheld()


def test_the_wiring_is_fact_path_and_replaces_rather_than_blanks():
    """R26: where a control ACTS, not whether it works. Two inert controls on 2026-08-24 had
    nothing wrong with their logic — one was handed no files, the other was never imported by
    production."""
    import inspect
    from chike import orchestrator
    src = inspect.getsource(orchestrator)
    assert "body_states_wrong_fee_band" in src, "the guard is not wired into the orchestrator"
    branch = src.split("body_states_wrong_fee_band")[1][:2400]
    assert "wrong_fee_band_withheld" in branch, (
        "the guard fires but does not install the replacement copy — on the fact path that "
        "would blank the reply and ship silence")
    assert "sub.computation is None" in src.split("body_states_wrong_fee_band")[0][-200:], (
        "the guard is not gated on the fact path")
    assert 'cleaned = ""' not in branch.split("return")[0], (
        "the fact-path branch blanks the body; _render returns the body alone here, so that "
        "ships an empty reply")


def test_the_containment_caveat_is_recorded_at_the_site():
    """The founder's instruction: record that it is a containment, same caveat as eval_347. A
    guard stops a wrong answer and never produces the right one, so a falling wrong-answer
    count is not a rising correct-answer count — and that must be readable where the guard is,
    not only in PROGRESS.md, which is where it would decay."""
    import inspect
    from chike import orchestrator
    src = inspect.getsource(orchestrator)
    branch = src.split("body_states_wrong_fee_band")[1][:2400]
    assert "CONTAINMENT" in branch.upper()
    assert "eval_347" in branch, "the caveat does not cite the precedent it shares"
    assert "A2" in branch and "A1" in branch, (
        "the two-bar consequence is not stated: A1 moves, A2 does not")
