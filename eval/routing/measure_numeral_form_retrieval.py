# -*- coding: utf-8 -*-
"""Why does 'watu watano' get a wrong SDL rate when 'watu 5' does not?

Both phrasings route identically (detect_intent -> none, fact path), so ROUTING cannot be the
explanation. The remaining variable is retrieval: a different query string retrieves a
different top-k, and the fact path can only say what it was handed.

This reproduces production's retrieval exactly — same e5-base model, same 'query: ' prefix,
same cosine normalisation, same index (chike-inference/rag_embeddings.npy) — and diffs the
top-k for each word/digit pair.

Runs locally: intfloat/multilingual-e5-base is already in the HF cache, so no download.

R18: committed before its result is written up.
Artifact: eval/results/numeral_form_retrieval.json
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, 'eval', 'results', 'numeral_form_retrieval.json')

# (label, word-numeral phrasing, digit phrasing)
PAIRS = [
    ('nick_01_vs_02',
     'nimeajiri watu watano tu je nalipa ile ya mafunzo',
     'nimeajiri watu 5 tu je nalipa ile ya mafunzo'),
    ('six_generalisation',
     'nimeajiri watu sita tu je nalipa ile ya mafunzo',
     'nimeajiri watu 6 tu je nalipa ile ya mafunzo'),
    ('twelve_above_threshold',
     'nimeajiri watu kumi na wawili je nalipa ile ya mafunzo',
     'nimeajiri watu 12 je nalipa ile ya mafunzo'),
]
TOP_K = 3


def main():
    import numpy as np
    from sentence_transformers import SentenceTransformer

    emb = np.load(os.path.join(REPO, 'chike-inference', 'rag_embeddings.npy'))
    with open(os.path.join(REPO, 'chike-inference', 'rag_facts_text.json'),
              encoding='utf-8') as f:
        texts = json.load(f)

    model = SentenceTransformer('intfloat/multilingual-e5-base')
    norms = np.linalg.norm(emb, axis=1, keepdims=True)
    normalized = emb / (norms + 1e-10)

    def topk(q):
        v = model.encode([f'query: {q}'])[0]
        v = v / (np.linalg.norm(v) + 1e-10)
        scores = np.dot(normalized, v)
        idx = np.argsort(scores)[-TOP_K:][::-1]
        return [{'rank': i + 1, 'position': int(j), 'score': round(float(scores[j]), 4),
                 'text': texts[j]} for i, j in enumerate(idx)]

    rows = []
    for label, word_q, digit_q in PAIRS:
        w, d = topk(word_q), topk(digit_q)
        w_pos = {f['position'] for f in w}
        d_pos = {f['position'] for f in d}
        rows.append({
            'pair': label,
            'word_query': word_q,
            'digit_query': digit_q,
            'word_topk': w,
            'digit_topk': d,
            'identical': w_pos == d_pos,
            'only_in_word': sorted(w_pos - d_pos),
            'only_in_digit': sorted(d_pos - w_pos),
        })
        print(f'\n=== {label} — identical top-{TOP_K}: {w_pos == d_pos} ===')
        print(f'WORD : {word_q}')
        for f in w:
            print(f"   {f['rank']} [{f['position']}] {f['score']}  {f['text'][:95]}")
        print(f'DIGIT: {digit_q}')
        for f in d:
            print(f"   {f['rank']} [{f['position']}] {f['score']}  {f['text'][:95]}")

    out = {
        'measured': '2026-08-22',
        'purpose': 'isolate whether Swahili word-numerals change fact-path retrieval',
        'harness': 'eval/routing/measure_numeral_form_retrieval.py',
        'embedding_model': 'intfloat/multilingual-e5-base',
        'index': 'chike-inference/rag_embeddings.npy',
        'top_k': TOP_K,
        'pairs_with_different_topk': [r['pair'] for r in rows if not r['identical']],
        'rows': rows,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f'\n[saved] {OUT}')
    print(f"[pairs differing] {out['pairs_with_different_topk']}")


if __name__ == '__main__':
    main()
