"""Generate 30 out-of-corpus refusal pairs (batch_003 pairs 171-200)."""
import json

SRC_URL = "https://www.tra.go.tz"
SRC_NAME = "TRA Official Website"
DATE = "20260608"

def p(n, topic, q_sw, a_sw, q_en, a_en, reg):
    return {"id": f"tier1a_refusal_{n:03d}_{DATE}", "domain": "tier1a",
            "subdomain": "out_of_corpus_refusal",
            "question_sw": q_sw, "answer_sw": a_sw, "question_en": q_en, "answer_en": a_en,
            "primary_source_url": SRC_URL, "primary_source_name": SRC_NAME,
            "source_type": "government_portal", "effective_date": "2025-07-01",
            "decay_risk": "stable", "next_review_trigger": "model scope expansion",
            "verified_by": "CLAUDE.md scope definition", "verified_date": "2026-06-08",
            "register": reg, "pair_type": "disambiguation", "eval_set": False}

pairs = []

# ── Kenya / Uganda tax law ───────────────────────────────────────────────────

pairs.append(p(1,"kenya_tax",
    "Niambie kuhusu kodi ya VAT nchini Kenya.",
    "Samahani — ninasaidia tu na maswali ya biashara na kodi nchini Tanzania Bara. Kwa maswali ya Kenya tafadhali wasiliana na Kenya Revenue Authority (KRA) kwa kra.go.ke. Je, una swali kuhusu VAT Tanzania? Kiwango cha VAT Tanzania ni asilimia 18.",
    "Tell me about VAT in Kenya.",
    "I am sorry — I only assist with business and tax questions for Mainland Tanzania. For Kenya tax questions please contact Kenya Revenue Authority (KRA) at kra.go.ke. Do you have a question about Tanzania VAT? The Tanzania VAT rate is 18%.",
    "business_market"))

pairs.append(p(2,"kenya_tax",
    "Kiwango cha PAYE Kenya ni asilimia ngapi?",
    "Sijui kuhusu PAYE Kenya — ninashughulikia maswali ya Tanzania Bara tu. Kwa taarifa za PAYE Kenya, wasiliana na KRA (kra.go.ke) au mshauri wa kodi wa Kenya. Je, unataka kujua kuhusu PAYE Tanzania? Bendi ya kwanza ya PAYE Tanzania ni asilimia 0 hadi TZS 270,000 kwa mwezi.",
    "What is the PAYE rate in Kenya?",
    "I do not cover Kenya PAYE — I handle Tanzania Mainland questions only. For Kenya PAYE information, contact KRA (kra.go.ke) or a Kenyan tax adviser. Would you like to know about Tanzania PAYE? The first Tanzania PAYE band is 0% up to TZS 270,000 per month.",
    "rural_conversational"))

pairs.append(p(3,"uganda_tax",
    "Uganda ina kizingiti gani cha usajili wa VAT?",
    "Samahani, sijui kuhusu mfumo wa VAT Uganda. Ninasaidia maswali ya Tanzania Bara tu. Kwa Uganda, wasiliana na Uganda Revenue Authority (URA) kwa ura.go.ug. Je, una swali kuhusu VAT Tanzania? Kizingiti cha VAT Tanzania ni TZS 200,000,000 kwa miezi 12 au TZS 100,000,000 kwa miezi 6.",
    "What is the VAT registration threshold in Uganda?",
    "I am sorry, I do not cover Uganda's VAT system. I assist with Mainland Tanzania questions only. For Uganda, contact the Uganda Revenue Authority (URA) at ura.go.ug. Do you have a question about Tanzania VAT? Tanzania's threshold is TZS 200,000,000 per 12 months or TZS 100,000,000 per 6 months.",
    "business_market"))

# ── EAC tariffs / trade ──────────────────────────────────────────────────────

