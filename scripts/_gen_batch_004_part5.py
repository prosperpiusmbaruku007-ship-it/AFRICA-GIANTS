#!/usr/bin/env python3
"""batch_004 part 5 — WCF (10 more, 021-030) + BRELA deep (40, 001-040) = 50 pairs"""
import json, os

OUT = "datasets/tier1a/raw_sources/raw_pairs_batch_004.jsonl"
D = "2026-06-09"
TRA = "https://www.tra.go.tz"
TRA_N = "TRA — Tanzania Revenue Authority"
BRELA_URL = "https://www.brela.go.tz"
BRELA_N = "BRELA — Business Registrations and Licensing Agency"
ML = "https://www.mlywf.go.tz"
ML_N = "Ministry of Labour, Youth, Women and Special Groups"
TANZLII = "https://www.tanzlii.org"
TANZLII_N = "TanzLII — Tanzania Legal Information Institute"
GP = "government_portal"
OG = "official_gazette"
EVT = "event_triggered"
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
# WCF COMPLIANCE — pairs 021-030 (10 more)
# =====================================================================

p("tier1a_wcf_021_20260609","wcf_compliance",
  "Je, WCF inamaliza kulipia mfanyakazi baada ya mwaka mmoja wa ulemavu?",
  "Hapana. WCF inaendelea kulipia mfanyakazi mwenye ulemavu wa kudumu kwa muda "
  "wote wa ulemavu wake kulingana na hali ya tathmini ya daktari na sheria. "
  "Manufaa ya ulemavu wa kudumu yanaweza kuendelea kwa muda mrefu. Muda wa kulipa "
  "unategemea kiwango cha ulemavu kilichothibitishwa na daktari wa WCF.",
  "Does WCF stop paying an employee after one year of disability?",
  "No. WCF continues to pay an employee with permanent disability for the full period "
  "of their disability according to the medical assessment and the law. Permanent "
  "disability benefits can continue for a long period. The payment duration depends "
  "on the degree of disability certified by the WCF medical officer.",
  ML, ML_N, GP, "2008-01-01", ST, "Workers Compensation Act amendment",
  "formal", "standard"),

p("tier1a_wcf_022_20260609","wcf_compliance",
  "Mwajiri analazimika kutoa ripoti ya ajali kwa WCF kwa fomu gani?",
  "Mwajiri analazimika kuwasilisha ripoti ya ajali kwa WCF ukitumia fomu rasmi za "
  "WCF. Fomu hizi zinapatikana kwenye ofisi za WCF au tovuti. Ripoti inajumuisha: "
  "tarehe na hali ya ajali, maelezo ya majeraha, na hatua zilizochukuliwa. Kuwasilisha "
  "ndani ya siku 30 ni lazima.",
  "What form must an employer use to submit an accident report to WCF?",
  "The employer must submit an accident report using WCF's official forms, available "
  "at WCF offices or their website. The report includes: date and circumstances of the "
  "accident, description of injuries, and steps taken. Submission within 30 days is "
  "mandatory.",
  ML, ML_N, GP, "2008-01-01", ST, "Workers Compensation Act amendment",
  "business_market", "standard"),

p("tier1a_wcf_023_20260609","wcf_compliance",
  "WCF inamlipa mfanyakazi moja kwa moja au kupitia mwajiri?",
  "WCF inalipa mfanyakazi MOJA KWA MOJA baada ya madai kukubaliwa — si kupitia "
  "mwajiri. Hii inazuia mwajiri kushikilia au kupunguza malipo ya fidia. "
  "Mwajiri ana jukumu la kuripoti na kufanya uchunguzi, lakini malipo ya fidia "
  "yanakuja moja kwa moja kutoka WCF.",
  "Does WCF pay the worker directly or through the employer?",
  "WCF pays the worker DIRECTLY after claims are approved — not through the employer. "
  "This prevents the employer from withholding or reducing compensation payments. "
  "The employer's role is reporting and investigation, but compensation payments "
  "come directly from WCF.",
  ML, ML_N, GP, "2008-01-01", ST, "Workers Compensation Act amendment",
  "rural_conversational", "standard"),

p("tier1a_wcf_024_20260609","wcf_compliance",
  "Mchango wa WCF wa asilimia 0.5 unahesabiwa kwa mshahara wa msingi tu au mshahara wote?",
  "Mchango wa WCF wa asilimia 0.5 unahesabiwa kwa MSHAHARA WOTE (gross emoluments) — "
  "si mshahara wa msingi tu. Mshahara wote unajumuisha mshahara wa msingi, posho, "
  "bonasi, na malipo mengine ya mwajiri. Hii ni sawa na msingi wa NSSF.",
  "Is the 0.5% WCF contribution calculated on basic salary only or total wages?",
  "The 0.5% WCF contribution is calculated on TOTAL WAGES (gross emoluments) — not "
  "just basic salary. Total wages include basic salary, allowances, bonuses, and other "
  "employer payments. This is the same basis as NSSF.",
  ML, ML_N, GP, "2008-01-01", ANN, "Workers Compensation Act amendment",
  "formal", "standard"),

p("tier1a_wcf_025_20260609","wcf_compliance",
  "WCF ya asilimia 0.5 inakatwa kutoka mshahara wa mfanyakazi kila mwezi — je, ni sahihi?",
  "Hapana. WCF ya asilimia 0.5 HAIJATOLEWA kutoka mshahara wa mfanyakazi. Ni mchango "
  "wa MWAJIRI peke yake ambao unalipwa kutoka pochi ya mwajiri — si kutoka kwa mfanyakazi. "
  "Mfanyakazi hapotezi chochote kwenye mshahara wake kutokana na WCF.",
  "The 0.5% WCF is deducted from the employee's monthly salary — is this correct?",
  "No. The 0.5% WCF is NOT deducted from the employee's salary. It is the EMPLOYER'S "
  "contribution paid entirely from the employer's own funds — not from the employee. "
  "The employee loses nothing from their salary due to WCF.",
  ML, ML_N, GP, "2008-01-01", ANN, "Workers Compensation Act amendment",
  "business_market", "adversarial"),

