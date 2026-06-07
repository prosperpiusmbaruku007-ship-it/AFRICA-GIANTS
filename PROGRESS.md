# PROGRESS LOG — AFRICA-GIANTS
## Last Updated: 2026-06-07 (session 2)

## Project Info
- Repo: https://github.com/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS
- Kaggle account: prospaprospa
- Working notebook URL: https://www.kaggle.com/code/prospaprospa/africa-giants-v2
- Base model: McGill-NLP/AfriqueLlama-8B
- Trained adapter on HF: prospaprospa007/africa-giants-adapter-v1
- HF secret in Kaggle: AFRICA_GIANTS
- Pipeline state file: models/pipeline_state.json
- Reference narrative: docs/reference_narrative.md

---

## 1. CURRENT PHASE

**FACT-GUARDIAN infrastructure installed. batch_002 error-corrected and checker CLEAN (0 flags). HF dataset updated to 300-pair SFT corpus. Next: build batch_003 adversarial pairs targeting SDL/GN487A/VAT model failures identified by inference test.**

---

## 2. LAST VERIFIED COMPLETED (with dates)

### 2026-06-07 — FACT-GUARDIAN installed + batch_002 error-corrected — CLEAN d901d64

**FACT-GUARDIAN infrastructure:**
- `scripts/locked_facts.json` — 41 locked regulatory facts with wrong_patterns, primary sources, verified dates
- `scripts/check_locked_facts.py` — validation script; exit 0 = CLEAN, exit 1 = violations; writes fact_check_log.txt
- Folder structures created: `.claude/skills/` (9 skill dirs) + `datasets/tier1a/flagged/` (needs_human_review/ consensus_blocked/ resolved/)
- HF dataset `prospAprospA007/africa-giants-dataset` updated — old 47-pair files deleted, new 300-pair SFT files uploaded (train_sft.jsonl 222KB, val_sft.jsonl 23KB)

**batch_002 error corrections (10 genuine errors across 8 pairs):**
- `permit_012`: Class B mislabelled as investor → corrected to employed expatriate
- `permit_011`: Class C described as work permit for employees → added Class B clarification
- `paye_deep_015`: PAYE late penalty stated as 5% → corrected to 2.5%
- `biz_lic_004`: "Tanzania Food and Drugs Authority" → "Tanzania Medicines and Medical Devices Authority (TMDA)"
- `biz_lic_002`, `biz_lic_015`: LGA licence renewal deadline "31 January" → "31 March"
- `paye_extended_018`: P9 deadline "31 January" → "31 March"

**Checker result:** `python scripts/check_locked_facts.py --file datasets/tier1a/cleaned_pairs/batch_002_cleaned.jsonl`
→ **CLEAN — 0 violations** (started at 55 flags, all resolved via error fixes + pattern tightening)

**Commits:** a71ccd3 (55→2 flags), d901d64 (2→0 flags, CLEAN)

**Inference test failures identified** (from 300-pair training run, accuracy 67% in-corpus / 40% refusal):
- SDL: model STILL says "disability leave" — needs 50+ adversarial pairs
- GN487A: model STILL says it's about residence permits — needs 80 adversarial pairs (HIGHEST PRIORITY)
- VAT: model inventing 5% food VAT and 10% utilities VAT — needs 40+ adversarial pairs

### 2026-06-04 — Batch 002 CLEANED and COMMITTED (243 pairs)
- File: datasets/tier1a/cleaned_pairs/batch_002_cleaned.jsonl — 243 pairs
- Combined with batch_001 (57): **300 total cleaned pairs** — corpus milestone
- 25 corrections applied across 3 runs (39 pairs updated):
  - Run 1: PAYE band 8% (not 9%), worked examples recalculated, penalty 2.5%, interest rate → statutory TRA
  - Run 2: Permit classes (A/B not B/C), royalties WHT 15%/15%, provisional tax 4 instalments,
    min turnover tax 1% (Finance Act 2025), tax disputes 6 months + 1/3 deposit + TRAB 45-day step,
    stamp duty flat 1%, P9 deadline 31 March
  - Run 3: P45 removed → Leaving Certificate/P9, casual worker one month, director WHT 20% non-residents,
    BRELA Form 23 disclaimer, TMDA (not TFDA), loss carry forward 60% cap, public sector PSC disclaimer,
    tax clearance caveat, PRN expiry softened, first-time offender no-guarantee note
