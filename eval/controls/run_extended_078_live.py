# -*- coding: utf-8 -*-
"""Runs all 78 rows of eval/accuracy_gate/edge_probe_extended_078_DRAFT.jsonl live against
production (chike-inference). Adjudication is NOT done here -- this only captures replies,
per-row, flushed immediately (R16 structural fix: a dropped connection loses at most one row).

Adjudication (against primary sources, not locked_facts.json -- 15 of these target facts
have never been verified against a primary source) happens as a separate pass, reading this
artifact.

R18: committed before/with the write-up citing it.
Artifact: eval/results/extended_078_live_replies_2026_09_05.json
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
PROBES = os.path.join(REPO, 'eval', 'accuracy_gate', 'edge_probe_extended_078_DRAFT.jsonl')
ENDPOINT = 'https://prosperpiusmbaruku007--chike-inference-web-endpoint.modal.run'
OUT = os.path.join(REPO, 'eval', 'results', 'extended_078_live_replies_2026_09_05.json')


def token():
    p = os.path.expanduser('~/.chike_modal_token.txt')
    return (os.environ.get('CHIKE_MODAL_TOKEN')
            or (open(p, encoding='utf-8').read().strip() if os.path.exists(p) else ''))


def ask(question):
    url = f'{ENDPOINT}?token={urllib.parse.quote(token())}'
    req = urllib.request.Request(url, data=json.dumps({'message': question}).encode('utf-8'),
                                 headers={'Content-Type': 'application/json'})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            body = json.loads(r.read().decode('utf-8', 'replace'))
            return {'outcome': 'HTTP_200', 'reply': body.get('reply', body.get('error', '')),
                    'elapsed_s': round(time.time() - t0, 1)}
    except Exception as exc:
        return {'outcome': 'ERROR', 'reply': f'{type(exc).__name__}: {str(exc)[:300]}',
                'elapsed_s': round(time.time() - t0, 1)}


def main():
    with open(PROBES, encoding='utf-8') as f:
        rows = [json.loads(line) for line in f if line.strip()]

    blob = {'measured': '2026-09-05', 'target': 'chike-inference (production)',
            'harness': 'eval/controls/run_extended_078_live.py',
            'source_probes': os.path.relpath(PROBES, REPO), 'rows': []}
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(blob, f, ensure_ascii=False, indent=2)

    for i, row in enumerate(rows, 1):
        r = ask(row['question'])
        out_row = dict(row)
        out_row['outcome'] = r['outcome']
        out_row['reply'] = r['reply']
        out_row['elapsed_s'] = r['elapsed_s']
        blob['rows'].append(out_row)
        with open(OUT, 'w', encoding='utf-8') as f:
            json.dump(blob, f, ensure_ascii=False, indent=2)
        print(f"[{i}/{len(rows)}] {row['id']} ({r['elapsed_s']}s): {r['reply'][:140]}")

    blob['status'] = 'COMPLETE -- adjudication pending, separate pass'
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(blob, f, ensure_ascii=False, indent=2)
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()
