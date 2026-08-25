# -*- coding: utf-8 -*-
"""THE THREE 'UNANSWERABLE' DOMAINS, RECLASSIFIED AS ANSWERED. Write the facts that say so.

THE RECLASSIFICATION. Market stall dues, council service levy and business licence fees have sat
on the board as COVERAGE GAPS since 2026-08-16. They are not gaps. A council-set fee has no
national amount to hold, so **naming the office and the rule is the CORRECT answer, not a
refusal** — and recording them as gaps keeps a permanent worklist of things that cannot exist.

SOURCE. All content below is from the source pass already done on 2026-08-16
(`scratch/coverage_scoping_2026_08_16.md`), which read the **Local Government Finance Act, CAP.
290 R.E. 2019** in full (62pp) and quotes it verbatim. Nothing here is newly asserted.

⛔ A WHITELIST GAP, SURFACED RATHER THAN PAPERED OVER. The Act was read from
`mof.go.tz` — a `.go.tz` government portal that is **NOT in sources/whitelist.json** (which holds
tra, brela, nssf, osha, ppra, tanzlii, immigration, parliament and the advisory firms). Cap 290 is
also on TanzLII, which IS whitelisted, **but that URL has not been fetched, and inventing one is
precisely the citation-laundering pattern CLAUDE.md section 3 exists to stop.** So each fact cites
what was actually read and carries `_pending_whitelist`. **Adding mof.go.tz to the whitelist is a
change to a control and is the founder's call, not this script's.** It is also the reason
local-levy facts could never be sourced cleanly before.

⚠️ AND A GUARD THAT HAD TO BE NARROWED FIRST — R17's over-broad class, found by trying to use it.
`minimum_turnover_tax` carries the bare wrong_patterns `0.3%`, `asilimia 0.3` and `0.3 percent`
(minimum turnover tax is 1%, and was never 0.3%). But `check_locked_facts.check_pair` matches every
pattern against the whole answer text **with no topical scoping** — so a CORRECT service-levy pair
quoting the statutory 0.3% cap would have been flagged as a locked-fact violation. Same shape as
bare `hisa` in the OOC list.

  Cost of narrowing, measured before doing it: **the bare patterns match exactly ONE row in the
  entire corpus (datasets + eval), and it is a held-out probe QUESTION, which `check_pair` never
  scans anyway.** So narrowing loses zero live detections. The narrowed forms keep the turnover-tax
  context and are exercised in both directions by the probes written here.

R18: committed before it runs. Probes: eval/fidelity/local_levy_probes.jsonl
Artifact: eval/results/local_levy_facts_added.json
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
FACTS = os.path.join(REPO, 'scripts', 'locked_facts.json')
OUT = os.path.join(REPO, 'eval', 'results', 'local_levy_facts_added.json')

CAP290 = ('https://www.mof.go.tz/uploads/documents/en-1676544247-CHAPTER_290-THE_LOCAL_'
          'GOVERNMENT_FINANCE_ACT-01.pdf')
PENDING = ('mof.go.tz is a .go.tz government portal but is NOT in sources/whitelist.json. Cap 290 '
           'is also on TanzLII (whitelisted) but that URL has not been fetched and will not be '
           'invented (CLAUDE.md section 3). Whitelist change = founder decision.')

# --- Narrowing. Each bare pattern gains the turnover-tax context it was always about. ----------
NARROW = {
    'asilimia 0.3': r'(kodi ndogo|mauzo ghafi|turnover)[^.]{0,60}asilimia 0\.3',
    '0.3%': r'(minimum turnover tax|turnover tax|kodi ndogo ya mauzo)[^.]{0,60}0\.3%',
    '0.3 percent': r'(minimum turnover|turnover tax|kodi ndogo)[^.]{0,60}0\.3 percent',
}

NEW_FACTS = {
    # --- Service levy: a CAP, not a rate. The single most important distinction here. ----------
    'council_service_levy_is_a_cap_not_a_rate': {
        'fact': 'Ushuru wa huduma wa halmashauri (service levy): sheria inaweka KIKOMO cha '
                'asilimia 0.3 ya mauzo (bila VAT na ushuru wa bidhaa) — si kiwango kimoja cha '
                'kitaifa. Kila halmashauri hupanga chake kwa sheria ndogo, na nyingi hutoza chini '
                'ya kikomo hicho. Uliza ofisi ya mapato ya halmashauri yako kwa kiwango halisi.',
        'correct_value': 'a CEILING of 0.3% of turnover net of VAT and excise — not a rate',
        'wrong_patterns': [
            # Asserting 0.3% IS the rate. Negative lookahead/behind keeps the CAP wording legal.
            r'ushuru wa huduma[^.]{0,40}(?<!kikomo cha )(?<!hauzidi )(?<!si zaidi ya )ni '
            r'asilimia 0\.3',
            r'service levy[^.]{0,40}(?<!cap of )(?<!not exceeding )is 0\.3%',
        ],
        'primary_source': CAP290,
        'source_note': 'Local Government Finance Act Cap 290 R.E. 2019, s.7(1)(u) for urban '
                       'authorities and s.6 in identical terms for district councils: "...at the '
                       'rate not exceeding 0.3 percent of the turnover net of the value added tax '
                       'and excise duty".',
        'verified_by': 'source pass 2026-08-16, full 62pp Act read and quoted verbatim',
        'effective_date': '2019-01-01',
        'status': 'CONFIRMED',
        '_pending_whitelist': PENDING,
    },
    # --- The statute contradicts itself precisely on our most common user. --------------------
    'council_service_levy_non_corporate_conflict': {
        'fact': 'Je mfanyabiashara mmoja mmoja hulipa ushuru wa huduma? Sheria yenyewe inagongana. '
                'Kifungu 7(1)(u) cha Cap 290 kinasema hulipwa na "corporate entities au mtu '
                'yeyote anayefanya biashara akiwa na leseni", lakini Jedwali la sheria hiyo hiyo '
                'linakataza halmashauri kutoza wasio-corporate. Duka la mtu mmoja ni '
                'non-corporate. Uliza halmashauri yako na omba maelezo kwa maandishi.',
        'correct_value': 'the operative section and the Schedule disagree — do not state a '
                         'single answer',
        'wrong_patterns': [],
        'primary_source': CAP290,
        'source_note': 'Cap 290 s.7(1)(u) versus the Schedule made under s.16(1), whose '
                       '"shall not impose" column lists non-corporate entities. A '
                       'sole-proprietor duka is non-corporate. No phrasing on our side resolves '
                       'a conflict inside the statute.',
        'verified_by': 'source pass 2026-08-16',
        'effective_date': '2019-01-01',
        'status': 'CONFIRMED',
        '_pending_whitelist': PENDING,
    },
    # --- Market dues: the amount cannot exist nationally. Say so, and say who sets it. ---------
    'market_dues_no_national_amount': {
        'fact': 'Ushuru wa soko au genge ni kiasi gani? Hakuna kiwango kimoja cha kitaifa. Kiasi '
                'hupangwa chini ya Sheria ya Masoko (Cap 106) na sheria ndogo za kila '
                'halmashauri — zaidi ya halmashauri 180, kila moja na yake, na hubadilika mara '
                'kwa mara. Uliza meneja wa soko au ofisi ya mapato ya halmashauri yako.',
        'correct_value': 'no national figure exists — name the office, never an amount',
        'wrong_patterns': [],
        'primary_source': CAP290,
        'source_note': 'Cap 290 Schedule item 5(b): market stall and slab dues "as prescribed '
                       'under the Markets Ordinance (Cap.106)". Set by council by-law across '
                       '180+ LGAs with no consolidated national publication.',
        'verified_by': 'source pass 2026-08-16',
        'effective_date': '2019-01-01',
        'status': 'CONFIRMED',
        '_pending_whitelist': PENDING,
    },
    # --- The national half of market dues: who may NOT be charged. Real, useful, and nobody
    # --- had written it because the domain was filed as uncoverable.
    'market_dues_exemptions': {
        'fact': 'Nani hatozwi ushuru wa soko: Jedwali la Sheria ya Fedha za Serikali za Mitaa '
                '(Cap 290) linakataza halmashauri kutoza wakulima wanaouza mazao yao mara kwa '
                'mara, magulio yanayosimamiwa na halmashauri za vijiji, na wauzaji wadogo wa '
                'vyakula vilivyopikwa kama maandazi na samaki wa kukaanga. Ukiwa katika makundi '
                'haya na unadaiwa, omba maelezo kwa maandishi.',
        'correct_value': 'peasants selling produce on-and-off, village-council magulio, and small '
                         'cooked-food vendors are excluded',
        'wrong_patterns': [],
        'primary_source': CAP290,
        'source_note': 'Cap 290 Schedule item 5(b), "shall not impose" column, verbatim.',
        'verified_by': 'source pass 2026-08-16',
        'effective_date': '2019-01-01',
        'status': 'CONFIRMED',
        '_pending_whitelist': PENDING,
    },
    # --- Licence fees: the STRUCTURE is national and verified; the AMOUNT is blocked on source. -
    'business_licence_fee_national_schedule_local_collection': {
        'fact': 'Leseni ya biashara inagharimu kiasi gani? Ada imepangwa KITAIFA chini ya Sheria '
                'ya Leseni za Biashara, lakini leseni hutolewa na kukusanywa na halmashauri, na '
                'halmashauri hairuhusiwi kutoza zaidi ya ada iliyopangwa. Ada hutegemea aina ya '
                'biashara na eneo — jiji/manispaa, wilaya/mji, au kijiji — na kama ni leseni kuu '
                'au ya tawi. Uliza halmashauri yako kwa ada ya aina yako.',
        'correct_value': 'fee set nationally, licence issued and collected locally; council may '
                         'not exceed the prescribed fee',
        'wrong_patterns': [],
        'primary_source': CAP290,
        'source_note': 'Cap 290 Schedule: a council MAY charge the "Business Licence fee for '
                       'general merchandising as prescribed under the Business Licensing Act", '
                       'and "Fees exceeding the prescribed fee" sits in the SHALL-NOT-IMPOSE '
                       'column. Schedule structure (2014 text): ~31 categories, priced by '
                       'geography tier and principal-vs-subsidiary, local and foreign columns. '
                       'A duka sits in category 29, General Trading.',
        'verified_by': 'source pass 2026-08-16',
        'effective_date': '2019-01-01',
        'status': 'STRUCTURE CONFIRMED — AMOUNT BLOCKED',
        'unresolved_note': 'The CURRENT First Schedule has not been obtained, so NO amount is '
                           'encoded. This is the named blocker: one document unblocks the whole '
                           'domain as a lookup table.',
        '_pending_whitelist': PENDING,
    },
}


def main():
    with open(FACTS, encoding='utf-8') as f:
        facts = json.load(f)

    mt = facts['minimum_turnover_tax']
    before = list(mt['wrong_patterns'])
    narrowed = []
    for p in before:
        narrowed.append(NARROW.get(p, p))
    assert sum(1 for p in before if p in NARROW) == len(NARROW), (
        f'expected to narrow {len(NARROW)} patterns; the entry has changed — re-derive before '
        f'editing a live guard')
    mt['wrong_patterns'] = narrowed
    mt.setdefault('_narrowing_note', {})
    mt['_narrowing_note'] = (
        'Narrowed 2026-08-25. The bare forms `0.3%` / `asilimia 0.3` / `0.3 percent` matched with '
        'NO topical scoping, so a CORRECT council-service-levy pair quoting the statutory 0.3% '
        'CAP (Cap 290 s.7(1)(u)) would have been flagged as a locked-fact violation. Measured '
        'cost of narrowing: the bare patterns matched exactly ONE corpus row, a held-out probe '
        'QUESTION, which check_pair never scans. Zero live detections lost. Both directions are '
        'exercised in eval/fidelity/local_levy_probes.jsonl.')

    added = []
    for k, v in NEW_FACTS.items():
        assert k not in facts, f'{k} already exists — this script would overwrite a live fact'
        facts[k] = v
        added.append(k)

    with open(FACTS, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(facts, f, ensure_ascii=False, indent=2)
        f.write('\n')

    report = {
        'measured': '2026-08-25',
        'harness': 'scripts/add_local_levy_facts.py',
        'reclassification': 'market dues, council service levy and business licence fees move '
                            'from COVERAGE GAP to ANSWERED. A council-set fee has no national '
                            'amount, so naming the office and the rule IS the correct answer.',
        'facts_added': added,
        'fact_count_before': len(facts) - 1 - len(added),
        'fact_count_after': len(facts) - 1,
        'guard_narrowed': {'key': 'minimum_turnover_tax', 'before': before, 'after': narrowed,
                           'why': mt['_narrowing_note']},
        'whitelist_gap': {'domain': 'mof.go.tz', 'detail': PENDING,
                          'action': 'FOUNDER DECISION — not taken by this script'},
        'INERT_UNTIL_REGEN': 'R15: locked_facts.json has changed, so these facts are NOT '
                             'retrievable until kaggle/regenerate_rag_e5.py runs and the index is '
                             'rebuilt, verified, committed to BOTH chike-inference/ and kaggle/, '
                             'and Modal is redeployed. Batch this with the fee-row consolidation '
                             'rather than running two regens.',
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"added {len(added)} facts: {added}")
    print(f"locked_facts: {report['fact_count_before']} -> {report['fact_count_after']}")
    print(f"narrowed {len(NARROW)} over-broad patterns on minimum_turnover_tax")
    print(f'[saved] {OUT}')


if __name__ == '__main__':
    main()