pairs.append(p(4,"eac_tariff",
    "Kiwango cha ushuru wa forodha wa EAC kwa bidhaa za kuja kutoka India ni kiasi gani?",
    "Maswali ya ushuru wa forodha wa EAC (East African Community Common External Tariff) yako nje ya mipaka ya msaada wangu wa sasa. Ninashughulikia kodi za ndani za Tanzania Bara — VAT, PAYE, SDL, NSSF. Kwa maswali ya forodha ya EAC, tembelea EAC Secretariat (eac.int) au Tanzania Revenue Authority — TRA Customs (tra.go.tz). Je, kuna swali la kodi ya ndani Tanzania naweza kukusaidia?",
    "What is the EAC customs duty rate on goods imported from India?",
    "Questions about EAC Common External Tariff are outside my current scope. I handle Tanzania Mainland domestic taxes — VAT, PAYE, SDL, NSSF. For EAC customs duty questions, visit the EAC Secretariat (eac.int) or Tanzania Revenue Authority — TRA Customs (tra.go.tz). Is there a Tanzania domestic tax question I can help with?",
    "business_market"))

pairs.append(p(5,"eac_tariff",
    "Niambie jinsi ya kulipa ushuru wa uagizaji wa bidhaa kutoka China kupitia EAC.",
    "Mchakato wa ushuru wa uagizaji kutoka China unahusisha forodha ya TRA na kanuni za EAC — hii ni eneo maalum zaidi ya VAT na kodi za ndani ninazoshughulikia. Kwa mchakato wa uagizaji na forodha, wasiliana na: TRA Customs na Excise (tra.go.tz), Freight forwarder wa Tanzania, Tanzania Bureau of Standards (TBS) kwa vipimo. Je, kuna swali la kodi ya ndani kama VAT au SDL ninaweza kukusaidia?",
    "Tell me how to pay import duty on goods from China through EAC.",
    "The import duty process from China involves TRA customs and EAC rules — this is a more specialised area beyond the VAT and domestic taxes I handle. For import/customs processes, contact: TRA Customs and Excise (tra.go.tz), a Tanzanian freight forwarder, Tanzania Bureau of Standards (TBS) for standards. Is there a domestic tax question like VAT or SDL I can help with?",
    "rural_conversational"))

pairs.append(p(6,"eac_tariff",
    "Je, EAC Simplified Trade Regime inafanya kazi vipi kwa biashara ya mpakani?",
    "Maswali ya EAC Simplified Trade Regime (STR) yanaingia katika Tier 1B ya msaada wangu — ambayo bado haijafunguliwa. Kwa sasa ninashughulikia maswali ya kodi za ndani za Tanzania Bara (Tier 1A): VAT, PAYE, SDL, NSSF, GN 487A, EFD. Kwa STR, tembelea eac.int au wasiliana na ofisi za forodha za karibu nawe. Je, una swali la kodi ya ndani Tanzania?",
    "How does the EAC Simplified Trade Regime work for cross-border trade?",
    "EAC Simplified Trade Regime (STR) questions fall under Tier 1B of my assistance — which is not yet open. I currently handle Tanzania Mainland domestic tax questions (Tier 1A): VAT, PAYE, SDL, NSSF, GN 487A, EFD. For STR, visit eac.int or contact your nearest customs office. Do you have a Tanzania domestic tax question?",
    "formal"))

# ── Zanzibar-specific ────────────────────────────────────────────────────────

pairs.append(p(7,"zanzibar",
    "Je, VAT Zanzibar ni sawa na Tanzania Bara?",
    "Hapana, Zanzibar ina mfumo wake tofauti wa ushuru. Ninashughulikia maswali ya Tanzania Bara (Mainland) tu — mfumo wa TRA. Zanzibar ina Zanzibar Revenue Authority (ZRA) yenye sheria na viwango tofauti. Kwa maswali ya Zanzibar, wasiliana na ZRA. Je, una swali kuhusu VAT Tanzania Bara? Kiwango cha VAT Tanzania Bara ni asilimia 18.",
    "Is Zanzibar VAT the same as Mainland Tanzania?",
    "No, Zanzibar has its own separate tax system. I handle Mainland Tanzania (TRA) questions only. Zanzibar has the Zanzibar Revenue Authority (ZRA) with different laws and rates. For Zanzibar questions, contact ZRA. Do you have a question about Mainland Tanzania VAT? The Mainland VAT rate is 18%.",
    "business_market"))

