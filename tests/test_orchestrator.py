"""Tests for chike.orchestrator — pipeline shape + dependency injection.

Every test injects a FakeBackend (no network, no GPU), proving the orchestrator is
fully exercisable via the model abstraction layer built in item 1.
"""
import os
from decimal import Decimal

import pytest

from chike.orchestrator import Orchestrator, REFUSAL_TEXT, CLARIFICATION_PENDING
from chike.model_abstraction import FakeBackend


# --- In-scope fact question flows through to a generated reply --------------

def test_in_scope_fact_question_reaches_the_model_and_returns_its_reply():
    fake = FakeBackend(scripted_reply="Ada ya BRELA ni TZS 22,000.")
    # Inject a stub retriever so the test never touches the real e5 index/network.
    orch = Orchestrator(backend=fake, retriever=lambda q: [])

    reply = orch.answer("BRELA ada ya mwaka ni ngapi")

    assert reply.in_scope is True
    assert reply.refused is False
    assert fake.call_count == 1                      # the model WAS called
    assert "TZS 22,000" in reply.text               # its reply reached the output
    assert reply.sub_answers[0].computation is None  # fact path, not compute


def test_retriever_facts_are_injected_into_the_model_prompt():
    fake = FakeBackend(scripted_reply="ok")
    orch = Orchestrator(backend=fake, retriever=lambda q: ["SDL ni 3.5%"])

    orch.answer("SDL ni kiasi gani")  # 'sdl' but no number -> fact path

    assert "SDL ni 3.5%" in fake.last_prompt         # retrieved fact reached the prompt


# --- Out-of-scope question short-circuits BEFORE the model -----------------

def test_out_of_scope_question_short_circuits_before_model():
    fake = FakeBackend(scripted_reply="should never be returned")
    orch = Orchestrator(backend=fake)

    reply = orch.answer("What is the capital gains tax rate?")

    assert reply.in_scope is False
    assert reply.refused is True
    assert reply.text == REFUSAL_TEXT
    assert fake.call_count == 0                       # model never called


# --- Compute question routes to rules_engine and its output reaches reply ---

def test_compute_question_routes_to_rules_engine_and_output_reaches_reply():
    # SDL for 15 employees on a total payroll of TZS 6,750,000 -> 3.5% = 236,250.
    # Backend is called twice: first for slot extraction (JSON), then to format.
    extraction = (
        '{"gross_monthly_payroll": {"value": 6750000, "confidence": "high"}, '
        '"employee_count": {"value": 15, "confidence": "high"}}'
    )
    fake = FakeBackend(replies=[extraction, "Hii ndio hesabu yako ya SDL:"])
    orch = Orchestrator(backend=fake)

    reply = orch.answer("SDL kwa wafanyakazi 15 wenye jumla ya mshahara 6,750,000")

    sub = reply.sub_answers[0]
    assert sub.sub_question.kind == "compute"
    assert sub.needs_clarification is False
    assert sub.computation is not None
    assert sub.computation.computation == "sdl"
    assert sub.computation.amount == Decimal("236250")   # deterministic engine result

    # Both the model persona text AND the authoritative working reach final reply.
    assert "Hii ndio hesabu yako ya SDL" in reply.text
    assert "TZS 236,250" in reply.text
    assert fake.call_count == 2                           # extraction + formatting


def test_compute_below_threshold_returns_not_applicable_working():
    # SDL for 5 employees -> below the 10-employee threshold -> applicable False.
    extraction = (
        '{"gross_monthly_payroll": {"value": 2000000, "confidence": "high"}, '
        '"employee_count": {"value": 5, "confidence": "high"}}'
    )
    fake = FakeBackend(replies=[extraction, ""])
    orch = Orchestrator(backend=fake)

    reply = orch.answer("SDL kwa wafanyakazi 5 wenye mshahara 2,000,000")

    sub = reply.sub_answers[0]
    assert sub.computation.applicable is False
    # Deterministic note surfaced. The copy gained the FIGURE in the Phase D re-run cycle:
    # eval_378 asked "ni ngapi", got a correct 'haihusiki' verdict with no number, and was
    # scored FAIL for it. 'chini ya 10' is the part of the verdict that has not changed.
    assert "TZS 0" in reply.text and "chini ya 10" in reply.text


def test_low_confidence_required_field_routes_to_clarification_not_rules_engine():
    # Extraction returns a required field at LOW confidence -> never guess: the
    # orchestrator must clarify, not call the rules engine or the formatting model.
    from chike.orchestrator import CLARIFICATION_PENDING

    extraction = (
        '{"gross_monthly_payroll": {"value": 6750000, "confidence": "low"}, '
        '"employee_count": {"value": 15, "confidence": "high"}}'
    )
    fake = FakeBackend(replies=[extraction])
    orch = Orchestrator(backend=fake)

    reply = orch.answer("SDL kwa wafanyakazi 15 wenye takribani 6,750,000")

    sub = reply.sub_answers[0]
    assert sub.needs_clarification is True
    assert sub.computation is None                        # rules engine NOT called
    # (copy change) clarifications now render real Swahili copy, not the bare sentinel;
    # detection is via the structured flag.
    assert reply.needs_clarification is True
    assert CLARIFICATION_PENDING not in reply.text
    assert "mshahara" in reply.text.lower()               # it actually asks for the salary figure
    assert fake.call_count == 1                            # extraction only, no formatting


