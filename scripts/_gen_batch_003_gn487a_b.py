#!/usr/bin/env python3
"""Append remaining 30 gn487a adversarial pairs (051-080) to raw_pairs_batch_003.jsonl."""
import json, os

OUT = "datasets/tier1a/raw_sources/raw_pairs_batch_003.jsonl"
SOURCE_URL = "https://tanzlii.org/akn/tz/act/gn/2025/487a/eng@2025-07-28"
SOURCE_NAME = "GN 487A — Business Licensing (Prohibition of Business Activities for Non-Citizens) Order 2025"

PAIRS = [
{
"id": "tier1a_gn487a_051_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Mgeni wetu wa duka anasema ana haki ya kufanya biashara kwa sababu amesimama Tanzania miaka mingi — hii ni kweli?",
"answer_sw": "Hapana. Muda wa kukaa Tanzania hauzidishi haki ya kufanya biashara iliyozuiliwa. GN 487A inazuia watu WASIO RAIA wa Tanzania — bila kujali wamekuwa Tanzania kwa miaka mingapi. Hata mgeni aliyekuwa Tanzania miaka 20 na ana vibali vyote vya makazi bado hawezi kumiliki duka la rejareja, saluni, au biashara nyingine ya makundi 15 yaliyozuiliwa. Njia pekee ya kupata haki hiyo ni kupata uraia wa Tanzania.",
"question_en": "Our foreign shop owner says he has the right to do business because he has been in Tanzania for many years — is this true?",
"answer_en": "No. Length of stay in Tanzania does not increase the right to operate a prohibited business. GN 487A restricts those who are NOT Tanzanian citizens — regardless of how many years they have been in Tanzania. Even a non-citizen who has been in Tanzania for 20 years with all valid residence permits still cannot own a retail shop, salon, or any of the other 15 prohibited business categories. The only way to gain that right is to obtain Tanzanian citizenship.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "rural_conversational", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_052_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Mfanyabiashara mgeni alikwambia hahitaji kujali GN 487A kwa sababu analipa kodi Tanzania — ana haki?",
"answer_sw": "Hapana. Kulipa kodi Tanzania (VAT, PAYE, corporate tax, au kodi nyingine) hakumpa mgeni haki ya kufanya biashara katika makundi 15 yaliyozuiliwa chini ya GN 487A. Ulipaji wa kodi ni wajibu wa kisheria kwa kila biashara inayofanya kazi Tanzania — si kibali cha kufanya biashara yoyote. GN 487A inahusiana na UMILIKI wa biashara, si ulipaji wa kodi. Mgeni anayefanya biashara iliyozuiliwa na kulipa kodi bado anakiuka GN 487A na anaweza kushtakiwa.",
"question_en": "A foreign trader told me he does not need to worry about GN 487A because he pays taxes in Tanzania — is he right?",
"answer_en": "No. Paying taxes in Tanzania (VAT, PAYE, corporate tax, or other taxes) does not give a non-citizen the right to operate in the 15 prohibited business categories under GN 487A. Tax payment is a legal obligation for every business operating in Tanzania — it is not a permit to operate any business. GN 487A concerns OWNERSHIP of a business, not tax payment. A non-citizen operating a prohibited business and paying taxes still violates GN 487A and can be prosecuted.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "business_market", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_053_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Mgeni mwenye TIC certificate (cheti cha uwekezaji kutoka TIC) ana ulinzi dhidi ya GN 487A?",
"answer_sw": "Si kwa ujumla. TIC (Tanzania Investment Centre) certificate inaruhusu uwekezaji wa kigeni katika sekta maalum za uwekezaji mkubwa — kama uzalishaji wa viwanda, madini, kilimo cha biashara kubwa. Hata hivyo, TIC certificate haizuii matumizi ya GN 487A kwa sekta zilizozuiliwa kama biashara ya rejareja, saluni, au ukarabati wa simu. Mwekezaji wa kigeni mwenye TIC certificate bado hawezi kufanya biashara katika makundi 15 yaliyozuiliwa. TIC na GN 487A ni mifumo tofauti — mshauri wa kisheria anaweza kusaidia kuelewa jinsi inavyoathiri uwekezaji wako mahususi.",
"question_en": "A non-citizen with a TIC certificate (investment certificate from Tanzania Investment Centre) — are they protected from GN 487A?",
"answer_en": "Not generally. A TIC (Tanzania Investment Centre) certificate permits foreign investment in specific large-scale investment sectors — such as industrial manufacturing, mining, large-scale commercial agriculture. However, a TIC certificate does not override GN 487A for the prohibited sectors such as retail trade, salons, or phone repair. A foreign investor with a TIC certificate still cannot operate businesses in the 15 prohibited categories. TIC and GN 487A are separate frameworks — a legal adviser can help understand how it affects your specific investment.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_054_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Mtu wa nje anafanya biashara ya kutengeneza nguo na kuziuza — je, ni tatizo?",
"answer_sw": "Inategemea. Uzalishaji wa viwanda (manufacturing) — kama kushona na kutengeneza nguo — si moja ya sekta 15 zilizozuiliwa wazi na GN 487A. Hata hivyo, KUUZA nguo moja kwa moja kwa wateja (retail) au kwa wachuuzi (wholesale) ni tatizo kwa sababu biashara ya jumla na rejareja imezuiliwa. Mgeni anayeshona nguo na kuziuza moja kwa moja katika duka lake anaweza kukiuka GN 487A upande wa uuzaji. Anashauriwa kupata ushauri wa kisheria ili kuelewa vizuri muundo sahihi wa biashara yake.",
"question_en": "A non-citizen runs a clothes manufacturing and selling business — is this a problem?",
"answer_en": "It depends. Industrial manufacturing — such as sewing and making clothes — is not one of the 15 explicitly prohibited sectors under GN 487A. However, SELLING clothes directly to customers (retail) or to traders (wholesale) is a problem because wholesale and retail trade is prohibited. A non-citizen who makes clothes and sells them directly from their own shop may violate GN 487A on the selling side. They are advised to get legal advice to understand the correct business structure.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "business_market", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_055_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Biashara ya mgeni ilianza kabla ya GN 487A — je, ina muda wa kukaa hadi itakapokamilika?",
"answer_sw": "Hapana. GN 487A haikutoa muda wowote wa kustaafu (grace period) kwa biashara zilizokuwepo kabla ya amri kuanza mwaka 2025. Amri ilianza kutumika mara moja tarehe 28 Julai 2025 bila kipindi cha mpito. Biashara yoyote ya mgeni katika makundi 15 yaliyozuiliwa ilipaswa kusimama au kuhamishiwa umiliki kwa Mtanzania mara amri iliposajiliwa. Kuendelea kufanya biashara hiyo baada ya tarehe hiyo ni kuvunja sheria moja kwa moja. Mgeni aliyekuwa na biashara kama hiyo anapaswa kuona wakili haraka.",
"question_en": "A non-citizen's business started before GN 487A — does it have a grace period to wind down?",
"answer_en": "No. GN 487A did not provide any grace period (wind-down period) for businesses that existed before the Order came into force in 2025. The Order took effect immediately on 28 July 2025 without any transition period. Any non-citizen business in the 15 prohibited categories was required to stop or transfer ownership to a Tanzanian immediately when the Order was gazetted. Continuing such a business after that date is a direct violation. A non-citizen who had such a business should see a lawyer urgently.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_056_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Mgeni ana mkoba wa pesa anayoikopesha watu kijijini kama mfumo wa SACCOS — GN 487A inamhusu?",
"answer_sw": "Inaweza kuumhusu. Kama mgeni anafanya shughuli za ukopeshaji (micro-lending) kwa ujumla — hasa kama inafanana na huduma za kifedha rasmi — inaweza kuchukuliwa kama sehemu ya makundi yaliyozuiliwa au kuanguka chini ya sheria nyingine za fedha. Huduma za uhamisho wa pesa kwa simu zimezuiliwa wazi, lakini ukopeshaji wa pesa unaweza kuhitaji leseni ya BoT. Kama mkoba huo unafanya kazi kama SACCOS rasmi, mgeni anahitaji kushauriana na Wakala wa Usimamizi wa Vyama vya Ushirika (COASCO) na wakili wa kisheria ili kuelewa kikamilifu.",
"question_en": "A non-citizen has a money lending system in the village similar to a SACCOS — does GN 487A affect them?",
"answer_en": "It may affect them. If a non-citizen is conducting general money lending activities — especially if it resembles formal financial services — it may fall under the prohibited categories or other financial laws. Mobile money transfer services are explicitly prohibited, and money lending may require a BoT licence. If the lending operates as a formal SACCOS, the non-citizen needs to consult COASCO (Cooperative Societies) and a legal adviser to fully understand their obligations.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "rural_conversational", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_057_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Biashara yangu iko mpakani mwa Tanzania na Kenya — GN 487A inatumika pia maeneo ya mpakani?",
"answer_sw": "Ndiyo. GN 487A inatumika Tanzania Bara yote, ikiwa ni pamoja na maeneo ya mpakani kama Namanga, Holili, Tunduma, na Kabanga. Wafanyabiashara wa msalaba wa mpaka (cross-border traders) ambao si raia wa Tanzania bado wanazuiwa kufanya biashara katika makundi 15 yaliyozuiliwa nchini Tanzania. Soko la STR (Simplified Trade Regime) la EAC halitoi ulinzi dhidi ya GN 487A. Mfanyabiashara mgeni anayeuza moja kwa moja katika soko la Tanzania (rejareja au jumla) anakiuka GN 487A hata kama anapita mpakani kila siku.",
"question_en": "My business is at the Tanzania-Kenya border — does GN 487A also apply in border areas?",
"answer_en": "Yes. GN 487A applies throughout Tanzania Mainland, including border areas such as Namanga, Holili, Tunduma, and Kabanga. Cross-border traders who are not Tanzanian citizens are still prohibited from operating businesses in the 15 restricted categories within Tanzania. The EAC Simplified Trade Regime (STR) does not provide protection against GN 487A. A non-citizen trader who sells directly in Tanzanian markets (retail or wholesale) violates GN 487A even if they cross the border daily.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "business_market", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_058_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Asha ni mfanyabiashara wa mpaka huko Tunduma — ana duka la vipande vya magari, si raia. Nini hatari yake?",
"answer_sw": "Asha yuko katika hatari kubwa ya kisheria. Biashara ya vipande vya magari ni moja ya makundi 15 yaliyozuiliwa kwa watu wasio raia wa Tanzania chini ya GN 487A. Kama Asha si raia wa Tanzania na anaendesha duka hilo kama biashara yake, anakiuka amri hii. Adhabu ni: faini ya angalau TZS milioni 10, kifungo cha hadi miezi 6 jela, na kufutwa kwa viza na kurushwa nchini kwake. Asha anahitaji ushauri wa wakili wa haraka na kufikiria kuhamisha biashara kwa raia wa Tanzania, au kuacha kabisa.",
"question_en": "Asha is a cross-border trader at Tunduma — she has a spare parts shop and is not a citizen. What is her risk?",
"answer_en": "Asha is at serious legal risk. Spare parts trade is one of the 15 categories prohibited for non-Tanzanian citizens under GN 487A. If Asha is not a Tanzanian citizen and operates that shop as her own business, she is violating this Order. Penalties are: a minimum TZS 10 million fine, up to 6 months imprisonment, and visa revocation with deportation. Asha urgently needs legal advice and should consider transferring the business to a Tanzanian citizen, or closing it entirely.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "rural_conversational", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_059_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Mgeni anaweza kufanya biashara ya ushauri (consultancy) Tanzania?",
"answer_sw": "Ushauri wa kitaalamu (professional consultancy) haujatajwa wazi kati ya makundi 15 yaliyozuiliwa na GN 487A. Kwa hiyo, mgeni anaweza kufanya kazi ya ushauri — kama mshauri wa IT, wa fedha, wa usimamizi — bila ya kukiuka GN 487A moja kwa moja, lakini anahitaji kibali sahihi cha kufanya kazi kutoka Wizara ya Kazi. Hata hivyo, kama biashara ya ushauri inajumuisha pia mauzo ya rejareja ya bidhaa au huduma za fedha za moja kwa moja, sehemu hiyo inaweza kuathiriwa. Mshauri wa kisheria anaweza kusaidia kuelewa mipaka sahihi.",
"question_en": "Can a non-citizen operate a consultancy business in Tanzania?",
"answer_en": "Professional consultancy is not explicitly listed among the 15 prohibited categories under GN 487A. Therefore, a non-citizen may conduct consultancy work — such as IT, financial, or management consulting — without directly violating GN 487A, but they still need a valid work permit from the Ministry of Labour. However, if the consultancy also includes retail sales of goods or direct financial services, that aspect may be affected. A legal adviser can help clarify the exact boundaries.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_060_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Mwanafunzi mgeni anayesomea Tanzania anaweza kufanya kazi ndogo ya biashara?",
"answer_sw": "Hali ya kisheria ya mwanafunzi wa kigeni ni ngumu. Visa ya masomo (student visa) kwa ujumla hairuhusu kufanya kazi au biashara Tanzania. Zaidi ya hayo, GN 487A inazuia watu wasio raia wa Tanzania kufanya biashara katika makundi 15 bila kujali aina ya visa waliyo nayo. Mwanafunzi anayefanya kazi ndogo za rejareja (kuuza chips, vitu vya sokoni) kwa ujumla anakiuka sheria mbili: sheria ya masomo (kwa kufanya kazi bila ruhusa) na GN 487A (kwa kufanya biashara ya rejareja). Anapaswa kushauriana na ofisi ya uhamiaji au chuo chake.",
"question_en": "Can a foreign student studying in Tanzania do a small side business?",
"answer_en": "A foreign student's legal situation is complex. A student visa generally does not permit employment or business activities in Tanzania. Furthermore, GN 487A prohibits non-Tanzanian citizens from operating businesses in the 15 categories regardless of what visa they hold. A student doing small retail activities (selling chips, market goods) generally violates two laws: immigration law (working without permission) and GN 487A (conducting retail trade). They should consult the immigration office or their institution.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "business_market", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_061_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Jirani yangu mgeni anauza samaki karibu na ziwa — je, anakiuka GN 487A?",
"answer_sw": "Inawezekana. Kuuza samaki moja kwa moja kwa wateja kunaweza kuchukuliwa kama biashara ya rejareja ya chakula, ambayo ni moja ya makundi yaliyozuiliwa. Kama jirani yako mgeni anauza samaki kama biashara yake binafsi — hata kwa kiwango kidogo — anaweza kukiuka GN 487A. Hata hivyo, kama anauza kwa kampuni ya usindikaji au kwa mkulima mkubwa wa samaki ambaye ni raia, hali inaweza kuwa tofauti. Ni bora apate ushauri wa kisheria ili kujua ni jinsi gani sheria inavyomhusu.",
"question_en": "My foreign neighbour sells fish near the lake — are they violating GN 487A?",
"answer_en": "Possibly. Selling fish directly to customers may be classified as retail food trade, which is one of the prohibited categories. If your foreign neighbour sells fish as their own business — even at a small scale — they may be violating GN 487A. However, if they are selling to a processing company or a large Tanzanian fish farmer, the situation may differ. It is best for them to get legal advice to understand exactly how the law applies to them.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "rural_conversational", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_062_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Kampuni ya kimataifa ya IT (teknolojia ya habari) inaweza kumilikiwa na mgeni Tanzania?",
"answer_sw": "Ndiyo, kwa ujumla inaweza. Huduma za teknolojia ya habari (IT), ubunifu wa programu (software development), na huduma za kielektroniki haziko kati ya makundi 15 yaliyozuiliwa wazi na GN 487A. Kampuni ya IT inayomilikiwa na mgeni inaweza kufanya kazi Tanzania mradi inazingatia sheria nyingine za biashara, kama usajili wa BRELA, ulipaji wa kodi, na vibali sahihi vya kazi kwa wafanyakazi. Hata hivyo, kama kampuni hiyo pia inaendesha duka la rejareja la bidhaa za IT (kuuza vifaa moja kwa moja kwa wateja), sehemu hiyo ya biashara inaweza kuathiriwa na GN 487A.",
"question_en": "Can an international IT (information technology) company be owned by a non-citizen in Tanzania?",
"answer_en": "Yes, generally it can. Information technology services, software development, and electronic services are not among the 15 explicitly prohibited categories under GN 487A. A non-citizen-owned IT company can operate in Tanzania provided it complies with other business laws, such as BRELA registration, tax payment, and valid work permits for employees. However, if that company also operates a retail shop selling IT goods (selling hardware directly to customers), that aspect of the business may be affected by GN 487A.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_063_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Mgeni ana mkahawa wa chakula cha jioni mjini — je, hii ni sawa chini ya GN 487A?",
"answer_sw": "Mkahawa unaomilikiwa na mgeni unaweza kukiuka GN 487A kama unachukuliwa kama biashara ya rejareja ya chakula. Mauzo ya chakula moja kwa moja kwa wateja (hata katika mkahawa wa kisasa) yanaweza kuainishwa kama rejareja (retail) ambayo ni moja ya makundi 15 yaliyozuiliwa. Mgeni mwenye mkahawa anapaswa kupata ushauri wa kisheria haraka ili kujua hali yake. Sawa na maduka ya mama lishe au nyama choma, muundo wa umiliki wa mkahawa unahitaji uchunguzi wa kisheria makini.",
"question_en": "A non-citizen owns an evening restaurant in the city — is this acceptable under GN 487A?",
"answer_en": "A non-citizen-owned restaurant may violate GN 487A if it is classified as retail food business. Selling food directly to customers (even in a formal restaurant) may be classified as retail, which is one of the 15 prohibited categories. A non-citizen with a restaurant should get legal advice quickly to understand their situation. Similar to mama lishe stalls or nyama choma restaurants, the ownership structure of a restaurant requires careful legal review.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "business_market", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_064_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Duka la dawa linaweza kumilikiwa na daktari mgeni Tanzania?",
"answer_sw": "Duka la dawa (pharmacy) linasimamiwa na sheria za afya za Tanzania — haswa Mamlaka ya Chakula na Dawa (TFDA/TMDA). GN 487A inazuia biashara ya rejareja kwa ujumla, lakini dawa ni sekta maalum inayohitaji leseni za TMDA. Kama mgeni ana leseni ya TMDA na biashara yake inafanya kazi kama duka la dawa rasmi (pharmacy), hali yake inategemea jinsi GN 487A inavyotafsiriwa kwa sekta ya afya. Mshauri wa kisheria anayeelewa sheria za afya na GN 487A anahitajika kusaidia kuelewa kikamilifu. Ushauri wa kisheria ni muhimu kabla ya kufanya maamuzi.",
"question_en": "Can a foreign doctor own a pharmacy in Tanzania?",
"answer_en": "A pharmacy is regulated by Tanzania health laws — specifically the Tanzania Medicines and Medical Devices Authority (TMDA). GN 487A restricts retail trade broadly, but medicine is a specialised sector requiring TMDA licences. If a non-citizen has a TMDA licence and the business operates as a formal pharmacy, their situation depends on how GN 487A is interpreted for the health sector. A legal adviser who understands both health laws and GN 487A is needed for a full answer. Legal advice is essential before making decisions.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_065_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Mariamu, mfanyabiashara wa Kariakoo, anasema mchina jirani wake ana 'vibali vyote' — inamaanisha nini?",
"answer_sw": "Hata mgeni mwenye 'vibali vyote' (kama leseni ya biashara, VAT, TIN, kibali cha makazi) hawezi kufanya biashara katika makundi 15 yaliyozuiliwa chini ya GN 487A. Vibali hivyo ni vya biashara ya jumla — si kibali cha kufanya biashara YOYOTE. GN 487A ina nguvu juu ya vibali vingine kwa sekta zilizozuiliwa. Mchina huyo akiwa na duka la rejareja au biashara nyingine ya makundi 15, bado anakiuka GN 487A bila kujali vibali alivyo navyo. Mariamu asikubali usemi wa 'nina vibali vyote' kama ushahidi wa uhalali wa biashara hiyo.",
"question_en": "Mariamu, a Kariakoo trader, says her Chinese neighbour has 'all the permits' — what does this mean?",
"answer_en": "Even a non-citizen with 'all the permits' (such as a business licence, VAT, TIN, residence permit) cannot operate in the 15 prohibited categories under GN 487A. Those permits are for general business — they are not a permit to operate ANY business. GN 487A takes precedence over other permits for the prohibited sectors. If that Chinese national has a retail shop or another of the 15 prohibited categories, they still violate GN 487A regardless of what permits they hold. Mariamu should not accept 'I have all the permits' as evidence of the legality of that business.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "business_market", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_066_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Mgeni ana mkoba wa fedha anaoumba biashara mpya — anaweza kufanya nini bila kukiuka GN 487A?",
"answer_sw": "Kuna sekta nyingi ambazo hazizuiliwi na GN 487A na zinaweza kuvutia uwekezaji wa kigeni, kama: uzalishaji wa viwanda, kilimo cha biashara kubwa, madini, ujenzi, teknolojia ya habari, utalii (hotel na lodge, si wakala), afya (hospitali, kliniki), elimu (shule na vyuo), na huduma za kitaalamu (kama sheria na uhasibu kwa firm zilizosajiliwa). Mwekezaji anapaswa kuchunguza sekta hizi na kushauriana na TIC (Tanzania Investment Centre) na wakili wa biashara ili kupata mwelekeo sahihi wa jinsi ya kuwekeza kwa njia ya kisheria.",
"question_en": "A non-citizen investor has capital to start a new business — what can they do without violating GN 487A?",
"answer_en": "There are many sectors not restricted by GN 487A that can attract foreign investment, such as: industrial manufacturing, large-scale commercial agriculture, mining, construction, information technology, tourism (hotels and lodges, not agencies), health (hospitals, clinics), education (schools and colleges), and professional services (such as law and accounting for registered firms). Investors should explore these sectors and consult TIC (Tanzania Investment Centre) and a business lawyer to get proper guidance on how to invest legally.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "business_market", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_067_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Kaka yangu aliyekuwa mgeni lakini sasa ana uraia wa Tanzania — je, GN 487A inamzuia bado?",
"answer_sw": "Hapana. Mtu aliyepata uraia wa Tanzania kwa njia ya kisheria sio tena 'mgeni' kwa madhumuni ya GN 487A. GN 487A inazuia 'watu wasio raia wa Tanzania' — na kaka yako sasa ni raia wa Tanzania. Anaweza kufanya biashara katika makundi yote 15 yaliyozuiliwa kwa wageni, kwa sababu kama raia wa Tanzania ana haki kamili za kibiashara. Atahitaji leseni za kawaida za biashara, usajili wa TRA, na vibali vingine vya kawaida, lakini si kizuizi cha GN 487A.",
"question_en": "My brother used to be a non-citizen but now has Tanzanian citizenship — does GN 487A still restrict him?",
"answer_en": "No. A person who has lawfully obtained Tanzanian citizenship is no longer a 'non-citizen' for GN 487A purposes. GN 487A restricts 'persons who are not Tanzanian citizens' — and your brother is now a Tanzanian citizen. He can operate businesses in all 15 categories that were previously restricted for non-citizens, because as a Tanzanian citizen he has full business rights. He will need the normal business licences, TRA registration, and other standard permits, but not the GN 487A restriction.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "rural_conversational", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_068_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Serikali ilitoa GN 487A kwa sababu gani hasa?",
"answer_sw": "Serikali ya Tanzania ilitoa GN 487A (2025) kwa lengo la kulinda fursa za kibiashara kwa raia wa Tanzania — hasa katika biashara ndogo ndogo na za kati ambazo zimekuwa zikifanywa na wageni. Amri inalenga makundi 15 ya biashara ambazo kwa miaka mingi zilikuwa zikifanywa na wageni badala ya Watanzania. Lengo ni kuwezesha wafanyabiashara wa Tanzania kupata sehemu ya kiuchumi katika sekta hizi. Hii ni sera ya sera ya uchumi shirikishi (economic empowerment) inayolenga ukuzaji wa biashara za Watanzania.",
"question_en": "Why exactly did the government issue GN 487A?",
"answer_en": "The Government of Tanzania issued GN 487A (2025) to protect business opportunities for Tanzanian citizens — particularly in small and medium enterprises that had been operated by non-citizens. The Order targets 15 business categories that for many years had been dominated by non-citizens rather than Tanzanians. The goal is to enable Tanzanian entrepreneurs to gain an economic share in these sectors. This is an economic empowerment policy aimed at growing Tanzanian businesses.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_069_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Tangu GN 487A ilitangazwa, je, kuna mabadiliko yoyote au marekebisho?",
"answer_sw": "Kulingana na taarifa za hadi Juni 2026, hakuna marekebisho rasmi ya GN 487A yaliyotangazwa kwenye Gazeti la Serikali. Amri ilibaki kama ilivyosajiliwa mwaka 2025. Operesheni ya utekelezaji ilifanyika (Septemba-Oktoba 2025) na sheria bado inafanya kazi. Inashauriwa daima kuthibitisha hali ya sasa ya GN 487A kwenye TanzLII.org au kupitia wakili wa biashara wa Tanzania, kwa sababu sheria za Tanzania zinaweza kubadilishwa au kufutwa wakati wowote kupitia Gazette.",
"question_en": "Since GN 487A was published, are there any changes or amendments?",
"answer_en": "According to information available up to June 2026, no official amendments to GN 487A have been published in the Government Gazette. The Order remained as gazetted in 2025. The enforcement exercise took place (September-October 2025) and the law continues to be in force. It is always advisable to verify the current status of GN 487A at TanzLII.org or through a Tanzanian business lawyer, as Tanzanian laws can be amended or revoked at any time through the Gazette.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_070_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Wakili wa kigeni anaweza kufungua ofisi ya kisheria Tanzania?",
"answer_sw": "Huduma za kisheria zinasimamiwa na Sheria ya Watetezi (Advocates Act) ya Tanzania, si tu GN 487A. Ili kufanya kazi kama wakili Tanzania, mtu lazima awe mwanachama wa chama cha mawakili cha Tanzania (TLS — Tanganyika Law Society) na awe amesajiliwa na Mahakama Kuu. Sheria ya Watetezi inaweza kuzuia wageni kufanya kazi kama watetezi wanaosimama mahakamani bila vikwazo. GN 487A haitaji huduma za kisheria (legal services) kama moja ya makundi 15 yaliyozuiliwa wazi. Hata hivyo, vikwazo vya TLS vinaweza kutumika. Mshauri wa TLS au wakili wa kienyeji anahitajika kwa ushauri sahihi.",
"question_en": "Can a foreign lawyer open a law office in Tanzania?",
"answer_en": "Legal services are regulated by Tanzania's Advocates Act, not just GN 487A. To practice as an advocate in Tanzania, one must be a member of the Tanzanyika Law Society (TLS) and registered with the High Court. The Advocates Act may restrict non-citizens from serving as advocates appearing in court without limitations. GN 487A does not list legal services (legal services) as one of the 15 explicitly prohibited categories. However, TLS restrictions may apply. Consultation with TLS or a local lawyer is needed for accurate advice.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_071_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Hassan ni fundi wa umeme kutoka Msumbiji — ana uwezo wa kufanya kazi Tanzania?",
"answer_sw": "Kazi ya ufundi wa umeme (electrical contractor) haiko kati ya makundi 15 yaliyozuiliwa wazi na GN 487A. Hassan anaweza kufanya kazi kama fundi wa umeme Tanzania, lakini lazima: (1) Awe na kibali sahihi cha kufanya kazi (work permit) kutoka Wizara ya Kazi, (2) Asajiliwe na Bodi ya Wahandisi (ERB — Engineers Registration Board) ikiwa atatoa huduma za uhandisi rasmi. Kama Hassan ataanzisha kampuni yake mwenyewe ya ufundi wa umeme na KUUZA bidhaa za umeme (rejareja), sehemu ya uuzaji inaweza kukiuka GN 487A. Kufanya kazi kama fundi wa mshahara au mkandarasi si tatizo kwa GN 487A.",
"question_en": "Hassan is an electrician from Mozambique — can he work in Tanzania?",
"answer_en": "Electrical contractor work is not among the 15 categories explicitly prohibited by GN 487A. Hassan can work as an electrician in Tanzania, but he must: (1) Have a valid work permit from the Ministry of Labour, (2) Register with the Engineers Registration Board (ERB) if providing formal engineering services. If Hassan establishes his own electrical company and SELLS electrical goods (retail), the selling aspect may violate GN 487A. Working as a salaried electrician or contractor is not a GN 487A issue.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "rural_conversational", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_072_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Mwenzi wangu mgeni anaendesha basi la mwendazake — je, hii ni tatizo?",
"answer_sw": "Huduma za usafiri wa abiria (passenger transport) haziko kati ya makundi 15 yaliyozuiliwa wazi na GN 487A. Hata hivyo, kuendesha gari ya biashara Tanzania kunahitaji: leseni ya SUMATRA (Surface and Marine Transport Regulatory Authority), usajili wa TRA, na kibali sahihi cha kufanya kazi kwa dereva mgeni. GN 487A peke yake haitazuia mgeni kuendesha basi la mwendazake, lakini sheria nyingine za usafirishaji na kazi zinaweza kutumika. Mwenzi wako anapaswa kuhakikisha ana hati zote za kisheria kabla ya kuendesha biashara hiyo.",
"question_en": "My foreign associate runs a daladala (minibus) — is this a problem?",
"answer_en": "Passenger transport services are not among the 15 categories explicitly prohibited by GN 487A. However, operating a commercial vehicle in Tanzania requires: a SUMATRA (Surface and Marine Transport Regulatory Authority) licence, TRA registration, and a valid work permit for a non-citizen driver. GN 487A alone would not prohibit a non-citizen from running a daladala, but other transport and labour laws may apply. Your associate should ensure they have all the legal documents before operating that business.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "rural_conversational", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_073_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Je, GN 487A inatumika Tanzania Visiwani (Zanzibar)?",
"answer_sw": "Hapana. GN 487A ni amri ya Serikali ya Jamhuri ya Muungano kwa Tanzania Bara peke yake. Zanzibar ina mfumo wake wa kisheria unaotawaliwa na Serikali ya Mapinduzi ya Zanzibar (SMZ), ambao unatofautiana na sheria za Tanzania Bara kwa mambo mengi ya biashara na uwekezaji. Mgeni anayefanya biashara Zanzibar anahitaji kuzingatia sheria za Zanzibar — zikiwa ni pamoja na Sheria ya Uwekezaji ya Zanzibar (ZIPA — Zanzibar Investment Promotion Authority). Kwa maswali ya biashara Zanzibar, wasiliana na ZIPA au wakili wa kisheria wa Zanzibar.",
"question_en": "Does GN 487A apply in Zanzibar?",
"answer_en": "No. GN 487A is an Order of the Union Government of Tanzania Mainland only. Zanzibar has its own legal framework governed by the Revolutionary Government of Zanzibar (RGZ), which differs from Tanzania Mainland laws in many aspects of business and investment. A non-citizen doing business in Zanzibar needs to follow Zanzibar laws — including Zanzibar Investment Law (ZIPA — Zanzibar Investment Promotion Authority). For business questions in Zanzibar, contact ZIPA or a Zanzibar legal adviser.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_074_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Ndugu yangu mgeni ana duka Dodoma — hajui kama anakiuka sheria. Nisaidie vipi?",
"answer_sw": "Msaidie ndugu yako kufanya hatua hizi haraka: (1) Angalia ikiwa biashara yake ipo katika moja ya makundi 15 yaliyozuiliwa (rejareja, jumla, pesa za simu, ukarabati wa simu, saluni, na mengine). (2) Kama ipo kwenye orodha, msaidie kupata wakili wa biashara au wa uhamiaji Dodoma haraka — kabla ya operesheni ya Idara ya Uhamiaji. (3) Chaguo ni: simamisha biashara, au hamisha umiliki kwa Mtanzania kwa njia ya kisheria. Kutokuwa na habari za sheria hakumkinga dhidi ya adhabu — GN 487A haina msamaha wa kutojua.",
"question_en": "My non-citizen sibling has a shop in Dodoma — they do not know if they are breaking the law. How can I help?",
"answer_en": "Help your sibling take these steps urgently: (1) Check if their business is in one of the 15 prohibited categories (retail, wholesale, mobile money, phone repair, salon, and others). (2) If it is on the list, help them find a business or immigration lawyer in Dodoma quickly — before an Immigration Department enforcement exercise. (3) Options are: stop the business, or transfer ownership to a Tanzanian citizen through a legal process. Lack of knowledge of the law does not protect against penalties — GN 487A has no ignorance exemption.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "rural_conversational", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_075_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Orodha yote ya makundi 15 ya GN 487A ipo wapi ili nione?",
"answer_sw": "Orodha kamili ya makundi 15 yaliyozuiliwa ipo katika maandiko rasmi ya GN 487A. Unaweza kuipata bure kwenye TanzLII.org (Tanzania Legal Information Institute): https://tanzlii.org/akn/tz/act/gn/2025/487a/eng@2025-07-28. Tovuti hii inaonyesha nakala kamili ya amri kama ilivyosajiliwa kwenye Gazeti la Serikali. Makampuni ya kisheria kama Bowmans, Dentons, DLA Piper, na VELMA Law pia yamechapisha muhtasari wa orodha kwenye tovuti zao — hizi ni muhimu kwa uelewa wa haraka, ingawa ni bora soma amri yenyewe ili kupata orodha kamili na sahihi.",
"question_en": "Where can I find the full list of all 15 GN 487A categories?",
"answer_en": "The complete list of the 15 prohibited categories is in the official text of GN 487A. You can access it free of charge at TanzLII.org (Tanzania Legal Information Institute): https://tanzlii.org/akn/tz/act/gn/2025/487a/eng@2025-07-28. This website shows the full text of the Order as gazetted. Law firms such as Bowmans, Dentons, DLA Piper, and VELMA Law have also published summaries of the list on their websites — these are useful for a quick overview, but it is best to read the Order itself for the complete and accurate list.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "business_market", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_076_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Je, GN 487A inazuia wageni kufanya kilimo Tanzania?",
"answer_sw": "Kilimo kwa ujumla hakiko kati ya makundi 15 yaliyozuiliwa wazi na GN 487A. Mgeni anaweza kufanya kilimo Tanzania — lakini kuna vizuizi vingine vya kisheria kama umiliki wa ardhi (sheria ya Tanzania inazuia wageni kumiliki ardhi moja kwa moja, wanaweza kukodisha tu) na makubaliano ya uwekezaji wa kilimo yanayohitaji idhini ya serikali. Hata hivyo, kama kilimo hicho kinajumuisha KUUZA mazao moja kwa moja kwa wateja kwa njia ya rejareja au jumla, sehemu hiyo ya biashara inaweza kukiuka GN 487A.",
"question_en": "Does GN 487A prohibit non-citizens from farming in Tanzania?",
"answer_en": "Farming in general is not among the 15 categories explicitly prohibited by GN 487A. A non-citizen can engage in farming in Tanzania — but there are other legal restrictions such as land ownership (Tanzania law restricts non-citizens from directly owning land; they can only lease) and agricultural investment agreements requiring government approval. However, if that farming involves SELLING produce directly to customers through retail or wholesale channels, that aspect of the business may violate GN 487A.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "rural_conversational", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_077_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Mgeni anayemiliki hoteli Tanzania — je, GN 487A inaathiri hoteli?",
"answer_sw": "Hoteli na huduma za malazi (hospitality/hotel industry) haziko kati ya makundi 15 yaliyozuiliwa wazi na GN 487A. Kwa hiyo, mgeni anaweza kumiliki hoteli Tanzania bila kukiuka GN 487A moja kwa moja. Hata hivyo, anahitaji leseni za Tanzania Tourism Board (TTB), kuzingatia sheria za OSHA, kulipa kodi zote zinazohusika, na kuhakikisha wafanyakazi wa kigeni wana vibali vya kazi. Kama hoteli hiyo pia inaendesha duka la rejareja au huduma za mobile money kwa wateja, sehemu hizo zinaweza kuathiriwa na GN 487A.",
"question_en": "A non-citizen owns a hotel in Tanzania — does GN 487A affect hotels?",
"answer_en": "Hotels and hospitality/accommodation services are not among the 15 categories explicitly prohibited by GN 487A. Therefore, a non-citizen can own a hotel in Tanzania without directly violating GN 487A. However, they need Tanzania Tourism Board (TTB) licences, must comply with OSHA regulations, pay all relevant taxes, and ensure foreign staff have work permits. If the hotel also operates a retail shop or mobile money services for guests, those aspects may be affected by GN 487A.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "business_market", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_078_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Mwalimu mgeni anayefundisha shule ya kibinafsi Tanzania — ana tatizo la GN 487A?",
"answer_sw": "Huduma za elimu (shule na vyuo) haziko kati ya makundi 15 yaliyozuiliwa na GN 487A. Mwalimu mgeni anayefundisha shule ya kibinafsi hawezi kukiuka GN 487A kwa shughuli hiyo. Hata hivyo, lazima awe na: kibali cha kufanya kazi (work permit) kutoka Wizara ya Kazi, usajili kutoka Wizara ya Elimu (kwa shule), na ATCl (Aliens Travel Certificate, inahitajika kwa baadhi ya aina za wageni). Kama shule hiyo pia inaendesha duka la vitabu na vifaa vya shule (rejareja), sehemu hiyo inaweza kuathiriwa na GN 487A.",
"question_en": "A foreign teacher running a private school in Tanzania — do they have a GN 487A issue?",
"answer_en": "Education services (schools and colleges) are not among the 15 prohibited categories under GN 487A. A foreign teacher running a private school does not violate GN 487A through that activity. However, they must have: a work permit from the Ministry of Labour, registration from the Ministry of Education (for the school), and other relevant permits. If the school also operates a bookshop selling stationery (retail), that aspect may be affected by GN 487A.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_079_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Nini tofauti kati ya 'kumiliki biashara' na 'kufanya kazi' chini ya GN 487A?",
"answer_sw": "GN 487A inazuia watu wasio raia KUMILIKI na KUENDESHA biashara katika makundi 15 — si 'kufanya kazi' kwa ujumla. Tofauti muhimu: Kumiliki/Kuendesha: wewe ni mmiliki wa biashara, unafanya maamuzi ya biashara, unafaidika moja kwa moja na faida — hii imezuiliwa. Kufanya kazi: wewe ni mfanyakazi wa mshahara wa kampuni inayomilikiwa na Mtanzania — hii inaruhusiwa kwa vibali sahihi vya kazi. Mfano: mgeni anayemiliki saluni (KUMILIKI) = kuvunja GN 487A. Mgeni anayefanya kazi kama msusi wa mshahara katika saluni inayomilikiwa na Mtanzania = halali (kwa kibali cha kazi sahihi).",
"question_en": "What is the difference between 'owning a business' and 'working' under GN 487A?",
"answer_en": "GN 487A prohibits non-citizens from OWNING and OPERATING businesses in the 15 categories — not 'working' in general. The key distinction: Owning/Operating: you are the business owner, you make business decisions, you directly benefit from profits — this is prohibited. Working: you are a salaried employee of a Tanzanian-owned company — this is allowed with a valid work permit. Example: a non-citizen who owns a salon (OWNING) = violates GN 487A. A non-citizen working as a salaried hairdresser in a Tanzanian-owned salon = legal (with a valid work permit).",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "business_market", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_080_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Kifupi: GN 487A ni nini, inazuia nini, na adhabu ni zipi — jibu kwa sentensi tatu tu?",
"answer_sw": "GN 487A ni Amri ya Leseni za Biashara (2025) inayozuia watu WASIO RAIA wa Tanzania kumiliki biashara katika makundi 15 maalum — hii ni AMRI YA BIASHARA, si ya makazi. Makundi yaliyozuiliwa yanajumuisha: rejareja, jumla, pesa za simu, ukarabati wa simu, saluni, forex, vituo vya mafuta, madalali, usafirishaji wa forodha, utalii, ajira, courier, vipande, kusaga unga, na nyingine 2. Adhabu kwa mgeni anayevunja amri ni: faini ya angalau TZS milioni 10, kifungo cha hadi miezi 6 (si zaidi), na kufutwa kwa viza; Mtanzania anayemsaidia anaweza kupata faini ya TZS milioni 5 au miezi 3 jela.",
"question_en": "Summary: what is GN 487A, what does it prohibit, and what are the penalties — answer in three sentences only?",
"answer_en": "GN 487A is a Business Licensing Order (2025) that prohibits NON-TANZANIAN CITIZENS from owning businesses in 15 specific categories — it is a BUSINESS ORDER, not an immigration or residence permit order. Prohibited categories include: retail, wholesale, mobile money, phone repair, salons, forex bureaus, petrol stations, brokerage, clearing and forwarding, travel agencies, employment bureaus, courier, spare parts, flour milling, and one other. Penalties for a non-citizen violating the Order are: a minimum TZS 10 million fine, up to 6 months imprisonment (not exceeding), and visa revocation; a Tanzanian who assists may face a TZS 5 million fine or 3 months imprisonment.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "business_market", "pair_type": "adversarial", "eval_set": False
},
]

# Append to existing file
with open(OUT, "a", encoding="utf-8") as f:
    for pair in PAIRS:
        f.write(json.dumps(pair, ensure_ascii=False) + "\n")

print(f"Appended {len(PAIRS)} pairs to {OUT}")

# Count full file and show register distribution
from collections import Counter
all_pairs = []
with open(OUT, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            all_pairs.append(json.loads(line))

regs = Counter(p["register"] for p in all_pairs)
print(f"\nFull batch: {len(all_pairs)} pairs")
print(f"Register distribution:")
print(f"  business_market: {regs['business_market']} ({regs['business_market']/len(all_pairs)*100:.0f}%)")
print(f"  formal:          {regs['formal']} ({regs['formal']/len(all_pairs)*100:.0f}%)")
print(f"  rural_conv:      {regs['rural_conversational']} ({regs['rural_conversational']/len(all_pairs)*100:.0f}%)")
