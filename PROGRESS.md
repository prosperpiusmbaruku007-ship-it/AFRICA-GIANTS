# PROGRESS LOG — AFRICA-GIANTS
## Last Updated: 2026-06-01

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

**Pre-Stage | Dataset Infrastructure Build**
Directory structure created. Schema and whitelist written. Validation scripts created.
Next: write first 50 verified Tier 1A compliance pairs from TRA.go.tz.

---

## 2. LAST VERIFIED COMPLETED (with dates)

### Training Pipeline (May 2026)
- Kaggle training pipeline: debugged and working
- EOS token root cause found: AfriqueLlama tokenizer_config.json sets `eos_token="<EOS_TOKEN>"` by default on every load
- All 5 EOS fixes applied and confirmed working in `scripts/fixed_cell_train.py`
- Training run completed: loss 3.177 → 1.574 over 10 steps; val loss 1.371 — PASSED threshold 2.5 ✓
- Adapter pushed to HuggingFace: `prospaprospa007/africa-giants-adapter-v1`
- Runtime: 41.1 seconds on Tesla T4 (Unsloth active)
- New kernel confirmed active: cell ID 648585292 (old 2510264585 retired)

### Research and Strategy (May–Jun 2026)
- 8 research iterations completed; citation laundering pattern documented
- All domain decisions locked (see Section 6)
- Reference narrative written: docs/reference_narrative.md
- Domain sequence locked: Tier1A → Tier1B → Tier1C → Tier2A → Tier2B → Tier3
- Dataset construction spec locked: 18-field schema, source whitelist, pipeline gates
- TANePS → NeST correction locked across all documents

### Infrastructure (2026-06-01)
- CLAUDE.md rewritten with full behavioral contract (13 sections, all rules R1–R12)
- PROGRESS.md rewritten as living record
- Directory structure created: datasets/tier1a through tier3, eval/, schema/, sources/
- schema/pair_schema.json created — 18-field canonical contract
- sources/whitelist.json created — all approved scrape targets with decay metadata
- scripts/validate_dataset.py created — schema + whitelist enforcement, exit 1 on failure
- scripts/run_eval.py created — accuracy + refusal gate runner, prints GATE PASSED/FAILED
- .gitkeep files added to all empty dataset directories

### Previously Applied Fixes — DO NOT REDO
1. ✅ Kaggle 401 fixed
2. ✅ Kernel username fixed
3. ✅ KaggleApiExtended updated
4. ✅ kernel_status fixed
5. ✅ fsspec conflicts handled
6. ✅ AFRICA_GIANTS HF token in Kaggle
7. ✅ GPU-agnostic notebook
8. ✅ BaseImageProcessor fixed
9. ✅ evaluation_strategy → eval_strategy
10. ✅ tokenizer → processing_class
11. ✅ max_seq_length removed from SFTConfig
12. ✅ SFTTrainer rewritten for TRL 0.24.0
13. ✅ P100 fail-fast removed
14. ✅ encoding=utf-8 everywhere
15. ✅ device_map fixed
16. ✅ get_chat_template removed
17. ✅ Old cached kernel replaced
18. ✅ EOS token root cause found and fixed
19. ✅ Training completed successfully
20. ✅ Adapter pushed to HuggingFace

---

## 3. ACTIVE WORK

Building dataset infrastructure. Directories created. Schema and whitelist written.
Scripts validated (run returns 0 pairs, 0 errors — correct for empty state).
Ready to begin writing Tier 1A pairs from TRA.go.tz.

---

## 4. NEXT PHYSICAL ACTIONS (dependency-ordered)

1. ✅ Create all dataset directory structure
2. ✅ Create schema/pair_schema.json
3. ✅ Create sources/whitelist.json
4. ✅ Create scripts/validate_dataset.py
5. ✅ Create scripts/run_eval.py
6. ✅ Commit and push infrastructure to GitHub

7. **NEXT — Scrape and write first 50 Tier 1A pairs:**
   - Scrape: https://www.tra.go.tz/index.php/tax-information
   - Scrape: https://tanzlii.org (GN 605A full text)
   - Write 50 pairs covering: VAT registration, VAT threshold, EFD obligations,
     Finance Act 2025 withholding rates, GN 487A prohibited activities,
     GN 605A minimum wage by sector
   - Every pair in business_market register first, then formal register variant
   - Save to: datasets/tier1a/cleaned_pairs/ (JSONL, utf-8)
   - ⚠️ HUMAN ACTION REQUIRED: 10% sample (5 pairs) must be reviewed by
     a TRA-registered tax consultant before gate evaluation proceeds

