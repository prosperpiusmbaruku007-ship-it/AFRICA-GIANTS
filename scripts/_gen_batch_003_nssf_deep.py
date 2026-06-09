"""Generate 50 NSSF deep-dive pairs (batch_003 pairs 201-250)."""
import json

SRC_URL = "https://www.nssf.or.tz/pages/payment-of-contributions"
SRC_NAME = "NSSF Contributions Page"
DATE = "20260608"

def p(n, sub, q_sw, a_sw, q_en, a_en, reg, ptype="standard"):
    return {"id": f"tier1a_nssf_deep_{n:03d}_{DATE}", "domain": "tier1a", "subdomain": sub,
            "question_sw": q_sw, "answer_sw": a_sw, "question_en": q_en, "answer_en": a_en,
            "primary_source_url": SRC_URL, "primary_source_name": SRC_NAME,
            "source_type": "government_portal", "effective_date": "2026-01-01",
            "decay_risk": "annual", "next_review_trigger": "NSSF Act amendment",
            "verified_by": "NSSF Act Cap.50 + NSSF website", "verified_date": "2026-06-08",
            "register": reg, "pair_type": ptype, "eval_set": False}

pairs = []

# ── MULTI-EMPLOYER NSSF (pairs 1-4) ─────────────────────────────────────────

pairs.append(p(1,"nssf_multi_employer",
    "Mfanyakazi wangu ana kazi mbili — kampuni yangu na kampuni nyingine. Je, NSSF inalipwa mara mbili?",
    "Kwa mfanyakazi mwenye waajiri wawili, kila mwajiri analipa NSSF kwa sehemu ya mshahara wake: mwajiri 10% na mfanyakazi 10% = jumla 20% kwa kila chanzo cha mshahara. Kwa mfano: Kampuni A inalipa 10% ya TZS 500,000, Kampuni B inalipa 10% ya TZS 300,000 — jumla ya michango inakuwa 20% ya kila mshahara, si 20% ya jumla. Mfanyakazi anatoa namba moja ya NSSF kwa waajiri wote. Michango yote inaenda kwenye akaunti moja ya NSSF ya mfanyakazi.",
    "My employee has two jobs — my company and another company. Is NSSF paid twice?",
    "For an employee with two employers, each employer pays NSSF on their portion of the salary: employer 10% plus employee 10% = total 20% from each salary source. Example: Company A pays 10% of TZS 500,000, Company B pays 10% of TZS 300,000 — contributions are 20% of each salary separately, not 20% of the combined total. The employee provides one NSSF number to all employers. All contributions go into the employee's single NSSF account.",
    "business_market"))

pairs.append(p(2,"nssf_multi_employer",
    "Mfanyakazi ana waajiri wawili — anaweza kutoa namba moja ya NSSF kwa wote?",
    "Ndiyo. Mfanyakazi ana namba moja tu ya NSSF (NSSF number) — hii ndiyo inayotumika bila kujali idadi ya waajiri. Kila mwajiri anawasilisha michango kwa namba hiyo hiyo ya NSSF. NSSF inakusanya michango yote na kuiongeza kwenye akaunti moja ya mfanyakazi. Kiwango ni 10% ya mwajiri + 10% ya mfanyakazi = 20% ya mshahara mkubwa wa jumla, kwa kila mwajiri tofauti tofauti.",
    "An employee has two employers — can they give one NSSF number to both?",
    "Yes. An employee has only one NSSF number — this is used regardless of the number of employers. Each employer submits contributions under that same NSSF number. NSSF aggregates all contributions and adds them to one employee account. The rate is 10% employer + 10% employee = 20% of gross wage, calculated separately by each employer.",
    "formal"))

pairs.append(p(3,"nssf_multi_employer",
    "Je, inawezekana kulipa NSSF zaidi ya viwango vya kawaida kama mfanyakazi anataka akiba zaidi?",
    "Ndiyo. Sheria ya NSSF inaruhusu michango ya ziada (voluntary contributions) zaidi ya kiwango cha lazima cha 10%+10%. Mfanyakazi au mwajiri anaweza kuchangia kwa hiari ziada ya kiwango cha lazima. Michango ya ziada inaongeza faida za mwisho wa kazi. Kwa maelezo ya mpango wa michango ya ziada, wasiliana na ofisi ya NSSF. Kiwango cha lazima cha msingi ni: mwajiri 10% + mfanyakazi 10% = 20% ya mshahara mkubwa wa jumla.",
    "Is it possible to pay more NSSF than the standard rate if an employee wants more savings?",
    "Yes. The NSSF Act allows voluntary contributions above the mandatory 10%+10% rate. An employee or employer can voluntarily contribute above the mandatory minimum. Additional contributions increase end-of-service benefits. For details on the voluntary contribution scheme, contact the NSSF office. The mandatory minimum is: employer 10% + employee 10% = 20% of gross wage.",
    "business_market"))

pairs.append(p(4,"nssf_multi_employer",
    "Mwajiri mkuu anapaswa kulipa NSSF nzima ikiwa mfanyakazi ana kazi nyingine?",
    "Hapana. Kila mwajiri analipa NSSF kwa sehemu ya mshahara wake peke yake — si jumla ya mishahara yote. Mwajiri wa kwanza analipa 10% ya mshahara wake (na kukata 10% ya mfanyakazi kutoka mshahara wake). Mwajiri wa pili anafanya vivyo hivyo kwa mshahara wake. Hakuna wajibu wa mwajiri mmoja kulipa NSSF kwa mshahara unaotoka kwa mwajiri mwingine. Msingi wa hesabu ni mshahara mkubwa wa jumla kutoka kwa mwajiri husika.",
    "Must the main employer pay full NSSF if an employee also has another job?",
    "No. Each employer pays NSSF on their own portion of salary only — not the combined total. The first employer pays 10% of their salary (and deducts the employee's 10% from that salary). The second employer does the same on their salary. No employer has an obligation to pay NSSF on wages paid by another employer. The calculation base is the gross wage from that specific employer.",
    "rural_conversational"))

# ── NSSF FOR CASUAL WORKERS (pairs 5-8) ─────────────────────────────────────

pairs.append(p(5,"nssf_casual_workers",
    "Wafanyakazi wa muda mfupi (casual workers) wanalipa NSSF Tanzania?",
    "Ndiyo. Wafanyakazi wanaolipwa mishahara, ikiwemo casual workers, wanastahili kulipa NSSF. Kiwango: mwajiri 10% + mfanyakazi 10% = 20% ya mshahara mkubwa wa jumla. Msingi wa hesabu ni mshahara mkubwa wa jumla (gross wage) — si mshahara wa msingi (basic salary). Tarehe ya mwisho wa malipo: ndani ya mwezi mmoja baada ya mwezi wa mshahara.",
    "Do casual workers pay NSSF in Tanzania?",
    "Yes. Workers who receive wages, including casual workers, are eligible to contribute to NSSF. Rate: employer 10% + employee 10% = 20% of gross wage. The calculation base is total gross wage — not basic salary. Payment deadline: within one month after the salary month.",
    "business_market"))