p("tier1a_wcf_026_20260609","wcf_compliance",
  "WCF inalipa gharama za matibabu zote bila kikomo — je, ni kweli?",
  "Si kweli kabisa. WCF inalipia gharama za matibabu zinazohusiana na jeraha la kazi, "
  "lakini kuna mipaka na masharti kulingana na sheria na miongozo ya WCF. Gharama "
  "zinazohusiana moja kwa moja na jeraha la kazi zinafunikwa; gharama za hali za "
  "awali za kiafya au matibabu yasiyohusiana hazifunikwi.",
  "WCF pays all medical costs without limit — is this true?",
  "Not entirely. WCF pays medical costs related to the work injury, but there are "
  "limits and conditions under the law and WCF guidelines. Costs directly related "
  "to the work injury are covered; costs for pre-existing conditions or unrelated "
  "treatment are not.",
  ML, ML_N, GP, "2008-01-01", ST, "Workers Compensation Act amendment",
  "formal", "standard"),

p("tier1a_wcf_027_20260609","wcf_compliance",
  "Jinsi ya kusajili biashara na WCF — hatua zipi?",
  "Hatua za kusajili na WCF: (1) nenda ofisi ya WCF au tovuti ya WCF, "
  "(2) jaza fomu ya usajili wa mwajiri, (3) wasilisha orodha ya wafanyakazi wote, "
  "(4) lipa ada ya usajili (kama inahitajika), na (5) pata nambari ya usajili ya WCF. "
  "Baada ya usajili, lipa mchango wa kila mwezi kwa wakati.",
  "How do you register a business with WCF — what are the steps?",
  "Steps to register with WCF: (1) visit a WCF office or WCF website, (2) complete "
  "the employer registration form, (3) submit a list of all employees, (4) pay the "
  "registration fee (if required), and (5) receive your WCF registration number. "
  "After registration, pay the monthly contribution on time.",
  ML, ML_N, GP, "2008-01-01", ANN, "WCF registration process update",
  "business_market", "standard"),

p("tier1a_wcf_028_20260609","wcf_compliance",
  "WCF na OSHA zinahusiana vipi?",
  "WCF na OSHA zinafanya kazi pamoja lakini kwa majukumu tofauti. OSHA inazuia "
  "ajali kwa kuhakikisha usalama kazini (inspections, improvement notices). WCF "
  "inalipa fidia baada ya ajali kutokea. Kwa ajali kubwa, mwajiri anaripoti kwa OSHA "
  "(masaa 24) na kwa WCF (siku 30). Kuzuia ajali kupitia OSHA kunasaidia kupunguza "
  "madai ya WCF.",
  "How do WCF and OSHA relate to each other?",
  "WCF and OSHA work together but with different roles. OSHA PREVENTS accidents by "
  "ensuring workplace safety (inspections, improvement notices). WCF COMPENSATES after "
  "an accident occurs. For serious accidents the employer reports to OSHA (24 hours) "
  "and to WCF (30 days). Preventing accidents through OSHA helps reduce WCF claims.",
  ML, ML_N, GP, "2008-01-01", ST, "Workers Compensation Act or OSHA amendment",
  "formal", "disambiguation"),

p("tier1a_wcf_029_20260609","wcf_compliance",
  "Mfanyakazi aliyeumia anaweza kudai WCF bila kumwambia mwajiri wake — je, ni kweli?",
  "Mfanyakazi analazimika kumwambia mwajiri wake kuhusu jeraha la kazi haraka iwezekanavyo. "
  "Mwajiri kisha ana wajibu wa kuripoti WCF. Hata hivyo, ikiwa mwajiri anakataa kuripoti, "
  "mfanyakazi anaweza kwenda WCF moja kwa moja. Kudumisha ushahidi wa jeraha na kuripoti "
  "mapema ni muhimu kwa mafanikio ya madai.",
  "Can an injured worker claim WCF without telling their employer — is this true?",
  "The worker should notify their employer of the work injury as soon as possible. "
  "The employer then has the obligation to report to WCF. However, if the employer "
  "refuses to report, the worker can approach WCF directly. Preserving evidence of "
  "the injury and reporting early is critical for a successful claim.",
  ML, ML_N, GP, "2008-01-01", ST, "Workers Compensation Act amendment",
  "rural_conversational", "standard"),

p("tier1a_wcf_030_20260609","wcf_compliance",
  "WCF inatumika kwa sekta ya kilimo — wakulima wanaolima shamba lao wenyewe wana haki?",
  "WCF inahusu WAAJIRI NA WAFANYAKAZI — yaani watu wanaofanya kazi kwa mtu mwingine. "
  "Mkulima anayemiliki na kulima shamba lake mwenyewe (self-employed) hana wajibu wa "
  "WCF na hana haki za WCF kama mfanyakazi. Hata hivyo, mkulima anayeajiri wafanyakazi "
  "wa kulima shamba lake analazimika kulipa WCF kwa wafanyakazi hao.",
  "Does WCF apply to agriculture — do farmers working their own land have rights?",
  "WCF relates to EMPLOYERS AND EMPLOYEES — people working for someone else. A farmer "
  "who owns and works their own land (self-employed) has no WCF obligation and no WCF "
  "rights as a worker. However, a farmer who employs workers on their land must pay "
  "WCF contributions for those workers.",
  ML, ML_N, GP, "2008-01-01", ST, "Workers Compensation Act amendment",
  "rural_conversational", "standard"),

# =====================================================================
# BRELA DEEP — pairs 001-040 (40 pairs)
# Source: brela.go.tz
# =====================================================================

p("tier1a_brela_deep_001_20260609","brela_registration",
  "BRELA ni nini na inashughulikia nini Tanzania?",
  "BRELA (Business Registrations and Licensing Agency) ni shirika la serikali "
  "linalosimamiwa na Wizara ya Viwanda na Biashara. Inashughulikia: usajili wa "
  "majina ya biashara, uanzishwaji wa kampuni, usajili wa kampuni za kigeni, "
  "uandishi wa hati muhimu za biashara, na utunzaji wa rejesta ya biashara Tanzania.",
  "What is BRELA and what does it handle in Tanzania?",
  "BRELA (Business Registrations and Licensing Agency) is a government agency under "
  "the Ministry of Industry and Trade. It handles: business name registration, company "
  "incorporation, foreign company registration, filing of key business documents, and "
  "maintenance of Tanzania's business registry.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "BRELA Act or fee schedule update",
  "business_market", "standard"),

p("tier1a_brela_deep_002_20260609","brela_registration",
  "Ninaweza kusajili jina la biashara (business name) bila kuunda kampuni?",
  "Ndiyo. Unaweza kusajili jina la biashara (sole proprietorship au partnership) "
  "bila kuunda kampuni ya kikomo cha dhima (limited company). Usajili wa jina la "
  "biashara unaruhusu kufanya biashara chini ya jina linalotambuliwa kisheria bila "
  "gharama za kuanzisha kampuni kamili.",
  "Can I register a business name without incorporating a company?",
  "Yes. You can register a business name (sole proprietorship or partnership) without "
  "incorporating a limited liability company. Business name registration allows trading "
  "under a legally recognised name without the cost of full company incorporation.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "BRELA fee schedule update",
  "business_market", "standard"),

