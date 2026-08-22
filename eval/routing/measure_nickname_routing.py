# -*- coding: utf-8 -*-
"""Measure WHERE the nicknamed-levy routing gap actually is, before anything is built.

No model calls, no deploy — pure inspection of the deterministic routing stack, so it can be
re-run by anyone in a second. Answers four questions the routing-extension scoping needs:

  1. Does `_natural_levy` resolve the nickname at all, and to WHICH levy (it is first-match
     over `_LEVY_CUES`, so cue ORDER decides which levy survives a multi-nickname question)?
  2. Which gate in `detect_intent` blocks the ones that fall through — the number test, the
     payroll-context test, the money-ask test, or the applicability test?
  3. Can `_fan_out_multi_levy` ever see a nicknamed levy? It fans out on
     `all_explicit_levies`, for which there is no natural-cue counterpart.
  4. On the rows that route to `fact`, which fidelity guards are even reachable?

R18: committed before its result is written up. Artifact:
eval/results/nickname_routing_measurement.json
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)

from chike import decomposition, routing  # noqa: E402

PROBES = os.path.join(HERE, 'nickname_probes.jsonl')
OUT = os.path.join(REPO, 'eval', 'results', 'nickname_routing_measurement.json')


def gate_trace(text):
    """Reproduce detect_intent's gates individually so the BLOCKING one is named."""
    ql = text.lower()
    return {
        'has_number': routing._has_number(ql),
        'payroll_ctx': any(c in ql for c in routing._PAYROLL_CTX),
        'has_money_ask': routing._has_money_ask(ql),
        'is_applicability': routing.is_applicability_question(text),
        'has_money_magnitude': routing._has_money_magnitude(ql),
        'count_transition': bool(routing._COUNT_TRANSITION.search(ql)),
        'derive_cue': bool(routing._DERIVE_CUE.search(ql)),
        'explicit_levy': routing._explicit_levy(ql),
        'all_explicit_levies': routing.all_explicit_levies(text),
        'natural_levy_first_match': routing._natural_levy(ql),
        'natural_levies_all_matching': [
            levy for levy, cues in routing._LEVY_CUES if any(c in ql for c in cues)
        ],
    }


def blocking_gate(t, intent):
    """Name the gate that kept a probe off the compute path.

    Mirrors detect_intent's arms in order. An earlier version of this function reported
    path-2's message for probes that were really blocked in path 1, which mislabelled the
    EXPLICIT-levy control (nick_03) as 'no levy cue resolved' when the levy was named
    outright. Fixed before any result was written up; the bug is recorded here rather than
    silently corrected, because a mislabelled instrument is the failure this cycle is about.
    """
    if intent != 'none':
        return None

    # --- path 1: explicit levy + number + a compute-intent cue ---
    if t['explicit_levy']:
        if not t['has_number']:
            return 'path1: explicit levy named but no number'
        if not (t['has_money_ask'] or t['is_applicability'] or t['has_money_magnitude']
                or t['count_transition'] or t['derive_cue']):
            return ('path1: explicit levy + number, but NO compute-intent cue '
                    '(no money-ask, not applicability, no magnitude, no count-transition, '
                    'no derivation cue)')

    # --- paths 2 / 2b: natural cue + number + payroll context + (money-ask | applicability) ---
    if not t['natural_levy_first_match']:
        return 'path2/2b: no levy CUE resolved (levy may still be named explicitly)'
    if not t['has_number']:
        return 'path2/2b: no number'
    if not t['payroll_ctx']:
        return 'path2/2b: no payroll context'
    if not t['has_money_ask'] and not t['is_applicability']:
        return 'path2: no money-ask AND path2b: not an applicability question'
    return 'unclassified — gates look satisfied; inspect detect_intent directly'


def main():
    rows = []
    with open(PROBES, encoding='utf-8') as f:
        probes = [json.loads(line) for line in f if line.strip()]

    for p in probes:
        q = p['question']
        subs = decomposition.decompose_query(q)
        intent = routing.detect_intent(q)
        t = gate_trace(q)

        # Would the orchestrator's fan-out fire? It requires kind=='compute' AND
        # >=2 EXPLICIT levies. Nicknames are invisible to it by construction.
        would_fan_out = intent in routing.COMPUTE_TYPES and len(t['all_explicit_levies']) >= 2
        dropped = [lv for lv in t['natural_levies_all_matching'] if lv != intent]

        rows.append({
            'id': p['id'],
            'family': p['family'],
            'question': q,
            'expect_levy': p['expect_levy'],
            'note': p.get('note', ''),
            'guards_against': p.get('guards_against', ''),
            'n_subquestions': len(subs),
            'detect_intent': intent,
            'routes_to': 'compute' if intent in routing.COMPUTE_TYPES else (
                'clarify' if intent == 'ambiguous_multi' else 'fact'),
            'gates': t,
            'blocking_gate': blocking_gate(t, intent),
            'fan_out_would_fire': would_fan_out,
            'nicknamed_levies_dropped': dropped,
        })

    compute = [r for r in rows if r['routes_to'] == 'compute']
    fact = [r for r in rows if r['routes_to'] == 'fact']
    out = {
        'measured': '2026-08-22',
        'purpose': 'locate the nicknamed-levy routing gap before scoping a fix',
        'harness': 'eval/routing/measure_nickname_routing.py',
        'probes': 'eval/routing/nickname_probes.jsonl',
        'summary': {
            'total': len(rows),
            'routes_compute': len(compute),
            'routes_fact': len(fact),
            'fan_out_fires_anywhere': sum(1 for r in rows if r['fan_out_would_fire']),
            'rows_with_a_dropped_nicknamed_levy': [
                r['id'] for r in rows if r['nicknamed_levies_dropped']],
            'blocking_gates': sorted({
                r['blocking_gate'] for r in rows if r['blocking_gate']}),
        },
        'rows': rows,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    for r in rows:
        drop = f" DROPS={r['nicknamed_levies_dropped']}" if r['nicknamed_levies_dropped'] else ''
        blk = f" | blocked: {r['blocking_gate']}" if r['blocking_gate'] else ''
        print(f"{r['id']:8} {r['routes_to']:8} intent={r['detect_intent']:16}"
              f" fanout={r['fan_out_would_fire']}{drop}{blk}")
    print(f"\n[saved] {OUT}")
    print(json.dumps(out['summary'], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
