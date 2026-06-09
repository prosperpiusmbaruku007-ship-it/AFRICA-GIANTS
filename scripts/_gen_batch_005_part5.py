#!/usr/bin/env python3
"""batch_005 part 5 — efd_deep (50 pairs, 201-250)"""
import json, os

OUT = "datasets/tier1a/raw_sources/raw_pairs_batch_005.jsonl"
D = "2026-06-09"
TRA = "https://www.tra.go.tz/page/electronic-fiscal-devices"
TRA_N = "Tanzania Revenue Authority — EFD"
TRA_VAT = "https://www.tra.go.tz/page/value-added-tax"
TRA_VAT_N = "Tanzania Revenue Authority — VAT"
GP = "government_portal"
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

p("tier1a_efd_201_20260609","efd_compliance",
  "EFD ni nini na inatumika kwa nini Tanzania?",
  "EFD (Electronic Fiscal Device) ni mashine ya kielelezo cha fedha iliyoidhinishwa "
  "na TRA inayorekodia kila muamala wa mauzo moja kwa moja na kupeleka taarifa kwa "
  "TRA moja kwa moja. Inatumika kuhakikisha kwamba: (1) kila mauzo yanafuatiliwa "
  "kwa madhumuni ya VAT na kodi ya mapato, (2) risiti za EFD zinaotolewa kwa wateja, "
  "(3) TRA inapata data ya mauzo moja kwa moja bila kutegemea ripoti za mkono tu. "
  "EFD inabadilisha risiti za kawaida za mkono.",
  "What is an EFD and what is it used for in Tanzania?",
  "An EFD (Electronic Fiscal Device) is a TRA-approved fiscal recording machine that "
  "records every sales transaction directly and transmits data to TRA automatically. "
  "It is used to ensure: (1) every sale is tracked for VAT and income tax purposes, "
  "(2) EFD receipts are issued to customers, (3) TRA receives sales data directly "
  "without relying only on manual reports. EFDs replace ordinary handwritten receipts.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA EFD mandate or technology update",
  "business_market", "standard"),

p("tier1a_efd_202_20260609","efd_compliance",
  "Biashara zipi Tanzania zinalazimishwa kutumia EFD?",
  "TRA inaweza kutoa amri ya EFD kwa aina yoyote ya biashara. Kwa sasa, EFD ni lazima "
  "kwa: (1) biashara zote zilizosajili VAT (bila kujali ukubwa), (2) biashara "
  "zilizoteuliwa na TRA hata kama hazisajili VAT. TRA imetoa orodha ya sekta "
  "zinalazimika kutumia EFD — ikiwa ni pamoja na maduka ya rejareja, hoteli, "
  "hospitali za kibinafsi, na sekta nyingine. Angalia TRA moja kwa moja kwa "
  "orodha ya hali ya sasa ya sekta zinazolazimika.",
  "Which businesses in Tanzania are required to use an EFD?",
  "TRA can issue an EFD directive to any business type. Currently, EFD is mandatory "
  "for: (1) all VAT-registered businesses (regardless of size), (2) businesses "
  "designated by TRA even if not VAT-registered. TRA has published a list of sectors "
  "required to use EFD — including retail shops, hotels, private hospitals, and other "
  "sectors. Check TRA directly for the current list of mandatory sectors.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA EFD directive update",
  "formal", "standard"),

p("tier1a_efd_203_20260609","efd_compliance",
  "EFD machine inanunuliwa wapi Tanzania — mwajiri ananunua wenyewe au TRA inatoa?",
  "MWAJIRI (biashara) ndiye anayenunua EFD — TRA haitoi mashine bure. Mashine "
  "lazima inunuliwe kutoka kwa wasambazaji wa EFD walioidhinishwa na TRA. "
  "Wasambazaji walioidhinishwa wanajulikana kwenye tovuti ya TRA. "
  "Kununua EFD kutoka chanzo kisichoidhinishwa ni kosa — mashine lazima iwe kwenye "
  "mfumo wa TRA na iwe imesajiliwa ipasavyo kabla ya kuanza kutumia.",
  "Where is an EFD machine purchased in Tanzania — does the employer buy it or does TRA provide it?",
  "The EMPLOYER (business) buys the EFD — TRA does not provide machines for free. "
  "The machine must be purchased from TRA-approved EFD suppliers. Approved suppliers "
  "are listed on the TRA website. Buying an EFD from an unapproved source is an "
  "offence — the machine must be on the TRA system and properly registered before "
  "starting to use it.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA EFD supplier list update",
  "business_market", "standard"),

p("tier1a_efd_204_20260609","efd_compliance",
  "Risiti ya EFD inatofautiana vipi na risiti ya kawaida ya biashara Tanzania?",
  "Risiti ya EFD ina vipengele maalum vinavyothibitisha uhalali wake: "
  "(1) nambari ya serial ya EFD, (2) nambari ya TIN ya biashara, (3) tarehe na "
  "wakati wa muamala uliorekodiwa na EFD, (4) nambari ya muamala (transaction number), "
  "(5) kiasi cha VAT kilichohesabiwa na EFD, (6) msimbo wa uthibitisho "
  "(verification code) unaoweza kukaguliwa kwenye mfumo wa TRA. "
  "Risiti za EFD ni ushahidi wa kisheria wa muamala wa biashara.",
  "How does an EFD receipt differ from an ordinary business receipt in Tanzania?",
  "An EFD receipt has specific features that verify its authenticity: "
  "(1) EFD serial number, (2) business TIN number, (3) date and time of transaction "
  "recorded by the EFD, (4) transaction number, (5) VAT amount calculated by the EFD, "
  "(6) verification code that can be checked on the TRA system. "
  "EFD receipts are legal evidence of a business transaction.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA EFD receipt requirement update",
  "formal", "standard"),

p("tier1a_efd_205_20260609","efd_compliance",
  "Mteja ana haki ya kudai risiti ya EFD Tanzania — je, biashara inaweza kukataa?",
  "Hapana. Kila mteja ana haki ya kupewa risiti ya EFD kwa kila nunuzi wanaofanya. "
  "Biashara iliyolazimika kutumia EFD HAIWEZI kukataa kutoa risiti ya EFD. "
  "Kutotoa risiti ya EFD ni kosa la kisheria chini ya Sheria ya TRA na inaweza "
  "kusababisha faini au kufungwa kwa biashara. Wateja wanashauriwa kudai risiti "
  "za EFD na kuripoti biashara zisizozipatia.",
  "Does a customer have the right to demand an EFD receipt in Tanzania — can a "
  "business refuse?",
  "No. Every customer has the right to receive an EFD receipt for every purchase they "
  "make. A business required to use an EFD CANNOT refuse to issue an EFD receipt. "
  "Not issuing an EFD receipt is a legal offence under TRA law and can result in "
  "fines or business closure. Customers are encouraged to demand EFD receipts and "
  "report businesses that do not provide them.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA EFD enforcement update",
  "business_market", "adversarial"),

p("tier1a_efd_206_20260609","efd_compliance",
  "EFD machine ikivunjika au kuharibika Tanzania — biashara inafanya nini?",
  "Ikiwa EFD machine inavunjika: (1) ripoti kwa TRA haraka (kupitia mfumo wa TRA au "
  "msambazaji wako wa EFD), (2) usifanye mauzo bila EFD kwa muda wowote bila ruhusa "
  "ya TRA — hii ni kosa, (3) TRA inaweza kutoa ruhusa ya muda mfupi ya kuandika "
  "risiti za mkono wakati wa kusubiri ukarabati, (4) mashine iliyoharibika lazima "
  "irekebishwe na msambazaji aliyeidhinishwa, si mtu yeyote. Hifadhi rekodi za "
  "mauzo yaliyofanywa wakati EFD haikufanya kazi.",
  "If an EFD machine breaks down in Tanzania — what does the business do?",
  "If an EFD machine breaks down: (1) report to TRA promptly (via TRA system or your "
  "EFD supplier), (2) do not make sales without the EFD for any period without TRA "
  "authorisation — this is an offence, (3) TRA may grant short-term permission to "
  "write manual receipts while awaiting repair, (4) the broken machine must be "
  "repaired by an authorised supplier, not just anyone. Keep records of sales made "
  "while the EFD was not functioning.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA EFD breakdown procedure update",
  "business_market", "standard"),

