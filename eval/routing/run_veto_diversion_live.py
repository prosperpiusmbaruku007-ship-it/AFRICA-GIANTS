# -*- coding: utf-8 -*-
"""ARM 2: run the veto-diverted set through live production and record what the fact path says.

Arm 1 (`measure_veto_diversion.py`) enumerated 17 questions that reach the fact path BECAUSE a
compute-path guard declined them. Enumeration is not harm: the fact path answers plenty of things
correctly, and for several of these it is the CORRECT home — a rate confirmation or a deadline
has nothing to compute.

So this arm fetches the actual replies, alongside the expected answer where the corpus carries
one (`correct_answer_sw` on the accuracy-gate rows), so the adjudication that follows is grounded
against a recorded expectation rather than resting on judgement alone. **The adjudication itself
is Claude Code's judgement and is labelled as such in the artifact — it is not a scorer output.**

WHY THE EXPECTED ANSWER MATTERS MORE HERE THAN USUAL. Eight of the seventeen are adversarial
FALSE-PREMISE confirmations — *"Kiwango cha WCF ni asilimia 3.5 ya mishahara, sivyo?"*, *"Kizingiti
cha SDL ni wafanyakazi 4, sivyo?"* — where the only wrong answer that matters is agreeing with the
premise. A reply can look fluent, on-topic and confident and still be a total failure, and no
figure-presence heuristic detects that.

R16: writes its artifact directly; no truncating console consumer between the run and the file.
R18: committed before it runs.

Artifact: eval/results/veto_diversion_live.json
"""
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import modal  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
POP = os.path.join(REPO, 'eval', 'results', 'veto_diversion_population.json')
OUT = os.path.join(REPO, 'eval', 'results', 'veto_diversion_live.json')

GATE_FILES = ['eval/accuracy_gate/eval_questions_001.jsonl',
              'eval/accuracy_gate/eval_questions_002_additions.jsonl',
              'eval/accuracy_gate/eval_questions_003.jsonl']


def expected_answers():
    out = {}
    for p in GATE_FILES:
        with open(os.path.join(REPO, p), encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    out[r['id']] = {'sw': r.get('correct_answer_sw'),
                                    'en': r.get('correct_answer_en'),
                                    'subdomain': r.get('subdomain')}
    return out


def main():
    with open(POP, encoding='utf-8') as f:
        pop = json.load(f)
    rows_in = pop['diverted']
    assert rows_in, 'the diverted population is empty — arm 1 must run first'
    exp = expected_answers()

    ChikeModel = modal.Cls.from_name('chike-inference', 'ChikeModel')
    rows = []
    for r in rows_in:
        print(f"\n=== {r['corpus']} / {r['id']} "
              f"[{','.join(c['mechanism'] for c in r['causes'])}] ===")
        print(f"Q: {r['question']}")
        e = exp.get(r['id'], {})
        rec = {'id': r['id'], 'corpus': r['corpus'], 'question': r['question'],
               'causes': r['causes'], 'subdomain': r.get('subdomain'),
               'expected_sw': e.get('sw'), 'expected_en': e.get('en'),
               'would_have_routed_to': [c['would_have_routed_to'] for c in r['causes']]}
        t0 = time.time()
        try:
            resp = ChikeModel().run.remote(r['question'])
            rec['reply'] = resp.get('reply', resp) if isinstance(resp, dict) else str(resp)
            print(f"A: {rec['reply']}")
            if e.get('sw'):
                print(f"EXPECTED: {e['sw'][:220]}")
        except Exception as ex:
            rec['error'] = f'{type(ex).__name__}: {ex}'
            print(f"ERROR: {rec['error']}")
        rec['elapsed_s'] = round(time.time() - t0, 1)
        rows.append(rec)

    out = {
        'measured': '2026-08-23',
        'harness': 'eval/routing/run_veto_diversion_live.py',
        'population_artifact': 'eval/results/veto_diversion_population.json',
        'target': 'live chike-inference, pipeline as deployed',
        'adjudication': 'PENDING — verdicts are Claude Code JUDGEMENT, added in a follow-up '
                        'commit against `expected_sw` where the corpus carries one.',
        'n': len(rows),
        'rows': rows,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f'\n[saved] {OUT}  ({len(rows)} rows)')


if __name__ == '__main__':
    main()
