"""
Scrape Tier 1A batch 002 source URLs and save raw HTML locally.
Saves to datasets/tier1a/raw_sources/scraped/
Prints per-URL success/failure status.
"""
import os
import time

try:
    import requests
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "requests"])
    import requests

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_DIR = os.path.join(ROOT, "datasets", "tier1a", "raw_sources", "scraped")
os.makedirs(OUT_DIR, exist_ok=True)

TARGETS = [
    ("paye.html",       "https://www.tra.go.tz/page/pay-as-you-earn-paye"),
    ("vat_edge.html",   "https://www.tra.go.tz/page/value-added-tax-vat"),
    ("withholding.html","https://www.tra.go.tz/page/withholding-tax"),
    ("gn605a.html",     "https://www.velmalaw.co.tz/insights"),
    ("work_permits.html","https://www.immigration.go.tz"),
    ("nssf_edge.html",  "https://www.nssf.go.tz/pages/payment-of-contributions"),
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

succeeded = []
failed = []

for filename, url in TARGETS:
    out_path = os.path.join(OUT_DIR, filename)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20, allow_redirects=True)
        resp.raise_for_status()
        html = resp.text
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        size_kb = len(html) / 1024
        print(f"  OK  {filename:25s}  {size_kb:7.1f} KB  {url}")
        succeeded.append(filename)
    except Exception as e:
        print(f"  FAIL {filename:25s}  {type(e).__name__}: {e}")
        failed.append((filename, url, str(e)))
    time.sleep(1)

print()
print(f"Succeeded: {len(succeeded)}/{len(TARGETS)}")
print(f"Failed:    {len(failed)}/{len(TARGETS)}")
if failed:
    print("Failed targets (will use CLAUDE.md locked facts as fallback):")
    for fn, url, err in failed:
        print(f"  {fn}: {url}")