p("tier1a_efd_207_20260609","efd_compliance",
  "EFD inahitajika kwa mauzo ya mtandaoni (online sales) Tanzania?",
  "TRA inashughulikia aina za EFD kwa mauzo ya kidijitali Tanzania. Mauzo ya "
  "mtandaoni yanayofanywa na biashara zilizosajili VAT bado yanahitaji ufuatiliaji "
  "wa kielelezo cha fedha. TRA inaweza kutoa mwongozo mahususi kwa biashara za "
  "mtandaoni kuhusu jinsi ya kufuata sheria za EFD kwa miamala ya kidijitali. "
  "Angalia TRA moja kwa moja kwa hali ya EFD kwa biashara yako ya mtandaoni.",
  "Is an EFD required for online sales in Tanzania?",
  "TRA is addressing EFD compliance for digital sales in Tanzania. Online sales made "
  "by VAT-registered businesses still require fiscal tracking. TRA may issue specific "
  "guidance for online businesses on how to comply with EFD requirements for digital "
  "transactions. Check TRA directly for the EFD position for your online business.",
  TRA, TRA_N, GP, "2025-09-01", ANN, "TRA EFD digital commerce update",
  "business_market", "standard"),

p("tier1a_efd_208_20260609","efd_compliance",
  "Adhabu za kutotumia EFD au kutotoa risiti ya EFD Tanzania ni zipi?",
  "Adhabu za kukiuka sheria za EFD Tanzania ni kali: (1) faini ya kiasi kikubwa "
  "kwa kutotoa risiti ya EFD, (2) kufungwa kwa biashara kwa muda — TRA ina mamlaka "
  "ya kufunga biashara inayokiuka sheria za EFD, (3) ukaguzi wa kina wa biashara "
  "yako na TRA, (4) hatari ya tathmini ya kodi kwa kipindi kilichopita. "
  "Faini na adhabu zinaweza kuwa TZS 1M-5M au zaidi kulingana na ukiukwaji.",
  "What are the penalties for not using an EFD or not issuing an EFD receipt in Tanzania?",
  "Penalties for EFD law violations in Tanzania are severe: (1) large fines for not "
  "issuing an EFD receipt, (2) temporary business closure — TRA has authority to "
  "close a business that violates EFD rules, (3) detailed TRA audit of your business, "
  "(4) risk of tax assessment for past periods. Fines and penalties can be TZS 1M-5M "
  "or more depending on the violation.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA EFD penalty update",
  "business_market", "standard"),

p("tier1a_efd_209_20260609","efd_compliance",
  "EFD ya biashara moja inaweza kutumika kwa biashara nyingine ya mwenye biashara "
  "huyo huyo Tanzania?",
  "Hapana. Kila EFD machine inasajiliwa kwa biashara MAALUM na TIN yake mahususi. "
  "EFD iliyosajiliwa kwa biashara moja haiwezi kutumika kisheria kwa biashara nyingine, "
  "hata kama mwenye biashara ni mtu mmoja. Kila biashara lazima iwe na EFD yake "
  "iliyosajiliwa kwa TIN yake mwenyewe.",
  "Can an EFD machine for one business be used for another business owned by the "
  "same person in Tanzania?",
  "No. Each EFD machine is registered to a SPECIFIC business and its particular TIN. "
  "An EFD registered for one business cannot legally be used for another business, "
  "even if the same person owns both. Each business must have its own EFD registered "
  "to its own TIN.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA EFD registration policy update",
  "formal", "adversarial"),

p("tier1a_efd_210_20260609","efd_compliance",
  "EFD machine inahitajika kwa kila tawi (branch) la biashara Tanzania?",
  "Ndiyo. Kila tawi au mahali pa biashara (point of sale) linalofanya mauzo "
  "lazima liwe na EFD lake mwenyewe iliyosajiliwa. Biashara yenye matawi mengi "
  "lazima iwe na EFD katika kila tawi. Unaweza kuwa na EFD nyingi zilizosajiliwa "
  "kwa TIN moja ya kampuni, lakini kila EFD lazima isajiliwe mahali pamoja na "
  "itumike mahali pale.",
  "Is an EFD machine required for every branch of a business in Tanzania?",
  "Yes. Every branch or point of sale that makes sales must have its own registered "
  "EFD. A business with multiple branches must have an EFD at each branch. You can "
  "have multiple EFDs registered under one company TIN, but each EFD must be "
  "registered at a specific location and used at that location.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA EFD branch requirement update",
  "formal", "standard"),

p("tier1a_efd_211_20260609","efd_compliance",
  "Biashara inaweza kutumia programu ya kompyuta (software POS) badala ya EFD "
  "machine Tanzania?",
  "TRA Tanzania inazidi kukubali mifumo ya software ya POS (Virtual EFD/Electronic "
  "Fiscal Receipt) kama mbadala wa EFD za kawaida za vifaa (hardware) katika "
  "hali fulani. Mfumo wa software lazima uidhiniwe na TRA na uunganishwe na mfumo "
  "wa TRA moja kwa moja. Usitumie programu yoyote ya POS bila uthibitisho kwamba "
  "imeidhinishwa na TRA — angalia TRA kwa hali ya sasa ya mifumo iliyoidhinishwa.",
  "Can a business use a computer software (POS system) instead of an EFD machine "
  "in Tanzania?",
  "TRA Tanzania is increasingly accepting software POS systems (Virtual EFD/Electronic "
  "Fiscal Receipt) as alternatives to traditional hardware EFDs in certain situations. "
  "The software system must be TRA-approved and connected directly to TRA's system. "
  "Do not use any POS software without confirming it is TRA-approved — check TRA "
  "for the current list of approved systems.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA virtual EFD or software POS approval update",
  "business_market", "standard"),

p("tier1a_efd_212_20260609","efd_compliance",
  "EFD inahusiana vipi na VAT — VAT inaonekana kwenye risiti ya EFD vipi?",
  "EFD inashughulikia VAT kiotomatiki kwenye kila muamala: (1) inahesabu kiasi cha "
  "VAT (18%) kwenye bei ya mauzo inayostahili, (2) inaonyesha bei kabla ya VAT, "
  "kiasi cha VAT, na jumla inayojumuisha VAT kwenye risiti, (3) inarekodia data "
  "ya VAT moja kwa moja kwa mfumo wa TRA ili kuandaa tamko la VAT la kila mwezi. "
  "Hii inamaanisha data ya tamko lako la VAT inatoka moja kwa moja kwenye rekodi "
  "za EFD.",
  "How does an EFD relate to VAT — how does VAT appear on an EFD receipt?",
  "An EFD handles VAT automatically on every transaction: (1) it calculates the VAT "
  "amount (18%) on the taxable sale price, (2) it shows the pre-VAT price, VAT amount, "
  "and VAT-inclusive total on the receipt, (3) it records VAT data directly to TRA's "
  "system to prepare the monthly VAT return. This means your VAT return data comes "
  "directly from EFD records.",
  TRA_VAT, TRA_VAT_N, GP, "2015-07-01", ANN, "Finance Act VAT or EFD system update",
  "business_market", "standard"),

p("tier1a_efd_213_20260609","efd_compliance",
  "Biashara iliyosajili VAT lazima iwasilishe tamko la VAT hata kama haikufanya "
  "mauzo mwezi huo Tanzania?",
  "Ndiyo. Biashara iliyosajili VAT Tanzania lazima iwasilishe tamko la VAT kwa TRA "
  "kila mwezi bila kujali kama ilifanya mauzo au la. Tamko la sifuri (nil return) "
  "linawasilishwa ikiwa hakuna mauzo. Tarehe ya mwisho ni tarehe 20 ya mwezi "
  "unaofuata. Kushindwa kuwasilisha nil return kunasababisha adhabu kama vile "
  "kutokufanya mauzo hakumaanishi tamko halikuhitajika.",
  "Must a VAT-registered business file a VAT return even if it made no sales that "
  "month in Tanzania?",
  "Yes. A VAT-registered business in Tanzania must file a VAT return with TRA every "
  "month regardless of whether it made sales or not. A nil return is filed if there "
  "were no sales. The deadline is the 20th of the following month. Failing to file "
  "a nil return attracts penalties just as if sales had been made but not reported.",
  TRA_VAT, TRA_VAT_N, GP, "2025-07-01", ANN, "Tax Administration Act VAT filing update",
  "business_market", "adversarial"),

