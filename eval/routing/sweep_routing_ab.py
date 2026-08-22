# -*- coding: utf-8 -*-
"""R17 sweep for ROUTING-GAP-A and ROUTING-GAP-B: what else changes?

Compares routing BEFORE and AFTER the change across every corpus this project has, and
reports EVERY question whose route changes — not just the ones the change targets. Per §5(d),
a mechanism is not safe because its target rows improved; it is safe when its blast radius is
enumerated.

BEFORE is reconstructed in-process by monkeypatching the three new mechanisms back off
(all_compute_levies -> all_explicit_levies, and the two new applicability regexes -> never
match), so both arms run against the same corpus in the same interpreter and no stale artifact
can drift out of sync with the code.

Reports two different things, deliberately separated:
  * INTENT CHANGES  — detect_intent's answer changed (fact <-> compute, or a different levy)
  * FANOUT CHANGES  — detect_intent is unchanged but the compute part now fans into >1 levy

R18: committed before its result is written up.
Artifact: eval/results/routing_ab_sweep.json
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)

from chike import routing  # noqa: E402

OUT = os.path.join(REPO, 'eval', 'results', 'routing_ab_sweep.json')


def corpora():
    """Every question the project can sweep, tagged by source."""
    rows = []
    for sub in ('accuracy_gate', 'refusal_gate'):
        d = os.path.join(REPO, 'eval', sub)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if not name.endswith('.jsonl'):
                continue
            with open(os.path.join(d, name), encoding='utf-8') as f:
                for i, line in enumerate(f):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        row = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    q = row.get('question') or row.get('question_sw') or row.get('text')
                    if q:
                        rows.append({'source': f'{sub}/{name}',
                                     'id': row.get('id', f'{name}:{i}'), 'question': q})
    # The authored nickname probes, including the four R17 adversarial/negative controls.
    p = os.path.join(HERE, 'nickname_probes.jsonl')
    if os.path.exists(p):
        with open(p, encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    row = json.loads(line)
                    rows.append({'source': 'routing/nickname_probes.jsonl',
                                 'id': row['id'], 'question': row['question'],
                                 'guards_against': row.get('guards_against', ''),
                                 'family': row.get('family', '')})
    return rows


NEVER = re.compile(r'(?!)')  # matches nothing


def route_snapshot(rows):
    out = {}
    for r in rows:
        intent = routing.detect_intent(r['question'])
        levies = (routing.all_compute_levies(r['question'])
                  if intent in routing.COMPUTE_TYPES else [])
        out[r['id']] = {
            'intent': intent,
            'kind': 'compute' if intent in routing.COMPUTE_TYPES else (
                'clarify' if intent == 'ambiguous_multi' else 'fact'),
            'fanout': levies if len(levies) >= 2 else [],
        }
    return out


def main():
    rows = corpora()
    by_id = {r['id']: r for r in rows}

    after = route_snapshot(rows)

    # --- reconstruct BEFORE: disable ALL FOUR new mechanisms in place ---
    # The fourth (_GAP_B_APPLICABILITY_CUES) was missed by the first version of this sweep,
    # which reported a zero blast radius for the 'je nalipa' form because both arms had it
    # switched on. A sweep that cannot turn the change off measures nothing — the exact
    # false-clean-sweep R17 warns about, found here by noticing that two probes which SHOULD
    # have moved were reported unchanged.
    saved = (routing.all_compute_levies, routing._WHICH_LEVY_ASK,
             routing._RATE_BASE_ASK, routing._APPLICABILITY_CUES)
    routing.all_compute_levies = routing.all_explicit_levies
    routing._WHICH_LEVY_ASK = NEVER
    routing._RATE_BASE_ASK = NEVER
    routing._APPLICABILITY_CUES = [c for c in routing._APPLICABILITY_CUES
                                   if c not in routing._GAP_B_APPLICABILITY_CUES]
    assert len(routing._APPLICABILITY_CUES) == len(saved[3]) - len(
        routing._GAP_B_APPLICABILITY_CUES), 'BEFORE arm did not actually disable the cues'
    try:
        before = route_snapshot(rows)
        # PREVENTIVE RULE (2026-08-22): a BEFORE arm must be asserted to REPRODUCE A KNOWN
        # PRE-CHANGE RESULT, not merely to differ from AFTER. These four routings were
        # measured on pristine code before any of this was written
        # (eval/results/nickname_routing_measurement.json). If the arm fails to reproduce
        # them it is not the pre-change state and its radius is meaningless.
        known_pre_change = {'nick_02': 'none', 'nick_03': 'none',
                            'nick_04': 'nssf', 'nick_08': 'sdl'}
        for pid, expected in known_pre_change.items():
            if pid in before:
                assert before[pid]['intent'] == expected, (
                    f'BEFORE arm is NOT the pre-change state: {pid} routed '
                    f"{before[pid]['intent']!r}, pristine code routed {expected!r}")
        assert before['nick_04']['fanout'] == [], (
            'BEFORE arm still has the gap-A fan-out enabled')
    finally:
        (routing.all_compute_levies, routing._WHICH_LEVY_ASK,
         routing._RATE_BASE_ASK, routing._APPLICABILITY_CUES) = saved

    intent_changes, fanout_changes = [], []
    for rid in before:
        b, a = before[rid], after[rid]
        rec = {'id': rid, 'source': by_id[rid]['source'],
               'question': by_id[rid]['question'],
               'guards_against': by_id[rid].get('guards_against', ''),
               'before': b, 'after': a}
        if b['intent'] != a['intent'] or b['kind'] != a['kind']:
            intent_changes.append(rec)
        elif b['fanout'] != a['fanout']:
            fanout_changes.append(rec)

    def tally(recs, key):
        out = {}
        for r in recs:
            k = r[key] if isinstance(r[key], str) else str(r[key])
            out[k] = out.get(k, 0) + 1
        return out

    out = {
        'measured': '2026-08-22',
        'harness': 'eval/routing/sweep_routing_ab.py',
        'change': 'ROUTING-GAP-A (fan out on nicknamed levies) + ROUTING-GAP-B '
                  '(je-nalipa applicability, which-levy ask, rate-base ask)',
        'questions_swept': len(rows),
        'sources': sorted({r['source'] for r in rows}),
        'intent_change_count': len(intent_changes),
        'fanout_change_count': len(fanout_changes),
        'intent_changes_by_source': tally(intent_changes, 'source'),
        'fanout_changes_by_source': tally(fanout_changes, 'source'),
        'intent_changes': intent_changes,
        'fanout_changes': fanout_changes,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"swept {len(rows)} questions across {len(out['sources'])} sources")
    print(f"INTENT changes: {len(intent_changes)}")
    for r in intent_changes:
        print(f"  {r['id']:<28} {r['before']['kind']:>7} {r['before']['intent']:<8}"
              f" -> {r['after']['kind']:>7} {r['after']['intent']:<8} [{r['source']}]")
        if r['guards_against']:
            print(f"       ⚠ guards_against: {r['guards_against']}")
    print(f"\nFANOUT changes: {len(fanout_changes)}")
    for r in fanout_changes:
        print(f"  {r['id']:<28} {r['before']['fanout']} -> {r['after']['fanout']}"
              f" [{r['source']}]")
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()