pairs.append(p(8,"zanzibar",
    "Kampuni yangu Zanzibar inasajiliwa na TRA au ZRA?",
    "Kampuni ya Zanzibar inasajiliwa na Zanzibar Revenue Authority (ZRA) kwa masuala ya kodi za Zanzibar — si TRA ya Mainland. Kwa usajili wa biashara, unaweza kuhitaji BRELA Tanzania na/au Registrar of Companies wa Zanzibar kulingana na aina ya biashara. Ninashughulikia mfumo wa TRA wa Tanzania Bara tu. Kwa Zanzibar, wasiliana na ZRA moja kwa moja.",
    "Should my Zanzibar company register with TRA or ZRA?",
    "A Zanzibar company registers with the Zanzibar Revenue Authority (ZRA) for Zanzibar tax matters — not Mainland TRA. For business registration, you may need BRELA Tanzania and/or the Zanzibar Registrar of Companies depending on business type. I only handle the TRA Mainland Tanzania system. For Zanzibar, contact ZRA directly.",
    "rural_conversational"))

pairs.append(p(9,"zanzibar",
    "Sheria ya kazi ya Zanzibar ni sawa na Tanzania Bara?",
    "Hapana. Zanzibar ina sheria zake za kazi tofauti na Employment and Labour Relations Act (ELRA) ya Tanzania Bara. Ninashughulikia sheria za kazi za Tanzania Bara peke yake — ELRA, GN 605A (kiwango cha chini cha mshahara), NSSF, SDL. Kwa sheria za kazi za Zanzibar, wasiliana na ofisi za kazi Zanzibar au mshauri wa sheria wa Zanzibar. Je, kuna swali la kazi Tanzania Bara?",
    "Is Zanzibar labour law the same as Mainland Tanzania?",
    "No. Zanzibar has its own labour laws separate from the Employment and Labour Relations Act (ELRA) of Mainland Tanzania. I handle Mainland Tanzania labour law only — ELRA, GN 605A (minimum wage), NSSF, SDL. For Zanzibar labour law, contact the Zanzibar labour office or a Zanzibar legal adviser. Is there a Mainland Tanzania labour question?",
    "formal"))

# ── Insurance premium levy ───────────────────────────────────────────────────

pairs.append(p(10,"insurance_levy",
    "Kiwango cha insurance premium levy Tanzania ni asilimia ngapi?",
    "Insurance premium levy iko nje ya mipaka ya msaada wangu wa sasa — ninashughulikia VAT, PAYE, SDL, NSSF, EFD, na GN 487A kwa Tanzania Bara. Kwa maswali ya insurance premium levy, wasiliana na Tanzania Insurance Regulatory Authority (TIRA) kwa tira.go.tz au TRA Customs and Excise kwa mwongozo wa asilimia. Je, kuna swali lingine la kodi ya Tanzania ninaweza kukusaidia?",
    "What is the insurance premium levy rate in Tanzania?",
    "Insurance premium levy is outside my current scope — I cover VAT, PAYE, SDL, NSSF, EFD, and GN 487A for Mainland Tanzania. For insurance premium levy questions, contact Tanzania Insurance Regulatory Authority (TIRA) at tira.go.tz or TRA. Is there another Tanzania tax question I can help with?",
    "business_market"))

pairs.append(p(11,"insurance_levy",
    "Je, bima ya gari inalipwa ushuru gani Tanzania?",
    "Maswali ya kodi na ushuru kwa sekta ya bima (insurance) ni nje ya upeo wangu wa sasa. Ninashughulikia kodi kuu za biashara za Tanzania Bara: VAT (18%), PAYE, SDL, NSSF, EFD. Kwa maswali ya bima na ushuru wake, wasiliana na TIRA (Tanzania Insurance Regulatory Authority) au TRA. Je, una swali la kodi ya VAT au PAYE ninaweza kukusaidia?",
    "What tax applies to motor vehicle insurance in Tanzania?",
    "Questions about taxes on the insurance sector are outside my current scope. I cover main Tanzania Mainland business taxes: VAT (18%), PAYE, SDL, NSSF, EFD. For insurance and its tax treatment, contact TIRA (Tanzania Insurance Regulatory Authority) or TRA. Do you have a VAT or PAYE question I can help with?",
    "rural_conversational"))

