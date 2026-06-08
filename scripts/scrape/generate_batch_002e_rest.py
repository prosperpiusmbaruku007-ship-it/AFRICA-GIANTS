"""Batch 002E part 2: income_tax_deep (15) + compliance_costs (10) = 25 pairs."""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PAIRS = [
# ── INCOME TAX DEEP (15) ─────────────────────────────────────────────────────
{
    "id":"tier1a_inc_tax_deep_001_20260603","domain":"tier1a","subdomain":"income_tax_deep",
    "question_sw":"Kampuni yangu ilipata faida ya TZS 50,000,000 mwaka huu. Kodi ya kampuni ni TZS ngapi?",
    "answer_sw":"Kodi ya mapato ya kampuni (corporation tax) kwa faida ya TZS 50,000,000: Kiwango cha kawaida = 30%. Kodi = TZS 50,000,000 × 30% = TZS 15,000,000. Hii inalipwa: kwa awali (provisional tax) kwa awamu nne wakati wa mwaka — Machi, Juni, Septemba, Desemba. Tofauti yoyote kati ya kodi ya awali iliyolipwa na kodi halisi ya mwaka inalipwa au kurudishwa wakati return ya mwisho inawasilishwa ndani ya miezi 6 baada ya mwisho wa mwaka. Kampuni iliyoorodheshwa DSE inalipa 25% badala ya 30%.",
    "answer_en":"Corporation tax on profit of TZS 50,000,000: Standard rate = 30%. Tax = TZS 50,000,000 × 30% = TZS 15,000,000. This is paid: in advance (provisional tax) in four instalments during the year — March, June, September, December. Any difference between provisional tax paid and actual annual tax is settled or refunded when the final return is filed within 6 months after year end. A DSE-listed company pays 25% instead of 30%.",
    "question_en":"My company made a profit of TZS 50,000,000 this year. How much corporation tax is due?",
    "primary_source_url":"https://www.tra.go.tz/page/corporation-tax",
    "primary_source_name":"TRA Corporation Tax — worked example ITA Cap.332",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"Finance Act amendment","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_inc_tax_deep_002_20260603","domain":"tier1a","subdomain":"income_tax_deep",
    "question_sw":"Biashara yangu ina mapato ya TZS 40,000,000 kwa mwaka. Ninatumia mfumo wa kodi ya makisio (presumptive tax)?",
    "answer_sw":"Ndiyo, biashara yenye mapato ya mwaka kati ya TZS 4,000,000 na TZS 100,000,000 inaweza kutumia mfumo wa kodi ya makisio (presumptive tax). Mapato ya TZS 40,000,000 yanaingia ndani ya kiwango hiki. Kwa mfumo huu, kodi inakokotolewa kwa kiwango kilichoandikwa awali (fixed rate) kulingana na aina ya biashara na eneo — si kwenye faida halisi. Huhitajiki kutunza vitabu kamili vya uhasibu (full accounts). Hata hivyo, kama biashara yako imesajiliwa VAT au una wafanyakazi wengi, unaweza kulazimishwa kutumia mfumo wa kawaida. Angalia na TRA.",
    "answer_en":"Yes, a business with annual turnover between TZS 4,000,000 and TZS 100,000,000 may use the presumptive tax system. TZS 40,000,000 in revenue falls within this range. Under this system, tax is calculated at a predetermined rate based on the type of business and location — not on actual profit. You are not required to maintain full accounting records. However, if your business is VAT registered or you have many employees, you may be required to use the normal system. Check with TRA.",
    "question_en":"My business has revenue of TZS 40,000,000 per year. Do I use the presumptive tax system?",
    "primary_source_url":"https://www.tra.go.tz/page/corporation-tax",
    "primary_source_name":"TRA — presumptive tax system ITA Cap.332",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"Finance Act amendment to presumptive thresholds","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_inc_tax_deep_003_20260603","domain":"tier1a","subdomain":"income_tax_deep",
    "question_sw":"Biashara yangu ndogo ina mapato ya TZS 80,000,000 — nitajua vipi ikiwa ninapaswa kutumia presumptive tax au mfumo wa kawaida?",
    "answer_sw":"Vigezo vya kuchagua mfumo: Presumptive tax inatumika kama: mapato yako ya mwaka ni TZS 4M–100M NA hujasajiliwa VAT NA huhitajiki kutunza vitabu kamili vya uhasibu. Mfumo wa kawaida (normal accounts) unatumika kama: mapato yako yanazidi TZS 100M, au umesajiliwa VAT, au mwajiri mkubwa wenye wajibu wa kuandaa hesabu zilizokaguliwa. Kwa TZS 80,000,000 bado unaweza kutumia presumptive ikiwa haujasajiliwa VAT. Lakini kama mapato yako yanakaribia TZS 100M, panga mpito kwa mfumo wa kawaida mapema.",
    "answer_en":"Criteria for choosing the system: Presumptive tax applies if: your annual turnover is TZS 4M–100M AND you are not VAT registered AND you are not required to maintain full accounting records. Normal accounts system applies if: your turnover exceeds TZS 100M, or you are VAT registered, or a large employer required to prepare audited accounts. At TZS 80,000,000 you can still use presumptive if not VAT registered. But if your revenue is approaching TZS 100M, plan the transition to the normal system in advance.",
    "question_en":"My small business has revenue of TZS 80,000,000 — how do I know whether to use presumptive tax or the normal system?",
    "primary_source_url":"https://www.tra.go.tz/page/corporation-tax",
    "primary_source_name":"TRA — presumptive vs normal tax system",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"Finance Act amendment","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"disambiguation","eval_set":False
},
{
    "id":"tier1a_inc_tax_deep_004_20260603","domain":"tier1a","subdomain":"income_tax_deep",
    "question_sw":"Gari la biashara linaweza kukatwa kama gharama kwa kodi ya mapato? Kiwango cha uchakavu ni kiasi gani?",
    "answer_sw":"Ndiyo. Magari yanayotumiwa kwa biashara yanaweza kukatwa kwa njia ya uchakavu (depreciation) kwenye kodi ya mapato ya kampuni. Kiwango cha uchakavu kwa magari (motor vehicles) chini ya Sheria ya Kodi ya Mapato Tanzania ni asilimia 25 kwa mwaka kwa njia ya msingi unaopungua (reducing balance method). Kwa mfano, gari linalogharimu TZS 30,000,000: mwaka 1 = 25% × 30,000,000 = TZS 7,500,000 inakatwa. Mwaka 2 = 25% × 22,500,000 = TZS 5,625,000 inakatwa, na kadhalika. Sehemu ya matumizi ya kibinafsi (personal use) haiwezi kukatwa.",
    "answer_en":"Yes. Vehicles used for business can be deducted through depreciation (capital allowances) for corporation tax. The depreciation rate for motor vehicles under Tanzania's Income Tax Act is 25% per year using the reducing balance method. For example, a vehicle costing TZS 30,000,000: Year 1 = 25% × 30,000,000 = TZS 7,500,000 deducted. Year 2 = 25% × 22,500,000 = TZS 5,625,000 deducted, and so on. Any personal use portion cannot be deducted.",
    "question_en":"Can a business vehicle be deducted as an expense for income tax? What is the depreciation rate?",
    "primary_source_url":"https://www.tra.go.tz/page/corporation-tax",
    "primary_source_name":"TRA Corporation Tax — motor vehicle depreciation ITA Cap.332",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"Finance Act amendment to depreciation rates","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_inc_tax_deep_005_20260603","domain":"tier1a","subdomain":"income_tax_deep",
    "question_sw":"Mashine ya kiwanda inakatwa kwa kiwango gani cha uchakavu kwa kodi ya mapato Tanzania?",
    "answer_sw":"Mashine na vifaa vya kiwanda (plant and machinery) vinakatwa kwa kiwango cha uchakavu cha asilimia 37.5 kwa mwaka kwa njia ya msingi unaopungua (reducing balance). Hii ni kiwango cha haraka zaidi kuliko magari (25%) na majengo (5%). Kwa mfano, mashine inayogharimu TZS 20,000,000: mwaka 1 = 37.5% × 20,000,000 = TZS 7,500,000. Mwaka 2 = 37.5% × 12,500,000 = TZS 4,687,500. Vifaa vya kompyuta na TEHAMA pia mara nyingi vinaangukia darasa la 37.5%. Thibitisha darasa halisi la mali yako na TRA kwani madarasa yaweza kubadilika.",
    "answer_en":"Plant and machinery are depreciated at 37.5% per year using the reducing balance method. This is a faster rate than vehicles (25%) and buildings (5%). For example, machinery costing TZS 20,000,000: Year 1 = 37.5% × 20,000,000 = TZS 7,500,000. Year 2 = 37.5% × 12,500,000 = TZS 4,687,500. Computers and ICT equipment also commonly fall in the 37.5% class. Confirm the exact class for your asset with TRA as classes may change.",
    "question_en":"At what depreciation rate is factory machinery deducted for income tax in Tanzania?",
    "primary_source_url":"https://www.tra.go.tz/page/corporation-tax",
    "primary_source_name":"TRA Corporation Tax — plant and machinery depreciation ITA Cap.332",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"Finance Act amendment","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_inc_tax_deep_006_20260603","domain":"tier1a","subdomain":"income_tax_deep",
    "question_sw":"Kampuni inanunua mashine mpya ya TZS 50,000,000. Je, inaweza kudai punguzo la mwaka wa kwanza (first year allowance) la 50%?",
    "answer_sw":"Ndiyo. Sheria ya Kodi ya Mapato Tanzania ina kifungu cha punguzo la uwekezaji (investment deduction) ambacho kinaruhusu kampuni kudai 50% ya gharama ya mali mpya ya kustahili katika mwaka wa kwanza wa ununuzi, badala ya uchakavu wa kawaida. Kwa mashine ya TZS 50,000,000: punguzo la mwaka wa kwanza = 50% × 50,000,000 = TZS 25,000,000 inayokatwa mwaka wa kwanza. Kiasi kilichobaki (TZS 25,000,000) kinaendelea kukatwa kwa kiwango cha uchakavu cha kawaida katika miaka inayofuata. Thibitisha kama mali yako inastahili chaguo hili na mshauri wa kodi.",
    "answer_en":"Yes. Tanzania's Income Tax Act has an investment deduction provision that allows a company to claim 50% of the cost of qualifying new assets in the first year of purchase, instead of the normal depreciation. For machinery costing TZS 50,000,000: first year allowance = 50% × 50,000,000 = TZS 25,000,000 deducted in year one. The remaining balance (TZS 25,000,000) continues to be depreciated at the normal rate in subsequent years. Confirm whether your asset qualifies for this option with a tax consultant.",
    "question_en":"A company buys new machinery for TZS 50,000,000. Can it claim a 50% first year allowance?",
    "primary_source_url":"https://www.tra.go.tz/page/corporation-tax",
    "primary_source_name":"TRA Corporation Tax — investment deduction ITA Cap.332",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"Finance Act amendment","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_inc_tax_deep_007_20260603","domain":"tier1a","subdomain":"income_tax_deep",
    "question_sw":"Mfanyabiashara mmoja (sole trader) analipa kodi ya biashara vipi tofauti na mkurugenzi wa kampuni?",
    "answer_sw":"Mfanyabiashara mmoja (sole trader): faida ya biashara inajumuishwa kwenye mapato yake ya mtu binafsi na inatozwa kwa kiwango cha kodi ya mtu binafsi (0%–30% kwa makundi). Analipa kodi moja tu — hakuna kodi ya kampuni. Mkurugenzi wa kampuni: kampuni inalipa kodi ya kampuni (30%) kwenye faida yake. Ikiwa mkurugenzi analipwa mshahara, mshahara huo unatozwa PAYE tofauti. Ikiwa kampuni inasambaza dividendi kwa mkurugenzi kama mwanahisa, dividendi hiyo inatozwa kodi ya kizuizi ya 5%. Kwa kampuni, kuna mzigo wa kodi mbili (kodi ya kampuni + kodi ya mtu binafsi kwenye dividendi).",
    "answer_en":"Sole trader: business profit is added to their personal income and taxed at individual income tax rates (0%–30% in bands). They pay only one tax — no corporation tax. Company director: the company pays corporation tax (30%) on its profits. If the director is paid a salary, that salary is separately subject to PAYE. If the company distributes dividends to the director as a shareholder, those dividends are subject to 5% withholding tax. For a company, there is a potential double tax burden (corporation tax + personal tax on dividends).",
    "question_en":"How does a sole trader pay business tax differently from a company director?",
    "primary_source_url":"https://www.tra.go.tz/page/corporation-tax",
    "primary_source_name":"TRA — sole trader vs company tax treatment ITA Cap.332",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"Finance Act amendment","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"disambiguation","eval_set":False
},
{
    "id":"tier1a_inc_tax_deep_008_20260603","domain":"tier1a","subdomain":"income_tax_deep",
    "question_sw":"Gharama ya kukarabati ofisi (revenue expense) na gharama ya kuimarisha ofisi (capital expense) — tofauti yao kwenye kodi ya mapato ni nini?",
    "answer_sw":"Gharama ya mapato (revenue expense) kama vile ukarabati wa kawaida, upigaji wa rangi, au usakinishaji wa vipande vilivyovunjika — inakatwa mara moja kama gharama ya biashara katika mwaka inalipwa. Gharama ya mtaji (capital expense) kama vile kuongeza chumba kipya, kubadilisha mfumo mzima wa umeme, au ununuzi wa kifaa kipya — haiwezi kukatwa yote mwaka mmoja, bali inakatwa polepole kwa njia ya uchakavu (depreciation) kwa miaka mingi. Kanuni ya msingi: ikiwa inaboreshea hali ya mali au inaongeza thamani yake — ni gharama ya mtaji. Ikiwa inairejesha hali yake ya awali tu — ni gharama ya mapato.",
    "answer_en":"Revenue expense such as ordinary repairs, repainting, or replacement of broken parts — is deducted immediately as a business expense in the year it is paid. Capital expense such as adding a new room, replacing the entire electrical system, or purchasing new equipment — cannot be deducted all in one year but is gradually deducted through depreciation over many years. The basic test: if it improves the state of the asset or adds value — it is a capital expense. If it merely restores the asset to its original condition — it is a revenue expense.",
    "question_en":"Office repairs (revenue expense) vs office improvements (capital expense) — what is their difference for income tax?",
    "primary_source_url":"https://www.tra.go.tz/page/corporation-tax",
    "primary_source_name":"TRA Corporation Tax — revenue vs capital expenditure",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"stable",
    "next_review_trigger":"ITA amendment","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"disambiguation","eval_set":False
},
{
    "id":"tier1a_inc_tax_deep_009_20260603","domain":"tier1a","subdomain":"income_tax_deep",
    "question_sw":"Kampuni hakulipa kodi ya awali (provisional tax) kwa wakati. Matokeo yake ni nini?",
    "answer_sw":"Kushindwa kulipa kodi ya awali kwa wakati kunasababisha: riba ya kisheria (statutory interest) inayohesabiwaje kwa kiwango kilichowekwa na Benki Kuu na kuwa inayolipwa kama adhabu kwa TRA. Riba inakusanyika kila siku kutoka tarehe ya mwisho ya malipo iliyopita. Zaidi ya hayo, ikiwa kampuni hakulipa kodi ya awali yoyote kwa mwaka mzima na inaongeza mzigo mkubwa wa kodi mwishoni mwa mwaka, TRA inaweza kuanza hatua za utekelezaji wa kisheria. Ni muhimu kulipa awamu zote kwa wakati — Machi 31, Juni 30, Septemba 30, na Desemba 31.",
    "answer_en":"Failure to pay provisional tax on time results in: statutory interest calculated at the rate set by the Central Bank, payable as a penalty to TRA. Interest accumulates daily from the date the payment was due. Additionally, if a company pays no provisional tax at all during the year and accumulates a large tax burden at year end, TRA may initiate legal enforcement steps. It is essential to pay all instalments on time — 31 March, 30 June, 30 September, and 31 December.",
    "question_en":"A company did not pay provisional tax on time. What are the consequences?",
    "primary_source_url":"https://www.tra.go.tz/page/corporation-tax",
    "primary_source_name":"TRA Corporation Tax — provisional tax late payment",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"Finance Act amendment to interest rates","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_inc_tax_deep_010_20260603","domain":"tier1a","subdomain":"income_tax_deep",
    "question_sw":"Kodi ya awali (provisional tax) ya kampuni inakokotolewa vipi?",
    "answer_sw":"Kodi ya awali inakokotolewa kwa njia mbili zinazoruhusiwa: (1) Mbinu ya mwaka uliopita: kila awamu = kodi halisi ya mwaka uliopita ÷ 4. Hii ni njia rahisi lakini inaweza kulazimisha ulipie zaidi ikiwa faida imeshuka. (2) Mbinu ya makisio ya mwaka huu: kampuni inakadiri faida ya mwaka huu na kuhesabu kodi inayotarajiwa, kisha inagawanya katika awamu 4. Njia hii inafaa zaidi ikiwa mwaka huu una mabadiliko makubwa ya faida. Kampuni inaweza kuwasilisha makisio yaliyorekebishwa (revised estimates) ikiwa hali inabadilika. Makisio lazima yawasilishwe kwenye tarehe za awamu.",
    "answer_en":"Provisional tax is calculated using two permitted methods: (1) Prior year method: each instalment = prior year actual tax ÷ 4. This is straightforward but may lead to overpayment if profit has declined. (2) Current year estimate method: the company estimates current year profit and calculates expected tax, then divides into 4 instalments. This method is more appropriate if the current year has significant profit changes. A company may submit revised estimates if circumstances change. Estimates must be filed by the instalment due dates.",
    "question_en":"How is a company's provisional tax calculated?",
    "primary_source_url":"https://www.tra.go.tz/page/corporation-tax",
    "primary_source_name":"TRA Corporation Tax — provisional tax calculation methods",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"Finance Act amendment","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_inc_tax_deep_011_20260603","domain":"tier1a","subdomain":"income_tax_deep",
    "question_sw":"Kampuni inapata hasara kwa miaka mitatu mfululizo. TRA inachukua hatua gani?",
    "answer_sw":"Sheria ya Kodi ya Mapato Tanzania ina kifungu kinachoweza kusababisha kampuni kulipa kodi ndogo ya chini ya 0.3% ya mapato ghafi (turnover minimum tax) kama imetangaza hasara kwa miaka mitatu mfululizo na haijalipi kodi yoyote. Hii ni hatua ya kuzuia kampuni kutumia hasara za bandia. Kodi hii inalipwa hata kama kampuni ina hasara halisi. Pia, TRA inaweza kuchunguza sababu za hasara zinazoendelea kuangalia kama kuna udanganyifu wa kodi. Ikiwa hasara ni ya kweli, wasiliana na TRA mapema na uwe na rekodi nzuri za uhasibu.",
    "answer_en":"Tanzania's Income Tax Act has a provision that may require a company to pay a minimum tax of 0.3% of gross turnover if it has declared losses for three consecutive years and paid no tax. This is a measure to prevent companies from using artificial losses. This tax is paid even if the company has genuine losses. Additionally, TRA may investigate the reasons for persistent losses to check for tax fraud. If the losses are genuine, communicate with TRA early and maintain good accounting records.",
    "question_en":"A company makes losses for three consecutive years. What action does TRA take?",
    "primary_source_url":"https://www.tra.go.tz/page/corporation-tax",
    "primary_source_name":"TRA Corporation Tax — minimum tax on turnover (3-year loss)",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"Finance Act amendment","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_inc_tax_deep_012_20260603","domain":"tier1a","subdomain":"income_tax_deep",
    "question_sw":"Ushirika (partnership) unalipa kodi ya mapato ya kampuni?",
    "answer_sw":"Hapana. Ushirika (partnership) haulipi kodi ya mapato ya kampuni kwa mujibu wa Sheria ya Kodi ya Mapato Tanzania. Badala yake, kila mshirika analipa kodi binafsi kwenye sehemu yake ya faida ya ushirika kulingana na uwiano wa ugawaji uliokubaliwa (profit sharing ratio). Faida ya mshirika inajumuishwa kwenye mapato yake ya mtu binafsi na inatozwa kwa kiwango cha kodi ya mtu binafsi (0%–30%). Ushirika unahitaji kuwasilisha return ya habari (information return) TRA ikionyesha jumla ya faida na jinsi ilivyogawanywa kati ya washirika.",
    "answer_en":"No. A partnership does not pay corporation tax under Tanzania's Income Tax Act. Instead, each partner pays personal tax on their share of the partnership profit according to the agreed profit sharing ratio. The partner's share is added to their personal income and taxed at individual income tax rates (0%–30%). The partnership must file an information return with TRA showing total profit and how it was distributed among partners.",
    "question_en":"Does a partnership pay corporation tax?",
    "primary_source_url":"https://www.tra.go.tz/page/corporation-tax",
    "primary_source_name":"TRA Corporation Tax — partnership tax treatment",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"stable",
    "next_review_trigger":"ITA amendment","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_inc_tax_deep_013_20260603","domain":"tier1a","subdomain":"income_tax_deep",
    "question_sw":"Kodi ya Huduma za Kidijitali (Digital Service Tax — DST) ni nini na inatumika kwa biashara gani?",
    "answer_sw":"DST ni kodi ya asilimia 2 kwenye mapato ghafi ya huduma za kidijitali zinazotolewa Tanzania (iliyoanzishwa Finance Act 2022). Inatumika kwa: kampuni za nje zinazotoa huduma za kidijitali kwa wateja Tanzania (kama vile streaming, programu za mtandaoni, matangazo ya kidijitali), na makampuni ya ndani ya Tanzania yanayotoa huduma hizo hizo. DST inafanya kazi tofauti na VAT — DST inalipwa kwenye mapato ghafi, si thamani iliyoongezwa. Biashara zinazostahili lazima zisajiliwe kwa DST na TRA na wasilishe return za DST. Thibitisha kama huduma zako zinaathiriwa.",
    "answer_en":"DST is a 2% tax on gross revenue from digital services provided in Tanzania (introduced Finance Act 2022). It applies to: foreign companies providing digital services to Tanzanian customers (e.g. streaming, online software, digital advertising), and domestic Tanzanian companies providing the same services. DST works differently from VAT — DST is charged on gross revenue, not value added. Qualifying businesses must register for DST with TRA and file DST returns. Confirm whether your services are affected.",
    "question_en":"What is the Digital Service Tax (DST) and which businesses does it apply to?",
    "primary_source_url":"https://www.tra.go.tz/page/corporation-tax",
    "primary_source_name":"TRA — Digital Service Tax Finance Act 2022",
    "source_type":"government_portal","effective_date":"2022-07-01","decay_risk":"annual",
    "next_review_trigger":"Finance Act amendment to DST","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_inc_tax_deep_014_20260603","domain":"tier1a","subdomain":"income_tax_deep",
    "question_sw":"Gharama za mafunzo ya wafanyakazi zinaweza kukatwa kama gharama ya biashara kwenye kodi ya mapato?",
    "answer_sw":"Ndiyo. Gharama za mafunzo ya wafanyakazi (kama ada za kozi, semina, vitabu, na safari za mafunzo) zinazohusiana moja kwa moja na biashara zinaweza kukatwa kama gharama ya biashara inayoruhusiwa (allowable expense) kwenye kodi ya mapato ya kampuni. Hii ni kwa mafunzo ya kweli ya biashara — si kwa elimu ya kibinafsi ya mmiliki isiyohusiana na biashara. Hifadhi risiti na rekodi za mafunzo kwa madhumuni ya ukaguzi. Gharama za mafunzo zinazofidiwa na SDL (mifuko ya VETA) haziwezi kudaiwa tena kama gharama ya biashara.",
    "answer_en":"Yes. Employee training costs (such as course fees, seminars, books, and training travel) directly related to the business can be deducted as an allowable business expense for corporation tax. This applies to genuine business training — not personal education of the owner unrelated to the business. Keep receipts and training records for audit purposes. Training costs reimbursed by SDL (VETA funds) cannot be claimed again as a business expense.",
    "question_en":"Can employee training costs be deducted as a business expense for income tax?",
    "primary_source_url":"https://www.tra.go.tz/page/corporation-tax",
    "primary_source_name":"TRA Corporation Tax — deductible training costs",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"stable",
    "next_review_trigger":"ITA amendment on deductible expenses","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_inc_tax_deep_015_20260603","domain":"tier1a","subdomain":"income_tax_deep",
    "question_sw":"Gharama za utangazaji (advertising) na masoko (marketing) zinaweza kukatwa kwenye kodi ya mapato ya kampuni?",
    "answer_sw":"Ndiyo. Gharama za utangazaji na masoko zinazohusiana moja kwa moja na biashara — kama vile matangazo ya televisheni, redio, mitandao ya jamii, mabango, na gharama za burudani za wateja wa biashara (business entertainment) — zinaweza kukatwa kama gharama za biashara zinazoruhusiwa. Hata hivyo, gharama za burudani za wateja ambazo ni za kupita kiasi au zisizo na uhusiano wa wazi na biashara zinaweza kupingwa na TRA. Hifadhi risiti na eleza uhusiano wa kila gharama na biashara. Matumizi ya kibinafsi (burudani la familia au marafiki) hayaruhusiwi.",
    "answer_en":"Yes. Advertising and marketing costs directly related to the business — such as television, radio, social media, billboards, and business customer entertainment costs — can be deducted as allowable business expenses. However, customer entertainment costs that are excessive or have no clear business connection may be challenged by TRA. Keep receipts and document the business purpose of each cost. Personal entertainment (family or friends) is not permitted.",
    "question_en":"Can advertising and marketing costs be deducted for a company's income tax?",
    "primary_source_url":"https://www.tra.go.tz/page/corporation-tax",
    "primary_source_name":"TRA Corporation Tax — deductible marketing costs",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"stable",
    "next_review_trigger":"ITA amendment","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},

# ── COMPLIANCE COSTS (10) ──────────────────────────────────────────────────────
{
    "id":"tier1a_compliance_001_20260603","domain":"tier1a","subdomain":"compliance_costs",
    "question_sw":"Ninaweza kulipa kodi zangu zote TRA kupitia GePG mtandaoni bila kwenda ofisi?",
    "answer_sw":"Ndiyo. GePG (Government e-Payment Gateway) inaruhusu kulipa kodi nyingi za TRA mtandaoni bila kwenda ofisi, ikiwa ni pamoja na PAYE, VAT, SDL, kodi ya makisio, na kodi za nyingine. Hatua: (1) Wasilisha return yako kwenye mfumo wa TRA (IDRAS au portal ya TRA) ili kupata nambari ya rejesta ya malipo (PRN). (2) Lipa kupitia benki inayoshiriki na GePG, ATM, internet banking, au simu za pesa (M-Pesa, Airtel Money, Tigo Pesa). (3) Hifadhi uthibitisho wa malipo kwa rekodi zako. Malipo yanafanyika mara moja na yanachukuliwa kama malipo rasmi.",
    "answer_en":"Yes. GePG (Government e-Payment Gateway) allows payment of most TRA taxes online without visiting an office, including PAYE, VAT, SDL, presumptive tax, and other taxes. Steps: (1) File your return on TRA's system (IDRAS or TRA portal) to obtain a payment reference number (PRN). (2) Pay via a GePG-connected bank, ATM, internet banking, or mobile money (M-Pesa, Airtel Money, Tigo Pesa). (3) Keep the payment confirmation for your records. Payment is processed immediately and treated as official tax payment.",
    "question_en":"Can I pay all my TRA taxes via GePG online without visiting an office?",
    "primary_source_url":"https://www.tra.go.tz",
    "primary_source_name":"TRA GePG — online tax payment system",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"GePG system change","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_compliance_002_20260603","domain":"tier1a","subdomain":"compliance_costs",
    "question_sw":"Nambari ya rejesta ya malipo (PRN) ya TRA ni nini na ninaipata wapi?",
    "answer_sw":"PRN (Payment Reference Number) ni nambari ya kipekee inayotolewa na mfumo wa TRA baada ya kuwasilisha return au kutoa ombi la malipo. PRN inathibitisha kwamba malipo yanakwenda kwenye akaunti sahihi ya kodi sahihi. Unapata PRN kwa: kuwasilisha return yako kwenye IDRAS au portal ya TRA, ambapo PRN itatolewa moja kwa moja baada ya kuthibitisha return. Kisha unalipa kupitia GePG kwa kutumia PRN hiyo. Kila PRN ina muda wa kuisha (kawaida siku chache) — lipa kabla haijakwisha. Bila PRN sahihi, malipo yanaweza kutokwenda kwenye akaunti yako ya kodi.",
    "answer_en":"A PRN (Payment Reference Number) is a unique number issued by the TRA system after filing a return or making a payment request. The PRN confirms that payment is going to the correct tax account. You obtain a PRN by: filing your return on IDRAS or the TRA portal, where a PRN is generated automatically after confirming the return. You then pay via GePG using that PRN. Each PRN has an expiry period (usually a few days) — pay before it expires. Without the correct PRN, payment may not reach your tax account.",
    "question_en":"What is a TRA payment reference number (PRN) and where do I get it?",
    "primary_source_url":"https://www.tra.go.tz",
    "primary_source_name":"TRA GePG — PRN payment reference",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"TRA system change","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_compliance_003_20260603","domain":"tier1a","subdomain":"compliance_costs",
    "question_sw":"Cheti cha usafi wa kodi (tax clearance certificate) ni nini na ni lini ninahitajika?",
    "answer_sw":"Cheti cha usafi wa kodi ni hati inayotolewa na TRA inayothibitisha kwamba mlipa kodi hana deni la kodi wala madai yanayosubiri na TRA. Unahitajika wakati wa: kuomba mikataba ya Serikali (procurement / NeST tenders), kupata leseni fulani za biashara, kuomba mikopo kutoka benki fulani, kuhuisha leseni za biashara zilizosimamishwa, na kuomba vibali vya uagizaji (import permits) kwa bidhaa fulani. Kampuni au mtu binafsi inayohitaji cheti lazima iwe imetimiza wajibu wake wote wa kodi na haina madeni yanayosubiri.",
    "answer_en":"A tax clearance certificate is a document issued by TRA confirming that the taxpayer has no outstanding tax debts or pending claims with TRA. It is required when: applying for Government contracts (procurement/NeST tenders), obtaining certain business licences, applying for loans from some banks, renewing suspended business licences, and applying for import permits for certain goods. A company or individual applying for the certificate must have fulfilled all tax obligations and have no outstanding debts.",
    "question_en":"What is a tax clearance certificate and when do I need one?",
    "primary_source_url":"https://www.tra.go.tz",
    "primary_source_name":"TRA — tax clearance certificate",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"stable",
    "next_review_trigger":"TRA policy change on clearance requirements","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_compliance_004_20260603","domain":"tier1a","subdomain":"compliance_costs",
    "question_sw":"Ninaomba cheti cha usafi wa kodi TRA — itachukua muda gani?",
    "answer_sw":"Muda wa kupata cheti cha usafi wa kodi unategemea hali ya akaunti yako ya kodi na mzigo wa kazi wa TRA. Kwa kawaida: ikiwa akaunti yako ya kodi iko safi (hakuna madeni, return zote zimefungwa, malipo yote yalithibitishwa), cheti kinaweza kutolewa ndani ya siku 3–7 za kazi. Ikiwa kuna madeni yanayosubiri au return ambazo hazikuwasilishwa, utahitajika kutatua matatizo hayo kwanza. Ombi linafanywa kwenye portal ya TRA au kwa maombi ya maandishi kwenye ofisi ya TRA. Epuka kuomba siku chache kabla ya tarehe ya mwisho ya tender.",
    "answer_en":"The time to obtain a tax clearance certificate depends on the status of your tax account and TRA's workload. Generally: if your tax account is clean (no debts, all returns filed, all payments confirmed), the certificate may be issued within 3–7 working days. If there are outstanding debts or unfiled returns, you must resolve those issues first. The application is made on TRA's portal or in writing at a TRA office. Avoid applying a few days before a tender deadline.",
    "question_en":"I'm applying for a TRA tax clearance certificate — how long will it take?",
    "primary_source_url":"https://www.tra.go.tz",
    "primary_source_name":"TRA — tax clearance certificate processing time",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"stable",
    "next_review_trigger":"TRA processing time change","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_compliance_005_20260603","domain":"tier1a","subdomain":"compliance_costs",
    "question_sw":"Kampuni yangu haina cheti cha usafi wa kodi lakini inataka kushindania tender ya Serikali. Matokeo ni nini?",
    "answer_sw":"Zabuni (tender) yoyote ya Serikali inayowasilishwa bila cheti cha usafi wa kodi inayotakiwa itakataliwa moja kwa moja bila kufunguliwa. Mamlaka ya Ununuzi wa Umma Tanzania (PPRA) na taasisi zinazopokea zabuni zinahitaji cheti cha usafi wa kodi halisi kama hati ya lazima ya kushindania. Zaidi ya hayo, kama kampuni inashindwa zabuni nyingi kwa kukosa cheti cha usafi, ukaguzi wa kodi unaweza kufuata. Suluhisho: anza mchakato wa upataji wa cheti angalau wiki 2 kabla ya tarehe ya mwisho ya zabuni.",
    "answer_en":"Any Government tender submitted without the required tax clearance certificate will be rejected outright without being opened. Tanzania's Public Procurement Regulatory Authority (PPRA) and procuring entities require a valid tax clearance certificate as a mandatory document for tendering. Additionally, if a company repeatedly fails tenders due to missing clearance, a tax audit may follow. Solution: start the process of obtaining the certificate at least 2 weeks before the tender deadline.",
    "question_en":"My company has no tax clearance certificate but wants to compete for a Government tender. What is the consequence?",
    "primary_source_url":"https://www.tra.go.tz",
    "primary_source_name":"TRA + PPRA — tax clearance for government tenders",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"stable",
    "next_review_trigger":"PPA 2023 amendment or PPRA guideline change","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_compliance_006_20260603","domain":"tier1a","subdomain":"compliance_costs",
    "question_sw":"Ninajisajili kwenye mfumo wa IDRAS wa TRA mtandaoni — hatua za kimsingi ni zipi?",
    "answer_sw":"Hatua za kujiandikisha kwenye IDRAS (Integrated Domestic Revenue Administration System) ya TRA: (1) Nenda kwenye tovuti ya TRA (tra.go.tz) na bonyeza kiungo cha e-Services au IDRAS. (2) Chagua 'Register' au 'Jiandikishe' na jaza fomu kwa kutumia TIN yako iliyosajiliwa. (3) Thibitisha akaunti yako kwa njia ya barua pepe au simu. (4) Ingia kwa mara ya kwanza, seti nywila mpya, na thibitisha maelezo ya biashara yako. (5) Sasa unaweza kuwasilisha returns za PAYE, VAT, SDL na mengine, na kupata PRN za malipo. Kama una tatizo la usajili, tembelea ofisi yoyote ya TRA ukiwa na TIN na hati za biashara.",
    "answer_en":"Steps to register on TRA's IDRAS (Integrated Domestic Revenue Administration System): (1) Go to the TRA website (tra.go.tz) and click the e-Services or IDRAS link. (2) Select 'Register' and complete the form using your registered TIN. (3) Verify your account via email or phone. (4) Log in for the first time, set a new password, and confirm your business details. (5) You can now file PAYE, VAT, SDL and other returns, and obtain payment PRNs. If you have a registration problem, visit any TRA office with your TIN and business documents.",
    "question_en":"I'm registering on TRA's IDRAS system online — what are the basic steps?",
    "primary_source_url":"https://www.tra.go.tz",
    "primary_source_name":"TRA — IDRAS online portal registration",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual",
    "next_review_trigger":"TRA portal system upgrade","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_compliance_007_20260603","domain":"tier1a","subdomain":"compliance_costs",
    "question_sw":"Kwa muda gani lazima nihifadhi rekodi za biashara kwa madhumuni ya ukaguzi wa TRA?",
    "answer_sw":"Chini ya Sheria ya Kodi ya Mapato Tanzania, mlipa kodi lazima ahifadhi rekodi zake za uhasibu kwa angalau miaka 5 baada ya mwaka wa mapato unaoathirika. Hii inahusisha: vitabu vya uhasibu, risiti za mauzo na manunuzi, orodha za mishahara (payroll), return za kodi zilizotumwa, maelezo ya benki, mikataba, na nyaraka zote za kuhusiana na biashara. Kwa udanganyifu uliodhibitiwa, TRA inaweza kufungua ukaguzi kwa miaka ya nyuma zaidi ya 5. Hifadhi rekodi za kidijitali na karatasi zote kwa usalama — hasara ya rekodi wakati wa ukaguzi inaweza kusababisha tathmini kubwa.",
    "answer_en":"Under Tanzania's Income Tax Act, a taxpayer must keep their accounting records for at least 5 years after the relevant year of income. This includes: accounting books, sales and purchase receipts, payroll records, filed tax returns, bank statements, contracts, and all business-related documents. For confirmed fraud cases, TRA may open investigations beyond 5 years. Keep all digital and paper records securely — loss of records during an audit may result in a large assessment.",
    "question_en":"For how long must I keep business records for TRA audit purposes?",
    "primary_source_url":"https://www.tra.go.tz",
    "primary_source_name":"TRA — record keeping requirements ITA Cap.332",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"stable",
    "next_review_trigger":"ITA amendment on record keeping period","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_compliance_008_20260603","domain":"tier1a","subdomain":"compliance_costs",
    "question_sw":"TRA inaweza kusamehe adhabu za kodi (penalty waiver)? Ninaomba vipi?",
    "answer_sw":"Ndiyo. TRA ina nguvu ya kusamehe adhabu (penalty waiver) kwa mujibu wa Sheria ya Kodi ya Mapato chini ya masharti fulani. Vigezo vinavyozingatiwa: hali ya nguvu ya lazima iliyosababisha kuchelewa (maumivu, majanga ya asili), historia nzuri ya utii wa kodi, na nia njema ya kulipa. Hatua za kuomba: (1) Lipa kodi yote ya msingi na riba kwanza. (2) Wasilisha maombi rasmi ya maandishi kwa Kamishna wa TRA ukieleza sababu za kuchelewa na hati zinazothibitisha. (3) Subiri uamuzi. Samahani nyingi zinatolewa kwa walipa kodi wa mara ya kwanza wenye rekodi nzuri. Samahani haizuii riba — riba mara nyingi italipwa hata baada ya samahani ya adhabu.",
    "answer_en":"Yes. TRA has authority to waive penalties under the Income Tax Act under certain conditions. Factors considered: force majeure circumstances causing the delay (illness, natural disasters), good compliance history, and genuine intent to pay. Steps to apply: (1) First pay all principal tax owed and any interest. (2) File a formal written application to the TRA Commissioner General explaining the reasons for the delay with supporting documents. (3) Await the decision. Many waivers are granted to first-time offenders with good records. A waiver does not cover interest — interest typically remains payable even after a penalty waiver.",
    "question_en":"Can TRA waive tax penalties (penalty waiver)? How do I apply?",
    "primary_source_url":"https://www.tra.go.tz",
    "primary_source_name":"TRA — penalty waiver application",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"stable",
    "next_review_trigger":"TRA penalty waiver policy change","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_compliance_009_20260603","domain":"tier1a","subdomain":"compliance_costs",
    "question_sw":"Kampuni yangu ni ya kwanza kukosea kulipa PAYE kwa mwezi mmoja tu. TRA itatoa samahani ya adhabu?",
    "answer_sw":"Walipa kodi wa mara ya kwanza (first-time offenders) wanaowasiliana na TRA kwa hiari kabla ya hatua za utekelezaji na ambao wana rekodi nzuri ya utii wa kodi wana uwezekano mkubwa wa kupata samahani au upunguzaji wa adhabu. Kwa kesi ya PAYE iliyochelewa mara moja: lipa PAYE yote ya msingi pamoja na riba ya kuchelewa, kisha omba rasmi samahani ya adhabu ukitaja historia yako nzuri ya utii. TRA inazingatia kila kesi kwa mtu binafsi. Samahani si ya lazima kisheria — ni uamuzi wa Kamishna. Kujitokeza mapema na kwa hiari ni sababu kubwa ya mafanikio ya ombi.",
    "answer_en":"First-time offenders who proactively approach TRA before enforcement steps and who have a good compliance history have a higher chance of receiving a waiver or reduction of penalties. For a single late PAYE case: pay all principal PAYE plus late payment interest, then formally apply for a penalty waiver citing your good compliance history. TRA considers each case individually. A waiver is not a legal right — it is the Commissioner's discretionary decision. Coming forward early and voluntarily is a major factor in a successful application.",
    "question_en":"My company is a first-time offender for failing to pay PAYE for just one month. Will TRA grant a penalty waiver?",
    "primary_source_url":"https://www.tra.go.tz",
    "primary_source_name":"TRA — first-time offender penalty relief",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"stable",
    "next_review_trigger":"TRA penalty policy change","verified_by":"pending_founder_review",
    "verified_date":"pending_founder_review","register":"business_market","pair_type":"standard","eval_set":False
},
{
    "id":"tier1a_compliance_010_20260603","domain":"tier1a","subdomain":"compliance_costs",
    "question_sw":"Ni rekodi zipi za biashara mhimu zaidi ambazo TRA inazihitaji wakati wa ukaguzi?",
    "answer_sw":"Rekodi muhimu zaidi ambazo TRA inazihitaji wakati wa ukaguzi wa biashara ni: (1) Vitabu vya uhasibu (ledgers, cash books, journals). (2) Risiti zote za mauzo (EFD/VFD receipts au risiti za mkono zilizoidhinishwa). (3) Ankara za manunuzi (purchase invoices) na stakabadhi. (4) Orodha za mishahara (payroll) na slips za mshahara. (5) Maelezo ya benki (bank statements) yanayolingana na vitabu. (6) Return za kodi zilizowasilishwa (PAYE, VAT, SDL). (7) Mikataba na wateja na wasambazaji. (8) Rekodi za hesabu za mali (asset register). Tofauti yoyote kati ya orodha hizi ni dalili ya tatizo la kodi.",
    "answer_en":"The most important records TRA requires during a business audit are: (1) Accounting books (ledgers, cash books, journals). (2) All sales receipts (EFD/VFD receipts or authorised manual receipts). (3) Purchase invoices and receipts. (4) Payroll records and payslips. (5) Bank statements consistent with the books. (6) Filed tax returns (PAYE, VAT, SDL). (7) Contracts with customers and suppliers. (8) Asset register records. Any discrepancy between these records is a sign of a tax problem.",
    "question_en":"What are the most important business records that TRA requires during an audit?",
    "primary_source_url":"https://www.tra.go.tz",
    "primary_source_name":"TRA — audit required records",
    "source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"stable",
    "next_review_trigger":"TRA audit methodology change","verified_by":"pending_founder_review",
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

print(f"income_tax_deep + compliance_costs: {len(filtered)} new pairs, {skipped} skipped")
print(f"batch_002 now has {len(all_pairs)} pairs")
