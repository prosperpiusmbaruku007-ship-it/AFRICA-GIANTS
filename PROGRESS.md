# Africa Giants — Project Progress

Last updated: 2026-06-21

## Current State
- Live adapter: africa-giants-adapter-v9 (Cerebrium still serving v6 — update overdue)
- Live on WhatsApp: +255637809070 via Wappfly
- Dataset: 2,662 pairs across 13 batches (batches 001–013), all SFT-format verified
- locked_facts.json: 82+ entries
- Training script: kaggle/train_ddp.py — ready to run as `python3 train_ddp.py`

## Gate History
| Version | In-corpus | Refusal | Gate | Notes |
|---|---|---|---|---|
| v6 | ~74% | 50% | FAIL | baseline |
| v7 | 79.5% | 80% | FAIL | refusal gate passed for first time |
| v8 | 82.1% | 70.0% | FAIL | closest to gate; refusal at threshold |
| v9 | 80.0% | 40.0% | FAIL | rebalanced dataset hurt refusal (stop-after-redirect not trained) |
| **v10** | pending | pending | pending | full 2,662-pair dataset, r=128, single GPU |

## v9 Gate Results (gate_001_results.json on HF adapter-v9)
Total: 200 questions | Pass: 160 | Fail: 40 | **Overall: 80.0%** — Gate FAILED

| Subdomain | Pass/Total | % | Status |
|---|---|---|---|
| efd_compliance | 19/20 | 95.0% | ✓ |
| brela_registration | 14/15 | 93.3% | ✓ |
| nssf_contributions | 23/25 | 92.0% | ✓ |
| vat_withholding | 18/20 | 90.0% | ✓ |
| gn487a | 30/40 | 75.0% | ✗ |
| osha_registration | 12/15 | 80.0% | ✗ |
| sdl_compliance | 20/25 | 80.0% | ✗ |
| out_of_corpus | 4/10 | 40.0% | ✗ |
| vat_registration | 20/30 | 66.7% | ✗ |

