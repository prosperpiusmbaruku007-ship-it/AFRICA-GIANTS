# ADR 0002 — Retrieval structural scoping: five candidate mechanisms, two measured

- **Status:** Interleave (§5) shipped, live-regressed on one of its own protected rows, and
  reverted the same day (2026-08-22) — production confirmed back on pre-ship code. The ship
  decision itself is now understood to have rested on a false distinction (§5(d)): rank-level
  measurement cannot certify answer stability. A standing bar for future retrieval ships is
  recorded in §5(d). General fusion (RRF/weighted/interleave) is DECLINED in all forms; §2
  (routing intercept) is the leading candidate, named explicitly as a small fix for 6 known fact
  keys, not a general retrieval solution. §8 (generation-side failure ceiling) is now MEASURED AND
  re-diagnosed: forcing the correct fact(s) into context for all 8 remaining rows produced 4
  correct, 1 partial, 3 clearly wrong — but an engine-shape check on those 3 found only 1
  (`nat_33`) is a genuine capability gap (no BRELA engine exists); the other 2 (`nat_23`, `nat_24`)
  have working SDL/NSSF/WCF engines nothing currently routes to — a routing/decomposition gap, not
  a model ceiling. §2's expected yield is ~5–6 of 8 alone, ~7 of 8 if paired with a separately
  scoped routing fix. §1/§6/§7 remain scoped-only, not built.
- **Deciders:** Founder + Claude Code.
- **Supersedes:** nothing. Promoted from `scratch/retrieval_structural_scoping_2026_08_22.md`
  (moved out of scratch on founder instruction — this is a decision record, not a throwaway
  diagnostic, and scratch/ is gitignored by the project's scratch-file convention).
- **Related:** PROGRESS.md "THE RETRIEVAL CYCLE'S VERDICT..." (2026-08-22, the nine-row verdict
  this scoping answers); `docs/decisions/0001-...` (the prior ADR precedent for this format);
  `scratch/coverage_scoping_2026_08_16.md` (the scoping-discipline precedent this mirrors).

## 1. Context

The R15 regen cycle (C4 wording rewrites + e5-base embedding upgrade) moved exactly one of 48
natural-register questions (`nat_43`) despite three target facts' ranks improving substantially
(`sdl_rate` 150→24, `GN605A_sector_count` 127→1, `annual_return_filing_fee` 113→25). Rank
movement that doesn't cross `top_k=3` (the number of facts `chike-inference/modal_app.py`
actually injects into the prompt) is invisible to production. Per-row wording is a real lever
(`nat_43`, and the similarity-floor ceiling test both prove it directly) but is not a viable
shape against a field where the correct fact routinely sits 20–150 rows deep across nine known
rows. This ADR scopes — and, for two items, measures — the structural alternatives.

## 2. The nine rows, current (post-R15) dense rank, 221-fact index

Re-measured this session against the live deployed index (`kaggle/rag_facts_text.json` /
`rag_embeddings.npy`, 221×768, e5-base), not the stale 217-row snapshot the original scoping
cited — `scratch/item5_lexical_measurement.py`, part (a):

