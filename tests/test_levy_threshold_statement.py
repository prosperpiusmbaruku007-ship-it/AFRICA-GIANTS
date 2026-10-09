"""THE THRESHOLD-LED ANSWER — a headcount question must not be answered rate-first.

⛔ THIS FILE EXISTS BECAUSE I SHIPPED THE REGRESSION IT TESTS, HOURS EARLIER, ON 2026-10-09.
The statement route's threshold branch called `levy_rate_statement`, so `eval_233` ("Ni idadi
gani ya waajiriwa inayofanya mwajiri kuwa na wajibu wa kulipa SDL?") came back led by "Kiwango
cha SDL ni asilimia 3.5 …", with the headcount rule buried mid-paragraph and a request for
payroll figures at the end. **Right branch, wrong renderer.** A PASS at gate `0e11c3d` became a
FAIL, measured live before the next gate ran, not discovered by it.

Two independent things were wrong, which is why a renderer and not a reword was the fix:
  * the scorer failed it CORRECTLY — the gold holds no rate, the reply volunteers 3.5, and an
    unsupported figure in an answer is a defect, not a bonus;
  * the copy was wrong-topic-first, which is R15's measured lever pointing the other way: lead
    with what the user asked about. They asked HOW MANY PEOPLE.

⚠️ AND THE SECOND DRAFT STILL FAILED, which is the part worth keeping. "SDL inamhusu mwajiri
mwenye wafanyakazi 10 au zaidi … halipi SDL" is correct and rate-free and shares only two
5-char-plus tokens with the gold, where the `definition` limb needs three. Revising wording after
watching a lexical scorer is one step from instrument-fitting, so the test applied was: **is the
wording defensible from the QUESTION rather than from the gold?** It is — eval_233 asks what
makes an employer "kuwa na WAJIBU WA KULIPA SDL", so "ana wajibu wa kulipa" is the asker's own
construction. Had the only defence been "it matches the gold", the right move would have been to
leave the row failing for the judge, as `eval_394` is being left.

R26 throughout: every arm below has the failing case planted beside the passing one, because a
test that only asserts the new text would pass just as happily on a renderer that always emits
the same paragraph.
"""
import io
import json
import os

import pytest

from chike import routing, rules_engine, swahili_numbers as swn
from chike.decomposition import decompose_query
from chike.scoring import score_question

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _rows(rel):
    with io.open(os.path.join(REPO, rel), encoding="utf-8") as fh:
        return {json.loads(l)["id"]: json.loads(l) for l in fh if l.strip()}


GATE = {}
for _f in ("eval/accuracy_gate/eval_questions_001.jsonl",
           "eval/accuracy_gate/eval_questions_002_additions.jsonl",
           "eval/accuracy_gate/eval_questions_003.jsonl"):
    GATE.update(_rows(_f))

with io.open(os.path.join(REPO, "kaggle", "chike_config.json"), encoding="utf-8") as _fh:
    _CFG = json.load(_fh)
REFUSALS = _CFG.get("refusal_phrases") or _CFG.get("REFUSAL_PHRASES") or []


def _threshold_parts(question):
    """Exactly the orchestrator's threshold-branch condition, over DECOMPOSED sub-questions.

    ⛔ DECOMPOSED, NOT WHOLE. My first count of which gate rows reach this branch tested the
    whole question string and reported TWO — the second being `eval_322`, a three-part
    enumeration whose SDL limb asks for the RATE while the word `kizingiti` sits in its VAT
    limb. The orchestrator routes SUB-questions, so that bleed does not exist; a check that
    models the pipeline wrongly manufactures a defect in the safe-looking direction (R34).
    """
    out = []
    for t in (decompose_query(question) or [question]):
        if (routing.detect_intent(t) in ("sdl", "nssf", "wcf")
                and routing.asks_levy_threshold(t)
                and swn.sole_headcount(t) is None
                and not swn.states_no_employees(t)):
            out.append(t)
    return out


def test_the_sdl_threshold_statement_states_the_headcount_and_NOT_the_rate():
    text = rules_engine.levy_threshold_statement("sdl").working
    assert "10 au zaidi" in text, text
    assert "chini ya 10" in text, "the sub-threshold limb is gone; the gold states it explicitly"
    assert "3.5" not in text and "asilimia" not in text, (
        f"the rate is back in a threshold answer. That is the exact regression this renderer "
        f"was split out to prevent — an unsupported figure on a headcount question: {text}")


