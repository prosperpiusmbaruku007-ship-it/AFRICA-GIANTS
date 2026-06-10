#!/usr/bin/env python3
"""
batch_006 part 6: out_of_corpus_refusal (20) + disambiguation_mixed (15) + rural_compliance (15)
IDs: b006_refusal_001-020, b006_disambig_001-015, b006_rural_001-015
Append to: datasets/tier1a/raw_sources/raw_pairs_batch_006.jsonl
"""
import json, os

OUT = "datasets/tier1a/raw_sources/raw_pairs_batch_006.jsonl"

SRC_TRA = "https://www.tra.go.tz/page/value-added-tax"
SRC_PAYE = "https://www.tra.go.tz/page/pay-as-you-earn-paye"
SRC_BRELA = "https://www.brela.go.tz/"
SRC_NSSF = "https://www.nssf.or.tz/"
SRC_GN487 = "https://tanzlii.org/akn/tz/act/gn/2025/487a/eng@2025-07-28"
SRC_SDL = "https://www.tra.go.tz/page/skills-development-levy"

def p(id_, subdomain, q_sw, a_sw, q_en, a_en, register, pair_type,
      src=SRC_TRA, src_name="TRA - Value Added Tax", eff="2025-07-01", decay="annual"):
    return {
        "id": id_, "domain": "tier1a", "subdomain": subdomain,
        "question_sw": q_sw, "answer_sw": a_sw,
        "question_en": q_en, "answer_en": a_en,
        "primary_source_url": src, "primary_source_name": src_name,
        "source_type": "government_portal", "effective_date": eff,
        "decay_risk": decay,
        "next_review_trigger": "Finance Act or regulatory update",
        "verified_by": "founder_self_review", "verified_date": "2026-06-10",
        "register": register, "pair_type": pair_type, "eval_set": False
    }

