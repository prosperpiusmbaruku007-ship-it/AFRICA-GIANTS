"""KAGGLE — Part 1 frontier LLM-as-judge regression via OpenRouter.

Fetch-and-run pattern (same as nli_regression.py / eval.py / eval_orchestrator.py):

    import requests
    r = requests.get('https://raw.githubusercontent.com/prosperpiusmbaruku007-ship-it/'
                     'AFRICA-GIANTS/main/kaggle/judge_regression.py?cb=1', timeout=15)
    exec(r.text)

Runs in a Kaggle notebook with Internet ON (NO GPU needed — inference is on OpenRouter).
Required Kaggle secrets:
  * AFRICA_GIANTS       - HuggingFace token WITH WRITE access (same as eval.py; used to read
                          the v15 gate results and to UPLOAD this run's results back to v15)
  * OPENROUTER_API_KEY  - OpenRouter key (credits available); the judge model runs there

What it does — the identical two-stage test used for both NLI models, but the judge is a
32B-class multilingual open model with documented Kiswahili coverage (qwen/qwen3-32b):
  STAGE 1  the 14 confirmed audit examples first, verdict vs known ground truth
  STAGE 2  immediately continue to the full 190 non-refusal questions

Judge task: given (question, reference correct answer, generated answer), classify the
generated answer as substantively correct / substantively wrong / undetermined, + 1 sentence.

Persists everything to HF v15 (judge_regression_<model>.json) so it can be analysed
off-Kaggle. Read-only w.r.t. chike/scoring.py — does NOT modify the scorer.
"""
import os, json, re, time, requests
from concurrent.futures import ThreadPoolExecutor

# ---- auth ------------------------------------------------------------------
try:
    import kaggle_secrets
    _sc = kaggle_secrets.UserSecretsClient()
    HF_TOKEN = _sc.get_secret('AFRICA_GIANTS')
    OR_KEY = _sc.get_secret('OPENROUTER_API_KEY')
    print('[auth] HF + OpenRouter secrets loaded from Kaggle')
except Exception as e:
    HF_TOKEN = os.environ.get('HF_TOKEN', '') or os.environ.get('AFRICA_GIANTS', '')
    OR_KEY = os.environ.get('OPENROUTER_API_KEY', '')
    print(f'[auth] fallback env: HF={"set" if HF_TOKEN else "MISSING"} OR={"set" if OR_KEY else "MISSING"}')
assert OR_KEY, 'OPENROUTER_API_KEY missing — attach it as a Kaggle secret named OPENROUTER_API_KEY'
assert HF_TOKEN, 'AFRICA_GIANTS (HF write token) missing — attach it as a Kaggle secret'

RAW = 'https://raw.githubusercontent.com/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS/main'
NOCACHE = {'Cache-Control': 'no-cache', 'Pragma': 'no-cache'}
cb = str(int(time.time() * 1000))
try:
    sha = requests.get('https://api.github.com/repos/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS/commits/main',
                       headers=NOCACHE, timeout=15).json().get('sha', '?')[:7]
    print(f'[git] main HEAD = {sha}')
except Exception as e:
    sha = '?'; print(f'[git] HEAD check skipped: {e}')

# ---- fetch shared scorer + data (same sources as eval.py) ------------------
r = requests.get(f'{RAW}/chike/scoring.py?cb={cb}', headers=NOCACHE, timeout=20); r.raise_for_status()
_ns = {'__file__': 'scoring.py'}
exec(compile(r.text, 'chike/scoring.py', 'exec'), _ns)
score_question = _ns['score_question']; scorer_reliability = _ns['scorer_reliability']
print(f'[chike] scoring.py fetched ({len(r.text)} bytes)')

qtext_raw = requests.get(f'{RAW}/eval/accuracy_gate/eval_questions_001.jsonl?cb={cb}', headers=NOCACHE, timeout=20).text
qs = {}
for line in qtext_raw.splitlines():
    line = line.strip()
    if line:
        q = json.loads(line); qs[q['id']] = q
CONFIG = requests.get(f'{RAW}/kaggle/chike_config.json?cb={cb}', headers=NOCACHE, timeout=20).json()
REFUSAL = CONFIG['refusal_phrases']
print(f'[data] {len(qs)} gate questions, {len(REFUSAL)} refusal phrases')

from huggingface_hub import hf_hub_download
p = hf_hub_download(repo_id='prospAprospA007/africa-giants-adapter-v15',
                    filename='gate_001_results.json', repo_type='model', token=HF_TOKEN or None)
