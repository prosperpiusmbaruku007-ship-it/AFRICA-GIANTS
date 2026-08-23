# -*- coding: utf-8 -*-
"""The coverage gate: refuse a FACT-PATH question whose topic the corpus does not hold.

WHY THIS EXISTS, AND WHY IT LOOKS NOTHING LIKE THE THREE DESIGNS BEFORE IT. `retrieve_facts`
applies no floor — it returns the three nearest facts at any score and the model writes a
confident answer out of them. Nine of twelve ordinary trader topics land there (measured
2026-08-23). Three safety-floor designs are dead, and all three died the same way, by consulting
a SIMILARITY SCORE:

  * an absolute threshold — correct facts score 0.765-0.809, irrelevant top-1s 0.790-0.859.
    There is no cut point.
  * a top-1/top-2 MARGIN — it INVERTS: the correct row has the smallest margin of 21 tested and
    three known-wrong rows have larger margins than every correct one.
  * forced MAXIMUM retrieval confidence — the exact correct facts placed directly into context
    still produced a confidently incomplete answer.

A fourth died in scoping: generic term overlap between the question and the index. To catch 7 of
the 12 it falsely refuses 74 answerable questions, because the index is 221 rows of dense
compliance prose and nearly every Swahili business question shares SOME token with SOME fact.

THIS GATE CONSULTS NO SCORE AND NO RETRIEVAL AT ALL. It asks one question — *is this question's
topic one of the ~20 the corpus was built for* — which is a CONSTANT comparison in R19's sense.
That is why it works on the fact path, where every D-FIDELITY rule before the sixth goes vacuous
because `amount is None`.

WHAT IT DELIBERATELY DOES NOT DO. Topic granularity IS the design. It holds `business_licence`,
not `business_licence_fee` vs `business_licence_renewal`; it holds `wht`, not the rent rate. Two
of the twelve get through for exactly that reason and that is a STATED LIMITATION, not a defect
to patch. Sub-topic cues are where an allowlist begins turning into the failure-driven list this
project has spent weeks closing; revisit only if a pilot shows those misses recurring.

WHY `kodi ya mapato` IS NOT A COVERED CUE, and this is the one place live evidence overrode the
scoping run. The scoped allowlist carried bare `kodi ya mapato` under `paye`. The 2026-08-23
canary showed production answering FOUR different obligations phrased that way, three of them
outside the corpus, each with an invented figure: corporate tax as 30% of TURNOVER
(TZS 15,000,000), a partnership given a rate and a fabricated TZS 2,500,000 monthly salary, and
an individual given a 30% flat rate on profit. **The phrase does not identify a topic**, so it
cannot be a covered cue. Only the qualified forms are.
"""
from __future__ import annotations

import re
from typing import List, Optional, Tuple

