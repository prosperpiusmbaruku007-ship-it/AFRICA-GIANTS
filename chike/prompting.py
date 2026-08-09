"""Canonical Chike RAG-injection prompt wrapper.

This builds chike_config.system_prompt + an "UKWELI ULIOTHIBITISHWA KWA SWALI HILI:"
block from the retrieved facts, then wraps it in the model's chat format so the
generate stage never hands the model a bare prompt (which yielded disclaimer-only
answers).

CHAT-FORMAT CORRECTION (2026-07-18): the wrapper now routes through the tokenizer's
OWN chat template (apply_chat_template), matching PRODUCTION (chike-inference/
modal_app.py, which has always used apply_chat_template) and TRAINING (kaggle/
train_ddp.py trained v15 via apply_chat_template — AfriqueLlama's naive-concatenation
template, NOT Llama-3 header tokens).

This module PREVIOUSLY emitted a hardcoded "<|begin_of_text|><|start_header_id|>..."
Llama-3 header format that neither training nor production ever used. A direct A/B
probe (kaggle/eos_production_probe.py, 20 questions x both formats on the real v15
adapter) proved the consequence: the production/apply_chat_template format stopped
early and emitted <|end_of_text|> 20/20; the hardcoded Llama-3 header format ran to
the 350-token cap 0/20 — the model only emits its stop token for the format it was
trained on. Every gate score measured via this wrapper before 2026-07-18 was therefore
measured against a prompt format the model was never trained on (an R12 dual-file-sync
violation in the eval harness, NOT a production defect — production always matched
training).

Callers on a real generation path (kaggle/eval.py, the orchestrator's GPU backend)
pass their loaded `tokenizer`, so build_chat_prompt is byte-identical to modal_app.py.
The no-tokenizer path is a test-only fallback that approximates the trained naive-
concat shape (system + blank line + question) — never the untrained header tokens.
"""

import json
import os
from typing import Optional, Sequence

_CONFIG_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "kaggle", "chike_config.json")
)

_FACTS_HEADER = "UKWELI ULIOTHIBITISHWA KWA SWALI HILI:"
_FACTS_FOOTER = "Tumia ukweli huu. Usibuni takwimu ambazo hazipo hapa."


def load_system_prompt(*, required: bool = True) -> str:
    """Read SYSTEM_PROMPT from kaggle/chike_config.json (R14 single source of truth).

    RAISES by default when the config cannot be read or carries no system_prompt.

    It used to return "" on failure. That is the CONTAINER-PATH-1 shape (2026-08-09):
    `_CONFIG_PATH` is REPO-RELATIVE, and the Modal image mounts only `chike/` while baking the
    config to `/root/assets/` — so inside the container this path does not exist and the soft
    default would hand the model an EMPTY system prompt. That is not a degraded answer, it is
    Chike with no persona, no register, and none of the R11 out-of-scope boundaries the prompt
    declares to the model. Silent, and worse than a crash.

    Production is currently safe only because `modal_app.ChikeModel` passes
    `system_prompt=BASE_SYSTEM_PROMPT` explicitly — safe by the caller's habit, not by
    construction, which is exactly what the phrase-list defect looked like the day before it
    bit. Strict-by-default closes it for every future caller instead.

    `required=False` restores the old soft behaviour for callers that genuinely want a
    best-effort read; nothing on a serving path should use it.
    """
    try:
        with open(_CONFIG_PATH, encoding="utf-8") as fh:
            prompt = json.load(fh).get("system_prompt", "")
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        if required:
            raise RuntimeError(
                f"system_prompt unavailable: cannot read {_CONFIG_PATH} ({exc}). "
                "This path is REPO-RELATIVE and does not resolve inside the Modal image — "
                "pass system_prompt explicitly from the baked config (see CONTAINER-PATH-1 "
                "in PROGRESS.md), or call load_system_prompt(required=False) if an empty "
                "prompt is genuinely acceptable here."
            ) from exc
        return ""
    if required and not prompt.strip():
        raise RuntimeError(
            f"system_prompt is empty in {_CONFIG_PATH} — refusing to build a prompt with no "
            "persona and no R11 scope boundaries."
        )
    return prompt


def build_enriched_system(system_prompt: str, facts: Sequence[str]) -> str:
    """system_prompt + the UKWELI facts block. No facts -> bare system prompt
    (identical to modal_app / eval fallback)."""
    if not facts:
        return system_prompt
    facts_block = "\n".join(f"- {fact}" for fact in facts)
    return (
        system_prompt
        + "\n\n" + _FACTS_HEADER + "\n"
        + facts_block
        + "\n\n" + _FACTS_FOOTER
    )


_TERMINAL_PUNCT = ("?", ".", "!")


def ensure_terminal_punct(text: str) -> str:
    """Append '?' when the user message lacks terminal punctuation (Defect B, 2026-07-28).

    v15 was trained on a naive-concat chat format with NO assistant-turn boundary, so on
    an UNPUNCTUATED question the model first completes the question's missing '?' (a
    leading-echo artifact) before answering — which clean_reply then had to strip
    (Defect A). Giving the question a terminal boundary makes the model start its answer
    directly, fixing the echo at the source and removing Defect A's >60-char echo coupling.

    No-op on already-punctuated text (all 400 gate questions end in punctuation, so their
    prompts stay byte-identical); on unpunctuated plain-WhatsApp questions it only removes
    the leading echo (answer content unchanged — verified live on p02/p06/p09/p15)."""
    t = (text or "").strip()
    if t and t[-1] not in _TERMINAL_PUNCT:
        return t + "?"
    return t


def build_chat_prompt(
    question: str,
    facts: Sequence[str],
    system_prompt: Optional[str] = None,
    tokenizer=None,
) -> str:
    """Full chat-format prompt: enriched system + user question, ready for the model.

    When `tokenizer` is supplied (every real generation path), the prompt is built with
    tokenizer.apply_chat_template(..., add_generation_prompt=True) over the SAME two
    messages modal_app.py builds — byte-identical to production and to the format v15
    was trained on. This is the fix for the EOS/non-stopping defect (see module
    docstring): the model reliably emits its stop token only for this format.

    When no tokenizer is available (unit tests without transformers/GPU), fall back to
    an approximation of the trained naive-concat shape — system prompt, a blank line,
    then the question. This is deliberately NOT the old Llama-3 header format; the
    header tokens are exactly what the model was never trained to stop after, so we do
    not emit them even in the fallback.

    system_prompt defaults to chike_config's.
    """
    if system_prompt is None:
        system_prompt = load_system_prompt()
    enriched = build_enriched_system(system_prompt, facts)
    user_msg = ensure_terminal_punct(question)   # Defect B: give the question a terminal boundary
    messages = [
        {"role": "system", "content": enriched},
        {"role": "user", "content": user_msg},
    ]
    if tokenizer is not None:
        return tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    # Test-only fallback (no tokenizer): trained naive-concat shape, never header tokens.
    return f"{enriched}\n\n{user_msg}"
