#!/usr/bin/env python3
"""batch_005 part 4 — compliance_costs_deep (50 pairs, 151-200)"""
import json, os

OUT = "datasets/tier1a/raw_sources/raw_pairs_batch_005.jsonl"
D = "2026-06-09"
TRA = "https://www.tra.go.tz"
TRA_N = "Tanzania Revenue Authority"
BRELA = "https://www.brela.go.tz"
BRELA_N = "BRELA — Business Registrations and Licensing Agency"
OSHA = "https://www.osha.go.tz"
OSHA_N = "OSHA — Occupational Safety and Health Authority"
NSSF = "https://www.nssf.go.tz"
NSSF_N = "NSSF — National Social Security Fund"
WCF = "https://portal.wcf.go.tz"
WCF_N = "WCF — Workers Compensation Fund"
GP = "government_portal"
ANN = "annual"
ST = "stable"
EVT = "event_triggered"

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
# COMPLIANCE COSTS DEEP — 50 pairs (151-200)
# Full compliance cost picture for informal/small Tanzania businesses
# Sources: BRELA, TRA, OSHA, NSSF, WCF portals
# =====================================================================

p("tier1a_compliance_costs_151_20260609","compliance_costs",
  "Biashara mpya ndogo ya Tanzania inahitaji kusajiliwa wapi kwanza?",
  "Biashara mpya ndogo ya Tanzania inaanza kwa: (1) BRELA — kusajili jina la biashara "
  "au kampuni (TZS 50,000 kwa hifadhi ya jina, TZS 95,000+ kwa uanzishaji wa kampuni), "
  "(2) TRA — kupata TIN (Taxpayer Identification Number) bila ada, (3) TRA — kusajili "
  "VAT ikiwa mauzo yanazidi TZS 200M/mwaka, (4) LGA ya eneo lako — leseni ya biashara. "
  "Mpangilio huu wa usajili unafuatwa kwa kawaida.",
  "Where does a new small Tanzania business need to register first?",
  "A new small Tanzania business starts with: (1) BRELA — register the business name "
  "or company (TZS 50,000 for name reservation, TZS 95,000+ for company incorporation), "
  "(2) TRA — get a TIN (Taxpayer Identification Number) at no fee, (3) TRA — register "
  "for VAT if turnover exceeds TZS 200M/year, (4) Local Government Authority (LGA) — "
  "business licence. This registration sequence is the standard path.",
  BRELA, BRELA_N, GP, "2025-07-01", ANN, "BRELA fee update or LGA fee change",
  "business_market", "standard"),

p("tier1a_compliance_costs_152_20260609","compliance_costs",
  "TIN ya TRA inagharimu kiasi gani na inachukua muda gani kupata?",
  "TIN (Taxpayer Identification Number) ya TRA Tanzania inapatikana BURE — hakuna ada. "
  "Unaweza kuomba mtandaoni kupitia mfumo wa TRA (tra.go.tz) au ofisini. Kawaida "
  "inachukua siku 1-3 za kazi. Unahitaji: hati ya utambulisho (NIDA/passport), "
  "ushahidi wa anwani, na kwa kampuni, hati za BRELA. TIN inahitajika kwa kila "
  "mwanahisa na mkurugenzi wa kampuni pia.",
  "How much does a TRA TIN cost and how long does it take to obtain?",
  "A TRA TIN (Taxpayer Identification Number) in Tanzania is FREE — no fee. You can "
  "apply online through the TRA system (tra.go.tz) or in person. It typically takes "
  "1-3 working days. You need: ID document (NIDA/passport), proof of address, and "
  "for a company, BRELA documents. A TIN is also required for each shareholder and "
  "director of the company.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA registration process update",
  "business_market", "standard"),

p("tier1a_compliance_costs_153_20260609","compliance_costs",
  "Leseni ya biashara ya LGA inagharimu kiasi gani na inahuishwa lini?",
  "Ada ya leseni ya biashara ya Mamlaka ya Serikali za Mitaa (LGA) inatofautiana "
  "kulingana na aina ya biashara, eneo, na ukubwa. Kwa biashara ndogo za kawaida "
  "mji mkubwa, ada inaweza kuanzia TZS 50,000 hadi TZS 500,000+ kwa mwaka. "
  "Leseni huhuishwa kila mwaka — tarehe ya mwisho ni 31 Machi ya mwaka unaofuata. "
  "Kuendesha biashara bila leseni ya LGA ni kosa na kunaweza kusababisha faini au "
  "kufungwa kwa biashara.",
  "How much does an LGA business licence cost and when is it renewed?",
  "The Local Government Authority (LGA) business licence fee varies by business type, "
  "location, and size. For ordinary small businesses in major cities, fees can range "
  "from TZS 50,000 to TZS 500,000+ per year. Licences are renewed annually — the "
  "deadline is 31 March of the following year. Operating without an LGA business "
  "licence is an offence and can result in fines or business closure.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "LGA fee schedule update",
  "business_market", "standard"),

p("tier1a_compliance_costs_154_20260609","compliance_costs",
  "Usajili wa NSSF unagharimu kiasi gani na unachukua muda gani?",
  "Usajili wa NSSF (National Social Security Fund) hauna ada ya usajili — ni BURE. "
  "Mwajiri anasajili kampuni yake na NSSF na kisha anasajili wafanyakazi wake. "
  "Mchakato unachukua siku 1-5 za kazi. Mara baada ya usajili, mwajiri anaanza "
  "kukatia na kuwasilisha michango ya NSSF kila mwezi (mwajiri 10% + mfanyakazi 10% "
  "= 20% ya mshahara wa jumla) ifikapo tarehe 10 ya mwezi unaofuata.",
  "How much does NSSF registration cost and how long does it take?",
  "NSSF (National Social Security Fund) registration has no registration fee — it is "
  "FREE. An employer registers their company with NSSF and then registers their "
  "employees. The process takes 1-5 working days. Once registered, the employer "
  "begins deducting and remitting NSSF contributions monthly (employer 10% + employee "
  "10% = 20% of gross wage) by the 10th of the following month.",
  NSSF, NSSF_N, GP, "2025-07-01", ANN, "NSSF Act amendment or registration process update",
  "business_market", "standard"),

p("tier1a_compliance_costs_155_20260609","compliance_costs",
  "Usajili wa OSHA unagharimu kiasi gani kwa biashara ndogo?",
  "Ada ya usajili wa OSHA (Occupational Safety and Health Authority) inategemea "
  "ukubwa wa biashara — idadi ya wafanyakazi na aina ya biashara. Kwa biashara ndogo "
  "zenye wafanyakazi chache (kama 10), ada inaweza kuwa TZS 50,000-150,000 kwa mwaka. "
  "Mwajiri mwenye wafanyakazi 10+ kwenye Mainland Tanzania analazimika kusajili OSHA. "
  "Angalia osha.go.tz kwa jedwali la ada la hali ya sasa.",
  "How much does OSHA registration cost for a small business?",
  "The OSHA (Occupational Safety and Health Authority) registration fee depends on "
  "business size — number of employees and type of business. For small businesses "
  "with few workers (say 10), fees can range from TZS 50,000-150,000 per year. "
  "Employers with 10+ workers on Mainland Tanzania are required to register with OSHA. "
  "Check osha.go.tz for the current fee schedule.",
  OSHA, OSHA_N, GP, "2025-07-01", ANN, "OSHA fee schedule update",
  "business_market", "standard"),

p("tier1a_compliance_costs_156_20260609","compliance_costs",
  "WCF (Workers Compensation Fund) usajili unagharimu kiasi gani?",
  "Usajili wa WCF hauna ada ya usajili ya moja kwa moja — gharama kuu ni mchango wa "
  "kila mwaka (annual premium) unaohesabiwa kwa asilimia 0.5% ya jumla ya mishahara "
  "ya mwaka. Kwa mfano, kampuni yenye mishahara ya TZS 100M kwa mwaka italipa "
  "TZS 500,000 kwa WCF kwa mwaka. Mwajiri mwenye wafanyakazi 1+ Tanzania analazimika "
  "kusajili WCF. Angalia portal.wcf.go.tz kwa mchakato wa usajili.",
  "How much does WCF (Workers Compensation Fund) registration cost?",
  "WCF registration has no direct registration fee — the main cost is the annual "
  "premium calculated at 0.5% of total annual payroll. For example, a company with "
  "TZS 100M annual payroll pays TZS 500,000 per year to WCF. Employers with 1+ "
  "workers in Tanzania are required to register with WCF. Check portal.wcf.go.tz "
  "for the registration process.",
  WCF, WCF_N, GP, "2025-07-01", ANN, "WCF Act amendment or premium rate update",
  "business_market", "standard"),

