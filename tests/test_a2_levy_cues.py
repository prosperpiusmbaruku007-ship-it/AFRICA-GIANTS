# -*- coding: utf-8 -*-
"""A2 — the levy said in everyday words, and the honest ceiling on fixing it.

A2 IS AN OPEN LEXICAL SET, NOT A CLASS. `mfuko`, `serikali inachukua`, `kupeleka kwa TRA` are
synonyms for a levy. No paradigm generates the next one — unlike object concord, where the
five members are the whole class and a census test can hold it shut.

    THE CONSTRAINT, STATED SO NOBODY LATER MISTAKES THIS FOR A CLOSURE:
    every cue here fixes ONLY the phrasing already seen to fail. Each addition is purchased
    with a user having received a wrong figure first. The candidate sweep makes that concrete
    — every money-ask candidate for nat_09 matched EXACTLY ONE corpus row, nat_09 itself,
    because the corpus contains one instance of that phrasing: the probe somebody wrote after
    it failed.

    The mitigation is therefore NOT a cleverer rule. It is the TRAINING-CORPUS DIFF — widening
    what the corpus contains so failures are found by a sweep rather than by a user.

NARROWEST FORM, PRICED RATHER THAN ASSERTED (R17 step 4). The original diagnosis warned that
`mfuko`/`serikali`/`TRA` are common words. The candidate sweep put numbers on it:

    mfuko               29 corpus rows -> 2 route changes
    kwenye mfuko         9 corpus rows -> the SAME 2 route changes
    serikali            80 corpus rows
    serikali inachukua   1 corpus row  -> 1 route change
    kwa tra             34 corpus rows
    peleka kwa tra       1 corpus row  -> 1 route change

Narrowing cost nothing in coverage and removed ~130 rows of surface.
"""
import json
import pathlib

import pytest

from chike import routing, swahili_numbers as swn

PROBES = pathlib.Path(__file__).resolve().parents[1] / (
    'eval/accuracy_gate/a2_levy_cues_012.jsonl')


def _rows():
    with PROBES.open(encoding='utf-8') as f:
        return [json.loads(ln) for ln in f if ln.strip()]


@pytest.mark.parametrize('row', _rows(), ids=lambda r: r['id'])
def test_a2_probe_routes_as_expected(row):
    got = routing.detect_intent(row['question'])
    assert got == row['expected_intent'], (
        f"{row['id']}: expected {row['expected_intent']}, got {got}. "
        f"guards_against: {row['guards_against']}")


@pytest.mark.parametrize('q', [
    'nimeweka pesa kwenye mfuko wangu wa begi je nalipa kodi',
    'serikali imetangaza sera mpya ya biashara mwaka huu je inaanza lini',
    'nawezaje kujisajili kwa tra kupata tin namba',
    'serikali inachukua hatua gani dhidi ya biashara zisizosajiliwa',
])
def test_the_common_words_do_not_route_on_their_own(q):
    """R17 step 2 — the risky vocabulary in a NON-levy sense.

    `serikali inachukua hatua` is the sharpest of these: the identical cue string in its
    ordinary meaning, 'takes STEPS' rather than 'takes MONEY'. It is held out by the path-2
    gate (number + payroll context + money-ask), not by the cue.
    """
    assert routing.detect_intent(q) == 'none'


def test_the_withheld_serikali_inakata_cue_still_names_a_live_defect():
    """THE PIN. `serikali inakata` is the exact sibling of `serikali inachukua`, is
    corpus-attested (rc_10), and is deliberately NOT a cue — because routing that row to
    compute is WORSE than leaving it on the fact path:

        "Ninalipwa laki mbili na hamsini kwa mwezi"   gold: PAYE on 250,000 -> ZERO
        sole_plausible_amount(...)                    -> 5,200,000

    The parser reads `mbili na hamsini` as 52 and multiplies by laki. PAYE on that is roughly
    TZS 1,388,000, served WITH A DETERMINISTIC WORKING to somebody who owes nothing.

    A PRE-EXISTING parser defect that the A2 cue merely unmasks. `laki <n> na <m>` affects
    every money extraction in the product, so it is its own item with its own sweep. When it
    is fixed, this test fails and the cue must be added in the same commit.
    """
    rc_10 = ('Ninalipwa laki mbili na hamsini kwa mwezi. '
             'Je serikali inakata kiasi gani kwenye mshahara wangu?')
    assert swn.sole_plausible_amount(rc_10) == 5200000, (
        'the `laki <n> na <m>` parse changed — if it now yields 250,000, add '
        '`serikali inakata` to the PAYE cues and delete this test in the same commit')
    assert routing.detect_intent(rc_10) == 'none', (
        'rc_10 now routes to compute while the amount parse is still wrong — it would be '
        'served PAYE on TZS 5,200,000 with the engine authority behind it')
    assert 'serikali inakata' not in dict(routing._LEVY_CUES)['paye']


def test_edge_p14_reaches_the_route_and_then_clarifies():
    """Routing a multi-group question is only an improvement if it CLARIFIES rather than
    computing on a guess. Its gold behaviour is SAFE-CLARIFY."""
    q = ('nina wafanyakazi watatu wa laki tano kila mmoja na wawili wa milioni moja '
         'kila mmoja nitachangia ngapi kwenye mfuko wa wafanyakazi kwa mwezi')
    assert routing.detect_intent(q) == 'nssf'
    assert swn.sole_plausible_amount(q) is None, (
        'a single amount was resolved for a two-group question — it would now compute on it'
    )


def test_the_probe_file_keeps_its_negatives():
    rows = _rows()
    assert sum(1 for r in rows if r['kind'] != 'member') >= 6, (
        'A2 touches three of the most common words in the corpus; negatives must stay '
        'substantial')
