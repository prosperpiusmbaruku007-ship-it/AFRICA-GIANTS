"""
Generate Batch 002A training pairs for AFRICA-GIANTS Tier 1A.

Covers:
  - paye (25 pairs): IDs tier1a_paye_001..025
  - gn605a (20 pairs): IDs tier1a_gn605a_001..020
  - work_permits (5 pairs): IDs tier1a_permit_001..005

Sources:
  - PAYE: tra.go.tz/page/pay-as-you-earn-paye  (page scraped but rendered as JS-heavy nav;
           facts from Finance Act 2025, TRA primary source)
  - Withholding/VAT: scraped vat_edge.html + withholding.html (confirmed 3%/6% VAT w/h)
  - GN 605A: CLAUDE.md locked facts — PKF/VELMA/TanzLII GN 605A (VELMA 404 on scrape)
  - Work permits: immigration.go.tz (scraped)

All pairs:
  - register: business_market
  - eval_set: false
  - verified_by: pending_founder_review
  - verified_date: pending_founder_review
  - pair_type: standard (or adversarial where noted)
"""
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_FILE = os.path.join(ROOT, "datasets", "tier1a", "raw_sources", "raw_pairs_batch_002a.jsonl")
EXISTING_FILE = os.path.join(ROOT, "datasets", "tier1a", "raw_sources", "existing_questions.txt")

# Load existing questions for dedup
with open(EXISTING_FILE, encoding="utf-8") as f:
    existing_questions = set(line.strip().lower() for line in f if line.strip())


def p(
    id_, subdomain, question_sw, answer_sw, question_en, answer_en,
    url, source_name, source_type="government_portal",
    effective_date="2025-07-01", decay_risk="annual",
    next_review="Finance Act update", register="business_market",
    pair_type="standard",
):
    return {
        "id": id_,
        "domain": "tier1a",
        "subdomain": subdomain,
        "question_sw": question_sw,
        "answer_sw": answer_sw,
        "question_en": question_en,
        "answer_en": answer_en,
        "primary_source_url": url,
        "primary_source_name": source_name,
        "source_type": source_type,
        "effective_date": effective_date,
        "decay_risk": decay_risk,
        "next_review_trigger": next_review,
        "verified_by": "pending_founder_review",
        "verified_date": "pending_founder_review",
        "register": register,
        "pair_type": pair_type,
        "eval_set": False,
    }


TRA_PAYE_URL = "https://www.tra.go.tz/page/pay-as-you-earn-paye"
TRA_PAYE_NAME = "TRA - Pay As You Earn (PAYE)"
TRA_WH_URL = "https://www.tra.go.tz/page/withholding-tax"
TRA_WH_NAME = "TRA - Withholding Tax"
NSSF_URL = "https://www.nssf.go.tz/pages/payment-of-contributions"
NSSF_NAME = "NSSF - Payment of Contributions"
IMMIG_URL = "https://www.immigration.go.tz"
IMMIG_NAME = "Tanzania Immigration Department"
GN605A_URL = "https://tanzlii.org/akn/tz/act/gn/2025/605a/eng@2025-10-13"
GN605A_NAME = "Government Notice 605A (GN 605A) - Wage Order 2025, TanzLII"

pairs = []

# ─────────────────────────────────────────────────────────────────────────────
# PAYE — 25 pairs
# Source: TRA (fallback — scraped page rendered navigation only, facts from
# Finance Act 2025 as applied by TRA primary source)
# ─────────────────────────────────────────────────────────────────────────────

pairs.append(p(
    "tier1a_paye_001_20260603", "paye",
    "PAYE ni nini Tanzania?",
    "PAYE (Pay As You Earn) ni kodi ya mapato inayokatwa na mwajiri kutoka kwa mishahara ya wafanyakazi kila mwezi, kisha kulipwa TRA. Mwajiri ni wakala wa makusanyo — analipa kodi kwa niaba ya mfanyakazi. Thibitisha na TRA.",
    "What is PAYE in Tanzania?",
    "PAYE (Pay As You Earn) is income tax withheld by an employer from employees' monthly wages and remitted to TRA. The employer is the collection agent — paying tax on behalf of the employee. Confirm with TRA.",
    TRA_PAYE_URL, TRA_PAYE_NAME,
))

pairs.append(p(
    "tier1a_paye_002_20260603", "paye",
    "Mwajiri anapaswa kusajili PAYE TRA lini?",
    "Mwajiri anapaswa kusajili PAYE kabla ya kuanza kulipa mshahara wa kwanza wa mfanyakazi. Usajili unafanywa kupitia mfumo wa IDRAS kwenye tovuti ya TRA. Thibitisha na TRA.",
    "When must an employer register for PAYE with TRA?",
    "An employer must register for PAYE before paying the first employee's salary. Registration is done through the IDRAS system on the TRA website. Confirm with TRA.",
    TRA_PAYE_URL, TRA_PAYE_NAME,
))

pairs.append(p(
    "tier1a_paye_003_20260603", "paye",
    "Tarehe ya mwisho ya kulipa PAYE TRA ni ipi?",
    "PAYE lazima ilipwe TRA ifikapo tarehe 7 ya mwezi unaofuata. Kwa mfano, PAYE ya Januari inalipwa ifikapo tarehe 7 Februari. Thibitisha na TRA.",
    "What is the PAYE remittance deadline in Tanzania?",
    "PAYE must be remitted to TRA by the 7th of the following month. For example, January PAYE is due by 7 February. Confirm with TRA.",
    TRA_PAYE_URL, TRA_PAYE_NAME,
))

pairs.append(p(
    "tier1a_paye_004_20260603", "paye",
    "Malipo gani yanastahili PAYE Tanzania?",
    "PAYE inakata: mshahara wa msingi, ujira wa ziada (overtime), posho (allowances — nyumba, usafiri, chakula), bonasi, motisha, na thamani ya manufaa kama vile gari la kampuni au nyumba ya kampuni. Thibitisha na TRA.",
    "What payments are subject to PAYE in Tanzania?",
    "PAYE applies to: basic salary, overtime pay, allowances (housing, transport, meals), bonuses, incentives, and the value of benefits such as company car or company housing. Confirm with TRA.",
    TRA_PAYE_URL, TRA_PAYE_NAME,
))

