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
    "tanzlii.org", "nest.go.tz", "ppra.go.tz", "wcf.go.tz"
]

# THE FLAG WAS ENFORCED AT SERVING AND NOT AT AUTHORING — removed 2026-08-23.
#
# CLAUDE.md section 4 says plainly: use nssf.go.tz, `nssf.or.tz` fails DNS. Serving honours it —
# `chike.generation_cleanup.clean_generated_reply` rewrites or.tz -> go.tz and
# `_validate_and_clean` applies it on every reply. **Authoring did not: this list whitelisted the
# dead domain**, so 786 occurrences across 34 files in datasets/tier1a/cleaned_pairs/ were written
# citing it and nothing objected.
#
# That is why the model emits it. The serving rewrite is a patch over a training-data defect, and
# the patch is what kept the defect invisible: it never reached a user, so it never surfaced. It
# was found only because `generate_raw` bypasses cleaning by design and a diagnostic ran through it.
#
# Removing it here CLOSES THE AUTHORING GAP and will fail existing batches, which is the correct
# signal rather than a regression. The 786 rows are a separate, scoped decision: rewriting them
# only changes behaviour after a retrain, so it belongs with the next training cycle, not here.
DEAD_DOMAINS = {
    "nssf.or.tz": "nssf.or.tz fails DNS — use nssf.go.tz (CLAUDE.md section 4)",
}

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

    # Dead domains are checked against the WHOLE PAIR, not just the source fields. The 786
    # existing occurrences are overwhelmingly inside answer TEXT ("Thibitisha na nssf.or.tz"),
    # which a source-field-only check cannot see — and answer text is what the model learns to
    # imitate, so it is the half that actually mattered.
    body = json.dumps(pair, ensure_ascii=False).lower()
    for dead, why in DEAD_DOMAINS.items():
        if dead in body:
            flags.append(f"DEAD DOMAIN [{pid}]: {dead} — {why}")

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