p("tier1a_compliance_costs_157_20260609","compliance_costs",
  "Biashara ndogo yenye wafanyakazi 5 Tanzania inahitaji kulipa mchango wa SDL?",
  "Hapana. SDL (Skills Development Levy) inatumika kwa waajiri wenye wafanyakazi "
  "10 AU ZAIDI kwenye Mainland Tanzania. Biashara yenye wafanyakazi 5 tu "
  "HAIHITAJIKI kulipa SDL. Ikiwa biashara itakua na kufikia wafanyakazi 10, "
  "basi itaanza kulipa SDL ya asilimia 3.5 ya jumla ya mishahara kila mwezi.",
  "Does a small business with 5 employees in Tanzania need to pay SDL?",
  "No. SDL (Skills Development Levy) applies to employers with 10 OR MORE employees "
  "on Mainland Tanzania. A business with only 5 employees is NOT required to pay SDL. "
  "Once the business grows to reach 10 employees, it then starts paying SDL at 3.5% "
  "of total gross payroll monthly.",
  TRA, TRA_N, GP, "2021-07-01", ANN, "Finance Act SDL threshold update",
  "business_market", "standard"),

p("tier1a_compliance_costs_158_20260609","compliance_costs",
  "Gharama ya jumla ya kufuata sheria za biashara kwa miaka ya kwanza kwa biashara "
  "ndogo ya Tanzania ni kiasi gani kwa kawaida?",
  "Makadirio ya gharama za kufuata sheria (compliance costs) kwa biashara ndogo mpya "
  "ya Tanzania (wafanyakazi 5-10, mauzo chini ya TZS 200M): "
  "BRELA usajili TZS 95,000-200,000 (mara moja), TIN bure, "
  "LGA leseni TZS 50,000-300,000 kwa mwaka, NSSF usajili bure (michango 20% ya mishahara), "
  "OSHA TZS 50,000-150,000 kwa mwaka, WCF 0.5% ya mishahara kwa mwaka, "
  "EFD machine TZS 250,000-500,000 ikiwa inasajili VAT. "
  "Jumla ya mara moja: ~TZS 200,000-700,000. Kila mwaka: kulingana na mishahara.",
  "What is the typical total compliance cost in the first years for a small Tanzania business?",
  "Estimated compliance costs for a new small Tanzania business (5-10 employees, "
  "turnover below TZS 200M): BRELA registration TZS 95,000-200,000 (one-time), TIN free, "
  "LGA licence TZS 50,000-300,000 per year, NSSF registration free (contributions 20% of payroll), "
  "OSHA TZS 50,000-150,000 per year, WCF 0.5% of payroll per year, "
  "EFD machine TZS 250,000-500,000 if registering for VAT. "
  "One-time costs: ~TZS 200,000-700,000. Annual: depends on payroll.",
  BRELA, BRELA_N, GP, "2025-07-01", ANN, "Registration fee or compliance cost update",
  "business_market", "standard"),

p("tier1a_compliance_costs_159_20260609","compliance_costs",
  "Biashara yenye TIN tu lakini bila leseni ya LGA inaweza kufanya biashara halali Tanzania?",
  "Hapana. TIN inaonyesha usajili wa kodi — haiipi ruhusa ya kufanya biashara. "
  "Leseni ya biashara ya LGA ndiyo inayokuruhusu kisheria kufungua na kuendesha "
  "biashara katika eneo fulani. Biashara yenye TIN tu bado inaweza kukutana na "
  "ukaguzi wa LGA na kutozwa faini ya kufanya biashara bila leseni. TIN na leseni "
  "ya LGA ni mahitaji tofauti yanayofanya kazi pamoja.",
  "Can a business with only a TIN but no LGA licence operate legally in Tanzania?",
  "No. A TIN shows tax registration — it does not grant permission to operate a "
  "business. The LGA business licence is what legally authorises you to open and "
  "run a business in a specific area. A business with only a TIN can still face LGA "
  "inspection and be fined for operating without a licence. TIN and LGA licence are "
  "separate requirements that work together.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Business Licensing Act update",
  "rural_conversational", "adversarial"),

p("tier1a_compliance_costs_160_20260609","compliance_costs",
  "Mwajiri mdogo mwenye wafanyakazi 3 tu anahitaji EFD machine?",
  "Wajibu wa EFD (Electronic Fiscal Device) unategemea aina ya biashara na "
  "ukubwa wa mauzo — SI idadi ya wafanyakazi. EFD inahitajika kwa: biashara zote "
  "zilizosajili VAT, baadhi ya biashara zilizo na mauzo ya chini lakini zimeorodheshwa "
  "na TRA. Biashara ndogo isiyo na usajili wa VAT na isiyo kwenye orodha ya TRA "
  "inaweza isihitaji EFD. Angalia TRA moja kwa moja kwa biashara yako.",
  "Does a small employer with only 3 workers need an EFD machine?",
  "The EFD (Electronic Fiscal Device) obligation depends on business type and turnover "
  "— NOT the number of employees. EFD is required for: all VAT-registered businesses, "
  "some businesses with lower turnover but listed by TRA. A small business not "
  "registered for VAT and not on TRA's list may not need an EFD. Check directly "
  "with TRA for your specific business.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA EFD mandate update",
  "rural_conversational", "standard"),

p("tier1a_compliance_costs_161_20260609","compliance_costs",
  "EFD machine inagharimu kiasi gani Tanzania na mwajiri analipa au TRA?",
  "EFD machine nchini Tanzania inagharimu kati ya TZS 250,000 hadi TZS 500,000 "
  "au zaidi kulingana na aina na mzalishaji. MWAJIRI (biashara) ndiye anayenunua "
  "EFD — si TRA. Hata hivyo, TRA inaidhinisha wasambazaji wa EFD na inahitaji kwamba "
  "EFD inunuliwa kutoka kwa msambazaji aliyeidhinishwa na kuunganishwa kwenye mfumo "
  "wa TRA. Ada ya uunganisho na matengenezo ya kila mwaka inaweza kuwa ya ziada.",
  "How much does an EFD machine cost in Tanzania and does the employer or TRA pay?",
  "An EFD machine in Tanzania costs between TZS 250,000 and TZS 500,000 or more "
  "depending on type and manufacturer. The EMPLOYER (business) buys the EFD — not "
  "TRA. However, TRA approves EFD suppliers and requires that the EFD is purchased "
  "from an approved supplier and connected to the TRA system. Connection and annual "
  "maintenance fees may be additional.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA EFD fee or supplier update",
  "business_market", "standard"),

p("tier1a_compliance_costs_162_20260609","compliance_costs",
  "Kampuni ndogo isiyolipa kodi kwa wakati inapata adhabu ngapi Tanzania?",
  "Adhabu za kuchelewa kwa Tanzania zinategemea aina ya kodi: "
  "PAYE: asilimia 2.5 kwa mwezi wa kiasi kilichochelewa. "
  "VAT: asilimia 2 kwa mwezi + faini ya mara moja ya asilimia 25. "
  "NSSF: asilimia 5 kwa mwezi. "
  "SDL: adhabu kama PAYE. "
  "Adhabu hizi zinaendelea kujilimbikiza kila mwezi hadi kiasi kimelipwa. "
  "Kutofungua faili kabisa kunaweza kusababisha ukaguzi wa TRA na tathmini za kodi.",
  "What penalties does a small company face for late tax payment in Tanzania?",
  "Late payment penalties in Tanzania depend on the tax type: "
  "PAYE: 2.5% per month of the overdue amount. "
  "VAT: 2% per month plus a one-time 25% penalty. "
  "NSSF: 5% per month. "
  "SDL: penalties similar to PAYE. "
  "These penalties compound every month until the amount is paid. Failing to file "
  "at all can trigger a TRA audit and tax assessments.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act or Tax Administration Act update",
  "business_market", "standard"),

