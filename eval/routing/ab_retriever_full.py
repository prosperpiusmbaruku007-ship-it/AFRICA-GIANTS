# -*- coding: utf-8 -*-
"""THE FULL A/B ON THE RETRIEVER: single-arm (shipped) vs two-arm (class default), one measurement.

WHY THIS EXISTS AND WHY IT IS BIGGER THAN THE LAST ONE.
`eval/routing/measure_two_arm_effect.py` (2026-08-24) found the two-arm benefit is a CLASS and
that it lives where production is WRONG — 12 of 16 replies change on the veto-diverted rows
against 1 of 22 on the natural 48. That is a signal at 13 differing rows, 4/2/7. **It is not a
gate, and it is explicitly not a licence to switch production.** This harness is the measurement
the decision deserves.

FOUR THINGS THIS DOES THAT THE LAST ONE DID NOT.

  1. **NO STAGE-1 EXCLUSION. Every row runs LIVE on BOTH arms.** The previous run skipped rows
     whose retrieved fact sets were identical, on the argument that identical prompts under
     greedy decoding (`do_sample: false`, R14) must give identical replies. That argument is
     almost certainly right — which is exactly why it has never been checked. Running them makes
     the identical-set rows a **measured control**: they must come back byte-identical, and a
     single row that does not falsifies the determinism assumption underneath every paired A/B
     in this repo. What a FAILED control looks like here is stated and is distinguishable from
     the pass (R23): a non-empty `nondeterministic_rows` list.

  2. **THE PRIOR DECISION'S OWN EVIDENCE IS IN THE POPULATION.** The 2026-08-17 decision rests
     on named rows, and until now this workstream had re-run none of them:
       * COST — `eval_127` and `eval_208`, *"the only two genuine non-clarification regressions
         ever recorded"*, both attributed to the two-arm retriever (PROGRESS.md, Phase D Run 2
         part 3). `eval_208`: two-arm invented a *"TZS milioni 90"* six-month VAT threshold.
         `eval_127`: a self-contradictory SDL/PAYE deadline answer.
       * BENEFIT-SIDE — the six two-arm-only passes from the same run: `eval_019`/`eval_187`
         (judge-confirmed correct) and `eval_008`/`eval_034`/`eval_186`/`eval_331` (judged
         WRONG — the *illusory* wins that turned the part-3 verdict negative).
       * GUARD — `eval_355`, whose rank-3 EFD fact the rejected *interleave* merge evicted. It
         is the row append-only was designed not to break, so it is the standing check that the
         shipped merge still cannot drop a baseline fact.
     **A decision defended by its own evidence must be re-tested on that evidence.** If the two
     regressions hold, this is a genuine trade and the answer may still be single-arm. If they
     do not reproduce, single-arm's basis is gone entirely.

  3. **DIRECTION IS ADJUDICATED, NOT COUNTED**, against ground truth attached to every row
     (`expected_sw` / `expected_behavior` / `correct_answer_sw` — carried into the artifact so
     the adjudication is grounded in the corpus rather than in memory). "The answer changed" is
     not "the answer improved"; the verdicts land in a follow-up commit and are labelled
     JUDGEMENT.

  4. **R24 BASELINES, WITH STALE ONES EXCLUDED RATHER THAN COUNTED AS FAILURES.** The single-arm
     arm IS production, so it must reproduce the recorded live reply. Three rows failed that in
     the last run (`nat_05`, `nat_23`, `nat_24`) and all three were explained: ROUTING-GAP-A/B
     moved them to the COMPUTE path after their reply was recorded. That is a stale baseline,
     not a divergence — but "I know why" is not a mechanism. The rule here is mechanical:
       * recorded path != path today  -> **STALE_EXCLUDED**, with both paths in the artifact
       * recorded path == path today, replies differ -> **FAILS**, and the row is marked
         `evidence_admissible: false` — a row whose single-arm arm is not production cannot be
         evidence about production
       * no recorded reply -> **NO_BASELINE**, eligible but unverified, and counted separately
     A staleness rule that can excuse anything excuses nothing, so it is one comparison and it
     is recorded per row.

POPULATIONS ARE NAMED, AND WHY EACH ONE IS WHERE THE DECISION APPLIES IS WRITTEN INTO THE
ARTIFACT. That is R22's procedural consequence enacted in the instrument rather than remembered:
this project has now three times measured a remedy on the population where it was not needed
(the discard rate, the coverage gate, this retriever), so a measurement offered for a decision
states the population it was taken on and why that population is where the decision applies.

CRASH-SAFETY IS STRUCTURAL, NOT DEFENSIVE. Per-row flush AND resume-from-artifact: a re-run
skips rows already recorded. The first attempt at the predecessor died 20 rows in on
`ConnectionResetError(10054)` and wrote nothing, because its artifact was dumped once at the end
— the fourth member of the family that began with console truncation. A harness whose output is
written once at the end can lose everything to anything.

R18: committed before it runs.
Artifact: eval/results/ab_retriever_full.json
"""
import argparse
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
GATE_CORPORA = [
    os.path.join(REPO, 'eval', 'accuracy_gate', 'eval_questions_001.jsonl'),
    os.path.join(REPO, 'eval', 'accuracy_gate', 'eval_questions_002_additions.jsonl'),
    os.path.join(REPO, 'eval', 'accuracy_gate', 'eval_questions_003.jsonl'),
]
INDEX_TEXT = os.path.join(REPO, 'chike-inference', 'rag_facts_text.json')
INDEX_EMB = os.path.join(REPO, 'chike-inference', 'rag_embeddings.npy')
OUT = os.path.join(REPO, 'eval', 'results', 'ab_retriever_full.json')
ADAPTER_REPO = 'prospAprospA007/africa-giants-adapter-v15'
ENDPOINT = 'https://prosperpiusmbaruku007--chike-inference-generate-endpoint.modal.run'
TOP_K = 3

