# -*- coding: utf-8 -*-
"""R16 LIVE VERIFICATION for the 2026-09-24 deploy, which carries THREE changes at once:

  A. classifier  -- bare `soko la hisa` narrowed to five investing forms (ecb61b3)
  B. index       -- `brela_foreign_late_filing_penalty` citation Section XII -> Part XIII,
                    and `minimum_turnover_tax` reworded (467115b + 9c43143, via the R15 regen)
  C. routing     -- corporate gate widened: `orodheshwa`, `kodi ya makampuni`,
                    `makampuni yenye hasara`, `nadaiwa kodi` (28e5c55)

R16 says `✓ App deployed` is not verification, and a config-only change is the NORMAL path
here (A is pure config). Every row below is a request whose behaviour DIFFERS before and
after, plus negatives that must be UNCHANGED -- a change that only proves the new behaviour
can be silently over-broad.

STRUCTURAL, NOT DEFENSIVE (R16's general form). The artifact is written after EVERY ROW, each
row captures its own error instead of aborting the run, and a re-run RESUMES from the existing
artifact. A dropped Tanzanian link, a codec fault, or Ctrl-C costs one row, never the run.

WHAT THIS CAN AND CANNOT SEE. It observes REPLY TEXT only -- there is no endpoint that reports
the chosen route. So routing is verified by its OBSERVABLE SIGNATURE: ext_05's exemption
answer is only reachable through corporate_sector()=="health", which is only reachable through
the widened gate. Where a signature is ambiguous the row says so in `note` rather than
pretending to more than it measures.

Usage:  python eval/controls/verify_r16_deploy_2026_09_24.py [--resume]
Artifact: eval/results/r16_deploy_verification_2026_09_24.json
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
OUT = os.path.join(REPO, 'eval', 'results', 'r16_deploy_verification_2026_09_24.json')

# Each check: id, change under test, question, and a predicate over the reply.
# `expect` is a dict of assertions; `must_contain`/`must_not_contain` are case-insensitive.
CHECKS = [
    # ---- A. classifier narrowing -------------------------------------------------------
    {'id': 'A1_ext01_must_answer', 'change': 'A/classifier',
     'question': 'Kampuni yetu inauza vifaa vya ujenzi, hatujaorodheshwa soko la hisa. Kodi '
                 'ya mapato tunayolipa mwishoni mwa mwaka ni asilimia ngapi ya faida?',
     'must_not_contain': ['liko nje ya mada yangu', 'nje ya maarifa yangu'],
     'note': 'THE ROW THAT CAUSED THE FIX. Refused live 2026-09-05 by the bare phrase. Must '
             'now answer. Any OOC refusal string here means a STALE CONTAINER -- config-only '
             'change, no code diff, exactly R16 s core case.'},
    {'id': 'A2_investing_must_still_refuse', 'change': 'A/classifier',
     'question': 'Nataka kuwekeza kwenye soko la hisa, nianzeje?',
     'must_contain': ['nje ya mada yangu'],
     'note': 'NEGATIVE LIMB. The narrowing must not have opened a stock-market leak. If this '
             'answers, A went too far.'},
    {'id': 'A3_config_only_phrase_still_refuses', 'change': 'A/classifier (staleness probe)',
     'question': 'Kodi ya majengo ninayolipa kwa nyumba yangu ni kiasi gani?',
     'must_contain': ['nje ya mada yangu'],
     'note': 'R16 STALENESS DIAGNOSTIC, the one that settled the 2026-08-07 incident. '
             '`kodi ya majengo` is in chike_config.json but NOT in the hardcoded fallback, so '
             'a correct refusal here proves the container actually LOADED the new config '
             'rather than falling back. Read together with A1: A3 refusing while A1 also '
             'refuses means stale config; A3 refusing and A1 answering is the target state.'},

    # ---- B. index / Section XII --------------------------------------------------------
    {'id': 'B1_foreign_penalty_citation', 'change': 'B/index',
     'question': 'Tawi letu la kampuni ya kigeni limechelewa kuwasilisha ripoti ya mwaka. '
                 'Adhabu ni tofauti na kampuni za huku?',
     'must_not_contain': ['section xii', 'kifungu xii'],
     'must_contain': ['25'],
     'note': 'ext_15 verbatim. Reproduced "Section XII" live on 2026-09-05 from index row '
             '171. The USD 25 figure was always correct and must stay; only the citation was '
             'wrong. "Part XIII" is NOT asserted as must_contain: the model may answer '
             'correctly without naming the Part at all, and demanding it would fail a good '
             'reply. The stale string is the defect; its absence is the check.'},
    {'id': 'B2_amt_wording', 'change': 'B/index',
     'question': 'Kampuni yetu imepata hasara miaka mitatu mfululizo. Tunalipa kiasi gani?',
     'must_not_contain': ['chini ya asilimia 1'],
     'note': 'The second payload in the regen, staged since 2026-09-05. "kodi ya chini (AMT) '
             'ya asilimia 1" was live-read as "a tax of LESS THAN 1%". The reply must not '
             'render the rate as below 1%.'},

    # ---- C. corporate gate widening ----------------------------------------------------
    {'id': 'C1_ext03_public_float', 'change': 'C/routing',
     'question': 'Tulioorodheshwa DSE mwaka jana lakini ni asilimia 15 tu ya hisa zetu ndizo '
                 'mikononi mwa umma. Tunalipa kodi ipi?',
     'must_contain': ['30'],
     'must_not_contain': ['liko nje ya mada yangu'],
     'note': 'ext_03. 15% float is BELOW the 25% threshold, so the ordinary 30% applies. '
             'Answered 25% before the fix. Routing has no observable endpoint, so "30" is the '
             'signature -- a reply reaching 30% through the engine and one reaching it from '
             'weights are indistinguishable here, and that is stated rather than hidden.'},
    {'id': 'C2_ext05_sector_exemption', 'change': 'C/routing + R31',
     'question': 'Zahanati yetu binafsi imekuwa na hasara miaka mitatu mfululizo. Tunatakiwa '
                 'kulipa ile kodi ya makampuni yenye hasara?',
     'must_contain': ['hapana'],
     'note': 'ext_05, THE STRONGEST ROUTING SIGNATURE IN THIS FILE. corporate_sector() has '
             'returned "health" for "zahanati yetu" since 2026-09-05; the s.4(8) exemption is '
             'reachable ONLY through the widened gate. Live on 2026-09-05 this answered '
             '"Ndiyo, pay AMT" -- wrong. A "Hapana" here is near-conclusive that the route '
             'opened AND the sector was read, because nothing else produces that answer.'},
    {'id': 'C3_ext04_transport_amt', 'change': 'C/routing',
     'question': 'Kampuni yetu ya usafirishaji wa mizigo imepata hasara miaka mitatu '
                 'iliyopita mfululizo. Sasa tunadaiwa kodi gani?',
     'must_contain': ['1'],
     'must_not_contain': ['liko nje ya mada yangu'],
     'note': 'ext_04. Transport is NOT an exempt sector, so AMT at 1% applies -- the opposite '
             'branch to C2. Both must be right; C2 alone would pass a system that exempts '
             'everyone.'},
    {'id': 'C4_eval211_must_not_route', 'change': 'C/routing (the pin)',
     'question': 'Kampuni yangu imekuwa na hasara miaka 4 mfululizo — je nitaweza kupunguza '
                 'mapato ya mwaka wa 5 kwa hasara zote bila kikomo?',
     'must_not_contain': ['alternative minimum tax'],
     'note': 'THE CONSTRAINT. A loss-carryforward OFFSET-LIMIT question must not be answered '
             'as AMT applicability. Verified locally as route=none after the widening; this '
             'confirms it live. If the reply is an AMT answer, C over-triggered.'},

    # ---- standard negatives ------------------------------------------------------------
    {'id': 'N1_ordinary_fact', 'change': 'negative',
     'question': 'Ada ya kuwasilisha ripoti ya mwaka BRELA ni shilingi ngapi?',
     'must_contain': ['22,000'],
     'note': 'An ordinary fact lookup, correct before and after. Catches a deploy that broke '
             'retrieval wholesale.'},
    {'id': 'N2_ordinary_compute', 'change': 'negative',
     'question': 'Tuna wafanyakazi kumi, mishahara yote jumla milioni tano kwa mwezi. Ile ya '
                 'mafunzo ni kiasi gani?',
     'must_contain': ['175,000'],
     'note': 'SDL 3.5% x 5,000,000. A compute path untouched by all three changes.'},
    {'id': 'N3_genuine_ooc', 'change': 'negative',
     'question': 'Nina mgodi mdogo wa madini. Mrahaba tunaolipa serikalini ni asilimia ngapi?',
     'must_contain': ['nje ya'],
     'note': 'Mining royalties -- genuinely OOC, untouched by the narrowing. The refusal gate '
             'must still work on what it is for.'},
]


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


def adjudicate(check, reply):
    low = reply.lower()
    missing = [s for s in check.get('must_contain', []) if s.lower() not in low]
    present = [s for s in check.get('must_not_contain', []) if s.lower() in low]
    return ('PASS' if not missing and not present else 'FAIL'), missing, present


def main():
    resume = '--resume' in sys.argv
    blob = {'measured': '2026-09-24', 'target': 'chike-inference (production)',
            'harness': 'eval/controls/verify_r16_deploy_2026_09_24.py',
            'changes_under_test': {'A': 'classifier: soko la hisa narrowed (ecb61b3)',
                                   'B': 'index: Section XII -> Part XIII + AMT rewording '
                                        '(467115b, 9c43143, via R15 regen)',
                                   'C': 'routing: corporate gate widened (28e5c55)'},
            'rows': []}
    done = set()
    if resume and os.path.exists(OUT):
        blob = json.load(open(OUT, encoding='utf-8'))
        done = {r['id'] for r in blob['rows'] if r.get('outcome') == 'HTTP_200'}
        print(f'[resume] {len(done)} row(s) already captured')

    for i, check in enumerate(CHECKS, 1):
        if check['id'] in done:
            continue
        r = ask(check['question'])
        verdict, missing, present = (('ERROR', [], [])
                                     if r['outcome'] != 'HTTP_200'
                                     else adjudicate(check, r['reply']))
        row = dict(check)
        row.update({'outcome': r['outcome'], 'reply': r['reply'],
                    'elapsed_s': r['elapsed_s'], 'verdict': verdict,
                    'missing_required': missing, 'present_forbidden': present})
        blob['rows'] = [x for x in blob['rows'] if x['id'] != check['id']] + [row]
        with open(OUT, 'w', encoding='utf-8') as f:                # write after EVERY row
            json.dump(blob, f, ensure_ascii=False, indent=2)
        flag = {'PASS': 'OK  ', 'FAIL': 'FAIL', 'ERROR': 'ERR '}[verdict]
        print(f"[{i}/{len(CHECKS)}] {flag} {check['id']} ({r['elapsed_s']}s)")
        print(f"        {r['reply'][:150]}")
        if verdict == 'FAIL':
            if missing:
                print(f'        MISSING: {missing}')
            if present:
                print(f'        FORBIDDEN PRESENT: {present}')

    order = {c['id']: n for n, c in enumerate(CHECKS)}
    blob['rows'].sort(key=lambda r: order.get(r['id'], 999))
    counts = {v: sum(1 for r in blob['rows'] if r['verdict'] == v)
              for v in ('PASS', 'FAIL', 'ERROR')}
    blob['summary'] = counts
    blob['status'] = 'ALL PASS' if counts['FAIL'] == 0 and counts['ERROR'] == 0 else 'NOT CLEAN'
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(blob, f, ensure_ascii=False, indent=2)
    print(f"\n{counts}  -> {blob['status']}")
    print(f'[saved] {os.path.relpath(OUT, REPO)}')
    # Exit non-zero on anything unclean so this cannot be mistaken for a pass in a chain.
    sys.exit(0 if blob['status'] == 'ALL PASS' else 1)


if __name__ == '__main__':
    main()
