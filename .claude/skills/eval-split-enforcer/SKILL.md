# EVAL-SPLIT-ENFORCER

## Purpose
Before generating SFT files verify that no eval_set: true
pair appears in train_sft.jsonl and no training pair
appears in the eval set. Contamination inflates accuracy
scores silently and invalidates the gate results.

## When to activate
Before every run of generate_sft.py
Before every accuracy gate run
Before any Kaggle training session

## Why this matters
If eval pairs leak into training the model memorises the
answers. The accuracy gate then tests what the model
memorised not what it learned. A 90% gate result with
contamination is meaningless.

## Step 1: Check all cleaned pairs for eval_set field
python scripts/check_eval_split.py \
  --cleaned-dir datasets/tier1a/cleaned_pairs/

## Step 2: Check generated SFT files if they exist
python scripts/check_eval_split.py \
  --sft-train datasets/tier1a/sft/train_sft.jsonl

## Step 3: If contamination found
Do NOT proceed with training.
List the contaminated instructions shown (first 60 chars).
Remove them from train_sft.jsonl or re-run generate_sft.py
after fixing the eval_set flag on the source pair.

## Technical note
SFT files use instruction/input/output/system format — they
have no id field. Contamination is detected by comparing the
instruction text against eval question text (question_sw),
NOT by ID matching. This is intentional and correct.

## Pass case
0 eval questions found in train_sft.jsonl.
Output: CLEAN — eval split verified. Safe to train.

## Fail case
Found 3 eval questions in train_sft.jsonl.
Output: CONTAMINATION DETECTED — remove before training.
contaminated: line 47: jinsi ya kusajili kampuni ya limited...

## Integration
Called by HF-UPLOADER before generate_sft.py
Called by TRAINING-PREFLIGHT before Kaggle session
Exits with code 1 if contamination found
