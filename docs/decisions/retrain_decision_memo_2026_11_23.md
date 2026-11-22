# RETRAIN DECISION MEMO — 2026-11-23 (read-only; nothing deployed, nothing sent to Hugging Face)

**Recommendation: do NOT retrain adapter v15 now.** The evidence is below, every figure points at a committed artifact, and the three places where my first reading was wrong are named in §8.

Read with the standing entry `PROGRESS.md` "DECIDED 2026-09-24 — DO NOT RETRAIN"; this memo re-asks that question on the population the founder named and finds the decision stands, with one important exception (§4) and one new reason (§5).

Evidence arms (committed before this memo cites them, R18):
`eval/controls/retrain_memo_coverage_2026_11_23.py` → `eval/results/retrain_memo_coverage_2026_11_23.json` (replay of every logged MODEL reply through today's orchestrator) and
`eval/controls/sweep_training_sdl_exemptions_2026_11_23.py` → `eval/results/sweep_training_sdl_exemptions_2026_11_23.json` (the SDL-exemption rows of the live training export, all 27 read).

---

## 1. The population

**The 23** is the record's figure and it is right: PROGRESS 4ab lists the 23 MODEL rows that remained on the model after four were taken off it — **025, 029, 044, 048, 071, 085, 127, 155, 162, 163, 174, 183, 187, 237, 301, 302, 304, 324, 332, 375, 383, 388, 390** — from the gate `c2143c0` adjudication (`eval/results/gate_c2143c0_adjudication_2026_11_16.json`, MODEL 26 = these minus 029 plus 229/239/348/355). That adjudication is also the latest full gate: **no gate has run since 2026-11-16**, so every route and guard built since is measured by targeted live checks only (R12c), not by the gate.

Plus this week's cases where the model contradicted a row served at rank 1–3 (verbatim replies from the committed live artifacts, `sdl_nssf_deploy_live_2026_11_23.json`, `exemptions_nhif_deploy_live_2026_11_23.json`, `widened_exemptions_live_2026_11_23.json`).

## 2. Is each covered live today?

Method: the real `Orchestrator`, a stub backend that returns the **stored** model reply for every model call, production's OOC list. ROUTE = the question now reaches a model-free route (the reply is never produced again); GUARD = the question reaches the model and a guard changes or replaces the stored reply; OPEN = it reaches the model and the stored reply comes out unchanged. *Approximation:* on the compute path the slot extractor's model fallback also receives the stored reply, so ROUTE/GUARD are what the code does and OPEN is an upper bound on "not covered".

**The 23 (gate `c2143c0`): 1 ROUTE (388), 1 GUARD (302), 21 OPEN.** (Of the full 27 replayed: 4 ROUTE, 2 GUARD, 21 OPEN. ROUTE = 229, 239, 348 — taken off the model at 4ab — and 388, now; GUARD = 355, taken off at 4ab, and 302, now.)

**This week (9 cases): 6 ROUTE, 3 GUARD, 0 OPEN.**

| case | live defect (the model's reply) | covered by |
|---|---|---|
| private-school SDL | "Shule binafsi zenye wafanyakazi 10+ zinatozwa SDL" (wrong YES) | `sdl_exemptions` statement, 0 model calls |
| exemption list | fabricated list ("TRA Act No. 9 of 2015", "under 18", farms "with 10+") | same statement |
| "Nani amesamehewa SDL?" | a non-answer | same statement |
| mining SDL | invented "msamaha maalum chini ya Sheria ya Madini" | same statement (widened) |
| NHIF with NSSF | NSSF answered, NHIF unaddressed | NHIF append line (model-free route unchanged) |
| household SDL premises | "inalenga eneo la biashara" | D-FIDELITY-27, `replaced` |
| age-60 stops / "180 months" | invented cut-offs | D-FIDELITY-28, `replaced` |
| **"adhabu" sentence** | "Ni adhabu kwa mwajiri kuajiri wafanyakazi wengi bila kusajiliwa" | **`sdl_payer` statement, built and live today** (build `a67462c`) |

⚠️ **Two live defects found today by reading, on routes I vetoed on purpose** (`eval/results/sdl_payer_live_2026_11_23.json`, rows 12 and 13): *"Mfanyakazi analipa SDL wapi?"* → **"Mfanyakazi anachangia SDL … Ni jukumu la mwajiri kukata 3.5% ya mishahara ya mfanyakazi"** (wrong: the exact false belief `sdl_payer` exists to correct; the veto sent a question with a false presupposition to the model, which confirmed it); and *"SDL na NSSF zinakatwa kwa mfanyakazi?"* → **"Mfanyakazi hakatiwi chochote katika SDL au NSSF"** (wrong for NSSF: the employee's 10% IS deducted). Both are model-path, both pre-existing, neither fixed here. **D-FIDELITY-26 and D-FIDELITY-25b have still never fired live** (guards seen across 19 replies: none).

## 3. What remains uncovered (the 21 OPEN)

By the adjudication's own notes (my grouping, not re-adjudicated today): **wrong base / inverted party** 025, 044, 048, 375; **invented specifics** 071, 163, 174, 183, 301, 304, 085, 162; **polarity on a negated or compound premise** 332, 390; **a wrong constant that a statement could carry** 127 (SDL on the 7th, in a compound question), 237, 383 (the no-share-capital fee, row 181 states 500,000), 085 (late penalty vs the filing fee); **thin or time-bound** 155 (the enforcement exercise ended 8 Oct 2025), 187; **compute with an added fabrication** 324; **other** 029. Of the 21, the adjudication marked the governing fact as present in the index for 15 ("idx_checked: yes") and unchecked for 6. **Rank has not been measured for any of them, so some may be retrieval work** (step-zero rule); I have not measured it here.

**Much of this remainder is constants.** The cheapest lever this project has found, repeatedly and again today, is a model-free statement route for a constant (PROGRESS 4bh): this week it fixed every specimen it was pointed at, in one window each, with zero model calls, and could not be walked past by a rephrasing. About eight of the 21 look routable on that reading.

## 4. Would retraining adapter v15 on the repaired training data fix the remainder?

**Plausibly for one class, not for the class that remains.**

1. **No training row carries retrieved context.** Of **3,936 rows in `datasets/tier1a/sft/train_sft.jsonl`, 0 have a non-empty `input`**, every row has the same 296-character system prompt, and `train_ddp.py:327-329` would prepend a `Context:` block if one existed. **The adapter has never been trained to use served facts**; it was trained to answer from its own weights, and production then serves it facts. The failure that dominates the 21 — *the model contradicts a row it was handed* — is a context-following failure. Retraining on the same Q→A format, even fully corrected, teaches the model the corrected claims *as parametric recall*, which is the capacity the 2026-07-03 finding already said is exhausted ("r=64 reliably stores ~100–150 facts; we have 200+") and which competes with context rather than deferring to it. A retrain that addresses the remainder needs a **different corpus format** (question + retrieved rows → faithful answer). That is corpus construction, not "retraining on the repaired data".
2. **The 2026-09-24 measurement stands:** of 7 distinct rows where the fact reached the model's context and the answer was wrong, 0 were explained by what the corpus corrections changed (`retrain_case_2026_09_24.json`).
3. **The exception, and it is real:** for SDL exemptions the training data DID carry the defect. **13 of the 27 SDL-exemption rows in the live export assert something the Act or the held sources do not support** — and **row 1836 teaches the school wrong YES verbatim** ("Shule na vyuo binafsi … vinaweza kutakiwa kulipa SDL", where registered educational institutions are exempt), and the live wrong reply mirrors it. Rows 2444 and 2645 also list a private school among SDL payers; **965, 1227, 1416, 2041, 3447** assert or suggest an EPZ/SEZ SDL exemption for which **no held source says anything** (the statement route deliberately vetoes EPZ/SEZ for exactly that reason); **400 and 3792** invent an application and annual-proof process; 257 and 740 and 1545 overstate. So the model's school error is *at least partly a training-data defect* — and **that class is already fixed live by a statement at zero cost**, so a retrain's marginal benefit on it is ~nil.

## 5. What the "repaired" data still contains that is wrong or unverified

- **The SDL-exemption rows above (13 of 27)** — corrected facts landed on 2026-11-23, *after* the last precondition declaration. This is the same arc as the 2026-10-05→10-07 reversal: the "MET" in `retrain_precondition_rederived_2026_10_08.json` (17 defect classes, polarity-aware) is **stale on its own terms** — it knows nothing of the licence-expiry correction (2026-11-17, six layers), the WCF accident-trigger quarantine (2026-11-16), the SDL exemption categories, age-60, or the TIN window. **I did not re-run it**: it regenerates the export with `generate_sft.py`, which writes, and this memo is read-only. Re-running it is the first step of any retrain.
- **What this memo's own sweep could not check:** it keys on SDL + an exemption word (a lower bound, R21). My other claim-keyed sweeps of the export found 0 rows for: licence expires 30 June, SDL deducted from the employee, NSSF stops at 60, a 180-month cut-off, "premises" scope, an NHIF figure, the invented "adhabu" sentence. Zero is a lower bound, not a clean bill.
- **Over-removal has been examined for only 51.3% of quarantine removals** (257 of 501 carry a verdict; **244, i.e. 48.7%, are unexamined**, `overremoval_by_class_2026_10_08.json`): the export may have lost correct rows, and a retrain would inherit that silently (R37).
- **Eval gold keys and the clarification scoring policy** still understate A2 by up to ~4 points (4z: 28 of 76 misses were GOLD); a retrain judged on that gate inherits the same bias.
- **Source editions:** 52 of 61 cached sources were `UNDECLARED` at the time of the edition audit (the current count was not re-measured here); a fact's `status` is not its evidence (R29 mode 3).

## 6. Cost and time of a retrain on Kaggle

Recorded in the repo: r=128, α=128, lr 2e-5, **1 epoch**, batch 1 × 8 accumulation, max_seq 2048, cosine, warm-start from v14-lora; **3,936 rows ≈ 492 optimizer steps on one GPU** (≈246 across two). **The repo records no wall-clock time or GPU-hours for any training run, and I will not invent one**; the first thing a retrain plan needs is that measurement from the founder's last Kaggle session. Fixed costs that ARE recorded: the **full gate ≈ 100 minutes of GPU** plus the judge ($0.21 for 361 rows, R12b), a **hand adjudication of the disagreement queue** (≈76 rows at the last gate), and a **Kaggle regen** if the index moves. Kaggle's own quota is a platform limit I have not verified from anything held here.

## 7. Risks (regressions the gate would have to catch)

- **The gate cannot resolve a small effect.** 400 rows: one question = 0.25 points; the judge moved on ~4 unchanged-text rows between the last two gates, ≈1 point of variance on its own; the regex headline overstates by ~3. A retrain whose realistic effect is a handful of rows is not distinguishable from noise (the 2026-09-24 granularity finding, unchanged).
- **A retrain moves everything at once** (weights), so a regression is unattributable and a gain is unattributable (R12c). Model-free routes and guards move one named row each.
- **The same-format retrain can *worsen* context-following** by strengthening parametric answers against served rows — the shape of today's two new defects, where a confident parametric prior beat the correct fact. No instrument here measures it before the gate.
- **A retrain invalidates every targeted live check and every guard's pricing.** The guards (D-FIDELITY-1…28) were each priced on stored replies of the *current* adapter (R19/R37); a new adapter has new replies and the prices are void.
- **Corpus stage mismatch (R36):** a quarantine that does not reach `sft/` has not removed anything — the export must be regenerated and re-swept before any training, and was stale once already.
- **The `unsupported_figure` flag, D-FIDELITY-26 and 25b are unproven live**; a retrain adds a second unproven layer.

## 8. Where my first reading was wrong (kept, so the next reader sees it)

1. I read "the 23 from the gate" against the adjudication's 26 and the false-pass queue's 23 and first wrote that the figure was a coincidence of the queue size; **PROGRESS 4ab lists the 23, and the figure is the founder's and correct** (26 − 4 + eval_029). The harness docstring says so.
2. My first payer-route cue (bare `mfanyakazi` / `mshahara`) hijacked **~30 sweep questions** (compute base, disability, benefits in kind, headcount); narrowed before commit.
3. A first splice of the exemptions veto left an empty regex alternative (`makato||`) that **vetoed every exemptions question** — shown by my own sweep reading "exemptions 18 → 0", which is the instrument working; fixed and pinned by a test (`test_patterns_contain_no_control_characters_and_no_empty_alternative`).

## 9. Recommendation, with the evidence behind it

**Do not retrain now. Do these first, in this order; each is cheaper than a retrain and each has measured yield.**

1. **Statement routes for the remaining constants** (about eight of the 21 look routable; not yet verified one by one), and a **narrow fix for the two new payer-adjacent defects** (rows 12/13 above: a presupposition-correcting statement for "an employee pays/is deducted" questions even when a where/how cue is present, and an SDL-and-NSSF party composite). *Evidence:* four of this week's specimens moved off the model in one window each; the standing lesson (PROGRESS 4bh).
2. **Repair the training corpus** — the 13 SDL-exemption rows first, then re-run the precondition re-derivation (needs a write; ask first) and the over-removal audit's unexamined 244. *Evidence:* §5. This is needed for ANY future retrain and has value only then.
3. **Run one full gate on the current build as a BATCH baseline** (R12c: many changes have landed since 2026-11-16 — the legitimate use of the instrument), adjudicate the queue by hand, and recount the MODEL class. *Evidence:* the 21-OPEN figure is a replay on a stub; only a gate says how many the live model still gets wrong.
4. **Decide on a retrain only against that fresh count, and only in a context-conditioned format.** If the post-routes MODEL remainder is ≲10 rows, the retrain cannot be told apart from noise (§7) and is not worth its cost; if it is larger *and* the rank-1–3 contradictions persist, the case to make is for **context-conditioned SFT pairs**, a corpus-construction project of its own, not a re-run on the repaired Q→A data.

**What would change this recommendation:** a measured wall-clock for a v15-sized run (cost); a fresh gate showing ≥20 MODEL rows that no route can carry (benefit); or evidence that context-conditioned pairs raise faithfulness on a held-out set of contradictions authored before the data (R21/R33).
