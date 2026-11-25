# NEXT REGEN QUEUE (rows and fixes that need a Kaggle regen; nothing here is applied yet)

Queued 2026-11-17. The served index is 215 rows. The next regen batch applies everything below as ONE package (R15: locked_facts -> CONCISE_BILINGUAL_FACTS / `_COVERAGE_NEW_KEYS` -> Kaggle `regenerate_rag_e5.py` -> fetch -> verify -> commit to BOTH `chike-inference/` and `kaggle/` -> `rag_fact_count` -> pending-regen tests flip -> R16 deploy). The new row is **appended after row 214** so no existing row number moves.

## 1. `company_annual_return_deadline` — the BRELA annual-return deadline (founder, 2026-11-17)

**Why.** The gate's stored reply to `eval_072` states "annual return ... hasa ndani ya miezi 12 kutoka tarehe ya usajili wake". The Act says otherwise, and **no served row states the rule in the asker's vocabulary**: it sits only inside the legacy form-number label of `annual_return_form_number` (row 114). The guard D-FIDELITY-20 (`fidelity.brela_annual_return_deadline_misstated`, live from the next deploy) is the layer that reaches it meanwhile; a guard replaces a wrong answer, it does not retrieve a right one (A1 vs A2), so the row is still owed.

**Source (primary, edition asserted).** Companies Act Cap.212 **R.E. 2023** (running header "[CAP. 212 R.E. 2023]" on every page; cached copy `scratch/tra_pass/companies_act.pdf`, sha256 `3bce27e43b7a9d68…`, **gitignored and UNDECLARED in `data/source_documents/MANIFEST.json`** — step 0 below). **s.131(1):** a company delivers successive annual returns, each made up to a date not later than the "return date", i.e. (a) the anniversary of the company's incorporation, or (b) if the last return was made up to a different date, the anniversary of that date. **s.131(3):** failure to deliver within **twenty-eight days of the return date** makes the company and every officer in default liable to a fine, and a default fine for continued failure. (Section numbers go in metadata only: R44.)

