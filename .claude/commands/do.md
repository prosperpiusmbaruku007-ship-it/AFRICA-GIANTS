#Read this file completely then execute every instruction below exactly as written.
Generate batch_009 — 300 training pairs in 6 chunks
of 50 pairs each. Generate ALL chunks in one session.
Save and review after each chunk before continuing
to the next. Do not stop between chunks.

The pairs must address the real eval failures:
- gn487a: 60% — biggest gap
- brela_registration: 60%
- out_of_corpus refusal: 0% — most urgent
- efd_compliance: 70%
- sdl_compliance: 68%
- vat_withholding: 70%
- vat_registration: 73%
- nssf_contributions: 80%
- osha_registration: 80%

OUTPUT FILE:
datasets/tier1a/raw_sources/raw_pairs_batch_009.jsonl

CHECKPOINT DIR:
datasets/tier1a/raw_sources/batch_009_checkpoints/

PAIR FORMAT — every pair must use this exact structure:
{
  "instruction": "question in Swahili",
  "input": "",
  "output": "answer in Swahili — complete, accurate, verified"
}

============================================================
SETUP — run once before any generation
============================================================

import json
import os
import anthropic
import concurrent.futures

client = anthropic.Anthropic()

OUTPUT_FILE    = "datasets/tier1a/raw_sources/raw_pairs_batch_009.jsonl"
CHECKPOINT_DIR = "datasets/tier1a/raw_sources/batch_009_checkpoints"
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

# Clear output file if exists from previous attempt
if os.path.exists(OUTPUT_FILE):
    os.remove(OUTPUT_FILE)
    print(f"[setup] Cleared existing {OUTPUT_FILE}")

total_saved = 0

def save_chunk(pairs, chunk_num):
    global total_saved
    checkpoint_path = f"{CHECKPOINT_DIR}/checkpoint_{chunk_num:03d}.jsonl"
    with open(checkpoint_path, "w", encoding="utf-8") as f:
        for p in pairs:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for p in pairs:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    total_saved += len(pairs)
    print(f"[chunk {chunk_num}/6] Saved {len(pairs)} pairs — total: {total_saved}")

def cross_ai_review(pairs, chunk_num):
    pairs_json = json.dumps(pairs[:10], ensure_ascii=False, indent=2)

    PROMPT_FACTS = """Tanzania tax and business law expert.
Review these training pairs for Chike AI assistant.
Check: (1) fact accuracy against TRA/Finance Act 2025/GN 487A
(2) refusal pairs must NEVER answer — only refuse
(3) GN487A penalty must say OR not AND for fine/imprisonment
(4) no fabricated numbers
Return JSON: {"issues": [{"index": 0, "problem": "...", "fix": "..."}], "approved_count": N}"""

    PROMPT_LANG = """Swahili language and Tanzania compliance expert.
Review these training pairs for language quality.
Check: (1) natural correct Swahili (2) answer completeness
(3) question clarity and unambiguity
Return JSON: {"language_issues": [{"index": 0, "issue": "..."}], "quality": {"swahili": 0-10, "completeness": 0-10}}"""

    def review_facts():
        try:
            r = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1000,
                messages=[{"role": "user", "content": PROMPT_FACTS + "\n\nPAIRS:\n" + pairs_json}]
            )
            return json.loads(r.content[0].text)
        except Exception as e:
            return {"issues": [], "approved_count": len(pairs), "error": str(e)}

    def review_lang():
        try:
            r = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1000,
                messages=[{"role": "user", "content": PROMPT_LANG + "\n\nPAIRS:\n" + pairs_json}]
            )
            return json.loads(r.content[0].text)
        except Exception as e:
            return {"language_issues": [], "quality": {}, "error": str(e)}

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        fa = ex.submit(review_facts)
        fb = ex.submit(review_lang)
        ra = fa.result(timeout=60)
        rb = fb.result(timeout=60)

    fact_issues = len(ra.get("issues", []))
    lang_issues = len(rb.get("language_issues", []))
    quality     = rb.get("quality", {})

    review_path = f"{CHECKPOINT_DIR}/review_{chunk_num:03d}.json"
    with open(review_path, "w", encoding="utf-8") as f:
        json.dump({"chunk": chunk_num, "facts": ra, "language": rb}, f,
                  ensure_ascii=False, indent=2)

    print(f"[review {chunk_num}/6] fact_issues={fact_issues} lang_issues={lang_issues} quality={quality}")

