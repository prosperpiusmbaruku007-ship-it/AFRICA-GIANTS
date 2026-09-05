# -*- coding: utf-8 -*-
"""
Did the verification arc (2026-08-28 -> 2026-09-05, 100/251 -> 234/250 grounded locked
facts) change what a user's question actually retrieves? The 48's own accuracy number
cannot answer this -- PROGRESS.md's 2026-09-04 pilot re-derivation found 3 of 4 rows that
moved that cycle were retrieval-rank noise, not the fact corrections credited at first.
This is the noise-immune instrument built for exactly this question
(eval/grounding/measure_fact_reach.py) applied to its actual purpose: PRE-arc index vs.
POST-arc (shipped, live) index, same probes, same retrieval mechanics.

METHOD. Two indices, same probe fixture, same production-exact retrieval:
  PRE  -- built from commit 3cd3924 (2026-08-26 21:04, the last commit touching
          precompute_rag_embeddings.py/locked_facts.json BEFORE the arc's first commit,
          audit_locked_facts_verification_provenance_v2.py, 2026-08-28), embedded locally
          right now with the SAME cached e5-base production uses. 187 facts.
  POST -- the ACTUAL shipped chike-inference/ index (rag_embeddings.npy /
          rag_facts_text.json), what production loads today, not a recomputed stand-in.
          183 facts.
Probes: measure_fact_reach.py's own 36 (34 critical_queries + 2 boundary additions),
reused as-is via its load_probes(), not re-authored here.

⛔ THE CAVEAT THAT DECIDES HOW TO READ THIS, stated before the numbers, not after. Most of
these 36 probes exist BECAUSE the arc (or the sessions immediately alongside it) found and
fixed the exact fact they check -- efd_not_every_business, vat_standard_rate, the local-levy
facts, the fee consolidation. A probe fixture built substantially FROM the intervention
being measured will show that intervention working almost by construction (R22: measuring
the population that already got attention, not the population that needs it). This
instrument is not blind to its own subject. Two things partially offset this, not remove
it: (a) the fixture also contains probes for facts the arc did NOT touch (SDL rate, NSSF
employer, GN487A dates/penalties, corporate tax, council levies) -- if the PRE index already
retrieves these fine, that is neutral evidence, not manufactured credit; (b) the 2 boundary
probes (nat_28/nat_44) were added to THIS measure independently, for a different reason
(populating an empty category), not to flatter the arc, and were previously used by the
pilot re-derivation to find the arc's headline claim WRONG -- if anything they are more
likely to show a null or negative result than a manufactured positive one.

R18: committed before its result is written up.
Artifact: eval/results/arc_effect_pre_vs_post.json
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)

from eval.grounding.measure_fact_reach import (  # noqa: E402
    Retriever,
    _categorize,
    load_deployed_index,
    load_probes,
)

PRE_ARC_COMMIT = '3cd3924'
PRE_ARC_SNAPSHOT_DIR = os.path.join(REPO, 'scratch', 'pre_arc_snapshot')
POST_INDEX_DIR = os.path.join(REPO, 'chike-inference')
OUT = os.path.join(REPO, 'eval', 'results', 'arc_effect_pre_vs_post.json')


def build_pre_arc_index(model):
    """Checks out PRE_ARC_COMMIT's own locked_facts.json + precompute_rag_embeddings.py
    into scratch/pre_arc_snapshot/scripts/ (git show, not a working-tree checkout -- never
    touches the actual repo state) and runs THAT commit's own build_fact_texts(), so the
    facts are rendered exactly as that commit's own code would have rendered them, not
    reinterpreted through today's precompute logic."""
    import subprocess
    snap_scripts = os.path.join(PRE_ARC_SNAPSHOT_DIR, 'scripts')
    os.makedirs(snap_scripts, exist_ok=True)
    for name in ('locked_facts.json', 'precompute_rag_embeddings.py'):
        content = subprocess.run(
            ['git', 'show', f'{PRE_ARC_COMMIT}:scripts/{name}'],
            cwd=REPO, capture_output=True, text=True, encoding='utf-8', check=True,
        ).stdout
        with open(os.path.join(snap_scripts, name), 'w', encoding='utf-8') as f:
            f.write(content)

    sys.path.insert(0, snap_scripts)
    import importlib
    if 'precompute_rag_embeddings' in sys.modules:
        del sys.modules['precompute_rag_embeddings']
    pre_precompute = importlib.import_module('precompute_rag_embeddings')

    cwd = os.getcwd()
    os.chdir(PRE_ARC_SNAPSHOT_DIR)  # FACTS_PATH in the old script is 'scripts/locked_facts.json', CWD-relative
    try:
        texts, keys, dropped = pre_precompute.build_fact_texts()
    finally:
        os.chdir(cwd)
        sys.path.remove(snap_scripts)
        del sys.modules['precompute_rag_embeddings']

    import numpy as np
    prefixed = ['passage: ' + t for t in texts]
    emb = np.array(model.encode(prefixed, show_progress_bar=False))
    norm = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-10)
    return norm, texts, len(dropped)


