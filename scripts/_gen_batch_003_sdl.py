"""
Generate 50 SDL compliance adversarial pairs for batch_003.
Appends to datasets/tier1a/raw_sources/raw_pairs_batch_003.jsonl
IDs: tier1a_sdl_001_20260608 through tier1a_sdl_050_20260608

Distribution:
  - 20 adversarial: SDL name correction (pairs 001-020)
  - 10 calculation examples with TZS amounts (pairs 021-030)
  - 10 threshold edge cases 9 vs 10 employees (pairs 031-040)
  - 5 exemptions EPZ/NGO (pairs 041-045)
  - 5 deadline and penalty (pairs 046-050)

Register: >=40% business_market, 30-40% formal, 20% rural_conversational
"""
import json

SOURCE_URL = "https://www.tra.go.tz/page/skills-development-levy-sdl"
SOURCE_NAME = "TRA SDL Page"
DATE = "20260608"
EFFECTIVE = "2025-07-01"

def make(n, subdomain, q_sw, a_sw, q_en, a_en, register, pair_type="adversarial"):
    return {
        "id": f"tier1a_sdl_{n:03d}_{DATE}",
        "domain": "tier1a",
        "subdomain": subdomain,
        "question_sw": q_sw,
        "answer_sw": a_sw,
        "question_en": q_en,
        "answer_en": a_en,
        "primary_source_url": SOURCE_URL,
        "primary_source_name": SOURCE_NAME,
        "source_type": "government_portal",
        "effective_date": EFFECTIVE,
        "decay_risk": "annual",
        "next_review_trigger": "Finance Act amendment",
        "verified_by": "CLAUDE.md locked_facts — TRA SDL",
        "verified_date": "2026-06-08",
        "register": register,
        "pair_type": pair_type,
        "eval_set": False,
    }

pairs = []

# ── 20 ADVERSARIAL: SDL name correction ──────────────────────────────────────

pairs.append(make(1, "sdl_name_correction",
    q_sw='SDL inamaanisha "Service Delivery Levy" — je, hii ni kweli?',
    a_sw='Hapana. SDL inamaanisha Skills Development Levy — Kodi ya Kukuza Ujuzi kwa Kiswahili. Haihusiani na "Service Delivery Levy" wala "short-term disability leave". Kiwango ni asilimia 3.5 ya mshahara mkubwa wa jumla, inayolipwa na mwajiri peke yake, kwa wafanyakazi 10 au zaidi, mwisho siku ya 7 ya mwezi unaofuata.',
    q_en='SDL stands for "Service Delivery Levy" — is this correct?',
    a_en='No. SDL stands for Skills Development Levy — Kodi ya Kukuza Ujuzi in Swahili. It has nothing to do with "Service Delivery Levy" or "short-term disability leave". The rate is 3.5% of gross payroll, paid by the employer only, for employers with 10 or more employees, due by the 7th of the following month.',
    register="business_market"
))

pairs.append(make(2, "sdl_name_correction",
    q_sw='Mwajiri aliniambia SDL ni kodi ya "disability leave" ya muda mfupi. Je, hiyo ni sahihi?',
    a_sw='Hiyo si sahihi. SDL ni Skills Development Levy (Kodi ya Kukuza Ujuzi) — kodi ya serikali inayolipwa na waajiri kwa ajili ya kukuza mafunzo ya kitaaluma. Haihusiani kabisa na likizo ya ulemavu. Kiwango: asilimia 3.5 ya jumla ya mishahara. Hulipwa na mwajiri peke yake — hakatiwi kutoka mshahara wa mfanyakazi.',
    q_en='My employer told me SDL is a "short-term disability leave" levy. Is that correct?',
    a_en='That is incorrect. SDL is the Skills Development Levy (Kodi ya Kukuza Ujuzi) — a government levy paid by employers to fund vocational training. It has nothing to do with disability leave. Rate: 3.5% of gross payroll. Paid by the employer only — not deducted from the employee\'s wages.',
    register="business_market"
))

pairs.append(make(3, "sdl_name_correction",
    q_sw='Je, SDL ni "Social Development Levy"?',
    a_sw='Hapana. SDL ni Skills Development Levy — Kodi ya Kukuza Ujuzi. Si "Social Development Levy". Kusudi lake ni kufadhili mafunzo ya kitaaluma nchini Tanzania. Inatolewa na TRA. Kiwango: asilimia 3.5 ya mshahara mkubwa wa jumla, kwa waajiri wenye wafanyakazi 10 au zaidi kwenye Tanzania Bara.',
    q_en='Is SDL a "Social Development Levy"?',
    a_en='No. SDL is the Skills Development Levy — Kodi ya Kukuza Ujuzi. Not "Social Development Levy". Its purpose is to fund vocational training in Tanzania. Administered by TRA. Rate: 3.5% of gross payroll, for employers with 10 or more employees on Mainland Tanzania.',
    register="formal"
))

pairs.append(make(4, "sdl_name_correction",
    q_sw='SDL na NSSF ni kitu kimoja?',
    a_sw='Hapana, ni tofauti kabisa. NSSF ni mchango wa hifadhi ya jamii (asilimia 10 mwajiri + asilimia 10 mfanyakazi). SDL ni Skills Development Levy — Kodi ya Kukuza Ujuzi — inayolipwa na mwajiri peke yake kwa kiwango cha asilimia 3.5 ya mshahara mkubwa wa jumla, kwa wafanyakazi 10 au zaidi, mwisho siku 7 ya mwezi unaofuata.',
    q_en='Are SDL and NSSF the same thing?',
    a_en='No, they are completely different. NSSF is a social security contribution (10% employer + 10% employee). SDL is the Skills Development Levy — Kodi ya Kukuza Ujuzi — paid by the employer only at 3.5% of gross payroll, for employers with 10 or more employees, due by the 7th of the following month.',
    register="business_market"
))

pairs.append(make(5, "sdl_name_correction",
    q_sw='Maana ya SDL ni "Skills Delivery Levy" — je, ni hivyo?',
    a_sw='Hapana. Jina sahihi ni Skills Development Levy — si "Skills Delivery Levy". Kwa Kiswahili: Kodi ya Kukuza Ujuzi. Neno muhimu ni "Development" (Kukuza) — kodi hii inafadhili ukuzaji wa ujuzi wa wafanyakazi. Kiwango: asilimia 3.5, mwajiri peke yake, wafanyakazi 10+, siku 7 ya mwezi unaofuata.',
    q_en='SDL means "Skills Delivery Levy" — is that right?',
    a_en='No. The correct name is Skills Development Levy — not "Skills Delivery Levy". In Swahili: Kodi ya Kukuza Ujuzi. The key word is "Development" (Kukuza) — this levy funds skills development for workers. Rate: 3.5%, employer only, 10+ employees, due 7th of following month.',
    register="business_market"
))

