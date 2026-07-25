"""Group B retrieval probe (RUN ON KAGGLE — local Tanzania network blocks the e5 download).

Purpose: for eval_162 (mgeni) and eval_347 (EFD threshold), the CORRECT fact exists in
locked_facts.json AND is present in the RAG index, yet the model answered wrongly. This probe
determines which sub-cause applies by showing what actually ranks top-k for each query against
the LIVE e5 index:
  - target fact IN the top-3 the model sees  -> HALLUCINATION (model ignored a retrieved fact)
  - target fact NOT in top-3                 -> RETRIEVAL-RANKING failure (fixable: e.g. add a
                                                Swahili-first fact / retrieval-side change)

It mirrors production retrieval EXACTLY (chike-inference/modal_app.py retrieve_facts):
  intfloat/multilingual-e5-base, 'query: ' prefix, L2-normalized cosine, top_k=3.
Read-only: fetches the committed index from GitHub main (cache-busted) and only queries it.
Nothing is rebuilt, saved, or uploaded.
"""
import json
import time
import numpy as np
import requests
from sentence_transformers import SentenceTransformer

RAW = 'https://raw.githubusercontent.com/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS/main'
EMBED_MODEL = 'intfloat/multilingual-e5-base'
TOP_K = 3  # production top_k in modal_app.retrieve_facts

_nocache = {'Cache-Control': 'no-cache', 'Pragma': 'no-cache'}

# Verify which commit the index we are probing was built from (raw CDN ~5-min TTL — same
# stale-cache caveat as regenerate_rag_e5.py; cache-bust and log the HEAD sha).
_sha = requests.get('https://api.github.com/repos/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS/commits/main',
                    headers=_nocache, timeout=30).json().get('sha', '?')[:7]
print(f'[fetch] GitHub main HEAD = {_sha} (probing the index committed at THIS commit)')

_cb = int(time.time())
emb_bytes = requests.get(f'{RAW}/chike-inference/rag_embeddings.npy?cb={_cb}', headers=_nocache, timeout=60).content
with open('rag_embeddings.npy', 'wb') as f:
    f.write(emb_bytes)
facts = requests.get(f'{RAW}/chike-inference/rag_facts_text.json?cb={_cb}', headers=_nocache, timeout=60).json()
emb = np.load('rag_embeddings.npy')
norms = np.linalg.norm(emb, axis=1, keepdims=True)
emb_norm = emb / (norms + 1e-10)
print(f'[load] index: {emb_norm.shape[0]} facts, dim {emb_norm.shape[1]} (expect 768)')
assert emb_norm.shape[0] == len(facts), 'embeddings/facts length mismatch'

model = SentenceTransformer(EMBED_MODEL)

# (label, exact eval question, acceptable target substrings that mean "the correct fact") ----
PROBES = [
    ('eval_162 mgeni',
     "'Mgeni' katika GN 487A inamaanisha nani hasa?",
     ['mgeni cap357', "defines 'non-citizen'", 'cap.357', 'marriage', 'kuoa au kuolewa']),
    ('eval_347 EFD threshold',
     'Kizingiti cha kuanza kutumia EFD ni mauzo ya TZS 200,000,000, sivyo?',
     ['efd threshold tzs 11m', '11 million', '11m']),
]

for label, question, targets in PROBES:
    q = model.encode([f'query: {question}'])[0]
    q = q / (np.linalg.norm(q) + 1e-10)
    scores = np.dot(emb_norm, q)
    order = np.argsort(scores)[::-1]
    print('\n' + '=' * 78)
    print(f'{label}\n  Q: {question}')
    top = order[:5]
    hit_rank = None
    for rank, i in enumerate(order[:TOP_K]):
        if any(t.lower() in facts[i].lower() for t in targets):
            hit_rank = rank + 1
            break
    for rank, i in enumerate(top):
        star = ' <== TARGET' if any(t.lower() in facts[i].lower() for t in targets) else ''
        intop = '*' if rank < TOP_K else ' '
        print(f'  {intop}#{rank+1} {scores[i]:.4f}  {facts[i][:96]}{star}')
    verdict = (f'target IN top-{TOP_K} (rank {hit_rank}) -> HALLUCINATION'
               if hit_rank else f'target NOT in top-{TOP_K} -> RETRIEVAL-RANKING failure')
    print(f'  VERDICT: {verdict}')
