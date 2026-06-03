# PROGRESS LOG — AFRICA-GIANTS
## Last Updated: 2026-06-03

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

**Pre-Stage | Eval Set Complete — 200 questions committed. Awaiting accuracy gate run.**

---

## 2. LAST VERIFIED COMPLETED (with dates)

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

### Immediate — Complete the eval set (next Claude Code session)

The /do command in .claude/commands/do.md contains the exact instruction.
Run claude then /do to continue.

Claude Code must:
1. Read CLAUDE.md, PROGRESS.md, docs/reference_narrative.md,
   datasets/tier1a/cleaned_pairs/batch_001_cleaned.jsonl,
   and eval/accuracy_gate/eval_questions_001.jsonl
2. APPEND 65 questions to eval/accuracy_gate/eval_questions_001.jsonl
   starting from eval_136 — do not overwrite existing content
3. Write gn487a (eval_136–175), osha_registration (eval_176–190),
   out_of_corpus (eval_191–200)
4. Run self-check on full 200-question file
5. Show first 3 and last 3 new questions for founder review
6. Do NOT commit — wait for founder confirmation

### Open items on training pairs (not blocking eval set)
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
8. ⏳ Build 200-question eval set — 135 of 200 done, 65 remaining (2026-06-03)
9. ⬜ Founder reviews eval set quality (first 5 + last 5 questions)
10. ⬜ Commit eval set to GitHub after founder approval
11. ⬜ Engage TRA consultant for 10% training pair sample review
12. ⬜ Run accuracy gate: python scripts/run_eval.py
    Target: >85% in-corpus accuracy AND >70% out-of-corpus refusal
13. ⬜ If gate passes: prepare first human pilot on WhatsApp
14. ⬜ Continue building Tier 1A toward 200 pairs total
    (add PAYE, minimum wages GN 605A, work permits, withholding tax on imports)

---

## 5. BLOCKED ITEMS

| Blocker | Unblocked by |
|---------|-------------|
| Accuracy gate run | Eval set complete + founder approval |
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
| **TOTAL** | **1,600** | **57** | **0** | **10** | **No** |

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