p("tier1a_compliance_costs_163_20260609","compliance_costs",
  "Ukaguzi wa TRA (tax audit) unafanywa mara ngapi kwa biashara ndogo Tanzania?",
  "TRA inafanya ukaguzi wa kodi kulingana na tathmini ya hatari (risk-based auditing). "
  "Biashara ndogo iliyofuata vizuri sheria za kodi inaweza isikaguliwe kwa miaka mingi. "
  "Ukaguzi unaweza kusababishwa na: tofauti kubwa kati ya mapato yaliyoripotiwa na "
  "mauzo ya benki, malalamiko ya watu wengine, sekta zenye hatari ya juu, au "
  "uteuzi wa nasibu. Huhifadhi rekodi nzuri za miaka 5+ kwa ajili ya ukaguzi wowote.",
  "How often does TRA conduct a tax audit on a small business in Tanzania?",
  "TRA conducts tax audits based on risk assessment (risk-based auditing). A small "
  "business that has complied well with tax laws may not be audited for many years. "
  "An audit can be triggered by: large discrepancy between reported income and bank "
  "deposits, complaints from others, high-risk sectors, or random selection. Keep "
  "good records for 5+ years in case of any audit.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA audit policy update",
  "formal", "standard"),

p("tier1a_compliance_costs_164_20260609","compliance_costs",
  "Biashara ya rejareja ndogo (duka) inahitaji leseni ngapi Tanzania kwa ujumla?",
  "Duka la rejareja ndogo Tanzania kwa kawaida linahitaji: (1) Leseni ya biashara ya "
  "LGA (kila mwaka, 31 Machi), (2) TIN ya TRA (mara moja), (3) NSSF ikiwa ana "
  "wafanyakazi wanaolipwa, (4) WCF ikiwa ana wafanyakazi, (5) EFD ikiwa imesajili "
  "VAT au TRA imeamuru. Leseni maalum zaidi zinaweza kuhitajika kulingana na bidhaa "
  "zinazouzwa — kama dawa (TMDA), chakula (TFNC/TMDA), pombe (leseni ya biashara ya "
  "pombe).",
  "How many licences does a small retail shop generally need in Tanzania?",
  "A small retail shop in Tanzania typically needs: (1) LGA business licence (annual, "
  "31 March), (2) TRA TIN (once), (3) NSSF if it has paid employees, (4) WCF if it "
  "has employees, (5) EFD if VAT-registered or TRA has directed it. More specific "
  "licences may be required depending on goods sold — such as medicine (TMDA), food "
  "(TFNC/TMDA), or alcohol (liquor business licence).",
  BRELA, BRELA_N, GP, "2025-07-01", ANN, "Licensing framework update",
  "rural_conversational", "standard"),

p("tier1a_compliance_costs_165_20260609","compliance_costs",
  "Gharama za kutokufuata sheria (non-compliance) ni ndogo kuliko gharama za kufuata "
  "sheria kwa biashara ndogo — je, hii ni ukweli wa kibiashara?",
  "Hii ni mtazamo wa hatari sana na si sahihi kwa muda mrefu. Gharama za kweli za "
  "kutokufuata sheria ni pamoja na: adhabu za kujilimbikiza (2.5-5% kwa mwezi), "
  "hatari ya kufungwa kwa biashara, ukosefu wa ushirikiano na benki na washirika wa "
  "biashara wanaohitaji uthibitisho wa uzingatiaji, na hatari ya jinai kwa baadhi ya "
  "makosa. Biashara zisizofuata sheria mara nyingi haziwezi kukua kwa sababu "
  "haziwezi kupata mikopo ya benki au mikataba ya serikali.",
  "The cost of non-compliance is less than the cost of compliance for a small business "
  "— is this a business reality?",
  "This is a very risky view and is not correct over the long term. Real non-compliance "
  "costs include: accumulating penalties (2.5-5% per month), risk of business closure, "
  "inability to partner with banks and business partners who require compliance proof, "
  "and criminal risk for some offences. Non-compliant businesses often cannot grow "
  "because they cannot access bank loans or government contracts.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax enforcement update",
  "business_market", "adversarial"),

p("tier1a_compliance_costs_166_20260609","compliance_costs",
  "Kampuni iliyosimamishwa shughuli (dormant company) bado inalipa ada za kila "
  "mwaka kwa BRELA?",
  "Ndiyo. Kampuni iliyosajiliwa Tanzania — hata kama haifanyi shughuli yoyote — "
  "bado inalazimika kuwasilisha ripoti ya kila mwaka (annual return) kwa BRELA ndani "
  "ya siku 42 baada ya siku ya kumbukumbu ya usajili. Kushindwa kuwasilisha kunaweza "
  "kusababisha adhabu au kampuni kufutwa orodha. Ikiwa huhitaji kampuni tena, "
  "ni bora kufuata mchakato rasmi wa kufuta (deregistration).",
  "Does a dormant company still need to pay annual fees to BRELA?",
  "Yes. A registered Tanzania company — even if it conducts no activities — is still "
  "required to file an annual return to BRELA within 42 days of the anniversary of "
  "its registration date. Failure to file can result in penalties or the company "
  "being struck off the register. If you no longer need the company, it is better "
  "to follow the formal deregistration process.",
  BRELA, BRELA_N, GP, "2025-07-01", ANN, "BRELA annual return requirement update",
  "business_market", "standard"),

p("tier1a_compliance_costs_167_20260609","compliance_costs",
  "Mshauri wa kodi au mhasibu ni lazima kwa biashara ndogo Tanzania — au "
  "mwenye biashara anaweza kujiendesha mwenyewe?",
  "Kisheria, hakuna wajibu wa kuwa na mshauri wa kodi au mhasibu kwa biashara ndogo "
  "Tanzania. Mwenye biashara anaweza kuwasilisha tamko lake la kodi mwenyewe. Hata "
  "hivyo, kwa vitendo: makosa ya kodi yanasababisha adhabu kubwa, TRA inaweza kukagua "
  "hesabu zako, na mhasibu mzuri anaweza kupunguza kodi halali kupitia makato sahihi. "
  "Gharama ya mshauri (TZS 200,000-1M+/mwaka kwa biashara ndogo) mara nyingi "
  "inazingatiwa kidogo ikilinganishwa na thamani anayoiongeza.",
  "Is a tax adviser or accountant mandatory for a small business in Tanzania — or "
  "can the owner self-manage?",
  "Legally, there is no obligation to have a tax adviser or accountant for a small "
  "Tanzania business. The owner can file their own tax returns. However, practically: "
  "tax errors lead to large penalties, TRA can audit your accounts, and a good "
  "accountant can legitimately reduce tax through correct deductions. The cost of "
  "an adviser (TZS 200,000-1M+/year for a small business) is often small compared "
  "to the value they add.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Administration Act update",
  "business_market", "standard"),

p("tier1a_compliance_costs_168_20260609","compliance_costs",
  "Biashara ya mtu mmoja (sole proprietorship) inahitaji akaunti ya benki tofauti "
  "na akaunti yake binafsi Tanzania?",
  "Kisheria, haijawekwa wazi kwamba biashara ya mtu mmoja lazima iwe na akaunti "
  "tofauti ya benki ya biashara. Hata hivyo, vitendo vya kibiashara na kodi "
  "vinahitaji sana: (1) TRA inaweza kuuliza rekodi za fedha za biashara — "
  "kuchanganya na akaunti binafsi kunafanya hivi vigumu, (2) benki nyingi "
  "zinahitaji akaunti ya biashara kwa mikopo ya biashara, (3) wasambazaji na "
  "wateja wa biashara mara nyingi wanapendelea kulipa akaunti ya biashara rasmi.",
  "Does a sole proprietorship in Tanzania need a separate bank account from their "
  "personal account?",
  "Legally, it is not explicitly required that a sole proprietorship have a separate "
  "business bank account. However, business and tax practice strongly requires: "
  "(1) TRA can request business financial records — mixing with personal account "
  "makes this very difficult, (2) most banks require a business account for business "
  "loans, (3) suppliers and business customers often prefer to pay a formal business "
  "account.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Banking practice update",
  "business_market", "standard"),

p("tier1a_compliance_costs_169_20260609","compliance_costs",
  "Hatua za kufuta kampuni BRELA Tanzania ni zipi na zinagharimu kiasi gani?",
  "Kufuta kampuni Tanzania (voluntary dissolution) inahusisha: (1) uamuzi wa "
  "wanaohisa kukubaliana kufuta, (2) kuwasilisha fomu maalum za kufuta kwa BRELA, "
  "(3) kuhakikisha madeni yote yamelipwa au kukubaliana na wadai, (4) kupata uthibitisho "
  "wa TRA kwamba hakuna deni la kodi linalosimama, (5) BRELA inafuta kampuni rasmi. "
  "Ada za kufuta kwa BRELA ni ndogo (TZS 20,000-50,000). Mchakato unaweza kuchukua "
  "miezi 2-6.",
  "What are the steps to deregister a company at BRELA in Tanzania and how much does it cost?",
  "Deregistering a Tanzania company (voluntary dissolution) involves: (1) shareholder "
  "resolution to dissolve, (2) filing specific dissolution forms with BRELA, (3) ensuring "
  "all debts are paid or agreed with creditors, (4) obtaining TRA clearance confirming "
  "no outstanding tax debt, (5) BRELA formally removes the company. "
  "BRELA dissolution fees are small (TZS 20,000-50,000). The process can take 2-6 months.",
  BRELA, BRELA_N, GP, "2025-07-01", ANN, "BRELA dissolution process update",
  "formal", "standard"),

