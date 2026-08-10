"""D-FIDELITY-1 — the widened asserted-result pattern, and the probes that shaped it.

The guard's `_RESULT` matched `=` and nothing else, so a body stating "SDL ... sawa na TZS
210,000" against a working of TZS 17,500 produced an empty asserted-set and
`body_contradicts_working` returned False. "sawa na" is the ordinary Swahili way to state a
result, so the guard had been partly blind since it shipped — and it is live.

Widening was driven by frequency over 946 distinct stored model generations, then constrained by
the probes below. Two of them earned their place by CHANGING the answer:

  * bare levy-scoped "ni" ("PAYE ni TZS 128,000") was justified by frequency and rejected here —
    it reads a band boundary, an applicability threshold and an exemption as computed results.
  * the operand exclusion exists because a colon alone cannot tell a result from an operand.

R17 in both directions, because the sweep showed the blindness is two-sided: three of the five
stored bodies whose verdict changes are the guard firing on CORRECT bodies and blanking them. A
too-eager pattern makes that worse, so the non-assertion probes are not a formality.
"""
import re

import pytest

from chike import fidelity


class R:
    """Stand-in for ComputationResult — the guards read amount/working/computation only."""

    def __init__(self, computation, amount, working):
        self.computation, self.amount, self.working = computation, amount, working


# --- figures that MUST NOT be read as an asserted result --------------------------------
NON_ASSERTIONS = [
    ('na_01', 'Kizingiti cha kusajili VAT ni TZS 200,000,000 kwa miezi 12.', 200_000_000,
     'a THRESHOLD stated with "ni" — the commonest non-result use of the commonest connector'),
    ('na_02', 'Kwa mshahara wa TZS 760,000, PAYE ni TZS 68,000 pamoja na 25% ya ziada.',
     760_000, 'the BASE, introduced by "mshahara wa"'),
    ('na_03', 'PAYE haikatwi kwa mshahara ulio chini ya TZS 270,000.', 270_000,
     'a BAND BOUNDARY under a negation'),
    ('na_04', 'Faini kwa mgeni ni isiyopungua TZS 10,000,000.', 10_000_000,
     'a PENALTY floor — a fact figure, not a compute result'),
    ('na_05', 'Kima cha chini cha kilimo ni TZS 175,000 kwa mwezi.', 175_000,
     'a statutory FLOOR stated with "ni"'),
    ('na_06', 'Band 2 (8%): TZS 250,000 × 8% = TZS 20,000', 250_000,
     'a band BASE introduced by a colon — the colon must attach to the result, not the operand'),
    ('na_07', 'Mauzo yako yakizidi TZS 11,000,000 unahitaji EFD.', 11_000_000,
     'an EFD threshold in a conditional'),
    ('na_08', 'Mshahara wa mfanyakazi ni kati ya TZS 520,001 na TZS 760,000.', 520_001,
     'a RANGE bound'),
    ('na_09', 'SDL inatumika kwa mwajiri mwenye jumla ya mishahara ya TZS 10,000,000.',
     10_000_000, 'an applicability BASE attributed to a levy token'),
    ('na_10', 'Ada ya BRELA ni TZS 22,000 kwa mwaka.', 22_000,
     'a FEE stated with "ni"'),
    ('na_11', 'NSSF ni asilimia 20 ya mshahara, si TZS 50,000 kwa kila mfanyakazi.', 50_000,
     'a figure under a NEGATION ("si")'),
    ('na_12', 'Kwa mshahara wa TZS 800,000: PAYE = TZS 78,000.', 800_000,
     'colon after a base phrase — it precedes the levy, not the amount'),
    ('na_13', 'Kikomo cha juu cha Band 3 kwa PAYE ni TZS 760,000.', 760_000,
     'PAYE band boundary with "ni" straight after the levy token — this probe is why bare '
     'levy-scoped "ni" is NOT in the pattern despite being attested 23 times'),
    ('na_14', 'Kizingiti cha SDL ni TZS 10,000,000 ya mishahara kwa mwaka.', 10_000_000,
     'an SDL applicability threshold with "ni" after the levy token — same rejection'),
    ('na_15', 'Mshahara usiokatwa NSSF ni TZS 0 kwa mwezi wa kwanza.', 0,
     'an exemption stated as "NSSF ni TZS 0" — same rejection'),
    ('na_16', 'Band 1 (0%): TZS 270,000 = TZS 0', 270_000,
     'a band base that is the LEFT side of an equation — na_06 one operator short'),
]

# --- figures that MUST be read as an asserted result -------------------------------------
ASSERTIONS = [
    ('as_01', 'Jumla ya mchango: TZS 200,000', 200_000,
     'colon total — the construction behind three measured guard FALSE POSITIVES'),
    ('as_02', 'SDL ni asilimia 3.5 ya jumla ya mishahara, sawa na TZS 210,000.', 210_000,
     '"sawa na" — the construction that exposed the gap'),
    ('as_03', 'PAYE ya jumla: TZS 78,000/mwezi', 78_000, 'colon total with a unit suffix'),
    ('as_04', 'PAYE itakuwa TZS 72,000 kwa mwezi.', 72_000, 'future-tense assertion'),
    ('as_05', 'Kwa mshahara wa TZS 610,000, PAYE ni karibu TZS 78,000.', 78_000,
     'hedged assertion — still an assertion'),
    ('as_06', 'Mfanyakazi anachangia: TZS 400,000 (20%)', 400_000,
     'the wrong NSSF split the guard let through — a claimed 20% employee AND 20% employer '
     'share of the same salary, which the regex scorer passed and the judge called correct'),
    ('as_07', 'TZS 1,000,000 → NSSF: mwajiri 10% = TZS 100,000', 100_000,
     'arrow/colon breakdown line'),
]


