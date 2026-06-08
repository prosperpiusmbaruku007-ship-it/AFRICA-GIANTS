import json

path = "datasets/tier1a/raw_sources/raw_pairs_batch_002.jsonl"
pairs = []
with open(path, encoding="utf-8") as f:
    for line in f:
        pairs.append(json.loads(line))

by_id = {p["id"]: p for p in pairs}

p = by_id["tier1a_inc_tax_deep_011_20260603"]
print("CURRENT SW:", p["answer_sw"])
print()
print("CURRENT EN:", p["answer_en"])
print()

# SW: text uses "0.3% ya mapato ghafi" (numeric, not spelled out)
if "0.3% ya mapato ghafi" in p["answer_sw"]:
    p["answer_sw"] = p["answer_sw"].replace("0.3% ya mapato ghafi", "asilimia 1 ya mapato ghafi")
    print("SW fixed: 0.3% → asilimia 1")
elif "asilimia 0.3 ya mapato ghafi" in p["answer_sw"]:
    p["answer_sw"] = p["answer_sw"].replace("asilimia 0.3 ya mapato ghafi", "asilimia 1 ya mapato ghafi")
    print("SW fixed: asilimia 0.3 → asilimia 1")
else:
    print("SW: rate string not found — check manually")

# Check if EN fix already applied (ran in run2 script)
if "1% of gross turnover" in p["answer_en"]:
    print("EN: already shows 1% — OK")
elif "0.3% of gross turnover" in p["answer_en"]:
    p["answer_en"] = p["answer_en"].replace("minimum tax of 0.3% of gross turnover", "minimum tax of 1% of gross turnover")
    print("EN fixed")

# Check if Finance Act note already added
if "1 Julai 2025" in p["answer_sw"]:
    print("SW: Finance Act note already present")
if "1 July 2025" in p["answer_en"]:
    print("EN: Finance Act note already present")

print()
print("AFTER SW:", p["answer_sw"])
print("AFTER EN:", p["answer_en"])

with open(path, "w", encoding="utf-8") as out:
    for pair in pairs:
        out.write(json.dumps(pair, ensure_ascii=False) + "\n")
print("\nSaved.")
