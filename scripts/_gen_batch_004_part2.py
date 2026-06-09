#!/usr/bin/env python3
"""batch_004 part 2 — OSHA compliance (40 pairs) + PAYE adversarial first 10 = 50 pairs"""
import json, os

OUT = "datasets/tier1a/raw_sources/raw_pairs_batch_004.jsonl"
D = "2026-06-09"
TRA = "https://www.tra.go.tz"
TRA_N = "TRA — Tanzania Revenue Authority"
OSHA_URL = "https://www.osha.go.tz"
OSHA_N = "OSHA — Occupational Safety and Health Authority"
TANZLII = "https://www.tanzlii.org"
TANZLII_N = "TanzLII — Tanzania Legal Information Institute"
GP = "government_portal"
OG = "official_gazette"
EVT = "event_triggered"
ST = "stable"
ANN = "annual"

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
# OSHA COMPLIANCE (40 pairs, IDs osha_001–040)
# Source: osha.go.tz | Occupational Safety and Health Act, 2003
# =====================================================================

# --- OSHA standard (26 pairs) ---

p("tier1a_osha_001_20260609","osha_registration",
  "Je, biashara yangu inahitaji kusajiliwa na OSHA?",
  "Ndiyo, kama una wafanyakazi 10 au zaidi, biashara yako lazima isajiliwe na OSHA "
  "(Mamlaka ya Usalama na Afya Kazini). Usajili huu ni wa kila mwaka na unahitaji "
  "cheti cha OSHA kuonyeshwa mahali pa kazi.",
  "Does my business need to register with OSHA?",
  "Yes. If you have 10 or more employees your workplace must register with OSHA "
  "(Occupational Safety and Health Authority). Registration is annual and requires "
  "displaying the OSHA certificate at the workplace.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ANN, "OSHA Act amendment or threshold change",
  "business_market", "standard"),

p("tier1a_osha_002_20260609","osha_registration",
  "Kiwango cha usajili wa OSHA kinaanza kwa wafanyakazi wangapi?",
  "Waajiri wenye wafanyakazi 10 au zaidi wanalazimika kusajili mahali pao pa kazi "
  "na OSHA kwa mujibu wa Sheria ya Usalama na Afya Kazini ya 2003. Biashara zenye "
  "wafanyakazi chini ya 10 hazihitajiki rasmi kusajiliwa, ingawa sheria bado inatumika.",
  "From how many employees does OSHA registration become mandatory?",
  "Employers with 10 or more employees must register their workplace with OSHA under "
  "the Occupational Safety and Health Act 2003. Businesses with fewer than 10 employees "
  "are not formally required to register, though the Act's general provisions still apply.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ANN, "OSHA Act amendment or threshold change",
  "formal", "standard"),

p("tier1a_osha_003_20260609","osha_registration",
  "Gharama ya usajili wa OSHA kila mwaka ni kiasi gani?",
  "Gharama ya usajili wa OSHA inategemea sekta na saizi ya mahali pa kazi. Angalia "
  "jedwali la ada la OSHA kwa kiwango sahihi cha sekta yako — ada mbalimbali zinatumika "
  "kwa viwanda, ofisi, maduka na mahali pa kazi mengine.",
  "How much does the annual OSHA registration fee cost?",
  "The OSHA registration fee depends on your sector and workplace size. Check the OSHA "
  "fee schedule for your sector's exact rate — different rates apply to factories, "
  "offices, shops, and other workplace types.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ANN, "OSHA fee schedule update",
  "business_market", "standard"),

p("tier1a_osha_004_20260609","osha_safety_committee",
  "Ni lini mwajiri analazimika kuunda kamati ya usalama (safety committee)?",
  "Mwajiri mwenye wafanyakazi 20 au zaidi analazimika kuunda kamati ya usalama na "
  "afya kazini. Kamati hii lazima ikutane mara kwa mara na kuhakikisha usalama "
  "mahali pa kazi unashughulikiwa.",
  "When is an employer required to establish a safety committee?",
  "An employer with 20 or more employees must establish an occupational safety and "
  "health committee. The committee must meet regularly and ensure workplace safety "
  "matters are addressed.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ST, "OSHA Act amendment",
  "formal", "standard"),

p("tier1a_osha_005_20260609","osha_accident_reporting",
  "Ikiwa mfanyakazi ameumia kazini, ninapaswa kuripoti lini na wapi?",
  "Ajali kubwa au ya kifo lazima iripotiwe kwa OSHA ndani ya masaa 24. Mwajiri "
  "pia ana wajibu wa kuripoti kwa WCF (Workers Compensation Fund) ndani ya siku 30. "
  "Kuchelewesha kuripoti ni kosa la kisheria.",
  "If a worker is injured at work when and where do I report it?",
  "A serious or fatal accident must be reported to OSHA within 24 hours. The employer "
  "also has an obligation to report to the WCF (Workers Compensation Fund) within "
  "30 days. Late reporting is a legal offence.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ST, "OSHA Act amendment",
  "business_market", "standard"),

p("tier1a_osha_006_20260609","osha_first_aid",
  "Je, mwajiri analazimika kuwa na huduma ya msaada wa kwanza (first aid) kazini?",
  "Ndiyo. Waajiri wanalazimika kutoa vifaa vya msaada wa kwanza mahali pa kazi na "
  "kuhakikisha kuwa wafanyakazi waliofunzwa msaada wa kwanza wako kazini. "
  "Idadi ya mafundi wa msaada wa kwanza inategemea saizi ya mahali pa kazi.",
  "Is an employer required to have first aid facilities at work?",
  "Yes. Employers must provide first aid equipment at the workplace and ensure trained "
  "first aiders are available. The number of first aiders required depends on "
  "the size of the workplace.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ST, "OSHA Act amendment",
  "rural_conversational", "standard"),