8. **After 50 pairs written:**
   - Run `python scripts/validate_dataset.py` — must exit 0
   - Begin Tier 1A eval set from EY/KPMG/PKF/VELMA advisory sources
   - Target: 200 eval questions (different source family from training)

9. **After eval set built:**
   - Run `python scripts/run_eval.py`
   - Target: >85% accuracy AND >70% refusal
   - If gate fails: identify gap, add targeted pairs, re-run

---

## 5. BLOCKED ITEMS

| Blocker | Unblocked by |
|---------|-------------|
| Tier 1A expert review | Engaging a TRA-registered tax consultant (human decision) |
| Accuracy gate run | Completing Tier 1A pairs + eval set construction |
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

---

## 7. DECISIONS STILL CONTESTED (require verification before encoding)

**Tanzania tourism earnings exact figure:**
- Status: [VERIFY BEFORE USE]
- Why: Grounding context across all research iterations flagged this as unverified
- Primary source needed: Bank of Tanzania Annual Report or Tanzania Tourism Board statistics
- Action: Agent must web-search BoT official portal before citing any tourism figure
- Do not cite in any investor, government, or training pair context until verified

**Any claim from citation laundering sources (full list in CLAUDE.md Section 3):**
- Status: Facts may be real; citations were fabricated across 8 research iterations
- Action: Re-verify against CLAUDE.md Section 4 whitelist before encoding as training pair
- All such claims remain [VERIFY] until confirmed from approved source

---

## 8. DATASET STATUS TABLE

| Domain | Target pairs | Written | Verified | In eval set | Gate passed |
|--------|-------------|---------|----------|-------------|-------------|
| Tier 1A: TRA Compliance | 300 | 0 | 0 | 0 | No |
| Tier 1A: Labour/GN 605A | 200 | 0 | 0 | 0 | No |
| Tier 1A: GN 487A | 100 | 0 | 0 | 0 | No |
| Tier 1B: EAC STR | 300 | 0 | 0 | 0 | No |
| Tier 1C: NeST | 200 | 0 | 0 | 0 | No |
| Tier 2A: Legibility | 200 | 0 | 0 | 0 | No |
| Tier 2B: VICOBA | 300 | 0 | 0 | 0 | No |
| Tier 3 | Reserved | — | — | — | — |
| **TOTAL** | **1,600** | **0** | **0** | **0** | **No** |

Eval set target: 200 questions (from advisory sources — different family from training)
Accuracy gate: NOT STARTED
Refusal gate: NOT STARTED

---

## 9. SCRAPE TARGETS PIPELINE

### Tier 1A Training Sources
| URL | Source type | Content | Decay risk | Status | Last verified |
|-----|------------|---------|-----------|--------|--------------|
| https://www.tra.go.tz/index.php/tax-information | gov portal | HTML | Annual | pending | 2026-06-01 |
| https://www.tra.go.tz/index.php/filing-returns | gov portal | HTML | Annual | pending | 2026-06-01 |
| https://www.brela.go.tz | gov portal | HTML | Stable | pending | 2026-06-01 |
| https://www.nssf.or.tz | gov portal | HTML | Annual | pending | 2026-06-01 |
| https://www.osha.go.tz | gov portal | HTML | Stable | pending | 2026-06-01 |
| Tanzania Government Gazette (GN 487A, GN 605A, Finance Act 2025) | official gazette | PDF | Event-triggered | pending | 2026-06-01 |
| https://tanzlii.org (GN 605A full text) | official law | PDF | Event-triggered | pending | 2026-06-01 |

### Tier 1A Eval Sources (DIFFERENT document family from training)
| URL | Source type | Content | Decay risk | Status | Last verified |
|-----|------------|---------|-----------|--------|--------------|
| ey.com/en_tz Finance Act 2025 | tier1 advisory | PDF | Annual | pending | 2026-06-01 |
| kpmg.com/tz Tax News Flash Oct 2025 | tier1 advisory | PDF | Annual | pending | 2026-06-01 |
| pkfea.com GN 605A alert | tier1 advisory | PDF | Event-triggered | pending | 2026-06-01 |
| velmalaw.co.tz GN 487A analysis | tier1 advisory | HTML | Event-triggered | pending | 2026-06-01 |
| bowmans.com GN 487A briefing | tier1 advisory | HTML | Event-triggered | pending | 2026-06-01 |
| clydeco.com Finance Act / wage order | tier1 advisory | HTML | Annual | pending | 2026-06-01 |