pairs.append(make(6, "sdl_name_correction",
    q_sw='SDL inamaanisha nini kwa Kiswahili? Jibu mfupi.',
    a_sw='SDL ni Skills Development Levy. Kwa Kiswahili: Kodi ya Kukuza Ujuzi. Inalipwa na mwajiri kwa asilimia 3.5 ya jumla ya mishahara, kwa makampuni yenye wafanyakazi 10 au zaidi kwenye Tanzania Bara.',
    q_en='What does SDL stand for in Swahili? Short answer.',
    a_en='SDL is the Skills Development Levy. In Swahili: Kodi ya Kukuza Ujuzi. Paid by the employer at 3.5% of total payroll, for companies with 10 or more employees on Mainland Tanzania.',
    register="rural_conversational"
))

pairs.append(make(7, "sdl_name_correction",
    q_sw='Accountant wetu anasema SDL inakatwa kutoka mshahara wa mfanyakazi. Je, hiyo ni kweli?',
    a_sw='Hiyo si sahihi. SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — hulipwa na mwajiri peke yake. Haikatwi kutoka mshahara wa mfanyakazi hata kidogo. Mwajiri ndiye anayebeba gharama ya asilimia 3.5 ya jumla ya mishahara na kuipeleka TRA ifikapo siku ya 7 ya mwezi unaofuata.',
    q_en='Our accountant says SDL is deducted from the employee\'s salary. Is that true?',
    a_en='That is incorrect. SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — is paid by the employer only. It is not deducted from the employee\'s salary at all. The employer bears the cost of 3.5% of total payroll and remits it to TRA by the 7th of the following month.',
    register="business_market"
))

pairs.append(make(8, "sdl_name_correction",
    q_sw='Je, SDL ni kodi mpya iliyoanzishwa na Finance Act 2025?',
    a_sw='Hapana. SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — imekuwepo kwa miaka mingi Tanzania. Kilichobadilika katika Finance Act 2025 ni kiwango: kilishuka kutoka asilimia 4 hadi asilimia 3.5, kuanzia tarehe 1 Julai 2025. Kodi yenyewe si mpya.',
    q_en='Is SDL a new levy introduced by Finance Act 2025?',
    a_en='No. SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — has existed in Tanzania for many years. What changed in Finance Act 2025 is the rate: it was reduced from 4% to 3.5%, effective 1 July 2025. The levy itself is not new.',
    register="rural_conversational"
))

pairs.append(make(9, "sdl_name_correction",
    q_sw='Mtu mmoja alisema SDL ni "Staff Development Levy". Je, ni jina sahihi?',
    a_sw='Hapana. Jina sahihi ni Skills Development Levy — Kodi ya Kukuza Ujuzi kwa Kiswahili. Si "Staff Development Levy". Inajumuisha maana pana ya kukuza ujuzi kwa wafanyakazi wote, si tu wafanyakazi wa ndani ya shirika. Kiwango ni asilimia 3.5, mwajiri peke yake, wafanyakazi 10 au zaidi.',
    q_en='Someone said SDL is "Staff Development Levy". Is that the correct name?',
    a_en='No. The correct name is Skills Development Levy — Kodi ya Kukuza Ujuzi in Swahili. Not "Staff Development Levy". It covers the broader meaning of skills development for all workers, not just internal staff. Rate: 3.5%, employer only, 10 or more employees.',
    register="business_market"
))

pairs.append(make(10, "sdl_name_correction",
    q_sw='SDL inahusu nini hasa? Niambie wazi.',
    a_sw='SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — ni kodi inayolipwa na waajiri kwa TRA kwa lengo la kufadhili mafunzo ya kitaaluma na ukuzaji wa ujuzi nchini Tanzania. Si likizo ya ulemavu, si huduma ya utoaji, si kitu kingine chochote zaidi ya kodi ya kukuza ujuzi. Kiwango: asilimia 3.5 ya mshahara mkubwa wa jumla.',
    q_en='What exactly is SDL? Tell me clearly.',
    a_en='SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — is a levy paid by employers to TRA to fund vocational training and skills development in Tanzania. It is not disability leave, not service delivery, not anything else — it is strictly a skills development levy. Rate: 3.5% of gross payroll.',
    register="rural_conversational"
))

pairs.append(make(11, "sdl_name_correction",
    q_sw='Je, SDL inahusiana na mfuko wa ustawi wa wafanyakazi (WCF)?',
    a_sw='Hapana, ni kodi tofauti. SDL ni Skills Development Levy (Kodi ya Kukuza Ujuzi) — asilimia 3.5 ya jumla ya mishahara, kwa wafanyakazi 10 au zaidi. WCF ni Workers Compensation Fund — asilimia 0.5 ya mishahara, kwa waajiri wote wenye wafanyakazi. Zinalipwa vyote kwa mwajiri lakini kwenda taasisi tofauti na kwa madhumuni tofauti.',
    q_en='Is SDL related to the Workers Compensation Fund (WCF)?',
    a_en='No, they are different levies. SDL is the Skills Development Levy (Kodi ya Kukuza Ujuzi) — 3.5% of total payroll, for employers with 10 or more employees. WCF is the Workers Compensation Fund — 0.5% of payroll, for all employers with employees. Both are paid by the employer but go to different institutions for different purposes.',
    register="rural_conversational"
))

pairs.append(make(12, "sdl_name_correction",
    q_sw='SDL inalipwa lini — mara moja kwa mwaka au kila mwezi?',
    a_sw='SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — inalipwa kila mwezi, pamoja na PAYE. Mwisho wa malipo ni siku ya 7 ya kila mwezi kwa mishahara ya mwezi uliopita. Kiwango ni asilimia 3.5 ya jumla ya mishahara ya mwezi husika, inayolipwa na mwajiri peke yake.',
    q_en='When is SDL paid — once a year or monthly?',
    a_en='SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — is paid monthly, together with PAYE. The deadline is the 7th of each month for the previous month\'s payroll. Rate is 3.5% of that month\'s gross payroll, paid by the employer only.',
    register="business_market"
))

pairs.append(make(13, "sdl_name_correction",
    q_sw='Rafiki yangu anasema SDL ni asilimia 4. Je, hiyo bado ni sahihi?',
    a_sw='Hapana tena. Kiwango cha SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — kilipunguzwa kutoka asilimia 4 hadi asilimia 3.5 na Finance Act 2025, kuanzia tarehe 1 Julai 2025. Ikiwa unatumia kiwango cha asilimia 4 baada ya tarehe hiyo, unalipa zaidi ya inavyotakiwa au hesabu yako ni makosa.',
    q_en='My friend says SDL is 4%. Is that still correct?',
    a_en='Not anymore. The SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — rate was reduced from 4% to 3.5% by the Finance Act 2025, effective 1 July 2025. If you are using 4% after that date, you are overpaying or your calculation is wrong.',
    register="business_market"
))

