import json, sys
sys.stdout.reconfigure(encoding="utf-8")

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
    flags.append(f"NOT FOUND {p['id']}.SW: [{old[:70]}]")
    return False

def en(p, old, new):
    if old in p["answer_en"]:
        p["answer_en"] = p["answer_en"].replace(old, new)
        changed.add(p["id"])
        return True
    flags.append(f"NOT FOUND {p['id']}.EN: [{old[:70]}]")
    return False

# ============================================================
# CORRECTION 14: P9 deadline 31 January -> 31 March
# ============================================================
p = by_id["tier1a_paye_extended_004_20260603"]
sw(p, "31 Januari", "31 Machi")
en(p, "31 January", "31 March")
print(f"C14 Fixed paye_extended_004")

# ============================================================
# CORRECTION 15: Remove P45, replace with Leaving Certificate / P9
# ============================================================
p = by_id["tier1a_paye_extended_018_20260603"]
sw(p,
   "Mwajiri anatoa Fomu P45 (au hati sawa) ikionyesha jumla ya mshahara na PAYE iliyokatwa hadi tarehe ya kumaliza kazi. Fomu hii inasaidia mwajiri mpya kuhesabu PAYE kwa usahihi kwa sehemu ya mwaka iliyobaki.",
   "Mwajiri anatoa Hati ya Kuacha Kazi au sehemu husika ya Fomu P9 inayoonyesha jumla ya mapato na PAYE iliyokatwa hadi tarehe ya kumaliza kazi. Thibitisha hati halisi inayohitajika na TRA.")
en(p,
   "The employer issues Form P45 (or equivalent) showing total earnings and PAYE deducted up to the date of leaving. This form helps the new employer calculate PAYE correctly for the remainder of the year.",
   "The employer issues a Leaving Certificate or relevant part of Form P9 showing total earnings and PAYE deducted up to the date of leaving. Confirm the exact document required with TRA.")
print(f"C15 Fixed paye_extended_018: {p['answer_sw'][:100]}")

# ============================================================
# CORRECTION 16: Casual worker 30-day -> one month
# ============================================================
p = by_id["tier1a_paye_017_20260603"]
sw(p, "zaidi ya siku 30 mfululizo", "zaidi ya mwezi mmoja mfululizo")
en(p, "more than 30 consecutive days", "more than one month continuously")
print(f"C16 Fixed paye_017")

# ============================================================
# CORRECTION 17: Non-resident director rate 20%
# ============================================================
p = by_id["tier1a_paye_018_20260603"]
sw(p,
   "kiwango ni asilimia 15 kwa wakazi. Thibitisha",
   "kiwango ni asilimia 15 kwa wakazi na asilimia 20 kwa wasio wakazi. Thibitisha")
en(p,
   "the rate is 15% for residents. Confirm",
   "the rate is 15% for residents and 20% for non-residents. Confirm")
print(f"C17 Fixed paye_018: {p['answer_sw']}")

# ============================================================
# CORRECTION 18: BRELA share transfer wording
# ============================================================
p = by_id["tier1a_brela_chg_004_20260603"]
sw(p,
   "uhamishaji hauna nguvu ya kisheria",
   "uhamishaji unaweza kukosa nguvu ya kisheria dhidi ya watu wa tatu")
en(p,
   "transfer has no legal force",
   "transfer may lack legal effect against third parties")
print(f"C18 Fixed brela_chg_004")

# ============================================================
# CORRECTION 19: BRELA Form 23 disclaimer
# ============================================================
p = by_id["tier1a_brela_chg_001_20260603"]
sw(p,
   "kuwasilisha Fomu 23 (Taarifa ya Mabadiliko ya Wakurugenzi) kwa BRELA ndani ya siku 14 baada ya mabadiliko,",
   "kuwasilisha Fomu 23 (Taarifa ya Mabadiliko ya Wakurugenzi) kwa BRELA ndani ya siku 14 baada ya mabadiliko (thibitisha nambari ya sasa ya fomu kupitia mfumo wa BRELA Online (brela.go.tz) kwani nambari za fomu zinaweza kubadilika),")
en(p,
   "filing Form 23 (Notice of Change of Directors) with BRELA within 14 days of the change,",
   "filing Form 23 (Notice of Change of Directors) with BRELA within 14 days of the change (confirm current form number via BRELA Online at brela.go.tz as form numbers may have changed),")
print(f"C19 Fixed brela_chg_001")

