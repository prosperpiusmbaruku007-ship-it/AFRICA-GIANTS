#Read this file completely then execute every instruction below exactly as written.

TASK: Apply all PENDING corrections below to:
datasets/tier1a/raw_sources/raw_pairs_batch_009.jsonl

For each correction:
1. Search for the exact wrong phrase
2. Replace with the correct version
3. Update locked_facts.json with the verified fact
4. Run check_locked_facts.py after all corrections
5. Commit once with all changes

Show count of pairs changed per correction.
Show commit hash at the end then STOP.

============================================================
CORRECTION 1 — GN487A TRANSITIONAL PROVISION
Status: PENDING
Severity: CRITICAL
Evidence: Bowmans Law July 2025, MAK Africa Legal
August 2025, TanzaniaInvest July 2025, The Citizen
July 2025, IMMMA/DLA Piper 2025 — ALL CONFIRM
============================================================

WRONG PHRASES — search and replace all of these:
- "Hakukuwa na kipindi cha mpito"
- "hakukuwa na kipindi cha mpito"
- "Hakuna kipindi cha mazoea"
- "hakuna kipindi cha mazoea"
- "wageni waliokuwa na biashara katika orodha ya 15
  tangu 28 Julai 2025 wamekuwa wakikosea sheria"

REPLACE WITH:
"GN 487A ina masharti ya mpito: wageni waliokuwa
na leseni halali tarehe 28 Julai 2025 katika
shughuli zilizokatazwa waliruhusiwa kuendelea mpaka
leseni zao ziishe. Baada ya leseni kuisha, upya
(renewal) haukuruhusiwa na leseni mpya haikuweza
kutolewa."

Add to locked_facts.json:
KEY: "gn487a_transitional_provision"
VALUE: "Non-citizens with valid licences at 28 July
2025 may continue until licence expiry. No renewal
permitted. No new licences issued for prohibited
activities. Source: Bowmans, MAK Africa Legal,
TanzaniaInvest, The Citizen — all confirmed."

============================================================
CORRECTION 2 — EFD THRESHOLD TZS 11M
Status: PENDING
Severity: CRITICAL
Evidence: TRA official website tra.go.tz/page/
efd-vfd-suppliers, RSM Tanzania Tax Guide 2025/26,
Auditax International February 2025
============================================================

WRONG PHRASES — search and replace:
- "Kila biashara Tanzania lazima iwe na EFD machine"
- "kila biashara inahitaji EFD bila kizingiti"
- Any pair implying EFD is required with no threshold

REPLACE WITH (add to relevant EFD pairs):
"EFD inahitajika kwa biashara zenye mauzo ya TZS
milioni 11 au zaidi kwa mwaka. Biashara zenye mauzo
chini ya TZS milioni 11 zinaweza kutumia risiti za
kawaida (manual receipts). VAT registered businesses
zote lazima zitumie EFD bila kujali kiasi cha mauzo.
Thibitisha na TRA tra.go.tz."

Add to locked_facts.json:
KEY: "efd_threshold_tzs_11m"
VALUE: "EFD required for businesses with annual
turnover TZS 11 million and above. Below TZS 11M
may use manual receipts. All VAT-registered
businesses must use EFD regardless of turnover.
Source: TRA official website, RSM Tax Guide 2025/26."

============================================================
CORRECTION 3 — VISA REVOCATION LANGUAGE
Status: PENDING
Severity: OVERSTATED
Evidence: The Star July 2025 (possible revocation),
The Citizen July 2025 (risk having their...revoked).
Bowmans uses AND (mandatory). Sources genuinely
disagree — use softer language.
============================================================

WRONG PHRASES — search and replace:
- "kufutwa kwa visa ni lazima daima"
- "visa itafutwa lazima"
- "kufutwa kwa visa/kibali cha kuingia Tanzania
  ni lazima daima"
- "kufutwa kwa visa ni lazima daima bila exception"

REPLACE WITH:
"kufutwa kwa visa na kibali cha ukaazi kunaweza
kutokea kama sehemu ya adhabu — thibitisha na
Idara ya Uhamiaji na wakili wa biashara kwa
hali yako maalum"

