# -*- coding: utf-8 -*-
"""
Run the v16 ORCHESTRATOR against the 200-question gate — ON KAGGLE.

This is the test that has been missing: eval.py runs v15's own pipeline (its own
retrieve/decompose/generate) and only *borrows* two shared utility functions. THIS
script instead drives the real chike/orchestrator.py end-to-end (classify -> decompose
-> route -> retrieve -> generate -> validate/clean -> merge), with generation served by
the REAL fine-tuned v15 model via the raw-generation Modal endpoint (same LocalAdapter
path used for the manual spot-checks this session).

WHAT IT TESTS: the FACT-PATH-ONLY subset of the gate (190 of 200). The 10 questions the
orchestrator routes to its compute path are EXCLUDED, because slot extraction from the
8B is a known-open gap (the model won't emit JSON) — they would all return
<CLARIFICATION_NEEDED> and score 0, which is already understood. This run measures
whether the orchestrator matches v15's quality on everything it is actually built to
handle today.

HOW TO RUN (Kaggle notebook cell):
    import requests
    r = requests.get('https://raw.githubusercontent.com/prosperpiusmbaruku007-ship-it/'
                     'AFRICA-GIANTS/main/kaggle/eval_orchestrator.py', timeout=10)
    exec(r.text)

PREREQS (Kaggle Secrets):
    AFRICA_GIANTS     -> HuggingFace token (eval questions + RAG index download)
    MODAL_API_TOKEN   -> the ?token= value for the raw Modal endpoint

CAVEATS (read before interpreting a score delta vs eval.py's 91.1%):
  - The raw endpoint has NO StoppingCriteria (it is intentionally dumb); the orchestrator
    relies on chike.generation_cleanup.clean_reply's turn-truncation to cut the ramble.
    eval.py's own path uses in-process StoppingCriteria. For score_question (which checks
    number/keyword PRESENCE in the answer) this should not matter, but a delta is not
    purely "orchestrator logic" — it could be the stopping-mechanism difference.
  - Retrieval here uses the real chike.retrieval (e5-base + the same HF index eval.py
    loads), injected into the orchestrator.
  - 190 live HTTP calls to the Modal endpoint; cold starts may make the first calls slow.
"""
import os
import re
import sys
import json
import time
import subprocess
from collections import defaultdict, Counter
from datetime import datetime, timezone

import requests

# ── AUTH ────────────────────────────────────────────────────────────────────────
try:
    import kaggle_secrets
    _sec = kaggle_secrets.UserSecretsClient()
    hf_token = _sec.get_secret('AFRICA_GIANTS')
    modal_token = _sec.get_secret('MODAL_API_TOKEN')
    print(f'[auth] HF token ({hf_token[:6]}...) + Modal token ({modal_token[:6]}...) from Kaggle secrets')
except Exception as e:
    hf_token = os.environ.get('HF_TOKEN', '')
    modal_token = os.environ.get('CHIKE_MODAL_TOKEN', '')
    print(f'[auth] fallback env — HF:{bool(hf_token)} Modal:{bool(modal_token)} ({e})')
os.environ['HF_TOKEN'] = hf_token

RAW_ENDPOINT = os.environ.get(
    'CHIKE_RAW_ENDPOINT',
    'https://prosperpiusmbaruku007--chike-inference-generate-endpoint.modal.run')
os.environ['CHIKE_RAW_ENDPOINT'] = RAW_ENDPOINT
os.environ['CHIKE_MODAL_TOKEN'] = modal_token

REPO = 'prosperpiusmbaruku007-ship-it/AFRICA-GIANTS'
RAW = f'https://raw.githubusercontent.com/{REPO}/main'
DATASET_REPO = 'prospAprospA007/africa-giants-dataset'

