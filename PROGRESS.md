# PROGRESS LOG — AFRICA-GIANTS
## Last Updated: 2026-05-24

## Project Info
- Repo: https://github.com/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS
- Kaggle account: prospaprospa
- Kaggle notebook: https://www.kaggle.com/code/prospaprospa/africa-giants-trainer
- Base model: McGill-NLP/AfriqueLlama-8B
- HF secret in Kaggle named: AFRICA_GIANTS

## Completed Pipeline Steps
- data_pipeline: ✅ DONE
- hf_upload: ✅ DONE
- kaggle_trigger: ✅ DONE
- kaggle_monitor: ⚠️ SKIPPED (KGAT token lacks kernels.get scope)
- evaluate: ❌ WAITING (no trained model on HF yet)
- deploy: ❌ NOT STARTED

## Root Causes Found (from actual log read)

### Crash 1: P100 assigned — PyTorch no longer supports sm_60
- Kaggle assigned P100 (sm_60) instead of T4 (sm_75)
- `pip install torch==2.1.2+cu118` FAILS — that version was removed from PyPI
  (only 2.2.0+cu118 and higher remain, all require sm_70+)
- Pre-installed torch 2.10+cu128 loads but also requires sm_70+ minimum
- FIXED: notebook now fails immediately with instructions to switch GPU to T4
- FIXED: kernel metadata now requests `"accelerator": "nvidiaTeslaT4"`

### Crash 2: Kaggle secret AFRICA_GIANTS → HTTP 400
- `user_secrets.get_secret("AFRICA_GIANTS")` returns HTTP 400 Bad Request
- The secret exists in your Kaggle account but has NOT been attached to this kernel
- MANUAL ACTION REQUIRED (see next steps)

## Manual Actions Required (do these in Kaggle web UI)

### Action 1 — Change GPU to T4
1. Go to https://www.kaggle.com/code/prospaprospa/africa-giants-trainer
2. Click Edit
3. In the right sidebar → Settings → Accelerator → select "GPU T4 x2"
4. Save

### Action 2 — Attach AFRICA_GIANTS secret to the kernel
1. Go to https://www.kaggle.com/code/prospaprospa/africa-giants-trainer
2. Click Edit
3. In the right sidebar → Add-ons → Secrets
4. Find "AFRICA_GIANTS" and toggle it ON
5. If it's not listed, first create it:
   - kaggle.com → Account (top right) → Settings → Secrets → Add new secret
   - Label: AFRICA_GIANTS  Value: your HuggingFace write token (hf_xxx...)
6. Save

### Action 3 — Trigger the kernel
After both actions above, run:
```
python run.py train
```
Or trigger manually from the Kaggle web UI → Run All.

## All Fixes Applied
- Fixed Kaggle 401 — updated KGAT key in .env and kaggle.json
- Fixed kernel username — was prospAprospA007 → prosperpiusmbaruku007
- Fixed KaggleApiExtended → new kaggle API style
- Fixed kernel_status → Kaggle SDK 2.x enum
- Fixed fsspec dependency conflicts
- Added AFRICA_GIANTS HF secret to Kaggle (but still need to attach to kernel)
- Fixed P100 incompatibility — notebook now GPU-agnostic
- Fixed BaseImageProcessor import error — removed bad transformers version pin
- Fixed get_chat_template import — resilient to old/new unsloth API paths
- Fixed Windows cp1252 log reader — scripts/read_kaggle_logs.py now works
- Added early P100 fail-fast — clear error message when sm_60 assigned
- Added "accelerator": "nvidiaTeslaT4" to kernel metadata
- Added [bracket] diagnostic prints to all notebook cells
- Pinned trl<0.16 for BitsAndBytes path (P100 fallback)

## Tech Stack
- Training: Kaggle free GPU (T4 x2 required now — P100 sm_60 no longer supported)
- Base model: McGill-NLP/AfriqueLlama-8B (Llama 3.1 + 20 African languages)
- Fine-tuning: Unsloth + QLoRA (T4/V100/A100 only)
- Deployment: HuggingFace Spaces + Inference API
- Languages: Swahili + English
- Purpose: AI for Tanzanian businesses
