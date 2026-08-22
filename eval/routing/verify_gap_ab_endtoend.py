# -*- coding: utf-8 -*-
"""Does the routing change DELIVER? Sub-answer shape for the newly-routed rows.

Routing them to compute is only worth anything if the engines then produce the right
deterministic workings. This runs the real Orchestrator with a FakeBackend (no GPU, no
network), so what is measured is the ROUTING + RULES-ENGINE half end to end — the model's
prose is stubbed out deliberately, because it is the deterministic working that carries the
answer on the compute path.

This is NOT the §5(d) answer-level bar. That needs a live R16 cycle against the deployed
pipeline and is the explicit next step; this is the local check that the change is worth
deploying at all.

R18: committed before its result is written up.
Artifact: eval/results/gap_ab_endtoend.json
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)

from chike.model_abstraction import FakeBackend  # noqa: E402
from chike.orchestrator import Orchestrator  # noqa: E402

OUT = os.path.join(REPO, 'eval', 'results', 'gap_ab_endtoend.json')

ROWS = [
    ('nat_23', 'nina wafanyakazi 12 mishahara jumla milioni 5.5 nitalipa ngapi kwenye '
               'ile ya mafunzo na ile ya uzeeni',
     'SDL 3.5% x 5,500,000 = 192,500 AND NSSF 20% x 5,500,000 = 1,100,000. '
     'Both levies, 12 >= 10 so SDL applies.'),
    ('nat_24', 'tuko na watu 9 tu mishahara milioni 4 kwa mwezi nilipe nini kati ya '
               'ile ya mafunzo ya fidia na ya uzeeni',
     'SDL must NOT apply (9 < 10); WCF 0.5% x 4,000,000 = 20,000; NSSF employer 10% = 400,000.'),
    ('nat_05', 'nimenunua mashine za kiwanda za milioni 50 na nina wafanyakazi 12 hiyo ya '
               'mafunzo nitalipa asilimia tatu na nusu ya nini',
     'Base is GROSS PAYROLL, never machine value. Correct = name the base and ask for it.'),
    ('edge_p10', 'nawalipa wafanyakazi watano jumla ya milioni 4 kwa mwezi nitalipa ngapi '
                 'kwa ile ya mafunzo na ya uzeeni kwa pamoja',
     'Unplanned beneficiary found by the sweep. 5 employees so SDL must NOT apply; '
     'NSSF 20% x 4,000,000 = 800,000.'),
    ('th_12', 'Nina wafanyakazi 9 — je nalipa SDL?',
     'Unplanned beneficiary. 9 < 10, so the answer is NO, deterministically.'),
]


def main():
    results = []
    for rid, question, expectation in ROWS:
        # Empty scripted prose: the compute path appends the engine's authoritative working
        # regardless of what the model says, so a blank body isolates the deterministic half.
        orch = Orchestrator(backend=FakeBackend(scripted_reply=''), retriever=lambda q: [])
        try:
            reply = orch.answer(question)
            rec = {
                'id': rid, 'question': question, 'expectation': expectation,
                'text': reply.text,
                'needs_clarification': reply.needs_clarification,
                'sub_answers': [{
                    'kind': getattr(sa.sub_question, 'kind', '?'),
                    'computation_type': getattr(sa.sub_question, 'computation_type', None),
                    'working': (sa.computation.working if sa.computation else None),
                    'needs_clarification': sa.needs_clarification,
                    'text': sa.text,
                } for sa in reply.sub_answers],
            }
        except Exception as e:
            rec = {'id': rid, 'question': question, 'expectation': expectation,
                   'error': f'{type(e).__name__}: {e}'}
        results.append(rec)

        print(f"\n=== {rid} ===")
        print(f"expect: {expectation}")
        if 'error' in rec:
            print(f"ERROR: {rec['error']}")
            continue
        for sa in rec['sub_answers']:
            print(f"  [{sa['kind']}/{sa['computation_type']}] "
                  f"clarify={sa['needs_clarification']} working={sa['working']!r}")
        print(f"  merged: {rec['text'][:220]!r}")

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump({'measured': '2026-08-22',
                   'harness': 'eval/routing/verify_gap_ab_endtoend.py',
                   'note': 'Orchestrator + FakeBackend; model prose stubbed so the '
                           'deterministic engine half is what is measured. NOT the §5(d) '
                           'live answer-level bar.',
                   'rows': results}, f, ensure_ascii=False, indent=2)
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()
