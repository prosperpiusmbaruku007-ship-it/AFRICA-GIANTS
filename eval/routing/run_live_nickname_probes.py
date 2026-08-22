# -*- coding: utf-8 -*-
"""Live half of the nickname-routing measurement: does the levy conflation reproduce?

Uses production `run()` only — no debug method, no deploy needed, so this measures exactly
what a user would get today.

The comparison that matters: probes the local measurement says route to FACT vs probes it
says route to COMPUTE, same subject matter. If the fact-routed ones state a wrong rate and
the compute-routed one is right, the wrong rate is a consequence of the routing miss rather
than an independent generation defect.

REPEATS each probe (default 2) because the original finding was 2-for-2 and a single sample
cannot distinguish a stable defect from a sampling artefact.

R16: writes its artifact directly, no truncating console consumer.
R18: committed before its result is written up.
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import modal  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
MEASUREMENT = os.path.join(REPO, 'eval', 'results', 'nickname_routing_measurement.json')
OUT = os.path.join(REPO, 'eval', 'results', 'nickname_live_probes.json')

# Subset worth model time: the defect probe, its digit and explicit-levy siblings, the
# applicability form, and the one shape the local measurement says DOES reach compute.
SUBSET = ['nick_01', 'nick_02', 'nick_03', 'nick_12', 'nick_08']
REPEATS = 2

# SDL is 3.5%; 0.5% is WCF's and 10%/20% are NSSF's. A rate stated next to a
# 'mafunzo'/SDL subject is checkable against a constant — no computed figure required.
RATE = re.compile(r'asilimia\s*([0-9]+(?:[.,][0-9]+)?)|([0-9]+(?:[.,][0-9]+)?)\s*%')


def rates_in(text):
    out = []
    for m in RATE.finditer(text or ''):
        out.append((m.group(1) or m.group(2)).replace(',', '.'))
    return out


def main():
    with open(MEASUREMENT, encoding='utf-8') as f:
        local = {r['id']: r for r in json.load(f)['rows']}

    ChikeModel = modal.Cls.from_name('chike-inference', 'ChikeModel')
    rows = []

    for pid in SUBSET:
        p = local[pid]
        for attempt in range(1, REPEATS + 1):
            print(f"\n=== {pid} attempt {attempt} "
                  f"(local says: routes_to={p['routes_to']}, intent={p['detect_intent']}) ===")
            print(f"Q: {p['question']}")
            rec = {
                'id': pid,
                'attempt': attempt,
                'question': p['question'],
                'local_routes_to': p['routes_to'],
                'local_detect_intent': p['detect_intent'],
                'local_blocking_gate': p['blocking_gate'],
                'expect_levy': p['expect_levy'],
            }
            try:
                resp = ChikeModel().run.remote(p['question'])
                reply = resp.get('reply', resp) if isinstance(resp, dict) else str(resp)
                rec['reply'] = reply
                rec['rates_stated'] = rates_in(reply)
                rec['mentions_nssf_domain'] = 'nssf.go.tz' in (reply or '').lower()
                rec['mentions_tra_domain'] = 'tra.go.tz' in (reply or '').lower()
                print(f"A: {reply}")
                print(f"rates={rec['rates_stated']} nssf_domain={rec['mentions_nssf_domain']}")
            except Exception as e:
                rec['error'] = f'{type(e).__name__}: {e}'
                print(f"ERROR: {rec['error']}")
            rows.append(rec)

    out = {
        'measured': '2026-08-22',
        'purpose': ('does the SDL/WCF/NSSF conflation reproduce across adjacent phrasings, '
                    'and is the compute-routed shape immune?'),
        'harness': 'eval/routing/run_live_nickname_probes.py',
        'local_measurement': 'eval/results/nickname_routing_measurement.json',
        'repeats_per_probe': REPEATS,
        'rows': rows,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()
