# SOURCE-ENFORCER

## Training whitelist (allowed for training pairs only)
- tra.go.tz
- nssf.go.tz
- brela.go.tz
- immigration.go.tz
- mlywf.go.tz
- osha.go.tz
- tanzlii.org
- nest.go.tz

## Eval-only sources (NEVER for training)
- ey.com / ey.co.tz
- kpmg.com / kpmg.co.tz
- pkf.co.tz
- bowmans.com
- pwc.com / taxsummaries.pwc.com
- ifc.org
- auditax.co.tz
- habibadvisory.com
- remotepeople.com
- rivermate.com

## Domain boundary
- eac.int content → Tier 1B ONLY
- nest.go.tz content → Tier 1C ONLY
- comesa.int → NOT Tier 1A

## Before writing each pair
python scripts/check_sources.py --file [batch_file.jsonl]

---

## COMPANION SCRIPT — scripts/check_sources.py

```python
#!/usr/bin/env python3
"""
SOURCE-ENFORCER validation script.
Usage: python scripts/check_sources.py --file path/to/batch.jsonl
Exit code: 0 = clean, 1 = violations found
"""
import json, sys, argparse, os

TRAINING_WHITELIST = [
    "tra.go.tz", "nssf.go.tz", "brela.go.tz",
    "immigration.go.tz", "mlywf.go.tz", "osha.go.tz",
    "tanzlii.org", "nest.go.tz"
]

EVAL_ONLY = [
    "ey.com", "kpmg.com", "pkf.co.tz", "bowmans.com",
    "pwc.com", "taxsummaries.pwc.com", "ifc.org",
    "auditax.co.tz", "habibadvisory.com",
    "remotepeople.com", "rivermate.com", "payspace.com",
    "deel.com", "rsm.co.tz"
]

TIER1B_ONLY = ["eac.int", "comesa.int"]
TIER1C_ONLY = ["nest.go.tz"]

BANNED = [
    "wikipedia.org", "chatgpt.com", "chat.openai.com",
    "reddit.com", "quora.com"
]

def check_pair(pair):
    flags = []
    url = pair.get("primary_source_url", "").lower()
    url_name = pair.get("primary_source_name", "").lower()
    pid = pair.get("id", "unknown")
    domain = pair.get("domain", "tier1a")

    combined = url + " " + url_name

    for e in EVAL_ONLY:
        if e in combined:
            flags.append(f"EVAL-ONLY source in training pair [{pid}]: {url}")

    for b in BANNED:
        if b in combined:
            flags.append(f"BANNED source [{pid}]: {url}")

    for t in TIER1B_ONLY:
        if t in combined and domain == "tier1a":
            flags.append(f"TIER1B source in Tier1A pair [{pid}]: {url}")

    all_known = TRAINING_WHITELIST + EVAL_ONLY + TIER1B_ONLY + TIER1C_ONLY + BANNED
    if url and not any(w in url for w in all_known):
        flags.append(
            f"UNKNOWN SOURCE [{pid}]: {url} — verify it is a valid primary source"
        )

    return flags

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"ERROR: File not found: {args.file}")
        sys.exit(1)

    total = 0
    flagged = 0
    with open(args.file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            pair = json.loads(line)
            total += 1
            flags = check_pair(pair)
            if flags:
                flagged += 1
                for flag in flags:
                    print(f"SOURCE FLAG: {flag}")

    print(f"\nChecked {total} pairs. {flagged} source violations.")
    if flagged > 0:
        sys.exit(1)
    else:
        print("CLEAN — all sources valid.")
        sys.exit(0)

if __name__ == "__main__":
    main()
```

PASS CASE:
  primary_source_url: "https://www.tra.go.tz/page/pay-as-you-earn-paye"
  Output: CLEAN — all sources valid. (exit 0)

FAIL CASE:
  primary_source_url: "https://www.pkf.co.tz/insights/tanzania-tax-guide"
  Output: SOURCE FLAG: EVAL-ONLY source in training pair [tier1a_paye_001]: pkf.co.tz
  (exit 1)
