# -*- coding: utf-8 -*-
"""SCOPING ARM 2 — a CURATED COVERED-TOPIC ALLOWLIST, the design the generic-overlap arm did not test.

WHY A SECOND ARM. Arm 1 (`measure_coverage_gate_signals.py`) measured generic term overlap
between the question and the index, and the result was decisive and negative: to catch 4 of the
12 uncovered questions it falsely refuses 38 answerable ones. It fails for a structural reason —
the index is 221 rows of dense compliance prose, so nearly every Swahili business question shares
SOME content token with SOME fact, covered or not. Overlap does not separate the two populations.

An allowlist is a different signal and has to be measured separately: instead of asking *does
this question resemble the index*, it asks *is this question's topic one of the ~20 the corpus
was built for*. That is a CONSTANT comparison in R19's sense — it consults no score, needs no
engine result, and works on the fact path where every existing fidelity rule goes vacuous.

HOW THE LIST WAS BUILT, and why that matters for reading the numbers. The cues are derived from
the CORPUS side — the topic clusters in `scripts/locked_facts.json` (gn487a 32 facts, vat 19,
trademark 18, company/brela 24, paye 8, sdl 7, nssf 7, wcf 7, minimum wage 13, osha 7, efd 4,
permits 4, stamp duty 3, presumptive 3, wht 2, objections 3, penalties 4, exemptions 10) — and
NOT from the evaluation questions. Authoring cues by reading the test set would measure the
author, not the design.

THE FAILURE MODE BEING PRICED IS STILL FALSE REFUSAL. An allowlist refuses by DEFAULT, so its
risk profile is the opposite of a phrase blocklist and strictly worse on this axis: every
covered question phrased in vocabulary nobody thought of is refused. That is why the headline
number below is what it refuses on the 400 gate questions and the 27 in-scope adversarial
probes, not what it catches.

TWO MATCHING RULES, both reported: SUBSTRING (an inflection-tolerant containment test, matching
how the OOC phrase list already works in production) and WORD-BOUNDED. The 2026-08-23 coverage
harness was wrong precisely because it used bare substrings, so the difference is measured here
rather than assumed.

R18: committed before its result is written up.
Artifact: eval/results/coverage_gate_allowlist.json
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)

sys.path.insert(0, HERE)

from chike import decomposition, routing                                    # noqa: E402
# Reuse arm 1's loader verbatim rather than re-deriving it: the two arms MUST see byte-identical
# corpora or their false-refusal counts are not comparable. `eval/` is not a package, hence the
# path insert above rather than a dotted import.
from measure_coverage_gate_signals import load_corpora                      # noqa: E402

OUT = os.path.join(REPO, 'eval', 'results', 'coverage_gate_allowlist.json')

# Topic -> the words a user would actually type for it. Corpus-derived (see docstring).
# Deliberately generous: an allowlist's danger is being too NARROW, so a scoping measurement
# should give the design its best case rather than its worst.
COVERED = {
    'vat': ['vat', 'ongezeko la thamani', 'kodi ya ongezeko'],
    'efd': ['efd', 'mashine ya risiti', 'risiti'],
    'paye': ['paye', 'kodi ya mshahara', 'kodi ya mapato'],
    'sdl': ['sdl', 'mafunzo', 'ufundi stadi', 'skills development'],
    'nssf': ['nssf', 'hifadhi ya jamii', 'pensheni', 'mfuko wa hifadhi'],
    'wcf': ['wcf', 'fidia', 'ajali kazini', 'ameumia', 'kuumia kazini'],
    'minimum_wage': ['kima cha chini', 'mshahara wa chini', 'gn 605', 'gn605',
                     'mshahara', 'kulipa mfanyakazi'],
    'brela_company': ['brela', 'kampuni', 'kusajili biashara', 'usajili wa biashara',
                      'jina la biashara', 'ritani', 'annual return', 'ubia', 'ushirikiano'],
    'trademark': ['alama ya biashara', 'trademark', 'nembo', 'chapa'],
    'osha': ['osha', 'usalama mahali pa kazi', 'afya na usalama', 'sehemu ya kazi'],
    'gn487a': ['mgeni', 'wageni', 'raia wa kigeni', 'non-citizen', 'msaidizi',
               'biashara zilizokatazwa'],
    'permit': ['kibali', 'permit', 'residence permit', 'work permit'],
    'stamp_duty': ['stempu', 'stamp duty'],
    'presumptive': ['makadirio', 'makisio', 'presumptive'],
    'wht': ['withholding', 'kodi ya zuio', 'zuio', 'wht', 'kukata kodi'],
    'objection_appeal': ['pingamizi', 'rufaa', 'objection', 'trab', 'kupinga'],
    'penalty': ['faini', 'adhabu', 'riba ya kuchelewa', 'penalty', 'kuchelewa kuwasilisha'],
    'business_licence': ['leseni ya biashara', 'business licence'],
    'exemption': ['msamaha', 'exemption', 'hairuhusiwi kutozwa'],
    'filing': ['tarehe ya mwisho', 'deadline', 'kuwasilisha ritani', 'kuwasilisha return'],
    'employment': ['mkataba wa ajira', 'mfanyakazi', 'wafanyakazi', 'kuajiri', 'likizo'],
}

# --- v2 CORRECTIONS, and why each one is NOT fitting to the test set -------------------------
# v1 scored 34 false refusals. Reading all 34 (rather than the count) showed that only a
# minority were the design failing; the rest were two authoring faults and one measurement
# fault. The corrections below are admitted ONLY because each is justified from the CORPUS
# side and would have been written by anyone who had checked the list against locked_facts:
#
#   (a) THE TOPIC'S OWN NAME WAS MISSING. Nineteen of the 34 were GN 487A questions containing
#       the literal string "GN 487A" — the largest cluster in locked_facts (32 facts) and I
#       omitted its name. Likewise `miliki ya akili` (trademark, 18 facts) and provisional tax.
#       Adding a topic's own name is completing the list, not tuning it.
#   (b) SWAHILI NOUN-CLASS PLURALS. `mshahara`->`mishahara` (m-/mi-) and `kibali`->`vibali`
#       (ki-/vi-) are the standard plural forms; a substring cue on the singular cannot match
#       them. This is THE THIRD AXIS from the concord work — a cue list is blind to inflection
#       unless the inflections are enumerated — arriving in a new list.
#
# ANY FURTHER CUE ADDED BY READING THIS CORPUS WOULD BE FITTING TO THE TEST SET, and its cost
# would have to be priced on held-out probes instead (R17 step 2). The residue after these two
# classes is reported separately below and is the design's honest irreducible cost.
CORRECTIONS = {
    'gn487a': ['gn 487', 'gn487', '487a'],
    'trademark': ['miliki ya akili', 'intellectual property'],
    'minimum_wage': ['mishahara'],
    'permit': ['vibali'],
    'provisional_tax': ['provisional tax', 'kodi ya awali'],
}

COVERED_V2 = {t: list(c) for t, c in COVERED.items()}
for t, cues in CORRECTIONS.items():
    COVERED_V2.setdefault(t, [])
    COVERED_V2[t] += [c for c in cues if c not in COVERED_V2[t]]

# Rows in the accuracy-gate files whose subdomain is `out_of_corpus` are questions the product
# is SUPPOSED to refuse (import duty, Zanzibar, Bitcoin). v1 counted a coverage-gate refusal on
# those as a FALSE refusal, which is backwards — a measurement fault, not a design one.
CORRECT_TO_REFUSE = 'out_of_corpus'

_ALL_CUES = [(topic, cue) for topic, cues in COVERED.items() for cue in cues]
_ALL_CUES_V2 = [(topic, cue) for topic, cues in COVERED_V2.items() for cue in cues]


def matched_topics(text, word_bounded, cues=None):
    ql = text.lower()
    out = []
    for topic, cue in (cues if cues is not None else _ALL_CUES):
        if word_bounded:
            hit = re.search(r'(?<![a-z])' + re.escape(cue) + r'(?![a-z])', ql) is not None
        else:
            hit = cue in ql
        if hit and topic not in out:
            out.append(topic)
    return out


def main():
    corpora = load_corpora()
    results = {}
    for name, rows in corpora.items():
        out_rows = []
        for r in rows:
            parts = decomposition.decompose_query(r['q'])
            intents = [routing.detect_intent(p) for p in parts]
            route = next((x for x in intents if x != 'none'), 'none')
            out_rows.append({
                'id': r['id'], 'q': r['q'], 'subdomain': r.get('subdomain'),
                'verdict': r.get('verdict'), 'route': route,
                'topics_substring': matched_topics(r['q'], word_bounded=False),
                'topics_wordbound': matched_topics(r['q'], word_bounded=True),
                'v2_substring': matched_topics(r['q'], False, _ALL_CUES_V2),
                'v2_wordbound': matched_topics(r['q'], True, _ALL_CUES_V2),
            })
        results[name] = out_rows

    candidates = []
    for rule in ('topics_substring', 'topics_wordbound', 'v2_substring', 'v2_wordbound'):
        for fpo in (True, False):
            c = {'rule': rule, 'fact_path_only': fpo, 'per_corpus': {}}
            for name, rows in results.items():
                ref = [r for r in rows
                       if (not (fpo and r['route'] != 'none')) and not r[rule]]
                # An `out_of_corpus` row refused by the coverage gate is a CORRECT refusal, not
                # a false one — it belongs in the catch column, not the cost column.
                ooc_ref = [r for r in ref if r.get('subdomain') == CORRECT_TO_REFUSE]
                ref = [r for r in ref if r.get('subdomain') != CORRECT_TO_REFUSE]
                entry = {'n': len(rows), 'refused': len(ref),
                         'correctly_refused_ooc': len(ooc_ref),
                         'rate': round(len(ref) / len(rows), 4),
                         'refused_ids': [r['id'] for r in ref][:40]}
                if name == 'natural_48':
                    entry['refused_that_were_CORRECT'] = sum(
                        1 for r in ref if (r['verdict'] or '').startswith('CORRECT'))
                if name == 'uncovered_12':
                    entry['caught'] = [r['id'] for r in ref]
                    entry['missed'] = [{'id': r['id'], 'matched': r[rule]}
                                       for r in rows if r not in ref]
                c['per_corpus'][name] = entry
            c['ooc_correctly_refused'] = sum(
                v.get('correctly_refused_ooc', 0) for v in c['per_corpus'].values())
            c['false_refusals_total'] = (c['per_corpus']['gate_400']['refused']
                                         + c['per_corpus']['inscope_69']['refused']
                                         + c['per_corpus']['natural_48']
                                         ['refused_that_were_CORRECT'])
            c['caught_of_12'] = c['per_corpus']['uncovered_12']['refused']
            candidates.append(c)

    out = {
        'measured': '2026-08-23',
        'harness': 'eval/coverage/measure_topic_allowlist.py',
        'purpose': 'SCOPING ARM 2. Prices a curated covered-topic allowlist. Designs nothing; '
                   'the list here is a corpus-derived best case, authored without reading the '
                   'evaluation questions.',
        'n_topics': len(COVERED),
        'n_cues': len(_ALL_CUES),
        'n_cues_v2': len(_ALL_CUES_V2),
        'allowlist': COVERED,
        'corrections_v2': CORRECTIONS,
        'v2_rationale': "v1's 34 false refusals were read individually rather than counted. "
                        "Two authoring faults (a topic's own name missing; Swahili noun-class "
                        "plurals) and one measurement fault (out_of_corpus rows counted as "
                        "false refusals). v2 fixes all three. No cue was added by reading a "
                        "question the design should have answered but did not for any other "
                        "reason — that would be fitting to the test set.",
        'candidates': candidates,
        'rows': results,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f'v1: {len(COVERED)} topics, {len(_ALL_CUES)} cues | v2: {len(_ALL_CUES_V2)} cues')
    print(f"\n  {'rule':<20}{'factOnly':>9}{'falseRef':>10}{'caught/12':>11}"
          f"{'oocOK':>7}{'gate400':>9}{'insc69':>8}{'nat48ok':>9}")
    for c in candidates:
        p = c['per_corpus']
        print(f"  {c['rule']:<20}{str(c['fact_path_only']):>9}"
              f"{c['false_refusals_total']:>10}{c['caught_of_12']:>11}"
              f"{c['ooc_correctly_refused']:>7}"
              f"{p['gate_400']['refused']:>9}{p['inscope_69']['refused']:>8}"
              f"{p['natural_48']['refused_that_were_CORRECT']:>9}")
    best = min((c for c in candidates if c['rule'].startswith('v2')),
               key=lambda c: (c['false_refusals_total'], -c['caught_of_12']))
    print(f"\n=== lowest-cost v2 variant: {best['rule']} fact_path_only="
          f"{best['fact_path_only']} ===")
    print('\n--- lowest-cost variant, what it MISSED on the 12 ---')
    for m in best['per_corpus']['uncovered_12']['missed']:
        print(f"  {m['id'][:44]:<46} matched {m['matched']}")
    print('\n--- lowest-cost variant, first false refusals on gate_400 ---')
    for rid in best['per_corpus']['gate_400']['refused_ids'][:15]:
        row = next(r for r in results['gate_400'] if r['id'] == rid)
        print(f"  {rid:<12} {row['q'][:88]}")
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()