p("tier1a_efd_214_20260609","efd_compliance",
  "Mauzo ya VAT ya sifuri (zero-rated) yanaonekana vipi kwenye EFD Tanzania?",
  "Mauzo yanayostahili kiwango cha sifuri cha VAT (zero-rated) yanaingizwa kwenye "
  "EFD kwa kiwango cha 0% — si msamaha. Tofauti kati ya zero-rated na exempt: "
  "mauzo ya zero-rated yanaonyeshwa kwenye tamko la VAT na yanakuruhusu kudai VAT "
  "ya pembejeo (input VAT) unayolipa. Mauzo ya exempt hayaonyeshwi kwa madhumuni "
  "ya VAT na hayakuruhusu kudai input VAT. EFD lazima iwe na programu inayoweza "
  "kutofautisha kati ya zero-rated, exempt, na standard-rated.",
  "How do zero-rated VAT sales appear on an EFD in Tanzania?",
  "Sales qualifying for zero-rated VAT are entered in the EFD at 0% rate — not as "
  "exempt. The difference between zero-rated and exempt: zero-rated sales appear on "
  "the VAT return and allow you to reclaim input VAT you paid. Exempt sales are not "
  "shown for VAT purposes and don't allow input VAT reclaim. The EFD must have "
  "software that can distinguish between zero-rated, exempt, and standard-rated.",
  TRA_VAT, TRA_VAT_N, GP, "2015-07-01", ANN, "TRA EFD categorisation update",
  "formal", "disambiguation"),

p("tier1a_efd_215_20260609","efd_compliance",
  "Biashara inaweza kudai VAT ya pembejeo (input VAT) bila risiti ya EFD ya "
  "muuzaji Tanzania?",
  "Kwa ujumla, TRA inashikilia kwamba kudai input VAT kunahitaji risiti halisi ya "
  "EFD au ankara ya VAT iliyotolewa na muuzaji aliyesajili VAT. Bila risiti ya EFD "
  "au ankara halisi ya VAT, madai ya input VAT yanaweza kukataliwa na TRA wakati "
  "wa ukaguzi. Hifadhi risiti zote za EFD na ankara za VAT kutoka kwa wasambazaji "
  "wako kwa angalau miaka 5.",
  "Can a business claim input VAT without an EFD receipt from the supplier in Tanzania?",
  "Generally, TRA requires that claiming input VAT be supported by a genuine EFD "
  "receipt or a VAT invoice issued by a VAT-registered supplier. Without an EFD "
  "receipt or genuine VAT invoice, input VAT claims can be rejected by TRA during "
  "audit. Keep all EFD receipts and VAT invoices from your suppliers for at least "
  "5 years.",
  TRA_VAT, TRA_VAT_N, GP, "2015-07-01", ANN, "TRA input VAT or EFD evidence update",
  "formal", "standard"),

p("tier1a_efd_216_20260609","efd_compliance",
  "Msimbo wa QR code kwenye risiti ya EFD Tanzania — inamaanisha nini na inatumikaje?",
  "Risiti za EFD za Tanzania zinaweza kuwa na msimbo wa QR code unaomruhusu mteja "
  "au mkaguzi wa TRA kuthibitisha uhalali wa risiti moja kwa moja. Kwa kutumia "
  "simu ya mkononi au programu ya TRA, unaweza kuscan QR code na kupata: taarifa "
  "za muamala, TIN ya biashara, tarehe na kiasi, na uthibitisho kwamba risiti "
  "imesajiliwa kwenye mfumo wa TRA. Hii inasaidia kupambana na risiti za bandia.",
  "The QR code on a Tanzania EFD receipt — what does it mean and how is it used?",
  "Tanzania EFD receipts can have a QR code that allows a customer or TRA inspector "
  "to verify the receipt's authenticity directly. Using a mobile phone or TRA app, "
  "you can scan the QR code to get: transaction details, business TIN, date and "
  "amount, and confirmation that the receipt is registered in TRA's system. This "
  "helps combat fake receipts.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA EFD QR code or verification system update",
  "business_market", "standard"),

p("tier1a_efd_217_20260609","efd_compliance",
  "EFD ya zamani (model ya zamani) inaweza kubadilishwa na EFD mpya — ni lazima "
  "kusajili tena?",
  "Ndiyo. Ikiwa unabadilisha EFD machine na machine mpya, lazima: (1) fungua EFD "
  "ya zamani rasmi kupitia mfumo wa TRA na msambazaji wako, (2) sajili EFD mpya "
  "kwa biashara yako na TIN yako, (3) uhakikishe data ya zamani imehamishwa ipasavyo "
  "au imehifadhiwa. Usianza tu kutumia EFD mpya bila kufunga ya zamani na kusajili "
  "mpya — hii ni ukiukwaji wa mfumo wa TRA.",
  "An old EFD machine is being replaced with a new one — must it be re-registered?",
  "Yes. When you replace an EFD machine with a new one, you must: (1) formally close "
  "the old EFD through the TRA system and your supplier, (2) register the new EFD "
  "to your business and TIN, (3) ensure old data is properly transferred or preserved. "
  "Do not simply start using a new EFD without closing the old one and registering "
  "the new one — this is a violation of TRA's system.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA EFD replacement procedure update",
  "formal", "standard"),

p("tier1a_efd_218_20260609","efd_compliance",
  "Hoteli au mgahawa Tanzania inahitaji EFD maalum tofauti na maduka ya rejareja?",
  "Hospitality sector (hoteli, mikahawa) inaweza kuhitaji aina maalum ya EFD "
  "inayoweza kushughulikia bidhaa nyingi (menu items), meza tofauti, na tipping. "
  "Hata hivyo, msingi wa kisheria ni sawa — EFD iliyoidhinishwa na TRA, "
  "iliyosajiliwa kwa TIN ya biashara, inayotoa risiti za EFD. TRA inatoa "
  "mwongozo mahususi kwa hospitality sector. Angalia msambazaji wako wa EFD kwa "
  "suluhisho la hospitality.",
  "Does a hotel or restaurant in Tanzania need a special EFD different from retail shops?",
  "The hospitality sector (hotels, restaurants) may need a specialised EFD that can "
  "handle multiple products (menu items), different tables, and tipping. However, "
  "the legal basis is the same — a TRA-approved EFD, registered to the business TIN, "
  "issuing EFD receipts. TRA provides specific guidance for the hospitality sector. "
  "Check your EFD supplier for hospitality solutions.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA EFD sector guidance update",
  "business_market", "standard"),

p("tier1a_efd_219_20260609","efd_compliance",
  "Risiti ya EFD lazima itolewa kwa manunuzi yote — ikiwa ni pamoja na manunuzi "
  "madogo ya TZS 500 Tanzania?",
  "Ndiyo. Sheria ya EFD inaitaji risiti itolewe kwa kila muamala bila kujali kiasi "
  "chake. Hata kwa nunuzi ndogo ya TZS 500, biashara iliyolazimika kutumia EFD "
  "lazima itoe risiti ya EFD. Hakuna kizingiti cha chini cha kiasi ambacho "
  "kinakuruhusu kutotoa risiti ya EFD.",
  "Must an EFD receipt be issued for all purchases — including small purchases "
  "of TZS 500 in Tanzania?",
  "Yes. EFD law requires a receipt to be issued for every transaction regardless "
  "of amount. Even for a small TZS 500 purchase, a business required to use an EFD "
  "must issue an EFD receipt. There is no minimum amount threshold that allows "
  "you to skip issuing an EFD receipt.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA EFD receipt threshold update",
  "rural_conversational", "standard"),

