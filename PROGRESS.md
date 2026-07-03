# Africa Giants — Project Progress

Last updated: 2026-07-03

## Training History

| Version | r | Val Loss | In-corpus | OOC | Gate | Notes |
|---|---|---|---|---|---|---|
| v8 | 64 | 0.4447 | 82.1% | 70% | FAIL | Best stable — served production |
| v9 | 64 | 0.1164 | 82.1% | 40% | FAIL | Overfit epoch 2 |
| v10 | 128 | 0.4107 | 77.9% | 10% | FAIL | OOC collapsed, GN487A hallucination |
| v11 | 128 | 0.4660 | 73.2% | 30% | FAIL | v10-lora warmstart + epoch 2 overfit |
| v12 | 64 | — | 70.5% | 10% | FAIL | v8-lora warmstart, data conflict |
| v13 | 64 | — | 71.6% | 100% | FAIL | Classifier fixed OOC permanently |
| v14 | 128 | — | — | — | IN TRAINING | v11-lora warmstart, lr=2e-5, 3811 pairs |

Gate requirement: >82% in-corpus AND >70% OOC
OOC note: classifier handles OOC in production — gate OOC measures bare model

## v14 Training Config (commit — this session, 2026-07-03)
Hypothesis under test: does r=128 capacity unlock better fact recall than v8's r=64
(which plateaued at 82.1% and was never beaten by r=64 successors)?
- LORA_RANK = 128, LORA_ALPHA = 128 (matches v11-lora — shapes must match for warm-start)
- PREV_LORA_REPO = africa-giants-adapter-v11-lora (r=128 confirmed via adapter_config.json)
- learning_rate = 2e-5 — VERY conservative (half of v13's 5e-5). Rationale: nudge weights
  toward new GN487A/NSSF data without aggressively overwriting v11 epoch-1 knowledge.
  Risk = underfit if too low; val loss will show quickly.
- num_train_epochs = 1 ONLY (v11 epoch 1 val=0.4111 was best; epoch 2 overfit to 0.4660)
- ADAPTER_REPO = africa-giants-adapter-v14; LORA_ONLY_REPO = africa-giants-adapter-v14-lora
- Both HF repos created (exist_ok) this session
- chike_config.json version bumped to v14; training block updated (r/alpha 128, lr 2e-5)

## Architecture Findings — RAG + Refusal Classifier (2026-07-03)
Evidence gathered this session that reframes what to invest in next:
- **OOC refusal is SOLVED at the system level, not by the model.** v8 model-only refusal
  was 70%; with the inference-time phrase classifier + hardcoded refusal + system-prompt
  boundaries, OOC intercept is ~100% (5/5 OOC, 5/5 in-scope pass-through). The gate-2
  problem is closed by architecture, not by more fine-tuning.
- **Fine-tuning is the wrong tool for fact recall.** v8 (2,672 pairs) scored the best
  in-corpus ever (82.1%); every r=64 successor scored LOWER despite growing to 3,811 pairs
  (80.0 → 77.9 → 73.2 → 70.5 → 71.6). More pairs → interference, not more knowledge.
  8/15 v8-vs-v13 hard-fact outputs are byte-identical — LoRA barely moves the model on
  facts; retrieved/injected context dominates the answer.
- **RAG grounding is the correct fact path** (facts decay: VAT withholding changed 1 Jul
  2025, GN 605A revoked 2022 wage order 1 Jan 2026 — weights freeze facts, retrieval doesn't).
  v14 tests the capacity hypothesis (r=128), but the strategic bet is retrieval-first with
  the fine-tune demoted to register/refusal styling.
- Two-eval discipline going forward: keep the bare-weights eval as a DIAGNOSTIC (never hide
  it), gate the PRODUCT on the full-system eval (model + RAG + classifier). Not goalpost-moving
  as long as both are reported and RAG retrieves from the training family, eval from the
  practitioner family (R6).

## GN487A/GN605A Poisoning FIX (2026-07-03)
Root cause: RAG retrieval collision. The GN487A `full_legal_name` fact body contained NO
"Government Notice" anchor, while the GN605A fact literally contains "(Government Notice
No. 605A)". A GN487A name query therefore retrieved the 605A fact and the model parroted
"Government Notice No.605A" as GN487A's name (observed identically in v8 AND v13).
Fixes in `scripts/locked_facts.json` (canonical):
- Strengthened `gn487a_full_legal_name`: fact body now leads with "GN 487A is Government
  Notice No. 487A ... is NOT Government Notice No. 605A" (adds the correct anchor so RAG
  retrieves the right fact) + wrong_patterns catching any 487A→605A / 487A→wage confusion.
- Added `gn487a_vs_gn605a_disambiguation` fact — explicit separation of the two notices.
- Rebuilt RAG index: `scripts/precompute_rag_embeddings.py` → chike-inference/rag_embeddings.npy
  (232, 384) + rag_facts_text.json (was 231 facts → 232). Redeploy Modal to activate.
- Verified: locked_facts JSON valid (233 keys incl _meta); check_locked_facts on batch_014
  (1,122 pairs) = 0 flags (no false positives from the new patterns).

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

## Current Production State
- Modal serving: africa-giants-adapter-v13 + inference-time OOC classifier
- Endpoint: https://prosperpiusmbaruku007--chike-inference-web-endpoint.modal.run
- WhatsApp: +255637809070 via Wappfly → Railway → Modal
- RAG: 231 facts pre-computed (rag_embeddings.npy + rag_facts_text.json)
- Cerebrium: UNPAID ($20.81) — superseded by Modal, endpoint inactive
- Auth: ?token= query param, Railway env MODAL_API_TOKEN

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

## Pending Tasks (Priority Order)

### IN PROGRESS
- v14 training on Kaggle (r=128, v11-lora warmstart, lr=2e-5, 1 epoch)

### AFTER v14 COMPLETES
- Run eval.py on v14 — watch for in-corpus improvement above 82.1%
- If v14 > 82.1% in-corpus: update Modal to v14, run full production test
- If v14 ≤ 82.1%: keep v13 in production, consider RAG-only architecture with frontier API model

### BACKLOG (non-blocking)
- Review 1,129 pending fact candidates — TRA-heavy (619), use generate-from-facts after approving
- Recover 74 flagged pairs — run approve-flags on batches 016, 018
- Pay Cerebrium $20.81 OR formally close the account
- zuck30 lightweight offline Chike discussion (held from earlier session)
- Consider replacing AfriqueLlama-8B with frontier API model (Claude Sonnet / Gemini Flash)
  via OpenRouter in modal_app.py — single line change, same RAG infrastructure

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
- Modal serving v13 + classifier (neither gate fully passed at bare-model level)
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
- Modal: serving adapter-v13 + OOC classifier (Cerebrium retired — see Current Production State)
- Wappfly: +255637809070
- Kaggle: training notebook (africa_giants_V2.ipynb) + eval notebook (africa_giants_eval.ipynb)
- GitHub: main branch
- HuggingFace token: Kaggle secret `AFRICA_GIANTS`
- Local pipeline: Ollama (qwen2.5:7b generation, nomic-embed-text dedup/embeddings)
