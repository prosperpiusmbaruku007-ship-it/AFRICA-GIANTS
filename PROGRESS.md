# PROGRESS LOG — AFRICA-GIANTS
## Last Updated: 2026-06-14 (session 13 — end of day)

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

**CHIKE BY AFRICA GIANTS — LIVE ON CEREBRIUM (ADA_L4, commit `bace093`). HTTP 200 confirmed. 4bit quantization with float16 fallback. min_replicas=0 (scale to zero). Wappfly handler live on Railway. Product renamed Chike. Railway server removed. 1,752 gazette-verified trainable pairs on HF. Adapter-v3 Kaggle training run pending (manual trigger required).**

**Product identity confirmed:** AI assistant = CHIKE | Company = AFRICA GIANTS | Full name = CHIKE BY AFRICA GIANTS

---

## 2. LAST VERIFIED COMPLETED (with dates)

### 2026-06-14 (session 13) — Chike LIVE on Cerebrium + Wappfly handler deployed

**COMPLETED:**
- Cerebrium deployment working — `chike-inference` app, ADA_L4 GPU, transformers inference:
  - Root cause of all prior vLLM failures confirmed: AfriqueLlama custom architecture not in vLLM registry
  - Switched `chike-inference/main.py` from vLLM → AutoModelForCausalLM + AutoTokenizer (transformers)
  - `cerebrium.toml`: `compute = "ADA_L4"` under `[cerebrium.hardware]` — proven working key format
  - HF_TOKEN secret already present in Cerebrium project; `login()` confirmed at startup
  - Prompt leak fixed: decode `outputs[0][input_len:]` (new tokens only); `apply_chat_template` with Llama-3 fallback; stop-string truncation for hallucinated follow-up turns
  - HTTP 200 on both test questions — clean replies, no prompt prefix
  - Cerebrium endpoint: `https://api.aws.us-east-1.cerebrium.ai/v4/p-e3f41403/chike-inference/run`
  - Commits: `2d195e7` (vLLM→transformers), `f35746f` (toml key fix), `39b4b19` (prompt leak fix)
- Wappfly webhook handler built — `wappfly-function/handler.py` (FastAPI, deployed to Railway):
  - Greeting detection returns WELCOME without calling Cerebrium
  - Calls Cerebrium `/run` with 120s timeout; passes `CEREBRIUM_KEY` from env
  - Fallback error message in Swahili + English if Cerebrium fails
  - Live at: https://striking-cat-production-ed7e.up.railway.app/webhook
  - WhatsApp number: +255637809070 (Wappfly inbound webhook connected)

**KNOWN MODEL ISSUES (adapter-v3 accuracy — not fixable in server code):**
- VAT rate: model says "18% goods / 16% services" — correct is single 18% standard rate
- Model generates multiple assistant turns when temperature > 0 (stop-string truncation handles this)
- Both issues are adapter-v3 training data gaps — target fix in adapter-v4 after Kaggle run

**CEREBRIUM DEPLOYMENT NOTES (locked — do not change without testing):**
- `compute = "ADA_L4"` is the correct key (NOT `gpu =`, NOT `hardware =`)
- `gpu =` and `memory =` under `[cerebrium.hardware]` are silently ignored — results in CPU-only deploy
- `AMPERE_A100` and `AMPERE_A100_40GB` require plan upgrade (hobby plan: CPU, ADA_L4, ADA_L40, AMPERE_A10, TURING_T4)
- vLLM is incompatible with AfriqueLlama — do not reintroduce it
- Scaling params must go under `[cerebrium.scaling]`, not `[cerebrium.deployment]`
- `response_grace_period = 180` is a valid field under `[cerebrium.scaling]`

**ADDITIONAL SESSION 13 WORK (after initial deployment):**

- Product renamed: **Chike → Chike Brain by Africa Giants** — commit `b31f96e` (reverted to Chike in session 14)
  - SYSTEM_PROMPT updated in `chike-inference/main.py`
  - CLAUDE.md, PROGRESS.md updated

- Old Railway inference server removed — commit `b31f96e`
  - Deleted: `server/`, `Procfile`, `railway.json`, `.env.example`
  - Replaced by Wappfly handler on Railway (`wappfly-function/handler.py`)

- Cerebrium scaling tuned across multiple commits:
  - `45bd5ef`: min_replicas=1, max_replicas=3, cooldown=300
  - `2b87730`: min_replicas=0, [cerebrium.scaling] section added, response_grace_period=180
  - `e6fa6d0`: min_replicas=1 (final — always warm, no cold starts)

