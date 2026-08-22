# -*- coding: utf-8 -*-
"""How many index rows look like the malformed ones that out-ranked real SDL facts?

Found via eval/routing/measure_numeral_form_retrieval.py: a plain SDL applicability question
retrieved 'minimum shareholders: 2 employees', 'unpaid contribution penalty rate: five %' and
'minimum directors: 2 employees' — none of them SDL facts, and all three malformed.

This converts 'scope unknown' into a counted number. It is a HEURISTIC, deliberately stated as
one: it flags shapes, not wrongness, and every hit needs human adjudication before anything is
rewritten. Three independent signals, reported separately so they can be argued with:

  A. english_key_value  — '<lowercase english key>: <short value>' fragment rows
  B. spelled_numeral    — an English or Swahili numeral WORD where a figure belongs
  C. suspect_unit       — a count/period value carrying the wrong unit noun
                          ('shareholders: 2 employees', 'renewal period: saba years')

R18: committed before its result is written up.
Artifact: eval/results/index_fragment_scan.json
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
INDEX = os.path.join(REPO, 'chike-inference', 'rag_facts_text.json')
OUT = os.path.join(REPO, 'eval', 'results', 'index_fragment_scan.json')

KEY_VALUE = re.compile(r'^[a-z][a-z0-9 /()\-]{2,60}:\s*(.{1,40})$')
EN_NUM = r'one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve'
SW_NUM = r'moja|mbili|tatu|nne|tano|sita|saba|nane|tisa|kumi'
SPELLED = re.compile(rf'\b(?:{EN_NUM}|{SW_NUM})\b\s*(?:%|years?|weeks?|months?|days?|employees?)',
                     re.I)
# a numeric count followed by a unit noun that does not match the key's subject
SUSPECT_UNIT = re.compile(
    r'(shareholders?|directors?|renewal period|validity|duration|threshold)\b[^:]*:\s*'
    r'\d+\s*(employees?|years?|weeks?|months?|days?)', re.I)


def main():
    with open(INDEX, encoding='utf-8') as f:
        texts = json.load(f)

    hits = {'english_key_value': [], 'spelled_numeral': [], 'suspect_unit': []}
    for i, t in enumerate(texts):
        row = {'position': i, 'text': t}
        if KEY_VALUE.match(t.strip()):
            hits['english_key_value'].append(row)
        if SPELLED.search(t):
            hits['spelled_numeral'].append(row)
        if SUSPECT_UNIT.search(t):
            hits['suspect_unit'].append(row)

    any_hit = sorted({r['position'] for v in hits.values() for r in v})
    out = {
        'measured': '2026-08-22',
        'index': 'chike-inference/rag_facts_text.json',
        'total_rows': len(texts),
        'method': 'HEURISTIC shape detector — flags shapes, not wrongness; every hit needs '
                  'human adjudication before any rewrite',
        'counts': {k: len(v) for k, v in hits.items()},
        'rows_matching_any': len(any_hit),
        'share_of_index': round(len(any_hit) / len(texts), 3),
        'positions_matching_any': any_hit,
        'hits': hits,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"index rows: {len(texts)}")
    for k, v in hits.items():
        print(f"  {k}: {len(v)}")
    print(f"  matching ANY signal: {len(any_hit)} ({out['share_of_index']:.1%})")
    print('\n--- sample of suspect_unit ---')
    for r in hits['suspect_unit'][:10]:
        print(f"  [{r['position']}] {r['text'][:100]}")
    print('\n--- sample of spelled_numeral ---')
    for r in hits['spelled_numeral'][:10]:
        print(f"  [{r['position']}] {r['text'][:100]}")
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()