p("tier1a_brela_deep_003_20260609","brela_registration",
  "Gharama ya kuhifadhi jina la kampuni (name reservation) ni kiasi gani?",
  "Gharama ya kuhifadhi jina la kampuni kwa BRELA ni karibu Shilingi 20,000 kwa "
  "kipindi cha siku 30. Wakati huu, jina lililohifadhiwa haliwezi kusajiliwa na "
  "mtu mwingine. Baada ya siku 30, inahitajika kuhifadhi upya au kuendelea na "
  "uanzishwaji wa kampuni.",
  "What is the cost of reserving a company name at BRELA?",
  "The cost of reserving a company name at BRELA is approximately TZS 20,000 for a "
  "30-day period. During this time the reserved name cannot be registered by anyone "
  "else. After 30 days you must re-reserve or proceed with company incorporation.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "BRELA fee schedule update",
  "business_market", "standard"),

p("tier1a_brela_deep_004_20260609","brela_registration",
  "Kampuni ya kikomo cha dhima ya Tanzania (local limited company) inaanzishwaje?",
  "Kuanzisha kampuni ya kikomo cha dhima ya Tanzania: (1) hifadhi jina kwenye BRELA, "
  "(2) andaa Memorandum of Association na Articles of Association, (3) wasilisha "
  "nyaraka na ada ya Shilingi 50,000 (kampuni ya ndani), (4) pata Cheti cha Uanzishwaji "
  "(Certificate of Incorporation), na (5) sajili kwa TRA kwa TIN na VAT kama inahitajika.",
  "How do you incorporate a local limited company in Tanzania?",
  "To incorporate a Tanzania limited company: (1) reserve a name at BRELA, (2) prepare "
  "a Memorandum of Association and Articles of Association, (3) submit documents and a "
  "fee of TZS 50,000 (domestic company), (4) receive the Certificate of Incorporation, "
  "and (5) register with TRA for TIN and VAT if required.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "BRELA fee or Companies Act update",
  "formal", "standard"),

p("tier1a_brela_deep_005_20260609","brela_registration",
  "Kampuni ya kigeni (foreign company) inaweza kusajiliwa Tanzania — je, mchakato ni gani?",
  "Ndiyo. Kampuni ya kigeni inaweza kusajiliwa Tanzania kama tawi (branch). Mchakato "
  "unajumuisha: kuwasilisha nyaraka za kampuni mama (Certificate of Incorporation, "
  "Memorandum and Articles of Association), kuwasilisha maombi ya BRELA, kulipa ada "
  "(karibu Shilingi 200,000+), na kupata Cheti cha Usajili wa Kampuni ya Kigeni. "
  "Pia inahitajika kupata hati za TRA, BRELA business permit, na leseni nyingine.",
  "Can a foreign company register in Tanzania — what is the process?",
  "Yes. A foreign company can register in Tanzania as a branch. The process includes: "
  "submitting parent company documents (Certificate of Incorporation, Memorandum and "
  "Articles), filing BRELA application, paying a fee (approximately TZS 200,000+), "
  "and receiving a Foreign Company Registration Certificate. TRA registration, BRELA "
  "business permit, and other licences are also required.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "BRELA fee or Companies Act update",
  "formal", "standard"),

p("tier1a_brela_deep_006_20260609","brela_registration",
  "Annual return ya kampuni inawasilishwa lini kwa BRELA?",
  "Annual return ya kampuni inawasilishwa kwa BRELA ndani ya siku 42 baada ya mkutano "
  "wa mwaka (AGM) au ndani ya siku 30 baada ya tarehe ya kumbukumbu ya uanzishwaji "
  "kwa kampuni zisizofanya AGM. Kutowasillisha kwa wakati kunasababisha faini na "
  "hatimaye kufutwa kwa kampuni kwenye rejesta.",
  "When is a company's annual return submitted to BRELA?",
  "A company annual return is submitted to BRELA within 42 days of the Annual General "
  "Meeting (AGM), or within 30 days of the incorporation anniversary date for companies "
  "that do not hold an AGM. Late filing results in penalties and eventually deregistration "
  "from the register.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "Companies Act or BRELA regulation update",
  "formal", "standard"),

p("tier1a_brela_deep_007_20260609","brela_registration",
  "Cheti cha utiifu (Certificate of Compliance / Form 23) kinatumika kwa nini?",
  "Cheti cha utiifu (Form 23) kinathibitisha kwamba kampuni ipo katika hali nzuri "
  "ya kisheria na imefuata mahitaji ya BRELA. Kinahitajika kwa shughuli nyingi kama: "
  "kufungua akaunti ya benki, kutuma zabuni za serikali, na mikataba ya aina fulani. "
  "MUHIMU: Cheti hiki kinathibitisha uandikishwaji tu — BRELA inashauriwa kwamba "
  "usahihi wa maelezo ndani ya hati za kampuni haujathibitishwa.",
  "What is a Certificate of Compliance (Form 23) used for?",
  "A Certificate of Compliance (Form 23) confirms that a company is in good legal "
  "standing and has met BRELA requirements. It is required for many activities such as: "
  "opening a bank account, submitting government tenders, and certain contracts. "
  "IMPORTANT: This certificate only confirms registration — BRELA advises that the "
  "accuracy of content in company documents has not been verified.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "BRELA regulation update",
  "formal", "standard"),

p("tier1a_brela_deep_008_20260609","brela_registration",
  "Tanzania inaweka kiwango cha chini cha mtaji wa kampuni (minimum share capital)?",
  "Hapana. Tanzania haina kiwango cha chini cha lazima cha mtaji wa hisa kwa kampuni "
  "za kikomo cha dhima. Kampuni inaweza kuanzishwa na mtaji mdogo tu — kwa mfano, "
  "hisa moja. Hata hivyo, benki na sekta fulani zinaweza kuwa na mahitaji yao ya "
  "mtaji wa chini kwa sababu za udhibiti.",
  "Does Tanzania set a minimum share capital for companies?",
  "No. Tanzania has no mandatory minimum share capital requirement for limited companies. "
  "A company can be incorporated with very little capital — for example, one share. "
  "However, banks and certain regulated sectors may have their own minimum capital "
  "requirements for regulatory purposes.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "Companies Act amendment",
  "formal", "standard"),

