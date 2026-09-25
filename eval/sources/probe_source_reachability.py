"""Probe candidate PRIMARY SOURCES for reachability, per-path, and record the verdict.

WHY THIS EXISTS (R30). On 2026-08-16 this project discovered that `WebFetch` failing against
tra.go.tz is a bug in ONE TOOL'S HTTP CLIENT, not a property of the domain, and wrote down a
working `curl` recipe. It was never turned into a script, so it was never re-applied: every
session between 2026-08-16 and 2026-09-02 that hit the same `Parse Error` re-recorded it as
"TRA page unavailable". R30 bullet 2 says a working-around-a-failure finding is not done when
it is written down, it is done when the next session cannot fail to know it. This is that
script.

WHAT IT IS FOR, precisely: answering "does a primary source exist and can we reach it" during
SCOPING. It does NOT encode facts. Anything that becomes a locked fact still goes through the
full R4 / R28 / R29 discipline, and through "A CONSOLIDATED ACT IS NOT THE CURRENT LAW".

THREE THINGS IT REFUSES TO CONFLATE, because conflating them is what produced the stale note
this script replaces:

  * a DOMAIN verdict vs a PATH verdict. tanzlii.org serves its listing pages with a plain 200
    and real content while 403-ing its Act full-text pages behind a Cloudflare challenge.
    "tanzlii is blocked" and "tanzlii is fine" are both wrong. Verdicts here are per-URL.
  * a TRANSPORT failure vs a CHALLENGE vs an EMPTY SHELL. HTTP 200 is not evidence of content:
    a Turnstile interstitial is a 403 with a body, and a client-rendered SPA is a 200 with
    almost none. Each is recorded distinctly, because each has a different remedy (retry with
    another tool / no remedy / find the API or another host).
  * a GUESSED URL 404 vs a closed route. R30 bullet 3: a 404 on a guess proves nothing about
    the domain. Rows carry `url_provenance` so a guess can never be read as a finding.

ARTIFACT DISCIPLINE (R16). The artifact is written after EVERY ROW and the run RESUMES from it,
so a dropped Tanzanian link costs one row and never the run. Per-row errors are captured, not
raised.

Usage:  python eval/sources/probe_source_reachability.py [--force]
"""

import json
import os
import re
import subprocess
import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(REPO, "eval", "results", "coverage_source_reachability_2026_09_25.json")

# A real browser UA. Not decoration: the 2026-09-02 tanzlii verdict was reached WITH one, which
# is why that verdict (for document pages) still stands and is reproduced below.
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

CHALLENGE_MARKERS = ("just a moment", "turnstile", "cf-challenge", "challenge-platform",
                     "enable javascript and cookies")

# `url_provenance` values:
#   LINKED    - the URL was read off a page we fetched (strongest)
#   OFFICIAL  - published by the institution itself / already in sources/whitelist.json
#   GUESS     - constructed by pattern. A 404 here is NOT a finding about the domain (R30 #3).
PROBES = [
    # --- rental withholding (consequential #1) ---
    dict(id="rental_wht_tra", topic="rental_withholding", url_provenance="LINKED",
         url="https://www.tra.go.tz/page/withholding-tax",
         expect="Withholding rate table incl. rent, and the withholding-AGENT definition",
         needles=["Rental Income", "Withholding Agent"]),

    # --- TRA audit rights (consequential #2) ---
    dict(id="taa_cap438_pdf", topic="tra_audit", url_provenance="GUESS",
         url="https://www.tra.go.tz/images/uploads/acts/Tax_Administration_Act.pdf",
         expect="Tax Administration Act Cap.438 R.E.2023 full text (s.51 access to premises)",
         needles=[], binary=True),

    # --- weights and measures ---
    dict(id="wma_home", topic="weights_measures", url_provenance="OFFICIAL",
         url="https://www.wma.go.tz/",
         expect="Weights and Measures Agency — the real calibration authority",
         needles=["Weights and Measures Agency"]),
    dict(id="wma_laws", topic="weights_measures", url_provenance="LINKED",
         url="https://www.wma.go.tz/publications/laws",
         expect="WMA's own legal-basis page (Cap.340 + subsidiary regs)",
         needles=[]),

    # --- fire safety ---
    dict(id="fire_force_apex", topic="fire_safety", url_provenance="LINKED",
         url="https://zimamoto.go.tz/",
         expect="Fire and Rescue Force — national force under MOHA, the real issuer",
         needles=["Fire and Rescue"]),
    dict(id="fire_force_www", topic="fire_safety", url_provenance="LINKED",
         url="https://www.zimamoto.go.tz/",
         expect="SAME site via the www host MOHA itself links to — expected to FAIL",
         needles=[]),
    dict(id="fire_fabricated_domain", topic="fire_safety", url_provenance="GUESS",
         url="https://www.fire.go.tz/",
         expect="THE DOMAIN THE MODEL INVENTED in ext_33. Expected: does not resolve.",
         needles=[]),

    # --- TIN process ---
    dict(id="tin_starting_business", topic="tin_process", url_provenance="LINKED",
         url="https://www.tra.go.tz/page/starting-business-income-for-individuals-and-paying-taxes",
         expect="TRA Starting Business page — TIN registration path",
         needles=[]),

    # --- tanzlii, per-path (the whole point of this script) ---
    dict(id="tanzlii_listing", topic="_infrastructure", url_provenance="OFFICIAL",
         url="https://tanzlii.org/en/legislation/",
         expect="Listing page. 2026-09-02 recorded tanzlii as Turnstile-blocked; test it.",
         needles=["legislation"]),
    dict(id="tanzlii_act_fulltext", topic="_infrastructure", url_provenance="GUESS",
         url="https://tanzlii.org/en/akn/tz/act/2015/10/eng",
         expect="Act full text. URL pattern read off the listing page, act number is a guess.",
         needles=[]),
]