# --- Applicability-vs-amount routing (Finding 1) ---------------------------
# An obligation/threshold question ('am I obligated to pay X?') is answered from the
# rule's threshold (SDL, from headcount) or flat no-threshold rule (NSSF/WCF) WITHOUT a
# salary — recovering a correct deterministic yes/no the amount path would reject.

def test_sdl_applicability_below_threshold_answers_from_headcount_no_salary():
    # eval_121 shape: 8 employees, obligation ask, NO amount ask -> deterministic 'Hapana'
    # from the count alone; the salary the amount path demands is never requested.
    extraction = '{"employee_count": {"value": 8, "confidence": "high"}}'
    fake = FakeBackend(replies=[extraction, "Kwa mujibu wa hesabu:"])
    orch = Orchestrator(backend=fake)

    reply = orch.answer("Je, mwajiri mwenye wafanyakazi 8 ana wajibu wa kulipa SDL?")

    sub = reply.sub_answers[0]
    assert sub.sub_question.kind == "compute"
    assert sub.needs_clarification is False
    assert sub.computation is not None
    assert sub.computation.computation == "sdl"
    assert sub.computation.applicable is False
    assert sub.computation.amount is None                  # applicability answer, no amount
    assert "haihusiki" in reply.text                       # deterministic verdict surfaced
    assert reply.needs_clarification is False


def test_sdl_applicability_at_threshold_answers_yes_from_headcount():
    # eval_368 shape: 12 (part-timers count) -> 'Ndiyo, SDL inatozwa', still no salary needed.
    extraction = '{"employee_count": {"value": 12, "confidence": "high"}}'
    fake = FakeBackend(replies=[extraction, "Ndiyo:"])
    orch = Orchestrator(backend=fake)

    reply = orch.answer(
        "Nina wafanyakazi 12 lakini wote ni wa muda, je bado nafikia kizingiti cha SDL?")

    sub = reply.sub_answers[0]
    assert sub.computation.computation == "sdl"
    assert sub.computation.applicable is True
    assert sub.computation.amount is None
    assert "inatozwa" in reply.text


def test_nssf_applicability_answers_yes_with_no_extraction_call():
    # eval_308 shape: NSSF has no headcount threshold -> answer directly, NO field needed,
    # so the backend is called ONCE (formatting only) — no extraction round-trip.
    fake = FakeBackend(replies=["Ndiyo, NSSF inakuhusu:"])
    orch = Orchestrator(backend=fake)

    reply = orch.answer("Je, kama nina wafanyakazi 8 tu, bado nalazimika kulipa NSSF?")

    sub = reply.sub_answers[0]
    assert sub.computation.computation == "nssf"
    assert sub.computation.applicable is True
    assert "kizingiti" in sub.computation.working.lower()  # 'no headcount threshold' verdict
    assert fake.call_count == 1                            # NO extraction call


def test_wcf_applicability_answers_yes_with_no_extraction_call():
    # eval_311 shape: WCF applies from the first employee; the stated salary is irrelevant.
    fake = FakeBackend(replies=["Ndiyo, WCF inakuhusu:"])
    orch = Orchestrator(backend=fake)

    reply = orch.answer(
        "Nina mfanyakazi mmoja tu anayelipwa TZS 500,000, je bado nachangia WCF?")

    sub = reply.sub_answers[0]
    assert sub.computation.computation == "wcf"
    assert sub.computation.applicable is True
    assert fake.call_count == 1


def test_sdl_applicability_without_a_count_clarifies_for_headcount_not_salary():
    # An SDL obligation question routed to compute (a number is present) but with no usable
    # headcount -> clarify for the COUNT, never for a salary.
    extraction = '{"employee_count": {"value": 0, "confidence": "low"}}'
    fake = FakeBackend(replies=[extraction])
    orch = Orchestrator(backend=fake)

    reply = orch.answer(
        "Nina mshahara wa jumla TZS 5,000,000 kwa wafanyakazi wengi, je nina wajibu "
        "wa kulipa SDL?")

    sub = reply.sub_answers[0]
    assert sub.needs_clarification is True
    assert sub.computation is None                         # rules engine NOT called
    assert "wafanyakazi" in reply.text.lower()             # asks for the COUNT
    assert "mshahara ni shilingi" not in reply.text.lower()  # NOT the salary-ask copy
    assert fake.call_count == 1                            # extraction only


