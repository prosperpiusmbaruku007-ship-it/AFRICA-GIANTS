# -*- coding: utf-8 -*-
"""Does production's SINGLE-ARM retriever lose to the two-arm hybrid on a CLASS, or on one row?

THE FINDING THAT PROMPTED THIS. On `eval_337` the shipped single-arm retriever produces
*"asilimia 10"* (wrong) and the two-arm hybrid produces *"asilimia 20 ya mshahara ghafi (10
mwajiri + 10 mfanyakazi)"* (right). Production injects single-arm deliberately —
`modal_app.py:421-430`, on the grounds that *"four measurements have failed to show a two-arm
benefit and the only two genuine non-clarification regressions ever recorded were its
artefacts."*

**That decision was made on evidence and is not overturned by one row.** But the evidence
predates this row, and the premise/instruction thread's conclusions were taken on the two-arm
path, so we now hold a case where the shipped configuration is measurably worse and a set of
results taken on the other one. **One row is a curiosity. A class reopens the 2026-08-17
decision on evidence rather than leaving it defended by its own age.**

TWO STAGES, so the live cost is spent only where it can tell us something.

  STAGE 1, OFFLINE. The second arm fires ONLY on a digit-bearing query (`chike/retrieval.py`
  strips numeric amounts and re-queries). So for every candidate row, compare the two retrievers'
  fact sets directly. Rows where the sets are IDENTICAL cannot differ in output and are excluded
  from the live stage — that exclusion is measured, not assumed.

  STAGE 2, LIVE. For rows where the sets differ, run BOTH arms through `Orchestrator.answer`
  against the deployed weights and record both replies. R24: the single-arm arm is asserted
  against the recorded live reply wherever one exists, so the baseline is proven before the
  contrast is read.

POPULATION: the 17 veto-diverted rows plus the 48 natural edge probes — the two sets where this
project's wrong answers actually live. Compute-path rows are kept in stage 1 (the retriever is
still called) but flagged, since their answer comes from the rules engine.

DIRECTION IS ADJUDICATED, NOT COUNTED. "The answer changed" is not "the answer improved"; each
differing row is recorded with both replies for reading, and the verdict is labelled judgement.

R18: committed before it runs.
Artifact: eval/results/two_arm_effect.json
"""
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)

DIVERTED = os.path.join(REPO, 'eval', 'results', 'veto_diversion_live.json')
NAT48 = os.path.join(REPO, 'eval', 'accuracy_gate', 'edge_probe_natural_048.jsonl')
ADJ48 = os.path.join(REPO, 'eval', 'results',
                     'natural48_rerun_2026_08_17_adjudication.json')
INDEX_TEXT = os.path.join(REPO, 'chike-inference', 'rag_facts_text.json')
INDEX_EMB = os.path.join(REPO, 'chike-inference', 'rag_embeddings.npy')
OUT = os.path.join(REPO, 'eval', 'results', 'two_arm_effect.json')
ADAPTER_REPO = 'prospAprospA007/africa-giants-adapter-v15'
ENDPOINT = 'https://prosperpiusmbaruku007--chike-inference-generate-endpoint.modal.run'
TOP_K = 3


def _token():
    for k in ('CHIKE_MODAL_TOKEN', 'MODAL_API_TOKEN'):
        v = os.environ.get(k)
        if v:
            return v.strip()
    p = os.path.expanduser('~/.chike_modal_token.txt')
    return (open(p, encoding='utf-8').read().strip() or None) if os.path.exists(p) else None


def single_arm():
    """Faithful copy of modal_app.ChikeModel.retrieve_facts — the SHIPPED retriever."""
    import numpy as np
    from sentence_transformers import SentenceTransformer
    with open(INDEX_TEXT, encoding='utf-8') as f:
        texts = json.load(f)
    emb = np.load(INDEX_EMB)
    model = SentenceTransformer('intfloat/multilingual-e5-base')

    def retrieve(question, top_k=TOP_K):
        q = model.encode([f'query: {question}'])[0]
        q = q / (np.linalg.norm(q) + 1e-10)
        norms = np.linalg.norm(emb, axis=1, keepdims=True)
        scores = np.dot(emb / (norms + 1e-10), q)
        return [texts[i] for i in np.argsort(scores)[-top_k:][::-1]]

    return retrieve