- Validation: 300 pairs, 0 errors, 0 duplicates — PASSED
- Next: Upload batch_002_cleaned.jsonl to HuggingFace, retrain on 300 pairs on Kaggle

### 2026-06-03 — Batch 002 dataset build COMPLETE (193 raw pairs)
- File: datasets/tier1a/raw_sources/raw_pairs_batch_002.jsonl — 193 pairs
- Combined with batch_001 (57): **250 total pairs** — milestone reached
- Subdomains all batches:
  - Batch A (original): paye (25), gn605a (20), work_permits (15), withholding_tax (15), vat_edge_cases (15), nssf_edge_cases (10) [100 pairs]
  - Batch C: paye_extended (20), income_tax (15), business_licensing (15) [50 pairs]
  - Batch D: stamp_duty (10), skills_levy_extended (8), nssf_disputes (8), brela_changes (10), tax_disputes (7) [43 pairs]
- Deduplication: 0 duplicates across all 250 pairs — CLEAN
- Schema validation: 0 errors, all 18 fields populated
- Scraping (new URLs): stamp_duty.html, withholding2.html, brela2.html, nssf2.html — OK
  paye_retry.html timed out, income_tax.html timed out — fallback to CLAUDE.md locked facts
- existing_questions.txt: 500 questions (250 pairs × 2 languages)
- Status: COMPLETE — awaiting founder review before moving to cleaned_pairs/

### 2026-06-03 — Accuracy gate eval launched
- Eval notebook: https://www.kaggle.com/code/prospaprospa/africa-giants-eval
- Kernel: prospaprospa/africa-giants-eval — status RUNNING when last observed
- Scoring: 200 questions × keyword/number/refusal match per answer_type
- On completion: uploads gate_001_results.json to prospaprospa007/africa-giants-adapter-v1 on HF Hub
- When results arrive: save to eval/results/gate_001_results.json and update PROGRESS.md Section 8 table
- Gate targets: >85% in-corpus accuracy AND >70% out-of-corpus refusal

### 2026-06-03
Eval set complete: 200 questions written, 17 post-review fixes applied, committed to main. Self-check passed: 0 errors, 0 banned sources, 10 out-of-corpus refusals, 0 duplicate IDs.

### Eval Set Build (2026-06-03) — COMPLETE
- eval/accuracy_gate/eval_questions_001.jsonl — 200 questions committed (bfc8aed)
- IDs: eval_001 to eval_200
- Self-check passed: 0 parse errors, 0 missing fields, 0 banned sources, 0 duplicates
- 17 post-review fixes applied (COSOTA/BRELA, VAT arithmetic, NSSF deadlines, OSHA thresholds)
- Subdomains: vat_registration 30, vat_withholding 20, efd_compliance 20, brela_registration 15, nssf_contributions 25, sdl_compliance 25, gn487a 40, osha_registration 15, out_of_corpus 10

### Training Pairs — Batch 001 (2026-06-02) — COMMITTED fbd2045
- File: datasets/tier1a/cleaned_pairs/batch_001_cleaned.jsonl
- Total pairs: 57 (50 original + 7 adversarial)
- Validation: PASSED — 57 pairs, 0 errors
- eval_set=true: 10 pairs held out
- verified_by: founder_self_review (50) / pending_founder_review (7 adversarial)
- All fixes applied: SDL/NSSF dates, VAT/SDL URLs, rolling threshold language,
  qualifying-buyer definition, professional services exception, Thibitisha closings,
  adversarial pairs added