# --- What the corpus holds -------------------------------------------------------------------
# Derived from the topic clusters in scripts/locked_facts.json, NOT from any evaluation corpus.
# The false-refusal cost of this list is measured on eval/coverage/coverage_gate_heldout_040.jsonl,
# which was authored and FROZEN before this file existed. No cue here may be tuned against the
# 48, the 400-question gate corpus, or the 12 — that is the whole reason the probe set is
# held out.
COVERED_TOPICS = {
    'vat': ['vat', 'ongezeko la thamani', 'kodi ya ongezeko'],
    'efd': ['efd', 'mashine ya risiti', 'risiti'],
    # QUALIFIED FORMS ONLY — see the module docstring. Bare `kodi ya mapato` spans PAYE,
    # corporate, partnership and profit-based individual tax; three of those four are uncovered.
    'paye': ['paye', 'kodi ya mshahara', 'kodi ya mapato ya ajira',
             'kodi ya mapato ya mfanyakazi'],
    'sdl': ['sdl', 'mafunzo', 'ufundi stadi', 'skills development'],
    'nssf': ['nssf', 'hifadhi ya jamii', 'pensheni', 'mfuko wa hifadhi'],
    'wcf': ['wcf', 'fidia', 'ajali kazini', 'ameumia', 'kuumia kazini'],
    'minimum_wage': ['kima cha chini', 'mshahara wa chini', 'gn 605', 'gn605',
                     'mshahara', 'mishahara', 'kulipa mfanyakazi'],
    'brela_company': ['brela', 'kampuni', 'kusajili biashara', 'usajili wa biashara',
                      'jina la biashara', 'ritani', 'annual return', 'ubia', 'ushirikiano'],
    'trademark': ['alama ya biashara', 'trademark', 'nembo', 'chapa', 'miliki ya akili',
                  'intellectual property'],
    'osha': ['osha', 'usalama mahali pa kazi', 'afya na usalama', 'sehemu ya kazi'],
    'gn487a': ['mgeni', 'wageni', 'raia wa kigeni', 'non-citizen', 'msaidizi',
               'biashara zilizokatazwa', 'gn 487', 'gn487', '487a'],
    'permit': ['kibali', 'vibali', 'permit', 'residence permit', 'work permit'],
    'stamp_duty': ['stempu', 'stamp duty'],
    'presumptive': ['makadirio', 'makisio', 'presumptive'],
    'provisional_tax': ['provisional tax', 'kodi ya awali'],
    'wht': ['withholding', 'kodi ya zuio', 'zuio', 'wht', 'kukata kodi'],
    'objection_appeal': ['pingamizi', 'rufaa', 'objection', 'trab', 'kupinga'],
    'penalty': ['faini', 'adhabu', 'riba ya kuchelewa', 'penalty', 'kuchelewa kuwasilisha'],
    'business_licence': ['leseni ya biashara', 'business licence'],
    'exemption': ['msamaha', 'exemption', 'hairuhusiwi kutozwa'],
    'filing': ['tarehe ya mwisho', 'deadline', 'kuwasilisha ritani', 'kuwasilisha return'],
    'employment': ['mkataba wa ajira', 'mfanyakazi', 'wafanyakazi', 'kuajiri', 'likizo'],
}

_COVERED_CUES: List[Tuple[str, str]] = [
    (topic, cue) for topic, cues in COVERED_TOPICS.items() for cue in cues]

# --- Where to send someone we cannot help ----------------------------------------------------
# THE REFUSAL ROUTES RATHER THAN DEAD-ENDS. "I don't know" and "that is the council's, not mine"
# are different answers, and for a compliance product the second is a useful one — the user
# leaves knowing which door to knock on.
#
# Authored from which Tanzanian body actually owns each obligation, NOT from probe outcomes. A
# question with no entry here still refuses; it just gets the generic copy. That asymmetry is
# deliberate: this map may only ever improve a refusal, never cause or prevent one.
#
# (cue, topic in Swahili, authority, contact)
UNCOVERED_AUTHORITIES: List[Tuple[str, str, str, str]] = [
    ('ushuru wa soko', 'ushuru wa soko', 'halmashauri yako', 'ofisi ya halmashauri'),
    ('genge', 'ushuru wa soko', 'halmashauri yako', 'ofisi ya halmashauri'),
    ('ushuru wa huduma', 'ushuru wa huduma wa halmashauri', 'halmashauri yako',
     'ofisi ya halmashauri'),
    ('bango la matangazo', 'ada ya matangazo', 'halmashauri yako', 'ofisi ya halmashauri'),
    ('zimamoto', 'cheti cha usalama wa moto', 'Jeshi la Zimamoto na Uokoaji', 'moto.go.tz'),
    ('usalama wa moto', 'cheti cha usalama wa moto', 'Jeshi la Zimamoto na Uokoaji',
     'moto.go.tz'),
    ('mizani', 'upimaji wa mizani', 'Wakala wa Vipimo (WMA)', 'wma.go.tz'),
    ('wakala wa vipimo', 'upimaji wa mizani', 'Wakala wa Vipimo (WMA)', 'wma.go.tz'),
    ('tmda', 'usajili wa bidhaa za dawa na vipodozi', 'TMDA', 'tmda.go.tz'),
    ('vipodozi', 'usajili wa bidhaa za dawa na vipodozi', 'TMDA', 'tmda.go.tz'),
    ('tbs', 'viwango vya ubora wa bidhaa', 'TBS', 'tbs.go.tz'),
    ('pango la ardhi', 'kodi ya pango la ardhi', 'Wizara ya Ardhi', 'ardhi.go.tz'),
    ('ushuru wa mazao', 'ushuru wa mazao', 'halmashauri yako', 'ofisi ya halmashauri'),
    ('tozo ya utalii', 'tozo ya utalii', 'Bodi ya Utalii Tanzania (TTB)', 'tanzaniatourism.go.tz'),
    ('kisima', 'kibali cha matumizi ya maji', 'Bodi ya Maji ya Bonde', 'maji.go.tz'),
    ('ushuru wa bidhaa', 'ushuru wa bidhaa (excise)', 'TRA', 'tra.go.tz'),
    ('stempu za kielektroniki', 'stempu za kielektroniki (ETS)', 'TRA', 'tra.go.tz'),
    ('leseni ya barabara', 'leseni ya barabara', 'TRA', 'tra.go.tz'),
    ('kodi ya mapato ya kampuni', 'kodi ya mapato ya kampuni', 'TRA', 'tra.go.tz'),
    ('daladala', 'jedwali la kodi ya makadirio kwa usafirishaji', 'TRA', 'tra.go.tz'),
    ('tin', 'usajili wa TIN', 'TRA', 'tra.go.tz'),
    ('ukaguzi wa tra', 'ukaguzi wa TRA', 'TRA', 'tra.go.tz'),
]

