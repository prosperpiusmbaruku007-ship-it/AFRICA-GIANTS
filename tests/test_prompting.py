"""Tests for chike.prompting — the canonical RAG-injection wrapper.

Confirms the wrapper matches production's format (chike-inference/modal_app.py /
kaggle/eval.py): the UKWELI header + '- ' bullets + footer, and the Llama chat
scaffolding, with a bare-system fallback when there are no facts.
"""
from chike.prompting import build_enriched_system, build_chat_prompt


def test_enriched_system_wraps_facts_in_ukweli_block():
    enriched = build_enriched_system("Wewe ni Chike.", ["SDL ni 3.5%", "BRELA ni 22,000"])
    assert "Wewe ni Chike." in enriched
    assert "UKWELI ULIOTHIBITISHWA KWA SWALI HILI:" in enriched
    assert "- SDL ni 3.5%" in enriched            # '- ' bullet per fact
    assert "- BRELA ni 22,000" in enriched
    assert "Tumia ukweli huu. Usibuni takwimu ambazo hazipo hapa." in enriched


def test_enriched_system_falls_back_to_bare_prompt_without_facts():
    assert build_enriched_system("Wewe ni Chike.", []) == "Wewe ni Chike."


def test_chat_prompt_has_llama_scaffolding_and_question():
    prompt = build_chat_prompt("SDL ni ngapi?", ["SDL ni 3.5%"], system_prompt="Wewe ni Chike.")
    assert prompt.startswith("<|begin_of_text|><|start_header_id|>system<|end_header_id|>")
    assert "<|start_header_id|>user<|end_header_id|>\n\nSDL ni ngapi?<|eot_id|>" in prompt
    assert prompt.endswith("<|start_header_id|>assistant<|end_header_id|>\n\n")
    # Facts are injected into the SYSTEM turn (as in production), not the user turn.
    assert "UKWELI ULIOTHIBITISHWA" in prompt.split("<|start_header_id|>user")[0]


def test_chat_prompt_matches_production_byte_layout():
    # Reproduces modal_app.py / eval.py exactly for a single fact.
    prompt = build_chat_prompt("Swali", ["fact-a"], system_prompt="SYS")
    expected = (
        "<|begin_of_text|>"
        "<|start_header_id|>system<|end_header_id|>\n\n"
        "SYS\n\nUKWELI ULIOTHIBITISHWA KWA SWALI HILI:\n- fact-a\n\n"
        "Tumia ukweli huu. Usibuni takwimu ambazo hazipo hapa.<|eot_id|>"
        "<|start_header_id|>user<|end_header_id|>\n\nSwali<|eot_id|>"
        "<|start_header_id|>assistant<|end_header_id|>\n\n"
    )
    assert prompt == expected