res = {rr['id']: rr for rr in json.load(open(p, encoding='utf-8'))['results']}
print(f'[data] {len(res)} v15 stored results')


def clean(g):
    """same ramble-strip used by the NLI harness, for parity of the graded text."""
    for mk in ['\nuser', 'user_0', 'user ', '\n\n']:
        i = g.find(mk)
        if i > 40:
            g = g[:i]
    m = re.search(r'[Tt]hibitisha na[^)]*\)', g)
    if m:
        g = g[:m.end()]
    return g.strip()


# ---- judge (OpenRouter) ----------------------------------------------------
MODEL = 'qwen/qwen3-32b'          # dense 32B, Qwen3 covers 119 languages incl. Swahili
PRICE_IN = 0.00000008            # USD/token (OpenRouter listing, prompt)
PRICE_OUT = 0.00000028           # USD/token (OpenRouter listing, completion)

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


# ---- STAGE 1: 14 audit examples (real ground truth) ------------------------
AUDIT = ['eval_178', 'eval_114', 'eval_093', 'eval_176', 'eval_033', 'eval_019', 'eval_040',
         'eval_059', 'eval_180', 'eval_182', 'eval_165', 'eval_026', 'eval_157', 'eval_175']
# PASS = generated answer is genuinely correct; FAIL = genuinely wrong
TRUTH = {'eval_178': 'FAIL', 'eval_114': 'FAIL', 'eval_093': 'FAIL', 'eval_176': 'PASS', 'eval_033': 'PASS',
         'eval_019': 'PASS', 'eval_040': 'PASS', 'eval_059': 'FAIL', 'eval_180': 'PASS', 'eval_182': 'PASS',
         'eval_165': 'PASS', 'eval_026': 'PASS', 'eval_157': 'PASS', 'eval_175': 'PASS'}
V2T = {'correct': 'PASS', 'wrong': 'FAIL', 'undetermined': 'UNDET'}

print(f'\n[judge] model={MODEL}  STAGE 1 — 14 audit examples ...', flush=True)
t_s1 = time.time()
s1 = []
for qid in AUDIT:
    if qid not in res:
        continue
    q = qs.get(qid, {})
    row = judge(qid, q.get('question_sw', ''), q.get('correct_answer_sw', ''), clean(res[qid]['generated']))
    truth = TRUTH[qid]; jt = V2T[row['verdict']]
    row['truth'] = truth
    row['match_truth'] = (jt == truth)
    s1.append(row)
    flag = '' if (jt == truth or jt == 'UNDET') else '   <-- MISMATCH'
    print(f"   {qid:11} truth={truth:5} judge={row['verdict']:12} {flag}  {row['justification'][:70]}", flush=True)

s1_fd = sum(1 for r in s1 if r['truth'] == 'PASS' and r['verdict'] == 'wrong')   # false demotion
s1_fp = sum(1 for r in s1 if r['truth'] == 'FAIL' and r['verdict'] == 'correct')  # false promotion
s1_und = sum(1 for r in s1 if r['verdict'] == 'undetermined')
s1_ok = sum(1 for r in s1 if r['match_truth'])
print(f"\n[judge] STAGE 1: {s1_ok}/{len(s1)} match ground truth | "
      f"false-demote={s1_fd} false-promote={s1_fp} undetermined={s1_und} | {time.time()-t_s1:.0f}s")
print('   (clean here is necessary, not sufficient — mDeBERTa was clean on 14 but demoted 5 at 190. Continuing to STAGE 2.)', flush=True)

# ---- STAGE 2: full 190 (parallel) ------------------------------------------
targets = []
for qid, rr in res.items():
    q = dict(qs.get(qid, {})); q['id'] = qid
    q['answer_type'] = q.get('answer_type', rr.get('answer_type'))
    if q['answer_type'] == 'out_of_corpus_refusal':
        continue
    targets.append((qid, q, rr))
print(f'\n[judge] STAGE 2 — {len(targets)} non-refusal questions (8 workers) ...', flush=True)

t_s2 = time.time()
rows = {}
def _run(item):
    qid, q, rr = item
    r = judge(qid, q.get('question_sw', ''), q.get('correct_answer_sw', ''), clean(rr['generated']))
    return qid, r
done = 0
with ThreadPoolExecutor(max_workers=8) as ex:
    for qid, r in ex.map(_run, targets):
        rows[qid] = r
        done += 1
        if done % 40 == 0:
            print(f'   ...{done}/{len(targets)} judged ({time.time()-t_s2:.0f}s)', flush=True)