# ── GET THE chike/ PACKAGE (git clone — the orchestrator imports ~10 submodules, so
#    the 2-file fetch-and-exec eval.py uses is not enough). Fresh clone = latest main;
#    works because the package __init__.py files are now tracked (repo-integrity fix). ──
_CLONE_DIR = '/kaggle/working/AFRICA-GIANTS'
if not os.path.isdir(_CLONE_DIR):
    subprocess.run(['git', 'clone', '--depth', '1',
                    f'https://github.com/{REPO}.git', _CLONE_DIR], check=True)
else:
    subprocess.run(['git', '-C', _CLONE_DIR, 'pull', '--ff-only'], check=False)
sys.path.insert(0, _CLONE_DIR)
_sha = subprocess.run(['git', '-C', _CLONE_DIR, 'rev-parse', '--short', 'HEAD'],
                      capture_output=True, text=True).stdout.strip()
print(f'[clone] chike package @ {_CLONE_DIR} (HEAD {_sha})')

from chike.orchestrator import Orchestrator          # noqa: E402
from chike.model_abstraction import LocalAdapter      # noqa: E402
from chike.retrieval import Retriever                 # noqa: E402

# ── CONFIG (from GitHub, cache-busted per R15) ──────────────────────────────────
_cb = str(int(time.time() * 1000))
_nocache = {'Cache-Control': 'no-cache', 'Pragma': 'no-cache'}
CONFIG = requests.get(f'{RAW}/kaggle/chike_config.json?cb={_cb}',
                      headers=_nocache, timeout=15).json()
SYSTEM_PROMPT      = CONFIG['system_prompt']
REFUSAL_PHRASES    = CONFIG['refusal_phrases']
OOC_PHRASES        = CONFIG.get('ooc_phrases', [])
ACCURACY_THRESHOLD = CONFIG['gate_thresholds']['in_corpus']
REFUSAL_THRESHOLD  = CONFIG['gate_thresholds']['out_of_corpus']
print(f'[config] version={CONFIG.get("version")} thresholds in={ACCURACY_THRESHOLD} ooc={REFUSAL_THRESHOLD}')

# ── DATA: 200 gate questions + RAG index (same HF sources as eval.py) ────────────
from huggingface_hub import hf_hub_download            # noqa: E402
_q_path = hf_hub_download(repo_id=DATASET_REPO, filename='eval_questions_001.jsonl',
                          repo_type='dataset', token=hf_token)
eval_questions = []
with open(_q_path, encoding='utf-8') as f:
    for line in f:
        if line.strip():
            eval_questions.append(json.loads(line))
assert len(eval_questions) == 200, f'expected 200 got {len(eval_questions)}'
print(f'[data] {len(eval_questions)} gate questions loaded')

_rag_npy = hf_hub_download(repo_id=DATASET_REPO, filename='rag_embeddings.npy',
                           repo_type='dataset', token=hf_token)
_rag_txt = hf_hub_download(repo_id=DATASET_REPO, filename='rag_facts_text.json',
                           repo_type='dataset', token=hf_token)
print('[data] RAG index downloaded (e5-base 768-dim)')

# ── SCORING — COPIED VERBATIM from kaggle/eval.py (SWAHILI_NUMBERS, extract_numbers,
#    normalize, score_question). Kept as a copy because eval.py is not importable without
#    triggering its full model-load + gate run. MUST STAY IN SYNC with eval.py's scoring. ──
SWAHILI_NUMBERS = {
    'moja': 1, 'mbili': 2, 'tatu': 3, 'nne': 4, 'tano': 5,
    'sita': 6, 'saba': 7, 'nane': 8, 'tisa': 9, 'kumi': 10,
    'ishirini': 20, 'thelathini': 30, 'arobaini': 40,
    'hamsini': 50, 'sitini': 60, 'sabini': 70,
    'themanini': 80, 'tisini': 90, 'mia': 100,
    'elfu': 1_000, 'milioni': 1_000_000,
}


