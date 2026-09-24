# -*- coding: utf-8 -*-
"""Captures live replies for both members of every pair in paired_phrasing_024.jsonl.

THE QUESTION NOBODY CAN CURRENTLY ANSWER: how often does CHIKE contradict itself when the
same question is rephrased? Every probe set and gate corpus in this repo is
ONE-PHRASING-PER-QUESTION by construction, and such a corpus cannot detect phrasing-
dependence however large it is or however carefully it is adjudicated. The only evidence
that exists is 4-of-6 from the 12 deliberately-paired rows of the extended-078 -- too small
to generalise, and drawn entirely from coverage gaps, the population where it would be worst.

THIS FILE ONLY CAPTURES. Adjudication is a separate reading pass, for the same reason it was
separated for the 78: a harness that scores while it measures invites the scoring rule to be
adjusted to the data it is seeing.

=== THE VERDICT SCHEME, FROZEN HERE BEFORE ANY REPLY IS READ ===

CONSISTENCY AND CORRECTNESS ARE SEPARATE AXES AND MUST NOT BE COLLAPSED. Two answers can both
be WRONG and still be mutually CONSISTENT -- that is a correctness failure this corpus is not
measuring, and counting it as a contradiction would inflate the headline with the very thing
every other corpus in this repo already measures.

  CONSISTENT_CORRECT      both members agree AND the shared answer is right
  CONSISTENT_WRONG        both members agree AND the shared answer is wrong
                          -> NOT a contradiction. Counts toward the accuracy problem we
                             already know about, not toward this one.
  DIVERGENT_COMPATIBLE    one member says more than the other (extra detail, a caveat, a
                          citation) but nothing asserted in one is denied by the other
                          -> NOT a contradiction. Completeness variance.
  CONTRADICTORY           the two answers CANNOT BOTH BE TRUE. A figure vs a different
                          figure for the same quantity; "yes" vs "no"; "required" vs "not
                          required"; two different named authorities for one function.
                          -> THE TARGET MEASUREMENT.
  SCOPE_INCONSISTENT      one member is answered and the other refused as out of scope.
                          -> Its own verdict. It is not a factual contradiction, but to a
                             user it is the same experience -- the system's competence
                             appears to depend on how they typed. Reported separately so it
                             can be read either way rather than folded in silently.
  UNADJUDICABLE           one or both replies too vague to place.

HEADLINE = CONTRADICTORY / (adjudicable pairs). SCOPE_INCONSISTENT reported alongside, never
summed into it without saying so.

CATEGORY MATTERS AS MUCH AS THE RATE. The known 4-of-6 came from GAP rows only. This corpus
carries 6 pairs each of covered_fact / gap / compute / boundary precisely so the rate can be
read per category -- a contradiction rate driven entirely by gaps is a different finding from
one spread across covered facts, and the remedies differ completely.

R16 STRUCTURAL: artifact written after EVERY reply, per-row error capture, resume on restart.
R18: committed BEFORE the run, together with the frozen corpus.

Usage:  python eval/consistency/run_paired_phrasing_live.py [--resume]
Artifact: eval/results/paired_phrasing_live_2026_09_24.json
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
PAIRS = os.path.join(HERE, 'paired_phrasing_024.jsonl')
ENDPOINT = 'https://prosperpiusmbaruku007--chike-inference-web-endpoint.modal.run'
OUT = os.path.join(REPO, 'eval', 'results', 'paired_phrasing_live_2026_09_24.json')

VERDICT_SCHEME = {
    'CONSISTENT_CORRECT': 'both agree and the shared answer is right',
    'CONSISTENT_WRONG': 'both agree and the shared answer is wrong -- NOT a contradiction',
    'DIVERGENT_COMPATIBLE': 'one says more, nothing denied -- NOT a contradiction',
    'CONTRADICTORY': 'the two answers cannot both be true -- THE TARGET',
    'SCOPE_INCONSISTENT': 'one answered, one refused as out of scope -- reported separately',
    'UNADJUDICABLE': 'one or both replies too vague to place',
}


def token():
    p = os.path.expanduser('~/.chike_modal_token.txt')
    return (os.environ.get('CHIKE_MODAL_TOKEN')
            or (open(p, encoding='utf-8').read().strip() if os.path.exists(p) else ''))


def ask(question):
    url = f'{ENDPOINT}?token={urllib.parse.quote(token())}'
    req = urllib.request.Request(url, data=json.dumps({'message': question}).encode('utf-8'),
                                 headers={'Content-Type': 'application/json'})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            body = json.loads(r.read().decode('utf-8', 'replace'))
            return {'outcome': 'HTTP_200', 'reply': body.get('reply', body.get('error', '')),
                    'elapsed_s': round(time.time() - t0, 1)}
    except Exception as exc:                                              # noqa: BLE001
        return {'outcome': 'ERROR', 'reply': f'{type(exc).__name__}: {str(exc)[:300]}',
                'elapsed_s': round(time.time() - t0, 1)}


def main():
    with open(PAIRS, encoding='utf-8') as f:
        pairs = [json.loads(line) for line in f if line.strip()]
    assert len(pairs) == 24, f'expected 24 pairs, found {len(pairs)}'

    blob = {'measured': '2026-09-24', 'target': 'chike-inference (production)',
            'harness': 'eval/consistency/run_paired_phrasing_live.py',
            'source_pairs': 'eval/consistency/paired_phrasing_024.jsonl',
            'verdict_scheme': VERDICT_SCHEME,
            'why_this_population': (
                'The ONLY question this corpus exists to answer is phrasing-dependence, '
                'which no other corpus in this repo can detect: all of them are '
                'one-phrasing-per-question by construction. 24 pairs, 6 each across '
                'covered_fact / gap / compute / boundary, so the rate is readable per '
                'category -- the prior 4-of-6 estimate came from gaps only.'),
            'adjudication': 'NOT done here. Separate reading pass, consistency-first.',
            'rows': []}

    resume = '--resume' in sys.argv
    done = set()
    if resume and os.path.exists(OUT):
        blob = json.load(open(OUT, encoding='utf-8'))
        done = {(r['pair_id'], r['member']) for r in blob['rows']
                if r.get('outcome') == 'HTTP_200'}
        print(f'[resume] {len(done)} reply/replies already captured')

    total = len(pairs) * 2
    n = 0
    for pair in pairs:
        for member in ('a', 'b'):
            n += 1
            key = (pair['pair_id'], member)
            if key in done:
                continue
            q = pair[member]['q']
            r = ask(q)
            row = {'pair_id': pair['pair_id'], 'member': member,
                   'category': pair['category'], 'topic': pair['topic'],
                   'register': pair[member]['register'], 'question': q,
                   'outcome': r['outcome'], 'reply': r['reply'],
                   'elapsed_s': r['elapsed_s']}
            blob['rows'] = [x for x in blob['rows']
                            if (x['pair_id'], x['member']) != key] + [row]
            with open(OUT, 'w', encoding='utf-8') as f:      # after EVERY reply
                json.dump(blob, f, ensure_ascii=False, indent=2)
            print(f"[{n}/{total}] {pair['pair_id']}{member} ({pair['category']}, "
                  f"{r['elapsed_s']}s): {r['reply'][:120]}")

    order = {(p['pair_id'], m): i for i, p in enumerate(pairs) for m in ('a', 'b')}
    blob['rows'].sort(key=lambda r: order.get((r['pair_id'], r['member']), 999))
    errs = [r['pair_id'] + r['member'] for r in blob['rows'] if r['outcome'] != 'HTTP_200']
    blob['status'] = ('COMPLETE -- adjudication pending, separate pass' if not errs
                      else f'INCOMPLETE -- errors on {errs}')
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(blob, f, ensure_ascii=False, indent=2)
    print(f"\n{blob['status']}")
    print(f'[saved] {os.path.relpath(OUT, REPO)}')


if __name__ == '__main__':
    main()
