# -*- coding: utf-8 -*-
"""R16 + §5(d) live canary for the presumptive `kodi ya mapato` cue + entity veto deploy.

FOUR GROUPS, deliberately separated.

  TARGET      pic_01/02/03 — the gap itself. Each must now come back with the presumptive
              ENGINE's working ("Kodi ya makadirio = ..."), not a fact-path synthesis.

  ENTITY_VETO pic_04 — THE ONE THAT MUST BE CONFIRMED LIVE RATHER THAN ASSUMED. A clean
              475-row corpus sweep said the cue was safe; an authored probe said otherwise,
              because `_PRESUMPTIVE_TURNOVER_CUES` contains "nauza" which sits inside
              "i-nauza", so every company sentence already satisfied the turnover gate. Offline
              the veto holds. Live is where it counts: a company must NOT receive the
              resident-individual turnover table. pic_05 rides along as the BOARDED
              pre-existing defect (routes to PAYE via `tunalipa`) so its live behaviour is on
              the record rather than inferred from the router.

  NEGATIVE    every row scored CORRECT in the 2026-08-17 adjudication, compared to its recorded
              text. This is the §5(d) answer-level bar — not a rank check, not the targets.
              nat_27 excluded: a retired ungrounded luck control can neither break nor confirm
              anything, and the exclusion is recorded rather than silent.

  FRESHNESS   a config-only OOC phrase. It proves the container read chike_config.json rather
              than the hardcoded fallback, which is the only evidence that separates a live
              deploy from a warm container serving old code (R16).

R16: writes its artifact directly. No truncating console consumer stands between the run and
the file.
R18: committed before it runs.

Artifact: eval/results/presumptive_cue_canary_live.json
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
PROBES = os.path.join(HERE, 'presumptive_income_cue_probes.jsonl')
OUT = os.path.join(REPO, 'eval', 'results', 'presumptive_cue_canary_live.json')

RETIRED_CONTROLS = ['nat_27']
TARGET_IDS = ['pic_01', 'pic_02', 'pic_03']
VETO_IDS = ['pic_04', 'pic_05']
# Controls from the probe file that must keep their existing route end-to-end.
UNCHANGED_IDS = ['pic_13', 'pic_14', 'pic_15', 'pic_10', 'pic_12']
FRESHNESS = ('freshness_ooc', 'nataka kujua kodi ya faida ya mtaji nikiuza nyumba',
             'config-only OOC phrase; must refuse')

# What a reply must contain to count as "the engine produced a FIGURE", and what a company reply
# must NOT contain.
#
# THE MARKER IS NARROWER THAN "THE ENGINE RAN", and the 2026-08-23 run proved it: pic_02 scored
# engine_marker_present=False while being entirely CORRECT. Turnover of TZS 8,000,000 sits in a
# band whose rate depends on record-keeping, so compute_presumptive never-guesses and returns a
# clarification asking the user whether they keep books — the right behaviour, with no figure and
# no "kodi ya makadirio" string. The run's headline therefore read 2/3 when all three targets
# reached the engine.
#
# Left as-is rather than widened, because a marker that also matched the clarification copy would
# stop distinguishing "computed" from "asked", which is the distinction the target group exists
# to show. Read the replies, not the count — the count is a pointer.
ENGINE_MARKER = 'kodi ya makadirio'


def main():
    with open(ADJ, encoding='utf-8') as f:
        adj = json.load(f)
    by_id = {r['id']: r for r in adj['rows']}

    with open(PROBES, encoding='utf-8') as f:
        probes = {p['id']: p for p in (json.loads(l) for l in f if l.strip())}

    negatives = [r['id'] for r in adj['rows']
                 if r['now'].startswith('CORRECT') and r['id'] not in RETIRED_CONTROLS]

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
            rec['engine_marker_present'] = ENGINE_MARKER in reply.lower()
            if baseline is not None:
                rec['identical_to_baseline'] = (reply.strip() == baseline.strip())
                print(f"identical_to_baseline={rec['identical_to_baseline']}")
            print(f"engine_marker_present={rec['engine_marker_present']}")
            print(f"A: {reply}")
        except Exception as e:
            rec['error'] = f'{type(e).__name__}: {e}'
            print(f"ERROR: {rec['error']}")
        rec['elapsed_s'] = round(time.time() - t0, 1)
        rows.append(rec)

    for rid in TARGET_IDS:
        call(rid, probes[rid]['question'], 'TARGET', note=probes[rid]['guards_against'])
    for rid in VETO_IDS:
        call(rid, probes[rid]['question'], 'ENTITY_VETO',
             note=probes[rid].get('known_failing_reason') or probes[rid]['guards_against'])
    for rid in UNCHANGED_IDS:
        call(rid, probes[rid]['question'], 'UNCHANGED_CONTROL',
             note=probes[rid]['guards_against'])
    for rid in negatives:
        call(rid, by_id[rid]['question'], 'NEGATIVE',
             note=f"was {by_id[rid]['now']} on {adj['date']}",
             baseline=by_id[rid].get('reply'))
    call(FRESHNESS[0], FRESHNESS[1], 'FRESHNESS', note=FRESHNESS[2])

    neg = [r for r in rows if r['group'] == 'NEGATIVE']
    changed = [r['id'] for r in neg if r.get('identical_to_baseline') is False]
    targets = [r for r in rows if r['group'] == 'TARGET']
    veto = {r['id']: r for r in rows if r['group'] == 'ENTITY_VETO'}

    out = {
        'measured': '2026-08-23',
        'harness': 'eval/routing/canary_presumptive_cue_live.py',
        'change_under_test': "bare `kodi ya mapato` presumptive cue + "
                             "_PRESUMPTIVE_ENTITY_VETO_PATTERN",
        'baseline_adjudication': os.path.basename(ADJ),
        'retired_controls_excluded': RETIRED_CONTROLS,
        'engine_marker': ENGINE_MARKER,
        'targets_reached_engine': sum(1 for r in targets
                                      if r.get('engine_marker_present')),
        'targets_total': len(targets),
        'company_got_individual_table': veto.get('pic_04', {}).get('engine_marker_present'),
        'negatives_total': len(neg),
        'negatives_byte_identical': sum(1 for r in neg
                                        if r.get('identical_to_baseline') is True),
        'negatives_changed': changed,
        'rows': rows,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n[saved] {OUT}")
    print(f"targets reaching the engine: {out['targets_reached_engine']}/{out['targets_total']}")
    print(f"pic_04 company got the individual table: "
          f"{out['company_got_individual_table']}  (MUST be False)")
    print(f"negatives: {out['negatives_byte_identical']}/{len(neg)} byte-identical")
    print(f"CHANGED negatives (need adjudication): {changed}")


if __name__ == '__main__':
    main()
