#Read this file completely then execute every instruction below exactly as written.
# Complete ALL tasks in sequence. Do NOT stop between tasks.
# All fixes from session 5 code-review are already applied in this file.

---

## TASK 1: Save .claude/skills/git-push-guard/SKILL.md

# GIT-PUSH-GUARD

## Purpose
Scan all staged files (and optionally all modified files) for API key
patterns before any git commit or push. Reject if found.

## When to activate
Before every git add and git commit touching any file.
Especially before commits to scripts/ and PROGRESS.md.

## Known patterns that leaked this project
- OpenRouter keys: sk-or-
- Groq keys: gsk_
- Anthropic keys: sk-ant-
- OpenAI keys: sk-proj-
- HuggingFace tokens: hf_
- Gemini keys: AQ.
- GitHub tokens: github_pat_ or ghp_
- Cerebras keys: csk-

## Step 1: Scan staged files before commit
python scripts/scan_for_keys.py

## Step 2: If any key found
- Do NOT commit
- Show which file and which line
- Remove the key from the file
- Replace with: os.environ.get("KEY_NAME", "")
- Re-run scan until clean

## Step 3: Only if scan returns clean
Proceed with git commit and push.

## Pass case
No key patterns found in staged files.
Output: CLEAN — no API keys detected. Safe to commit.

## Fail case
sk-or-v1abc found in scripts/verify_pairs.py line 45.
Output: BLOCKED — API key detected. Remove before committing.

---

## TASK 2: Save scripts/scan_for_keys.py

```python
#!/usr/bin/env python3
"""
GIT-PUSH-GUARD — scan staged and/or modified files for API key patterns.
Usage:
  python scripts/scan_for_keys.py                 # Scan staged files only
  python scripts/scan_for_keys.py --all-modified  # Scan staged + unstaged
Exit: 0 = clean, 1 = key patterns found
"""
import subprocess, re, sys, os, argparse

KEY_PATTERNS = [
    (r'sk-or-[A-Za-z0-9_-]{20,}', 'OpenRouter key'),
    (r'gsk_[A-Za-z0-9]{20,}', 'Groq key'),
    (r'sk-ant-[A-Za-z0-9_-]{20,}', 'Anthropic key'),
    (r'sk-proj-[A-Za-z0-9_-]{20,}', 'OpenAI key'),
    (r'hf_[A-Za-z0-9]{20,}', 'HuggingFace token'),
    (r'AQ\.[A-Za-z0-9_-]{20,}', 'Gemini key'),
    (r'github_pat_[A-Za-z0-9_]{20,}', 'GitHub token'),
    (r'ghp_[A-Za-z0-9]{20,}', 'GitHub token'),
    (r'csk-[A-Za-z0-9]{20,}', 'Cerebras key'),
]

# Only skip lines where the matched key IS the env var name
# e.g. os.environ.get("sk-ant-your") — the key is a variable name, not a value
# Do NOT skip lines where os.environ.get also has a real key as the default arg
SAFE_LINE_PATTERNS = [
    r'YOUR_KEY_HERE',
    r'your-key-here',
    r'sk-ant-your',
    r'sk-or-your',
    r'gsk_your',
    r'hf_your',
    r'#\s*(example|Example|your key|placeholder)',
    r'sk-or-v1-\.\.\.',   # ellipsis placeholder
]


def get_staged_files():
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only'],
        capture_output=True, text=True
    )
    return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]


def get_modified_files():
    result = subprocess.run(
        ['git', 'diff', '--name-only'],
        capture_output=True, text=True
    )
    return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]


def is_safe_line(line):
    """Return True only if the line is clearly a placeholder/comment — not a real key."""
    for pat in SAFE_LINE_PATTERNS:
        if re.search(pat, line):
            return True
    return False


def scan_file(filepath):
    flags = []
    if not os.path.exists(filepath):
        return flags
    try:
        with open(filepath, encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                if is_safe_line(line):
                    continue
                for pattern, key_type in KEY_PATTERNS:
                    if re.search(pattern, line):
                        flags.append({
                            'file': filepath,
                            'line': line_num,
                            'type': key_type,
                            'content': line.strip()[:80]
                        })
    except Exception:
        pass
    return flags


def main():
    parser = argparse.ArgumentParser(
        description="Scan for embedded API keys before committing"
    )
    parser.add_argument('--all-modified', action='store_true',
                        help='Also scan unstaged modified files')
    args = parser.parse_args()

    staged = get_staged_files()
    files_to_scan = list(staged)

    if args.all_modified:
        for f in get_modified_files():
            if f not in files_to_scan:
                files_to_scan.append(f)

    if not files_to_scan:
        print('No files to scan (no staged or modified files found).')
        sys.exit(0)

    label = "staged + modified" if args.all_modified else "staged"
    print(f'Scanning {len(files_to_scan)} {label} files...')
    all_flags = []

    for filepath in files_to_scan:
        flags = scan_file(filepath)
        all_flags.extend(flags)

    if all_flags:
        print(f'\nBLOCKED — {len(all_flags)} API key pattern(s) found:')
        for f in all_flags:
            print(f"  {f['file']}:{f['line']} [{f['type']}]")
            print(f"  {f['content']}")
        print('\nRemove keys before committing.')
        print('Use os.environ.get("KEY_NAME", "") instead.')
        sys.exit(1)
    else:
        print(f'CLEAN — no API keys detected in {len(files_to_scan)} files.')
        sys.exit(0)


if __name__ == '__main__':
    main()
```

