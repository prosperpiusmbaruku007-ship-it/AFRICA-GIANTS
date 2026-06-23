import json
import os
import sys
import subprocess
from pathlib import Path

HF_DATASET_REPO = 'prospAprospA007/africa-giants-dataset'
TRAIN_SFT = 'datasets/tier1a/sft/train_sft.jsonl'
VAL_SFT   = 'datasets/tier1a/sft/val_sft.jsonl'


def upload():
    hf_token = os.environ.get('HF_TOKEN', '')
    if not hf_token:
        print("[upload] HF_TOKEN not set -- cannot upload to HuggingFace")
        sys.exit(1)

    # Step 1: Rebuild SFT files from all cleaned_pairs
    print("[upload] Rebuilding SFT files ...")
    result = subprocess.run(
        [sys.executable, 'scripts/generate_sft.py'],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"[upload] generate_sft.py failed:\n{result.stderr}")
        sys.exit(1)
    print(result.stdout.strip())

    # Step 2: Assert SFT output has exactly 4 fields (source_document must be excluded)
    print("[upload] Asserting SFT schema ...")
    with open(TRAIN_SFT, encoding='utf-8') as f:
        sft_pairs = [json.loads(line) for line in f if line.strip()]
    assert all(
        set(p.keys()) == {'instruction', 'input', 'output', 'system'}
        for p in sft_pairs
    ), "SFT pairs contain unexpected fields -- check generate_sft.py fmt_pair()"
    print(f"[upload] SFT assertion passed -- {len(sft_pairs)} pairs, 4 fields each")

    with open(VAL_SFT, encoding='utf-8') as f:
        val_pairs = [json.loads(line) for line in f if line.strip()]

    # Step 3: Upload to HuggingFace
    print(f"[upload] Uploading to {HF_DATASET_REPO} ...")
    from huggingface_hub import HfApi
    api = HfApi(token=hf_token)

    api.upload_file(
        path_or_fileobj=TRAIN_SFT,
        path_in_repo='train_sft.jsonl',
        repo_id=HF_DATASET_REPO,
        repo_type='dataset',
        commit_message=f'Update train_sft.jsonl -- {len(sft_pairs)} pairs',
    )
    print(f"[upload] train_sft.jsonl uploaded ({len(sft_pairs)} pairs)")

    api.upload_file(
        path_or_fileobj=VAL_SFT,
        path_in_repo='val_sft.jsonl',
        repo_id=HF_DATASET_REPO,
        repo_type='dataset',
        commit_message=f'Update val_sft.jsonl -- {len(val_pairs)} pairs',
    )
    print(f"[upload] val_sft.jsonl uploaded ({len(val_pairs)} pairs)")

    # Step 4: Update README on HuggingFace
    total = len(sft_pairs) + len(val_pairs)
    readme = f"""# Africa Giants Dataset

Tanzanian-Swahili compliance Q&A pairs for CHIKE by Africa Giants.

## Stats
- Train pairs: {len(sft_pairs)}
- Val pairs:   {len(val_pairs)}
- Total:       {total}

## Domain
TRA (VAT, PAYE, SDL, EFD), BRELA, NSSF, OSHA, WCF, GN487A, GN605A

## Model
Base:    McGill-NLP/AfriqueLlama-8B
Adapter: prospAprospA007/africa-giants-adapter-v8
"""
    api.upload_file(
        path_or_fileobj=readme.encode('utf-8'),
        path_in_repo='README.md',
        repo_id=HF_DATASET_REPO,
        repo_type='dataset',
        commit_message=f'Update README -- {total} total pairs',
    )
    print("[upload] README.md updated")
    print(f"\n[upload] Dataset uploaded. train={len(sft_pairs)} val={len(val_pairs)}. "
          "Ready for Kaggle training.")


if __name__ == '__main__':
    upload()
