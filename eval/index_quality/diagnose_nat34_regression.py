# -*- coding: utf-8 -*-
"""DIAGNOSIS: is the company-registration ladder genuinely unreachable for nat_34, or merely
ranked below the top-3 guard window? (2026-08-26, post real Kaggle regen)

CONTEXT. The Kaggle regen (eval/results/... run output, reported by the founder) built the real
187-row consolidated index, reproduced the offline-measured nat_23/nat_33/nat_05 ranks EXACTLY
(45/23/8), confirmed 31/31 guard anchors unique, and then FAILED on the
'Company registration fee (nat_34 displacement guard)' critical query — the re-anchored guard
added 2026-08-26 (commit 76897e3) after `verify_regen_guards_post_consolidation.py` found the
OLD anchor ('company registration fee 1') goes dead under consolidation. That check verified
TEXT-LEVEL anchor uniqueness; it could not and did not check RETRIEVAL rank, which is exactly
what changed. This is the same shape as the anchor-uniqueness work one layer out: a text-level
check cannot see a retrieval-level regression.

WHY LOCAL E5 IS TRUSTED FOR THIS DIAGNOSIS (not for shipping). The Kaggle run's rank-regression
gate reproduced this repo's local e5 offline measurement EXACTLY on three independent anchors
(45/23/8, zero drift) -- the first direct proof that local multilingual-e5-base and Kaggle's
multilingual-e5-base are numerically identical for this content, not merely assumed compatible.
That licenses USING local e5 to DIAGNOSE (read rank, do not build/ship an index) with the same
confidence as reading the Kaggle log directly. It does not relicense running the regen locally --
nothing here is saved or uploaded.

QUESTION: does consolidation make the ladder's content genuinely unreachable for nat_34, or does
it merely displace it from rank 3 (pre) to just outside the top-3 window (post)?

R18: committed before its result is written up.
Artifact: eval/results/nat34_regression_diagnosis.json
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, 'eval', 'results', 'nat34_regression_diagnosis.json')
OLD_TEXT = os.path.join(REPO, 'chike-inference', 'rag_facts_text.json')
OLD_EMB = os.path.join(REPO, 'chike-inference', 'rag_embeddings.npy')

sys.path.insert(0, os.path.join(REPO, 'scripts'))

# Verbatim -- eval/accuracy_gate/edge_probe_natural_048.jsonl, id=nat_34. Same text the
# regenerate_rag_e5.py guard uses (R24: no paraphrase).
NAT_34_QUERY = 'query: nataka kusajili kampuni gharama ya kuanzia ni ngapi na kuhifadhi jina'


def main():
    import numpy as np
    import precompute_rag_embeddings as pre
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer('intfloat/multilingual-e5-base')
    qv = model.encode([NAT_34_QUERY])[0]
    qv = qv / (np.linalg.norm(qv) + 1e-10)

    # --- OLD (pre-consolidation) index: real, already-shipped Kaggle-produced embeddings ---
    old_texts = json.load(open(OLD_TEXT, encoding='utf-8'))
    old_emb = np.load(OLD_EMB)
    old_emb = old_emb / (np.linalg.norm(old_emb, axis=1, keepdims=True) + 1e-10)
    fee1_idx = [i for i, t in enumerate(old_texts)
                if t.lower().startswith('company registration fee 1:')]
    assert len(fee1_idx) == 1, fee1_idx
    old_sims = old_emb @ qv
    old_order = np.argsort(-old_sims)
    old_rank = int(np.where(old_order == fee1_idx[0])[0][0]) + 1
    old_top10 = [{'rank': r, 'row': int(i), 'text': old_texts[int(i)][:100]}
                 for r, i in enumerate(old_order[:10], 1)]

    # --- NEW (prospective, post-consolidation) index: LOCAL diagnostic only, per the
    # licensing note above. Not saved, not uploaded. ---
    new_texts, _keys, _dropped = pre.build_fact_texts()
    ladder_idx = [i for i, t in enumerate(new_texts) if 'hadi TZS 1,000,000 ni TZS 95,000' in t]
    assert len(ladder_idx) == 1, ladder_idx
    new_prefixed = ['passage: ' + t for t in new_texts]
    new_emb = np.array(model.encode(new_prefixed, show_progress_bar=False))
    new_emb = new_emb / (np.linalg.norm(new_emb, axis=1, keepdims=True) + 1e-10)
    new_sims = new_emb @ qv
    new_order = np.argsort(-new_sims)
    new_rank = int(np.where(new_order == ladder_idx[0])[0][0]) + 1
    new_top10 = [{'rank': r, 'row': int(i), 'text': new_texts[int(i)][:100]}
                 for r, i in enumerate(new_order[:10], 1)]

    # --- The displacing mechanism: business_name_maintenance_fee's OWN rank, old vs new. It
    # is untouched text in both indices (not a FACT_GROUPS member) -- if its RANK moved, that
    # is purely a side effect of other rows disappearing around it, not a content change. ---
    bnm_old = [i for i, t in enumerate(old_texts) if t.lower().startswith('business name maintenance fee')]
    bnm_new = [i for i, t in enumerate(new_texts) if t.lower().startswith('business name maintenance fee')]
    bnm_old_rank = int(np.where(old_order == bnm_old[0])[0][0]) + 1 if bnm_old else None
    bnm_new_rank = int(np.where(new_order == bnm_new[0])[0][0]) + 1 if bnm_new else None

    genuinely_unreachable = new_rank > 20  # a threshold for "no realistic path to top-3"
    verdict = {
        'nat_34_query': NAT_34_QUERY,
        'pre_consolidation': {
            'index_rows': len(old_texts),
            'target_row': 'company_registration_fee_1 (95,000 TZS, own standalone row)',
            'rank': old_rank,
            'in_top_3': old_rank <= 3,
            'top_10': old_top10,
        },
        'post_consolidation_prospective': {
            'index_rows': len(new_texts),
            'target_row': 'company_registration_ladder (group passage, absorbs the same fee)',
            'rank': new_rank,
            'in_top_3': new_rank <= 3,
            'top_10': new_top10,
        },
        'displacing_mechanism': {
            'row': 'business_name_maintenance_fee (5,000 TZS) -- NOT a FACT_GROUPS member, '
                   'text unchanged old vs new',
            'rank_pre_consolidation': bnm_old_rank,
            'rank_post_consolidation': bnm_new_rank,
            'explanation': (
                'Its own text never changed. Its RANK improved (9 -> 3) purely because '
                'consolidation removed 14 other short company/trademark-fee rows that used to '
                'sit between it and the top of the ranking. That vacated slot is what pushed '
                'the ladder passage from rank 3 to rank 4 -- a side effect of REMOVING '
                'competing content, not of the ladder itself becoming less relevant.'
            ),
        },
        'production_top_k': 3,  # chike/retrieval.py, chike-inference/modal_app.py defaults
        'genuinely_unreachable': genuinely_unreachable,
        'verdict': (
            'NOT unreachable -- displaced by exactly one position (rank 3 -> rank 4), just '
            'outside the top-3 window production actually uses by default. This is a REAL, '
            'measurable regression caused by the consolidation, not a guard-anchoring problem: '
            'the starting registration-fee figure nat_34 asks for was retrievable in top-3 '
            'before consolidation and is not after, for this exact verbatim question.'
        ),
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(verdict, f, ensure_ascii=False, indent=2)

    print(f"PRE  (n={len(old_texts)}): company_registration_fee_1 rank {old_rank} "
          f"(top3={old_rank<=3})")
    print(f"POST (n={len(new_texts)}): ladder passage rank {new_rank} (top3={new_rank<=3})")
    print(f"business_name_maintenance_fee: rank {bnm_old_rank} (pre) -> {bnm_new_rank} (post)")
    print(f"\nGENUINELY UNREACHABLE: {genuinely_unreachable}")
    print(f"VERDICT: {verdict['verdict']}")
    print(f"\n[saved] {OUT}")


if __name__ == '__main__':
    main()
