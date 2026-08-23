# -*- coding: utf-8 -*-
"""Choose the quantity instruction BY MEASUREMENT on frozen held-out probes, not by wording taste.

WHY THIS IS NOT JUST 'ADD A4'S SENTENCE'. The separation run fixed `eval_337` with
*" Nataka JUMLA ya mchango (mwajiri pamoja na mfanyakazi), si sehemu ya upande mmoja."* appended to
the question. **That sentence names the answer's shape for that one question** — it is not a
mechanism, it is a hint. A shippable change is a GENERAL instruction in the system prompt (R14),
and whether a general instruction reproduces A4's result is a separate empirical question. Assuming
it does is the reach-versus-benefit error that has already cost this project two cycles.

THE PROBES WERE FROZEN FIRST — `eval/accuracy_gate/quantity_instruction_heldout_024.jsonl` at
`121b128`, before any candidate wording existed. That ordering is the only thing that makes the
numbers below a measurement rather than a fit (R21).

  ARM P (10) the total-versus-share axis, DEMANDING DIFFERENT ANSWERS FROM THE SAME FACTS —
             `qi_p01` wants 20, `qi_p02`/`qi_p03` want 10 from opposite parties, `qi_p05` is a
             levy with no split, `qi_p07` is true on both sides. **A candidate that fixes the
             total by biasing toward totals breaks four of these**, which is the whole point of
             authoring the arm this way.
  ARM N (14) no party axis at all. An instruction runs on EVERY generation, so this is where its
             blast radius is priced. Any regression here is a cost the fix must justify.

CANDIDATES, three, differing in one dimension each — how much they SAY versus how much they
CONSTRAIN. Scored identically; the winner is whichever measures best, including 'none of them'.

SCORING IS MECHANICAL AND DELIBERATELY CRUDE: does the reply contain the expected value, and where
a party matters, does it name the right one. It cannot see fluency or hedging. Rows are printed in
full so the crude score can be overruled by reading — and where it is overruled, that is recorded
as judgement.

Uses the deployed `generate_raw` with the production prompt wrapper and the REAL retriever, so the
facts each probe sees are the facts production would retrieve.

R18: committed before it runs.
Artifact: eval/results/quantity_instruction_candidates.json
"""
import json
import os
import re
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)

import modal                                                                # noqa: E402
from chike import prompting                                                 # noqa: E402
from chike.retrieval import retrieve                                        # noqa: E402

PROBES = os.path.join(REPO, 'eval', 'accuracy_gate',
                      'quantity_instruction_heldout_024.jsonl')
OUT = os.path.join(REPO, 'eval', 'results', 'quantity_instruction_candidates.json')
ADAPTER_REPO = 'prospAprospA007/africa-giants-adapter-v15'

# Each candidate is appended to the system prompt. Nothing else changes.
CANDIDATES = {
    'C0_baseline': '',
    # C1 — NAME THE AXIS, PRESCRIBE NOTHING. The lightest possible form: tell the model the
    # distinction exists and to state which side it is answering. Cannot bias toward totals,
    # so arm P's opposite-direction rows should survive it.
    'C1_name_the_axis': (
        ' Kwa michango inayogawanywa kati ya mwajiri na mfanyakazi (kama NSSF), TAJA WAZI '
        'kama kiwango unachotoa ni cha JUMLA, cha mwajiri, au cha mfanyakazi — na jibu lile '
        'swali lililoulizwa.'),
    # C2 — NAME THE AXIS AND GIVE BOTH. Stronger: always supply the total and the split, so a
    # reader gets the right number whichever they wanted. Risks verbosity on arm N.
    'C2_state_total_and_split': (
        ' Kwa michango inayogawanywa kati ya mwajiri na mfanyakazi (kama NSSF), toa JUMLA na '
        'mgawanyo wake (mfano: jumla asilimia 20 — asilimia 10 mwajiri na asilimia 10 '
        'mfanyakazi), kisha jibu lile swali lililoulizwa.'),
    # C3 — GENERAL, NO LEVY NAMED. Tests whether the effect needs NSSF spelled out or works from
    # the abstract distinction alone. If C3 matches C1 the instruction generalises; if it does
    # not, the fix is narrower than it looks.
    'C3_general_no_levy': (
        ' Unapotoa kiwango au kiasi, hakikisha unajibu KIPIMO KILICHOULIZWA — jumla ikiulizwa '
        'jumla, sehemu ya upande mmoja ikiulizwa sehemu hiyo — na taja ni kipi.'),
}


