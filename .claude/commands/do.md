#Read this file completely then execute every instruction below exactly as written.

# Batch 013 — Correction pairs for Africa Giants v8

This is a correction batch targeting exact failure patterns from the v7 accuracy gate analysis.
Run this entire file as a task. Read every step before starting.

## STEP 0 — CONFIRM STARTING STATE

```python
import json, glob

with open('datasets/tier1a/locked_facts.json') as f:
    facts = json.load(f)
assert len(facts) >= 85, f"locked_facts too short: {len(facts)}"
print(f"locked_facts OK: {len(facts)} entries")
for key in ['VAT_zero_rated_vs_exempt_input_VAT', 'BRELA_COSOTA_split',
            'SDL_source_law', 'OSHA_annual_inspection',
            'gn487a_penalty_citizen_facilitator', 'OSHA_safety_officer_threshold']:
    print(f"  {'OK' if key in facts else 'MISSING'} — {key}")

total = sum(1 for fp in glob.glob('datasets/tier1a/cleaned_pairs/*.jsonl')
            for l in open(fp) if l.strip())
print(f"Current dataset total: {total} pairs")
assert total >= 2537, f"Dataset too small: {total}"

with open('datasets/tier1a/raw_sources/raw_pairs_batch_001.jsonl') as f:
    for i, line in enumerate(f):
        if i >= 2: break
        print(json.loads(line))
```

Do not proceed until all checks pass.

## STEP 1 — AGENT 2: FACT FETCHER

Print all current keys in locked_facts.json first. Then fetch exactly 5 facts needed for batch_013 that are NOT already in locked_facts.json:

Fact 1 — GN487A mgeni definition: does GN487A exclude dual citizens with Tanzanian passport?
- Fetch: https://www.clydeco.com/en/insights/2025/07/practical-implications-of-the-business-licensing
- Confirm: non-citizen defined by Tanzania Citizenship Act Cap.357 — dual citizens with Tanzanian passport are NOT excluded

Fact 2 — GN487A msaidizi exact definition
- Fetch: https://velmalaw.co.tz/news/prohibited-non-tanzanian-business-activities/
- Confirm: msaidizi is a Tanzanian who lends their name, licence, or identity to allow a foreigner to operate a prohibited business

Fact 3 — Marriage to Tanzanian and GN487A status
- Fetch: https://www.clydeco.com/en/insights/2025/07/practical-implications-of-the-business-licensing
- Confirm: marriage to a Tanzanian does not grant citizen status or GN487A exemption

Fact 4 — VAT withholding: who remits to TRA
- Fetch: https://www.tra.go.tz/page/value-added-tax-vat
- Confirm: qualifying buyer (withholding agent) remits directly to TRA — NOT the supplier

Fact 5 — EFD: TRA authority to close business
- Fetch: https://www.tra.go.tz/page/electronic-fiscal-devices
- Confirm: TRA has authority to suspend licence and close premises for repeated EFD non-compliance

For each fact:
- Confirmed: add to locked_facts.json with source URL and status LOCKED
- Unverifiable: add with status HEDGE

After adding all 5 commit:
`git commit -m 'locked_facts: Agent 2 pre-batch_013 — 5 new entries'`

## STEP 2 — BUILD DEDUP INDEX

```python
import json, glob

seen = set()
for filepath in sorted(glob.glob('datasets/tier1a/cleaned_pairs/*.jsonl')):
    with open(filepath) as f:
        for line in f:
            if line.strip():
                d = json.loads(line)
                key = (d.get('instruction','') + d.get('output',''))[:120].lower().strip()
                seen.add(key)
print(f"Dedup index built: {len(seen)} existing pairs indexed")

def is_duplicate(pair, seen_set):
    key = (pair.get('instruction','') + pair.get('output',''))[:120].lower().strip()
    return key in seen_set

def register_pair(pair, seen_set):
    key = (pair.get('instruction','') + pair.get('output',''))[:120].lower().strip()
    seen_set.add(key)
```

## STEP 3 — AGENT 3: PAIR WRITER

Create directory: `datasets/tier1a/raw_sources/batch_013_checkpoints/`

Read locked_facts.json fully before writing any pair.

CRITICAL RULES — violations cause FAIL in Agent 4 review:
- VAT withholding: BUYER remits to TRA — never say supplier remits
- VAT withholding certificate: issued on day VAT becomes payable — NOT the 20th
- VAT zero-rated: suppliers CAN claim input VAT — never invert this
- GN487A: BOTH parties penalised — never say only the foreigner
- SDL source law: VET Act Cap.82 — never cite VAT Act or Income Tax Act
- GN605B does not exist — always write GN605A
- OSHA safety officer: HEDGE — never state specific employee number
- BRELA: trademarks/patents. COSOTA: copyright. ORT does not exist
- EFD closure: always write kufunga (close) — never kufungua (open)

