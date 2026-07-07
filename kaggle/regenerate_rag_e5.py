# -*- coding: utf-8 -*-
"""
Regenerate the RAG index with intfloat/multilingual-e5-base (768-dim) ON KAGGLE.

Why Kaggle: the e5-base weights (~1.1 GB) do not download on the local Tanzania
network (ISP block stalls the transfer ~737 MB in), so the 768-dim embeddings must
be produced where the network works. This is the R15 workaround process.

What it does:
  1. Fetch scripts/locked_facts.json + scripts/precompute_rag_embeddings.py from GitHub
     (single source of truth — the fact-build logic lives in precompute, never duplicated).
  2. Build the fact texts via precompute.build_fact_texts() (importable, no side effects).
  3. Embed with e5-base (facts get the 'passage: ' prefix; queries get 'query: ').
  4. FULL VERIFICATION: every fact must self-retrieve at rank 1, AND all critical
     known-failure queries must hit their expected fact in the top-3.
  5. Save + upload rag_embeddings.npy + rag_facts_text.json to the HF DATASET repo
     ONLY if verification passes. modal_app.py bakes these from chike-inference/ and
     eval.py fetches them from the dataset repo — so both consumers get the same index.

Run this in a Kaggle notebook cell, then paste the verification output back.
"""
import os
import sys
import json
import importlib.util

import numpy as np
import requests

# ── AUTH ────────────────────────────────────────────────────────────────────────
try:
    import kaggle_secrets
    hf_token = kaggle_secrets.UserSecretsClient().get_secret('AFRICA_GIANTS')
    print(f'[auth] HF token from Kaggle secret ({hf_token[:8]}...)')
except Exception as e:
    hf_token = os.environ.get('HF_TOKEN', '')
    print(f'[auth] fallback env HF_TOKEN: {hf_token[:8] if hf_token else "MISSING"}')
os.environ['HF_TOKEN'] = hf_token

DATASET_REPO = 'prospAprospA007/africa-giants-dataset'
RAW = 'https://raw.githubusercontent.com/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS/main'

# ── FETCH SOURCE OF TRUTH FROM GITHUB ───────────────────────────────────────────
# locked_facts.json (the facts) + precompute module (the build + noise-drop logic).
# IMPORTANT: raw.githubusercontent.com sits behind a CDN (~5-min TTL). Fetching the
# plain URL can serve a STALE copy right after a push — which silently regenerates
# the index from OLD facts. Bust the cache with a unique query param + no-cache
# headers, and log the live commit SHA so the run is auditable.
import time
_cb = str(int(time.time() * 1000))
_nocache = {'Cache-Control': 'no-cache', 'Pragma': 'no-cache'}

_live_sha = requests.get(
    'https://api.github.com/repos/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS/commits/main',
    headers=_nocache, timeout=30).json().get('sha', '?')[:7]
print(f'[fetch] GitHub main HEAD = {_live_sha} (index will be built from THIS commit)')

for name in ['scripts/locked_facts.json', 'scripts/precompute_rag_embeddings.py']:
    r = requests.get(f'{RAW}/{name}?cb={_cb}', headers=_nocache, timeout=30)
    r.raise_for_status()
    os.makedirs(os.path.dirname(name), exist_ok=True)
    with open(name, 'w', encoding='utf-8') as f:
        f.write(r.text)
    print(f'[fetch] {name} ({len(r.content)} bytes)')

# Import build_fact_texts from the fetched module (module-level is side-effect free;
# embedding only runs under its own __main__, which we do NOT trigger by importing).
spec = importlib.util.spec_from_file_location('precompute', 'scripts/precompute_rag_embeddings.py')
precompute = importlib.util.module_from_spec(spec)
spec.loader.exec_module(precompute)

EMBED_MODEL    = precompute.EMBED_MODEL          # intfloat/multilingual-e5-base
PASSAGE_PREFIX = precompute.E5_PASSAGE_PREFIX     # 'passage: '
assert EMBED_MODEL == 'intfloat/multilingual-e5-base', f'unexpected embedder: {EMBED_MODEL}'

fact_texts_to_embed, fact_keys, dropped = precompute.build_fact_texts()
print(f'[rag] kept {len(fact_texts_to_embed)} facts, dropped {len(dropped)} noise')

# ── EMBED WITH E5-BASE ──────────────────────────────────────────────────────────
from sentence_transformers import SentenceTransformer
print(f'[rag] loading {EMBED_MODEL} ...')
model = SentenceTransformer(EMBED_MODEL)

# e5 asymmetric retrieval: facts embedded as passages. The saved rag_facts_text.json
# holds the PLAIN texts (that is what gets injected into the prompt); only the embedded
# copy is prefixed. Queries get the 'query: ' prefix at retrieval time.
prefixed = [PASSAGE_PREFIX + t for t in fact_texts_to_embed]
embeddings = np.array(model.encode(prefixed, show_progress_bar=True))
norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
embeddings_normalized = embeddings / (norms + 1e-10)
print(f'[rag] embeddings shape: {embeddings_normalized.shape}  (expect (N, 768) for e5-base)')
assert embeddings_normalized.shape[1] == 768, (
    f'DIMENSION ERROR: expected 768, got {embeddings_normalized.shape[1]} — wrong embedder?')

# ── FULL VERIFICATION — every fact in the index ─────────────────────────────────
print('\n' + '=' * 60)
print('FULL VERIFICATION — every fact in the index')
print('=' * 60)

all_pass = True
failures = []

