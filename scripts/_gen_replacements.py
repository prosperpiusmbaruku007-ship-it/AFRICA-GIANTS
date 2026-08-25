#!/usr/bin/env python3
"""Generate 13 replacement pairs for eval_set holdouts + contamination removals."""
import json

pairs = [

# ==========================================
# PAIRS 1-10: Replacements for eval_set pairs
# ==========================================

# 1. vat_registration — replaces tier1a_vat_002 (eval_set)
{
  "id": "tier1a_vat_rep_001_20260611",
  "domain": "tier1a",
  "subdomain": "vat_registration",
  "question_sw": "Ninataka kusajili VAT — ninahitaji nyaraka zipi na TRA itachukua muda gani kusindika ombi langu?",
  "answer_sw": "Ili kusajili VAT na TRA unahitaji: (1) fomu ya usajili (ITX 101.01.E); (2) nakala ya cheti cha TIN; (3) uthibitisho wa mahali pa biashara kama vile mkataba wa pango; (4) nakala ya kitambulisho cha taifa au pasipoti ya mmiliki; (5) rekodi za mauzo zinazoonyesha mauzo yanayopita kizingiti cha TZS 200,000,000 kwa miezi 12 au TZS 100,000,000 kwa miezi 6. Wasilisha fomu kwenye ofisi ya TRA au mtandaoni kupitia mfumo wa e-filing. TRA inachakata maombi mengi ndani ya siku 14 za kazi.",
  "question_en": "I want to register for VAT — what documents does TRA require and how long does the application take?",
  "answer_en": "To register for VAT with TRA you need: (1) the registration form (ITX 101.01.E); (2) copy of TIN certificate; (3) proof of business premises such as a rental agreement; (4) copy of owner national ID or passport; (5) sales records showing turnover exceeding TZS 200,000,000 over 12 months or TZS 100,000,000 over 6 months. Submit at a TRA office or via the e-filing portal. TRA typically processes applications within 14 working days.",
  "primary_source_url": "https://www.tra.go.tz/page/value-added-tax",
  "primary_source_name": "TRA - Value Added Tax",
  "source_type": "government_portal",
  "effective_date": "2025-07-01",
  "decay_risk": "annual",
  "next_review_trigger": "Finance Act amendment changing VAT registration threshold or process",
  "verified_by": "founder_self_review",
  "verified_date": "2026-06-11",
  "register": "formal",
  "pair_type": "standard",
  "eval_set": False
},

# 2. vat_withholding — replaces tier1a_vat_006 (eval_set)
{
  "id": "tier1a_vat_rep_002_20260611",
  "domain": "tier1a",
  "subdomain": "vat_withholding",
  "question_sw": "Mimi ni wakala wa zuio la VAT. Ninaweza kupunguza VAT niliyoizuia kutoka kwa wasambazaji dhidi ya VAT ninayodaiwa mimi mwenyewe?",
  "answer_sw": "Hapana. VAT ya zuio unayoizuia kutoka kwa msambazaji wako hailipwi kama mkopo dhidi ya deni lako la VAT. Wewe kama wakala wa zuio unalipa kiasi hicho moja kwa moja TRA kwa niaba ya msambazaji. Msambazaji wako ndiye anayeidai kama mkopo wa VAT (input VAT) kwenye return yake. Lazima utoe hati ya zuio la VAT kwa msambazaji siku ambayo VAT inastahili kulipwa — si tarehe ya 20.",
  "question_en": "I am a designated VAT withholding agent. Can I offset the VAT I withheld from suppliers against my own VAT liability?",
  "answer_en": "No. The VAT you withhold from your suppliers cannot be offset against your own output VAT liability. As the withholding agent you remit the withheld amount directly to TRA on behalf of your supplier. Your supplier claims it as input VAT on their own return. You must issue the VAT withholding certificate to your supplier on the day the VAT becomes payable — not on the 20th.",
  "primary_source_url": "https://www.tra.go.tz/page/value-added-tax",
  "primary_source_name": "TRA - Value Added Tax",
  "source_type": "government_portal",
  "effective_date": "2025-07-01",
  "decay_risk": "annual",
  "next_review_trigger": "Finance Act amendment changing VAT withholding rules",
  "verified_by": "founder_self_review",
  "verified_date": "2026-06-11",
  "register": "business_market",
  "pair_type": "standard",
  "eval_set": False
},

# 3. vat_registration — replaces tier1a_vat_010 (eval_set)
{
  "id": "tier1a_vat_rep_003_20260611",
  "domain": "tier1a",
  "subdomain": "vat_registration",
  "question_sw": "Mauzo yangu bado hayajafika TZS 200 milioni kwa mwaka. Ninaweza kusajili VAT kwa hiari (voluntary VAT registration)?",
  "answer_sw": "Ndiyo — unaweza kusajili VAT kwa hiari hata kama mauzo yako hayajafika kizingiti cha lazima cha TZS 200,000,000 kwa miezi 12 (au TZS 100,000,000 kwa miezi 6). Faida ya usajili wa hiari: unaweza kudai mkopo wa VAT (input VAT) kwa manunuzi ya biashara yako na hivyo kupunguza gharama. Hasara: utahitajika kuwasilisha return ya kila mwezi, kutoa risiti za EFD, na kulipa VAT kwa wakati. Fikiria kama faida ya mkopo wa VAT inazidi gharama ya utiifu (compliance).",
  "question_en": "My annual sales have not yet reached TZS 200 million. Can I register for VAT voluntarily?",
  "answer_en": "Yes — you can register for VAT voluntarily even if your turnover has not reached the mandatory threshold of TZS 200,000,000 per 12 months (or TZS 100,000,000 per 6 months). Benefit: you can claim input VAT credits on business purchases, reducing costs. Drawback: you must submit a monthly VAT return, issue EFD receipts, and pay VAT on time. Weigh whether the input VAT benefit outweighs the compliance burden.",
  "primary_source_url": "https://www.tra.go.tz/page/value-added-tax",
  "primary_source_name": "TRA - Value Added Tax",
  "source_type": "government_portal",
  "effective_date": "2025-07-01",
  "decay_risk": "annual",
  "next_review_trigger": "Finance Act amendment changing voluntary VAT registration rules",
  "verified_by": "founder_self_review",
  "verified_date": "2026-06-11",
  "register": "business_market",
  "pair_type": "standard",
  "eval_set": False
},

# 4. efd_compliance — replaces tier1a_efd_003 (eval_set)
{
  "id": "tier1a_efd_rep_001_20260611",
  "domain": "tier1a",
  "subdomain": "efd_compliance",
  "question_sw": "Mteja wangu alilipa kupitia uhamisho wa benki (bank transfer) — si pesa taslimu. Je, bado ninahitaji kutoa risiti ya EFD?",
  "answer_sw": "Ndiyo — njia ya malipo haibadilishi wajibu wa EFD. Iwe ni pesa taslimu, uhamisho wa benki, malipo ya simu (mobile money), au kadi ya mkopo — biashara yoyote inayohitajika kutumia EFD lazima itoe risiti ya EFD kwa kila mauzo. EFD inarekodi muamala wa mauzo, si njia ya malipo. Kushindwa kutoa risiti ya EFD kunakufanya upate adhabu za TRA hata kama mteja alilipa kupitia benki.",
  "question_en": "My customer paid via bank transfer, not cash. Do I still need to issue an EFD receipt?",
  "answer_en": "Yes — the payment method does not change the EFD obligation. Whether payment is cash, bank transfer, mobile money, or credit card — any business required to use EFD must issue an EFD receipt for every sale. The EFD records the sale transaction, not the payment channel. Failing to issue an EFD receipt attracts TRA penalties even when the customer paid by bank transfer.",
  "primary_source_url": "https://www.tra.go.tz/page/electronic-fiscal-devices",
  "primary_source_name": "TRA - Electronic Fiscal Devices",
  "source_type": "government_portal",
  "effective_date": "2025-07-01",
  "decay_risk": "stable",
  "next_review_trigger": "TRA EFD regulation amendment",
  "verified_by": "founder_self_review",
  "verified_date": "2026-06-11",
  "register": "business_market",
  "pair_type": "standard",
  "eval_set": False
},

# 5. brela_registration — replaces tier1a_brela_003 (eval_set)
{
  "id": "tier1a_brela_rep_001_20260611",
  "domain": "tier1a",
  "subdomain": "brela_registration",
  "question_sw": "Nimetaka kubadilisha jina la biashara yangu iliyosajiliwa na BRELA. Nawezaje kufanya hivyo?",
  "answer_sw": "Kubadilisha jina la biashara lililosajiliwa na BRELA: (1) angalia kwanza kama jina jipya linapatikana kwenye mfumo wa BRELA ili kuhakikisha halipo tayari; (2) jaza fomu ya mabadiliko ya jina na wasilisha pamoja na nakala ya cheti cha usajili wa sasa na ada ya mabadiliko; (3) BRELA itatoa cheti kipya chenye jina jipya. Muhimu: baada ya kubadilisha jina lazima pia uarifu TRA ili kusasisha akaunti yako ya kodi na TIN certificate yako.",
  "question_en": "I want to change my business name registered with BRELA. How do I do this?",
  "answer_en": "To change a BRELA-registered business name: (1) first check the new name is available on the BRELA system to ensure it does not already exist; (2) complete the name-change application form and submit it with a copy of the current registration certificate and the amendment fee; (3) BRELA will issue a new certificate with the new name. Important: after changing the name you must also notify TRA to update your tax account and TIN certificate.",
  "primary_source_url": "https://www.brela.go.tz",
  "primary_source_name": "BRELA - Business Registrations and Licensing Agency",
  "source_type": "government_portal",
  "effective_date": "2025-01-01",
  "decay_risk": "stable",
  "next_review_trigger": "BRELA fee or process changes announced by BRELA",
  "verified_by": "founder_self_review",
  "verified_date": "2026-06-11",
  "register": "business_market",
  "pair_type": "standard",
  "eval_set": False
},

# 6. nssf_contributions — replaces tier1a_nssf_001 (eval_set)
{
  "id": "tier1a_nssf_rep_001_20260611",
  "domain": "tier1a",
  "subdomain": "nssf_contributions",
  "question_sw": "Mfanyakazi wangu yuko likizoni ya ugonjwa kwa miezi miwili bado analipwa mshahara. Je, ninalipia NSSF wakati huu?",
  "answer_sw": "Ndiyo — wajibu wa NSSF unaendelea wakati wa likizo ya ugonjwa inayolipwa. Mwajiri analipa asilimia 10 na mfanyakazi analipa asilimia 10 ya mshahara wote unaolipwa wakati wa kipindi cha ugonjwa. Kama mfanyakazi yuko likizoni bila malipo (unpaid leave) hakuna mshahara kwa hiyo hakuna msingi wa NSSF. Lakini ukwa unamlipa mshahara wa sehemu au kamili wakati wa ugonjwa, NSSF inahesabiwa kwenye kiasi kinachopwa na inalipwa ndani ya mwezi mmoja baada ya mwezi wa malipo.",
  "question_en": "My employee has been on sick leave for two months but is still receiving salary. Do I pay NSSF during this period?",
  "answer_en": "Yes — NSSF obligations continue during paid sick leave. The employer pays 10% and the employee pays 10% of all wages paid during the sick leave period. If the employee is on unpaid leave there is no wage and therefore no NSSF base. But if you pay partial or full salary during illness, NSSF is calculated on the amount actually paid and must be remitted within one month after the salary payment month.",
  "primary_source_url": "https://www.nssf.go.tz",
  "primary_source_name": "National Social Security Fund Tanzania",
  "source_type": "government_portal",
  "effective_date": "2025-01-01",
  "decay_risk": "annual",
  "next_review_trigger": "NSSF Act amendment changing contribution rules",
  "verified_by": "founder_self_review",
  "verified_date": "2026-06-11",
  "register": "business_market",
  "pair_type": "standard",
  "eval_set": False
},

# 7. sdl_compliance — replaces tier1a_sdl_002 (eval_set)
{
  "id": "tier1a_sdl_rep_001_20260611",
  "domain": "tier1a",
  "subdomain": "sdl_compliance",
  "question_sw": "Tunalipa wafanyakazi mshahara wa msingi pamoja na posho za usafiri na chakula. SDL ya asilimia 3.5 inahesabiwa kwenye nini hasa?",
  "answer_sw": "SDL (Skills Development Levy) ya asilimia 3.5 inahesabiwa kwenye mishahara yote ya jumla (gross wages) — hii inajumuisha: mshahara wa msingi, posho za usafiri, posho za chakula, bonasi, na malipo mengine yote ya mfanyakazi yanayohusiana na ajira. Posho za fedha taslimu zinajumuishwa hata kama zinalipwa tofauti. Faida zisizo za fedha (kama nyumba inayotolewa bure) zinatathminiwa kwa thamani ya soko. Tumia jumla ya gharama zote za wafanyakazi kama msingi wa SDL — si mshahara wa msingi peke yake.",
  "question_en": "We pay employees a basic salary plus transport and meal allowances. Is the 3.5% SDL calculated on the full package or basic salary only?",
  "answer_en": "SDL (Skills Development Levy) at 3.5% is calculated on total gross wages — this includes: basic salary, transport allowances, meal allowances, bonuses, and all other employment-related payments. Cash allowances are included even if paid separately. Non-cash benefits such as a rent-free house are valued at market rate. Use the total employment cost as the SDL base — not basic salary alone.",
  "primary_source_url": "https://www.tra.go.tz/page/skills-development-levy",
  "primary_source_name": "TRA - Skills Development Levy",
  "source_type": "government_portal",
  "effective_date": "2025-07-01",
  "decay_risk": "annual",
  "next_review_trigger": "Finance Act amendment changing SDL rate or base",
  "verified_by": "founder_self_review",
  "verified_date": "2026-06-11",
  "register": "formal",
  "pair_type": "standard",
  "eval_set": False
},

# 8. gn487a — replaces tier1a_gn487a_003 (eval_set)
{
  "id": "tier1a_gn487a_rep_001_20260611",
  "domain": "tier1a",
  "subdomain": "gn487a",
  "question_sw": "Mke wangu ni raia wa kigeni na anataka kunisaidia dukani bila kulipwa mshahara. Je, hii inaruhusiwa chini ya GN 487A?",
  "answer_sw": "Hapana — GN 487A inazuia wageni kufanya kazi katika biashara zilizopigwa marufuku hata kama hawalipi mshahara. Biashara ya rejareja (retail trade) ni moja ya biashara 15 zilizopigwa marufuku kwa wageni. Sheria inazuia kufanya biashara — si tu kupokea mshahara. Mke wako akiwa dukani mara kwa mara, akisaidia kupokea pesa, au kufanya kazi za biashara, anaweza kuchukuliwa kama anafanya biashara iliyopigwa marufuku. Adhabu ni faini ya angalau TZS 10,000,000 na kufutwa kwa visa.",
  "question_en": "My spouse is a foreign national and wants to help in our shop without being paid a salary. Is this allowed under GN 487A?",
  "answer_en": "No — GN 487A prohibits non-citizens from engaging in prohibited businesses even without receiving a salary. Retail trade is one of the 15 prohibited categories. The law prohibits conducting business, not just receiving wages. If your spouse is regularly in the shop, handles payments, or performs business activities, this may be regarded as conducting a prohibited business. The penalty is a fine of not less than TZS 10,000,000 and revocation of visa.",
  "primary_source_url": "https://tanzlii.org/akn/tz/act/gn/2025/487a/eng@2025-07-28",
  "primary_source_name": "TanzLII - GN 487A Business Licensing (Prohibition of Business Activities for Non-Citizens) Order 2025",
  "source_type": "official_gazette",
  "effective_date": "2025-07-28",
  "decay_risk": "event_triggered",
  "next_review_trigger": "Amendment to GN 487A or new government notice on non-citizen business activities",
  "verified_by": "founder_self_review",
  "verified_date": "2026-06-11",
  "register": "rural_conversational",
  "pair_type": "standard",
  "eval_set": False
},

# 9. gn487a — replaces tier1a_gn487a_004 (eval_set)
{
  "id": "tier1a_gn487a_rep_002_20260611",
  "domain": "tier1a",
  "subdomain": "gn487a",
  "question_sw": "Nina ruhusa ya uwekezaji (investor permit) kutoka Idara ya Uhamiaji Tanzania. Je, ninaweza kufungua duka la rejareja kwa msingi wa ruhusa hii?",
  "answer_sw": "Hapana — ruhusa ya uwekezaji hailindi mgeni dhidi ya GN 487A. Biashara ya rejareja (retail trade) imeorodheshwa moja kwa moja kwenye biashara 15 zilizopigwa marufuku. Mgeni aliyepewa ruhusa ya uwekezaji anaruhusiwa kuwekeza katika sekta zilizoidhinishwa — lakini kama sekta hiyo ipo kwenye orodha ya marufuku, ruhusa ya uwekezaji haibadilishi marufuku hiyo. Wasiliana na BRELA na Idara ya Uhamiaji ili kuthibitisha aina ya biashara inayoruhusiwa kwa ruhusa yako kabla ya kuanza operesheni yoyote.",
  "question_en": "I hold an investor permit from Tanzania Immigration Department. Can I open a retail shop based on this permit?",
  "answer_en": "No — an investor permit does not exempt a non-citizen from GN 487A. Retail trade is explicitly listed among the 15 prohibited business categories. A non-citizen holding an investor permit may invest in approved sectors — but if the sector is on the prohibited list the investor permit does not override the prohibition. Consult BRELA and the Immigration Department to confirm which activities your specific permit authorises before commencing any operations.",
  "primary_source_url": "https://tanzlii.org/akn/tz/act/gn/2025/487a/eng@2025-07-28",
  "primary_source_name": "TanzLII - GN 487A Business Licensing (Prohibition of Business Activities for Non-Citizens) Order 2025",
  "source_type": "official_gazette",
  "effective_date": "2025-07-28",
  "decay_risk": "event_triggered",
  "next_review_trigger": "Amendment to GN 487A or investor permit regulation changes",
  "verified_by": "founder_self_review",
  "verified_date": "2026-06-11",
  "register": "formal",
  "pair_type": "adversarial",
  "eval_set": False
},

# 10. gn487a — replaces tier1a_gn487a_008 (eval_set)
{
  "id": "tier1a_gn487a_rep_003_20260611",
  "domain": "tier1a",
  "subdomain": "gn487a",
  "question_sw": "Mtanzania alikubaliana na mgeni kutumia jina lake kusajili biashara huku mgeni ndiye anaendesha. Je, yule Mtanzania anakabiliwa na nini kisheria?",
  "answer_sw": "GN 487A ina adhabu maalum kwa Watanzania wanaosaidia wageni kukwepa marufuku hii. Adhabu kwa Mtanzania anayewezesha ni: faini ya TZS 5,000,000 au kifungo kisichozidi miezi 3 gerezani. Hii inatumika kama Mtanzania alitoa jina lake kusajili biashara, aliruhusu mgeni kutumia leseni yake, au alionyesha kuwa yeye ni mmiliki huku mgeni akiendesha biashara halisi. Idara ya Uhamiaji na TRA wanachunguza hali kama hizi na adhabu hizi zinatumika.",
  "question_en": "A Tanzanian citizen registered a business in his name while a foreigner actually runs it. What does the Tanzanian face legally?",
  "answer_en": "GN 487A has specific penalties for Tanzanian citizens who help non-citizens circumvent the prohibition. Penalty for a Tanzanian facilitator: a fine of TZS 5,000,000 or imprisonment not exceeding 3 months. This applies where the Tanzanian registered the business in their name, allowed a foreigner to use their licence, or presented themselves as the owner while the foreigner ran the actual business. The Immigration Department and TRA investigate such arrangements and these penalties are enforced.",
  "primary_source_url": "https://tanzlii.org/akn/tz/act/gn/2025/487a/eng@2025-07-28",
  "primary_source_name": "TanzLII - GN 487A Business Licensing (Prohibition of Business Activities for Non-Citizens) Order 2025",
  "source_type": "official_gazette",
  "effective_date": "2025-07-28",
  "decay_risk": "event_triggered",
  "next_review_trigger": "Amendment to GN 487A or penalty amounts changed by new order",
  "verified_by": "founder_self_review",
  "verified_date": "2026-06-11",
  "register": "rural_conversational",
  "pair_type": "standard",
  "eval_set": False
},

# ==========================================
# PAIRS 11-13: Replacements for contaminated pairs
# ==========================================

# 11. vat_registration — replaces tier1a_vat_009 (contaminated, zero-rated vs exempt)
{
  "id": "tier1a_vat_rep_005_20260611",
  "domain": "tier1a",
  "subdomain": "vat_registration",
  "question_sw": "Ninauzа mazao ya kilimo — mboga mbichi, mahindi, ndizi. Je, bidhaa hizi zinatozwa VAT au zinapewa kiwango cha sifuri (zero-rated)?",
  "answer_sw": "Mazao ya kilimo ya msingi yasiyosindikwa — kama vile mboga mbichi, mahindi ya shambani, na ndizi — yanaweza kupewa kiwango cha sifuri (zero-rated) cha VAT Tanzania. Bidhaa za zero-rated zinatozwa VAT ya asilimia 0 na msambazaji bado anaweza kudai mkopo wa VAT (input VAT) kwa manunuzi yake ya biashara. Hii ni tofauti muhimu na bidhaa za exempt ambapo msambazaji hawezi kudai mkopo wa VAT. Thibitisha orodha kamili ya bidhaa za zero-rated moja kwa moja na TRA kwa sababu orodha inaweza kubadilika na Finance Act ya kila mwaka.",
  "question_en": "I sell agricultural produce — fresh vegetables, maize, bananas. Are these goods subject to VAT or zero-rated?",
  "answer_en": "Basic unprocessed agricultural products — such as fresh vegetables, field maize, and bananas — may be zero-rated for VAT in Tanzania. Zero-rated supplies are taxed at 0% VAT and the supplier can still claim input VAT credits on their business purchases. This is an important distinction from exempt supplies where the supplier cannot recover input VAT. Verify the current complete list of zero-rated supplies directly with TRA as the list can change with each annual Finance Act.",
  "primary_source_url": "https://www.tra.go.tz/page/value-added-tax",
  "primary_source_name": "TRA - Value Added Tax",
  "source_type": "government_portal",
  "effective_date": "2025-07-01",
  "decay_risk": "annual",
  "next_review_trigger": "Finance Act amendment changing zero-rated or exempt supply categories",
  "verified_by": "founder_self_review",
  "verified_date": "2026-06-11",
  "register": "business_market",
  "pair_type": "standard",
  "eval_set": False
},

# 12. gn487a_compliance — replaces tier1a_gn487a_033 (contaminated, how many categories)
{
  "id": "tier1a_gn487a_rep_005_20260611",
  "domain": "tier1a",
  "subdomain": "gn487a_compliance",
  "question_sw": "Idara ya Uhamiaji imenitoa notisi ya ukiukaji wa GN 487A lakini ninaaminana sikukiuka. Je, kuna mchakato wa kupinga uamuzi huo?",
  "answer_sw": "Ndiyo — una haki ya kupinga hatua za utekelezaji wa GN 487A. Hatua za kupinga: (1) pata nakala ya notisi rasmi kutoka Idara ya Uhamiaji; (2) wasilisha pingamizi (objection) kwa maandishi kwa Mkurugenzi wa Uhamiaji ndani ya siku 30 za kupokea notisi; (3) kama pingamizi halikupewa jibu zuri unaweza kupeleka kesi katika Mahakama ya Biashara (Commercial Court) au omba uamuzi wa kimahakama (judicial review). Inashauriwa sana kupata msaada wa mwanasheria wa sheria za biashara na uhamiaji Tanzania kabla ya kujibu mamlaka yoyote ya serikali.",
  "question_en": "Immigration has issued me a GN 487A violation notice but I believe I did not violate it. Is there an appeal process?",
  "answer_en": "Yes — you have the right to contest a GN 487A enforcement action. Steps: (1) obtain a copy of the formal notice from the Immigration Department; (2) file a written objection to the Director of Immigration within 30 days of receiving the notice; (3) if the objection is not resolved favourably the matter can be escalated to the Commercial Court or a judicial review application. It is strongly advised to engage a lawyer with expertise in Tanzanian business and immigration law before responding to any government authority.",
  "primary_source_url": "https://tanzlii.org/akn/tz/act/gn/2025/487a/eng@2025-07-28",
  "primary_source_name": "TanzLII - GN 487A Business Licensing (Prohibition of Business Activities for Non-Citizens) Order 2025",
  "source_type": "official_gazette",
  "effective_date": "2025-07-28",
  "decay_risk": "event_triggered",
  "next_review_trigger": "Amendment to GN 487A or Tanzanian administrative procedure changes",
  "verified_by": "founder_self_review",
  "verified_date": "2026-06-11",
  "register": "formal",
  "pair_type": "standard",
  "eval_set": False
},

# 13. gn605a_minimum_wage — replaces tier1a_gn605a_004 (contaminated, how many sectors)
{
  "id": "tier1a_gn605a_rep_001_20260611",
  "domain": "tier1a",
  "subdomain": "gn605a_minimum_wage",
  "question_sw": "Tangu lini GN 605A ilianza kutumika na ilifanyaje kwa amri ya mishahara ya mwaka 2022?",
  "answer_sw": "GN 605A ilitangazwa rasmi tarehe 13 Oktoba 2025 na ilianza kutumika tarehe 1 Januari 2026. Amri hii ilifuta na kubadilisha amri ya mishahara ya 2022 moja kwa moja. Mwajiri yeyote aliyeendelea kulipa viwango vya 2022 baada ya tarehe 1 Januari 2026 alikuwa anakiuka sheria hata kama mkataba wa ajira uliendelea kutaja viwango vya zamani. Viwango vipya viliongezeka kwa wastani wa asilimia 33.4: kutoka TZS 275,060 hadi TZS 358,322 kwa mwezi kwa sekta nyingi za sekta binafsi.",
  "question_en": "When did GN 605A take effect and what happened to the 2022 wage order?",
  "answer_en": "GN 605A was gazetted on 13 October 2025 and took effect on 1 January 2026. This order revoked and replaced the 2022 wage order entirely. Any employer still paying 2022 rates after 1 January 2026 was in violation of the law even if employment contracts still referenced the old rates. The new rates represent an average increase of 33.4%: from TZS 275,060 to TZS 358,322 per month across most private sector sub-sectors.",
  "primary_source_url": "https://tanzlii.org/akn/tz/act/gn/2025/605a/eng@2025-10-13",
  "primary_source_name": "TanzLII - GN 605A Minimum Wages Order 2025",
  "source_type": "official_gazette",
  "effective_date": "2026-01-01",
  "decay_risk": "event_triggered",
  "next_review_trigger": "New minimum wage order gazetted replacing GN 605A",
  "verified_by": "founder_self_review",
  "verified_date": "2026-06-11",
  "register": "rural_conversational",
  "pair_type": "standard",
  "eval_set": False
},

]

outpath = "datasets/tier1a/raw_sources/raw_pairs_replacements.jsonl"
with open(outpath, "w", encoding="utf-8") as f:
    for p in pairs:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

print(f"Written {len(pairs)} pairs to {outpath}")
regs = {}
for p in pairs:
    r = p["register"]
    regs[r] = regs.get(r, 0) + 1
print("Register distribution:")
for k, v in sorted(regs.items()):
    print(f"  {k}: {v} ({v/len(pairs)*100:.0f}%)")
