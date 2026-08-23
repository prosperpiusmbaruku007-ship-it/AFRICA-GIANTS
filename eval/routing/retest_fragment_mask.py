# -*- coding: utf-8 -*-
"""RE-TEST the fragment mask against the target it was never tried on.

WHY RE-TEST SOMETHING ALREADY MEASURED AS FAILING. `scratch/feemask_experiment.json` (2026-08-17)
built a fee-row mask and measured it: **0 of 9 target rows fixed, 3 currently-correct rows
regressed.** It was folded into the C4 rewrite and not shipped, correctly.

But the nine targets were `nat_05`, `nat_23`, `nat_24` and `nat_28` — and three of those have since
been **reclassified as COMPUTE-path rows and closed by ROUTING-GAP-A/B**. A mask that failed on rows
whose real problem turned out to be *routing* has not been tested on a row whose problem is
genuinely fragment displacement. **`eval_342` is that row**: its top-3 was three bare `key: value`
percentage fragments with no PAYE fact anywhere, and the PAYE band fact sat at **rank 51**.

**This is a re-test, not a belief.** The prior negative stands unless this moves it, and the three
regressions remain the standing cost.

FALSIFIERS, NAMED BEFORE RUNNING — any one of these and the mask stays dead:
  F1  eval_342's anchor (`paye all bands sequence`) does not enter the top-3 under the mask.
  F2  the mask makes the expected-answer overlap WORSE on more currently-correct rows than it
      improves on the 54 all-three-slots rows.
  F3  the 54 rows show no net improvement in expected-answer overlap at all.

WHAT IS MEASURED, and the honest name for it. Retrieval is offline and exact; whether a better
top-3 produces a better ANSWER is not measurable without generation. So the benefit proxy here is
**expected-answer term overlap**: how many distinctive content terms of the row's recorded
`correct_answer_sw` appear in its top-3. Higher is better. **It is a PROXY and is labelled as one
everywhere it appears** — 2026-08-17's mask improved retrieval on paper and fixed nothing, which is
exactly the gap between a proxy and an outcome.

R18: committed before its result is written up.
Artifact: eval/results/fragment_mask_retest.json
"""
import json
import os
import re
import sys

os.environ.setdefault('HF_HUB_OFFLINE', '1')
os.environ.setdefault('TRANSFORMERS_OFFLINE', '1')

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, 'eval', 'coverage'))

from measure_coverage_gate_signals import content_tokens, load_corpora     # noqa: E402
from measure_defect_exposure import is_fragment                            # noqa: E402

INDEX_TEXT = os.path.join(REPO, 'chike-inference', 'rag_facts_text.json')
INDEX_EMB = os.path.join(REPO, 'chike-inference', 'rag_embeddings.npy')
EXPOSURE = os.path.join(REPO, 'eval', 'results', 'defect_exposure.json')
ADJ = os.path.join(REPO, 'eval', 'results', 'natural48_rerun_2026_08_17_adjudication.json')
OUT = os.path.join(REPO, 'eval', 'results', 'fragment_mask_retest.json')

TOP_K = 3
EVAL_342_ANCHOR = 'paye all bands sequence'

GATE_FILES = ['eval/accuracy_gate/eval_questions_001.jsonl',
              'eval/accuracy_gate/eval_questions_002_additions.jsonl',
              'eval/accuracy_gate/eval_questions_003.jsonl']