| row | dense rank (post-R15) | gold row(s) |
|---|---|---|
| nat_43 | **1** (fixed by C4's `GN605A_sector_count` rewrite — the one confirmed live win) | 72 |
| nat_41 | 5 | 52, 219 |
| nat_05 | 15 | 5 |
| nat_45 | 19 | 51 |
| nat_28 | 33 | 17 |
| nat_44 | 33 | 16 |
| nat_33 | 48 | 134 |
| nat_24 | 91 | 7 |
| nat_23 | 94 | 5 |

Eight of nine remain unresolved (`nat_43` already closed by R15). `top_k` 3→9 reaches none of
them (`scratch/factpath_ceiling_and_topk.py`, prior session) — not a cutoff problem.

---

## 3. FEE-SHAPE DOMINANCE, HANDLED AT INDEX-CONTENT LEVEL — scoped, not built

**What was already tried and killed:** a retrieval-time mask (exclude the 66 `<key>: <number>
<unit>` fee rows from general retrieval, re-admit via a fee-intent-gated second pass).
`scratch/feemask_experiment.py`: **0 of 9 fixed** — masking promoted a *different* wrong row, not
the correct one, every time. Cost: 3 confirmed regressions (nat_27, nat_36, nat_37 lose their
supporting fact). **This specific design is closed.**

**What was NOT tried:** rewriting the *competitor* fee rows' text out of the generic
`<key>: <number> <unit>` shape — the same content move C4 already proved works on a *target*
fact, applied to the ~66 rows crowding top-3 slots (58% of all top-3 slots across the 48
questions, `scratch/factpath_feetable_dominance.json`).

**Cost:** content-authoring only, folds into the normal regen cycle. Size: likely 20–30 rows that
actually co-occur with the nine failing questions' top-3 pools, not all 66.

**Risk:** rewriting a fee row to be less numeric-attractive for one query class could make it
*worse* for the query class it's the correct answer to — the same trade C4 already caught once
(nat_27 displacement risk on the withheld VAT rewrite). Needs the same 400+48 regression check
C4 already built.

**Priority: HIGH, unchanged.** Cheapest lever not yet tried in its correct form. **Not yet
executed — folds into the next regen, per the recommended order below.**

---

## 4. ROUTING-LAYER INTERCEPT FOR FACT QUESTIONS — scoped, and the disanalogy named honestly

**The founder's challenge, stated plainly first:** compute questions route to an *engine* that
computes an answer from arbitrary inputs; a fact-question intercept routes to... a specific fact
key, chosen by a hand-maintained cue list. **Yes — that is exactly what this is: a hand-maintained
question→fact-key allowlist.** It is cheap and reliable for the 6–7 known fact keys behind the
nine failing rows, and worth nothing for any fact-recall failure not yet observed. Read plainly,
that is the failure-driven approach with extra steps, which is the opposite of what a mechanism
needs to prove out before a pilot: something that helps failures nobody has found yet.

**Where the compute-path analogy actually holds, and where it stops:** `chike/routing.py`'s
`_natural_levy` (line 883) and `detect_intent` route into a **closed, four-member target set**
(sdl/nssf/paye/wcf) — the cue list's only job is coarse disambiguation ("which of 4"), and a
downstream deterministic *engine* supplies the real answer from live inputs regardless of which
cue fired. That's why one cue-list pass generalized across many phrasings and moved 9 compute
rows WRONG→CORRECT: the target space was small and closed, and the hard part (arithmetic) was
never in the cue list. A fact intercept has no such engine behind it — the cue list itself
**is** the answer-delivery mechanism, mapping straight to a fact key with nothing downstream to
generalize the way arithmetic does. The two are not structurally identical; the compute case's
success doesn't transfer.

**The one real thing it does buy, stated narrowly:** one cue-list entry per fact key can cover
several *phrasings* of that one already-known-broken question (e.g. 3–5 ways users ask about
`vat_withholding_goods`), where a single embedding rewrite (R15/C4's tool) optimizes rank for
close to one canonical phrasing — the ceiling-test finding is that query-echoing text reaches
rank 1 only for text close to the literal query. So this is a narrow, real edge over a wording
pass, not a structural fix: it generalizes across phrasing for a **fixed, known** set of facts,
and does nothing for the field's actual shape (buried facts nobody has flagged yet).

**Coverage ceiling, named concretely:** covering `sdl_rate`, `GN605A_sector_count` (already
fixed), `vat_withholding_goods`/`services`, `brela_annual_return_fee`, `osha_registration`,
`wcf_accident_reporting_deadline` — 6 fact keys — would deterministically protect the 8 known
rows. Zero benefit to any future fact-recall failure not on this list, and zero interaction with
the other ~30 fact-path natural48 questions currently answered correctly by ordinary retrieval.

**Cost:** code-only, no GPU, no regen. Each of the 6 keys needs its own R17 adversarial-probe
pass (author in-scope probes containing the risky cue vocabulary, not just sweep the existing
corpus) — real per-key effort even though no infrastructure changes.

**Revised recommendation, after §5(d)'s ship-and-revert:** general fusion is declined outright, not
paired with a guard — so this mechanism is evaluated on its own merits, not as a patch for
another. On its own merits it is the strongest candidate scoped so far, for one specific reason:
it is the only mechanism here with a **provably bounded blast radius by construction** — an
explicit cue match short-circuits RAG entirely for that question; every other question's retrieval
is byte-identical to today, because nothing about the mechanism touches it. §5(d) showed that
property does not hold for any fusion variant tested; it does hold here, structurally, not by
measurement.

**Named honestly, as asked directly: what is this FOR.** It is not a general retrieval fix and
should not be scoped, funded, or reported as one. **It is a fix for six known, already-identified
fact keys — `sdl_rate`, `GN605A_sector_count` (done), `vat_withholding_goods`/`services`,
`brela_annual_return_fee`, `osha_registration`, `wcf_accident_reporting_deadline` — and nothing
else.** There is no broader version of this mechanism that escapes the coverage ceiling described
above. The ceiling is not a matter of the cue table being small today and growable later; it is
structural to a hand-authored cue→key table: it can only ever cover a key a person put in the
table, so however large the table grows, it stays reactive to failures someone has already found.
Growing it over time changes its *size*, not its *character* — it never gains the ability to help
a fact-recall failure nobody has observed yet, which is the field's actual, ongoing shape. **This is a
legitimate, small, immediate-relief objective — close 8 known rows safely — not a candidate
solution to the retrieval problem, and it should be named that way in any future status report.**
Priority: **HIGH, scoped explicitly as a targeted patch, not a general lever.**

---

## 5. HYBRID LEXICAL + DENSE FUSION, GENERAL FORM — MEASURED this session (`scratch/item5_lexical_measurement.py` / `.json`)

**The question, stated precisely per the founder's framing:** not "does hybrid help" — the
narrow number-stripped arm already answered that weakly (1 recovery / 86 dilutions, rejected).
The real question: **does lexical (token-overlap) scoring recover the rows dense ranking buries
at rank 20–150, or only rows already close?** Measured against the current 221-fact index, three
fusion strategies (weighted 0.5/0.5 minmax, Reciprocal Rank Fusion k=60, dense/lexical
interleave — same three from `scratch/item4_hybrid_sweep.py`), reported both the recovery and
the cost together, not the positive alone.

### (a) The eight remaining known-failure rows, hand-verified gold, dense vs. hybrid rank

| row | dense | weighted | RRF | interleave |
|---|---|---|---|---|
| nat_05 | 15 | **1** | **1** | **2** |
| nat_23 | 94 | **1** | **3** | **2** |
| nat_33 | 48 | **2** | **3** | 6 |
| nat_41 | 5 | **1** | **1** | **2** |
| nat_28 | 33 | 8 | 6 | 14 |
| nat_44 | 33 | 9 | 5 | 16 |
| nat_45 | 19 | 25 | 6 | 37 |
| nat_24 | 91 | 95 | 37 | 54 |

**RRF crosses `top_k=3` on 4 of 8** — `nat_05` (rank 15→1), `nat_23` (94→3), `nat_33` (48→3),
`nat_41` (5→1). That includes a row buried at rank 94, which no wording pass this cycle reached —
this is the first mechanism tested against this cluster that moves *multiple* buried rows in one
change rather than one row per rewrite. Weighted crosses on the same rows minus `nat_33`
(rank 2 either way, so effectively the same 4). Interleave is weaker on recovery (3 of 8:
`nat_05`, `nat_23`, `nat_41`) but — see below — cleaner on cost. **None of the three strategies
move `nat_24`, and none cross `top_k=3` for `nat_28`, `nat_44`, or `nat_45`** — real, substantial
rank improvement (33→5–9) that repeats the exact "doesn't cross the cutoff" pattern R15 already
demonstrated.

### (b) Dilution cost — 21 fact-path questions in the natural48 set (gold by argmax-cosine proxy, same method as item4; caveat below)

| strategy | mean rank | top3% | recovered (>3→≤3) | diluted (≤3→>3) |
|---|---|---|---|---|
| dense (baseline) | 50.5 | 19.0% | — | — |
| weighted | 43.9 | 19.0% | 3 | 3 |
| RRF | 49.6 | **28.6%** | 5 | 3 |
| interleave | 58.8 | 28.6% | 2 | **0** |

**The cost, named specifically, not just counted:** RRF and weighted both push `nat_31`, `nat_32`,
`nat_34` from rank 1 to rank 8–16 — out of `top_k=3`. These are not hypothetical: all three are
**live-verified CORRECT today** (`eval/results/natural48_rerun_2026_08_17_adjudication.json`,
`path: fact, was: CORRECT, now: CORRECT, reply_identical_to_baseline: true`). Shipping RRF or
weighted as-is would risk breaking three confirmed-correct production answers to gain roughly
four. **Interleave measured zero dilution** on this set, at the cost of weaker recovery (misses
`nat_33`, and has the worst mean rank of the four).

**Caveat on the (b) proxy:** the argmax-cosine-to-`expected_behavior` gold selection is
imperfect — it mis-picked `nat_43`'s gold as a neighboring row (rank 124) instead of the
hand-verified correct row (rank 1), because the two are textually close. The (a) table above is
hand-verified and is the reliable number; (b)'s aggregate is directionally consistent but should
be read as approximate, not exact.

### (c) Can the guard be general, or only an enumerated list? — tested, answer is negative

The obvious objection to "pair RRF with a guard that pins `nat_31`/`nat_32`/`nat_34`": if the
guard is defined as exactly those three keys, the dilution count reads zero because the casualties
were named in advance — circular, not a measurement. Tested whether a **general, property-based**
guard exists instead: the candidate named but never measured in the similarity-floor scoping
(PROGRESS.md, 2026-08-16) was **margin** (top-1 score minus top-2 score under plain dense
ranking) — high margin meaning dense is unambiguous and should be trusted outright, low margin
meaning dense is uncertain, which is exactly the condition fusion is meant to help.
`scratch/item5b_margin_guard.py` computed margin for all 21 fact-path questions:

| group | margin range | n |
|---|---|---|
| currently-correct, dense rank 1 (`nat_31`, `nat_32`, `nat_34`, `nat_43`) | 0.0002 – 0.0037 | 4 |
| known-buried (the eight unresolved rows) | 0.0004 – 0.0101 | 8 |

**The ranges overlap, and the direction is inverted from what a naive rule would assume:**
`nat_32` (currently correct) has the single smallest margin of all 21 questions measured
(0.0002), while three known-buried rows (`nat_44`, `nat_41`, `nat_45`) have *larger* margins than
every currently-correct row. A margin threshold built to "trust confident dense hits" would get
this backwards — it would flag the known-buried rows as more trustworthy than the ones actually
worth protecting. **No general threshold on this signal separates the two groups.** This is a
finding in its own right, not just a null result: it says the compressed-score-band problem named
in the 2026-08-16 floor scoping isn't just "everything is close together" — confidence-by-margin
specifically fails to track correctness here.

**Consequence, stated as the founder asked:** the guard, if built, can only be an enumerated key
list — not a property computed from the score vector. **What that means a year from now:** when a
new fact is added or reworded and happens to land at dense rank 1 for its natural phrasing (which
this measurement shows is common and not reliably distinguishable from a "risky" rank-1 by
margin), nothing about the guard notices. It stays unprotected under RRF/weighted until someone
independently re-runs a full live adjudication and spots the regression — there is no automated
signal comparable to `check_facts_index_sync.py`'s drift check for "which facts need pinning."
The list has to be manually re-derived by a human remembering to do it, every time the index
changes. **The earlier "guarded dilution = 0" number is therefore a floor for these three
specific keys today, not a measurement that generalizes.**

**Interleave's zero dilution is different in kind — proven structural, not empirical, and it
needs no guard at all.** By construction (`chike/retrieval.py`-style interleave: alternately pull
from the dense order and the lexical order, dedup), **the dense-rank-1 candidate is always
consulted first and placed at position 1 of the merged list**, before the lexical order is ever
read. Any question dense already gets right at rank 1 stays at rank 1 under interleave,
*regardless of what the lexical signal says* — this is a property of the merge algorithm, true
for every future fact the same way it's true for `nat_31`/`nat_32`/`nat_34`/`nat_43` today, with
no list to maintain and nothing to silently miss.

**Verdict, holding both options side by side rather than picking the bigger number:**

| | recovers (of 8 known-buried) | dilution | how the safety holds |
|---|---|---|---|
| RRF + enumerated pin list | 4 (`nat_05`, `nat_23`, `nat_33`, `nat_41`) | 0, but only for the 3 named keys — a floor, re-derived by hand on every future change | manual, silently stale |
| Interleave, no guard | 3 (`nat_05`, `nat_23`, `nat_41`) | 0, proven structural for any dense-rank-1 fact, present or future | automatic, self-maintaining |

Three recovered at zero-by-construction dilution is arguably worth more than four recovered at
zero-by-patching dilution, exactly because the patch's safety depends on a list nobody is
guaranteed to update. **Priority: HIGH for interleave as the lower-risk option; RRF+pin-list
scoped and measured but flagged as carrying an unbounded, silent maintenance liability that
interleave does not have.**

**Not yet built. This is a measurement only** — no retriever code changed, no fusion strategy is
live. **The ship decision is: interleave (weaker recovery, self-maintaining safety) vs. RRF with
a pin list that must be manually re-derived every time a fact changes (stronger recovery,
maintenance liability) — a separate go-ahead, not decided here.**

### (d) Interleave was shipped, live-tested, and reverted — the premise was false, not just the ship (2026-08-22)

**Lead finding, stated before the regression that surfaced it:** interleave's structural guarantee
held *perfectly*, on every row tested, and a live answer still broke. The guarantee covered
whether the target fact kept its rank; it said nothing about the other two injected slots, and
generation turned out to be sensitive to those. This is the **presence-not-conclusion family**
(PROGRESS.md, recurring at the level of a test assertion, a sweep harness, and a routing check)
arriving at a **ship criterion** for the first time: "the target fact is present at rank ≤3" was
cheap to check and easy to mistake for "the answer is unchanged."

**The ship decision itself was made on a false distinction.** (c) chose interleave over RRF on
"RRF dilutes 3 named rows, interleave dilutes 0." That was never a real difference in what the two
mechanisms do to an answer — both change the non-target slots for virtually every query. It was a
difference in which one had been measured. RRF's cost was named because someone had to enumerate
casualties by hand; interleave's was assumed zero because the rank-only instrument had nothing to
report. **Neither mechanism has a smaller blast radius than the other on the quantity that
determines correctness.**

Given the go-ahead, interleave was implemented (`chike-inference/modal_app.py`'s `retrieve_facts`
+ `kaggle/eval.py`, R14 dual-sync), deployed through the full R16 cycle, and live-canaried per the
founder's explicit instruction: test the claimed invariant rather than assert it. It failed.

**`nat_32` — one of the three rows this ship was specifically supposed to protect — returned a
wrong, live, reproducible (2/2 identical calls, `do_sample=False`) answer**, asserting construction
is one of GN487A's 15 prohibited activities and that passive shareholding is punishable — the
opposite of the correct distinction this row tests. Diagnosis: the target fact (row 210, the
shareholder-vs-operator distinction) **stayed at rank 1 under both old and new code**. The
regression came from the other two slots: old top-3 `[210, 176, 179]` → new top-3 `[210, 92, 176]`.
One filler fact swapped for a different one, with the correct fact present and unchanged both
times, was enough to flip the model's completion.

**The more actionable number: 8 of 8 rows changed context; 1 of 8 flipped.** Compared old-vs-new
top-3 for all 8 rows canaried as "must stay correct":

| row | old top-3 | new top-3 | live outcome |
|---|---|---|---|
| nat_31 | 205, 206, 193 | 205, 21, 206 | stayed correct |
| nat_32 | 210, 176, 179 | 210, 92, 176 | **flipped to wrong** |
| nat_34 | 130, 131, 114 | 130, 44, 131 | stayed correct |
| nat_43 | 72, 128, 182 | 72, 128, 7 | stayed correct |
| nat_26 | 171, 101, 146 | 171, 57, 101 | not re-tested live |
| nat_27 | 170, 199, 171 | 170, 5, 199 | not re-tested live |
| nat_36 | 171, 25, 126 | 171, 58, 25 | not re-tested live |
| nat_38 | 171, 58, 148 | 171, 58, 57 | not re-tested live |

Every row's context changed; only one flipped. That ratio, not the single incident, is the
transferable result: **any retrieval change touching pooled context has a blast radius across the
whole currently-correct set that no offline instrument this project owns can currently detect** —
rank stability passed all 8; the 48-question live run would only have caught this after the fact,
one deploy at a time.

**STANDING BAR for every future retrieval-change ship, recorded here because this is what would
have stopped this one:** rank-level measurement (does the target fact keep its position?) is
*necessary but not sufficient*. Before any retrieval mechanism ships — fusion, re-ranking, a bigger
model, anything capable of reordering which facts accompany an already-correct target — it needs
an **answer-level** regression check: old generated reply vs. new generated reply, across the full
currently-correct set, not just the rows the change targets. A mechanism that only reports target-
fact rank is reporting presence, not the conclusion a ship decision actually needs.

**Reverted and verified live within the same session** — both files restored (nothing had been
committed), full R16 cycle repeated, `nat_32`/`nat_31`/`nat_34`/`nat_43` re-tested live and
confirmed back to their correct pre-ship answers. Production is on the pre-ship, dense-only
single-arm code as of this entry.

**Revised verdict: neither RRF nor interleave ships.** Not because interleave's structural
guarantee was false — it held in every single test — but because the guarantee was scoped to the
wrong thing (one fact's rank) for what a ship decision actually needs (the full injected set's
stability for rows not being fixed). §1 (rewrite the fee-row text directly) and §2 (a routing
intercept scoped to named fact keys) remain the two candidates that don't share this problem,
because both touch a bounded, named set of rows *on purpose* rather than reshaping every query's
retrieved context as a side effect of a general merge rule. **Priority for general fusion
(RRF/weighted/interleave), all forms: DECLINED pending a mechanism that can change a target row's
rank without touching any other row's supporting context — no such mechanism is scoped yet.**

---

## 6. RE-RANKING (cross-encoder) — scoped only, unchanged from original scoping

Named as a design direction by the similarity-floor scoping (2026-08-16: top-1 scores
0.790–0.859, failing-row correct-fact scores 0.765–0.809 — no absolute threshold separates them)
but never built or measured. Cost: a small multilingual cross-encoder on the existing T4
container, cheap relative to the 8B model's dominant latency (7.3s median), but requires a new
harness and a new model dependency. **Priority: MEDIUM, unchanged, and flagged with the same
caution §5(d) just surfaced:** a cross-encoder re-ranking every query's dense shortlist has the
same general shape as fusion — it re-scores and can reorder the top-3 for questions that were
already correct, not only for the nine target rows. It is NOT automatically exempt from the
blast-radius problem §5(d) found; that would need its own explicit test (old-vs-new top-3 set
across a broad sample, not just the target rows) before it could be called safer than fusion. A
version gated to fire only when dense is "uncertain" would need a reliable uncertainty signal —
and §5(c)'s margin experiment already found none exists on this index. Re-ranking is untested on
this exact question and should not be assumed safer than what was just measured.

---

## 7. A DIFFERENT / BIGGER EMBEDDING MODEL — scoped only, unchanged

This is not a fresh idea — it is what R15 already was (384-dim → e5-base 768-dim, yield +1/48,
fee-shape dominance unchanged). The failure mode described in §3 is about surface text shape, not
encoder capacity; no evidence held predicts a bigger model changes which rows win. **Priority:
LOW. Not scheduled.**

---

## 8. GENERATION-SIDE FAILURE AFTER SUCCESSFUL RETRIEVAL — MEASURED across all 8 remaining rows (2026-08-22)

**Measured, not left as a live-canary hint.** Two rows forced into `top_k=3` during §5(d)'s live
canaries (`nat_05`, `nat_23`) both still failed despite reaching context — enough to warrant a
direct test, run as its own measurement rather than another retrieval build. Added a temporary,
additive-only debug method (`ChikeModel.run_forced_facts`, `chike-inference/modal_app.py`) that
runs the real v15 pipeline (`chike.pipeline_v15.answer`, the actual generation model, the actual
prompt builder) with `retrieve_facts` replaced by a constant — the correct fact(s) for that row,
supplied directly, bypassing ranking entirely. Deployed via full R16 cycle, ran all 8 remaining
known-buried rows (`nat_43` excluded — already fixed by R15), then **removed the debug method and
redeployed again**, confirming `nat_43`/`nat_32` still answer correctly and `run_forced_facts` no
longer exists. Production was never left running debug-only code; nothing about `run()` or
`retrieve_facts()` was touched.

> # ✅ SETTLED — re-measured on live v16 with a committed instrument (2026-08-22)
>
> **The provisional results below have been re-run and are superseded.** Instrument committed
> before the run (R18) at `9be20c7`; artifact `eval/results/ss8_forced_facts_v16_2026_08_22.json`;
> fixture `eval/forced_facts/ss8_rows.json`; runner `eval/forced_facts/run_ss8_forced_facts.py`.
> Every row reports `pipeline: "v16"`.
>
> **The 4 CORRECT / 1 PARTIAL / 3 WRONG split reproduced exactly.** Two failure-mode descriptions
> did not:
> - **`nat_23` routed to `compute`** — the NSSF engine fired and computed correctly (20% ×
>   5,500,000 = 1,100,000); **SDL was silently dropped.** Not a generation ceiling; the routing
>   fan-out miss, confirmed live.
> - **`nat_24` returned a bare "Thibitisha na TRA" deferral**, not the "no hedge, no uncertainty
>   signal" the provisional entry described. This overturns the PROGRESS.md headline's "no route to
>   a refusal of any kind" claim, corrected there.
> - **`nat_05` is also a routing miss** (`detect_intent → "none"`, routed `fact`, so the compute
>   path's clarification never fires). **Three of eight rows are routing misses; only `nat_33` is a
>   genuine capability gap.**
>
> **§2's yield, now measured not estimated: 4–5 of 8 alone (not ~5–6); 6–7 of 8 with a routing/
> decomposition extension; `nat_33` out of reach of both.** §2's §8 precondition is satisfied.
>
> The historical record of the superseded attempt follows.
>
> ---
>
> # ⛔ SUPERSEDED / PROVISIONAL — the original attempt, kept for audit trail
>
> **The instrument is uninspectable and by its own description ran the wrong pipeline.**
> `run_forced_facts` was deployed, used and removed **without ever being committed** —
> `git log -S'run_forced_facts' --all` returns nothing, on any branch. No artifact exists. The
> method description above says it ran `chike.pipeline_v15.answer`; production serves **v16** (see
> the retraction in the CORRECTION below). The results here may therefore be measurements of a
> non-production pipeline, taken by an instrument that cannot be re-read.
>
> **Provisional in full:** the 4/1/3 split, every per-row outcome, the arithmetic-clustering
> pattern, and **§2's revised yield in the SUMMARY table and Recommended-order item 1, which is
> arithmetic on this table and inherits its defect.**
>
> **The narrow defence covers two rows only.** `detect_intent` returns `nssf`/`none` for
> `nat_23`/`nat_24`, so both arms route those two to the same pooled-fact generation and the
> pilot-safety finding drawn from them survives either way. That is a statement about two rows. It
> does not extend to the other six, to the split, or to the clustering claim.
>
> **Being re-measured now:** harness committed first, run on the live v16 path, all eight rows.
> **§2 does not start until that lands.**

| row | facts forced | outcome |
|---|---|---|
| `nat_44` | vat_withholding_goods (3%) | **CORRECT** — states 3%, doesn't confuse with 6% |
| `nat_45` | wcf_accident_reporting_deadline (7 days) | **CORRECT** — states 7 days |
| `nat_41` | OSHA registration-before-opening + no-threshold | **CORRECT** — no specific deadline, correctly refers to OSHA, invents nothing |
| `nat_28` | vat_withholding_services (6%) + certificate-timing | **CORRECT** — both facts stated accurately, no arithmetic required |
| `nat_05` | sdl_rate (3.5% of payroll) | **PARTIAL** — states the rate is of "mishahara ghafi" (gross payroll), correctly avoiding the wrong-base trap, but does not ask for the payroll figure the rubric wants |
| `nat_33` | BRELA late-fee (2,500/mo) + annual fee (22,000) | **WRONG** — states only the penalty rate; drops the annual fee entirely despite it being forced into context, and never computes 7×2,500 |
| `nat_24` | sdl_threshold + NSSF rate + WCF rate (3 facts) | **WRONG** — bare non-answer ("Thibitisha na TRA"), no content at all despite all three facts present |
| `nat_23` | sdl_rate + NSSF rate (2 facts) | **WRONG** — restates the input salary and stops; no arithmetic on either levy, despite both facts present |

**Result: 4 clearly correct, 1 partial, 3 clearly wrong — a mixed finding, not a clean answer
either way.** Most (4–5 of 8) DO produce a correct or acceptable answer once retrieval is forced to
succeed — retrieval genuinely is a binding constraint for the majority of these rows, and closing
it (§1, §2) is worth doing. But a full **3 of 8 (37.5%) fail even with the exact right facts
handed to the model directly** — retrieval was never going to be sufficient for these three,
regardless of which retrieval mechanism eventually ships.

**CORRECTION, same day — the first framing above called this a "generation-side" ceiling before
checking whether it was actually a routing gap. It wasn't fully checked. Checked now, and it
changes the diagnosis for 2 of the 3 failures.** The three all involve arithmetic, so the first
pass filed them together as one model-capability property. That conflated two different questions:
(a) does a deterministic engine exist for this arithmetic at all, and (b) does anything route to
it. Checked directly against `chike/routing.py` and `chike/rules_engine/`:

- **`nat_33` (BRELA, 7×2,500) is genuinely NOT engine-shaped.** `COMPUTE_TYPES =
  ("sdl","nssf","paye","wcf","minimum_wage")` — BRELA is not one of them, and no
  `chike/rules_engine/brela.py` (or equivalent) exists anywhere in the codebase. There is nothing to
  route to. This one really is a capability gap: either the model has to synthesize the
  multiplication in free text reliably (it currently doesn't), or a new engine has to be built.
- **`nat_23` and `nat_24` ARE engine-shaped — the arithmetic they need (SDL 3.5%, NSSF 20%, WCF
  0.5% of payroll) already has real, working engines** (`chike/rules_engine/sdl.py`, `nssf.py`,
  `wcf.py`) that ADR 0001 documents as the mechanism that already fixed 9 compute rows once.
  **The engines are live and the router still does not reach them for these two questions.**
  Ran `chike.decomposition.decompose_query` + `chike.routing.detect_intent` directly on both
  (artifact: `scratch/verify_v16_routing_2026_08_22.json`): neither splits into separate
  sub-questions — both stay one whole sentence, because the decomposer doesn't split on nicknamed
  levy references like *"ile ya mafunzo na ile ya uzeeni"*, only on `?`-splits and explicit
  enumerated lists — and `detect_intent` returns `nssf` (a single levy, not the 2-levy fanout
  `nat_23`'s gold answer needs) and `none` (`nat_24` — the 3-way threshold-trap phrasing doesn't
  fire the natural-levy cue detector at all) respectively. `Orchestrator._fan_out_multi_levy`
  (`orchestrator.py:832`) would split a multi-levy compute part into one compute per levy, but it
  fans out only what `detect_intent`/`_explicit_levy` already named — a nicknamed levy that was
  never detected cannot reach it. **The gap is real, and it is a routing/decomposition gap —
  nicknamed multi-levy phrasing isn't recognized yet — not a limit on what the engines themselves
  can compute.**

  > **RETRACTION (same day, after a crash mid-edit).** This bullet previously gave two reasons
  > instead of one, and the first was wrong: it claimed *"production (v15, live) has zero
  > compute-engine routing of any kind"* and described `chike/orchestrator.py` as *"v16, not
  > live."* **Both are false.** `kaggle/chike_config.json` carries `"pipeline": "v16"` — set at
  > `ec9cbb3` (*"config(pipeline): v16 — the cutover flip"*) and unchanged since;
  > `chike-inference/modal_app.py:153` reads it into `PIPELINE`; `:458` branches on it and calls
  > `self._orchestrator().answer(message)`; `_orchestrator()` builds
  > `Orchestrator(backend=..., retriever=self.retrieve_facts, ...)` — production's own bound
  > retriever, identical to the v15 arm's — and `Orchestrator.answer()` runs
  > `decompose → route → rules_engine` (`orchestrator.py:824-850`). **v16 is deployed, the live
  > path does reach the rules engines, and every 48-run measurement this cycle was of the real
  > system.** The `pipeline_v15.answer` grep behind the false claim was run against a code path
  > the config selector no longer chooses.
  >
  > The routing diagnosis above is unaffected: it was never derived from which pipeline is live,
  > only from direct calls to `decompose_query`/`detect_intent` — the exact modules
  > `Orchestrator.decompose()`/`.route()` invoke — and was re-verified after the crash. The
  > correction makes the gap *worse*, not better: the pipeline that owns these engines is already
  > in production, so there is no pending cutover that closes it.

**Revised framing: 1 of 3 failures is a model/engine-coverage capability gap (`nat_33`); 2 of 3 are
an architectural routing gap with a known, existing fix pattern (`nat_23`, `nat_24`) — not a raw
generation-capability ceiling as first stated.** `nat_05` (partial) is unaffected by this
correction — it needs an inferential move (recognize the given figure is the wrong base), not
arithmetic dispatch, and is unrelated to engine routing.

**Consequence for §2's expected yield — revised again, upward, and conditionally.** If a routing/
decomposition extension is later built to (a) split nicknamed multi-levy phrasing and (b) detect
multi-levy fanouts and threshold traps from natural cues the way it does from explicit levy names,
`nat_23` and `nat_24` become reachable by the EXISTING sdl/nssf/wcf engines — not a new engine, a
routing fix. That would put §2's real yield back close to **7 of 8**, not the ~5/8 estimated before
this check, with only `nat_33` needing either a new BRELA engine or a genuine generation-side fix.
**This routing/decomposition extension is NOT scoped or built here** — it belongs to the routing
workstream (`chike/routing.py`, `chike/decomposition.py`, `chike/orchestrator.py`), not this
retrieval ADR, and is a separate go-ahead. Until it exists, §2 alone still only reaches ~5–6 of 8,
because closing retrieval doesn't help if nothing downstream can use SDL/NSSF/WCF facts to compute
a fanout answer.

**Consequence for the pilot-safety floor (§5(c)):** this closes a gap the margin experiment left
open. A retrieval-confidence floor — even a hypothetically working one, which margin is not — is
built on a signal from the RETRIEVAL side (how sure is the index that it found the right fact).
`nat_23` and `nat_24` had the correct fact(s) placed directly in context, i.e. **maximum possible
retrieval confidence by construction**, and the model still produced a bare non-answer with no
hedge, no "sijui," no visible uncertainty marker at all. **A retrieval-side floor cannot catch this
failure class even in principle** — the defect is not "the model wasn't sure which fact to use,"
it is "the model had the fact and did not use it correctly." The pilot's "refuse when we don't
know" safety net would need a signal from the GENERATION side (e.g., a post-hoc check that the
reply actually addresses every part of a multi-part question, or a self-consistency check), not a
better retrieval score, and no such mechanism is scoped anywhere in this document.

---

## 9. ROUTING EXTENSION — SCOPED FROM MEASUREMENT, NOTHING BUILT (2026-08-22)

**Measured first, per the standing order.** Harness `eval/routing/measure_nickname_routing.py`,
probes `eval/routing/nickname_probes.jsonl` (16, including 4 R17 adversarial/negative controls),
artifact `eval/results/nickname_routing_measurement.json`. Pure inspection of the deterministic
routing stack — no model, no deploy, re-runnable in a second. **This section is scoping. Nothing in
it has been built, and it needs its own go-ahead.**

### 9.1 The nickname machinery is NOT the gap

The first framing — "the decomposer doesn't split nicknamed multi-levy phrasing" — is true but is
not the binding constraint. Measured: `nick_08/09/10` (nickname + digit + payroll context +
explicit money-ask) route to compute correctly as `sdl`, `nssf`, `wcf`. **`_natural_levy` resolves
`mafunzo`→sdl, `uzeeni`→nssf, `fidia`→wcf today, and `_LEVY_CUES` already contains all three.**
Any scoping that starts by adding nickname cues is solving a solved problem.

### 9.2 Three distinct gaps, not one

| gap | probes | what actually blocks it | shape of fix |
|---|---|---|---|
| **A. Fan-out is blind to nicknames** | `nick_04` (nat_23), `nick_11` | `_fan_out_multi_levy` fans out on `routing.all_explicit_levies`, which matches only the four explicit levy tokens. **There is no `all_natural_levies` counterpart.** `_natural_levy` returns a FIRST match over `_LEVY_CUES`, so a 2-nickname question resolves to one levy and the other is invisible | add the natural-cue counterpart and fan out on the union. The fan-out itself needs no change — it is already reachable from a nickname-resolved compute route |
| **B. The compute-intent gate rejects real asks** | `nick_02`, `nick_06` (nat_24), `nick_07` (nat_05), **`nick_03`** | path 2 needs `_has_money_ask`; path 2b needs `is_applicability_question`. *"nilipe nini kati ya…"* (which of these do I pay), *"nitalipa asilimia tatu na nusu ya nini"* (of what), and *"je nalipa SDL"* (do I pay X) satisfy neither | widen the ask-shape recognisers. **Not a levy-cue change** |
| **C. The number requirement** | `nick_01`, `nick_12` | paths 2/2b require `_has_number`. `watano` is a Swahili numeral word, not a digit | **DO NOT relax — see 9.3** |

**`nick_03` is the load-bearing result.** It names **SDL explicitly**, states a headcount, and still
routes to fact — blocked in path 1 for having no compute-intent cue. **So gap B is not about
nicknames at all.** The live conflation probe would still miss with the levy spelled out. Framing
this workstream as "nicknamed multi-levy decomposition" would have fixed gap A and left the gap that
actually produced the observed defect untouched.

### 9.3 The obvious fix for gap C is measured to be unsafe

Relaxing `_has_number` to accept Swahili numeral words would capture `nick_01` and `nick_12`. It
would also capture **both R17 adversarial probes**, which are currently held out by that gate alone:

- `nick_15` — *"natoa **mafunzo** ya kompyuta kwa wanafunzi je nasajili biashara yangu wapi"* —
  training as a **service**, not the Skills Development Levy. Cue resolves `sdl`.
- `nick_16` — *"mfanyakazi wangu ameumia je **fidia** yake italipwa na nani"* — a compensation
  **claim**, not a WCF levy amount. Cue resolves `wcf`.

Both would be pulled into levy compute. **This is the R17 lesson holding exactly: the corpus sweep
was clean and the authored probes were not.** Gap C should be left closed, or opened only behind a
context qualifier that these two probes are wired to fail against.

### 9.4 What actually causes the conflation — measured, and NOT what this section first said

**An earlier draft of this subsection blamed the routing miss and the missing fact-path guard.
Measurement contradicts it, and the draft is corrected rather than quietly adjusted.**

Live, 2 attempts each (`eval/results/nickname_live_probes.json`):

| probe | phrasing difference | live answer | verdict |
|---|---|---|---|
| `nick_01` | *watu **watano*** (word numeral) | *"…asilimia **0.5** kwa ajili ya mafunzo… **nssf.go.tz**"* | **WRONG**, 2/2 (4/4 including the original two) |
| `nick_02` | *watu **5*** (digit) — otherwise identical | *"Kama una wafanyakazi chini ya 10, hakuna ulazima wa kulipa SDL. Thibitisha na tra.go.tz."* | **CORRECT**, 2/2 |
| `nick_03` | digit + **SDL named explicitly** | *"…unatakiwa kuwa na wafanyakazi 10 au zaidi ili kulazimika kulipa SDL…"* | **CORRECT**, 2/2 |
| `nick_08` | compute-routed | model body content-free; **engine appends `SDL = 3.5% × TZS 5,500,000 = TZS 192,500`** | **CORRECT**, 2/2 |

**`nick_01` and `nick_02` route identically** (`detect_intent → none`, fact path) — so the routing
miss cannot be the differentiator. **And they retrieve the IDENTICAL top-3** (measured directly
against the production index with production's own e5 query encoding,
`eval/results/numeral_form_retrieval.json`: same three facts, ranks 1 and 2 merely swapped) — so
retrieval content is not the differentiator either. Same route, same facts, opposite answers,
each stable across repeats under greedy decoding. **The divergence is generation-side, and its
trigger is the surface form of the numeral.**

### 9.5 The much larger finding underneath it: retrieval fails this question completely

The top-3 that BOTH phrasings receive is:

```
1  minimum shareholders: 2 employees
2  unpaid contribution penalty rate: five %
3  minimum directors: 2 employees
```

**Not one of them is an SDL fact.** No rate, no threshold. The correct answer `nick_02` gives is not
grounded in its context at all — it comes from model memory, and `nick_01` shows what happens when
that memory lands wrong. **A "correct" answer here is a coin-flip that happened to land, not a
working system**, which is a materially worse finding than the conflation that surfaced it.

Two consequences:

- **The `nick_02`/`nick_03` "CORRECT" verdicts must not be read as the system working.** They are
  ungrounded generations that happened to be right. Any future measurement using them as passing
  controls is measuring luck.
- **The index contains malformed rows that win top-1 on payroll questions**, and they are now
  counted rather than gestured at (`eval/index_quality/scan_fragment_rows.py` →
  `eval/results/index_fragment_scan.json`, a **heuristic shape detector — it flags shapes, not
  wrongness, and every hit needs human adjudication**):

  | signal | hits / 221 | notes |
  |---|---|---|
  | terse English `key: value` fragment rows | **89 (40.3%)** | the shape R15 explicitly documents as retrieving *worse* than short Swahili-first text with the value at the front |
  | spelled-out numeral where a figure belongs | 6 | `trademark renewal period: **saba** years`, `unpaid contribution penalty rate: **five** %`, `penalty imprisonment non citizen: six months **null**` |
  | count/period carrying the wrong unit noun | 3 | `minimum directors: 2 **employees**`, `minimum shareholders: 2 **employees**` — **and one false positive** (`duration of maternity cash benefit: 12 weeks`, which is correct), which is why this is labelled a heuristic |

  **Any signal: 90 of 221 rows (40.7%).** The headline number is the 89: R15's own note says a fact
  embedded without the `key: ` prefix, Swahili-first with the value at the front, retrieves far
  better — and roughly two fifths of the live index is in the shape that note warns against.
  **This is §1 (index-content rewriting), and it now looks under-rated rather than a tidy-up
  that folds into the next regen.** It is not scoped further here and the 89 have not been
  adjudicated one by one.

### 9.6 The guard gap is real, but it is not the cause

Stated correctly this time: the conflation reply got past `_cross_levy_guard` because **the guard
was never invoked.** It is called only inside `answer()`'s compute branch and returns early on
`len(by_levy) < 2`. A fact-routed question produces no `ComputationResult`, so every D-FIDELITY rule
that compares a body against `sub.computation` is **vacuously satisfied**. The only fact-path check
is GUARD A, which compares a stated headcount against a `chini ya N` claim — here the headcount
claim was *correct*; the **rate** was wrong. So there is a genuine hole. **It is a missing safety
net, not the cause** — the cause is 9.5.

**This is D-FIDELITY-5's shape, one level out.** D-FIDELITY-5 exists because "a contradiction
doesn't need a number" — a body that denies an obligation in words defeats every figure-comparing
rule. Here a body that states a **wrong rate for a named levy** defeats them the same way, and for
the same structural reason: nothing to compare against.

**A rate check is not Guard B.** Guard B (fabricated amounts) is impossible because a fabricated
figure and a legitimate transformation are both just arithmetic relationships to the user's number.
**A levy rate is a constant, not a derived quantity** — SDL is 3.5%, WCF 0.5%, NSSF 10/20% — so
"3.5% is not 0.5% under any transformation" has exactly GUARD A's safety property. **That makes a
fact-path rate/levy-consistency guard worth scoping.** The obvious risk, which must be measured
before anything is built: a correct multi-levy fact answer legitimately states several rates, so the
check has to bind a rate to its adjacent levy subject and not merely detect a wrong number
somewhere in the body. Untested. Not scoped further here.

### 9.7 A rate guard is worth scoping, and it is NOT the impossible Guard B

Guard B (fabricated *amounts*) is impossible because a fabricated figure and a legitimate
transformation are both just arithmetic relationships to the user's number. **A levy rate is a
constant, not a derived quantity** — SDL 3.5%, WCF 0.5%, NSSF 10/20% — so *"3.5% is not 0.5% under
any transformation"* has exactly GUARD A's safety property, and this is D-FIDELITY-5's shape one
level out: a wrong **rate** defeats every figure-comparing rule for the same structural reason a
worded denial does — there is nothing to compare against. The measured risk to test first: a correct
multi-levy fact answer legitimately states several rates, so the check must bind a rate to its
adjacent levy subject rather than detect a wrong number anywhere in the body. **Untested. Belongs to
`chike/fidelity.py`, not routing.**

### 9.8 What this workstream is, stated honestly

- **Gap A** (fan-out blind to nicknames) is real and matches the original framing. Small fix:
  an `all_natural_levies` counterpart; the fan-out itself needs no change.
- **Gap B** (ask-shape) is real and **affects explicitly-named levies too** (`nick_03`), so the
  "nicknamed multi-levy" framing would have missed it.
- **Gap C** (number requirement) should stay shut — 9.3.
- **9.5 is the biggest item found here and it is not routing work at all.** Retrieval returns zero
  relevant facts for a plain SDL applicability question, and malformed index rows out-rank real
  ones. That is §1, and it now looks under-rated rather than a tidy-up.
- **9.7** is a candidate guard in `chike/fidelity.py`.

**Expected yield is NOT measured.** §8 says `nat_23`/`nat_24`/`nat_05` become reachable, but no
before/after has been run, so **6–7 of 8 is an inference from §8, labelled as one** per the standing
order — it is not a measured yield and must not be ranked as though it were. The next step for this
workstream is a measurement, not a build.

---

## SUMMARY (updated 2026-08-22, post-ship-attempt)

| # | mechanism | status this round | priority |
|---|---|---|---|
| 5 | Hybrid lexical+dense fusion (RRF/weighted/interleave) | **SHIPPED (interleave), LIVE-REGRESSED, REVERTED.** Target-fact rank preservation held for all 8 rows tested; the OTHER two injected slots changed for all 8 anyway, and one (`nat_32`) flipped to a wrong live answer. Neither RRF's nor interleave's real blast radius (answer stability, not rank) was ever fully enumerated — interleave's was wrongly assumed zero. | **DECLINED, all forms** |
| 2 | Routing-layer fact intercept | **SCOPED, purpose named honestly:** a hand-maintained allowlist that closes 6 known fact keys / 8 known rows and nothing else — not a general retrieval fix, no broader version escapes that ceiling. Leading candidate because it's the only mechanism here with a *provably* bounded blast radius (explicit cue match short-circuits RAG; everything else untouched — no fusion variant could claim that after §5(d)). **✅ Expected real yield per §8, MEASURED on live v16 (`eval/results/ss8_forced_facts_v16_2026_08_22.json`): 4–5 of 8 alone — lower than the ~5–6 previously estimated; 6–7 of 8 if paired with a separate routing/decomposition fix (not scoped here); `nat_33` out of reach of both. No longer provisional.** | **HIGH, as a named small objective, not a solution to retrieval** |
| 1 | Fee-shape rows rewritten at index-content level | scoped only, unchanged. Same §8 ceiling applies to `nat_33` (no engine exists); `nat_23`/`nat_24` are engine-shaped, blocked on routing not retrieval. | HIGH (folds into next regen) |
| 6 | Re-ranking (cross-encoder) | scoped only, unchanged — flagged that it likely shares §5(d)'s blast-radius problem (re-scores every query's shortlist) and needs its own explicit old-vs-new test before being assumed safer | MEDIUM |
| 7 | Different/bigger embedding model | scoped only, unchanged — this is what R15 was | LOW, not scheduled |
| 8 | Generation-side / engine-routing failure after successful retrieval | **✅ SETTLED — re-measured on live v16 with a committed instrument (R18). Split reproduced 4/1/3; `nat_23` routed to `compute` and the NSSF engine computed correctly with SDL dropped; `nat_24` deferred ("Thibitisha na TRA"); `nat_05` is a third routing miss. Three of eight are routing misses, only `nat_33` is a capability gap.** Originally measured by an uncommitted harness, then re-diagnosed the same day. Forced the correct fact(s) into context for all 8 remaining rows: 4 correct, 1 partial, 3 clearly wrong. Checked whether the 3 failures are engine-shaped before calling them generation-side (they weren't fully checked first pass): **`nat_33` has no engine at all (BRELA isn't a `COMPUTE_TYPES` member) — a real capability gap. `nat_23`/`nat_24` have working engines (SDL/NSSF/WCF), and v16 — which owns them and IS the deployed pipeline (`chike_config.json: "pipeline": "v16"`) — still doesn't route to them, because the decomposer doesn't split nicknamed multi-levy phrasing and `detect_intent` returns `nssf`/`none`.** 2 of 3 are a routing gap with a known fix pattern, not a model ceiling. (An earlier version of this row claimed production runs v15 with zero compute routing — **retracted, false**; see §8's retraction. The engine-shape half of the diagnosis stands on its own — it was checked against the code and re-verified. The half that says these rows *failed* is provisional, from the table.) Also the headline pilot-safety finding: these failures carry maximum retrieval confidence (fact forced directly into context) and no visible hedge, so no retrieval-confidence floor could ever catch them — see PROGRESS.md's dedicated pilot-precondition entry, not just this ADR. | The routing/decomposition extension for nicknamed multi-levy fanouts is a separate go-ahead, owned by `chike/routing.py`/`chike/decomposition.py`, not this ADR. A new BRELA engine (`nat_33`) is separately scoped-able, smallest of the three. |

## STANDING ORDER: MEASURE, THEN SCOPE — NOT SCOPE, THEN MEASURE (2026-08-22)

**Measurement has now reordered this queue against the prior recommendation four separate
times.** That is no longer a run of bad luck; it is the base rate, and the ordering discipline
should follow it.

| # | item | what the recommendation was | what measuring did to it |
|---|---|---|---|
| 1 | **Fee-mask** (`87606cb`) | scoped as a fix worth building | **measured and rejected outright** |
| 2 | **Margin as a similarity floor** (`5149e9b`) | the leading floor design after the absolute threshold died | **measured: it INVERTS** — the correct row had the smallest margin of 21, three known-wrong rows scored larger margins than every correct one. Retired at its original scoping location |
| 3 | **Interleave / hybrid fusion** (`5de044d`, `f171363`) | shipped, on a structural guarantee that was real | **the guarantee certified the wrong quantity.** Live-regressed, reverted, §5 declined in all forms |
| 4 | **§2 vs the routing extension** (`e22cdcd`, this cycle) | §2 was the lead candidate on an expected ~5–6 of 8 | **re-measured on live v16: §2 alone is 4–5 of 8; the routing extension takes it to 6–7. The comparison inverted.** The provisional numbers §2 led on were produced by an uncommitted harness |

**The shared shape:** in every case a design was scoped, ranked and — twice — nearly or actually
built, on a number or a premise that had not been measured on the live system. In every case the
measurement, when it finally happened, did not refine the estimate; it **reversed the decision**.
Three of the four reversals were cheap because they happened before or shortly after a build. The
fourth was cheap only because §8 was re-run before §2 started.

**So the order is: measure, then scope, then build.** Concretely, before an item may be ranked in
the table below:

1. Its expected yield is measured on the **live** pipeline, not estimated from a related number.
2. The instrument is **committed before the result is written up** (R18) — three of these four
   reversals turned on evidence nobody could re-derive.
3. The measurement includes **R17 adversarial probes authored to contain the risky vocabulary**,
   because a clean sweep over an existing corpus is weak evidence, not a green light.
4. Anything built ships under the **§5(d) standing bar**: an answer-level regression check across
   the currently-correct set, never a rank check or a structural guarantee alone.

A ranking in the table below that does not satisfy 1–2 is a hypothesis, and must be labelled one.

## Recommended order, updated after the ship-and-revert and the §8 measurement (2026-08-22)

**✅ ORDERING PRECONDITION SATISFIED (2026-08-22): §8 is settled on the live v16 pipeline.** It was
the item deciding whether the generation ceiling is real. Measured answer: **mostly it is not** —
three of the eight rows are routing misses, one (`nat_33`) is a capability gap, and the model
handled every fact-shaped row correctly once retrieval succeeded. Items below are now actionable on
measured evidence. **Nothing here has been started; each remains a separate go-ahead.**

**⚠️ ITEMS 1 AND 2 SWAPPED (2026-08-22), on the measurement, not on preference.** §2 led this list
on a provisional ~5–6 of 8 produced by an uncommitted harness. Measured: §2 alone is **4–5 of 8**,
the routing extension takes it to **6–7 of 8**, and **three of the eight rows are routing misses**
with a fix pattern this project has already executed successfully (D-DECOMP-1, GUARD A, the
applicability arm, the concord classes). The routing extension is now the lead item. This is
reversal #4 in the table above.

1. **The routing/decomposition extension is now the LEAD item.** It is NOT retrieval work and does
   not belong to this ADR — it is owned by `chike/routing.py` / `chike/decomposition.py` /
   `chike/orchestrator.py` — but it outranks everything here on measured yield, so this ADR defers
   to it rather than competing with it. **Scoped in its own section below (§9); nothing built.**
2. **§2 (routing intercept)** — named for what it actually is: closes retrieval for 8 known rows,
   measured to convert **4–5 of them to CORRECT** per §8, not all 8, and **lower than the ~5–6 it
   was ranked on**. Not a guard for §5 (§5 is declined outright) — evaluated on its own
   bounded-blast-radius merit. Needs its own R17 adversarial-probe pass per key before shipping,
   and **must ship under the §5(d) standing bar**: an answer-level regression check across the
   currently-correct set, not just a rank check on the 8 target rows, before it is called safe.
   **Overlaps item 1 and should be re-costed after it** — if the routing extension lands first,
   several of §2's target rows reach an engine without any allowlist entry, and §2's remaining
   yield is smaller than 4–5 of 8.
3. **A new BRELA rules-engine module (`nat_33`)** is the smallest of the three §8 gaps — same
   shape as `sdl.py`/`nssf.py`/`wcf.py`, one flat rate times a stated duration — but still a
   capability the codebase doesn't have today, not a routing fix. Separately scopeable.
4. **§1 folds into the next regen**, independent of §2 — content fix, tooling already exists, and
   like §2 it changes only the rows it targets rather than reshaping general retrieval. Same
   standing-bar requirement applies.
5. **§5 (general fusion, any variant) is closed for now.** Not because the structural argument in
   (c) was false, but because it answered the wrong question (does the target's rank survive?)
   instead of the one that matters (does everything else stay stable?). Do not re-propose RRF,
   weighted, or interleave without first designing a measurement that checks full injected-set
   stability across a broad sample, not just target-fact rank on the known-buried rows.
6. **§6 (re-ranking) only after §1/§2**, and only with the blast-radius caveat above tested first
   — do not assume it is safer than fusion just because it wasn't the mechanism that just broke.
7. **§7 not scheduled.**

**Nothing above is authorized to build without a separate go-ahead — including items 2 and 3,
which are named here for the first time but not scoped in the depth §1–§7 received.** §5 was
built, deployed, and reverted this round under an explicit go-ahead; §8 was measured (not built —
`run_forced_facts` was removed after use) under this round's go-ahead to investigate, not to ship.
