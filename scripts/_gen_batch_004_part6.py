#!/usr/bin/env python3
"""batch_004 part 6 — Tax disputes (40) + 10 rural_conversational mixed = 50 pairs (total 300)"""
import json, os

OUT = "datasets/tier1a/raw_sources/raw_pairs_batch_004.jsonl"
D = "2026-06-09"
TRA = "https://www.tra.go.tz"
TRA_N = "TRA — Tanzania Revenue Authority"
TANZLII = "https://www.tanzlii.org"
TANZLII_N = "TanzLII — Tanzania Legal Information Institute"
BRELA_URL = "https://www.brela.go.tz"
BRELA_N = "BRELA — Business Registrations and Licensing Agency"
ML = "https://www.mlywf.go.tz"
ML_N = "Ministry of Labour, Youth, Women and Special Groups"
OSHA_URL = "https://www.osha.go.tz"
OSHA_N = "OSHA — Occupational Safety and Health Authority"
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
# TAX DISPUTES (40 pairs, IDs tax_dispute_001-040)
# Sources: tra.go.tz, tanzlii.org
# =====================================================================

p("tier1a_tax_dispute_001_20260609","tax_disputes",
  "TRA imetoa tathmini ya kodi ambayo nadhani si sahihi — ninafanya nini kwanza?",
  "Hatua ya kwanza ni kuwasilisha PINGAMIZI (objection) rasmi kwa Kamishna Mkuu wa "
  "TRA ndani ya siku 30 baada ya kupokea tathmini. Kabla ya pingamizi kukubaliwa, "
  "lazima ulipe angalau THELUTHI MOJA (1/3) ya kiasi kinachodaiwa. Kisha subiri "
  "uamuzi wa Kamishna ambao unafanywa ndani ya miezi 6.",
  "TRA has issued a tax assessment I believe is incorrect — what is my first step?",
  "The first step is to file a formal OBJECTION with the TRA Commissioner General "
  "within 30 days of receiving the assessment. Before the objection is accepted, "
  "you must pay at least ONE THIRD (1/3) of the disputed amount. Then await the "
  "Commissioner's determination, which is made within 6 months.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act or Tax Revenue Appeals Act update",
  "business_market", "standard"),

p("tier1a_tax_dispute_002_20260609","tax_disputes",
  "Muda wa kuwasilisha pingamizi kwa TRA ni siku ngapi baada ya kupokea tathmini?",
  "Muda wa kuwasilisha pingamizi kwa Kamishna Mkuu wa TRA ni siku 30 baada ya "
  "kupokea tathmini ya kodi. Ikiwa muda huu umepita bila pingamizi, tathmini "
  "inakuwa ya mwisho kisheria. Katika hali fulani za kipekee inaweza kuomba "
  "muda wa ziada, lakini hii si ya kawaida.",
  "Within how many days of receiving a tax assessment must an objection to TRA be filed?",
  "An objection to the TRA Commissioner General must be filed within 30 days of "
  "receiving the tax assessment. If this period passes without an objection the "
  "assessment becomes final in law. In exceptional circumstances an extension may "
  "be requested, but this is not guaranteed.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Revenue Appeals Act update",
  "formal", "standard"),

p("tier1a_tax_dispute_003_20260609","tax_disputes",
  "Kwa nini lazima nilipe 1/3 ya kodi inayodaiwa kabla ya pingamizi kukubaliwa?",
  "Malipo ya 1/3 ni sharti la kisheria linalozuia matumizi mabaya ya mchakato wa "
  "pingamizi. Inahakikisha kwamba wadai wa kodi wana nia ya kweli na wanaweza kulipa "
  "sehemu ya deni lao. Sehemu iliyolipwa inaweza kurudishwa ikiwa pingamizi linafanikiwa "
  "au inakuwa mkopo dhidi ya tathmini iliyorekebishwa.",
  "Why must I pay 1/3 of the disputed tax before an objection is accepted?",
  "The 1/3 payment is a legal requirement that prevents abuse of the objection process. "
  "It ensures that tax disputers have genuine intent and ability to pay part of their "
  "liability. The amount paid can be refunded if the objection succeeds or credited "
  "against a revised assessment.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Revenue Appeals Act update",
  "formal", "standard"),

p("tier1a_tax_dispute_004_20260609","tax_disputes",
  "Kamishna Mkuu wa TRA ana muda gani kuamua pingamizi langu?",
  "Kamishna Mkuu wa TRA ana miezi 6 kuamua pingamizi. Kama hatajibu ndani ya miezi 6, "
  "pingamizi linachukuliwa kama limekataliwa kisheria na mlipaji kodi anaweza kukata "
  "rufaa kwa Bodi ya Rufaa ya Mapato ya Kodi (TRAB) — hata bila uamuzi rasmi.",
  "How long does the TRA Commissioner General have to decide my objection?",
  "The TRA Commissioner General has 6 months to decide an objection. If they fail to "
  "respond within 6 months the objection is deemed rejected by law and the taxpayer "
  "can appeal to the Tax Revenue Appeals Board (TRAB) — even without a formal "
  "determination.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Revenue Appeals Act update",
  "formal", "standard"),

p("tier1a_tax_dispute_005_20260609","tax_disputes",
  "TRAB ni nini na inaendeshwa vipi?",
  "TRAB (Tax Revenue Appeals Board) ni Bodi ya Rufaa ya Mapato ya Kodi Tanzania. "
  "Inashughulikia rufaa dhidi ya maamuzi ya TRA yaliyofanywa baada ya pingamizi. "
  "Waheshimiwa wa kisheria na wataalam wa kodi wanasikiliza hoja zote mbili. "
  "Mlipaji kodi ana siku 45 kuwasilisha rufaa kwa TRAB baada ya kupokea uamuzi "
  "wa Kamishna.",
  "What is TRAB and how does it operate?",
  "TRAB (Tax Revenue Appeals Board) is Tanzania's Tax Revenue Appeals Board. It "
  "handles appeals against TRA decisions made following an objection. Legal members "
  "and tax experts hear arguments from both sides. The taxpayer has 45 days to "
  "file an appeal with TRAB after receiving the Commissioner's decision.",
  TANZLII, TANZLII_N, OG, "2001-01-01", ST, "Tax Revenue Appeals Act update",
  "formal", "standard"),

