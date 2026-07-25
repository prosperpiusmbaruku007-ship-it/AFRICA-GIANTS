"""LOCAL frontier LLM-as-judge — 400-question CENSUS (follow-up #3, work item 1 of 5).

Scales kaggle/judge_regression.py from the 190 fact-path subset to the full 400-question
combined gate, and runs a CENSUS (not a sample) of all 385 non-refusal questions. Reason
(decided on the data, not on cost): reliable=False does NOT mean "the system failed to
answer" — every one of the 400 produced a real generated answer. It means the regex/word-
overlap scorer has LOW CONFIDENCE in its own pass/fail verdict. So the judge has TWO jobs:

  (1) GAP-FILL   grade the 133 excluded (reliable=False) — the MEASUREMENT GAP.
  (2) REGEX-AUDIT independently check the 252 reliable=True non-refusal verdicts, because
                 reliable=True means "regex is confident", NOT "regex is right" — and this
                 session already found multiple confident-but-wrong regex bugs by hand.

A 40-question spot-check of the 252 reliable verdicts was rejected: at a 3% true error rate
(~8 hidden wrong verdicts, the order of bugs already found), a clean 40-sample happens 30% of
the time. The population (252) is small enough that a trustworthy sample is nearly a census
anyway, and the census costs only ~2 cents / ~3 min more. So: judge everything, once.

CAVEAT (preserved in the output JSON): the judge is NOT ground truth — that is work item 2.
A judge-vs-regex disagreement on the reliable set is a CANDIDATE bug to adjudicate, not an
automatic correction. This harness surfaces the full disagreement list; it corrects nothing.

INPUT — pinned to a COMMITTED, reproducible artifact (NOT a live HF fetch):
    eval/results/gate_orchestrator_combined_5239190.json  (commit field == '5239190')
This is the exact baseline being characterized. The stored `reliable`/`reliable_reason`/`pass`
fields (as scored by commit 5239190's chike/scoring.py) are trusted as-is — we are grading
that run's verdicts, so we do not recompute them.

GRADING — row['generated'] is graded DIRECTLY (it is already reply.text, the cleaned text the
gate itself scored). No re-clean; re-cleaning would diverge from what the gate measured.

RUN (local, from repo root):
    python scripts/judge_regression_400.py
Requires OPENROUTER_API_KEY in the environment (falls back to a Kaggle secret of the same
name if run in a notebook). No GPU. ~399 OpenRouter calls, ~$0.037, ~330s at 8 workers.

Output -> eval/results/judge_regression_qwen3-32b_400.json (archived alongside the gate runs).
Read-only w.r.t. chike/scoring.py — does NOT modify the scorer.
"""
import os, io, json, re, time
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor

# ── paths / model ──────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASELINE = os.path.join(ROOT, 'eval', 'results', 'gate_orchestrator_combined_5239190.json')
BASELINE_COMMIT = '5239190'
MODEL = 'qwen/qwen3-32b'          # dense 32B, Qwen3 covers 119 languages incl. Swahili
OUT = os.path.join(ROOT, 'eval', 'results', f'judge_regression_{MODEL.split("/")[-1]}_400.json')
PRICE_IN = 0.00000008            # USD/token (OpenRouter listing, prompt)
PRICE_OUT = 0.00000028           # USD/token (OpenRouter listing, completion)
CAVEAT = ('The judge is NOT ground truth (that is work item 2 of follow-up #3). A judge-vs-'
          'regex disagreement on the reliable set is a CANDIDATE bug to adjudicate, not an '
          'automatic correction. This harness surfaces the disagreement list; it corrects nothing.')

# ── auth (local env first; Kaggle-secret fallback) ─────────────────────────────
OR_KEY = os.environ.get('OPENROUTER_API_KEY', '')
if not OR_KEY:
    try:
        import kaggle_secrets
        OR_KEY = kaggle_secrets.UserSecretsClient().get_secret('OPENROUTER_API_KEY')
    except Exception:
        pass
assert OR_KEY, 'OPENROUTER_API_KEY missing (set it in the environment, or attach as a Kaggle secret)'

import requests

# ── load the pinned, committed baseline ────────────────────────────────────────
with open(BASELINE, encoding='utf-8') as fh:
    data = json.load(fh)
assert data.get('commit') == BASELINE_COMMIT, f"baseline commit {data.get('commit')!r} != {BASELINE_COMMIT!r}"
rows = data['results']
assert len(rows) == 400, f'expected 400 rows, got {len(rows)}'