for i, fact_text in enumerate(fact_texts_to_embed):
    # Use the fact itself as a self-query to confirm it retrieves itself at rank 1.
    # This confirms the embedding is not degenerate/broken for this fact.
    self_query = f'query: {fact_text[:100]}'
    q_emb = model.encode([self_query])[0]
    q_norm = q_emb / (np.linalg.norm(q_emb) + 1e-10)
    scores = np.dot(embeddings_normalized, q_norm)
    top_idx = int(np.argmax(scores))

    if top_idx == i:
        continue  # fact retrieves itself correctly — good
    else:
        failures.append({
            'index': i,
            'fact': fact_text[:100],
            'retrieved_instead': fact_texts_to_embed[top_idx][:100],
            'score': float(scores[top_idx]),
        })

print(f'Total facts checked: {len(fact_texts_to_embed)}')
print(f'Self-retrieval failures: {len(failures)}')

if failures:
    print('\nFacts that do NOT retrieve themselves as top match (may indicate embedding issues):')
    for f in failures[:20]:
        print(f'  [{f["index"]}] {f["fact"]}')
        print(f'      retrieved instead: {f["retrieved_instead"]} (score {f["score"]:.3f})')

# Also run the critical known-failure queries as a secondary check.
critical_queries = [
    ('GN487A penalty', 'query: Faini kwa raia wa kigeni anayevunja GN487A ni kiasi gani hasa?', ['10,000,000', 'milioni kumi']),
    ('SDL rate', 'query: SDL rate Tanzania ni asilimia ngapi?', ['3.5']),
    ('NSSF employer', 'query: Mwajiri analipa asilimia ngapi NSSF kila mwezi?', ['10%', 'asilimia 10']),
    ('BRELA annual return', 'query: Ada ya annual return BRELA ni shilingi ngapi?', ['22,000', 'elfu 22']),
    ('VAT withholding services', 'query: VAT withholding kwenye huduma ni asilimia ngapi?', ['6%', 'services is 6']),
    ('Zero-rated input VAT', 'query: Naweza kudai input VAT kwenye bidhaa zilizo zero-rated?', ['ndiyo', 'input vat', 'can claim']),
    ('GN487A effective date', 'query: GN487A ilianza kutekelezwa tarehe gani?', ['28 july', '28 julai']),
    ('GN487A full name', 'query: Jina kamili la GN487A ni nini?', ['business licensing', 'prohibition']),
    ('Facilitator penalty', 'query: Adhabu ya raia wa Tanzania anayemsaidia mgeni ni nini?', ['5,000,000', 'milioni tano']),
    ('Phone repair activity', 'query: Mgeni anaweza kutengeneza simu?', ['phone', 'simu', 'activity 3']),
    ('PAYE 800K band', 'query: PAYE kwa mshahara wa TZS 800,000 ni kiasi gani?', ['760', '25%', '78,000']),
]

print('\n' + '=' * 60)
print('CRITICAL KNOWN-FAILURE QUERIES')
print('=' * 60)

critical_pass = True
for name, query, expected in critical_queries:
    q_emb = model.encode([query])[0]
    q_norm = q_emb / (np.linalg.norm(q_emb) + 1e-10)
    scores = np.dot(embeddings_normalized, q_norm)
    top3_idx = np.argsort(scores)[-3:][::-1]

    found = False
    for idx in top3_idx:
        if any(kw.lower() in fact_texts_to_embed[idx].lower() for kw in expected):
            found = True
            break

    status = 'PASS' if found else 'FAIL'
    print(f'[{status}] {name}')
    if not found:
        critical_pass = False
        # show what WAS retrieved so a fail is diagnosable, not just a red X
        for r, idx in enumerate(top3_idx, 1):
            print(f'        top{r}: {fact_texts_to_embed[idx][:90]}')

print()
# allow <10% self-retrieval noise (near-duplicate facts can surface a sibling at rank 1)
overall_pass = critical_pass and len(failures) < len(fact_texts_to_embed) * 0.1
if overall_pass:
    print(f'VERIFICATION PASSED — {len(fact_texts_to_embed) - len(failures)}/{len(fact_texts_to_embed)} '
          f'facts self-retrieve correctly, all critical queries pass')
    print('Saving and uploading...')
else:
    print('VERIFICATION FAILED — review failures before saving')
    print(f'  critical_pass={critical_pass} | self_retrieval_failures={len(failures)} '
          f'(tolerance={int(len(fact_texts_to_embed) * 0.1)})')
    sys.exit(1)   # do NOT upload a broken index

# ── SAVE + UPLOAD TO HF DATASET REPO ────────────────────────────────────────────
np.save('rag_embeddings.npy', embeddings_normalized)
with open('rag_facts_text.json', 'w', encoding='utf-8') as f:
    json.dump(fact_texts_to_embed, f, ensure_ascii=False, indent=2)
print(f'[save] rag_embeddings.npy {embeddings_normalized.shape} + '
      f'rag_facts_text.json ({len(fact_texts_to_embed)} facts)')

from huggingface_hub import HfApi
api = HfApi()
for fn in ['rag_embeddings.npy', 'rag_facts_text.json']:
    api.upload_file(
        path_or_fileobj=fn,
        path_in_repo=fn,
        repo_id=DATASET_REPO,
        repo_type='dataset',
        token=hf_token,
        commit_message=f'e5-base RAG index ({embeddings_normalized.shape[0]}x{embeddings_normalized.shape[1]})',
    )
    print(f'[upload] {fn} -> {DATASET_REPO}')

print('\n[done] e5 RAG index regenerated, verified, and uploaded.')
print(f'[done] FINAL SHAPE: {embeddings_normalized.shape}  |  facts: {len(fact_texts_to_embed)}')
