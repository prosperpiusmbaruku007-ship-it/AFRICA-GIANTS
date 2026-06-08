<identity>
You are the lead engineer and institutional memory of AFRICA-GIANTS — a
Tanzanian AI company being built from first principles. An extensive research
session produced verified strategic decisions, a locked dataset construction
specification, a domain sequence, and a reference narrative stored in
docs/reference_narrative.md. Your task is to write CLAUDE.md, PROGRESS.md,
sources/whitelist.json, and schema/pair_schema.json so that any future
Claude Code session opens this project with complete, accurate, actionable
context and immediately knows what to do next without asking.

These four files are the difference between a project that compounds and one
that repeats itself.
</identity>

---

## CRITICAL: READ BEFORE TOUCHING ANYTHING

**PRESERVATION RULE — NON-NEGOTIABLE:**
The following files and directories ALREADY EXIST and are WORKING.
Do NOT delete, move, rename, or modify any of them under any circumstances:

```
notebooks/                          ← Kaggle training notebooks
kaggle/                             ← Kaggle sync directory + africa_giants_V2.ipynb
scripts/fixed_cell_model.py         ← Working Unsloth/BitsAndBytes model loader
scripts/fixed_cell_data.py          ← Working dataset formatter with EOS fix
scripts/fixed_cell_train.py         ← Working SFTTrainer with all 5 EOS fixes
scripts/_trl_sft_trainer_v0_24_0.py ← TRL source reference
run.py                              ← Pipeline orchestrator
models/pipeline_state.json          ← Pipeline state (completed: data_pipeline, hf_upload)
.claude/commands/fix-eos.md         ← EOS token fix command
```

Your task is to ADD new directories and files ALONGSIDE the existing structure.
Do not touch the existing training pipeline. It works.

**ENVIRONMENT:**
- OS: Windows, PowerShell
- Project root: C:\Users\jhjh\AFRICA-GIANTS
- GitHub: https://github.com/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS
- Use encoding=utf-8 for ALL file operations
- After all files are created: git add -A, git commit, git push

---

<chain_of_thought>
Before writing a single line of any file, complete this reasoning sequence in order.

STEP 1 — WHAT IS EACH FILE FOR?

CLAUDE.md = behavioral contract. Every line must change how the agent acts.
Contains: what this project IS, what the agent must NEVER do, approved sources,
accuracy gate, domain sequence, repo architecture, Swahili register rules,
verified regulatory facts, citation laundering warning.
Does NOT contain: status, dates, pair counts, scrape progress.

PROGRESS.md = living record. Updated every session.
Contains: current phase, last completed, active work, next actions, blocked items,
locked decisions with sources, contested claims, dataset status table,
scrape targets with status, domain expansion triggers.
Does NOT contain: behavioral rules, architecture specs, source whitelists.

sources/whitelist.json = machine-readable enforcement.
Contains: every approved scrape URL with institution, source_type, use_for
(training vs eval), decay_risk, last_verified, re_scrape_trigger.
Pipeline rejects any URL not in this file.

schema/pair_schema.json = canonical metadata contract.
Contains: every required field for a Q&A training pair.
All fields required — no optional fields. Pipeline rejects incomplete pairs.

STEP 2 — VERIFIED DECISIONS TO ENCODE (all verified from primary sources)

LOCKED (encode as fact with source):
- VAT threshold: TZS 200M/12mo or TZS 100M/6mo (TRA.go.tz, Finance Act 2025)
- VAT standard rate: 18% (TRA.go.tz)
- Finance Act 2025 VAT withholding: 3% goods / 6% services, effective 1 Jul 2025
  (EY Tanzania Finance Act 2025; KPMG Tax News Flash Oct 2025)
- VAT withholding certificate: issued by day VAT becomes payable, NOT the 20th
  (EY Finance Act 2025 — the 20th is the return filing deadline, different obligation)
- B2C e-payment VAT: 16% from 1 Sep 2025, implementation rules still pending CG notice
  (VATCalc; Global VAT Compliance Jul 2025)
- Public sector minimum wage: TZS 500,000/month from Jul 2025
  (President Samia announcement 1 May 2025)
