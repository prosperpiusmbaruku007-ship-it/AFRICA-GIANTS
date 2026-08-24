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


def test_corrects_the_dead_nssf_domain():
    """INVERTED 2026-08-24 — this test used to assert the `.go.ke` rewrite as well, and the
    history is kept here because the R17 corollary says a test that instructs future maintainers
    not to fix a real defect is worse than no test.

    It asserted `.go.ke` -> `.go.tz` and `".go.ke" not in ...`. That rewrite was measured to be
    CORRUPTING CORRECT OUTPUT: 21 corpus rows carry a `.go.ke` domain and every one is an
    out-of-scope refusal naming Kenya's own regulator, so `kra.go.ke` became `kra.go.tz` — a
    domain that does not exist. The assertion was pinning a defect in place, and it did exactly
    what such a pin does: it failed when the defect was removed.

    What remains is the rewrite that IS justified — `nssf.or.tz` is DNS-failing (CLAUDE.md
    section 4) with 1,374 corpus occurrences behind it, and there is no context in which it is a
    correct citation. The positive pin for the removal lives in tests/test_cleaning.py.
    """
    assert "nssf.go.tz" in clean_generated_reply("Wasiliana na nssf.or.tz kwa NSSF.")
    assert clean_generated_reply("Angalia osha.go.ke kwa taarifa.") == (
        "Angalia osha.go.ke kwa taarifa.")


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


def test_clean_reply_strips_glued_role_token_ramble():
    # Real leak pattern (eval_048/eval_107): the real answer, then fabricated Q&A turns
    # whose question blocks END in a leaked role/junk token glued to the '?'
    # ('?user_0x01', '?become'). The generic '?...>15 chars' rule missed these because the
    # glued token is short. clean_reply must cut at the first such block.
    raw = (
        "Mchango kamili wa NSSF ni asilimia 20 ya mshahara. Thibitisha na NSSF (nssf.go.tz).user\n\n"
        "NSSF inasema nini kuhusu michango ya hiari?become\n\n"
        "Michango ya hiari ni huduma ya NSSF. Thibitisha na NSSF (nssf.go.tz).user"
    )
    cleaned = clean_reply(raw)
    assert cleaned == "Mchango kamili wa NSSF ni asilimia 20 ya mshahara. Thibitisha na NSSF (nssf.go.tz)."
    assert "become" not in cleaned and "michango ya hiari" not in cleaned.lower()


def test_clean_reply_keeps_legit_intro_plus_enumerated_steps():
    # The opposite case (eval_064/eval_066): a short intro line followed by a legitimately
    # enumerated answer is NOT fabrication — the '\n\n' block boundary must be preserved.
    raw = (
        "Hatua sahihi ni:\n\n"
        "(1) Taarifa TRA ndani ya masaa 24;\n"
        "(2) Wasiliana na msambazaji aliyeidhinishwa;\n"
        "(3) Msambazaji pekee ndiye anayeruhusiwa kufanya marekebisho."
    )
    assert clean_reply(raw) == raw


# --- degradation-tail cuts (2026-07-18): EOS-failure mitigations -------------
# The model rarely emits EOS, so ~79% of generations overrun into a degradation tail.
# These three cases were the enumerated gaps clean_reply used to miss.

def test_cuts_intra_block_sentence_repetition_loop():
    # eval_317: a complete correct answer, then the closing sentence looped ×N with no
    # '\n\n' boundary. Cut at the first repeat, keep exactly one occurrence.
    raw = ("Shughuli za saluni imepigwa marufuku kwa wasio raia. "
           "Thibitisha na Idara ya Uhamiaji (immigration.go.tz). "
           "Thibitisha na Idara ya Uhamiaji (immigration.go.tz). "
           "Thibitisha na Idara ya Uhamiaji (immigration.go.tz).")
    cleaned = clean_reply(raw)
    assert cleaned == ("Shughuli za saluni imepigwa marufuku kwa wasio raia. "
                       "Thibitisha na Idara ya Uhamiaji (immigration.go.tz).")
    assert cleaned.count("Thibitisha na Idara ya Uhamiaji") == 1