p("tier1a_tax_dispute_006_20260609","tax_disputes",
  "Ninafanya rufaa kwa TRAB ndani ya siku ngapi baada ya uamuzi wa Kamishna?",
  "Rufaa kwa TRAB inawasilishwa ndani ya siku 45 baada ya kupokea uamuzi wa "
  "Kamishna Mkuu wa TRA. Ikiwa muda huu umepita bila rufaa, uamuzi wa Kamishna "
  "unakuwa wa mwisho kisheria. Ni muhimu kuzingatia muda huu kwa makini.",
  "Within how many days of the Commissioner's decision must I appeal to TRAB?",
  "An appeal to TRAB must be filed within 45 days of receiving the TRA Commissioner "
  "General's decision. If this period passes without an appeal, the Commissioner's "
  "decision becomes final in law. It is critical to observe this deadline carefully.",
  TANZLII, TANZLII_N, OG, "2001-01-01", ST, "Tax Revenue Appeals Act update",
  "business_market", "standard"),

p("tier1a_tax_dispute_007_20260609","tax_disputes",
  "Riba na adhabu zinaendelea kukusanyika wakati wa mchakato wa pingamizi — je, ni kweli?",
  "Ndiyo. Riba ya kisheria ya TRA na adhabu za ucheleweshaji zinaendelea kukusanyika "
  "kwenye kiasi kisicholipwa hata wakati pingamizi linaendelea. Hii inamaanisha "
  "kwamba hata kama pingamizi linashindwa, jumla ya deni linaweza kuwa kubwa zaidi "
  "kuliko tathmini ya awali kutokana na riba iliyokusanyika.",
  "Do interest and penalties continue to accrue during the objection process — is this true?",
  "Yes. TRA statutory interest and late payment penalties continue to accrue on the "
  "unpaid amount even while an objection is in progress. This means that even if an "
  "objection eventually fails, the total debt may be significantly larger than the "
  "original assessment due to accrued interest.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act penalty update",
  "formal", "standard"),

p("tier1a_tax_dispute_008_20260609","tax_disputes",
  "Je, ninaweza kupata cheti cha utii wa kodi (tax clearance certificate) wakati pingamizi linaendelea?",
  "Kwa kawaida, cheti cha utii wa kodi hakitolewa wakati kuna kesi ya kodi inayoendelea "
  "au deni lisilolipwa la kodi ambalo halijatatua. TRA inaweza kuwa na sera zake za "
  "kuzingatia hali maalum. Inashauriwa kushauriana na TRA moja kwa moja kuhusu hali "
  "yako ya kibinafsi.",
  "Can I obtain a tax clearance certificate while an objection is in progress?",
  "Generally a tax clearance certificate is not issued when there is an active tax "
  "dispute or unsettled tax debt. TRA may have its own policies for specific circumstances. "
  "It is advisable to consult TRA directly about your individual situation.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA clearance policy update",
  "business_market", "standard"),

p("tier1a_tax_dispute_009_20260609","tax_disputes",
  "Baada ya TRAB, hatua inayofuata ya rufaa ya kodi ni ipi?",
  "Baada ya uamuzi wa TRAB, rufaa inayofuata ni kwa TRAT (Tax Revenue Appeals "
  "Tribunal). Kutoka TRAT, rufaa ya mwisho ni kwa Mahakama ya Rufaa ya Tanzania "
  "(Court of Appeal). Kila hatua inahitaji muda na kugharimu gharama za kisheria "
  "kubwa zaidi.",
  "After TRAB what is the next step in a tax appeal?",
  "After a TRAB decision the next appeal is to the TRAT (Tax Revenue Appeals "
  "Tribunal). From TRAT the final appeal is to Tanzania's Court of Appeal. Each "
  "step requires time and increasingly significant legal costs.",
  TANZLII, TANZLII_N, OG, "2001-01-01", ST, "Tax Revenue Appeals Act update",
  "formal", "standard"),

p("tier1a_tax_dispute_010_20260609","tax_disputes",
  "TRA inaweza kukagua biashara yangu bila notisi ya awali — je, hii inaruhusiwa?",
  "Ndiyo. TRA ina mamlaka ya kukagua biashara bila notisi ya awali katika hali "
  "fulani. Hata hivyo, kwa ukaguzi wa kawaida wa hesabu (audit), TRA mara nyingi "
  "hutoa notisi na ratiba. Wakaguzi wa TRA wana haki ya kuangalia rekodi za kodi, "
  "akaunti za benki, na hati za biashara.",
  "Can TRA audit my business without prior notice — is this permitted?",
  "Yes. TRA has authority to audit a business without prior notice in certain "
  "circumstances. However, for a routine accounts audit, TRA usually provides notice "
  "and a schedule. TRA auditors have the right to examine tax records, bank accounts, "
  "and business documents.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Administration Act update",
  "business_market", "standard"),

p("tier1a_tax_dispute_011_20260609","tax_disputes",
  "Muda wa kutuma pingamizi ni miezi 3 — je, hii ni sahihi?",
  "Hapana. Muda wa kutuma pingamizi kwa Kamishna Mkuu wa TRA ni siku 30 — si "
  "miezi 3. Siku 30 zinahesabika kutoka tarehe ya kupokea tathmini ya kodi. "
  "Miezi 3 ni muda tofauti unaohusiana na uamuzi wa Kamishna (ambao ni miezi 6), "
  "si muda wa kuwasilisha pingamizi.",
  "The objection filing period is 3 months — is this correct?",
  "No. The objection filing period with the TRA Commissioner General is 30 DAYS — "
  "not 3 months. The 30 days are counted from the date of receiving the tax "
  "assessment. Three months is a different period related to the Commissioner's "
  "decision timeframe (which is actually 6 months), not the filing deadline.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Revenue Appeals Act update",
  "business_market", "adversarial"),

p("tier1a_tax_dispute_012_20260609","tax_disputes",
  "Kampuni inaweza kupinga tathmini ya VAT tofauti na PAYE — inafanywa vipi?",
  "Ndiyo, kila aina ya tathmini inaweza kupingwa. Mchakato ni sawa kwa aina zote — "
  "wasilisha pingamizi kwa Kamishna Mkuu ndani ya siku 30 na ipe 1/3 ya kiasi "
  "kinachodaiwa. Tathmini tofauti (VAT, PAYE, kodi ya mapato) zinapiganwa tofauti "
  "na kila moja ina muda wake wa pingamizi.",
  "Can a company dispute a VAT assessment separately from a PAYE assessment — how is this done?",
  "Yes, each type of assessment can be disputed. The process is the same for all types "
  "— file an objection with the Commissioner General within 30 days and pay 1/3 of "
  "the disputed amount. Different assessments (VAT, PAYE, income tax) are disputed "
  "separately, each with its own objection timeline.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Revenue Appeals Act update",
  "formal", "standard"),

