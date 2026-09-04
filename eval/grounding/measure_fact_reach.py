# -*- coding: utf-8 -*-
"""
Does the fact a question's correct answer depends on actually reach the pooled context
production sends to the model? This is the retrieval-only half of "was the verification
arc worth anything" -- a question the 48's own accuracy number PROVABLY cannot answer,
because its accuracy movement is entangled with model-weight noise and retrieval-rank
noise at once. See PROGRESS.md's 2026-09-04 pilot re-derivation: three of the four rows
that moved that cycle were traced to retrieval instability between regens, not the fact
corrections that were credited when the movement was first reported -- the correction was
real, but it was not what moved those three rows.

WHAT THIS MEASURES, PER PROBE. Reproduces production's actual retrieval chain exactly --
chike.decomposition.decompose_query, then the same per-sub-question top_k=3 retrieval and
dedupe-preserve-order-cap-9 pooling as Orchestrator._pool_facts (chike/orchestrator.py:
680-690; confirmed live -- chike-inference/modal_app.py:483-488 wires
`retriever=self.retrieve_facts`, explicitly NOT chike.retrieval's two-arm hybrid, which
R26 already found production does not call) -- against a target fact's own row(s),
identified by a NEEDLE (a substring unique to that fact's CURRENT text), never by row
position or index. No model generation, no adjudication: a fact either lands in the
pooled context or it doesn't. This removes BOTH sources of noise in the 48's number --
model-weight variance and human-adjudication variance -- leaving only the retrieval-layer
question.

FIXTURE: THE PROBES ARE A FLOOR, NOT A CENSUS. Reuses kaggle/regenerate_rag_e5.py's own
34 `critical_queries` tuples (name, verbatim question, expected needle(s)) rather than
building a new fixture, for three reasons:
  1. They are already verbatim real-phrasing questions (R24's rule), not paraphrases.
  2. Their needles are already forced fresh on EVERY regen by that file's own anchor-
     uniqueness gate -- a needle that goes dead or ambiguous blocks the regen outright.
     This fixture therefore stays current as a side effect of a process that already
     runs on every ship, not a new maintenance burden layered on top.
  3. One fixture instead of two drifting in parallel.
Extracted by AST from the source file (ast.literal_eval on the `critical_queries`
assignment), NOT by importing that module -- importing it triggers Kaggle auth, network
fetches, and an EXPECTED_HEAD ancestry check as side effects at import time, none of which
this measure needs or wants.

⛔ THE CAVEAT THAT MATTERS, stated here because it is easy to lose once a number exists:
these 34 probes are hand-picked regression guards, written by people fixing retrieval
problems they had already found. They are a SURVIVORSHIP-BIASED population, skewed toward
facts that already got attention. This script is a floor fixture -- "did we regress
something we already know matters" -- and is NEVER a claim about how the whole corpus
retrieves. See coverage_12_rerun.json for the actual corpus-wide coverage picture (roughly
1 in 4 real-world questions has a fact behind it at all), a completely different question
from the one this script answers.

CATEGORIES, PER PROBE -- rank reported, not just a hit/miss bit, because a binary rate
hides exactly the boundary drift this measure exists to catch:
  IN_TOP3   rank 1-3    reaches context on a single, undecomposed retrieval call
  BOUNDARY  rank 4-16   the historically volatile band -- nat_28/nat_44 (vat_withholding_
                        services/goods) were reported at "7th-16th" across this project's
                        own regen history (PROGRESS.md, 2026-09-04) -- WATCHED as its own
                        category below, never folded into a single pass/fail rate
  DEEP      rank > 16   essentially unreachable today
  ABSENT    needle not found anywhere in the index -- the fact was dropped, renamed, or
                        its needle has gone stale (see this session's PINNED-drift finding:
                        efd_not_every_business's old "Si lazima" needle no longer matches
                        its own corrected text)
`reaches_context` (the pooled-context hit, matching Orchestrator._pool_facts exactly) is
reported SEPARATELY from the `raw_rank` category, since a multi-part question can pool a
fact ranked outside its own top-3 in via a DIFFERENT sub-question's retrieval.

EXTRA PROBES, 2 OF THEM, ADDED FOR A SPECIFIC AND DISCLOSED REASON. The 34 critical_queries
guards, run as-is, produce ZERO probes in the BOUNDARY category on today's index -- every
one of the 34 is either solidly IN_TOP3 or one of the four known ABSENT gaps this session
staged fixes for. That makes BOUNDARY a category that exists in the code but can never be
exercised by this fixture -- the same "vacuous check" shape R20 already warns against, just
arrived at by fixture composition instead of a bad assert. So two more probes are added
below (EXTRA_BOUNDARY_PROBES), sourced the same way critical_queries itself was built --
verbatim questions from an already-committed fixture (eval/accuracy_gate/
edge_probe_natural_048.jsonl's nat_28/nat_44, `intent_expected: "fact"`), needles verified
unique in the deployed index before use -- not hand-invented. These are the two facts
(vat_withholding_services/goods) this project's own history already reports at "7th-16th"
across past regens. Without them the BOUNDARY category would report clean by construction,
which is a worse failure than reporting nothing: a clean BOUNDARY count from a fixture that
cannot ever populate it would read as "the boundary is fine" when it has never been asked.

STABILITY, MEASURED NOT ASSUMED (2026-09-05, --compare-prospective mode, real run --
eval/results/grounded_fact_reach_baseline.json / _prospective_compare.json). Against the
36-probe fixture (34 + the 2 boundary additions): 28 of 28 probes already IN_TOP3 on the
currently-deployed index moved rank 0 against the prospective post-latest-edit build (183
rows, 29 dropped as noise in the same regen) -- e5-base is fully cached locally, so both
arms ran with no network. The four probes targeting this session's actual fixes flipped
ABSENT -> IN_TOP3 (ranks 1, 1, 1, 2) cleanly, in the intended direction, nothing else moved
category. Contrast, and the reason this measure is worth having: over the same period, the
48's OWN accuracy number moved on 4 rows from retrieval-rank noise alone, with the
underlying fact TEXT unchanged for 3 of them (PROGRESS.md, 2026-09-04 pilot re-derivation)
-- this measure isolates exactly the layer that moved there, with nothing else attached.

HONEST LIMIT ON THE BOUNDARY RESULT SPECIFICALLY, stated rather than buried: this is ONE
before/after hop, on 2 boundary probes -- nat_28 (rank 10 -> 10, zero movement) and nat_44
(rank 7 -> 6, one-rank movement, inside this project's own ±5 RANK_GATE_CASES tolerance
for float/BLAS-order noise). The "7th-16th" historical range for nat_28/nat_44 was observed
ACROSS SEVERAL past regens (consolidation passes, batch drops), a 9-rank spread wider than
either number above -- meaning that volatility likely accumulates over MULTIPLE regen
cycles rather than showing up in any single hop, which is exactly what this one hop cannot
see. Re-read eval/results/grounded_fact_reach_prospective_compare.json directly next time
this runs rather than trusting this paragraph's numbers, which are already history by the
time they are read again. n=2 is not enough to call the boundary category stable OR
unstable; it is enough to confirm the category can populate with real facts and real
movement, which is the minimum bar for it to mean anything as a watchlist.
Track the BOUNDARY-category names across the next several regens (diff successive --out
artifacts) before trusting an aggregate rate over this fixture -- a single measurement
answers "is it stable now"; only repeated ones answer "is it stable," exactly the lesson
the 48's own accuracy number turned out to need.

R18: committed before its result is written up.
Baseline artifact: eval/results/grounded_fact_reach_baseline.json
Prospective-compare artifact: eval/results/grounded_fact_reach_prospective_compare.json
"""
import argparse
import ast
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, 'scripts'))

