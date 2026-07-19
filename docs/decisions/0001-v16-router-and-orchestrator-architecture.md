# ADR 0001 — v16 Orchestrator: router, extraction, and decompose/merge architecture

- **Status:** Accepted (2026-07-20). Phase 0 bake-off pending a corrected test distribution (see §7).
- **Deciders:** Founder + Claude Code (architecture review session, 2026-07-20).
- **Supersedes:** the original 5-phase "fix v16's router" plan (embedding fast-path + LLM fallback).
- **Related:** PROGRESS.md "v16-READINESS BASELINE" (2026-07-20); the 20-question real-weights
  A/B (`scratch/v16_ab_test.py`, gate weights, commit 2208931).

## 1. Context

The v16 `Orchestrator` (`chike/orchestrator.py`) was tested end-to-end for the first time
against **live production weights** using 20 natural-Swahili questions that deliberately name
no law/agency/tax. Result: v15 ≥ v16 on 18/20, v16 won 0 of 4 compute questions, and produced
3 failure modes v15 does not have (empty output, hallucinated extra turns, self-contradictory
math). The dominant cause was that v16's `route()` sends a sub-question to the deterministic
rules engine only on a **literal** tax-name keyword (`sdl`/`nssf`/`paye`/`wcf`) + a digit, so
all 20 routed to `fact` and the compute path — v16's reason to exist — never fired.

A 5-phase remediation plan was proposed: (1) an embedding-based fast-path router reusing the
e5 fact index, (2) a qwen3-32b/OpenRouter LLM fallback for low-confidence cases, (3) extraction
fixes, (4) output-governance parity, (5) re-gate. This ADR records the architecture review of
that plan, its rejection, and the adopted counter-proposal.

## 2. Findings from investigating the actual code