p("tier1a_tax_dispute_013_20260609","tax_disputes",
  "Kampuni inaweza kufikia makubaliano (settlement) na TRA nje ya mahakama — je, ni kweli?",
  "Ndiyo. TRA ina mchakato wa kusuluhisha migogoro ya kodi nje ya mahakama. "
  "Msuluhishi (alternative dispute resolution) unaweza kuwa wa haraka na wa bei nafuu "
  "kuliko kesi za mahakama. Makubaliano yanaweza kujumuisha kufuta sehemu ya adhabu "
  "au riba ikiwa msingi wa kodi unakubaliwa. Shauriana na mshauri wa kodi kwanza.",
  "Can a company reach a settlement with TRA outside of court — is this true?",
  "Yes. TRA has a process for settling tax disputes outside court. Alternative dispute "
  "resolution can be faster and less costly than court proceedings. Settlements may "
  "include waiving some penalties or interest if the underlying tax liability is "
  "accepted. Consult a tax adviser first.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA dispute resolution policy",
  "business_market", "standard"),

p("tier1a_tax_dispute_014_20260609","tax_disputes",
  "TRA inaweza kukamata mali za kampuni kama kodi haijalipiwa — je, ni kweli?",
  "Ndiyo. TRA ina mamlaka ya kisheria ya kuchukua hatua za makusanyo kwa kodi "
  "isiyolipwa, ikiwa ni pamoja na: kuzuia akaunti za benki, kukamata mali, na "
  "mauzo ya mali kwa minada. Hatua hizi zinaelekea kufuata notisi za onyo. "
  "Makubaliano ya malipo yanaweza kuzuia hatua hizi.",
  "Can TRA seize company assets if tax is not paid — is this true?",
  "Yes. TRA has legal authority to take collection action for unpaid tax, including: "
  "freezing bank accounts, seizing assets, and auctioning property. These steps "
  "typically follow warning notices. A payment arrangement can prevent these actions.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Administration Act update",
  "business_market", "standard"),

p("tier1a_tax_dispute_015_20260609","tax_disputes",
  "Ukaguzi wa TRA unachukua muda gani na ninaweza kufanya nini wakati wake?",
  "Ukaguzi wa TRA unaweza kuchukua wiki kadhaa hadi miezi kadhaa kulingana na ukubwa "
  "wa biashara na matatizo yanayopatikana. Wakati wa ukaguzi: weka rekodi zote sahihi "
  "na ziwepo, jibu maswali ya ukaguzi kwa wakati, unaweza kutumia mshauri wa kodi au "
  "wakili, na omba maelezo ya kila suala kabla ya kukubali matokeo.",
  "How long does a TRA audit take and what can I do during it?",
  "A TRA audit can take several weeks to several months depending on business size and "
  "issues found. During the audit: keep all records accurate and available, respond to "
  "audit questions promptly, you can engage a tax adviser or lawyer, and request "
  "explanations for each issue before accepting findings.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA audit procedure update",
  "formal", "standard"),

p("tier1a_tax_dispute_016_20260609","tax_disputes",
  "Pingamizi kwa TRA linamaanisha sina haja ya kulipa kodi yoyote mpaka uamuzi — je, ni kweli?",
  "Hapana. Pingamizi halisimamishi wajibu wako wa kulipa 1/3 ya kiasi kinachodaiwa "
  "NA kulipa kodi nyingine inayodaiwa ambayo haijapingwa. Riba na adhabu zinaendelea "
  "kukusanyika. Pingamizi linasimamisha tu hatua za makusanyo kwa kiasi "
  "kinachopingwa — si kodi yote.",
  "Filing an objection with TRA means I don't need to pay any tax until the decision — is this true?",
  "No. An objection does not suspend your obligation to pay 1/3 of the disputed amount "
  "AND to pay other undisputed tax owed. Interest and penalties continue to accrue. "
  "An objection only suspends collection action on the disputed amount — not all tax.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Revenue Appeals Act update",
  "formal", "adversarial"),

p("tier1a_tax_dispute_017_20260609","tax_disputes",
  "Tofauti kati ya tathmini (assessment) na ukaguzi (audit) ya TRA ni nini?",
  "Ukaguzi (audit) ni mchakato wa TRA wa kuchunguza rekodi za kodi za mlipaji kodi. "
  "Tathmini (assessment) ni uamuzi rasmi wa TRA unaosema kiasi cha kodi kinachostahili. "
  "Ukaguzi unaweza kusababisha tathmini ikiwa makosa yatapatikana. Tathmini ndiyo "
  "hati rasmi ambayo inaweza kupingwa ndani ya siku 30.",
  "What is the difference between a TRA assessment and an audit?",
  "An audit is TRA's process of examining a taxpayer's tax records. An assessment is "
  "TRA's formal decision stating the amount of tax owed. An audit can lead to an "
  "assessment if errors are found. An assessment is the formal document that can be "
  "objected to within 30 days.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Administration Act update",
  "formal", "disambiguation"),

p("tier1a_tax_dispute_018_20260609","tax_disputes",
  "Kiwango cha asilimia ya riba ya kisheria ya TRA kwenye kodi iliyochelewa ni asilimia ngapi?",
  "Riba ya kisheria ya TRA kwenye kodi iliyochelewa imewekwa kwa kiwango cha asilimia 5 "
  "kwa mwezi (au kiwango kinachotangazwa mara kwa mara). Hii inaendelea kukusanyika "
  "kwa kila mwezi wa ucheleweshaji. Ni muhimu kulipa kodi kwa wakati ili kuepuka "
  "mrundikano wa riba.",
  "What is the TRA statutory interest rate on overdue tax?",
  "TRA statutory interest on overdue tax is set at 5% per month (or the rate "
  "periodically announced). This continues to accrue for every month of delay. "
  "It is important to pay tax on time to avoid accumulating interest charges.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act interest rate update",
  "formal", "standard"),

p("tier1a_tax_dispute_019_20260609","tax_disputes",
  "TRAB inaweza kuamua dhidi ya TRA na kumpa mlipaji kodi ushindi kamili — je, ni kweli?",
  "Ndiyo. TRAB ni bodi huru ambayo inaweza kuamua dhidi ya TRA na kutoa ushindi "
  "kamili au sehemu ya ushindi kwa mlipaji kodi. Ikiwa TRAB ikitoa ushindi kamili, "
  "TRA inaweza kurudisha kiasi kilicholipwa na kufuta tathmini. TRAB ni njia muhimu "
  "ya kupata haki kwa mlipaji kodi.",
  "Can TRAB decide against TRA and give the taxpayer a complete win — is this true?",
  "Yes. TRAB is an independent board that can decide against TRA and award a complete "
  "or partial win to the taxpayer. If TRAB grants a complete win, TRA must refund "
  "amounts paid and cancel the assessment. TRAB is an important avenue for taxpayer "
  "justice.",
  TANZLII, TANZLII_N, OG, "2001-01-01", ST, "Tax Revenue Appeals Act update",
  "formal", "standard"),