p("tier1a_osha_007_20260609","osha_inspection",
  "OSHA inspekta ana mamlaka gani wanapokuja kukagua biashara yangu?",
  "Inspekta wa OSHA ana mamlaka ya: kuingia mahali pa kazi bila notisi awali (wakati "
  "wa saa za kazi), kuchunguza rekodi za usalama, kuhoji wafanyakazi, kuchukua sampuli, "
  "na kutoa notisi ya uboreshaji (improvement notice) au amri ya kuzuia (prohibition "
  "notice) ikiwa kuna hatari.",
  "What powers does an OSHA inspector have when visiting my business?",
  "An OSHA inspector has authority to: enter the workplace without prior notice "
  "(during working hours), examine safety records, interview employees, take samples, "
  "and issue an improvement notice or prohibition notice if a hazard exists.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ST, "OSHA Act amendment",
  "business_market", "standard"),

p("tier1a_osha_008_20260609","osha_improvement_notice",
  "Notisi ya uboreshaji (improvement notice) kutoka OSHA inamaanisha nini?",
  "Notisi ya uboreshaji ni amri rasmi kutoka OSHA inayomwambia mwajiri aboreshe "
  "hali fulani ya hatari ndani ya muda maalum uliotajwa. Kukosa kufuata notisi "
  "ni kosa la jinai na kunaweza kusababisha faini au kufungwa kwa mahali pa kazi.",
  "What does an improvement notice from OSHA mean?",
  "An improvement notice is a formal OSHA order requiring an employer to remedy a "
  "specific hazard within a stated time period. Failure to comply is a criminal "
  "offence and can result in fines or closure of the workplace.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ST, "OSHA Act amendment",
  "formal", "standard"),

p("tier1a_osha_009_20260609","osha_prohibition_notice",
  "Amri ya kuzuia (prohibition notice) kutoka OSHA inatofautiana vipi na notisi ya uboreshaji?",
  "Notisi ya uboreshaji inakupa muda wa kurekebisha tatizo. Amri ya kuzuia, kinyume "
  "chake, inahitaji kazi kusimamishwa MARA MOJA kwa sababu kuna hatari ya haraka ya "
  "kifo au majeraha makubwa. Mwajiri hawezi kuendelea na shughuli mpaka hatari "
  "isimamishwe.",
  "How does a prohibition notice from OSHA differ from an improvement notice?",
  "An improvement notice gives you time to fix a problem. A prohibition notice, by "
  "contrast, requires work to stop IMMEDIATELY because there is an imminent risk of "
  "death or serious injury. The employer cannot resume operations until the danger "
  "is eliminated.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ST, "OSHA Act amendment",
  "formal", "standard"),

p("tier1a_osha_010_20260609","osha_penalties",
  "Adhabu ya ukiukwaji wa sheria ya OSHA ni nini?",
  "Ukiukwaji wa Sheria ya Usalama na Afya Kazini ya 2003 unaweza kusababisha: faini, "
  "kufungwa kwa mahali pa kazi, au kifungo cha jela. Makosa ya jinai kama kutokuripoti "
  "ajali ya kifo yana adhabu kali zaidi. Mwajiri mwenye historia ya ukiukwaji ana "
  "hatari ya adhabu kubwa zaidi.",
  "What is the penalty for violating the OSHA Act?",
  "Violations of the Occupational Safety and Health Act 2003 can result in: fines, "
  "workplace closure, or imprisonment. Criminal offences such as failing to report a "
  "fatal accident carry heavier penalties. An employer with a history of violations "
  "faces higher penalties.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ST, "OSHA Act amendment",
  "formal", "standard"),

p("tier1a_osha_011_20260609","osha_registration",
  "Je, OSHA ni sawa na bima ya wafanyakazi (WCF)?",
  "Hapana. OSHA (Occupational Safety and Health Authority) inashughulikia USALAMA "
  "na KINGA mahali pa kazi — usajili wa usalama na ukaguzi. WCF (Workers Compensation "
  "Fund) inashughulikia BIMA ya ajali — malipo ya fidia baada ya mfanyakazi kuumia. "
  "Waajiri wote wanawajibika kwa zote mbili.",
  "Is OSHA the same as workers compensation insurance (WCF)?",
  "No. OSHA (Occupational Safety and Health Authority) deals with workplace SAFETY "
  "and PREVENTION — safety registration and inspections. WCF (Workers Compensation "
  "Fund) deals with accident INSURANCE — compensation payments after a worker is "
  "injured. All employers are liable to both.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ST, "OSHA Act amendment",
  "business_market", "standard"),

p("tier1a_osha_012_20260609","osha_registration",
  "Biashara ya ofisi (office work) inahitaji kusajiliwa na OSHA pia?",
  "Ndiyo. OSHA inatumika kwa mahali pote pa kazi Tanzania, ikiwa ni pamoja na ofisi, "
  "si viwanda tu. Ikiwa ofisi yako ina wafanyakazi 10 au zaidi, lazima isajiliwe. "
  "Ofisi pia zinahitaji hewa safi, taa ya kutosha, na hali nzuri ya kufanya kazi.",
  "Does an office business also need to register with OSHA?",
  "Yes. OSHA applies to all workplaces in Tanzania, including offices — not just "
  "factories. If your office has 10 or more employees it must register. Offices also "
  "require adequate ventilation, lighting, and good working conditions.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ANN, "OSHA Act amendment",
  "business_market", "standard"),

p("tier1a_osha_013_20260609","osha_health_surveillance",
  "Ni wafanyakazi wa aina gani wanahitaji uchunguzi wa afya wa mara kwa mara?",
  "Wafanyakazi wanaofanya kazi katika mazingira hatari — kemikali, vumbi la madini, "
  "kelele kali, au mionzi — wanalazimika kupata uchunguzi wa afya wa mara kwa mara. "
  "Mwajiri anawajibika kupanga na kulipa kwa uchunguzi huu.",
  "Which workers require regular health surveillance?",
  "Workers in hazardous environments — chemicals, mineral dust, excessive noise, or "
  "radiation — must undergo periodic health surveillance. The employer is responsible "
  "for arranging and paying for these examinations.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ST, "OSHA Act amendment",
  "formal", "standard"),