def fetch(url, dest):
    """One curl with the known-working recipe. Returns (status, bytes, transport_error)."""
    try:
        p = subprocess.run(
            ["curl", "-s", "-L", "--max-time", "45", "-A", UA, "-o", dest,
             "-w", "%{http_code} %{size_download}", url],
            capture_output=True, text=True, timeout=90)
    except subprocess.TimeoutExpired:
        return None, 0, "curl_timeout"
    parts = (p.stdout or "").split()
    if len(parts) != 2:
        return None, 0, f"curl_no_metrics rc={p.returncode} err={(p.stderr or '')[:120]}"
    status, size = parts[0], int(parts[1])
    # curl reports 000 when the connection never produced an HTTP response at all
    # (DNS failure, refused, TLS). That is a TRANSPORT verdict, not an HTTP one.
    if status == "000":
        return None, size, "no_http_response"
    return int(status), size, None


def classify(status, size, body, transport_error, binary):
    """Five distinct verdicts. 'not 200' and 'no content' are different findings."""
    if transport_error == "no_http_response":
        return "UNRESOLVABLE"
    if transport_error:
        return "PROBE_ERROR"
    low = (body or "").lower()
    if any(m in low for m in CHALLENGE_MARKERS):
        return "CHALLENGED"
    if status != 200:
        return f"HTTP_{status}"
    if binary:
        return "OK" if size > 10000 else "EMPTY_SHELL"
    # A 200 with almost no body is a client-rendered SPA shell, not a served document.
    text = re.sub(r"<[^>]+>", " ", re.sub(r"(?s)<(script|style).*?</\1>", "", body or ""))
    if len(re.sub(r"\s+", " ", text).strip()) < 500:
        return "EMPTY_SHELL"
    return "OK"


def main():
    force = "--force" in sys.argv
    scratch = os.path.join(REPO, "scratch")
    os.makedirs(scratch, exist_ok=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)

    art = {"measured": str(date.today()), "harness": "eval/sources/probe_source_reachability.py",
           "user_agent": UA,
           "what_this_measures": "REACHABILITY of a candidate primary source at a SPECIFIC URL. "
                                 "Not the truth of anything it says, and not a licence to encode "
                                 "a fact from it (R4/R28/R29 still apply in full).",
           "verdicts": {"OK": "served real content",
                        "CHALLENGED": "bot challenge; switching tools will not help",
                        "EMPTY_SHELL": "200 but client-rendered/near-empty; needs another route",
                        "UNRESOLVABLE": "no HTTP response at all (DNS/refused/TLS)",
                        "HTTP_n": "reached, refused with status n",
                        "PROBE_ERROR": "the probe failed, verdict UNKNOWN — not a source verdict"},
           "rows": {}}
    if os.path.exists(OUT) and not force:
        try:
            art = json.load(open(OUT, encoding="utf-8"))
        except Exception:
            pass
    art.setdefault("rows", {})

    for probe in PROBES:
        pid = probe["id"]
        if pid in art["rows"] and not force:
            print(f"  skip (resumed) {pid}")
            continue
        dest = os.path.join(scratch, f"_src_{pid}.bin")
        status, size, terr = fetch(probe["url"], dest)
        body = ""
        if not probe.get("binary") and os.path.exists(dest):
            try:
                body = open(dest, encoding="utf-8", errors="replace").read()
            except Exception as e:
                terr = terr or f"read_failed:{e}"
        verdict = classify(status, size, body, terr, probe.get("binary", False))
        found = [n for n in probe.get("needles", []) if n.lower() in body.lower()]
        missing = [n for n in probe.get("needles", []) if n not in found]

        art["rows"][pid] = {
            "topic": probe["topic"], "url": probe["url"],
            "url_provenance": probe["url_provenance"], "expect": probe["expect"],
            "http_status": status, "bytes": size, "verdict": verdict,
            "needles_found": found, "needles_missing": missing,
            "transport_error": terr,
        }
        # R16: write after EVERY row. A dropped link costs one row, never the run.
        json.dump(art, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"  {verdict:<14} {pid:<26} HTTP={status} bytes={size}"
              + (f" MISSING={missing}" if missing else ""))

    by_verdict = {}
    for r in art["rows"].values():
        by_verdict[r["verdict"]] = by_verdict.get(r["verdict"], 0) + 1
    art["summary"] = by_verdict
    json.dump(art, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\nsummary:", by_verdict)
    print("artifact:", OUT)


if __name__ == "__main__":
    main()
