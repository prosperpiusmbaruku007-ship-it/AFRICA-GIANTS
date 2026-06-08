# GIT-PUSH-GUARD

## Purpose
Scan all staged files (and optionally all modified files) for API key
patterns before any git commit or push. Reject if found.

## When to activate
Before every git add and git commit touching any file.
Especially before commits to scripts/ and PROGRESS.md.

## Known patterns that leaked this project
- OpenRouter keys: sk-or-
- Groq keys: gsk_
- Anthropic keys: sk-ant-
- OpenAI keys: sk-proj-
- HuggingFace tokens: hf_
- Gemini keys: AQ.
- GitHub tokens: github_pat_ or ghp_
- Cerebras keys: csk-

## Step 1: Scan staged files before commit
python scripts/scan_for_keys.py

## Step 2: If any key found
- Do NOT commit
- Show which file and which line
- Remove the key from the file
- Replace with: os.environ.get("KEY_NAME", "")
- Re-run scan until clean

## Step 3: Only if scan returns clean
Proceed with git commit and push.

## Pass case
No key patterns found in staged files.
Output: CLEAN — no API keys detected. Safe to commit.

## Fail case
sk-or-v1abc found in scripts/verify_pairs.py line 45.
Output: BLOCKED — API key detected. Remove before committing.

## Why os.environ.get is NOT a safe bypass
A line like:
  openrouter_key = os.environ.get("OPENROUTER_API_KEY", "sk-or-v1-realkey")
still contains a real key as the default argument. The scan
flags the actual key pattern regardless of surrounding context.
Only true placeholders (YOUR_KEY_HERE, sk-or-v1-...) are skipped.
