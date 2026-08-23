# -*- coding: utf-8 -*-
"""CLASS ANALYSIS of the seven wrong veto-diverted rows: was the fact retrieved, and what happened.

THE SHARPEST CASE THIS PROJECT HAS. On these rows the system **knew enough to refuse to compute**
— a compute-path guard declined the question — and then produced a wrong number anyway. For the
covered subset it also **held the relevant fact**. Nothing about retrieval was uncertain and
nothing about routing was accidental.

WHAT THIS HARNESS DECIDES, per row, and it is a fork with two very different consequences:

  RETRIEVED_AND_DISCARDED  the anchor fact was in the top-3 the model was given, and the reply
                           contradicts it. This is the DISCARD question arriving where it
                           actually matters. The 2026-08-22 discard measurement put the rate at
                           ~1 in 13 on the natural 48 — a set on which the model was mostly
                           RIGHT. If it is far higher here, that measurement generalised from
                           the wrong population.
  NOT_RETRIEVED            the anchor fact exists but did not reach the prompt. Then this is
                           ask-alignment, on rows that already have a measured lever: leading a
                           fact with the asker's vocabulary moved nat_36 from rank 17 to rank 1
                           and swung nat_28 by 69 ranks.
  NO_FACT_EXISTS           the corpus holds nothing that answers it. Coverage, not retrieval.

ANCHOR FACTS ARE HAND-IDENTIFIED AND THE REASON IS RECORDED PER ROW. That is a judgement and is
labelled as one: it is the claim "THIS is the fact that would have prevented THIS wrong answer",
which no mechanical rule can make. Index positions are resolved by MATCHING TEXT, never by a
stored row number — pinning a verdict to an index position is R18 instance 1, where the index
moved underneath the pins and they kept asserting the old verdict silently.

Retrieval is the production path: e5-base, `query:`/`passage:` prefixes, cosine over the deployed
index, top_k=3. Runs offline from the local HF cache.

R18: committed before its result is written up.
Artifact: eval/results/covered_half_class_analysis.json
"""
import json
import os
import sys

os.environ.setdefault('HF_HUB_OFFLINE', '1')
os.environ.setdefault('TRANSFORMERS_OFFLINE', '1')

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)

LIVE = os.path.join(REPO, 'eval', 'results', 'veto_diversion_live.json')
ADJ = os.path.join(REPO, 'eval', 'results', 'veto_diversion_live_adjudication.json')
INDEX_TEXT = os.path.join(REPO, 'chike-inference', 'rag_facts_text.json')
INDEX_EMB = os.path.join(REPO, 'chike-inference', 'rag_embeddings.npy')
OUT = os.path.join(REPO, 'eval', 'results', 'covered_half_class_analysis.json')

TOP_K = 3

# id -> (substring that identifies the anchor fact in the index, why it is the anchor).
# None means the corpus holds nothing that answers the question.
ANCHORS = {
    'eval_010': ('vat registration threshold: VAT registration threshold is TZS 200,000,000',
                 'The reply asserts the trader has already crossed the 100M/6-month threshold. '
                 'This fact states BOTH limbs — 200M/12mo OR 100M/6mo — and the question gives '
                 'only an annual figure, so having it in context is what separates "20M more" '
                 'from "you have already crossed".'),
    'eval_337': ('NSSF jumla: asilimia 20 ya mshahara',
                 'The reply gives the NSSF rate as 10%. This fact states the total as 20% and '
                 'names the 10+10 split, which is exactly the distinction the reply collapses.'),
    'eval_342': ('paye all bands sequence',
                 'The reply says the top PAYE rate is 20%. This fact carries the whole band '
                 'sequence ending "30% above TZS 1M", so the top rate is legible from it '
                 'without any arithmetic.'),
    'eval_348': ('NSSF split triggers',
                 'The reply agrees that 10/10 is the only lawful split. This fact enumerates '
                 'all three — 10+10, 15+5, 20+0 — and is the single row that refutes the '
                 'premise.'),
    'pic_11': ('presumptive tax ceiling 100m',
               'The reply invents a presumptive ceiling of "milioni 10". This fact states TZS '
               '100,000,000 and is the direct contradiction.'),
    'pic_04': (None,
               'Corporate income tax is not in the corpus at all. 30% of PROFIT for a company '
               'appears in no fact, so no retrieval could have prevented this reply.'),
    'pic_10': (None,
               'The presumptive TRANSPORT schedule (First Schedule para 2(5), a per-vehicle '
               'table) is not in the corpus and the engine does not implement it.'),
}