p("tier1a_brela_deep_009_20260609","brela_registration",
  "Kampuni ya Tanzania inaweza kubadilisha jina lake — mchakato ni gani?",
  "Ndiyo. Kampuni inaweza kubadilisha jina lake kwa: (1) kupita azimio la mkutano "
  "maalum wa wanahisa (special resolution), (2) kuwasilisha ombi la mabadiliko ya "
  "jina kwa BRELA pamoja na ada, (3) kupata Cheti kipya cha Uanzishwaji chenye jina "
  "jipya, na (4) kusasisha nyaraka zote, akaunti za benki, na hati za kisheria.",
  "Can a Tanzania company change its name — what is the process?",
  "Yes. A company can change its name by: (1) passing a special resolution at a "
  "special general meeting of shareholders, (2) submitting a name change application "
  "to BRELA with the fee, (3) receiving a new Certificate of Incorporation with the "
  "new name, and (4) updating all documents, bank accounts, and legal instruments.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "Companies Act amendment",
  "business_market", "standard"),

p("tier1a_brela_deep_010_20260609","brela_registration",
  "BRELA na TRA ni mashirika sawa — je, ni kweli?",
  "Hapana. BRELA (Business Registrations and Licensing Agency) na TRA (Tanzania Revenue "
  "Authority) ni mashirika tofauti yanayofanya kazi tofauti. BRELA inasajili kampuni "
  "na biashara. TRA inakusanya kodi. Kusajili na BRELA hakutoi TIN — lazima usajili "
  "kwa TRA tofauti kupata TIN.",
  "BRELA and TRA are the same organisation — is this true?",
  "No. BRELA (Business Registrations and Licensing Agency) and TRA (Tanzania Revenue "
  "Authority) are separate organisations with different functions. BRELA registers "
  "companies and businesses. TRA collects taxes. Registering with BRELA does not give "
  "you a TIN — you must register separately with TRA to obtain a TIN.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "BRELA or TRA Act update",
  "business_market", "disambiguation"),

p("tier1a_brela_deep_011_20260609","brela_registration",
  "Kampuni iliyosajiliwa BRELA lazima iwe na katibu wa kampuni (company secretary)?",
  "Kwa kampuni za UMMA (public companies), company secretary ni lazima. Kwa kampuni "
  "za BINAFSI (private limited companies) nchini Tanzania, mahitaji yanaweza kutofautiana "
  "kulingana na makubaliano ya ndani ya kampuni na sheria inayotumika. Kampuni nyingi "
  "za binafsi za Tanzania hazilazimu katibu wa kampuni lakini inashauriwa kuwa na "
  "mshauri wa kisheria.",
  "Does a BRELA-registered company need a company secretary?",
  "For PUBLIC companies a company secretary is mandatory. For PRIVATE limited companies "
  "in Tanzania requirements may vary depending on the company's internal arrangements "
  "and applicable law. Many Tanzanian private companies do not require a formal company "
  "secretary but having legal counsel is advisable.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "Companies Act amendment",
  "formal", "standard"),

p("tier1a_brela_deep_012_20260609","brela_registration",
  "Hisa za kampuni ya binafsi za Tanzania zinaweza kuuzwa vipi?",
  "Hisa za kampuni ya binafsi (private company) zinauzwa kwa idhini ya bodi ya "
  "wakurugenzi au kwa mujibu wa Articles of Association. Mara nyingi, wanahisa wengine "
  "wa kampuni wana haki ya kwanza ya kununua (pre-emption rights). Mauzi ya hisa "
  "yanabidi kusajiliwa na BRELA. Kampuni ya umma (public company) inaweza kuuza hisa "
  "kwa umma kupitia DSE (Dar es Salaam Stock Exchange).",
  "How can shares in a Tanzanian private company be transferred?",
  "Shares in a private company are transferred with the approval of the board of "
  "directors or as provided in the Articles of Association. Often other shareholders "
  "have pre-emption rights (first right to buy). Share transfers must be filed with "
  "BRELA. A public company can sell shares to the public through DSE "
  "(Dar es Salaam Stock Exchange).",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "Companies Act amendment",
  "formal", "standard"),

p("tier1a_brela_deep_013_20260609","brela_registration",
  "Kampuni inaweza kufutwa (struck off) kwenye rejesta ya BRELA ikiwa haitofanya nini?",
  "Kampuni inaweza kufutwa kwenye rejesta ya BRELA ikiwa: (1) haikuwasilisha annual "
  "return kwa miaka miwili au zaidi, (2) iliomba kufutwa mwenyewe (voluntary strike off), "
  "au (3) ikiwa kuna ushahidi kwamba haifanyi biashara. Kufutwa hakumaanisha kuondoa "
  "wajibu wote wa kisheria wa kampuni.",
  "A company can be struck off the BRELA register if it fails to do what?",
  "A company can be struck off the BRELA register if: (1) it has not filed annual "
  "returns for two or more years, (2) it applies for voluntary strike off, or (3) "
  "there is evidence that it is not carrying on business. Strike off does not remove "
  "all legal liabilities of the company.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "Companies Act amendment",
  "formal", "standard"),

p("tier1a_brela_deep_014_20260609","brela_registration",
  "Tofauti kati ya kufuta kampuni (dissolution) na kufutwa kwa rejesta (strike off) ni nini?",
  "Strike off ni hatua ya kiutawala inayofutwa kwa kampuni kwenye rejesta ya BRELA — "
  "mara nyingi kwa kushindwa kuwasilisha nyaraka. Dissolution (kuvunjwa) ni mchakato "
  "kamili wa kuhitimisha shughuli za kampuni, kulipa madeni, na kugawanya mali "
  "zilizobaki. Dissolution kawaida inafuata winding up (ufutaji wa shughuli za kampuni).",
  "What is the difference between company dissolution and being struck off the register?",
  "Strike off is an administrative action removing a company from the BRELA register — "
  "often for failure to file documents. Dissolution is the full process of winding up "
  "company affairs, paying debts, and distributing remaining assets. Dissolution "
  "usually follows a formal winding up process.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "Companies Act amendment",
  "formal", "disambiguation"),