p("tier1a_compliance_costs_170_20260609","compliance_costs",
  "Mwenye biashara ndogo anaweza kusajili biashara yake peke yake bila wakili?",
  "Ndiyo. Usajili wa biashara Tanzania unaweza kufanywa na mwenye biashara mwenyewe "
  "bila wakili au mshauri. BRELA ina mfumo wa mtandaoni (brela.go.tz) na TRA ina "
  "mfumo wa mtandaoni (tra.go.tz) ambapo usajili unaweza kufanywa moja kwa moja. "
  "Hata hivyo, kwa muundo wa kampuni (limited company) na wanaohisa wengi, wakili "
  "anaweza kusaidia kuhakikisha nyaraka za msingi (Memorandum na Articles) "
  "zinafanya kazi vizuri kwa mahitaji yako.",
  "Can a small business owner register their business themselves without a lawyer?",
  "Yes. Business registration in Tanzania can be done by the business owner themselves "
  "without a lawyer or consultant. BRELA has an online system (brela.go.tz) and TRA "
  "has an online system (tra.go.tz) where registration can be done directly. However, "
  "for a company structure (limited company) with multiple shareholders, a lawyer "
  "can help ensure the founding documents (Memorandum and Articles) work well for "
  "your specific needs.",
  BRELA, BRELA_N, GP, "2025-07-01", ANN, "BRELA online system update",
  "rural_conversational", "standard"),

p("tier1a_compliance_costs_171_20260609","compliance_costs",
  "Biashara ya mauzo ya mtandaoni peke yake (online-only) inahitaji usajili wa "
  "BRELA Tanzania?",
  "Ndiyo. Biashara yoyote inayofanya shughuli Tanzania — ikiwa ni pamoja na biashara "
  "ya mtandaoni peke yake — inahitaji usajili wa kisheria. Ikiwa ni biashara ya mtu "
  "mmoja, angalau jina la biashara linapaswa kusajiliwa BRELA. Ikiwa ni kampuni, "
  "kampuni lazima isajiliwe BRELA. TIN pia inahitajika. Biashara ya mtandaoni "
  "peke yake HAIEPUKI mahitaji ya kisheria ya Tanzania.",
  "Does an online-only business need BRELA registration in Tanzania?",
  "Yes. Any business operating in Tanzania — including an online-only business — "
  "needs legal registration. If it is a sole proprietorship, at minimum the business "
  "name should be registered at BRELA. If it is a company, the company must be "
  "registered at BRELA. A TIN is also required. An online-only business does NOT "
  "escape Tanzania's legal registration requirements.",
  BRELA, BRELA_N, GP, "2025-07-01", ANN, "Business registration framework update",
  "business_market", "adversarial"),

p("tier1a_compliance_costs_172_20260609","compliance_costs",
  "Mfanyabiashara anayeuza kwa VICOBA au vikundi vya akiba tu anahitaji TIN Tanzania?",
  "Ndiyo. Kila mtu anayefanya shughuli za kibiashara Tanzania anahitaji TIN — "
  "hata kama wanauza kwa vikundi vya ndani tu. Mauzo kwa VICOBA bado ni mapato ya "
  "kibiashara yanayolazimishwa kwa kodi ya mapato. TIN ni mahitaji ya msingi ya "
  "kufanya biashara rasmi Tanzania. Usajili ni bure na unachukua siku 1-3.",
  "Does a trader who only sells to VICOBAs or savings groups need a TIN in Tanzania?",
  "Yes. Every person conducting business activities in Tanzania needs a TIN — even "
  "if they only sell to community groups. Sales to VICOBAs are still business income "
  "subject to income tax. A TIN is the basic requirement for doing formal business in "
  "Tanzania. Registration is free and takes 1-3 days.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA registration requirement update",
  "rural_conversational", "standard"),

p("tier1a_compliance_costs_173_20260609","compliance_costs",
  "Tofauti kati ya usajili wa biashara (BRELA) na leseni ya biashara (LGA) ni nini?",
  "Hizi ni hatua mbili tofauti za kufuata sheria. Usajili wa BRELA unasajili JINA au "
  "MUUNDO wa biashara yako (kampuni au biashara ya mtu mmoja) kwenye rejista ya "
  "kitaifa — ni mara moja tu. Leseni ya biashara ya LGA inakupa RUHUSA ya kufanya "
  "shughuli za biashara katika eneo maalum la kijiografia la LGA — inarudiwa kila "
  "mwaka. Unahitaji zote mbili: BRELA kwa uhalali wa kisheria wa biashara yako, "
  "LGA kwa ruhusa ya eneo.",
  "What is the difference between business registration (BRELA) and a business licence (LGA)?",
  "These are two separate compliance steps. BRELA registration registers the NAME or "
  "STRUCTURE of your business (company or sole proprietorship) in the national registry "
  "— done once. An LGA business licence gives you PERMISSION to conduct business "
  "activities in a specific geographic area of the LGA — renewed annually. You need "
  "both: BRELA for the legal existence of your business, LGA for area permission.",
  BRELA, BRELA_N, GP, "2025-07-01", ANN, "Business registration or licensing framework update",
  "business_market", "disambiguation"),

p("tier1a_compliance_costs_174_20260609","compliance_costs",
  "Mwajiri anahitaji kujua gharama za uzingatiaji (compliance) za kila mfanyakazi "
  "mpya anayeajiri Tanzania — ni kiasi gani kwa mfanyakazi mmoja?",
  "Gharama za uzingatiaji kwa kila mfanyakazi mpya Tanzania (mbali na mshahara) ni: "
  "NSSF mwajiri: asilimia 10 ya mshahara wa jumla kila mwezi (si ada ya usajili), "
  "WCF: asilimia 0.5 ya mshahara wa mwaka, SDL (ikiwa wafanyakazi 10+): asilimia 3.5 "
  "ya mshahara wa jumla kila mwezi. Kwa mfano, mfanyakazi wa TZS 500,000/mwezi: "
  "NSSF TZS 50,000/mwezi + WCF TZS 2,500/mwezi + SDL TZS 17,500/mwezi (ikiwa ≥10) "
  "= TZS 70,000/mwezi ya ziada ya uzingatiaji.",
  "What compliance costs per new employee does an employer need to know in Tanzania?",
  "Compliance costs per new Tanzania employee (beyond salary): "
  "NSSF employer: 10% of gross monthly wage (not a registration fee), "
  "WCF: 0.5% of annual wage, SDL (if 10+ employees): 3.5% of gross monthly wage. "
  "For example, an employee on TZS 500,000/month: NSSF TZS 50,000/month + WCF "
  "TZS 2,500/month + SDL TZS 17,500/month (if ≥10) = TZS 70,000/month extra "
  "compliance cost.",
  NSSF, NSSF_N, GP, "2025-07-01", ANN, "NSSF, WCF, SDL rate update",
  "business_market", "standard"),

p("tier1a_compliance_costs_175_20260609","compliance_costs",
  "Biashara ndogo inayofanya mauzo ya TZS 20M kwa mwaka inahitaji kusajili VAT Tanzania?",
  "Hapana. Kizingiti cha kusajili VAT Tanzania ni TZS 200,000,000 (TZS 200M) kwa "
  "miezi 12, au TZS 100,000,000 (TZS 100M) kwa miezi 6. Biashara yenye mauzo ya "
  "TZS 20M kwa mwaka iko mbali sana chini ya kizingiti hiki na HAIHITAJIKI kusajili "
  "VAT. Hata hivyo, inaweza kusajili hiari (voluntary registration) ikiwa inataka "
  "kudai VAT kwenye manunuzi ya biashara.",
  "Does a small business making TZS 20M annual sales need to register for VAT in Tanzania?",
  "No. The VAT registration threshold in Tanzania is TZS 200,000,000 (TZS 200M) per "
  "12 months, or TZS 100,000,000 (TZS 100M) per 6 months. A business with TZS 20M "
  "annual sales is far below this threshold and is NOT required to register for VAT. "
  "However, it can voluntarily register if it wishes to reclaim VAT on business "
  "purchases.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act VAT threshold update",
  "rural_conversational", "standard"),

