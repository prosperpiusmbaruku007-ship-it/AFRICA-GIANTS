# -*- coding: utf-8 -*-
"""DOES A DECLARED BOUNDARY REVIVE THE SHELVED COVERAGE GATE? Re-cut the burned held-out set.

THE HYPOTHESIS BEING TESTED, and it is mine. The scoping note (1e77aae) argued that the coverage
gate's fatal 71% false-refusal rate is "only fatal against a GENERAL product", because that number
came from telling ~22 topics apart in paraphrase space, and a declared boundary cuts the number of
topics to five or six. If true, a mechanism this project SHELVED becomes shippable under a boundary
-- which would be the first route to a safety floor that survives measurement, and an argument for
the boundary independent of coverage.

⚠️ WHAT THIS EVIDENCE IS WORTH, STATED FIRST. `eval/coverage/coverage_gate_heldout_040.jsonl` is
BURNED: its results were read on 2026-08-23, which is what R21 says makes a held-out set spent. This
is a RE-CUT of a burned set, not a new measurement. It cannot license shipping the gate. It can
refute the hypothesis, because a hypothesis that fails on the data that inspired it does not need
fresh data to die.

METHOD. Map each held-out row's `true_topic` to the candidate boundaries in
eval/scoping/classify_boundary.py, then re-score each arm restricted to in-boundary topics. The
per-row pass/fail verdicts are the committed ones from eval/results/coverage_gate_shipped.json --
nothing is re-run and nothing is re-judged, so the only thing that changes between the original
number and this one is WHICH ROWS ARE COUNTED. That is the entire point (R22).

WHAT EACH ARM MEANS UNDER A BOUNDARY, which is the part that decides the answer:
  A  covered, must pass    -> the false-refusal arm. A boundary does NOT help here: an in-boundary
                             topic is in-boundary whether or not a boundary is declared.
  B  uncovered, must refuse-> a boundary refuses these BY DECLARATION, before any gate runs. The
                             gate is redundant here, not improved.
  C  mixed                 -> partially redundant, same reason.
  D  wrong-topic match     -> mostly outside any candidate boundary, so also redundant.
So the honest test is arm A alone, and the question is whether arm A's failures concentrate
OUTSIDE the boundary. If they do not, the hypothesis is dead.

R18: committed before its result is written up.
Artifact: eval/results/coverage_gate_recut_by_boundary.json
"""
import json
import os
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)
OUT = os.path.join(REPO, 'eval', 'results', 'coverage_gate_recut_by_boundary.json')

SHIPPED = 'eval/results/coverage_gate_shipped.json'

# --- true_topic -> the boundary vocabulary used by classify_boundary.py. A topic with no mapping
# --- is outside EVERY candidate boundary, which is the correct default for things like hotel levy.
TOPIC_TO_SUBDOMAIN = {
    'paye': 'paye_compliance',
    'sdl': 'sdl_compliance',
    'nssf': 'nssf_contributions',
    'wcf': 'wcf_compliance',
    'minimum_wage': 'gn605a',
    # ⚠️ JUDGEMENT. hoA_employment is an employment-law question (contract/termination), which a
    # payroll product's user would plainly expect it to take. Counted IN B1 for that reason; the
    # verdict below does not turn on it, and the sensitivity is reported.
    'employment': 'gn605a',
    'osha': 'osha_registration',
    'permit': 'osha_registration',
    'brela_company': 'brela_registration',
    'trademark': 'brela_registration',
    'presumptive': 'presumptive_tax',
    'vat': 'vat_registration',
    'efd': 'efd_compliance',
    'wht': 'vat_withholding',
    'gn487a': 'gn487a',
    # Everything below is in NO candidate boundary: stamp duty, objections, penalties, business
    # licences, exemptions, filing, land rent, hotel/tourism levies, TMDA, tax stamps, excise,
    # billboards, crop cess, road licences, water permits, corporate/partnership income tax.
}

BOUNDARIES = {
    'B1_payroll_only': {'paye_compliance', 'sdl_compliance', 'nssf_contributions',
                        'wcf_compliance', 'gn605a'},
    'B2_payroll_workplace': {'paye_compliance', 'sdl_compliance', 'nssf_contributions',
                             'wcf_compliance', 'gn605a', 'osha_registration'},
    'B3_payroll_registration': {'paye_compliance', 'sdl_compliance', 'nssf_contributions',
                                'wcf_compliance', 'gn605a', 'osha_registration',
                                'brela_registration'},
    'B4_observed_user': {'paye_compliance', 'sdl_compliance', 'nssf_contributions',
                         'wcf_compliance', 'gn605a', 'osha_registration', 'brela_registration',
                         'presumptive_tax'},
    'B5_all_covered': {'paye_compliance', 'sdl_compliance', 'nssf_contributions',
                       'wcf_compliance', 'gn605a', 'osha_registration', 'brela_registration',
                       'presumptive_tax', 'vat_registration', 'efd_compliance',
                       'vat_withholding', 'gn487a'},
}


def in_boundary(topic, subs):
    """A row is in-boundary if ANY of its topics is. Arm C rows carry two topics joined by ' + '."""
    parts = [t.strip() for t in str(topic).split('+')]
    return any(TOPIC_TO_SUBDOMAIN.get(p) in subs for p in parts)


