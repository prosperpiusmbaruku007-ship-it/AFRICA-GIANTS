#!/usr/bin/env python3
"""
TEMP-FILE-CLEANER companion script.
Usage:
  python scripts/clean_temp_files.py --scan    # List temp files without deleting
  python scripts/clean_temp_files.py --clean   # Delete them
Exit: 0 = clean (no temp files), 1 = temp files found
"""
import os, glob, argparse, json, sys

CLEANED_DIR = "datasets/tier1a/cleaned_pairs"

# Flag files whose name contains these substrings (case-insensitive).
# Does NOT flag batch_NNN_eval.jsonl or batch_NNN_adversarial.jsonl.
TEMP_INDICATORS = ("_test", "_temp", "test_", "temp_", "_draft")


def is_temp_file(basename):
    """Flag only known temp patterns, not all non-matching files."""
    lower = basename.lower()
    return any(lower.startswith(t) or t in lower for t in TEMP_INDICATORS)


def count_pairs(filepath):
    """Count valid JSON objects (pairs), not raw line count."""
    count = 0
    try:
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        json.loads(line)
                        count += 1
                    except json.JSONDecodeError:
                        pass
    except Exception:
        pass
    return count


def find_temp_files():
    all_files = glob.glob(os.path.join(CLEANED_DIR, "*.jsonl"))
    temp_files = []
    for f in all_files:
        basename = os.path.basename(f)
        if is_temp_file(basename):
            pairs = count_pairs(f)
            temp_files.append({"path": f, "name": basename, "pairs": pairs})
    return temp_files


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scan", action="store_true",
                        help="List temp files without deleting")
    parser.add_argument("--clean", action="store_true",
                        help="Delete temp files")
    args = parser.parse_args()

    if not args.scan and not args.clean:
        parser.print_help()
        sys.exit(1)

    temp_files = find_temp_files()

    if not temp_files:
        print("CLEAN — only valid batch files present.")
        sys.exit(0)

    print(f"TEMP FILES FOUND: {len(temp_files)} file(s)")
    total_pairs = 0
    for f in temp_files:
        print(f"  {f['name']}: {f['pairs']} valid pairs")
        total_pairs += f['pairs']
    print(f"Total pairs inflating corpus count: {total_pairs}")

    if args.clean:
        for f in temp_files:
            os.remove(f['path'])
            print(f"Deleted: {f['name']}")
        print(f"Removed {total_pairs} temp pairs from count.")
        sys.exit(0)
    else:
        print("Run with --clean to delete these files.")
        sys.exit(1)


if __name__ == "__main__":
    main()