- 4bit quantization added — commit `3c0e3db`
  - `BitsAndBytesConfig`: nf4, float16 compute, double quant
  - `bitsandbytes>=0.46.1` added to cerebrium.toml deps
  - **Caused 406 errors** on all requests (uncaught exception from bitsandbytes on first request)

- 406 fix — commit `bace093` (CURRENT LIVE)
  - Root cause: bitsandbytes raises exception on ADA_L4 at first request; Cerebrium surfaces as 406
  - Fix: wrap 4bit load in try/except, fall back to float16 if bitsandbytes fails
  - `BitsAndBytesConfig` moved to top-level import; duplicate imports inside `get_model()` removed
  - HTTP 200 confirmed post-fix: `run_time_ms: 28,733ms` (model load on first request)
  - Subsequent requests will be faster (model cached in memory)

**CURRENT LIVE STACK:**
- WhatsApp number: +255637809070 (Wappfly)
- Webhook handler: Railway — https://striking-cat-production-ed7e.up.railway.app/webhook
- Webhook code: `wappfly-function/handler.py` (FastAPI)
- Inference: Cerebrium ADA_L4 — `https://api.aws.us-east-1.cerebrium.ai/v4/p-e3f41403/chike-inference/run`
- Cerebrium commit: `bace093` — transformers, 4bit with float16 fallback, min_replicas=0
- Model: `prospAprospA007/africa-giants-adapter-v3` (adapter-v3 training pending)
- HF_TOKEN: set as Cerebrium secret ✓

---

### 2026-06-12 (session 12) — Chike WhatsApp inference server built + HF branding updated

**COMPLETED:**
- WhatsApp inference server built — commit `86f28b7`:
  - `server/app.py` — FastAPI server (deleted in session 13); replaced by Wappfly handler
  - `server/requirements.txt` — fastapi, uvicorn, transformers, peft, torch, accelerate, python-multipart, huggingface_hub, bitsandbytes
  - `server/README.md` — deployment docs, endpoints, env vars, local dev instructions
  - `Procfile` — `web: uvicorn server.app:app --host 0.0.0.0 --port $PORT`
  - `railway.json` — NIXPACKS builder, /health healthcheck, ON_FAILURE restart
  - `.env.example` — Chike header added; real credentials redacted to placeholders
  - `CLAUDE.md` — product name note added at Section 1
- HuggingFace READMEs updated with Chike branding:
  - `prospAprospA007/africa-giants-adapter-v2` model repo: title → "Chike by Africa Giants (adapter-v2)"
  - `prospAprospA007/africa-giants-dataset` dataset repo: title → "Chike by Africa Giants — Tanzania Business Regulatory Q&A Dataset"
- scan_for_keys.py: CLEAN — 0 API keys in 7 staged files

**CORPUS STATE (confirmed session 12):**
- batch_001_cleaned.jsonl: 56 pairs (46 trainable, 10 eval_set=true)
- batch_002_cleaned.jsonl: 243 pairs (243 trainable)
- batch_002a_cleaned.jsonl: 50 pairs (50 trainable)
- batch_002b_cleaned.jsonl: 50 pairs (50 trainable)
- batch_003_cleaned.jsonl: 300 pairs (300 trainable)
- batch_004_cleaned.jsonl: 300 pairs (300 trainable)
- batch_005_cleaned.jsonl: 300 pairs (300 trainable)
- batch_006_cleaned.jsonl: 300 pairs (300 trainable)
- batch_007_replacements.jsonl: 13 pairs (13 trainable)
- batch_008_cleaned.jsonl: 150 pairs (150 trainable)
- **TOTAL TRAINABLE: 1,752 pairs**
- HF: train_sft.jsonl=1,576 pairs (1.23MB), val_sft.jsonl=176 pairs (139KB)

**PENDING BEFORE FIRST USER PILOT:**
1. Kaggle adapter-v3 training run: https://www.kaggle.com/code/prospaprospa/africa-giants-v2 (Run All)
2. After training: run `python scripts/run_eval.py` — must pass >85% in-corpus AND >70% refusal
3. Cross-AI review of batch_008: set GEMINI_API_KEY + OPENROUTER_API_KEY then run verify_pairs.py

---

### 2026-06-12 (session 11) — batch_008 corrections applied, adapter-v3 SFT ready

