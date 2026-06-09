#Read this file completely then execute every instruction below exactly as written.

Continue to next subdomain without stopping

SUBDOMAIN 3: vat_registration (40 pairs)
Current total in file: 130 pairs. Write pairs 131-170.
Every VAT pair MUST:

State 18% is the ONLY VAT rate — no 5% or 10% exists
At least 15 pairs directly contradict invented 5%/10% rates
Cover: registration threshold TZS 200M/year or 100M/6mo
Cover: VAT withholding 3% goods / 6% services (Finance Act 2025)
Cover: zero-rated vs exempt distinction
Register: 40% business_market, 30% formal, 20% rural

After 40 pairs: run 3 checks, commit if clean.
Commit message: "batch_003 checkpoint: 170 pairs (gn487a+sdl+vat)"
Then immediately continue to next subdomain.

SUBDOMAIN 4: out_of_corpus refusal (30 pairs)
Write pairs 171-200.
Every refusal pair MUST:

Answer a question OUTSIDE Tanzania Tier 1A compliance
Politely refuse and redirect to what the model covers
Examples of out-of-corpus questions:
Kenya tax law, Uganda regulations, EAC tariffs,
Zanzibar-specific rules, insurance premium levy,
capital gains tax on shares, mining royalties,
personal financial advice, medical advice,
legal advice beyond compliance, crypto regulations

Example pair:
Q_SW: "Niambie kuhusu kodi ya VAT nchini Kenya."
A_SW: "Samahani — ninasaidia tu na maswali ya biashara
na kodi nchini Tanzania Bara. Kwa maswali ya
Kenya tafadhali wasiliana na KRA (kra.go.ke).
Je, una swali kuhusu VAT Tanzania?"
pair_type: disambiguation
register: business_market

Register: 50% business_market, 30% rural, 20% formal
pair_type: disambiguation for all refusal pairs
eval_set: false

After 30 pairs: run 3 checks, commit if clean.
Commit message: "batch_003 checkpoint: 200 pairs (added refusal)"
Then immediately continue.

SUBDOMAIN 5: nssf_contributions deep (50 pairs)
Write pairs 201-250.
Cover these edge cases not in existing 25 nssf pairs:

Multi-employer NSSF — how calculated when employee
has two jobs
NSSF for casual workers — monthly vs daily workers
NSSF for directors — are working directors covered?
NSSF for foreign employees — do they pay?
NSSF calculation on overtime and bonuses
NSSF and maternity leave — obligations continue?
NSSF payment when employee is on unpaid leave
NSSF for probationary employees
NSSF for part-time workers — pro-rata calculation
NSSF contribution ceiling — is there one?
Alternative arrangement 15%/5% — when allowed?
NSSF and WCF difference — two separate obligations
NSSF registration new employer — timing requirement
NSSF number portability across employers
NSSF and pension fund double contribution — allowed?

Every NSSF pair MUST state:

Rate: 10% employer + 10% employee = 20% total
Base: gross wage (not basic salary)
Deadline: within one month after salary month

Register: 40% business_market, 30% formal, 20% rural
After 50 pairs: run 3 checks, commit if clean.
Commit message: "batch_003 checkpoint: 250 pairs (added nssf_deep)"
Then immediately continue.

SUBDOMAIN 6: efd_compliance_deep (50 pairs)
Write pairs 251-300.
Cover these angles not in existing 8 efd pairs:

EFD machine types: ETR vs EFD vs VFD — differences
EFD registration process — who must register
EFD receipt requirements — what must appear on receipt
EFD for service businesses — same rules as retail?
EFD malfunction — what to do, manual receipts allowed?
EFD and mobile money payments — receipt required?
EFD for market vendors — threshold for requirement
EFD for professionals (lawyers, doctors, consultants)
EFD receipt rejection by customer — legal obligation
EFD audit — what TRA checks
EFD penalties — failure to issue receipt
EFD and VAT — relationship between two obligations
EFD for online businesses — requirement applies?
EFD Z-report — daily requirement explained
EFD for businesses with multiple branches

Register: 40% business_market, 30% formal, 20% rural
After 50 pairs: run 3 checks, commit if clean.
Commit message: "batch_003 checkpoint: 300 pairs complete"

FINAL STEPS after all 300 pairs written
Step 1: Run full validation
python scripts/validate_raw.py 2>/dev/null || 
python scripts/validate_dataset.py 
--file datasets/tier1a/raw_sources/raw_pairs_batch_003.jsonl
Step 2: Run dedup check across all batches
python scripts/build_question_index.py --check
Step 3: Run full cross-AI review on complete batch_003
python scripts/verify_pairs.py 
--file datasets/tier1a/raw_sources/raw_pairs_batch_003.jsonl 
--batch-size 20
If Gemini returns 503: wait 60 seconds and retry.
If OpenRouter returns 429: wait 60 seconds and retry.
Show which batches got live responses.
Step 4: Run locked facts on final file
python scripts/check_locked_facts.py 
--file datasets/tier1a/raw_sources/raw_pairs_batch_003.jsonl
Step 5: Show summary report

Total pairs written
Pairs per subdomain
Register distribution
Any flags or violations found

Step 6: Final commit
git add datasets/tier1a/raw_sources/raw_pairs_batch_003.jsonl
git add scripts/locked_facts.json
git commit -m "batch_003 complete: 300 adversarial pairs gn487a+sdl+vat+refusal+nssf_deep+efd_deep"
git push origin main
Show commit hash then STOP.