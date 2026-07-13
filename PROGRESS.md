# Africa Giants — Project Progress

Last updated: 2026-07-12

## v16 Shared-Module Extraction — Complete

modal_app.py and eval.py now import chike.prompting and chike.generation_cleanup
instead of carrying inline copies of the RAG wrapper and stop/clean logic. This
closes the drift risk flagged during both earlier ports — there is now exactly
one place each piece of logic is defined (chike/prompting.py,
chike/generation_cleanup.py) and three places that use it via import: the
orchestrator, modal_app.py (via Modal's add_local_dir), and eval.py (via
fetch-and-exec of the two files, matching the existing pattern used to load
eval.py itself).

Production verified unaffected: 5 spot-check questions (GN487A, SDL, BRELA,
VAT withholding, zero-rated VAT) byte-identical to pre-change baseline.

### Gate re-verification scope (important — do not misread)

The eval.py gate tests the v15 pipeline (eval's own retrieve/decompose/generate,
mirroring production modal_app.py) with build_chat_prompt + clean_generated_reply
now sourced from the shared chike/ modules. It confirms the shared-module
extraction is behavior-preserving. It does not test the v16 orchestrator end-to-
end — the orchestrator is validated separately via FakeBackend unit tests and
raw-endpoint spot-checks. No gate currently exercises the v16 orchestrator
pipeline.

## Repo-integrity fix — untracked __init__.py files (found and fixed same session)

.gitignore's _*.py pattern was silently matching all __init__.py files project-wide,
meaning chike/__init__.py, chike/model_abstraction/__init__.py, and
chike/rules_engine/__init__.py were never tracked in git since item 1 of this
build phase, despite every commit succeeding and all local tests passing.

Root cause: Modal (add_local_dir) copies the working directory directly and
eval.py fetches individual files by name — both sidestep Python package import
entirely, so neither path ever exercised the actual package structure. Only a
fresh git clone would have hit ImportError on FakeBackend and AttributeError
on rules_engine.compute — confirmed empirically via git archive HEAD extraction
before and after the fix.

Fix: narrowed the ignore pattern to scripts/_*.py (matching the documented
scratch-file convention established earlier this session), committed the three
previously-untracked __init__.py files, and re-verified via fresh git-archive
extraction that the package now imports correctly from a clean checkout.

Lesson for future sessions: any local-only verification method (tests, Modal
deploy, manual imports) that runs against the working directory rather than a
fresh checkout can mask git-tracking gaps. The git-archive-extraction check
used here is now the standard verification method for confirming a package
is actually complete in git, not just present on disk.

## v16 status — porting phase complete

Six components built, tested, and proven against the real fine-tuned v15 model:
model abstraction layer, orchestrator, rules engine, retrieval, prompt wrapper,
generation cleanup. Fact-path questions (Q1-Q5 pattern) match production
exactly. Shared-module extraction eliminates duplication across all three
consumers (orchestrator, modal_app.py, eval.py).

Remaining gap: slot extraction for compound/compute questions. Confirmed this
session that v15 never solved this — the fine-tuned model attempted
calculations directly from natural language with no dedicated extraction step,
succeeding only on memorized scenarios. This is new architecture with no
port target, correctly blocked pending real ambiguous Swahili phrasing data
collection — not further engineering work.

## v16 Compute-Path Investigation — Resolved (not a bug, a scope confirmation)

Investigated whether v15 had a working slot-extraction step to port, following
the same pattern that succeeded for the wrapper, stop/clean, and decompose ports.

Finding: v15 never had slot extraction. The fine-tuned 8B model attempted
compound calculations directly from natural language in one shot, succeeding
only on scenarios matching a memorized worked example (e.g. exactly 12
employees at TZS 600,000) and failing on any other numbers — this is the
exact structural weakness documented throughout this project.

This means chike/extraction.py (built in item 4) is not a port target — it's
new architecture with no v15 precedent to validate against. This confirms,
rather than changes, the original scoping decision: the interface shape is
built and tested against FakeBackend; the confidence threshold and real
extraction-prompt design remain correctly blocked pending real ambiguous
Swahili phrasing data, which does not yet exist.

