#!/usr/bin/env python3
"""
Persistent cross-AI reviewer for batch_004.
Rules:
  - Gemini 503 or 429: wait 60s and retry same batch
  - OpenRouter 429: wait 45s and retry
  - All models error on a batch: wait 90s and retry
  - Never skip a batch — retry until at least one model responds
Output: scripts/verify_batch004_log.txt + appends to scripts/verification_log.jsonl
"""
import json, os, sys, time, re, urllib.request, urllib.error
from datetime import datetime

BATCH_FILE = "datasets/tier1a/raw_sources/raw_pairs_batch_004.jsonl"
LOG_FILE   = "scripts/verify_batch004_log.txt"
JSONL_LOG  = "scripts/verification_log.jsonl"
BATCH_SIZE = 20

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
- GN 605A average minimum wage described as TZS 275,060 (WRONG — old rate, now 358,322)
- 2022 Wage Order described as still valid (WRONG — revoked effective 1 Jan 2026)
- OSHA registration threshold described as 5 employees (WRONG — 10)
- WCF rate described as 1% (WRONG — 0.5%)

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


def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def call_gemini(pairs_text, api_key):
    payload = json.dumps({
        "contents": [{"parts": [{"text": REVIEW_PROMPT + "\n\n" + pairs_text}]}]
    }).encode("utf-8")
    url = (f"https://generativelanguage.googleapis.com/v1beta/"
           f"models/gemini-3.5-flash:generateContent?key={api_key}")
    try:
        req = urllib.request.Request(url, data=payload,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=90) as resp:
            result = json.loads(resp.read())
            return result["candidates"][0]["content"]["parts"][0]["text"].strip()
    except urllib.error.HTTPError as e:
        return f"GEMINI_ERROR:{e.code}"
    except Exception as e:
        return f"GEMINI_ERROR:{e}"