REGEN_SCRIPT = os.path.join(REPO, 'kaggle', 'regenerate_rag_e5.py')
DEFAULT_INDEX_DIR = os.path.join(REPO, 'chike-inference')

TOP_K = 3
POOL_CAP = 9
BOUNDARY_MAX = 16  # matches this project's own "7th-16th" characterization of nat_28/nat_44

# Added 2026-09-05 -- see module docstring's "EXTRA PROBES" section. The 34 critical_queries
# guards alone produce ZERO BOUNDARY-category probes on today's index, which would make that
# category vacuous by fixture composition. These two are sourced from an already-committed
# fixture (eval/accuracy_gate/edge_probe_natural_048.jsonl, verbatim, intent_expected="fact"),
# needles verified unique in the deployed index before use -- not hand-invented questions.
EXTRA_BOUNDARY_PROBES = [
    ('nat_28 verbatim (VAT withholding SERVICES, boundary-history probe)',
     'query: nimefanya kazi ya ushauri kwa taasisi ya serikali wamesema watakata vat je '
     'asilimia ngapi na cheti nitapata lini',
     ['vat withholding services']),
    ('nat_44 verbatim (VAT withholding GOODS, boundary-history probe)',
     'query: nimeuzia wakala wa serikali bidhaa je watanikata asilimia ngapi ya vat',
     ['vat withholding goods']),
]


