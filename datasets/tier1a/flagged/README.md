# FLAGGED PAIRS

## Folders

### needs_human_review/
Pairs flagged by only ONE AI model during verify_pairs.py
Single model flag — may be a false positive.
Founder reviews and decides: fix or approve as-is.
Check this folder after every batch.

### consensus_blocked/
Pairs flagged by TWO OR MORE AI models during verify_pairs.py
These are definite errors — must be fixed before committing.
Claude Code fixes automatically using locked_facts.json.
Do not commit any pair from this folder unfixed.

### resolved/
Pairs that were flagged and then fixed.
Kept for audit trail — do not delete.

## How pairs get here
verify_pairs.py writes flagged pair IDs to:
  scripts/verification_log.jsonl

Claude Code reads verification_log.jsonl and copies
flagged pairs to the correct subfolder automatically
after every 50-pair save.

## Founder review process
1. Open needs_human_review/ after each batch
2. Read each flagged pair JSON file
3. Decide: fix or approve
4. If fix needed: correct the pair and move to resolved/
5. If approved as-is: move directly to resolved/
6. Tell Claude Code which pairs were approved or fixed