p("tier1a_efd_220_20260609","efd_compliance",
  "Biashara inayopokea malipo ya awali (deposit/advance) inatoa risiti ya EFD "
  "wakati wa kupokea deposit au wakati wa kukamilisha mauzo Tanzania?",
  "Kwa ujumla, risiti ya EFD inapaswa kutolewa WAKATI WA KUPOKEA malipo — ikiwa ni "
  "pamoja na deposit ya awali. Kila kiasi kinachoingia biashara kama malipo ya "
  "bidhaa au huduma kinapaswa kurekodiwa kwenye EFD wakati kinapopokelewa. "
  "Kusubiri mpaka kukamilisha mauzo yote kabla ya kutoa risiti ya EFD kunaweza "
  "kuwa kosa la muda wa risiti.",
  "A business receiving advance payment (deposit) — is the EFD receipt issued at "
  "the time of receiving the deposit or at the time of completing the sale?",
  "Generally, an EFD receipt should be issued AT THE TIME OF RECEIVING payment — "
  "including an advance deposit. Every amount entering the business as payment for "
  "goods or services should be recorded on the EFD when received. Waiting until "
  "the full sale is complete before issuing an EFD receipt may be a receipt timing "
  "error.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA EFD receipt timing guidance update",
  "formal", "standard"),

p("tier1a_efd_221_20260609","efd_compliance",
  "Tofauti kati ya ankara ya VAT (VAT invoice) na risiti ya EFD Tanzania ni nini?",
  "Ankara ya VAT (VAT invoice) na risiti ya EFD ni nyaraka tofauti lakini zinaweza "
  "kufanya kazi pamoja: Risiti ya EFD ni uthibitisho wa malipo uliotolewa na mashine "
  "ya EFD. Ankara ya VAT ni hati ya biashara inayoonyesha maelezo ya bidhaa/huduma, "
  "kiasi cha VAT, na TIN za pande zote — inahitajika kwa madai ya input VAT. "
  "Biashara nyingi zinatoa risiti ya EFD NA ankara ya VAT pamoja kwa wateja wa "
  "biashara (B2B). Kwa wateja wa kawaida (B2C), risiti ya EFD inatosha.",
  "What is the difference between a VAT invoice and an EFD receipt in Tanzania?",
  "A VAT invoice and an EFD receipt are different documents but can work together: "
  "An EFD receipt is proof of payment issued by the EFD machine. A VAT invoice is "
  "a commercial document showing details of goods/services, VAT amount, and both "
  "parties' TINs — required for input VAT claims. Most businesses issue both an EFD "
  "receipt AND a VAT invoice together for business customers (B2B). For regular "
  "customers (B2C), the EFD receipt is sufficient.",
  TRA_VAT, TRA_VAT_N, GP, "2015-07-01", ANN, "TRA EFD or VAT invoice requirement update",
  "business_market", "disambiguation"),

p("tier1a_efd_222_20260609","efd_compliance",
  "EFD machine ya Tanzania inahitaji mtandao wa intaneti kufanya kazi?",
  "EFD machines nyingi za Tanzania zinaweza kufanya kazi bila mtandao kwa muda mfupi "
  "na zinahifadhi data za muamala kwenye mashine. Lakini zinahitaji muunganisho wa "
  "mtandao (internet/SIM card) mara kwa mara ili: (1) kupeleka data ya muamala "
  "kwenye seva ya TRA, (2) kupata masasisho ya mfumo. EFD isiyopeleka data kwa TRA "
  "kwa muda mrefu inaweza kukiuka sheria — angalia mwongozo wa msambazaji wako "
  "kuhusu mahitaji ya muunganisho.",
  "Does a Tanzania EFD machine need an internet connection to work?",
  "Most Tanzania EFD machines can operate offline briefly and store transaction data "
  "on the machine. But they need periodic internet/SIM connection to: (1) transmit "
  "transaction data to TRA's server, (2) receive system updates. An EFD that does "
  "not transmit data to TRA for a long period may be in violation — check your "
  "supplier's guidance on connectivity requirements.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA EFD connectivity requirement update",
  "business_market", "standard"),

p("tier1a_efd_223_20260609","efd_compliance",
  "Biashara inayofanya mauzo ya jumla (wholesale) kwa makampuni mengine tu — "
  "inahitaji EFD Tanzania?",
  "Biashara za jumla (wholesale) pia zinaweza kulazimishwa kutumia EFD Tanzania, "
  "hasa ikiwa zimesajili VAT. Hata kama wateja wote ni biashara nyingine (B2B), "
  "EFD bado inahitajika kwa muamala wote. Ankara za VAT zinazoandikwa mkono au "
  "kwa kompyuta bila EFD hazikubaliwi kama mbadala wa EFD bila ruhusa maalum "
  "ya TRA.",
  "A business selling wholesale only to other companies — does it need an EFD "
  "in Tanzania?",
  "Wholesale businesses can also be required to use an EFD in Tanzania, especially "
  "if VAT-registered. Even if all customers are other businesses (B2B), an EFD is "
  "still required for all transactions. Handwritten or computer-printed VAT invoices "
  "without an EFD are not accepted as an EFD substitute without special TRA permission.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA EFD wholesale sector update",
  "formal", "standard"),

p("tier1a_efd_224_20260609","efd_compliance",
  "EFD inaathiri vipi tathmini ya VAT ya TRA — TRA inaweza kuona mauzo ya moja "
  "kwa moja?",
  "Ndiyo. Mfumo wa EFD unaruhusu TRA kuona data ya mauzo ya biashara MOJA KWA MOJA "
  "na kwa wakati halisi. Hii inamaanisha: (1) TRA inaweza kulinganisha data ya "
  "EFD na tamko la VAT lililowasilishwa, (2) tofauti kubwa kati ya data ya EFD na "
  "tamko inaweza kusababisha ukaguzi moja kwa moja, (3) biashara zinazojaribu "
  "kudanganya kwenye mauzo zikijua EFD ipo zinachukua hatari kubwa sana ya "
  "kugunduliwa na TRA.",
  "How does an EFD affect TRA's VAT assessment — can TRA see sales directly?",
  "Yes. The EFD system allows TRA to see business sales data DIRECTLY and in real "
  "time. This means: (1) TRA can compare EFD data against the filed VAT return, "
  "(2) a large discrepancy between EFD data and the return can trigger an automatic "
  "audit, (3) businesses that try to understate sales knowing an EFD is present "
  "take a very high risk of being detected by TRA.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA EFD real-time data system update",
  "formal", "standard"),

p("tier1a_efd_225_20260609","efd_compliance",
  "EFD machine inaweza kufutwa (cancelled) kwenye mfumo wa TRA — biashara "
  "inafanya hivyo lini?",
  "EFD machine inafutwa kwenye mfumo wa TRA katika hali hizi: (1) biashara "
  "inafunga kabisa, (2) biashara inafunga tawi husika, (3) machine inapokelewa "
  "mbaya isiyoweza kukarabatiwa, (4) biashara inabadilisha EFD mpya. Mchakato "
  "wa kufuta lazima ufuate mwongozo wa TRA na msambazaji. Biashara KAMWE "
  "isifute EFD bila kupata uthibitisho wa TRA na data ya mwisho kutolewa ipasavyo.",
  "An EFD machine can be deactivated on TRA's system — when does a business do this?",
  "An EFD machine is deactivated on TRA's system in these situations: (1) the business "
  "is closing permanently, (2) a specific branch is closing, (3) the machine is "
  "irreparably damaged, (4) the business is replacing it with a new EFD. The "
  "deactivation process must follow TRA and supplier guidance. A business must "
  "NEVER deactivate an EFD without TRA confirmation and final data properly extracted.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA EFD deactivation procedure update",
  "formal", "standard"),