## v16 status summary

Fact-path (Q1-Q5 pattern): COMPLETE. Proven end-to-end through real
retrieval, real model, real wrapper, real cleanup, real decompose. Matches
production exactly.

Compute-path (Q6 pattern): PARTIALLY COMPLETE.
- Context loss: FIXED (decompose_query port)
- Routing to rules engine: WORKING (proven in earlier orchestrator tests
  with FakeBackend)
- Slot extraction from real free text: NOT YET BUILT — correctly blocked,
  requires real data collection, not more architecture work

Next session priority, unchanged from earlier scoping: collect real
ambiguous Swahili phrasing before touching slot extraction further. In the
meantime, the one remaining low-risk port available is the 3-way shared-module
extraction (chike/prompting.py and chike/generation_cleanup.py into
modal_app.py and eval.py, closing the drift risk flagged during both of those
ports) — this is available now and requires no new data.

## v16 Fact-Path Parity — Achieved

Q1-Q5 (single-topic fact questions) now produce answers through the v16
orchestrator that match production exactly: correct substantive content
(TZS amounts, percentages, Ndiyo/Hapana) AND correct format (no ramble,
no fabricated follow-up turns, correct domain citations).

This was proven empirically, not assumed:
1. Isolated the gap via a raw-generation Modal endpoint bypassing production's
   opaque pipeline
2. Confirmed retrieval, rules engine, and orchestrator routing were correct
   from the start — the gap was entirely in generate/validate stage formatting
3. Ported the RAG wrapper (chike/prompting.py) — fixed substantive correctness
4. Ported the stop/clean stage (chike/generation_cleanup.py) — fixed format/ramble
5. Both ports extracted into shared modules rather than duplicated inline,
   directly avoiding the class of divergence bug that caused two earlier
   production incidents this session

Remaining gap — Q6 (compound/compute questions):
- decompose_query not yet ported — thin stub splits on ?/(2)/(3) and loses
  context (employee count, salary figures) needed for the compute sub-questions
- Slot extraction from the 8B model doesn't reliably emit parseable structured
  output from a bare prompt — needs either a few-shot/chat-formatted extraction
  prompt (port from what if anything worked in v15) or routing extraction to
  a frontier model, consistent with the earlier-documented finding that
  arithmetic/compound-question handling is the 8B model's structural weakness

Next priority: port decompose_query (known-working logic, straightforward port)
before attempting to fix slot extraction (open question, needs investigation).

## v16 Build Progress

Items 1-4 complete, tested, committed:
1. Model Abstraction Layer — chike/model_abstraction/ (10/10 tests) — commit 55d516c
2. Orchestrator pipeline skeleton — chike/orchestrator.py (8/8 tests) — commit 329ccc5
   (was 7/7 at item 2; +1 clarification-routing test added when item 4 wired extraction in)
3. Deterministic rules engine — chike/rules_engine/ (pre-existing, now committed) — commit 31bc921
4. Slot extraction interface (confidence-signal shape only) — chike/extraction.py (8/8 tests) — commit 729dc54

Total: 26/26 tests passing, zero network/GPU dependency for the full test suite.
(Counts differ from the original build note's 6/23 estimate: extraction shipped 8 interface
tests, not 6, and the orchestrator gained a clarification-routing test in item 4 — 26 actual.)

BLOCKED — requires real data, do not proceed without it:
- Confidence threshold tuning for extraction routing
- Clarification response phrasing
- Both explicitly marked as TODO in chike/extraction.py (and the orchestrator sentinel
  CLARIFICATION_PENDING), tagged "requires real ambiguous-phrasing test data — see
  PROGRESS.md milestone 5 gap"

Remaining v16 items not yet started (per original build order):
- Real retrieval wiring (currently stub retriever in orchestrator)
- Real classifier wiring (currently thin phrase-match stub)
- Real decompose_query enumeration logic (currently thin newline/? split stub)
- Fidelity validation (currently stub, always returns True)
- Change detection job
- Monitoring/logging
- Admin tooling
- Frontier model comparison harness