# ============================================================
# CORRECTION 20: TFDA/TMDA -> TMDA
# ============================================================
for pid in ["tier1a_biz_lic_004_20260603", "tier1a_biz_lic_009_20260603"]:
    p = by_id[pid]
    orig_sw, orig_en = p["answer_sw"], p["answer_en"]
    p["answer_sw"] = p["answer_sw"].replace("TFDA/TMDA", "TMDA").replace("TFDA", "TMDA")
    p["answer_en"] = p["answer_en"].replace("TFDA/TMDA", "TMDA").replace("TFDA", "TMDA")
    if p["answer_sw"] != orig_sw or p["answer_en"] != orig_en:
        changed.add(pid)
        print(f"C20 Fixed {pid}")
    else:
        print(f"C20 {pid}: no TFDA references found — no change needed")

# ============================================================
# CORRECTION 21: Loss carry forward — Finance Act 2024 note
# ============================================================
p = by_id["tier1a_income_tax_007_20260603"]
sw(p,
   "Hasara haiwezi kubebwa nyuma (carry back) nchini Tanzania.",
   ("Tangu Finance Act 2024: baada ya miaka 4 mfululizo ya hasara, asilimia 60 tu ya mapato ya mwaka wa 5 "
    "inaweza kutumika kupunguza hasara zilizobebwa mbele (ilipungua kutoka asilimia 70). "
    "Hasara haiwezi kubebwa nyuma (carry back) nchini Tanzania."))
en(p,
   "Losses cannot be carried back in Tanzania.",
   ("Since Finance Act 2024: after 4 consecutive loss years, only 60% of year 5 income can be offset "
    "against carried forward losses (reduced from 70%). "
    "Losses cannot be carried back in Tanzania."))
print(f"C21 Fixed income_tax_007")

# ============================================================
# CORRECTION 22: Public sector disclaimer — Treasury or PSC
# ============================================================
p = by_id["tier1a_gn605a_007_20260603"]
sw(p,
   "Thibitisha na Hazina.",
   "Thibitisha na Hazina au PSC kwa hati rasmi inayothibitisha kiwango na tarehe ya kuanza.")
en(p,
   "Confirm with the Treasury.",
   "Confirm with the Treasury or PSC for the official instrument confirming the rate and effective date.")
print(f"C22 Fixed gn605a_007")

# ============================================================
# CORRECTION 23: Tax clearance time caveat
# ============================================================
p = by_id["tier1a_compliance_004_20260603"]
sw(p,
   "ndani ya siku 3–7 za kazi.",
   "ndani ya siku 3–7 za kazi, ingawa inaweza kuchukua muda mrefu zaidi kulingana na mzigo wa kazi wa TRA — omba mapema iwezekanavyo.")
en(p,
   "within 3–7 working days.",
   "within 3–7 working days, though this may take longer depending on TRA workload — apply as early as possible.")
print(f"C23 Fixed compliance_004")

# ============================================================
# CORRECTION 24: PRN expiry softening
# Replace full parenthetical to avoid nested parens
# ============================================================
p = by_id["tier1a_compliance_002_20260603"]
sw(p,
   "(kawaida siku chache)",
   "(thibitisha muda halisi na TRA)")
en(p,
   "(usually a few days)",
   "(confirm current duration with TRA)")
flags.append("NOTE C24: replaced full parenthetical '(kawaida siku chache)' rather than inner text only — avoids nested parens per do.md literal instruction")
print(f"C24 Fixed compliance_002")

# ============================================================
# CORRECTION 25: First-time offender — no-guarantee disclaimer at end
# ============================================================
p = by_id["tier1a_compliance_009_20260603"]
sw(p,
   "Kujitokeza mapema na kwa hiari ni sababu kubwa ya mafanikio ya ombi.",
   "Kujitokeza mapema na kwa hiari ni sababu kubwa ya mafanikio ya ombi. Hii si haki ya kisheria bali ni uamuzi wa hiari wa Kamishna — hakuna uhakika wa kupata msamaha.")
en(p,
   "Coming forward early and voluntarily is a major factor in a successful application.",
   "Coming forward early and voluntarily is a major factor in a successful application. This is not a legal right but a discretionary decision of the Commissioner — there is no guarantee of a waiver.")
print(f"C25 Fixed compliance_009")

# ============================================================
# SAVE
# ============================================================
with open(path, "w", encoding="utf-8") as out:
    for pair in pairs:
        out.write(json.dumps(pair, ensure_ascii=False) + "\n")

print(f"\nRun 3 complete. Total pairs changed: {len(changed)}")
print("Changed IDs:", sorted(changed))
if flags:
    print("\nNOTES/FLAGS:")
    for f in flags:
        print(" -", f)
