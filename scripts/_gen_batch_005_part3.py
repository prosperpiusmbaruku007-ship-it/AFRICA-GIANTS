#!/usr/bin/env python3
"""batch_005 part 3 — stamp_duty_deep (50 pairs, 101-150)"""
import json, os

OUT = "datasets/tier1a/raw_sources/raw_pairs_batch_005.jsonl"
D = "2026-06-09"
TRA_SD = "https://www.tra.go.tz/page/stamp-duty"
TRA_SD_N = "Tanzania Revenue Authority — Stamp Duty"
TANZLII = "https://www.tanzlii.org"
TANZLII_N = "TanzLII — Tanzania Legal Information Institute"
GP = "government_portal"
OG = "official_gazette"
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
# STAMP DUTY DEEP — 50 pairs (101-150)
# Source: TRA Stamp Duty page | Stamp Duty Act Tanzania
# =====================================================================

p("tier1a_stamp_duty_101_20260609","stamp_duty",
  "Ushuru wa stempu kwenye uhamishaji wa ardhi au majengo Tanzania ni asilimia ngapi?",
  "Ushuru wa stempu kwenye uhamishaji wa ardhi au majengo Tanzania ni asilimia 1 BAPA "
  "(flat rate) ya thamani ya malipo au thamani ya soko — whichever is higher. Hakuna "
  "kiwango cha ngazi (tiered) kama 0.5% kwa sehemu ya kwanza. Asilimia 1 inatumika "
  "kwenye thamani yote ya uhamishaji.",
  "What is the stamp duty rate on transfer of land or buildings in Tanzania?",
  "Stamp duty on transfer of land or buildings in Tanzania is a FLAT 1% of the "
  "consideration or market value — whichever is higher. There is no tiered structure "
  "such as 0.5% on the first portion. The 1% applies on the full transfer value.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Finance Act or Stamp Duty Act amendment",
  "business_market", "standard"),

p("tier1a_stamp_duty_102_20260609","stamp_duty",
  "Ushuru wa stempu Tanzania unatumika kwa nyaraka zipi kuu?",
  "Ushuru wa stempu Tanzania unatumika kwa nyaraka kuu hizi: (1) hati za uhamishaji "
  "wa ardhi na majengo, (2) makubaliano ya ukodishaji (lease agreements) ya muda "
  "mrefu, (3) hati za ushirika wa biashara (partnership deeds), (4) hati za mkopo na "
  "dhamana, (5) hati za kubadilishana (exchange deeds), na (6) nyaraka nyingine "
  "zilizotajwa kwenye Jedwali la Sheria ya Ushuru wa Stempu.",
  "What are the main documents subject to stamp duty in Tanzania?",
  "Stamp duty in Tanzania applies to these main documents: (1) land and building "
  "transfer deeds, (2) long-term lease agreements, (3) business partnership deeds, "
  "(4) loan and security documents, (5) exchange deeds, and (6) other instruments "
  "listed in the Schedule of the Stamp Duty Act.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act amendment",
  "formal", "standard"),

p("tier1a_stamp_duty_103_20260609","stamp_duty",
  "Mkataba wa kukodisha (lease) kwa miaka miwili au chini ya miaka miwili una "
  "ushuru wa stempu Tanzania?",
  "Mkataba wa kukodisha wa muda mfupi (kawaida chini ya miaka mitatu) unaweza "
  "kuwa na ushuru wa stempu wa chini au kusamehewa kulingana na Sheria ya Ushuru "
  "wa Stempu Tanzania. Mikataba ya kukodisha ya muda mrefu (kawaida miaka mitatu "
  "au zaidi) ina ushuru wa stempu unaohesabiwa kwa kuzingatia muda wa mkataba na "
  "kiwango cha pango. Angalia TRA kwa jedwali la hali ya sasa.",
  "Does a lease contract for two years or less attract stamp duty in Tanzania?",
  "A short-term lease (generally less than three years) may attract lower stamp duty "
  "or be exempt depending on the Tanzania Stamp Duty Act. Long-term leases (generally "
  "three years or more) carry stamp duty calculated based on the duration and rent "
  "amount. Check TRA for the current schedule.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act amendment",
  "formal", "standard"),

p("tier1a_stamp_duty_104_20260609","stamp_duty",
  "Ushuru wa stempu hulipwa na nani — mnunuzi au muuzaji?",
  "Kwa kawaida Tanzania, ushuru wa stempu kwenye uhamishaji wa ardhi hulipwa na "
  "MNUNUZI (mpokeaji wa hati). Hata hivyo, pande zote mbili zinaweza kukubaliana "
  "juu ya mgawanyo wa gharama hii katika mkataba wa mauzo. TRA inatazamia kwamba "
  "ushuru umelipwa kabla ya hati kusajiliwa au kutumika kisheria.",
  "Who pays stamp duty — the buyer or the seller?",
  "Generally in Tanzania, stamp duty on land transfer is paid by the BUYER (the "
  "recipient of the instrument). However, both parties can agree on how to share "
  "this cost in the sale agreement. TRA expects the duty to be paid before the "
  "instrument is registered or used legally.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act amendment",
  "business_market", "standard"),

p("tier1a_stamp_duty_105_20260609","stamp_duty",
  "Ushuru wa stempu unalipwa lini — kabla au baada ya kusaini mkataba?",
  "Ushuru wa stempu Tanzania kwa kawaida unahitajika kulipwa KABLA ya hati "
  "kusajiliwa rasmi au kabla ya kutumika katika mahakama. Hati ambayo haijalipwa "
  "ushuru wa stempu inaweza kukosa nguvu ya kisheria au kukataliwi katika "
  "mahakama. Ni busara kulipa ushuru wa stempu mara baada ya kusainiwa hati "
  "ili hati iwe na nguvu ya kisheria kamili.",
  "When is stamp duty paid — before or after signing a contract?",
  "Stamp duty in Tanzania is generally required to be paid BEFORE the instrument "
  "is formally registered or before it is used in court. An instrument that has "
  "not had stamp duty paid may lack legal force or be rejected in court. It is "
  "advisable to pay stamp duty promptly after signing so the instrument has full "
  "legal effect.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act amendment",
  "business_market", "standard"),

p("tier1a_stamp_duty_106_20260609","stamp_duty",
  "Hati ya uhamishaji wa hisa za kampuni (share transfer) ina ushuru wa stempu Tanzania?",
  "Ndiyo. Uhamishaji wa hisa za kampuni Tanzania una ushuru wa stempu. Ushuru "
  "huu unahesabiwa kwa asilimia ya thamani ya hisa zinazohamishwa. Kampuni na "
  "washirika wanapaswa kuhakikisha hati za uhamishaji wa hisa zimesajiliwa ipasavyo "
  "na ushuru wa stempu umelipwa ili uhamishaji uwe na nguvu ya kisheria.",
  "Does a company share transfer instrument attract stamp duty in Tanzania?",
  "Yes. Transfer of company shares in Tanzania attracts stamp duty. This is calculated "
  "at a percentage of the value of shares being transferred. Companies and shareholders "
  "should ensure share transfer instruments are properly stamped and registered so "
  "the transfer has full legal effect.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act or Companies Act amendment",
  "formal", "standard"),

