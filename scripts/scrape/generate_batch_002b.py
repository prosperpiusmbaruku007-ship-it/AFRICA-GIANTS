"""
Generate Batch 002B training pairs for AFRICA-GIANTS Tier 1A.

Covers:
  - work_permits (10 pairs): IDs tier1a_permit_006..015
  - withholding_tax (15 pairs): IDs tier1a_wh_001..015
  - vat_edge_cases (15 pairs): IDs tier1a_vat_edge_001..015
  - nssf_edge_cases (10 pairs): IDs tier1a_nssf_edge_001..010

Sources:
  - Withholding: scraped withholding.html (tra.go.tz/page/withholding-tax)
  - VAT edge: scraped vat_edge.html (tra.go.tz/page/value-added-tax-vat)
  - NSSF edge: scraped nssf_edge.html (nssf.go.tz/pages/payment-of-contributions)
  - Work permits: scraped immigration.go.tz + GN 487A locked facts
"""
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_FILE = os.path.join(ROOT, "datasets", "tier1a", "raw_sources", "raw_pairs_batch_002b.jsonl")
EXISTING_FILE = os.path.join(ROOT, "datasets", "tier1a", "raw_sources", "existing_questions.txt")
BATCH_A_FILE = os.path.join(ROOT, "datasets", "tier1a", "raw_sources", "raw_pairs_batch_002a.jsonl")

# Load all existing questions (batch 001 + batch A) for dedup
existing_questions = set()
with open(EXISTING_FILE, encoding="utf-8") as f:
    for line in f:
        existing_questions.add(line.strip().lower())
with open(BATCH_A_FILE, encoding="utf-8") as f:
    for line in f:
        p = json.loads(line)
        existing_questions.add(p["question_sw"].lower().strip())
        existing_questions.add(p["question_en"].lower().strip())


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


TRA_WH_URL   = "https://www.tra.go.tz/page/withholding-tax"
TRA_WH_NAME  = "TRA - Withholding Tax"
TRA_VAT_URL  = "https://www.tra.go.tz/page/value-added-tax-vat"
TRA_VAT_NAME = "TRA - Value Added Tax (VAT)"
NSSF_URL     = "https://www.nssf.go.tz/pages/payment-of-contributions"
NSSF_NAME    = "NSSF - Payment of Contributions"
IMMIG_URL    = "https://www.immigration.go.tz"
IMMIG_NAME   = "Tanzania Immigration Department"
GN487A_URL   = "https://tanzlii.org/akn/tz/act/gn/2025/487a/eng@2025-07-28"
GN487A_NAME  = "Government Notice 487A (GN 487A) - Business Licensing Prohibition Order 2025"

pairs = []

# ─────────────────────────────────────────────────────────────────────────────
# Work Permits — 10 remaining pairs (pairs 006–015)
# ─────────────────────────────────────────────────────────────────────────────

pairs.append(p(
    "tier1a_permit_006_20260603", "work_permits",
    "Vibali 15 vya shughuli vilivyopigwa marufuku kwa wageni chini ya GN 487A ni vipi?",
    "GN 487A (iliyoanza Julai 2025) inapiga marufuku wageni kufanya: biashara ya jumla/reja reja, uhamishaji wa pesa za simu, ukarabati wa simu, saluni na ususi, na shughuli 11 nyingine zilizoorodheshwa kwenye amri. Biashara ya usambazaji mdogo inajumuishwa. Thibitisha orodha kamili na Idara ya Uhamiaji.",
    "What are the 15 business activities prohibited for non-citizens under GN 487A?",
    "GN 487A (effective July 2025) prohibits non-citizens from conducting: wholesale/retail trade, mobile money transfers, phone repair, salon and hairdressing business, and 11 other activities listed in the order. Small distribution business is included. Confirm the full list with the Immigration Department.",
    GN487A_URL, GN487A_NAME,
    source_type="official_gazette",
    effective_date="2025-07-28",
    decay_risk="event_triggered",
    next_review="GN 487A amendment or repeal",
))

pairs.append(p(
    "tier1a_permit_007_20260603", "work_permits",
    "GN 487A ilianza rasmi tarehe ngapi?",
    "GN 487A ilianza rasmi tarehe 28 Julai 2025. Baadaye, Idara ya Uhamiaji iliendesha operesheni ya utekelezaji kuanzia Septemba 11 hadi Oktoba 8, 2025. Thibitisha na Idara ya Uhamiaji.",
    "When did GN 487A officially come into effect?",
    "GN 487A officially came into effect on 28 July 2025. Subsequently, the Immigration Services Department conducted an enforcement exercise from 11 September to 8 October 2025. Confirm with the Immigration Department.",
    GN487A_URL, GN487A_NAME,
    source_type="official_gazette",
    effective_date="2025-07-28",
    decay_risk="event_triggered",
    next_review="GN 487A amendment or repeal",
))

pairs.append(p(
    "tier1a_permit_008_20260603", "work_permits",
    "Mgeni mwenye kibali cha makazi daraja C anaweza kufanya shughuli zilizopigwa marufuku na GN 487A?",
    "Hapana. GN 487A inaweka marufuku ya aina ya shughuli — hata kibali cha kazi halimruhusu mgeni kufanya shughuli zilizoorodheshwa kwenye amri. Sheria hizi mbili zinatumika pamoja. Thibitisha na Idara ya Uhamiaji na mshauri wa kisheria.",
    "Can a non-citizen with a Class C residence permit conduct activities prohibited by GN 487A?",
    "No. GN 487A restricts the type of activity — even a work permit does not authorise a non-citizen to conduct activities listed in the order. Both laws apply concurrently. Confirm with the Immigration Department and a legal adviser.",
    GN487A_URL, GN487A_NAME,
    source_type="official_gazette",
    effective_date="2025-07-28",
    decay_risk="event_triggered",
    next_review="GN 487A amendment or repeal",
    pair_type="adversarial",
))