p("tier1a_efd_226_20260609","efd_compliance",
  "Biashara ya mwaka mzima inayofunga kwa wiki moja tu — lazima itoe taarifa "
  "kwa TRA kwamba EFD haitafanya kazi?",
  "Ikiwa biashara inafunga kwa muda mfupi (likizo, ukarabati wa jengo), EFD "
  "itakuwa haifanyi kazi kwa muda huo. Hii kwa kawaida si lazima kuripotiwa "
  "mapema kwa TRA ikiwa ni funga ya muda mfupi ya kawaida ya biashara. Hata hivyo, "
  "ikiwa EFD itakuwa imefungwa kwa muda mrefu, inashauriwa kuwasiliana na TRA ili "
  "kuzuia hali yoyote ya utata wa data au maswali ya ukaguzi.",
  "A year-round business closing for just one week — must it notify TRA that the "
  "EFD won't operate?",
  "If a business closes briefly (holiday, building renovation), the EFD will be "
  "inactive for that period. This is generally not required to be pre-reported to "
  "TRA if it is an ordinary short business closure. However, if the EFD will be "
  "inactive for a long period, it is advisable to contact TRA to prevent any data "
  "anomaly or audit queries.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA EFD inactive period guidance update",
  "business_market", "standard"),

p("tier1a_efd_227_20260609","efd_compliance",
  "Biashara ya usafirishaji (taxi, bodaboda) inahitaji EFD Tanzania?",
  "Biashara za usafirishaji wa abiria kama bodaboda na taxi zimekuwa nje ya "
  "listi ya lazima ya EFD kwa kawaida — hasa kwa madereva wa kujitegemea wenye "
  "mauzo madogo. Hata hivyo, kampuni kubwa za usafirishaji zilizosajili VAT au "
  "zile TRA zilizotamua lazima zitumie EFD. Angalia TRA moja kwa moja kwa "
  "ufafanuzi wa hali yako ya biashara ya usafirishaji.",
  "Does a transport business (taxi, bodaboda) need an EFD in Tanzania?",
  "Passenger transport businesses like bodaboda and taxis have generally been "
  "outside the mandatory EFD list — especially for independent drivers with small "
  "turnover. However, large transport companies that are VAT-registered or those "
  "directed by TRA must use an EFD. Check TRA directly for clarification for your "
  "specific transport business situation.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA EFD transport sector update",
  "rural_conversational", "standard"),

p("tier1a_efd_228_20260609","efd_compliance",
  "EFD inahitajika kwa biashara ya kulipwa kwa huduma za kitaalamu Tanzania — "
  "kama daktari au wakili?",
  "Watoa huduma za kitaalamu (madaktari, mawakili, wahasibu) wanaofanya mazoezi "
  "kama biashara na wamesajili VAT wanaweza kulazimishwa kutumia EFD. Hata "
  "bila VAT, TRA inaweza kutamua aina za biashara za kitaalamu lazima zitumie EFD. "
  "Kwa watoa huduma wadogo wa kitaalamu, angalia TRA kwa orodha ya sekta "
  "zinazolazimika sasa hivi.",
  "Is an EFD required for professional service businesses in Tanzania — such as "
  "doctors or lawyers?",
  "Professional service providers (doctors, lawyers, accountants) practising as a "
  "business who are VAT-registered can be required to use an EFD. Even without VAT, "
  "TRA can designate professional business types as mandatory EFD users. For small "
  "professional service providers, check TRA for the current list of mandatory sectors.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA EFD professional services update",
  "formal", "standard"),

p("tier1a_efd_229_20260609","efd_compliance",
  "EFD inatumika kwa mauzo ya bidhaa zilizo huru ya VAT (exempt) Tanzania — "
  "au EFD ni kwa mauzo ya VAT tu?",
  "EFD inatumika kwa mauzo YOTE ya biashara iliyolazimika kutumia EFD — ikiwa ni "
  "pamoja na mauzo ya bidhaa zilizo huru ya VAT (exempt) na mauzo ya kiwango cha "
  "sifuri (zero-rated). Biashara lazima iingie muamala wote kwenye EFD na "
  "iuainishe ipasavyo (standard rate, zero-rated, exempt). Kuchagua tu mauzo "
  "ya VAT kwenye EFD na kuacha mauzo ya exempt ni kosa la uzingatiaji wa EFD.",
  "Is an EFD used for exempt VAT sales in Tanzania — or is an EFD only for VAT sales?",
  "An EFD is used for ALL sales of a business required to use an EFD — including "
  "exempt VAT sales and zero-rated sales. The business must enter all transactions "
  "in the EFD and categorise them correctly (standard rate, zero-rated, exempt). "
  "Entering only VAT sales in the EFD and leaving out exempt sales is an EFD "
  "compliance error.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA EFD categorisation or compliance update",
  "formal", "adversarial"),

p("tier1a_efd_230_20260609","efd_compliance",
  "Biashara inaweza kukata mwajiriwa wake kama msimamizi wa EFD — "
  "mwajiriwa huyo atawajibika kwa makosa ya EFD?",
  "Mwajiri ana jukumu kuu la kisheria la kuhakikisha EFD inatumika vizuri — "
  "jukumu hili haliwezi kuhamishwa kabisa kwa mwajiriwa. Hata kama mwajiriwa "
  "fulani ameteuliwa kusimamia EFD, adhabu za TRA kwa makosa ya EFD zinaelekezwa "
  "kwa BIASHARA (mwajiri) si mwajiriwa mmoja mmoja. Mwajiri ana wajibu wa "
  "kuhakikisha mafunzo mazuri ya wafanyakazi na mifumo ya ufuatiliaji wa ndani.",
  "A business can appoint an employee as EFD supervisor — will that employee be "
  "responsible for EFD errors?",
  "The employer has the primary legal responsibility to ensure the EFD is used "
  "correctly — this responsibility cannot be fully transferred to an employee. Even "
  "if a specific employee is appointed to supervise the EFD, TRA penalties for EFD "
  "violations are directed at the BUSINESS (employer) not an individual employee. "
  "The employer has a duty to ensure proper staff training and internal monitoring "
  "systems.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA EFD liability update",
  "formal", "standard"),

p("tier1a_efd_231_20260609","efd_compliance",
  "Biashara ya Tanzania inaweza kuomba EFD maalum ya kupokea malipo ya kadi "
  "za benki (POS terminal) inayofanya kazi kama EFD pia?",
  "Baadhi ya suluhisho za kisasa za POS (point of sale) zinazounganisha EFD na "
  "malipo ya kadi zinaweza kukubalika na TRA kama mfumo mmoja. Hata hivyo, "
  "mfumo huo lazima uidhiniwe rasmi na TRA. POS terminal ya benki peke yake "
  "(bila idhini ya TRA kama EFD) haiwezi kutumika kama mbadala wa EFD. "
  "Angalia TRA na msambazaji wako kwa mifumo ya pamoja ya POS+EFD.",
  "Can a Tanzania business apply for a special EFD that also accepts bank card "
  "payments (POS terminal) working as an EFD too?",
  "Some modern POS solutions that combine EFD and card payment acceptance may be "
  "acceptable to TRA as a single system. However, such a system must be formally "
  "TRA-approved. A bank POS terminal alone (without TRA approval as an EFD) cannot "
  "serve as an EFD substitute. Check TRA and your supplier for combined POS+EFD "
  "systems.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA EFD integrated POS approval update",
  "business_market", "standard"),

p("tier1a_efd_232_20260609","efd_compliance",
  "Biashara inayotumia EFD haitahitaji kuwasilisha tamko la VAT kwa TRA kwa "
  "sababu EFD inapeleka data moja kwa moja — je, hii ni sahihi?",
  "Hapana. EFD inashiriki data ya mauzo na TRA kwa wakati halisi, lakini hii "
  "HAIONDOI wajibu wa biashara wa kuwasilisha tamko la VAT rasmi kila mwezi. "
  "Tamko la VAT bado linahitajika kuwasilishwa ndani ya tarehe 20 ya kila mwezi. "
  "EFD data ni rasilimali ya TRA ya ukaguzi — si mbadala wa tamko rasmi la VAT "
  "lililothibitishwa na biashara.",
  "A business using an EFD will not need to file a VAT return with TRA because the "
  "EFD sends data directly — is this correct?",
  "No. The EFD shares sales data with TRA in real time, but this does NOT eliminate "
  "the business's obligation to file a formal VAT return monthly. A VAT return must "
  "still be filed by the 20th of each month. EFD data is TRA's audit resource — it "
  "is not a substitute for a formal VAT return confirmed by the business.",
  TRA_VAT, TRA_VAT_N, GP, "2015-07-01", ANN, "TRA EFD and VAT return dual obligation update",
  "business_market", "adversarial"),