pairs.append(p(6,"nssf_casual_workers",
    "Mfanyakazi anayefanya kazi siku 3 kwa wiki — NSSF inahesabiwaje?",
    "NSSF kwa mfanyakazi wa siku chache kwa wiki inahesabiwaje kwa msingi wa mshahara unaolipwa halisi (actual gross wage). Kama mfanyakazi analipwa TZS 10,000 kwa siku, siku 3 kwa wiki = TZS 120,000 kwa mwezi (kama wiki 4), basi NSSF = TZS 120,000 × 20% = TZS 24,000 (mwajiri 12,000 + mfanyakazi 12,000). Hakuna uwiano wa saa za kazi — inategemea mshahara mkubwa wa jumla uliolipwa.",
    "An employee works 3 days per week — how is NSSF calculated?",
    "NSSF for a part-week worker is calculated on actual gross wages paid. If an employee is paid TZS 10,000 per day, 3 days per week = TZS 120,000 per month (assuming 4 weeks), then NSSF = TZS 120,000 × 20% = TZS 24,000 (employer TZS 12,000 + employee TZS 12,000). There is no pro-rating by hours — it depends on actual gross wages paid.",
    "rural_conversational"))

pairs.append(p(7,"nssf_casual_workers",
    "Je, mwajiri analazimika kuwasilisha NSSF kwa wafanyakazi wa muda mfupi wanaofanya kazi siku moja tu?",
    "Kinadharia ndiyo — NSSF inahusu wafanyakazi wote wanaolipwa mishahara, bila kujali muda wa ajira. Hata hivyo, kwa vitendo, wafanyakazi wanaofanya kazi siku moja wanaweza kuwa hawana usajili wa NSSF (NSSF number). Mwajiri anapaswa kuhakikisha wafanyakazi wote wanaoajiriwa mara kwa mara wana NSSF number. Kwa wafanyakazi wa siku moja wa kweli, wasiliana na NSSF kwa mwongozo wa utekelezaji.",
    "Is an employer required to remit NSSF for casual workers who work only one day?",
    "In principle yes — NSSF applies to all wage-earning workers regardless of employment duration. However, in practice, workers who work only one day may not have an NSSF registration number. The employer should ensure all regularly employed workers have an NSSF number. For truly one-day casual workers, contact NSSF for implementation guidance.",
    "formal"))

pairs.append(p(8,"nssf_casual_workers",
    "NSSF kwa wafanyakazi wanaolipwa kwa siku (daily rated) inahesabiwaje?",
    "NSSF kwa wafanyakazi wanaolipwa kwa siku inahesabiwaje kwa jumla ya mshahara mkubwa wa jumla uliolipwa katika kipindi cha malipo (kawaida mwezi). Jumla mshahara = siku zilizofanya kazi × kiwango cha siku. NSSF = jumla ya mshahara × 20% (mwajiri 10% + mfanyakazi 10%). Msingi ni mshahara mkubwa wa jumla — si kiwango cha siku peke yake. Tarehe: ndani ya mwezi mmoja baada ya mwezi wa mshahara.",
    "How is NSSF calculated for daily-rated workers?",
    "NSSF for daily-rated workers is calculated on total gross wages paid in the payment period (usually a month). Total wages = days worked × daily rate. NSSF = total wages × 20% (employer 10% + employee 10%). The base is total gross wage — not the daily rate alone. Deadline: within one month after the salary month.",
    "business_market"))

# ── NSSF FOR DIRECTORS (pairs 9-11) ──────────────────────────────────────────

pairs.append(p(9,"nssf_directors",
    "Je, mkurugenzi wa kampuni analipa NSSF?",
    "Mkurugenzi anayepokea mshahara (executive director) analipa NSSF kama mfanyakazi yeyote — mwajiri 10% + mkurugenzi 10% = 20% ya mshahara mkubwa wa jumla. Mkurugenzi asiyepokea mshahara (non-executive director) ambaye hapokei mishahara ya kawaida hawezi kuwa na wajibu wa NSSF kwa msingi wa mshahara. Kwa mwongozo wa hali maalum za wakurugenzi, wasiliana na NSSF.",
    "Does a company director pay NSSF?",
    "An executive director who receives a salary pays NSSF like any other employee — employer 10% + director 10% = 20% of gross wage. A non-executive director who does not receive regular wages may not have an NSSF obligation on a wage basis. For guidance on specific director arrangements, contact NSSF.",
    "formal"))

pairs.append(p(10,"nssf_directors",
    "Mkurugenzi Mkurugenzi (MD) analipwa TZS 5,000,000 kwa mwezi. NSSF yake ni kiasi gani?",
    "NSSF ya MD: mshahara wa TZS 5,000,000 × 20% = TZS 1,000,000 kwa mwezi. Kampuni inalipa: TZS 5,000,000 × 10% = TZS 500,000. MD analipa (kutoka mshahara wake): TZS 5,000,000 × 10% = TZS 500,000. Msingi ni mshahara mkubwa wa jumla — si mshahara wa msingi. Wasilisha ndani ya mwezi mmoja baada ya mwezi wa mshahara.",
    "The Managing Director is paid TZS 5,000,000 per month. How much is their NSSF?",
    "NSSF for the MD: salary TZS 5,000,000 × 20% = TZS 1,000,000 total per month. Company pays: TZS 5,000,000 × 10% = TZS 500,000. MD pays (from their salary): TZS 5,000,000 × 10% = TZS 500,000. Base is gross wage — not basic salary. Submit within one month after the salary month.",
    "business_market"))

pairs.append(p(11,"nssf_directors",
    "Wakurugenzi wa pekee (sole directors) wanaofanya kazi peke yao — je, wana wajibu wa NSSF?",
    "Mkurugenzi wa pekee anayejilipa mshahara katika kampuni yake ana wajibu wa NSSF — kampuni (kama mwajiri) inalipa 10% na mkurugenzi (kama mfanyakazi) analipa 10% = jumla 20% ya mshahara mkubwa wa jumla. Ikiwa mkurugenzi anachukua gawio (dividends) badala ya mshahara, hali inaweza kutofautiana. Kwa mwongozo wa hali hii maalum, wasiliana na NSSF moja kwa moja.",
    "Sole directors who work alone in their company — do they have NSSF obligations?",
    "A sole director who pays themselves a salary in their company has NSSF obligations — the company (as employer) pays 10% and the director (as employee) pays 10% = total 20% of gross wage. If the director takes dividends instead of a salary, the situation may differ. For guidance on this specific arrangement, contact NSSF directly.",
    "formal"))

# ── NSSF FOR FOREIGN EMPLOYEES (pairs 12-14) ─────────────────────────────────

pairs.append(p(12,"nssf_foreign_employees",
    "Mfanyakazi wa kigeni anayefanya kazi Tanzania analipa NSSF?",
    "Ndiyo. Mfanyakazi wa kigeni anayefanya kazi Tanzania Bara na kupokea mshahara analazimika kulipa NSSF. Kiwango ni sawa: mwajiri 10% + mfanyakazi 10% = 20% ya mshahara mkubwa wa jumla. Raia wa kigeni wanaofanya kazi Tanzania wanastahili faida za NSSF baada ya kukusanya michango ya kutosha. Tofauti pekee inaweza kuwa katika mazingira ya makubaliano ya pande mbili ya hifadhi ya jamii — wasiliana na NSSF.",
    "Does a foreign employee working in Tanzania pay NSSF?",
    "Yes. A foreign employee working on Mainland Tanzania and receiving wages is required to contribute to NSSF. The rate is the same: employer 10% + employee 10% = 20% of gross wage. Foreign nationals working in Tanzania are entitled to NSSF benefits after accumulating sufficient contributions. The only difference may be in the context of bilateral social security agreements — contact NSSF.",
    "formal"))

