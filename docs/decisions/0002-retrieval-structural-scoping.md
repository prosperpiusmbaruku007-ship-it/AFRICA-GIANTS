# ADR 0002 — Retrieval structural scoping: five candidate mechanisms, two measured

- **Status:** Interleave (§5) shipped, live-regressed on one of its own protected rows, and
  reverted the same day (2026-08-22) — production confirmed back on pre-ship code. The ship
  decision itself is now understood to have rested on a false distinction (§5(d)): rank-level
  measurement cannot certify answer stability. A standing bar for future retrieval ships is
  recorded in §5(d). General fusion (RRF/weighted/interleave) is DECLINED in all forms; §2
  (routing intercept) is the leading candidate, named explicitly as a small fix for 6 known fact
  keys, not a general retrieval solution. §8 (generation-side failure ceiling) is now MEASURED,
  not just discovered: forcing the correct fact(s) into context for all 8 remaining rows produced
  4 correct, 1 partial, 3 clearly wrong — retrieval is a binding constraint for most of these rows
  but not all of them, and §2's expected real yield is revised to ~5 of 8, not 8 of 8. §1/§6/§7
  remain scoped-only, not built.
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

**The failures cluster on a clean, nameable property: arithmetic/multi-fact synthesis, not simple
lookup.** The 3 clear failures (`nat_23`, `nat_24`, `nat_33`) all require either applying a
percentage to a given amount, multiplying a monthly penalty by a stated number of months, or
merging two-to-three distinct obligations into one complete reply. The 4 clear successes
(`nat_44`, `nat_45`, `nat_41`, `nat_28`) are single-fact statements or two facts presented side by
side with no arithmetic between them. `nat_05` (partial) needs an inferential move (recognize the
given figure is the wrong base) rather than arithmetic, and got the recognition right without
closing the loop. **This is not retrieval's problem, and no mechanism in §1–§7 can fix it** — it
sits in generation/decomposition, downstream of a successful retrieval, and needs its own
investigation (why does the model drop facts or refuse to compute when multiple obligations are in
play) before it can be sized precisely. What's now known is its approximate SIZE on this sample:
roughly a third of the remaining known-buried rows.

**Consequence for §2's expected yield:** the routing intercept (§4) closes retrieval for all 8
known rows by construction, but this measurement predicts it converts roughly **5 of 8 to
CORRECT, not 8 of 8** — `nat_23`, `nat_24`, and likely `nat_33` should be expected to remain wrong
or partial after §2 ships, for reasons the intercept cannot touch. Report it that way when §2
ships: partial success against its own target set, not a clean sweep.

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

## SUMMARY (updated 2026-08-22, post-ship-attempt)

| # | mechanism | status this round | priority |
|---|---|---|---|
| 5 | Hybrid lexical+dense fusion (RRF/weighted/interleave) | **SHIPPED (interleave), LIVE-REGRESSED, REVERTED.** Target-fact rank preservation held for all 8 rows tested; the OTHER two injected slots changed for all 8 anyway, and one (`nat_32`) flipped to a wrong live answer. Neither RRF's nor interleave's real blast radius (answer stability, not rank) was ever fully enumerated — interleave's was wrongly assumed zero. | **DECLINED, all forms** |
| 2 | Routing-layer fact intercept | **SCOPED, purpose named honestly:** a hand-maintained allowlist that closes 6 known fact keys / 8 known rows and nothing else — not a general retrieval fix, no broader version escapes that ceiling. Leading candidate because it's the only mechanism here with a *provably* bounded blast radius (explicit cue match short-circuits RAG; everything else untouched — no fusion variant could claim that after §5(d)). **Expected real yield per §8: ~5 of 8, not 8 of 8.** | **HIGH, as a named small objective, not a solution to retrieval** |
| 1 | Fee-shape rows rewritten at index-content level | scoped only, unchanged. Same §8 ceiling applies — closing retrieval for `nat_23`/`nat_24`/`nat_33` won't make them correct. | HIGH (folds into next regen) |
| 6 | Re-ranking (cross-encoder) | scoped only, unchanged — flagged that it likely shares §5(d)'s blast-radius problem (re-scores every query's shortlist) and needs its own explicit old-vs-new test before being assumed safer | MEDIUM |
| 7 | Different/bigger embedding model | scoped only, unchanged — this is what R15 was | LOW, not scheduled |
| 8 | Generation-side failure after successful retrieval | **MEASURED** (`ChikeModel.run_forced_facts`, temporary/removed): forced the correct fact(s) into context for all 8 remaining rows. **4 correct, 1 partial, 3 clearly wrong (`nat_23`, `nat_24`, `nat_33`) despite exact facts present.** Failures cluster on arithmetic/multi-fact synthesis, not simple lookup. Also closes a gap in the pilot-safety floor: these failures carry maximum retrieval confidence and no visible hedge, so no retrieval-confidence floor could ever catch them. | Root cause (why generation drops facts / declines to compute) needs its own investigation, outside this ADR's scope |

## Recommended order, updated after the ship-and-revert and the §8 measurement (2026-08-22)

1. **§2 (routing intercept) is the priority**, named for what it actually is: closes retrieval for
   8 known rows, expected to convert **~5 of them to CORRECT** per §8, not all 8. Not a guard for
   §5 (§5 is declined outright) — evaluated on its own bounded-blast-radius merit. Needs its own
   R17 adversarial-probe pass per key before shipping, and **must ship under the §5(d) standing
   bar**: an answer-level regression check across the currently-correct set, not just a rank check
   on the 8 target rows, before it is called safe.
2. **§1 folds into the next regen**, independent of §2 — content fix, tooling already exists, and
   like §2 it changes only the rows it targets rather than reshaping general retrieval. Same
   standing-bar requirement applies, and the same §8 ceiling: expect it to help `nat_44`-shaped
   rows, not `nat_23`/`nat_24`/`nat_33`-shaped ones.
3. **§5 (general fusion, any variant) is closed for now.** Not because the structural argument in
   (c) was false, but because it answered the wrong question (does the target's rank survive?)
   instead of the one that matters (does everything else stay stable?). Do not re-propose RRF,
   weighted, or interleave without first designing a measurement that checks full injected-set
   stability across a broad sample, not just target-fact rank on the known-buried rows.
4. **§6 (re-ranking) only after §1/§2**, and only with the blast-radius caveat above tested first
   — do not assume it is safer than fusion just because it wasn't the mechanism that just broke.
5. **§7 not scheduled.**
6. **§8's root cause is the next open question, and it now sits ahead of §1/§2 in importance even
   though it isn't retrieval work**: why does generation drop a fact or decline to compute when 2–3
   obligations are in play, on `nat_23`/`nat_24`/`nat_33`-shaped questions specifically? That
   investigation determines the real ceiling of the whole workstream, not just these 3 rows — if
   it's a general multi-fact/arithmetic weakness, it likely affects rows outside this specific
   nine-row set too.

**Nothing above is authorized to build without a separate go-ahead.** §5 was built, deployed, and
reverted this round under an explicit go-ahead; §8 was measured (not built — `run_forced_facts`
was removed after use) under this round's go-ahead to investigate, not to ship.