p("tier1a_tax_dispute_020_20260609","tax_disputes",
  "Mashirika ya kidini na ya hisani (charitable) hayalazimishwi na mchakato wa pingamizi la kodi — je, ni kweli?",
  "Hapana. Mashirika ya kidini na ya hisani yanayolazimishwa na kodi au yanayopokea "
  "tathmini ya kodi (hata ikiwa yanaamini wana msamaha) yalazimike kufuata mchakato "
  "ule ule wa pingamizi — yaani kuwasilisha ndani ya siku 30 na kulipa 1/3. "
  "Madai ya msamaha yanashughulikiwa kama sehemu ya maudhui ya pingamizi.",
  "Religious and charitable organisations are not required to follow the tax objection process — is this true?",
  "No. Religious and charitable organisations that are assessed for tax (even if they "
  "believe they have an exemption) must follow the same objection process — filing "
  "within 30 days and paying 1/3. Exemption claims are addressed as part of the "
  "substance of the objection.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Revenue Appeals Act update",
  "formal", "adversarial"),

p("tier1a_tax_dispute_021_20260609","tax_disputes",
  "Niliweza kupata unafuu wa adhabu kutoka TRA — taratibu ni zipi?",
  "TRA inaweza kutoa unafuu wa adhabu (penalty remission) kwa sababu maalum kama: "
  "janga la asili, ugonjwa mbaya, au hali ya nguvu za mazingira (force majeure). "
  "Omba unafuu kwa maandishi kwa Kamishna Mkuu wa TRA ukieleza sababu. TRA "
  "itaangalia ombi na kutoa uamuzi. Hii si ya kawaida na inategemea hali halisi.",
  "I may be able to get penalty relief from TRA — what is the procedure?",
  "TRA can grant penalty remission for specific reasons such as: natural disaster, "
  "serious illness, or force majeure. Apply for remission in writing to the TRA "
  "Commissioner General explaining the reasons. TRA will review the application and "
  "issue a decision. This is uncommon and depends on the actual circumstances.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA remission policy",
  "business_market", "standard"),

p("tier1a_tax_dispute_022_20260609","tax_disputes",
  "Kampuni inaweza kutumia wakili binafsi katika kesi ya TRAB — je, ni kweli?",
  "Ndiyo. Mlipaji kodi ana haki ya kuwakilishwa na wakili, mshauri wa kodi, au "
  "mwakilishi mwingine aliyeidhinishwa katika kesi za TRAB. TRA pia ina washauri "
  "wake. Kuwa na uwakilishi mzuri wa kisheria kunaweza kuathiri sana matokeo ya kesi.",
  "Can a company use a private lawyer in a TRAB case — is this true?",
  "Yes. A taxpayer has the right to be represented by a lawyer, tax adviser, or other "
  "authorised representative in TRAB proceedings. TRA also has its own counsel. "
  "Having strong legal representation can significantly affect the outcome of a case.",
  TANZLII, TANZLII_N, OG, "2001-01-01", ST, "Tax Revenue Appeals Act update",
  "formal", "standard"),

p("tier1a_tax_dispute_023_20260609","tax_disputes",
  "Tathmini ya TRA ya miaka 5 iliyopita inaweza kupingwa — je, kuna kikomo cha muda?",
  "TRA ina muda wa miaka 5 kuwasilisha tathmini (limitation period) kwa makosa "
  "ya kawaida ya kodi. Hata hivyo, kwa udanganyifu au kutopiga kodi kwa makusudi, "
  "hakuna kikomo cha muda. Tathmini iliyotolewa ndani ya miaka 5 inaweza kupingwa "
  "ndani ya siku 30 za kuipokea.",
  "Can a TRA assessment for 5 years ago be disputed — is there a time limit?",
  "TRA has a 5-year limitation period to issue assessments for normal tax errors. "
  "However for fraud or willful non-declaration there is no time limit. An assessment "
  "issued within the 5-year period can be disputed within 30 days of receiving it.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Administration Act update",
  "formal", "standard"),

p("tier1a_tax_dispute_024_20260609","tax_disputes",
  "Kama TRA haikujibu pingamizi langu baada ya miezi 6, ninafanya nini?",
  "Ikiwa Kamishna Mkuu wa TRA hajatoa uamuzi ndani ya miezi 6, pingamizi "
  "linachukuliwa kama limekataliwa kisheria. Unaweza basi kukata rufaa moja kwa "
  "moja kwa TRAB ndani ya siku 45. Hakuna haja ya kusubiri muda zaidi — tuma "
  "rufaa yako kwa TRAB haraka.",
  "If TRA does not respond to my objection after 6 months what do I do?",
  "If the TRA Commissioner General has not issued a decision within 6 months, the "
  "objection is deemed rejected by law. You can then appeal directly to TRAB within "
  "45 days. There is no need to wait longer — file your TRAB appeal promptly.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Revenue Appeals Act update",
  "business_market", "standard"),

p("tier1a_tax_dispute_025_20260609","tax_disputes",
  "Muda wa pingamizi ni siku 90 — je, hii ni sahihi?",
  "Hapana. Muda wa kuwasilisha pingamizi kwa Kamishna Mkuu wa TRA ni siku 30 — "
  "si siku 90. Kama unachanganya muda huu na muda mwingine (kama miezi 6 ya "
  "uamuzi wa Kamishna au siku 45 za rufaa ya TRAB), ni muhimu kuzingatia muda "
  "sahihi kwa kila hatua.",
  "The objection period is 90 days — is this correct?",
  "No. The objection filing period with the TRA Commissioner General is 30 DAYS — "
  "not 90 days. If you are confusing this with other timeframes (such as the "
  "Commissioner's 6-month decision window or TRAB's 45-day appeal window), each "
  "step has its own specific deadline.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Revenue Appeals Act update",
  "formal", "adversarial"),