Add to locked_facts.json:
KEY: "gn487a_visa_revocation"
VALUE: "Visa revocation is a possible consequence
not universally mandatory in all sources. Bowmans
says AND (mandatory). The Star and The Citizen say
possible/risk. Train model to say CAN be revoked
not WILL always be revoked. Use: kunaweza kutokea
not ni lazima daima."

============================================================
CORRECTION 4 — VAT WITHHOLDING REMITTANCE DEADLINE
Status: PENDING
Severity: CRITICAL
Evidence: PWC Tax Summaries 2025, Lexology Finance
Act 2025 analysis, Habib Advisory Tax Guide 2025/26,
TRA official VAT returns page — ALL SAY 20th
============================================================

WRONG PHRASES — search and replace:
- "ndani ya siku 7 baada ya mwisho wa mwezi"
- "siku 7 baada ya mwisho"
- Any pair saying VAT withholding goes to TRA
  within 7 days

REPLACE WITH:
"VAT withholding inalipwa TRA tarehe 20 ya mwezi
unaofuata — siku ile ile ya VAT return ya kawaida.
Si siku 7. Thibitisha na TRA tra.go.tz."

Add to locked_facts.json:
KEY: "vat_withholding_remittance_deadline"
VALUE: "VAT withholding remitted to TRA by 20th of
following month — same deadline as VAT return.
NOT 7 days. Source: PWC Tax Summaries 2025, Finance
Act 2025 analysis (Lexology), Habib Advisory
Tax Guide 2025/26."

============================================================
CORRECTION 5 — VAT LATE REGISTRATION PENALTY
2.5% INVENTED
Status: PENDING
Severity: CRITICAL
Evidence: VAT Act Tanzania Cap 148 — actual penalty
is fine up to TZS 200,000 and/or 2-12 months
imprisonment plus interest. NO 2.5% monthly rate
exists in the VAT Act.
============================================================

WRONG PHRASES — search ALL pairs for:
- "2.5%" in any VAT registration context
- "Faini ya 2.5% kwa kila mwezi wa kuchelewa"

REMOVE completely. REPLACE WITH:
"Adhabu ya kushindwa kusajili VAT kwa wakati ni
faini ya hadi TZS 200,000 na/au kifungo cha miezi
2 hadi 12, pamoja na riba kwa VAT iliyopaswa
kukusanywa tangu kufika kizingiti. Hakuna asilimia
ya 2.5% kwa mwezi katika Sheria ya VAT.
Thibitisha na TRA tra.go.tz."

Add to locked_facts.json:
KEY: "vat_late_registration_penalty"
VALUE: "Penalty for failure to register VAT: fine
up to TZS 200,000 AND/OR imprisonment 2-12 months
PLUS interest on unpaid VAT. NO 2.5% monthly rate
exists in the VAT Act. Source: VAT Act Tanzania
Cap 148."

============================================================
CORRECTION 6 — NO SMALL BUSINESS EXCEPTION
IN GN487A
Status: PENDING
Severity: CRITICAL
Evidence: GN 487A gazette text — Schedule has no
size threshold. Bowmans, MAK Africa Legal, all
sources confirm flat TZS 10M minimum with no
small business carve-out.
============================================================

WRONG PHRASES — search and replace:
- "TZS milioni 5 kwa biashara ndogo"
- "msamaha kwa biashara ndogo" in GN487A context
- Any pair implying reduced penalty for small
  businesses under GN487A

REPLACE WITH:
"Hakuna msamaha kwa biashara ndogo katika GN 487A.
Faini ya angalau TZS milioni 10 inatumika kwa
wageni wote bila kujali ukubwa wa biashara, mtaji,
au mapato. Thibitisha na Idara ya Uhamiaji."

Add to locked_facts.json:
KEY: "gn487a_no_small_business_exception"
VALUE: "GN 487A has NO small business exception.
TZS 10M minimum penalty applies equally to all
non-citizens regardless of business size, revenue,
or capital. The TZS 5M figure for small businesses
is fabricated. Source: GN 487A gazette Schedule."

============================================================
CORRECTION 7 — BRELA DEREGISTRATION NOT AUTOMATIC
FOR GN487A VIOLATIONS
Status: PENDING
Severity: CRITICAL
Evidence: GN 487A text lists penalties as fine,
imprisonment, visa revocation. No BRELA
deregistration listed as penalty. Companies Act
Tanzania has its own separate grounds.
============================================================

