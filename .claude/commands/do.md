#Read this file completely then execute every instruction below exactly as written.
Save the following Python script exactly as-is to:
scripts/plan_next_batch.py
Use utf-8 encoding.

```python
#!/usr/bin/env python3
"""
BATCH-PLANNER — generate next batch plan from gate results and coverage.
Usage: python scripts/plan_next_batch.py
"""
import json, os, glob

GATE_RESULTS_FILE = "gate_001_results.json"
CLEANED_DIR = "datasets/tier1a/cleaned_pairs"
TARGET_PAIRS = 3000

ADVERSARIAL_THRESHOLD = 60   # Below this: build adversarial pairs
IMPROVEMENT_THRESHOLD = 75   # Below this: build more standard pairs

FIXED_REFUSAL_PAIRS = 30

def count_existing_pairs():
    total = 0
    subdomain_counts = {}
    for filepath in glob.glob(f"{CLEANED_DIR}/*.jsonl"):
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    p = json.loads(line)
                    sub = p.get("subdomain", "unknown")
                    subdomain_counts[sub] = subdomain_counts.get(sub, 0) + 1
                    total += 1
                except json.JSONDecodeError:
                    pass
    return total, subdomain_counts

def load_gate_results():
    if not os.path.exists(GATE_RESULTS_FILE):
        print(f"No gate results found at {GATE_RESULTS_FILE}")
        return {}
    with open(GATE_RESULTS_FILE, encoding="utf-8") as f:
        return json.load(f)

def main():
    total, subdomain_counts = count_existing_pairs()
    gate = load_gate_results()

    print(f"\n{'='*60}")
    print(f"BATCH PLANNER — AFRICA-GIANTS")
    print(f"{'='*60}")
    print(f"Current corpus: {total:,} pairs")
    print(f"Target: {TARGET_PAIRS:,} pairs")
    print(f"Remaining: {TARGET_PAIRS - total:,} pairs")
    print(f"Batches needed (300/batch): {(TARGET_PAIRS - total) // 300 + 1}")

    print(f"\n--- ACCURACY GATE STATUS ---")
    if gate:
        for subdomain, score in sorted(gate.items(),
                                        key=lambda x: x[1]):
            if isinstance(score, (int, float)):
                pct = score * 100 if score <= 1 else score
                status = (
                    "❌ ADVERSARIAL NEEDED" if pct < ADVERSARIAL_THRESHOLD
                    else "⚠️  MORE PAIRS NEEDED" if pct < IMPROVEMENT_THRESHOLD
                    else "✅ PASSING"
                )
                print(f"  {subdomain:<30} {pct:.1f}%  {status}")

    print(f"\n--- RECOMMENDED NEXT BATCH (300 pairs) ---")
    print(f"  80 pairs: gn487a (adversarial — base model says 'residence permit')")
    print(f"  50 pairs: sdl_compliance (adversarial — base model says 'disability leave')")
    print(f"  40 pairs: vat_registration (base model invents 5% and 10% reduced rates)")
    print(f"  30 pairs: out_of_corpus refusal pairs")
    print(f"  50 pairs: nssf_contributions edge cases + NSSF deep")
    print(f"  50 pairs: new subdomain — efd_compliance_deep or wcf_details")

    print(f"\n--- PAIR TYPE ALLOCATION ---")
    print(f"  adversarial pairs (explicitly contradict base model error): 40%")
    print(f"  standard pairs (normal Q&A): 40%")
    print(f"  disambiguation pairs (this vs that): 10%")
    print(f"  procedural pairs (step-by-step): 10%")

if __name__ == "__main__":
    main()
```

Then test it:
python scripts/plan_next_batch.py

Expected: shows current corpus size, remaining to 3000 target,
and recommended batch_003 subdomain allocation.

Show full output then STOP. Wait for next instruction.