---

## TASK 3: Save .claude/skills/locked-facts-updater/SKILL.md

# LOCKED-FACTS-UPDATER

## Purpose
When a new Finance Act or Government Notice is published,
update locked_facts.json with the correct new value AND
automatically add the old value as a wrong_pattern so
FACT-GUARDIAN catches any pairs still using the old rate.

## When to activate
- When the founder says "Finance Act [year] published"
- When a new GN number is mentioned
- When any regulatory figure is confirmed changed
- Every July when Tanzania publishes the annual Finance Act
- When a TRA page scrape returns a value different from locked_facts.json

## Why this is CRITICAL
Finance Act 2025 changed SDL from 4% to 3.5%.
Finance Act 2025 changed minimum tax from 0.5% to 1%.
Finance Act 2025 introduced 3%/6% VAT withholding.
GN 605A changed minimum wages effective January 2026.

In each case pairs written before the change encoded the
OLD value. Without this skill those pairs contaminate the
training corpus for months before anyone notices.

## Step 1: Identify what changed
When a new regulation is announced ask:
- What is the old value?
- What is the new value?
- What is the effective date?
- What is the primary source URL?

## Step 2: Run the companion script
```bash
python scripts/update_locked_fact.py \
  --fact-key sdl_rate \
  --new-value "3.5%" \
  --old-value "4%" \
  --effective-date 2025-07-01 \
  --source "https://tra.go.tz/page/skills-development-levy-sdl"
```
The script updates locked_facts.json and immediately scans all
cleaned pairs for pairs still using the old value.

## Step 3: Fix flagged pairs
For each flagged pair update the answer to use the new value.
Add a note: "Kuanzia [date]" / "Effective [date]"
Where old rate was correct historically keep it but add
context: "Kabla ya [date] ilikuwa X, sasa ni Y"

## Step 4: Regenerate SFT files
python scripts/generate_sft.py
Then upload and retrain on Kaggle.

## Step 5: Update PROGRESS.md
Add entry: "Finance Act [year] — [N] facts updated,
[N] pairs corrected, retrain triggered"

## Annual Finance Act check (every July)
Tanzania publishes Finance Act every June/July.
In July each year use WebFetch to check:
  tra.go.tz/page/pay-as-you-earn-paye
  tra.go.tz/page/value-added-tax
  tra.go.tz/page/skills-development-levy-sdl
  tra.go.tz/page/corporation-tax
Compare each key figure against locked_facts.json.
Run update_locked_fact.py for any discrepancy found.

## Pass case
No changes found — locked_facts.json matches primary sources.
Output: CURRENT — all facts match primary sources.

## Fail case
SDL rate on TRA page says 4% but locked_facts.json says 3.5%.
Output: UPDATE REQUIRED — sdl_rate: TRA shows 4%, locked
shows 3.5%. Run: python scripts/update_locked_fact.py
  --fact-key sdl_rate --new-value "4%" --old-value "3.5%"
  --effective-date 2026-07-01 --source [url]

## Integration
update_locked_fact.py calls check_locked_facts.py automatically.
Calls HF-UPLOADER after fixing pairs and regenerating SFT.
Updates PROGRESS.md with change log entry.
Should run every July when Finance Act is published.

---

## TASK 4: Save scripts/update_locked_fact.py