pairs.append(p(
    "tier1a_permit_009_20260603", "work_permits",
    "Kampuni ya nje (foreign company) inaweza kumiliki duka la reja reja Tanzania?",
    "Hapana chini ya GN 487A. Biashara ya reja reja ni mojawapo ya shughuli 15 zilizopigwa marufuku kwa wageni. Kampuni inayomilikiwa na wageni haiwezi kufanya biashara ya reja reja Tanzania Bara. Thibitisha na Idara ya Uhamiaji na TIC.",
    "Can a foreign-owned company own a retail shop in Tanzania?",
    "No under GN 487A. Retail trade is one of the 15 activities prohibited for non-citizens. A company owned by foreigners cannot conduct retail business in Tanzania Mainland. Confirm with the Immigration Department and TIC.",
    GN487A_URL, GN487A_NAME,
    source_type="official_gazette",
    effective_date="2025-07-28",
    decay_risk="event_triggered",
    next_review="GN 487A amendment or repeal",
    pair_type="adversarial",
))

pairs.append(p(
    "tier1a_permit_010_20260603", "work_permits",
    "Mgeni anafanya ukarabati wa simu Tanzania — ana hatari gani?",
    "Ukarabati wa simu ni mojawapo ya shughuli 15 zilizopigwa marufuku na GN 487A. Mgeni anayefanya ukarabati wa simu bila kibali anakabili: faini ya chini ya TZS 10,000,000, kifungo cha hadi miezi 6, na kufutwa kwa viza. Thibitisha na Idara ya Uhamiaji.",
    "A non-citizen is running a phone repair shop in Tanzania — what is their risk?",
    "Phone repair is one of the 15 activities prohibited by GN 487A. A non-citizen operating phone repair without authorisation faces: a minimum TZS 10,000,000 fine, up to 6 months imprisonment, and visa revocation. Confirm with the Immigration Department.",
    GN487A_URL, GN487A_NAME,
    source_type="official_gazette",
    effective_date="2025-07-28",
    decay_risk="event_triggered",
    next_review="GN 487A amendment or repeal",
))

pairs.append(p(
    "tier1a_permit_011_20260603", "work_permits",
    "Mwombaji wa kibali cha kazi (Class C) Tanzania anahitaji hati gani?",
    "Kwa kawaida, mwombaji wa Class C anahitaji: passport inayotumika, barua ya mwajiri, mkataba wa kazi, vyeti vya elimu/uzoefu, picha za pasipoti, fomu ya TRA (TIN), na ada ya maombi. Mahitaji yanaweza kutofautiana — thibitisha orodha kamili na Idara ya Uhamiaji.",
    "What documents does a Class C work permit applicant in Tanzania need?",
    "Typically, a Class C applicant needs: a valid passport, employer letter, employment contract, educational/experience certificates, passport photos, TRA form (TIN), and application fee. Requirements may vary — confirm the full list with the Immigration Department.",
    IMMIG_URL, IMMIG_NAME,
    effective_date="2025-07-28",
    decay_risk="annual",
    next_review="Immigration regulation change",
))

pairs.append(p(
    "tier1a_permit_012_20260603", "work_permits",
    "Kibali cha kazi Tanzania kinadumu kwa muda gani?",
    "Kibali cha makazi daraja C kawaida kinatolewa kwa kipindi cha hadi miaka 2, kinachoweza kuhuishwa. Kibali cha daraja B (mwekezaji) kinaweza kutolewa kwa hadi miaka 5. Thibitisha muda halisi wa aina yako ya kibali na Idara ya Uhamiaji.",
    "How long is a work permit valid in Tanzania?",
    "A Class C residence permit is typically issued for up to 2 years, renewable. A Class B (investor) permit may be issued for up to 5 years. Confirm the exact duration for your permit type with the Immigration Department.",
    IMMIG_URL, IMMIG_NAME,
    effective_date="2025-07-28",
    decay_risk="annual",
    next_review="Immigration regulation change",
))

pairs.append(p(
    "tier1a_permit_013_20260603", "work_permits",
    "Mgeni anaweza kuanza kufanya kazi Tanzania kabla ya kupata kibali?",
    "Hapana. Mgeni lazima apate kibali cha makazi (Class C) kabla ya kuanza kufanya kazi. Kufanya kazi kabla ya kibali ni ukiukwaji wa sheria ya uhamiaji na unaweza kusababisha kufukuzwa nchini. Mwajiri pia anachukuliwa na jukumu. Thibitisha na Idara ya Uhamiaji.",
    "Can a non-citizen start working in Tanzania before receiving their permit?",
    "No. A non-citizen must obtain a Class C residence permit before starting work. Working before a permit is an immigration law violation and can result in deportation. The employer also bears liability. Confirm with the Immigration Department.",
    IMMIG_URL, IMMIG_NAME,
    effective_date="2025-07-28",
    decay_risk="stable",
    next_review="Immigration regulation change",
    pair_type="adversarial",
))

pairs.append(p(
    "tier1a_permit_014_20260603", "work_permits",
    "Ada ya kibali cha makazi Class C Tanzania ni kiasi gani?",
    "Ada ya kibali cha makazi daraja C inaweza kutofautiana kulingana na muda na aina ya kazi. Karibu na USD 500–2,000 kwa mwaka — lakini thibitisha ada halisi za sasa na Idara ya Uhamiaji kupitia tovuti immigration.go.tz, kwani ada zinaweza kubadilika.",
    "What is the fee for a Class C residence permit in Tanzania?",
    "The Class C residence permit fee varies depending on duration and type of employment. Approximately USD 500–2,000 per year — but confirm the current exact fees with the Immigration Department at immigration.go.tz, as fees may change.",
    IMMIG_URL, IMMIG_NAME,
    effective_date="2025-07-28",
    decay_risk="annual",
    next_review="Immigration fee revision",
))

