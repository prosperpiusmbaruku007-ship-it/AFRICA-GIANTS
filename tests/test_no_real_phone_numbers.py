"""The repo is PUBLIC. A real participant/founder/reviewer phone number must not come back into a test fixture unnoticed.

Every Tanzanian mobile number (2556xxxxxxxx / 2557xxxxxxxx, with or without '+', spaces or dashes; or local 06x/07x) found in a file under
tests/ must be in PLACEHOLDERS below. Adding a number to the list is a deliberate act that shows up in review: use obvious placeholders
(2557000000NN). Old commits still contain two real numbers (no history rewrite -- see PROGRESS.md section 5).
"""
import pathlib
import re

TESTS = pathlib.Path(__file__).parent

PLACEHOLDERS = frozenset({
    "255700000000", "255700000001", "255700000002", "255700000003", "255700000004", "255700000005", "255700000006",
    "255700000007", "255700000011", "255700000022", "255700000098", "255700000099",
    "255712345678", "255712345913", "255787654321", "255799000111", "255799999999",
})

_INTL = re.compile(r"(?<!\d)\+?255[\s-]?([67]\d{2})[\s-]?(\d{3})[\s-]?(\d{3})(?!\d)")
_LOCAL = re.compile(r"(?<![\d+])0([67]\d{2})[\s-]?(\d{3})[\s-]?(\d{3})(?!\d)")


def foreign_numbers(text, allowed=PLACEHOLDERS):
    """Phone-like numbers in `text` (normalised to 255XXXXXXXXX) that are not allowlisted placeholders."""
    found = {"255" + "".join(m.groups()) for m in _INTL.finditer(text)}
    found |= {"255" + "".join(m.groups()) for m in _LOCAL.finditer(text)}
    return sorted(found - set(allowed))


def test_no_test_file_contains_a_non_placeholder_phone_number():
    offenders = {}
    for p in sorted(TESTS.rglob("*")):
        if p.is_file() and p.suffix in {".py", ".json", ".jsonl", ".txt", ".md", ".yml", ".yaml", ".env"}:
            bad = foreign_numbers(p.read_text(encoding="utf-8", errors="replace"))
            if bad:
                offenders[str(p.relative_to(TESTS))] = ["..." + n[-4:] for n in bad]    # shape only: never print the number
    assert not offenders, f"non-placeholder phone numbers in tests (tails shown): {offenders}"


# ── the control: plant one and watch it fire; and a clean case must pass (R26) ──────────────────────────────────────────────
def test_the_scanner_fires_on_a_planted_number_in_every_notation():
    d = "7" + "11111111"                    # built at runtime so this file itself carries no non-placeholder number
    for planted in ("255" + d, "+255" + d, f"+255 {d[:3]} {d[3:6]} {d[6:]}", f"255-{d[:3]}-{d[3:6]}-{d[6:]}",
                    "0" + d, f"0{d[:3]} {d[3:6]} {d[6:]}"):
        assert foreign_numbers(f"sender = '{planted}@s.whatsapp.net'") == ["255" + d], planted


def test_the_scanner_passes_placeholders_and_ignores_non_phone_digits():
    clean = "a 255700000099 b +255700000098 c 2026111312345678 d 12557000000999 e 0700000099"
    # 0700000099 == 255700000099 (allowlisted); the long digit runs are not phone numbers (no boundary)
    assert foreign_numbers(clean) == []


def test_the_scan_of_the_real_tests_directory_is_not_vacuous():
    n = sum(len(_INTL.findall(p.read_text(encoding="utf-8", errors="replace"))) for p in TESTS.glob("test_*.py"))
    assert n > 50, "the scanner found almost no phone numbers in tests/ -- it is probably not matching the fixtures"