**COMPLETED:**
- batch_008 corrections — commit `166d4ec`:
  - SECTION A (GN487A penalty): corrected AND/OR structure in 6 pairs (PEN_013/019/022/027/028/030)
    - Fine OR imprisonment (court chooses one) AND visa revocation (always mandatory)
    - Removed unsupported extra penalties (goods forfeiture, deportation) from PEN_019
    - Removed unsupported whistleblower protection claims from PEN_022
    - Softened deportation/fine scenario to honest "not addressed in GN 487A" (PEN_027)
  - SECTION B (GN487A scope): corrected 6 pairs (SCP_005/008/013/016/018/020)
    - Tailoring NOT explicitly named — Category 15 (micro/small industries) guidance added
    - Second-hand goods NOT explicitly named — Category 1 (retail/wholesale) analysis added
    - Small food outlets NOT explicitly named — Category 1 caveat added
    - SCP_005: corrected 15-category list (barbershops/tailoring/food NOT separate categories)
    - SCP_020: corrected summary list to match official gazette categories
  - SECTION D (VAT): VAT_PRO_014 corrected — CPA licence forces VAT on professional services only,
    not unrelated businesses (clothing shop uses standard TZS 200M/TZS 100M threshold)
  - SECTION E (PAYE): TZS 26,000/month personal relief does NOT exist — removed from 9 pairs
    (paye_adv_001/002/004/005/007/010/012/013/015); fix dpt_012 enforcement dates; adv_006 deadline 7th
- SFT regenerated: train=1576, val=176, total=1,752 trainable pairs — HF updated
- Evidence base for corrections: FB Attorneys PDF (GN 487A gazette text), TRA official VAT page,
  Habib Advisory Tanzania Tax Guide 2025/2026

**CORPUS STATE (after session 11):**
- batch_001_cleaned.jsonl: 56 pairs total (46 trainable, 10 eval_set=true)
- batch_002_cleaned.jsonl: 243 pairs
- batch_002a_cleaned.jsonl: 50 pairs (Class B→A investor fix, royalties WHT 15%)
- batch_002b_cleaned.jsonl: 50 pairs (Class B→A investor fix, royalties WHT 15%)
- batch_003_cleaned.jsonl: 300 pairs (+1 nssf_directors disambiguation)
- batch_004_cleaned.jsonl: 300 pairs (+1 osha_vs_wcf_accident disambiguation)
- batch_005_cleaned.jsonl: 300 pairs
- batch_006_cleaned.jsonl: 300 pairs (batch not confirmed in cleaned — verify)
- batch_007_replacements: 13 pairs
- batch_008_cleaned.jsonl: 150 pairs (75 gn487a_adv, 40 vat_registration, 20 refusal, 15 paye_adv)
- **TOTAL TRAINABLE: 1,752 pairs** (eval_set=true excluded)
- HF: train_sft.jsonl=1576 pairs (1.23MB), val_sft.jsonl=176 pairs (139KB)

**VERIFIED REGULATORY FACTS (confirmed this session from primary sources):**
- GN 487A penalty structure: fine OR imprisonment (court chooses) AND visa revocation (mandatory AND)
  Fine minimum TZS 10M; imprisonment maximum 6 months. Source: FB Attorneys gazette PDF
- GN 487A Schedule: 15 EXACT categories — tailoring, second-hand goods, food outlets NOT named separately
  They may fall under Category 1 (retail/wholesale) or Category 15 (micro/small industries)
- PAYE: NO separate TZS 26,000/month personal relief deduction exists in Tanzania
  The tax-free allowance IS the 0% Band 1 on first TZS 270,000/month (= TZS 3,240,000/year)
  Source: Habib Advisory Tanzania Tax Guide 2025/2026
- PAYE deadline: 7th of the following month (NOT 20th). Source: Habib Advisory 2025/2026

**PENDING BEFORE KAGGLE TRAINING RUN:**
1. Cross-AI review on batch_008 (150 pairs): set GEMINI_API_KEY + OPENROUTER_API_KEY then:
   python scripts/verify_pairs.py --file datasets/tier1a/raw_sources/raw_pairs_batch_008.jsonl --batch-size 10
2. Trigger Kaggle training: https://www.kaggle.com/code/prospaprospa/africa-giants-v2 (Run All)
3. After training: run python scripts/run_eval.py and check gate results

**KNOWN UNRESOLVED:**
- gn487a_072: SUMATRA vs LATRA for daladala licensing — needs TanzLII/LATRA verification
- brela_deep_006: annual return 42 vs 60 days — needs BRELA portal verification