p("tier1a_compliance_costs_176_20260609","compliance_costs",
  "Je, biashara inaweza kupata msamaha wa kodi kwa kuwa biashara ya wanawake Tanzania?",
  "Sheria za kodi za Tanzania hazitoi msamaha wa jumla wa kodi tu kwa sababu biashara "
  "inamilikiwa na mwanamke. Hata hivyo, kuna vitu vinavyosaidia biashara za wanawake: "
  "NMB Bank na DFI pakiti (IFC/BII) zinasaidia biashara za wanawake kwa mikopo, "
  "baadhi ya programu za maendeleo zinaweza kutoa ruzuku zisizo za kodi. Uzingatiaji "
  "wa kodi bado unahitajika kwa biashara zote.",
  "Can a business get tax exemption for being a women-owned business in Tanzania?",
  "Tanzania tax laws do not provide a general tax exemption simply because a business "
  "is women-owned. However, there are things that help women-owned businesses: NMB "
  "Bank and DFI packages (IFC/BII) support women's businesses with loans, some "
  "development programmes may offer non-tax grants. Tax compliance is still required "
  "for all businesses.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax incentive policy update",
  "rural_conversational", "standard"),

p("tier1a_compliance_costs_177_20260609","compliance_costs",
  "Rekodi za biashara Tanzania zinapaswa kuhifadhiwa kwa miaka mingapi?",
  "TRA inaitaji wafanyabiashara Tanzania kuhifadhi rekodi za kodi (vitabu vya hesabu, "
  "risiti, ankara, taarifa za benki) kwa miaka MITANO (5) kutoka tarehe ya kuwasilisha "
  "tamko la kodi husika. Hii ni muhimu kwa ukaguzi wowote wa TRA. BRELA inaweza "
  "pia kuhitaji hifadhi ya nyaraka za kampuni kwa muda mrefu zaidi. Hifadhi rekodi "
  "zako kwa usalama — kidijitali na nakala za karatasi.",
  "For how many years must Tanzania business records be kept?",
  "TRA requires Tanzania businesses to keep tax records (account books, receipts, "
  "invoices, bank statements) for FIVE (5) years from the filing date of the relevant "
  "tax return. This is critical for any TRA audit. BRELA may also require retention "
  "of company documents for longer periods. Keep your records securely — both "
  "digitally and as paper copies.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Administration Act record-keeping update",
  "formal", "standard"),

p("tier1a_compliance_costs_178_20260609","compliance_costs",
  "Biashara inaweza kuomba muda wa ziada wa kuwasilisha tamko la kodi Tanzania?",
  "Ndiyo. Mwajiriwa wa kodi (taxpayer) anaweza kuomba ugani (extension) wa muda wa "
  "kuwasilisha tamko la kodi kwa TRA. Ombi linapaswa kuwasilishwa KABLA ya tarehe ya "
  "mwisho ya asili. TRA inaweza kukubaliana au kukataa ombi. Riba ya kuchelewa "
  "inaweza bado kuendelea hata wakati wa ugani ulioombwa. Ugani si uhakika — omba "
  "mapema na toa sababu za msingi.",
  "Can a business apply for an extension to file a tax return in Tanzania?",
  "Yes. A taxpayer can apply for an extension of time to file a tax return with TRA. "
  "The application must be submitted BEFORE the original deadline. TRA may agree or "
  "refuse the application. Late interest may still accrue even during a requested "
  "extension. An extension is not guaranteed — apply early and provide solid reasons.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Administration Act update",
  "business_market", "standard"),

p("tier1a_compliance_costs_179_20260609","compliance_costs",
  "Je, biashara ya mkulima mdogo wa Tanzania inahitaji TIN na kodi?",
  "Mkulima mdogo anayeuza mazao yake kwa matumizi ya nyumbani au soko la karibu "
  "kwa kiwango kidogo anaweza kutolazimishwa TIN na kodi rasmi. Hata hivyo, mkulima "
  "ambaye ana biashara ya kilimo ya kibiashara — anauza kwa kampuni, sokoni, au "
  "nje ya nchi — analazimika kufuata sheria za kodi. Mstari si wazi kabisa. Kwa "
  "maswali ya mahususi, wasiliana na TRA au mshauri wa kodi wa kilimo.",
  "Does a small-scale Tanzanian farmer need a TIN and pay taxes?",
  "A small farmer selling their crops for home use or a nearby market at a small "
  "scale may not be required to have a TIN and formal taxation. However, a farmer "
  "with a commercial farming business — selling to companies, at market, or for "
  "export — is required to comply with tax laws. The line is not entirely clear. "
  "For specific questions, contact TRA or an agricultural tax adviser.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act agricultural exemption update",
  "rural_conversational", "standard"),

p("tier1a_compliance_costs_180_20260609","compliance_costs",
  "Biashara inayopokea pesa kupitia M-Pesa au mobile money tu inatozwa kodi Tanzania?",
  "Ndiyo. Njia ya kupokea malipo (M-Pesa, benki, au pesa taslimu) HAIATHIRI wajibu "
  "wa kodi. Mauzo yoyote ya biashara yanayolipwa kupitia mobile money bado ni mapato "
  "ya biashara yanayolazimishwa kwa kodi ya mapato na VAT (ikiwa imezidi kizingiti). "
  "Mnamo Septemba 2025, TRA ilianza kutazamia uzingatiaji wa VAT kwenye mauzo ya "
  "kidijitali. Hifadhi rekodi za miamala yote ya mobile money kwa kodi.",
  "A business receiving money only via M-Pesa or mobile money is taxed in Tanzania?",
  "Yes. The method of receiving payment (M-Pesa, bank, or cash) does NOT affect the "
  "tax obligation. Any business sales paid via mobile money are still business income "
  "subject to income tax and VAT (if threshold exceeded). As of September 2025, TRA "
  "has increased focus on VAT compliance for digital sales. Keep records of all mobile "
  "money transactions for tax purposes.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA digital economy enforcement update",
  "rural_conversational", "adversarial"),

p("tier1a_compliance_costs_181_20260609","compliance_costs",
  "Biashara ndogo Tanzania inapaswa kutenganisha akaunti ya biashara na akaunti ya "
  "mwenye biashara — serikali inaweza kukagua akaunti yake binafsi?",
  "TRA inaweza kuomba mahakama ruhusa ya kukagua akaunti za benki za mshukiwa wa "
  "ukwepaji wa kodi — ikiwa ni pamoja na akaunti za kibinafsi zikionekana kuwa "
  "biashara inafanya shughuli kupitia akaunti binafsi. Hii ni sababu nzuri zaidi "
  "ya kuhifadhi biashara na fedha za kibinafsi tofauti. Akaunti tofauti za benki "
  "zinazuia uchunguzi usiohitajika na zinahifadhi faragha ya kibinafsi.",
  "Should a small Tanzania business separate the business account from the owner's "
  "personal account — can the government audit the personal account?",
  "TRA can seek court authorisation to examine bank accounts of a tax evasion suspect "
  "— including personal accounts if the business appears to be operating through "
  "personal accounts. This is another strong reason to keep business and personal "
  "funds separate. Separate bank accounts prevent unnecessary scrutiny and protect "
  "personal privacy.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Administration Act audit power update",
  "business_market", "standard"),

p("tier1a_compliance_costs_182_20260609","compliance_costs",
  "Kampuni mpya inaweza kuanza kufanya biashara siku ile ile ya kusajiliwa BRELA?",
  "Kisheria, kampuni inaweza kuanza baadhi ya shughuli za maandalizi mara baada ya "
  "kusajiliwa BRELA. Hata hivyo, kwa biashara kamili ya kisheria, bado unahitaji: "
  "TIN (unaweza kuomba wakati huo huo na BRELA), leseni ya LGA kwa eneo lako (inachukua "
  "siku kadhaa hadi wiki), NSSF/WCF usajili ikiwa una wafanyakazi. Kuanza kupokea "
  "malipo ya biashara bila TIN au leseni ya LGA kunaweza kukuletea matatizo ya kisheria.",
  "Can a new company start doing business the same day it is registered at BRELA?",
  "Legally, a company can begin some preparatory activities immediately after BRELA "
  "registration. However, for full lawful business operation you still need: TIN (can "
  "be applied for simultaneously with BRELA), LGA licence for your area (takes several "
  "days to weeks), NSSF/WCF registration if you have employees. Starting to receive "
  "business payments without a TIN or LGA licence can create legal problems.",
  BRELA, BRELA_N, GP, "2025-07-01", ANN, "Business registration and licensing update",
  "business_market", "standard"),

