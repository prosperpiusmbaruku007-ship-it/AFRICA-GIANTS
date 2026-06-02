"""Validate raw_pairs_batch_001.jsonl in raw_sources against schema + whitelist."""
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent.parent
with open(ROOT / "schema" / "pair_schema.json", encoding="utf-8") as f:
    schema = json.load(f)
with open(ROOT / "sources" / "whitelist.json", encoding="utf-8") as f:
    whitelist = json.load(f)

required = schema["required"]
allowed = schema["allowed_values"]
domains = {urlparse(e["url"]).netloc for e in whitelist}

errors = []
count = 0
eval_count = 0
adv_count = 0

src = ROOT / "datasets" / "tier1a" / "raw_sources" / "raw_pairs_batch_001.jsonl"
with open(src, encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        p = json.loads(line.strip())
        count += 1
        if p.get("eval_set") is True:
            eval_count += 1
        if p.get("pair_type") == "adversarial":
            adv_count += 1
        for field in required:
            if field not in p or p[field] == "" or p[field] is None:
                errors.append(f"Line {i} [{p['id']}]: missing/empty {field}")
        for field, vals in allowed.items():
            if field in p and p[field] not in vals:
                errors.append(f"Line {i} [{p['id']}]: {field}={p[field]!r} not in {vals}")
        dom = urlparse(p.get("primary_source_url", "")).netloc
        if dom not in domains:
            errors.append(f"Line {i} [{p['id']}]: domain not whitelisted: {dom}")

print(f"Total pairs: {count}")
print(f"eval_set=true: {eval_count}")
print(f"adversarial: {adv_count}")
print(f"Errors: {len(errors)}")
for e in errors[:30]:
    print(" ", e)
if not errors:
    print("VALIDATION PASSED")
else:
    import sys
    sys.exit(1)