### v9 Root Cause Analysis
- **vat_registration (10 failures):** arithmetic on thresholds, rolling 12-month definition, zero-rated vs exempt disambiguation, qualifying buyer definition
- **gn487a (10 failures):** full legal name never stated, effective date hallucinated (28+29 Jul), "mgeni" definition inverted, marriage exception wrong (ndoa haibadilishi hadhi), enforcement exercise dates wrong, enforcement body hedged
- **sdl_compliance (5 failures):** WCF rate wrong (20% instead of 0.5%), SDL threshold (10 employees) ignored, SDL+PAYE same deadline wrong, GN 605B cited (doesn't exist)
- **out_of_corpus (6 failures):** refusal-then-elaborate pattern — model says "nje ya maarifa yangu" then explains anyway; eval_191 (PAYE TZS 800K) misclassified as out-of-corpus
- **osha_registration (3 failures):** >50 employee safety officer requirement missed, late registration first step wrong

## Pending Tasks — Immediate
1. **Run v10 training** — upload kaggle/train_ddp.py to Kaggle, run as `python3 train_ddp.py`
   - Dataset: prospaprospa007/africa-giants-dataset (2,395 train / 267 val)
   - Model: McGill-NLP/AfriqueLlama-8B, r=128, alpha=128, fp16
   - Push target: prospaprospa007/africa-giants-adapter-v10
2. **Write batch_014** — correction pairs for v9 failures (see breakdown above):
   - Priority 1: VAT arithmetic worked examples (15–20 pairs), rolling 12-month definition
   - Priority 2: GN487A precision pairs — full name, single date, mgeni definition, ndoa exception
   - Priority 3: Out-of-corpus clean-stop pairs (refusal only, no elaboration) — 20+ pairs
   - Priority 4: SDL/WCF precision — 0.5% rate, 10-employee threshold, same-day deadline
   - Move eval_191 (PAYE 800K) from refusal gate to accuracy gate
3. **Fix repetition loop in production** — chike-inference/main.py lines 109–116 missing `repetition_penalty=1.1` — identified but not yet applied
4. **Update Cerebrium** to serve adapter-v9 (or wait for v10)

## Dataset State
- Source files: 13 batches in `datasets/tier1a/cleaned_pairs/`
  - Batches 001–008: old 18-field schema (question_sw/answer_sw) — converted by generate_sft.py
  - Batches 009–013: SFT format (instruction/input/output/system) — direct use
- SFT files (current, on HuggingFace):
  - train_sft.jsonl: 2,395 pairs
  - val_sft.jsonl: 267 pairs
  - Total loaded: 2,662 (10 excluded as eval_set:true)
- Generation: `python scripts/generate_sft.py` — always use this, never raw glob from cleaned_pairs
- Balanced files retained locally: `sft/train_sft_balanced.jsonl` (1,658) / `sft/val_sft_balanced.jsonl` (183) — used for v9, NOT on HuggingFace

## Training Script
- File: `kaggle/train_ddp.py`
- Run: `python3 train_ddp.py` (Unsloth handles multi-GPU natively — no torchrun)
- Config: LORA_RANK=128, LORA_ALPHA=128, MAX_SEQ_LENGTH=2048, 2 epochs, lr=2e-4
- Previous LoRA (v9-lora, r=64) will fail to load — EXPECTED, v10 starts fresh at r=128
- Pushes: merged 16-bit to adapter-v10, LoRA-only to adapter-v10-lora
- Dataset assertion: `_train_count >= 2300`

## Scorer Fixes Applied (eval notebook — Kaggle africa_giants_eval.ipynb)
- `la` removed from NO_WORDS in yes_no scorer (word boundary issue)
- `Thibitisha na` citation strip in definition/procedure scorer
- Both fixes in eval notebook Cell 2 only — NOT in run_eval.py (local script)

## Known Issues / Technical Debt
- `chike-inference/main.py`: missing `repetition_penalty=1.1` — production model repeats "Thibitisha na TRA" 8–9× before truncation
- Cerebrium still serving v6 adapter — v9 weights exist on HF but not deployed
- `run_eval.py` (local) does not have the scorer fixes that the Kaggle eval notebook has
- eval_191 (PAYE TZS 800K) misclassified in refusal gate — should be accuracy gate

## Dataset Naming Convention
- Batches 001–008: `batch_NNN_cleaned.jsonl`
- Batches 009–013: `cleaned_pairs_batch_NNN.jsonl`
- Always use `glob('datasets/tier1a/cleaned_pairs/*.jsonl')` — never hardcode prefix
- Always use `generate_sft.py` to build SFT files — it handles both schemas

## HuggingFace Repos
- africa-giants-adapter-v9: LIVE (merged 16-bit, gate results uploaded)
- africa-giants-adapter-v9-lora: LIVE (r=64 LoRA-only — NOT compatible with v10 r=128)
- africa-giants-adapter-v10: pending (v10 training not yet run)
- africa-giants-adapter-v10-lora: pending
- africa-giants-dataset: 2,662 pairs (train 2,395 / val 267)

## Infrastructure
- Cerebrium: serving adapter-v6 (STALE — needs update)
- Wappfly: +255637809070
- Kaggle: training notebook (africa_giants_V2.ipynb) + eval notebook (africa_giants_eval.ipynb)
- GitHub: main branch, HEAD at 496850d
- HuggingFace token: Kaggle secret `AFRICA_GIANTS`

## Recent Commits
- 496850d: train_ddp.py r=128 single GPU
- 9ef505b: fix train_ddp.py python3 not torchrun
- acfc506: dataset full 2662 pairs schema verified
- 36edbae: add train_ddp.py DDP v10 script
- ca17114: dataset balanced 1841 pairs v9
- 533140d: batch_013 135 correction pairs
- 67769c4: session close PROGRESS.md v7 results
