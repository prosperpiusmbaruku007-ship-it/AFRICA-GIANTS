"""AN OPTIONALITY QUESTION IS NOT AN APPLICABILITY QUESTION, AND THE LEAD WAS ANSWERING THE
WRONG ONE IN BOTH DIRECTIONS.

⛔ A YES/NO LEAD IS AN ANSWER TO ONE PARTICULAR QUESTION, AND THE ENGINE ONLY KNOWS ONE. Every
applicability verdict writes its lead for the plain frame "does this levy apply?" —
`nssf_applies()` opens "Ndiyo.". Route a question with a different premise to the same verdict
and the lead answers something nobody asked, in the engine's own voice.

  eval_394  "Je, NSSF SI ya hiari …"  premise TRUE, confirmed by applicable=True. Lead "Ndiyo."
            was accidentally right in substance and CONTRADICTED the model body's "Hapana, si
            ya hiari" one sentence later. The judge marked the row WRONG for the contradiction
            — and THE BODY WAS THE CORRECT HALF. That is why the fix is here and not a
            body-blanking rule: blanking on disagreement deletes the right answer.

  the mirror "Je, NSSF NI ya hiari?"  premise FALSE, contradicted by the same verdict. Lead
            "Ndiyo." reads as YES, NSSF IS VOLUNTARY. **Flatly wrong**, worse than eval_394,
            and found by asking the mirror of the gate row rather than only the gate row —
            R17 step 2 applied to a PREMISE instead of a cue list.

⚠️ AND THE OLD `applicable is False` GATE WAS NEVER A STATEMENT ABOUT NEGATION. It encoded
eval_393's premise SHAPE ("the levy does not apply"), which applicable=False confirms, so it
rejected the second real instance of the thing the function is for. R20's borrowed-detector
question: whose words is the check written for, and is it the same population?
"""
import pytest

from chike import routing, rules_engine
from chike.model_abstraction import FakeBackend
from chike.orchestrator import Orchestrator
from chike.rules_engine import rate_statement as rs


def _answer(question):
    fake = FakeBackend(scripted_reply="Hapana, si ya hiari. <<MODEL BODY>>")
    reply = Orchestrator(backend=fake, retriever=lambda _q: []).answer(question)
    return reply.text or "", fake.call_count


@pytest.mark.parametrize("question,levy", [
    ("Je, NSSF si ya hiari kwa mwajiri anayestahili?", "NSSF"),
    ("Je, WCF si ya hiari?", "WCF"),
])
def test_a_NEGATED_premise_the_verdict_confirms_is_AGREED_with(question, levy):
    text, calls = _answer(question)
    assert calls == 0, "the body is blanked, so the lead cannot be pushed out of reach"
    assert text.startswith("Ndiyo, ni kweli —"), text
    assert "si ya hiari" in text, f"the premise is not restated, so the agreement is bare: {text}"
    assert "LAZIMA" in text, text
    assert "<<MODEL BODY>>" not in text, (
        "the model body survived. The yes/no polarity is read from the first paragraph, so a "
        "preamble in front of the re-led verdict puts the lead back out of reach")


@pytest.mark.parametrize("question", [
    "Je, NSSF ni ya hiari kwa mwajiri anayestahili?",
    "Je, WCF ni ya hiari?",
])
def test_a_POSITIVE_premise_the_verdict_contradicts_is_DENIED(question):
    """⛔ THE HALF THAT WAS FLATLY WRONG. Before 2026-10-10 this answered "Ndiyo." — yes, it is
    voluntary — to a question asking whether a compulsory levy is optional."""
    text, _calls = _answer(question)
    assert text.startswith("Hapana."), (
        f"a question asserting the levy IS voluntary must be DENIED, not agreed with: {text}")
    assert "si ya hiari" in text and "LAZIMA" in text, (
        f"a bare 'Hapana.' denies something the user has to guess at, which is the ambiguity "
        f"that produced eval_394: {text}")


def test_the_two_polarities_do_NOT_get_the_same_lead():
    """The both-directions plant. A rule that leads the same way on both premises is the
    defect, whichever way it leads — and that was the state of the code until today."""
    agreed, _ = _answer("Je, NSSF si ya hiari kwa mwajiri anayestahili?")
    denied, _ = _answer("Je, NSSF ni ya hiari kwa mwajiri anayestahili?")
    assert agreed.split()[0] != denied.split()[0], (
        f"both premises are being led identically:\n  {agreed[:90]}\n  {denied[:90]}")
    # Same substantive verdict underneath, which is what makes the re-lead safe.
    for text in (agreed, denied):
        assert "haina kizingiti cha idadi ya wafanyakazi" in text, (
            f"the engine's substantive verdict was lost, not merely re-led: {text}")


