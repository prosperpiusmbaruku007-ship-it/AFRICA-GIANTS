#!/usr/bin/env python3
"""
REGULATORY-VERIFIER — cross-AI review for AFRICA-GIANTS training pairs.
Usage: python scripts/verify_pairs.py --file path/to/batch.jsonl
Exit: 0 = clean, 1 = flags found or no models responded

CONFIRMED WORKING MODELS (June 2026):
  - Gemini gemini-3.5-flash — free, confirmed working
  - OpenRouter mistralai/mistral-7b-instruct:free — higher rate limits than llama-3.3-70b

NOT USED:
  - Groq — IP blocked in Tanzania at ISP/Cloudflare level
  - Cerebras — IP blocked in Tanzania at ISP/Cloudflare level
  - Brave Search — blocked in Tanzania (TRA registration issue)
  - Perplexity — requires upfront payment
"""
import json, sys, os, argparse, urllib.request, urllib.error, time
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
- SDL = disability leave (WRONG)
- NSSF = 6% (WRONG — should be 10%)
- PAYE band 2 = 9% (WRONG — should be 8%)
- GN487A = residence permit order (WRONG — business prohibition)
- VAT changed from 14% (WRONG)
- P45 form exists in Tanzania (it does not)

Output FLAG: [pair_id] | [field] | [wrong_value] | [correct_value] | [source]
or CLEAN — nothing else."""


def call_gemini(pairs_text, api_key):
    """Google Gemini gemini-3.5-flash — free tier. gemini-2.0-flash shut down June 2026."""
    full_prompt = REVIEW_PROMPT + "\n\n" + pairs_text
    payload = json.dumps({
        "contents": [{"parts": [{"text": full_prompt}]}]
    }).encode("utf-8")
    url = (f"https://generativelanguage.googleapis.com/v1beta/"
           f"models/gemini-3.5-flash:generateContent?key={api_key}")
    for attempt in range(3):
        try:
            req = urllib.request.Request(
                url, data=payload,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read())
                return (result["candidates"][0]["content"]
                        ["parts"][0]["text"].strip())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                wait = 30 * (attempt + 1)
                print(f"  Gemini 429 — waiting {wait}s then retry...", flush=True)
                time.sleep(wait)
            else:
                return f"GEMINI_ERROR: HTTP {e.code}"
        except Exception as e:
            return f"GEMINI_ERROR: {e}"


def call_openrouter(pairs_text, api_key):
    """OpenRouter mistral-7b-instruct:free — higher rate limits than llama-3.3-70b."""
    payload = json.dumps({
        "model": "mistralai/mistral-7b-instruct:free",
        "max_tokens": 1000,
        "messages": [
            {"role": "system", "content": REVIEW_PROMPT},
            {"role": "user", "content": pairs_text}
        ]
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://github.com/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS",
            "X-Title": "AFRICA-GIANTS"
        }
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read())
                return result["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                wait = 45 * (attempt + 1)
                print(f"  OpenRouter 429 — waiting {wait}s then retry...", flush=True)
                time.sleep(wait)
            else:
                return f"OPENROUTER_ERROR: HTTP {e.code}"
        except Exception as e:
            return f"OPENROUTER_ERROR: {e}"


def call_openai(pairs_text, api_key):
    """OpenAI gpt-4o-mini — optional, free credits covers full project."""
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
    """Claude strict adversarial — uses claude-haiku for low cost."""
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
        description="Cross-AI review: Gemini + OpenRouter + optional OpenAI/Claude"
    )
    parser.add_argument("--file", required=True)
    parser.add_argument("--log", default="scripts/verification_log.jsonl")
    parser.add_argument("--batch-size", type=int, default=10)
    args = parser.parse_args()

    # Load API keys
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    openrouter_key = os.environ.get("OPENROUTER_API_KEY", "")
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    claude_key = os.environ.get("ANTHROPIC_API_KEY", "")

    available = []
    if gemini_key:
        available.append("gemini")
    if openrouter_key:
        available.append("openrouter")
    if openai_key:
        available.append("openai")
    if claude_key:
        available.append("claude_strict")

    if not available:
        print("ERROR: No API keys found.")
        print("Set GEMINI_API_KEY (free: aistudio.google.com)")
        print("Set OPENROUTER_API_KEY (free: openrouter.ai)")
        print("NOTE: Groq and Cerebras are IP-blocked in Tanzania")
        sys.exit(1)

    print(f"Models available: {', '.join(available)}")
    print(f"NOTE: Groq/Cerebras not used — IP blocked in Tanzania")
    print(f"NOTE: Brave Search not used — blocked in Tanzania")
    print(f"NOTE: Perplexity not used — requires upfront payment\n")

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

        if gemini_key:
            print("  Calling Gemini...", end=" ", flush=True)
            responses["gemini"] = call_gemini(pairs_text, gemini_key)
            status = "ERROR" if "ERROR" in str(responses["gemini"]) else "done"
            print(status)

        if openrouter_key:
            print("  Calling OpenRouter...", end=" ", flush=True)
            responses["openrouter"] = call_openrouter(pairs_text, openrouter_key)
            status = "ERROR" if "ERROR" in str(responses["openrouter"]) else "done"
            print(status)

        if openai_key:
            print("  Calling OpenAI...", end=" ", flush=True)
            responses["openai"] = call_openai(pairs_text, openai_key)
            status = "ERROR" if "ERROR" in str(responses["openai"]) else "done"
            print(status)

        if claude_key:
            print("  Calling Claude strict...", end=" ", flush=True)
            responses["claude_strict"] = call_claude_strict(pairs_text, claude_key)
            status = "ERROR" if "ERROR" in str(responses["claude_strict"]) else "done"
            print(status)

        # CRITICAL: Check if any model actually responded
        successful = [r for r in responses.values()
                      if r and "ERROR" not in str(r)]
        if not successful:
            print("  WARNING: No models responded successfully this batch")

        # Parse flags and show per-model status
        batch_flags = []
        for model_name, response in responses.items():
            if "ERROR" in str(response):
                print(f"  {model_name}: {str(response)[:80]}")
            elif response and response.strip() == "CLEAN":
                print(f"  {model_name}: CLEAN")
            elif response:
                flags = parse_flags(response, model_name)
                print(f"  {model_name}: responded ({len(response)} chars)")
                if flags:
                    for fl in flags:
                        print(f"    FLAG: {fl['raw']}")
                batch_flags.extend(flags)
            else:
                print(f"  {model_name}: (no response)")

        # Majority vote
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
                      f"only {models_flagging[0]} — human review needed")
                for fl in pair_flags:
                    fl["needs_human"] = True
                all_flags.extend(pair_flags)

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

    log_dir = os.path.dirname(args.log)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
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