def test_eval_233_PASSES_on_the_threshold_renderer_and_FAILS_on_the_rate_renderer():
    """⛔ THE PLANT, BOTH DIRECTIONS, ON THE REAL ROW AND THE REAL SCORER.

    Asserting only that the new text passes would be satisfied by any wording that happened to
    overlap the gold. The second limb is what makes it evidence: the renderer the branch used to
    call still FAILS the same row, so the difference being measured is the renderer's, not the
    scorer's mood.
    """
    q = GATE["eval_233"]
    good = rules_engine.levy_threshold_statement("sdl").working
    bad = rules_engine.levy_rate_statement("sdl", None).working
    assert score_question(q, good, REFUSALS) is True, good
    assert score_question(q, bad, REFUSALS) is False, (
        "the RATE statement now passes eval_233 too, so this test no longer demonstrates the "
        "regression it was written for — re-read the scorer before relaxing anything")


@pytest.mark.parametrize("levy", ["nssf", "wcf"])
def test_a_levy_with_no_headcount_threshold_says_so_rather_than_naming_one(levy):
    """`WCF_MIN_EMPLOYEES = 1` with its own comment reading "from the first employee, no
    threshold". Rendering that as "one employee" would read AS a threshold and invite the bleed
    `eval_394` produced in the other direction (a headcount qualifier attached to NSSF, which
    has none). So the absence is stated as an absence."""
    text = rules_engine.levy_threshold_statement(levy).working
    assert "haina kizingiti" in text, text
    assert "mfanyakazi wa kwanza" in text, text
    assert not any(ch.isdigit() for ch in text), (
        f"a levy with no headcount threshold must not name a number: {text}")


def test_an_unsupported_computation_type_RAISES_rather_than_inventing_a_threshold():
    assert rules_engine.rate_statement_supports_threshold("paye") is False
    with pytest.raises(ValueError):
        rules_engine.levy_threshold_statement("paye")
    with pytest.raises(ValueError):
        rules_engine.levy_threshold_statement("vat")


def test_exactly_ONE_gate_row_reaches_the_threshold_branch_and_it_is_eval_233():
    """The population, asserted rather than assumed. If a second row starts reaching this
    branch, its answer changes shape and nobody is looking — the `nat_23` property (an insertion
    perturbs its neighbours) applied to a routing branch."""
    reaching = sorted(i for i, r in GATE.items() if _threshold_parts(r["question_sw"]))
    assert reaching == ["eval_233"], (
        f"the threshold branch's gate-400 population changed: {reaching}. Each new row needs "
        f"its answer read before this is updated.")


# ── THE METHOD RENDERER (added 2026-10-09, after measuring the second instance) ─────────
# ⛔ ONE RENDERER WAS SERVING FOUR DIFFERENT ASKS, and three of them needed their own. The
# threshold case is above; this is the method case; the third was WCF's base inside the rate
# statement itself. All three were found by MEASURING live replies against the judge, and none of
# them is visible to the regex scorer — eval_130 is `procedure`, eval_112 is `number` with "0.5"
# present, and both score as passes either way. That is the argument for the targeted check.

def _method_parts(question):
    out = []
    for t in (decompose_query(question) or [question]):
        if (routing.detect_intent(t) in ("sdl", "nssf", "wcf")
                and routing.asks_levy_method(t)
                and swn.sole_plausible_amount(t) is None):
            out.append(t)
    return out


def test_the_method_statement_leads_with_the_OPERATION_not_the_rate():
    text = rules_engine.levy_method_statement("sdl").working
    assert text.startswith("Zidisha"), (
        f"a method answer that does not open with the operation is the defect this renderer was "
        f"split out for: {text}")
    assert "3.5" in text and "JUMLA ya mishahara" in text
    assert "wafanyakazi 10 au zaidi" in text, "the applicability qualifier is still owed here"
    assert "sDL" not in text, (
        "the levy name has been case-munged. My first draft spliced the incidence clause "
        "mid-sentence with [0].lower(), which produced 'sDL inalipwa' — visible only by printing "
        "the output, never by reading the source")


def test_the_REGEX_SCORER_CANNOT_TELL_THE_TWO_RENDERERS_APART_on_eval_130():
    """⛔ MY FIRST VERSION OF THIS TEST ASSERTED THE OPPOSITE AND FAILED, AND THE FAILURE IS THE
    MOST USEFUL THING IN THIS FILE.

    I wrote it as the usual both-directions plant: the method renderer passes eval_130 and the
    rate renderer fails it. **The rate renderer PASSES TOO.** `answer_type` is `procedure`, which
    the scorer grades by counting three shared 5-character-plus tokens with the gold, and both
    renderings share "mishahara", "wafanyakazi" and "jumla". The scorer is blind to whether the
    OPERATION is stated at all.

    So the regex scorer cannot see this defect, cannot see the WCF base defect (`number`, "0.5"
    present), and could not see the inverted "divide by 3.5%" that eval_130 shipped at 0e11c3d —
    which is exactly why that row was one of the seventeen false passes the judge flagged. **A
    full gate run would have scored every one of these as a pass.** That is the argument for the
    targeted judge-scored check, stated as a test so it cannot quietly stop being true.

    What IS asserted is therefore structural: the operation is present in one and absent in the
    other. A scorer assertion here would be a check that cannot fail.
    """
    q = GATE["eval_130"]
    method = rules_engine.levy_method_statement("sdl").working
    rate = rules_engine.levy_rate_statement("sdl", None).working
    assert "Zidisha" in method and "Zidisha" not in rate, (
        "the two renderers no longer differ on whether they state the operation, which is the "
        "whole reason the method renderer exists")
    assert score_question(q, method, REFUSALS) is True
    assert score_question(q, rate, REFUSALS) is True, (
        "the regex scorer has started distinguishing these two. That would be good news, but "
        "this test's docstring then describes a world that no longer exists — re-read it rather "
        "than flipping the assertion")


