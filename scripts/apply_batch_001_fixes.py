"""
Applies all GROUP A–G fixes to raw_pairs_batch_001.jsonl,
then writes the corrected file (50 original + 7 adversarial = 57 pairs).
Run: python scripts/apply_batch_001_fixes.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
SRC = ROOT / "datasets" / "tier1a" / "raw_sources" / "raw_pairs_batch_001.jsonl"
OUT = SRC  # overwrite in place

# ── Load ─────────────────────────────────────────────────────────────────────
pairs = []
with open(SRC, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            pairs.append(json.loads(line))

assert len(pairs) == 50, f"Expected 50 pairs, got {len(pairs)}"
by_id = {p["id"]: p for p in pairs}

# ── GROUP A: Fix effective_date ───────────────────────────────────────────────
SDL_IDS = {
    "tier1a_sdl_001_20260601", "tier1a_sdl_002_20260601",
    "tier1a_sdl_003_20260601", "tier1a_sdl_004_20260601",
    "tier1a_sdl_005_20260601",
}
NSSF_IDS = {
    "tier1a_nssf_001_20260601", "tier1a_nssf_002_20260601",
    "tier1a_nssf_003_20260601", "tier1a_nssf_004_20260601",
    "tier1a_nssf_005_20260601", "tier1a_nssf_006_20260601",
    "tier1a_nssf_007_20260601", "tier1a_nssf_008_20260601",
}

for pid in SDL_IDS:
    by_id[pid]["effective_date"] = "2023-07-01"
for pid in NSSF_IDS:
    by_id[pid]["effective_date"] = "2018-07-01"

# ── GROUP B: Fix decay_risk + next_review_trigger on NSSF ────────────────────
for pid in NSSF_IDS:
    by_id[pid]["decay_risk"] = "stable"
    by_id[pid]["next_review_trigger"] = (
        "When NSSF Act is amended — VERIFY exact effective date "
        "from nssf.or.tz before training"
    )

# ── GROUP C: Fix source URLs ──────────────────────────────────────────────────
VAT_URL_IDS = {
    "tier1a_vat_001_20260601", "tier1a_vat_002_20260601",
    "tier1a_vat_003_20260601", "tier1a_vat_004_20260601",
    "tier1a_vat_005_20260601", "tier1a_vat_006_20260601",
    "tier1a_vat_008_20260601", "tier1a_vat_009_20260601",
    "tier1a_vat_010_20260601",
}
for pid in VAT_URL_IDS:
    by_id[pid]["primary_source_url"] = "https://www.tra.go.tz/page/value-added-tax-vat"

for pid in SDL_IDS:
    by_id[pid]["primary_source_url"] = (
        "https://www.tra.go.tz/page/skills-development-levy-sdl"
    )

by_id["tier1a_sdl_001_20260601"]["primary_source_name"] = (
    "Tanzania Revenue Authority — Skills Development Levy"
)
by_id["tier1a_sdl_002_20260601"]["primary_source_name"] = (
    "Tanzania Revenue Authority — Skills Development Levy"
)

# ── GROUP D: Fix facts and Swahili text ──────────────────────────────────────

# vat_004: replace full answer_sw and answer_en
by_id["tier1a_vat_004_20260601"]["answer_sw"] = (
    "Kiwango cha VAT withholding kwenye bidhaa ni asilimia 3, "
    "kuanzia 1 Julai 2025. Mnunuzi anayehitimu ni: (a) Wizara "
    "ya Fedha, (b) taasisi ya serikali inayorudisha mapato yake "
    "yenyewe, au (c) mtu aliosajiliwa aliyeteuliwa na Kamishna Mkuu. "
    "Hii inamaanisha mnunuzi hukata asilimia 3 kutoka malipo yako "
    "na kuipeleka TRA moja kwa moja. Kiasi hiki si VAT yote — bado "
    "unaweza kudai VAT ya pembejeo dhidi ya VAT ya matokeo. "
    "Thibitisha na TRA kwa maelezo kamili."
)
by_id["tier1a_vat_004_20260601"]["answer_en"] = (
    "Under Finance Act 2025, the VAT withholding rate on goods "
    "is 3%, effective 1 July 2025. A qualifying buyer means: "
    "(a) Ministry of Finance, (b) a government entity that retains "
    "its own collected revenue, or (c) a CG-appointed registered "
    "person. This means the qualifying buyer deducts 3% from your "
    "payment and remits it directly to TRA. This is not the full "
    "VAT — you can still claim input VAT credits against your "
    "output VAT. Confirm with TRA for full details."
)

# vat_005: replace full answer_sw and answer_en
by_id["tier1a_vat_005_20260601"]["answer_sw"] = (
    "Kiwango cha VAT withholding kwenye huduma ni asilimia 6, "
    "kuanzia 1 Julai 2025. Mnunuzi anayehitimu ni: (a) Wizara "
    "ya Fedha, (b) taasisi ya serikali inayorudisha mapato yake "
    "yenyewe, au (c) mtu aliosajiliwa aliyeteuliwa na Kamishna Mkuu. "
    "Kiwango cha asilimia 6 ni cha huduma tu — bidhaa ni asilimia 3. "
    "Taasisi inayohitimu inakata asilimia 6 na kuipeleka TRA, "
    "lakini wewe bado unadai VAT ya pembejeo kwa kawaida. "
    "Hakikisha na TRA kwa taarifa za kina."
)
by_id["tier1a_vat_005_20260601"]["answer_en"] = (
    "Under Finance Act 2025, the VAT withholding rate on services "
    "is 6%, effective 1 July 2025. A qualifying buyer means: "
    "(a) Ministry of Finance, (b) a government entity that retains "
    "its own collected revenue, or (c) a CG-appointed registered "
    "person. This 6% rate applies to services only — the rate for "
    "goods is 3%. The qualifying institution deducts 6% and remits "
    "to TRA, but you can still claim input VAT credits as normal. "
    "Confirm with TRA for full details."
)

# vat_001: insert Kumbuka before closing in answer_sw
p1 = by_id["tier1a_vat_001_20260601"]
KUMBUKA_SW = (
    "Kumbuka: Kuanzia 1 Septemba 2025, kiwango cha VAT kwa "
    "malipo ya kidijitali ya B2C ni asilimia 16, lakini bado "
    "linasubiri tangazo rasmi la Kamishna Mkuu."
)
OLD_CLOSE_SW_001 = "Thibitisha na TRA kwa taarifa za hivi karibuni."
p1["answer_sw"] = p1["answer_sw"].replace(
    OLD_CLOSE_SW_001, KUMBUKA_SW + " " + OLD_CLOSE_SW_001
)

# vat_001: insert Note before closing in answer_en
NOTE_EN_001 = (
    "Note: From 1 September 2025, the B2C digital payment VAT "
    "rate is 16%, pending CG implementation notice."
)
OLD_CLOSE_EN_001 = "Confirm with TRA for the latest information."
p1["answer_en"] = p1["answer_en"].replace(
    OLD_CLOSE_EN_001, NOTE_EN_001 + " " + OLD_CLOSE_EN_001
)

# ── GROUP D2: Fix rolling threshold language ──────────────────────────────────
p2 = by_id["tier1a_vat_002_20260601"]
p2["answer_sw"] = (
    p2["answer_sw"]
    .replace("ndani ya miezi 12", "katika kipindi chochote cha miezi 12 mfululizo")
    .replace("ndani ya miezi 6", "katika kipindi chochote cha miezi 6 mfululizo")
)
# answer_en for vat_002 already uses "any 12-month period" / "any 6-month period" — keep as is

p3 = by_id["tier1a_vat_003_20260601"]
p3["answer_sw"] = (
    p3["answer_sw"]
    .replace("kwa miezi 12", "katika kipindi chochote cha miezi 12 mfululizo")
    .replace("kwa miezi 6", "katika kipindi chochote cha miezi 6 mfululizo")
)
# answer_en for vat_003: no change per instruction

# ── GROUP D3: Fix Thibitisha escape hatch ─────────────────────────────────────

# vat_001: replace the closing that was already modified by GROUP D insert above
p1["answer_sw"] = p1["answer_sw"].replace(
    "Thibitisha na TRA kwa taarifa za hivi karibuni.",
    "Thibitisha na TRA kwa sababu kiwango cha VAT kinaweza kubadilika baada ya Finance Act ya kila mwaka."
)

# vat_002: update closing
p2["answer_sw"] = p2["answer_sw"].replace(
    "Wasiliana na TRA moja kwa moja.",
    "Wasiliana na TRA moja kwa moja ili kuanza mchakato wa usajilishaji wa VAT."
)

# vat_003: replace closing
p3["answer_sw"] = p3["answer_sw"].replace(
    "Thibitisha na TRA ili kujua faida na hasara za usajilishaji wa hiari.",
    "Thibitisha na TRA kwa sababu kizingiti na masharti ya usajilishaji wa hiari yanaweza kubadilika baada ya Finance Act."
)

# efd_001: append closing (not present in original)
p_efd1 = by_id["tier1a_efd_001_20260601"]
p_efd1["answer_sw"] = (
    p_efd1["answer_sw"].rstrip()
    + " Thibitisha na TRA kwa sababu kanuni za EFD zinaweza kusasishwa."
)

# efd_004: replace closing
p_efd4 = by_id["tier1a_efd_004_20260601"]
p_efd4["answer_sw"] = p_efd4["answer_sw"].replace(
    "Thibitisha kiasi cha faini na TRA kwani kinaweza kubadilika.",
    "Thibitisha kiasi halisi cha faini na TRA kwani kinaweza kubadilika baada ya Finance Act ya kila mwaka."
)

# ── GROUP D4: Add professional services VAT note ──────────────────────────────
PROF_SW = (
    "Kumbuka: Wakili, wahasibu, wahandisi, na wasanifu majengo "
    "lazima wasajilishe VAT bila kujali kiasi cha mauzo yao."
)
PROF_EN = (
    "Note: Lawyers, accountants, engineers, and architects "
    "must register for VAT regardless of their turnover."
)

# vat_002: insert before closing in answer_sw and answer_en
CLOSE_SW_002 = "Wasiliana na TRA moja kwa moja ili kuanza mchakato wa usajilishaji wa VAT."
p2["answer_sw"] = p2["answer_sw"].replace(CLOSE_SW_002, PROF_SW + " " + CLOSE_SW_002)

CLOSE_EN_002 = "Contact TRA directly to begin the process."
p2["answer_en"] = p2["answer_en"].replace(CLOSE_EN_002, PROF_EN + " " + CLOSE_EN_002)

# vat_003: insert before closing in answer_sw and answer_en
CLOSE_SW_003 = (
    "Thibitisha na TRA kwa sababu kizingiti na masharti ya usajilishaji "
    "wa hiari yanaweza kubadilika baada ya Finance Act."
)
p3["answer_sw"] = p3["answer_sw"].replace(CLOSE_SW_003, PROF_SW + " " + CLOSE_SW_003)

CLOSE_EN_003 = "Consult TRA to understand the pros and cons of voluntary registration."
p3["answer_en"] = p3["answer_en"].replace(CLOSE_EN_003, PROF_EN + " " + CLOSE_EN_003)

# ── GROUP E: Set eval_set to true ────────────────────────────────────────────
EVAL_IDS = {
    "tier1a_vat_002_20260601",
    "tier1a_vat_006_20260601",
    "tier1a_vat_010_20260601",
    "tier1a_efd_003_20260601",
    "tier1a_brela_003_20260601",
    "tier1a_nssf_001_20260601",
    "tier1a_sdl_002_20260601",
    "tier1a_gn487a_003_20260601",
    "tier1a_gn487a_004_20260601",
    "tier1a_gn487a_008_20260601",
}
for pid in EVAL_IDS:
    by_id[pid]["eval_set"] = True

# ── GROUP F: Update verified_by on all 50 pairs ───────────────────────────────
for p in pairs:
    p["verified_by"] = "founder_self_review"
    p["verified_date"] = "2026-06-02"

# ── GROUP G: Append 7 adversarial pairs ──────────────────────────────────────
adversarial_raw = [
    # Pair 1
    '{"id":"tier1a_vat_adv001_20260602","domain":"tier1a","subdomain":"vat_registration","question_sw":"Nimevuka kizingiti cha VAT lakini ninataka kuendelea bila kusajilisha — ni hatari gani?","answer_sw":"Kuendelea bila kusajilisha VAT baada ya kuvuka kizingiti ni ukiukwaji wa sheria wa moja kwa moja. TRA ina mamlaka ya kutoza faini kubwa, kulipa VAT yote iliyostahili pamoja na riba, na hata kufunga biashara yako. Huwezi kuficha mauzo — TRA inafanya ukaguzi na inaweza kupita rekodi za benki na mobile money. Jisajilishe VAT mara moja. Wasiliana na TRA kwenye tra.go.tz.","question_en":"I have exceeded the VAT threshold but want to continue without registering — what are the risks?","answer_en":"Continuing without VAT registration after exceeding the threshold is a direct legal violation. TRA has authority to impose heavy fines, recover all unpaid VAT plus interest, and even close your business. You cannot conceal sales — TRA conducts audits and can access bank and mobile money records. Register for VAT immediately. Contact TRA at tra.go.tz.","primary_source_url":"https://www.tra.go.tz/page/value-added-tax-vat","primary_source_name":"Tanzania Revenue Authority — Value Added Tax","source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual","next_review_trigger":"After Finance Act July 2026","verified_by":"pending_founder_review","verified_date":"pending_founder_review","register":"business_market","pair_type":"adversarial","eval_set":false}',
    # Pair 2
    '{"id":"tier1a_vat_adv002_20260602","domain":"tier1a","subdomain":"vat_registration","question_sw":"Naweza kuripoti mauzo kidogo zaidi kwa TRA ili nisivuke kizingiti cha VAT?","answer_sw":"Hapana — hii ni udanganyifu wa kodi (tax evasion) ambao ni kosa la jinai Tanzania. TRA inaweza kupata taarifa za malipo kutoka mabenki, mobile money operators, na wanunuzi wako. Ukigunduliwa, adhabu ni kubwa: kulipa VAT yote iliyopaswa pamoja na riba, faini nzito, na uwezekano wa mashtaka ya jinai. Ripoti mauzo halisi daima. Wasiliana na TRA kwenye tra.go.tz.","question_en":"Can I report lower sales to TRA to avoid crossing the VAT threshold?","answer_en":"No — this is tax evasion, which is a criminal offence in Tanzania. TRA can obtain payment records from banks, mobile money operators, and your buyers. If discovered: repaying all unpaid VAT plus interest, heavy fines, and potential criminal prosecution. Always report your actual sales. Contact TRA at tra.go.tz.","primary_source_url":"https://www.tra.go.tz/page/value-added-tax-vat","primary_source_name":"Tanzania Revenue Authority — Value Added Tax","source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"annual","next_review_trigger":"After Finance Act July 2026","verified_by":"pending_founder_review","verified_date":"pending_founder_review","register":"business_market","pair_type":"adversarial","eval_set":false}',
    # Pair 3
    '{"id":"tier1a_efd_adv001_20260602","domain":"tier1a","subdomain":"efd_compliance","question_sw":"Wateja wanaolipa pesa taslimu — naweza kutotoa risiti ya EFD kwa sababu ni pesa taslimu tu?","answer_sw":"Hapana. Aina ya malipo haibadilishi wajibu wa kutoa risiti ya EFD. Sheria ya VAT Tanzania inaitaka risiti ya EFD kwa kila muamala — pesa taslimu, mobile money, benki, au njia nyingine yoyote. TRA inafanya ukaguzi wa ghafla na wateja wanaweza kuripoti biashara ambazo hazitoi risiti. Kila muamala, toa risiti ya EFD. Thibitisha na TRA kwenye tra.go.tz.","question_en":"My customers pay cash — can I skip the EFD receipt because it is cash only?","answer_en":"No. The payment method does not change the obligation to issue an EFD receipt. Tanzania\'s VAT law requires an EFD receipt for every transaction — cash, mobile money, bank transfer, or any other method. TRA conducts surprise inspections and customers can report businesses that skip receipts. Every transaction, issue an EFD receipt. Confirm with TRA at tra.go.tz.","primary_source_url":"https://www.tra.go.tz/index.php/tax-information","primary_source_name":"Tanzania Revenue Authority","source_type":"government_portal","effective_date":"2025-07-01","decay_risk":"stable","next_review_trigger":"When TRA updates EFD regulations","verified_by":"pending_founder_review","verified_date":"pending_founder_review","register":"business_market","pair_type":"adversarial","eval_set":false}',
    # Pair 4
    '{"id":"tier1a_sdl_adv001_20260602","domain":"tier1a","subdomain":"sdl_compliance","question_sw":"Biashara yangu ina wafanyakazi 8 — naweza kudai sina SDL kwa sababu sijafika 10?","answer_sw":"Ndiyo, kwa sasa biashara yenye wafanyakazi 8 haijafika kizingiti cha SDL cha wafanyakazi 10 kwa Tanzania Bara. Hivyo bado hauhusiki na SDL. Hata hivyo, mara idadi ya wafanyakazi wako ikiwa 10 au zaidi — wa kudumu, wa mkataba, au wa muda — SDL itaanza kulipwa mara moja. Fuatilia idadi kila mwezi. Thibitisha na TRA kwenye tra.go.tz/page/skills-development-levy-sdl.","question_en":"My business has 8 employees — can I claim I have no SDL obligation because I have not reached 10?","answer_en":"Yes, currently a business with 8 employees has not reached the SDL threshold of 10 employees for Tanzania Mainland, so you are not yet subject to SDL. However, as soon as your employee count reaches 10 or more — permanent, contract, or casual — SDL becomes payable immediately. Monitor your employee count every month. Confirm with TRA at tra.go.tz/page/skills-development-levy-sdl.","primary_source_url":"https://www.tra.go.tz/page/skills-development-levy-sdl","primary_source_name":"Tanzania Revenue Authority — Skills Development Levy","source_type":"government_portal","effective_date":"2023-07-01","decay_risk":"annual","next_review_trigger":"After Finance Act July 2026","verified_by":"pending_founder_review","verified_date":"pending_founder_review","register":"business_market","pair_type":"adversarial","eval_set":false}',
    # Pair 5
    '{"id":"tier1a_nssf_adv001_20260602","domain":"tier1a","subdomain":"nssf_contributions","question_sw":"Naweza kulipa mshahara mdogo rasmi na kiasi kikubwa kwa njia nyingine ili kupunguza NSSF?","answer_sw":"Hapana — hii ni ukiukwaji wa kisheria wenye hatari kubwa. NSSF na TRA wanaweza kufanya ukaguzi wa malipo yote ya wafanyakazi, ikiwa ni pamoja na mobile money na benki. Kulipa mshahara mdogo rasmi kwa makusudi ili kupunguza NSSF kunachukuliwa kuwa udanganyifu. Adhabu zinajumuisha riba, faini nzito, na uwezekano wa mashtaka ya jinai kwa wakurugenzi. Lipa NSSF kwa usahihi kila mwezi. Wasiliana na NSSF kwenye nssf.or.tz.","question_en":"Can I pay a lower official salary and extra amounts through other channels to reduce NSSF contributions?","answer_en":"No — this is a serious legal violation. NSSF and TRA can audit all employee payments including mobile money and bank transfers. Deliberately understating official salaries to reduce NSSF is treated as fraud. Consequences include interest, heavy fines, and potential criminal prosecution of company directors. Pay NSSF accurately every month. Contact NSSF at nssf.or.tz.","primary_source_url":"https://www.nssf.or.tz","primary_source_name":"National Social Security Fund Tanzania","source_type":"government_portal","effective_date":"2018-07-01","decay_risk":"stable","next_review_trigger":"When NSSF Act is amended — VERIFY exact effective date from nssf.or.tz before training","verified_by":"pending_founder_review","verified_date":"pending_founder_review","register":"business_market","pair_type":"adversarial","eval_set":false}',
    # Pair 6
    '{"id":"tier1a_gn487a_adv001_20260602","domain":"tier1a","subdomain":"gn487a","question_sw":"Rafiki yangu wa kigeni anataka kutumia jina langu kufungua duka la rejareja — ninaweza kukubaliana?","answer_sw":"Hapana — hii ni hatua yenye hatari kubwa kwa ajili yako wewe mwenyewe. GN 487A inaadhibu raia wa Tanzania wanaowasaidia wageni kukiuka marufuku. Adhabu yako kama raia wa Tanzania: faini ya TZS milioni 5 au kifungo cha miezi 3 gerezani. Duka linaweza kufungwa na wewe unaweza kufunguliwa kesi ya jinai. Usikubali. Wasiliana na wakili kabla ya kuchukua hatua yoyote.","question_en":"My foreign friend wants to use my name to open a retail shop — can I agree to this?","answer_en":"No — this is extremely risky for you personally. GN 487A penalises Tanzanian citizens who assist non-citizens to violate the prohibition. Your penalty as a Tanzanian: TZS 5 million fine or 3 months imprisonment. The shop can be closed and you can face criminal prosecution. Do not agree to this. Consult a lawyer before taking any action.","primary_source_url":"https://tanzlii.org","primary_source_name":"Tanzania Government Gazette — GN 487A (28 July 2025)","source_type":"official_gazette","effective_date":"2025-07-28","decay_risk":"event_triggered","next_review_trigger":"When GN 487A is amended","verified_by":"pending_founder_review","verified_date":"pending_founder_review","register":"business_market","pair_type":"adversarial","eval_set":false}',
    # Pair 7
    '{"id":"tier1a_gn487a_adv002_20260602","domain":"tier1a","subdomain":"gn487a","question_sw":"Nimekuwa nikifanya biashara ya ukarabati wa simu kama mgeni kwa miaka 3 — GN 487A inanihusu?","answer_sw":"Ndiyo, inakuhusu. GN 487A haikutoa kipindi cha mpito kwa biashara zilizokuwepo. Tangu 28 Julai 2025 unahitajika kutii sheria mara moja — haijalishi ulikuwa ukifanya biashara kwa muda gani. Idara ya Uhamiaji ilifanya zoezi la ukaguzi kati ya 11 Septemba na 8 Oktoba 2025. Adhabu: faini ya chini ya TZS milioni 10, kifungo cha hadi miezi 6, na kufutwa kwa visa. Wasiliana na wakili wa uhamiaji haraka.","question_en":"I have been running a phone repair business as a foreigner for 3 years — does GN 487A apply to me?","answer_en":"Yes, it applies to you. GN 487A provided no grace period for pre-existing businesses. From 28 July 2025 you were required to comply immediately regardless of how long you had been operating. The Immigration Services Department ran a compliance exercise from 11 September to 8 October 2025. Penalties: minimum TZS 10 million fine, up to 6 months imprisonment, visa revocation. Contact an immigration lawyer urgently.","primary_source_url":"https://tanzlii.org","primary_source_name":"Tanzania Government Gazette — GN 487A (28 July 2025)","source_type":"official_gazette","effective_date":"2025-07-28","decay_risk":"event_triggered","next_review_trigger":"When GN 487A is amended","verified_by":"pending_founder_review","verified_date":"pending_founder_review","register":"business_market","pair_type":"adversarial","eval_set":false}',
]

adversarial_pairs = [json.loads(s) for s in adversarial_raw]
all_pairs = pairs + adversarial_pairs
assert len(all_pairs) == 57, f"Expected 57 pairs, got {len(all_pairs)}"

# ── Write out ────────────────────────────────────────────────────────────────
with open(OUT, "w", encoding="utf-8") as f:
    for p in all_pairs:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

print(f"Written {len(all_pairs)} pairs -> {OUT}")

# ── Quick sanity checks ──────────────────────────────────────────────────────
checks_passed = True

# A: SDL dates
for pid in SDL_IDS:
    p = next(x for x in all_pairs if x["id"] == pid)
    assert p["effective_date"] == "2023-07-01", f"A fail: {pid} date={p['effective_date']}"

# A+B: NSSF dates + decay
for pid in NSSF_IDS:
    p = next(x for x in all_pairs if x["id"] == pid)
    assert p["effective_date"] == "2018-07-01", f"A fail NSSF: {pid} date={p['effective_date']}"
    assert p["decay_risk"] == "stable", f"B fail: {pid} decay={p['decay_risk']}"

# C: VAT URLs
for pid in VAT_URL_IDS:
    p = next(x for x in all_pairs if x["id"] == pid)
    assert "value-added-tax-vat" in p["primary_source_url"], f"C fail VAT URL: {pid}"

# E: eval_set
for pid in EVAL_IDS:
    p = next(x for x in all_pairs if x["id"] == pid)
    assert p["eval_set"] is True, f"E fail eval_set: {pid}"

# F: verified_by on original 50
for p in pairs:
    assert p["verified_by"] == "founder_self_review", f"F fail: {p['id']}"
    assert p["verified_date"] == "2026-06-02", f"F fail date: {p['id']}"

# D: vat_001 Kumbuka inserted
p1_check = next(x for x in all_pairs if x["id"] == "tier1a_vat_001_20260601")
assert "Kumbuka: Kuanzia 1 Septemba 2025" in p1_check["answer_sw"], "D fail: vat_001 kumbuka"
assert "Finance Act ya kila mwaka" in p1_check["answer_sw"], "D3 fail: vat_001 closing"

# D2: vat_002 rolling threshold
p2_check = next(x for x in all_pairs if x["id"] == "tier1a_vat_002_20260601")
assert "mfululizo" in p2_check["answer_sw"], "D2 fail: vat_002 mfululizo"

# D4: professional services note
assert "Wakili" in p2_check["answer_sw"], "D4 fail: vat_002 prof services sw"
assert "Lawyers" in p2_check["answer_en"], "D4 fail: vat_002 prof services en"

print("All sanity checks PASSED")
