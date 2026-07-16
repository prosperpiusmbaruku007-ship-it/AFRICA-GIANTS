"""Orchestrator — the shared pipeline skeleton that turns a user question into a reply.

Pipeline shape (this module proves the *shape* and the dependency-injection pattern;
several stages are deliberately thin stubs until their own build items land):

    classify (out-of-scope check)
      -> decompose (multi-part question splitting)
        -> for each sub-question:
            route -> fact-lookup path OR compute path
              fact-lookup: retrieve facts   (STUB retriever — wire real RAG later)
              compute:     call rules_engine (COMPLETE — already built and tested)
            -> generate reply via a ModelBackend (FakeBackend in tests)
            -> validate                       (STUB — fidelity check is a later item)
          -> merge sub-answers into the final reply

Dependency injection is the whole point: the orchestrator is handed a ModelBackend
at construction, so tests inject FakeBackend (no network, no GPU) and production
wires in LocalAdapter or FrontierAPI. Nothing here imports a model directly.

Design invariant carried from the rules engine: arithmetic is NEVER trusted to the
language model. The compute path's authoritative figure is the deterministic
ComputationResult.working, which is carried on the SubAnswer and rendered verbatim
into the final reply — the model only supplies Swahili persona around it.
"""

import dataclasses
import re
from dataclasses import dataclass
from typing import Callable, Optional, Sequence

from . import rules_engine
from .rules_engine.results import ComputationResult
from .model_abstraction import ModelBackend
from .extraction import SlotExtractor, REQUIRED_FIELDS
from .retrieval import retrieve as default_retrieve
from . import prompting
from . import generation_cleanup
from . import decomposition

# --- Stage-level configuration (thin stubs; real lists live in chike_config.json) ---

# Minimal out-of-scope markers. Production uses the full ooc_phrases list (R11);
# this subset is enough to prove the short-circuit before the model is called.
DEFAULT_OOC_PHRASES = (
    "capital gain", "faida ya mtaji", "import duty", "ushuru wa forodha",
    "transfer pricing", "stamp duty", "mining royalt", "zanzibar",
)

# Keyword -> rules_engine computation type. A sub-question mentioning one of these
# AND containing a number is routed to the deterministic compute path.
_COMPUTE_KEYWORDS = {
    "sdl": "sdl",
    "nssf": "nssf",
    "paye": "paye",
    "wcf": "wcf",
}

REFUSAL_TEXT = (
    "Samahani, swali hili liko nje ya maarifa yangu. "
    "Tafadhali thibitisha na TRA."
)

# TODO: requires real ambiguous-phrasing test data — see PROGRESS.md milestone 5 gap.
# Clarification response phrasing is intentionally unwritten. This sentinel lets the
# never-guess routing contract be exercised in tests without inventing user-facing copy.
CLARIFICATION_PENDING = "<CLARIFICATION_NEEDED>"


@dataclass(frozen=True)
class SubQuestion:
    """One atomic question after decomposition, with its routing decision.

    `kind` is 'compute' or 'fact'. For 'compute', `computation_type` names the
    rules_engine calculation; the field VALUES are resolved later by the slot
    extractor, not stored here.
    """

    text: str
    kind: str                                   # 'compute' | 'fact'
    computation_type: Optional[str] = None


@dataclass(frozen=True)
class SubAnswer:
    """The answer to one sub-question.

    `text` is the model's Swahili reply (post-clean). `raw_text` is the model's
    generation BEFORE clean_reply ran — kept so a future clean_reply change can be
    rescored offline against saved data instead of forcing a fresh GPU run. Empty
    until the validate/clean stage populates it (clarification/refusal paths never
    call the model, so their raw_text stays ""). `computation` is the authoritative
    deterministic result when this went down the compute path (None otherwise) —
    it, not the model text, is the source of truth for any number.
    """

    sub_question: SubQuestion
    text: str
    raw_text: str = ""
    facts: tuple = ()
    computation: Optional[ComputationResult] = None
    needs_clarification: bool = False