pairs.append(p(
    "tier1a_paye_005_20260603", "paye",
    "Viwango vya PAYE Tanzania kwa 2025/2026 ni vipi?",
    "Viwango vya PAYE Tanzania Bara (Finance Act 2025): TZS 0–270,000/mwezi: 0%; TZS 270,001–520,000: 8% ya ziada; TZS 520,001–760,000: 20% ya ziada + TZS 20,000; TZS 760,001–1,000,000: 25% ya ziada + TZS 68,000; zaidi ya TZS 1,000,000: 30% ya ziada + TZS 128,000. Thibitisha na TRA baada ya kila Finance Act.",
    "What are the PAYE rates in Tanzania for 2025/2026?",
    "Tanzania Mainland PAYE bands (Finance Act 2025): TZS 0–270,000/month: 0%; TZS 270,001–520,000: 8% on excess; TZS 520,001–760,000: 20% on excess + TZS 20,000; TZS 760,001–1,000,000: 25% on excess + TZS 68,000; over TZS 1,000,000: 30% on excess + TZS 128,000. Confirm with TRA after each Finance Act.",
    TRA_PAYE_URL, TRA_PAYE_NAME,
))

pairs.append(p(
    "tier1a_paye_006_20260603", "paye",
    "PAYE inarudishwa TRA kwa njia gani?",
    "PAYE inarudishwa kupitia mfumo wa IDRAS (TRA Taxpayer Portal) mtandaoni. Mwajiri anaingiza return ya mwezi na kisha kulipa kupitia GePG au benki iliyoidhinishwa. Thibitisha na TRA.",
    "How is PAYE remitted to TRA?",
    "PAYE is remitted through the IDRAS (TRA Taxpayer Portal) online system. The employer files a monthly return and pays through GePG or an approved bank. Confirm with TRA.",
    TRA_PAYE_URL, TRA_PAYE_NAME,
))

pairs.append(p(
    "tier1a_paye_007_20260603", "paye",
    "Adhabu ya kutolipa PAYE kwa wakati ni ipi?",
    "Faini ya kuchelewsha PAYE ni asilimia 5 ya kiwango kilichochelewa kwa kila mwezi au sehemu ya mwezi, pamoja na riba. TRA pia inaweza kufunga akaunti za benki za mwajiri anayekosea. Thibitisha na TRA.",
    "What is the penalty for late PAYE remittance in Tanzania?",
    "The late PAYE penalty is 5% of the unpaid amount per month or part thereof, plus interest. TRA can also freeze bank accounts of non-compliant employers. Confirm with TRA.",
    TRA_PAYE_URL, TRA_PAYE_NAME,
))

pairs.append(p(
    "tier1a_paye_008_20260603", "paye",
    "Mwajiri anatoa taarifa ya kila mwaka ya PAYE TRA lini?",
    "Mwajiri anatoa Taarifa ya Mwaka ya PAYE (Annual PAYE Statement) ifikapo tarehe 31 Machi ya mwaka unaofuata. Taarifa hiyo inaonyesha jumla ya mapato na kodi iliyokatwa kwa kila mfanyakazi. Thibitisha na TRA.",
    "When does an employer submit the annual PAYE reconciliation to TRA?",
    "An employer must submit the Annual PAYE Statement (reconciliation) by 31 March of the following year. It shows total income and tax withheld per employee. Confirm with TRA.",
    TRA_PAYE_URL, TRA_PAYE_NAME,
))

pairs.append(p(
    "tier1a_paye_009_20260603", "paye",
    "Je, NSSF inakatwa kabla ya kuhesabu PAYE?",
    "Ndiyo. Mchango wa lazima wa NSSF (asilimia 10 ya mfanyakazi) unakatwa mshahara ghafi na unapunguza msingi wa PAYE. Kwa mfano, mfanyakazi mwenye mshahara TZS 600,000 analipa NSSF TZS 60,000; PAYE inacheswa kwa TZS 540,000. Thibitisha na TRA na NSSF.",
    "Is NSSF deducted before calculating PAYE?",
    "Yes. The mandatory employee NSSF contribution (10% of gross wage) is deducted from gross salary before calculating PAYE. For example, an employee earning TZS 600,000 pays TZS 60,000 NSSF; PAYE is calculated on TZS 540,000. Confirm with TRA and NSSF.",
    TRA_PAYE_URL, TRA_PAYE_NAME,
))

pairs.append(p(
    "tier1a_paye_010_20260603", "paye",
    "Je, SDL inaathiri PAYE ya mfanyakazi?",
    "Hapana. SDL (Skills and Development Levy) inalipwa na mwajiri kutoka mfuko wake mwenyewe — haikimuzi mfanyakazi. SDL haifanyi mabadiliko kwenye msingi wa PAYE wa mfanyakazi. Thibitisha na TRA.",
    "Does SDL affect an employee's PAYE calculation?",
    "No. SDL (Skills and Development Levy) is paid by the employer from their own funds — it is not deducted from the employee. SDL does not change the employee's PAYE base. Confirm with TRA.",
    TRA_PAYE_URL, TRA_PAYE_NAME,
))

pairs.append(p(
    "tier1a_paye_011_20260603", "paye",
    "Thamani ya nyumba ya kampuni inajumuishwa katika PAYE vipi?",
    "Kama mwajiri anatoa nyumba kwa mfanyakazi, thamani ya nyumba hiyo inajumuishwa katika mapato ya mfanyakazi kwa madhumuni ya PAYE. Thamani inahesabiwa kulingana na kanuni za TRA — kwa kawaida ni asilimia ya mshahara wa msingi au kodi ya soko. Thibitisha na TRA.",
    "How is employer-provided housing included in PAYE calculation?",
    "If an employer provides housing to an employee, the value of that housing is included in the employee's income for PAYE purposes. The value is calculated according to TRA rules — typically a percentage of basic salary or market rent. Confirm with TRA.",
    TRA_PAYE_URL, TRA_PAYE_NAME,
))

