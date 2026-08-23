# -*- coding: utf-8 -*-
"""Re-run the 2026-08-16 coverage measurement against CURRENT state.

WHY THIS EXISTS. The 2026-08-16 readiness assessment rests on one number —
`scratch/coverage_gap_2026_08_16.json`: twelve questions from an ordinary duka owner's month,
**12/12 passed the OOC classifier, 0/12 took a deterministic route, 0/12 had a fact behind
them**. That number is now seven days old and three things have shipped that could move it
(a presumptive-tax engine, a business-licence renewal fact, routing gaps A+B). The pilot
re-derivation must not quote the old figure — R18 instance 4 is exactly the shape of quoting a
number nobody re-derived.

WHAT IT MEASURES, per row, all three columns re-derived from live repo code:

  1. `ooc_classifier`   — chike.classification.classify over config-resolved phrase lists
                          (R14: the same union modal_app.py builds).
  2. `deterministic_route` — chike.decomposition.decompose_query then routing.detect_intent on
                          each part. This is Orchestrator.route's own logic (orchestrator.py:203
                          calls detect_intent and nothing else), so it needs no model, no GPU
                          and no network.
  3. `has_fact`         — LEXICAL, and deliberately so. The real path is an e5 embedding
                          lookup, which cannot run here (local network blocks the e5-base
                          download; page-file exhaustion has already degraded three
                          measurements). So each row carries hand-authored `fact_anchors`: terms
                          that MUST appear in a fact for that fact to be ABOUT the topic. A row
                          is `has_fact` only if some locked_fact value or RAG index row contains
                          one.

  THE BOUND ON COLUMN 3, stated rather than buried: anchors PROVE PRESENCE, never absence of a
  usable answer, and presence in the index is not the same as retrieval reaching it (the
  presence-not-conclusion family, four instances). A row that flips to has_fact=True here has
  gained a fact in the corpus; whether RAG returns it at top-3 is a separate question this
  harness cannot answer. Treated as an UPPER BOUND on coverage throughout.

Artifact: eval/results/coverage_12_rerun.json
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)

from chike import classification, decomposition, routing          # noqa: E402

BASELINE = os.path.join(REPO, 'scratch', 'coverage_gap_2026_08_16.json')
LOCKED = os.path.join(REPO, 'scripts', 'locked_facts.json')
INDEX = os.path.join(REPO, 'chike-inference', 'rag_facts_text.json')
OUT = os.path.join(REPO, 'eval', 'results', 'coverage_12_rerun.json')

# One entry per baseline row, in baseline order. `anchors` are the terms a fact must contain to
# be ABOUT this topic — chosen from the topic's own vocabulary, not from any fact's wording, so
# they cannot be tuned to produce a hit.
ANCHORS = [
    ['makadirio', 'makisio', 'presumptive'],                       # presumptive, 30M turnover
    ['makadirio', 'makisio', 'presumptive'],                       # presumptive, micro band
    ['leseni ya biashara', 'business licence', 'business license'],  # licence FEE
    ['leseni ya biashara', 'business licence', 'business license'],  # licence RENEWAL
    ['ushuru wa huduma', 'service levy', 'halmashauri'],           # LGA service levy
    ['ushuru wa soko', 'genge', 'market stall', 'stall due'],       # market stall
    ['zimamoto', 'fire safety', 'fire certificate'],                # fire safety cert
    ['vipimo', 'mizani', 'weights and measures'],                   # weights and measures
    ['kodi ya pango', 'kodi ya kupanga', 'rent withholding', 'withholding tax on rent'],
    ['tin', 'namba ya mlipakodi'],                                  # TIN registration
    ['ukaguzi', 'audit'],                                           # TRA audit visit
    ['mobile money', 'pesa kwa simu', 'malipo ya simu', 'miamala'],  # mobile-money receipts
]


def corpus_texts():
    """Every string a lexical anchor could match: locked_facts values + the RAG index rows."""
    with open(LOCKED, encoding='utf-8') as f:
        locked = json.load(f)
    with open(INDEX, encoding='utf-8') as f:
        index = json.load(f)
    lf = []
    for key, val in locked.items():
        if key == '_meta':
            continue
        # A fact may be a bare string or a dict with a value/note; flatten either shape.
        lf.append(f'{key}: {json.dumps(val, ensure_ascii=False)}')
    return lf, [str(r) for r in index]


def main():
    with open(BASELINE, encoding='utf-8') as f:
        base = json.load(f)
    rows_in = base['rows']
    assert len(rows_in) == 12, f'baseline has {len(rows_in)} rows, expected 12'
    assert len(ANCHORS) == 12, 'anchor list must be 1:1 with the baseline rows'

    locked_texts, index_texts = corpus_texts()
    locked_l = [t.lower() for t in locked_texts]
    index_l = [t.lower() for t in index_texts]

    ooc_phrases, in_scope_phrases = classification.resolve_phrases(
        classification.load_local_config())

    rows_out = []
    for row, anchors in zip(rows_in, ANCHORS):
        q = row['question']

        in_scope = classification.classify(q, ooc_phrases, in_scope_phrases)

        parts = decomposition.decompose_query(q)
        intents = [routing.detect_intent(p) for p in parts]
        route = next((i for i in intents if i != 'none'), 'none')

        hits_locked = [t for t, tl in zip(locked_texts, locked_l)
                       if any(a in tl for a in anchors)]
        hits_index = [t for t, tl in zip(index_texts, index_l)
                      if any(a in tl for a in anchors)]
        has_fact = bool(hits_locked or hits_index)

        rows_out.append({
            'topic': row['topic'],
            'question': q,
            'baseline': {
                'ooc_classifier': row['ooc_classifier'],
                'deterministic_route': row['deterministic_route'],
                'has_fact': row['has_fact'],
            },
            'now': {
                'ooc_classifier': 'pass_to_model' if in_scope else 'refused',
                'deterministic_route': route,
                'decomposed_parts': parts,
                'part_intents': intents,
                'has_fact_lexical': has_fact,
                'anchors': anchors,
                'locked_fact_hits': hits_locked[:6],
                'index_hits': hits_index[:6],
                'n_locked_hits': len(hits_locked),
                'n_index_hits': len(hits_index),
            },
            'changed': {
                'route': route != row['deterministic_route'],
                'has_fact': has_fact != row['has_fact'],
            },
        })

    summary = {
        'n': len(rows_out),
        'passed_ooc_classifier': sum(1 for r in rows_out
                                     if r['now']['ooc_classifier'] == 'pass_to_model'),
        'took_a_deterministic_route': sum(1 for r in rows_out
                                          if r['now']['deterministic_route'] != 'none'),
        'have_a_fact_behind_them_UPPER_BOUND': sum(1 for r in rows_out
                                                   if r['now']['has_fact_lexical']),
        'baseline_2026_08_16': {
            'passed_ooc_classifier': base['passed_ooc_classifier'],
            'took_a_deterministic_route': base['took_a_deterministic_route'],
            'have_a_fact_behind_them': base['have_a_fact_behind_them'],
            'locked_facts_total': base['locked_facts_total'],
            'rag_index_total': base['rag_index_total'],
        },
        'locked_facts_total': len(locked_texts),
        'rag_index_total': len(index_texts),
    }

    out = {
        'measured': '2026-08-23',
        'harness': 'eval/coverage/rerun_coverage_12.py',
        'baseline_artifact': 'scratch/coverage_gap_2026_08_16.json',
        'method': 'OOC + route re-derived from live repo code (no model, no network). has_fact '
                  'is LEXICAL over hand-authored per-row anchors and is an UPPER BOUND: it '
                  'proves a fact exists in the corpus, NOT that retrieval reaches it.',
        'summary': summary,
        'rows': rows_out,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print('\n--- per row (baseline -> now) ---')
    for r in rows_out:
        flag = '  <-- CHANGED' if (r['changed']['route'] or r['changed']['has_fact']) else ''
        print(f"  {r['topic'][:44]:<46} route {r['baseline']['deterministic_route']:>12} -> "
              f"{r['now']['deterministic_route']:<14} fact {str(r['baseline']['has_fact']):>5} -> "
              f"{str(r['now']['has_fact_lexical']):<5}{flag}")
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()
