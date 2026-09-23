# -*- coding: utf-8 -*-
"""Tallies eval/results/extended_078_adjudication_2026_09_23.json by category and by cause,
and runs the ONE pre-registered test in this exercise: the founder predicted, BEFORE results
were read, that the untouched-facts category (ext_63-78) would score WORSE than the rest,
since it is the only category drawn independently of what has been worked on.

The honest comparison is untouched-vs-OTHER-FACT-INTENT rows, not untouched-vs-everything:
the full set contains 12 rows whose correct behaviour is a REFUSAL (coverage gaps, OOC,
unbuilt domains) and 14 compute rows, and mixing those into the baseline would compare
different tasks rather than different populations (R22).

R18: committed with the write-up that cites it.
Artifact read: eval/results/extended_078_adjudication_2026_09_23.json
"""
import json
import os
import sys
from collections import Counter, defaultdict
from math import comb

sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def fisher_two_sided(a, b, c, d):
    """Two-sided Fisher exact p for the 2x2 table [[a,b],[c,d]]. Used instead of a
    hand-picked effect-size threshold so a small-n difference cannot be reported as a
    finding (see the VERDICT block below)."""
    n = a + b + c + d
    r1, r2, c1 = a + b, c + d, a + c

    def prob(x):
        y, z, w = r1 - x, c1 - x, r2 - (c1 - x)
        if y < 0 or z < 0 or w < 0:
            return 0.0
        return comb(r1, x) * comb(r2, z) / comb(n, c1)

    obs = prob(a)
    return sum(p for x in range(min(r1, c1) + 1)
               if (p := prob(x)) and p <= obs + 1e-12)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
ADJ = os.path.join(REPO, 'eval', 'results', 'extended_078_adjudication_2026_09_23.json')
PROBES = os.path.join(REPO, 'eval', 'accuracy_gate', 'edge_probe_extended_078_DRAFT.jsonl')

CLEAN = {'PASS', 'PASS_BY_OUTCOME'}


def main():
    adj = json.load(open(ADJ, encoding='utf-8'))
    rows = adj['rows']
    assert len(rows) == 78, f'expected 78 adjudicated rows, got {len(rows)}'

    probes = {json.loads(l)['id']: json.loads(l)
              for l in open(PROBES, encoding='utf-8') if l.strip()}
    assert len(probes) == 78, f'expected 78 probes, got {len(probes)}'
    missing = [r['id'] for r in rows if r['id'] not in probes]
    assert not missing, f'adjudicated ids absent from the probe file: {missing}'

    print('=== VERDICTS ===')
    for v, n in Counter(r['verdict'] for r in rows).most_common():
        print(f'  {v:<16} {n:>3}  ({n / len(rows):.1%})')

    print('\n=== CAUSE OF NON-PASS ===')
    causes = Counter(r['cause'] for r in rows if r['verdict'] not in CLEAN and r['cause'])
    for c, n in causes.most_common():
        print(f'  {c:<22} {n:>3}')
    not_model = sum(n for c, n in causes.items() if c != 'model')
    print(f'  -- of which NOT a model accuracy failure: {not_model}')

    print('\n=== BY CATEGORY ===')
    bycat = defaultdict(list)
    for r in rows:
        bycat[r['cat']].append(r)
    for cat in sorted(bycat):
        rs = bycat[cat]
        ok = sum(1 for r in rs if r['verdict'] in CLEAN)
        marks = ' '.join(('OK' if r['verdict'] in CLEAN
                          else ('--' if r['verdict'] == 'PARTIAL'
                                else ('??' if r['verdict'] == 'UNADJUDICABLE' else 'XX')))
                         for r in rs)
        print(f'  {cat:<34} {ok}/{len(rs)}   {marks}')

    # ---- the pre-registered prediction ----
    print('\n=== PRE-REGISTERED PREDICTION ===')
    print('  Predicted before results: untouched facts (ext_63-78) score WORSE than the rest.')
    untouched = [r for r in rows if r['cat'].startswith('untouched_')]
    assert untouched, 'no untouched_* rows found -- category naming changed?'

    # Comparison baseline: other rows whose probe intent is a plain fact lookup.
    other_fact = [r for r in rows
                  if not r['cat'].startswith('untouched_')
                  and probes[r['id']]['intent_expected'] == 'fact']
    assert other_fact, 'no comparison population -- intent_expected values changed?'

    for label, pop in (('untouched facts', untouched), ('other fact-intent rows', other_fact)):
        ok = sum(1 for r in pop if r['verdict'] in CLEAN)
        wrong = sum(1 for r in pop if r['verdict'] == 'WRONG')
        print(f'  {label:<26} n={len(pop):>3}  clean={ok:>3} ({ok / len(pop):.1%})'
              f'   wrong={wrong:>3} ({wrong / len(pop):.1%})')

    ua = sum(1 for r in untouched if r['verdict'] in CLEAN)
    oa = sum(1 for r in other_fact if r['verdict'] in CLEAN)
    gap = ua / len(untouched) - oa / len(other_fact)
    pval = fisher_two_sided(ua, len(untouched) - ua, oa, len(other_fact) - oa)
    print(f'\n  gap (untouched - other) = {gap:+.1%}   Fisher exact two-sided p = {pval:.3f}')

    # Deliberately NOT a bare directional verdict. An earlier version of this script
    # declared "prediction confirmed" on a hand-picked +/-5pp threshold, which would have
    # reported a p=0.52 difference as a finding -- a verdict line that cannot tell signal
    # from noise is the vacuous-check shape R20 exists to catch, arriving in a tally.
    if pval > 0.05:
        print('  VERDICT: DIRECTION CONSISTENT, NOT ESTABLISHED. The untouched arm is lower,'
              f'\n           but at n={len(untouched)} vs {len(other_fact)} this difference is'
              ' indistinguishable from chance.'
              '\n           Do not scope work on this gap. To settle it, widen the untouched'
              ' arm -- it is\n           the cheaper of the two populations to author.')
    else:
        print('  VERDICT: prediction confirmed at p<0.05.')


if __name__ == '__main__':
    main()