pairs.append(p(
    "tier1a_paye_012_20260603", "paye",
    "Gari la kampuni linalipwa PAYE vipi?",
    "Mfanyakazi anayetumia gari la kampuni kwa madhumuni ya kibinafsi anapata manufaa yanayostahili PAYE. Thamani ya manufaa inahesabiwa kulingana na sheria ya kodi ya TRA. Mwajiri analazimika kujumuisha thamani hiyo katika mshahara unaostahili PAYE. Thibitisha na TRA.",
    "How is a company car taxed under PAYE?",
    "An employee who uses a company car for personal purposes receives a taxable benefit subject to PAYE. The benefit value is calculated under TRA tax rules. The employer must include this value in the PAYE-liable payroll. Confirm with TRA.",
    TRA_PAYE_URL, TRA_PAYE_NAME,
))

pairs.append(p(
    "tier1a_paye_013_20260603", "paye",
    "Mfanyakazi anayefanya kazi kwa waajiri wawili analipa PAYE vipi?",
    "Mfanyakazi mwenye waajiri wawili au zaidi lazima ataarifu kila mwajiri kuhusu vyanzo vingine vya mapato. Mwajiri mkuu (primary employer) hutumia viwango vya kawaida; waajiri wengine wanatumia kiwango cha juu zaidi (top rate) au makubaliano maalum na TRA. Thibitisha na TRA.",
    "How is PAYE calculated for an employee with two employers?",
    "An employee with two or more employers must notify each employer of the other income sources. The primary employer uses the normal tax bands; secondary employers apply the highest rate or a special TRA arrangement. Confirm with TRA.",
    TRA_PAYE_URL, TRA_PAYE_NAME,
))

pairs.append(p(
    "tier1a_paye_014_20260603", "paye",
    "Je, bonasi na motisha zinapaswa kulipwa PAYE?",
    "Ndiyo. Bonasi, motisha (incentives), na malipo ya kipekee yote yanajumuishwa katika mapato yanayostahili PAYE. Yanalipwa mwezi yanayotolewa na PAYE inacheswa kwa msingi wa mwezi huo. Thibitisha na TRA.",
    "Are bonuses and incentives subject to PAYE in Tanzania?",
    "Yes. Bonuses, incentives, and one-off payments are all included in PAYE-liable income. They are taxed in the month paid, with PAYE calculated on the total income for that month. Confirm with TRA.",
    TRA_PAYE_URL, TRA_PAYE_NAME,
))

pairs.append(p(
    "tier1a_paye_015_20260603", "paye",
    "Malipo ya mwisho ya kazi (gratuity/terminal benefits) yanastahili PAYE?",
    "Malipo ya mwisho wa kazi kama vile malipo ya likizo yasiyotumika, mafao ya kujitenga (gratuity), na malipo ya fidia yanaweza kustahili PAYE kulingana na sheria ya kodi. Sehemu fulani inaweza kuwa huru — thibitisha hesabu halisi na TRA kabla ya kulipa.",
    "Are terminal benefits and gratuity subject to PAYE?",
    "Terminal payments such as unused leave pay-out, gratuity, and severance may be subject to PAYE depending on the tax rules. Certain portions may be exempt — confirm the exact calculation with TRA before payment.",
    TRA_PAYE_URL, TRA_PAYE_NAME,
))

pairs.append(p(
    "tier1a_paye_016_20260603", "paye",
    "Kazi ya ziada (overtime) inalipwa PAYE Tanzania?",
    "Ndiyo. Malipo ya kazi ya ziada yanajumuishwa katika jumla ya mapato ya mwezi na yanastahili PAYE kwa kiwango kinacholingana na kanda ya mapato. Hakuna kiwango maalum cha PAYE kwa overtime peke yake. Thibitisha na TRA.",
    "Is overtime pay subject to PAYE in Tanzania?",
    "Yes. Overtime pay is included in total monthly earnings and is subject to PAYE at the applicable rate band. There is no separate PAYE rate for overtime. Confirm with TRA.",
    TRA_PAYE_URL, TRA_PAYE_NAME,
))

pairs.append(p(
    "tier1a_paye_017_20260603", "paye",
    "Je, mfanyakazi wa muda mfupi (casual worker) analipa PAYE?",
    "Inategemea: kama mfanyakazi wa muda mfupi anafanya kazi kwa zaidi ya siku 30 mfululizo au kuwa na mapato yanayozidi kiwango cha chini cha PAYE (TZS 270,000/mwezi), mwajiri anapaswa kukata PAYE. Thibitisha hali halisi na TRA.",
    "Do casual workers pay PAYE in Tanzania?",
    "It depends: if a casual worker works for more than 30 consecutive days or has earnings exceeding the minimum PAYE threshold (TZS 270,000/month), the employer must deduct PAYE. Confirm the specific situation with TRA.",
    TRA_PAYE_URL, TRA_PAYE_NAME,
))

pairs.append(p(
    "tier1a_paye_018_20260603", "paye",
    "Malipo ya mkurugenzi (director's fee) yanastahili PAYE?",
    "Ndiyo. Malipo ya mkurugenzi wa kampuni yanastahili PAYE. Kama mkurugenzi si mfanyakazi wa wakati kamili, yanaweza kustahili kodi ya zuio (withholding tax) badala ya PAYE — kiwango ni asilimia 15 kwa wakazi. Thibitisha aina ya mkurugenzi na TRA.",
    "Are director's fees subject to PAYE in Tanzania?",
    "Yes. Director's fees are subject to PAYE. If the director is not a full-time employee, the fees may be subject to withholding tax instead of PAYE — the rate is 15% for residents. Confirm the director's classification with TRA.",
    TRA_PAYE_URL, TRA_PAYE_NAME,
))

pairs.append(p(
    "tier1a_paye_019_20260603", "paye",
    "PAYE tofauti na kodi ya zuio (withholding tax) ni nini?",
    "PAYE inahusu mapato ya ajira tu — mwajiri anakata na kulipa kila mwezi. Kodi ya zuio inahusu malipo mengine kama vile gawio (dividends), riba, ada za ushauri, na pango — wakala mwingine (mtu anayetoa malipo) anakata na kulipa. Viwango na tarehe za malipo zinatofautiana. Thibitisha na TRA.",
    "What is the difference between PAYE and withholding tax in Tanzania?",
    "PAYE relates only to employment income — the employer deducts and remits monthly. Withholding tax covers other payments such as dividends, interest, consultancy fees, and rent — the paying party deducts and remits. Rates and deadlines differ. Confirm with TRA.",
    TRA_PAYE_URL, TRA_PAYE_NAME,
))