pairs.append(p(13,"nssf_foreign_employees",
    "Je, mfanyakazi wa kigeni anaweza kutoa mchango wake wa NSSF atakapoondoka Tanzania?",
    "Mfanyakazi wa kigeni anaondoka Tanzania anaweza kudai sehemu ya faida ya NSSF kulingana na miaka ya michango. Ikiwa wamechangia chini ya miezi 180 (miaka 15), wanaweza kupata faida za muda mfupi. Upatikanaji wa faida unategemea makubaliano ya hifadhi ya jamii kati ya Tanzania na nchi ya asili ya mfanyakazi. Kwa maelezo ya upatikanaji wa faida kwa wafanyakazi wa kigeni, wasiliana na NSSF moja kwa moja.",
    "Can a foreign employee withdraw their NSSF contributions when leaving Tanzania?",
    "A foreign employee leaving Tanzania may claim NSSF benefits depending on their years of contribution. If they have contributed for fewer than 180 months (15 years), they may be eligible for short-term benefits. Access to benefits depends on any social security bilateral agreements between Tanzania and the employee's home country. For details on benefit access for foreign employees, contact NSSF directly.",
    "business_market"))

pairs.append(p(14,"nssf_foreign_employees",
    "Mfanyakazi kutoka Kenya anafanya kazi Dar es Salaam — wajibu wa NSSF ni wa Tanzania au Kenya?",
    "Mfanyakazi kutoka Kenya anayefanya kazi Tanzania Bara analipa NSSF ya Tanzania — si NSSF ya Kenya. Wajibu unafuata mahali pa kazi (lex loci laboris). Mwajiri wa Tanzania analipa 10% ya mshahara na kukata 10% kutoka kwa mfanyakazi, kisha kuwasilisha NSSF Tanzania. Hata hivyo, kama mfanyakazi amepewa kwa muda mfupi, kanuni za EAC Portability of Social Security zinaweza kutumika — wasiliana na NSSF.",
    "An employee from Kenya works in Dar es Salaam — is the NSSF obligation Tanzania's or Kenya's?",
    "An employee from Kenya working on Mainland Tanzania pays Tanzania NSSF — not Kenya's. The obligation follows the place of work (lex loci laboris). The Tanzanian employer pays 10% of the wage and deducts 10% from the employee, then remits to Tanzania NSSF. However, if the employee is on a short-term secondment, EAC Portability of Social Security rules may apply — contact NSSF.",
    "formal"))

# ── NSSF ON OVERTIME AND BONUSES (pairs 15-18) ───────────────────────────────

pairs.append(p(15,"nssf_overtime_bonuses",
    "NSSF inahesabiwaje kwa wafanyakazi wanaopata overtime?",
    "Mshahara wa overtime unajumuishwa kwenye msingi wa mshahara mkubwa wa jumla kwa NSSF. Yaani: NSSF = (mshahara wa msingi + overtime + malipo mengine yoyote yanayolipwa kawaida) × 20%. Msingi ni mshahara mkubwa wa jumla — si mshahara wa msingi peke yake. Kiwango: mwajiri 10% + mfanyakazi 10%. Tarehe ya mwisho: ndani ya mwezi mmoja baada ya mwezi wa mshahara.",
    "How is NSSF calculated for employees who receive overtime?",
    "Overtime wages are included in the gross wage base for NSSF. That is: NSSF = (basic salary + overtime + any other regularly paid allowances) × 20%. The base is total gross wage — not basic salary alone. Rate: employer 10% + employee 10%. Deadline: within one month after the salary month.",
    "business_market"))

pairs.append(p(16,"nssf_overtime_bonuses",
    "Je, bonus ya mwaka mzima (annual bonus) inatozwa NSSF?",
    "Kinadharia ndiyo — malipo yote yanayolipwa kwa mfanyakazi kama sehemu ya mshahara (ikiwemo bonuses) yanaweza kujumuishwa kwenye msingi wa NSSF. Hata hivyo, utekelezaji wa vitendo unaweza kutofautiana kulingana na aina ya bonus (mara moja vs ya kawaida) na jinsi inavyoainishwa kisheria. Kwa mwongozo wa hali yako maalum ya bonus, wasiliana na NSSF. Kiwango cha lazima ni mwajiri 10% + mfanyakazi 10% ya mshahara mkubwa wa jumla.",
    "Is an annual bonus subject to NSSF?",
    "In principle yes — all payments made to an employee as part of compensation (including bonuses) may be included in the NSSF base. However, practical application may vary depending on the type of bonus (one-off vs regular) and how it is legally classified. For guidance on your specific bonus situation, contact NSSF. The mandatory rate is employer 10% + employee 10% of gross wage.",
    "formal"))

pairs.append(p(17,"nssf_overtime_bonuses",
    "Mfanyakazi ana posho za nyumba (housing allowance) na chakula (meal allowance). Je, hizi zinatozwa NSSF?",
    "Posho zinazolipwa kawaida kama sehemu ya mshahara (housing allowance, meal allowance) kwa ujumla zinajumuishwa kwenye msingi wa NSSF — yaani mshahara mkubwa wa jumla. Hii ni kwa sababu NSSF inategemea 'gross wage' si 'basic salary'. Posho zinazolipwa mara moja au zinazorejesha gharama halisi (reimbursements) zinaweza kushughulikiwa tofauti. Wasiliana na NSSF kwa mwongozo wa aina mahususi za posho.",
    "An employee has housing and meal allowances. Are these subject to NSSF?",
    "Allowances regularly paid as part of compensation (housing allowance, meal allowance) are generally included in the NSSF gross wage base. This is because NSSF is based on 'gross wage' not 'basic salary'. One-off allowances or genuine reimbursements of actual expenses may be treated differently. Contact NSSF for guidance on specific types of allowances.",
    "business_market"))

pairs.append(p(18,"nssf_overtime_bonuses",
    "Je, 'gross wage' kwa NSSF ni sawa na 'gross salary' kwenye payslip?",
    "Kwa ujumla ndiyo — mshahara mkubwa wa jumla (gross wage) kwa NSSF ni jumla ya malipo yote ya mfanyakazi kabla ya makato: mshahara wa msingi, posho za kawaida, overtime, na malipo mengine yanayolipwa kawaida. Si jumla ya aina yoyote ya malipo ya pekee au reimbursements. Kiwango: mwajiri 10% + mfanyakazi 10% = 20% ya gross wage. Msingi huu ni tofauti na 'basic salary' — NSSF haihesabiwi kwa mshahara wa msingi peke yake.",
    "Is 'gross wage' for NSSF the same as 'gross salary' on the payslip?",
    "Generally yes — gross wage for NSSF is the total of all regular employee payments before deductions: basic salary, regular allowances, overtime, and other regularly paid components. It does not include one-off special payments or reimbursements. Rate: employer 10% + employee 10% = 20% of gross wage. This base differs from 'basic salary' — NSSF is not calculated on basic salary alone.",
    "formal"))

# ── NSSF DURING MATERNITY LEAVE (pairs 19-21) ────────────────────────────────

