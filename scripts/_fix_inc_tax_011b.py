import json, sys
sys.stdout.reconfigure(encoding="utf-8")

path = "datasets/tier1a/raw_sources/raw_pairs_batch_002.jsonl"
pairs = []
with open(path, encoding="utf-8") as f:
    for line in f:
        pairs.append(json.loads(line))

by_id = {p["id"]: p for p in pairs}
p = by_id["tier1a_inc_tax_deep_011_20260603"]

# Fix SW: "0.3% ya mapato ghafi" to "asilimia 1 ya mapato ghafi"
old = "0.3% ya mapato ghafi"
new = "asilimia 1 ya mapato ghafi"
if old in p["answer_sw"]:
    p["answer_sw"] = p["answer_sw"].replace(old, new)
    print(f"SW fixed: rate updated to asilimia 1")
else:
    print(f"SW: '{old}' not found")

print(f"SW after: {p['answer_sw'][:200]}")
print(f"EN check: {'1% of gross turnover' in p['answer_en']} (EN already correct)")

with open(path, "w", encoding="utf-8") as out:
    for pair in pairs:
        out.write(json.dumps(pair, ensure_ascii=False) + "\n")
print("Saved.")