Next session priority: collect real ambiguous Swahili phrasing (see RISKS.md,
'over-clarification' risk) before touching extraction further. All other stub
components (retrieval, classifier, decompose) can be replaced with the real,
already-proven v15 logic in parallel — none of that requires new data, it
requires porting existing working code into the new orchestrator shape.

## Real WhatsApp Testing Findings (2026-07-08) — Post v15 91.1% Gate

Confirmed working well:
- Compound question handling stable across multi-message conversation
- VICOBA multi-jurisdiction question correctly separated NSSF/BRELA/TRA scope
- EFD-VAT deadline interaction correctly answered
- GN487A inheritance question correctly identified as still prohibited (de facto control test)

New calculation errors confirmed (same root cause as documented NSSF limitation):
- SDL calculation wrong for 15 employees @ 450,000: gave TZS 63,750, correct is TZS 236,250
  (15 × 450,000 × 3.5%). Appears to compute per-employee flat amount rather than percentage of salary.
- NSSF calculation wrong for same scenario: gave TZS 675,000 (using only 10% employer share),
  correct is TZS 1,350,000 (20% total). Confirms scenario-pinned facts (600,000/12-employee
  example) do not generalize to different salary/headcount combinations.

New potential hallucination — needs verification:
- GN487A ownership threshold: model stated 'asilimia 25%' as the prohibited ownership
  percentage. This does NOT appear in locked_facts.json. GN487A prohibits OPERATING listed
  activities, not ownership percentage per se (see gn487a_shareholder_vs_operator_distinction).
  This number appears fabricated. Needs verification against primary source before any
  correction — do not assume it is wrong without checking, but do not treat it as confirmed
  either.

Confirms architectural conclusion already documented: scenario-pinned calculation facts
in RAG do not generalize. Every new salary/employee-count combination not matching a
pinned example risks wrong arithmetic. This is the clearest evidence yet that the fix
path is a calculation-capable frontier model for arithmetic-type questions, not more
worked examples in locked_facts.

Recommended next session priority:
1. Verify the GN487A 25% ownership claim — check TanzLII/gazette, confirm hallucination
   or find missing locked fact
2. Consider whether SDL/NSSF/PAYE calculation questions should route to a frontier API
   model (Claude/Gemini via OpenRouter) for the arithmetic step specifically, using RAG
   only to supply the rate/threshold facts, rather than expecting the 8B model to do
   percentage math reliably
3. This is a scoping decision, not a quick fix — do not attempt in a reactive cycle

## GATE PASSED — v15 (2026-07-07) — FIRST PASSING RESULT IN PROJECT HISTORY

In-corpus: 87.9% (167/190) — PASS (threshold 85%)
Out-of-corpus: 100% (10/10) — PASS (threshold 70%)

Subdomain results:
- brela_registration: 100.0%
- out_of_corpus: 100.0%
- efd_compliance: 95.0%
- osha_registration: 93.3%
- sdl_compliance: 92.0%
- vat_registration: 86.7%
- gn487a: 85.0%
- vat_withholding: 85.0%
- nssf_contributions: 76.0% (only subdomain below 85%, does not block aggregate pass)

What got us here:
1. 750 hand-coded training pairs (batch_015) written in v8's original style
2. Removed 9 eval-contaminated pairs present in corpus since v8 (R6 leak)
3. e5-base embedder migration — fixed multilingual retrieval gap (MiniLM buried English facts at rank 13-48 for Swahili queries)
4. Concise bilingual high-stakes facts (GN487A, SDL, NSSF, WCF, BRELA) — short Swahili-dominant text with values in both words and digits
5. RAG noise filter — dropped 26 bare legal citations/exemption facts that were generic attractors
6. Fixed PAYE band retrieval by consolidating into paye_bands_with_examples with worked example
7. CRITICAL FIX: no_repeat_ngram_size=2 was destructively interacting with RAG injection —
   forbidding the model from reproducing exact facts it was handed (tra.go.tz, TZS amounts),
   causing 45% domain corruption (.tz→.ke). Fixed by setting no_repeat_ngram_size=0.
8. Eval.py now tests the full production system (classifier + RAG + model) per R12 —
   previously tested bare model weights only

