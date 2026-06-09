#!/usr/bin/env python3
"""batch_004 part 4 — WHT deep (30 more, 011-040) + WCF compliance (20, 001-020) = 50 pairs"""
import json, os

OUT = "datasets/tier1a/raw_sources/raw_pairs_batch_004.jsonl"
D = "2026-06-09"
TRA = "https://www.tra.go.tz"
TRA_N = "TRA — Tanzania Revenue Authority"
TANZLII = "https://www.tanzlii.org"
TANZLII_N = "TanzLII — Tanzania Legal Information Institute"
ML = "https://www.mlywf.go.tz"
ML_N = "Ministry of Labour, Youth, Women and Special Groups"
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
# WHT DEEP — pairs 011-040 (30 pairs)
# =====================================================================

p("tier1a_wht_deep_011_20260609","wht_withholding_tax",
  "Nani analazimika kukata WHT — mlipaji au mpokeaji wa malipo?",
  "MLIPAJI (mtu anayetoa malipo) ndiye analazimika kukata WHT na kuipeleka TRA. "
  "Kwa mfano, kampuni inayolipa ada za ushauri kwa mshauri italazimika kukata WHT "
  "kabla ya kumpa mshauri malipo yaliyobaki. Mpokeaji hakati WHT — mtoaji ndiye "
  "anayebeba wajibu huu.",
  "Who is required to deduct WHT — the payer or the recipient of the payment?",
  "The PAYER (the person making the payment) must deduct WHT and remit it to TRA. "
  "For example, a company paying consulting fees to a consultant must deduct WHT "
  "before giving the consultant the net payment. The recipient does not deduct WHT "
  "— the payer bears this obligation.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act WHT amendment",
  "business_market", "standard"),

p("tier1a_wht_deep_012_20260609","wht_withholding_tax",
  "WHT inatumika kwa malipo ya gani — orodhesha aina kuu za malipo yanayotoza WHT?",
  "Aina kuu za malipo yanayotoza WHT Tanzania ni: gawio (dividends) 10%, riba "
  "(interest) 10%, kodi ya pango (rent) 10%/20%, royalties 15%, ada za usimamizi "
  "na kitaalamu 5%/15%, ada za mkurugenzi 15%/20%, bima 5%, na mapato ya rasilimali "
  "za asili 15%. Kiwango kinatofautiana kati ya wakazi na wasio wakazi.",
  "What payments does WHT apply to — list the main categories subject to WHT?",
  "The main payment categories subject to WHT in Tanzania are: dividends 10%, interest "
  "10%, rent 10%/20%, royalties 15%, management and professional fees 5%/15%, director "
  "fees 15%/20%, insurance premiums 5%, and natural resource income 15%. Rates differ "
  "between residents and non-residents.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act WHT rate change",
  "formal", "standard"),

