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
    flags.append(f"NOT FOUND {p['id']}.SW: [{old[:40]}]")
    return False

def en(p, old, new):
    if old in p["answer_en"]:
        p["answer_en"] = p["answer_en"].replace(old, new)
        changed.add(p["id"])
        return True
    flags.append(f"NOT FOUND {p['id']}.EN: [{old[:40]}]")
    return False

# === paye_deep_009: threshold calc — uses ÷ (U+00F7) and × (U+00D7) ===
p = by_id["tier1a_paye_deep_009_20260603"]
# Read the actual strings from the pair to find exact characters
print(f"paye_deep_009 SW snippet: {p['answer_sw'][50:150]}")
print(f"paye_deep_009 EN snippet: {p['answer_en'][50:150]}")

# SW: "kundi la 9% (la pili)" → "kundi la 8% (la pili)"
sw(p, "kundi la 9% (la pili)", "kundi la 8% (la pili)")
# Division sign check
if "÷ 9%" in p["answer_sw"]:
    sw(p, "TZS 26,000 ÷ 9% = TZS 288,889", "TZS 26,000 ÷ 8% = TZS 325,000")
    sw(p, "TZS 270,000 + TZS 288,889 = TZS 558,889/mwezi", "TZS 270,000 + TZS 325,000 = TZS 595,000/mwezi")
sw(p, "karibu TZS 559,000", "karibu TZS 595,000")

en(p, "9% band (second band)", "8% band (second band)")
if "÷ 9%" in p["answer_en"]:
    en(p, "TZS 26,000 ÷ 9% = TZS 288,889", "TZS 26,000 ÷ 8% = TZS 325,000")
    en(p, "TZS 270,000 + TZS 288,889 = TZS 558,889/month", "TZS 270,000 + TZS 325,000 = TZS 595,000/month")
en(p, "approximately TZS 559,000", "approximately TZS 595,000")
print(f"paye_deep_009 done")

# === paye_deep_010: uses × (U+00D7) ===
p = by_id["tier1a_paye_deep_010_20260603"]
print(f"paye_deep_010 SW snippet: {p['answer_sw'][50:160]}")
if "× 9%" in p["answer_sw"]:
    sw(p, "250,000 × 9% = TZS 22,500", "250,000 × 8% = TZS 20,000")
else:
    print("  paye_deep_010: band2 calc already fixed or uses different char")
# Totals
sw(p, "Jumla = TZS 58,500", "Jumla = TZS 56,000")
sw(p, "PAYE ya mfanyakazi = TZS 32,500", "PAYE ya mfanyakazi = TZS 30,000")
if "× 9%" in p["answer_en"]:
    en(p, "250,000 × 9% = TZS 22,500", "250,000 × 8% = TZS 20,000")
en(p, "Total = TZS 58,500", "Total = TZS 56,000")
en(p, "Employee PAYE = TZS 32,500", "Employee PAYE = TZS 30,000")
flags.append("FLAG paye_deep_010: do.md says final PAYE TZS 28,000 but 56,000-26,000=30,000. Applied TZS 30,000. Confirm with founder.")
print(f"paye_deep_010 done")

# === paye_deep_016: uses × (U+00D7) ===
p = by_id["tier1a_paye_deep_016_20260603"]
print(f"paye_deep_016 SW snippet: {p['answer_sw'][50:160]}")
if "× 9%" in p["answer_sw"]:
    sw(p, "250,000 × 9% = TZS 22,500", "250,000 × 8% = TZS 20,000")
else:
    print("  paye_deep_016: band2 calc already fixed or uses different char")
sw(p, "Jumla = TZS 105,500", "Jumla = TZS 103,000")
sw(p, "PAYE ya Aprili = TZS 79,500", "PAYE ya Aprili = TZS 77,000")
if "× 9%" in p["answer_en"]:
    en(p, "250,000 × 9% = TZS 22,500", "250,000 × 8% = TZS 20,000")
en(p, "Total = TZS 105,500", "Total = TZS 103,000")
en(p, "April PAYE = TZS 79,500", "April PAYE = TZS 77,000")
print(f"paye_deep_016 done")

# === paye_deep_022: 3-employee multi-calc (uses × no spaces: 250,000×9%=22,500) ===
p = by_id["tier1a_paye_deep_022_20260603"]
print(f"paye_deep_022 SW snippet: {p['answer_sw'][80:200]}")
# Employee 2 band 2 (no-space format like "250,000×9%=22,500")
# Check what multiplication char is used
for char in ["×", "x", "*"]:
    test = f"250,000{char}9%=22,500"
    if test in p["answer_sw"]:
        print(f"  Found Employee2 Band2 with char U+{ord(char):04X}: {test}")
        sw(p, f"250,000{char}9%=22,500", f"250,000{char}8%=20,000")
        en(p, f"250,000{char}9%=22,500", f"250,000{char}8%=20,000")
        break
else:
    # Try with spaces
    for char in ["×", "x", "*"]:
        test = f"250,000 {char} 9% = 22,500"
        if test in p["answer_sw"]:
            print(f"  Found with spaces, char U+{ord(char):04X}")
            sw(p, f"250,000 {char} 9% = 22,500", f"250,000 {char} 8% = 20,000")
            en(p, f"250,000 {char} 9% = 22,500", f"250,000 {char} 8% = 20,000")
            break
    else:
        flags.append("NOT FOUND paye_deep_022: Employee2 Band2 calc string not located")

sw(p, "Jumla=48,500", "Jumla=46,000")
sw(p, "PAYE=TZS 22,500. (3)", "PAYE=TZS 20,000. (3)")
sw(p, "TZS 0 + TZS 22,500 + TZS 254,500 = TZS 277,000", "TZS 0 + TZS 20,000 + TZS 254,500 = TZS 274,500")
en(p, "Total=48,500", "Total=46,000")
en(p, "PAYE=TZS 22,500. (3)", "PAYE=TZS 20,000. (3)")
en(p, "TZS 0 + TZS 22,500 + TZS 254,500 = TZS 277,000", "TZS 0 + TZS 20,000 + TZS 254,500 = TZS 274,500")
print(f"paye_deep_022 done")

# === SAVE ===
with open(path, "w", encoding="utf-8") as out:
    for p in pairs:
        out.write(json.dumps(p, ensure_ascii=False) + "\n")

print(f"\nTotal pairs changed this run: {len(changed)}")
print("Changed:", sorted(changed))
if flags:
    print("\nFLAGS:")
    for f in flags:
        print(" -", f)
else:
    print("No flags.")
