# -*- coding: utf-8 -*-
"""SCOPING MEASUREMENT for the coverage gate. Measures signals; designs nothing.

THE PROBLEM. On an uncovered question `retrieve_facts` applies no floor: it returns the three
nearest facts at any score and the model writes a confident answer out of them. Measured
2026-08-23, nine of twelve ordinary trader topics land there. Three floor designs are dead —
absolute score has no cut point, margin INVERTS, and forced maximum retrieval confidence still
produced a wrong answer — and all three died because they consulted a SCORE. So the question
this harness exists to answer is:

    what signal says "the corpus holds a fact about this topic" WITHOUT consulting a score,
    and what does it cost in false refusals?

THE FAILURE MODE BEING PRICED IS FALSE REFUSAL, NOT MISSED CATCH. Refusing something we can
answer makes the product worse, not safer — it is the bare-`hisa` shape (R17), where one
over-broad phrase would have refused seven real gate questions. So every candidate is scored
FIRST on what it refuses that we can answer, and only then on what it catches.

FOUR CANDIDATE SIGNALS, none of which reads a similarity value:

  S1  ROUTE          — a deterministic route (compute / presumptive / VAT / EFD / minimum wage)
                       means the answer comes from an engine, not the index. Covered by
                       construction. Free, and it is the reason the gate need only guard the
                       fact path.
  S2  Q_IN_CORPUS    — does any content term of the QUESTION appear anywhere in the index text?
                       Question-side only: no retrieval at all.
  S3  TOP1_OVERLAP   — does the top-1 retrieved fact share a content term with the question?
                       Uses retrieval ORDER but never its score. This is the direct test of the
                       `nat_05` mechanism: a BRELA fee answering an SDL question shares nothing
                       with the question it was returned for.
  S4  TOP3_OVERLAP   — the same count over the pooled top-3, reported as a DISTRIBUTION so a
                       threshold can be chosen after looking rather than before.

Each of S2-S4 is computed under two token-matching rules, because Swahili morphology is a real
design parameter and not a detail: EXACT whole-token, and STEM (first 5 characters), which lets
`mauzo`/`kuuza`/`nauza` match. Both are reported for every candidate; neither is assumed.

CORPORA — chosen so the cost side is bigger than the catch side:
  gate_400        eval_questions_001/002/003 — the accuracy gate. In-corpus by construction;
                  ANY refusal here is a false refusal.
  natural_48      the natural edge probes, joined to their 2026-08-17 adjudicated verdicts, so
                  refusals can be split by whether we actually answered the row correctly.
  inscope_69      the R17 in-scope adversarial probes (expected_refusal=false) — questions
                  authored specifically to look refusable while being answerable.
  uncovered_12    the coverage fixture. The only corpus where a refusal is the RIGHT answer.

Runs fully offline: e5-base is in the local HF cache, so HF_HUB_OFFLINE=1 is set below and no
download is attempted.

R18: committed before its result is written up.
Artifact: eval/results/coverage_gate_signals.json
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

from chike import decomposition, routing                                    # noqa: E402

OUT = os.path.join(REPO, 'eval', 'results', 'coverage_gate_signals.json')
INDEX_TEXT = os.path.join(REPO, 'chike-inference', 'rag_facts_text.json')
INDEX_EMB = os.path.join(REPO, 'chike-inference', 'rag_embeddings.npy')
ADJUDICATION = os.path.join(REPO, 'eval', 'results',
                            'natural48_rerun_2026_08_17_adjudication.json')

TOP_K = 3          # production value, chike-inference/modal_app.py

# Swahili + English function words and question scaffolding. These carry no topic, so letting
# them count as overlap would make every signal fire on every question — the vacuous-check
# shape from the other direction.
STOP = set("""
nina ninao nini nani lini wapi vipi gani ngapi kiasi je ni na ya wa za la kwa katika kutoka
hadi kama lakini au pia sasa bado tu sana zaidi kila yote wote hii hilo hiyo huyu hawa ile
yangu yako yake yetu yenu zangu zako langu lako wangu wako nataka naomba nahitaji nauliza
ninaomba tafadhali samahani asante ndiyo hapana sio siyo kuna kuwa kufanya nifanye nifanyeje
nitapata nitalipa nalipa inagharimu inatakiwa lazima naweza inaweza anaweza wanaweza the what
is are how much many for and with from that this does can should must have has who when where
mimi wewe yeye sisi ninyi wao mwaka mwezi siku sasa hivi baada kabla kwenye ndani nje juu
chini mbele nyuma pale hapa huko yenyewe mwenyewe ambayo ambao ambaye
""".split())

_WORD = re.compile(r"[a-zA-Z']+")
STEM_LEN = 5


def content_tokens(text):
    """Topic-bearing tokens: alphabetic, >=4 chars, not a stop word, not a number.

    Numbers are excluded deliberately: a figure the USER supplied says nothing about whether
    the corpus holds a fact — it is the same trap the grounding harness hit when it counted a
    user-supplied 'milioni 60' as an unsupported figure.
    """
    return {w.lower() for w in _WORD.findall(text)
            if len(w) >= 4 and w.lower() not in STOP}


def stems(tokens):
    return {t[:STEM_LEN] for t in tokens}


def load_corpora():
    def jl(path, qfield):
        rows = []
        with open(os.path.join(REPO, path), encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    rows.append({'id': r.get('id'), 'q': r[qfield],
                                 'subdomain': r.get('subdomain')})
        return rows

    gate = []
    for p in ('eval/accuracy_gate/eval_questions_001.jsonl',
              'eval/accuracy_gate/eval_questions_002_additions.jsonl',
              'eval/accuracy_gate/eval_questions_003.jsonl'):
        gate += jl(p, 'question_sw')

    nat = jl('eval/accuracy_gate/edge_probe_natural_048.jsonl', 'question')
    with open(ADJUDICATION, encoding='utf-8') as f:
        adj = {r['id']: r for r in json.load(f)['rows']}
    for r in nat:
        a = adj.get(r['id'], {})
        r['verdict'] = a.get('verdict')
        r['path'] = a.get('path')

    inscope = []
    for fn in ('concord_1pl_in_scope_020.jsonl', 'object_concord_in_scope_022.jsonl',
               'ooc_adversarial_in_scope_015.jsonl',
               'orthographic_variant_in_scope_012.jsonl'):
        with open(os.path.join(REPO, 'eval/refusal_gate', fn), encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                if r.get('expected_refusal') is False:
                    inscope.append({'id': r.get('id'), 'q': r['question'],
                                    'subdomain': r.get('subdomain'), 'file': fn})

    with open(os.path.join(REPO, 'scratch', 'coverage_gap_2026_08_16.json'),
              encoding='utf-8') as f:
        cov = [{'id': r['topic'], 'q': r['question'], 'subdomain': r['topic']}
               for r in json.load(f)['rows']]

    return {'gate_400': gate, 'natural_48': nat, 'inscope_69': inscope, 'uncovered_12': cov}


def main():
    import numpy as np
    from sentence_transformers import SentenceTransformer

    with open(INDEX_TEXT, encoding='utf-8') as f:
        texts = json.load(f)
    emb = np.load(INDEX_EMB)
    assert emb.shape[0] == len(texts), (emb.shape, len(texts))
    emb = emb / np.linalg.norm(emb, axis=1, keepdims=True)

    fact_tokens = [content_tokens(t) for t in texts]
    fact_stems = [stems(s) for s in fact_tokens]
    corpus_tokens = set().union(*fact_tokens)
    corpus_stems = set().union(*fact_stems)

    model = SentenceTransformer('intfloat/multilingual-e5-base')
    corpora = load_corpora()

    results = {}
    for name, rows in corpora.items():
        qs = [f"query: {r['q']}" for r in rows]
        qv = model.encode(qs, batch_size=16, show_progress_bar=False,
                          normalize_embeddings=True)
        sims = qv @ emb.T
        order = np.argsort(-sims, axis=1)[:, :TOP_K]

        out_rows = []
        for i, r in enumerate(rows):
            qt = content_tokens(r['q'])
            qs_ = stems(qt)
            parts = decomposition.decompose_query(r['q'])
            intents = [routing.detect_intent(p) for p in parts]
            route = next((x for x in intents if x != 'none'), 'none')

            top = [int(j) for j in order[i]]
            # S3/S4 measure OVERLAP SIZE, not a boolean, so the threshold can be picked from
            # the distribution afterwards instead of being assumed here.
            ov_exact = [len(qt & fact_tokens[j]) for j in top]
            ov_stem = [len(qs_ & fact_stems[j]) for j in top]

            out_rows.append({
                'id': r['id'], 'q': r['q'], 'subdomain': r.get('subdomain'),
                'verdict': r.get('verdict'), 'adjudicated_path': r.get('path'),
                'route': route,
                'n_content_tokens': len(qt),
                's2_q_in_corpus_exact': len(qt & corpus_tokens),
                's2_q_in_corpus_stem': len(qs_ & corpus_stems),
                's3_top1_overlap_exact': ov_exact[0],
                's3_top1_overlap_stem': ov_stem[0],
                's4_top3_overlap_exact_max': max(ov_exact),
                's4_top3_overlap_stem_max': max(ov_stem),
                's4_top3_overlap_stem_each': ov_stem,
                'top1_fact': texts[top[0]][:120],
                'top1_score': round(float(sims[i][top[0]]), 4),
            })
        results[name] = out_rows

    # --- candidate evaluation -------------------------------------------------------------
    # A candidate = (signal, threshold, gate_applies_only_to_fact_path). For each we report
    # what it REFUSES on each corpus. On gate_400 / inscope_69 every refusal is a false
    # refusal; on uncovered_12 every refusal is a catch.
    def refuses(row, field, thr, fact_path_only):
        if fact_path_only and row['route'] != 'none':
            return False
        return row[field] < thr

    candidates = []
    for field in ('s3_top1_overlap_exact', 's3_top1_overlap_stem',
                  's4_top3_overlap_exact_max', 's4_top3_overlap_stem_max',
                  's2_q_in_corpus_exact', 's2_q_in_corpus_stem'):
        for thr in (1, 2, 3):
            for fpo in (True, False):
                c = {'signal': field, 'threshold_refuse_below': thr,
                     'fact_path_only': fpo, 'per_corpus': {}}
                for name, rows in results.items():
                    ref = [r for r in rows if refuses(r, field, thr, fpo)]
                    entry = {'n': len(rows), 'refused': len(ref),
                             'rate': round(len(ref) / len(rows), 4)}
                    if name == 'natural_48':
                        entry['refused_that_were_CORRECT'] = sum(
                            1 for r in ref if r['verdict'] == 'CORRECT')
                        entry['refused_that_were_WRONG'] = sum(
                            1 for r in ref if r['verdict'] == 'WRONG')
                    if name in ('gate_400', 'inscope_69'):
                        entry['false_refusal_ids'] = [r['id'] for r in ref][:20]
                    if name == 'uncovered_12':
                        entry['caught'] = [r['id'] for r in ref]
                    c['per_corpus'][name] = entry
                # headline cost/benefit, so the table can be sorted on the thing that matters
                c['false_refusals_total'] = (c['per_corpus']['gate_400']['refused']
                                             + c['per_corpus']['inscope_69']['refused']
                                             + c['per_corpus']['natural_48']
                                             ['refused_that_were_CORRECT'])
                c['caught_of_12'] = c['per_corpus']['uncovered_12']['refused']
                candidates.append(c)

    candidates.sort(key=lambda c: (c['false_refusals_total'], -c['caught_of_12']))

    out = {
        'measured': '2026-08-23',
        'harness': 'eval/coverage/measure_coverage_gate_signals.py',
        'purpose': 'SCOPING. Measures candidate signals for a coverage gate. Designs nothing '
                   'and recommends nothing; the ordering below is by measured false-refusal '
                   'cost, which is the failure mode that makes the product worse.',
        'top_k': TOP_K,
        'index_rows': len(texts),
        'stem_len': STEM_LEN,
        'corpora': {k: len(v) for k, v in results.items()},
        'candidates': candidates,
        'rows': results,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print('corpora:', json.dumps(out['corpora']))
    print('\n--- route coverage (S1, free) ---')
    for name, rows in results.items():
        routed = sum(1 for r in rows if r['route'] != 'none')
        print(f'  {name:<14} routed {routed:>4}/{len(rows):<4} '
              f'({routed / len(rows):.0%}) -> gate never applies to these')
    print('\n--- candidates, sorted by FALSE REFUSALS (lower is better) ---')
    print(f"  {'signal':<28}{'thr':>4}{'factOnly':>9}{'falseRef':>10}{'caught/12':>11}"
          f"{'gate400':>9}{'insc69':>8}{'nat48ok':>9}")
    for c in candidates[:18]:
        p = c['per_corpus']
        print(f"  {c['signal']:<28}{c['threshold_refuse_below']:>4}"
              f"{str(c['fact_path_only']):>9}{c['false_refusals_total']:>10}"
              f"{c['caught_of_12']:>11}{p['gate_400']['refused']:>9}"
              f"{p['inscope_69']['refused']:>8}"
              f"{p['natural_48']['refused_that_were_CORRECT']:>9}")
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()