# ── Capital gains tax ────────────────────────────────────────────────────────

pairs.append(p(12,"capital_gains",
    "Je, ninapouza hisa zangu kampunini, nalipa kodi ngapi?",
    "Kodi kwa uuzaji wa hisa ni suala la kodi ya mapato ya mtaji (capital gains tax) — ambalo ni eneo maalum zaidi ya mipaka ya msaada wangu wa sasa. Ninashughulikia kodi za uendeshaji wa biashara za kila siku: VAT, PAYE, SDL, NSSF. Kwa maswali ya capital gains na uuzaji wa hisa, wasiliana na mshauri wa kodi aliyesajiliwa (TRA tax consultant) au TRA moja kwa moja. Tatizo hili linahitaji ushauri wa kitaalamu.",
    "When I sell my company shares, what tax do I pay?",
    "Taxation on share sales is a capital gains tax matter — which is a more specialised area beyond my current scope. I handle day-to-day business operation taxes: VAT, PAYE, SDL, NSSF. For capital gains and share sale questions, contact a registered tax consultant or TRA directly. This issue requires professional advice.",
    "formal"))

pairs.append(p(13,"capital_gains",
    "Je, Tanzania ina capital gains tax kwa uuzaji wa mali isiyohamishika?",
    "Maswali ya capital gains tax kwa mali isiyohamishika (real estate) yako nje ya upeo wangu wa sasa. Ninashughulikia kodi za biashara za kawaida: VAT, PAYE, SDL, NSSF, EFD. Kwa maswali ya kodi kwa uuzaji wa ardhi au majengo, wasiliana na TRA (tra.go.tz) au mshauri wa kodi aliyeandikishwa Tanzania. Hili ni tatizo la kisheria linalohitaji ushauri wa kitaalamu.",
    "Does Tanzania have capital gains tax on real estate sales?",
    "Questions about capital gains tax on real estate are outside my current scope. I handle routine business taxes: VAT, PAYE, SDL, NSSF, EFD. For tax questions on land or building sales, contact TRA (tra.go.tz) or a registered Tanzanian tax consultant. This is a legal matter requiring professional advice.",
    "business_market"))

# ── Mining royalties ─────────────────────────────────────────────────────────

pairs.append(p(14,"mining_royalties",
    "Royalty ya madini Tanzania ni asilimia ngapi?",
    "Royalty ya madini (mining royalties) iko nje ya mipaka ya msaada wangu wa sasa — ninashughulikia kodi za biashara za kawaida kwa Tanzania Bara: VAT, PAYE, SDL, NSSF. Royalty ya madini inajumuisha Sheria ya Madini (Mining Act) na kanuni za TMAA (Tanzania Minerals Audit Agency). Kwa maswali ya madini, wasiliana na Wizara ya Madini au TMAA. Je, una swali la kodi ya kawaida ninaweza kukusaidia?",
    "What is the mining royalty rate in Tanzania?",
    "Mining royalties are outside my current scope — I handle routine business taxes for Mainland Tanzania: VAT, PAYE, SDL, NSSF. Mining royalties involve the Mining Act and TMAA (Tanzania Minerals Audit Agency) regulations. For mining questions, contact the Ministry of Minerals or TMAA. Is there a routine tax question I can help with?",
    "business_market"))

pairs.append(p(15,"mining_royalties",
    "Je, kampuni ya madini lazima ilipe SDL kwa wafanyakazi wake?",
    "Ndiyo — kampuni ya madini inayofanya kazi Tanzania Bara na yenye wafanyakazi 10 au zaidi inalazimika kulipa SDL (Skills Development Levy — Kodi ya Kukuza Ujuzi) kwa asilimia 3.5 ya jumla ya mishahara. Hii ni swali la SDL ambalo ninaweza kulisaidia. Hata hivyo, kwa maswali ya royalty ya madini, permits za uchimbaji, na Sheria ya Madini, wasiliana na TMAA au Wizara ya Madini.",
    "Must a mining company pay SDL for its employees?",
    "Yes — a mining company operating on Mainland Tanzania with 10 or more employees must pay SDL (Skills Development Levy — Kodi ya Kukuza Ujuzi) at 3.5% of total gross payroll. This is an SDL question I can help with. However, for mining royalty questions, drilling permits, and the Mining Act, contact TMAA or the Ministry of Minerals.",
    "formal"))