p("tier1a_stamp_duty_107_20260609","stamp_duty",
  "Ushuru wa stempu unapunguzwa ikiwa ardhi inahamishwa kama zawadi (gift) kati "
  "ya familia — je, kuna msamaha?",
  "Tanzania inaweza kuwa na masharti maalum ya ushuru wa stempu kwa uhamisho wa "
  "zawadi (gift) kati ya wanafamilia wa karibu — lakini hii inategemea Sheria ya "
  "Ushuru wa Stempu na masharti yake. Sio msamaha wa kawaida unaotumika moja kwa "
  "moja. Angalia TRA au mwanasheria wa mali kwa hali yako mahususi kwani masharti "
  "yanaweza kuhitajika.",
  "Is stamp duty reduced when land is transferred as a gift between family members "
  "— is there an exemption?",
  "Tanzania may have specific stamp duty provisions for gift transfers between close "
  "family members — but this depends on the Stamp Duty Act and its conditions. It "
  "is not a blanket exemption that applies automatically. Check TRA or a property "
  "lawyer for your specific situation as conditions may be required.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act amendment",
  "formal", "standard"),

p("tier1a_stamp_duty_108_20260609","stamp_duty",
  "Ushuru wa stempu Tanzania ni asilimia 0.5% ya thamani ya nusu ya kwanza ya "
  "ardhi na asilimia 1% ya thamani inayobaki — je, ni sahihi?",
  "Hapana. Ushuru wa stempu kwenye uhamishaji wa ardhi Tanzania ni BAPA asilimia 1 "
  "kwenye thamani yote — hakuna mfumo wa ngazi (tiered) wa 0.5% na 1%. Kiwango "
  "kimoja cha asilimia 1 kinatumika kwenye thamani yote ya uhamishaji bila kujali "
  "kiasi chake.",
  "Tanzania stamp duty is 0.5% on the first half of the land value and 1% on the "
  "remainder — is this correct?",
  "No. Stamp duty on land transfer in Tanzania is a FLAT 1% on the full value — there "
  "is no tiered structure of 0.5% and 1%. A single 1% rate applies on the total "
  "transfer value regardless of amount.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Finance Act or Stamp Duty Act amendment",
  "business_market", "adversarial"),

p("tier1a_stamp_duty_109_20260609","stamp_duty",
  "Mkataba wa biashara ambao pande mbili zinasaini Tanzania unahitaji ushuru wa "
  "stempu kiotomatiki?",
  "Si kila mkataba wa biashara unahitaji ushuru wa stempu Tanzania. Sheria ya Ushuru "
  "wa Stempu inaorodhesha nyaraka MAALUM zinazohitaji kupigwa stempu — kama hati za "
  "uhamishaji wa ardhi, dhamana, na mikataba maalum. Mikataba ya kawaida ya utoaji "
  "wa huduma au bidhaa kati ya makampuni mawili inaweza isihitaji ushuru wa stempu. "
  "Angalia jedwali la Sheria ya Ushuru wa Stempu kwa aina yako ya mkataba.",
  "Does a business contract signed by two parties in Tanzania automatically require "
  "stamp duty?",
  "Not every business contract requires stamp duty in Tanzania. The Stamp Duty Act "
  "lists SPECIFIC instruments that need to be stamped — such as land transfer deeds, "
  "securities, and specified contracts. Ordinary service or goods contracts between "
  "two companies may not require stamp duty. Check the schedule of the Stamp Duty "
  "Act for your type of contract.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act amendment",
  "business_market", "disambiguation"),

p("tier1a_stamp_duty_110_20260609","stamp_duty",
  "Hati ya kukopa (loan agreement) kati ya kampuni mbili za Tanzania ina ushuru "
  "wa stempu?",
  "Ndiyo. Mikataba ya mkopo na dhamana Tanzania kwa kawaida iko kwenye orodha ya "
  "Sheria ya Ushuru wa Stempu. Ushuru huu unahesabiwa kwa kuzingatia kiasi cha mkopo "
  "au thamani ya dhamana. Kampuni zinazofanya makubaliano ya mkopo zinapaswa kuhakikisha "
  "ushuru wa stempu umelipwa ili mkopo uwe na nguvu kamili ya kisheria.",
  "Does a loan agreement between two Tanzania companies attract stamp duty?",
  "Yes. Loan agreements and security documents in Tanzania are generally listed in "
  "the Stamp Duty Act schedule. The duty is calculated based on the loan amount or "
  "security value. Companies entering loan agreements should ensure stamp duty is "
  "paid so the loan has full legal enforceability.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act amendment",
  "formal", "standard"),

p("tier1a_stamp_duty_111_20260609","stamp_duty",
  "Je, ushuru wa stempu unaweza kuepukwa kwa kuandika mkataba nje ya Tanzania?",
  "Hapana. Kufanya au kusaini mkataba nje ya Tanzania HAKUEPUSHI ushuru wa stempu "
  "Tanzania ikiwa mkataba unatumika au unatekelezwa Tanzania. Sheria ya Ushuru wa "
  "Stempu Tanzania inashughulikia nyaraka zinazohusiana na mali au biashara Tanzania "
  "bila kujali mahali ziliposainiwa.",
  "Can stamp duty be avoided by writing a contract outside Tanzania?",
  "No. Signing or drafting a contract outside Tanzania does NOT avoid Tanzania stamp "
  "duty if the contract is used or executed in Tanzania. The Tanzania Stamp Duty Act "
  "covers instruments relating to Tanzania property or business regardless of where "
  "they were signed.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act amendment",
  "formal", "adversarial"),

p("tier1a_stamp_duty_112_20260609","stamp_duty",
  "Ushuru wa stempu unalipwa kwa TRA vipi — mchakato ni upi?",
  "Mchakato wa kulipa ushuru wa stempu Tanzania: (1) amua kiasi cha ushuru kinachohitajika "
  "kulingana na aina ya hati na thamani, (2) tembelea ofisi ya TRA au tumia mfumo wa "
  "mtandaoni wa TRA kupata PRN (Payment Reference Number), (3) lipa kupitia benki "
  "iliyoidhinishwa au mfumo wa e-payment, (4) hati yako inachapishwa/kupigiwa muhuri "
  "wa stempu na TRA kama uthibitisho wa malipo.",
  "How is stamp duty paid to TRA — what is the process?",
  "Stamp duty payment process in Tanzania: (1) determine the required duty amount "
  "based on instrument type and value, (2) visit a TRA office or use the TRA online "
  "system to get a PRN (Payment Reference Number), (3) pay through an authorised "
  "bank or e-payment system, (4) your instrument is stamped or endorsed by TRA as "
  "proof of payment.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "TRA process update",
  "business_market", "standard"),

p("tier1a_stamp_duty_113_20260609","stamp_duty",
  "Hati isiyolipwa ushuru wa stempu inaweza kutumika kama ushahidi mahakamani?",
  "Hapana kwa ujumla. Hati ambayo inahitaji ushuru wa stempu lakini haijalipwa "
  "inaweza kukataliwi kama ushahidi mahakamani Tanzania. Mahakama inaweza kukataa "
  "kulazimisha hati ambayo haijakubaliwa ipasavyo. Hata hivyo, inaweza kuwa na "
  "nafasi ya 'kuimarisha' hati (impounding) kwa kulipa ushuru uliokosekana pamoja "
  "na adhabu.",
  "Can an unstamped instrument be used as evidence in court?",
  "Generally no. An instrument that requires stamp duty but has not been stamped can "
  "be rejected as evidence in Tanzania court. Courts may refuse to enforce an improperly "
  "stamped document. However, there may be a possibility to 'impound' the instrument "
  "by paying the outstanding duty plus penalties.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act amendment",
  "formal", "standard"),