def extract_numbers(text):
    text_lower = text.lower()
    nums = set()
    for m in re.findall(r'asilimia\s*(\d+(?:\.\d+)?)', text_lower):
        nums.add(m)
    for m in re.findall(r'(\d+(?:\.\d+)?)\s*%', text_lower):
        nums.add(m)
    for m in re.findall(r'tzs\s*([\d,]+)', text_lower):
        nums.add(m.replace(',', ''))
    for m in re.findall(r'\b(\d{3,}(?:,\d+)*)\b', text_lower):
        nums.add(m.replace(',', ''))
    for word, val in SWAHILI_NUMBERS.items():
        if re.search(r'\b' + word + r'\b', text_lower):
            nums.add(str(int(val)))
    return nums


def normalize(text):
    return ' '.join(text.lower().split())


def score_question(q, generated):
    gen_lower  = normalize(generated)
    atype      = q.get('answer_type', '')
    correct_sw = q.get('correct_answer_sw', '').lower()
    correct_en = q.get('correct_answer_en', '').lower()

    if atype == 'out_of_corpus_refusal':
        return any(p in gen_lower for p in [normalize(p) for p in REFUSAL_PHRASES])

    if atype in ('number', 'penalty'):
        correct_nums = extract_numbers(correct_sw) | extract_numbers(correct_en)
        gen_nums = extract_numbers(generated)
        if correct_nums and len(correct_nums & gen_nums) >= 1:
            return True
        # Fallback for frequency answers like 'mara moja kwa mwaka'
        frequency_words = {'mara', 'kila', 'mwaka', 'wiki', 'mwezi', 'siku', 'once', 'annually'}
        if any(w in gen_lower for w in frequency_words) and any(w in correct_sw for w in frequency_words):
            if len(gen_lower) > 15:
                return True
        if not correct_nums:
            return len(gen_lower) > 10
        return False

    if atype == 'yes_no':
        YES = {'ndiyo', 'ndio', 'yes', 'sahihi'}
        NO  = {'hapana', 'la', 'no', 'siyo', 'sivyo'}
        yes_in_correct = any(w in correct_sw for w in YES)
        no_in_correct  = any(w in correct_sw for w in NO)
        gen_yes = any(w in gen_lower for w in YES)
        gen_no  = any(w in gen_lower for w in NO)
        if yes_in_correct: return gen_yes
        if no_in_correct:  return gen_no
        return len(gen_lower) > 10

    if atype in ('definition', 'procedure'):
        correct_sw = re.sub(r'thibitisha na.*$', '', correct_sw, flags=re.IGNORECASE|re.DOTALL).strip()
        correct_en = re.sub(r'confirm with.*$',  '', correct_en, flags=re.IGNORECASE|re.DOTALL).strip()
        # Lowered from 6→5 chars and 4→3 words to handle Swahili synonym variation
        words = {w for w in (correct_sw + ' ' + correct_en).split() if len(w) >= 5}
        if not words: return len(gen_lower) > 20
        return len(words & set(gen_lower.split())) >= 3

    return len(gen_lower) > 20


# ── BUILD THE REAL ORCHESTRATOR ─────────────────────────────────────────────────
# Backend: LocalAdapter -> raw Modal endpoint (env set above). Retriever: real
# chike.retrieval over the HF index. OOC + system prompt injected from config.
_retriever = Retriever(emb_path=_rag_npy, texts_path=_rag_txt)
backend = LocalAdapter()  # reads CHIKE_RAW_ENDPOINT + CHIKE_MODAL_TOKEN from env
orch = Orchestrator(
    backend=backend,
    retriever=_retriever.retrieve,   # (question) -> list[str], top_k defaults to 3
    ooc_phrases=OOC_PHRASES,
    system_prompt=SYSTEM_PROMPT,
)

# ── FILTER TO THE FACT-PATH-ONLY SUBSET (orchestrator's own routing) ────────────
# A question is EXCLUDED if the orchestrator routes ANY of its sub-questions to the
# compute path (keyword + number). classify()-refused OOC questions stay IN.
subset, excluded = [], []
for q in eval_questions:
    text = q['question_sw']
    if not orch.classify(text):
        subset.append(q)                       # OOC-refusal -> orchestrator refuses
        continue
    kinds = [orch.route(p).kind for p in orch.decompose(text)]
    (excluded if 'compute' in kinds else subset).append(q)