def main():
    import numpy as np
    from sentence_transformers import SentenceTransformer

    with open(LIVE, encoding='utf-8') as f:
        live = {r['id']: r for r in json.load(f)['rows']}
    with open(ADJ, encoding='utf-8') as f:
        adj = json.load(f)
    wrong_ids = [r['id'] for r in adj['rows'] if r['verdict'] == 'WRONG']
    assert wrong_ids, 'no WRONG rows in the adjudication — nothing to analyse'
    assert set(wrong_ids) == set(ANCHORS), (
        f'anchor map and WRONG set disagree: {set(wrong_ids) ^ set(ANCHORS)}')

    with open(INDEX_TEXT, encoding='utf-8') as f:
        texts = json.load(f)
    emb = np.load(INDEX_EMB)
    assert emb.shape[0] == len(texts), (emb.shape, len(texts))
    emb = emb / np.linalg.norm(emb, axis=1, keepdims=True)

    model = SentenceTransformer('intfloat/multilingual-e5-base')

    rows = []
    for rid in wrong_ids:
        needle, why = ANCHORS[rid]
        q = live[rid]['question']
        qv = model.encode([f'query: {q}'], normalize_embeddings=True)[0]
        sims = qv @ emb.T
        order = list(np.argsort(-sims))
        top = [int(i) for i in order[:TOP_K]]

        if needle is None:
            klass, anchor_pos, anchor_rank = 'NO_FACT_EXISTS', None, None
        else:
            # RESOLVE BY TEXT, never by a stored index position — R18 instance 1.
            hits = [i for i, t in enumerate(texts) if needle in t]
            assert len(hits) == 1, (
                f'{rid}: anchor needle matched {len(hits)} index rows; it must identify exactly '
                f'one or the verdict below is about an unknown row')
            anchor_pos = hits[0]
            anchor_rank = order.index(anchor_pos) + 1
            klass = ('RETRIEVED_AND_DISCARDED' if anchor_pos in top else 'NOT_RETRIEVED')

        rows.append({
            'id': rid, 'question': q, 'reply': live[rid].get('reply'),
            'expected_sw': live[rid].get('expected_sw'),
            'mechanism': [c['mechanism'] for c in live[rid]['causes']],
            'anchor_needle': needle, 'anchor_why': why,
            'anchor_index_pos': anchor_pos, 'anchor_rank': anchor_rank,
            'anchor_score': (round(float(sims[anchor_pos]), 4)
                             if anchor_pos is not None else None),
            'class': klass,
            'top3': [{'pos': i, 'score': round(float(sims[i]), 4), 'text': texts[i][:150]}
                     for i in top],
        })

    counts = {}
    for r in rows:
        counts[r['class']] = counts.get(r['class'], 0) + 1

    out = {
        'measured': '2026-08-23',
        'harness': 'eval/routing/analyse_covered_half.py',
        'source': ['eval/results/veto_diversion_live.json',
                   'eval/results/veto_diversion_live_adjudication.json'],
        'method': 'Anchor facts hand-identified with the reason recorded per row (JUDGEMENT, '
                  'labelled). Index positions resolved by TEXT MATCH, never by a stored row '
                  'number. Retrieval is the production path: e5-base, query:/passage: prefixes, '
                  'cosine, top_k=3.',
        'top_k': TOP_K,
        'index_rows': len(texts),
        'counts': counts,
        'rows': rows,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(json.dumps(counts, indent=2))
    print()
    for r in rows:
        print(f"=== {r['id']:<10}{r['class']:<26}"
              f"anchor rank {r['anchor_rank']}  score {r['anchor_score']}")
        print(f"  Q: {r['question'][:100]}")
        print(f"  A: {(r['reply'] or '')[:150]}")
        for t in r['top3']:
            print(f"     top3 [{t['pos']:>3}] {t['score']}  {t['text'][:100]}")
        print()
    print(f'[saved] {OUT}')


if __name__ == '__main__':
    main()