Production deployed: adapter-v15 on Modal (2026-07-07), live at
https://prosperpiusmbaruku007--chike-inference-web-endpoint.modal.run

Post-deploy endpoint smoke test (6 critical facts): 5/6 correct and clean (no .ke
corruption, no token mashing). GN487A 10M, SDL 3.5%, BRELA 22,000, VAT withholding 6%,
zero-rated input VAT — all correct. KNOWN CAVEAT: PAYE-on-800,000 query returned
TZS 202,000 instead of 78,000 — the model over-reasoned the bands instead of using the
fact's stated answer. Fragile to phrasing (gate eval_191 phrasing passed). The concise
paye_bands_with_examples fact lists bands that invite miscalculation; a follow-up should
state 78,000 more emphatically or drop the band table. Not a corruption/retrieval issue.

## v15 Production Fixes — Complete (2026-07-08)

Fixed via real WhatsApp testing feedback:
1. Compound question fabrication — leading-question strip now loops, removes
   all consecutive fabricated (N) questions before the real answer
2. Compound answer truncation — max_new_tokens 280→350. All substantive
   information (SDL amount, NSSF amount, deadline, penalty rate) now completes.
   The model tends to append a redundant self-generated summary after delivering
   the full answer; this summary may still clip at 350 tokens, but no substantive
   content is lost — only a restatement of information already given.
3. NSSF compound calculation (120,000 → 1,440,000) — contrast-language fact rewrite
4. Domain corruption (.ke, nssf.or.tz) — post-generation regex correction
5. Repetition loops on complex queries — decompose_query enumeration pattern extension

Remaining known limitations (documented, not fixed):
- Triple-compound queries with untrained number scenarios (e.g. salary 900,000 when
  facts are pinned to 600,000/800,000) still produce refusal collapse rather than a
  coherent attempt. Requires a calculation engine or frontier API model with genuine
  arithmetic reasoning — not more RAG fact tuning. Backlogged.
- Model generates a fabricated preamble before some compound answers (stripped from
  display, still consumes generation budget) and a redundant summary after (may clip
  but is non-substantive). Root fix requires training data demonstrating direct-answer
  behavior on compound questions without preamble or recap — not a generation parameter.

RAG index: 210 facts, e5-base 768-dim, 14 critical regression guards in
kaggle/regenerate_rag_e5.py including contrast-language checks.

Gate result holding: v15 at 87.9% in-corpus / 100% OOC — confirmed no regression
from any production fix via spot-check (GN487A/SDL/BRELA/VAT withholding/zero-rated
VAT) after each change including the final max_new_tokens adjustment to 350.

## Known Limitations — Compound Query Generation (2026-07-08)

Surfaced via real WhatsApp testing of multi-part compound questions. Retrieval and
loop behaviour were fixed (decompose_query enumeration extension, commit 3e47597;
NSSF fact rewrite + regen guard, commits 3d6c1e2 / bd348f7). The remaining issues
below are model-generation limits of the 8B AfriqueLlama, not retrieval bugs.

1. Model number-selection failure on scaled calculations
   Fact retrieval works correctly (nssf_calculation_example retrieves at rank 1,
   contains the correct scaled total AND single-employee figure). The 8B model
   still sometimes selects the wrong number from a correct fact when multiple
   numbers appear in context. Attempted fix: explicit 'SI TZS 120,000' contrast
   language in the fact text (commit 3d6c1e2). Partial mitigation, not a full fix.

2. Scenario-pinned calculation facts do not generalize
   locked_facts calc examples are written for specific numbers (e.g. NSSF for
   12 employees at 600,000 each; PAYE for salary of 800,000). When a real user
   asks about different numbers (e.g. salary of 900,000), the wrong scenario's
   fact retrieves and the model either uses the wrong fixed answer or fails to
   adapt. This is a structural limitation of fact-based RAG for arithmetic —
   the system does not have a calculation engine, only worked examples.

   Fix path: either (a) add many more worked examples covering common salary
   bands, which does not scale, or (b) frontier API model with genuine
   arithmetic reasoning capability replacing the 8B parametric approach for
   calculation-type questions specifically.