p("tier1a_osha_014_20260609","osha_registration",
  "OSHA cheti kinaombwa wapi na jinsi gani?",
  "Cheti cha OSHA kinaombwa kupitia tovuti ya OSHA (osha.go.tz) au ofisi ya OSHA "
  "ya mkoa. Unahitaji fomu ya maombi, ada ya usajili, na taarifa za mahali pa kazi "
  "kama idadi ya wafanyakazi na aina ya shughuli. Cheti kinahuishwa kila mwaka.",
  "Where and how is an OSHA certificate applied for?",
  "An OSHA certificate is applied for through the OSHA website (osha.go.tz) or the "
  "regional OSHA office. You need an application form, the registration fee, and "
  "workplace details such as employee count and type of activity. It is renewed annually.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ANN, "OSHA fee schedule or process update",
  "business_market", "standard"),

p("tier1a_osha_015_20260609","osha_fire_safety",
  "Sheria ya OSHA inasema nini kuhusu usalama wa moto (fire safety)?",
  "Waajiri wanalazimika kuhakikisha: vizima moto (fire extinguishers) vipo na "
  "vimekaguliwa, njia za kutoka kwa dharura (emergency exits) ziko wazi na "
  "zina alama, mafunzo ya dharura yanatolewa kwa wafanyakazi, na mpango wa "
  "uokoaji (evacuation plan) upo.",
  "What does the OSHA Act say about fire safety?",
  "Employers must ensure: fire extinguishers are present and inspected, emergency "
  "exits are clear and marked, evacuation drills are provided to employees, and "
  "an evacuation plan is in place.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ST, "OSHA Act amendment",
  "formal", "standard"),

p("tier1a_osha_016_20260609","osha_registration",
  "Je, kampuni mpya inahitaji usajili wa OSHA kabla ya kuanza kufanya kazi?",
  "Ndiyo. Kampuni mpya yenye wafanyakazi 10 au zaidi inapaswa kusajiliwa na OSHA "
  "KABLA ya kuanza shughuli, au haraka iwezekanavyo baada ya kufikia wafanyakazi 10. "
  "Kuanza kufanya kazi bila usajili ni ukiukwaji wa sheria.",
  "Does a new company need OSHA registration before starting operations?",
  "Yes. A new company with 10 or more employees should register with OSHA BEFORE "
  "commencing operations, or as soon as possible after reaching 10 employees. "
  "Operating without registration is a legal violation.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ANN, "OSHA Act amendment",
  "business_market", "standard"),

p("tier1a_osha_017_20260609","osha_safety_committee",
  "Kamati ya usalama (safety committee) inafanya nini hasa?",
  "Kamati ya usalama inafanya: kukagua hali ya usalama mahali pa kazi, kupitia "
  "ajali na matukio, kupendekeza maboresho ya usalama, kuhakikisha wafanyakazi "
  "wana mafunzo ya usalama, na kuwasiliana na usimamizi kuhusu masuala ya usalama. "
  "Kamati inakutana angalau mara moja kwa mwezi.",
  "What does a safety committee specifically do?",
  "A safety committee: inspects workplace safety conditions, reviews accidents and "
  "incidents, recommends safety improvements, ensures workers receive safety training, "
  "and communicates safety issues to management. The committee meets at least once a month.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ST, "OSHA Act amendment",
  "formal", "standard"),

p("tier1a_osha_018_20260609","osha_registration",
  "Je, mkaguzi (contractor) anayefanya kazi ofisini kwangu anahitaji OSHA?",
  "Mwajiri mkuu (principal employer) anabeba wajibu wa usalama wa kila mtu mahali "
  "pa kazi, ikiwa ni pamoja na wakandarasi. Kama mkandarasi anafanya kazi yenye "
  "hatari katika eneo lako, lazima uhakikishe anafuata viwango vya usalama vya OSHA "
  "na ana bima ya WCF.",
  "Does a contractor working on my premises need OSHA coverage?",
  "The principal employer bears safety responsibility for everyone on the premises, "
  "including contractors. If a contractor performs hazardous work at your site you "
  "must ensure they meet OSHA safety standards and have WCF insurance.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ST, "OSHA Act amendment",
  "business_market", "standard"),

p("tier1a_osha_019_20260609","osha_registration",
  "Kama mfanyakazi anakataa kufanya kazi kwa sababu ya hatari ya usalama, ana haki?",
  "Ndiyo. Wafanyakazi wana haki ya kukataa kufanya kazi yenye hatari ya haraka na "
  "ya kweli ya kifo au majeraha makubwa. Mwajiri haruhusiwi kumfuta mfanyakazi "
  "kwa kukataa kufanya kazi hatari. Haki hii inalindwa na Sheria ya OSHA.",
  "If a worker refuses to work due to a safety hazard do they have the right?",
  "Yes. Workers have the right to refuse to perform work that poses an imminent and "
  "genuine risk of death or serious injury. An employer may not dismiss an employee "
  "for refusing to perform dangerous work. This right is protected under the OSHA Act.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ST, "OSHA Act amendment",
  "rural_conversational", "standard"),

p("tier1a_osha_020_20260609","osha_registration",
  "Je, OSHA inahusiana na Sheria ya Viwanda ya 1950?",
  "Ndiyo. Sheria ya OSHA ya 2003 ilichukua nafasi ya Sheria ya Viwanda ya 1950 "
  "(Factories Ordinance). Sheria ya 1950 ilikuwa inashughulikia viwanda tu, wakati "
  "OSHA 2003 inashughulikia mahali POTE pa kazi, ikiwa ni pamoja na ofisi, "
  "maduka, na mahali pa kazi mengine.",
  "How does OSHA relate to the Factories Ordinance of 1950?",
  "OSHA 2003 replaced the Factories Ordinance of 1950. The 1950 ordinance covered "
  "only factories, while OSHA 2003 covers ALL workplaces including offices, shops, "
  "and other work settings.",
  TANZLII, TANZLII_N, OG, "2003-07-01", ST, "OSHA Act amendment",
  "formal", "standard"),

