"""Tests for chike.fidelity — the D-FIDELITY-1 compute-answer fidelity guard.

Locks the detector's exactness proven in the afef9dd 400 sweep: it flags the 3 real
body-vs-working contradictions (eval_367/371/378) and NONE of the 10 benign breakdown
shapes, and it drives the orchestrator to blank a contradictory body so only the
authoritative working is rendered.
"""
from decimal import Decimal

from chike.fidelity import body_contradicts_working
from chike.rules_engine.results import ComputationResult
from chike.orchestrator import Orchestrator
from chike.model_abstraction import FakeBackend


def _r(computation="sdl", applicable=True, amount=None, working="w"):
    amt = None if amount is None else Decimal(amount)
    return ComputationResult(computation=computation, applicable=applicable,
                             amount=amt, working=working)


# --- Case A: engine gave NO figure (not-applicable) ------------------------

def test_caseA_not_applicable_body_computes_amount_is_contradiction():
    # eval_378: SDL for 8 employees is not applicable, but the body computes 175,000.
    r = _r("sdl", applicable=False, amount=None)
    body = "Kwa hesabu sahihi: SDL = TZS 5,000,000 × 3.5% = TZS 175,000. Thibitisha na TRA."
    assert body_contradicts_working(body, r) is True


def test_caseA_not_applicable_faithful_verdict_is_not_contradiction():
    r = _r("sdl", applicable=False, amount=None)
    body = "SDL haihusiki: una wafanyakazi 8 (chini ya 10). SDL inahusu waajiri wenye wafanyakazi 10 au zaidi."
    assert body_contradicts_working(body, r) is False


def test_caseA_applicability_yes_no_amount_body_asserting_a_figure_is_contradiction():
    # applicable=True but no amount (applicability-yes): the body must not invent a figure.
    r = _r("sdl", applicable=True, amount=None)
    body = "Ndiyo, SDL inatozwa: SDL = TZS 4,000,000 × 3.5% = TZS 140,000."
    assert body_contradicts_working(body, r) is True


def test_caseA_applicability_yes_verdict_only_is_not_contradiction():
    r = _r("sdl", applicable=True, amount=None)
    body = "Ndiyo. Una wafanyakazi 12 (10 au zaidi), hivyo SDL inatozwa — asilimia 3.5 ya mishahara."
    assert body_contradicts_working(body, r) is False


# --- Case B0: within a 0% band ---------------------------------------------

def test_caseB0_zero_amount_faithful_no_paye_is_not_contradiction():
    # eval_377: salary in the 0% band; faithful body asserts no result.
    r = _r("paye", applicable=True, amount=0)
    body = "Kwa mshahara wa TZS 200,000/mwezi, hakuna PAYE inayokatwa. Uko ndani ya Bendi ya 0%."
    assert body_contradicts_working(body, r) is False


def test_caseB0_zero_amount_body_asserting_nonzero_is_contradiction():
    r = _r("paye", applicable=True, amount=0)
    body = "PAYE = TZS 5,000 kwa mwezi."
    assert body_contradicts_working(body, r) is True


# --- Case B: definite positive amount --------------------------------------

def test_caseB_amount_absent_from_body_is_contradiction():
    # eval_367: non-resident PAYE is a flat 750,000, but the body asserts 264,000.
    r = _r("paye", applicable=True, amount=750000)
    body = ("Kwa mfanyakazi asiye mkazi: asilimia 15 inatumika kwenye TZS 1,760,000 "
            "(TZS 5,000,000 − TZS 3,240,000). PAYE = TZS 264,000 (15% × TZS 1,760,000).")
    assert body_contradicts_working(body, r) is True


def test_caseB_amount_present_amid_breakdown_is_not_contradiction():
    # eval_191: band breakdown that still restates the correct 78,000 final.
    r = _r("paye", applicable=True, amount=78000)
    body = ("Kanda 2 (8%): TZS 250,000. Kanda 3 (20%): TZS 240,000. "
            "Jumla ya PAYE = TZS 68,000 + 25% × (TZS 800,000 − TZS 760,000) = TZS 78,000.")
    assert body_contradicts_working(body, r) is False


def test_caseB_net_pay_extra_is_not_contradiction():
    # eval_395: PAYE correct (78,000) plus a derived net-pay figure (722,000) — still faithful.
    r = _r("paye", applicable=True, amount=78000)
    body = ("PAYE = TZS 68,000 + 25% × (TZS 800,000 − TZS 760,000) = TZS 78,000. "
            "Mshahara halisi baada ya PAYE = TZS 800,000 − TZS 78,000 = TZS 722,000.")
    assert body_contradicts_working(body, r) is False