pairs.append(p(
    "tier1a_paye_020_20260603", "paye",
    "Je, PAYE inaweza kuomba kurudishwa (refund)?",
    "Ndiyo. Kama PAYE iliyokatwa ni zaidi ya kodi halisi, mfanyakazi anaweza kuomba kurudishwa kupitia TRA. Ombi hufanywa kupitia mfumo wa IDRAS baada ya kujaza taarifa ya mwaka (individual tax return) ikiwa ni lazima. Thibitisha na TRA.",
    "Can PAYE be refunded if overpaid?",
    "Yes. If PAYE deducted exceeds the actual tax liability, the employee can apply for a refund through TRA. The application is made via the IDRAS system after filing the annual return where required. Confirm with TRA.",
    TRA_PAYE_URL, TRA_PAYE_NAME,
))

pairs.append(p(
    "tier1a_paye_021_20260603", "paye",
    "Posho ya usafiri inapaswa kulipwa PAYE Tanzania?",
    "Inategemea: posho ya usafiri inayolipwa kupita kiasi cha gharama halisi za kazi (reimbursement ya kweli) inastahili PAYE. Posho inayolipwa kama nyongeza ya mshahara — bila kuhusiana na safari ya kazi — inastahili PAYE kamili. Thibitisha mtiririko halisi na TRA.",
    "Is a transport allowance subject to PAYE in Tanzania?",
    "It depends: transport allowance paid beyond actual business travel costs (genuine reimbursement) is subject to PAYE. Allowances paid as a salary top-up — not related to business travel — are fully subject to PAYE. Confirm the actual arrangement with TRA.",
    TRA_PAYE_URL, TRA_PAYE_NAME,
))

pairs.append(p(
    "tier1a_paye_022_20260603", "paye",
    "Mwajiri analazimika kuweka rekodi gani za PAYE?",
    "Mwajiri lazima aweke: orodha ya wafanyakazi na TIN zao, hesabu za mishahara, hesabu za PAYE kwa kila mfanyakazi, stakabadhi za malipo ya TRA, na fomu za PAYE P9. Rekodi hizi zinahifadhiwa kwa miaka 5. Thibitisha na TRA.",
    "What PAYE records must an employer maintain?",
    "An employer must keep: employee list with their TINs, payroll calculations, PAYE calculations per employee, TRA payment receipts, and PAYE P9 forms. Records must be kept for 5 years. Confirm with TRA.",
    TRA_PAYE_URL, TRA_PAYE_NAME,
    decay_risk="stable",
    next_review="Legislative change",
))

pairs.append(p(
    "tier1a_paye_023_20260603", "paye",
    "Je, ruzuku ya matibabu (medical allowance) inastahili PAYE Tanzania?",
    "Ruzuku ya matibabu inayolipwa moja kwa moja kwa mfanyakazi (cash allowance) inastahili PAYE. Malipo ya matibabu yanayolipwa moja kwa moja kwa hospitali au insurer kwa niaba ya mfanyakazi yanaweza kuwa na nafuu — thibitisha kiasi na TRA.",
    "Is a medical allowance subject to PAYE in Tanzania?",
    "A medical allowance paid directly to the employee as cash is subject to PAYE. Payments made directly to a hospital or insurer on behalf of the employee may receive a tax relief — confirm the threshold and arrangement with TRA.",
    TRA_PAYE_URL, TRA_PAYE_NAME,
))

pairs.append(p(
    "tier1a_paye_024_20260603", "paye",
    "Kama mwajiri hakukata PAYE, nani analipa deni?",
    "Mwajiri anachukuliwa kuwa na jukumu kamili kwa PAYE yote ambayo haikukatwa au hakulipwa TRA, pamoja na faini na riba. TRA inaweza kudai deni hilo moja kwa moja kutoka kwa mwajiri bila kujali kama mfanyakazi alipata mshahara kamili. Thibitisha na TRA.",
    "If an employer fails to deduct PAYE, who owes the tax?",
    "The employer bears full liability for all PAYE not deducted or remitted to TRA, including penalties and interest. TRA can demand the debt directly from the employer regardless of whether the employee received full pay. Confirm with TRA.",
    TRA_PAYE_URL, TRA_PAYE_NAME,
    decay_risk="stable",
    next_review="Legislative change",
    pair_type="adversarial",
))

pairs.append(p(
    "tier1a_paye_025_20260603", "paye",
    "PAYE inalipwa kwa mwezi mmoja ambao haukuwa na wafanyakazi — toa return?",
    "Ndiyo. Mwajiri aliyesajiliwa PAYE lazima atoe return ya sifuri (nil return) hata kwa miezi ambayo hakuna wafanyakazi au hakuna malipo. Kushindwa kutoa nil return kunasababisha faini. Thibitisha na TRA.",
    "Must an employer file a PAYE return for a month with no employees?",
    "Yes. A PAYE-registered employer must file a nil return even for months with no employees or no payments. Failure to file a nil return attracts a penalty. Confirm with TRA.",
    TRA_PAYE_URL, TRA_PAYE_NAME,
    decay_risk="stable",
    next_review="Legislative change",
    pair_type="adversarial",
))

# ─────────────────────────────────────────────────────────────────────────────
# GN 605A — 20 pairs
# Source: GN 605A via TanzLII (CLAUDE.md locked facts)
# ─────────────────────────────────────────────────────────────────────────────

pairs.append(p(
    "tier1a_gn605a_001_20260603", "gn605a",
    "GN 605A ni nini Tanzania?",
    "GN 605A ni Amri ya Mishahara ya Sekta ya Faragha (Wage Order) iliyotolewa chini ya ELRA. Inaweka kiwango cha chini cha mishahara (minimum wage) kwa sekta 16 na sekta ndogo 46 nchini Tanzania Bara. Ilianza kutumika tarehe 1 Januari 2026. Thibitisha na MLYWF.",
    "What is GN 605A in Tanzania?",
    "GN 605A is the Private Sector Wage Order issued under ELRA. It sets the minimum wage for 16 sectors and 46 sub-sectors in Tanzania Mainland. It came into effect on 1 January 2026. Confirm with MLYWF.",
    GN605A_URL, GN605A_NAME,
    source_type="official_gazette",
    effective_date="2026-01-01",
    decay_risk="event_triggered",
    next_review="New wage order gazette",
))