### Training Pipeline (May 2026) — COMPLETED
- EOS token root cause found and fixed
- Training run: loss 3.177 → 1.574, val loss 1.371 — PASSED threshold 2.5
- Adapter pushed: prospaprospa007/africa-giants-adapter-v1
- Runtime: 41.1 seconds on Tesla T4

### Infrastructure (2026-06-01) — COMPLETED
- CLAUDE.md: full behavioral contract (13 sections, all rules R1–R12)
- Directory structure: datasets/tier1a through tier3, eval/, schema/, sources/
- schema/pair_schema.json: 18-field canonical contract
- sources/whitelist.json: all approved scrape targets
- scripts/validate_dataset.py: schema + whitelist enforcement
- scripts/run_eval.py: accuracy + refusal gate runner

---

## 3. ACTIVE WORK

### Immediate next tasks

**Step 9:** ✅ Training data uploaded to HF Hub. Notebook `africa-giants-v2` run triggered on Kaggle.

**Step 10:** ✅ Accuracy gate results: 67% in-corpus accuracy / 40% refusal rate — BOTH GATES FAILED.
Target: >85% in-corpus AND >70% refusal. Training on 300 pairs insufficient.

**Step 11:** ✅ Dataset build COMPLETE — 300 pairs total (batch_001 57 + batch_002 243).

**Step 12:** ✅ Founder reviewed batch_002, 25 corrections applied, batch_002_cleaned.jsonl committed.

**Step 13:** ✅ HF dataset updated — 300-pair SFT files uploaded (train_sft.jsonl + val_sft.jsonl).

**Step 14:** ✅ FACT-GUARDIAN installed — locked_facts.json (41 facts) + check_locked_facts.py. Checker CLEAN on batch_002.

**Step 14b:** ✅ Autonomy scripts installed (b4772d4):
  - `scripts/check_sources.py` — SOURCE-ENFORCER, CLEAN on batch_002
  - `scripts/build_question_index.py` — DEDUP-GUARD, 600 unique questions / 300 IDs indexed
  - `scripts/generate_sft.py` — SFT file generator; produces 261 train / 29 val from 290 non-eval pairs
  - `scripts/hf_clean_upload.py` — HF upload tool (delete old → upload new → verify); do NOT run without intent

**Step 15:** ⬜ Build batch_003 — adversarial pairs targeting the 3 confirmed model failure modes:
  - GN487A confusion (80 pairs) — model says it's about residence permits
  - SDL confusion (50 pairs) — model says "disability leave"
  - VAT invented rates (40 pairs) — model invents 5%/10% reduced rates
  Total batch_003 target: ~170 adversarial pairs

**Step 16:** ⬜ Retrain on 300 + batch_003 corpus on Kaggle africa-giants-v2, re-run accuracy gate.

**Step 17:** ⬜ Engage TRA consultant for 10% training pair sample review — ~30 pairs, ~TZS 50,000–100,000.

### Open items on training pairs (not blocking training run)
- NSSF alternate arrangement (15%/5%) — no training pair covers this yet
- NSSF deadline wording: pairs say "10th" but primary source says "within one month"
- 7 adversarial pairs need founder review (pending_founder_review)
- 10% sample (6 pairs) needs TRA-registered consultant review (~TZS 50,000–100,000)

---

## 4. NEXT PHYSICAL ACTIONS (dependency-ordered)

1. ✅ Create all dataset directory structure
2. ✅ Create schema/pair_schema.json
3. ✅ Create sources/whitelist.json
4. ✅ Create scripts/validate_dataset.py
5. ✅ Create scripts/run_eval.py
6. ✅ Commit and push infrastructure to GitHub
7. ✅ Batch 001: 57 pairs validated and committed — fbd2045 (2026-06-02)
8. ✅ Build 200-question eval set — 200 of 200 done, committed bfc8aed / 302e299
9. ✅ Founder reviews eval set quality — complete, 17 fixes applied and committed
10. ✅ Commit eval set to GitHub after founder approval — done
11. ✅ Trained on 300 pairs — adapter prospaprospa007/africa-giants-adapter-v1 pushed
12. ✅ Accuracy gate run: 67% in-corpus / 40% refusal — FAILED both gates
13. ✅ FACT-GUARDIAN installed — checker CLEAN on batch_002 (d901d64)
14. ⬜ Build batch_003 adversarial pairs (GN487A 80 + SDL 50 + VAT 40 = ~170 pairs)
15. ⬜ Retrain on expanded corpus, re-run accuracy gate
16. ⬜ Engage TRA consultant for 10% training pair sample review — ~30 pairs, ~TZS 50,000–100,000
17. ⬜ If gate passes: prepare first human pilot on WhatsApp