============================================================
CHUNK 1 — GN487A penalty AND/OR + categories (50 pairs)
============================================================

Generate exactly 50 pairs then call:
save_chunk(pairs, 1)
cross_ai_review(pairs, 1)

Topics:
25 pairs — GN487A penalty AND/OR structure
Each output MUST contain these exact phrases:
"faini AU kifungo" (fine OR imprisonment)
"kufutwa kwa visa ni lazima daima" (visa always mandatory)
NEVER use "faini NA kifungo" in output

Example pair:
{
  "instruction": "Mgeni aliyekamatwa akifanya biashara ya rejareja Tanzania anaweza kupewa faini NA kifungo kwa wakati mmoja?",
  "input": "",
  "output": "Hapana. Adhabu kwa mgeni chini ya GN 487A ni: faini ya angalau TZS milioni 10 AU kifungo cha hadi miezi 6 — si zote mbili pamoja. Hata hivyo, kufutwa kwa visa/kibali cha kuingia Tanzania ni lazima daima, bila kujali kama faini au kifungo kimetolewa. Muundo sahihi ni: (faini AU kifungo) NA kufutwa kwa visa. Thibitisha na Idara ya Uhamiaji."
}

25 pairs — GN487A 15 prohibited categories
Cover all 15 categories by name. Mix yes/no questions,
definition questions, and scenario questions.
Categories:
1.Biashara ya rejareja 2.Biashara ya jumla
3.Saluni na urembo 4.Ukarabati wa simu
5.Uhamishaji wa pesa 6.Huduma za usafi
7.Ushonaji na utengenezaji wa nguo
8.Upigaji picha na video 9.Usafirishaji mdogo
10.Huduma za ujumbe na delivery
11.Uchapishaji na unanakili 12.Udhibiti wa wadudu
13.Biashara ya nguo za pili 14.Biashara ndogo/machinga
15.Boda boda na bajaj

============================================================
CHUNK 2 — Out of corpus refusal (50 pairs)
============================================================

Generate exactly 50 pairs then call:
save_chunk(pairs, 2)
cross_ai_review(pairs, 2)

CRITICAL: Every output MUST start with:
"Swali hili liko nje ya maarifa yangu ya sasa."
And MUST NOT attempt to answer the question.
And MUST end with direction to TRA or qualified adviser.

Topics (vary question phrasing widely):
8 pairs — import duty rates on different goods
6 pairs — capital gains tax on land/property/shares
6 pairs — crypto/Bitcoin/digital assets taxation
5 pairs — transfer pricing between related companies
5 pairs — Zanzibar tax differences from mainland
5 pairs — gold/mineral/oil royalty rates
5 pairs — insurance premium levy rates
5 pairs — EPZ/SEZ tax exemptions and conditions
5 pairs — stamp duty land valuation methods
5 pairs — mix of other genuinely out-of-corpus topics

Each pair must use different question phrasing.
Do not repeat the same scenario twice.

Example pair:
{
  "instruction": "Kiwango cha ushuru wa kuingiza simu za mkononi kutoka China ni asilimia ngapi Tanzania?",
  "input": "",
  "output": "Swali hili liko nje ya maarifa yangu ya sasa. Mimi ni Chike, mshauri wa biashara kutoka Africa Giants, na ninashughulikia mada za VAT, PAYE, SDL, NSSF, WCF, BRELA, TRA, OSHA, GN 487A, EFD, na biashara za Tanzania Bara. Ushuru wa forodha ni mada tofauti inayohitaji utaalamu maalum. Tafadhali wasiliana na TRA kupitia tra.go.tz au mshauri wa forodha aliyehitimu kwa jibu sahihi."
}

============================================================
CHUNK 3 — BRELA registration gaps (40 pairs)
         + GN487A spouse/exception (10 pairs)
============================================================

Generate exactly 50 pairs then call:
save_chunk(pairs, 3)
cross_ai_review(pairs, 3)

40 pairs BRELA:
15 pairs — annual return consequences
  Focus: fines + deregistration + commercial restrictions
  The model scores 60% here — it knows basics but
  misses consequences of non-compliance

15 pairs — sole trader vs limited company liability
  Personal liability vs separate legal entity
  When to choose each structure
  Cost and reporting differences

10 pairs — BRELA vs COSOTA vs TRA distinction
  BRELA: business + trademarks + patents + designs
  COSOTA: copyrights ONLY
  TRA: tax registration (TIN) — completely separate
  Need BOTH BRELA certificate AND TIN to operate