pairs.append(p(
    "tier1a_gn605a_002_20260603", "gn605a",
    "GN 605A ilianza tarehe ngapi?",
    "GN 605A ilianza kutumika tarehe 1 Januari 2026. Ilisainiwa mnamo Oktoba 2025. Amri ya zamani ya mshahara wa mwaka 2022 ilifutwa rasmi kuanzia tarehe hiyo hiyo. Thibitisha na TanzLII.",
    "When did GN 605A come into effect?",
    "GN 605A came into effect on 1 January 2026. It was gazetted in October 2025. The 2022 wage order was formally revoked from the same date. Confirm with TanzLII.",
    GN605A_URL, GN605A_NAME,
    source_type="official_gazette",
    effective_date="2026-01-01",
    decay_risk="event_triggered",
    next_review="New wage order gazette",
))

pairs.append(p(
    "tier1a_gn605a_003_20260603", "gn605a",
    "Amri ya mishahara ya 2022 bado inatumika Tanzania?",
    "Hapana. Amri ya mishahara ya 2022 ilifutwa rasmi kuanzia tarehe 1 Januari 2026 wakati GN 605A ilipoanza kutumika. Mwajiri anayendelea kulipa kwa viwango vya 2022 anakiuka sheria. Thibitisha na MLYWF.",
    "Is the 2022 wage order still valid in Tanzania?",
    "No. The 2022 wage order was formally revoked from 1 January 2026 when GN 605A came into force. An employer continuing to pay at 2022 rates is violating the law. Confirm with MLYWF.",
    GN605A_URL, GN605A_NAME,
    source_type="official_gazette",
    effective_date="2026-01-01",
    decay_risk="event_triggered",
    next_review="New wage order gazette",
    pair_type="adversarial",
))

pairs.append(p(
    "tier1a_gn605a_004_20260603", "gn605a",
    "Ongezeko la wastani la mshahara chini ya GN 605A ni kiasi gani?",
    "Ongezeko la wastani la sekta ya faragha chini ya GN 605A ni asilimia 33.4 — kutoka TZS 275,060 hadi TZS 358,322 kwa mwezi. Hii ni wastani kwa sekta zote; sekta fulani zinaongezeka zaidi. Thibitisha kiasi halisi cha sekta yako na MLYWF.",
    "What is the average wage increase under GN 605A?",
    "The average private sector increase under GN 605A is 33.4% — from TZS 275,060 to TZS 358,322 per month. This is the average across all sectors; some sectors increase by more. Confirm your sector's exact amount with MLYWF.",
    GN605A_URL, GN605A_NAME,
    source_type="official_gazette",
    effective_date="2026-01-01",
    decay_risk="event_triggered",
    next_review="New wage order gazette",
))

pairs.append(p(
    "tier1a_gn605a_005_20260603", "gn605a",
    "Kiwango cha chini kabisa cha mshahara chini ya GN 605A ni kiasi gani?",
    "Kiwango cha chini kabisa kwa sekta ya jumla ni karibu TZS 175,000 kwa mwezi. Viwango vinafikia hadi TZS 765,900 kwa sekta ya madini ya kimataifa na nishati. Thibitisha kiwango halisi cha sekta yako na MLYWF.",
    "What is the lowest minimum wage under GN 605A?",
    "The lowest minimum wage for the general sector is approximately TZS 175,000 per month. Rates reach up to TZS 765,900 for the international mining and energy sector. Confirm your sector's exact rate with MLYWF.",
    GN605A_URL, GN605A_NAME,
    source_type="official_gazette",
    effective_date="2026-01-01",
    decay_risk="event_triggered",
    next_review="New wage order gazette",
))

pairs.append(p(
    "tier1a_gn605a_006_20260603", "gn605a",
    "Kiwango cha juu kabisa cha mshahara chini ya GN 605A ni kiasi gani?",
    "Kiwango cha juu kabisa ni TZS 765,900 kwa mwezi — inayohusu sekta ya madini ya kimataifa na nishati. Hii ni kiwango cha chini; waajiri wanaweza kulipa zaidi. Thibitisha sekta yako na MLYWF.",
    "What is the highest minimum wage under GN 605A?",
    "The highest minimum wage is TZS 765,900 per month — applicable to the international mining and energy sector. This is a floor; employers may pay above this. Confirm your sector with MLYWF.",
    GN605A_URL, GN605A_NAME,
    source_type="official_gazette",
    effective_date="2026-01-01",
    decay_risk="event_triggered",
    next_review="New wage order gazette",
))

pairs.append(p(
    "tier1a_gn605a_007_20260603", "gn605a",
    "Sekta ya umma inalipwa mshahara gani Tanzania tangu Julai 2025?",
    "Wafanyakazi wa serikali (sekta ya umma) Tanzania Bara wanalipwa mshahara wa chini wa TZS 500,000 kwa mwezi, kuanzia Julai 2025, kufuatia tangazo la Rais Samia. GN 605A inashughulikia sekta ya faragha peke yake. Thibitisha na Hazina.",
    "What is the public sector minimum wage in Tanzania since July 2025?",
    "Government employees (public sector) in Tanzania Mainland receive a minimum wage of TZS 500,000 per month from July 2025, following President Samia's announcement. GN 605A covers the private sector only. Confirm with the Treasury.",
    GN605A_URL, GN605A_NAME,
    source_type="official_gazette",
    effective_date="2025-07-01",
    decay_risk="event_triggered",
    next_review="New public sector salary circular",
))

pairs.append(p(
    "tier1a_gn605a_008_20260603", "gn605a",
    "GN 605A inashughulikia sekta ngapi?",
    "GN 605A inashughulikia sekta 16 na sekta ndogo 46 za sekta ya faragha Tanzania Bara. Kila sekta ina kiwango chake cha mshahara wa chini kulingana na mazingira ya kazi. Thibitisha sekta yako na MLYWF.",
    "How many sectors does GN 605A cover?",
    "GN 605A covers 16 sectors and 46 sub-sectors of the private sector in Tanzania Mainland. Each sector has its own minimum wage level based on working conditions. Confirm your sector with MLYWF.",
    GN605A_URL, GN605A_NAME,
    source_type="official_gazette",
    effective_date="2026-01-01",
    decay_risk="event_triggered",
    next_review="New wage order gazette",
))

