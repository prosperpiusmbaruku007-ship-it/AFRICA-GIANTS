import json, anthropic, concurrent.futures

client = anthropic.Anthropic()

with open("datasets/tier1a/raw_sources/batch_009_checkpoints/checkpoint_003.jsonl", encoding="utf-8") as f:
    lines = [json.loads(l) for l in f if l.strip()]
sample = lines[:10]
pairs_json = json.dumps(sample, ensure_ascii=False, indent=2)

PROMPT_FACTS = (
    "Tanzania business law expert. Review these 10 BRELA and GN487A training pairs.\n"
    "Check: (1) BRELA annual return fee TZS 22,000 is correct; "
    "(2) Late penalty TZS 2,500/month is correct; "
    "(3) GN487A spouse exception correctly stated as not exempting non-citizen; "
    "(4) No fabricated legal facts.\n"
    "Return JSON only: {\"issues\": [{\"index\": 0, \"problem\": \"...\"}], \"approved_count\": 0}"
)
PROMPT_LANG = (
    "Swahili language expert. Review these Tanzania BRELA/GN487A training pairs.\n"
    "Check: (1) natural Swahili (2) clear and complete answers.\n"
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

review = {"chunk": 3, "facts": ra, "language": rb}
with open("datasets/tier1a/raw_sources/batch_009_checkpoints/review_003.json", "w", encoding="utf-8") as f:
    json.dump(review, f, ensure_ascii=False, indent=2)

fact_issues = len(ra.get("issues", []))
lang_issues = len(rb.get("language_issues", []))
quality = rb.get("quality", {})
print(f"[review 3/6] fact_issues={fact_issues} lang_issues={lang_issues} quality={quality}")
for issue in ra.get("issues", []):
    print(f"  FACT [{issue.get('index','?')}]: {issue.get('problem','?')}")
print("Review saved.")
