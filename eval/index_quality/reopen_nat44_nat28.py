# -*- coding: utf-8 -*-
"""Re-open the nat_44 / nat_28 withholding-rewrite decision with a SOUND check.

The rewrite measured nat_44 rank 33->4 and nat_28's rate half 33->8 — real wins — and was HELD
BACK on 2026-08-17 because it "regresses nat_27". That basis is gone twice over:

  1. nat_27 is UNGROUNDED. Fact [13] (VAT standard rate) is at rank 15 for its verbatim
     question and is not retrieved either way, so there is no live behaviour to regress.
  2. The regression was detected by a substring guard testing `'18%' in fact_text`. Six index
     facts contain '18%', including [64] vat_withholding_formula_correct — the very fact the
     rewrite touches. The guard could not distinguish [13] from [64].

This re-measures with the faults removed:
  - verbatim eval phrasings, not paraphrases
  - keywords VERIFIED UNIQUE in the index (asserted at runtime, not assumed)
  - ranks reported for the intended fact BY POSITION, so no substring can stand in for it

Nothing is written back to the index.

R18: committed before its result is written up.
Artifact: eval/results/reopen_nat44_nat28.json
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, 'eval', 'results', 'reopen_nat44_nat28.json')
PASSAGE_PREFIX = 'passage: '

# Verbatim from eval/accuracy_gate/edge_probe_natural_048.jsonl.
ROWS = {
    'nat_44': ('nimeuzia wakala wa serikali bidhaa je watanikata asilimia ngapi ya vat', 16),
    'nat_28': ('nimefanya kazi ya ushauri kwa taasisi ya serikali wamesema watakata vat je '
               'asilimia ngapi na cheti nitapata lini', 17),
    'nat_27': ('vat ya asilimia ngapi naiweka kwenye bei ya bidhaa zangu', 13),
}
# Unique-in-index anchors, asserted below rather than trusted.
ANCHORS = {16: 'withholding on goods is 3%', 17: 'withholding on services is 6%',
           13: 'NEVER 14%'}

# Two rewrite variants, measured against each other.
#
# V1 leads with the RATE and the legal framing. V2 applies the topic-alignment finding
# properly: lead with the USER'S OWN VOCABULARY (kuuzia serikali / kazi ya ushauri / cheti),
# not the regulatory label. The targeted-rewrite measurement showed that was the lever that
# moved nat_36 17->1 — and V1's nat_28 result is a direct test of whether it generalises,
# because V1 drops the words nat_28 actually uses ('ushauri', 'cheti').
VARIANTS = {
    'v1_rate_led': {
        16: 'Wakala wa serikali akikununulia bidhaa atakukata VAT withholding ya asilimia 3 '
            '(3%) ya thamani ya bidhaa bila VAT. Hii ni kwa BIDHAA — huduma ni asilimia 6. '
            'Ilianza tarehe 1 Julai 2025 (Finance Act 2025).',
        17: 'Ukifanya kazi ya HUDUMA kwa taasisi ya serikali watakukata VAT withholding ya '
            'asilimia 6 (6%) ya thamani ya huduma bila VAT. Hii ni kwa HUDUMA — bidhaa ni '
            'asilimia 3. Ilianza tarehe 1 Julai 2025 (Finance Act 2025).',
    },
    'v2_ask_led': {
        16: 'Ukiuzia wakala au taasisi ya serikali BIDHAA, watakukata VAT ya asilimia 3 (3%) '
            'ya thamani ya bidhaa bila VAT. Kwa bidhaa ni asilimia 3; kwa huduma ni asilimia '
            '6. Ilianza 1 Julai 2025 (Finance Act 2025).',
        17: 'Ukifanya kazi ya ushauri au huduma nyingine kwa taasisi ya serikali, watakukata '
            'VAT ya asilimia 6 (6%) ya thamani ya huduma bila VAT, na utapewa CHETI cha VAT '
            'withholding. Kwa huduma ni asilimia 6; kwa bidhaa ni asilimia 3. '
            'Ilianza 1 Julai 2025 (Finance Act 2025).',
    },
}


def main():
    import numpy as np
    from sentence_transformers import SentenceTransformer

    emb = np.load(os.path.join(REPO, 'chike-inference', 'rag_embeddings.npy'))
    with open(os.path.join(REPO, 'chike-inference', 'rag_facts_text.json'),
              encoding='utf-8') as f:
        texts = json.load(f)

    # Soundness precondition: every anchor must be unique, or this check has the same
    # fault as the guard it replaces.
    anchor_report = {}
    for pos, anchor in ANCHORS.items():
        hits = [i for i, t in enumerate(texts) if anchor.lower() in t.lower()]
        anchor_report[anchor] = hits
        assert hits == [pos], f'anchor {anchor!r} not unique to [{pos}]: {hits}'

    model = SentenceTransformer('intfloat/multilingual-e5-base')

    def ranks(matrix):
        out = {}
        for row, (q, pos) in ROWS.items():
            v = model.encode([f'query: {q}'])[0]
            v = v / (np.linalg.norm(v) + 1e-10)
            scores = np.dot(matrix, v)
            order = np.argsort(scores)[::-1]
            out[row] = {
                'target_position': pos,
                'rank': int(np.where(order == pos)[0][0]) + 1,
                'score': round(float(scores[pos]), 4),
                'top3': [{'position': int(j), 'text': texts[j][:90]} for j in order[:3]],
            }
            out[row]['in_top3'] = out[row]['rank'] <= 3
        return out

    base = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-10)
    before = ranks(base)

    arms = {}
    for label, rewrites in VARIANTS.items():
        arm_emb = emb.copy()
        for pos, new_text in rewrites.items():
            arm_emb[pos] = model.encode([PASSAGE_PREFIX + new_text])[0]
        arm = arm_emb / (np.linalg.norm(arm_emb, axis=1, keepdims=True) + 1e-10)
        r = ranks(arm)
        arms[label] = {
            'rewrites': {str(k): v for k, v in rewrites.items()},
            'ranks': r,
            'deltas': {row: before[row]['rank'] - r[row]['rank'] for row in ROWS},
        }

    out = {
        'measured': '2026-08-22',
        'harness': 'eval/index_quality/reopen_nat44_nat28.py',
        'note': 'measurement only — nothing written back to the index',
        'anchor_uniqueness_verified': anchor_report,
        'before': before,
        'arms': arms,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print('anchors verified unique:', anchor_report)
    header = f"{'row':8} {'before':>12}"
    for label in arms:
        header += f" | {label:>18}"
    print('\n' + header)
    for r in ROWS:
        line = f"{r:8} rank {before[r]['rank']:>4}   "
        for label, arm in arms.items():
            a = arm['ranks'][r]
            line += (f" | rank {a['rank']:>4} "
                     f"{'TOP3' if a['in_top3'] else '    '} {arm['deltas'][r]:+5}")
        print(line)
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()