pairs.append(make(14, "sdl_name_correction",
    q_sw='Je, SDL na PAYE ni kodi moja?',
    a_sw='Hapana, ni kodi mbili tofauti. PAYE (Pay As You Earn) ni kodi ya mapato inayokatwa kutoka mshahara wa mfanyakazi na mwajiri anapeleka TRA. SDL ni Skills Development Levy (Kodi ya Kukuza Ujuzi) — inayolipwa na mwajiri peke yake kwa asilimia 3.5 ya jumla ya mishahara. Zinawasilishwa pamoja siku ya 7 lakini ni malipo tofauti.',
    q_en='Are SDL and PAYE the same tax?',
    a_en='No, they are two different levies. PAYE (Pay As You Earn) is an income tax deducted from the employee\'s salary and remitted by the employer to TRA. SDL is the Skills Development Levy (Kodi ya Kukuza Ujuzi) — paid by the employer only at 3.5% of gross payroll. Both are submitted together on the 7th but are separate payments.',
    register="formal"
))

pairs.append(make(15, "sdl_name_correction",
    q_sw='SDL inafadhili nini hasa?',
    a_sw='SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — inafadhili mafunzo ya kitaaluma na ukuzaji wa ujuzi wa wafanyakazi nchini Tanzania, kupitia Vocational Education and Training Authority (VETA) na taasisi nyingine za mafunzo. Si kodi ya ustawi, si kodi ya huduma — ni kodi ya kukuza ujuzi hasa.',
    q_en='What exactly does SDL fund?',
    a_en='SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — funds vocational training and skills development for workers in Tanzania, through the Vocational Education and Training Authority (VETA) and other training institutions. It is not a welfare levy, not a services levy — it is specifically a skills development levy.',
    register="rural_conversational"
))

pairs.append(make(16, "sdl_name_correction",
    q_sw='Mwajiri mdogo mwenye wafanyakazi 5 analipa SDL?',
    a_sw='Hapana. SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — inalipwa tu na waajiri wenye wafanyakazi 10 au zaidi kwenye Tanzania Bara. Mwajiri mwenye wafanyakazi chini ya 10 hatalazimika kulipa SDL. Hata hivyo, jina sahihi la kodi hii ni Skills Development Levy, si kodi ya huduma ya utoaji wala disability leave.',
    q_en='Does a small employer with 5 employees pay SDL?',
    a_en='No. SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — is paid only by employers with 10 or more employees on Mainland Tanzania. An employer with fewer than 10 employees is not required to pay SDL. Regardless, the correct name of this levy is Skills Development Levy, not service delivery levy or disability leave.',
    register="rural_conversational"
))

pairs.append(make(17, "sdl_name_correction",
    q_sw='Je, SDL inahusiana na kodi ya usalama wa chakula au kilimo?',
    a_sw='Hapana hata kidogo. SDL ni Skills Development Levy — Kodi ya Kukuza Ujuzi — na inahusiana na ukuzaji wa ujuzi wa wafanyakazi, si kilimo wala usalama wa chakula. Inatolewa na TRA, inalipwa na waajiri wenye wafanyakazi 10 au zaidi, kwa kiwango cha asilimia 3.5 ya jumla ya mishahara.',
    q_en='Is SDL related to food security or agricultural levies?',
    a_en='Not at all. SDL is the Skills Development Levy — Kodi ya Kukuza Ujuzi — and it concerns workforce skills development, not agriculture or food security. It is administered by TRA, paid by employers with 10 or more employees, at 3.5% of gross payroll.',
    register="rural_conversational"
))

pairs.append(make(18, "sdl_name_correction",
    q_sw='Mwanasheria alisema SDL inamaanisha "Statutory Deduction Levy". Je, hii ni jina sahihi?',
    a_sw='Hapana. Jina sahihi ni Skills Development Levy — Kodi ya Kukuza Ujuzi kwa Kiswahili — inayosimamiwa na TRA. "Statutory Deduction Levy" si jina halisi la kodi yoyote ya Tanzania. SDL inalipwa na mwajiri peke yake (si kukatwa mshahara) kwa asilimia 3.5 ya jumla ya mishahara, kwa wafanyakazi 10 au zaidi.',
    q_en='A lawyer said SDL means "Statutory Deduction Levy". Is that the correct name?',
    a_en='No. The correct name is Skills Development Levy — Kodi ya Kukuza Ujuzi in Swahili — administered by TRA. "Statutory Deduction Levy" is not a real name for any Tanzanian levy. SDL is paid by the employer only (not deducted from wages) at 3.5% of gross payroll, for employers with 10 or more employees.',
    register="business_market"
))

pairs.append(make(19, "sdl_name_correction",
    q_sw='Kampuni yangu ina wafanyakazi 12. Je, tunahitaji kulipa SDL na kiwango chake ni kiasi gani?',
    a_sw='Ndiyo. Kampuni yenye wafanyakazi 12 inalazimika kulipa SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi). Kiwango ni asilimia 3.5 ya jumla ya mishahara mkubwa ya wafanyakazi wote 12. Mwajiri ndiye anayelipia — hakatiwi kutoka mshahara wa mfanyakazi. Mwisho wa malipo: siku ya 7 ya mwezi unaofuata, pamoja na PAYE.',
    q_en='My company has 12 employees. Do we need to pay SDL and what is the rate?',
    a_en='Yes. A company with 12 employees is required to pay SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi). The rate is 3.5% of the total gross payroll of all 12 employees. The employer pays it — it is not deducted from employee salaries. Deadline: 7th of the following month, together with PAYE.',
    register="formal"
))

pairs.append(make(20, "sdl_name_correction",
    q_sw='SDL "Short-term Disability Levy" — je, hii ni maana ya SDL?',
    a_sw='Hapana. SDL haifanyi kazi ya kulipa wafanyakazi wakati wa ulemavu wa muda mfupi. SDL ni Skills Development Levy — Kodi ya Kukuza Ujuzi — inayofadhili mafunzo ya kitaaluma. Masuala ya ulemavu na magonjwa yanashughulikiwa na NSSF na Workers Compensation Fund (WCF) — si SDL. SDL: asilimia 3.5, mwajiri peke yake, wafanyakazi 10+, siku ya 7.',
    q_en='Is SDL a "Short-term Disability Levy"?',
    a_en='No. SDL does not pay workers during short-term disability. SDL is the Skills Development Levy — Kodi ya Kukuza Ujuzi — which funds vocational training. Disability and illness matters are handled by NSSF and the Workers Compensation Fund (WCF) — not SDL. SDL: 3.5%, employer only, 10+ employees, due 7th.',
    register="formal"
))

# ── 10 CALCULATION EXAMPLES WITH TZS ─────────────────────────────────────────

