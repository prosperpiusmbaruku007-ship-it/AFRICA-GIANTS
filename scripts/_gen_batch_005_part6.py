#!/usr/bin/env python3
"""batch_005 part 6 — osha_nssf_adversarial (50 pairs, 251-300)"""
import json, os

OUT = "datasets/tier1a/raw_sources/raw_pairs_batch_005.jsonl"
D = "2026-06-09"
OSHA = "https://www.osha.go.tz"
OSHA_N = "OSHA — Occupational Safety and Health Authority Tanzania"
NSSF = "https://www.nssf.or.tz"
NSSF_N = "NSSF — National Social Security Fund Tanzania"
WCF = "https://portal.wcf.go.tz"
WCF_N = "WCF — Workers Compensation Fund Tanzania"
TANZLII = "https://www.tanzlii.org"
TANZLII_N = "TanzLII — Tanzania Legal Information Institute"
GP = "government_portal"
OG = "official_gazette"
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
# OSHA + NSSF ADVERSARIAL — 50 pairs (251-300)
# =====================================================================

p("tier1a_osha_nssf_251_20260609","osha_adversarial",
  "OSHA Tanzania inasimamia usalama wa mahali pa kazi tu — si afya ya wafanyakazi — je, ni sahihi?",
  "Hapana. Jina kamili ni Mamlaka ya Usalama na Afya Mahali pa Kazi (Occupational "
  "Safety and HEALTH Authority). OSHA inasimamia ZOTE MBILI: usalama wa mazingira "
  "ya kazi (vifaa salama, miundo ya jengo, hatari za mashine) NA afya ya wafanyakazi "
  "(ugonjwa wa kazini, kemikali hatari, kelele, joto). Dhana kwamba OSHA ni ya "
  "'usalama tu' ni kosa la kawaida.",
  "OSHA Tanzania only supervises workplace safety — not worker health — is this correct?",
  "No. The full name is Occupational Safety and HEALTH Authority. OSHA supervises "
  "BOTH: workplace environment safety (safe equipment, building structure, machine "
  "hazards) AND worker health (occupational disease, hazardous chemicals, noise, "
  "heat). The notion that OSHA is 'only about safety' is a common error.",
  OSHA, OSHA_N, GP, "2003-01-01", ANN, "OSHA Act amendment",
  "business_market", "adversarial"),

p("tier1a_osha_nssf_252_20260609","osha_adversarial",
  "Biashara yenye wafanyakazi 5 tu Tanzania hailazimiki kusajili OSHA — je, kizingiti ni wafanyakazi wangapi?",
  "OSHA Act Tanzania inaitaji mwajiri mwenye wafanyakazi 10 AU ZAIDI kwenye "
  "Mainland Tanzania kusajili OSHA. Biashara yenye wafanyakazi 5 tu HAIHITAJIKI "
  "kusajili OSHA kisheria. Hata hivyo, hata biashara ndogo zinazidi kizingiti "
  "bado zinatakiwa kufuata kanuni za msingi za usalama mahali pa kazi.",
  "A business with only 5 workers in Tanzania doesn't need to register with OSHA "
  "— how many employees is the threshold?",
  "The OSHA Act in Tanzania requires an employer with 10 OR MORE employees on "
  "Mainland Tanzania to register with OSHA. A business with only 5 workers is NOT "
  "legally required to register with OSHA. However, even smaller businesses that "
  "exceed the threshold are still required to follow basic workplace safety rules.",
  OSHA, OSHA_N, GP, "2003-01-01", ANN, "OSHA Act amendment",
  "business_market", "standard"),

p("tier1a_osha_nssf_253_20260609","osha_adversarial",
  "Mkaguzi wa OSHA anaweza kuingia mahali pa kazi bila notisi — je, hii inaruhusiwa kisheria?",
  "Ndiyo. Wakaguzi wa OSHA Tanzania wana mamlaka ya kisheria ya kuingia mahali "
  "pa kazi bila notisi ya mapema kwa madhumuni ya ukaguzi wa usalama. Hii ni "
  "nguvu ya kisheria chini ya OSHA Act ili kuhakikisha ukaguzi wa kweli — sio "
  "ukaguzi wa kuandaliwa. Mwajiri ana wajibu wa kuruhusu mkaguzi wa OSHA aingie "
  "na kushirikiana naye.",
  "Can an OSHA inspector enter a workplace without notice — is this legally permitted?",
  "Yes. OSHA inspectors in Tanzania have legal authority to enter a workplace without "
  "advance notice for safety inspection purposes. This is a statutory power under the "
  "OSHA Act to ensure genuine inspection — not a prepared inspection. The employer "
  "has an obligation to allow an OSHA inspector to enter and cooperate with them.",
  OSHA, OSHA_N, GP, "2003-01-01", ANN, "OSHA Act amendment",
  "formal", "standard"),

p("tier1a_osha_nssf_254_20260609","osha_adversarial",
  "Mfanyakazi anayeumia mahali pa kazi Tanzania analipwa fidia na OSHA moja kwa moja — je, ni sahihi?",
  "Hapana. Fidia ya mfanyakazi aliyeumia mahali pa kazi inalipwa na WCF (Workers "
  "Compensation Fund) — SI OSHA. OSHA inasimamia usalama na afya mahali pa kazi "
  "na inachunguza ajali. WCF ndiyo inayolipa fidia kwa wafanyakazi walioumia au "
  "kufiwa. OSHA na WCF ni vyombo tofauti vya serikali vinavyofanya kazi tofauti.",
  "A worker injured in the workplace in Tanzania is paid compensation directly by "
  "OSHA — is this correct?",
  "No. Compensation for a worker injured in the workplace is paid by WCF (Workers "
  "Compensation Fund) — NOT OSHA. OSHA supervises workplace safety and health and "
  "investigates accidents. WCF is what pays compensation to injured or bereaved "
  "workers. OSHA and WCF are separate government bodies doing different work.",
  OSHA, OSHA_N, GP, "2003-01-01", ANN, "OSHA Act or WCF Act amendment",
  "business_market", "disambiguation"),

p("tier1a_osha_nssf_255_20260609","osha_adversarial",
  "Biashara inayohifadhi kemikali hatari inahitaji vibali maalum Tanzania — au OSHA peke yake inatosha?",
  "Biashara inayohifadhi au kutumia kemikali hatari Tanzania inaweza kuhitaji: "
  "(1) usajili wa OSHA na kupata idhini ya mahali pa kazi (workplace approval), "
  "(2) vibali maalum vya kemikali hatari kutoka mamlaka nyingine (kama NEMC — "
  "National Environment Management Council) kulingana na aina ya kemikali, "
  "(3) vibali vya usafirishaji wa kemikali hatari. OSHA peke yake haijatoshi — "
  "uchunguze mahitaji yote ya kisheria ya kemikali yako maalum.",
  "A business storing hazardous chemicals needs special permits in Tanzania — or "
  "is OSHA registration alone sufficient?",
  "A business storing or using hazardous chemicals in Tanzania may need: (1) OSHA "
  "registration and workplace approval, (2) specific hazardous chemical permits "
  "from other authorities (such as NEMC — National Environment Management Council) "
  "depending on the type of chemical, (3) permits for transporting hazardous "
  "chemicals. OSHA alone is not sufficient — investigate all legal requirements "
  "for your specific chemicals.",
  OSHA, OSHA_N, GP, "2003-01-01", ANN, "OSHA or NEMC chemical regulation update",
  "formal", "standard"),

p("tier1a_osha_nssf_256_20260609","osha_adversarial",
  "OSHA inaweza kufunga biashara kwa sababu ya ukiukwaji wa usalama Tanzania?",
  "Ndiyo. OSHA ina mamlaka ya kutoa amri ya kusimamisha shughuli (stop order) au "
  "kufunga mahali pa kazi ikiwa panahatarisha usalama wa wafanyakazi kwa kiwango "
  "kikubwa. Mkaguzi wa OSHA anaweza kutoa: notisi ya kuboresha (improvement notice) "
  "kwa ukiukwaji mdogo, amri ya kusimamisha (prohibition notice) kwa hatari ya "
  "haraka, au kusimamisha shughuli hadi hatari itakapoondolewa. Kufunga kwa OSHA "
  "si suala la uhasibu — ni suala la usalama wa mwili.",
  "Can OSHA close a business for safety violations in Tanzania?",
  "Yes. OSHA has authority to issue a stop order or close a workplace if it poses "
  "a major threat to worker safety. An OSHA inspector can issue: an improvement "
  "notice for minor violations, a prohibition notice for immediate danger, or suspend "
  "operations until the hazard is removed. OSHA closure is not an accounting matter "
  "— it is a physical safety matter.",
  OSHA, OSHA_N, GP, "2003-01-01", ANN, "OSHA Act amendment",
  "formal", "standard"),

