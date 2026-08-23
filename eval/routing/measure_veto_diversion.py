# -*- coding: utf-8 -*-
"""How many questions does a compute-path veto hand to the unguarded fact path? ARM 1: enumerate.

THE QUESTION, from the 2026-08-23 canary. Four rows that the router correctly kept OFF the rules
engine each received a confidently wrong answer from the fact path instead — corporate tax as 30%
of TURNOVER, a daladala given the turnover rate, 30% flat on an individual's profit, and a
partnership handed a PAYE computation on a TZS 2,500,000 monthly salary invented by dividing
annual turnover by twelve. **Four rows are a sample. A sample is not a rate.**

If this is a common shape rather than four cases, it is a larger live defect than anything on the
board, because it means every never-guess veto this project has shipped is a REDIRECTION rather
than a refusal.

WHAT THIS ARM DOES. It enumerates the population mechanically, with attribution, and nothing else.
For every corpus question that currently routes to `none` (the fact path), it re-routes with one
diversion mechanism disabled at a time and asks: **would this have been a COMPUTE question if that
guard had not fired?** If yes, the guard diverted it, and the guard is named.

THE FIVE MECHANISMS, each independently switchable:

  entity_veto        _PRESUMPTIVE_ENTITY_VETO_PATTERN — company/partnership out of para 2
  schedule_veto      _PRESUMPTIVE_SCHEDULE_VETO_PATTERN — transport table, regime-election
  vat_threshold_ask  _THRESHOLD_ASK_VETO — "what IS the threshold" vs "have I crossed it"
  foreign_currency   _FOREIGN_CURRENCY — a figure in a currency the engine will not convert
  path1_commitment   the path-1 conjunction: an EXPLICIT levy plus a number is not compute
                     intent unless there is a money ask, an applicability cue, a payroll
                     magnitude, a count transition or a derivation cue

path1_commitment IS A LOCAL RE-IMPLEMENTATION, not a patch — the guard is an inline conjunction
inside detect_intent with no switchable object to swap. It is written out here in full and must
be kept in step with routing.py; a test pins that. The other four are patched on the real module
objects and restored, so BEFORE and AFTER are the same code path with one variable changed.

WHAT THIS ARM DELIBERATELY DOES NOT DO. It does not judge any reply. Being diverted is not
evidence of harm — the fact path answers plenty of things correctly, and some vetoed questions
have good fact answers (a definition, a deadline). **Arm 2 runs the diverted set live and
adjudicates.** Reading a count here as a defect count would be exactly the presence-not-conclusion
error this file exists to help avoid.

R18: committed before its result is written up.
Artifact: eval/results/veto_diversion_population.json
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, 'eval', 'coverage'))

from chike import decomposition, routing                                    # noqa: E402
from measure_coverage_gate_signals import load_corpora                      # noqa: E402

OUT = os.path.join(REPO, 'eval', 'results', 'veto_diversion_population.json')
_NEVER = re.compile(r'(?!x)x')          # matches nothing


def route_of(text):
    parts = decomposition.decompose_query(text)
    intents = [routing.detect_intent(p) for p in parts]
    return next((i for i in intents if i != 'none'), 'none')


def _presumptive_veto(schedule=True, entity=True):
    pats = []
    if schedule:
        pats.append(routing._PRESUMPTIVE_SCHEDULE_VETO_PATTERN)
    if entity:
        pats.append(routing._PRESUMPTIVE_ENTITY_VETO_PATTERN)
    return re.compile('|'.join(pats)) if pats else _NEVER


def route_without(mechanism, text):
    """Re-route `text` with exactly one diversion mechanism disabled."""
    saved = (routing._PRESUMPTIVE_VETO, routing._THRESHOLD_ASK_VETO, routing._FOREIGN_CURRENCY)
    try:
        if mechanism == 'entity_veto':
            routing._PRESUMPTIVE_VETO = _presumptive_veto(schedule=True, entity=False)
        elif mechanism == 'schedule_veto':
            routing._PRESUMPTIVE_VETO = _presumptive_veto(schedule=False, entity=True)
        elif mechanism == 'vat_threshold_ask':
            routing._THRESHOLD_ASK_VETO = _NEVER
        elif mechanism == 'foreign_currency':
            routing._FOREIGN_CURRENCY = _NEVER
        else:
            raise ValueError(mechanism)
        return route_of(text)
    finally:
        (routing._PRESUMPTIVE_VETO, routing._THRESHOLD_ASK_VETO,
         routing._FOREIGN_CURRENCY) = saved


def path1_would_have_committed(text):
    """The path-1 commitment guard, written out — see the module docstring.

    Returns the levy path 1 would have returned had the guard not required a money ask (or an
    applicability cue, or a payroll magnitude, or a count transition, or a derivation cue).
    """
    for part in decomposition.decompose_query(text):
        ql = part.lower()
        explicit = routing._explicit_levy(ql)
        if not (explicit and routing._has_number(ql)):
            continue
        committed = (routing._has_money_ask(ql)
                     or routing.is_applicability_question(part)
                     or routing._has_money_magnitude(ql)
                     or routing._COUNT_TRANSITION.search(ql)
                     or routing._DERIVE_CUE.search(ql))
        if not committed:
            return explicit
    return None


MECHANISMS = ['entity_veto', 'schedule_veto', 'vat_threshold_ask', 'foreign_currency']


def main():
    corpora = load_corpora()
    # The presumptive probe set is included as its own corpus: it is where the four canary rows
    # live, so leaving it out would drop the very sample that prompted the question.
    with open(os.path.join(HERE, 'presumptive_income_cue_probes.jsonl'), encoding='utf-8') as f:
        corpora['presumptive_probes'] = [
            {'id': p['id'], 'q': p['question'], 'subdomain': 'probe'}
            for p in (json.loads(l) for l in f if l.strip())]

    diverted, per_corpus = [], {}
    for name, rows in corpora.items():
        counts = {'n': len(rows), 'fact_path': 0, 'diverted': 0}
        for r in rows:
            if route_of(r['q']) != 'none':
                continue
            counts['fact_path'] += 1
            causes = []
            for m in MECHANISMS:
                would = route_without(m, r['q'])
                if would != 'none':
                    causes.append({'mechanism': m, 'would_have_routed_to': would})
            p1 = path1_would_have_committed(r['q'])
            if p1:
                causes.append({'mechanism': 'path1_commitment',
                               'would_have_routed_to': p1})
            if causes:
                counts['diverted'] += 1
                diverted.append({'corpus': name, 'id': r['id'], 'question': r['q'],
                                 'subdomain': r.get('subdomain'),
                                 'verdict_2026_08_17': r.get('verdict'),
                                 'causes': causes})
        per_corpus[name] = counts

    by_mechanism = {}
    for d in diverted:
        for c in d['causes']:
            by_mechanism.setdefault(c['mechanism'], []).append(d['id'])

    out = {
        'measured': '2026-08-23',
        'harness': 'eval/routing/measure_veto_diversion.py',
        'question': 'how many fact-path questions are there BECAUSE a compute-path guard '
                    'declined them?',
        'method': 'per-question counterfactual: disable one diversion mechanism at a time and '
                  're-route. ENUMERATION ONLY — being diverted is not evidence of harm; arm 2 '
                  'runs these live and adjudicates.',
        'mechanisms': MECHANISMS + ['path1_commitment'],
        'per_corpus': per_corpus,
        'total_fact_path': sum(c['fact_path'] for c in per_corpus.values()),
        'total_diverted': len(diverted),
        'by_mechanism': {k: {'n': len(v), 'ids': v[:40]} for k, v in by_mechanism.items()},
        'diverted': diverted,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"fact-path questions: {out['total_fact_path']}")
    print(f"of which DIVERTED by a compute-path guard: {out['total_diverted']}")
    print('\n--- per corpus ---')
    for name, c in per_corpus.items():
        print(f"  {name:<20}{c['diverted']:>4} diverted of {c['fact_path']:>4} fact-path "
              f"(corpus {c['n']})")
    print('\n--- per mechanism ---')
    for m, v in sorted(by_mechanism.items(), key=lambda kv: -len(kv[1])):
        print(f"  {m:<20}{len(v):>4}")
    print('\n--- the diverted set ---')
    for d in diverted:
        ms = ','.join(c['mechanism'] for c in d['causes'])
        print(f"  {d['corpus']:<18}{str(d['id']):<12}{ms:<38}{d['question'][:62]}")
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()