p("tier1a_stamp_duty_114_20260609","stamp_duty",
  "Hati ya ukodishaji (tenancy agreement) ya nyumba ya kawaida ya kaya inahitaji "
  "ushuru wa stempu Tanzania?",
  "Makubaliano ya ukodishaji wa nyumba ya makazi (residential tenancy) ya muda mfupi "
  "kwa kawaida yanaweza yasiwe kwenye orodha ya nyaraka zinazohitaji ushuru wa stempu "
  "au yawe na ushuru mdogo Tanzania. Hata hivyo, mikataba ya kukodisha ya muda mrefu "
  "ya mali za kibiashara kwa kawaida ina ushuru wa stempu. Angalia Sheria ya Ushuru "
  "wa Stempu au TRA kwa mwongozo wa hali yako.",
  "Does a regular residential tenancy agreement require stamp duty in Tanzania?",
  "Short-term residential tenancy agreements may not be listed in the stamp duty "
  "schedule or may attract minimal duty in Tanzania. However, long-term commercial "
  "property leases typically carry stamp duty. Check the Stamp Duty Act or TRA "
  "for guidance on your specific situation.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act amendment",
  "rural_conversational", "standard"),

p("tier1a_stamp_duty_115_20260609","stamp_duty",
  "Adhabu ya kutolipa ushuru wa stempu kwa wakati Tanzania ni nini?",
  "Adhabu ya kutolipa ushuru wa stempu kwa wakati Tanzania inajumuisha: riba kwenye "
  "kiasi kilichochelewa, adhabu ya ziada inayoweza kuhesabiwa kama asilimia ya ushuru "
  "uliochelewa. Pia hati inaweza kukosaushuru wa kutosha na kuathiri nguvu yake ya "
  "kisheria. Kulipa mapema na kupata hati kupigiwa muhuri ni njia ya kuzuia adhabu hizi.",
  "What is the penalty for not paying stamp duty on time in Tanzania?",
  "The penalty for late stamp duty payment in Tanzania includes: interest on the "
  "overdue amount, and an additional penalty which may be calculated as a percentage "
  "of the overdue duty. Also the instrument may be insufficiently stamped and its "
  "legal force affected. Paying promptly and having the instrument stamped is the "
  "way to avoid these penalties.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act or Tax Administration Act update",
  "business_market", "standard"),

p("tier1a_stamp_duty_116_20260609","stamp_duty",
  "Uhamishaji wa ardhi kati ya kampuni mama na tanzu yake (subsidiary) una ushuru "
  "wa stempu Tanzania?",
  "Ndiyo kwa ujumla. Uhamishaji wa ardhi kati ya kampuni mbili za Tanzania — hata "
  "kama ni kampuni mama na tanzu — una ushuru wa stempu wa asilimia 1. Misamaha "
  "maalum ya kikundi cha kampuni (group relief) inaweza kutumika katika hali fulani, "
  "lakini si moja kwa moja. Omba ushauri wa mwanasheria wa kodi au TRA kabla ya "
  "mauzo ya ndani ya kikundi.",
  "Does a land transfer between a parent company and its subsidiary attract stamp "
  "duty in Tanzania?",
  "Yes generally. A land transfer between two Tanzania companies — even parent and "
  "subsidiary — attracts 1% stamp duty. Specific group relief exemptions may apply "
  "in certain circumstances but are not automatic. Seek advice from a tax lawyer "
  "or TRA before intra-group transfers.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act amendment",
  "formal", "standard"),

p("tier1a_stamp_duty_117_20260609","stamp_duty",
  "Ushuru wa stempu kwenye hati ya ushirika wa biashara (partnership deed) "
  "Tanzania ni kiasi gani?",
  "Hati ya ushirika wa biashara (partnership deed) ina ushuru wa stempu Tanzania. "
  "Kiasi kinategemea masharti ya Sheria ya Ushuru wa Stempu — kawaida ni kiasi "
  "kidogo cha kawaida (fixed amount) au asilimia ya mtaji wa ushirika. Angalia "
  "TRA kwa kiwango cha hali ya sasa. Hati ya ushirika isiyopigwa stempu inaweza "
  "kuathiri uhalali wa ushirika.",
  "What is the stamp duty on a business partnership deed in Tanzania?",
  "A business partnership deed attracts stamp duty in Tanzania. The amount depends "
  "on the Stamp Duty Act provisions — typically a small fixed amount or a percentage "
  "of partnership capital. Check TRA for the current rate. An unstamped partnership "
  "deed can affect the legal validity of the partnership.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act amendment",
  "formal", "standard"),

p("tier1a_stamp_duty_118_20260609","stamp_duty",
  "Tofauti kati ya ushuru wa stempu na kodi ya ardhi (land rent) Tanzania ni nini?",
  "Ushuru wa stempu na kodi ya ardhi ni mambo mawili tofauti kabisa. Ushuru wa stempu "
  "ni kodi ya mara moja inayolipwa kwenye hati za kisheria kama uhamishaji wa ardhi "
  "— inalipwa na mnunuzi mara moja. Kodi ya ardhi (ground rent/land rent) ni malipo "
  "ya kila mwaka kwa Serikali kwa matumizi ya ardhi ya umma (hekta/ekari) — inalipwa "
  "mwaka hadi mwaka na mmiliki au mpangishaji.",
  "What is the difference between stamp duty and land rent in Tanzania?",
  "Stamp duty and land rent are two completely separate things. Stamp duty is a "
  "one-time tax paid on legal instruments like land transfer — paid once by the buyer. "
  "Land rent is an annual payment to the Government for use of public land — paid "
  "year after year by the owner or leaseholder.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act or land rent policy update",
  "business_market", "disambiguation"),

p("tier1a_stamp_duty_119_20260609","stamp_duty",
  "Ushuru wa stempu unalipwa kwenye bei ya mauzo au thamani ya soko — lipi ni kubwa?",
  "Ushuru wa stempu Tanzania unahesabiwa kwa kuzingatia KIASI KIKUBWA ZAIDI kati ya "
  "(a) bei ya mauzo iliyoandikwa kwenye mkataba, au (b) thamani ya soko ya mali. "
  "Hii inazuia uwezekano wa kupunguza thamani iliyoandikwa ili kulipa ushuru mdogo "
  "zaidi. TRA inaweza kutathmini thamani ya soko yenyewe ikiwa inaamini thamani "
  "iliyoandikwa ni ndogo kupita kiasi.",
  "Is stamp duty calculated on the sale price or market value — which is greater?",
  "Tanzania stamp duty is calculated on whichever is GREATER of: (a) the sale price "
  "written in the contract, or (b) the market value of the property. This prevents "
  "the possibility of understating the written value to pay less duty. TRA can "
  "assess market value itself if it believes the stated value is unreasonably low.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act amendment",
  "formal", "standard"),

