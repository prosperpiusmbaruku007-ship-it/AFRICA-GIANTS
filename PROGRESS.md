# PROGRESS LOG — AFRICA-GIANTS
## Last Updated: 2026-06-09 (session 7)

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

**batch_005 COMPLETE (300 pairs, commit eba5e97). Founder review samples generated for batch_003 + batch_004 (30 pairs each, commit 7dfe94f). Next: founder reviews batch_003_founder_sample.jsonl + batch_004_founder_sample.jsonl, approves both, then move all three batches (003/004/005) to cleaned_pairs/, run check_eval_split.py + generate_sft.py, retrain on Kaggle on 1,200 pairs.**

---

## 2. LAST VERIFIED COMPLETED (with dates)

### 2026-06-09 (session 6) — batch_004 cross-AI review + all consensus flags resolved from primary sources

**COMPLETED:**
- batch_004 cross-AI review: 300 pairs, 15 batches — commit `946c03d`
  - 18 consensus flags (both Gemini + OpenRouter agreed)
  - 124 single-model human-review flags (mostly OpenRouter false positives on adversarial pairs)
- Primary source verification of all 18 consensus flags:
  - WHT director fees (non-resident): **TRA.go.tz confirms 15% for all** — pairs had 20% (WRONG)
  - WCF accident reporting deadline: **portal.wcf.go.tz confirms 7 working days** — pairs had 30 days (WRONG); AI models said 14 days (also WRONG)
  - BRELA name reservation: **brela.go.tz confirms TZS 50,000** — pairs had 20,000 (WRONG)
  - BRELA local incorporation: **brela.go.tz confirms TZS 95,000 minimum** — pairs had 50,000 (WRONG)
  - BRELA foreign branch: **brela.go.tz confirms USD 750 + USD 220** — pairs had TZS 200,000+ (WRONG)
  - brela_deep_007 Certificate of Compliance description: wording dispute only, no factual error
- All 5 confirmed errors fixed — 15 pairs corrected total across 2 commits:
  - `f4ba56c` — WHT director fees + BRELA fees (4 fixes, 9 pairs)
  - `1cc7754` — WCF deadline (6 pairs: wcf_005/022/028 + osha_005/031 + mix_rc_007)
- locked_facts.json: added `wht_director_fees` and `wcf_accident_reporting` entries

**VERIFIED REGULATORY FACTS (added this session):**
- WHT director fees (non-full-time): 15% — single rate, residents AND non-residents. Source: TRA.go.tz
- WCF accident reporting: 7 working days via portal.wcf.go.tz. Source: WCF portal
- BRELA name reservation: TZS 50,000 / 30 days. Source: brela.go.tz/pages/tozo-za-kampuni
- BRELA incorporation (min): TZS 95,000 (scales with paid-up capital). Source: brela.go.tz
- BRELA foreign branch: USD 750 (certified copy) + USD 220 (document filing). Source: brela.go.tz

**CORPUS STATE (after session 7):**
- batch_001_cleaned.jsonl: 57 pairs (committed, verified)
- batch_002_cleaned.jsonl: 243 pairs (committed, verified)
- raw_pairs_batch_003.jsonl: 300 pairs — cross-AI CLEAN, needs founder 10% review
- raw_pairs_batch_004.jsonl: 300 pairs — cross-AI done, all consensus flags resolved, needs founder 10% review
- raw_pairs_batch_005.jsonl: 300 pairs — check_locked_facts CLEAN, check_sources CLEAN, needs founder review
- Total raw: 1,200 pairs
- Total cleaned: 300 pairs

**batch_005 subdomains:** permit_deep (50) + income_tax_adversarial (50) + stamp_duty_deep (50) + compliance_costs_deep (50) + efd_deep (50) + osha_nssf_adversarial (50)

**Founder review samples ready:**
- datasets/tier1a/flagged/needs_human_review/batch_003_founder_sample.jsonl (30 pairs)
- datasets/tier1a/flagged/needs_human_review/batch_004_founder_sample.jsonl (30 pairs)
- batch_005 needs its own founder review before moving to cleaned_pairs/

**PENDING BEFORE NEXT TRAINING:**
1. Founder reviews batch_003_founder_sample.jsonl (30 pairs) — approve or flag
2. Founder reviews batch_004_founder_sample.jsonl (30 pairs) — approve or flag
3. Generate batch_005 founder sample (30 pairs) and review
4. Move all three batches (003/004/005) to cleaned_pairs/ after approval
5. python scripts/check_eval_split.py
6. python scripts/generate_sft.py
7. Upload to HuggingFace and retrain on Kaggle (africa-giants-v2) on 1,200 pairs
8. Run accuracy gate — target >75% in-corpus, >70% refusal

