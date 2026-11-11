"""Number-BEFORE-scale amounts ("11 milioni", "400 elfu", "1.5 milioni", "11 million").

Found live 2026-11-12: the parser read "TZS 11 milioni" as [11, 1_000_000]. A fabricated EFD threshold
went unflagged (D-FIDELITY-7 never saw 11,000,000) AND the compute engines were handed TZS 1,000,000 for
"6 milioni" (SDL 35,000 instead of 210,000). Every earlier specimen used the scale-first order, so every
test passed: R33, the probe set shared the notation of the person who wrote the parser.

Sweep (eval/controls/sweep_parser_*_2026_11_12.py, artifacts in eval/results/): 8,060 distinct committed
strings, 39 changed; and of 236 scale-first questions rewritten number-first, the OLD parser gave a
different engine answer on 67 (SDL 22, presumptive 17, VAT registration 10, NSSF 9, WCF 6, PAYE 3) --
the NEW parser on 0. The equivalence tests below are the compact permanent form of that result.
"""
import pytest

from chike import swahili_numbers as swn
from chike.orchestrator import ModelBackend, Orchestrator


def _amounts(text):
    return sorted(int(a) if a == int(a) else float(a) for a in swn.parse_amounts(text))


@pytest.mark.parametrize("text,expected", [
    ("TZS 11 milioni", [11_000_000]),
    ("11 milioni", [11_000_000]),
    ("mauzo ya 15 milioni", [15_000_000]),
    ("400 elfu", [400_000]),
    ("5 laki", [500_000]),
    ("2 bilioni", [2_000_000_000]),
    ("1.5 milioni", [1_500_000]),             # decimal mark
    ("1,5 milioni", [1_500_000]),             # comma-decimal convention
    ("11.5 milioni", [11_500_000]),
    ("40.5 milioni", [40_500_000]),
    ("11 million", [11_000_000]),             # code-switched English
    ("2 millions", [2_000_000]),
    ("kodi ya 5 elfu na 3 milioni", [5_000, 3_000_000]),
])
def test_number_first_scale_amounts_parse_to_the_full_amount(text, expected):
    assert _amounts(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("milioni 11", [11_000_000]),
    ("TZS milioni 11", [11_000_000]),
    ("elfu 400", [400_000]),
    ("milioni 1.5", [1_500_000]),
    ("TZS 11M", [11_000_000]),
    ("TZS 500,000", [500_000]),
    ("TZS 11,000,000", [11_000_000]),
])
def test_existing_notations_are_untouched(text, expected):
    assert _amounts(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("siku 26 elfu 18", [26, 18_000]),            # `elfu` belongs to `elfu 18`, not to `26 elfu`
    ("milioni 6 elfu 500", [500_000, 6_000_000]),  # pre-existing reading, unchanged
    ("wafanyakazi 12, mishahara ni milioni 6", [12, 6_000_000]),
    ("12 wafanyakazi", [12]),                      # a headcount is not an amount
    ("GN487A", []),                                # alphanumeric code is not money
])
def test_collisions_and_non_amounts_keep_todays_reading(text, expected):
    assert _amounts(text) == expected


def test_a_three_digit_tail_is_declined_not_guessed_and_is_reported():
    """'1,500 milioni' = 1.5 million or 1,500 million -- a factor of 1000. Same policy as 'milioni 1,500'."""
    assert _amounts("1,500 milioni") == []
    assert swn.ambiguous_scale_figures("1,500 milioni") == ["1,500 milioni"]
    assert swn.sole_plausible_amount("mauzo ni 1,500 milioni") is None


def test_the_compiled_patterns_contain_no_control_characters():
    """R39: a regex patched in through a generating script with a NON-RAW string compiles `\\b` to a
    literal backspace and matches nothing. The source looks right; only the compiled object tells."""
    for name in ("_SCALE_DIGIT", "_DIGIT_SCALE"):
        pat = getattr(swn, name).pattern
        assert not any(ord(c) < 32 for c in pat), (name, repr(pat))


# ── the engines: the answer a user reads, not the parsed list ───────────────────────────────
class _Silent(ModelBackend):
    def generate(self, prompt, params=None):
        return ""


def _answer(q):
    return Orchestrator(_Silent(), retriever=lambda x: [], ooc_phrases=[], in_scope_phrases=[]).answer(q).text


# Scale-first originals taken from committed corpora; the number-first twin is derived mechanically.
_EQUIV = [
    "Kampuni yenye wafanyakazi 15 inalipa SDL kiasi gani kwa mishahara ya jumla milioni 9?",
    "Nina wafanyakazi 12, mishahara yote kwa mwezi ni milioni 6. SDL nitalipa kiasi gani?",
    "Katika miezi 6 iliyopita nimeuza jumla ya TZS milioni 120 — je nimefika kiwango cha VAT?",
    "Biashara yangu imepata mauzo ya TZS milioni 95 katika miezi 6 — je nimevuka kizingiti cha VAT?",
    "Mauzo yangu kwa mwaka ni milioni 40, nitalipa kodi ya makadirio kiasi gani?",
    "Biashara yangu inauza milioni 4 kwa mwaka, kodi ya makadirio ni ngapi?",
    "Mauzo yangu ya mwaka ni TZS milioni 250, je ni lazima kusajili VAT?",
]


def _number_first(q):
    import re
    return re.sub(r"\b(elfu|laki|milioni|bilioni)\s+(\d{1,3}(?:[.,]\d{1,2})?)(?![\d.,]*\d)", r"\2 \1", q,
                  flags=re.IGNORECASE)


@pytest.mark.parametrize("scale_first", _EQUIV)
def test_the_same_question_in_either_spelling_gets_the_same_engine_answer(scale_first):
    nf = _number_first(scale_first)
    assert nf != scale_first, "the rewrite must actually change the text, or this proves nothing"
    assert _answer(nf) == _answer(scale_first)


def test_the_founding_compute_specimen_sdl_is_210000_not_35000():
    """'6 milioni' used to hand compute_sdl TZS 1,000,000 -> SDL 35,000 (owed: 210,000)."""
    text = _answer("Nina wafanyakazi 12, mishahara yote kwa mwezi ni 6 milioni. SDL nitalipa kiasi gani?")
    assert "210,000" in text and "35,000" not in text, text


def test_the_founding_vat_specimen_does_not_tell_a_120m_business_it_need_not_register():
    text = _answer("Katika miezi 6 iliyopita nimeuza jumla ya TZS 120 milioni — je nimefika kiwango cha VAT?")
    assert "TZS 120,000,000" in text and "TZS 1,000,000" not in text, text
