"""ONE RENDERER WAS SERVING FOUR ASKS. NOW THERE ARE FIVE, AND EACH CHECKS ITS OWN OUTPUT.

⛔ WHY A CONTRACT AND NOT JUST FIVE FUNCTIONS. Splitting `levy_rate_statement` into separate
renderers for rate / threshold / method / incidence / party is a statement of intent, and
nothing stopped the next edit from putting a rate back into the threshold text or dropping the
operation out of the method text. Three regressions in one day came from the conflation:

  eval_233  a headcount question answered rate-first      PASS -> FAIL
  eval_130  a method question answered without the method WRONG -> UNDETERMINED
  eval_112  WCF's rate stated on one wage, not the payroll  judge CORRECT both ways
  eval_087  a party question answered total-first         CORRECT -> UNDETERMINED

⚠️ THE BASE ONE IS THE REASON THE CONTRACT EXISTS RATHER THAN A TEST PER ROW. On eval_112 the
regex scorer sees answer_type `number` with "0.5" present and passes it either way, and the
judge voted CORRECT 5/5 before AND after the fix. **Hand reading was the only instrument that
caught it.** A contract on the renderer's own output is the mechanical replacement for that,
and it is the only one of the four that no scorer here can see.

R26 throughout: every arm has the failing case planted beside the passing one, and the
specimens are the REAL pre-fix text — from the committed live artifact or from the live
renderer itself — never a paraphrase.

⛔ AND THE PRECONDITION LESSON IS APPLIED, NOT CITED. `test_rate_branch_needs_a_figure_to_engage`
asserted `sole_plausible_amount(q) is None` — a property of the QUESTION, true before and after
the statement route, which stayed green through a deliberate reversal of the behaviour it was
named for. Every assertion below is on an OUTCOME: the text a renderer emits, or the reply the
real orchestrator returns. Each would go red if the behaviour it guards were inverted.
"""
import io
import json
import os

import pytest

from chike import routing, rules_engine, swahili_numbers as swn
from chike.model_abstraction import FakeBackend
from chike.orchestrator import Orchestrator
from chike.rules_engine import rate_statement as rs

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEVIES = ("sdl", "nssf", "wcf")


def _answer(question):
    """The real orchestrator, no network. `call_count == 0` means a deterministic answer."""
    fake = FakeBackend(scripted_reply="<<MODEL PATH>>")
    orch = Orchestrator(backend=fake, retriever=lambda _q: [])
    reply = orch.answer(question)
    return reply.text or "", fake.call_count


def _artifact(rel):
    return json.load(io.open(os.path.join(REPO, rel), encoding="utf-8"))


# ── THE POSITIVE LIMB: every renderer must render, for every levy it claims ──────────────

@pytest.mark.parametrize("levy", LEVIES)
def test_every_renderer_renders_for_every_levy_it_claims_to_support(levy):
    """The contract runs inside each renderer, so this is also the whole-table check: a table
    entry that stops answering its own question cannot be rendered at all."""
    assert rules_engine.rate_statement_supports(levy)
    assert rules_engine.rate_statement_supports_threshold(levy)
    assert rules_engine.rate_statement_supports_method(levy)
    assert rules_engine.rate_statement_supports_incidence(levy)
    for fn in (lambda: rules_engine.levy_rate_statement(levy),
               lambda: rules_engine.levy_rate_statement(levy, 800000),
               lambda: rules_engine.levy_threshold_statement(levy),
               lambda: rules_engine.levy_method_statement(levy),
               lambda: rules_engine.levy_incidence_statement(levy)):
        assert fn().working.strip()
    for party in ("employer", "employee"):
        assert rules_engine.rate_statement_supports_party(levy, party)
        assert rules_engine.levy_party_share_statement(levy, party).working.strip()


# ── THE NEGATIVE LIMB: each real specimen must be blocked by its own renderer's contract ──

def test_the_BASE_contract_blocks_the_REAL_eval_112_pre_fix_reply():
    """⛔ THE SPECIMEN IS THE LIVE PRE-FIX REPLY, READ OUT OF THE COMMITTED ARTIFACT.

    Not reconstructed from the defect description — the text production actually served on
    build dce1432, when the route first started answering eval_112 from the engine. It states
    WCF's 0.5% on "mshahara ghafi", the individual's wage, where WCF is charged on the whole
    payroll. Both automated scorers passed it.
    """
    rows = _artifact("eval/results/diverted_rows_live_2026_10_09.json")["rows"]
    specimen = next(r["reply"] for r in rows if r["id"] == "eval_112")
    assert "asilimia 0.5" in specimen and "jumla" not in specimen.lower()[:120], (
        f"the artifact's eval_112 reply is no longer the defective one, so this test is pinned "
        f"to the wrong specimen: {specimen!r}")
    with pytest.raises(rs.RendererContractError, match="WHOLE payroll"):
        rs._assert_answers_its_own_question("rate", "wcf", specimen)
    # And the text that replaced it passes, so the contract is not simply rejecting everything.
    rs._assert_answers_its_own_question("rate", "wcf",
                                        rules_engine.levy_rate_statement("wcf").working)


