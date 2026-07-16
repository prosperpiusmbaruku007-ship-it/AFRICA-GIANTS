"""Deterministic Swahili numeral + ambiguity tests — the exact cases the qwen3-32b
judge misread this session (laki/robo/mia compound words). Run locally, no GPU."""
from decimal import Decimal

from chike.swahili_numbers import (
    parse_amounts, parse_count, detect_vague_quantity, detect_approximation,
    detect_missing_antecedent, detect_wrong_base, detect_allowance_ambiguity, detect_period,
)


def _first(text):
    a = parse_amounts(text)
    return a[0] if a else None


# --- the judge's confirmed number-word errors, now parsed correctly --------
def test_laki_tano_is_500k_not_5k():
    assert _first("mshahara wa laki tano") == Decimal("500000")


def test_laki_nne_is_400k():
    assert _first("analipwa laki nne") == Decimal("400000")


def test_milioni_mbili_na_robo_is_2_25m():
    assert _first("payroll ni milioni mbili na robo") == Decimal("2250000")


def test_milioni_moja_na_nusu_is_1_5m():
    assert _first("anapata milioni moja na nusu kwa mwezi") == Decimal("1500000")


def test_milioni_mia_mbili_na_hamsini_is_250m():
    assert _first("mauzo yetu ni milioni mia mbili na hamsini") == Decimal("250000000")


def test_milioni_sabini_na_mbili_is_72m():
    assert _first("wanapata milioni sabini na mbili kwa mwaka") == Decimal("72000000")


def test_elfu_mia_saba_na_hamsini_is_750k():
    assert _first("analipwa elfu mia saba na hamsini") == Decimal("750000")


def test_digit_and_slang_forms():
    assert _first("mtaji ni kama 20m hivi") == Decimal("20000000")
    assert _first("milioni 190 mwaka huu") == Decimal("190000000")
    assert _first("mshahara wa TZS 500,000") == Decimal("500000")


def test_spelled_and_digit_counts():
    assert parse_count("tuna wafanyakazi kumi na wawili") == 12
    assert parse_count("tuna wafanyakazi 15") == 15
    assert parse_count("wafanyakazi ishirini") == 20


def test_law_citation_number_not_parsed_as_amount():
    # The digits inside a law/citation code must never be read as a currency figure —
    # "487" in "GN487A", "605" in "GN605A". This was a DANGEROUS misread (extract_120).
    assert parse_amounts("hii ni sawa chini ya GN487A") == []
    assert parse_amounts("kiwango cha mshahara kipo GN605A") == []
    # a real figure alongside a citation is still parsed; only the code digits are excluded
    assert parse_amounts("chini ya GN487A, payroll ni milioni tano") == [Decimal("5000000")]


# --- ambiguity detectors (the clarification triggers) ----------------------
def test_vague_quantity():
    assert detect_vague_quantity("duka langu lina wafanyakazi wachache tu")
    assert detect_vague_quantity("mshahara mdogo")
    assert not detect_vague_quantity("wafanyakazi 12 kila mmoja laki tano")


def test_approximation():
    assert detect_approximation("wafanyakazi ka-12 hivi")
    assert detect_approximation("mauzo ni kama milioni mbili hivi")
    assert detect_approximation("salary yake kama laki 8 kasoro")
    assert not detect_approximation("mshahara ni laki tano")


def test_missing_antecedent_only_without_number():
    assert detect_missing_antecedent("kwa hao, SDL ni kiasi gani?")
    # antecedent word but an explicit number present -> not a missing antecedent
    assert not detect_missing_antecedent("kwa hao wafanyakazi 12, SDL?")


def test_wrong_base_trap():
    assert detect_wrong_base("mauzo yetu ni milioni 190, SDL yetu ni kiasi gani?", "sdl")
    assert detect_wrong_base("company ina mtaji wa milioni 100, NSSF ni kiasi gani?", "nssf")
    assert not detect_wrong_base("payroll ni milioni 5, SDL?", "sdl")
    # wrong_base only applies to payroll levies
    assert not detect_wrong_base("mauzo yetu ni milioni 190, VAT?", "vat")


def test_allowance_ambiguity():
    assert detect_allowance_ambiguity("mshahara wa msingi laki tano na posho ya nyumba laki moja")
    assert detect_allowance_ambiguity("nampa take home laki nane")
    assert not detect_allowance_ambiguity("mshahara ni laki tano")


def test_period_divisors():
    assert detect_period("milioni sabini na mbili kwa mwaka")[0] == 12
    assert detect_period("robo mwaka tumelipa milioni tatu")[0] == 3
    assert detect_period("nusu mwaka milioni thelathini")[0] == 6
    assert detect_period("payroll yote kwa mwezi")[0] == 1
    # week/day need extra info -> None divisor (clarify, don't silently convert)
    assert detect_period("elfu kumi kwa siku")[0] is None