p("tier1a_compliance_costs_183_20260609","compliance_costs",
  "Mtu anayefanya kazi mbili — mwajiriwa na mwenye biashara — ana wajibu wa "
  "kodi gani Tanzania?",
  "Mtu mwenye kipato cha vyanzo viwili (mshahara wa ajira + faida ya biashara) ana: "
  "(1) PAYE inayokatwa na mwajiri wake kwenye mshahara, (2) wajibu wa kuwasilisha "
  "tamko la kodi la mwaka ambalo linajumuisha kipato cha biashara pia, (3) kulipa "
  "kodi ya ziada ikiwa kipato cha biashara kinaongeza jumla ya kodi zaidi ya PAYE "
  "iliyokatwa. Biashara yake inahitaji TIN yake mwenyewe ikiwa ni kampuni, au "
  "TIN yake kwa biashara ya mtu mmoja.",
  "A person with two jobs — employed and business owner — what tax obligations apply "
  "in Tanzania?",
  "A person with two income sources (employment salary + business profit) has: "
  "(1) PAYE deducted by their employer on their salary, (2) an obligation to file "
  "an annual tax return that includes business income too, (3) pay additional tax "
  "if business income increases total tax above the PAYE already deducted. Their "
  "business needs its own TIN if it is a company, or their personal TIN for a "
  "sole proprietorship.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act PAYE or income tax update",
  "business_market", "standard"),

p("tier1a_compliance_costs_184_20260609","compliance_costs",
  "Kampuni inayolipa mshahara kwa pesa taslimu (bila akaunti ya benki) inaweza "
  "kulipa PAYE na NSSF kwa njia hiyo hiyo?",
  "Malipo ya PAYE na NSSF TRA yanafanywa kupitia mfumo wa PRN/benki au e-payment "
  "ya TRA — SI kwa pesa taslimu ofisini. Hata kama kampuni inalipa mishahara ya "
  "wafanyakazi kwa pesa taslimu, mwajiri bado analazimishwa kuwasilisha PAYE na "
  "NSSF kupitia njia rasmi za malipo za TRA na NSSF. Hifadhi rekodi za mishahara "
  "ya pesa taslimu kama ushahidi.",
  "Can a company that pays wages in cash (without bank accounts) also pay PAYE and "
  "NSSF the same way?",
  "PAYE and NSSF payments to TRA are made through the PRN/bank system or TRA "
  "e-payment — NOT by cash at the office. Even if a company pays employee wages "
  "in cash, the employer is still required to remit PAYE and NSSF through TRA's "
  "and NSSF's official payment channels. Keep records of cash wage payments as "
  "evidence.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA payment system update",
  "rural_conversational", "standard"),

p("tier1a_compliance_costs_185_20260609","compliance_costs",
  "Kuna uhusiano gani kati ya BRELA, TRA, OSHA, na NSSF — wanashiriki taarifa?",
  "Vyombo vya serikali vya Tanzania vina uhusiano wa kushirikiana taarifa unaoendelea "
  "kukua. TRA inashirikiana na BRELA — usajili wa kampuni BRELA mara nyingi "
  "unahusishwa na mfumo wa TIN moja kwa moja. TRA inaweza kupata taarifa za ajira "
  "kutoka NSSF ili kutathmini PAYE na SDL. OSHA na WCF wanaweza pia kushiriki "
  "taarifa na TRA. Hii inamaanisha biashara isiyofuata sheria moja inaweza "
  "kugunduliwa kupitia chombo kingine.",
  "What is the relationship between BRELA, TRA, OSHA, and NSSF — do they share information?",
  "Tanzania government agencies have a growing data-sharing relationship. TRA cooperates "
  "with BRELA — company registration at BRELA is often linked directly to the TIN "
  "system. TRA can obtain employment data from NSSF to assess PAYE and SDL. OSHA and "
  "WCF may also share data with TRA. This means a business that fails to comply with "
  "one agency can be discovered through another.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Inter-agency data sharing update",
  "formal", "standard"),

p("tier1a_compliance_costs_186_20260609","compliance_costs",
  "Biashara ya usafirishaji (bodaboda, daladala) inahitaji usajili wowote mbali "
  "na leseni ya udereva Tanzania?",
  "Ndiyo. Biashara ya usafirishaji Tanzania inahitaji: (1) leseni ya udereva binafsi, "
  "(2) usajili wa gari (SUMATRA/TANROADS), (3) TIN ya TRA kwa biashara, (4) leseni "
  "ya biashara ya LGA ikiwa una kikosi cha magari, (5) NSSF ikiwa una madereva "
  "waliofanywa waajiriwa (si wakusudia wa kujitegemea). Bodaboda anayefanya kazi "
  "kwa kujitegemea ana mahitaji tofauti kidogo na kampuni ya bodaboda iliyosajiliwa.",
  "Does a transport business (bodaboda, daladala) need any registration beyond a "
  "driving licence in Tanzania?",
  "Yes. A Tanzania transport business needs: (1) personal driving licence, (2) vehicle "
  "registration (SUMATRA/TANROADS), (3) TRA TIN for the business, (4) LGA business "
  "licence if running a fleet, (5) NSSF if drivers are formal employees (not "
  "independent contractors). A self-employed bodaboda rider has slightly different "
  "requirements from a registered bodaboda company.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Transport sector compliance update",
  "rural_conversational", "standard"),

p("tier1a_compliance_costs_187_20260609","compliance_costs",
  "Mwajiri anaweza kuomba mwajiriwa wake 'ajiandikishe mwenyewe NSSF' ili "
  "kuepuka wajibu wa mwajiri — je, inaruhusiwa?",
  "Hapana. NSSF ni WAJIBU WA MWAJIRI — si mwajiriwa. Mwajiriwa hawezi 'kusajili "
  "mwenyewe' badala ya mwajiri wake. Mwajiri ndiye anayepaswa: (1) kusajili kampuni "
  "kwa NSSF, (2) kusajili kila mfanyakazi, (3) kukata mchango wa mfanyakazi (10%), "
  "(4) kuongeza mchango wa mwajiri (10%), na (5) kuwasilisha jumla (20%) na NSSF "
  "kila mwezi. Mwajiri anayekataa kufanya hivi anakiuka Sheria ya NSSF.",
  "Can an employer ask their employee to 'register themselves with NSSF' to avoid "
  "the employer's obligations — is this permitted?",
  "No. NSSF is the EMPLOYER'S OBLIGATION — not the employee's. An employee cannot "
  "'self-register' on behalf of their employer. The employer must: (1) register "
  "the company with NSSF, (2) register each employee, (3) deduct the employee "
  "contribution (10%), (4) add the employer contribution (10%), and (5) remit "
  "the total (20%) to NSSF monthly. An employer who refuses to do this is in "
  "violation of the NSSF Act.",
  NSSF, NSSF_N, GP, "2025-07-01", ANN, "NSSF Act amendment",
  "business_market", "adversarial"),

p("tier1a_compliance_costs_188_20260609","compliance_costs",
  "Biashara inayofanya mauzo ya mara moja tu kwa mwaka (seasonal business) "
  "ina wajibu wa kodi wa kila mwezi Tanzania?",
  "Biashara ya msimu (seasonal) bado ina wajibu wa kodi wa kila mwezi ikiwa ina "
  "wafanyakazi: PAYE, NSSF, SDL (ikiwa ≥10) zinawasilishwa kila mwezi. Hata hivyo, "
  "kwa miezi ya biashara isipo na shughuli, PAYE na SDL ni sifuri ikiwa hakuna "
  "mshahara uliolipwa. Tamko la kodi la mwaka linawasilishwa mwaka mzima hata kama "
  "biashara ilifanya kazi miezi 3 tu. Mfumo wa TRA hautambui 'biashara ya msimu' "
  "kama aina maalum — sheria za kawaida zinatumika.",
  "A business that sells only once a year (seasonal business) — does it have monthly "
  "tax obligations in Tanzania?",
  "A seasonal business still has monthly tax obligations if it has employees: PAYE, "
  "NSSF, SDL (if ≥10) are submitted monthly. However, during months with no business "
  "activity, PAYE and SDL are zero if no wages were paid. An annual tax return is "
  "filed for the full year even if the business only operated for 3 months. TRA's "
  "system does not recognise 'seasonal business' as a special category — standard "
  "rules apply.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Administration Act update",
  "rural_conversational", "standard"),