10 pairs GN487A:
5 pairs — Tanzanian spouse does not exempt non-citizen
  "Ndoa na raia wa Tanzania haibadilishi hadhi ya
   uraia chini ya GN 487A"
5 pairs — No small business exception exists
  "Hakuna msamaha kwa biashara ndogo katika GN 487A"
  The TZS 10M minimum applies equally to all

============================================================
CHUNK 4 — EFD compliance gaps (35 pairs)
         + SDL compliance gaps (15 pairs)
============================================================

Generate exactly 50 pairs then call:
save_chunk(pairs, 4)
cross_ai_review(pairs, 4)

35 pairs EFD:
15 pairs — every transaction without exception
  Scenarios: TZS 100 sale, mobile money, card payment,
  customer refuses receipt, market stall, online sale
  Key message: no minimum amount, no payment method exception

10 pairs — TRA enforcement and detection methods
  Surprise inspections, customer complaints,
  EFD data cross-referenced with M-Pesa/bank records,
  One complaint = full audit risk

10 pairs — consequences of non-compliance
  Business closure, director personal liability,
  Tax evasion charges, licence suspension

15 pairs SDL:
8 pairs — 10-employee threshold mechanics
  Below 10: no SDL, exactly 10: starts immediately,
  Mid-month hire: starts that month, contractor vs employee

7 pairs — SDL vs WCF distinction
  SDL: 3.5% to TRA for skills training
  WCF: 0.5% to WCF Authority for injury compensation
  Both employer-only, neither from employee salary
  Different institutions, different purposes, different rates

============================================================
CHUNK 5 — VAT withholding (25 pairs)
         + VAT registration (15 pairs)
         + SDL GN605A interaction (10 pairs)
============================================================

Generate exactly 50 pairs then call:
save_chunk(pairs, 5)
cross_ai_review(pairs, 5)

25 pairs VAT withholding:
12 pairs — 3% goods vs 6% services
  Common confusions to address:
  IT services = 6% (not 3%)
  Construction materials = 3%
  Consultancy = 6%
  Mixed supplies: split and apply correct rate

8 pairs — 3 qualifying buyer types
  Ministry of Finance: automatic
  Government entity retaining own revenue: automatic
  CG-designated person: requires formal designation
  Private company: CANNOT be qualifying buyer without CG

5 pairs — certificate timing
  Day VAT becomes payable — NOT the 20th
  20th is VAT return deadline — different obligation
  Two separate deadlines, two separate legal duties

15 pairs VAT registration:
8 pairs — threshold mechanics with calculations
  Rolling 12-month TZS 200M
  Rolling 6-month TZS 100M
  Either triggers mandatory immediate registration
  Include calculation scenarios

7 pairs — professional mandatory registration
  Lawyers, CPAs, engineers, architects
  Low revenue does NOT exempt listed professions
  Specific TRA requirement for these categories

10 pairs SDL + GN605A:
SDL base is gross payroll
If GN605A raises minimum wages SDL base increases
GN605A effective 1 January 2026, covers 16 sectors
SDL calculation must use updated wage floor

============================================================
CHUNK 6 — NSSF gaps (10 pairs)
         + OSHA gaps (10 pairs)
         + GN487A enforcement dates (15 pairs)
         + Mixed reinforcement (15 pairs)
============================================================

Generate exactly 50 pairs then call:
save_chunk(pairs, 6)
cross_ai_review(pairs, 6)

10 pairs NSSF:
5 pairs — late payment: 5% monthly interest,
  director personal liability, contact NSSF early
5 pairs — domestic workers covered,
  self-employed voluntary 20% total

10 pairs OSHA:
5 pairs — every employer regardless of count,
  OSHA separate from BRELA
5 pairs — safety officer 50+ general, 20+ construction,
  director personal liability for non-compliance

15 pairs GN487A enforcement:
5 pairs — gazetted 28 July 2025, effective same day
5 pairs — enforcement exercise 11 Sep to 8 Oct 2025
5 pairs — led by Immigration Services Department,
  exercise ended but law permanent ongoing enforcement

15 pairs mixed reinforcement — hardest questions:
Pick the 15 topics with lowest accuracy across
all subdomains and create one reinforcement pair
for each. These are deliberately the hardest
scenarios combining multiple compliance areas.
Example: "Mgeni mwenye duka la rejareja ambaye
pia amesajili NSSF — je, NSSF inasaidia kuomba
msamaha wa GN 487A?" (No — completely separate systems)

