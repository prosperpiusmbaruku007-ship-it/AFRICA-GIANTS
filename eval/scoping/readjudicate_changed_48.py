# -*- coding: utf-8 -*-
"""CLOSING AN R18 HOLE I OPENED: the compute-vs-fact figure quoted on 2026-08-24 was never committed.

WHAT WENT WRONG. The scoping note (commit 1e77aae) headlines a compute path at 4% wrong against a
fact path at 24% -- a six-fold gap -- cited as `[M, natural 48, live replies 2026-08-24]`. **There is
no such artifact.** The adjudication behind it was done in-session and never written to disk, which
by R18 makes it PROVISIONAL, and provisionality is contagious: the boundary argument it supports is
provisional too. This is the fifth instance of the pattern R18 exists for, and it is mine.

WHAT IS ACTUALLY RE-DERIVABLE, AND WHY THIS IS CHEAP. Diffing the committed 2026-08-17 adjudication
against the committed 2026-08-24 single-arm replies (eval/results/ab_retriever_full.json) shows that
**exactly three of the 48 replies changed**, and they are exactly the three rows the 2026-08-17 pass
marked WRONG on the compute path: nat_05, nat_23, nat_24. Every other row is byte-identical, so its
verdict cannot have moved. The whole question therefore reduces to adjudicating three replies, and
that adjudication is recorded here rather than in a chat message.

THE VERDICTS AND THEIR REASONING are written out in full below, including where a defensible
stricter or looser reading exists -- because the previous number moved twice (12.5% committed, 4%
claimed, 0% re-derived) and a bare figure is what made that possible.

R18: committed before its result is written up.
Artifact: eval/results/natural48_readjudicated_2026_08_24.json
"""
import json
import os
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, 'eval', 'results', 'natural48_readjudicated_2026_08_24.json')

ADJ = 'eval/results/natural48_rerun_2026_08_17_adjudication.json'
AB = 'eval/results/ab_retriever_full.json'
NAT = 'eval/accuracy_gate/edge_probe_natural_048.jsonl'

# --- The three verdicts. Adjudicator: Claude (Opus 5), against the row's own committed rubric.
VERDICTS = {
    'nat_05': {
        'was': 'WRONG', 'now': 'PARTIAL',
        'why': 'The trap is cleared. The rubric names exactly one WRONG condition -- 3.5% x '
               '50,000,000 -- and the reply does not compute it; it states the base as "asilimia '
               '3.5 ya JUMLA YA MISHAHARA", which is the correct base and a direct answer to the '
               'question actually asked ("asilimia tatu na nusu ya nini" = 3.5% of what?). It '
               'does not ask for the payroll figure, which is the rubric\'s second CORRECT '
               'clause, so it is not scored CORRECT.',
        'stricter_or_looser': 'A defensible reading scores this CORRECT: the user asked what the '
                              'base is, and got the right base. Recorded as PARTIAL to stay '
                              'consistent with the 2026-08-17 adjudicator, who scored a reply '
                              'WRONG for answering only one of two levies even though the levy '
                              'it answered was right. The direction of the move (away from '
                              'WRONG) does not depend on which reading is taken.',
        'also_gone': 'the fabricated TZS 260,000 BRELA registration fee, and the misrouting of '
                     'an SDL question to a BRELA source.',
    },
    'nat_23': {
        'was': 'WRONG', 'now': 'PARTIAL',
        'why': 'The rubric\'s WRONG condition is "answering only one levy". Cleared: the reply '
               'now answers BOTH, and both figures are right -- NSSF 20% x 5,500,000 = 1,100,000 '
               '(550,000 + 550,000) and SDL 3.5% x 5,500,000 = 192,500 at 12 employees.',
        'stricter_or_looser': 'NOT scored CORRECT, and the reason is a defect that survived the '
                              'fix: the reply still says "wafanyakazi 12 wenye mishahara TZS '
                              '5,500,000 KILA MMOJA" -- 5.5M is the TOTAL payroll, not each '
                              'employee\'s wage. Its own arithmetic contradicts its own prose '
                              '(12 x 5.5M would be 66M). Every number is right and the sentence '
                              'around them is wrong.',
        'boarded': 'the "kila mmoja" misstatement is a live self-contradiction on a correct '
                   'computation -- same shape as the eval_127 two-arm regression, and not '
                   'covered by any D-FIDELITY rule, which compare figures rather than the prose '
                   'that frames them.',
    },
    'nat_24': {
        'was': 'WRONG', 'now': 'CORRECT',
        'why': 'All three limbs of the triage are now right and correctly attributed: SDL does '
               'NOT apply and the reply says so explicitly with the reason (9 < 10); WCF applies '
               'from the first employee at 0.5%; NSSF applies at 20% (10% + 10%). The rubric '
               'asks WHICH levies apply, not how much, so this is a complete answer. The '
               '2026-08-17 failure -- conflating SDL and WCF into "mafunzo ya fidia" and '
               'attributing NSSF\'s 10% to WCF -- is gone.',
        'stricter_or_looser': 'A hedging first sentence ("hakuna taarifa kamili kuhusu kiwango '
                              'cha malipo") precedes the correct triage, and "asilimia 0% ya '
                              'SDL" is an awkward way to say SDL does not apply. Neither is a '
                              'wrong claim; both are quality, not correctness.',
        'note': 'THIS IS THE ROW D-FIDELITY-6 AND THE RATE GUARD WERE BUILT FOR. It is the only '
                'wrong -> right move in the set, and it landed on its target.',
    },
}


