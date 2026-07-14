"""KAGGLE — Part 1 NLI contradiction-demotion regression (GPU), read-only.

Standard fetch-and-run pattern (same as eval.py / eval_orchestrator.py / regenerate_rag_e5.py):

    import requests
    r = requests.get('https://raw.githubusercontent.com/prosperpiusmbaruku007-ship-it/'
                     'AFRICA-GIANTS/main/kaggle/nli_regression.py', timeout=10)
    exec(r.text)

Run it in a Kaggle notebook with GPU (T4) enabled, Internet ON, and the AFRICA_GIANTS
secret attached (same secret eval.py uses for HuggingFace).

It is SELF-CONTAINED and READ-ONLY — it does NOT modify chike/scoring.py or write any
result back. It fetches the already-committed chike/scoring.py and eval_questions_001.jsonl
from GitHub raw, pulls the v15 stored gate results from HuggingFace, loads mDeBERTa-v3 on
the GPU, and evaluates the proposed Part 1 rule against all 190 shared question IDs plus
the 14 confirmed audit examples:

    NLI (mDeBERTa sw-sw, both directions), max contradiction >= 0.70  ==> score as FAIL

It reports the two numbers that gate the recommendation:
  * FALSE demotions: currently-PASS (reliable) answers wrongly flipped to FAIL  (MUST be ~0)
  * BENEFIT: currently-EXCLUDED contradictions recovered as correctly-scored FAIL
"""
import os, json, re, time, requests

# ---- auth (same secret name as eval.py) -----------------------------------
try:
    import kaggle_secrets
    HF_TOKEN = kaggle_secrets.UserSecretsClient().get_secret('AFRICA_GIANTS')
    print(f'[auth] HF token loaded ({HF_TOKEN[:6]}...)')
except Exception as e:
    HF_TOKEN = os.environ.get('HF_TOKEN', '')
    print(f'[auth] fallback env HF_TOKEN: {"set" if HF_TOKEN else "MISSING"}')

RAW = 'https://raw.githubusercontent.com/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS/main'
NOCACHE = {'Cache-Control': 'no-cache', 'Pragma': 'no-cache'}
cb = str(int(time.time() * 1000))
try:
    sha = requests.get('https://api.github.com/repos/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS/commits/main',
                       headers=NOCACHE, timeout=15).json().get('sha', '?')[:7]
    print(f'[git] main HEAD = {sha}')
except Exception as e:
    print(f'[git] HEAD check skipped: {e}')

# ---- fetch shared scorer (leaf module, stdlib-only) -----------------------
r = requests.get(f'{RAW}/chike/scoring.py?cb={cb}', headers=NOCACHE, timeout=20); r.raise_for_status()
_ns = {'__file__': 'scoring.py'}
exec(compile(r.text, 'chike/scoring.py', 'exec'), _ns)
score_question      = _ns['score_question']
scorer_reliability  = _ns['scorer_reliability']
print(f'[chike] scoring.py fetched ({len(r.text)} bytes)')

# ---- fetch questions + config ---------------------------------------------
qtext = requests.get(f'{RAW}/eval/accuracy_gate/eval_questions_001.jsonl?cb={cb}', headers=NOCACHE, timeout=20).text
qs = {}
for line in qtext.splitlines():
    line = line.strip()
    if line:
        q = json.loads(line); qs[q['id']] = q
CONFIG = requests.get(f'{RAW}/kaggle/chike_config.json?cb={cb}', headers=NOCACHE, timeout=20).json()
REFUSAL = CONFIG['refusal_phrases']
print(f'[data] {len(qs)} gate questions, {len(REFUSAL)} refusal phrases')

# ---- v15 stored gate results from HF --------------------------------------
from huggingface_hub import hf_hub_download
p = hf_hub_download(repo_id='prospAprospA007/africa-giants-adapter-v15',
                    filename='gate_001_results.json', repo_type='model', token=HF_TOKEN or None)
res = {rr['id']: rr for rr in json.load(open(p, encoding='utf-8'))['results']}
print(f'[data] {len(res)} v15 stored results')