nonref = [r for r in rows if r['answer_type'] != 'out_of_corpus_refusal']
excluded = [r for r in nonref if not r['reliable']]          # 133 — the measurement gap
reliable = [r for r in nonref if r['reliable']]              # 252 — the regex-audit set
assert len(nonref) == 385, len(nonref)
assert len(excluded) == 133, len(excluded)
assert len(reliable) == 252, len(reliable)
print(f'[data] baseline {BASELINE_COMMIT}: 400 rows | non-refusal={len(nonref)} '
      f'(excluded/gap={len(excluded)}, reliable/audit={len(reliable)}) | refusals skipped={400-len(nonref)}')

# ── judge (OpenRouter) — identical prompt + call to kaggle/judge_regression.py ──
JUDGE_SYS = (
    "You are a bilingual Kiswahili/English compliance-answer grader for Tanzanian tax, "
    "labour and business-registration questions. You are given a QUESTION, a REFERENCE "
    "answer known to be correct, and a GENERATED answer to grade. Decide whether the "
    "GENERATED answer is substantively correct RELATIVE TO THE REFERENCE: it must agree on "
    "the key fact, figure, polarity (yes/no) or refusal. Extra wording, code-switching or "
    "phrasing differences do NOT make it wrong. A directly contradicting figure, a flipped "
    "yes/no, or a confidently wrong claim IS wrong. If the generated answer is too vague or "
    "off-topic to tell, use undetermined. Judge meaning, not surface form. Answer in the "
    "language you like but keep the justification to ONE sentence."
)


def judge(qid, question, ref, gen):
    user = (
        f"SWALI (question):\n{question}\n\n"
        f"JIBU SAHIHI LA RUFAA (reference correct answer):\n{ref}\n\n"
        f"JIBU LILILOTOLEWA (generated answer to grade):\n{gen}\n\n"
        'Return ONLY a JSON object, no other text:\n'
        '{"verdict": "correct" | "wrong" | "undetermined", "justification": "<one sentence>"}'
    )
    body = {'model': MODEL, 'temperature': 0, 'max_tokens': 400,
            'reasoning': {'enabled': False},
            'messages': [{'role': 'system', 'content': JUDGE_SYS},
                         {'role': 'user', 'content': user}]}
    t = time.time()
    verdict, just, pin, pout, err = 'undetermined', '', 0, 0, ''
    for attempt in range(3):
        try:
            resp = requests.post('https://openrouter.ai/api/v1/chat/completions',
                                 headers={'Authorization': 'Bearer ' + OR_KEY,
                                          'Content-Type': 'application/json'},
                                 json=body, timeout=120)
            j = resp.json()
            if 'choices' not in j:
                err = str(j.get('error', j))[:160]
                time.sleep(2 + attempt * 3); continue
            msg = j['choices'][0]['message']['content'] or ''
            u = j.get('usage', {}) or {}
            pin, pout = u.get('prompt_tokens', 0), u.get('completion_tokens', 0)
            mm = re.search(r'\{[^{}]*"verdict"[^{}]*\}', msg, re.S)
            if mm:
                try:
                    o = json.loads(mm.group(0))
                    verdict = str(o.get('verdict', 'undetermined')).lower().strip()
                    just = str(o.get('justification', ''))[:200]
                except Exception:
                    pass
            if verdict not in ('correct', 'wrong', 'undetermined'):
                lm = msg.lower()
                verdict = ('wrong' if 'wrong' in lm else 'correct' if 'correct' in lm else 'undetermined')
            err = ''
            break
        except Exception as e:
            err = f'{type(e).__name__}: {e}'[:160]
            time.sleep(2 + attempt * 3)
    return {'id': qid, 'verdict': verdict, 'justification': just,
            'pin': pin, 'pout': pout, 'dt': round(time.time() - t, 2), 'err': err}


# ── STAGE 1: 14 audit examples vs known ground truth (the judge-trust anchor) ───
# UNCHANGED from the 190 harness. Real hand-labeled truth; an early-abort sanity check that
# the judge behaves before spending on the census. These 14 are judged here AND again in the
# STAGE-2 census (hence ~399 calls, not 385): comparing the two verdicts for the same id is a
# free within-run non-determinism probe (groundwork for work item 4). The census verdict is
# the one used in the gap-fill / regex-audit grouping below.
AUDIT = ['eval_178', 'eval_114', 'eval_093', 'eval_176', 'eval_033', 'eval_019', 'eval_040',
         'eval_059', 'eval_180', 'eval_182', 'eval_165', 'eval_026', 'eval_157', 'eval_175']