FORMAT for every pair:
```json
{"instruction": "[question in Swahili]", "input": "", "output": "[answer in Swahili]", "system": "Jina lako ni Chike, mshauri wa biashara kutoka Africa Giants. Kauli mbiu yako ni: Fahamu Biashara Yako, Maarifa Yako. Unajibu maswali kuhusu biashara, kodi, BRELA, TRA, NSSF, OSHA, SDL, PAYE, VAT kwa Kiswahili na Kiingereza. Kama swali liko nje ya mada yako sema wazi kwamba halijui na mwelekeze kwa mtaalamu."}
```

SAVE PATTERN — 10 pairs at a time. After every 10 pairs save immediately to checkpoint file. Never hold more than 10 pairs in memory per subdomain.

Checkpoint naming:
`batch_013_checkpoints/ck_[subdomain]_001.jsonl` — pairs 1-10
`batch_013_checkpoints/ck_[subdomain]_002.jsonl` — pairs 11-20

After each save print: `[Agent 3] Saved ck_[subdomain]_NNN.jsonl — 10 pairs`

### Subdomain targets:

**VAT_WITHHOLDING_CORRECTION — 20 pairs (2 checkpoints)**
Target failures: eval_037, eval_042, eval_048
Keywords in output: `anayehitimu`, `anakata`, `certificate`, `wizara`, `moja kwa moja`, `kupeleka`
Topics: buyer remits moja kwa moja to TRA; certificate issued day VAT payable not 20th; 20th is remittance deadline not certificate date; supplier receives remaining VAT from buyer; rates hedge
Cover: number, yes_no, definition, procedure

**VAT_ZERO_RATED_CORRECTION — 15 pairs (2 checkpoints)**
Target failure: eval_017
Keywords in output: `zero-rated`, `exempt`, `pembejeo`, `kudai`, `hairuhusiwi`
Topics: zero-rated = 0% VAT, CAN claim pembejeo; exempt = no VAT, CANNOT claim pembejeo; write 5+ pairs with "inaweza kudai" for zero-rated; write 5+ pairs with "haiwezi kudai" for exempt
Cover: yes_no, definition

**GN487A_CORRECTION — 25 pairs (3 checkpoints)**
Target failures: eval_158, eval_162, eval_167, eval_175
Keywords in output: `msaidizi`, `mgeni`, `adhabu`, `wote wawili`, `ndoa`, `uraia`
Topics: msaidizi = Mtanzania anayekopa jina/leseni/utambulisho kumruhusu mgeni — kosa la kisheria; mgeni = asiye raia wa Tanzania per Cap.357 — dual citizens with TZ passport NOT excluded; adhabu: WOTE WAWILI — mgeni TZS 10M+/miezi 6/visa; msaidizi TZS 5M/miezi 3; ndoa haitoi uraia moja kwa moja — GN487A bado inatumika
Cover: yes_no, definition, penalty, procedure

**SDL_CORRECTION — 20 pairs (2 checkpoints)**
Target failures: eval_125, eval_113, eval_127, eval_134
Keywords in output: `GN605A`, `Sheria ya Mafunzo ya Ufundi`, `VET`, `Cap.82`, `ilifutwa`, `tofauti`
Topics: GN605A ndio sahihi — GN605B haipo; SDL chini ya VET Act Cap.82 s.14 — SI VAT Act wala Income Tax Act; PAYE na SDL zote tarehe 7 — tofauti lakini tarehe moja; SDL penalty: hedge thibitisha na TRA
Cover: number, yes_no, definition, procedure, penalty

**OUT_OF_CORPUS_CORRECTION — 15 pairs (2 checkpoints)**
Target failures: eval_195, eval_197
Keywords in output: `nje ya maarifa yangu`, `maarifa`, `mshauri`
Topics: Zanzibar tax — Chike Tanzania Bara tu, wasiliana na ZRA; stamp duty ardhi — nje ya maarifa yangu, wasiliana na mshauri wa kisheria; every output MUST contain approved refusal phrase
Cover: out_of_corpus_refusal only

**OSHA_CORRECTION — 15 pairs (2 checkpoints)**
Target failures: eval_177, eval_186
Keywords in output: `ukaguzi`, `kila mwaka`, `leseni`, `kumwajiri`, `adhabu`, `osha.go.tz`
Topics: OSHA ukaguzi wa kila mwaka — mandatory for all workplaces; leseni inafanywa upya kila mwaka; safety officer: HEDGE — thibitisha na OSHA; adhabu: TZS 1M-5M AU miezi 12 AU vyote viwili
Cover: yes_no, procedure, penalty