# --- Route-aware merge (ADR 0001 Phase B) ----------------------------------
# An all-fact multi-part message COLLAPSES to a single v15-style whole-question
# generation (decompose -> pool facts -> generate once). This test REPLACES the old
# test_multi_part_question_produces_one_subanswer_per_part, whose `len == 2` /
# `call_count == 2` assertions encoded the very per-fragment generation that caused the
# Q1/Q12 regressions and that Phase B removes — revised openly, not silently.

def test_multi_part_all_fact_collapses_to_single_pass():
    def retr(q):
        if "BRELA" in q:
            return ["BRELA ada ya mwaka ni TZS 22,000"]
        if "NSSF" in q:
            return ["NSSF ni asilimia 20 ya mshahara"]
        return []

    fake = FakeBackend(scripted_reply="jibu moja lililojumuishwa")
    orch = Orchestrator(backend=fake, retriever=retr)

    reply = orch.answer("BRELA ada ni ngapi? NSSF ni asilimia ngapi?")

    # One generation, one sub-answer — the v15 collapse, not per-fragment generation.
    assert fake.call_count == 1
    assert len(reply.sub_answers) == 1
    # Facts from BOTH sub-queries were pooled into the single prompt (v15 retrieval-merge).
    assert "BRELA ada ya mwaka ni TZS 22,000" in fake.last_prompt
    assert "NSSF ni asilimia 20 ya mshahara" in fake.last_prompt
    # The single generation is over the WHOLE original question (not a lone fragment).
    assert fake.last_prompt.rstrip().endswith("BRELA ada ni ngapi? NSSF ni asilimia ngapi?")
    assert reply.text == "jibu moja lililojumuishwa"


def test_empty_generation_triggers_whole_question_fallback():
    # Q1 analog: the structured generation comes back empty; the merge-time guard must
    # re-generate over the whole question and surface THAT, never return an empty reply.
    fake = FakeBackend(replies=["", "Jibu kamili baada ya fallback."])
    orch = Orchestrator(backend=fake, retriever=lambda q: [])

    reply = orch.answer("BRELA ada ni ngapi?")

    assert reply.text == "Jibu kamili baada ya fallback."   # guard rescued the empty result
    assert reply.text.strip() != ""
    assert fake.call_count == 2                              # primary (empty) + fallback


def test_fabricated_followup_turn_is_cleaned_in_single_pass():
    # Q12 analog: one generation, cleaned once. The model rambles into a fabricated
    # follow-up Q&A turn ('\n\nSwali: ...'); the single-pass clean truncates it.
    ramble = (
        "NSSF ni asilimia 20 ya mshahara ghafi. Thibitisha na NSSF (nssf.go.tz)."
        "\n\nSwali: Je, nikichelewa kulipa NSSF adhabu ni ipi?"
        "\nJibu: Faini ya kubuni ambayo mfano haupaswi kuiamini."
    )
    fake = FakeBackend(scripted_reply=ramble)
    orch = Orchestrator(backend=fake, retriever=lambda q: ["NSSF ni 20%"])

    reply = orch.answer("NSSF inalipwaje?")

    assert fake.call_count == 1                              # ONE generation (v15 shape)
    assert len(reply.sub_answers) == 1
    assert reply.text == "NSSF ni asilimia 20 ya mshahara ghafi. Thibitisha na NSSF (nssf.go.tz)."
    assert "kubuni" not in reply.text                        # fabricated follow-up removed
    assert "Swali:" not in reply.text


def test_mixed_compute_and_fact_keeps_two_distinct_sources():
    # THE load-bearing regression guard (scope s2): a compound message with a compute part
    # AND a fact part must keep them as TWO sub-answers from TWO sources — the compute part
    # through the deterministic rules engine (authoritative working), the fact part through
    # RAG+model. It must fail LOUDLY if a future change collapses the compute part into the
    # pooled fact generation (then there would be no computation object / no verified figure).
    from chike import routing

    q = ("Nihesabie SDL kwa wafanyakazi 15 wenye jumla ya mshahara 6,750,000? "
         "Je, kama mgeni naruhusiwa kufanya biashara ya rejareja?")
    compute_part = "Nihesabie SDL kwa wafanyakazi 15 wenye jumla ya mshahara 6,750,000?"
    fact_part = "Je, kama mgeni naruhusiwa kufanya biashara ya rejareja?"
    # Preconditions: the parts route to opposite paths.
    assert routing.detect_intent(compute_part) == "sdl"
    assert routing.detect_intent(fact_part) == "none"

    extraction = (
        '{"gross_monthly_payroll": {"value": 6750000, "confidence": "high"}, '
        '"employee_count": {"value": 15, "confidence": "high"}}'
    )
    fake = FakeBackend(replies=[extraction, "Hii ndio hesabu yako ya SDL:",
                                "Kwa GN487A, biashara ya rejareja imezuiliwa kwa wasio raia."])
    orch = Orchestrator(backend=fake, retriever=lambda q: [])

    reply = orch.answer(q)

    compute_subs = [s for s in reply.sub_answers if s.computation is not None]
    fact_subs = [s for s in reply.sub_answers
                 if s.computation is None and not s.needs_clarification]
    assert len(reply.sub_answers) == 2
    # LOUD guard: the compute part is NOT collapsed into the pooled fact generation.
    assert len(compute_subs) == 1, "compute part must stay a rules-engine sub-answer, not fold into fact"
    assert len(fact_subs) == 1
    assert compute_subs[0].computation.computation == "sdl"
    assert compute_subs[0].computation.amount == Decimal("236250")   # deterministic engine
    assert "TZS 236,250" in reply.text                               # authoritative working survives
    assert "GN487A" in reply.text                                     # fact source survives
    assert fake.call_count == 3            # extract + compute-format + one pooled fact gen


