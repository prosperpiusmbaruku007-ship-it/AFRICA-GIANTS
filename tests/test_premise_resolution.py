"""THE PREMISE RESOLVER — a class fix, tested as a class rather than row by row.

⛔ EVERY ASSERTION HERE IS AN OUTCOME, NEVER A PRECONDITION. The test this replaces in spirit
is `test_rate_branch_needs_a_figure_to_engage`, whose whole body asserted a property of the
QUESTION (`sole_plausible_amount(...) is None`) — true before the behaviour, true after it,
and therefore green through a deliberate reversal of the behaviour it was named for. So the
rule is: could this assertion still pass if the mechanism were inverted? If yes, it is not a
test of the mechanism.

The specific inversion to defend against is real and was mine: the `inverts` column on the
two IS_VOLUNTARY frames was backwards in the first draft and the table read perfectly fine.
Swapping them answers every compulsion question with the opposite verdict, in the engine's
voice, on the exact axis eval_394 was about — so all eight polarity combinations are pinned
below, by outcome.
"""
import pytest

from chike import routing
from chike.model_abstraction import FakeBackend
from chike.orchestrator import Orchestrator
from chike.rules_engine import premise, results


def _answer(question, body=""):
    fake = FakeBackend(scripted_reply=body)
    reply = Orchestrator(backend=fake, retriever=lambda _q: []).answer(question)
    return reply.text or ""


# ── the polarity table, all eight combinations, by outcome ──────────────────────────────
@pytest.mark.parametrize("question,proposition,asserted", [
    ("Je, NSSF ni ya hiari?", premise.IS_VOLUNTARY, True),
    ("Je, NSSF si ya hiari?", premise.IS_VOLUNTARY, False),
    ("Je, WCF ni lazima?", premise.IS_VOLUNTARY, False),
    ("Je, WCF si lazima?", premise.IS_VOLUNTARY, True),
    ("je ni halali?", premise.WAGE_IS_LAWFUL, True),
    ("je si halali?", premise.WAGE_IS_LAWFUL, False),
    ("nakiuka sheria?", premise.WAGE_IS_LAWFUL, False),
    ("sikiuki sheria?", premise.WAGE_IS_LAWFUL, True),
])
def test_what_each_surface_form_ASSERTS(question, proposition, asserted):
    """⛔ THE TABLE THAT WAS BACKWARDS. `ni ya hiari` (is it voluntary) asserts voluntary=TRUE
    and does NOT invert; `ni lazima` (is it compulsory) asserts voluntary=FALSE and DOES.
    Reading the table cannot distinguish a correct polarity column from a plausible one —
    only asking it what each form means can."""
    p = premise.detect(question)
    assert p is not None, question
    assert (p.proposition, p.asserted_truth) == (proposition, asserted)


def test_the_two_voluntariness_frames_assert_OPPOSITE_things():
    """The invariant that fails loudly if the two rows are ever swapped again, stated without
    naming either column — so it survives a refactor of how `inverts` is represented."""
    assert (premise.detect("Je, NSSF ni ya hiari?").asserted_truth
            is not premise.detect("Je, NSSF ni lazima?").asserted_truth)


# ── the ask-clause narrowing, both limbs ───────────────────────────────────────────────
def test_a_frame_outside_the_ask_is_not_a_premise():
    """extract_087: an AMOUNT question whose yes/no lead comes from base_rejection. `tunalipa`
    sits in a clause about production spending and asks nothing — resolving on it would
    re-lead a correct answer, and this was 10 of my first 46 'findings'."""
    assert premise.detect(
        "Uzalishaji tunalipa jumla milioni nne, mauzo tunalipa jumla milioni tatu, "
        "SDL ya kampuni nzima ni ngapi?") is None


def test_a_frame_that_IS_the_ask_is_a_premise():
    """The other limb. A narrowing asserted only in the rejecting direction can empty the
    population and still pass."""
    p = premise.detect("Je, mwajiri mwenye wafanyakazi 8 ana wajibu wa kulipa SDL?")
    assert p is not None and p.frame == "has-a-duty"


def test_the_confirmation_tag_survives_into_the_ask_clause():
    p = premise.detect("Kampuni yenye wafanyakazi 9 haitakiwi kulipa SDL, sivyo?")
    assert p is not None and p.frame == "it-is-required" and p.surface_negated


# ── resolution: the four actions, each by outcome ──────────────────────────────────────
def test_a_POSITIVE_premise_is_left_byte_identical():
    """⛔ THE SCOPING CLAIM, AND THE REASON THE BLAST RADIUS IS 3 ROWS AND NOT 135. A plain
    positive question already has the lead the engine wrote for it. If this ever fails, every
    correct yes/no answer in the corpus is in the blast radius."""
    verdict = results.ComputationResult(
        computation="sdl", applicable=True, amount=None,
        working="Ndiyo. Una wafanyakazi 15 (10 au zaidi), hivyo SDL inatozwa.",
        lead_claim=(premise.OBLIGATION_APPLIES, True))
    res = premise.resolve("nina wafanyakazi 15 je SDL inanihusu", verdict)
    assert res.action == "untouched"
    assert res.result.working == verdict.working