p("tier1a_osha_nssf_257_20260609","osha_adversarial",
  "OSHA na WCF ni chombo kimoja cha serikali Tanzania — je, ni sahihi?",
  "Hapana. OSHA na WCF ni vyombo TOFAUTI vya serikali: OSHA (Occupational Safety "
  "and Health Authority) inasimamia usalama na afya mahali pa kazi — inakagua, "
  "inadhibiti, na inasimamia. WCF (Workers Compensation Fund) ni mfuko wa bima ya "
  "ajali za kazi — inalipa fidia kwa wafanyakazi walioumia. Mwajiri analazimika "
  "kusajili NA OSHA NA WCF kwa madhumuni tofauti.",
  "OSHA and WCF are the same government body in Tanzania — is this correct?",
  "No. OSHA and WCF are SEPARATE government bodies: OSHA (Occupational Safety and "
  "Health Authority) supervises workplace safety and health — it inspects, regulates, "
  "and enforces. WCF (Workers Compensation Fund) is a workplace accident insurance "
  "fund — it pays compensation to injured workers. An employer must register with "
  "BOTH OSHA and WCF for different purposes.",
  OSHA, OSHA_N, GP, "2003-01-01", ANN, "OSHA Act or WCF Act amendment",
  "business_market", "disambiguation"),

p("tier1a_osha_nssf_258_20260609","osha_adversarial",
  "Mwajiri aliyesajili OSHA hahitaji tena kufanya tathmini ya hatari (risk assessment) — OSHA inafanya hiyo mwenyewe — je, ni sahihi?",
  "Hapana. Tathmini ya hatari (risk assessment) ni WAJIBU WA MWAJIRI — si OSHA. "
  "Mwajiri ana jukumu la kutambua hatari za mahali pa kazi, kutathmini hatari hizo, "
  "kuweka hatua za kudhibiti, na kuandika ripoti. OSHA inakagua kwamba mwajiri "
  "amefanya tathmini ya hatari ipasavyo na inatekeleza sheria ikiwa haijafanywa. "
  "Usajili wa OSHA hauondoi wajibu wa mwajiri wa tathmini ya hatari.",
  "An employer registered with OSHA doesn't need to do a risk assessment anymore "
  "— OSHA does that themselves — is this correct?",
  "No. Risk assessment is the EMPLOYER'S OBLIGATION — not OSHA's. The employer has "
  "a duty to identify workplace hazards, assess those risks, put control measures in "
  "place, and document the assessment. OSHA inspects that the employer has properly "
  "conducted a risk assessment and enforces compliance if not done. OSHA registration "
  "does not remove the employer's risk assessment obligation.",
  OSHA, OSHA_N, GP, "2003-01-01", ANN, "OSHA Act amendment",
  "formal", "adversarial"),

p("tier1a_osha_nssf_259_20260609","osha_adversarial",
  "Mwajiri wa Tanzania anahitaji kuwapa vifaa vya usalama (PPE) wafanyakazi wake — au wafanyakazi wanunue wenyewe?",
  "MWAJIRI ndiye analazimika kuwapa wafanyakazi vifaa vya usalama (PPE — Personal "
  "Protective Equipment) BURE kwa gharama za mwajiri. Hii ni wajibu wa kisheria "
  "chini ya OSHA Act. Mwajiri HAWEZI kumtaka mfanyakazi anunue vifaa vya usalama "
  "kwa pesa zake mwenyewe. Pia mwajiri lazima ahakikishe vifaa vipo katika hali "
  "nzuri na wafanyakazi wanajua kutumia PPE ipasavyo.",
  "Is a Tanzania employer required to provide safety equipment (PPE) to workers "
  "— or do workers buy their own?",
  "The EMPLOYER is required to provide workers with personal protective equipment "
  "(PPE) FREE of charge at the employer's expense. This is a legal obligation under "
  "the OSHA Act. An employer CANNOT require a worker to buy their own safety "
  "equipment. The employer must also ensure equipment is in good condition and "
  "workers know how to use PPE properly.",
  OSHA, OSHA_N, GP, "2003-01-01", ANN, "OSHA Act amendment",
  "rural_conversational", "adversarial"),

p("tier1a_osha_nssf_260_20260609","osha_adversarial",
  "NSSF Tanzania inashughulikia bima ya afya (health insurance) — NSSF italipa gharama za hospitali za mwajiriwa — je, ni sahihi?",
  "Si sahihi kabisa. NSSF (National Social Security Fund) Tanzania ni mfuko wa "
  "pensheni na manufaa ya kijamii — si bima ya afya ya kila siku. NSSF inalipa: "
  "pensheni ya uzee (miaka 60/55), manufaa ya ulemavu, manufaa ya kifo cha mapema. "
  "Kwa bima ya afya ya hospitali, Tanzania ina mfumo tofauti — NHIF (National "
  "Health Insurance Fund) au CHF (Community Health Fund). NSSF na NHIF ni "
  "mifumo tofauti ya bima ya kijamii.",
  "NSSF Tanzania covers health insurance — NSSF will pay an employee's hospital "
  "bills — is this correct?",
  "Not quite. NSSF (National Social Security Fund) Tanzania is a pension and social "
  "benefits fund — not everyday health insurance. NSSF pays: old-age pension (age "
  "60/55), disability benefits, early death benefits. For hospital health insurance, "
  "Tanzania has a separate system — NHIF (National Health Insurance Fund) or CHF "
  "(Community Health Fund). NSSF and NHIF are different social insurance systems.",
  NSSF, NSSF_N, GP, "2018-07-01", ANN, "NSSF Act or NHIF Act amendment",
  "business_market", "disambiguation"),

p("tier1a_osha_nssf_261_20260609","osha_adversarial",
  "Mwajiriwa anaweza kuchagua kutosajiliwa NSSF ikiwa anataka — ni hiari ya mfanyakazi — je, ni sahihi?",
  "Hapana. NSSF ni LAZIMA kwa wafanyakazi wote walioajiriwa Tanzania bila kujali "
  "tamaa ya mfanyakazi. Mwajiri hawezi kumruhusu mfanyakazi 'ajiepushe' na NSSF. "
  "Mfanyakazi hawezi kuomba kutosajiliwa. Mwajiri ana wajibu wa kisheria wa "
  "kusajili kila mfanyakazi na kukata mchango wa NSSF (10% ya mfanyakazi + 10% ya "
  "mwajiri). Kutosajili mfanyakazi ni ukiukwaji wa Sheria ya NSSF.",
  "An employee can choose not to register with NSSF if they want — it is the "
  "worker's choice — is this correct?",
  "No. NSSF is MANDATORY for all employed workers in Tanzania regardless of the "
  "worker's preference. An employer cannot allow a worker to 'opt out' of NSSF. "
  "A worker cannot request not to be registered. The employer has a legal obligation "
  "to register every employee and deduct NSSF contributions (10% employee + 10% "
  "employer). Not registering an employee is a violation of the NSSF Act.",
  NSSF, NSSF_N, GP, "2018-07-01", ANN, "NSSF Act amendment",
  "business_market", "adversarial"),

p("tier1a_osha_nssf_262_20260609","osha_adversarial",
  "NSSF inaweza kulipa mfanyakazi aliyefikia umri wa miaka 55 bila kujali aina ya kazi Tanzania?",
  "Miaka 55 ni umri wa kustaafu mapema kwa wafanyakazi wa sekta ya MADINI na kazi "
  "kali zinazohitajika chini ya NSSF Act. Kwa wafanyakazi wa kawaida wa sekta nyingine, "
  "umri wa kawaida wa pensheni ya NSSF ni miaka 60. Pia, ili kupata pensheni kamili "
  "ya NSSF, mfanyakazi anahitaji angalau miezi 180 (miaka 15) ya michango. "
  "Mfanyakazi wa ofisi anayeacha kazi akiwa na umri wa 55 hawezi kudai pensheni ya "
  "NSSF kiotomatiki.",
  "Can NSSF pay a worker who has reached age 55 regardless of their type of work "
  "in Tanzania?",
  "Age 55 is the early retirement age for workers in the MINING sector and hazardous "
  "occupations specified under the NSSF Act. For ordinary workers in other sectors, "
  "the normal NSSF pension age is 60. Also, to receive a full NSSF pension, a worker "
  "needs at least 180 months (15 years) of contributions. An office worker who "
  "leaves work at age 55 cannot automatically claim NSSF pension.",
  NSSF, NSSF_N, GP, "2018-07-01", ANN, "NSSF Act amendment",
  "formal", "disambiguation"),