def load_probes(regen_script=REGEN_SCRIPT):
    """AST-extract kaggle/regenerate_rag_e5.py's `critical_queries` list without importing
    the module (importing it triggers Kaggle auth + network fetches as side effects), then
    append EXTRA_BOUNDARY_PROBES so the BOUNDARY category has real members to track."""
    with open(regen_script, encoding='utf-8') as f:
        src = f.read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                getattr(t, 'id', None) == 'critical_queries' for t in node.targets):
            return ast.literal_eval(node.value) + EXTRA_BOUNDARY_PROBES
    raise RuntimeError(f"'critical_queries' assignment not found in {regen_script} -- "
                        f"has it been renamed?")


def load_deployed_index(index_dir=DEFAULT_INDEX_DIR):
    import numpy as np
    emb = np.load(os.path.join(index_dir, 'rag_embeddings.npy'))
    with open(os.path.join(index_dir, 'rag_facts_text.json'), encoding='utf-8') as f:
        texts = json.load(f)
    norm = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-10)
    return norm, texts


def build_prospective_index(model):
    """Prospective post-latest-fact-edit index, embedded locally with the SAME cached
    e5-base production uses -- not yet shipped, not yet in kaggle/rag_facts_text.json."""
    import numpy as np
    from precompute_rag_embeddings import build_fact_texts
    texts, keys, dropped = build_fact_texts()
    prefixed = ['passage: ' + t for t in texts]
    emb = np.array(model.encode(prefixed, show_progress_bar=False))
    norm = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-10)
    return norm, texts, len(dropped)


def _categorize(rank):
    if rank is None:
        return 'ABSENT'
    if rank <= TOP_K:
        return 'IN_TOP3'
    if rank <= BOUNDARY_MAX:
        return 'BOUNDARY'
    return 'DEEP'


