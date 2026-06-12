"""Apply all corrections from do.md to raw_pairs_batch_008.jsonl."""
import json, sys, copy

FILEPATH = "datasets/tier1a/raw_sources/raw_pairs_batch_008.jsonl"

pairs = []
with open(FILEPATH, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            pairs.append(json.loads(line))

changes = {}


def fix(pair_id, field, old, new):
    for p in pairs:
        if p["id"] == pair_id:
            if old not in p[field]:
                print(f"  WARNING: '{old[:60]}' NOT FOUND in {pair_id}.{field}")
            else:
                p[field] = p[field].replace(old, new, 1)
                changes.setdefault(pair_id, []).append(field)
            return
    print(f"  ERROR: pair {pair_id} not found")


# ─── SECTION A — GN 487A PENALTY CORRECTIONS ─────────────────────────────────

# A1 — PEN_013
fix("b008_gn487a_pen_013_20260612", "answer_en",
    "Also, not being imprisoned and not having the visa revoked raises "
    "separate issues — all three penalties should have been imposed.",
    "No — a fine of TZS 8,000,000 is BELOW the mandatory minimum of "
    "TZS 10,000,000. The fine alone is a legal error — the court must "
    "impose at least TZS 10M. On imprisonment: the gazette says 'fine "
    "OR imprisonment' — the court chooses one, so not being imprisoned "
    "is not automatically wrong if the fine was imposed. However, NOT "
    "revoking the visa IS a separate error — visa revocation is mandatory "
    "(AND) and must accompany whichever penalty the court imposes. "
    "The defendant can appeal both the below-minimum fine and the "
    "missing visa revocation.")

fix("b008_gn487a_pen_013_20260612", "answer_sw",
    "Pia, kutofungwa na kutofutwa kwa visa ni tatizo tofauti — adhabu "
    "kamili zinapaswa kutolewa zote tatu.",
    "Kuhusu kutofungwa: gazeti inasema 'faini AU kifungo' — korti "
    "inachagua moja, kwa hivyo kutofungwa si kosa la kisheria kama "
    "faini ilitolewa badala yake. Lakini kutofutwa kwa visa NI kosa — "
    "visa lazima ifutwe (NA) na iende pamoja na faini au kifungo "
    "iwe yoyote iliyotolewa. Mshtakiwa anaweza kupinga faini ndogo "
    "na kukosekana kwa kufutwa kwa visa mahakamani.")

# A2 — PEN_028
fix("b008_gn487a_pen_028_20260612", "answer_en",
    "Connective word: AND — not OR. All three go together.",
    "How the penalties connect: fine OR imprisonment (court chooses "
    "one) AND visa revocation (always mandatory). The fine has a "
    "mandatory minimum of TZS 10M. Imprisonment is a maximum of "
    "6 months — the court may or may not impose it. Visa revocation "
    "is connected by AND — it accompanies whichever penalty the court "
    "imposes and is non-negotiable.")

fix("b008_gn487a_pen_028_20260612", "answer_sw",
    "Neno la kiungo: NA — si AU. Zote tatu zinakwenda pamoja.",
    "Jinsi adhabu zinavyounganika: faini AU kifungo (korti inachagua "
    "moja) NA visa kufutwa (lazima daima). Faini ina kiwango cha chini "
    "cha TZS 10M. Kifungo ni kiwango cha juu cha miezi 6 — korti "
    "inaweza au isitoe. Visa inafutwa kwa NA — inaambatana na adhabu "
    "yoyote korti itakayotoa na haiwezi kuepukwa.")

# A3 — PEN_030
fix("b008_gn487a_pen_030_20260612", "answer_en",
    "For non-citizen it is AND (all three). For facilitator it is "
    "OR (one of two).",
    "For non-citizen: fine OR imprisonment (court chooses one) AND "
    "visa revocation always mandatory. For facilitator: fine OR "
    "imprisonment only (court chooses one), no visa revocation. "
    "Key distinction: for the non-citizen the visa revocation is "
    "always AND — it cannot be avoided. The choice is only between "
    "fine and imprisonment, not whether to revoke the visa.")

fix("b008_gn487a_pen_030_20260612", "answer_sw",
    "Kwa mgeni ni NA (zote tatu). Kwa msaidizi ni AU (moja ya mbili).",
    "Kwa mgeni: faini AU kifungo (korti inachagua) NA visa kufutwa "
    "DAIMA lazima. Kwa msaidizi: faini AU kifungo tu (korti inachagua), "
    "bila visa kufutwa. Tofauti kuu: kwa mgeni visa kufutwa ni NA — "
    "haiwezi kuepukwa. Chaguo ni kati ya faini na kifungo tu, "
    "si kama visa itafutwa au la.")

# A4 — PEN_019
fix("b008_gn487a_pen_019_20260612", "answer_en",
    "a non-citizen may also (1) forfeit goods acquired through the "
    "illegal business; (2) lose business licences; (3) be deported "
    "after serving a prison sentence. GN 487A is the basis — other "
    "laws may also apply.",
    "TZS 10M is the MINIMUM fine — a court may impose more. The GN "
    "487A penalty clause specifies exactly: fine of at least TZS 10M "
    "OR imprisonment up to 6 months AND visa revocation. Consequences "
    "such as goods forfeiture, business licence cancellation, or "
    "deportation are NOT expressly stated in GN 487A — they may arise "
    "under other Tanzanian laws (Business Licensing Act, Immigration "
    "Act) but should not be presented as GN 487A penalties. Consult "
    "a lawyer for the full picture in your specific situation.")

fix("b008_gn487a_pen_019_20260612", "answer_sw",
    "mgeni anaweza pia (1) kupoteza bidhaa zake kama mali iliyopatikana "
    "kupitia biashara haramu; (2) kufutwa kwa leseni za biashara; "
    "(3) kutenganishwa (deportation) baada ya kushughulikia adhabu ya "
    "jela. GN 487A ni msingi — sheria nyingine zinaweza pia kutumika.",
    "TZS 10M ni faini ya CHINI KABISA — korti inaweza kutoza zaidi. "
    "Kifungu cha adhabu cha GN 487A kinabainisha hasa: faini ya angalau "
    "TZS 10M AU kifungo hadi miezi 6 NA visa kufutwa. Matokeo kama "
    "kunyang'anywa kwa bidhaa, kufutwa kwa leseni, au kufukuzwa "
    "HAYATAJWI wazi katika GN 487A yenyewe — yanaweza kutokea chini "
    "ya sheria nyingine za Tanzania lakini hayapaswi kuwasilishwa "
    "kama adhabu za GN 487A. Thibitisha na wakili kwa hali yako mahususi.")

# A5 — PEN_022
fix("b008_gn487a_pen_022_20260612", "answer_en",
    "Confidential reports are accepted. A reporter is not penalised "
    "for reporting in good faith.",
    "Anyone can report — a citizen, business competitor, or government "
    "official. The main enforcement departments are: Immigration "
    "Department, TRA, and the police. Contact the nearest Immigration "
    "Department office. Note: GN 487A itself does not specify reporting "
    "procedures, confidentiality provisions, or whistleblower "
    "protections — verify reporting procedures and any protections "
    "directly with the Immigration Department before reporting.")

fix("b008_gn487a_pen_022_20260612", "answer_sw",
    "Ripoti za siri (confidential reports) zinakubaliwa. Mripoti "
    "hakabiwi adhabu kwa kuripoti kwa nia njema.",
    "Kumbuka: GN 487A yenyewe haitaji utaratibu wa kuripoti, usiri, "
    "au ulinzi wa mripoti — thibitisha utaratibu wa kuripoti na ulinzi "
    "wowote moja kwa moja na Idara ya Uhamiaji kabla ya kuripoti.")

# A6 — PEN_027
fix("b008_gn487a_pen_027_20260612", "answer_en",
    "Typically, a person deported before completing the legal process "
    "escapes the penalty",
    "GN 487A does not address this scenario directly. Under general "
    "Tanzanian criminal procedure, a court order remains legally valid "
    "regardless of deportation. In practice, enforcement of a fine "
    "against a deported person is difficult and may require "
    "international legal cooperation. The conviction and visa revocation "
    "order remain on record. For specific advice consult a Tanzanian "
    "lawyer or the Immigration Department.")

fix("b008_gn487a_pen_027_20260612", "answer_sw",
    "kwa kawaida, mtu aliyefukuzwa kabla ya kumaliza mchakato wa "
    "kisheria anakimbia adhabu",
    "GN 487A haishughulikii hali hii moja kwa moja. Kwa kanuni za "
    "jumla za jinai Tanzania, uamuzi wa korti unabaki halali hata "
    "baada ya mtu kufukuzwa. Kwa vitendo, utekelezaji wa faini dhidi "
    "ya mtu aliyefukuzwa ni mgumu na unaweza kuhitaji ushirikiano "
    "wa kisheria wa kimataifa. Hukumu na amri ya visa kufutwa "
    "zinabaki kwenye rekodi. Kwa ushauri mahususi wasiliana na "
    "wakili wa Tanzania au Idara ya Uhamiaji.")


# ─── SECTION B — GN 487A SCOPE CORRECTIONS ───────────────────────────────────

# B1 — SCP_013
fix("b008_gn487a_scp_013_20260612", "answer_en",
    "Yes — tailoring and garment making is on the list of business "
    "categories prohibited for non-citizens under GN 487A",
    "Tailoring and garment making is not explicitly named as a "
    "separate category in the GN 487A Schedule. It may fall under "
    "Category 15 'Ownership and operation of micro and small "
    "industries' if operated as a small industrial activity. "
    "If you operate a tailoring business as a micro or small "
    "industry, it is likely covered. However, since it is not "
    "explicitly named, verify your specific situation with the "
    "Immigration Department or a lawyer before assuming it is "
    "or is not covered.")

fix("b008_gn487a_scp_013_20260612", "answer_sw",
    "Ndiyo — ushonaji wa nguo (tailoring and garment making) uko "
    "kwenye orodha ya biashara zilizopigwa marufuku kwa wageni "
    "chini ya GN 487A",
    "Ushonaji wa nguo (tailoring and garment making) haukutajwa "
    "moja kwa moja kama kategoria tofauti katika Ratiba ya GN 487A. "
    "Unaweza kuangukia chini ya Kategoria 15 'Umiliki na uendeshaji "
    "wa viwanda vidogo na vidogo sana (micro and small industries)' "
    "kama unafanywa kama biashara ya viwanda vidogo. Kwa sababu "
    "haukutajwa wazi, thibitisha hali yako mahususi na Idara ya "
    "Uhamiaji au wakili kabla ya kuhitimisha kama umejumuishwa au la.")

# B2 — SCP_016
fix("b008_gn487a_scp_016_20260612", "answer_en",
    "Second-hand goods trading is among the business categories "
    "prohibited for non-citizens under GN 487A.",
    "Second-hand goods trading is not explicitly named as a separate "
    "category in the GN 487A Schedule. However, selling second-hand "
    "goods in retail stores or wholesale may fall under Category 1 "
    "'The business of sale of goods on a wholesale and retail basis' "
    "— which IS explicitly prohibited. If you are selling used goods "
    "in a shop or market stall in retail or wholesale format, this "
    "is likely covered under Category 1. Verify with the Immigration "
    "Department for your specific situation.")

fix("b008_gn487a_scp_016_20260612", "answer_sw",
    "Biashara ya bidhaa za mikono ya pili (second-hand goods trading) "
    "iko kwenye aina za biashara zilizopigwa marufuku kwa wageni "
    "chini ya GN 487A.",
    "Biashara ya bidhaa za mitumba haikutajwa moja kwa moja kama "
    "kategoria tofauti katika Ratiba ya GN 487A. Hata hivyo, kuuza "
    "bidhaa za mitumba madukani au masokoni kwa njia ya rejareja "
    "au jumla kunaweza kuangukia chini ya Kategoria 1 'Biashara ya "
    "kuuza bidhaa kwa jumla na rejareja' — ambayo IMEkatazwa wazi. "
    "Thibitisha na Idara ya Uhamiaji kwa hali yako mahususi.")

# B3 — SCP_018
fix("b008_gn487a_scp_018_20260612", "answer_en",
    "the business of selling agricultural produce and basic goods "
    "at markets (petty trade / market vending) is among the businesses "
    "prohibited for non-citizens.",
    "Selling vegetables and fruits at a market stall in retail "
    "format falls under Category 1 of GN 487A — 'The business of "
    "sale of goods on a wholesale and retail basis' — which is "
    "explicitly prohibited for non-citizens. While petty market "
    "vending is not named as a separate category, retail sale of "
    "any goods including produce at a market stall is covered by "
    "Category 1. A Portuguese national selling produce at Kariakoo "
    "market is violating GN 487A under Category 1.")

fix("b008_gn487a_scp_018_20260612", "answer_sw",
    "biashara ya kuuza mazao ya kilimo na bidhaa za msingi sokoni "
    "(petty trade / market vending) iko miongoni mwa biashara "
    "zilizopigwa marufuku kwa wageni.",
    "Kuuza mboga na matunda kwenye soko la rejareja kunaangukia "
    "chini ya Kategoria 1 ya GN 487A — 'Biashara ya kuuza bidhaa "
    "kwa jumla na rejareja' — ambayo IMEkatazwa wazi kwa wageni. "
    "Ingawa biashara ndogo ya soko (petty trade) haikutajwa kama "
    "kategoria tofauti, uuzaji wa bidhaa yoyote kwa njia ya rejareja "
    "sokoni umejumuishwa katika Kategoria 1. Mreno anayeuza mboga "
    "Kariakoo anakiuka GN 487A chini ya Kategoria 1.")

# B4 — SCP_005
fix("b008_gn487a_scp_005_20260612", "answer_en",
    "(6) barbershops, (7) tailoring and garment making, "
    "(8) small-scale food outlets",
    "(6) small-scale mining, (7) postal activities and parcel "
    "delivery, (8) tour guiding within the country, "
    "(9) establishment and operation of radio and television, "
    "(10) operation of museums or curio shops, "
    "(11) brokerage or agency in businesses and real estate, "
    "(12) clearing and forwarding services, "
    "(13) on-farm crop purchasing operations, "
    "(14) ownership or operation of gambling machines except in "
    "casino premises, (15) ownership and operation of micro and "
    "small industries. Note: barbershops fall under Category 4 "
    "(salon business). The complete official list is available "
    "at TanzLII or the Immigration Department.")

fix("b008_gn487a_scp_005_20260612", "answer_sw",
    "(6) kinyozi, (7) ushonaji wa nguo, (8) mkahawa wa chakula "
    "wa kiwango kidogo",
    "(6) uchimbaji madini wa kiwango kidogo, (7) huduma za posta "
    "na usafirishaji wa vifurushi ndani ya nchi, (8) uongozaji "
    "wa watalii ndani ya nchi, (9) uanzishaji na uendeshaji wa "
    "redio na televisheni, (10) uendeshaji wa makumbusho au maduka "
    "ya vinyago, (11) udalali au wakala wa biashara na mali isiyohamika, "
    "(12) huduma za usafishaji forodha na usafirishaji, (13) ununuzi "
    "wa mazao shambani, (14) umiliki au uendeshaji wa mashine za "
    "kamari isipokuwa ndani ya kasino, (15) umiliki na uendeshaji "
    "wa viwanda vidogo na vidogo sana. Kumbuka: kinyozi iko chini ya "
    "Kategoria 4 (salon business). Orodha kamili rasmi inapatikana "
    "kwenye TanzLII au Idara ya Uhamiaji.")

# B5 — SCP_008
fix("b008_gn487a_scp_008_20260612", "answer_en",
    "(2) Small food outlet — is on the list.",
    "(2) Small food outlet — is NOT explicitly named in the GN 487A "
    "Schedule. However, if it involves retail sale of goods it may "
    "fall under Category 1 (retail trade). Verify with Immigration.")

fix("b008_gn487a_scp_008_20260612", "answer_sw",
    "(2) Mkahawa mdogo wa chakula — ipo kwenye orodha.",
    "(2) Mkahawa mdogo wa chakula — HAIKO kwenye orodha kama "
    "kategoria iliyotajwa wazi katika GN 487A. Hata hivyo, kama "
    "inahusisha uuzaji wa bidhaa kwa rejareja inaweza kuangukia "
    "chini ya Kategoria 1 (biashara ya rejareja). Thibitisha na "
    "Idara ya Uhamiaji.")

# B6 — SCP_020
fix("b008_gn487a_scp_020_20260612", "answer_en",
    "retail, wholesale, mobile money transfers, phone repair, "
    "hair salons, barbershops, tailoring, small food outlets, "
    "cleaning services, second-hand goods trade, and others",
    "retail and wholesale (excl. supermarkets and specialised "
    "outlets), mobile money transfers, phone and electronic device "
    "repair, salon business (excl. hotel/tourism), home and office "
    "cleaning, small-scale mining, postal and parcel delivery, "
    "local tour guiding, radio and television operation, museums "
    "and curio shops, business and real estate brokerage, clearing "
    "and forwarding, on-farm crop purchasing, gambling machines "
    "(excl. casino), and micro/small industries.")

fix("b008_gn487a_scp_020_20260612", "answer_sw",
    "rejareja, jumla, uhamisho wa pesa za simu, ukarabati wa simu, "
    "salon, kinyozi, ushonaji, mkahawa mdogo, huduma za usafi, "
    "bidhaa za pili mkono, na mengine",
    "rejareja na jumla (isipokuwa supermarkets na vituo maalum), "
    "uhamisho wa pesa za simu, ukarabati wa simu na vifaa vya "
    "elektroniki, salon (isipokuwa hoteli/utalii), usafi wa nyumba "
    "na ofisi, uchimbaji madini mdogo, posta na usafirishaji "
    "vifurushi, uongozaji watalii, redio na televisheni, makumbusho "
    "na maduka ya vinyago, udalali wa biashara na mali isiyohamika, "
    "usafishaji forodha, ununuzi wa mazao shambani, mashine za "
    "kamari (isipokuwa kasino), na viwanda vidogo na vidogo sana.")


# ─── SECTION D — VAT CORRECTIONS ─────────────────────────────────────────────

# D1 — VAT_PRO_014
fix("b008_vat_pro_014_20260612", "answer_en",
    "Yes — as a registered CPA, you must register for VAT for ALL your "
    "businesses including your clothing shop. Your CPA licence makes you a "
    "'regulated profession' requiring VAT registration regardless of sales "
    "volume.",
    "As a registered CPA, your PROFESSIONAL ACCOUNTING SERVICES activity "
    "requires immediate VAT registration regardless of fees earned — this is "
    "confirmed by TRA. For your clothing shop as a SEPARATE unrelated business: "
    "the standard threshold of TZS 200M per 12 months or TZS 100M per 6 months "
    "applies to that business independently. Your CPA registration does not "
    "automatically extend mandatory VAT registration to your unrelated clothing "
    "business. However, both activities must be declared to TRA — confirm your "
    "specific combined situation with TRA or a qualified tax adviser.")

fix("b008_vat_pro_014_20260612", "answer_sw",
    "Ndiyo — kama CPA aliyesajiliwa, lazima usajili VAT kwa biashara ZOTE "
    "unazofanya, ikiwa ni pamoja na duka lako la nguo. Leseni yako ya CPA "
    "inakufanya 'fani inayodhibitiwa' ambayo inahitaji usajili wa VAT bila "
    "kujali mauzo.",
    "Kama CPA aliyesajiliwa, SHUGHULI ZAKO ZA UHASIBU zinastahili usajili "
    "wa VAT bila kujali mapato — hii imethibitishwa na TRA. Kwa duka lako la "
    "nguo kama biashara TOFAUTI isiyohusiana: kizingiti cha kawaida cha TZS "
    "200M kwa miezi 12 au TZS 100M kwa miezi 6 kinatumika kwa biashara hiyo "
    "tofauti. Leseni yako ya CPA haifanyi usajili wa VAT wa lazima kwa biashara "
    "zako zote ambazo hazihusiani na uhasibu. Hata hivyo, shughuli zote lazima "
    "ziorodheshwe kwa TRA — thibitisha hali yako maalum ya pamoja na TRA au "
    "mshauri wa kodi aliyehitimu.")


# ─── SECTION E — PAYE CORRECTIONS ────────────────────────────────────────────

# E2 — paye_adv_005 (entire pair about TZS 26,000 — replace whole answer)
for p in pairs:
    if p["id"] == "b008_paye_adv_005_20260612":
        p["answer_en"] = ("Tanzania's PAYE system has a zero-rate band for the first TZS 270,000 "
            "of monthly income — this is the built-in tax-free allowance. There is no "
            "separate monthly personal relief of TZS 26,000 to subtract from calculated "
            "PAYE. Income above TZS 270,000 is taxed progressively starting at 8%. "
            "For accurate PAYE calculations for your specific salary: use TRA IDRAS "
            "(taidras.tra.go.tz) or the services of a qualified tax accountant.")
        p["answer_sw"] = ("Mfumo wa PAYE Tanzania una bendi ya kiwango cha sifuri kwa TZS 270,000 "
            "za kwanza za mapato ya kila mwezi — hii ndiyo ruhusa ya mapato yasiyotozwa "
            "kodi iliyojengwa ndani ya mfumo. Hakuna punguzo la kibinafsi tofauti la "
            "TZS 26,000 kwa mwezi linalotakiwa kukatwa kutoka PAYE iliyohesabiwa. "
            "Mapato yanayozidi TZS 270,000 yanatozwa kodi kwa msururu wa 8% kuanzia. "
            "Kwa mahesabu sahihi ya PAYE ya mshahara wako mahususi: tumia TRA IDRAS "
            "(taidras.tra.go.tz) au msaada wa mhesabu wa kodi aliyehitimu.")
        changes.setdefault("b008_paye_adv_005_20260612", []).append("answer_en+answer_sw (replaced)")
        break

# E3 — paye_adv_004 (example calculation uses wrong relief)
fix("b008_paye_adv_004_20260612", "answer_en",
    "Band 3 (520,001-600,000): TZS 80,000 × 20% = TZS 16,000; "
    "Total PAYE before relief: TZS 36,000; Personal relief: TZS 26,000; "
    "PAYE to pay: TZS 10,000.",
    "Band 3 (520,001-600,000): TZS 80,000 × 20% = TZS 16,000; "
    "Total PAYE: TZS 36,000. Note: Tanzania's PAYE has no separate monthly "
    "personal relief deduction — the zero-rate up to TZS 270,000 is the only "
    "built-in allowance. For specific salary calculations use TRA IDRAS "
    "(taidras.tra.go.tz).")

fix("b008_paye_adv_004_20260612", "answer_sw",
    "Bendi 3 (520,001-600,000): TZS 80,000 × 20% = TZS 16,000; "
    "Jumla ya PAYE kabla ya punguzo: TZS 36,000; Punguzo la kibinafsi: "
    "TZS 26,000; PAYE ya kulipa: TZS 10,000.",
    "Bendi 3 (520,001-600,000): TZS 80,000 × 20% = TZS 16,000; "
    "Jumla ya PAYE: TZS 36,000. Kumbuka: PAYE Tanzania haina punguzo la "
    "kibinafsi tofauti la kila mwezi linalotakiwa kukatwa — kiwango cha sifuri "
    "hadi TZS 270,000 ndiyo ruhusa pekee iliyojengwa ndani ya mfumo. "
    "Kwa mahesabu ya mshahara mahususi tumia TRA IDRAS (taidras.tra.go.tz).")

# E4 — paye_adv_007 (uses TZS 26,000 to explain 270,001)
fix("b008_paye_adv_007_20260612", "answer_en",
    "TZS 1 × 8% = TZS 0.08 (effectively zero because the TZS 26,000 "
    "personal relief covers this tiny amount).",
    "TZS 1 × 8% = TZS 0.08. This is effectively zero in any practical "
    "sense — the total PAYE generated at this income level is negligible. "
    "Note: there is no separate TZS 26,000 monthly personal relief "
    "deduction in Tanzania's PAYE system.")

fix("b008_paye_adv_007_20260612", "answer_sw",
    "TZS 1 × 8% = TZS 0.08 (si hadi 0 kwa sababu punguzo la kibinafsi "
    "la TZS 26,000 linafunika kiasi hiki kidogo).",
    "TZS 1 × 8% = TZS 0.08. Kwa vitendo kiasi hiki ni kidogo sana — "
    "PAYE inayozalishwa kwa kiwango hiki cha mapato ni ndogo mno. "
    "Kumbuka: hakuna punguzo la kibinafsi tofauti la TZS 26,000 kwa mwezi "
    "katika mfumo wa PAYE Tanzania.")

# E5 — paye_adv_001
fix("b008_paye_adv_001_20260612", "answer_en",
    "Personal relief: TZS 26,000/month.",
    "Annual tax-free threshold: TZS 3,240,000 (TZS 270,000/month at 0%, "
    "built into Band 1).")

fix("b008_paye_adv_001_20260612", "answer_sw",
    "Punguzo la kibinafsi: TZS 26,000/mwezi.",
    "Kizingiti cha mapato yasiyotozwa kodi: TZS 3,240,000 kwa mwaka "
    "(TZS 270,000/mwezi kwa kiwango cha 0%, imejengwa ndani ya Bendi 1).")

# E6 — paye_adv_002, 010, 012, 013, 015 (generic TZS 26,000 removal)
E6_IDS = [
    "b008_paye_adv_002_20260612",
    "b008_paye_adv_010_20260612",
    "b008_paye_adv_012_20260612",
    "b008_paye_adv_013_20260612",
    "b008_paye_adv_015_20260612",
]
EN_PATTERNS = [
    "personal relief: TZS 26,000",
    "Personal relief: TZS 26,000",
    "personal relief TZS 26,000",
    "Personal relief TZS 26,000",
]
SW_PATTERNS = [
    "punguzo la kibinafsi: TZS 26,000",
    "Punguzo la kibinafsi: TZS 26,000",
    "punguzo la kibinafsi TZS 26,000",
    "Punguzo la kibinafsi TZS 26,000",
]
EN_REPLACE = ("Annual tax-free threshold: TZS 3,240,000/year (TZS 270,000/month "
              "at 0% — built into Band 1, no separate monthly relief).")
SW_REPLACE = ("Kizingiti cha mapato yasiyotozwa kodi: TZS 3,240,000/mwaka "
              "(TZS 270,000/mwezi kwa 0% — imejengwa ndani ya Bendi 1, hakuna "
              "punguzo tofauti la kila mwezi).")

for p in pairs:
    if p["id"] in E6_IDS:
        for pat in EN_PATTERNS:
            if pat in p["answer_en"]:
                p["answer_en"] = p["answer_en"].replace(pat, EN_REPLACE, 1)
                changes.setdefault(p["id"], []).append("answer_en")
        for pat in SW_PATTERNS:
            if pat in p["answer_sw"]:
                p["answer_sw"] = p["answer_sw"].replace(pat, SW_REPLACE, 1)
                changes.setdefault(p["id"], []).append("answer_sw")

# E7 — gn487a_dpt_012 (enforcement dates unverifiable)
fix("b008_gn487a_dpt_012_20260612", "answer_en",
    "The first enforcement operation took place between 11 September 2025 "
    "and 8 October 2025 led by the Immigration Department.",
    "An enforcement operation was conducted by the Immigration Department "
    "in the months following the gazette date of 28 July 2025. Verify "
    "current enforcement status with the Immigration Department directly.")

fix("b008_gn487a_dpt_012_20260612", "answer_sw",
    "Operesheni ya utekelezaji wa kwanza ilifanyika kati ya tarehe 11 "
    "Septemba 2025 na 8 Oktoba 2025 ikiongozwa na Idara ya Uhamiaji.",
    "Operesheni ya utekelezaji ilifanywa na Idara ya Uhamiaji katika "
    "miezi iliyofuata tarehe ya gazeti ya 28 Julai 2025. Thibitisha hali "
    "ya sasa ya utekelezaji na Idara ya Uhamiaji moja kwa moja.")

# E8 — paye_adv_006 (deadline 20th → 7th)
for p in pairs:
    if p["id"] == "b008_paye_adv_006_20260612":
        if "20th" in p["answer_en"]:
            p["answer_en"] = p["answer_en"].replace("20th", "7th of the following month")
            changes.setdefault(p["id"], []).append("answer_en")
        if "tarehe 20" in p["answer_sw"]:
            p["answer_sw"] = p["answer_sw"].replace("tarehe 20", "tarehe 7 ya mwezi unaofuata")
            changes.setdefault(p["id"], []).append("answer_sw")


# ─── WRITE BACK ───────────────────────────────────────────────────────────────
with open(FILEPATH, "w", encoding="utf-8") as f:
    for p in pairs:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

print(f"\n=== CORRECTIONS APPLIED ===")
print(f"Total pairs written: {len(pairs)}")
print(f"Pairs modified: {len(changes)}")
for pid, fields in sorted(changes.items()):
    print(f"  {pid}: {', '.join(fields)}")