def test_short_repeated_clause_is_not_truncated():
    # Guard against false truncation: a short (<12-char) legitimately repeated clause
    # ('Ndiyo. Ndiyo.') must NOT trigger the repetition cut.
    good = "Ndiyo. Ndiyo. Jibu ni TZS 22,000."
    assert clean_reply(good) == good


def test_cuts_fabricated_turn_glued_to_nssm_role_token():
    # eval_183: fabricated Q&A turns whose questions end in the leaked role token 'nssm',
    # which the old hardcoded whitelist missed. The generalized '?'+no-space-lowercase rule
    # catches it.
    raw = ("Ndiyo. Kutokuwasilisha OSHA kunaweza kusababisha faini. Thibitisha na osha.go.tz.understander\n\n"
           "Kampuni yangu ina wafanyakazi 15 — je, tunasajili OSHA?nssm\n\nNdiyo — OSHA inatumika.")
    cleaned = clean_reply(raw)
    assert cleaned == "Ndiyo. Kutokuwasilisha OSHA kunaweza kusababisha faini. Thibitisha na osha.go.tz."
    assert "nssm" not in cleaned and "wafanyakazi 15" not in cleaned


def test_cuts_fabricated_turn_glued_to_domain_token():
    # eval_339/367/392 variant: the fake question ends in a domain token ('?about:blank',
    # '?nssf.go.tz') rather than a role word — the '?'+glued-token rule now covers dots/colons.
    raw = ("Mfanyakazi asiye mkazi halipiwi PAYE. Thibitisha na TRA (tra.go.tz).\n\n"
           "Kiwango cha juu cha PAYE ni ngapi?about:blank\n\nNi asilimia 30.")
    cleaned = clean_reply(raw)
    assert cleaned == "Mfanyakazi asiye mkazi halipiwi PAYE. Thibitisha na TRA (tra.go.tz)."
    assert "about:blank" not in cleaned and "asilimia 30" not in cleaned


def test_cuts_non_latin_script_leak():
    # eval_033/034/058: leaked Arabic answer glued after a fabricated '?'. Cut at the first
    # non-Latin character; the legitimate leading answer survives.
    raw = ("Finance Act 2025 ilianzisha VAT withholding kuanzia 1 Julai 2025. Thibitisha na TRA (tra.go.tz).\n\n"
           "Je, ninatakiwa kukata?نعم. Kama wewe ni mnunuzi.")
    cleaned = clean_reply(raw)
    assert "نعم" not in cleaned
    assert "kuanzia 1 Julai 2025" in cleaned


def test_preserves_arithmetic_minus_sign_in_compute_answers():
    # eval_191 REGRESSION GUARD: the arithmetic MINUS SIGN (U+2212) and MULTIPLICATION
    # (U+00D7) in PAYE/SDL sums must NOT be treated as a foreign-script leak — an earlier
    # non-Latin cut truncated this answer mid-sum, dropping '= TZS 78,000'.
    good = "PAYE = TZS 68,000 + 25% × (TZS 800,000 − TZS 760,000) = TZS 78,000. Thibitisha na TRA (tra.go.tz)."
    assert clean_reply(good) == good


def test_domain_loop_cut_keeps_first_real_citation():
    # eval_090/218/332: a real citation followed by a glued/looped junk domain. Keep the
    # first (legitimate) domain, drop only the junk.
    raw = "Withholding tax kwa asiye mkazi ni 15%. Thibitisha na tra.go.tz.understandthis.com.understandthis.com."
    cleaned = clean_reply(raw)
    assert cleaned == "Withholding tax kwa asiye mkazi ni 15%. Thibitisha na tra.go.tz"
    assert "understandthis" not in cleaned
