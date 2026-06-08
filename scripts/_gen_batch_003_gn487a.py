#!/usr/bin/env python3
"""Generate first 50 pairs of batch_003 — GN487A adversarial."""
import json, os

OUT = "datasets/tier1a/raw_sources/raw_pairs_batch_003.jsonl"
SOURCE_URL = "https://tanzlii.org/akn/tz/act/gn/2025/487a/eng@2025-07-28"
SOURCE_NAME = "GN 487A — Business Licensing (Prohibition of Business Activities for Non-Citizens) Order 2025"

PAIRS = [
# ─────────────────────────────────────────────────────────────
# BLOCK 1: GN487A identity — adversarial against "residence permit" confusion
# ─────────────────────────────────────────────────────────────
{
"id": "tier1a_gn487a_001_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "GN 487A ya mwaka 2025 inazungumzia nini hasa?",
"answer_sw": "GN 487A (Government Notice 487A, 2025) ni Amri ya Leseni za Biashara inayozuia wageni kufanya shughuli fulani za biashara nchini Tanzania — inaitwa rasmi 'Business Licensing (Prohibition of Business Activities for Non-Citizens) Order 2025'. Amri hii HAIHUSU vibali vya makazi wala vibali vya kazi. Inazuia watu wasio raia wa Tanzania kufanya biashara katika makundi 15 maalum, kuanzia tarehe 28 Julai 2025. Adhabu ni faini ya angalau TZS milioni 10, pamoja na kifungo cha hadi miezi 6 na kufutwa kwa viza.",
"question_en": "What exactly does GN 487A of 2025 cover?",
"answer_en": "GN 487A (Government Notice 487A, 2025) is a Business Licensing Order that prohibits non-citizens from conducting certain business activities in Tanzania — its full name is the 'Business Licensing (Prohibition of Business Activities for Non-Citizens) Order 2025'. This Order is NOT about residence permits or work permits. It prohibits non-Tanzanian nationals from operating in 15 specific business categories, effective 28 July 2025. Penalties are a minimum TZS 10 million fine plus up to 6 months imprisonment and visa revocation.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_002_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Rafiki yangu mgeni alisema lazima aombe 'kibali cha makazi' kwa sababu ya GN 487A — hii ni kweli?",
"answer_sw": "Hapana, hii si kweli. GN 487A haihusu vibali vya makazi (residence permits). GN 487A ni amri inayozuia wageni kufanya shughuli za biashara katika makundi 15 maalum — kama vile biashara ya rejareja, uhamisho wa pesa kwa simu, ukarabati wa simu, na saluni. Vibali vya makazi vya Tanzania vinasimamiwa na Sheria ya Uhamiaji, si GN 487A. Kama rafiki yako mgeni anataka kufanya biashara katika makundi haya 15, hataweza kwa chini ya GN 487A — hata kama ana kibali cha makazi. Rafiki yako amshauri azungumze na wakili wa uhamiaji.",
"question_en": "My foreign friend was told he must apply for a 'residence permit' because of GN 487A — is this true?",
"answer_en": "No, this is not true. GN 487A does not concern residence permits. GN 487A is an order that prohibits non-citizens from conducting business in 15 specific categories — such as retail trade, mobile money transfers, phone repair, and salons. Tanzania residence permits are governed by the Immigration Act, not GN 487A. Even if your friend has a residence permit, he still cannot operate in those 15 business categories under GN 487A. Advise your friend to consult an immigration lawyer.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "business_market", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_003_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "GN 487A inazuia wageni wafanye kazi Tanzania — hii ni sahihi?",
"answer_sw": "Si sahihi kamili. GN 487A inazuia wageni KUMILIKI au KUENDESHA biashara katika makundi 15 maalum — si kufanya kazi kwa ujumla. Wageni wanaweza bado kufanya kazi kama wafanyakazi wa kampuni kwa vibali vya kazi sahihi. Amri inalenga watu binafsi wasio raia wanaoendesha biashara zao wenyewe katika makundi yaliyozuiliwa, kama vile maduka ya rejareja, saluni, ukarabati wa simu, au uhamisho wa pesa. Vibali vya kazi kwa wafanyakazi wa kampuni ni suala tofauti linaloshughulikiwa na Sheria ya Ajira.",
"question_en": "GN 487A bans foreigners from working in Tanzania — is this correct?",
"answer_en": "Not entirely correct. GN 487A prohibits non-citizens from OWNING or OPERATING businesses in 15 specific categories — not from working in general. Foreigners can still work as employees with valid work permits. The Order targets individual non-citizens running their own businesses in the prohibited categories, such as retail shops, salons, phone repair, or mobile money. Work permits for company employees are a separate matter governed by Employment Law.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_004_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Je, GN 487A ni sawa na visa restriction au kikwazo cha uingiaji nchini?",
"answer_sw": "Hapana. GN 487A si kikwazo cha uingiaji nchini (visa restriction). Ni amri ya LESENI ZA BIASHARA inayozuia watu wasio raia kufanya biashara katika sekta 15 zilizoorodheshwa. Mgeni anaweza kuingia Tanzania kwa viza ya kawaida ya utalii au biashara — GN 487A haitazuia uingiaji wake. Lakini akifanya biashara iliyozuiliwa (kama kufungua duka la rejareja au saluni) akiwa ndani ya Tanzania, atapata adhabu ya faini ya TZS milioni 10 au zaidi, kifungo cha hadi miezi 6, na kufutwa kwa viza yake.",
"question_en": "Is GN 487A the same as a visa restriction or entry ban?",
"answer_en": "No. GN 487A is not an entry ban or visa restriction. It is a BUSINESS LICENSING ORDER that prohibits non-citizens from operating businesses in 15 listed sectors. A foreigner can still enter Tanzania on a normal tourist or business visa — GN 487A does not block entry. However, if they operate a prohibited business (such as opening a retail shop or salon) while inside Tanzania, they face a minimum TZS 10 million fine, up to 6 months imprisonment, and visa revocation.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_005_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Mgeni anafanya biashara Tanzania — anahitaji nini chini ya GN 487A?",
"answer_sw": "Chini ya GN 487A (2025), mgeni hawezi kufanya biashara katika makundi 15 yaliyozuiliwa hata akiwa na vibali vyote vya biashara na makazi. Makundi yaliyozuiliwa yanajumuisha: biashara ya jumla na rejareja, huduma za uhamisho wa pesa kwa simu, ukarabati wa simu, saluni na kinyozi, ubadilishaji wa fedha za kigeni, uendeshaji wa kituo cha mafuta, huduma za madalali, na mengine. Kama mgeni anataka kufanya biashara nchini Tanzania, lazima afanye kwa njia ya ubia na raia wa Tanzania au kufanya biashara katika sekta ambazo hazijazuiliwa. Mshauri wa kisheria ni muhimu.",
"question_en": "A foreigner wants to do business in Tanzania — what do they need under GN 487A?",
"answer_en": "Under GN 487A (2025), a non-citizen cannot operate businesses in the 15 prohibited categories even with all valid business and residence permits. Prohibited categories include: wholesale and retail trade, mobile money transfer services, phone repair, salons and barbershops, forex bureaus, petrol station operations, brokerage services, and others. If a non-citizen wants to do business in Tanzania, they must do so through a partnership with a Tanzanian citizen or operate in non-restricted sectors. Legal advice is essential.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "business_market", "pair_type": "adversarial", "eval_set": False
},
# ─────────────────────────────────────────────────────────────
# BLOCK 2: Mobile money transfers — prohibited activity
# ─────────────────────────────────────────────────────────────
{
"id": "tier1a_gn487a_006_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Mtu asiye raia wa Tanzania anaweza kuwa wakala wa M-Pesa au Airtel Money?",
"answer_sw": "Hapana. Chini ya GN 487A (2025), huduma za uhamisho wa pesa kwa simu (mobile money agent services) ni moja ya shughuli 15 zilizozuiliwa kwa watu wasio raia wa Tanzania. Mtu asiye raia hawezi kuwa wakala wa M-Pesa, Airtel Money, Tigo Pesa, au mtandao wowote wa pesa za simu kama biashara yake binafsi. Adhabu kwa ukiukwaji ni faini ya angalau TZS milioni 10 na kifungo cha hadi miezi 6 jela, pamoja na kufutwa kwa viza. Raia wa Tanzania wanaofanya uwezeshaji wanahatarisha faini ya TZS milioni 5 au kifungo cha miezi 3.",
"question_en": "Can a non-Tanzanian citizen become an M-Pesa or Airtel Money agent?",
"answer_en": "No. Under GN 487A (2025), mobile money transfer agent services are one of the 15 business activities prohibited for non-citizens. A non-citizen cannot operate as an M-Pesa, Airtel Money, Tigo Pesa, or any mobile money network agent as their own business. Penalties for violation are a minimum TZS 10 million fine and up to 6 months imprisonment, plus visa revocation. Tanzanian citizens who facilitate such arrangements risk a TZS 5 million fine or 3 months imprisonment.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "business_market", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_007_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Kijiji chetu kina mtu kutoka Kenya anayeendesha wakala wa pesa za simu — je, hii ni halali?",
"answer_sw": "Hapana, si halali chini ya GN 487A (2025). Raia wa Kenya au nchi nyingine yoyote ambaye si raia wa Tanzania hawezi kuendesha biashara ya wakala wa pesa za simu (mobile money agent) nchini Tanzania. Hii ni moja ya shughuli 15 zilizozuiliwa rasmi. Adhabu kwa mtu huyu ni faini ya angalau TZS milioni 10 na kifungo cha hadi miezi 6, pamoja na kufutwa kwa viza yake. Raia wa Tanzania yeyote aliyemwezesha (kama kusimamia au kushiriki) anaweza kupata faini ya TZS milioni 5 au kifungo cha miezi 3. Ni vyema kuwasiliana na Idara ya Uhamiaji au polisi wa biashara.",
"question_en": "Our village has a person from Kenya running a mobile money agent — is this legal?",
"answer_en": "No, it is not legal under GN 487A (2025). A Kenyan national or any non-Tanzanian citizen cannot operate a mobile money agent business in Tanzania. This is one of the 15 officially prohibited activities. Penalties for that person are a minimum TZS 10 million fine and up to 6 months imprisonment, plus visa revocation. Any Tanzanian citizen who facilitated (such as supervising or partnering) faces a TZS 5 million fine or 3 months imprisonment. It is advisable to contact the Immigration Department or business police.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "rural_conversational", "pair_type": "adversarial", "eval_set": False
},
# ─────────────────────────────────────────────────────────────
# BLOCK 3: Phone repair — prohibited activity
# ─────────────────────────────────────────────────────────────
{
"id": "tier1a_gn487a_008_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Ninataka kufungua duka la kutengeneza simu — mimi ni raia wa China. Je, GN 487A inaniathiri?",
"answer_sw": "Ndiyo, GN 487A inakuathiri moja kwa moja. Ukarabati na matengenezo ya simu za mkononi (phone repair/maintenance) ni moja ya shughuli 15 zilizozuiliwa kwa watu wasio raia wa Tanzania, kuanzia tarehe 28 Julai 2025. Kama raia wa China, huwezi kumiliki au kuendesha duka la kutengeneza simu nchini Tanzania. Ukivunja amri hii, utakabiliwa na faini ya angalau TZS milioni 10, kifungo cha hadi miezi 6 jela, na kufutwa kwa viza yako. Unaweza kuzungumza na wakili kuhusu njia nyingine za kisheria za kuwekeza Tanzania, kama ubia na raia wa Tanzania.",
"question_en": "I want to open a phone repair shop — I am a Chinese national. Does GN 487A affect me?",
"answer_en": "Yes, GN 487A directly affects you. Mobile phone repair and maintenance is one of the 15 business activities prohibited for non-Tanzanian citizens, effective 28 July 2025. As a Chinese national, you cannot own or operate a phone repair shop in Tanzania. If you violate this Order, you face a minimum TZS 10 million fine, up to 6 months imprisonment, and visa revocation. You may consult a lawyer about other legal investment options in Tanzania, such as a partnership with a Tanzanian citizen.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "business_market", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_009_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Mwenzangu mgeni ana duka la kutengeneza simu tangu mwaka 2020 — je, bado anaweza kuendelea?",
"answer_sw": "Hapana. GN 487A (inayofanya kazi kuanzia 28 Julai 2025) hairuhusu istisna kwa biashara zilizokuwepo kabla ya amri. Ukarabati wa simu ni kati ya shughuli 15 zilizozuiliwa kwa watu wasio raia. Mwenzako lazima asimamishe shughuli hiyo au ahamishie umiliki kwa raia wa Tanzania. Kuendelea kufanya biashara hii kama mgeni baada ya 28 Julai 2025 ni kuvunja sheria, na adhabu ni faini ya TZS milioni 10 au zaidi, kifungo cha hadi miezi 6, na kufutwa kwa viza. Anashauriwa kupata ushauri wa kisheria haraka iwezekanavyo.",
"question_en": "My foreign colleague has had a phone repair shop since 2020 — can he continue?",
"answer_en": "No. GN 487A (effective 28 July 2025) makes no exception for businesses that existed before the Order. Phone repair is among the 15 activities prohibited for non-citizens. Your colleague must cease that activity or transfer ownership to a Tanzanian citizen. Continuing this business as a non-citizen after 28 July 2025 is a violation, and penalties are a TZS 10 million or more fine, up to 6 months imprisonment, and visa revocation. He is advised to seek legal advice as soon as possible.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "business_market", "pair_type": "adversarial", "eval_set": False
},
# ─────────────────────────────────────────────────────────────
# BLOCK 4: Salon / beauty services — prohibited
# ─────────────────────────────────────────────────────────────
{
"id": "tier1a_gn487a_010_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Mke wangu ni raia wa Ethiopia, anataka kufungua saluni Dar es Salaam — je, anaweza?",
"answer_sw": "Hapana. Chini ya GN 487A (2025), huduma za saluni, kinyozi, na urembo ni moja ya shughuli 15 zilizozuiliwa kwa watu wasio raia wa Tanzania. Mke wako hawezi kumiliki wala kuendesha saluni kama biashara yake binafsi. Adhabu ni faini ya angalau TZS milioni 10, kifungo cha hadi miezi 6, na kufutwa kwa viza yake. Unaweza fikiria chaguo la ubia ambapo raia wa Tanzania ndiye mmiliki rasmi, lakini hata hivyo mhusika anapaswa kupata ushauri wa kisheria kwanza ili kuhakikisha muundo wa ubia ni halali.",
"question_en": "My wife is an Ethiopian citizen and wants to open a salon in Dar es Salaam — can she?",
"answer_en": "No. Under GN 487A (2025), salon, barbershop, and beauty services are one of the 15 business activities prohibited for non-Tanzanian citizens. Your wife cannot own or operate a salon as her own business. Penalties are a minimum TZS 10 million fine, up to 6 months imprisonment, and visa revocation. You may consider a partnership arrangement where a Tanzanian citizen is the registered owner, but even then she should seek legal advice first to ensure the partnership structure is lawful.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "business_market", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_011_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Kinyozi kutoka Uganda anafanya kazi katika saluni yangu — je, hii ni tatizo?",
"answer_sw": "Inategemea. GN 487A inazuia watu wasio raia KUMILIKI na KUENDESHA saluni — si kufanya kazi kama mfanyakazi wa saluni. Kama huyu kinyozi ni mfanyakazi wako na wewe (raia wa Tanzania) ndiye mmiliki wa saluni, hiyo inaweza kuwa sawa kwa upande wa GN 487A, lakini lazima awe na kibali sahihi cha kufanya kazi (work permit) kutoka Wizara ya Kazi. Kama yeye mwenyewe ndiye mmiliki wa saluni au anafanya kazi bila kibali cha kazi, basi kuna tatizo la kisheria. Thibitisha hali yake ya kisheria na ushauri wa wakili au Idara ya Kazi.",
"question_en": "A Ugandan barber works in my salon — is this a problem?",
"answer_en": "It depends. GN 487A prohibits non-citizens from OWNING and OPERATING a salon — not from working as an employee. If this barber is your employee and you (a Tanzanian citizen) are the salon owner, that may be fine under GN 487A, but he must have a valid work permit from the Ministry of Labour. If he himself is the salon owner, or is working without a work permit, then there is a legal problem. Verify his legal status with a lawyer or the Labour Department.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "business_market", "pair_type": "adversarial", "eval_set": False
},
# ─────────────────────────────────────────────────────────────
# BLOCK 5: Retail & wholesale trade — prohibited
# ─────────────────────────────────────────────────────────────
{
"id": "tier1a_gn487a_012_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Muuzaji wa jumla kutoka India ana ghala la bidhaa Dar — je, GN 487A inamhusu?",
"answer_sw": "Ndiyo, GN 487A inamhusu moja kwa moja. Biashara ya jumla (wholesale trade) ni moja ya shughuli 15 zilizozuiliwa kwa watu wasio raia wa Tanzania, ikiwa ni pamoja na kuendesha ghala la bidhaa na kuuza kwa wingi. Muuzaji huyu kutoka India lazima asimamishe shughuli hii au ahamishie umiliki kwa raia wa Tanzania kwa njia inayokubalika kisheria. Kutofuata amri hii kunaweza kusababisha faini ya angalau TZS milioni 10, kifungo cha hadi miezi 6, na kufutwa kwa viza. Anashauriwa kupata ushauri wa kisheria haraka.",
"question_en": "A wholesale trader from India has a warehouse in Dar — does GN 487A apply to him?",
"answer_en": "Yes, GN 487A directly applies to him. Wholesale trade is one of the 15 business activities prohibited for non-Tanzanian citizens, including operating a product warehouse and selling in bulk. This trader from India must cease the activity or transfer ownership to a Tanzanian citizen through a legally compliant structure. Non-compliance may result in a minimum TZS 10 million fine, up to 6 months imprisonment, and visa revocation. He is advised to seek legal advice urgently.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_013_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Mtu wa nje ana duka la rejareja la chakula karibu na nyumba yangu — ni halali?",
"answer_sw": "Hapana. Biashara ya rejareja (retail trade), ikiwa ni pamoja na maduka ya chakula, ni moja ya shughuli 15 zilizozuiliwa kwa watu wasio raia wa Tanzania chini ya GN 487A (2025). Mtu huyu wa nje anakiuka amri hii na anaweza kupata adhabu ya faini ya TZS milioni 10 au zaidi pamoja na kifungo cha hadi miezi 6 na kufutwa kwa viza. Kama unataka kuripoti, unaweza kuwasiliana na Idara ya Uhamiaji au Ofisi ya Msajili wa Biashara (BRELA).",
"question_en": "A foreign national has a small retail food shop near my house — is this legal?",
"answer_en": "No. Retail trade, including food shops, is one of the 15 business activities prohibited for non-Tanzanian citizens under GN 487A (2025). This foreign national is violating the Order and may face a TZS 10 million or more fine, up to 6 months imprisonment, and visa revocation. If you want to report this, you can contact the Immigration Department or the Business Registrations and Licensing Agency (BRELA).",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "rural_conversational", "pair_type": "adversarial", "eval_set": False
},
# ─────────────────────────────────────────────────────────────
# BLOCK 6: Penalties — adversarial against wrong amounts / jail terms
# ─────────────────────────────────────────────────────────────
{
"id": "tier1a_gn487a_014_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Adhabu ya mgeni anayevunja GN 487A ni nini hasa?",
"answer_sw": "Adhabu rasmi kwa mtu asiye raia wa Tanzania anayevunja GN 487A ni: (1) Faini ya angalau TZS milioni 10 (shilingi milioni kumi), (2) Kifungo cha hadi miezi 6 jela (si zaidi ya miezi sita), na (3) Kufutwa kwa viza yake na kurushwa nje ya nchi. Adhabu hizi zinaweza kutolewa pamoja au moja kwa moja. Kumbuka: Faini ya TZS milioni 10 ni kiwango cha CHINI — mahakama inaweza kutoa faini kubwa zaidi. Vyanzo vilivyothibitishwa: Bowmans (30 Jul 2025), Dentons (29 Jul 2025), DLA Piper Africa.",
"question_en": "What exactly are the penalties for a foreigner violating GN 487A?",
"answer_en": "The official penalties for a non-Tanzanian citizen violating GN 487A are: (1) A minimum TZS 10 million fine, (2) Imprisonment for up to 6 months (not exceeding six months), and (3) Visa revocation and deportation. These penalties may be applied together or individually. Note: The TZS 10 million fine is the MINIMUM — courts may impose a higher amount. Verified sources: Bowmans (30 Jul 2025), Dentons (29 Jul 2025), DLA Piper Africa.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_015_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Sikia kwamba kifungo kwa mgeni anayevunja GN 487A ni miaka 1 — hii ni kweli?",
"answer_sw": "Hapana, hii si kweli. Kifungo cha juu kwa mgeni anayevunja GN 487A ni MIEZI 6 — si miaka 1 wala zaidi. GN 487A inasema wazi 'imprisonment for a term not exceeding six months' (kifungo kisichozidi miezi sita). Vyanzo vingi vya kisheria vilivyothibitishwa (Bowmans, Dentons, DLA Piper, VELMA Law) vyote vinapoeleza miezi 6 kama kiwango cha juu. Pamoja na kifungo, mgeni anaweza pia kupata faini ya angalau TZS milioni 10 na kufutwa kwa viza. Thibitisha taarifa za kisheria daima kwa vyanzo rasmi kama TanzLII.org.",
"question_en": "I heard that the imprisonment for a foreigner violating GN 487A is 1 year — is this true?",
"answer_en": "No, this is not true. The maximum imprisonment for a non-citizen violating GN 487A is 6 MONTHS — not 1 year or more. GN 487A clearly states 'imprisonment for a term not exceeding six months'. Multiple verified legal sources (Bowmans, Dentons, DLA Piper, VELMA Law) all report 6 months as the maximum. In addition to imprisonment, the non-citizen may also face a minimum TZS 10 million fine and visa revocation. Always verify legal information with authoritative sources like TanzLII.org.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "business_market", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_016_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Je, faini ya GN 487A kwa Mtanzania anayemsaidia mgeni ni kiasi gani?",
"answer_sw": "Raia wa Tanzania anayemsaidia mgeni kufanya biashara iliyozuiliwa chini ya GN 487A anakabiliwa na adhabu tofauti na mgeni mwenyewe. Adhabu ya Mtanzania ni: (1) Faini ya TZS milioni 5 (shilingi milioni tano), AU (2) Kifungo cha hadi miezi 3 jela. Hii inahusu Watanzania wanaomruhusu mgeni kutumia jina lao, leseni yao, au akaunti yao ya benki kufanya biashara iliyozuiliwa. Ni kosa kubwa la kisheria kufanya hivyo. Ikiwa mgeni alivunja sheria, Mtanzania aliyehusika anaweza pia kushitakiwa.",
"question_en": "What is the penalty for a Tanzanian who assists a foreigner under GN 487A?",
"answer_en": "A Tanzanian citizen who helps a non-citizen operate a prohibited business under GN 487A faces different penalties from the non-citizen. The Tanzanian's penalty is: (1) A TZS 5 million fine, OR (2) Imprisonment of up to 3 months. This applies to Tanzanians who allow foreigners to use their name, business licence, or bank account to operate a prohibited business. This is a serious legal offence. If the foreigner violated the law, the Tanzanian who assisted may also be prosecuted.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_017_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Nilisikia Mtanzania anayemsaidia mgeni anaweza kupata faini ya TZS milioni 10 — ni kweli?",
"answer_sw": "Hapana. Faini ya TZS milioni 10 ni kwa mgeni (mtu asiye raia) anayevunja GN 487A. Adhabu kwa RAIA WA TANZANIA anayemsaidia mgeni ni ndogo zaidi: faini ya TZS milioni 5 TU, au kifungo cha hadi miezi 3 jela. Kumbuka tofauti hii muhimu: mgeni → TZS milioni 10 + miezi 6 + kufutwa kwa viza; Mtanzania anayemsaidia → TZS milioni 5 au miezi 3. Hata hivyo, adhabu ya Mtanzania bado ni kubwa — TZS milioni 5 ni kiasi kikubwa kwa biashara ndogo ndogo.",
"question_en": "I heard a Tanzanian who helps a foreigner can get a TZS 10 million fine — is this true?",
"answer_en": "No. The TZS 10 million fine is for the non-citizen violating GN 487A. The penalty for a TANZANIAN CITIZEN who assists a non-citizen is lower: a TZS 5 million fine ONLY, or imprisonment of up to 3 months. Remember this important distinction: non-citizen → TZS 10M + 6 months + visa revocation; Tanzanian who assists → TZS 5M or 3 months. However, the Tanzanian's penalty is still significant — TZS 5 million is a large amount for small businesses.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "business_market", "pair_type": "adversarial", "eval_set": False
},
# ─────────────────────────────────────────────────────────────
# BLOCK 7: Forex bureau — prohibited
# ─────────────────────────────────────────────────────────────
{
"id": "tier1a_gn487a_018_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Raia wa kigeni anaweza kufungua bureau de change Tanzania?",
"answer_sw": "Hapana. Ubadilishaji wa fedha za kigeni (forex bureau / bureau de change) ni moja ya shughuli 15 zilizozuiliwa kwa watu wasio raia wa Tanzania chini ya GN 487A (2025). Hata kama mtu wa nje ana leseni ya BoT (Benki Kuu ya Tanzania) ya ubadilishaji wa fedha, hawezi kuwa mmiliki au meneja wa bureau de change kama biashara yake binafsi chini ya GN 487A. Adhabu ni faini ya angalau TZS milioni 10, kifungo cha hadi miezi 6, na kufutwa kwa viza.",
"question_en": "Can a foreign national open a bureau de change in Tanzania?",
"answer_en": "No. Forex bureau (bureau de change) operations are one of the 15 business activities prohibited for non-Tanzanian citizens under GN 487A (2025). Even if a foreigner has a BoT (Bank of Tanzania) licence for currency exchange, they cannot be the owner or operator of a bureau de change as their own business under GN 487A. Penalties are a minimum TZS 10 million fine, up to 6 months imprisonment, and visa revocation.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
# ─────────────────────────────────────────────────────────────
# BLOCK 8: Effective date & enforcement context
# ─────────────────────────────────────────────────────────────
{
"id": "tier1a_gn487a_019_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "GN 487A ilianza kutumika lini Tanzania?",
"answer_sw": "GN 487A — yaani Amri ya 'Business Licensing (Prohibition of Business Activities for Non-Citizens) Order 2025' — ilianza kutumika rasmi tarehe 28 Julai 2025. Amri hii ilisajiliwa (gazetted) na Serikali ya Tanzania na inaathiri wageni wote wanaofanya biashara katika makundi 15 yaliyoorodheshwa. Operesheni ya utekelezaji wa awali ilifanywa na Idara ya Uhamiaji kati ya 11 Septemba na 8 Oktoba 2025. Biashara zilizokuwepo kabla ya tarehe hii hazikupewa muda maalum wa kustaafu — amri ilianza mara moja.",
"question_en": "When did GN 487A come into effect in Tanzania?",
"answer_en": "GN 487A — the 'Business Licensing (Prohibition of Business Activities for Non-Citizens) Order 2025' — officially came into effect on 28 July 2025. The Order was gazetted by the Government of Tanzania and affects all non-citizens operating businesses in the 15 listed categories. The initial enforcement exercise was conducted by the Immigration Department between 11 September and 8 October 2025. Businesses that existed before this date were not given a specific wind-down period — the Order took immediate effect.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_020_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Ni wizara gani au idara gani inayotekeleza GN 487A?",
"answer_sw": "GN 487A inatekelezwa na Idara ya Uhamiaji (Immigration Services Department) chini ya Wizara inayohusiana na uhamiaji. Operesheni ya utekelezaji wa kwanza rasmi ilifanywa na Idara ya Uhamiaji kati ya tarehe 11 Septemba 2025 hadi 8 Oktoba 2025. Wakati wa operesheni hii, wageni waliokutwa wakifanya biashara zilizozuiliwa walifungiwa biashara na kushuguhuliwa kisheria. Pia BRELA (Business Registrations and Licensing Agency) inaweza kushiriki katika utekelezaji kwa upande wa leseni za biashara.",
"question_en": "Which ministry or department enforces GN 487A?",
"answer_en": "GN 487A is enforced by the Immigration Services Department under the relevant Ministry. The first official enforcement exercise was conducted by the Immigration Department between 11 September 2025 and 8 October 2025. During this exercise, non-citizens found operating prohibited businesses had their businesses closed and were dealt with legally. BRELA (Business Registrations and Licensing Agency) may also be involved in enforcement on the business licensing side.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
# ─────────────────────────────────────────────────────────────
# BLOCK 9: Clearing & forwarding, courier — prohibited
# ─────────────────────────────────────────────────────────────
{
"id": "tier1a_gn487a_021_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Kampuni ya usafirishaji na uwakala wa forodha (clearing and forwarding) inaweza kumilikiwa na mgeni?",
"answer_sw": "Hapana. Huduma za usafirishaji na uwakala wa forodha (clearing and forwarding) ni moja ya shughuli 15 zilizozuiliwa kwa watu wasio raia wa Tanzania chini ya GN 487A (2025). Mtu asiye raia hawezi kumiliki au kuendesha kampuni ya clearing and forwarding kama biashara yake binafsi nchini Tanzania. Adhabu ni faini ya angalau TZS milioni 10, kifungo cha hadi miezi 6, na kufutwa kwa viza. Kampuni kubwa za kimataifa za logistics zinazofanya kazi Tanzania lazima zizingatie muundo sahihi wa umiliki ili kutofuata GN 487A.",
"question_en": "Can a clearing and forwarding company be owned by a non-citizen?",
"answer_en": "No. Clearing and forwarding services are one of the 15 business activities prohibited for non-Tanzanian citizens under GN 487A (2025). A non-citizen cannot own or operate a clearing and forwarding company as their own business in Tanzania. Penalties are a minimum TZS 10 million fine, up to 6 months imprisonment, and visa revocation. Large international logistics companies operating in Tanzania must ensure their ownership structure complies with GN 487A.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_022_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Mgeni wangu anatoa huduma za uchukuzi wa haraka (courier) Tanzania — je, anahitaji kibali gani?",
"answer_sw": "Chini ya GN 487A (2025), huduma za uchukuzi wa haraka (courier services) ni moja ya shughuli 15 zilizozuiliwa kwa watu wasio raia wa Tanzania. Hakuna kibali kitakachomruhusu mgeni kuendesha biashara hii kama biashara yake binafsi — GN 487A inakataza umiliki wenyewe katika sekta hii. Mgeni wako lazima asimamishe shughuli hii. Anaweza kufikiria ubia (joint venture) na raia wa Tanzania ambapo Mtanzania ndiye mmiliki mkuu, lakini muundo huo unahitaji ushauri wa kisheria ili uhakikishe unakubaliana na GN 487A na sheria nyingine.",
"question_en": "My foreign associate provides courier services in Tanzania — what permit does he need?",
"answer_en": "Under GN 487A (2025), courier services are one of the 15 business activities prohibited for non-Tanzanian citizens. No permit will allow a non-citizen to operate this business as their own — GN 487A prohibits ownership itself in this sector. Your associate must cease this activity. He may consider a joint venture with a Tanzanian citizen where the Tanzanian is the primary owner, but that structure requires legal advice to ensure compliance with GN 487A and other laws.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "business_market", "pair_type": "adversarial", "eval_set": False
},
# ─────────────────────────────────────────────────────────────
# BLOCK 10: Petrol stations, flour milling — prohibited
# ─────────────────────────────────────────────────────────────
{
"id": "tier1a_gn487a_023_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Kama mgeni ninataka kufungua kituo cha mafuta Tanzania — je, inawezekana?",
"answer_sw": "Hapana, haiwezekani kama biashara yako binafsi. Uendeshaji wa vituo vya mafuta na petroli ni moja ya shughuli 15 zilizozuiliwa kwa watu wasio raia wa Tanzania chini ya GN 487A (2025). Hata kama una leseni ya mauzo ya mafuta kutoka EWURA (Energy and Water Utilities Regulatory Authority), GN 487A inakukatalia umiliki wa moja kwa moja wa kituo cha mafuta. Unaweza kuchunguza uwezekano wa uwekezaji kupitia kampuni ya Tanzania iliyosajiliwa vizuri, lakini hii inahitaji ushauri wa wakili kabla ya kuanza.",
"question_en": "As a non-citizen I want to open a petrol station in Tanzania — is this possible?",
"answer_en": "No, not as your own business. Operating petrol and fuel stations is one of the 15 business activities prohibited for non-Tanzanian citizens under GN 487A (2025). Even if you have a fuel sales licence from EWURA (Energy and Water Utilities Regulatory Authority), GN 487A denies you direct ownership of a petrol station. You may explore investment through a properly registered Tanzanian company, but this requires legal advice before proceeding.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "business_market", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_024_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Familia yangu kutoka nje ina kinu cha kusaga unga kijijini — je, inabidi wafanye nini?",
"answer_sw": "Chini ya GN 487A (2025), kusaga nafaka na unga (flour milling) ni moja ya shughuli 15 zilizozuiliwa kwa watu wasio raia wa Tanzania. Familia yako lazima isimamishe shughuli hii au ihamishie umiliki kwa raia wa Tanzania kisheria kabla hawajakamatwa. Ukiwa umeendelea bila kubadilisha muundo wa umiliki, wanaweza kupata faini ya angalau TZS milioni 10, kifungo cha hadi miezi 6, na kufutwa kwa viza. Njia bora ni kupata ushauri wa wakili kuhusu jinsi ya kubadilisha muundo wa biashara haraka.",
"question_en": "My family from abroad runs a flour mill in a village — what should they do?",
"answer_en": "Under GN 487A (2025), flour milling is one of the 15 business activities prohibited for non-Tanzanian citizens. Your family must cease this activity or legally transfer ownership to a Tanzanian citizen before facing enforcement. Continuing without changing the ownership structure risks a minimum TZS 10 million fine, up to 6 months imprisonment, and visa revocation. The best course is to seek legal advice about restructuring the business quickly.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "rural_conversational", "pair_type": "adversarial", "eval_set": False
},
# ─────────────────────────────────────────────────────────────
# BLOCK 11: Auctioneer / brokerage — prohibited
# ─────────────────────────────────────────────────────────────
{
"id": "tier1a_gn487a_025_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Dalali wa mali isiyohamishika kutoka nje anaweza kufanya kazi Tanzania?",
"answer_sw": "Kama mwenye biashara yake binafsi, hapana. Huduma za udalali (brokerage services) — ikiwa ni pamoja na madalali wa mali isiyohamishika, wahamasishaji wa mauzo, na waamuzi wa bei — ni moja ya shughuli 15 zilizozuiliwa chini ya GN 487A (2025). Dalali huyu hawezi kumiliki au kuendesha ofisi ya udalali kama biashara yake. Anaweza kufanya kazi kama mfanyakazi wa kampuni ya udalali inayomilikiwa na raia wa Tanzania, mradi ana kibali sahihi cha kufanya kazi. Lakini kuwa mmiliki au mkurugenzi wa biashara ya udalali si ruhusiwa.",
"question_en": "Can a foreign real estate broker operate in Tanzania?",
"answer_en": "As an independent business owner, no. Brokerage services — including real estate agents, sales brokers, and price intermediaries — are one of the 15 prohibited activities under GN 487A (2025). This broker cannot own or operate a brokerage office as their own business. They may work as an employee of a brokerage company owned by a Tanzanian citizen, provided they have a valid work permit. But owning or directing a brokerage business is not permitted.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "business_market", "pair_type": "adversarial", "eval_set": False
},
# ─────────────────────────────────────────────────────────────
# BLOCK 12: Tourism — prohibited
# ─────────────────────────────────────────────────────────────
{
"id": "tier1a_gn487a_026_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Mgeni anaweza kufungua wakala wa utalii Tanzania?",
"answer_sw": "Hapana. Huduma za wakala wa utalii na uongozaji wa safari (travel agency and tour guiding) ni moja ya shughuli 15 zilizozuiliwa kwa watu wasio raia wa Tanzania chini ya GN 487A (2025). Hata kama ana leseni ya TANAPA (Tanzania National Parks) au TTB (Tanzania Tourism Board), mgeni hawezi kumiliki au kuendesha wakala wa utalii kama biashara yake binafsi. Anaweza kufanya kazi kama mwongozaji wa utalii kwa kampuni inayomilikiwa na Watanzania, lakini si kama mmiliki wake. Adhabu ni faini ya angalau TZS milioni 10, miezi 6 jela, na kufutwa kwa viza.",
"question_en": "Can a non-citizen open a travel agency in Tanzania?",
"answer_en": "No. Travel agency and tour guiding services are one of the 15 business activities prohibited for non-Tanzanian citizens under GN 487A (2025). Even with a TANAPA (Tanzania National Parks) or TTB (Tanzania Tourism Board) licence, a non-citizen cannot own or operate a travel agency as their own business. They may work as a tour guide for a Tanzanian-owned company, but not as the owner. Penalties are a minimum TZS 10 million fine, 6 months imprisonment, and visa revocation.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
# ─────────────────────────────────────────────────────────────
# BLOCK 13: Employment bureau — prohibited
# ─────────────────────────────────────────────────────────────
{
"id": "tier1a_gn487a_027_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Kampuni ya uajiri (recruitment/employment agency) inaweza kumilikiwa na raia wa kigeni?",
"answer_sw": "Hapana. Huduma za uajiri na wakala wa ajira (employment bureau / recruitment agency) ni moja ya shughuli 15 zilizozuiliwa kwa watu wasio raia wa Tanzania chini ya GN 487A (2025). Raia wa kigeni hawezi kumiliki au kuendesha kampuni ya uajiri kama biashara yake binafsi nchini Tanzania. Akijaribu kufanya hivyo, anakabiliwa na faini ya angalau TZS milioni 10, kifungo cha hadi miezi 6, na kufutwa kwa viza. Sekta hii ni nyeti kwa sababu inahusiana na masoko ya ajira kwa Watanzania.",
"question_en": "Can a foreign national own an employment/recruitment agency in Tanzania?",
"answer_en": "No. Employment bureau and recruitment agency services are one of the 15 business activities prohibited for non-Tanzanian citizens under GN 487A (2025). A foreign national cannot own or operate a recruitment agency as their own business in Tanzania. Attempting to do so risks a minimum TZS 10 million fine, up to 6 months imprisonment, and visa revocation. This sector is particularly sensitive as it relates to the labour market for Tanzanian citizens.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
# ─────────────────────────────────────────────────────────────
# BLOCK 14: Spare parts — prohibited
# ─────────────────────────────────────────────────────────────
{
"id": "tier1a_gn487a_028_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Biashara ya vipande vya magari (spare parts) inaweza kumilikiwa na mgeni?",
"answer_sw": "Hapana. Biashara ya vipande vya magari na elektroniki (spare parts trading) ni moja ya shughuli 15 zilizozuiliwa kwa watu wasio raia wa Tanzania chini ya GN 487A (2025). Maduka ya vipande vya magari, baisikeli, au vifaa vya elektroniki yanayomilikiwa na wageni yamezuiwa. Adhabu ni faini ya angalau TZS milioni 10, kifungo cha hadi miezi 6, na kufutwa kwa viza. Raia wa Tanzania anayemruhusu mgeni kutumia jina lake la biashara kwa hili anakabiliwa na faini ya TZS milioni 5 au kifungo cha miezi 3.",
"question_en": "Can a non-citizen own a spare parts (car/electronics) business?",
"answer_en": "No. Spare parts trading for vehicles and electronics is one of the 15 business activities prohibited for non-Tanzanian citizens under GN 487A (2025). Shops selling car, bicycle, or electronics spare parts that are non-citizen-owned are prohibited. Penalties are a minimum TZS 10 million fine, up to 6 months imprisonment, and visa revocation. A Tanzanian who allows a non-citizen to use their business name for this faces a TZS 5 million fine or 3 months imprisonment.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "rural_conversational", "pair_type": "adversarial", "eval_set": False
},
# ─────────────────────────────────────────────────────────────
# BLOCK 15: Disambiguation — 15 categories vs other permits
# ─────────────────────────────────────────────────────────────
{
"id": "tier1a_gn487a_029_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Je, GN 487A inaathiri makampuni makubwa ya kimataifa yanayofanya kazi Tanzania?",
"answer_sw": "Inategemea muundo wa umiliki na aina ya biashara. GN 487A inazuia watu binafsi wasio raia wa Tanzania kumiliki biashara katika makundi 15 maalum. Makampuni makubwa ya kimataifa (kama MNCs) yanayofanya kazi Tanzania kwa njia ya kampuni iliyosajiliwa Tanzania yanaweza kuathiriwa kama mmiliki mkuu au mkurugenzi mtendaji ni mgeni anayeendesha moja ya biashara 15 zilizozuiliwa. Kampuni zinazofanya kazi katika sekta zisizozuiliwa (kama madini, uzalishaji wa viwandani, IT, fedha rasmi) kwa ujumla haziathiriwi. Ushauri wa kisheria ni muhimu kwa kila kampuni kutathmini muundo wake.",
"question_en": "Does GN 487A affect large multinational companies operating in Tanzania?",
"answer_en": "It depends on ownership structure and business type. GN 487A prohibits individual non-Tanzanian citizens from owning businesses in 15 specific categories. Large international companies (MNCs) operating in Tanzania through a locally registered company may be affected if the primary owner or managing director is a non-citizen running one of the 15 prohibited business types. Companies operating in non-restricted sectors (such as mining, manufacturing, IT, formal finance) are generally not affected. Legal advice is essential for each company to assess its own structure.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_030_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Mwekezaji wa kigeni mwenye hisa katika kampuni ya Tanzania — je, GN 487A inamzuia?",
"answer_sw": "Si kwa njia ya moja kwa moja. GN 487A inalenga biashara zinazomilikiwa au kuendeshwa NA wageni moja kwa moja — si uwekezaji wa hisa kwa ujumla. Mwekezaji wa kigeni mwenye hisa ndogo (minority shareholder) katika kampuni ya Tanzania inayomilikiwa na Watanzania kwa wengi haizuiwi na GN 487A, mradi kampuni inafanya kazi katika sekta zinazoruhusu uwekezaji wa kigeni. Hata hivyo, kama mwekezaji huyu ndiye mkurugenzi mtendaji anayeendesha moja ya sekta 15 zilizozuiliwa, hali inaweza kuwa tofauti. Ushauri wa kisheria unapendekezwa.",
"question_en": "A foreign investor with shares in a Tanzanian company — does GN 487A restrict them?",
"answer_en": "Not directly. GN 487A targets businesses owned or operated BY non-citizens directly — not general shareholding. A foreign investor who is a minority shareholder in a Tanzanian-majority-owned company is not restricted by GN 487A, provided the company operates in sectors that allow foreign investment. However, if that investor is also the managing director operating one of the 15 prohibited sectors, the situation may differ. Legal advice is recommended.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
# ─────────────────────────────────────────────────────────────
# BLOCK 16: Rural register — adversarial framing
# ─────────────────────────────────────────────────────────────
{
"id": "tier1a_gn487a_031_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Jirani yangu mgeni anauza mahindi na maharage sokoni — je, ana tatizo la sheria?",
"answer_sw": "Ndiyo, labda ana tatizo. Chini ya GN 487A (2025), biashara ya rejareja — ikiwa ni pamoja na kuuza mazao ya kilimo sokoni — ni moja ya shughuli 15 zilizozuiliwa kwa watu wasio raia wa Tanzania. Kama jirani yako mgeni anauza mahindi, maharage, au mazao mengine kama biashara yake binafsi, anakiuka GN 487A. Adhabu ni faini ya angalau TZS milioni 10 na kifungo cha hadi miezi 6 jela. Unaweza kumwambia aone wakili au asilimame mpaka apate ushauri sahihi wa kisheria.",
"question_en": "My foreign neighbour sells maize and beans at the market — do they have a legal problem?",
"answer_en": "Yes, possibly. Under GN 487A (2025), retail trade — including selling agricultural produce at a market — is one of the 15 activities prohibited for non-Tanzanian citizens. If your neighbour is selling maize, beans, or other produce as their own business, they are violating GN 487A. Penalties are a minimum TZS 10 million fine and up to 6 months imprisonment. You can advise them to see a lawyer or stop until they get proper legal advice.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "rural_conversational", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_032_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Mama lishe mgeni karibu na ofisi yangu — je, sheria inamsemaje?",
"answer_sw": "Chini ya GN 487A (2025), biashara ya rejareja ya chakula — ikiwa ni pamoja na mama lishe wanaoandaa na kuuza chakula — ni kati ya shughuli zilizozuiliwa kwa watu wasio raia wa Tanzania. Mama lishe huyu mgeni anaweza kukiuka GN 487A kama anachukuliwa kuendesha biashara yake binafsi. Adhabu inayowezekana ni faini ya TZS milioni 10 au zaidi na kifungo cha hadi miezi 6. Hali yake ya kisheria inahitaji uchunguzi — ikiwezekana apate ushauri wa wakili wa uhamiaji.",
"question_en": "There is a foreign mama lishe (street food seller) near my office — what does the law say?",
"answer_en": "Under GN 487A (2025), retail food business — including mama lishe who prepare and sell food — falls within the prohibited activities for non-Tanzanian citizens. This foreign mama lishe may be violating GN 487A if they are considered to be running their own business. Potential penalties are a TZS 10 million or more fine and up to 6 months imprisonment. Their legal situation requires review — they should ideally get immigration legal advice.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "rural_conversational", "pair_type": "adversarial", "eval_set": False
},
# ─────────────────────────────────────────────────────────────
# BLOCK 17: Number of prohibited categories
# ─────────────────────────────────────────────────────────────
{
"id": "tier1a_gn487a_033_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "GN 487A inazuia makundi mangapi ya biashara kwa wageni?",
"answer_sw": "GN 487A (2025) inazuia jumla ya makundi 15 (kumi na tano) ya biashara kwa watu wasio raia wa Tanzania. Makundi haya yanajumuisha (lakini si tu): biashara ya jumla, biashara ya rejareja, huduma za uhamisho wa pesa kwa simu, ukarabati wa simu, saluni na kinyozi, ubadilishaji wa fedha za kigeni, uendeshaji wa vituo vya mafuta, huduma za madalali, usafirishaji na uwakala wa forodha, wakala wa utalii, wakala wa ajira, huduma za uchukuzi wa haraka, biashara ya vipande vya magari, kusaga nafaka, na huduma za udalali wa mali isiyohamishika. Orodha kamili ipo katika GN 487A iliyosajiliwa kwenye Tanzania Government Gazette.",
"question_en": "How many business categories does GN 487A prohibit for non-citizens?",
"answer_en": "GN 487A (2025) prohibits a total of 15 (fifteen) business categories for non-Tanzanian citizens. These categories include (but are not limited to): wholesale trade, retail trade, mobile money transfer services, phone repair, salons and barbershops, forex bureaus, petrol station operations, brokerage services, clearing and forwarding, travel agencies, employment bureaus, courier services, spare parts trading, flour milling, and property brokerage. The complete list is in GN 487A as published in the Tanzania Government Gazette.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
# ─────────────────────────────────────────────────────────────
# BLOCK 18: What happens after arrest
# ─────────────────────────────────────────────────────────────
{
"id": "tier1a_gn487a_034_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Mgeni akikamatwa akifanya biashara iliyozuiliwa, hatua za kisheria ni zipi?",
"answer_sw": "Chini ya GN 487A (2025), mgeni anayekamatwa akifanya biashara iliyozuiliwa anakabiliwa na hatua zifuatazo: (1) Biashara inafungwa mara moja na vitu vya biashara vinaweza kukamatwa, (2) Mgeni anashtakiwa mahakamani, (3) Akipatikana na hatia, anaweza kupata faini ya angalau TZS milioni 10, kifungo cha hadi miezi 6, AU vyote viwili, (4) Viza yake inafutwa, (5) Anaweza kufukuzwa nchini (deportation). Operesheni ya utekelezaji wa kwanza (Sep-Oct 2025) ilionyesha kwamba biashara zilifungwa haraka bila fursa ya kuomba msamaha.",
"question_en": "If a non-citizen is arrested for operating a prohibited business, what are the legal steps?",
"answer_en": "Under GN 487A (2025), a non-citizen arrested for operating a prohibited business faces: (1) Immediate business closure and possible seizure of business goods, (2) Criminal prosecution in court, (3) If convicted, a minimum TZS 10 million fine, up to 6 months imprisonment, OR both, (4) Visa revocation, (5) Possible deportation. The first enforcement exercise (Sep-Oct 2025) showed that businesses were closed swiftly without opportunity for leniency.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
# ─────────────────────────────────────────────────────────────
# BLOCK 19: Disambiguation — GN487A vs work permit (3 more)
# ─────────────────────────────────────────────────────────────
{
"id": "tier1a_gn487a_035_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Kibali cha kazi (work permit) kinamzuia mgeni kufanya biashara iliyozuiliwa?",
"answer_sw": "Hapana. Kibali cha kazi kinaruhusu mgeni kufanya kazi kama mfanyakazi wa kampuni au taasisi — si kumiliki au kuendesha biashara yake binafsi. GN 487A na sheria ya vibali vya kazi ni tofauti kabisa: kibali cha kazi kinahusu uhusiano wa ajira, GN 487A inahusu umiliki wa biashara katika makundi 15. Mgeni mwenye kibali cha kazi anaweza bado kukiuka GN 487A kama anafanya biashara iliyozuiliwa kando ya kazi yake ya kawaida. Ni muhimu kutofautisha kati ya 'mfanyakazi' na 'mwenye biashara'.",
"question_en": "Does a work permit prevent a non-citizen from operating a prohibited business?",
"answer_en": "No. A work permit allows a non-citizen to work as an employee of a company or institution — not to own or operate their own business. GN 487A and work permit law are completely different: work permits concern employment relationships, GN 487A concerns business ownership in 15 categories. A non-citizen with a work permit can still violate GN 487A by running a prohibited business alongside their regular employment. It is important to distinguish between being an 'employee' and a 'business owner'.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "business_market", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_036_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "GN 487A ni tofauti na GN 605A — zinasemaje?",
"answer_sw": "Ndio, hizi ni amri tofauti kabisa. GN 487A (Business Licensing (Prohibition of Business Activities for Non-Citizens) Order 2025, inayofanya kazi kuanzia 28 Julai 2025) inazuia wageni kufanya biashara katika makundi 15 maalum. GN 605A (Wage Order 2025, iliyosajiliwa 13 Oktoba 2025, inayofanya kazi kuanzia 1 Januari 2026) inabainisha mishahara ya chini ya sekta mbalimbali kwa wafanyakazi wote Tanzania. GN 487A inahusu UMILIKI wa biashara; GN 605A inahusu MISHAHARA ya wafanyakazi. Kampuni inaweza kufuata GN 605A (kulipa mishahara sahihi) na bado kukiuka GN 487A (kama mmiliki ni mgeni katika sekta zilizozuiliwa).",
"question_en": "GN 487A and GN 605A are different — what does each say?",
"answer_en": "Yes, these are completely different Orders. GN 487A (Business Licensing Prohibition Order 2025, effective 28 July 2025) prohibits non-citizens from operating businesses in 15 specific categories. GN 605A (Wage Order 2025, gazetted 13 October 2025, effective 1 January 2026) sets minimum wages across various sectors for all workers in Tanzania. GN 487A concerns business OWNERSHIP; GN 605A concerns worker WAGES. A company can comply with GN 605A (paying correct wages) and still violate GN 487A (if the owner is a non-citizen in a prohibited sector).",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_037_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Sijui GN 487A inaathiri sekta yangu — nifanye nini?",
"answer_sw": "Hatua bora ni: (1) Angalia orodha kamili ya makundi 15 ya shughuli zilizozuiliwa katika GN 487A kwenye TanzLII.org, (2) Linganisha sekta yako na orodha hiyo, (3) Kama sekta yako ipo kwenye orodha na wewe ni mgeni, wasiliana na wakili wa biashara au uhamiaji haraka, (4) Kama huna uhakika, pata ushauri wa kisheria kabla ya kuendelea na biashara. Usijaribu kujiamua mwenyewe bila ushauri wa kisheria — adhabu za GN 487A ni kali na zinafanya kazi mara moja. Biashara zinazoathiriwa zinapendekezwa kutathmini muundo wao wa umiliki na mshauri wa kisheria.",
"question_en": "I am not sure if GN 487A affects my sector — what should I do?",
"answer_en": "The best steps are: (1) Check the complete list of 15 prohibited activity categories in GN 487A at TanzLII.org, (2) Compare your sector against that list, (3) If your sector is on the list and you are a non-citizen, contact a business or immigration lawyer urgently, (4) If unsure, get legal advice before continuing to operate. Do not try to self-assess without legal advice — GN 487A penalties are severe and take immediate effect. Affected businesses are advised to review their ownership structure with a legal adviser.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "business_market", "pair_type": "adversarial", "eval_set": False
},
# ─────────────────────────────────────────────────────────────
# BLOCK 20: Final batch — mixed registers, edge questions
# ─────────────────────────────────────────────────────────────
{
"id": "tier1a_gn487a_038_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Raia wa nchi ya EAC (kama Uganda au Kenya) ana upendeleo wowote chini ya GN 487A?",
"answer_sw": "Hapana. GN 487A (2025) haitoa upendeleo wowote kwa raia wa nchi za EAC (Jumuiya ya Afrika Mashariki) kama Uganda, Kenya, Rwanda, Burundi, au DRC. Amri inazungumzia watu 'wasio raia wa Tanzania' kwa ujumla bila kutofautisha asili ya nchi. Hata kama kuna makubaliano ya biashara ya EAC, GN 487A inatumika kwa watu wote wa kigeni wanaofanya biashara katika makundi 15 nchini Tanzania. Raia wa Kenya au Uganda anayeendesha duka la rejareja au saluni Tanzania anakiuka GN 487A sawa na raia wa China au Ulaya.",
"question_en": "Does an EAC citizen (e.g. Ugandan or Kenyan) get any preference under GN 487A?",
"answer_en": "No. GN 487A (2025) gives no preference to citizens of EAC countries (East African Community) such as Uganda, Kenya, Rwanda, Burundi, or DRC. The Order refers to persons 'who are not Tanzanian citizens' broadly, without distinguishing national origin. Even if there are EAC trade agreements, GN 487A applies to all non-citizens operating businesses in the 15 categories in Tanzania. A Kenyan or Ugandan running a retail shop or salon in Tanzania violates GN 487A in the same way as a Chinese or European national.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_039_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Mkono mrefu wa Idara ya Uhamiaji unafika hadi vijiji — wanaweza kufuatilia biashara za mgeni?",
"answer_sw": "Ndiyo. Idara ya Uhamiaji ina mamlaka ya kufanya ukaguzi na operesheni za utekelezaji kote nchini, ikiwa ni pamoja na maeneo ya vijijini. Operesheni ya kwanza ya GN 487A (Septemba-Oktoba 2025) iliendelea maeneo mengi ya Tanzania Bara. Biashara za wageni katika maeneo ya vijijini zinaathiriwa sawa na maeneo ya mijini. Mkakati bora ni kuhakikisha biashara zote za wageni zinakubaliana na GN 487A kabla ya utekelezaji kufikia eneo lako.",
"question_en": "Can the Immigration Department reach villages to monitor foreign-owned businesses?",
"answer_en": "Yes. The Immigration Department has authority to conduct inspections and enforcement operations across the country, including rural areas. The first GN 487A enforcement exercise (September-October 2025) covered many areas of Tanzania Mainland. Foreign businesses in rural areas are affected equally to urban areas. The best approach is to ensure all foreign-owned businesses comply with GN 487A before enforcement reaches your area.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "rural_conversational", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_040_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Mgeni anayeomba kuhamia Tanzania anaweza kufungua duka — amri ya GN 487A inasemaje?",
"answer_sw": "GN 487A inamzuia mgeni yeyote asiye raia wa Tanzania kufungua duka la rejareja au biashara nyingine yoyote katika makundi 15 yaliyozuiliwa — bila kujali kama ana kibali cha makazi au la, au kama ameomba uhalisi wa kudumu au la. Hali ya uhamiaji (immigraiton status) haibadilishi uhalali wa kumiliki biashara katika sekta hizi. Duka la rejareja ni miongoni mwa shughuli zilizozuiliwa wazi. Mtu huyu anapaswa kupata ushauri wa kisheria kabla ya kufanya maamuzi ya biashara nchini Tanzania.",
"question_en": "A foreigner applying to move to Tanzania wants to open a shop — what does GN 487A say?",
"answer_en": "GN 487A prohibits any non-Tanzanian citizen from opening a retail shop or any other business in the 15 prohibited categories — regardless of whether they have a residence permit, have applied for permanent residency, or are in any immigration status. Immigration status does not change the legality of owning a business in these sectors. A retail shop is explicitly among the prohibited activities. This person should get legal advice before making any business decisions in Tanzania.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "business_market", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_041_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Kampuni yetu inaajiri Watanzania wengi — je, bado GN 487A inatuathiri kama wamiliki ni wageni?",
"answer_sw": "Ndiyo. Kuajiri Watanzania wengi hakubadilishi ukweli kwamba mmiliki ni mgeni anayefanya biashara katika sekta iliyozuiliwa. GN 487A inazingatia UMILIKI na UENDESHAJI wa biashara — si idadi ya wafanyakazi wa Kitanzania. Ikiwa biashara yako iko katika moja ya makundi 15 yaliyozuiliwa na mmiliki mkuu ni mgeni, kampuni inakiuka GN 487A bila kujali wafanyakazi wake. Hata hivyo, kuajiri Watanzania wengi ni jambo zuri na linaweza kusaidia wakati wa mazungumzo ya kisheria, lakini halitoi ulinzi dhidi ya GN 487A.",
"question_en": "Our company employs many Tanzanians — does GN 487A still apply to us if owners are non-citizens?",
"answer_en": "Yes. Employing many Tanzanians does not change the fact that the owner is a non-citizen operating in a prohibited sector. GN 487A focuses on OWNERSHIP and OPERATION of the business — not the number of Tanzanian employees. If your business is in one of the 15 prohibited categories and the primary owner is a non-citizen, the company violates GN 487A regardless of its workforce. However, employing many Tanzanians is positive and may assist in legal negotiations, but it does not provide protection against GN 487A.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_042_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Je, kuna njia ya halali ya mgeni kuendesha duka la rejareja Tanzania?",
"answer_sw": "Njia ya kawaida inayozingatiwa kisheria ni ubia (joint venture) ambapo raia wa Tanzania ndiye mmiliki mkuu wa kisheria na mwenye udhibiti wa biashara, huku mwekezaji wa kigeni akiwa na hisa au mchango wa mtaji bila kumiliki au kudhibiti biashara moja kwa moja. Hata hivyo, muundo huu lazima uwe wa kweli na si wa kuficha ukweli — BRELA na Idara ya Uhamiaji wanajua mbinu za 'dummy owner'. Ushauri wa wakili wenye uzoefu wa sheria za biashara na uhamiaji Tanzania ni lazima kabla ya kuanza muundo wowote wa ubia. Kuvunja GN 487A kwa makusudi kupitia utaratibu wa bandia kunaweza kuongeza adhabu.",
"question_en": "Is there a legal way for a non-citizen to operate a retail shop in Tanzania?",
"answer_en": "The commonly considered legal route is a joint venture where a Tanzanian citizen is the primary legal owner and controls the business, while the foreign investor holds shares or contributes capital without directly owning or controlling it. However, this structure must be genuine and not a disguise — BRELA and the Immigration Department are aware of 'dummy owner' techniques. Legal advice from a lawyer experienced in Tanzanian business and immigration law is essential before setting up any partnership structure. Intentionally circumventing GN 487A through a sham arrangement can increase penalties.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "business_market", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_043_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "GN 487A ina nguvu ya kisheria au ni mwongozo tu?",
"answer_sw": "GN 487A ina nguvu kamili ya kisheria. Ni amri rasmi iliyosajiliwa kwenye Tanzania Government Gazette, iliyotolewa chini ya Sheria ya Leseni za Biashara (Business Licensing Act). Kwa sababu imesajiliwa rasmi (gazetted), ina nguvu ya sheria kama ilivyo sheria yoyote nyingine ya Tanzania. Kutofuata amri hii kunasababisha mashtaka ya jinai (criminal prosecution), si adhabu za kiutawala tu. Idara ya Uhamiaji ina nguvu ya kukamata na kushtaki watu wanaokiuka GN 487A moja kwa moja bila taarifa ya awali.",
"question_en": "Does GN 487A have legal force or is it just a guideline?",
"answer_en": "GN 487A has full legal force. It is a formal Order published in the Tanzania Government Gazette, issued under the Business Licensing Act. Because it is officially gazetted, it has the same force as any other Tanzanian law. Non-compliance results in criminal prosecution, not just administrative penalties. The Immigration Department has the power to arrest and prosecute persons violating GN 487A directly, without prior warning.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_044_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Nakala ya GN 487A inapatikana wapi ili niisomee?",
"answer_sw": "Nakala kamili ya GN 487A inapatikana bure kwenye TanzLII.org (Tanzania Legal Information Institute) kwa anwani: https://tanzlii.org/akn/tz/act/gn/2025/487a/eng@2025-07-28. Pia inaweza kupatikana kwenye Tanzania Government Gazette rasmi. Kwa msaada wa uhalisi, makampuni ya kisheria kama Bowmans, Dentons, DLA Piper, na VELMA Law wamechapisha muhtasari wa GN 487A kwenye tovuti zao — lakini ushauri wao si mbadala wa kusoma amri yenyewe au kupata ushauri wa wakili binafsi.",
"question_en": "Where can I find a copy of GN 487A to read it myself?",
"answer_en": "The full text of GN 487A is available free of charge at TanzLII.org (Tanzania Legal Information Institute) at: https://tanzlii.org/akn/tz/act/gn/2025/487a/eng@2025-07-28. It is also available in the official Tanzania Government Gazette. For practical guidance, law firms such as Bowmans, Dentons, DLA Piper, and VELMA Law have published summaries of GN 487A on their websites — but their advisories are not a substitute for reading the Order itself or getting your own legal advice.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "business_market", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_045_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Mgeni ana kampuni iliyosajiliwa BRELA — hii inamlinda dhidi ya GN 487A?",
"answer_sw": "Hapana. Kuwa na kampuni iliyosajiliwa BRELA hakumlindi mgeni dhidi ya GN 487A kama kampuni hiyo inafanya biashara katika moja ya sekta 15 zilizozuiliwa. GN 487A inazuia watu wasio raia KUMILIKI na KUENDESHA biashara katika sekta hizi — na hilo linahusu hata kama wana kampuni iliyosajiliwa kisheria. BRELA inasajili kampuni lakini haina mamlaka ya kutoa ruhusa dhidi ya GN 487A. Usajili wa BRELA na ufuatamizi wa GN 487A ni mambo mawili tofauti ambayo lazima yashughulikiwe kwa wakati mmoja.",
"question_en": "A non-citizen has a BRELA-registered company — does this protect them against GN 487A?",
"answer_en": "No. Having a BRELA-registered company does not protect a non-citizen against GN 487A if that company operates in one of the 15 prohibited sectors. GN 487A prohibits non-citizens from OWNING and OPERATING businesses in these sectors — and this applies even with a legally registered company. BRELA registers companies but has no authority to grant exemption from GN 487A. BRELA registration and GN 487A compliance are two separate matters that must be addressed simultaneously.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "business_market", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_046_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Je, GN 487A inaathiri Watanzania wa diaspora waliozaliwa nje ya nchi?",
"answer_sw": "GN 487A inahusu watu 'wasio raia wa Tanzania' — yaani watu ambao hawana uraia wa Tanzania kisheria. Mtanzania wa diaspora aliyezaliwa nje ya nchi lakini akiwa na pasipoti ya Tanzania na uraia wa Tanzania hawathiriwi na GN 487A — anachukuliwa kama raia wa Tanzania. Hata hivyo, kama mtu ana uraia wa nchi mbili (dual citizenship) na Tanzania hairuhusu uraia wa nchi mbili, hali yake ya kisheria inaweza kuwa ngumu. Watu walio na maswali kuhusu hali yao ya uraia wanapaswa kuwasiliana na Wizara ya Mambo ya Ndani au wakili wa uhamiaji.",
"question_en": "Does GN 487A affect Tanzanians in the diaspora who were born outside the country?",
"answer_en": "GN 487A applies to persons 'who are not Tanzanian citizens' — that is, people who do not legally hold Tanzanian citizenship. A Tanzanian in the diaspora who was born abroad but holds a Tanzanian passport and citizenship is not affected by GN 487A — they are treated as a Tanzanian citizen. However, if a person holds dual citizenship and Tanzania does not recognise dual citizenship, their legal situation may be complex. Those with questions about their citizenship status should contact the Ministry of Home Affairs or an immigration lawyer.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_047_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Jirani yangu mgeni ana biashara ndogo ya kuchoma nyama — GN 487A inamhusu?",
"answer_sw": "Inategemea jinsi biashara inavyoainishwa. Kuchoma na kuuza nyama kunaweza kuainishwa kama biashara ya rejareja ya chakula, ambayo ni moja ya sekta zilizozuiliwa. Kama jirani yako mgeni anafanya biashara hii kama mmiliki wake binafsi, labda anakiuka GN 487A. Hata hivyo, kama anafanya kazi kama mfanyakazi wa kampuni ya chakula inayomilikiwa na Mtanzania, hiyo si tatizo la GN 487A. Hali yake inategemea muundo halisi wa biashara. Ni bora ampeleke apate ushauri wa kisheria ili ajue kwa uhakika.",
"question_en": "My foreign neighbour has a small nyama choma (grilled meat) stall — does GN 487A apply?",
"answer_en": "It depends on how the business is classified. Grilling and selling meat may be classified as retail food business, which is one of the prohibited sectors. If your foreign neighbour operates this as their own individual business, they may be violating GN 487A. However, if they work as an employee of a Tanzanian-owned food company, that is not a GN 487A issue. Their situation depends on the actual business structure. It is best for them to get legal advice to know for certain.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "rural_conversational", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_048_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Kampuni yangu inaagiza bidhaa kutoka nje na kuziuza — je, GN 487A inaathiri uagizaji wa bidhaa?",
"answer_sw": "Inategemea hatua ya biashara. GN 487A inazuia wageni kuuza bidhaa nchini Tanzania kwa njia ya rejareja au jumla (retail/wholesale) — uagizaji (importation) wenyewe hauzuiiwi kwa njia ya moja kwa moja. Hata hivyo, kama mwagizaji ni mgeni na pia anauza bidhaa hizo moja kwa moja kwa wateja (retail) au kwa wachuuzi (wholesale), anakiuka GN 487A. Mgeni anaweza kuwa mwagizaji na kuuza bidhaa kwa kampuni ya Tanzania iliyosajiliwa ambayo kisha inauza kwa wateja — lakini muundo huu unahitaji ushauri wa wakili ili uhakikishe unakubaliana na sheria.",
"question_en": "My company imports goods from abroad and sells them — does GN 487A affect importing?",
"answer_en": "It depends on the stage of the business. GN 487A prohibits non-citizens from selling goods in Tanzania through retail or wholesale — importation itself is not directly prohibited. However, if the importer is a non-citizen who also directly sells those goods to customers (retail) or to traders (wholesale), they violate GN 487A. A non-citizen may import and sell goods to a registered Tanzanian company which then sells to customers — but this structure requires legal advice to ensure compliance.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "business_market", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_049_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Je, kuna maeneo maalum Tanzania ambapo GN 487A haitumiki — kama EPZ au viwanda maalum?",
"answer_sw": "Hapana maeneo maalum yaliyotajwa katika GN 487A ambapo amri haitumiki. GN 487A inatumika Tanzania Bara yote. Hata hivyo, EPZ (Export Processing Zones) na viwanda vya SEZ (Special Economic Zones) vina mifumo yao ya kisheria ambayo inaweza kutoa fursa tofauti za uwekezaji wa kigeni — lakini hizo ni mifumo tofauti inayosimamiwa na EPZA (Export Processing Zones Authority), si suala la GN 487A moja kwa moja. Mgeni katika EPZ bado anaweza kukiuka GN 487A kama anafanya biashara iliyozuiliwa nje ya mipaka ya EPZ. Ushauri maalum wa kisheria kwa kila hali unapendekezwa.",
"question_en": "Are there special zones in Tanzania where GN 487A does not apply — like EPZ or special industrial areas?",
"answer_en": "No specific areas are mentioned in GN 487A where the Order does not apply. GN 487A applies across all of Tanzania Mainland. However, EPZ (Export Processing Zones) and SEZ (Special Economic Zones) have their own legal frameworks that may offer different foreign investment opportunities — but these are separate regimes regulated by EPZA (Export Processing Zones Authority), not a GN 487A exception directly. A non-citizen in an EPZ can still violate GN 487A if they conduct prohibited activities outside EPZ boundaries. Specific legal advice for each situation is recommended.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "formal", "pair_type": "adversarial", "eval_set": False
},
{
"id": "tier1a_gn487a_050_20260608",
"domain": "tier1a", "subdomain": "gn487a_compliance",
"question_sw": "Ninapaswa kumripoti vipi mgeni anayefanya biashara iliyozuiliwa katika mtaa wangu?",
"answer_sw": "Unaweza kuripoti mgeni anayefanya biashara iliyozuiliwa chini ya GN 487A kwa njia zifuatazo: (1) Idara ya Uhamiaji ya mkoa wako au wilaya yako, (2) Polisi wa biashara (Business Intelligence Unit), (3) BRELA (Business Registrations and Licensing Agency) — ofisi za mkoa, (4) Namba ya dharura ya Uhamiaji ikiwa inapatikana mkoa wako. Utoa taarifa kwa jina au bila jina. Kwa ujumla, inapendekezwa kwamba kwanza ujaribu kutoa ushauri wa kirafiki kwa mgeni huyo kabla ya kuripoti, ili apate nafasi ya kufuata sheria bila kuathiri maisha yake. Lakini ikiwa tatizo linaendelea, kuripoti ni haki yako ya kisheria.",
"question_en": "How do I report a non-citizen operating a prohibited business in my neighbourhood?",
"answer_en": "You can report a non-citizen operating a prohibited business under GN 487A through: (1) The Immigration Department in your region or district, (2) Business Intelligence Unit of Police, (3) BRELA (Business Registrations and Licensing Agency) — regional offices, (4) Immigration emergency number if available in your region. Reports can be made with or without giving your name. Generally, it is advisable to first try offering friendly advice to the non-citizen so they have a chance to comply without disrupting their life. But if the problem continues, reporting is your legal right.",
"primary_source_url": SOURCE_URL, "primary_source_name": SOURCE_NAME,
"source_type": "official_gazette", "effective_date": "2025-07-28",
"decay_risk": "stable", "next_review_trigger": "New Business Licensing Act or amendment to GN 487A",
"verified_by": "founder_self_review", "verified_date": "2026-06-08",
"register": "rural_conversational", "pair_type": "adversarial", "eval_set": False
},
]

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    for pair in PAIRS:
        f.write(json.dumps(pair, ensure_ascii=False) + "\n")

print(f"Saved {len(PAIRS)} pairs to {OUT}")

# Register distribution check
from collections import Counter
regs = Counter(p["register"] for p in PAIRS)
print(f"Register distribution: {dict(regs)}")
print(f"  business_market: {regs['business_market']/len(PAIRS)*100:.0f}%")
print(f"  formal:          {regs['formal']/len(PAIRS)*100:.0f}%")
print(f"  rural_conv:      {regs['rural_conversational']/len(PAIRS)*100:.0f}%")