def test_the_BASE_contract_blocks_the_MIRROR_defect_too():
    """NSSF is a per-employee percentage. Stating it on the aggregate payroll is the same defect
    inverted, and a contract that only checked the aggregate levies would be half a check."""
    mirrored = ("Kiwango cha NSSF ni asilimia 20 ya jumla ya mishahara ghafi ya wafanyakazi "
                "wote. Sehemu ya mwajiri hulipwa na mwajiri — HAIKATWI kwenye mshahara.")
    with pytest.raises(rs.RendererContractError, match="PER-EMPLOYEE"):
        rs._assert_answers_its_own_question("rate", "nssf", mirrored)


def test_the_THRESHOLD_contract_blocks_the_rate_led_answer():
    """eval_233's regression: the renderer the branch used to call. The specimen is the LIVE
    rate renderer, so it tracks the real text rather than a frozen copy of it."""
    with pytest.raises(rs.RendererContractError, match="volunteers a rate"):
        rs._assert_answers_its_own_question(
            "threshold", "sdl", rules_engine.levy_rate_statement("sdl").working)


def test_the_METHOD_contract_blocks_an_answer_with_no_operation():
    with pytest.raises(rs.RendererContractError, match="does not LEAD with the operation"):
        rs._assert_answers_its_own_question(
            "method", "sdl", rules_engine.levy_rate_statement("sdl").working)


def test_the_PARTY_contract_blocks_the_total_led_answer_that_regressed_eval_087():
    """The specimen is the live rate renderer — the exact text that was being served to
    eval_087 when the judge moved it from CORRECT to a 2-wrong/2-correct split."""
    total_led = rules_engine.levy_rate_statement("nssf").working
    assert "asilimia 20" in total_led
    for party in ("employer", "employee"):
        with pytest.raises(rs.RendererContractError, match="leads with 20"):
            rs._assert_answers_its_own_question("party", "nssf", total_led, party=party)


def test_the_PARTY_contract_requires_an_employer_only_levy_to_DENY_the_employee_share_first():
    """SDL and WCF have no employee share. A reply that opens with the rate and mentions the
    denial later reads as the employee's own figure, which is the eval_086 party inversion in
    a new place."""
    rate_first = ("Kiwango ni asilimia 3.5 ya jumla ya mishahara ghafi ya wafanyakazi wote. "
                  "Mfanyakazi halipi SDL.")
    with pytest.raises(rs.RendererContractError, match="before any rate"):
        rs._assert_answers_its_own_question("party", "sdl", rate_first, party="employee")
    # The shipped text denies first and therefore passes.
    rs._assert_answers_its_own_question(
        "party", "sdl", rules_engine.levy_party_share_statement("sdl", "employee").working,
        party="employee")


def test_the_INCIDENCE_contract_blocks_text_that_does_not_say_who_pays():
    with pytest.raises(rs.RendererContractError, match="does not say who pays"):
        rs._assert_answers_its_own_question(
            "incidence", "sdl", "Kiwango cha SDL ni asilimia 3.5 ya jumla ya mishahara.")


# ⛔ THE WIRING, NOT THE LOGIC. Both inert controls of 2026-08-24 had perfect logic and were
# reached by nothing. These assert the contract is reached THROUGH each renderer, by corrupting
# the renderer's own table entry and watching the renderer — not the contract — raise.
@pytest.mark.parametrize("kind,table,key,fn", [
    ("threshold", "_THRESHOLD", "sdl",
     lambda: rules_engine.levy_threshold_statement("sdl")),
    ("method", "_METHOD", "sdl",
     lambda: rules_engine.levy_method_statement("sdl")),
    ("incidence", "_INCIDENCE", "sdl",
     lambda: rules_engine.levy_incidence_statement("sdl")),
    ("party", "_PARTY_SHARE", ("nssf", "employee"),
     lambda: rules_engine.levy_party_share_statement("nssf", "employee")),
])
def test_each_renderer_APPLIES_its_contract_rather_than_merely_having_one(kind, table, key, fn,
                                                                         monkeypatch):
    original = dict(getattr(rs, table))
    broken = dict(original)
    broken[key] = "Hakuna jibu."            # answers no question at all
    monkeypatch.setattr(rs, table, broken)
    with pytest.raises(rs.RendererContractError):
        fn()
    monkeypatch.setattr(rs, table, original)
    assert fn().working.strip()


