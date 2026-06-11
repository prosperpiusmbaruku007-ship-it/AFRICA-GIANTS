#Read this file completely then execute every instruction below exactly as written.
Run all tasks simultaneously where possible.
Execute all 4 task groups in parallel.

============================================================
TASK GROUP 1: CROSS-AI REVIEW — unreviewed pairs
Run in background, do not wait for completion before starting other tasks.
============================================================

TASK 1A: Complete batch_004 cross-AI review (pairs 41-280 unreviewed)
nohup python scripts/verify_pairs.py \
  --file datasets/tier1a/raw_sources/raw_pairs_batch_004.jsonl \
  --batch-size 20 \
  > scripts/verify_bg_batch004_full.txt 2>&1 &
echo "batch_004 full review PID: $!"

TASK 1B: batch_003 cross-AI review (not yet reviewed)
nohup python scripts/verify_pairs.py \
  --file datasets/tier1a/raw_sources/raw_pairs_batch_003.jsonl \
  --batch-size 20 \
  > scripts/verify_bg_batch003.txt 2>&1 &
echo "batch_003 review PID: $!"

Monitor every 10 minutes:
while true; do
  echo "=== $(date) ==="
  echo "--- batch_003 ---"
  tail -3 scripts/verify_bg_batch003.txt 2>/dev/null
  echo "--- batch_004 full ---"
  tail -3 scripts/verify_bg_batch004_full.txt 2>/dev/null
  sleep 600
done &
echo "Monitor PID: $!"

============================================================
TASK GROUP 2: TARGETED SUBDOMAIN SCANS — all 5 batches
Run these sequentially after starting Task Group 1 background jobs.
============================================================

SCAN 1: compliance_costs — ALL pairs across all batches
Find all pairs with subdomain containing "compliance" in:
  raw_pairs_batch_003.jsonl
  raw_pairs_batch_004.jsonl
  raw_pairs_batch_005.jsonl
  raw_pairs_batch_006.jsonl

For every compliance_costs pair found apply ALL of these:
  FIX 7: Remove "siku chache" / "few days" PRN expiry claims
    Replace with: "muda wa uhalali wa PRN unaonekana kwenye bili — angalia kabla ya kulipa"
  FIX 8: Remove "siku 3-7 za kazi" / "3-7 working days" tax clearance claims
    Replace with: "inategemea ukaguzi wa TRA kupitia IDRAS — angalia hali yako kwenye mfumo"
  FIX 9: Delete any sentence saying tender failures trigger TRA audit
  FIX 10: Change first-time offender waiver from legal rule to:
    "historia nzuri ya uzingatiaji inaweza kuzingatiwa na TRA
    lakini hakuna uhakika wa kisheria"

Print count of compliance_costs pairs found and fixed per batch.

SCAN 2: work_permits — Class D references
Search ALL batch files for "Class D" OR "Darasa D" OR "darasa D"
For each match found:
  Change "Class D" to "Class C"
  Change "Darasa D" to "Darasa C"
  Add to answer: "Watafiti pia wanahitaji COSTECH Research Clearance
  (ada USD 300 kwa mtu) kwa utafiti wa kisayansi.
  Darasa C haihitaji kibali cha kazi kutoka Wizara ya Kazi."
  English: "Researchers also need COSTECH Research Clearance
  (fee USD 300 per person) for scientific research.
  Class C does not require a Work Permit from the Ministry of Labour."
Source: Tanzania Embassy Washington DC + immigration.go.tz

SCAN 3: BRELA fees — understated amounts
Search ALL batch files for BRELA fee amounts below TZS 50,000
Patterns to find: "20,000" OR "30,000" OR "40,000" in BRELA context
For each match:
  Name reservation: change to TZS 50,000
  Incorporation: change to TZS 95,000 minimum
  Foreign branch: change to USD 750 plus USD 220

SCAN 4: income_tax DSE rate and AMT
Search ALL batch files for DSE 25% described as permanent:
  Patterns: "muda wote" "permanently" "indefinitely" "daima" in DSE context
  Fix: Add "kwa miaka 3 tu kuanzia tarehe ya kuorodheshwa"
  English: "for three years only from the listing date"
Search ALL batch files for AMT applying to all companies:
  Patterns: "kampuni zote" "all companies" "any company" near "1%" near "mauzo"
  Fix: Add "kwa kampuni zenye hasara ya kodi kwa miaka 3 mfululizo tu"
  English: "only for companies with 3 consecutive years of tax losses"

SCAN 5: WCF deadline — verify correction H is complete
Run:
grep -n "siku 30\|30 days" \
  datasets/tier1a/raw_sources/raw_pairs_batch_003.jsonl \
  datasets/tier1a/raw_sources/raw_pairs_batch_004.jsonl \
  datasets/tier1a/raw_sources/raw_pairs_batch_005.jsonl \
  datasets/tier1a/raw_sources/raw_pairs_batch_006.jsonl \
  | grep -i wcf
If any matches found: change to "siku 7 za kazi" / "7 working days"