TRUTH = {'eval_178': 'FAIL', 'eval_114': 'FAIL', 'eval_093': 'FAIL', 'eval_176': 'PASS', 'eval_033': 'PASS',
         'eval_019': 'PASS', 'eval_040': 'PASS', 'eval_059': 'FAIL', 'eval_180': 'PASS', 'eval_182': 'PASS',
         'eval_165': 'PASS', 'eval_026': 'PASS', 'eval_157': 'PASS', 'eval_175': 'PASS'}
V2T = {'correct': 'PASS', 'wrong': 'FAIL', 'undetermined': 'UNDET'}
by_id = {r['id']: r for r in rows}

print(f'\n[judge] model={MODEL}  STAGE 1 — 14 audit examples vs ground truth ...', flush=True)
t_s1 = time.time()
s1 = []
for qid in AUDIT:
    r = by_id.get(qid)
    if not r:
        print(f'   {qid}: MISSING from baseline — skipped'); continue
    row = judge(qid, r.get('question_sw', ''), r.get('correct_answer_sw', ''), r['generated'])
    truth = TRUTH[qid]; jt = V2T[row['verdict']]
    row['truth'] = truth; row['match_truth'] = (jt == truth)
    s1.append(row)
    flag = '' if (jt == truth or jt == 'UNDET') else '   <-- MISMATCH'
    print(f"   {qid:11} truth={truth:5} judge={row['verdict']:12}{flag}  {row['justification'][:70]}", flush=True)
s1_fd = sum(1 for r in s1 if r['truth'] == 'PASS' and r['verdict'] == 'wrong')      # false demotion
s1_fp = sum(1 for r in s1 if r['truth'] == 'FAIL' and r['verdict'] == 'correct')    # false promotion
s1_und = sum(1 for r in s1 if r['verdict'] == 'undetermined')
s1_ok = sum(1 for r in s1 if r['match_truth'])
print(f"\n[judge] STAGE 1: {s1_ok}/{len(s1)} match ground truth | "
      f"false-demote={s1_fd} false-promote={s1_fp} undetermined={s1_und} | {time.time()-t_s1:.0f}s")

# ── STAGE 2: CENSUS over all 385 non-refusal (parallel, 8 workers) ─────────────
print(f'\n[judge] STAGE 2 — CENSUS of {len(nonref)} non-refusal questions (8 workers) ...', flush=True)
t_s2 = time.time()
verdicts = {}


def _run(r):
    return r['id'], judge(r['id'], r.get('question_sw', ''), r.get('correct_answer_sw', ''), r['generated'])


done = 0
with ThreadPoolExecutor(max_workers=8) as ex:
    for qid, v in ex.map(_run, nonref):
        verdicts[qid] = v
        done += 1
        if done % 40 == 0:
            print(f'   ...{done}/{len(nonref)} judged ({time.time()-t_s2:.0f}s)', flush=True)
wall_s2 = time.time() - t_s2


def _rec(r):
    v = verdicts[r['id']]
    return {'id': r['id'], 'source': r['source'], 'answer_type': r['answer_type'],
            'subdomain': r.get('subdomain', ''), 'reliable_reason': r.get('reliable_reason', ''),
            'clarified': bool(r.get('clarified')),
            'regex': ('PASS' if r['pass'] else 'FAIL'), 'judge': v['verdict'],
            'justification': v['justification'], 'q': r.get('question_sw', '')[:60], 'err': v['err']}


# ── GROUP 1 — GAP-FILL: the 133 excluded, organised by the 8 exclusion reasons ─
gap_by_reason = defaultdict(list)
for r in excluded:
    gap_by_reason[r.get('reliable_reason', '')].append(_rec(r))
gap_counts = {reason: Counter(x['judge'] for x in recs)
              for reason, recs in gap_by_reason.items()}

# ── GROUP 2 — REGEX-AUDIT: the 252 reliable verdicts, disagreements surfaced ───
# Clarified rows are split out: their regex 'FAIL' is a DELIBERATE clarification (pass forced
# False), not a scoring error, so grading the clarification copy must not be miscounted as a
# regex false-fail. Surface them under their own key.
false_pass, false_fail, undetermined_a, clarified_a, agree_a = [], [], [], [], []
for r in reliable:
    rec = _rec(r)
    if rec['clarified']:
        clarified_a.append(rec)
    elif rec['regex'] == 'PASS' and rec['judge'] == 'wrong':
        false_pass.append(rec)                 # regex confidently PASSED a wrong answer
    elif rec['regex'] == 'FAIL' and rec['judge'] == 'correct':
        false_fail.append(rec)                 # regex confidently FAILED a correct answer
    elif rec['judge'] == 'undetermined':
        undetermined_a.append(rec)
    else:
        agree_a.append(rec)