pairs.append(p(
    "tier1a_permit_015_20260603", "work_permits",
    "Mwajiri anahitaji TIN kabla ya kumwomba mfanyakazi mgeni kibali cha kazi?",
    "Ndiyo. Kampuni lazima iwe na TIN iliyotolewa na TRA na iwe imesajiliwa kisheria Tanzania kabla ya kuomba kibali cha kazi kwa mfanyakazi mgeni. Idara ya Uhamiaji inataka uthibitisho wa usajili wa kampuni na hali ya kodi. Thibitisha na TRA na Idara ya Uhamiaji.",
    "Does an employer need a TIN before sponsoring a foreign work permit in Tanzania?",
    "Yes. The company must have a TRA-issued TIN and be legally registered in Tanzania before applying for a work permit for a foreign employee. The Immigration Department requires proof of company registration and tax compliance. Confirm with TRA and the Immigration Department.",
    IMMIG_URL, IMMIG_NAME,
    effective_date="2025-07-28",
    decay_risk="stable",
    next_review="Immigration regulation change",
))

# ─────────────────────────────────────────────────────────────────────────────
# Withholding Tax — 15 pairs
# Source: scraped withholding.html (tra.go.tz/page/withholding-tax)
# ─────────────────────────────────────────────────────────────────────────────

pairs.append(p(
    "tier1a_wh_001_20260603", "withholding_tax",
    "Tarehe ya mwisho ya kulipa kodi ya zuio (withholding tax) TRA ni ipi?",
    "Kodi ya zuio lazima ilipwe TRA ndani ya siku 7 baada ya mwisho wa kila mwezi wa kalenda. Kwa mfano, kodi ya zuio iliyokatwa Januari inalipwa ifikapo tarehe 7 Februari. Thibitisha na TRA.",
    "What is the withholding tax remittance deadline in Tanzania?",
    "Withholding tax must be remitted to TRA within 7 days after the end of each calendar month. For example, withholding tax deducted in January is due by 7 February. Confirm with TRA.",
    TRA_WH_URL, TRA_WH_NAME,
))

pairs.append(p(
    "tier1a_wh_002_20260603", "withholding_tax",
    "Kiwango cha kodi ya zuio ya VAT kwa bidhaa ni asilimia ngapi Tanzania?",
    "Kiwango cha kodi ya zuio ya VAT kwa usambazaji wa bidhaa na wakala wa zuio (qualifying buyer) ni asilimia 3, kulingana na Kifungu cha 5(5) cha Sheria ya VAT. Hii ilianza kutumika tarehe 1 Julai 2025 (Finance Act 2025). Thibitisha na TRA.",
    "What is the VAT withholding rate on goods in Tanzania?",
    "The VAT withholding obligation on supply of goods by the Withholding Agent under Section 5(5) of the VAT Act is 3%, effective 1 July 2025 (Finance Act 2025). Confirm with TRA.",
    TRA_WH_URL, TRA_WH_NAME,
))

pairs.append(p(
    "tier1a_wh_003_20260603", "withholding_tax",
    "Kiwango cha kodi ya zuio ya VAT kwa huduma ni asilimia ngapi Tanzania?",
    "Kiwango cha kodi ya zuio ya VAT kwa usambazaji wa huduma na wakala wa zuio (qualifying buyer) ni asilimia 6, kulingana na Kifungu cha 5(5) cha Sheria ya VAT. Hii ilianza kutumika tarehe 1 Julai 2025 (Finance Act 2025). Thibitisha na TRA.",
    "What is the VAT withholding rate on services in Tanzania?",
    "The VAT withholding obligation on supply of services by the Withholding Agent under Section 5(5) of the VAT Act is 6%, effective 1 July 2025 (Finance Act 2025). Confirm with TRA.",
    TRA_WH_URL, TRA_WH_NAME,
))

pairs.append(p(
    "tier1a_wh_004_20260603", "withholding_tax",
    "Kiwango cha kodi ya zuio ya gawio (dividends) kwa kampuni zilizoorodheshwa DSE ni asilimia ngapi?",
    "Kiwango cha kodi ya zuio ya gawio kwa kampuni zilizoorodheshwa kwenye Soko la Hisa la Dar es Salaam (DSE) ni asilimia 5 — kwa wakazi na wasio wakazi. Thibitisha na TRA.",
    "What is the withholding tax rate on dividends from DSE-listed companies?",
    "The withholding tax rate on dividends from Dar es Salaam Stock Exchange (DSE) listed companies is 5% — for both residents and non-residents. Confirm with TRA.",
    TRA_WH_URL, TRA_WH_NAME,
))

pairs.append(p(
    "tier1a_wh_005_20260603", "withholding_tax",
    "Kiwango cha kodi ya zuio ya gawio kwa kampuni zingine (zisizoorodheshwa DSE) ni asilimia ngapi?",
    "Kiwango cha kodi ya zuio ya gawio kwa kampuni zisizoorodheshwa DSE ni asilimia 10 kwa wakazi na asilimia 10 kwa wasio wakazi. Kama kampuni inayopokea gawio inamiliki zaidi ya asilimia 25 ya hisa — kiwango ni asilimia 5. Thibitisha na TRA.",
    "What is the withholding tax rate on dividends from non-DSE-listed companies?",
    "The withholding tax rate on dividends from non-DSE-listed companies is 10% for residents and 10% for non-residents. If the recipient company holds 25%+ of shares — the rate is 5%. Confirm with TRA.",
    TRA_WH_URL, TRA_WH_NAME,
))

pairs.append(p(
    "tier1a_wh_006_20260603", "withholding_tax",
    "Kiwango cha kodi ya zuio ya riba (interest) Tanzania ni asilimia ngapi?",
    "Kiwango cha kodi ya zuio ya riba ni asilimia 10 kwa wakazi na asilimia 10 kwa wasio wakazi. Thibitisha na TRA.",
    "What is the withholding tax rate on interest in Tanzania?",
    "The withholding tax rate on interest is 10% for residents and 10% for non-residents. Confirm with TRA.",
    TRA_WH_URL, TRA_WH_NAME,
))