p("tier1a_osha_021_20260609","osha_registration",
  "Mwajiri ana wajibu gani wa kutoa vifaa vya kinga binafsi (PPE)?",
  "Mwajiri analazimika kutoa vifaa vya kinga binafsi (PPE) bila malipo kwa "
  "wafanyakazi wanaofanya kazi katika mazingira hatari. PPE inaweza kujumuisha: "
  "kofia ngumu, miwani ya usalama, glovu, buti, na vipande vya masikio. "
  "Wafanyakazi wana wajibu wa kuvaa PPE iliyotolewa.",
  "What obligation does an employer have to provide personal protective equipment (PPE)?",
  "An employer must provide personal protective equipment (PPE) free of charge to "
  "workers performing hazardous work. PPE may include hard hats, safety goggles, "
  "gloves, boots, and ear protection. Workers have an obligation to wear the "
  "PPE provided.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ST, "OSHA Act amendment",
  "formal", "standard"),

p("tier1a_osha_022_20260609","osha_registration",
  "Je, biashara ya ujenzi inahitaji OSHA? Hatua gani maalum za usalama zinahitajika?",
  "Ndiyo. Ujenzi ni sekta yenye hatari kubwa na inahitaji usajili wa OSHA. Hatua "
  "maalum zinajumuisha: matunzio ya scaffolding, ulinzi wa mahandaki, PPE kwa "
  "wafanyakazi wote, mafunzo ya usalama, na afisa wa usalama mahali pa kazi. "
  "OSHA inafanya ukaguzi wa mara kwa mara kwa maeneo ya ujenzi.",
  "Does a construction business need OSHA? What specific safety measures are required?",
  "Yes. Construction is a high-risk sector and requires OSHA registration. Specific "
  "measures include: proper scaffolding, trench protection, PPE for all workers, "
  "safety training, and a site safety officer. OSHA conducts frequent inspections "
  "of construction sites.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ANN, "OSHA regulation update",
  "business_market", "standard"),

p("tier1a_osha_023_20260609","osha_registration",
  "Mfanyakazi ana haki ya kupata nakala ya ripoti ya uchunguzi wa ajali?",
  "Ndiyo. Mfanyakazi aliyeathiriwa na ajali, au wawakilishi wake, wana haki ya "
  "kupata nakala ya ripoti ya uchunguzi wa ajali iliyofanywa na mwajiri au OSHA. "
  "Uwazi huu ni sehemu ya haki za mfanyakazi chini ya Sheria ya OSHA.",
  "Does a worker have the right to obtain a copy of an accident investigation report?",
  "Yes. An affected worker, or their representatives, has the right to obtain a copy "
  "of the accident investigation report prepared by the employer or OSHA. This "
  "transparency is part of workers' rights under the OSHA Act.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ST, "OSHA Act amendment",
  "formal", "standard"),

p("tier1a_osha_024_20260609","osha_registration",
  "Kama na ofisi ndogo ya wafanyakazi 5, bado nahitaji kufuata sheria ya OSHA?",
  "Ingawa usajili rasmi wa OSHA unatakiwa kwa wafanyakazi 10+, masharti ya msingi "
  "ya usalama ya OSHA yanatumika kwa biashara zote. Hii inajumuisha: mazingira salama "
  "ya kazi, hewa safi, taa ya kutosha, na msaada wa kwanza. Usalama wa wafanyakazi "
  "ni wajibu wa kisheria bila kujali saizi.",
  "If I have a small office of 5 employees do I still need to follow OSHA law?",
  "Although formal OSHA registration is required for 10+ employees, the basic OSHA "
  "safety requirements apply to all businesses. This includes: safe working environment, "
  "adequate ventilation, sufficient lighting, and first aid. Employee safety is a "
  "legal duty regardless of size.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ANN, "OSHA Act amendment",
  "rural_conversational", "standard"),

p("tier1a_osha_025_20260609","osha_registration",
  "Mwajiri anapaswa kutunza rekodi gani za usalama wa mahali pa kazi?",
  "Mwajiri lazima atunze: rejesta ya ajali na matukio, rekodi za mafunzo ya usalama, "
  "rekodi za uchunguzi wa afya wa wafanyakazi, matokeo ya ukaguzi wa usalama, na "
  "nakala za notisi za OSHA. Rekodi hizi zinaweza kukaguliwa na inspekta wa OSHA.",
  "What safety records must an employer keep at the workplace?",
  "An employer must maintain: an accident and incident register, safety training "
  "records, employee health surveillance records, safety inspection results, and copies "
  "of OSHA notices. These records can be inspected by an OSHA inspector.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ST, "OSHA Act amendment",
  "formal", "standard"),

p("tier1a_osha_026_20260609","osha_registration",
  "Je, OSHA na NSSF ni tofauti?",
  "Ndiyo, ni tofauti kabisa. OSHA (Occupational Safety and Health Authority) "
  "inashughulikia USALAMA mahali pa kazi — ukaguzi, viwango vya usalama, na usajili "
  "wa mahali pa kazi. NSSF (National Social Security Fund) inashughulikia BIMA YA "
  "JAMII — pensheni, matibabu, na manufaa ya kijamii. Zote mbili zinahitaji "
  "kufuata na mwajiri.",
  "Are OSHA and NSSF different?",
  "Yes, they are entirely different. OSHA (Occupational Safety and Health Authority) "
  "deals with workplace SAFETY — inspections, safety standards, and workplace "
  "registration. NSSF (National Social Security Fund) deals with SOCIAL SECURITY — "
  "pension, medical, and social benefits. Both require employer compliance.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ST, "OSHA Act amendment",
  "business_market", "disambiguation"),

# --- OSHA adversarial (10 pairs) ---

p("tier1a_osha_027_20260609","osha_adversarial",
  "OSHA inatumika tu kwa viwanda na miundombinu ya uzalishaji, si ofisi — je, hii ni kweli?",
  "Hapana, si kweli. OSHA ya 2003 inatumika kwa MAHALI POTE pa kazi Tanzania, "
  "ikiwa ni pamoja na ofisi, maduka, hospitali, shule, na mahali pengine. Sheria ya "
  "zamani ya Viwanda (1950) ilikuwa ya viwanda tu, lakini OSHA 2003 iliongeza wigo "
  "hadi mahali pa kazi yote.",
  "OSHA only applies to factories and production facilities, not offices — is this true?",
  "No, this is false. OSHA 2003 applies to ALL workplaces in Tanzania including "
  "offices, shops, hospitals, schools, and other settings. The old Factories Ordinance "
  "(1950) was factory-specific, but OSHA 2003 expanded coverage to all workplaces.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ST, "OSHA Act amendment",
  "business_market", "adversarial"),

