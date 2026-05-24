# PROGRESS LOG — AFRICA-GIANTS
## Last Updated: 2026-05-24 (BLOCKER: secret not attached + Kaggle API ignores T4 request)

## Project Info
- Repo: https://github.com/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS
- Kaggle account: prospaprospa
- Kaggle notebook: https://www.kaggle.com/code/prospaprospa/africa-giants-trainer
- Base model: McGill-NLP/AfriqueLlama-8B
- HF secret in Kaggle named: AFRICA_GIANTS

## Completed Pipeline Steps
- data_pipeline: ✅ DONE
- hf_upload: ✅ DONE
- kaggle_trigger: ❌ BLOCKED — two manual actions required (see below)
- kaggle_monitor: ⚠️ WILL SKIP (KGAT token lacks kernels.get scope)
- evaluate: ❌ WAITING (no trained model on HF yet)
- deploy: ❌ NOT STARTED

## Current Blockers (confirmed from live kernel logs 2026-05-24)

### Blocker 1: Kaggle API ignores T4 accelerator request — P100 assigned every time
- `"accelerator": "nvidiaTeslaT4"` and `"nvidiaTeslaT4x2"` in kernel-metadata.json are IGNORED
- Kaggle's `kernels_push()` API does NOT update GPU type for existing kernels
- Kaggle keeps assigning P100 (sm_60) regardless
- P100 has NO compatible torch wheel: `torch==2.1.2+cu118` never existed at the whl index
  (earliest cu118 is 2.2.0+cu118, all cu118 versions require sm_70+)
- Pre-installed torch 2.10+cu128 also requires sm_70+ minimum
- P100 training is completely impossible in Kaggle's current environment
- FIX: user must manually run the kernel from Kaggle web UI with T4 selected
  (web UI GPU selection IS honored; API push is not)

### Blocker 2: AFRICA_GIANTS secret not attached to kernel → HTTP 400
- `user_secrets.get_secret("AFRICA_GIANTS")` returns HTTP 400 Bad Request
- The secret exists in Kaggle account but has NOT been toggled ON for this kernel
- Must be done manually in the Kaggle web UI (Add-ons → Secrets)

## MANUAL ACTIONS REQUIRED — DO THESE IN ORDER

### Action 1 — GPU: confirmed T4 x2 in web UI ✅ (but API push overrides — see Action 3)

### Action 2 — Attach AFRICA_GIANTS secret to kernel (STILL PENDING ❌)
1. Go to https://www.kaggle.com/code/prospaprospa/africa-giants-trainer
2. Click Edit
3. In the right sidebar → Add-ons → Secrets
4. Find "AFRICA_GIANTS" and toggle it ON
5. If it's not listed, first create it:
   - kaggle.com → Account (top right) → Settings → Secrets → Add new secret
   - Label: AFRICA_GIANTS  Value: your HuggingFace write token (hf_xxx...)
6. Save

### Action 3 — Run kernel manually from web UI (NOT via python run.py train)
After Action 2, in the Kaggle web UI:
1. Go to https://www.kaggle.com/code/prospaprospa/africa-giants-trainer
2. Confirm Accelerator = GPU T4 x2 (Settings panel)
3. Click Run All (top toolbar)
The web UI will use T4 x2 as shown. The API push does not.

After the kernel completes (≈30-60 min), run locally to finish the pipeline:
```
python run.py train
```
(data_pipeline + hf_upload are done; the orchestrator will skip straight to evaluate+deploy)

## All Fixes Applied
- Fixed Kaggle 401 — updated KGAT key in .env and kaggle.json
- Fixed kernel username — was prospAprospA007 → prosperpiusmbaruku007
- Fixed KaggleApiExtended → new kaggle API style
- Fixed kernel_status → Kaggle SDK 2.x enum
- Fixed fsspec dependency conflicts
- Added AFRICA_GIANTS HF secret to Kaggle (but still need to attach to kernel)
- Fixed P100 incompatibility — notebook now GPU-agnostic (Unsloth on T4, BitsAndBytes on P100)
- Fixed BaseImageProcessor import error — removed bad transformers version pin
- Fixed get_chat_template import — resilient to old/new unsloth API paths
- Fixed Windows cp1252 log reader — scripts/read_kaggle_logs.py (also fixed missing import subprocess)
- Removed P100 fail-fast — replaced with warning print so BitsAndBytes path can attempt
- Changed accelerator to "nvidiaTeslaT4x2" in kernel metadata (API still ignores it)
- Added [bracket] diagnostic prints to all notebook cells
- Fixed broken torch==2.1.2+cu118 install in P100 path (that version never existed at whl index)

## Tech Stack
- Training: Kaggle free GPU (T4 x2 required now — P100 sm_60 no longer supported)
- Base model: McGill-NLP/AfriqueLlama-8B (Llama 3.1 + 20 African languages)
- Fine-tuning: Unsloth + QLoRA (T4/V100/A100 only)
- Deployment: HuggingFace Spaces + Inference API
- Languages: Swahili + English
- Purpose: AI for Tanzanian businesses