pairs.append(p(
    "tier1a_wh_007_20260603", "withholding_tax",
    "Kiwango cha kodi ya zuio ya mrabaha (royalties) Tanzania ni asilimia ngapi?",
    "Kiwango cha kodi ya zuio ya mrabaha ni asilimia 15 kwa wakazi na asilimia 10 kwa wasio wakazi. Thibitisha na TRA.",
    "What is the withholding tax rate on royalties in Tanzania?",
    "The withholding tax rate on royalties is 15% for residents and 10% for non-residents. Confirm with TRA.",
    TRA_WH_URL, TRA_WH_NAME,
))

pairs.append(p(
    "tier1a_wh_008_20260603", "withholding_tax",
    "Kiwango cha kodi ya zuio ya ada za huduma (service fees) Tanzania ni asilimia ngapi?",
    "Kiwango cha kodi ya zuio ya ada za huduma (service fees) ni asilimia 5 kwa wakazi na asilimia 15 kwa wasio wakazi. Thibitisha na TRA.",
    "What is the withholding tax rate on service fees in Tanzania?",
    "The withholding tax rate on service fees is 5% for residents and 15% for non-residents. Confirm with TRA.",
    TRA_WH_URL, TRA_WH_NAME,
))

pairs.append(p(
    "tier1a_wh_009_20260603", "withholding_tax",
    "Kiwango cha kodi ya zuio ya pango la kibiashara (commercial rent) Tanzania ni asilimia ngapi?",
    "Kiwango cha kodi ya zuio ya pango la kibiashara ni asilimia 10 kwa wakazi na asilimia 15 kwa wasio wakazi. Thibitisha na TRA.",
    "What is the withholding tax rate on commercial rent in Tanzania?",
    "The withholding tax rate on commercial rent is 10% for residents and 15% for non-residents. Confirm with TRA.",
    TRA_WH_URL, TRA_WH_NAME,
))

pairs.append(p(
    "tier1a_wh_010_20260603", "withholding_tax",
    "Ada ya mkurugenzi asiye wa wakati kamili inalipwa kodi ya zuio ya asilimia ngapi Tanzania?",
    "Ada ya mkurugenzi asiye wa wakati kamili (non full-time director) inalipwa kodi ya zuio ya asilimia 15 kwa wakazi na asilimia 15 kwa wasio wakazi. Thibitisha na TRA.",
    "What withholding tax rate applies to non-full-time director fees in Tanzania?",
    "Non-full-time director fees are subject to 15% withholding tax for residents and 15% for non-residents. Confirm with TRA.",
    TRA_WH_URL, TRA_WH_NAME,
))

pairs.append(p(
    "tier1a_wh_011_20260603", "withholding_tax",
    "Kodi ya zuio ya mwisho (final withholding tax) na isiyo ya mwisho (non-final) ni tofauti gani?",
    "Kodi ya zuio ya mwisho: mpokeaji haawezi kudai mkopo wa kodi — kodi hiyo ndiyo ya mwisho kabisa kwa mapato hayo. Kodi ya zuio isiyo ya mwisho: mpokeaji anaweza kudai mkopo dhidi ya kodi yake ya mwaka. Thibitisha hali ya malipo yako na TRA.",
    "What is the difference between final and non-final withholding tax in Tanzania?",
    "Final withholding tax: the recipient cannot claim a tax credit — it is the final tax on that income. Non-final withholding tax: the recipient can claim a credit against their annual tax liability. Confirm your payment classification with TRA.",
    TRA_WH_URL, TRA_WH_NAME,
    decay_risk="stable",
    next_review="Legislative change",
))

pairs.append(p(
    "tier1a_wh_012_20260603", "withholding_tax",
    "Wakala wa zuio (withholding agent) ni nani Tanzania?",
    "Wakala wa zuio ni mtu anayehitajika kisheria kukata kodi ya zuio kutoka kwa malipo anayofanya. Wakala wa zuio ni: serikali na taasisi zake, makampuni, na watu binafsi waliotajwa na sheria. Wakala anapaswa kusajiliwa TRA na kulipa ndani ya siku 7. Thibitisha na TRA.",
    "Who is a withholding agent in Tanzania?",
    "A withholding agent is a person legally required to deduct withholding tax from payments they make. Withholding agents include: government and its institutions, companies, and specified individuals. The agent must be registered with TRA and pay within 7 days. Confirm with TRA.",
    TRA_WH_URL, TRA_WH_NAME,
    decay_risk="stable",
    next_review="Legislative change",
))

pairs.append(p(
    "tier1a_wh_013_20260603", "withholding_tax",
    "Kodi ya zuio ya malipo ya bidhaa kwa serikali Tanzania ni asilimia ngapi?",
    "Malipo ya bidhaa zinazotolewa kwa serikali na taasisi zake yanastahili kodi ya zuio ya asilimia 2 ya malipo ghafi. Hii inashughulikia wazabuni wote wanaouza bidhaa kwa serikali. Thibitisha na TRA.",
    "What withholding tax applies to payments for goods supplied to the government in Tanzania?",
    "Payments for goods supplied to the government and its institutions are subject to 2% withholding tax on gross payment. This applies to all suppliers selling goods to government entities. Confirm with TRA.",
    TRA_WH_URL, TRA_WH_NAME,
))

pairs.append(p(
    "tier1a_wh_014_20260603", "withholding_tax",
    "Adhabu ya kutolipa kodi ya zuio kwa wakati Tanzania ni nini?",
    "Wakala wa zuio ambaye hakulipa kwa wakati anakabili: faini ya asilimia 5 ya kiwango kilichochelewa kwa kila mwezi au sehemu yake, pamoja na riba. TRA pia inaweza kudai malipo moja kwa moja kutoka kwa wakala. Thibitisha na TRA.",
    "What is the penalty for late withholding tax remittance in Tanzania?",
    "A withholding agent who pays late faces: a 5% penalty on the overdue amount per month or part thereof, plus interest. TRA can also claim the payment directly from the agent. Confirm with TRA.",
    TRA_WH_URL, TRA_WH_NAME,
))