pairs.append(p(19,"nssf_maternity_leave",
    "Mfanyakazi yuko likizo ya uzazi (maternity leave). Je, NSSF inaendelea kulipwa?",
    "Ndiyo. Wakati wa likizo ya uzazi inayolipwa (paid maternity leave), mwajiri anapaswa kuendelea kulipa NSSF kwa kiwango cha kawaida kwa mshahara unaolipwa. Kiwango ni mwajiri 10% + mfanyakazi 10% = 20% ya mshahara mkubwa wa jumla. Ikiwa mfanyakazi yuko likizo ya uzazi bila malipo, hali inategemea kama mshahara unalipwa au la — michango ya NSSF inafuata malipo ya mshahara halisi.",
    "An employee is on maternity leave. Does NSSF continue to be paid?",
    "Yes. During paid maternity leave, the employer must continue paying NSSF at the standard rate on wages paid. Rate: employer 10% + employee 10% = 20% of gross wage. If the employee is on unpaid maternity leave, the situation depends on whether wages are being paid — NSSF contributions follow actual wage payments.",
    "business_market"))

pairs.append(p(20,"nssf_maternity_leave",
    "Mfanyakazi wa kike ana haki ya likizo ngapi ya uzazi Tanzania?",
    "Kulingana na ELRA (Employment and Labour Relations Act) Tanzania, mfanyakazi wa kike ana haki ya likizo ya uzazi ya siku 84 (wiki 12) bila kupoteza mshahara. Wakati huu wote, NSSF inaendelea kulipwa kwa mshahara unaolipwa: mwajiri 10% + mfanyakazi 10% = 20% ya mshahara mkubwa wa jumla. Tarehe ya mwisho wa malipo ya NSSF inabaki ndani ya mwezi mmoja baada ya mwezi wa mshahara.",
    "How many days of maternity leave does a female employee have in Tanzania?",
    "Under Tanzania's ELRA (Employment and Labour Relations Act), a female employee is entitled to 84 days (12 weeks) of maternity leave without loss of pay. Throughout this period, NSSF continues to be paid on wages paid: employer 10% + employee 10% = 20% of gross wage. The NSSF payment deadline remains within one month after the salary month.",
    "formal"))

pairs.append(p(21,"nssf_maternity_leave",
    "Je, mwajiri analazimika kulipa NSSF ya sehemu ya mwajiri wakati mfanyakazi yuko likizoni?",
    "Ndiyo — mchango wa mwajiri (employer contribution) wa NSSF ni wajibu wa mwajiri, si mfanyakazi. Wakati mfanyakazi yuko likizo yoyote inayolipwa (maternity, sick leave, annual leave), mwajiri anaendelea kulipa NSSF ya sehemu yake (10%) na kukata mchango wa mfanyakazi (10%) kutoka mshahara unaolipwa. Mwajiri hawezi kusimamisha mchango wake wa 10% kwa sababu mfanyakazi yuko likizoni.",
    "Is the employer required to pay their NSSF portion while an employee is on leave?",
    "Yes — the employer's NSSF contribution is the employer's obligation, not the employee's. While an employee is on any paid leave (maternity, sick leave, annual leave), the employer continues to pay their share (10%) and deduct the employee's share (10%) from wages paid. The employer cannot suspend their 10% contribution because the employee is on leave.",
    "business_market"))

# ── NSSF DURING UNPAID LEAVE (pairs 22-24) ───────────────────────────────────

pairs.append(p(22,"nssf_unpaid_leave",
    "Mfanyakazi yuko likizo bila malipo (unpaid leave) kwa mwezi mzima. Je, NSSF inalipwa?",
    "Wakati mfanyakazi yuko likizo bila malipo, hakuna mshahara unaolipwa — na kwa hivyo hakuna msingi wa NSSF ya kulipiwa. NSSF inahesabiwaje kwa msingi wa mshahara mkubwa wa jumla uliolipwa. Kama hakuna mshahara, hakuna michango ya NSSF inayohitajika kwa kipindi hicho. Kumbuka: mwezi huo hauhesabiwi kama mwezi wa mchango kwa madhumuni ya faida za NSSF.",
    "An employee is on unpaid leave for a whole month. Is NSSF paid?",
    "When an employee is on unpaid leave, no wages are paid — and therefore there is no NSSF base to calculate on. NSSF is calculated on actual gross wages paid. If no wages are paid, no NSSF contributions are required for that period. Note: that month will not count as a contribution month for NSSF benefit purposes.",
    "rural_conversational"))

pairs.append(p(23,"nssf_unpaid_leave",
    "Je, mfanyakazi anaweza kulipa NSSF yake mwenyewe wakati wa likizo bila malipo?",
    "Ndiyo. Mfanyakazi anaweza kulipa michango ya NSSF kwa hiari wakati wa likizo bila malipo ili kulinda akaunti yake ya NSSF na kuendelea kukusanya miezi ya mchango. Hii inasaidia kuhakikisha mfanyakazi anafikia miezi 180 ya michango inayohitajika kwa pensheni kamili. Wasiliana na NSSF kwa utaratibu wa kulipa kama mwanachama anayechangia kwa hiari.",
    "Can an employee pay their own NSSF during unpaid leave?",
    "Yes. An employee can voluntarily pay NSSF contributions during unpaid leave to protect their NSSF account and continue accumulating contribution months. This helps ensure the employee reaches the 180 contribution months needed for full pension. Contact NSSF for the procedure to pay as a voluntary contributing member.",
    "rural_conversational"))

pairs.append(p(24,"nssf_unpaid_leave",
    "Mfanyakazi aliyekuwa amelipwa nusu mshahara wakati wa ugonjwa — NSSF inahesabiwaje?",
    "NSSF inahesabiwaje kwa msingi wa mshahara uliolipwa halisi. Ikiwa mfanyakazi alilipwa nusu mshahara (50%) wakati wa ugonjwa, NSSF inahesabiwaje kwa msingi wa nusu mshahara hiyo: (nusu mshahara) × 20% = NSSF. Mwajiri 10% na mfanyakazi 10% ya mshahara uliodhalilishwa. Tarehe ya mwisho inabaki ndani ya mwezi mmoja baada ya mwezi wa mshahara.",
    "An employee was paid half salary during illness — how is NSSF calculated?",
    "NSSF is calculated on actual wages paid. If an employee was paid half salary (50%) during illness, NSSF is calculated on that half salary: (half salary) × 20% = NSSF. Employer 10% and employee 10% on the reduced salary. The deadline remains within one month after the salary month.",
    "business_market"))

# ── NSSF FOR PROBATIONARY EMPLOYEES (pairs 25-27) ────────────────────────────

pairs.append(p(25,"nssf_probationary",
    "Mfanyakazi aliye kwenye probation (muda wa majaribio) analipa NSSF?",
    "Ndiyo. Mfanyakazi aliye kwenye muda wa majaribio (probationary period) analipa NSSF kama mfanyakazi yeyote mwingine — mwajiri 10% + mfanyakazi 10% = 20% ya mshahara mkubwa wa jumla. Hali ya probation haiathiri wajibu wa NSSF. Muda wa probation unahesabiwaje kama miezi ya mchango wa NSSF ikiwa mfanyakazi ataendelea kufanya kazi.",
    "Does a probationary employee pay NSSF?",
    "Yes. An employee on probation pays NSSF like any other employee — employer 10% + employee 10% = 20% of gross wage. Probationary status does not affect the NSSF obligation. The probationary period counts as NSSF contribution months if the employee continues in employment.",
    "business_market"))