p("tier1a_compliance_costs_189_20260609","compliance_costs",
  "Mtu anayefanya kazi nje ya nchi lakini bado ana biashara Tanzania ana wajibu "
  "gani wa kodi Tanzania?",
  "Hali inategemea ukazi wa kodi (tax residency). Ikiwa mtu amekaa nje ya Tanzania "
  "zaidi ya siku 183 kwa mwaka wa fedha, huenda asizingatiwe mkazi wa kodi wa "
  "Tanzania kwa kipato chake cha kigeni. Hata hivyo, biashara yake Tanzania bado "
  "inalipa kodi ya Tanzania kwenye mapato yanayotokana Tanzania. Anapaswa kupata "
  "ushauri maalum kutoka mwanasheria wa kodi wa kimataifa kwa hali yake.",
  "A person working abroad but still owning a business in Tanzania — what Tanzania "
  "tax obligations apply?",
  "The situation depends on tax residency. If a person has been outside Tanzania for "
  "more than 183 days in a tax year, they may not be considered a Tanzania tax resident "
  "for their foreign income. However, their Tanzania business still pays Tanzania tax "
  "on income arising in Tanzania. They should get specific advice from an international "
  "tax lawyer for their situation.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act residency rule update",
  "formal", "standard"),

p("tier1a_compliance_costs_190_20260609","compliance_costs",
  "Je, BRELA inaweza kufuta kampuni bila idhini ya wamiliki wake Tanzania?",
  "Ndiyo. BRELA inaweza kufuta kampuni kwenye rejista yake (administrative strike-off) "
  "ikiwa: (1) kampuni imeshindwa kuwasilisha annual return kwa miaka miwili au zaidi, "
  "(2) kuna ushahidi kwamba kampuni haifanyi tena shughuli. BRELA kawaida inatoa "
  "notisi kabla ya kufuta. Wamiliki wanaweza kupinga au kurudisha kampuni ikiwa kufutwa "
  "kulifanywa kwa kosa. Kampuni iliyofutwa na BRELA haina nguvu ya kisheria.",
  "Can BRELA deregister a company without the owners' consent in Tanzania?",
  "Yes. BRELA can administratively strike off a company from its register if: (1) the "
  "company has failed to file annual returns for two or more years, (2) there is "
  "evidence the company is no longer operating. BRELA usually gives notice before "
  "striking off. Owners can object or restore the company if the strike-off was done "
  "in error. A company struck off by BRELA has no legal force.",
  BRELA, BRELA_N, GP, "2025-07-01", ANN, "Companies Act or BRELA administrative policy update",
  "formal", "standard"),

p("tier1a_compliance_costs_191_20260609","compliance_costs",
  "Kampuni ya Tanzania yenye makao makuu Mombasa Kenya — inaweza kusajiliwa "
  "Tanzania bila tawi (branch) rasmi?",
  "Kampuni ya kigeni inayofanya shughuli Tanzania inahitaji kusajili tawi lake "
  "(foreign branch) kwa BRELA Tanzania. Kampuni ya Kenya inayouza bidhaa au kutoa "
  "huduma Tanzania kwa njia ya kawaida ya biashara lazima isajili tawi la Tanzania. "
  "Kampuni isiyosajili tawi inafanya shughuli nje ya sheria na inaweza kusababisha "
  "matatizo ya kodi na kisheria kwa Tanzania.",
  "A Tanzania company with headquarters in Mombasa Kenya — can it operate in "
  "Tanzania without a formal branch?",
  "A foreign company conducting business in Tanzania needs to register its branch "
  "(foreign branch) with BRELA Tanzania. A Kenya company regularly selling goods or "
  "providing services in Tanzania must register a Tanzania branch. A company that does "
  "not register a branch is operating outside the law and can create tax and legal "
  "problems in Tanzania.",
  BRELA, BRELA_N, GP, "2025-07-01", ANN, "Companies Act or foreign branch registration update",
  "formal", "standard"),

p("tier1a_compliance_costs_192_20260609","compliance_costs",
  "Biashara ndogo Tanzania inaweza kutumia mfumo wa 'lump sum tax' badala ya "
  "kuhesabu kodi halisi ya mapato?",
  "Tanzania haina mfumo rasmi wa 'lump sum tax' kwa biashara ndogo kwa ujumla. Hata "
  "hivyo, kuna mfumo wa kodi ndogo ya mauzo (minimum turnover tax) ya asilimia 1 kwa "
  "biashara zisizofanya faida. Baadhi ya LGA zinaweza kuwa na mifumo rahisi ya kodi "
  "ya biashara ndogo (presumptive tax) lakini hizi ni za eneo, si za TRA ya kitaifa. "
  "Angalia TRA na LGA yako kwa chaguo zilizopo.",
  "Can a small Tanzania business use a 'lump sum tax' system instead of calculating "
  "actual income tax?",
  "Tanzania does not have a general formal 'lump sum tax' system for small businesses. "
  "However, there is a minimum turnover tax system at 1% for businesses that do not "
  "make a profit. Some LGAs may have simplified small business tax systems (presumptive "
  "tax) but these are local, not national TRA. Check with TRA and your LGA for "
  "available options.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax policy for small businesses update",
  "business_market", "standard"),

p("tier1a_compliance_costs_193_20260609","compliance_costs",
  "Wafanyabiashara wa mpakani (cross-border traders) Tunduma wana mahitaji "
  "gani ya uzingatiaji Tanzania?",
  "Mfanyabiashara wa mpakani Tunduma-Nakonde anahitaji kuzingatia: (1) TIN ya TRA "
  "kwa biashara yake Tanzania, (2) Hati za forodha (customs documentation) za "
  "TANZRA/TRA — ikiwa ni pamoja na invoice ya biashara, packing list, na hati ya "
  "asili ya bidhaa, (3) EAC STR (Simplified Trade Regime) inaweza kutumika ikiwa "
  "bidhaa ziko kwenye orodha ya kawaida na kiasi ni chini ya USD 2,000, (4) Leseni "
  "ya biashara ya LGA ya Tunduma. Angalia KRA/ZRA kwa biashara ya upande wa Kenya/Zambia.",
  "What compliance requirements do cross-border traders at Tunduma have in Tanzania?",
  "A Tunduma-Nakonde cross-border trader needs to comply with: (1) TRA TIN for their "
  "Tanzania business, (2) customs documentation for TANZRA/TRA — including commercial "
  "invoice, packing list, and certificate of origin, (3) EAC STR (Simplified Trade "
  "Regime) may apply if goods are on the common list and amount is below USD 2,000, "
  "(4) Tunduma LGA business licence. Check KRA/ZRA for Kenya/Zambia side requirements.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "EAC STR or customs procedure update",
  "rural_conversational", "standard"),

p("tier1a_compliance_costs_194_20260609","compliance_costs",
  "Biashara ya Tanzania inayofilisiwa (insolvent) ina utaratibu gani wa kufuta "
  "na wadai wanafanyaje?",
  "Ufilisi (insolvency/liquidation) wa kampuni Tanzania unafuata Sheria ya Makampuni. "
  "Kuna: (1) ufilisi wa hiari (voluntary liquidation) ukiamuliwa na wanaohisa, (2) "
  "ufilisi wa kulazimishwa (compulsory liquidation) ukiamriwa na mahakama kwa ombi "
  "la mdai. Msimamizi wa mali (liquidator) anachaguliwa, anauza mali, analipa wadai "
  "kwa mpangilio wa kipaumbele cha kisheria, na hatimaye kampuni inafutwa. TRA ni "
  "mmoja wa wadai wa kipaumbele cha juu.",
  "What is the procedure for a Tanzania business going insolvent and what do creditors do?",
  "Corporate insolvency/liquidation in Tanzania follows the Companies Act. There is: "
  "(1) voluntary liquidation decided by shareholders, (2) compulsory liquidation "
  "ordered by court on creditor application. A liquidator is appointed, sells assets, "
  "pays creditors in the legally prescribed priority order, and the company is finally "
  "struck off. TRA is one of the high-priority creditors.",
  BRELA, BRELA_N, GP, "2025-07-01", ANN, "Companies Act or insolvency law update",
  "formal", "standard"),

