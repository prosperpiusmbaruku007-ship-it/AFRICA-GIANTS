# -*- coding: utf-8 -*-
"""STEP 1 of the scoped-product question: classify every corpus question by CANDIDATE BOUNDARY.

THE QUESTION THIS SERVES. Is there a version of this product that ships without a runtime safety
floor -- a narrower declared domain, with the refusal being the PRODUCT'S BOUNDARY rather than a
per-question judgement? Every floor design measured in this project has failed. A boundary declared
in advance classifies nothing at runtime, so it is not subject to the 37x paraphrase gap that killed
the coverage gate. Step 1 bounds the question offline and for free; step 2 (held-out first-messages
in a recruited employer's voice) is the decisive measurement.

⛔ WHAT THIS MEASUREMENT IS, AND THE POPULATION IT IS TAKEN ON (R22, stated inside the artifact so
the caveat cannot be separated from the number by being quoted):

  Population A -- the 400-row gate corpus. AUTHORED BY US, from the same source families as the
    facts. It measures WHAT WE BUILT, not what a user asks. A boundary's "coverage" here is a
    statement about our own construction choices and NOTHING ELSE.
  Population B -- the natural 48. Authored as realistic messages, still by us. Carries live paths
    and adjudicated verdicts, so it is the only population where in-boundary ACCURACY is knowable.
  Population C -- the 12 coverage-gap probes. Authored deliberately as the HARD half, to depict
    questions the corpus does NOT hold. A boundary's hit rate here is a LOWER bound, not a rate.

  NONE of these is the population the decision applies to. That population is REAL EMPLOYERS'
  FIRST MESSAGES, and this project has never held a sample of it. Step 1 therefore cannot answer
  "would a scoped product hit"; it can only answer "IS OUR CORPUS SHAPED LIKE A SCOPED PRODUCT",
  which is a question about us. Reported as such, with no extrapolation.

THE CLASSIFICATION AXIS, AND WHY IT IS NOT OUR SUBDOMAIN LABELS. Classifying by `subdomain` would
be circular: the labels are ours, so any boundary drawn along them covers exactly what we chose to
build. The axis used instead is the STATUTORY TRIGGER -- which fact about a business creates the
obligation. That is a property of Tanzanian law, not of our filing system, and it is the axis a
product boundary actually cuts along, because it decides WHO the product is for:

  employer_only  the obligation exists ONLY because the business has employees
  any_business   the obligation exists regardless of whether anyone is employed
  non_citizen    the obligation attaches to the owner's nationality
  ooc            outside the corpus by design

Each mapping below carries its trigger in a comment. Disputable ones are marked and their
sensitivity is reported separately rather than buried in a total.

⚠️ THE SUPERSET POINT, which is the reason this axis was chosen. An employer is not a user who has
ONLY payroll obligations. An employer with 12 staff still registers a business, still issues EFD
receipts, still crosses the VAT threshold. So "our users are employers" and "our product answers
payroll" are DIFFERENT SCOPES, and the gap between them is measured here as
`refused_share_for_an_employer` -- of everything a real employer might ask, how much a payroll
boundary would decline. A boundary chosen because the user population fits it can still refuse most
of what that population asks.

ROUTE LABELS come from the PRODUCTION router: chike.orchestrator.Orchestrator.decompose + .route,
the same two calls answer() makes (orchestrator.py:867). Not a re-implementation and not a keyword
guess. The compute path is the boundary's whole safety argument -- if a boundary does not
concentrate compute-path questions, it does not buy the safety it is being proposed for.

R18: committed before its result is written up.
Artifact: eval/results/boundary_classification.json
"""
import json
import os
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)
OUT = os.path.join(REPO, 'eval', 'results', 'boundary_classification.json')

from chike.orchestrator import Orchestrator            # noqa: E402
from chike import routing                              # noqa: E402