def expected_answers():
    out = {}
    for p in GATE_FILES:
        with open(os.path.join(REPO, p), encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    if r.get('correct_answer_sw'):
                        out[r['id']] = r['correct_answer_sw']
    return out


def overlap(expected, top_texts):
    """Distinctive content terms of the expected answer present in the top-3.

    PROXY, not an outcome. Numbers are kept here (unlike the coverage harness, which drops them)
    because for THIS question the figure IS the answer — an expected answer of "asilimia 30" is
    matched by a fact carrying 30 and by nothing else.
    """
    want = content_tokens(expected) | set(re.findall(r'\d[\d,\.]*', expected))
    have = set()
    for t in top_texts:
        have |= content_tokens(t) | set(re.findall(r'\d[\d,\.]*', t))
    return len(want & have), len(want)


def main():
    import numpy as np
    from sentence_transformers import SentenceTransformer

    with open(INDEX_TEXT, encoding='utf-8') as f:
        texts = json.load(f)
    emb = np.load(INDEX_EMB)
    emb = emb / np.linalg.norm(emb, axis=1, keepdims=True)
    frag = [is_fragment(t) for t in texts]
    keep = np.array([not f for f in frag])

    anchor_hits = [i for i, t in enumerate(texts) if EVAL_342_ANCHOR in t]
    assert len(anchor_hits) == 1, f'anchor matched {len(anchor_hits)} rows, need exactly 1'
    anchor = anchor_hits[0]

    with open(EXPOSURE, encoding='utf-8') as f:
        exposure = json.load(f)
    all3 = [r for r in exposure['rows'] if r['n_fragment_in_top3'] == 3]
    assert all3, 'no all-three-slots rows found — the exposure artifact is stale'

    with open(ADJ, encoding='utf-8') as f:
        adj = json.load(f)
    correct_nat = {r['id'] for r in adj['rows'] if r['now'].startswith('CORRECT')}

    exp = expected_answers()
    model = SentenceTransformer('intfloat/multilingual-e5-base')

    # Populations: (a) the all-three-slots rows — where the mask should help;
    #              (b) currently-CORRECT rows — where it must not hurt. R22: measure the remedy on
    #              the population that needs it AND on the one that would pay for it.
    corpora = load_corpora()
    by_id = {r['id']: (name, r) for name, rows in corpora.items() for r in rows}
    target_ids = [r['id'] for r in all3]
    cost_ids = sorted(correct_nat | {i for i in exp if i in by_id} - set(target_ids))
    # Keep the cost arm bounded and deterministic: the natural-48 correct set plus the first 150
    # gate rows with an expected answer, minus anything already in the target arm.
    cost_ids = [i for i in cost_ids if i in by_id][:180]

    def evaluate(ids):
        qs = [by_id[i][1]['q'] for i in ids]
        qv = model.encode([f'query: {q}' for q in qs], batch_size=16,
                          normalize_embeddings=True, show_progress_bar=False)
        sims = qv @ emb.T
        rows = []
        for n, rid in enumerate(ids):
            base = [int(j) for j in np.argsort(-sims[n])[:TOP_K]]
            masked_scores = np.where(keep, sims[n], -np.inf)
            masked = [int(j) for j in np.argsort(-masked_scores)[:TOP_K]]
            rec = {'id': rid, 'corpus': by_id[rid][0], 'question': by_id[rid][1]['q'],
                   'top3_base': base, 'top3_masked': masked, 'changed': base != masked}
            if rid in exp:
                b_hit, want = overlap(exp[rid], [texts[j] for j in base])
                m_hit, _ = overlap(exp[rid], [texts[j] for j in masked])
                rec.update({'expected_terms': want, 'overlap_base': b_hit,
                            'overlap_masked': m_hit, 'delta': m_hit - b_hit})
            rows.append(rec)
        return rows

    target_rows = evaluate(target_ids)
    cost_rows = evaluate(cost_ids)

    def tally(rows):
        scored = [r for r in rows if 'delta' in r]
        return {'n': len(rows), 'scored': len(scored),
                'improved': sum(1 for r in scored if r['delta'] > 0),
                'worsened': sum(1 for r in scored if r['delta'] < 0),
                'unchanged': sum(1 for r in scored if r['delta'] == 0),
                'net_terms': sum(r['delta'] for r in scored)}

    # F1 — eval_342 specifically.
    q342 = by_id['eval_342'][1]['q'] if 'eval_342' in by_id else None
    assert q342, 'eval_342 not present in the corpora'
    v = model.encode([f'query: {q342}'], normalize_embeddings=True)[0]
    s = v @ emb.T
    base_order = list(np.argsort(-s))
    masked_order = list(np.argsort(-np.where(keep, s, -np.inf)))
    f1 = {'anchor_index': anchor,
          'rank_base': base_order.index(anchor) + 1,
          'rank_masked': masked_order.index(anchor) + 1,
          'in_top3_base': anchor in [int(j) for j in base_order[:TOP_K]],
          'in_top3_masked': anchor in [int(j) for j in masked_order[:TOP_K]],
          'top3_masked_text': [texts[int(j)][:120] for j in masked_order[:TOP_K]]}

    t_tally, c_tally = tally(target_rows), tally(cost_rows)
    verdict = {
        'F1_eval342_anchor_reaches_top3': f1['in_top3_masked'],
        'F2_hurts_more_than_it_helps': c_tally['worsened'] > t_tally['improved'],
        'F3_no_net_improvement_on_targets': t_tally['net_terms'] <= 0,
    }
    verdict['mask_survives'] = (verdict['F1_eval342_anchor_reaches_top3']
                                and not verdict['F2_hurts_more_than_it_helps']
                                and not verdict['F3_no_net_improvement_on_targets'])

    out = {
        'measured': '2026-08-23',
        'harness': 'eval/routing/retest_fragment_mask.py',
        'prior': 'scratch/feemask_experiment.json (2026-08-17) — 0/9 fixed, 3 regressed. Its '
                 'targets were nat_05/23/24 (since reclassified COMPUTE and closed by '
                 'ROUTING-GAP-A/B) plus nat_28.',
        'benefit_measure': 'expected-answer term overlap in the top-3. A PROXY, not an outcome: '
                           'the 2026-08-17 mask improved retrieval on paper and fixed nothing.',
        'fragment_rows': int(sum(frag)), 'index_rows': len(texts),
        'F1_eval_342': f1,
        'target_arm_all_three_slots': t_tally,
        'cost_arm_currently_correct': c_tally,
        'falsifiers': verdict,
        'target_rows': target_rows,
        'cost_rows': cost_rows,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"F1  eval_342 anchor rank {f1['rank_base']} -> {f1['rank_masked']}   "
          f"in top3 after mask: {f1['in_top3_masked']}")
    for t in f1['top3_masked_text']:
        print(f"      masked top3: {t}")
    print(f"\nTARGET arm (all-3-slots)      {t_tally}")
    print(f"COST   arm (currently correct) {c_tally}")
    print(f"\nfalsifiers: {json.dumps(verdict, indent=2)}")
    print(f"\n[saved] {OUT}")


if __name__ == '__main__':
    main()
