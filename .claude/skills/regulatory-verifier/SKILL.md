# REGULATORY-VERIFIER

## CONFIRMED STATUS (June 2026)
Working models:
- Gemini gemini-3.5-flash — free, confirmed working
- OpenRouter meta-llama/llama-3.3-70b-instruct:free — confirmed not geo-blocked

IP-blocked in Tanzania (do NOT use):
- Groq — blocked at ISP/Cloudflare level
- Cerebras — blocked at ISP/Cloudflare level

Do NOT use (other reasons):
- Brave Search — blocked by TRA registration requirement
- Perplexity — requires upfront payment

## API keys required
```powershell
# Free — get at aistudio.google.com
[System.Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "AQ.your-key", "User")

# Free — get at openrouter.ai
[System.Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY", "sk-or-your-key", "User")

# Optional — free credits at platform.openai.com
[System.Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-proj-your-key", "User")
```

## When to activate
After every 50-pair CHECKPOINT-SAVER save.
Before any batch moves from raw_sources to cleaned_pairs.

## Three-layer verification

### LAYER 1: Locked facts check (FACT-GUARDIAN)
Run: python scripts/check_locked_facts.py --file [batch_file]

### LAYER 2: Gemini review (gemini-3.5-flash)
Free. Confirmed working June 2026.

### LAYER 3: OpenRouter review (llama-3.3-70b-instruct:free)
Free. Not geo-blocked. Confirmed working June 2026.

## Majority vote rule
2+ models flag same pair → CONSENSUS — block, fix before commit
1 model flags → SINGLE — route to needs_human_review folder
All clean → COMMIT

## Critical: false-clean prevention
If ALL models return errors the script must exit with code 1
NOT silently report CLEAN. A clean with no models responding
is a false clean and must be treated as a failure.

## Run after every 50-pair save
```bash
python scripts/verify_pairs.py --file [batch_file.jsonl]
```

## Log all results
Every result written to: scripts/verification_log.jsonl
Flagged pairs routed by FLAGGED-PAIR-ROUTER skill.