p("tier1a_stamp_duty_120_20260609","stamp_duty",
  "Mnunuzi wa nyumba Tanzania anahitaji kulipa ushuru wa stempu na VAT kwenye "
  "ununuzi huo — je, ni kweli?",
  "VAT na ushuru wa stempu ni makodi tofauti na yanaweza yakatumika wakati mmoja "
  "kwenye ununuzi wa mali. VAT kwa kawaida inatumika ikiwa muuzaji ni msajiliwa wa "
  "VAT na mauzo yanastahili VAT (kwa mfano, mali mpya kutoka msanidi aliyesajiliwa). "
  "Ushuru wa stempu wa asilimia 1 unatumika kwenye uhamishaji wenyewe wa hati. "
  "Ni muhimu kuelewa kila moja kando na mwanasheria au mtaalamu wa mali.",
  "A Tanzania home buyer needs to pay both stamp duty and VAT on the purchase "
  "— is this true?",
  "VAT and stamp duty are separate taxes and both can apply simultaneously to a "
  "property purchase. VAT generally applies if the seller is VAT-registered and "
  "the sale is taxable (for example, new property from a registered developer). "
  "The 1% stamp duty applies to the transfer instrument itself. It is important "
  "to understand each separately with a lawyer or property specialist.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Finance Act or VAT/stamp duty update",
  "business_market", "disambiguation"),

p("tier1a_stamp_duty_121_20260609","stamp_duty",
  "Ushuru wa stempu kwenye hati za mkopo (mortgage) Tanzania ni asilimia ngapi?",
  "Hati za mkopo au rehani (mortgage) Tanzania zina ushuru wa stempu. Kiwango "
  "kinategemea Jedwali la Sheria ya Ushuru wa Stempu — kawaida ni kiasi kidogo cha "
  "kawaida au asilimia ya kiasi cha mkopo. Angalia TRA kwa jedwali la hali ya sasa "
  "kwani viwango vinaweza kutofautiana kulingana na aina ya mkopo (rehani ya ardhi, "
  "mkopo wa biashara, n.k.).",
  "What is the stamp duty rate on mortgage documents in Tanzania?",
  "Mortgage or loan security documents in Tanzania carry stamp duty. The rate depends "
  "on the Stamp Duty Act schedule — typically a small fixed amount or a percentage "
  "of the loan amount. Check TRA for the current schedule as rates can vary by type "
  "of mortgage (land mortgage, business loan, etc.).",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act amendment",
  "formal", "standard"),

p("tier1a_stamp_duty_122_20260609","stamp_duty",
  "Ushuru wa stempu wa asilimia 2 kwenye uhamishaji wa ardhi unaonekana "
  "katika baadhi ya vyanzo — je, ni kiwango sahihi cha Tanzania?",
  "Hapana. Kiwango cha ushuru wa stempu kwenye uhamishaji wa ardhi Tanzania ni "
  "asilimia 1 BAPA — si asilimia 2. Vyanzo vinavyosema asilimia 2 vinaweza "
  "kuwa na kosa au vinahusu nchi nyingine. Hakikisha mara zote kiwango cha hali "
  "ya sasa na TRA ya Tanzania kwenye tovuti yake au ofisi yake moja kwa moja.",
  "A 2% stamp duty on land transfer appears in some sources — is this the correct "
  "Tanzania rate?",
  "No. The stamp duty rate on land transfer in Tanzania is a FLAT 1% — not 2%. "
  "Sources quoting 2% may be in error or referring to another country. Always "
  "verify the current rate with Tanzania TRA on its website or directly at its offices.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Finance Act or Stamp Duty Act amendment",
  "business_market", "adversarial"),

p("tier1a_stamp_duty_123_20260609","stamp_duty",
  "Ardhi inayohamishiwa na serikali (compulsory acquisition) ina ushuru wa stempu?",
  "Kwa kawaida, uhamishaji wa ardhi kupitia unyakuzi wa lazima na serikali (compulsory "
  "acquisition) umeweza kusamehewa ushuru wa stempu Tanzania. Hata hivyo, masharti "
  "maalum ya kisheria yanatumika na inashauriwa kutafuta ushauri wa kisheria kwa hali "
  "yako. Fidia inayolipwa na serikali kwa ardhi iliyonyakuliwa inaweza pia kuwa na "
  "matokeo ya kodi mengine.",
  "Does land transferred through government compulsory acquisition attract stamp duty?",
  "Generally, land transfer through compulsory government acquisition may be exempt "
  "from stamp duty in Tanzania. However, specific legal conditions apply and it is "
  "advisable to seek legal advice for your situation. Compensation paid by the "
  "government for acquired land may also have other tax implications.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Land Acquisition Act or Stamp Duty Act amendment",
  "formal", "standard"),

p("tier1a_stamp_duty_124_20260609","stamp_duty",
  "Hati ya uhamishaji wa gari (motor vehicle transfer) ina ushuru wa stempu Tanzania?",
  "Uhamishaji wa gari Tanzania una ada za kusajilisha gari (registration transfer fee) "
  "zinazolipwa kwa Mamlaka ya Usimamizi wa Usafiri wa Nchi Kavu (SUMATRA) au TANROADS "
  "— hizi si ushuru wa stempu kwa njia ya kawaida. Ushuru wa stempu Tanzania unajumuisha "
  "zaidi hati za ardhi, mkopo, na mikataba maalum. Angalia SUMATRA/TRA kwa ada "
  "zinazohusika na magari.",
  "Does a motor vehicle transfer instrument attract stamp duty in Tanzania?",
  "Motor vehicle transfers in Tanzania involve registration transfer fees paid to "
  "SUMATRA or TANROADS — these are not stamp duty in the conventional sense. Tanzania "
  "stamp duty primarily covers land instruments, loans, and specified contracts. "
  "Check SUMATRA/TRA for fees applicable to vehicles.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act or vehicle registration fee update",
  "business_market", "disambiguation"),

p("tier1a_stamp_duty_125_20260609","stamp_duty",
  "Pande mbili zinaweza kukubaliana kwenye mkataba kwamba muuzaji atalipa ushuru "
  "wa stempu — je, hii inaweza kuepuka wajibu wa mnunuzi?",
  "Makubaliano ya kibinafsi kati ya muuzaji na mnunuzi kuhusu nani atalipa ushuru "
  "wa stempu yanafanya kazi kati yao. Lakini mbele ya TRA na mahakama, ushuru wa "
  "stempu bado unabaki wajibu wa kisheria wa pande ya kawaida (mnunuzi). Ikiwa "
  "muuzaji alipaswa kulipa lakini hakufanya, mnunuzi anaweza bado kulazimika "
  "kulipa ili hati isimame kisheria.",
  "Can both parties agree in the contract that the seller will pay stamp duty — "
  "does this avoid the buyer's obligation?",
  "A private agreement between seller and buyer about who pays stamp duty works "
  "between themselves. But before TRA and courts, stamp duty remains the statutory "
  "obligation of the usual party (buyer). If the seller was supposed to pay but "
  "didn't, the buyer may still be required to pay to make the instrument stand legally.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act amendment",
  "formal", "standard"),

