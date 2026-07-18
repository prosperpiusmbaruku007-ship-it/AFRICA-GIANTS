"""Tests for chike.prompting — the canonical RAG-injection wrapper.

Confirms the wrapper matches production's format (chike-inference/modal_app.py /
kaggle/eval.py): the UKWELI header + '- ' bullets + footer, and — the 2026-07-18
correction — the tokenizer's OWN chat template (apply_chat_template) rather than the
old hardcoded Llama-3 header tokens, which the model was never trained to stop after.
With no tokenizer, a naive-concat fallback (system + blank line + question) is used.
"""
from chike.prompting import build_enriched_system, build_chat_prompt


class _RecordingTokenizer:
    """Minimal apply_chat_template stand-in: records what it was handed and returns a
    marker string, so tests can assert build_chat_prompt delegates to the real chat
    template (the production path) instead of hardcoding a format."""

    def __init__(self):
        self.calls = []

    def apply_chat_template(self, messages, tokenize=False, add_generation_prompt=False):
        self.calls.append(
            {"messages": messages, "tokenize": tokenize,
             "add_generation_prompt": add_generation_prompt}
        )
        return "<<TEMPLATED>>" + messages[-1]["content"]


def test_enriched_system_wraps_facts_in_ukweli_block():
    enriched = build_enriched_system("Wewe ni Chike.", ["SDL ni 3.5%", "BRELA ni 22,000"])
    assert "Wewe ni Chike." in enriched
    assert "UKWELI ULIOTHIBITISHWA KWA SWALI HILI:" in enriched
    assert "- SDL ni 3.5%" in enriched            # '- ' bullet per fact
    assert "- BRELA ni 22,000" in enriched
    assert "Tumia ukweli huu. Usibuni takwimu ambazo hazipo hapa." in enriched


def test_enriched_system_falls_back_to_bare_prompt_without_facts():
    assert build_enriched_system("Wewe ni Chike.", []) == "Wewe ni Chike."


def test_chat_prompt_delegates_to_tokenizer_chat_template():
    # The production path: when a tokenizer is supplied, build_chat_prompt must route
    # through apply_chat_template with add_generation_prompt=True over the [system, user]
    # messages — NOT emit any hardcoded header format itself.
    tok = _RecordingTokenizer()
    prompt = build_chat_prompt(
        "SDL ni ngapi?", ["SDL ni 3.5%"], system_prompt="Wewe ni Chike.", tokenizer=tok)

    assert prompt == "<<TEMPLATED>>SDL ni ngapi?"       # returned the tokenizer's output verbatim
    assert len(tok.calls) == 1
    call = tok.calls[0]
    assert call["add_generation_prompt"] is True
    assert call["tokenize"] is False
    sys_msg, user_msg = call["messages"]
    assert sys_msg["role"] == "system" and user_msg["role"] == "user"
    assert user_msg["content"] == "SDL ni ngapi?"
    # Facts are injected into the SYSTEM turn (as in production), not the user turn.
    assert "UKWELI ULIOTHIBITISHWA" in sys_msg["content"]
    assert "- SDL ni 3.5%" in sys_msg["content"]
    # No untrained Llama-3 header tokens are hand-built by the wrapper.
    assert "<|begin_of_text|>" not in prompt and "<|start_header_id|>" not in prompt


def test_chat_prompt_fallback_is_naive_concat_without_header_tokens():
    # No tokenizer (unit-test path): naive-concat shape (enriched system, blank line,
    # question) — deliberately NOT the old Llama-3 header format the model can't stop after.
    prompt = build_chat_prompt("Swali", ["fact-a"], system_prompt="SYS")
    expected = (
        "SYS\n\nUKWELI ULIOTHIBITISHWA KWA SWALI HILI:\n- fact-a\n\n"
        "Tumia ukweli huu. Usibuni takwimu ambazo hazipo hapa."
        "\n\nSwali"
    )
    assert prompt == expected
    assert "<|start_header_id|>" not in prompt and "<|begin_of_text|>" not in prompt