def test_caseB_words_only_body_no_numeric_result_is_not_flagged():
    # Conservative: no asserted '= TZS N' result at all -> never flagged (avoids words-only false-pos).
    r = _r("paye", applicable=True, amount=750000)
    body = "PAYE ya mfanyakazi asiye mkazi ni kiwango tambarare cha asilimia kumi na tano."
    assert body_contradicts_working(body, r) is False


# --- The 10 benign shapes from the sweep must ALL stay unflagged -----------

BENIGN = [
    (_r("nssf", True, 200000), "NSSF ya mwajiri = 10% × TZS 400,000 = TZS 40,000. Jumla ya wafanyakazi 5: = TZS 200,000."),
    (_r("paye", True, 78000),  "Jumla ya PAYE = TZS 68,000 + 25% × (TZS 800,000 − TZS 760,000) = TZS 78,000."),
    (_r("sdl",  True, 192500), "SDL = 3.5% × TZS 5,500,000 = TZS 192,500"),
    (_r("sdl",  False, None),  "SDL haihusiki: una wafanyakazi 8 (chini ya 10)."),
    (_r("nssf", True, 45000),  "NSSF (sehemu ya mfanyakazi) = 10% × TZS 450,000 = TZS 45,000"),
    (_r("paye", True, 128000), "Jumla ya PAYE = TZS 68,000 + 25% × (TZS 1,000,000 − TZS 760,000) = TZS 128,000."),
    (_r("paye", True, 131000), "Hesabu: TZS 128,000 + 30% × (TZS 1,010,000 − TZS 1,000,000) = TZS 131,000."),
    (_r("paye", True, 0),      "Kwa mshahara wa TZS 200,000/mwezi, hakuna PAYE inayokatwa."),
    (_r("nssf", True, 250000), "Sehemu ya mwajiri: TZS 2,500,000 × 10% = TZS 250,000. Sehemu ya mfanyakazi: = TZS 250,000. Jumla: TZS 500,000."),
    (_r("paye", True, 78000),  "Kwa mshahara wa TZS 800,000, PAYE = TZS 68,000 + 25% × (TZS 800,000 − TZS 760,000) = TZS 78,000. Baada ya PAYE = TZS 800,000 − TZS 78,000 = TZS 722,000."),
]


def test_all_ten_benign_breakdowns_are_not_contradictions():
    flagged = [b for (r, b) in BENIGN if body_contradicts_working(b, r)]
    assert flagged == [], flagged


# --- End-to-end: a contradictory compute body is blanked, working rendered alone ---

def test_orchestrator_blanks_contradictory_body_and_renders_working_only():
    # SDL amount asked for 8 employees / TZS 5,000,000 -> engine says NOT APPLICABLE.
    # ONE scripted reply, not two: since the Phase D re-run cycle this question takes the
    # SDL-zero branch, which sits BEFORE slot extraction because a sub-threshold headcount
    # settles the amount without the payroll. So the extraction model call no longer happens
    # here — one fewer call, and the deterministic headcount (sole_headcount) is the only
    # input the branch reads.
    wrong_body = "Kwa hesabu sahihi: SDL = TZS 5,000,000 × 3.5% = TZS 175,000."
    fake = FakeBackend(replies=[wrong_body])
    orch = Orchestrator(backend=fake)

    reply = orch.answer("Kampuni ina wafanyakazi 8 wenye mishahara TZS 5,000,000 — SDL inayolipwa ni ngapi?")

    assert "175,000" not in reply.text                 # the wrong figure is gone
    # Authoritative working is what's shown. This question now takes the SDL-zero branch
    # added in the Phase D re-run cycle, which keeps the model in the loop — so this also
    # pins that the fidelity guard still blanks a contradictory body on that path.
    assert "TZS 0" in reply.text and "chini ya 10" in reply.text
    assert reply.sub_answers[0].raw_text == wrong_body  # raw generation preserved for offline rescore


def test_orchestrator_keeps_a_faithful_compute_body():
    # 15 employees / TZS 6,750,000 -> SDL applies = 236,250; a faithful body is NOT blanked.
    extraction = ('{"gross_monthly_payroll": {"value": 6750000, "confidence": "high"}, '
                  '"employee_count": {"value": 15, "confidence": "high"}}')
    good_body = "Hii ndio hesabu yako: SDL = 3.5% × TZS 6,750,000 = TZS 236,250."
    fake = FakeBackend(replies=[extraction, good_body])
    orch = Orchestrator(backend=fake)

    reply = orch.answer("SDL kwa wafanyakazi 15 wenye jumla ya mshahara 6,750,000 ni ngapi?")

    assert "236,250" in reply.text
    assert reply.sub_answers[0].text == good_body       # faithful body retained
