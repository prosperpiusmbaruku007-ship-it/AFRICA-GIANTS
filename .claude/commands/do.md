#Read this file completely then execute every instruction below exactly as written.
Confirmed. Start sdl_compliance adversarial pairs.
Target: 50 pairs.

Every SDL pair MUST follow these rules:

RULE 1: Full name always stated
Every pair must include the full name in both languages:
"Skills Development Levy (SDL)" in English
"Kodi ya Kukuza Ujuzi (SDL)" in Swahili

RULE 2: Directly contradict the base model error
At least 20 of the 50 pairs must be adversarial pairs
that explicitly say SDL is NOT disability leave and
NOT Service Delivery Levy.

Example adversarial question:
Q: "SDL inamaanisha 'Service Delivery Levy' — je, hii ni kweli?"
A: "Hapana. SDL inamaanisha Skills Development Levy —
   Kodi ya Kukuza Ujuzi. Si 'Service Delivery Levy'
   wala 'short-term disability leave'..."

RULE 3: Always state these four facts together
- Rate: 3.5% of gross payroll
- Threshold: 10 or more employees Mainland Tanzania
- Paid by: employer only, NOT deducted from employee
- Deadline: 7th of following month with PAYE

RULE 4: Cover these angles across 50 pairs
- 20 adversarial pairs: SDL name correction
- 10 pairs: SDL calculation examples with TZS amounts
- 10 pairs: SDL threshold edge cases (9 employees vs 10)
- 5 pairs: SDL exemptions (EPZ, NGO)
- 5 pairs: SDL deadline and penalty

RULE 5: Register distribution
- business_market: at least 40%
- formal: 30-40%
- rural_conversational: 20%

Append to:
datasets/tier1a/raw_sources/raw_pairs_batch_003.jsonl

After all 50 pairs run:
python scripts/check_locked_facts.py \
  --file datasets/tier1a/raw_sources/raw_pairs_batch_003.jsonl
python scripts/check_sources.py \
  --file datasets/tier1a/raw_sources/raw_pairs_batch_003.jsonl

Report total pairs in file, checks result,
and register distribution then STOP and wait.