def call_openrouter(pairs_text, api_key):
    payload = json.dumps({
        "model": "openrouter/auto",
        "max_tokens": 1000,
        "messages": [
            {"role": "system", "content": REVIEW_PROMPT},
            {"role": "user",   "content": pairs_text}
        ]
    }).encode("utf-8")
    try:
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
        with urllib.request.urlopen(req, timeout=90) as resp:
            result = json.loads(resp.read())
            return result["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as e:
        return f"OPENROUTER_ERROR:{e.code}"
    except Exception as e:
        return f"OPENROUTER_ERROR:{e}"


def format_pairs(pairs, batch_num):
    lines = [f"BATCH {batch_num} — Tanzania regulatory Q&A pairs:\n"]
    for p in pairs:
        lines.append(f"PAIR_ID: {p.get('id','unknown')}")
        lines.append(f"Q: {p.get('question_en','')}")
        lines.append(f"A: {p.get('answer_en','')}")
        lines.append("")
    return "\n".join(lines)


def parse_flags(response, model):
    flags = []
    if not response or "ERROR" in str(response):
        return flags
    for line in response.strip().split("\n"):
        line = line.strip()
        if line.startswith("FLAG:"):
            flags.append({"model": model, "raw": line})
    return flags


def review_batch_with_retry(pairs, batch_num, total_batches, gemini_key, or_key):
    """Keep retrying until at least one model returns a valid response."""
    attempt = 0
    while True:
        attempt += 1
        pairs_text = format_pairs(pairs, batch_num)
        log(f"Batch {batch_num}/{total_batches} (pairs {(batch_num-1)*BATCH_SIZE+1}"
            f"-{(batch_num-1)*BATCH_SIZE+len(pairs)}) — attempt {attempt}")

        responses = {}

        # --- Gemini ---
        if gemini_key:
            log("  Gemini calling...")
            gr = call_gemini(pairs_text, gemini_key)
            if gr.startswith("GEMINI_ERROR:503") or gr.startswith("GEMINI_ERROR:429"):
                code = gr.split(":")[1]
                log(f"  Gemini {code} — waiting 60s...")
                time.sleep(60)
                gr = call_gemini(pairs_text, gemini_key)
                if gr.startswith("GEMINI_ERROR:"):
                    log(f"  Gemini still erroring: {gr}")
                else:
                    log(f"  Gemini: OK after retry")
            elif gr.startswith("GEMINI_ERROR:"):
                log(f"  Gemini error: {gr}")
            else:
                log(f"  Gemini: responded ({len(gr)} chars)")
            responses["gemini"] = gr

        # --- OpenRouter ---
        if or_key:
            log("  OpenRouter calling...")
            orr = call_openrouter(pairs_text, or_key)
            if "OPENROUTER_ERROR:429" in orr:
                log("  OpenRouter 429 — waiting 45s...")
                time.sleep(45)
                orr = call_openrouter(pairs_text, or_key)
                if orr.startswith("OPENROUTER_ERROR:"):
                    log(f"  OpenRouter still erroring: {orr}")
                else:
                    log(f"  OpenRouter: OK after retry")
            elif orr.startswith("OPENROUTER_ERROR:"):
                log(f"  OpenRouter error: {orr}")
            else:
                log(f"  OpenRouter: responded ({len(orr)} chars)")
            responses["openrouter"] = orr

        # --- Check if any model succeeded ---
        successful = {k: v for k, v in responses.items()
                      if v and not v.startswith(("GEMINI_ERROR", "OPENROUTER_ERROR"))}

        if not successful:
            log(f"  All models errored — waiting 90s before retry...")
            time.sleep(90)
            continue  # retry same batch

        # --- Parse results ---
        all_flags = []
        for model, response in responses.items():
            if response and not response.startswith(("GEMINI_ERROR", "OPENROUTER_ERROR")):
                if response.strip() == "CLEAN":
                    log(f"  {model}: CLEAN")
                else:
                    flags = parse_flags(response, model)
                    if flags:
                        log(f"  {model}: {len(flags)} flag(s)")
                        for fl in flags:
                            log(f"    {fl['raw']}")
                        all_flags.extend(flags)
                    else:
                        log(f"  {model}: responded, no FLAGS found")
            else:
                log(f"  {model}: {str(response)[:80]}")

        # Majority vote
        flag_by_pair = {}
        for flag in all_flags:
            try:
                pair_id = flag["raw"].split("|")[0].replace("FLAG:", "").strip()
                flag_by_pair.setdefault(pair_id, []).append(flag)
            except Exception:
                pass

        consensus = []
        human_review = []
        for pair_id, pf in flag_by_pair.items():
            models_flagging = list(set(f["model"] for f in pf))
            if len(models_flagging) >= 2:
                log(f"  CONSENSUS [{pair_id}]: {len(models_flagging)} models — FIX REQUIRED")
                consensus.extend(pf)
            else:
                log(f"  SINGLE FLAG [{pair_id}]: only {models_flagging[0]} — human review")
                for f in pf:
                    f["needs_human"] = True
                human_review.extend(pf)

        return {
            "batch": batch_num,
            "responses": responses,
            "all_flags": all_flags,
            "consensus": consensus,
            "human_review": human_review,
        }


def main():
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    or_key     = os.environ.get("OPENROUTER_API_KEY", "")

    if not gemini_key and not or_key:
        print("ERROR: No API keys found. Set GEMINI_API_KEY or OPENROUTER_API_KEY.")
        sys.exit(1)

    # Header
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"batch_004 cross-AI review — started {datetime.now().isoformat()}\n")
        f.write(f"File: {BATCH_FILE}\n")
        f.write(f"Models: {'gemini ' if gemini_key else ''}{'openrouter' if or_key else ''}\n")
        f.write("=" * 60 + "\n\n")

    log(f"Starting batch_004 cross-AI review")
    log(f"Gemini: {'SET' if gemini_key else 'NOT SET'}")
    log(f"OpenRouter: {'SET' if or_key else 'NOT SET'}")

    # Load pairs
    pairs = [json.loads(l) for l in open(BATCH_FILE, encoding="utf-8") if l.strip()]
    log(f"Loaded {len(pairs)} pairs, batch size {BATCH_SIZE}")

    total_batches = (len(pairs) + BATCH_SIZE - 1) // BATCH_SIZE
    all_results = []
    total_consensus = 0
    total_human = 0

    for batch_idx in range(total_batches):
        start = batch_idx * BATCH_SIZE
        batch = pairs[start:start + BATCH_SIZE]
        result = review_batch_with_retry(
            batch, batch_idx + 1, total_batches, gemini_key, or_key
        )
        all_results.append(result)
        total_consensus += len(result["consensus"])
        total_human     += len(result["human_review"])
        log(f"  Batch {batch_idx+1} done — cumulative: {total_consensus} consensus, "
            f"{total_human} human review")
        # Brief pause between batches to be respectful of rate limits
        if batch_idx < total_batches - 1:
            time.sleep(5)

    # Summary
    log("")
    log("=" * 60)
    log("CROSS-AI REVIEW COMPLETE")
    log(f"Pairs reviewed: {len(pairs)}")
    log(f"Batches: {total_batches}")
    log(f"Consensus flags (fix required): {total_consensus}")
    log(f"Human review flags: {total_human}")

    # Write to verification_log.jsonl
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "file": BATCH_FILE,
        "total_pairs": len(pairs),
        "models_used": ([("gemini" if gemini_key else "")] +
                        [("openrouter" if or_key else "")]),
        "total_flags": total_consensus + total_human,
        "consensus_flags": total_consensus,
        "human_review_flags": total_human,
        "flags": [f for r in all_results for f in r["all_flags"]],
    }
    with open(JSONL_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    log(f"Log written: {LOG_FILE}")
    log(f"JSONL log appended: {JSONL_LOG}")

    if total_consensus > 0:
        log("ACTION REQUIRED: fix consensus-flagged pairs before committing to cleaned_pairs/")
        sys.exit(1)
    elif total_human > 0:
        log("ACTION SUGGESTED: review single-model flags before finalising")
        sys.exit(1)
    else:
        log("CLEAN — all models agree. batch_004 ready for cleaned_pairs/")
        sys.exit(0)


if __name__ == "__main__":
    main()