pairs.append(p(
    "tier1a_wh_015_20260603", "withholding_tax",
    "Jinsi ya kupata cheti cha kodi ya zuio (withholding tax certificate) Tanzania?",
    "Cheti cha kodi ya zuio kinapatikana kupitia mfumo wa malipo ya kodi (Tax Payment) kwenye Lango la Walipa Kodi (Taxpayer Portal) wa TRA. Kinachapishwa na wakala wa zuio au mtu aliyekatwa kodi (withholdee) baada ya malipo kukamilika. Thibitisha na TRA.",
    "How do you obtain a withholding tax certificate in Tanzania?",
    "A withholding tax certificate is obtained through the Tax Payment section of TRA's Taxpayer Portal. It can be printed by either the withholding agent or the withholdee after payment is completed. Confirm with TRA.",
    TRA_WH_URL, TRA_WH_NAME,
))

# ─────────────────────────────────────────────────────────────────────────────
# VAT Edge Cases — 15 pairs
# Source: scraped vat_edge.html (tra.go.tz/page/value-added-tax-vat)
# ─────────────────────────────────────────────────────────────────────────────

pairs.append(p(
    "tier1a_vat_edge_001_20260603", "vat_edge_cases",
    "Mauzo ya nje ya nchi (exports) yanastahili VAT ya asilimia ngapi Tanzania?",
    "Mauzo ya nje ya nchi (exports) ya bidhaa na huduma yanastahili VAT ya asilimia sifuri (zero-rated) ikiwa na uthibitisho wa kufilisi bidhaa nje ya Tanzania Bara. VAT ya sifuri inaruhusu msajiliwa kudai mkopo wa pembejeo (input tax credit). Thibitisha na TRA.",
    "What VAT rate applies to exports of goods and services from Tanzania?",
    "Exports of goods and services are zero-rated (0% VAT) provided there is proof of consumption/supply outside Tanzania Mainland. Zero-rating allows the registered person to claim input tax credit. Confirm with TRA.",
    TRA_VAT_URL, TRA_VAT_NAME,
))

pairs.append(p(
    "tier1a_vat_edge_002_20260603", "vat_edge_cases",
    "Biashara inayoanza — inaweza kusajili VAT kabla ya kufikia kizingiti cha TZS 200M?",
    "Ndiyo. Mtu anayekusudia kufanya biashara (intending trader) anaweza kuomba usajili wa hiari wa VAT wakati wowote, mradi atoe uthibitisho wa kutosha kama vile mikataba, zabuni, mipango ya ujenzi, au ufadhili wa benki. Thibitisha na TRA.",
    "Can a start-up register for VAT before reaching the TZS 200M threshold?",
    "Yes. An intending trader can apply for voluntary VAT registration at any time, provided they submit sufficient evidence such as contracts, tenders, building plans, or bank financing. Confirm with TRA.",
    TRA_VAT_URL, TRA_VAT_NAME,
))

pairs.append(p(
    "tier1a_vat_edge_003_20260603", "vat_edge_cases",
    "Je, VAT inastahili kwa bidhaa na huduma zote Tanzania?",
    "Hapana. VAT inastahili kwa usambazaji unaostahili (taxable supply) peke yake unaofanywa na mtu msajiliwa katika mwendo wa shughuli za kiuchumi. Usambazaji fulani una kiwango cha sifuri (zero-rated) au umeachiliwa (exempt). Thibitisha hali ya bidhaa/huduma yako na TRA.",
    "Does VAT apply to all goods and services in Tanzania?",
    "No. VAT applies only to taxable supplies made by a registered person in the course of economic activities. Some supplies are zero-rated or exempt. Confirm the status of your goods/services with TRA.",
    TRA_VAT_URL, TRA_VAT_NAME,
    decay_risk="stable",
    next_review="Legislative change",
))

pairs.append(p(
    "tier1a_vat_edge_004_20260603", "vat_edge_cases",
    "VAT ya uingizaji (imports) inafanyaje kazi Tanzania?",
    "VAT ya asilimia 18 inastahili kwa uingizaji wa bidhaa zinazostahili kutoka nje ya Tanzania Bara. Uingizaji wa huduma pia unastahili VAT. Sheria za kawaida za Forodha zinatumika. Thibitisha mahitaji ya VAT ya uingizaji na TRA na Forodha.",
    "How does VAT on imports work in Tanzania?",
    "18% VAT applies to the importation of taxable goods from outside Tanzania Mainland. Importation of services is also subject to VAT. Normal Customs laws and procedures apply. Confirm import VAT requirements with TRA and Customs.",
    TRA_VAT_URL, TRA_VAT_NAME,
))

pairs.append(p(
    "tier1a_vat_edge_005_20260603", "vat_edge_cases",
    "Msajiliwa wa VAT ambaye hajafikia kizingiti anapaswa kujisajili wenyewe — je, TRA anaweza kumsajili bila ombi?",
    "Ndiyo. Ikiwa Kamishna Mkuu ameridhika kwamba mtu anahitajika kusajiliwa VAT na ana sababu nzuri — ikiwemo kulinda mapato ya serikali — anaweza kumsajili bila ombi na kumwarifu ndani ya siku 14 baada ya usajili. Thibitisha na TRA.",
    "Can TRA register a business for VAT without an application?",
    "Yes. If the Commissioner General is satisfied that a person must register for VAT and there is good reason — including protection of government revenue — they can register that person without an application and notify them within 14 days of registration. Confirm with TRA.",
    TRA_VAT_URL, TRA_VAT_NAME,
    pair_type="adversarial",
))