pairs.append(p(
    "tier1a_gn605a_009_20260603", "gn605a",
    "Mwajiri anapaswa kutekeleza GN 605A ndani ya muda gani?",
    "Mwajiri alipaswa kutekeleza GN 605A kuanzia malipo ya kwanza ya mishahara ya Januari 2026. Utekelezaji haukuwa na kipindi cha mpito — ufanisi ulianza moja kwa moja tarehe 1 Januari 2026. Thibitisha na MLYWF.",
    "When must an employer implement GN 605A?",
    "Employers were required to implement GN 605A from the first payroll of January 2026. There was no transition period — the order took effect immediately on 1 January 2026. Confirm with MLYWF.",
    GN605A_URL, GN605A_NAME,
    source_type="official_gazette",
    effective_date="2026-01-01",
    decay_risk="event_triggered",
    next_review="New wage order gazette",
))

pairs.append(p(
    "tier1a_gn605a_010_20260603", "gn605a",
    "Adhabu kwa mwajiri anayelipa chini ya mshahara wa chini wa GN 605A ni nini?",
    "Mwajiri anayelipa chini ya kiwango cha mshahara wa chini anaweza kukabili: malimbikizo ya tofauti ya mshahara, faini chini ya ELRA, au kesi ya kisheria iliyowasilishwa na mfanyakazi. Ukaguzi wa MLYWF unaweza kuanzisha hatua za kisheria. Thibitisha na mshauri wa kisheria.",
    "What is the penalty for an employer paying below the GN 605A minimum wage?",
    "An employer paying below the minimum wage may face: back-payment of wage shortfalls, fines under ELRA, or legal proceedings filed by the employee. MLYWF labour inspectors can initiate enforcement action. Confirm with a legal adviser.",
    GN605A_URL, GN605A_NAME,
    source_type="official_gazette",
    effective_date="2026-01-01",
    decay_risk="event_triggered",
    next_review="New wage order gazette",
))

pairs.append(p(
    "tier1a_gn605a_011_20260603", "gn605a",
    "NSSF inacheswa vipi kwa mshahara wa chini wa GN 605A?",
    "NSSF inacheswa kwa asilimia 20 ya mshahara ghafi (10% mwajiri + 10% mfanyakazi). Kwa mshahara wa chini wa TZS 358,322: mfanyakazi analipa TZS 35,832; mwajiri analipa TZS 35,832 pia. Jumlisha: mchango wote wa NSSF ni TZS 71,664 kwa mwezi. Thibitisha na NSSF.",
    "How is NSSF calculated on the GN 605A average minimum wage?",
    "NSSF is calculated at 20% of gross wage (10% employer + 10% employee). On the TZS 358,322 average minimum wage: employee pays TZS 35,832; employer pays TZS 35,832. Total NSSF contribution: TZS 71,664 per month. Confirm with NSSF.",
    NSSF_URL, NSSF_NAME,
    effective_date="2026-01-01",
    decay_risk="event_triggered",
    next_review="New wage order or NSSF Act amendment",
))

pairs.append(p(
    "tier1a_gn605a_012_20260603", "gn605a",
    "SDL inacheswa vipi kwa mshahara wa chini wa GN 605A?",
    "SDL (Skills and Development Levy) ni asilimia 3.5 ya jumla ya mishahara ya wafanyakazi wote kwa mwajiri mwenye wafanyakazi 10 au zaidi. Kwa mshahara wa chini wa TZS 358,322: SDL = TZS 12,541 kwa mfanyakazi mmoja kwa mwezi. Inalipwa na mwajiri. Thibitisha na TRA.",
    "How is SDL calculated on the GN 605A average minimum wage?",
    "SDL (Skills and Development Levy) is 3.5% of total gross wages for employers with 10+ employees. On TZS 358,322 average minimum wage: SDL = TZS 12,541 per employee per month. Paid by the employer. Confirm with TRA.",
    TRA_PAYE_URL, TRA_PAYE_NAME,
    effective_date="2026-01-01",
    decay_risk="event_triggered",
    next_review="New wage order or Finance Act",
))

pairs.append(p(
    "tier1a_gn605a_013_20260603", "gn605a",
    "Mfanyakazi wa majaribio (probationary employee) ana haki ya mshahara wa chini wa GN 605A?",
    "Ndiyo. Mfanyakazi katika kipindi cha majaribio ana haki ya angalau kiwango cha chini cha GN 605A cha sekta husika. Muda wa majaribio haupunguzi haki ya mshahara wa chini. Thibitisha na MLYWF.",
    "Is a probationary employee entitled to the GN 605A minimum wage?",
    "Yes. An employee on probation is entitled to at least the GN 605A minimum wage for their sector. The probation period does not reduce the right to minimum pay. Confirm with MLYWF.",
    GN605A_URL, GN605A_NAME,
    source_type="official_gazette",
    effective_date="2026-01-01",
    decay_risk="event_triggered",
    next_review="New wage order gazette",
))

pairs.append(p(
    "tier1a_gn605a_014_20260603", "gn605a",
    "Mfanyakazi wa muda mfupi (part-time) ana haki ya mshahara wa chini?",
    "Ndiyo, kwa msingi wa pro-rata. Mfanyakazi wa muda mfupi ana haki ya mshahara wa chini wa GN 605A kuhesabiwa kwa idadi ya masaa aliyofanya kazi ikilinganishwa na masaa ya kawaida ya wiki ya kazi. Thibitisha na MLYWF.",
    "Does a part-time worker have the right to the minimum wage under GN 605A?",
    "Yes, on a pro-rata basis. A part-time worker is entitled to the GN 605A minimum wage calculated according to the hours worked compared to the normal working week. Confirm with MLYWF.",
    GN605A_URL, GN605A_NAME,
    source_type="official_gazette",
    effective_date="2026-01-01",
    decay_risk="event_triggered",
    next_review="New wage order gazette",
))

