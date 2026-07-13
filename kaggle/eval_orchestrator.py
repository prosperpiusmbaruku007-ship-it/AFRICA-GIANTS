# -*- coding: utf-8 -*-
"""
Run the v16 ORCHESTRATOR against the 200-question gate — ON KAGGLE.

This is the test that has been missing: eval.py runs v15's own pipeline (its own
retrieve/decompose/generate) and only *borrows* shared utility functions. THIS
script instead drives the real chike/orchestrator.py end-to-end (classify -> decompose
-> route -> retrieve -> generate -> validate/clean -> merge), with generation served by
the REAL fine-tuned v15 model loaded DIRECTLY on Kaggle's GPU — the exact same 4-bit
load eval.py uses. No Modal, no HTTP, no raw-generation endpoint: one in-process model
load and direct generate() calls, so this script depends on nothing but the model
weights on HuggingFace, identical to how eval.py already runs on Kaggle.

WHAT IT TESTS: the FACT-PATH-ONLY subset of the gate (190 of 200). The 10 questions the
orchestrator routes to its compute path are EXCLUDED, because slot extraction from the
8B is a known-open gap (the model won't emit JSON) — they would all return
<CLARIFICATION_NEEDED> and score 0, which is already understood. This run measures
whether the orchestrator matches v15's quality on everything it is actually built to
handle today.

HOW TO RUN (Kaggle notebook cell, GPU accelerator ON):
    import requests
    r = requests.get('https://raw.githubusercontent.com/prosperpiusmbaruku007-ship-it/'
                     'AFRICA-GIANTS/main/kaggle/eval_orchestrator.py', timeout=10)
    exec(r.text)

PREREQS:
    - Kaggle GPU accelerator ON (loads the 8B in 4-bit, same as eval.py).
    - Kaggle Secret AFRICA_GIANTS -> HuggingFace token (model weights + eval questions
      + RAG index). This is the ONLY secret required — no MODAL_API_TOKEN.

NOTES (for interpreting a score delta vs eval.py's corrected baseline):
  - The in-process backend applies the SAME StoppingCriteria eval.py uses (stop_strings
    from chike_config.json), so the stopping mechanism is now identical to eval.py — any
    delta reflects orchestrator logic (classify/decompose/route/merge), not a
    stopping-mechanism difference as in the earlier Modal-endpoint version.
  - Retrieval uses the real chike.retrieval (e5-base + the same HF index eval.py loads),
    injected into the orchestrator.
  - 190 in-process generations on the Kaggle GPU; the first call is slower (model warmup).
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
# Required Kaggle Secret (attach before running):
#   AFRICA_GIANTS -> HuggingFace token (model weights + eval questions + RAG index).
# This is the ONLY secret needed — the model loads directly on the Kaggle GPU, so there
# is no Modal endpoint and no MODAL_API_TOKEN. A missing token fails LOUDLY here rather
# than falling back to '' (an empty token silently becomes 'Bearer ' and crashes deep
# inside hf_hub_download with no hint of the real cause).
try:
    import kaggle_secrets
    _sec = kaggle_secrets.UserSecretsClient()
except Exception as e:
    raise RuntimeError(
        'kaggle_secrets unavailable — this script must run on Kaggle with the '
        'AFRICA_GIANTS secret attached.') from e


def _kaggle_secret(label, env_fallback):
    try:
        val = _sec.get_secret(label)
    except Exception:
        val = ''
    return (val or os.environ.get(env_fallback, '') or '').strip()


hf_token = _kaggle_secret('AFRICA_GIANTS', 'HF_TOKEN')
if not hf_token:
    raise RuntimeError(
        'AFRICA_GIANTS (HuggingFace token) not found in Kaggle secrets — attach it to '
        'this notebook before running. It is the only secret this script needs.')
print(f'[auth] AFRICA_GIANTS ({hf_token[:6]}...) OK')
os.environ['HF_TOKEN'] = hf_token

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
from chike.model_abstraction import ModelBackend      # noqa: E402
from chike.retrieval import Retriever                 # noqa: E402
from chike.scoring import score_question              # noqa: E402  (shared scorer)

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
from huggingface_hub import hf_hub_download, HfApi     # noqa: E402
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

# SCORING is imported from the shared chike.scoring module (import above) — single source
# of truth with kaggle/eval.py. score_question(q, generated, REFUSAL_PHRASES) is called below.


# ── LOAD THE v15 MODEL DIRECTLY ON THE KAGGLE GPU (same 4-bit load as eval.py) ──
# In-process ModelBackend — no Modal, no HTTP. generate(prompt) returns the RAW
# completion (prompt -> new tokens -> decode); the orchestrator's own validate/clean
# stage (chike.generation_cleanup.clean_reply) does the turn-truncation downstream,
# exactly as it did for the Modal path this replaces. Because the raw completion is
# what feeds clean_reply, it is also what gets saved as raw_generated below.
import torch                                                            # noqa: E402
from transformers import (AutoTokenizer, AutoModelForCausalLM,          # noqa: E402
                          BitsAndBytesConfig, StoppingCriteria, StoppingCriteriaList)

ADAPTER_REPO = CONFIG.get('adapter_repo', 'prospAprospA007/africa-giants-adapter-v15')
GEN          = CONFIG['generation_params']
STOP_STRINGS = GEN.get('stop_strings',
                       ['\n\nQ:', '\n\nSwali:', '<|start_header_id|>', '\n\n---'])


class _StopOnSubstrings(StoppingCriteria):
    # Byte-identical to eval.py's StopOnSubstrings — hard-stop the instant the model
    # opens a new Q&A turn, so in-process generation matches eval.py's stop mechanism.
    def __init__(self, tokenizer, stop_strings):
        self.tokenizer = tokenizer
        self.stop_strings = stop_strings

    def __call__(self, input_ids, scores, **kwargs):
        text = self.tokenizer.decode(input_ids[0], skip_special_tokens=True)
        return any(s in text[-100:] for s in self.stop_strings)


class KaggleDirectBackend(ModelBackend):
    """In-process ModelBackend: loads the v15 adapter in 4-bit on the Kaggle GPU and
    generates directly, mirroring eval.py's load + generate config exactly. Returns the
    RAW completion (no clean_reply here — the orchestrator cleans downstream)."""

    def __init__(self, adapter_repo, token, gen_params, stop_strings):
        print(f'[model] Loading {adapter_repo} directly on GPU (4-bit) ...')
        self.tokenizer = AutoTokenizer.from_pretrained(
            adapter_repo, token=token, trust_remote_code=True)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        bnb = BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_quant_type='nf4',
            bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            adapter_repo, quantization_config=bnb, device_map='auto',
            token=token, trust_remote_code=True)
        self.model.eval()
        self.gen_params = dict(gen_params)
        self.stop_strings = stop_strings
        print('[model] Loaded OK')

    def generate(self, prompt, params=None):
        p = dict(self.gen_params)
        if params:
            p.update(params)                                   # caller overrides win
        inputs = self.tokenizer(prompt, return_tensors='pt').to(self.model.device)
        stopping = StoppingCriteriaList(
            [_StopOnSubstrings(self.tokenizer, self.stop_strings)])
        with torch.no_grad():
            out = self.model.generate(
                **inputs,
                max_new_tokens=p.get('max_new_tokens', 350),
                do_sample=False,
                temperature=1.0,
                repetition_penalty=p.get('repetition_penalty', 1.1),
                no_repeat_ngram_size=p.get('no_repeat_ngram_size', 0),
                stopping_criteria=stopping,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.pad_token_id,
            )
        new_tokens = out[0][inputs['input_ids'].shape[1]:]
        return self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


# ── BUILD THE REAL ORCHESTRATOR ─────────────────────────────────────────────────
# Backend: KaggleDirectBackend (in-process GPU load — no Modal). Retriever: real
# chike.retrieval over the HF index. OOC + system prompt injected from config.
_retriever = Retriever(emb_path=_rag_npy, texts_path=_rag_txt)
backend = KaggleDirectBackend(ADAPTER_REPO, hf_token, GEN, STOP_STRINGS)
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
    raw_generated = ''
    try:
        reply = orch.answer(q['question_sw'])
        generated = reply.text
        raw_generated = reply.raw_text   # pre-clean generation, for offline rescoring
        passed = score_question(q, generated, REFUSAL_PHRASES)
    except Exception as e:
        generated = f'ERROR: {e}'
        passed = False
    results.append({
        'id': q['id'], 'subdomain': q['subdomain'],
        'answer_type': q.get('answer_type', ''),
        'question_sw': q['question_sw'],
        'correct_answer_sw': q['correct_answer_sw'],
        # 'generated' = post-clean answer scored above; 'raw_generated' = pre-clean
        # model output, saved so a future clean_reply change can be rescored offline
        # without another GPU run (the gap that forced this validation cycle).
        'generated': generated, 'raw_generated': raw_generated, 'pass': passed,
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

# Upload so the file survives the ephemeral Kaggle session — same pattern eval.py uses
# for gate_001_results.json (uploaded to the adapter-v15 model repo). Kept as a separate
# filename so it sits ALONGSIDE the v15 baseline for a per-question diff, not overwriting it.
try:
    HfApi().upload_file(
        path_or_fileobj=out_path,
        path_in_repo='gate_orchestrator_subset.json',
        repo_id='prospAprospA007/africa-giants-adapter-v15',
        repo_type='model',
        token=hf_token,
        commit_message=(f'v16 orchestrator fact-path subset run — '
                        f'in_corpus={in_acc:.1%} on {len(in_corpus)} tested, for regression diagnosis'),
    )
    print('[upload] gate_orchestrator_subset.json -> prospAprospA007/africa-giants-adapter-v15')
except Exception as e:
    print(f'[upload] failed (non-critical): {e}')
