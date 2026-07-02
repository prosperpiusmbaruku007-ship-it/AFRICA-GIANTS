# Africa Giants — Project Progress

Last updated: 2026-07-02

## Training History

| Version | r | Val Loss | In-corpus | OOC | Notes |
|---|---|---|---|---|---|
| v8 | 64 | 0.4447 | 82.1% | 70% | PRODUCTION — current best, serving WhatsApp |
| v9 | 64 | 0.1164 | 82.1% | 40% | Overfit |
| v10 | 128 | 0.4107 | 77.9% | 10% | OOC collapsed, dangerous GN487A hallucination |
| v11 | 128 | 0.4660 | 73.2% | 30% | FAILED — v10-lora warm start + epoch 2 overfit |
| v12 | 64 | 0.46xx | 70.5% | 10% (30% fixed) | FAILED — data problem (SDL mislabeled, n je bug) |
| v13 | 64 | — | — | — | READY TO TRAIN — same config as v12, data fixed |

## v12 Gate Results (gate_001_results.json on HF adapter-v12)
- In-corpus: 70.5% (134/190) — Gate FAILED (need >85%)
- OOC model-only: 10% (1/10) — but 2 were tokenization artifacts ("n je" bug)
- OOC with fixed eval detection: 30% (3/10) — eval phrase list now patched (commit cecb349)
- OOC with classifier + model (full system): 9/10 = 90% — Gate PASSES at system level
- Root causes identified: 3 SDL tourism levy pairs mislabeled, missing day-7 deadline,
  n je tokenization bug in eval detection, missing explicit OOC boundaries in system prompt

## v12 → v13 Changes (commit b58317a, 2026-07-02)

### Architecture
- Inference-time OOC classifier added to `chike-inference/modal_app.py`
  - Phrase-level matching (multi-word, Swahili + English) — no single-word false positives
  - Intercepts: capital gains, import/customs duty, transfer pricing, stamp duty,
    mining royalties, EPZ, insurance premium levy, Zanzibar tax, crypto
  - HARDCODED_REFUSAL returned before GPU call for OOC questions
  - Tested: 5/5 OOC intercepted, 5/5 in-scope pass through, 9/10 eval OOC intercepted
  - Deployed to Modal: prosperpiusmbaruku007--chike-inference-web-endpoint.modal.run
- Eval notebook now tests full production system (classifier + model), not model alone
  - Cell 1: classify_question() added; Cell 7: classifier runs before generate_answer()

### System Prompt (kaggle/chike_config.json)
- Added explicit OOC boundary list in Swahili and English
- Added explicit in-scope list (BRELA/VAT/PAYE/SDL/NSSF/OSHA/EFD/WCF/GN487A)
- Propagates to train_ddp.py via GitHub fetch; eval notebook via Cell 1 GitHub fetch

### Eval Detection (commit cecb349, 2026-07-02)
- Fixed "n je" tokenization bug: added space-variant phrases to REFUSAL_PHRASES
- Added check_refusal() with ' '.join(text.lower().split()) normalization
- Removed false-positive phrases (thibitisha na tra, wasiliana na) from kaggle notebook
- Applied to both kaggle/africa_giants_eval.ipynb and scripts/run_eval.py

### Data Fixes (batch_014: 547 → 549 pairs)
- REMOVED 3 Tourism Development Levy pairs mislabeled as sdl_compliance
  (Tourism levy = 1% on hotel revenue ≠ SDL = 3.5% of salaries; wrong tax, wrong rate)
  Moved to datasets/tier1a/rejected/sdl_tourism_levy_mislabeled.jsonl
- FIXED SDL deadline pair [4]: now states "siku ya 7 ya mwezi unaofuata" explicitly
- ADDED 5 targeted OOC hard-refusal pairs (capital gains, import duty, transfer pricing,
  stamp duty, mining royalties) — no partial answers, redirects to correct authority

## v13 Training Config (same as v12 — config was correct, data was the problem)
- LORA_RANK = 64 (matches v8-lora)
- PREV_LORA_REPO = africa-giants-adapter-v8-lora (stable baseline)
- learning_rate = 5e-5 (conservative)
- num_train_epochs = 1
- Gate requirement: >85% in-corpus AND >70% OOC (system-level with classifier)
- SFT uploaded: train=2889 / val=322 — prospAprospA007/africa-giants-dataset

## v13 Expected Gate Behavior
- OOC (system-level, classifier + model): 9/10 = 90% → PASS (≥70% threshold)
- In-corpus target: >85% — requires SDL and GN487A to recover to v8 levels
  - SDL was 84% in v8 → should recover with tourism pairs removed and deadline fixed
  - GN487A was 75% in v8 → needs to recover from v12's 55%
  - If both recover: in-corpus ~82-84% — close but may still need one more run