p("tier1a_stamp_duty_126_20260609","stamp_duty",
  "Ushuru wa stempu wa hati ya uhamishaji wa hisa katika sekta ya madini Tanzania "
  "ni sawa na hati ya ardhi ya kawaida?",
  "Uhamishaji wa hisa katika sekta ya madini Tanzania unaweza kuwa na masharti "
  "maalum ya ushuru chini ya Sheria ya Madini na mfumo wake wa ushuru. Viwango "
  "au exemptions zinaweza kutofautiana na uhamishaji wa ardhi wa kawaida. Ni muhimu "
  "kupata ushauri maalum wa mwanasheria wa madini na kodi kwa aina hii ya muamala.",
  "Is stamp duty on a mining sector share transfer the same as a regular land "
  "transfer in Tanzania?",
  "Mining sector share transfers in Tanzania may have special tax provisions under "
  "the Mining Act and its fiscal regime. Rates or exemptions may differ from regular "
  "land transfers. It is important to obtain specialist advice from a mining and "
  "tax lawyer for this type of transaction.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Mining Act or Stamp Duty Act amendment",
  "formal", "standard"),

p("tier1a_stamp_duty_127_20260609","stamp_duty",
  "Ushuru wa stempu unaweza kusamehewa kwa hati za biashara za kikanda (EAC) — "
  "je, EAC inatoa msamaha?",
  "Kwa ujumla, hati zinazohusiana na biashara ya EAC au STR zinaweza kuwa na masharti "
  "maalum lakini msamaha wa ushuru wa stempu wa Tanzania kwa miamala ya EAC si "
  "moja kwa moja. Ushuru wa stempu Tanzania ni wa ndani — EAC inashughulikia zaidi "
  "ushuru wa forodha (customs duties). Angalia TRA kwa masharti mahususi ya hati "
  "za kibiashara za kikanda.",
  "Can stamp duty be exempted for EAC (East African Community) regional business "
  "instruments — does EAC provide an exemption?",
  "Generally, instruments relating to EAC trade or the STR may have special "
  "provisions but Tanzania stamp duty exemption for EAC transactions is not "
  "automatic. Tanzania stamp duty is a domestic tax — EAC primarily deals with "
  "customs duties. Check TRA for specific provisions on regional trade instruments.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "EAC treaty or Stamp Duty Act update",
  "formal", "standard"),

p("tier1a_stamp_duty_128_20260609","stamp_duty",
  "Hati ya usawa wa ardhi (land valuation certificate) inahitajika kabla ya kulipa "
  "ushuru wa stempu Tanzania?",
  "Ndiyo, thamani ya ardhi lazima ithibitishwe ili TRA iweze kukokotoa ushuru wa "
  "stempu sahihi. TRA inaweza kuhitaji tathmini (valuation) ya rasmi kutoka mtaalamu "
  "wa tathmini aliyeidhinishwa, hasa kwa miamala ya thamani kubwa au pale ambapo "
  "bei ya mauzo inaweza kutofautiana sana na thamani ya soko. Tathmini hii "
  "inasaidia kuhakikisha ushuru unahesabiwa kwa kiwango kikubwa zaidi.",
  "Is a land valuation certificate required before paying stamp duty in Tanzania?",
  "Yes, the land value must be verified so TRA can calculate the correct stamp duty. "
  "TRA may require a formal valuation from an authorised valuer, especially for "
  "high-value transactions or where the sale price may differ significantly from "
  "market value. The valuation helps ensure the duty is calculated on the higher amount.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "TRA process or Stamp Duty Act update",
  "formal", "standard"),

p("tier1a_stamp_duty_129_20260609","stamp_duty",
  "Kampuni inayopitia muundo mpya (restructuring) ambapo ardhi inahamishwa kwa "
  "kampuni mpya — ushuru wa stempu unaepukika?",
  "Uhamishaji wa ardhi ndani ya muundo wa kikundi (group restructuring) Tanzania "
  "kwa kawaida HAUKEPUKI ushuru wa stempu wa asilimia 1. Hata kama ni muundo wa "
  "ndani tu wa kikundi kimoja, uhamishaji wa hati za kisheria za ardhi bado una "
  "ushuru wa stempu Tanzania. Uchunguze kwa kina na mwanasheria wa kodi na "
  "mwanasheria wa mali kabla ya muundo wowote.",
  "A company undergoing restructuring where land is transferred to a new company "
  "— can stamp duty be avoided?",
  "Land transfer within a group restructuring in Tanzania generally does NOT avoid "
  "the 1% stamp duty. Even if it is purely an internal group restructuring, the "
  "transfer of legal land instruments still attracts Tanzania stamp duty. Investigate "
  "thoroughly with a tax lawyer and property lawyer before any restructuring.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act or company restructuring law update",
  "formal", "adversarial"),

p("tier1a_stamp_duty_130_20260609","stamp_duty",
  "Ushuru wa stempu unaweza kulipwa kwa Mpesa au Tigo Pesa Tanzania?",
  "Kwa sasa, malipo ya ushuru wa stempu Tanzania kwa kawaida yanafanywa kupitia "
  "mfumo wa TRA (PRN) kupitia benki zilizoidhinishwa au e-payment ya TRA. Malipo "
  "ya moja kwa moja kwa pesa ya simu (mobile money) kama M-Pesa kwa ushuru wa "
  "stempu yanaweza hayajakubaliwa rasmi kwenye mfumo wa TRA. Angalia TRA moja kwa "
  "moja au tovuti yake kwa njia za malipo zilizoidhinishwa za hali ya sasa.",
  "Can stamp duty be paid via M-Pesa or Tigo Pesa in Tanzania?",
  "Currently, stamp duty payments in Tanzania are generally made through the TRA "
  "system (PRN) via authorised banks or TRA e-payment. Direct payment via mobile "
  "money (M-Pesa) for stamp duty may not yet be formally accepted in the TRA system. "
  "Check TRA directly or on its website for currently authorised payment methods.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "TRA payment system update",
  "rural_conversational", "standard"),

p("tier1a_stamp_duty_131_20260609","stamp_duty",
  "Ushuru wa stempu Tanzania hulipwa kwenye thamani ya ardhi TU au pia kwenye "
  "majengo yaliyo juu ya ardhi hiyo?",
  "Ushuru wa stempu wa asilimia 1 unahesabiwa kwenye THAMANI YA JUMLA ya uhamishaji "
  "— yaani thamani ya ardhi NA majengo yote yaliyo juu yake pamoja. Haigawanywi "
  "ardhi na majengo kwa madhumuni ya ushuru wa stempu. Thamani ya mali yote "
  "inayohamishwa (ardhi + majengo) ndiyo msingi wa kuhesabu ushuru.",
  "Is Tanzania stamp duty paid on the land value ONLY or also on the buildings on it?",
  "The 1% stamp duty is calculated on the TOTAL transfer value — meaning the value "
  "of the land AND all buildings on it combined. There is no separation of land and "
  "buildings for stamp duty purposes. The value of the entire property being "
  "transferred (land + buildings) is the basis for the calculation.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act amendment",
  "business_market", "standard"),

p("tier1a_stamp_duty_132_20260609","stamp_duty",
  "Je, ushuru wa stempu unatumika kwenye mikataba ya ujenzi (construction contracts)?",
  "Mikataba ya ujenzi kwa kawaida haiko kwenye orodha kuu ya nyaraka zinazohitaji "
  "ushuru wa stempu Tanzania. Ushuru wa stempu unajumuisha zaidi hati za kisheria "
  "zinazohusiana na uhamishaji wa mali au dhamana za mkopo. Hata hivyo, ikiwa "
  "mkataba wa ujenzi una vipengele vya uhamishaji wa ardhi au dhamana, sehemu hizo "
  "zinaweza kuathiriwa. Angalia Sheria ya Ushuru wa Stempu na ushauri wa kisheria.",
  "Does stamp duty apply to construction contracts?",
  "Construction contracts are generally not in the main schedule of instruments "
  "requiring Tanzania stamp duty. Stamp duty primarily covers legal instruments "
  "relating to property transfer or loan security. However, if a construction "
  "contract includes property transfer or security elements, those parts may be "
  "affected. Check the Stamp Duty Act and seek legal advice.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act amendment",
  "formal", "standard"),

