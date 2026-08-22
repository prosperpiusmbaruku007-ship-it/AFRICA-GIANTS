# -*- coding: utf-8 -*-
"""§1 fragment hypothesis, tested against two falsifiable targets instead of a random sample.

nat_27 needs fact [13] (VAT standard rate 18%). nat_36 needs fact [57] (EFD threshold
11,000,000). Both facts EXIST in the deployed index and neither is retrieved for its own
question. If rewriting the rows that outrank them does not surface them, the fragment
hypothesis is wrong, cheaply.

Four things measured, in order:

  0. GUARD-PHRASING CHECK. kaggle/regenerate_rag_e5.py ships R15 verification guards
     asserting these exact two facts retrieve in the top-3 ('VAT standard rate (nat_27
     displacement guard)', 'EFD threshold, VAT-unregistered (nat_36 displacement guard)').
     The regen was verified as passing. The grounding measurement says they are NOT
     retrieved. Both cannot be true, so the guard phrasing and the verbatim production
     phrasing are measured side by side.
  1. BASELINE rank of the target fact for the verbatim question.
  2. ARM A — rewrite the COMPETITORS that outrank the target (the fragment rows), leaving
     the target untouched. This is the fragment hypothesis proper: does clearing fragment
     noise let a real fact rise?
  3. ARM B — rewrite the TARGET itself Swahili-first, value-at-front, leaving competitors
     untouched. [13] is itself a fragment-shaped row, so this is the more direct lever.

Nothing is written back to the index. This is a measurement.

R18: committed before its result is written up.
Artifact: eval/results/targeted_rewrite.json
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, 'eval', 'results', 'targeted_rewrite.json')
PASSAGE_PREFIX = 'passage: '

TARGETS = [
    {
        'row': 'nat_27',
        'target_position': 13,
        'verbatim_question': 'vat ya asilimia ngapi naiweka kwenye bei ya bidhaa zangu',
        'guard_question': 'VAT ya asilimia ngapi naiweka kwenye bei ya bidhaa zangu?',
        # Swahili-first, value at the front, no English 'key: ' prefix — the shape R15's
        # own note says retrieves far better (see paye_bands_with_examples).
        'rewrite': 'Kiwango cha kawaida cha VAT Tanzania Bara ni asilimia 18 (18%). '
                   'Hiki ndicho kiwango unachoweka kwenye bei ya bidhaa unazouza. '
                   'Hakijabadilika tangu mwaka 2015 — si asilimia 14, si asilimia 16.',
    },
    {
        'row': 'nat_36',
        'target_position': 57,
        'verbatim_question': 'mauzo yangu ya mwaka ni milioni 15 na sijasajili vat je '
                             'nahitaji mashine ya risiti',
        'guard_question': 'Mauzo yangu ya mwaka ni milioni 15 na sijasajili vat je '
                          'nahitaji mashine ya risiti?',
        # [57] is ALREADY Swahili-first with the value near the front. The rewrite here
        # front-loads the ASK (mashine ya risiti / EFD) rather than the threshold label,
        # so this arm tests topic-alignment rather than the fragment shape.
        'rewrite': 'Unahitaji mashine ya risiti (EFD) ikiwa mauzo yako ya mwaka '
                   'yamefikia TZS 11,000,000 (milioni kumi na moja) — hata kama '
                   'hujasajili VAT. Kizingiti cha EFD ni TZS 11,000,000 kwa mwaka; '
                   'si TZS 200,000,000, hicho ni kizingiti cha kusajili VAT.',
    },
]


def main():
    import numpy as np
    from sentence_transformers import SentenceTransformer

    emb = np.load(os.path.join(REPO, 'chike-inference', 'rag_embeddings.npy'))
    with open(os.path.join(REPO, 'chike-inference', 'rag_facts_text.json'),
              encoding='utf-8') as f:
        texts = json.load(f)
    with open(os.path.join(REPO, 'eval', 'results', 'index_fragment_scan.json'),
              encoding='utf-8') as f:
        fragments = {r['position'] for r in json.load(f)['hits']['english_key_value']}

    model = SentenceTransformer('intfloat/multilingual-e5-base')

    def unit(v):
        return v / (np.linalg.norm(v) + 1e-10)

    def rank_of(matrix, question, position):
        q = unit(model.encode([f'query: {question}'])[0])
        scores = np.dot(matrix, q)
        order = np.argsort(scores)[::-1]
        rank = int(np.where(order == position)[0][0]) + 1
        top3 = [{'position': int(j), 'score': round(float(scores[j]), 4),
                 'text': texts[j][:110]} for j in order[:3]]
        return rank, round(float(scores[position]), 4), top3, order

    base_matrix = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-10)
    results = []

    for t in TARGETS:
        pos = t['target_position']
        rec = {'row': t['row'], 'target_position': pos,
               'target_text': texts[pos],
               'target_is_english_fragment': pos in fragments}

        # --- 0/1: baseline, both phrasings ---
        for label, q in (('verbatim', t['verbatim_question']),
                         ('guard_phrasing', t['guard_question'])):
            rank, score, top3, _ = rank_of(base_matrix, q, pos)
            rec[f'baseline_{label}'] = {'question': q, 'target_rank': rank,
                                        'target_score': score, 'top3': top3,
                                        'in_top3': rank <= 3}

        _, _, _, order = rank_of(base_matrix, t['verbatim_question'], pos)
        competitors = [int(j) for j in order[:rank_of(
            base_matrix, t['verbatim_question'], pos)[0] - 1]]
        frag_competitors = [c for c in competitors if c in fragments]
        rec['competitors_above_target'] = len(competitors)
        rec['fragment_competitors_above_target'] = len(frag_competitors)
        rec['fragment_share_of_competitors'] = (
            round(len(frag_competitors) / len(competitors), 3) if competitors else None)

        # --- ARM A: rewrite the fragment competitors, leave the target alone ---
        # A fragment 'x y z: value' becomes 'value ndiyo x y z.' — value at the front,
        # no English key prefix. Mechanical, so the arm tests the SHAPE, not my wording.
        arm_a = emb.copy()
        rewritten = []
        for c in frag_competitors:
            key, _, value = texts[c].partition(':')
            new_text = f'{value.strip()} — {key.strip()}.'
            rewritten.append({'position': c, 'from': texts[c], 'to': new_text})
            arm_a[c] = model.encode([PASSAGE_PREFIX + new_text])[0]
        arm_a_matrix = arm_a / (np.linalg.norm(arm_a, axis=1, keepdims=True) + 1e-10)
        rank_a, score_a, top3_a, _ = rank_of(arm_a_matrix, t['verbatim_question'], pos)
        rec['arm_a_rewrite_competitors'] = {
            'n_rewritten': len(rewritten), 'target_rank': rank_a,
            'target_score': score_a, 'in_top3': rank_a <= 3, 'top3': top3_a,
            'rank_change': rec['baseline_verbatim']['target_rank'] - rank_a,
            'samples': rewritten[:5],
        }

        # --- ARM B: rewrite the target itself, leave competitors alone ---
        arm_b = emb.copy()
        arm_b[pos] = model.encode([PASSAGE_PREFIX + t['rewrite']])[0]
        arm_b_matrix = arm_b / (np.linalg.norm(arm_b, axis=1, keepdims=True) + 1e-10)
        rank_b, score_b, top3_b, _ = rank_of(arm_b_matrix, t['verbatim_question'], pos)
        rec['arm_b_rewrite_target'] = {
            'new_text': t['rewrite'], 'target_rank': rank_b, 'target_score': score_b,
            'in_top3': rank_b <= 3, 'top3': top3_b,
            'rank_change': rec['baseline_verbatim']['target_rank'] - rank_b,
        }
        results.append(rec)

    out = {'measured': '2026-08-22',
           'harness': 'eval/index_quality/measure_targeted_rewrite.py',
           'note': 'measurement only — nothing written back to the index',
           'rows': results}
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    for r in results:
        print(f"\n{'=' * 72}\n{r['row']}  target [{r['target_position']}] "
              f"english_fragment={r['target_is_english_fragment']}")
        print(f"  text: {r['target_text'][:100]}")
        bv, bg = r['baseline_verbatim'], r['baseline_guard_phrasing']
        print(f"  BASELINE verbatim      : rank {bv['target_rank']:>4} "
              f"score {bv['target_score']} in_top3={bv['in_top3']}")
        print(f"  BASELINE guard phrasing: rank {bg['target_rank']:>4} "
              f"score {bg['target_score']} in_top3={bg['in_top3']}")
        print(f"  competitors above target: {r['competitors_above_target']} "
              f"({r['fragment_competitors_above_target']} are fragments, "
              f"share={r['fragment_share_of_competitors']})")
        a, b = r['arm_a_rewrite_competitors'], r['arm_b_rewrite_target']
        print(f"  ARM A (rewrote {a['n_rewritten']} competitors): rank {a['target_rank']:>4} "
              f"(change {a['rank_change']:+}) in_top3={a['in_top3']}")
        print(f"  ARM B (rewrote the target) : rank {b['target_rank']:>4} "
              f"(change {b['rank_change']:+}) in_top3={b['in_top3']}")
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()
