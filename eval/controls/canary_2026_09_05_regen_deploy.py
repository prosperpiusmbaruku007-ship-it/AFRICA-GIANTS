# -*- coding: utf-8 -*-
"""R16 canary set for the 2026-09-05 regen deploy (183-row index closing 4 known gaps:
efd_not_every_business's stale-content fix, vat_standard_rate's ask-aligned rewrite,
efd_receipt_per_transaction_no_minimum's new fact, and nat_36's displacement guard --
same underlying row as the first fix).

WHY THESE ROWS. Four probes are the guards' OWN verbatim query from kaggle/
regenerate_rag_e5.py's critical_queries (loaded via AST, never retyped -- R24), covering
every fact this regen actually changed. A fifth is a standard negative (an ordinary
in-scope compute question that must still answer correctly, unaffected by any of this
regen's changes) -- R16's required negative case, proving the redeploy didn't break
something it wasn't meant to touch.

RUN TWICE, by design: once BEFORE the redeploy (baseline -- the OLD index, still serving
the stale efd_not_every_business content and the pre-ask-alignment VAT/EFD replies) and
once AFTER (post -- the NEW 183-row index). The two artifacts are the actual evidence a
redeploy changed production behaviour, per R16's "a health check proves nothing about the
change" rule -- a --tag argument names which run produced which file.

WHAT "PASS" MEANS. Hits the LIVE endpoint and checks the MODEL'S SWAHILI REPLY for content
a correct answer must contain. A substring match on natural-language generation is a
heuristic, not a proof -- every reply is saved in full for a human read.

Written per-row (R16's structural fix): flushed to the artifact immediately after each
call returns, not batched at the end, so a dropped connection loses at most one row.

R18: committed before/with the write-up citing it.
Artifacts: eval/results/canary_2026_09_05_regen_deploy_before.json
           eval/results/canary_2026_09_05_regen_deploy_after.json
"""
import argparse
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


# (name, question, must_contain_any, must_not_contain_any, provenance)
PROBES = [
    ('efd_not_every_business (Q16 verbatim) -- the 5-week stale-content fix',
     CQ['EFD not-every-business (Q16 verbatim)'],
     ['HAKUNA', 'hakuna kizingiti', 'bila kujali'],
     ['11,000,000', 'milioni kumi na moja'],
     'verbatim critical_queries guard; must_not_contain is the OLD fabricated threshold'),
    ('vat_standard_rate (nat_27 displacement guard) -- ask-aligned rewrite',
     CQ['VAT standard rate (nat_27 displacement guard)'],
     ['18%', '18 %', 'asilimia 18'],
     ['14%'],
     'verbatim critical_queries guard; must_not_contain is the old wrong 14% figure'),
    ('efd_receipt_per_transaction_no_minimum (nat_37 gap-closing guard) -- new fact',
     CQ['EFD receipt required per-transaction, no minimum (nat_37 gap-closing guard)'],
     ['kila muamala', 'kila mauzo', 'lazima', 'risiti'],
     ['TZS 500', 'shilingi 500'],
     'verbatim critical_queries guard; must_not_contain is nat_37\'s original fabrication '
     '(a TZS 500 minimum-transaction EFD exemption that traces to no statute)'),
    ('EFD threshold, VAT-unregistered (nat_36 displacement guard) -- same row as fix 1',
     CQ['EFD threshold, VAT-unregistered (nat_36 displacement guard)'],
     ['HAKUNA', 'hakuna kizingiti', 'bila kujali'],
     ['11,000,000', 'milioni kumi na moja'],
     'verbatim critical_queries guard; same underlying fact as efd_not_every_business'),
    ('standard negative (ordinary in-scope compute question, must still answer correctly)',
     CQ['SDL 12-employee calculation'],
     ['3.5', '252,000'],
     [],
     'verbatim critical_queries guard; unaffected by this regen, R16 negative case'),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tag', required=True, choices=['before', 'after'],
                     help='which side of the redeploy this run is measuring')
    args = ap.parse_args()
    out = os.path.join(REPO, 'eval', 'results',
                        f'canary_2026_09_05_regen_deploy_{args.tag}.json')

    blob = {'measured': '2026-09-05', 'tag': args.tag,
            'harness': 'eval/controls/canary_2026_09_05_regen_deploy.py',
            'target': 'chike-inference (production)', 'rows': []}
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(blob, f, ensure_ascii=False, indent=2)

    for name, question, must_contain_any, must_not_contain_any, provenance in PROBES:
        r = ask(question)
        hit = any(s in r['reply'] for s in must_contain_any)
        leaked = [s for s in must_not_contain_any if s in r['reply']]
        row = {'name': name, 'question': question, 'must_contain_any': must_contain_any,
               'must_not_contain_any': must_not_contain_any, 'provenance': provenance,
               'outcome': r['outcome'], 'reply': r['reply'], 'elapsed_s': r['elapsed_s'],
               'keyword_hit': hit, 'stale_content_leaked': bool(leaked),
               'leaked_terms': leaked}
        blob['rows'].append(row)
        with open(out, 'w', encoding='utf-8') as f:
            json.dump(blob, f, ensure_ascii=False, indent=2)
        flag = 'LEAK' if leaked else ('HIT' if hit else 'MISS')
        print(f"[{flag}] {name} ({r['elapsed_s']}s): {r['reply'][:160]}")

    blob['status_counts'] = {
        'keyword_hit': sum(1 for r in blob['rows'] if r['keyword_hit']),
        'keyword_miss': sum(1 for r in blob['rows'] if not r['keyword_hit']),
        'stale_content_leaked': sum(1 for r in blob['rows'] if r['stale_content_leaked']),
        'http_error': sum(1 for r in blob['rows'] if r['outcome'] == 'ERROR'),
    }
    blob['status'] = 'COMPLETE'
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(blob, f, ensure_ascii=False, indent=2)
    print(f"\n{blob['status_counts']}")
    print(f'[saved] {out}')
    return 0 if (blob['status_counts']['keyword_miss'] == 0
                 and blob['status_counts']['stale_content_leaked'] == 0
                 and blob['status_counts']['http_error'] == 0) else 1


if __name__ == '__main__':
    sys.exit(main())
