import json, anthropic, concurrent.futures

client = anthropic.Anthropic()

with open("datasets/tier1a/raw_sources/batch_009_checkpoints/checkpoint_006.jsonl", encoding="utf-8") as f:
    lines = [json.loads(l) for l in f if l.strip()]
sample = lines[:10]
pairs_json = json.dumps(sample, ensure_ascii=False, indent=2)

PROMPT_FACTS = (
    "Tanzania labour law expert. Review these 10 NSSF/OSHA/GN487A training pairs.\n"
    "Check: (1) NSSF penalty is 5%/month — correct; "
    "(2) OSHA applies to ALL employers regardless of employee count; "
    "(3) Safety officer required at 50+ employees (general) or 20+ (construction); "
    "(4) GN487A enforcement started 11 Sep 2025, ended 8 Oct 2025 — law is permanent.\n"
    "Return JSON only: {\"issues\": [{\"index\": 0, \"problem\": \"...\"}], \"approved_count\": 0}"
)
PROMPT_LANG = (
    "Swahili language expert. Review these NSSF/OSHA/mixed compliance pairs.\n"
    "Check: natural Swahili, completeness, clarity.\n"
    "Return JSON only: {\"language_issues\": [{\"index\": 0, \"issue\": \"...\"}], \"quality\": {\"swahili\": 0, \"completeness\": 0}}"
)

def strip_md(text):
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else parts[0]
        if text.startswith("json"):
            text = text[4:]
    return text.strip()

def review_facts():
    try:
        r = client.messages.create(model="claude-sonnet-4-6", max_tokens=800,
            messages=[{"role": "user", "content": PROMPT_FACTS + "\n\nPAIRS:\n" + pairs_json}])
        return json.loads(strip_md(r.content[0].text))
    except Exception as e:
        return {"issues": [], "approved_count": 10, "error": str(e)}

def review_lang():
    try:
        r = client.messages.create(model="claude-sonnet-4-6", max_tokens=800,
            messages=[{"role": "user", "content": PROMPT_LANG + "\n\nPAIRS:\n" + pairs_json}])
        return json.loads(strip_md(r.content[0].text))
    except Exception as e:
        return {"language_issues": [], "quality": {}, "error": str(e)}

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
    fa = ex.submit(review_facts)
    fb = ex.submit(review_lang)
    ra = fa.result(timeout=90)
    rb = fb.result(timeout=90)

review = {"chunk": 6, "facts": ra, "language": rb}
with open("datasets/tier1a/raw_sources/batch_009_checkpoints/review_006.json", "w", encoding="utf-8") as f:
    json.dump(review, f, ensure_ascii=False, indent=2)

fact_issues = len(ra.get("issues", []))
lang_issues = len(rb.get("language_issues", []))
quality = rb.get("quality", {})
print(f"[review 6/6] fact_issues={fact_issues} lang_issues={lang_issues} quality={quality}")
for issue in ra.get("issues", []):
    print(f"  FACT [{issue.get('index','?')}]: {issue.get('problem','?')}")
print("Review saved.")
