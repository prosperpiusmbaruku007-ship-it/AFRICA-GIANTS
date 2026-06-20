"""Agent 4: Review batch_012 checkpoints against locked_facts using Anthropic API."""
import json, glob, os
from anthropic import Anthropic

client = Anthropic()

with open("scripts/locked_facts.json") as f:
    locked_facts = json.load(f)

OUT_DIR = "datasets/tier1a/raw_sources/batch_012_checkpoints"
fail_tracker = {}
escalate_to_agent2 = []

def review_checkpoint(pairs, subdomain, ck_num, locked_facts):
    facts_text = json.dumps(
        {k: v for k, v in locked_facts.items() if not k.startswith("_")},
        ensure_ascii=False, indent=2
    )
    pairs_text = json.dumps(pairs, ensure_ascii=False, indent=2)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        messages=[{
            "role": "user",
            "content": f"""You are a strict fact and math reviewer for a Tanzanian business compliance AI.

Review checkpoint {ck_num} for subdomain '{subdomain}' — {len(pairs)} pairs.

LOCKED FACTS (absolute source of truth):
{facts_text}

STRICT REVIEW RULES — flag FAIL for any of these:
1. VAT_WITHHOLDING pairs: any pair stating specific calculation formula "3% ya VAT amount" or "3% ya invoice" — must hedge with thibitisha na TRA
2. GN605A sector rates: any rate NOT in GN605A_key_sector_rates — only Agricultural 175k, Hotel 5/4-star 375k, Hotel bars 195k, Mining 695k, Energy international 765.9k, Commercial banks 733k, Construction Class I 515k, Telecom 644k, Industrial 200k
3. BRELA pairs: any specific TZS fee stated — must say angalia brela.go.tz
4. Any percentage, rate, TZS amount, or date contradicting locked_facts
5. Math calculation error
6. OUT_OF_CORPUS pairs missing approved refusal phrase (nje ya maarifa yangu / swali hili liko nje / sina uhakika / mshauri wa kodi / wasiliana na mshauri)
7. Unnatural keyword stuffing that breaks Swahili fluency
8. VAT_WITHHOLDING: any pair claiming to state exact withholding percentage without hedge

For each FAIL:
FAIL [pair_index_0based] | TYPE: FACT_ERROR or LANGUAGE_ERROR | REASON: [exact issue] | FIX: [what to change]

End your response with exactly these lines:
PASS_COUNT: X
FAIL_COUNT: Y
FACT_ERRORS: [list of 0-based pair indices with fact errors, or NONE]
LANGUAGE_ERRORS: [list of 0-based pair indices with language issues, or NONE]

Pairs to review:
{pairs_text}"""
        }]
    )
    return response.content[0].text

subdomains = [
    "vat_withholding",
    "efd_compliance",
    "vat_registration",
    "sdl_compliance",
    "brela_registration",
    "nssf_contributions",
    "osha_registration",
    "out_of_corpus",
]

all_review_results = {}

for subdomain in subdomains:
    ck_files = sorted(glob.glob(f"{OUT_DIR}/ck_{subdomain}_*.jsonl"))
    if not ck_files:
        print(f"[Agent 4] No checkpoint files for {subdomain}")
        continue

    subdomain_results = []
    for ck_file in ck_files:
        ck_num = ck_file.replace("\\", "/").split("/")[-1].replace(".jsonl", "").split("_")[-1]
        with open(ck_file, encoding="utf-8") as f:
            pairs = [json.loads(l) for l in f if l.strip()]
        print(f"\n[Agent 4] Reviewing {subdomain} ck_{ck_num} — {len(pairs)} pairs ...")
        result = review_checkpoint(pairs, subdomain, ck_num, locked_facts)
        subdomain_results.append({"checkpoint": ck_num, "result": result, "pairs": pairs})
        print(result)

        # Track failures
        lines = result.split("\n")
        for line in lines:
            if line.startswith("FAIL "):
                parts = line.split("|")
                if len(parts) >= 2:
                    try:
                        idx = int(parts[0].replace("FAIL", "").strip())
                        pair_key = f"{subdomain}_{ck_num}_{idx}"
                        is_fact = "FACT_ERROR" in parts[1]
                        fail_tracker[pair_key] = fail_tracker.get(pair_key, 0) + 1
                        if fail_tracker[pair_key] >= 2 and is_fact:
                            escalate_to_agent2.append({
                                "subdomain": subdomain,
                                "pair_index": idx,
                                "checkpoint": ck_num,
                                "pair": pairs[idx] if idx < len(pairs) else None
                            })
                    except ValueError:
                        pass

    all_review_results[subdomain] = subdomain_results

review_path = os.path.join(OUT_DIR, "review_results.json")
with open(review_path, "w", encoding="utf-8") as f:
    json.dump(all_review_results, f, ensure_ascii=False, indent=2)

print(f"\n[Agent 4] Review complete. Results saved: {review_path}")

# Summary
total_pass = 0
total_fail = 0
for sd, results in all_review_results.items():
    sd_pass = 0
    sd_fail = 0
    for r in results:
        text = r["result"]
        for line in text.split("\n"):
            if line.startswith("PASS_COUNT:"):
                try: sd_pass += int(line.split(":")[1].strip())
                except: pass
            if line.startswith("FAIL_COUNT:"):
                try: sd_fail += int(line.split(":")[1].strip())
                except: pass
    total_pass += sd_pass
    total_fail += sd_fail
    print(f"  {sd}: PASS={sd_pass} FAIL={sd_fail}")

print(f"\nOVERALL: PASS={total_pass} FAIL={total_fail}")
print(f"Pairs needing rewrite: {sum(1 for v in fail_tracker.values() if v == 1)}")
print(f"Facts escalated to Agent 2: {len(escalate_to_agent2)}")

if escalate_to_agent2:
    print("\nEscalated facts:")
    for e in escalate_to_agent2:
        print(f"  {e['subdomain']} ck_{e['checkpoint']} pair_{e['pair_index']}")
