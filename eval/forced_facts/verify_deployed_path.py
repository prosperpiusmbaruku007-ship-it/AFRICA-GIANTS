# -*- coding: utf-8 -*-
"""Is the deployed pipeline the pipeline in this repo? Decide it, and name the divergence.

THE OBSERVATION. Same question, same weights, greedy decode, two answers:

    deployed ChikeModel.run                     -> "Kiwango sahihi ni asilimia 10"   (WRONG)
    local Orchestrator + LocalAdapter (default) -> "…asilimia 20 (10 mwajiri + 10 …)" (RIGHT)

If the deployed pipeline is not the code in this repo, every offline reconstruction in this
workstream inherits the doubt — the separation arms, the forced-fact runs, the grounding
measurement, the discard rate. That is a lot of conclusions resting on one assumption nobody had
tested.

THE CANDIDATE EXPLANATION, from reading `chike-inference/modal_app.py:421-430`. Production builds
the SAME `Orchestrator` class from this repo, but injects its own retriever:

    retriever=self.retrieve_facts,   # single-arm top-3

while `Orchestrator`'s DEFAULT is `chike.retrieval.retrieve` — a TWO-ARM hybrid that, on a query
containing digits, runs a second pass over the number-stripped query and appends the first new
fact, yielding **top_k + 1**. `eval_337`'s question carries "3.5" and "0.5", so the two-arm path
hands the model FOUR facts and the single-arm path THREE. The injection is deliberate and
documented in that file: four measurements failed to show a two-arm benefit and the only two
genuine regressions recorded were its artefacts.

**So the hypothesis is that this is a RECONSTRUCTION error, not a deployment drift** — I used the
class default where production injects. This harness decides it.

THE DECISIVE TEST. Rebuild the local Orchestrator with a single-arm retriever that mirrors
`modal_app.retrieve_facts` exactly, and assert the reply is BYTE-IDENTICAL to the recorded live
reply. If it is:
  * the deployed container is running this repo's code, and
  * the divergence is fully explained by the injected retriever, and
  * only harnesses that used the two-arm default are affected.
If it is NOT, the divergence is somewhere else and the doubt is real.

Both arms are run on every specimen so the difference is attributable rather than inferred.

R18: committed before it runs.
Artifact: eval/results/deployed_path_verification.json
"""
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)

from chike.orchestrator import Orchestrator                                 # noqa: E402
from chike.model_abstraction import LocalAdapter                            # noqa: E402

LIVE = os.path.join(REPO, 'eval', 'results', 'veto_diversion_live.json')
INDEX_TEXT = os.path.join(REPO, 'chike-inference', 'rag_facts_text.json')
INDEX_EMB = os.path.join(REPO, 'chike-inference', 'rag_embeddings.npy')
OUT = os.path.join(REPO, 'eval', 'results', 'deployed_path_verification.json')
ADAPTER_REPO = 'prospAprospA007/africa-giants-adapter-v15'
ENDPOINT = 'https://prosperpiusmbaruku007--chike-inference-generate-endpoint.modal.run'

SPECIMENS = ['eval_337', 'eval_348', 'eval_342']
TOP_K = 3


def _token():
    for k in ('CHIKE_MODAL_TOKEN', 'MODAL_API_TOKEN'):
        v = os.environ.get(k)
        if v:
            return v.strip()
    p = os.path.expanduser('~/.chike_modal_token.txt')
    return (open(p, encoding='utf-8').read().strip() or None) if os.path.exists(p) else None


def single_arm_retriever():
    """A faithful copy of modal_app.ChikeModel.retrieve_facts — single arm, top-3, e5, cosine.

    Written out rather than imported because modal_app.py is a Modal module that cannot be
    imported locally. Kept line-for-line equivalent to lines 281-308 of that file; if it drifts,
    the assertion below is what catches it.
    """
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
        idx = np.argsort(scores)[-top_k:][::-1]
        return [texts[i] for i in idx]

    return retrieve


def main():
    from transformers import AutoTokenizer

    token = _token()
    assert token, 'no Modal token — this harness needs the deployed weights'
    tok = AutoTokenizer.from_pretrained(ADAPTER_REPO, trust_remote_code=True)

    with open(LIVE, encoding='utf-8') as f:
        live = {r['id']: r for r in json.load(f)['rows']}

    def build(retriever):
        return Orchestrator(backend=LocalAdapter(endpoint_url=ENDPOINT, token=token,
                                                 tokenizer=tok),
                            retriever=retriever)

    orch_single = build(single_arm_retriever())          # production's injection
    orch_default = build(None)                           # the class default: two-arm hybrid

    rows = []
    for sid in SPECIMENS:
        q = live[sid]['question']
        recorded = (live[sid].get('reply') or '').strip()
        t0 = time.time()
        single = orch_single.answer(q).text.strip()
        t1 = time.time()
        default = orch_default.answer(q).text.strip()
        rec = {
            'id': sid, 'question': q, 'recorded_live_reply': recorded,
            'single_arm_reply': single, 'default_two_arm_reply': default,
            'single_arm_matches_live': single == recorded,
            'two_arm_matches_live': default == recorded,
            'arms_differ': single != default,
            'n_facts_single': len(orch_single.retriever(q)),
            'n_facts_two_arm': len(orch_default.retriever(q)),
            'elapsed_single_s': round(t1 - t0, 1),
            'elapsed_two_arm_s': round(time.time() - t1, 1),
        }
        rows.append(rec)
        print(f"\n=== {sid}")
        print(f"  facts: single-arm {rec['n_facts_single']}  two-arm {rec['n_facts_two_arm']}")
        print(f"  single-arm matches live: {rec['single_arm_matches_live']}")
        print(f"  two-arm    matches live: {rec['two_arm_matches_live']}")
        print(f"  LIVE  : {recorded[:130]}")
        print(f"  SINGLE: {single[:130]}")
        print(f"  TWOARM: {default[:130]}")

    matched = sum(1 for r in rows if r['single_arm_matches_live'])
    out = {
        'measured': '2026-08-24',
        'harness': 'eval/forced_facts/verify_deployed_path.py',
        'question': 'is the deployed pipeline the code in this repo, or has it drifted?',
        'hypothesis': 'reconstruction error, not deployment drift — production INJECTS a '
                      'single-arm retriever (modal_app.py:421-430) where the Orchestrator class '
                      'default is the two-arm hybrid',
        'specimens': SPECIMENS,
        'single_arm_matches_live': matched,
        'two_arm_matches_live': sum(1 for r in rows if r['two_arm_matches_live']),
        'n': len(rows),
        'verdict': ('DEPLOYED PATH CONFIRMED AS REPO CODE — divergence fully explained by the '
                    'injected retriever' if matched == len(rows) else
                    'UNEXPLAINED — the single-arm reconstruction does not reproduce live; the '
                    'doubt about every offline reconstruction is REAL'),
        'rows': rows,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n=== single-arm reproduces live: {matched}/{len(rows)}")
    print(f"=== {out['verdict']}")
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()