pairs.append(p(
    "tier1a_gn605a_015_20260603", "gn605a",
    "GN 605A inahusu wafanyakazi wa sekta ya kilimo?",
    "Ndiyo. Sekta ya kilimo imejumuishwa katika GN 605A. Kiwango halisi cha mshahara wa chini kwa kilimo kinatofautiana na sekta nyingine — thibitisha kiwango cha sasa kwa sekta ya kilimo na MLYWF.",
    "Does GN 605A apply to workers in the agricultural sector?",
    "Yes. The agricultural sector is included in GN 605A. The exact minimum wage for agriculture differs from other sectors — confirm the current agricultural sector rate with MLYWF.",
    GN605A_URL, GN605A_NAME,
    source_type="official_gazette",
    effective_date="2026-01-01",
    decay_risk="event_triggered",
    next_review="New wage order gazette",
))

pairs.append(p(
    "tier1a_gn605a_016_20260603", "gn605a",
    "Mgeni wa Tanzania anaweza kulipwa chini ya mshahara wa chini wa GN 605A?",
    "Hapana. GN 605A inatumika kwa wafanyakazi wote wanaofanya kazi Tanzania Bara, bila kujali uraia. Mwajiri hawezi kulipa mfanyakazi mgeni mshahara chini ya kiwango cha GN 605A. Thibitisha na MLYWF.",
    "Can a foreign worker in Tanzania be paid below the GN 605A minimum wage?",
    "No. GN 605A applies to all workers employed in Tanzania Mainland, regardless of citizenship. An employer cannot pay a foreign employee below the GN 605A rate. Confirm with MLYWF.",
    GN605A_URL, GN605A_NAME,
    source_type="official_gazette",
    effective_date="2026-01-01",
    decay_risk="event_triggered",
    next_review="New wage order gazette",
    pair_type="adversarial",
))

pairs.append(p(
    "tier1a_gn605a_017_20260603", "gn605a",
    "WCF inacheswa vipi kwa mshahara wa chini wa GN 605A?",
    "WCF (Workers Compensation Fund) ni asilimia 0.5 ya jumla ya mishahara ghafi — inalipwa na mwajiri peke yake. Kwa mshahara wa chini wa TZS 358,322: WCF = TZS 1,792 kwa mfanyakazi kwa mwezi. Thibitisha na WCF.",
    "How is WCF calculated on the GN 605A minimum wage?",
    "WCF (Workers Compensation Fund) is 0.5% of total gross wages — paid by the employer only. On TZS 358,322 minimum wage: WCF = TZS 1,792 per employee per month. Confirm with WCF.",
    GN605A_URL, GN605A_NAME,
    source_type="official_gazette",
    effective_date="2026-01-01",
    decay_risk="event_triggered",
    next_review="New wage order gazette",
))

pairs.append(p(
    "tier1a_gn605a_018_20260603", "gn605a",
    "Gharama yote ya mwajiri kwa mfanyakazi mmoja mwenye mshahara wa chini wa GN 605A ni kiasi gani?",
    "Kwa mshahara wa chini wa wastani wa TZS 358,322/mwezi: NSSF ya mwajiri TZS 35,832 (10%); SDL TZS 12,541 (3.5%); WCF TZS 1,792 (0.5%). Jumla ya gharama ya ziada kwa mwajiri: TZS 50,165. Gharama yote ya mwajiri: TZS 358,322 + TZS 50,165 = TZS 408,487/mwezi. Thibitisha na TRA na NSSF.",
    "What is the total employer cost for one employee at the GN 605A average minimum wage?",
    "On TZS 358,322/month minimum wage: employer NSSF TZS 35,832 (10%); SDL TZS 12,541 (3.5%); WCF TZS 1,792 (0.5%). Total employer add-on cost: TZS 50,165. Full employer cost: TZS 358,322 + TZS 50,165 = TZS 408,487/month. Confirm with TRA and NSSF.",
    NSSF_URL, NSSF_NAME,
    effective_date="2026-01-01",
    decay_risk="event_triggered",
    next_review="New wage order or statutory rate change",
))

pairs.append(p(
    "tier1a_gn605a_019_20260603", "gn605a",
    "PAYE inacheswa vipi kwa mshahara wa chini wa TZS 358,322?",
    "Mshahara ghafi TZS 358,322. Punguza NSSF ya mfanyakazi (10%): TZS 358,322 − TZS 35,832 = TZS 322,490. Kanda za PAYE: TZS 0–270,000 = TZS 0; TZS 270,001–322,490 (TZS 52,490 × 8%) = TZS 4,199. PAYE ya mwezi: TZS 4,199. Thibitisha hesabu na TRA.",
    "How is PAYE calculated on the GN 605A average minimum wage of TZS 358,322?",
    "Gross wage TZS 358,322. Deduct employee NSSF (10%): TZS 358,322 − TZS 35,832 = TZS 322,490. PAYE bands: TZS 0–270,000 = TZS 0; TZS 270,001–322,490 (TZS 52,490 × 8%) = TZS 4,199. Monthly PAYE: TZS 4,199. Confirm the calculation with TRA.",
    TRA_PAYE_URL, TRA_PAYE_NAME,
    effective_date="2026-01-01",
    decay_risk="event_triggered",
    next_review="New wage order or Finance Act rate change",
))

pairs.append(p(
    "tier1a_gn605a_020_20260603", "gn605a",
    "Nithibitishe kiwango cha mshahara wa chini wa sekta yangu — niende wapi?",
    "Kiwango cha mshahara wa chini kwa sekta yako kinapatikana: (1) Tovuti ya MLYWF (mlywf.go.tz) au ofisi yoyote ya kazi; (2) TanzLII (tanzlii.org) — tafuta 'GN 605A'; (3) Shirika la wafanyakazi au chama cha waajiri cha sekta yako. Thibitisha kiwango halisi kabla ya kulipa.",
    "How do I verify the minimum wage for my specific sector under GN 605A?",
    "The minimum wage for your sector is available at: (1) MLYWF website (mlywf.go.tz) or any labour office; (2) TanzLII (tanzlii.org) — search 'GN 605A'; (3) Your sector's trade union or employers' association. Confirm the exact rate before processing payroll.",
    GN605A_URL, GN605A_NAME,
    source_type="official_gazette",
    effective_date="2026-01-01",
    decay_risk="event_triggered",
    next_review="New wage order gazette",
))

# ─────────────────────────────────────────────────────────────────────────────
# Work Permits — 5 pairs (first 5 only per Batch A instructions)
# Source: immigration.go.tz (scraped successfully)
# ─────────────────────────────────────────────────────────────────────────────