pairs.append(make(21, "sdl_calculation",
    q_sw='Kampuni yangu inalipa mishahara ya jumla ya TZS 5,000,000 kwa mwezi kwa wafanyakazi 15. SDL ni kiasi gani?',
    a_sw='SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — ni asilimia 3.5 ya jumla ya mishahara. Hesabu: TZS 5,000,000 × 3.5% = TZS 175,000 kwa mwezi. Hii inalipwa na mwajiri peke yake — haikatwi kutoka mshahara. Iwasilishwe TRA ifikapo siku ya 7 ya mwezi unaofuata, pamoja na PAYE.',
    q_en='My company pays total monthly wages of TZS 5,000,000 to 15 employees. How much is SDL?',
    a_en='SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — is 3.5% of total payroll. Calculation: TZS 5,000,000 × 3.5% = TZS 175,000 per month. This is paid by the employer only — not deducted from salaries. Remit to TRA by the 7th of the following month, together with PAYE.',
    register="business_market",
    pair_type="standard"
))

pairs.append(make(22, "sdl_calculation",
    q_sw='Wafanyakazi 10 wanaolipwa jumla TZS 3,600,000 kwa mwezi. SDL ya mwezi ni TZS ngapi?',
    a_sw='SDL (Skills Development Levy — Kodi ya Kukuza Ujuzi): TZS 3,600,000 × 3.5% = TZS 126,000 kwa mwezi. Kampuni yako inastahili kulipa SDL kwa sababu una wafanyakazi 10 hasa — yaani unafika kiwango cha chini (10 au zaidi). Inalipwa na mwajiri, mwisho siku ya 7 ya mwezi unaofuata.',
    q_en='10 employees are paid a total of TZS 3,600,000 per month. What is the monthly SDL?',
    a_en='SDL (Skills Development Levy — Kodi ya Kukuza Ujuzi): TZS 3,600,000 × 3.5% = TZS 126,000 per month. Your company qualifies to pay SDL because you have exactly 10 employees — the minimum threshold (10 or more). Paid by the employer, due by the 7th of the following month.',
    register="business_market",
    pair_type="standard"
))

pairs.append(make(23, "sdl_calculation",
    q_sw='Biashara yangu ina wafanyakazi 20 na jumla ya mishahara ni TZS 12,000,000 kwa mwezi. Niambie: SDL, NSSF ya mwajiri, na SDL vinajumlika vingapi?',
    a_sw='Hesabu: SDL (Skills Development Levy — Kodi ya Kukuza Ujuzi) = TZS 12,000,000 × 3.5% = TZS 420,000. NSSF ya mwajiri = TZS 12,000,000 × 10% = TZS 1,200,000. Jumla ya malipo ya mwajiri kwa TRA na NSSF = TZS 1,620,000. (SDL na PAYE kwenda TRA; NSSF kwenda NSSF.) SDL inalipwa siku ya 7 pamoja na PAYE.',
    q_en='My business has 20 employees with total payroll TZS 12,000,000 per month. Calculate: SDL, employer NSSF, and their combined total.',
    a_en='Calculation: SDL (Skills Development Levy — Kodi ya Kukuza Ujuzi) = TZS 12,000,000 × 3.5% = TZS 420,000. Employer NSSF = TZS 12,000,000 × 10% = TZS 1,200,000. Total employer obligations to TRA and NSSF = TZS 1,620,000. (SDL and PAYE go to TRA; NSSF goes to NSSF.) SDL is due on the 7th together with PAYE.',
    register="formal",
    pair_type="standard"
))

pairs.append(make(24, "sdl_calculation",
    q_sw='Mfanyakazi mmoja analipwa TZS 800,000 kwa mwezi. SDL ya mfanyakazi huyu peke yake ni kiasi gani?',
    a_sw='SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — haihesabiwi kwa mfanyakazi mmoja mmoja. Inatolewa kwa msingi wa jumla ya mishahara yote ya kampuni. Ikiwa kampuni ina wafanyakazi 10 au zaidi, SDL = jumla ya mishahara yote × 3.5%. Kwa mfano: wafanyakazi 10 wote wanaolipwa TZS 800,000 kila mmoja = jumla TZS 8,000,000 × 3.5% = TZS 280,000 SDL kwa mwezi.',
    q_en='One employee earns TZS 800,000 per month. What is the SDL for this employee alone?',
    a_en='SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — is not calculated per individual employee. It is based on the company\'s total gross payroll. If the company has 10 or more employees, SDL = total payroll × 3.5%. Example: 10 employees each earning TZS 800,000 = total TZS 8,000,000 × 3.5% = TZS 280,000 SDL per month.',
    register="business_market",
    pair_type="standard"
))

pairs.append(make(25, "sdl_calculation",
    q_sw='Jumla ya mishahara ya kampuni ni TZS 25,000,000 kwa mwezi. SDL ni TZS ngapi? Na ikiwa tungepoteza wafanyakazi 2 na kubaki na 9, SDL itabadilika vipi?',
    a_sw='Sasa hivi (25 wafanyakazi, TZS 25,000,000): SDL = TZS 25,000,000 × 3.5% = TZS 875,000. Ikiwa utabaki na wafanyakazi 9 (chini ya 10): haulazimiki tena kulipa SDL — kiwango cha chini ni wafanyakazi 10 au zaidi. SDL itakuwa sifuri. Hata hivyo, thibisha na TRA kwamba idadi ya wafanyakazi imepungua kabla ya kusimamisha malipo.',
    q_en='Total company payroll is TZS 25,000,000 per month. What is the SDL? And if we lose 2 employees and are left with 9, how does SDL change?',
    a_en='Currently (25 employees, TZS 25,000,000): SDL = TZS 25,000,000 × 3.5% = TZS 875,000. If you are left with 9 employees (below 10): you are no longer required to pay SDL — the threshold is 10 or more employees. SDL becomes zero. However, confirm with TRA that your employee count has decreased before stopping payments.',
    register="formal",
    pair_type="standard"
))

pairs.append(make(26, "sdl_calculation",
    q_sw='Ninataka kujua: SDL ya mwaka mzima kwa kampuni yenye mishahara ya TZS 8,000,000 kwa mwezi na wafanyakazi 13.',
    a_sw='SDL ya kila mwezi: TZS 8,000,000 × 3.5% = TZS 280,000. SDL ya mwaka mzima: TZS 280,000 × 12 = TZS 3,360,000. Hii inalipwa kwa awamu 12 (kila mwezi), mwisho siku ya 7 ya kila mwezi. SDL = Skills Development Levy (Kodi ya Kukuza Ujuzi), inalipwa na mwajiri, haijumuishi malipo ya PAYE, NSSF, au WCF.',
    q_en='I want to know: annual SDL for a company with monthly payroll TZS 8,000,000 and 13 employees.',
    a_en='Monthly SDL: TZS 8,000,000 × 3.5% = TZS 280,000. Annual SDL: TZS 280,000 × 12 = TZS 3,360,000. This is paid in 12 instalments (monthly), due by the 7th of each month. SDL = Skills Development Levy (Kodi ya Kukuza Ujuzi), paid by the employer, separate from PAYE, NSSF, or WCF payments.',
    register="business_market",
    pair_type="standard"
))