pairs.append(p(
    "tier1a_vat_edge_006_20260603", "vat_edge_cases",
    "Nambari ya usajili wa VAT inatumika kwa madhumuni gani Tanzania?",
    "Nambari ya usajili wa VAT (VAT registration number) inatumika: kwenye hati za VAT (invoices, returns), pamoja na TIN kwenye nyaraka za rasmi za VAT, na lazima ionekane kwenye Cheti cha Usajili cha VAT mahali panapoonekana kazini. Thibitisha na TRA.",
    "What is the VAT registration number used for in Tanzania?",
    "The VAT registration number is used: on VAT documents (invoices, returns), alongside the TIN on official VAT documents, and must be displayed on the VAT Registration Certificate in a visible place at the principal business premises. Confirm with TRA.",
    TRA_VAT_URL, TRA_VAT_NAME,
    decay_risk="stable",
    next_review="Legislative change",
))

pairs.append(p(
    "tier1a_vat_edge_007_20260603", "vat_edge_cases",
    "Mtu lazima asajili VAT ndani ya muda gani baada ya kufikia kizingiti?",
    "Mtu anayehitajika kusajiliwa VAT lazima afanye maombi kwa Kamishna Mkuu ndani ya siku 30 baada ya kufikia kizingiti. Kukosa kusajili kwa wakati kunaweza kusababisha usajili wa lazima na faini. Thibitisha na TRA.",
    "Within what time must a business register for VAT after reaching the threshold?",
    "A person required to register for VAT must apply to the Commissioner General within 30 days of reaching the threshold. Failing to register on time may result in compulsory registration and penalties. Confirm with TRA.",
    TRA_VAT_URL, TRA_VAT_NAME,
))

pairs.append(p(
    "tier1a_vat_edge_008_20260603", "vat_edge_cases",
    "Watoa huduma wa kitaalamu (professional service providers) wanastahili VAT Tanzania?",
    "Ndiyo, watoa huduma wa kitaalamu wanastahili usajili wa VAT kama wanafikia kizingiti cha TZS 200M/mwaka au TZS 100M/miezi 6. Wanaweza pia kusajili kwa hiari kabla ya kufikia kizingiti. Thibitisha hali ya huduma zako maalum na TRA.",
    "Do professional service providers qualify for VAT registration in Tanzania?",
    "Yes, professional service providers qualify for VAT registration if they reach the TZS 200M/year or TZS 100M/6-month threshold. They can also voluntarily register before reaching the threshold. Confirm the status of your specific services with TRA.",
    TRA_VAT_URL, TRA_VAT_NAME,
))

pairs.append(p(
    "tier1a_vat_edge_009_20260603", "vat_edge_cases",
    "Usambazaji wa bidhaa nje ya Tanzania Bara unastahili VAT ya Tanzania?",
    "Bidhaa zinazosambazwa au huduma zinazofurahiwa nje ya Tanzania Bara zinastahili kiwango cha sifuri (zero-rated) kwa kutoa uthibitisho. Hii inatofautiana na msamaha (exempt) — msajiliwa wa VAT anaweza kudai input tax credit kwa usambazaji wa zero-rated. Thibitisha na TRA.",
    "Is a supply consumed outside Tanzania Mainland subject to Tanzania VAT?",
    "Supplies consumed or enjoyed outside Tanzania Mainland are zero-rated upon proof. This differs from exempt — a VAT-registered person can claim input tax credit on zero-rated supplies. Confirm with TRA.",
    TRA_VAT_URL, TRA_VAT_NAME,
))

pairs.append(p(
    "tier1a_vat_edge_010_20260603", "vat_edge_cases",
    "VAT inalipwa kwa muda gani na msajiliwa Tanzania?",
    "Msajiliwa wa VAT analipa VAT kupitia return ya VAT ya kila mwezi. Return na malipo yanatolewa ifikapo tarehe 20 ya mwezi unaofuata mwezi wa biashara. Thibitisha tarehe na TRA.",
    "When does a VAT registrant file and pay VAT in Tanzania?",
    "A VAT registrant pays VAT through a monthly VAT return. The return and payment are due by the 20th of the month following the trading month. Confirm the deadline with TRA.",
    TRA_VAT_URL, TRA_VAT_NAME,
))

pairs.append(p(
    "tier1a_vat_edge_011_20260603", "vat_edge_cases",
    "Cheti cha kodi ya zuio ya VAT kinatoka lini?",
    "Cheti cha kodi ya zuio ya VAT kinatoka siku VAT inapokuwa stahili kulipwa (the day VAT becomes payable) — si tarehe 20 ya mwezi. Tarehe 20 ni ya kufungua return ya VAT, ambayo ni wajibu tofauti. Thibitisha na TRA.",
    "When must a VAT withholding certificate be issued?",
    "A VAT withholding certificate must be issued on the day VAT becomes payable — not on the 20th of the month. The 20th is the VAT return filing deadline, which is a separate obligation. Confirm with TRA.",
    TRA_VAT_URL, TRA_VAT_NAME,
    pair_type="adversarial",
))

pairs.append(p(
    "tier1a_vat_edge_012_20260603", "vat_edge_cases",
    "Kampuni mpya inayoanza (intending trader) inaweza kusajili VAT bila kuwa na mapato bado?",
    "Ndiyo. Mtu anayekusudia kufanya biashara (intending trader) anaweza kuomba usajili wa VAT 'wakati wowote' mradi atoe ushahidi wa kutosha kama vile mikataba, zabuni, mipango ya ujenzi, mipango ya biashara, au ufadhili wa benki. Thibitisha na TRA.",
    "Can a new start-up (intending trader) register for VAT with no revenue yet?",
    "Yes. An intending trader can apply for VAT registration 'at any time' provided they present sufficient evidence such as contracts, tenders, building plans, business plans, or bank financing. Confirm with TRA.",
    TRA_VAT_URL, TRA_VAT_NAME,
    pair_type="adversarial",
))