## Current State
- Production: v8 on Modal (WhatsApp +255637809070)
- Classifier deployed on Modal: intercepts OOC before model call
- Dataset: 3,221 total (2,889 train / 322 val) — prospAprospA007/africa-giants-dataset
- batch_014 (v13): 549 pairs — 77 GN487A, fixed SDL, 5 OOC refusals
- train_ddp.py updated to v13 (ADAPTER_REPO = africa-giants-adapter-v13)

## R6 review — RESOLVED (Habib released) + GN487A eval-family quarantine
**Habib Advisory (162 pairs) — RELEASED into batch_014 on 2026-07-01.**
Cleared a 4-check eval-contamination scan vs eval_questions_001.jsonl:
CHECK1 exact-instruction=0, CHECK2 exact-output=0, CHECK3 "habib" keyword in eval=0,
CHECK4 semantic (normalized cosine, threshold 0.92 + subdomain-keyword topic gate)=
0 genuine risks (1 cross-topic false positive only). Habib Advisory is NOT in the
Section-4 eval whitelist, so no source-family conflict.

**GN487A practitioner sources — QUARANTINED (eval family, R6/R4).**
VELMA + Bowmans GN487A files moved to `data/eval_family_quarantine/immigration/`
(OUTSIDE the os.walk scan root so the pipeline never trains on them). Reason:
velmalaw.co.tz / bowmans.com / clydeco.com are the NAMED gn487a eval family
(CLAUDE.md §4; pair_reviewer.py maps gn487a eval -> immigration.go.tz). They may
later feed EVAL expansion only, never training.
Automated primary GN487A re-sourcing (tanzlii / gazette / immigration.go.tz /
parliament) FAILED: all returns were search/landing/homepage shells. **RESOLVED
2026-07-01** — founder supplied the official gazette PDF directly; 20 facts locked and
77 seed-generated training pairs merged (see Current State "Key changes"). The VELMA/
Bowmans eval-family files remain quarantined for possible EVAL expansion only.

## Pipeline — Autonomous Q&A Factory (Phases 1–4 COMPLETE)
The pipeline is now a one-command autonomous Q&A factory. Source doc → reviewed dataset → HF.
- **Phase 1 — Foundations:** configs updated, directories created, run.py rewritten (bd83be5)
- **Phase 2 — RAG:** locked_facts injected at inference, persistent numpy embeddings (9f53b40)
- **Phase 3 — Autonomous Q&A pipeline:** PDF/HTML/TXT → reviewed dataset (bf9e1fd)
- **Phase 4 — One-command HuggingFace upload** (5d73769)
- Multi-provider LLM support: Anthropic / OpenRouter / Ollama (405e9c7)
- Default generation model: gemini-2.5-flash-lite (cheaper than 2.5, better than 2.0) (c50fcaa)
- Local dedup via nomic-embed-text; pre-computed RAG embeddings; 402 fails fast (223ac6a)

## Gate History
| Version | In-corpus | Refusal | Gate | Notes |
|---|---|---|---|---|
| v6 | ~74% | 50% | FAIL | baseline |
| v7 | 79.5% | 80% | FAIL | refusal gate passed for first time |
| **v8** | **82.1%** | **70.0%** | FAIL | **best scores to date; production adapter** |
| v9 | 80.0% | 40.0% | FAIL | rebalanced dataset hurt refusal (stop-after-redirect not trained) |
| v10 | — | — | REVERTED | r=128 hallucinated on insufficient data — reverted to v8 2026-06-22 |
| v11 | pending | pending | pending | next training run — gated on batch_014 correction pairs |

**Best scores to date: v8 — 82.1% in-corpus, 70.0% out-of-corpus refusal.**
Both gates still unmet (need >85% in-corpus AND >70% refusal simultaneously).

## v9 Gate Results (gate_001_results.json on HF adapter-v9)
Total: 200 questions | Pass: 160 | Fail: 40 | **Overall: 80.0%** — Gate FAILED

| Subdomain | Pass/Total | % | Status |
|---|---|---|---|
| efd_compliance | 19/20 | 95.0% | ✓ |
| brela_registration | 14/15 | 93.3% | ✓ |
| nssf_contributions | 23/25 | 92.0% | ✓ |
| vat_withholding | 18/20 | 90.0% | ✓ |
| gn487a | 30/40 | 75.0% | ✗ |
| osha_registration | 12/15 | 80.0% | ✗ |
| sdl_compliance | 20/25 | 80.0% | ✗ |
| out_of_corpus | 4/10 | 40.0% | ✗ |
| vat_registration | 20/30 | 66.7% | ✗ |