**BRELA_CORRECTION — 15 pairs (2 checkpoints)**
Target failures: eval_083, eval_072
Keywords in output: `BRELA`, `COSOTA`, `alama`, `hakimiliki`, `anniversary`, `tarehe ya usajili`
Topics: BRELA = alama za biashara, hataza, miundo; COSOTA = hakimiliki; ORT haipo; annual return = siku ya kumbukumbu ya usajili kila mwaka — NOT tarehe 42 baada ya usajili
Cover: yes_no, definition, procedure

**EFD_CORRECTION — 10 pairs (1 checkpoint)**
Target failure: eval_060
Keywords in output: `kufunga`, `mamlaka`, `kusimamisha`
Topics: TRA ina mamlaka ya KUFUNGA biashara — jibu Ndiyo; never write kufungua; TRA inaweza: kutoza faini, kusimamisha leseni, KUFUNGA biashara
Cover: yes_no

## STEP 4 — AGENT 4: PAIR REVIEWER

```python
import json, glob
from anthropic import Anthropic

client = Anthropic()

with open('datasets/tier1a/locked_facts.json') as f:
    locked_facts = json.load(f)

fail_tracker = {}
escalate_to_agent2 = []

def review_subdomain_checkpoint(pairs, subdomain, locked_facts, checkpoint_num):
    facts_text = json.dumps(locked_facts, ensure_ascii=False, indent=2)
    pairs_text = json.dumps(pairs, ensure_ascii=False, indent=2)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        messages=[{"role": "user", "content": f"""You are a strict fact reviewer for a Tanzanian business compliance AI.

Review checkpoint {checkpoint_num} for subdomain '{subdomain}' — {len(pairs)} pairs.

LOCKED FACTS:
{facts_text}

FAIL if any of these:
1. VAT withholding: supplier remits to TRA instead of qualifying buyer — FAIL
2. VAT withholding certificate due on 20th — FAIL (correct: day VAT becomes payable)
3. Zero-rated suppliers cannot claim input VAT — FAIL (they CAN)
4. GN487A: only foreigner penalised — FAIL (BOTH penalised)
5. SDL citing VAT Act or Income Tax Act as source — FAIL (correct: VET Act Cap.82)
6. GN605B mentioned — FAIL (does not exist)
7. Trademark to COSOTA or copyright to BRELA — FAIL
8. ORT mentioned as IP body — FAIL (does not exist)
9. kufungua instead of kufunga in TRA closure context — FAIL
10. OSHA safety officer specific employee number without hedge — FAIL
11. Out-of-corpus pair missing refusal phrase — FAIL
12. Unverified TZS penalty amount stated as fact — FAIL

For each FAIL:
FAIL [pair_index] | TYPE: FACT_ERROR or LANGUAGE_ERROR | REASON: exact issue | LOCKED_FACT_SAYS: what locked_facts says

End with:
PASS_COUNT: X
FAIL_COUNT: Y
FACT_ERRORS: [list of pair indices]

Pairs:
{pairs_text}"""}]
    )
    return response.content[0].text

subdomains = [
    'vat_withholding_correction', 'vat_zero_rated_correction',
    'gn487a_correction', 'sdl_correction', 'out_of_corpus_correction',
    'osha_correction', 'brela_correction', 'efd_correction'
]

all_review_results = {}

for subdomain in subdomains:
    ck_files = sorted(glob.glob(
        f'datasets/tier1a/raw_sources/batch_013_checkpoints/ck_{subdomain}_*.jsonl'
    ))
    if not ck_files:
        print(f"[Agent 4] No files for {subdomain}")
        continue
    subdomain_results = []
    for ck_file in ck_files:
        ck_num = ck_file.split('_')[-1].replace('.jsonl','')
        with open(ck_file) as f:
            pairs = [json.loads(l) for l in f if l.strip()]
        print(f"[Agent 4] Reviewing {subdomain} checkpoint {ck_num} — {len(pairs)} pairs ...")
        result = review_subdomain_checkpoint(pairs, subdomain, locked_facts, ck_num)
        subdomain_results.append({'checkpoint': ck_num, 'result': result})
        print(result)
        for i, pair in enumerate(pairs):
            pair_key = f"{subdomain}_{ck_num}_{i}"
            if f"FAIL {i}" in result and "FACT_ERROR" in result:
                fail_tracker[pair_key] = fail_tracker.get(pair_key, 0) + 1
                if fail_tracker[pair_key] >= 2:
                    escalate_to_agent2.append({
                        'subdomain': subdomain, 'pair_index': i,
                        'checkpoint': ck_num, 'pair': pair
                    })
    all_review_results[subdomain] = subdomain_results

with open('datasets/tier1a/raw_sources/batch_013_checkpoints/review_results.json', 'w') as f:
    json.dump(all_review_results, f, ensure_ascii=False, indent=2)

print(f"\n[Agent 4] Complete. Escalations: {len(escalate_to_agent2)}")
```

