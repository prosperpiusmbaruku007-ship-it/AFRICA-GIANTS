#!/usr/bin/env python3
"""
SIBLING-MATCH AUDIT — is every key the checker resolves via SIBLING actually
resolved to the row that answers it, or merely to a row that shares a slug fragment?

WHY THIS EXISTS (2026-08-26). The fee-consolidation work exposed a live instance:
removing `late_filing_penalty_monthly_fee_section_12_act`'s own row deleted the ONLY
thing standing between `late_filing_penalty_monthly_fee` (a DIFFERENT key, the
TZS 2,500 domestic fee) and drift -- because that unrelated row was the SIBLING match
`_is_sibling` was resolving it against. The two facts share nothing but a slug prefix.
`_is_sibling` was already tightened once before (2026-08-17, the 'nssf'/'brela'
single-word incident) for exactly this failure shape. This audit asks the standing
question directly: of every key CURRENTLY resolving via sibling match, how many are
verified by CONTENT (the key's own figure appears in the matched row) versus resolving
on slug-fragment coincidence alone, unverified?

THIS DOES NOT SCORE. It partitions sibling matches into:
  - figure_confirmed:   the key's own extracted figure appears in the matched row(s).
                         Strong evidence the row actually answers this key.
  - no_figure_to_check: fact_value has no extractable figure (citations, prose claims).
                         Cannot be auto-verified; needs a human read, same as any PINNED
                         present_elsewhere entry.
  - figure_NOT_found:   the key has a figure and it does NOT appear in the matched
                         row(s). This is the dangerous bucket -- the same shape as the
                         late_filing_penalty_monthly_fee case: a sibling match that is
                         not backed by content and would go undetected as drift the
                         moment the coincidental row disappears.

Run: python eval/index_quality/audit_sibling_matches.py
Output: eval/results/sibling_match_audit.json
"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.normpath(os.path.join(_HERE, '..', '..'))
sys.path.insert(0, os.path.join(_REPO, 'scripts'))

from check_facts_index_sync import (  # noqa: E402
    FACTS_PATH, INDEX_PATH, _is_sibling, _key_slug, check,
)
from precompute_rag_embeddings import _figure_of, fact_value  # noqa: E402


def audit(facts_path=FACTS_PATH, index_path=INDEX_PATH):
    locked = json.load(open(facts_path, encoding='utf-8'))
    index = json.load(open(index_path, encoding='utf-8'))
    index_slugs = [f.split(':')[0].strip().lower() for f in index]

    _ok, report = check(facts_path, index_path)

    rows = []
    for key in report['sibling']:
        slug = _key_slug(key)
        matched = [(i, index_slugs[i], index[i]) for i in range(len(index))
                   if _is_sibling(slug, index_slugs[i])]
        fig = _figure_of(fact_value(locked[key]))
        if fig is None:
            verdict = 'no_figure_to_check'
        elif any(fig in text for _, _, text in matched):
            verdict = 'figure_confirmed'
        else:
            verdict = 'figure_NOT_found'
        rows.append({
            'key': key,
            'fact_value': fact_value(locked[key])[:120],
            'figure': fig,
            'matched_rows': [{'row': i, 'index_slug': s, 'text': t[:160]}
                              for i, s, t in matched],
            'verdict': verdict,
        })

    summary = {
        'total_sibling_keys': len(rows),
        'figure_confirmed': sum(1 for r in rows if r['verdict'] == 'figure_confirmed'),
        'no_figure_to_check': sum(1 for r in rows if r['verdict'] == 'no_figure_to_check'),
        'figure_NOT_found': sum(1 for r in rows if r['verdict'] == 'figure_NOT_found'),
    }
    return summary, rows


def main():
    summary, rows = audit()
    out = {'index_path': INDEX_PATH, 'summary': summary, 'rows': rows}
    os.makedirs(os.path.join(_REPO, 'eval', 'results'), exist_ok=True)
    out_path = os.path.join(_REPO, 'eval', 'results', 'sibling_match_audit.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"sibling-resolved keys: {summary['total_sibling_keys']}")
    print(f"  figure CONFIRMED in matched row   {summary['figure_confirmed']}")
    print(f"  no figure to check (needs a read) {summary['no_figure_to_check']}")
    print(f"  figure NOT found in matched row   {summary['figure_NOT_found']}  <-- suspect")
    print()
    suspects = [r for r in rows if r['verdict'] == 'figure_NOT_found']
    if suspects:
        print('SUSPECT sibling matches (figure not found in the row the checker accepted):')
        for r in suspects:
            print(f"  {r['key']!r}: value={r['fact_value']!r} figure={r['figure']!r}")
            for m in r['matched_rows']:
                print(f"      -> row {m['row']} ({m['index_slug']!r}): {m['text']!r}")
    print(f"\nwrote {out_path}")


if __name__ == '__main__':
    main()