# --- the prior decision's own rows, with the claim each one carries -------------------------
PRIOR_ROWS = {
    'eval_127': ('prior_cost',
                 'RECORDED 2-ARM REGRESSION: self-contradictory SDL/PAYE deadline — '
                 '"zinawasilishwa kwa nyakati tofauti" then the same date twice.'),
    'eval_208': ('prior_cost',
                 'RECORDED 2-ARM REGRESSION: invented a "TZS milioni 90" six-month VAT '
                 'threshold that does not exist.'),
    'eval_019': ('prior_benefit', 'two-arm-only pass, JUDGE-CONFIRMED CORRECT in part 3.'),
    'eval_187': ('prior_benefit', 'two-arm-only pass, JUDGE-CONFIRMED CORRECT in part 3.'),
    'eval_008': ('prior_benefit', 'two-arm-only pass JUDGED WRONG — an illusory win.'),
    'eval_034': ('prior_benefit', 'two-arm-only pass JUDGED WRONG — an illusory win.'),
    'eval_186': ('prior_benefit', 'two-arm-only pass JUDGED WRONG — an illusory win.'),
    'eval_331': ('prior_benefit', 'two-arm-only pass JUDGED WRONG — an illusory win. Also one '
                                  'of the two rows the rejected INTERLEAVE merge evicted.'),
    'eval_355': ('prior_guard',
                 'the rank-3 EFD fact INTERLEAVE evicted. Append-only must not drop it — the '
                 'standing check that the shipped merge is still additive.'),
}

WHY_POPULATION = {
    'natural_48': 'plain-Swahili natural phrasing, the closest proxy to what a pilot tester '
                  'types. THE MODEL IS MOSTLY RIGHT HERE (28/48 CORRECT at 2026-08-17), which '
                  'is exactly why a benefit measured only here reads as "no benefit" — this is '
                  'the population the 2026-08-17 measurements were taken on.',
    'diverted': 'the veto-diverted rows: questions the presumptive/entity veto sends to the '
                'fact path, where 41% of replies are confidently WRONG. THIS IS THE POPULATION '
                'THE REMEDY IS FOR (R22) — a retrieval fix is for rows retrieval currently '
                'fails.',
    'prior_cost': 'the two rows the 2026-08-17 decision cites as the two-arm retriever\'s only '
                  'genuine harms. If they hold, the decision is a real trade.',
    'prior_benefit': 'the six two-arm-only passes from the same run — two judge-confirmed, four '
                     'judged illusory. The benefit side of the prior evidence.',
    'prior_guard': 'the interleave-eviction row. Not about single vs two arm at all: it checks '
                   'that the shipped append-only merge still cannot drop a baseline fact.',
}


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


def _path_of(reply):
    """Derive the pipeline path the way the 2026-08-17 adjudication labelled it."""
    if getattr(reply, 'refused', False):
        return 'refusal'
    kinds = {sa.sub_question.kind for sa in getattr(reply, 'sub_answers', ())}
    return 'compute' if 'compute' in kinds else ('fact' if kinds else 'refusal')


