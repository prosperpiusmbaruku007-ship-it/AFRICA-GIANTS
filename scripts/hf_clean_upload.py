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