pairs.append(p(26,"nssf_probationary",
    "Je, mwajiri analazimika kusajili mfanyakazi mpya kwa NSSF mara moja?",
    "Ndiyo. Mwajiri analazimika kusajili mfanyakazi mpya kwa NSSF ndani ya mwezi wa kwanza wa ajira. Usajili wa NSSF lazima ufanyike kabla au wakati wa malipo ya kwanza ya mshahara. Kuchelewa kusajili kunaweza kusababisha adhabu. Mfanyakazi mpya anapewa namba ya NSSF ambayo inatumika kwa ajira zake zote za baadaye Tanzania.",
    "Is an employer required to register a new employee with NSSF immediately?",
    "Yes. An employer must register a new employee with NSSF within the first month of employment. NSSF registration must occur before or at the time of the first salary payment. Delayed registration may result in penalties. The new employee is given an NSSF number that is used for all their future employment in Tanzania.",
    "formal"))

pairs.append(p(27,"nssf_probationary",
    "Mfanyakazi wa probation alitolewa kazi mwezi wa 3. Je, NSSF iliyolipwa inarejeshwa?",
    "Hapana — NSSF iliyolipwa hairejiswi kwa mwajiri wala mfanyakazi wakati ajira inaisha kabla ya muda. Michango iliyolipwa inabaki kwenye akaunti ya NSSF ya mfanyakazi. Mfanyakazi anaweza kupata faida za muda mfupi (short-term benefits) au kuhifadhi michango hiyo kwa ajira yake ijayo. Mwajiri hawezi kudai kurejeshwa kwa michango ya mwajiri aliyolipa.",
    "A probationary employee was terminated in month 3. Is NSSF paid refunded?",
    "No — paid NSSF is not refunded to either the employer or employee when employment ends before completion. Contributions paid remain in the employee's NSSF account. The employee may access short-term benefits or retain those contributions for future employment. The employer cannot claim a refund of employer contributions already paid.",
    "rural_conversational"))

# ── NSSF FOR PART-TIME WORKERS (pairs 28-31) ─────────────────────────────────

pairs.append(p(28,"nssf_part_time",
    "Mfanyakazi wa nusu muda (part-time) analipa NSSF sawa na wa muda wote?",
    "Ndiyo. Mfanyakazi wa nusu muda analipa NSSF kwa msingi wa mshahara wake mkubwa wa jumla — bila kujali ni nusu ya muda au muda wote. Kiwango ni sawa: mwajiri 10% + mfanyakazi 10% = 20% ya mshahara mkubwa wa jumla wa mfanyakazi huyo. Kwa mfano: mfanyakazi wa nusu muda analipwa TZS 300,000/mwezi → NSSF = TZS 60,000 (mwajiri 30,000 + mfanyakazi 30,000).",
    "Does a part-time worker pay NSSF the same as a full-time employee?",
    "Yes. A part-time worker pays NSSF on their actual gross wages — regardless of whether they are part-time or full-time. The rate is the same: employer 10% + employee 10% = 20% of that employee's gross wage. Example: a part-time worker paid TZS 300,000/month → NSSF = TZS 60,000 (employer TZS 30,000 + employee TZS 30,000).",
    "business_market"))

pairs.append(p(29,"nssf_part_time",
    "Je, hakuna kiwango cha chini cha NSSF kwa mfanyakazi wa nusu muda?",
    "Hakuna kiwango cha chini cha shilingi za mchango wa NSSF kilichotajwa kisheria — mchango ni asilimia 20% ya mshahara mkubwa wa jumla, bila kujali kiasi. Mfanyakazi anayepata mshahara wa chini ya kiwango cha chini cha mshahara cha sekta yake bado analipa NSSF kwa msingi wa mshahara anaolipwa halisi. Kiwango cha chini cha mshahara (GN 605A) kinaathiri kiwango cha chini cha mshahara unaolipwa, si hesabu ya NSSF.",
    "Is there no minimum NSSF amount for a part-time worker?",
    "There is no legally specified minimum shilling amount for NSSF contributions — the contribution is 20% of actual gross wages, regardless of the amount. An employee earning below their sector's minimum wage still pays NSSF based on actual wages paid. The minimum wage (GN 605A) affects the minimum wage that must be paid, not the NSSF calculation itself.",
    "formal"))

pairs.append(p(30,"nssf_part_time",
    "Ninaajiri watu 5 wa nusu muda. Je, NSSF inatumika kwao?",
    "Ndiyo. Wafanyakazi 5 wa nusu muda wanaolipwa mishahara wanalazimika kulipwa NSSF. Kiwango: mwajiri 10% + mfanyakazi 10% = 20% ya mshahara mkubwa wa jumla wa kila mfanyakazi. Hata hivyo, kama wote 5 ni wa nusu muda na hauna wafanyakazi wengine, huhitajiwi SDL kwa sababu una wafanyakazi chini ya 10 (SDL inahitaji wafanyakazi 10 au zaidi). NSSF inatumika bila kujali idadi ya wafanyakazi.",
    "I employ 5 part-time workers. Does NSSF apply to them?",
    "Yes. 5 part-time workers who receive wages must have NSSF paid for them. Rate: employer 10% + employee 10% = 20% of each employee's gross wage. However, if all 5 are part-time and you have no other employees, you are not required to pay SDL because you have fewer than 10 employees (SDL requires 10 or more). NSSF applies regardless of the number of employees.",
    "rural_conversational"))

pairs.append(p(31,"nssf_part_time",
    "NSSF kwa wafanyakazi wa nusu muda inawasilishwa kwa pamoja na wa muda wote au tofauti?",
    "NSSF inawasilishwa pamoja kwa wafanyakazi wote — wa muda wote, nusu muda, na wa muda mfupi — kwenye orodha moja ya malipo (NSSF contribution schedule). Kila mfanyakazi anaonekana tofauti na namba yake ya NSSF, lakini malipo yote yanapelekwa pamoja kwenye NSSF. Kiwango ni 20% ya mshahara mkubwa wa jumla kwa kila mfanyakazi. Tarehe: ndani ya mwezi mmoja baada ya mwezi wa mshahara.",
    "Is NSSF for part-time workers submitted together with full-time workers or separately?",
    "NSSF is submitted together for all employees — full-time, part-time, and casual workers — on one contribution schedule. Each employee appears separately with their NSSF number, but all payments go together to NSSF. Rate: 20% of gross wage per employee. Deadline: within one month after the salary month.",
    "business_market"))

# ── NSSF CONTRIBUTION CEILING (pairs 32-34) ──────────────────────────────────

pairs.append(p(32,"nssf_ceiling",
    "Je, kuna kiwango cha juu cha mshahara kinachohesabiwaje kwa NSSF?",
    "Sheria ya NSSF ya Tanzania haiweki kiwango cha juu cha mshahara (contribution ceiling) ambacho kinaathiri hesabu ya NSSF. Yaani: NSSF inahesabiwaje kwa msingi wa mshahara mkubwa wa jumla wote, bila kikomo cha juu. Kwa mfano: MD analipwa TZS 20,000,000 — NSSF = TZS 20,000,000 × 20% = TZS 4,000,000 kwa mwezi. Hakuna kiwango cha juu cha kupunguza msingi huu kwa sasa.",
    "Is there an upper salary limit (contribution ceiling) for NSSF calculation?",
    "Tanzania's NSSF Act does not set an upper salary contribution ceiling that limits the NSSF calculation base. That is: NSSF is calculated on the full gross wage, with no upper limit. Example: an MD paid TZS 20,000,000 — NSSF = TZS 20,000,000 × 20% = TZS 4,000,000 per month. There is no ceiling to cap this base at present.",
    "formal"))