- Private sector minimum wage: GN 605A, gazetted 13 Oct 2025, effective 1 Jan 2026
  Average increase 33.4%: TZS 275,060 → TZS 358,322/month, 16 sectors 46 sub-sectors
  Range: ~TZS 175,000 general to TZS 765,900 international mining/energy
  (PKF Eastern Africa; VELMA Law; The Citizen 17 Oct 2025; Bloomberg Tax 22 Oct 2025;
   Clyde & Co Feb 2026; TanzLII GN 605A full text)
- GN 487A: Business Licensing (Prohibition of Business Activities for Non-Citizens) Order
  Effective 28 Jul 2025. 15 prohibited activities including wholesale/retail trade,
  mobile money transfers, phone repair, salon business.
  Penalties: min TZS 10M + up to 6 months imprisonment for non-citizens;
  TZS 5M + 3 months imprisonment for Tanzanians facilitating violations.
  Enforcement: Immigration Services Dept exercise 11 Sep–8 Oct 2025.
  (Bowmans 30 Jul 2025; Dentons 29 Jul 2025; DLA Piper Africa; VELMA Law)
- NeST: mandatory from 1 Jul 2023 for 1,147 procuring entities.
  77,595 planned tenders worth TZS 30.12T as of Apr 2024.
  TANePS DECOMMISSIONED 31 Dec 2023. Never reference TANePS again.
  (PPRA.go.tz; NeST Guidelines 2025; MAPS assessment)
- EAC STR: USD 2,000 threshold, ~370 eligible products on Common List, 4 instruments
  CRITICAL DISTINCTION: originating status ≠ Common List eligibility.
  A product may qualify under rules of origin but not appear on the Common List
  at the specific border post — must be stated as explicit disambiguation pair.
  (COMESA Secretariat; ICTSD; ILO women cross-border traders guide)
- VICOBA: ~50,000 groups, TZS 1.5T combined assets, 4.4M clients (2024 report)
  BoT building national digital VICOBA framework. TCB launched KIKOBA product.
- Tanzania mobile money: 76.5M active accounts Dec 2025; TZS 198,859B value 2024;
  77% of transactions via USSD (TCRA; Bank of Tanzania; IMARC)
- Tanzania smartphone penetration: 36.75% (TCRA, Jun 2025)
- NMB Bank: ~USD 180M DFI package (IFC/BII/Norfund), ~USD 550M cumulative since 2022,
  SME and women-owned business mandate (TechAfrica News 2025)

CONTESTED (put in PROGRESS.md under "Decisions still contested", NOT in CLAUDE.md):
- Foreign-business ban enforcement specifics beyond what Bowmans/VELMA confirm
- Tourism earnings exact figure: grounding context says [VERIFY FROM BoT ANNUAL REPORT]
  Do not cite a specific tourism earnings number until verified from BoT
- Any claim sourced to: Spheron, Red Hat, Contabo, Siliconflow, Scrapfly,
  ScrapelessScrapfly, MLQ, Proxidize, GuruSup, Ryz Labs Learn, Medium (regulatory),
  arxiv (regulatory), BentoML, Preprints.org, Princeton (regulatory)
  These are the citation laundering sources documented across 8 research iterations.
  Underlying facts were sometimes real; citations were fabricated. Flag all as [VERIFY].

STEP 3 — REPO ARCHITECTURE TO ADD (alongside existing files)

Add these directories without touching existing structure:
datasets/tier1a/raw_sources/
datasets/tier1a/cleaned_pairs/
datasets/tier1a/eval_set/
datasets/tier1a/adversarial/
datasets/tier1a/rejected/
datasets/tier1b/raw_sources/
datasets/tier1b/cleaned_pairs/
datasets/tier1b/eval_set/
datasets/tier1b/adversarial/
datasets/tier1b/rejected/
datasets/tier1c/raw_sources/
datasets/tier1c/cleaned_pairs/
datasets/tier1c/eval_set/
datasets/tier1c/adversarial/
datasets/tier1c/rejected/
datasets/tier2a/raw_sources/
datasets/tier2a/cleaned_pairs/
datasets/tier2a/eval_set/
datasets/tier2b/raw_sources/
datasets/tier2b/cleaned_pairs/
datasets/tier2b/eval_set/
datasets/tier3/                     ← Reserved. No files yet. Generated by operation.
eval/accuracy_gate/
eval/refusal_gate/
eval/results/
schema/
sources/
docs/domain_research/
docs/decisions/
models/checkpoints/                 ← Model checkpoints named by gate score + date

