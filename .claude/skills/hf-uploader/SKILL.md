# HF-UPLOADER

## Step 1: Generate fresh SFT files from corpus
```bash
python scripts/generate_sft.py
```
Verify output: "Train: 270 | Val: 30" (for 300-pair corpus)

## Step 2: Delete ALL old files from HuggingFace
```bash
python scripts/hf_clean_upload.py --delete-only
```

## Step 3: Upload new SFT files
```bash
python scripts/hf_clean_upload.py --upload
```

## Step 4: Verify upload
```bash
python scripts/hf_clean_upload.py --verify
```
Expected output: "train_sft.jsonl: present | val_sft.jsonl: present | No .parquet files"

## Critical: dataset repo name
REPO = "prospAprospA007/africa-giants-dataset"
Note mixed capitals: prospAprospA007 (NOT prospaprospa007)
The HuggingFace dataset was created with this mixed-capital username.

---

## COMPANION SCRIPT — scripts/generate_sft.py

```python
#!/usr/bin/env python3
"""Generate SFT training files from all cleaned pair batches."""
import json, random, os, glob

SYSTEM_PROMPT = (
    "Wewe ni msaidizi wa AI wa biashara za Tanzania. "
    "Unajibu maswali kuhusu sheria za biashara, kodi, "
    "usajili wa kampuni kwa Kiswahili na Kiingereza. "
    "You are a Tanzanian business AI assistant answering "
    "questions about regulations, tax, company registration, "
    "and financial rules in Swahili and English."
)

CLEANED_DIR = "datasets/tier1a/cleaned_pairs"
SFT_DIR = "datasets/tier1a/sft"

def load_all_pairs():
    all_pairs = []
    for filepath in sorted(glob.glob(f"{CLEANED_DIR}/*.jsonl")):
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    p = json.loads(line)
                    # Skip eval-set pairs from training
                    if not p.get("eval_set", False):
                        all_pairs.append(p)
    return all_pairs

def fmt_pair(p):
    q = p.get("question_sw", "") or p.get("question_en", "")
    a = p.get("answer_sw", "") or p.get("answer_en", "")
    return {
        "instruction": q,
        "input": "",
        "output": a,
        "system": SYSTEM_PROMPT
    }

def main():
    all_pairs = load_all_pairs()
    print(f"Loaded {len(all_pairs)} non-eval pairs")

    formatted = [fmt_pair(p) for p in all_pairs]
    random.seed(42)
    random.shuffle(formatted)

    split = int(len(formatted) * 0.9)
    train = formatted[:split]
    val = formatted[split:]
    print(f"Train: {len(train)} | Val: {len(val)}")

    os.makedirs(SFT_DIR, exist_ok=True)

    train_path = os.path.join(SFT_DIR, "train_sft.jsonl")
    val_path = os.path.join(SFT_DIR, "val_sft.jsonl")

    with open(train_path, "w", encoding="utf-8") as f:
        for p in train:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    with open(val_path, "w", encoding="utf-8") as f:
        for p in val:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    print(f"Saved: {train_path}")
    print(f"Saved: {val_path}")

if __name__ == "__main__":
    main()
```

## COMPANION SCRIPT — scripts/hf_clean_upload.py

```python
#!/usr/bin/env python3
"""HuggingFace clean upload — delete old files then upload new SFT files."""
import sys, os, argparse
sys.path.insert(0, ".")

REPO = "prospAprospA007/africa-giants-dataset"
SFT_DIR = "datasets/tier1a/sft"

def get_token():
    try:
        from src.common.secrets import get_hf_token
        return get_hf_token()
    except Exception:
        token = os.environ.get("HF_TOKEN", "")
        if not token:
            print("ERROR: No HF token found. Set HF_TOKEN env var.")
            sys.exit(1)
        return token

def delete_old_files(api, token):
    from huggingface_hub import CommitOperationDelete
    files = list(api.list_repo_files(
        repo_id=REPO, repo_type="dataset", token=token))
    print(f"Current files: {files}")

    to_delete = [f for f in files if
                 f.endswith(".parquet") or
                 f == "instruction_dataset.jsonl"]

    if to_delete:
        ops = [CommitOperationDelete(path_in_repo=f) for f in to_delete]
        api.create_commit(
            repo_id=REPO, repo_type="dataset", operations=ops,
            commit_message="delete old parquet/instruction files",
            token=token
        )
        print(f"Deleted: {to_delete}")
    else:
        print("No old files to delete")

def upload_sft_files(api, token):
    for fname in ["train_sft.jsonl", "val_sft.jsonl"]:
        local = os.path.join(SFT_DIR, fname)
        if not os.path.exists(local):
            print(f"ERROR: {local} not found — run generate_sft.py first")
            sys.exit(1)
        size = os.path.getsize(local)
        print(f"Uploading {fname} ({size:,} bytes)...")
        api.upload_file(
            path_or_fileobj=local,
            path_in_repo=fname,
            repo_id=REPO, repo_type="dataset", token=token
        )
        print(f"OK: {fname}")
    print(f"Upload complete. URL: https://huggingface.co/datasets/{REPO}")

def verify_upload(api, token):
    files = list(api.list_repo_files(
        repo_id=REPO, repo_type="dataset", token=token))
    has_train = "train_sft.jsonl" in files
    has_val = "val_sft.jsonl" in files
    has_parquet = any(f.endswith(".parquet") for f in files)
    print(f"train_sft.jsonl: {'present' if has_train else 'MISSING'}")
    print(f"val_sft.jsonl:   {'present' if has_val else 'MISSING'}")
    print(f"Parquet files:   {'PRESENT - DELETE THEM' if has_parquet else 'none (clean)'}")
    if not has_train or not has_val or has_parquet:
        sys.exit(1)
    print("VERIFIED clean.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--delete-only", action="store_true")
    parser.add_argument("--upload", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    from huggingface_hub import HfApi, login
    token = get_token()
    login(token=token)
    api = HfApi()

    if args.delete_only:
        delete_old_files(api, token)
    elif args.upload:
        upload_sft_files(api, token)
    elif args.verify:
        verify_upload(api, token)
    else:
        # Full sequence
        delete_old_files(api, token)
        upload_sft_files(api, token)
        verify_upload(api, token)

if __name__ == "__main__":
    main()
```