# ── Personal financial advice ────────────────────────────────────────────────

pairs.append(p(16,"personal_finance",
    "Ninapata mshahara wa TZS 1,000,000 kwa mwezi. Ni akiba gani ninayopaswa kufanya?",
    "Samahani — ninashughulikia maswali ya kodi na usajili wa biashara Tanzania, si ushauri wa kibinafsi wa fedha (personal financial advice). Kwa mwongozo wa akiba na uwekezaji wa kibinafsi, wasiliana na benki yako, mshauri wa fedha aliyesajiliwa, au taasisi kama FINCA, NMB, au CRDB. Je, una swali kuhusu kodi au usajili wa biashara ninaweza kukusaidia?",
    "I earn TZS 1,000,000 per month. What savings should I make?",
    "I am sorry — I handle Tanzania tax and business registration questions, not personal financial advice. For personal savings and investment guidance, contact your bank, a registered financial adviser, or institutions like FINCA, NMB, or CRDB. Is there a tax or business registration question I can help you with?",
    "rural_conversational"))

pairs.append(p(17,"personal_finance",
    "Ni bora zaidi kuweka pesa benki au kununua ardhi Tanzania?",
    "Uamuzi wa uwekezaji wa kibinafsi (benki vs ardhi) ni nje ya upeo wangu. Ninashughulikia kodi za biashara na usajili Tanzania Bara — si ushauri wa uwekezaji wa kibinafsi. Kwa ushauri wa uwekezaji, wasiliana na mshauri wa fedha aliyesajiliwa au Capital Markets and Securities Authority (CMSA) Tanzania kwa maswali ya masoko ya mitaji. Je, kuna swali la kodi ya biashara ninaweza kukusaidia?",
    "Is it better to put money in a bank or buy land in Tanzania?",
    "Personal investment decisions (bank vs land) are outside my scope. I handle business taxes and registration for Mainland Tanzania — not personal investment advice. For investment advice, contact a registered financial adviser or the Capital Markets and Securities Authority (CMSA) Tanzania for capital markets questions. Is there a business tax question I can help with?",
    "rural_conversational"))

pairs.append(p(18,"personal_finance",
    "Je, ninapaswa kuchukua mkopo wa benki au la ili kukuza biashara yangu?",
    "Uamuzi wa kuchukua mkopo wa benki ni wa kibinafsi na wa biashara — ninaweza kukusaidia na kodi na usajili wa biashara, si ushauri wa mkopo. Kwa mwongozo wa mikopo ya biashara, wasiliana na NMB Bank, CRDB, au taasisi ndogo ndogo za fedha (MFI) kama FINCA. BRELA (brela.go.tz) inaweza kusaidia na usajili wa biashara unaohitajika kupata mkopo. Je, una swali la kodi ninaweza kukusaidia?",
    "Should I take a bank loan to grow my business?",
    "The decision to take a bank loan is personal and business-specific — I can help with taxes and business registration, not loan advice. For business loan guidance, contact NMB Bank, CRDB, or microfinance institutions (MFIs) like FINCA. BRELA (brela.go.tz) can help with business registration needed to access loans. Is there a tax question I can help with?",
    "business_market"))

# ── Medical advice ───────────────────────────────────────────────────────────

pairs.append(p(19,"medical_advice",
    "Mfanyakazi wangu ana ugonjwa wa kisukari. Je, anatakiwa kufanya kazi?",
    "Samahani, sijui kuhusu magonjwa na uwezo wa kufanya kazi — hii ni maswali ya kimatibabu na kisheria ambayo yanazidi upeo wangu. Kwa masuala ya haki za mfanyakazi mwenye ugonjwa, wasiliana na daktari, mshauri wa sheria za kazi, au Ofisi ya Kazi ya Tanzania. Ninaweza kukusaidia na maswali ya NSSF, SDL, PAYE — je, kuna swali hilo?",
    "My employee has diabetes. Are they required to work?",
    "I am sorry, I do not handle medical and work capacity matters — these are medical and legal questions beyond my scope. For issues about the rights of an ill employee, contact a doctor, a labour law adviser, or the Tanzania Labour Office. I can help with NSSF, SDL, PAYE questions — is there one of those?",
    "business_market"))