**KNOWN UNRESOLVED (from cross-AI review, single-model flags — human review):**
- wcf_005 (Gemini): WCF notification timeframe — now fixed to 7 working days ✓
- Several OpenRouter flags on adversarial pairs: all false positives (model misreads question as answer)
- brela_deep_006: annual return 42 days vs 60 days — OpenRouter says 60, pairs say 42. Needs verification.

---

### 2026-06-09 (session 5) — batch_003 + batch_004 complete, OpenRouter fix, locked_facts hardening

**COMPLETED:**
- batch_003: 300 pairs (gn487a adversarial + sdl adversarial + vat + refusal + nssf_deep + efd_deep)
- batch_004: 300 pairs (gn605a + osha + paye adversarial + wht_deep + wcf + brela_deep + tax_disputes + rural)
- Cross-AI review: batch_003 reviewed, exit code 0 CLEAN
- OpenRouter: switched to `openrouter/auto` model (bypasses per-model free-tier rate limits)
- locked_facts.json: 15 pattern fixes for adversarial false-positives
- 14 skills installed, 11 scripts committed
- All mandatory CLAUDE.md rules active

### 2026-06-09 (session 7) — batch_005 COMPLETE + founder review samples generated

**COMPLETED:**
- batch_005: 300 pairs — commit `eba5e97`
  - permit_deep (50): work permit classes A/B/C/D/E, GN 487A interaction, adversarial
  - income_tax_adversarial (50): corporate tax, WHT rates, provisional tax, self-employed
  - stamp_duty_deep (50): flat 1% rate, lease/loan/share transfer, process, disambiguation
  - compliance_costs_deep (50): BRELA/TRA/NSSF/WCF/OSHA costs, EFD, penalties, EPZ
  - efd_deep (50): EFD mandate, receipts, VAT integration, TIMS, breakdowns, QR codes
  - osha_nssf_adversarial (50): OSHA vs WCF disambiguation, NSSF opt-out myths, WCF coverage
- Founder review samples: batch_003 + batch_004 (30 pairs each) — commit `7dfe94f`
- locked_facts.json: 11 additional patterns tightened (permit classes, SDL, PAYE, NSSF, stamp duty)
- check_sources.py: wcf.go.tz added to TRAINING_WHITELIST
- All 300 pairs: check_locked_facts CLEAN + check_sources CLEAN

**NEXT TASK (batch_006):**
- After founder approves batch_003/004/005: generate SFT on 1,200 pairs, retrain
- Target: 3,000 total pairs; 1,800 remaining after batch_005
- Suggested next subdomains: gn605a_deep (minimum wage sector tables), eac_str_intro (EAC STR — tier 1B unlock preview), vat_return_deep (filing procedures, credits, refunds)

---

### 2026-06-08 (session 4) — Verifier pipeline stabilised, data fixes, batch planner installed

**verify_pairs.py changes (session 4):**
- Gemini model: `gemini-2.0-flash` → `gemini-3.5-flash` (2.0-flash shutdown June 2026)
- Groq removed entirely — IP geo-blocked in Tanzania (HTTP 403 on all keys, confirmed 2 keys)
- Cerebras added then removed — also IP geo-blocked in Tanzania (HTTP 403)
- OpenRouter added — `meta-llama/llama-3.3-70b-instruct:free` — key valid, model confirmed,
  hits free-tier 429 before responding; not geo-blocked
- OPENROUTER_API_KEY loads from env var only (hardcoded key blocked by GitHub push protection)
- Commits: `3624554` (Gemini 3.5-flash), `f39f3f0` (OpenRouter added), `b94d9a8` (model ID confirmed)

**Data fixes (session 4) — committed `3efae26`:**
- `batch_001_cleaned.jsonl` — `sdl_001`: "Skills **and** Development Levy" → "Skills Development Levy"
- `locked_facts.json` — `vat_registration_threshold` pattern `"50 million"` → `"\\b50 million\\b"`
  (was false-positive matching "2**50** million" in vat_002 answer via substring match)
- `check_locked_facts.py` result after fix: **CLEAN — 0 violations** on batch_001 (57 pairs)

**plan_next_batch.py installed (session 4) — committed `cedf00e`:**
- Created from `do.md` command
- Output: 313 pairs current / 2,687 remaining / 9 batches of 300 needed
- No gate results file yet (`gate_001_results.json` not present)

**API key status (session 4 end):**
- Groq: geo-blocked — do not use
- Cerebras: geo-blocked — do not use
- Gemini `GEMINI_API_KEY`: **WORKING** — responds on all batches
- OpenRouter `OPENROUTER_API_KEY`: key valid, model confirmed, free-tier 429 (needs paid tier or retry)
- OpenAI `OPENAI_API_KEY`: 429 rate limit / quota exhausted
- ANTHROPIC_API_KEY: not set