p("tier1a_tax_dispute_026_20260609","tax_disputes",
  "Kampuni inaweza kuendelea kufanya biashara wakati kesi ya kodi iko TRAB — je, ni kweli?",
  "Ndiyo kwa kawaida. Kesi ya kodi inayoendelea mbele ya TRAB haizuii kampuni "
  "kuendelea kufanya biashara. Hata hivyo, TRA inaweza kuchukua hatua za makusanyo "
  "kwa kiasi kisichopingwa au kisicholipwa. Cheti cha utii wa kodi kinaweza kuathirika.",
  "Can a company continue to operate while a tax case is before TRAB — is this true?",
  "Yes, generally. A pending TRAB tax case does not stop a company from continuing to "
  "operate. However, TRA can take collection action for undisputed or unpaid amounts. "
  "A tax clearance certificate may be affected.",
  TANZLII, TANZLII_N, OG, "2001-01-01", ST, "Tax Revenue Appeals Act update",
  "business_market", "standard"),

p("tier1a_tax_dispute_027_20260609","tax_disputes",
  "Makubaliano ya malipo (payment plan) na TRA yanaweza kupata — taratibu ni zipi?",
  "Kuomba makubaliano ya malipo na TRA: (1) wasiliana na TRA mapema kabla ya deni "
  "kuwa kubwa sana, (2) omba rasmi makubaliano ya malipo kwa maandishi ukieleza "
  "hali yako ya fedha, (3) wasilisha mapendekezo ya malipo ya awamu. TRA inaweza "
  "kukubali ikiwa una nia ya kweli ya kulipa.",
  "How can a payment arrangement with TRA be obtained — what is the procedure?",
  "To request a payment arrangement with TRA: (1) contact TRA early before the debt "
  "becomes very large, (2) formally request a payment arrangement in writing explaining "
  "your financial situation, (3) submit a proposed instalment payment schedule. TRA "
  "may agree if you demonstrate genuine intent to pay.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA enforcement policy",
  "business_market", "standard"),

p("tier1a_tax_dispute_028_20260609","tax_disputes",
  "Adhabu ya kutokuwasilisha taarifa ya kodi kwa TRA ni asilimia ngapi?",
  "Adhabu ya kutowasilisha taarifa ya kodi (failure to file return) inategemea aina "
  "ya kodi. Kwa kawaida ni faini ya kiasi maalum au asilimia ya kodi inayodaiwa, "
  "kulingana na aina ya kodi na muda wa ucheleweshaji. Angalia Sheria ya Usimamizi "
  "wa Kodi au wasiliana na TRA kwa kiwango maalum cha aina yako ya kodi.",
  "What is the penalty rate for not filing a tax return with TRA?",
  "The penalty for failure to file a tax return depends on the type of tax. It is "
  "generally a specified fixed amount or a percentage of the tax owed, depending on "
  "the tax type and duration of delay. Refer to the Tax Administration Act or "
  "contact TRA for the specific rate for your tax type.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act penalty update",
  "formal", "standard"),

p("tier1a_tax_dispute_029_20260609","tax_disputes",
  "Mashirika mapya ya biashara hayana ukaguzi wa TRA kwa miaka 3 ya kwanza — je, ni kweli?",
  "Hapana. Hakuna kanuni ya kisheria inayompa biashara mpya ruhusa ya miaka 3 bila "
  "ukaguzi wa TRA. TRA inaweza kukagua biashara yoyote — mpya au ya zamani — wakati "
  "wowote inapoona inafaa. Biashara mpya zinapaswa kuhifadhi rekodi sahihi tangu "
  "siku ya kwanza.",
  "New businesses are free from TRA audits for the first 3 years — is this true?",
  "No. There is no legal provision giving new businesses a 3-year audit exemption from "
  "TRA. TRA can audit any business — new or established — at any time it considers "
  "appropriate. New businesses must maintain accurate records from day one.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Administration Act update",
  "rural_conversational", "adversarial"),

p("tier1a_tax_dispute_030_20260609","tax_disputes",
  "Nini kinatokea ikiwa kampuni itashindwa kulipa 1/3 ya kodi inayodaiwa kwa ajili ya pingamizi?",
  "Ikiwa kampuni haikuweza kulipa 1/3 ya kiasi kinachodaiwa, pingamizi lake halikubaliwa "
  "na linachukuliwa kuwa halijatumwa. Tathmini inakuwa ya mwisho baada ya siku 30 "
  "kupita. Kampuni bado inaweza kuomba makubaliano ya malipo, lakini mchakato wa "
  "pingamizi wa kisheria utakuwa umefungwa.",
  "What happens if a company fails to pay the 1/3 of the disputed tax for an objection?",
  "If a company cannot pay 1/3 of the disputed amount, the objection is not accepted "
  "and is treated as not filed. The assessment becomes final after 30 days pass. "
  "The company can still seek a payment arrangement, but the formal objection "
  "process will be closed.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Revenue Appeals Act update",
  "business_market", "standard"),

p("tier1a_tax_dispute_031_20260609","tax_disputes",
  "Wakurugenzi wa kampuni wanabeba dhima ya kibinafsi kwa kodi za kampuni — je, ni kweli?",
  "Kwa kawaida hapana — kampuni ya kikomo cha dhima ina utu wa kisheria tofauti. "
  "Hata hivyo, kuna hali ambapo wakurugenzi wanabeba dhima ya kibinafsi kwa kodi "
  "kama: kwa ukweli wa udanganyifu, kwa PAYE isiyolipwa (kwa sababu ni pesa za "
  "wafanyakazi), au wakati kampuni inafanywa kuwa chombo cha kukwepa kodi. "
  "Shauriana na wakili wa kodi kwa hali yako.",
  "Company directors bear personal liability for company taxes — is this true?",
  "Generally no — a limited company has a separate legal personality. However, there "
  "are situations where directors can bear personal liability for taxes such as: for "
  "fraud, for unpaid PAYE (since it is employees' money), or when a company is used "
  "as a tax evasion vehicle. Consult a tax lawyer for your specific situation.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Administration Act update",
  "formal", "standard"),

p("tier1a_tax_dispute_032_20260609","tax_disputes",
  "TRAB na mahakama ya kawaida (High Court) vinafanana — je, ni kweli?",
  "Hapana. TRAB (Tax Revenue Appeals Board) ni bodi maalum ya kodi iliyoundwa chini "
  "ya Sheria ya Rufaa ya Mapato ya Kodi. Mahakama ya Juu (High Court) ni mahakama ya "
  "jumla. Rufaa za kodi lazima zianze TRAB kabla ya kwenda mahakama. Kutokupitia "
  "TRAB kwanza ni kukosa mchakato wa kawaida wa kisheria.",
  "TRAB and the ordinary court (High Court) are the same — is this true?",
  "No. TRAB (Tax Revenue Appeals Board) is a specialist tax board established under "
  "the Tax Revenue Appeals Act. The High Court is a general court. Tax appeals must "
  "start at TRAB before going to court. Bypassing TRAB is a failure to follow the "
  "proper legal process.",
  TANZLII, TANZLII_N, OG, "2001-01-01", ST, "Tax Revenue Appeals Act update",
  "formal", "disambiguation"),