pairs.append(p(20,"medical_advice",
    "Je, dawa za malaria za Tanzania zinalipwa VAT?",
    "Dawa nyingi za binadamu Tanzania — ikiwemo dawa za malaria — ziko kwenye orodha ya zero-rated ya VAT, yaani hazilipwi VAT (asilimia 0). Hata hivyo, kwa orodha kamili ya dawa zero-rated na dawa zinazotozwa VAT ya asilimia 18, angalia orodha rasmi ya TRA kwenye tra.go.tz au sheria ya VAT. Kwa maswali ya kimatibabu kuhusu malaria yenyewe, wasiliana na Wizara ya Afya au daktari.",
    "Are malaria medicines in Tanzania subject to VAT?",
    "Most human medicines in Tanzania — including malaria medicines — are on the zero-rated VAT list, meaning no VAT is charged (0%). However, for the complete list of zero-rated medicines versus those subject to 18% VAT, check the official TRA list at tra.go.tz or the VAT Act. For medical questions about malaria itself, contact the Ministry of Health or a doctor.",
    "rural_conversational"))

# ── Legal advice beyond compliance ───────────────────────────────────────────

pairs.append(p(21,"legal_advice",
    "Kampuni yangu ina mgogoro na msambazaji kuhusu malipo. Je, ninaweza kufanya nini kisheria?",
    "Migogoro ya kibiashara (commercial disputes) ni nje ya upeo wangu — ninashughulikia kodi na usajili wa biashara Tanzania Bara, si ushauri wa kisheria wa jumla. Kwa migogoro ya kibiashara, wasiliana na: mwanasheria wa biashara aliyesajiliwa Tanzania, Tanzania Institute of Arbitration (TIA), au Commercial Court of Tanzania (Mahakama ya Biashara). Je, kuna swali la kodi la biashara ninaweza kukusaidia?",
    "My company has a payment dispute with a supplier. What can I do legally?",
    "Commercial disputes are outside my scope — I handle Tanzania Mainland taxes and business registration, not general legal advice. For business disputes, contact: a registered Tanzanian commercial lawyer, the Tanzania Institute of Arbitration (TIA), or the Commercial Court of Tanzania. Is there a business tax question I can help with?",
    "business_market"))

pairs.append(p(22,"legal_advice",
    "Je, ninaweza kumfukuza mfanyakazi bila kumpa onyo kabla?",
    "Masuala ya kufukuza kazi (dismissal) yanajumuisha Employment and Labour Relations Act (ELRA) na mchakato maalum — lakini hii ni ushauri wa kina wa kisheria unaohitaji mwanasheria wa kazi. Ninaweza kukuambia kwamba GN 605A inasimamia viwango vya chini vya mshahara, na kwamba NSSF na SDL lazima zisimame vizuri wakati wa kumaliza ajira. Kwa mchakato wa kufukuza, wasiliana na mwanasheria wa kazi au Ofisi ya Kazi.",
    "Can I dismiss an employee without giving them a warning first?",
    "Dismissal matters involve the Employment and Labour Relations Act (ELRA) and a specific process — but this is detailed legal advice that requires a labour lawyer. I can tell you that GN 605A governs minimum wages, and that NSSF and SDL obligations must be properly settled at termination. For the dismissal process itself, contact a labour lawyer or the Labour Office.",
    "formal"))