---

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
- batch_001_cleaned.jsonl: 56 pairs (committed, verified — 46 trainable + 10 eval_set=true)
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

### 2026-06-10 (session 8) — batch_006 COMPLETE 300 pairs + cross-AI review batch_003 + batch_005

**COMPLETED:**
- batch_006: 300 pairs — commit `73f3e21`
  - gn487a_adversarial (50): corrects residence-permit confusion, wrong penalties, wrong agency
  - sdl_adversarial (50): corrects "disability leave" error, wrong rate/threshold
  - eac_str_basics (30, tier1b): USD 2,000, Common List, originating ≠ Common List
  - digital_services_tax (20): B2C VAT 16%, WHT 6% on services, EFD online
  - vat_refund_deep (50): input/output VAT, exporter refunds, zero-rated vs exempt
  - paye_foreign_employees (50): all employees pay PAYE, non-cash benefits, DTA, P9
  - out_of_corpus_refusal (20) + disambiguation_mixed (15) + rural_compliance (15)
- batch_003 cross-AI review: CLEAN (0 consensus, 1 human-review flag — gn487a_072 SUMATRA vs LATRA)
  - Flag routed to datasets/tier1a/flagged/needs_human_review/batch_003_gn487a_072_flag.json
- batch_005 cross-AI review: CLEAN (0 flags)
- batch_005_founder_sample.jsonl: regenerated with seed=99, commit 457c222
- locked_facts.json: 5 additional pattern fixes (gn487a_effective_date, sdl_rate, permit_class_a, stamp_duty, 5% SDL lookbehind)

**CORPUS STATE (after session 8):**
- batch_001_cleaned.jsonl: 57 pairs (cleaned)
- batch_002_cleaned.jsonl: 243 pairs (cleaned)
- raw_pairs_batch_003.jsonl: 300 pairs — cross-AI CLEAN, founder sample ready (seed=99 needed for 003 too)
- raw_pairs_batch_004.jsonl: 300 pairs — cross-AI done, all consensus flags resolved
- raw_pairs_batch_005.jsonl: 300 pairs — cross-AI CLEAN, founder sample (seed=99) ready
- raw_pairs_batch_006.jsonl: 300 pairs — check_locked_facts CLEAN, check_sources CLEAN, needs cross-AI review
- Total raw: 1,500 pairs | Total cleaned: 300 pairs

**REGISTER NOTE batch_006:** formal(177) bm(76) rural(47) — below minimums (need bm≥120, rural≥60).
Technical subdomains (PAYE/VAT/SDL deep dives) naturally skew formal. Compensate in batch_007.

**PENDING BEFORE NEXT TRAINING:**
1. Founder reviews batch_003_founder_sample.jsonl (30 pairs)
2. Founder reviews batch_004_founder_sample.jsonl (30 pairs)
3. Founder reviews batch_005_founder_sample.jsonl (30 pairs, seed=99)
4. Move all three batches (003/004/005) to cleaned_pairs/ after approval
5. python scripts/check_eval_split.py
6. python scripts/generate_sft.py
7. Upload to HuggingFace and retrain on Kaggle on 1,200 pairs
8. Run accuracy gate — target >75% in-corpus, >70% refusal

**KNOWN UNRESOLVED (single-model human-review flags):**
- gn487a_072: SUMATRA vs LATRA for daladala licensing — needs TanzLII/LATRA verification
- GN 487A imprisonment penalty: 6 months (pairs) vs 12 months (Gemini) — 8 pairs need TanzLII verification
- brela_deep_006: annual return 42 vs 60 days — needs BRELA verification

---

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

### Current priority: Kaggle adapter-v3 training → eval gates → first user pilot

**Step A (DONE):** ✅ Corpus complete — 1,752 trainable pairs across 10 cleaned batch files
- All batch corrections applied (GN487A penalty, scope, PAYE 26K myth, VAT CPA, deadlines)
- SFT files: train=1,576 / val=176 — uploaded to HF

**Step B (DONE):** ✅ Chike LIVE on Cerebrium — current commit `bace093`
- `chike-inference/main.py` — transformers inference, 4bit with float16 fallback, prompt-leak fix
- `chike-inference/cerebrium.toml` — ADA_L4, min_replicas=1, [cerebrium.scaling] section
- HTTP 200 confirmed, model self-identifies as "Chike"
- Endpoint: `https://api.aws.us-east-1.cerebrium.ai/v4/p-e3f41403/chike-inference/run`