def test_multi_compute_parts_are_not_collapsed():
    # Two compute questions in one message -> two rules-engine sub-answers, each with its
    # OWN authoritative figure. Proves compute parts are never pooled into a single
    # generation (the enumeration/"A, B na C" path routes into exactly this shape).
    sdl_extract = (
        '{"gross_monthly_payroll": {"value": 6750000, "confidence": "high"}, '
        '"employee_count": {"value": 15, "confidence": "high"}}'
    )
    nssf_extract = '{"gross_monthly_payroll": {"value": 800000, "confidence": "high"}}'
    fake = FakeBackend(replies=[sdl_extract, "Hesabu ya SDL", nssf_extract, "Hesabu ya NSSF"])
    orch = Orchestrator(backend=fake, retriever=lambda q: [])

    reply = orch.answer(
        "Nihesabie SDL kwa wafanyakazi 15 wenye mshahara 6,750,000? "
        "Nihesabie NSSF kwa mshahara 800,000?")

    assert len(reply.sub_answers) == 2
    computed = [s.computation.computation for s in reply.sub_answers if s.computation]
    assert len(computed) == 2, "both compute parts must keep their own generation"
    assert set(computed) == {"sdl", "nssf"}
    assert fake.call_count == 4            # (extract + format) x 2, no fact pooling


# --- D-DECOMP-1: multi-levy compute fan-out --------------------------------
# A compute part that NAMES several levies ("...SDL na NSSF...") used to compute only the
# first (detect_intent -> _explicit_levy) and silently drop the rest (eval_318 lost NSSF).
# all_explicit_levies + _fan_out_multi_levy expand it into one compute per named levy.

def test_all_explicit_levies_lists_every_named_levy_in_order():
    from chike import routing
    assert routing.all_explicit_levies("nataka kujua SDL na NSSF") == ["sdl", "nssf"]
    assert routing.all_explicit_levies("SDL, NSSF, PAYE na WCF kwa mfanyakazi") == [
        "sdl", "nssf", "paye", "wcf"]
    assert routing.all_explicit_levies("PAYE yake ni ngapi") == ["paye"]      # single
    assert routing.all_explicit_levies("je nasajili VAT?") == []              # no compute levy


def test_fan_out_expands_multi_levy_leaves_others_identical():
    from chike.orchestrator import SubQuestion, Orchestrator
    routed = [
        SubQuestion(text="wafanyakazi 11 mishahara 5,500,000 SDL na NSSF", kind="compute",
                    computation_type="sdl"),
        SubQuestion(text="je nasajili VAT?", kind="fact"),
    ]
    fanned = Orchestrator._fan_out_multi_levy(routed)
    # the multi-levy compute part became two computes (sdl, then nssf), in order
    assert [(s.kind, s.computation_type) for s in fanned] == [
        ("compute", "sdl"), ("compute", "nssf"), ("fact", None)]
    # the fact SubQuestion is the SAME object (untouched)
    assert fanned[2] is routed[1]
    # a routed list with no multi-levy part is returned byte-identically (same objects)
    single = [SubQuestion(text="SDL yangu?", kind="compute", computation_type="sdl"),
              SubQuestion(text="VAT?", kind="fact")]
    assert Orchestrator._fan_out_multi_levy(single) == single