SCAN 6: OSHA threshold — apply Correction 13 + 20 to ALL batches
Search ALL batch files for "wafanyakazi 10.*OSHA" OR "OSHA.*10 employees"
OR "10 or more employees.*OSHA" in OSHA subdomain pairs
For each match:
  Change to: "Kila mwajiri mwenye mahali pa kazi Tanzania analazimika
  kusajili na OSHA bila kujali idadi ya wafanyakazi"
  English: "Every employer with a workplace in Tanzania must register
  with OSHA regardless of employee count"
Also search for wcf_010 comparison "OSHA (threshold ya 10)":
  Change to: "OSHA inatumika kwa mahali pote pa kazi bila kizingiti"
  English: "OSHA applies to all workplaces without a threshold"

============================================================
TASK GROUP 3: LOCKED_FACTS.JSON UPDATES
Run after scans complete.
============================================================

Add these new entries to scripts/locked_facts.json:

Entry: osha_registration_threshold_b004
  fact: "OSHA applies to ALL workplaces — no minimum employee threshold"
  wrong_patterns: [
    "wafanyakazi 10.*OSHA",
    "OSHA.*10 employees",
    "OSHA.*threshold ya 10",
    "10 or more.*OSHA",
    "OSHA.*wafanyakazi 10 au zaidi",
    "biashara zenye wafanyakazi chini ya 10.*OSHA"
  ]

Entry: dse_25_rate_three_years_only
  fact: "DSE 25% CIT rate applies for THREE YEARS ONLY from listing date"
  wrong_patterns: [
    "muda wote.*DSE.*25",
    "permanently.*DSE.*25",
    "daima.*asilimia 25.*DSE",
    "indefinitely.*25.*listed",
    "DSE.*25.*permanently"
  ]

Entry: amt_loss_companies_only
  fact: "AMT 1% applies ONLY to companies with 3 consecutive years of tax losses"
  wrong_patterns: [
    "kampuni zote.*1%.*mauzo",
    "all companies.*1%.*turnover",
    "any company.*minimum.*1%",
    "kampuni yoyote.*kodi ya chini.*1"
  ]

Entry: permit_class_d_does_not_exist
  fact: "Tanzania has NO Class D permit — only Class A, B, C"
  wrong_patterns: [
    "Class D",
    "Darasa D",
    "darasa D",
    "kibali cha darasa D"
  ]

Run check after updates:
python scripts/check_locked_facts.py \
  --file datasets/tier1a/raw_sources/raw_pairs_batch_003.jsonl
python scripts/check_locked_facts.py \
  --file datasets/tier1a/raw_sources/raw_pairs_batch_004.jsonl
python scripts/check_locked_facts.py \
  --file datasets/tier1a/raw_sources/raw_pairs_batch_005.jsonl
python scripts/check_locked_facts.py \
  --file datasets/tier1a/raw_sources/raw_pairs_batch_006.jsonl
All must return CLEAN before proceeding to Task Group 4.

============================================================
TASK GROUP 4: MOVE TO CLEANED_PAIRS + GENERATE SFT
Run only after Task Group 3 returns CLEAN on all batches.
Do NOT run if any cross-AI review from Task Group 1 is still running —
wait for it to finish and check flags first.
============================================================

STEP 4A: Check if Task Group 1 cross-AI reviews are complete
Check: tail scripts/verify_bg_batch003.txt
Check: tail scripts/verify_bg_batch004_full.txt
If still running: wait. Print status and pause.
If complete: check for any new consensus flags before continuing.

STEP 4B: Move batches to cleaned_pairs
cp datasets/tier1a/raw_sources/raw_pairs_batch_003.jsonl \
   datasets/tier1a/cleaned_pairs/batch_003_cleaned.jsonl
cp datasets/tier1a/raw_sources/raw_pairs_batch_004.jsonl \
   datasets/tier1a/cleaned_pairs/batch_004_cleaned.jsonl
cp datasets/tier1a/raw_sources/raw_pairs_batch_005.jsonl \
   datasets/tier1a/cleaned_pairs/batch_005_cleaned.jsonl

NOTE: batch_006 stays in raw_sources until founder reviews its
cross-AI flags (3 consensus + 37 human-review flags in report above).

STEP 4C: Full corpus check
python scripts/check_locked_facts.py \
  --file datasets/tier1a/cleaned_pairs/batch_001_cleaned.jsonl
python scripts/check_locked_facts.py \
  --file datasets/tier1a/cleaned_pairs/batch_002_cleaned.jsonl
python scripts/check_locked_facts.py \
  --file datasets/tier1a/cleaned_pairs/batch_003_cleaned.jsonl
python scripts/check_locked_facts.py \
  --file datasets/tier1a/cleaned_pairs/batch_004_cleaned.jsonl
python scripts/check_locked_facts.py \
  --file datasets/tier1a/cleaned_pairs/batch_005_cleaned.jsonl
python scripts/build_question_index.py --check
python scripts/clean_temp_files.py --scan
All must return CLEAN.