@pytest.mark.parametrize("question,count,expect_lead", [
    # The verdict says SDL applies. "hainihusu" asserts it does not -> DENY.
    ("nina wafanyakazi 15 je SDL hainihusu", 15, "Hapana."),
    # The verdict says SDL does not apply. "hainihusu" asserts the same -> AGREE.
    ("nina wafanyakazi 6 tu je SDL hainihusu", 6, "Ndiyo, ni kweli —"),
])
def test_a_NEGATED_premise_is_agreed_with_or_denied_by_the_VERDICT(question, count,
                                                                  expect_lead):
    text = _answer(question)
    assert text.startswith(expect_lead), text
    # And the substantive verdict is intact underneath — a re-lead may never change it.
    assert f"wafanyakazi {count}" in text, text


def test_a_PROPOSITION_MISMATCH_strips_the_particle_rather_than_asserting_it():
    """⛔ extract_184, AND THE WHOLE eval_394 LESSON IN ONE ROW. The question asks whether WCF
    is COMPULSORY; the verdict answers whether NSSF APPLIES. Those are different claims, so
    the engine must stop asserting a yes/no it never evaluated.

    ⚠️ This is the SAFE direction and not a win: it converts a confident wrong yes/no into a
    non-answer, which moves A1 and never A2."""
    text = _answer("Tunachangia NSSF kwa wafanyakazi 15, je WCF nayo ni lazima?")
    assert not text.startswith(("Ndiyo", "Hapana")), (
        f"a yes/no particle is still being asserted for a proposition the verdict never "
        f"evaluated: {text[:120]!r}")
    assert "NSSF haina kizingiti" in text, (
        f"the substantive verdict was lost, not merely un-led: {text[:120]!r}")


def test_IS_VOLUNTARY_is_NOT_compatible_with_OBLIGATION_APPLIES():
    """The non-compatibility IS the finding. A levy can apply to you and whether it is
    optional is a different claim; conflating them shipped a compulsory levy declared
    voluntary."""
    assert premise.OBLIGATION_APPLIES not in premise._COMPATIBLE.get(
        premise.IS_VOLUNTARY, ())


def test_THRESHOLD_CROSSED_is_compatible_so_a_correct_lead_is_not_stripped():
    """eval_370: "je nimevuka kizingiti cha VAT?" is answered by "you must register". If this
    compatibility were dropped, a CORRECT "Ndiyo, unatakiwa kujisajili VAT" would lose its
    lead — a regression wearing the costume of a safety improvement."""
    verdict = results.ComputationResult(
        computation="vat_registration", applicable=True, amount=None,
        working="Ndiyo, unatakiwa kujisajili VAT. Mauzo yako ya TZS 100,500,000 ...",
        lead_claim=(premise.OBLIGATION_APPLIES, True))
    res = premise.resolve("Mzunguko wangu wa miezi 6 umefika TZS 100,500,000 — je nimevuka "
                          "kizingiti cha VAT?", verdict)
    assert res.action == "untouched", res.why


def test_a_RENDERER_resolution_is_not_re_resolved_by_the_backstop():
    """⛔ THE ORDERING GUARD. The optionality renderer re-leads for a premise the generic
    resolver would call a MISMATCH, so without `premise_resolved` the backstop would strip
    the lead off the very answer that fixed eval_394 — the mechanism destroying its own
    predecessor's fix."""
    text = _answer("Je, NSSF si ya hiari kwa mwajiri anayestahili?")
    assert text.startswith("Ndiyo, ni kweli —"), text
    assert "LAZIMA" in text, text
    denied = _answer("Je, NSSF ni ya hiari kwa mwajiri anayestahili?")
    assert denied.startswith("Hapana."), denied
    assert "si ya hiari" in denied, denied


def test_the_eval_393_path_is_still_byte_identical():
    text = _answer("Kampuni yenye wafanyakazi 9 haitakiwi kulipa SDL, sivyo?")
    assert text.startswith("Ndiyo, ni kweli — SDL haihusiki"), text