def test_multi_levy_part_computes_each_levy_plus_fact_survives():
    # eval_318 shape: "...SDL na NSSF?" (compute, two levies) + "...VAT?" (fact). All three
    # sub-answers must survive: SDL and NSSF each with their OWN authoritative working, and the
    # VAT fact — NSSF is no longer dropped. Phase B invariant intact (2 compute subs + 1 fact).
    sdl_extract = ('{"gross_monthly_payroll": {"value": 5500000, "confidence": "high"}, '
                   '"employee_count": {"value": 11, "confidence": "high"}}')
    nssf_extract = '{"gross_monthly_payroll": {"value": 5500000, "confidence": "high"}}'
    fake = FakeBackend(replies=[sdl_extract, "Hesabu ya SDL:", nssf_extract, "Hesabu ya NSSF:",
                                "Ndiyo, unatakiwa kusajili VAT."])
    orch = Orchestrator(backend=fake, retriever=lambda q: [])

    reply = orch.answer(
        "Nina wafanyakazi 11 wenye mishahara TZS 5,500,000 — SDL na NSSF? "
        "Je nasajili VAT kama mapato ni TZS 205,000,000?")

    compute_subs = [s for s in reply.sub_answers if s.computation is not None]
    fact_subs = [s for s in reply.sub_answers
                 if s.computation is None and not s.needs_clarification]
    assert [s.computation.computation for s in compute_subs] == ["sdl", "nssf"]
    assert len(fact_subs) == 1, "the VAT fact part must survive alongside the two computes"
    assert compute_subs[0].computation.amount == Decimal("192500")     # SDL 3.5% x 5,500,000
    assert compute_subs[1].computation.amount == Decimal("1100000")    # NSSF 20% x 5,500,000
    assert "TZS 192,500" in reply.text
    assert "TZS 1,100,000" in reply.text                               # NSSF no longer dropped
    assert "VAT" in reply.text
    assert fake.call_count == 5            # (extract+format) x 2 computes + 1 pooled fact gen


# --- Real-weights confirmation (Phase D Stage 1) ---------------------------
# These drive the ACTUAL v15 adapter over the raw generate_endpoint (LocalAdapter),
# with the AfriqueLlama tokenizer loaded so prompts are byte-identical to production
# (Stage 0 fix). They are env-gated: with no Modal token available the whole block
# SKIPS, so the offline suite stays green and reproducible. Set CHIKE_MODAL_TOKEN
# (or place the token in ~/.chike_modal_token.txt) to run them for real.
#
# What they gate (ADR 0001 Phase D Stage 1). Stage 1's first run showed the LLM backstop
# was inert on real weights (it answered in prose instead of emitting routing JSON) and the
# fact path fabricated a number (rc_22 -> "PAYE TZS 4,000" with no salary). The backstop was
# retired in favour of a deterministic router extension + a fabrication guard; these tests
# now confirm THOSE mechanisms on real weights:
#   - test_net_take_home_routed_to_compute_and_never_guesses_on_real_weights (rc_11): the
#     router's net-take-home extension routes to compute deterministically; the extractor's
#     RC-3 gross/net veto ('mkononi') then never-guesses -> a clarification, never a fabricated
#     take-home. (Whether to relax RC-3 for a 'mshahara'-labelled figure is an open decision.)
#   - test_fabrication_guard_never_guesses_on_real_weights (rc_22): a payroll amount with the
#     salary MISSING hits the fabrication guard -> clarification, NEVER a fabricated number.
#   - test_q1_q12_regressions_resolved_on_real_weights: the Phase B route-aware merge,
#     on real weights, produces NON-EMPTY output for Q1 (was empty) and Q12 (was
#     empty + hallucinated follow-up turns).
#   - test_mixed_compound_end_to_end_on_real_weights: a mixed compute+fact compound
#     keeps two distinct sources end-to-end (a real computed number AND a fact answer).

GENERATE_ENDPOINT = (
    "https://prosperpiusmbaruku007--chike-inference-generate-endpoint.modal.run"
)
ADAPTER_REPO = "prospAprospA007/africa-giants-adapter-v15"


def _real_modal_token():
    """Token from env, else ~/.chike_modal_token.txt. Never logged. None if absent."""
    for k in ("CHIKE_MODAL_TOKEN", "MODAL_API_TOKEN"):
        v = os.environ.get(k)
        if v:
            return v.strip()
    path = os.path.expanduser("~/.chike_modal_token.txt")
    if os.path.exists(path):
        tok = open(path, encoding="utf-8").read().strip()
        return tok or None
    return None


_HAVE_REAL_WEIGHTS = _real_modal_token() is not None
_real_weights = pytest.mark.skipif(
    not _HAVE_REAL_WEIGHTS,
    reason="Phase D real-weights test: no Modal token (set CHIKE_MODAL_TOKEN or "
    "~/.chike_modal_token.txt). The offline suite skips this block.",
)


def _real_orchestrator():
    """Orchestrator wired to the REAL v15 model via LocalAdapter -> generate_endpoint,
    with the AfriqueLlama tokenizer loaded (CPU) so prompts match production byte-for-byte
    (Stage 0). Uses the real RAG retriever (default) — the same facts v15 serves."""
    from transformers import AutoTokenizer
    from chike.model_abstraction import LocalAdapter

    tok = AutoTokenizer.from_pretrained(ADAPTER_REPO, trust_remote_code=True)
    endpoint = os.environ.get("CHIKE_RAW_ENDPOINT") or GENERATE_ENDPOINT
    backend = LocalAdapter(endpoint_url=endpoint, token=_real_modal_token(), tokenizer=tok)
    return Orchestrator(backend=backend)  # real retriever (default_retrieve)