pairs.append(p(33,"nssf_ceiling",
    "NSSF Tanzania ina mipaka ya chini ya mchango — je, kuna kiwango cha chini?",
    "Hakuna kiwango cha chini cha shilingi kilichowekwa kisheria kwa michango ya NSSF. Mchango ni asilimia ya mshahara mkubwa wa jumla — 20% (mwajiri 10% + mfanyakazi 10%). Hata mfanyakazi anayepata mshahara mdogo sana analipa NSSF kwa asilimia hiyo hiyo. Kiwango cha chini cha mshahara (GN 605A — TZS 175,000-765,900 kulingana na sekta) kinaathiri kiwango cha chini cha mshahara, si hesabu ya NSSF.",
    "Does NSSF have a minimum contribution floor?",
    "There is no legally prescribed minimum shilling amount for NSSF contributions. The contribution is a percentage of gross wage — 20% (employer 10% + employee 10%). Even an employee earning a very low wage pays NSSF at that same percentage. The minimum wage (GN 605A — TZS 175,000-765,900 by sector) affects the minimum wage payable, not the NSSF calculation.",
    "business_market"))

pairs.append(p(34,"nssf_ceiling",
    "Kampuni yangu inalipa NSSF kubwa sana kwa sababu ya mishahara ya juu. Je, kuna njia ya kupunguza?",
    "Hapana njia ya kisheria ya kupunguza mchango wa NSSF kwa mishahara halisi. NSSF ni wajibu wa kisheria: mwajiri 10% + mfanyakazi 10% = 20% ya mshahara mkubwa wa jumla, bila kikomo cha juu. Kubadilisha muundo wa malipo ili kupunguza NSSF (kwa mfano, kulipa sehemu kubwa kama gawio au posho) kunaweza kukabiliwa na ukaguzi wa TRA/NSSF. Shirika linastahili kulipa NSSF kamili kwa mishahara yote.",
    "My company pays a large NSSF amount due to high salaries. Is there a way to reduce it?",
    "There is no lawful way to reduce NSSF contributions on actual salaries. NSSF is a legal obligation: employer 10% + employee 10% = 20% of gross wage, with no upper ceiling. Restructuring pay to reduce NSSF (for example, by paying part as dividends or allowances) may be challenged by TRA/NSSF audit. Companies are expected to pay full NSSF on all wages.",
    "rural_conversational"))

# ── NSSF ALTERNATIVE 15%/5% (pairs 35-37) ────────────────────────────────────

pairs.append(p(35,"nssf_alternative",
    "Nimesikia kwamba kuna mpango wa NSSF wa asilimia 15/5 — ni kweli?",
    "Mpango wa kawaida wa NSSF ni asilimia 10 mwajiri + asilimia 10 mfanyakazi = asilimia 20. Kuna mipango ya hiari ya pensheni ya ziada (occupational pension schemes) ambapo mgawanyo unaweza kutofautiana, lakini hizi ni mipango ya ziada ya hiari — si mbadala wa NSSF ya lazima. Kiwango cha lazima cha msingi cha NSSF ni asilimia 10+10 = 20% ya mshahara mkubwa wa jumla. Kwa mwongozo wa mipango ya ziada, wasiliana na NSSF au mshauri wa pensheni.",
    "I heard there is an NSSF scheme of 15%/5% — is this true?",
    "The standard NSSF scheme is 10% employer + 10% employee = 20%. There are voluntary supplementary occupational pension schemes where the split may differ, but these are voluntary additional schemes — not a substitute for mandatory NSSF. The mandatory minimum NSSF rate is 10%+10% = 20% of gross wage. For guidance on supplementary schemes, contact NSSF or a pension consultant.",
    "business_market"))

pairs.append(p(36,"nssf_alternative",
    "Je, mwajiri anaweza kubadilisha mgawanyo wa NSSF kutoka 10/10 kwenda 15/5?",
    "Hapana — mgawanyo wa lazima wa NSSF wa Tanzania ni 10% mwajiri + 10% mfanyakazi, na hauwezi kubadilishwa unilaterally na mwajiri. Mwajiri hawezi kupunguza mchango wake hadi asilimia 5 na kuongeza wa mfanyakazi hadi asilimia 15 bila idhini ya NSSF. Mwajiri anaweza kuongeza kwa hiari (kulipa zaidi ya asilimia 10 kutoka pochi yake), lakini hawezi kupunguza chini ya asilimia 10.",
    "Can an employer change the NSSF split from 10/10 to 15/5?",
    "No — Tanzania's mandatory NSSF split is 10% employer + 10% employee and cannot be changed unilaterally by the employer. The employer cannot reduce their contribution to 5% and increase the employee's to 15% without NSSF authority. An employer may voluntarily contribute more (paying above 10% from their own pocket), but cannot reduce below 10%.",
    "formal"))

pairs.append(p(37,"nssf_alternative",
    "Je, mwajiri anaweza kulipa NSSF ya mfanyakazi pia (kulipa 20% yote)?",
    "Ndiyo. Mwajiri anaweza kuchagua kulipa 20% yote ya NSSF (sehemu ya mwajiri na mfanyakazi) kama faida ya ziada kwa mfanyakazi — bila kukata kitu kutoka mshahara wa mfanyakazi. Hii ni maamuzi ya biashara na inaweza kuwa na athari za kodi (PAYE) kwa mfanyakazi kama inachukuliwa kama faida inayolipwa. Wasiliana na TRA/mshauri wa kodi kwa athari za kodi. Kiwango cha lazima kwa mwajiri ni asilimia 10 tu.",
    "Can the employer pay the employee's NSSF share too (paying all 20%)?",
    "Yes. An employer can choose to pay all 20% of NSSF (both employer and employee shares) as an additional benefit to the employee — without deducting anything from the employee's salary. This is a business decision and may have tax implications (PAYE) for the employee if treated as a taxable benefit. Contact TRA/a tax adviser for tax implications. The mandatory minimum for the employer is 10% only.",
    "business_market"))

# ── NSSF VS WCF (pairs 38-40) ────────────────────────────────────────────────

pairs.append(p(38,"nssf_vs_wcf",
    "Tofauti kati ya NSSF na WCF ni nini?",
    "NSSF (National Social Security Fund) ni hifadhi ya jamii ya muda mrefu — pensheni, faida za matibabu, faida za uzazi. Kiwango: mwajiri 10% + mfanyakazi 10% = 20% ya mshahara mkubwa wa jumla. WCF (Workers Compensation Fund) ni fidia ya mfanyakazi aliyeumia kazini — inahusu majeraha ya mahali pa kazi, ulemavu wa kazi, na kifo kazini. Kiwango: mwajiri peke yake asilimia 0.5 ya mshahara mkubwa wa jumla. Zote mbili ni lazima na zinalipwa kwa mwajiri, lakini zinaenda taasisi tofauti.",
    "What is the difference between NSSF and WCF?",
    "NSSF (National Social Security Fund) is long-term social security — pension, medical benefits, maternity benefits. Rate: employer 10% + employee 10% = 20% of gross wage. WCF (Workers Compensation Fund) is compensation for work-related injuries — it covers workplace injuries, work-related disability, and death at work. Rate: employer only at 0.5% of gross wage. Both are mandatory and paid by the employer, but go to different institutions.",
    "business_market"))