# ── the lead-claim contract ────────────────────────────────────────────────────────────
def test_every_declared_lead_claim_sits_on_a_RECOGNISED_particle():
    """⛔ A MIS-DECLARED CLAIM IS WORSE THAN NONE: the resolver would prepend a second
    particle in front of an unrecognised one, putting two polarity markers in one sentence —
    which is the eval_393 defect, manufactured by the machinery built to remove it.

    "Bado hapana." is the specimen: a third surface form that a `startswith("Hapana.")` check
    does not see."""
    from chike import rules_engine as re_
    from chike.rules_engine import corporate_tax, minimum_wage, presumptive
    from chike.rules_engine import registration_thresholds as rt
    verdicts = [
        re_.sdl_applies(12), re_.sdl_applies(6), re_.applicability("nssf"),
        re_.applicability("wcf"), re_.sdl_crosses_threshold(10),
        rt.efd_required(False), rt.efd_required(True),
        rt.vat_registration(450_000_000, "annual"),
        presumptive.compute_presumptive(6_000_000, True, excluded_service=True),
        presumptive.compute_presumptive(250_000_000, True),
        corporate_tax.corporate_tax_rate_statement(loss_years=3, sector="agriculture"),
        corporate_tax.corporate_tax_rate_statement(loss_years=2),
        corporate_tax.corporate_tax_rate_statement(loss_years=3),
    ]
    declared = [v for v in verdicts if v.lead_claim is not None]
    assert len(declared) >= 11, f"only {len(declared)} verdicts declare a claim"
    for v in declared:
        stripped = results.strip_lead_particle(v.working)
        assert stripped != v.working, (
            f"{v.computation} declares lead_claim={v.lead_claim} but its working does not "
            f"open with a recognised yes/no particle: {v.working[:90]!r}")


def test_a_verdict_whose_particle_is_EMBEDDED_declares_no_claim():
    """vat_registration's below-threshold branch opens "Kwa upande wa ...: hapana, ..." with
    the particle mid-sentence. Declaring a claim there would invite exactly the double-particle
    defect above, so it declares None — and that absence is deliberate, not an omission."""
    below = __import__("chike.rules_engine.registration_thresholds",
                       fromlist=["x"]).vat_registration(5_000_000, "annual")
    assert below.lead_claim is None
    assert premise.resolve("je sihitaji kusajili VAT?", below).action == "untouched"


def test_corporate_AMT_declares_FALSE_where_applicable_is_TRUE():
    """⛔ THE REASON `lead_claim` EXISTS RATHER THAN BEING INFERRED. The permanent sector
    exemption returns applicable=True and leads "Hapana, AMT haitumiki" — the flag means the
    corporate-tax statement applies, the LEAD claims AMT does not. Inferring the claim from
    `applicable` would invert every negated AMT question."""
    from chike.rules_engine import corporate_tax
    r = corporate_tax.corporate_tax_rate_statement(loss_years=3, sector="agriculture")
    assert r.applicable is True
    assert r.lead_claim == (premise.OBLIGATION_APPLIES, False)


# ── the routing half ───────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("question,expect", [
    ("nimeajiri watumishi 25 je silipi SDL", "sdl"),
    ("Je, kama nina wafanyakazi 8 tu, bado silazimika kulipa NSSF?", "nssf"),
    ("Nina mfanyakazi mmoja tu anayelipwa TZS 500,000, je bado sichangii WCF?", "wcf"),
    ("Tuna wafanyakazi wachache sana, WCF haituhusu?", "wcf"),
])
def test_a_NEGATED_question_reaches_the_engine_its_positive_twin_reaches(question, expect):
    assert routing.detect_intent(question) == expect


@pytest.mark.parametrize("question", [
    "Sichangii chama cha wafanyakazi, je hiyo ni shida kisheria?",
    "Silipi kodi ya ardhi, nifanye nini?",
    "Je silipi deni langu la benki mwezi huu, nifanye nini?",
    "Hatulipi wafanyakazi wetu kwa wakati, tutafanya nini?",
    "Silazimika kuhudhuria mkutano wa BRELA, sivyo?",
])
def test_the_negated_forms_do_NOT_route_a_question_no_engine_holds(question):
    """R17 step 2. A clean corpus sweep is a lower bound — and here it is a particularly weak
    one: the cue widening moved ZERO corpus rows, because the corpus is ~96% positive-premise.
    These probes are the only evidence the widening is not over-broad."""
    assert routing.detect_intent(question) == "none"


def test_the_negated_cue_lists_are_separately_named_so_a_sweep_can_subtract_them():
    """The precedent _GAP_B_APPLICABILITY_CUES sets, and the reason it set it: an earlier
    sweep inlined that set, could not turn it off, and reported a zero blast radius — a false
    clean sweep."""
    assert routing._NEGATED_APPLICABILITY_CUES
    assert all(c in routing._APPLICABILITY_CUES
               for c in routing._NEGATED_APPLICABILITY_CUES)
    assert routing._OWN_OBLIGATION_NEGATED and routing._OWN_OBLIGATION_AFFIRMATIVE


def test_no_routing_pattern_compiled_to_a_control_character():
    """R39 #4: `\\b` in a non-raw string is a literal backspace, the source looks correct in
    every tool that reads source, and the only place the truth exists is the compiled object.
    Swept over every pattern in the module, not only the ones this change touched."""
    import re as _re
    bad = {}
    for name in dir(routing):
        obj = getattr(routing, name)
        if isinstance(obj, _re.Pattern):
            ctrl = [hex(ord(c)) for c in obj.pattern if ord(c) < 32]
            if ctrl:
                bad[name] = ctrl
    assert not bad, f"compiled patterns containing control characters: {bad}"
