#!/usr/bin/env python3
"""
batch_006 part 3: eac_str_basics (30, tier1b) + digital_services_tax (20, tier1a)
IDs: b006_eac_001–030, b006_dst_001–020
Append to: datasets/tier1a/raw_sources/raw_pairs_batch_006.jsonl
"""
import json, os

OUT = "datasets/tier1a/raw_sources/raw_pairs_batch_006.jsonl"

SRC_EAC = "https://www.comesa.int/simplified-trade-regime/"
NAME_EAC = "COMESA - Simplified Trade Regime"
SRC_VAT = "https://www.tra.go.tz/page/value-added-tax"
NAME_VAT = "TRA - Value Added Tax"

def eac(id_, q_sw, a_sw, q_en, a_en, register, pair_type):
    return {
        "id": id_,
        "domain": "tier1b",
        "subdomain": "eac_str_basics",
        "question_sw": q_sw,
        "answer_sw": a_sw,
        "question_en": q_en,
        "answer_en": a_en,
        "primary_source_url": SRC_EAC,
        "primary_source_name": NAME_EAC,
        "source_type": "ilo_unctad_official",
        "effective_date": "2007-01-01",
        "decay_risk": "stable",
        "next_review_trigger": "EAC/COMESA Common List revision or threshold amendment",
        "verified_by": "founder_self_review",
        "verified_date": "2026-06-10",
        "register": register,
        "pair_type": pair_type,
        "eval_set": False
    }

def dst(id_, q_sw, a_sw, q_en, a_en, register, pair_type):
    return {
        "id": id_,
        "domain": "tier1a",
        "subdomain": "digital_services_tax",
        "question_sw": q_sw,
        "answer_sw": a_sw,
        "question_en": q_en,
        "answer_en": a_en,
        "primary_source_url": SRC_VAT,
        "primary_source_name": NAME_VAT,
        "source_type": "government_portal",
        "effective_date": "2025-09-01",
        "decay_risk": "annual",
        "next_review_trigger": "Finance Act amendment or CG notice on digital VAT implementation",
        "verified_by": "founder_self_review",
        "verified_date": "2026-06-10",
        "register": register,
        "pair_type": pair_type,
        "eval_set": False
    }

