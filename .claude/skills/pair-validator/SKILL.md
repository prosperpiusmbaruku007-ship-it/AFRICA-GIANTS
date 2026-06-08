# PAIR-VALIDATOR

## Run this sequence after every 50-pair save

### Step 1: Schema validation
```bash
python scripts/validate_dataset.py
```
Expected: "0 errors"
If errors > 0: fix before continuing

### Step 2: Source check
```bash
python scripts/check_sources.py --file [batch_file]
```
Expected: "CLEAN"

### Step 3: Fact check
```bash
python scripts/check_locked_facts.py --file [batch_file]
```
Expected: "CLEAN"

### Step 4: Dedup check
```bash
python scripts/build_question_index.py --check-only
```
Expected: "CLEAN — 0 duplicates"

### Step 5: Only if all 4 pass
Continue writing next 50 pairs.
If any step fails: fix that batch before continuing.

## Valid field values (quick reference)
| Field | Valid Values |
|-------|-------------|
| domain | tier1a, tier1b, tier1c |
| register | business_market, formal, rural_conversational |
| pair_type | standard, adversarial, disambiguation, procedural |
| decay_risk | stable, annual, event_triggered |
| eval_set | true, false (boolean not string) |
| effective_date | YYYY-MM-DD format only |
| verified_by | founder_self_review, tra_consultant, pending_founder_review |

## Before git commit
Run all 4 checks across ALL files not just the current batch.
Only commit if all 4 return exit code 0.
