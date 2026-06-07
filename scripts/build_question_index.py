#!/usr/bin/env python3
"""
DEDUP-GUARD index builder and checker.
Usage:
  python scripts/build_question_index.py           # Build index
  python scripts/build_question_index.py --check   # Build + check all files
"""
import json, sys, argparse, os, glob

INDEX_FILE = "datasets/tier1a/raw_sources/existing_questions.txt"

def build_index():
    questions = set()
    ids = set()
    files_checked = []

    patterns = [
        "datasets/tier1a/cleaned_pairs/*.jsonl",
        "datasets/tier1a/raw_sources/raw_pairs_*.jsonl"
    ]

    for pattern in patterns:
        for filepath in glob.glob(pattern):
            files_checked.append(filepath)
            with open(filepath, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        p = json.loads(line)
                        q_sw = p.get("question_sw", "").lower().strip()
                        q_en = p.get("question_en", "").lower().strip()
                        if q_sw:
                            questions.add(q_sw)
                        if q_en:
                            questions.add(q_en)
                        if p.get("id"):
                            ids.add(p["id"])
                    except json.JSONDecodeError:
                        continue

    os.makedirs(os.path.dirname(INDEX_FILE), exist_ok=True)
    with open(INDEX_FILE, "w", encoding="utf-8") as out:
        for q in sorted(questions):
            out.write(q + "\n")

    print(f"Index built: {len(questions)} unique questions, {len(ids)} unique IDs")
    print(f"Files checked: {len(files_checked)}")
    return questions, ids

def check_duplicates():
    """Full cross-file deduplication check."""
    seen_questions = set()
    seen_ids = set()
    dupes_q = []
    dupes_id = []
    total = 0

    patterns = [
        "datasets/tier1a/cleaned_pairs/*.jsonl",
        "datasets/tier1a/raw_sources/raw_pairs_*.jsonl"
    ]

    for pattern in patterns:
        for filepath in sorted(glob.glob(pattern)):
            with open(filepath, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        p = json.loads(line)
                        total += 1
                        q_key = p.get("question_sw", "").lower().strip()
                        pid = p.get("id", "")

                        if q_key in seen_questions:
                            dupes_q.append({"id": pid, "question": q_key[:80]})
                        seen_questions.add(q_key)

                        if pid and pid in seen_ids:
                            dupes_id.append(pid)
                        if pid:
                            seen_ids.add(pid)
                    except json.JSONDecodeError:
                        continue

    print(f"\nTotal pairs: {total}")
    if dupes_q:
        print(f"DUPLICATE QUESTIONS: {len(dupes_q)}")
        for d in dupes_q[:10]:
            print(f"  [{d['id']}] {d['question']}")
    if dupes_id:
        print(f"DUPLICATE IDs: {len(dupes_id)}")
        for d in dupes_id[:10]:
            print(f"  {d}")

    if not dupes_q and not dupes_id:
        print("CLEAN — 0 duplicates found.")
        return True
    return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="Build index and run full dedup check")
    parser.add_argument("--check-only", action="store_true",
                        help="Run full dedup check only")
    args = parser.parse_args()

    if args.check_only:
        clean = check_duplicates()
        sys.exit(0 if clean else 1)
    else:
        build_index()
        if args.check:
            clean = check_duplicates()
            sys.exit(0 if clean else 1)

if __name__ == "__main__":
    main()