p("tier1a_tax_dispute_033_20260609","tax_disputes",
  "Mtu mmoja mmoja anayepokea tathmini ya kodi ya kibinafsi anaweza kupinga vipi?",
  "Mtu mmoja mmoja anayepokea tathmini ya kodi ya kibinafsi (Personal Income Tax) "
  "anafuata mchakato ule ule wa pingamizi: (1) wasilisha pingamizi kwa Kamishna Mkuu "
  "ndani ya siku 30, (2) lipa 1/3 ya kiasi kinachodaiwa, na (3) subiri uamuzi wa "
  "Kamishna. Haki hizi zinatumika kwa watu binafsi na kampuni.",
  "How can an individual who receives a personal income tax assessment object?",
  "An individual receiving a personal income tax assessment follows the same objection "
  "process: (1) file an objection with the Commissioner General within 30 days, (2) "
  "pay 1/3 of the disputed amount, and (3) await the Commissioner's determination. "
  "These rights apply to both individuals and companies.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Revenue Appeals Act update",
  "rural_conversational", "standard"),

p("tier1a_tax_dispute_034_20260609","tax_disputes",
  "Kampuni inayopigwa kodi mara mbili (Tanzania na nchi nyingine) inafanya nini?",
  "Tanzania ina Mikataba ya Kuepuka Kutozwa Kodi Mara Mbili (DTA) na nchi kadhaa. "
  "Ikiwa mbia wako wa biashara katika nchi yenye DTA na Tanzania, angalia masharti "
  "ya DTA kwa unafuu wa kodi. Ikiwa hakuna DTA, unaweza kudai mkopo wa kodi "
  "ya nje (foreign tax credit) dhidi ya kodi ya Tanzania kulingana na sheria ya kodi.",
  "What should a company do if it is being taxed twice (Tanzania and another country)?",
  "Tanzania has Double Taxation Agreements (DTAs) with several countries. If your "
  "business partner is in a country with a DTA with Tanzania, check the DTA terms "
  "for tax relief. If there is no DTA, you may claim a foreign tax credit against "
  "Tanzania tax under tax law.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "DTA update",
  "formal", "standard"),

p("tier1a_tax_dispute_035_20260609","tax_disputes",
  "Ukaguzi wa TRA unavyopatikana ni tatizo — ninajua haki zangu wakati wa ukaguzi?",
  "Wakati wa ukaguzi wa TRA una haki ya: (1) kuomba kitambulisho cha mkaguzi, "
  "(2) kupata nakala ya hati yoyote inayochukuliwa, (3) kutumia mshauri wa kodi "
  "au wakili wakati wowote, (4) kutoa maelezo ya rekodi zako, na (5) kuomba "
  "maelezo ya matokeo ya ukaguzi kabla ya tathmini ya rasmi kutolewa.",
  "A TRA audit is underway — what are my rights during the audit?",
  "During a TRA audit you have the right to: (1) request the auditor's identification, "
  "(2) receive copies of any documents taken, (3) use a tax adviser or lawyer at any "
  "time, (4) provide explanations of your records, and (5) request explanation of "
  "audit findings before a formal assessment is issued.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Administration Act update",
  "business_market", "standard"),

p("tier1a_tax_dispute_036_20260609","tax_disputes",
  "Muda wa Kamishna kujibu pingamizi ni miezi 3 — je, ni sahihi?",
  "Hapana. Muda wa Kamishna Mkuu wa TRA kujibu pingamizi ni miezi 6 — si miezi 3. "
  "Baada ya miezi 6 bila jibu, pingamizi linachukuliwa kama limekataliwa na mlipaji "
  "kodi anaweza kwenda TRAB. Miezi 3 si muda sahihi kwa hatua hii.",
  "The Commissioner's response period for an objection is 3 months — is this correct?",
  "No. The TRA Commissioner General's response period for an objection is 6 MONTHS "
  "— not 3 months. After 6 months without a response the objection is deemed rejected "
  "and the taxpayer can proceed to TRAB. Three months is not the correct timeframe "
  "for this step.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Revenue Appeals Act update",
  "business_market", "adversarial"),

p("tier1a_tax_dispute_037_20260609","tax_disputes",
  "Ikiwa TRAB imeniamua vibaya, hii ni uamuzi wa mwisho kabisa — je, ni kweli?",
  "Hapana. Uamuzi wa TRAB unaweza kupingwa kwa rufaa mbele ya TRAT (Tax Revenue "
  "Appeals Tribunal). Kutoka TRAT, rufaa ya mwisho ipo mbele ya Mahakama ya Rufaa "
  "(Court of Appeal). Kila hatua inahitaji sababu za kisheria za kutosha na gharama "
  "za ziada za kisheria.",
  "If TRAB decides against me this is the absolute final decision — is this true?",
  "No. A TRAB decision can be challenged by appeal before the TRAT (Tax Revenue "
  "Appeals Tribunal). From TRAT the final appeal lies before the Court of Appeal. "
  "Each step requires sufficient legal grounds and additional legal costs.",
  TANZLII, TANZLII_N, OG, "2001-01-01", ST, "Tax Revenue Appeals Act update",
  "formal", "adversarial"),

p("tier1a_tax_dispute_038_20260609","tax_disputes",
  "Mtu anayeweka taarifa ya kodi ya uongo anaweza kuadhibiwa vipi?",
  "Kutoa taarifa ya kodi ya uongo au kupotosha TRA ni kosa la jinai chini ya Sheria "
  "ya Usimamizi wa Kodi. Adhabu zinaweza kujumuisha: faini kubwa, malipo ya kodi "
  "iliyokosekana na riba, na kifungo cha jela. Mlipaji kodi anayegundua makosa na "
  "kujirekebisha kwa hiari ana uwezekano wa kupata adhabu ndogo.",
  "What penalties can a person who files a false tax return face?",
  "Filing a false tax return or misleading TRA is a criminal offence under the Tax "
  "Administration Act. Penalties can include: large fines, payment of unpaid tax with "
  "interest, and imprisonment. A taxpayer who discovers errors and self-corrects "
  "voluntarily has a possibility of reduced penalties.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Administration Act update",
  "formal", "standard"),