pairs.append(p(
    "tier1a_permit_001_20260603", "work_permits",
    "Mgeni anayefanya kazi Tanzania anahitaji kibali gani?",
    "Mgeni anayeajiriwa na kampuni Tanzania anahitaji Kibali cha Makazi daraja C (Residence Permit Class C) — kibali cha kufanya kazi. Kibali hutolewa na Idara ya Uhamiaji. Mgeni lazima awe na mwajiri rasmi kabla ya kuomba kibali. Thibitisha na Idara ya Uhamiaji.",
    "What permit does a foreign national employed in Tanzania need?",
    "A foreign national employed by a company in Tanzania needs a Class C Residence Permit — a work permit. It is issued by the Immigration Department. The foreigner must have a formal employer before applying. Confirm with the Immigration Department.",
    IMMIG_URL, IMMIG_NAME,
    effective_date="2025-07-28",
    decay_risk="event_triggered",
    next_review="GN 487A enforcement update or immigration regulation change",
))

pairs.append(p(
    "tier1a_permit_002_20260603", "work_permits",
    "Mwekezaji mgeni Tanzania anahitaji kibali gani cha makazi?",
    "Mwekezaji mgeni anayefanya biashara kwa akaunti yake mwenyewe anahitaji Kibali cha Makazi daraja B (Residence Permit Class B) — kinachojulikana kama kibali cha mwekezaji. Kinatolewa kwa wanaofanya uwekezaji unaokidhi vigezo vya TIC. Thibitisha na Idara ya Uhamiaji na TIC.",
    "What residence permit does a foreign investor in Tanzania need?",
    "A foreign investor running a business on their own account needs a Class B Residence Permit — known as an investor permit. It is granted to those making investments meeting TIC criteria. Confirm with the Immigration Department and TIC.",
    IMMIG_URL, IMMIG_NAME,
    effective_date="2025-07-28",
    decay_risk="event_triggered",
    next_review="Immigration regulation change or GN 487A update",
))

pairs.append(p(
    "tier1a_permit_003_20260603", "work_permits",
    "Mtu asiye raia anayefanya biashara bila kibali Tanzania anakabili adhabu gani?",
    "Chini ya GN 487A (iliyoanza Julai 2025): faini ya chini ya TZS 10,000,000 na/au kifungo cha hadi miezi 6 na kufutwa kwa viza. Sheria hii inashughulikia shughuli 15 zilizopigwa marufuku kwa wageni — ikiwemo biashara ya jumla/reja reja, uhamishaji wa pesa za simu, ukarabati wa simu, na saluni. Thibitisha na Idara ya Uhamiaji.",
    "What penalty does a non-citizen face for doing business without a permit in Tanzania?",
    "Under GN 487A (effective July 2025): a minimum fine of TZS 10,000,000 and/or imprisonment up to 6 months plus visa revocation. This order covers 15 activities prohibited for non-citizens — including wholesale/retail trade, mobile money transfers, phone repair, and salons. Confirm with the Immigration Department.",
    IMMIG_URL, IMMIG_NAME,
    effective_date="2025-07-28",
    decay_risk="event_triggered",
    next_review="GN 487A enforcement update",
))

pairs.append(p(
    "tier1a_permit_004_20260603", "work_permits",
    "Raia wa Tanzania anayemsaidia mgeni kufanya shughuli zilizopigwa marufuku ana hatari gani?",
    "Chini ya GN 487A: raia wa Tanzania anayemsaidia mgeni kufanya shughuli zilizopigwa marufuku anakabili faini ya TZS 5,000,000 au kifungo cha miezi 3 gerezani. Hata kukodisha duka au akaunti ya benki kwa mgeni kwa madhumuni hayo kunaweza kufuatwa. Thibitisha na mshauri wa kisheria.",
    "What risk does a Tanzanian citizen face for helping a non-citizen conduct prohibited business?",
    "Under GN 487A: a Tanzanian facilitating a non-citizen's prohibited activities faces a TZS 5,000,000 fine or 3 months imprisonment. Even renting a shop or bank account to a foreigner for such purposes may be pursued. Confirm with a legal adviser.",
    IMMIG_URL, IMMIG_NAME,
    source_type="official_gazette",
    effective_date="2025-07-28",
    decay_risk="event_triggered",
    next_review="GN 487A enforcement update",
))

pairs.append(p(
    "tier1a_permit_005_20260603", "work_permits",
    "Ombi la kibali cha makazi Tanzania linafanywa wapi mtandaoni?",
    "Maombi ya vibali vya makazi (daraja A, B, C) yanafanywa mtandaoni kupitia mfumo wa e-services wa Idara ya Uhamiaji kwenye tovuti immigration.go.tz. Mwombaji anatakiwa kuunda akaunti, kujaza fomu, na kupakia hati zinazohitajika. Thibitisha mahitaji ya sasa na Idara ya Uhamiaji.",
    "Where is a Tanzania residence permit application submitted online?",
    "Applications for residence permits (Class A, B, C) are submitted online through the Immigration Department's e-services system at immigration.go.tz. The applicant creates an account, completes the form, and uploads required documents. Confirm current requirements with the Immigration Department.",
    IMMIG_URL, IMMIG_NAME,
    effective_date="2025-07-28",
    decay_risk="annual",
    next_review="Immigration portal change",
))

# ─────────────────────────────────────────────────────────────────────────────
# Dedup check against existing questions
# ─────────────────────────────────────────────────────────────────────────────
filtered = []
skipped = []
for pair in pairs:
    q_sw = pair["question_sw"].lower().strip()
    q_en = pair["question_en"].lower().strip()
    if q_sw in existing_questions or q_en in existing_questions:
        skipped.append(pair["id"])
    else:
        filtered.append(pair)

print(f"Generated: {len(pairs)}  Skipped (dupes): {len(skipped)}  Kept: {len(filtered)}")
if skipped:
    print(f"Skipped IDs: {skipped}")

# Save
with open(OUT_FILE, "w", encoding="utf-8") as f:
    for pair in filtered:
        f.write(json.dumps(pair, ensure_ascii=False) + "\n")

print(f"Saved {len(filtered)} pairs to {OUT_FILE}")