```python
#!/usr/bin/env python3
"""
LOCKED-FACTS-UPDATER companion script.
Updates a fact in locked_facts.json and scans all cleaned pairs
for pairs still using the old (now-wrong) value.

Usage:
  python scripts/update_locked_fact.py \
    --fact-key sdl_rate \
    --new-value "3.5%" \
    --old-value "4%" \
    --effective-date 2025-07-01 \
    --source "https://tra.go.tz/page/skills-development-levy-sdl"
  
  python scripts/update_locked_fact.py --fact-key sdl_rate --dry-run
Exit: 0 = clean, 1 = pairs found using old value
"""
import json, os, argparse, subprocess, sys, glob

FACTS_FILE = "scripts/locked_facts.json"
CLEANED_DIR = "datasets/tier1a/cleaned_pairs"


def main():
    parser = argparse.ArgumentParser(
        description="Update a locked fact and scan pairs for old value"
    )
    parser.add_argument("--fact-key", required=True,
                        help="Key in locked_facts.json to update")
    parser.add_argument("--new-value", required=True,
                        help="New correct value")
    parser.add_argument("--old-value", required=True,
                        help="Old (now wrong) value — added to wrong_patterns")
    parser.add_argument("--effective-date", required=True,
                        help="Effective date of change (YYYY-MM-DD)")
    parser.add_argument("--source", required=True,
                        help="Primary source URL confirming new value")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would change without writing")
    args = parser.parse_args()

    if not os.path.exists(FACTS_FILE):
        print(f"ERROR: {FACTS_FILE} not found")
        sys.exit(1)

    with open(FACTS_FILE, encoding="utf-8") as f:
        facts = json.load(f)

    if args.fact_key not in facts:
        available = [k for k in facts if not k.startswith("_")]
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

    print(f"\nFact key:  {args.fact_key}")
    print(f"  Old value: {old_fact_value}")
    print(f"  New value: {args.new_value}")
    print(f"  Adding to wrong_patterns: '{new_wrong}'")
    print(f"  Effective date: {args.effective_date}")
    print(f"  Source: {args.source}")

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
    print(f"\nScanning {len(pair_files)} batch file(s) for old value...")
    violations = 0
    for pf in pair_files:
        result = subprocess.run(
            ["python", "scripts/check_locked_facts.py", "--file", pf],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"  FLAGS in {os.path.basename(pf)}:")
            print(result.stdout)
            violations += 1

    if violations == 0:
        print("CLEAN — no pairs use the old value.")
    else:
        print(f"\n{violations} batch file(s) have pairs using the old value.")
        print("Fix flagged pairs, then run generate_sft.py to regenerate.")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

---

## TASK 5: Save .claude/skills/temp-file-cleaner/SKILL.md

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

## Patterns that are flagged as temp
Any file in cleaned_pairs/ that starts with _ or matches
_test*, _temp*, test_*, temp_*, *_draft*, and does NOT
match the valid pattern batch_NNN_cleaned.jsonl.
Files named batch_NNN_eval.jsonl or batch_NNN_adversarial.jsonl
are explicitly NOT flagged — only temp/test prefixes.

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

---

## TASK 6: Save scripts/clean_temp_files.py

```python
#!/usr/bin/env python3
"""
TEMP-FILE-CLEANER companion script.
Usage:
  python scripts/clean_temp_files.py --scan    # List temp files only
  python scripts/clean_temp_files.py --clean   # Delete them
Exit: 0 = clean (no temp files), 1 = temp files found
"""
import os, glob, argparse, re, json, sys

CLEANED_DIR = "datasets/tier1a/cleaned_pairs"
VALID_PATTERN = re.compile(r'^batch_\d{3}_cleaned\.jsonl$')

# Only flag files with these prefixes/substrings — not everything else
TEMP_INDICATORS = ("_test", "_temp", "test_", "temp_", "_draft")


def is_temp_file(basename):
    """Flag only known temp patterns, not all non-matching files."""
    lower = basename.lower()
    return any(lower.startswith(t) or t in lower for t in TEMP_INDICATORS)


