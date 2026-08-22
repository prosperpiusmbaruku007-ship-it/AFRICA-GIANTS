# -*- coding: utf-8 -*-
"""Dry-run the regen guard block locally, before it ever runs on Kaggle.

regenerate_rag_e5.py cannot run here (HF/Kaggle side effects), so this replicates its guard
evaluation exactly — same anchors, same top-3, same KNOWN_FAILING semantics — against the
committed index. It answers, without a Kaggle cycle:

  * is every anchor unique in the index (the precondition the new block asserts)?
  * which guards PASS / FAIL / KNOWN-FAIL under verbatim phrasing?
  * would the regen be blocked, and if so by what?

Reads the guard list and KNOWN_FAILING out of kaggle/regenerate_rag_e5.py by AST parse — no
import, no execution, no network, no modification.

R18: committed before its result is written up.
Artifact: eval/results/regen_guards_local_dryrun.json
"""
import ast
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
REGEN = os.path.join(REPO, 'kaggle', 'regenerate_rag_e5.py')
OUT = os.path.join(REPO, 'eval', 'results', 'regen_guards_local_dryrun.json')


def load(name):
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
    from sentence_transformers import SentenceTransformer

    guards = load('critical_queries')
    known_failing = set(load('KNOWN_FAILING'))
    accepted_ambiguous = set(load('ACCEPTED_AMBIGUOUS'))

    with open(os.path.join(REPO, 'chike-inference', 'rag_facts_text.json'),
              encoding='utf-8') as f:
        texts = json.load(f)
    emb = np.load(os.path.join(REPO, 'chike-inference', 'rag_embeddings.npy'))
    normalized = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-10)
    model = SentenceTransformer('intfloat/multilingual-e5-base')

    rows, seen, blocked_by = [], set(), []
    for name, query, expected in guards:
        anchors = {}
        for kw in expected:
            hits = [i for i, t in enumerate(texts) if kw.lower() in t.lower()]
            anchors[kw] = hits

        q = model.encode([query])[0]
        q = q / (np.linalg.norm(q) + 1e-10)
        scores = np.dot(normalized, q)
        top3 = [int(j) for j in np.argsort(scores)[-3:][::-1]]
        satisfied = [j for j in top3
                     if any(kw.lower() in texts[j].lower() for kw in expected)]
        found = bool(satisfied)

        if not found and name in known_failing:
            status = 'KNOWN-FAIL'
            seen.add(name)
        elif found and name in known_failing:
            status = 'STALE-KNOWN-FAIL'
            seen.add(name)
            blocked_by.append(name)
        else:
            status = 'PASS' if found else 'FAIL'
            if not found:
                blocked_by.append(name)

        rows.append({
            'name': name, 'status': status, 'query': query, 'expected': expected,
            'anchor_hits': {k: v for k, v in anchors.items()},
            'anchor_unique': all(len(v) == 1 for v in anchors.values()),
            'dead_anchors': [k for k, v in anchors.items() if not v],
            'accepted_ambiguous': name in accepted_ambiguous,
            'top3': [{'position': j, 'text': texts[j][:88]} for j in top3],
            'satisfied_by': satisfied,
        })

    orphans = sorted(known_failing - seen)
    if orphans:
        blocked_by.append(f'ORPHAN:{orphans}')

    ambiguous = [r['name'] for r in rows
                 if not r['anchor_unique'] and not r['accepted_ambiguous']]
    dead = [(r['name'], r['dead_anchors']) for r in rows if r['dead_anchors']]
    out = {
        'measured': '2026-08-22',
        'harness': 'eval/index_quality/verify_regen_guards_local.py',
        'source': 'kaggle/regenerate_rag_e5.py (AST parse, read-only)',
        'total_guards': len(rows),
        'status_counts': {s: sum(1 for r in rows if r['status'] == s)
                          for s in ('PASS', 'FAIL', 'KNOWN-FAIL', 'STALE-KNOWN-FAIL')},
        'known_failing': sorted(known_failing),
        'orphan_known_failing': orphans,
        'guards_with_ambiguous_anchors': ambiguous,
        'ambiguous_count': len(ambiguous),
        'accepted_ambiguous': sorted(accepted_ambiguous),
        'guards_with_dead_anchors': dead,
        'regen_would_block': bool(blocked_by),
        'blocked_by': blocked_by,
        'rows': rows,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(json.dumps(out['status_counts'], indent=2))
    print(f"ambiguous anchors (excl. accepted): {len(ambiguous)}/{len(rows)} {ambiguous}")
    print(f"accepted-benign ambiguity: {sorted(accepted_ambiguous)}")
    print(f"dead anchors: {dead}")
    print(f"orphan KNOWN_FAILING: {orphans}")
    print(f"REGEN WOULD BLOCK: {out['regen_would_block']} {blocked_by}")
    print('\n--- the five migrated displacement guards ---')
    for r in rows:
        if 'displacement guard' in r['name'] or 'nat_43' in r['name']:
            print(f"  [{r['status']:16}] {r['name'][:56]:56} unique={r['anchor_unique']}")
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()