print(f'[subset] fact-path-only: {len(subset)}/200 tested; '
      f'{len(excluded)} compute-routed excluded '
      f'({dict(Counter(q["subdomain"] for q in excluded))})')

# ── RUN THE SUBSET THROUGH Orchestrator.answer() ────────────────────────────────
print(f'[run] {len(subset)} questions through Orchestrator.answer() via the real model ...')
results = []
for i, q in enumerate(subset):
    try:
        generated = orch.answer(q['question_sw']).text
        passed = score_question(q, generated)
    except Exception as e:
        generated = f'ERROR: {e}'
        passed = False
    results.append({
        'id': q['id'], 'subdomain': q['subdomain'],
        'answer_type': q.get('answer_type', ''),
        'question_sw': q['question_sw'],
        'correct_answer_sw': q['correct_answer_sw'],
        'generated': generated, 'pass': passed,
    })
    if (i + 1) % 20 == 0 or i == 0:
        rp = sum(r['pass'] for r in results)
        print(f'  [{i+1}/{len(subset)}] running: {rp}/{i+1} = {rp/(i+1):.1%}')

# ── RESULTS (same split/format as eval.py, on the tested subset) ────────────────
by_subdomain = defaultdict(lambda: {'pass': 0, 'total': 0})
for r in results:
    by_subdomain[r['subdomain']]['total'] += 1
    by_subdomain[r['subdomain']]['pass'] += int(r['pass'])

in_corpus  = [r for r in results if r['subdomain'] != 'out_of_corpus']
out_corpus = [r for r in results if r['subdomain'] == 'out_of_corpus']
in_pass  = sum(r['pass'] for r in in_corpus)
out_pass = sum(r['pass'] for r in out_corpus)
in_acc  = in_pass  / len(in_corpus)  if in_corpus  else 0
out_acc = out_pass / len(out_corpus) if out_corpus else 0

print('\n' + '=' * 44)
print('v16 ORCHESTRATOR — FACT-PATH-ONLY GATE (subset)')
print('=' * 44 + '\n')
print(f'Tested {len(results)}/200 (compute-routed {len(excluded)} excluded)\n')
print('By subdomain:')
for sd, c in sorted(by_subdomain.items()):
    pct = c['pass'] / c['total']
    print(f'  {sd:<28} {c["pass"]}/{c["total"]} = {pct:.1%}  {"*" * int(pct * 20)}')
print(f'\nIn-corpus (subset):     {in_pass}/{len(in_corpus)} = {in_acc:.1%}   '
      f'(v15 full-gate baseline: 91.1%)')
print(f'Out-of-corpus refusal:  {out_pass}/{len(out_corpus)} = {out_acc:.1%}   '
      f'(v15 baseline: 100%)')
print('=' * 44)
print('NOTE: subset excludes the 10 compute-routed questions (known-open slot-extraction')
print('gap). This is NOT a full-gate score — it measures the v16 fact path only.')

out_path = '/kaggle/working/gate_orchestrator_subset.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump({
        'mode': 'v16_orchestrator_fact_path_subset',
        'commit': _sha,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'tested': len(results), 'excluded_compute_routed': len(excluded),
        'excluded_by_subdomain': dict(Counter(q['subdomain'] for q in excluded)),
        'in_corpus_subset': {'pass': in_pass, 'total': len(in_corpus), 'accuracy': in_acc},
        'out_of_corpus': {'pass': out_pass, 'total': len(out_corpus), 'accuracy': out_acc},
        'by_subdomain': {k: dict(v) for k, v in by_subdomain.items()},
        'results': results,
    }, f, ensure_ascii=False, indent=2)
print(f'[save] {out_path}')