WRONG PHRASES — search and replace:
- "BRELA inaweza kufuta kampuni ya mgeni moja kwa
  moja kwa kukiuka GN 487A"
- "BRELA itafuta kampuni moja kwa moja"

REPLACE WITH:
"Ukiukaji wa GN 487A unaweza kusababisha adhabu za
jinai na hatua za uhamiaji. Kufutwa kwa kampuni na
BRELA ni mchakato tofauti wa kisheria wenye
masharti yake chini ya Sheria za Kampuni — si
adhabu ya moja kwa moja ya GN 487A.
Thibitisha na wakili wa biashara."

============================================================
CORRECTION 8 — CLOSING BUSINESS DOES NOT ERASE
TAX DEBT
Status: PENDING
Severity: CRITICAL
Evidence: Tax Administration Act Tanzania —
universal tax law principle confirmed.
============================================================

WRONG PHRASES — search and replace:
- Any pair implying kufunga biashara cancels
  TRA obligations or past tax debts

REPLACE WITH:
"Kufunga biashara kunasimamisha shughuli za
baadaye lakini hakufuti wajibu wa kodi uliotokana
na kipindi ambacho biashara ilikuwa inafanya kazi.
TRA inaweza kudai PAYE, VAT, SDL, faini, na riba
zilizobaki hata baada ya biashara kufungwa.
Thibitisha na TRA tra.go.tz."

============================================================
CORRECTION 9 — SDL BASE IS CASH EMOLUMENTS ONLY
Status: PENDING
Severity: MODERATE
Evidence: PWC Tax Summaries 2025 confirms SDL is
3.5% of gross CASH emoluments. TRA SDL page and
RSM Tax Guide 2025/26 confirm cash only.
============================================================

WRONG PHRASES — search and replace:
- Any SDL pair claiming SDL applies to benefits
  in kind (nyumba ya kampuni, gari la kampuni,
  bima ya afya)

ADD clarification to such pairs:
"SDL inakokotolewa kwa malipo ya FEDHA (cash
emoluments) peke yake — si faida zisizo za fedha
(benefits in kind) kama nyumba ya kampuni, gari
la kampuni, au bima ya afya inayolipwa moja kwa
moja. SDL base: mshahara wa msingi + posho za
fedha + bonasi za fedha. Thibitisha na TRA."

============================================================
CORRECTION 10 — EAC CITIZENS GN487A AMBIGUITY
Status: PENDING
Severity: OVERSTATED
Evidence: EAC Common Market Protocol covers right
of establishment and free movement of services —
genuine legal ambiguity exists between GN487A
and EAC Protocol obligations.
============================================================

WRONG PHRASES — search and replace:
- "Raia wa EAC hawana haki zozote"
- "hakuna mjadala wowote kuhusu raia wa EAC"
- Any pair saying EAC rights are completely
  irrelevant to GN487A with no nuance

ADD to such pairs:
"GN 487A kwa maandishi yake inatumika kwa
non-citizens wote bila kutenganisha raia wa EAC.
Hata hivyo, uhusiano wake na haki za EAC Common
Market Protocol (uhuru wa kuanzisha biashara na
huduma) unaweza kuhitaji tafsiri ya kisheria ya
kina. Thibitisha na wakili wa biashara."

============================================================
CORRECTION 11 — NSSF PAYMENT DATE UNCLEAR
Status: PENDING
Severity: MODERATE
Evidence: Dataset gave inconsistent dates (10th,
end of month) without citing official NSSF source.
Reviewer flagged this correctly.
============================================================

WRONG PHRASES — search and replace:
- "tarehe 10 au mwisho wa mwezi" for NSSF deadline
- Any pair giving inconsistent NSSF dates

REPLACE WITH:
"NSSF iwasilishwe mwishoni mwa mwezi unaofuata
mwezi wa malipo ya wafanyakazi. Thibitisha tarehe
halisi ya sasa na nssf.or.tz kwa sababu TRA
inaweza kutangaza mabadiliko."

Add to locked_facts.json:
KEY: "nssf_payment_deadline"
VALUE: "NSSF due by end of month following payroll
month. Dataset had inconsistent dates — always
direct users to nssf.or.tz to confirm current
deadline. Do not state specific date without
official confirmation."

