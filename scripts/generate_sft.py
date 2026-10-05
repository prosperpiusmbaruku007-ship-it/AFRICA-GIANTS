#!/usr/bin/env python3
"""Generate SFT training files from all cleaned pair batches."""
import json, random, os, glob

SYSTEM_PROMPT = (
    "Wewe ni msaidizi wa AI wa biashara za Tanzania. "
    "Unajibu maswali kuhusu sheria za biashara, kodi, "
    "usajili wa kampuni kwa Kiswahili na Kiingereza. "
    "You are a Tanzanian business AI assistant answering "
    "questions about regulations, tax, company registration, "
    "and financial rules in Swahili and English."
)

# ⛔ BOTH DIRECTORIES, AND THIS IS NOT OPTIONAL. On 2026-10-05 the 8 SFT-shaped files moved out
# of cleaned_pairs/ into sft_shaped_pairs/, because cleaned_pairs/ asserts the 18-field contract
# (R3) and those rows never carried it. They are still 2,705 of the 4,410 non-eval pairs this
# generator loads -- 61% -- so reading only cleaned_pairs/ would silently shrink the next
# retrain's data by more than half while the script still printed a cheerful "Loaded N pairs".
# fmt_pair() already handled both shapes; only the directory list changed.
# Verified across the move: train_sft.jsonl and val_sft.jsonl are byte-identical before/after.
CLEANED_DIRS = ["datasets/tier1a/cleaned_pairs", "datasets/tier1a/sft_shaped_pairs"]
SFT_DIR = "datasets/tier1a/sft"

def load_all_pairs():
    all_pairs = []
    # sorted over the UNION, so ordering (and therefore the seeded shuffle) is stable and
    # independent of which directory a file lives in -- that is what makes the byte-identity
    # check above meaningful rather than coincidental.
    paths = sorted(p for d in CLEANED_DIRS for p in glob.glob(f"{d}/*.jsonl"))
    assert paths, f"no pair files found under {CLEANED_DIRS} -- refusing to build an empty SFT set"
    for filepath in paths:
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    p = json.loads(line)
                    # Skip eval-set pairs from training
                    if not p.get("eval_set", False):
                        all_pairs.append(p)
    return all_pairs

def fmt_pair(p):
    # Support schema format (question_sw/answer_sw) and SFT format (instruction/output)
    q = p.get("question_sw", "") or p.get("question_en", "") or p.get("instruction", "")
    a = p.get("answer_sw", "") or p.get("answer_en", "") or p.get("output", "")
    return {
        "instruction": q,
        "input": "",
        "output": a,
        "system": SYSTEM_PROMPT
    }

def main():
    all_pairs = load_all_pairs()
    print(f"Loaded {len(all_pairs)} non-eval pairs")

    formatted = [fmt_pair(p) for p in all_pairs]
    random.seed(42)
    random.shuffle(formatted)

    split = int(len(formatted) * 0.9)
    train = formatted[:split]
    val = formatted[split:]
    print(f"Train: {len(train)} | Val: {len(val)}")

    os.makedirs(SFT_DIR, exist_ok=True)

    train_path = os.path.join(SFT_DIR, "train_sft.jsonl")
    val_path = os.path.join(SFT_DIR, "val_sft.jsonl")

    with open(train_path, "w", encoding="utf-8") as f:
        for p in train:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    with open(val_path, "w", encoding="utf-8") as f:
        for p in val:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    print(f"Saved: {train_path}")
    print(f"Saved: {val_path}")

if __name__ == "__main__":
    main()