def load_population():
    with open(DIVERTED, encoding='utf-8') as f:
        div = json.load(f)['rows']
    rows = [{'id': r['id'], 'q': r['question'], 'set': 'diverted',
             'recorded_live': (r.get('reply') or '').strip()} for r in div]
    with open(ADJ48, encoding='utf-8') as f:
        adj = {r['id']: r for r in json.load(f)['rows']}
    with open(NAT48, encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            a = adj.get(r['id'], {})
            rows.append({'id': r['id'], 'q': r['question'], 'set': 'natural_48',
                         'recorded_live': (a.get('reply') or '').strip(),
                         'verdict_2026_08_17': a.get('now'),
                         'path': a.get('path')})
    seen, out = set(), []
    for r in rows:                       # the diverted set and the 48 overlap
        if r['id'] not in seen:
            seen.add(r['id'])
            out.append(r)
    return out


def main():
    from transformers import AutoTokenizer
    from chike.retrieval import retrieve as two_arm
    from chike.orchestrator import Orchestrator
    from chike.model_abstraction import LocalAdapter

    population = load_population()
    one = single_arm()

    # ---- STAGE 1: which rows can even differ? -----------------------------------------------
    stage1 = []
    for r in population:
        a = list(one(r['q']))
        b = list(two_arm(r['q']))
        stage1.append({**r, 'n_single': len(a), 'n_two_arm': len(b),
                       'sets_differ': a != b,
                       'extra_facts': [t[:120] for t in b if t not in a]})
    differing = [r for r in stage1 if r['sets_differ']]
    print(f'population {len(population)}   fact sets differ on {len(differing)} '
          f'({len(differing) / len(population):.0%})')

    # ---- STAGE 2: live, only where they differ ----------------------------------------------
    token = _token()
    assert token, 'no Modal token'
    tok = AutoTokenizer.from_pretrained(ADAPTER_REPO, trust_remote_code=True)

    def build(retriever):
        return Orchestrator(backend=LocalAdapter(endpoint_url=ENDPOINT, token=token,
                                                 tokenizer=tok), retriever=retriever)

    orch_single, orch_two = build(one), build(two_arm)

    live_rows = []
    for r in differing:
        t0 = time.time()
        s = orch_single.answer(r['q']).text.strip()
        t = orch_two.answer(r['q']).text.strip()
        rec = {**r,
               'single_arm_reply': s, 'two_arm_reply': t,
               'replies_differ': s != t,
               'single_matches_recorded_live': (s == r['recorded_live']
                                                if r['recorded_live'] else None),
               'elapsed_s': round(time.time() - t0, 1)}
        live_rows.append(rec)
        print(f"\n=== {r['id']} ({r['set']}) facts {r['n_single']}->{r['n_two_arm']}  "
              f"replies_differ={rec['replies_differ']}  "
              f"baseline_ok={rec['single_matches_recorded_live']}")
        if rec['replies_differ']:
            print(f"  SINGLE: {s[:170]}")
            print(f"  TWOARM: {t[:170]}")

    changed = [r for r in live_rows if r['replies_differ']]
    baseline_ok = [r for r in live_rows if r['single_matches_recorded_live'] is True]
    baseline_bad = [r['id'] for r in live_rows if r['single_matches_recorded_live'] is False]

    out = {
        'measured': '2026-08-24',
        'harness': 'eval/routing/measure_two_arm_effect.py',
        'question': 'does the shipped single-arm retriever lose to the two-arm hybrid on a '
                    'CLASS, or on one row?',
        'prior_decision': 'modal_app.py injects single-arm; 2026-08-17 recorded four '
                          'measurements showing no two-arm benefit and two regressions.',
        'adjudication': 'PENDING — direction is JUDGEMENT and is added in a follow-up commit. '
                        '"The answer changed" is not "the answer improved".',
        'population': len(population),
        'fact_sets_differ': len(differing),
        'replies_differ': len(changed),
        'r24_baselines_reproducing_live': len(baseline_ok),
        'r24_baselines_failing': baseline_bad,
        'stage1': stage1,
        'live_rows': live_rows,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"\n=== fact sets differ: {len(differing)}/{len(population)}")
    print(f"=== replies differ:    {len(changed)}/{len(differing)}")
    print(f"=== R24 baselines reproducing live: {len(baseline_ok)}/{len(live_rows)}"
          f"  failing: {baseline_bad}")
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()
