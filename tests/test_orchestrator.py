"""Tests for chike.orchestrator — pipeline shape + dependency injection.

Every test injects a FakeBackend (no network, no GPU), proving the orchestrator is
fully exercisable via the model abstraction layer built in item 1.
"""
from decimal import Decimal

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


# --- Decomposition produces one sub-answer per part ------------------------

def test_multi_part_question_produces_one_subanswer_per_part():
    fake = FakeBackend(scripted_reply="jibu")
    orch = Orchestrator(backend=fake, retriever=lambda q: [])

    reply = orch.answer("BRELA ada ni ngapi? NSSF ni asilimia ngapi?")

    assert len(reply.sub_answers) == 2
    assert fake.call_count == 2


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
    # System prompt + UKWELI block + '- ' fact + Llama chat scaffolding all present.
    assert prompt.startswith("<|begin_of_text|><|start_header_id|>system")
    assert "Wewe ni Chike." in prompt
    assert "UKWELI ULIOTHIBITISHWA KWA SWALI HILI:" in prompt
    assert "- SDL ni 3.5%" in prompt
    assert prompt.rstrip().endswith("<|start_header_id|>assistant<|end_header_id|>")


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
