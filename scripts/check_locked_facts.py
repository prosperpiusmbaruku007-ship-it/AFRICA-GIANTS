#!/usr/bin/env python3
"""
FACT-GUARDIAN validation script.
Usage: python scripts/check_locked_facts.py --file path/to/batch.jsonl
Exit code: 0 = clean, 1 = violations found

Assertions are defined in scripts/locked_facts.json (wrong_patterns per fact key).
Last updated: 2026-06-16 — added from primary source verification:
  paye_all_bands_sequence    — 0%/8%/20%/25%/30% bands (PWC Jan 2026)
  paye_nonresident_flat_rate — 15% flat for non-residents (PWC Jan 2026)
  paye_personal_relief       — CORRECTED: no personal relief exists in Tanzania
  brela_annual_return_fee    — TZS 22,000 filing; TZS 2,500/month late penalty
  wcf_new_employer_registration — 30 days from first hire
  wcf_disease_reporting_deadline — disease 7 days; death/claim 12 months
  gn605a_increment_range     — TZS 20,000–195,000 increment range (PKF Oct 2025)
"""
import json, sys, re, argparse, os
from datetime import datetime

def load_locked_facts(facts_path="scripts/locked_facts.json"):
    if not os.path.exists(facts_path):
        print(f"ERROR: locked_facts.json not found at {facts_path}")
        sys.exit(1)
    with open(facts_path, encoding="utf-8") as f:
        data = json.load(f)
    # Return only fact entries (not _meta or _unresolved_items)
    return {k: v for k, v in data.items()
            if not k.startswith("_") and "wrong_patterns" in v}

def check_pair(pair, facts):
    flags = []
    text = (
        pair.get("answer_sw", "") + " " +
        pair.get("answer_en", "")
    ).lower()
    pid = pair.get("id", "unknown")

    for fact_key, fact in facts.items():
        for pattern in fact.get("wrong_patterns", []):
            try:
                if re.search(pattern.lower(), text):
                    flags.append({
                        "pair_id": pid,
                        "fact_key": fact_key,
                        "wrong_pattern": pattern,
                        "correct": fact.get("fact", ""),
                        "source": fact.get("primary_source", "")
                    })
            except re.error:
                # If regex fails, do simple string match
                if pattern.lower() in text:
                    flags.append({
                        "pair_id": pid,
                        "fact_key": fact_key,
                        "wrong_pattern": pattern,
                        "correct": fact.get("fact", ""),
                        "source": fact.get("primary_source", "")
                    })
    return flags

def main():
    parser = argparse.ArgumentParser(
        description="Validate training pairs against locked regulatory facts"
    )
    parser.add_argument("--file", required=True,
                        help="Path to JSONL file to validate")
    parser.add_argument("--facts", default="scripts/locked_facts.json",
                        help="Path to locked_facts.json")
    parser.add_argument("--log", default="scripts/fact_check_log.txt",
                        help="Path to log file")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"ERROR: File not found: {args.file}")
        sys.exit(1)

    facts = load_locked_facts(args.facts)
    total = 0
    flagged_pairs = 0
    all_flags = []

    with open(args.file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                pair = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"JSON ERROR on line {total+1}: {e}")
                continue
            total += 1
            flags = check_pair(pair, facts)
            if flags:
                flagged_pairs += 1
                all_flags.extend(flags)
                for flag in flags:
                    print(f"FLAG [{flag['pair_id']}] {flag['fact_key']}")
                    print(f"  Wrong pattern: '{flag['wrong_pattern']}'")
                    print(f"  Correct fact: {flag['correct'][:100]}")
                    print(f"  Source: {flag['source']}")
                    print()

    # Write log
    timestamp = datetime.now().isoformat()
    with open(args.log, "a", encoding="utf-8") as log:
        log.write(f"\n[{timestamp}] Checked {args.file}\n")
        log.write(f"Total: {total} | Flagged: {flagged_pairs}\n")
        for flag in all_flags:
            log.write(f"  FLAG [{flag['pair_id']}] {flag['fact_key']}: "
                      f"{flag['wrong_pattern']}\n")

    print(f"Checked {total} pairs. {flagged_pairs} pairs flagged.")

    if flagged_pairs > 0:
        print(f"\nFix all flagged pairs before committing.")
        print(f"Log written to: {args.log}")
        sys.exit(1)
    else:
        print("CLEAN — no locked fact violations found.")
        sys.exit(0)

if __name__ == "__main__":
    main()