STEP 4D: Check corpus count BEFORE generating SFT
Count total trainable pairs:
python -c "
import json, glob
total = sum(
  1 for f in glob.glob('datasets/tier1a/cleaned_pairs/*.jsonl')
  for line in open(f, encoding='utf-8') if line.strip()
  for p in [json.loads(line)] if not p.get('eval_set', False)
)
print(f'Total trainable pairs: {total}')
print('GO' if total >= 1500 else f'BLOCKED — need 1500, have {total}')
"

IF total < 1500: STOP HERE before SFT generation.
Print: "TRAINING BLOCKED — {total} pairs ready, need 1500.
Batch_006 (300 pairs) must be approved and moved to cleaned_pairs first.
Run targeted scan on batch_006, complete founder review of its
3 consensus flags and remaining human-review flags, then move it.
Commit all scan fixes below and STOP — do not generate SFT yet."

IF total >= 1500: Continue to STEP 4E.

IMPORTANT NOTE ON REPEATED PAIRS:
Batch_001 and batch_002 (300 pairs) were trained in adapter-v1.
Including them in this retrain is CORRECT and REQUIRED because:
1. Corrections A-J were applied to those pairs — the model needs to
   see the corrected versions to overwrite wrong patterns from v1.
2. This is a FULL RETRAIN from scratch — NOT a resume or incremental.
3. generate_sft.py must use ALL cleaned_pairs/ batches 001-006.
DO NOT exclude batch_001 or batch_002 from the SFT generation.

STEP 4E: Generate SFT files (only if total >= 1500)
python scripts/check_eval_split.py
python scripts/generate_sft.py
Expected: Train ~1350, Val ~150 (90/10 of 1500 pairs from all 6 batches)

STEP 4F: PURGE all old files from HuggingFace BEFORE uploading
This is mandatory. Old train_sft.jsonl and val_sft.jsonl from adapter-v1
(300 pairs) will still be sitting on HuggingFace. If you upload new files
without deleting the old ones first, Kaggle may load a mix of old and new
data — the dataset repo caches aggressively and will NOT automatically
replace old files with new ones of the same name reliably.

Step 1 — Delete ALL existing files in the dataset repo:
python scripts/hf_clean_upload.py --delete-only
This removes: train_sft.jsonl, val_sft.jsonl, any .parquet files,
any instruction_dataset.jsonl, any leftover files from previous runs.

Step 2 — Verify the repo is completely empty:
python scripts/hf_clean_upload.py --verify
Expected output: "train_sft.jsonl: MISSING | val_sft.jsonl: MISSING | No .parquet files"
If any file still shows as present: run --delete-only again before continuing.
DO NOT upload until the repo is confirmed empty.

Step 3 — Upload fresh SFT files:
python scripts/hf_clean_upload.py --upload

Step 4 — Verify upload is clean (no old files mixed in):
python scripts/hf_clean_upload.py --verify
Expected: "train_sft.jsonl: present | val_sft.jsonl: present | No .parquet files"
Also verify pair counts are correct:
python -c "
import json
train = sum(1 for l in open('datasets/tier1a/sft/train_sft.jsonl', encoding='utf-8') if l.strip())
val = sum(1 for l in open('datasets/tier1a/sft/val_sft.jsonl', encoding='utf-8') if l.strip())
print(f'Local SFT: train={train}, val={val}, total={train+val}')
print('CORRECT' if train+val >= 1480 else 'ERROR — count too low, check generate_sft.py')
"

If verify fails or count is wrong: STOP. Do not proceed to training.
Fix the upload issue before continuing.

STEP 4G: Final commit
git add datasets/tier1a/cleaned_pairs/
git add datasets/tier1a/raw_sources/
git add scripts/locked_facts.json
git commit -m "founder review complete: 20 corrections applied + targeted scans + 1500 pairs ready for full retrain from scratch — adapter-v2"
git push origin main
Show commit hash then STOP and wait for founder instruction.

============================================================
REPORT WHEN DONE — print this summary:
============================================================
1. Cross-AI reviews: batch_003 complete? Y/N, flags found
   Cross-AI reviews: batch_004 pairs 41-280 complete? Y/N, flags found
2. Scans completed:
   - compliance_costs: X pairs fixed across Y batches
   - work_permits Class D: X pairs fixed
   - BRELA fees: X pairs fixed
   - DSE/AMT income_tax: X pairs fixed
   - WCF deadline remaining: X found (should be 0)
   - OSHA threshold: X pairs fixed across all batches
3. locked_facts.json: 4 new entries added Y/N
4. All batches CLEAN Y/N
5. Batches 003-005 moved to cleaned_pairs Y/N
6. TRAINING GATE: total trainable pairs = X
   Is X >= 1500? Y/N
   If N: STOP — list what is needed to reach 1500
   If Y: SFT generated: Train ~1350, Val ~150
7. HuggingFace upload: complete Y/N (only if >= 1500)
8. Commit hash: [show hash]
Then STOP.