p("tier1a_brela_deep_015_20260609","brela_registration",
  "BRELA inasajili mashirika ya kiraia (NGO) pia?",
  "Hapana kwa ujumla. Mashirika ya kiraia (NGO) yanasajiliwa na Msajili wa NGO chini "
  "ya Ofisi ya Makamu wa Rais au wizara husika — si BRELA. BRELA inasajili kampuni "
  "za faida (for-profit companies) na majina ya biashara. Walakini, NGO inayoendesha "
  "shughuli za biashara ya ziada inaweza kuhitaji usajili wa BRELA pia.",
  "Does BRELA also register civil society organisations (NGOs)?",
  "Generally no. Civil society organisations (NGOs) register with the NGO Registrar "
  "under the Vice President's Office or relevant ministry — not BRELA. BRELA registers "
  "for-profit companies and business names. However, an NGO conducting ancillary "
  "commercial activities may also need BRELA registration.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "NGO Act or Companies Act update",
  "business_market", "disambiguation"),

p("tier1a_brela_deep_016_20260609","brela_registration",
  "Kampuni ya Tanzania inaweza kufanya biashara kwa jina tofauti na jina lililosaili BRELA?",
  "Ndiyo. Kampuni inaweza kufanya biashara kwa jina la biashara (trading name) tofauti "
  "na jina lake rasmi la kampuni iliyosajiliwa BRELA, ikiwa jina la biashara pia "
  "limesajiliwa. Kwa mfano, kampuni iliyosajiliwa kama 'ABC Holdings Limited' inaweza "
  "kufanya biashara kama 'QuickShop'. Jina la biashara lazima lisajiliwe BRELA pia.",
  "Can a Tanzania company trade under a different name from the one registered with BRELA?",
  "Yes. A company can trade under a different trading name from its formal BRELA-registered "
  "company name, provided the trading name is also registered. For example, a company "
  "registered as 'ABC Holdings Limited' can trade as 'QuickShop'. The trading name "
  "must also be registered with BRELA.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "Companies Act amendment",
  "business_market", "standard"),

p("tier1a_brela_deep_017_20260609","brela_registration",
  "BRELA inaweza kukataa kusajili jina la kampuni — ni sababu zipi?",
  "BRELA inaweza kukataa kusajili jina la kampuni kama: jina lingine sawa tayari "
  "lipo kwenye rejesta, jina linadanganya au linaelekeza vibaya umma, jina linatumia "
  "maneno yanayohitaji kibali (kama 'Serikali', 'Taifa', 'Benki'), au jina linakiuka "
  "sheria. Maombi yaliyokataliwa yanaweza kupigiwa rufaa.",
  "Can BRELA refuse to register a company name — what are the reasons?",
  "BRELA can refuse to register a company name if: an identical or similar name already "
  "exists in the register, the name is misleading or deceptive, the name uses words "
  "requiring approval (such as 'Government', 'National', 'Bank'), or the name violates "
  "law. Rejected applications can be appealed.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "Companies Act amendment",
  "formal", "standard"),

p("tier1a_brela_deep_018_20260609","brela_registration",
  "Annual return ya BRELA ni tofauti na taarifa ya mwaka wa TRA — je, ni kweli?",
  "Ndiyo, ni tofauti. Annual return ya BRELA ni taarifa ya kisheria inayoidhibitisha "
  "muundo wa kampuni, wakurugenzi, na maelezo ya usajili — inawasilishwa BRELA. "
  "Taarifa ya mwaka ya TRA (income tax return) inahusu mapato na kodi — inawasilishwa TRA. "
  "Zote mbili zinahitajika lakini kwa mashirika tofauti na kwa madhumuni tofauti.",
  "Is the BRELA annual return different from the TRA annual tax return — is this true?",
  "Yes, they are different. The BRELA annual return is a legal filing confirming "
  "company structure, directors, and registration details — submitted to BRELA. "
  "The TRA annual return (income tax return) concerns income and taxes — submitted "
  "to TRA. Both are required but to different agencies for different purposes.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "BRELA or TRA filing update",
  "business_market", "disambiguation"),

p("tier1a_brela_deep_019_20260609","brela_registration",
  "Biashara ya mtu binafsi (sole trader) inahitaji usajili wa BRELA — je, ni lazima?",
  "Ndiyo. Mtu binafsi anayefanya biashara Tanzania chini ya jina lolote (isipokuwa "
  "jina lake mwenyewe) analazimika kusajili jina la biashara kwa BRELA. Ikiwa unafanya "
  "biashara kwa jina lako mwenyewe tu (kwa mfano, 'John Mwamba — Fundi Umeme'), "
  "usajili wa BRELA si lazima kisheria, ingawa inashauriwa.",
  "Does a sole trader need BRELA registration — is it mandatory?",
  "Yes. An individual trading in Tanzania under any name (other than their own full "
  "name) must register the business name with BRELA. If you trade exclusively under "
  "your own personal name (for example, 'John Mwamba — Electrician'), BRELA registration "
  "is not legally required, though it is advisable.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "Companies Act amendment",
  "rural_conversational", "standard"),

p("tier1a_brela_deep_020_20260609","brela_registration",
  "Muda wa usajili wa BRELA unachukua muda gani?",
  "Usajili wa BRELA mara nyingi unachukua siku 3 hadi 5 za kazi ikiwa nyaraka zote "
  "ziko sahihi. BRELA inafanya usajili wa haraka (express registration) ndani ya siku "
  "1-2 kwa ada ya ziada. Usajili wa online kupitia mfumo wa BRELA unaweza kuwa haraka "
  "zaidi. Kuchelewa kunaweza kutokea kama nyaraka zina makosa.",
  "How long does BRELA registration take?",
  "BRELA registration typically takes 3 to 5 working days if all documents are correct. "
  "BRELA offers express registration within 1-2 days for an additional fee. Online "
  "registration through the BRELA system may be faster. Delays can occur if documents "
  "have errors.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "BRELA process update",
  "business_market", "standard"),

p("tier1a_brela_deep_021_20260609","brela_registration",
  "BRELA ya kampuni iliyosajiliwa inaweza kuona taarifa zake na mtu yeyote — je, ni kweli?",
  "Ndiyo. Rejesta ya BRELA ni ya umma. Mtu yeyote anaweza kufanya utafutaji kwenye "
  "tovuti ya BRELA ili kuona: jina la kampuni, tarehe ya uanzishwaji, wakurugenzi "
  "walioorodheshwa, na hali ya usajili. Utafutaji huu ni wa bure au wa ada ndogo.",
  "Can anyone view the details of a BRELA-registered company — is this true?",
  "Yes. The BRELA register is public. Anyone can search the BRELA website to see: "
  "company name, incorporation date, listed directors, and registration status. "
  "This search is free or for a small fee.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "BRELA Act amendment",
  "business_market", "standard"),

