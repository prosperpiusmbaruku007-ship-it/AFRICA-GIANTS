# TEMP-FILE-CLEANER

## Purpose
Delete or exclude test files and temp files from
cleaned_pairs/ before any corpus count or SFT generation.
Prevents inflated pair counts from polluting batch planning.

## When to activate
Before running plan_next_batch.py
Before running generate_sft.py
Before running any script that counts pairs in cleaned_pairs/

## Why this happened
_test3.jsonl and _test10.jsonl in cleaned_pairs/ caused
plan_next_batch.py to report 313 pairs instead of 300.
Batch planning decisions were made on wrong numbers.

## Step 1: Scan for temp files
python scripts/clean_temp_files.py --scan

## Step 2: If temp files found
Review the list before deleting.
Never silently delete without confirming the list first.

## Step 3: Delete confirmed temp files
python scripts/clean_temp_files.py --clean

## What counts as a temp file
Files in cleaned_pairs/ whose name starts with _ or contains
_test, _temp, test_, temp_, _draft (case-insensitive).
Valid files that are NOT flagged:
  batch_NNN_cleaned.jsonl  — standard cleaned batch
  batch_NNN_eval.jsonl     — eval set batch (NOT flagged)
  batch_NNN_adversarial.jsonl — adversarial batch (NOT flagged)

## Pass case
No temp files found.
Output: CLEAN — only valid batch files present.

## Fail case
Found: _test3.jsonl (3 pairs), _test10.jsonl (10 pairs)
Output: TEMP FILES FOUND — remove before counting corpus.
Removed 13 pairs from count. True corpus: 300 pairs.

## Integration
Called by BATCH-PLANNER before plan_next_batch.py
Called by HF-UPLOADER before generate_sft.py
Logs removals to PROGRESS.md