p("tier1a_tax_dispute_039_20260609","tax_disputes",
  "Unaweza kupinga tathmini ya kodi hata kama umekubali awali — je, ni kweli?",
  "Kwa kawaida hapana. Ukisha kukubali tathmini na kuisaini, inakuwa ya mwisho. "
  "Kupinga baadaye ni ngumu isipokuwa kama kuna ushahidi wa udanganyifu, makosa "
  "ya wazi ya kisheria, au hali nyingine maalum. Ni muhimu kusoma na kuelewa "
  "tathmini yoyote kabla ya kuisaini au kukubali.",
  "Can you dispute a tax assessment even after initially accepting it — is this true?",
  "Generally no. Once you have accepted and signed an assessment it becomes final. "
  "Challenging it later is difficult unless there is evidence of fraud, clear legal "
  "error, or other special circumstances. It is critical to read and understand any "
  "assessment before signing or accepting it.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Revenue Appeals Act update",
  "formal", "adversarial"),

p("tier1a_tax_dispute_040_20260609","tax_disputes",
  "Muda mzima wa mchakato wa kupinga kodi kutoka tathmini hadi Mahakama ya Rufaa unaweza kuchukua muda gani?",
  "Mchakato mzima unaweza kuchukua miaka mingi: pingamizi (miezi 6 ya Kamishna) + "
  "TRAB (miezi 6-12 ya kusikilizwa) + TRAT (miaka 1-2) + Mahakama ya Rufaa "
  "(miaka 2-5). Kwa jumla, kesi ngumu ya kodi inaweza kuchukua miaka 5-10 hadi "
  "kupata uamuzi wa mwisho. Makubaliano ya mapema ni ya busara mara nyingi.",
  "How long can the full tax dispute process from assessment to Court of Appeal take?",
  "The full process can take many years: objection (Commissioner's 6 months) + TRAB "
  "(6-12 months of hearings) + TRAT (1-2 years) + Court of Appeal (2-5 years). "
  "Overall, a complex tax case can take 5-10 years to reach a final decision. "
  "Early settlement is often prudent.",
  TANZLII, TANZLII_N, OG, "2001-01-01", ST, "Tax Revenue Appeals Act update",
  "formal", "standard"),

# =====================================================================
# 10 mixed rural_conversational pairs to ensure ≥20% register target
# Covering: VAT, PAYE, SDL, NSSF, BRELA basics in simple Swahili
# =====================================================================

p("tier1a_mix_rc_001_20260609","gn605a_minimum_wage",
  "Boss wangu analipa chini ya GN 605A — ninafanya nini?",
  "Ukijua mshahara wako uko chini ya kiwango cha GN 605A, una haki ya kudai "
  "tofauti. Kwanza, zungumza na mwajiri wako kwa amani. Kama hajabadilisha hali, "
  "unaweza kwenda Ofisi ya Kazi ya karibu nawe (Labour Office) au Kamati ya "
  "Usuluhishi wa Migogoro ya Kazi (CMA) kudai malipo yako. Huna haja ya wakili.",
  "My employer is paying below GN 605A — what do I do?",
  "If you know your salary is below the GN 605A rate, you have the right to claim "
  "the shortfall. First, speak with your employer peacefully. If they don't change, "
  "you can go to the nearest Labour Office or the Commission for Mediation and "
  "Arbitration (CMA) to claim your pay. You don't need a lawyer.",
  "https://www.mlywf.go.tz", ML_N, GP, "2026-01-01", EVT,
  "Next wage order gazette", "rural_conversational", "standard"),

p("tier1a_mix_rc_002_20260609","vat_registration",
  "Duka langu linauza Shilingi 250M kwa mwaka — lazima niandikishe VAT?",
  "Ndiyo. Ukizidi Shilingi 200M kwa mwaka au Shilingi 100M kwa miezi 6, lazima "
  "uandikishe VAT na TRA. Duka lako la Shilingi 250M linazidi kizingiti cha Shilingi "
  "200M kwa mwaka, kwa hivyo uandikishe sasa hivi. Ukichelewa, unaweza kupata adhabu.",
  "My shop sells TZS 250M per year — must I register for VAT?",
  "Yes. If you exceed TZS 200M per year or TZS 100M in 6 months, you must register "
  "for VAT with TRA. Your shop at TZS 250M exceeds the TZS 200M annual threshold, "
  "so you should register now. Late registration can result in penalties.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act VAT threshold change",
  "rural_conversational", "standard"),

p("tier1a_mix_rc_003_20260609","nssf_contributions",
  "Mfanyakazi wangu anakataa kuchangia NSSF — ninafanya nini?",
  "Mchango wa NSSF ni wa lazima kisheria kwa wafanyakazi wote. Mfanyakazi "
  "hawezi kukataa mchango wa NSSF — ni wajibu wa kisheria wa mwajiri KUKATA "
  "mchango wa mfanyakazi (asilimia 10) na KUONGEZA mchango wa mwajiri (asilimia 10) "
  "na kumpelekea NSSF. Mfanyakazi kukubali au la si sharti.",
  "My employee refuses to contribute to NSSF — what do I do?",
  "NSSF contributions are legally mandatory for all employees. An employee cannot "
  "refuse NSSF contributions — it is the employer's legal obligation to DEDUCT the "
  "employee's contribution (10%) and ADD the employer's contribution (10%) and "
  "remit to NSSF. The employee's agreement is not a condition.",
  "https://www.nssf.or.tz", "NSSF — National Social Security Fund",
  GP, "2018-01-01", ANN, "NSSF Act amendment",
  "rural_conversational", "standard"),

p("tier1a_mix_rc_004_20260609","paye_adversarial",
  "Ninasikia PAYE inabadilika kila mwaka — kanda za sasa ni zipi?",
  "Kanda za PAYE za sasa kwa mwezi ni: asilimia 0 (hadi Shilingi 270,000), asilimia "
  "8 (Shilingi 270,001 hadi 520,000), asilimia 20 (Shilingi 520,001 hadi 760,000), "
  "asilimia 25 (Shilingi 760,001 hadi 1,000,000), na asilimia 30 (zaidi ya "
  "Shilingi 1,000,000). Hizi ndizo kanda za Finance Act ya sasa.",
  "I hear PAYE changes every year — what are the current bands?",
  "The current monthly PAYE bands are: 0% (up to TZS 270,000), 8% (TZS 270,001 to "
  "520,000), 20% (TZS 520,001 to 760,000), 25% (TZS 760,001 to 1,000,000), and 30% "
  "(above TZS 1,000,000). These are the current Finance Act bands.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act PAYE band change",
  "rural_conversational", "standard"),