p("tier1a_osha_nssf_263_20260609","osha_adversarial",
  "NSSF inakataa kulipa pensheni ikiwa mfanyakazi amestaafu mapema kwa hiari — je, ni kweli?",
  "Si kweli kabisa. Mfanyakazi anayestaafu mapema kwa hiari (voluntary early retirement) "
  "anaweza bado kudai manufaa ya NSSF, lakini kiasi kitategemea: miezi ya michango "
  "aliyochangia (lazima angalau 60 kwa manufaa yaliyopunguzwa), umri wake, na aina "
  "ya manufaa anayodai. Anastaafu kabla ya miaka 60 anaweza kupata manufaa "
  "yaliyopunguzwa au kulazimishwa kusubiri hadi umri wa kawaida wa pensheni. "
  "Wasiliana na NSSF moja kwa moja kwa hali yako.",
  "NSSF refuses to pay pension if a worker retired early voluntarily — is this true?",
  "Not entirely true. A worker who voluntarily takes early retirement can still claim "
  "NSSF benefits, but the amount will depend on: months of contributions paid (must "
  "be at least 60 for reduced benefits), their age, and the type of benefit claimed. "
  "Retiring before age 60 may result in reduced benefits or being required to wait "
  "until normal pension age. Contact NSSF directly for your situation.",
  NSSF, NSSF_N, GP, "2018-07-01", ANN, "NSSF Act amendment",
  "formal", "standard"),

p("tier1a_osha_nssf_264_20260609","osha_adversarial",
  "Mwajiriwa wa mkataba wa miezi 3 anahitaji kusajiliwa NSSF — mkataba mfupi unasamehewa Tanzania?",
  "Hapana. Mfanyakazi wa mkataba wa muda wowote (hata miezi 3) Tanzania anayepokea "
  "mshahara kutoka kwa mwajiri lazima asajiliwe NSSF na michango ilipwe kwa "
  "kipindi chote cha mkataba. Sheria ya NSSF HAINA msamaha wa muda wa mkataba mfupi. "
  "Mwajiri anayeajiri mfanyakazi kwa mkataba mfupi bila kusajili NSSF anakiuka sheria.",
  "A worker on a 3-month contract needs to be registered with NSSF — is a "
  "short-term contract exempt in Tanzania?",
  "No. Any worker on any contract duration (even 3 months) in Tanzania who receives "
  "wages from an employer must be registered with NSSF and contributions paid for "
  "the entire contract period. The NSSF Act has NO short-term contract exemption. "
  "An employer who hires a worker on a short contract without NSSF registration "
  "is violating the law.",
  NSSF, NSSF_N, GP, "2018-07-01", ANN, "NSSF Act amendment",
  "rural_conversational", "adversarial"),

p("tier1a_osha_nssf_265_20260609","osha_adversarial",
  "Mwajiriwa anayefanya kazi sehemu ya wakati (part-time) Tanzania hajalazimishwa na NSSF — je, ni sahihi?",
  "Sheria ya NSSF Tanzania kwa ujumla inasema wafanyakazi wanaolipwa mishahara "
  "ya mara kwa mara lazima wasajiliwe NSSF — ikiwa ni pamoja na wafanyakazi wa "
  "sehemu ya wakati. NSSF inaweza kuhusika kwa mfanyakazi wa sehemu ya wakati "
  "anayelipwa mshahara unaostahili michango. Angalia NSSF moja kwa moja kwa "
  "mwongozo mahususi wa wafanyakazi wa sehemu ya wakati.",
  "A part-time employee in Tanzania is not covered by NSSF — is this correct?",
  "The Tanzania NSSF Act generally requires all workers receiving regular wages to "
  "be registered with NSSF — including part-time workers. NSSF may cover a part-time "
  "worker receiving wages that qualify for contributions. Check with NSSF directly "
  "for specific guidance on part-time worker coverage.",
  NSSF, NSSF_N, GP, "2018-07-01", ANN, "NSSF Act amendment",
  "formal", "standard"),

p("tier1a_osha_nssf_266_20260609","osha_adversarial",
  "WCF inalipa mfanyakazi aliyeumia mahali pa kazi bila hata mwajiri kusajili WCF — je, WCF inalipa bila kujali?",
  "Hapana. Ikiwa mwajiri HAIKUSAJILI WCF, mfanyakazi aliyeumia ana changamoto za "
  "kupata fidia ya moja kwa moja kupitia WCF. Hata hivyo, sheria ya Tanzania "
  "inaweza kumuruhusu mfanyakazi kudai fidia kutoka mwajiri moja kwa moja au "
  "kupitia mahakama. Mwajiri asiyesajili WCF bado ana wajibu wa kisheria wa kulipa "
  "fidia kwa mfanyakazi aliyeumia — na adhabu za ziada kwa kutosajili.",
  "Does WCF pay an injured workplace worker even if the employer has not registered "
  "with WCF — does WCF pay regardless?",
  "No. If an employer has NOT registered with WCF, an injured worker faces challenges "
  "getting direct compensation through WCF. However, Tanzania law may still allow "
  "the worker to claim compensation directly from the employer or through court. "
  "An employer not registered with WCF still has a legal obligation to pay "
  "compensation to an injured worker — plus additional penalties for not registering.",
  WCF, WCF_N, GP, "2008-01-01", ANN, "Workers Compensation Act amendment",
  "business_market", "adversarial"),

p("tier1a_osha_nssf_267_20260609","osha_adversarial",
  "WCF inafidia tu ajali za mahali pa kazi — si magonjwa yanayotokana na kazi — je, ni sahihi?",
  "Hapana. WCF (Workers Compensation Fund) Tanzania inashughulikia ZOTE MBILI: "
  "(1) ajali za mahali pa kazi (workplace accidents) — majeraha ya haraka kama "
  "kuanguka, kuumwa na mashine, na (2) magonjwa yanayotokana na kazi (occupational "
  "diseases) — magonjwa yanayoendelea kwa muda mrefu kutokana na mazingira ya kazi "
  "kama ugonjwa wa mapafu kwa uchimbaji madini, upotezaji wa kusikia kwa kelele. "
  "Mwajiri anaweza kulipwa fidia kwa aina zote mbili.",
  "WCF only covers workplace accidents — not work-related diseases — is this correct?",
  "No. Tanzania's WCF (Workers Compensation Fund) covers BOTH: (1) workplace "
  "accidents — immediate injuries like falls, machine injuries, and (2) occupational "
  "diseases — long-term illnesses arising from work environment such as lung disease "
  "from mining, hearing loss from noise. A worker can claim compensation for both "
  "types.",
  WCF, WCF_N, GP, "2008-01-01", ANN, "Workers Compensation Act amendment",
  "business_market", "adversarial"),

p("tier1a_osha_nssf_268_20260609","osha_adversarial",
  "WCF 0.5% ya mishahara inalipwa kwa pamoja na michango ya NSSF — mwajiri analipa kila mmoja kwa nguzo tofauti — je, ni sahihi?",
  "Ndiyo, mwajiri analipa NSSF na WCF kwa njia tofauti na mifumo tofauti: NSSF "
  "inalipwa kwa NSSF moja kwa moja kupitia mfumo wa NSSF au benki iliyoidhinishwa, "
  "tarehe 10 ya kila mwezi. WCF inalipwa kwa WCF moja kwa moja kupitia mfumo wa "
  "WCF (portal.wcf.go.tz). Kila chombo cha serikali kina kumbukumbu yake na "
  "tarehe zake za malipo. Hakuna malipo ya pamoja ya NSSF+WCF kwenye dirisha moja.",
  "The WCF 0.5% of payroll is paid together with NSSF contributions — the employer "
  "pays each to a different account — is this correct?",
  "Yes, an employer pays NSSF and WCF through different channels and systems: NSSF "
  "is paid directly to NSSF through the NSSF system or an approved bank, by the "
  "10th of each month. WCF is paid directly to WCF through the WCF system "
  "(portal.wcf.go.tz). Each government body has its own records and payment dates. "
  "There is no combined NSSF+WCF payment at one window.",
  NSSF, NSSF_N, GP, "2018-07-01", ANN, "NSSF or WCF payment system update",
  "formal", "standard"),

p("tier1a_osha_nssf_269_20260609","osha_adversarial",
  "NSSF na PPSMB (PPF) — ni mifumo sawa ya pensheni Tanzania — je, mwajiri anachagua mmoja tu?",
  "NSSF na PPF (Parastatal Pension Fund, inayoitwa pia PPSMB) ni mifumo TOFAUTI "
  "ya pensheni Tanzania. NSSF inahudumia wafanyakazi wa sekta ya kibinafsi hasa. "
  "PPF inahudumia wafanyakazi wa mashirika ya umma na baadhi ya mashirika ya "
  "kibinafsi. Kwa kawaida, mwajiri hawana chaguo — mfumo unategemea aina ya "
  "mwajiri (sekta ya umma vs kibinafsi). Angalia mwongozo wa serikali kwa "
  "biashara yako maalum.",
  "NSSF and PPSMB (PPF) — are they the same pension system in Tanzania — does "
  "the employer just choose one?",
  "NSSF and PPF (Parastatal Pension Fund, also called PPSMB) are DIFFERENT pension "
  "systems in Tanzania. NSSF primarily serves private sector employees. PPF serves "
  "employees of public institutions and some private ones. Generally, an employer "
  "does not have a choice — the system depends on the type of employer (public vs "
  "private sector). Check government guidance for your specific type of business.",
  NSSF, NSSF_N, GP, "2018-07-01", ANN, "Pension sector merger or harmonisation update",
  "formal", "disambiguation"),

