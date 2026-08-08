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
from . import swahili_numbers as swn
from .rules_engine import rates
from .rules_engine.results import ComputationResult
from .model_abstraction import ModelBackend
from .extraction import SlotExtractor, REQUIRED_FIELDS, APPLICABILITY_REQUIRED_FIELDS
from .retrieval import retrieve as default_retrieve
from . import prompting
from . import generation_cleanup
from . import decomposition
from . import routing
from . import classification
from . import clarification
from . import fidelity

# --- Stage-level configuration ---------------------------------------------

# The OOC refusal a user actually receives. Delegated to chike.classification so it is the
# SAME text production (modal_app.py) and the gate (kaggle/eval.py) emit — this module used
# to carry its own terser string, which the refusal gate could not catch (both match
# refusal_phrases) but which would have regressed every refused user on wiring. See the
# REFUSAL_TEXT comment in chike/classification.py.
REFUSAL_TEXT = classification.REFUSAL_TEXT

# Legacy internal marker. Clarifications no longer RENDER this sentinel — they render real
# Swahili copy from chike.clarification, and callers detect a clarification via the structured
# SubAnswer.needs_clarification flag / Reply.needs_clarification (not a magic string in the
# text). Kept defined only for backward-compatible imports; do not use it for detection.
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
    needs_clarification: bool = False           # any sub-answer asked to clarify (never-guess)


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
        # R14 stop_strings: resolve from gen_params -> chike_config.json -> the module
        # default, and pass them EXPLICITLY into clean_reply (see _validate_and_clean).
        # The module default happens to equal the config list today, so this is a behavioural
        # no-op right now — but relying on that made a config-only edit to
        # generation_params.stop_strings silently NOT reach the v16 clean stage while it did
        # reach production and the gate. A latent config divergence inside a measurement run
        # is the wrong thing to leave open.
        _cfg_stops = (classification.load_local_config()
                      .get("generation_params", {}).get("stop_strings"))
        self.stop_strings = tuple(
            (gen_params or {}).get("stop_strings")
            or _cfg_stops
            or generation_cleanup.STOP_STRINGS
        )
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
                sub_question=sq, text=clarification.AMBIGUOUS_LEVY, needs_clarification=True,
            )
        # PREREQ-1 M4: the headcount CROSSES the threshold mid-period ("nina wafanyakazi 9 na
        # ninaajiri mfanyakazi wa 10..."). routing._COUNT_TRANSITION vetoes the static
        # headcount shortcut — correctly, since a static read of '9' would answer 'haihusiki'
        # — but that veto alone dropped the question onto the amount path, which then demanded
        # a salary the yes/no never needs (eval_124). Answer the crossing deterministically,
        # and ONLY at/above the threshold: below it the crossing settles nothing, so the
        # never-guess refusal stands untouched (probe ap_15).
        if sq.computation_type == "sdl" and routing.asks_applicability(sq.text):
            ordinal = routing.count_transition_ordinal(sq.text)
            if ordinal is not None and ordinal >= rates.SDL_MIN_EMPLOYEES:
                return self._deterministic_answer(
                    sq, rules_engine.sdl_crosses_threshold(ordinal))
        # Applicability-only question (obligation/threshold, no amount asked): answer the
        # yes/no from headcount (SDL) or the flat no-threshold rule (NSSF/WCF) — no salary
        # required, which the amount path below would otherwise demand (Finding 1).
        if (rules_engine.supports_applicability(sq.computation_type)
                and routing.is_applicability_question(sq.text)):
            return self._answer_applicability(sq)
        # Phase D re-run: SDL below the threshold is TZS 0 WHATEVER the payroll is, so an
        # AMOUNT question does not need the payroll either — the same "input not needed"
        # reasoning as the applicability branch above (Finding 1), applied to 'ni ngapi'.
        # eval_378 answered correctly but never stated a figure; eval_376/eval_379 asked for
        # a payroll that cannot change the answer. Placed AFTER the applicability branch so
        # yes/no questions keep their 'Hapana.' verdict, and gated on a KNOWN sub-threshold
        # count so a question that merely omits the headcount still clarifies.
        #
        # TWO GUARDS, both added after the 569-question sweep caught this branch asserting a
        # confident wrong number — the nat_07 class, third occurrence this cycle:
        #   * sole_headcount, not parse_count: gp_02 ("vibarua 8 ... na 4 ...") is a 12-person
        #     employer and the branch answered TZS 0 on the first group's 8.
        #   * no stated threshold CROSSING: "wafanyakazi 9 na ninaajiri mfanyakazi wa 10"
        #     answered TZS 0 when SDL is in fact due. That is exactly the case M4's veto
        #     exists for, so the veto governs here too and the question keeps clarifying.
        if (sq.computation_type == "sdl"
                and routing.count_transition_ordinal(sq.text) is None):
            zero_count = (0 if swn.states_no_employees(sq.text)
                          else swn.sole_headcount(sq.text))
            if zero_count is not None and zero_count < rates.SDL_MIN_EMPLOYEES:
                # Model in the loop, not _deterministic_answer: eval_247/371/372/378 already
                # reached compute_sdl's below-threshold branch and were judged CORRECT — they
                # failed only for want of a figure. Keeping the same rendering path adds the
                # figure without also changing their register, and _render appends `working`
                # verbatim so 'TZS 0' is guaranteed present whatever the model says.
                result = rules_engine.sdl_zero_below_threshold(zero_count)
                prompt = self._build_compute_prompt(sq.text, result)
                reply = self.backend.generate(prompt, self.gen_params)
                return SubAnswer(sub_question=sq, text=reply, computation=result)

        # PATTERN F2. The headcount differs BY NAMED MONTH and straddles the threshold
        # (eval_329: Januari 9, Februari 10, one payroll). One figure is wrong whichever month
        # it describes, so answer per month.
        #
        # DELIBERATELY OUTSIDE the crossing veto above. That veto exists because a stated
        # crossing means a single static count is not the whole story — which is precisely what
        # this branch supplies rather than assumes: it reads BOTH counts and answers both. The
        # first version sat inside the veto and could never fire on eval_329, the one row it was
        # written for; ex_09 only reached it because a separate regex bug hid its crossing.
        # _deterministic_answer, not the model-in-the-loop path, because the whole point is a
        # two-part shape the model would flatten.
        if sq.computation_type == "sdl":
            periods = swn.parse_month_headcounts(sq.text)
            payroll = swn.sole_plausible_amount(sq.text)
            if periods and payroll is not None:
                return self._deterministic_answer(
                    sq, rules_engine.sdl_by_month(periods, payroll))

        # RATE QUESTION ("Kiwango cha SDL ni ngapi kwa mtu mwenye mshahara wa TZS 480,000?").
        # The rate is the answer and does not depend on the figure the question carries.
        #
        # GATED ON AN AMOUNT BEING PRESENT, deliberately. eval_111 and eval_112 ask the same
        # thing with no figure, already answer correctly on the fact path, and carry detail this
        # branch does not reproduce (SDL is employer-only; WCF is paid to the WCF Authority, not
        # TRA). Firing here would replace a correct richer answer with a thinner one, so the
        # branch engages only where a figure is present — which is exactly the case that was
        # clarifying instead of answering.
        if (rules_engine.rate_statement_supports(sq.computation_type)
                and routing.asks_rate(sq.text)):
            amount = swn.sole_plausible_amount(sq.text)
            if amount is not None:
                return self._deterministic_answer(
                    sq, rules_engine.levy_rate_statement(sq.computation_type, amount))
        extraction = self.extractor.extract(sq.text, required, sq.computation_type)
        if not extraction.usable(required):
            # PREREQ-2 pattern B. GATED TO RUN ONLY WHERE EXTRACTION ALREADY FAILED, so a
            # question that computes today (eval_092, eval_302) can never be diverted here.
            #
            # eval_399 shape first: INDIVIDUALS enumerated, not a group. PAYE bands are
            # progressive, so summing two salaries is not a presentation choice but an
            # arithmetic error (1,600,000 as one salary = TZS 308,000; the true answer is
            # 10,400 + 188,000 = TZS 198,400).
            if sq.computation_type == "paye":
                individuals = swn.parse_individual_salaries(sq.text)
                if individuals:
                    return self._deterministic_answer(sq, rules_engine.compute_paye_each(
                        individuals, resident=routing.paye_resident(sq.text)))
            grouped = swn.parse_payroll_groups(sq.text)
            if grouped and grouped.get("groups"):
                inputs = {"gross_monthly_payroll": grouped["payroll"]}
                if "employee_count" in required:
                    inputs["employee_count"] = grouped["headcount"]
                # eval_289 asks for the employer share of a GROUP total — the same party
                # resolution the single-figure path already applies must reach here too.
                if sq.computation_type == "nssf":
                    inputs["party"] = routing.nssf_party(sq.text)
                result = rules_engine.compute(sq.computation_type, **inputs)
                prompt = self._build_compute_prompt(sq.text, result)
                reply = self.backend.generate(prompt, self.gen_params)
                return SubAnswer(sub_question=sq, text=reply, computation=result)
            # PREREQ-1 M1/M2/M3: the compute path is blocked because the only figure offered
            # is NOT a payroll base (a loan, rent, market value, utility bill, or a count of
            # machines/invoices/branches). Asking for a salary here validates the false
            # premise — it implies the figure IS a base and only the salary is missing. Name
            # the real base instead. This is an ANSWER, not a clarification (see
            # rules_engine/base_rejection.py), so it re-enters the judged denominator.
            #
            # Placed AFTER the usable() check so it can never divert a question that computes:
            # the 483-question sweep found exactly one currently-computing question affected
            # (eval_363, which moves to the applicability branch and keeps its verdict).
            rejectable = swn.detect_rejectable_base(sq.text, sq.computation_type)
            if rejectable:
                stated = (swn.rejectable_base_amount(sq.text)
                          if rejectable == "wrong_base" else None)
                return self._deterministic_answer(
                    sq, rules_engine.reject_base(sq.computation_type, stated))
            copy = clarification.compute_clarification(
                sq.computation_type, extraction.clarification_reasons(required), sq.text)
            return SubAnswer(sub_question=sq, text=copy, needs_clarification=True)

        inputs = {name: extraction.fields[name].value for name in required}
        # D-NSSF-1: NSSF asks for the employee's / employer's / total share. Resolve the party
        # from the question so the engine returns the right headline (it used to always return
        # the 20% total, doubling single-party answers). Levy-gated, like the applicability
        # branch above; other levies are untouched.
        if sq.computation_type == "nssf":
            inputs["party"] = routing.nssf_party(sq.text)
        # D-PAYE-1: a non-resident employee pays flat 15%, not the resident progressive bands.
        # Resolve residency from the question (guarded against the mixed two-person case, which
        # defers to decompose/merge). Levy-gated like the NSSF branch; other levies untouched.
        if sq.computation_type == "paye":
            inputs["resident"] = routing.paye_resident(sq.text)
        result = rules_engine.compute(sq.computation_type, **inputs)
        prompt = self._build_compute_prompt(sq.text, result)
        reply = self.backend.generate(prompt, self.gen_params)
        return SubAnswer(sub_question=sq, text=reply, computation=result)

    @staticmethod
    def _deterministic_answer(sq: SubQuestion, result: ComputationResult) -> SubAnswer:
        """A compute answer whose text is the engine's `working` ALONE — no model call.

        Used where the deterministic verdict IS the whole answer and a model preamble could
        only distort it (PREREQ-1: base rejections and the SDL threshold crossing). The body
        is left empty so _render emits `working` verbatim, the same discipline D-FIDELITY-1
        applies after the fact. needs_clarification stays False: these are answers, and the
        judge_gradeable exclusion of clarifications is precisely what made Phase D's
        judge-augmented comparison not like-for-like.

        The blanked body also protects the yes/no scorer, which reads the polarity of the
        FIRST paragraph: _render joins body and working with a single newline, so a model
        preamble leading with the wrong word would flip a correct 'Hapana.' verdict."""
        return SubAnswer(sub_question=sq, text="", computation=result)

    def _answer_applicability(self, sq: SubQuestion) -> SubAnswer:
        """Deterministic yes/no for an applicability-only levy question. SDL needs the
        headcount (clarify for the COUNT — not a salary — if absent); NSSF/WCF need no
        field (flat no-threshold rule). The verdict's `working` is rendered as ground
        truth through the same compute prompt (Finding 1)."""
        appl_required = APPLICABILITY_REQUIRED_FIELDS[sq.computation_type]
        if appl_required:
            extraction = self.extractor.extract(sq.text, appl_required, sq.computation_type)
            if not extraction.usable(appl_required):
                return SubAnswer(
                    sub_question=sq,
                    text=clarification.applicability_clarification(sq.computation_type),
                    needs_clarification=True,
                )
            inputs = {name: extraction.fields[name].value for name in appl_required}
        else:
            inputs = {}
        result = rules_engine.applicability(sq.computation_type, **inputs)
        # eval_393: a NEGATED premise put to us for confirmation ("...haitakiwi kulipa SDL,
        # sivyo?") is AGREED with when the verdict confirms it — leading 'Hapana.' reads as a
        # contradiction of an answer that in fact agrees. Gated on applicable is False, so a
        # negated premise the verdict CONTRADICTS is still denied (eval_391's shape). The body
        # is blanked too: the yes/no polarity is read from the first paragraph, so a model
        # preamble in front of the re-led verdict would put the lead back out of reach.
        if not result.applicable and routing.confirms_negated_premise(sq.text):
            return self._deterministic_answer(
                sq, rules_engine.agree_with_negated_premise(result))
        prompt = self._build_compute_prompt(sq.text, result)
        reply = self.backend.generate(prompt, self.gen_params)
        return SubAnswer(sub_question=sq, text=reply, computation=result)

    def _answer_fact(self, sq: SubQuestion) -> SubAnswer:
        # Never-guess (R8) fabrication guard: a situation-specific payroll-levy AMOUNT
        # with no salary/payroll figure given can't be computed — clarify instead of
        # letting the fact/RAG model invent a number (rc_22). No model call, no retrieval.
        if routing.is_uncomputable_payroll_amount(sq.text):
            return SubAnswer(sub_question=sq, text=clarification.PAYROLL_AMOUNT,
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
            return SubAnswer(sub_question=sq, text=clarification.PAYROLL_AMOUNT,
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

        D-FIDELITY-1: for a compute answer, if the cleaned model body numerically contradicts
        the authoritative sub.computation (it ignored the working and re-derived a naive figure —
        e.g. an SDL amount below the 10-employee threshold, or progressive PAYE for a non-resident),
        the body is BLANKED so _render emits the deterministic working alone. This upholds the
        arithmetic-never-trusted-to-the-model invariant (ADR 0001): a body proven to contradict the
        engine is discarded whole, not partially salvaged. raw_text keeps the pre-clean generation."""
        if sub.needs_clarification:
            return sub
        # Preserve the pre-clean generation in raw_text before overwriting text,
        # so future clean_reply changes can be rescored offline (see SubAnswer docstring).
        cleaned = generation_cleanup.clean_reply(sub.text, self.stop_strings)
        if sub.computation is not None and fidelity.body_contradicts_working(cleaned, sub.computation):
            cleaned = ""
        return dataclasses.replace(sub, text=cleaned, raw_text=sub.text)

    # --- Stage 5: merge ----------------------------------------------------

    @staticmethod
    def _render(sub: SubAnswer) -> str:
        if sub.needs_clarification:
            return sub.text.strip()          # real Swahili clarification copy (chike.clarification)
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

    @staticmethod
    def _fan_out_multi_levy(routed: list) -> list:
        """D-DECOMP-1: expand any compute sub-question that names >=2 explicit levies into one
        compute sub-question per levy (same text, distinct computation_type), preserving order.
        Single-levy compute parts and all fact parts pass through unchanged, so every question
        that did not name multiple levies produces a byte-identical `routed` list. The first
        named levy keeps the position detect_intent already assigned; the remaining levies are
        inserted immediately after it."""
        out = []
        for sq in routed:
            if sq.kind == "compute":
                levies = routing.all_explicit_levies(sq.text)
                if len(levies) >= 2:
                    out.extend(dataclasses.replace(sq, computation_type=lv) for lv in levies)
                    continue
            out.append(sq)
        return out

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
        # D-DECOMP-1: a compute part that NAMES several levies ("...SDL na NSSF...") routed to
        # only the first (detect_intent -> _explicit_levy), silently dropping the rest
        # (eval_318 lost NSSF). Fan each such part out into one compute per named levy, sharing
        # the part text so each runs its own extraction + rules-engine compute. Fact parts and
        # single-levy compute parts are untouched (byte-identical). This only ADDS compute
        # sub-answers — it never folds a compute part into the pooled fact generation, so the
        # Phase B route-aware merge invariant is preserved.
        routed = self._fan_out_multi_levy(routed)
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
            needs_clarification=any(sa.needs_clarification for sa in sub_answers),
        )