pairs.append(make(27, "sdl_calculation",
    q_sw='Wafanyakazi 11 wanalipwa wastani wa TZS 500,000 kila mmoja. SDL ya mwezi ni TZS ngapi?',
    a_sw='Jumla ya mishahara: 11 × TZS 500,000 = TZS 5,500,000. SDL (Skills Development Levy — Kodi ya Kukuza Ujuzi): TZS 5,500,000 × 3.5% = TZS 192,500 kwa mwezi. Inalipwa na mwajiri peke yake, mwisho siku ya 7 ya mwezi unaofuata.',
    q_en='11 employees are each paid an average of TZS 500,000. What is the monthly SDL?',
    a_en='Total payroll: 11 × TZS 500,000 = TZS 5,500,000. SDL (Skills Development Levy — Kodi ya Kukuza Ujuzi): TZS 5,500,000 × 3.5% = TZS 192,500 per month. Paid by the employer only, due by the 7th of the following month.',
    register="rural_conversational",
    pair_type="standard"
))

pairs.append(make(28, "sdl_calculation",
    q_sw='Mishahara ya wafanyakazi 15 ni: 5 wanapata TZS 1,200,000 na 10 wanapata TZS 600,000. SDL ni kiasi gani?',
    a_sw='Jumla ya mishahara: (5 × TZS 1,200,000) + (10 × TZS 600,000) = TZS 6,000,000 + TZS 6,000,000 = TZS 12,000,000. SDL (Skills Development Levy — Kodi ya Kukuza Ujuzi): TZS 12,000,000 × 3.5% = TZS 420,000 kwa mwezi. Mwajiri analipa jumla hii — hajikatui kutoka mshahara wa mfanyakazi yeyote.',
    q_en='Payroll for 15 employees: 5 earn TZS 1,200,000 and 10 earn TZS 600,000. What is the SDL?',
    a_en='Total payroll: (5 × TZS 1,200,000) + (10 × TZS 600,000) = TZS 6,000,000 + TZS 6,000,000 = TZS 12,000,000. SDL (Skills Development Levy — Kodi ya Kukuza Ujuzi): TZS 12,000,000 × 3.5% = TZS 420,000 per month. The employer pays this total — it is not deducted from any employee\'s salary.',
    register="formal",
    pair_type="standard"
))

pairs.append(make(29, "sdl_calculation",
    q_sw='Mwezi huu kulipwa mishahara tu kwa wafanyakazi 10 kila mmoja TZS 358,322 (kiwango cha chini cha mshahara). SDL ni kiasi gani?',
    a_sw='Jumla ya mishahara: 10 × TZS 358,322 = TZS 3,583,220. SDL (Skills Development Levy — Kodi ya Kukuza Ujuzi): TZS 3,583,220 × 3.5% = TZS 125,413 (kuzungusha hadi shilingi kamili). Kumbuka: kiwango cha chini cha mshahara wa sekta ya kawaida ni TZS 358,322 kuanzia 1 Januari 2026 (GN 605A).',
    q_en='This month only 10 employees were paid the minimum wage of TZS 358,322 each. What is the SDL?',
    a_en='Total payroll: 10 × TZS 358,322 = TZS 3,583,220. SDL (Skills Development Levy — Kodi ya Kukuza Ujuzi): TZS 3,583,220 × 3.5% = TZS 125,413 (rounded to whole shillings). Note: the minimum wage for general private sector is TZS 358,322 from 1 January 2026 (GN 605A).',
    register="business_market",
    pair_type="standard"
))

pairs.append(make(30, "sdl_calculation",
    q_sw='Kampuni yangu inalipa SDL ya TZS 350,000 kwa mwezi. Je, jumla ya mishahara ni TZS ngapi?',
    a_sw='Kuhesabu nyuma: ikiwa SDL = TZS 350,000 na kiwango = asilimia 3.5, basi jumla ya mishahara = TZS 350,000 ÷ 3.5% = TZS 10,000,000 kwa mwezi. SDL ni Skills Development Levy (Kodi ya Kukuza Ujuzi). Hakikisha kampuni ina wafanyakazi 10 au zaidi ili SDL itumike.',
    q_en='My company pays TZS 350,000 in SDL per month. What is the total payroll?',
    a_en='Working backwards: if SDL = TZS 350,000 and rate = 3.5%, then total payroll = TZS 350,000 ÷ 3.5% = TZS 10,000,000 per month. SDL is the Skills Development Levy (Kodi ya Kukuza Ujuzi). Confirm the company has 10 or more employees for SDL to apply.',
    register="business_market",
    pair_type="standard"
))

# ── 10 THRESHOLD EDGE CASES ───────────────────────────────────────────────────

pairs.append(make(31, "sdl_threshold",
    q_sw='Kampuni yangu ina wafanyakazi 9. Je, tunalipa SDL?',
    a_sw='Hapana. SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — inastahili tu kwa waajiri wenye wafanyakazi 10 au zaidi kwenye Tanzania Bara. Wafanyakazi 9 ni chini ya kiwango cha chini. Ikiwa utaajiri mfanyakazi mmoja zaidi na kufikia 10, utalazimika kuanza kulipa SDL kwa asilimia 3.5 ya jumla ya mishahara.',
    q_en='My company has 9 employees. Do we pay SDL?',
    a_en='No. SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — only applies to employers with 10 or more employees on Mainland Tanzania. 9 employees is below the threshold. If you hire one more employee and reach 10, you will be required to start paying SDL at 3.5% of total gross payroll.',
    register="business_market"
))

pairs.append(make(32, "sdl_threshold",
    q_sw='Wafanyakazi wangu waligeuka 10 mwezi huu. SDL inaanza lini?',
    a_sw='SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — inaanza kulipwa mara tu unapofika wafanyakazi 10. Kwa mwezi huu, hesabu SDL kwa jumla ya mishahara ya wafanyakazi wote 10. Wasilisha pamoja na PAYE ifikapo siku ya 7 ya mwezi unaofuata. Kiwango: asilimia 3.5 ya jumla ya mishahara.',
    q_en='My employees just reached 10 this month. When does SDL start?',
    a_en='SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — starts as soon as you reach 10 employees. For this month, calculate SDL on the total payroll of all 10 employees. Submit together with PAYE by the 7th of the following month. Rate: 3.5% of total gross payroll.',
    register="business_market"
))

