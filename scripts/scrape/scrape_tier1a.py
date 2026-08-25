"""
Tier 1A scraper — fetches raw HTML from approved government portals and saves
to datasets/tier1a/raw_sources/. Falls back gracefully on network failure.

Approved sources (sources/whitelist.json):
  - https://www.tra.go.tz/index.php/tax-information
  - https://www.tra.go.tz/index.php/filing-returns
  - https://www.brela.go.tz
  - https://www.nssf.go.tz
  - https://www.osha.go.tz

Usage: python scripts/scrape/scrape_tier1a.py
"""
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = ROOT / "datasets" / "tier1a" / "raw_sources"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TARGETS = [
    {
        "id": "tra_tax_information",
        "url": "https://www.tra.go.tz/index.php/tax-information",
        "institution": "Tanzania Revenue Authority",
        "filename": "tra_tax_information.html",
    },
    {
        "id": "tra_filing_returns",
        "url": "https://www.tra.go.tz/index.php/filing-returns",
        "institution": "Tanzania Revenue Authority",
        "filename": "tra_filing_returns.html",
    },
    {
        "id": "brela_home",
        "url": "https://www.brela.go.tz",
        "institution": "Business Registrations and Licensing Agency",
        "filename": "brela_home.html",
    },
    {
        "id": "nssf_home",
        "url": "https://www.nssf.go.tz",
        "institution": "National Social Security Fund Tanzania",
        "filename": "nssf_home.html",
    },
    {
        "id": "osha_home",
        "url": "https://www.osha.go.tz",
        "institution": "Occupational Safety and Health Authority",
        "filename": "osha_home.html",
    },
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; AFRICA-GIANTS-dataset-builder/1.0; "
        "+https://github.com/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS)"
    ),
    "Accept-Language": "sw,en;q=0.9",
}


def make_session():
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def strip_html(html: str) -> str:
    text = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"\s{3,}", "\n\n", text)
    return text.strip()


def scrape_all():
    if not HAS_REQUESTS:
        print("requests not installed — skipping live scrape. Install with: pip install requests")
        return {}

    session = make_session()
    results = {}
    manifest = []

    for target in TARGETS:
        url = target["url"]
        filename = target["filename"]
        out_path = OUTPUT_DIR / filename
        text_path = OUTPUT_DIR / filename.replace(".html", "_text.txt")

        print(f"Fetching {url} ...")
        try:
            resp = session.get(url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            html = resp.text

            with open(out_path, "w", encoding="utf-8", errors="replace") as f:
                f.write(html)

            text = strip_html(html)
            with open(text_path, "w", encoding="utf-8", errors="replace") as f:
                f.write(text)

            status = "ok"
            char_count = len(text)
            print(f"  Saved {char_count:,} chars of text → {text_path.name}")
            results[target["id"]] = text

        except Exception as e:
            status = f"error: {e}"
            print(f"  FAILED: {e}")
            error_path = OUTPUT_DIR / filename.replace(".html", "_error.txt")
            with open(error_path, "w", encoding="utf-8") as f:
                f.write(f"Fetch failed at {datetime.now(timezone.utc).isoformat()}\nURL: {url}\nError: {e}\n")
            results[target["id"]] = None

        manifest.append({
            "id": target["id"],
            "url": url,
            "institution": target["institution"],
            "filename": filename,
            "status": status,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        })
        time.sleep(2)

    manifest_path = OUTPUT_DIR / "scrape_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"\nManifest saved: {manifest_path}")
    return results


if __name__ == "__main__":
    results = scrape_all()
    ok = sum(1 for v in results.values() if v is not None)
    print(f"\nScrape complete: {ok}/{len(TARGETS)} sources fetched successfully.")
    sys.exit(0)
