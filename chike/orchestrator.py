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
from . import routing
from . import classification

# --- Stage-level configuration ---------------------------------------------

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
        ooc_phrases: Optional[Sequence[str]] = None,
        in_scope_phrases: Optional[Sequence[str]] = None,
        gen_params: Optional[dict] = None,
        extractor: Optional[SlotExtractor] = None,
        system_prompt: Optional[str] = None,
    ):
        self.backend = backend
        # Default to the real v15 retrieval; an injected retriever overrides it.
        self.retriever = retriever if retriever is not None else default_retrieve
        # OOC classifier phrase lists: default to the production set resolved from
        # chike_config.json via the shared chike.classification module (R11/R12 parity —
        # the 53 ooc / 24 in_scope union, no longer an 8-phrase stub). Either list can be
        # overridden for tests; a partial override still fills the other from config.
        if ooc_phrases is None or in_scope_phrases is None:
            cfg_ooc, cfg_in = classification.resolve_phrases(
                classification.load_local_config())
        self.ooc_phrases = tuple(ooc_phrases) if ooc_phrases is not None else tuple(cfg_ooc)
        self.in_scope_phrases = (tuple(in_scope_phrases) if in_scope_phrases is not None
                                 else tuple(cfg_in))
        self.gen_params = gen_params
        # Slot extractor shares the injected backend by default (same DI contract).
        self.extractor = extractor or SlotExtractor(backend, gen_params)
        # Chike system prompt (R14) for the generate-stage RAG wrapper.
        self.system_prompt = (
            system_prompt if system_prompt is not None else prompting.load_system_prompt()
        )

    # --- Stage 1: classify -------------------------------------------------

    def classify(self, question: str) -> bool:
        """Return True if the question is in scope. Delegates to the shared
        chike.classification.classify — byte-for-byte the same R11 OOC gate the Modal
        edge (modal_app.py) and the eval gate (kaggle/eval.py) run, over the same
        config-resolved phrase lists. This closes Finding 3 (the former 8-phrase stub)."""
        return classification.classify(question, self.ooc_phrases, self.in_scope_phrases)

    # --- Stage 2: decompose ------------------------------------------------

    def decompose(self, question: str) -> list:
        """Split a multi-part question into sub-queries via chike.decomposition —
        the proven production decompose_query (R12): '?'-splitting, Swahili
        connectors ('na pia' ...), and enumeration lists ('A, B, na C') that carry
        the preamble context (salary, employee count) to each item."""
        return decomposition.decompose_query(question)

    # --- Stage 3: route ----------------------------------------------------

    def route(self, text: str) -> SubQuestion:
        """Decide compute vs fact-lookup for one sub-question, via chike.routing
        (ADR 0001 Phase A — the Candidate-C deterministic router that validated at
        precision 1.0 / 8-of-8 boundary pairs / 0 OOC misroutes on the natural set).

        route only picks the path and the computation TYPE; field VALUES are resolved
        (with confidence) by the slot extractor. 'ambiguous_multi' is compute-intent with
        an unresolved specific levy — it takes the compute path, where the missing type
        surfaces as a never-guess clarification (see _answer_compute)."""
        intent = routing.detect_intent(text)
        if intent == "none":
            return SubQuestion(text=text, kind="fact")
        return SubQuestion(text=text, kind="compute", computation_type=intent)

    # --- Stage 4: answer one sub-question ----------------------------------

    def _answer_sub(self, sq: SubQuestion) -> SubAnswer:
        sub = (self._answer_compute(sq) if sq.kind == "compute"
               else self._answer_fact(sq))
        return self._validate_and_clean(sub)

    def _answer_compute(self, sq: SubQuestion) -> SubAnswer:
        """Compute path: extract fields WITH confidence first, and only call the
        rules engine if every required field is present and high-confidence. A
        missing OR low-confidence required field routes to clarification — the
        rules engine is never handed a guessed value."""
        # 'ambiguous_multi' (or any type the rules engine doesn't define) is compute-intent
        # with an unresolved levy — never guess which one; clarify.
        required = REQUIRED_FIELDS.get(sq.computation_type)
        if required is None:
            return SubAnswer(
                sub_question=sq, text=CLARIFICATION_PENDING, needs_clarification=True,
            )
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
        # Never-guess (R8) fabrication guard: a situation-specific payroll-levy AMOUNT
        # with no salary/payroll figure given can't be computed — clarify instead of
        # letting the fact/RAG model invent a number (rc_22). No model call, no retrieval.
        if routing.is_uncomputable_payroll_amount(sq.text):
            return SubAnswer(sub_question=sq, text=CLARIFICATION_PENDING,
                             needs_clarification=True)
        facts = tuple(self.retriever(sq.text))
        prompt = self._build_fact_prompt(sq.text, facts)
        reply = self.backend.generate(prompt, self.gen_params)
        return SubAnswer(sub_question=sq, text=reply, facts=facts)

    def _pool_facts(self, retrieval_queries) -> tuple:
        """Retrieve facts for each sub-query and pool them (dedup, preserve order,
        cap 9) — the v15 run() retrieval-merge (modal_app.py:437-443) that a single
        whole-question generation is then built on."""
        facts, seen = [], set()
        for q in retrieval_queries:
            for fact in self.retriever(q):
                if fact not in seen:
                    facts.append(fact)
                    seen.add(fact)
        return tuple(facts[:9])

    def _answer_facts_single_pass(self, retrieval_queries, generation_question) -> SubAnswer:
        """v15-style single fact generation: pool facts across retrieval_queries, then
        generate ONCE over generation_question. This is the collapse that restores v15's
        proven whole-question behaviour for all-fact messages (closing the per-fragment
        Q1 empty-output and Q12 fabricated-turn regressions), and produces the pooled fact
        answer for the fact remainder of a mixed compute+fact message."""
        sq = SubQuestion(text=generation_question, kind="fact")
        # Same never-guess fabrication guard as _answer_fact, applied to the collapsed
        # whole-question generation (rc_22 arrives here via the all-fact path).
        if routing.is_uncomputable_payroll_amount(generation_question):
            return SubAnswer(sub_question=sq, text=CLARIFICATION_PENDING,
                             needs_clarification=True)
        facts = self._pool_facts(retrieval_queries)
        prompt = self._build_fact_prompt(generation_question, facts)
        reply = self.backend.generate(prompt, self.gen_params)
        return self._validate_and_clean(SubAnswer(sub_question=sq, text=reply, facts=facts))

    # --- Generate-stage prompts (production-aligned RAG wrapper, chike.prompting) ---

    def _backend_tokenizer(self):
        # The real GPU backend (KaggleDirectBackend / Modal) exposes .tokenizer; passing
        # it makes build_chat_prompt route through apply_chat_template — byte-identical to
        # production and to the format v15 was trained on, so the model actually stops at
        # EOS (see chike/prompting.py docstring). FakeBackend has none -> test fallback.
        return getattr(self.backend, "tokenizer", None)

    def _build_compute_prompt(self, question: str, result: ComputationResult) -> str:
        # Hand the model the deterministic working as GROUND TRUTH, injected through
        # the same production RAG wrapper as facts so the generate stage is uniform.
        working_fact = f"Jibu sahihi (hesabu iliyothibitishwa): {result.working}"
        return prompting.build_chat_prompt(
            question, [working_fact], self.system_prompt,
            tokenizer=self._backend_tokenizer())

    def _build_fact_prompt(self, question: str, facts: Sequence[str]) -> str:
        # Production-aligned wrapper (system prompt + UKWELI block + tokenizer chat
        # template) — the format the v16 diagnostic proved reproduces production quality.
        return prompting.build_chat_prompt(
            question, facts, self.system_prompt,
            tokenizer=self._backend_tokenizer())

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
        """Full pipeline entry point.

        Route-aware merge (ADR 0001 Phase B): decomposition is a RETRIEVAL fan-out that
        RE-COLLAPSES to a single generation whenever every part is fact — matching v15
        run() (decompose -> pool facts -> generate once over the whole message), which is
        what closes the per-fragment Q1 empty-output and Q12 fabricated-turn regressions.
        Per-part generation is kept ONLY where two genuinely different answer sources are
        needed: a compute part goes through the deterministic rules engine (authoritative
        arithmetic, never trusted to the model), while the fact remainder is pooled into a
        single generation over just the fact sub-questions (so it never re-answers the
        compute part or does its sum)."""
        if not self.classify(question):
            return Reply(
                question=question, in_scope=False, refused=True,
                text=REFUSAL_TEXT, raw_text=REFUSAL_TEXT, sub_answers=(),
            )

        routed = [self.route(part) for part in self.decompose(question)]
        compute_parts = [sq for sq in routed if sq.kind == "compute"]
        fact_parts = [sq for sq in routed if sq.kind == "fact"]

        if not compute_parts:
            # All-fact -> collapse to v15's single whole-question pass.
            sub_answers = (self._answer_facts_single_pass(
                [sq.text for sq in fact_parts], question),)
        else:
            # Any compute part present -> per-part compute (rules engine), then AT MOST one
            # pooled fact generation over the fact sub-questions only. Compute parts are
            # NEVER folded into the fact generation (that would forfeit the authoritative
            # deterministic figure — the one load-bearing reason per-part generation exists).
            subs = [self._answer_sub(sq) for sq in compute_parts]
            if fact_parts:
                fact_question = " ".join(sq.text for sq in fact_parts)
                subs.append(self._answer_facts_single_pass(
                    [sq.text for sq in fact_parts], fact_question))
            sub_answers = tuple(subs)

        merged = "\n\n".join(self._render(sa) for sa in sub_answers)
        merged_raw = "\n\n".join(self._raw_render(sa) for sa in sub_answers)

        # Merge-time empty guard: a genuinely empty merged reply (every sub-answer came back
        # blank after cleaning) must never be returned silently. Fall back to ONE v15-style
        # whole-question single-pass generation and return that instead.
        if not merged.strip():
            fallback = self._answer_facts_single_pass(
                [sq.text for sq in routed], question)
            sub_answers = (fallback,)
            merged = self._render(fallback)
            merged_raw = self._raw_render(fallback)

        return Reply(
            question=question, in_scope=True, refused=False,
            text=merged, raw_text=merged_raw, sub_answers=sub_answers,
        )