# ── cost / latency ─────────────────────────────────────────────────────────────
allv = list(verdicts.values()) + s1
tot_in = sum(v['pin'] for v in allv)
tot_out = sum(v['pout'] for v in allv)
cost = tot_in * PRICE_IN + tot_out * PRICE_OUT
mean_dt = sum(v['dt'] for v in verdicts.values()) / max(1, len(verdicts))
errors = [{'id': v['id'], 'err': v['err']} for v in verdicts.values() if v['err']]

print('\n' + '=' * 72)
print(f'JUDGE CENSUS  model={MODEL}  baseline={BASELINE_COMMIT}')
print('=' * 72)
print('\n### GROUP 1 — GAP-FILL (133 excluded, judge verdict by exclusion reason):')
for reason in sorted(gap_by_reason, key=lambda k: -len(gap_by_reason[k])):
    c = gap_counts[reason]
    print(f"   {reason:34} n={len(gap_by_reason[reason]):3}  "
          f"correct={c.get('correct',0)} wrong={c.get('wrong',0)} undet={c.get('undetermined',0)}")
print('\n### GROUP 2 — REGEX-AUDIT (252 reliable verdicts vs judge):')
print(f"   FALSE-PASS candidates (regex PASS, judge WRONG):    {len(false_pass)}")
for x in false_pass: print('      *', x['id'], x['source'], x['answer_type'], '|', x['justification'][:70])
print(f"   FALSE-FAIL candidates (regex FAIL, judge CORRECT):  {len(false_fail)}")
for x in false_fail: print('      *', x['id'], x['source'], x['answer_type'], '|', x['justification'][:70])
print(f"   undetermined (judge could not tell):                {len(undetermined_a)}")
print(f"   clarified (deliberate clarification, not a bug):    {len(clarified_a)}")
print(f"   agreements:                                         {len(agree_a)}")
print(f"\n### API errors: {len(errors)}")
for x in errors: print('   ', x)
print(f'\n[cost] calls={len(allv)}  prompt_tok={tot_in}  completion_tok={tot_out}  ~USD={cost:.4f}')
print(f'[latency] STAGE 2 wall={wall_s2:.0f}s for {len(verdicts)} calls (8 workers); mean/call={mean_dt:.2f}s')
print(f'\n[CAVEAT] {CAVEAT}')

# ── persist (committed alongside the gate runs; no HF upload needed) ───────────
out = {
    'harness': 'judge_regression_400', 'model': MODEL,
    'baseline_input': os.path.relpath(BASELINE, ROOT).replace('\\', '/'),
    'baseline_commit': BASELINE_COMMIT, 'caveat': CAVEAT,
    'stage1_audit': {'match_truth': s1_ok, 'n': len(s1), 'false_demote': s1_fd,
                     'false_promote': s1_fp, 'undetermined': s1_und, 'rows': s1},
    'gap_fill_133': {
        'total': len(excluded),
        'by_reason': {k: v for k, v in gap_by_reason.items()},
        'verdict_counts_by_reason': {k: dict(v) for k, v in gap_counts.items()},
    },
    'regex_audit_252': {
        'total': len(reliable),
        'false_pass_candidates': false_pass,
        'false_fail_candidates': false_fail,
        'undetermined': undetermined_a,
        'clarified': clarified_a,
        'agree_count': len(agree_a),
        'counts': {'false_pass': len(false_pass), 'false_fail': len(false_fail),
                   'undetermined': len(undetermined_a), 'clarified': len(clarified_a),
                   'agree': len(agree_a)},
    },
    'cost': {'calls': len(allv), 'prompt_tokens': tot_in, 'completion_tokens': tot_out,
             'usd': round(cost, 4)},
    'latency': {'stage2_wall_s': round(wall_s2, 1), 'mean_per_call_s': round(mean_dt, 2), 'workers': 8},
    'api_errors': errors,
    'all_verdicts': verdicts,
}
with open(OUT, 'w', encoding='utf-8') as fh:
    json.dump(out, fh, ensure_ascii=False, indent=2)
print(f'\n[save] {os.path.relpath(OUT, ROOT)}')
print('JUDGE_CENSUS_DONE')