def _computations(reply):
    return [s.computation for s in reply.sub_answers if s.computation is not None]


@_real_weights
def test_net_take_home_routed_to_compute_and_never_guesses_on_real_weights():
    # rc_11: net-of-PAYE take-home ("...mshahara wa mwezi ni milioni moja na nusu ...
    # kitakachobaki mkononi baada ya kodi ya mshahara"). The router's net-take-home extension
    # routes this to compute DETERMINISTICALLY; the extractor's RC-3 gross/net veto ('mkononi')
    # then never-guesses -> a CLARIFICATION, never a fabricated fact-path number. (This outcome
    # is deterministic; the real backend must never turn it into a guessed figure.)
    orch = _real_orchestrator()
    reply = orch.answer(
        "Mshahara wangu wa mwezi ni milioni moja na nusu. Nataka kujua "
        "kitakachobaki mkononi baada ya kodi ya mshahara."
    )
    print("\n[rc_11] text:\n" + reply.text)
    sub = reply.sub_answers[0]
    assert sub.sub_question.kind == "compute"             # router extension routed it to compute
    assert sub.computation is None                         # never-guess on the gross/net ambiguity
    assert sub.needs_clarification is True                 # clarify, not a fabricated take-home


@_real_weights
def test_fabrication_guard_never_guesses_on_real_weights():
    # rc_22: a payroll amount with NO salary given ("Nina duka lenye wafanyakazi wanne.
    # Makato ya mshahara ninayotakiwa kulipa kila mwezi ni kiasi gani?"). The fabrication
    # guard must force a clarification (R8) — never a fabricated number.
    orch = _real_orchestrator()
    reply = orch.answer(
        "Nina duka lenye wafanyakazi wanne. Makato ya mshahara ninayotakiwa "
        "kulipa kila mwezi ni kiasi gani?"
    )
    print("\n[rc_22] text:\n" + reply.text)
    assert not _computations(reply), (
        "never-guess violated: a computation ran with no salary provided — "
        f"{[c.computation for c in _computations(reply)]}")
    assert any(s.needs_clarification for s in reply.sub_answers), \
        "expected the fabrication guard to clarify (missing salary), not answer"


@_real_weights
def test_q1_q12_regressions_resolved_on_real_weights():
    orch = _real_orchestrator()
    # Q1 (was empty output): single GN 487A fact — non-citizen salon restriction.
    q1 = ("Mimi ni mgeni na nataka kufungua saluni Arusha, nina mtaji wa milioni 80, "
          "naruhusiwa kufanya hivyo?")
    r1 = orch.answer(q1)
    print("\n[Q1] text:\n" + r1.text)
    assert r1.text.strip(), "Q1 regressed: empty output (the original v16 bug)"
    assert not r1.needs_clarification                      # a fact answer, not a clarification
    assert r1.refused is False

    # Q12 (was empty + hallucinated follow-up turns): two-part fact — NSSF vs SDL.
    q12 = ("Kuna aina mbili za makato ya wafanyakazi ninazosikia watu wakizungumza, "
           "ni kitu kimoja au tofauti? Mwajiri analipa vyote viwili?")
    r12 = orch.answer(q12)
    print("\n[Q12] text:\n" + r12.text)
    assert r12.text.strip(), "Q12 regressed: empty output (the original v16 bug)"
    # No fabricated multi-turn dialogue: the cleaned reply must not spawn extra Q/A turns.
    for marker in ("Swali:", "Jibu:", "Mtumiaji:", "Mteja:"):
        assert r12.text.count(marker) <= 1, f"fabricated follow-up turn ({marker!r})"


@_real_weights
def test_mixed_compound_end_to_end_on_real_weights():
    # Mixed compute+fact: SDL computation AND a BRELA annual-fee fact must both survive
    # the route-aware merge as two distinct sources (Phase B structural guarantee). Uses a
    # two-'?' phrasing that decomposes cleanly into [compute SDL] + [fact BRELA] — the same
    # structure as the offline test_mixed_compute_and_fact_keeps_two_distinct_sources. (A
    # single-'?' 'Pia,'-joined phrasing does NOT decompose and collapses to one compute part,
    # which also corrupts the SDL extraction — a decomposition-coverage gap tracked separately.)
    orch = _real_orchestrator()
    reply = orch.answer(
        "Nihesabie SDL kwa wafanyakazi 15 wenye jumla ya mshahara milioni 12 "
        "kwa mwezi? Je, ada ya BRELA ya mwaka ni ngapi?"
    )
    print("\n[mixed] text:\n" + reply.text)
    comps = _computations(reply)
    assert any(c.computation == "sdl" for c in comps), \
        f"expected an SDL computation, got {[c.computation for c in comps]}"
    assert len(reply.sub_answers) >= 2, "compute and fact must remain two distinct sources"
    assert reply.text.strip()


# --- Dependency injection: production backends are drop-in ------------------