p("tier1a_osha_nssf_270_20260609","osha_adversarial",
  "Mwajiri anaweza kupunguza mshahara wa mfanyakazi ili kufidia mchango wa NSSF wa mwajiri — je, inaruhusiwa Tanzania?",
  "Hapana. Mchango wa mwajiri wa NSSF (asilimia 10) ni GHARAMA YA MWAJIRI — "
  "HAIWEZI kukatwa kutoka mshahara wa mfanyakazi au kupunguza mshahara wake. "
  "Mfanyakazi analipa sehemu yake (asilimia 10) ambayo inakatwa kutoka mshahara wake, "
  "lakini sehemu ya mwajiri (asilimia 10) inalipwa na MWAJIRI mwenyewe kwa gharama "
  "zake. Mwajiri anayepunguza mshahara wa mfanyakazi kulipa mchango wake wa NSSF "
  "anakiuka sheria ya kazi na NSSF.",
  "Can an employer reduce a worker's salary to compensate for the employer's NSSF "
  "contribution — is this permitted in Tanzania?",
  "No. The employer's NSSF contribution (10%) is the EMPLOYER'S COST — it cannot "
  "be deducted from the employee's salary or reduce their wage. The employee pays "
  "their share (10%) which is deducted from their salary, but the employer's share "
  "(10%) is paid by the EMPLOYER themselves from their own funds. An employer who "
  "reduces a worker's salary to pay their NSSF contribution violates labour law "
  "and NSSF law.",
  NSSF, NSSF_N, GP, "2018-07-01", ANN, "NSSF Act or ELRA amendment",
  "business_market", "adversarial"),

p("tier1a_osha_nssf_271_20260609","osha_adversarial",
  "NSSF inaweza kutoa mkopo wa dharura kwa mwanachama aliyechangia kwa miaka 3 Tanzania?",
  "NSSF Tanzania imetoa programu za mkopo kwa wanachama wake katika mfumo wake wa "
  "umiliki. Masharti yanaweza kujumuisha: kipindi cha chini cha michango (angalau "
  "miezi 36 au zaidi), kuwa bado mwanachama wa sasa, na mkopo unaotolewa kwa "
  "matumizi maalum (nyumba, elimu). Angalia NSSF moja kwa moja kwa programu za "
  "mikopo ya hali ya sasa kwani masharti yanaweza kubadilika.",
  "Can NSSF provide an emergency loan to a member who has contributed for 3 years "
  "in Tanzania?",
  "NSSF Tanzania has offered loan programmes to its members under its own ownership "
  "framework. Conditions may include: minimum contribution period (at least 36 months "
  "or more), still being a current member, and loans provided for specific uses "
  "(housing, education). Check NSSF directly for current loan programme terms as "
  "conditions can change.",
  NSSF, NSSF_N, GP, "2018-07-01", ANN, "NSSF loan programme update",
  "business_market", "standard"),

p("tier1a_osha_nssf_272_20260609","osha_adversarial",
  "Mfanyakazi anayeacha kazi kabla ya miaka 15 ya michango anapoteza NSSF yake yote Tanzania?",
  "Hapana. Mfanyakazi anayeacha kazi kabla ya miaka 15 (miezi 180) ya michango "
  "HAPOTEZI michango yake yote. Anaweza: (1) kuomba faida ya kujitolea/kujisogeza "
  "(withdrawal benefit) kwa michango aliyochangia, au (2) kuendelea kuwa mwanachama "
  "na kuchangia kwa mwajiri mwingine hadi afikia miezi 180. Manufaa atakayopata "
  "yanategemea michango halisi aliyochangia — si sifuri.",
  "A worker who leaves employment before 15 years of contributions loses all their "
  "NSSF in Tanzania?",
  "No. A worker who leaves employment before 15 years (180 months) of contributions "
  "does NOT lose all their contributions. They can: (1) apply for a withdrawal benefit "
  "for contributions paid, or (2) remain a member and contribute with a new employer "
  "until reaching 180 months. The benefits they receive depend on actual contributions "
  "paid — not zero.",
  NSSF, NSSF_N, GP, "2018-07-01", ANN, "NSSF Act amendment",
  "rural_conversational", "standard"),

p("tier1a_osha_nssf_273_20260609","osha_adversarial",
  "OSHA inahitajika kwa wafanyakazi wanaofanya kazi nyumbani (home workers) Tanzania — usajili ni lazima?",
  "Kwa wafanyakazi wanaofanya kazi nyumbani kwao, hali ya OSHA inategemea ikiwa "
  "nyumba hiyo inachukuliwa 'mahali pa kazi' (workplace) kwa maana ya kisheria. "
  "Wafanyakazi wa nyumba ambao mwajiri anawatembelea au kutoa vifaa kazi vinaweza "
  "kuathiriwa na sheria za OSHA. Kwa wafanyakazi wa kujitegemea wanaofanya kazi "
  "nyumbani kwao wenyewe, OSHA inaweza kutotumika kwa njia ile ile. Omba mwongozo "
  "wa OSHA kwa hali yako.",
  "Is OSHA registration required for home workers in Tanzania?",
  "For workers working from their own home, the OSHA position depends on whether "
  "the home is considered a 'workplace' in the legal sense. Home workers whose "
  "employer visits them or provides work equipment may be affected by OSHA law. "
  "For truly self-employed people working from their own home, OSHA may not apply "
  "in the same way. Seek OSHA guidance for your specific situation.",
  OSHA, OSHA_N, GP, "2003-01-01", ANN, "OSHA Act home working guidance update",
  "formal", "standard"),

p("tier1a_osha_nssf_274_20260609","osha_adversarial",
  "Mwajiri anapaswa kutoa mafunzo ya usalama kwa kila mfanyakazi mpya kabla ya kuanza kazi Tanzania?",
  "Ndiyo. OSHA Act Tanzania inataka mwajiri kutoa mafunzo ya usalama na afya "
  "mahali pa kazi kwa wafanyakazi — hasa wafanyakazi wapya kabla ya kuanza kazi "
  "au kufanya kazi kwenye mazingira ya hatari. Mafunzo lazima yashughulikie: "
  "hatari za mahali pa kazi husika, jinsi ya kutumia PPE, taratibu za dharura, "
  "na hatua za kudhibiti hatari. Mwajiri lazima ahifadhi rekodi za mafunzo hayo.",
  "Must an employer provide safety training to every new employee before starting "
  "work in Tanzania?",
  "Yes. The Tanzania OSHA Act requires employers to provide workplace safety and "
  "health training to workers — especially new workers before starting work or "
  "before working in hazardous environments. Training must cover: specific workplace "
  "hazards, how to use PPE, emergency procedures, and hazard control measures. "
  "The employer must keep records of that training.",
  OSHA, OSHA_N, GP, "2003-01-01", ANN, "OSHA Act amendment",
  "formal", "standard"),

p("tier1a_osha_nssf_275_20260609","osha_adversarial",
  "Mwajiriwa anayedai fidia ya WCF lazima apitie mahakama — WCF haiwezi kulipa moja kwa moja — je, ni sahihi?",
  "Hapana. WCF ina utaratibu wa kudai fidia moja kwa moja BILA mahakama kwa hali "
  "nyingi za kawaida za ajali za kazi. Mfanyakazi au mwajiri anaweza kuwasilisha "
  "madai kupitia mfumo wa WCF (portal.wcf.go.tz) au ofisi ya WCF moja kwa moja. "
  "Mahakama inahitajika tu ikiwa dawa imekataliwa na WCF na mwathiriwa anataka "
  "kupinga uamuzi huo. Kwa ajali za kawaida, WCF ina mchakato wa malipo ya moja "
  "kwa moja.",
  "A worker claiming WCF compensation must go through court — WCF cannot pay "
  "directly — is this correct?",
  "No. WCF has a direct claim procedure WITHOUT court for most ordinary workplace "
  "accident cases. A worker or employer can file claims through the WCF system "
  "(portal.wcf.go.tz) or WCF office directly. Court is only needed if a claim is "
  "rejected by WCF and the claimant wants to challenge that decision. For ordinary "
  "accidents, WCF has a direct payment process.",
  WCF, WCF_N, GP, "2008-01-01", ANN, "Workers Compensation Act amendment",
  "business_market", "standard"),