def test_an_unsupported_type_RAISES_rather_than_inventing_an_answer():
    for levy in ("paye", "vat"):
        assert rules_engine.rate_statement_supports_incidence(levy) is False
        assert rules_engine.rate_statement_supports_party(levy, "employer") is False
        with pytest.raises(ValueError):
            rules_engine.levy_incidence_statement(levy)
        with pytest.raises(ValueError):
            rules_engine.levy_party_share_statement(levy, "employer")


# ── THE EXTRACTOR: a capability, not an intention (R31) ─────────────────────────────────

def test_levy_party_is_REACHED_from_natural_phrasing_and_not_from_a_keyword():
    """⛔ THE TEST THE UNIT SUITE STRUCTURALLY CANNOT PROVIDE. `levy_party_share_statement` was
    written with a docstring naming an extractor (`asks_levy_party`) that existed in no file —
    engine function, support predicate, no extractor, no call site. That is the corporate
    `sector=` shape: unit-testable by passing the keyword in by hand, unreachable from anything
    a person would type. These supply the party ONLY through the sentence."""
    assert routing.levy_party("Kiwango cha NSSF kwa upande wa mwajiri ni asilimia ngapi?",
                              "nssf") == "employer"
    assert routing.levy_party("Kiwango cha NSSF kwa upande wa mfanyakazi ni asilimia ngapi?",
                              "nssf") == "employee"


def test_levy_party_maps_the_TOTAL_default_to_None():
    """`nssf_party` defaults to 'total' on no match, which is right for picking an amount
    headline and would be catastrophic here: it would make every levy rate question a party
    question. The mapping to None is what keeps the common case common."""
    for q in ("Kiwango cha NSSF ni asilimia ngapi?",
              "Jumla ya mchango wa NSSF ni asilimia ngapi?",
              "Mwajiri na mfanyakazi wanachangia NSSF asilimia ngapi kwa pamoja?"):
        assert routing.nssf_party(q) == "total"
        assert routing.levy_party(q, "nssf") is None, q


def test_the_PLURAL_aggregate_base_is_not_read_as_a_party_ask():
    """⛔ THE COLLISION THE NARROWNESS EXISTS FOR, and it would have looked like success. The
    employee cues are SINGULAR ('wa mfanyakazi'), and four corpus rows ask for a rate on "jumla
    ya mishahara ya WAFANYAKAZI wote" — the aggregate base. A bare 'mfanyakazi' cue would divert
    all four onto the party renderer and answer a base question with a share, raising the
    diversion count, which reads as the change working."""
    for q in ("Kiwango cha SDL ni asilimia ngapi ya jumla ya mishahara ya wafanyakazi wote?",
              "Kiwango cha WCF ni asilimia ngapi ya jumla ya mishahara ya jumla?"):
        assert routing.levy_party(q, routing.detect_intent(q)) is None, q


def test_levy_party_declines_every_type_that_has_no_party_text():
    for ct in ("paye", "vat", "none", None):
        assert routing.levy_party("sehemu ya mwajiri ni ngapi", ct) is None


# ── THE BRANCH: driven through the real orchestrator ────────────────────────────────────

@pytest.mark.parametrize("question,opens_with", [
    ("Kiwango cha mchango wa NSSF kwa upande wa mwajiri ni asilimia ngapi ya mshahara wa "
     "jumla wa mfanyakazi?", "Sehemu ya mwajiri"),
    ("Kiwango cha mchango wa NSSF kwa upande wa mfanyakazi ni asilimia ngapi ya mshahara "
     "wake wa jumla?", "Sehemu ya mfanyakazi"),
])
def test_eval_086_and_087_are_answered_with_the_asked_share_FIRST(question, opens_with):
    """eval_086 and eval_087 verbatim. Before this branch both got "Kiwango cha NSSF ni
    asilimia 20 …" with the asked-for 10% in a parenthetical — eval_086 survived only because
    the clause after the parenthetical happens to lead with the employer, so the two rows
    differed by luck rather than by handling."""
    text, calls = _answer(question)
    assert calls == 0, "this must be a deterministic answer, not a model reply"
    assert text.startswith(opens_with), text
    first_rate = rs._RATE_TOKEN.search(text)
    assert first_rate and first_rate.group(1) == "10", (
        f"the reply leads with {first_rate.group(1) if first_rate else None} where the asked "
        f"share is 10 — the eval_087 regression is back: {text}")