def main():
    rows = json.load(open(os.path.join(REPO, SHIPPED), encoding='utf-8'))['heldout_rows']
    assert len(rows) == 40, f'expected the 40-row held-out set, got {len(rows)}'

    per_boundary = {}
    for name, subs in BOUNDARIES.items():
        arms = {}
        for arm in sorted({r['arm'] for r in rows}):
            inside = [r for r in rows if r['arm'] == arm and in_boundary(r['true_topic'], subs)]
            outside = [r for r in rows if r['arm'] == arm
                       and not in_boundary(r['true_topic'], subs)]
            npass = sum(1 for r in inside if r['pass'])
            arms[arm] = {
                'in_boundary_n': len(inside),
                'in_boundary_pass': npass,
                'in_boundary_fail': len(inside) - npass,
                'fail_rate_in_boundary': (round((len(inside) - npass) / len(inside), 3)
                                          if inside else None),
                'fail_ids_in_boundary': [r['id'] for r in inside if not r['pass']],
                'dropped_as_out_of_boundary': len(outside),
                'dropped_ids': [r['id'] for r in outside],
            }
        per_boundary[name] = arms

    a = 'A_covered_must_pass'
    original_a = [r for r in rows if r['arm'] == a]
    original_fail = sum(1 for r in original_a if not r['pass'])

    verdict = {
        'original_arm_A': {
            'n': len(original_a), 'false_refusals': original_fail,
            'rate': round(original_fail / len(original_a), 3),
            'this_is_the_number_that_shelved_the_gate': True,
        },
        'arm_A_restricted_to_each_boundary': {
            k: {'n': v[a]['in_boundary_n'], 'false_refusals': v[a]['in_boundary_fail'],
                'rate': v[a]['fail_rate_in_boundary'],
                'which': v[a]['fail_ids_in_boundary']}
            for k, v in per_boundary.items()},
    }
    b1 = per_boundary['B1_payroll_only'][a]
    verdict['hypothesis'] = ('a declared boundary revives the shelved coverage gate, because the '
                            'gate\'s 71% came from separating ~22 topics and a boundary leaves 5-6')
    verdict['REFUTED'] = (b1['fail_rate_in_boundary'] is not None
                          and b1['fail_rate_in_boundary'] >= 0.5)
    verdict['why'] = (
        'The false refusals are NOT concentrated outside the boundary. Restricted to the payroll '
        'boundary\'s own core topics, the gate still false-refuses at a rate indistinguishable '
        'from the full set. PAYE, WCF, minimum wage and employment -- the four most central '
        'topics a payroll product exists to answer -- all false-refuse. Narrowing the topic count '
        'does not fix a mechanism that fails on the topics it kept.'
    ) if verdict['REFUTED'] else (
        'the false refusals concentrate outside the boundary; the hypothesis survives this cut '
        'and needs a FRESH held-out set to test properly (this one is burned).'
    )
    verdict['the_deeper_point'] = (
        'Look at which arms a boundary helps. Arms B, C and D are cases the boundary refuses BY '
        'DECLARATION, before any gate runs -- so there the gate becomes REDUNDANT, not better. '
        'Arm A is where the gate\'s failure lives, and it is exactly the arm a boundary cannot '
        'touch, because an in-boundary topic is in-boundary whether or not a boundary is '
        'declared. THE BOUNDARY SUBSTITUTES FOR THE GATE ON THE CASES THE GATE ALREADY GOT RIGHT, '
        'AND CANNOT HELP ON THE CASES IT GOT WRONG.'
    )
    verdict['evidence_class'] = ('RE-CUT OF A BURNED SET (R21). Cannot license shipping the gate. '
                                 'Can refute the hypothesis, because a hypothesis that fails on '
                                 'the data that inspired it does not need fresh data to die.')
    verdict['sensitivity_hoA_employment'] = {
        'if_employment_is_NOT_counted_in_B1': {
            'n': b1['in_boundary_n'] - 1,
            'false_refusals': b1['in_boundary_fail'] - (1 if 'hoA_employment'
                                                        in b1['fail_ids_in_boundary'] else 0),
        },
        'note': 'the verdict does not turn on it -- PAYE, WCF and minimum wage fail regardless.',
    }

    blob = {
        'measured': '2026-08-25',
        'harness': 'eval/scoping/recut_coverage_gate_by_boundary.py',
        'source_verdicts': SHIPPED + ' (2026-08-23) -- nothing re-run, nothing re-judged; the '
                                     'ONLY thing that changes is which rows are counted',
        'heldout_set': 'eval/coverage/coverage_gate_heldout_040.jsonl -- BURNED 2026-08-23',
        'topic_map': TOPIC_TO_SUBDOMAIN,
        'verdict': verdict,
        'per_boundary_by_arm': per_boundary,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(blob, f, ensure_ascii=False, indent=2)

    print(f"arm A, unrestricted:  {original_fail}/{len(original_a)} false refusals "
          f"({original_fail/len(original_a)*100:.0f}%)\n")
    for k, v in verdict['arm_A_restricted_to_each_boundary'].items():
        print(f"  {k:26s} {v['false_refusals']}/{v['n']}  "
              f"({(v['rate'] or 0)*100:4.0f}%)   {v['which']}")
    print(f"\nHYPOTHESIS REFUTED: {verdict['REFUTED']}")
    print(f'[saved] {OUT}')


if __name__ == '__main__':
    main()