---

## 5. BLOCKED ITEMS

| Blocker | Unblocked by |
|---------|-------------|
| Accuracy gate run | Retrain adapter on Kaggle + run scripts/run_eval.py |
| Tier 1A expert review | Engaging TRA-registered consultant (human decision) |
| Tier 1B start | Tier 1A accuracy gate passing |
| Tier 1C start | Tier 1A accuracy gate passing |
| Product launch (any form) | BOTH gates passing: >85% in-corpus AND >70% refusal |
| Seed funding conversation | Accuracy gate passed + 200 real WhatsApp conversations |
| Institutional partnership pitch | Verified legibility profiles from Tier 2A |

---

## 6. DECISIONS LOCKED (with source and date)

| Decision | Source | Locked |
|----------|--------|--------|
| NeST not TANePS (mandatory from 1 Jul 2023) | PPRA.go.tz, NeST Guidelines 2025 | Jun 2026 |
| Finance Act 2025 VAT withholding 3%/6% effective 1 Jul 2025 | EY/KPMG Oct 2025 | Jun 2026 |
| GN 605A minimum wage, effective 1 Jan 2026 | PKF/VELMA/TanzLII | Jun 2026 |
| 2022 wage order REVOKED effective 1 Jan 2026 | GN 605A | Jun 2026 |
| GN 487A: 15 prohibited activities, effective 28 Jul 2025 | Bowmans/Dentons/VELMA | Jun 2026 |
| Training + eval from different source families | Research session | Jun 2026 |
| WhatsApp-first delivery (36.75% smartphones, 77% USSD) | TCRA Jun 2025 | Jun 2026 |
| No logistics/goods movement (B2B graveyard evidence) | Reference narrative | Jun 2026 |
| VICOBA: assist+explain only, never the ledger | Reference narrative | Jun 2026 |
| Tier 3 data generated by operation, not authored | Reference narrative | Jun 2026 |
| STR disambiguation: originating status ≠ Common List eligibility | COMESA/EAC Secretariat | Jun 2026 |
| Domain expert sign-off required on 10% sample before gate | Research session | Jun 2026 |
| EAC STR threshold: USD 2,000 / ~370 eligible products | COMESA Secretariat | Jun 2026 |
| No credit scoring without licensed bank partner + BoT legal opinion | Reference narrative | Jun 2026 |
| NMB Bank: ~USD 180M DFI package (IFC/BII/Norfund) | TechAfrica News 2025 | Jun 2026 |
| Claude Code cannot fetch external URLs in this environment | Confirmed 2026-06-03 | Jun 2026 |
| Eval questions written from CLAUDE.md locked facts — acceptable | Confirmed 2026-06-03 | Jun 2026 |

---

## 7. DECISIONS STILL CONTESTED (require verification before encoding)

**Tanzania tourism earnings exact figure:**
- Status: [VERIFY BEFORE USE]
- Primary source needed: Bank of Tanzania Annual Report or Tanzania Tourism Board
- Do not cite in any investor, government, or training pair context until verified

**Any claim from citation laundering sources (full list in CLAUDE.md Section 3):**
- Status: Facts may be real; citations were fabricated across 8 research iterations
- Action: Re-verify against CLAUDE.md Section 4 whitelist before encoding as training pair

---

## 8. DATASET STATUS TABLE