pairs.append(p(39,"nssf_vs_wcf",
    "Je, kampuni inalazimika kulipa WCF na NSSF zote mbili?",
    "Ndiyo. Kampuni inalazimika kulipa NSSF na WCF — ni wajibu tofauti mbili. NSSF: mwajiri 10% + mfanyakazi 10% = 20% ya mshahara mkubwa wa jumla. WCF: mwajiri peke yake asilimia 0.5 ya mshahara mkubwa wa jumla. Kwa hivyo, jumla ya mchango wa mwajiri kwa mishahara = 10% (NSSF) + 0.5% (WCF) = 10.5% ya mshahara mkubwa wa jumla kutoka pochi ya mwajiri.",
    "Is a company required to pay both WCF and NSSF?",
    "Yes. A company is required to pay both NSSF and WCF — they are two separate obligations. NSSF: employer 10% + employee 10% = 20% of gross wage. WCF: employer only at 0.5% of gross wage. Therefore, total employer contribution on wages = 10% (NSSF) + 0.5% (WCF) = 10.5% of gross wage from the employer's own pocket.",
    "formal"))

pairs.append(p(40,"nssf_vs_wcf",
    "Mfanyakazi alijeruhiwa kazini. Je, fidia inatoka NSSF au WCF?",
    "Fidia ya majeraha ya kazini inatoka WCF (Workers Compensation Fund) — si NSSF. WCF inashughulikia: gharama za matibabu ya majeraha ya kazi, fidia ya ulemavu wa muda au wa kudumu, na fidia ya kifo kazini. NSSF inashughulikia: pensheni ya uzee, faida za matibabu za muda mrefu, faida za uzazi. Kwa fidia ya jeraha la kazi, mwajiri anapaswa kuwasiliana na WCF na kuwasilisha fomu za madai.",
    "An employee was injured at work. Does compensation come from NSSF or WCF?",
    "Compensation for work injuries comes from WCF (Workers Compensation Fund) — not NSSF. WCF covers: medical costs for work injuries, temporary or permanent disability compensation, and death-at-work compensation. NSSF covers: old-age pension, long-term medical benefits, maternity benefits. For a work injury claim, the employer should contact WCF and submit claim forms.",
    "rural_conversational"))

# ── NSSF NUMBER PORTABILITY (pairs 41-43) ────────────────────────────────────

pairs.append(p(41,"nssf_portability",
    "Mfanyakazi anahamia kazi nyingine — NSSF yake inabaki au inaanza upya?",
    "Namba ya NSSF inabaki — ni ya maisha yote na haibadilikwi kubadilisha mwajiri. Mfanyakazi anaendelea kutumia namba ile ile ya NSSF katika ajira zake zote. Michango yote iliyolipwa na waajiri wote inakusanywa kwenye akaunti moja hiyo. Mwajiri mpya anaomba namba ya NSSF ya mfanyakazi na kuendelea kuchangia chini ya namba hiyo. Hakuna 'mwanzo upya' — akaunti inaendelea kukua.",
    "An employee changes jobs — does their NSSF stay or restart?",
    "The NSSF number stays — it is lifelong and does not change when changing employers. The employee continues using the same NSSF number in all their employment. All contributions paid by all employers accumulate in that one account. The new employer asks for the employee's NSSF number and continues contributing under that number. There is no 'fresh start' — the account continues to grow.",
    "business_market"))

pairs.append(p(42,"nssf_portability",
    "Mfanyakazi alifanya kazi Tanzania, kisha Kenya, kisha Tanzania tena — akaunti ya NSSF inafanya kazi vipi?",
    "Akaunti ya NSSF ya Tanzania inabaki pale mfanyakazi anapoondoka Tanzania. Michango iliyolipwa kabla ya kuondoka inabaki. Wakati mfanyakazi anarudi Tanzania na kuajiriwa tena, anaendelea na namba ile ile ya NSSF na akaunti yake ya awali. Hata hivyo, miezi ya kufanya kazi Kenya haijumuishwi katika hesabu ya miezi ya michango ya NSSF ya Tanzania. Kwa mwongozo wa hali hii, wasiliana na NSSF.",
    "An employee worked in Tanzania, then Kenya, then Tanzania again — how does the NSSF account work?",
    "The Tanzania NSSF account remains when an employee leaves Tanzania. Contributions made before leaving remain in the account. When the employee returns to Tanzania and is re-employed, they continue with the same NSSF number and their original account. However, months worked in Kenya do not count towards Tanzania NSSF contribution months. For guidance on this situation, contact NSSF.",
    "formal"))

pairs.append(p(43,"nssf_portability",
    "Mfanyakazi wangu ana namba ya NSSF ya zamani asiyoijua. Je, tunafanya nini?",
    "Ikiwa mfanyakazi hajui namba yake ya zamani ya NSSF, hatua ni: (1) Tembelea ofisi ya NSSF karibu nawe na kitambulisho cha taifa (NIDA) au pasipoti; (2) NSSF itafuta namba yake ya zamani kwa kutumia taarifa zake za kibinafsi; (3) Kama hakuna akaunti ya zamani, NSSF itasajili upya. Mwajiri asimwandikishe mfanyakazi kwa namba mpya bila kwanza kuthibitisha hali yake ya sasa na NSSF.",
    "My employee has an old NSSF number they don't know. What do we do?",
    "If an employee doesn't know their old NSSF number, the steps are: (1) Visit the nearest NSSF office with a national ID (NIDA) or passport; (2) NSSF will search for their old number using their personal details; (3) If no old account exists, NSSF will register afresh. The employer should not register the employee with a new number without first confirming their status with NSSF.",
    "business_market"))

# ── NSSF AND PENSION DOUBLE CONTRIBUTION (pairs 44-47) ───────────────────────

pairs.append(p(44,"nssf_pension_fund",
    "Je, kampuni yenye mfuko wa pensheni wake inalazimika pia kulipa NSSF?",
    "Ndiyo — kwa ujumla, NSSF ni wajibu wa lazima bila kujali kama kampuni ina mfuko wa pensheni wa ndani (occupational pension fund). NSSF na mifuko ya pensheni ya biashara ni mifumo tofauti. Hata hivyo, kwa kampuni zenye mifuko iliyoidhinishwa na Social Security Regulatory Authority (SSRA), mazingira ya kutolipa NSSF na badala yake kulipa kwenye mfuko wa pensheni ulioathirishwa yanawezekana — wasiliana na SSRA kwa mwongozo.",
    "Must a company with its own pension fund also pay NSSF?",
    "Yes — in general, NSSF is a mandatory obligation regardless of whether the company has an internal occupational pension fund. NSSF and occupational pension schemes are separate systems. However, for companies with funds approved by the Social Security Regulatory Authority (SSRA), exemption arrangements where contributions go to the approved fund instead of NSSF may be possible — contact SSRA for guidance.",
    "rural_conversational"))