============================================================
CORRECTION 12 — SDL RATE CONFIRMED 3.5%
Status: INFORMATIONAL — NO CHANGE NEEDED
Evidence: Finance Act 2023 reduced SDL from 4% to
3.5% effective 1 July 2023. PWC Tax Summaries 2025
confirms 3.5%. Reviewer questioned this but was
wrong. 3.5% IS CORRECT for 2025/26.
============================================================

No changes needed. SDL is correctly stated as
3.5% in batch_009. Confirm this in locked_facts.json:

Add to locked_facts.json:
KEY: "sdl_rate_2025"
VALUE: "SDL rate is 3.5% of gross cash emoluments
effective 1 July 2023 (Finance Act 2023 reduced
from 4%). Minimum 10 employees threshold applies.
Source: PWC Tax Summaries 2025, Finance Act 2023."

============================================================
CORRECTION 13 — SDL EMPLOYEE THRESHOLD CONFIRMED 10
Status: INFORMATIONAL — NO CHANGE NEEDED
Evidence: PWC Tax Summaries 2025 and RSM Tax Guide
2025/26 both confirm minimum 10 employees.
Reviewer questioned this but was wrong.
10 employees IS CORRECT.
============================================================

No changes needed. Confirm in locked_facts.json:

Add to locked_facts.json:
KEY: "sdl_employee_threshold"
VALUE: "SDL applies to employers with minimum 10
employees. Below 10 employees = no SDL obligation.
Source: PWC Tax Summaries 2025, RSM Tax Guide
2025/26, TRA SDL official page."

============================================================
[ADD NEW CORRECTIONS HERE AS YOU REVIEW MORE PAIRS]
============================================================

CORRECTION 14 — [TITLE]
Status: PENDING
Severity: [CRITICAL / OVERSTATED / MODERATE]
Evidence: [source URL or name]
============================================================

WRONG PHRASES:
- [paste wrong phrase from pair here]

REPLACE WITH:
[paste correct version here]

Add to locked_facts.json:
KEY: "[key_name]"
VALUE: "[correct fact + source]"

============================================================
CORRECTION 15 — [TITLE]
Status: PENDING
Severity:
Evidence:
============================================================

WRONG PHRASES:
-

REPLACE WITH:

Add to locked_facts.json:
KEY:
VALUE:

============================================================
VERIFICATION SCRIPT — RUN AFTER ALL CORRECTIONS
============================================================

python -c "
import json

with open('datasets/tier1a/raw_sources/raw_pairs_batch_009.jsonl',
          encoding='utf-8') as f:
    lines = [l for l in f if l.strip()]

checks = {
    'transitional_fixed': 0,
    'efd_threshold_present': 0,
    'visa_softened': 0,
    'vat_withholding_20th': 0,
    'vat_2_5_pct_REMAINING': 0,
    'no_small_biz_exception': 0,
}

for line in lines:
    d = json.loads(line)
    out = d.get('output', '')
    inst = d.get('instruction', '')
    if 'masharti ya mpito' in out:
        checks['transitional_fixed'] += 1
    if 'milioni 11' in out and 'EFD' in out:
        checks['efd_threshold_present'] += 1
    if 'inaweza kutokea kama sehemu ya adhabu' in out:
        checks['visa_softened'] += 1
    if 'tarehe 20' in out and 'withholding' in out.lower():
        checks['vat_withholding_20th'] += 1
    if '2.5%' in out and 'VAT' in out:
        checks['vat_2_5_pct_REMAINING'] += 1
    if 'Hakuna msamaha kwa biashara ndogo' in out:
        checks['no_small_biz_exception'] += 1

print(f'Total pairs: {len(lines)}')
for k, v in checks.items():
    flag = ' *** WARNING' if k == 'vat_2_5_pct_REMAINING' and v > 0 else ''
    print(f'  {k}: {v}{flag}')
"

python check_locked_facts.py \
  datasets/tier1a/raw_sources/raw_pairs_batch_009.jsonl

git add datasets/tier1a/raw_sources/raw_pairs_batch_009.jsonl
git add datasets/tier1a/raw_sources/locked_facts.json
git commit -m "batch_009: apply corrections canvas — GN487A transition, EFD threshold, VAT deadline, 2.5% removed, visa language, no small biz exception"
git push origin main
Show commit hash and verification counts then STOP.

