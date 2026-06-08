# FLAGGED-PAIR-ROUTER

## Purpose
Route flagged pairs from verify_pairs.py into the correct
subfolder so the founder can review them efficiently.
Prevents flagged pairs from blocking the batch — they are
quarantined for review while clean pairs continue.

## When to activate
Immediately after verify_pairs.py runs and produces any flag.
Also activate when check_locked_facts.py produces any flag.

## Folder structure (created in Step 1)
datasets/tier1a/flagged/consensus_blocked/   — 2+ models agree: must fix
datasets/tier1a/flagged/needs_human_review/  — 1 model flags: founder decides
datasets/tier1a/flagged/resolved/            — fixed pairs, audit trail

## Step 1: After verify_pairs.py flags a pair
Read scripts/verification_log.jsonl for the latest entry.
Extract flagged pair IDs from the flags list.

## Step 2: Copy flagged pairs to correct folder
```python
import json, os, shutil

# Read latest verification log entry
log_entries = []
with open("scripts/verification_log.jsonl", encoding="utf-8") as f:
    for line in f:
        log_entries.append(json.loads(line))

latest = log_entries[-1]
batch_file = latest["file"]

# Load all pairs from the batch
pairs = {}
with open(batch_file, encoding="utf-8") as f:
    for line in f:
        p = json.loads(line)
        pairs[p["id"]] = p

# Route flags to correct folder
for flag in latest.get("flags", []):
    pair_id = (flag.get("pair_id") or
               flag.get("raw","").split("|")[0].replace("FLAG:","").strip())
    is_consensus = not flag.get("needs_human", False)

    folder = (
        "datasets/tier1a/flagged/consensus_blocked"
        if is_consensus else
        "datasets/tier1a/flagged/needs_human_review"
    )
    os.makedirs(folder, exist_ok=True)

    if pair_id in pairs:
        out_path = os.path.join(folder, f"{pair_id}.json")
        with open(out_path, "w", encoding="utf-8") as out:
            json.dump({
                "pair": pairs[pair_id],
                "flags": [f for f in latest["flags"]
                          if pair_id in str(f)],
                "models_flagging": list(set(
                    f.get("model","unknown")
                    for f in latest["flags"]
                    if pair_id in str(f)
                )),
                "routed_at": latest["timestamp"]
            }, out, ensure_ascii=False, indent=2)
        print(f"Routed {pair_id} -> {folder}")

print("Routing complete.")
```

## Step 3: Report to founder
After routing tell the founder:
- How many pairs in consensus_blocked (must fix before commit)
- How many pairs in needs_human_review (review at convenience)
- How many pairs are clean and ready to commit

## Step 4: After founder approves or fixes
Move resolved pairs to datasets/tier1a/flagged/resolved/
Then commit only the clean pairs.

## Pass case
verify_pairs.py finds 0 flags → skip this skill entirely
→ commit the batch directly

## Fail case
verify_pairs.py finds 3 consensus flags →
Route all 3 to consensus_blocked/
Tell founder: "3 pairs blocked, fix before committing.
47 pairs are clean and ready."
Fix the 3 pairs using locked_facts.json
Move fixed pairs to resolved/
Re-run verify_pairs.py on fixed pairs
If clean → commit all 50 pairs

## Integration
Called automatically after every verify_pairs.py run
that produces flags. Updates verification_log.jsonl
with routing decisions. Works with PAIR-VALIDATOR
which also checks before committing.