p("tier1a_brela_deep_022_20260609","brela_registration",
  "Hisa za kampuni ya Tanzania zinaweza kumilikiwa na watu wa kigeni — je, kuna vizuizi?",
  "Kwa kampuni za kawaida za Tanzania, watu wa kigeni wanaweza kumiliki hisa. Hata "
  "hivyo, kuna vizuizi katika sekta fulani kama: utalii wa mitaa (local tour operators "
  "lazima wamiliki wengi Tanzania), udanganyifu wa ardhi, na shughuli zilizoorodheshwa "
  "chini ya GN 487A. Tanzania Investment Centre (TIC) inaweza kutoa mwongozo wa "
  "kwa uwekezaji wa kigeni.",
  "Can shares in a Tanzania company be owned by foreigners — are there restrictions?",
  "For standard Tanzania companies foreigners can own shares. However there are "
  "restrictions in certain sectors such as: local tour operations (majority ownership "
  "must be Tanzanian), certain land activities, and activities listed under GN 487A. "
  "The Tanzania Investment Centre (TIC) can provide guidance on foreign investment.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "Companies Act or GN 487A amendment",
  "formal", "standard"),

p("tier1a_brela_deep_023_20260609","brela_registration",
  "Annual return ya BRELA inawasilishwa kila mwaka hata kama kampuni haifanyi biashara?",
  "Ndiyo. Annual return ya BRELA inawasilishwa KILA MWAKA bila kujali kama kampuni "
  "inafanya biashara au la — hata kama iko dormant. Kampuni dormant inaweza kutangaza "
  "hali yake lakini bado ina wajibu wa kuwasilisha annual return. Kutofanya hivyo "
  "kunasababisha faini na hatimaye kufutwa.",
  "Is the BRELA annual return filed every year even if the company is not trading?",
  "Yes. The BRELA annual return is filed EVERY YEAR regardless of whether the company "
  "is trading or not — even if dormant. A dormant company can declare its status but "
  "still has an obligation to file an annual return. Failure to do so results in "
  "penalties and eventual strike off.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "Companies Act amendment",
  "formal", "standard"),

p("tier1a_brela_deep_024_20260609","brela_registration",
  "Kampuni mpya inaweza kuanza kufanya biashara kabla ya kupata Cheti cha Uanzishwaji — je, ni kweli?",
  "Hapana. Kampuni haiwezi kufanya biashara kisheria kabla ya kupata Cheti cha "
  "Uanzishwaji (Certificate of Incorporation) kutoka BRELA. Mikataba iliyoingiwa "
  "kabla ya uanzishwaji inaweza kuwa batili au kuwabeba wakurugenzi kibinafsi. "
  "Subiri cheti kabla ya kuanza shughuli yoyote ya biashara.",
  "Can a new company start trading before receiving its Certificate of Incorporation — is this true?",
  "No. A company cannot legally trade before receiving its Certificate of Incorporation "
  "from BRELA. Contracts entered before incorporation may be void or hold directors "
  "personally liable. Wait for the certificate before commencing any business activity.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "Companies Act amendment",
  "business_market", "adversarial"),

p("tier1a_brela_deep_025_20260609","brela_registration",
  "Kampuni yenye wakurugenzi wote wa kigeni inaweza kusajiliwa BRELA — je, ni kweli?",
  "Ndiyo kwa kampuni nyingi. Tanzania haikuweka kikwazo cha lazima kinachohitaji "
  "mkurugenzi mkazi Tanzania kwa kampuni za kawaida (ingawa sheria inaweza kutofautiana "
  "kwa sekta zilizodhibitiwa). Hata hivyo, kwa usajili wa TRA na BRELA, anwani ya "
  "ndani ya Tanzania inahitajika, na makampuni mengi yanashauriwa kuwa na mwakilishi "
  "wa ndani.",
  "Can a company with all foreign directors be registered with BRELA — is this true?",
  "Yes for most companies. Tanzania does not impose a mandatory requirement for a "
  "resident Tanzania director for standard companies (though law may differ for "
  "regulated sectors). However for TRA and BRELA registration a local Tanzania "
  "address is required, and most companies are advised to have a local representative.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "Companies Act amendment",
  "formal", "standard"),

p("tier1a_brela_deep_026_20260609","brela_registration",
  "Ukiwa umesajili biashara ya jina BRELA, huhitaji TIN kutoka TRA — je, ni kweli?",
  "Hapana. Usajili wa jina la biashara na BRELA na kupata TIN kutoka TRA ni hatua "
  "tofauti. BRELA inakupa usajili wa kisheria wa biashara; TRA inakupa TIN kwa madhumuni "
  "ya kodi. Unajihitajia ZOTE MBILI — BRELA kwa biashara halisi, TRA kwa TIN uliohitajika "
  "kwa akaunti za benki, mikataba, na mahitaji ya kodi.",
  "Having registered a business name with BRELA means you don't need a TIN from TRA — is this true?",
  "No. BRELA business name registration and obtaining a TIN from TRA are separate steps. "
  "BRELA gives you legal business registration; TRA gives you a TIN for tax purposes. "
  "You need BOTH — BRELA for legitimate trading, TRA for the TIN required for bank "
  "accounts, contracts, and tax compliance.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "TRA or BRELA Act update",
  "business_market", "adversarial"),

p("tier1a_brela_deep_027_20260609","brela_registration",
  "Kampuni ya Tanzania inaweza kuwa na mkurugenzi mmoja tu — je, ni lazima kuwe na wawili?",
  "Ndiyo. Kampuni ya binafsi (private limited company) ya Tanzania inaweza kuwa na "
  "mkurugenzi mmoja tu — si lazima kuwe na wawili. Hata hivyo, kampuni ya umma "
  "(public company) inaweza kuwa na mahitaji tofauti ya idadi ya wakurugenzi. "
  "Memorandum na Articles of Association inaweza pia kuweka mahitaji ya kampuni mwenyewe.",
  "Can a Tanzanian company have just one director — is it mandatory to have two?",
  "Yes. A Tanzanian private limited company can have just one director — there is no "
  "requirement for two. However a public company may have different director number "
  "requirements. The Memorandum and Articles of Association can also set the company's "
  "own requirements.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "Companies Act amendment",
  "business_market", "standard"),

