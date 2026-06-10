#!/usr/bin/env python3
"""
batch_006 part 2: sdl_adversarial — 50 pairs
IDs: b006_sdl_001 – b006_sdl_050
Target: correct base-model errors (SDL = 'disability leave', wrong rate, wrong threshold, wrong payer)
Source: TRA SDL page (government_portal)
Append to: datasets/tier1a/raw_sources/raw_pairs_batch_006.jsonl
"""
import json, os

OUT = "datasets/tier1a/raw_sources/raw_pairs_batch_006.jsonl"
SRC = "https://www.tra.go.tz/page/skills-development-levy"
NAME = "TRA - Skills Development Levy"
REVIEW = "Finance Act amendment changing SDL rate or threshold"

def p(id_, q_sw, a_sw, q_en, a_en, register, pair_type):
    return {
        "id": id_,
        "domain": "tier1a",
        "subdomain": "sdl_adversarial",
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

# --- GROUP 1: SDL name — correcting "disability leave" base model error ---

p("b006_sdl_001",
  "SDL inamaanisha nini — ni Skills Development Levy au disability leave?",
  "SDL inamaanisha Skills Development Levy — Ushuru wa Maendeleo ya Ujuzi. Si disability leave (likizo ya ulemavu), si sick leave, si aina yoyote ya likizo. Ni ushuru wa serikali anaolipa mwajiri kwa Serikali kila mwezi ili kusaidia mafunzo ya ufundi nchini.",
  "What does SDL stand for — is it Skills Development Levy or disability leave?",
  "SDL stands for Skills Development Levy. It is NOT disability leave, sick leave, or any type of leave. It is a government levy paid monthly by the employer to fund vocational and skills training in Tanzania.",
  "formal", "adversarial"),

p("b006_sdl_002",
  "Mwajiri anasema SDL ni 'Sikuwa Leave Disability' — ni kweli?",
  "Uongo kabisa. SDL haina uhusiano wowote na likizo (leave) au ulemavu (disability). SDL ni Skills Development Levy — ushuru wa fedha ambao mwajiri (si mwajiriwa) analipa TRA kila mwezi. Inahesabiwa kama asilimia ya jumla ya mishahara.",
  "My employer says SDL is 'Sick Leave Disability' — is that true?",
  "Completely false. SDL has no connection to leave or disability. SDL is Skills Development Levy — a monetary levy that the employer (not the employee) pays to TRA every month. It is calculated as a percentage of total gross payroll.",
  "business_market", "adversarial"),

p("b006_sdl_003",
  "Nini lengo la SDL — ni malipo ya likizo ya ugonjwa au mafunzo ya kazi?",
  "Lengo la SDL ni kufadhili mafunzo ya ufundi na ujuzi wa kazi (vocational training) nchini Tanzania — si malipo ya likizo. SDL ilanzishwa ili kusaidia VETA (Vocational Education and Training Authority) na mifumo ya mafunzo ya kitaalamu. Mwajiri ndiye analipa, mfanyakazi hapunguziwa kitu.",
  "What is the purpose of SDL — is it sick leave payments or job training?",
  "The purpose of SDL is to fund vocational and job skills training in Tanzania — not leave payments. SDL was established to support VETA (Vocational Education and Training Authority) and professional training systems. The employer pays it; nothing is deducted from the employee.",
  "formal", "standard"),

p("b006_sdl_004",
  "Je, SDL inahusu likizo yoyote — likizo ya ulemavu, ugonjwa, au uzazi?",
  "Hapana kabisa. SDL haihusu aina yoyote ya likizo — wala ulemavu, wala ugonjwa, wala uzazi. Skills Development Levy inahusiana na ushuru tu, si haki za likizo. Haki za likizo (ugonjwa, uzazi, ulemavu) zinasimamia na ELRA (Employment and Labour Relations Act) — si SDL.",
  "Does SDL relate to any type of leave — disability leave, sick leave, or maternity leave?",
  "Absolutely not. SDL has nothing to do with any type of leave — disability, sick, or maternity. Skills Development Levy is purely a tax levy, not an employment leave entitlement. Leave rights are governed by ELRA (Employment and Labour Relations Act) — not SDL.",
  "formal", "adversarial"),

p("b006_sdl_005",
  "Mfanyakazi wangu ana ulemavu — anapaswa kulipwa SDL?",
  "Swali hili linachanganya mambo mawili tofauti. SDL si malipo ya wafanyakazi wenye ulemavu — ni ushuru wa mwajiri. Mwajiri analipa SDL kwa TRA kwa kiwango cha 3.5% ya mishahara yote, bila kujali hali ya kiafya ya wafanyakazi. Mfanyakazi mwenye ulemavu ana haki zake tofauti chini ya ELRA na WCF, lakini hizo hazihusiani na SDL.",
  "My employee has a disability — should they be paid SDL?",
  "This question confuses two different things. SDL is not a payment to disabled employees — it is an employer levy. The employer pays SDL to TRA at 3.5% of total gross payroll, regardless of employees' health status. An employee with a disability has separate rights under ELRA and WCF, but those are unrelated to SDL.",
  "business_market", "disambiguation"),

# --- GROUP 2: SDL rate (correcting wrong percentages) ---

p("b006_sdl_006",
  "Kiwango cha SDL ni 2% au 3.5% ya mishahara?",
  "Kiwango cha SDL ni 3.5% ya jumla ya mishahara (gross payroll) — si 2%. Mwajiri analipa TZS 3,500 kwa kila TZS 100,000 za mishahara inayolipwa. Kiwango hiki kinatumika kwa wajiri wote wenye wafanyakazi 10 au zaidi.",
  "Is the SDL rate 2% or 3.5% of payroll?",
  "The SDL rate is 3.5% of total gross payroll — not 2%. The employer pays TZS 3,500 for every TZS 100,000 of payroll. This rate applies to all employers with 10 or more employees.",
  "business_market", "adversarial"),

p("b006_sdl_007",
  "Mtu anasema SDL ni 4% ya mishahara — ni sahihi?",
  "Hapana. Kiwango cha SDL ni 3.5% — si 4%. Angalau hadi Sheria ya Fedha inayofuata kuibadilisha, mwajiri analipa asilimia tatu nukta tano (3.5%) ya jumla ya mishahara ya wafanyakazi wake.",
  "Someone says SDL is 4% of payroll — is this correct?",
  "No. The SDL rate is 3.5% — not 4%. At least until the next Finance Act changes it, the employer pays three point five percent (3.5%) of total employee payroll.",
  "business_market", "adversarial"),

p("b006_sdl_008",
  "SDL ya kampuni yenye mishahara ya TZS 5,000,000 kwa mwezi ni kiasi gani?",
  "SDL = 3.5% × TZS 5,000,000 = TZS 175,000 kwa mwezi. Mwajiri analipa TZS 175,000 kwa TRA ifikapo tarehe 7 ya mwezi unaofuata. Kiwango cha 3.5% kinatumiwa kwa jumla ya mishahara yote (gross payroll).",
  "SDL for a company with TZS 5,000,000 monthly payroll is how much?",
  "SDL = 3.5% × TZS 5,000,000 = TZS 175,000 per month. The employer pays TZS 175,000 to TRA by the 7th of the following month. The 3.5% rate is applied to total gross payroll.",
  "business_market", "standard"),

p("b006_sdl_009",
  "Je, SDL ya 5% ipo kwenye sheria ya Tanzania?",
  "Hapana. Kiwango cha SDL ni 3.5% — hakuna SDL ya 5% katika sheria ya Tanzania. Ikiwa mtu au mfumo unakuambia SDL ni 5%, hiyo ni kosa. Thibitisha na TRA au angalia Sheria ya Fedha ya hivi karibuni.",
  "Is there a 5% SDL in Tanzanian law?",
  "No. The SDL rate is 3.5% — there is no 5% SDL in Tanzanian law. If anyone or any system tells you SDL is 5%, that is an error. Verify with TRA or check the latest Finance Act.",
  "formal", "adversarial"),

p("b006_sdl_010",
  "SDL inahesabiwa juu ya mishahara halisi (net) au mishahara kabla ya kodi (gross)?",
  "SDL inahesabiwa juu ya mishahara ya jumla (gross payroll) — si mishahara ya net (baada ya PAYE). Hii inamaanisha unajumuisha mshahara wote kabla ya kukata kodi au michango mingine.",
  "Is SDL calculated on net salaries or gross salaries (before tax)?",
  "SDL is calculated on gross payroll — not net salaries (after PAYE). This means you include total salaries before any tax deductions or other contributions.",
  "formal", "standard"),

# --- GROUP 3: SDL threshold (correcting wrong employee count) ---

p("b006_sdl_011",
  "SDL inahitajika kuanzia wafanyakazi wangapi — 5 au 10?",
  "SDL inahitajika kuanzia wafanyakazi 10 au zaidi — si 5. Mwajiri mwenye wafanyakazi 9 au chini yake hajalazimishwa kulipa SDL. Ukifika wafanyakazi 10, SDL inakuwa lazima tangu mwezi huo huo.",
  "SDL is required from how many employees — 5 or 10?",
  "SDL is required from 10 or more employees — not 5. An employer with 9 or fewer employees is not required to pay SDL. Once you reach 10 employees, SDL becomes mandatory from that same month.",
  "business_market", "adversarial"),

p("b006_sdl_012",
  "Biashara yangu ina wafanyakazi 8 — je, nalipa SDL?",
  "Hapana. Kizingiti cha SDL ni wafanyakazi 10 au zaidi. Kwa biashara yenye wafanyakazi 8, SDL haihitajiki kwa sasa. Ikiwa utafikia wafanyakazi 10 au zaidi wakati wowote, SDL itakuwa lazima kuanzia mwezi huo.",
  "My business has 8 employees — do I pay SDL?",
  "No. The SDL threshold is 10 or more employees. For a business with 8 employees, SDL is not currently required. If and when you reach 10 or more employees, SDL becomes mandatory from that month.",
  "business_market", "standard"),

p("b006_sdl_013",
  "Kampuni ina wafanyakazi 10 — inalipa SDL. Je, ikiwa idadi ya wafanyakazi inashuka chini ya 10?",
  "Kama idadi ya wafanyakazi inashuka chini ya 10 kwa kudumu, wajibu wa SDL unaweza kutoweka. Hata hivyo, thibitisha na TRA kuhusu utaratibu wa kujiondoa rasmi. Kupungua kwa muda mfupi (kwa mwezi mmoja) kunaweza kusababisha tofauti — thibitisha.",
  "A company has 10 employees — it pays SDL. What if the employee count drops below 10?",
  "If the employee count permanently drops below 10, the SDL obligation may cease. However, verify with TRA on the formal deregistration process. A temporary drop (for one month) may have different treatment — verify.",
  "formal", "disambiguation"),

p("b006_sdl_014",
  "Mwajiri ana wafanyakazi 10 wa kudumu na 3 wa muda — SDL inahesabiwa kwa wote?",
  "SDL inahesabiwa kwa wafanyakazi WOTE wanaolipwa mshahara — wakudumu NA wa muda. Kizingiti cha '10 wafanyakazi' kinategemea jumla ya wafanyakazi wote, si wakudumu peke yao. Mishahara ya wote inajumuishwa kwenye msingi wa SDL.",
  "An employer has 10 permanent employees and 3 temporary ones — is SDL calculated on all?",
  "SDL is calculated on ALL employees receiving a salary — permanent AND temporary. The threshold of '10 employees' is based on total headcount, not permanent employees alone. All their salaries are included in the SDL base.",
  "formal", "standard"),

p("b006_sdl_015",
  "Kizingiti cha SDL ni wafanyakazi 10 au ni kulingana na mapato ya biashara?",
  "Kizingiti cha SDL ni IDADI ya wafanyakazi — si mapato ya biashara. Hata biashara ndogo yenye mapato kidogo inalipa SDL ikiwa ina wafanyakazi 10 au zaidi. Na biashara kubwa yenye wafanyakazi 9 tu hailazimishwi kulipa SDL.",
  "Is the SDL threshold 10 employees or based on business revenue?",
  "The SDL threshold is based on NUMBER OF EMPLOYEES — not business revenue. Even a small business with low revenue pays SDL if it has 10 or more employees. And a large business with only 9 employees is not required to pay SDL.",
  "formal", "adversarial"),

# --- GROUP 4: SDL payer — employer vs employee ---

p("b006_sdl_016",
  "SDL inakatwa kutoka kwa mfanyakazi au mwajiri ndiye analipa?",
  "Mwajiri ndiye analipa SDL — hakatiwi kutoka kwa mfanyakazi. Hii ni tofauti muhimu na PAYE (ambayo inakatwa kutoka kwa mshahara wa mfanyakazi). SDL ni gharama ya mwajiri peke yake, inayolipwa TRA kama ushuru tofauti.",
  "Is SDL deducted from the employee or does the employer pay it?",
  "The employer pays SDL — it is NOT deducted from the employee's salary. This is an important difference from PAYE (which is deducted from the employee's pay). SDL is entirely the employer's cost, paid to TRA as a separate levy.",
  "business_market", "adversarial"),

p("b006_sdl_017",
  "Mfanyakazi wangu ameuliza kwa nini SDL imekatwa kwenye payslip yake — ni sahihi kuikata?",
  "Hapana — si sahihi kuikata SDL kutoka kwa mfanyakazi. SDL ni ushuru wa mwajiri, si mfanyakazi. Ikiwa SDL imekatwa kwenye payslip ya mfanyakazi, hiyo ni kosa. Mwajiri anapaswa kuirudisha fedha kwa mfanyakazi na kulipa SDL mwenyewe.",
  "My employee asked why SDL was deducted from their payslip — is it correct to deduct it?",
  "No — it is not correct to deduct SDL from the employee. SDL is the employer's levy, not the employee's. If SDL appears as a deduction on an employee's payslip, that is an error. The employer should refund the amount to the employee and pay SDL themselves.",
  "business_market", "adversarial"),

p("b006_sdl_018",
  "Je, SDL na NSSF ni tofauti gani katika suala la ni nani analipa?",
  "NSSF: mwajiri hulipa 10% NA mfanyakazi huchangia 10% — jumla 20% ya mshahara (kila mmoja 10%). SDL: mwajiri hulipa 3.5% peke yake — mfanyakazi hachangii chochote. Ni tofauti muhimu: NSSF ni mchango wa pamoja, SDL ni ushuru wa mwajiri tu.",
  "What is the difference between SDL and NSSF in terms of who pays?",
  "NSSF: the employer pays 10% AND the employee contributes 10% — a combined 20% of salary (10% each). SDL: the employer alone pays 3.5% — the employee contributes nothing. The key difference: NSSF is a joint contribution, SDL is an employer-only levy.",
  "business_market", "disambiguation"),

p("b006_sdl_019",
  "SDL na PAYE — ni tofauti gani?",
  "PAYE (Pay As You Earn): kodi ya mapato inayokatwa kutoka kwa MFANYAKAZI na kulipwa TRA na mwajiri kwa niaba yake. SDL (Skills Development Levy): ushuru wa 3.5% anaolipa MWAJIRI mwenyewe, si mfanyakazi. PAYE ni kodi ya mfanyakazi; SDL ni ushuru wa mwajiri.",
  "SDL and PAYE — what is the difference?",
  "PAYE (Pay As You Earn): income tax deducted from the EMPLOYEE and remitted to TRA by the employer on their behalf. SDL (Skills Development Levy): a 3.5% levy paid by the EMPLOYER themselves, not the employee. PAYE is the employee's tax; SDL is the employer's levy.",
  "formal", "disambiguation"),

p("b006_sdl_020",
  "Je, SDL inaweza kulipwa kama sehemu ya mshahara wa mfanyakazi bila ya kumjulisha?",
  "Hapana. SDL ni ushuru wa mwajiri unaolipwa TRA — si sehemu ya mshahara wa mfanyakazi. Kuiingiza kwenye mshahara wa mfanyakazi bila idhini ni kosa la kisheria. Mfanyakazi ana haki ya kupata mshahara wake kamili na mwajiri analipa SDL kando.",
  "Can SDL be paid as part of an employee's salary without informing them?",
  "No. SDL is an employer levy paid to TRA — it is not part of the employee's salary. Including it in the employee's payroll without consent is a legal error. The employee is entitled to their full salary and the employer pays SDL separately.",
  "formal", "adversarial"),

# --- GROUP 5: SDL deadlines and filing ---

p("b006_sdl_021",
  "SDL inalipwa lini kwa mwezi — tarehe 7 au 20?",
  "SDL inalipwa ifikapo tarehe 7 ya mwezi unaofuata — si tarehe 20. Tarehe ya 20 ni ya VAT return. SDL na PAYE zinalipwa kabla ya tarehe 7, na VAT kabla ya tarehe 20. Zisije zikachanganywa.",
  "When is SDL paid each month — by the 7th or the 20th?",
  "SDL is paid by the 7th of the following month — not the 20th. The 20th is the VAT return deadline. SDL and PAYE are paid before the 7th, and VAT before the 20th. Do not confuse them.",
  "business_market", "adversarial"),

p("b006_sdl_022",
  "SDL inalipwa pamoja na PAYE au tofauti?",
  "SDL na PAYE zote mbili zinalipwa ifikapo tarehe 7 ya mwezi unaofuata, lakini zinaweza kuwa na malipo tofauti au kwa fomu tofauti kupitia mfumo wa TRA. Kwa vitendo, mara nyingi zinalipwa pamoja kupitia mfumo wa TRA. Hakikisha kila moja inalipwa kwa mstari sahihi wa malipo.",
  "Is SDL paid together with PAYE or separately?",
  "Both SDL and PAYE are due by the 7th of the following month, but they may be separate payments or forms through the TRA system. In practice, they are often paid together through the TRA system. Ensure each is credited to the correct payment line.",
  "formal", "standard"),

p("b006_sdl_023",
  "Adhabu ya kutolipa SDL kwa wakati ni nini?",
  "Kutolipa SDL kwa wakati kunasababisha adhabu ya riba (penalty interest) kulingana na kanuni za TRA. Kama inavyotumika kwa mapato mengine, TRA inaweza kutoza faini ya marehemu zaidi ya gharama za riba. Lipa kabla ya tarehe 7 kuepuka gharama hizi.",
  "What is the penalty for not paying SDL on time?",
  "Failing to pay SDL on time incurs penalty interest charges according to TRA regulations. As with other taxes, TRA may impose late-payment fines on top of interest charges. Pay before the 7th to avoid these costs.",
  "formal", "standard"),

p("b006_sdl_024",
  "SDL register inamaanisha nini — kampuni inahitaji kusajiliwa tofauti na TRA?",
  "Mwajiri mwenye wafanyakazi 10 au zaidi anahitaji kusajiliwa kwa SDL na TRA. Kama kampuni imesajiliwa TIN (taxpayer identification number) tayari, mara nyingi usajili wa SDL unaongezwa hapo hapo. Thibitisha na TRA kuhusu utaratibu wa usajili wa SDL.",
  "What does SDL registration mean — does a company need to register separately with TRA?",
  "An employer with 10 or more employees must register for SDL with TRA. If the company already has a TIN (taxpayer identification number), SDL registration is often added to the same registration. Verify with TRA on the SDL registration process.",
  "formal", "standard"),

# --- GROUP 6: SDL scope — which payments are included ---

p("b006_sdl_025",
  "SDL inahesabiwa kwa mshahara mzima au mshahara wa msingi (basic salary) tu?",
  "SDL inahesabiwa kwa jumla ya mishahara ya gross — ikiwa ni pamoja na mshahara wa msingi, posho za kila aina (housing, transport, meal), na malipo mengine ya kawaida. Si mshahara wa msingi peke yake. Jumla ya payroll ndiyo msingi.",
  "Is SDL calculated on total salary or basic salary only?",
  "SDL is calculated on total gross payroll — including basic salary, all types of allowances (housing, transport, meals), and other regular payments. Not basic salary alone. The total payroll is the base.",
  "formal", "standard"),

p("b006_sdl_026",
  "Posho ya nyumba na posho ya usafiri — zinajumuishwa kwenye SDL?",
  "Ndiyo. Kwa ujumla, posho za mara kwa mara kama posho ya nyumba na usafiri zinajumuishwa kwenye jumla ya mishahara inayotumika kuhesabu SDL. Inahusisha malipo yote ya kawaida ya mwajiri kwa mwajiriwa. Thibitisha muundo maalum na mshauri wako wa kodi.",
  "Housing allowance and transport allowance — are they included in SDL?",
  "Yes. Generally, regular allowances such as housing and transport allowances are included in the total payroll used to calculate SDL. This covers all regular employer payments to employees. Confirm your specific structure with your tax advisor.",
  "formal", "standard"),

p("b006_sdl_027",
  "Bonasi ya mwisho wa mwaka — inajumuishwa kwenye msingi wa SDL?",
  "Ndiyo, kwa ujumla bonasi na malipo ya kipekee yanajumuishwa kwenye msingi wa SDL kwa mwezi yanalipwa. Ikiwa bonasi inalipwa Desemba, SDL inahesabiwa kwa jumla ya mishahara ya Desemba ikiwa ni pamoja na bonasi. Thibitisha muundo maalum na TRA au mshauri wa kodi.",
  "Year-end bonus — is it included in the SDL base?",
  "Yes, generally bonuses and one-time payments are included in the SDL base for the month they are paid. If a bonus is paid in December, SDL is calculated on the total December payroll including the bonus. Confirm specific structures with TRA or a tax advisor.",
  "formal", "standard"),

p("b006_sdl_028",
  "SDL inajumuisha malipo ya wafanyakazi wa muda mfupi (casual workers)?",
  "Ndiyo. Wafanyakazi wa muda mfupi (casual) ambao wanalipwa na mwajiri wanajumuishwa kwenye msingi wa SDL. Ikiwa unalipa mshahara kwa mtu, hata kama ni casual worker, mshahara huo unaingia kwenye jumla ya payroll ya SDL.",
  "Does SDL include payments to casual (short-term) workers?",
  "Yes. Casual workers who are paid by the employer are included in the SDL base. If you pay a salary to someone, even a casual worker, that salary enters the total SDL payroll calculation.",
  "formal", "standard"),

p("b006_sdl_029",
  "Mfanyakazi anayefanya kazi kwa misingi ya mkataba (contract) — mshahara wake unajumuishwa kwenye SDL?",
  "Inategemea hali ya mkataba. Mfanyakazi wa mkataba anayepewa mshahara wa kawaida na mwajiri wake (employee relationship) — mshahara wake unajumuishwa kwenye SDL. Mkandarasi anayejitegemea (self-employed contractor) anayetoa ankara — mara nyingi haingii kwenye SDL. Muundo sahihi wa kisheria ndio unaotoa jibu.",
  "A contract worker — is their salary included in SDL?",
  "It depends on the contract arrangement. A contract employee receiving regular salary from their employer (employee relationship) — their salary is included in SDL. An independent self-employed contractor who issues invoices — typically not included in SDL. The exact legal structure determines the answer.",
  "formal", "disambiguation"),

# --- GROUP 7: SDL and specific employer types ---

p("b006_sdl_030",
  "Kampuni ya EPZ (Export Processing Zone) inalipa SDL?",
  "Makampuni ya EPZ kawaida yana msamaha au vivutio maalum vya kodi ikiwemo SDL. Hata hivyo, masharti mahususi yanategemea mikataba ya TIC/EPZ ya kila kampuni. Thibitisha na TRA au TIC ili kujua hali halisi ya kampuni yako.",
  "Does an EPZ (Export Processing Zone) company pay SDL?",
  "EPZ companies typically have exemptions or special tax incentives that may include SDL. However, specific terms depend on each company's TIC/EPZ agreement. Verify with TRA or TIC to confirm your company's specific situation.",
  "formal", "disambiguation"),

p("b006_sdl_031",
  "Shirika lisilo la faida (NGO, asasi ya kiraia) inalipa SDL?",
  "NGO na asasi za kiraia zenye wafanyakazi 10 au zaidi wanaolipwa mshahara kwa kawaida zinalipa SDL. Kuwa si la faida hakutoi msamaha wa kiotomatikilai. Thibitisha na TRA hali ya usajili wa SDL wa shirika lako.",
  "Does a non-profit organization (NGO, civil society) pay SDL?",
  "NGOs and civil society organizations with 10 or more salaried employees generally pay SDL. Being non-profit does not automatically provide an exemption. Verify with TRA the SDL registration status of your organization.",
  "formal", "standard"),

p("b006_sdl_032",
  "Serikali ya Tanzania inalipa SDL kwa wafanyakazi wake?",
  "Idara za serikali kwa kawaida haziko chini ya SDL kama ilivyo kwa waajiri wa sekta binafsi. Hata hivyo, mashirika ya umma (parastatals) yanayofanya kazi kwa hali ya kampuni yanaweza kuwa na wajibu tofauti. Thibitisha na TRA hali halisi ya aina ya shirika lako.",
  "Does the Tanzanian government pay SDL for its employees?",
  "Government departments are typically not subject to SDL in the same way as private sector employers. However, public corporations (parastatals) operating in a corporate structure may have different obligations. Verify with TRA the exact situation for your type of organization.",
  "formal", "disambiguation"),

p("b006_sdl_033",
  "Mwajiri mgeni anayefanya kazi Tanzania — analipa SDL?",
  "Ndiyo. Mwajiri yeyote anayeendesha biashara Tanzania na kulipa mishahara kwa wafanyakazi Tanzania analipa SDL kama ana wafanyakazi 10 au zaidi. Uraia wa mwajiri (mgeni au raia) hauthiri wajibu wa SDL.",
  "A foreign employer operating in Tanzania — do they pay SDL?",
  "Yes. Any employer operating a business in Tanzania and paying salaries to Tanzania-based employees pays SDL if they have 10 or more employees. The citizenship of the employer (foreign or citizen) does not affect the SDL obligation.",
  "formal", "standard"),

# --- GROUP 8: SDL disambiguation (SDL vs WCF, NSSF, OSHA) ---

p("b006_sdl_034",
  "Tofauti kuu kati ya SDL, NSSF, WCF ni nini?",
  "SDL (3.5%, mwajiri tu, ≥10 wafanyakazi): ushuru wa mafunzo ya ujuzi, kwenda TRA. NSSF (10%+10%, mwajiri na mfanyakazi): pensheni na bima ya jamii, kwenda NSSF. WCF (0.5%, mwajiri tu): bima ya ajali za kazi, kwenda WCF. Ni mifumo mitatu tofauti ya kisheria.",
  "What are the main differences between SDL, NSSF, and WCF?",
  "SDL (3.5%, employer only, ≥10 employees): levy for skills training, goes to TRA. NSSF (10%+10%, employer and employee): pension and social security, goes to NSSF. WCF (0.5%, employer only): workplace accident insurance, goes to WCF. They are three separate legal frameworks.",
  "formal", "disambiguation"),

p("b006_sdl_035",
  "Je, SDL na WCF zinalipwa siku moja?",
  "Hapana, zinalipwa kwa vyombo tofauti. SDL inalipwa TRA ifikapo tarehe 7. WCF (Workers Compensation Fund) inalipwa WCF — kiwango cha 0.5% ya mishahara. Muda wa malipo wa WCF unaweza kutofautiana — thibitisha na WCF portal. Ni mifumo miwili tofauti isiyohusiana.",
  "Are SDL and WCF paid on the same date?",
  "No, they are paid to different bodies. SDL is paid to TRA by the 7th. WCF (Workers Compensation Fund) is paid to WCF — at 0.5% of payroll. WCF payment timing may vary — verify with the WCF portal. They are two separate unrelated frameworks.",
  "business_market", "standard"),

p("b006_sdl_036",
  "SDL na OSHA — ni sheria zinazoathiriana?",
  "Hapana moja kwa moja. SDL (Skills Development Levy) ni ushuru wa TRA unaohusiana na mafunzo ya ujuzi wa kazi. OSHA inasimamia usalama na afya mahali pa kazi. Ni sheria mbili tofauti zenye madhumuni tofauti. Kufuata OSHA hakukuondolei wajibu wa SDL, na kinyume chake.",
  "SDL and OSHA — are they interconnected laws?",
  "Not directly. SDL (Skills Development Levy) is a TRA levy related to job skills training. OSHA governs occupational health and safety. They are two different laws with different purposes. OSHA compliance does not remove your SDL obligation, and vice versa.",
  "formal", "disambiguation"),

# --- GROUP 9: SDL practical scenarios ---

p("b006_sdl_037",
  "Kampuni yangu ilifanya hasara mwaka huu — je, bado nalipa SDL?",
  "Ndiyo. SDL inahesabiwa kwa mishahara (gross payroll) — si faida ya kampuni. Hata kampuni inayofanya hasara inalipa SDL kama ina wafanyakazi 10+ na inalipalipa mishahara. SDL si kodi ya mapato — ni ushuru wa mwajiri kulingana na mishahara.",
  "My company made a loss this year — do I still pay SDL?",
  "Yes. SDL is calculated on payroll (gross salaries) — not company profit. Even a loss-making company pays SDL if it has 10+ employees and is paying salaries. SDL is not an income tax — it is an employer levy based on payroll.",
  "business_market", "adversarial"),

p("b006_sdl_038",
  "Mwajiri amebadilisha wadhifa wa wafanyakazi 3 kuwa wapya mwezi huu — SDL inaathirika?",
  "SDL inategemea jumla ya wafanyakazi na mishahara kwa mwezi husika — si mabadiliko ya udhifa. Kwa mwezi wa mpito (watu wanakuja na kuondoka), hesabu wafanyakazi wote waliohudumika mwezi huo. Hata wanaojiunga nusu mwezi wanaweza kuhesabiwa. Thibitisha na mshauri wa kodi.",
  "My employer replaced 3 workers with new ones this month — how does this affect SDL?",
  "SDL depends on the total employee count and payroll for that month — not changes in staffing. For a transition month (people joining and leaving), count all employees who served that month. Even those joining mid-month may be counted. Verify with a tax advisor.",
  "formal", "standard"),

p("b006_sdl_039",
  "SDL ya mwezi Januari inahesabiwa kwa mshahara wa Januari au Desemba?",
  "SDL ya mwezi Januari inahesabiwa kwa mishahara ya Januari (mishahara iliyolipwa ndani ya mwezi huo) na inalipwa TRA ifikapo tarehe 7 Februari. SDL inafuata mwezi ambao mishahara inayohusika ililipwa — si mwezi wa malipo ya SDL.",
  "Is January's SDL calculated on January's or December's payroll?",
  "January's SDL is calculated on January's payroll (salaries paid within that month) and is remitted to TRA by 7 February. SDL follows the month in which the relevant salaries were paid — not the month in which SDL itself is remitted.",
  "formal", "standard"),

p("b006_sdl_040",
  "Mwajiri alipuka (liquidation) — je, SDL inaendelea kulipwa?",
  "Katika mchakato wa ufilisi (liquidation), mdhamini (liquidator) analipa madeni ya serikali ikiwa ni pamoja na SDL iliyobakia. SDL iliyokwisha kulipwa ni faida kwa wafanyakazi — ilikwenda kwa VETA/TRA. SDL inayobakia ni deni la awali (priority debt) katika ufilisi.",
  "An employer goes into liquidation — does SDL continue to be paid?",
  "During liquidation, the liquidator pays government debts including outstanding SDL. SDL already paid was for the benefit of employees — it went to VETA/TRA. Outstanding SDL is a priority debt in the liquidation process.",
  "formal", "standard"),

# --- GROUP 10: SDL misconceptions and out-of-corpus ---

p("b006_sdl_041",
  "SDL inalipiwa wafanyakazi moja kwa moja au inakwenda serikalini?",
  "SDL inakwenda serikalini — hasa TRA (Tanzania Revenue Authority). Haiendi moja kwa moja kwa wafanyakazi. TRA inaitumia kusaidia VETA (Vocational Education and Training Authority) na programu za mafunzo. Mfanyakazi hupata manufaa kwa njia ya mafunzo ya umma, si malipo ya moja kwa moja.",
  "Is SDL paid directly to employees or does it go to the government?",
  "SDL goes to the government — specifically TRA (Tanzania Revenue Authority). It is not paid directly to employees. TRA uses it to support VETA (Vocational Education and Training Authority) and training programmes. Employees benefit through public training, not direct payments.",
  "formal", "standard"),

p("b006_sdl_042",
  "Je, SDL ni bima au ushuru?",
  "SDL ni ushuru (levy/tax) — si bima. Tofauti na NSSF (ambayo ni bima ya pensheni) au WCF (bima ya ajali), SDL ni malipo ya serikali yanayokwenda TRA na VETA. Haitoi fidia ya moja kwa moja kwa mfanyakazi yeyote.",
  "Is SDL insurance or a tax?",
  "SDL is a levy/tax — not insurance. Unlike NSSF (which is pension insurance) or WCF (workplace accident insurance), SDL is a government payment that goes to TRA and VETA. It does not provide direct compensation to any individual employee.",
  "formal", "standard"),

p("b006_sdl_043",
  "Mwajiri wa ndani ya nyumba (nyumba ya binafsi, msaidizi wa nyumbani) — analipa SDL?",
  "Kwa kawaida, waajiri wa msaidizi wa nyumbani (nyumba za binafsi wenye msaidizi mmoja au wachache) wako nje ya mfumo wa SDL wa kawaida wa biashara. Hata hivyo, hali maalum inaweza kutofautiana. Thibitisha na TRA kama unashuku una wajibu.",
  "A domestic employer (private home, household helper) — do they pay SDL?",
  "Generally, employers of domestic workers (private households with one or few helpers) are outside the standard business SDL framework. However, specific situations may vary. Verify with TRA if you suspect you have an obligation.",
  "rural_conversational", "out_of_corpus_refusal"),

p("b006_sdl_044",
  "SDL inatumiwa kufundisha wafanyakazi wa kampuni yangu moja kwa moja?",
  "Si moja kwa moja. SDL inakwenda TRA/VETA na inachangia mfumo mkubwa wa mafunzo ya ufundi. Kampuni haipati sehemu ya SDL yake moja kwa moja. Wafanyakazi wanaweza kufaidika kwa kuingia kwenye mafunzo ya VETA, lakini si kulipwa SDL moja kwa moja.",
  "Is SDL used to train my company's employees directly?",
  "Not directly. SDL goes to TRA/VETA and contributes to the broader vocational training system. A company does not receive its SDL share back directly. Employees can benefit by accessing VETA training, but not from SDL being paid back directly.",
  "business_market", "standard"),

p("b006_sdl_045",
  "Je, SDL inaweza kutumika kama gharama inayopunguzwa (deductible) kwa Corporate Tax?",
  "SDL inaweza kuchukuliwa kama gharama ya biashara inayopunguzwa kwa madhumuni ya Corporate Tax. Hii ina maana mwajiri anaweza kuondoa SDL iliyolipwa kutoka mapato yake kabla ya kuhesabu kodi ya makampuni. Thibitisha na mshauri wako wa kodi hali yako mahususi.",
  "Can SDL be treated as a deductible expense for Corporate Tax?",
  "SDL may be treated as a deductible business expense for Corporate Tax purposes. This means the employer may deduct SDL paid from their income before calculating corporate tax. Verify with your tax advisor for your specific situation.",
  "formal", "standard"),

# --- GROUP 11: Multi-error adversarial ---

p("b006_sdl_046",
  "Rafiki anasema: 'SDL ya 5% inakatwa kutoka kwa mfanyakazi na inalipiwa NSSF.' Sahihi?",
  "Kila sehemu ni kosa. SDL: (1) ni 3.5% — si 5%; (2) inalipwa na MWAJIRI — haikatiwi kwa mfanyakazi; (3) inalipwa TRA — si NSSF. NSSF ni mfumo tofauti kabisa (10%+10%, mwajiri na mfanyakazi). Habari hizi tatu ni potofu.",
  "A friend says: 'SDL of 5% is deducted from the employee and paid to NSSF.' Correct?",
  "Every part is wrong. SDL: (1) is 3.5% — not 5%; (2) is paid by the EMPLOYER — not deducted from employees; (3) is paid to TRA — not NSSF. NSSF is a completely separate framework (10%+10%, employer and employee). All three pieces of information are false.",
  "business_market", "adversarial"),

p("b006_sdl_047",
  "Mwajiri anasema: 'Sisi tuna wafanyakazi 10, lakini tunalipa SDL ya 2% tu.' Je, hii ni sahihi?",
  "Hapana. Kama kampuni ina wafanyakazi 10 au zaidi, kiwango cha SDL ni 3.5% — si 2%. Kulipa 2% tu kunaacha deni la 1.5% kwa TRA, ambayo itasababisha adhabu na riba. Lipeni SDL sahihi ya 3.5% ya jumla ya mishahara.",
  "An employer says: 'We have 10 employees but only pay 2% SDL.' Is this correct?",
  "No. If a company has 10 or more employees, the SDL rate is 3.5% — not 2%. Paying only 2% leaves a 1.5% debt to TRA, which will attract penalties and interest. Pay the correct SDL of 3.5% of total payroll.",
  "business_market", "adversarial"),

p("b006_sdl_048",
  "SDL ya kampuni yenye wafanyakazi 15 na mishahara jumla TZS 10M kwa mwezi ni kiasi gani?",
  "SDL = 3.5% × TZS 10,000,000 = TZS 350,000 kwa mwezi. Inalipwa TRA ifikapo tarehe 7 ya mwezi unaofuata. Idadi ya wafanyakazi (15) inathibitisha SDL inahitajika (≥10), lakini kiwango kinahesabiwa kwa jumla ya mishahara, si kwa kichwa cha mtu.",
  "SDL for a company with 15 employees and total payroll of TZS 10M per month is how much?",
  "SDL = 3.5% × TZS 10,000,000 = TZS 350,000 per month. It is paid to TRA by the 7th of the following month. The headcount (15) confirms SDL is required (≥10), but the amount is calculated on total payroll, not per person.",
  "business_market", "standard"),

p("b006_sdl_049",
  "SDL, NSSF, WCF, PAYE — muhtasari wa ni nani analipa nini.",
  "PAYE: mfanyakazi hulipa (mwajiri anaikata na kuipeleka TRA, tarehe 7). NSSF: mwajiri 10% + mfanyakazi 10% (inakwenda NSSF). WCF: mwajiri 0.5% peke yake (inakwenda WCF). SDL: mwajiri 3.5% peke yake kwa wafanyakazi ≥10 (inakwenda TRA, tarehe 7). Sehemu za mfanyakazi: PAYE + NSSF. Sehemu za mwajiri peke yake: NSSF (10%) + WCF + SDL.",
  "SDL, NSSF, WCF, PAYE — summary of who pays what.",
  "PAYE: employee pays (employer deducts and remits to TRA, by 7th). NSSF: employer 10% + employee 10% (goes to NSSF). WCF: employer 0.5% only (goes to WCF). SDL: employer 3.5% only for ≥10 employees (goes to TRA, by 7th). Employee's portions: PAYE + NSSF. Employer-only portions: NSSF (10%) + WCF + SDL.",
  "formal", "standard"),

p("b006_sdl_050",
  "Kwa muhtasari: SDL inamaanisha nini kwa mwajiri wa kawaida Tanzania?",
  "SDL (Skills Development Levy) kwa mwajiri: (1) Jina kamili: Skills Development Levy — si disability leave wala aina yoyote ya likizo; (2) Kiwango: 3.5% ya gross payroll; (3) Kizingiti: wafanyakazi 10 au zaidi; (4) Analipa: mwajiri peke yake (si mfanyakazi); (5) Kwenda: TRA ifikapo tarehe 7 ya mwezi unaofuata; (6) Lengo: kufadhili mafunzo ya ufundi (VETA).",
  "Summary: what does SDL mean for a typical employer in Tanzania?",
  "SDL (Skills Development Levy) for the employer: (1) Full name: Skills Development Levy — not disability leave or any type of leave; (2) Rate: 3.5% of gross payroll; (3) Threshold: 10 or more employees; (4) Payer: employer only (not the employee); (5) Destination: TRA by the 7th of the following month; (6) Purpose: to fund vocational training (VETA).",
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
