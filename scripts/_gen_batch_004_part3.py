#!/usr/bin/env python3
"""batch_004 part 3 — PAYE adversarial (40 more) + WHT deep (first 10) = 50 pairs"""
import json, os

OUT = "datasets/tier1a/raw_sources/raw_pairs_batch_004.jsonl"
D = "2026-06-09"
TRA = "https://www.tra.go.tz"
TRA_N = "TRA — Tanzania Revenue Authority"
TANZLII = "https://www.tanzlii.org"
TANZLII_N = "TanzLII — Tanzania Legal Information Institute"
GP = "government_portal"
OG = "official_gazette"
EVT = "event_triggered"
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
# PAYE ADVERSARIAL — pairs 011–050 (40 pairs)
# =====================================================================

p("tier1a_paye_adv_011_20260609","paye_adversarial",
  "Provisional tax inalipwa kwa awamu 3 kwa mwaka — je, hii ni sahihi?",
  "Hapana. Kodi ya awali (provisional tax) inalipwa kwa awamu 4 kwa mwaka — si 3. "
  "Awamu zinapaswa kulipwa: tarehe 31 Machi, 30 Juni, 30 Septemba, na 31 Desemba. "
  "Kampuni inayolipa kwa awamu 3 itakuwa na makosa ya malipo na inaweza kuadhibiwa.",
  "Provisional tax is paid in 3 instalments per year — is this correct?",
  "No. Provisional tax (advance income tax) is paid in 4 instalments per year — not 3. "
  "Instalments are due: 31 March, 30 June, 30 September, and 31 December. A company "
  "paying in only 3 instalments will have an underpayment error and may be penalised.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act amendment to provisional tax",
  "formal", "adversarial"),