# --- The actor map. One row per subdomain, each with the statutory trigger that creates the
# --- obligation. This is the only place a judgement is made, so it is the only place to audit.
ACTOR = {
    # employer_only -- no employees, no obligation.
    'paye_compliance':   ('employer_only', 'ITA Cap 332: withholding on employment income. '
                                           'No employment income, no PAYE.'),
    'sdl_compliance':    ('employer_only', 'SDL is charged on the payroll of an employer with '
                                           '>=10 employees. Threshold is a headcount.'),
    'nssf_contributions':('employer_only', 'NSSF Act: 10%+10% on an employee\'s wage. '
                                           'Contribution presupposes an employee.'),
    'wcf_compliance':    ('employer_only', 'WCF Act: 0.5% of payroll; registration is triggered '
                                           'within 30 days of hiring the FIRST employee.'),
    'gn605a':            ('employer_only', 'Minimum wage order binds a person who PAYS wages.'),
    # ⚠️ DISPUTABLE. OSHA registration attaches to a WORKPLACE, and a sole trader\'s shop is a
    # workplace. It is grouped employer_only because the Act\'s duties are framed as an employer\'s
    # duties to workers -- but a boundary drawn here would be arguable, so every total below is
    # also reported with OSHA moved to any_business (`sensitivity_osha`).
    'osha_registration': ('employer_only', 'OSHA Act 2003: duties of an employer to persons at '
                                           'work. DISPUTABLE -- a sole trader\'s premises is '
                                           'also a workplace.'),

    # any_business -- arises whether or not anyone is employed.
    'vat_registration':  ('any_business', 'Turnover threshold (TZS 200M/12mo or 100M/6mo). '
                                          'Headcount is irrelevant.'),
    'vat_withholding':   ('any_business', 'Attaches to appointed withholding agents / payers. '
                                          'Not employment-conditioned.'),
    'efd_compliance':    ('any_business', 'Receipting obligation of a business making sales.'),
    'brela_registration':('any_business', 'Registration/annual return of the entity itself.'),
    'presumptive_tax':   ('any_business', 'Cap 332 s.35 presumptive regime applies to small '
                                          'non-VAT-registered traders. Structurally a SOLE '
                                          'TRADER regime -- the opposite of employer-conditioned.'),

    'gn487a':            ('non_citizen', 'Business Licensing (Prohibition ... for Non-Citizens) '
                                         'Order: trigger is the owner\'s nationality.'),
    'out_of_corpus':     ('ooc', 'Outside the corpus by design.'),
}

# --- Candidate boundaries. Named by what a user would be TOLD the product does.
BOUNDARIES = {
    'B1_payroll_only': {
        'label': 'Employer payroll only (PAYE, SDL, NSSF, WCF, minimum wage)',
        'subdomains': {'paye_compliance', 'sdl_compliance', 'nssf_contributions',
                       'wcf_compliance', 'gn605a'},
        'copy': '"Mishahara na makato ya wafanyakazi" -- the question as literally asked.',
    },
    'B2_payroll_workplace': {
        'label': 'B1 + workplace registration (OSHA)',
        'subdomains': {'paye_compliance', 'sdl_compliance', 'nssf_contributions',
                       'wcf_compliance', 'gn605a', 'osha_registration'},
        'copy': 'Everything that follows from HAVING STAFF.',
    },
    'B3_payroll_registration': {
        'label': 'B2 + business registration (BRELA)',
        'subdomains': {'paye_compliance', 'sdl_compliance', 'nssf_contributions',
                       'wcf_compliance', 'gn605a', 'osha_registration', 'brela_registration'},
        'copy': '"Kusajili biashara na kulipa wafanyakazi."',
    },
    'B4_observed_user': {
        'label': 'B3 + presumptive income tax (the boundary matching the OBSERVED coverage-gap user)',
        'subdomains': {'paye_compliance', 'sdl_compliance', 'nssf_contributions',
                       'wcf_compliance', 'gn605a', 'osha_registration', 'brela_registration',
                       'presumptive_tax'},
        'copy': '"Kodi ya makadirio, usajili, na mishahara."',
    },
    'B5_all_covered': {
        'label': 'Everything the corpus covers (today\'s product, no boundary)',
        'subdomains': {k for k, (a, _) in ACTOR.items() if a != 'ooc'},
        'copy': 'No declared boundary -- the runtime-judgement product that needs a floor.',
    },
}

