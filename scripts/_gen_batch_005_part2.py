#!/usr/bin/env python3
"""batch_005 part 2 — income_tax_adversarial (50 pairs, 051-100)"""
import json, os

OUT = "datasets/tier1a/raw_sources/raw_pairs_batch_005.jsonl"
D = "2026-06-09"
TRA = "https://www.tra.go.tz/page/corporation-tax"
TRA_N = "Tanzania Revenue Authority — Corporation Tax"
TRA_IT = "https://www.tra.go.tz/page/income-tax"
TRA_IT_N = "Tanzania Revenue Authority — Income Tax"
TRA_WHT = "https://www.tra.go.tz/page/withholding-tax"
TRA_WHT_N = "Tanzania Revenue Authority — Withholding Tax"
PWC = "https://taxsummaries.pwc.com/tanzania/individual/taxes-on-personal-income"
PWC_N = "PWC Tanzania Tax Summaries — Individual Income"
GP = "government_portal"
T1A = "tier1_advisory"
ANN = "annual"
ST = "stable"

def p(id_, sub, q_sw, a_sw, q_en, a_en, url, sn, st, eff, dr, trig, reg, pt):
    return {"id": id_, "domain": "tier1a", "subdomain": sub,
            "question_sw": q_sw, "answer_sw": a_sw,
            "question_en": q_en, "answer_en": a_en,
            "primary_source_url": url, "primary_source_name": sn,
            "source_type": st, "effective_date": eff,
            "decay_risk": dr, "next_review_trigger": trig,
            "verified_by": "founder_self_review", "verified_date": D,
            "register": reg, "pair_type": pt, "eval_set": False}