pairs = [

# ================================================================
# EAC STR BASICS — 30 pairs (tier1b)
# ================================================================

# --- Group 1: What is STR ---

eac("b006_eac_001",
    "STR maana yake nini kwa mfanyabiashara mdogo wa mpakani?",
    "STR (Simplified Trade Regime — Utaratibu Rahisi wa Biashara) ni mfumo wa EAC na COMESA unaoruhusu wafanyabiashara wadogo kupita forodha bila malipo ya ushuru wa kawaida. Kwa kutumia STR, bidhaa zinazovuka mpaka zinaweza kupita bila ushuru mkubwa kama masharti mawili yanakidhiwa: thamani ya bidhaa haitazidi Dola za Marekani 2,000, na bidhaa zipo kwenye Orodha ya Pamoja (Common List).",
    "What does STR mean for a small border trader?",
    "STR (Simplified Trade Regime) is an EAC and COMESA framework that allows small traders to cross borders without paying standard customs duties. Under STR, goods crossing a border can pass duty-free if two conditions are met: the value of goods does not exceed USD 2,000 per consignment, and the goods are on the Common List.",
    "rural_conversational", "standard"),

eac("b006_eac_002",
    "STR ililenga kuwasaidia wafanyabiashara gani?",
    "STR ililenga kuwasaidia wafanyabiashara wadogo wa mpakani — hasa wanawake wanaouza mazao, vyakula, na bidhaa ndogo ndogo kati ya nchi za EAC na COMESA. Biashara kubwa na makampuni makubwa yanayoagiza bidhaa kwa wingi bado yanatumia utaratibu wa kawaida wa forodha.",
    "Who does STR aim to help?",
    "STR was designed to help small border traders — especially women selling produce, food, and small goods between EAC and COMESA countries. Large businesses and companies importing goods in large quantities still use the standard customs process.",
    "rural_conversational", "standard"),

eac("b006_eac_003",
    "STR ni utaratibu wa nchi moja au wa kikanda?",
    "STR ni utaratibu wa kikanda — inatekelezwa kwa pamoja na nchi wanachama wa EAC na COMESA. Tanzania, Kenya, Uganda, Rwanda, Burundi, DRC, Zambia na nchi nyingine zinashiriki. Hii inamaanisha mfanyabiashara wa Tanzania anaweza kutumia STR wakati wa biashara na nchi yoyote mwanachama inayoshiriki.",
    "Is STR a single-country or regional arrangement?",
    "STR is a regional arrangement — jointly implemented by EAC and COMESA member states. Tanzania, Kenya, Uganda, Rwanda, Burundi, DRC, Zambia and other countries participate. This means a Tanzanian trader can use STR when trading with any participating member state.",
    "formal", "standard"),

# --- Group 2: USD 2,000 threshold ---

eac("b006_eac_004",
    "Kizingiti cha STR ni Dola ngapi — USD 2,000 au USD 3,000?",
    "Kizingiti cha STR ni Dola za Marekani 2,000 (USD 2,000) kwa msafara mmoja (per consignment) — si USD 3,000. Bidhaa zenye thamani ya hadi USD 2,000 zinaweza kupita bila ushuru wa forodha kama zipo kwenye Common List. Kama thamani inazidi USD 2,000, utaratibu wa kawaida wa forodha unatumika.",
    "What is the STR threshold — USD 2,000 or USD 3,000?",
    "The STR threshold is USD 2,000 per consignment — not USD 3,000. Goods worth up to USD 2,000 can pass duty-free if they are on the Common List. If the value exceeds USD 2,000, the standard customs process applies.",
    "rural_conversational", "adversarial"),

eac("b006_eac_005",
    "Kizingiti cha USD 2,000 ni kwa safari moja au kwa mwezi?",
    "Kizingiti cha USD 2,000 ni kwa MSAFARA MMOJA (per consignment) — si kwa wiki au mwezi. Kila wakati unapovuka mpaka na bidhaa, thamani yake hiyo inazingatiwa. Mfanyabiashara anaweza kufanya safari nyingi, lakini kila safari lazima iwe chini ya USD 2,000.",
    "Is the USD 2,000 threshold per trip or per month?",
    "The USD 2,000 threshold is per CONSIGNMENT — not per week or month. Each time you cross the border with goods, that value is assessed. A trader can make multiple trips, but each trip must be below USD 2,000.",
    "rural_conversational", "disambiguation"),

eac("b006_eac_006",
    "Bidhaa zangu zina thamani ya USD 2,500 — naweza kutumia STR?",
    "Hapana. STR inatumika tu kama thamani ya msafara wako haitazidi USD 2,000. Kwa msafara wenye thamani ya USD 2,500, lazima utumie utaratibu wa kawaida wa forodha ukijumuisha ushuru wa kawaida wa bidhaa hizo. Njia moja ya kisheria ni kugawanya msafara kwenye safari mbili tofauti — lakini thibitisha na ofisa wa forodha.",
    "My goods are worth USD 2,500 — can I use STR?",
    "No. STR applies only if your consignment value does not exceed USD 2,000. For a consignment worth USD 2,500, you must use the standard customs process including regular customs duties. One legal approach is splitting into two separate trips — but verify with a customs officer.",
    "rural_conversational", "standard"),

eac("b006_eac_007",
    "Je, thamani ya USD 2,000 inahesabiwa kwa sarafu gani — dola, shilingi, au bei ya soko?",
    "Thamani ya USD 2,000 inahesabiwa kwa Dola za Marekani (USD) — lakini wakati wa kuhesabu, inaweza kubadilishwa kwa sarafu ya ndani kwa kiwango cha ubadilishaji wa siku hiyo. Ofisa wa forodha ndiye anayehesabu thamani halisi. Hakikisha una kumbukumbu ya bei ya bidhaa zako.",
    "Is the USD 2,000 value calculated in dollars, shillings, or market price?",
    "The USD 2,000 value is denominated in US Dollars — but when assessed, it can be converted to local currency at the exchange rate of that day. The customs officer calculates the actual value. Make sure you have a record of your goods' prices.",
    "rural_conversational", "standard"),

# --- Group 3: Common List ---

eac("b006_eac_008",
    "Common List ya STR ina bidhaa ngapi na ina bidhaa gani?",
    "Common List ya STR ina takriban bidhaa 370 zilizoidhinishwa. Inajumuisha hasa: mazao ya kilimo (mahindi, viazi, mboga, matunda), vyakula vya kaya, nguo za kawaida, na bidhaa ndogo ndogo za kila siku. Orodha kamili inapatikana kwenye ofisi za forodha au tovuti za EAC/COMESA.",
    "How many products are on the STR Common List and what does it include?",
    "The STR Common List has approximately 370 approved products. It mainly includes: agricultural produce (maize, potatoes, vegetables, fruits), household food items, everyday clothing, and small everyday goods. The full list is available at customs offices or on EAC/COMESA websites.",
    "rural_conversational", "standard"),

eac("b006_eac_009",
    "Je, bidhaa zote za EAC zipo kwenye Common List ya STR?",
    "Hapana. Si bidhaa zote zinazozalishwa au kuuzwa EAC zipo kwenye Common List. Common List ina bidhaa takriban 370 maalum zilizochaguliwa. Bidhaa nyingi za viwandani, bidhaa za hatari, au bidhaa za teknolojia hazipo kwenye orodha hiyo. Kabla ya kusafiri, angalia kama bidhaa zako zipo kwenye Common List.",
    "Are all EAC goods on the STR Common List?",
    "No. Not all goods produced or sold in the EAC are on the Common List. The Common List contains approximately 370 specific selected products. Many manufactured goods, hazardous goods, or technology products are not on the list. Before travelling, check whether your goods are on the Common List.",
    "formal", "adversarial"),

eac("b006_eac_010",
    "Mchele, mahindi na viazi — vipo kwenye Common List ya STR?",
    "Ndiyo. Mazao ya kilimo ya msingi kama mchele, mahindi, na viazi kwa ujumla yamo kwenye Common List ya STR. Hii ndiyo sababu STR inafaa sana kwa wakulima na wafanyabiashara wa mazao ya kilimo wanaovuka mipaka ya EAC. Thibitisha na ofisi ya forodha hali ya bidhaa maalum kabla ya safari.",
    "Rice, maize, and potatoes — are they on the STR Common List?",
    "Yes. Basic agricultural crops like rice, maize, and potatoes are generally on the STR Common List. This is why STR is especially beneficial for farmers and agricultural produce traders crossing EAC borders. Confirm with the customs office the status of specific goods before travelling.",
    "rural_conversational", "standard"),

# --- Group 4: 4 instruments ---

eac("b006_eac_011",
    "STR ina zana gani kuu 4 za biashara?",
    "STR ina zana 4 kuu: (1) Simplified Certificate of Origin (SCO) — hati inayothibitisha asili ya bidhaa; (2) Simplified Customs Document (SCD) — fomu rahisi ya forodha badala ya fomu ngumu; (3) Common List — orodha ya bidhaa ~370 zinazostahili STR; (4) Kizingiti cha USD 2,000 — mipaka ya thamani ya msafara.",
    "What are the 4 main STR instruments?",
    "STR has 4 main instruments: (1) Simplified Certificate of Origin (SCO) — a document certifying the origin of goods; (2) Simplified Customs Document (SCD) — a simplified customs form instead of complex forms; (3) Common List — list of ~370 eligible goods; (4) USD 2,000 threshold — the consignment value limit.",
    "formal", "standard"),

eac("b006_eac_012",
    "Simplified Certificate of Origin (SCO) ni nini na inapatikanaje?",
    "SCO (Simplified Certificate of Origin) ni hati inayothibitisha kwamba bidhaa zimezalishwa au kutengenezwa ndani ya nchi wanachama wa EAC/COMESA. Inapatikana kutoka kwa mamlaka za forodha au ofisi za biashara nchini. SCO inahitajika kuonyesha bidhaa zinastahili kupata manufaa ya STR.",
    "What is the Simplified Certificate of Origin (SCO) and how do you get one?",
    "An SCO (Simplified Certificate of Origin) is a document certifying that goods were produced or processed within an EAC/COMESA member state. It is obtained from customs authorities or trade offices in the country. The SCO is required to show goods qualify for STR benefits.",
    "formal", "standard"),

eac("b006_eac_013",
    "Simplified Customs Document (SCD) ni rahisi kiasi gani?",
    "SCD ni fomu rahisi ya forodha iliyoundwa maalum kwa wafanyabiashara wadogo wa STR. Ina sehemu chache zaidi na lugha rahisi zaidi kuliko fomu ya kawaida ya forodha. Lengo lake ni kupunguza ugumu wa karatasi kwa wafanyabiashara wadogo ambao wengi hawana elimu ya juu ya biashara.",
    "How simplified is the Simplified Customs Document (SCD)?",
    "The SCD is a simplified customs form designed specifically for small STR traders. It has fewer sections and simpler language than the standard customs form. Its purpose is to reduce paperwork complexity for small traders, many of whom may not have advanced business education.",
    "rural_conversational", "standard"),

# --- Group 5: CRITICAL disambiguation ---

eac("b006_eac_014",
    "Asili ya bidhaa (originating status) na Common List — ni tofauti gani kwa STR?",
    "Hii ni tofauti muhimu sana kwa STR: ORIGINATING STATUS inamaanisha bidhaa imezalishwa ndani ya nchi za EAC/COMESA — hii inahitajika. COMMON LIST inamaanisha aina ya bidhaa imo kwenye orodha ya ~370 zilizoidhinishwa — hii pia inahitajika. Hizi ni masharti MAWILI TOFAUTI. Bidhaa inayotoka EAC lakini haipo kwenye Common List HAIPATWI manufaa ya STR. Bidhaa ipo kwenye Common List lakini imezalishwa China HAIPATWI manufaa ya STR pia.",
    "Originating status and the Common List — what is the difference for STR?",
    "This is a critical STR distinction: ORIGINATING STATUS means goods were produced within EAC/COMESA countries — this is required. COMMON LIST means the type of goods is among the ~370 approved items — this is also required. These are TWO SEPARATE conditions. Goods from EAC that are NOT on the Common List do NOT qualify for STR benefits. Goods that ARE on the Common List but produced in China also do NOT qualify for STR benefits.",
    "formal", "disambiguation"),

eac("b006_eac_015",
    "Nina mahindi kutoka Tanzania yanayokwenda Kenya — mahindi yote ya Tanzania yanapata STR?",
    "Lazima masharti mawili yakidhiwe. Kwanza: mahindi lazima yawe kwenye Common List — ndiyo, mahindi kwa ujumla yako. Pili: mahindi lazima yathibitishwe kuzalishwa Tanzania (originating status) kupitia SCO. Kama masharti yote mawili yanakidhiwa na thamani haitazidi USD 2,000, basi unapata manufaa ya STR.",
    "I have Tanzanian maize going to Kenya — do all Tanzanian maize get STR benefits?",
    "Two conditions must both be met. First: maize must be on the Common List — yes, maize is generally on it. Second: maize must be certified as produced in Tanzania (originating status) via an SCO. If both conditions are met and value does not exceed USD 2,000, then you get STR benefits.",
    "rural_conversational", "standard"),

eac("b006_eac_016",
    "Bidhaa yangu ipo kwenye Common List lakini imezalishwa China — ninapata STR?",
    "Hapana. Uhalali wa STR unahitaji ORIGINATING STATUS — bidhaa lazima izalishwe ndani ya nchi wanachama wa EAC/COMESA. Bidhaa iliyozalishwa China haistahili STR hata kama aina yake ipo kwenye Common List. Masharti yote mawili — asili ya ndani (originating) NA imo kwenye Common List — lazima yakidhiwe.",
    "My product is on the Common List but was made in China — do I get STR benefits?",
    "No. STR eligibility requires ORIGINATING STATUS — goods must be produced within EAC/COMESA member states. Goods produced in China do not qualify for STR even if their category is on the Common List. Both conditions — domestic origin (originating) AND on the Common List — must be satisfied.",
    "formal", "adversarial"),

eac("b006_eac_017",
    "Originating status inamaanisha bidhaa yote ya malighafi kutoka EAC au inatosha kuzalishwa EAC?",
    "Kwa ujumla, 'originating status' inamaanisha bidhaa zimepitia mchakato wa kutosha wa uzalishaji ndani ya nchi wanachama — si lazima malighafi yote kutoka EAC. Kwa bidhaa za kilimo zinazopandwa na kuvunwa ndani ya nchi wanachama, hii ni rahisi kuthibitisha. Kwa bidhaa zilizosindikwa, kanuni za asili (rules of origin) za EAC zinatoa mwongozo zaidi.",
    "Does originating status mean all raw materials from EAC or is it enough to be produced in EAC?",
    "Generally, 'originating status' means goods have undergone sufficient processing within member states — not necessarily that all raw materials are from EAC. For agricultural goods grown and harvested within member states, this is straightforward to demonstrate. For processed goods, EAC rules of origin provide further guidance.",
    "formal", "disambiguation"),

eac("b006_eac_018",
    "Nina bidhaa zinazozalishwa Tanzania lakini hazipo kwenye Common List — ninaweza kutumia STR?",
    "Hapana. Ingawa bidhaa zako zinazalishwa Tanzania (originating status ✓), kama hazipo kwenye Common List, hazistahili manufaa ya STR. Lazima masharti yote mawili yakidhiwe. Kwa bidhaa zisizopo kwenye Common List, utaratibu wa kawaida wa forodha na ushuru unaotumika.",
    "I have goods produced in Tanzania but not on the Common List — can I use STR?",
    "No. Although your goods are produced in Tanzania (originating status ✓), if they are not on the Common List, they do not qualify for STR benefits. Both conditions must be met. For goods not on the Common List, the standard customs process and applicable duties apply.",
    "rural_conversational", "adversarial"),

# --- Group 6: Practical STR process ---

eac("b006_eac_019",
    "Mfanyabiashara wa mpakani anahitaji hati gani kutumia STR?",
    "Hati zinazohitajika kwa STR: (1) Simplified Certificate of Origin (SCO) — kuthibitisha asili ya bidhaa; (2) Simplified Customs Document (SCD) — fomu rahisi ya forodha; (3) Utambulisho wa kibinafsi (kitambulisho cha taifa au pasipoti). Pia, orodha ya bidhaa na bei zake ni muhimu. Ofisi ya forodha itaweza kukusaidia zaidi.",
    "What documents does a border trader need to use STR?",
    "Documents needed for STR: (1) Simplified Certificate of Origin (SCO) — to prove the origin of goods; (2) Simplified Customs Document (SCD) — the simplified customs form; (3) Personal identification (national ID or passport). Additionally, a list of goods and their prices is important. The customs office can assist you further.",
    "rural_conversational", "standard"),

eac("b006_eac_020",
    "Mfanyabiashara wa mipaka anaweza kupata SCO wapi?",
    "SCO inapatikana kutoka kwa mamlaka za forodha au ofisi za biashara nchini Tanzania. Katika maeneo mengi ya mpakani, kuna ofisi maalum zinazosaidia wafanyabiashara wadogo kupata hati za STR. Thibitisha na ofisi ya forodha ya eneo lako au Ofisi ya Biashara ya Wilaya.",
    "Where can a border trader get an SCO?",
    "The SCO is available from customs authorities or trade offices in Tanzania. In many border areas, there are dedicated offices to help small traders obtain STR documents. Confirm with your local customs office or District Trade Office.",
    "rural_conversational", "standard"),

eac("b006_eac_021",
    "Je, mwanawake mdogo wa mipaka anaweza kutumia STR bila msaada wa mwanasheria?",
    "Ndiyo — hilo ndilo lengo lake. STR iliundwa ili wafanyabiashara wadogo, wakiwemo wanawake wasio na elimu ya juu ya biashara, waweze kutumia forodha kwa urahisi zaidi. Hati (SCO, SCD) ni rahisi zaidi kuliko utaratibu wa kawaida. Ofisi za forodha za mpakani zinapaswa kuwa na wataalam wa kusaidia.",
    "Can a small woman border trader use STR without a lawyer?",
    "Yes — that is exactly the purpose. STR was designed so that small traders, including women without advanced business education, can navigate customs more easily. The documents (SCO, SCD) are simpler than the standard process. Border customs offices should have staff available to assist.",
    "rural_conversational", "standard"),

eac("b006_eac_022",
    "Je, STR inatumika kwenye bandari ya Dar es Salaam au mpakani wa nchi tu?",
    "STR iliundwa kimsingi kwa biashara ya mpakani (land borders) kati ya nchi za EAC/COMESA. Bandari ya Dar es Salaam inahudumia biashara ya bahari ya kimataifa ambayo inatumia utaratibu tofauti wa forodha. Kwa biashara ndogo za mpakani wa ardhini (kama Namanga, Mutukula, Tunduma), STR ndiyo mfumo unaofaa.",
    "Does STR apply at Dar es Salaam port or only at land borders?",
    "STR was designed primarily for land border trade between EAC/COMESA countries. Dar es Salaam port serves international sea trade which uses a different customs process. For small land border trade (such as Namanga, Mutukula, Tunduma), STR is the appropriate framework.",
    "business_market", "disambiguation"),

eac("b006_eac_023",
    "Mfanyabiashara wa biashara kubwa (commercial importer) anaweza kutumia STR?",
    "Hapana kwa kawaida. STR iliundwa kwa wafanyabiashara WADOGO wa mpakani — si wafanyabiashara wa biashara kubwa au makampuni ya uingizaji bidhaa. Makampuni makubwa yanayoagiza bidhaa kwa wingi bado yanatumia utaratibu wa kawaida wa forodha na chanzo cha ushuru unaofaa.",
    "Can a large commercial importer use STR?",
    "Not typically. STR was designed for SMALL border traders — not large-scale commercial businesses or importing companies. Large companies importing goods in bulk still use the standard customs process and applicable duty rates.",
    "formal", "disambiguation"),

eac("b006_eac_024",
    "Mfanyabiashara wa Tanzania anaweza kutumia STR kuuza bidhaa Kenya?",
    "Ndiyo. Mfanyabiashara wa Tanzania anaweza kutumia STR kuuza bidhaa Kenya (na nchi nyingine wanachama) kama masharti yanakidhiwa: bidhaa zimezalishwa Tanzania (originating ✓), zipo kwenye Common List (✓), na thamani haitazidi USD 2,000 kwa msafara (✓). STR inafanya kazi kwa njia mbili — kuingiza na kutoa bidhaa.",
    "Can a Tanzanian trader use STR to sell goods in Kenya?",
    "Yes. A Tanzanian trader can use STR to sell goods in Kenya (and other member states) if conditions are met: goods produced in Tanzania (originating ✓), on the Common List (✓), and value does not exceed USD 2,000 per consignment (✓). STR works in both directions — importing and exporting.",
    "rural_conversational", "standard"),

# --- Group 7: Refusals and edge cases ---

eac("b006_eac_025",
    "Je, kila mpaka wa Tanzania una uwezo wa kushughulikia STR?",
    "Sina uhakika wa orodha kamili ya mipaka yote inayoshughulikia STR Tanzania. Mipaka mikubwa kama Namanga (Kenya), Mutukula (Uganda), na Tunduma (Zambia) kwa ujumla ina mfumo wa STR. Lakini mipaka midogo au ya mbali inaweza kuwa na uwezo tofauti. Thibitisha na Tanzania Revenue Authority (TRA) au ofisi ya forodha ya mpaka unaolengwa.",
    "Does every Tanzanian border crossing have STR capacity?",
    "I am not certain of the complete list of Tanzania border crossings with STR capacity. Major crossings like Namanga (Kenya), Mutukula (Uganda), and Tunduma (Zambia) generally have STR systems in place. But smaller or remote crossings may have different capacity. Verify with TRA or the specific border's customs office.",
    "formal", "out_of_corpus_refusal"),

eac("b006_eac_026",
    "Je, STR inatumika kwa bidhaa za mazao ya bahari (samaki, pweza)?",
    "Bidhaa za mazao ya bahari zinaweza kuwa kwenye Common List, lakini hali inategemea aina maalum ya bidhaa. Samaki safi na bidhaa za bahari zinazozalishwa ndani ya EAC kwa ujumla zinaweza kustahili — lakini thibitisha na ofisi ya forodha kama aina yako mahususi ipo kwenye Common List ya sasa.",
    "Does STR apply to marine products (fish, octopus)?",
    "Marine products may be on the Common List, but eligibility depends on the specific type. Fresh fish and marine products produced within EAC can generally qualify — but verify with the customs office whether your specific type is on the current Common List.",
    "rural_conversational", "disambiguation"),

eac("b006_eac_027",
    "EAC STR na COMESA STR — ni tofauti au mfumo mmoja?",
    "EAC STR na COMESA STR ni mifumo inayofanana na inayounganishwa — si tofauti kabisa. Nchi nyingi za EAC pia ni wanachama wa COMESA, na wanaheshimu mifumo yote miwili. Masharti ya msingi (USD 2,000, Common List) yanafanana sana. Mabadiliko madogo yanaweza kuwepo kwa nchi maalum — thibitisha na ofisi ya forodha.",
    "EAC STR and COMESA STR — are they different or the same framework?",
    "EAC STR and COMESA STR are similar and interconnected frameworks — not completely separate. Many EAC countries are also COMESA members, and they honor both frameworks. The core conditions (USD 2,000, Common List) are very similar. Minor variations may exist for specific countries — verify with the customs office.",
    "formal", "disambiguation"),

eac("b006_eac_028",
    "Je, thamani ya msafara USD 2,000 hasa — STR inatumika au haitumiki?",
    "Kizingiti ni 'haitazidi USD 2,000' — kwa hivyo bidhaa zenye thamani ya USD 2,000 hasa (si zaidi ya) zinastahili STR kama masharti mengine yanakidhiwa. Thamani ya USD 2,001 inatosha kuvuka kizingiti na kusababisha utaratibu wa kawaida.",
    "If consignment value is exactly USD 2,000 — does STR apply or not?",
    "The threshold is 'does not exceed USD 2,000' — so goods valued at exactly USD 2,000 (not more) qualify for STR if other conditions are met. A value of USD 2,001 is enough to exceed the threshold and trigger the standard customs process.",
    "formal", "standard"),

eac("b006_eac_029",
    "STR inakuwa na matatizo gani yanayoripotiwa mara kwa mara?",
    "Matatizo yanayoripotiwa mara kwa mara ni pamoja na: ofisa wa forodha kutowajua mfumo wa STR vizuri, ucheleweshaji wa kutoa SCO, na kutopatikana kwa SCD kwenye baadhi ya mipaka. Wafanyabiashara wanashauriwa kujua haki zao za STR na kuomba msimamizi mkuu kama ofisa hawajui mfumo. Thibitisha haki zako na TRA.",
    "What problems are commonly reported with STR?",
    "Commonly reported problems include: customs officers not being fully familiar with STR, delays in issuing SCOs, and unavailability of SCDs at some border crossings. Traders are advised to know their STR rights and ask for a senior officer if the officer is unfamiliar with the system. Confirm your rights with TRA.",
    "rural_conversational", "standard"),

eac("b006_eac_030",
    "Kwa muhtasari: mfanyabiashara wa mipaka anahitaji nini kufaidika na STR?",
    "Kufaidika na STR, mfanyabiashara anahitaji: (1) Bidhaa zilizozalishwa ndani ya EAC/COMESA (originating status) — thibitishwa na SCO; (2) Aina ya bidhaa ipo kwenye Common List (~370 bidhaa); (3) Thamani ya msafara si zaidi ya USD 2,000; (4) Simplified Customs Document (SCD) iliyojazwa vizuri; (5) Kitambulisho cha kibinafsi. Masharti yote lazima yakidhiwe — si moja au mawili tu.",
    "Summary: what does a border trader need to benefit from STR?",
    "To benefit from STR, a trader needs: (1) Goods produced within EAC/COMESA (originating status) — certified by SCO; (2) Goods category on the Common List (~370 products); (3) Consignment value not exceeding USD 2,000; (4) A properly completed Simplified Customs Document (SCD); (5) Personal identification. All conditions must be met — not just one or two.",
    "rural_conversational", "standard"),

# ================================================================
# DIGITAL SERVICES TAX — 20 pairs (tier1a)
# ================================================================

# --- Group 1: What are digital services ---

dst("b006_dst_001",
    "Huduma za kidijitali maana yake nini kwa madhumuni ya VAT Tanzania?",
    "Huduma za kidijitali ni huduma zinazotolewa kwa njia ya mtandao au mfumo wa kielektroniki — kama vile streaming ya video na muziki, programu za simu (apps), huduma za wingu (cloud), matangazo ya mtandaoni, na michezo ya video. Kwa madhumuni ya VAT, TRA inafuatilia huduma kama hizo zinazotolewa Tanzania.",
    "What do digital services mean for VAT purposes in Tanzania?",
    "Digital services are services provided via the internet or electronic system — such as video and music streaming, mobile applications (apps), cloud services, online advertising, and video games. For VAT purposes, TRA tracks such services supplied in Tanzania.",
    "formal", "standard"),

dst("b006_dst_002",
    "Je, Tanzania ina kodi maalum ya huduma za kidijitali?",
    "Ndiyo. Sheria ya Fedha ya 2025 ilianzisha mabadiliko yanayoathiri VAT kwenye miamala ya kielektroniki. Kiwango cha VAT cha 16% kinatumiwa kwa malipo ya B2C (biashara-kwa-wateja) ya kielektroniki kuanzia 1 Septemba 2025. Hii ni tofauti na kiwango cha kawaida cha VAT cha 18% kinachotumika kwa bidhaa na huduma za kawaida.",
    "Does Tanzania have a special tax on digital services?",
    "Yes. The Finance Act 2025 introduced changes affecting VAT on electronic transactions. A 16% VAT rate applies to B2C (business-to-consumer) electronic payments from 1 September 2025. This differs from the standard 18% VAT rate that applies to regular goods and services.",
    "formal", "standard"),

dst("b006_dst_003",
    "VAT ya 16% ya B2C e-payment — inamaanisha nini kwa vitendo?",
    "Kuanzia 1 Septemba 2025, malipo ya kielektroniki ya B2C (wateja wanaolipa bidhaa/huduma kwa njia ya simu au mtandao) yanabeba kiwango cha VAT cha 16% — badala ya 18% ya kawaida. Hii inaathiri mifumo ya malipo ya kidijitali kama M-Pesa, Tigo Pesa, kadi za benki, na njia nyingine za malipo ya kielektroniki. Maelezo ya utekelezaji bado yanangojewa kutoka TRA.",
    "The 16% B2C e-payment VAT — what does it mean in practice?",
    "From 1 September 2025, B2C electronic payments (consumers paying for goods/services via mobile or internet) carry a 16% VAT rate — instead of the standard 18%. This affects digital payment systems like M-Pesa, Tigo Pesa, bank cards, and other electronic payment methods. Implementation details are still awaited from TRA.",
    "formal", "standard"),

dst("b006_dst_004",
    "Tofauti kati ya VAT 18% ya kawaida na VAT 16% ya e-payment ni ipi?",
    "VAT 18%: kiwango cha kawaida kinachotumika kwa bidhaa na huduma nyingi Tanzania. VAT 16%: kiwango maalum kwa malipo ya B2C ya kielektroniki (e-payments) kuanzia 1 Sep 2025. Tofauti ni asilimia 2 — lakini maelezo ya jinsi ya kupanga hizi mbili (kuamua ni ipi inatumika) yanategemea kanuni za utekelezaji kutoka TRA. Thibitisha na TRA mara kanuni zinapatikana.",
    "What is the difference between the standard 18% VAT and the 16% e-payment VAT?",
    "VAT 18%: the standard rate applying to most goods and services in Tanzania. VAT 16%: a special rate for B2C electronic payments (e-payments) from 1 Sep 2025. The difference is 2 percentage points — but the details of how to apply each (deciding which applies) depend on TRA's implementation rules. Verify with TRA once rules are available.",
    "formal", "disambiguation"),

dst("b006_dst_005",
    "Netflix, Spotify — zinatozwa VAT Tanzania?",
    "Kwa ujumla, watoa huduma wa kidijitali wa nje ya nchi (non-resident providers) wanaotoa huduma kwa wateja Tanzania wanaweza kuwa na wajibu wa VAT Tanzania. Hata hivyo, utekelezaji halisi wa sheria hii dhidi ya makampuni makubwa ya kimataifa ni suala ngumu. Sina uhakika wa hali halisi ya sasa ya makampuni kama Netflix na Spotify dhidi ya TRA. Thibitisha na TRA au mshauri wa kodi.",
    "Netflix, Spotify — are they subject to VAT in Tanzania?",
    "Generally, non-resident digital service providers supplying services to Tanzanian consumers may have Tanzania VAT obligations. However, the practical enforcement of this against major international companies is complex. I am not certain of the current specific status of companies like Netflix and Spotify with TRA. Verify with TRA or a tax advisor.",
    "formal", "out_of_corpus_refusal"),

dst("b006_dst_006",
    "Mtoa huduma wa nje ya nchi anayetoa huduma za kidijitali Tanzania — wajibu wake wa VAT ni nini?",
    "Kwa ujumla, sheria ya VAT Tanzania inaweza kuhitaji watoa huduma wa kidijitali wa nje ya nchi wanaotoa huduma kwa wateja Tanzania kusajiliwa kwa VAT Tanzania. Hata hivyo, masharti maalum ya kizingiti cha usajili na mchakato wa utekelezaji yanategemea kanuni za TRA. Thibitisha na TRA au mshauri wa kodi.",
    "A non-resident digital service provider supplying services to Tanzania — what are their VAT obligations?",
    "Generally, Tanzania VAT law may require non-resident digital service providers supplying services to Tanzanian customers to register for Tanzania VAT. However, specific registration threshold requirements and enforcement processes depend on TRA regulations. Verify with TRA or a tax advisor.",
    "formal", "out_of_corpus_refusal"),

dst("b006_dst_007",
    "Matangazo ya mtandaoni (online ads) yanayolipwa na kampuni ya Tanzania — VAT inatumika?",
    "Ndiyo. Kampuni ya Tanzania inayolipa kwa huduma za matangazo ya mtandaoni (kama Google Ads, Meta Ads) inapaswa kuzingatia VAT au withholding tax inayohusika. Kwa huduma kutoka watoa wa nje, withholding tax ya 6% (services) inaweza kutumika kuanzia 1 Julai 2025. Thibitisha muundo maalum na mshauri wa kodi.",
    "Online advertising payments by a Tanzanian company — does VAT apply?",
    "Yes. A Tanzanian company paying for online advertising services (like Google Ads, Meta Ads) should consider applicable VAT or withholding tax. For services from foreign providers, 6% withholding tax (services) may apply from 1 July 2025. Confirm specific structure with a tax advisor.",
    "business_market", "standard"),

dst("b006_dst_008",
    "Duka la mtandaoni la Tanzania linauza bidhaa — EFD inahitajika?",
    "Ndiyo. Duka la mtandaoni (e-commerce store) la Tanzania linalouza bidhaa kwa wateja Tanzania linahitaji EFD (Electronic Fiscal Device) kama kampuni inastahili VAT. Kila mauzo lazima itoe risiti ya EFD. Biashara za mtandaoni hazipewi msamaha wa EFD kwa sababu ya kuwa za kidijitali.",
    "A Tanzanian online shop selling goods — is EFD required?",
    "Yes. A Tanzanian e-commerce store selling goods to Tanzanian customers requires an EFD (Electronic Fiscal Device) if the company is VAT-registered. Every sale must issue an EFD receipt. Online businesses are not exempt from EFD just because they are digital.",
    "business_market", "standard"),

dst("b006_dst_009",
    "Withholding tax ya 6% ya huduma — inaathiri malipo ya kidijitali?",
    "Withholding tax ya 6% kwenye huduma (services) ilianza 1 Julai 2025 chini ya Sheria ya Fedha 2025. Inaathiri malipo ya huduma zinazotolewa — ikiwa ni pamoja na huduma za kidijitali kama programu (software), ushauri wa IT, na huduma za wingu (cloud) kutoka watoa wa nje. Mlipaji wa Tanzania lazima ashikilie 6% na ailipe TRA.",
    "6% withholding tax on services — does it affect digital payments?",
    "The 6% withholding tax on services started 1 July 2025 under the Finance Act 2025. It affects payments for services supplied — including digital services like software, IT consulting, and cloud services from foreign providers. The Tanzanian payer must withhold 6% and remit it to TRA.",
    "formal", "standard"),

dst("b006_dst_010",
    "Kwa muhtasari: mfanyabiashara wa Tanzania anapaswa kujua nini kuhusu kodi za huduma za kidijitali?",
    "Mambo makuu: (1) VAT ya kawaida ni 18% — bado inatumika kwa bidhaa/huduma nyingi; (2) VAT ya 16% kwa B2C e-payments kuanzia 1 Sep 2025; (3) Withholding tax 6% kwa huduma (ikiwa ni pamoja na kidijitali) kuanzia 1 Jul 2025; (4) EFD inahitajika kwa mauzo ya mtandaoni pia; (5) Watoa huduma wa nje wanaweza kuwa na wajibu wa VAT Tanzania. Thibitisha maelezo ya utekelezaji na TRA kwa sababu kanuni fulani bado zinaandaliwa.",
    "Summary: what does a Tanzanian business need to know about digital services taxes?",
    "Key points: (1) Standard VAT is 18% — still applies to most goods/services; (2) 16% VAT on B2C e-payments from 1 Sep 2025; (3) 6% withholding tax on services (including digital) from 1 Jul 2025; (4) EFD is required for online sales too; (5) Foreign service providers may have Tanzania VAT obligations. Verify implementation details with TRA as some rules are still being finalized.",
    "business_market", "standard"),

dst("b006_dst_011",
    "Biashara ya kuuza programu za simu (mobile apps) Tanzania — VAT inatumika?",
    "Ndiyo. Uuzaji wa programu za simu kwa wateja Tanzania unashughulikiwa kama huduma ya kidijitali na unabeba VAT inayofaa. Kama kampuni imesajiliwa VAT, lazima itoe risiti za EFD na ikusanye VAT. Kwa watoa kutoka nje ya nchi, masharti yanaweza kutofautiana — thibitisha na TRA.",
    "A business selling mobile apps in Tanzania — does VAT apply?",
    "Yes. Selling mobile apps to Tanzanian customers is treated as a digital service and carries applicable VAT. If the company is VAT-registered, it must issue EFD receipts and collect VAT. For foreign-based providers, requirements may differ — verify with TRA.",
    "formal", "standard"),

dst("b006_dst_012",
    "Huduma za wingu (cloud storage/computing) — kodi gani Tanzania?",
    "Huduma za wingu (cloud storage, cloud computing) zinachukuliwa kama huduma zinazokabiliwa na VAT Tanzania na possibly withholding tax. Kwa watoa wa ndani: VAT 18% + EFD. Kwa watoa wa nje ya nchi: withholding tax 6% inaweza kutumika kwa mlipaji wa Tanzania. Thibitisha muundo wako mahususi na mshauri wa kodi.",
    "Cloud services (cloud storage/computing) — what taxes apply in Tanzania?",
    "Cloud services are treated as services subject to Tanzania VAT and possibly withholding tax. For domestic providers: 18% VAT + EFD. For foreign-based providers: 6% withholding tax may apply for the Tanzanian payer. Confirm your specific structure with a tax advisor.",
    "formal", "standard"),

dst("b006_dst_013",
    "Biashara ya usafirishaji wa Uber/Bolt Tanzania — VAT inatumika?",
    "Ndiyo. Huduma za usafirishaji wa kidijitali kama Uber na Bolt zinachukuliwa kama huduma za biashara zinazostahili VAT Tanzania. Kama mtoaji wa huduma amefika kizingiti cha usajili wa VAT (TZS 200M/mwaka au TZS 100M/miezi 6), lazima asajiliwe na ikusanye VAT. Hata hivyo, masharti maalum ya makampuni ya kidijitali ya kimataifa yanategemea muundo wao wa biashara Tanzania.",
    "Ride-hailing business like Uber/Bolt in Tanzania — does VAT apply?",
    "Yes. Digital transport services like Uber and Bolt are treated as business services subject to Tanzania VAT. If the service provider has reached the VAT registration threshold (TZS 200M/year or TZS 100M/6 months), they must register and collect VAT. However, specific requirements for international digital companies depend on their Tanzania business structure.",
    "business_market", "standard"),

dst("b006_dst_014",
    "Je, ada za biashara za WhatsApp Business zina kodi Tanzania?",
    "WhatsApp Business (toleo la bure) halitozi ada — kwa hivyo hakuna swali la kodi la moja kwa moja. WhatsApp Business API (inayotumiwa na makampuni makubwa) inaweza kuwa na ada kutoka Meta — hizi zinastahili kuzingatiwa kama huduma za kidijitali za nje ya nchi. Sina uhakika wa hali halisi ya kodi ya WhatsApp Business API Tanzania. Thibitisha na mshauri wa kodi.",
    "Are there taxes in Tanzania on WhatsApp Business fees?",
    "WhatsApp Business (free version) has no fees — so there is no direct tax question. WhatsApp Business API (used by large companies) may have fees from Meta — these could be considered foreign digital services and subject to withholding tax considerations. I am not certain of the exact tax status of WhatsApp Business API in Tanzania. Verify with a tax advisor.",
    "business_market", "out_of_corpus_refusal"),

dst("b006_dst_015",
    "Duka la mtandaoni linalonunua kutoka China na kuuza Tanzania — VAT ya ununuzi inashughulikiwa vipi?",
    "Kwa ununuzi wa bidhaa kutoka China (importation): ushuru wa forodha na VAT ya uingizaji inatumika. Kwa mauzo ya bidhaa kwa wateja Tanzania: VAT ya kawaida ya 18% inatumika kama umefikia kizingiti cha usajili. Hizi ni shughuli mbili tofauti za kodi. Thibitisha taratibu zote na mshauri wa kodi au TRA.",
    "An online shop buying from China and selling in Tanzania — how is the VAT on purchases handled?",
    "For purchases of goods from China (importation): import duties and import VAT apply. For sales of goods to Tanzanian customers: standard 18% VAT applies if you have reached the registration threshold. These are two separate tax transactions. Confirm all procedures with a tax advisor or TRA.",
    "business_market", "standard"),

dst("b006_dst_016",
    "Je, kizingiti cha usajili wa VAT kinatumika kwa biashara za kidijitali?",
    "Ndiyo. Kizingiti cha VAT Tanzania (TZS 200M/mwaka au TZS 100M/miezi 6) kinatumika kwa biashara zote — za kidijitali NA za kimwili. Biashara ya mtandaoni inayofikia kizingiti hiki lazima isajiliwe kwa VAT kama kampuni yoyote nyingine.",
    "Does the VAT registration threshold apply to digital businesses?",
    "Yes. Tanzania's VAT registration threshold (TZS 200M/year or TZS 100M/6 months) applies to all businesses — digital AND physical. An online business reaching this threshold must register for VAT like any other company.",
    "formal", "standard"),

dst("b006_dst_017",
    "Withholding tax kwa programu (software licences) za nje — kiwango gani?",
    "Withholding tax kwenye huduma (services) kutoka nje ya nchi, ikiwa ni pamoja na leseni za programu (software licences), ni 6% kuanzia 1 Julai 2025 (Sheria ya Fedha 2025). Kampuni ya Tanzania inayolipa kwa leseni ya programu ya nje ya nchi lazima ishikilie 6% na ilipe TRA. Kiwango cha 3% kinatumiwa kwa bidhaa, si huduma.",
    "Withholding tax on foreign software licences — what rate?",
    "Withholding tax on services from foreign countries, including software licences, is 6% from 1 July 2025 (Finance Act 2025). A Tanzanian company paying for a foreign software licence must withhold 6% and remit it to TRA. The 3% rate applies to goods, not services.",
    "formal", "standard"),

dst("b006_dst_018",
    "Kampuni yangu inatumia huduma za AI/cloud kutoka nje — ninashikilia withholding tax?",
    "Ndiyo. Malipo kwa huduma za AI, cloud computing, au huduma nyingine za kidijitali kutoka watoa wa nje ya nchi yanastahili withholding tax ya 6% (huduma) kuanzia 1 Jul 2025. Umshikilie mtoa huduma (usimlipie kiasi chote) na ulipe 6% TRA peke yako. Hii inakuruhusu kupata gharama hiyo kama gharama inayopunguzwa.",
    "My company uses AI/cloud services from abroad — do I withhold tax?",
    "Yes. Payments for AI services, cloud computing, or other digital services from foreign providers are subject to 6% withholding tax (services) from 1 July 2025. Withhold from the provider (do not pay them the full amount) and remit 6% to TRA yourself. This allows you to treat the cost as a deductible expense.",
    "business_market", "standard"),

dst("b006_dst_019",
    "Streaming ya michezo ya video (gaming) Tanzania — kodi gani?",
    "Huduma za michezo ya video za kidijitali zinachukuliwa kama huduma za kidijitali na zinakabiliwa na VAT Tanzania. Kama mtoa wa ndani, VAT 18% inatumika. Kwa watoa wa nje, withholding tax ya 6% inaweza kutumika kwa mlipaji wa Tanzania. Maelezo ya utekelezaji kwa makampuni makubwa ya gaming ya kimataifa yanahitaji kuthibitishwa na TRA.",
    "Video game streaming in Tanzania — what taxes apply?",
    "Digital video game services are treated as digital services subject to Tanzania VAT. For domestic providers, 18% VAT applies. For foreign providers, 6% withholding tax may apply to the Tanzanian payer. Implementation details for large international gaming companies should be verified with TRA.",
    "business_market", "standard"),

dst("b006_dst_020",
    "Muhtasari: biashara ya kidijitali Tanzania inahitaji kuzingatia kodi zipi?",
    "Biashara ya kidijitali Tanzania inapaswa kuzingatia: (1) VAT 18% kwa bidhaa/huduma za kawaida (kizingiti TZS 200M/mwaka); (2) VAT 16% kwa B2C e-payments kuanzia 1 Sep 2025; (3) Withholding tax 3% kwa bidhaa za nje, 6% kwa huduma za nje (kuanzia 1 Jul 2025); (4) EFD inahitajika kwa mauzo yote — mtandaoni pia; (5) PAYE na SDL kwa wafanyakazi wa kudumu ≥10. Masharti ya utekelezaji wa baadhi ya mabadiliko mapya bado yanaandaliwa na TRA.",
    "Summary: what taxes does a digital business in Tanzania need to consider?",
    "A digital business in Tanzania should consider: (1) 18% VAT on regular goods/services (TZS 200M/year threshold); (2) 16% VAT on B2C e-payments from 1 Sep 2025; (3) Withholding tax 3% on foreign goods, 6% on foreign services (from 1 Jul 2025); (4) EFD required for all sales — including online; (5) PAYE and SDL for permanent staff of 10+. Implementation rules for some new changes are still being finalized by TRA.",
    "business_market", "standard"),

]

# Append to JSONL
written = 0
with open(OUT, "a", encoding="utf-8") as f:
    for pair in pairs:
        f.write(json.dumps(pair, ensure_ascii=False) + "\n")
        written += 1

print(f"Wrote {written} pairs to {OUT}")

from collections import Counter
regs = Counter(p_["register"] for p_ in pairs)
ptypes = Counter(p_["pair_type"] for p_ in pairs)
domains = Counter(p_["domain"] for p_ in pairs)
print("Domain distribution:", dict(domains))
print("Register distribution:", dict(regs))
print("Pair type distribution:", dict(ptypes))