p("tier1a_osha_028_20260609","osha_adversarial",
  "Kiwango cha usajili wa OSHA ni wafanyakazi 5 au zaidi — je, hii ni sahihi?",
  "Hapana. Kiwango sahihi cha usajili wa OSHA ni wafanyakazi 10 au zaidi — si 5. "
  "Kiwango cha wafanyakazi 5 si cha kisheria na hakipo katika Sheria ya OSHA ya 2003. "
  "Biashara zinazopata wafanyakazi 10 ndizo zinazolazimika kusajiliwa.",
  "The OSHA registration threshold is 5 or more employees — is this correct?",
  "No. The correct OSHA registration threshold is 10 or more employees — not 5. "
  "A threshold of 5 is not statutory and does not appear in the OSHA Act 2003. "
  "Businesses reaching 10 employees are the ones required to register.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ST, "OSHA Act amendment",
  "formal", "adversarial"),

p("tier1a_osha_029_20260609","osha_adversarial",
  "Kamati ya usalama inahitajika kwa biashara zenye wafanyakazi 10 au zaidi — je, hii ni kweli?",
  "Hapana. Kamati ya usalama inahitajika kwa biashara zenye wafanyakazi 20 au zaidi "
  "— si 10. Kiwango cha 10 ni kwa USAJILI wa OSHA. Kiwango tofauti cha wafanyakazi "
  "20 kinatumika kwa UUNDWAJI WA KAMATI ya usalama.",
  "A safety committee is required for businesses with 10 or more employees — is this true?",
  "No. A safety committee is required for businesses with 20 or more employees — "
  "not 10. The threshold of 10 is for OSHA REGISTRATION. The separate threshold "
  "of 20 applies to establishing a SAFETY COMMITTEE.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ST, "OSHA Act amendment",
  "business_market", "adversarial"),

p("tier1a_osha_030_20260609","osha_adversarial",
  "Cheti cha OSHA kinaisha muda baada ya miaka 3 — je, ni kweli?",
  "Hapana. Cheti cha OSHA kinahuishwa KILA MWAKA — si baada ya miaka 3. "
  "Usajili wa kila mwaka unahitajika kudumisha utiifu wa kisheria. Cheti "
  "kilichoisha muda ni ukiukwaji wa OSHA.",
  "An OSHA certificate expires after 3 years — is this true?",
  "No. An OSHA certificate is renewed ANNUALLY — not every 3 years. Annual "
  "registration is required to maintain legal compliance. An expired certificate "
  "is an OSHA violation.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ANN, "OSHA Act amendment",
  "rural_conversational", "adversarial"),

p("tier1a_osha_031_20260609","osha_adversarial",
  "Ajali za kazini zinaripotiwa ndani ya siku 7 — je, muda huu ni sahihi?",
  "Hapana kwa ajali kubwa. Ajali kubwa au za kifo lazima ziripotiwe kwa OSHA "
  "ndani ya masaa 24 — si siku 7. Kwa WCF (Workers Compensation Fund), "
  "muda wa kuripoti ni siku 30. Muda wa masaa 24 unahusu OSHA peke yake na "
  "unatumika kwa ajali za haraka.",
  "Workplace accidents are reported within 7 days — is this timeframe correct?",
  "No, not for serious accidents. Serious or fatal accidents must be reported to "
  "OSHA within 24 HOURS — not 7 days. For WCF (Workers Compensation Fund) the "
  "reporting period is 30 days. The 24-hour window applies to OSHA specifically "
  "for urgent accidents.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ST, "OSHA Act amendment",
  "formal", "adversarial"),

p("tier1a_osha_032_20260609","osha_adversarial",
  "Mwajiri anaweza kumfuta mfanyakazi anayekataa kufanya kazi yenye hatari — je, hii ni kweli?",
  "Hapana. Kufuta mfanyakazi kwa kukataa kufanya kazi yenye hatari ya haraka ni "
  "KINYUME na Sheria ya OSHA na Sheria ya Ajira na Mahusiano ya Kazini (ELRA). "
  "Wafanyakazi wana haki ya kulindwa kufanya kazi yenye hatari ya haraka ya kifo "
  "au majeraha makubwa bila kulipizwa kisasi.",
  "An employer can dismiss an employee who refuses to perform dangerous work — is this true?",
  "No. Dismissing an employee for refusing to perform work with an imminent hazard is "
  "ILLEGAL under both the OSHA Act and the Employment and Labour Relations Act (ELRA). "
  "Workers have a protected right to refuse imminently dangerous work without facing "
  "retaliation.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ST, "OSHA Act amendment",
  "business_market", "adversarial"),

p("tier1a_osha_033_20260609","osha_adversarial",
  "Vifaa vya kinga binafsi (PPE) mfanyakazi anunue mwenyewe — je, mwajiri hana wajibu?",
  "Hapana. Mwajiri analazimika kutoa PPE BILA MALIPO kwa wafanyakazi wanaofanya "
  "kazi hatari. Kuwaacha wafanyakazi wanunue PPE wenyewe ni ukiukwaji wa Sheria "
  "ya OSHA. Mwajiri ndiye mwenye wajibu mkubwa wa usalama mahali pa kazi.",
  "Personal protective equipment (PPE) should be bought by the worker themselves — the employer has no obligation?",
  "No. The employer is required to provide PPE FREE OF CHARGE to workers in hazardous "
  "roles. Requiring workers to buy their own PPE is a violation of the OSHA Act. "
  "The employer bears primary responsibility for workplace safety.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ST, "OSHA Act amendment",
  "rural_conversational", "adversarial"),

