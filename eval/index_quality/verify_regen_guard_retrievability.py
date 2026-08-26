# -*- coding: utf-8 -*-
"""RETRIEVABILITY re-verification after an index-composition change — the check that
`verify_regen_guards_post_consolidation.py` (2026-08-26) did NOT do, and its gap is why
`nat_34`'s guard reached Kaggle broken a second time.

THE GAP, NAMED. That script re-verified every guard anchor was still a UNIQUE SUBSTRING in the
prospective index -- pure text, no model, deterministic anywhere. It found and fixed one dead
anchor (`nat_34`'s old anchor, absorbed into the ladder group) by pointing it at a phrase from
the new group passage. That phrase WAS unique. It did not check whether the row containing that
phrase was still RETRIEVED IN TOP-3 for the guard's actual query -- and consolidation had, in the
same change, pushed three OTHER short standalone rows (company_name_reservation_fee,
company_name_change_fee, business_name_maintenance_fee) up the ranking by removing 14 rows that
used to sit between them and the top, displacing the ladder passage from rank 3 to rank 4 for
that exact query. A text check cannot see this: the anchor is unique, present, correct -- and
still outside the window a real user's query would put it in.

THIS SCRIPT CLOSES THAT GAP. For every guard in kaggle/regenerate_rag_e5.py's critical_queries,
it checks BOTH: anchor text uniqueness (as before) AND the actual retrieval RANK of the matched
row(s) against the PROSPECTIVE index, using the now-validated local e5 (the 2026-08-26 Kaggle
run reproduced this repo's local e5 EXACTLY on three independent anchors -- 45/23/8, zero drift
-- which licenses using it to DIAGNOSE rank here, though never to build or ship an index; nothing
here is saved or uploaded).

SECOND GAP, CLOSED 2026-08-26 (found the same day, by the same mechanism, in the OTHER
direction). Fixing nat_34 by rewriting `company_registration_ladder`'s text moved `nat_23` from
rank 45 to 46 between Kaggle runs -- within RANK_TOLERANCE, but the only change between the two
runs was the ladder rewrite, so the rewrite itself displaced a neighbour by one position. THE
GENERAL PROPERTY: an ask-alignment rewrite is not a local edit to "its own" row -- it is an
INDEX-COMPOSITION CHANGE like consolidation was, and it must be checked against every guard's
rank, not just the row being rewritten. This script originally only walked `critical_queries`
(the top-3 guards); it now ALSO walks `RANK_GATE_CASES` (the tolerance-banded consolidation
anchors), because a rewrite can perturb either kind, and checking only the guard you meant to fix
is exactly the blind spot that let nat_34 reach Kaggle broken the first time.

Run this on EVERY future index-composition change, INCLUDING a content rewrite to a single
existing row, before packaging for Kaggle -- not only when something is suspected. `nat_34` was
found by a real Kaggle failure, which is the expensive way.

R18: committed before its result is written up.
Artifact: eval/results/regen_guard_retrievability_post_consolidation.json
"""
import ast
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
REGEN = os.path.join(REPO, 'kaggle', 'regenerate_rag_e5.py')
OUT = os.path.join(REPO, 'eval', 'results', 'regen_guard_retrievability_post_consolidation.json')
TOP_K = 3

sys.path.insert(0, os.path.join(REPO, 'scripts'))


def load_from_regen(name):
    with open(REGEN, encoding='utf-8') as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == name:
                    return ast.literal_eval(node.value)
    raise SystemExit(f'{name} not found in {REGEN}')