============================================================
AFTER ALL 6 CHUNKS COMPLETE
============================================================

Run final verification:
python -c "
import json, glob

# Count total
with open('datasets/tier1a/raw_sources/raw_pairs_batch_009.jsonl') as f:
    lines = [l for l in f if l.strip()]
print(f'Total pairs: {len(lines)}')
assert len(lines) == 300, f'Expected 300 got {len(lines)}'

# Verify no empty outputs
empty = 0
refusal_correct = 0
and_or_errors = 0
for l in lines:
    d = json.loads(l)
    out = d.get('output', '')
    if not out.strip():
        empty += 1
    if 'liko nje ya maarifa' in out and 'asilimia' in out:
        refusal_correct += 0  # refusal should not have numbers
    if 'faini NA kifungo' in out.lower():
        and_or_errors += 1

print(f'Empty outputs: {empty} (should be 0)')
print(f'AND/OR errors in GN487A: {and_or_errors} (should be 0)')
print('All checks passed' if empty == 0 and and_or_errors == 0 else 'ISSUES FOUND')
"

Run check_locked_facts.py:
python check_locked_facts.py \
  datasets/tier1a/raw_sources/raw_pairs_batch_009.jsonl

Run DEDUP check:
python -c "
import json, glob

existing_keys = set()
for f in glob.glob('datasets/tier1a/cleaned_pairs/*.jsonl'):
    with open(f, encoding='utf-8') as fh:
        for line in fh:
            if line.strip():
                d = json.loads(line)
                key = (d.get('instruction','') + d.get('output',''))[:120]
                existing_keys.add(key)

dupes = 0
with open('datasets/tier1a/raw_sources/raw_pairs_batch_009.jsonl',
          encoding='utf-8') as f:
    for i, line in enumerate(f):
        if line.strip():
            d = json.loads(line)
            key = (d.get('instruction','') + d.get('output',''))[:120]
            if key in existing_keys:
                dupes += 1
                print(f'DUPE at line {i}: {key[:80]}')

print(f'Duplicates found: {dupes} (should be 0)')
"

Then commit everything:
git add datasets/tier1a/raw_sources/raw_pairs_batch_009.jsonl
git add datasets/tier1a/raw_sources/batch_009_checkpoints/
git commit -m "batch_009: 300 pairs — 6 chunks, cross-AI reviewed, gn487a AND/OR fix, 50 refusal pairs"
git push origin main
Show commit hash and final summary then STOP.

============================================================
ALSO IN THE SAME SESSION — update welcome message
============================================================

After batch_009 is committed update
wappfly-function/handler.py WELCOME message:

WELCOME = (
    "🌍 *Chike* — mshauri wako wa biashara Tanzania.\n"
    "_Fahamu Biashara Yako, Maarifa Yako._\n\n"
    "Ninajibu maswali yote ya biashara kwa sekunde chache:\n\n"
    "💰 *Kodi* — VAT · PAYE · SDL · WHT · EFD\n"
    "📋 *Usajili* — BRELA · TRA · NSSF · OSHA · WCF\n"
    "⚖️ *Sheria* — GN 487A · Vibali · Leseni\n"
    "📊 *Mishahara* — GN 605A · SDL · WCF\n\n"
    "Uliza swali lolote sasa hivi. 👇\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "🌍 *Chike* — your Tanzanian business adviser.\n"
    "_Understand Your Business, That Knowledge Is Yours._\n\n"
    "I answer all business questions in seconds:\n\n"
    "💰 *Tax* — VAT · PAYE · SDL · WHT · EFD\n"
    "📋 *Registration* — BRELA · TRA · NSSF · OSHA · WCF\n"
    "⚖️ *Law* — GN 487A · Permits · Licences\n"
    "📊 *Wages* — GN 605A · SDL · WCF\n\n"
    "Ask me anything right now. 👇\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "⚠️ _Chike iko katika awamu ya majaribio (beta)._\n"
    "_Thibitisha majibu muhimu na TRA au mshauri wa kodi._\n\n"
    "⚠️ _Chike is in beta. Always verify important_\n"
    "_answers with TRA or a qualified adviser._"
)

git add wappfly-function/handler.py
git commit -m "update welcome message — hooking structure, beta disclaimer"
git push origin main
Show both commit hashes then STOP.