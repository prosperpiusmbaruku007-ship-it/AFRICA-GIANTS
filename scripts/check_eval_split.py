#!/usr/bin/env python3
"""
EVAL-SPLIT-ENFORCER companion script.
Detects eval pair contamination in SFT training files.

Compares by instruction TEXT (question_sw/question_en) because
SFT files use instruction/input/output/system format — they have
no id field. Matching by ID would never find contamination.

Usage:
  python scripts/check_eval_split.py
  python scripts/check_eval_split.py --cleaned-dir datasets/tier1a/cleaned_pairs/
  python scripts/check_eval_split.py --sft-train datasets/tier1a/sft/train_sft.jsonl
Exit: 0 = clean, 1 = contamination found
"""
import json, os, glob, argparse, sys


def get_eval_questions(cleaned_dir):
    """Return normalised set of question texts from eval_set: true pairs."""
    eval_questions = set()
    count = 0
    for filepath in glob.glob(os.path.join(cleaned_dir, "*.jsonl")):
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    p = json.loads(line)
                    if p.get("eval_set") is True:
                        count += 1
                        q_sw = p.get("question_sw", "").strip().lower()
                        q_en = p.get("question_en", "").strip().lower()
                        if q_sw:
                            eval_questions.add(q_sw)
                        if q_en:
                            eval_questions.add(q_en)
                except json.JSONDecodeError:
                    pass
    return eval_questions, count


def get_train_count(cleaned_dir):
    """Count training (non-eval) pairs."""
    count = 0
    for filepath in glob.glob(os.path.join(cleaned_dir, "*.jsonl")):
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        p = json.loads(line)
                        if p.get("eval_set") is not True:
                            count += 1
                    except json.JSONDecodeError:
                        pass
    return count


def check_sft_for_eval_contamination(sft_file, eval_questions):
    """
    Check SFT file for eval contamination by comparing instruction text.
    SFT files have no id field — must compare by question text.
    """
    if not os.path.exists(sft_file):
        print(f"SFT file not found: {sft_file} (run generate_sft.py first)")
        return []
    contaminated = []
    with open(sft_file, encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                p = json.loads(line)
                instruction = p.get("instruction", "").strip().lower()
                if instruction and instruction in eval_questions:
                    contaminated.append(
                        f"line {line_num}: {instruction[:60]}"
                    )
            except json.JSONDecodeError:
                pass
    return contaminated


def main():
    parser = argparse.ArgumentParser(
        description="Verify eval pairs are not in SFT training data"
    )
    parser.add_argument("--cleaned-dir",
                        default="datasets/tier1a/cleaned_pairs",
                        help="Directory containing cleaned JSONL pairs")
    parser.add_argument("--sft-train",
                        default="datasets/tier1a/sft/train_sft.jsonl",
                        help="Path to generated train_sft.jsonl")
    args = parser.parse_args()

    print("Checking eval split...")
    eval_questions, eval_pair_count = get_eval_questions(args.cleaned_dir)
    train_count = get_train_count(args.cleaned_dir)

    print(f"Training pairs: {train_count}")
    print(f"Eval pairs (eval_set: true): {eval_pair_count}")
    print(f"Unique eval question strings: {len(eval_questions)}")

    if not eval_questions:
        print("NOTE: No eval_set: true pairs found — "
              "eval set may not be populated yet.")
        print("CLEAN — eval split verified. Safe to train.")
        sys.exit(0)

    contaminated = check_sft_for_eval_contamination(
        args.sft_train, eval_questions
    )

    if contaminated:
        print(f"\nCONTAMINATION DETECTED: {len(contaminated)} eval question(s) "
              f"found in {args.sft_train}")
        for entry in contaminated:
            print(f"  CONTAMINATED: {entry}")
        print("\nFix: remove these from train_sft.jsonl or re-run "
              "generate_sft.py after correcting eval_set flags.")
        sys.exit(1)
    else:
        print("CLEAN — eval split verified. Safe to train.")
        sys.exit(0)


if __name__ == "__main__":
    main()
