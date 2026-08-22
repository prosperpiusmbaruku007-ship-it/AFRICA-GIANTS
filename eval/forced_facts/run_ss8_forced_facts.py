# -*- coding: utf-8 -*-
"""SS8 forced-fact re-measurement against the LIVE deployed pipeline.

Calls ChikeModel().run_forced_facts.remote() via modal.Cls.from_name — the same pattern
chike-whatsapp uses — through the already-authenticated local Modal CLI session.

R16: writes its artifact to a file directly. NEVER pipe this through Select-Object, head,
more or Select-String — a truncating consumer has twice killed a measurement run in this
project before it wrote its file.

R18: committed before it is run. Artifact path is fixed and versioned so the write-up can
cite it.
"""
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import modal  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
FIXTURE = os.path.join(HERE, 'ss8_rows.json')
OUT = os.path.join(REPO, 'eval', 'results', 'ss8_forced_facts_v16_2026_08_22.json')


def main():
    with open(FIXTURE, encoding='utf-8') as f:
        fixture = json.load(f)

    ChikeModel = modal.Cls.from_name('chike-inference', 'ChikeModel')
    results = []

    for row in fixture['rows']:
        print(f"\n=== {row['id']} ===")
        print(f"Q: {row['question']}")
        print(f"forced: {row['forced_fact_rationale']} ({len(row['forced_facts'])} fact(s))")
        rec = {
            'id': row['id'],
            'question': row['question'],
            'forced_facts': row['forced_facts'],
            'forced_fact_rationale': row['forced_fact_rationale'],
            'expected_behavior': row['expected_behavior'],
            'provisional_2026_08_22_outcome': row['provisional_2026_08_22_outcome'],
        }
        t0 = time.time()
        try:
            resp = ChikeModel().run_forced_facts.remote(
                row['question'], row['forced_facts'])
            rec['raw_response'] = resp
            rec['reply'] = resp.get('reply', '') if isinstance(resp, dict) else str(resp)
            rec['pipeline_reported'] = (
                resp.get('pipeline') if isinstance(resp, dict) else None)
            print(f"pipeline: {rec['pipeline_reported']}")
            print(f"A: {rec['reply']}")
        except Exception as e:
            rec['error'] = f'{type(e).__name__}: {e}'
            print(f"ERROR: {rec['error']}")
        rec['elapsed_s'] = round(time.time() - t0, 1)
        results.append(rec)

    out = {
        'measured': '2026-08-22',
        'target': 'live chike-inference, pipeline as deployed',
        'harness': 'eval/forced_facts/run_ss8_forced_facts.py',
        'instrument': 'ChikeModel.run_forced_facts (chike-inference/modal_app.py)',
        'fixture': 'eval/forced_facts/ss8_rows.json',
        'pipelines_reported': sorted(
            {r.get('pipeline_reported') for r in results if r.get('pipeline_reported')}),
        'rows': results,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f'\n[saved] {OUT}')
    print(f"[pipelines reported] {out['pipelines_reported']}")


if __name__ == '__main__':
    main()