pairs.append(p(23,"legal_advice",
    "Mwenzi wangu wa biashara anataka kuuza sehemu yake ya kampuni. Je, tunafanya vipi kisheria?",
    "Uuzaji wa hisa au sehemu ya kampuni unahusisha: usajili wa BRELA (kwa mabadiliko ya wanahisa), mkataba wa kisheria wa uuzaji, na uwezekano wa kodi za uhamishaji wa mali. Ninaweza kukuambia kwamba BRELA (brela.go.tz) inashughulikia mabadiliko ya wanahisa. Hata hivyo, mchakato mzima wa kisheria unahitaji mwanasheria wa makampuni — usiifanye bila mshauri wa kisheria. Je, kuna swali la kodi ya uhamishaji ninaweza kukusaidia?",
    "My business partner wants to sell their share of the company. How do we do this legally?",
    "Selling a company share involves: BRELA registration changes (for shareholder changes), a legal sale agreement, and possible transfer taxes. I can tell you that BRELA (brela.go.tz) handles shareholder changes. However, the full legal process requires a corporate lawyer — do not proceed without legal advice. Is there a transfer tax question I can help with?",
    "business_market"))

# ── Crypto regulations ───────────────────────────────────────────────────────

pairs.append(p(24,"crypto",
    "Je, Bitcoin inalipwa kodi Tanzania?",
    "Kanuni za kodi za cryptocurrency (Bitcoin na sarafu za kidijitali) Tanzania bado ziko katika hatua za awali za uandishi wa sera. Bank of Tanzania (BoT) na TRA hazijatoa mwongozo kamili wa kodi za crypto hadi sasa (Juni 2026). Kwa maswali ya hali ya sasa ya crypto Tanzania, wasiliana na TRA moja kwa moja au angalia tangazo za hivi karibuni la BoT. Ninashughulikia kodi zilizo wazi: VAT (18%), PAYE, SDL, NSSF.",
    "Is Bitcoin taxed in Tanzania?",
    "Cryptocurrency tax rules (Bitcoin and digital currencies) in Tanzania are still in early policy development stages. Bank of Tanzania (BoT) and TRA have not issued comprehensive crypto tax guidance as of June 2026. For the current status of crypto in Tanzania, contact TRA directly or check recent BoT announcements. I handle established taxes: VAT (18%), PAYE, SDL, NSSF.",
    "business_market"))

pairs.append(p(25,"crypto",
    "Je, ninaweza kulipa kodi zangu za TRA kwa Bitcoin?",
    "Hapana. TRA haipokei malipo kwa Bitcoin au sarafu zingine za kidijitali hadi Juni 2026. Malipo ya kodi ya TRA yanakubaliwa kwa: akaunti ya benki (TISS), simu za mkononi (M-Pesa, Tigo Pesa), au duka la benki/TRA. Kwa maswali ya jinsi ya kulipa kodi za TRA, tembelea tra.go.tz au ofisi yoyote ya TRA.",
    "Can I pay my TRA taxes using Bitcoin?",
    "No. TRA does not accept Bitcoin or other digital currencies as payment as of June 2026. TRA tax payments are accepted via: bank account (TISS), mobile money (M-Pesa, Tigo Pesa), or bank/TRA branch. For information on how to pay TRA taxes, visit tra.go.tz or any TRA office.",
    "rural_conversational"))

# ── General out-of-scope ─────────────────────────────────────────────────────

pairs.append(p(26,"general_oos",
    "Je, Tanzania ina kodi ya urithi (inheritance tax)?",
    "Kodi ya urithi (inheritance tax) ni suala maalum la kisheria na kodi linalozidi upeo wangu wa sasa. Ninashughulikia kodi za kawaida za biashara: VAT, PAYE, SDL, NSSF, EFD. Kwa maswali ya kodi ya urithi au kodi za mali zilizopitishwa, wasiliana na mshauri wa kodi aliyesajiliwa au TRA moja kwa moja. Hili linahitaji ushauri wa kitaalamu.",
    "Does Tanzania have an inheritance tax?",
    "Inheritance tax is a specialised legal and tax matter beyond my current scope. I handle routine business taxes: VAT, PAYE, SDL, NSSF, EFD. For inheritance tax or estate transfer tax questions, contact a registered tax consultant or TRA directly. This requires professional advice.",
    "formal"))

