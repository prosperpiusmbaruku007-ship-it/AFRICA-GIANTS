"""Batch 002E part 1: paye_deep — 25 pairs."""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PAIRS = [
{
    "id":"tier1a_paye_deep_001_20260603","domain":"tier1a","subdomain":"paye_deep",
    "question_sw":"Jedwali la PAYE Tanzania kwa mwezi lina makundi mangapi ya kodi na kiwango chake ni gani?",
    "answer_sw":"Jedwali la PAYE Tanzania (Sheria ya Kodi ya Mapato, Finance Act 2025) lina makundi matano ya kodi kwa mwezi: (1) TZS 0–270,000: kiwango 0% — hakuna PAYE. (2) TZS 270,001–520,000: kiwango 9% kwenye sehemu inayozidi TZS 270,000. (3) TZS 520,001–760,000: kiwango 20% kwenye sehemu inayozidi TZS 520,000. (4) TZS 760,001–1,000,000: kiwango 25% kwenye sehemu inayozidi TZS 760,000. (5) TZS 1,000,001 na zaidi: kiwango 30% kwenye sehemu inayozidi TZS 1,000,000. Zaidi ya hayo kuna punguzo la kibinafsi (personal relief) la TZS 26,000 kwa mwezi linalokatwa kwenye PAYE iliyohesabiwa.",
    "answer_en":"Tanzania's monthly PAYE table (Income Tax Act, Finance Act 2025) has five tax bands: (1) TZS 0–270,000: 0% — no PAYE. (2) TZS 270,001–520,000: 9% on amount over TZS 270,000. (3) TZS 520,001–760,000: 20% on amount over TZS 520,000. (4) TZS 760,001–1,000,000: 25% on amount over TZS 760,000. (5) TZS 1,000,001 and above: 30% on amount over TZS 1,000,000. Additionally there is a personal relief of TZS 26,000 per month deducted from the calculated PAYE.",
    "question_en":"How many tax bands does Tanzania's monthly PAYE table have and what are the rates?",
    "primary_source_url":"https://www.tra.go.tz/page/pay-as-you-earn-paye",
    "primary_source_name":"TRA PAYE — ITA Cap.332 Finance Act 2025 tax bands",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"Finance Act amendment","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_paye_deep_002_20260603","domain":"tier1a","subdomain":"paye_deep",
    "question_sw":"Mfanyakazi anapata mshahara wa TZS 350,000 kwa mwezi. PAYE yake ni kiasi gani?",
    "answer_sw":"Mahesabu ya PAYE kwa TZS 350,000/mwezi: Hatua 1 — hesabu kodi kwenye jedwali: sehemu ya kwanza TZS 270,000 inatozwa 0% = TZS 0. Sehemu ya pili TZS 80,000 (yaani 350,000 − 270,000) inatozwa 9% = TZS 7,200. Jumla ya kodi = TZS 7,200. Hatua 2 — toa punguzo la kibinafsi: TZS 7,200 − TZS 26,000 = hasi (chini ya sifuri). Kwa hiyo PAYE inayolipwa = TZS 0. Mfanyakazi huyu halazimiki kulipa PAYE mwezi huo.",
    "answer_en":"PAYE calculation for TZS 350,000/month: Step 1 — apply tax bands: first TZS 270,000 taxed at 0% = TZS 0. Next TZS 80,000 (i.e. 350,000 − 270,000) taxed at 9% = TZS 7,200. Total calculated tax = TZS 7,200. Step 2 — deduct personal relief: TZS 7,200 − TZS 26,000 = negative (below zero). Therefore PAYE payable = TZS 0. This employee owes no PAYE that month.",
    "question_en":"An employee earns a salary of TZS 350,000 per month. How much PAYE do they owe?",
    "primary_source_url":"https://www.tra.go.tz/page/pay-as-you-earn-paye",
    "primary_source_name":"TRA PAYE — worked example ITA Cap.332 Finance Act 2025",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"Finance Act amendment to tax bands","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_paye_deep_003_20260603","domain":"tier1a","subdomain":"paye_deep",
    "question_sw":"Mfanyakazi wangu anapata TZS 600,000 kwa mwezi. PAYE inayolipwa ni TZS ngapi?",
    "answer_sw":"Mahesabu ya PAYE kwa TZS 600,000/mwezi: Kundi la 1 (TZS 0–270,000): 0% = TZS 0. Kundi la 2 (TZS 270,001–520,000): 250,000 × 9% = TZS 22,500. Kundi la 3 (TZS 520,001–600,000): 80,000 × 20% = TZS 16,000. Jumla kabla ya punguzo = TZS 38,500. Punguzo la kibinafsi = TZS 26,000. PAYE inayolipwa = TZS 38,500 − TZS 26,000 = TZS 12,500. Mwajiri anawasilisha TZS 12,500 TRA ifikapo tarehe 7 ya mwezi unaofuata.",
    "answer_en":"PAYE calculation for TZS 600,000/month: Band 1 (TZS 0–270,000): 0% = TZS 0. Band 2 (TZS 270,001–520,000): 250,000 × 9% = TZS 22,500. Band 3 (TZS 520,001–600,000): 80,000 × 20% = TZS 16,000. Total before relief = TZS 38,500. Personal relief = TZS 26,000. PAYE payable = TZS 38,500 − TZS 26,000 = TZS 12,500. The employer remits TZS 12,500 to TRA by the 7th of the following month.",
    "question_en":"My employee earns TZS 600,000 per month. How much PAYE is payable?",
    "primary_source_url":"https://www.tra.go.tz/page/pay-as-you-earn-paye",
    "primary_source_name":"TRA PAYE — worked example ITA Cap.332 Finance Act 2025",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"Finance Act amendment","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_paye_deep_004_20260603","domain":"tier1a","subdomain":"paye_deep",
    "question_sw":"Mfanyakazi anapata TZS 800,000 kwa mwezi. Hesabu PAYE yake hatua kwa hatua.",
    "answer_sw":"PAYE kwa TZS 800,000/mwezi: Kundi 1 (0–270,000): TZS 0. Kundi 2 (270,001–520,000): 250,000 × 9% = TZS 22,500. Kundi 3 (520,001–760,000): 240,000 × 20% = TZS 48,000. Kundi 4 (760,001–800,000): 40,000 × 25% = TZS 10,000. Jumla = TZS 80,500. Punguzo la kibinafsi TZS 26,000. PAYE inayolipwa = TZS 80,500 − TZS 26,000 = TZS 54,500.",
    "answer_en":"PAYE for TZS 800,000/month: Band 1 (0–270,000): TZS 0. Band 2 (270,001–520,000): 250,000 × 9% = TZS 22,500. Band 3 (520,001–760,000): 240,000 × 20% = TZS 48,000. Band 4 (760,001–800,000): 40,000 × 25% = TZS 10,000. Total = TZS 80,500. Personal relief TZS 26,000. PAYE payable = TZS 80,500 − TZS 26,000 = TZS 54,500.",
    "question_en":"An employee earns TZS 800,000 per month. Calculate their PAYE step by step.",
    "primary_source_url":"https://www.tra.go.tz/page/pay-as-you-earn-paye",
    "primary_source_name":"TRA PAYE — worked example ITA Cap.332 Finance Act 2025",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"Finance Act amendment","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_paye_deep_005_20260603","domain":"tier1a","subdomain":"paye_deep",
    "question_sw":"Meneja wangu anapata TZS 1,200,000 kwa mwezi. PAYE yake ni TZS ngapi?",
    "answer_sw":"PAYE kwa TZS 1,200,000/mwezi: Kundi 1 (0–270,000): TZS 0. Kundi 2 (270,001–520,000): 250,000 × 9% = TZS 22,500. Kundi 3 (520,001–760,000): 240,000 × 20% = TZS 48,000. Kundi 4 (760,001–1,000,000): 240,000 × 25% = TZS 60,000. Kundi 5 (1,000,001–1,200,000): 200,000 × 30% = TZS 60,000. Jumla = TZS 190,500. Punguzo la kibinafsi TZS 26,000. PAYE inayolipwa = TZS 190,500 − TZS 26,000 = TZS 164,500.",
    "answer_en":"PAYE for TZS 1,200,000/month: Band 1 (0–270,000): TZS 0. Band 2 (270,001–520,000): 250,000 × 9% = TZS 22,500. Band 3 (520,001–760,000): 240,000 × 20% = TZS 48,000. Band 4 (760,001–1,000,000): 240,000 × 25% = TZS 60,000. Band 5 (1,000,001–1,200,000): 200,000 × 30% = TZS 60,000. Total = TZS 190,500. Personal relief TZS 26,000. PAYE payable = TZS 190,500 − TZS 26,000 = TZS 164,500.",
    "question_en":"My manager earns TZS 1,200,000 per month. How much PAYE do they owe?",
    "primary_source_url":"https://www.tra.go.tz/page/pay-as-you-earn-paye",
    "primary_source_name":"TRA PAYE — worked example ITA Cap.332 Finance Act 2025",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"Finance Act amendment","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_paye_deep_006_20260603","domain":"tier1a","subdomain":"paye_deep",
    "question_sw":"Punguzo la kibinafsi (personal relief) katika PAYE Tanzania ni kiasi gani na inafanya kazi vipi?",
    "answer_sw":"Punguzo la kibinafsi ni TZS 26,000 kwa mwezi (TZS 312,000 kwa mwaka). Baada ya kuhesabu PAYE kwa kutumia jedwali la makundi ya kodi, unatoa TZS 26,000 kutoka kwenye jumla ya PAYE iliyohesabiwa. Kama PAYE iliyohesabiwa ni chini ya TZS 26,000, mfanyakazi halazimiki kulipa PAYE — punguzo halirudi kama pesa. Kwa mfano: mfanyakazi anayepata TZS 500,000 anahesabu PAYE ya TZS 20,700, kisha anatoa punguzo la TZS 26,000 → PAYE = TZS 0.",
    "answer_en":"The personal relief is TZS 26,000 per month (TZS 312,000 per year). After calculating PAYE using the tax band table, you subtract TZS 26,000 from the total calculated PAYE. If the calculated PAYE is less than TZS 26,000, the employee owes no PAYE — the relief is not refunded as cash. For example: an employee earning TZS 500,000 calculates PAYE of TZS 20,700, then deducts relief of TZS 26,000 → PAYE = TZS 0.",
    "question_en":"What is the personal relief in Tanzania's PAYE and how does it work?",
    "primary_source_url":"https://www.tra.go.tz/page/pay-as-you-earn-paye",
    "primary_source_name":"TRA PAYE — personal relief ITA Cap.332",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"Finance Act amendment to personal relief amount","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_paye_deep_007_20260603","domain":"tier1a","subdomain":"paye_deep",
    "question_sw":"Nani anastahili punguzo la kibinafsi la PAYE Tanzania?",
    "answer_sw":"Punguzo la kibinafsi la TZS 26,000/mwezi linapatikana kwa wakazi wa Tanzania (residents) wote ambao wana mapato ya ajira yanayotozwa PAYE. Raia wa Tanzania na wageni wenye makazi Tanzania wanastahili. Mfanyakazi anayefanya kazi kwa waajiri wengi anapata punguzo mara moja tu kupitia mwajiri mkuu wake (primary employer). Wageni wasio na makazi Tanzania hawastahili punguzo la kibinafsi. Mwajiri anahusika kuhakikisha punguzo linatumika kwa usahihi wakati wa kuhesabu PAYE ya mwezi.",
    "answer_en":"The personal relief of TZS 26,000/month is available to all Tanzania residents (wakazi) who have employment income subject to PAYE. Tanzanian citizens and foreigners resident in Tanzania qualify. An employee working for multiple employers receives the relief only once through their primary employer. Non-resident foreigners do not qualify for personal relief. The employer is responsible for ensuring the relief is correctly applied when calculating monthly PAYE.",
    "question_en":"Who qualifies for the PAYE personal relief in Tanzania?",
    "primary_source_url":"https://www.tra.go.tz/page/pay-as-you-earn-paye",
    "primary_source_name":"TRA PAYE — personal relief eligibility ITA Cap.332",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"Finance Act amendment","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_paye_deep_008_20260603","domain":"tier1a","subdomain":"paye_deep",
    "question_sw":"Mfanyakazi anayepata TZS 400,000 kwa mwezi analipa PAYE ngapi?",
    "answer_sw":"PAYE kwa TZS 400,000/mwezi: Kundi 1 (0–270,000): TZS 0. Kundi 2 (270,001–400,000): 130,000 × 9% = TZS 11,700. Jumla kabla ya punguzo = TZS 11,700. Punguzo la kibinafsi = TZS 26,000. Kwa sababu TZS 11,700 ni chini ya punguzo la TZS 26,000, PAYE inayolipwa = TZS 0. Mwajiri hahitajiki kuwasilisha PAYE kwa mwezi huo — lakini bado lazima atume return ya PAYE (nil return) kama inavyohitajika.",
    "answer_en":"PAYE for TZS 400,000/month: Band 1 (0–270,000): TZS 0. Band 2 (270,001–400,000): 130,000 × 9% = TZS 11,700. Total before relief = TZS 11,700. Personal relief = TZS 26,000. Since TZS 11,700 is less than the TZS 26,000 relief, PAYE payable = TZS 0. The employer does not need to remit PAYE that month — but must still file a PAYE return (nil return) as required.",
    "question_en":"An employee earning TZS 400,000 per month — how much PAYE do they pay?",
    "primary_source_url":"https://www.tra.go.tz/page/pay-as-you-earn-paye",
    "primary_source_name":"TRA PAYE — worked example ITA Cap.332 Finance Act 2025",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"Finance Act amendment","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_paye_deep_009_20260603","domain":"tier1a","subdomain":"paye_deep",
    "question_sw":"Mshahara wa kiwango cha chini zaidi kinachoanza kulipa PAYE halisi (baada ya punguzo la kibinafsi) ni TZS ngapi?",
    "answer_sw":"Kwa kuzingatia punguzo la kibinafsi la TZS 26,000/mwezi, mfanyakazi anaanza kulipa PAYE halisi wakati mshahara wake unapozidi kiwango kinachosababisha kodi ya TZS 26,000. Kwenye kundi la 9% (la pili), TZS 26,000 ÷ 9% = TZS 288,889. Kwa hiyo: mshahara wa TZS 270,000 + TZS 288,889 = TZS 558,889/mwezi ndio kiwango ambacho mfanyakazi anaanza kulipa PAYE kidogo zaidi ya sufuri. Kwa vitendo, kwa mshahara chini ya karibu TZS 559,000 PAYE ya kweli = TZS 0 baada ya punguzo la kibinafsi.",
    "answer_en":"Taking into account the personal relief of TZS 26,000/month, an employee starts paying actual PAYE when their salary exceeds the level that generates tax of TZS 26,000. In the 9% band (second band), TZS 26,000 ÷ 9% = TZS 288,889. Therefore: salary of TZS 270,000 + TZS 288,889 = TZS 558,889/month is the salary at which an employee begins paying a small positive PAYE. In practice, for salaries below approximately TZS 559,000 actual PAYE = TZS 0 after personal relief.",
    "question_en":"What is the minimum salary at which an employee actually starts paying PAYE (after personal relief)?",
    "primary_source_url":"https://www.tra.go.tz/page/pay-as-you-earn-paye",
    "primary_source_name":"TRA PAYE — effective threshold ITA Cap.332 Finance Act 2025",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"Finance Act amendment","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_paye_deep_010_20260603","domain":"tier1a","subdomain":"paye_deep",
    "question_sw":"Mwajiri anayetoa mshahara wa TZS 700,000 — PAYE ya mfanyakazi ni ngapi na mwajiri analipa nini zaidi?",
    "answer_sw":"PAYE ya mfanyakazi (TZS 700,000/mwezi): Kundi 1 (0–270,000): TZS 0. Kundi 2 (270,001–520,000): 250,000 × 9% = TZS 22,500. Kundi 3 (520,001–700,000): 180,000 × 20% = TZS 36,000. Jumla = TZS 58,500. Punguzo la kibinafsi TZS 26,000. PAYE ya mfanyakazi = TZS 32,500 (inakatwa kwenye mshahara wake). Zaidi ya hayo mwajiri analipa: NSSF 10% (sehemu ya mwajiri) = TZS 70,000; SDL 3.5% = TZS 24,500; WCF 0.5% = TZS 3,500. Hizi ni gharama za mwajiri juu ya mshahara — hazikatwi kwa mfanyakazi.",
    "answer_en":"Employee PAYE (TZS 700,000/month): Band 1 (0–270,000): TZS 0. Band 2 (270,001–520,000): 250,000 × 9% = TZS 22,500. Band 3 (520,001–700,000): 180,000 × 20% = TZS 36,000. Total = TZS 58,500. Personal relief TZS 26,000. Employee PAYE = TZS 32,500 (deducted from their salary). Additionally the employer pays: NSSF 10% (employer share) = TZS 70,000; SDL 3.5% = TZS 24,500; WCF 0.5% = TZS 3,500. These are employer costs above the salary — not deducted from the employee.",
    "question_en":"An employer paying a salary of TZS 700,000 — how much PAYE does the employee owe and what else does the employer pay?",
    "primary_source_url":"https://www.tra.go.tz/page/pay-as-you-earn-paye",
    "primary_source_name":"TRA PAYE — employer cost breakdown ITA Cap.332",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"Finance Act amendment","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_paye_deep_011_20260603","domain":"tier1a","subdomain":"paye_deep",
    "question_sw":"Jinsi ya kuhesabu mshahara wa mikono (net salary) mfanyakazi anapopata baada ya PAYE na NSSF kukatwa — mfano wa TZS 800,000.",
    "answer_sw":"Mahesabu ya mshahara wa mikono (take-home) kwa mshahara ghafi TZS 800,000/mwezi: PAYE = TZS 54,500 (kama ilivyohesabiwa). NSSF ya mfanyakazi (10%) = TZS 80,000. Jumla ya makato = TZS 134,500. Mshahara wa mikono = TZS 800,000 − TZS 134,500 = TZS 665,500. Kumbuka: WCF na SDL ni gharama za mwajiri peke yake — hazikatwi kwa mfanyakazi. NSSF ya mwajiri (10%) inalipwa tena juu ya mshahara na mwajiri.",
    "answer_en":"Take-home salary calculation for gross salary TZS 800,000/month: PAYE = TZS 54,500 (as calculated). Employee NSSF (10%) = TZS 80,000. Total deductions = TZS 134,500. Take-home salary = TZS 800,000 − TZS 134,500 = TZS 665,500. Note: WCF and SDL are employer-only costs — not deducted from the employee. The employer's NSSF share (10%) is paid additionally on top of the salary by the employer.",
    "question_en":"How do you calculate an employee's take-home (net) salary after PAYE and NSSF deductions — example with TZS 800,000.",
    "primary_source_url":"https://www.tra.go.tz/page/pay-as-you-earn-paye",
    "primary_source_name":"TRA PAYE + NSSF — net salary calculation",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"Finance Act or NSSF rate amendment","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_paye_deep_012_20260603","domain":"tier1a","subdomain":"paye_deep",
    "question_sw":"Tofauti kati ya mfanyakazi na mkandarasi (contractor) kwa madhumuni ya PAYE ni ipi?",
    "answer_sw":"Mfanyakazi (employee) yuko chini ya mkataba wa ajira — anahusika na PAYE inayokatwa na mwajiri. Mkandarasi (contractor/self-employed) ana mkataba wa huduma — analipa kodi yake mwenyewe kama mapato ya biashara au mapato ya mtu binafsi, na mwajiri anakata kodi ya kizuizi (withholding tax) badala ya PAYE. Dalili za mfanyakazi ni: masaa ya kazi yaliyowekwa na mwajiri, zana za kazi zinazotolewa na mwajiri, kazi ya pekee kwa mwajiri mmoja, na mwajiri anadhibiti jinsi kazi inavyofanywa. Kutumia mkandarasi kuweka mbali PAYE bila sababu halisi ya kibiashara ni ukwepaji wa kodi — TRA inachunguza hali hizi.",
    "answer_en":"An employee is under an employment contract — subject to PAYE deducted by the employer. A contractor/self-employed person has a service contract — they pay their own tax as business income or individual income, and the payer deducts withholding tax instead of PAYE. Signs of an employee include: working hours set by the employer, tools provided by the employer, working exclusively for one employer, and the employer controlling how the work is done. Using contractor status to avoid PAYE without genuine business reason is tax evasion — TRA investigates these situations.",
    "question_en":"What is the difference between an employee and a contractor for PAYE purposes?",
    "primary_source_url":"https://www.tra.go.tz/page/pay-as-you-earn-paye",
    "primary_source_name":"TRA PAYE — employee vs contractor classification",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"stable",
    "next_review_trigger":"ITA amendment on employment definition","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"disambiguation","eval_set":False
},
{
    "id":"tier1a_paye_deep_013_20260603","domain":"tier1a","subdomain":"paye_deep",
    "question_sw":"Kampuni yangu inajaribu kuorodhesha wafanyakazi kama wakandarasi kuepuka PAYE. Hatari gani?",
    "answer_sw":"Kutoa hali ya ukandarasi kwa mfanyakazi halisi (misclassification) ni ukwepaji wa kodi kwa mujibu wa Sheria ya Kodi ya Mapato Tanzania. TRA ina mamlaka ya: kutoa tathmini ya PAYE ya nyuma kwa miaka yote ya ukandarasi wa uongo, kuongeza adhabu ya 100% ya PAYE iliyokosekana, kutoza riba ya 16% kwa mwaka kwa kila mwezi uliopita, na kufungua mashtaka ya jinai dhidi ya watendaji wa kampuni. Kanuni ya kutumia ni: kama ukweli wa hali unaonyesha ajira, ni ajira — jina la mkataba halibadilishi hali ya kisheria.",
    "answer_en":"Labelling a genuine employee as a contractor (misclassification) is tax evasion under Tanzania's Income Tax Act. TRA has authority to: issue a back assessment of PAYE for all years of false contractor status, add a 100% penalty on the missing PAYE, charge 16% per annum interest for every month that has passed, and open criminal proceedings against company officers. The test to apply is: if the facts of the situation show employment, it is employment — the name of the contract does not change the legal status.",
    "question_en":"My company is trying to classify employees as contractors to avoid PAYE. What is the risk?",
    "primary_source_url":"https://www.tra.go.tz/page/pay-as-you-earn-paye",
    "primary_source_name":"TRA PAYE — misclassification risk and penalties",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"stable",
    "next_review_trigger":"ITA enforcement policy change","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"adversarial","eval_set":False
},
{
    "id":"tier1a_paye_deep_014_20260603","domain":"tier1a","subdomain":"paye_deep",
    "question_sw":"PAYE inahesabiwaje kwa mfanyakazi wa saa — analipwa TZS 3,000 kwa saa na anafanya kazi masaa 80 kwa mwezi?",
    "answer_sw":"Mshahara wa mwezi: 80 saa × TZS 3,000 = TZS 240,000. Kwa sababu TZS 240,000 iko chini ya kiwango cha kwanza cha PAYE cha TZS 270,000 (0%), na pia ni chini ya kiwango ambacho punguzo la kibinafsi kinaweza kufikia, PAYE = TZS 0. Mwajiri hahitajiki kukata PAYE kwa mwezi huo. Hata hivyo, ikiwa mfanyakazi huyu ana ajira nyingine na jumla ya mapato yake yanazidi TZS 559,000 kwa mwezi, atakuwa na PAYE ya kulipa kupitia return yake ya mtu binafsi.",
    "answer_en":"Monthly salary: 80 hours × TZS 3,000 = TZS 240,000. Since TZS 240,000 falls within the first PAYE band at TZS 270,000 (0%), and is also below the level where personal relief can reach, PAYE = TZS 0. The employer does not need to deduct PAYE that month. However, if this employee has other employment and their total income exceeds TZS 559,000 per month, they will have PAYE to pay through their individual tax return.",
    "question_en":"How is PAYE calculated for an hourly worker — paid TZS 3,000 per hour and works 80 hours per month?",
    "primary_source_url":"https://www.tra.go.tz/page/pay-as-you-earn-paye",
    "primary_source_name":"TRA PAYE — hourly worker calculation",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"Finance Act amendment","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_paye_deep_015_20260603","domain":"tier1a","subdomain":"paye_deep",
    "question_sw":"Mwajiri analipa PAYE ifikapo tarehe ngapi ya mwezi na inawasilishwa vipi?",
    "answer_sw":"PAYE inapaswa kulipwa na kuwasilishwa TRA ifikapo tarehe 7 ya mwezi unaofuata mwezi wa malipo ya mshahara. Kwa mfano, PAYE ya mshahara wa Januari inalipwa ifikapo Februari 7. Uwasilishaji unafanywa kupitia mfumo wa mtandaoni wa TRA (IDRAS) au GePG. Mwajiri anawasilisha: fomu ya PAYE return ikionyesha jumla ya mishahara iliyolipwa na PAYE inayodaiwa, pamoja na malipo ya pesa halisi. Kuchelewa kulipa (hata siku moja) kunasababisha adhabu ya 5% ya PAYE isiyolipwa kwa kila mwezi pamoja na riba ya 16% kwa mwaka.",
    "answer_en":"PAYE must be paid and filed with TRA by the 7th of the month following the month of salary payment. For example, PAYE on January salaries is due by 7 February. Filing is done via TRA's online system (IDRAS) or GePG. The employer submits: a PAYE return form showing total salaries paid and PAYE due, along with the actual cash payment. Late payment (even by one day) incurs a 5% penalty on unpaid PAYE per month plus 16% per annum interest.",
    "question_en":"By what date must an employer pay PAYE and how is it submitted?",
    "primary_source_url":"https://www.tra.go.tz/page/pay-as-you-earn-paye",
    "primary_source_name":"TRA PAYE — filing deadline and payment method",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"TRA administrative circular","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_paye_deep_016_20260603","domain":"tier1a","subdomain":"paye_deep",
    "question_sw":"Mshahara wa mfanyakazi unabadilika kutoka TZS 500,000 hadi TZS 900,000 kuanzia Aprili. PAYE ya Aprili inahesabiwaje?",
    "answer_sw":"PAYE ya Aprili inategemea mshahara mpya wa TZS 900,000. Mwajiri anahesabu kwa mwezi huo peke yake: Kundi 1 (0–270,000): TZS 0. Kundi 2 (270,001–520,000): 250,000 × 9% = TZS 22,500. Kundi 3 (520,001–760,000): 240,000 × 20% = TZS 48,000. Kundi 4 (760,001–900,000): 140,000 × 25% = TZS 35,000. Jumla = TZS 105,500. Punguzo la kibinafsi TZS 26,000. PAYE ya Aprili = TZS 79,500. Hakuna marekebisho ya nyuma kwa miezi iliyopita.",
    "answer_en":"April PAYE is based on the new salary of TZS 900,000. The employer calculates for that month alone: Band 1 (0–270,000): TZS 0. Band 2 (270,001–520,000): 250,000 × 9% = TZS 22,500. Band 3 (520,001–760,000): 240,000 × 20% = TZS 48,000. Band 4 (760,001–900,000): 140,000 × 25% = TZS 35,000. Total = TZS 105,500. Personal relief TZS 26,000. April PAYE = TZS 79,500. No retrospective adjustment for prior months.",
    "question_en":"An employee's salary changes from TZS 500,000 to TZS 900,000 from April. How is April's PAYE calculated?",
    "primary_source_url":"https://www.tra.go.tz/page/pay-as-you-earn-paye",
    "primary_source_name":"TRA PAYE — mid-year salary change",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"Finance Act amendment","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_paye_deep_017_20260603","domain":"tier1a","subdomain":"paye_deep",
    "question_sw":"PAYE inatumika kwa mwaka au kwa mwezi? Kwa nini mwaka wote unahusika?",
    "answer_sw":"PAYE inahesabiwaje kwa msingi wa mwezi — kila mwezi mwajiri anahesabu PAYE kwenye mshahara wa mwezi huo na kuwasilisha TRA ifikapo tarehe 7 ya mwezi unaofuata. Hata hivyo, mwaka wote unafaa kwa sababu: mfanyakazi anaweza kuwa na mapato mengine (kutoka vyanzo vingine) ambayo yanabadilisha kiwango halisi cha kodi. Ikiwa PAYE inayokatwa na waajiri wote kwa mwaka wote ni kidogo kuliko kodi halisi ya mwaka, mfanyakazi lazima alipe tofauti kupitia return ya mtu binafsi. Kwa mfanyakazi mmoja na mwajiri mmoja tu, hesabu ya mwezi mara 12 kawaida inatoa jibu sahihi.",
    "answer_en":"PAYE is calculated on a monthly basis — each month the employer calculates PAYE on that month's salary and remits to TRA by the 7th of the following month. However, the full year matters because: an employee may have other income (from other sources) that changes their actual tax rate. If PAYE withheld by all employers for the full year is less than the actual annual tax owed, the employee must pay the difference through an individual tax return. For a single employee with a single employer, monthly calculation × 12 generally produces the correct answer.",
    "question_en":"Is PAYE calculated monthly or annually? Why does the full year matter?",
    "primary_source_url":"https://www.tra.go.tz/page/pay-as-you-earn-paye",
    "primary_source_name":"TRA PAYE — monthly vs annual basis",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"stable",
    "next_review_trigger":"ITA amendment","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_paye_deep_018_20260603","domain":"tier1a","subdomain":"paye_deep",
    "question_sw":"Kampuni yangu haina wafanyakazi wa kulipa mwezi huu. Je, lazima niwasilishe return ya PAYE (nil return)?",
    "answer_sw":"Ndiyo. Hata kama hakuna mshahara uliojulishwa mwezi huo, mwajiri aliyesajiliwa kwa PAYE lazima awasilishe return ya PAYE (nil return) ikionyesha maelezo yenye 'hakuna malipo' — yaani return inayoonyesha TZS 0 kwa mwezi huo. Kushindwa kuwasilisha nil return kunaweza kusababisha adhabu za kuchelewa kana kwamba kulikuwa na PAYE ya kulipa. Ili kuepuka adhabu hizi, wasilisha nil return kwa wakati hata wakati hakuna mshahara.",
    "answer_en":"Yes. Even if no salary was paid that month, an employer registered for PAYE must file a nil PAYE return showing 'no payments' — i.e. a return declaring TZS 0 for that month. Failure to file a nil return may attract late filing penalties as if PAYE was due. To avoid these penalties, file a nil return on time even when there is no payroll.",
    "question_en":"My company has no employees to pay this month. Must I still file a PAYE return (nil return)?",
    "primary_source_url":"https://www.tra.go.tz/page/pay-as-you-earn-paye",
    "primary_source_name":"TRA PAYE — nil return obligation",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"stable",
    "next_review_trigger":"TRA administrative circular","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_paye_deep_019_20260603","domain":"tier1a","subdomain":"paye_deep",
    "question_sw":"Mfanyakazi wa simu (casual worker) anayefanya kazi siku 10 tu kwa mwezi analipa PAYE vipi?",
    "answer_sw":"Wafanyakazi wa simu (casual workers) wanaolipwa kwa siku au wiki wanakabiliwa na PAYE kwa njia sawa na wafanyakazi wa kawaida — yaani jumla ya malipo yao ya mwezi inahesabiwa na kisha PAYE inakokotolewa. Ikiwa mfanyakazi anapata TZS 15,000 kwa siku × 10 siku = TZS 150,000/mwezi, hii iko chini ya kiwango cha PAYE (hata kabla ya punguzo la kibinafsi), kwa hiyo PAYE = TZS 0. Mwajiri bado anahitajika kuweka rekodi za malipo ya wafanyakazi wa simu kwa madhumuni ya ukaguzi.",
    "answer_en":"Casual workers paid per day or week are subject to PAYE in the same way as regular employees — their total monthly payments are calculated and then PAYE is computed. If a casual worker earns TZS 15,000 per day × 10 days = TZS 150,000/month, this is below the PAYE threshold (even before personal relief), so PAYE = TZS 0. The employer is still required to keep records of casual worker payments for audit purposes.",
    "question_en":"A casual worker works only 10 days per month — how do they pay PAYE?",
    "primary_source_url":"https://www.tra.go.tz/page/pay-as-you-earn-paye",
    "primary_source_name":"TRA PAYE — casual worker treatment",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"Finance Act amendment","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"rural_conversational","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_paye_deep_020_20260603","domain":"tier1a","subdomain":"paye_deep",
    "question_sw":"Mstahimilivu wa kodi ya PAYE (PAYE threshold) kwa mwaka mzima ni TZS ngapi?",
    "answer_sw":"Kiwango cha mwaka ambacho mfanyakazi anaanza kulipa PAYE halisi (baada ya punguzo la kibinafsi) ni kama ifuatavyo: Kwa mwaka wote, punguzo la kibinafsi la TZS 312,000 (yaani TZS 26,000 × 12) linakatwa kutoka kodi iliyohesabiwa. Mfanyakazi anayepata chini ya karibu TZS 6,706,000 kwa mwaka (≈ TZS 559,000 kwa mwezi × 12) mara nyingi halazimiki kulipa PAYE yoyote baada ya punguzo la kibinafsi. Kwa mapato zaidi ya hayo, PAYE itaanza kulipwa. Thibitisha kwa hesabu kamili kwa mwaka wako maalum.",
    "answer_en":"The annual income level at which an employee starts paying actual PAYE (after personal relief) is approximately as follows: For the full year, personal relief of TZS 312,000 (i.e. TZS 26,000 × 12) is deducted from calculated tax. An employee earning below approximately TZS 6,706,000 per year (≈ TZS 559,000 per month × 12) generally owes no PAYE after personal relief. For income above that level, PAYE starts to become payable. Confirm with a full calculation for your specific year.",
    "question_en":"What is the annual PAYE threshold in Tanzania — the salary level above which an employee starts paying PAYE?",
    "primary_source_url":"https://www.tra.go.tz/page/pay-as-you-earn-paye",
    "primary_source_name":"TRA PAYE — annual threshold ITA Cap.332 Finance Act 2025",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"Finance Act amendment","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_paye_deep_021_20260603","domain":"tier1a","subdomain":"paye_deep",
    "question_sw":"PAYE inalipwa na nani — mfanyakazi au mwajiri?",
    "answer_sw":"PAYE ni kodi ya mfanyakazi — ni wajibu wa mfanyakazi kisheria. Lakini mwajiri ndiye anayebeba jukumu la kuikata kutoka mshahara na kuiwasilisha TRA kwa niaba ya mfanyakazi. Ikiwa mwajiri hakukata PAYE, mwajiri ndiye anayeadhibiwa kisheria na TRA — si mfanyakazi. Hata hivyo, mfanyakazi bado anaweza kulazimishwa kulipa kodi yake binafsi ikiwa mwajiri hakufanya hivyo. Kwa vitendo: mwajiri anakata → anawasilisha TRA → mfanyakazi anapata mshahara wa mikono (baada ya makato).",
    "answer_en":"PAYE is the employee's tax — it is legally the employee's obligation. However, the employer bears the responsibility of withholding it from the salary and remitting it to TRA on behalf of the employee. If the employer did not withhold PAYE, the employer is legally penalised by TRA — not the employee. However, the employee may still be required to pay their own tax personally if the employer failed to do so. In practice: employer withholds → remits to TRA → employee receives take-home salary (after deductions).",
    "question_en":"Who pays PAYE — the employee or the employer?",
    "primary_source_url":"https://www.tra.go.tz/page/pay-as-you-earn-paye",
    "primary_source_name":"TRA PAYE — responsibility for payment",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"stable",
    "next_review_trigger":"ITA amendment","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"disambiguation","eval_set":False
},
{
    "id":"tier1a_paye_deep_022_20260603","domain":"tier1a","subdomain":"paye_deep",
    "question_sw":"Kampuni yangu ina wafanyakazi 3: mmoja anapata TZS 300,000, mwingine TZS 650,000, wa tatu TZS 1,500,000. Jumla ya PAYE ya kampuni kwa mwezi ni TZS ngapi?",
    "answer_sw":"Hesabu ya kila mfanyakazi: (1) TZS 300,000: (300,000−270,000)×9%=TZS 2,700. Punguzo TZS 26,000. PAYE=TZS 0. (2) TZS 650,000: Kundi 2: 250,000×9%=22,500. Kundi 3: 130,000×20%=26,000. Jumla=48,500. Punguzo TZS 26,000. PAYE=TZS 22,500. (3) TZS 1,500,000: Kundi 2: 22,500. Kundi 3: 48,000. Kundi 4: 60,000. Kundi 5: 500,000×30%=150,000. Jumla=280,500. Punguzo TZS 26,000. PAYE=TZS 254,500. Jumla ya PAYE ya kampuni = TZS 0 + TZS 22,500 + TZS 254,500 = TZS 277,000.",
    "answer_en":"Calculation per employee: (1) TZS 300,000: (300,000−270,000)×9%=TZS 2,700. Relief TZS 26,000. PAYE=TZS 0. (2) TZS 650,000: Band 2: 250,000×9%=22,500. Band 3: 130,000×20%=26,000. Total=48,500. Relief TZS 26,000. PAYE=TZS 22,500. (3) TZS 1,500,000: Band 2: 22,500. Band 3: 48,000. Band 4: 60,000. Band 5: 500,000×30%=150,000. Total=280,500. Relief TZS 26,000. PAYE=TZS 254,500. Company total PAYE = TZS 0 + TZS 22,500 + TZS 254,500 = TZS 277,000.",
    "question_en":"My company has 3 employees: one earns TZS 300,000, another TZS 650,000, third TZS 1,500,000. What is the company's total monthly PAYE?",
    "primary_source_url":"https://www.tra.go.tz/page/pay-as-you-earn-paye",
    "primary_source_name":"TRA PAYE — multi-employee payroll example",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"Finance Act amendment","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_paye_deep_023_20260603","domain":"tier1a","subdomain":"paye_deep",
    "question_sw":"Ninaweza kulipa PAYE ya kampuni yangu kupitia simu ya pesa (M-Pesa au Airtel)?",
    "answer_sw":"Ndiyo. PAYE inaweza kulipwa kupitia simu za pesa zinazounganishwa na GePG (Government e-Payment Gateway). Hatua ni: (1) Wasilisha PAYE return kwenye mfumo wa TRA na upate nambari ya rejista ya malipo (payment reference number / PRN). (2) Nenda kwenye simu yako ya pesa (M-Pesa, Airtel Money, Tigo Pesa) na uchague chaguo la Serikali au Lipa Bili. (3) Weka PRN na kiasi cha PAYE, thibitisha malipo. (4) Hifadhi uthibitisho wa malipo. Malipo yanafanyika mara moja na yanachukuliwa kama malipo rasmi ya kodi.",
    "answer_en":"Yes. PAYE can be paid via mobile money connected to GePG (Government e-Payment Gateway). Steps: (1) File the PAYE return on TRA's system and obtain a payment reference number (PRN). (2) Go to your mobile money (M-Pesa, Airtel Money, Tigo Pesa) and select the Government or Pay Bill option. (3) Enter the PRN and PAYE amount, confirm payment. (4) Save the payment confirmation. Payment is processed immediately and is treated as official tax payment.",
    "question_en":"Can I pay my company's PAYE via mobile money (M-Pesa or Airtel)?",
    "primary_source_url":"https://www.tra.go.tz/page/pay-as-you-earn-paye",
    "primary_source_name":"TRA GePG — mobile money PAYE payment",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"GePG system change","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_paye_deep_024_20260603","domain":"tier1a","subdomain":"paye_deep",
    "question_sw":"Mfanyakazi anapata mshahara wa TZS 520,000 hasa — anaingia kwenye kundi gani la PAYE?",
    "answer_sw":"Mshahara wa TZS 520,000 uko kwenye mwisho wa kundi la pili (9%). Mahesabu: Kundi 1 (0–270,000): TZS 0. Kundi 2 (270,001–520,000): 250,000 × 9% = TZS 22,500. Jumla = TZS 22,500. Punguzo la kibinafsi = TZS 26,000. PAYE inayolipwa = TZS 0 (kwa sababu TZS 22,500 < TZS 26,000). Ikiwa mshahara utaongezeka hadi TZS 521,000, sehemu ya TZS 1,000 itatozwa kwa 20% = TZS 200 ya ziada. Hata hivyo punguzo bado linafunika, kwa hiyo PAYE itabaki TZS 0 mpaka mshahara ufikie karibu TZS 559,000.",
    "answer_en":"A salary of exactly TZS 520,000 is at the top of the second band (9%). Calculation: Band 1 (0–270,000): TZS 0. Band 2 (270,001–520,000): 250,000 × 9% = TZS 22,500. Total = TZS 22,500. Personal relief = TZS 26,000. PAYE payable = TZS 0 (because TZS 22,500 < TZS 26,000). If salary increases to TZS 521,000, the additional TZS 1,000 is taxed at 20% = TZS 200 extra. However, the relief still covers it, so PAYE remains TZS 0 until salary reaches approximately TZS 559,000.",
    "question_en":"An employee earns exactly TZS 520,000 — which PAYE band do they fall in?",
    "primary_source_url":"https://www.tra.go.tz/page/pay-as-you-earn-paye",
    "primary_source_name":"TRA PAYE — band boundary ITA Cap.332",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"Finance Act amendment","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_paye_deep_025_20260603","domain":"tier1a","subdomain":"paye_deep",
    "question_sw":"Kiwango cha juu kabisa cha PAYE Tanzania ni asilimia ngapi na kinaanza kutumika kwenye mshahara gani?",
    "answer_sw":"Kiwango cha juu kabisa cha PAYE Tanzania ni asilimia 30, kinatumika kwenye sehemu ya mshahara inayozidi TZS 1,000,000 kwa mwezi. Sehemu yoyote ya mshahara juu ya TZS 1,000,000 kwa mwezi inatozwa 30%. Kwa mfano, mfanyakazi anayepata TZS 2,000,000: sehemu ya TZS 1,000,000 ya ziada (1,000,001–2,000,000) inatozwa 30% = TZS 300,000 ya kodi kwenye sehemu hiyo peke yake. PAYE yote kabla ya punguzo la kibinafsi itakuwa TZS 130,500 + TZS 300,000 = TZS 430,500.",
    "answer_en":"The highest PAYE rate in Tanzania is 30%, applied on the portion of salary exceeding TZS 1,000,000 per month. Any part of salary above TZS 1,000,000 per month is taxed at 30%. For example, an employee earning TZS 2,000,000: the extra TZS 1,000,000 portion (1,000,001–2,000,000) is taxed at 30% = TZS 300,000 tax on that portion alone. Total PAYE before personal relief will be TZS 130,500 + TZS 300,000 = TZS 430,500.",
    "question_en":"What is the maximum PAYE rate in Tanzania and at what salary does it start?",
    "primary_source_url":"https://www.tra.go.tz/page/pay-as-you-earn-paye",
    "primary_source_name":"TRA PAYE — top rate ITA Cap.332 Finance Act 2025",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"Finance Act amendment","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
]

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dedup_path = os.path.join(ROOT, "datasets", "tier1a", "raw_sources", "existing_questions.txt")
existing_questions = set()
if os.path.exists(dedup_path):
    with open(dedup_path, encoding="utf-8") as f:
        existing_questions = {line.strip().lower() for line in f if line.strip()}

filtered, skipped = [], 0
for pair in PAIRS:
    q_sw = pair["question_sw"].lower().strip()
    q_en = pair["question_en"].lower().strip()
    if q_sw in existing_questions or q_en in existing_questions:
        print(f"  SKIP: {pair['id']}")
        skipped += 1
    else:
        filtered.append(pair)
        existing_questions.add(q_sw)
        existing_questions.add(q_en)

batch_path = os.path.join(ROOT, "datasets", "tier1a", "raw_sources", "raw_pairs_batch_002.jsonl")
existing_pairs = []
with open(batch_path, encoding="utf-8") as f:
    for line in f:
        existing_pairs.append(json.loads(line))

all_pairs = existing_pairs + filtered
with open(batch_path, "w", encoding="utf-8") as out:
    for p in all_pairs:
        out.write(json.dumps(p, ensure_ascii=False) + "\n")

with open(dedup_path, "w", encoding="utf-8") as out:
    for q in sorted(existing_questions):
        out.write(q + "\n")

print(f"paye_deep: {len(filtered)} new pairs, {skipped} skipped")
print(f"batch_002 now has {len(all_pairs)} pairs")