p("tier1a_mix_rc_005_20260609","osha_registration",
  "Ninaendesha mkahawa mdogo na wafanyakazi 12 — OSHA inanifikiria?",
  "Ndiyo. Mkahawa wenye wafanyakazi 12 unazidi kizingiti cha OSHA cha wafanyakazi "
  "10. Lazima usajili mkahawa wako na OSHA na upate cheti cha OSHA. Pia "
  "unahitaji msaada wa kwanza (first aid kit) na kuhakikisha jiko na "
  "mazingira ya kazi ni salama.",
  "I run a small café with 12 staff — does OSHA apply to me?",
  "Yes. A café with 12 employees exceeds the OSHA threshold of 10. You must register "
  "your café with OSHA and obtain an OSHA certificate. You also need first aid "
  "supplies and must ensure the kitchen and working environment are safe.",
  "https://www.osha.go.tz", OSHA_N, GP, "2003-07-01", ANN,
  "OSHA Act amendment", "rural_conversational", "standard"),

p("tier1a_mix_rc_006_20260609","brela_registration",
  "Nataka kufungua biashara ya kuuza nguo — ninahitaji nini BRELA?",
  "Kwa biashara ya nguo, unahitaji kusajili jina la biashara au kampuni na BRELA. "
  "Hatua ni: (1) chagua jina na lilithbitishe BRELA halijachukuliwa, (2) wasilisha "
  "fomu ya usajili na ada (karibu Shilingi 20,000-50,000), (3) pata cheti cha "
  "usajili. Kisha nenda TRA kwa TIN na leseni ya biashara ya manispaa.",
  "I want to start a clothes selling business — what do I need from BRELA?",
  "For a clothes business you need to register a business name or company with BRELA. "
  "The steps are: (1) choose a name and confirm with BRELA it is not taken, (2) submit "
  "the registration form and fee (approximately TZS 20,000-50,000), (3) receive your "
  "registration certificate. Then go to TRA for a TIN and the municipal trading licence.",
  "https://www.brela.go.tz", BRELA_N, GP, "2002-01-01", ANN,
  "BRELA fee schedule update", "rural_conversational", "standard"),

p("tier1a_mix_rc_007_20260609","wcf_compliance",
  "Mfanyakazi wangu alianguka na kuumia dukani — WCF inasaidiaje?",
  "Taarisha WCF kuhusu ajali hii ndani ya siku 30. WCF italipa: gharama za hospitali "
  "na dawa, na posho ya mfanyakazi wakati wa kupumzika kutokana na majeraha. "
  "Pia taarisha OSHA kama majeraha ni makubwa — ndani ya masaa 24. Hifadhi "
  "nyaraka zote za hospitali kama ushahidi.",
  "My employee fell and was injured in the shop — how does WCF help?",
  "Report the accident to WCF within 30 days. WCF will pay: hospital and medicine "
  "costs, and an allowance for the employee during recovery. Also notify OSHA "
  "if the injuries are serious — within 24 hours. Keep all hospital documents "
  "as evidence.",
  ML, ML_N, GP, "2008-01-01", ST, "Workers Compensation Act amendment",
  "rural_conversational", "standard"),

p("tier1a_mix_rc_008_20260609","tax_disputes",
  "TRA imeniandikia barua ya kodi ya ziada — nifanye nini kwanza?",
  "Soma barua kwa makini. Kama ni tathmini ya kodi inayosema unadaiwa kiasi fulani, "
  "una siku 30 tu kupinga (objection). Kama hujui tathmini ni sahihi au la, "
  "peleka barua kwa mshauri wa kodi au akaunti haraka. Usikae bila kuchukua hatua "
  "— siku 30 zinapita haraka.",
  "TRA has written me a letter about additional tax — what should I do first?",
  "Read the letter carefully. If it is a tax assessment stating you owe a certain "
  "amount, you have only 30 days to object. If you're not sure whether the assessment "
  "is correct, take the letter to a tax adviser or accountant quickly. Don't sit idle "
  "— 30 days passes fast.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Tax Revenue Appeals Act update",
  "rural_conversational", "standard"),

p("tier1a_mix_rc_009_20260609","gn605a_minimum_wage",
  "Nina biashara ya usafiri (bodaboda 5) — wapanda bodaboda wangu wana haki ya mshahara wa chini?",
  "Kama wapanda bodaboda wako ni WAFANYAKAZI (unawalipa mshahara), ndio — wana haki "
  "ya mshahara wa chini wa GN 605A kwa sekta ya usafiri. Kama ni WAFANYABIASHARA "
  "HURU (wanakupa sehemu ya mapato), wanachukuliwa kama wajibu wao wenyewe — "
  "si wafanyakazi. Aina ya uhusiano wa ajira ndiyo inayoamua.",
  "I run a transport business (5 motorbikes) — do my riders have a right to minimum wage?",
  "If your riders are EMPLOYEES (you pay them a salary), yes — they have a right to "
  "the GN 605A minimum wage for the transport sector. If they are SELF-EMPLOYED "
  "(they pay you a share of income), they are treated as independent — not employees. "
  "The nature of the employment relationship determines this.",
  "https://www.mlywf.go.tz", ML_N, GP, "2026-01-01", EVT,
  "Next wage order gazette", "rural_conversational", "standard"),

p("tier1a_mix_rc_010_20260609","sdl_compliance",
  "Ninafanya biashara ya usafi — wafanyakazi 15. Je, ninalipa SDL?",
  "Ndiyo. SDL (Skills Development Levy) inatakiwa kwa waajiri wenye wafanyakazi "
  "10 au zaidi. Una wafanyakazi 15, kwa hivyo unalipa SDL. Kiwango ni asilimia 3.5 "
  "ya jumla ya mshahara wote wa wafanyakazi wako. Inalipwa TRA pamoja na PAYE "
  "kila mwezi ifikapo tarehe 7.",
  "I run a cleaning business — 15 employees. Do I pay SDL?",
  "Yes. SDL (Skills Development Levy) is required for employers with 10 or more "
  "employees. You have 15 staff, so you pay SDL. The rate is 3.5% of total wages "
  "paid to all employees. It is paid to TRA together with PAYE every month by "
  "the 7th.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act SDL threshold change",
  "rural_conversational", "standard"),

]

written = 0
with open(OUT, "a", encoding="utf-8") as f:
    for pr in pairs:
        f.write(json.dumps(pr, ensure_ascii=False) + "\n")
        written += 1

total = sum(1 for _ in open(OUT, encoding="utf-8") if _.strip())
print(f"Part 6: wrote {written} pairs")
print(f"Total in file: {total}")
