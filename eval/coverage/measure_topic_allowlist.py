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

_ALL_CUES = [(topic, cue) for topic, cues in COVERED.items() for cue in cues]


def matched_topics(text, word_bounded):
    ql = text.lower()
    out = []
    for topic, cue in _ALL_CUES:
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
            })
        results[name] = out_rows

    candidates = []
    for rule in ('topics_substring', 'topics_wordbound'):
        for fpo in (True, False):
            c = {'rule': rule, 'fact_path_only': fpo, 'per_corpus': {}}
            for name, rows in results.items():
                ref = [r for r in rows
                       if (not (fpo and r['route'] != 'none')) and not r[rule]]
                entry = {'n': len(rows), 'refused': len(ref),
                         'rate': round(len(ref) / len(rows), 4),
                         'refused_ids': [r['id'] for r in ref][:30]}
                if name == 'natural_48':
                    entry['refused_that_were_CORRECT'] = sum(
                        1 for r in ref if r['verdict'] == 'CORRECT')
                if name == 'uncovered_12':
                    entry['caught'] = [r['id'] for r in ref]
                    entry['missed'] = [{'id': r['id'], 'matched': r[rule]}
                                       for r in rows if r not in ref]
                c['per_corpus'][name] = entry
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
        'allowlist': COVERED,
        'candidates': candidates,
        'rows': results,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f'{len(COVERED)} topics, {len(_ALL_CUES)} cues')
    print(f"\n  {'rule':<20}{'factOnly':>9}{'falseRef':>10}{'caught/12':>11}"
          f"{'gate400':>9}{'insc69':>8}{'nat48ok':>9}")
    for c in candidates:
        p = c['per_corpus']
        print(f"  {c['rule']:<20}{str(c['fact_path_only']):>9}"
              f"{c['false_refusals_total']:>10}{c['caught_of_12']:>11}"
              f"{p['gate_400']['refused']:>9}{p['inscope_69']['refused']:>8}"
              f"{p['natural_48']['refused_that_were_CORRECT']:>9}")
    best = min(candidates, key=lambda c: (c['false_refusals_total'], -c['caught_of_12']))
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
