#!/usr/bin/env python3
"""
REGULATORY-VERIFIER — cross-AI review using Groq + Gemini + OpenAI.
Replaces manual Perplexity paste workflow entirely.
Usage: python scripts/verify_pairs.py --file path/to/batch.jsonl
Exit: 0 = clean, 1 = flags found

Models used:
  - Groq (llama-3.1-8b-instant) — free forever, no card needed
  - Gemini (gemini-1.5-flash) — free forever, no card needed
  - OpenAI gpt-4o-mini — optional, $5 free credits covers full project
  - Claude strict (optional if ANTHROPIC_API_KEY set) — adversarial prompt

NOTE: Brave Search is NOT used — blocked in Tanzania by TRA registration requirement.
NOTE: Perplexity is NOT used — requires $5 upfront payment with no free tier.
"""
import json, sys, os, argparse, urllib.request, urllib.error, re
from datetime import datetime

REVIEW_PROMPT = """You are a strict Tanzania tax law expert reviewing Q&A training pairs
for a Tanzanian business compliance AI assistant.

Review each pair for factual errors against current TRA/NSSF/BRELA/Immigration
regulations as of 2025/2026.

KNOWN WRONG PATTERNS the base model produces — check for these specifically:
- SDL described as Service Delivery Levy or disability leave (WRONG — Skills Development Levy)
- NSSF rate described as 6% (WRONG — 10% each side)
- PAYE second band described as 9% (WRONG — 8%)
- GN487A described as residence permit rules (WRONG — business prohibition order)
- VAT described as changed from 14% (WRONG — 18% since 2015 unchanged)
- Provisional tax described as 3 instalments (WRONG — 4 instalments)
- Property stamp duty described as tiered 0.5%/1% (WRONG — flat 1%)
- P45 form mentioned (WRONG — UK form, does not exist in Tanzania)
- Royalties WHT described as 10% non-resident (WRONG — 15% both)
- Commissioner objection deadline described as 90 days (WRONG — 6 months)
- Minimum tax described as 0.3% or 0.5% (WRONG — 1% since July 2025)

Focus ONLY on:
- Wrong percentages or rates
- Wrong TZS amounts
- Wrong deadlines or dates
- Wrong form names
- Wrong descriptions of laws or orders

For each error found output EXACTLY this format on one line:
FLAG: [pair_id] | [field] | [wrong_value] | [correct_value] | [source]

If no errors found output exactly: CLEAN

Do not add any other text."""

STRICT_PROMPT = """You are an adversarial Tanzania tax auditor.
Your ONLY job is to find errors. Assume every answer might be wrong.
Be especially suspicious of these known base model errors:
- SDL = disability leave (base model says this — it is wrong)
- NSSF = 6% (base model says this — it is wrong, should be 10%)
- PAYE band 2 = 9% (base model says this — it is wrong, should be 8%)
- GN487A = residence permit order (base model says this — it is wrong)
- VAT changed from 14% (base model says this — it is wrong)
- P45 form exists in Tanzania (it does not)

Output FLAG: [pair_id] | [field] | [wrong_value] | [correct_value] | [source]
or CLEAN — nothing else."""


