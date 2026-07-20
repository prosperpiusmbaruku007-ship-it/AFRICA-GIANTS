# Africa Giants — Project Progress

Last updated: 2026-07-20

**STANDING STATUS:** EOS harness fix (build_chat_prompt → apply_chat_template) — **CLOSED,
RE-BASELINED, and VALIDATED at scale.** The corrected 400-question combined regression is
IN (commit e9cc68a, persisted to `eval/results/gate_orchestrator_combined_e9cc68a.json`) —
**the first fully clean, trustworthy full-scale gate run this project has had.** EOS fix
confirmed broad-based (0 loops / 0 header-leakage / 0 empty across 400; ~3× runtime).
eval_317/146 **resolved**; eval_213/355/155 are **genuine defects the corrected harness
newly exposed** (NOT harness noise); eval_332/365 **reclassified as scorer artifacts**.
Retrieval-layer prohibition-inversion fix — CLOSED and VALIDATED (d92e63f). Reporting-layer
negated-lazima lexicon fix shipped (cec8fae). **Compute buckets (32–40%) are scorer-limited,
not a confirmed measure of true compute accuracy** — closing that gap needs the
frontier-judge scoring approach, not more prompt/retrieval work. NEW convention: every gate
run is committed to `eval/results/` (see below). Next: eval_213 faithfulness defect +
frontier-judge compute scoring + framing-aware polarity.

## v16 router architecture — ADR 0001 (see docs/decisions/0001-v16-router-and-orchestrator-architecture.md)

The v16 router/orchestrator remediation is governed by **ADR 0001** (do not duplicate here — read it):
- Original embedding-router + LLM-fallback plan REJECTED; extractor-intent counter-proposal adopted.
- **Phase 0 bake-off DECIDED (2026-07-20):** on the 50-question natural routing set, the embedding
  router (Candidate B) **misrouted 2 OOC questions (capital-gains, mining-royalty) into compute** —
  empirically confirming the ADR's key safety objection — and was boundary-blind (3/8). Candidate C
  (lexical-prefilter + extractor-intent) won: precision 1.0, 8/8 boundary pairs, 0 OOC misroutes.
- **Phase A foundation:** lexical prefilter as a recall-biased invoke-gate → extractor emits
  `{intent, fields}` in its existing single call → never-guess preserved. No new model on the
  serving path; OOC stays with `classify()`. Test artifact: `eval/router_eval/router_natural_eval_001.jsonl`.
- **Phases A, B, C IMPLEMENTED (2026-07-20)** — see ADR §9. A: deterministic router + backstop
  (`592f0d2`). B: route-aware merge fixes the decompose/generate/concatenate divergence, closing
  the Q1/Q12 regressions (`72b3cbe`). C: unified OOC classification into shared
  `chike/classification.py`, closing Finding 3 (`f55f0cf`). Offline suite: **167 passed, 2 skipped**
  (the 2 skips are the Phase D GPU pair).
- **Phase D REMAINING (GPU, BLOCKING before any production wiring)** — see ADR §10: un-skip the 2
  GPU tests, re-run the 20-question A/B and the full 400-gate through the corrected system,
  require **v16 ≥ v15 on both**. Also resolves the deferred AND-vs-OR invoke-gate cost lever.

## v16-READINESS BASELINE — first real-weights, natural-phrasing A/B vs v15 (2026-07-20) — BLOCKING

**The single most methodologically important test of this session.** 20 questions written in
natural Swahili that deliberately name NO law/agency/tax type (compute, prohibition, boundary,
ambiguous, and evasion framings), run end-to-end against the **live production weights** twice:
v15 via the real `web_endpoint` (full pipeline as users receive it) and v16 via
`Orchestrator(LocalAdapter → generate_endpoint)` — same weights, same RAG index, real Modal
inference, **0 errors / 0 timeouts** across all 40 calls. Harness: `scratch/v16_ab_test.py`;
raw data `scratch/v16_ab_test_result.json` (gitignored scratch).

### Verdict: v16 is a REGRESSION against v15, NOT an upgrade — do not wire into production
- **v15 ≥ v16 on 18/20** (both correct 9; both wrong 2; v15 strictly better 7; v16 strictly better 2).
- **v16 wins 0 of the 4 compute questions** (Q2, Q5, Q8, Q15). It did not produce a single
  correct authoritative arithmetic answer; on Q5/Q15 its model-generated math was
  self-contradictory (Q5 "14% × 7,200,000 = 1,440,000" — false; Q15 a nonsensical
  "11 × 400,000 + 10 × 600,000 = 8,900,000" that doesn't even self-consist).
- **3 v16-UNIQUE regressions** absent from v15: (1) Q1 **empty answer** (`"\n\n"`);
  (2) Q12 **hallucinated two extra Q&A turns** the user never asked; (3) self-contradictory
  arithmetic justifications (Q5/Q15) surfaced by the raw endpoint's ungoverned generation.
- Both systems correctly refused **every** evasion attempt (Q6/14/17/18/19/20 — no
  evasion-acceptance in either) — but that comes from the SHARED model+RAG, not from anything
  v16 adds.

### ROOT CAUSE — the router never inferred subdomain; compute path fired 0/20
v16's `route()` (`chike/orchestrator.py:174`) routes to the deterministic rules engine only on
a **literal** tax-name keyword (`sdl`/`nssf`/`paye`/`wcf`) + a digit. Because the 20 questions
name no tax, **all 20 routed to `fact`** — the deterministic engine (v16's entire reason to
exist) was UNREACHABLE, the never-guess clarification guard never triggered
(`has_clarification_sentinel` false 20/20, even on Q2/Q5/Q15 where salaries were missing/
ambiguous), and v16's "authoritative arithmetic" was in fact model arithmetic
(`computation: null` on all 20). v16's router adds **no** subdomain-inference over the shared
RAG+model layer, which is identical to v15.

### The route() gap is BIDIRECTIONAL — and this exposes a gap in THIS SESSION's own methodology
This connects directly to the earlier-session route() keyword-gap findings (the "ROUTING
FINDING", ~line 885, and the RC-5 tracked follow-up + `ct=None` wrong-base guard work, ~lines
848/784/833). Those documented the router pulling fact/BRELA/VAT questions that merely CONTAIN
a payroll figure INTO the compute path incorrectly (the "wrong-base" misroutes — extract_078
"laki nne … BRELA?", extract_205 "payroll milioni tano … nisajili VAT?", ~21 flagged, patched
via the wrong-base guard). **This test proves the gap runs the OTHER way too:** the router also
fails to send genuine, naturally-phrased compute questions INTO the compute path. The failure
is bidirectional — misrouting fact→compute AND failing to route compute→compute.

Consequence for our own numbers: **every prior gate score claiming v16 "fact-path parity" or
"compute-path validated" was measured on a question set that structurally avoided ever
stress-testing the router on natural phrasing.** The fact-path-parity runs held `route()` fixed
and compared the 190 fact-bucket questions (all still routed to fact); the compute-path
validation called `SlotExtractor` DIRECTLY, bypassing `route()` entirely (see ~line 887). So no
prior test ever exercised the router on questions that (a) are compute in intent but (b) don't
name the tax — i.e. exactly how real users ask. This is a real gap in the session's testing
methodology, not merely a v16 defect, and must be stated as such: our headline v16 numbers were
measured around the router, never through it.

### SEPARATE, ADDITIONAL BLOCKER — the raw-endpoint governance gap
Independent of routing: v16's Orchestrator calls `generate_endpoint` (raw tokenize→generate→
decode) directly via `LocalAdapter`, and `_validate_and_clean` is currently stop/clean only.
The raw endpoint's ungoverned output is what produced the Q1 empty answer, the Q12 hallucinated
extra turns, and the self-contradictory math — failure modes v15's integrated pipeline
suppresses. **Even after the router is fixed, whatever calls the raw endpoint directly needs at
least v15's level of output cleaning/validation, or these same failure modes will surface on
legitimate compute-routed answers once the router actually starts sending traffic there.** This
is a distinct problem from the router and must be fixed on its own track.

### BLOCKING path to production-readiness (dependency-ordered — v16 must NOT be wired into Modal until 1–2 land and 4 passes)
1. **Replace the router stub with real subdomain/intent inference** (classifier or LLM router)
   so naturally-phrased compute questions reach the rules engine. Nothing else matters until
   this lands. Gate: these 20 (and the broader set) route compute questions to `compute`.
2. **Make the slot extractor resolve real-world phrasing** — per-person × count
   ("wengine kumi … laki sita kila mmoja"), currency conversion (Q8 KES→TZS), and FIRE the
   never-guess clarification when salaries are missing (Q2/Q5). Gate: deterministic trace on
   Q5/Q15 matches the correct figures (Q15 payroll 6,400,000 / SDL 224,000, etc.).
3. **Fix decompose→generate→clean** to eliminate empty output (Q1) and hallucinated extra
   turns (Q12): `_validate_and_clean` must reach at least v15's robustness + a non-empty guard.
   (This is the governance-gap track above.)
4. **Re-run THIS EXACT A/B plus the full 400-gate THROUGH the real router**, and require
   **v16 ≥ v15 on both raw correctness and the reliable subset** before any production wiring.
   The bar is not "v16 works" — it is "v16 beats the system already serving users."

Until at least steps 1–2 land and step 4 passes, wiring v16 into Modal would degrade the live
product. Keep v15 in production; treat this entry as the concrete spec for what the
orchestrator's stub stages (`route`/`classify`/`validate`) must become.

## EOS/generation 'root cause' — CORRECTED with direct evidence (2026-07-18)

Direct A/B test (kaggle/eos_production_probe.py, commit 6d21253, 20 questions
across 20 subdomains, skip_special_tokens=False, no substring stopping criteria
so only real EOS emission could stop generation):