@pytest.mark.parametrize("question", [
    "Naweza kujiunga NSSF kwa hiari?",
    "Je, mtu anayejiajiri anaweza kuchangia NSSF kwa hiari?",
])
def test_the_VOLUNTARY_OPT_IN_question_is_untouched(question):
    """⛔ THE REAL COUNTER-EXAMPLE, AND IT IS WHY THE CUE IS NOT A BARE `hiari`. NSSF genuinely
    HAS voluntary membership for the self-employed, so this asks about opting IN. Answering it
    "NSSF is mandatory for employers" is the eval_211 wrong-topic harm class. The predicative
    `si/ni ya hiari` frame is what keeps it on the fact path."""
    assert routing.asks_levy_optionality(question) is False
    _text, calls = _answer(question)
    assert calls == 1, "this must still reach the model on the fact path"


def test_negates_optionality_separates_the_premises_and_asks_nothing_about_the_route():
    assert routing.negates_optionality("Je, NSSF si ya hiari?") is True
    assert routing.negates_optionality("Je, NSSF ni ya hiari?") is False
    # Deliberately says nothing about whether an optionality question was asked at all.
    assert routing.negates_optionality("SDL si ya hiari kwa mtu yeyote") is True
    assert routing.asks_levy_optionality("Je, NSSF ni ya hiari?") is True


def test_the_optionality_claim_answers_COMPULSION_and_not_HEADCOUNT():
    """eval_394's substantive defect, which the lead merely made visible: the engine answered
    "NSSF haina kizingiti cha idadi ya wafanyakazi" — a headcount fact — to a question about
    whether the levy is voluntary. The claim now states compulsion, and the contract enforces
    it."""
    for levy in ("nssf", "wcf", "sdl"):
        claim = rules_engine.levy_optionality_claim(levy)
        assert "hiari" in claim.lower() and "LAZIMA" in claim
        assert "asilimia" not in claim.lower(), (
            f"{levy}: a rate on a question about compulsion is the unsupported-figure defect "
            f"the threshold renderer was split out for: {claim}")


def test_only_SDL_names_a_headcount_in_its_compulsion_claim():
    """SDL is compulsory only at 10+, so the qualifier is required there and would be INVENTED
    for NSSF and WCF, which have no threshold at all — eval_394's own bleed in the other
    direction (SDL's headcount bolted onto NSSF)."""
    assert "10" in rules_engine.levy_optionality_claim("sdl")
    for levy in ("nssf", "wcf"):
        claim = rules_engine.levy_optionality_claim(levy)
        assert not any(ch.isdigit() for ch in claim), (
            f"{levy} has no headcount threshold and its claim names a number: {claim}")


def test_the_contract_blocks_a_HEADCOUNT_answer_to_an_optionality_question():
    """R26's plant: the real pre-fix text, which is the applicability verdict itself."""
    headcount_answer = rules_engine.applicability("nssf").working
    assert "kizingiti cha idadi" in headcount_answer
    with pytest.raises(rs.RendererContractError, match="does not mention voluntariness"):
        rs._assert_answers_its_own_question("optionality", "nssf", headcount_answer)


def test_agree_with_negated_premise_still_REFUSES_a_premise_the_verdict_contradicts():
    """The guard that keeps this from turning a correct verdict into a wrong one, both ways."""
    applies = rules_engine.applicability("nssf")           # applicable=True
    with pytest.raises(ValueError, match="must be denied"):
        rules_engine.agree_with_negated_premise(applies)   # default: confirmed when NOT applicable
    not_applies = rules_engine.sdl_applies(9)              # applicable=False
    with pytest.raises(ValueError, match="must be denied"):
        rules_engine.agree_with_negated_premise(not_applies, confirmed_when_applicable=True)


def test_the_eval_393_path_is_BYTE_IDENTICAL_after_the_signature_change():
    """The default keeps every existing caller unchanged. A new keyword that silently alters
    the old behaviour would be a regression hiding inside a fix."""
    result = rules_engine.sdl_applies(9)
    assert result.applicable is False
    re_led = rules_engine.agree_with_negated_premise(result)
    assert re_led.working.startswith("Ndiyo, ni kweli —")
    assert "Hapana." not in re_led.working
    assert re_led.applicable is False and re_led.amount == result.amount


def test_deny_positive_premise_REQUIRES_the_premise_restated():
    with pytest.raises(ValueError, match="premise restated"):
        rules_engine.deny_positive_premise(rules_engine.applicability("nssf"), restate="")


def test_the_scoping_artifact_records_the_polarity_flag_going_to_zero_and_WHY():
    """R39: a detector going quiet looks identical to a detector going blind. The polarity arm
    was 2 before this fix and is 0 after — because eval_394 now takes the deterministic path
    and leaves the body+working population entirely. That reason is recorded, not inferred."""
    import io
    import json
    import os
    a = json.load(io.open(os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "eval", "results", "render_disagreement_scoping_2026_10_10.json"), encoding="utf-8"))
    pol = a["_adjudication"]["polarity"]
    assert pol["flags"] == 0
    assert "_why_this_is_now_ZERO" in pol and "eval_394" in pol["_why_this_is_now_ZERO"]