p("tier1a_osha_nssf_276_20260609","osha_adversarial",
  "Mfanyakazi aliyeumia kazini Tanzania anapata kiasi gani cha fidia kutoka WCF?",
  "Kiasi cha fidia ya WCF Tanzania kinategemea: aina ya jeraha au ulemavu, asilimia "
  "ya ulemavu iliyoamuliwa na daktari wa WCF, na mshahara wa mfanyakazi. Fidia kwa "
  "ulemavu wa kudumu wa asilimia 100 ni miaka fulani ya mshahara (kiwango "
  "kilichowekwa na Workers Compensation Act). Fidia ya kifo cha mfanyakazi inajumuisha "
  "malipo ya mkupuo na malipo ya mwenzi/watoto. Angalia WCF kwa jedwali la fidia "
  "la hali ya sasa.",
  "How much compensation does an injured Tanzanian worker receive from WCF?",
  "The amount of WCF compensation in Tanzania depends on: the type of injury or "
  "disability, the percentage of disability assessed by a WCF-appointed doctor, and "
  "the worker's wage. Compensation for 100% permanent disability is a set number of "
  "years of wages (amount prescribed by the Workers Compensation Act). Death "
  "compensation includes a lump sum payment and spouse/children payments. Check "
  "WCF for the current compensation schedule.",
  WCF, WCF_N, GP, "2008-01-01", ANN, "Workers Compensation Act amendment",
  "formal", "standard"),

p("tier1a_osha_nssf_277_20260609","osha_adversarial",
  "Mwajiri anaweza kupunguza au kuzuia fidia ya WCF ikiwa mfanyakazi mwenyewe "
  "alisababisha ajali — je, ni kweli?",
  "Inategemea hali. WCF Tanzania kwa kawaida inalipa fidia hata kama mfanyakazi "
  "alichangia katika ajali — isipokuwa ikiwa ajali ilitokana na tabia ya makusudi "
  "ya mfanyakazi au ukiukwaji mkubwa wa maagizo ya usalama. Hata hivyo, uzembe "
  "mdogo wa mfanyakazi kwa kawaida HAUKATII haki ya fidia. Sheria ya WCF inasema "
  "mfanyakazi analindwa hata kama ana makosa madogo.",
  "Can an employer reduce or block WCF compensation if the worker themselves caused "
  "the accident — is this true?",
  "It depends on the situation. Tanzania's WCF generally pays compensation even if "
  "the worker contributed to the accident — except if the accident resulted from the "
  "worker's intentional conduct or serious violation of safety instructions. However, "
  "minor worker negligence generally does NOT disqualify a compensation claim. WCF "
  "law protects the worker even if they have minor fault.",
  WCF, WCF_N, GP, "2008-01-01", ANN, "Workers Compensation Act amendment",
  "formal", "standard"),

p("tier1a_osha_nssf_278_20260609","osha_adversarial",
  "Kampuni mpya yenye wafanyakazi 15 Tanzania inahitaji kusajili OSHA na WCF wakati mmoja au hatua kwa hatua?",
  "Kampuni mpya yenye wafanyakazi 15 Tanzania inahitaji kusajili VYOMBO VYOTE "
  "haraka iwezekanavyo. Mpangilio wa vitendo: (1) BRELA + TIN (kwanza), (2) NSSF "
  "(wakati wa kuajiri wafanyakazi wa kwanza), (3) WCF (wakati wa kuajiri wafanyakazi "
  "wa kwanza — mwajiri mwenye hata mfanyakazi 1 anahitaji WCF), (4) OSHA (mara "
  "idadi ya wafanyakazi ifikia 10). Usisimame mpaka wafanyakazi 15 kusajili OSHA — "
  "usajili unatakiwa mapema unapofikia kizingiti cha 10.",
  "Does a new company with 15 employees in Tanzania need to register with OSHA "
  "and WCF at the same time or step by step?",
  "A new company with 15 employees in Tanzania needs to register with ALL bodies as "
  "quickly as possible. Practical sequence: (1) BRELA + TIN (first), (2) NSSF (when "
  "hiring the first employee), (3) WCF (when hiring the first employee — even an "
  "employer with 1 worker needs WCF), (4) OSHA (once the employee count reaches 10). "
  "Do not wait until 15 employees to register with OSHA — registration is required "
  "as soon as you hit the threshold of 10.",
  OSHA, OSHA_N, GP, "2003-01-01", ANN, "OSHA Act or WCF Act amendment",
  "business_market", "standard"),

p("tier1a_osha_nssf_279_20260609","osha_adversarial",
  "NSSF inaendelea kukusanya michango ikiwa kampuni imefungwa kwa sababu ya COVID au dharura — je, kuna msamaha?",
  "NSSF Tanzania haikutoa msamaha wa jumla wa michango wakati wa COVID-19 kwa "
  "biashara. Hata biashara zilizofungwa kwa amri ya serikali wakati wa janga, "
  "ikiwa zilikuwa bado na wafanyakazi walioendelea kulipwa mishahara, zililazimika "
  "kuendelea kuwasilisha michango ya NSSF. Biashara ambazo hazikuweza kulipa "
  "ziliweza kuwasiliana na NSSF kuhusu mpango wa malipo au hali yao. Angalia "
  "NSSF moja kwa moja kwa taarifa za hali maalum kama dharura za baadaye.",
  "Does NSSF continue collecting contributions if a company closes due to COVID "
  "or emergency — is there an exemption?",
  "NSSF Tanzania did not provide a general COVID-19 contribution waiver for "
  "businesses. Even businesses closed by government order during the pandemic, "
  "if they still had employees who continued to be paid wages, were required to "
  "continue submitting NSSF contributions. Businesses that could not pay could "
  "contact NSSF about a payment plan or their situation. Check NSSF directly "
  "for information on specific situations like future emergencies.",
  NSSF, NSSF_N, GP, "2018-07-01", ANN, "NSSF emergency policy update",
  "formal", "standard"),

p("tier1a_osha_nssf_280_20260609","osha_adversarial",
  "Mwajiri anaweza kusimamisha michango ya NSSF kwa miezi 3 bila adhabu ikiwa ana tatizo la mtiririko wa pesa Tanzania?",
  "Hapana. NSSF haiku na utaratibu rasmi wa 'kusimamisha michango' bila adhabu. "
  "Michango ya NSSF lazima iwasilishwe ifikapo tarehe 10 ya kila mwezi bila "
  "kujali matatizo ya mtiririko wa pesa. Kuchelewa kunasababisha adhabu ya "
  "asilimia 5 kwa mwezi. Mwajiri mwenye matatizo ya kweli ya fedha anaweza "
  "kuwasiliana na NSSF kuomba mpango wa malipo wa awamu — lakini hii si "
  "kusimamisha na bado riba inajilimbikiza.",
  "Can an employer suspend NSSF contributions for 3 months without penalty if "
  "they have a cash flow problem in Tanzania?",
  "No. NSSF does not have a formal 'suspend contributions' procedure without penalty. "
  "NSSF contributions must be submitted by the 10th of each month regardless of "
  "cash flow problems. Late payment attracts a 5% penalty per month. An employer "
  "with genuine financial difficulties can contact NSSF to request an instalment "
  "payment plan — but this is not a suspension and interest still accrues.",
  NSSF, NSSF_N, GP, "2018-07-01", ANN, "NSSF Act amendment",
  "business_market", "adversarial"),

p("tier1a_osha_nssf_281_20260609","osha_adversarial",
  "Mfanyakazi wa kigeni aliyeajiriwa Tanzania anahitaji kusajiliwa NSSF na WCF — je, wana haki sawa na Watanzania?",
  "Ndiyo. Mfanyakazi wa kigeni aliyeajiriwa kisheria Tanzania (mwenye kibali halisi "
  "cha kazi) ana haki sawa za kisheria za NSSF na WCF kama mfanyakazi wa Kitanzania. "
  "Mwajiri lazima asajili mfanyakazi wa kigeni NSSF na WCF na kuwasilisha michango. "
  "Uraia wa mfanyakazi hauathiri wajibu wa mwajiri wa kuhifadhi bima na manufaa "
  "ya kijamii.",
  "Is a foreign employee hired in Tanzania required to be registered with NSSF and "
  "WCF — do they have equal rights to Tanzanians?",
  "Yes. A foreign worker lawfully employed in Tanzania (with a valid work permit) has "
  "the same legal rights to NSSF and WCF as a Tanzanian employee. The employer must "
  "register the foreign worker with NSSF and WCF and remit contributions. The "
  "worker's citizenship does not affect the employer's obligation to maintain "
  "social security and insurance coverage.",
  NSSF, NSSF_N, GP, "2018-07-01", ANN, "NSSF Act or ELRA amendment",
  "formal", "standard"),

