#!/usr/bin/env python3
"""
batch_006 part 1: gn487a_adversarial — 50 pairs
IDs: b006_gn487a_001 – b006_gn487a_050
Target: correct base-model errors (model says 'residence permit', wrong penalties, wrong agency)
Source: tanzlii.org (official_gazette) + immigration.go.tz (government_portal)
Append to: datasets/tier1a/raw_sources/raw_pairs_batch_006.jsonl
"""
import json, os

OUT = "datasets/tier1a/raw_sources/raw_pairs_batch_006.jsonl"
SRC_TZ = "https://tanzlii.org/akn/tz/act/gn/2025/487a/eng@2025-07-28"
SRC_IM = "https://www.immigration.go.tz/"
NAME_TZ = "Government Notice 487A - Business Licensing Prohibition Order 2025, TanzLII"
NAME_IM = "Immigration Services Department Tanzania"
REVIEW = "GN 487A amendment, court ruling, or ministry clarification"

def p(id_, subdomain, q_sw, a_sw, q_en, a_en, register, pair_type,
      src_url=SRC_TZ, src_name=NAME_TZ, src_type="official_gazette"):
    return {
        "id": id_,
        "domain": "tier1a",
        "subdomain": subdomain,
        "question_sw": q_sw,
        "answer_sw": a_sw,
        "question_en": q_en,
        "answer_en": a_en,
        "primary_source_url": src_url,
        "primary_source_name": src_name,
        "source_type": src_type,
        "effective_date": "2025-07-28",
        "decay_risk": "event_triggered",
        "next_review_trigger": REVIEW,
        "verified_by": "founder_self_review",
        "verified_date": "2026-06-10",
        "register": register,
        "pair_type": pair_type,
        "eval_set": False
    }