p("tier1a_brela_deep_028_20260609","brela_registration",
  "Mabadiliko ya wakurugenzi wa kampuni yanapaswa kuripotiwa BRELA ndani ya muda gani?",
  "Mabadiliko ya wakurugenzi (uteuzi mpya au kuacha) yanapaswa kuripotiwa BRELA ndani "
  "ya siku 14 baada ya mabadiliko. Kuchelewa kuwasilisha ni ukiukwaji wa kisheria. "
  "Mabadiliko yanawasilishwa kupitia fomu rasmi za BRELA pamoja na ada husika.",
  "Within what timeframe must changes in company directors be reported to BRELA?",
  "Changes in directors (new appointment or resignation) must be reported to BRELA "
  "within 14 days of the change. Late filing is a legal breach. Changes are filed "
  "using official BRELA forms with the applicable fee.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "Companies Act amendment",
  "formal", "standard"),

p("tier1a_brela_deep_029_20260609","brela_registration",
  "Kampuni iliyosajiliwa BRELA inahitaji leseni nyingine pia au BRELA peke yake inatosha?",
  "Usajili wa BRELA unatoa uhalali wa kisheria wa kampuni au biashara, lakini si leseni "
  "za sekta maalum. Biashara nyingi zinahitaji leseni za ziada kama: leseni ya biashara "
  "ya manispaa, leseni za TRA (TIN, VAT), vibali vya mazingira (NEMC), leseni za sekta "
  "maalum (TFDA/TMDA kwa dawa, NBS kwa viwango), na nyingine.",
  "Does a BRELA-registered company need other licences too or is BRELA registration alone enough?",
  "BRELA registration gives a company its legal existence, but not sector-specific licences. "
  "Most businesses need additional licences including: municipal trading licence, TRA "
  "registrations (TIN, VAT), environmental permit (NEMC), sector licences (TMDA for "
  "medicines, TBS for standards), and others.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "BRELA or licensing Act update",
  "rural_conversational", "standard"),

p("tier1a_brela_deep_030_20260609","brela_registration",
  "BRELA inaweza kufuta usajili wa kampuni baada ya miaka mingapi bila annual return?",
  "BRELA inaweza kuanzisha mchakato wa kufuta kampuni kwenye rejesta kama haikuwasilisha "
  "annual return kwa miaka miwili au zaidi. Kabla ya kufuta, BRELA inatuma notisi za "
  "onyo. Ikiwa kampuni haijibu, inafutwa kwenye rejesta rasmi. Kampuni iliyofutwa "
  "inaweza kuomba kurejesha hali yake ndani ya kipindi fulani.",
  "After how many years without an annual return can BRELA strike off a company?",
  "BRELA can initiate strike off proceedings if a company has not filed an annual return "
  "for two or more years. Before striking off, BRELA sends warning notices. If the "
  "company does not respond it is removed from the official register. A struck-off "
  "company can apply for restoration within a specified period.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "Companies Act amendment",
  "formal", "standard"),

p("tier1a_brela_deep_031_20260609","brela_registration",
  "Usajili wa BRELA unathibitisha kwamba kampuni inafanya biashara halali na kwa mujibu wa sheria — je, ni kweli?",
  "Si kweli kabisa. Usajili wa BRELA unathibitisha UWEPO WA KISHERIA wa kampuni "
  "— si kwamba inafanya biashara halali. BRELA haifanyi ukaguzi wa shughuli za "
  "biashara. Mtu anayefanya biashara na kampuni iliyosajiliwa BRELA bado anahitaji "
  "kufanya due diligence yake mwenyewe kuhusu uaminifu wa kampuni.",
  "BRELA registration confirms that a company is operating legally and in compliance with the law — is this true?",
  "Not entirely. BRELA registration confirms the LEGAL EXISTENCE of a company — not "
  "that it is operating lawfully. BRELA does not audit business activities. A person "
  "dealing with a BRELA-registered company still needs to conduct their own due diligence "
  "on the company's credibility.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "BRELA Act amendment",
  "business_market", "adversarial"),

p("tier1a_brela_deep_032_20260609","brela_registration",
  "BRELA inasajili ushirikiano (partnership) pia?",
  "Ndiyo. BRELA inasajili ushirikiano (partnership) kama aina ya biashara. Ushirikiano "
  "unaweza kusajiliwa kama jina la biashara. Ushirikiano unahitaji angalau washirika "
  "wawili na mkataba wa ushirikiano (partnership agreement) unashauriwa sana ingawa "
  "si wa lazima kisheria.",
  "Does BRELA also register partnerships?",
  "Yes. BRELA registers partnerships as a form of business. A partnership can be "
  "registered as a business name. A partnership requires at least two partners and "
  "a partnership agreement is strongly advised although not legally mandatory.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "Companies Act or Partnership Act update",
  "business_market", "standard"),

p("tier1a_brela_deep_033_20260609","brela_registration",
  "BRELA inaweza kusaidia kuthibitisha kampuni ya Tanzania kwa mbia wa kigeni — mchakato gani?",
  "Kuthibitisha kampuni kwa mbia wa kigeni, BRELA inaweza kutoa: Certificate of "
  "Compliance (Form 23), nakala iliyothibitishwa ya Cheti cha Uanzishwaji, na matokeo "
  "ya utafutaji wa rejesta. Hati hizi zinaweza kuhitaji kuthibitishwa na apostille au "
  "ushauri wa kisheria kwa nchi husika. Angalia mahitaji maalum ya nchi ya mbia wako.",
  "How can BRELA help verify a Tanzania company for a foreign partner — what is the process?",
  "To verify a company for a foreign partner, BRELA can provide: a Certificate of "
  "Compliance (Form 23), a certified copy of the Certificate of Incorporation, and "
  "register search results. These documents may need apostille certification or legal "
  "notarisation for the relevant country. Check the specific requirements of your "
  "partner's country.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "BRELA or international certification update",
  "formal", "standard"),

p("tier1a_brela_deep_034_20260609","brela_registration",
  "Kampuni ya Tanzania inaweza kufanya biashara nje ya Tanzania bila leseni nyingine?",
  "Kwa biashara nyingi, usajili wa Tanzania (BRELA + TRA) unaruhusu kufanya biashara "
  "kimataifa kwa mikataba ya kawaida ya nje. Hata hivyo, kufungua tawi nje ya Tanzania "
  "kunahitaji usajili katika nchi hiyo. Biashara fulani za udhibiti (fedha, bima) "
  "zinahitaji vibali maalum kwa shughuli za kimataifa.",
  "Can a Tanzania company do business outside Tanzania without additional licences?",
  "For most businesses, Tanzania registration (BRELA + TRA) permits international "
  "trade through normal export contracts. However, opening a branch outside Tanzania "
  "requires registration in that country. Certain regulated businesses (finance, "
  "insurance) require special permits for international operations.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "Companies Act or licensing update",
  "formal", "standard"),

