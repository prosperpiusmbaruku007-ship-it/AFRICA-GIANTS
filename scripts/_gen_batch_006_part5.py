#!/usr/bin/env python3
"""
batch_006 part 5: paye_foreign_employees — 50 pairs
IDs: b006_paye_for_001 – b006_paye_for_050
Target: PAYE obligations for foreign/expatriate employees working in Tanzania
Source: TRA PAYE page (government_portal)
Append to: datasets/tier1a/raw_sources/raw_pairs_batch_006.jsonl
"""
import json, os

OUT = "datasets/tier1a/raw_sources/raw_pairs_batch_006.jsonl"
SRC = "https://www.tra.go.tz/page/pay-as-you-earn-paye"
NAME = "TRA - Pay As You Earn (PAYE)"
REVIEW = "Finance Act amendment changing PAYE bands or non-resident tax treatment"

def p(id_, q_sw, a_sw, q_en, a_en, register, pair_type):
    return {
        "id": id_,
        "domain": "tier1a",
        "subdomain": "paye_foreign_employees",
        "question_sw": q_sw,
        "answer_sw": a_sw,
        "question_en": q_en,
        "answer_en": a_en,
        "primary_source_url": SRC,
        "primary_source_name": NAME,
        "source_type": "government_portal",
        "effective_date": "2025-07-01",
        "decay_risk": "annual",
        "next_review_trigger": REVIEW,
        "verified_by": "founder_self_review",
        "verified_date": "2026-06-10",
        "register": register,
        "pair_type": pair_type,
        "eval_set": False
    }