**Finding 1 — cleaning is already at parity (Phase 4's premise is largely false).**
`Orchestrator._validate_and_clean` (`orchestrator.py:253`) calls
`generation_cleanup.clean_reply`. v15's `run()` calls the *same* function
(`chike-inference/modal_app.py:524`). Same `_is_fabricated_block`,
`_truncate_repeated_sentences`, domain fixes. There is no meaningful cleaning gap to close.

**Finding 2 — the real regression cause is an architectural divergence in how decomposition is used.**
- **v15** (`modal_app.py:434-524`): decompose → retrieve facts per sub-query → **merge all facts**
  (dedup, cap 9) → build **one** prompt on the **whole original message** → **generate once** → clean.
- **v16** (`orchestrator.py:283-285`, `_answer_fact:211-215`): decompose → for **each**
  sub-question independently retrieve → prompt → **generate** → clean → **concatenate the texts**.

v16 answers fragments in isolation and glues them together. This directly caused the two
v16-unique regressions: Q1 went empty (two junk-retrieval fragments each generated empty →
`"\n\n".join(["",""])`), and Q12 hallucinated extra Q&A turns (a bare fragment invited a ramble;
`clean_reply` checks per `\n\n` block, so a fabricated question in one block and its answer in
the next slips through). v15 never split the generation, so neither occurred. **This structure,
not cleaning, is the real "governance gap."**

**Finding 3 — `classify()` is a third stub the plan ignored.**
`Orchestrator.classify` (`orchestrator.py:154`) uses 8 `DEFAULT_OOC_PHRASES`; production
`classify_question` uses the config's **53** `ooc_phrases` (`kaggle/chike_config.json`).
Gate 2 (>70% correct refusal) and the 15 `out_of_corpus_refusal` gate questions would ride on
the 8-phrase stub.

## 3. Decision — reject Phase 1 (embedding router) and Phase 2 (LLM fallback)

**Phase 1 (embedding subdomain router) rejected because:**
- **It conflates fact-retrieval with intent-classification.** e5 encodes topical/lexical
  similarity; compute-vs-fact is orthogonal to topic. *"Kiwango cha SDL ni kiasi gani?"* (fact)
  and *"Nihesabie SDL yangu"* (compute) embed close together yet route differently. Embedding
  similarity is structurally blind to the boundary that matters.
- **An 11–12-way subdomain classifier is redundant with RAG.** 7–8 of those subdomains all
  funnel to the same fact→RAG path, and RAG already selects subdomain-appropriate facts. The
  only routing decision the engine needs is narrow: which of {sdl, nssf, paye, wcf} — or none.
- **It introduces a worse failure mode than the honest keyword stub.** The stub fails honestly
  (no keyword → fact → RAG → an answer). A thresholded embedding router that misfires to compute
  hands the question to `SlotExtractor`, whose never-guess contract (`extraction.py:200`) returns
  **clarification** — so a fact question misroutes into *"tell me your salary."* False-confidence
  misrouting on the fact path is a regression the stub cannot produce.

**Phase 2 (qwen3-32b/OpenRouter fallback on the serving path) rejected because:**
- **Cost/latency compounds.** A compute sub-question already costs **two** model calls
  (`extraction.py:146` extract, then `orchestrator.py:208` answer). Adding embed + external LLM
  = ~4 round-trips/sub-question vs v15's one, ×N on compound messages — on a WhatsApp product
  whose thesis is low marginal cost/latency.
- **It puts a third-party dependency on the critical path.** The qwen-judge precedent was
  offline/batch. Online, every ambiguous message blocks on an external API with rate limits,
  variable latency, and availability risk from Tanzania.
- **qwen3-32b is non-deterministic at temp=0** (PROGRESS.md 2026-07-16): the same question would
  route differently across calls — irreproducible, un-gate-able production behavior.
- **"Below threshold" is an unvalidated hyperparameter** — no calibration set, no target
  precision/recall, no tuning plan; a silent-failure knob.

## 4. Decision — adopt the counter-proposal

**Phase 0 — Offline router bake-off** against labeled data (see §7 for the corrected
distribution). Decide with data whether any ML router is warranted before building one.

**Phase A — Fold routing into the extractor call we already pay for** (replaces Phases 1+2).
Extend `SlotExtractor`'s single model call to emit `{intent: sdl|nssf|paye|wcf|none, fields:{…}}`.
Routing + extraction from one call: no external LLM, no OpenRouter on the critical path.
Never-guess preserved: `intent=compute` + low-confidence fields → clarify; `intent=none` → fact.
Bound cost with a cheap high-precision lexical prefilter (has-a-number AND a payroll/tax cue) so
the extractor-router runs only on plausibly-compute questions; obvious pure-fact questions skip
straight to RAG as today.

**Phase B — Fix the decompose/merge divergence** (this is the real Phase 4). For an all-fact
sub-question set, adopt v15's shape (retrieve-for-all → generate once on the whole message).
Per-part generation only when parts have different routes (compute + fact mix). Add a merge-time
empty-output guard with whole-question fallback.

**Phase C — Bring `classify()` + the refusal path to parity** (load the 53 `ooc_phrases` from
config, as production does); include the 15 OOC questions in the re-gate.

**Phase D — Re-gate** exactly as the original Phase 5 required: re-run the exact 20-question A/B
**plus** the full 400-gate **through the real router**, requiring **v16 ≥ v15 on both raw and
reliable subsets**, with router-decision logging shipped as a first-class requirement.

Ordering: A, B, C are independent and low-risk — do them in parallel. The ML router
(embedding/LLM) is built **only if Phase 0 proves** the lexical + extractor-intent approach
cannot hit target precision, and if so it goes offline-first, never as a synchronous external
call on the serving path.

## 5. Consequences

- **Positive:** fewer serving round-trips than the rejected plan; no new external dependency on
  the request path; the routing decision is made where structured extraction already happens;
  the real regression cause (decompose/merge) is fixed rather than masked; OOC/refusal parity is
  explicitly restored; the whole approach is validated offline before code is written.
- **Negative / accepted trade-off:** Phase A adds a model call to *some* fact questions (those
  that pass the numeric+cue prefilter but turn out to be fact) — still far fewer round-trips than
  embed+LLM+extract+generate, and one fewer external dependency.
- **Unchanged bar:** v16 must not be wired into Modal until Phases A–B land and Phase D passes
  with v16 ≥ v15. This ADR does not lower that gate.

## 6. Status of each stub (for future readers)

| Stage | Current state | Target |
|-------|---------------|--------|
| `classify()` | stub, 8 OOC phrases | Phase C — 53-phrase parity |
| `route()` | keyword+digit literal match | Phase A — extractor-emitted intent |
| `SlotExtractor` | real logic; not exercised by route() on natural phrasing | Phase A — real-phrasing + intent |
| decompose→generate→merge | per-part generate + concatenate | Phase B — v15 retrieve-all/generate-once for all-fact |
| `_validate_and_clean` | already at v15 parity (`clean_reply`) | no change needed |

## 7. Phase 0 methodology correction — the 400-question set is the WRONG test distribution

Before running the bake-off, the archived gate set was profiled. **The 400-question set is
keyword-explicit on the compute side and cannot validate a router for natural traffic:**

- **All 113 compute questions (100%) literally name their tax** (sdl/nssf/paye/wcf). 0 require
  inference.
- On this set the **current keyword+digit stub scores 100% compute recall and 0% false
  positives** — a *perfect* score — **while we already know from the 20-question real-weights
  test that the same stub routes 0/4 natural compute questions correctly.**

A bake-off here would hand the keyword router a perfect score and produce false confidence in
exactly the approach the 20-question test just disproved — the same mistake, repeated. Phase 0
as originally scoped is therefore not merely unhelpful but actively misleading.

**Correction (required before Phase 0 runs):** the bake-off must be scored against a
**natural-phrasing routing set** written under the same "name no subdomain/law/agency"
discipline as the 20-question test, with known compute/fact ground truth. The 20 already-tested
questions contribute only 4 compute cases — too few — so a purpose-built natural routing eval
(target ~40–60 questions, balanced compute/fact, no tax-naming) is needed, with the 400 keyword
set retained only as a *no-regression* control (a candidate must not lose the easy cases either).
The decision-relevant metric is precision/recall on the **natural** set. This correction is
itself an instance of the ADR's own thesis: validate against the distribution real users
produce, not the one the router is trained to match.