PIPELINE ENFORCEMENT (enforce in CLAUDE.md):
raw_sources → cleaned_pairs: ALL metadata fields populated + source on whitelist
cleaned_pairs → eval_set: human expert sign-off on 10% sample required
cleaned_pairs → training: eval_set pairs EXCLUDED from training data
eval gate: >85% accuracy AND >70% refusal BOTH must pass — neither alone suffices
tier3/ is RESERVED — no pairs written until behavioral data generated by operation

STEP 4 — NEXT THREE PHYSICAL ACTIONS FOR FIRST SESSION

Action 1: Create directory structure above using mkdir commands (PowerShell).
  Verify: `dir datasets` shows all tier folders.
  Depends on: nothing.

Action 2: Validate that scripts/validate_dataset.py exists.
  If not: create it. It must check every JSONL file in datasets/*/cleaned_pairs/
  against schema/pair_schema.json (all fields present) and sources/whitelist.json
  (source_url domain whitelisted). Exit code 1 if any pair fails.
  Verify: `python scripts/validate_dataset.py` runs without error on empty directories.
  Depends on: Action 1 complete + schema/pair_schema.json created (Output 4).

Action 3: Validate that scripts/run_eval.py exists.
  If not: create it. It must load eval/accuracy_gate/ JSONL, run each question
  through the model, compare to verified answer, report accuracy %.
  Also load eval/refusal_gate/ JSONL, test out-of-corpus questions, report refusal %.
  Print "GATE PASSED" only if BOTH >85% accuracy AND >70% refusal are true.
  Verify: `python scripts/run_eval.py` runs (will report 0 pairs currently — that is correct).
  Depends on: Action 2 complete.

STEP 5 — SCRAPE TARGETS

All targets encoded in sources/whitelist.json (Output 3).

TIER 1A TRAINING SOURCES (use_for: "training"):
- https://www.tra.go.tz/index.php/tax-information (HTML, Annual, TRA VAT/PAYE/SDL/EFD)
- https://www.tra.go.tz/index.php/filing-returns (HTML, Annual, filing procedures)
- https://www.brela.go.tz (HTML, Stable, business registration + fees)
- https://www.nssf.or.tz (HTML, Annual, NSSF contributions + registration)
- https://www.osha.go.tz (HTML, Stable, OSHA workplace registration obligations)
- Tanzania Government Gazette (PDF, Event-triggered, GN 487A + GN 605A + Finance Act 2025)
- https://tanzlii.org (PDF official acts, Event-triggered, Labour law + minimum wage orders)

TIER 1A EVAL SOURCES (use_for: "eval" — DIFFERENT document family from training):
- ey.com/en_tz — Finance Act 2025 analysis (PDF, Annual)
- kpmg.com/tz — Tax News Flash Tanzania Oct 2025 (PDF, Annual)
- pkfea.com — GN 605A wage order alert (PDF, Event-triggered)
- velmalaw.co.tz — GN 487A analysis + wage order (HTML, Event-triggered)
- bowmans.com — GN 487A briefing (HTML, Event-triggered)
- clydeco.com — Finance Act commentary + wage order Feb 2026 (HTML, Annual)

TIER 1B TRAINING SOURCES:
- https://www.eac.int (HTML + PDF, Stable, STR instruments + Common List)
- https://www.comesa.int (PDF, Stable, originating status rules + STR policy)
- ilo.org — Step-by-Step Guide for Women Cross-Border Traders (PDF, Stable)
- unctad.org — Tanzania informal cross-border trade guide (PDF, Stable)
- eabc.info — STR manual for cereals/horticulture, Sep 2025 tender (PDF, Event-triggered)

TIER 1C TRAINING SOURCES:
- https://www.ppra.go.tz (HTML + PDF, Annual, NeST user guides + PPA 2023)
- ppra.go.tz — NeST Special Groups Procurement Guide 2025 (PDF, Stable)
- Official Tanzania parliament portal — Public Procurement Act 2023 full text (PDF, Stable)

STEP 6 — METADATA SCHEMA (all fields required, no optional fields)

{
  "id": "string — unique identifier, format: {domain}_{sequence}_{date}",
  "domain": "string — tier1a | tier1b | tier1c | tier2a | tier2b",
  "subdomain": "string — e.g. vat_compliance | labour_wages | gn487a | str_threshold",
  "question_sw": "string — question in Swahili, native register (not translated)",
  "answer_sw": "string — answer in Swahili, native register",
  "question_en": "string — question in English",
  "answer_en": "string — answer in English",
  "primary_source_url": "string — MUST be on sources/whitelist.json approved list",
  "primary_source_name": "string — e.g. Tanzania Revenue Authority, Finance Act 2025",
  "source_type": "string — government_portal | tier1_advisory | ilo_unctad_official | official_gazette",
  "effective_date": "string — ISO date, when this fact became legally effective",
  "decay_risk": "string — stable | annual | event_triggered",
  "next_review_trigger": "string — e.g. After Finance Act July 2026 | Monitor gazette",
  "verified_by": "string — name/role of domain expert who confirmed correctness",
  "verified_date": "string — ISO date of expert verification",
  "register": "string — formal | business_market | rural_conversational",
  "pair_type": "string — standard | disambiguation | adversarial | out_of_corpus_refusal",
  "eval_set": "boolean — true = held-out for eval, excluded from training"
}

STEP 7 — NON-NEGOTIABLE RULES FOR CLAUDE.md

Every rule below maps to a documented failure mode from the research session.
Include all of them. Violating any one caused a specific, documented harm.

R1: Never reference TANePS. The live system is NeST (mandatory from 1 Jul 2023, PPRA.go.tz).
    Citing TANePS destroys credibility in any government, investor, or partner meeting.

R2: Never encode a VAT rate, threshold, or withholding percentage without citing
    the Finance Act year it was effective. Finance Act 2025 changed multiple rates
    effective 1 Jul 2025 and 1 Sep 2025. Pre-Jul-2025 data is wrong for these fields.

R3: Never move a pair to cleaned_pairs/ without ALL 18 schema fields populated.
    Incomplete pairs corrupt the training set silently.

R4: Never use a source from the citation laundering list as authoritative.
    (Full list in CLAUDE.md section 2.) The pattern: plausible facts, fabricated citations.
    Even if the underlying fact is true, an invalid source disqualifies the pair.

R5: Never quote a minimum wage figure without citing GN 605A.
    The 2022 wage order was REVOKED effective 1 Jan 2026. Quoting the old rates
    gives wrong payroll advice to every Tanzanian employer.

R6: Never write training pairs and eval pairs from the same source document family.
    Training: TRA/BRELA/NSSF/OSHA primary portals + official gazettes.
    Eval: EY/KPMG/PKF/VELMA/Bowmans/Clyde&Co practitioner advisory alerts.
    Contamination inflates accuracy scores without improving real-world performance.

R7: Never ship any user-facing product before BOTH accuracy gates pass:
    >85% on in-corpus Swahili questions AND >70% correct refusal on
    out-of-corpus questions. Neither gate alone is sufficient.

R8: Never add a VICOBA calculation feature that positions the model as the ledger.
    The model assists and explains. It never owns or produces the authoritative record.
    A single arithmetic error destroys irreversible group trust.

R9: Never write pairs for tier3/ from authored content.
    Tier3 data is generated by operation — behavioral patterns from real usage.
    Authored tier3 pairs = fiction trained as fact.

R10: Never delete or modify: notebooks/, kaggle/, scripts/fixed_cell_*.py,
     run.py, models/pipeline_state.json, .claude/commands/fix-eos.md.
     The training pipeline works. Do not touch it.

R11: Never build the web app, mobile app, or any interface other than WhatsApp
     before 1,000 verified business users and one named institutional partner.
     77% of Tanzania mobile money runs via USSD. 36.75% have smartphones.
     WhatsApp reaches the connected majority first.

R12: The reference narrative is at docs/reference_narrative.md.
     Read it before making any strategic or architectural decision.
     It is the authoritative strategy document for this project.
</chain_of_thought>

---

## OUTPUT 1 — CLAUDE.md
*Produce this file at: C:\Users\jhjh\AFRICA-GIANTS\CLAUDE.md*
*Maximum 300 lines. Every line changes agent behavior.*
*Follow all rules in STEP 7 above. Use CONSTRAINT 3 (rules not instructions).*
*Use CONSTRAINT 4 (every number carries its source).*

Required sections in this exact order:
1. Project identity (5 lines max — what this IS, what it is NOT, reference narrative pointer)
2. What the agent must NEVER do (all rules from STEP 7, R1–R12)
3. Citation laundering warning (permanent institutional memory — list all invalid sources)
4. Primary source whitelist (domains only, point to sources/whitelist.json for full list)
5. Domain sequence and current active tier (one line per domain with status)
6. Dataset schema reference (schema/pair_schema.json — all 18 fields required)
7. Accuracy gate definition (>85% in-corpus AND >70% out-of-corpus refusal — BOTH)
8. Repo architecture map (folder names + one-line description of what belongs there)
9. Pipeline enforcement rules (the four transition gates from STEP 3)
10. Swahili register requirements (three registers, why each matters)
11. Verified regulatory facts (all facts from STEP 2 LOCKED list, with sources)
12. Failed competitors (Copia May 2024, MarketForce Apr 2024, Twiga, Wasoko-MaxAB)
13. Final line: "See PROGRESS.md for current project status and next actions."

---

## OUTPUT 2 — PROGRESS.md
*Produce this file at: C:\Users\jhjh\AFRICA-GIANTS\PROGRESS.md*
*This is the living record. It reflects current state as of today.*

Required sections in this exact order:

### 1. CURRENT PHASE
One line: Pre-Stage | Dataset Infrastructure Build | Creating schema, whitelist, directory structure

### 2. LAST VERIFIED COMPLETED (with dates where known)
Include the full training pipeline history:
- Kaggle training pipeline: debugged and working (May 2026)
- EOS token root cause found: AfriqueLlama tokenizer_config.json sets eos_token="<EOS_TOKEN>"
  All 5 fixes applied and confirmed working in cell-train
- Training run completed: loss 3.177→1.574 over 10 steps, val loss 1.371, PASSED threshold 2.5
- Adapter pushed to HuggingFace: prospaprospa007/africa-giants-adapter-v1
- Val gate: 1.371 < 2.5 threshold PASSED
- Merged model pushed to HF: MERGE_AND_PUSH=True run completed
- New kernel confirmed active: cell ID 648585292 (old 2510264585 retired)
- TANePS→NeST correction: locked across all documents
- Research complete: 8 research iterations, all domain decisions locked
- Reference narrative written: docs/reference_narrative.md
- Domain sequence locked: Tier1A→Tier1B→Tier1C→Tier2A→Tier2B→Tier3
- Dataset construction spec locked: schema, whitelist, pipeline gates

### 3. ACTIVE WORK
Current task: Building dataset infrastructure (directories, schema, whitelist, validation scripts)

### 4. NEXT PHYSICAL ACTIONS (dependency-ordered)
1. Create all dataset directory structure (PowerShell mkdir)
2. Validate scripts/validate_dataset.py exists — create if not
3. Validate scripts/run_eval.py exists — create if not
4. Copy docs/reference_narrative.md from outputs if not already in repo
5. Begin writing first 50 verified Tier 1A compliance pairs from TRA.go.tz
   ⚠️ HUMAN ACTION REQUIRED: A TRA-registered tax consultant must review
   a 10% sample of pairs before they move to cleaned_pairs/

### 5. BLOCKED ITEMS
- Tier 1A pair writing: blocked on tax consultant review workflow
  Unblocked by: engaging a TRA-registered consultant (human decision required)
- Accuracy gate: blocked on having enough pairs to test against
  Unblocked by: completing Tier 1A pair writing + eval set construction
- Product launch: blocked on accuracy gate passing
  Unblocked by: >85% in-corpus AND >70% refusal both confirmed

### 6. DECISIONS LOCKED (with source and date)
Include all major decisions from the research session with their sources.
Examples (include all):
- NeST not TANePS: PPRA.go.tz, NeST Guidelines 2025 — locked Jun 2026
- Finance Act 2025 VAT withholding 3%/6%: EY/KPMG — locked Jun 2026
- GN 605A wage order: PKF/VELMA/TanzLII — locked Jun 2026
- GN 487A non-citizen ban: Bowmans/Dentons/VELMA — locked Jun 2026
- Training+eval from different source families: locked Jun 2026
- WhatsApp-first delivery: locked (36.75% smartphone, 77% USSD) — Jun 2026
- No logistics/goods movement: B2B graveyard evidence — locked Jun 2026
- VICOBA: assist+explain only, never the ledger — locked Jun 2026
- Tier3 data generated by operation, not authored — locked Jun 2026

### 7. DECISIONS STILL CONTESTED (open questions requiring verification)
- Tanzania tourism earnings exact figure: must verify from BoT Annual Report
  Why it matters: cited in reference narrative as [VERIFY]
  Primary source needed: Bank of Tanzania Annual Report / TTB statistics
  Who verifies: agent via web search of BoT official portal
- Any claim originally sourced to citation laundering list: all require re-verification
  Against whitelist-approved sources before encoding in any training pair

### 8. DATASET STATUS TABLE
| Domain | Target pairs | Written | Verified | In eval set | Gate passed |
|--------|-------------|---------|----------|-------------|-------------|
| Tier 1A: TRA Compliance | 300 | 0 | 0 | 0 | No |
| Tier 1A: Labour/GN 605A | 200 | 0 | 0 | 0 | No |
| Tier 1A: GN 487A | 100 | 0 | 0 | 0 | No |
| Tier 1B: EAC STR | 300 | 0 | 0 | 0 | No |
| Tier 1C: NeST | 200 | 0 | 0 | 0 | No |
| Tier 2A: Legibility | 200 | 0 | 0 | 0 | No |
| Tier 2B: VICOBA | 300 | 0 | 0 | 0 | No |
| Tier 3 | Reserved | — | — | — | — |
| **TOTAL** | **1,600** | **0** | **0** | **0** | **No** |

Eval set target: 200 questions (from advisory sources — different family from training)
Accuracy gate: NOT STARTED
Refusal gate: NOT STARTED

### 9. SCRAPE TARGETS PIPELINE
For each URL, include: Source type | Content type | Decay risk | Status | Last verified

(Tier 1A Training)
- https://www.tra.go.tz/index.php/tax-information | gov portal | HTML | Annual | pending | 2026-06-01
- https://www.tra.go.tz/index.php/filing-returns | gov portal | HTML | Annual | pending | 2026-06-01
- https://www.brela.go.tz | gov portal | HTML | Stable | pending | 2026-06-01
- https://www.nssf.or.tz | gov portal | HTML | Annual | pending | 2026-06-01
- https://www.osha.go.tz | gov portal | HTML | Stable | pending | 2026-06-01
- Tanzania Government Gazette (GN 487A, GN 605A, Finance Act 2025) | official gazette | PDF | Event-triggered | pending | 2026-06-01
- https://tanzlii.org (GN 605A full text) | official law | PDF | Event-triggered | pending | 2026-06-01

(Tier 1A Eval — different document family)
- ey.com/en_tz Finance Act 2025 | tier1 advisory | PDF | Annual | pending | 2026-06-01
- kpmg.com/tz Tax News Flash Oct 2025 | tier1 advisory | PDF | Annual | pending | 2026-06-01
- pkfea.com GN 605A alert | tier1 advisory | PDF | Event-triggered | pending | 2026-06-01
- velmalaw.co.tz GN 487A analysis | tier1 advisory | HTML | Event-triggered | pending | 2026-06-01
- bowmans.com GN 487A briefing | tier1 advisory | HTML | Event-triggered | pending | 2026-06-01
- clydeco.com Finance Act / wage order | tier1 advisory | HTML | Annual | pending | 2026-06-01

(Tier 1B)
- https://www.eac.int STR instruments | official | HTML+PDF | Stable | pending | 2026-06-01
- https://www.comesa.int STR policy | official | PDF | Stable | pending | 2026-06-01
- ilo.org women cross-border traders guide | ILO official | PDF | Stable | pending | 2026-06-01
- unctad.org Tanzania cross-border guide | UNCTAD official | PDF | Stable | pending | 2026-06-01
- eabc.info STR cereals/horticulture manual | regional body | PDF | Event-triggered | pending | 2026-06-01

(Tier 1C)
- https://www.ppra.go.tz NeST user guides | gov portal | HTML+PDF | Annual | pending | 2026-06-01
- ppra.go.tz NeST Special Groups Guide 2025 | gov portal | PDF | Stable | pending | 2026-06-01
- Tanzania parliament portal PPA 2023 | official act | PDF | Stable | pending | 2026-06-01

### 10. DOMAIN EXPANSION TRIGGERS
(Do not build these until triggers fire — premature expansion = no foundation)

Domestic tourism operators:
- Trigger: >1,000 verified Tier 1A users AND tourism questions appear in compliance corpus
- Primary source when triggered: Tanzania Tourism Act, Hotel Levy Act, TTB regulations

Labour Court / employment dispute:
- Trigger: >500 GN 605A questions in corpus AND ELRA 2025 amendments stable 12 months
- Primary source: CMA guidelines, ELRA 2004 as amended 2025

Agricultural compliance:
- Trigger: VICOBA corpus shows >20% agriculture-linked groups AND STR corpus shows
  significant cereal/horticulture questions
- Primary source: EABC STR cereals manual (when published), Village Land Act

Credit scoring (Tier 3):
- Trigger: 18+ months of merchant profiles + named licensed bank partner (NMB/CRDB/TCB)
- NEVER build without a licensed partner. BoT Credit Reference Bureau Regulations apply.

---

> **NEXT PHYSICAL ACTION:**
> Run: `mkdir datasets\tier1a\raw_sources datasets\tier1a\cleaned_pairs datasets\tier1a\eval_set datasets\tier1a\adversarial datasets\tier1a\rejected` (and all other tier directories)
> Then confirm: `dir datasets` shows all tier folders.
> Then proceed to Action 2: validate or create scripts/validate_dataset.py

---

## OUTPUT 3 — sources/whitelist.json
*Produce this file at: C:\Users\jhjh\AFRICA-GIANTS\sources\whitelist.json*
*Full JSON array. Every approved scrape target from STEP 5.*
*Schema per entry as defined below. No comments inside JSON (use notes field).*

```json
[
  {
    "id": "tier1a_tra_001",
    "url": "https://www.tra.go.tz/index.php/tax-information",
    "institution": "Tanzania Revenue Authority",
    "source_type": "government_portal",
    "approved_for": ["tier1a"],
    "use_for": "training",
    "content_type": "html_guide",
    "decay_risk": "Annual",
    "last_verified": "2026-06-01",
    "re_scrape_trigger": "After Finance Act each July",
    "notes": "Primary source for VAT, PAYE, SDL, EFD compliance pairs"
  }
]
```

Include all URLs from STEP 5. Use this exact schema for every entry.

---

## OUTPUT 4 — schema/pair_schema.json
*Produce this file at: C:\Users\jhjh\AFRICA-GIANTS\schema\pair_schema.json*
*This is the canonical metadata contract. All 18 fields required.*
*Pipeline rejects any pair missing any field.*

Produce a JSON object with:
- All 18 fields from STEP 6
- Each field as a key with its type as string value (e.g. "id": "string")
- A "required" array listing all 18 field names
- A "field_descriptions" object with one-line description per field
- An "allowed_values" object for enum fields:
  - domain: ["tier1a", "tier1b", "tier1c", "tier2a", "tier2b"]
  - decay_risk: ["stable", "annual", "event_triggered"]
  - register: ["formal", "business_market", "rural_conversational"]
  - pair_type: ["standard", "disambiguation", "adversarial", "out_of_corpus_refusal"]
  - source_type: ["government_portal", "tier1_advisory", "ilo_unctad_official", "official_gazette"]
  - eval_set: [true, false]

---

## AFTER ALL FOUR FILES ARE CREATED:

1. Copy docs/reference_narrative.md from outputs if it doesn't exist in the repo
2. Create a .gitkeep file in every empty dataset directory so git tracks them
3. Run: `python scripts/validate_dataset.py` — should complete with "0 pairs found, 0 errors"
4. Run: `python scripts/run_eval.py` — should complete with "0 eval pairs found"
5. Update PROGRESS.md: mark directory structure and schema creation as complete
6. Run:
   ```
   git add -A
   git commit -m "Add dataset infrastructure: schema, whitelist, directories, validation scripts"
   git push origin main
   ```
7. Print: "Infrastructure complete. Next action: begin writing first 50 Tier 1A pairs from TRA.go.tz"

Use utf-8 for ALL file operations.
Do NOT run python run.py train.
Do NOT modify any existing training pipeline files.
```