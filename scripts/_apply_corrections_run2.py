import json

path = "datasets/tier1a/raw_sources/raw_pairs_batch_002.jsonl"
pairs = []
with open(path, encoding="utf-8") as f:
    for line in f:
        pairs.append(json.loads(line))

by_id = {p["id"]: p for p in pairs}
changed = set()
flags = []

def sw(p, old, new):
    if old in p["answer_sw"]:
        p["answer_sw"] = p["answer_sw"].replace(old, new)
        changed.add(p["id"])
        return True
    flags.append(f"NOT FOUND {p['id']}.SW: [{old[:60]}]")
    return False

def en(p, old, new):
    if old in p["answer_en"]:
        p["answer_en"] = p["answer_en"].replace(old, new)
        changed.add(p["id"])
        return True
    flags.append(f"NOT FOUND {p['id']}.EN: [{old[:60]}]")
    return False

# ============================================================
# CORRECTION 5: Permit class errors
# ============================================================

# --- permit_001: daraja C → daraja B, add dual-permit note ---
p = by_id["tier1a_permit_001_20260603"]
sw(p, "daraja C", "daraja B")
sw(p, "Class C", "Class B")
en(p, "Class C", "Class B")
# Add dual-permit sentence before "Thibitisha"
sw(p,
   "Thibitisha na Idara ya Uhamiaji.",
   "Kawaida zinahitajika zote mbili: kibali cha kazi kutoka Wizara ya Kazi NA kibali cha makazi daraja B kutoka Idara ya Uhamiaji. Thibitisha na Idara ya Uhamiaji.")
en(p,
   "Confirm with the Immigration Department.",
   "Usually both are required: a work permit from the Ministry of Labour AND a Class B residence permit from Immigration. Confirm with the Immigration Department.")
print(f"Fixed permit_001: {p['answer_sw'][:120]}")

# --- permit_002: daraja B → daraja A, Class B → Class A ---
p = by_id["tier1a_permit_002_20260603"]
sw(p, "daraja B", "daraja A")
sw(p, "Class B", "Class A")
en(p, "Class B", "Class A")
print(f"Fixed permit_002: {p['answer_sw'][:120]}")

# --- permit_008: change daraja C → daraja B if present ---
p = by_id["tier1a_permit_008_20260603"]
if "daraja C" in p["answer_sw"]:
    sw(p, "daraja C", "daraja B")
    en(p, "Class C", "Class B")
    print(f"Fixed permit_008 (daraja C found)")
else:
    print(f"permit_008: no daraja C found — no change needed")

# --- permit_014: remove USD fee figure, replace with fee schedule ref ---
p = by_id["tier1a_permit_014_20260603"]
# SW: remove "Karibu na USD 500–2,000 kwa mwaka — lakini thibitisha..." block
sw(p,
   "Karibu na USD 500–2,000 kwa mwaka — lakini thibitisha ada halisi za sasa na Idara ya Uhamiaji kupitia tovuti immigration.go.tz, kwani ada zinaweza kubadilika.",
   "Ada zinatofautiana sana kulingana na aina ya kibali, uraia, na muda — angalia jedwali la sasa la ada kwenye immigration.go.tz")
# EN
en(p,
   "Approximately USD 500–2,000 per year — but confirm the current exact fees with the Immigration Department at immigration.go.tz, as fees may change.",
   "Fees vary widely by permit class, nationality and duration — check current schedule at immigration.go.tz")
print(f"Fixed permit_014: {p['answer_sw']}")

# ============================================================
# CORRECTION 6: Royalties withholding tax 10% → 15% non-residents
# ============================================================
p = by_id["tier1a_wh_007_20260603"]
sw(p, "asilimia 10 kwa wasio wakazi", "asilimia 15 kwa wasio wakazi")
en(p, "10% for non-residents", "15% for non-residents")
print(f"Fixed wh_007: {p['answer_sw']}")