p("tier1a_stamp_duty_133_20260609","stamp_duty",
  "Hati ya mauzo ya ardhi iliyosainiwa kabla ya sheria mpya ya ushuru wa stempu "
  "inalipa kiwango cha zamani au kipya?",
  "Kwa kawaida, kiwango cha ushuru wa stempu kinachohusika ni kile kilichokuwepo "
  "wakati hati ilisainiwa au wakati malipo yanafanywa — kulingana na utaratibu "
  "wa Sheria ya Ushuru wa Stempu. Sheria mpya inaweza kuwa na masharti ya mpito "
  "yanayoathiri hati za zamani ambazo bado hazijapigwa stempu. Angalia TRA kwa "
  "mwongozo wa hali za mpito za kisheria.",
  "Does a land sale instrument signed before a new stamp duty law use the old or new rate?",
  "Generally, the applicable stamp duty rate is the one in force at the time the "
  "instrument was signed or when payment is made — depending on the Stamp Duty Act "
  "procedure. New legislation may have transitional provisions affecting old "
  "unstamped instruments. Check TRA for guidance on legal transitional situations.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act amendment",
  "formal", "standard"),

p("tier1a_stamp_duty_134_20260609","stamp_duty",
  "Hati ya ushirika wa VICOBA au SACCOS ina ushuru wa stempu Tanzania?",
  "Nyaraka za VICOBA (vikundi vya akiba) na SACCOS zinaweza kuwa na mfumo maalum "
  "wa ushuru au zisamehewa kwa sababu ya asili yao ya ushirika wa jamii. Hata "
  "hivyo, ikiwa SACCOS inaingia mikataba ya mkopo au mali ya ardhi, sehemu hizo "
  "za mikataba zina ushuru wa kawaida. Angalia TRA na Mamlaka ya SACCOS kwa "
  "mwongozo mahususi.",
  "Does a VICOBA or SACCOS formation instrument attract stamp duty in Tanzania?",
  "VICOBA (savings group) and SACCOS documents may have a special tax treatment "
  "or be exempt due to their community cooperative nature. However, if a SACCOS "
  "enters loan contracts or land-related instruments, those parts carry normal "
  "stamp duty. Check TRA and the SACCOS Authority for specific guidance.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act or cooperative law update",
  "rural_conversational", "standard"),

p("tier1a_stamp_duty_135_20260609","stamp_duty",
  "Kampuni ya NGO inayopokea ardhi kama mchango wa bure (donation) inalipa ushuru "
  "wa stempu Tanzania?",
  "NGO inayopokea ardhi kama mchango inaweza kuhitaji ushuru wa stempu kwenye hati "
  "ya uhamishaji, hata kama hakuna malipo ya pesa. Kwa hati za kawaida za uhamishaji, "
  "ushuru wa stempu unahesabiwa kwa kuzingatia thamani ya soko ya ardhi (si bei ya "
  "mauzo ya sifuri). Angalia TRA kwa masharti mahususi ya NGO zilizosajiliwa rasmi — "
  "inaweza kuwa na msamaha katika hali fulani.",
  "A registered NGO receiving land as a free donation — does it pay stamp duty in Tanzania?",
  "An NGO receiving land as a donation may still require stamp duty on the transfer "
  "instrument, even with no cash payment. For standard transfer instruments, stamp "
  "duty is calculated based on the market value of the land (not the zero sale price). "
  "Check TRA for specific provisions for formally registered NGOs — there may be "
  "an exemption in certain situations.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act or NGO fiscal framework update",
  "formal", "standard"),

p("tier1a_stamp_duty_136_20260609","stamp_duty",
  "Ushuru wa stempu Tanzania unalipwa kwa shilingi au unaweza kulipwa kwa dola "
  "za Marekani?",
  "Ushuru wa stempu Tanzania unalipwa kwa SHILINGI YA TANZANIA (TZS) — si dola. "
  "Hata kama muamala wenyewe ulifanywa kwa dola (kwa mfano, mauzo ya ardhi kwa "
  "USD), kiasi cha ushuru kinabadilishwa kulingana na kiwango cha ubadilishaji wa "
  "Benki Kuu ya Tanzania (BoT) siku ya malipo.",
  "Is Tanzania stamp duty paid in Tanzanian shillings or can it be paid in US dollars?",
  "Tanzania stamp duty is paid in TANZANIAN SHILLINGS (TZS) — not dollars. Even if "
  "the underlying transaction was in dollars (for example, a land sale in USD), the "
  "duty amount is converted at the Bank of Tanzania (BoT) exchange rate on the "
  "payment date.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "TRA payment policy update",
  "business_market", "standard"),

p("tier1a_stamp_duty_137_20260609","stamp_duty",
  "Ushuru wa stempu Tanzania unafunika mikataba ya usimamizi (management agreements) "
  "ya muda mrefu — je, ipo?",
  "Mikataba ya usimamizi ya muda mrefu Tanzania inaweza kuhitaji ushuru wa stempu "
  "ikiwa inafanana na muundo wa makubaliano ya kukodisha au ikiwa imeorodheshwa "
  "kwenye Jedwali la Sheria ya Ushuru wa Stempu. Mikataba ya kawaida ya huduma za "
  "usimamizi inaweza isihusike. Angalia mwanasheria wa kodi kwa aina yako mahususi "
  "ya mkataba wa usimamizi.",
  "Does Tanzania stamp duty cover long-term management agreements?",
  "Long-term management agreements in Tanzania may require stamp duty if they resemble "
  "lease structures or are listed in the Stamp Duty Act schedule. Ordinary management "
  "service contracts may not be covered. Check a tax lawyer for your specific type "
  "of management agreement.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act amendment",
  "formal", "standard"),

p("tier1a_stamp_duty_138_20260609","stamp_duty",
  "Mtu anayenunua ardhi Tanzania kwa mara ya kwanza ana msamaha wowote wa ushuru "
  "wa stempu — kama 'first home buyer' msamaha wa nchi nyingine?",
  "Tanzania haina mfumo maalum wa msamaha wa ushuru wa stempu kwa wanunuzi wa "
  "nyumba kwa mara ya kwanza (first-time buyer) kama nchi kama Uingereza au "
  "Australia. Ushuru wa stempu wa asilimia 1 unatumika kwa wanunuzi wote bila "
  "kujali iwapo ni ununuzi wao wa kwanza au la.",
  "Does a first-time land buyer in Tanzania get any stamp duty exemption — like a "
  "'first home buyer' relief in other countries?",
  "Tanzania does not have a dedicated first-time buyer stamp duty exemption like "
  "countries such as the UK or Australia. The flat 1% stamp duty applies to all "
  "buyers regardless of whether it is their first purchase.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act amendment",
  "rural_conversational", "standard"),