def jl(path):
    rows = [json.loads(l) for l in open(os.path.join(REPO, path), encoding='utf-8') if l.strip()]
    assert rows, f'{path} loaded ZERO rows'
    return rows


def main():
    adj = {r['id']: r for r in json.load(open(os.path.join(REPO, ADJ),
                                              encoding='utf-8'))['rows']}
    ab = {r['id']: r for r in json.load(open(os.path.join(REPO, AB), encoding='utf-8'))['rows']}
    nat = {r['id']: r for r in jl(NAT)}
    assert len(adj) == 48 and len(nat) == 48

    # --- Re-derive the changed set rather than trusting the list above. -----------------------
    changed = sorted(rid for rid, a in adj.items()
                     if (a.get('reply') or '').strip()
                     != (ab.get(rid, {}).get('single_arm_reply') or '').strip())
    assert set(changed) == set(VERDICTS), (
        f'the set of changed replies is {changed}, but verdicts were written for '
        f'{sorted(VERDICTS)}. A verdict for a row that did not change, or a changed row with no '
        f'verdict, means this artifact is not adjudicating what it claims to.')

    rows, before, after = [], Counter(), Counter()
    by_path_before, by_path_after = {}, {}
    for rid, a in adj.items():
        v = VERDICTS.get(rid)
        now = v['now'] if v else a['now']
        rows.append({'id': rid, 'path': a['path'], 'question': nat[rid]['question'],
                     'verdict_2026_08_17': a['now'], 'verdict_2026_08_24': now,
                     'reply_changed': rid in VERDICTS,
                     'adjudication': v,
                     'reply_2026_08_24': ab[rid]['single_arm_reply']})
        before[a['now']] += 1
        after[now] += 1
        by_path_before.setdefault(a['path'], Counter())[a['now']] += 1
        by_path_after.setdefault(a['path'], Counter())[now] += 1

    def rate(c, keys):
        n = sum(c.values())
        return round(sum(c[k] for k in keys) / n, 3) if n else None

    summary = {}
    for p in by_path_after:
        summary[p] = {
            'n': sum(by_path_after[p].values()),
            'before': dict(by_path_before[p]),
            'after': dict(by_path_after[p]),
            'wrong_rate_before': rate(by_path_before[p], ['WRONG']),
            'wrong_rate_after': rate(by_path_after[p], ['WRONG']),
            'wrong_or_partial_after': rate(by_path_after[p], ['WRONG', 'PARTIAL']),
        }

    blob = {
        'readjudicated': '2026-08-25',
        'harness': 'eval/scoping/readjudicate_changed_48.py',
        'closes': 'an R18 hole in commit 1e77aae -- the scoping note cites a compute/fact split '
                  'from an adjudication that was never committed.',
        'method': 'diff the committed 2026-08-17 adjudication against the committed 2026-08-24 '
                  'single-arm replies. EXACTLY THREE of 48 replies changed; the other 45 are '
                  'byte-identical, so their verdicts cannot have moved. Only the three are '
                  're-adjudicated, and the changed set is re-derived and ASSERTED against the '
                  'verdicts written, not taken on trust.',
        'adjudicator': 'Claude (Opus 5), against each row\'s committed rubric in '
                       'eval/accuracy_gate/edge_probe_natural_048.jsonl',
        'the_number_moved_twice': {
            'committed_2026_08_17': 'compute 3 WRONG of 24 = 12.5%',
            'claimed_2026_08_24_UNCOMMITTED': 'compute 1 WRONG of 24 = 4% -- no artifact exists',
            'this_pass': 'compute 0 WRONG of 24, with 3 PARTIAL',
            'lesson': 'a bare ratio on n=24 is unstable and was quoted three different ways in '
                      'eight days. WRONG+PARTIAL is reported alongside it for that reason.',
        },
        'by_path': summary,
        'overall_before': dict(before),
        'overall_after': dict(after),
        'rows': rows,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(blob, f, ensure_ascii=False, indent=2)

    for p, s in summary.items():
        print(f"{p:9s} n={s['n']:2d}  WRONG {s['wrong_rate_before']} -> {s['wrong_rate_after']}"
              f"   WRONG+PARTIAL after = {s['wrong_or_partial_after']}")
        print(f"           {s['before']}  ->  {s['after']}")
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()