# ============================================================
# CORRECTION 7: Provisional tax — 3 instalments → 4
# ============================================================
p = by_id["tier1a_income_tax_003_20260603"]
sw(p, "awamu tatu", "awamu nne")
sw(p,
   "awamu ya kwanza ifikapo mwisho wa mwezi wa 6 wa mwaka wa fedha, ya pili ifikapo mwisho wa mwezi wa 9, na ya tatu ifikapo mwisho wa mwezi wa 12",
   "awamu ya kwanza ifikapo mwisho wa mwezi wa 3 wa mwaka wa fedha, ya pili ifikapo mwisho wa mwezi wa 6, ya tatu ifikapo mwisho wa mwezi wa 9, na ya nne ifikapo mwisho wa mwezi wa 12")
en(p, "three instalments", "four instalments")
en(p,
   "first instalment by the end of month 6 of the financial year, second by end of month 9, and third by end of month 12",
   "first instalment by the end of month 3 of the financial year, second by end of month 6, third by end of month 9, and fourth by end of month 12")
print(f"Fixed income_tax_003")

# Confirm inc_tax_deep_001 already has awamu nne
p = by_id["tier1a_inc_tax_deep_001_20260603"]
if "awamu nne" in p["answer_sw"] and "four instalments" in p["answer_en"]:
    print("inc_tax_deep_001: awamu nne confirmed — no change needed")
else:
    sw(p, "awamu tatu", "awamu nne")
    en(p, "three instalments", "four instalments")
    print("inc_tax_deep_001: fixed")

# Confirm inc_tax_deep_010 already has awamu 4
p = by_id["tier1a_inc_tax_deep_010_20260603"]
if "awamu 4" in p["answer_sw"] or "awamu nne" in p["answer_sw"]:
    print("inc_tax_deep_010: four instalments confirmed — no change needed")
else:
    flags.append("FLAG inc_tax_deep_010: neither 'awamu 4' nor 'awamu nne' found — check manually")

# ============================================================
# CORRECTION 8: Minimum turnover tax 0.3% → 1%
# ============================================================
p = by_id["tier1a_inc_tax_deep_011_20260603"]
sw(p, "asilimia 0.3 ya mapato ghafi (turnover minimum tax)", "asilimia 1 ya mapato ghafi (turnover minimum tax)")
sw(p,
   "Kodi hii inalipwa hata kama kampuni ina hasara halisi.",
   "Kodi hii inalipwa hata kama kampuni ina hasara halisi. Kuanzia tarehe 1 Julai 2025 kiwango kimeongezwa kutoka asilimia 0.5 hadi asilimia 1.")
en(p, "minimum tax of 0.3% of gross turnover", "minimum tax of 1% of gross turnover")
en(p,
   "This tax is paid even if the company has genuine losses.",
   "This tax is paid even if the company has genuine losses. Effective 1 July 2025 the rate increased from 0.5% to 1%.")
print(f"Fixed inc_tax_deep_011")

# ============================================================
# CORRECTION 9: Commissioner decision deadline 90 days → 6 months
# ============================================================
p = by_id["tier1a_tax_disp_001_20260603"]
sw(p,
   "Kamishna atapitia hoja na kutoa uamuzi ndani ya siku 90.",
   "Kamishna atapitia hoja na kutoa uamuzi ndani ya miezi 6 kutoka tarehe ya kukubali hoja.")
en(p,
   "The Commissioner will review the objection and issue a decision within 90 days.",
   "The Commissioner will review the objection and issue a decision within 6 months from the date of admission of the objection.")
print(f"Fixed tax_disp_001 (C9: deadline)")

# ============================================================
# CORRECTION 10: Add 1/3 deposit requirement at beginning
# ============================================================
p = by_id["tier1a_tax_disp_001_20260603"]
deposit_sw = ("MUHIMU: Kabla ya kuwasilisha hoja ya pingamizi, lazima ulipe kiwango kikubwa kati ya: "
              "(a) kodi isiyobishaniwa AU (b) theluthi moja (1/3) ya kodi iliyotathminiwa — ndani ya siku 15 "
              "baada ya kupokea tathmini. Bila malipo haya hoja haitakubaliwa na TRA. ")
