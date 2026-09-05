# -*- coding: utf-8 -*-
"""The corporate tax domain (engine: chike/rules_engine/corporate_tax.py, routing:
chike/routing.py:651-747, facts: corporate_tax_rate/dse_25_rate_three_years_only/
minimum_turnover_tax/loss_carryforward_finance_act_2024 in scripts/locked_facts.json) has
never been exercised live, end to end, as a real user would type it. Everything that
exists for it -- the engine's branches, the routing reachability sweep
(eval/results/corporate_tax_routing_reachability_2026_09_01.json), the unit tests
(tests/test_corporate_tax_routing.py) -- calls the engine function directly or measures
routing in isolation. None of it sends a live Swahili sentence to the deployed model and
reads what a user actually gets back.

KNOWN GAP GOING IN, FOUND BY READING THE CODE BEFORE RUNNING ANYTHING (not discovered by
surprise): `corporate_tax_rate_statement()`'s s.4(8) sector-exemption branches
(agriculture/health/education permanent, tea processing 2024-07-01..2027-06-30) take a
`sector` parameter -- but chike/routing.py has NO function anywhere that extracts a
sector/industry from question text, and chike/orchestrator.py's `_answer_corporate_tax`
never passes one. The exemption is implemented and unit-tested at the engine-function
level (called directly with a hardcoded `sector=` kwarg) but is UNREACHABLE from a live
question. Probes 4/5 below are designed specifically to surface this live, not to avoid it.

7 fresh, natural-Swahili questions (business_market register, a company-owner persona --
NOT reused verbatim from any existing eval file, since this is a first-exercise of the
domain, not a regression guard) covering exactly the five cases named for this check:
standard corporate rate, partnership filing, AMT for an ordinary loss-making company, the
s.4(8) exemption (two sectors, to see if the gap is general or wording-specific), and the
DSE case (both the never-guess ask-first branch and the branch with float stated).

Adjudicated against the Income Tax Act Cap.332 + Finance Acts 2024/2025 text directly
(scratch/tra_pass/*.txt, cached primary sources -- s.4(8) at income_tax_act.txt:823-830,
FA2024 s.34 at finance_act_2024.txt:899-914, FA2025 s.60(d) at finance_act_2025.txt:
2316-2330, partnership transparency s.48(1) at income_tax_act.txt:1665-1739), not against
the locked facts alone -- the locked facts are what's being checked, not the ground truth.

Written per-row (R16's structural fix): flushed to the artifact immediately after each
call returns.

R18: committed before/with the write-up citing it.
Artifact: eval/results/corporate_domain_live_probe_2026_09_05.json
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
ENDPOINT = 'https://prosperpiusmbaruku007--chike-inference-web-endpoint.modal.run'
OUT = os.path.join(REPO, 'eval', 'results', 'corporate_domain_live_probe_2026_09_05.json')


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
    except Exception as exc:
        return {'outcome': 'ERROR', 'reply': f'{type(exc).__name__}: {str(exc)[:300]}',
                'elapsed_s': round(time.time() - t0, 1)}


# (name, question, statute_expectation)
PROBES = [
    ('standard_corporate_rate',
     'Kampuni yetu ni ya biashara ya kawaida, hatujaorodheshwa DSE. Kodi ya mapato ya '
     'kampuni tunayolipa ni asilimia ngapi?',
     '30% (First Schedule para 3(1)) -- an ordinary, non-DSE-listed company. Wrong if it '
     'states 25% or any other figure as the default.'),

    ('partnership_filing',
     'Sisi ni ubia wa maduka mawili, mimi na mwenzangu. Tunatakiwa kuwasilisha tamko la '
     'kodi ya mapato kama kampuni, au kila mmoja wetu analipa mwenyewe?',
     'Per s.48(1): the partnership itself is NOT liable for income tax and files no '
     'corporate return on its own income; each partner includes their share in their own '
     'individual return (s.48(2), s.50-51). Wrong if it says the partnership itself files '
     'and pays like a company.'),

    ('amt_ordinary_loss_making',
     'Kampuni yetu ya usafirishaji imepata hasara kwa miaka mitatu mfululizo. Sasa '
     'tutalipa kodi gani?',
     'AMT applies: 1% of the 3rd loss-year turnover (First Schedule para 3(3), as amended '
     'by FA2025 s.60(d)(ii), WEF 2025-07-01). Transport is not an exempt sector, so this '
     'is the correct default -- baseline case to contrast against probes 4/5.'),

    ('amt_agriculture_exempt_sector',
     'Kampuni yetu ya kilimo imepata hasara kwa miaka mitatu mfululizo. Je, tunapaswa '
     'kulipa hiyo kodi ya AMT?',
     'EXEMPT, permanently, no sunset (s.4(8): "shall not apply to a corporation '
     'conducting agricultural business"). Correct answer is NO/exempt. KNOWN GAP: '
     '`sector` is never extracted from question text anywhere in routing.py, so the '
     'engine cannot reach this branch live -- predict this returns the generic '
     '"AMT applies" answer, which would be WRONG for this specific company.'),

    ('amt_education_exempt_sector',
     'Shule yetu binafsi (kampuni ya elimu) imepata hasara kwa miaka mitatu mfululizo. '
     'Je, AMT inatumika kwetu?',
     'EXEMPT, permanently, no sunset (s.4(8): "...or engaged in the provision of health '
     'or education"). Same gap as probe 4, different sector wording -- checks whether '
     'the failure is general (no sector extraction at all) or specific to how '
     '"agriculture" was phrased.'),

    ('dse_listed_no_float_stated',
     'Kampuni yetu imeorodheshwa hivi karibuni katika Dar es Salaam Stock Exchange (DSE). '
     'Kodi ya mapato tunayolipa ni asilimia ngapi?',
     'Never-guess case: the 25% rate requires >=25% of equity issued to the public '
     '(First Schedule para 3(2)(a), float threshold lowered from 30% to 25% by FA2025 '
     's.60(d)(i)) -- NOT stated here. Correct behavior is to ASK for the public-float %, '
     'not assume either 25% or 30%. Wrong if it states a rate without asking.'),

    ('dse_listed_float_given',
     'Kampuni yetu imeorodheshwa DSE mwaka jana, na asilimia 30 ya hisa zetu ziko '
     'mikononi mwa umma. Kodi ya mapato tunayolipa ni asilimia ngapi?',
     '25% for 3 consecutive years from listing date, since 30% public float clears the '
     'current 25% threshold (First Schedule para 3(2)(a) as amended by FA2025 s.60(d)(i)). '
     'Wrong if it states 30% (the standard rate) or refuses to answer despite the float '
     'being given.'),
]


def main():
    blob = {'measured': '2026-09-05', 'target': 'chike-inference (production)',
            'harness': 'eval/controls/corporate_domain_live_probe_2026_09_05.py', 'rows': []}
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(blob, f, ensure_ascii=False, indent=2)

    for name, question, expectation in PROBES:
        r = ask(question)
        row = {'name': name, 'question': question, 'statute_expectation': expectation,
               'outcome': r['outcome'], 'reply': r['reply'], 'elapsed_s': r['elapsed_s'],
               'adjudication': 'NOT YET ADJUDICATED -- read reply against expectation by hand'}
        blob['rows'].append(row)
        with open(OUT, 'w', encoding='utf-8') as f:
            json.dump(blob, f, ensure_ascii=False, indent=2)
        print(f"[{name}] ({r['elapsed_s']}s): {r['reply']}")
        print()

    blob['status'] = 'COMPLETE -- adjudication pending'
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(blob, f, ensure_ascii=False, indent=2)
    print(f'[saved] {OUT}')


if __name__ == '__main__':
    main()