CORPUS_400 = ['eval/accuracy_gate/eval_questions_001.jsonl',
              'eval/accuracy_gate/eval_questions_002_additions.jsonl',
              'eval/accuracy_gate/eval_questions_003.jsonl']
NAT48 = 'eval/accuracy_gate/edge_probe_natural_048.jsonl'
PRESUMPTIVE = 'eval/accuracy_gate/presumptive_tax_probes_020.jsonl'
COVERAGE_12 = 'eval/results/coverage_12_rerun.json'
NAT48_ADJ = 'eval/results/natural48_rerun_2026_08_17_adjudication.json'
AB = 'eval/results/ab_retriever_full.json'


def jl(path):
    rows = []
    with open(os.path.join(REPO, path), encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    assert rows, f'{path} loaded ZERO rows -- a silent empty load is the defect R20 exists for'
    return rows


def route_of(orc, text):
    """The production route decision: decompose, then route each part (orchestrator.py:867).

    A multi-part question is 'compute' if ANY part computes, because the compute path is what the
    user's figures flow through and a mixed question exposes them to it."""
    parts = orc.decompose(text)
    kinds = [orc.route(p).kind for p in parts]
    return 'compute' if 'compute' in kinds else 'fact', len(parts)


def classify_corpus(orc):
    rows = []
    for path in CORPUS_400:
        for r in jl(path):
            sd = r.get('subdomain', '?')
            actor, trigger = ACTOR.get(sd, ('UNMAPPED', ''))
            assert actor != 'UNMAPPED', f'subdomain {sd!r} has no actor mapping -- add it'
            kind, nparts = route_of(orc, r['question_sw'])
            rows.append({'id': r['id'], 'q': r['question_sw'], 'subdomain': sd,
                         'actor': actor, 'route': kind, 'n_parts': nparts})
    for r in jl(PRESUMPTIVE):
        kind, nparts = route_of(orc, r['question'])
        rows.append({'id': r['id'], 'q': r['question'], 'subdomain': 'presumptive_tax',
                     'actor': 'any_business', 'route': kind, 'n_parts': nparts})
    return rows


def boundary_report(rows, key='subdomain'):
    out = {}
    answerable = [r for r in rows if r['actor'] != 'ooc']
    for name, b in BOUNDARIES.items():
        inside = [r for r in answerable if r[key] in b['subdomains']]
        outside = [r for r in answerable if r[key] not in b['subdomains']]
        rc = Counter(r['route'] for r in inside)
        out[name] = {
            'label': b['label'],
            'copy': b['copy'],
            'in_boundary': len(inside),
            'outside_boundary': len(outside),
            'share_of_answerable': round(len(inside) / len(answerable), 3),
            'route_mix_in_boundary': dict(rc),
            'compute_share_in_boundary': round(rc['compute'] / len(inside), 3) if inside else None,
            'outside_by_subdomain': dict(Counter(r['subdomain'] for r in outside)),
        }
    return out, len(answerable)


def main():
    # decompose/route never touch the backend -- they are pure text -> path decisions. A null
    # backend makes that explicit: if either call ever starts generating, this run raises rather
    # than silently measuring something else.
    orc = Orchestrator(backend=None)
    print('classifying the 400-row gate corpus + 20 presumptive probes ...')
    rows = classify_corpus(orc)
    by_actor = Counter(r['actor'] for r in rows)
    by_actor_route = defaultdict(Counter)
    for r in rows:
        by_actor_route[r['actor']][r['route']] += 1

    boundaries, n_answerable = boundary_report(rows)

    # --- THE SUPERSET MEASURE. For a user who IS an employer, how much of what they might ask
    # --- would each boundary decline? Employers hold BOTH employer_only and any_business duties.
    employer_relevant = [r for r in rows if r['actor'] in ('employer_only', 'any_business')]
    superset = {}
    for name, b in BOUNDARIES.items():
        refused = [r for r in employer_relevant if r['subdomain'] not in b['subdomains']]
        superset[name] = {
            'employer_relevant_rows': len(employer_relevant),
            'would_be_refused': len(refused),
            'refused_share_for_an_employer': round(len(refused) / len(employer_relevant), 3),
            'refused_by_subdomain': dict(Counter(r['subdomain'] for r in refused)),
        }

    # --- SENSITIVITY: OSHA is the one disputable mapping. Re-run the actor totals with it moved.
    sens = Counter()
    for r in rows:
        a = 'any_business' if r['subdomain'] == 'osha_registration' else r['actor']
        sens[a] += 1

    # --- Population B: the natural 48, with live route + committed verdicts. -------------------
    nat = {r['id']: r for r in jl(NAT48)}
    adj = {r['id']: r for r in json.load(open(os.path.join(REPO, NAT48_ADJ),
                                              encoding='utf-8'))['rows']}
    ab = {r['id']: r for r in json.load(open(os.path.join(REPO, AB), encoding='utf-8'))['rows']}
    nat_rows = []
    for rid, r in nat.items():
        sd = r['subdomain']
        actor, _ = ACTOR.get(sd, ('UNMAPPED', ''))
        live = ab.get(rid, {})
        nat_rows.append({
            'id': rid, 'q': r['question'], 'subdomain': sd, 'actor': actor,
            'route_2026_08_17': (adj.get(rid) or {}).get('path'),
            'route_live_2026_08_24': live.get('path_single'),
            'verdict_2026_08_17': (adj.get(rid) or {}).get('now'),
        })
    nat_by_boundary = {}
    for name, b in BOUNDARIES.items():
        inside = [r for r in nat_rows if r['subdomain'] in b['subdomains']]
        v = Counter(r['verdict_2026_08_17'] for r in inside)
        nat_by_boundary[name] = {
            'n': len(inside),
            'verdicts_2026_08_17': dict(v),
            'wrong_share': round((v['WRONG']) / len(inside), 3) if inside else None,
            'route_live': dict(Counter(r['route_live_2026_08_24'] for r in inside)),
        }

    # --- Population C: the 12 coverage-gap probes, hand-mapped to subdomain. -------------------
    # Each is the FIRST MESSAGE of a shop-owning sole trader, authored 2026-08-16 to probe what
    # the corpus does NOT hold. Mapping is by the obligation named in the question.
    cov = json.load(open(os.path.join(REPO, COVERAGE_12), encoding='utf-8'))['rows']
    COV_MAP = [
        ('presumptive_tax', 'income tax for a duka on 30M turnover -> presumptive regime'),
        ('presumptive_tax', 'kodi ya makadirio on 4M turnover'),
        ('business_licence', 'business licence FEE -- NOT IN CORPUS at all'),
        ('business_licence', 'business licence RENEWAL -- NOT IN CORPUS'),
        ('council_levy', 'council service levy % -- NOT IN CORPUS'),
        ('council_levy', 'market levy for a genge -- NOT IN CORPUS'),
        ('fire_safety', 'fire-safety certificate -- NOT IN CORPUS'),
        ('weights_measures', 'scale calibration interval -- NOT IN CORPUS'),
        ('rental_withholding', 'withholding on rent paid to a landlord -- NOT IN CORPUS'),
        ('tin_registration', 'getting a business TIN -- NOT IN CORPUS'),
        ('tra_inspection', 'what to do in a TRA inspection -- NOT IN CORPUS'),
        ('mobile_money_tax', 'tax on mobile-money receipts -- NOT IN CORPUS'),
    ]
    assert len(COV_MAP) == len(cov), 'coverage map and artifact rows disagree'
    cov_rows = []
    for (sd, why), r in zip(COV_MAP, cov):
        q = r.get('question') or r.get('q')
        kind, _ = route_of(orc, q)
        cov_rows.append({'q': q, 'mapped_subdomain': sd, 'why': why, 'route': kind,
                         'in_corpus_subdomains': sd in ACTOR})
    cov_by_boundary = {}
    for name, b in BOUNDARIES.items():
        hit = [r for r in cov_rows if r['mapped_subdomain'] in b['subdomains']]
        cov_by_boundary[name] = {'hits_of_12': len(hit),
                                 'hit_questions': [r['q'][:70] for r in hit]}

    blob = {
        'measured': '2026-08-25',
        'harness': 'eval/scoping/classify_boundary.py',
        'step': 'STEP 1 of the scoped-product question -- free, offline, and BOUNDING only',
        'what_this_can_and_cannot_answer': {
            'can': 'IS OUR CORPUS SHAPED LIKE A SCOPED PRODUCT -- a question about our own '
                   'construction choices.',
            'cannot': 'WOULD A SCOPED PRODUCT HIT -- that needs first messages from real '
                      'employers, a population this project has never held. Step 2.',
            'why_it_still_matters': 'if the corpus is NOT shaped like any candidate boundary, '
                                    'the boundary is refuted before a user is ever recruited, '
                                    'and step 2 need not be run at all.',
        },
        'why_each_population': {
            'A_gate_corpus_400': 'AUTHORED BY US from the same source families as the facts '
                                 '(R21). Coverage here measures what we BUILT.',
            'B_natural_48': 'the only population with live routes AND adjudicated verdicts, so '
                            'the only one where in-boundary ACCURACY is knowable.',
            'C_coverage_gap_12': 'authored as the deliberately HARD half. A hit rate here is a '
                                 'LOWER bound (R22 cuts both ways).',
            'NOT_MEASURED': 'real employers\' first messages. The decision applies there.',
        },
        'classification_axis': 'statutory trigger (who owes the obligation), NOT our subdomain '
                               'labels -- classifying by our own labels would make any boundary '
                               'we drew look well-covered by construction.',
        'actor_map': {k: {'actor': v[0], 'statutory_trigger': v[1]} for k, v in ACTOR.items()},
        'route_labels_from': 'chike.orchestrator.Orchestrator.decompose + .route -- the '
                             'production calls, not a keyword proxy',
        'population_A': {
            'n': len(rows),
            'by_actor': dict(by_actor),
            'by_actor_and_route': {k: dict(v) for k, v in by_actor_route.items()},
            'sensitivity_osha_moved_to_any_business': dict(sens),
            'boundaries': boundaries,
            'n_answerable': n_answerable,
            'superset_what_an_employer_would_be_refused': superset,
        },
        'population_B_natural_48': {
            'note': 'verdicts are the COMMITTED 2026-08-17 adjudication. The 2026-08-24 '
                    'compute/fact figure quoted in the scoping note was NEVER COMMITTED and is '
                    'therefore provisional (R18); it is re-adjudicated separately.',
            'rows': nat_rows,
            'by_boundary': nat_by_boundary,
        },
        'population_C_coverage_gap_12': {
            'rows': cov_rows,
            'by_boundary': cov_by_boundary,
        },
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(blob, f, ensure_ascii=False, indent=2)

    print(f'\nPopulation A: {len(rows)} questions')
    for k, v in by_actor.most_common():
        print(f'  {v:4d}  {k}   routes={dict(by_actor_route[k])}')
    print('\nBoundary coverage (of answerable corpus rows):')
    for name, b in boundaries.items():
        print(f"  {name:26s} {b['in_boundary']:4d}/{n_answerable}  "
              f"({b['share_of_answerable']*100:4.1f}%)  compute={b['compute_share_in_boundary']}")
    print('\nWhat an EMPLOYER would be refused:')
    for name, s in superset.items():
        print(f"  {name:26s} {s['would_be_refused']:4d}/{s['employer_relevant_rows']}  "
              f"({s['refused_share_for_an_employer']*100:4.1f}%)")
    print('\nCoverage-gap 12 hits:')
    for name, c in cov_by_boundary.items():
        print(f"  {name:26s} {c['hits_of_12']}/12")
    print(f'\n[saved] {OUT}')


if __name__ == '__main__':
    main()