p("tier1a_compliance_costs_195_20260609","compliance_costs",
  "Mwajiri mpya anahitaji kusajili wafanyakazi wake wa zamani (waliokuwepo kabla "
  "ya kuanzishwa kwake) NSSF?",
  "Wakati biashara mpya inachukua (acquires) biashara nyingine na wafanyakazi wake, "
  "wajibu wa NSSF unategemea muundo wa muamala. Ikiwa ni ununuzi wa biashara (asset "
  "purchase) na wafanyakazi wanaajiriwa upya, mwajiri mpya anasajili wafanyakazi "
  "wake upya na NSSF. Ikiwa ni ununuzi wa hisa (share purchase), kampuni inabaki "
  "sawa na NSSF na wafanyakazi wake — mwajiri mpya (wanaohisa) wanachukua majukumu "
  "ya NSSF ya kampuni.",
  "Does a new employer need to register employees who were there before their acquisition "
  "with NSSF?",
  "When a new business acquires another business and its employees, the NSSF obligation "
  "depends on the transaction structure. If it is an asset purchase with employees "
  "re-hired, the new employer re-registers the employees with NSSF. If it is a share "
  "purchase, the company remains the same with NSSF and its employees — the new "
  "employer (shareholders) takes over the company's NSSF obligations.",
  NSSF, NSSF_N, GP, "2025-07-01", ANN, "NSSF Act or employment transfer law update",
  "formal", "standard"),

p("tier1a_compliance_costs_196_20260609","compliance_costs",
  "Ushauri wa bure wa kodi unapatikana wapi Tanzania kwa biashara ndogo?",
  "Rasilimali za bure za kodi kwa biashara ndogo Tanzania ni: (1) Kituo cha Huduma "
  "za TRA (TRA Service Centre) — maofisa wa TRA wanaweza kutoa mwongozo wa msingi wa "
  "uzingatiaji bila malipo, (2) Tovuti ya TRA (tra.go.tz) ina miongozo na maswali "
  "ya kawaida, (3) Vituo vya Biashara na SME vya serikali kama SIDO Tanzania. "
  "Hata hivyo, kwa maswali magumu ya kodi, mshauri wa kodi aliyesajiliwa au "
  "mhasibu aliyeidhinishwa anashauriwa.",
  "Where can free tax advice be found in Tanzania for small businesses?",
  "Free tax resources for small Tanzania businesses include: (1) TRA Service Centre "
  "— TRA officers can provide basic compliance guidance at no charge, (2) TRA website "
  "(tra.go.tz) has guides and FAQs, (3) Government SME centres like SIDO Tanzania. "
  "However, for complex tax questions, a registered tax adviser or certified "
  "accountant is recommended.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA service centre update",
  "rural_conversational", "standard"),

p("tier1a_compliance_costs_197_20260609","compliance_costs",
  "Wafanyabiashara wanaofanya biashara nyumbani (home-based business) Tanzania "
  "bado wanahitaji leseni ya LGA?",
  "Ndiyo kwa ujumla. Biashara inayofanywa nyumbani bado inachukuliwa kama biashara "
  "ya kibiashara inayohitaji leseni ya LGA ikiwa inafanya shughuli za kibiashara za "
  "mara kwa mara. Ukweli kwamba biashara inafanywa nyumbani haubadilishi wajibu wa "
  "kisheria wa biashara. Angalia LGA yako kwa taratibu maalum za leseni ya biashara "
  "ya nyumbani — baadhi ya LGA zina kategoria maalum ya bei nafuu.",
  "Do home-based business operators in Tanzania still need an LGA licence?",
  "Yes generally. A home-based business is still considered a commercial business "
  "requiring an LGA licence if it conducts regular commercial activities. The fact "
  "that the business operates from home does not change business legal obligations. "
  "Check your LGA for specific home-based business licence procedures — some LGAs "
  "have special lower-cost categories.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "LGA licensing update",
  "rural_conversational", "standard"),

p("tier1a_compliance_costs_198_20260609","compliance_costs",
  "Mnunuzi wa biashara (buyer of a going concern) anachukua madeni ya kodi ya "
  "muuzaji Tanzania?",
  "Ikiwa mnunuzi ananunua BIASHARA (going concern) au hisa za kampuni — anaweza "
  "kuchukua madeni ya kodi ya zamani ya muuzaji ikiwa muamala umefanywa vibaya. "
  "Mnunuzi LAZIMA: (1) omba uthibitisho wa TRA wa kukosekana kwa madeni ya kodi "
  "kabla ya kununua, (2) fanya ukaguzi wa kina (due diligence) wa uzingatiaji wa "
  "kodi, (3) pangia mkataba wa mauzo unaomba mnunuzi awe na dhamana dhidi ya "
  "madeni ya kodi ya kabla ya mauzo. Kutofanya hivyo kunaweza kukufanya ulipie "
  "madeni ya kodi ya mmiliki wa zamani.",
  "Does a buyer of a business (going concern) take on the seller's tax debts in Tanzania?",
  "If a buyer purchases a BUSINESS (going concern) or company shares — they may "
  "inherit the seller's historical tax debts if the transaction is done poorly. "
  "The buyer MUST: (1) request a TRA tax clearance certificate showing no outstanding "
  "debts before buying, (2) conduct thorough tax compliance due diligence, (3) structure "
  "the sale contract to indemnify the buyer against pre-sale tax debts. Failing to "
  "do so can result in paying the previous owner's tax debts.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Administration Act or company acquisition update",
  "formal", "adversarial"),

p("tier1a_compliance_costs_199_20260609","compliance_costs",
  "Biashara ya Tanzania iliyo kwenye eneo la EPZ (Export Processing Zone) ina "
  "msamaha wa kodi gani?",
  "Kampuni zilizo kwenye EPZ (Export Processing Zone) Tanzania zinaweza kupata vivutio "
  "maalum vya kodi kutoka EPZA (Export Processing Zones Authority): msamaha wa kodi "
  "ya kampuni kwa miaka 10 ya kwanza, msamaha wa VAT na ushuru wa forodha kwenye "
  "vifaa vya uzalishaji, na vivutio vingine. Vivutio hivi ni vya kipekee kwa EPZ — "
  "HAVIHUSU biashara za nje ya EPZ. Biashara lazima isajiliwe rasmi na EPZA kupata "
  "vivutio hivi.",
  "What tax exemptions does a Tanzania business in an EPZ (Export Processing Zone) have?",
  "Companies in Tanzania's EPZ (Export Processing Zone) may receive special tax "
  "incentives from EPZA (Export Processing Zones Authority): 10-year corporate tax "
  "holiday, VAT and customs duty exemption on production equipment, and other "
  "incentives. These incentives are unique to EPZ — they DO NOT apply to businesses "
  "outside EPZ. A business must be formally registered with EPZA to access these "
  "incentives.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "EPZA incentives or Finance Act update",
  "formal", "standard"),

p("tier1a_compliance_costs_200_20260609","compliance_costs",
  "Muhtasari wa uzingatiaji wa msingi wa biashara ndogo Tanzania — hatua 10 za lazima ni zipi?",
  "Hatua 10 za msingi za uzingatiaji kwa biashara ndogo Tanzania: "
  "(1) Sajili jina la biashara au kampuni BRELA, "
  "(2) Pata TIN ya TRA (bure), "
  "(3) Omba leseni ya biashara ya LGA, "
  "(4) Sajili NSSF ikiwa una wafanyakazi, "
  "(5) Sajili WCF ikiwa una wafanyakazi, "
  "(6) Sajili OSHA ikiwa una wafanyakazi 10+, "
  "(7) Angalia kama unahitaji EFD (ikiwa VAT au TRA imeamuru), "
  "(8) Sajili VAT ikiwa mauzo yanazidi TZS 200M/mwaka, "
  "(9) Wasilisha tamko la kodi la mwaka kwa TRA, "
  "(10) Huisha leseni ya LGA kila mwaka (tarehe 31 Machi).",
  "Summary of essential small business compliance in Tanzania — what are the 10 mandatory steps?",
  "10 essential compliance steps for a small Tanzania business: "
  "(1) Register business name or company at BRELA, "
  "(2) Get TIN from TRA (free), "
  "(3) Apply for LGA business licence, "
  "(4) Register with NSSF if you have employees, "
  "(5) Register with WCF if you have employees, "
  "(6) Register with OSHA if you have 10+ employees, "
  "(7) Check if you need an EFD (if VAT-registered or TRA has directed), "
  "(8) Register for VAT if turnover exceeds TZS 200M/year, "
  "(9) File annual tax return with TRA, "
  "(10) Renew LGA licence annually (by 31 March).",
  BRELA, BRELA_N, GP, "2025-07-01", ANN, "Registration or licensing requirement update",
  "rural_conversational", "standard"),

]

written = 0
with open(OUT, "a", encoding="utf-8") as f:
    for pr in pairs:
        f.write(json.dumps(pr, ensure_ascii=False) + "\n")
        written += 1

total = sum(1 for _ in open(OUT, encoding="utf-8") if _.strip())
print(f"Part 4: wrote {written} pairs to {OUT}")
print(f"Total in file: {total}")