@pytest.mark.parametrize('pid,body,figure,why', NON_ASSERTIONS,
                         ids=[p[0] for p in NON_ASSERTIONS])
def test_non_assertions_are_not_read_as_results(pid, body, figure, why):
    assert figure not in fidelity._asserted_results(body), (
        f'{pid}: {figure:,} was read as an asserted result — {why}')


@pytest.mark.parametrize('pid,body,figure,why', ASSERTIONS, ids=[p[0] for p in ASSERTIONS])
def test_assertions_are_read_as_results(pid, body, figure, why):
    assert figure in fidelity._asserted_results(body), (
        f'{pid}: {figure:,} was NOT read as an asserted result — {why}')


def test_operand_exclusion_survives_backtracking():
    """The bug this pins was found by a sanity check, not by the probes above.

    With only `([\\d,]+)(?!\\s*[operator])` the regex BACKTRACKS: on "TZS 250,000 × 8%" the
    lookahead fails after 250,000, the engine gives back a digit, and "250,00" matches because
    its next character is a digit rather than an operator. The operand is not excluded — it is
    silently renumbered to 25,000, and na_06 then passes for entirely the wrong reason.
    """
    got = fidelity._asserted_results('Band 2 (8%): TZS 250,000 × 8% = TZS 20,000')
    assert got == {20_000}, f'expected only the result, got {got}'
    assert 25_000 not in got, 'the operand was truncated instead of excluded'


def test_intermediate_operands_are_dropped_from_an_equals_chain():
    """Not purely additive: the same rule removes intermediate operands the OLD '=' pattern
    read as results. Recorded here because it changes pre-existing behaviour."""
    working = ('PAYE = TZS 128,000 + 30% × (TZS 5,000,000 − TZS 1,000,000) '
               '= TZS 1,328,000')
    assert fidelity._asserted_results(working) == {1_328_000}


def test_the_row_that_exposed_the_gap():
    """th_19: body claims SDL "sawa na TZS 210,000" against an authoritative TZS 17,500."""
    body = ('Kwa wafanyakazi 12, SDL ni asilimia 3.5 ya jumla ya mishahara, sawa na '
            'TZS 210,000. Kama mauzo yako ni TZS 30,000,000, unahitaji EFD.')
    result = R('sdl', 17_500, 'SDL = 3.5% × TZS 500,000 = TZS 17,500')
    assert fidelity.body_contradicts_working(body, result)


# --- the sibling guard shares the gap: one fix, not two ----------------------------------
SIBLING_PUNCTUATIONS = [
    ('colon', 'Kwa mfanyakazi mmoja: WCF = TZS 4,000. SDL: TZS 28,000.'),
    ('equals', 'Kwa mfanyakazi mmoja: WCF = TZS 4,000. SDL = TZS 28,000.'),
    ('sawa_na', 'Kwa mfanyakazi mmoja: WCF = TZS 4,000. SDL ni sawa na TZS 28,000.'),
    ('itakuwa', 'Kwa mfanyakazi mmoja: WCF = TZS 4,000. SDL itakuwa TZS 28,000.'),
]


@pytest.mark.parametrize('label,body', SIBLING_PUNCTUATIONS,
                         ids=[p[0] for p in SIBLING_PUNCTUATIONS])
def test_sibling_guard_catches_every_punctuation_of_the_same_wrong_figure(label, body):
    """One employee: the engine says SDL does not apply. A body volunteering TZS 28,000 for it
    is wrong however it is punctuated. Before the widening, three of these four passed —
    verified by direct call, since the corpus contains none of the missed forms."""
    sdl_na = R('sdl', None, 'SDL haitumiki: wafanyakazi 1 (chini ya 10).')
    assert fidelity.body_contradicts_siblings(body, {'sdl': sdl_na}), (
        f'sibling guard blind to the "{label}" punctuation')


def test_result_and_attributed_are_one_pattern():
    """The historical split (`_RESULT` = '=' only, `_ATTRIBUTED` = '[:=]') is what let the two
    guards be blind in different ways. They are deliberately the same object now; a future
    change that re-splits them should have to say why."""
    assert fidelity._ATTRIBUTED is fidelity._RESULT


def test_pattern_is_case_insensitive_on_the_word_connectors():
    assert 210_000 in fidelity._asserted_results('SDL SAWA NA TZS 210,000')
    assert 72_000 in fidelity._asserted_results('PAYE ITAKUWA TZS 72,000')


def test_no_connector_matches_a_bare_amount():
    """A figure with no connector at all is a mention, never an assertion."""
    assert fidelity._asserted_results('Mshahara wake ni wa TZS 800,000 kwa mwezi') == set()
    assert re.search(r'TZS', 'Mshahara wake ni wa TZS 800,000 kwa mwezi')
