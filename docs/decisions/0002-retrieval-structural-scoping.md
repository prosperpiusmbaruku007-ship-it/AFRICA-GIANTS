# ADR 0002 — Retrieval structural scoping: five candidate mechanisms, two measured

- **Status:** Scoping + one measurement complete (2026-08-22). No mechanism shipped. Two items
  (#5 measurement, #2 scoping) executed per founder go-ahead; #1/#3/#4 remain scoped-only.
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

**Revised recommendation, given the §5 measurement below:** not a standalone structural fix —
demote from "HIGH, complementary" to **a targeted safety net that pairs with #5**: use this
intercept specifically to pin the currently-correct exact-match rows (`nat_31`, `nat_32`,
`nat_34` — see §5) so they are immune to RAG re-ranking noise, *before* any general hybrid
fusion is turned on for everything else. That directly neutralizes the one measured cost §5
found. Priority: **MEDIUM, scoped as a dilution guard, not a general lever.**

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

---

## 6. RE-RANKING (cross-encoder) — scoped only, unchanged from original scoping

Named as a design direction by the similarity-floor scoping (2026-08-16: top-1 scores
0.790–0.859, failing-row correct-fact scores 0.765–0.809 — no absolute threshold separates them)
but never built or measured. Cost: a small multilingual cross-encoder on the existing T4
container, cheap relative to the 8B model's dominant latency (7.3s median), but requires a new
harness and a new model dependency. **Priority: MEDIUM**, below §5 now that §5 has an actual
positive, costed measurement and this does not.

---

## 7. A DIFFERENT / BIGGER EMBEDDING MODEL — scoped only, unchanged

This is not a fresh idea — it is what R15 already was (384-dim → e5-base 768-dim, yield +1/48,
fee-shape dominance unchanged). The failure mode described in §3 is about surface text shape, not
encoder capacity; no evidence held predicts a bigger model changes which rows win. **Priority:
LOW. Not scheduled.**

---

## SUMMARY (updated)

| # | mechanism | status this round | priority |
|---|---|---|---|
| 5 | Hybrid lexical+dense fusion (RRF/weighted/interleave) | **MEASURED** — RRF recovers 4/8 known-buried rows (one from rank 94) at a cost of 3 named live regressions; interleave recovers 3/8 at zero measured dilution | **HIGH** |
| 4 | Routing-layer fact intercept | **SCOPED**, disanalogy to compute-path named honestly — it's a hand-maintained allowlist, coverage ceiling = known failures only | MEDIUM (as a dilution guard for §5, not standalone) |
| 1 | Fee-shape rows rewritten at index-content level | scoped only, unchanged | HIGH (folds into next regen) |
| 6 | Re-ranking (cross-encoder) | scoped only, unchanged | MEDIUM |
| 7 | Different/bigger embedding model | scoped only, unchanged — this is what R15 was | LOW, not scheduled |

## Recommended order, updated after this round's measurement

1. **Ship-decision needed on §5+§4 as a pair**, not on §5 alone: pin `nat_31`/`nat_32`/`nat_34`
   (and any other rank-1 exact matches at risk) via a routing intercept, THEN re-measure RRF's
   dilution count with that guard in place. If dilution drops to ~0 with the guard, RRF recovering
   4 of 8 known-buried rows — including one from rank 94 — is the strongest single result this
   whole retrieval cycle has produced.
2. **§1 folds into the next regen** regardless of §5/§4's outcome — independent content fix,
   tooling already exists.
3. **§6 (re-ranking) only if §1/§4/§5 leave rows unresolved** — `nat_24` (91→37 under RRF, still
   the deepest holdout) and `nat_28`/`nat_44`/`nat_45` (improved but not crossing top-3 under any
   strategy tested) are the likely remaining candidates.
4. **§7 not scheduled.**

**Nothing above is authorized to build yet beyond the §5 measurement already run.** A ship
decision on §5+§4 needs a separate go-ahead, same discipline as the rest of this document.