- PRODUCTION format (modal_app.py's apply_chat_template, matches training):
  20/20 stopped early, 20/20 emitted <|end_of_text|> (128001), mean 68 tokens.
- EVAL/ORCHESTRATOR format (chike/prompting.build_chat_prompt, hardcoded
  Llama-3 headers never used in training): 0/20 stopped early, 0/20 emitted
  EOS, 20/20 ran to the full 350-token cap.

CONFIRMED: the earlier '79% of all generations never stop, project-wide'
framing was WRONG. Production has never had this defect — it uses a prompt
format matching training, and the model reliably emits its stop token.
This was entirely a testing-harness artifact: chike/prompting.build_chat_prompt
uses a Llama-3 chat-header format the model was never trained on, so at
eval/gate time only, the model doesn't recognize where to stop.

REAL IMPACT: every eval/gate score computed via the orchestrator path this
session (the 190/250/400-question combined regressions, Bucket A/B/C/D,
the retrieval-fix validation, the prohibition-inversion investigation, the
cleanup-layer gap-closure) was measured against a prompt format that does
NOT match production. This is a genuine R12 (dual-file-sync) violation in
the eval harness itself, not a defect in the deployed system.

FIX (no retraining needed): chike/prompting.build_chat_prompt and
kaggle/eval.py need to use apply_chat_template (matching modal_app.py
and training), not the hardcoded Llama-3 header format. Once fixed, the
existing cleanup-layer gap-closure fixes are likely to matter far less
(since correctly-stopped generations rarely need aggressive tail-trimming)
but should remain as defense-in-depth.

NEXT STEP: fix chike/prompting.build_chat_prompt to use apply_chat_template,
re-run the full 400-question combined regression on the corrected format,
and treat that as the new, trustworthy baseline — every prior gate score
this session should be considered measured on a flawed harness and superseded
once this is fixed and re-run.

### FIX IMPLEMENTED (2026-07-18) — awaiting Kaggle 400-run re-baseline

- `chike/prompting.build_chat_prompt(question, facts, system_prompt, tokenizer=None)`
  now routes through `tokenizer.apply_chat_template(..., add_generation_prompt=True)`
  over the SAME `[system, user]` messages modal_app.py builds (byte-identical to
  production and training). No-tokenizer callers (unit tests) get a naive-concat
  fallback — system + blank line + question — deliberately NOT the untrained header
  tokens.
- `kaggle/eval.py` (`generate_answer`) now passes its loaded `tokenizer` to
  build_chat_prompt → the standalone gate now tokenizes the exact production prompt.
- `chike/orchestrator.py` passes `getattr(self.backend, 'tokenizer', None)` through
  `_build_fact_prompt` / `_build_compute_prompt`; `KaggleDirectBackend` exposes
  `.tokenizer`, so the combined-orchestrator gate uses apply_chat_template too.
- Tests updated to the corrected behavior (test_prompting.py, test_orchestrator.py);
  full local suite **140 passed**. Offline verification: fallback emits no header
  tokens; tokenizer path delegates to apply_chat_template with modal_app-identical
  messages.
- **PENDING (founder, Kaggle GPU): re-run the full 400-question combined regression on
  the corrected format. That will be the FIRST trustworthy full-scale gate score this
  project has had** — every prior score was measured on the mismatched format and is
  superseded once this lands. → **DONE 2026-07-19 (see FINAL summary below).**

## ✅ FAITHFULNESS + FACT-INDEX CYCLE — FINAL VERDICT (2026-07-20, gate-measured)

**Status: net-positive cycle, closed on full 400-gate data — NOT a clean single-shot win.**
The eval_213 faithfulness fix required three fact-index rounds and surfaced a real regression
along the way; the final measured result is a net improvement, with two documented scorer
artifacts and one latent (not-yet-costly) fragility carried on a watchlist. Honest full arc:

### 1. The eval_213 discovery + fix (2×2 collocation isolation)
The facilitator-penalty fact was retrieved at **rank 0** yet the model answered wrong ("only
non-citizens are punished") — a **faithfulness/grounding defect, not a retrieval gap** (the
initial retrieval-gap hypothesis was REFUTED by pulling the actual retrieved context — the
discipline that prevented shipping a wrong "fixed" status). A systematic **2×2 (verb × object)
factorial** (`faithfulness_leseni_probes.jsonl`) isolated it to the single `kukopesha + leseni`
collocation — swapping either the verb or the object alone eliminates it. A phrase-level
parametric-prior override, not a general defect.

### 2. The two-round (actually three-round) fact-index iteration this fix required
- **v1** `gn487a_license_lending_is_facilitation`: over-matched — displaced
  `gn487a_prohibited_activity_3` from the phone-repair query (**caught by the regen gate**).
  Root cause of THAT was activity_3 being English-only/weakly-grounded; fixed by
  Swahili-strengthening activity_3 rather than shrinking the new fact further.
- **v2** (narrowed) + adding `gn487a_marriage_no_exemption` (Swahili) to fix eval_175: the
  **marriage addition then caused two regressions**, found only on the full 400-gate at 19fce68 —
  **eval_380** (non-citizen minimum penalty answered **TZS 5M instead of 10M** — a wrong number)
  and **eval_175** (marriage answer degraded to a vague deflection). Retrieval-rank evidence
  showed the 10M fact was never outranked (rank 0); the v2 license fact's residual `5,000,000`
  tail put a **second 5M figure** into eval_380's top-3 — a **context-composition** failure.
- **v3** (commit 2448c14 → index 0939eef): dropped the penalty-amount tail from the license
  fact (kept the `kukopesha+leseni` collocation so eval_213 stays fixed) and Swahili-grounded
  the marriage fact so it wins its own query. Added two regen guards (marriage positive;
  eval_380 disambiguation: 10M present AND license fact absent from top-3).

### 3. Probe-vs-gate discipline caught and correctly triaged every issue
- **Stale "Linux-environment / os.path.join" Modal theory** — diagnosed as wrong and RETRACTED;
  real cause was a Windows console-encoding crash on Modal CLI output (`PYTHONUTF8=1`).
- **Unpushed-commit stale fetch** — the fetched-HEAD tripwire caught it; it was NOT a CDN delay
  (origin genuinely was two commits behind because the commits were never pushed).
- **Two probe-harness bugs** (stale target strings): fp_04 searched English `"marriage no
  exemption"` against a now-Swahili fact; fp_02 was tied to one exact phrase the marriage fact
  crowded out — both were false `retrieval_gap`s while the model answered correctly. Fixed the
  matcher (string-or-list) + verified offline against real `facts_seen`.
- **fp_05 fragility** — a genuine confident-wrong flip at probe level (passive-shareholding
  "yes" flipped to "no" by prohibition-heavy context), attributed deterministically
  (`do_sample=False`) to the marriage fact entering its top-3. Carried to the watchlist.

### 4. Final measured result — full 400-gate, v3 (7eb9226) vs 19fce68
- **Net +2 raw pass; +4 reliable-subset with ZERO reliable losses.** All 4 gains
  (`eval_380`, `eval_175`, `eval_069`, `eval_163`) are `reliable=True`; eval_069/eval_163 were
  19fce68 regressions now **recovered**. `eval_144` upgraded rambling→clean **reliable** pass.
- **eval_213 / eval_380 / eval_175 all confirmed fixed** on real generated text (eval_380 now
  "TZS 10,000,000"; eval_175 nails marriage≠citizenship/exemption).
- **fact_path reliable-subset 108→111/130 = 85.4%** — above the 85% threshold AND slightly
  above the pre-cycle baseline (e9cc68a 110/129 = 85.3%), with the faithfulness fix baked in.
  Buckets: A ▲ (raw 85.1→86.2%, reliable ▲), D reliable ▲ (53.7→54.9%), B/C flat.
- **The two losses are unreliable-subset scorer artifacts, not defects** — see (a) below.
- **The predicted fp_05 crowding cost did NOT materialize on the gate:** shareholder-carveout
  gate Qs (eval_173/eval_204) and all 6 facilitator-displaced Qs held pass.
- Archived: `eval/results/gate_orchestrator_combined_7eb9226.json` (predecessor `_19fce68.json`).

### (a) Logged as scorer-artifact / temporal items — NOT defects requiring a fix
- **eval_157** (gn487a definition): both runs enumerate the 15 activities; v3 reformatted to a
  numbered list and the overlap scorer scored it lower → `morphological_overlap_gap`, dropped to
  `reliable=False`. Formatting + scorer-lexical artifact.
- **eval_369** (gn487a yes_no, temporal retroactivity): `reliable=False` in BOTH runs
  (`yes_no_polarity_unverifiable`). Not the fp_05 class (opposite direction — a yes-applies case
  where the model over-hedged toward a spurious grandfathering carve-out). Pass→fail is a
  scorer-boundary flip between two flawed answers on an already-unreliable case. Candidate future
  locked-fact ("GN487A applies from 28 Jul 2025 regardless of business start date; no
  grandfathering") but does not touch the trustworthy gate.

### (b) STANDING WATCHLIST — check on any future gate run or fact-index change (not urgent)
1. **fp_05-class carve-out fragility.** GN487A "permitted/yes" carve-out questions (passive
   shareholding, etc.) sitting on English-only facts can be flipped negative by prohibition-heavy
   Swahili context. Real at probe level; NOT yet costing reliable-gate accuracy. If a future gate
   shows eval_173/eval_204 or similar carve-out Qs regressing, escalate.
2. **English-only GN487A fact batch** (the ~15 `gn487a_prohibited_activity_*` + remaining
   carve-outs) — still weakly grounded for Swahili queries; queued from earlier this session (see
   TRACKED SYSTEMIC GAP below). The 26-question gn487a top-3 crowding is real in retrieval space
   but not currently costing accuracy at the present top-k.

### (c) STRUCTURAL GN487A decision — deliberate future work, NOT reactive
Raise injected top-k for GN487A vs. a single consolidated GN487A rewrite (fewer, well-scoped,
all-Swahili facts with a designed layout + a standing carve-out guard set). The measured gate
says this is **not urgent** — decide deliberately with the watchlist data, not reactively.

---



> This section declared closure on 2026-07-19 based on a 14-case probe regression, BEFORE
> the full 400-gate revealed the marriage-fact addition had caused eval_380/eval_175
> regressions. It is retained for the audit trail but is SUPERSEDED by the FINAL VERDICT
> section above (v3 fix + measured gate result). In particular, the "ACCEPTED low-severity
> fp_04 trade-off" below was later CORRECTED: eval_175 did carry a real, measured gate cost.

The eval_213 faithfulness cycle (interim summary for the record):

- **eval_213 discovered:** the facilitator-penalty fact was retrieved correctly (rank 0) yet
  the model still answered wrong ("only non-citizens are punished") — a faithfulness/grounding
  defect, NOT a retrieval gap (refuted the initial retrieval-gap hypothesis by pulling the
  actual retrieved context).
- **Root-caused as NARROW** via a systematic 2×2 (verb × object) isolation probe
  (`faithfulness_leseni_probes.jsonl`): only the specific `kukopesha + leseni` collocation
  triggers it; swapping either the verb or the object alone eliminates it. Not a general
  faithfulness defect — a phrase-level parametric-prior override.
- **Fix:** targeted `gn487a_license_lending_is_facilitation` locked fact, iterated twice —
  v1 over-matched and displaced `gn487a_prohibited_activity_3` (caught by the regen gate);
  root cause of THAT was the activity fact being English-only/weakly-grounded, fixed by
  Swahili-strengthening the activity fact rather than further shrinking the new fact.
- **Regen verified clean** on all 15 critical queries + 2 new guards (License lending,
  Phone repair); committed to `chike-inference/` + `kaggle/` with byte-identical sha256.
- **Modal redeployed** successfully from Windows — after an INCORRECT "Linux environment /
  os.path.join breaks container paths" theory was diagnosed and RETRACTED; the real cause was
  a Windows console-encoding crash on Modal CLI's `✓` output, fixed with `PYTHONUTF8=1`
  (container recomputes paths on Linux, so host OS is irrelevant to runtime paths).
- **Full 14-case regression (commit 403da7a):** fp_01/lv_01 both flipped
  `faithfulness_failure → faithful`; all other 12 hold `faithful`; both control pairs pass;
  ZERO new faithfulness_failure; ZERO wrong answers introduced.

### Accepted low-severity side effect — fp_04 marriage-fact displacement

fp_04 (`Nimeoa mwanamke Mtanzania, je nasamehewa katazo la GN487A?`) moved
`faithful → retrieval_gap`: `gn487a_marriage_no_exemption` was pushed from rank 2 to **rank 3**
(one slot outside top-3) by the license-lending fact at rank 1. Reproducible (retrieval is
deterministic), borderline (single-position slip). The model still answered **correctly and
confidently** from a strong, correct parametric prior ("Hapana — ndoa haikupi msamaha...").
Blast-radius check (marriage-exemption gate questions): **eval_204 unaffected** (marriage fact
still rank 0); **eval_175** marginally displaced by this fix (rank 5, both new facts in top-3);
**eval_144** rank 5 but its top-3 contains NO new facts → **pre-existing** English-only weakness,
NOT caused by this fix. All 4 gate questions passed pre-fix (reliable) and answer correctly.
**Decision: ACCEPTED as a low-severity retrieval-hygiene trade-off** (zero answer-quality
impact; the net win of resolving the dangerous eval_213-class defect dominates; a one-off regen
now to move a rank-3 fact would risk repeating the exact displacement just resolved).
`gn487a_marriage_no_exemption` is QUEUED by name in the systemic English-only batch below.

## TRACKED SYSTEMIC GAP — English-only GN487A facts are weakly grounded for Swahili queries (2026-07-19)

Surfaced while fixing the lv_01 license-lending fact's regen over-match. The 15 prohibited-
activity facts `gn487a_prohibited_activity_1..15` — AND `gn487a_marriage_no_exemption` —
have NO `CONCISE_BILINGUAL_FACTS` entry; they fall back to the English `key: value` form
(e.g. "gn487a prohibited activity 3: Prohibited activity 3: Repair of mobile phones and
electronic devices"). A Swahili query like `Mgeni anaweza kutengeneza simu?` or `Nimeoa
mwanamke Mtanzania, je nasamehewa...?` shares ZERO distinctive surface tokens with the
English text (only `gn487a`) and matches only cross-lingually — a weak, ERRATIC e5 signal
(the marriage fact ranks 0 for one phrasing, 5 for another). These facts were only *luckily*
top-ranked before, absent a strong Swahili GN487A-domain competitor in the index.

**Structural risk:** ANY future Swahili-dense GN487A fact added to the index can displace a
weakly-grounded English-only fact from top-3 for its own query — not a one-off caused by the
license-lending fact specifically. Confirmed twice: the license-lending fact displaced
activity 3 from the phone-repair query (fixed by Swahili-grounding activity 3), and displaced
`gn487a_marriage_no_exemption` from fp_04's top-3 (accepted low-severity — see below).

**Fixed so far:** only `gn487a_prohibited_activity_3` (Swahili CONCISE added — it has the
'Phone repair activity' regen guard, so the fix is verifiable).

**QUEUED for the guarded batch (English-only, still weakly grounded):**
`gn487a_prohibited_activity_1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15` (14 activities)
+ `gn487a_marriage_no_exemption`.

**Recommended follow-up (dedicated, guarded batch — do NOT bulk-edit unverified):** for each
queued fact, add a Swahili-first CONCISE entry AND a matching `critical_queries` regen-guard
query, following the exact verify-before-commit discipline used for activity 3 — one fact (or
a small guarded group) at a time, each confirmed by the regen gate before the next. A bulk
unguarded Swahili rewrite is explicitly rejected: only activity 3 currently has a guard, so
the rest would ship less-verified.

## eval_183 RECLASSIFIED — locked_facts coverage gap, NOT a faithfulness defect (2026-07-19)

While designing the eval_213 faithfulness probe, local retrieval on eval_183's phrasing
("Mwajiri asiyesajili OSHA anaweza kufungiwa biashara yake?") showed **no fact stating OSHA
lacks direct business-closure authority exists in the 210-fact index** — the closest facts
are the OSHA penalty list (fine TZS 1–5M / imprisonment) and the GN487A closure distinction.
So the model was NOT overriding a retrieved fact; it filled a genuine coverage gap with a
wrong assumption (asserting a stop-work power). This is the **same class as eval_155** (a
locked_facts clarity/coverage issue), NOT a model faithfulness defect. **Fix target: add an
'OSHA has no direct business-closure authority; enforcement is fine/imprisonment' fact to
locked_facts.json** (then the R15 RAG-regen cycle) — a fact-base addition, not a prompt or
generation change. Batched with eval_155 for a dedicated locked_facts pass (deferred, per
prioritization). This moves eval_183 OFF the faithfulness track it was tentatively on.

## ✅ EOS CYCLE CLOSED — corrected 400-run re-baseline is IN (2026-07-19)

The founder ran the full 400-question combined regression on the corrected format (commit
**e9cc68a**, timestamp 2026-07-18T20:34Z). Persisted data:
`eval/results/gate_orchestrator_combined_e9cc68a.json` (fetched from HF and committed — see
standing convention below). This is the FIRST fully clean, trustworthy full-scale gate run
this project has had; every prior score was on the mismatched harness and is superseded.

**EOS fix confirmed broad-based (not concentrated in a few questions).** Across all 400
generations: **0** with a repetition-loop tail, **0** with `<|start_header_id|>`/
`<|begin_of_text|>` header-token leakage, **0** empty generations. Mean 229.8 chars, median
187, p90 469 (char proxy — no token-count field was persisted, but the loop/header/empty
counts are exact). Runtime dropped ~3× (13,300s → 4,861s), fully explained by clean early-
stop instead of runs hitting the 350-token cap. The probe's 20/20 finding holds at scale.

**Bucket results (raw / reliable subset):**
- fact_path_190: 156/181 = 86.2% / 110/129 = 85.3%
- staged_50: 35/50 = 70.0% / 28/40 = 70.0%
- compute_type: 36/112 = 32.1% / 20/50 = 40.0% (genuine 35/108 = 32.4% / 19/49 = 38.8%)
- adversarial_150: 60/144 = 41.7% / 45/82 = 54.9%
- Weakest subdomains (all compute-heavy): wcf 1/10, sdl 29/67, paye 14/31, nssf 37/64.
  Strong: gn487a 48/54, efd 23/25, gn605a 5/5, vat_registration 40/54.

**Per-question findings vs. this session's claims:**
- **eval_317 & eval_146 — RESOLVED.** Both pass=True, reliable=True, clean single-shot
  generation, correct polarity, no repetition tail. The d92e63f retrieval fix (eval_317
  salon capital-distractor) held up under the corrected harness.
- **eval_213 — GENUINE NEW DEFECT** (gold=yes/model=no; opposite direction from every
  prior inversion). Clean generation, reliable=True. Model confidently claims only
  non-citizens are punished under GN 487A, contradicting the locked facilitator-penalty
  fact (Tanzanian facilitator: TZS 5M / 3 months). See dedicated section below — the
  RAG-gap hypothesis was **REFUTED**; it is a faithfulness defect.
- **eval_355 — GENUINE DEFECT.** Sales TZS 10,999,000 vs 11M EFD threshold; model says
  "Ndiyo, unazidi" (wrong — 10.999M < 11M). A boundary-comparison error.
- **eval_155 — GENUINE DEFECT.** Model says the GN 487A enforcement *exercise* is still
  ongoing; gold: the exercise ended 8 Oct 2025 though the law is permanent. Conflates the
  time-limited exercise with the standing law.
- **eval_332 — SCORER ARTIFACT.** Model actually correct (agrees wholesale prohibited,
  reproduces both penalties incl. the citizen-helper TZS 5M); "Ndiyo [prohibited]" vs gold
  "Hapana [you can't]" is a framing-polarity mismatch, not an error.
- **eval_365 — SCORER ARTIFACT.** pass=True, reliable=False; model correctly states NSSF
  has no employee threshold; surface "hakuna" flagged by the polarity classifier.
- eval_183 (OSHA stop-work-order vs. business-closure) is a genuine *semantic* nuance the
  polarity scorer can't separate — left with the deferred framing-aware polarity item.

**Compute buckets (32–40%) are SCORER-LIMITED, not a confirmed measure of true compute
accuracy.** 130/400 results are reliable=False, and every exclusion reason is a
scorer/ground-truth limitation — NONE is a generation-quality reason (0 truncated/loop/
empty). Breakdown: compute_derived_number 48, qualitative_number_no_numeric_key 27,
yes_no_polarity_unverifiable 26, yes_no_ground_truth_ambiguous 9, year_only_numeric_key 6,
morphological_overlap_gap 6, zero_or_not_applicable_answer 6, year_collision_match 2. On the
compute path specifically, 62/113 are unreliable (mostly compute_derived_number — the
number-overlap scorer cannot verify a computed figure). This means the reliable-subset
denominators are governed by scorer structure, not generation cleanliness (the EOS fix could
not have moved them). **Closing this gap requires the frontier-judge scoring approach already
validated earlier this session — NOT further prompt or retrieval work.** Until then, treat
the compute numbers as a floor obscured by scorer leniency/blindness, not a true accuracy.

## eval_213 — RAG-gap hypothesis REFUTED; it is a FAITHFULNESS defect (2026-07-19)

Investigated with the same rigor as the salon-inversion case, and the mechanism is the
OPPOSITE of what I first hypothesized. Ran the real e5 retriever (chike.retrieval, using the
committed, git-clean `kaggle/rag_embeddings.npy` + `rag_facts_text.json` — the exact 210-fact
index the e9cc68a Kaggle run used) on eval_213's exact phrasing:

  Q: "raia wa Tanzania anayekopesha leseni yake kwa mgeni naye anaadhibiwa chini ya GN 487A?"
  top_3[0] = "Adhabu kwa raia wa Tanzania anayemsaidia mgeni kukiuka GN487A: faini si zaidi
             ya TZS 5,000,000 ... au kifungo si zaidi ya miezi 3."  ← the facilitator fact,
             retrieved at the VERY TOP of context.

The facilitator-penalty fact is **present in eval_213's retrieved context at position [0]**,
yet the model still answered "Hapana — adhabu zinawahusu tu wasio raia." So this is **NOT a
retrieval gap** — the model was handed the correct fact and contradicted it. The two-arm
hybrid retrieval fix (d92e63f) does **NOT transfer**; confirming the mechanism first (per
the founder's instruction) prevented applying the wrong fix. eval_213 is a
**faithfulness/grounding defect** (model overrides a retrieved fact with a confident prior
that "GN 487A is about non-citizens, therefore only non-citizens are punished"). eval_332
corroborates: with the same fact retrieved, the model gets the citizen-helper penalty RIGHT
inside the wholesale multipart — so the failure is phrasing/prompt-conditioned generation,
not index coverage. TRACKED as a new priority finding; candidate remedies are
faithfulness-side (e.g. prompt instruction to defer to retrieved penalties, or a
polarity/consistency check against retrieved facts), NOT retrieval-side.

## Standing convention (2026-07-19): commit every gate run to eval/results/

The immediate-predecessor combined-gate run could not be diffed against because its
`gate_orchestrator_combined.json` lived only on HF and was overwritten by the e9cc68a run
(never committed). To prevent this recurring: **every `gate_orchestrator_combined.json` (and
standalone gate) run is fetched from HF and committed into `eval/results/` with a
commit-tagged filename**, e.g. `gate_orchestrator_combined_<sha>.json`. This gives each
future re-baseline a real, byte-exact predecessor for per-ID before/after diffs. First entry:
`eval/results/gate_orchestrator_combined_e9cc68a.json`.

## ✅ CLOSED — cleanup-layer port to production (Modal + Kaggle) — premise was STALE (2026-07-18)

The earlier "port cleanup fixes to Modal + Kaggle" action item assumed
`chike-inference/modal_app.py` and `kaggle/eval.py` each carried their OWN OLD, unfixed
INLINE copy of `clean_reply`. **Direct inspection shows that is not (or no longer) the
case — both already import the shared module:**
- `chike-inference/modal_app.py:421` — `from chike.generation_cleanup import clean_reply`
  (called at :524); modal_app also already builds its prompt via `apply_chat_template`
  (:462), so production was **never** on the mismatched format.
- `kaggle/eval.py:88` — `clean_reply = _cleanup['clean_reply']` (shared module fetched
  from GitHub at runtime; called at :377).

So the three cleanup-layer fixes (`_truncate_repeated_sentences`, generalized
`_GLUED_TURN_RE`, `_cut_nonlatin_and_domain_loops` incl. the U+2212 allowance) already
reach both production and the standalone gate via the shared import — no inline port was
needed. The only genuine divergence was the prompt template (`build_chat_prompt`), fixed
above. Net: production was already correct on BOTH cleanup and chat-template; the fix this
session was scoped entirely to the eval/orchestrator harness. (Minor latent note: modal_app's
`except Exception` fallback at :467-475 still hardcodes the Llama-3 header format; it is dead
code unless apply_chat_template throws, but should be aligned to naive-concat in a future pass.)

Second follow-up (lower priority): framing-aware/semantic polarity for the 5 non-numeric
genuine model inversions (eval_059/062/183/332/391) + eval_317/146.

## Cleanup-layer gap-closure — three EOS-tail cuts (2026-07-18)

Closed the three enumerated `clean_reply` coverage gaps that left the degradation tail in
place after cleanup (chike/generation_cleanup.py; the mitigation layer for the EOS root
cause above). Regression-tested across all 400 raw generations with the module's zero-
content-loss discipline:
- **Intra-block repetition cut** (`_truncate_repeated_sentences`) — cuts at the first
  sentence (>=12 chars) that repeats an earlier one, keeping the first occurrence; re-joins
  via captured separators so a non-repeating reply is byte-identical. Fixes eval_317's
  "Thibitisha…" ×13 loop. A short repeated clause ('Ndiyo. Ndiyo.') is never truncated.
- **Generalized fabricated-turn detection** — `_GLUED_TURN_RE` now catches any short token
  glued directly to '?' with no space ('?nssm', '?about:blank', '?nssf.go.tz'), not just a
  hardcoded role-word whitelist. Fixes eval_183 (the 'nssm' leak) + the domain-token fake
  turns. Role-junk stripping now runs BEFORE the repetition cut so a duplicate closing line
  differing only by a leaked '.user' suffix still de-duplicates (eval_111).
- **Non-Latin-script + domain-loop cut** (`_cut_nonlatin_and_domain_loops`) — truncates at
  the first foreign-script char (Arabic/Cyrillic/CJK) and drops a glued/looped junk domain
  while KEEPING the first legitimate citation (`tra.go.tz` preserved, `.understandthis.com…`
  loop dropped). The allowed range deliberately includes Mathematical Operators (U+2200-22FF)
  so the arithmetic MINUS SIGN U+2212 in PAYE/SDL sums survives — an earlier draft cut there
  and truncated eval_191 mid-sum (caught by the score-regression guard; now a locked test).

Results across 400: eval_317/183 + all 80 detector-degraded cases now clean; 9 previously-
clean cases changed and ALL are prefix-only garbage removal (0 content loss, e.g. eval_090
1399→112, eval_218 1278→118 loop removals); **0 yes_no/number score regressions**, 0 new
candidate-inversion flips. Unit tests added (tests/test_generation_cleanup.py, incl. the
eval_191 minus-sign regression guard); full non-integration suite 138 passed. NOTE: this is
the MITIGATION layer — it does not reduce the 79% overrun (tokens are still generated then
trimmed); only the EOS root fix above does that.

## Post-retrieval-fix 400-run VALIDATION + polarity-parser lexicon fix (2026-07-18)

The founder re-ran the full combined 400 on Kaggle after the retrieval fix (d92e63f);
`gate_orchestrator_combined.json` on HF adapter-v15 (commit d92e63f) was diffed
independently, per-question, against the immediately prior run (HF commit 5817d9d,
internal code commit **c094636**, 400 q). Both files pulled locally; the local
`kaggle/rag_embeddings.npy` + `rag_facts_text.json` are MD5-identical to the HF index
the run used, so retrieval was reconstructed faithfully offline (e5 cached).

### Finding 1 — the retrieval fix is VALIDATED; "eval_317 still inverts" was a false alarm
The prior run had NO polarity review (that code, ca49520, did not exist yet), so the 9
candidate inversions were surfaced for the first time in the d92e63f run — comparison
required reconstructing polarity from the actual generated text in both runs, not the flag.

- **eval_317 (salon):** prior retrieval = `{fine-limit, trademark-fee, vat-deferment}`,
  ZERO GN487A facts → generated *"anaweza kuendesha saluni … chini ya milioni 100"* (the
  dangerous inversion). Post-fix the hybrid appended GN487A fact [21] → generated
  *"saluni **imepigwa marufuku** kwa wasio raia"* — **substantively CORRECT**. The
  retrieval fix reached generation and flipped the polarity wrong→right.
- **eval_355 (EFD 10,999,000):** prior hedge → post-fix *"chini ya 11,000,000 … EFD **si
  lazima**"* — correct (below threshold, not mandatory).
- It still showed as a candidate inversion + pass=False for **two reasons unrelated to
  "generation ignored the fact":** (a) the polarity parser's negation lexicon had no
  prohibition/negation verbs, so *"imepigwa marufuku"* fell through to the affirmative
  default `model=yes`; and (b) a generation-robustness repetition loop ("Thibitisha na
  Idara ya Uhamiaji" ×14) starved the overlap scorer.
- Of the 9: **5 are non-numeric** (eval_059/062/183/332/391) — byte-identical retrieval AND
  generation between runs (the fix's design guarantee held exactly), genuine pre-existing
  model errors OUT OF THIS FIX'S SCOPE; **1 numeric didn't fire** (eval_155, "487A" is not a
  strippable amount — correct); **3 fired and improved/held substance** (317 wrong→right,
  355 hedge→right, 146 right→right).

### Finding 2 — Bucket A 154→152 fully explained, non-regressive; design guarantee held
Exactly **2 flips across all 181 in-corpus Bucket-A questions, both numeric, ZERO
non-numeric flips** (byte-identical guarantee intact; also verified no Bucket-A question
newly refused/clarified, ruling out the interim OOC-classifier commit d767e71):
- **eval_146** — numeric, reliable=False. Substantively correct in BOTH runs ("no grace
  period"); the fix reworded it and the citation shifted Immigration→TanzLII, flipping the
  *unreliable* overlap scorer. Scorer noise, not a real regression.
- **eval_186** — numeric, reliable=True, the ONLY reliable flip. Mechanism confirmed as the
  fix (appended an extra fact → 4-bullet prompt → greedy decoding diverged), NOT GPU
  nondeterminism. But the lost "pass" was itself a **fabricated-number false-pass**: prior
  asserted a *"50 au zaidi"* safety-officer threshold the reference explicitly says is *not
  established*; post-fix dropped the fabrication for a vaguer answer that fails the overlap
  scorer. A lateral move (confident-wrong-that-passed → vague-incomplete-that-failed), not
  the loss of a genuinely-correct answer.

### The cross-cutting discovery — the polarity parser is the bottleneck, not retrieval
The reporting-only parser recognised `hakuna/haiwezi/…` but NOT the core Swahili
prohibition/negation forms these answers use — `marufuku`, `imezuiliwa`, `si lazima`,
`bila`. Proven on real data it BOTH missed the one real correction (eval_317, "marufuku"
read as yes) AND manufactured a spurious new inversion (eval_146, a benign rewording that
dropped the word "Hakuna").

### Reporting-layer fix IMPLEMENTED — negated-obligation lexicon (chike/scoring.py)
Separate from the retrieval-layer fix (d92e63f). Added to `_YN_NEG`: `si lazima` /
`sio lazima` / `siyo lazima` / `halazimiki` / `hailazimu` (an unambiguous NO regardless of
question framing), plus a negative-lookbehind on the positive-`lazima` marker in
`_polarity_conf` so a negated `lazima` reads as a clean 'no', not an ambiguous 'both'.

Full-400 regression (live patched module, re-derived over the stored generations):
- Candidate inversions **9 → 8**: exactly **eval_355 resolved**, ZERO new false positives.
- yes_no scorer: exactly **1 flip, eval_355 False→True** (a correct resolution; reliable=False
  and in Bucket D, so no reliable-subset headline moves). Nothing else in the 400 changed.
- Existing polarity test suite + full non-integration suite green (131 passed).

**DELIBERATELY NOT ADDED (contradicts the initial plan — evidence-driven):** the prohibition
verbs `marufuku` / `imezuiliwa` / `zuiliw` and the broad `bila`. Tested across all 400, a
flat mapping to NO **regressed FOUR genuinely-correct answers** (eval_149/152/153/389) —
because a Swahili prohibition verb carries prohibition CONTENT, not a fixed yes/no polarity:
for "can I do X?" it means NO, but for "is X prohibited / is he covered?" the correct answer
is YES ("Ndiyo, ni marufuku"). `bila` was worse (broke the reliable-scored eval_309). A
framing-aware variant was also tested and still broke eval_153 (a permission-framed question
whose correct answer is YES). So eval_317 and eval_146 CANNOT be resolved by any flat
lexicon; their SUBSTANCE is already correct post-retrieval-fix, and a regression guard test
(`test_prohibition_verbs_deliberately_not_flat_negation`) locks this decision in.

### Next tracked follow-ups (priority order, for future work)
1. **Generation-robustness repetition loop** — eval_317's "Thibitisha…" ×14 tail and
   eval_183's fabricated multi-turn Q&A. Likely a stop-string / `no_repeat_ngram` / decoding
   fix. This (not retrieval, not the parser) is what still fails eval_317's scorer.
2. **The 5 non-numeric genuine model errors** (eval_059/062/183/332/391) — real prohibition
   inversions the retrieval fix does not and was not meant to touch; need a generation/
   prompt-side intervention (leading-question handling, EFD-receipt absolutes) or the
   semantic judge. eval_317/146's remaining parser mis-reads also fold into the semantic-
   judge / framing-aware-polarity workstream.

---

## Prohibition-inversion investigation — ROOT CAUSE = numeric-query retrieval eviction (2026-07-18)

The 400-question run surfaced GN487A prohibition answers that flipped to "allowed"
(eval_317 salon, eval_332 wholesale), hidden from the reliable-subset headline
because scorer_reliability excluded them as yes_no_polarity_unverifiable. A
14-question probe set (gn487a_inversion_probes.jsonl, run on the real v15 model +
e5 RAG on Kaggle, results in gn487a_inversion_probe.json on HF adapter-v15) plus
an offline retrieval trace (e5-base is cached locally; retrieval is CPU-only cosine
over kaggle/rag_embeddings.npy, so the ACTUAL top-3 retrieved facts were reproduced
locally with no GPU) together identify a single, precise root cause.

### Root cause (corrected twice, now evidence-locked): the query's NUMBER hijacks e5 retrieval

The numeral in a question dominates the multilingual-e5-base query embedding and
evicts the topic fact from the top-3, replacing it with numerically-shaped but
semantically-wrong facts (trademark fees, VAT deferment thresholds, course fees —
all "X TZS" entries). With no relevant fact in context, the model falls back on
parametric memory. Confirmed directly by the retrieval trace:

- probe_01 salon + "TZS 100,000,000" -> retrieved {fine limit 100k TZS, trademark
  fee 10k, vat deferment 10M}. The correct salon facts (rag idx 172/176: "salon
  prohibited UNLESS hotel/tourism") were NOT retrieved. Model hallucinated a
  "<100M capital" exception = eval_317 reproduced. Strip the number -> GN487A-family
  facts return and the model answers correctly (probe_02).
- probe_12 EFD + "TZS 500" -> retrieved 3 trademark-fee facts (50k each). The
  correct EFD fact (idx 56: receipt threshold 11M turnover) was NOT retrieved.
  Model fabricated a "TZS 200,000 EFD floor". Strip the number -> the correct EFD
  11M fact returns to #1.
- probe_10 OSHA + "wafanyakazi 8" -> correct OSHA absolute (idx 51: "bila kikomo
  cha idadi ya wafanyakazi") buried at #3 behind {28-day processing, small-scale
  mining}; model hedged "under 10 employees you may not be required" — importing
  SDL's real 10-employee threshold. Strip the number -> the OSHA absolute returns
  to #1.

RETRIEVAL-vs-RECALL determination (the fork the fix hinges on): it is PRIMARILY
RETRIEVAL. The contaminating SDL-10 / VAT-200k facts were NOT themselves retrieved
in probe_10/probe_12 — so the wrong number is free parametric recall, but ONLY
because retrieval first evicted the correct topic fact. Every no-number control
retrieved the right fact and answered correctly. The fix therefore belongs in
RETRIEVAL (numeral downweighting/stripping in the query embedding, or a topic-term
retrieval pass), NOT in a prompt/generation clamp. Precedent already noted in
chike/retrieval.py:44-46 (a raw-dot-product SDL query once ranked GN487A penalties
top — same class of cross-topic embedding contamination).

### Why some numeric probes still answered correctly (H1/H2/H3 verdicts)

Given no fact in context, outcome depends purely on parametric-recall robustness:
- Unconditional absolutes recall correctly despite the retrieval whiff: mobile
  money, phone repair, tour guiding, real estate, wholesale prohibitions
  (probes 03/05/06/07/08); NSSF-from-first (14); min-wage ~175k floor (13).
- Conditional or threshold-adjacent facts fabricate a carve-out: salon (real
  hotel/tourism exception), OSHA (SDL-10 competitor), EFD (a plausible floor).

So: H1 (numeric-distractor binding) CONFIRMED but is a retrieval-eviction artifact,
not conditional-fact reasoning per se. H2 NARROW — only the conditional-exception
activity (salon) flips; 5 other GN487A activities with numbers stay correct;
NOT systemic across GN487A. H3 CONFIRMED-SELECTIVE — OSHA and EFD flip (competing
thresholds exist to recall), min-wage and NSSF hold. All three collapse into the
one retrieval-eviction mechanism above.

### Two SEPARATE, lower-severity findings (do not conflate with the safety issue)

FINDING B — polarity-parser over-surfacing (reporting-noise, NOT a safety defect):
probes 02/03/05/06/07/09 are substantively CORRECT ("...imepigwa marufuku kwa wasio
raia") yet flagged candidate_inversion=True. The "naweza X? ... [activity] marufuku"
construction parses as a low-confidence 'yes' in _polarity_conf (all confident=False).
Human review catches these, so it is review-time noise, not a hidden danger. Refine
by de-tiering a low-confidence 'yes' that contains a strong prohibition marker
(marufuku / imezuiliwa / hawawezi / inakataza) into a distinct "likely-correct,
confidence-parsing" bucket. Lower priority than the retrieval fix.

FINDING C — generation-robustness bleed-through (corroborated, its own defect):
probes 10/11/12 independently reproduced repetition loops, fabricated multi-turn
Q&A, and stray Arabic text surviving clean_reply — the same failure class seen in
eval_303/321/332 on the 400-run. Two independent datasets now show it; logged as a
standalone Priority-3 investigation for when capacity allows. No new action taken.

### Fix scoping (NOT yet implemented — reported for confirmation first)

Target ONLY the confirmed mechanism: numeral-driven retrieval eviction. Do NOT
build a blanket "suppress numeric prohibition answers" clamp — 6 of 8 numeric
GN487A probes answered CORRECTLY and a clamp would regress them. Candidate fix
locus is chike/retrieval.py query construction (numeral handling before embedding);
must be regression-tested against the full 400 for retrieval changes on non-numeric
questions before proposal. Awaiting go-ahead before writing fix code.

### Fix IMPLEMENTED — additive two-arm hybrid retrieval (chike/retrieval.py)

Approved and built. Retrieval-layer change only; the model-level confirmation
(does eval_317's answer actually flip to "prohibited"?) still requires a founder
Kaggle full-400 run (see below).

DESIGN — append-only union of two retrieval arms, at the single retriever boundary
(chike/retrieval.py Retriever.retrieve, used by the orchestrator via retriever.retrieve):
  1. Full-query arm — current production retrieval, top-3, KEPT VERBATIM.
  2. Number-stripped arm — re-embed with digit amounts removed (strip_numeric_amounts:
     'TZS 100,000,000' / bare '8' / '500' go; number-WORDS milioni/elfu/kumi stay,
     since they carry topic meaning without the hijacking magnitude), retrieve top-6.
  3. Merge = APPEND-ONLY: return baseline top-3 unchanged, then append the FIRST NEW
     fact the stripped arm surfaces (final size 4). Fires ONLY when the query contains
     a digit; non-numeric queries take a single-arm path that is byte-identical to
     production (one embed call, no merge) — locked by a unit test.

WHY APPEND-ONLY, NOT INTERLEAVE/RRF (this is the crux): interleave forces a stripped-
arm fact into slot 2, which EVICTED the correct EFD fact sitting at baseline rank 3 on
eval_331 and eval_355 — a real regression the 14-query guard set could NOT catch
because guard facts sit at rank 1. Append-only cannot drop a baseline fact by
construction (verified: 0 regressions across all 90 numeric test queries). It also
resolves the "incidental number vs subject number" problem WITHOUT a classifier: the
full arm keeps the numeric fact when the number is the subject (PAYE 800k, SDL/NSSF
12-employee calcs all still hit), the stripped arm recovers the topic fact when the
number is incidental, the union carries both. add=1 (size 4) chosen over add=2 (size 5)
because coverage was identical (85/90 either way) — take the smaller prompt.

RETRIEVAL-LAYER EVIDENCE (e5 cached locally; CPU cosine; model not run):
  - Topic coverage across 90 numeric GN487A/OSHA/EFD/NSSF questions in the 400:
    baseline 83/90 -> additive 85/90 -> interleave 83/90 (with 2 regressions).
  - additive REGRESSIONS: 0 (append-only, by construction and measured).
  - GAINS: eval_317 (salon — the headline inversion; baseline retrieved zero GN487A
    facts, additive appends a GN487A penalty fact) and eval_347 (EFD threshold false-
    premise question — additive appends the real EFD 11M fact).
  - 14 critical regression guards: 14/14 under additive (integration test asserts all
    14 hit AND eval_317 recovers a GN487A fact on the real 210-fact index).

OPEN FOLLOW-UP (not silently dropped): probe_12 / eval_056 remain unfixed. These use
the word 'Muamala wangu ni TZS 500 tu' — stripping the digit leaves 'Muamala ... tu',
which still mis-retrieves to transaction/fee facts. The real 400-set EFD questions that
use 'Mauzo' (turnover) — eval_354/355 — already retrieve the EFD fact fine. So this is a
narrow 'muamala' vs 'mauzo' wording artifact, NOT a systemic hole; tracked as a separate,
narrower follow-up (would need a topic-term retrieval arm) rather than over-engineered now.

WIRED FOR KAGGLE: no change to eval_orchestrator_combined.py is needed — it constructs
Retriever(...) and passes retriever.retrieve to the Orchestrator (lines 189-190), so the
hybrid is inherited automatically. The script clones main fresh and prints '[clone] chike
@ ... (HEAD <sha>)'; verify that SHA matches the fix commit before trusting the run. The
definitive test is whether the model's ANSWER flips on eval_317 and similar with the
recovered fact in context — founder runs the full 400 on Kaggle (Claude does not run GPU).

## Verification-entry recommendations — all three CLOSED

1. compute_type_reliable + compute_type_genuine_reliable headlines added to
   eval_orchestrator_combined.py (ec2909a) — reporting-only change, matches
   existing fact_path/staged reliable-subset pattern.

2. extract_numbers '000'-garbage-token bug fixed (60f140d) — comma-grouped
   numbers with a 1-2 digit leading group were fragmenting into a bare '000'
   token; fixed regex captures complete thousands-grouped numbers. 0 verdict
   flips across all 250 gate+additions questions (garbage token was present
   symmetrically in reference and generation, so removing it never changed
   a non-empty intersection on this specific dataset) — real fix, no visible
   impact on current results, removes a latent false-pass mechanism.

3. Zero/'does-not-apply' reference answers now flagged scorer_reliability=False
   (BUG 7, e6781fc) — a number/penalty question whose only extractable figure
   is 0 represents a below-threshold conclusion, not a computed amount that
   number-overlap scoring can verify. Exactly 1 reliability-flag change
   (eval_247), 0 verdict flips, scoped narrowly to the numeric-zero signal.

CAVEAT — stored data not yet updated: both scorer changes (#2, #3) were
regression-tested offline against the existing persisted generations in
gate_orchestrator_combined.json, which is valid since neither change alters
any pass/fail verdict. But the STORED JSON's scorer_reliability flags and
the compute_type_reliable/compute_type_genuine_reliable headline values
still reflect the OLD scorer (pre-e6781fc) until eval_orchestrator_combined.py
is re-run on Kaggle. Expected shift on next run: compute_type_reliable
5/7->5/6 (83.3%), compute_type_genuine_reliable 4/6->4/5 (80.0%) — eval_247
drops out of the reliable subset as intended. Do not read the current stored
file as already reflecting these fixes.

DEFERRED (documented, not silently dropped): eval_051's 'no minimum threshold /
illustrative-figures' leniency pattern is a distinct issue from the zero-
conclusion signal just fixed — noted for a future scoped pass if pursued.

All three fixes followed identical discipline: root-cause confirmation via
code inspection, full-scale regression across all 250 gate+additions
questions (not a small sample), verdict-preservation verification, the
114-test suite, and a reviewed report before each commit.

## v16 compute-path — first real end-to-end validation (corrected analysis)

Combined regression (commit 8bf3c85, real v15 model on Kaggle) — independently
re-verified against the actual persisted gate_orchestrator_combined.json,
gate_001_results.json, and gate_orchestrator_subset.json, not accepted from
a first-pass summary.

### Bucket composition (precisely defined)
- Bucket A (fact_path_190): raw bucket is 190 non-compute gate_001 questions;
  stored n=181 is the in-corpus scored subset after _score() drops 9
  out_of_corpus-subdomain rows (eval_192-eval_200) — both numbers are correct,
  they describe different things (raw bucket size vs. scored denominator).
- Bucket B (staged_50): all 50 staged additions, including the 10 compute-routed
  ones — there is no non-compute/compute split within B.
- Bucket C (compute_type): 20 compute-routed questions from either source
  (10 from the gate, 10 from the additions), n=19 after dropping 1 OOC-labeled
  row (eval_191 — the known PAYE-800K question mislabeled out_of_corpus in the
  gate data, documented separately in the v9 analysis).
- B and C overlap by exactly the 10 compute-routed additions (eval_241-250).
  A overlaps with neither.

### Fact-path (Bucket A) parity — CONFIRMED, genuinely strong
Compared against the prior orchestrator subset run on the same 190 IDs:
100% ID overlap, 0 differences in generated text, 0 differences in raw
generation — byte-identical. Only 2 pass-verdict flips (eval_010, eval_165),
both explained by an intentional scorer improvement (BUG-3 multiplier
composition fix) already in place before this run, not a behavior change.
The extraction/compute-path work genuinely did not touch the fact path.

### Scorer leniency for number-type questions — CONFIRMED, worse than first flagged
chike/scoring.py's number-type pass condition requires only ONE expected
figure to appear anywhere in the generated text; extra wrong figures never
cause a fail. Two compounding problems found on independent inspection:
1. Reference answers embed input figures (e.g. the salary used in the
   question) alongside the actual answer figure, so a model that only
   echoes the question's input numbers can pass without stating the
   correct output at all — demonstrated directly.
2. NEW FINDING: extract_numbers() on "TZS 40,000"-style text returns a
   garbage '000' token (the 3+-digit regex can't span the comma), and
   this '000' token is present in nearly every payroll-related correct
   answer AND generated answer, meaning a shared '000' alone can satisfy
   the pass condition regardless of the actual figures involved.

Concrete impact on this run: of 15 genuine-compute pass=True results in
Bucket C, 9 are already flagged scorer_reliability=False (the existing
reliability layer catches most leniency-driven false passes) — but the
combined regression script never computes or reports a reliable-subset
headline for Bucket C the way it does for A and B, so the published
compute numbers (raw 12/19=63.2%, genuine 11/15=73.3%) are the
leniency-inflated ones. The reliable-subset compute figure is only
4/6=66.7% — real, but on too small a denominator to be meaningful yet.

eval_247 specifically confirmed as a genuine per-employee-vs-total-payroll
misinterpretation (multiplied a stated TOTAL payroll by headcount, same
shape as eval_249) — correctly scored as failing, but only by luck of the
scorer (the correct answer's only figure is bare '0', which the leniency
bug doesn't help here). This case should arguably be flagged
scorer_reliability=False as well, since threshold/"TZS 0" answers are
exactly where number-overlap scoring is unsafe in either direction.

### Corrections to initial (pre-verification) characterization
- eval_191 does NOT explain Bucket A's 190->181 drop, as first stated —
  that drop is from 9 different rows (eval_192-200). eval_191 is itself
  compute-routed and lives in Bucket C, contributing to C's 20->19 drop.
- The 190-vs-181 figures are not an internal inconsistency in the data —
  both are correct, describing the raw bucket vs. the scored subset.

### Recommended next steps (not yet done)
1. Add a compute_type_reliable headline to eval_orchestrator_combined.py,
   matching the pattern already used for Buckets A and B, so the compute
   path's true (reliable-subset) performance is visible rather than
   burying it in per-question flags.
2. Fix the '000'-garbage-token bug in extract_numbers() — this affects
   scoring project-wide, not just Bucket C, since any number-type question
   with a comma-formatted TZS amount is at risk.
3. Consider flagging threshold/"answer is zero" reference answers as
   scorer_reliability=False by default, since number-overlap scoring
   cannot meaningfully verify a "does not apply" conclusion.

### Net assessment
Fact-path parity is real and strong — the compute-path work is correctly
isolated and did not disturb it. The compute-path itself is now producing
real, deterministic, rules-engine-backed arithmetic for the first time in
this project's history, but its true accuracy has not yet been measured
on a trustworthy denominator — the reliable-subset sample (n=6) is too
small to draw a conclusion from yet. This is not a regression or a failed
milestone; it is an honest, evidence-based statement of exactly how far
validation has actually gotten, consistent with this project's standing
practice of not trusting a headline number until its scoring methodology
has itself been verified.

## STANDING LESSON — validate Swahili semantic/numeral tests at FULL SCALE (2026-07-17)

Any test in this project that hinges on Swahili semantic or numeral ambiguity MUST be
validated on the full set before its result is trusted, no matter how clean a small
sample looks. A clean sample is NOT evidence; only the full run is.

This has now happened THREE times this session, same shape every time:
1. mDeBERTa NLI hybrid scorer — clean on a 14-example proof, rejected at 190-scale.
2. xlm-roberta-large-xnli — same pattern (small proof convincing, full-scale failure).
3. Slot extraction (chike/extraction.py) — 18-sample dry run showed correct_extract=6 /
   DANGEROUS_wrong_extract=0; the full 205 exposed 25 DANGEROUS (12.2%), concentrated in
   wrong_calculation_number (10/22) and compound_question (9/21) — the categories where a
   number is PRESENT but belongs to something other than the field being extracted
   (a threshold, sales/revenue/capital figure, share/branch count, a different sub-question).

Why samples mislead here: these failures are LONG-TAIL and semantic. An 18-question sample
picks the obvious shapes; the dangerous shapes (sales-figure-as-payroll, USD-as-TZS,
share-count-as-money) are individually rare and only surface in volume. The generic
(computation_type=None) path in particular had NO wrong-base guard at all — invisible until
the full set hit vat/brela/osha/gn487a questions carrying non-payroll numbers.

Rule going forward: no extraction/scorer change is "confirmed" on a sample. Sample = smoke
test only. The full-scale run is the gate.

## Slot-extraction danger investigation — CLOSED (RC-1/2/3 fixed, RC-5 tracked separately)

Full-205 stress test progression: 25 DANGEROUS -> 18 (grader/dataset fixes) -> 8 (RC-1 wrong-base guard) -> 2 (RC-2 plausibility floor, RC-3 currency/net detection).

Final confirmed state, real v15 model on Kaggle, exact match to local prediction:
correct_extract=31, correct_clarify=105, over_clarify=52 (safe misses), compound=15,
DANGEROUS_wrong_extract=2 (both RC-5, tracked below).

RC-5 (extract_078, extract_205) — NOT a numeral-parsing bug. The extracted figure
is genuinely correct in both cases; the problem is the question is a yes/no
compliance question (BRELA registration, VAT registration) that happens to
mention a real payroll figure, and the generic compute-routing path treats it
as a computation question when it should route to a fact-lookup/yes-no answer
instead. This is a routing/classifier scope issue, not an extraction issue.
Tracked as a separate follow-up pass — do not attempt to fix via the extractor,
since the extractor correctly reading a real figure is not the bug.

Extraction logic (chike/extraction.py + chike/swahili_numbers.py) is now
considered production-ready for the fact types it covers: SDL/NSSF/PAYE/WCF
payroll and employee-count extraction, correctly handling vague quantities,
missing antecedents, non-uniform per-person figures, period conversion,
casual slang/approximation, gross/net/allowance ambiguity, currency-unit
mismatches, and wrong-base figures (sales/capital/turnover/share-count
misread as payroll) — validated at 205-question stress-test scale with
two independent confirmations (local deterministic simulation matching
real v15 model output exactly, twice).

Standing lesson reconfirmed a third time this session: small-sample tests
are not predictive of full-scale behavior for Swahili numeral/semantic-
ambiguity logic. Full-scale validation is mandatory before trusting any
result in this category, regardless of how clean a smaller sample looks.
(Refinement: the lesson is about sample SIZE — local deterministic
simulation IS trustworthy once validated at full scale, now proven twice.)

## Extraction danger-case investigation — RESOLVED 25 -> 2 (2026-07-17)

Full-205 stress test on the real v15 exposed 25 DANGEROUS_wrong_extract (a HIGH-confidence
wrong number about to feed the rules engine). All 25 shown verbatim and categorized by root
cause. Fixes (one coherent pass):
- Grader false positives (6): compound danger is now keyed on whether a real computation
  type consumes the value, not mere HIGH confidence in a compound context.
- Dataset mislabel (1): extract_145 relabeled vague_quantity -> swahili_number_words (audit
  trail preserved in _review_original_category_2 / _review_relabel_2026_07_17).
- RC-1 wrong-base guard (9+1): detect_wrong_base now runs on the generic ct=None path (was
  gated to compute types, missing vat/brela/osha/gn487a entirely) + verb-form ("tunauza")
  and threshold ("kizingiti cha vat") and share ("hisa") patterns. Also caught extract_125.
- RC-2 plausibility floor (3): a monthly payroll/salary < MIN_PLAUSIBLE_AMOUNT (10,000 TZS)
  is a miscounted quantity (branches/employees/shares), vetoed to LOW. Also makes
  detect_missing_antecedent key on PLAUSIBLE amounts so a spelled count ("wawili"=2) no
  longer masks a missing antecedent (extract_153).
- RC-3 currency/net/per-diem (3): foreign-currency figures ("dola 300") flagged for
  conversion; net/take-home noun forms ("baada ya makato","mkononi") and explicit
  non-salary per-diem ("siyo mshahara","malazi na chakula") added to the allowance veto.

Full local deterministic 205 run: DANGEROUS 25 -> 2. 115/115 tests pass. No false wrong-base
or floor vetoes on genuine payroll questions (every affected SHOULD_EXTRACT case is a real
sales/capital/count-only question, correctly not extracted as payroll).

### RC-5 — TRACKED FOLLOW-UP (NOT fixed in this pass): routing/scope, not numeral parsing
extract_078 ("laki nne kila mmoja ... tunahitaji kusasisha BRELA?") and extract_205
("Payroll yetu milioni tano ... nisajili VAT?") are the last 2 DANGEROUS. The extracted
figure is GENUINELY CORRECT (400,000 / 5,000,000) — the problem is the question is a
BRELA/VAT yes/no that should never be routed to a payroll computation at all. This is a
classifier/route() scope fix, NOT an extraction-layer bug; forcing it into the numeral
parser would make the extractor second-guess valid figures. Fix at the routing layer in a
separate pass (broaden the out-of-compute / fact-intent detection so a payroll figure inside
a non-payroll question doesn't trigger the compute path).



## chike/extraction.py real logic built + Kaggle regression staged (2026-07-16) — UNCOMMITTED, pending founder review

Replaced the interface-only slot-extraction stub with real logic, tested against the
human-verified 205-example stress test. NOT committed — waiting on the founder's review
of the Kaggle results (per instruction).

Architecture — two layers, deliberate trust split:
- MODEL layer (chike/extraction.py SlotExtractor): the ModelBackend does free-text role
  assignment (which number is payroll vs headcount vs salary) — the model's real strength.
- DETERMINISTIC layer (chike/swahili_numbers.py, NEW, 15/15 local tests): pure unit-tested
  Python owns confidence + clarification, because this session proved even a 32B judge
  misreads Swahili compound numerals (laki/robo/mia). It can only DOWNGRADE a field to LOW
  (-> clarify) or apply a deterministic period conversion; never invents a value. Explicit
  detectors: vague_quantity, approximation(casual_slang), missing_antecedent, wrong_base
  (non-payroll figure for a payroll levy), allowance/gross-net, period(annual/quarter/half
  -> /12,/3,/6; week/day -> clarify), plus a numeral cross-check (downgrade if the model's
  value disagrees with the deterministic parse of a single-figure question).
- Failure-category mapping proven locally (FakeBackend, no GPU): all vague/slang/wrong_base/
  allowance -> correct_clarify; all swahili_number_words/period_conversion/aggregate/
  non_uniform -> correct_extract; 0 DANGEROUS (confident-but-wrong) mis-extractions.

Orchestrator wiring: _answer_compute now passes computation_type into extract(); no other
change. Existing 8 extraction tests still green; existing fact path untouched (route()
unchanged), so the 190 fact-path questions are byte-identical to the prior baseline.

ROUTING FINDING (surfaced during the build): orchestrator.route() only sends keyword+DIGIT
sub-questions to compute, so word-form-number ("milioni mia mbili na hamsini") and no-digit
vague questions bypass extraction entirely. The Step-4 stress test therefore calls
SlotExtractor directly (isolating extraction from routing). Broadening route() to catch
word-form compute intent is a separate follow-up (would move questions between the fact/
compute buckets, so deferred to keep the 190 fact-path comparison clean).

Kaggle scripts staged (prepare-only; founder runs on GPU, Claude never runs them locally):
- kaggle/extraction_stress_test.py — real v15 model vs the 205 reviewed entries, sample(18)
  then full(205); grades correct_extract / correct_clarify / DANGEROUS_wrong_extract /
  over_clarify per failure_category; persists to adapter-v15 HF repo.
- kaggle/eval_orchestrator_combined.py — 200 gate + 50 staged additions = 250 through the
  real orchestrator; reports (A) fact-path 190 UNCHANGED check, (B) first real score on the
  50 staged additions, (C) first real score on the ~10 compute-type questions now through
  real extraction + rules engine. Raw + reliable-denominator (scorer_reliability) scores.

DATA PREREQ (both scripts): data/reviewed/slot_extraction_stress_test_001_reviewed.jsonl and
eval/accuracy_gate/eval_questions_002_additions.jsonl are gitignored/untracked -> NOT on
GitHub, so the founder must upload both to the HF dataset repo (prospAprospA007/
africa-giants-dataset) before running (loaders check local clone -> /kaggle/input -> HF).

## qwen3-32b judge non-determinism finding (2026-07-16)

During slot-extraction dataset review, extract_120 and extract_011 both flipped
verdicts between a 13-entry sample run and the full 205-entry run, despite
temperature=0 configuration. This confirms qwen3-32b via OpenRouter is not fully
reproducible even at supposedly deterministic settings — likely provider-side
routing or reasoning-token variance. Any future single-pass judge verdict on a
borderline case should not be treated as final; consider a second confirmation
pass for anything near a decision boundary.

Also confirmed: qwen3-32b makes real errors on Swahili numeral parsing
specifically (laki/robo/milioni compound number words) — 7 of 22 flags in this
review were the judge misreading the entry's own correct figures, not genuine
dataset defects. This model is usable as a general semantic judge (proven
earlier in the scorer-adjudication work) but should not be fully trusted, without
a second check, on tasks specifically requiring correct Swahili numeral
comprehension.

Context/artifacts: harness kaggle/slot_extraction_review.py (self-contained,
OpenRouter qwen/qwen3-32b, additive-only review of the 205-entry slot-extraction
stress test against locked_facts.json on 3 axes: number fidelity, category fit,
self-consistency). Full run: 205 entries, $0.0866, 426s, 0 parse/API errors,
183 correct / 22 needs_revision. After manual triage the 7 confirmed judge-error
false-positives were corrected to `correct` (marked `_review_correction:
judge_error_confirmed` with the specific misreading recorded in
`_review_judge_original_reason`), leaving 190 correct / 15 needs_revision.
The 15-item human queue lives in data/reviewed/human_review_priority.jsonl
(4 factual_error defects: extract_064 OSHA-safety-officer-threshold-unconfirmed,
extract_164 SDL-10-threshold, extract_052 WCF-allowance-unconfirmed, extract_194
thin-spec; 10 category_dispute; 1 borderline_substantive extract_011). All files
stay in gitignored data/reviewed/, uncommitted, NOT merged into the extraction
build — that still waits on the human pass.

## Hybrid-scorer investigation CONCLUDED — both NLI models rejected, qwen3-32b judge is a genuine improvement (2026-07-16)

Goal: find a semantic layer to replace the regex fallbacks for the 71 gate
questions the fixed scorer marks `scorer_unreliable` and excludes (yes_no
polarity, qualitative-number, year-collision, morphological-overlap cases — see
the 2026-07-13 scorer-audit entry below). Three candidates were tested with the
SAME two-stage protocol every time: (STAGE 1) the 14 confirmed audit examples
against known ground truth, then (STAGE 2) the full 190 non-refusal question IDs.
Every run was executed on Kaggle by the founder and PERSISTED to the v15 HF repo
(`prospAprospA007/africa-giants-adapter-v15`) so the numbers below are read from
saved per-question data, not a local run or a truncated log.

Decision metric (same for all three): FALSE-DEMOTION count — currently-reliable
PASS answers that the candidate would flip to FAIL. A candidate that newly breaks
correct answers is not shippable, so this must be ~0.

### 1. Embedding similarity (intfloat/multilingual-e5-base) — REJECTED
Cosine similarity between reference and generated answer is blind to polarity:
clear contradictions (e.g. eval_059 "handwritten receipt OK", which is WRONG)
score HIGHER cosine than several correct answers. Best single threshold ≈ the
majority-class baseline. Topical similarity swamps correctness. Not viable.

### 2a. NLI — MoritzLaurer/mDeBERTa-v3-base-xnli (280M) — REJECTED
Rule: sw-sw bidirectional, max contradiction ≥ 0.70 ⇒ demote to FAIL.
STAGE 1 looked clean on the 14. STAGE 2 (full 190): **5 FALSE-DEMOTIONS**
(eval_120, eval_121, eval_126, eval_177, eval_191) — correct answers flagged as
contradictions at 0.81–0.98. High-confidence, so threshold-raising cannot fix
them. Confirmed from local run artifact.

### 2b. NLI — joeddav/xlm-roberta-large-xnli (560M) — REJECTED (worse)
Same rule, larger model. Persisted result `nli_regression_xlm-roberta-large-xnli.json`
(git_head 8efdd32). STAGE 1: 12/14 (missed 2 real contradictions, 0 false-positives
on the sample). STAGE 2 (full 190): **13 FALSE-DEMOTIONS** — CONFIRMED from the
saved file (this supersedes the earlier unpersisted "13" figure): eval_067, 074,
076, 081, 083, 086, 103, 119, 120, 121, 156, 161, 191. Several at 0.97–1.00
(eval_081=1.0, eval_119=0.99, eval_083=0.97) demoting plainly-correct definitions
and number answers. The bigger XNLI model is STRICTLY WORSE than mDeBERTa (13 vs 5).
Both NLI models share the failure mode: high-confidence spurious contradictions on
Swahili negation/polarity constructions — exactly the categories we needed help
with. The earlier "hang" on this model was root-caused (slow ~2.24GB anonymous
download + no staged logging, not a freeze) and fixed in the harness; the model
itself is the problem, not the plumbing.

### 3. Frontier LLM-as-judge — qwen/qwen3-32b via OpenRouter — GENUINE IMPROVEMENT
Dense 32B, Qwen3 documents 119 languages incl. Swahili. Judge task: given
(question, reference answer, generated answer) classify generated as substantively
correct / wrong / undetermined + one sentence. Persisted result
`judge_regression_qwen3-32b.json` (git_head 8efdd32). No GPU — runs on OpenRouter.

- **STAGE 1 (14, TRUE ground truth): 12/14 match.** Only **1 genuine harmful error**
  (eval_026, false-demote — misread a deadline) and **1 conservative abstain**
  (eval_093, undetermined instead of wrong). 0 false-promotions. Crucially it
  **correctly rescued eval_157 and eval_175** — two answers the regex scorer had
  WRONGLY FAILED — proving the judge corrects regex, not the reverse.
- **STAGE 2 (190): false-demotion = 13, false-promotion = 6, and it covered ALL 71
  currently-EXCLUDED questions** with a verdict (the entire point of the exercise),
  101 agreements with reliable regex, 0 API errors.
- These 13/6 are DISAGREEMENTS WITH THE IMPERFECT REGEX BASELINE, not proven errors
  (unlike NLI's demotions, which are demotions of verified-correct answers). By type
  the 13 demotions are 6 `number` (genuine regex false-passes on miscalculated
  figures the judge caught — e.g. eval_191 PAYE, eval_072 deadline, eval_091 NSSF),
  6 `procedure` (over-strict completeness/ramble penalties — the judge's real
  weakness), 1 yes_no. The 6 promotions include the two ground-truth-confirmed
  regex false-fails above.
- **Cost/latency: 205 calls, $0.0183 total, 160s wall for 191 calls (8 workers,
  6.33s/call mean).** Trivially acceptable for a gate-run cadence (gates run
  infrequently; ~2 cents and <3 min is nothing).

### Recommendation / next step
- chike/scoring.py stays UNCHANGED. Neither NLI model nor embeddings will be added.
- qwen3-32b is NOT rejected — it is the first candidate whose disagreements are
  mostly the judge being RIGHT (it caught regex false-passes AND rescued regex
  false-fails, and covered all 71 excluded questions). Its only real fault is
  over-strictness on `procedure` completeness.
- Per the founder's escalation branch: this is a genuine improvement worth
  ESCALATING to a larger paid frontier model on the identical harness, to see
  whether the `procedure` over-strictness disappears, and to adjudicate the 13
  demote / 6 promote disagreements against locked_facts.json to measure the judge's
  TRUE precision before wiring it in as the scorer's confirmation layer. Do NOT
  adopt it as a silent automatic scorer until the procedure over-strictness is
  characterized.
- Harnesses are committed and reusable: kaggle/nli_regression.py and
  kaggle/judge_regression.py (both fetch-and-run, both persist to v15 HF).

## v16 orchestrator fact-path parity — CONFIRMED EXACT (final, 2026-07-14)

After two rounds of scorer/cleanup fixes (yes_no polarity fix, clean_reply
parity fix, clean_reply ramble-hardening fix), the v15 pipeline and v16
orchestrator were re-run on Kaggle with fully identical scoring and cleanup
logic (both at commit d72f98f). Result on the exact 190 question IDs the
orchestrator was run on (181 in-corpus fact-path + 9 OOC): v15 = 161/190 =
**84.7%**, orchestrator = 161/190 = **84.7%**, with **0** per-question
disagreements out of 190.

This is definitive proof, not an estimate: raw model generations were already
proven byte-identical between the two pipelines (same v15 adapter, same greedy
decoding, same prompts, now non-Modal in-process load in both). The only
differences ever found were in post-generation measurement (scorer bugs, cleanup
divergence), and those are now fixed and shared across eval.py, modal_app.py, and
the orchestrator via chike/scoring.py + chike/generation_cleanup.py. Zero
disagreements is the direct consequence.

IMPORTANT — corrected historical record: v15's IN-CORPUS gate metric, measured
honestly with the fixed scorer/cleanup, is **84.7% (161/190)** — below the
operative **0.85** in-corpus threshold (kaggle/chike_config.json gate_thresholds,
the R14 single source of truth). The stored gate_001_results.json records
`gate_passed: False`. This is the first time v15 fails its own gate. Every
previously recorded v15 gate score (91.1%, 88.0%, 87.9%) was inflated by the
scorer bugs now fixed. The model's actual quality has not changed — the
measurement is now honest. Production has been serving at this true quality
level all along; this is a pre-existing measurement gap now closed, not a new
problem introduced by v16 work.

  (Note on framing: the gate scores in-corpus and OOC as two SEPARATE pools —
  in_corpus ≥ 0.85 AND out_of_corpus ≥ 0.70. OOC is 10/10 = 100%. A naive blend
  of both pools (171/200 = 85.5%) is NOT how the gate is scored and must not be
  cited as a pass; the failing pool is in-corpus at 84.7%. The 0.85 in-corpus
  threshold is the intended governing value in chike_config.json (R14); CLAUDE.md's
  old 0.82 reference was stale and has been corrected to 0.85.)

v16 orchestrator status: fact-path is proven at true parity with v15, using
real, non-proxy, non-Modal-dependent gate runs on Kaggle. Remaining work
(compute-path slot extraction, the 10 excluded compute-routed questions) is
unchanged — still correctly blocked pending real ambiguous-phrasing data.

Immediate implication (project-wide, requires a decision): since v15 (production)
now measures below the 0.85 in-corpus gate threshold with honest scoring, and the
orchestrator matches it exactly, NEITHER system currently passes the gate. This is
a real finding — not a v16 problem, a project-wide one. Options: raise real
accuracy (fact/generation work) or revisit the threshold with eyes open. No
silent reversion of the scorer fixes.

## Confirmed gate status (2026-07-13) — threshold reconciled to 0.85

CLAUDE.md previously referenced an outdated 0.82 in-corpus threshold; the
actual, intended, governing threshold has always been 0.85 in
chike_config.json (R14 single source of truth). CLAUDE.md corrected to match.

With the threshold confirmed at 0.85:
- v15 (production): 84.7% in-corpus (161/190) — FAILS the gate
- v16 orchestrator: 84.7% in-corpus (161/190) — FAILS the gate, exact parity with v15
- Both: 100% OOC — PASSES

This is not a v16 regression. It is the first honest measurement of production's
true accuracy, after fixing three scorer/cleanup bugs that had inflated every
previous recorded score (91.1% -> 88.0% -> 84.7%, corrected). Production has
been serving real WhatsApp users at approximately this true accuracy level
all along.

This is a real, standing gap against the project's own stated bar and needs
a decision: either close the accuracy gap (more/better training data, or the
frontier-model path already discussed earlier this project), or make a
deliberate, documented decision to adjust the threshold with clear reasoning
if 0.85 is reconsidered as the right bar — not by silently drifting to
whatever a given measurement happens to produce.

## Additional measurement findings (2026-07-13, post-parity investigation)

### Finding 4 — Compute-path exclusion flatters the orchestrator's headline number
The 181-question 'shared' comparison excludes 9 in-corpus compute-routed questions
that v15 answers correctly (no routing) but the orchestrator cannot yet answer
(slot extraction unbuilt, correctly stubbed). Counting these as fails on the full
190-question in-corpus set: orchestrator = 152/190 = 80.0%, v15 = 161/190 = 84.7%.
The 'exact parity' claim is TRUE ONLY for single-part, non-compute questions.
On the full set, the orchestrator is currently 4.7 points behind v15 — this is
the real, quantified cost of the deferred compute-path work, and should be
stated whenever the orchestrator's score is cited.

### Finding 5 — A fourth scorer bug inflates the in-corpus baseline itself
chike/scoring.py's number/penalty scorer falls back to 'pass if response is
>10 characters' whenever the expected answer contains no 3+ digit number,
percentage, or TZS amount (e.g. 'siku ya 7', 'ndani ya mwezi mmoja', '15
activities'). 27 of 82 number/penalty questions (33%) hit this fallback.
Confirmed genuine false-passes: eval_178 (hallucinated OSHA minimum-employee
threshold that doesn't exist), eval_114 (no SDL deadline given, credited pass),
eval_093 (wrong NSSF deadline, credited pass), eval_176 (contradicts locked_facts
and the gate's own reference answer, credited pass). This bug affects v15 and
the orchestrator equally (shared scorer), so it does not affect the parity
finding, but it means the 84.7% headline itself is inflated. Estimated honest
score after removing confirmed false-passes: approximately 82.5-83.2%.

Also flagged: eval_176's reference answer in the gate question set itself
contradicts locked_facts.OSHA_safety_officer_threshold, which explicitly says
this figure is unconfirmed and must not be stated — a separate gate
data-quality issue requiring correction independent of the scorer fix.

## Comprehensive scorer audit + coordinated fix (2026-07-14, commit 255a9ec)

After four separate scorer bugs were found one-at-a-time this session, a single
deliberate exhaustive pass was done over EVERY answer type in chike/scoring.py.
Six bugs total. **Key meta-finding: the scorer has both inflation AND deflation
bugs, and they roughly cancel — so Finding 5's "84.7% is inflated to ~82.5%" was
itself wrong-signed.** On the trustworthy (verifiable) subset the real figure is
HIGHER than 84.7%, not lower (see numbers below).

The six bugs:
- BUG 1 (number/penalty, inflates): `if not correct_nums: return len>10` length
  fallback when the answer has no 3+digit numeric key. 26 questions. Confirmed
  false-passes eval_178/114/093/176.
- BUG 2 (number/penalty, inflates): `\d{3,}` extracts the year '2025' from
  'Finance Act 2025' boilerplate; a shared year passes the question. Confirmed
  eval_033.
- BUG 3 (number/penalty, deflates): `extract_numbers` didn't compose multiplier
  words, so 'milioni 5' (→1,000,000 + dropped '5') never matched '5,000,000'.
  Confirmed false-fail eval_165 (a perfectly correct answer scored wrong).
- BUG 4 (yes_no, deflates + latent inflation): fixed negation list misses regular
  Swahili negatives (haku-/hau-/ha-+verb) and a subordinate-clause 'hakuna' flips
  polarity; the affirmative default silently passes any 'yes'-expected question.
  Confirmed false-fails eval_019/040/059/180/182.
- BUG 5 (definition/procedure, deflates): exact-token overlap≥3 defeated by
  morphology (usajili/usajilishaji) and synonyms (inakataza/inazuia,
  wageni/wasio-raia). Confirmed eval_026/157/175.
- BUG 6 (default branch, latent inflation): unknown answer_type fell through to a
  silent 'pass if >20 chars'.

**Empirical proof BUGs 1/2/4/5 are NOT regex-fixable:** a broadened yes_no
negation regex was built and regression-tested across all 61 yes_no — it made 5
correct fixes but introduced 3 NEW regressions (eval_060/153 clearly wrong),
because Swahili negations occur in both decisive and subordinate clauses. Every
broadening trades a false-fail for a new false-pass. Proven, not asserted.

**Decision (hybrid): fix the two regex-clean bugs, exclude the rest.**
- BUG 3 + BUG 6 fixed in chike/scoring.py, regression-tested: only 2 number/penalty
  verdicts flip (eval_165 correctly now passes; eval_010 correctly excluded as
  compute-derived) — zero new regressions among scored questions. Test suite 99/99.
- BUGs 1/2/4/5: a new `scorer_reliability(q, generated)` classifier marks every
  affected question `scorer_unreliable` with a reason and EXCLUDES it from the
  scored denominator — reported separately as 'unscored, pending semantic judge',
  never silently passed or failed. Deterministic from the question + output, so
  v15 and orchestrator exclude the same set.
- Gate data fix: eval_176/eval_190 reference answers corrected to match
  locked_facts.OSHA_safety_officer_threshold (state the threshold is unconfirmed,
  redirect to osha.go.tz) instead of asserting the wrong '50 employees' figure.

**New honest gate math (offline re-score of the stored runs; Kaggle re-run pending):**
- v15: 200 questions → 71 marked scorer_unreliable → **113/129 = 87.6%** on the
  verifiable denominator.
- v16 orchestrator: 190 it ran → 68 unreliable → **106/122 = 86.9%** on the
  verifiable denominator (still separately owes the 9 compute-routed it can't
  answer — Finding 4).
- Unreliable breakdown (v15): qualitative_number 26, yes_no_polarity 20,
  compute_derived 12, year_only 6, year_collision 2, morphological_gap 3,
  yes_no_ground_truth_ambiguous 2.

Both systems clear 0.85 ON THE VERIFIABLE SUBSET — but this is a REDUCED
denominator (129/200). The 71 excluded questions are genuinely unknown, not
passed: the system's true full-set accuracy is unknowable until a semantic judge
(LLM-as-judge / the frontier-model scoring path) scores the excluded categories.
Known residuals inside the 'reliable' set: ~2 synonym-variation false-fails
(eval_157/175) that prefix-stem detection doesn't catch — so 87.6% is a slight
UNDER-estimate. The long-term fix for the excluded 71 is a semantic judge, not
more regex.

FOLLOW-UP REQUIRED before the Kaggle re-run reproduces these numbers: eval.py and
eval_orchestrator.py must be wired to call scorer_reliability(), emit
`scorer_unreliable`+reason per question, and report the reduced-denominator score.
That wiring is NOT in commit 255a9ec (which was scoped to scoring.py + the gate
data file per instruction).

## Gate measurement-bug fix + corrected baseline + orchestrator gate rework (2026-07-13)

A measurement bug was found during v16 orchestrator validation: the gate scorer was
crediting wrong answers, inflating reported scores. Three commits fixed it, then two
more prepared the orchestrator gate for a real (non-proxy) Kaggle re-run.

**Scorer fixes (commit da9c69a):**
1. `chike/generation_cleanup.py` `clean_reply` was blindly truncating at the first
   `\n\n`, discarding real content. Fixed to preserve content blocks until a genuinely
   fabricated block is detected (9 verdict flips, all fail→pass, zero regressions).
2. The `yes_no` scorer credited a wrong answer whenever a fabricated ramble happened to
   contain the expected keyword. Fixed to compare substantive-answer POLARITY (leading
   Ndiyo/Hapana/La word + Swahili negation markers on the first `\n\n` block) instead of
   a full-text substring scan.

**Corrected baseline:** the old v15 in-corpus figure of 91.1% was inflated by the
substring bug. A preliminary local rescore of stored v15 outputs gave ~85.3%, but the
definitive real Kaggle re-run of `eval.py` (2026-07-14) settled it at **84.7% (161/190)**
in-corpus — see the confirmed-gate-status section at the top of this file. Against the
governing 0.85 in-corpus threshold (chike_config.json, R14) this is a gate FAIL.
The 91.1% figure elsewhere in this file predates the fix and should be read as inflated.

**Scorer extraction (commit b5a5e83):** `score_question` + helpers extracted into shared
`chike/scoring.py` (leaf module, stdlib-only), consumed by both `kaggle/eval.py` (via
fetch-and-exec) and `kaggle/eval_orchestrator.py` (via git-clone import) — single source
of truth, following the `chike/prompting.py` / `chike/generation_cleanup.py` pattern.

**Raw pre-clean persistence (commit 96f9d8b):** the prior orchestrator run stored only
the CLEANED output, so when `clean_reply` changed there was no way to rescore offline —
forcing a full GPU re-run. Fixed: `SubAnswer` and `Reply` now carry a `raw_text` field
holding the model's pre-clean generation (captured in `_validate_and_clean` before `text`
is overwritten; merged onto `Reply` alongside the cleaned `text`). `eval_orchestrator.py`
now saves both `generated` (cleaned, scored) and `raw_generated` (pre-clean) per question,
so any future `clean_reply` change is rescorable from saved JSON without another GPU run.
26→96 test suite still green.

**Orchestrator gate de-Modaled:**
`eval_orchestrator.py` previously drove generation via `LocalAdapter` — an HTTP client to
a Modal raw-generation endpoint requiring a second Kaggle secret (`MODAL_API_TOKEN`) and
190 live HTTP calls. Rewired to load the v15 adapter DIRECTLY on the Kaggle GPU (new
in-process `KaggleDirectBackend(ModelBackend)`, byte-identical 4-bit load + generation
config + `StopOnSubstrings` stopping criteria as `eval.py`), passed into the Orchestrator
as its backend. Now needs ONLY the `AFRICA_GIANTS` HF secret — same as `eval.py`. No
Modal, no HTTP, no raw endpoint. `LocalAdapter` (the HTTP client) is left intact for
local-dev-over-HTTP use; the `chike` package stays torch-free (transformers imported at
script level, same as `eval.py`).

### Ready for Kaggle re-run (founder runs; Claude does not)
- `kaggle/eval.py` → real corrected v15 baseline (~85.3% in-corpus expected).
- `kaggle/eval_orchestrator.py` → real v16 orchestrator fact-path number (replaces the
  82.3% v15-stored-output proxy from da9c69a), saving both cleaned + raw output.
- Both need only the `AFRICA_GIANTS` secret + Kaggle GPU. Both fetch code from GitHub
  main, which is fully pushed.

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

Gate requirement: ≥85% in-corpus AND ≥70% OOC
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