pairs.append(p(
    "tier1a_vat_edge_013_20260603", "vat_edge_cases",
    "Je, serikali na taasisi zake zinastahili VAT Tanzania?",
    "Serikali na taasisi zake zinaweza kuwa wasajiliwa wa VAT kama zinafanya shughuli za kiuchumi. Pia zinaweza kuwa wakala wa zuio ya VAT. Thibitisha hali halisi ya shughuli za taasisi husika na TRA.",
    "Are government entities and institutions subject to VAT in Tanzania?",
    "Government entities and institutions may be VAT registrants if they carry on economic activities. They may also serve as VAT withholding agents. Confirm the specific situation for the institution concerned with TRA.",
    TRA_VAT_URL, TRA_VAT_NAME,
    decay_risk="stable",
    next_review="Legislative change",
))

pairs.append(p(
    "tier1a_vat_edge_014_20260603", "vat_edge_cases",
    "Biashara ya B2C ya malipo ya kidijitali ina VAT ya asilimia ngapi kuanzia Septemba 2025?",
    "Shughuli za B2C za malipo ya kidijitali (e-payment) zinalipwa VAT ya asilimia 16 kuanzia tarehe 1 Septemba 2025. Kanuni za utekelezaji zingali zinasubiriwa kutoka kwa Kamishna Mkuu wa TRA. Thibitisha hali ya sasa na TRA.",
    "What VAT rate applies to B2C digital payment transactions from September 2025?",
    "B2C e-payment transactions are subject to 16% VAT from 1 September 2025. Implementation rules are pending a notice from the TRA Commissioner General. Confirm the current status with TRA.",
    TRA_VAT_URL, TRA_VAT_NAME,
    effective_date="2025-09-01",
    decay_risk="event_triggered",
    next_review="TRA Commissioner General implementation notice",
))

pairs.append(p(
    "tier1a_vat_edge_015_20260603", "vat_edge_cases",
    "Usajili wa VAT unafanywa kupitia mfumo gani wa TRA?",
    "Maombi ya usajili wa VAT yanafanywa kupitia Lango la Walipa Kodi (IDRAS — Taxpayer Portal) kwenye tovuti ya TRA baada ya mteja kuingia kwenye akaunti yake. Thibitisha mahitaji ya sasa na TRA.",
    "Which TRA system is used to apply for VAT registration?",
    "VAT registration applications are made through TRA's Taxpayer Portal (IDRAS) on the TRA website after the applicant logs into their account. Confirm current requirements with TRA.",
    TRA_VAT_URL, TRA_VAT_NAME,
    decay_risk="stable",
    next_review="TRA system change",
))

# ─────────────────────────────────────────────────────────────────────────────
# NSSF Edge Cases — 10 pairs
# Source: scraped nssf_edge.html (nssf.go.tz/pages/payment-of-contributions)
# ─────────────────────────────────────────────────────────────────────────────

pairs.append(p(
    "tier1a_nssf_edge_001_20260603", "nssf_edge_cases",
    "Mwajiri anaweza kulipa mchango wote wa NSSF 20% bila kukata sehemu ya mfanyakazi?",
    "Ndiyo. Mwajiri anaweza kuchagua kulipa mchango wote wa asilimia 20 bila kukata sehemu ya mfanyakazi (asilimia 10) kutoka mshahara wake. Hii ni chaguo la mwajiri — si lazima lakini inaruhusiwa na Sheria ya NSSF. Thibitisha na NSSF.",
    "Can an employer pay the full 20% NSSF contribution without deducting the employee's share?",
    "Yes. An employer may choose to remit the full 20% contribution without deducting the employee's share (10%) from their wage. This is the employer's option — not mandatory but permitted under the NSSF Act. Confirm with NSSF.",
    NSSF_URL, NSSF_NAME,
    decay_risk="stable",
    next_review="NSSF Act amendment",
    pair_type="adversarial",
))

pairs.append(p(
    "tier1a_nssf_edge_002_20260603", "nssf_edge_cases",
    "Mpango mbadala wa NSSF (15%/5%) unafanya kazi vipi?",
    "Badala ya mgawanyo wa kawaida wa 10%/10%, mwajiri anaweza kulipa asilimia 15 na mfanyakazi asilimia 5. Jumla bado ni asilimia 20 ya mshahara ghafi. Mpango huu unaruhusiwa chini ya Sheria ya NSSF Kifungu cha 12. Thibitisha na NSSF.",
    "How does the alternative NSSF arrangement (15%/5%) work?",
    "Instead of the standard 10%/10% split, the employer may pay 15% and the employee 5%. The total remains 20% of gross wage. This arrangement is permitted under the NSSF Act Section 12. Confirm with NSSF.",
    NSSF_URL, NSSF_NAME,
    decay_risk="stable",
    next_review="NSSF Act amendment",
))

pairs.append(p(
    "tier1a_nssf_edge_003_20260603", "nssf_edge_cases",
    "Faini ya kuchelewa kulipa NSSF Tanzania ni kiasi gani?",
    "Faini ya kuchelewa kulipa NSSF ni asilimia 5 ya kiwango kilichochelewa kwa kila mwezi au sehemu ya mwezi baada ya tarehe ya malipo. Faini inakusanywa kama deni kutoka kwa mwajiri. Thibitisha na NSSF.",
    "What is the penalty for late NSSF contribution payment in Tanzania?",
    "The late NSSF contribution penalty is 5% of the unpaid amount for each month or part of a month after the due date. The penalty is recovered as a debt from the employer. Confirm with NSSF.",
    NSSF_URL, NSSF_NAME,
    decay_risk="stable",
    next_review="NSSF Act amendment",
))

pairs.append(p(
    "tier1a_nssf_edge_004_20260603", "nssf_edge_cases",
    "NSSF inalipwa kwa njia gani Tanzania?",
    "NSSF inalipwa kupitia mfumo wa GePG (Government e-Payment Gateway). Mwajiri analazimika pia kutoa nyaraka za usaidizi (fomu NSSF/CON.05) kwenye ofisi ya NSSF mara tu baada ya malipo — kwa utoaji wa kimwili au njia ya kielektroniki. Thibitisha na NSSF.",
    "How is NSSF paid in Tanzania?",
    "NSSF is paid through the GePG (Government e-Payment Gateway) system. The employer must also submit supporting documents (NSSF/CON.05 form) to the NSSF office immediately after payment — by physical delivery or electronic means. Confirm with NSSF.",
    NSSF_URL, NSSF_NAME,
    decay_risk="annual",
    next_review="NSSF payment system change",
))

