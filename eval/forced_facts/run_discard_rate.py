# -*- coding: utf-8 -*-
"""DISCARD-RATE measurement — when a correct fact reaches context, is it used?

Runs on the DEPLOYED state (post ROUTING-GAP-A/B), so it measures what is live rather than
what was live.

Only FORCEABLE rows are called: ABSENCE rows have no fact to discard, and COMPUTE_NOW rows no
longer depend on retrieval. Both exclusions are carried into the artifact so the denominator
is auditable rather than assumed.

SCORING is mechanical and deliberately conservative — it reports a SIGNAL, and the per-row
replies are printed for adjudication:

  USED        every decisive figure in the forced fact appears in the reply
  PARTIAL     some appear
  NOT_USED    none appear
  NO_FIGURES  the forced fact carries no figure; judged by hand from the printed reply

A figure appearing in the reply is not proof the fact was USED — the model may have recited it
from weights, which is exactly the phenomenon under study. So this measures an UPPER BOUND on
use, i.e. a LOWER BOUND on the discard rate. Stated here so the number is not over-read.

R16: writes its artifact directly, no truncating console consumer.
R18: committed before it runs.

Artifact: eval/results/discard_rate.json
"""
import json
import os
import re
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import modal  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
FIXTURE = os.path.join(HERE, 'discard_rows.json')
OUT = os.path.join(REPO, 'eval', 'results', 'discard_rate.json')

SW_NUM = {'moja': '1', 'mbili': '2', 'tatu': '3', 'nne': '4', 'tano': '5', 'sita': '6',
          'saba': '7', 'nane': '8', 'tisa': '9', 'kumi': '10'}
EN_NUM = {'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5', 'six': '6',
          'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10'}
CITATION_NOISE = {'605', '487', '212', '213', '332', '438', '82', '50', '16', '2003',
                  '2015', '2019', '2022', '2023', '2024', '2025', '2026', '5'}


def normalise(text):
    t = (text or '').lower()
    for w, d in list(SW_NUM.items()) + list(EN_NUM.items()):
        t = re.sub(rf'\b{w}\b', d, t)
    t = re.sub(r'(?<=\d)[,\s](?=\d{3}\b)', '', t)

    def mul(m, f):
        v = float(m.group(1)) * f
        return str(int(v)) if v == int(v) else str(v)
    for word, factor in (('milioni', 1e6), ('million', 1e6), ('elfu', 1e3),
                         ('thousand', 1e3), ('laki', 1e5)):
        t = re.sub(rf'{word}\s*(\d+(?:\.\d+)?)', lambda m, f=factor: mul(m, f), t)
        t = re.sub(rf'(\d+(?:\.\d+)?)\s*{word}', lambda m, f=factor: mul(m, f), t)
    return t.replace(',', '.')


def figures(text):
    out, seen = [], set()
    for f in re.findall(r'\d+(?:\.\d+)?', normalise(text)):
        f = f[:-2] if f.endswith('.0') else f
        if f in CITATION_NOISE or f in seen:
            continue
        seen.add(f)
        out.append(f)
    return out


def present(fig, hay):
    return re.search(rf'(?<!\d){re.escape(fig)}(?!\d)', hay) is not None


def main():
    with open(FIXTURE, encoding='utf-8') as f:
        fixture = json.load(f)

    forceable = [r for r in fixture['rows'] if r['class'] == 'FORCEABLE']
    ChikeModel = modal.Cls.from_name('chike-inference', 'ChikeModel')
    rows = []

    for r in forceable:
        print(f"\n=== {r['id']} [{r['verdict_2026_08_17']}] "
              f"grounding={r['grounding_2026_08_22']} ===")
        print(f"Q: {r['question']}")
        print(f"forced: {r['why']}")
        rec = dict(r)
        t0 = time.time()
        try:
            resp = ChikeModel().run_forced_facts.remote(r['question'], r['forced_facts'])
            reply = resp.get('reply', '') if isinstance(resp, dict) else str(resp)
            rec['reply'] = reply
            rec['pipeline_reported'] = resp.get('pipeline') if isinstance(resp, dict) else None
            rec['sub_answer_kinds'] = (resp.get('sub_answer_kinds')
                                       if isinstance(resp, dict) else None)

            want = figures(' '.join(r['forced_facts']))
            hay = normalise(reply)
            hit = [f for f in want if present(f, hay)]
            rec['fact_figures'] = want
            rec['figures_in_reply'] = hit
            if not want:
                rec['use'] = 'NO_FIGURES'
            elif len(hit) == len(want):
                rec['use'] = 'USED'
            elif hit:
                rec['use'] = 'PARTIAL'
            else:
                rec['use'] = 'NOT_USED'
            print(f"pipeline={rec['pipeline_reported']} use={rec['use']} "
                  f"{hit}/{want}")
            print(f"A: {reply}")
        except Exception as e:
            rec['error'] = f'{type(e).__name__}: {e}'
            rec['use'] = 'ERROR'
            print(f"ERROR: {rec['error']}")
        rec['elapsed_s'] = round(time.time() - t0, 1)
        rows.append(rec)

    tally = {}
    for r in rows:
        tally[r['use']] = tally.get(r['use'], 0) + 1

    out = {
        'measured': '2026-08-22',
        'harness': 'eval/forced_facts/run_discard_rate.py',
        'fixture': 'eval/forced_facts/discard_rows.json',
        'deployed_state': 'post ROUTING-GAP-A/B (b1ddd12)',
        'caveat': 'A figure present in the reply is an UPPER BOUND on use — the model may '
                  'have recited it from weights. So this is a LOWER BOUND on the discard rate.',
        'denominator': len(rows),
        'excluded_absence': [r['id'] for r in fixture['rows'] if r['class'] == 'ABSENCE'],
        'excluded_compute_now': [r['id'] for r in fixture['rows']
                                 if r['class'] == 'COMPUTE_NOW'],
        'use_tally': tally,
        'not_used_ids': [r['id'] for r in rows if r['use'] == 'NOT_USED'],
        'partial_ids': [r['id'] for r in rows if r['use'] == 'PARTIAL'],
        'rows': rows,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f'\n[saved] {OUT}')
    print(json.dumps(tally, indent=2))
    print(f"NOT_USED: {out['not_used_ids']}")
    print(f"PARTIAL:  {out['partial_ids']}")


if __name__ == '__main__':
    main()
