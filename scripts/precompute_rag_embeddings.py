#!/usr/bin/env python3
"""
Run this locally after updating locked_facts.json to regenerate
Cerebrium RAG embeddings. Commit the output files and redeploy.

Usage: python scripts/precompute_rag_embeddings.py
"""
import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer

FACTS_PATH   = 'scripts/locked_facts.json'
OUTPUT_NPY   = 'chike-inference/rag_embeddings.npy'
OUTPUT_TEXTS = 'chike-inference/rag_facts_text.json'
EMBED_MODEL  = 'paraphrase-multilingual-MiniLM-L12-v2'

print(f'[rag] Loading model: {EMBED_MODEL}')
model = SentenceTransformer(EMBED_MODEL)

print(f'[rag] Loading facts from {FACTS_PATH}')
with open(FACTS_PATH, encoding='utf-8') as f:
    facts = json.load(f)

fact_texts = []
for k, v in facts.items():
    if k == '_meta':
        continue
    if isinstance(v, dict):
        text = v.get('fact') or f"{k}: {v.get('correct_value', str(v))}"
    else:
        text = f"{k}: {v}"
    fact_texts.append(text)

print(f'[rag] Embedding {len(fact_texts)} facts...')
embeddings = model.encode(fact_texts, show_progress_bar=True)

# Pre-normalize to unit vectors so inference cosine similarity == plain dot-product.
# (Raw un-normalized vectors made retrieval rank wrong facts.)
embeddings = np.array(embeddings)
norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
embeddings = embeddings / (norms + 1e-10)
print(f'[rag] normalized embeddings for cosine similarity')

np.save(OUTPUT_NPY, embeddings)
with open(OUTPUT_TEXTS, 'w', encoding='utf-8') as f:
    json.dump(fact_texts, f, ensure_ascii=False, indent=2)

print(f'[rag] Saved {OUTPUT_NPY} ({embeddings.shape})')
print(f'[rag] Saved {OUTPUT_TEXTS}')
print(f'[rag] File sizes:')
print(f'  rag_embeddings.npy:  {os.path.getsize(OUTPUT_NPY) / 1024:.1f} KB')
print(f'  rag_facts_text.json: {os.path.getsize(OUTPUT_TEXTS) / 1024:.1f} KB')
print(f'[rag] Done. Commit both files and redeploy Cerebrium.')