# ---- NLI model on GPU ------------------------------------------------------
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
MN = 'MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7'
dev = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f'[nli] loading {MN} on {dev} ...')
tok = AutoTokenizer.from_pretrained(MN)
mdl = AutoModelForSequenceClassification.from_pretrained(MN).to(dev).eval()
lab = {v.lower(): k for k, v in mdl.config.id2label.items()}
iC = lab['contradiction']

def clean(g):
    for mk in ['\nuser', 'user_0', 'user ', '\n\n']:
        i = g.find(mk)
        if i > 40: g = g[:i]
    m = re.search(r'[Tt]hibitisha na[^)]*\)', g)
    if m: g = g[:m.end()]
    return g.strip()

@torch.no_grad()
def contra_pair(a, b):
    """max contradiction prob over both directions (sw-sw)."""
    enc = tok([a, b], [b, a], return_tensors='pt', truncation=True, max_length=256, padding=True).to(dev)
    pr = torch.softmax(mdl(**enc).logits, -1)[:, iC]
    return float(pr.max())

TH = 0.70
false_demote, recovered, already_fail = [], [], []
t0 = time.time(); n = 0
for qid, rr in res.items():
    q = dict(qs.get(qid, {})); q['id'] = qid
    q['answer_type'] = q.get('answer_type', rr.get('answer_type'))
    if q['answer_type'] == 'out_of_corpus_refusal':
        continue
    gen = rr['generated']; cln = clean(gen); csw = q.get('correct_answer_sw', '')
    c = contra_pair(csw, cln)
    n += 1
    if c >= TH:
        rel, reason = scorer_reliability(q, gen)
        regex = score_question(q, gen, REFUSAL)
        cur = ('PASS' if regex else 'FAIL') if rel else 'EXCLUDED'
        rec = {'id': qid, 'type': q['answer_type'], 'contra': round(c, 2), 'current': cur,
               'q': q.get('question_sw', '')[:55], 'gen': cln[:70]}
        (false_demote if cur == 'PASS' else recovered if cur == 'EXCLUDED' else already_fail).append(rec)
print(f'\n[nli] scored {n} non-refusal questions in {time.time()-t0:.0f}s on {dev}')

print('\n' + '=' * 70)
print(f'RULE: mDeBERTa sw-sw bidirectional contradiction >= {TH} => score as FAIL')
print('=' * 70)
print(f'\n### FALSE-DEMOTION RISK (currently-PASS wrongly flipped to FAIL): {len(false_demote)}  <-- MUST be ~0')
for x in false_demote: print('   ', x)
print(f'\n### BENEFIT (currently-EXCLUDED recovered as correctly-scored FAIL): {len(recovered)}')
for x in recovered: print('   ', x)
print(f'\n### already-FAIL, NLI agrees (no change): {len(already_fail)}')
for x in already_fail: print('   ', x['id'], x['type'], x['contra'])

# ---- explicit cross-check on the 14 audit examples ------------------------
AUDIT = ['eval_178','eval_114','eval_093','eval_176','eval_033','eval_019','eval_040',
         'eval_059','eval_180','eval_182','eval_165','eval_026','eval_157','eval_175']
TRUTH = {'eval_178':'FAIL','eval_114':'FAIL','eval_093':'FAIL','eval_176':'PASS','eval_033':'PASS',
         'eval_019':'PASS','eval_040':'PASS','eval_059':'FAIL','eval_180':'PASS','eval_182':'PASS',
         'eval_165':'PASS','eval_026':'PASS','eval_157':'PASS','eval_175':'PASS'}
print('\n### 14-example cross-check (contra >=0.70 -> FAIL):')
for qid in AUDIT:
    if qid not in res: continue
    q = dict(qs.get(qid, {})); q['id'] = qid; q['answer_type'] = q.get('answer_type', res[qid].get('answer_type'))
    cln = clean(res[qid]['generated'])
    c = contra_pair(q.get('correct_answer_sw',''), cln)
    verdict = 'FAIL(nli)' if c >= TH else 'no-demote'
    print(f'   {qid:11} truth={TRUTH[qid]:5} contra={c:.2f} -> {verdict}')
print('\nDONE — read FALSE-DEMOTION count above: if 0, the rule is safe at scale.')