class Retriever:
    """Mirrors chike.retrieval / Orchestrator._pool_facts exactly, against a GIVEN
    (norm_embeddings, texts) index -- same e5-base, same 'query: '/'passage: ' asymmetry,
    same per-sub-question top_k=3 + dedupe-preserve-order + cap 9 pooling. Needle matching
    (not row position) is how a probe's target fact is located, so this survives a regen
    that reorders or renumbers rows."""

    def __init__(self, model, norm_emb, texts):
        self.model = model
        self.norm_emb = norm_emb
        self.texts = texts

    def _encode_query(self, q):
        import numpy as np
        v = self.model.encode([q if q.startswith('query:') else f'query: {q}'])[0]
        return v / (np.linalg.norm(v) + 1e-10)

    def rank_of(self, question, needle):
        """Full ranking of `question` against every row; first row containing `needle`
        (case-insensitive substring) is the rank. None if the needle is absent everywhere
        -- an ABSENT verdict, not a rank of infinity."""
        import numpy as np
        qv = self._encode_query(question)
        scores = np.dot(self.norm_emb, qv)
        order = np.argsort(-scores)
        for r, idx in enumerate(order, 1):
            if needle.lower() in self.texts[int(idx)].lower():
                return r
        return None

    def reaches_pooled_context(self, question, needle):
        """True iff `needle` appears in the POOLED context Orchestrator._pool_facts would
        actually build for `question` -- decompose, top_k=3 per sub-question, dedupe,
        cap 9. This is the authoritative "did it reach the model" bit; raw_rank's IN_TOP3/
        BOUNDARY/DEEP category is diagnostic, this is the ground truth."""
        from chike import decomposition
        import numpy as np
        subs = decomposition.decompose_query(question) or [question]
        pooled, seen = [], set()
        for sq in subs:
            qv = self._encode_query(sq)
            scores = np.dot(self.norm_emb, qv)
            top_idx = np.argsort(-scores)[:TOP_K]
            for idx in top_idx:
                idx = int(idx)
                if idx not in seen:
                    seen.add(idx)
                    pooled.append(idx)
        pooled = pooled[:POOL_CAP]
        return any(needle.lower() in self.texts[i].lower() for i in pooled)


def measure(retriever, probes):
    rows = []
    for name, question, expected in probes:
        # Guards may list >1 acceptable needle (any one confirms retrieval); use the
        # first for rank (a single, stable number to track), all for reaches_context.
        needles = expected if isinstance(expected, (list, tuple)) else [expected]
        primary = needles[0]
        rank = retriever.rank_of(question, primary)
        reaches = any(retriever.reaches_pooled_context(question, n) for n in needles)
        rows.append({
            'name': name,
            'question': question,
            'needle': primary,
            'raw_rank': rank,
            'category': _categorize(rank),
            'reaches_context': reaches,
        })
    return rows


