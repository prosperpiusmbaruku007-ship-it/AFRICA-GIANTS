# -*- coding: utf-8 -*-
"""WHAT DOES GROWTH DO TO RETRIEVAL? Rank of a known-correct fact as a function of index size.

THE QUESTION, and it gates the whole corpus-expansion plan. The narrative's Tier 1A target is 600
pairs; the deployed index holds 221 rows and already buries the correct fact at rank 16-86 for six
questions whose answer it contains. Before committing to any growth target, the relationship
between index size and burial depth should be a number rather than a worry.

METHOD. For each anchor question, sample random subsets of the deployed index that ALWAYS retain
the anchor row, at sizes 40 / 80 / 120 / 160 / 221, K trials each, and record the anchor's mean
rank. Query embeddings are computed once per question; subsetting needs no re-embedding because
cosine is per-row and independent. Then test whether **rank / n** is stable across sizes -- because
if it is, burial depth is a fixed PERCENTILE and growth scales it linearly, which is the difference
between "600 rows is fine" and "600 rows triples the burial".

⚠️ THE LIMIT, STATED IN THE INSTRUMENT RATHER THAN THE WRITE-UP, because a caveat that travels
separately from its number does not travel:

  1. **Subsets of today's rows are not the DISTRIBUTION 600 real rows would have.** They are the
     same 221 rows thinned. A real 600-row index would hold new topics, and whether those compete
     with a given anchor depends on what they are about. This BOUNDS the effect; it does not
     predict it.
  2. **Everything above n=221 is EXTRAPOLATION**, reported as such and never as a measurement.
     There are no rows beyond 221 to measure with, and inventing them would be fabrication.
  3. The anchors are the six rows already known to be buried plus `nat_43`, which is at rank 1
     after an ask-alignment rewrite. **nat_43 is the control that matters**: if burial were purely
     a function of index size, a rank-1 row would drift down with n like the others. If it does
     not, then WORDING dominates SIZE, and the growth risk is smaller than the curation win.

R18: committed before it runs.
Artifact: eval/results/rank_vs_index_size.json
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, 'eval', 'results', 'rank_vs_index_size.json')
INDEX_TEXT = os.path.join(REPO, 'chike-inference', 'rag_facts_text.json')
INDEX_EMB = os.path.join(REPO, 'chike-inference', 'rag_embeddings.npy')
NAT48 = os.path.join(REPO, 'eval', 'accuracy_gate', 'edge_probe_natural_048.jsonl')

SIZES = [40, 80, 120, 160, 221]
TRIALS = 40
SEED = 3407                      # the project's training seed, reused so runs are comparable
EXTRAPOLATE_TO = [300, 450, 600]

ANCHORS = {
    'nat_05': 'kiwango cha mafunzo ni asilimia tatu na nusu',
    'nat_23': 'kiwango cha mafunzo ni asilimia tatu na nusu',
    'nat_28': 'vat withholding services: VAT withholding on services is 6%',
    'nat_33': 'ada ya kuwasilisha ritani (annual return) ya kampuni kila mwaka ni TZS 22,000',
    'nat_43': 'sekta 16 na sekta ndogo 46',      # THE CONTROL — rank 1 after ask-alignment
    'nat_44': 'vat withholding goods: VAT withholding on goods is 3%',
    'nat_45': 'wcf accident reporting deadline: 7 working days',
}


def main():
    import numpy as np
    from sentence_transformers import SentenceTransformer

    texts = json.load(open(INDEX_TEXT, encoding='utf-8'))
    emb = np.load(INDEX_EMB)
    assert emb.shape[0] == len(texts) == 221, (emb.shape, len(texts))
    emb = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-10)
    nat = {r['id']: r for r in (json.loads(l) for l in open(NAT48, encoding='utf-8') if l.strip())}
    model = SentenceTransformer('intfloat/multilingual-e5-base')
    rng = np.random.default_rng(SEED)
    n_total = len(texts)

    rows = []
    for rid, needle in ANCHORS.items():
        hits = [i for i, t in enumerate(texts) if needle in t]
        assert len(hits) == 1, f'{rid}: needle matched {len(hits)} rows'
        anchor = hits[0]
        q = nat[rid]['question']
        qv = model.encode([f'query: {q}'], normalize_embeddings=True)[0]
        sims = qv @ emb.T
        others = np.array([i for i in range(n_total) if i != anchor])
        anchor_score = float(sims[anchor])

        curve = {}
        for n in SIZES:
            if n > n_total:
                continue
            if n == n_total:
                # exact, no sampling needed
                rank = int((sims > anchor_score).sum()) + 1
                curve[n] = {'mean_rank': float(rank), 'sd': 0.0, 'trials': 1,
                            'rank_over_n': round(rank / n, 4), 'exact': True}
                continue
            ranks = []
            for _ in range(TRIALS):
                pick = rng.choice(others, size=n - 1, replace=False)
                ranks.append(int((sims[pick] > anchor_score).sum()) + 1)
            ranks = np.array(ranks, dtype=float)
            curve[n] = {'mean_rank': round(float(ranks.mean()), 2),
                        'sd': round(float(ranks.std()), 2), 'trials': TRIALS,
                        'rank_over_n': round(float(ranks.mean()) / n, 4), 'exact': False}

        # Is burial a stable PERCENTILE? If rank/n is flat, growth scales rank linearly.
        ratios = [curve[n]['rank_over_n'] for n in curve]
        spread = round(max(ratios) - min(ratios), 4)
        ratio_at_full = curve[n_total]['rank_over_n']
        extrap = {n: round(ratio_at_full * n, 1) for n in EXTRAPOLATE_TO}

        rows.append({
            'id': rid, 'question': q, 'anchor_row': anchor,
            'anchor_score': round(anchor_score, 4),
            'rank_at_221': curve[n_total]['mean_rank'],
            'curve': curve,
            'rank_over_n_spread': spread,
            'percentile_is_stable': spread < 0.05,
            'EXTRAPOLATED_rank': extrap,
        })
        c = ' '.join(f"{n}:{curve[n]['mean_rank']:.0f}" for n in sorted(curve))
        print(f"{rid}  {c}   rank/n spread={spread}   extrap600={extrap[600]}")

    control = next(r for r in rows if r['id'] == 'nat_43')
    stable = [r['id'] for r in rows if r['percentile_is_stable']]

    blob = {
        'measured': '2026-08-25',
        'harness': 'eval/index_quality/measure_rank_vs_index_size.py',
        'index_rows': n_total, 'sizes_measured': SIZES, 'trials_per_size': TRIALS, 'seed': SEED,
        'THE_LIMIT': {
            'what_this_is': 'subsets of TODAY\'S 221 rows, thinned. It BOUNDS the effect of '
                            'growth under the assumption that new rows compete like existing '
                            'ones.',
            'what_this_is_not': 'a prediction. A real 600-row index holds new TOPICS, and whether '
                                'they compete with a given anchor depends on what they are about.',
            'above_221_is_extrapolation': 'reported as EXTRAPOLATED_rank and never as measured. '
                                          'There are no rows beyond 221 to measure with.',
        },
        'control_nat_43': {
            'why': 'rank 1 after an ask-alignment rewrite. If burial were purely a function of '
                   'index size, a rank-1 row would drift down with n like the others.',
            'curve': control['curve'],
            'extrapolated': control['EXTRAPOLATED_rank'],
            'reading': 'if it stays at 1 across every size, WORDING dominates SIZE and the growth '
                       'risk is smaller than the curation win.',
        },
        'percentile_stable_for': stable,
        'rows': rows,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(blob, f, ensure_ascii=False, indent=2)
    print(f"\npercentile stable for {len(stable)}/{len(rows)}: {stable}")
    print(f'[saved] {OUT}')


if __name__ == '__main__':
    main()
