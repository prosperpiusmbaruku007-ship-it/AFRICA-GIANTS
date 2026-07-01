# Africa Giants — Project Progress

Last updated: 2026-07-01

## Current State
- **Production adapter: africa-giants-adapter-v8** — served via Cerebrium AND Modal
  - Cerebrium: https://api.aws.us-east-1.cerebrium.ai/v4/p-e3f41403/chike-inference/run
    — **UNPAID, outstanding bill $20.81**
  - Modal (LIVE, v8): https://prosperpiusmbaruku007--chike-inference-web-endpoint.modal.run
    — waiting for v11 weights (cutover steps in docs/runbook_modal_cutover.md)
  - v10 built but REVERTED 2026-06-22 (r=128 hallucinated on insufficient data — see Gate History)
- Live on WhatsApp: **+255637809070 via Wappfly → Railway handler → Modal endpoint**
- RAG: pre-computed embeddings serving locked facts at inference
  (chike-inference/rag_embeddings.npy + rag_facts_text.json)
- Dataset: **3,209 pairs total** (batch_014 = 547 pairs across 10 subdomains)
  - SFT on HF prospAprospA007/africa-giants-dataset: **2,888 train / 321 val** (10 held eval_set:true)
  - locked_facts.json (scripts/locked_facts.json): **209 entries**
  - 59 source docs processed (27 produced facts; 32 produced zero confirmed facts)
- **v11 training: READY TO RUN** — kaggle/train_ddp.py: r=128, α=128, lr=1e-4, 2 epochs,
  warm-start from adapter-v10-lora; pushes to adapter-v11 / adapter-v11-lora (HF repos created).
  Run: `python3 train_ddp.py`.
- Best gate scores to date: **v8 — 82.1% in-corpus / 70.0% refusal** (neither passed; need >85% AND >70%).

### Key changes this session (2026-07-01)
- Habib Advisory (162 pairs) released into batch_014 after a clean 4-check eval-contamination scan.
- PRIORITY-2 false-confirm bug FIXED (classify_fact domain-prefix guard); NSSF Act batch_015/016 (14) discarded.
- GN487A GAP CLOSED: founder supplied the official gazette PDF; 20 facts locked; 77 seed-generated pairs
  (48 approved + 29 recovered from CHECK2/CHECK5-only flags) merged; new CHECK7 activity-accuracy guard added.
  gn487a training coverage 12 -> 89 pairs.

### Pending backlog (unfinished — NOT blocking v11)
- **74 flagged pairs** across 9 data/flagged/batch_*_flagged.jsonl (largest: batch_017 Habib = 41; mostly CHECK4/CHECK2).
- **1,129 unreviewed fact candidates** in data/flagged/new_facts_pending.json (TRA 619, BRELA 212, NSSF 144, …).
- **3 stale CHECK7 gn487a flagged pairs** held in data/reviewed/gn487a_seed_flagged.jsonl (non-listed / wrong-number).

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