deposit_en = ("IMPORTANT: Before filing the objection, you must pay the higher of: "
              "(a) undisputed tax OR (b) one-third (1/3) of the assessed tax — within 15 days of receiving "
              "the assessment. Without this payment TRA will not admit the objection. ")
p["answer_sw"] = deposit_sw + p["answer_sw"]
p["answer_en"] = deposit_en + p["answer_en"]
changed.add(p["id"])
print(f"Fixed tax_disp_001 (C10: deposit requirement added at start)")

# ============================================================
# CORRECTION 11: Objection extension — remove "nadra sana"
# ============================================================
p = by_id["tier1a_tax_disp_002_20260603"]
sw(p,
   "Hii ni nadra sana. Kila wakati, boresha hoja na uwasilishe ndani ya siku 30 — usitegemee kupata upanuzi.",
   "Omba ndani ya siku 7 kabla ya kumalizika kwa siku 30. Kamishna anaweza kutoa nyongeza ya hadi siku 30 zaidi ikiwa sababu ni nzuri. Hii ni haki iliyoko kisheria — si bahati.")
en(p,
   "This is very rare. Always prepare your objection and file within 30 days — do not rely on getting an extension.",
   "Apply within 7 days before the 30-day limit expires. The Commissioner may grant up to 30 additional days if reasonable grounds exist. This is a statutory right — not a matter of luck.")
print(f"Fixed tax_disp_002 (C11: extension language)")

# ============================================================
# CORRECTION 12: TRAB — add Step 2 after 30-day notice text
# ============================================================
p = by_id["tier1a_tax_disp_003_20260603"]
sw(p,
   "unaweza kupiga rufaa kwa TRAB ndani ya siku 30 baada ya kupokea uamuzi wa Kamishna.",
   ("unaweza kupiga rufaa kwa TRAB ndani ya siku 30 baada ya kupokea uamuzi wa Kamishna. "
    "Hatua ya 2: Wasilisha Maombi rasmi ya Rufaa (Statement of Appeal) kwa TRAB ndani ya siku 45 baada ya uamuzi huo huo. "
    "Hatua zote mbili ni za lazima — kukosa moja yao kunasababisha rufaa kutokubaliwa."))
en(p,
   "you may appeal to TRAB within 30 days of receiving the Commissioner's decision.",
   ("you may appeal to TRAB within 30 days of receiving the Commissioner's decision. "
    "Step 2: Lodge the formal Statement of Appeal with TRAB within 45 days of the same Commissioner decision. "
    "Both steps are mandatory — missing either step causes the appeal to be inadmissible."))
print(f"Fixed tax_disp_003 (C12: TRAB Step 2)")

# ============================================================
# CORRECTION 13: Stamp duty property transfer — flat 1%
# ============================================================
p = by_id["tier1a_stamp_duty_004_20260603"]
sw(p,
   "Kodi ya stempu kwenye mabadiliko ya mali isiyohamia (exchange of property) ni asilimia 0.5 kwa TZS 100,000 ya kwanza ya thamani, kisha asilimia 1 ya thamani inayozidi TZS 100,000.",
   "Kodi ya stempu kwenye uhamishaji wa ardhi au nyumba ni asilimia 1 ya thamani ya malipo au thamani ya soko. Kwa mfano, mali inayouzwa kwa TZS 500,000,000 inalipa kodi ya stempu ya TZS 5,000,000.")
en(p,
   "Stamp duty on an exchange of immovable property (land or buildings) is 0.5% on the first TZS 100,000 of value, then 1% on the value exceeding TZS 100,000.",
   "Stamp duty on transfer of land or buildings is 1% of the consideration or market value. For example, property sold for TZS 500,000,000 pays stamp duty of TZS 5,000,000.")
print(f"Fixed stamp_duty_004 (C13: flat 1%)")

# ============================================================
# SAVE
# ============================================================
with open(path, "w", encoding="utf-8") as out:
    for p in pairs:
        out.write(json.dumps(p, ensure_ascii=False) + "\n")

print(f"\nTotal pairs changed: {len(changed)}")
print("Changed IDs:", sorted(changed))
if flags:
    print("\nFLAGS:")
    for f in flags:
        print(" -", f)
else:
    print("No flags.")