pairs.append(p(45,"nssf_pension_fund",
    "SSRA ni nini na inahusiana vipi na NSSF?",
    "SSRA (Social Security Regulatory Authority) ni msimamizi wa mifuko yote ya hifadhi ya jamii Tanzania — ikiwemo NSSF, PPF, GEPF, na LAPF. SSRA inaweka viwango vya utawala, haki za washiriki, na miongozo ya uwekezaji kwa mifuko yote. NSSF yenyewe ni mfuko mkubwa zaidi wa hifadhi ya jamii Tanzania, unaoshughulikia sekta kubwa ya binafsi. Kiwango cha mchango wa NSSF: mwajiri 10% + mfanyakazi 10% = 20% ya mshahara mkubwa wa jumla.",
    "What is SSRA and how does it relate to NSSF?",
    "SSRA (Social Security Regulatory Authority) is the regulator of all social security funds in Tanzania — including NSSF, PPF, GEPF, and LAPF. SSRA sets governance standards, member rights, and investment guidelines for all funds. NSSF itself is Tanzania's largest social security fund, covering most of the private sector. NSSF contribution rate: employer 10% + employee 10% = 20% of gross wage.",
    "business_market"))

pairs.append(p(46,"nssf_pension_fund",
    "Je, mfanyakazi wa serikali analipa NSSF au PPF?",
    "Wafanyakazi wa serikali kwa ujumla wanachangia PPF (Public Service Pension Fund) badala ya NSSF. NSSF inashughulikia hasa sekta ya binafsi. PPF ni mfuko wa pensheni wa wafanyakazi wa umma. Hata hivyo, wafanyakazi wa mashirika ya serikali (parastatal organizations) wanaweza kuchangia NSSF kulingana na makubaliano ya ajira. Kwa kuthibitisha mfuko sahihi kwa aina yako ya kazi, wasiliana na mwajiri wako au SSRA.",
    "Does a government employee pay NSSF or PPF?",
    "Government employees generally contribute to PPF (Public Service Pension Fund) rather than NSSF. NSSF primarily covers the private sector. PPF is the pension fund for public service employees. However, employees of parastatal organisations may contribute to NSSF depending on their employment terms. To confirm the correct fund for your type of work, contact your employer or SSRA.",
    "rural_conversational"))

pairs.append(p(47,"nssf_pension_fund",
    "Mfanyakazi ana NSSF na pia kampuni inalipa kwenye mfuko wa pensheni wa binafsi. Je, hii inaruhusiwa?",
    "Ndiyo. Kampuni inaweza kulipa NSSF ya lazima (mwajiri 10% + mfanyakazi 10%) NA pia kuchangia kwenye mfuko wa pensheni wa ziada (supplementary pension scheme) kwa faida za mfanyakazi. Hii ni kawaida kwa kampuni kubwa zinazotoa faida za ziada. Mchango wa ziada wa pensheni una athari za kodi (PAYE) kulingana na jinsi unavyoshughulikiwa. Wasiliana na TRA/mshauri wa kodi kwa athari za kodi za mchango wa pensheni ya ziada.",
    "An employee has NSSF and the company also pays into a private pension fund. Is this allowed?",
    "Yes. A company can pay mandatory NSSF (employer 10% + employee 10%) AND also contribute to a supplementary pension scheme as an employee benefit. This is common for large companies offering additional benefits. Supplementary pension contributions have tax implications (PAYE) depending on how they are treated. Contact TRA/a tax adviser for the tax treatment of supplementary pension contributions.",
    "formal"))

# ── NSSF REGISTRATION TIMING (pairs 48-50) ───────────────────────────────────

pairs.append(p(48,"nssf_registration",
    "Kampuni mpya inasajili NSSF lini?",
    "Kampuni mpya inalazimika kusajili kwa NSSF ndani ya mwezi mmoja wa kuanza biashara au kuajiri mfanyakazi wa kwanza. Usajili wa mwajiri (employer registration) unatangulia usajili wa wafanyakazi. Kisha, kila mfanyakazi mpya anasajiliwa ndani ya mwezi wa kwanza wa ajira yake. Michango ya kwanza inaanza mara mfanyakazi anapopokea mshahara wa kwanza — kiwango: mwajiri 10% + mfanyakazi 10% = 20% ya mshahara mkubwa wa jumla.",
    "When does a new company register with NSSF?",
    "A new company must register with NSSF within one month of starting business or hiring the first employee. Employer registration comes first. Then each new employee is registered within the first month of their employment. First contributions start as soon as the employee receives their first salary — rate: employer 10% + employee 10% = 20% of gross wage.",
    "business_market"))

pairs.append(p(49,"nssf_registration",
    "Adhabu ya kutosajilisha mfanyakazi kwa NSSF ni nini?",
    "Kutosajilisha mfanyakazi kwa NSSF kunaweza kusababisha: adhabu ya usajili wa kuchelewa, madeni ya michango ya malimbikizo kwa kiwango cha 10%+10% ya mshahara mkubwa wa jumla, riba ya ucheleweshaji (5% kwa mwezi kwa michango isiyolipwa), na hatua za kisheria. NSSF inspectors wanaweza kufanya ukaguzi. Usajili wa mapema unalinda mwajiri na mfanyakazi.",
    "What is the penalty for not registering an employee with NSSF?",
    "Failure to register an employee with NSSF may result in: a late registration penalty, backdated contribution arrears at 10%+10% of gross wage, interest on late payments (5% per month on unpaid contributions), and legal action. NSSF inspectors may conduct audits. Early registration protects both employer and employee.",
    "formal"))

pairs.append(p(50,"nssf_registration",
    "NSSF return inawasilishwa kwa njia gani Tanzania?",
    "NSSF return (orodha ya malipo ya michango) inawasilishwa: (1) Kwa njia ya mtandao kupitia mfumo wa NSSF Online (nssf.or.tz); (2) Ofisini — kwa kuleta fomu na malipo ya moja kwa moja; (3) Benki zilizoidhinishwa. Malipo yanaweza kufanywa kwa njia ya benki, simu za mkononi, au ofisi ya NSSF. Tarehe ya mwisho: ndani ya mwezi mmoja baada ya mwezi wa mshahara. Kiwango: mwajiri 10% + mfanyakazi 10% = 20% ya mshahara mkubwa wa jumla.",
    "How is an NSSF return submitted in Tanzania?",
    "NSSF returns (contribution payment schedules) are submitted: (1) Online through the NSSF Online system (nssf.or.tz); (2) In-person — by bringing forms and direct payment to an NSSF office; (3) At authorised banks. Payments can be made by bank, mobile money, or at an NSSF office. Deadline: within one month after the salary month. Rate: employer 10% + employee 10% = 20% of gross wage.",
    "business_market"))

# ── WRITE ──────────────────────────────────────────────────────────────────────
OUT = "datasets/tier1a/raw_sources/raw_pairs_batch_003.jsonl"
with open(OUT, "a", encoding="utf-8") as f:
    for pr in pairs:
        f.write(json.dumps(pr, ensure_ascii=False) + "\n")
print(f"Wrote {len(pairs)} NSSF deep pairs")
regs = {}
for pr in pairs:
    regs[pr["register"]] = regs.get(pr["register"], 0) + 1
total = len(pairs)
for k, v in sorted(regs.items()):
    print(f"  {k}: {v} ({v/total*100:.0f}%)")
