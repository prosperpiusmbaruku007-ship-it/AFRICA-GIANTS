"""
Validates all JSONL pairs in datasets/*/cleaned_pairs/ against:
  1. schema/pair_schema.json — all 18 required fields present + enum values valid
  2. sources/whitelist.json — primary_source_url domain is whitelisted

Exit code 0: all pairs valid (or no pairs found).
Exit code 1: one or more pairs failed validation.

Usage: python scripts/validate_dataset.py
"""
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent.parent
SCHEMA_PATH = ROOT / "schema" / "pair_schema.json"
WHITELIST_PATH = ROOT / "sources" / "whitelist.json"
DATASETS_ROOT = ROOT / "datasets"


def load_schema():
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_whitelist():
    with open(WHITELIST_PATH, encoding="utf-8") as f:
        entries = json.load(f)
    return {urlparse(e["url"]).netloc for e in entries}


def validate_pair(pair, required_fields, allowed_values, whitelisted_domains, filepath, line_num):
    errors = []

    for field in required_fields:
        if field not in pair:
            errors.append(f"Missing field: {field}")
        elif pair[field] == "" or pair[field] is None:
            errors.append(f"Empty field: {field}")

    for field, allowed in allowed_values.items():
        if field in pair and pair[field] not in allowed:
            errors.append(f"Invalid value for {field}: '{pair[field]}' not in {allowed}")

    if "primary_source_url" in pair:
        domain = urlparse(pair["primary_source_url"]).netloc
        if domain not in whitelisted_domains:
            errors.append(f"Source domain not whitelisted: '{domain}' — add to sources/whitelist.json")

    if errors:
        print(f"  [{filepath.name}:{line_num}] FAILED:")
        for e in errors:
            print(f"    - {e}")
    return errors


def main():
    schema = load_schema()
    required = schema["required"]
    allowed = schema["allowed_values"]
    whitelisted = load_whitelist()

    cleaned_pair_dirs = sorted(DATASETS_ROOT.glob("*/cleaned_pairs"))

    total_pairs = 0
    total_errors = 0

    for cleaned_dir in cleaned_pair_dirs:
        jsonl_files = sorted(cleaned_dir.glob("*.jsonl"))
        for jsonl_file in jsonl_files:
            with open(jsonl_file, encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        pair = json.loads(line)
                    except json.JSONDecodeError as e:
                        print(f"  [{jsonl_file.name}:{line_num}] JSON parse error: {e}")
                        total_errors += 1
                        continue
                    total_pairs += 1
                    errors = validate_pair(pair, required, allowed, whitelisted, jsonl_file, line_num)
                    total_errors += len(errors)

    print(f"\nValidation complete: {total_pairs} pairs found, {total_errors} errors")

    if total_errors > 0:
        print("VALIDATION FAILED — fix errors before moving pairs to cleaned_pairs/")
        sys.exit(1)
    else:
        print("VALIDATION PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