p("tier1a_wht_deep_013_20260609","wht_withholding_tax",
  "Tofauti kati ya WHT na PAYE ni nini?",
  "WHT (Withholding Tax) inahusu MALIPO YANAYOTOKA KWA BIASHARA — kama gawio, riba, "
  "royalties, na ada za huduma. PAYE (Pay As You Earn) inahusu MISHAHARA YA WAFANYAKAZI. "
  "WHT inakataolewa na mlipaji kabla ya kutoa malipo. PAYE inakataolewa na mwajiri "
  "kutoka mshahara wa mfanyakazi. Zote mbili zinawasilishwa TRA.",
  "What is the difference between WHT and PAYE?",
  "WHT (Withholding Tax) applies to BUSINESS PAYMENTS — such as dividends, interest, "
  "royalties, and service fees. PAYE (Pay As You Earn) applies to EMPLOYEE SALARIES. "
  "WHT is deducted by the payer before making the payment. PAYE is deducted by the "
  "employer from the employee's salary. Both are remitted to TRA.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "business_market", "disambiguation"),

p("tier1a_wht_deep_014_20260609","wht_withholding_tax",
  "Kampuni inayolipa gawio kwa wanahisa wa kigeni inakata WHT ya asilimia ngapi?",
  "Kampuni inayolipa gawio kwa wanahisa wasio wakazi (kigeni) inakata WHT ya asilimia 10. "
  "Kiwango hiki ni sawa na kwa wanahisa wakazi — asilimia 10 kwa wote. Baadhi ya "
  "mikataba ya kuepuka kodi mara mbili (DTA) inaweza kupunguza kiwango hiki kwa "
  "wanahisa wa nchi fulani.",
  "A company paying dividends to foreign shareholders deducts WHT at what rate?",
  "A company paying dividends to non-resident (foreign) shareholders deducts WHT at "
  "10%. This rate is the same as for resident shareholders — 10% for both. Some "
  "Double Taxation Agreements (DTAs) may reduce this rate for shareholders from "
  "specific countries.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act WHT rate change",
  "formal", "standard"),

p("tier1a_wht_deep_015_20260609","wht_withholding_tax",
  "Je, WHT inaathiri mkataba wa makubaliano ya biashara (business agreement) vipi?",
  "Mtu anayeingia mkataba wa biashara Tanzania anapaswa kuzingatia WHT katika "
  "mahesabu ya bei. Kwa mfano, ikiwa ada ya ushauri ni Shilingi 1,000,000 na WHT "
  "ni asilimia 5, mshauri atapokea Shilingi 950,000 na mwajiri atalipa Shilingi 50,000 "
  "TRA. Mikataba inapaswa kuainisha wazi kama bei ni kabla au baada ya WHT.",
  "How does WHT affect a business contract agreement?",
  "A person entering a business contract in Tanzania must factor WHT into pricing. "
  "For example, if a consulting fee is TZS 1,000,000 and WHT is 5%, the consultant "
  "receives TZS 950,000 and the payer remits TZS 50,000 to TRA. Contracts should "
  "clearly state whether prices are gross (before) or net (after) WHT.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act WHT amendment",
  "business_market", "standard"),

p("tier1a_wht_deep_016_20260609","wht_withholding_tax",
  "WHT yote inawasilishwa TRA pamoja kwenye fomu moja — je, ni kweli?",
  "Ndiyo, WHT zote za mwezi inawasilishwa TRA kupitia fomu moja ya WHT return "
  "ifikapo tarehe 7 ya mwezi unaofuata. Fomu inaonyesha kila aina ya malipo, "
  "kiasi kilichokatwa, na maelezo ya mpokeaji. TRA inaweza kukagua kila aina "
  "tofauti katika ukaguzi.",
  "All WHT is submitted to TRA together on one form — is this correct?",
  "Yes. All WHT deductions for the month are submitted to TRA on a single WHT return "
  "by the 7th of the following month. The form shows each type of payment, amount "
  "deducted, and recipient details. TRA can audit each category separately during "
  "an examination.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA filing guidance",
  "formal", "standard"),

p("tier1a_wht_deep_017_20260609","wht_withholding_tax",
  "WHT kwa msaada wa kiufundi (technical assistance) kutoka kampuni ya kigeni ni asilimia ngapi?",
  "WHT kwa ada za msaada wa kiufundi na usimamizi kutoka kampuni ya kigeni (wasio "
  "wakazi) ni asilimia 15. Kwa kampuni ya ndani (wakazi), kiwango ni asilimia 5. "
  "Tofauti hii ni muhimu kwa makampuni yanayopanga mikataba ya ushauri wa kimataifa.",
  "What is the WHT rate on technical assistance from a foreign company?",
  "WHT on technical assistance and management fees from a foreign (non-resident) "
  "company is 15%. For a domestic (resident) company the rate is 5%. This difference "
  "is important for companies contracting international advisory services.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act WHT rate change",
  "formal", "standard"),

p("tier1a_wht_deep_018_20260609","wht_withholding_tax",
  "Biashara ndogo (SME) yenye mauzo chini ya Shilingi 100M lazima ipigie WHT?",
  "Ndiyo. Wajibu wa WHT hauhusiani na ukubwa wa biashara au mauzo. Kampuni yoyote "
  "inayofanya malipo yanayotoza WHT — iwe kubwa au ndogo — inalazimika kukata na "
  "kulipa WHT. SME zenye mauzo madogo bado zina wajibu wa WHT kwenye malipo "
  "kama royalties, gawio, na ada za ushauri.",
  "Does a small business (SME) with sales below TZS 100M have to withhold WHT?",
  "Yes. The WHT obligation is not linked to business size or turnover. Any company "
  "making payments subject to WHT — large or small — must deduct and remit WHT. "
  "SMEs with low turnover still have WHT obligations on payments such as royalties, "
  "dividends, and consulting fees.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA WHT guidance",
  "rural_conversational", "standard"),

p("tier1a_wht_deep_019_20260609","wht_withholding_tax",
  "Cheti cha WHT (WHT certificate) kinatumika kwa nini?",
  "Cheti cha WHT kinathibitisha kwamba mwajiri alilipa WHT kwa niaba ya mpokeaji. "
  "Mpokeaji anaweza kutumia cheti hiki kama mkopo wa kodi dhidi ya kodi yake "
  "ya mwisho ya mwaka (tax credit). Kampuni inayowasilisha taarifa ya kodi ya "
  "kampuni inaweza kupunguza kodi yake kwa kiasi cha WHT iliyokatwa na kuonyeshwa "
  "kwenye cheti.",
  "What is a WHT certificate used for?",
  "A WHT certificate confirms that the payer remitted WHT on behalf of the recipient. "
  "The recipient can use this certificate as a tax credit against their final annual "
  "tax liability. A company filing a corporate income tax return can reduce its tax "
  "liability by the WHT amount shown on the certificate.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "business_market", "standard"),

p("tier1a_wht_deep_020_20260609","wht_withholding_tax",
  "WHT na VAT withholding ni tofauti — kampuni inaweza kuchanganya?",
  "Ndiyo, hizi ni ushuru tofauti kabisa. WHT (Withholding Tax) inahusu kodi ya mapato "
  "kwenye malipo ya huduma, gawio, na riba. VAT withholding (3%/6% kuanzia Julai 2025) "
  "inahusu VAT inayopitiwa kwa wakala wa serikali. Kampuni inapaswa kuhesabu na kuripoti "
  "kila moja tofauti — kutafsiriwa pamoja ni kosa la kisheria.",
  "WHT and VAT withholding are different — can a company confuse them?",
  "Yes, these are completely different taxes. WHT (Withholding Tax) covers income tax on "
  "service payments, dividends, and interest. VAT withholding (3%/6% from July 2025) "
  "covers VAT channelled through government agencies. A company must calculate and report "
  "each separately — confusing them is a legal error.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act WHT and VAT amendment",
  "formal", "disambiguation"),

p("tier1a_wht_deep_021_20260609","wht_withholding_tax",
  "WHT ya asilimia 5 inatumika kwa malipo ya mtu binafsi wa Tanzania wa huduma za kitaalamu — je, ni sahihi?",
  "Ndiyo. Malipo ya ada za usimamizi na huduma za kitaalamu kwa mtu binafsi MKAZI wa "
  "Tanzania yanakatwa WHT ya asilimia 5. Kwa wasio wakazi (non-resident consultants), "
  "kiwango ni asilimia 15. Mwajiri anayemkabidhi mshauri Tanzania mtu binafsi atakata "
  "asilimia 5 kabla ya kulipa.",
  "WHT of 5% applies to payments to a Tanzanian individual for professional services — is this correct?",
  "Yes. Management and professional service fee payments to a RESIDENT individual in "
  "Tanzania attract 5% WHT. For non-resident consultants the rate is 15%. An employer "
  "engaging a Tanzanian individual consultant will deduct 5% before payment.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act WHT rate change",
  "business_market", "standard"),

p("tier1a_wht_deep_022_20260609","wht_withholding_tax",
  "Malipo ya pango kwa mwenye nyumba asiye wakazi Tanzania yatatozwa WHT ya asilimia ngapi?",
  "Malipo ya pango kwa mwenye nyumba asiye wakazi (non-resident landlord) yatatozwa "
  "WHT ya asilimia 20. Kwa mwenye nyumba mkazi, kiwango ni asilimia 10. Mpangaji "
  "(tenant) analazimika kukata WHT kabla ya kulipa pango na kulipa TRA ifikapo "
  "tarehe 7 ya mwezi unaofuata.",
  "Rent paid to a non-resident landlord in Tanzania attracts WHT at what rate?",
  "Rent paid to a non-resident landlord attracts 20% WHT. For a resident landlord "
  "the rate is 10%. The tenant must deduct WHT before paying rent and remit to TRA "
  "by the 7th of the following month.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act WHT rate change",
  "rural_conversational", "standard"),

p("tier1a_wht_deep_023_20260609","wht_withholding_tax",
  "WHT kwa royalties za wakazi na wasio wakazi ni sawa — je, hii ni kweli?",
  "Ndiyo. Kwa royalties, kiwango cha WHT ni sawa kwa wakazi na wasio wakazi — "
  "asilimia 15 kwa wote wawili. Hii ni tofauti na aina nyingine za malipo kama "
  "ada za usimamizi (5% kwa wakazi, 15% kwa wasio wakazi) na ada za mkurugenzi "
  "(15% kwa wakazi, 20% kwa wasio wakazi).",
  "WHT on royalties is the same for residents and non-residents — is this true?",
  "Yes. For royalties the WHT rate is the same for both residents and non-residents "
  "— 15% for both. This differs from other payment types like management fees "
  "(5% residents, 15% non-residents) and director fees (15% residents, 20% "
  "non-residents).",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act WHT rate change",
  "formal", "standard"),

p("tier1a_wht_deep_024_20260609","wht_withholding_tax",
  "Mtu aliyekatwa WHT anaweza kuomba rejesho lake vipi?",
  "Mtu aliyekatwa WHT anaweza kudai mkopo wa WHT dhidi ya kodi yake ya mwaka "
  "kwa kuwasilisha taarifa ya kodi (income tax return) na TRA. Ikiwa WHT "
  "iliyokatwa inazidi kodi halisi, TRA italipa rejesho. Cheti cha WHT kinahitajika "
  "kama ushahidi wa malipo.",
  "How can a person who has had WHT deducted claim a refund?",
  "A person who has had WHT deducted can claim a WHT credit against their annual "
  "tax liability by filing an income tax return with TRA. If WHT deducted exceeds "
  "actual tax owed, TRA will issue a refund. The WHT certificate is required as "
  "proof of payment.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA refund procedure",
  "formal", "standard"),

p("tier1a_wht_deep_025_20260609","wht_withholding_tax",
  "WHT haihusiani na biashara ya kilimo — wakulima na washirika wa kilimo hawana WHT — je, ni kweli?",
  "Si kweli kwa ujumla. Hata sekta ya kilimo inaweza kukabili WHT kwenye malipo fulani "
  "kama royalties kwa mbegu au teknolojia, na ada za usimamizi. Hata hivyo, mkulima "
  "mdogo anayeuza mazao yake moja kwa moja kwa mnunuzi hana WHT inayostahili. "
  "WHT inategemea aina ya malipo, si sekta.",
  "WHT has nothing to do with agriculture — farmers and agricultural cooperatives have no WHT — is this true?",
  "Not as a general rule. Even the agricultural sector can encounter WHT on certain "
  "payments such as royalties for seeds or technology, and management fees. However, "
  "a small farmer selling crops directly to a buyer has no WHT liability. WHT depends "
  "on the type of payment, not the sector.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act WHT amendment",
  "rural_conversational", "standard"),

p("tier1a_wht_deep_026_20260609","wht_withholding_tax",
  "Kiwango cha WHT kwa riba ya benki ni asilimia ngapi?",
  "WHT kwa riba ya benki inayolipwa kwa mkazi ni asilimia 10. Kwa wasio wakazi, "
  "kiwango ni pia asilimia 10. Benki inayolipa riba kwenye akaunti ya akiba "
  "inalazimika kukata WHT ya asilimia 10 na kuipeleka TRA kabla ya kulipa riba "
  "kwa mwenyekiti wa akaunti.",
  "What is the WHT rate on bank interest?",
  "WHT on bank interest paid to a resident is 10%. For non-residents the rate is "
  "also 10%. A bank paying interest on a savings account must deduct 10% WHT and "
  "remit it to TRA before paying interest to the account holder.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act WHT rate change",
  "business_market", "standard"),

p("tier1a_wht_deep_027_20260609","wht_withholding_tax",
  "WHT kwa malipo ya leseni ya software kutoka kampuni ya kigeni ni asilimia ngapi?",
  "Malipo ya leseni ya software kwa kampuni ya kigeni yanaweza kuainishwa kama royalties "
  "au ada za huduma za kiufundi kulingana na hali halisi ya mkataba. Ikiwa ni royalties, "
  "WHT ni asilimia 15. Ikiwa ni ada za huduma za kiufundi za mtu asiye mkazi, WHT ni "
  "asilimia 15 pia. Ni muhimu kufanya tathmini ya asili ya malipo na mshauri wa kodi.",
  "What is the WHT rate on software licence payments to a foreign company?",
  "Software licence payments to a foreign company may be classified as royalties or "
  "technical service fees depending on the actual contract terms. If royalties, WHT "
  "is 15%. If non-resident technical service fees, WHT is also 15%. It is important "
  "to assess the nature of the payment with a tax adviser.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act WHT amendment",
  "formal", "standard"),

p("tier1a_wht_deep_028_20260609","wht_withholding_tax",
  "WHT kwa gawio kwa wakazi na wasio wakazi ni asilimia 15 — je, ni sahihi?",
  "Hapana. WHT kwa gawio ni asilimia 10 kwa wakazi NA kwa wasio wakazi — si asilimia 15. "
  "Kiwango cha asilimia 15 kinatumika kwa aina nyingine za malipo kama royalties na ada "
  "za mkurugenzi (wakazi). Gawio daima inatoza asilimia 10 bila kujali wakazi au la.",
  "WHT on dividends for residents and non-residents is 15% — is this correct?",
  "No. WHT on dividends is 10% for both residents AND non-residents — not 15%. The "
  "15% rate applies to other payment types such as royalties and resident director fees. "
  "Dividends always attract 10% regardless of resident status.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act WHT rate change",
  "business_market", "adversarial"),

p("tier1a_wht_deep_029_20260609","wht_withholding_tax",
  "Ikiwa kampuni haikukata WHT inayostahili, nani atabeba adhabu — kampuni au mpokeaji?",
  "KAMPUNI (mlipaji) ndiye atabeba adhabu ya kutokukata WHT. TRA inaweza kudai WHT "
  "iliyokosekana, adhabu ya ucheleweshaji (2.5% kwa mwezi), na riba ya kisheria "
  "kutoka kwa kampuni — si kwa mpokeaji. Hii ndiyo sababu ni muhimu kwa kampuni "
  "kufuatilia WHT yote kwenye malipo yanayostahili.",
  "If a company failed to deduct required WHT, who bears the penalty — the company or the recipient?",
  "The COMPANY (payer) bears the penalty for failure to deduct WHT. TRA can demand "
  "the unpaid WHT, late payment penalty (2.5% per month), and statutory interest "
  "from the company — not from the recipient. This is why it is critical for "
  "companies to track all WHT on qualifying payments.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA enforcement guidance",
  "formal", "standard"),

p("tier1a_wht_deep_030_20260609","wht_withholding_tax",
  "Tofauti kati ya WHT kwa malipo ya ndani na malipo ya nje ya nchi ni nini?",
  "WHT kwa malipo ya NDANI (wakazi) mara nyingi ina kiwango cha chini — kwa mfano, "
  "ada za usimamizi 5%, ada za mkurugenzi 15%. WHT kwa malipo ya NJE (wasio wakazi) "
  "ina kiwango cha juu zaidi — ada za usimamizi 15%, ada za mkurugenzi 20%, kodi ya "
  "pango 20%. Gawio na riba ni sawa kwa wote (10%). Mikataba ya DTA inaweza kupunguza "
  "viwango vya wasio wakazi.",
  "What is the difference between WHT on domestic payments and cross-border payments?",
  "WHT on DOMESTIC (resident) payments generally has lower rates — management fees 5%, "
  "director fees 15%. WHT on CROSS-BORDER (non-resident) payments has higher rates — "
  "management fees 15%, director fees 20%, rent 20%. Dividends and interest are the "
  "same for both (10%). Double Taxation Agreements (DTAs) can reduce non-resident rates.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act WHT rate change",
  "formal", "disambiguation"),

p("tier1a_wht_deep_031_20260609","wht_withholding_tax",
  "WHT kwa malipo ya bima na malipo ya riba ni sawa — asilimia 5 kwa wote — je, ni sahihi?",
  "Hapana. WHT kwa malipo ya bima ni asilimia 5, lakini WHT kwa riba (interest) ni "
  "asilimia 10 — si asilimia 5. Kiwango cha asilimia 5 kwa riba si sahihi. "
  "Kiwango cha asilimia 5 kinatumika tu kwa bima na ada za huduma za wakazi.",
  "WHT on insurance payments and interest payments is the same — 5% for both — is this correct?",
  "No. WHT on insurance payments is 5%, but WHT on interest is 10% — not 5%. "
  "A 5% rate on interest is incorrect. The 5% rate applies only to insurance "
  "and resident service fees.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act WHT rate change",
  "business_market", "adversarial"),

p("tier1a_wht_deep_032_20260609","wht_withholding_tax",
  "Ikiwa mkataba unasema malipo 'ni ya WHT inclusive', mpokeaji anachukua nini?",
  "Ikiwa mkataba unasema malipo 'WHT inclusive' au 'gross-up', mwajiri atalazimika "
  "kulipa zaidi ili mpokeaji apate kiasi kilichokubalika BAADA ya WHT. Mwajiri "
  "atachangia WHT kutoka kwake badala ya kuikata kutoka kwa mpokeaji. Hii huongeza "
  "gharama halisi ya mwajiri. Mkataba unapaswa kuainisha wazi.",
  "If a contract says payments are 'WHT inclusive', what does the recipient receive?",
  "If a contract says 'WHT inclusive' or provides for 'gross-up', the payer must pay "
  "more so that the recipient receives the agreed amount AFTER WHT. The payer absorbs "
  "the WHT cost instead of deducting from the recipient. This increases the payer's "
  "actual cost. The contract should clearly specify.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA WHT guidance",
  "formal", "standard"),

p("tier1a_wht_deep_033_20260609","wht_withholding_tax",
  "WHT inatekelezwa vipi kwenye makubaliano ya DTA (Double Taxation Agreement)?",
  "Mikataba ya DTA inaweza kupunguza kiwango cha WHT kwa malipo kati ya nchi mbili "
  "zilizoingia mkataba. Tanzania ina DTA na nchi kadhaa. Kampuni inayofanya malipo "
  "kwa mpokeaji katika nchi yenye DTA na Tanzania inaweza kutumia kiwango cha chini "
  "cha DTA badala ya kiwango cha kawaida cha Tanzania — ikiwa hali zote za DTA zinatimizwa.",
  "How does a Double Taxation Agreement (DTA) affect WHT?",
  "A DTA can reduce the WHT rate on payments between two treaty countries. Tanzania "
  "has DTAs with several countries. A company making payments to a recipient in a "
  "country that has a DTA with Tanzania may apply the lower DTA rate instead of "
  "Tanzania's standard rate — provided all DTA conditions are met.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "DTA amendment or ratification",
  "formal", "standard"),

p("tier1a_wht_deep_034_20260609","wht_withholding_tax",
  "WHT haihitajiki kwa malipo ya chini ya Shilingi 500,000 — je, ni kweli?",
  "Hapana. Hakuna kizingiti cha chini cha kisheria cha kiasi cha malipo kinachomwondolea "
  "mwajiri wajibu wa WHT. Malipo yoyote yanayotoza WHT — iwe madogo au makubwa — "
  "yanatakiwa WHT. Kizingiti cha Shilingi 500,000 hakipo chini ya sheria ya WHT "
  "ya Tanzania.",
  "WHT is not required for payments below TZS 500,000 — is this true?",
  "No. There is no statutory minimum payment threshold that exempts a payer from WHT. "
  "Any payment subject to WHT — large or small — requires WHT deduction. A threshold "
  "of TZS 500,000 does not exist under Tanzania's WHT law.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA WHT guidance",
  "rural_conversational", "adversarial"),

p("tier1a_wht_deep_035_20260609","wht_withholding_tax",
  "WHT kwa ada za mkurugenzi ni sawa kwa wakazi na wasio wakazi — je, ni kweli?",
  "Hapana. Ada za mkurugenzi zinatoza WHT tofauti: asilimia 15 kwa WAKAZI na "
  "asilimia 20 kwa WASIO WAKAZI. Tofauti hii ya asilimia 5 ni muhimu — kampuni "
  "yenye mkurugenzi wa kigeni atalipa WHT ya asilimia 20 kwenye ada zake, si asilimia 15.",
  "WHT on director fees is the same for residents and non-residents — is this true?",
  "No. Director fees attract different WHT: 15% for RESIDENTS and 20% for "
  "NON-RESIDENTS. This 5% difference is significant — a company with a foreign "
  "director will pay 20% WHT on their fees, not 15%.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act WHT rate change",
  "business_market", "adversarial"),

p("tier1a_wht_deep_036_20260609","wht_withholding_tax",
  "Mtu anayepokea gawio la asilimia 10 WHT — ana haki ya kupata cheti cha WHT?",
  "Ndiyo. Mtu yeyote ambaye amehusika na kukatwa WHT ana haki ya kupokea cheti "
  "cha WHT kutoka kwa mlipaji. Cheti hiki kinathibitisha WHT iliyokatwa na "
  "kinatumika kama mkopo wa kodi dhidi ya kodi ya mwaka wa mpokeaji. Mlipaji "
  "analazimika kutoa cheti ndani ya siku 30 za kukata.",
  "A person who has had 10% WHT deducted on dividends — are they entitled to a WHT certificate?",
  "Yes. Any person who has had WHT deducted is entitled to receive a WHT certificate "
  "from the payer. This certificate confirms the WHT deducted and serves as a tax "
  "credit against the recipient's annual tax. The payer must issue the certificate "
  "within 30 days of deduction.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA WHT guidance",
  "rural_conversational", "standard"),

p("tier1a_wht_deep_037_20260609","wht_withholding_tax",
  "WHT kwa malipo ya royalties kwa kampuni ya kigeni ni sawa na kwa kampuni ya ndani — je, ni kweli?",
  "Ndiyo kwa royalties — kiwango cha WHT kwa royalties ni asilimia 15 kwa wakazi "
  "NA wasio wakazi. Hii inaifanya royalties tofauti na aina nyingine za malipo ambapo "
  "wakazi wanafaidika na kiwango cha chini. Kwa royalties, kiwango ni sawa kwa wote.",
  "WHT on royalties paid to a foreign company is the same as for a domestic company — is this true?",
  "Yes for royalties — the WHT rate on royalties is 15% for both residents AND "
  "non-residents. This makes royalties different from other payment types where "
  "residents benefit from a lower rate. For royalties the rate is equal for all.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act WHT rate change",
  "formal", "standard"),

p("tier1a_wht_deep_038_20260609","wht_withholding_tax",
  "WHT ya asilimia 10 inatumika kwa malipo ya riba na gawio — je, mwajiri anapaswa kukata kiasi kimoja kwa aina zote mbili?",
  "Ndiyo kwa kiwango — WHT ya asilimia 10 inatumika kwa riba na gawio zote mbili. "
  "Hata hivyo, zinawasilishwa kwa mstari tofauti katika fomu ya WHT return ili TRA "
  "iweze kufuatilia kila aina. Mwajiri atakata asilimia 10 kwa kila malipo lakini "
  "ataripoti kila aina tofauti.",
  "WHT of 10% applies to both interest and dividend payments — should an employer deduct the same amount for both types?",
  "Yes on the rate — 10% WHT applies to both interest and dividends. However, they "
  "are reported on separate lines in the WHT return form so TRA can track each type. "
  "The employer deducts 10% on each payment but reports each category separately.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA WHT filing guidance",
  "formal", "standard"),

p("tier1a_wht_deep_039_20260609","wht_withholding_tax",
  "WHT inaweza kulipwa kwa nguzo ya bidhaa (in-kind) badala ya pesa — je, ni kweli?",
  "Hapana. WHT ni ushuru wa pesa taslimu na lazima ulipwe TRA kwa pesa — si kwa bidhaa "
  "au huduma. Hata kama malipo ya asili yaliyotoza WHT yalikuwa ya bidhaa (in-kind), "
  "WHT lazima ihesabiwe kwa thamani ya bidhaa na kulipwa TRA kwa pesa.",
  "WHT can be paid in kind (goods instead of cash) instead of money — is this true?",
  "No. WHT is a cash tax and must be paid to TRA in money — not in goods or services. "
  "Even if the original payment that triggered WHT was in kind, WHT must be calculated "
  "at the market value of the goods and paid to TRA in cash.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA WHT guidance",
  "formal", "adversarial"),

p("tier1a_wht_deep_040_20260609","wht_withholding_tax",
  "WHT inatumika kwa malipo ya ndani ya Tanzania peke yake — malipo kwa nchi za nje hayatozi WHT — je, ni kweli?",
  "Hapana. WHT inatumika kwa MALIPO YA AINA ZOTE — ya ndani na ya nje. Kwa kweli, "
  "malipo ya nje (kwa wasio wakazi) mara nyingi yanatoza WHT ya kiwango cha JUU zaidi "
  "kuliko malipo ya ndani. Kwa mfano, ada za usimamizi kwa wasio wakazi ni asilimia 15 "
  "ikilinganishwa na asilimia 5 kwa wakazi.",
  "WHT only applies to domestic Tanzania payments — payments abroad are not subject to WHT — is this true?",
  "No. WHT applies to ALL PAYMENT TYPES — both domestic and cross-border. In fact, "
  "cross-border payments (to non-residents) often attract HIGHER WHT rates than domestic "
  "payments. For example, management fees for non-residents are 15% compared to 5% "
  "for residents.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act WHT amendment",
  "business_market", "adversarial"),

# =====================================================================
# WCF COMPLIANCE — pairs 001-020 (20 pairs)
# Source: mlywf.go.tz | Workers Compensation Act 2008
# =====================================================================

p("tier1a_wcf_001_20260609","wcf_compliance",
  "WCF ni nini na wajibu wake kwa biashara yangu ni nini?",
  "WCF (Workers Compensation Fund) ni mfuko wa bima ya ajali za kazi wa Tanzania. "
  "Kama mwajiri, unalazimika kusajiliwa WCF na kulipa mchango wa asilimia 0.5 ya "
  "mshahara wote wa wafanyakazi wako kila mwezi. WCF inalipia mfanyakazi "
  "aliyeumia kazini — matibabu, fidia, na manufaa ya ulemavu au kifo.",
  "What is WCF and what is its obligation for my business?",
  "WCF (Workers Compensation Fund) is Tanzania's workplace accident insurance fund. "
  "As an employer you must register with WCF and pay a contribution of 0.5% of total "
  "employee wages each month. WCF pays injured workers — medical expenses, compensation, "
  "and disability or death benefits.",
  ML, ML_N, GP, "2008-01-01", ANN, "Workers Compensation Act amendment",
  "business_market", "standard"),

p("tier1a_wcf_002_20260609","wcf_compliance",
  "Kiwango cha mchango wa WCF ni asilimia ngapi?",
  "Kiwango cha mchango wa WCF ni asilimia 0.5 ya mshahara wote wa wafanyakazi "
  "(gross emoluments). Mchango huu unalipwa na MWAJIRI peke yake — mfanyakazi "
  "hakatiwi chochote. Mwajiri analipa asilimia 0.5 ya jumla ya mishahara yote.",
  "What is the WCF contribution rate?",
  "The WCF contribution rate is 0.5% of total employee wages (gross emoluments). "
  "This contribution is paid by the EMPLOYER only — the employee has nothing deducted. "
  "The employer pays 0.5% of total payroll.",
  ML, ML_N, GP, "2008-01-01", ANN, "Workers Compensation Act amendment",
  "formal", "standard"),

p("tier1a_wcf_003_20260609","wcf_compliance",
  "WCF na NSSF ni sawa — ni shirika moja tu — je, ni kweli?",
  "Hapana. WCF na NSSF ni mashirika tofauti yanayofanya kazi tofauti. WCF "
  "(Workers Compensation Fund) inashughulikia BIMA ya AJALI za kazi peke yake. "
  "NSSF (National Social Security Fund) inashughulikia USALAMA WA JAMII kwa upana "
  "zaidi — pensheni, matibabu, mama na mtoto. Waajiri lazima wasajiliwe na ZOTE MBILI "
  "tofauti.",
  "WCF and NSSF are the same — they are just one organisation — is this true?",
  "No. WCF and NSSF are separate organisations with different functions. WCF (Workers "
  "Compensation Fund) handles WORKPLACE ACCIDENT INSURANCE only. NSSF (National Social "
  "Security Fund) handles BROADER SOCIAL SECURITY — pensions, medical, maternity. "
  "Employers must register with BOTH separately.",
  ML, ML_N, GP, "2008-01-01", ANN, "Workers Compensation Act amendment",
  "business_market", "disambiguation"),

p("tier1a_wcf_004_20260609","wcf_compliance",
  "Mfanyakazi analipa sehemu ya mchango wa WCF — je, ni kweli?",
  "Hapana. Mchango wa WCF unalipwa na MWAJIRI PEKE YAKE — hakuna sehemu inayokatwa "
  "kutoka kwa mfanyakazi. Hii ni tofauti na NSSF ambapo mwajiri na mfanyakazi kila "
  "mmoja wanachangia asilimia 10. Kwa WCF, mwajiri anabeba gharama yote ya asilimia 0.5.",
  "The employee pays part of the WCF contribution — is this true?",
  "No. The WCF contribution is paid by the EMPLOYER ONLY — nothing is deducted from "
  "the employee. This differs from NSSF where both employer and employee each contribute "
  "10%. For WCF the employer bears the full 0.5% cost.",
  ML, ML_N, GP, "2008-01-01", ANN, "Workers Compensation Act amendment",
  "formal", "adversarial"),

p("tier1a_wcf_005_20260609","wcf_compliance",
  "Ikiwa mfanyakazi ameumia kazini, mwajiri anamwarifu WCF ndani ya muda gani?",
  "Mwajiri analazimika kumwarifu WCF kuhusu ajali ya kazi ndani ya siku 30 baada ya "
  "ajali kutokea. Kwa ajali kubwa au ya kifo, OSHA lazima iarifu ndani ya masaa 24. "
  "Kutokuripoti kwa wakati kunasababisha adhabu na inaweza kuathiri madai ya mfanyakazi.",
  "If a worker is injured at work within what timeframe must the employer notify WCF?",
  "The employer must notify WCF of a workplace accident within 30 days of it occurring. "
  "For serious or fatal accidents OSHA must be notified within 24 hours. Failure to "
  "report on time results in penalties and may affect the worker's claim.",
  ML, ML_N, GP, "2008-01-01", ST, "Workers Compensation Act amendment",
  "business_market", "standard"),

p("tier1a_wcf_006_20260609","wcf_compliance",
  "WCF inalipia majeraha ya nje ya mahali pa kazi — kama mfanyakazi alianguka akitoka kazini — je, ni kweli?",
  "Si kweli kwa ujumla. WCF inashughulikia majeraha YANAYOTOKANA NA KAZI peke yake "
  "— yaani yanayotokea wakati wa kufanya kazi au katika safari ya kazi inayoidhinishwa. "
  "Mfanyakazi aliyeumia nyumbani au wakati wa safari ya kibinafsi hakiwa na haki ya "
  "madai ya WCF.",
  "WCF covers injuries outside the workplace — like a worker who fell on the way home — is this true?",
  "Not as a general rule. WCF covers WORK-RELATED injuries only — those occurring "
  "during the performance of work or on an authorised work journey. An employee injured "
  "at home or during a personal trip is not entitled to a WCF claim.",
  ML, ML_N, GP, "2008-01-01", ST, "Workers Compensation Act amendment",
  "rural_conversational", "standard"),

p("tier1a_wcf_007_20260609","wcf_compliance",
  "Mfanyakazi wa muda mfupi (casual worker) ana haki ya WCF?",
  "Ndiyo. Wafanyakazi wa muda mfupi na wa msimu wana haki ya WCF kwa majeraha "
  "yanayotokana na kazi wakati wa muda wao wa kufanya kazi. Waajiri wanalazimika "
  "kusajili pia wafanyakazi wa muda mfupi kwa WCF au kuhakikisha wanafunikwa "
  "chini ya orodha ya jumla ya ajira.",
  "Does a casual (short-term) worker have WCF rights?",
  "Yes. Casual and seasonal workers are entitled to WCF for work-related injuries "
  "during their period of employment. Employers must also register casual workers "
  "with WCF or ensure they are covered under the general employment list.",
  ML, ML_N, GP, "2008-01-01", ST, "Workers Compensation Act amendment",
  "rural_conversational", "standard"),

p("tier1a_wcf_008_20260609","wcf_compliance",
  "Mchango wa WCF ni asilimia 1 ya mshahara wa mfanyakazi — je, ni sahihi?",
  "Hapana. Kiwango sahihi cha mchango wa WCF ni asilimia 0.5 — si asilimia 1. "
  "Asilimia 0.5 inakokotolewa kutoka kwa jumla ya mshahara wote wa wafanyakazi "
  "(gross emoluments). Kiwango cha asilimia 1 ni kosa — si sahihi chini ya sheria.",
  "The WCF contribution is 1% of employee salary — is this correct?",
  "No. The correct WCF contribution rate is 0.5% — not 1%. The 0.5% is calculated "
  "on total gross employee wages (gross emoluments). A rate of 1% is incorrect "
  "under the law.",
  ML, ML_N, GP, "2008-01-01", ANN, "Workers Compensation Act amendment",
  "business_market", "adversarial"),

p("tier1a_wcf_009_20260609","wcf_compliance",
  "Manufaa ya WCF yanajumuisha nini kwa mfanyakazi aliyeumia?",
  "Manufaa ya WCF kwa mfanyakazi aliyeumia yanajumuisha: gharama za matibabu "
  "(hospitali, dawa, upasuaji), posho ya ulemavu wa muda (wakati wa kupumzika "
  "kutokana na majeraha), fidia ya ulemavu wa kudumu, na manufaa ya kifo (kwa "
  "familia ikiwa mfanyakazi amefariki). WCF haifuniki hasara za mali.",
  "What benefits does WCF include for an injured worker?",
  "WCF benefits for an injured worker include: medical expenses (hospital, medicine, "
  "surgery), temporary disability allowance (during recovery from injury), permanent "
  "disability compensation, and death benefits (to family if the worker dies). WCF "
  "does not cover property losses.",
  ML, ML_N, GP, "2008-01-01", ST, "Workers Compensation Act amendment",
  "formal", "standard"),

p("tier1a_wcf_010_20260609","wcf_compliance",
  "Wajibu wa mwajiri wa kulipa WCF unaanzia wafanyakazi wangapi?",
  "Wajibu wa kulipa WCF unaanzia mfanyakazi WA KWANZA. Hakuna kizingiti cha idadi "
  "ya wafanyakazi kwa WCF — hata mwajiri mwenye mfanyakazi mmoja tu analazimika "
  "kusajili na kulipa WCF. Hii inatofautiana na OSHA (threshold ya 10) na SDL "
  "(threshold ya 10).",
  "From how many employees does the WCF payment obligation start?",
  "The WCF obligation starts from the FIRST employee. There is no employee count "
  "threshold for WCF — even an employer with just one employee must register and "
  "pay WCF. This differs from OSHA (threshold of 10) and SDL (threshold of 10).",
  ML, ML_N, GP, "2008-01-01", ANN, "Workers Compensation Act amendment",
  "business_market", "standard"),

p("tier1a_wcf_011_20260609","wcf_compliance",
  "WCF inashughulikia magonjwa yanayotokana na kazi (occupational diseases) pia?",
  "Ndiyo. WCF inashughulikia magonjwa yanayotokana na kazi — magonjwa yanayotokea "
  "au yanayoongezeka kwa sababu ya mazingira ya kazi. Mifano ni: uziwi wa kelele, "
  "magonjwa ya mapafu kutokana na vumbi, na matatizo yanayosababishwa na kemikali. "
  "Mfanyakazi mwenye ugonjwa wa kazi ana haki ya madai ya WCF.",
  "Does WCF also cover occupational diseases?",
  "Yes. WCF covers occupational diseases — conditions that arise or worsen because "
  "of the work environment. Examples include: noise-induced deafness, dust-related "
  "lung diseases, and conditions caused by chemicals. An employee with an occupational "
  "disease is entitled to make a WCF claim.",
  ML, ML_N, GP, "2008-01-01", ST, "Workers Compensation Act amendment",
  "formal", "standard"),

p("tier1a_wcf_012_20260609","wcf_compliance",
  "Mwajiri anaweza kusimama kidedea akiwa na bima binafsi ya wafanyakazi badala ya WCF — je, ni kweli?",
  "Hapana. Bima binafsi ya wafanyakazi haichukui nafasi ya usajili wa kisheria wa WCF. "
  "Waajiri wote Tanzania wanalazimika kusajiliwa WCF na kulipa mchango wake bila kujali "
  "kama wana bima binafsi nyingine. Hizi ni mahitaji tofauti ya kisheria.",
  "An employer can substitute private employee insurance for WCF registration — is this true?",
  "No. Private employee insurance does not replace the statutory WCF registration. All "
  "employers in Tanzania must register with WCF and pay contributions regardless of "
  "whether they have additional private insurance. These are separate legal requirements.",
  ML, ML_N, GP, "2008-01-01", ANN, "Workers Compensation Act amendment",
  "business_market", "adversarial"),

p("tier1a_wcf_013_20260609","wcf_compliance",
  "WCF mchango unalipwa TRA au WCF moja kwa moja?",
  "Mchango wa WCF unalipwa moja kwa moja kwa WORKERS COMPENSATION FUND (WCF) — "
  "si kwa TRA. WCF ni shirika lake tofauti linalosimamiwa na Wizara ya Kazi. "
  "Usajili, malipo ya mchango, na madai yote yanashughulikiwa na WCF, si TRA.",
  "Is the WCF contribution paid to TRA or directly to WCF?",
  "The WCF contribution is paid directly to the WORKERS COMPENSATION FUND (WCF) — "
  "not to TRA. WCF is a separate organisation managed by the Ministry of Labour. "
  "Registration, contribution payments, and all claims are handled by WCF, not TRA.",
  ML, ML_N, GP, "2008-01-01", ANN, "Workers Compensation Act amendment",
  "business_market", "standard"),

p("tier1a_wcf_014_20260609","wcf_compliance",
  "Mfanyakazi wa kipindi cha majaribio (probationary) ana haki ya WCF?",
  "Ndiyo. Wafanyakazi wa kipindi cha majaribio wana haki ya WCF kwa majeraha "
  "yanayotokana na kazi wakati wa kipindi hicho. Hali ya probationary haibadilishi "
  "haki za WCF — mfanyakazi yeyote anayefanya kazi kwa mwajiri Tanzania ana haki "
  "ya WCF tangu siku ya kwanza.",
  "Does a probationary employee have WCF rights?",
  "Yes. Probationary employees have WCF rights for work-related injuries during the "
  "probationary period. Probationary status does not change WCF entitlements — any "
  "employee working for a Tanzania employer has WCF rights from day one.",
  ML, ML_N, GP, "2008-01-01", ST, "Workers Compensation Act amendment",
  "rural_conversational", "standard"),

p("tier1a_wcf_015_20260609","wcf_compliance",
  "WCF inashughulikia matukio ya dharura tu — kama maumivu ya kawaida, mfanyakazi hana haki — je, ni kweli?",
  "Si kweli kwa ujumla. WCF inashughulikia majeraha na magonjwa yanayotokana na KAZI — "
  "sio matukio ya dharura tu. Maumivu ya kawaida yanayotokana na kazi (kama maumivu "
  "ya mgongo kutokana na kuketi muda mrefu, au maumivu ya mkono kutokana na "
  "kujirudiarudia) yanaweza kustahili madai ya WCF.",
  "WCF only covers emergency incidents — for normal aches, the employee has no rights — is this true?",
  "Not as a general rule. WCF covers injuries and WORK-CAUSED conditions — not just "
  "emergency incidents. Common work-related pains (such as back pain from prolonged "
  "sitting, or hand strain from repetitive movements) can qualify for WCF claims.",
  ML, ML_N, GP, "2008-01-01", ST, "Workers Compensation Act amendment",
  "formal", "adversarial"),

p("tier1a_wcf_016_20260609","wcf_compliance",
  "Tofauti kati ya WCF na NSSF ni nini — wote wawili wanahusiana na manufaa ya wafanyakazi?",
  "WCF inashughulikia MAJERAHA NA MAGONJWA ya kazi peke yake — ajali za kazini na "
  "magonjwa yanayotokana na kazi. NSSF inashughulikia USALAMA WA JAMII kwa ujumla — "
  "pensheni ya uzee, manufaa ya mama na mtoto, na manufaa ya ulemavu usio wa kazi. "
  "Waajiri wanawajibika kwa zote mbili, na wajibu wao ni tofauti.",
  "What is the difference between WCF and NSSF — both relate to employee benefits?",
  "WCF covers WORK INJURIES AND DISEASES only — workplace accidents and occupational "
  "diseases. NSSF covers GENERAL SOCIAL SECURITY — retirement pension, maternity "
  "benefits, and non-work disability. Employers are obligated to both, with separate "
  "obligations.",
  ML, ML_N, GP, "2008-01-01", ST, "Workers Compensation Act amendment",
  "formal", "disambiguation"),

p("tier1a_wcf_017_20260609","wcf_compliance",
  "WCF inashughulikia tu wafanyakazi wa sekta ya viwanda — waajiri wa ofisi hawahitajiki kusajili — je, ni kweli?",
  "Hapana. WCF inatumika kwa waajiri WOTE Tanzania — viwanda, ofisi, biashara, "
  "kilimo, na sekta nyingine zote. Hakuna msamaha kwa sekta yoyote. Mwajiri wa ofisi "
  "yenye wafanyakazi wachache bado analazimika kusajili na kulipa WCF.",
  "WCF only covers industrial sector employees — office employers don't need to register — is this true?",
  "No. WCF applies to ALL employers in Tanzania — industry, offices, trade, agriculture, "
  "and all other sectors. There is no exemption for any sector. An office employer "
  "with few employees still must register and pay WCF.",
  ML, ML_N, GP, "2008-01-01", ANN, "Workers Compensation Act amendment",
  "business_market", "adversarial"),

p("tier1a_wcf_018_20260609","wcf_compliance",
  "Mfanyakazi wa kigeni anayefanya kazi Tanzania ana haki ya WCF?",
  "Ndiyo. Wafanyakazi wa kigeni wanaofanya kazi Tanzania chini ya mkataba wa ajira "
  "wa Tanzania wana haki ya WCF kwa majeraha yanayotokana na kazi. Mwajiri anayemwajiri "
  "mfanyakazi wa kigeni Tanzania analazimika kumjumuisha katika orodha ya WCF.",
  "Does a foreign worker employed in Tanzania have WCF rights?",
  "Yes. Foreign workers employed in Tanzania under a Tanzania employment contract are "
  "entitled to WCF for work-related injuries. An employer engaging a foreign worker "
  "in Tanzania must include them in the WCF payroll.",
  ML, ML_N, GP, "2008-01-01", ST, "Workers Compensation Act amendment",
  "formal", "standard"),

p("tier1a_wcf_019_20260609","wcf_compliance",
  "Mfanyakazi anayedai WCF lazima athibitishe nini?",
  "Mfanyakazi anayedai WCF lazima athibitishe: kwamba majeraha yalitokea wakati wa "
  "kufanya kazi, kwamba yalitokana na kazi au mazingira ya kazi, na kwamba "
  "waliripotiwa kwa mwajiri kwa wakati. Hati za matibabu na ripoti ya ajali kutoka "
  "kwa mwajiri zinahitajika kama ushahidi.",
  "What must an employee claiming WCF prove?",
  "An employee claiming WCF must prove: that the injury occurred during the course of "
  "work, that it arose from work or the work environment, and that it was reported to "
  "the employer in time. Medical documentation and the employer's accident report are "
  "required as evidence.",
  ML, ML_N, GP, "2008-01-01", ST, "Workers Compensation Act amendment",
  "rural_conversational", "standard"),

p("tier1a_wcf_020_20260609","wcf_compliance",
  "WCF ni tofauti na bima ya maisha (life insurance) — je, ni kweli?",
  "Ndiyo, ni tofauti kabisa. WCF inashughulikia majeraha na magonjwa yanayotokana "
  "na KAZI — ni bima ya ajali za kazini inayodhibitiwa na serikali. Bima ya maisha "
  "ni mkataba wa kibinafsi kati ya mtu na kampuni ya bima unaohusisha kifo kutoka "
  "sababu yoyote. Waajiri wanalazimika WCF; bima ya maisha ni ya hiari.",
  "WCF is different from life insurance — is this true?",
  "Yes, they are completely different. WCF covers WORK-RELATED injuries and diseases "
  "— it is government-regulated workplace accident insurance. Life insurance is a "
  "private contract between an individual and an insurer covering death from any cause. "
  "WCF is mandatory for employers; life insurance is voluntary.",
  ML, ML_N, GP, "2008-01-01", ST, "Workers Compensation Act amendment",
  "formal", "disambiguation"),

]

written = 0
with open(OUT, "a", encoding="utf-8") as f:
    for pr in pairs:
        f.write(json.dumps(pr, ensure_ascii=False) + "\n")
        written += 1

total = sum(1 for _ in open(OUT, encoding="utf-8") if _.strip())
print(f"Part 4: wrote {written} pairs")
print(f"Total in file: {total}")