p("tier1a_stamp_duty_139_20260609","stamp_duty",
  "Hati ya mauzo iliyoandikwa vizuri bila kulipwa ushuru wa stempu bado ni hati "
  "halali ya kisheria Tanzania?",
  "Hapana kwa ujumla. Hati inayohitaji ushuru wa stempu lakini haijalipwa inaweza "
  "kukosa nguvu ya kisheria au kukataliwi na mahakama. Hata kama hati imeandikwa "
  "vizuri — ina pande zote mbili, masharti wazi, na sahihi za kisheria — kukosa "
  "ushuru wa stempu kunaweza kuifanya hati hiyo isitekelezwe kisheria. Lipa ushuru "
  "wa stempu mara baada ya kusaini.",
  "A well-written sale instrument without stamp duty paid is still a legally valid "
  "document in Tanzania?",
  "Generally no. An instrument requiring stamp duty but unpaid may lack legal force "
  "or be rejected by courts. Even if the instrument is well-written — has both "
  "parties, clear terms, and legal signatures — missing stamp duty can make the "
  "instrument unenforceable in law. Pay stamp duty promptly after signing.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act amendment",
  "business_market", "adversarial"),

p("tier1a_stamp_duty_140_20260609","stamp_duty",
  "Ushuru wa stempu Tanzania unaweza kurejeshwa (refund) ikiwa muamala haukufanikia?",
  "Ikiwa muamala wa ardhi haukukamilika (kwa mfano, mkataba ulifutwa rasmi kabla ya "
  "kutekelezwa), inaweza kuwa na utaratibu wa kuomba kurejesha ushuru wa stempu "
  "uliolipwa Tanzania. Utaratibu huu kwa kawaida unahitaji ushahidi wa kufutwa kwa "
  "muamala na maombi rasmi kwa TRA ndani ya muda fulani. Angalia TRA kwa masharti "
  "na tarehe za mwisho za maombi ya kurejesha.",
  "Can Tanzania stamp duty be refunded if a transaction does not go through?",
  "If a property transaction is not completed (for example, the contract was formally "
  "cancelled before execution), there may be a procedure to apply for a refund of "
  "paid stamp duty in Tanzania. This process usually requires evidence of transaction "
  "cancellation and a formal application to TRA within a certain period. Check TRA "
  "for conditions and deadlines for refund applications.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act or Tax Administration Act update",
  "formal", "standard"),

p("tier1a_stamp_duty_141_20260609","stamp_duty",
  "Kampuni inayonunua ardhi kwa makusudi ya kujenga viwanda (industrial development) "
  "Tanzania ina msamaha wa ushuru wa stempu?",
  "Tanzania Investment Centre (TIC) inaweza kutoa vivutio maalum vya uwekezaji kwa "
  "miradi ya viwanda — hivi vinaweza kujumuisha msamaha wa ushuru wa stempu au "
  "kupunguzwa kwa ushuru mwingine. Msamaha huu si wa kawaida — unategemea aina ya "
  "uwekezaji, eneo, na kukubaliana na TIC. Uwekezaji wa viwanda unapaswa kupata "
  "idhini ya TIC kabla ya kudai msamaha wowote.",
  "A company buying land for industrial development in Tanzania — is there a stamp "
  "duty exemption?",
  "The Tanzania Investment Centre (TIC) can offer special investment incentives for "
  "industrial projects — these may include stamp duty exemption or reduction of other "
  "taxes. This exemption is not standard — it depends on the type of investment, "
  "location, and agreement with TIC. Industrial investments should get TIC approval "
  "before claiming any exemptions.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "TIC incentive or Stamp Duty Act update",
  "formal", "standard"),

p("tier1a_stamp_duty_142_20260609","stamp_duty",
  "Tofauti kati ya ushuru wa stempu na ushuru wa usajili wa ardhi (land registration "
  "fee) Tanzania ni nini?",
  "Hizi ni ada mbili tofauti zinazolipwa wakati wa kununua ardhi Tanzania. Ushuru "
  "wa stempu (1% ya thamani) unalipwa kwa TRA na unahusiana na hati ya kisheria. "
  "Ada ya usajili wa ardhi ni ada tofauti inayolipwa kwa Msajili wa Ardhi (Registrar "
  "of Titles / MLHHSD) kwa kusajili hati hiyo kwenye rejista ya ardhi. Zote mbili "
  "zinahitajika kwa uhamishaji kamili wa kisheria wa ardhi.",
  "What is the difference between stamp duty and land registration fee in Tanzania?",
  "These are two separate charges paid when buying land in Tanzania. Stamp duty "
  "(1% of value) is paid to TRA and relates to the legal instrument. The land "
  "registration fee is a separate fee paid to the Registrar of Titles (MLHHSD) to "
  "register that instrument in the land register. Both are required for full legal "
  "transfer of land.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act or land registration fee update",
  "business_market", "disambiguation"),

p("tier1a_stamp_duty_143_20260609","stamp_duty",
  "Ardhi inayohamishwa kwa sababu ya talaka (divorce) Tanzania — ina ushuru wa stempu?",
  "Uhamishaji wa ardhi kati ya wanandoa kama sehemu ya mgawanyo wa mali wa talaka "
  "unaweza kuwa na masharti maalum ya ushuru chini ya Sheria ya Ndoa Tanzania "
  "na Sheria ya Ushuru wa Stempu. Inaweza kuwa na msamaha au kupunguzwa kwa "
  "ushuru katika hali za talaka. Angalia mwanasheria wa familia na kodi kwa "
  "hali yako mahususi.",
  "Land transferred as part of a divorce settlement in Tanzania — does it attract "
  "stamp duty?",
  "Transfer of land between spouses as part of a divorce asset division may have "
  "special tax treatment under the Tanzania Law of Marriage Act and the Stamp Duty "
  "Act. There may be an exemption or reduction in divorce situations. Consult a "
  "family and tax lawyer for your specific situation.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act or family law update",
  "rural_conversational", "standard"),

p("tier1a_stamp_duty_144_20260609","stamp_duty",
  "Kampuni inayotoa hisa mpya (new share issue) inalipa ushuru wa stempu Tanzania?",
  "Utoaji wa hisa mpya na kampuni (new share issue) unaweza kuwa na ushuru wa stempu "
  "Tanzania unaohesabiwa kwa kuzingatia thamani ya hisa mpya zinazotolewa. Hii "
  "ni tofauti na uhamishaji wa hisa zilizopo kati ya wanaohisa (share transfer). "
  "Angalia Sheria ya Ushuru wa Stempu na TRA kwa kiwango kinachohusika na utoaji "
  "mpya wa hisa.",
  "Does a company issuing new shares attract stamp duty in Tanzania?",
  "A company issuing new shares may attract stamp duty in Tanzania calculated on the "
  "value of the new shares being issued. This is different from a transfer of "
  "existing shares between shareholders. Check the Stamp Duty Act and TRA for the "
  "rate applicable to new share issuances.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act or Companies Act amendment",
  "formal", "standard"),

p("tier1a_stamp_duty_145_20260609","stamp_duty",
  "Hati ya dhamana ya mkopo wa benki (bank loan security) Tanzania ina ushuru wa "
  "stempu — mnunuzi analipa wakati wa kusaini au baadaye?",
  "Dhamana ya mkopo wa benki Tanzania (kama rehani ya ardhi, charge) ina ushuru wa "
  "stempu ambao unapaswa kulipwa KABLA ya kusajili dhamana hiyo au kabla ya "
  "kutumika kisheria. Kawaida, ushuru unalipwa WAKATI AU KABLA ya kusaini au "
  "kusajili. Benki nyingi zinasimamia mchakato huu na mteja (mkopaji) mara nyingi "
  "anabeba gharama hii.",
  "Does a bank loan security instrument in Tanzania carry stamp duty — does the buyer "
  "pay at signing or later?",
  "A bank loan security in Tanzania (such as a land mortgage or charge) carries stamp "
  "duty that must be paid BEFORE registering the security or before it can be used "
  "legally. Generally, duty is paid AT OR BEFORE signing or registration. Banks "
  "usually manage this process and the client (borrower) typically bears the cost.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act or banking regulation update",
  "business_market", "standard"),