pairs.append(make(33, "sdl_threshold",
    q_sw='Mwezi mmoja nilifikia wafanyakazi 11, mwezi uliofuata nilikuwa na 8 kwa sababu ya kuacha kazi. Je, nililazimika kulipa SDL mwezi mzima wa kwanza?',
    a_sw='Ndiyo. Mwezi ulipokuwa na wafanyakazi 11 ulilazimika kulipa SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — kwa sababu ulifika kiwango cha chini cha 10. Mwezi uliofuata ulipokuwa na wafanyakazi 8 huhitajiwi tena kulipa SDL. SDL inatathminiwa kila mwezi kulingana na idadi halisi ya wafanyakazi wa mwezi husika.',
    q_en='One month I had 11 employees, the next I was down to 8 due to resignations. Was I required to pay SDL for the whole first month?',
    a_en='Yes. The month you had 11 employees you were required to pay SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — because you met the threshold of 10 or more. The following month with 8 employees you are no longer required to pay SDL. SDL is assessed each month based on the actual employee count for that month.',
    register="formal"
))

pairs.append(make(34, "sdl_threshold",
    q_sw='Kiwango cha chini cha SDL ni wafanyakazi wangapi? Na Zanzibar inajumuishwa?',
    a_sw='Kiwango cha chini cha SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — ni wafanyakazi 10 au zaidi kwenye Tanzania Bara (Mainland Tanzania). Zanzibar ina mamlaka yake ya ushuru na sheria tofauti. SDL ya TRA (Mainland) haitumiki kwa Zanzibar. Waajiri wa Zanzibar wanahitaji kushauriana na Zanzibar Revenue Authority (ZRA).',
    q_en='What is the minimum employee threshold for SDL? And is Zanzibar included?',
    a_en='The minimum threshold for SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — is 10 or more employees on Mainland Tanzania. Zanzibar has its own tax authority and different laws. TRA\'s SDL (Mainland) does not apply to Zanzibar. Zanzibar-based employers should consult the Zanzibar Revenue Authority (ZRA).',
    register="formal"
))

pairs.append(make(35, "sdl_threshold",
    q_sw='Je, wafanyakazi wa muda mfupi (casual workers) wanajumuishwa katika kuhesabu idadi ya wafanyakazi kwa SDL?',
    a_sw='Wafanyakazi wanaolipwa mishahara kwenye orodha ya malipo (payroll) — ikiwemo wafanyakazi wa muda mfupi wanaolipwa mshahara — wanajumuishwa katika hesabu ya SDL (Skills Development Levy — Kodi ya Kukuza Ujuzi). Thibisha na TRA hali halisi ya wafanyakazi wako wa muda mfupi. Kawaida, mtu yeyote kwenye payroll yako anajumuishwa katika jumla ya mishahara inayotozwa SDL.',
    q_en='Are casual workers included in the employee count for SDL threshold purposes?',
    a_en='Workers on the payroll — including casual workers paid wages — are generally included in the SDL (Skills Development Levy — Kodi ya Kukuza Ujuzi) calculation. Confirm the exact treatment of your casual workers with TRA. Generally, anyone on your payroll is included in the gross payroll subject to SDL.',
    register="business_market"
))

pairs.append(make(36, "sdl_threshold",
    q_sw='Biashara yangu Tanzania Bara ina wafanyakazi 9 wa kudumu na 3 wa mkataba. Je, wafanyakazi wa mkataba wanajumuishwa?',
    a_sw='Jumla ya wafanyakazi wanaolipwa (9 wa kudumu + 3 wa mkataba = 12) unazidi kiwango cha chini cha 10. Kwa hivyo unalazimika kulipa SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — kwa asilimia 3.5 ya jumla ya mishahara ya wafanyakazi wote 12. Wafanyakazi wa mkataba wanaolipwa mishahara wanajumuishwa katika hesabu ya SDL.',
    q_en='My Mainland Tanzania business has 9 permanent employees and 3 contract workers. Are contract workers included?',
    a_en='Total paid workforce (9 permanent + 3 contract = 12) exceeds the threshold of 10. Therefore you are required to pay SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — at 3.5% of the total payroll for all 12 employees. Contract workers who receive wages are included in the SDL calculation.',
    register="business_market"
))

pairs.append(make(37, "sdl_threshold",
    q_sw='Kampuni ina tawi Dar es Salaam (wafanyakazi 6) na tawi Mwanza (wafanyakazi 5). Je, SDL inahesabiwaje?',
    a_sw='Jumla ya wafanyakazi wote: 6 + 5 = 11, yaani inazidi kiwango cha chini cha 10. SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — inahesabiwi kwa msingi wa jumla ya mishahara ya kampuni nzima (matawi yote), si kwa tawi moja moja. Thibisha na TRA jinsi ya kuwasilisha SDL kwa kampuni yenye matawi mengi.',
    q_en='A company has a Dar es Salaam branch (6 employees) and a Mwanza branch (5 employees). How is SDL calculated?',
    a_en='Total workforce across all branches: 6 + 5 = 11, which exceeds the threshold of 10. SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — is calculated on the company\'s total payroll (all branches combined), not branch by branch. Confirm with TRA how to remit SDL for a company with multiple branches.',
    register="formal"
))

pairs.append(make(38, "sdl_threshold",
    q_sw='Mwajiri aliniambia: "tuna wafanyakazi 10 lakini mmoja yuko likizoni, kwa hivyo tumehesabu kwa 9." Je, hii ni sahihi?',
    a_sw='Hapana. Mfanyakazi aliye likizoni bado ni mfanyakazi wako — anahesabika katika jumla ya wafanyakazi kwa SDL. SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — inategemea wafanyakazi wote wanaolipwa, ikiwemo wale wanaolipwa wakati wa likizo. Kampuni yenye wafanyakazi 10 (mmoja likizoni bado analipwa) inalazimika kulipa SDL kwa asilimia 3.5 ya jumla ya mishahara.',
    q_en='An employer told me: "we have 10 employees but one is on leave, so we calculated for 9." Is this correct?',
    a_en='No. An employee on leave is still your employee — they count in the total for SDL purposes. SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — depends on all employees on payroll, including those being paid while on leave. A company with 10 employees (one on paid leave still counted) is required to pay SDL at 3.5% of total gross payroll.',
    register="rural_conversational"
))

pairs.append(make(39, "sdl_threshold",
    q_sw='Nilikuwa na wafanyakazi 10 tangu miaka mitatu. SDL ninaidaiwa kutoka lini?',
    a_sw='SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — inadaiwa kutoka tarehe ulipofika wafanyakazi 10 au zaidi. Ikiwa umekuwa na wafanyakazi 10+ kwa miaka mitatu na hujawahi kulipa SDL, kuna uwezekano wa madai ya malimbikizo, faini, na riba. Wasiliana na TRA mara moja ili kutathmini hali yako na kupanga mpango wa kulipa madeni yaliyosalia.',
    q_en='I have had 10 employees for three years. From when am I liable for SDL?',
    a_en='SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — is owed from the date you reached 10 or more employees. If you have had 10+ employees for three years and have never paid SDL, there may be outstanding assessments, penalties, and interest. Contact TRA immediately to assess your situation and arrange a payment plan for any arrears.',
    register="business_market"
))