pairs = [

# --- GROUP 1: What is GN 487A (corrects "residence permit" base-model error) ---

p("b006_gn487a_001", "gn487a_adversarial",
  "GN 487A ni nini hasa — ni amri ya vibali vya makazi au ni sheria ya biashara?",
  "GN 487A si amri ya vibali vya makazi wala vibali vya kazi. Ni Amri ya Leseni za Biashara inayozuia raia wa kigeni kufanya shughuli fulani za biashara Tanzania Bara. Jina lake kamili ni *Business Licensing (Prohibition of Business Activities for Non-Citizens) Order*. Ilianza kutumika tarehe 28 Julai 2025.",
  "What exactly is GN 487A — is it a residence permit order or a business law?",
  "GN 487A is not a residence permit or work permit order. It is a Business Licensing Order prohibiting non-citizens from engaging in certain business activities in Mainland Tanzania. Its full name is the *Business Licensing (Prohibition of Business Activities for Non-Citizens) Order*. It took effect on 28 July 2025.",
  "formal", "adversarial"),

p("b006_gn487a_002", "gn487a_adversarial",
  "GN 487A ilianza kutumika lini, na kiidara gani kinatekeleza?",
  "GN 487A ilianza rasmi tarehe 28 Julai 2025. Kinachotekeleza ni Idara ya Uhamiaji (Immigration Services Department) — si BRELA, si TRA. Zoezi la kwanza la utekelezaji lilifanyika kati ya tarehe 11 Septemba na 8 Oktoba 2025.",
  "When did GN 487A come into force, and which department enforces it?",
  "GN 487A officially came into force on 28 July 2025. The enforcing agency is the Immigration Services Department — not BRELA, not TRA. The first enforcement exercise took place between 11 September and 8 October 2025.",
  "business_market", "standard",
  SRC_IM, NAME_IM, "government_portal"),

p("b006_gn487a_003", "gn487a_adversarial",
  "GN 487A ilianzishwa kwa sababu gani — ni sheria ya uhamiaji au ya kiuchumi?",
  "GN 487A ni amri ya kiuchumi inayolinda biashara ndogo za Watanzania — si sheria ya uhamiaji. Lengo lake ni kuhifadhi sekta fulani za kiuchumi kwa ajili ya raia wa Tanzania. Uhamiaji unatekeleza amri hii kwa sababu inahusu uraia wa wafanyabiashara, lakini msingi wake ni kiuchumi, si udhibiti wa uhamiaji.",
  "Why was GN 487A created — is it an immigration law or an economic law?",
  "GN 487A is an economic order protecting Tanzanian small businesses — not an immigration law. Its purpose is to reserve certain economic sectors for Tanzanian citizens. Immigration enforces the order because it involves the citizenship status of business operators, but the underlying basis is economic, not immigration control.",
  "formal", "disambiguation"),

p("b006_gn487a_004", "gn487a_adversarial",
  "Je, GN 487A inazuia raia wa kigeni KUISHI Tanzania au KUFANYA BIASHARA?",
  "GN 487A inazuia AINA za biashara — si makazi. Raia wa kigeni ana haki ya kuomba kibali cha makazi na kukaa Tanzania vizuri. GN 487A inasema tu kwamba mkazi huyo mgeni hawezi KUMILIKI au KUENDESHA mojawapo ya shughuli 15 maalum zilizokatazwa.",
  "Does GN 487A prohibit non-citizens from LIVING in Tanzania or from DOING BUSINESS?",
  "GN 487A restricts TYPES of business activity — not residency. A non-citizen has the right to apply for a residence permit and live in Tanzania lawfully. GN 487A only says that the foreign resident cannot OWN or OPERATE one of the 15 specific prohibited activities.",
  "formal", "disambiguation"),

p("b006_gn487a_005", "gn487a_adversarial",
  "Mtu anasema GN 487A ni vibali vya kazi vipya kwa wageni — kweli au uongo?",
  "Uongo kabisa. GN 487A haina uhusiano na vibali vya kazi (work permits). Vibali vya kazi — Class A hadi G — vinasimamia mtu anayefanya kazi kama MWAJIRIWA. GN 487A inasimamia aina za biashara ambazo raia wa kigeni hawezi KUMILIKI au KUENDESHA. Ni sheria mbili tofauti kabisa zenye masharti tofauti.",
  "Someone says GN 487A is new work permits for foreigners — true or false?",
  "Completely false. GN 487A has no connection to work permits. Work permits — Class A through G — govern a person working as an EMPLOYEE. GN 487A governs the types of businesses a non-citizen cannot OWN or OPERATE. They are two completely separate laws with different requirements.",
  "business_market", "adversarial"),

# --- GROUP 2: Prohibited activities (depth on specific activities) ---

p("b006_gn487a_006", "gn487a_adversarial",
  "GN 487A inakataza shughuli ngapi kwa raia wa kigeni, na zipi kuu miongoni mwake?",
  "GN 487A inakataza jumla ya shughuli 15 kwa raia wa kigeni. Miongoni mwa zilizotajwa wazi ni: biashara ya jumla (wholesale) na rejareja (retail), uhamishaji wa pesa wa simu (mobile money transfers), ukarabati wa simu (phone repair), na salon za nywele. Kuna shughuli nyingine 11 zilizoorodheshwa katika amri kamili.",
  "How many activities does GN 487A prohibit for non-citizens, and what are the main ones?",
  "GN 487A prohibits a total of 15 business activities for non-citizens. Among those explicitly mentioned are: wholesale and retail trade, mobile money transfers, phone repair, and hair salons. There are 11 other activities listed in the full order.",
  "formal", "standard"),

p("b006_gn487a_007", "gn487a_adversarial",
  "Wakala wa M-Pesa, Tigo Pesa, au Airtel Money — raia wa kigeni anaweza kuwa wakala?",
  "Hapana. Uhamishaji wa pesa wa simu (mobile money transfers) umeorodheshwa wazi kati ya shughuli 15 zilizokatazwa na GN 487A. Raia wa kigeni hawezi kuwa wakala wa M-Pesa, Tigo Pesa, Airtel Money, au huduma nyingine kama hizo. Ukiukaji unaweza kusababisha faini ya angalau TZS 10,000,000 na kufutwa kwa visa.",
  "M-Pesa, Tigo Pesa, or Airtel Money agent — can a non-citizen be an agent?",
  "No. Mobile money transfers are explicitly listed among the 15 prohibited activities under GN 487A. A non-citizen cannot be an M-Pesa, Tigo Pesa, Airtel Money, or similar mobile money agent. Violations can result in a fine of at least TZS 10,000,000 and visa revocation.",
  "business_market", "standard"),

p("b006_gn487a_008", "gn487a_adversarial",
  "Je, duka la kutengeneza simu linamilikiwa na mgeni ni tatizo gani?",
  "Ukarabati wa simu (phone repair) umekatazwa wazi na GN 487A. Raia wa kigeni hawezi kumiliki au kuendesha duka la ukarabati wa simu Tanzania Bara. Ikiwa ataendelea, anakabiliwa na faini ya angalau TZS milioni 10, kifungo cha hadi miezi 6, na kufutwa kwa visa.",
  "What problem does a non-citizen owning a phone repair shop face?",
  "Phone repair is explicitly prohibited under GN 487A. A non-citizen cannot own or operate a phone repair shop in Mainland Tanzania. If they continue, they face a fine of at least TZS 10 million, up to 6 months imprisonment, and visa revocation.",
  "business_market", "standard"),

p("b006_gn487a_009", "gn487a_adversarial",
  "Biashara ya salon ya nywele — mgeni wa Asia anaweza kuendesha?",
  "Hapana. GN 487A inakataza wazi salon za nywele kwa raia wa kigeni. Mgeni wa Asia anahitaji kuhamisha salon hiyo kwa raia wa Tanzania, au akabiliane na adhabu: faini ya angalau TZS 10,000,000 na kufutwa kwa visa.",
  "Hair salon business — can an Asian non-citizen operate one?",
  "No. GN 487A explicitly prohibits hair salon businesses for non-citizens. An Asian non-citizen needs to transfer the salon to a Tanzanian citizen, or face penalties: a fine of at least TZS 10,000,000 and visa revocation.",
  "rural_conversational", "standard"),

p("b006_gn487a_010", "gn487a_adversarial",
  "Je, biashara ya rejareja yoyote imekatazwa, au ni aina fulani tu?",
  "GN 487A inakataza biashara ya jumla (wholesale) NA rejareja (retail) kwa ujumla kwa raia wa kigeni. Hii inajumuisha maduka ya bidhaa, supermarket ndogo, na uuzaji wa moja kwa moja kwa wateja wa Tanzania. Hakuna msamaha kwa aina ndogo ya rejareja au eneo maalum la biashara.",
  "Is any retail business prohibited, or only specific types?",
  "GN 487A prohibits wholesale AND retail trade in general for non-citizens. This includes goods shops, small supermarkets, and direct sales to Tanzanian consumers. There is no exemption for small-scale retail or a specific business location.",
  "formal", "standard"),

# --- GROUP 3: Who is covered ---

p("b006_gn487a_011", "gn487a_adversarial",
  "Je, GN 487A inalenga mataifa fulani ya kigeni — kama Wachina au Wasomali peke yake?",
  "Hapana. GN 487A inatumika kwa raia WOTE wa kigeni bila kujali nchi wanayotoka. Inajumuisha raia wa China, Somalia, Kenya, Uganda, India, Ulaya, na kila nchi nyingine. Kigezo pekee ni kuwa si raia wa Tanzania — utaifa wenyewe haufanyi tofauti.",
  "Does GN 487A target specific foreign nationalities — like Chinese or Somalis only?",
  "No. GN 487A applies to ALL non-citizens regardless of their country of origin. This includes citizens of China, Somalia, Kenya, Uganda, India, Europe, and every other country. The only criterion is not being a Tanzanian citizen — nationality itself makes no difference.",
  "business_market", "adversarial"),

p("b006_gn487a_012", "gn487a_adversarial",
  "Raia wa EAC — Kenya, Uganda, Rwanda, Burundi — wana msamaha kutoka GN 487A?",
  "Hapana. GN 487A haitoi msamaha kwa raia wa nchi za EAC. Licha ya Itifaki ya Soko la Pamoja la EAC, amri hii inatumika kwa raia wote wa kigeni, ikiwa ni pamoja na raia wa Kenya, Uganda, Rwanda, Burundi, na Sudan Kusini. Wote wanashughulikiwa kama raia wa kigeni chini ya GN 487A.",
  "Are EAC citizens — Kenya, Uganda, Rwanda, Burundi — exempt from GN 487A?",
  "No. GN 487A does not exempt EAC citizens. Despite the EAC Common Market Protocol, this order applies to all non-citizens, including citizens of Kenya, Uganda, Rwanda, Burundi, and South Sudan. They are all treated as non-citizens under GN 487A.",
  "business_market", "adversarial"),

p("b006_gn487a_013", "gn487a_adversarial",
  "Mgeni anayeishi Tanzania kwa miaka 20 ana haki maalum chini ya GN 487A?",
  "Hapana. GN 487A inategemea URAIA, si muda wa makazi. Mtu anayeishi Tanzania kwa miaka 20 bila kupata uraia wa Tanzania bado anachukuliwa kuwa raia wa kigeni chini ya amri hii. Muda wa makazi haumpi msamaha wowote.",
  "Does a non-citizen living in Tanzania for 20 years have special rights under GN 487A?",
  "No. GN 487A is based on CITIZENSHIP, not length of residence. A person who has lived in Tanzania for 20 years without obtaining Tanzanian citizenship is still considered a non-citizen under this order. Length of residence provides no exemption.",
  "rural_conversational", "adversarial"),

p("b006_gn487a_014", "gn487a_adversarial",
  "Watoto wa raia wa kigeni waliozaliwa Tanzania — GN 487A inawasimamia?",
  "Inategemea hali ya uraia wao. Ikiwa mtoto amepata uraia wa Tanzania, GN 487A haimthiri. Ikiwa mtoto bado ni raia wa kigeni licha ya kuzaliwa Tanzania, GN 487A inatumika. Mshauri wa kisheria anaweza kusaidia kutathmini hali ya uraia wa kila mmoja.",
  "Children of non-citizens born in Tanzania — does GN 487A apply to them?",
  "It depends on their citizenship status. If a child has obtained Tanzanian citizenship, GN 487A does not apply to them. If the child remains a non-citizen despite being born in Tanzania, GN 487A applies. A legal adviser can help assess each person's citizenship status.",
  "rural_conversational", "disambiguation"),

p("b006_gn487a_015", "gn487a_adversarial",
  "Je, raia wa kigeni mwenye ndoa na Mtanzania ana msamaha kutoka GN 487A?",
  "Hapana. Ndoa na raia wa Tanzania haimpi mwenzi mgeni uraia wa Tanzania wala msamaha kutoka GN 487A. Uraia unapatikana kupitia mchakato rasmi wa uraia — si ndoa peke yake. Hadi hapo, mwenzi mgeni bado anazingatiwa kama raia wa kigeni chini ya amri hii.",
  "Does a non-citizen married to a Tanzanian get an exemption from GN 487A?",
  "No. Marriage to a Tanzanian citizen does not confer Tanzanian citizenship or an exemption from GN 487A. Citizenship is obtained through a formal naturalization process — not marriage alone. Until then, the foreign spouse is still treated as a non-citizen under this order.",
  "rural_conversational", "adversarial"),

# --- GROUP 4: Penalties (correcting wrong amounts) ---

p("b006_gn487a_016", "gn487a_adversarial",
  "Adhabu ya chini kabisa kwa mgeni anayekiuka GN 487A ni ngapi — TZS 500,000 au zaidi?",
  "Faini ya chini kabisa ni TZS 10,000,000 (milioni kumi) — si TZS 500,000 wala TZS 1,000,000. Mbali na faini, mshtakiwa anaweza pia kupata kifungo cha hadi miezi 6 gerezani NA kufutwa kwa visa yake. Ni adhabu kali mno.",
  "What is the minimum penalty for a non-citizen violating GN 487A — TZS 500,000 or more?",
  "The minimum fine is TZS 10,000,000 (ten million) — not TZS 500,000 or TZS 1,000,000. In addition to the fine, the offender may face up to 6 months imprisonment AND visa revocation. The penalties are severe.",
  "formal", "adversarial"),

p("b006_gn487a_017", "gn487a_adversarial",
  "Je, visa inafutwa pamoja na faini — au ni hatua ya ziada?",
  "Kufutwa kwa visa ni sehemu ya kawaida ya adhabu — si hatua ya ziada ya hiari. Raia wa kigeni aliyepatikana na hatia ya kukiuka GN 487A anaweza kupoteza visa yake na kulazimishwa kuondoka Tanzania. Faini na kufutwa kwa visa vinafanyika pamoja.",
  "Is visa revocation part of the penalty, or an optional extra step?",
  "Visa revocation is a standard part of the penalty — not an optional additional step. A non-citizen found guilty of violating GN 487A can lose their visa and be required to leave Tanzania. The fine and visa revocation happen together.",
  "formal", "standard"),

p("b006_gn487a_018", "gn487a_adversarial",
  "Mtanzania anayenusuru mgeni kukiuka GN 487A atapata adhabu gani?",
  "Mtanzania anayenusuru raia wa kigeni kufanya biashara iliyokatazwa anakabiliwa na faini ya TZS 5,000,000 AU kifungo cha miezi 3 gerezani. Hizi si adhabu za mgeni mwenyewe (TZS 10M na miezi 6) — ni adhabu maalum kwa wanaowezesha ukiukaji.",
  "What penalty does a Tanzanian face for facilitating a GN 487A violation?",
  "A Tanzanian who facilitates a non-citizen in conducting a prohibited business faces a fine of TZS 5,000,000 OR 3 months imprisonment. These are not the same as the penalties for the non-citizen themselves (TZS 10M and 6 months) — they are specific penalties for facilitators.",
  "formal", "adversarial"),

p("b006_gn487a_019", "gn487a_adversarial",
  "Faini ya Mtanzania na faini ya mgeni ni sawa? Kusema kweli.",
  "Hapana, si sawa. Mgeni anayekiuka GN 487A: faini ya angalau TZS 10,000,000 na hadi miezi 6 gerezani na kufutwa kwa visa. Mtanzania anayenusuru ukiukaji: faini ya TZS 5,000,000 AU miezi 3 gerezani. Adhabu ya mgeni ni kali zaidi.",
  "Is the fine for a Tanzanian and a non-citizen the same? Honestly.",
  "No, they are not the same. Non-citizen violating GN 487A: minimum TZS 10,000,000 fine plus up to 6 months imprisonment plus visa revocation. Tanzanian facilitating a violation: TZS 5,000,000 fine OR 3 months imprisonment. The non-citizen's penalty is harsher.",
  "business_market", "standard"),

p("b006_gn487a_020", "gn487a_adversarial",
  "Je, mgeni anaweza kulipa faini na kuendelea na duka lake — kama leseni ya adhabu?",
  "Hapana. Faini si leseni ya kuendelea. Baada ya kulipa faini, biashara bado inabaki kuwa haramu kwa raia wa kigeni, na visa inafutwa. Mtu anaweza kulazimishwa kuondoka Tanzania kabisa. Kulipa faini hakupi haki ya kuendelea.",
  "Can a non-citizen pay the fine and keep the shop open — like a penalty licence?",
  "No. The fine is not a licence to continue. After paying the fine, the business remains illegal for the non-citizen to operate, and the visa is revoked. The person may be required to leave Tanzania entirely. Paying the fine does not grant the right to continue.",
  "business_market", "adversarial"),

# --- GROUP 5: Employment vs ownership (key adversarial) ---

p("b006_gn487a_021", "gn487a_adversarial",
  "Raia wa kigeni ana kibali cha kazi Class B — anaweza kufanya kazi katika duka la rejareja kama mwajiriwa?",
  "Ndiyo — kama MWAJIRIWA. GN 487A inakataza KUMILIKI na KUENDESHA biashara — si kufanya kazi kama mwajiriwa. Raia wa kigeni mwenye Class B anaweza kufanya kazi kama mwajiriwa katika duka la rejareja bila kukiuka GN 487A. Tatizo linatokea tu akimiliki au akiendesha duka mwenyewe.",
  "A non-citizen holds a Class B work permit — can they work in a retail shop as an employee?",
  "Yes — as an EMPLOYEE. GN 487A prohibits OWNING and OPERATING businesses — not working as an employee. A non-citizen with a Class B permit can work as an employee in a retail shop without violating GN 487A. The problem only arises if they own or operate the shop themselves.",
  "business_market", "adversarial"),

p("b006_gn487a_022", "gn487a_adversarial",
  "Je, tofauti kati ya kuendesha duka na kufanya kazi katika duka ni nini chini ya GN 487A?",
  "Kuendesha duka (operating): mmiliki au meneja mkuu anayefanya maamuzi ya biashara — hii imekatazwa kwa raia wa kigeni kwa shughuli 15. Kufanya kazi katika duka (working as employee): mfanyakazi anayetekeleza maelekezo ya mwajiri chini ya kibali cha kazi halali — hii hairuhusiwi na GN 487A. Ni tofauti muhimu.",
  "What is the difference between operating a shop and working in a shop under GN 487A?",
  "Operating a shop: being the owner or primary manager who makes business decisions — this is prohibited for non-citizens across the 15 activities. Working in a shop as an employee: a worker carrying out an employer's instructions under a valid work permit — GN 487A does not prohibit this. It is an important distinction.",
  "formal", "disambiguation"),

p("b006_gn487a_023", "gn487a_adversarial",
  "Kubadilisha kibali cha kazi kunaondoa mipaka ya GN 487A — kweli au uongo?",
  "Uongo. Kibali cha kazi kinahusu aina ya kazi unayoruhusiwa kufanya kama MWAJIRIWA. GN 487A inahusu aina za biashara unazoruhusiwa KUMILIKI au KUENDESHA. Hata ukiwa na Class A, D, au E, bado huwezi kumiliki biashara iliyoorodheshwa kwenye GN 487A. Ni vikwazo viwili tofauti kabisa.",
  "Changing a work permit removes GN 487A restrictions — true or false?",
  "False. A work permit governs the type of employment you are permitted to do as an EMPLOYEE. GN 487A governs the types of businesses you are permitted to OWN or OPERATE. Even with a Class A, D, or E permit, you still cannot own a business listed under GN 487A. They are two completely separate restrictions.",
  "formal", "adversarial"),

p("b006_gn487a_024", "gn487a_adversarial",
  "Ubia (joint venture) kati ya mgeni na Mtanzania — GN 487A inazuiwa?",
  "Hapana. Ubia (joint venture au partnership) hauzui GN 487A. Raia wa kigeni ndani ya ubia bado hawezi kufanya kazi za biashara zilizo kwenye orodha ya 15 kwa niaba yake mwenyewe. Mtanzania ndiye anapaswa kuwa mmiliki mkuu na meneja wa shughuli zilizokatazwa. Muundo wa kisheria sahihi unahitajika.",
  "A joint venture between a non-citizen and a Tanzanian — does this bypass GN 487A?",
  "No. A joint venture or partnership does not bypass GN 487A. The non-citizen within the partnership still cannot perform business activities on the list of 15 on their own behalf. The Tanzanian must be the primary owner and manager of the prohibited activities. Correct legal structuring is required.",
  "business_market", "adversarial"),

p("b006_gn487a_025", "gn487a_adversarial",
  "Mkurugenzi mgeni wa kampuni ya rejareja — je, nafasi yake yenyewe inakiuka GN 487A?",
  "Si kiotomatikilai. Kumiliki hisa au kuwa mkurugenzi msimamia (non-executive director) peke yake si ukiukaji wazi wa GN 487A. Lakini ikiwa mkurugenzi mgeni anafanya kazi za uendeshaji wa kila siku wa biashara ya rejareja, anahatari kukiuka GN 487A. Mstari huu si wazi daima — thibitisha na mwanasheria.",
  "A foreign company director of a retail company — does their role alone violate GN 487A?",
  "Not automatically. Owning shares or serving as a non-executive director alone is not a clear GN 487A violation. But if the foreign director handles day-to-day operational management of the retail business, they risk violating GN 487A. This line is not always clear — verify with a lawyer.",
  "formal", "disambiguation"),

# --- GROUP 6: Specific business types ---

p("b006_gn487a_026", "gn487a_adversarial",
  "Mgeni ana duka la vifaa vya ujenzi (hardware) — je, GN 487A inasimamia?",
  "Ndiyo. Duka la vifaa vya ujenzi ni biashara ya rejareja — na biashara ya rejareja imekatazwa wazi kwa raia wa kigeni. Mgeni hawezi kumiliki au kuendesha duka la hardware Tanzania Bara. Anaweza kufanya kazi kama mwajiriwa wa duka kama ana kibali cha kazi, lakini hawezi kuwa mmiliki.",
  "A non-citizen has a hardware store — does GN 487A apply?",
  "Yes. A hardware store is retail trade — and retail trade is explicitly prohibited for non-citizens. A non-citizen cannot own or operate a hardware store in Mainland Tanzania. They may work as an employee in the store if they have a work permit, but they cannot be the owner.",
  "rural_conversational", "standard"),

p("b006_gn487a_027", "gn487a_adversarial",
  "Mgeni ana mgahawa mdogo jijini — GN 487A inasimamia migahawa?",
  "Ndiyo. Uendeshaji wa migahawa midogo umeorodheshwa kati ya shughuli 15 zilizokatazwa na GN 487A. Mgeni anahitaji au kuhamisha mgahawa huo kwa raia wa Tanzania, au akabiliane na adhabu: faini ya angalau TZS 10 milioni na kufutwa kwa visa.",
  "A non-citizen has a small restaurant in the city — does GN 487A cover restaurants?",
  "Yes. Operating small restaurants is listed among the 15 activities prohibited under GN 487A. The non-citizen needs to either transfer the restaurant to a Tanzanian citizen, or face penalties: a fine of at least TZS 10 million and visa revocation.",
  "business_market", "standard"),

p("b006_gn487a_028", "gn487a_adversarial",
  "Mchina mmoja ana duka la vipuri vya bodaboda kijijini kwetu — ni halali?",
  "Biashara ya uuzaji wa vipuri (spare parts) ni biashara ya rejareja — ambayo imo kwenye orodha ya shughuli 15 zilizokatazwa na GN 487A. Mchina (au mgeni mwingine yeyote) hawezi kumiliki duka hilo. Jambo hili linaweza kuripotiwa kwa Idara ya Uhamiaji.",
  "A Chinese person has a motorcycle spare parts shop in our village — is it legal?",
  "Selling spare parts is retail trade — which is on the list of 15 prohibited activities under GN 487A. A Chinese national (or any other non-citizen) cannot own that shop. This matter can be reported to the Immigration Services Department.",
  "rural_conversational", "standard",
  SRC_IM, NAME_IM, "government_portal"),

p("b006_gn487a_029", "gn487a_adversarial",
  "Biashara ya dawa ya duka — mgeni anaweza kumiliki?",
  "Biashara ya uuzaji wa dawa kwa rejareja imeorodheshwa kati ya shughuli 15 zilizokatazwa na GN 487A. Raia wa kigeni hawezi kumiliki au kuendesha duka la dawa. Mbali na GN 487A, uuzaji wa dawa pia unasimamia na TMDA (Tanzania Medicines and Medical Devices Authority) — masharti ya ziada ya kibali yanaweza kutumika.",
  "A pharmaceutical retail shop — can a non-citizen own it?",
  "Retail sale of medicines is listed among the 15 prohibited activities under GN 487A. A non-citizen cannot own or operate a pharmacy or medicine shop. In addition to GN 487A, medicine sales are also regulated by TMDA (Tanzania Medicines and Medical Devices Authority) — additional licensing requirements may apply.",
  "formal", "standard"),

p("b006_gn487a_030", "gn487a_adversarial",
  "Biashara ya mtandaoni (e-commerce) inayouza bidhaa Tanzania — mgeni anaweza?",
  "Hapana, kama biashara hiyo inauza bidhaa kwa rejareja kwa wateja Tanzania. Biashara ya rejareja kwenye mtandao bado inachukuliwa kama biashara ya rejareja — ambayo imekatazwa kwa raia wa kigeni. Eneo la mtandaoni haibadilishi hali ya kisheria. Wateja wa Tanzania, malipo ya Tanzania — hii ni biashara ya Tanzania.",
  "An e-commerce business selling products in Tanzania — can a non-citizen run it?",
  "No, if the business sells products at retail to customers in Tanzania. Online retail is still considered retail trade — which is prohibited for non-citizens. The online nature does not change the legal status. Tanzanian customers, Tanzanian payments — this is a Tanzanian business.",
  "business_market", "adversarial"),

# --- GROUP 7: Interaction with other laws ---

p("b006_gn487a_031", "gn487a_adversarial",
  "Je, GN 487A ni sawa na Sheria ya Wahamiaji — ni sheria moja au mbili tofauti?",
  "Ni sheria mbili tofauti kabisa. Sheria ya Wahamiaji inasimamia haki ya kuishi na kufanya kazi Tanzania (vibali vya makazi na kazi). GN 487A inasimamia AINA za biashara zinazoruhusiwa au kukatazwa kwa raia wa kigeni. Mtu anaweza kuwa na kibali halali cha makazi na bado akikiuka GN 487A kwa kuendesha biashara iliyokatazwa.",
  "Is GN 487A the same as Immigration law — one law or two different ones?",
  "They are two completely different laws. Immigration law governs the right to live and work in Tanzania (residence and work permits). GN 487A governs the TYPES of businesses non-citizens are permitted or prohibited to operate. A person can have a valid residence permit and still violate GN 487A by operating a prohibited business.",
  "formal", "disambiguation"),

p("b006_gn487a_032", "gn487a_adversarial",
  "Usajili wa BRELA unalinda dhidi ya GN 487A — kweli au uongo?",
  "Uongo. Usajili wa BRELA ni hitaji la msingi la kisheria kwa biashara yoyote, lakini haumruhusu mwenye hisa mgeni kufanya biashara yoyote iliyokatazwa. GN 487A inabaki kuzuia shughuli 15 bila kujali hali ya usajili wa BRELA. Hata ukisajili kampuni yako vizuri BRELA, bado huwezi kuendesha duka la rejareja kama mgeni.",
  "Does BRELA registration protect against GN 487A — true or false?",
  "False. BRELA registration is a basic legal requirement for any business, but does not allow a foreign shareholder to conduct any prohibited activity. GN 487A still blocks the 15 activities regardless of BRELA registration status. Even if you register your company properly with BRELA, you still cannot run a retail shop as a non-citizen.",
  "business_market", "adversarial"),

p("b006_gn487a_033", "gn487a_adversarial",
  "TIC Certificate ya uwekezaji inalinda dhidi ya GN 487A?",
  "TIC Certificate inatoa haki na vivutio kwa wawekezaji — lakini haifuti GN 487A. Ikiwa biashara ya TIC inaingia kwenye mojawapo ya shughuli 15 za GN 487A, lazima izingatie kanuni zote mbili. TIC na GN 487A ni mifumo miwili tofauti inayofanya kazi pamoja. Thibitisha na TIC na mwanasheria.",
  "Does a TIC Investment Certificate protect against GN 487A?",
  "A TIC Certificate provides rights and incentives for investors — but it does not override GN 487A. If a TIC business engages in one of the 15 GN 487A activities, it must comply with both sets of rules. TIC and GN 487A are two separate systems that operate in parallel. Verify with TIC and a lawyer.",
  "formal", "disambiguation"),

p("b006_gn487a_034", "gn487a_adversarial",
  "GN 487A na GN 605A — ni amri zinazohusiana au tofauti kabisa?",
  "Ni amri mbili tofauti kabisa. GN 487A (28 Julai 2025): inazuia raia wa kigeni kufanya aina fulani za biashara. GN 605A (1 Januari 2026): inaweka mshahara wa chini kwa sekta mbalimbali — inaathiri waajiri WOTE, wakiwemo raia na wageni. Hazihusiani moja kwa moja.",
  "GN 487A and GN 605A — are they related orders or completely different?",
  "They are two completely different orders. GN 487A (28 July 2025): prohibits non-citizens from engaging in certain business activities. GN 605A (1 January 2026): sets minimum wages across various sectors — affecting ALL employers, both citizens and non-citizens. They have no direct connection.",
  "business_market", "disambiguation"),

p("b006_gn487a_035", "gn487a_adversarial",
  "Je, TRA inaweza kutekeleza GN 487A wakati wa ukaguzi wa kodi?",
  "TRA inashughulikia masuala ya kodi — si utekelezaji wa amri za leseni za biashara kama GN 487A. Utekelezaji wa GN 487A ni kazi ya Idara ya Uhamiaji. Wakati wa ukaguzi wa kodi, TRA inaweza RIPOTI tuhuma kwa Uhamiaji, lakini hana mamlaka ya kutekeleza GN 487A wenyewe.",
  "Can TRA enforce GN 487A during a tax audit?",
  "TRA handles tax matters — not enforcement of business licensing orders like GN 487A. GN 487A enforcement is the responsibility of the Immigration Services Department. During a tax audit, TRA may REFER suspicions to Immigration, but TRA does not have authority to enforce GN 487A independently.",
  "business_market", "adversarial",
  SRC_IM, NAME_IM, "government_portal"),

# --- GROUP 8: Existing businesses, transition, compliance ---

p("b006_gn487a_036", "gn487a_adversarial",
  "Mgeni alikuwa na duka tangu 2020 — biashara yake ya zamani inalindwa dhidi ya GN 487A?",
  "Hapana. GN 487A ya 2025 inatumika kwa biashara zote — za zamani NA mpya. Hakuna msamaha kwa biashara zilizoanzishwa kabla ya tarehe ya kuanza (28 Julai 2025). Mgeni aliyekuwa na duka la rejareja kabla ya tarehe hiyo bado lazima atii GN 487A — ama ahamishie kwa raia wa Tanzania au akabiliane na adhabu.",
  "A non-citizen had a shop since 2020 — is their existing business protected from GN 487A?",
  "No. GN 487A of 2025 applies to all businesses — existing AND new. There is no exemption for businesses established before the effective date (28 July 2025). A non-citizen who had a retail shop before that date must still comply with GN 487A — either transfer it to a Tanzanian citizen or face penalties.",
  "business_market", "adversarial"),

p("b006_gn487a_037", "gn487a_adversarial",
  "GN 487A ilitoa muda wa mpito rasmi kwa wageni walio na biashara zilizotangulia?",
  "GN 487A haikutoa muda mrefu wa mpito rasmi. Amri ilianza kutumika 28 Julai 2025 na ilikuwa ya lazima tangu tarehe hiyo. Zoezi la utekelezaji la Septemba–Oktoba 2025 lilikuwa kampeni maalum — si mwanzo wa uhalali wa amri. Ukiukaji wowote kuanzia 28 Julai 2025 ungeweza kusababisha adhabu.",
  "Did GN 487A provide a formal transition period for non-citizens with pre-existing businesses?",
  "GN 487A did not provide a long formal transition period. The order took effect on 28 July 2025 and was mandatory from that date. The September–October 2025 enforcement exercise was a specific campaign — not the start of the order's legal validity. Any violation from 28 July 2025 onward could result in penalties.",
  "formal", "adversarial"),

p("b006_gn487a_038", "gn487a_adversarial",
  "Leseni ya halmashauri (LGA) iliyotolewa 2024 inalinda mgeni dhidi ya GN 487A?",
  "Hapana. Leseni za halmashauri zinahusu kufuata kanuni za biashara za eneo — si uraia wa mmiliki. GN 487A ni amri ya kitaifa inayozidi leseni za halmashauri. Hata leseni kamili ya 2024 hailindi mgeni dhidi ya GN 487A baada ya 28 Julai 2025.",
  "Does an LGA business licence issued in 2024 protect a non-citizen from GN 487A?",
  "No. LGA licences address local business compliance — not the owner's citizenship. GN 487A is a national order that supersedes LGA licences. Even a complete 2024 licence does not protect a non-citizen from GN 487A after 28 July 2025.",
  "business_market", "adversarial"),

p("b006_gn487a_039", "gn487a_adversarial",
  "Mgeni anayefanya biashara iliyokatazwa anapaswa kufanya nini sasa hivi?",
  "Mgeni anapaswa: (1) Kuacha uendeshaji wa moja kwa moja wa biashara iliyokatazwa haraka iwezekanavyo. (2) Kushauriana na mwanasheria wa biashara kuhusu chaguzi za kisheria — ikiwemo kuhamisha biashara kwa raia wa Tanzania au kufunga kabisa. (3) Kuhakikisha kampuni au biashara inasajiliwa vizuri chini ya mmiliki raia wa Tanzania. Kuendelea bila kuchukua hatua ni hatari kubwa.",
  "What should a non-citizen currently operating a prohibited business do right now?",
  "The non-citizen should: (1) Immediately stop directly operating the prohibited business as soon as possible. (2) Consult a business lawyer about legal options — including transferring the business to a Tanzanian citizen or closing entirely. (3) Ensure the company or business is properly registered under a Tanzanian citizen owner. Continuing without action carries significant risk.",
  "business_market", "standard",
  SRC_IM, NAME_IM, "government_portal"),

p("b006_gn487a_040", "gn487a_adversarial",
  "Naona mgeni ana biashara iliyokatazwa — naridhika nani?",
  "Ripoti Idara ya Uhamiaji iliyo karibu nawe au ofisi ya Mkurugenzi wa Wilaya (DC). Unaweza pia kuwasiliana na Polisi. Usihatarisha usalama wako mwenyewe kwa kukabiliana na mtu mwenyewe — ripoti kwa mamlaka rasmi badala yake.",
  "I see a non-citizen with a prohibited business — who do I report to?",
  "Report to the nearest Immigration Services Department office or the District Commissioner's (DC) office. You may also contact the Police. Do not put yourself at risk by confronting the person directly — report to official authorities instead.",
  "rural_conversational", "standard",
  SRC_IM, NAME_IM, "government_portal"),

# --- GROUP 9: Disambiguation with related activities ---

p("b006_gn487a_041", "gn487a_adversarial",
  "Mshauri (consultant) mgeni anayesaidia biashara ya Mtanzania — ni ukiukaji wa GN 487A?",
  "GN 487A inakataza KUMILIKI na KUENDESHA biashara — si kutoa ushauri (consulting). Mshauri mgeni mwenye kibali cha kazi kinachofaa anaweza kutoa ushauri wa kibiashara bila kukiuka GN 487A. Tatizo linatokea tu 'ushauri' unapogeuka kuwa uendeshaji wa biashara moja kwa moja.",
  "A foreign consultant helping a Tanzanian business — is this a GN 487A violation?",
  "GN 487A prohibits OWNING and OPERATING businesses — not providing consultancy. A foreign consultant with an appropriate work permit can provide business advice without violating GN 487A. The problem only arises if 'consulting' turns into directly operating the business.",
  "formal", "disambiguation"),

p("b006_gn487a_042", "gn487a_adversarial",
  "Mgeni anaweza kumiliki hisa za kampuni ya rejareja Tanzania?",
  "Umiliki wa hisa peke yake si sawa na kuendesha biashara. Hata hivyo, GN 487A inazuia raia wa kigeni KUFANYA biashara za orodha ya 15. Ikiwa umiliki wa hisa unakupelekea udhibiti wa uendeshaji wa biashara ya rejareja, hii inaweza kukiuka roho ya GN 487A. Muundo wa kisheria unaofaa unahitajika — thibitisha na mwanasheria.",
  "Can a non-citizen own shares in a Tanzanian retail company?",
  "Owning shares alone is not the same as operating a business. However, GN 487A prohibits non-citizens from ENGAGING IN businesses on the list of 15. If share ownership leads to operational control of a retail business, this may violate the spirit of GN 487A. Appropriate legal structuring is needed — verify with a lawyer.",
  "formal", "disambiguation"),

p("b006_gn487a_043", "gn487a_adversarial",
  "Biashara ya kilimo kubwa — GN 487A inazuia mgeni kulima kwa faida?",
  "Kilimo kwa ujumla hakiko kwenye orodha ya shughuli 15 zilizokatazwa na GN 487A. Hata hivyo, uuzaji wa rejareja wa mazao unaweza kuathiriwa ikiwa unachukuliwa kama biashara ya rejareja. Kwa uwekezaji mkubwa wa kilimo, makubaliano na TIC yanaweza kuhitajika. Thibitisha na mwanasheria.",
  "Large-scale agriculture — does GN 487A prevent a non-citizen from farming commercially?",
  "Agriculture in general is not on the list of 15 prohibited activities under GN 487A. However, retail sale of farm produce could be affected if treated as retail trade. For large agricultural investments, agreements with TIC may be required. Verify with a lawyer.",
  "formal", "standard"),

p("b006_gn487a_044", "gn487a_adversarial",
  "Mgeni anafundisha darasa lake la lugha ya Kiingereza — GN 487A inasimamia?",
  "Huduma za elimu na mafunzo hazipo kwenye orodha ya 15 ya GN 487A. Mgeni anayeendesha shule ya lugha au darasa la binafsi hana vizuizi vya GN 487A. Hata hivyo, bado anahitaji kibali cha kazi kinachofaa kufundisha Tanzania.",
  "A non-citizen teaches their own English language class — does GN 487A apply?",
  "Education and training services are not on GN 487A's list of 15 prohibited activities. A non-citizen running a language school or private tutoring class faces no GN 487A restrictions. However, they still need an appropriate work permit to teach in Tanzania.",
  "business_market", "standard"),

p("b006_gn487a_045", "gn487a_adversarial",
  "Mabenki ya kimataifa yanayofanya kazi Tanzania yako chini ya GN 487A?",
  "Hapana. Taasisi za fedha (mabenki, makampuni ya bima) zinasimamia chini ya sheria maalum za sekta ya fedha na Bank of Tanzania (BoT). GN 487A inalenga biashara ndogo na za kati za kila siku — si taasisi za fedha zenye leseni rasmi za BoT au TIRA.",
  "Do international banks operating in Tanzania fall under GN 487A?",
  "No. Financial institutions (banks, insurance companies) are regulated under specific financial sector laws and the Bank of Tanzania (BoT). GN 487A targets everyday small and medium businesses — not financial institutions with formal BoT or TIRA licences.",
  "formal", "standard"),

# --- GROUP 10: Out-of-corpus refusals ---

p("b006_gn487a_046", "gn487a_adversarial",
  "Je, GN 487A inatumika Zanzibar pia?",
  "Sina uhakika. Sheria za Serikali ya Muungano na Serikali ya Mapinduzi Zanzibar (SMZ) zina mipaka tofauti — biashara nyingi za ndani ni suala la SMZ peke yake. Thibitisha na Ofisi ya Msajili wa Biashara Zanzibar au mwanasheria anayejua sheria za Zanzibar.",
  "Does GN 487A also apply in Zanzibar?",
  "I am not certain. Laws of the Union Government and the Revolutionary Government of Zanzibar (RGZ) have different jurisdictions — many internal business matters fall solely under RGZ. Verify with the Zanzibar Business Registrar's Office or a lawyer familiar with Zanzibar law.",
  "formal", "out_of_corpus_refusal"),

p("b006_gn487a_047", "gn487a_adversarial",
  "Daktari mgeni anayeendesha kliniki binafsi — GN 487A inakataza?",
  "Huduma za afya hazipo kwenye orodha ya 15 ya GN 487A. Daktari mgeni bado anahitaji usajili wa Baraza la Madaktari na Wauguzi Tanzania (MCDT) na kibali cha kazi. Sina uhakika wa masharti yote maalum. Thibitisha na MCDT na Idara ya Uhamiaji.",
  "A foreign doctor running a private clinic — does GN 487A prohibit this?",
  "Health services are not on GN 487A's list of 15 activities. A foreign doctor still needs registration with the Medical Council of Tanganyika (MCDT) and a work permit. I am not certain of all specific requirements. Verify with MCDT and the Immigration Services Department.",
  "formal", "out_of_corpus_refusal"),

p("b006_gn487a_048", "gn487a_adversarial",
  "Je, kuna adhabu kali zaidi kwa mgeni anayekiuka GN 487A mara ya pili?",
  "Sina uhakika wa masharti maalum ya marudio ya makosa (recidivism) ndani ya GN 487A. Amri inaeleza adhabu za msingi: TZS 10M na hadi miezi 6 gerezani. Kwa hali ya ukiukaji wa mara ya pili, thibitisha na mwanasheria au Idara ya Uhamiaji.",
  "Are there enhanced penalties for a non-citizen violating GN 487A a second time?",
  "I am not certain of specific recidivism provisions within GN 487A. The order specifies basic penalties: TZS 10M and up to 6 months imprisonment. For the specific situation of a second violation, verify with a lawyer or the Immigration Services Department.",
  "formal", "out_of_corpus_refusal"),

# --- GROUP 11: Final adversarial (catching multi-error base model output) ---

p("b006_gn487a_049", "gn487a_adversarial",
  "Mtu anasema: 'GN 487A inalenga Wachina peke yake, ilitangazwa 2024, na adhabu ni TZS 500,000.' Sahihi?",
  "Hapana — kila sehemu ni kosa. GN 487A: (1) inatumika kwa raia WOTE wa kigeni — si Wachina peke yake; (2) ilitangazwa 28 Julai 2025 — si 2024; (3) faini ya chini ni TZS 10,000,000 — si TZS 500,000. Habari hizi tatu ni potofu kabisa.",
  "Someone says: 'GN 487A targets only Chinese, was announced in 2024, and the fine is TZS 500,000.' Correct?",
  "No — every part is wrong. GN 487A: (1) applies to ALL non-citizens — not only Chinese people; (2) was announced 28 July 2025 — not 2024; (3) the minimum fine is TZS 10,000,000 — not TZS 500,000. All three pieces of information are completely false.",
  "business_market", "adversarial"),

p("b006_gn487a_050", "gn487a_adversarial",
  "Muhtasari: GN 487A inamaanisha nini kwa mfanyabiashara mgeni Tanzania?",
  "GN 487A (28 Julai 2025) inamaanisha: (1) Shughuli 15 zimefungwa kwa umiliki na uendeshaji wa raia wa kigeni — biashara ya jumla, rejareja, mobile money, salon, ukarabati wa simu na nyingine. (2) Ukikiuka: faini ya angalau TZS 10M, hadi miezi 6 gerezani, visa inafutwa. (3) Mtanzania anayekusaidia kukiuka: faini ya TZS 5M au miezi 3. (4) Utekelezaji: Idara ya Uhamiaji. (5) Kigezo: uraia — si muda wa makazi, si utaifa, si leseni ya zamani.",
  "Summary: what does GN 487A mean for a non-citizen business operator in Tanzania?",
  "GN 487A (28 July 2025) means: (1) 15 activities are closed to ownership and operation by non-citizens — wholesale, retail, mobile money, salon, phone repair and others. (2) If you violate: minimum TZS 10M fine, up to 6 months imprisonment, visa revoked. (3) Tanzanian who helps you violate: TZS 5M fine or 3 months. (4) Enforcement: Immigration Services Department. (5) Criterion: citizenship — not length of residence, not nationality, not a prior licence.",
  "formal", "standard"),

]

# Append to JSONL
os.makedirs(os.path.dirname(OUT), exist_ok=True)
written = 0
with open(OUT, "a", encoding="utf-8") as f:
    for pair in pairs:
        f.write(json.dumps(pair, ensure_ascii=False) + "\n")
        written += 1

print(f"Wrote {written} pairs to {OUT}")

# Count by register and pair_type
from collections import Counter
regs = Counter(p_["register"] for p_ in pairs)
ptypes = Counter(p_["pair_type"] for p_ in pairs)
print("Register distribution:", dict(regs))
print("Pair type distribution:", dict(ptypes))