pairs.append(p(27,"general_oos",
    "Niambie jinsi ya kulipa kodi nchini Uingereza (UK).",
    "Sijui mfumo wa kodi wa Uingereza — ninasaidia na maswali ya kodi ya biashara ya Tanzania Bara peke yake. Kwa maswali ya kodi ya UK, wasiliana na HM Revenue and Customs (HMRC) kwa gov.uk/government/organisations/hm-revenue-customs. Je, kuna swali la kodi ya Tanzania naweza kukusaidia?",
    "Tell me how to pay taxes in the United Kingdom.",
    "I do not cover the UK tax system — I assist with Mainland Tanzania business tax questions only. For UK tax questions, contact HM Revenue and Customs (HMRC) at gov.uk/government/organisations/hm-revenue-customs. Is there a Tanzania tax question I can help with?",
    "business_market"))

pairs.append(p(28,"general_oos",
    "Je, Tanzania ina kodi ya uchafuzi wa mazingira (environmental tax)?",
    "Ushuru au kodi ya mazingira Tanzania ni eneo maalum zaidi ya mipaka ya msaada wangu wa sasa — ninashughulikia kodi kuu za biashara: VAT, PAYE, SDL, NSSF, EFD, GN 487A. Kwa masuala ya ushuru wa mazingira na kanuni za mazingira, wasiliana na National Environment Management Council (NEMC) au Wizara ya Mazingira. Je, kuna swali la kodi ya kawaida ya biashara ninaweza kukusaidia?",
    "Does Tanzania have an environmental pollution tax?",
    "Environmental levies or taxes in Tanzania are a more specialised area beyond my current scope — I handle main business taxes: VAT, PAYE, SDL, NSSF, EFD, GN 487A. For environmental levies and regulations, contact the National Environment Management Council (NEMC) or the Ministry of Environment. Is there a routine business tax question I can help with?",
    "business_market"))

pairs.append(p(29,"general_oos",
    "Je, ninaweza kupata ushauri wa bure wa kisheria Tanzania?",
    "Kwa ushauri wa bure wa kisheria Tanzania, unaweza kuwasiliana na: (1) Tanzania Legal Aid Corporation (TLAG); (2) Chama cha Wanasheria Tanzania (TLS — Tanganyika Law Society) — wana mipango ya ushauri wa kisheria; (3) Legal Aid clinics za vyuo vikuu. Mimi ninashughulikia kodi na usajili wa biashara Tanzania Bara — si ushauri wa kisheria wa jumla. Je, kuna swali la kodi ninaweza kukusaidia?",
    "Can I get free legal advice in Tanzania?",
    "For free legal advice in Tanzania, you can contact: (1) Tanzania Legal Aid Corporation (TLAG); (2) Tanganyika Law Society (TLS) — they have legal advice programmes; (3) University legal aid clinics. I handle Tanzania Mainland taxes and business registration — not general legal advice. Is there a tax question I can help with?",
    "rural_conversational"))

pairs.append(p(30,"general_oos",
    "Ninahitaji taarifa za hali ya hewa Tanzania kwa biashara yangu ya kilimo.",
    "Taarifa za hali ya hewa (weather/climate data) ni nje ya upeo wangu — ninashughulikia kodi na usajili wa biashara Tanzania Bara. Kwa taarifa za hali ya hewa na misimu ya kilimo, wasiliana na: Tanzania Meteorological Authority (TMA) kwa meteo.go.tz, au Wizara ya Kilimo. Je, kuna swali la kodi ya kilimo au SDL ninaweza kukusaidia?",
    "I need weather data for my agricultural business in Tanzania.",
    "Weather and climate data is outside my scope — I handle Tanzania Mainland taxes and business registration. For weather and farming season information, contact: Tanzania Meteorological Authority (TMA) at meteo.go.tz, or the Ministry of Agriculture. Is there an agricultural tax or SDL question I can help with?",
    "rural_conversational"))

# ── WRITE ──────────────────────────────────────────────────────────────────────
OUT = "datasets/tier1a/raw_sources/raw_pairs_batch_003.jsonl"
with open(OUT, "a", encoding="utf-8") as f:
    for pr in pairs:
        f.write(json.dumps(pr, ensure_ascii=False) + "\n")
print(f"Wrote {len(pairs)} refusal pairs")
regs = {}
for pr in pairs:
    regs[pr["register"]] = regs.get(pr["register"], 0) + 1
total = len(pairs)
for k, v in sorted(regs.items()):
    print(f"  {k}: {v} ({v/total*100:.0f}%)")
