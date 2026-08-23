# -*- coding: utf-8 -*-
"""Is D1 quantity-axis blindness, or is it the FALSE-PREMISE FRAME? One variable: the premise.

WHY THIS RUN EXISTS. The quantity-instruction candidates failed to improve arm P — and reading
the replies showed why: THE BASELINE WAS ALREADY MOSTLY RIGHT on those probes. `qi_p01`
("Mchango wa NSSF kwa jumla ni asilimia ngapi?") returns "asilimia 20 (10 mwajiri + 10
mfanyakazi)" with no instruction at all. Yet `eval_337` — the same axis, the same facts —
returns "asilimia 10".

The difference between them is not the quantity. It is that `eval_337` ASSERTS TWO WRONG VALUES
and asks for confirmation: "ni asilimia 3.5, au ni 0.5?". So do `eval_342` ("...ni asilimia 25,
sivyo?") and `eval_348` ("...sivyo?"). **All three specimens of the covered-half defect are
false-premise frames**, and the correction-shaped finding says replies to them are wrong in a way
users cannot detect.

HYPOTHESIS: the model anchors on refuting the asserted value and loses the rest of the question.
If so, D1 and D4 are not two defects but one, and the fix is not an instruction about quantities.

FOUR CALLS, ONE VARIABLE. Same facts, same wrapper, premise present vs absent, on two specimens.

FALSIFIER, named before running: if the premise-free variants are ALSO wrong, the premise is not
the variable and this hypothesis is dead.

R18: committed before it runs. Artifact: eval/results/premise_frame_test.json
"""
import json, os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)
import modal                                                                # noqa: E402
from chike import prompting                                                 # noqa: E402
from chike.retrieval import retrieve                                        # noqa: E402

OUT = os.path.join(REPO, 'eval', 'results', 'premise_frame_test.json')
ADAPTER = 'prospAprospA007/africa-giants-adapter-v15'

ARMS = [
    ('nssf_WITH_premise', 'Kiwango cha mchango wa NSSF ni asilimia 3.5, au ni 0.5?', '20'),
    ('nssf_NO_premise', 'Kiwango cha mchango wa NSSF ni asilimia ngapi ya mshahara?', '20'),
    ('paye_WITH_premise', 'Kiwango cha juu kabisa cha PAYE ni asilimia 25, sivyo?', '30'),
    ('paye_NO_premise', 'Kiwango cha juu kabisa cha PAYE ni asilimia ngapi?', '30'),
]

def main():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(ADAPTER, trust_remote_code=True)
    system = prompting.load_system_prompt()
    M = modal.Cls.from_name('chike-inference', 'ChikeModel')
    rows = []
    for name, q, expect in ARMS:
        facts = tuple(retrieve(q))
        prompt = prompting.build_chat_prompt(q, facts, system, tokenizer=tok)
        t0 = time.time()
        try:
            resp = M().generate_raw.remote(prompt)
            reply = resp.get('completion', resp) if isinstance(resp, dict) else str(resp)
            reply = str(reply).replace('<|end_of_text|>', '').strip()
        except Exception as e:
            reply = f'ERROR {type(e).__name__}: {e}'
        rows.append({'arm': name, 'question': q, 'expect': expect, 'reply': reply,
                     'n_facts': len(facts), 'elapsed_s': round(time.time() - t0, 1)})
        print(f'\n=== {name}\nQ: {q}\nA: {reply[:260]}')
    out = {'measured': '2026-08-23',
           'harness': 'eval/forced_facts/test_premise_frame.py',
           'hypothesis': 'the false-premise frame, not the quantity axis, is the variable',
           'falsifier': 'if the premise-free variants are also wrong, the hypothesis is dead',
           'rows': rows}
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f'\n[saved] {OUT}')

if __name__ == '__main__':
    main()