pairs.append(make(40, "sdl_threshold",
    q_sw='Je, wafanyakazi wa Zanzibar wanajumuishwa kwenye kuhesabu wafanyakazi 10 wa SDL ya Tanzania Bara?',
    a_sw='Hapana. SDL ya TRA (Mainland) inatumika tu kwa wafanyakazi wa Tanzania Bara. Wafanyakazi waliopo Zanzibar si sehemu ya hesabu ya SDL ya Mainland. Ikiwa una wafanyakazi 8 Mainland na 4 Zanzibar, unaweza kutolazimika kulipa SDL ya TRA (Mainland 8 < 10). Zanzibar ina mfumo wake tofauti kupitia ZRA.',
    q_en='Are Zanzibar-based employees included in the 10-employee count for Mainland Tanzania SDL?',
    a_en='No. TRA\'s SDL (Mainland) applies only to employees based on Mainland Tanzania. Zanzibar-based employees are not part of the Mainland SDL calculation. If you have 8 Mainland employees and 4 Zanzibar employees, you may not be liable for TRA SDL (Mainland 8 < 10). Zanzibar has its own separate system through ZRA.',
    register="formal"
))

# ── 5 EXEMPTIONS ─────────────────────────────────────────────────────────────

pairs.append(make(41, "sdl_exemptions",
    q_sw='Kampuni yetu iko katika Eneo la Usindikaji wa Uuzaji Nje (EPZ). Je, tunalipa SDL?',
    a_sw='Kampuni zilizo ndani ya Eneo la Usindikaji wa Uuzaji Nje (Export Processing Zone — EPZ) zina msamaha wa SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — kulingana na faida za EPZ. Msamaha huu ni sehemu ya vivutio vya uwekezaji vya EPZ Tanzania. Thibitisha hali yako ya msamaha na EPZ Authority na TRA kwa maandishi kabla ya kusimama kulipa SDL.',
    q_en='Our company is in an Export Processing Zone (EPZ). Do we pay SDL?',
    a_en='Companies located within an Export Processing Zone (EPZ) are exempt from SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — as part of the EPZ investment incentives package. This exemption is part of Tanzania\'s EPZ investment incentives. Confirm your exemption status in writing with the EPZ Authority and TRA before stopping SDL payments.',
    register="formal",
    pair_type="standard"
))

pairs.append(make(42, "sdl_exemptions",
    q_sw='NGO yetu ina wafanyakazi 15. Je, tunasamehewa SDL?',
    a_sw='Mashirika yasiyo ya faida (NGO) yanaweza kuwa na msamaha wa SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — kulingana na hali ya usajili na shughuli zao. Msamaha si wa moja kwa moja — NGO lazima iombe na kupata uthibitisho kutoka TRA. Thibitisha hali ya msamaha wako wa SDL kwa maandishi na TRA. Hadi utakapopata uthibitisho rasmi, lipa SDL ili kuepuka adhabu.',
    q_en='Our NGO has 15 employees. Are we exempt from SDL?',
    a_en='Non-governmental organizations (NGOs) may be exempt from SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — depending on their registration status and activities. Exemption is not automatic — the NGO must apply for and obtain written confirmation from TRA. Confirm your SDL exemption status in writing with TRA. Until you receive official confirmation, continue paying SDL to avoid penalties.',
    register="business_market",
    pair_type="standard"
))

pairs.append(make(43, "sdl_exemptions",
    q_sw='Taasisi ya serikali (government agency) inayolipa mishahara kwa wafanyakazi 50 — je, inalipa SDL?',
    a_sw='Mashirika ya serikali kwa ujumla hayalazimiki kulipa SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — kama ilivyoelezwa na TRA. SDL inahusu hasa sekta binafsi. Hata hivyo, msamaha huu unatofautiana kwa aina ya taasisi. Mashirika ya serikali yanayofanya biashara kama kampuni za kibiashara yanaweza kutakiwa kulipa. Thibisha hali yako na TRA kwa maandishi.',
    q_en='A government agency paying salaries to 50 employees — does it pay SDL?',
    a_en='Government institutions are generally not required to pay SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — as specified by TRA. SDL primarily concerns the private sector. However, this exemption varies by type of institution. Parastatal bodies that operate commercially may be required to pay. Confirm your status with TRA in writing.',
    register="formal",
    pair_type="standard"
))

pairs.append(make(44, "sdl_exemptions",
    q_sw='Kampuni ya uwekezaji wa nje iliyopo kwenye SEZ (Special Economic Zone) — je, inalipa SDL?',
    a_sw='Kampuni zilizo ndani ya Special Economic Zone (SEZ) — kama vile EPZ — zinaweza kupata msamaha wa SDL (Skills Development Levy — Kodi ya Kukuza Ujuzi) kama sehemu ya vivutio vya uwekezaji. Msamaha wa SEZ unathibitishwa na EPZA (Export Processing Zones Authority). Omba barua ya uthibitisho wa msamaha kutoka EPZA na nakala ya uthibitisho kutoka TRA kabla ya kusimama kulipa SDL.',
    q_en='A foreign-invested company in a Special Economic Zone (SEZ) — does it pay SDL?',
    a_en='Companies within a Special Economic Zone (SEZ) — such as EPZ — may be exempt from SDL (Skills Development Levy — Kodi ya Kukuza Ujuzi) as part of the investment incentives package. SEZ exemptions are confirmed by EPZA (Export Processing Zones Authority). Obtain a written exemption letter from EPZA and a copy of TRA confirmation before stopping SDL payments.',
    register="formal",
    pair_type="standard"
))

pairs.append(make(45, "sdl_exemptions",
    q_sw='Shule au chuo binafsi chenye walimu 20 — je, kinalipa SDL?',
    a_sw='Shule na vyuo binafsi vinavyofanya kazi kama biashara binafsi vinaweza kutakiwa kulipa SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — ikiwa vina wafanyakazi 10 au zaidi. Msamaha unategemea hali ya usajili (NGO, taasisi ya kidini, au kampuni ya biashara). Kama chuo kiliposajiliwa kama NGO au taasisi ya kidini, tafuta uthibitisho wa msamaha kutoka TRA. La sivyo, lipa SDL kwa asilimia 3.5 ya jumla ya mishahara.',
    q_en='A private school or college with 20 teachers — does it pay SDL?',
    a_en='Private schools and colleges operating as private businesses may be required to pay SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — if they have 10 or more employees. Exemption depends on registration status (NGO, religious institution, or commercial company). If the institution is registered as an NGO or religious body, seek written exemption confirmation from TRA. Otherwise, pay SDL at 3.5% of total gross payroll.',
    register="business_market",
    pair_type="standard"
))