p("tier1a_efd_233_20260609","efd_compliance",
  "EFD inasaidia biashara kuhesabu jumla ya VAT inayodaiwa kwa wateja "
  "au inalipwa kwa wasambazaji Tanzania vipi?",
  "EFD inasaidia kwa mwelekeo mmoja wa VAT — inahesabu OUTPUT VAT (VAT "
  "inayodaiwa kwa wateja kwenye mauzo). Kwa INPUT VAT (VAT inayolipwa kwa "
  "wasambazaji kwenye manunuzi), biashara lazima ihifadhi risiti za EFD na ankara "
  "za VAT za wasambazaji wake na kuziingiza kwenye tamko lake la VAT la kila mwezi. "
  "EFD ya biashara yako HAIREKORDI manunuzi yako — unahitaji mfumo wa akaunti "
  "wa ndani kwa hilo.",
  "How does an EFD help a business calculate total VAT charged to customers or paid "
  "to suppliers in Tanzania?",
  "An EFD helps with one direction of VAT — it calculates OUTPUT VAT (VAT charged "
  "to customers on sales). For INPUT VAT (VAT paid to suppliers on purchases), the "
  "business must keep EFD receipts and VAT invoices from its suppliers and enter "
  "them in its monthly VAT return. Your business EFD does NOT record your purchases "
  "— you need an internal accounting system for that.",
  TRA_VAT, TRA_VAT_N, GP, "2015-07-01", ANN, "TRA EFD VAT accounting guidance update",
  "formal", "standard"),

p("tier1a_efd_234_20260609","efd_compliance",
  "Biashara ya mkoba mdogo ya Kariakoo — ikiwa inafanya mauzo ya TZS 30M kwa mwaka "
  "tu — je, inahitaji EFD?",
  "Biashara yenye mauzo ya TZS 30M kwa mwaka iko chini ya kizingiti cha VAT cha "
  "TZS 200M. Kwa hivyo, HAIHITAJIKI kusajili VAT. Ikiwa haijasajili VAT na TRA "
  "haijaitambua kwa amri maalum ya EFD, biashara hiyo HAIHITAJIKI kuwa na EFD. "
  "Hata hivyo, ikiwa sekta yake imo kwenye orodha ya TRA ya sekta zinazolazimika "
  "kutumia EFD bila kujali mauzo, basi EFD inahitajika. Angalia TRA na sekta yako.",
  "A small bag seller in Kariakoo making only TZS 30M sales per year — do they "
  "need an EFD?",
  "A business with TZS 30M annual sales is below the VAT threshold of TZS 200M. "
  "Therefore, it is NOT required to register for VAT. If not VAT-registered and TRA "
  "has not designated it with a specific EFD directive, that business is NOT required "
  "to have an EFD. However, if its sector is on TRA's list of sectors required to "
  "use EFD regardless of sales, then an EFD is required. Check TRA and your sector.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA EFD threshold and sector mandate update",
  "rural_conversational", "standard"),

p("tier1a_efd_235_20260609","efd_compliance",
  "Biashara inayoombwa na mteja wake wa biashara kutoa ankara ya VAT — "
  "lazima itoe EFD receipt pia au ankara ya VAT inatosha?",
  "Biashara iliyolazimika kutumia EFD lazima itoe risiti ya EFD kwa kila muamala "
  "bila kujali ikiwa mteja anataka ankara ya VAT pia. Kwa wateja wa biashara (B2B) "
  "wanaodai input VAT, biashara inaweza kutoa ZOTE MBILI: risiti ya EFD NA ankara "
  "ya VAT inayoonyesha TIN za pande zote na maelezo ya bidhaa/huduma. Risiti ya "
  "EFD peke yake inaweza isiwe na maelezo ya kutosha kwa madai ya input VAT.",
  "A business asked by its business customer for a VAT invoice — must it also issue "
  "an EFD receipt or is the VAT invoice enough?",
  "A business required to use an EFD must issue an EFD receipt for every transaction "
  "regardless of whether the customer also wants a VAT invoice. For business customers "
  "(B2B) claiming input VAT, the business can issue BOTH: an EFD receipt AND a VAT "
  "invoice showing both parties' TINs and goods/service details. An EFD receipt alone "
  "may not have sufficient detail for input VAT claims.",
  TRA_VAT, TRA_VAT_N, GP, "2015-07-01", ANN, "TRA EFD and VAT invoice dual-document update",
  "formal", "standard"),

p("tier1a_efd_236_20260609","efd_compliance",
  "EFD inahusiana na mfumo wa TIMS (Tanzania Integrated Management System) wa "
  "TRA vipi?",
  "TIMS (Tanzania Integrated Management System) ni mfumo mkuu wa usimamizi wa "
  "kodi wa TRA unaounganisha taarifa nyingi za kodi. EFD inaunganishwa na TIMS "
  "kwa kupeleka data ya mauzo moja kwa moja. Hii inaruhusu TRA kulinganisha data "
  "ya EFD na: tamko la VAT lililowasilishwa, PAYE, na kodi nyingine, katika mfumo "
  "mmoja wa ufuatiliaji wa uzingatiaji. Makampuni yenye EFD yanaonekana zaidi "
  "kwenye mfumo wa TRA kuliko biashara zisizo na EFD.",
  "How does an EFD relate to TRA's TIMS (Tanzania Integrated Management System)?",
  "TIMS (Tanzania Integrated Management System) is TRA's central tax management "
  "system that integrates multiple tax data sources. An EFD connects to TIMS by "
  "transmitting sales data directly. This allows TRA to cross-reference EFD data "
  "against: filed VAT returns, PAYE, and other taxes, within one compliance tracking "
  "system. Companies with EFDs are more visible in TRA's system than businesses "
  "without EFDs.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA TIMS or EFD integration update",
  "formal", "standard"),

p("tier1a_efd_237_20260609","efd_compliance",
  "Biashara inayofanya rejareja ya dawa (pharmacy) Tanzania inahitaji aina "
  "maalum ya EFD?",
  "Maduka ya dawa (pharmacy) Tanzania yanayofanya mauzo ya dawa lazima yatumie "
  "EFD kama biashara nyingine zilizolazimishwa. Bidhaa za dawa fulani zinaweza "
  "kuwa huru ya VAT (exempt) au za kiwango cha sifuri — EFD lazima iwe na "
  "programu inayoweza kuuainisha kwa usahihi. Pia, pharmacy inaweza kuhitaji "
  "leseni maalum ya TMDA mbali na EFD ya TRA. Angalia TRA na TMDA kwa mahitaji "
  "yote yanayohusika.",
  "Does a pharmaceutical retail business (pharmacy) in Tanzania need a special "
  "type of EFD?",
  "Pharmacies in Tanzania making medicine sales must use an EFD like other mandatory "
  "businesses. Certain pharmaceutical products may be VAT-exempt or zero-rated — "
  "the EFD must have software that can correctly categorise them. Also, a pharmacy "
  "may need a specific TMDA licence separate from TRA's EFD. Check TRA and TMDA "
  "for all applicable requirements.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA EFD pharmacy or TMDA sector update",
  "formal", "standard"),

p("tier1a_efd_238_20260609","efd_compliance",
  "Msimbo wa kurudisha bidhaa (return/refund) kwenye EFD Tanzania unafanyaje?",
  "Ikiwa mteja anarudisha bidhaa na biashara lazima imrudishie pesa, EFD ina "
  "utaratibu maalum wa kurekodi muamala wa kurudi (credit note/return transaction). "
  "Hii inapunguza jumla ya mauzo na VAT iliyorekodiwa kwa kipindi hicho. KAMWE "
  "usifute muamala uliokwisha fanywa — tumia utaratibu wa credit note wa EFD. "
  "Kufuta muamala badala ya kutumia credit note ni kosa la uzingatiaji wa EFD.",
  "How is a product return/refund handled on an EFD in Tanzania?",
  "If a customer returns goods and the business must refund them, the EFD has a "
  "specific procedure to record the return transaction (credit note/return transaction). "
  "This reduces the total sales and VAT recorded for that period. NEVER delete a "
  "completed transaction — use the EFD's credit note procedure. Deleting a transaction "
  "instead of using a credit note is an EFD compliance error.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA EFD return procedure update",
  "formal", "standard"),

