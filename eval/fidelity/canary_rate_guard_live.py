# -*- coding: utf-8 -*-
"""R16 + §5(d) live canary for the D-FIDELITY-6 rate-guard deploy.

Four groups:

  FIX        nat_24 — the row that specified the guard. Its WCF prose said "10% ... kwa ajili ya
             WCF"; after this deploy that sentence must be GONE, with the engine's correct
             "WCF ni asilimia 0.5" line still standing.
  DETECTIONS the other four rows the sweep flagged, re-run live. Two of them (nat_01, nat_04)
             are compute rows whose 2026-08-11 replies carried SDL=0.5%.
             ⚠️ nick_01 IS EXPECTED TO STILL SHOW 0.5%. It is a FACT-path row, and the guard
             deliberately does not cover the fact path — a fact body cannot be blanked because
             _render would emit nothing. Predicted here IN ADVANCE so an unchanged result reads
             as the known gap it is, not as a failed deploy.
  NEGATIVES  every currently-CORRECT row, byte-compared against its recorded reply. §5(d).
             nat_27, nat_37 and nat_38 are EXCLUDED as retired luck controls — all three answer
             from model weights over an index gap, so neither breaking nor holding proves
             anything.
  FRESHNESS  a config-only OOC phrase (R16 container freshness).

R16: writes its artifact directly. R18: committed before it runs.
Artifact: eval/results/rate_guard_canary_live.json
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
sys.path.insert(0, REPO)

from chike import fidelity  # noqa: E402

ADJ = os.path.join(REPO, 'eval', 'results',
                   'natural48_rerun_2026_08_17_adjudication.json')
OUT = os.path.join(REPO, 'eval', 'results', 'rate_guard_canary_live.json')

RETIRED_CONTROLS = ['nat_27', 'nat_37', 'nat_38']

DETECTIONS = [
    ('nat_01', 'nina wafanyakazi 14 mishahara yote kwa mwezi ni milioni 6 ile ya mafunzo ya '
               'ufundi nitalipa ngapi', 'compute', 'SDL=0.5% on 2026-08-11'),
    ('nat_04', None, 'compute', 'SDL=0.5% on 2026-08-11'),
    ('nick_01', 'nimeajiri watu watano tu je nalipa ile ya mafunzo', 'fact',
     'EXPECTED TO STILL SHOW 0.5% — fact path is deliberately uncovered'),
]
FRESHNESS = ('freshness_ooc', 'nataka kujua kodi ya faida ya mtaji nikiuza nyumba')


def main():
    with open(ADJ, encoding='utf-8') as f:
        adj = json.load(f)
    by_id = {r['id']: r for r in adj['rows']}

    ChikeModel = modal.Cls.from_name('chike-inference', 'ChikeModel')
    rows = []

    def call(rid, question, group, note='', baseline=None):
        print(f"\n=== [{group}] {rid} ===\nQ: {question}")
        rec = {'id': rid, 'group': group, 'question': question, 'note': note,
               'baseline_reply': baseline}
        t0 = time.time()
        try:
            resp = ChikeModel().run.remote(question)
            reply = resp.get('reply', resp) if isinstance(resp, dict) else str(resp)
            rec['reply'] = reply
            # The guard's own verdict on the live reply — the direct check.
            rec['guard_flags_reply'] = fidelity.body_states_wrong_levy_rate(reply)
            rec['attributed_rates'] = [[lv, str(rt)]
                                       for lv, rt in fidelity.attributed_levy_rates(reply)]
            if baseline is not None:
                rec['identical_to_baseline'] = (reply.strip() == baseline.strip())
                print(f"identical_to_baseline={rec['identical_to_baseline']}")
            print(f"guard_flags={rec['guard_flags_reply']} rates={rec['attributed_rates']}")
            print(f"A: {reply}")
        except Exception as e:
            rec['error'] = f'{type(e).__name__}: {e}'
            print(f"ERROR: {rec['error']}")
        rec['elapsed_s'] = round(time.time() - t0, 1)
        rows.append(rec)

    # --- FIX ---
    call('nat_24', by_id['nat_24']['question'], 'FIX',
         note='WCF prose must lose the 10%; engine 0.5% line must remain')

    # --- DETECTIONS ---
    for rid, q, path, note in DETECTIONS:
        question = q or by_id[rid]['question']
        call(rid, question, 'DETECTION', note=f'{path} path — {note}')

    # --- NEGATIVES (§5(d)) ---
    negatives = [r['id'] for r in adj['rows']
                 if r['now'].startswith('CORRECT') and r['id'] not in RETIRED_CONTROLS
                 and r['id'] != 'nat_24']
    for rid in negatives:
        call(rid, by_id[rid]['question'], 'NEGATIVE',
             note=f"was {by_id[rid]['now']}", baseline=by_id[rid].get('reply'))

    call(FRESHNESS[0], FRESHNESS[1], 'FRESHNESS', note='config-only OOC phrase')

    neg = [r for r in rows if r['group'] == 'NEGATIVE']
    changed = [r['id'] for r in neg if r.get('identical_to_baseline') is False]
    fix = next(r for r in rows if r['id'] == 'nat_24')
    out = {
        'measured': '2026-08-22',
        'harness': 'eval/fidelity/canary_rate_guard_live.py',
        'change_under_test': 'D-FIDELITY-6 rate guard (f0aa44c)',
        'retired_controls_excluded': RETIRED_CONTROLS,
        'nat_24_guard_flags_reply': fix.get('guard_flags_reply'),
        'nat_24_wcf_10pct_present': bool(re.search(r'10\s*%[^.]{0,40}wcf|wcf[^.]{0,40}10\s*%',
                                                   fix.get('reply', ''), re.IGNORECASE)),
        'negatives_total': len(neg),
        'negatives_byte_identical': sum(1 for r in neg
                                        if r.get('identical_to_baseline') is True),
        'negatives_changed': changed,
        'detections_still_flagged': [r['id'] for r in rows
                                     if r['group'] == 'DETECTION'
                                     and r.get('guard_flags_reply')],
        'rows': rows,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n[saved] {OUT}")
    print(f"nat_24 guard_flags={out['nat_24_guard_flags_reply']} "
          f"wcf_10pct_present={out['nat_24_wcf_10pct_present']}")
    print(f"negatives: {out['negatives_byte_identical']}/{len(neg)} byte-identical; "
          f"changed={changed}")
    print(f"detections still flagged: {out['detections_still_flagged']}")


if __name__ == '__main__':
    main()