3. Empty/refusal collapse on complex compound queries
   When retrieval succeeds (3 correct facts for 3 sub-questions) but the
   facts do not perfectly match the asked scenario, the model sometimes
   produces a bare refusal ('Thibitisha na TRA') rather than attempting a
   partial or approximate answer using the general principles it does know.

## Session End State (2026-07-05)

### Production system (live on WhatsApp +255637809070)
- Model: africa-giants-adapter-v14 on Modal (T4 GPU, scales to zero)
- RAG: 206 facts, cosine similarity, concise bilingual high-stakes facts
- Classifier: inference-time OOC filter (capital gains, mining, import duty etc.)
- Gate scores: 83.2% in-corpus (best ever), 90% OOC

### What works reliably in production (RAG-driven)
- GN487A penalty: TZS 10M non-citizen, TZS 5M facilitator ✅
- SDL rate: 3.5%, threshold 10+ employees ✅
- VAT registration threshold: TZS 200M/12mo, TZS 100M/6mo ✅
- VAT withholding: 6% services, 3% goods ✅
- NSSF: 10% employer + 10% employee = 20% total ✅
- BRELA annual return: TZS 22,000 ✅
- WCF rate: 0.5% of gross payroll ✅
- Capital gains / import duty / mining OOC: hardcoded refusal ✅

### Known limitations (model-generation, not RAG)
- Multi-part questions: RAG retrieves top-3 facts, cannot cover 5 subdomains in one query
- Minor Swahili typos: TZSh, asilimai, garbled domain on secondary topics
- SDL combined-query threshold: correct for simple queries, fails for mixed queries
- NSSF URL: updated to nssf.go.tz (old nssf.or.tz kept failing DNS)

### Architecture insight confirmed this session
The model handles Swahili formatting and persona.
Facts come from locked_facts.json via RAG.
Training more versions will not improve factual accuracy — RAG does that.
Next improvement = query decomposition for multi-part questions + stronger cross-lingual embedder.

### Immediate next session priorities
1. Query decomposition — break multi-part WhatsApp messages into sub-queries before RAG
2. intfloat/multilingual-e5-base embedder — better cross-lingual retrieval than MiniLM
3. Hand-coded pairs targeting specific eval failures (50 pairs, not yet done)
4. Pay Cerebrium $20.81 or close account
5. zuck30 lightweight offline Chike discussion

## Training History

| Version | r | Val Loss | In-corpus | OOC | Gate | Notes |
|---|---|---|---|---|---|---|
| v8 | 64 | 0.4447 | 82.1% | 70% | FAIL | Best stable — served production |
| v9 | 64 | 0.1164 | 82.1% | 40% | FAIL | Overfit epoch 2 |
| v10 | 128 | 0.4107 | 77.9% | 10% | FAIL | OOC collapsed, GN487A hallucination |
| v11 | 128 | 0.4660 | 73.2% | 30% | FAIL | v10-lora warmstart + epoch 2 overfit |
| v12 | 64 | — | 70.5% | 10% | FAIL | v8-lora warmstart, data conflict |
| v13 | 64 | — | 71.6% | 100% | FAIL | Classifier fixed OOC permanently |
| v14 | 128 | — | 83.2% | 90% | PASS | v11-lora warmstart, lr=2e-5, 3811 pairs — best ever, beats v8 82.1% |

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

## RAG Retrieval History (2026-07-05)

Three-step fix applied this session:

1. Cosine normalization (59a2177)
   - Raw dot-product was giving high-norm vectors unfair advantage
   - Fix: normalize all embeddings before scoring

2. Noise drop (9f91b79)
   - 26 Swahili-only bare citations and exemption facts were outranking English
     value facts for every Swahili query
   - Fix: exclude legal citations, act references, exemption categories,
     signatory facts from the embedded index
   - Index: 232 → 206 facts