p("tier1a_osha_034_20260609","osha_adversarial",
  "OSHA inahusiana tu na majeraha ya kimwili — magonjwa yanayosababishwa na kazi hayafunikwi?",
  "Hapana. OSHA ya 2003 inashughulikia USALAMA NA AFYA zote mbili — ikiwa ni pamoja "
  "na magonjwa yanayosababishwa na kazi (occupational diseases) kama uziwi wa kelele, "
  "magonjwa ya mapafu kutokana na vumbi, na matatizo ya kemikali. Afya ya mfanyakazi "
  "kwa njia yote ni wajibu wa mwajiri.",
  "OSHA only relates to physical injuries — work-caused diseases are not covered?",
  "No. OSHA 2003 covers BOTH safety and health — including occupational diseases such "
  "as noise-induced deafness, dust-related lung conditions, and chemical health issues. "
  "Employee health in all its forms is an employer obligation.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ST, "OSHA Act amendment",
  "formal", "adversarial"),

p("tier1a_osha_035_20260609","osha_adversarial",
  "Biashara inayofanya kazi usiku tu haihitaji OSHA kwa sababu inspekta wanafanya kazi mchana tu?",
  "Hili ni wazo potofu. OSHA inatumika kwa wakati wote wa kazi bila kujali muda wa siku "
  "au usiku. Ingawa ukaguzi mara nyingi hufanywa mchana, wajibu wa OSHA unaendelea "
  "muda wote wa shughuli. Usajili unahitajika na viwango vya usalama lazima vifuatwe "
  "wakati wote.",
  "A business operating only at night doesn't need OSHA because inspectors only work during the day?",
  "This is a misconception. OSHA applies during all working hours regardless of day or "
  "night. Although inspections often occur during daylight, OSHA obligations continue "
  "throughout all operational hours. Registration is required and safety standards "
  "must be met at all times.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ST, "OSHA Act amendment",
  "business_market", "adversarial"),

p("tier1a_osha_036_20260609","osha_adversarial",
  "OSHA na WCF ni shirika moja tu — ni kweli?",
  "Hapana. OSHA na WCF ni mashirika tofauti kabisa yanayofanya kazi tofauti. "
  "OSHA (Occupational Safety and Health Authority) inasimamia USALAMA kazini. "
  "WCF (Workers Compensation Fund) inasimamia BIMA ya ajali za kazi. Waajiri "
  "wanalazimika kusajiliwa na ZOTE MBILI kwa namna tofauti.",
  "OSHA and WCF are just one organisation — is this true?",
  "No. OSHA and WCF are completely separate organisations with different functions. "
  "OSHA (Occupational Safety and Health Authority) oversees workplace SAFETY. "
  "WCF (Workers Compensation Fund) administers workplace accident INSURANCE. "
  "Employers must register with BOTH separately.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ST, "OSHA Act amendment",
  "business_market", "adversarial"),

# --- OSHA disambiguation (4 pairs) ---

p("tier1a_osha_037_20260609","osha_disambiguation",
  "Tofauti kati ya usajili wa OSHA na usajili wa WCF ni nini?",
  "Usajili wa OSHA unahusu USALAMA mahali pa kazi — ukaguzi, viwango vya usalama, "
  "na cheti cha OSHA. Usajili wa WCF unahusu BIMA ya ajali — malipo ya mfanyakazi "
  "aliyeumia. Zote mbili zinahitajika lakini zina taratibu tofauti, ada tofauti, "
  "na mashirika tofauti.",
  "What is the difference between OSHA registration and WCF registration?",
  "OSHA registration is about workplace SAFETY — inspections, safety standards, and "
  "OSHA certificate. WCF registration is about accident INSURANCE — payments to "
  "injured workers. Both are required but have separate processes, separate fees, "
  "and separate organisations.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ST, "OSHA Act amendment",
  "formal", "disambiguation"),

p("tier1a_osha_038_20260609","osha_disambiguation",
  "Tofauti kati ya kiwango cha usajili wa OSHA (wafanyakazi 10) na kiwango cha kamati ya usalama (wafanyakazi 20) ni nini?",
  "Kiwango cha 10 ni kwa USAJILI rasmi wa biashara yako na OSHA — kupata cheti cha OSHA. "
  "Kiwango cha 20 ni kwa KUUNDA KAMATI ya usalama ndani ya biashara. Kwa hivyo biashara "
  "yenye wafanyakazi 10-19 inasajiliwa na OSHA lakini haihitaji kamati ya usalama. "
  "Biashara yenye wafanyakazi 20+ inahitaji vyote viwili.",
  "What is the difference between the OSHA registration threshold (10 employees) and the safety committee threshold (20 employees)?",
  "The threshold of 10 is for formal OSHA REGISTRATION of your business — obtaining "
  "an OSHA certificate. The threshold of 20 is for ESTABLISHING A SAFETY COMMITTEE "
  "inside the business. So a business with 10-19 employees registers with OSHA but "
  "doesn't need a safety committee. A business with 20+ needs both.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ST, "OSHA Act amendment",
  "formal", "disambiguation"),

p("tier1a_osha_039_20260609","osha_disambiguation",
  "Improvement notice na prohibition notice kutoka OSHA ni tofauti vipi?",
  "Improvement notice (notisi ya uboreshaji): OSHA inakupa muda maalum kurekebisha "
  "tatizo. Prohibition notice (amri ya kuzuia): shughuli lazima zisimame MARA MOJA "
  "kwa sababu kuna hatari ya haraka ya kifo au majeraha makubwa. Prohibition ni "
  "hatua kali zaidi inayohitaji kusimamisha kazi bila kucheleweshwa.",
  "How do an improvement notice and a prohibition notice from OSHA differ?",
  "Improvement notice: OSHA gives you a set time to fix a problem. Prohibition "
  "notice: operations must stop IMMEDIATELY because there is imminent risk of death "
  "or serious injury. A prohibition is the more serious step requiring an instant "
  "work stoppage with no delay.",
  OSHA_URL, OSHA_N, GP, "2003-07-01", ST, "OSHA Act amendment",
  "business_market", "disambiguation"),

