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

CLEANED_DIR = "datasets/tier1a/cleaned_pairs"
SFT_DIR = "datasets/tier1a/sft"

def load_all_pairs():
    all_pairs = []
    for filepath in sorted(glob.glob(f"{CLEANED_DIR}/*.jsonl")):
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