### Tier 1B Training Sources
| URL | Source type | Content | Decay risk | Status | Last verified |
|-----|------------|---------|-----------|--------|--------------|
| https://www.eac.int STR instruments | official | HTML+PDF | Stable | pending | 2026-06-01 |
| https://www.comesa.int STR policy | official | PDF | Stable | pending | 2026-06-01 |
| ilo.org women cross-border traders guide | ILO official | PDF | Stable | pending | 2026-06-01 |
| unctad.org Tanzania cross-border guide | UNCTAD official | PDF | Stable | pending | 2026-06-01 |
| eabc.info STR cereals/horticulture manual | regional body | PDF | Event-triggered | pending | 2026-06-01 |

### Tier 1C Training Sources
| URL | Source type | Content | Decay risk | Status | Last verified |
|-----|------------|---------|-----------|--------|--------------|
| https://www.ppra.go.tz NeST user guides | gov portal | HTML+PDF | Annual | pending | 2026-06-01 |
| ppra.go.tz NeST Special Groups Guide 2025 | gov portal | PDF | Stable | pending | 2026-06-01 |
| Tanzania parliament portal PPA 2023 | official act | PDF | Stable | pending | 2026-06-01 |

---

## 10. DOMAIN EXPANSION TRIGGERS

Do not build these until their specific triggers fire. Premature expansion = no foundation.

**Domestic tourism operators (guesthouses, tour guides, community tourism):**
- Trigger 1: >1,000 verified Tier 1A users
- Trigger 2: tourism questions appear in compliance corpus at scale (>10% of queries)
- Primary source when triggered: Tanzania Tourism Act, Hotel Levy Act, TTB regulations

**Labour Court / employment dispute navigation:**
- Trigger 1: >500 GN 605A questions in the corpus
- Trigger 2: ELRA 2025 amendments stable for 12 months without further revision
- Primary source: CMA guidelines, ELRA 2004 as amended 2025

**Agricultural compliance and land-title:**
- Trigger 1: VICOBA corpus shows >20% agriculture-linked groups (by loan type or savings cycle)
- Trigger 2: EAC STR corpus shows significant cereal/horticulture trade questions
- Primary source: EABC STR cereals/horticulture manual (when published), Village Land Act

**Merchant and VICOBA credit scoring (Tier 3):**
- Trigger 1: 18+ months of verified merchant profile data from Tier 1A + Tier 2A
- Trigger 2: Named licensed bank partner (NMB/CRDB/TCB) with formal expression of interest
- LEGAL GATE: BoT legal opinion from Bowmans or VELMA Law on Credit Reference Bureau
  Regulations MUST be obtained before build begins. BoT may classify scoring output
  as operating a credit reference bureau — this is a blocking legal question.
- Never hold a lending license or loan book. AFRICA-GIANTS scores; the bank lends.

**Kenya expansion (first international):**
- Unlocked by: EAC cross-border corpus (Tier 1B already serves bilateral STR)
- Regulatory corpus must be rebuilt for KRA and Kenyan labour law (different from TRA)
- Language moat transfers (Swahili is Kenya's national language alongside English)
- Architecture transfers; compliance corpus does not

---

## KAGGLE ENVIRONMENT (for reference — do not change)
- trl: 0.24.0
- transformers: 5.5.0
- GPU: Tesla T4 (Unsloth active)
- Python: 3.12
- AfriqueLlama eos_token: `<|end_of_text|>` id=128001
- Dataset: 17 train / 4 eval examples
- Training: 10 steps, 2 epochs, 41.1 seconds

---

## RULES FOR THIS FILE
- Update after every session (add to Section 2, update Section 3, update Section 8 table)
- Use ISO dates (YYYY-MM-DD) for all timestamps
- Never put behavioral rules here — those belong in CLAUDE.md
- Never put architecture specs here — those belong in CLAUDE.md
- This file tracks WHAT HAS HAPPENED and WHAT IS NEXT, not HOW TO BEHAVE