3. Concise bilingual facts (9f91b79)
   - 90% of value facts were English-only; Swahili queries matched Swahili
     noise instead of correct English facts (GN487A 10M was rank 18)
   - Fix: high-stakes facts rewritten as short Swahili-dominant strings
     with value in both Swahili words and TZS digits; no trailing bare
     domains (trailing domains were feeding URL hallucination)
   - Result: GN487A 10M → rank 1, SDL 3.5% → rank 1, NSSF 10% → rank 1

Final verified state (endpoint test 2026-07-05):
- GN487A non-citizen penalty: TZS 10,000,000 ✅ (was 5M dangerous)
- SDL rate: 3.5% ✅
- BRELA annual return: TZS 22,000 ✅
- VAT withholding services: 6% ✅
- NSSF employer: 10% ✅
- URL hallucination (brelautang.org): GONE ✅
- Token mashing (mgenimgeni, go.tzsijui): GONE ✅

Known remaining issues (model-generation, not RAG):
- Minor Swahili typos: TZSh, asilimai, mweka juu
- VAT cites wrong year (2024 instead of 2025)
- These are v14 8B model limits — addressed by frontier API path not RAG tuning

OSHA domain hallucination fix (607a923):
- Q9 OSHA question hallucinated OSHAnz.org (New Zealand OSHA)
- Fix: added domain-free OSHA concise facts (osha_registration_threshold_b004,
  OSHA_annual_inspection) — now cites osha.go.tz correctly
- Also removed dead concise key nssf_employee_rate (not in locked_facts)

## Known Limitations (architectural, not fixable by RAG tuning)

SDL combined-query threshold:
- Simple query 'SDL threshold ni wafanyakazi wangapi?' → RAG retrieves correct fact at rank 1 ✅
- Combined query mixing rate + threshold + comparison → generic percentage facts rank higher
- Model falls back to parametric belief of '11 employees' (incorrect — correct is 10)
- Root cause: 384-dim multilingual embedding cannot decompose multi-part Swahili queries
- Fix path: stronger embedder (intfloat/multilingual-e5-base) OR query decomposition
  before retrieval OR frontier API model — NOT more concise fact tuning (proven twice)

### Parametric memory override — v14 resists RAG correction on memorized strings

Two confirmed cases where v14's memorized values override correct RAG-injected facts:

1. SDL combined-query threshold
   - Model says 11 employees (wrong) even when correct fact (10+) is in context
   - Correct for simple queries, fails when mixed with rate/comparison

2. NSSF URL
   - Model outputs nssf.or.tz even when RAG explicitly injects nssf.go.tz
   - RAG can override numerical values (WCF 0.5% proved this)
   - RAG cannot override deeply memorized string tokens in 8B weights

Pattern: RAG reliably corrects number hallucinations (WCF 1M→0.5%, GN487A 5M→10M)
but cannot reliably correct memorized string tokens (URLs, thresholds stored as text).

Fix path: frontier API model (Claude Sonnet / Gemini Flash) — larger models do not
have this parametric override problem because their memorized URLs are more accurate
and their instruction-following is stronger.

## Current Production State (2026-07-05)

- Modal serving: africa-giants-adapter-v14 + inference-time OOC classifier
- RAG: 206 facts, cosine similarity, concise bilingual high-stakes facts
- Endpoint: https://prosperpiusmbaruku007--chike-inference-web-endpoint.modal.run
- WhatsApp: +255637809070 via Wappfly → Railway → Modal
- Gate scores: v14 in-corpus 83.2%, OOC 90% (classifier)
- Best ever: 83.2% in-corpus (beats v8's 82.1%)
- Cerebrium: UNPAID ($20.81) — inactive, superseded by Modal

## Known Issues / Next Session Priorities

1. Hand-coded pairs (50 pairs targeting specific eval failures) — not yet done
   See: data/reviewed/hand_coded_batch_015.jsonl (may be empty or incomplete)
2. v14 minor generation quality (typos, wrong year) — model-level, needs either:
   a. More targeted training pairs in Chike's exact answer style
   b. Switch to frontier API model (Claude Sonnet / Gemini Flash via OpenRouter)
3. 1,129 pending fact candidates — review session needed
4. Cerebrium $20.81 bill — pay or formally close account
5. zuck30 lightweight offline Chike discussion — still pending

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