pairs = [

# =====================================================================
# INCOME TAX ADVERSARIAL — corporate + individual (50 pairs, 051-100)
# Sources: TRA corporation tax, TRA income tax, PWC Tanzania
# =====================================================================

p("tier1a_income_tax_adv_051_20260609","income_tax_adversarial",
  "Kiwango cha kodi ya kampuni Tanzania ni asilimia 25 kwa kampuni zote — je, ni sahihi?",
  "Hapana. Kiwango cha kawaida cha kodi ya kampuni Tanzania ni asilimia 30. Asilimia 25 "
  "inatumika kwa kampuni zilizoorodhesha hisa kwenye Soko la Hisa la Dar es Salaam (DSE) "
  "kwa angalau asilimia 30 ya hisa zao kwa umma. Ikiwa kampuni yako haijaorodheshwa DSE, "
  "ulipa asilimia 30.",
  "The corporate income tax rate in Tanzania is 25% for all companies — is this correct?",
  "No. The standard corporate income tax rate in Tanzania is 30%. The 25% rate applies "
  "only to companies that have listed at least 30% of their shares on the Dar es Salaam "
  "Stock Exchange (DSE) for the public. If your company is not DSE-listed, you pay 30%.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "business_market", "adversarial"),

p("tier1a_income_tax_adv_052_20260609","income_tax_adversarial",
  "Kampuni mpya ya Tanzania haihitaji kulipa kodi ya mapato kwa miaka mitatu ya kwanza "
  "ya biashara — je, hii ni sera ya serikali?",
  "Hapana. Hakuna msamaha wa jumla wa kodi ya kampuni kwa miaka mitatu kwa kampuni mpya. "
  "Kampuni zote za Tanzania zinaanza kulipa kodi ya kampuni mara zinapoanza kufanya faida. "
  "Msamaha wa kodi mahususi unaweza kutolewa kwa sekta fulani (kama uwekezaji wa TIC), "
  "lakini hauitumiki kwa biashara zote mpya kwa ujumla.",
  "A new Tanzania company does not need to pay income tax for the first three years — "
  "is this government policy?",
  "No. There is no general three-year corporate tax exemption for new companies. All "
  "Tanzania companies begin paying corporate tax as soon as they make a profit. Specific "
  "tax exemptions may be granted for certain sectors (such as TIC investments), but these "
  "do not apply to all new businesses generally.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act or TIC incentive update",
  "business_market", "adversarial"),

p("tier1a_income_tax_adv_053_20260609","income_tax_adversarial",
  "Faida yote inayotolewa kama gawio (dividend) kwa mwanahisa inalipwa kodi ya kampuni "
  "na kisha kodi ya zuio — kwa hivyo mwanahisa analipishwa mara mbili. Je, hii ni kweli?",
  "Ndiyo, Tanzania inatumia mfumo ambao gawio linalipishwa kodi mbili: kwanza kodi ya "
  "kampuni asilimia 30 kwenye faida ya kampuni, kisha kodi ya zuio asilimia 10 kwenye "
  "gawio linalolipwa kwa mwanahisa mkazi. Hii ni muundo wa kawaida wa mfumo wa kodi wa "
  "kishariki ambao haupaswi kuchanganywa na kodi ya ziada isiyo halali. Asilimia 10 ya "
  "WHT kwenye gawio ni mwisho — mwanahisa mkazi haendi kulipa kodi zaidi ya kodi hiyo.",
  "All profit paid as a dividend to a shareholder is taxed at corporate tax and then "
  "withholding tax — so the shareholder is taxed twice. Is this true?",
  "Yes, Tanzania uses a classical system where dividends are taxed twice: first corporate "
  "tax at 30% on the company profit, then withholding tax at 10% on the dividend paid "
  "to a resident shareholder. This is the standard classical corporate tax structure "
  "and should not be confused with an unlawful additional levy. The 10% WHT on dividends "
  "is final — a resident shareholder does not then pay further income tax on it.",
  TRA_WHT, TRA_WHT_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "formal", "standard"),

p("tier1a_income_tax_adv_054_20260609","income_tax_adversarial",
  "Kodi ya mapato ya mtu binafsi Tanzania ni sawa kwa raia na wasio raia — je, ni kweli?",
  "Kwa ujumla, wakazi wa Tanzania (raia na wasio raia wanaoishi Tanzania zaidi ya siku "
  "183 kwa mwaka) wanalipa kodi ya mapato kwa viwango sawa vya PAYE (bendi za kodi). "
  "Tofauti kuu ipo kwa usimamizi wa kodi ya zuio (WHT): wasio raia walioajiriwa wanalipa "
  "viwango tofauti vya WHT kwenye aina fulani za mapato (kama ada za mkurugenzi) "
  "ikilinganishwa na wakazi.",
  "Tanzania individual income tax is the same for citizens and non-citizens — is this true?",
  "Generally, Tanzania residents (citizens and non-citizens living in Tanzania for more "
  "than 183 days per year) pay income tax at the same PAYE band rates. The main "
  "difference is in withholding tax treatment: employed non-residents pay different WHT "
  "rates on certain income types (such as director fees) compared to residents.",
  TRA_IT, TRA_IT_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "formal", "standard"),

p("tier1a_income_tax_adv_055_20260609","income_tax_adversarial",
  "Kodi ya mapato ya kampuni inalipwa mwishoni mwa mwaka wa fedha tu — hakuna "
  "malipo ya kati ya mwaka — je, ni sahihi?",
  "Hapana. Kampuni za Tanzania zinalazimika kulipa kodi ya awali (provisional tax) "
  "kwa awamu NNE sawa katika mwaka wa fedha — mwishoni mwa miezi ya 3, 6, 9, na 12 "
  "kutoka mwanzo wa mwaka wa fedha. Malipo ya awali yanakokotolewa kwa asilimia 100 "
  "ya kodi ya mwaka uliopita au makadirio ya mwaka wa sasa.",
  "Corporate income tax is only paid at the end of the financial year — no mid-year "
  "payments — is this correct?",
  "No. Tanzania companies are required to pay provisional tax in FOUR equal instalments "
  "during the financial year — at the end of months 3, 6, 9, and 12 from the start of "
  "the financial year. Provisional instalments are calculated at 100% of the previous "
  "year's tax or an estimate of the current year.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "business_market", "adversarial"),

p("tier1a_income_tax_adv_056_20260609","income_tax_adversarial",
  "Kampuni iliyopata hasara miaka miwili mfululizo inaweza kubeba hasara hiyo mbele "
  "bila kikomo chochote — je, ni kweli?",
  "Si kweli kamili. Hasara zinaweza kubebwa mbele (loss carry-forward) Tanzania, "
  "lakini Finance Act 2024 iliongeza kikwazo: baada ya miaka MINNE mfululizo ya hasara, "
  "asilimia 60 tu ya faida ya mwaka wa tano inaweza kutumika kulipa hasara zilizobebwa. "
  "Kwa kampuni iliyopata hasara miaka miwili tu, bado hakuna kikwazo — lakini anzisha "
  "kumbukumbu nzuri za hesabu kwa sababu kikwazo kinaingia baada ya mwaka wa nne.",
  "A company that made losses for two consecutive years can carry those losses forward "
  "without any limit — is this true?",
  "Not entirely true. Losses can be carried forward in Tanzania, but Finance Act 2024 "
  "added a restriction: after FOUR consecutive loss years, only 60% of year-five profit "
  "can be used to offset carried-forward losses. For a company that has only lost for "
  "two years, there is still no restriction — but keep good accounting records because "
  "the restriction kicks in after year four.",
  TRA, TRA_N, GP, "2024-07-01", ANN, "Finance Act amendment",
  "formal", "standard"),

p("tier1a_income_tax_adv_057_20260609","income_tax_adversarial",
  "Kodi ya zuio kwenye riba (interest) inayolipwa kwa mkazi ni asilimia 15 — je, ni sahihi?",
  "Hapana. Kodi ya zuio kwenye riba inayolipwa kwa mkazi Tanzania ni asilimia 10, "
  "si asilimia 15. Kwa wasio wakazi, kiwango ni asilimia 10 pia (kinatosha kwa "
  "biashara nyingi na makampuni ya kimataifa). Angalia mkataba wa kuzuia kutozwa "
  "kodi mara mbili (DTA) kwa nchi inayohusika kwa kiwango kilichopunguzwa.",
  "Withholding tax on interest paid to a resident is 15% — is this correct?",
  "No. Withholding tax on interest paid to a resident in Tanzania is 10%, not 15%. "
  "For non-residents, the rate is also 10% (applicable for most businesses and "
  "international companies). Check the applicable double tax agreement (DTA) for a "
  "reduced rate.",
  TRA_WHT, TRA_WHT_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "business_market", "adversarial"),

p("tier1a_income_tax_adv_058_20260609","income_tax_adversarial",
  "Mshauri wa biashara wa kujitegemea (self-employed consultant) analipa kodi "
  "ya PAYE kama mfanyakazi wa kawaida — je, ni sahihi?",
  "Hapana. Mshauri wa kujitegemea (self-employed) analipa kodi ya mapato kwa njia tofauti "
  "na mfanyakazi aliyeajiriwa. PAYE ni kwa wafanyakazi waliochukuliwa kazi rasmi na mwajiri. "
  "Mshauri wa kujitegemea anapaswa: (1) kusajili biashara yake, (2) kuwasilisha "
  "mapato yake kwenye tamko la kodi ya mwaka, na (3) kulipa kodi ya awali kama faida "
  "inayotarajiwa inazidi kizingiti.",
  "A self-employed consultant pays income tax the same way as a regular employee via "
  "PAYE — is this correct?",
  "No. A self-employed consultant pays income tax differently from an employed worker. "
  "PAYE applies to workers formally employed by an employer. A self-employed consultant "
  "must: (1) register their business, (2) submit their income on an annual tax return, "
  "and (3) pay provisional tax if expected profit exceeds the threshold.",
  TRA_IT, TRA_IT_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "business_market", "adversarial"),

p("tier1a_income_tax_adv_059_20260609","income_tax_adversarial",
  "Malipo ya kodi ya kampuni yanaweza kufanywa kwa pesa taslimu ofisini kwa TRA — "
  "je, hii ni njia inayokubalika?",
  "Hapana. TRA Tanzania inashughulikia malipo ya kodi ya kampuni kupitia mfumo wa "
  "TANEPS/PRN (Payment Reference Number) kwa benki zilizoidhinishwa, au kupitia mfumo "
  "wa malipo ya mtandaoni (e-payment). Malipo ya pesa taslimu moja kwa moja ofisini "
  "kwa kiasi kikubwa cha kodi hayakubaliwi na yanaweza kusababisha matatizo ya kiutawala. "
  "Tumia PRN kupitia benki au mfumo wa malipo ya TRA.",
  "Corporate tax payments can be made in cash at the TRA office — is this an accepted method?",
  "No. TRA Tanzania handles corporate tax payments through the TANEPS/PRN (Payment "
  "Reference Number) system at authorised banks, or through the e-payment online system. "
  "Direct cash payments at the office for large tax amounts are not accepted and can "
  "cause administrative problems. Use PRN through a bank or TRA's payment system.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA payment system update",
  "business_market", "adversarial"),

p("tier1a_income_tax_adv_060_20260609","income_tax_adversarial",
  "Kampuni ya Kiingereza yenye ofisi ndogo Tanzania (branch) inalipa kodi ya kampuni "
  "Tanzania tu kwa faida inayotokana Tanzania — je, ni sahihi?",
  "Ndiyo, kwa ujumla. Tawi (branch) la kampuni ya kigeni Tanzania linalipishwa kodi "
  "ya kampuni kwa faida inayohusishwa na shughuli za tawi hilo Tanzania. Kiwango cha "
  "kodi ya tawi (branch profits tax) ni asilimia 30. Faida inayobaki baada ya kodi ya "
  "kampuni na kuhamishwa nje ya nchi inaweza pia kuwa na kodi ya zuio ya asilimia 10.",
  "A British company with a small branch in Tanzania pays Tanzania corporate tax only "
  "on profits arising in Tanzania — is this correct?",
  "Yes, generally. A foreign company branch in Tanzania is taxed on profits attributable "
  "to the branch's Tanzania activities. The branch profits tax rate is 30%. Profits "
  "remaining after corporate tax and repatriated abroad may also attract a 10% "
  "withholding tax.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act or DTA amendment",
  "formal", "standard"),

p("tier1a_income_tax_adv_061_20260609","income_tax_adversarial",
  "Biashara ya mtu mmoja (sole trader) hailazimiki kusajiliwa kwa TRA ikiwa mauzo "
  "yake hayafiki kizingiti cha VAT — je, ni kweli?",
  "Si kweli kamili. Ingawa biashara yenye mauzo chini ya kizingiti cha VAT (TZS 200M "
  "kwa mwaka) hailazimiki kusajili VAT, LAZIMA kusajiliwa na TRA kwa ajili ya kodi "
  "ya mapato ikiwa inapata faida. Kila mtu anayefanya biashara Tanzania anapaswa kuwa "
  "na TIN na kuwasilisha tamko la kodi ya mwaka. Kusajili VAT na kusajili TRA kwa kodi "
  "ya mapato ni mambo mawili tofauti.",
  "A sole trader does not need to register with TRA if their turnover is below the "
  "VAT threshold — is this true?",
  "Not entirely true. Although a business below the VAT threshold (TZS 200M/year) does "
  "not need to register for VAT, it MUST still register with TRA for income tax if it "
  "earns a profit. Every person doing business in Tanzania should have a TIN and submit "
  "an annual tax return. VAT registration and TRA income tax registration are two "
  "separate requirements.",
  TRA_IT, TRA_IT_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "rural_conversational", "adversarial"),

p("tier1a_income_tax_adv_062_20260609","income_tax_adversarial",
  "Kampuni inaweza kupunguza kodi ya mapato kwa kununua magari ya kampuni na "
  "kuyadai kama gharama — je, inaruhusiwa?",
  "Ndiyo, lakini kwa masharti. Kampuni inaweza kudai gharama ya kushuka kwa thamani "
  "(depreciation/capital allowance) kwenye magari yaliyonunuliwa kwa madhumuni ya "
  "biashara. TRA ina ratiba ya capital allowances (asilimia 25-37.5 kulingana na aina). "
  "Hata hivyo: (1) gharama za kibinafsi haziruhusiwi kudaiwa, (2) magari ya anasa "
  "yanaweza kupunguzwa kiwango cha madai, na (3) bei ya ununuzi kamili haiwezi kudaiwa "
  "mara moja — inasambazwa kwa miaka.",
  "A company can reduce income tax by buying company cars and claiming them as expenses "
  "— is this allowed?",
  "Yes, but with conditions. A company can claim capital allowances (depreciation) on "
  "vehicles purchased for business purposes. TRA has a capital allowance schedule "
  "(25–37.5% depending on class). However: (1) personal-use expenses cannot be claimed, "
  "(2) luxury vehicles may have capped allowances, and (3) the full purchase price "
  "cannot be claimed at once — it is spread over years.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act or capital allowance schedule update",
  "business_market", "standard"),

p("tier1a_income_tax_adv_063_20260609","income_tax_adversarial",
  "Gawio linalolipwa kwa mwanahisa asiye mkazi (non-resident) lina kodi ya zuio ya "
  "asilimia 10 — sawa na mkazi — je, ni sahihi?",
  "Hapana. Kodi ya zuio kwenye gawio kwa mwanahisa asiye mkazi (non-resident) ni "
  "asilimia 10 pia, lakini angalia mikataba ya DTA. Tanzania ina mikataba ya kuepuka "
  "kodi mara mbili na nchi kadhaa (kama Uswizi, Uingereza, India) ambayo inaweza "
  "kupunguza kiwango hadi asilimia 5 au zaidi. Kagua DTA inayohusika kwa kiwango "
  "halisi kinachotumika.",
  "Dividends paid to a non-resident shareholder carry a 10% withholding tax — same "
  "as for a resident — is this correct?",
  "The base rate for withholding tax on dividends to a non-resident is also 10%, but "
  "check applicable DTA agreements. Tanzania has double tax treaties with several "
  "countries (such as Switzerland, UK, India) which may reduce the rate to 5% or more. "
  "Check the applicable DTA for the actual rate that applies.",
  TRA_WHT, TRA_WHT_N, GP, "2025-07-01", ANN, "DTA network change or Finance Act",
  "formal", "standard"),

p("tier1a_income_tax_adv_064_20260609","income_tax_adversarial",
  "Kampuni inayolipa ada za usimamizi (management fees) kwa kampuni mama ya nje "
  "ya nchi haihitaji kushikilia kodi ya zuio Tanzania — je, ni sahihi?",
  "Hapana. Ada za usimamizi (management fees) au ada za huduma za kiufundi "
  "(technical service fees) zinazolipwa kwa mtu asiye mkazi zinakatwa kodi ya zuio "
  "Tanzania. Kiwango kwa kawaida ni asilimia 15 kwa ada za usimamizi. Kushindwa "
  "kushikilia kodi hii kunafanya mlipaji (kampuni ya Tanzania) awajibike kulipa kodi "
  "hiyo pamoja na riba na adhabu.",
  "A company paying management fees to a foreign parent company does not need to "
  "withhold tax in Tanzania — is this correct?",
  "No. Management fees or technical service fees paid to a non-resident attract "
  "withholding tax in Tanzania. The rate is generally 15% on management fees. Failing "
  "to withhold makes the payer (the Tanzania company) liable to pay the tax together "
  "with interest and penalties.",
  TRA_WHT, TRA_WHT_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "formal", "adversarial"),

p("tier1a_income_tax_adv_065_20260609","income_tax_adversarial",
  "Watu binafsi wanaopata kipato cha chini ya TZS 270,000 kwa mwezi hawalipi kodi "
  "yoyote ya mapato — je, ni sahihi?",
  "Ndiyo. Mtu binafsi anayepata kipato kisichozidi TZS 270,000 kwa mwezi (band ya kwanza "
  "ya PAYE) analipa kodi ya PAYE ya asilimia 0 kwenye kipato hicho. Kizingiti hiki "
  "kinamaanisha wafanyakazi wa mshahara mdogo hawalazimiki kulipa PAYE. Hata hivyo, "
  "bado inashauriwa kusajiliwa na TIN na mwajiri bado analazimika kuwasilisha malipo "
  "ya PAYE (hata kama ni sifuri) kwenye TRA.",
  "Individuals earning below TZS 270,000 per month pay no income tax at all — is this correct?",
  "Yes. An individual earning up to TZS 270,000 per month (first PAYE band) pays 0% "
  "PAYE on that income. This threshold means low-wage workers are not required to pay "
  "PAYE. However, it is still advisable to have a TIN and the employer is still required "
  "to submit PAYE returns (even if zero) to TRA.",
  PWC, PWC_N, T1A, "2025-07-01", ANN, "Finance Act PAYE band update",
  "rural_conversational", "standard"),

p("tier1a_income_tax_adv_066_20260609","income_tax_adversarial",
  "Kodi ya mapato kwenye faida ya uuzaji wa ardhi (capital gain) Tanzania ni "
  "asilimia 30 ya faida yote — je, ni sahihi?",
  "Si sahihi kabisa. Ushuru wa mapato kutoka mauzo ya ardhi au mali za mtaji Tanzania "
  "unaweza kutofautiana. Kwa ujumla, faida ya mtaji (capital gain) kutoka uuzaji wa "
  "ardhi ya biashara inalipishwa kodi kama sehemu ya mapato ya kawaida ya biashara "
  "kwa asilimia 30 kwa kampuni. Kwa watu binafsi, kiwango kinaweza kutofautiana "
  "kulingana na aina ya mali na muda wa umiliki. Pia tofauti na withholding tax ya "
  "asilimia 10 kwenye uuzaji wa ardhi kwa mtu asiye mkazi.",
  "Income tax on capital gains from land sales in Tanzania is 30% of all profit — "
  "is this correct?",
  "Not exactly. Tax on income from land or capital asset sales in Tanzania varies. "
  "Generally, capital gain from sale of business land is taxed as ordinary business "
  "income at 30% for companies. For individuals, the rate can vary depending on the "
  "type of asset and period of ownership. Also distinguish from the 10% withholding "
  "tax on land sales by a non-resident.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "formal", "standard"),

p("tier1a_income_tax_adv_067_20260609","income_tax_adversarial",
  "Kampuni inaweza kukatia mwajiriwa wake kodi ya PAYE na haitoi risiti — "
  "mwajiriwa hana haki ya kudai ushahidi wa makato — je, ni kweli?",
  "Hapana kabisa. Mwajiriwa ana haki ya kupokea ushahidi wa makato ya PAYE — kawaida "
  "kwa njia ya slip ya mshahara (payslip) au nyaraka za mwisho wa mwaka. Mwajiriwa "
  "anaweza kutumia kumbukumbu hizi kuthibitisha malipo ya kodi yake na kudai "
  "marejesho (tax refund) ikiwa atalipishwa kodi zaidi ya kiasi kinachohitajika. "
  "Kushindwa kutoa ushahidi wa makato ni ukiukwaji wa wajibu wa mwajiri.",
  "A company can deduct PAYE from an employee and give no receipt — the employee has "
  "no right to claim evidence of deductions — is this true?",
  "Absolutely not. An employee has the right to receive evidence of PAYE deductions — "
  "normally via a payslip or end-of-year documents. The employee can use these records "
  "to prove their tax payments and claim a refund if overtaxed. Failing to provide "
  "deduction evidence is a breach of employer obligations.",
  TRA_IT, TRA_IT_N, GP, "2025-07-01", ANN, "Finance Act or employment law update",
  "business_market", "adversarial"),

p("tier1a_income_tax_adv_068_20260609","income_tax_adversarial",
  "Mshauri wa kigeni anayefanya kazi Tanzania kwa wiki moja haahitaji kusajiliwa "
  "TRA kwa sababu atakuwa Tanzania kwa muda mfupi tu — je, ni sahihi?",
  "Si sahihi kamili. Mshauri wa kigeni anayepokea malipo kwa kazi aliyofanya Tanzania "
  "anapaswa kulipa kodi ya Tanzania kwenye mapato hayo. Hata ikiwa yuko Tanzania kwa "
  "muda mfupi, mwajiri wake wa Tanzania (au kampuni inayomhusisha) ina wajibu wa "
  "kushikilia kodi ya zuio (WHT) kwenye malipo. Hii inatumika bila kujali muda wa "
  "kukaa Tanzania.",
  "A foreign consultant working in Tanzania for one week doesn't need to register "
  "with TRA because they will only be in Tanzania briefly — is this correct?",
  "Not entirely correct. A foreign consultant receiving payment for work done in Tanzania "
  "must pay Tanzania tax on that income. Even if present briefly, their Tanzania employer "
  "or contracting company has an obligation to withhold tax (WHT) on the payments. "
  "This applies regardless of the length of stay in Tanzania.",
  TRA_WHT, TRA_WHT_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "formal", "adversarial"),

p("tier1a_income_tax_adv_069_20260609","income_tax_adversarial",
  "Kampuni ambayo haikufanya biashara mwaka mzima hailazimiki kuwasilisha tamko "
  "la kodi ya kampuni kwa TRA — je, ni sahihi?",
  "Hapana. Kampuni iliyosajiliwa Tanzania lazima iwasilishe tamko la kodi ya kampuni "
  "(annual return) kwa TRA kila mwaka wa fedha, hata kama haikufanya shughuli yoyote "
  "au haikupata mapato. Tamko hili linaonyesha kwamba kampuni bado ipo na haijafutiwa. "
  "Kushindwa kuwasilisha kunaweza kusababisha adhabu hata kama kodi halisi ni sifuri.",
  "A company that did no business for the whole year does not need to file a corporate "
  "tax return with TRA — is this correct?",
  "No. A registered Tanzania company must file an annual tax return with TRA for every "
  "financial year, even if it conducted no activities or earned no income. This return "
  "demonstrates the company is still active and not struck off. Failure to file can "
  "result in penalties even if the actual tax liability is zero.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Administration Act update",
  "business_market", "adversarial"),

p("tier1a_income_tax_adv_070_20260609","income_tax_adversarial",
  "Kampuni inayolipa mshaara mkubwa kwa mkurugenzi wake inapunguza kodi ya kampuni "
  "kwa sababu mshahara ni gharama inayopunguzwa — je, TRA inakubali hili?",
  "TRA inakubali mshahara wa mkurugenzi kama gharama ya biashara inayopunguzwa "
  "(deductible) — lakini kwa kiasi cha biashara kilichowekwa. Kwa kawaida, TRA "
  "inaweza kupinga mshahara wa mkurugenzi ambao ni mkubwa kupita kiasi ikilinganishwa "
  "na ukubwa wa biashara au viwango vya soko. Mshahara wa mkurugenzi unapaswa kuakisi "
  "huduma halisi na kuwa na msingi wa soko. Pia, PAYE inalipwa kwenye mshahara huo.",
  "A company that pays its director a large salary reduces its corporate tax because "
  "salary is a deductible expense — will TRA accept this?",
  "TRA accepts director salaries as deductible business expenses — but only at an "
  "arm's-length commercial amount. TRA can challenge director salaries that are "
  "excessive relative to business size or market rates. Director salaries should "
  "reflect actual services and be commercially defensible. Also, PAYE is still "
  "payable on that salary.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act amendment or transfer pricing update",
  "formal", "standard"),

p("tier1a_income_tax_adv_071_20260609","income_tax_adversarial",
  "Mauzo ya bidhaa kwenye mitandao ya kijamii (Facebook, Instagram) hayalipishi "
  "kodi Tanzania kwa sababu ni biashara ya mtandaoni tu — je, ni sahihi?",
  "Hapana. Mauzo ya bidhaa au huduma kupitia mitandao ya kijamii bado yana kodi ya "
  "Tanzania ikiwa biashara ipo Tanzania au bidhaa/huduma zinauzwa kwa wateja wa "
  "Tanzania. Kodi ya mapato ya biashara, VAT (ikiwa mauzo yanazidi kizingiti), na "
  "EFD (kama unaomba) zinatumika bila kujali iwapo mauzo yanafanywa mtandaoni au "
  "mwili kwa mwili.",
  "Sales via social media (Facebook, Instagram) are not taxed in Tanzania because "
  "it is online business only — is this correct?",
  "No. Sales of goods or services via social media are still subject to Tanzania tax "
  "if the business is based in Tanzania or the goods/services are sold to Tanzania "
  "customers. Business income tax, VAT (if sales exceed the threshold), and EFD "
  "(if applicable) apply regardless of whether sales are made online or in person.",
  TRA_IT, TRA_IT_N, GP, "2025-07-01", ANN, "Finance Act digital economy update",
  "rural_conversational", "adversarial"),

p("tier1a_income_tax_adv_072_20260609","income_tax_adversarial",
  "Kampuni inayoshirikiana na kampuni nyingine (partnership) kila mmoja analipa "
  "kodi ya kampuni yake mwenyewe — je, ushirika una mfumo wake wa kodi?",
  "Ushirika wa biashara (partnership) Tanzania kwa kawaida haupigiwi kodi moja kwa "
  "moja kama kampuni. Kila mshirika analipa kodi kwenye sehemu yake ya faida ya ushirika "
  "kwenye tamko lake la kibinafsi au kampuni (kulingana na aina ya mshirika). Ushirika "
  "unawasilisha tamko lake TRA lakini kodi inalipwa na washirika mmoja mmoja, si na "
  "ushirika wenyewe.",
  "A partnership — each partner pays their own corporate tax — is there a separate "
  "tax structure for partnerships?",
  "A business partnership in Tanzania is generally not taxed directly like a company. "
  "Each partner pays tax on their share of partnership profit in their own individual "
  "or corporate return (depending on the type of partner). The partnership files its "
  "own return with TRA but the tax is paid by each partner individually, not by the "
  "partnership itself.",
  TRA_IT, TRA_IT_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "formal", "standard"),

p("tier1a_income_tax_adv_073_20260609","income_tax_adversarial",
  "Mfanyakazi anayeacha kazi anapata kodi yake ya PAYE iliyokatwa kwa mwaka "
  "yote ikiwa ni refund — je, hii ni haki yake?",
  "Si moja kwa moja. Kodi ya PAYE inayolipwa kupitia mwajiri kwa mwaka huhesabiwa "
  "kwa kuzingatia kipato chake chote cha mwaka. Ikiwa mfanyakazi alikatwa PAYE zaidi "
  "ya kiasi kinachohitajika (kwa mfano, alikuwa na miezi michache ya kazi tu), "
  "anaweza kudai refund kupitia tamko la kodi ya mwaka (TRA). Hata hivyo, kama "
  "alikatwa PAYE sahihi, hana haki ya refund kiotomatiki tu kwa sababu ya kuacha kazi.",
  "An employee who leaves a job gets all their PAYE deducted for the year back as a "
  "refund — is this their right?",
  "Not automatically. PAYE paid through an employer for the year is calculated against "
  "their total annual income. If an employee was over-deducted (for example, they only "
  "worked a few months), they can claim a refund through the annual tax return (TRA). "
  "However, if the correct PAYE was withheld, they are not automatically entitled to "
  "a refund just because they left employment.",
  TRA_IT, TRA_IT_N, GP, "2025-07-01", ANN, "Finance Act or PAYE procedure update",
  "business_market", "standard"),

p("tier1a_income_tax_adv_074_20260609","income_tax_adversarial",
  "Kodi ya mapato ya biashara ya kilimo Tanzania iko chini ya kodi ya kawaida ya "
  "biashara — kilimo kina mfumo maalum wa kodi — je, ni kweli?",
  "Shughuli fulani za kilimo Tanzania zina msamaha au mfumo maalum wa kodi. Kwa "
  "mfano, mapato ya kilimo ya mzalishaji mdogo yanaweza kusamehewa kodi ya mapato. "
  "Hata hivyo, kampuni kubwa za kilimo na mauzo ya mazao kwa biashara (commercial "
  "agriculture) zinalipishwa kodi ya kawaida. Angalia TRA na mwanasheria wa kodi "
  "kwa sekta yako mahususi ya kilimo.",
  "Tanzania agricultural business income tax is lower than regular business tax — "
  "agriculture has a special tax framework — is this true?",
  "Certain agricultural activities in Tanzania have exemptions or special tax treatment. "
  "For example, agricultural income of small-scale producers may be exempt from income "
  "tax. However, large agricultural companies and commercial crop sales are subject to "
  "standard tax. Check with TRA and a tax adviser for your specific agricultural sector.",
  TRA_IT, TRA_IT_N, GP, "2025-07-01", ANN, "Finance Act or agricultural policy update",
  "rural_conversational", "standard"),

p("tier1a_income_tax_adv_075_20260609","income_tax_adversarial",
  "Wakati kampuni inabadilisha mwaka wake wa fedha (financial year), inahitaji "
  "ruhusa ya TRA — au inaweza kubadilisha yenyewe?",
  "Kampuni inayotaka kubadilisha mwaka wake wa fedha Tanzania inahitaji idhini ya "
  "TRA. Kubadilisha bila ruhusa kunaweza kusababisha mgongano wa vipindi vya "
  "kuwasilisha na shida za makokotoo ya kodi ya awali. Omba TRA mapema na ubainishe "
  "kipindi cha mpito.",
  "When a company changes its financial year it needs TRA permission — or can it "
  "change on its own?",
  "A company wishing to change its financial year in Tanzania needs TRA approval. "
  "Changing without permission can cause overlapping filing periods and provisional "
  "tax calculation problems. Apply to TRA in advance and specify the transition period.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Administration Act update",
  "formal", "standard"),

p("tier1a_income_tax_adv_076_20260609","income_tax_adversarial",
  "Malipo ya pango la nyumba ya kampuni kwa mkurugenzi wake ni gharama ya biashara "
  "inayopunguzwa kodi — hakuna vizuizi — je, ni sahihi?",
  "Kwa kiasi fulani. Pango la makazi la mkurugenzi linaweza kudaiwa kama gharama ya "
  "biashara ikiwa makazi yanatolewa kama sehemu ya mkataba wa ajira na inahusiana "
  "moja kwa moja na biashara. Hata hivyo, thamani ya makazi haya lazima ijumuishwe "
  "kwenye kipato cha mkurugenzi kwa PAYE (kama manufaa ya nje ya fedha). Mkurugenzi "
  "analipa PAYE kwenye thamani ya makazi; kampuni inadai gharama — lakini si "
  "'bure' kwa kodi.",
  "A company paying its director's home rent is a fully deductible business expense "
  "with no restrictions — is this correct?",
  "Partially. Director accommodation rent can be claimed as a business expense if "
  "accommodation is provided as part of the employment contract and is directly "
  "connected to the business. However, the value of this accommodation must be "
  "included in the director's income for PAYE purposes (as a non-cash benefit). "
  "The director pays PAYE on the accommodation value; the company claims the expense "
  "— but it is not 'tax-free' overall.",
  TRA_IT, TRA_IT_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "business_market", "standard"),

p("tier1a_income_tax_adv_077_20260609","income_tax_adversarial",
  "Kiwango cha kodi ya zuio kwa ada za leseni (licence fees) zinazolipwa nje ya "
  "nchi ni asilimia 15 — je, ni sahihi?",
  "Ndiyo. Ada za leseni (licence fees) au mrabaha (royalties) zinazolipwa kwa mtu "
  "asiye mkazi Tanzania zina kodi ya zuio ya asilimia 15. Kiwango hiki kinatumika "
  "kwa ada za haki miliki ya akili, haki za matumizi ya programu za kompyuta, "
  "alama za biashara, na hati miliki. Angalia DTA inayohusika kwa kiwango "
  "kilichopunguzwa.",
  "The withholding tax rate on licence fees paid abroad is 15% — is this correct?",
  "Yes. Licence fees or royalties paid to a non-resident in Tanzania carry a 15% "
  "withholding tax. This rate applies to payments for intellectual property, software "
  "usage rights, trademarks, and patents. Check the applicable DTA for a reduced rate.",
  TRA_WHT, TRA_WHT_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "formal", "standard"),

p("tier1a_income_tax_adv_078_20260609","income_tax_adversarial",
  "Kampuni mpya inayopata hasara kwa mwaka wa kwanza inaweza kupata refund ya kodi "
  "ya awali (provisional tax) iliyolipwa — je, inaruhusiwa?",
  "Ndiyo. Ikiwa kampuni ilipiga makokotoo ya kodi ya awali lakini hatimaye ikakuta "
  "faida ni ndogo au kuna hasara, inaweza kudai refund ya sehemu ya kodi ya awali "
  "iliyolipwa kupita. Mchakato: wasilisha tamko la mwaka, TRA itathibitisha kiasi cha "
  "kodi sahihi, na tofauti inarejeshwa au inabebwa kama mkopo wa kodi kwa mwaka ujao.",
  "A new company that makes a loss in its first year can get a refund of provisional "
  "tax paid — is this permitted?",
  "Yes. If a company calculated provisional tax but ultimately found actual profit was "
  "lower or there was a loss, it can claim a refund of the overpaid provisional tax. "
  "Process: file the annual return, TRA confirms the correct tax amount, and the "
  "difference is refunded or carried as a tax credit to the following year.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Administration Act update",
  "business_market", "standard"),

p("tier1a_income_tax_adv_079_20260609","income_tax_adversarial",
  "Mtu anayepata kipato kutoka vyanzo viwili tofauti (mshahara + biashara ndogo) "
  "analipa PAYE kwenye mshahara tu na anasahau biashara ndogo — je, ni sahihi?",
  "Hapana. Mtu anayepata kipato kutoka vyanzo vingi — kama mshahara (PAYE inakatwa "
  "na mwajiri) na biashara ndogo — lazima ajiripoti mapato YOTE kwenye tamko la kodi "
  "la mwaka lake. PAYE iliyokatwa na mwajiri ni malipo ya awali ya kodi ya mwaka. "
  "Mapato yote ya mwaka yanajumlishwa na kodi ya mwaka inakokotolewa — ikiwa mapato "
  "ya biashara yanaongeza mzigo wa kodi, adalipa tofauti.",
  "A person earning from two sources (salary + small business) pays PAYE only on their "
  "salary and ignores the small business — is this correct?",
  "No. A person earning from multiple sources — such as salary (PAYE deducted by employer) "
  "and small business — must declare ALL income on their annual tax return. PAYE deducted "
  "by the employer is an advance payment on annual tax. All annual income is totalled and "
  "annual tax calculated — if business income adds to the tax burden, the difference must "
  "be paid.",
  TRA_IT, TRA_IT_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "rural_conversational", "adversarial"),

p("tier1a_income_tax_adv_080_20260609","income_tax_adversarial",
  "Kodi ya kampuni kwa DSE-listed company ni asilimia 25 kwa miaka mitano ya kwanza "
  "tu, kisha inarudi asilimia 30 — je, ni sahihi?",
  "Hapana. Kiwango cha asilimia 25 kwa kampuni zilizoorodhesha DSE HAINA kipindi maalum "
  "cha mwisho wa miaka mitano. Kiwango cha asilimia 25 kinatumika kwa muda wote kampuni "
  "ikiwa kwenye orodha ya DSE kwa angalau asilimia 30 ya hisa kwa umma. Ikiwa kampuni "
  "itaondolewa orodha au hisa za umma zitashuka chini ya asilimia 30, basi kiwango "
  "kinarudi asilimia 30.",
  "The 25% corporate tax rate for a DSE-listed company applies for the first five years "
  "only, then reverts to 30% — is this correct?",
  "No. The 25% rate for DSE-listed companies does NOT have a five-year sunset period. "
  "The 25% rate applies for as long as the company remains listed on DSE with at least "
  "30% of shares available to the public. If the company is delisted or the public "
  "shareholding drops below 30%, the rate reverts to 30%.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act or DSE listing rule update",
  "formal", "adversarial"),

p("tier1a_income_tax_adv_081_20260609","income_tax_adversarial",
  "Kodi ya zuio kwenye huduma za usimamizi (management fees) kwa mkazi Tanzania ni "
  "asilimia 5 — je, ni sahihi?",
  "Hapana. Kodi ya zuio kwenye ada za usimamizi zinazolipwa kwa MKAZI Tanzania ni "
  "asilimia 5. Lakini kwa ASIYE MKAZI, kiwango ni asilimia 15. Hii ni tofauti muhimu. "
  "Mkazi = mtu au kampuni inayoishi/ipo Tanzania kwa zaidi ya siku 183 kwa mwaka wa "
  "fedha. Kagua hali ya ukazi wa mpokeaji kabla ya kushikilia kodi.",
  "Withholding tax on management service fees to a Tanzania resident is 5% — "
  "is this correct?",
  "Yes, 5% for a resident. But for a NON-RESIDENT, the rate is 15%. This is an "
  "important distinction. Resident = a person or company that lives in or is present "
  "in Tanzania for more than 183 days of the financial year. Verify the residency "
  "status of the recipient before withholding.",
  TRA_WHT, TRA_WHT_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "business_market", "disambiguation"),

p("tier1a_income_tax_adv_082_20260609","income_tax_adversarial",
  "Kampuni ndogo yenye mauzo ya TZS 100M kwa mwaka inalipa kodi ya mapato ya "
  "kawaida ya asilimia 30 — je, ni sahihi?",
  "Si lazima. Kampuni ndogo yenye mauzo chini ya kizingiti fulani inaweza kulipa "
  "kodi ya mapato ya chini (minimum turnover tax) badala ya kodi ya kawaida ya "
  "asilimia 30, ikiwa kodi ya asilimia 30 kwenye faida ingewa ndogo zaidi kuliko kodi "
  "ya chini ya mauzo. Kodi ya chini ya mauzo ni asilimia 1 ya mauzo ya jumla "
  "(wef 1 Julai 2025). Kampuni inalipa KIWANGO KIKUBWA ZAIDI kati ya kodi ya mapato "
  "ya kawaida na kodi ya chini.",
  "A small company with TZS 100M annual turnover pays the standard 30% income tax "
  "— is this correct?",
  "Not necessarily. A small company below a certain threshold may pay minimum turnover "
  "tax instead of standard 30% if the 30% on profit would be less than the minimum "
  "tax. Minimum turnover tax is 1% of gross turnover (effective 1 July 2025). A "
  "company pays the HIGHER of: standard income tax OR minimum turnover tax.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "business_market", "standard"),

p("tier1a_income_tax_adv_083_20260609","income_tax_adversarial",
  "Tamko la kodi ya kampuni linawasilishwa ndani ya miezi sita baada ya mwisho wa "
  "mwaka wa fedha — je, ni sahihi?",
  "Ndiyo. Kampuni ya Tanzania lazima iwasilishe tamko la kodi ya kampuni (corporate "
  "income tax return) ndani ya miezi 6 kutoka mwisho wa mwaka wake wa fedha. Kwa "
  "kampuni inayotumia mwaka wa kalenda (Januari–Desemba), tarehe ya mwisho ni "
  "30 Juni ya mwaka unaofuata. Kuchelewa kunaongeza adhabu ya kodi.",
  "The corporate tax return is filed within six months after the end of the financial "
  "year — is this correct?",
  "Yes. A Tanzania company must file its corporate income tax return within 6 months "
  "from the end of its financial year. For a company using the calendar year "
  "(January–December), the deadline is 30 June of the following year. Late filing "
  "attracts penalties.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Administration Act update",
  "formal", "standard"),

p("tier1a_income_tax_adv_084_20260609","income_tax_adversarial",
  "Kampuni inayotoa sadaka (donation) kwa taasisi za hisani inalipwa kodi kidogo "
  "kwa sababu sadaka ni gharama inayopunguzwa — je, TRA inakubali sadaka zote?",
  "TRA inakubali sadaka kama gharama inayopunguzwa LAKINI kwa masharti: "
  "(1) taasisi inayopokea lazima iwe na usajili wa hisani unaotambuliwa na TRA, "
  "(2) sadaka lazima idhibitiwe kwa nyaraka (risiti ya sadaka), na "
  "(3) kikomo fulani cha sadaka kinaweza kutumika. Sadaka kwa watu binafsi au "
  "taasisi zisizotambuliwa hazipunguzwi. Hakikisha usajili wa taasisi kabla ya kudai.",
  "A company making a donation to a charity pays less tax because donations are "
  "deductible — does TRA accept all donations?",
  "TRA accepts donations as deductible expenses BUT with conditions: (1) the receiving "
  "institution must be TRA-recognised registered charity, (2) donations must be "
  "documented (donation receipt), and (3) a cap on deductible donations may apply. "
  "Donations to individuals or unrecognised institutions are not deductible. Verify "
  "the institution's registration before claiming.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "formal", "standard"),

p("tier1a_income_tax_adv_085_20260609","income_tax_adversarial",
  "Biashara ya mikoba ya ngozi inayouza nje ya nchi (export) haina kodi yoyote "
  "Tanzania — mauzo ya nje ni huru kabisa — je, ni sahihi?",
  "Si sahihi kabisa. Mauzo ya nje (exports) yanaweza kuwa huru au kuwa na kiwango "
  "cha sifuri cha VAT Tanzania, lakini FAIDA inayotokana na biashara ya mauzo ya nje "
  "bado inalipishwa kodi ya mapato ya biashara kwa asilimia 30 (au kiwango "
  "kinachofaa). Msamaha wa VAT kwenye mauzo ya nje haumaanishi msamaha wa kodi ya "
  "mapato. TRA inalazimisha pia malipo ya NSSF, SDL, na PAYE kwa wafanyakazi.",
  "A leather bag business selling abroad (exports) has no taxes at all in Tanzania "
  "— exports are completely tax-free — is this correct?",
  "Not entirely correct. Exports may be VAT-exempt or zero-rated in Tanzania, but the "
  "PROFIT from an export business is still subject to business income tax at 30% (or "
  "applicable rate). VAT exemption on exports does not mean income tax exemption. "
  "TRA also enforces NSSF, SDL, and PAYE obligations for employees.",
  TRA_IT, TRA_IT_N, GP, "2025-07-01", ANN, "Finance Act or export policy update",
  "rural_conversational", "adversarial"),

p("tier1a_income_tax_adv_086_20260609","income_tax_adversarial",
  "Kampuni ya teknolojia inayotengeneza programu za simu Tanzania hailazimiki "
  "kulipa kodi kwa sababu programu ni bidhaa ya mtandaoni — je, ni sahihi?",
  "Hapana. Kampuni inayotengeneza programu za simu au bidhaa za kidijitali Tanzania "
  "inalipa kodi ya mapato ya kawaida ya kampuni (asilimia 30 au kiwango kinachofaa). "
  "Bidhaa za kidijitali hazina msamaha wa kodi ya mapato wa Tanzania. Pia kwa mauzo "
  "ya dijitali kwa wateja wa Tanzania, mazingira ya VAT yanaendelea kubadilika (B2C "
  "e-payment VAT ya asilimia 16 kutoka Septemba 2025).",
  "A technology company making mobile apps in Tanzania does not need to pay tax because "
  "software is a digital product — is this correct?",
  "No. A company making mobile apps or digital products in Tanzania pays standard "
  "corporate income tax (30% or applicable rate). Digital products do not have a "
  "Tanzania income tax exemption. Also for digital sales to Tanzania customers, the "
  "VAT environment is evolving (B2C e-payment VAT of 16% from September 2025).",
  TRA_IT, TRA_IT_N, GP, "2025-07-01", ANN, "Finance Act digital economy update",
  "business_market", "adversarial"),

p("tier1a_income_tax_adv_087_20260609","income_tax_adversarial",
  "Kampuni inayolipa ada za kitaalamu kwa daktari au mwanasheria wa nje (freelance) "
  "ya Tanzania haishikili kodi yoyote — je, ni sahihi?",
  "Hapana. Malipo ya ada za kitaalamu kwa mtu wa Tanzania (daktari, mwanasheria, "
  "mhasibu wa kujitegemea) yanashikiliwa kodi ya zuio ya asilimia 5 (WHT kwa mkazi). "
  "Kampuni inayolipa ada hizi ina wajibu wa kushikilia WHT kabla ya kulipa na kuwasilisha "
  "na TRA ndani ya siku 7 baada ya mwisho wa mwezi. Kushindwa kushikilia kunafanya "
  "kampuni iwajibike kwa kodi, riba, na adhabu.",
  "A company paying professional fees to a freelance Tanzanian doctor or lawyer does "
  "not withhold any tax — is this correct?",
  "No. Payments of professional fees to a Tanzania person (doctor, lawyer, independent "
  "accountant) are subject to 5% withholding tax (WHT for resident). The company paying "
  "these fees has an obligation to withhold WHT before paying and remit to TRA within "
  "7 days after month end. Failing to withhold makes the company liable for the tax, "
  "interest, and penalties.",
  TRA_WHT, TRA_WHT_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "business_market", "adversarial"),

p("tier1a_income_tax_adv_088_20260609","income_tax_adversarial",
  "Kampuni inayofiwa na mwanachama muhimu wa uongozi (CEO) inaweza kuomba msamaha "
  "wa kodi kwa mwaka huo kwa sababu ya msiba — je, ipo utaratibu huo?",
  "Hapana. Hakuna msamaha wa kodi wa kampuni Tanzania kwa sababu ya msiba au kifo "
  "cha kiongozi. Wajibu wa kodi wa kampuni unaendelea bila kujali hali ya "
  "wafanyakazi au uongozi. Ikiwa kampuni ina matatizo ya kulipa kodi kwa wakati wa "
  "hali ngumu, inaweza kuwasiliana na TRA kuomba mpango wa malipo badala ya "
  "msamaha.",
  "A company that loses a key executive (CEO) can apply for a tax exemption for that "
  "year due to bereavement — is there such a procedure?",
  "No. There is no Tanzania corporate tax exemption due to bereavement or the death "
  "of a leader. The company's tax obligations continue regardless of staff or "
  "leadership circumstances. If a company has difficulties paying tax during a "
  "difficult period, it can contact TRA to request a payment plan rather than "
  "an exemption.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Administration Act update",
  "rural_conversational", "adversarial"),

p("tier1a_income_tax_adv_089_20260609","income_tax_adversarial",
  "Kodi ya zuio kwenye pango la ardhi/mali isiyohamishika kwa mkazi Tanzania ni "
  "asilimia 15 — je, ni sahihi?",
  "Hapana. Kodi ya zuio kwenye pango la ardhi au mali isiyohamishika inayolipwa "
  "kwa mkazi Tanzania ni asilimia 10, si asilimia 15. Kwa asiye mkazi, kiwango ni "
  "asilimia 15. Hii ni sehemu ya jedwali la kodi ya zuio la Tanzania. Kampuni "
  "inayolipa pango kwa mkazi lazima ishikilie asilimia 10 na kuwasilisha ndani ya "
  "siku 7 baada ya mwisho wa mwezi.",
  "Withholding tax on land/real estate rent paid to a Tanzania resident is 15% "
  "— is this correct?",
  "No. Withholding tax on rent of land or real estate paid to a Tanzania resident is "
  "10%, not 15%. For non-residents, the rate is 15%. This is part of Tanzania's "
  "withholding tax schedule. A company paying rent to a resident must withhold 10% "
  "and remit within 7 days after month end.",
  TRA_WHT, TRA_WHT_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "formal", "adversarial"),

p("tier1a_income_tax_adv_090_20260609","income_tax_adversarial",
  "Kampuni inaweza kusaidia mwajiriwa wake kulipa kodi yake ya PAYE kama sehemu "
  "ya mfuko wa mishahara — kampuni inalipa kodi badala ya mwajiriwa — je, inaruhusiwa?",
  "Ndiyo, kampuni inaweza kubeba mzigo wa PAYE ya mwajiriwa — lakini thamani ya "
  "PAYE inayolipwa na mwajiri inaonekana kama manufaa ya ziada ya mwajiriwa (benefit "
  "in kind) na lazima ijumuishwe tena kwenye mshahara wa mwajiriwa kwa madhumuni ya "
  "kodi. Hii inasababisha 'gross-up' ya mshahara. Ni halali lakini inahitaji "
  "makokotoo sahihi ya mhasibu.",
  "A company can pay an employee's PAYE on their behalf as part of the salary "
  "package — the company pays tax instead of the employee — is this allowed?",
  "Yes, a company can bear an employee's PAYE burden — but the PAYE paid by the "
  "employer is treated as an additional employee benefit (benefit in kind) and must "
  "be grossed back into the employee's salary for tax purposes. This causes a "
  "'gross-up' of the salary. It is legal but requires accurate calculations by "
  "an accountant.",
  TRA_IT, TRA_IT_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "formal", "standard"),

p("tier1a_income_tax_adv_091_20260609","income_tax_adversarial",
  "Orodha ya kodi ya zuio Tanzania: riba ni asilimia ngapi kwa mkazi na asiye mkazi?",
  "Kodi ya zuio kwenye riba (interest) Tanzania: kwa MKAZI ni asilimia 10; kwa "
  "ASIYE MKAZI ni asilimia 10 pia (lakini DTA inaweza kupunguza). Kiwango "
  "kimoja (10%) kinatumika kwa pande zote mbili kwa riba — tofauti na ada za "
  "usimamizi ambapo mkazi hulipa 5% na asiye mkazi hulipa 15%.",
  "Tanzania withholding tax list: what rate does interest attract for resident and "
  "non-resident?",
  "Withholding tax on interest in Tanzania: for RESIDENT is 10%; for NON-RESIDENT is "
  "also 10% (but DTA may reduce it). A single rate (10%) applies to both parties for "
  "interest — unlike management fees where a resident pays 5% and a non-resident "
  "pays 15%.",
  TRA_WHT, TRA_WHT_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "business_market", "standard"),

p("tier1a_income_tax_adv_092_20260609","income_tax_adversarial",
  "Kampuni ya Tanzania haijasajiliwa DSE lakini inamilikiwa asilimia 100 na kampuni "
  "ya Uingereza — inatumia kiwango cha asilimia 25 au asilimia 30?",
  "Umiliki na kiwango cha kodi ya DSE ni mambo tofauti. Kiwango cha asilimia 25 "
  "kinatokana na ORODHA ya hisa kwenye DSE kwa umma Tanzania — si umiliki wa kigeni. "
  "Kampuni inayomilikiwa na Uingereza asilimia 100 ambayo haijaorodhesha DSE "
  "inalipa kiwango cha kawaida cha asilimia 30. Umiliki wa kigeni peke yake "
  "haupunguzi kiwango cha kodi.",
  "A Tanzania company not listed on DSE but 100% owned by a UK company — does it use "
  "the 25% or 30% rate?",
  "DSE listing and tax rate are separate matters. The 25% rate comes from LISTING "
  "shares on the DSE for the public in Tanzania — not from foreign ownership. A company "
  "that is 100% UK-owned but not DSE-listed pays the standard 30% rate. Foreign "
  "ownership alone does not reduce the tax rate.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act or DSE rule update",
  "formal", "disambiguation"),

p("tier1a_income_tax_adv_093_20260609","income_tax_adversarial",
  "Kampuni inapoteza haki ya kubeba hasara mbele ikiwa haijatoa tamko la kodi "
  "kwa mwaka wa hasara — je, ni kweli?",
  "Ndiyo. Kushindwa kuwasilisha tamko la kodi kwa mwaka wa hasara kunaweza "
  "kuathiri haki ya kubeba hasara mbele. TRA inaweza kupinga udai wa hasara "
  "ambao haujathbitishwa na tamko la kodi lililothibitishwa. Daima wasilisha "
  "tamko hata katika miaka ya hasara ili kuhifadhi haki ya carry-forward.",
  "A company loses its right to carry losses forward if it does not file a tax return "
  "for the loss year — is this true?",
  "Yes. Failing to file a tax return for a loss year can compromise the right to "
  "carry that loss forward. TRA may challenge loss claims not substantiated by a "
  "confirmed tax return. Always file a return even in loss years to preserve the "
  "carry-forward right.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Administration Act update",
  "formal", "adversarial"),

p("tier1a_income_tax_adv_094_20260609","income_tax_adversarial",
  "Mtu anayepata kipato tu kutoka njia moja ya mwajiri wake halazimiki kuwasilisha "
  "tamko la kodi ya mwaka — PAYE inatosha — je, ni sahihi?",
  "Kwa ujumla ndiyo — ikiwa kipato chake chote kinakatwa PAYE sahihi na mwajiri mmoja, "
  "mwajiriwa wa kawaida anaweza asihitajike kuwasilisha tamko la kibinafsi la kodi. "
  "PAYE inafanya kazi kama kodi ya mwisho kwa wafanyakazi wengi. Hata hivyo, "
  "mwajiriwa LAZIMA awasilishe tamko la mwaka ikiwa: ana vyanzo vingi vya kipato, "
  "anataka kudai gharama zinazopunguzwa, au ana hasara za awali zinazobebwa.",
  "A person earning income only from one employer does not need to file an annual "
  "tax return — PAYE is sufficient — is this correct?",
  "Generally yes — if all income is correctly deducted at source by one employer, "
  "a regular employee may not need to file an individual tax return. PAYE acts as "
  "a final tax for most employees. However, an employee MUST file an annual return "
  "if: they have multiple income sources, want to claim deductible expenses, or "
  "have prior losses to carry.",
  PWC, PWC_N, T1A, "2025-07-01", ANN, "Finance Act PAYE procedure update",
  "business_market", "standard"),

p("tier1a_income_tax_adv_095_20260609","income_tax_adversarial",
  "Faida iliyogawanywa kama bonus ya mwisho wa mwaka kwa wafanyakazi inalipwa kodi "
  "ya PAYE ya kawaida — je, bonus ina kodi maalum?",
  "Bonus ya mwisho wa mwaka kwa wafanyakazi Tanzania inalipwa kodi ya PAYE kama "
  "mshahara wa kawaida — inalipwa kwa wakati wa kulipwa, kwa bendi ya kodi "
  "inayotumika kwa kipato chake cha jumla cha mwezi huo. Hakuna kiwango cha "
  "kodi maalum cha chini kwa bonasi za wafanyakazi Tanzania. Ni mapato ya kawaida ya "
  "ajira.",
  "Profit distributed as an annual bonus to employees is subject to standard PAYE "
  "— does a bonus have a special tax rate?",
  "An annual bonus for Tanzania employees is taxed as PAYE like regular salary — it "
  "is taxed at the time of payment at the applicable band rate for the employee's "
  "total income for that month. There is no special lower tax rate for employee "
  "bonuses in Tanzania. It is ordinary employment income.",
  TRA_IT, TRA_IT_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "formal", "standard"),

p("tier1a_income_tax_adv_096_20260609","income_tax_adversarial",
  "Kampuni inayounza mali zake (mali isiyohamishika) haishikili kodi yoyote — "
  "mwunuzi ndiye anayepaswa kulipa kodi ya ununuzi — je, ni sahihi?",
  "Kwa ujumla si sahihi. Faida ya mtaji (capital gain) kutoka mauzo ya mali "
  "isiyohamishika na biashara inalipishwa kodi ya mapato kwenye mauzo. Pia, "
  "ikiwa muuzaji ni asiye mkazi, mwunuzi ana wajibu wa kushikilia kodi ya zuio "
  "ya asilimia 10 kwenye bei ya mauzo. Kwa muuzaji mkazi anayefanya biashara, "
  "faida inalipishwa kodi ya mapato. Zote mbili, mwunuzi na muuzaji, wana majukumu "
  "ya kodi.",
  "A company selling its property does not withhold any tax — the buyer is responsible "
  "for purchase taxes — is this correct?",
  "Generally not correct. Capital gain from sale of real property by a business is "
  "subject to income tax on disposal. Also, if the seller is a non-resident, the "
  "buyer has an obligation to withhold 10% on the sale price. For a resident business "
  "seller, the profit is subject to income tax. Both buyer and seller have tax "
  "obligations.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "formal", "adversarial"),

p("tier1a_income_tax_adv_097_20260609","income_tax_adversarial",
  "Kampuni ndogo yenye wafanyakazi 3 haihitaji mfumo wa PAYE — analipa mshahara "
  "tu na anafanya reconciliation mwishoni mwa mwaka — je, ni sahihi?",
  "Hapana. Kila mwajiri Tanzania, bila kujali ukubwa wa kampuni, lazima ashikilie "
  "PAYE kwa kila mfanyakazi mwenye mshahara unaozidi TZS 270,000 kwa mwezi na "
  "kuwasilisha kwa TRA ifikapo tarehe 7 ya mwezi unaofuata. Hakuna mfumo wa "
  "'kulipa mara moja mwishoni mwa mwaka' kwa PAYE. Kushindwa kuwasilisha kwa wakati "
  "kunasababisha adhabu ya asilimia 2.5 kwa mwezi.",
  "A small company with 3 employees does not need a PAYE system — just pays wages "
  "and does a reconciliation at year end — is this correct?",
  "No. Every Tanzania employer, regardless of company size, must withhold PAYE from "
  "every employee earning above TZS 270,000 per month and remit to TRA by the 7th of "
  "the following month. There is no 'pay once at year end' system for PAYE. Failure "
  "to remit on time attracts a penalty of 2.5% per month.",
  TRA_IT, TRA_IT_N, GP, "2025-07-01", ANN, "Finance Act or PAYE procedure update",
  "rural_conversational", "adversarial"),

p("tier1a_income_tax_adv_098_20260609","income_tax_adversarial",
  "Mtu anayeuza nyumba yake ya makazi Tanzania (si ya biashara) analipa kodi gani?",
  "Kwa kawaida, mauzo ya nyumba ya makazi (residential property) na mmiliki anayeishi "
  "humo kwa muda mrefu inaweza kusamehewa kodi ya faida ya mtaji Tanzania — lakini "
  "masharti yanashikilia: iwe nyumba ya msingi ya makazi, mmiliki ameishi humo kwa "
  "muda wa kutosha. Ikiwa nyumba ni ya biashara au ni miongoni mwa mali nyingi za "
  "uwekezaji, faida ya mtaji inaweza kulipishwa kodi. Omba ushauri wa mwanasheria wa "
  "kodi kwa hali yako mahususi.",
  "A person selling their residential home in Tanzania (not a business property) — "
  "what tax do they pay?",
  "Generally, the sale of a residential home by an owner who has lived there for a "
  "long period may be exempt from capital gains tax in Tanzania — but conditions "
  "apply: it must be a primary residence and the owner must have lived there for "
  "a sufficient period. If the home is a business property or one of many investment "
  "properties, capital gains may be taxed. Seek advice from a tax lawyer for your "
  "specific situation.",
  TRA_IT, TRA_IT_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "rural_conversational", "standard"),

p("tier1a_income_tax_adv_099_20260609","income_tax_adversarial",
  "Matumizi ya chakula cha ofisi na burudani za wateja (entertainment) yanaweza "
  "kudaiwa kikamilifu kama gharama ya biashara Tanzania — je, ni sahihi?",
  "Si kweli kabisa. Gharama za burudani (entertainment) zinaweza kupunguzwa kwa kiasi "
  "tu Tanzania — TRA ina mipaka kwenye gharama za burudani za wateja. Chakula cha "
  "ofisi cha kawaida kwa wafanyakazi kinaweza kuruhusiwa zaidi, lakini chakula cha "
  "anasa na matumizi ya burudani ya wateja yanazungumziwa zaidi na TRA. Daima hifadhi "
  "nyaraka na ufafanuzi wa madhumuni ya biashara.",
  "Office food expenses and client entertainment can be fully claimed as Tanzania "
  "business expenses — is this correct?",
  "Not entirely true. Entertainment expenses may only be partially deductible in "
  "Tanzania — TRA has limits on client entertainment expenses. Regular office food "
  "for employees may be more permissible, but luxury entertainment and client "
  "hospitality are more closely scrutinised by TRA. Always keep documentation and "
  "business purpose explanations.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act or TRA guidance update",
  "business_market", "standard"),

p("tier1a_income_tax_adv_100_20260609","income_tax_adversarial",
  "Kampuni inayohangaika na mtiririko wa pesa inaweza kuomba TRA kusimamisha "
  "ukusanyaji wa kodi kwa miezi sita — je, ipo utaratibu huo rasmi?",
  "Hakuna msamaha rasmi wa 'kusimamisha kodi kwa miezi sita' Tanzania. Hata hivyo, "
  "TRA ina utaratibu wa kupanga malipo ya awamu (instalment plan) kwa walipakodi "
  "wenye matatizo ya kweli ya mtiririko wa pesa. Unaweza kuwasiliana na TRA moja kwa "
  "moja kueleza hali yako na kuomba mpango wa malipo. Riba ya kuchelewa bado inaendelea "
  "hata wakati wa mpango wa malipo — lakini adhabu inaweza kupunguzwa kwa sababu ya "
  "ushirikiano.",
  "A company struggling with cash flow can ask TRA to suspend tax collection for six "
  "months — is there such a formal procedure?",
  "There is no formal 'six-month tax suspension' in Tanzania. However, TRA has a "
  "procedure for arranging payment instalments (instalment plan) for taxpayers with "
  "genuine cash-flow difficulties. You can contact TRA directly to explain your "
  "situation and request a payment plan. Late interest continues to accrue even during "
  "a payment plan — but penalties may be reduced due to cooperation.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Administration Act update",
  "business_market", "standard"),

]

written = 0
with open(OUT, "a", encoding="utf-8") as f:
    for pr in pairs:
        f.write(json.dumps(pr, ensure_ascii=False) + "\n")
        written += 1

total = sum(1 for _ in open(OUT, encoding="utf-8") if _.strip())
print(f"Part 2: wrote {written} pairs to {OUT}")
print(f"Total in file: {total}")