p("tier1a_osha_nssf_282_20260609","osha_adversarial",
  "Tofauti kati ya NSSF ya Tanzania na PSSSF (Public Service Social Security Fund) ni nini?",
  "NSSF (National Social Security Fund) na PSSSF (Public Service Social Security Fund) "
  "ni mifumo miwili tofauti ya hifadhi ya jamii Tanzania: NSSF inahudumia wafanyakazi "
  "wa SEKTA YA KIBINAFSI hasa. PSSSF inahudumia wafanyakazi wa SEKTA YA UMMA (watumishi "
  "wa serikali, mashirika ya umma). Viwango vya michango na manufaa yanaweza kutofautiana. "
  "Biashara ya kibinafsi haisajili PSSSF — inasajili NSSF.",
  "What is the difference between NSSF Tanzania and PSSSF (Public Service Social "
  "Security Fund)?",
  "NSSF (National Social Security Fund) and PSSSF (Public Service Social Security "
  "Fund) are two different social security systems in Tanzania: NSSF primarily "
  "serves PRIVATE SECTOR employees. PSSSF serves PUBLIC SECTOR employees (government "
  "workers, public corporations). Contribution rates and benefits may differ. A "
  "private business registers with NSSF — not PSSSF.",
  NSSF, NSSF_N, GP, "2018-07-01", ANN, "NSSF or PSSSF harmonisation update",
  "formal", "disambiguation"),

p("tier1a_osha_nssf_283_20260609","osha_adversarial",
  "Kampuni inayofanya kazi kwenye jengo la kukodi inahitaji kupata idhini ya OSHA kwa jengo hilo Tanzania?",
  "Kwa ujumla, mwajiri aliyekodi jengo ana wajibu wa kuhakikisha mazingira ya kazi "
  "yanafuata viwango vya OSHA — hata kama hajamiliki jengo. Ikiwa jengo lina hatari "
  "za kimuundo (kama umeme mbaya, paa yenye hatari, njia za dharura zilizofungwa), "
  "mwajiri anaweza kuzungumza na mmiliki wa jengo LAKINI bado ana wajibu wa kisheria "
  "wa kulinda wafanyakazi wake. OSHA inaweza kukagua mahali pa kazi bila kujali "
  "nani anamiliki jengo.",
  "Does a company working in a rented building need to get OSHA approval for "
  "that building in Tanzania?",
  "Generally, an employer who rents a building has an obligation to ensure the work "
  "environment meets OSHA standards — even if they don't own the building. If the "
  "building has structural hazards (such as faulty electrics, dangerous roof, blocked "
  "emergency exits), the employer can speak to the building owner BUT still has a "
  "legal duty to protect their workers. OSHA can inspect a workplace regardless of "
  "who owns the building.",
  OSHA, OSHA_N, GP, "2003-01-01", ANN, "OSHA Act amendment",
  "formal", "standard"),

p("tier1a_osha_nssf_284_20260609","osha_adversarial",
  "Mwajiri anayolipa mfanyakazi posho za chakula na usafiri anahitaji kujumuisha posho hizi katika msingi wa NSSF Tanzania?",
  "Msingi wa michango ya NSSF Tanzania unategemea 'mshahara wa jumla' (gross wage). "
  "Posho za chakula na usafiri zinazolipwa kwa kawaida na mara kwa mara kama sehemu "
  "ya mfuko wa mishahara ZINAWEZA kujumuishwa kwenye msingi wa NSSF kulingana na "
  "jinsi zinavyofafanuliwa. Posho za hiari au zisizo za kawaida zinaweza kuepuka "
  "NSSF. Angalia NSSF na mwanasheria wa ajira kwa hali yako mahususi ya posho "
  "za mfanyakazi.",
  "An employer paying food and transport allowances — must these be included in "
  "the NSSF base in Tanzania?",
  "The NSSF contribution base in Tanzania depends on 'gross wage'. Food and transport "
  "allowances paid regularly and consistently as part of the remuneration package "
  "MAY be included in the NSSF base depending on how they are defined. Discretionary "
  "or irregular allowances may escape NSSF. Check NSSF and an employment lawyer "
  "for your specific allowance situation.",
  NSSF, NSSF_N, GP, "2018-07-01", ANN, "NSSF Act or gross wage definition update",
  "formal", "standard"),

p("tier1a_osha_nssf_285_20260609","osha_adversarial",
  "Mfanyakazi anayehamia kazi nyingine Tanzania — NSSF yake inabaki au inaanza upya na mwajiri mpya?",
  "NSSF ya mfanyakazi HAIANZI UPYA anapobadilisha mwajiri. Nambari ya NSSF ya "
  "mfanyakazi inabaki sawa, na michango yake yote iliyochangiwa na waajiri "
  "wote wa awali inajumlishwa kwenye akaunti yake moja ya NSSF. Mfanyakazi "
  "anapaswa kumpa mwajiri mpya nambari yake ya NSSF ili mwajiri mpya aendelee "
  "kuchangia kwenye akaunti ile ile — sio kuanza akaunti mpya.",
  "A worker moving to a new job in Tanzania — does their NSSF start over or "
  "continue with the new employer?",
  "An employee's NSSF does NOT start over when they change employer. The worker's "
  "NSSF number stays the same, and all contributions paid by all previous employers "
  "are added to their single NSSF account. The worker should give their new employer "
  "their NSSF number so the new employer continues contributing to the same account "
  "— not starting a new one.",
  NSSF, NSSF_N, GP, "2018-07-01", ANN, "NSSF Act amendment",
  "rural_conversational", "standard"),

p("tier1a_osha_nssf_286_20260609","osha_adversarial",
  "OSHA inaweza kutozwa kwa mwajiri ambaye mfanyakazi wake aliumia nje ya saa za kazi Tanzania?",
  "Kwa ujumla, OSHA na WCF zinashughulikia majeraha YA MAHALI PA KAZI na wakati wa "
  "kazi. Majeraha yanayotokea nje ya saa za kazi na mahali pa kazi (kama mfanyakazi "
  "alianguka nyumbani kwake) kwa kawaida HAYASHUGHULIKIW na WCF kama jeraha la "
  "kazini. Hata hivyo, kama jeraha lilitokea wakati mfanyakazi alikuwa akifanya "
  "shughuli inayohusiana na kazi (kama safari ya biashara), WCF inaweza kutumika.",
  "Can OSHA impose liability on an employer if a worker was injured outside working "
  "hours in Tanzania?",
  "Generally, OSHA and WCF deal with injuries AT THE WORKPLACE and during working "
  "hours. Injuries occurring outside working hours and the workplace (such as a "
  "worker falling at their home) are generally NOT treated by WCF as a workplace "
  "injury. However, if the injury occurred while the worker was performing a "
  "work-related activity (such as a business trip), WCF may apply.",
  OSHA, OSHA_N, GP, "2003-01-01", ANN, "OSHA Act or WCF Act amendment",
  "formal", "standard"),

p("tier1a_osha_nssf_287_20260609","osha_adversarial",
  "Mwajiri asiye na OSHA lakini ana WCF — anafuata sheria Tanzania?",
  "Mwajiri mwenye wafanyakazi 10+ analazimika kusajili OSHA NA WCF. Kusajili WCF "
  "tu bila OSHA (kwa mwajiri anayestahili OSHA) ni uzingatiaji wa sehemu tu — "
  "si kamili. OSHA na WCF zinafanya kazi tofauti: WCF inashughulikia bima ya "
  "fidia baada ya ajali; OSHA inashughulikia kuzuia ajali na usalama wa kila siku. "
  "Kusajili WCF PEKE YAKE hakumaanishi kwamba mwajiri amefuata sheria ya OSHA.",
  "An employer with WCF but without OSHA — are they compliant in Tanzania?",
  "An employer with 10+ employees is required to register with BOTH OSHA AND WCF. "
  "Registering with WCF only without OSHA (for an employer who qualifies for OSHA) "
  "is only partial compliance — not full. OSHA and WCF do different things: WCF "
  "handles accident compensation insurance after an injury; OSHA handles accident "
  "prevention and daily safety. Having WCF ALONE does not mean an employer has "
  "complied with OSHA law.",
  OSHA, OSHA_N, GP, "2003-01-01", ANN, "OSHA Act amendment",
  "formal", "adversarial"),

p("tier1a_osha_nssf_288_20260609","osha_adversarial",
  "Mfanyakazi wa ngazi ya juu (senior manager) anahitaji kujumuishwa kwenye NSSF Tanzania?",
  "Ndiyo. Mfanyakazi wa ngazi ya juu — ikiwa ni pamoja na wasimamizi wakuu, "
  "wakurugenzi waliochukuliwa kazi rasmi, na wafanyakazi wengine wa mishahara ya "
  "juu — wanalazimishwa kusajiliwa NSSF kama wafanyakazi wengine wote. Sheria ya "
  "NSSF HAINA msamaha wa ngazi ya kazi au kiwango cha mshahara. Mfanyakazi "
  "anayepata mshahara mkubwa bado analipa michango ya NSSF bila kikomo cha juu "
  "kwa kawaida (angalia NSSF kwa kiwango cha juu ikiwa kinatumiwa).",
  "Does a senior manager need to be included in NSSF in Tanzania?",
  "Yes. A senior manager — including managing directors, formally employed directors, "
  "and other high-salary staff — is required to register with NSSF like all other "
  "employees. The NSSF Act has NO exemption for job level or salary amount. A worker "
  "earning a large salary still pays NSSF contributions without a ceiling in most "
  "cases (check NSSF for whether a ceiling applies).",
  NSSF, NSSF_N, GP, "2018-07-01", ANN, "NSSF Act amendment",
  "formal", "adversarial"),

