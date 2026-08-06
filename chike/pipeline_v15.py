"""The v15 production pipeline, extracted from chike-inference/modal_app.py::ChikeModel.run.

This is the ONE definition of what a real user's message goes through today:

    classify (OOC)            -> chike.classification            [refuse, no model call]
      -> never-guess guard    -> chike.routing                   [clarify, no model call]
        -> decompose          -> chike.decomposition_v15         [NO ordinal split]
          -> retrieve per sub-query, pool (dedup, order-preserving, cap 9)  [SINGLE-ARM]
            -> build prompt   -> chike.prompting + apply_chat_template
              -> generate     -> injected callable (the only environment-specific stage)
                -> postprocess-> stop-split + chike.generation_cleanup.clean_reply

WHY IT EXISTS (Phase D, ADR 0001 §10). The paired v15-vs-v16 run needs a v15 arm that is
faithful *by construction*, not "a fourth copy we believe matches production". kaggle/eval.py
could not be that arm: it lacks production's is_uncomputable_payroll_amount guard entirely,
and it runs only the 200-question gate_001. Both modal_app.py and the paired harness now
import THIS module, so the arm cannot drift from the deployment it claims to measure.

TWO CAPABILITIES THIS MODULE MUST NEVER ACQUIRE — the v15 arm must not inherit v16 powers,
or the comparison measures nothing:
  1. Decomposition is chike.decomposition_v15 (no `_split_ordinal_enumeration`). Importing
     chike.decomposition would hand v15 the eval_322 3-way split production does not have.
  2. Retrieval is SINGLE-ARM. chike.retrieval.Retriever.retrieve() is the two-arm numeric
     hybrid (d92e63f) that production does not run; V15Retriever below deliberately calls the
     single-arm ranking path instead. Both are guarded by tests/test_pipeline_v15.py.

GENERATION IS INJECTED, not owned here: tokenize -> model.generate -> decode is the only
genuinely environment-specific step (Modal T4 container vs Kaggle in-process 4-bit), so it is
passed in as `generate(prompt) -> str`. Everything either side of it is shared and provable.

NOT a leaf module (it imports sibling chike modules), so kaggle/eval.py's fetch+exec
bootstrap cannot load it — eval.py keeps its own inline decompose copy for now, guarded by a
byte-equivalence test. chike/decomposition_v15.py IS a leaf and can be fetched standalone.
"""

from typing import Callable, Optional, Sequence

from . import classification
from . import clarification
from . import decomposition_v15
from . import generation_cleanup
from . import prompting
from . import routing

# Never-guess (R8) reply for a payroll-levy AMOUNT asked with no salary figure. Shared with
# the v16 path (chike.clarification.PAYROLL_AMOUNT) and byte-identical to the constant
# modal_app.py used to define inline — both fire on the same routing predicate.
PAYROLL_CLARIFICATION = clarification.PAYROLL_AMOUNT

# Fact-pool cap: up to 3 sub-queries x top-3, bounding the prompt (modal_app.py).
FACT_CAP = 9

# Post-generation stop markers applied before clean_reply, verbatim from production.
_MANUAL_STOPS = ['<|start_header_id|>', 'User:', 'Mtumiaji:']


class V15Retriever:
    """Single-arm retrieval — production's `modal_app.retrieve_facts`, nothing more.

    Wraps chike.retrieval.Retriever but deliberately calls the single-arm ranking path
    (`_encode_and_rank`), NOT `retrieve()`. `retrieve()` is the two-arm numeric hybrid that
    ships in chike/ and does NOT run in production; letting it into the v15 arm would give
    v15 a retrieval capability it does not have and confound the paired comparison.

    The import is lazy so this module stays importable without numpy/sentence-transformers.
    """

    def __init__(self, emb_path: Optional[str] = None, texts_path: Optional[str] = None,
                 expected_fact_count: Optional[int] = None):
        from .retrieval import Retriever

        kwargs = {}
        if emb_path is not None:
            kwargs['emb_path'] = emb_path
        if texts_path is not None:
            kwargs['texts_path'] = texts_path
        if expected_fact_count is not None:
            kwargs['expected_fact_count'] = expected_fact_count
        self._inner = Retriever(**kwargs)

    def preflight(self) -> int:
        return self._inner.preflight()

    def retrieve_facts(self, question: str, top_k: int = 3) -> list:
        r = self._inner
        r._ensure_index()
        if r.fact_embeddings is None or not r.fact_texts:
            return []
        r._ensure_embed_model()
        return [r.fact_texts[i] for i in r._encode_and_rank(question, top_k)]


