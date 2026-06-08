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
shows 3.5%. Run:
  python scripts/update_locked_fact.py \
    --fact-key sdl_rate --new-value "4%" --old-value "3.5%" \
    --effective-date 2026-07-01 --source [url]

## Example — locked_facts.json entry after update
If SDL changed from 3.5% to 4% on 2026-07-01:

Before:
  "fact": "3.5%",
  "wrong_patterns": ["asilimia 4 ya", "4% of"],
  "effective_date": "2025-07-01"

After (update_locked_fact.py handles this automatically):
  "fact": "4%",
  "wrong_patterns": ["asilimia 4 ya", "4% of",
                     "asilimia 3.5 ya", "3.5% of"],
  "effective_date": "2026-07-01"

## Integration
update_locked_fact.py calls check_locked_facts.py automatically.
Calls HF-UPLOADER after fixing pairs and regenerating SFT.
Updates PROGRESS.md with change log entry.
Should run every July when Finance Act is published.