_WORD_EDGE = r'(?<![a-z0-9])%s(?![a-z0-9])'

COVERED_DOMAINS_SW = 'BRELA, TRA, NSSF, OSHA, SDL, PAYE, VAT, EFD, WCF na GN487A'


def _matches(cue: str, ql: str) -> bool:
    """Word-edge containment.

    Word edges, not bare substrings: the 2026-08-23 coverage harness reported `tin` matching
    inside `lis-TIN-g` across 29 facts, and that error was in the direction that FLATTERS
    coverage — 7 of 12 rather than 3. A measurement bug that overstates coverage is the one that
    ships a pilot.
    """
    return re.search(_WORD_EDGE % re.escape(cue), ql) is not None


def covered_topics(text: str) -> List[str]:
    """Every corpus topic this text names, in COVERED_TOPICS order. Empty means uncovered."""
    ql = (text or '').lower()
    out: List[str] = []
    for topic, cue in _COVERED_CUES:
        if topic not in out and _matches(cue, ql):
            out.append(topic)
    return out


def is_covered(text: str) -> bool:
    return bool(covered_topics(text))


def uncovered_authority(text: str) -> Optional[Tuple[str, str, str]]:
    """(topic_sw, authority, contact) when we can name who owns this, else None."""
    ql = (text or '').lower()
    for cue, topic_sw, authority, contact in UNCOVERED_AUTHORITIES:
        if _matches(cue, ql):
            return topic_sw, authority, contact
    return None


def refusal_text(text: str) -> str:
    """The refusal. Names the topic and the authority; never offers a figure.

    Opens with `Sina uhakika`, which is the project's own referral formula and is in
    REFUSAL_PHRASES, so a refusal produced here is recognised as one by the refusal gate rather
    than scored as a wrong answer.
    """
    named = uncovered_authority(text)
    if named is not None:
        topic_sw, authority, contact = named
        return (f'Sina uhakika kuhusu {topic_sw} — hili ni la {authority}, si mada yangu, '
                f'hivyo sitakupa kiwango wala kiasi. Thibitisha na {authority} ({contact}). '
                f'Mimi ninashughulikia {COVERED_DOMAINS_SW}.')
    return ('Sina uhakika kuhusu hili — sina taarifa iliyothibitishwa kwenye eneo hili, '
            f'hivyo sitakupa kiwango wala kiasi. Mimi ninashughulikia {COVERED_DOMAINS_SW}; '
            'kwa swali hili wasiliana na TRA (tra.go.tz) au mamlaka husika.')