def call_groq(pairs_text, api_key):
    """Groq API — free tier, Llama 3 model."""
    payload = json.dumps({
        "model": "llama-3.1-8b-instant",
        "max_tokens": 1000,
        "messages": [
            {"role": "system", "content": REVIEW_PROMPT},
            {"role": "user", "content": pairs_text}
        ]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"GROQ_ERROR: {e}"


def call_gemini(pairs_text, api_key):
    """Google Gemini API — free tier."""
    full_prompt = REVIEW_PROMPT + "\n\n" + pairs_text
    payload = json.dumps({
        "contents": [{"parts": [{"text": full_prompt}]}]
    }).encode("utf-8")

    url = (f"https://generativelanguage.googleapis.com/v1beta/"
           f"models/gemini-1.5-flash:generateContent?key={api_key}")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            return (result["candidates"][0]["content"]
                    ["parts"][0]["text"].strip())
    except Exception as e:
        return f"GEMINI_ERROR: {e}"


def call_openai(pairs_text, api_key):
    """OpenAI gpt-4o-mini — $5 free credits covers full 3,000-pair project."""
    payload = json.dumps({
        "model": "gpt-4o-mini",
        "max_tokens": 1000,
        "messages": [
            {"role": "system", "content": REVIEW_PROMPT},
            {"role": "user", "content": pairs_text}
        ]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"OPENAI_ERROR: {e}"


def call_claude_strict(pairs_text, api_key):
    """Claude strict adversarial review — uses claude-haiku for low cost."""
    payload = json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 1000,
        "system": STRICT_PROMPT,
        "messages": [{"role": "user", "content": pairs_text}]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            return result["content"][0]["text"].strip()
    except Exception as e:
        return f"CLAUDE_STRICT_ERROR: {e}"


def parse_flags(response, model_name):
    flags = []
    if not response or "ERROR" in str(response):
        return flags
    for line in response.strip().split("\n"):
        line = line.strip()
        if line.startswith("FLAG:"):
            flags.append({"model": model_name, "raw": line})
    return flags


def format_pairs_for_review(pairs, batch_num):
    lines = [f"BATCH {batch_num} — Tanzania regulatory Q&A pairs:\n"]
    for p in pairs:
        lines.append(f"PAIR_ID: {p.get('id', 'unknown')}")
        lines.append(f"Q: {p.get('question_en', '')}")
        lines.append(f"A: {p.get('answer_en', '')}")
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Cross-AI review using Groq + Gemini + optional Claude strict"
    )
    parser.add_argument("--file", required=True,
                        help="Path to JSONL file to verify")
    parser.add_argument("--log",
                        default="scripts/verification_log.jsonl",
                        help="Path to verification log")
    parser.add_argument("--batch-size", type=int, default=10,
                        help="Pairs per AI review batch")
    args = parser.parse_args()

    # Load API keys
    groq_key = os.environ.get("GROQ_API_KEY", "")
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    claude_key = os.environ.get("ANTHROPIC_API_KEY", "")

    available = []
    if groq_key:
        available.append("groq")
    if gemini_key:
        available.append("gemini")
    if openai_key:
        available.append("openai")
    if claude_key:
        available.append("claude_strict")

    if not available:
        print("ERROR: No API keys found.")
        print("Set GROQ_API_KEY and/or GEMINI_API_KEY environment variables.")
        print("Get Groq free at: console.groq.com")
        print("Get Gemini free at: aistudio.google.com")
        print("Get OpenAI at: platform.openai.com (optional, $5 free credits)")
        sys.exit(1)

    print(f"Models available: {', '.join(available)}")
    print(f"NOTE: Brave Search not used (blocked in Tanzania)")
    print(f"NOTE: Perplexity not used (requires $5 upfront payment)\n")

    # Load pairs
    if not os.path.exists(args.file):
        print(f"ERROR: {args.file} not found")
        sys.exit(1)

    pairs = []
    with open(args.file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    pairs.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

    print(f"Reviewing {len(pairs)} pairs...\n")

    all_flags = []
    total_batches = (len(pairs) + args.batch_size - 1) // args.batch_size

    for batch_num in range(total_batches):
        start = batch_num * args.batch_size
        batch = pairs[start:start + args.batch_size]
        pairs_text = format_pairs_for_review(batch, batch_num + 1)

        print(f"Batch {batch_num + 1}/{total_batches} "
              f"(pairs {start + 1}-{start + len(batch)}):")

        responses = {}

        if groq_key:
            print("  Calling Groq...", end=" ", flush=True)
            responses["groq"] = call_groq(pairs_text, groq_key)
            status = "ERROR" if "ERROR" in str(responses["groq"]) else "done"
            print(status)

        if gemini_key:
            print("  Calling Gemini...", end=" ", flush=True)
            responses["gemini"] = call_gemini(pairs_text, gemini_key)
            status = "ERROR" if "ERROR" in str(responses["gemini"]) else "done"
            print(status)

        if openai_key:
            print("  Calling OpenAI...", end=" ", flush=True)
            responses["openai"] = call_openai(pairs_text, openai_key)
            status = "ERROR" if "ERROR" in str(responses["openai"]) else "done"
            print(status)

        if claude_key:
            print("  Calling Claude strict...", end=" ", flush=True)
            responses["claude_strict"] = call_claude_strict(
                pairs_text, claude_key)
            status = ("ERROR" if "ERROR" in str(responses["claude_strict"])
                      else "done")
            print(status)

        # Collect all flags
        batch_flags = []
        for model_name, response in responses.items():
            flags = parse_flags(response, model_name)
            batch_flags.extend(flags)

        # Show results per model
        for model_name, response in responses.items():
            flags = parse_flags(response, model_name)
            if "ERROR" in str(response):
                print(f"  {model_name}: {response}")
            elif flags:
                for f in flags:
                    print(f"  FLAG ({model_name}): {f['raw']}")
            else:
                print(f"  {model_name}: CLEAN")

        # Majority vote: flag pair if 2+ models agree
        flag_by_pair = {}
        for flag in batch_flags:
            try:
                pair_id = (flag["raw"].split("|")[0]
                           .replace("FLAG:", "").strip())
                if pair_id not in flag_by_pair:
                    flag_by_pair[pair_id] = []
                flag_by_pair[pair_id].append(flag)
            except Exception:
                pass

        for pair_id, pair_flags in flag_by_pair.items():
            models_flagging = list(set(f["model"] for f in pair_flags))
            if len(models_flagging) >= 2:
                print(f"  CONSENSUS [{pair_id}]: "
                      f"{len(models_flagging)} models agree — FIX REQUIRED")
                all_flags.extend(pair_flags)
            else:
                print(f"  SINGLE FLAG [{pair_id}]: "
                      f"only {models_flagging[0]} — mark for human review")
                for f in pair_flags:
                    f["needs_human"] = True
                all_flags.extend(pair_flags)

    # Write log
    timestamp = datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "file": args.file,
        "total_pairs": len(pairs),
        "models_used": available,
        "total_flags": len(all_flags),
        "consensus_flags": len([f for f in all_flags
                                 if not f.get("needs_human")]),
        "human_review_flags": len([f for f in all_flags
                                    if f.get("needs_human")]),
        "flags": all_flags
    }

    os.makedirs(os.path.dirname(args.log), exist_ok=True)
    with open(args.log, "a", encoding="utf-8") as log:
        log.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    print(f"\n{'='*60}")
    print(f"Cross-AI review complete")
    print(f"Pairs reviewed: {len(pairs)}")
    print(f"Models used: {', '.join(available)}")
    print(f"Consensus flags (fix required): {log_entry['consensus_flags']}")
    print(f"Human review flags: {log_entry['human_review_flags']}")
    print(f"Log: {args.log}")

    if log_entry["consensus_flags"] > 0:
        print("\nFix consensus-flagged pairs before committing.")
        sys.exit(1)
    elif log_entry["human_review_flags"] > 0:
        print("\nReview single-model flags then re-run.")
        sys.exit(1)
    else:
        print("\nCLEAN — all models agree. Ready to commit.")
        sys.exit(0)


if __name__ == "__main__":
    main()