p("tier1a_osha_nssf_289_20260609","osha_adversarial",
  "Kampuni ya kilimo Tanzania yenye wafanyakazi wa msimu 50 — inahitaji kusajili OSHA na WCF kwa wafanyakazi hao?",
  "Wafanyakazi wa msimu wanaolipwa mishahara bado wanashughulikiwa na sheria za "
  "kazi Tanzania. WCF: mwajiri mwenye wafanyakazi hata 1 (ikiwa ni pamoja na wa "
  "msimu) anahitaji WCF — bima ya ajali inashughulikia wafanyakazi wote. OSHA: "
  "ikiwa jumla ya wafanyakazi (ikiwa ni pamoja na wa msimu) inafika 10+, mwajiri "
  "analazimishwa kusajili OSHA. Kilimo kina hatari za maalum (kemikali, vifaa vya "
  "kulima) zinazofanya OSHA muhimu zaidi.",
  "A farming company in Tanzania with 50 seasonal workers — does it need to "
  "register with OSHA and WCF for those workers?",
  "Seasonal workers receiving wages are still covered by Tanzania labour law. WCF: "
  "an employer with even 1 worker (including seasonal) needs WCF — accident "
  "insurance covers all workers. OSHA: if total worker count (including seasonal) "
  "reaches 10+, the employer is required to register with OSHA. Agriculture has "
  "specific hazards (chemicals, farming equipment) that make OSHA even more important.",
  WCF, WCF_N, GP, "2008-01-01", ANN, "Workers Compensation Act or OSHA Act amendment",
  "rural_conversational", "standard"),

p("tier1a_osha_nssf_290_20260609","osha_adversarial",
  "NSSF inaweza kukatiwa mfanyakazi kwa ombi la mwajiri — mwajiri anaweza kusimamisha akaunti ya NSSF ya mfanyakazi wake — je, inaruhusiwa?",
  "Hapana kabisa. Mwajiri HAWEZI kusimamisha, kufunga, au kuathiri akaunti ya NSSF "
  "ya mfanyakazi kwa njia yoyote. Akaunti ya NSSF ni ya mfanyakazi mwenyewe — "
  "si ya mwajiri. Mwajiri tu ana wajibu wa kuwasilisha michango. Mfanyakazi "
  "peke yake ndiye anayeweza kuomba manufaa, kubadilisha taarifa za kibinafsi, "
  "au kushughulikia akaunti yake ya NSSF.",
  "Can a worker's NSSF be suspended at the employer's request — can an employer "
  "freeze a worker's NSSF account — is this permitted?",
  "Absolutely not. An employer CANNOT suspend, close, or affect a worker's NSSF "
  "account in any way. The NSSF account belongs to the worker — not the employer. "
  "The employer only has a duty to submit contributions. Only the worker themselves "
  "can apply for benefits, change personal details, or manage their NSSF account.",
  NSSF, NSSF_N, GP, "2018-07-01", ANN, "NSSF Act amendment",
  "business_market", "adversarial"),

p("tier1a_osha_nssf_291_20260609","osha_adversarial",
  "Mfanyakazi akifa kazini Tanzania — mwajiri ana wajibu gani wa kisheria zaidi ya WCF?",
  "Mbali na WCF (ambayo inalipa fidia ya kifo kwa familia), mwajiri ana wajibu "
  "wa ziada: (1) kuarifu OSHA na polisi kuhusu kifo cha kazini ndani ya muda "
  "uliopangwa, (2) kushirikiana na uchunguzi wa OSHA wa ajali iliyosababisha kifo, "
  "(3) kulipa mshahara wote uliostahiliwa hadi tarehe ya kifo, (4) kushughulikia "
  "NSSF kwa manufaa ya kifo yanayostahili familia, (5) kuhakikisha mazingira ya "
  "kazi yanaboreshwa ili kuzuia kifo kingine kama hicho.",
  "If an employee dies at work in Tanzania — what legal obligations does the "
  "employer have beyond WCF?",
  "Beyond WCF (which pays death compensation to the family), the employer has "
  "additional obligations: (1) notify OSHA and police about the workplace death "
  "within the specified time, (2) cooperate with OSHA's investigation of the fatal "
  "accident, (3) pay all wages owed up to the date of death, (4) engage with NSSF "
  "for death benefits payable to the family, (5) ensure workplace conditions are "
  "improved to prevent another similar death.",
  OSHA, OSHA_N, GP, "2003-01-01", ANN, "OSHA Act or WCF Act amendment",
  "formal", "standard"),

p("tier1a_osha_nssf_292_20260609","osha_adversarial",
  "NSSF inashughulikia mfanyakazi aliyefukuzwa kazi Tanzania — ana haki ya pensheni yake?",
  "Mfanyakazi aliyefukuzwa kazi Tanzania HAPOTEZI michango yake ya NSSF iliyochangiwa. "
  "Akaunti yake ya NSSF inabaki na pesa zilizokwisha wasilishwa. Anaweza: (1) kuendelea "
  "kuchangia kwa mwajiri mpya ikiwa ataajiriwa tena, (2) kuomba manufaa yanayostahili "
  "kulingana na michango aliyochangia ikiwa amefikia masharti. Haki ya NSSF ni "
  "tofauti kabisa na haki ya fidia ya kufukuzwa — zote mbili zinaweza kudaiwa.",
  "NSSF covers a dismissed worker in Tanzania — do they retain their pension rights?",
  "A worker dismissed in Tanzania does NOT lose NSSF contributions already paid. "
  "Their NSSF account remains with the money already submitted. They can: (1) continue "
  "contributing with a new employer if re-employed, (2) apply for eligible benefits "
  "based on contributions paid if they meet conditions. NSSF rights are completely "
  "separate from dismissal compensation rights — both can be claimed.",
  NSSF, NSSF_N, GP, "2018-07-01", ANN, "NSSF Act amendment",
  "rural_conversational", "standard"),

p("tier1a_osha_nssf_293_20260609","osha_adversarial",
  "Mwajiri analazimika kutoa choo cha kutosha na maji safi mahali pa kazi Tanzania — OSHA inasimamia hili?",
  "Ndiyo. OSHA Tanzania inasimamia vifaa vya msingi vya usafi na afya mahali pa "
  "kazi, ikiwa ni pamoja na: vyoo vya kutosha kwa idadi ya wafanyakazi, maji safi "
  "ya kunywa, nafasi ya kutosha ya kufanyia kazi, hewa safi, na taa ya kutosha. "
  "Hizi ni mahitaji ya msingi ya sheria ya OSHA — si 'ziada' zinazotegemea hiari "
  "ya mwajiri. Mkaguzi wa OSHA anaweza kutoa notisi ya kuboresha ikiwa "
  "mahitaji haya hayajakamilika.",
  "Is an employer required to provide adequate toilets and clean water at the "
  "workplace in Tanzania — does OSHA regulate this?",
  "Yes. OSHA Tanzania regulates basic sanitation and health facilities at the "
  "workplace, including: adequate toilets for the number of workers, clean drinking "
  "water, sufficient workspace, fresh air, and adequate lighting. These are basic "
  "legal requirements under OSHA law — not extras that depend on employer discretion. "
  "An OSHA inspector can issue an improvement notice if these requirements are not met.",
  OSHA, OSHA_N, GP, "2003-01-01", ANN, "OSHA Act welfare provision update",
  "rural_conversational", "standard"),

p("tier1a_osha_nssf_294_20260609","osha_adversarial",
  "Mwajiriwa wa kujitegemea (self-employed contractor) anaweza kusajili NSSF peke yake Tanzania bila mwajiri?",
  "Ndiyo. Mtu wa kujitegemea (self-employed) au mfanyabiashara ambaye si mwajiriwa "
  "wa mtu mwingine anaweza kusajili NSSF kama mwanachama anayejichangia (voluntary "
  "member). Mwanachama wa hiari analipa mchango wote mwenyewe (si kutenganishwa "
  "kati ya mwajiri na mfanyakazi). Hii inakuruhusu kupata manufaa ya NSSF ya "
  "pensheni na manufaa mengine baadaye. Angalia NSSF kwa masharti ya usajili wa "
  "hiari.",
  "Can a self-employed contractor register with NSSF on their own in Tanzania "
  "without an employer?",
  "Yes. A self-employed person or business person who is not employed by someone "
  "else can register with NSSF as a voluntary contributing member. A voluntary "
  "member pays the full contribution themselves (not split between employer and "
  "employee). This allows them to access NSSF pension and other benefits later. "
  "Check NSSF for voluntary registration conditions.",
  NSSF, NSSF_N, GP, "2018-07-01", ANN, "NSSF voluntary membership update",
  "rural_conversational", "standard"),

