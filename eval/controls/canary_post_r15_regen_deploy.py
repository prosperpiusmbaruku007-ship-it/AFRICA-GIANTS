# -*- coding: utf-8 -*-
"""R16 canary set for the 2026-08-26/28 R15 regen #2 deploy (187-row index: three consolidated
fee families, the nat_34 ask-alignment rewrite, five new local-levy facts).

WHY THESE ROWS, SPECIFICALLY. Per PROGRESS.md's "What has NOT been decided / done" note left at
the point the regen was shipped but Modal redeploy deferred: canaries are needed for the three
consolidated row families (trademark fees, company_registration_ladder, BRELA filing fees),
nat_34 specifically, the five new local-levy facts, one standard negative (an ordinary in-scope
question that must still answer correctly -- already the R16 "negative case"), and one
config-only phrase (proves the container loaded the full baked config, not the hardcoded
fallback -- CONTAINER-PATH-1 in prior cycles).

WHERE EACH QUERY CAME FROM. Six of the nine are the GUARD'S OWN verbatim query from
kaggle/regenerate_rag_e5.py's critical_queries (loaded via AST, never retyped -- R24: a canary
that paraphrases the thing it claims to check certifies the wrong input). The trademark_fees
probe has no critical_queries guard of its own; it is feegroup_curation.json's C1_controls
question, which the 2026-08-26 verbatim audit (audit_feegroup_curation_controls_verbatim.py)
already found is a hand-authored paraphrase, not verbatim eval-corpus text -- flagged as such in
this artifact's `verbatim` field rather than silently treated as equivalent to the other eight.

WHAT "PASS" MEANS HERE. Unlike the guard retrievability checker (rank against a local index),
this hits the LIVE endpoint and checks the MODEL'S SWAHILI REPLY for the fact content a correct
answer must contain (pulled from scripts/locked_facts.json for the five new facts, since the
guard's own `expected` field is an INDEX-passage anchor substring, not reply wording). A
substring match on natural-language generation is a heuristic, not a proof -- every reply is
also saved in full so a human can read the ones that don't obviously match.

Written per-row (R16's structural fix): each probe's result is flushed to the artifact
immediately after that call returns, not batched at the end, so a dropped connection loses at
most one row.

R18: committed before/with the write-up citing it.
Artifact: eval/results/canary_post_r15_regen_deploy.json
"""
import ast
import json
import os
import sys
import time
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
REGEN = os.path.join(REPO, 'kaggle', 'regenerate_rag_e5.py')
FACTS = os.path.join(REPO, 'scripts', 'locked_facts.json')
OUT = os.path.join(REPO, 'eval', 'results', 'canary_post_r15_regen_deploy.json')
ENDPOINT = 'https://prosperpiusmbaruku007--chike-inference-web-endpoint.modal.run'


def token():
    p = os.path.expanduser('~/.chike_modal_token.txt')
    return (os.environ.get('CHIKE_MODAL_TOKEN')
            or (open(p, encoding='utf-8').read().strip() if os.path.exists(p) else ''))


def load_critical_queries():
    with open(REGEN, encoding='utf-8') as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == 'critical_queries':
                    return {name: query for name, query, _ in ast.literal_eval(node.value)}
    raise SystemExit('critical_queries not found in regenerate_rag_e5.py')


CQ = load_critical_queries()


def ask(query):
    query = query[len('query: '):] if query.startswith('query: ') else query
    url = f'{ENDPOINT}?token={urllib.parse.quote(token())}'
    req = urllib.request.Request(url, data=json.dumps({'message': query}).encode('utf-8'),
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


# (name, question, must_contain-any, verbatim-source note)
PROBES = [
    ('brela_filing_fees (consolidated family)', CQ['BRELA annual return'],
     ['22,000'], 'verbatim critical_queries guard'),
    ('company_registration_ladder / nat_34 (consolidated family)',
     CQ['Company registration fee (nat_34 displacement guard)'],
     ['95,000'], 'verbatim critical_queries guard'),
    ('trademark_fees (consolidated family)',
     'Hiyo ada ya marejesho ya alama ya biashara kuchelewa, ni shilingi ngapi hasa?',
     ['30,000'], 'NOT verbatim -- feegroup_curation.json C1_controls, a hand-authored paraphrase '
                  '(see audit_feegroup_curation_controls_verbatim.py); no critical_queries guard '
                  'exists for this family'),
    ('council_service_levy_is_a_cap_not_a_rate (new fact)',
     CQ['Council service levy is a ceiling (new fact)'],
     ['0.3', 'kikomo', 'KIKOMO'], 'verbatim critical_queries guard'),
    ('council_service_levy_non_corporate_conflict (new fact)',
     CQ['Council service levy non-corporate conflict (new fact)'],
     ['gongana', 'corporate', '290', '7(1)'], 'verbatim critical_queries guard'),
    ('market_dues_no_national_amount (new fact)',
     CQ['Market dues no national amount (new fact)'],
     ['kitaifa', '106', 'halmashauri'], 'verbatim critical_queries guard'),
    ('market_dues_exemptions (new fact)',
     CQ['Market dues exemptions (new fact)'],
     ['maandazi', 'samaki'], 'verbatim critical_queries guard'),
    ('business_licence_fee_national_schedule_local_collection (new fact)',
     CQ['Business licence fee national schedule, local collection (new fact)'],
     ['KITAIFA', 'kitaifa', 'halmashauri'], 'verbatim critical_queries guard'),
    ('standard negative (ordinary in-scope question, must still answer correctly)',
     CQ['SDL 12-employee calculation'],
     ['3.5', 'asilimia'], 'verbatim critical_queries guard'),
    ('config-only phrase (OOC refusal; absent from the 39-phrase hardcoded fallback)',
     'Mshahara wangu ni TZS 900,000, sasa kodi ya majengo (property tax) ninayolipa ni ngapi?',
     ['nje ya mada', 'sina uhakika', 'thibitisha'],
     'verbatim -- eval/results/gate_orchestrator_combined_*.json question_sw'),
]


def main():
    blob = {'measured': '2026-08-28', 'harness': 'eval/controls/canary_post_r15_regen_deploy.py',
            'target': 'chike-inference (production, rag_fact_count=187)', 'rows': []}
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(blob, f, ensure_ascii=False, indent=2)

    for name, question, must_contain_any, provenance in PROBES:
        r = ask(question)
        hit = any(s in r['reply'] for s in must_contain_any)
        row = {'name': name, 'question': question, 'must_contain_any': must_contain_any,
               'provenance': provenance, 'outcome': r['outcome'], 'reply': r['reply'],
               'elapsed_s': r['elapsed_s'], 'keyword_hit': hit}
        blob['rows'].append(row)
        with open(OUT, 'w', encoding='utf-8') as f:
            json.dump(blob, f, ensure_ascii=False, indent=2)
        print(f"[{'HIT' if hit else 'MISS'}] {name} ({r['elapsed_s']}s): {r['reply'][:160]}")

    blob['status_counts'] = {
        'keyword_hit': sum(1 for r in blob['rows'] if r['keyword_hit']),
        'keyword_miss': sum(1 for r in blob['rows'] if not r['keyword_hit']),
        'http_error': sum(1 for r in blob['rows'] if r['outcome'] == 'ERROR'),
    }
    blob['status'] = 'COMPLETE'
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(blob, f, ensure_ascii=False, indent=2)
    print(f"\n{blob['status_counts']}")
    print(f'[saved] {OUT}')
    return 0 if blob['status_counts']['keyword_miss'] == 0 and \
        blob['status_counts']['http_error'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