def measure(retriever, probes):
    rows = []
    for name, question, expected in probes:
        needles = expected if isinstance(expected, (list, tuple)) else [expected]
        primary = needles[0]
        rank = retriever.rank_of(question, primary)
        reaches = any(retriever.reaches_pooled_context(question, n) for n in needles)
        rows.append({'name': name, 'raw_rank': rank, 'category': _categorize(rank),
                     'reaches_context': reaches})
    return rows


def main():
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('intfloat/multilingual-e5-base')

    probes = load_probes()
    print(f'[probes] {len(probes)} (measure_fact_reach.py\'s own fixture, reused as-is)')

    print(f'[pre]  building index from {PRE_ARC_COMMIT} (last commit before the arc)...')
    norm_pre, texts_pre, dropped_pre = build_pre_arc_index(model)
    print(f'[pre]  {len(texts_pre)} facts ({dropped_pre} dropped)')

    print(f'[post] loading ACTUAL shipped index from {POST_INDEX_DIR}...')
    norm_post, texts_post = load_deployed_index(POST_INDEX_DIR)
    print(f'[post] {len(texts_post)} facts (what production loads today)')

    r_pre = Retriever(model, norm_pre, texts_pre)
    r_post = Retriever(model, norm_post, texts_post)
    rows_pre = measure(r_pre, probes)
    rows_post = measure(r_post, probes)

    by_name_pre = {r['name']: r for r in rows_pre}
    deltas = []
    for post in rows_post:
        pre = by_name_pre[post['name']]
        rank_delta = (None if not (pre['raw_rank'] and post['raw_rank'])
                      else post['raw_rank'] - pre['raw_rank'])
        deltas.append({
            'name': post['name'],
            'pre_rank': pre['raw_rank'], 'post_rank': post['raw_rank'],
            'rank_delta': rank_delta,
            'pre_category': pre['category'], 'post_category': post['category'],
            'pre_reaches_context': pre['reaches_context'],
            'post_reaches_context': post['reaches_context'],
            'context_reach_changed': pre['reaches_context'] != post['reaches_context'],
        })

    improved = [d for d in deltas if not d['pre_reaches_context'] and d['post_reaches_context']]
    regressed = [d for d in deltas if d['pre_reaches_context'] and not d['post_reaches_context']]
    unchanged_reaching = [d for d in deltas
                           if d['pre_reaches_context'] and d['post_reaches_context']]
    unchanged_not_reaching = [d for d in deltas
                              if not d['pre_reaches_context'] and not d['post_reaches_context']]

    out = {
        'measured': '2026-09-05',
        'pre_arc_commit': PRE_ARC_COMMIT,
        'pre_arc_commit_date': '2026-08-26 21:04:08 +0300',
        'pre_fact_count': len(texts_pre), 'post_fact_count': len(texts_post),
        'probe_count': len(probes),
        'survivorship_caveat': (
            'most probes were authored because of facts the arc (or sessions alongside it) '
            'fixed -- see module docstring. Read this as "did the arc\'s own targets get '
            'fixed", not as an unbiased corpus-wide estimate.'),
        'summary': {
            'improved (ABSENT/DEEP/BOUNDARY -> reaching context)': len(improved),
            'regressed (was reaching, now not)': len(regressed),
            'unchanged, already reaching both times': len(unchanged_reaching),
            'unchanged, still not reaching either time': len(unchanged_not_reaching),
        },
        'improved_names': [d['name'] for d in improved],
        'regressed_names': [d['name'] for d in regressed],
        'still_not_reaching_names': [d['name'] for d in unchanged_not_reaching],
        'deltas': deltas,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"\nIMPROVED: {len(improved)} -- {out['improved_names']}")
    print(f"REGRESSED: {len(regressed)} -- {out['regressed_names']}")
    print(f"unchanged, already reaching: {len(unchanged_reaching)}")
    print(f"unchanged, STILL not reaching: {len(unchanged_not_reaching)} -- "
          f"{out['still_not_reaching_names']}")
    print(f'[saved] {OUT}')


if __name__ == '__main__':
    main()
