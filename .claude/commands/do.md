#Read this file completely then execute every instruction below exactly as written.
first commit to wher we reached and update progress.md context is 90% full

Do not wait for Gemini to recover.
The two deterministic checks both passed all 80 pairs.
Gemini was clean on every batch it responded to.
This is sufficient to proceed.

Move to next subdomain: sdl_compliance adversarial pairs.
Target: 50 pairs.

Every SDL pair MUST:
- State full name: Skills Development Levy (not Service
  Delivery Levy, not disability leave)
- State rate: 3.5% of gross payroll
- State threshold: employers with 10 or more employees
- State paid by employer only — not deducted from employee
- At least 20 pairs must directly contradict the
  wrong answer the model gives ("disability leave")

Write first 50 sdl pairs and append to:
datasets/tier1a/raw_sources/raw_pairs_batch_003.jsonl

After 50 pairs run:
python scripts/check_locked_facts.py \
  --file datasets/tier1a/raw_sources/raw_pairs_batch_003.jsonl
python scripts/check_sources.py \
  --file datasets/tier1a/raw_sources/raw_pairs_batch_003.jsonl

Report results then STOP and wait.
Skip verify_pairs.py for now — re-run on full batch
once Gemini recovers.