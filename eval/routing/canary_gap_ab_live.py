# -*- coding: utf-8 -*-
"""R16 + §5(d) live canary for the ROUTING-GAP-A/B deploy.

Four groups, deliberately separated:

  TARGETS    nat_23, nat_24, nat_05 — the rows the change was built for.
  UNPLANNED  edge_p10, th_11, th_12, ov_08 — found by the sweep, NOT targeted, therefore the
             least-predicted part of the change and the most important to look at.
  NEGATIVES  every row currently scored CORRECT in the 2026-08-17 adjudication. This is the
             §5(d) answer-level bar: not a rank check, not the target rows — the replies of
             the set that already works, compared against their recorded text.
             nat_27 is EXCLUDED: it is a retired luck control (ungrounded), so it can neither
             break nor confirm anything. Its exclusion is recorded rather than silent.
  FRESHNESS  a config-only OOC phrase, which proves the container read chike_config.json
             rather than the hardcoded fallback (R16).

R16: writes its artifact directly. No truncating console consumer between the run and the file.
R18: committed before its result is written up.

Artifact: eval/results/gap_ab_canary_live.json
"""
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import modal  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
ADJ = os.path.join(REPO, 'eval', 'results', 'natural48_rerun_2026_08_17_adjudication.json')
OUT = os.path.join(REPO, 'eval', 'results', 'gap_ab_canary_live.json')

TARGETS = ['nat_23', 'nat_24', 'nat_05']
RETIRED_CONTROLS = ['nat_27']          # ungrounded luck row — see the 2026-08-22 retirement

UNPLANNED = [
    ('edge_p10', 'nawalipa wafanyakazi watano jumla ya milioni 4 kwa mwezi nitalipa ngapi '
                 'kwa ile ya mafunzo na ya uzeeni kwa pamoja',
     'two-levy question that was silently answering only NSSF'),
    ('th_11', 'Nina wafanyakazi 11 — je nalipa SDL?', '11 >= 10, SDL applies'),
    ('th_12', 'Nina wafanyakazi 9 — je nalipa SDL?', '9 < 10, SDL does NOT apply'),
    ('ov_08', 'biashara yangu ya foroza ina wafanyakazi 15 je nalipa SDL', '15 >= 10, applies'),
]
FRESHNESS = ('freshness_ooc', 'nataka kujua kodi ya faida ya mtaji nikiuza nyumba',
             'config-only OOC phrase; must refuse')


def main():
    with open(ADJ, encoding='utf-8') as f:
        adj = json.load(f)
    by_id = {r['id']: r for r in adj['rows']}

    negatives = [r['id'] for r in adj['rows']
                 if r['now'].startswith('CORRECT') and r['id'] not in TARGETS
                 and r['id'] not in RETIRED_CONTROLS]

    ChikeModel = modal.Cls.from_name('chike-inference', 'ChikeModel')
    rows = []

    def call(rid, question, group, note='', baseline=None):
        print(f"\n=== [{group}] {rid} ===")
        print(f"Q: {question}")
        rec = {'id': rid, 'group': group, 'question': question, 'note': note,
               'baseline_reply': baseline}
        t0 = time.time()
        try:
            resp = ChikeModel().run.remote(question)
            reply = resp.get('reply', resp) if isinstance(resp, dict) else str(resp)
            rec['reply'] = reply
            if baseline is not None:
                rec['identical_to_baseline'] = (reply.strip() == baseline.strip())
                print(f"identical_to_baseline={rec['identical_to_baseline']}")
            print(f"A: {reply}")
        except Exception as e:
            rec['error'] = f'{type(e).__name__}: {e}'
            print(f"ERROR: {rec['error']}")
        rec['elapsed_s'] = round(time.time() - t0, 1)
        rows.append(rec)

    for rid in TARGETS:
        call(rid, by_id[rid]['question'], 'TARGET',
             note=by_id[rid].get('why', ''), baseline=by_id[rid].get('reply'))
    for rid, q, note in UNPLANNED:
        call(rid, q, 'UNPLANNED', note=note)
    for rid in negatives:
        call(rid, by_id[rid]['question'], 'NEGATIVE',
             note=f"was {by_id[rid]['now']} on {adj['date']}",
             baseline=by_id[rid].get('reply'))
    call(FRESHNESS[0], FRESHNESS[1], 'FRESHNESS', note=FRESHNESS[2])

    neg = [r for r in rows if r['group'] == 'NEGATIVE']
    changed = [r['id'] for r in neg if r.get('identical_to_baseline') is False]
    out = {
        'measured': '2026-08-22',
        'harness': 'eval/routing/canary_gap_ab_live.py',
        'change_under_test': 'ROUTING-GAP-A + ROUTING-GAP-B (b1ddd12)',
        'baseline_adjudication': os.path.basename(ADJ),
        'retired_controls_excluded': RETIRED_CONTROLS,
        'counts': {g: sum(1 for r in rows if r['group'] == g)
                   for g in ('TARGET', 'UNPLANNED', 'NEGATIVE', 'FRESHNESS')},
        'negatives_total': len(neg),
        'negatives_byte_identical': sum(1 for r in neg
                                        if r.get('identical_to_baseline') is True),
        'negatives_changed': changed,
        'rows': rows,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n[saved] {OUT}")
    print(f"negatives: {out['negatives_byte_identical']}/{len(neg)} byte-identical")
    print(f"CHANGED negatives (need adjudication): {changed}")


if __name__ == '__main__':
    main()