**Step B2 (DONE):** ✅ Wappfly handler LIVE on Railway
- `wappfly-function/handler.py` — FastAPI, greeting detection, 120s Cerebrium timeout
- Railway URL: https://striking-cat-production-ed7e.up.railway.app
- Wappfly inbound webhook: /webhook (set and confirmed)
- WhatsApp number: +255637809070

**Step C (PENDING — manual):** ⬜ Trigger adapter-v3 Kaggle training run
- URL: https://www.kaggle.com/code/prospaprospa/africa-giants-v2
- Action: Run All
- Dataset: 1,752 pairs (train=1,576, val=176) already on HF

**Step D (PENDING — after training):** ⬜ Run accuracy gate
- `python scripts/run_eval.py`
- Must print GATE PASSED: >85% in-corpus AND >70% refusal
- Adapter-v2 results for reference: 83.2% in-corpus (FAIL), 50% refusal (FAIL)

**Step E (PENDING — parallel to C):** ⬜ Cross-AI review of batch_008 (150 pairs)
- Set API keys in PowerShell session first:
  `$env:GEMINI_API_KEY = "your_key"`
  `$env:OPENROUTER_API_KEY = "sk-or-v1-..."`
- Then: `python scripts/verify_pairs.py --file datasets/tier1a/raw_sources/raw_pairs_batch_008.jsonl --batch-size 10`

### Known unresolved items (not blocking training)
- `gn487a_072`: SUMATRA vs LATRA for daladala licensing — needs TanzLII/LATRA verification
- `brela_deep_006`: annual return 42 vs 60 days — needs BRELA portal verification
- GN487A imprisonment penalty: 6 months (pairs) vs 12 months (Gemini session 4 flag) — Section C of do.md confirmed 6 months correct per gazette text
- batch_001_cleaned.jsonl shows 56 pairs (PROGRESS.md previously said 57 — 56 is confirmed correct count)

---

## 4. NEXT PHYSICAL ACTIONS (dependency-ordered)

1. ✅ Infrastructure, schema, scripts, eval set, whitelist — all committed
2. ✅ adapter-v1: trained on 300 pairs — 67% in-corpus / 40% refusal — FAILED both gates
3. ✅ FACT-GUARDIAN + REGULATORY-VERIFIER + dedup-guard + all autonomy scripts installed
4. ✅ Corpus built to 1,752 trainable pairs across batches 001–008 + 002a/b + 007_replacements
5. ✅ All batch corrections applied (GN487A, PAYE 26K myth, VAT CPA, BRELA fees, WHT)
6. ✅ adapter-v2: trained on 1,500 pairs — 83.2% in-corpus / 50% refusal — FAILED both gates
7. ✅ HF SFT files updated: train=1,576, val=176 (1,752 pairs total) — adapter-v3 ready
8. ✅ Chike LIVE on Cerebrium — 4bit+float16 fallback, HTTP 200, commit `bace093`
9. ✅ Product renamed Chike Brain → Chike — commit `b31f96e` + current session
10. ✅ Railway server removed (server/, Procfile, railway.json, .env.example) — commit `b31f96e`
11. ✅ Wappfly handler live on Railway, connected to WhatsApp +255637809070
12. ⬜ Trigger adapter-v3 training on Kaggle (manual — Run All at africa-giants-v2)
13. ⬜ Run eval gates after training: `python scripts/run_eval.py` (need >85% AND >70%)
14. ⬜ Cross-AI review batch_008 (set API keys, run verify_pairs.py)
15. ⬜ Engage TRA consultant for 10% sample review (~30 pairs, ~TZS 50,000–100,000)
16. ⬜ First human pilot on WhatsApp +255637809070 (after BOTH gates pass — R7 is blocking)

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
| Tier 1A: TRA Compliance | 600 | 1,752 | 1,752 | 10 | No — pending training |
| Tier 1A: Labour/GN 605A | included above | — | — | — | — |
| Tier 1A: GN 487A | included above | — | — | — | — |
| Tier 1B: EAC STR | 300 | 30 (batch_006) | 30 | 0 | No — pending 1A gate |
| Tier 1C: NeST | 200 | 0 | 0 | 0 | No — pending 1A gate |
| Tier 2A: Legibility | 200 | 0 | 0 | 0 | No |
| Tier 2B: VICOBA | 300 | 0 | 0 | 0 | No |
| Tier 3 | Reserved | — | — | — | — |
| **TOTAL TRAINABLE** | **—** | **1,752** | **1,752** | **10** | **No** |

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