def probes():
    with open(PROBES, encoding='utf-8') as f:
        rows = [json.loads(line) for line in f if line.strip()]
    assert len(rows) == 24, f'probe file has {len(rows)} rows, expected 24'
    return rows


def _norm(s):
    return re.sub(r'[\s,]', '', (s or '').lower())


def score(probe, reply):
    """Crude and honest: expected value present, and the right party named when one matters."""
    r = _norm(reply)
    val = _norm(probe.get('expect_value'))
    party = probe.get('expect_party') or ''
    value_ok = (val in r) if val else None
    party_ok = None
    if party:
        # First content word of the expected party, which is the discriminating token
        # ('jumla', 'mwajiri', 'mfanyakazi', 'kila', 'hapana', 'inakatwa').
        key = _norm(party.split()[0])
        party_ok = key in r
    return value_ok, party_ok


def main():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(ADAPTER_REPO, trust_remote_code=True)
    base_system = prompting.load_system_prompt()
    rows = probes()

    # Retrieve ONCE per probe: the facts are a property of the question, not the instruction, so
    # holding them fixed keeps the instruction the only variable across candidates.
    facts_for = {}
    for p in rows:
        facts_for[p['id']] = tuple(retrieve(p['question']))

    ChikeModel = modal.Cls.from_name('chike-inference', 'ChikeModel')
    results = {}
    for cname, suffix in CANDIDATES.items():
        system = base_system + suffix
        out_rows = []
        print(f'\n################ {cname} ################')
        for p in rows:
            prompt = prompting.build_chat_prompt(
                p['question'], facts_for[p['id']], system, tokenizer=tok)
            rec = {'id': p['id'], 'arm': p['arm'], 'question': p['question'],
                   'expect_value': p.get('expect_value'),
                   'expect_party': p.get('expect_party'),
                   'n_facts': len(facts_for[p['id']])}
            t0 = time.time()
            try:
                resp = ChikeModel().generate_raw.remote(prompt)
                reply = resp.get('completion', resp.get('text', resp)) \
                    if isinstance(resp, dict) else str(resp)
                reply = str(reply).replace('<|end_of_text|>', '').strip()
                rec['reply'] = reply
                v, pa = score(p, reply)
                rec['value_ok'], rec['party_ok'] = v, pa
                rec['pass'] = all(x for x in (v, pa) if x is not None)
                print(f"  {p['id']:<9}{p['arm'][0]}  value={v} party={pa}  {reply[:120]}")
            except Exception as e:
                rec['error'] = f'{type(e).__name__}: {e}'
                rec['pass'] = False
                print(f"  {p['id']:<9}ERROR {rec['error']}")
            rec['elapsed_s'] = round(time.time() - t0, 1)
            out_rows.append(rec)
        results[cname] = out_rows

    def tally(rws, arm):
        sub = [r for r in rws if r['arm'].startswith(arm)]
        return {'n': len(sub), 'pass': sum(1 for r in sub if r.get('pass'))}

    summary = {c: {'P': tally(rws, 'P'), 'N': tally(rws, 'N')} for c, rws in results.items()}

    out = {
        'measured': '2026-08-23',
        'harness': 'eval/forced_facts/measure_quantity_instruction.py',
        'probes': 'eval/accuracy_gate/quantity_instruction_heldout_024.jsonl (frozen 121b128, '
                  'before any candidate wording existed)',
        'instrument': 'deployed generate_raw + production prompt wrapper + real retriever; '
                      'facts held fixed per probe so the instruction is the only variable',
        'scoring': 'MECHANICAL AND CRUDE — expected value present, right party named. Blind to '
                   'fluency and hedging. Replies are stored in full so it can be overruled by '
                   'reading, and any override is recorded as judgement.',
        'candidates': {k: v for k, v in CANDIDATES.items()},
        'summary': summary,
        'rows': results,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print('\n================ SUMMARY ================')
    print(f"  {'candidate':<26}{'P (must improve)':>18}{'N (must not change)':>22}")
    for c, s in summary.items():
        print(f"  {c:<26}{s['P']['pass']:>10}/{s['P']['n']:<7}{s['N']['pass']:>14}/{s['N']['n']}")
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()