def load_population():
    rows = []

    # --- the veto-diverted set (recorded live 2026-08-23, current pipeline) ------------------
    with open(DIVERTED, encoding='utf-8') as f:
        div = json.load(f)
    for r in div['rows']:
        rows.append({'id': r['id'], 'q': r['question'], 'population': 'diverted',
                     'ground_truth': r.get('expected_sw', ''),
                     'recorded_live': (r.get('reply') or '').strip(),
                     'recorded_path': None,          # this artifact does not record a path
                     'recorded_from': 'eval/results/veto_diversion_live.json (2026-08-23)'})

    # --- the natural 48, with their 2026-08-17 replies AND paths ----------------------------
    with open(ADJ48, encoding='utf-8') as f:
        adj = {r['id']: r for r in json.load(f)['rows']}
    with open(NAT48, encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            a = adj.get(r['id'], {})
            rows.append({'id': r['id'], 'q': r['question'], 'population': 'natural_48',
                         'ground_truth': r.get('expected_behavior', ''),
                         'recorded_live': (a.get('reply') or '').strip(),
                         'recorded_path': a.get('path'),
                         'verdict_2026_08_17': a.get('now'),
                         'recorded_from': 'eval/results/natural48_rerun_2026_08_17_'
                                          'adjudication.json'})

    # --- the prior decision's own rows ------------------------------------------------------
    seen_prior = set()
    for path in GATE_CORPORA:
        with open(path, encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                rid = r.get('id')
                if rid in PRIOR_ROWS and rid not in seen_prior:
                    seen_prior.add(rid)
                    pop, claim = PRIOR_ROWS[rid]
                    rows.append({'id': rid, 'q': r['question_sw'], 'population': pop,
                                 'prior_claim': claim,
                                 'ground_truth': r.get('correct_answer_sw', ''),
                                 'recorded_live': '',      # no live reply on the current path
                                 'recorded_path': None,
                                 'recorded_from': os.path.relpath(path, REPO)})
    missing = sorted(set(PRIOR_ROWS) - seen_prior)
    assert not missing, f'prior-decision rows not found in the gate corpora: {missing}'

    # de-dupe, keeping the FIRST occurrence but preserving the prior-row annotation, since
    # eval_127 is in the diverted set AND is one of the two recorded regressions.
    out, by_id = [], {}
    for r in rows:
        if r['id'] in by_id:
            prev = by_id[r['id']]
            if not prev.get('ground_truth'):
                prev['ground_truth'] = r.get('ground_truth', '')
            continue
        by_id[r['id']] = r
        out.append(r)
    for rid in PRIOR_ROWS:                       # annotate prior rows that arrived via another set
        r = by_id[rid]
        if r['population'] != PRIOR_ROWS[rid][0]:
            r['prior_claim'] = PRIOR_ROWS[rid][1]
            r['also_population'] = PRIOR_ROWS[rid][0]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fresh', action='store_true',
                    help='ignore any existing artifact instead of resuming from it')
    args = ap.parse_args()

    from transformers import AutoTokenizer
    from chike.retrieval import retrieve as two_arm
    from chike.orchestrator import Orchestrator
    from chike.model_abstraction import LocalAdapter

    population = load_population()
    from collections import Counter
    print('population', len(population), dict(Counter(r['population'] for r in population)))

    done = {}
    if os.path.exists(OUT) and not args.fresh:
        try:
            prev = json.load(open(OUT, encoding='utf-8'))
            done = {r['id']: r for r in prev.get('rows', []) if not r.get('error')}
            print(f'resuming — {len(done)} rows already recorded')
        except Exception as exc:
            print(f'could not resume ({exc}); starting fresh')

    one = single_arm()
    token = _token()
    assert token, 'no Modal token'
    tok = AutoTokenizer.from_pretrained(ADAPTER_REPO, trust_remote_code=True)

    def build(retriever):
        return Orchestrator(backend=LocalAdapter(endpoint_url=ENDPOINT, token=token,
                                                 tokenizer=tok), retriever=retriever)

    orch_single, orch_two = build(one), build(two_arm)

    results = []

    def flush(status):
        with open(OUT, 'w', encoding='utf-8') as fh:
            json.dump({
                'measured': '2026-08-24',
                'status': status,
                'harness': 'eval/routing/ab_retriever_full.py',
                'question': 'single-arm (shipped) vs two-arm (class default): the full A/B, '
                            'including the rows the 2026-08-17 decision rests on.',
                'arms': {'single': 'copy of modal_app.ChikeModel.retrieve_facts — top-3, one '
                                   'embed call. THIS IS PRODUCTION.',
                         'two': 'chike.retrieval.retrieve — top-3 plus the first new fact from '
                                'a number-stripped second arm on digit-bearing queries '
                                '(top_k+1, append-only).'},
                'why_each_population': WHY_POPULATION,
                'adjudication': 'PENDING — direction is JUDGEMENT, added in a follow-up commit '
                                'against the ground_truth carried on each row.',
                'n_population': len(population),
                'rows': results,
            }, fh, ensure_ascii=False, indent=2)

    for i, r in enumerate(population, 1):
        if r['id'] in done:
            results.append(done[r['id']])
            flush('IN_PROGRESS')
            continue
        t0 = time.time()
        facts_s = facts_t = None
        try:
            facts_s = list(one(r['q']))
            facts_t = list(two_arm(r['q']))
            rs = orch_single.answer(r['q'])
            rt = orch_two.answer(r['q'])
            s, t = rs.text.strip(), rt.text.strip()
            path_s, path_t = _path_of(rs), _path_of(rt)
            err = None
        except Exception as exc:
            s = t = ''
            path_s = path_t = None
            err = f'{type(exc).__name__}: {exc}'
            print(f"  [{r['id']}] ERROR {err}")

        # --- R24 baseline verdict, with the staleness rule applied mechanically -------------
        if err is not None:
            baseline = 'ERROR'
        elif not r['recorded_live']:
            baseline = 'NO_BASELINE'
        elif r['recorded_path'] and r['recorded_path'] != path_s:
            baseline = 'STALE_EXCLUDED'
        elif s == r['recorded_live']:
            baseline = 'REPRODUCES'
        else:
            baseline = 'FAILS'

        rec = {**r,
               'n_facts_single': None if facts_s is None else len(facts_s),
               'n_facts_two': None if facts_t is None else len(facts_t),
               'fact_sets_differ': None if facts_s is None else (facts_s != facts_t),
               'extra_facts': [] if facts_t is None else [x[:150] for x in facts_t
                                                          if x not in (facts_s or [])],
               'single_arm_reply': s, 'two_arm_reply': t,
               'path_single': path_s, 'path_two': path_t,
               'replies_differ': (s != t) if err is None else None,
               'baseline': baseline,
               'evidence_admissible': baseline != 'FAILS' and err is None,
               'error': err,
               'elapsed_s': round(time.time() - t0, 1)}
        results.append(rec)
        flush('IN_PROGRESS')                    # the artifact survives the next fault
        print(f"[{i}/{len(population)}] {r['id']} ({r['population']}) "
              f"facts {rec['n_facts_single']}->{rec['n_facts_two']} "
              f"differ={rec['fact_sets_differ']} replies_differ={rec['replies_differ']} "
              f"baseline={baseline} {rec['elapsed_s']}s")
        if rec['replies_differ']:
            print(f'   SINGLE: {s[:160]}')
            print(f'   TWOARM: {t[:160]}')

    ok = [r for r in results if not r.get('error')]
    errors = [r['id'] for r in results if r.get('error')]
    # THE CONTROL: identical fact sets under greedy decoding must give identical replies.
    nondet = [r['id'] for r in ok if r['fact_sets_differ'] is False and r['replies_differ']]
    by_pop = {}
    for r in ok:
        p = by_pop.setdefault(r['population'], {'n': 0, 'sets_differ': 0, 'replies_differ': 0})
        p['n'] += 1
        p['sets_differ'] += 1 if r['fact_sets_differ'] else 0
        p['replies_differ'] += 1 if r['replies_differ'] else 0

    summary = {
        'by_population': by_pop,
        'determinism_control': {
            'identical_fact_sets': sum(1 for r in ok if r['fact_sets_differ'] is False),
            'of_those_replies_differ': len(nondet),
            'nondeterministic_rows': nondet,
            'reading': 'PASS means the stage-1 exclusion used by the predecessor harness was '
                       'sound. A non-empty list would falsify the determinism assumption '
                       'behind every paired A/B in this repo.',
        },
        'r24_baselines': {
            v: [r['id'] for r in results if r.get('baseline') == v]
            for v in ('REPRODUCES', 'STALE_EXCLUDED', 'FAILS', 'NO_BASELINE', 'ERROR')
        },
        'rows_with_errors': errors,
    }
    with open(OUT, encoding='utf-8') as fh:
        blob = json.load(fh)
    blob['status'] = 'COMPLETE' if not errors else 'COMPLETE_WITH_ERRORS'
    blob['summary'] = summary
    with open(OUT, 'w', encoding='utf-8') as fh:
        json.dump(blob, fh, ensure_ascii=False, indent=2)

    print('\n=== by population')
    for p, v in by_pop.items():
        print(f"  {p:<14} n={v['n']:<3} fact sets differ {v['sets_differ']:<3} "
              f"replies differ {v['replies_differ']}")
    print(f"=== determinism control: {summary['determinism_control']['identical_fact_sets']} "
          f"identical-set rows, {len(nondet)} nondeterministic {nondet}")
    print(f"=== R24 baselines: " + ', '.join(
        f'{k}={len(v)}' for k, v in summary['r24_baselines'].items()))
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()
