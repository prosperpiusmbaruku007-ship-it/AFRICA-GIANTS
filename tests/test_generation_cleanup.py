"""Tests for chike.generation_cleanup — the stop/clean stage ported from production."""
from chike.generation_cleanup import (
    clean_generated_reply,
    truncate_at_stops,
    clean_reply,
)


# --- clean_generated_reply (exact port) ------------------------------------

def test_strips_all_leading_fabricated_questions_in_a_loop():
    text = "(4) Je, kuna adhabu? (5) Je, kuna ada? Jibu halisi ni TZS 22,000."
    assert clean_generated_reply(text) == "Jibu halisi ni TZS 22,000."


def test_corrects_memorized_domain_tokens():
    assert "nssf.go.tz" in clean_generated_reply("Wasiliana na nssf.or.tz kwa NSSF.")
    assert ".go.tz" in clean_generated_reply("Angalia osha.go.ke kwa taarifa.")
    assert ".go.ke" not in clean_generated_reply("Angalia osha.go.ke kwa taarifa.")


# --- truncate_at_stops ------------------------------------------------------

def test_truncates_at_eot_turn_boundary():
    ramble = "SDL ni asilimia 3.5.<|eot_id|><|start_header_id|>user<|end_header_id|>\n\nSwali jingine?"
    assert truncate_at_stops(ramble) == "SDL ni asilimia 3.5."


def test_truncates_at_stop_string():
    assert truncate_at_stops("Jibu.\n\nSwali: nyingine") == "Jibu."


def test_truncate_at_stops_leaves_plain_text_without_markers():
    # truncate_at_stops only handles real turn/stop markers; plain '\n\n' is handled
    # by clean_reply (the model's fabricated turns are plain-text \n\n-separated).
    answer = "SDL ni asilimia 3.5. Thibitisha na TRA (tra.go.tz)."
    assert truncate_at_stops(answer) == answer


# --- clean_reply (full stage) ----------------------------------------------

def test_clean_reply_on_real_style_ramble():
    raw = (
        "SDL (Skills Development Levy) ni asilimia 3.5 ya mishahara ghafi. "
        "Thibitisha na TRA (tra.go.tz)."
        "<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n"
        "Kampuni yangu ina wafanyakazi 15 — je, tunalipa SDL?"
    )
    cleaned = clean_reply(raw)
    assert cleaned == (
        "SDL (Skills Development Levy) ni asilimia 3.5 ya mishahara ghafi. "
        "Thibitisha na TRA (tra.go.tz)."
    )
    assert "wafanyakazi 15" not in cleaned         # fabricated follow-up gone
    assert "<|" not in cleaned                      # no residual special tokens


def test_clean_reply_leaves_a_clean_answer_untouched():
    good = "Ada ya BRELA ni TZS 22,000. Thibitisha na BRELA.go.tz."
    assert clean_reply(good) == good