p("tier1a_efd_239_20260609","efd_compliance",
  "EFD inaweza kusaidia kupambana na wizi wa wafanyakazi (staff theft) kwenye "
  "biashara ya rejareja Tanzania?",
  "Ndiyo, kwa njia fulani. EFD inarekodia kila muamala na inaweza kuonyesha "
  "takwimu za mauzo kwa kila kasher au saa. Meneja anaweza kulinganisha mauzo "
  "ya EFD na stoo iliyokuwepo ili kutambua tofauti. Hata hivyo, EFD imeundwa "
  "kwa madhumuni ya kodi ya TRA — si mfumo wa kudhibiti wizi hasa. Biashara "
  "zinazohitaji udhibiti mkali wa ulinzi wa ndani zinapaswa kutumia mifumo "
  "ya akaunti ya ndani ya ziada.",
  "Can an EFD help prevent staff theft in a retail business in Tanzania?",
  "Yes, to some extent. An EFD records every transaction and can show sales figures "
  "per cashier or per hour. A manager can compare EFD sales against stock held to "
  "identify discrepancies. However, the EFD is designed for TRA tax purposes — "
  "not specifically as a theft control system. Businesses needing strict internal "
  "security controls should use additional internal accounting systems.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA EFD system capability",
  "business_market", "standard"),

p("tier1a_efd_240_20260609","efd_compliance",
  "Biashara mpya iliyosajili VAT ina muda gani wa kupata na kusajili EFD Tanzania?",
  "Biashara inayosajili VAT Tanzania inapaswa kupata na kusajili EFD haraka "
  "iwezekanavyo — kwa kawaida ndani ya muda mfupi wa kuanza kufanya mauzo ya "
  "VAT. TRA inaweza kutoa mwongozo mahususi wa muda wa kupata EFD baada ya "
  "usajili wa VAT. Kufanya mauzo ya VAT bila EFD (baada ya kulazimishwa) "
  "ni ukiukwaji wa sheria ya VAT na EFD.",
  "A new VAT-registered business — how much time does it have to obtain and "
  "register an EFD in Tanzania?",
  "A business registering for VAT in Tanzania should obtain and register an EFD "
  "as quickly as possible — generally within a short period of starting to make "
  "VAT sales. TRA may provide specific timing guidance on EFD acquisition after "
  "VAT registration. Making VAT sales without an EFD (after being required to) "
  "is a violation of VAT and EFD law.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA EFD registration deadline update",
  "business_market", "standard"),

p("tier1a_efd_241_20260609","efd_compliance",
  "EFD ina tofauti gani na mfumo wa POS wa kawaida wa kompyuta wa duka?",
  "POS (Point of Sale) ya kawaida ya kompyuta ni mfumo wa biashara wa ndani "
  "unaosaidia kusimamia mauzo, stoo, na wateja — lakini haupeleki data moja kwa "
  "moja kwa TRA. EFD ni kifaa kilichoidhinishwa na TRA kinachounganishwa moja kwa "
  "moja na mfumo wa TRA na kurekodia data ya kodi. Biashara nyingi zinatumia "
  "mifumo MIWILI: POS ya biashara kwa usimamizi wa biashara, NA EFD ya TRA kwa "
  "uzingatiaji wa kodi.",
  "What is the difference between an EFD and a regular computer POS system in a shop?",
  "A regular computer POS (Point of Sale) is an internal business system that helps "
  "manage sales, stock, and customers — but it does not transmit data directly to "
  "TRA. An EFD is a TRA-approved device connected directly to TRA's system that "
  "records tax data. Many businesses use TWO systems: a business POS for business "
  "management, AND a TRA EFD for tax compliance.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA EFD vs POS clarification",
  "business_market", "disambiguation"),

p("tier1a_efd_242_20260609","efd_compliance",
  "EFD inaweza kutumika nje ya majengo ya biashara — kama kwa wafanyabiashara "
  "wa soko la nje au mauzo ya nyumba kwa nyumba?",
  "TRA ina aina za EFD za portable (zinazobebeka) zinazofaa kwa: wafanyabiashara "
  "wa soko la nje (outdoor markets), mauzo ya nyumba kwa nyumba, na biashara za "
  "mkononi. EFD za portable zinahitaji muunganisho wa SIM/data kufanya kazi. "
  "Mauzo ya mkononi na ya soko bado yanalazimishwa na sheria za EFD ikiwa biashara "
  "iko kwenye orodha ya lazima.",
  "Can an EFD be used outside business premises — such as for outdoor market "
  "traders or door-to-door sales?",
  "TRA has portable EFD types suitable for: outdoor market traders, door-to-door "
  "sales, and mobile businesses. Portable EFDs require a SIM/data connection to "
  "function. Mobile and market sales are still subject to EFD law if the business "
  "is on the mandatory list.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA portable EFD update",
  "business_market", "standard"),

p("tier1a_efd_243_20260609","efd_compliance",
  "EFD inaweza kuratibu mifumo miwili ya VAT — standard rate (18%) na zero-rated "
  "(0%) — kwenye muamala mmoja Tanzania?",
  "Ndiyo. EFD za kisasa ziliweza kushughulikia muamala mmoja wenye bidhaa za aina "
  "tofauti za VAT — kwa mfano, duka linalouza bidhaa za 18% na bidhaa za zero-rated "
  "pamoja. EFD inakokotoa VAT ya kila bidhaa kulingana na kategoria yake na "
  "kuonyesha muhtasari wa risiti na jumla ya VAT inayohusika. Weka programu ya "
  "EFD iliyosasishwa ili kushughulikia aina zote za VAT.",
  "Can an EFD handle two VAT rates — standard rate (18%) and zero-rated (0%) — "
  "on one transaction in Tanzania?",
  "Yes. Modern EFDs can handle a single transaction with goods of different VAT "
  "types — for example, a shop selling 18% goods and zero-rated goods together. "
  "The EFD calculates VAT for each item according to its category and shows a receipt "
  "summary with the applicable total VAT. Keep EFD software updated to handle all "
  "VAT categories.",
  TRA_VAT, TRA_VAT_N, GP, "2015-07-01", ANN, "TRA EFD multi-rate capability update",
  "formal", "standard"),

p("tier1a_efd_244_20260609","efd_compliance",
  "EFD inaathiriwa na mabadiliko ya VAT ya asilimia 16 ya mauzo ya kidijitali "
  "B2C iliyoanza Septemba 2025 Tanzania?",
  "B2C e-payment VAT ya asilimia 16 (ikilinganishwa na kiwango cha kawaida cha 18%) "
  "ni utaratibu tofauti unaohusiana na mauzo ya kidijitali. Sheria za utekelezaji "
  "bado zinasubiriwa kutoka kwa Kamishna Mkuu. Biashara za mtandaoni zinazotumia "
  "EFD lazima zifuate mwongozo wa TRA mara utakapotolewa kuhusu jinsi EFD itakavyo "
  "kushughulikia kiwango kipya cha asilimia 16 kwa muamala wa B2C.",
  "Is an EFD affected by the 16% B2C digital sales VAT that started in September "
  "2025 in Tanzania?",
  "The B2C e-payment VAT at 16% (compared to the standard 18%) is a separate "
  "arrangement related to digital sales. Implementation rules are still awaited from "
  "the Commissioner General. Online businesses using EFDs must follow TRA guidance "
  "when issued on how the EFD will handle the new 16% rate for B2C transactions.",
  TRA_VAT, TRA_VAT_N, GP, "2025-09-01", ANN, "TRA B2C e-payment VAT implementation update",
  "formal", "standard"),

