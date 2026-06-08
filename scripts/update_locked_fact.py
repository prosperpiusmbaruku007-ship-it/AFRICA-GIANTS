#!/usr/bin/env python3
"""
LOCKED-FACTS-UPDATER companion script.
Updates a fact in locked_facts.json, adds the old value to wrong_patterns,
then scans all cleaned pairs for pairs still using the old value.

Usage:
  python scripts/update_locked_fact.py \
    --fact-key sdl_rate \
    --new-value "3.5%" \
    --old-value "4%" \
    --effective-date 2025-07-01 \
    --source "https://tra.go.tz/page/skills-development-levy-sdl"

  python scripts/update_locked_fact.py --fact-key sdl_rate --list-keys
Exit: 0 = updated and clean, 1 = pairs found using old value
"""
import json, os, argparse, subprocess, sys, glob

FACTS_FILE = "scripts/locked_facts.json"
CLEANED_DIR = "datasets/tier1a/cleaned_pairs"


def main():
    parser = argparse.ArgumentParser(
        description="Update a locked fact and scan pairs for old value"
    )
    parser.add_argument("--fact-key",
                        help="Key in locked_facts.json to update")
    parser.add_argument("--new-value",
                        help="New correct value")
    parser.add_argument("--old-value",
                        help="Old (now wrong) value — added to wrong_patterns")
    parser.add_argument("--effective-date",
                        help="Effective date of change (YYYY-MM-DD)")
    parser.add_argument("--source",
                        help="Primary source URL confirming new value")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would change without writing")
    parser.add_argument("--list-keys", action="store_true",
                        help="List all available fact keys then exit")
    args = parser.parse_args()

    if not os.path.exists(FACTS_FILE):
        print(f"ERROR: {FACTS_FILE} not found")
        sys.exit(1)

    with open(FACTS_FILE, encoding="utf-8") as f:
        facts = json.load(f)

    if args.list_keys:
        keys = [k for k in facts if not k.startswith("_")]
        print(f"Available fact keys ({len(keys)}):")
        for k in sorted(keys):
            v = facts[k].get("fact", "?")[:60]
            print(f"  {k:<35} current: {v}")
        sys.exit(0)

    required = ["fact_key", "new_value", "old_value", "effective_date", "source"]
    missing = [r for r in required if not getattr(args, r, None)]
    if missing:
        print(f"ERROR: Missing required args: {missing}")
        print("Run with --list-keys to see available fact keys.")
        parser.print_help()
        sys.exit(1)

    if args.fact_key not in facts:
        available = sorted(k for k in facts if not k.startswith("_"))
        print(f"ERROR: fact key '{args.fact_key}' not found in locked_facts.json")
        print(f"Available keys: {available}")
        sys.exit(1)

    fact = facts[args.fact_key]
    old_fact_value = fact.get("fact", "")
    old_patterns = fact.get("wrong_patterns", [])

    new_wrong = args.old_value
    if new_wrong not in old_patterns:
        updated_patterns = old_patterns + [new_wrong]
    else:
        updated_patterns = old_patterns
        print(f"NOTE: '{new_wrong}' already in wrong_patterns — no duplicate added")

    print(f"\nFact key:  {args.fact_key}")
    print(f"  Old value:            {old_fact_value}")
    print(f"  New value:            {args.new_value}")
    print(f"  Adding wrong_pattern: '{new_wrong}'")
    print(f"  Effective date:       {args.effective_date}")
    print(f"  Source:               {args.source}")

    if args.dry_run:
        print("\nDRY RUN — no changes written.")
        return

    facts[args.fact_key]["fact"] = args.new_value
    facts[args.fact_key]["wrong_patterns"] = updated_patterns
    facts[args.fact_key]["effective_date"] = args.effective_date
    facts[args.fact_key]["primary_source"] = args.source

    with open(FACTS_FILE, "w", encoding="utf-8") as f:
        json.dump(facts, f, ensure_ascii=False, indent=2)
    print(f"\nUpdated {FACTS_FILE}")

    # Scan all cleaned pairs for old value
    pair_files = sorted(glob.glob(f"{CLEANED_DIR}/*.jsonl"))
    if not pair_files:
        print("No cleaned pair files found to scan.")
        sys.exit(0)

    print(f"\nScanning {len(pair_files)} batch file(s) for old value...")
    violations = 0
    for pf in pair_files:
        result = subprocess.run(
            ["python", "scripts/check_locked_facts.py", "--file", pf],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"  FLAGS in {os.path.basename(pf)}:")
            print(result.stdout.strip())
            violations += 1
        else:
            print(f"  {os.path.basename(pf)}: clean")

    if violations == 0:
        print("\nCLEAN — no pairs use the old value.")
    else:
        print(f"\n{violations} batch file(s) have pairs using the old value.")
        print("Fix flagged pairs, then run: python scripts/generate_sft.py")
        sys.exit(1)


if __name__ == "__main__":
    main()
