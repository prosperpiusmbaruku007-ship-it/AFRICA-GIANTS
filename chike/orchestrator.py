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

import re
from dataclasses import dataclass, field
from typing import Callable, Optional, Sequence

from . import rules_engine
from .rules_engine.results import ComputationResult
from .model_abstraction import ModelBackend

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


@dataclass(frozen=True)
class SubQuestion:
    """One atomic question after decomposition, with its routing decision.

    `kind` is 'compute' or 'fact'. For 'compute', `computation_type` and `inputs`
    are the resolved call into rules_engine; for 'fact' both are empty.
    """

    text: str
    kind: str                                   # 'compute' | 'fact'
    computation_type: Optional[str] = None
    inputs: dict = field(default_factory=dict)


@dataclass(frozen=True)
class SubAnswer:
    """The answer to one sub-question.

    `text` is the model's Swahili reply. `computation` is the authoritative
    deterministic result when this went down the compute path (None otherwise) —
    it, not the model text, is the source of truth for any number.
    """

    sub_question: SubQuestion
    text: str
    facts: tuple = ()
    computation: Optional[ComputationResult] = None


@dataclass(frozen=True)
class Reply:
    """Final orchestrator output for one user question."""

    question: str
    in_scope: bool
    refused: bool
    text: str
    sub_answers: tuple = ()


class Orchestrator:
    """Runs the classify -> decompose -> route -> generate -> validate -> merge pipeline.

    Args:
        backend: the injected ModelBackend. Tests pass FakeBackend; production
            passes LocalAdapter or FrontierAPI. This is the entire reason the
            model abstraction layer (item 1) exists.
        retriever: fact-lookup stub — callable(question) -> sequence of fact strings.
            Defaults to returning nothing until real RAG retrieval is wired in.
        ooc_phrases: out-of-scope markers for the classifier stub.
        gen_params: generation params forwarded to backend.generate().
    """

    def __init__(
        self,
        backend: ModelBackend,
        retriever: Optional[Callable[[str], Sequence[str]]] = None,
        ooc_phrases: Sequence[str] = DEFAULT_OOC_PHRASES,
        gen_params: Optional[dict] = None,
    ):
        self.backend = backend
        self.retriever = retriever or (lambda _q: ())
        self.ooc_phrases = tuple(p.lower() for p in ooc_phrases)
        self.gen_params = gen_params

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
        """Split a multi-part question into atomic sub-questions. STUB heuristic:
        break on newlines and '?'. Production uses the decompose_query enumeration
        logic (R12 dual-file sync); that is a later item."""
        parts = []
        for line in question.replace("?", "?\n").splitlines():
            piece = line.strip()
            if piece:
                parts.append(piece)
        return parts or [question.strip()]

    # --- Stage 3: route ----------------------------------------------------

    def route(self, text: str) -> SubQuestion:
        """Decide compute vs fact-lookup for one sub-question. STUB heuristic:
        a supported computation keyword plus at least one number -> compute path.

        Number extraction is intentionally naive (documented stub): the largest
        number is the gross payroll / salary, the smallest is the employee count.
        Good enough to exercise the compute wiring; real extraction is a later item.
        """
        low = text.lower()
        numbers = [int(n.replace(",", "")) for n in re.findall(r"\d[\d,]*", text)]

        for keyword, ctype in _COMPUTE_KEYWORDS.items():
            if keyword in low and numbers:
                return SubQuestion(
                    text=text, kind="compute",
                    computation_type=ctype, inputs=self._extract_inputs(ctype, numbers),
                )
        return SubQuestion(text=text, kind="fact")

    @staticmethod
    def _extract_inputs(ctype: str, numbers: list) -> dict:
        gross = max(numbers)
        if ctype == "sdl":
            # employee_count is the smaller number when two are present.
            count = min(numbers) if len(numbers) > 1 else 0
            return {"gross_monthly_payroll": gross, "employee_count": count}
        if ctype == "paye":
            return {"monthly_salary": gross}
        return {"gross_monthly_payroll": gross}  # nssf, wcf

    # --- Stage 4: answer one sub-question ----------------------------------

    def _answer_sub(self, sq: SubQuestion) -> SubAnswer:
        if sq.kind == "compute":
            result = rules_engine.compute(sq.computation_type, **sq.inputs)
            prompt = self._build_compute_prompt(sq.text, result)
            reply = self.backend.generate(prompt, self.gen_params)
            sub = SubAnswer(sub_question=sq, text=reply, computation=result)
        else:
            facts = tuple(self.retriever(sq.text))
            prompt = self._build_fact_prompt(sq.text, facts)
            reply = self.backend.generate(prompt, self.gen_params)
            sub = SubAnswer(sub_question=sq, text=reply, facts=facts)
        self._validate(sub)  # STUB: fidelity check is a later item
        return sub

    @staticmethod
    def _build_compute_prompt(question: str, result: ComputationResult) -> str:
        # Hand the model the deterministic working as GROUND TRUTH to format.
        return (
            f"Swali: {question}\n"
            f"Jibu sahihi (hesabu iliyothibitishwa): {result.working}\n"
            f"Andika jibu kwa Kiswahili ukitumia hesabu hii kama ilivyo."
        )

    @staticmethod
    def _build_fact_prompt(question: str, facts: Sequence[str]) -> str:
        context = "\n".join(facts) if facts else "(hakuna ukweli uliopatikana)"
        return f"Swali: {question}\nUkweli:\n{context}\nAndika jibu kwa Kiswahili."

    def _validate(self, sub: SubAnswer) -> bool:
        """STUB fidelity check. A later item verifies the model text did not
        contradict sub.computation. For now every answer passes."""
        return True

    # --- Stage 5: merge ----------------------------------------------------

    @staticmethod
    def _render(sub: SubAnswer) -> str:
        # For compute answers, append the authoritative deterministic working so
        # the exact figure is guaranteed present regardless of what the model said.
        if sub.computation is not None:
            body = sub.text.strip()
            working = sub.computation.working
            return f"{body}\n{working}" if body else working
        return sub.text.strip()

    def answer(self, question: str) -> Reply:
        """Full pipeline entry point."""
        if not self.classify(question):
            return Reply(
                question=question, in_scope=False, refused=True,
                text=REFUSAL_TEXT, sub_answers=(),
            )

        sub_answers = tuple(self._answer_sub(self.route(part))
                            for part in self.decompose(question))
        merged = "\n\n".join(self._render(sa) for sa in sub_answers)
        return Reply(
            question=question, in_scope=True, refused=False,
            text=merged, sub_answers=sub_answers,
        )
