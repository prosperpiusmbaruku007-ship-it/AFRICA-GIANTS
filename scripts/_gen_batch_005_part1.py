#!/usr/bin/env python3
"""batch_005 part 1 — permit_deep (50 pairs, 001-050)"""
import json, os

OUT = "datasets/tier1a/raw_sources/raw_pairs_batch_005.jsonl"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
D = "2026-06-09"
IMM = "https://www.immigration.go.tz"
IMM_N = "Immigration Services Department — Tanzania"
TANZLII = "https://www.tanzlii.org"
TANZLII_N = "TanzLII — Tanzania Legal Information Institute"
GP = "government_portal"
OG = "official_gazette"
ANN = "annual"
EVT = "event_triggered"
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
# PERMIT DEEP — work permits and immigration (50 pairs, 001-050)
# Source: immigration.go.tz | Immigration Act, GN 487A
# =====================================================================

p("tier1a_permit_deep_001_20260609","work_permits",
  "Aina za vibali vya kazi Tanzania ni zipi?",
  "Tanzania ina aina kuu za vibali vya kazi kwa wageni: Darasa A (mwekezaji/biashara "
  "binafsi), Darasa B (mfanyakazi aliyeajiriwa na kampuni), Darasa C (muda mfupi/mkataba "
  "wa muda), Darasa D (utafiti/uchunguzi wa madini), Darasa E (tegemezi wa mhitimu wa "
  "kibali), na Darasa G (huduma ya umma). Kila darasa lina mahitaji na ada tofauti.",
  "What are the classes of work permits in Tanzania?",
  "Tanzania has main work permit classes for foreigners: Class A (investor/self-employment), "
  "Class B (employed by a company), Class C (short-term/contract), Class D (research/"
  "prospecting), Class E (dependant of permit holder), and Class G (public service). "
  "Each class has different requirements and fees.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment or fee update",
  "formal", "standard"),