@dataclass(frozen=True)
class Reply:
    """Final orchestrator output for one user question."""

    question: str
    in_scope: bool
    refused: bool
    text: str
    raw_text: str = ""
    sub_answers: tuple = ()


class Orchestrator:
    """Runs the classify -> decompose -> route -> generate -> validate -> merge pipeline.

    Args:
        backend: the injected ModelBackend. Tests pass FakeBackend; production
            passes LocalAdapter or FrontierAPI. This is the entire reason the
            model abstraction layer (item 1) exists.
        retriever: fact-lookup — callable(question) -> sequence of fact strings.
            Defaults to the real v15 RAG retrieval (chike.retrieval.retrieve, e5-base
            + the 210-fact index). Tests inject a stub the same way they inject
            FakeBackend; dependency injection is preserved.
        ooc_phrases: out-of-scope markers for the classifier stub.
        gen_params: generation params forwarded to backend.generate().
    """

    def __init__(
        self,
        backend: ModelBackend,
        retriever: Optional[Callable[[str], Sequence[str]]] = None,
        ooc_phrases: Sequence[str] = DEFAULT_OOC_PHRASES,
        gen_params: Optional[dict] = None,
        extractor: Optional[SlotExtractor] = None,
        system_prompt: Optional[str] = None,
    ):
        self.backend = backend
        # Default to the real v15 retrieval; an injected retriever overrides it.
        self.retriever = retriever if retriever is not None else default_retrieve
        self.ooc_phrases = tuple(p.lower() for p in ooc_phrases)
        self.gen_params = gen_params
        # Slot extractor shares the injected backend by default (same DI contract).
        self.extractor = extractor or SlotExtractor(backend, gen_params)
        # Chike system prompt (R14) for the generate-stage RAG wrapper.
        self.system_prompt = (
            system_prompt if system_prompt is not None else prompting.load_system_prompt()
        )

    # --- Stage 1: classify -------------------------------------------------

    def classify(self, question: str) -> bool:
        """Return True if the question is in scope. STUB: phrase match only.

        Real classifier (R11) lives at the Modal edge with the full phrase lists;
        this is enough to short-circuit an out-of-scope question before the model.
        """
        low = question.lower()
        return not any(phrase in low for phrase in self.ooc_phrases)

    # --- Stage 2: decompose ------------------------------------------------

    def decompose(self, question: str) -> list:
        """Split a multi-part question into sub-queries via chike.decomposition —
        the proven production decompose_query (R12): '?'-splitting, Swahili
        connectors ('na pia' ...), and enumeration lists ('A, B, na C') that carry
        the preamble context (salary, employee count) to each item."""
        return decomposition.decompose_query(question)

    # --- Stage 3: route ----------------------------------------------------

    def route(self, text: str) -> SubQuestion:
        """Decide compute vs fact-lookup for one sub-question. STUB heuristic:
        a supported computation keyword plus at least one number signals a compute
        scenario. Field VALUES are NOT parsed here — resolving them (with confidence)
        is the slot extractor's job (item 4); route only picks the path and type.
        """
        low = text.lower()
        has_number = bool(re.search(r"\d", text))
        for keyword, ctype in _COMPUTE_KEYWORDS.items():
            if keyword in low and has_number:
                return SubQuestion(text=text, kind="compute", computation_type=ctype)
        return SubQuestion(text=text, kind="fact")

    # --- Stage 4: answer one sub-question ----------------------------------

    def _answer_sub(self, sq: SubQuestion) -> SubAnswer:
        sub = self._answer_compute(sq) if sq.kind == "compute" else self._answer_fact(sq)
        return self._validate_and_clean(sub)

    def _answer_compute(self, sq: SubQuestion) -> SubAnswer:
        """Compute path: extract fields WITH confidence first, and only call the
        rules engine if every required field is present and high-confidence. A
        missing OR low-confidence required field routes to clarification — the
        rules engine is never handed a guessed value."""
        required = REQUIRED_FIELDS[sq.computation_type]
        extraction = self.extractor.extract(sq.text, required, sq.computation_type)
        if not extraction.usable(required):
            return SubAnswer(
                sub_question=sq, text=CLARIFICATION_PENDING, needs_clarification=True,
            )

        inputs = {name: extraction.fields[name].value for name in required}
        result = rules_engine.compute(sq.computation_type, **inputs)
        prompt = self._build_compute_prompt(sq.text, result)
        reply = self.backend.generate(prompt, self.gen_params)
        return SubAnswer(sub_question=sq, text=reply, computation=result)

    def _answer_fact(self, sq: SubQuestion) -> SubAnswer:
        facts = tuple(self.retriever(sq.text))
        prompt = self._build_fact_prompt(sq.text, facts)
        reply = self.backend.generate(prompt, self.gen_params)
        return SubAnswer(sub_question=sq, text=reply, facts=facts)

    # --- Generate-stage prompts (production-aligned RAG wrapper, chike.prompting) ---

    def _build_compute_prompt(self, question: str, result: ComputationResult) -> str:
        # Hand the model the deterministic working as GROUND TRUTH, injected through
        # the same production RAG wrapper as facts so the generate stage is uniform.
        working_fact = f"Jibu sahihi (hesabu iliyothibitishwa): {result.working}"
        return prompting.build_chat_prompt(question, [working_fact], self.system_prompt)

    def _build_fact_prompt(self, question: str, facts: Sequence[str]) -> str:
        # Production-aligned wrapper (system prompt + UKWELI block + chat template) —
        # the format the v16 diagnostic proved reproduces production answer quality.
        return prompting.build_chat_prompt(question, facts, self.system_prompt)

    def _validate_and_clean(self, sub: SubAnswer) -> SubAnswer:
        """Validate/clean stage. Real implementation of the stop/clean step: truncate
        fabricated follow-on turns and apply production's domain corrections
        (chike.cleaning). Clarification sentinels pass through untouched.

        NOTE: the fidelity check (does the model text contradict sub.computation?)
        is still a separate follow-up; this stage currently does stop/clean only."""
        if sub.needs_clarification:
            return sub
        # Preserve the pre-clean generation in raw_text before overwriting text,
        # so future clean_reply changes can be rescored offline (see SubAnswer docstring).
        return dataclasses.replace(
            sub, text=generation_cleanup.clean_reply(sub.text), raw_text=sub.text)

    # --- Stage 5: merge ----------------------------------------------------

    @staticmethod
    def _render(sub: SubAnswer) -> str:
        if sub.needs_clarification:
            return CLARIFICATION_PENDING
        # For compute answers, append the authoritative deterministic working so
        # the exact figure is guaranteed present regardless of what the model said.
        if sub.computation is not None:
            body = sub.text.strip()
            working = sub.computation.working
            return f"{body}\n{working}" if body else working
        return sub.text.strip()

    @staticmethod
    def _raw_render(sub: SubAnswer) -> str:
        # Pre-clean counterpart of _render: the raw model generation when one was
        # produced, else the final text (clarification/compute-working have no raw).
        return sub.raw_text or sub.text.strip()

    def answer(self, question: str) -> Reply:
        """Full pipeline entry point."""
        if not self.classify(question):
            return Reply(
                question=question, in_scope=False, refused=True,
                text=REFUSAL_TEXT, raw_text=REFUSAL_TEXT, sub_answers=(),
            )

        sub_answers = tuple(self._answer_sub(self.route(part))
                            for part in self.decompose(question))
        merged = "\n\n".join(self._render(sa) for sa in sub_answers)
        merged_raw = "\n\n".join(self._raw_render(sa) for sa in sub_answers)
        return Reply(
            question=question, in_scope=True, refused=False,
            text=merged, raw_text=merged_raw, sub_answers=sub_answers,
        )