pairs = [

# --- Group 1: PAYE applies to ALL employees ---

p("b006_paye_for_001",
  "Mfanyakazi mgeni (expatriate) Tanzania analipa PAYE kama Mtanzania?",
  "Ndiyo. PAYE inatumika kwa wafanyakazi WOTE wanaofanya kazi Tanzania — wakiwemo wageni na wasio na makazi ya kudumu. Mwajiri analazimika kukata PAYE kutoka kwa mshahara wa mfanyakazi mgeni na kulipa TRA ifikapo tarehe 7 ya mwezi unaofuata, kama ilivyo kwa wafanyakazi wote wengine.",
  "Does a foreign (expatriate) employee in Tanzania pay PAYE like a Tanzanian?",
  "Yes. PAYE applies to ALL employees working in Tanzania — including foreigners and non-permanent residents. The employer is required to deduct PAYE from a foreign employee's salary and remit to TRA by the 7th of the following month, just as with all other employees.",
  "formal", "standard"),

p("b006_paye_for_002",
  "Je, kampuni inaweza kutomkata PAYE mfanyakazi wake mgeni kwa sababu yeye ni mgeni?",
  "Hapana. Utaifa wa mfanyakazi haathiri wajibu wa PAYE wa mwajiri. Kampuni inaweza kuadhibiwa kwa kushindwa kukata na kuwasilisha PAYE ya mfanyakazi mgeni. PAYE inategemea mahali pa kufanya kazi (Tanzania), si utaifa wa mfanyakazi.",
  "Can a company skip withholding PAYE for a foreign employee because they are foreign?",
  "No. An employee's nationality does not affect the employer's PAYE obligation. A company can be penalized for failing to deduct and remit PAYE for a foreign employee. PAYE depends on the place of work (Tanzania), not the employee's nationality.",
  "formal", "adversarial"),

p("b006_paye_for_003",
  "Mfanyakazi mgeni aliye na Class A work permit (investor) — analipa PAYE?",
  "Class A work permit ni ya wawekezaji wanaojitegemea — si wafanyakazi waliohiriwa. Mmiliki wa Class A anayefanya kazi kama mwajiriwa (employed) katika kampuni yake anahitaji kutathmini hali yake ya kisheria. Lakini kama mtu ana mshahara kutoka kampuni, PAYE itatumika. Thibitisha muundo maalum na mshauri wa kodi.",
  "A foreign employee with a Class A work permit (investor) — do they pay PAYE?",
  "Class A is for self-employed investors — not hired employees. A Class A holder working as an employee in their own company needs to assess their legal status. But if a person receives a salary from a company, PAYE applies. Confirm the specific structure with a tax advisor.",
  "formal", "disambiguation"),

p("b006_paye_for_004",
  "Je, mfanyakazi mgeni aliye Tanzania kwa mwezi mmoja tu analipa PAYE?",
  "Inategemea muundo wa ajira. Mfanyakazi aliyehiriwa na mwajiri wa Tanzania na kupata mshahara kutoka Tanzania analipa PAYE kwa kipindi chochote cha kufanya kazi Tanzania. Kwa ziara za muda mfupi za kibiashara (si kazi ya kawaida), PAYE inaweza isitumike. Thibitisha hali maalum na TRA au mshauri wa kodi.",
  "Does a foreign employee in Tanzania for just one month pay PAYE?",
  "It depends on the employment structure. An employee hired by a Tanzanian employer receiving salary from Tanzania pays PAYE for any period of working in Tanzania. For brief business visits (not regular work), PAYE may not apply. Confirm the specific situation with TRA or a tax advisor.",
  "formal", "disambiguation"),

p("b006_paye_for_005",
  "Mshahara wa mfanyakazi mgeni unaopatikana nje ya Tanzania — PAYE Tanzania inatumika?",
  "Inategemea hali ya usajili wa kazi. Ikiwa mfanyakazi anafanya kazi Tanzania kwa ajili ya mwajiri wa Tanzania na mshahara unalipwa nje ya nchi, TRA inaweza bado kuhitaji PAYE Tanzania. 'Shadow payroll' ni mfumo unaotumika katika hali kama hizi — mwajiri anahifadhi rekodi za PAYE Tanzania hata kama mshahara unalipwa nje. Thibitisha na TRA.",
  "A foreign employee's salary paid outside Tanzania — does Tanzania PAYE apply?",
  "It depends on the employment arrangement. If the employee works in Tanzania for a Tanzanian employer and salary is paid outside the country, TRA may still require Tanzania PAYE. 'Shadow payroll' is a system used in such cases — the employer maintains Tanzania PAYE records even though salary is paid abroad. Verify with TRA.",
  "formal", "disambiguation"),

# --- Group 2: Non-cash benefits as taxable income ---

p("b006_paye_for_006",
  "Posho ya nyumba inayolipwa kwa mfanyakazi mgeni — ni mapato yanayolazimika PAYE?",
  "Ndiyo. Posho ya nyumba (housing allowance) inachukuliwa kama sehemu ya mapato ya ajira na inabeba PAYE. Hii inatumika kwa wafanyakazi wote — raia na wageni. Posho ya nyumba inajumlishwa pamoja na mshahara wa msingi kwa madhumuni ya kuhesabu PAYE.",
  "Housing allowance paid to a foreign employee — is it subject to PAYE?",
  "Yes. Housing allowance is treated as employment income and is subject to PAYE. This applies to all employees — citizens and foreigners. Housing allowance is added to basic salary for the purpose of calculating PAYE.",
  "formal", "standard"),

p("b006_paye_for_007",
  "Kampuni inatoa nyumba kwa mfanyakazi mgeni bila gharama — je, thamani yake ni mapato?",
  "Ndiyo. Nyumba inayotolewa bure na mwajiri (accommodation in kind) inachukuliwa kama manufaa ya kazi (employment benefit) inayopaswa kuthaminiwa na kujumlishwa kwenye mapato ya ajira kwa madhumuni ya PAYE. Thamani ya nyumba iliyotolewa bure inakokotolewa kwa kiwango cha soko au kwa njia iliyowekwa na TRA.",
  "A company provides free housing to a foreign employee — is the value treated as income?",
  "Yes. Employer-provided housing (accommodation in kind) is treated as an employment benefit that must be valued and added to employment income for PAYE purposes. The value of free housing is calculated at market rates or by a TRA-prescribed method.",
  "formal", "standard"),

p("b006_paye_for_008",
  "Gari la kampuni linalotumika na mfanyakazi kwa matumizi ya kibinafsi — PAYE inatumika?",
  "Ndiyo. Manufaa ya gari la kampuni yanayotumiwa kwa matumizi ya kibinafsi (personal use of company car) yanachukuliwa kama mapato yanayolazimika PAYE. TRA ina njia ya kuhesabu thamani ya manufaa haya. Matumizi ya gari kwa ajili ya biashara tu hayajumuishwi.",
  "Company car used by an employee for personal use — does PAYE apply?",
  "Yes. The benefit of a company car used for personal use is treated as taxable employment income. TRA has a prescribed method for valuing this benefit. Use strictly for business purposes is not included.",
  "formal", "standard"),

p("b006_paye_for_009",
  "Ada za shule za watoto wa mfanyakazi mgeni zinazolipwa na mwajiri — PAYE inahusika?",
  "Ndiyo. Ada za shule za watoto wanaolipwa na mwajiri (school fees paid by employer) zinachukuliwa kama manufaa ya kazi yanayolazimika PAYE. Inajumlishwa kwenye mapato ya ajira ya mfanyakazi mgeni. Hii ni faida inayolipwa kwa niaba ya mfanyakazi — hivyo inajumuishwa kwa PAYE.",
  "School fees for a foreign employee's children paid by the employer — is PAYE involved?",
  "Yes. School fees for children paid by the employer are treated as taxable employment benefits. They are added to the foreign employee's employment income for PAYE. This is a benefit paid on behalf of the employee — so it is included for PAYE.",
  "formal", "standard"),

p("b006_paye_for_010",
  "Tikiti ya ndege ya kwenda nchi ya asili — ni manufaa yanayolazimika PAYE?",
  "Kwa ujumla, tikiti za ndege zinazolipwa na mwajiri kwa ajili ya likizo ya mfanyakazi au safari za kibinafsi zinachukuliwa kama manufaa yanayolazimika PAYE. Hata hivyo, tikiti za safari za biashara (business travel) hazijumuishwi. Thibitisha hali ya tikiti maalum na mshauri wa kodi ili kuepuka kosa.",
  "A return flight ticket to home country — is it a taxable employment benefit?",
  "Generally, flight tickets paid by the employer for an employee's vacation or personal travel are treated as taxable employment benefits. However, business travel tickets are not included. Verify the status of specific tickets with a tax advisor to avoid errors.",
  "formal", "standard"),

# --- Group 3: PAYE bands and calculation for foreign employees ---

p("b006_paye_for_011",
  "Mfanyakazi mgeni analipa kwa kiwango gani cha PAYE — kina tofauti na raia?",
  "Kwa wafanyakazi wa kawaida wa ajira (employees), viwango vya PAYE ni sawa kwa raia na wageni wanaofanya kazi Tanzania. Viwango vya PAYE vya Tanzania (mwaka 2025/2026) ni vya kijumla: 0% kwa chini ya TZS 270,000/mwezi, 8%-30% kwa viwango vya juu zaidi. Tofauti inaweza kuwepo kwa watu wa hali maalum kama wasio na makazi (non-residents) — thibitisha na TRA.",
  "Does a foreign employee pay PAYE at a different rate from a citizen?",
  "For regular employees, PAYE rates are the same for citizens and foreigners working in Tanzania. Tanzania PAYE rates (2025/2026) are graduated: 0% below TZS 270,000/month, 8%-30% for higher brackets. Differences may exist for persons with special status like non-residents — verify with TRA.",
  "formal", "standard"),

p("b006_paye_for_012",
  "Mfanyakazi mgeni anaishi Tanzania na anafanya kazi Tanzania — anakuwa mkazi wa kodi (tax resident)?",
  "Kwa ujumla, mtu aliyekaa Tanzania kwa siku 183 au zaidi katika mwaka wa kodi anakuwa mkazi wa kodi Tanzania. Hali ya mkazi wa kodi inaathiri jinsi mapato yake yoyote nje ya Tanzania yanavyoshughulikiwa. Kwa PAYE ya mfanyakazi, mwajiri anakata kwa kiwango cha kawaida bila kujali hali ya makazi — thibitisha tofauti za non-resident na TRA.",
  "A foreign employee living and working in Tanzania — do they become a tax resident?",
  "Generally, a person who has stayed in Tanzania for 183 or more days in a tax year becomes a Tanzania tax resident. Tax residency affects how their worldwide income is treated. For employee PAYE, the employer deducts at standard rates regardless of residence status — verify non-resident differences with TRA.",
  "formal", "standard"),

p("b006_paye_for_013",
  "Personal relief ya PAYE inapatikana kwa wafanyakazi wageni?",
  "Personal relief ya TZS 270,000/mwezi (TZS 3,240,000/mwaka) kwa kawaida inapatikana kwa wafanyakazi wanaofanya kazi Tanzania — raia na wageni wenye hali ya makazi ya kawaida. Hata hivyo, hali ya personal relief kwa wasio na makazi (non-residents) inaweza kutofautiana. Thibitisha na TRA kwa hali maalum ya mfanyakazi wako.",
  "Is the PAYE personal relief available to foreign employees?",
  "Personal relief of TZS 270,000/month (TZS 3,240,000/year) is generally available to employees working in Tanzania — citizens and foreigners with regular residence status. However, personal relief treatment for non-residents may differ. Verify with TRA for your employee's specific situation.",
  "formal", "disambiguation"),

p("b006_paye_for_014",
  "Mfanyakazi mgeni anapata mshahara wa USD 5,000 kwa mwezi — PAYE inahesabiwa kwa USD au TZS?",
  "PAYE inahesabiwa na kulipwa TRA kwa Shilingi za Tanzania (TZS). Mshahara wa USD lazima ubadilishwe kuwa TZS kwa kiwango cha ubadilishaji cha siku ya malipo (au kiwango kilichoidhinishwa na TRA). Kisha viwango vya PAYE vya Tanzania vinatumika kwa kiasi cha TZS.",
  "A foreign employee receives a salary of USD 5,000 per month — is PAYE calculated in USD or TZS?",
  "PAYE is calculated and paid to TRA in Tanzanian Shillings (TZS). A USD salary must be converted to TZS at the exchange rate on the payment date (or a TRA-approved rate). Tanzania's PAYE bands are then applied to the TZS amount.",
  "formal", "standard"),

p("b006_paye_for_015",
  "Mwajiri anayetoa mshahara wa mgeni — anaweza kuficha mshahara fulani kutoka PAYE?",
  "Hapana. Mwajiri anahitaji kujumuisha MAPATO YOTE ya ajira — mshahara wa msingi, posho, manufaa, na malipo mengine — kwenye hesabu ya PAYE. Kuficha sehemu ya mshahara au manufaa TRA ni ukiukaji wa sheria ya PAYE na unaweza kusababisha adhabu na deni la PAYE.",
  "An employer paying a foreign employee — can they hide part of the salary from PAYE?",
  "No. The employer must include ALL employment income — basic salary, allowances, benefits, and other payments — in the PAYE calculation. Concealing part of the salary or benefits from TRA is a violation of PAYE law and can result in penalties and PAYE arrears.",
  "formal", "adversarial"),

# --- Group 4: Employer obligations ---

p("b006_paye_for_016",
  "Mwajiri anahitaji nini kwa mfanyakazi mgeni mpya — hatua za PAYE?",
  "Hatua za PAYE kwa mfanyakazi mgeni mpya: (1) Omba TIN (Tax Identification Number) kwa mfanyakazi ikiwa hana; (2) Jiandikishe TRA kama mwajiri ukiwa bado hujafanya hivyo; (3) Anza kukata PAYE kuanzia mshahara wa kwanza; (4) Wasilisha PAYE return ya kila mwezi ifikapo tarehe 7; (5) Toa P9 form mwishoni mwa mwaka wa kodi (kabla ya 31 Machi).",
  "What does an employer need for a new foreign employee — PAYE steps?",
  "PAYE steps for a new foreign employee: (1) Apply for a TIN (Tax Identification Number) for the employee if they don't have one; (2) Register with TRA as an employer if not already done; (3) Start deducting PAYE from the first salary payment; (4) File monthly PAYE returns by the 7th; (5) Issue a P9 form at the end of the tax year (before 31 March).",
  "formal", "standard"),

p("b006_paye_for_017",
  "Je, mfanyakazi mgeni anahitaji TIN Tanzania kwa PAYE?",
  "Ndiyo. Kila mtu anayepokea mapato Tanzania — raia au mgeni — anahitaji TIN (Tax Identification Number) ya TRA. TIN inahitajika kwa mwajiri kuwasilisha PAYE returns na kwa mfanyakazi kuwasilisha kodi zake binafsi. Omba TIN kwa mfanyakazi mgeni wako mapema iwezekanavyo baada ya kuanza kazi.",
  "Does a foreign employee need a Tanzania TIN for PAYE?",
  "Yes. Every person receiving income in Tanzania — citizens and foreigners — needs a TRA TIN (Tax Identification Number). The TIN is required for the employer to file PAYE returns and for the employee to file personal taxes. Apply for a TIN for your foreign employee as early as possible after they start work.",
  "business_market", "standard"),

p("b006_paye_for_018",
  "P9 form kwa mfanyakazi mgeni — ni nini na inapaswa kutolewa lini?",
  "P9 form ni hati ya muhtasari ya kila mwaka wa kodi inayoonyesha: jumla ya mapato ya mfanyakazi, jumla ya PAYE iliyokatwa, na personal relief iliyotumika. Inahitajika kutolewa na mwajiri kwa kila mfanyakazi — raia na wageni — kabla ya 31 Machi ya mwaka unaofuata wa kodi.",
  "P9 form for a foreign employee — what is it and when must it be issued?",
  "The P9 form is an annual tax year summary document showing: total employee income, total PAYE deducted, and personal relief applied. It must be issued by the employer to every employee — citizens and foreigners — before 31 March of the following tax year.",
  "formal", "standard"),

p("b006_paye_for_019",
  "Adhabu ya mwajiri asiyekata PAYE ya mfanyakazi mgeni ni nini?",
  "Mwajiri asiyekata PAYE ya mfanyakazi (raia au mgeni) anakabiliwa na: (1) Adhabu ya 2.5% ya kila mwezi juu ya kiasi kilichokosekana; (2) Riba inayoendelea; (3) TRA inaweza kufanya ukaguzi na kudai PAYE na adhabu zote. Mwajiri anaweza pia kuwa liable kibinafsi kwa PAYE isiyolipwa — hata kama mfanyakazi ameshaacha kazi.",
  "What is the penalty for an employer who fails to deduct PAYE for a foreign employee?",
  "An employer who fails to deduct PAYE for any employee (citizen or foreign) faces: (1) A 2.5% penalty per month on the shortfall; (2) Ongoing interest; (3) TRA may audit and claim all PAYE and penalties due. The employer can also be personally liable for unpaid PAYE — even after the employee has left.",
  "formal", "standard"),

p("b006_paye_for_020",
  "Je, mfanyakazi mgeni anaondoka Tanzania kabla ya mwisho wa mwaka — jinsi ya kushughulikia PAYE yake?",
  "Wakati mfanyakazi mgeni anaondoka Tanzania kabla ya mwaka wa kodi kumalizika: (1) Hesabu PAYE ya mwaka nzima kulingana na muda wa kufanya kazi Tanzania; (2) Fanya marekebisho ya mwisho ya PAYE kwa mwezi wa mwisho; (3) Toa P9 form inayoonyesha kipindi kilichofaa; (4) Futa usajili wa mfanyakazi kwenye mfumo wa PAYE TRA. Thibitisha hatua za mwisho na TRA.",
  "A foreign employee leaves Tanzania before year end — how is their PAYE handled?",
  "When a foreign employee leaves Tanzania before the tax year ends: (1) Calculate PAYE based on the period worked in Tanzania; (2) Make a final PAYE adjustment in the last month; (3) Issue a P9 form covering the applicable period; (4) Remove the employee from the TRA PAYE system. Confirm final steps with TRA.",
  "formal", "standard"),

# --- Group 5: Tax equalization and gross-up ---

p("b006_paye_for_021",
  "Tax equalization (usawa wa kodi) ni nini kwa mfanyakazi mgeni?",
  "Tax equalization ni utaratibu ambapo mwajiri anabeba PAYE badala ya mfanyakazi mgeni — ili kuhakikisha mfanyakazi hapotezi mshahara wake wa net kwa sababu ya kodi Tanzania. Mwajiri 'ana-gross up' mshahara kwa kiasi cha kodi inayolazimika. Hii inamaanisha mwajiri analipa kodi ya TRA kwa niaba ya mfanyakazi. Thamani ya kodi hii inakuwa manufaa ya ziada yanayolazimika PAYE pia.",
  "What is tax equalization for a foreign employee?",
  "Tax equalization is an arrangement where the employer bears the PAYE instead of the foreign employee — to ensure the employee does not lose their net salary due to Tanzania taxes. The employer 'grosses up' the salary by the applicable tax amount. This means the employer pays TRA on behalf of the employee. The value of this tax payment becomes an additional taxable benefit itself.",
  "formal", "standard"),

p("b006_paye_for_022",
  "Mwajiri analipa PAYE kwa niaba ya mfanyakazi mgeni — je, thamani ya kodi hiyo pia inabeba PAYE?",
  "Ndiyo. Wakati mwajiri analipa PAYE kwa niaba ya mfanyakazi (tax equalization au tax gross-up), thamani ya PAYE hiyo inakuwa manufaa ya ziada ya ajira — ambayo yenyewe pia inabeba PAYE. Hii inasababisha athari ya 'PAYE juu ya PAYE' (cascading tax). Mahesabu ya tax equalization ni ngumu na mara nyingi yanahitaji mshauri wa kodi.",
  "An employer pays PAYE on behalf of a foreign employee — does the value of that tax also carry PAYE?",
  "Yes. When the employer pays PAYE on behalf of the employee (tax equalization or tax gross-up), the value of that PAYE becomes an additional employment benefit — which itself also carries PAYE. This creates a 'PAYE on PAYE' cascading effect. Tax equalization calculations are complex and often require a tax advisor.",
  "formal", "standard"),

p("b006_paye_for_023",
  "Jinsi ya kuhesabu gross-up ya PAYE — mfano rahisi.",
  "Mfano rahisi: Mfanyakazi anahitaji net TZS 1,000,000 baada ya PAYE ya 25%. Gross-up = Net ÷ (1 - kiwango cha kodi) = TZS 1,000,000 ÷ 0.75 = TZS 1,333,333 gross. PAYE = TZS 1,333,333 × 25% = TZS 333,333. Net = TZS 1,333,333 - TZS 333,333 = TZS 1,000,000. Kwa viwango vya Tanzania vya juu, mahesabu yanakuwa ngumu zaidi kwa sababu ya viwango vya kujiendelea (progressive bands). Tumia mshauri wa kodi.",
  "How to calculate PAYE gross-up — a simple example.",
  "Simple example: Employee needs net TZS 1,000,000 after 25% PAYE. Gross-up = Net ÷ (1 - tax rate) = TZS 1,000,000 ÷ 0.75 = TZS 1,333,333 gross. PAYE = TZS 1,333,333 × 25% = TZS 333,333. Net = TZS 1,333,333 - TZS 333,333 = TZS 1,000,000. For Tanzania's higher progressive bands, calculations become more complex. Use a tax advisor.",
  "formal", "standard"),

# --- Group 6: Double Taxation Treaties (DTA) ---

p("b006_paye_for_024",
  "Tanzania ina mikataba ya kuzuia kodi mara mbili (DTA) na nchi zipi?",
  "Sina uhakika wa orodha kamili ya sasa ya mikataba ya DTA ya Tanzania. Kwa ujumla, Tanzania ina mikataba na nchi kadhaa — lakini orodha na masharti yao yanabadilika. Thibitisha orodha ya sasa ya mikataba ya DTA ya Tanzania na TRA au mshauri wa kodi wa kimataifa.",
  "Which countries does Tanzania have Double Taxation Agreements (DTAs) with?",
  "I am not certain of the current complete list of Tanzania's DTA agreements. Generally, Tanzania has agreements with several countries — but the list and their terms change over time. Verify the current list of Tanzania's DTAs with TRA or an international tax advisor.",
  "formal", "out_of_corpus_refusal"),

p("b006_paye_for_025",
  "DTA (mkataba wa kuzuia kodi mara mbili) — inasaidiana jinsi gani na PAYE Tanzania?",
  "DTA inaweza kuruhusu mfanyakazi mgeni kupata marekebisho au msamaha wa PAYE Tanzania ikiwa wanalipa kodi sawa katika nchi yao ya asili. Hata hivyo, mwajiri lazima bado ake PAYE ya kawaida Tanzania isipokuwa pale ambapo exemption rasmi ya DTA imeombiwa na kukubaliwa na TRA. Omba exemption ya DTA kabla ya kuanza kutoa marekebisho.",
  "DTA (Double Taxation Agreement) — how does it interact with Tanzania PAYE?",
  "A DTA can allow a foreign employee to receive PAYE relief or exemption in Tanzania if they are paying equivalent taxes in their home country. However, the employer must still deduct standard PAYE unless a formal DTA exemption has been applied for and approved by TRA. Apply for DTA exemption before granting any relief.",
  "formal", "standard"),

p("b006_paye_for_026",
  "Mfanyakazi mgeni anasema wanalipa kodi UK — wanaweza kuepuka PAYE Tanzania?",
  "Si kiotomatikilai. Hata kama mfanyakazi analipa kodi UK, PAYE Tanzania bado inatumika kwa mshahara unaotokana na kazi Tanzania isipokuwa wanapata ruhusa maalum kupitia DTA ya Tanzania-UK na TRA inakubali exemption rasmi. Omba rasmi — usitegemea tu madai ya mfanyakazi bila uthibitisho wa TRA.",
  "A foreign employee says they pay taxes in the UK — can they avoid Tanzania PAYE?",
  "Not automatically. Even if an employee pays UK taxes, Tanzania PAYE still applies to income from work in Tanzania unless they obtain specific relief through the Tanzania-UK DTA and TRA formally approves the exemption. Apply formally — do not simply rely on employee claims without TRA confirmation.",
  "formal", "adversarial"),

p("b006_paye_for_027",
  "Mfanyakazi mgeni anayeomba DTA relief — mchakato wake ni upi?",
  "Kwa ujumla, mchakato ni: (1) Mfanyakazi anathibitisha hali yake ya mkazi wa kodi katika nchi ya asili na haki za DTA; (2) Wasilisha ombi kwa Kamishna wa TRA ukiambatisha ushahidi wa kodi inayolipwa nje; (3) Subiri kibali rasmi cha TRA kabla ya kutoa marekebisho yoyote ya PAYE; (4) Hifadhi uthibitishaji wote. Mchakato maalum unategemea DTA inayohusika.",
  "A foreign employee applying for DTA relief — what is the process?",
  "Generally, the process is: (1) The employee confirms their tax residency in the home country and DTA entitlements; (2) Submit an application to the TRA Commissioner with evidence of taxes paid abroad; (3) Wait for formal TRA approval before making any PAYE adjustments; (4) Maintain all documentation. The specific process depends on the applicable DTA.",
  "formal", "out_of_corpus_refusal"),

# --- Group 7: Short-term assignments and secondments ---

p("b006_paye_for_028",
  "Mfanyakazi aliyepelekwa Tanzania kwa miezi 3 (secondment) — PAYE inatumika?",
  "Kwa secondment ya miezi 3, PAYE Tanzania itatumika kwa mapato yote ya ajira Tanzania katika kipindi hicho. Mwajiri (Tanzania au nje) analazimika kukata PAYE ya mshahara wowote unaolipwa kwa kazi inayofanywa Tanzania. Kipindi kifupi cha kazi hakimtoi mfanyakazi kutoka PAYE.",
  "An employee sent to Tanzania on a 3-month secondment — does PAYE apply?",
  "For a 3-month secondment, Tanzania PAYE applies to all employment income earned in Tanzania during that period. The employer (Tanzania or foreign) must deduct PAYE from any salary paid for work performed in Tanzania. A short work period does not exempt the employee from PAYE.",
  "formal", "standard"),

p("b006_paye_for_029",
  "Mwajiri wa nje ya nchi anayetuma mfanyakazi Tanzania — analazimika kujisajili TRA kwa PAYE?",
  "Hili ni swali ngumu la kisheria. Kama mwajiri wa nje hana uhalali wa kibiashara Tanzania (PE - Permanent Establishment), anaweza asihitajike kujisajili TRA. Hata hivyo, kama mwajiri ana uwepo Tanzania, usajili wa PAYE unaweza kutumika. Thibitisha hali yako maalum na TRA au mshauri wa kodi wa kimataifa.",
  "A foreign employer sending employees to Tanzania — do they need to register with TRA for PAYE?",
  "This is a complex legal question. If the foreign employer has no Tanzanian business presence (PE - Permanent Establishment), they may not need to register with TRA. However, if the employer has a presence in Tanzania, PAYE registration may apply. Confirm your specific situation with TRA or an international tax advisor.",
  "formal", "out_of_corpus_refusal"),

p("b006_paye_for_030",
  "Je, PAYE inategemea ni wapi kazi inafanywa au ni wapi mshahara unalipwa?",
  "PAYE Tanzania inategemea MAHALI PA KAZI — si mahali pa malipo ya mshahara. Kama mtu anafanya kazi Tanzania, PAYE Tanzania inatumika hata kama mshahara unalipwa Hong Kong, London, au mahali pengine. Mahali pa malipo ya mshahara si kigezo cha msingi — mahali pa kazi ndio msingi.",
  "Does PAYE depend on where work is performed or where salary is paid?",
  "Tanzania PAYE depends on WHERE WORK IS PERFORMED — not where the salary is paid. If a person works in Tanzania, Tanzania PAYE applies even if salary is paid in Hong Kong, London, or elsewhere. The place of salary payment is not the primary criterion — the place of work is the basis.",
  "formal", "adversarial"),

# --- Group 8: NSSF and other obligations for foreign employees ---

p("b006_paye_for_031",
  "Mfanyakazi mgeni Tanzania — analazimika pia kuchangia NSSF?",
  "Ndiyo. NSSF inachangiwa na wafanyakazi WOTE wanaofanya kazi Tanzania — wakiwemo wageni wenye vibali vya kazi halali. Mwajiri analipa 10% na mfanyakazi anachangia 10% (jumla 20%) ya mshahara wa msingi. Hata hivyo, wafanyakazi wa muda mfupi au wa secondment wanaweza kuwa na hali maalum — thibitisha na NSSF.",
  "A foreign employee in Tanzania — must they also contribute to NSSF?",
  "Yes. NSSF contributions are made by ALL employees working in Tanzania — including foreigners with valid work permits. The employer pays 10% and the employee contributes 10% (20% combined) of basic salary. However, short-term or secondment employees may have special status — verify with NSSF.",
  "formal", "standard"),

p("b006_paye_for_032",
  "Je, mfanyakazi mgeni anayeondoka Tanzania atapata pensheni yake ya NSSF?",
  "Kwa ujumla, mchangiaji wa NSSF ana haki ya manufaa baada ya kufikia miaka ya kustaafu na masharti ya muda wa michango. Hata hivyo, wageni wanaohama wanaweza kuwa na matatizo ya kupata manufaa kama hawakufikia miaka ya kustaafu Tanzania. Thibitisha hali yako maalum na NSSF kuhusu uhamisho wa manufaa au payout ya awali.",
  "A foreign employee leaving Tanzania — will they receive their NSSF pension?",
  "Generally, an NSSF contributor has benefit rights after reaching retirement age and meeting contribution period requirements. However, departing foreigners may face challenges in accessing benefits if they have not reached retirement age in Tanzania. Confirm your specific situation with NSSF about benefit transfer or early payout options.",
  "formal", "out_of_corpus_refusal"),

p("b006_paye_for_033",
  "Mwajiri wa Tanzania na mfanyakazi mgeni — wajibu wote wa kodi ni nini kwa muhtasari?",
  "Wajibu wa mwajiri kwa mfanyakazi mgeni: (1) PAYE — kata na wasilisha tarehe 7 (viwango vya kawaida); (2) NSSF — 10% mwajiri + 10% mfanyakazi; (3) SDL — 3.5% ya gross payroll (kama wafanyakazi ≥10); (4) WCF — 0.5% ya gross payroll (kwa ajali za kazi); (5) P9 — toa kabla ya 31 Machi. Sheria zinazotumika ni sawa na kwa wafanyakazi wa ndani Tanzania.",
  "A Tanzanian employer with a foreign employee — summary of all tax obligations?",
  "Employer obligations for a foreign employee: (1) PAYE — deduct and remit by 7th (standard rates); (2) NSSF — 10% employer + 10% employee; (3) SDL — 3.5% of gross payroll (if ≥10 employees); (4) WCF — 0.5% of gross payroll (for work accidents); (5) P9 — issue before 31 March. The applicable laws are the same as for local Tanzanian employees.",
  "formal", "standard"),

# --- Group 9: Disambiguation ---

p("b006_paye_for_034",
  "PAYE na withholding tax (WHT) kwa wasomi wa nje — ni nini tofauti?",
  "PAYE: kodi ya mapato ya ajira inayokatwa na MWAJIRI kwa MFANYAKAZI aliyehiriwa (employed person). WHT ya nje: kodi inayokatwa kwenye malipo ya huduma (consulting fees, management fees, royalties) kwa MKANDARASI asiyehiriwa au mtu wa nje ya nchi. PAYE = ajira; WHT = huduma/bidhaa kutoka nje. Ni mifumo miwili tofauti.",
  "PAYE and withholding tax (WHT) for foreign professionals — what is the difference?",
  "PAYE: income tax on employment earnings deducted by the EMPLOYER from a HIRED EMPLOYEE (employed person). WHT on foreigners: tax deducted on payments for services (consulting fees, management fees, royalties) to an INDEPENDENT CONTRACTOR or non-resident. PAYE = employment; WHT = services/goods from abroad. They are two separate frameworks.",
  "formal", "disambiguation"),

p("b006_paye_for_035",
  "Mshauri mgeni anakuja Tanzania kwa wiki moja kulipa mafunzo — PAYE au WHT?",
  "Inategemea muundo wa uhusiano. Kama mshauri ana mkataba wa ajira na kampuni ya Tanzania (mwajiriwa) — PAYE. Kama mshauri ni mkandarasi huru anayetoa invoice kwa huduma — WHT kwenye malipo ya huduma (6% kuanzia 1 Jul 2025). Muundo wa kisheria wa uhusiano wako ndio unaobainisha kiwango. Thibitisha na mshauri wa kodi.",
  "A foreign consultant comes to Tanzania for a week to deliver training — PAYE or WHT?",
  "It depends on the relationship structure. If the consultant has an employment contract with a Tanzanian company (employee) — PAYE. If the consultant is an independent contractor invoicing for services — WHT on service payments (6% from 1 Jul 2025). The legal structure of your relationship determines which applies. Verify with a tax advisor.",
  "formal", "disambiguation"),

p("b006_paye_for_036",
  "Mkurugenzi mgeni wa kampuni ya Tanzania (non-full time director) — PAYE au WHT?",
  "Mkurugenzi asiye na wakati wote (non-full-time director) anayepokea ada ya mkurugenzi (director fees) — WHT ya 15% inatumika (si PAYE). Hii inatumika kwa wakurugenzi wa ndani NA wa nje ya nchi. Mkurugenzi mwenye wakati wote (full-time) anayepokea mshahara — PAYE inatumika. Angalia muundo wa malipo.",
  "A foreign company director in Tanzania (non-full time director) — PAYE or WHT?",
  "A non-full-time director receiving director fees — 15% WHT applies (not PAYE). This applies to both resident and non-resident directors. A full-time director receiving a salary — PAYE applies. Check the payment structure.",
  "formal", "standard"),

p("b006_paye_for_037",
  "Je, mfanyakazi mgeni anaweza kudai kujitegemea (self-employed) ili kuepuka PAYE?",
  "TRA inachunguza hali halisi ya kazi — si tu jinsi inavyoitwa. Kama mtu anafanya kazi kama mwajiriwa (anahudhuria kila siku, anapokea maelekezo ya kazi, anatumia vifaa vya mwajiri), PAYE inatumika bila kujali kama anaitwa 'consultant' au 'self-employed'. Mgawanyo wa mwajiriwa/mkandarasi haufanyi kazi kwa lengo la kuepuka PAYE.",
  "Can a foreign employee claim to be self-employed to avoid PAYE?",
  "TRA examines the actual nature of the work — not just what it is called. If a person works like an employee (attends daily, receives work instructions, uses employer's equipment), PAYE applies regardless of whether they are called a 'consultant' or 'self-employed'. An employee/contractor classification does not work to avoid PAYE.",
  "formal", "adversarial"),

# --- Group 10: Final summary pairs ---

p("b006_paye_for_038",
  "Mfanyakazi mgeni ambaye amesajiliwa NSSF, analipa PAYE, na ana TIN — ana hali nzuri?",
  "Ndiyo — mfanyakazi mwenye TIN, PAYE inayokatwa kwa usahihi, na NSSF inayochangiwa — ana hali nzuri ya kodi Tanzania. Hii ni muundo sahihi wa kufuata. Mwajiri pia anahitaji SDL (kama wafanyakazi ≥10) na WCF (0.5%) zilizolipwa. Hifadhi kumbukumbu zote za P9 na malipo kwa ajili ya ukaguzi wowote wa TRA.",
  "A foreign employee registered with NSSF, paying PAYE, with a TIN — are they in good standing?",
  "Yes — an employee with a TIN, correctly deducted PAYE, and NSSF contributions — is in good Tanzania tax standing. This is the correct compliance structure. The employer also needs SDL (if ≥10 employees) and WCF (0.5%) paid. Keep all P9 records and payment receipts for any TRA audit.",
  "business_market", "standard"),

p("b006_paye_for_039",
  "Je, TIN ya kampuni inaweza kutumika badala ya TIN ya mfanyakazi kwa PAYE?",
  "Hapana. PAYE inahitaji TIN ya mfanyakazi binafsi — si TIN ya kampuni. Mfanyakazi (mgeni au raia) lazima awe na TIN yake mwenyewe. Mwajiri anawasilisha PAYE kwa TIN ya kampuni lakini PAYE inaruhusiwa kwa TIN ya mfanyakazi maalum. Zinaweza kuhitajika TIN zote mbili.",
  "Can a company TIN be used instead of an employee TIN for PAYE?",
  "No. PAYE requires the individual employee's TIN — not the company TIN. An employee (foreign or citizen) must have their own TIN. The employer remits PAYE using the company TIN but PAYE is attributed to the specific employee's TIN. Both TINs may be required.",
  "formal", "standard"),

p("b006_paye_for_040",
  "Mwajiri ameacha kulipa PAYE ya mfanyakazi mgeni — mfanyakazi huyo ana hatari gani?",
  "Mfanyakazi anaweza kukabiliwa na deni la kodi la kibinafsi kwa PAYE isiyolipwa hata kama mwajiri ndiye aliyekosea. Unashauriwa: (1) Wasiliana na TRA kuripoti tatizo; (2) Hifadhi ushahidi wa mshahara wako na makato yoyote (payslips); (3) Omba msaada wa kisheria kama inabidi. Usitegemea kwamba TRA itamchukulia mwajiri tu.",
  "An employer has stopped paying PAYE for a foreign employee — what risk does the employee face?",
  "The employee may face a personal tax liability for unpaid PAYE even if it was the employer's fault. You are advised to: (1) Contact TRA to report the issue; (2) Keep evidence of your salary and any deductions (payslips); (3) Seek legal help if needed. Do not assume TRA will only pursue the employer.",
  "business_market", "standard"),

p("b006_paye_for_041",
  "Je, mfanyakazi mgeni anaweza kuwasilisha kodi binafsi (personal income tax return) Tanzania?",
  "Ndiyo. Kama mtu anapokea mapato nje ya ajira (kama mapato ya kukodisha nyumba, mapato ya biashara, au mapato mengine ya Tanzania), inaweza kuhitajika kuwasilisha kodi ya mapato binafsi. Hata hivyo, kwa mfanyakazi wa kawaida ambaye PAYE yake yote imetolewa vizuri na mwajiri, kuwasilisha kodi ya binafsi si lazima daima. Thibitisha na TRA.",
  "Can a foreign employee file a personal income tax return in Tanzania?",
  "Yes. If a person receives income outside employment (such as rental income, business income, or other Tanzania-sourced income), they may need to file a personal income tax return. However, for a regular employee whose PAYE has been fully and correctly deducted by the employer, filing a personal return may not always be required. Verify with TRA.",
  "formal", "standard"),

p("b006_paye_for_042",
  "Mfanyakazi mgeni aliyekuwa Tanzania na sasa amerudi nyumbani — TRA inaweza kumpigia kodi baadaye?",
  "Kama PAYE ilipwa vizuri wakati wa kufanya kazi Tanzania, hawezi kupigiwa kodi tena kwa mapato yale. Hata hivyo, kama kuna PAYE iliyokosekana au ukiukaji wa kodi, TRA inaweza kutaka kulipa hata baada ya kuondoka. Hii inaweza kuathiri visa ya kurudi Tanzania au mali zinazobaki Tanzania. Thibitisha usafi wa kodi kabla ya kuondoka.",
  "A foreign employee who was in Tanzania and has now returned home — can TRA still tax them later?",
  "If PAYE was correctly paid during the period of work in Tanzania, they cannot be taxed again on that income. However, if there is unpaid PAYE or a tax violation, TRA may seek payment even after departure. This may affect future Tanzania visas or assets remaining in Tanzania. Verify clean tax status before departing.",
  "formal", "standard"),

p("b006_paye_for_043",
  "Mfanyakazi mgeni wa NGO/asasi ya kiraia — PAYE inatumika?",
  "Ndiyo. PAYE inatumika kwa wafanyakazi wa asasi za kiraia (NGO, asasi za jamii, mashirika ya kimataifa) wanaofanya kazi Tanzania — kama wana mshahara. Mwajiri (NGO au asasi) analazimika kukata na kuwasilisha PAYE. Baadhi ya asasi za kimataifa zenye hadhi maalum za UN au kidiplomasia zinaweza kuwa na msamaha — thibitisha na TRA.",
  "A foreign employee of an NGO/civil society organization — does PAYE apply?",
  "Yes. PAYE applies to employees of civil society organizations (NGOs, community organizations, international organizations) working in Tanzania — if they receive a salary. The employer (NGO or organization) must deduct and remit PAYE. Some international organizations with special UN or diplomatic status may have exemptions — verify with TRA.",
  "formal", "standard"),

p("b006_paye_for_044",
  "Ujumla: hatua muhimu 5 kwa mwajiri wa Tanzania aliye na mfanyakazi mgeni.",
  "Hatua 5 muhimu: (1) Omba TIN kwa mfanyakazi mapema; (2) Kata PAYE kwa viwango sahihi kuanzia mshahara wa kwanza; (3) Jumuisha manufaa yote (nyumba, gari, ada za shule) kwenye msingi wa PAYE; (4) Wasilisha PAYE return na malipo kabla ya tarehe 7 ya kila mwezi; (5) Toa P9 kabla ya 31 Machi. Fuata pia NSSF, SDL, na WCF kama inavyotumika.",
  "Summary: 5 key steps for a Tanzanian employer with a foreign employee.",
  "5 Key steps: (1) Apply for a TIN for the employee early; (2) Deduct PAYE at correct rates from the first salary; (3) Include all benefits (housing, car, school fees) in the PAYE base; (4) File PAYE returns and payments before the 7th of each month; (5) Issue P9 before 31 March. Also follow NSSF, SDL, and WCF as applicable.",
  "business_market", "standard"),

p("b006_paye_for_045",
  "Kwa nini ni muhimu kushughulikia PAYE ya mfanyakazi mgeni vizuri tangu mwanzo?",
  "Kushughulikia PAYE ya mfanyakazi mgeni vizuri kunamlinda mwajiri kutoka: adhabu za 2.5%/mwezi, ukaguzi wa TRA, madai ya nyuma ya PAYE, na tatizo za kisheria. Pia kunamlinda mfanyakazi mgeni kutoka deni la kodi la kibinafsi. Makosa yanayogunduliwa baadaye (hasa baada ya mfanyakazi kuondoka) ni ngumu na gharama zaidi kutatua.",
  "Why is it important to handle a foreign employee's PAYE correctly from the start?",
  "Handling a foreign employee's PAYE correctly from the start protects the employer from: 2.5%/month penalties, TRA audits, backdated PAYE claims, and legal problems. It also protects the foreign employee from personal tax liabilities. Errors discovered later (especially after the employee has left) are harder and more expensive to resolve.",
  "formal", "standard"),

p("b006_paye_for_046",
  "Mfanyakazi mgeni mwenye hisa za kampuni (share options) — thamani yao inalazimika PAYE?",
  "Kwa ujumla, manufaa ya hisa za kampuni (share options, restricted stock) zinazotolewa kwa wafanyakazi zinachukuliwa kama mapato ya ajira pale zinapoibuliwa au kupatikana — na zinabeba PAYE. Hata hivyo, matibabu maalum ya kodi ya stock options Tanzania ni ngumu na yanategemea muundo wa mpango wa hisa. Thibitisha na mshauri wa kodi.",
  "A foreign employee with company share options — is their value subject to PAYE?",
  "Generally, company share benefits (share options, restricted stock) given to employees are treated as employment income when exercised or vested — and they carry PAYE. However, the specific tax treatment of stock options in Tanzania is complex and depends on the share plan structure. Verify with a tax advisor.",
  "formal", "out_of_corpus_refusal"),

p("b006_paye_for_047",
  "Mfanyakazi mgeni aliyesha-resign — mwajiri anahitaji kulipa PAYE ya mwisho lini?",
  "PAYE ya mshahara wa mwisho (terminal benefits — mshahara wa mwisho, posho ya kuachana, likizo iliyobaki inayolipwa) inapaswa kukokotolewa, kukatwa, na kuwasilishwa TRA ifikapo tarehe 7 ya mwezi unaofuata baada ya malipo ya mwisho. Toa P9 kwa mfanyakazi baada ya malipo ya mwisho.",
  "A foreign employee has resigned — when must the employer pay the final PAYE?",
  "PAYE on the final salary (terminal benefits — last salary, severance, unused leave paid out) must be calculated, deducted, and remitted to TRA by the 7th of the month following the final payment. Issue a P9 to the employee after the final payment.",
  "formal", "standard"),

p("b006_paye_for_048",
  "Je, malipo ya ugawaji (redundancy pay) kwa mfanyakazi mgeni yanabeba PAYE?",
  "Ndiyo kwa ujumla. Malipo ya ugawaji (redundancy pay) yanachukuliwa kama mapato ya ajira na yanabeba PAYE Tanzania. Hata hivyo, sheria ya Tanzania inaweza kutoa matibabu maalum kwa malipo ya kutolipwa kazi (end-of-service lump sums). Thibitisha matibabu ya kodi ya malipo yako maalum na mshauri wa kodi.",
  "Does redundancy pay for a foreign employee carry PAYE?",
  "Generally yes. Redundancy payments are treated as employment income and carry Tanzania PAYE. However, Tanzanian law may provide special treatment for end-of-service lump sum payments. Verify the tax treatment of your specific payments with a tax advisor.",
  "formal", "standard"),

p("b006_paye_for_049",
  "Mfanyakazi mgeni aliyekasirika na sheria ya PAYE — wapi anaweza kupata msaada?",
  "Mfanyakazi mgeni mwenye malalamiko ya PAYE anaweza: (1) Wasiliana na idara ya HR/uhasibu ya mwajiri wake kwanza; (2) Wasiliana na TRA moja kwa moja kuuliza maswali au kuripoti tatizo; (3) Piga rufaa kwa Kamishna wa TRA kama tatizo halijatatuliwa; (4) Tafuta msaada wa TRAB (Tax Revenue Appeals Board) kwa malalamiko rasmi; (5) Tafuta ushauri wa mwanasheria au mshauri wa kodi.",
  "A foreign employee confused about PAYE law — where can they get help?",
  "A foreign employee with PAYE concerns can: (1) Contact their employer's HR/accounting department first; (2) Contact TRA directly to ask questions or report a problem; (3) Appeal to the TRA Commissioner if the issue is unresolved; (4) Seek TRAB (Tax Revenue Appeals Board) for formal complaints; (5) Seek advice from a lawyer or tax advisor.",
  "business_market", "standard"),

p("b006_paye_for_050",
  "Muhtasari: PAYE kwa mfanyakazi mgeni Tanzania — mambo 6 makuu.",
  "PAYE ya mfanyakazi mgeni Tanzania — mambo 6: (1) PAYE inatumika kwa wote — raia na wageni; (2) Viwango ni sawa (progressive bands, personal relief); (3) Manufaa yote (nyumba, gari, ada za shule) ni mapato yanayolazimika PAYE; (4) Mwajiri anakata na kuwasilisha tarehe 7 kila mwezi; (5) P9 inatakiwa kabla 31 Machi; (6) DTA inaweza kutoa msamaha — omba rasmi TRA kabla ya kutoa marekebisho. Kushindwa kufuata = adhabu ya 2.5%/mwezi.",
  "Summary: PAYE for a foreign employee in Tanzania — 6 key points.",
  "PAYE for foreign employees in Tanzania — 6 key points: (1) PAYE applies to all — citizens and foreigners; (2) Rates are the same (progressive bands, personal relief); (3) All benefits (housing, car, school fees) are PAYE-taxable income; (4) Employer deducts and remits by 7th each month; (5) P9 required before 31 March; (6) A DTA may provide relief — apply formally to TRA before making adjustments. Failure to comply = 2.5%/month penalty.",
  "formal", "standard"),

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
print("Register distribution:", dict(regs))
print("Pair type distribution:", dict(ptypes))