p("tier1a_osha_040_20260609","osha_disambiguation",
  "OSHA na ELRA (Sheria ya Ajira) zinahusiana vipi?",
  "OSHA inashughulikia USALAMA na AFYA mahali pa kazi — viwango vya mazingira ya "
  "kazi na ukaguzi. ELRA (Employment and Labour Relations Act) inashughulikia "
  "MAHUSIANO YA AJIRA — mikataba, masaa ya kazi, malipo, na masharti ya ajira. "
  "Zote mbili zinatumika pamoja — mwajiri lazima afuate OSHA na ELRA.",
  "How are OSHA and ELRA (Employment Act) related?",
  "OSHA deals with workplace SAFETY and HEALTH — working environment standards and "
  "inspections. ELRA (Employment and Labour Relations Act) deals with EMPLOYMENT "
  "RELATIONS — contracts, working hours, pay, and terms of employment. Both apply "
  "together — an employer must comply with both OSHA and ELRA.",
  TANZLII, TANZLII_N, OG, "2003-07-01", ST, "OSHA or ELRA Act amendment",
  "formal", "disambiguation"),

# =====================================================================
# PAYE ADVERSARIAL — first 10 pairs (pairs paye_adv_001–010)
# Source: tra.go.tz
# =====================================================================

p("tier1a_paye_adv_001_20260609","paye_adversarial",
  "Kiwango cha pili cha PAYE ni asilimia 9 kwa mapato kati ya Shilingi 270,001 na 520,000 kwa mwezi — je, hii ni sahihi?",
  "Hapana. Kiwango cha pili cha PAYE ni asilimia 8 — si asilimia 9. Kanda za PAYE "
  "kwa mwezi ni: asilimia sifuri (hadi Shilingi 270,000), asilimia 8 (Shilingi 270,001 "
  "hadi 520,000), asilimia 20 (Shilingi 520,001 hadi 760,000), asilimia 25 (Shilingi "
  "760,001 hadi 1,000,000), na asilimia 30 (zaidi ya Shilingi 1,000,000).",
  "The second PAYE band is 9% on income between TZS 270,001 and 520,000 per month — is this correct?",
  "No. The second PAYE band is 8% — not 9%. The monthly PAYE bands are: 0% (up to "
  "TZS 270,000), 8% (TZS 270,001–520,000), 20% (TZS 520,001–760,000), 25% "
  "(TZS 760,001–1,000,000), and 30% (above TZS 1,000,000).",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act amendment to PAYE bands",
  "business_market", "adversarial"),

p("tier1a_paye_adv_002_20260609","paye_adversarial",
  "Fomu ya P45 inatumika Tanzania wakati mfanyakazi anaondoka kazini — je, hii ni kweli?",
  "Hapana. Fomu ya P45 ni fomu ya Uingereza (UK) na HAIPO Tanzania. Tanzania "
  "inatumia Hati ya Kuondoka (Leaving Certificate) na fomu ya P9 (taarifa ya mwaka "
  "ya PAYE). Mwajiri hutoa Hati ya Kuondoka kwa mfanyakazi anayeacha kazi, si P45.",
  "Form P45 is used in Tanzania when an employee leaves employment — is this true?",
  "No. Form P45 is a UK form and DOES NOT EXIST in Tanzania. Tanzania uses a "
  "Leaving Certificate and the P9 form (annual PAYE return). An employer issues a "
  "Leaving Certificate to a departing employee, not a P45.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA procedure update",
  "formal", "adversarial"),

p("tier1a_paye_adv_003_20260609","paye_adversarial",
  "Tarehe ya mwisho ya kuwasilisha P9 (taarifa ya mwaka ya PAYE) ni tarehe 31 Januari — je, hii ni kweli?",
  "Hapana. Tarehe ya mwisho ya kuwasilisha fomu ya P9 ni tarehe 31 MACHI — si "
  "31 Januari. Tarehe hii inahusu kipindi cha kutoa taarifa ya PAYE kwa mwaka mzima. "
  "Adhabu ya kutokutoa fomu ya P9 kwa wakati ni Shilingi 200,000.",
  "The deadline for submitting the P9 (annual PAYE return) is 31 January — is this true?",
  "No. The P9 submission deadline is 31 MARCH — not 31 January. This date applies "
  "to the annual PAYE reconciliation return. The penalty for late P9 submission "
  "is TZS 200,000.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act or TRA deadline change",
  "business_market", "adversarial"),

p("tier1a_paye_adv_004_20260609","paye_adversarial",
  "Adhabu ya kuchelewa kulipa PAYE ni asilimia 5 kwa kila mwezi — je, hii ni sahihi?",
  "Hapana. Adhabu ya kuchelewa kulipa PAYE ni asilimia 2.5 kwa mwezi — si asilimia "
  "5. Riba ya kisheria ya TRA pia inatumika juu ya adhabu hii. Jumla ya adhabu na "
  "riba inaweza kuwa kubwa kwa kipindi kirefu cha ucheleweshaji.",
  "The penalty for late PAYE payment is 5% per month — is this correct?",
  "No. The penalty for late PAYE payment is 2.5% per month — not 5%. TRA statutory "
  "interest also applies on top of this penalty. The combined penalty and interest "
  "can be substantial over an extended period of delay.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act or TRA penalty rate change",
  "formal", "adversarial"),

p("tier1a_paye_adv_005_20260609","paye_adversarial",
  "Kodi ya mwaka ya makato ya PAYE ya mfanyakazi mwenye mshahara wa Shilingi 8,000,000 kwa mwezi inahesabiwaje?",
  "Kwa mshahara wa Shilingi 8,000,000 kwa mwezi, PAYE inahesabika kwa kanda kama ifuatavyo: "
  "Shilingi 0: kanda ya asilimia sifuri (hadi 270,000). "
  "Shilingi 270,001–520,000 = Shilingi 250,000 × 8% = Shilingi 20,000. "
  "Shilingi 520,001–760,000 = Shilingi 240,000 × 20% = Shilingi 48,000. "
  "Shilingi 760,001–1,000,000 = Shilingi 240,000 × 25% = Shilingi 60,000. "
  "Zaidi ya 1,000,000 = Shilingi 7,000,000 × 30% = Shilingi 2,100,000. "
  "Jumla ya PAYE = Shilingi 2,228,000 kwa mwezi.",
  "How is monthly PAYE calculated for an employee earning TZS 8,000,000 per month?",
  "For a monthly salary of TZS 8,000,000 PAYE is banded as follows: "
  "TZS 0 at 0% (up to 270,000). "
  "TZS 270,001–520,000 = TZS 250,000 × 8% = TZS 20,000. "
  "TZS 520,001–760,000 = TZS 240,000 × 20% = TZS 48,000. "
  "TZS 760,001–1,000,000 = TZS 240,000 × 25% = TZS 60,000. "
  "Above 1,000,000 = TZS 7,000,000 × 30% = TZS 2,100,000. "
  "Total PAYE = TZS 2,228,000 per month.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act PAYE band change",
  "formal", "standard"),

