# -*- coding: utf-8 -*-
"""Measure the SHIPPED coverage gate against the FROZEN held-out probes and all four corpora.

THE POINT OF THE HELD-OUT SET. `eval/coverage/coverage_gate_heldout_040.jsonl` was authored and
committed BEFORE `chike/coverage.py` existed (c8b46a9), and no cue in the shipped list may be
tuned against the 48, the 400-question gate corpus or the 12. That is what makes the
false-refusal number below a MEASUREMENT rather than a fit — the distinction the scoping run
could not make about itself, because its cues and its corpora were read in the same sitting.

WHAT IS MEASURED, per part, exactly as production applies it:

  * routing first — a deterministic route means the gate never applies (compute results are
    grounded by construction, not by retrieval);
  * then `coverage.is_covered` on each fact part;
  * arm C additionally checks the two halves SEPARATELY: the covered part must survive and the
    uncovered part must be refused. Wholesale either way is a failure.

ONE CUE DIFFERS FROM THE SCOPED LIST, AND IT IS REPORTED SEPARATELY BECAUSE IT MUST BE. The
scoped allowlist carried bare `kodi ya mapato` under `paye`; the shipped list carries only the
qualified forms. That change came from LIVE evidence — the 2026-08-23 canary showed production
answering four different obligations phrased that way, three of them uncovered, each with an
invented figure — not from reading a corpus. It can only INCREASE the corpus false-refusal cost,
so the cost is re-measured here rather than carried over from scoping.

R18: committed before its result is written up.
Artifact: eval/results/coverage_gate_shipped.json
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)
sys.path.insert(0, HERE)

from chike import coverage, decomposition, routing                          # noqa: E402
from measure_coverage_gate_signals import load_corpora                      # noqa: E402

OUT = os.path.join(REPO, 'eval', 'results', 'coverage_gate_shipped.json')
HELDOUT = os.path.join(HERE, 'coverage_gate_heldout_040.jsonl')


def part_verdicts(text):
    """Per-part gate outcome, mirroring Orchestrator.answer.

    Returns a list of dicts, one per decomposed part.
    """
    out = []
    for part in decomposition.decompose_query(text):
        intent = routing.detect_intent(part)
        if intent != 'none':
            out.append({'part': part, 'route': intent, 'gated': False,
                        'refused': False, 'topics': []})
            continue
        topics = coverage.covered_topics(part)
        out.append({'part': part, 'route': 'none', 'gated': True,
                    'refused': not topics, 'topics': topics})
    return out


def message_refused(text):
    v = part_verdicts(text)
    return bool(v) and all(p['refused'] for p in v)


def main():
    with open(HELDOUT, encoding='utf-8') as f:
        probes = [json.loads(line) for line in f if line.strip()]
    assert len(probes) == 40, f'held-out set has {len(probes)} rows, expected 40'

    heldout_rows = []
    for p in probes:
        verdicts = part_verdicts(p['question'])
        all_ref = bool(verdicts) and all(v['refused'] for v in verdicts)
        any_ref = any(v['refused'] for v in verdicts)
        matched = [t for v in verdicts for t in v['topics']]

        if p['expect'] == 'pass':
            ok = not any_ref
            # A pass is only a GOOD pass if it matched the topic the question is actually
            # about. Passing via the wrong topic is a latent false negative — the shape the
            # 2026-08-23 canary caught live, where `kodi ya mapato` matched `paye` for four
            # different obligations.
            right_topic = p['true_topic'] in matched
        elif p['expect'] == 'refuse':
            ok = all_ref
            right_topic = None
        else:                                            # mixed
            ok = any_ref and not all_ref
            right_topic = None

        heldout_rows.append({
            'id': p['id'], 'arm': p['arm'], 'expect': p['expect'],
            'true_topic': p['true_topic'], 'question': p['question'],
            'parts': verdicts, 'all_refused': all_ref, 'any_refused': any_ref,
            'matched_topics': matched, 'pass': ok, 'matched_true_topic': right_topic,
            'refusal_text': (coverage.refusal_text(p['question']) if any_ref else None),
            'guards_against': p['guards_against'],
        })

    by_arm = {}
    for r in heldout_rows:
        a = by_arm.setdefault(r['arm'], {'n': 0, 'pass': 0, 'fail_ids': [],
                                         'wrong_topic_pass_ids': []})
        a['n'] += 1
        if r['pass']:
            a['pass'] += 1
        else:
            a['fail_ids'].append(r['id'])
        if r['matched_true_topic'] is False:
            a['wrong_topic_pass_ids'].append(r['id'])

    # --- corpus cost, re-measured against the SHIPPED list ---------------------------------
    corpora = load_corpora()
    corpus = {}
    for name, rows in corpora.items():
        refused, ooc_refused = [], []
        for r in rows:
            if not message_refused(r['q']):
                continue
            if r.get('subdomain') == 'out_of_corpus':
                ooc_refused.append(r['id'])
            else:
                refused.append({'id': r['id'], 'q': r['q'], 'verdict': r.get('verdict')})
        entry = {'n': len(rows), 'refused': len(refused),
                 'correctly_refused_ooc': len(ooc_refused),
                 'refused_rows': refused[:40]}
        if name == 'natural_48':
            entry['refused_that_were_CORRECT'] = sum(
                1 for x in refused if (x['verdict'] or '').startswith('CORRECT'))
        corpus[name] = entry

    false_refusals = (corpus['gate_400']['refused'] + corpus['inscope_69']['refused']
                      + corpus['natural_48']['refused_that_were_CORRECT'])

    out = {
        'measured': '2026-08-23',
        'harness': 'eval/coverage/measure_coverage_gate_shipped.py',
        'heldout_frozen_at': 'c8b46a9 — committed before chike/coverage.py existed',
        'n_topics': len(coverage.COVERED_TOPICS),
        'n_authorities': len(coverage.UNCOVERED_AUTHORITIES),
        'heldout_by_arm': by_arm,
        'heldout_total_pass': sum(1 for r in heldout_rows if r['pass']),
        'heldout_n': len(heldout_rows),
        'corpus_false_refusals_total': false_refusals,
        'corpus': corpus,
        'heldout_rows': heldout_rows,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"HELD-OUT: {out['heldout_total_pass']}/{out['heldout_n']}")
    for arm, a in sorted(by_arm.items()):
        print(f"  {arm:<34}{a['pass']}/{a['n']}"
              f"   fail={a['fail_ids']}"
              + (f"   wrong-topic pass={a['wrong_topic_pass_ids']}"
                 if a['wrong_topic_pass_ids'] else ''))
    print('\nCORPUS COST (shipped list)')
    for name, e in corpus.items():
        extra = (f"  correct-refused-as-CORRECT={e['refused_that_were_CORRECT']}"
                 if 'refused_that_were_CORRECT' in e else '')
        print(f"  {name:<14}refused {e['refused']:>3}/{e['n']:<4} "
              f"(ooc correctly refused {e['correctly_refused_ooc']}){extra}")
    print(f"\n  false refusals total: {false_refusals}")
    print('\n--- sample refusal copy ---')
    for rid in ('hoB_billboard', 'hoB_water_permit', 'hoD_company_tax'):
        row = next((r for r in heldout_rows if r['id'] == rid), None)
        if row and row['refusal_text']:
            print(f"  {rid}: {row['refusal_text']}")
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()
