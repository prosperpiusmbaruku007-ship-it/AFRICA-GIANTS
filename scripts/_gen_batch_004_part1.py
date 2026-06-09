#!/usr/bin/env python3
"""batch_004 part 1 — GN 605A minimum wage (50 pairs, 001-050)"""
import json, os

OUT = "datasets/tier1a/raw_sources/raw_pairs_batch_004.jsonl"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

D = "2026-06-09"
GN = "https://www.tanzlii.org/akn/tz/act/gn/2025/605a"
GN_N = "Tanzania Government Gazette — GN No. 605A (2025)"
ML = "https://www.mlywf.go.tz"
ML_N = "Ministry of Labour, Youth, Women and Special Groups"
OG = "official_gazette"
GP = "government_portal"
EVT = "event_triggered"
ANN = "annual"
TRIG = "Next wage order gazette"

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

# --- GN 605A standard (35 pairs) ---

p("tier1a_gn605a_001_20260609","gn605a_minimum_wage",
  "GN 605A ni nini na inaweza kuathiri biashara yangu vipi?",
  "GN 605A ni Agizo la Serikali linaloweka kiwango cha chini cha mshahara kwa sekta mbalimbali "
  "Tanzania. Agizo hili lilianza kutumika tarehe 1 Januari 2026. Kama mwajiri, lazima ulipe "
  "wafanyakazi wako angalau kiwango kilichowekwa kwa sekta yako — kutolipa ni kosa la kisheria.",
  "What is GN 605A and how does it affect my business?",
  "GN 605A is a Government Notice setting the minimum wage across sectors in Tanzania. It took "
  "effect on 1 January 2026. As an employer you must pay at least the floor set for your sector "
  "— failure to comply is a legal offence.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "business_market", "standard"),

p("tier1a_gn605a_002_20260609","gn605a_minimum_wage",
  "Kiwango cha chini cha mshahara cha wastani kwa sekta binafsi chini ya GN 605A ni kiasi gani?",
  "Kwa mujibu wa GN 605A, kiwango cha chini cha mshahara cha wastani kwa sekta binafsi ni "
  "Shilingi 358,322 kwa mwezi — ongezeko la asilimia 33.4 kutoka Shilingi 275,060 za agizo la awali. "
  "Kiwango hiki kilianza kutumika tarehe 1 Januari 2026.",
  "What is the average minimum wage for the private sector under GN 605A?",
  "Under GN 605A the average private sector minimum wage is TZS 358,322 per month — a 33.4% "
  "increase from TZS 275,060 under the previous order, effective 1 January 2026.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "formal", "standard"),

p("tier1a_gn605a_003_20260609","gn605a_minimum_wage",
  "Mshahara mdogo zaidi kwa mfanyakazi wa kawaida ni shilingi ngapi sasa hivi?",
  "Kwa mfanyakazi wa kawaida, mshahara wa chini ni karibu Shilingi 175,000 kwa mwezi kuanzia "
  "Januari 2026. Huyu ni mfanyakazi wa chini kabisa katika ngazi ya sekta — sekta za madini ya "
  "kimataifa zinaweza kufikia Shilingi 765,900. Angalia jedwali la GN 605A kwa sekta yako.",
  "What is the minimum wage for a general worker now?",
  "For a general worker the minimum wage floor is approximately TZS 175,000 per month from "
  "January 2026. This is the lowest tier — international mining/energy can reach TZS 765,900. "
  "Check the GN 605A schedule for your specific sector.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "rural_conversational", "standard"),

p("tier1a_gn605a_004_20260609","gn605a_minimum_wage",
  "GN 605A inashughulikia sekta ngapi na sekta ndogo ngapi?",
  "GN 605A inashughulikia sekta 16 na sekta ndogo 46. Zinajumuisha kilimo, ujenzi, biashara ya "
  "jumla na rejareja, hoteli na utalii, madini, usafiri, benki na fedha, viwanda, na nyinginezo. "
  "Kila sekta ina kiwango chake.",
  "How many sectors and sub-sectors does GN 605A cover?",
  "GN 605A covers 16 sectors and 46 sub-sectors, including agriculture, construction, wholesale "
  "and retail trade, hotels and tourism, mining, transport, banking and finance, manufacturing, "
  "and others. Each sector has its own minimum wage floor.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "formal", "standard"),

p("tier1a_gn605a_005_20260609","gn605a_minimum_wage",
  "Je, Agizo la Mshahara wa 2022 bado lina nguvu?",
  "Hapana. Agizo la Mshahara wa 2022 lilifutwa na GN 605A ambalo lilianza kutumika "
  "tarehe 1 Januari 2026. Waajiri hawapaswi tena kurejelea viwango vya 2022 — vinginevyo "
  "wanakiuka sheria na wanaweza kuadhibiwa.",
  "Is the 2022 Wage Order still valid?",
  "No. The 2022 Wage Order was revoked by GN 605A, which took effect on 1 January 2026. "
  "Employers must not use 2022 rates for payroll — doing so is a legal breach.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "business_market", "standard"),

p("tier1a_gn605a_006_20260609","gn605a_minimum_wage",
  "Mshahara wa chini kwa sekta ya madini ya kimataifa ni Shilingi ngapi?",
  "Kwa sekta ya madini na nishati ya kimataifa, mshahara wa chini chini ya GN 605A ni karibu "
  "Shilingi 765,900 kwa mwezi — hii ndiyo kiwango cha juu zaidi katika agizo lote. "
  "Kiwango hiki kilianza kutumika Januari 2026.",
  "What is the minimum wage for the international mining sector?",
  "For the international mining and energy sector the GN 605A minimum wage is approximately "
  "TZS 765,900 per month — the highest floor in the entire order, effective January 2026.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "formal", "standard"),

p("tier1a_gn605a_007_20260609","gn605a_minimum_wage",
  "Mshahara wa chini kwa sekta ya umma ni Shilingi ngapi?",
  "Kwa sekta ya umma, Rais Samia alitangaza mshahara wa chini wa Shilingi 500,000 kwa mwezi "
  "kuanzia Julai 2025. Hii ni tofauti kabisa na GN 605A ambayo inashughulikia sekta binafsi.",
  "What is the minimum wage for the public sector?",
  "For the public sector, President Samia announced a minimum wage of TZS 500,000 per month "
  "effective July 2025. This is separate from GN 605A which governs the private sector.",
  ML, ML_N, GP, "2025-07-01", EVT, TRIG, "formal", "standard"),

p("tier1a_gn605a_008_20260609","gn605a_minimum_wage",
  "Kama mwajiri, gharama zangu za ziada juu ya mshahara wa chini ni nini?",
  "Juu ya mshahara wa chini, mwajiri analipa: NSSF asilimia 10 ya mshahara, SDL asilimia 3.5 "
  "(kwa waajiri wenye wafanyakazi 10 au zaidi), na WCF asilimia 0.5. Kwa hivyo gharama halisi "
  "ni mshahara + asilimia 14 (au asilimia 10.5 kwa biashara ndogo chini ya wafanyakazi 10).",
  "As an employer, what additional costs do I pay on top of the minimum wage?",
  "On top of the minimum wage an employer pays: NSSF 10% of salary, SDL 3.5% (for employers "
  "with 10 or more staff), and WCF 0.5%. Total employer cost is salary + ~14% (or ~10.5% for "
  "small businesses under 10 staff).",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "business_market", "standard"),

p("tier1a_gn605a_009_20260609","gn605a_minimum_wage",
  "Kama nina wafanyakazi wachini ya 10, bado nailazimika kulipa mshahara wa chini?",
  "Ndiyo. GN 605A inatumika kwa waajiri wote bila kujali idadi ya wafanyakazi. Tofauti pekee ni "
  "SDL — SDL ya asilimia 3.5 inatakiwa tu kwa waajiri wenye wafanyakazi 10 au zaidi. Lakini "
  "mshahara wa chini ni lazima hata kama una mfanyakazi mmoja tu.",
  "If I have fewer than 10 employees do I still need to pay the GN 605A minimum wage?",
  "Yes. GN 605A applies to all employers regardless of staff count. The only difference is "
  "SDL — the 3.5% Skills Development Levy applies only to employers with 10 or more staff. "
  "But the minimum wage is mandatory even with just one employee.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "rural_conversational", "standard"),

p("tier1a_gn605a_010_20260609","gn605a_minimum_wage",
  "Adhabu ya kulipa chini ya mshahara wa chini wa GN 605A ni nini?",
  "Mwajiri anayolipa chini ya mshahara wa chini anaweza kukabiliwa na malimbikizo ya malipo "
  "tofauti kwa mfanyakazi, faini chini ya Sheria ya Ajira na Mahusiano ya Kazini (ELRA), na "
  "mashitaka ya jinai. Inspekta wa Kazi ana mamlaka ya kukagua na kuagiza malipo ya nyuma.",
  "What is the penalty for paying below the GN 605A minimum wage?",
  "An employer paying below the minimum wage faces back-pay liability to the employee, fines "
  "under the Employment and Labour Relations Act (ELRA), and possible criminal prosecution. "
  "A Labour Officer can inspect and order back payment.",
  ML, ML_N, GP, "2026-01-01", EVT, TRIG, "formal", "standard"),

p("tier1a_gn605a_011_20260609","gn605a_minimum_wage",
  "Je, mfanyakazi wa nyumbani (domestic worker) ana kiwango cha mshahara wa chini?",
  "Ndiyo. Wafanyakazi wa nyumbani wamejumuishwa katika GN 605A na wana kiwango cha mshahara "
  "wa chini. Hawastahili kulipwa chini ya kiwango kilichowekwa kwa ajili yao kuanzia Januari 2026. "
  "Angalia jedwali la GN 605A kwa kiwango maalum cha sekta hii.",
  "Do domestic workers have a minimum wage under GN 605A?",
  "Yes. Domestic workers are included in GN 605A and have a minimum wage floor. They must not "
  "be paid below the rate set for their category from January 2026. Check the GN 605A schedule "
  "for the specific domestic worker rate.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "business_market", "standard"),

p("tier1a_gn605a_012_20260609","gn605a_minimum_wage",
  "Mshahara wa chini unatumika kwa wafanyakazi wa muda (part-time) pia?",
  "Ndiyo. GN 605A inatumika kwa wafanyakazi wa muda. Kiwango kinahesabiwa kwa uwiano wa "
  "masaa ya kufanya kazi — kama mfanyakazi anafanya nusu ya masaa ya kawaida, analipwa "
  "angalau nusu ya mshahara wa chini wa mwezi.",
  "Does the minimum wage apply to part-time workers too?",
  "Yes. GN 605A applies to part-time workers. The rate is calculated proportionally — if a "
  "worker works half the standard hours, they must receive at least half the monthly minimum wage.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "business_market", "standard"),

p("tier1a_gn605a_013_20260609","gn605a_minimum_wage",
  "Je, ongezeko la mshahara wa GN 605A lilikuwa la asilimia ngapi kwa wastani?",
  "Kwa mujibu wa GN 605A, ongezeko la wastani kwa sekta binafsi lilikuwa asilimia 33.4 — "
  "kutoka Shilingi 275,060 hadi Shilingi 358,322 kwa mwezi. Mwaka uliopita (2022), viwango "
  "vya mshahara vilikuwa vya chini zaidi; GN 605A imeviongeza kwa kiasi kikubwa.",
  "What was the average percentage increase under GN 605A?",
  "Under GN 605A the average private sector increase was 33.4% — from TZS 275,060 to "
  "TZS 358,322 per month. The 2022 rates were significantly lower; GN 605A raised them substantially.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "formal", "standard"),

p("tier1a_gn605a_014_20260609","gn605a_minimum_wage",
  "Nani anawajibika kuhakikisha waajiri wanafuata GN 605A?",
  "Wizara ya Kazi, Vijana, Wanawake na Makundi Maalum (MLYWF) kupitia Inspekta wa Kazi "
  "ndio wenye jukumu la kuhakikisha utekelezaji wa GN 605A. Inspekta wana mamlaka ya "
  "kuingia mahali pa kazi, kukagua rekodi za mishahara, na kutoa amri za kulipa.",
  "Who is responsible for enforcing GN 605A compliance?",
  "The Ministry of Labour, Youth, Women and Special Groups (MLYWF) through Labour Inspectors "
  "is responsible for enforcing GN 605A. Inspectors have authority to enter workplaces, "
  "examine payroll records, and issue payment orders.",
  ML, ML_N, GP, "2026-01-01", EVT, TRIG, "formal", "standard"),

p("tier1a_gn605a_015_20260609","gn605a_minimum_wage",
  "Je, PAYE inatumika kwa mfanyakazi anayepata mshahara wa chini wa Shilingi 358,322?",
  "Kwa mshahara wa Shilingi 358,322 kwa mwezi, PAYE inaweza kulipwa au la kulingana na "
  "mwaka — kwa sababu kiwango cha kwanza cha PAYE cha asilimia sifuri kinaendelea hadi "
  "Shilingi 270,000. Sehemu inayozidi Shilingi 270,000 inalipwa kwa kiwango cha asilimia 8. "
  "Hesabu: (358,322 - 270,000) × 8% = Shilingi 7,066 za PAYE kwa mwezi.",
  "Does PAYE apply to an employee earning the TZS 358,322 minimum wage?",
  "At TZS 358,322 per month some PAYE is due — the zero-rate band ends at TZS 270,000. "
  "The amount above TZS 270,000 is taxed at 8%. Calculation: "
  "(358,322 - 270,000) × 8% = TZS 7,066 PAYE per month.",
  "https://www.tra.go.tz", "TRA — Tanzania Revenue Authority",
  GP, "2025-07-01", ANN, "Finance Act amendment", "business_market", "standard"),

p("tier1a_gn605a_016_20260609","gn605a_minimum_wage",
  "Mfanyakazi ana haki ya kudai mshahara wake wa nyuma ikiwa alidanganywa?",
  "Ndiyo. Mfanyakazi ambaye alipiwa chini ya mshahara wa chini ana haki ya kudai tofauti "
  "yote ya nyuma. Anaweza kufungua kesi mbele ya Kamati ya Usuluhishi wa Migogoro ya Kazi "
  "(CMA) au Mahakama ya Kazi. Muda wa madai ni miaka mitatu kutoka tarehe ya ukiukwaji.",
  "Can an employee claim back pay if underpaid below minimum wage?",
  "Yes. An employee paid below minimum wage can claim the full shortfall in back pay. "
  "They can file at the Commission for Mediation and Arbitration (CMA) or the Labour Court. "
  "The limitation period for claims is three years from the date of the breach.",
  ML, ML_N, GP, "2026-01-01", EVT, TRIG, "formal", "standard"),

p("tier1a_gn605a_017_20260609","gn605a_minimum_wage",
  "Je, mwajiri anaweza kulipa mshahara mdogo kuliko GN 605A kama mfanyakazi amekubali?",
  "Hapana. Makubaliano ya mtu mmoja mmoja hayawezi kupunguza haki ya kisheria ya mshahara "
  "wa chini. GN 605A ni kiwango cha chini kabisa — hata kama mfanyakazi 'amekubali' kulipwa "
  "kidogo, makubaliano hayo si ya kisheria na hayafai.",
  "Can an employer pay below GN 605A if the employee agrees?",
  "No. Individual agreements cannot reduce the statutory minimum wage entitlement. GN 605A "
  "is an absolute floor — even if an employee 'agrees' to less, that agreement is void and "
  "unenforceable.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "business_market", "standard"),

p("tier1a_gn605a_018_20260609","gn605a_minimum_wage",
  "Mfanyakazi wa muda wa majaribio (probationary) ana haki ya mshahara wa chini?",
  "Ndiyo. Kipindi cha majaribio hakimzuii mfanyakazi kupata mshahara wa chini. GN 605A "
  "inatumika tangu siku ya kwanza ya ajira, bila kujali kama mfanyakazi yuko katika "
  "kipindi cha majaribio au la.",
  "Does a probationary employee get the minimum wage?",
  "Yes. The probationary period does not exempt the employer from paying the minimum wage. "
  "GN 605A applies from day one of employment, regardless of whether the employee is on "
  "probation.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "rural_conversational", "standard"),

p("tier1a_gn605a_019_20260609","gn605a_minimum_wage",
  "Je, mfanyakazi wa kilimo ana kiwango tofauti cha mshahara wa chini?",
  "Ndiyo. Sekta ya kilimo ina viwango vyake maalum chini ya GN 605A ambavyo ni tofauti na "
  "viwango vya sekta nyingine. Angalia jedwali maalum la GN 605A kwa viwango vya kilimo "
  "kwa mazao tofauti — kama chai, kahawa, mkonge, na maua.",
  "Does the agriculture sector have a different minimum wage floor?",
  "Yes. The agriculture sector has its own specific rates under GN 605A which differ from "
  "other sectors. Check the GN 605A schedule for agriculture rates by crop type — tea, "
  "coffee, sisal, flowers, etc.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "rural_conversational", "standard"),

p("tier1a_gn605a_020_20260609","gn605a_minimum_wage",
  "Mzungumzo wa mshahara (CBA) unaweza kuleta mshahara wa juu kuliko GN 605A?",
  "Ndiyo. Makubaliano ya pamoja ya mishahara (CBA) yanaweza kuweka viwango vya juu zaidi "
  "kuliko GN 605A — na hivyo ni bora kwa mfanyakazi. Lakini hayawezi kuweka viwango vya "
  "chini kuliko GN 605A. GN 605A ni sakafu ya chini, si dari la juu.",
  "Can a Collective Bargaining Agreement (CBA) set wages higher than GN 605A?",
  "Yes. A CBA can set rates higher than GN 605A — which benefits the employee. But it "
  "cannot set rates below GN 605A. GN 605A is a floor, not a ceiling.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "formal", "standard"),

p("tier1a_gn605a_021_20260609","gn605a_minimum_wage",
  "Ikiwa sekta yangu haipo kwenye jedwali la GN 605A, ninatumia kiwango gani?",
  "Ikiwa sekta yako haipo moja kwa moja kwenye jedwali la GN 605A, tumia kiwango cha "
  "jumla (general) cha karibu Shilingi 175,000 kwa mwezi kama kiwango cha chini. "
  "Inashauriwa kushauriana na Wizara ya Kazi kwa ufafanuzi.",
  "If my sector is not listed in the GN 605A schedule, which rate applies?",
  "If your sector is not directly listed in the GN 605A schedule, apply the general "
  "minimum rate of approximately TZS 175,000 per month as the floor. It is advisable to "
  "consult the Ministry of Labour for clarification.",
  ML, ML_N, GP, "2026-01-01", EVT, TRIG, "business_market", "standard"),

p("tier1a_gn605a_022_20260609","gn605a_minimum_wage",
  "Je, mwajiri anaweza kulipa mshahara wa chini kwa sehemu sehemu (manunuzi badala ya fedha)?",
  "Hapana. Mshahara wa chini lazima ulipwe kwa fedha taslimu au kwa njia ya benki. "
  "Malipo kwa bidhaa, makazi, au faida nyingine yanaweza kuhesabiwa kama sehemu ya "
  "mshahara tu kama sheria inaruhusu na hayapunguzi sehemu ya fedha chini ya kiwango cha chini.",
  "Can an employer pay the minimum wage partly in kind (goods instead of cash)?",
  "No. The minimum wage must be paid in cash or via bank. Payments in goods, housing, or "
  "other benefits can only count as part of salary if the law permits it and they do not "
  "reduce the cash component below the minimum wage floor.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "rural_conversational", "standard"),

p("tier1a_gn605a_023_20260609","gn605a_minimum_wage",
  "Mfanyakazi aliyeajiriwa kupitia wakala wa ajira (labour contractor) ana haki ya GN 605A?",
  "Ndiyo. Mfanyakazi aliyeajiriwa kupitia wakala wa ajira ana haki ya mshahara wa chini wa "
  "GN 605A. Mwajiri wa mwisho (principal employer) na wakala wanaweza kubeba wajibu wa "
  "pamoja kuhakikisha mshahara huu unalipwa.",
  "Does a worker employed through a labour contractor have GN 605A rights?",
  "Yes. A worker employed through a labour contractor is entitled to the GN 605A minimum "
  "wage. The principal employer and contractor may share joint liability for ensuring payment.",
  ML, ML_N, GP, "2026-01-01", EVT, TRIG, "formal", "standard"),

p("tier1a_gn605a_024_20260609","gn605a_minimum_wage",
  "Je, GN 605A inashughulikia wafanyakazi wa kigeni wanaofanya kazi Tanzania?",
  "Ndiyo. GN 605A inatumika kwa wafanyakazi wote wanaofanya kazi Tanzania, bila kujali "
  "uraia. Mfanyakazi wa kigeni anayefanya kazi Tanzania ana haki ya kiwango cha chini "
  "kilichowekwa kwa sekta yake.",
  "Does GN 605A apply to foreign workers working in Tanzania?",
  "Yes. GN 605A applies to all workers employed in Tanzania regardless of nationality. "
  "A foreign worker employed in Tanzania is entitled to the minimum wage set for their sector.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "formal", "standard"),

p("tier1a_gn605a_025_20260609","gn605a_minimum_wage",
  "Kwa mwajiri wa hoteli na utalii, mshahara wa chini ni Shilingi ngapi?",
  "Sekta ya hoteli na utalii ina kiwango chake maalum chini ya GN 605A. Angalia jedwali la "
  "GN 605A kwa kiwango sahihi cha sekta ya hoteli na utalii — kiwango hiki ni zaidi ya "
  "kiwango cha jumla cha Shilingi 175,000 kwa mwezi.",
  "For a hotel and tourism employer, what is the minimum wage?",
  "The hotel and tourism sector has its own specific rate under GN 605A. Check the GN 605A "
  "schedule for the exact hotel and tourism sector rate — it is above the general floor of "
  "approximately TZS 175,000 per month.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "business_market", "standard"),

p("tier1a_gn605a_026_20260609","gn605a_minimum_wage",
  "Jinsi gani ya kusimamia usahihi wa mishahara katika biashara yangu?",
  "Weka rekodi sahihi za malipo kwa kila mfanyakazi: tarehe ya malipo, kiasi, na uthibitisho "
  "wa malipo. Tengeneza payslip kwa kila mfanyakazi kila mwezi. Hakikisha kiasi cha kila "
  "mfanyakazi ni angalau kiwango cha chini cha GN 605A kwa sekta yako.",
  "How do I manage minimum wage compliance in my business?",
  "Keep accurate payment records for each employee: payment date, amount, and proof of "
  "payment. Issue a payslip to every employee each month. Verify each amount is at least "
  "the GN 605A minimum for your sector.",
  ML, ML_N, GP, "2026-01-01", EVT, TRIG, "business_market", "standard"),

p("tier1a_gn605a_027_20260609","gn605a_minimum_wage",
  "Mfanyakazi wa benki ana kiwango cha juu cha mshahara wa chini kuliko wengine?",
  "Ndiyo. Sekta ya benki na fedha ina kiwango cha mshahara wa chini cha juu zaidi chini ya "
  "GN 605A ikilinganishwa na sekta nyingi. Sekta hii iko katika ngazi ya juu za jedwali la "
  "GN 605A — angalia jedwali maalum kwa kiwango sahihi.",
  "Does a bank employee have a higher minimum wage floor than others?",
  "Yes. The banking and finance sector has a higher minimum wage floor under GN 605A "
  "compared to many other sectors. This sector sits in the upper tiers of the GN 605A "
  "schedule — check the specific schedule for the exact rate.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "formal", "standard"),

p("tier1a_gn605a_028_20260609","gn605a_minimum_wage",
  "Ni lini GN 605A ilipitiwa na kutangazwa?",
  "GN 605A ilipitiwa na kutangazwa rasmi mnamo Oktoba 2025 — The Citizen iliripoti tarehe "
  "17 Oktoba 2025. Ilianza kutumika tarehe 1 Januari 2026. Agizo hili lilichukua nafasi ya "
  "agizo la 2022 ambalo lilifutwa.",
  "When was GN 605A gazetted and announced?",
  "GN 605A was gazetted and announced in October 2025 — The Citizen reported on 17 October "
  "2025. It took effect on 1 January 2026, replacing and revoking the 2022 order.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "formal", "standard"),

p("tier1a_gn605a_029_20260609","gn605a_minimum_wage",
  "Mfanyakazi wa sekta ya ulinzi (watchman/security) ana kiwango gani cha mshahara?",
  "Sekta ya ulinzi na usalama ina kiwango chake katika GN 605A. Kwa kawaida ni kiwango cha "
  "wastani — zaidi ya kiwango cha jumla lakini chini ya sekta kama madini. "
  "Angalia jedwali la GN 605A kwa kiwango sahihi cha sekta ya ulinzi.",
  "What minimum wage applies to a security watchman?",
  "The security and guarding sector has its own rate in GN 605A — typically a mid-tier rate, "
  "above the general floor but below sectors like mining. Check the GN 605A schedule for "
  "the exact security sector rate.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "rural_conversational", "standard"),

p("tier1a_gn605a_030_20260609","gn605a_minimum_wage",
  "Je, mwajiri anaweza kupunguza malipo ya ziada kama posho ya usafiri kutoka mshahara wa chini?",
  "Hapana. Mshahara wa chini wa GN 605A lazima ulipwe kamili — posho za ziada kama usafiri, "
  "chakula, au makazi hazihesabiwi kama sehemu ya mshahara wa chini isipokuwa sheria "
  "inaruhusu hilo moja kwa moja. Mwajiri hawezi kutumia posho kupunguza mshahara wa msingi.",
  "Can an employer deduct transport allowances from the minimum wage payment?",
  "No. The GN 605A minimum wage must be paid in full — additional allowances like transport, "
  "food, or housing do not count as part of the minimum wage unless the law explicitly "
  "permits it. An employer cannot use allowances to reduce the basic salary below the floor.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "business_market", "standard"),

p("tier1a_gn605a_031_20260609","gn605a_minimum_wage",
  "Serikali inaweza kutoa muda wa mpito kwa waajiri wadogo kushindwa kulipa mshahara wa GN 605A?",
  "Hapana muda maalum wa mpito uliotangazwa. GN 605A ilianza kutumika tarehe 1 Januari 2026 "
  "bila muda wa mpito kwa saizi ya biashara. Waajiri wote wanatarajiwa kufuata tarehe hiyo "
  "bila kujali ukubwa wa biashara.",
  "Has the government given small employers a transition period for GN 605A compliance?",
  "No specific transition period was announced. GN 605A took effect on 1 January 2026 "
  "without a size-based transition period. All employers were expected to comply from "
  "that date regardless of business size.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "formal", "standard"),

p("tier1a_gn605a_032_20260609","gn605a_minimum_wage",
  "Mshahara wa chini hutolewa kwa masaa au kwa mwezi?",
  "GN 605A inatoa viwango kwa mwezi. Tanzania haina kiwango cha kisheria cha mshahara kwa "
  "saa kwa msingi. Kwa wafanyakazi wa muda, kiwango cha kila saa kinahesabiwa kwa kugawanya "
  "mshahara wa mwezi na masaa ya kawaida ya kazi (mara nyingi saa 208 kwa mwezi).",
  "Is the minimum wage set per hour or per month?",
  "GN 605A sets rates per month. Tanzania has no statutory hourly minimum wage as a base. "
  "For part-time workers the hourly equivalent is calculated by dividing the monthly minimum "
  "by standard working hours (typically 208 hours per month).",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "formal", "standard"),

p("tier1a_gn605a_033_20260609","gn605a_minimum_wage",
  "Je, mfanyakazi anayeomba kazi mpya ana haki ya kuuliza mwajiri wa zamani mshahara wake wote?",
  "Ndiyo. Mfanyakazi ana haki ya kupokea malipo yake yote ya mwisho ikiwa ni pamoja na "
  "mshahara wa mwisho, malipo ya likizo iliyosalia, na posho nyingine zote zinazodaiwa. "
  "Mwajiri ana wajibu wa kulipa haya ndani ya siku 7 baada ya kumaliza ajira.",
  "When leaving a job does an employee have a right to receive all owed wages?",
  "Yes. An employee is entitled to receive all final payments including last salary, "
  "accrued leave pay, and any other owed allowances. The employer must pay these within "
  "7 days of termination of employment.",
  ML, ML_N, GP, "2026-01-01", EVT, TRIG, "rural_conversational", "standard"),

p("tier1a_gn605a_034_20260609","gn605a_minimum_wage",
  "Je, GN 605A inatumika kwa wafanyakazi wa NGO?",
  "Ndiyo. GN 605A inatumika kwa wafanyakazi wote Tanzania ikiwa ni pamoja na wale "
  "wanaofanya kazi katika mashirika yasiyokuwa ya faida (NGO). Hakuna msamaha maalum "
  "kwa NGO — waajiri wa NGO lazima pia wafuate viwango vya mshahara wa chini.",
  "Does GN 605A apply to NGO employees?",
  "Yes. GN 605A applies to all employees in Tanzania including those working in "
  "non-governmental organisations (NGOs). There is no special exemption for NGOs — "
  "NGO employers must also comply with minimum wage rates.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "formal", "standard"),

p("tier1a_gn605a_035_20260609","gn605a_minimum_wage",
  "Mfanyakazi wa viwanda (manufacturing) ana mshahara wa chini wa kiasi gani?",
  "Sekta ya viwanda na uzalishaji ina kiwango chake katika GN 605A. Kiwango hiki ni cha "
  "wastani — zaidi ya kiwango cha jumla cha Shilingi 175,000 lakini chini ya sekta za "
  "madini. Angalia jedwali la GN 605A kwa kiwango sahihi cha sekta ya viwanda.",
  "What minimum wage applies to a manufacturing worker?",
  "The manufacturing sector has its own rate in GN 605A — a mid-tier rate above the general "
  "floor of TZS 175,000 but below mining sectors. Check the GN 605A schedule for the "
  "exact manufacturing rate.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "business_market", "standard"),

# --- GN 605A adversarial (12 pairs) ---

p("tier1a_gn605a_036_20260609","gn605a_adversarial",
  "Mshahara wa chini bado ni Shilingi 275,060 kwa mwezi kwa sekta binafsi — je, hii ni kweli?",
  "Hapana, hii si kweli. Shilingi 275,060 ilikuwa kiwango cha agizo la 2022 ambalo "
  "LILIFUTWA. Kiwango kipya chini ya GN 605A ni Shilingi 358,322 kwa mwezi (wastani) "
  "kuanzia 1 Januari 2026. Kutumia viwango vya 2022 ni ukiukwaji wa kisheria.",
  "The minimum wage is still TZS 275,060 per month for the private sector — is this correct?",
  "No, this is incorrect. TZS 275,060 was the 2022 order rate which was REVOKED. The new "
  "rate under GN 605A is TZS 358,322 per month (average) effective 1 January 2026. "
  "Using 2022 rates is a legal breach.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "business_market", "adversarial"),

p("tier1a_gn605a_037_20260609","gn605a_adversarial",
  "GN 605A inashughulikia sekta 12 na sekta ndogo 30 — je, namba hizi ni sahihi?",
  "Hapana. Namba sahihi ni sekta 16 na sekta ndogo 46 — si 12 na 30. Agizo la GN 605A "
  "linashughulikia sekta 16 na sekta ndogo 46 zinazojumuisha aina mbalimbali za ajira "
  "Tanzania. Namba zozote tofauti na hizi ni kosa.",
  "GN 605A covers 12 sectors and 30 sub-sectors — are these numbers correct?",
  "No. The correct figures are 16 sectors and 46 sub-sectors — not 12 and 30. GN 605A "
  "covers 16 sectors and 46 sub-sectors spanning the range of employment in Tanzania. "
  "Any different numbers are wrong.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "formal", "adversarial"),

p("tier1a_gn605a_038_20260609","gn605a_adversarial",
  "GN 605A ilianza kutumika Julai 2025 — je, hii ni sahihi?",
  "Hapana. GN 605A ilianza kutumika tarehe 1 JANUARI 2026 — si Julai 2025. "
  "Julai 2025 ndiyo tarehe ambayo ongezeko la sekta ya umma (Shilingi 500,000) lilianza — "
  "hizi ni hatua mbili tofauti. GN 605A ni ya sekta binafsi na ilianza Januari 2026.",
  "GN 605A took effect in July 2025 — is this correct?",
  "No. GN 605A took effect on 1 JANUARY 2026 — not July 2025. July 2025 was the date the "
  "public sector raise (TZS 500,000) took effect — these are two separate actions. "
  "GN 605A governs the private sector and started January 2026.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "business_market", "adversarial"),

p("tier1a_gn605a_039_20260609","gn605a_adversarial",
  "Agizo la mshahara wa 2022 bado lina nguvu kwa biashara ndogo ndogo (SME)?",
  "Hapana. Agizo la 2022 lilifutwa kwa waajiri WOTE tarehe 1 Januari 2026 bila kujali "
  "ukubwa wa biashara. Hakuna kifungu cha msamaha kwa SME. Waajiri wote — wakubwa na "
  "wadogo — lazima wafuate GN 605A kuanzia Januari 2026.",
  "The 2022 Wage Order is still valid for small businesses (SMEs)?",
  "No. The 2022 order was revoked for ALL employers on 1 January 2026 regardless of "
  "business size. There is no SME exemption clause. All employers — large and small — "
  "must comply with GN 605A from January 2026.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "rural_conversational", "adversarial"),

p("tier1a_gn605a_040_20260609","gn605a_adversarial",
  "Ongezeko la mshahara wa GN 605A lilikuwa asilimia 20 kwa wastani — je, hii ni kweli?",
  "Hapana. Ongezeko la wastani lilikuwa asilimia 33.4 — si asilimia 20. Mshahara wa wastani "
  "uliongezeka kutoka Shilingi 275,060 hadi Shilingi 358,322. Ongezeko la asilimia 20 "
  "lingekuwa likifikia tu Shilingi 330,072 — namba hiyo si sahihi.",
  "The GN 605A wage increase was 20% on average — is this correct?",
  "No. The average increase was 33.4% — not 20%. The average minimum wage rose from "
  "TZS 275,060 to TZS 358,322. A 20% increase would have reached only TZS 330,072 — "
  "that figure is incorrect.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "formal", "adversarial"),

p("tier1a_gn605a_041_20260609","gn605a_adversarial",
  "Wafanyakazi wa nyumbani (domestic workers) hawamo kwenye GN 605A — ni kweli?",
  "Hapana, si kweli. Wafanyakazi wa nyumbani wamejumuishwa katika GN 605A na wana kiwango "
  "chao cha mshahara wa chini. Hakuna msamaha kwa wafanyakazi wa nyumbani — waajiri wa "
  "nyumbani lazima pia wafuate agizo hili.",
  "Domestic workers are not covered by GN 605A — is this correct?",
  "No, this is incorrect. Domestic workers are included in GN 605A and have their own "
  "minimum wage rate. There is no exemption for domestic workers — household employers "
  "must also comply with this order.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "rural_conversational", "adversarial"),

p("tier1a_gn605a_042_20260609","gn605a_adversarial",
  "Mshahara wa chini wa sekta ya umma ni Shilingi 400,000 kutoka Julai 2025 — je, hii ni sahihi?",
  "Hapana. Mshahara wa chini wa sekta ya umma ni Shilingi 500,000 kwa mwezi — si Shilingi "
  "400,000. Rais Samia alitangaza Shilingi 500,000 mnamo tarehe 1 Mei 2025, kuanzia Julai "
  "2025. Namba ya Shilingi 400,000 si sahihi.",
  "The public sector minimum wage is TZS 400,000 from July 2025 — is this correct?",
  "No. The public sector minimum wage is TZS 500,000 per month — not TZS 400,000. "
  "President Samia announced TZS 500,000 on 1 May 2025, effective July 2025. "
  "The figure of TZS 400,000 is incorrect.",
  ML, ML_N, GP, "2025-07-01", EVT, TRIG, "business_market", "adversarial"),

p("tier1a_gn605a_043_20260609","gn605a_adversarial",
  "Mshahara wa chini unahusu tu wafanyakazi wa kudumu — wafanyakazi wa muda mfupi hawafunikwi?",
  "Hapana, hii si kweli. GN 605A inafunika wafanyakazi wote — wa kudumu, wa muda mfupi, "
  "wa muda, na wa msimu. Kwa wafanyakazi wasio wa kudumu, kiwango kinahesabiwa kwa uwiano. "
  "Hakuna msamaha kwa aina yoyote ya mkataba wa ajira.",
  "The minimum wage only covers permanent employees — temporary workers are not covered?",
  "No, this is false. GN 605A covers all workers — permanent, short-term, fixed-term, and "
  "seasonal. For non-permanent workers the rate is calculated proportionally. There is no "
  "exemption for any type of employment contract.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "business_market", "adversarial"),

p("tier1a_gn605a_044_20260609","gn605a_adversarial",
  "Mshahara wa chini wa sekta ya madini ya kimataifa ni Shilingi 400,000 — je, namba hii ni sahihi?",
  "Hapana. Kwa sekta ya madini ya kimataifa na nishati, kiwango cha mshahara wa chini "
  "chini ya GN 605A ni karibu Shilingi 765,900 kwa mwezi — si Shilingi 400,000. "
  "Hii ndiyo kiwango cha juu zaidi katika agizo lote.",
  "The minimum wage for international mining is TZS 400,000 — is this figure correct?",
  "No. For the international mining and energy sector the GN 605A minimum wage floor is "
  "approximately TZS 765,900 per month — not TZS 400,000. This is the highest rate "
  "in the entire order.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "formal", "adversarial"),

p("tier1a_gn605a_045_20260609","gn605a_adversarial",
  "Waajiri hawana adhabu ya kweli kwa kulipa chini ya mshahara wa chini — ni kweli?",
  "Hapana, si kweli. Kulipa chini ya mshahara wa chini ni kosa la kisheria chini ya ELRA. "
  "Adhabu zinajumuisha malimbikizo ya malipo tofauti, faini ya Shilingi 300,000 hadi "
  "3,000,000, na uwezekano wa mashitaka ya jinai. Inspekta wa Kazi wana mamlaka kamili ya "
  "kutekeleza sheria hii.",
  "Employers face no real penalties for paying below the minimum wage — is this true?",
  "No, this is false. Paying below the minimum wage is a criminal offence under ELRA. "
  "Penalties include back-pay liability, fines of TZS 300,000 to 3,000,000, and possible "
  "criminal prosecution. Labour Inspectors have full authority to enforce this law.",
  ML, ML_N, GP, "2026-01-01", EVT, TRIG, "rural_conversational", "adversarial"),

p("tier1a_gn605a_046_20260609","gn605a_adversarial",
  "NGO hazihitaji kulipa mshahara wa chini kwa sababu si biashara ya faida — je, hii ni kweli?",
  "Hapana, si kweli. NGO ni waajiri kama waajiri wengine na lazima wafuate GN 605A. "
  "Hali ya faida au isiyo ya faida ya shirika haibadilishi wajibu wa kulipa mshahara wa "
  "chini. Kila mwajiri Tanzania — iwe kampuni ya faida au NGO — analazimika kulipa.",
  "NGOs don't need to pay minimum wage because they are not for-profit — is this true?",
  "No, this is false. NGOs are employers like any other and must comply with GN 605A. "
  "The profit or non-profit status of an organisation does not change the obligation to "
  "pay minimum wage. Every employer in Tanzania — profit or NGO — must comply.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "formal", "adversarial"),

p("tier1a_gn605a_047_20260609","gn605a_adversarial",
  "Mwajiri anaweza kulipa mshahara wa chini mdogo kama mfanyakazi amekubali maandikoni?",
  "Hapana. Makubaliano ya maandishi hayawezi kupunguza haki ya kisheria ya mshahara wa "
  "chini. GN 605A ni sheria ya lazima — hata kama mfanyakazi ametia sahihi makubaliano ya "
  "kulipwa kidogo, makubaliano hayo si ya kisheria. Mwajiri bado ana wajibu wa kisheria.",
  "Can an employer pay below minimum wage if the employee agreed in writing?",
  "No. A written agreement cannot waive the statutory minimum wage entitlement. GN 605A "
  "is mandatory law — even if an employee has signed an agreement to receive less, that "
  "agreement is void. The employer still has a legal obligation.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "business_market", "adversarial"),

# --- GN 605A disambiguation (3 pairs) ---

p("tier1a_gn605a_048_20260609","gn605a_disambiguation",
  "Tofauti kati ya mshahara wa chini (minimum wage) na mshahara wa maisha (living wage) ni nini?",
  "Mshahara wa chini (GN 605A) ni kiwango cha kisheria cha chini kabisa ambacho mwajiri "
  "analazimika kulipa — ni wajibu wa kisheria. Mshahara wa maisha ni kiasi kinachodhaniwa "
  "kinahitajika kwa mtu kuishi kwa heshima — si lazima kisheria lakini ni lengo la kibinadamu. "
  "GN 605A inaweka mshahara wa chini; mshahara wa maisha Tanzania unakadiriwa kuwa wa juu zaidi.",
  "What is the difference between minimum wage and living wage?",
  "The minimum wage (GN 605A) is the legally mandated floor an employer must pay — it is "
  "a legal obligation. A living wage is the amount estimated to cover dignified living — "
  "not legally required but a human wellbeing target. GN 605A sets the minimum; Tanzania's "
  "estimated living wage is higher.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "formal", "disambiguation"),

p("tier1a_gn605a_049_20260609","gn605a_disambiguation",
  "GN 605A na CBA (makubaliano ya pamoja ya mishahara) vinaendanaje?",
  "GN 605A inaweka kiwango cha chini cha lazima cha kisheria. CBA inaweza kuweka viwango "
  "vya juu kuliko GN 605A — na hivyo inatumika kwa wafanyakazi wanaofunikwa na CBA hiyo. "
  "CBA haiwezi kuweka viwango vya chini kuliko GN 605A — hilo haliruhusiwi kisheria. "
  "GN 605A ni sakafu; CBA inaweza kuwa dari la juu.",
  "How do GN 605A and a Collective Bargaining Agreement (CBA) interact?",
  "GN 605A sets the mandatory legal floor. A CBA can set rates higher than GN 605A — "
  "and those higher rates apply to workers covered by that CBA. A CBA cannot set rates "
  "below GN 605A — that is legally prohibited. GN 605A is the floor; a CBA can be "
  "a higher ceiling.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "formal", "disambiguation"),

p("tier1a_gn605a_050_20260609","gn605a_disambiguation",
  "GN 605A kwa sekta binafsi na ongezeko la sekta ya umma la Shilingi 500,000 ni tofauti gani?",
  "Ni hatua mbili tofauti: GN 605A inashughulikia sekta BINAFSI (sekta 16, sekta ndogo 46) "
  "kuanzia Januari 2026, na kiwango cha wastani cha Shilingi 358,322. Ongezeko la Shilingi "
  "500,000 ni la sekta ya UMMA tu, lililotangazwa na Rais Samia kuanzia Julai 2025. Waajiri "
  "wa sekta binafsi wanafuata GN 605A; serikali inafuata tangazo la Rais.",
  "What is the difference between GN 605A for the private sector and the TZS 500,000 "
  "public sector raise?",
  "These are two separate actions: GN 605A covers the PRIVATE sector (16 sectors, 46 "
  "sub-sectors) from January 2026 with an average floor of TZS 358,322. The TZS 500,000 "
  "raise applies to the PUBLIC sector only, announced by President Samia from July 2025. "
  "Private employers follow GN 605A; government follows the Presidential announcement.",
  GN, GN_N, OG, "2026-01-01", EVT, TRIG, "business_market", "disambiguation"),

]

# Write to output file (append mode so later parts can add to same file)
written = 0
with open(OUT, "a", encoding="utf-8") as f:
    for pr in pairs:
        f.write(json.dumps(pr, ensure_ascii=False) + "\n")
        written += 1

print(f"Part 1: wrote {written} pairs to {OUT}")
print(f"Total in file: {sum(1 for _ in open(OUT, encoding='utf-8') if _.strip())}")