pairs.append(p(
    "tier1a_nssf_edge_005_20260603", "nssf_edge_cases",
    "Mwajiri mwenye matawi mengi atalipa NSSF ofisi ipi?",
    "Michango ya waajiri wenye ofisi zaidi ya mkoa mmoja inalipwa kwenye Ofisi ya NSSF ambayo mchango ulipelekwa. Ofisi za kikanda zinahitajika kushirikiana ili kuhakikisha uzingatiaji wa mwajiri mwenye matawi tofauti. Thibitisha na NSSF.",
    "Which NSSF office does a multi-branch employer pay contributions to?",
    "Contributions for employers with offices in more than one region are accounted for at the NSSF office where the contribution was remitted. Regional offices must cooperate to ensure compliance of employers with different branches. Confirm with NSSF.",
    NSSF_URL, NSSF_NAME,
    decay_risk="stable",
    next_review="NSSF administrative change",
))

pairs.append(p(
    "tier1a_nssf_edge_006_20260603", "nssf_edge_cases",
    "NSSF inacheswa kwa mshahara ghafi (gross wage) au mshahara wa msingi (basic salary)?",
    "NSSF inacheswa kwa mshahara ghafi (gross wage) — si mshahara wa msingi peke yake. Mshahara ghafi unajumuisha mishahara yote ya lazima kabla ya makato yoyote. Thibitisha ufafanuzi kamili wa 'mshahara wa jumla' na NSSF.",
    "Is NSSF calculated on gross wage or basic salary in Tanzania?",
    "NSSF is calculated on gross wage — not basic salary alone. Gross wage includes all compulsory remuneration before any deductions. Confirm the full definition of 'total wage' with NSSF.",
    NSSF_URL, NSSF_NAME,
    decay_risk="stable",
    next_review="NSSF Act amendment",
    pair_type="adversarial",
))

pairs.append(p(
    "tier1a_nssf_edge_007_20260603", "nssf_edge_cases",
    "Mfanyakazi anayefanya kazi kwa waajiri wawili analipa NSSF mara mbili?",
    "Inategemea: kila mwajiri anapaswa kulipa NSSF kwa mfanyakazi wake. Kama mfanyakazi ana waajiri wawili, NSSF inalipwa na kila mwajiri kwa kipande cha mshahara kinachohusika. Thibitisha mpangilio sahihi na NSSF.",
    "Does an employee working for two employers pay NSSF twice?",
    "It depends: each employer must pay NSSF for their employee. If an employee has two employers, each pays NSSF on their respective portion of wages. Confirm the correct arrangement with NSSF.",
    NSSF_URL, NSSF_NAME,
    decay_risk="stable",
    next_review="NSSF Act amendment",
))

pairs.append(p(
    "tier1a_nssf_edge_008_20260603", "nssf_edge_cases",
    "Mwajiri anaweza kuacha kulipa NSSF kwa sababu biashara inazorota?",
    "Hapana. NSSF ni mchango wa lazima chini ya sheria — mwajiri hawezi kuacha kulipa hata kama biashara inazorota au inakabili matatizo ya fedha. Kushindwa kulipa kunasababisha faini ya asilimia 5 kwa mwezi na madai ya kisheria. Thibitisha na NSSF.",
    "Can an employer stop paying NSSF because the business is struggling financially?",
    "No. NSSF is a mandatory statutory contribution — an employer cannot stop paying even if the business is struggling financially. Failure to pay attracts a 5% monthly penalty and legal claims. Confirm with NSSF.",
    NSSF_URL, NSSF_NAME,
    decay_risk="stable",
    next_review="NSSF Act amendment",
    pair_type="adversarial",
))

pairs.append(p(
    "tier1a_nssf_edge_009_20260603", "nssf_edge_cases",
    "NSSF inalipwa ndani ya muda gani baada ya mwisho wa mwezi?",
    "Kwa mujibu wa Sheria ya NSSF Kifungu cha 12, mchango wa NSSF unapaswa kulipwa ndani ya mwezi mmoja (within one month) baada ya mwisho wa mwezi husika. Thibitisha tarehe halisi na NSSF kwani sheria inaweza kusomwa tofauti na mazoea ya vitendo.",
    "Within what period must NSSF contributions be paid after the end of the month?",
    "Under the NSSF Act Section 12, contributions must be paid within one month after the end of the relevant month. Confirm the exact deadline with NSSF as the law may be interpreted differently from practical arrangements.",
    NSSF_URL, NSSF_NAME,
    decay_risk="stable",
    next_review="NSSF Act amendment",
    pair_type="adversarial",
))

pairs.append(p(
    "tier1a_nssf_edge_010_20260603", "nssf_edge_cases",
    "Mwajiri mpya — lini anapaswa kusajili NSSF?",
    "Mwajiri mpya anapaswa kusajili NSSF mara tu anapoanza kuajiri wafanyakazi. Usajili unafanywa kupitia Lango la Huduma la NSSF (NSSF Self Service Portal) au ofisi yoyote ya NSSF. Thibitisha tarehe na mahitaji ya usajili na NSSF.",
    "When must a new employer register with NSSF?",
    "A new employer must register with NSSF as soon as they start employing workers. Registration is done through the NSSF Self Service Portal or any NSSF office. Confirm the registration timeline and requirements with NSSF.",
    NSSF_URL, NSSF_NAME,
    decay_risk="stable",
    next_review="NSSF registration process change",
))

# ─────────────────────────────────────────────────────────────────────────────
# Dedup check
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

with open(OUT_FILE, "w", encoding="utf-8") as f:
    for pair in filtered:
        f.write(json.dumps(pair, ensure_ascii=False) + "\n")

print(f"Saved {len(filtered)} pairs to {OUT_FILE}")