p("tier1a_permit_deep_002_20260609","work_permits",
  "Tofauti kati ya kibali cha kazi Darasa A na Darasa B ni nini?",
  "Darasa A ni kwa mwekezaji au mtu anayefanya biashara yake mwenyewe Tanzania — "
  "anapanga na kuwekeza mtaji wake mwenyewe. Darasa B ni kwa mfanyakazi aliyeajiriwa "
  "na kampuni Tanzania — mwajiri (kampuni) ndiye anayeomba kibali kwa niaba ya "
  "mfanyakazi huyo. Darasa A linahitaji ushahidi wa uwekezaji; Darasa B linahitaji "
  "mkataba wa ajira na ushahidi wa ujuzi wa kipekee.",
  "What is the difference between Class A and Class B work permits?",
  "Class A is for an investor or person running their own business in Tanzania — they "
  "invest their own capital. Class B is for an employee hired by a Tanzania company — "
  "the employer (company) applies for the permit on the worker's behalf. Class A requires "
  "proof of investment; Class B requires an employment contract and evidence of specialist "
  "skills.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "business_market", "disambiguation"),

p("tier1a_permit_deep_003_20260609","work_permits",
  "Kampuni inahitaji vibali ngapi vya kazi kwa wageni?",
  "Serikali inaweka kikwazo cha idadi ya vibali vya Darasa B kwa kila kampuni "
  "kulingana na idadi ya wafanyakazi wa Tanzania. Uwiano unaotakiwa kwa kawaida ni "
  "wageni wasizidi asilimia fulani ya wafanyakazi wote. Idara ya Uhamiaji ndio yenye "
  "mamlaka ya kuamua na kampuni inapaswa kuwasiliana nao moja kwa moja kwa mwongozo "
  "wa hali ya sasa.",
  "How many work permits can a company get for foreign employees?",
  "The government imposes a quota on Class B permits per company based on the number "
  "of Tanzanian employees. The required ratio generally means foreigners cannot exceed "
  "a certain percentage of total staff. The Immigration Department has authority to "
  "decide and companies should contact them directly for current quota guidance.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act or quota regulation change",
  "business_market", "standard"),

p("tier1a_permit_deep_004_20260609","work_permits",
  "Darasa B linahitaji sifa gani za mfanyakazi wa kigeni?",
  "Kibali cha Darasa B kinahitaji kwamba mfanyakazi wa kigeni ana ujuzi wa kipekee "
  "ambao haupatikani kwa urahisi kwa Watanzania. Mwajiri lazima aonyeshe: (1) alijaribu "
  "kuajiri Mtanzania kwanza, (2) mfanyakazi huyu ana sifa maalum zinazohitajika, na "
  "(3) anatoa mafunzo kwa wafanyakazi wa Tanzania ili hatimaye Mtanzania achukue nafasi hiyo.",
  "What qualifications does a Class B foreign worker need?",
  "A Class B permit requires the foreign worker to possess specialist skills not readily "
  "available from Tanzanians. The employer must show: (1) they tried to hire a Tanzanian "
  "first, (2) this specific worker has required specialist qualifications, and (3) they "
  "will train Tanzanian employees so a citizen can eventually fill the role.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "formal", "standard"),

p("tier1a_permit_deep_005_20260609","work_permits",
  "Kibali cha Darasa C (muda mfupi) kinamaanisha nini na kinatumika kwa nini?",
  "Kibali cha Darasa C ni kibali cha kazi cha muda mfupi kinachotolewa kwa wageni "
  "wanaofanya kazi ya mkataba wa muda maalum Tanzania. Kinatumika kwa: wataalam wa "
  "muda mfupi wanaokuja kufanya mradi maalum, washauri wa kimataifa, na watendaji "
  "wa mkataba wa muda. Muda wake ni mfupi kuliko Darasa B.",
  "What is a Class C (short-term) permit and when is it used?",
  "A Class C permit is a short-term work permit for foreigners performing fixed-term "
  "contract work in Tanzania. It is used for: short-term specialists coming to complete "
  "a specific project, international consultants, and fixed-term contract workers. "
  "Its duration is shorter than a Class B permit.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "business_market", "standard"),

p("tier1a_permit_deep_006_20260609","work_permits",
  "Mchakato wa kuomba kibali cha kazi Darasa B Tanzania unachukua muda gani?",
  "Mchakato wa kuomba kibali cha kazi Darasa B unachukua kwa kawaida wiki 4 hadi 8 "
  "kutoka tarehe ya kuwasilisha maombi kamili. Hatua ni: (1) mwajiri anawasilisha maombi "
  "na nyaraka zote kwa Idara ya Uhamiaji, (2) Idara inakagua na kutathmini, (3) kibali "
  "kinatolewa au kukataliwa. Maombi yaliyokosekana nyaraka yanachelewesha mchakato.",
  "How long does the Class B work permit application process take in Tanzania?",
  "The Class B work permit application typically takes 4 to 8 weeks from the date of "
  "a complete submission. Steps are: (1) employer submits application and all documents "
  "to the Immigration Department, (2) the Department reviews and assesses, (3) permit "
  "is issued or refused. Incomplete applications cause delays.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration processing time change",
  "business_market", "standard"),

p("tier1a_permit_deep_007_20260609","work_permits",
  "Kibali cha kazi kinahuishwa mara ngapi Tanzania?",
  "Vibali vya kazi Tanzania kwa kawaida vina muda wa miaka miwili na vinahuishwa "
  "kabla ya kumalizika. Mwajiri anapaswa kuomba uhuishaji angalau miezi 3 kabla ya "
  "tarehe ya kumalizika. Kushindwa kuhuisha kwa wakati kunaweza kusababisha mfanyakazi "
  "kuwa na hali ya haramu Tanzania.",
  "How often is a work permit renewed in Tanzania?",
  "Tanzania work permits typically have a 2-year validity and are renewed before expiry. "
  "The employer should apply for renewal at least 3 months before the expiry date. "
  "Failure to renew on time can result in the worker becoming undocumented in Tanzania.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "formal", "standard"),

p("tier1a_permit_deep_008_20260609","work_permits",
  "Je, mfanyakazi wa kigeni anaweza kufanya kazi Tanzania bila kibali cha kazi?",
  "Hapana. Mfanyakazi yeyote wa kigeni anayefanya kazi Tanzania lazima awe na kibali "
  "halali cha kazi. Kufanya kazi bila kibali ni kosa la jinai chini ya Sheria ya Uhamiaji. "
  "Adhabu zinajumuisha kufukuzwa nchini, faini, na mwajiri anayemruhusu mfanyakazi kufanya "
  "kazi bila kibali anaweza pia kuadhibiwa.",
  "Can a foreign worker work in Tanzania without a work permit?",
  "No. Any foreign worker employed in Tanzania must hold a valid work permit. Working "
  "without a permit is a criminal offence under the Immigration Act. Penalties include "
  "deportation, fines, and an employer who allows a worker to work without a permit "
  "can also be penalised.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "rural_conversational", "standard"),

p("tier1a_permit_deep_009_20260609","work_permits",
  "GN 487A inaathiri vipi wageni wanaofanya biashara Tanzania?",
  "GN 487A (Agizo la Uzuiaji wa Shughuli za Biashara kwa Wasio Raia) lilianza kutumika "
  "tarehe 28 Julai 2025. Linazuia raia wa kigeni kufanya shughuli 15 za biashara "
  "ikiwa ni pamoja na: biashara ya jumla na rejareja, uhamisho wa pesa ya simu, "
  "ukarabati wa simu, salon na nyingine. Adhabu: faini ya angalau Shilingi 10M + kifungo "
  "hadi miezi 6 + kufutwa kwa viza.",
  "How does GN 487A affect foreigners doing business in Tanzania?",
  "GN 487A (Business Licensing Prohibition of Business Activities for Non-Citizens Order) "
  "took effect on 28 July 2025. It prohibits foreign nationals from conducting 15 business "
  "activities including: wholesale/retail trade, mobile money transfers, phone repair, "
  "salon business and others. Penalties: minimum TZS 10M fine + up to 6 months "
  "imprisonment + visa revocation.",
  TANZLII, TANZLII_N, OG, "2025-07-28", EVT, "GN 487A amendment or replacement",
  "business_market", "standard"),

p("tier1a_permit_deep_010_20260609","work_permits",
  "Mtanzania anayemsaidia mgeni kufanya biashara iliyozuiwa ana adhabu gani?",
  "Raia wa Tanzania anayemsaidia mgeni kufanya biashara iliyozuiwa chini ya GN 487A "
  "anaweza kupewa: faini ya Shilingi 5,000,000 AU kifungo cha miezi 3. Hii inajumuisha "
  "kuweka jina lako kwenye biashara ya mgeni, kuwa 'front' au mwakilishi wa biashara "
  "hiyo, au kujumuishwa kwa njia nyingine yoyote.",
  "What penalty does a Tanzanian face for helping a foreigner conduct a prohibited business?",
  "A Tanzanian citizen who assists a foreigner in conducting a prohibited business "
  "under GN 487A can receive: a TZS 5,000,000 fine OR 3 months imprisonment. This "
  "includes fronting your name for a foreigner's business, acting as their business "
  "representative, or being involved in any other way.",
  TANZLII, TANZLII_N, OG, "2025-07-28", EVT, "GN 487A amendment",
  "business_market", "standard"),

p("tier1a_permit_deep_011_20260609","work_permits",
  "Mfanyakazi wa kigeni ana ruhusa ya kufanya kazi nyingi kwa waajiri tofauti kwa kibali kimoja?",
  "Hapana. Kibali cha kazi Tanzania kwa kawaida kinatolewa kwa mwajiri MMOJA maalum. "
  "Kufanya kazi kwa mwajiri mwingine bila ruhusa ya Idara ya Uhamiaji ni ukiukwaji wa "
  "masharti ya kibali. Mfanyakazi anayetaka kubadili mwajiri lazima aomba kibali kipya "
  "au urekebishaji wa kibali kilichopo.",
  "Can a foreign worker work for multiple employers with one permit?",
  "No. A Tanzania work permit is generally issued for ONE specific employer. Working "
  "for another employer without Immigration Department approval is a breach of permit "
  "conditions. A worker wishing to change employers must apply for a new permit or an "
  "amendment to the existing one.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "formal", "standard"),

p("tier1a_permit_deep_012_20260609","work_permits",
  "Mfanyakazi wa kigeni anayeomba Darasa B anahitaji vyeti vya elimu vilivyothibitishwa?",
  "Ndiyo. Ombi la Darasa B linahitaji vyeti vya elimu na uzoefu wa kazi vilivyothibitishwa. "
  "Hati za kigeni zinahitaji kuthibitishwa (notarised/apostille) na taasisi husika. "
  "Hii inathibitisha kwamba mfanyakazi ana sifa za kweli za uzoefu wa kipekee "
  "unaodaiwa kwenye ombi.",
  "Does a Class B foreign work permit application require certified educational certificates?",
  "Yes. A Class B application requires certified educational and work experience documents. "
  "Foreign documents need notarisation or apostille certification from the relevant "
  "authority. This verifies that the worker genuinely holds the specialist qualifications "
  "claimed in the application.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "formal", "standard"),

p("tier1a_permit_deep_013_20260609","work_permits",
  "Kibali cha kazi kinaweza kukataliwa — sababu za kawaida ni zipi?",
  "Sababu za kawaida za kukataliwa kwa kibali cha kazi ni: (1) ujuzi uliodaiwa unapatikana "
  "kwa Watanzania, (2) mwajiri ameshindwa kuthibitisha jaribio la kuajiri Mtanzania kwanza, "
  "(3) nyaraka za ombi ni kukosekana au si sahihi, (4) kampuni haikufuata mahitaji ya "
  "uwiano wa wafanyakazi, au (5) mombaji ana historia mbaya ya ukiukwaji wa uhamiaji.",
  "A work permit can be refused — what are the common reasons?",
  "Common reasons for work permit refusal include: (1) claimed skills are available from "
  "Tanzanians, (2) employer failed to demonstrate attempting to hire Tanzanians first, "
  "(3) application documents are missing or incorrect, (4) company did not meet employee "
  "ratio requirements, or (5) applicant has a history of immigration violations.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "business_market", "standard"),

p("tier1a_permit_deep_014_20260609","work_permits",
  "Nini kinatokea kama kibali cha kazi kimeisha muda kabla ya kuhuishwa?",
  "Ikiwa kibali cha kazi kimeisha muda bila kuhuishwa, mfanyakazi anawa na hali ya "
  "haramu kisheria Tanzania. Lazima waende Idara ya Uhamiaji haraka ili kurekebisha hali. "
  "Kuchelewa kunaweza kusababisha faini, na mwajiri pia ana wajibu wa kuhakikisha "
  "vibali vya wafanyakazi wake ni halali daima.",
  "What happens if a work permit expires before renewal?",
  "If a work permit expires without renewal the worker is in an unlawful status in Tanzania. "
  "They must go to the Immigration Department promptly to regularise. Delay can result "
  "in fines, and the employer also has a responsibility to ensure their workers' permits "
  "are always valid.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "rural_conversational", "standard"),

p("tier1a_permit_deep_015_20260609","work_permits",
  "Mwajiri anaweza kumfuta mfanyakazi wa kigeni bila kumrudisha nchini kwake — je, ana wajibu gani?",
  "Ikiwa mfanyakazi wa kigeni (Darasa B) anafutwa kazi, mwajiri ana wajibu wa: "
  "(1) kumwarifu Idara ya Uhamiaji kuhusu mwisho wa ajira, (2) kibali cha kazi "
  "kinaomba kufutwa au kuhuishwa kwa mwajiri mpya, na (3) kuhakikisha mfanyakazi "
  "anarudi katika hali ya halali. Mwajiri anaweza pia kubeba gharama za kurudi kwake.",
  "If an employer dismisses a foreign worker what immigration obligations apply?",
  "If a Class B foreign worker is dismissed, the employer must: (1) notify the "
  "Immigration Department of the end of employment, (2) the work permit needs to be "
  "cancelled or transferred to a new employer, and (3) ensure the worker returns to "
  "lawful status. The employer may also bear repatriation costs.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "formal", "standard"),

p("tier1a_permit_deep_016_20260609","work_permits",
  "Kibali cha Darasa B kinahitaji mkataba wa ajira uliothibitishwa na TRA?",
  "Hapana — mkataba wa ajira wa Darasa B hauhitaji kuthibitishwa na TRA hasa. "
  "Unahitaji: (1) mkataba wa ajira uliosaitiwa na pande zote, (2) uonyeshe mshahara "
  "uliopatikana, (3) uwe na kipindi halisi cha ajira kilichobainishwa. TRA inahusika "
  "na kodi (PAYE) inayotokana na mshahara, si uthibitisho wa mkataba wa uhamiaji.",
  "Does a Class B work permit require an employment contract certified by TRA?",
  "No — a Class B employment contract does not specifically require TRA certification. "
  "It needs: (1) a contract signed by both parties, (2) to show the agreed salary, "
  "(3) to have a defined employment period. TRA is involved in the tax (PAYE) on the "
  "salary, not in certifying the immigration contract.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "business_market", "disambiguation"),

p("tier1a_permit_deep_017_20260609","work_permits",
  "Mfanyakazi wa kigeni aliye Tanzania kwa visa ya utalii anaweza kuanza kazi bila kibali?",
  "Hapana kabisa. Visa ya utalii (tourist visa) hairuhusiwi kwa ajili ya kufanya kazi "
  "Tanzania. Mtu aliye Tanzania kwa visa ya utalii na anafanya kazi yoyote inayolipwa "
  "anakiuka sheria ya uhamiaji. Kabla ya kuanza kazi, mfanyakazi wa kigeni lazima "
  "apate kibali sahihi cha kazi kutoka Idara ya Uhamiaji.",
  "Can a foreigner on a tourist visa in Tanzania start working without a permit?",
  "Absolutely not. A tourist visa does not permit working in Tanzania. A person in "
  "Tanzania on a tourist visa who performs any paid work is in violation of immigration "
  "law. Before commencing employment a foreign worker must obtain the correct work "
  "permit from the Immigration Department.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "rural_conversational", "adversarial"),

p("tier1a_permit_deep_018_20260609","work_permits",
  "Darasa A — mwekezaji — linahitaji kiasi gani cha uwekezaji?",
  "Kibali cha Darasa A kinahitaji ushahidi wa uwekezaji halisi Tanzania. Kiwango cha "
  "chini cha uwekezaji kinaweza kutofautiana kulingana na sekta na aina ya biashara. "
  "Tanzania Investment Centre (TIC) ndiyo kitengo kinachohusika na uwekezaji wa kigeni "
  "na kinaweza kutoa mwongozo wa hali ya sasa kuhusu viwango vya chini vya uwekezaji.",
  "Class A — investor — what minimum investment amount is required?",
  "A Class A permit requires evidence of real investment in Tanzania. The minimum "
  "investment threshold can vary depending on the sector and type of business. The "
  "Tanzania Investment Centre (TIC) is the body responsible for foreign investment "
  "and can provide current guidance on minimum investment thresholds.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "TIC or Immigration Act update",
  "formal", "standard"),

p("tier1a_permit_deep_019_20260609","work_permits",
  "Kibali cha kazi kinahitajika kwa mwanachama wa familia ya mtu mwenye kibali?",
  "Mwanafamilia tegemezi (mke/mume, watoto) wa mtu mwenye kibali cha kazi anaweza "
  "kuomba kibali cha Darasa E (tegemezi). Kibali cha Darasa E kinaruhusu kukaa Tanzania "
  "lakini mara nyingi hakiidhinishi kufanya kazi. Ikiwa mwanafamilia anataka kufanya "
  "kazi, anahitaji kibali chake mwenyewe cha kazi cha darasa linalofaa.",
  "Is a work permit required for a family member of a permit holder?",
  "A dependent family member (spouse, children) of a work permit holder can apply for "
  "a Class E (dependant) permit. A Class E permit allows residence in Tanzania but "
  "typically does not authorise employment. If the family member wishes to work, they "
  "need their own separate work permit of the appropriate class.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "formal", "standard"),

p("tier1a_permit_deep_020_20260609","work_permits",
  "GN 487A inahusu vibali vya kazi au ni agizo tofauti?",
  "GN 487A na vibali vya kazi ni vitu viwili tofauti. Kibali cha kazi kinaruhusu mgeni "
  "kufanya kazi kwa mwajiri. GN 487A, kwa upande wake, kinakataza raia wa kigeni "
  "kufanya shughuli MAALUM za biashara (kama biashara ya rejareja, salon) bila kujali "
  "kama wana kibali cha kazi au la. Hata mgeni mwenye kibali halisi cha kazi hawezi "
  "kufanya biashara zilizozuiwa chini ya GN 487A.",
  "Is GN 487A about work permits or is it a separate order?",
  "GN 487A and work permits are two separate things. A work permit allows a foreigner "
  "to work for an employer. GN 487A separately prohibits foreign nationals from "
  "conducting SPECIFIC business activities (such as retail trade, salons) regardless "
  "of whether they hold a work permit. Even a foreigner with a valid work permit "
  "cannot engage in activities prohibited under GN 487A.",
  TANZLII, TANZLII_N, OG, "2025-07-28", EVT, "GN 487A amendment",
  "business_market", "disambiguation"),

# --- Adversarial pairs ---

p("tier1a_permit_deep_021_20260609","permit_adversarial",
  "Darasa B la kibali cha kazi ni kwa wawekezaji wa kigeni — je, hii ni sahihi?",
  "Hapana. Darasa B ni kwa mfanyakazi aliyeAJIRIWA na kampuni Tanzania — si mwekezaji. "
  "Darasa linalohusu wawekezaji ni Darasa A. Darasa B linahitaji mwajiri (kampuni) "
  "kuwasilisha maombi kwa niaba ya mfanyakazi wake wa kigeni aliyeajiriwa. Kuchanganya "
  "Darasa A na Darasa B ni kosa la kawaida la ombi.",
  "Class B work permit is for foreign investors — is this correct?",
  "No. Class B is for an employee HIRED by a Tanzania company — not an investor. "
  "The investor class is Class A. Class B requires the employer (company) to submit "
  "the application on behalf of their employed foreign worker. Confusing Class A and "
  "Class B is a common application error.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "business_market", "adversarial"),

p("tier1a_permit_deep_022_20260609","permit_adversarial",
  "Kibali cha Darasa C ni kwa wawekezaji wa muda wa miaka miwili — je, ni sahihi?",
  "Hapana. Darasa C ni kibali cha kazi cha MUDA MFUPI kwa wageni wanaofanya kazi ya "
  "mkataba wa muda — si kwa wawekezaji. Wawekezaji wa miaka miwili wanatumia Darasa A. "
  "Darasa C kinatumika kwa wataalam wa muda mfupi, washauri wa kimataifa, au kazi za "
  "mradi wa muda.",
  "Class C permit is for investors on a two-year period — is this correct?",
  "No. Class C is a SHORT-TERM work permit for foreigners doing fixed-term contract work "
  "— not for investors. Investors on a multi-year basis use Class A. Class C is for "
  "short-term specialists, international consultants, or project-based work.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "formal", "adversarial"),

p("tier1a_permit_deep_023_20260609","permit_adversarial",
  "Mgeni anaweza kufanya kazi Tanzania kwa visa ya utalii ikiwa atapata idhini ya mdomo "
  "kutoka mwajiri — je, hii inaruhuliwa?",
  "Hapana. Idhini ya mdomo kutoka mwajiri haina thamani ya kisheria kwa uhamiaji. "
  "Kufanya kazi kwa visa ya utalii ni kosa la kisheria hata kama mwajiri amekuambia "
  "ni sawa. Mfanyakazi wa kigeni LAZIMA apate kibali rasmi cha kazi kutoka Idara ya "
  "Uhamiaji kabla ya kuanza kazi yoyote inayolipwa Tanzania.",
  "A foreigner can work in Tanzania on a tourist visa if they get verbal approval from the employer — is this permitted?",
  "No. Verbal approval from an employer has no legal value for immigration purposes. "
  "Working on a tourist visa is a criminal offence even if the employer told you it "
  "is fine. A foreign worker MUST obtain a formal work permit from the Immigration "
  "Department before starting any paid work in Tanzania.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "rural_conversational", "adversarial"),

p("tier1a_permit_deep_024_20260609","permit_adversarial",
  "Mgeni mwenye kibali cha kazi Tanzania anaweza kufanya biashara ya rejareja — "
  "GN 487A haiwezi kumzuia kwa sababu ana kibali — je, ni kweli?",
  "Hapana. GN 487A inatumika BILA KUJALI kama mgeni ana kibali cha kazi au la. "
  "Biashara ya rejareja iko kwenye orodha ya shughuli 15 zilizozuiwa kwa raia wa "
  "kigeni chini ya GN 487A. Kibali cha kazi hakimpi mgeni ruhusa ya kufanya shughuli "
  "zilizozuiwa na GN 487A.",
  "A foreigner with a work permit can do retail trade — GN 487A cannot stop them because "
  "they have a permit — is this true?",
  "No. GN 487A applies REGARDLESS of whether a foreigner has a work permit or not. "
  "Retail trade is on the list of 15 activities prohibited for foreign nationals under "
  "GN 487A. A work permit does not give a foreigner permission to conduct activities "
  "prohibited by GN 487A.",
  TANZLII, TANZLII_N, OG, "2025-07-28", EVT, "GN 487A amendment",
  "business_market", "adversarial"),

p("tier1a_permit_deep_025_20260609","permit_adversarial",
  "Kibali cha kazi Tanzania kinahuisha kiotomatiki kila mwaka — mwajiri hahitaji "
  "kufanya chochote — je, ni kweli?",
  "Hapana. Kibali cha kazi HAIJUISHI kiotomatiki. Mwajiri lazima AOMBE uhuishaji "
  "kikamilifu angalau miezi 3 kabla ya kumalizika kwa kibali. Kutoomba kwa wakati "
  "kunaweza kusababisha mfanyakazi wa kigeni kuwa na hali ya haramu. "
  "Mwajiri ana wajibu wa kufuatilia tarehe za mwisho za vibali vyote vya wafanyakazi wake.",
  "A Tanzania work permit auto-renews every year — the employer doesn't need to do anything — is this true?",
  "No. Work permits do NOT auto-renew. The employer must ACTIVELY APPLY for renewal "
  "at least 3 months before the permit expires. Failing to apply on time can leave "
  "the foreign worker in an unlawful status. The employer has a responsibility to "
  "track all their workers' permit expiry dates.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "business_market", "adversarial"),

p("tier1a_permit_deep_026_20260609","permit_adversarial",
  "Mwajiri asiye na TIN hawezi kuomba kibali cha kazi kwa mfanyakazi wake wa kigeni — je, ni kweli?",
  "Ndiyo, hii ni kweli kwa sababu sahihi. Mwajiri Tanzania lazima awe amesajiliwa "
  "kisheria (na BRELA na TRA) kabla ya kuomba kibali cha kazi kwa mfanyakazi wa kigeni. "
  "Ushahidi wa usajili wa kisheria wa kampuni na TIN ni sehemu ya nyaraka za ombi "
  "la kibali cha kazi. Kampuni isiyosajiliwa haiwezi kuwa mwajiri halisi wa mfanyakazi wa kigeni.",
  "An employer without a TIN cannot apply for a work permit for their foreign worker — is this correct?",
  "Yes, this is correct for good reason. A Tanzania employer must be legally registered "
  "(with BRELA and TRA) before applying for a work permit for a foreign employee. "
  "Evidence of company legal registration and TIN is part of the work permit application "
  "documents. An unregistered company cannot be a lawful employer of a foreign worker.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "business_market", "standard"),

p("tier1a_permit_deep_027_20260609","permit_adversarial",
  "Adhabu ya mgeni kufanya kazi bila kibali ni kama ile ya mgeni kufanya biashara "
  "iliyozuiwa chini ya GN 487A — je, viwango ni sawa?",
  "Hapana, viwango si sawa. Kufanya kazi bila kibali cha kazi: adhabu ya jumla chini "
  "ya Sheria ya Uhamiaji. Kufanya biashara iliyozuiwa chini ya GN 487A: faini ya angalau "
  "Shilingi 10,000,000 + kifungo hadi miezi 6 + kufutwa kwa viza — viwango maalum zaidi "
  "na vikali zaidi. GN 487A ina viwango vya adhabu vilivyobainishwa wazi.",
  "The penalty for a foreigner working without a permit is the same as for conducting "
  "a GN 487A-prohibited business — are the levels the same?",
  "No, the levels are not the same. Working without a work permit: general penalty under "
  "the Immigration Act. Conducting a GN 487A-prohibited business: minimum TZS 10,000,000 "
  "fine + up to 6 months imprisonment + visa revocation — more specific and harsher. "
  "GN 487A has clearly stated penalty levels.",
  TANZLII, TANZLII_N, OG, "2025-07-28", EVT, "GN 487A amendment",
  "formal", "adversarial"),

p("tier1a_permit_deep_028_20260609","permit_adversarial",
  "Mfanyakazi wa kigeni anaweza kubadilisha mwajiri bila kuomba kibali kipya "
  "kwa sababu kibali chake bado ni halali — je, ni sahihi?",
  "Hapana. Kibali cha Darasa B kinaambatanishwa na mwajiri MAALUM aliyetajwa kwenye kibali. "
  "Kubadilisha mwajiri bila kibali kipya au marekebisho ya kibali kilichopo ni ukiukwaji. "
  "Mfanyakazi lazima apate kibali kipya kinachomtaja mwajiri mpya, au mwajiri mpya "
  "aomba uhamisho rasmi kutoka Idara ya Uhamiaji.",
  "A foreign worker can change employer without applying for a new permit because their "
  "permit is still valid — is this correct?",
  "No. A Class B permit is tied to the SPECIFIC employer named on the permit. Changing "
  "employers without a new permit or amendment to the existing one is a violation. "
  "The worker must obtain a new permit naming the new employer, or the new employer "
  "must apply for a formal transfer from the Immigration Department.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "formal", "adversarial"),

# --- Disambiguation pairs ---

p("tier1a_permit_deep_029_20260609","permit_disambiguation",
  "Tofauti kati ya kibali cha kazi (work permit) na ruhusa ya kukaa (residence permit) ni nini?",
  "Kibali cha kazi (work permit) kinaruhusu mgeni kufanya kazi maalum na mwajiri maalum "
  "Tanzania. Ruhusa ya kukaa (residence permit) kinaruhusu mgeni kukaa Tanzania kwa "
  "muda mrefu lakini si lazima kufanya kazi. Mfanyakazi wa kigeni mara nyingi anahitaji "
  "vyote viwili — kibali cha kazi kwa ajili ya ajira yake NA ruhusa ya kukaa kwa ajili "
  "ya makazi yake Tanzania.",
  "What is the difference between a work permit and a residence permit?",
  "A work permit authorises a foreigner to perform specific work with a specific employer "
  "in Tanzania. A residence permit authorises a foreigner to live in Tanzania long-term "
  "but does not necessarily authorise employment. A foreign worker often needs both — "
  "a work permit for their employment AND a residence permit for their residence in Tanzania.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "formal", "disambiguation"),

p("tier1a_permit_deep_030_20260609","permit_disambiguation",
  "Tofauti kati ya GN 487A na kibali cha kazi ni nini — vinafanya kazi pamoja vipi?",
  "Kibali cha kazi kinahusu UAJIRIWA (mgeni anayefanya kazi kwa mwajiri). GN 487A "
  "kinahusu UMILIKI/UENDESHAJI wa biashara fulani. Vinafanya kazi pamoja kwa njia hii: "
  "mgeni anaweza kuwa na kibali cha kazi halali lakini BADO asiendeshee biashara "
  "zilizozuiwa na GN 487A. Uzingatiaji wote wawili ni wa lazima — hawabadilishi mwingine.",
  "What is the difference between GN 487A and a work permit — how do they work together?",
  "A work permit relates to EMPLOYMENT (a foreigner working for an employer). GN 487A "
  "relates to OWNERSHIP/OPERATION of certain businesses. They work together like this: "
  "a foreigner can hold a valid work permit but STILL cannot operate businesses prohibited "
  "by GN 487A. Compliance with both is mandatory — they do not substitute for each other.",
  TANZLII, TANZLII_N, OG, "2025-07-28", EVT, "GN 487A amendment",
  "business_market", "disambiguation"),

# --- More standard pairs ---

p("tier1a_permit_deep_031_20260609","work_permits",
  "Mwajiri analazimika kuwasilisha nyaraka zipi kuomba Darasa B?",
  "Nyaraka za kawaida zinazohitajika kwa ombi la Darasa B ni: (1) fomu ya ombi "
  "iliyojazwa, (2) nakala ya pasipoti ya mombaji, (3) nakala ya vyeti vya elimu "
  "na uzoefu wa kazi (zilizothibitishwa), (4) mkataba wa ajira uliosainwa, (5) hati "
  "za kampuni (certificate of incorporation, TIN), (6) ushahidi wa jaribio la kuajiri "
  "Mtanzania kwanza, na (7) picha za pasipoti.",
  "What documents must an employer submit to apply for a Class B permit?",
  "Standard documents required for a Class B application include: (1) completed "
  "application form, (2) copy of applicant's passport, (3) certified copies of "
  "educational certificates and work experience, (4) signed employment contract, "
  "(5) company documents (certificate of incorporation, TIN), (6) evidence of attempting "
  "to hire a Tanzanian first, and (7) passport photos.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Department requirements update",
  "formal", "standard"),

p("tier1a_permit_deep_032_20260609","work_permits",
  "Idara ya Uhamiaji Tanzania inafanya kazi saa ngapi na iko wapi?",
  "Idara ya Uhamiaji ya Tanzania ina makao makuu Dar es Salaam na ofisi za mikoa "
  "kote nchini. Maombi ya vibali vya kazi yanaweza kuwasilishwa kwenye ofisi kuu "
  "au ofisi za mkoa. Angalia tovuti ya immigration.go.tz kwa maelezo ya hali ya sasa "
  "ya saa za kufanya kazi, anwani, na taratibu za maombi mtandaoni.",
  "What are the Tanzania Immigration Department's hours and where is it located?",
  "The Tanzania Immigration Department has its headquarters in Dar es Salaam and "
  "regional offices across the country. Work permit applications can be submitted at "
  "the main office or regional offices. Check immigration.go.tz for current operating "
  "hours, addresses, and online application procedures.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Department operational update",
  "rural_conversational", "standard"),

p("tier1a_permit_deep_033_20260609","work_permits",
  "Kampuni inaweza kuomba vibali vingi vya kazi kwa wakati mmoja?",
  "Ndiyo. Kampuni inaweza kuwasilisha maombi mengi ya vibali vya kazi kwa wakati mmoja "
  "kwa wafanyakazi tofauti wa kigeni. Hata hivyo, kila ombi linashughulikia mfanyakazi "
  "mmoja mmoja na linahitaji nyaraka kamili. Idadi ya vibali vya jumla iko chini ya kikwazo "
  "cha uwiano wa wafanyakazi wa kampuni.",
  "Can a company apply for multiple work permits simultaneously?",
  "Yes. A company can submit multiple work permit applications at the same time for "
  "different foreign workers. However, each application covers one individual worker "
  "and requires complete documentation. The total number of permits is subject to the "
  "company's employee ratio quota.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "business_market", "standard"),

p("tier1a_permit_deep_034_20260609","work_permits",
  "Kibali cha kazi kinaweza kuhamishiwa kampuni nyingine bila kuomba upya?",
  "Kwa kawaida, kibali cha kazi Tanzania hakim transfer otomatiki kwa kampuni nyingine. "
  "Mabadiliko ya mwajiri yanahitaji mchakato rasmi wa uhamiaji — ama kuomba kibali kipya "
  "au marekebisho ya kibali kilichopo kupitia Idara ya Uhamiaji. Omba ushauri kutoka "
  "Idara ya Uhamiaji kwa hali maalum.",
  "Can a work permit be transferred to a different company without reapplying?",
  "Generally, a Tanzania work permit does not transfer automatically to another company. "
  "A change of employer requires a formal immigration process — either a new permit "
  "application or an amendment to the existing permit through the Immigration Department. "
  "Seek guidance from the Immigration Department for specific circumstances.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "business_market", "standard"),

p("tier1a_permit_deep_035_20260609","work_permits",
  "Je, GN 487A inaathiri wawekezaji wa kigeni wanaoweka mtaji Tanzania?",
  "GN 487A inahusu shughuli MAALUM za biashara ya kila siku — kama biashara ya rejareja, "
  "salon, na uhamisho wa pesa ya simu. Uwekezaji wa mtaji mkubwa (kama kujenga hoteli, "
  "kiwanda, au mradi wa miundombinu) kwa kawaida HAUATHIRIWI na GN 487A. Shughuli "
  "zilizozuiwa ni za biashara ndogo ndogo — si uwekezaji mkubwa wa kimkakati.",
  "Does GN 487A affect foreign investors placing capital in Tanzania?",
  "GN 487A concerns SPECIFIC everyday trade activities — such as retail trade, salons, "
  "and mobile money transfers. Large capital investment (such as building a hotel, "
  "factory, or infrastructure project) is generally NOT affected by GN 487A. The "
  "prohibited activities are small-business trades — not large strategic investments.",
  TANZLII, TANZLII_N, OG, "2025-07-28", EVT, "GN 487A amendment",
  "formal", "standard"),

p("tier1a_permit_deep_036_20260609","work_permits",
  "Mfanyakazi wa kigeni anaweza kufanya kazi kwa masaa ya ziada nje ya masaa ya "
  "mkataba wake — je, kinaathiri kibali chake?",
  "Masaa ya ziada ya mfanyakazi wa kigeni kwa mwajiri WAKE MWENYEWE hayaathiri kibali "
  "chake — ni sehemu ya mkataba wake wa ajira na mwajiri aliyetajwa kwenye kibali. "
  "Tatizo linatokea ikiwa 'overtime' ni kwa mwajiri WA PILI — hiyo itahitaji ruhusa "
  "ya ziada ya uhamiaji.",
  "Can a foreign worker do overtime outside their contract hours — does it affect their permit?",
  "Overtime for the foreign worker's OWN employer does not affect their permit — it "
  "is part of their employment relationship with the employer named on the permit. "
  "The problem arises if the 'overtime' is for a SECOND employer — that would require "
  "additional immigration authorisation.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "formal", "standard"),

p("tier1a_permit_deep_037_20260609","work_permits",
  "Orodha ya shughuli 15 zilizozuiwa kwa wageni chini ya GN 487A ni zipi?",
  "GN 487A inazuia raia wa kigeni kufanya shughuli hizi: biashara ya jumla na rejareja, "
  "uhamisho wa pesa ya simu (mobile money), ukarabati wa simu, salon na kinyozi, "
  "na shughuli nyingine 11 zilizo kwenye jedwali la GN 487A. Kwa orodha kamili ya shughuli "
  "15, angalia gazeti rasmi la serikali (GN 487A ya tarehe 28 Julai 2025) au "
  "tanzlii.org.",
  "What are the 15 business activities prohibited for foreigners under GN 487A?",
  "GN 487A prohibits foreign nationals from conducting: wholesale and retail trade, "
  "mobile money transfers, phone repair, salon and barber businesses, and 11 other "
  "activities listed in the GN 487A schedule. For the full list of all 15 activities "
  "see the official Government Gazette (GN 487A dated 28 July 2025) or tanzlii.org.",
  TANZLII, TANZLII_N, OG, "2025-07-28", EVT, "GN 487A amendment",
  "formal", "standard"),

p("tier1a_permit_deep_038_20260609","work_permits",
  "Mgeni anayekaa Tanzania kwa sababu za familia (si kazi) anahitaji kibali cha kazi?",
  "Ikiwa mgeni anakaa Tanzania tu kwa sababu za familia (kama mke/mume wa raia wa "
  "Tanzania) na hafanyi kazi inayolipwa, kwa kawaida anahitaji ruhusa ya kukaa "
  "(residence permit) badala ya kibali cha kazi. Ikiwa ataanza kufanya kazi yoyote "
  "inayolipwa, atalazimika kuomba kibali cha kazi kinachofaa.",
  "A foreigner staying in Tanzania for family reasons (not work) — do they need a work permit?",
  "If a foreigner is in Tanzania purely for family reasons (such as being married to "
  "a Tanzanian citizen) and does no paid work, they generally need a residence permit "
  "rather than a work permit. If they begin any paid employment, they will need to "
  "apply for the appropriate work permit.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "rural_conversational", "standard"),

p("tier1a_permit_deep_039_20260609","work_permits",
  "Mwajiri anayeomba Darasa B lazima athibitishe kwamba alitangaza kazi nchini Tanzania kwanza?",
  "Ndiyo. Mwajiri lazima aonyeshe ushahidi kwamba alijaribu kuajiri Mtanzania wenye sifa "
  "kabla ya kuomba mfanyakazi wa kigeni. Hii mara nyingi inajumuisha: nakala za matangazo "
  "ya kazi (newspapers, job boards), rekodi za waombaji wa Tanzania waliohojiwa, na "
  "maelezo ya kwa nini hawakuwa na sifa. Hii ni sehemu muhimu ya ombi la Darasa B.",
  "Must an employer applying for Class B prove they advertised the job in Tanzania first?",
  "Yes. The employer must show evidence of attempting to recruit a qualified Tanzanian "
  "before applying for a foreign worker. This typically includes: copies of job "
  "advertisements (newspapers, job boards), records of Tanzanian applicants interviewed, "
  "and explanation of why they were not qualified. This is a critical part of any "
  "Class B application.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "business_market", "standard"),

p("tier1a_permit_deep_040_20260609","work_permits",
  "Kampuni inaweza kuomba kibali cha kazi kwa mgeni kabla ya kumwajiri rasmi?",
  "Ndiyo. Mara nyingi mwajiri anaomba kibali cha kazi kabla ya mfanyakazi kufika Tanzania "
  "ili mfanyakazi aweze kuja na kujiunga mara moja. Hii inaitwa ombi la kibali kabla ya "
  "kufika. Mkataba wa ajira uliosainwa unahitajika kama sehemu ya ombi, lakini "
  "mfanyakazi anaweza bado kuwa nje ya Tanzania wakati ombi linashughulikiwa.",
  "Can a company apply for a work permit for a foreigner before officially hiring them?",
  "Yes. Often an employer applies for a work permit before the employee arrives in "
  "Tanzania so the worker can join immediately on arrival. This is called a pre-arrival "
  "permit application. A signed employment contract is required as part of the application "
  "but the worker may still be outside Tanzania while the application is processed.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "formal", "standard"),

p("tier1a_permit_deep_041_20260609","work_permits",
  "Utekelezaji wa GN 487A unafanywa na idara gani na kwa wakati gani?",
  "GN 487A inatekelezwa na Idara ya Huduma za Uhamiaji. Utekelezaji mkubwa ulifanywa "
  "kati ya tarehe 11 Septemba na 8 Oktoba 2025 — mazoezi ya ukaguzi wa biashara katika "
  "maeneo ya biashara ya Tanzania. Maofisa wa uhamiaji walikuwa na mamlaka ya kukagua "
  "biashara, kuuliza hati, na kuchukua hatua dhidi ya wavunjaji.",
  "Which department enforces GN 487A and during what period?",
  "GN 487A is enforced by the Immigration Services Department. A major enforcement "
  "exercise was conducted between 11 September and 8 October 2025 — a business inspection "
  "exercise at Tanzania's commercial areas. Immigration officers had authority to inspect "
  "businesses, demand documents, and take action against violators.",
  TANZLII, TANZLII_N, OG, "2025-07-28", EVT, "GN 487A enforcement update",
  "formal", "standard"),

p("tier1a_permit_deep_042_20260609","work_permits",
  "Mtu wa kigeni akilazimika kwenda nje ya Tanzania kwa muda mfupi — kibali chake "
  "kinaendelea kufanya kazi?",
  "Ndiyo, kibali cha kazi cha Tanzania kinaendelea kutumika kwa ujumla hata ikiwa "
  "mhusika anaondoka Tanzania kwa muda mfupi (kama safari ya biashara au familia). "
  "Hata hivyo, visas vya kuingia tena (re-entry visas) vinaweza kuhitajika kulingana "
  "na uraia wa mhusika na masharti ya eneo lake. Angalia Idara ya Uhamiaji kwa masharti "
  "ya hali yako.",
  "If a foreigner must leave Tanzania briefly — does their work permit remain valid?",
  "Yes, a Tanzania work permit generally continues to be valid even if the holder leaves "
  "Tanzania briefly (such as for a business trip or family visit). However, re-entry "
  "visas may be required depending on the holder's nationality and visa conditions. "
  "Check with the Immigration Department for requirements in your specific situation.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "business_market", "standard"),

p("tier1a_permit_deep_043_20260609","work_permits",
  "Mfanyakazi wa kigeni ana haki ya kupata nakala ya kibali chake mwenyewe?",
  "Ndiyo. Mfanyakazi wa kigeni ana haki ya kupata na kushikilia nakala ya kibali chake "
  "cha kazi. Hati hii inaonyesha hali yake ya kisheria ya kufanya kazi Tanzania. "
  "Ni busara kubeba nakala ya kibali wakati wa kufanya kazi au kusafiri Tanzania kwa "
  "madhumuni ya kazi.",
  "Is a foreign worker entitled to receive a copy of their own work permit?",
  "Yes. A foreign worker is entitled to receive and hold a copy of their work permit. "
  "This document demonstrates their lawful employment status in Tanzania. It is advisable "
  "to carry a copy of the permit when working or travelling in Tanzania for work purposes.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "rural_conversational", "standard"),

p("tier1a_permit_deep_044_20260609","work_permits",
  "Kampuni ya NGO ya kigeni inafuata sheria sawa ya vibali vya kazi kama kampuni ya faida?",
  "Ndiyo. NGO za kigeni zinahitaji vibali vya kazi kwa wafanyakazi wao wa kigeni "
  "kama kampuni za faida. Sheria ya Uhamiaji inatumika bila kujali aina ya shirika. "
  "NGO inayoshindwa kupata vibali vya kazi kwa wafanyakazi wake wa kigeni inakiuka "
  "sheria ya uhamiaji.",
  "Does a foreign NGO follow the same work permit laws as a for-profit company?",
  "Yes. Foreign NGOs need work permits for their foreign workers just like for-profit "
  "companies. The Immigration Act applies regardless of the type of organisation. "
  "An NGO that fails to obtain work permits for its foreign workers is in violation "
  "of immigration law.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "formal", "standard"),

p("tier1a_permit_deep_045_20260609","work_permits",
  "Kibali cha kazi kinaathiriwa na mabadiliko ya jina au muundo wa kampuni?",
  "Ndiyo. Ikiwa kampuni inabadilisha jina au muundo wake (kwa mfano, uundaji upya au "
  "ununuzi na kampuni nyingine), vibali vya kazi vilivyopo vinaweza kuhitaji "
  "kusasishwa au kubadilishwa ili kuonyesha mabadiliko hayo. Mwajiri anapaswa kuwasiliana "
  "na Idara ya Uhamiaji mara tu mabadiliko ya muundo wa kampuni yanapotokea.",
  "Is a work permit affected by a change of company name or structure?",
  "Yes. If a company changes its name or structure (for example, through a restructuring "
  "or acquisition), existing work permits may need to be updated or reissued to reflect "
  "the changes. The employer should contact the Immigration Department as soon as any "
  "corporate structural changes occur.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "business_market", "standard"),

p("tier1a_permit_deep_046_20260609","work_permits",
  "Je, mzigo wa kuthibitisha ujuzi wa kipekee wa mfanyakazi wa kigeni uko kwa mwajiri au mfanyakazi?",
  "Mzigo wa kuthibitisha uko KWA MWAJIRI. Ni mwajiri — si mfanyakazi — anayepaswa "
  "kuwasilisha ushahidi kwa Idara ya Uhamiaji kwamba: ujuzi uliodaiwa ni wa kipekee, "
  "hautapatikana kwa Watanzania, na jaribio la kweli la kuajiri Mtanzania lilifanywa. "
  "Mwajiri ambaye hatekelezi ushahidi huu atalipiga ombi lake.",
  "Does the burden of proving a foreign worker's specialist skills lie with the employer or the worker?",
  "The burden of proof lies with the EMPLOYER. It is the employer — not the worker — "
  "who must submit evidence to the Immigration Department that: the claimed skills are "
  "specialist, are not available from Tanzanians, and a genuine attempt to hire "
  "a Tanzanian was made. An employer who fails to supply this evidence will have their "
  "application rejected.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "formal", "standard"),

p("tier1a_permit_deep_047_20260609","work_permits",
  "Mgeni aliyeomba vibali lakini bado anasubiri jibu — anaweza kuanza kufanya kazi?",
  "Hapana. Kuwasilisha ombi la kibali cha kazi HAKUTOI ruhusa ya kufanya kazi wakati "
  "wa kusubiri jibu. Mfanyakazi wa kigeni lazima APOKEE kibali halisi kilichotolewa "
  "kabla ya kuanza kufanya kazi. Kufanya kazi wakati ombi linaendelea ni ukiukwaji "
  "wa sheria ya uhamiaji.",
  "A foreigner who has applied for a permit but is still awaiting a decision — can they start working?",
  "No. Submitting a work permit application does NOT grant permission to work while "
  "awaiting the decision. A foreign worker must RECEIVE the actual issued permit before "
  "commencing employment. Working while an application is pending is a violation of "
  "immigration law.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "business_market", "adversarial"),

p("tier1a_permit_deep_048_20260609","work_permits",
  "Mfanyakazi wa kigeni anayefanya utafiti (research) Tanzania anahitaji aina gani ya kibali?",
  "Mfanyakazi wa kigeni anayefanya utafiti au uchunguzi (kama utafiti wa kisayansi, "
  "uchunguzi wa madini) anahitaji kibali cha Darasa D. Darasa D ni maalum kwa "
  "utafiti na uchunguzi wa rasilimali asili. Inatofautiana na Darasa B (ajira ya kawaida) "
  "kwa sababu utafiti una asili na masharti tofauti.",
  "What type of permit does a foreigner conducting research in Tanzania need?",
  "A foreigner conducting research or prospecting (such as scientific research or "
  "mineral prospecting) needs a Class D permit. Class D is specific to research and "
  "natural resource prospecting. It differs from Class B (regular employment) because "
  "research has a different nature and conditions.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "rural_conversational", "standard"),

p("tier1a_permit_deep_049_20260609","work_permits",
  "Je, kampuni inaweza kumrudisha nyumbani mfanyakazi wake wa kigeni bila ya kumwarifu Idara ya Uhamiaji?",
  "Hapana. Ikiwa mfanyakazi wa kigeni anaondoka Tanzania (kwa hiari au kufutwa kazi), "
  "mwajiri ana wajibu wa kumwarifu Idara ya Uhamiaji. Kushindwa kumwarifu "
  "kunaweza kusababisha matatizo ya siku zijazo kwa kampuni katika maombi mengine ya "
  "vibali na inaweza kuathiri rekodi ya uzingatiaji wa uhamiaji wa kampuni.",
  "Can a company repatriate a foreign worker without notifying the Immigration Department?",
  "No. When a foreign worker leaves Tanzania (whether voluntarily or through dismissal), "
  "the employer has an obligation to notify the Immigration Department. Failure to "
  "notify can cause complications for future permit applications and may affect the "
  "company's immigration compliance record.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "Immigration Act amendment",
  "formal", "standard"),

p("tier1a_permit_deep_050_20260609","work_permits",
  "Je, mfanyakazi wa kigeni ana haki za kazi sawa na Watanzania chini ya ELRA?",
  "Ndiyo. Mfanyakazi wa kigeni anayefanya kazi Tanzania kwa kibali halisi cha kazi "
  "ana haki za kimsingi za kazi chini ya Sheria ya Ajira na Mahusiano ya Kazini (ELRA) "
  "— ikiwa ni pamoja na haki ya mshahara wa chini wa GN 605A, likizo ya mwaka, "
  "ulinzi dhidi ya kufutwa kazi bila sababu, na nyinginezo. Uraia wake haunyimi "
  "haki za kimsingi za kazi.",
  "Does a foreign worker have the same employment rights as Tanzanians under ELRA?",
  "Yes. A foreign worker lawfully employed in Tanzania with a valid work permit has "
  "basic employment rights under the Employment and Labour Relations Act (ELRA) — "
  "including the right to GN 605A minimum wage, annual leave, protection from unfair "
  "dismissal, and others. Their foreign nationality does not strip them of basic "
  "employment rights.",
  IMM, IMM_N, GP, "2008-01-01", ANN, "ELRA or Immigration Act amendment",
  "formal", "standard"),

]

written = 0
with open(OUT, "a", encoding="utf-8") as f:
    for pr in pairs:
        f.write(json.dumps(pr, ensure_ascii=False) + "\n")
        written += 1

total = sum(1 for _ in open(OUT, encoding="utf-8") if _.strip())
print(f"Part 1: wrote {written} pairs to {OUT}")
print(f"Total in file: {total}")