**Step 0 — before anything is encoded.** Copy the Act into `data/source_documents/brela/companies_act_cap212_re2023.pdf` and declare it in the manifest with the edition QUOTED from the header and the sha256 (the repo's own rule: an UNDECLARED source may not settle a figure on its own; `scripts/check_source_editions.py::assert_edition`).

**Locked fact (new key).** `company_annual_return_deadline`: `fact` = the sentence below (ask-aligned lead: the user's words first, the regulatory label later, per R15); `correct_value` = "each annual return is made up to the anniversary of incorporation (or of the last return's date) and delivered within 28 days of that return date; a late company and each officer in default are liable to a fine"; `wrong_patterns` = the 12-months-from-registration and 30-September constructions **written with the Edit tool and checked with `repr()` of the compiled pattern** (the control-character test now guards the file); `primary_source` as above; `verified_by`/`verified_date` filled (R29: a `CONFIRMED` status is not the evidence, `verified_by` is).

**Served row text (CONCISE_BILINGUAL_FACTS, no `key:` prefix; append to `_COVERAGE_NEW_KEYS`).**

> Annual return ya BRELA kwa kampuni inapaswa kuwasilishwa lini? Kila mwaka: kila return hutayarishwa hadi tarehe ya maadhimisho ya kuanzishwa kwa kampuni (au ya return iliyotangulia). Ukichelewa zaidi ya siku 28 baada ya tarehe hiyo, kampuni na maafisa wake wanaweza kutozwa faini (Sheria ya Makampuni). Si miezi 12 tangu usajili, na si 30 Septemba.

**Guards for the regen script** (`kaggle/regenerate_rag_e5.py`): critical queries "Annual return ya BRELA inapaswa kuwasilishwa lini?" and "Mara ngapi kampuni inahitajika kuwasilisha annual return?" (anchor `siku 28 baada ya tarehe hiyo`, which must match exactly one fact: check every committed anchor against the prospective index, the 2026-10-05 lesson); **the rank gate must still PASS** and `check_facts_index_sync` must be clean; `rag_fact_count` 215 -> 216 in `kaggle/chike_config.json` ONLY in the commit that ships the fetched artifacts; `EXPECTED_FACT_COUNT` 216 in `kaggle/eval_gate_production_2026_10_09.py` and the pending-regen / freshness tests flip.

**Then measure, do not assume (R22/R12c):** the fact's rank for the two phrasings BEFORE and AFTER (step zero of any wording job: rank 1 is the ceiling), and a targeted live check of `eval_072` and the two phrasings with a negative (a TAX annual return question still routes to the corporate-return statement).

## 2. Also owed to this batch (data, NOT index; applied separately, listed so they are not lost)

- **The training pair that teaches the wrong claim.** `datasets/tier1a/sft_shaped_pairs/cleaned_pairs_batch_011.jsonl:67` (and its `sft/train_sft.jsonl` copy) opens correctly (anniversary date, "si lazima mwaka wa kifedha") and then CONTRADICTS itself: "Kanuni ya jumla: wasilisha annual return ndani ya miezi 12 ya mwisho wa mwaka wa biashara wako." That sentence is the likeliest origin of the model's 12-month claim. **Proposed repair (awaiting the founder, R37 read first):** drop that sentence and put the rule in its place ("Ukichelewa zaidi ya siku 28 baada ya tarehe hiyo, kampuni na maafisa wake wanaweza kutozwa faini (Sheria ya Makampuni)."), identical in the authored file and the export, with a reach test, exactly as the 2026-11-17 GN 605A repairs.
- `corporate_income_tax_return.wrong_patterns[0]` is already narrowed off BRELA text (no regen needed).

---

## 3. RESOLVED 2026-11-24b (packaged, PENDING the Kaggle run): WCF's contribution BASE. See `kaggle/RUN_REGEN_2026_11_24b.md`. Original entry kept below.

`scripts/locked_facts.json` `wcf_threshold_no_minimum` still says "WCF: 0.5% of gross cash emoluments, from employee 1", and so do `wcf_rate_0_5_percent_confirmed` (rates.py comment) and the WCF rate statement's base wording. The SDL half of the same sentence was corrected on 2026-11-24 against VETA Act s.14(3) ("gross monthly emoluments" INCLUDES allowances; the word "cash" is not in that Act). **The WCF base is defined by a DIFFERENT Act — the Workers Compensation Act Cap.263 — that was NOT read for this.**

**To do:** cache the Workers Compensation Act Cap.263 R.E.2023 (edition asserted in `scripts/check_source_editions.py`), read the contribution provision and its definition of earnings / emoluments / wages verbatim, check Finance Acts 2024/2025/2026 and the WCF Regulations (GN 185/2016) for amendment (R29), and then EITHER confirm "cash" with the quoted text OR correct the wording in `wcf_threshold_no_minimum` (the SDL-correct half is already done), the WCF rate fact and its statement, and fix the corresponding index row (66) in the next regen. **Do not assume the SDL answer carries over: the two Acts define their bases separately.** Owner: the next regen window. Expiry: before the next WCF-touching change (R35: a queue item with no date lapses).


## 4. HELD BY THE FOUNDER 2026-11-24b: the NSSF contribution base (`nssf_contribution_base_wages`), NOT packaged

The page image of Cap.50 R.E.2023 (p.587, `data/source_documents/nssf/nssf_act_cap50_re2023.pdf` page 9) reads "and includes any allowance paid by the employer to the employee either directly or by implication in respect of **living** and any payment of wages in lieu of notice of termination of employment". So the proposed "posho yoyote" was WRONG: the Act names allowances "in respect of living" only. Awaiting the founder's read of the corrected wording; it rides the NEXT regen.
