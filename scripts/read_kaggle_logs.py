# -*- coding: utf-8 -*-
"""
Read the latest Kaggle kernel status and output logs.

Run with: python scripts/read_kaggle_logs.py

Fixes Windows cp1252 encoding by reconfiguring stdout to UTF-8 before
any output and setting PYTHONUTF8=1 so the Kaggle SDK reads responses
correctly.
"""
import os
import sys

# Must happen before any print() or SDK import that touches stdout/stderr
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
os.environ["PYTHONUTF8"] = "1"

import json
import tempfile

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
except ImportError:
    pass  # dotenv optional; fall through to env vars

KAGGLE_KEY      = os.getenv("KAGGLE_KEY", "")
KAGGLE_USERNAME = os.getenv("KAGGLE_USERNAME", "")
KERNEL_REF      = "prospaprospa/africa-giants-trainer"

# Set up credentials the same way run_pipeline.py does
if KAGGLE_KEY.startswith("KGAT_"):
    os.environ["KAGGLE_API_TOKEN"] = KAGGLE_KEY
    token_path = os.path.expanduser("~/.kaggle/access_token")
    os.makedirs(os.path.dirname(token_path), exist_ok=True)
    with open(token_path, "w", encoding="utf-8") as f:
        f.write(KAGGLE_KEY)
    print("Auth: KGAT access token")
else:
    os.environ["KAGGLE_USERNAME"] = KAGGLE_USERNAME
    os.environ["KAGGLE_KEY"]      = KAGGLE_KEY
    kaggle_json = os.path.expanduser("~/.kaggle/kaggle.json")
    os.makedirs(os.path.dirname(kaggle_json), exist_ok=True)
    with open(kaggle_json, "w", encoding="utf-8") as f:
        json.dump({"username": KAGGLE_USERNAME, "key": KAGGLE_KEY}, f)
    print("Auth: legacy API key")

from kaggle.api.kaggle_api_extended import KaggleApi

api = KaggleApi()
api.authenticate()

# ── 1. Kernel status ────────────────────────────────────────────────────────
print(f"\n=== Kernel status: {KERNEL_REF} ===")
try:
    status = api.kernels_status(KERNEL_REF)
    raw = str(status).encode("utf-8", errors="replace").decode("utf-8")
    print(raw)

    # Extract failure message if present
    for attr in ("failure_message", "failureMessage", "error_message"):
        msg = getattr(status, attr, None)
        if msg:
            print(f"\n*** FAILURE MESSAGE: {msg} ***")
            break

    # Status value
    for attr in ("status", "currentRunningVersion"):
        val = getattr(status, attr, None)
        if val is not None:
            print(f"{attr}: {val}")
except Exception as e:
    print(f"kernels_status failed: {e}")
    print("(KGAT token may lack 'kernels.get' scope — check logs in Kaggle web UI)")

# ── 2. Kernel output files ───────────────────────────────────────────────────
print(f"\n=== Kernel output: {KERNEL_REF} ===")
try:
    with tempfile.TemporaryDirectory() as tmpdir:
        api.kernels_output(KERNEL_REF, path=tmpdir, force=True)
        files = os.listdir(tmpdir)
        if not files:
            print("No output files found (kernel may still be running or produced no files).")
        for fname in files:
            fpath = os.path.join(tmpdir, fname)
            print(f"\n--- {fname} ---")
            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                # Print last 200 lines — most useful for finding crash cause
                lines = content.splitlines()
                if len(lines) > 200:
                    print(f"(showing last 200 of {len(lines)} lines)")
                    lines = lines[-200:]
                print("\n".join(lines))
            except Exception as read_err:
                print(f"  (binary file or read error: {read_err})")
except Exception as e:
    print(f"kernels_output failed: {e}")
    print("(KGAT token may lack output scope)")

print("\n=== Done ===")
print("If both calls failed with 403/permission errors, go to:")
print(f"  https://www.kaggle.com/code/{KERNEL_REF}")
print("Open the latest failed version → scroll to the last error in the output tab.")