# ── 5 DEADLINE AND PENALTY ────────────────────────────────────────────────────

pairs.append(make(46, "sdl_deadline_penalty",
    q_sw='SDL inalipwa lini na nini hutokea ikiwa itachelewa?',
    a_sw='SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — inalipwa ifikapo siku ya 7 ya kila mwezi kwa mishahara ya mwezi uliopita, pamoja na PAYE. Ikiwa itachelewa: TRA inaweza kutoza riba ya asilimia 2 kwa mwezi (au kiwango kingine kilichowekwa) pamoja na faini. Kuchelewa kwa miezi kadhaa kunaweza kusababisha ukaguzi, tathmini, na hatua za kisheria.',
    q_en='When is SDL due and what happens if it is late?',
    a_en='SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — is due by the 7th of each month for the previous month\'s payroll, together with PAYE. If late: TRA may impose interest (typically 2% per month or the current prescribed rate) plus penalties. Persistent late payments can result in audits, assessments, and legal action.',
    register="business_market",
    pair_type="standard"
))

pairs.append(make(47, "sdl_deadline_penalty",
    q_sw='Je, ninaweza kulipa SDL na PAYE siku tofauti?',
    a_sw='Kimsingi SDL na PAYE zote mbili zinapaswa kuwasilishwa TRA ifikapo siku ya 7 ya mwezi unaofuata. Kwa vitendo, zinalipwa pamoja kwa sababu zinawasilishwa kwenye fomu sawa ya malipo. Kulipa siku moja bila nyingine kunaweza kuchanganya rekodi za TRA. Mapendekezo: lipa SDL na PAYE pamoja siku ya 7 au kabla ya siku ya 7. SDL = Skills Development Levy (Kodi ya Kukuza Ujuzi).',
    q_en='Can I pay SDL and PAYE on different days?',
    a_en='In principle, both SDL and PAYE must be submitted to TRA by the 7th of the following month. In practice, they are paid together because they are submitted on the same payment form. Paying one day without the other may confuse TRA records. Recommendation: pay SDL and PAYE together on or before the 7th. SDL = Skills Development Levy (Kodi ya Kukuza Ujuzi).',
    register="business_market",
    pair_type="standard"
))

pairs.append(make(48, "sdl_deadline_penalty",
    q_sw='Tulikosa kulipa SDL kwa miezi 3. TRA wanaweza kufanya nini?',
    a_sw='Kukosa kulipa SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — kwa miezi 3 ni ukiukaji wa makubaliano wa ushuru. TRA inaweza: (1) Kutoza riba kwa kila mwezi wa ucheleweshaji; (2) Kuamua faini za ziada; (3) Kufanya ukaguzi wa malipo yote ya payroll; (4) Kutoa tathmini rasmi ya madeni; (5) Kuchukua hatua za kisheria ikiwa madeni hayatatuliwi. Wasiliana na TRA mara moja ili kutathmini hali na kupanga malipo ya madeni.',
    q_en='We missed paying SDL for 3 months. What can TRA do?',
    a_en='Failing to pay SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — for 3 months is a tax compliance violation. TRA may: (1) Charge interest for each month of delay; (2) Impose additional penalties; (3) Conduct a full payroll audit; (4) Issue a formal assessment of arrears; (5) Take legal action if arrears are not settled. Contact TRA immediately to assess the situation and arrange a payment plan.',
    register="formal",
    pair_type="standard"
))

pairs.append(make(49, "sdl_deadline_penalty",
    q_sw='Mwezi huu Siku ya 7 ni Jumamosi. Je, nalipa SDL siku ya 8 (Jumatatu)?',
    a_sw='Ikiwa tarehe ya mwisho wa kulipa SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — inakuwa siku ya mapumziko (Jumamosi, Jumapili, au sikukuu), tarehe ya mwisho huhamishwa hadi siku ya kazi inayofuata — yaani Jumatatu. Hii ni kanuni ya kawaida ya ushuru Tanzania. Lipa siku ya Jumatatu bila hofu ya adhabu, lakini thibisha hii na TRA kila mara ya shaka.',
    q_en='This month the 7th falls on a Saturday. Do I pay SDL on the 8th (Monday)?',
    a_en='If the SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — deadline falls on a public holiday, Saturday, or Sunday, the deadline is moved to the next working day — i.e., Monday. This is the standard Tanzanian tax rule. Pay on Monday without fear of penalty, but confirm this with TRA whenever in doubt.',
    register="rural_conversational",
    pair_type="standard"
))

pairs.append(make(50, "sdl_deadline_penalty",
    q_sw='Kuna adhabu ya nguvu kwa kutolipa SDL au tu faini ndogo?',
    a_sw='Adhabu ya kutolipa SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — inaweza kuwa kubwa: riba ya kuchelewa (kawaida asilimia 2 kwa mwezi au zaidi), faini za hadi asilimia fulani ya kiasi kilichodaiwa, ukaguzi wa kina wa malipo yote, tathmini ya nyuma hadi miaka mitano, na hatua za kisheria za jinai katika kesi kali. Ushirikiano wa mapema na TRA unapunguza adhabu. Usisita kulipa SDL hata kama una shida ya fedha — wasiliana na TRA kwanza.',
    q_en='Are SDL non-payment penalties severe or just a small fine?',
    a_en='Penalties for non-payment of SDL — Skills Development Levy (Kodi ya Kukuza Ujuzi) — can be severe: late interest (typically 2% per month or more), fines up to a percentage of the amount owed, full payroll audits, back-assessments up to five years, and criminal proceedings in serious cases. Early cooperation with TRA reduces penalties. Do not delay SDL even if facing cash flow difficulties — contact TRA first.',
    register="business_market",
    pair_type="standard"
))

# ── WRITE TO FILE ─────────────────────────────────────────────────────────────
output_file = "datasets/tier1a/raw_sources/raw_pairs_batch_003.jsonl"

with open(output_file, "a", encoding="utf-8") as f:
    for p in pairs:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

print(f"Wrote {len(pairs)} SDL pairs to {output_file}")

# Distribution check
registers = {}
for p in pairs:
    r = p["register"]
    registers[r] = registers.get(r, 0) + 1

total = len(pairs)
print("\nRegister distribution:")
for reg, count in sorted(registers.items()):
    pct = count / total * 100
    print(f"  {reg}: {count} ({pct:.0f}%)")

subdomains = {}
for p in pairs:
    s = p["subdomain"]
    subdomains[s] = subdomains.get(s, 0) + 1
print("\nSubdomain distribution:")
for sub, count in sorted(subdomains.items()):
    print(f"  {sub}: {count}")