def test_the_method_statement_states_NO_example_figure():
    """eval_130's gold carries a worked example ('milioni 10 → 350,000') and the engine
    deliberately does not. An invented amount is the compute path's job; a statement that makes
    one up is the fabrication class D-FIDELITY-7 exists for."""
    for levy in ("sdl", "wcf", "nssf"):
        text = rules_engine.levy_method_statement(levy).working
        figures = [tok for tok in text.replace(",", "").split()
                   if tok.strip(".").isdigit() and len(tok.strip(".")) >= 4]
        assert not figures, f"{levy}: the method statement invented a figure: {figures} in {text}"
        assert "nihesabu" in text, (
            f"{levy}: the hand-off to the compute path is gone, so the user is left with a method "
            f"and no way to get the number")


def test_exactly_ONE_gate_row_reaches_the_method_branch_and_it_is_eval_130():
    reaching = sorted(i for i, r in GATE.items() if _method_parts(r["question_sw"]))
    assert reaching == ["eval_130"], (
        f"the method branch's gate-400 population changed: {reaching}. Each new row needs its "
        f"answer read before this is updated.")


def test_a_method_ask_WITH_a_figure_goes_to_the_compute_path_instead():
    """The ordering guard. A method ask can also satisfy `asks_rate`, so the method branch is
    placed first — but it must not swallow a question that carries the user's own figure, which
    the compute path owns."""
    q = "Jumla ya mishahara ni TZS 10,000,000. SDL inahesabiwa vipi?"
    assert routing.asks_levy_method(q) is True
    assert swn.sole_plausible_amount(q) is not None, (
        "the guard clause this test exists for reads sole_plausible_amount; if that is None here "
        "the ordering guard is untested")
    assert _method_parts(q) == [], "a figure-bearing method ask must not reach the method branch"


def test_an_unsupported_type_RAISES_rather_than_inventing_a_method():
    assert rules_engine.rate_statement_supports_method("paye") is False
    with pytest.raises(ValueError):
        rules_engine.levy_method_statement("paye")


def test_the_WCF_rate_statement_states_the_AGGREGATE_base_not_a_single_wage():
    """⛔ MY MEASURED REGRESSION, PINNED. The rate statement said "ya mshahara ghafi" for every
    levy. For NSSF that is right (20% of the individual's gross wage); for WCF it is wrong by
    omission — 0.5% of the employer's gross cash emoluments, i.e. the whole payroll. The judge
    moved eval_112 from CORRECT to UNDETERMINED when the route started serving the generic text
    instead of the fact-path reply, which had the base right. The regex scorer passes it either
    way, so only a judge-scored targeted check could see it."""
    wcf = rules_engine.levy_rate_statement("wcf").working
    assert "JUMLA ya mishahara ghafi ya wafanyakazi wote" in wcf, wcf
    nssf = rules_engine.levy_rate_statement("nssf").working
    assert "ya mshahara ghafi wa mfanyakazi" in nssf, (
        f"NSSF's base must stay the INDIVIDUAL's wage — it is 20% of one employee's gross pay, "
        f"not of the payroll, and swapping the two bases is the same defect mirrored: {nssf}")
    assert score_question(GATE["eval_112"], wcf, REFUSALS) is True


def test_eval_322s_rate_limb_is_NOT_captured_by_the_threshold_branch():
    """The near-miss, pinned by name. `kizingiti` appears in its VAT limb and `SDL` in its rate
    limb; only decomposition keeps those apart, so this fails loudly if decomposition stops
    splitting it."""
    q = GATE["eval_322"]["question_sw"]
    assert "kizingiti" in q and "SDL" in q
    assert _threshold_parts(q) == [], (
        "eval_322's SDL limb now reaches the threshold branch, so a question asking for the "
        "RATE would be answered with the headcount rule")