pairs = [

# ================================================================
# OUT-OF-CORPUS REFUSALS — 20 pairs
# ================================================================

p("b006_refusal_001", "out_of_corpus_refusal",
  "Kiwango cha ushuru wa forodha (import duty) kwa televisheni kutoka China ni ngapi?",
  "Sina uhakika wa kiwango maalum cha ushuru wa forodha kwa televisheni. Viwango vya forodha vinategemea HS Code ya bidhaa na ratiba ya forodha ya Tanzania (EAC Common External Tariff). Thibitisha na TRA (Idara ya Forodha) au wakala wa usafirishaji (customs agent) aliyesajiliwa.",
  "What is the import duty rate for a television set from China?",
  "I am not certain of the specific import duty rate for television sets. Duty rates depend on the HS Code of the goods and the Tanzania customs tariff schedule (EAC Common External Tariff). Verify with TRA (Customs Department) or a registered customs agent.",
  "business_market", "out_of_corpus_refusal"),

p("b006_refusal_002", "out_of_corpus_refusal",
  "Kampuni ya madini (mining company) inalipa kodi gani maalum Tanzania?",
  "Kampuni za madini zina mfumo maalum wa kodi na vivutio vya uwekezaji tofauti na kampuni za kawaida. Kodi hizi zinasimamia na Sheria ya Madini na mikataba ya ubia wa serikali (mining agreements). Sina uhakika wa viwango vya sasa. Thibitisha na TRA, Wizara ya Madini, au mshauri wa kodi wa sekta ya madini.",
  "What special taxes does a mining company pay in Tanzania?",
  "Mining companies have a specialized tax and investment incentive framework different from regular companies. These are governed by the Mining Act and government partnership agreements (mining agreements). I am not certain of current rates. Verify with TRA, the Ministry of Minerals, or a mining sector tax advisor.",
  "formal", "out_of_corpus_refusal"),

p("b006_refusal_003", "out_of_corpus_refusal",
  "Mapato ya kilimo ya mkulima binafsi — yanalazimu kodi ya mapato Tanzania?",
  "Matibabu ya kodi ya mapato ya kilimo Tanzania ni ngumu na yanategemea kiwango cha mapato na muundo wa biashara. Wakulima wadogo wanaweza kuwa na hali tofauti na wazalishaji wakubwa wa kibiashara. Sina uhakika wa masharti ya sasa. Thibitisha na TRA kuhusu hali yako maalum ya kilimo.",
  "Does a private farmer's agricultural income require income tax in Tanzania?",
  "The income tax treatment of agricultural income in Tanzania is complex and depends on income levels and business structure. Smallholder farmers may have different treatment than large commercial producers. I am not certain of current rules. Verify with TRA about your specific farming situation.",
  "rural_conversational", "out_of_corpus_refusal"),

p("b006_refusal_004", "out_of_corpus_refusal",
  "Je, mwanachama wa VICOBA analipa kodi kwa faida za mkopo wa VICOBA?",
  "Matibabu ya kodi ya mapato ya VICOBA na faida za mkopo wake ni suala ambalo halijajadiliwa wazi katika kanuni za TRA za kawaida. VICOBA ni mfumo wa akiba wa jamii ambao mara nyingi unaonekana kama wa kibinafsi. Sina uhakika wa mwelekeo wa kodi wa sasa kwa VICOBA. Thibitisha na TRA.",
  "Does a VICOBA member pay tax on VICOBA loan income?",
  "The tax treatment of VICOBA income and loan returns is a matter not clearly addressed in standard TRA regulations. VICOBA is a community savings system often treated as informal. I am not certain of the current tax position on VICOBA. Verify with TRA.",
  "rural_conversational", "out_of_corpus_refusal"),

p("b006_refusal_005", "out_of_corpus_refusal",
  "Kampuni ya bima inalipa kodi gani maalum Tanzania — premium tax ipo?",
  "Kampuni za bima zina mfumo maalum wa kodi na usimamizi wa TIRA (Tanzania Insurance Regulatory Authority). Premium tax na tozo maalum za bima zinaweza kutumika. Sina uhakika wa viwango vya sasa. Thibitisha na TRA au TIRA.",
  "What special taxes does an insurance company pay in Tanzania — is there a premium tax?",
  "Insurance companies have a specialized tax framework regulated by TIRA (Tanzania Insurance Regulatory Authority). Premium taxes and special insurance levies may apply. I am not certain of current rates. Verify with TRA or TIRA.",
  "formal", "out_of_corpus_refusal"),

p("b006_refusal_006", "out_of_corpus_refusal",
  "Gari la zamani linalouza Tanzania — ushuru wa biashara (excise duty) ni ngapi?",
  "Ushuru wa biashara (excise duty) wa magari ya zamani (used vehicles) unategemea sana umri wa gari, CIF value, na HS Code. EAC Common External Tariff na excise duty schedule zinatoa viwango maalum. Sina uhakika wa viwango vya sasa. Thibitisha na TRA (Customs) au wakala wa usafirishaji.",
  "A used car being sold in Tanzania — what is the applicable excise duty?",
  "Excise duty on used vehicles depends heavily on the vehicle's age, CIF value, and HS Code. The EAC Common External Tariff and excise duty schedule specify the rates. I am not certain of current rates. Verify with TRA (Customs) or a shipping/customs agent.",
  "business_market", "out_of_corpus_refusal"),

p("b006_refusal_007", "out_of_corpus_refusal",
  "Land rent (kodi ya ardhi) kwa ekari moja Tanzania — ni TZS ngapi kwa mwaka?",
  "Land rent (tozo za ardhi) zinatofautiana sana kulingana na: eneo la ardhi (Dar es Salaam vs mikoani), mji au kijiji, na matumizi ya ardhi (biashara, kilimo, makazi). Sina uhakika wa viwango vya sasa. Thibitisha na Halmashauri yako ya Wilaya au Wizara ya Ardhi.",
  "Land rent for one acre in Tanzania — how much per year in TZS?",
  "Land rent varies significantly depending on: location (Dar es Salaam vs upcountry), urban or village classification, and land use type (commercial, agricultural, residential). I am not certain of current rates. Verify with your District Council or the Ministry of Lands.",
  "rural_conversational", "out_of_corpus_refusal"),

p("b006_refusal_008", "out_of_corpus_refusal",
  "Tozo za TPA (Tanzania Ports Authority) kwa kontena moja — ni kiasi gani?",
  "Tozo za TPA zinategemea aina ya mzigo, ukubwa wa kontena, na muda wa kuhifadhiwa bandarini. Sina uhakika wa tozo za sasa. Thibitisha na TPA moja kwa moja au wakala wa usafirishaji wako.",
  "TPA (Tanzania Ports Authority) fees for one container — how much?",
  "TPA fees depend on cargo type, container size, and storage duration at the port. I am not certain of current rates. Verify directly with TPA or your shipping agent.",
  "business_market", "out_of_corpus_refusal"),

p("b006_refusal_009", "out_of_corpus_refusal",
  "Je, kampuni ya utalii (safari company) ina mfumo maalum wa VAT Tanzania?",
  "Kampuni za utalii zinaweza kuwa na mfumo maalum wa VAT — hasa kwa huduma za utalii zinazotolewa kwa wageni (inbound tourism). Inaweza kustahili zero-rating kwa baadhi ya huduma. Sina uhakika wa kanuni za sasa maalum. Thibitisha na TRA au Tanzania Tourism Board (TTB).",
  "Does a safari/tourism company have a special VAT framework in Tanzania?",
  "Tourism companies may have a special VAT framework — especially for tourism services provided to foreign visitors (inbound tourism). Some services may qualify for zero-rating. I am not certain of current specific rules. Verify with TRA or Tanzania Tourism Board (TTB).",
  "business_market", "out_of_corpus_refusal"),

p("b006_refusal_010", "out_of_corpus_refusal",
  "Chama cha ushirika (cooperative society) kinalipa kodi gani Tanzania?",
  "Vyama vya ushirika vina mfumo maalum wa ushirika na kodi. Viwango vya kodi ya mapato na msamaha maalum unaotumika kwa SACCOS na ushirika wa kilimo unategemea muundo na mapato ya kila chama. Sina uhakika wa viwango vya sasa. Thibitisha na TRA au Msajili wa Vyama vya Ushirika.",
  "What taxes does a cooperative society pay in Tanzania?",
  "Cooperative societies have a special legal and tax framework. Income tax rates and special exemptions applicable to SACCOs and agricultural cooperatives depend on each society's structure and income. I am not certain of current rules. Verify with TRA or the Registrar of Cooperatives.",
  "formal", "out_of_corpus_refusal"),

p("b006_refusal_011", "out_of_corpus_refusal",
  "Kampuni ya nje inayofanya biashara Tanzania tu kwa mtandao — ina wajibu wa kusajiliwa Tanzania?",
  "Hili ni suala la kisheria la 'permanent establishment' (PE). Kampuni ya nje inayotoa huduma Tanzania kwa mtandao tu inaweza au isihitajike kusajiliwa Tanzania kulingana na PE analysis. Sina uhakika wa mwelekeo halisi wa sheria ya Tanzania kwa kesi hii. Thibitisha na mwanasheria wa biashara au TRA.",
  "A foreign company doing business in Tanzania only via internet — must it register in Tanzania?",
  "This is a legal 'permanent establishment' (PE) question. A foreign company providing services in Tanzania only via internet may or may not need to register in Tanzania depending on the PE analysis. I am not certain of Tanzania's current legal position on this. Verify with a business lawyer or TRA.",
  "formal", "out_of_corpus_refusal"),

p("b006_refusal_012", "out_of_corpus_refusal",
  "Je, mwajiri anaweza kupunguza gharama za NSSF kutoka kodi ya mapato ya makampuni?",
  "Michango ya NSSF ya mwajiri kwa kawaida inaweza kuchukuliwa kama gharama inayopunguzwa kwa kodi ya mapato ya makampuni — lakini masharti maalum yanategemea sheria ya kodi ya Tanzania na muundo wa malipo. Thibitisha na mshauri wa kodi wa kodi ya makampuni au TRA.",
  "Can an employer deduct NSSF contributions from corporate income tax?",
  "Employer NSSF contributions can generally be treated as a deductible expense for corporate income tax purposes — but specific conditions depend on Tanzania's corporate tax law and payment structure. Verify with a corporate tax advisor or TRA.",
  "formal", "out_of_corpus_refusal"),

p("b006_refusal_013", "out_of_corpus_refusal",
  "Gawio (dividends) linalolipwa kwa mwanachama wa kampuni mgeni — WHT ni ngapi?",
  "Gawio kwa wanahisa wa nje ya nchi (non-resident dividends) linabeba withholding tax. Kiwango cha kawaida ni 10% kwa wanahisa wasio na makazi — lakini DTA inaweza kupunguza hadi chini. Sina uhakika wa viwango vyote vya sasa. Thibitisha na TRA au mshauri wa kodi wa kimataifa.",
  "Dividends paid to a foreign company shareholder — what is the WHT rate?",
  "Dividends to non-resident shareholders carry withholding tax. The standard rate for non-resident shareholders is typically 10% — but a DTA may reduce this. I am not certain of all current rates. Verify with TRA or an international tax advisor.",
  "formal", "out_of_corpus_refusal"),

p("b006_refusal_014", "out_of_corpus_refusal",
  "Ununuzi wa hisa za kampuni ya Tanzania iliyoorodheshwa DSE — kuna kodi?",
  "Miamala ya hisa kwenye Dar es Salaam Stock Exchange (DSE) inaweza kuwa na kodi ya mauzo ya hisa (capital gains tax) au msamaha maalum. Mfumo wa kodi wa soko la hisa Tanzania una kanuni maalum. Sina uhakika wa mwelekeo wa sasa. Thibitisha na DSE, TRA, au mshauri wa fedha.",
  "Buying shares in a DSE-listed Tanzanian company — is there a tax?",
  "Share transactions on the Dar es Salaam Stock Exchange (DSE) may be subject to capital gains tax or special exemptions. The tax framework for Tanzania's stock market has specific rules. I am not certain of the current position. Verify with DSE, TRA, or a financial advisor.",
  "formal", "out_of_corpus_refusal"),

p("b006_refusal_015", "out_of_corpus_refusal",
  "Mkulima anayeuza miti (timber) kutoka msitu wake — ana wajibu gani wa kodi?",
  "Uuzaji wa miti kutoka misitu una mfumo maalum wa usimamizi wa mazingira na kodi. Inaweza kuhusisha: leseni za ukataji wa misitu (TFS — Tanzania Forest Service), kodi za mazao ya misitu, na pengine kodi ya mapato. Sina uhakika wa masharti yote ya sasa. Thibitisha na TFS na TRA.",
  "A farmer selling timber from their forest — what tax obligations do they have?",
  "Selling timber from forests has a specialized environmental management and tax framework. This may involve: timber harvesting licences (TFS — Tanzania Forest Service), forest produce levies, and possibly income tax. I am not certain of all current requirements. Verify with TFS and TRA.",
  "rural_conversational", "out_of_corpus_refusal"),

p("b006_refusal_016", "out_of_corpus_refusal",
  "Biashara ya pombe za kienyeji (pombe) — leseni na kodi zinahitajika?",
  "Utengenezaji na uuzaji wa pombe za kienyeji unasimamia chini ya sheria ya pombe Tanzania na mamlaka za serikali za mitaa. Leseni zinahitajika kutoka Halmashauri ya Wilaya. Kodi za biashara zinahusu hali ya usajili wa biashara na kiwango cha mapato. Sina uhakika wa masharti yote. Thibitisha na Halmashauri yako ya Wilaya.",
  "A traditional brew business — what licences and taxes are required?",
  "Manufacturing and selling traditional brews is regulated under Tanzania's liquor laws and local government authorities. Licences are required from the District Council. Business taxes depend on registration status and income levels. I am not certain of all requirements. Verify with your District Council.",
  "rural_conversational", "out_of_corpus_refusal"),

p("b006_refusal_017", "out_of_corpus_refusal",
  "Tozo za TRL (Tanzania Railways Limited) kwa mzigo — ni ngapi?",
  "Tozo za usafiri wa reli (TRL) zinaathiriwa na aina ya mzigo, uzito, na umbali. Sina uhakika wa tozo za sasa. Wasiliana na TRL moja kwa moja kwa orodha ya sasa ya bei.",
  "TRL (Tanzania Railways Limited) freight charges — how much?",
  "Rail freight charges (TRL) vary by cargo type, weight, and distance. I am not certain of current rates. Contact TRL directly for the current price list.",
  "business_market", "out_of_corpus_refusal"),

p("b006_refusal_018", "out_of_corpus_refusal",
  "Mfumo wa pension ya serikali (Government Pension Fund — GEPF) — jinsi unavyofanya kazi?",
  "GEPF (Government Employees Provident Fund) ni mfumo wa pensheni kwa watumishi wa serikali. Ina kanuni tofauti na NSSF (ambayo ni kwa sekta binafsi). Sina uhakika wa masharti ya sasa ya GEPF — kutoa mchango, faida, na kanuni za kustaafu. Thibitisha na GEPF au Hazina.",
  "The Government Pension Fund (GEPF) — how does it work?",
  "GEPF (Government Employees Provident Fund) is a pension scheme for government employees. It has different rules from NSSF (which covers the private sector). I am not certain of current GEPF rules — contributions, benefits, and retirement conditions. Verify with GEPF or the Treasury.",
  "formal", "out_of_corpus_refusal"),

p("b006_refusal_019", "out_of_corpus_refusal",
  "Kampuni ya usafirishaji wa baharini (shipping company) inalipa kodi gani Tanzania?",
  "Makampuni ya usafirishaji wa baharini yana mfumo maalum wa kodi wa kimataifa. Tanzania ina maeneo ya ushirikiano na vyama vya usafirishaji wa baharini. Sina uhakika wa mfumo wa kodi wa sasa kwa shipping companies Tanzania. Thibitisha na TRA au mwanasheria wa usafirishaji wa baharini.",
  "What taxes does a maritime shipping company pay in Tanzania?",
  "Maritime shipping companies have a specialized international tax framework. Tanzania has cooperation arrangements with maritime shipping associations. I am not certain of the current tax framework for shipping companies in Tanzania. Verify with TRA or a maritime lawyer.",
  "formal", "out_of_corpus_refusal"),

p("b006_refusal_020", "out_of_corpus_refusal",
  "Je, kampuni inaweza kupata msamaha wa kodi Tanzania kupitia TIC?",
  "Ndiyo — TIC (Tanzania Investment Centre) inatoa vivutio vya uwekezaji ikiwa ni pamoja na uwezekano wa msamaha au kupunguziwa kodi. Hata hivyo, vivutio maalum vinategemea aina ya uwekezaji, kiasi cha mtaji, na mikataba ya TIC. Sina uhakika wa vivutio vya sasa vinavyopatikana. Thibitisha na TIC moja kwa moja au mshauri wa uwekezaji.",
  "Can a company obtain tax exemptions in Tanzania through TIC?",
  "Yes — TIC (Tanzania Investment Centre) offers investment incentives including possible tax exemptions or reductions. However, specific incentives depend on the type of investment, capital amount, and TIC agreements. I am not certain of currently available incentives. Verify directly with TIC or an investment advisor.",
  "formal", "out_of_corpus_refusal"),

# ================================================================
# DISAMBIGUATION MIXED — 15 pairs
# ================================================================

p("b006_disambig_001", "disambiguation_mixed",
  "TIN (Tax Identification Number) na leseni ya biashara — ni vitu sawa?",
  "Hapana. TIN (Nambari ya Utambulisho wa Kodi) ni nambari ya TRA inayotambulisha mlipa kodi — inatumika kwa kodi zote. Leseni ya biashara ni hati inayoruhusiwa biashara kufanya shughuli fulani — inatoka kwa halmashauri au mamlaka husika. Biashara inahitaji ZOTE MBILI: TIN kwa TRA na leseni ya biashara kwa halmashauri.",
  "TIN (Tax Identification Number) and a business licence — are they the same thing?",
  "No. A TIN (Tax Identification Number) is a TRA number that identifies a taxpayer — used for all taxes. A business licence is a document permitting a business to conduct specific activities — it comes from the local council or relevant authority. A business needs BOTH: a TIN for TRA and a business licence from the council.",
  "business_market", "disambiguation",
  SRC_TRA, "TRA - Tax Administration"),

p("b006_disambig_002", "disambiguation_mixed",
  "TANePS na NeST — Tanzania inayotumia ipi sasa?",
  "NeST (National e-Procurement System) — si TANePS. TANePS ilikomeshwa rasmi tarehe 31 Desemba 2023 na ilikuwa ya lazima kutoka 1 Julai 2023. Kuanzia 1 Julai 2023, taasisi 1,147 za manunuzi zinalazimika kutumia NeST peke yake. TANePS haipo tena — kamwe usiirejee kwa mazingira ya sasa.",
  "TANePS and NeST — which one is Tanzania using now?",
  "NeST (National e-Procurement System) — not TANePS. TANePS was officially decommissioned on 31 December 2023 and NeST became mandatory from 1 July 2023. From 1 July 2023, 1,147 procuring entities are required to use NeST only. TANePS no longer exists — never reference it in any current context.",
  "formal", "adversarial",
  "https://www.ppra.go.tz/", "PPRA - NeST Procurement System", "2023-07-01", "event_triggered"),

p("b006_disambig_003", "disambiguation_mixed",
  "EFD receipt na VAT invoice — ni hati moja au mbili tofauti?",
  "Ni hati MBILI TOFAUTI. VAT invoice: hati rasmi ya kibiashara inayotolewa na msambazaji kwa mnunuzi ikiwa na maelezo kamili ya VAT (jina, TIN, kiasi, kiwango). EFD receipt: hati inayotolewa na mashine ya EFD (Electronic Fiscal Device) inayothibitisha mauzo ya biashara — mara nyingi inajumuisha maelezo ya VAT pia. Kwa biashara zilizosajiliwa VAT, EFD receipt ndiyo nyaraka inayothibitishwa na TRA. Zote mbili zinaweza kuhitajika katika hali tofauti.",
  "EFD receipt and VAT invoice — are they one document or two different ones?",
  "They are TWO DIFFERENT documents. VAT invoice: a formal commercial document issued by a supplier to a buyer with full VAT details (name, TIN, amount, rate). EFD receipt: a document issued by an EFD machine (Electronic Fiscal Device) confirming a business sale — often includes VAT details too. For VAT-registered businesses, the EFD receipt is TRA's verified document. Both may be required in different situations.",
  "formal", "disambiguation"),

p("b006_disambig_004", "disambiguation_mixed",
  "Usajili wa VAT na usajili wa TIN — ni usajili mmoja au tofauti?",
  "Ni usajili MBILI TOFAUTI ingawa zinahusiana. TIN registration: inayohitajika kwa kila mlipa kodi — biashara, mtu binafsi, au shirika. Inafanywa mara moja. VAT registration: inayohitajika pale biashara inafikia kizingiti cha TZS 200M/mwaka au TZS 100M/miezi 6. Inafanywa baada ya kufikia kizingiti. Biashara nyingi zina TIN lakini hazina usajili wa VAT (bado hazijafika kizingiti).",
  "VAT registration and TIN registration — are they the same or different?",
  "They are TWO DIFFERENT registrations although related. TIN registration: required for every taxpayer — business, individual, or organization. Done once. VAT registration: required when a business reaches the TZS 200M/year or TZS 100M/6-month threshold. Done after reaching the threshold. Many businesses have a TIN but no VAT registration (they have not yet reached the threshold).",
  "business_market", "disambiguation"),

p("b006_disambig_005", "disambiguation_mixed",
  "PAYE na kodi ya mapato ya makampuni (corporate tax) — ni kodi moja au tofauti?",
  "Ni kodi MBILI TOFAUTI. PAYE (Pay As You Earn): kodi ya mapato ya MFANYAKAZI inayokatwa na mwajiri. Corporate tax (kodi ya mapato ya makampuni): kodi inayolipwa na KAMPUNI juu ya faida yake. Mfanyakazi analipa PAYE; kampuni inalipa corporate tax. Kampuni pia inalazimika kukusanya na kuwasilisha PAYE kwa niaba ya wafanyakazi wake.",
  "PAYE and corporate income tax — are they the same tax or different?",
  "They are TWO DIFFERENT taxes. PAYE (Pay As You Earn): income tax on EMPLOYEE earnings deducted by the employer. Corporate tax: tax paid by the COMPANY on its profits. The employee pays PAYE; the company pays corporate tax. The company is also required to collect and remit PAYE on behalf of its employees.",
  "business_market", "disambiguation", SRC_PAYE, "TRA - PAYE"),

p("b006_disambig_006", "disambiguation_mixed",
  "NSSF na NHIF — ni mifumo tofauti au moja?",
  "Ni mifumo MIWILI TOFAUTI ya hifadhi ya jamii. NSSF (National Social Security Fund): pensheni na manufaa ya muda mrefu — inafadhiliwa na michango ya mwajiri (10%) na mfanyakazi (10%). NHIF (National Health Insurance Fund): bima ya afya — inafadhiliwa kwa njia tofauti. Wafanyakazi wa sekta binafsi kawaida wanchangia NSSF; watumishi wa serikali wanaweza kuchangia NHIF. Ni mifumo miwili tofauti yenye mamlaka tofauti.",
  "NSSF and NHIF — are they different or the same scheme?",
  "They are TWO DIFFERENT social security systems. NSSF (National Social Security Fund): pension and long-term benefits — funded by employer (10%) and employee (10%) contributions. NHIF (National Health Insurance Fund): health insurance — funded differently. Private sector employees typically contribute to NSSF; government employees may contribute to NHIF. They are two separate systems with different authorities.",
  "business_market", "disambiguation", SRC_NSSF, "NSSF"),

p("b006_disambig_007", "disambiguation_mixed",
  "BRELA na halmashauri (LGA) — leseni kutoka kwa wapi?",
  "Kuna leseni mbili tofauti zinazohitajika. BRELA (Business Registrations and Licensing Agency): inasajili KAMPUNI au BIASHARA kwa kitaifa — unasajili jina, wamiliki, muundo wa kisheria. LGA (Halmashauri ya Wilaya): inatoa LESENI ya biashara ya kufanya shughuli katika eneo husika. BRELA inatoa usajili wa kitaifa; halmashauri inatoa leseni ya eneo. Zote mbili zinahitajika.",
  "BRELA and local council (LGA) — which one issues a business licence?",
  "Two different registrations are required. BRELA (Business Registrations and Licensing Agency): registers the COMPANY or BUSINESS at national level — you register the name, owners, legal structure. LGA (District Council): issues the BUSINESS LICENCE to operate in a specific area. BRELA provides national registration; the council provides area-specific licensing. Both are required.",
  "business_market", "disambiguation", SRC_BRELA, "BRELA"),

p("b006_disambig_008", "disambiguation_mixed",
  "Withholding tax (WHT) na PAYE — kila moja inatumika lini?",
  "PAYE: inatumiwa kwa WAFANYAKAZI WALIOHIRIWA (employed persons) — mwajiri anakata na kuwasilisha TRA. WHT: inatumiwa kwa MALIPO KWA WASIO WAFANYAKAZI (payments to contractors, non-residents, directors) — mlipaji anakata na kuwasilisha TRA. Kama mtu ana mkataba wa ajira = PAYE. Kama analipwa kwa ankara ya huduma au ni mgeni asiye mwajiriwa = WHT. Angalia muundo wa uhusiano.",
  "Withholding tax (WHT) and PAYE — when does each apply?",
  "PAYE: applies to HIRED EMPLOYEES (employed persons) — employer deducts and remits to TRA. WHT: applies to PAYMENTS TO NON-EMPLOYEES (payments to contractors, non-residents, directors) — the payer deducts and remits to TRA. If a person has an employment contract = PAYE. If paid by service invoice or is a non-employed non-resident = WHT. Check the relationship structure.",
  "formal", "disambiguation", SRC_PAYE, "TRA - PAYE"),

p("b006_disambig_009", "disambiguation_mixed",
  "SDL na WCF — tofauti yao kuu nini na zinalipwa wapi?",
  "SDL (Skills Development Levy, 3.5%): ushuru wa mafunzo ya ujuzi — inalipwa TRA na mwajiri, kwa wafanyakazi ≥10. WCF (Workers Compensation Fund, 0.5%): bima ya ajali za kazi — inalipwa WCF (taasisi tofauti), kwa wafanyakazi wote (kizingiti kinategemea sekta). Walipwa: TRA vs WCF. Lengo: mafunzo vs bima ya ajali. Viwango: 3.5% vs 0.5%.",
  "SDL and WCF — what is their key difference and where are they paid?",
  "SDL (Skills Development Levy, 3.5%): a skills training levy — paid to TRA by the employer, for ≥10 employees. WCF (Workers Compensation Fund, 0.5%): workplace accident insurance — paid to WCF (a separate institution), for all employees (threshold depends on sector). Recipients: TRA vs WCF. Purpose: training vs accident insurance. Rates: 3.5% vs 0.5%.",
  "business_market", "disambiguation", SRC_SDL, "TRA - SDL"),

p("b006_disambig_010", "disambiguation_mixed",
  "OSHA na WCF — vinahusu usalama wa kazi lakini ni tofauti gani?",
  "OSHA (Occupational Safety and Health Authority): inasimamia USALAMA mahali pa kazi — ukaguzi wa mahali pa kazi, mafunzo ya usalama, usajili wa mwajiri wa OSHA. WCF (Workers Compensation Fund): inatoa FIDIA ya pesa kwa mfanyakazi aliyeumia kazini. OSHA = kuzuia ajali; WCF = kulipa fidia baada ya ajali. Ni taasisi mbili tofauti lakini zinafanya kazi pamoja katika kuzuia na kukabiliana na ajali za kazi.",
  "OSHA and WCF — both related to workplace safety but what is the difference?",
  "OSHA (Occupational Safety and Health Authority): oversees WORKPLACE SAFETY — workplace inspections, safety training, employer OSHA registration. WCF (Workers Compensation Fund): provides CASH COMPENSATION to injured workers. OSHA = accident prevention; WCF = paying compensation after an accident. They are two different institutions that work together in preventing and responding to workplace accidents.",
  "formal", "disambiguation", "https://www.osha.go.tz/", "OSHA Tanzania"),

p("b006_disambig_011", "disambiguation_mixed",
  "Tax clearance certificate na TIN certificate — ni tofauti gani?",
  "TIN certificate: hati inayothibitisha una TIN (Tax Identification Number) — inathibitisha umesajiliwa na TRA. Inatolewa baada ya usajili wa TIN. Tax clearance certificate: hati inayothibitisha huna deni la kodi lililolipwa — inaonyesha una hali nzuri ya kodi. Inatolewa baada ya kulipa kodi zote zinazodaiwa. TIN = utambulisho; Tax clearance = uthibitisho wa uzuri wa kodi.",
  "Tax clearance certificate and TIN certificate — what is the difference?",
  "TIN certificate: a document confirming you have a TIN (Tax Identification Number) — it confirms you are registered with TRA. Issued after TIN registration. Tax clearance certificate: a document confirming you have no outstanding tax debt — it shows your tax standing is clean. Issued after paying all owed taxes. TIN = identity; Tax clearance = confirmation of good tax standing.",
  "business_market", "disambiguation"),

p("b006_disambig_012", "disambiguation_mixed",
  "P9 form na P9A form — ni tofauti gani?",
  "P9 form: hati ya muhtasari wa kodi ya kila mwaka inayotolewa na mwajiri kwa mfanyakazi — inaonyesha jumla ya mapato na PAYE iliyokatwa mwaka mzima. Inatakiwa kabla ya 31 Machi. P9A: ni toleo la zamani au fomu ya ziada kwa hali maalum — matumizi yake yanategemea kanuni za sasa za TRA. Thibitisha fomu inayohitajika sasa na TRA.",
  "P9 form and P9A form — what is the difference?",
  "P9 form: an annual tax summary document issued by the employer to the employee — showing total income and PAYE deducted for the whole year. Required before 31 March. P9A: an older version or supplementary form for specific situations — its current use depends on current TRA rules. Verify the currently required form with TRA.",
  "formal", "disambiguation", SRC_PAYE, "TRA - PAYE"),

p("b006_disambig_013", "disambiguation_mixed",
  "EAC free trade area na STR — ni nini tofauti?",
  "EAC Free Trade Area (FTA): inafuta ushuru wa forodha kati ya nchi wanachama kwa bidhaa zinazotimiza masharti ya asili (rules of origin) — mfumo wa kimataifa wa biashara. EAC/COMESA STR (Simplified Trade Regime): mfumo maalum kwa wafanyabiashara WADOGO (threshold USD 2,000, bidhaa ~370) zinazokusudia kupunguza urasimu wa forodha kwa biashara ndogo. FTA ni kwa biashara yoyote; STR ni kwa biashara ndogo maalum.",
  "EAC free trade area and STR — what is the difference?",
  "EAC Free Trade Area (FTA): eliminates customs duties between member states for goods meeting rules of origin — a general international trade framework. EAC/COMESA STR (Simplified Trade Regime): a special scheme for SMALL traders (USD 2,000 threshold, ~370 goods) designed to reduce customs bureaucracy for small trade. FTA is for any business; STR is specifically for small traders.",
  "formal", "disambiguation",
  "https://www.comesa.int/simplified-trade-regime/", "COMESA - STR", "2007-01-01", "stable"),

p("b006_disambig_014", "disambiguation_mixed",
  "SDL na NSSF — zote zinalipwa tarehe 7 — je, kwa akaunti moja au tofauti?",
  "SDL na NSSF zinazalipwa tarehe 7 lakini kwa taasisi TOFAUTI. SDL inalipwa TRA (Tanzania Revenue Authority) kwa akaunti ya TRA. NSSF inalipwa NSSF (National Social Security Fund) kwa akaunti ya NSSF. Lipia kwa akaunti sahihi — kulipa SDL kwa akaunti ya NSSF au kinyume chake kutasababisha matatizo ya upatanisho.",
  "SDL and NSSF — both due on the 7th — do they go to one account or different ones?",
  "SDL and NSSF are both due on the 7th but go to DIFFERENT institutions. SDL is paid to TRA (Tanzania Revenue Authority) to the TRA account. NSSF is paid to NSSF (National Social Security Fund) to the NSSF account. Pay to the correct account — paying SDL to the NSSF account or vice versa will cause reconciliation problems.",
  "business_market", "disambiguation", SRC_SDL, "TRA - SDL"),

p("b006_disambig_015", "disambiguation_mixed",
  "Usajili wa OSHA na usajili wa WCF — lazima usajilishe wote wawili?",
  "Ndiyo — ni usajili MBILI TOFAUTI kwa taasisi tofauti. Usajili wa OSHA (Occupational Safety and Health Authority): mwajiri lazima asajilishe mahali pa kazi kwa OSHA na kufuata kanuni za usalama. Usajili wa WCF (Workers Compensation Fund): mwajiri lazima asajilishe wafanyakazi kwa WCF na kulipa michango ya bima ya ajali. Usajilishe ZOTE MBILI — hazibadilishani.",
  "OSHA registration and WCF registration — must you register for both?",
  "Yes — they are TWO SEPARATE registrations with different institutions. OSHA registration (Occupational Safety and Health Authority): an employer must register the workplace with OSHA and comply with safety standards. WCF registration (Workers Compensation Fund): an employer must register employees with WCF and pay accident insurance contributions. Register for BOTH — they are not interchangeable.",
  "formal", "disambiguation", "https://www.osha.go.tz/", "OSHA Tanzania"),

# ================================================================
# RURAL COMPLIANCE — 15 pairs (rural_conversational, practical)
# ================================================================

p("b006_rural_001", "rural_compliance",
  "Mama ntilie anayeuza chakula kila siku mjini — anahitaji kusajili biashara?",
  "Ndio, kwa kawaida. Hata mchuuzi wa chakula cha mitaani (mama ntilie) anafaa kusajili biashara yake na halmashauri ya mtaa/wilaya na kupata leseni ya biashara. Usajili wa TIN pia unashauriwa kama una mapato ya mara kwa mara. Kizingiti cha VAT (TZS 200M/mwaka) kwa kawaida hakifiki kwa mama ntilie mdogo. NSSF haihitajiki kama huna wafanyakazi waliohiriwa.",
  "A mama ntilie who sells food daily in town — does she need to register a business?",
  "Generally yes. Even a street food vendor (mama ntilie) should register their business with the local council/district and obtain a business licence. TIN registration is also advisable if you have regular income. The VAT threshold (TZS 200M/year) typically does not apply to a small mama ntilie. NSSF is not required if you have no hired employees.",
  "rural_conversational", "standard", SRC_BRELA, "BRELA"),

p("b006_rural_002", "rural_compliance",
  "Mkulima anayeuza mazao yake sokoni mwenyewe — PAYE inahitajika?",
  "Hapana kwa kawaida. Mkulima anayeuza mazao yake mwenyewe si mfanyakazi wa mtu mwingine — kwa hivyo PAYE haihusiki. PAYE ni kwa wafanyakazi waliohiriwa tu. Kama mkulima ana wafanyakazi wake, ndipo anaweza kuwa na wajibu wa PAYE kwa wafanyakazi hao.",
  "A farmer who sells their own produce at the market — is PAYE required?",
  "Generally no. A farmer selling their own produce is not an employee of someone else — so PAYE does not apply to them. PAYE is only for hired employees. If the farmer has hired workers, then they may have PAYE obligations for those workers.",
  "rural_conversational", "standard", SRC_PAYE, "TRA - PAYE"),

p("b006_rural_003", "rural_compliance",
  "Dereva wa bodaboda — ana wajibu gani wa kodi na leseni?",
  "Dereva wa bodaboda kwa kawaida anahitaji: (1) Leseni ya udereva (driving licence) ya kategoria husika; (2) Leseni ya gari (vehicle registration na bima); (3) Leseni ya biashara kutoka halmashauri kama ana duka au kituo; (4) TIN na BRELA kama biashara imekua. PAYE haitumiki kwa mwenye biashara yake mwenyewe. VAT kwa kawaida haifiki. Angalia kanuni za halmashauri yako.",
  "A motorcycle taxi (bodaboda) rider — what tax and licence obligations do they have?",
  "A bodaboda rider typically needs: (1) An appropriate driving licence; (2) Vehicle registration and insurance; (3) A business licence from the local council if they have a base or station; (4) TIN and BRELA registration if the business has grown. PAYE does not apply to self-employed operators. VAT typically does not apply. Check your local council's rules.",
  "rural_conversational", "standard", SRC_BRELA, "BRELA"),

p("b006_rural_004", "rural_compliance",
  "Duka la mitumba (used clothes) — VAT inatumika?",
  "Duka la mitumba lenye mauzo ya chini ya TZS 200M kwa mwaka halijafika kizingiti cha usajili wa VAT — kwa hivyo VAT haihitajiki. Hata hivyo, usajili wa biashara na halmashauri na TIN zinahitajika. Kama mauzo yanafika TZS 200M/mwaka au TZS 100M/miezi 6, usajili wa VAT unakuwa lazima.",
  "A second-hand clothes shop (mitumba) — does VAT apply?",
  "A mitumba shop with sales below TZS 200M per year has not reached the VAT registration threshold — so VAT is not required. However, business registration with the local council and a TIN are still required. Once sales reach TZS 200M/year or TZS 100M/6 months, VAT registration becomes mandatory.",
  "rural_conversational", "standard"),

p("b006_rural_005", "rural_compliance",
  "Fundi wa seremala (carpenter) anayefanya kazi peke yake — anahitaji NSSF?",
  "Fundi anayejitegemea (mwenye biashara yake mwenyewe, hana wafanyakazi) hajalazimishwa kwa NSSF ya wafanyakazi. Hata hivyo, NSSF inatoa programu ya michango ya hiari (voluntary contribution) kwa wajitegemea wanaotaka usalama wa pensheni. Kama fundi ataanza kuwa na wafanyakazi waliohiriwa, NSSF itakuwa lazima.",
  "A self-employed carpenter — do they need NSSF?",
  "A self-employed carpenter (running their own business, no hired workers) is not required to contribute to NSSF for employees. However, NSSF offers a voluntary contribution programme for self-employed persons who want pension security. If the carpenter starts hiring employees, NSSF becomes mandatory for those employees.",
  "rural_conversational", "standard", SRC_NSSF, "NSSF"),

p("b006_rural_006", "rural_compliance",
  "Muuzaji wa samaki sokoni — ana haja ya EFD machine?",
  "Muuzaji wa samaki mdogo wa sokoni kwa kawaida hahitaji EFD kama yeye mwenyewe hajalazimishwa kusajiliwa VAT (yaani mauzo yake ni chini ya TZS 200M kwa mwaka). EFD inahitajika tu kwa biashara zilizosajiliwa VAT. Hata hivyo, usajili wa biashara na halmashauri (leseni) na TIN bado zinahitajika.",
  "A fish seller at the market — do they need an EFD machine?",
  "A small fish seller at the market generally does not need an EFD if they are not required to be VAT-registered (i.e., their sales are below TZS 200M per year). EFD is only required for VAT-registered businesses. However, business registration with the local council (licence) and a TIN are still needed.",
  "rural_conversational", "standard"),

p("b006_rural_007", "rural_compliance",
  "Msimamizi wa mgahawa wa kijiji (kama mfanyakazi) — mwajiri wake analazimika kulipa nini?",
  "Mwajiri wa msimamizi wa mgahawa analazimika: (1) PAYE — kukata na kuwasilisha TRA tarehe 7; (2) NSSF — 10% mwajiri + 10% mfanyakazi; (3) WCF — 0.5% ya mshahara (bima ya ajali); (4) SDL — 3.5% kama mwajiri ana wafanyakazi 10+; (5) Kufuata GN 605A — kulipa mshahara wa chini unaofaa kwa sekta. Hizi zinatumika hata kwa mgahawa mdogo wa kijiji.",
  "A village restaurant manager (as an employee) — what must their employer pay?",
  "The employer of a restaurant manager must: (1) PAYE — deduct and remit to TRA by the 7th; (2) NSSF — 10% employer + 10% employee; (3) WCF — 0.5% of salary (accident insurance); (4) SDL — 3.5% if employer has 10+ employees; (5) Follow GN 605A — pay minimum wage applicable to the sector. These apply even for a small village restaurant.",
  "rural_conversational", "standard"),

p("b006_rural_008", "rural_compliance",
  "Mfanyabiashara wa mpakani wa Tunduma — GN 487A inamsimamia?",
  "Kama mfanyabiashara ni raia wa Tanzania, GN 487A haimsimamia — inalinda raia wa Tanzania katika sekta zilizokatazwa kwa wageni. Kama mfanyabiashara ni raia wa kigeni (Zambia, au nchi nyingine), GN 487A inaweza kutumika kama anafanya shughuli zilizo kwenye orodha ya 15 (kama biashara ya rejareja). Uraia ndio kigezo.",
  "A border trader at Tunduma — does GN 487A apply to them?",
  "If the trader is a Tanzanian citizen, GN 487A does not apply to them — it protects Tanzanian citizens in sectors prohibited to foreigners. If the trader is a non-citizen (Zambian, or from another country), GN 487A may apply if they are conducting activities on the list of 15 (like retail trade). Citizenship is the criterion.",
  "rural_conversational", "standard",
  SRC_GN487, "Government Notice 487A 2025, TanzLII", "2025-07-28", "event_triggered"),

p("b006_rural_009", "rural_compliance",
  "Mkulima wa VICOBA anayekopa pesa kutoka kwenye kikundi — kodi ya mapato inatumika?",
  "Mkopo kutoka kwa VICOBA si mapato — ni deni linalopaswa kulipwa. Kwa hivyo mkopo wenyewe haubeba kodi ya mapato. Hata hivyo, faida unayopata kwa KUTUMIA mkopo (kama biashara inafanya faida) inaweza kuwa mapato yanayolazimika. Kwa VICOBA ndogo za kijiji, TRA kwa kawaida haizingatii mkopo wa kikundi kama mapato ya kodi.",
  "A VICOBA farmer who borrows money from the group — does income tax apply?",
  "A loan from VICOBA is not income — it is a debt to be repaid. Therefore the loan itself does not carry income tax. However, profit you earn FROM USING the loan (if the business makes a profit) may be taxable income. For small village VICOBAs, TRA generally does not treat group loans as taxable income.",
  "rural_conversational", "standard"),

p("b006_rural_010", "rural_compliance",
  "Mtu anayeuza mkaa msituni — ana haja ya usajili wowote?",
  "Uuzaji wa mkaa (charcoal) unasimamia na sheria ya misitu na sheria ya mazingira Tanzania. Kwa ujumla, unahitaji: kibali cha ukataji miti kutoka TFS (Tanzania Forest Service) au Halmashauri; na labda leseni ya biashara kutoka halmashauri kama unauza kibiashara. TIN inashauriwa kama una biashara ya kawaida. Thibitisha na Halmashauri yako.",
  "A person selling charcoal from the forest — do they need any registration?",
  "Charcoal (mkaa) sales are regulated by Tanzania's forestry and environmental laws. Generally, you need: a timber cutting permit from TFS (Tanzania Forest Service) or the Council; and possibly a business licence from the council if selling commercially. A TIN is advisable if you have a regular business. Verify with your local council.",
  "rural_conversational", "standard", SRC_BRELA, "BRELA"),

p("b006_rural_011", "rural_compliance",
  "Mwalimu wa shule ya msingi ya binafsi (private primary school) — shule inalipa kodi gani?",
  "Shule binafsi za msingi zinaweza kuwa na wajibu wa: (1) PAYE kwa walimu waliohiriwa; (2) NSSF, SDL (kama walimu ≥10), WCF; (3) Usajili wa biashara BRELA na leseni ya elimu kutoka Wizara ya Elimu; (4) VAT kama mauzo ya ada yanafikia kizingiti (ingawa elimu inaweza kuwa na msamaha — thibitisha). TIN ya shule inahitajika.",
  "A teacher at a private primary school — what taxes does the school pay?",
  "Private primary schools may have: (1) PAYE for hired teachers; (2) NSSF, SDL (if ≥10 teachers), WCF; (3) BRELA business registration and education licence from Ministry of Education; (4) VAT if tuition fee revenue reaches the threshold (education may have an exemption — verify). The school's TIN is required.",
  "rural_conversational", "standard"),

p("b006_rural_012", "rural_compliance",
  "Duka la dawa la kijijini — linahitajika leseni gani mbali na biashara?",
  "Duka la dawa linahitaji leseni za ziada mbali na leseni ya biashara ya halmashauri: (1) Leseni ya kuuza dawa kutoka TMDA (Tanzania Medicines and Medical Devices Authority); (2) Msimamizi aliye na sifa ya kemia/afya anayehusika; (3) TIN ya biashara. Bila leseni ya TMDA, duka la dawa ni haramu hata kama lina leseni ya biashara.",
  "A rural pharmacy — what licences are needed beyond a business licence?",
  "A pharmacy needs additional licences beyond a council business licence: (1) A medicine selling licence from TMDA (Tanzania Medicines and Medical Devices Authority); (2) A qualified pharmacy/health supervisor responsible for the shop; (3) Business TIN. Without a TMDA licence, a pharmacy is illegal even if it has a business licence.",
  "rural_conversational", "standard", SRC_BRELA, "BRELA"),

p("b006_rural_013", "rural_compliance",
  "Mfanyabiashara mdogo anayekusanya pesa za kikundi kwa biashara (VICOBA leader) — ana wajibu wa kodi?",
  "Kiongozi wa VICOBA anayekusanya na kusimamia pesa za kikundi kwa niaba ya wanachama — si mfanyabiashara peke yake. Pesa za kikundi si mapato yake ya kibinafsi. Hata hivyo, kama kiongozi ana mshahara au posho kutoka kwa kikundi, hiyo inaweza kuwa mapato yanayolazimika kodi. Fanya ufafanuzi wa kisheria kwa kiongozi anayekusudia kupata malipo.",
  "A small business person collecting group savings as VICOBA leader — do they have tax obligations?",
  "A VICOBA leader collecting and managing group funds on behalf of members — is not themselves running a business. Group funds are not their personal income. However, if the leader receives a salary or allowance from the group, that may be taxable income. Seek legal clarity for a leader intending to receive payment.",
  "rural_conversational", "standard"),

p("b006_rural_014", "rural_compliance",
  "Mtu anayetengeneza na kuuza asali (honey) kijijini — anahitaji usajili gani?",
  "Mtengenezaji wa asali anayouza kibiashara kwa kawaida anahitaji: (1) Leseni ya biashara kutoka halmashauri; (2) TIN kama biashara inazalisha mapato ya mara kwa mara; (3) Kibali cha usafi wa chakula kutoka TFDA/TMDA au Ofisi ya Afya ya Wilaya; (4) Kama mauzo yanafika TZS 200M/mwaka, usajili wa VAT. Thibitisha masharti maalum na halmashauri na TMDA.",
  "A person who makes and sells honey in a village — what registration is required?",
  "A honey producer selling commercially typically needs: (1) A business licence from the local council; (2) A TIN if the business generates regular income; (3) A food safety permit from TFDA/TMDA or the District Health Office; (4) If sales reach TZS 200M/year, VAT registration. Confirm specific requirements with the local council and TMDA.",
  "rural_conversational", "standard", SRC_BRELA, "BRELA"),

p("b006_rural_015", "rural_compliance",
  "Msimamizi wa kiwanda kidogo cha kusaga mahindi (posho mill) — ana wajibu gani?",
  "Mmiliki wa posho mill anahitaji: (1) Leseni ya biashara kutoka halmashauri; (2) TIN kwa TRA; (3) Kama ana wafanyakazi waliohiriwa: PAYE, NSSF, WCF; (4) SDL kama wafanyakazi ≥10; (5) Usajili wa OSHA kama ana wafanyakazi na mashine ya hatari; (6) Kama mauzo yanafikia TZS 200M/mwaka: VAT. Kwa posho mill ndogo ya kawaida, PAYE na NSSF vinaweza visihitajike kama mmiliki anafanya kazi peke yake.",
  "The owner of a small grain milling business (posho mill) — what obligations do they have?",
  "A posho mill owner needs: (1) A business licence from the local council; (2) A TIN with TRA; (3) If they have hired employees: PAYE, NSSF, WCF; (4) SDL if ≥10 employees; (5) OSHA registration if they have employees and dangerous machinery; (6) If sales reach TZS 200M/year: VAT. For a small typical posho mill, PAYE and NSSF may not apply if the owner works alone.",
  "rural_conversational", "standard"),

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
subs = Counter(p_["subdomain"] for p_ in pairs)
print("Subdomain distribution:", dict(subs))
print("Register distribution:", dict(regs))
print("Pair type distribution:", dict(ptypes))