def count_pairs(filepath):
    """Count valid JSON lines (pairs), not raw line count."""
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
        print(f"  {f['name']}: {f['pairs']} pairs")
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
```

---

## TASK 7: Save .claude/skills/eval-split-enforcer/SKILL.md

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
List the contaminated instructions (first 60 chars shown).
Remove matching pairs from train_sft.jsonl.
Re-run check until clean.

## Pass case
0 eval questions found in train_sft.jsonl.
Output: CLEAN — eval split verified. Safe to train.

## Fail case
Found 3 eval questions in train_sft.jsonl.
Output: CONTAMINATION DETECTED — remove before training.

## Integration
Called by HF-UPLOADER before generate_sft.py
Called by TRAINING-PREFLIGHT before Kaggle session
Exits with code 1 if contamination found

---

## TASK 8: Save scripts/check_eval_split.py

```python
#!/usr/bin/env python3
"""
EVAL-SPLIT-ENFORCER companion script.
Detects eval pair contamination in SFT training files.
Compares by instruction text (question_sw/question_en) because
SFT files use instruction/input/output/system format, not id fields.

Usage:
  python scripts/check_eval_split.py
  python scripts/check_eval_split.py --cleaned-dir datasets/tier1a/cleaned_pairs/
  python scripts/check_eval_split.py --sft-train datasets/tier1a/sft/train_sft.jsonl
Exit: 0 = clean, 1 = contamination found
"""
import json, os, glob, argparse, sys


def get_eval_questions(cleaned_dir):
    """Return set of question texts from eval_set: true pairs."""
    eval_questions = set()
    for filepath in glob.glob(os.path.join(cleaned_dir, "*.jsonl")):
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    p = json.loads(line)
                    if p.get("eval_set") is True:
                        q_sw = p.get("question_sw", "").strip().lower()
                        q_en = p.get("question_en", "").strip().lower()
                        if q_sw:
                            eval_questions.add(q_sw)
                        if q_en:
                            eval_questions.add(q_en)
                except json.JSONDecodeError:
                    pass
    return eval_questions


def get_train_questions(cleaned_dir):
    """Return set of question texts from training (eval_set: false) pairs."""
    train_questions = set()
    for filepath in glob.glob(os.path.join(cleaned_dir, "*.jsonl")):
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    p = json.loads(line)
                    if p.get("eval_set") is not True:
                        q_sw = p.get("question_sw", "").strip().lower()
                        if q_sw:
                            train_questions.add(q_sw)
                except json.JSONDecodeError:
                    pass
    return train_questions


def check_sft_for_eval_contamination(sft_file, eval_questions):
    """
    Check SFT file by comparing instruction text against eval question text.
    SFT files use instruction/input/output/system — no id field.
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
    eval_questions = get_eval_questions(args.cleaned_dir)
    train_questions = get_train_questions(args.cleaned_dir)

    print(f"Training pairs: {len(train_questions)}")
    print(f"Eval pairs (eval_set: true): {len(eval_questions)}")

    if not eval_questions:
        print("NOTE: No eval_set: true pairs found — "
              "eval set may not be populated yet.")

    contaminated = check_sft_for_eval_contamination(
        args.sft_train, eval_questions
    )

    if contaminated:
        print(f"\nCONTAMINATION DETECTED: {len(contaminated)} eval question(s) "
              f"found in {args.sft_train}")
        for entry in contaminated:
            print(f"  CONTAMINATED: {entry}")
        print("Remove these pairs from train_sft.jsonl before training.")
        sys.exit(1)
    else:
        print("CLEAN — eval split verified. Safe to train.")
        sys.exit(0)


if __name__ == "__main__":
    main()
```

---

## TASK 9: Update CLAUDE.md — add mandatory pre-task checks to Section 9

Find the block ending with:
  Checkpoint name encodes the score: e.g. `tier1a_acc87_ref72_2026-09-01/`

Insert immediately after it (before the --- separator):

**Mandatory pre-task checks (automated scripts — must exit 0):**
- Before `plan_next_batch.py`: `python scripts/clean_temp_files.py --scan`
- Before `generate_sft.py`: `python scripts/check_eval_split.py`
- Before every `git commit`: `python scripts/scan_for_keys.py`

If any check fails: fix the issue before proceeding. Do not bypass.

---

## TASK 10: Test all new scripts

Run these in order:
python scripts/scan_for_keys.py --all-modified
python scripts/clean_temp_files.py --scan
python scripts/check_eval_split.py --cleaned-dir datasets/tier1a/cleaned_pairs/

Show full output for all three.

---

## TASK 11: Commit everything

git add .claude/skills/git-push-guard/
git add .claude/skills/locked-facts-updater/
git add .claude/skills/temp-file-cleaner/
git add .claude/skills/eval-split-enforcer/
git add scripts/scan_for_keys.py
git add scripts/update_locked_fact.py
git add scripts/clean_temp_files.py
git add scripts/check_eval_split.py
git add CLAUDE.md
git add .claude/commands/do.md
git commit -m "add 4 new skills + companion scripts; fix do.md reliability issues"
git push origin main
Show commit hash then STOP.