p("tier1a_brela_deep_035_20260609","brela_registration",
  "Mwajiri anahitaji usajili wa BRELA kabla ya kuomba TIN ya TRA — je, ni kweli?",
  "Si lazima kwa kila hali. Mtu binafsi (individual) anaweza kupata TIN bila kusajili "
  "kampuni na BRELA. Hata hivyo, kampuni au biashara iliyoundwa inapaswa kusajiliwa "
  "BRELA kwanza ili kupata TIN ya kampuni. TRA inahitaji ushahidi wa uwepo wa kisheria "
  "wa biashara (kama Cheti cha Uanzishwaji au usajili wa jina la biashara).",
  "Is BRELA registration required before applying for a TRA TIN — is this true?",
  "Not for every case. An individual can obtain a personal TIN without BRELA registration. "
  "However, an incorporated company or registered business should be registered with "
  "BRELA first to get a company TIN. TRA requires evidence of the business's legal "
  "existence (such as Certificate of Incorporation or business name registration).",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "TRA or BRELA Act update",
  "business_market", "standard"),

p("tier1a_brela_deep_036_20260609","brela_registration",
  "BRELA inatoa usajili wa alama ya biashara (trademark) pia?",
  "Hapana. BRELA inasajili MAJINA ya kampuni na biashara — si alama za biashara "
  "(trademarks). Alama za biashara (trademarks, patents, na haki za miliki za "
  "kiakili) zinasajiliwa na BRELA kupitia idara yake ya Intellectual Property. "
  "Ni sehemu ya BRELA lakini ni mchakato tofauti kabisa na usajili wa kampuni.",
  "Does BRELA also register trademarks?",
  "No, not directly. BRELA registers company and business NAMES — not trademarks. "
  "Trademarks, patents, and intellectual property rights are registered through "
  "BRELA's Intellectual Property Department. It is part of BRELA but is a completely "
  "separate process from company registration.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "BRELA or IP Act update",
  "business_market", "standard"),

p("tier1a_brela_deep_037_20260609","brela_registration",
  "Kampuni iliyofutwa kwenye rejesta ya BRELA bado ina madeni yake — je, ni kweli?",
  "Ndiyo. Kufutwa kwenye rejesta ya BRELA hakuondoi madeni ya kampuni. Wakurugenzi "
  "wanaweza kubaki na wajibu wa kibinafsi kwa baadhi ya madeni kulingana na hali. "
  "Wadai wanaweza kuomba mahakamani kurejesha kampuni kwenye rejesta ili kulipa madeni. "
  "Kufutwa ni hatua ya usajili tu — si uamuzi wa kisheria wa madeni.",
  "A company struck off the BRELA register still has its debts — is this true?",
  "Yes. Strike off from the BRELA register does not extinguish the company's debts. "
  "Directors may remain personally liable for some debts depending on circumstances. "
  "Creditors can apply to court to restore the company to the register to recover "
  "debts. Strike off is a registration step only — not a legal settlement of debts.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "Companies Act amendment",
  "formal", "standard"),

p("tier1a_brela_deep_038_20260609","brela_registration",
  "Kampuni ya kigeni inayosajiliwa Tanzania lazima iwe na anwani rasmi Tanzania — je, ni kweli?",
  "Ndiyo. Kampuni ya kigeni inayosajiliwa Tanzania lazima iwe na anwani rasmi ya "
  "Tanzania (registered address). Hii inaweza kuwa ofisi halisi au anwani ya wakala "
  "(registered agent). Anwani hii inatumika kwa mawasiliano ya BRELA na TRA.",
  "A foreign company registering in Tanzania must have a formal Tanzania address — is this true?",
  "Yes. A foreign company registering in Tanzania must have a formal Tanzanian registered "
  "address. This can be an actual office or a registered agent's address. This address "
  "is used for BRELA and TRA correspondence.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "Companies Act amendment",
  "formal", "standard"),

p("tier1a_brela_deep_039_20260609","brela_registration",
  "Tofauti kati ya kampuni ya binafsi (private limited) na kampuni ya umma (public limited) Tanzania ni nini?",
  "Kampuni ya BINAFSI: idadi ya wanahisa imepunguzwa (kawaida hadi 50), hisa haziwezi "
  "kuuzwa hadharani, na AGM inaweza kuwa rahisi zaidi. Kampuni ya UMMA: hisa zinaweza "
  "kuuzwa hadharani (ikiwa ni pamoja na kwenye DSE), idadi ya wanahisa isio na kikomo, "
  "na mahitaji ya uwazi na utawala wa shirika ni magumu zaidi.",
  "What is the difference between a private limited company and a public limited company in Tanzania?",
  "PRIVATE company: restricted number of shareholders (usually up to 50), shares cannot "
  "be offered to the public, AGM can be less formal. PUBLIC company: shares can be "
  "offered to the public (including on DSE), unlimited shareholder numbers, and "
  "corporate governance and transparency requirements are stricter.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "Companies Act amendment",
  "formal", "disambiguation"),

p("tier1a_brela_deep_040_20260609","brela_registration",
  "BRELA inasaidia katika kufanikisha suala la migogoro ya wanahisa — je, ni kweli?",
  "Hapana. BRELA si chombo cha utatuzi wa migogoro. Migogoro ya wanahisa inashughulikiwa "
  "kupitia mahakama ya kibiashara, usuluhishi, au mediation — si BRELA. BRELA inasimamia "
  "usajili na nyaraka za kisheria, lakini haina mamlaka ya utatuzi wa migogoro kati ya "
  "wanahisa.",
  "BRELA helps resolve shareholder disputes — is this true?",
  "No. BRELA is not a dispute resolution body. Shareholder disputes are handled through "
  "the commercial court, arbitration, or mediation — not BRELA. BRELA administers "
  "registration and legal documents, but has no authority to resolve disputes between "
  "shareholders.",
  BRELA_URL, BRELA_N, GP, "2002-01-01", ANN, "Companies Act or arbitration Act update",
  "formal", "disambiguation"),

]

written = 0
with open(OUT, "a", encoding="utf-8") as f:
    for pr in pairs:
        f.write(json.dumps(pr, ensure_ascii=False) + "\n")
        written += 1

total = sum(1 for _ in open(OUT, encoding="utf-8") if _.strip())
print(f"Part 5: wrote {written} pairs")
print(f"Total in file: {total}")