**To run verifier next session:**
```powershell
$env:OPENROUTER_API_KEY = "sk-or-v1-..."   # your key from openrouter.ai/keys
python scripts/verify_pairs.py --file datasets/tier1a/cleaned_pairs/batch_002_cleaned.jsonl --batch-size 10
```

**Cross-AI review results — batch_001 (57 pairs), Gemini only responding:**
- 0 consensus flags (OpenRouter not responding = no 2-model agreement possible)
- 19 single-model Gemini flags — breakdown:
  - VAT rates (4 pairs): Gemini claims 18%/2%/2% — **pairs are correct** per Finance Act 2025
  - GN487A date (3 pairs): Gemini claims 28 Jun 2024 — **pairs are correct** (locked: 28 Jul 2025)
  - GN487A imprisonment (8 pairs): Gemini claims "not less than 12 months" vs pairs say "up to 6 months" — **NEEDS HUMAN VERIFICATION** against TanzLII gazette text
  - NSSF deadline (1 pair): Gemini claims 30 days/last day vs pairs say 10th — needs check
  - SDL name (already fixed this session)

**Session checkpoint commit: `cedf00e` — 63 files, 22,195 insertions — pushed to main**

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

**Step 14c:** ✅ REGULATORY-VERIFIER stabilised (session 4) — commit `b94d9a8`:
  - `scripts/verify_pairs.py` — Gemini 3.5-flash (working) + OpenRouter llama-3.3-70b (valid, 429 on free tier)
  - Groq and Cerebras removed — both geo-blocked in Tanzania
  - batch_001 reviewed: 0 consensus flags, 19 Gemini single-model flags (mostly hallucinations)
  - GN487A imprisonment penalty flag: Gemini claims 12mo minimum vs locked 6mo — verify before next batch

**Step 14d:** ✅ Data fixes applied and committed `3efae26`:
  - sdl_001 name corrected, locked_facts.json word-boundary fix — CLEAN on check_locked_facts.py

**Step 14e:** ✅ plan_next_batch.py installed — committed `cedf00e`:
  - 313 pairs / 2,687 remaining / 9 batches of 300 to target

**Step 15:** ⬜ Verify GN487A imprisonment penalty against TanzLII gazette
  - URL: https://tanzlii.org/akn/tz/act/gn/2025/487a/eng@2025-07-28
  - Question: is it "up to 6 months" or "not less than 12 months"?
  - Affects 8 pairs: gn487a_004–009, adv001, adv002
  - Fix pairs if Gemini is right; add locked fact if pairs are right

**Step 16:** ⬜ Build batch_003 — adversarial pairs targeting the 3 confirmed model failure modes:
  - GN487A confusion (80 pairs) — model says it's about residence permits
  - SDL confusion (50 pairs) — model says "disability leave"
  - VAT invented rates (40 pairs) — model invents 5%/10% reduced rates
  - Out-of-corpus refusal (30 pairs)
  - NSSF + EFD deep (50 pairs)
  Total batch_003 target: 300 pairs

**Step 17:** ⬜ Run verify_pairs.py on batch_002_cleaned.jsonl (243 pairs) once OpenRouter stops rate-limiting
  - `python scripts/verify_pairs.py --file datasets/tier1a/cleaned_pairs/batch_002_cleaned.jsonl --batch-size 10`

**Step 18:** ⬜ Retrain on 313 + batch_003 corpus on Kaggle africa-giants-v2, re-run accuracy gate.

**Step 19:** ⬜ Engage TRA consultant for 10% training pair sample review — ~30 pairs, ~TZS 50,000–100,000.

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
14. ✅ REGULATORY-VERIFIER stabilised — Gemini 3.5-flash + OpenRouter confirmed (b94d9a8)
15. ✅ Data fixes — sdl_001 name + locked_facts word-boundary fix — CLEAN (3efae26)
16. ✅ plan_next_batch.py installed — 313 pairs, 9 batches remaining (cedf00e)
17. ⬜ Verify GN487A imprisonment penalty (6mo vs 12mo) against TanzLII gazette
18. ⬜ Build batch_003 (300 pairs: GN487A 80 + SDL 50 + VAT 40 + refusal 30 + NSSF/EFD 50 + other 50)
19. ⬜ Run verify_pairs.py on batch_002_cleaned.jsonl when OpenRouter rate limit clears
20. ⬜ Retrain on expanded corpus, re-run accuracy gate
21. ⬜ Engage TRA consultant for 10% training pair sample review — ~30 pairs, ~TZS 50,000–100,000
22. ⬜ If gate passes: prepare first human pilot on WhatsApp

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
| **TOTAL** | **1,600** | **313** | **0** | **10** | **No** |

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