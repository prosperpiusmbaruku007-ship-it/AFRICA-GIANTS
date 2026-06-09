#!/usr/bin/env python3
"""
SOURCE-ENFORCER validation script.
Usage: python scripts/check_sources.py --file path/to/batch.jsonl
Exit code: 0 = clean, 1 = violations found
"""
import json, sys, argparse, os

TRAINING_WHITELIST = [
    "tra.go.tz", "nssf.go.tz", "nssf.or.tz", "brela.go.tz",
    "immigration.go.tz", "mlywf.go.tz", "osha.go.tz",
    "tanzlii.org", "nest.go.tz", "ppra.go.tz"
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

    # Warn about unrecognised sources
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