def pool_facts(retrieve_facts: Callable[[str], Sequence[str]],
               sub_queries: Sequence[str], cap: int = FACT_CAP) -> list:
    """Retrieve per sub-query, merge dedup + order-preserving, cap. Verbatim from
    modal_app.run()'s retrieval-merge loop."""
    facts, seen = [], set()
    for sub_query in sub_queries:
        for fact in retrieve_facts(sub_query):
            if fact not in seen:
                facts.append(fact)
                seen.add(fact)
    return facts[:cap]


def build_messages(message: str, facts: Sequence[str], system_prompt: str) -> list:
    """The exact two-message list production hands apply_chat_template, including the
    Defect-B terminal-punctuation fix on the user turn."""
    enriched_system = prompting.build_enriched_system(system_prompt, facts)
    user_msg = prompting.ensure_terminal_punct(message)
    return [
        {'role': 'system', 'content': enriched_system},
        {'role': 'user', 'content': user_msg},
    ]


def build_prompt(message: str, facts: Sequence[str], system_prompt: str, tokenizer) -> str:
    """apply_chat_template over build_messages, with production's hardcoded-header FALLBACK
    preserved.

    The fallback matters and is easy to lose: chike.prompting.build_chat_prompt falls back to
    a naive-concat shape when it has no tokenizer, whereas production falls back to the
    Llama-3 header format when apply_chat_template RAISES. Those are different strings on a
    path that only fires when a tokenizer misbehaves — exactly the kind of silent divergence
    this extraction exists to prevent — so production's version is reproduced here."""
    messages = build_messages(message, facts, system_prompt)
    try:
        return tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True,
        )
    except Exception:                                            # noqa: BLE001
        return (
            f'<|begin_of_text|>'
            f'<|start_header_id|>system<|end_header_id|>\n\n'
            f'{messages[0]["content"]}<|eot_id|>'
            f'<|start_header_id|>user<|end_header_id|>\n\n'
            f'{messages[1]["content"]}<|eot_id|>'
            f'<|start_header_id|>assistant<|end_header_id|>\n\n'
        )


def postprocess(reply: str, stop_strings: Sequence[str]) -> str:
    """Production's post-generation stage: the manual stop-split loop, then the full
    clean_reply with config-exact stop strings. The manual loop is a subset of clean_reply
    and is kept as the harmless fast-path production runs."""
    for stop in _MANUAL_STOPS + list(stop_strings):
        if stop in reply:
            reply = reply.split(stop)[0].strip()
    return generation_cleanup.clean_reply(reply, stop_strings)


def answer(
    message: str,
    *,
    generate: Callable[[str], str],
    retrieve_facts: Callable[[str], Sequence[str]],
    system_prompt: str,
    tokenizer,
    stop_strings: Sequence[str],
    config: Optional[dict] = None,
    ooc_phrases: Optional[Sequence[str]] = None,
    in_scope_phrases: Optional[Sequence[str]] = None,
    log: Optional[Callable[[str], None]] = None,
) -> dict:
    """Run the full v15 pipeline. Returns production's contract: {'reply': str} or
    {'error': str}.

    `generate(prompt) -> str` is the injected model call (already decoded, pre-clean).
    Phrase lists default to the config-resolved production set; `config` is the loaded
    chike_config dict (modal_app passes its baked CONFIG, the harness passes the fetched one).
    """
    def _log(msg):
        if log is not None:
            log(msg)

    if not message or not message.strip():
        return {'error': 'No message provided'}

    if ooc_phrases is None or in_scope_phrases is None:
        cfg_ooc, cfg_in = classification.resolve_phrases(config or {})
        ooc_phrases = ooc_phrases if ooc_phrases is not None else cfg_ooc
        in_scope_phrases = in_scope_phrases if in_scope_phrases is not None else cfg_in

    # 1. OOC classifier — intercepts out-of-scope topics before any model call (R11).
    if not classification.classify(message, ooc_phrases, in_scope_phrases):
        _log(f'[classifier] OOC intercepted: {message[:60]}')
        return {'reply': classification.REFUSAL_TEXT}

    # 2. Never-guess fabrication guard (R8) — before decompose/RAG/generate, no model call.
    if routing.is_uncomputable_payroll_amount(message):
        _log(f'[guard] uncomputable payroll amount -> clarify: {message[:60]}')
        return {'reply': PAYROLL_CLARIFICATION}

    # 3. Decompose (v15 shape) -> 4. retrieve per sub-query and pool (single-arm).
    sub_queries = decomposition_v15.decompose_query(message)
    facts = pool_facts(retrieve_facts, sub_queries)
    _log(f'[RAG] {len(sub_queries)} sub-queries -> {len(facts)} unique facts')

    # 5. Prompt -> 6. generate -> 7. postprocess.
    prompt = build_prompt(message, facts, system_prompt, tokenizer)
    reply = postprocess(generate(prompt), stop_strings)
    _log(f'[chike] Q: {message[:60]}')
    _log(f'[chike] A: {reply[:60]}')
    return {'reply': reply}
