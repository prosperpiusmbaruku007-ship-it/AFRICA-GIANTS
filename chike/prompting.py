"""Canonical Chike RAG-injection prompt wrapper.

This is the prompt format the v16 diagnostic proved reproduces production answer
quality: chike_config.system_prompt + an "UKWELI ULIOTHIBITISHWA KWA SWALI HILI:"
block built from the retrieved facts + the Llama chat-template scaffolding. Built
here as ONE function so the orchestrator's generate stage does not hand the model a
bare prompt (which yielded disclaimer-only answers).

Matches chike-inference/modal_app.py (lines ~451-483) and kaggle/eval.py (lines
~331-345) byte-for-byte — the facts header, footer, '- ' bullet, and header-token
layout are identical to both.

DIVERGENCE-RISK FOLLOW-UP: modal_app.py and eval.py currently build this SAME wrapper
inline and independently — the duplication class that caused earlier eval/production
drift. This module is written to become the single shared home, but wiring the other
two to import it is a cross-deployment change (modal bakes chike-inference/; eval
fetches individual files from GitHub), so it is tracked as a follow-up. For now this
is the orchestrator's copy, kept identical to the other two on purpose.
"""

import json
import os
from typing import Optional, Sequence

_CONFIG_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "kaggle", "chike_config.json")
)

_FACTS_HEADER = "UKWELI ULIOTHIBITISHWA KWA SWALI HILI:"
_FACTS_FOOTER = "Tumia ukweli huu. Usibuni takwimu ambazo hazipo hapa."


def load_system_prompt() -> str:
    """Read SYSTEM_PROMPT from kaggle/chike_config.json (R14 single source of truth)."""
    try:
        with open(_CONFIG_PATH, encoding="utf-8") as fh:
            return json.load(fh).get("system_prompt", "")
    except (FileNotFoundError, json.JSONDecodeError):
        return ""


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


def build_chat_prompt(
    question: str,
    facts: Sequence[str],
    system_prompt: Optional[str] = None,
) -> str:
    """Full Llama chat-format prompt: enriched system + user question + assistant
    generation header. system_prompt defaults to chike_config's."""
    if system_prompt is None:
        system_prompt = load_system_prompt()
    enriched = build_enriched_system(system_prompt, facts)
    return (
        "<|begin_of_text|>"
        "<|start_header_id|>system<|end_header_id|>\n\n"
        f"{enriched}<|eot_id|>"
        "<|start_header_id|>user<|end_header_id|>\n\n"
        f"{question.strip()}<|eot_id|>"
        "<|start_header_id|>assistant<|end_header_id|>\n\n"
    )
