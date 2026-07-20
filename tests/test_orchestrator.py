"""Tests for chike.orchestrator — pipeline shape + dependency injection.

Every test injects a FakeBackend (no network, no GPU), proving the orchestrator is
fully exercisable via the model abstraction layer built in item 1.
"""
from decimal import Decimal

import pytest

from chike.orchestrator import Orchestrator, REFUSAL_TEXT
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
    assert "haihusiki" in reply.text                      # deterministic note surfaced


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
    assert reply.text == CLARIFICATION_PENDING
    assert fake.call_count == 1                            # extraction only, no formatting


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
    # Preconditions: the parts route to opposite paths, and the fact part does NOT trip the
    # backstop gate (no number, no payroll cue) — so it consumes no extra model call.
    assert routing.detect_intent(compute_part) == "sdl"
    assert routing.detect_intent(fact_part) == "none"
    assert routing.invoke_extractor(fact_part) is False

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


# --- GPU-deferred (Phase D, real weights) — NOT run here -------------------
# These require the real v15 adapter on GPU; they are the real-weights confirmation that
# the offline plumbing above holds with actual model output. Marked skip so they are
# visibly present but never executed in the offline suite (ADR 0001 Phase D).

@pytest.mark.skip(reason="Phase D — GPU, real weights: re-run Q1/Q12 from the 20-question A/B set")
def test_q1_q12_regressions_resolved_on_real_weights():
    ...


@pytest.mark.skip(reason="Phase D — GPU, real weights: mixed compute+fact end-to-end")
def test_mixed_compound_end_to_end_on_real_weights():
    ...


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
    assert prompt.rstrip().endswith("SDL ni ngapi")
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


# --- Extractor-emitted-intent backstop (ADR 0001 Phase A) ------------------
# The deterministic router (chike.routing) abstains on these, the invoke gate fires, and a
# scripted FakeBackend stands in for the real model's {intent, fields} output. These prove
# the PLUMBING only (Phase D validates the real model's judgment on GPU).

def test_backstop_recovers_compute_intent_the_deterministic_router_missed():
    from chike import routing

    q = "Mfanyakazi wangu ana mshahara wa milioni mbili kwa mwezi."
    # Precondition: deterministic router abstains (no money-'how-much' cue) but the gate fires.
    assert routing.detect_intent(q) == "none"
    assert routing.invoke_extractor(q) is True

    intent_json = '{"intent": "paye", "monthly_salary": {"value": 2000000, "confidence": "high"}}'
    fake = FakeBackend(replies=[intent_json, "Jibu lako la PAYE:"])
    orch = Orchestrator(backend=fake, retriever=lambda q: [])

    reply = orch.answer(q)
    sub = reply.sub_answers[0]
    assert sub.sub_question.kind == "compute"            # backstop re-routed fact -> compute
    assert sub.sub_question.computation_type == "paye"
    assert sub.computation is not None                    # rules engine actually ran
    assert sub.computation.computation == "paye"
    assert fake.call_count == 2                            # ONE intent call + one formatting call


def test_backstop_declines_to_fact_when_model_says_none():
    q = "Nina wafanyakazi kadhaa dukani, nauliza kuhusu mishahara yao."
    fake = FakeBackend(replies=['{"intent": "none"}', "Jibu la ukweli."])
    orch = Orchestrator(backend=fake, retriever=lambda q: [])

    reply = orch.answer(q)
    sub = reply.sub_answers[0]
    assert sub.sub_question.kind == "fact"                # stayed on the fact path
    assert sub.computation is None
    assert reply.text == "Jibu la ukweli."
    assert fake.call_count == 2                            # intent call + fact generation


def test_backstop_preserves_never_guess_on_missing_required_field():
    from chike.orchestrator import CLARIFICATION_PENDING

    # Missing salary: the model emits a compute intent but supplies no amount -> the extraction
    # is unusable -> clarify. The rules engine must NOT be handed a guessed value.
    q = ("Nina duka lenye wafanyakazi wanne. Makato ya mshahara ninayotakiwa kulipa "
         "kila mwezi ni kiasi gani?")
    fake = FakeBackend(replies=['{"intent": "nssf"}'])     # intent only, no fields
    orch = Orchestrator(backend=fake, retriever=lambda q: [])

    reply = orch.answer(q)
    sub = reply.sub_answers[0]
    assert sub.needs_clarification is True
    assert sub.computation is None                         # rules engine NOT called
    assert reply.text == CLARIFICATION_PENDING
    assert fake.call_count == 1                             # intent call only, no formatting