def test_orchestrator_accepts_any_modelbackend():
    from chike.model_abstraction import ModelBackend

    class RecordingBackend(ModelBackend):
        def generate(self, prompt, params=None):
            return "custom"

    orch = Orchestrator(backend=RecordingBackend(), retriever=lambda q: [])
    reply = orch.answer("VAT ni ngapi")
    assert reply.text == "custom"


# --- Real retriever is the default, and injection still overrides it --------

def test_default_retriever_is_the_real_v15_retrieve_function():
    import chike.retrieval as retrieval

    orch = Orchestrator(backend=FakeBackend())
    # Wired, but NOT invoked here — so no e5 model/index load happens.
    assert orch.retriever is retrieval.retrieve


def test_validate_stage_strips_ramble_from_fact_reply():
    ramble = (
        "SDL ni asilimia 3.5 ya mishahara ghafi. Thibitisha na TRA (tra.go.tz)."
        "<|eot_id|><|start_header_id|>user<|end_header_id|>\n\nSwali jingine la kubuni?"
    )
    fake = FakeBackend(scripted_reply=ramble)
    orch = Orchestrator(backend=fake, retriever=lambda q: ["SDL ni 3.5%"])

    reply = orch.answer("SDL ni ngapi")

    assert reply.text == "SDL ni asilimia 3.5 ya mishahara ghafi. Thibitisha na TRA (tra.go.tz)."
    assert "kubuni" not in reply.text          # fabricated follow-up turn removed
    assert "<|" not in reply.text               # residual special tokens stripped


def test_fact_prompt_uses_production_rag_wrapper():
    fake = FakeBackend(scripted_reply="ok")
    orch = Orchestrator(
        backend=fake,
        retriever=lambda q: ["SDL ni 3.5%"],
        system_prompt="Wewe ni Chike.",
    )
    orch.answer("SDL ni ngapi")

    prompt = fake.last_prompt
    # FakeBackend exposes no .tokenizer, so build_chat_prompt uses the naive-concat
    # fallback (a real GPU backend would route through apply_chat_template instead).
    # System prompt + UKWELI block + '- ' fact + the question are all present; the old
    # hardcoded Llama-3 header tokens are NOT (the model was never trained to stop after
    # them — see chike/prompting.py).
    assert "Wewe ni Chike." in prompt
    assert "UKWELI ULIOTHIBITISHWA KWA SWALI HILI:" in prompt
    assert "- SDL ni 3.5%" in prompt
    # Unpunctuated question gains a terminal '?' (Defect B) before the prompt is built.
    assert prompt.rstrip().endswith("SDL ni ngapi?")
    assert "<|begin_of_text|>" not in prompt and "<|start_header_id|>" not in prompt


def test_fact_prompt_routes_through_apply_chat_template_when_backend_has_tokenizer():
    # Stage 0 / Finding D-1: when the real backend exposes .tokenizer, build_chat_prompt must
    # use apply_chat_template (byte-identical to modal_app.run()/production), NOT the naive-concat
    # fallback. The prior test above pins the no-tokenizer fallback; this pins the parity path.
    class StubTokenizer:
        def apply_chat_template(self, messages, tokenize=False, add_generation_prompt=True):
            return "CHAT_TEMPLATE::" + "|".join(m["role"] for m in messages)

    class TokenizerBackend(FakeBackend):
        tokenizer = StubTokenizer()

    fake = TokenizerBackend(scripted_reply="ok")
    orch = Orchestrator(backend=fake, retriever=lambda q: ["SDL ni 3.5%"],
                        system_prompt="Wewe ni Chike.")
    orch.answer("SDL ni ngapi")

    # apply_chat_template was used (its marker), and the naive-concat shape was NOT produced.
    assert fake.last_prompt == "CHAT_TEMPLATE::system|user"
    assert "UKWELI" not in fake.last_prompt   # naive fallback would inline the facts block here


def test_injected_retriever_overrides_the_real_default():
    calls = []

    def stub(q):
        calls.append(q)
        return ["injected fact"]

    fake = FakeBackend(scripted_reply="ok")
    orch = Orchestrator(backend=fake, retriever=stub)
    orch.answer("BRELA ada ni ngapi")

    assert calls == ["BRELA ada ni ngapi"]                # stub used, not real retrieval
    assert "injected fact" in fake.last_prompt


# --- Net-take-home router extension + fabrication guard --------------------
# These REPLACE the retired extractor-emitted-intent backstop (which only ever proved
# wiring against a scripted FakeBackend and then failed its first real-weights test).
# rc_11 is now recovered deterministically by the router; rc_22 is a never-guess clarify
# via the fabrication guard — no model call, no scripted JSON, fully offline.