p("tier1a_paye_adv_012_20260609","paye_adversarial",
  "Malipo ya bonasi hazikodiwi PAYE kwa sababu si mshahara wa msingi — je, ni kweli?",
  "Hapana. Bonasi ni mapato yanayotoka kwa ajira na YANAWEZA KUPIGWA KODI ya PAYE. "
  "Bonasi inaongezwa kwenye mshahara wa mwezi wa mfanyakazi na jumla yake inakabiliwa "
  "na kanda za PAYE. Waajiri wanapaswa kuhesabu PAYE kwenye bonasi kwa wakati wa kulipa.",
  "Bonus payments are not subject to PAYE because they are not basic salary — is this true?",
  "No. Bonuses are employment income and ARE subject to PAYE. A bonus is added to the "
  "employee's monthly salary and the total is subject to PAYE bands. Employers must "
  "calculate PAYE on the bonus at the time of payment.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "business_market", "adversarial"),

p("tier1a_paye_adv_013_20260609","paye_adversarial",
  "Posho ya makazi (housing allowance) haizingatiwi kama mapato ya PAYE — je, hii ni sahihi?",
  "Hapana. Posho ya makazi kwa ujumla inajumuishwa kama mapato yanayotoza PAYE. Isipokuwa "
  "kama nyumba inatolewa moja kwa moja na mwajiri (sio posho ya pesa), kuna ufupisho "
  "maalum. Lakini posho ya makazi inayolipwa kwa pesa nyingi moja kwa moja kwa mfanyakazi "
  "inatoza PAYE kwa kawaida.",
  "Housing allowance is not considered PAYE taxable income — is this correct?",
  "No. Housing allowance is generally included as PAYE-taxable income. Unless housing is "
  "provided directly by the employer (not as a cash allowance), specific provisions apply. "
  "But a housing allowance paid as cash directly to the employee is normally subject to PAYE.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "business_market", "adversarial"),

p("tier1a_paye_adv_014_20260609","paye_adversarial",
  "Mwajiri hanahitaji kulipa PAYE kwa mfanyakazi wa muda mfupi au wa msimu — je, hii ni kweli?",
  "Hapana. Mwajiri analazimika kukata na kulipa PAYE kwa WAFANYAKAZI WOTE wanaopata "
  "mapato ya ajira, ikiwa ni pamoja na wafanyakazi wa muda mfupi, wa msimu, na wa saa. "
  "Hali ya muda wa mkataba haibadilishi wajibu wa PAYE — inatumika kuanzia siku ya kwanza.",
  "An employer does not need to pay PAYE for temporary or seasonal workers — is this true?",
  "No. An employer must deduct and remit PAYE for ALL employees receiving employment "
  "income, including short-term, seasonal, and hourly workers. The duration of the "
  "contract does not change the PAYE obligation — it applies from day one.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA PAYE guidance",
  "rural_conversational", "adversarial"),

p("tier1a_paye_adv_015_20260609","paye_adversarial",
  "PAYE inalipwa na mfanyakazi mwenyewe kwa TRA moja kwa moja — mwajiri hana wajibu wa kukata?",
  "Hapana. PAYE ni mfumo wa PAYE-AS-YOU-EARN ambapo MWAJIRI ndiye anayelazimika "
  "KUKATA PAYE kutoka mshahara wa mfanyakazi na kuipeleka TRA. Mfanyakazi hajalazimishwa "
  "kulipa moja kwa moja kwa TRA isipokuwa katika hali maalum (kama ana mapato ya ziada). "
  "Wajibu mkubwa ni wa mwajiri.",
  "PAYE is paid directly to TRA by the employee themselves — the employer has no deduction obligation?",
  "No. PAYE is a Pay-As-You-Earn system where the EMPLOYER is required to DEDUCT PAYE "
  "from the employee's salary and remit it to TRA. The employee is not required to pay "
  "directly to TRA unless in special circumstances (such as having additional income). "
  "The primary obligation rests with the employer.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA PAYE guidance",
  "business_market", "adversarial"),

p("tier1a_paye_adv_016_20260609","paye_adversarial",
  "Kanda ya PAYE ya asilimia 20 inaanza kwa mshahara wa Shilingi 500,001 kwa mwezi — je, hii ni sahihi?",
  "Hapana. Kanda ya asilimia 20 inaanza kwa mshahara wa Shilingi 520,001 kwa mwezi — "
  "si Shilingi 500,001. Kanda kamili ni: 0% (hadi 270,000), 8% (270,001–520,000), "
  "20% (520,001–760,000), 25% (760,001–1,000,000), 30% (zaidi ya 1,000,000). "
  "Namba ya Shilingi 500,001 si sahihi.",
  "The 20% PAYE band starts at TZS 500,001 per month — is this correct?",
  "No. The 20% band starts at TZS 520,001 per month — not TZS 500,001. The full bands "
  "are: 0% (up to 270,000), 8% (270,001–520,000), 20% (520,001–760,000), "
  "25% (760,001–1,000,000), 30% (above 1,000,000). The figure of TZS 500,001 is incorrect.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act PAYE band change",
  "formal", "adversarial"),

p("tier1a_paye_adv_017_20260609","paye_adversarial",
  "Kanda ya juu kabisa ya PAYE ni asilimia 35 — je, hii ni sahihi?",
  "Hapana. Kanda ya juu kabisa ya PAYE Tanzania ni asilimia 30 — si asilimia 35. "
  "Kiwango cha asilimia 30 kinatumika kwa mapato yanayozidi Shilingi 1,000,000 kwa mwezi. "
  "Kiwango cha asilimia 35 hakipo katika muundo wa PAYE wa Tanzania.",
  "The top PAYE band is 35% — is this correct?",
  "No. The top PAYE band in Tanzania is 30% — not 35%. The 30% rate applies to income "
  "above TZS 1,000,000 per month. A 35% rate does not exist in Tanzania's PAYE structure.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act PAYE band change",
  "business_market", "adversarial"),

p("tier1a_paye_adv_018_20260609","paye_adversarial",
  "Mwajiri analipa PAYE ifikapo tarehe 20 ya kila mwezi unaofuata — je, hii ni sahihi?",
  "Hapana. PAYE inalipwa ifikapo tarehe 7 ya kila mwezi unaofuata — si tarehe 20. "
  "Tarehe 20 ni kwa VATreturn (si PAYE). Mwajiri analazimika kulipa PAYE ya mwezi "
  "uliopita ifikapo tarehe 7 ya mwezi unaofuata. Kuchelewa kunaleta adhabu ya asilimia 2.5.",
  "An employer pays PAYE by the 20th of each following month — is this correct?",
  "No. PAYE is remitted by the 7th of each following month — not the 20th. The 20th "
  "is the VAT return deadline (not PAYE). An employer must remit last month's PAYE "
  "by the 7th of the following month. Late payment attracts a 2.5% penalty.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA filing deadline change",
  "business_market", "adversarial"),

p("tier1a_paye_adv_019_20260609","paye_adversarial",
  "Msaada wa kibinafsi (personal relief) wa PAYE ni Shilingi 400,000 kwa mwaka — je, hii ni sahihi?",
  "Hapana. Msaada wa kibinafsi wa PAYE kwa mkazi wa Tanzania ni Shilingi 270,000 kwa mwaka "
  "— si Shilingi 400,000. Hii inamaanisha mwaka wa mapato ya kwanza kabla ya kutolipwa PAYE "
  "ni Shilingi 3,240,000 kwa mwaka (Shilingi 270,000 × 12). Kiwango cha Shilingi 400,000 "
  "si sahihi.",
  "The personal PAYE relief is TZS 400,000 per year — is this correct?",
  "No. The personal PAYE relief for a Tanzania resident is TZS 270,000 per year — "
  "not TZS 400,000. This means the first TZS 3,240,000 annual income (TZS 270,000 × 12) "
  "is tax-free. The figure of TZS 400,000 is incorrect.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act personal relief change",
  "formal", "adversarial"),

p("tier1a_paye_adv_020_20260609","paye_adversarial",
  "Watumishi wa serikali hawajumuishwi na PAYE — wanalipwa mshahara kamili bila makato — je, ni kweli?",
  "Hapana. Watumishi wa serikali wanajumuishwa na PAYE kama wafanyakazi wengine. "
  "PAYE inakatwa kutoka mshahara wa watumishi wa serikali na kuwasilishwa TRA kwa njia "
  "ya Hazina kwa kawaida. Hakuna msamaha wa PAYE kwa ajira ya serikali.",
  "Government employees are exempt from PAYE — they receive their full salary without deductions?",
  "No. Government employees are subject to PAYE like other employees. PAYE is deducted "
  "from government employees' salaries and remitted to TRA through Treasury. There is "
  "no PAYE exemption for government employment.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA PAYE guidance",
  "formal", "adversarial"),

p("tier1a_paye_adv_021_20260609","paye_adversarial",
  "PAYE haihusiani na SDL — zinalipwa kwa njia tofauti kabisa na hazihusiani — je, ni kweli?",
  "Si kweli kabisa. PAYE na SDL zote mbili zinatolewa na mwajiri na zinajumuishwa katika "
  "mahesabu ya mishahara (payroll). Ingawa ni ushuru tofauti — PAYE inalipwa TRA, SDL "
  "inalipwa TRA pia — zinafanywa pamoja kwenye mzunguko wa mishahara. Mwajiri hulipa "
  "PAYE kwa niaba ya wafanyakazi na SDL kwa niaba yake mwenyewe.",
  "PAYE and SDL are completely separate and have no relation — is this true?",
  "Not entirely. Both PAYE and SDL are employer-managed and included in payroll calculations. "
  "Though they are different levies — PAYE paid to TRA, SDL also paid to TRA — they are "
  "handled together in the payroll cycle. The employer remits PAYE on behalf of employees "
  "and SDL on their own behalf.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA payroll guidance",
  "business_market", "disambiguation"),

p("tier1a_paye_adv_022_20260609","paye_adversarial",
  "Jinsi ya kuhesabu PAYE ya mfanyakazi mwenye mshahara wa Shilingi 600,000 kwa mwezi?",
  "Kwa mshahara wa Shilingi 600,000: "
  "Kanda ya 0%: Shilingi 270,000 → kodi sifuri. "
  "Kanda ya 8%: Shilingi 270,001–520,000 = Shilingi 250,000 × 8% = Shilingi 20,000. "
  "Kanda ya 20%: Shilingi 520,001–600,000 = Shilingi 80,000 × 20% = Shilingi 16,000. "
  "Jumla ya PAYE = Shilingi 36,000 kwa mwezi.",
  "How to calculate PAYE for an employee earning TZS 600,000 per month?",
  "For a salary of TZS 600,000: "
  "0% band: TZS 270,000 → zero tax. "
  "8% band: TZS 270,001–520,000 = TZS 250,000 × 8% = TZS 20,000. "
  "20% band: TZS 520,001–600,000 = TZS 80,000 × 20% = TZS 16,000. "
  "Total PAYE = TZS 36,000 per month.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act PAYE band change",
  "business_market", "standard"),

p("tier1a_paye_adv_023_20260609","paye_adversarial",
  "Saa za ziada (overtime) hazipigwi kodi ya PAYE — je, hii ni sahihi?",
  "Hapana. Malipo ya saa za ziada ni mapato ya ajira na YANAPIGWA KODI ya PAYE. "
  "Malipo ya overtime yanaongezwa kwenye mshahara wa mwezi na jumla nzima inakabiliwa "
  "na kanda za PAYE. Hakuna msamaha maalum wa PAYE kwa overtime.",
  "Overtime payments are not subject to PAYE — is this correct?",
  "No. Overtime payments are employment income and ARE subject to PAYE. Overtime pay "
  "is added to the monthly salary and the total is subject to PAYE bands. There is no "
  "special PAYE exemption for overtime.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "rural_conversational", "adversarial"),

p("tier1a_paye_adv_024_20260609","paye_adversarial",
  "Ruzuku ya mafunzo (training allowance) haipigwi kodi ya PAYE kamwe — je, hii ni sahihi?",
  "Si kweli kwa ujumla. Ruzuku ya mafunzo inayolipwa moja kwa moja kwa mfanyakazi kama "
  "pesa inaweza kutoza PAYE ikiwa ni mapato ya ajira yanayopita kizingiti. Ruzuku ya "
  "mafunzo inayolipwa moja kwa moja kwa taasisi ya mafunzo (si kwa mfanyakazi) kwa "
  "kawaida haijumuishwi. Mazingira yanategemea jinsi ruzuku inavyolipwa.",
  "Training allowances are never subject to PAYE — is this correct?",
  "Not as a general rule. A training allowance paid directly to the employee as cash can "
  "be subject to PAYE if it constitutes taxable employment income. Training fees paid "
  "directly to a training institution (not to the employee) are generally excluded. "
  "The treatment depends on how the allowance is structured.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "formal", "adversarial"),

p("tier1a_paye_adv_025_20260609","paye_adversarial",
  "Mwajiri anaweza kutolipa PAYE kwa mwezi mmoja ikiwa biashara inapoteza pesa — je, hii ni kweli?",
  "Hapana. Wajibu wa kulipa PAYE hauhusiani na hali ya faida au hasara ya biashara. "
  "Hata ikiwa biashara inapoteza pesa, mwajiri bado analazimika kukata na kulipa PAYE "
  "ya wafanyakazi ifikapo tarehe 7. Kutolipa ni ukiukwaji wa kisheria unaopelekea adhabu "
  "ya asilimia 2.5 kwa mwezi.",
  "An employer can skip PAYE payment for one month if the business is losing money — is this true?",
  "No. The obligation to pay PAYE is not linked to the business's profit or loss. Even if "
  "the business is losing money, the employer must still deduct and remit PAYE by the 7th. "
  "Non-payment is a legal violation attracting a 2.5% monthly penalty.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA PAYE guidance",
  "business_market", "adversarial"),

p("tier1a_paye_adv_026_20260609","paye_adversarial",
  "Malipo ya fidia ya kuachishwa kazi (severance pay) hayapigwi kodi — je, ni kweli?",
  "Si kweli kabisa. Sehemu ya malipo ya fidia ya kuachishwa kazi inaweza kuwa exempt "
  "kutoka kodi. Hata hivyo, sehemu inayozidi kiwango cha kisheria kinachoruhusiwa "
  "inaweza kutoza kodi. Waajiri wanapaswa kushauriana na TRA au mshauri wa kodi kwa "
  "maelezo ya kina ya mwaka husika.",
  "Severance pay on termination is entirely tax-free — is this true?",
  "Not entirely. Part of severance pay on termination may be exempt from tax. However, "
  "the amount exceeding the permitted statutory threshold may be taxable. Employers "
  "should consult TRA or a tax adviser for the specific treatment in the relevant year.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "formal", "adversarial"),

p("tier1a_paye_adv_027_20260609","paye_adversarial",
  "Mkurugenzi wa kampuni anayepokea posho tu (bila mshahara) hahitajiki kulipa PAYE — je, ni kweli?",
  "Hapana. Mkurugenzi anayepokea malipo ya aina yoyote yanayotoka kwa kampuni — iwe "
  "mshahara, posho, au malipo ya njia nyingine — anaweza kuwa na wajibu wa PAYE. "
  "Sura ya malipo si kinachohusika — kilichohusika ni kama malipo ni mapato ya ajira. "
  "Mkurugenzi mkazi anapaswa kushauriana na mshauri wa kodi.",
  "A company director receiving only allowances (no salary) has no PAYE obligation — is this true?",
  "No. A director receiving any payment from the company — whether salary, allowances, "
  "or other forms — may have PAYE liability. The form of the payment is not what matters "
  "— what matters is whether the payment is employment income. A resident director should "
  "consult a tax adviser.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA PAYE guidance",
  "formal", "adversarial"),

p("tier1a_paye_adv_028_20260609","paye_adversarial",
  "P9 inawasilishwa kwa TRA kupitia ujumbe wa simu (SMS) — je, hii ni sahihi?",
  "Hapana. P9 (taarifa ya mwaka ya PAYE) inawasilishwa kupitia mfumo wa kielektroniki "
  "wa TRA (TRA Online/e-filing system) au ofisi ya TRA. Ujumbe wa simu peke yake "
  "haukubaliki kwa uwasilishaji rasmi wa P9. Wasilisha kupitia njia sahihi za TRA.",
  "P9 is submitted to TRA via SMS — is this correct?",
  "No. P9 (annual PAYE return) is submitted through TRA's electronic system (TRA "
  "Online/e-filing) or at a TRA office. SMS alone is not accepted for formal P9 "
  "submission. Use TRA's approved submission channels.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA e-filing system update",
  "rural_conversational", "adversarial"),

p("tier1a_paye_adv_029_20260609","paye_adversarial",
  "Mfanyakazi anayefanya kazi kwa wakati huu huu kwa waajiri wawili analipa PAYE mara moja tu — je, ni kweli?",
  "Hapana. Mfanyakazi anayefanya kazi kwa waajiri wawili kwa wakati mmoja — yaani ana "
  "ajira mbili — ana wajibu wa kuhakikisha PAYE yote inalipwa kwa mshahara wake wote. "
  "Kila mwajiri anakata PAYE kwa mshahara wake. Mfanyakazi anaweza kuwa na deni la PAYE "
  "ziada ikiwa kanda za PAYE hazikusomwa pamoja. Ni bora kukubaliana na mwajiri mmoja "
  "kuhusu mapato yote.",
  "An employee working for two employers simultaneously pays PAYE only once — is this true?",
  "No. An employee with two simultaneous employers has an obligation to ensure all PAYE "
  "is paid on total income. Each employer deducts PAYE on their portion. There may be "
  "additional PAYE due if bands were not applied cumulatively. It is best to arrange "
  "with one employer to aggregate all income for PAYE purposes.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA PAYE guidance",
  "formal", "adversarial"),

p("tier1a_paye_adv_030_20260609","paye_adversarial",
  "PAYE hairuhusiwi kukatwa kwa wafanyakazi wanaopata mshahara wa chini chini ya Shilingi 500,000 — je, ni kweli?",
  "Hapana. PAYE inakatwa MARA TU mapato yanayopita Shilingi 270,000 kwa mwezi — "
  "si Shilingi 500,000. Mfanyakazi mwenye mshahara wa Shilingi 358,322 (kiwango cha "
  "wastani cha GN 605A) tayari ana PAYE inayodaiwa: "
  "(358,322 - 270,000) × 8% = Shilingi 7,066. Kiwango cha Shilingi 500,000 si sahihi.",
  "PAYE cannot be deducted from employees earning below TZS 500,000 — is this true?",
  "No. PAYE becomes deductible AS SOON AS income exceeds TZS 270,000 per month — "
  "not TZS 500,000. An employee earning TZS 358,322 (the GN 605A average minimum) "
  "already has PAYE due: (358,322 - 270,000) × 8% = TZS 7,066. "
  "The threshold of TZS 500,000 is incorrect.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act PAYE band change",
  "rural_conversational", "adversarial"),

p("tier1a_paye_adv_031_20260609","paye_standard",
  "Mwajiri ana wajibu gani wa kutoa payslip kwa mfanyakazi?",
  "Mwajiri analazimika kutoa payslip (kadi ya mshahara) kwa kila mfanyakazi kila mwezi. "
  "Payslip inapaswa kuonyesha: mshahara wa msingi, posho zote, makato ya PAYE, makato "
  "ya NSSF, makato mengine, na mshahara halisi wa kulipwa. Kutotoa payslip ni ukiukwaji "
  "wa Sheria ya Ajira na Mahusiano ya Kazini (ELRA).",
  "What is an employer's obligation to provide a payslip to an employee?",
  "An employer must issue a payslip to every employee every month. The payslip must "
  "show: basic salary, all allowances, PAYE deducted, NSSF deducted, other deductions, "
  "and net salary paid. Failure to provide a payslip is a violation of the Employment "
  "and Labour Relations Act (ELRA).",
  TRA, TRA_N, GP, "2025-07-01", ANN, "ELRA or TRA payroll guidance",
  "business_market", "standard"),

p("tier1a_paye_adv_032_20260609","paye_standard",
  "Mwajiri anawasilisha fomu ya P10 tarehe ngapi kila mwezi?",
  "Fomu ya P10 (malipo ya kila mwezi ya PAYE) inawasilishwa ifikapo tarehe 7 ya "
  "kila mwezi unaofuata kipindi cha malipo. Kwa mfano, PAYE ya Januari inawasilishwa "
  "ifikapo tarehe 7 Februari. Kuchelewa kunaleta adhabu ya asilimia 2.5 kwa kila "
  "mwezi wa ucheleweshaji.",
  "By what date does an employer submit the P10 form each month?",
  "The P10 form (monthly PAYE remittance) is submitted by the 7th of each month following "
  "the pay period. For example, January PAYE is submitted by 7 February. Late submission "
  "attracts a 2.5% penalty for each month of delay.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA filing deadline change",
  "formal", "standard"),

p("tier1a_paye_adv_033_20260609","paye_standard",
  "Tofauti kati ya P9 na P10 ni nini kwa madhumuni ya PAYE?",
  "P10 ni fomu ya KILA MWEZI ya kuwasilisha na kulipa PAYE iliyokatwa kwa kipindi. "
  "P9 ni TAARIFA YA MWAKA ya PAYE — inawasilishwa mara moja kwa mwaka ifikapo tarehe "
  "31 Machi na inatoa muhtasari wa PAYE yote iliyolipwa na mwaka. Waajiri wanahitaji "
  "zote mbili — P10 kila mwezi na P9 mwishoni mwa mwaka.",
  "What is the difference between P9 and P10 for PAYE purposes?",
  "P10 is the MONTHLY form for submitting and paying PAYE deducted for the period. "
  "P9 is the ANNUAL PAYE RETURN — filed once per year by 31 March summarising all PAYE "
  "paid through the year. Employers need both — P10 monthly and P9 at year end.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA filing guidance",
  "business_market", "disambiguation"),

p("tier1a_paye_adv_034_20260609","paye_adversarial",
  "Mfanyakazi mwenye TIN anaweza kuomba TRA imrudishie PAYE yote iliyokatwa bila kuwasilisha PIT return — je, ni kweli?",
  "Hapana. Ili kupata rejesho la PAYE, mfanyakazi lazima aandike na kuwasilisha Personal "
  "Income Tax (PIT) return kwa TRA. TIN peke yake haitoshi — TRA inahitaji taarifa "
  "kamili ya mapato ya mwaka. Baada ya ukaguzi, TRA italipa rejesho la kiasi kilicholipwa "
  "zaidi ya kodi halisi.",
  "An employee with a TIN can request TRA to refund all PAYE deducted without submitting a PIT return — is this true?",
  "No. To receive a PAYE refund an employee must prepare and submit a Personal Income Tax "
  "(PIT) return to TRA. A TIN alone is insufficient — TRA requires a full annual income "
  "statement. After review, TRA will refund the amount overpaid above actual tax liability.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA e-filing guidance",
  "formal", "adversarial"),

p("tier1a_paye_adv_035_20260609","paye_adversarial",
  "Mwajiri wa nyumbani (domestic employer) hana wajibu wa PAYE kwa msaidizi wa nyumbani — je, ni kweli?",
  "Si kweli kwa ujumla. Ikiwa msaidizi wa nyumbani anapata mshahara unaozidi kiwango cha "
  "PAYE cha asilimia sifuri (Shilingi 270,000 kwa mwezi), basi PAYE inatakiwa kisheria. "
  "Waajiri wa nyumbani mara nyingi hawajui wajibu huu, lakini sheria inatumika. "
  "Msaidizi mwenye mshahara wa GN 605A ya chini ana PAYE kidogo au la.",
  "A domestic employer has no PAYE obligation for a household worker — is this true?",
  "Not as a general rule. If a household worker earns above the PAYE zero-rate threshold "
  "(TZS 270,000 per month), PAYE is legally required. Domestic employers often don't know "
  "this obligation, but the law applies. A worker at the lower GN 605A rate would have "
  "minimal or no PAYE.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA PAYE guidance",
  "rural_conversational", "adversarial"),

p("tier1a_paye_adv_036_20260609","paye_standard",
  "Jinsi ya kuhesabu PAYE ya mfanyakazi mwenye mshahara wa Shilingi 400,000 kwa mwezi?",
  "Kwa mshahara wa Shilingi 400,000: "
  "Kanda ya 0%: Shilingi 270,000 → kodi sifuri. "
  "Kanda ya 8%: Shilingi 270,001–400,000 = Shilingi 130,000 × 8% = Shilingi 10,400. "
  "Jumla ya PAYE = Shilingi 10,400 kwa mwezi.",
  "How to calculate PAYE for an employee earning TZS 400,000 per month?",
  "For a salary of TZS 400,000: "
  "0% band: TZS 270,000 → zero tax. "
  "8% band: TZS 270,001–400,000 = TZS 130,000 × 8% = TZS 10,400. "
  "Total PAYE = TZS 10,400 per month.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act PAYE band change",
  "rural_conversational", "standard"),

p("tier1a_paye_adv_037_20260609","paye_adversarial",
  "Kodi ya PAYE inalipwa mwaka mmoja baada ya mwisho wa mwaka wa kodi — je, hii ni sahihi?",
  "Hapana. PAYE inalipwa KILA MWEZI ifikapo tarehe 7 ya mwezi unaofuata — si mwaka mzima "
  "baadaye. Mfumo wa PAYE unafanya kazi kwa msingi wa kulipa-unapopata (pay-as-you-earn) "
  "ili mwajiri akatwe kodi kila mwezi. Kusubiri mwaka ni mfumo wa kodi ya biashara (income "
  "tax), si wa PAYE.",
  "PAYE is paid one year after the end of the tax year — is this correct?",
  "No. PAYE is paid MONTHLY by the 7th of the following month — not a year later. The "
  "PAYE system works on a pay-as-you-earn basis so tax is collected monthly. Annual "
  "settlement is the income tax (corporate) system, not PAYE.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA PAYE guidance",
  "business_market", "adversarial"),

p("tier1a_paye_adv_038_20260609","paye_adversarial",
  "Wafanyakazi wa kampuni za NGO za kigeni hawalazimiki kulipa PAYE kwa sababu NGO imepewa msamaha — je, ni kweli?",
  "Hapana. Msamaha wa kodi wa NGO unahusu MAPATO ya NGO — si mishahara ya wafanyakazi. "
  "Wafanyakazi wa NGO za kigeni wanaofanya kazi Tanzania wanajumuishwa na PAYE kwa "
  "mishahara wanayopata. NGO bado inalazimika kukata na kulipa PAYE kwa wafanyakazi wake.",
  "Employees of foreign NGOs don't need to pay PAYE because the NGO has a tax exemption — is this true?",
  "No. An NGO's tax exemption covers the NGO's OWN INCOME — not employees' salaries. "
  "Employees of foreign NGOs working in Tanzania are subject to PAYE on their earnings. "
  "The NGO still must deduct and remit PAYE for its employees.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA PAYE guidance",
  "formal", "adversarial"),

p("tier1a_paye_adv_039_20260609","paye_adversarial",
  "Kiwango cha PAYE cha asilimia 25 kinatumika kwa mapato kati ya Shilingi 700,001 na 1,000,000 kwa mwezi — je, ni sahihi?",
  "Hapana. Kanda ya asilimia 25 inaanza kwa Shilingi 760,001 — si Shilingi 700,001. "
  "Kanda ya asilimia 20 inaisha kwa Shilingi 760,000 (si 700,000). Kanda kamili za PAYE "
  "za kila mwezi ni: 0% (hadi 270k), 8% (270k–520k), 20% (520k–760k), 25% (760k–1M), "
  "30% (zaidi ya 1M). Shilingi 700,001 iko bado katika kanda ya asilimia 20.",
  "The 25% PAYE band applies to income between TZS 700,001 and 1,000,000 per month — is this correct?",
  "No. The 25% band starts at TZS 760,001 — not TZS 700,001. The 20% band ends at "
  "TZS 760,000 (not 700,000). The full monthly PAYE bands are: 0% (up to 270k), "
  "8% (270k–520k), 20% (520k–760k), 25% (760k–1M), 30% (above 1M). "
  "TZS 700,001 is still within the 20% band.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act PAYE band change",
  "formal", "adversarial"),

p("tier1a_paye_adv_040_20260609","paye_adversarial",
  "Mwajiri anaweza kulipa PAYE mara moja mwaka (lump sum) badala ya kila mwezi — je, ni kweli?",
  "Hapana. PAYE lazima ilipwe kila mwezi ifikapo tarehe 7 — hakuna ruhusa ya kulipa mara "
  "moja kwa mwaka kama mwajiri. Mfumo wa PAYE umeundwa kulipa mwezi kwa mwezi. "
  "Kulimbikiza na kulipa mwaka mzima kwa mkupuo kunasababisha adhabu za ucheleweshaji "
  "wa kila mwezi ambao ulishindwa kulipa kwa wakati.",
  "An employer can pay PAYE as an annual lump sum instead of monthly — is this true?",
  "No. PAYE must be paid monthly by the 7th — there is no employer permission to pay "
  "annually in a lump sum. The PAYE system is designed for monthly remittance. "
  "Accumulating and paying for the whole year in one go generates monthly late-payment "
  "penalties for every month that was not paid on time.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA PAYE guidance",
  "business_market", "adversarial"),

p("tier1a_paye_adv_041_20260609","paye_adversarial",
  "Posho ya chakula (meal allowance) haikodiwi PAYE ikiwa inatolewa kila siku — je, ni kweli?",
  "Si kweli kwa ujumla. Posho ya chakula inayolipwa kwa pesa moja kwa moja kwa mfanyakazi "
  "kwa kawaida inajumuishwa kama mapato yanayotoza PAYE. Chakula kinachotolewa mahali pa "
  "kazi moja kwa moja (kama canteen au mlo wa bure) kinaweza kuwa na matibabu tofauti. "
  "Mazingira ya kila kampuni yanaweza kutofautiana — tathmini na mshauri wa kodi.",
  "A daily meal allowance paid in cash is not subject to PAYE — is this true?",
  "Not as a general rule. A meal allowance paid as cash directly to the employee is "
  "generally included as PAYE-taxable income. Meals provided in-kind at the workplace "
  "(such as a canteen or free meal) may have different treatment. Each company's specific "
  "circumstances may vary — assess with a tax adviser.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "formal", "adversarial"),

p("tier1a_paye_adv_042_20260609","paye_adversarial",
  "Kampuni inayoanza mnamo Julai inaanza PAYE kuanzia Januari ya mwaka unaofuata — je, ni kweli?",
  "Hapana. PAYE inaanza mara moja tu mfanyakazi anaanza kulipwa mshahara unaopita "
  "kiwango cha msamaha cha Shilingi 270,000 kwa mwezi. Hakuna kipindi cha kusubiri "
  "hadi Januari — wajibu wa PAYE unaanza mwezi wa kwanza wa malipo. Kampuni mpya "
  "inapaswa kuomba TIN na kusajili PAYE mara inapoanza kulipa mishahara.",
  "A company starting in July begins PAYE only from January of the following year — is this true?",
  "No. PAYE begins immediately once an employee is paid a salary exceeding the TZS 270,000 "
  "per month exemption. There is no waiting until January — PAYE obligation starts in the "
  "first month of payment. A new company should obtain a TIN and register for PAYE as "
  "soon as it begins paying salaries.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA PAYE guidance",
  "business_market", "adversarial"),

p("tier1a_paye_adv_043_20260609","paye_standard",
  "Mfanyakazi wa kigeni (expatriate) analipa PAYE Tanzania kwa njia gani?",
  "Mfanyakazi wa kigeni anayefanya kazi Tanzania na kupata mshahara Tanzania analipa "
  "PAYE kwa njia ile ile ya wafanyakazi wa ndani — mwajiri anakata PAYE na kulipa TRA "
  "kila mwezi. Ikiwa mfanyakazi ana makao makuu Tanzania, analipa kodi ya mapato yote "
  "duniani. Mikataba ya kuepuka kutozwa kodi mara mbili (DTAs) inaweza kutoa uondoaji "
  "kwa nchi fulani.",
  "How does a foreign (expatriate) employee pay PAYE in Tanzania?",
  "A foreign employee working in Tanzania and receiving a Tanzania salary pays PAYE "
  "the same way as local employees — the employer deducts PAYE and remits to TRA monthly. "
  "If the employee has permanent establishment in Tanzania, worldwide income may be "
  "taxable. Double Taxation Agreements (DTAs) may provide relief for specific countries.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA PAYE guidance",
  "formal", "standard"),

p("tier1a_paye_adv_044_20260609","paye_adversarial",
  "Mwajiri aliye na deni la PAYE anaweza kulipa kidogo kidogo kwa miaka mingi bila faini — je, ni kweli?",
  "Hapana. Deni la PAYE linasababisha adhabu ya asilimia 2.5 kwa kila mwezi wa "
  "ucheleweshaji wa kila kiasi kilichodaiwa, pamoja na riba ya kisheria ya TRA. Hakuna "
  "muda wa kulipa bila adhabu bila kukubaliana na TRA kwa mpango rasmi wa makubaliano ya "
  "malipo (payment plan). Bila makubaliano, adhabu zinaendelea kukusanyika.",
  "An employer with PAYE arrears can pay gradually over many years without penalties — is this true?",
  "No. PAYE arrears attract a 2.5% penalty per month of delay on each outstanding amount, "
  "plus TRA statutory interest. There is no penalty-free payment period without agreeing a "
  "formal payment plan with TRA. Without an agreement, penalties continue to accumulate.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA enforcement guidance",
  "formal", "adversarial"),

p("tier1a_paye_adv_045_20260609","paye_adversarial",
  "PAYE haihusiani na SDL na NSSF — kila moja inalipwa kwa shirika tofauti kabisa — je, ni kweli?",
  "Si kweli kabisa. PAYE, SDL, na NSSF zote tatu zinahusiana na payroll ya mfanyakazi "
  "na zinashughulikia kwa wakati mmoja. PAYE inalipwa TRA, SDL inalipwa TRA, na NSSF "
  "inalipwa NSSF. Ingawa shirika la kupokea linatofautiana, mwajiri huzihesabu na "
  "kuzilipa zote kama sehemu ya mzunguko mmoja wa mishahara.",
  "PAYE has nothing to do with SDL and NSSF — each is paid to an entirely different agency — is this true?",
  "Not entirely. PAYE, SDL, and NSSF are all linked to the employee payroll and handled "
  "simultaneously. PAYE goes to TRA, SDL goes to TRA, and NSSF goes to NSSF. While the "
  "receiving agency differs, the employer calculates and pays all of them as part of one "
  "payroll cycle.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA payroll guidance",
  "business_market", "disambiguation"),

p("tier1a_paye_adv_046_20260609","paye_adversarial",
  "Kiwango cha PAYE ni sawa kwa wafanyakazi wote bila kujali mapato — asilimia 30 kwa wote — je, ni kweli?",
  "Hapana. PAYE Tanzania ni KIWANGO CHA UENDELEZAJI (progressive rate) — si kiwango "
  "kimoja cha asilimia 30 kwa wote. Watu wenye mapato madogo wanalipa kidogo au hawalipi "
  "chochote; watu wenye mapato makubwa wanalipa zaidi. Kanda tano za kodi zinatumika: "
  "0%, 8%, 20%, 25%, na 30% kulingana na kiwango cha mapato.",
  "The PAYE rate is the same for all employees regardless of income — 30% for everyone — is this true?",
  "No. Tanzania's PAYE is a PROGRESSIVE RATE — not a flat 30% for everyone. Lower "
  "earners pay little or nothing; higher earners pay more. Five tax bands apply: 0%, "
  "8%, 20%, 25%, and 30% depending on the income level.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act PAYE band change",
  "rural_conversational", "adversarial"),

p("tier1a_paye_adv_047_20260609","paye_adversarial",
  "Faida ya bima ya afya ya mfanyakazi inayolipwa na mwajiri haitozi PAYE kamwe — je, ni kweli?",
  "Si kweli kwa ujumla. Malipo ya bima ya afya yanayolipwa na mwajiri kwa niaba ya "
  "mfanyakazi yanaweza kuwa sehemu ya mapato yanayotoza PAYE kulingana na hali na "
  "kiwango. Kwa umakini, waajiri wanahitaji tathmini ya kila hali na mshauri wa kodi "
  "ili kujua kama bima ya afya inajumuishwa kwenye mapato ya PAYE au la.",
  "Medical insurance premiums paid by an employer for an employee are never subject to PAYE — is this true?",
  "Not as a general rule. Employer-paid medical insurance premiums for an employee can "
  "be part of PAYE-taxable income depending on the circumstances and the amount. Employers "
  "need a case-by-case assessment with a tax adviser to determine whether health insurance "
  "contributions are included in PAYE income.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act amendment",
  "formal", "adversarial"),

p("tier1a_paye_adv_048_20260609","paye_standard",
  "Mwajiri anaweza kurekebisha makosa ya PAYE ya miezi iliyopita vipi?",
  "Mwajiri anaweza kurekebisha makosa ya PAYE ya miezi iliyopita kwa: (1) kuwasilisha "
  "marekebisho ya P10 kwa TRA ikionyesha kiasi sahihi, (2) kulipa tofauti pamoja na "
  "adhabu na riba inayohusika, na (3) kurekebisha rekodi za wafanyakazi. Ni bora "
  "kuwasiliana na TRA mapema kama marekesiho yanahusisha kiasi kikubwa.",
  "How can an employer correct past PAYE errors for previous months?",
  "An employer can correct past PAYE errors by: (1) submitting an amended P10 to TRA "
  "showing the correct amount, (2) paying the difference plus applicable penalties and "
  "interest, and (3) correcting employee records. It is advisable to contact TRA early "
  "if the correction involves a significant amount.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA PAYE correction procedure",
  "business_market", "standard"),

p("tier1a_paye_adv_049_20260609","paye_standard",
  "PAYE inakokotolewa kwa msingi wa mshahara gani — jumla au mshahara wa msingi tu?",
  "PAYE inakokotolewa kwa MSHAHARA WA JUMLA (gross taxable employment income) — "
  "si mshahara wa msingi tu. Mapato yanayotoza PAYE yanajumuisha: mshahara wa msingi, "
  "posho za jumla, bonasi, na faida nyingine zinazotolewa na mwajiri. Posho maalum "
  "zinazoidhinishwa kwa kanuni zinaweza kutolewa.",
  "Is PAYE calculated on gross salary or basic salary only?",
  "PAYE is calculated on TOTAL GROSS TAXABLE EMPLOYMENT INCOME — not just basic salary. "
  "Taxable employment income includes: basic salary, general allowances, bonuses, and "
  "other employer-provided benefits. Specific allowances that meet regulatory conditions "
  "may be excluded.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA PAYE guidance",
  "formal", "standard"),

p("tier1a_paye_adv_050_20260609","paye_adversarial",
  "Mwajiri anapata adhabu ya asilimia 10 mara moja kwa kuchelewa kulipa PAYE — je, ni sahihi?",
  "Hapana. Adhabu ya PAYE ni asilimia 2.5 kwa kila MWEZI wa ucheleweshaji — si "
  "asilimia 10 mara moja. Kwa hivyo baada ya miezi 4, jumla ya adhabu inakuwa asilimia "
  "10, lakini inakua kwa mwezi. Kiwango cha asilimia 10 mara moja si sahihi chini ya "
  "sheria ya Tanzania.",
  "An employer receives a one-time 10% penalty for late PAYE payment — is this correct?",
  "No. The PAYE penalty is 2.5% for each MONTH of delay — not a one-time 10%. After "
  "4 months of delay the cumulative penalty reaches 10%, but it accrues monthly. "
  "A one-time flat 10% rate is incorrect under Tanzania law.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act penalty rate change",
  "business_market", "adversarial"),

# =====================================================================
# WHT DEEP — first 10 pairs (wht_deep_001–010)
# Source: tra.go.tz | Finance Act 2025
# =====================================================================

p("tier1a_wht_deep_001_20260609","wht_withholding_tax",
  "Kiwango cha withholding tax kwa royalties kwa wakazi wa Tanzania ni asilimia ngapi?",
  "Kiwango cha withholding tax kwa royalties kwa WAKAZI wa Tanzania ni asilimia 15. "
  "Kwa WASIO WAKAZI, kiwango pia ni asilimia 15. Kiwango hiki kinatumika kwa malipo "
  "ya haki ya matumizi ya mali ya kiakili, mauzo ya teknolojia, na malipo yanayofanana.",
  "What is the withholding tax rate on royalties for Tanzania residents?",
  "The withholding tax rate on royalties for Tanzania RESIDENTS is 15%. For "
  "NON-RESIDENTS the rate is also 15%. This rate applies to payments for use of "
  "intellectual property rights, technology transfers, and similar payments.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act WHT rate change",
  "formal", "standard"),

p("tier1a_wht_deep_002_20260609","wht_withholding_tax",
  "Withholding tax kwa royalties ni asilimia 10 kwa wasio wakazi — je, hii ni sahihi?",
  "Hapana. Kiwango cha withholding tax kwa royalties kwa wasio wakazi ni asilimia 15 — "
  "si asilimia 10. Kiwango hiki kinatumika kwa wakazi na wasio wakazi sawa. "
  "Kiwango cha asilimia 10 si sahihi kwa royalties Tanzania.",
  "Withholding tax on royalties is 10% for non-residents — is this correct?",
  "No. The withholding tax rate on royalties for non-residents is 15% — not 10%. "
  "This rate applies equally to residents and non-residents. A rate of 10% is "
  "incorrect for royalties in Tanzania.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act WHT rate change",
  "business_market", "adversarial"),

p("tier1a_wht_deep_003_20260609","wht_withholding_tax",
  "Kiwango cha WHT kwa gawio (dividends) kwa wakazi ni asilimia ngapi?",
  "Kiwango cha withholding tax kwa gawio kwa wakazi wa Tanzania ni asilimia 10. "
  "Kwa wasio wakazi, kiwango pia ni asilimia 10. Mwajiri au kampuni inayotoa gawio "
  "inalazimika kukata WHT kabla ya kulipa mpokeaji.",
  "What is the WHT rate on dividends for residents?",
  "The withholding tax rate on dividends for Tanzania residents is 10%. For "
  "non-residents the rate is also 10%. The paying company must deduct WHT before "
  "remitting dividends to the recipient.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act WHT rate change",
  "formal", "standard"),

p("tier1a_wht_deep_004_20260609","wht_withholding_tax",
  "WHT kwa riba (interest) ni asilimia ngapi kwa wakazi na wasio wakazi?",
  "Kiwango cha withholding tax kwa riba ni asilimia 10 kwa wakazi na pia asilimia 10 "
  "kwa wasio wakazi. Kiwango hiki kinatumika kwa malipo ya riba yanayolipwa na benki, "
  "makampuni, au watu binafsi.",
  "What is the WHT rate on interest for residents and non-residents?",
  "The withholding tax rate on interest is 10% for residents and 10% for "
  "non-residents. This rate applies to interest payments made by banks, companies, "
  "or individuals.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act WHT rate change",
  "business_market", "standard"),

p("tier1a_wht_deep_005_20260609","wht_withholding_tax",
  "WHT kwa ada za usimamizi na huduma za kitaalamu (management/professional fees) kwa wakazi ni asilimia ngapi?",
  "Kiwango cha WHT kwa ada za usimamizi na huduma za kitaalamu kwa wakazi ni asilimia 5. "
  "Kwa wasio wakazi, kiwango ni asilimia 15. Tofauti hii kati ya wakazi na wasio wakazi "
  "ni muhimu kwa makampuni yanayolipa ada kwa wataalam wa kigeni.",
  "What is the WHT rate on management and professional service fees for residents?",
  "The WHT rate on management and professional service fees for residents is 5%. "
  "For non-residents the rate is 15%. This difference between residents and non-residents "
  "is important for companies paying fees to foreign experts.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act WHT rate change",
  "formal", "standard"),

p("tier1a_wht_deep_006_20260609","wht_withholding_tax",
  "WHT kwa ada za mkurugenzi (director fees) kwa wakazi ni asilimia ngapi?",
  "Kiwango cha WHT kwa ada za mkurugenzi kwa wakazi wa Tanzania ni asilimia 15. "
  "Kwa wasio wakazi, kiwango ni asilimia 20. WHT inakatwa na kampuni kabla ya kulipa "
  "mkurugenzi. Hii ni kwa ada za mkurugenzi zinazolipwa kama ujumbe, si mshahara wa ajira.",
  "What is the WHT rate on director fees for residents?",
  "The WHT rate on director fees for Tanzania residents is 15%. For non-residents "
  "the rate is 20%. WHT is deducted by the company before paying the director. "
  "This applies to director fees paid as a sitting allowance, not as employment salary.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act WHT rate change",
  "business_market", "standard"),

p("tier1a_wht_deep_007_20260609","wht_withholding_tax",
  "WHT kwa kodi ya pango (rent) kwa wakazi na wasio wakazi ni asilimia ngapi?",
  "WHT kwa kodi ya pango (rent) kwa wakazi wa Tanzania ni asilimia 10. "
  "Kwa wasio wakazi, kiwango ni asilimia 20. Mtu anayelipia kodi ya pango "
  "kwa mmiliki wa nyumba analazimika kukata WHT kabla ya kulipa na kulipa "
  "TRA ifikapo tarehe 7 ya mwezi unaofuata.",
  "What is the WHT rate on rent for residents and non-residents?",
  "WHT on rent for Tanzania residents is 10%. For non-residents the rate is 20%. "
  "The person paying rent to a property owner must deduct WHT before paying and "
  "remit to TRA by the 7th of the following month.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act WHT rate change",
  "formal", "standard"),

p("tier1a_wht_deep_008_20260609","wht_withholding_tax",
  "Ada za mkurugenzi wa Tanzania (mkazi) zinatoza asilimia 20 ya WHT — je, hii ni sahihi?",
  "Hapana. Ada za mkurugenzi wa Tanzania mkazi zinatoza WHT ya asilimia 15 — si asilimia 20. "
  "Kiwango cha asilimia 20 ni kwa mkurugenzi ASIYE MKAZI (non-resident). Tofauti hii "
  "kati ya mkazi (15%) na asiye mkazi (20%) ni muhimu sana kuhesabu vizuri.",
  "Director fees for a Tanzanian (resident) director attract 20% WHT — is this correct?",
  "No. Director fees for a Tanzania resident director attract 15% WHT — not 20%. "
  "The 20% rate is for NON-RESIDENT directors. This distinction between resident (15%) "
  "and non-resident (20%) is critical to calculate correctly.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act WHT rate change",
  "business_market", "adversarial"),

p("tier1a_wht_deep_009_20260609","wht_withholding_tax",
  "WHT inalipwa TRA tarehe ngapi baada ya kukata?",
  "WHT inalipwa TRA ifikapo tarehe 7 ya mwezi unaofuata baada ya kukata. Kwa mfano, "
  "WHT iliyokatwa Januari inalipwa ifikapo tarehe 7 Februari. Cheti cha WHT "
  "(withholding tax certificate) hutolewa kwa mlipwaji ndani ya siku 30 za kukata.",
  "By what date is WHT remitted to TRA after deduction?",
  "WHT is remitted to TRA by the 7th of the following month after deduction. For "
  "example, WHT deducted in January is paid by 7 February. A WHT certificate is "
  "issued to the payee within 30 days of deduction.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "TRA filing deadline change",
  "formal", "standard"),

p("tier1a_wht_deep_010_20260609","wht_withholding_tax",
  "WHT kwa bima (insurance premiums) ni asilimia ngapi?",
  "WHT kwa malipo ya bima ni asilimia 5. Hii inatumika kwa malipo ya premium ya bima "
  "yanayolipwa kwa kampuni za bima. Kiwango hiki kinatumika bila kujali kama kampuni "
  "ya bima ni ya ndani au ya kigeni.",
  "What is the WHT rate on insurance premiums?",
  "WHT on insurance premium payments is 5%. This applies to insurance premium payments "
  "made to insurance companies. This rate applies regardless of whether the insurance "
  "company is domestic or foreign.",
  TRA, TRA_N, GP, "2025-07-01", ANN, "Finance Act WHT rate change",
  "rural_conversational", "standard"),

]

written = 0
with open(OUT, "a", encoding="utf-8") as f:
    for pr in pairs:
        f.write(json.dumps(pr, ensure_ascii=False) + "\n")
        written += 1

total = sum(1 for _ in open(OUT, encoding="utf-8") if _.strip())
print(f"Part 3: wrote {written} pairs")
print(f"Total in file: {total}")