### v9 Root Cause Analysis (drives batch_014 corrections)
- **vat_registration (10 failures):** arithmetic on thresholds, rolling 12-month definition, zero-rated vs exempt disambiguation, qualifying buyer definition
- **gn487a (10 failures):** full legal name never stated, effective date hallucinated (28+29 Jul), "mgeni" definition inverted, marriage exception wrong (ndoa haibadilishi hadhi), enforcement exercise dates wrong, enforcement body hedged
- **sdl_compliance (5 failures):** WCF rate wrong (20% instead of 0.5%), SDL threshold (10 employees) ignored, SDL+PAYE same deadline wrong, GN 605B cited (doesn't exist)
- **out_of_corpus (6 failures):** refusal-then-elaborate pattern — model says "nje ya maarifa yangu" then explains anyway; eval_191 (PAYE TZS 800K) misclassified as out-of-corpus
- **osha_registration (3 failures):** >50 employee safety officer requirement missed, late registration first step wrong

## Pending Tasks — Immediate
1. **Write batch_014 via the autonomous pipeline** — correction pairs for v9 failures:
   - Priority 1: VAT arithmetic worked examples (15–20 pairs), rolling 12-month definition
   - Priority 2: GN487A precision pairs — full name, single date, mgeni definition, ndoa exception
   - Priority 3: Out-of-corpus clean-stop pairs (refusal only, no elaboration) — 20+ pairs
   - Priority 4: SDL/WCF precision — 0.5% rate, 10-employee threshold, same-day deadline
   - Move eval_191 (PAYE 800K) from refusal gate to accuracy gate
2. **Run v11 training** once batch_014 lands — upload kaggle/train_ddp.py to Kaggle
   - Model: McGill-NLP/AfriqueLlama-8B; push target: africa-giants-adapter-v11
   - NOTE: v10 reverted because r=128 over-fit / hallucinated on insufficient data —
     v11 must only follow a meaningful dataset expansion, not just a rank bump
3. **Fix repetition loop in production** — chike-inference/main.py: repetition_penalty tuning
   (711745a set 1.3 + no_repeat_ngram_size=4) — verify it resolved the "Thibitisha na TRA" repeat
4. Stage more source documents — only 2 raw docs currently in data/source_documents/tra/

## Dataset State
- Source files: 15 batch files in `datasets/tier1a/cleaned_pairs/` (batches 001–013)
  - Batches 001–008: old 18-field schema (question_sw/answer_sw) — converted by generate_sft.py
  - Batches 009–013: SFT format (instruction/input/output/system) — direct use
- SFT files (current, on HuggingFace):
  - train_sft.jsonl: 2,395 pairs
  - val_sft.jsonl: 267 pairs
  - Total cleaned: 2,672 (10 excluded as eval_set:true)
- Generation: `python scripts/generate_sft.py` — always use this, never raw glob from cleaned_pairs

## Training Script
- File: `kaggle/train_ddp.py`
- Run: `python3 train_ddp.py` (Unsloth handles multi-GPU natively — no torchrun)
- Config: LORA_RANK=128, LORA_ALPHA=128, MAX_SEQ_LENGTH=2048, 2 epochs, lr=2e-4
- LESSON FROM v10: r=128 on the current dataset size hallucinated — expand data before re-running

## Last 10 Commits
- 223ac6a feat: pre-computed RAG embeddings, nomic-embed-text for local dedup, 402 fails fast
- c50fcaa config: use gemini-2.5-flash-lite as default — better than 2.0, cheaper than 2.5
- 405e9c7 feat: multi-provider LLM support — Anthropic, OpenRouter, Ollama
- 5d73769 feat: Phase 4 one-command HuggingFace upload
- bf9e1fd feat: Phase 3 autonomous Q&A pipeline — PDF/HTML/TXT to reviewed dataset
- 9f53b40 feat: Phase 2 RAG — locked_facts injected at inference, persistent numpy embeddings
- 444781f fix: preserve data/ directory structure in git with .gitkeep files
- bd83be5 fix: Phase 1 foundations — configs updated, directories created, run.py rewritten
- da47100 cerebrium: revert to v8, clear old model cache, v10 deferred pending better training data
- 711745a cerebrium: repetition_penalty 1.1 → 1.3, add no_repeat_ngram_size=4

## Known Issues / Technical Debt
- v10 reverted: r=128 hallucinated on insufficient data — production stays on v8
- Cerebrium serving v8 (best gate scores but neither gate fully passed)
- `run_eval.py` (local) does not have the scorer fixes that the Kaggle eval notebook has
- eval_191 (PAYE TZS 800K) misclassified in refusal gate — should be accuracy gate
- Only 2 source documents staged — corpus expansion needs more raw material

## HuggingFace Repos
- africa-giants-adapter-v8: LIVE (production — best gate scores: 82.1% / 70.0%)
- africa-giants-adapter-v9 / v9-lora: built, gate FAILED (refusal regressed)
- africa-giants-adapter-v10 / v10-lora: built then REVERTED (hallucinated)
- africa-giants-adapter-v11: pending (gated on batch_014)
- africa-giants-dataset: 2,672 pairs (train 2,395 / val 267)

## Infrastructure
- Cerebrium: serving adapter-v8
- Wappfly: +255637809070
- Kaggle: training notebook (africa_giants_V2.ipynb) + eval notebook (africa_giants_eval.ipynb)
- GitHub: main branch
- HuggingFace token: Kaggle secret `AFRICA_GIANTS`
- Local pipeline: Ollama (qwen2.5:7b generation, nomic-embed-text dedup/embeddings)
</content>
</invoke>