p("tier1a_efd_245_20260609","efd_compliance",
  "EFD imesaidia kuongeza makusanyo ya VAT Tanzania kwa kiasi gani?",
  "TRA imerekodia ongezeko kubwa la makusanyo ya kodi tangu kuanzishwa kwa "
  "mfumo wa EFD. EFD imesaidia kupunguza ukwepaji wa VAT kwa kurekodi mauzo "
  "moja kwa moja, kupunguza utegemezi wa ripoti za mkono peke yake, na kuruhusu "
  "ukaguzi wa data kwa wakati halisi. Nchi kama Kenya (ETR) na Tanzania zimeweka "
  "mifumo ya EFD kwa sababu ya ushahidi wa kuongeza makusanyo ya VAT. Takwimu "
  "mahususi zinatoka kwenye ripoti za kila mwaka za TRA.",
  "By how much has an EFD helped increase VAT collections in Tanzania?",
  "TRA has recorded significant increases in tax collections since the introduction "
  "of the EFD system. EFDs have helped reduce VAT evasion by recording sales "
  "directly, reducing reliance on manual reports alone, and enabling real-time data "
  "auditing. Countries like Kenya (ETR) and Tanzania have implemented EFD systems "
  "based on evidence of increased VAT collection. Specific figures come from TRA's "
  "annual reports.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA annual revenue report",
  "formal", "standard"),

p("tier1a_efd_246_20260609","efd_compliance",
  "Biashara inahitaji kutunza kopi za risiti za EFD zilizotolewa — kwa muda gani?",
  "Biashara lazima ihifadhi kopi za data ya EFD (au rekodi za muamala) kwa miaka "
  "MITANO (5) kulingana na mahitaji ya kuhifadhi rekodi za TRA. EFD yenyewe "
  "inaweza kuhifadhi data kwa muda fulani wa ndani, lakini inashauriwa pia "
  "kuhifadhi nakala za nje kwa usalama (backup). Rekodi hizi ni muhimu ikiwa "
  "EFD yenyewe itaharibika au wakati wa ukaguzi wa TRA.",
  "Does a business need to keep copies of EFD receipts issued — for how long?",
  "A business must keep copies of EFD data (or transaction records) for FIVE (5) "
  "years in line with TRA record-keeping requirements. The EFD itself may store data "
  "internally for some period, but it is also advisable to keep external backup "
  "copies securely. These records are critical if the EFD itself malfunctions or "
  "during a TRA audit.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA EFD record retention update",
  "formal", "standard"),

p("tier1a_efd_247_20260609","efd_compliance",
  "Biashara inayofanya mauzo ya rejareja tu kwa pesa taslimu (hakuna kadi, "
  "hakuna mobile money) bado inahitaji EFD Tanzania?",
  "Njia ya malipo (pesa taslimu, kadi, mobile money) HAIATHIRI wajibu wa EFD. "
  "EFD inahitajika kwa biashara zilizolazimishwa bila kujali wateja wanalipa vipi. "
  "Biashara ya rejareja inayofanya mauzo yote kwa pesa taslimu tu bado lazima "
  "itoe risiti ya EFD kwa kila muamala ikiwa iko kwenye orodha ya lazima ya TRA.",
  "A business that only makes retail cash sales (no cards, no mobile money) — does "
  "it still need an EFD in Tanzania?",
  "The payment method (cash, card, mobile money) does NOT affect the EFD obligation. "
  "An EFD is required for mandated businesses regardless of how customers pay. A "
  "retail business making all sales in cash still must issue an EFD receipt for "
  "every transaction if it is on TRA's mandatory list.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA EFD cash business update",
  "rural_conversational", "adversarial"),

p("tier1a_efd_248_20260609","efd_compliance",
  "Msambazaji wa EFD aliyeidhinishwa na TRA ana jukumu gani ikiwa EFD haitafanya "
  "kazi vizuri?",
  "Msambazaji aliyeidhinishwa na TRA ana majukumu ya: (1) kutoa EFD iliyoidhinishwa "
  "na kusajiliwa vizuri kwenye mfumo wa TRA, (2) kutoa mafunzo ya kuitumia, "
  "(3) kutoa huduma ya ukarabati wa haraka pale EFD inapoharibika, (4) kushughulikia "
  "matatizo ya muunganisho wa data kwa TRA. Ikiwa msambazaji hakufanya kazi "
  "vizuri, biashara inaweza kulalamika kwa TRA. Hata hivyo, mwajiri/biashara "
  "bado ana wajibu wa kuhakikisha EFD inafanya kazi.",
  "What responsibility does a TRA-approved EFD supplier have if the EFD doesn't "
  "work properly?",
  "A TRA-approved supplier has responsibilities to: (1) supply an EFD properly "
  "approved and registered on TRA's system, (2) provide usage training, (3) provide "
  "prompt repair service when the EFD breaks down, (4) handle data connectivity "
  "issues to TRA. If the supplier fails, the business can complain to TRA. However, "
  "the employer/business still has the obligation to ensure the EFD works.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA EFD supplier obligation update",
  "formal", "standard"),

p("tier1a_efd_249_20260609","efd_compliance",
  "EFD inasaidia watu maskini wa Tanzania vipi — risiti za EFD zinawafaidia wananchi?",
  "Risiti za EFD zinalinda wananchi kwa njia kadhaa: (1) biashara iliyotoa risiti "
  "ya EFD inathibitisha kwamba alilipa VAT halisi na hakudanganya bei, (2) wananchi "
  "wanaweza kutumia risiti za EFD kama ushahidi wa manunuzi kwa madhumuni ya "
  "udanganyifu wa bidhaa, (3) TRA inapata mapato zaidi ya kodi ambayo yanaweza "
  "kutumiwa kwa huduma za umma. Kampeni ya TRA ya 'Omba Risiti' inawahimiza "
  "wananchi kudai risiti za EFD.",
  "How do EFDs help ordinary Tanzanians — do EFD receipts benefit citizens?",
  "EFD receipts protect citizens in several ways: (1) a business that issued an EFD "
  "receipt proves it paid the actual VAT and did not deceive on price, (2) citizens "
  "can use EFD receipts as purchase evidence for product fraud claims, (3) TRA "
  "receives more tax revenue which can be used for public services. TRA's 'Omba "
  "Risiti' (Ask for Receipt) campaign encourages citizens to demand EFD receipts.",
  TRA, TRA_N, GP, "2015-07-01", ANN, "TRA EFD public awareness campaign update",
  "rural_conversational", "standard"),

p("tier1a_efd_250_20260609","efd_compliance",
  "Biashara inayopokea ufadhili (grant) kutoka shirika la kimataifa — mpokeaji "
  "wa grant analipa VAT na anahitaji EFD Tanzania?",
  "Ufadhili (grant) kutoka shirika la kimataifa kwa kawaida si mauzo ya kibiashara "
  "yanayostahili VAT — ni mapato ya hiari, si malipo kwa bidhaa/huduma. Kwa hivyo, "
  "grant yenyewe kwa kawaida HAILIPISHI VAT wala haihitaji EFD. Hata hivyo, ikiwa "
  "shirika la kimataifa linakununulia bidhaa au huduma (yaani unauza kwake), "
  "hizo ni mauzo ya kawaida zinazostahili VAT na EFD. Angalia mwanasheria wa kodi "
  "kwa muundo maalum wa ufadhili wako.",
  "A business receiving a grant from an international organisation — does the grant "
  "recipient pay VAT and need an EFD in Tanzania?",
  "A grant from an international organisation is generally not a commercial sale "
  "subject to VAT — it is gratuitous income, not payment for goods/services. Therefore, "
  "the grant itself generally does NOT attract VAT or require an EFD. However, if "
  "the international organisation is buying goods or services from you (i.e., you "
  "are selling to them), those are regular taxable sales requiring VAT and an EFD. "
  "Consult a tax lawyer for your specific grant structure.",
  TRA_VAT, TRA_VAT_N, GP, "2025-07-01", ANN, "TRA grant VAT treatment update",
  "formal", "standard"),

]

written = 0
with open(OUT, "a", encoding="utf-8") as f:
    for pr in pairs:
        f.write(json.dumps(pr, ensure_ascii=False) + "\n")
        written += 1

total = sum(1 for _ in open(OUT, encoding="utf-8") if _.strip())
print(f"Part 5: wrote {written} pairs to {OUT}")
print(f"Total in file: {total}")