p("tier1a_paye_adv_006_20260609","paye_adversarial",
  "Kiwango cha pili cha PAYE ni asilimia 9 tangu Finance Act 2023 — je, hii ni sahihi?",
  "Hapana. Kiwango cha pili cha PAYE ni asilimia 8 — hii haikubadilishwa hadi "
  "asilimia 9 na Finance Act 2023 wala Finance Act nyingine yoyote. Kanda ya "
  "asilimia 8 bado inatumika kwa mapato kati ya Shilingi 270,001 na 520,000 kwa mwezi. "
  "Kiwango cha asilimia 9 si sahihi chini ya sheria ya Tanzania.",
  "The second PAYE band is 9% since the Finance Act 2023 — is this correct?",
  "No. The second PAYE band is 8% — it was not changed to 9% by Finance Act 2023 or "
  "any other Finance Act. The 8% band still applies to income between TZS 270,001 "
  "and 520,000 per month. A rate of 9% is incorrect under Tanzania tax law.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act PAYE band change",
  "business_market", "adversarial"),

p("tier1a_paye_adv_007_20260609","paye_adversarial",
  "Kodi ya awali ya PAYE ya Shilingi sifuri inaendelea hadi mshahara wa Shilingi 300,000 kwa mwezi — je, hii ni sahihi?",
  "Hapana. Kanda ya asilimia sifuri ya PAYE inaendelea hadi Shilingi 270,000 kwa "
  "mwezi — si Shilingi 300,000. Mapato yanayozidi Shilingi 270,000 yanaanza "
  "kupigwa kodi ya asilimia 8 (kanda ya pili). Kiwango cha Shilingi 300,000 si sahihi.",
  "The zero-rate PAYE band continues up to TZS 300,000 per month — is this correct?",
  "No. The zero-rate PAYE band runs up to TZS 270,000 per month — not TZS 300,000. "
  "Income above TZS 270,000 starts being taxed at 8% (second band). "
  "The figure of TZS 300,000 is incorrect.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act PAYE band change",
  "business_market", "adversarial"),

p("tier1a_paye_adv_008_20260609","paye_adversarial",
  "P10 ni fomu ya mwaka ya PAYE inayowasilishwa mwezi Machi — je, hii ni sahihi?",
  "Hapana. P10 ni fomu ya KILA MWEZI (monthly PAYE remittance return) — si fomu ya "
  "mwaka. Fomu ya MWAKA ya PAYE ni P9 ambayo inawasilishwa ifikapo tarehe 31 Machi. "
  "P10 inalipwa na kuwasilishwa ifikapo tarehe 7 ya kila mwezi unaofuata.",
  "P10 is the annual PAYE return submitted in March — is this correct?",
  "No. P10 is the MONTHLY PAYE remittance return — not the annual return. The ANNUAL "
  "PAYE return is P9 which is submitted by 31 March. P10 is paid and submitted by "
  "the 7th of each following month.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA filing procedure change",
  "formal", "adversarial"),

p("tier1a_paye_adv_009_20260609","paye_adversarial",
  "PAYE haihusishi posho za usafiri — hizi zote zimefutwa kodi — je, ni kweli?",
  "Hapana. Posho nyingi zinazolipwa na mwajiri zinazidi mstari wa kisheria ZINATOZA "
  "PAYE. Posho za usafiri zinaweza kuwa exempt kama zinahusiana moja kwa moja na "
  "safari halisi za kazi na zina kiwango cha kawaida. Posho za jumla za usafiri "
  "zinazolipwa kila mwezi bila uhusiano na safari maalum za kazi zinatoza PAYE.",
  "PAYE does not apply to transport allowances — these are all tax-free — is this true?",
  "No. Many employer-paid allowances above the statutory threshold ARE subject to PAYE. "
  "Transport allowances may be exempt if directly linked to actual work travel and at a "
  "reasonable rate. General monthly transport allowances paid without linkage to specific "
  "work trips are subject to PAYE.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act allowance ruling",
  "business_market", "adversarial"),

p("tier1a_paye_adv_010_20260609","paye_adversarial",
  "Mfanyakazi ana haki ya kupata malipo yake yote ya PAYE kama rejesho baada ya mwisho wa mwaka — je, hii ni sahihi?",
  "Si sahihi kwa ujumla. Mfanyakazi anaweza kupata rejesho la PAYE tu ikiwa PAYE "
  "iliyokatwa inazidi kodi yake halisi ya mwaka. Hii inaweza kutokea ikiwa mfanyakazi "
  "alifanya kazi sehemu ya mwaka au alikuwa na makato ya ziada. Kuomba rejesho "
  "kunahitaji kuwasilisha PIT (Personal Income Tax) return kwa TRA.",
  "An employee is entitled to a full refund of all PAYE deducted after year end — is this correct?",
  "Not correct as a general rule. An employee can receive a PAYE refund only if PAYE "
  "deducted exceeds their actual annual tax liability. This may arise if the employee "
  "worked only part of the year or had excess deductions. Claiming a refund requires "
  "filing a PIT (Personal Income Tax) return with TRA.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA filing procedure",
  "formal", "adversarial"),

]  # end of pairs

written = 0
with open(OUT, "a", encoding="utf-8") as f:
    for pr in pairs:
        f.write(json.dumps(pr, ensure_ascii=False) + "\n")
        written += 1

total = sum(1 for _ in open(OUT, encoding="utf-8") if _.strip())
print(f"Part 2: wrote {written} pairs")
print(f"Total in file: {total}")