wall_s2 = time.time() - t_s2

false_demote, false_promote, excluded_verdicts, agree, errors = [], [], [], [], []
for qid, q, rr in targets:
    r = rows[qid]
    rel, reason = scorer_reliability(q, rr['generated'])
    regex = score_question(q, rr['generated'], REFUSAL)
    cur = ('PASS' if regex else 'FAIL') if rel else 'EXCLUDED'
    rec = {'id': qid, 'type': q['answer_type'], 'current': cur, 'judge': r['verdict'],
           'why': r['justification'], 'q': q.get('question_sw', '')[:55]}
    if r['err']:
        errors.append({'id': qid, 'err': r['err']})
    if cur == 'PASS' and r['verdict'] == 'wrong':
        false_demote.append(rec)
    elif cur == 'FAIL' and r['verdict'] == 'correct':
        false_promote.append(rec)
    elif cur == 'EXCLUDED':
        excluded_verdicts.append(rec)
    else:
        agree.append(rec)

tot_in = sum(r['pin'] for r in list(rows.values()) + s1)
tot_out = sum(r['pout'] for r in list(rows.values()) + s1)
cost = tot_in * PRICE_IN + tot_out * PRICE_OUT
mean_dt = sum(r['dt'] for r in rows.values()) / max(1, len(rows))

print('\n' + '=' * 70)
print(f'JUDGE={MODEL}  (frontier LLM-as-judge, correct/wrong/undetermined vs reference)')
print('=' * 70)
print(f'\n### FALSE-DEMOTION (currently-PASS, judge says WRONG): {len(false_demote)}')
for x in false_demote: print('   ', x)
print(f'\n### FALSE-PROMOTION (currently-FAIL, judge says CORRECT): {len(false_promote)}')
for x in false_promote: print('   ', x)
print(f'\n### EXCLUDED-now-covered (judge verdict for the scorer_unreliable set): {len(excluded_verdicts)}')
for x in excluded_verdicts: print('   ', x)
print(f'\n### agreements (no disagreement with reliable regex): {len(agree)}')
print(f'### API errors: {len(errors)}')
for x in errors: print('   ', x)
print(f'\n[cost] calls={len(rows)+len(s1)}  prompt_tok={tot_in}  completion_tok={tot_out}  ~USD={cost:.4f}')
print(f'[latency] STAGE 2 wall={wall_s2:.0f}s for {len(rows)} calls (8 workers); mean/call={mean_dt:.2f}s')

# ---- persist to HF v15 -----------------------------------------------------
out = {
    'model': MODEL, 'git_head': sha,
    'stage1_14example': {'match_truth': s1_ok, 'n': len(s1),
                         'false_demote': s1_fd, 'false_promote': s1_fp, 'undetermined': s1_und,
                         'rows': s1},
    'stage2_190': {'false_demote_count': len(false_demote), 'false_promote_count': len(false_promote),
                   'excluded_covered_count': len(excluded_verdicts), 'agree_count': len(agree),
                   'api_errors': len(errors),
                   'false_demote': false_demote, 'false_promote': false_promote,
                   'excluded_verdicts': excluded_verdicts, 'errors': errors},
    'cost': {'calls': len(rows) + len(s1), 'prompt_tokens': tot_in, 'completion_tokens': tot_out,
             'usd': round(cost, 4)},
    'latency': {'stage2_wall_s': round(wall_s2, 1), 'mean_per_call_s': round(mean_dt, 2), 'workers': 8},
}
fname = f'judge_regression_{MODEL.split("/")[-1]}.json'
try:
    from huggingface_hub import HfApi
    import io
    HfApi().upload_file(
        path_or_fileobj=io.BytesIO(json.dumps(out, ensure_ascii=False, indent=2).encode('utf-8')),
        path_in_repo=fname, repo_id='prospAprospA007/africa-giants-adapter-v15',
        repo_type='model', token=HF_TOKEN or None,
        commit_message=f'judge regression: {MODEL} (fd={len(false_demote)} fp={len(false_promote)})')
    print(f'\n[hf] uploaded -> prospAprospA007/africa-giants-adapter-v15/{fname}')
except Exception as e:
    print(f'\n[hf] UPLOAD FAILED ({type(e).__name__}: {e}) — copy the JSON below manually')
    print(json.dumps(out, ensure_ascii=False))
print('\nJUDGE_DONE — decision numbers: STAGE 2 false-demote / false-promote above.')