def test_net_take_home_routes_to_compute_then_never_guesses_gross_net():
    from chike import routing
    from chike.orchestrator import CLARIFICATION_PENDING

    # rc_11: the router's net-take-home extension routes this to compute (paye)
    # DETERMINISTICALLY — replacing the retired LLM backstop. The extractor's existing RC-3
    # gross/net veto then fires ('mkononi' makes the stated 1.5M gross-or-net ambiguous), so
    # the never-guess contract yields a CLARIFICATION rather than a possibly-wrong take-home.
    # This is strictly safer than the retired backstop (which produced a degenerate non-answer)
    # and is fully deterministic. See the report: whether to relax RC-3 for a figure explicitly
    # labelled 'mshahara' is a separate, open decision.
    q = ("Mshahara wangu wa mwezi ni milioni moja na nusu. Nataka kujua kitakachobaki "
         "mkononi baada ya kodi ya mshahara.")
    assert routing.detect_intent(q) == "paye"            # router extension routed it to compute

    fake = FakeBackend(scripted_reply="{}")              # extract probe; value is deterministic
    orch = Orchestrator(backend=fake, retriever=lambda q: [])
    reply = orch.answer(q)
    sub = reply.sub_answers[0]
    assert sub.sub_question.kind == "compute"            # routed to compute (not fact, not fabricated)
    assert sub.sub_question.computation_type == "paye"
    assert sub.computation is None                        # never-guess: rules engine NOT handed an ambiguous base
    assert sub.needs_clarification is True
    # (copy change) renders reason-aware gross/net clarification copy, not the bare sentinel.
    assert reply.needs_clarification is True
    assert CLARIFICATION_PENDING not in reply.text
    assert "ghafi" in reply.text.lower() or "mkononi" in reply.text.lower()
    assert fake.call_count == 1                           # one extract probe, no formatting/fabrication call


def test_fabrication_guard_clarifies_without_calling_the_model():
    from chike.orchestrator import CLARIFICATION_PENDING
    from chike import clarification

    # rc_22: a payroll-levy AMOUNT asked with no salary given. The fact path must NOT be
    # allowed to fabricate a number — the guard returns a clarification and the model
    # (and retriever) are never even called.
    q = ("Nina duka lenye wafanyakazi wanne. Makato ya mshahara ninayotakiwa kulipa "
         "kila mwezi ni kiasi gani?")
    calls = []
    fake = FakeBackend(scripted_reply="SHOULD NOT BE CALLED")
    orch = Orchestrator(backend=fake, retriever=lambda q: calls.append(q) or [])

    reply = orch.answer(q)
    sub = reply.sub_answers[0]
    assert sub.needs_clarification is True
    assert sub.computation is None                         # never a computed number
    # (copy change) renders the shared PAYROLL_AMOUNT clarification, not the bare sentinel.
    assert reply.needs_clarification is True
    assert CLARIFICATION_PENDING not in reply.text
    assert reply.text == clarification.PAYROLL_AMOUNT
    assert fake.call_count == 0                            # model NEVER called — no fabrication possible
    assert calls == []                                    # retrieval skipped too


# --- R14 stop_strings resolution (2026-08-06) --------------------------------
# _validate_and_clean used to call clean_reply(text) with no stop_strings, relying on
# generation_cleanup's module default. That default equals config's list today, so it was a
# behavioural no-op -- but a config-only edit to generation_params.stop_strings would have
# reached production (modal_app passes STOP_STRINGS) and the gate (eval.py passes STOP_STRINGS)
# and NOT the v16 clean stage. These lock the explicit resolution.

def test_stop_strings_default_to_the_config_list():
    import json as _json
    import os as _os

    from chike.orchestrator import Orchestrator as _Orch
    from chike.model_abstraction import FakeBackend as _Fake

    root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
    with open(_os.path.join(root, "kaggle", "chike_config.json"), encoding="utf-8") as fh:
        expected = _json.load(fh)["generation_params"]["stop_strings"]

    orch = _Orch(backend=_Fake("jibu"))
    assert list(orch.stop_strings) == list(expected)


def test_gen_params_stop_strings_override_the_config():
    from chike.orchestrator import Orchestrator as _Orch
    from chike.model_abstraction import FakeBackend as _Fake

    orch = _Orch(backend=_Fake("jibu"), gen_params={"stop_strings": ["\n\nSTOP"]})
    assert list(orch.stop_strings) == ["\n\nSTOP"]


def test_clean_stage_actually_applies_the_resolved_stop_strings():
    # The point of the fix: a custom stop string must truncate the model's reply. With the
    # old implicit default this reply would have come back whole.
    from chike.orchestrator import Orchestrator as _Orch
    from chike.model_abstraction import FakeBackend as _Fake

    orch = _Orch(
        backend=_Fake("Jibu halisi hapa.\n\nZZZKATA rubbish tail"),
        retriever=lambda q: ("ukweli",),
        gen_params={"stop_strings": ["\n\nZZZKATA"]},
    )
    reply = orch.answer("Kiwango cha SDL ni asilimia ngapi?")
    assert "ZZZKATA" not in reply.text
    assert reply.text.startswith("Jibu halisi hapa.")