============================================================
CORRECTION 14 — PAYE: EMPLOYEE DOES NOT LOSE ANYTHING
IS OVERSTATED
Status: PENDING
Severity: MODERATE
Evidence: General tax law principle — while PAYE is
employer's obligation to remit, employee can face
compliance record issues, tax clearance disputes,
or audit questions if employer failed to remit
despite deducting.
============================================================

WRONG PHRASES — search and replace:
- "mfanyakazi HUPOTEZA CHOCHOTE kwa upande wa PAYE"
- "mfanyakazi hapotezi chochote"

REPLACE WITH:
"PAYE ni wajibu wa mwajiri kuwasilisha TRA —
si akiba ya mfanyakazi. Hata hivyo kama mwajiri
alikata PAYE lakini hakuituma TRA, mfanyakazi
anaweza kukabiliwa na matatizo ya rekodi za kodi,
uthibitisho wa malipo, au maswali ya ukaguzi.
Mfanyakazi anaweza kulalamika TRA au Mahakama
ya Kazi. Thibitisha na TRA tra.go.tz na
Wizara ya Kazi."

============================================================
CORRECTION 15 — GN487A BENEFICIAL OWNERSHIP NOT
EXPLICITLY IN ORDER TEXT
Status: PENDING
Severity: MODERATE
Evidence: GN 487A gazette text reviewed — no
explicit "beneficial ownership test" language
found in the Order itself. This is legal
interpretation, not written law.
============================================================

WRONG PHRASES — search and replace:
- "Sheria inazingatia udhibiti wa kweli na faida"
  presented as written in GN 487A
- "GN 487A inatambua beneficial ownership wazi"
- Any pair claiming GN 487A explicitly mentions
  beneficial ownership as a test

REPLACE WITH:
"GN 487A haisemi wazi kuhusu 'beneficial ownership'
kama kipimo. Hata hivyo mamlaka za uhamiaji na
mahakama zinaweza kuchunguza udhibiti wa kweli na
mnufaika halisi wa biashara kama sehemu ya uchunguzi
wa ukiukwaji. Thibitisha na wakili wa biashara na
Idara ya Uhamiaji kwa tafsiri ya kisheria ya hali
yako maalum."

============================================================
CORRECTION 16 — ONLINE RETAIL GN487A NOT EXPLICIT
Status: PENDING
Severity: MODERATE
Evidence: GN 487A text does not explicitly mention
online stores or e-commerce. Applying it to online
retail is legal interpretation, not written law.
============================================================

WRONG PHRASES — search and replace:
- Any pair stating definitively that online retail
  owned by non-citizen DEFINITELY violates GN 487A
  without noting this is interpretation

ADD to such pairs:
"GN 487A haisemi wazi 'online store' au biashara
za mtandaoni. Kutumika kwake kwa biashara za
mtandaoni ni tafsiri ya kisheria inayotegemea
maamuzi ya mamlaka au mahakama. Thibitisha na
wakili wa biashara na Idara ya Uhamiaji kwa
hali yako maalum."

============================================================
CORRECTION 17 — PAYE BAND CALCULATIONS NEED VERIFICATION
Status: PENDING
Severity: MODERATE
Evidence: Reviewer correctly flagged that PAYE
band calculations in pairs must be verified
against current TRA tax table. Bands change
with Finance Acts.
============================================================

CONFIRMED PAYE BANDS 2025/26 (from PWC Tax
Summaries confirmed earlier in this project):

Monthly bands Tanzania Mainland:
Band 1: TZS 0 - 270,000 → 0%
Band 2: TZS 270,001 - 520,000 → 8%
Band 3: TZS 520,001 - 760,000 → 20%
Band 4: TZS 760,001 - 1,000,000 → 25%
Band 5: Above TZS 1,000,000 → 30%

Search ALL PAYE calculation pairs and verify
against these exact bands. Fix any that use
wrong thresholds or rates.

Add to locked_facts.json:
KEY: "paye_bands_monthly_2025_26"
VALUE: "Band 1: 0-270,000 = 0%; Band 2:
270,001-520,000 = 8%; Band 3: 520,001-760,000
= 20%; Band 4: 760,001-1,000,000 = 25%;
Band 5: above 1,000,000 = 30%. No personal
relief of TZS 26,000 exists. Source: PWC Tax
Summaries 2025, confirmed from Habib Advisory
Tax Guide 2025/26."