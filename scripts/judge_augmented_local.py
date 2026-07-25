"""Local item-5 frontier-judge OVERLAY over the pinned 5239190 baseline (no GPU).

The local twin of the Kaggle harness's judge pass (kaggle/eval_orchestrator_combined.py) and
the direct successor to scripts/judge_regression_400.py: the census was a single-shot (N=1),
non-pinned audit; this runs the *decided* mechanism — pinned provider (DeepInfra, seed=42,
allow_fallbacks:false) + MAJORITY-OF-5 (chike.judge) — over the exact same committed baseline,
and emits the three side-by-side numbers (raw / reliable-denominator / judge-augmented) plus the
disagreement queue that build_confirmation_report() produces.

Pure OpenRouter (the judge is qwen/qwen3-32b, no local model), so it runs off OPENROUTER_API_KEY
without Kaggle. Read-only w.r.t. scoring.py and the live gate — reporting/transparency only.

    export OPENROUTER_API_KEY=...        # OpenRouter key with credits
    python scripts/judge_augmented_local.py

Writes eval/results/judge_augmented_5239190.json.
"""
import os
import io
import sys
import json
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from chike import judge as cj                                            # noqa: E402

OR_KEY = os.environ.get('OPENROUTER_API_KEY', '')
assert OR_KEY, 'set OPENROUTER_API_KEY'

BASELINE = 'eval/results/gate_orchestrator_combined_5239190.json'
base = json.load(open(BASELINE, encoding='utf-8'))
assert base.get('commit') == '5239190', f"expected pinned 5239190 baseline, got {base.get('commit')}"
results = base['results']
print(f'[data] {len(results)} baseline rows (commit 5239190)')

gradeable = cj.judge_gradeable(results)
print(f'[judge] majority-of-{cj.DEFAULT_N}, pinned {cj.DEFAULT_PROVIDER} seed={cj.DEFAULT_SEED}')
print(f'[judge] grading {len(gradeable)} in-corpus non-clarified answers '
      f'(~{len(gradeable) * cj.DEFAULT_N} calls) ...', flush=True)

t0 = time.time()


def _judge_row(r):
    v = cj.judge_majority(r['question_sw'], r.get('correct_answer_sw', ''),
                          cj.clean_for_judge(r['generated']), api_key=OR_KEY)
    return r['id'], v


jrows, done = {}, 0
with ThreadPoolExecutor(max_workers=8) as ex:
    for qid, v in ex.map(_judge_row, gradeable):
        jrows[qid] = v
        done += 1
        if done % 25 == 0:
            print(f'   ...{done}/{len(gradeable)} judged ({time.time()-t0:.0f}s)', flush=True)

for r in results:
    r['judge'] = jrows[r['id']]['verdict'] if r['id'] in jrows else None

report = cj.build_confirmation_report(results)
provs = sorted({p for v in jrows.values() for p in v['providers']})
ties = sorted(qid for qid, v in jrows.items() if v['tie'])
jpin = sum(v['pin'] for v in jrows.values()); jpout = sum(v['pout'] for v in jrows.values())
jerr = sum(v['err_count'] for v in jrows.values())
jcost = jpin * cj.PRICE_IN + jpout * cj.PRICE_OUT
wall = time.time() - t0

rp = report
print('\n' + '=' * 64)
print(f'ITEM-5 JUDGE OVERLAY @5239190  (majority-of-{cj.DEFAULT_N}, {cj.DEFAULT_PROVIDER})')
print('=' * 64)
print(f'  provider(s) served (want [{cj.DEFAULT_PROVIDER}]): {provs}   '
      f'ties->undetermined: {len(ties)}   api_errors: {jerr}')
print(f'  raw in-corpus:      {rp["raw"]["pass"]}/{rp["raw"]["total"]} = {rp["raw"]["acc"]:.1%}')
print(f'  reliable-denom:     {rp["reliable_denom"]["pass"]}/{rp["reliable_denom"]["total"]} '
      f'= {rp["reliable_denom"]["acc"]:.1%}  (regex, gap excluded)')
print(f'  JUDGE-AUGMENTED:    {rp["judge_augmented"]["pass"]}/{rp["judge_augmented"]["total"]} '
      f'= {rp["judge_augmented"]["acc"]:.1%}  (gap filled; undet excluded)   '
      f'floor(undet=fail) {rp["judge_augmented"]["floor_undet_fail"]["acc"]:.1%}')
gf = rp['gap_fill']
print(f'  gap-fill: {gf["gap_n"]} reliable=False -> {gf["judge_correct"]} correct / '
      f'{gf["judge_wrong"]} wrong / {gf["judge_undetermined"]} undetermined')
dq = rp['disagreement_queue']
print(f'  DISAGREEMENT QUEUE (candidates, NOT applied):')
print(f'     false-pass ({len(dq["false_pass_candidates"])}): {dq["false_pass_candidates"]}')
print(f'     false-fail ({len(dq["false_fail_candidates"])}): {dq["false_fail_candidates"]}')
print(f'  ~USD {jcost:.4f}   wall {wall:.0f}s')

out = {'harness': 'judge_augmented_local', 'baseline_commit': '5239190',
       'model': cj.DEFAULT_MODEL, 'n': cj.DEFAULT_N, 'provider_pin': cj.DEFAULT_PROVIDER,
       'seed': cj.DEFAULT_SEED, 'providers_served': provs, 'graded': len(gradeable),
       'report': report, 'tie_ids': ties,
       'per_id': {qid: {'verdict': v['verdict'], 'votes': v['votes'], 'tie': v['tie'],
                        'justification': v['justification']} for qid, v in jrows.items()},
       'cost': {'calls': len(gradeable) * cj.DEFAULT_N, 'prompt_tokens': jpin,
                'completion_tokens': jpout, 'usd': round(jcost, 4)},
       'wall_s': round(wall, 1), 'api_errors': jerr,
       'caveat': ('report-alongside only: judge fills reliable=False gap + flags reliable=True '
                  'disagreements; never flips a confident regex verdict; does not drive GATE PASSED.')}
outp = 'eval/results/judge_augmented_5239190.json'
json.dump(out, open(outp, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'\n[save] {outp}')