p("tier1a_osha_nssf_295_20260609","osha_adversarial",
  "Mwajiri anaweza kutumia michango ya NSSF iliyokatwa kutoka mshahara wa mfanyakazi kwa matumizi ya kampuni kabla ya kuwasilisha — je, hii ni haramu?",
  "Ndiyo, hii ni HARAMU kabisa. Pesa iliyokatwa kutoka mshahara wa mfanyakazi kama "
  "mchango wa NSSF ni pesa ya mfanyakazi iliyoshikiliwa na mwajiri kwa niaba ya "
  "mfanyakazi. Mwajiri HANA haki ya kutumia pesa hizi kwa madhumuni yoyote "
  "ya kampuni. Kutumia michango ya NSSF ya wafanyakazi ni wizi na ni kosa la jinai "
  "chini ya Sheria ya NSSF na sheria za kazi.",
  "Can an employer use NSSF contributions deducted from employee wages for company "
  "use before remitting — is this illegal?",
  "Yes, this is completely ILLEGAL. Money deducted from an employee's wages as NSSF "
  "contributions is the employee's money held by the employer on the employee's "
  "behalf. The employer has NO right to use this money for any company purpose. "
  "Using workers' NSSF contributions is theft and is a criminal offence under the "
  "NSSF Act and labour laws.",
  NSSF, NSSF_N, GP, "2018-07-01", ANN, "NSSF Act or criminal code amendment",
  "business_market", "adversarial"),

p("tier1a_osha_nssf_296_20260609","osha_adversarial",
  "Kama mwajiri amewasilisha NSSF kwa miaka 10 bila kukosea — ana haki ya kupata 'clean record' inayothibitishwa na NSSF?",
  "NSSF Tanzania inaweza kutoa taarifa ya uzingatiaji (compliance statement) au "
  "cheti cha ukaguzi wa malipo kinachoonyesha historia ya malipo ya mwajiri. Hati "
  "hii inaweza kuhitajika kwa: kuthibitishwa na TRA wakati wa ukaguzi, maombi "
  "ya mikopo ya benki, zabuni za serikali, au ukaguzi wa washirika wa biashara. "
  "Angalia NSSF kwa jinsi ya kupata taarifa hii rasmi.",
  "If an employer has remitted NSSF for 10 years without error — do they have a "
  "right to a 'clean record' certificate from NSSF?",
  "NSSF Tanzania can issue a compliance statement or payment audit certificate "
  "showing an employer's payment history. This document may be required for: "
  "verification by TRA during audits, bank loan applications, government tenders, "
  "or business partner due diligence. Check NSSF for how to obtain this formal "
  "statement.",
  NSSF, NSSF_N, GP, "2018-07-01", ANN, "NSSF compliance statement procedure update",
  "formal", "standard"),

p("tier1a_osha_nssf_297_20260609","osha_adversarial",
  "Mwajiri anaweza kudai msaada (subsidy) kutoka WCF ikiwa ananunua vifaa vya usalama kwa wafanyakazi Tanzania?",
  "WCF Tanzania kwa kawaida si chombo cha kutoa ruzuku ya vifaa vya usalama — "
  "hilo ni jukumu la OSHA au programu za serikali za usalama wa kazi. WCF "
  "inashughulikia malipo ya fidia ya ajali baada ya kutokea. Hata hivyo, WCF "
  "inaweza kuwa na programu za kuzuia ajali au mafunzo ya usalama kwa waajiri "
  "waliojisajili vizuri. Angalia WCF na OSHA kwa programu zozote zinazosaidia "
  "kupunguza ajali za mahali pa kazi.",
  "Can an employer claim a subsidy from WCF if they buy safety equipment for "
  "workers in Tanzania?",
  "WCF Tanzania is generally not a body that provides safety equipment subsidies "
  "— that is the domain of OSHA or government workplace safety programmes. WCF "
  "handles accident compensation payments after they occur. However, WCF may have "
  "accident prevention programmes or safety training for well-registered employers. "
  "Check WCF and OSHA for any programmes that help reduce workplace accidents.",
  WCF, WCF_N, GP, "2008-01-01", ANN, "WCF or OSHA prevention programme update",
  "formal", "standard"),

p("tier1a_osha_nssf_298_20260609","osha_adversarial",
  "Mwajiriwa anayeishi mbali na hospitali ya karibu Tanzania — WCF italipia usafirishaji wake hospitalini?",
  "WCF Tanzania inashughulikia gharama za matibabu za mfanyakazi aliyeumia mahali "
  "pa kazi — ikiwa ni pamoja na gharama za usafirishaji wa dharura kwa hospitali "
  "katika hali nyingi. Hata hivyo, kiasi na aina ya gharama zinazolipwa na WCF "
  "zinategemea Sheria ya Fidia ya Wafanyakazi na kanuni zake. Angalia WCF moja "
  "kwa moja kwa maelezo ya gharama zinazofunikwa kwa kesi yako mahususi.",
  "A worker living far from the nearest hospital in Tanzania — will WCF pay for "
  "their transport to hospital?",
  "Tanzania's WCF handles medical expenses for a worker injured at the workplace "
  "— including emergency transport to hospital costs in many cases. However, the "
  "amounts and types of expenses covered by WCF depend on the Workers Compensation "
  "Act and its regulations. Check WCF directly for details of expenses covered "
  "for your specific case.",
  WCF, WCF_N, GP, "2008-01-01", ANN, "Workers Compensation Act amendment",
  "rural_conversational", "standard"),

p("tier1a_osha_nssf_299_20260609","osha_adversarial",
  "Kampuni inahitajika kuandaa mpango wa kukabiliana na dharura (emergency response plan) Tanzania — OSHA inashughulikia hili?",
  "Ndiyo. OSHA Act Tanzania inataka mwajiri — hasa katika sekta zenye hatari kali "
  "kama viwanda, kemikali, ujenzi — kuandaa na kutekeleza mpango wa kukabiliana "
  "na dharura. Mpango huu lazima ujumuishe: taratibu za uokoaji wa haraka, nambari "
  "za dharura, mafunzo ya wafanyakazi wa kutoa huduma ya kwanza, na mazoezi ya "
  "mara kwa mara. OSHA inaweza kuuliza kuona mpango huu wakati wa ukaguzi.",
  "Is a company required to prepare an emergency response plan in Tanzania — "
  "does OSHA handle this?",
  "Yes. The Tanzania OSHA Act requires employers — especially in high-hazard sectors "
  "like industrial, chemical, and construction — to prepare and implement an emergency "
  "response plan. This plan must include: rapid evacuation procedures, emergency "
  "numbers, first aid worker training, and regular drills. OSHA can ask to see "
  "this plan during an inspection.",
  OSHA, OSHA_N, GP, "2003-01-01", ANN, "OSHA Act emergency plan update",
  "formal", "standard"),

p("tier1a_osha_nssf_300_20260609","osha_adversarial",
  "Muhtasari wa wajibu wa mwajiri wa Tanzania kwa OSHA, WCF, na NSSF — tofauti kuu ni zipi?",
  "Muhtasari wa vyombo vitatu vya kazi Tanzania: "
  "NSSF — Pensheni na hifadhi ya jamii: mwajiri anasajili wafanyakazi, anakata "
  "10% ya mfanyakazi, analipa 10% yake, anawasilisha jumla 20% ifikapo tarehe 10. "
  "WCF — Bima ya ajali za kazi: mwajiri anasajili biashara, analipa 0.5% ya "
  "mishahara ya mwaka, anapata bima ya fidia kwa wafanyakazi walioumia. "
  "OSHA — Usalama na afya mahali pa kazi: mwajiri mwenye 10+ wafanyakazi "
  "anasajili, anafanya tathmini ya hatari, anahakikisha mazingira salama, ana "
  "mkaguzi anayeweza kuja bila notisi.",
  "Summary of a Tanzania employer's obligations to OSHA, WCF, and NSSF — what "
  "are the key differences?",
  "Summary of the three Tanzania labour bodies: "
  "NSSF — Pension and social security: employer registers workers, deducts 10% "
  "from employee, pays own 10%, remits total 20% by the 10th. "
  "WCF — Workplace accident insurance: employer registers the business, pays 0.5% "
  "of annual payroll, gets compensation insurance for injured workers. "
  "OSHA — Workplace safety and health: employer with 10+ workers registers, conducts "
  "risk assessment, ensures safe conditions, subject to inspectors who can arrive "
  "without notice.",
  OSHA, OSHA_N, GP, "2003-01-01", ANN, "OSHA, WCF, or NSSF Act amendment",
  "business_market", "standard"),

]

written = 0
with open(OUT, "a", encoding="utf-8") as f:
    for pr in pairs:
        f.write(json.dumps(pr, ensure_ascii=False) + "\n")
        written += 1

total = sum(1 for _ in open(OUT, encoding="utf-8") if _.strip())
print(f"Part 6: wrote {written} pairs to {OUT}")
print(f"Total in file: {total}")