def summarize(rows):
    by_cat = {}
    for r in rows:
        by_cat[r['category']] = by_cat.get(r['category'], 0) + 1
    reach_hits = sum(1 for r in rows if r['reaches_context'])
    return {
        'total_probes': len(rows),
        'reaches_context_count': reach_hits,
        'reaches_context_rate': round(reach_hits / len(rows), 3) if rows else None,
        'by_category': by_cat,
        'boundary_watchlist': sorted(r['name'] for r in rows if r['category'] == 'BOUNDARY'),
        'deep_or_absent': sorted(r['name'] for r in rows
                                  if r['category'] in ('DEEP', 'ABSENT')),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--index-dir', default=DEFAULT_INDEX_DIR,
                     help='directory with rag_embeddings.npy + rag_facts_text.json '
                          '(default: chike-inference/, what production actually loads)')
    ap.add_argument('--out', default=os.path.join(
        REPO, 'eval', 'results', 'grounded_fact_reach_baseline.json'))
    ap.add_argument('--compare-prospective', action='store_true',
                     help='also build the prospective post-latest-edit index locally '
                          '(precompute.build_fact_texts(), embedded with the cached '
                          'e5-base) and report per-probe deltas against it')
    ap.add_argument('--prospective-out', default=os.path.join(
        REPO, 'eval', 'results', 'grounded_fact_reach_prospective_compare.json'))
    args = ap.parse_args()

    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('intfloat/multilingual-e5-base')

    probes = load_probes()
    print(f'[probes] {len(probes)} loaded from {os.path.relpath(REGEN_SCRIPT, REPO)} '
          f'(survivorship-biased floor fixture -- see module docstring)')

    norm_a, texts_a = load_deployed_index(args.index_dir)
    print(f'[index] deployed: {len(texts_a)} rows from {args.index_dir}')
    retriever_a = Retriever(model, norm_a, texts_a)
    rows_a = measure(retriever_a, probes)
    summary_a = summarize(rows_a)

    baseline = {
        'measured': '2026-09-05',
        'index_dir': args.index_dir,
        'index_rows': len(texts_a),
        'method': 'production-exact pooled retrieval (chike.decomposition + '
                  'Orchestrator._pool_facts semantics), needle-matched, not row-'
                  'position-matched',
        'top_k': TOP_K, 'pool_cap': POOL_CAP, 'boundary_max_rank': BOUNDARY_MAX,
        'fixture_caveat': ('34 hand-picked regression probes from kaggle/'
                            'regenerate_rag_e5.py -- a floor, not a corpus-wide claim; '
                            'see module docstring'),
        'summary': summary_a,
        'rows': rows_a,
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(baseline, f, ensure_ascii=False, indent=2)

    print(f"\nreaches_context: {summary_a['reaches_context_count']}/{summary_a['total_probes']} "
          f"({summary_a['reaches_context_rate']:.0%})")
    print(f"by category: {summary_a['by_category']}")
    if summary_a['boundary_watchlist']:
        print(f"BOUNDARY (watch across future regens): {summary_a['boundary_watchlist']}")
    if summary_a['deep_or_absent']:
        print(f"DEEP/ABSENT: {summary_a['deep_or_absent']}")
    print(f'[saved] {args.out}')

    if not args.compare_prospective:
        return

    print('\n' + '=' * 60)
    print('PROSPECTIVE COMPARE (local e5, not yet shipped)')
    print('=' * 60)
    norm_b, texts_b, n_dropped = build_prospective_index(model)
    print(f'[index] prospective: {len(texts_b)} rows ({n_dropped} dropped as noise)')
    retriever_b = Retriever(model, norm_b, texts_b)
    rows_b = measure(retriever_b, probes)
    summary_b = summarize(rows_b)

    by_name_a = {r['name']: r for r in rows_a}
    deltas = []
    for rb in rows_b:
        ra = by_name_a.get(rb['name'])
        rank_delta = (None if not (ra and ra['raw_rank'] and rb['raw_rank'])
                      else rb['raw_rank'] - ra['raw_rank'])
        deltas.append({
            'name': rb['name'],
            'deployed_rank': ra['raw_rank'] if ra else None,
            'prospective_rank': rb['raw_rank'],
            'rank_delta': rank_delta,
            'deployed_category': ra['category'] if ra else None,
            'prospective_category': rb['category'],
            'category_changed': (ra is not None and ra['category'] != rb['category']),
            'deployed_reaches_context': ra['reaches_context'] if ra else None,
            'prospective_reaches_context': rb['reaches_context'],
        })

    unchanged_zero_move = sum(
        1 for d in deltas
        if d['deployed_category'] == 'IN_TOP3' and d['rank_delta'] == 0)
    compare_out = {
        'measured': '2026-09-05',
        'deployed_index_rows': len(texts_a),
        'prospective_index_rows': len(texts_b),
        'prospective_dropped_as_noise': n_dropped,
        'summary_deployed': summary_a,
        'summary_prospective': summary_b,
        'note': (f'{unchanged_zero_move} probe(s) already IN_TOP3 on the deployed index '
                 f'moved rank 0 against the prospective build -- the stability contrast '
                 f'this measure is built to watch for. Category flips (a probe changing '
                 f'IN_TOP3/BOUNDARY/DEEP/ABSENT) are listed explicitly, not just averaged.'),
        'category_flips': [d for d in deltas if d['category_changed']],
        'deltas': deltas,
    }
    os.makedirs(os.path.dirname(args.prospective_out), exist_ok=True)
    with open(args.prospective_out, 'w', encoding='utf-8') as f:
        json.dump(compare_out, f, ensure_ascii=False, indent=2)

    print(f'\n{unchanged_zero_move} IN_TOP3 probe(s) moved 0 ranks despite the prospective '
          f'build touching {len(texts_a) - len(texts_b) if len(texts_a) != len(texts_b) else "a different set of"} rows')
    if compare_out['category_flips']:
        print('CATEGORY FLIPS:')
        for d in compare_out['category_flips']:
            print(f"  {d['name']}: {d['deployed_category']} (rank {d['deployed_rank']}) -> "
                  f"{d['prospective_category']} (rank {d['prospective_rank']})")
    print(f'[saved] {args.prospective_out}')


if __name__ == '__main__':
    main()