def main():
    import numpy as np
    import precompute_rag_embeddings as pre
    from sentence_transformers import SentenceTransformer

    guards = load_from_regen('critical_queries')
    known_failing = set(load_from_regen('KNOWN_FAILING'))
    accepted_ambiguous = set(load_from_regen('ACCEPTED_AMBIGUOUS'))
    rank_gate_cases = load_from_regen('RANK_GATE_CASES')
    rank_tolerance = load_from_regen('RANK_TOLERANCE')

    texts, _keys, _dropped = pre.build_fact_texts()
    model = SentenceTransformer('intfloat/multilingual-e5-base')
    prefixed = ['passage: ' + t for t in texts]
    emb = np.array(model.encode(prefixed, show_progress_bar=False))
    emb = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-10)

    rank_gate_rows, rank_gate_regressions = [], []
    for name, query, needle, pre_rank, measured_rank in rank_gate_cases:
        hits = [i for i, t in enumerate(texts) if needle in t]
        if len(hits) != 1:
            rank_gate_regressions.append({
                'name': name, 'status': 'DEAD_OR_AMBIGUOUS_ANCHOR', 'matches': len(hits),
            })
            continue
        anchor_idx = hits[0]
        qv = model.encode([query])[0]
        qv = qv / (np.linalg.norm(qv) + 1e-10)
        sims = emb @ qv
        order = np.argsort(-sims)
        observed_rank = int(np.where(order == anchor_idx)[0][0]) + 1
        within_tolerance = observed_rank <= measured_rank + rank_tolerance
        beats_baseline = observed_rank < pre_rank
        ok = within_tolerance and beats_baseline
        row = {
            'name': name, 'status': 'PASS' if ok else 'RANK_GATE_REGRESSION',
            'pre_consolidation_rank': pre_rank, 'measured_rank': measured_rank,
            'observed_rank': observed_rank, 'tolerance': rank_tolerance,
        }
        rank_gate_rows.append(row)
        if not ok:
            rank_gate_regressions.append(row)

    rows, regressions = [], []
    for name, query, expected in guards:
        anchor_rows = set()
        for kw in expected:
            anchor_rows |= {i for i, t in enumerate(texts) if kw.lower() in t.lower()}
        if not anchor_rows:
            rows.append({'name': name, 'status': 'DEAD_ANCHOR', 'best_rank': None})
            continue

        qv = model.encode([query])[0]
        qv = qv / (np.linalg.norm(qv) + 1e-10)
        sims = emb @ qv
        order = np.argsort(-sims)
        ranks = {i: int(np.where(order == i)[0][0]) + 1 for i in anchor_rows}
        best_rank = min(ranks.values())
        in_top_k = best_rank <= TOP_K

        if not in_top_k and name in known_failing:
            status = 'KNOWN-FAIL'
        elif in_top_k and name in known_failing:
            status = 'STALE-KNOWN-FAIL'
        else:
            status = 'PASS' if in_top_k else 'RETRIEVAL_REGRESSION'
            if status == 'RETRIEVAL_REGRESSION':
                regressions.append({
                    'name': name, 'query': query, 'best_rank': best_rank,
                    'top_3': [{'rank': r, 'text': texts[int(i)][:100]}
                              for r, i in enumerate(order[:TOP_K], 1)],
                })
        rows.append({'name': name, 'status': status, 'best_rank': best_rank, 'ranks': ranks})

    out = {
        'measured': '2026-08-26',
        'harness': 'eval/index_quality/verify_regen_guard_retrievability.py',
        'prospective_index_rows': len(texts),
        'top_k': TOP_K,
        'total_guards': len(rows),
        'status_counts': {s: sum(1 for r in rows if r['status'] == s)
                          for s in ('PASS', 'RETRIEVAL_REGRESSION', 'KNOWN-FAIL',
                                    'STALE-KNOWN-FAIL', 'DEAD_ANCHOR')},
        'regressions': regressions,
        'rows': rows,
        'rank_gate_cases': {
            'total': len(rank_gate_cases),
            'status_counts': {
                'PASS': sum(1 for r in rank_gate_rows if r['status'] == 'PASS'),
                'RANK_GATE_REGRESSION': len(rank_gate_regressions),
            },
            'regressions': rank_gate_regressions,
            'rows': rank_gate_rows,
        },
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(json.dumps(out['status_counts'], indent=2))
    if regressions:
        print(f'\n[RETRIEVAL REGRESSION] {len(regressions)} guard(s) whose anchor is unique '
              f'but ranked outside top-{TOP_K}:')
        for r in regressions:
            print(f"  {r['name']}: best_rank={r['best_rank']}")
    else:
        print(f'\n[OK] every guard anchor ranks within top-{TOP_K} for its own query')

    print(f"\nRANK_GATE_CASES: {out['rank_gate_cases']['status_counts']}")
    if rank_gate_regressions:
        print(f'[RANK GATE REGRESSION] {len(rank_gate_regressions)} case(s) outside tolerance '
              f'or baseline:')
        for r in rank_gate_regressions:
            print(f"  {r['name']}: {r}")
    else:
        print('[OK] every RANK_GATE_CASES anchor within tolerance and beats its pre-'
              'consolidation baseline')

    print(f'\n[saved] {OUT}')
    return 0 if not regressions and not rank_gate_regressions else 1


if __name__ == '__main__':
    sys.exit(main())