| Domain | Target pairs | Written | Verified | In eval set | Gate passed |
|--------|-------------|---------|----------|-------------|-------------|
| Tier 1A: TRA Compliance | 300 | 37 | 0 | 7 | No |
| Tier 1A: Labour/GN 605A | 200 | 0 | 0 | 0 | No |
| Tier 1A: GN 487A | 100 | 12 | 0 | 2 | No |
| Tier 1B: EAC STR | 300 | 0 | 0 | 0 | No |
| Tier 1C: NeST | 200 | 0 | 0 | 0 | No |
| Tier 2A: Legibility | 200 | 0 | 0 | 0 | No |
| Tier 2B: VICOBA | 300 | 0 | 0 | 0 | No |
| Tier 3 | Reserved | — | — | — | — |
| **TOTAL** | **1,600** | **300** | **0** | **10** | **No** |

### Eval Set Status (separate from training pairs)
| File | Questions written | Questions remaining | Committed | Self-check |
|------|------------------|--------------------|-----------| -----------|
| eval/accuracy_gate/eval_questions_001.jsonl | 200 | 0 | Yes | Not started |

---

## 9. SCRAPE TARGETS PIPELINE

### Tier 1A Training Sources
| URL | Source type | Decay risk | Status |
|-----|------------|-----------|--------|
| tra.go.tz/index.php/tax-information | gov portal | Annual | pending |
| tra.go.tz/index.php/filing-returns | gov portal | Annual | pending |
| brela.go.tz | gov portal | Stable | pending |
| nssf.or.tz | gov portal | Annual | pending |
| osha.go.tz | gov portal | Stable | pending |
| Tanzania Government Gazette (GN 487A, GN 605A, Finance Act 2025) | official gazette | Event-triggered | pending |
| tanzlii.org | official law | Event-triggered | pending |

### Tier 1A Eval Sources
| URL | Source type | Decay risk | Status |
|-----|------------|-----------|--------|
| ey.com/en_tz Finance Act 2025 | tier1 advisory | Annual | used — network blocked, facts from CLAUDE.md |
| kpmg.com/tz Tax News Flash | tier1 advisory | Annual | used — network blocked, facts from CLAUDE.md |
| pkfea.com GN 605A alert | tier1 advisory | Event-triggered | used — network blocked, facts from CLAUDE.md |
| velmalaw.co.tz GN 487A analysis | tier1 advisory | Event-triggered | used — network blocked, facts from CLAUDE.md |
| bowmans.com GN 487A briefing | tier1 advisory | Event-triggered | used — network blocked, facts from CLAUDE.md |
| taxsummaries.pwc.com/tanzania | tier1 advisory | Annual | used — network blocked, facts from CLAUDE.md |

---

## 10. DOMAIN EXPANSION TRIGGERS

Do not build these until their specific triggers fire.

**Domestic tourism operators:** Trigger: >1,000 verified Tier 1A users
**Labour Court navigation:** Trigger: >500 GN 605A questions in corpus
**Agricultural compliance:** Trigger: VICOBA corpus shows >20% agriculture-linked groups
**Merchant/VICOBA credit scoring (Tier 3):** Trigger: 18+ months data + named bank partner
  LEGAL GATE: BoT legal opinion required before build begins — blocking question
**Kenya expansion:** Unlocked by EAC cross-border corpus (Tier 1B)

---

## KAGGLE ENVIRONMENT (do not change)
- trl: 0.24.0 | transformers: 5.5.0 | GPU: Tesla T4 | Python: 3.12
- AfriqueLlama eos_token: `<|end_of_text|>` id=128001
- Dataset: 17 train / 4 eval examples | Training: 10 steps, 2 epochs, 41.1 seconds

---

## RULES FOR THIS FILE
- Update after every session (Section 2, Section 3, Section 8 table)
- Use ISO dates (YYYY-MM-DD) for all timestamps
- Never put behavioral rules here — those belong in CLAUDE.md
- Never put architecture specs here — those belong in CLAUDE.md
- This file tracks WHAT HAS HAPPENED and WHAT IS NEXT, not HOW TO BEHAVE