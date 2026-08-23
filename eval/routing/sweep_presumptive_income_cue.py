# -*- coding: utf-8 -*-
"""R17 sweep for the presumptive `kodi ya mapato` cue gap.

THE GAP, measured 2026-08-23 by eval/coverage/rerun_coverage_12.py:

    "Nina duka dogo, mauzo yangu ni milioni 30 kwa mwaka. Nalipa KODI YA MAPATO kiasi gani?"
        -> route `none`   (the fact path, no engine)
    "Biashara yangu inauza milioni 4 kwa mwaka, KODI YA MAKADIRIO ni ngapi?"
        -> route `presumptive`

`_BUSINESS_INCOME_TAX_CUES` requires "kodi ya mapato YA BIASHARA / YA DUKA". Bare "kodi ya
mapato" with a turnover figure and a shop in the sentence is not enough. **An engine reachable
only by the technical term serves the users who least need it** — a duka owner does not know
that `makadirio` is the word that works.

WHY THIS CUE NEEDS A SWEEP AND NOT JUST AN ADDITION. `kodi ya mapato` is the general Swahili
term for income tax. It appears in PAYE questions, corporate-tax questions and definition
questions. The route's guard is a conjunction — turnover cue AND money magnitude AND no veto —
which is strong, but it has a hole this cue would open:

    PRESUMPTIVE IS A REGIME FOR ONE RESIDENT INDIVIDUAL (First Schedule para 2). A COMPANY pays
    30% on PROFIT. And `_PRESUMPTIVE_TURNOVER_CUES` contains "nauza", which is a SUBSTRING of
    "i-nauza" — so "Kampuni yangu INAUZA bidhaa za milioni 50" already satisfies the turnover
    gate. Adding bare "kodi ya mapato" would route that company to the individual table and
    return a confidently wrong figure with the engine's authority behind it.

So this sweep measures TWO things, not one: the blast radius of the cue, and whether an entity
veto is required alongside it. Per R17 the corpus sweep is necessary and NOT sufficient — the
authored probes in presumptive_income_cue_probes.jsonl are the half that can find what the
corpus never exercises, and the majority of them are deliberately CORRECT bodies that must keep
their current route.

R18: committed before its result is written up.
Artifact: eval/results/presumptive_income_cue_sweep.json
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, 'eval', 'coverage'))

from chike import decomposition, routing                                    # noqa: E402
from measure_coverage_gate_signals import load_corpora                      # noqa: E402

OUT = os.path.join(REPO, 'eval', 'results', 'presumptive_income_cue_sweep.json')
PROBES = os.path.join(HERE, 'presumptive_income_cue_probes.jsonl')

CANDIDATE_CUE = 'kodi ya mapato'


def route_of(text):
    parts = decomposition.decompose_query(text)
    intents = [routing.detect_intent(p) for p in parts]
    return next((i for i in intents if i != 'none'), 'none')


def with_patch(cue_on, veto_on):
    """Install the requested arm, yielding the same code path with one variable changed.

    RE-RUNNABLE AFTER THE SHIP, which is the point. Both mechanisms are now in routing.py, so
    each arm is built by ADDING OR REMOVING them from the live module rather than by bolting a
    local copy on top. `before` genuinely reconstructs the pre-change router; a sweep that can
    only be run once, before the commit, is a result nobody can re-derive (R18).

    The entity veto is composed from `_PRESUMPTIVE_ENTITY_VETO_PATTERN`, kept separate in
    routing.py precisely so this function can subtract exactly that arm.
    """
    import re as _re
    orig_cues = list(routing._BUSINESS_INCOME_TAX_CUES)
    orig_veto = routing._PRESUMPTIVE_VETO

    if cue_on:
        if CANDIDATE_CUE not in routing._BUSINESS_INCOME_TAX_CUES:
            routing._BUSINESS_INCOME_TAX_CUES.append(CANDIDATE_CUE)
    else:
        routing._BUSINESS_INCOME_TAX_CUES[:] = [
            c for c in orig_cues if c != CANDIDATE_CUE]

    pattern = routing._PRESUMPTIVE_SCHEDULE_VETO_PATTERN
    if veto_on:
        pattern += r'|' + routing._PRESUMPTIVE_ENTITY_VETO_PATTERN
    routing._PRESUMPTIVE_VETO = _re.compile(pattern)
    return orig_cues, orig_veto


def restore(orig_cues, orig_veto):
    routing._BUSINESS_INCOME_TAX_CUES[:] = orig_cues
    routing._PRESUMPTIVE_VETO = orig_veto


def load_probes():
    rows = []
    with open(PROBES, encoding='utf-8') as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    assert rows, 'probe file is empty — a sweep with no authored arm is exactly what R17 forbids'
    return rows


def main():
    corpora = load_corpora()
    probes = load_probes()
    corpora['authored_probes'] = [{'id': p['id'], 'q': p['question'],
                                   'subdomain': p.get('guards_against')} for p in probes]

    arms = {'before': (False, False), 'cue_only': (True, False), 'cue_plus_veto': (True, True)}
    routes = {}
    for arm, (cue_on, veto_on) in arms.items():
        oc, ov = with_patch(cue_on, veto_on)
        try:
            routes[arm] = {name: {r['id']: route_of(r['q']) for r in rows}
                           for name, rows in corpora.items()}
        finally:
            restore(oc, ov)

    changes = {}
    for name, rows in corpora.items():
        for arm in ('cue_only', 'cue_plus_veto'):
            moved = []
            for r in rows:
                b = routes['before'][name][r['id']]
                a = routes[arm][name][r['id']]
                if a != b:
                    moved.append({'id': r['id'], 'q': r['q'], 'from': b, 'to': a})
            changes.setdefault(arm, {})[name] = moved

    # Probe verdicts: each probe declares the route it must end at.
    probe_results = {}
    for arm in ('before', 'cue_only', 'cue_plus_veto'):
        rows = []
        for p in probes:
            got = routes[arm]['authored_probes'][p['id']]
            rows.append({'id': p['id'], 'expected': p['expect_route'], 'got': got,
                         'pass': got == p['expect_route'], 'question': p['question'],
                         'guards_against': p['guards_against']})
        probe_results[arm] = {
            'passed': sum(1 for r in rows if r['pass']), 'n': len(rows),
            'failures': [r for r in rows if not r['pass']],
        }

    out = {
        'measured': '2026-08-23',
        'harness': 'eval/routing/sweep_presumptive_income_cue.py',
        'probe_file': 'eval/routing/presumptive_income_cue_probes.jsonl',
        'candidate_cue': CANDIDATE_CUE,
        'entity_veto_pattern': routing._PRESUMPTIVE_ENTITY_VETO_PATTERN,
        'corpora': {k: len(v) for k, v in corpora.items()},
        'blast_radius': {arm: {name: len(m) for name, m in per.items()}
                         for arm, per in changes.items()},
        'changes': changes,
        'probe_results': probe_results,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print('corpora:', json.dumps(out['corpora']))
    print('\n--- blast radius (rows whose route changes) ---')
    for arm, per in out['blast_radius'].items():
        print(f'  {arm:<16}{json.dumps(per)}')
    print('\n--- authored probes ---')
    for arm, res in probe_results.items():
        print(f"  {arm:<16}{res['passed']}/{res['n']} pass")
        for f_ in res['failures']:
            print(f"      FAIL {f_['id']}: expected {f_['expected']}, got {f_['got']}")
            print(f"           {f_['question'][:88]}")
    print('\n--- corpus rows that MOVE, cue_plus_veto ---')
    for name, moved in changes['cue_plus_veto'].items():
        for m in moved:
            if name == 'authored_probes':
                continue
            print(f"  {name:<14}{m['id']:<12}{m['from']} -> {m['to']}   {m['q'][:70]}")
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()
