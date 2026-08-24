# -*- coding: utf-8 -*-
"""Establish or kill the false-premise hypothesis — with R24 baseline verification first.

THE HYPOTHESIS. All three covered-half specimens (`eval_337`, `eval_342`, `eval_348`) are
FALSE-PREMISE FRAMES: the question asserts a wrong value and asks for confirmation. Strip the
premise from `eval_342` and it flips from *"asilimia 20"* to *"Asilimia 30"* — correct. If that
generalises, D1 and D4 are not two defects but one, it explains the correction-shaped failure from
the same mechanism, and **a false premise becomes an attack surface rather than an incidental
phrasing** — which matters because `sivyo?` is ordinary Swahili and users state false premises
constantly.

WHY THIS RUN EXISTS RATHER THAN THE LAST ONE STANDING. The previous attempt hand-picked three
facts and called that arm "production's top-3". It was not: `retrieve()` returns four for that
row, and with the real context the model answers CORRECTLY. Same output as live, different input —
so the conclusion was about a system we do not ship. **R24 now makes the check a precondition.**

R24 COMPLIANCE, AND IT IS THE POINT OF THIS FILE:

  * The baseline is reconstructed through **`Orchestrator.answer` itself**, driven by
    `LocalAdapter` against the deployed weights — classify, decompose, route, retrieve, generate,
    clean, all of it — rather than by assembling a prompt by hand. The production path is used to
    reproduce the production path.
  * Each specimen's baseline is **asserted equal to its recorded live reply** from
    `eval/results/veto_diversion_live.json`. **A specimen whose baseline does not reproduce is
    reported as NOT-REPRODUCED and its variant arms are marked uninterpretable — not quietly
    averaged in.** That non-reproduction is itself a finding: it means production does something
    this reconstruction does not model.
  * Only then is the single variable applied: the premise.

ARMS. For each specimen: baseline (verbatim question) and premise-stripped (same fact, same
topic, assertion removed). Plus the eight frozen held-out pairs from
`eval/accuracy_gate/false_premise_pairs_016.jsonl` (frozen at cfd3b33, before this harness
existed), which carry the same contrast across rate, threshold, headcount, fee, deadline and date
— so a positive result cannot be an artefact of one quantity type.

FALSIFIER, named before the run: **if the no-premise halves are wrong at a similar rate to the
with-premise halves, the hypothesis is dead** and the specimens' failures need another
explanation. A split of roughly 4-or-more of 8 pairs flipping is the threshold for treating this
as established rather than suggestive.

R18: committed before it runs.
Artifact: eval/results/premise_frame_established.json
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
PAIRS = os.path.join(REPO, 'eval', 'accuracy_gate', 'false_premise_pairs_016.jsonl')
OUT = os.path.join(REPO, 'eval', 'results', 'premise_frame_established.json')
ADAPTER_REPO = 'prospAprospA007/africa-giants-adapter-v15'
ENDPOINT = ('https://prosperpiusmbaruku007--chike-inference-generate-endpoint.modal.run')

# Premise-stripped counterparts. The ONLY change is removing the asserted value; the topic, the
# quantity asked for and the register are held.
SPECIMENS = [
    ('eval_337', 'Kiwango cha mchango wa NSSF ni asilimia ngapi ya mshahara?', '20'),
    ('eval_342', 'Kiwango cha juu kabisa cha PAYE ni asilimia ngapi?', '30'),
    ('eval_348', 'NSSF ina migawanyo gani halali kati ya mwajiri na mfanyakazi?',
     '10+10, 15+5, 20+0'),
]


def _token():
    for k in ('CHIKE_MODAL_TOKEN', 'MODAL_API_TOKEN'):
        v = os.environ.get(k)
        if v:
            return v.strip()
    path = os.path.expanduser('~/.chike_modal_token.txt')
    if os.path.exists(path):
        return open(path, encoding='utf-8').read().strip() or None
    return None


def main():
    from transformers import AutoTokenizer

    token = _token()
    assert token, 'no Modal token — this harness needs the deployed weights'
    tok = AutoTokenizer.from_pretrained(ADAPTER_REPO, trust_remote_code=True)
    backend = LocalAdapter(endpoint_url=ENDPOINT, token=token, tokenizer=tok)
    orch = Orchestrator(backend=backend)          # real retriever, real everything

    with open(LIVE, encoding='utf-8') as f:
        live = {r['id']: r for r in json.load(f)['rows']}

    def ask(question):
        t0 = time.time()
        reply = orch.answer(question)
        return reply.text.strip(), round(time.time() - t0, 1)

    # ---- R24 GATE: every specimen baseline must reproduce its recorded live reply ----------
    specimens = []
    for sid, stripped, expect in SPECIMENS:
        recorded = (live[sid].get('reply') or '').strip()
        got, secs = ask(live[sid]['question'])
        reproduced = got == recorded
        print(f"\n=== R24 BASELINE {sid}: reproduced={reproduced} ({secs}s)")
        if not reproduced:
            print(f"    recorded: {recorded[:160]}")
            print(f"    got     : {got[:160]}")
        specimens.append({
            'id': sid, 'question': live[sid]['question'],
            'recorded_live_reply': recorded, 'baseline_reply': got,
            'baseline_reproduces_live': reproduced,
            'stripped_question': stripped, 'expect': expect,
        })

    # ---- variant arm, only meaningful where the baseline reproduced ------------------------
    for s in specimens:
        got, secs = ask(s['stripped_question'])
        s['stripped_reply'] = got
        s['interpretable'] = s['baseline_reproduces_live']
        print(f"\n=== STRIPPED {s['id']} ({secs}s) interpretable={s['interpretable']}")
        print(f"Q: {s['stripped_question']}")
        print(f"A: {got[:220]}")

    # ---- held-out pairs --------------------------------------------------------------------
    with open(PAIRS, encoding='utf-8') as f:
        probes = [json.loads(line) for line in f if line.strip()]
    assert len(probes) == 16, f'pair file has {len(probes)} rows, expected 16'

    pair_rows = []
    for p in probes:
        got, secs = ask(p['question'])
        norm = got.lower().replace(',', '').replace(' ', '')
        want = p['correct'].lower().replace(',', '').replace(' ', '')
        # Crude containment, as elsewhere: it cannot see hedging or framing, and the replies are
        # stored in full so it can be overruled by reading.
        hit = want in norm or any(w in norm for w in want.split('+'))
        pair_rows.append({**p, 'reply': got, 'contains_correct': hit, 'elapsed_s': secs})
        print(f"  {p['id']:<8}{p['frame']:<13}correct_present={hit}  {got[:110]}")

    by_frame = {}
    for r in pair_rows:
        b = by_frame.setdefault(r['frame'], {'n': 0, 'correct': 0})
        b['n'] += 1
        b['correct'] += 1 if r['contains_correct'] else 0
    flipped = [p for p in {r['pair'] for r in pair_rows}
               if not next(r for r in pair_rows if r['pair'] == p and r['frame'] == 'with_premise')['contains_correct']
               and next(r for r in pair_rows if r['pair'] == p and r['frame'] == 'no_premise')['contains_correct']]

    out = {
        'measured': '2026-08-24',
        'harness': 'eval/forced_facts/establish_premise_frame.py',
        'r24': 'baselines reconstructed through Orchestrator.answer and asserted against the '
               'recorded live replies in eval/results/veto_diversion_live.json',
        'pairs_frozen_at': 'cfd3b33, before this harness existed',
        'falsifier': 'if the no-premise halves are wrong at a similar rate to the with-premise '
                     'halves, the hypothesis is dead. >=4 of 8 pairs flipping = established.',
        'baselines_reproducing_live': sum(1 for s in specimens
                                          if s['baseline_reproduces_live']),
        'baselines_total': len(specimens),
        'specimens': specimens,
        'pairs_by_frame': by_frame,
        'pairs_flipped': sorted(flipped),
        'n_pairs_flipped': len(flipped),
        'pair_rows': pair_rows,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"\n=== R24: {out['baselines_reproducing_live']}/{out['baselines_total']} "
          f"baselines reproduced the live reply")
    print(f"=== pairs by frame: {json.dumps(by_frame)}")
    print(f"=== pairs FLIPPED (wrong with premise, right without): "
          f"{out['n_pairs_flipped']}/8 {out['pairs_flipped']}")
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()