p("tier1a_stamp_duty_146_20260609","stamp_duty",
  "Ushuru wa stempu Tanzania ni mkubwa kiasi gani kwa uhamishaji wa ardhi wa TZS 500M?",
  "Kwa uhamishaji wa ardhi wenye thamani ya TZS 500,000,000, ushuru wa stempu wa "
  "asilimia 1 ni TZS 5,000,000. Hii ni hesabu rahisi: thamani × asilimia 1 = "
  "TZS 500,000,000 × 0.01 = TZS 5,000,000. Ikiwa thamani ya soko ni zaidi ya bei "
  "ya mauzo iliyoandikwa, ushuru unahesabiwa kwa thamani ya soko.",
  "How large is Tanzania stamp duty for a land transfer worth TZS 500M?",
  "For a land transfer worth TZS 500,000,000, the 1% stamp duty is TZS 5,000,000. "
  "This is a simple calculation: value × 1% = TZS 500,000,000 × 0.01 = TZS 5,000,000. "
  "If the market value exceeds the stated sale price, the duty is calculated on the "
  "market value.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Finance Act or Stamp Duty Act amendment",
  "business_market", "standard"),

p("tier1a_stamp_duty_147_20260609","stamp_duty",
  "Ardhi ya kilimo (agricultural land) ina kiwango tofauti cha ushuru wa stempu "
  "kuliko ardhi ya makazi Tanzania?",
  "Sheria ya Ushuru wa Stempu Tanzania inaweza kuwa na tofauti za ushuru kulingana "
  "na aina ya ardhi au matumizi yake. Kwa ujumla, kiwango cha kawaida cha asilimia 1 "
  "kinatumika kwa aina nyingi za ardhi. Msamaha au kupunguzwa kwa ushuru kwa ardhi "
  "ya kilimo unaweza kutegemea masharti mahususi ya kisheria. Angalia TRA moja kwa "
  "moja kwa aina yako ya ardhi.",
  "Does agricultural land have a different stamp duty rate than residential land "
  "in Tanzania?",
  "The Tanzania Stamp Duty Act may have variations based on type of land or its use. "
  "Generally, the standard 1% rate applies to most land types. An exemption or "
  "reduction for agricultural land may depend on specific legal conditions. Check "
  "TRA directly for your type of land.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act or land use policy update",
  "rural_conversational", "standard"),

p("tier1a_stamp_duty_148_20260609","stamp_duty",
  "Mwanasheria anayeandaa hati ya mauzo ya ardhi ana wajibu wowote wa ushuru wa "
  "stempu — au ni wajibu wa mnunuzi tu?",
  "Mwanasheria anayeandaa hati ya mauzo ana jukumu la kisheria la kumwarifu mteja "
  "kuhusu wajibu wa ushuru wa stempu na kuhakikisha hati inasimama kisheria. Hata "
  "hivyo, WAJIBU WA MWISHO wa kulipa ushuru wa stempu unabaki kwa mnunuzi (au "
  "pande zote mbili kama zilikubaliana). Mwanasheria asiye mzuri anayekosa kueleza "
  "ushuru wa stempu anaweza kuadhibiwa kitaalamu.",
  "Does a lawyer preparing a land sale instrument have any stamp duty obligation — "
  "or is it only the buyer's responsibility?",
  "A lawyer preparing a sale instrument has a professional duty to advise their client "
  "about stamp duty obligations and ensure the document stands legally. However, the "
  "FINAL OBLIGATION to pay stamp duty remains with the buyer (or both parties as "
  "agreed). A negligent lawyer who fails to explain stamp duty may face professional "
  "sanctions.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Stamp Duty Act or professional code update",
  "formal", "standard"),

p("tier1a_stamp_duty_149_20260609","stamp_duty",
  "Ushuru wa stempu Tanzania unahusiana na 'Capital Gains Tax' (kodi ya faida ya "
  "mtaji) — ni mambo sawa?",
  "Hapana, ni mambo tofauti kabisa. Ushuru wa stempu ni kodi kwenye HATI YA KISHERIA "
  "ya uhamishaji — inayolipwa mara moja kwenye thamani ya uhamishaji. Kodi ya faida "
  "ya mtaji (capital gain) ni kodi kwenye FAIDA inayopatikana na muuzaji — tofauti "
  "kati ya bei ya mauzo na gharama ya ununuzi wa awali. Mnunuzi analipa ushuru wa "
  "stempu; muuzaji anaweza kulipa kodi ya faida ya mtaji.",
  "Are Tanzania stamp duty and Capital Gains Tax the same thing?",
  "No, these are completely different things. Stamp duty is a tax on the LEGAL "
  "INSTRUMENT of transfer — paid once on the transfer value. Capital gains tax is "
  "a tax on the PROFIT earned by the seller — the difference between the sale price "
  "and original purchase cost. The buyer pays stamp duty; the seller may pay capital "
  "gains tax.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "business_market", "disambiguation"),

p("tier1a_stamp_duty_150_20260609","stamp_duty",
  "Je, ushuru wa stempu Tanzania unatumika kwa hati za kidijitali "
  "(e-contracts/digital agreements) zilizosainiwa mtandaoni?",
  "Sheria ya Ushuru wa Stempu Tanzania (Stamp Duty Act) iliandikwa kabla ya enzi ya "
  "mikataba ya kidijitali. Hati za kidijitali au mikataba iliyosainiwa mtandaoni "
  "kwenye mazingira ya Tanzania yanaweza bado kuhitaji ushuru wa stempu ikiwa "
  "yanashughulikia aina za miamala zilizoorodheshwa kwenye sheria. Mfumo wa kisheria "
  "wa Tanzania wa e-transactions (e-Transactions Act) unasimamia hati za kidijitali. "
  "Angalia TRA au mwanasheria kwa hali yako.",
  "Does Tanzania stamp duty apply to digital instruments (e-contracts/digital "
  "agreements) signed online?",
  "The Tanzania Stamp Duty Act was written before the era of digital contracts. "
  "Digital instruments or contracts signed online in Tanzania may still require "
  "stamp duty if they deal with listed transaction types. Tanzania's electronic "
  "transactions legal framework (e-Transactions Act) governs digital instruments. "
  "Check TRA or a lawyer for your specific situation.",
  TRA_SD, TRA_SD_N, GP, "2025-07-01", ANN, "e-Transactions Act or Stamp Duty Act update",
  "formal", "standard"),

]

written = 0
with open(OUT, "a", encoding="utf-8") as f:
    for pr in pairs:
        f.write(json.dumps(pr, ensure_ascii=False) + "\n")
        written += 1

total = sum(1 for _ in open(OUT, encoding="utf-8") if _.strip())
print(f"Part 3: wrote {written} pairs to {OUT}")
print(f"Total in file: {total}")