## STEP 5 — REWRITE FAILED PAIRS

For each FAIL:
- LANGUAGE_ERROR: rewrite for natural Swahili
- FACT_ERROR first failure: correct using locked_facts.json
- FACT_ERROR second failure same pair: escalate to Agent 2 (max 5 new facts total Steps 1+5 combined)

## STEP 6 — KEYWORD COVERAGE CHECK

```python
import json, glob

all_pairs = []
for fp in sorted(glob.glob(
    'datasets/tier1a/raw_sources/batch_013_checkpoints/ck_*.jsonl'
)):
    with open(fp) as f:
        for line in f:
            if line.strip():
                all_pairs.append(json.loads(line))

subdomain_keywords = {
    'vat_withholding_correction':  ['anayehitimu','anakata','certificate','moja kwa moja'],
    'vat_zero_rated_correction':   ['zero-rated','exempt','pembejeo','kudai'],
    'gn487a_correction':           ['msaidizi','mgeni','adhabu','wote wawili','ndoa'],
    'sdl_correction':              ['GN605A','Cap.82','ilifutwa','tofauti'],
    'out_of_corpus_correction':    ['maarifa','mshauri'],
    'osha_correction':             ['ukaguzi','kila mwaka','leseni','osha.go.tz'],
    'brela_correction':            ['BRELA','COSOTA','alama','hakimiliki'],
    'efd_correction':              ['kufunga','mamlaka','kusimamisha'],
}

print(f"Total pairs: {len(all_pairs)}")
all_ok = True
for subdomain, keywords in subdomain_keywords.items():
    print(f"\n{subdomain}:")
    for kw in keywords:
        count = sum(1 for p in all_pairs if kw in p.get('output',''))
        status = '✓' if count >= 3 else '⚠ LOW'
        if count < 3:
            all_ok = False
        print(f"  {kw}: {count} {status}")

refusal_phrases = [
    'nje ya maarifa yangu','swali hili liko nje',
    'sina uhakika','mshauri wa kodi','wasiliana na mshauri'
]
oc = [p for p in all_pairs if any(ph in p.get('output','') for ph in refusal_phrases)]
print(f"\nRefusal pairs: {len(oc)} (target: 15)")
if len(oc) < 12:
    all_ok = False
print(f"\n{'✓ All checks passed' if all_ok else '⚠ Fix low keywords before proceeding'}")
```

## STEP 7 — FORMAT VERIFICATION AND SAMPLE DISPLAY

```python
import json, glob

all_pairs = []
for fp in sorted(glob.glob(
    'datasets/tier1a/raw_sources/batch_013_checkpoints/ck_*.jsonl'
)):
    with open(fp) as f:
        for line in f:
            if line.strip():
                all_pairs.append(json.loads(line))

assert all(
    'instruction' in p and 'output' in p and 'system' in p and 'input' in p
    for p in all_pairs
), 'WRONG FORMAT'
print(f"Format OK — {len(all_pairs)} total pairs")
assert len(all_pairs) >= 130, f"Too few pairs: {len(all_pairs)}"

subdomain_keywords = {
    'vat_withholding_correction':  ['anayehitimu','moja kwa moja'],
    'vat_zero_rated_correction':   ['zero-rated','pembejeo'],
    'gn487a_correction':           ['msaidizi','wote wawili'],
    'sdl_correction':              ['GN605A','Cap.82'],
    'out_of_corpus_correction':    ['maarifa'],
    'osha_correction':             ['kila mwaka'],
    'brela_correction':            ['COSOTA'],
    'efd_correction':              ['kufunga'],
}

print("\n========== SAMPLES FOR HUMAN REVIEW ==========")
for sd, kws in sorted(subdomain_keywords.items()):
    matches = [p for p in all_pairs if any(kw in p.get('output','') for kw in kws)]
    print(f"\n--- {sd} ({len(matches)} pairs) ---")
    for p in matches[:2]:
        print(f"Q: {p['instruction']}")
        print(f"A: {p['output'][:300]}")
        print()
```

## STEP 8 — STOP AND REPORT

Report:
1. locked_facts.json final count and 5 new facts from Agent 2
2. Total pairs per subdomain
3. Agent 4 review summary — pass/fail per subdomain
4. Any Agent 2 escalations during review
5. Keyword coverage table
6. Sample pairs (2 per subdomain)

STOP. Do not merge files. Do not copy to cleaned_pairs. Do not rebuild dataset. Do not commit batch_013 pairs.

Wait for human approval before any further action.
After writing the file confirm it was saved correctly by showing the first 20 lines. Then commit:
bashgit add .claude/commands/do.md
git commit -m 'do.md: updated to batch_013 pipeline instruction'
git push origin main
Report commit hash