@pytest.mark.parametrize("question", [
    "Mfanyakazi alifanya kazi siku 26 mwezi huu, NSSF yake ni kiasi gani basi?",
    "Mfanyakazi wangu analipwa dola 500 za Marekani kwa mwezi, NSSF yake ni ngapi?",
    "Muuzaji analipwa kwa kamisheni, asilimia 5 ya alichouza mwezi — NSSF yake ni ngapi?",
])
def test_an_AMOUNT_question_naming_a_party_does_NOT_get_a_rate_statement(question):
    """⛔⛔ THE SIX REGRESSIONS MY FIRST VERSION OF THIS BRANCH SHIPPED, PINNED AS TESTS.

    Gating on the party alone was asking "is a party mentioned" where the question that matters
    is "is the party's SHARE what was requested" — and a party is named in every amount question
    about a levy ("NSSF YAKE ni kiasi gani?"). These three asked for a figure, had none, and
    correctly CLARIFIED; the branch replaced all three clarifications with a rate statement.
    `asks_rate` is the gate that fixed it, and these rows are why it is load-bearing.
    """
    text, _calls = _answer(question)
    assert "Sehemu ya mfanyakazi ni asilimia" not in text, (
        f"an amount question has been answered with the employee's rate instead of being asked "
        f"for the salary: {text}")
    assert "Sehemu ya mwajiri ni asilimia" not in text, text


def test_a_party_question_that_CAN_be_computed_keeps_its_computation():
    """eval_289 was the worst of the six and the one a loose amount gate let through: two
    salaries are present, so `sole_plausible_amount` returns None, and the branch swallowed a
    correct COMPUTED answer (10% x TZS 7,000,000 = TZS 700,000) and replaced it with a bare
    rate."""
    q = ("Nusu ya wafanyakazi 14 wanapata TZS 620,000, nusu wanapata TZS 380,000 — sehemu ya "
         "mwajiri ya NSSF?")
    text, _calls = _answer(q)
    assert "700,000" in text, (
        f"the computed employer share is gone — the party branch is swallowing a question the "
        f"compute path answers: {text}")


@pytest.mark.parametrize("question,must_contain", [
    ("Kiwango cha SDL ni asilimia ngapi ya jumla ya mishahara ya jumla ya wafanyakazi wote?",
     "JUMLA ya mishahara"),
    ("Kiwango cha WCF ni asilimia ngapi ya jumla ya mishahara ya jumla?",
     "JUMLA ya mishahara ghafi ya wafanyakazi wote"),
])
def test_the_CONTROL_ARM_keeps_the_rate_renderer(question, must_contain):
    """eval_111 and eval_112 verbatim — the rows whose whole point is the aggregate BASE. If
    either started getting a party answer, the extractor is too wide and the blast-radius
    enumeration in eval/routing/sweep_levy_party_2026_10_10.py is not a population."""
    text, calls = _answer(question)
    assert calls == 0
    assert must_contain in text, text
    assert not text.startswith("Sehemu ya"), (
        f"a base question is being answered with a party's share: {text}")


def test_the_branch_ORDER_puts_method_and_threshold_ahead_of_party():
    """A method ask and a headcount ask can both name a party; the more specific renderer must
    win. Asserted on the OUTPUT, so re-ordering the branches turns this red."""
    method, _ = _answer("Mwajiri anahesabu kiasi cha SDL cha kulipa kwa mwezi vipi?")
    assert method.startswith("Zidisha"), method
    threshold, _ = _answer("Ni idadi gani ya waajiriwa inayofanya mwajiri kuwa na wajibu wa "
                           "kulipa SDL Tanzania Bara?")
    assert threshold.startswith("Mwajiri mwenye wafanyakazi 10"), threshold


def test_the_sweep_artifact_records_a_THREE_row_blast_radius_and_a_held_control_arm():
    """R18: the write-up and its evidence one lookup apart. This also makes the sweep's own
    verdict a standing assertion rather than a thing someone once read."""
    a = _artifact("eval/results/levy_party_sweep_2026_10_10.json")
    assert a["questions_swept"] >= 2400
    assert a["findings"] == [], a["findings"]
    assert a["moved"] == 3, (
        f"the party branch's blast radius has changed from 3 to {a['moved']} rows — re-run the "
        f"sweep and read every new row before updating this number")
    assert sorted(m["id"] for m in a["moved_rows"]) == sorted(a["must_move"])
