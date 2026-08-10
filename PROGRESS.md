# Africa Giants — Project Progress

Last updated: 2026-08-10

**🚀 v16 IS LIVE IN PRODUCTION (2026-08-09, `ec9cbb3`).** The router + rules engine +
orchestrator pipeline now serves every request. Cutover entry immediately below — deployed
commit, the two gate results that authorised it, and the rollback procedure.

**➡️ QUEUE (founder-ordered, 2026-08-10): th_16 → D-FIDELITY-1 widening → VAT/EFD compute
route.** SAFETY-3's investigation is done and is written up below; the fix was approved for VAT
and EFD only, staged. **th_16 is DONE and live** — see the entry immediately below. Minimum-wage
sector rates and unit normalisation are separate investigations, not part of the route.

**Two findings from this cycle outrank the wiring itself and are written up as their own
entries: CONTAINER-PATH-1** (wiring v16 with defaulted phrase lists would have silently
reopened SAFETY-1 — 39 OOC phrases instead of 107, invisible to every offline instrument;
second occurrence of R16's class) **and the STANDING LIMITATION** (the regex gate positively
credits eval_318 and eval_320, the two worst defects the cycle found — which is why the judge
overlay is now mandatory).

## ✅ th_16 FIXED AND LIVE — "paying above the minimum wage is illegal" (2026-08-10)

The worst answer this project has produced, and the only SAFETY-3 finding taken out of order.
Production told an employer paying a farm worker TZS 200,000/month:

> *Hapana — malipo hayo yanazidi **kiwango cha juu cha chini** cha lazima cha kisheria … mfanyakazi
> wa shamba anaweza kulipwa kiwango cha chini cha TZS 175,000 **tu**. **Malipo ya ziada juu ya hapo
> ni kinyume cha sheria.***

"Kiwango cha juu cha chini" — a *maximum-minimum* — describes nothing that exists in Tanzanian
law. **It reproduced in two independent runs** (`edge20_v16_run1_prefix_67e9e4c` and
`edge20_v16_run2_3144a98`, row 17, plus the SAFETY-3 probe), so it was never sampling noise.

### The cause was an ABSENT fact, not a wrong one — and that changed the fix

The SAFETY-3 report attributed the VAT inversion to generation-with-the-fact-present. That
diagnosis does **not** carry over here, and assuming it would have produced the wrong remedy.
Offline reproduction of production retrieval (`scratch/mw_retrieval.py`, same e5-base, same
`query: ` prefix, same live index) found:

| | result |
|---|---|
| realistic Swahili minimum-wage queries retrieving **any** GN 605A fact | **0 of 7** |
| rank of the best GN 605A fact on those queries | **#22 – #52** |
| the same instrument on eight other domains | **7 of 8 at rank 1** |
| the one minimum-wage query that *did* work | `GN 605A ilianza kutumika lini?` — because it names the notice |

The reproduction is exact, not approximate: its top-3 for the edge20 row-17 question matched
that run's recorded `facts_retrieved` **in the same order**, including the three irrelevant
facts (NSSF, PAYE, VAT deferment) that the model was actually given.

**GN 605A was in the index only as long English `key: value` text keyed on the notice number.**
It answered the one question that names it and nothing a user actually says. This is precisely
the failure mode the R15 note already warns about — *"short Swahili-first text with the value at
the front retrieves far better than a long English fact"* — reaching a domain nobody had swept.

**A disproved hypothesis, recorded because it was tested:** instrument 1 saw `file search fee:
3,000 TZS` rank top-3 on a wage query, which looked like the source of SAFETY-3's unexplained
fabricated *"TZS 3,000 minimum"* WCF answer (th_22). Checked directly — **no**, that fact is not
retrieved for th_22's question. The fabrication remains unexplained and stays logged.

### Verified against the gazette itself, not a summary

TanzLII is behind a Cloudflare challenge from this network (403, same class as the Groq/Cerebras
blocks). The official PDF was instead downloaded from **kazi.go.tz** — Tier 1A whitelist —
*Special Supplement No. 9 to Special Gazette No. 6 Vol. 106, 13 Oct 2025*, and read paragraph by
paragraph. **Paragraph 4(3):**

> *"The minimum wage rates specified in the Second Schedule shall be regarded as the minimum wage
> payable to employee in the respective sector or area, **and an employer may pay such employee an
> amount above the minimum wage prescribed** in respective sector or area."*

Also confirmed: para 4(4) (more favourable terms via contract or CBA), para 6 ("Persons enjoying
better terms"), para 7 revoking **GN No. 687 of 2022** by name, and the entire Second Schedule.
Every sector rate already in `locked_facts.json` verified against the gazette — **no corrections
needed**, and "16 sectors, 46 sub-sectors" reconciles exactly (46 lettered sub-sectors + 4
unlettered sectors = 50 rate rows).

### One fact, not two — decided by measurement

The obvious shape was two entries: floor semantics + the agricultural rate. Benched, that shape
**lost**: with production injecting only `top_k=3` (+1 on numeric queries), the two competed for
the same slots and knocked each other out.

| shape | targets served | evictions |
|---|---|---|
| split, full B | 6/8 | 0 |
| split, short B | 6/8 | 0 |
| split, narrow B | 4/8 | 0 |
| **merged (shipped)** | **7/8** | **0** |

The wording was iterated offline through four variants before anything was written to disk,
which was only possible because of a side finding: **R15's Kaggle round-trip is no longer
required.** e5-base is now in the local HF cache, and re-embedding the current 217 committed
texts locally reproduced the live index at **cosine 1.000000 on every fact**
(`scratch/mw_regen_control.py`). R15 step 1's stated reason — *"local network blocks e5-base
download"* — no longer holds. The rule should be amended; the *verification* steps stay.

### R17 applied to both halves

The shipped entry is deliberately loaded with generic wage vocabulary (*namlipa, nampa,
mfanyakazi, mshahara, kwa mwezi, inaruhusiwa, ni sawa, nakiuka sheria*) — exactly the words in
almost every payroll question this system answers. A clean sweep would have proved nothing, so
**22 in-scope payroll probes were authored to contain that vocabulary while needing a different
fact** (`eval/accuracy_gate/minimum_wage_floor_probes_030.jsonl`, 8 targets + 22 displacement
probes, `guards_against` per row, wired to `tests/test_minimum_wage_floor.py`).

The `wrong_patterns` got the same treatment: swept over **149,983 stored strings** for false
positives (**0** — every match was the defect itself or a note describing it), then given
authored probes for the *legitimate* phrasings they could plausibly catch — "kiwango cha juu
zaidi cha mshahara wa chini" (the highest minimum rate, which eval_120/eval_382 both ask for).

### Result

| check | result |
|---|---|
| self-retrieval on the new fact's own subject vocabulary | **3/3** |
| target queries served on the regenerated index | **7/8** (t_hotel is a documented miss) |
| evictions across 30 control + R17 probes | **0** |
| full test suite | **625 passed** |

Artifact: `eval/results/th16_minimum_wage_floor_verification.json`. Index 217 → 218 facts,
`kaggle/` and `chike-inference/` byte-identical.

**t_hotel is an accepted miss, named rather than hidden.** *"Nina mfanyakazi wa hoteli namlipa
TZS 400,000 kwa mwezi, je ni sawa?"* needs the **hotel** floor (375,000 / 225,000 / 195,000 by
star rating), which this entry deliberately does not carry — a fact listing every sector's rate
is the long-English shape that caused the problem. Retrieving the semantics without the rate
would let the model assert lawfulness against a number it does not have. It is listed in
`KNOWN_MISSES` with its reason so a future regression on a *different* target cannot hide
inside a lowered bar.

### Two things this turned up that are NOT th_16

1. **Pre-existing retrieval gaps, not caused by this change** — four of the 22 authored probes
   retrieved no relevant fact on the OLD index either: `p_05` / `p_09` / `p_11` (PAYE deadline,
   PAYE penalty, "can I pay without deducting PAYE") and `p_16` (is the 2022 wage order still in
   force). Recorded per row in the probe file, so the test asserts **non-regression** rather
   than absolute correctness — a test that failed here would be failing for a defect it did not
   cause and cannot fix. **Evidence that retrieval reachability is wider than minimum wage.**
   Own item.
2. **Context noise.** The floor fact is now also injected into **9 of 22** unrelated payroll
   probes. Nothing is evicted, but the build script's own history records an irrelevant injected
   fact changing an answer (two 5M facts beating one 10M). Those nine are the negative controls
   for the live check.

## 🚀 v16 CUTOVER — LIVE IN PRODUCTION (2026-08-09)

**Deployed commit: `ec9cbb3`** (`config(pipeline): v16 — the cutover flip`). Endpoint
`prosperpiusmbaruku007--chike-inference-web-endpoint.modal.run`. Second of the two deliberate
deploys; the first was the credential rotation on v15, so **this deploy carried exactly one
change**.

### What authorised it — both preconditions, measured, not asserted

| precondition | result | source |
|---|---|---|
| ADR 0001 §10 bar: v16 ≥ v15 on raw **and** reliable | **raw +3.6, reliable +1.6** — PASS | `gate_phase_d_paired_1476caa.json`, sha256-verified, 46/46 recomputed checks |
| defective clarification rate ≤5% | **2.9%** (3/102) — PASS | same artifact |

Supporting, from the same run: compute **+13.7 raw / +8.7 reliable**, 19 real gains / 1 false,
6 regressions all of them v16 clarifications, judge range **+5.1 to +7.8 sign-stable**, fact
path **byte-identical on 281 of 282** non-compute scored rows. The headline the decision rested
on — *no row where v16 states a wrong number that v15 stated right* — holds, with the eval_318
correction recorded in the `1476caa` entry.

### Live verification — R16 procedure, judged against pre-registration

`modal app stop chike-inference --yes` first (verified `stopped`, 0 tasks, via `modal app list`
— the command exits 0 silently), then `modal deploy`, then
`scratch/cutover_verify.py` comparing each reply **byte-for-byte** against
`scratch/canary_expected_v16.json`, which was written **before** the cutover.

| # | canary | live sha | result |
|---|---|---|---|
| 1 | **CONTAINER-PATH-1 / OOC** (`kodi ya majengo`, config-only phrase) | `a71619b1` | **PASS** — refuses, and byte-identical to v15's refusal |
| 2 | eval_115 — fact negative case | `5b46098b` | **PASS** — byte-identical to v15 |
| 3 | eval_320 — cross-levy canary | `66aac953` | **PASS** — guard blanked the nssf and wcf bodies |
| 4 | eval_318 — cross-levy canary | `6a314afc` | production correct; **the pre-registered string was wrong** (below) |
| 5 | eval_323 — changed compute row | `3f3fc316` | **PASS** |
| 6 | eval_280 — changed compute row | `57e36a8c` | **PASS** |

**Canary 1 ran first deliberately** and is the most important result: v16 moved phrase-list
loading from `run()` into `Orchestrator`, so a config-only OOC phrase still refusing is the only
available proof that the container reads the baked `chike_config.json` and serves **107 phrases,
not the 39-phrase hardcoded fallback**. CONTAINER-PATH-1 is closed in production, not just in
the source.

**The D-FIDELITY-2 guard fired live on a real user-facing answer, first time out.** eval_318's
contradicting `TZS 110,000` NSSF figure is gone from the live reply; the correct `TZS 1,100,000`
remains.

### 🐛 The one deviation was in the verification harness, not in production

eval_318's live reply did not match its pre-registered string. Verified read-only, before
touching anything:

```
artifact v16 text  MINUS  the SDL body the guard should blank  ==  LIVE   →  True
```

Production produced exactly the designed output. **The expected string was malformed.**
`recover()` in `scratch/canary_expected_v16.py` reconstructs each sub-answer body as the text
*preceding its deterministic working* — so any text after the **last** working is never
captured. That trailing segment is the pooled **fact** sub-answer. eval_318 is the only canary
carrying one, which is why it is the only row affected.

Stopping on the deviation and reporting before acting was the correct call and stays the rule:
a near-miss explained after the fact is exactly what pre-registration exists to prevent.

### ✅ `recover()` FIXED and eval_318 RE-REGISTERED (2026-08-10)

Recovery now lives in **`scratch/render_recovery.py`** and **parses the `_render` grammar**
instead of slicing at landmarks. `rep.sub_answers` gives the exact part count and which parts
are compute; each compute part is `body\n<working>` or bare `<working>`, parts join with
`\n\n`. A small backtracking parse finds the unique segmentation, **reports ambiguity or
no-parse rather than guessing**, and callers assert a **round-trip invariant**: re-rendering
with nothing dropped must reproduce the stored text byte-for-byte.

**Three defects, not one — and the second fix was itself wrong.** Worth recording because the
sequence is the lesson:

| # | defect | direction | how it was caught |
|---|---|---|---|
| 1 | text after the LAST working discarded | truncation | eval_318 false FAIL at the cutover |
| 2 | `find()` anchored on a working occurring **inside a body** — eval_320's model answer contains a line character-identical to the deterministic WCF working | mis-split | only visible once #1 was fixed |
| 3 | *my first fix*: taking the body as the final `\n\n`-delimited chunk | **under-removal** — left eval_320's contradicting `SDL = TZS 28,000` / `NSSF = 160,000` / `PAYE − TZS 26,000` block in the output | eval_320 stopped matching live |

**Defect 3 is the one to remember.** The first fix passed its own self-check cleanly — a
narrow/wide verdict comparison — because narrow and wide bodies both *contained* a
contradiction, so the guard **verdict** agreed while the **extent of removal** silently
differed. An instrument that compares verdicts cannot see a defect in extent. What caught it
was re-running the corrected harness against the **recorded live replies** and noticing that a
row which had previously PASSED now disagreed. **A fix that changes a row which was already
correct is a fix that needs explaining**, and that check is now the habit.

**Verification, all three loops:**

| check | result |
|---|---|
| corrected expectations vs pre-registration | **exactly one row changed — eval_318**; the other five shas byte-identical to what was pre-registered |
| eval_318 corrected expectation, derived from the artifact + guard **without reference to the live reply** | sha `6a314afc` — **exactly the live sha** |
| full live canary re-run against the corrected file | **6/6 PASS**, every row byte-identical |
| `preflight_wiring.py` re-run with the parser | 87/87 workings byte-identical, **0 unrecoverable, 0 round-trip failures**, guard touches exactly eval_318 + eval_320 |

The `1476caa` pre-flight conclusion therefore **stands, and now stands by construction rather
than by luck**: it had compared the *set* of guard-blanked rows and never compared its
`rendered` string to `stored`, so the broken recovery was latent rather than load-bearing.
That is no longer something to rely on — the round-trip assert makes a mis-parse fail loudly.

### 🟢 Production reproduces the harness BYTE-IDENTICALLY

Before the cutover, live v15 was captured on all five canaries
(`scratch/canary_baseline_v15.json`) and matched the `1476caa` artifact's v15 arm **byte for
byte**. After the cutover, five of six rows matched their pre-registered v16 strings byte for
byte, and the sixth matched once the harness bug is accounted for.

**This is the load-bearing fact for every future artifact.** It means a Kaggle paired-gate
number is a *prediction about production*, not merely a lab result — the same weights, config,
generation params and RAG index produce the same bytes on both sides. Any future run where the
live endpoint and the artifact disagree on a canary is a real divergence and must be
investigated as one, because the null hypothesis is byte-equality.

### ↩️ ROLLBACK — a config flag flip, never a code change

1. Set `"pipeline": "v15"` in `kaggle/chike_config.json`.
2. `python -m modal app stop chike-inference --yes` — **required**; warm containers keep serving
   the baked v16 config, and this command prompts and aborts silently without `--yes`.
3. `python -m modal deploy chike-inference/modal_app.py`.
4. Verify per R16 with a request whose behaviour differs between arms — a compute row such as
   eval_323 renders as v15 prose rather than a deterministic working.

The flag **defaults to `v15`** on an absent or unrecognised value, so a malformed config can
never silently promote v16. `modal_app.py` bakes the **local working-tree** config via
`add_local_file`: the committed flag is not the live flag until the next deploy — in both
directions.

### Carried forward from the cutover

- **SAFETY-3 is now user-facing** and is the next work item. The VAT inversion was not live
  under v15 (which never applies the threshold); it went live at this deploy.
- ~~Fix `recover()` in both scratch harnesses, then re-register eval_318~~ — **done
  2026-08-10**, see the section above.
- The standing audit of remaining repo-relative reads inside the Modal image (CONTAINER-PATH-1)
  is unchanged and still open.

**Canary artifacts.** `scratch/canary_expected_v16.PRE_REGISTERED.json` is the untouched
pre-cutover record and is **not** rewritten to match the outcome;
`scratch/canary_expected_v16_corrected.json` is the post-fix version, stamped as such, with a
`differs_from_pre_registration` flag per row. Keeping both is the point — a pre-registration
edited after the fact is not a pre-registration.

**🏁 CYCLE FULLY CLOSED (2026-07-26):** the entire router-investigation + defect-fix cycle is now
closed end-to-end with real GPU confirmation. Follow-up #3's last two threads landed this session:
**work item 2** (round-2 adjudication of the afef9dd 25+7 queue — judge 23/24 = 95.8%, zero new engine
defects, commit `f195c23`) and **D-FIDELITY-1** (model body contradicting the deterministic compute
working — shipped `75421f0`, GPU-confirmed: 3 target rows corrected + judge 5/5, single fully-explained
eval_378 scorer-artifact flip, zero collateral). Two non-blocking follow-ups logged for later
(SCORER-SEMANTICS-1: credit "TZS 0"/not-applicable answers; JUDGE-NONDET: eval_397). See the
D-FIDELITY-1 and work-item-2-round-2 entries below.

## 🏁 PHASE D BATCHED RUN (1476caa) — ADR BAR PASSES; THE RESIDUAL REGRESSION CLASS IS GONE (2026-08-09)

Artifact: **`eval/results/gate_phase_d_paired_1476caa.json`** — fetched from HF
(`prospAprospA007/africa-giants-dataset`) and **sha256-verified**
`65015f060be37ef4c2208bce59952e61ab064e2fb35e939a81f8ae68a8e32ea1`, 1,022,937 bytes,
`complete: true`, `clone_head == live_head == 1476caa`, 400 questions, 217-fact index.
**Every number below was recomputed from the raw `v15_results` / `v16_results` / `part3_results`
rows independently of the summary block: 46 checks, all 46 matched.** Harness
`scratch/recompute_1476caa.py`.

This is the run the batched decision (founder, 2026-08-08) was waiting for: C1–C4 **plus** D and
F1/F2 together, measured on the configuration that would actually be wired, rather than on an
intermediate.

### Headline

| | 3ac522a | 030a5ff | 5d0dcb7 | **1476caa** |
|---|---|---|---|---|
| ADR bar raw | −6.8 **FAIL** | +0.5 | +1.3 | **+3.6 PASS** |
| ADR bar reliable | −3.7 **FAIL** | +1.1 | +0.8 | **+1.6 PASS** |
| compute raw / reliable | −29.4 / −23.0 | −2.0 / +4.0 | +4.9 / +5.0 | **+13.7 / +8.7** |
| gains / regressions | 11 / 37 | 19 / 17 | 17 / 12 | **20 / 6** |
| defective clarification rate | — | — | 9.8% | **2.9%** (target ≤5%) |

Per bucket (raw, then reliable):

| bucket | n | raw v15 | raw v16 | Δ | rel v15 | rel v16 | Δ |
|---|---|---|---|---|---|---|---|
| fact_path_190 | 193 | 158/184 | 158/184 | **0.0** | 111/130 | 111/130 | **0.0** |
| staged_50 | 50 | 38/50 | 42/50 | +8.0 | 31/39 | 33/39 | +5.1 |
| compute_type | 103 | 70/102 | 84/102 | **+13.7** | 36/53 | 46/60 | **+8.7** |
| adversarial_150 | 150 | 98/144 | 108/144 | +6.9 | 65/89 | 73/96 | +3.0 |
| **ALL_400** | 400 | **300/384** | **314/384** | **+3.6** | **212/263** | **222/270** | **+1.6** |

### The v15 arm was CACHED — and the cache was verified in full, not on the harness's 60 rows

`1476caa` cached the v15 arm from `5d0dcb7` behind a 60-row determinism check rather than
regenerating 400 GPU rows. **All 400 rows were re-verified offline here: 0 generated-text
differences and 0 pass-verdict differences against the `5d0dcb7` artifact.** The caching commit
is sound, and the v15 baseline is byte-identical for the **fourth** consecutive run — so no
sampling-noise defence exists for any v16 movement.

The judge verdicts on that cached arm are also unchanged, **400/400** — worth stating because a
byte-identical arm with drifting judge verdicts would have made every cross-run judge delta
meaningless, and JUDGE-NONDET makes that a live possibility rather than a hypothetical.

### Pre-registration — hit on the number and the direction

Recorded in the harness docstring at `57145f3`, **before** the run: *10 rows change on the 400;
9 were failing and should now pass; raw 314/384 vs v15 300/384 = +3.6; defective rate 3/102 =
2.9%.*

Observed, comparing the v16 arm against v16 at `5d0dcb7`: **9 flips, every one FAIL→PASS, zero
PASS→FAIL, raw 305 → 314**, and the defective rate exactly 3/102. **The composition claim was
slightly off in the safe direction — 12 rows changed text, not 10.** The two extras (eval_275,
eval_314) changed wording without flipping a verdict. Third consecutive calibration point, and
the second to hit its total exactly.

**The pre-registered watch row cleared.** eval_314 was flagged in advance as the one to watch —
already passing, shape changed by the rate branch, and *"if it flips to FAIL the rate branch is
over-broad and should be narrowed to rows that were clarifying"*. It is **still PASS and still
judge-correct** at `1476caa`. The rate branch is not over-broad.

### The 6 regressions — and the residual class is now EMPTY

**All 6 are v16 clarifications** (eval_271, 281, 291, 294, 295, 334). **There is not one row in
the entire 400 where v16 states a wrong number that v15 stated right.** Judge applied to *v15's*
answer on those 6: **5 wrong, 1 undetermined, 0 correct.**

That last figure is the one that moved. At `5d0dcb7` the "no class of regression" clause was
satisfied outright for the class it was written to catch, but **not clean** for a narrower
residual: eval_280 and eval_323, where a judge-confirmed *correct* v15 answer became a
clarification. **Both now pass** — eval_280 via C4 + headcount extraction, eval_323 via F1, each
closing exactly as the D/F investigation projected. The residual class goes from 1 row to zero.

> ### 🟢 THERE IS NO ROW WHERE v16 STATES A WRONG NUMBER THAT v15 STATED RIGHT.
>
> Stated plainly because **this is the sentence the wiring decision rests on**, and "the ADR
> clause is satisfied" is a weaker and less findable claim. Three measured zeros hold it up,
> across all 400:
>
> - **zero** rows where v16 states a wrong number that v15 stated right;
> - **zero** rows where a judge-confirmed correct v15 answer became a v16 clarification;
> - **zero** fact-path divergence on 281 of 282 non-compute scored rows, the single exception
>   (eval_322) passing in both arms.
>
> Every one of the 6 regressions is a v16 clarification replacing a v15 answer the judge calls
> wrong or cannot call at all.
>
> #### ⚠️ CORRECTION (2026-08-09, at cutover) — the original wording overreached, and here is the exception
>
> This block first read **"THERE IS NO ROW WHERE v16 IS WORSE THAN v15 BY ANY READING."** That
> is a stronger claim than the three zeros beneath it support, and it is **false on one row**:
>
> **eval_318 goes v15 `judge=undetermined` → v16 `judge=wrong`.** v15 recites the VAT threshold
> and never applies it to the user's figure; v16 applies it **backwards** and tells a business
> that must register for VAT that it need not (SAFETY-3 below). By the judge's reading that is
> v16 being worse than v15 on that row. The three zeros are each still exactly true — v15 never
> *stated the number right* there, so no zero is violated — but "worse by any reading" reaches
> past them, and eval_318 is what it reaches into.
>
> Caught by Claude re-reading its own claim against the cutover canary data, not by the founder
> or by any instrument. **The narrower headline above is the defensible one and is what the
> wiring decision actually rested on**; the overreaching version was live in this file from the
> `1476caa` entry until the cutover.
>
> Also unchanged and still the second honest qualifier: the one other row where v16 has ever
> been *worse* than v15 in this project's record — **nat_16**, the SAFETY-2 / D-RESIDENCY-1
> residency mis-detection, where v16 prints a wrong figure as a verified calculation while v15
> asserts no figure — is **not in the 400** and is unaffected by this run. It remains open. So
> the fully-qualified statement is: no row in the measured set where v16 states a wrong number
> v15 stated right, with **eval_318** the judge-visible exception inside the set and **nat_16**
> the known exception outside it.

### ⚠️ GAIN RECORD CORRECTED — 19 real / 1 false, not 20

The raw judge verdict on the 20 gains is **18 correct / 2 wrong** (eval_320, eval_321).
Adjudicated individually against gold rather than taken from the judge, that resolves to
**19 real gains and 1 false**, with the two rows going in opposite directions:

- **eval_320 is a genuine FALSE gain.** The regex credited it because every correct figure
  (0 / 80,000 / 78,000 / 4,000) appears somewhere in the merged answer — while the model body in
  the same breath asserts **SDL = TZS 28,000 on a ONE-employee payroll**, **NSSF = 160,000**, and
  **PAYE = 8% × 800,000 − TZS 26,000 = 64,000**, the last via a personal relief that **does not
  exist in Tanzania** (CLAUDE.md §11). The judge is right and the scorer is wrong.
- **eval_321 is a JUDGE error in the opposite direction.** Checked part-by-part against gold:
  SDL TZS 0 (8 < 10) ✓, NSSF 640,000 ✓, WCF 16,000 ✓, OSHA "Ndiyo, unatakiwa kusajili" ✓ — **all
  four parts match.** Independently corroborated by the cross-levy sweep below, which recovered
  eval_321's three model bodies as bare *"Thibitisha na TRA (tra.go.tz)."*: every figure in that
  answer is a deterministic working, so there is nothing left for the model to have got wrong.

**eval_320 is the row D-FIDELITY-2 was built for.** With the guard shipped this session those
bodies are blanked and the deterministic workings carry the answer, which should convert
eval_320 from a false gain into a real one — **but that is a projection, not a measurement, and
it is not confirmed until the next paired run.**

### Judge range — four treatments, sign-stable, and the exclusion gap has nearly closed

The reconstruction was **calibrated against the published `5d0dcb7` table first** and reproduced
all eight of its cells exactly before being applied here (`scratch/judge_treatments.py`).

| Treatment | v15 | v16 | Δ | (Δ at 5d0dcb7) |
|---|---|---|---|---|
| Reported (`build_confirmation_report`) | 267/360 = 74.2% | 297/368 = 80.7% | +6.5 | +6.2 |
| Common denominator, decisive in both arms (n=354) | 266/354 = 75.1% | 284/354 = 80.2% | **+5.1** | +3.7 |
| Every clarification = FAIL, undetermined excluded | 267/361 = 74.0% | 297/372 = 79.8% | +5.9 | +4.1 |
| Hard floor — clarifications *and* undetermined FAIL, /384 | 267/384 = 69.5% | 297/384 = 77.3% | +7.8 | +6.2 |

**Honest range +5.1 to +7.8; strictest like-for-like +5.1. No accounting flips the sign** — do
not quote +6.5 flat. Every treatment improved on `5d0dcb7`, the strictest by the most (+3.7 →
+5.1). **The exclusion asymmetry is now 3 rows, down from 10:** of v16's 21 clarifications, 17
sit inside the graded set and are already scored FAIL and only 4 are excluded outright (v15: 1).
Judge-undetermined fell 23 → 12 on v16.

### Fact path — byte-zero regression surface, holding

**281 of the 282 non-compute scored rows are BYTE-IDENTICAL between v15 and v16.** The sole
exception is again **eval_322**, the three-part enumeration the decomposer splits; both arms
PASS. 15 of 16 OOC rows are byte-identical, the exception being **eval_191** — the row whose
`out_of_corpus` label is a known mislabel (tracked separately; it is a core in-scope PAYE
computation and correcting the label moves the gate denominator).

So v16's entire delta still lives in the 102 compute rows, and the fact path carries **byte-zero**
regression surface rather than statistically-zero.

### Two-arm retriever — the regex pointed the wrong way for a fourth time

Part 3 reproduced **exactly**: two-arm 78/90 = 86.7% vs single-arm 74/90 = 82.2%, regex **+4.4**.
Judge-augmented on the same rows lands 70/89 = 78.7%. Four independent measurements have now
failed to demonstrate a two-arm benefit, and the regex scorer has pointed the wrong way on the
same question set every time. **Single-arm stays. Settled; do not reopen.**

### Clarification

**Defective clarification rate 3/102 = 2.9%, against ≤5% — PASS.** The three are exactly the
deliberate residuals: **eval_281** (permanent won't-fix, the approximation veto), **eval_326**
(residency split, D-RESIDENCY-1), **eval_334** (blocked on a *regulatory* question about
allowance taxability, not a code one). There is no defective clarification left that is a code
defect. All-clarification rate 16/102 = 15.7%, reported as context only — the retired target's
measured floor is 14.7% and **must not be reinstated**.

### Wiring — CODE COMMITTED, PRE-FLIGHT PASSED, ~~NOT DEPLOYED~~ **DEPLOYED `ec9cbb3`** (2026-08-09)

Both preconditions are clear. The rotation completed and **v16 is live** — see the cutover entry
at the top of this file. The text below records the wiring as it was staged, before the deploy.

**Shipped as code, not as a deploy:** `ChikeModel._orchestrator()` builds the Orchestrator once
per container with `retriever=self.retrieve_facts` (single-arm, load-bearing) and `run()`
dispatches on a new `chike_config.json` flag `pipeline: "v15" | "v16"`. The flag **defaults to
`v15`** on an absent or unrecognised value, so a malformed config can never silently promote
v16; rollback is a config edit + redeploy, never a code change.

> #### 🚨 The wiring surfaced a container-only Gate-2 regression — see **CONTAINER-PATH-1** below
>
> Letting `Orchestrator` default its OOC phrase lists would have served **39 phrases instead
> of 107** inside the Modal container, silently reopening SAFETY-1. Closed by passing
> `resolve_phrases(CONFIG)` explicitly from the baked config; `stop_strings` set explicitly for
> the same reason. Full write-up in its own entry — it is a class of defect, not a detail of
> this wiring.

**Pre-flight — all four ran, all four passed, before any deploy:**

| check | result |
|---|---|
| full test suite | 605 passed |
| `scripts/scan_for_keys.py` | clean |
| 620-row deterministic sweep | 0 rows changed |
| byte-compare vs the stored 1476caa v16 rows | deterministic path **byte-identical on all 87 working-producing rows**; the guard is the **only** behavioural change, on **exactly eval_318 and eval_320** |

The byte-compare (`scratch/preflight_wiring.py`) re-renders each stored row through today's
code from its recorded model bodies. It answers the two questions the test suite cannot: that
HEAD still reproduces what was measured, and that nothing besides the guard changed.

### 🚦 DEPLOY CHECKLIST — read the flag correctly

> **THE COMMITTED FLAG IS NOT THE LIVE FLAG.** `chike-inference/modal_app.py` bakes the
> **local working-tree** `kaggle/chike_config.json` into the image via `add_local_file`, so
> whatever the flag says takes effect **only at the next `modal deploy`**. Until then the
> running containers keep serving whatever config was baked at the *previous* deploy. Reading
> the committed value as "already live" is exactly backwards, and it is the same warm-container
> reasoning as R16.
>
> **~~Current state: `pipeline: "v15"` (flipped back at `e365c25`), production serving v15,
> nothing deployed.~~ SUPERSEDED — the cutover ran. Current state: `pipeline: "v16"`, deployed
> at `ec9cbb3`, production serving v16.** See the cutover entry at the top of this file.
> The flag was briefly committed as `v16`, then flipped back so the credential-rotation deploy
> carried ONE change rather than two — a combined deploy leaves two candidate causes for any
> failure, which is what R16 exists to prevent — then re-flipped as step 1 of the cutover.

**Agreed sequence (founder, 2026-08-09) — two deploys, deliberately:**

| # | who | step |
|---|---|---|
| 1 | Claude | flip the flag to `v15` and commit — **done, `e365c25`** |
| 2 | founder | rotate: new value → Modal secret `modal-api-token` / `MODAL_API_TOKEN` → `~/.chike_modal_token.txt` → Railway `MODAL_API_TOKEN` |
| 3 | founder | confirm the chain is complete |
| 4 | Claude | **rotation deploy** — `modal app stop chike-inference --yes` then `modal deploy`; verify the live path on the new token: one fact question answers normally, one OOC question refuses — **done** (took three rotation attempts; the Modal secret held a 10-char value against the local 43-char file, diagnosed from inside the container without exposing it) |
| 5 | Claude | **v16 cutover, its own deploy** — re-flip to `v16`, `modal app stop --yes`, deploy, then the full canary set — **done, `ec9cbb3`** |

Rotation order, confirmed: **Modal secret → `modal app stop --yes` && `modal deploy` → Railway
variable + redeploy → verify.** There is an unavoidable 401 window on the WhatsApp path
(Modal injects secrets at container start, so a single-value secret cannot be valid on both
sides at once); every reply during it is the FALLBACK message. Accepted — there are no users
yet. `generate_endpoint` shares the same gate, so `~/.chike_modal_token.txt` must be updated
before any local canary run.

**Step 5 live verification per R16** — `modal app stop chike-inference --yes` FIRST, because
"✓ App deployed" proves nothing while containers are warm. Then against the live endpoint:
**eval_320 and eval_318** (permanent canaries for the cross-levy class — the gate cannot see
them, both score `pass=True`), **eval_323 and eval_280** (changed compute rows), **a fact row
as the negative case** (must be byte-identical to v15), and **an OOC question** (must still
refuse).

## ✅ D-FIDELITY-2 — a compute body that volunteers a WRONG figure for a SIBLING levy (SHIPPED 2026-08-09)

`chike/fidelity.py::body_contradicts_siblings` + `Orchestrator._cross_levy_guard`, with 18 tests
in `tests/test_fidelity_cross_levy.py` and the findings artifact at
**`eval/results/cross_levy_guard_sweep_findings.json`**.

### What D-FIDELITY-1 structurally could not see

D-FIDELITY-1 validates each sub-answer body against **its own** `ComputationResult`. That is
blind to a body which restates its own levy correctly while asserting wrong figures for the
others in the same breath. **eval_320** is the case: the WCF sub-answer restated WCF 4,000
correctly and passed the per-levy guard, while the same body volunteered `SDL = 3.5% × TZS
800,000 = TZS 28,000` for a **one-employee** payroll (engine: TZS 0, below the 10-employee
threshold) and `PAYE = 8% × TZS 800,000 − TZS 26,000 = TZS 64,000` (engine: 78,000, and the
**TZS 26,000 personal relief does not exist** — CLAUDE.md §11). The regex scored the row PASS;
the judge called it wrong.

The guard runs as a **second pass**, because sibling results do not exist until every compute
part has been answered. Blanking is whole-body and idempotent, so running after the per-levy
guard can only ever remove more text, never resurrect any. **Compute sub-answers only** — a fact
sub-answer has no `ComputationResult` to fall back on, so blanking it would delete content
rather than replace it with the truth.

### Sweep — three instruments, because a clean result from one is not a green light

**A — no-op proof, 620 rows.** Every corpus question through the real Orchestrator twice, guard
active vs guard replaced by identity, comparing merged text, clarification flags and the per-sub
`ComputationResult` tuple. **0 of 620 rows change.** The guard cannot move a figure, a route or
a clarification.

**B — real-body replay.** The guard can only fire where a question routes to **two or more**
compute levies, which is **9 corpus questions**; 6 are in the gate and were replayed against the
**actual model bodies** recorded in the `1476caa` artifact. Bodies are recovered *exactly*, not
approximated: `_render` emits `body\n<working>` joined by `\n\n` and the workings are
deterministic, so each body is the text preceding its own working. The 3 probe rows (fv_01,
fv_02, fv_04) are not in the artifact and are reported **unmatched rather than guessed at**.

**2 questions flagged, 3 bodies, 0 false positives, 0 false negatives.** eval_320 is flagged
**twice** — its NSSF body and its WCF body each volunteer wrong sibling figures independently.
eval_318's SDL body asserts `NSSF = TZS 110,000` where the engine says 1,100,000 (a factor of
ten). **The four unflagged rows were each adjudicated individually rather than counted**
(eval_319, eval_321, eval_323, eval_327): every one names a sibling levy but attributes **no TZS
figure** to it, so there is nothing to contradict. All four are true negatives.

**C — ablation. All three design decisions are load-bearing**, measured rather than asserted:

| disabled | good bodies wrongly blanked | bad bodies missed | live flags |
|---|---|---|---|
| `_acceptable` → headline amount only | 2 (both NSSF share-vs-total probes) | — | unchanged |
| `_levy_windows` → every levy sees the whole body | 1 | eval_318 | **loses eval_318, spuriously gains eval_323** |
| `_ATTRIBUTED` → `=` only, no colon | — | 2 (incl. the eval_320 target) | unchanged |

**Windowing is the strongest result: without it the guard both misses eval_318 and blanks
eval_323, a correct body on a live corpus row.** `_acceptable` exists because NSSF's
authoritative `amount` is the employee share in a per-employee framing (eval_320) and the 20%
total in a payroll framing (eval_318), so a faithful body quoting either is not a contradiction —
that probe is the one that changed the code. Colon attribution matters because the enumeration
shapes attribute with `:` as often as with `=`; `_RESULT` is left byte-identical so the validated
own-levy detector is untouched.

**605 tests pass** (587 + 18).

### What this does NOT do

It is a **consistency check between two outputs of one computation**, exactly as D-FIDELITY-1 is.
It has no independent notion of correctness and **cannot detect an error upstream of both** — the
SAFETY-2 / D-RESIDENCY-1 class, where body and working agree because both derive from the same
mis-resolved input, is untouched by it. It also cannot see a fact sub-answer, which is precisely
why the eval_318 VAT defect below needs its own item rather than being folded in here.

## 🔬 SAFETY-3 INVESTIGATION ROUND — it is a CLASS, and it is wider than "wrong direction" (2026-08-10)

**Nothing implemented. Proposal only.** Artifact:
**`eval/results/safety3_threshold_investigation.json`**. Probes preserved at
**`eval/accuracy_gate/threshold_comparison_probes_024.jsonl`** (note: this takes the sweep
corpus from 620 rows to 644 — no test is wired to them yet, that belongs with the fix).

### The headline: the corpus understated the failure rate by about five times

| instrument | result |
|---|---|
| corpus exposure (620 rows) | **132 rows require a threshold comparison**; 48 have it performed by the model |
| corpus outcome (400 gate, both arms, adjudicated individually) | **1** answer with a wrong verdict (eval_318, v16) + 1 wrong-direction phrase with a right conclusion (eval_124, v15, fixed in v16) |
| **24 authored probes against LIVE v16** | **7 of 20 model-performed comparisons are WRONG (35%)**; **4 of 4 deterministic controls correct** |

**R17, demonstrated with numbers rather than restated.** The corpus rate is 1-in-8; the authored
rate is 7-in-20. Every one of the extra failures is a *form the corpus does not contain*. The
corpus was not reassuring — it was silent.

### Six distinct failure mechanisms, not one

`eval_318` is the direction inversion. It is the *least* of what is there.

| mechanism | probe | what happened |
|---|---|---|
| **direction inversion** | th_03 | TZS 195M vs a 200M threshold → *"umepita kizingiti"*. Invents an obligation that does not exist. |
| **direction inversion** | th_17 | reproduces the live eval_318 inversion byte-for-byte |
| **wrong threshold selected** | th_06 | TZS 120M in six months exceeds the **100M six-month limb**; the answer applies the 200M annual limb and says no |
| **no unit normalisation** | th_08 | TZS 20M/month = 240M/yr. The answer states *"you cross 100M in 5.5 months"* and then concludes **below the threshold** |
| **floor treated as ceiling** | th_16 | paying TZS 200,000 against a TZS 175,000 minimum wage → *"malipo ya ziada juu ya hapo ni kinyume cha sheria"*. **It tells an employer that paying above the minimum wage is illegal.** |
| **threshold conflation** | th_24 | TZS 50M is above EFD's 11M and below VAT's 200M; the answer orders **VAT registration off the EFD threshold** |
| **sub-question dropped** | th_20 | the VAT part of a multi-part question is never answered at all |

**th_16 is arguably worse than eval_318.** A fabricated prohibition on paying workers *more*
than the minimum is wrong-direction advice on a labour-law question, and nothing in the corpus
or the gate would ever have found it.

**Both directions fail.** th_03/th_24 invent obligations; th_06/th_08/th_17 excuse real ones. A
fix that biases toward "register" would trade one class of wrong advice for another.

### Root cause: not retrieval, not generation quality — a MISSING DETERMINISTIC PATH

Established, not assumed:

1. **Retrieval is fine.** The RAG index carries five VAT-threshold entries, including the
   Swahili-first *"Kizingiti cha kusajili VAT: mauzo ya TZS 200,000,000 kwa miezi 12."* The
   model **recites 200,000,000 correctly** and then compares wrongly. The fact is present and
   correctly stated in the very sentence that misapplies it.
2. **Not generation quality either.** `th_01` — the identical 205M-vs-200M comparison, asked
   standalone — is answered **correctly**. The model can do it. It just is not required to.
3. **There is no route.** `routing.COMPUTE_TYPES` is `("sdl","nssf","paye","wcf")`. VAT, EFD,
   minimum wage and the share-capital bands have **no computation type at all**, so
   `detect_intent("je nasajili VAT kama mapato ni TZS 205,000,000?")` returns **`none`** and the
   comparison is performed in free generation with no `ComputationResult` behind it.

**This is ROUTING-GAP-PAYE in a new domain, and the same argument settles it.** SDL and PAYE sit
behind a rules engine because a levy amount is arithmetic. *A threshold comparison is also
arithmetic* — `V >= T` — and it is the simpler of the two. The probe result is the measurement
that argument was always missing: **4/4 where the engine owns the comparison, 13/20 where the
model does.**

Corollary: because there is no `ComputationResult`, **neither fidelity guard has jurisdiction**.
D-FIDELITY-2 blanked eval_318's SDL body and left the VAT inversion untouched — correctly, by
its own design. No amount of guard widening reaches this; it needs a route.

### Does v16 being live make it worse? Yes — three ways, and one way better

**Worse:**
1. **Authority by association.** Under v16 the inversion is rendered *after* two deterministic
   workings, inside an answer that otherwise reads as verified computation. v15 delivered the
   same class of error as hedged prose.
2. **The guard raised its share of the answer.** D-FIDELITY-2 blanked the contradicting SDL
   body, so the wrong VAT sentence went from a clause inside a long paragraph to **186 of the
   317 characters (59%)** of the live reply. Removing wrong prose around a wrong claim
   concentrates it.
3. **v15 did not assert it.** Paired over the 79 gate rows demanding a comparison, v15 leaves
   eval_318 **UNRESOLVED** — it states the rule conditionally (*"unatakiwa kujiandikisha **ikiwa**
   mauzo yanazidi..."*) and never applies it. v16 applies it and gets it backwards. `undetermined
   → wrong`.

**Better:** all **four** rows where v16 asserts a direction v15 did not are **SDL headcount**
rows, all four routed to the engine, all four **judge-correct**, and two of them were
**judge-wrong under v15**. Where the deterministic path exists, v16 strictly improves the
comparison. That is the same finding from the other side.

### Options

| | approach | closes | cost / risk |
|---|---|---|---|
| **A** | **Deterministic threshold route** — give the engine `vat_registration` and `efd_requirement` computation types; extraction supplies V and its period, the engine holds T and emits verdict + working | direction, threshold selection, conflation, and unit normalisation — all four are consequences of the engine not owning the comparison. Also gives both fidelity guards jurisdiction for the first time | period extraction (12mo / 6mo / monthly) is a **new extraction surface** and th_08 shows it is genuinely hard. Router changes carry the highest blast radius in this system (ROUTING-GAP-PAYE) |
| **B** | **Fact-path comparison guard** — post-generation: recompute V vs T on any answer reciting a known threshold, blank or correct on mismatch | direction inversion and conflation, with no routing or extraction change | **cannot** fix th_06/th_08 — knowing *which limb* and *how to annualise* is exactly what it lacks, so it must blank. Blanking a fact sub-answer **deletes content** rather than replacing it with truth — the stated reason D-FIDELITY-2 excluded fact sub-answers. My own detector needed three iterations and still had 4 false positives before per-threshold attribution |
| **C** | **Refuse to compare** (R8 never-guess) — state the rule conditionally, decline the verdict. This is exactly v15's eval_318 behaviour | every wrong answer, immediately | turns 13 currently-correct answers into non-answers, on a question ("am I over the VAT threshold?") that is core to the product. Gate would score it worse — clarifications FAIL under most treatments |

**Recommendation — A for VAT and EFD, staged, with C as the fallback inside it.**

- **Phase 1: VAT (200M/12mo + 100M/6mo) and EFD (11M) only.** Both are single scalars needing
  no sector or band resolution, and they carry the question volume — 29 and 6 corpus rows. When
  the period is unambiguous the engine answers; **when the period cannot be extracted the engine
  declines and the answer states the rule conditionally** (option C, scoped to the hard case
  rather than applied to everything). That keeps th_08 safe without pretending to solve it.
- **Phase 2: minimum wage — separate investigation.** GN 605A is 16 sectors and 46 sub-sectors;
  resolving which floor applies is a bigger extraction problem than the comparison. **th_16 may
  not need a route at all** — a locked fact stating plainly that paying *above* the minimum is
  lawful is cheap and worth doing on its own.
- **Phase 3: unit normalisation** (th_08) as its own item. Annualising a monthly figure is an
  extraction problem, not a comparison problem, and folding it into Phase 1 would hide it.

**Do not skip the R17 step on the router change.** These 24 probes are the *start* of the probe
set, not the whole of it — a router change needs its own adversarial probes written against the
new cue list, plus the 644-row sweep.

### Three incidental defects, each needing its own item

1. **🔴 D-FIDELITY-1 has an attribution gap — VERIFIED, not suspected.** th_19's body says
   *"SDL ... **sawa na** TZS 210,000"* while its working says **TZS 17,500**. Checked directly:
   `_asserted_results(body)` returns an **empty set** and `body_contradicts_working` returns
   **False**. `_RESULT` matches `=` only and `_ATTRIBUTED` matches `[:=]`; **"sawa na" is the
   ordinary Swahili way to state a result and neither pattern sees it.** This is the same shape
   as the colon widening that D-FIDELITY-2's ablation proved load-bearing, and it means a body
   contradicting its own working passes silently.
2. **🔴 Compute base error on embedded multi-part.** th_19 computes SDL on a base of
   **TZS 500,000** instead of the stated 6,000,000; th_20 computes NSSF on **TZS 750,000**
   instead of 9,000,000. Both are the stated payroll **divided by 12** — a per-employee or
   per-month derivation firing where it should not. The deterministic layer is confidently
   wrong, which is the SAFETY-2 / D-RESIDENCY-1 class, not this one.
3. **🟠 A fact sub-question can be silently dropped** (th_20 never answers its VAT part) and
   **🟠 a fabricated figure** (th_22 invents a *"TZS 3,000 minimum"* WCF that appears in no
   locked fact).

## 🔴 SAFETY-3 — eval_318 answers the VAT threshold BACKWARDS on the fact path (2026-08-09)

> ### ⬆️ PROMOTED TO TOP OF THE QUEUE — 2026-08-09, at the v16 cutover
>
> **The promotion trigger was the cutover making it user-facing. No new evidence arrived.** The
> defect, the mechanism and the gold are exactly as characterised below and as they were this
> morning. What changed is deployment state: under v15 this row was *undetermined* — the model
> recited the threshold and never applied it — and at `ec9cbb3` v16 went live and now emits the
> inversion to real users.
>
> **"Logged" and "serving users" are different states, and this crossed the line at cutover.**
> A defect can sit correctly filed, correctly root-caused and honestly reported, and still
> change priority the moment the code path carrying it starts answering people. That transition
> is a promotion trigger in its own right and should be treated as one whenever a deploy moves
> a known defect onto the live path.
>
> It gets a **fresh investigation round** — characterise before any code, in the usual way.
> This is the next work item; nothing else starts ahead of it.

**Own investigation. Not folded into D-FIDELITY-2, and not closable by it.**

The fact sub-answer of eval_318, at both `5d0dcb7` and `1476caa`:

> *"**Hapana**, kwa sababu kizingiti chako cha usajili wa VAT ni TZS 200,000,000 tu. Mapato ya
> TZS 205,000,000 **hayazidi** kizingiti hicho, hivyo **huhitajiwi kusajili VAT**."*

**TZS 205,000,000 does exceed TZS 200,000,000.** The gold is explicit: *"mapato TZS 205,000,000
yamevuka kizingiti cha TZS 200,000,000/mwaka, hivyo **lazima usajili VAT**."* The system tells a
business that must register for VAT that it need not. This is **wrong-direction compliance
advice** — the same class as SAFETY-1, where the OOC gate leaked and the model answered a
capital-gains question with a confident rate.

**The row scores `pass=True, reliable=True` in both arms.** The regex credits it because 200M and
205M both appear; only the judge catches it (`judge=wrong`, and it sits in v16's false-pass
queue). A wrong-direction answer that the gate positively credits is worse than one it fails.

**Which path, and which arms.** The defect sits on the **shared fact path — the path that serves
every user whichever arm ships**. On this specific row only **v16** emits the inversion; v15
recites the threshold correctly and simply never applies it to the user's figure (`judge=
undetermined`). So v16 is worse *on this row*, but the mechanism — an unguarded numeric
comparison performed by the model on the fact path, with no deterministic backstop — is v15's
too, and v15's non-answer here is luck rather than safety.

**Not a rules-engine gap.** VAT registration is not a levy the rules engine computes; there is no
`ComputationResult` to guard, so neither fidelity guard can reach it. This is the
ROUTING-GAP-PAYE shape in a new domain: *the engine never ran at all*, and the model did the
threshold arithmetic unsupervised. Candidate directions — a deterministic threshold-comparison
route for VAT registration, or a fact-path numeric-comparison guard — are a **scoped
investigation, not a fix to attempt reactively**, and they must be characterised before any code
in the usual way.

### ⚠️ IT WAS ALREADY FILED ON 2026-07-26 AND NEVER PROMOTED — this is the actual finding

eval_318's VAT inversion is recorded in this file at the work-item-2 round-2 adjudication of the
`afef9dd` queue: *"eval_318 **inverted** the VAT 205M>200M comparison"*, filed as one of **"4
generation"** root causes inside a list of 16 confirmed regex false-passes. It was correctly
identified, correctly root-caused, written down — **and given no owner, no item number, and no
tracking line.** It has survived an entire fix cycle untouched and is still live in the most
recent run.

**Standing lesson — a defect filed as a row inside a queue is not tracked.** The
adjudication queues exist to compare *instruments* (regex vs judge), and their output is a list
of scored rows, not a work list. Two instruments flagged this row and neither produced an owner,
because nothing in the process promotes a row out of a queue into the defect register. Anything
found inside an adjudication batch that is a **user-facing wrong answer** must be lifted out into
its own dated item with its own heading at the time it is found — the queue entry is evidence,
not a record of work. Concretely: when a future adjudication produces a false-pass list, sweep it
for wrong-direction and wrong-number answers **before** closing the batch, and promote each one.

## 🔴🔴 CONTAINER-PATH-1 — WIRING v16 WOULD HAVE SILENTLY REOPENED SAFETY-1 (2026-08-09)

**The most important finding of the wiring work, and it is a CLASS, not a detail.** Caught
while writing `ChikeModel._orchestrator()`; closed in the same commit (`30db5e6`). Nothing
shipped broken — but nothing offline would have told us if it had.

### The defect

`Orchestrator.__init__` defaults its OOC phrase lists from
`classification.load_local_config()`, which reads a **repo-relative** path:

```python
_LOCAL_CONFIG_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "kaggle", "chike_config.json"))
```

The Modal image mounts **only** `chike/` — `add_local_dir(..., '/root/chike')` — and bakes the
config somewhere else entirely, `/root/assets/chike_config.json`. So inside the container that
path resolves to **`/root/kaggle/chike_config.json`, which does not exist**.
`load_local_config()` swallows the `FileNotFoundError` and returns `{}` by design, and
`resolve_phrases({})` returns the hardcoded-only list.

**Measured, not reasoned:** `resolve_phrases(CONFIG)` → **107** OOC phrases.
`resolve_phrases({})` → **39**. The 68 missing ones are the config-only additions —
**the entire SAFETY-1 audit**, the 54-phrase expansion that closed the live refusal-gate leak
where the production endpoint answered *"niliuza kiwanja changu... nalipa kodi gani"* with a
confident capital-gains rate.

So wiring v16 with defaulted phrase lists would have **served users a v16 whose OOC gate had
been silently rolled back to its pre-SAFETY-1 state.** Gate 2 is a launch-blocking gate under
R7.

### Why no offline instrument could have caught it

This is the part worth internalising. **The path resolves correctly everywhere except in
production:**

| environment | `../kaggle/chike_config.json` resolves to | phrases |
|---|---|---|
| local dev / `pytest` | the real repo file | **107** ✅ |
| Kaggle clone (every gate + paired run, incl. the 1476caa measurement) | the real cloned file | **107** ✅ |
| **Modal container** | `/root/kaggle/...` — absent | **39** ❌ |

The full test suite passes. The 620-row sweep passes. The byte-compare against the stored
1476caa rows passes. **The harness that produced the measurement authorising the wiring had
the full 107**, so even a perfect replication of the measured configuration would not have
revealed it. The divergence exists *only* in the one environment no offline instrument runs
in, and the failure is **silent** — a shorter list refuses less, and refusing less looks like
working.

### Second time R16's class has bitten — and the first is the same shape

| | 2026-08-07 — stale containers | 2026-08-09 — CONTAINER-PATH-1 |
|---|---|---|
| change | OOC phrase list expanded in config | v16 wired, phrase lists left to default |
| what was true locally | new phrases present and correct | 107 phrases resolved correctly |
| what the container did | kept serving the OLD config from warm containers | would have resolved `{}` → 39 phrases |
| how it presents | the leak the fix closed reproduces exactly | the leak SAFETY-1 closed silently reopens |
| detectable offline? | **no** | **no** |

**Both are the same failure: a config value that is correct in the repo and absent in the
container, presenting as a refusal-gate regression.** R16 was written about *timing* (warm
containers serve old config). CONTAINER-PATH-1 shows the same class through *path resolution* —
the config never reaches the container at all, at any point, no matter how many times you
redeploy. Generalising R16 accordingly:

> **A config value is not "in production" because it is in `chike_config.json`. It is in
> production when a request has demonstrably behaved differently because of it.** Two ways it
> can fail to arrive: the container is stale (R16), or the code reads a path the container does
> not have (this). Neither is visible to any test that runs outside the container.

### Rules that follow

1. **Never let production code depend on `load_local_config()`.** It is the *local/orchestrator*
   loader — its own docstring says so — and it fails soft to `{}`. Production must pass the
   baked `CONFIG` explicitly. Done here for `ooc_phrases`, `in_scope_phrases` and
   `stop_strings`.
2. **Audit every remaining repo-relative path read from inside the Modal image.**
   `chike/prompting.py` uses the same pattern (`load_system_prompt`) — production overrides it
   by passing `system_prompt=BASE_SYSTEM_PROMPT` explicitly, so it is safe *today*, but only
   because the caller happens to be explicit. Worth a standing check rather than luck.
3. **A fail-soft default in a config loader is a liability on the serving path.** `{}` is right
   for a unit test and wrong for a container: it converts "the config is missing" into "the
   safety list is shorter". Where a fail-soft default meets production, the caller must be
   explicit.
4. **The live canary set must include an OOC refusal on every deploy** — it is the only check
   that can see this class. It is already in the wiring verification set, and it is now the
   single non-negotiable item in it.

## 🔐 CREDENTIAL HYGIENE — a docstring promised "never logged" and was false in exactly the failure path (2026-08-09)

`tests/test_orchestrator.py::_real_modal_token` is documented *"Token from env, else
~/.chike_modal_token.txt. **Never logged.**"* Every scratch probe carries the same promise. It
held on the success path and **broke on the only path that matters** — the token rides in the
**query string**, so `requests`' own `HTTPError` embeds it verbatim:

```
401 Client Error: Unauthorized for url: https://...generate-endpoint.modal.run/?token=<LIVE TOKEN>
```

During the 2026-08-09 rotation the real-weights tests — which normally SKIP, and only ran
because a token file now existed — hit the post-rotation 401 and **printed the live credential
into the pytest failure report**. Not a hypothetical: it went to a temp file on disk and into
terminal scrollback, and the token had to be treated as burned and rotated again.

**Three things worth keeping:**

1. **A safety claim in a docstring is not a safety mechanism.** The promise was written about
   the code the author was looking at (nothing calls `print(token)`) and not about the library
   underneath it. `LocalAdapter.generate()` now scrubs before re-raising, and
   `tests/test_container_path_guards.py` fails if a future change lets the value through — the
   claim is now enforced rather than asserted.
2. **A credential in a QUERY STRING leaks by default, not by mistake.** Every layer that
   renders a URL — exception messages, access logs, proxies, browser history, CI output — gets
   the secret for free. The query-param design was chosen deliberately (a module-level
   `from fastapi import Header` would crash the GPU container that imports `modal_app` without
   fastapi), so this is a **known cost of a defensible decision**, and the mitigation is to
   scrub at every boundary rather than to re-litigate the design.
3. **`scan_for_keys` cannot see this class.** It scans *staged files* for hardcoded keys. A
   credential that only ever appears in runtime output is invisible to it. Nothing in the repo
   was ever wrong; the leak was entirely in what the code *printed*.

Same shape as CONTAINER-PATH-1 above, one layer up: something true of the code as written, and
false in the one environment or path that was never exercised.

## 🔴 STANDING LIMITATION — THE GATE CREDITS BOTH OF THE WORST DEFECTS THIS CYCLE FOUND (2026-08-09)

**The two most serious defects found this cycle both score `pass=True` on the regex scorer.**
Not `reliable=False`, not excluded — positively credited, counted toward the launch-blocking
in-corpus number.

| row | what it does | regex | judge |
|---|---|---|---|
| **eval_318** | tells a business with TZS 205,000,000 turnover it need **not** register for VAT against a 200M threshold — wrong-direction compliance advice | `pass=True`, `reliable=True` | wrong |
| **eval_320** | asserts **SDL TZS 28,000 on a ONE-employee payroll** and a PAYE figure derived from the **phantom TZS 26,000 relief** (CLAUDE.md §11) | `pass=True` | wrong |

**Mechanism — this is structural, not bad luck.** The scorer is number-set intersection: it asks
*"is a correct figure present?"* and never *"is a WRONG figure also present?"* eval_318 passes
because 200,000,000 and 205,000,000 both appear; eval_320 passes because all four correct
figures (0 / 80,000 / 78,000 / 4,000) appear **alongside** the wrong ones. So **an answer that
states the right number AND a contradicting wrong number scores identically to one that states
only the right number** — and that is exactly the shape the v16 compute path produces, because
`_render` appends the authoritative working to whatever the model said. The better the
deterministic layer gets at guaranteeing a correct figure is present, the more reliably it
*masks* a wrong figure sitting next to it from the scorer. **This is D-SCORER-1, but the
severity is new**: the masked content is now wrong-direction compliance advice and an
authoritative-looking wrong levy figure, not a rambling near-miss.

### Why this and the queue-buried lesson are one argument

The judge caught both rows. It also caught eval_318 **a cycle earlier**, on 2026-07-26, and that
finding was lost because it lived as a line item inside an adjudication queue with no owner (see
SAFETY-3 above). So the record is: **the only instrument that can see this class found both
defects, and the process still lost one of them for a full cycle.**

Two conclusions, and they are different questions that have been getting conflated:

1. **Should the judge MOVE the `GATE PASSED` number? Still no — unchanged.** That remains gated
   on work item 2 (real adjudicated ground truth). Nothing here changes that; the judge is not
   ground truth and was itself wrong on eval_321 this very run.
2. **Should the judge RUN at all? Always — ✅ APPROVED AND SHIPPED (`1facd2a`).** The overlay
   used to be *optional*: it fired only when `OPENROUTER_API_KEY` was present and
   `CHIKE_JUDGE != 0`, and both harnesses were explicitly designed to complete without it. That
   made the only instrument capable of seeing wrong-direction answers a thing that could
   silently not happen. **Both `kaggle/eval_phase_d_paired.py` and
   `kaggle/eval_orchestrator_combined.py` now RAISE at second 0** — not after ~3.5h of GPU —
   with the cost stated in the error ($0.21 + $0.20 + $0.05 on this run) so nobody skips it to
   save money. `CHIKE_JUDGE=0` survives as an explicit human opt-out, but it prints a banner and
   stamps the artifact `judge_overlay: "SKIPPED"`, so **a judge-less run is self-identifying and
   can never be read as a clean result.**

**Additional standing practice:** every run's false-pass queue must be swept for
**wrong-direction and wrong-number** answers and each one promoted to its own item *before* the
run is declared clean. A false-pass list is evidence, not a work list.

**eval_318 and eval_320 are therefore PERMANENT LIVE CANARIES, not gate rows.** The gate cannot
see them by construction, so they are checked against the live endpoint on every deploy. They
are already in the wiring verification set for exactly this reason.

## 🏁 PHASE D RUN 3 (5d0dcb7) — ADR BAR PASSES ON THE SHIPPING CONFIG; clarification metric replaced (2026-08-08)

Artifacts: **`eval/results/gate_phase_d_paired_5d0dcb7.json`** (fetched from HF, **sha256-verified**
`0385db93ba5a946b`, 1,024,998 bytes, `complete: true`, `clone_head == live_head == 5d0dcb7`)
+ **`..._findings.json`**. **Every number recomputed from raw rows, independently of the summary
block; all recomputations matched.** This is the **first run on the configuration that would
actually ship** — the two earlier runs measured v16 *with* the two-arm retriever, which was dropped.

### Headline

| | 3ac522a | 030a5ff | **5d0dcb7 (shipped config)** |
|---|---|---|---|
| ADR bar raw | −6.8 FAIL | +0.5 PASS | **+1.3 PASS** |
| ADR bar reliable | −3.7 FAIL | +1.1 PASS | **+0.8 PASS** |
| compute raw / reliable | −29.4 / −23.0 | −2.0 / +4.0 | **+4.9 / +5.0** |
| gains / regressions | 11 / 37 | 19 / 17 | **17 / 12** |
| judge-augmented v15 → v16 | — | 74.4 → 80.2 | **74.2 → 80.4** |

### The finding the headline understated

`fact_path` is not merely "flat". On the shipped configuration **v16 and v15 produce
BYTE-IDENTICAL text on 281 of the 282 scored fact-path rows** (and 15 of 16 OOC rows). The one
exception, eval_322, is a three-part enumeration the decomposer splits — both arms PASS, judge
calls both correct. So **v16's entire delta lives in the 102 compute rows and the fact path has
byte-zero regression surface**, not statistically zero. The two-arm retriever was the only thing
that had ever perturbed it. This is the strongest available form of the ADR "no class of
regression" answer, and it only became measurable once the arm was dropped.

### Pre-registration hit exactly, including its composition

Recorded in the harness docstring at `d0e7390` **before** the run: deterministic **+7**
(eval_368; 247/371/372/378/379/393), retrieval **−4** (6 lost, 2 regained), net **+3 → 305/384 =
+1.3**. Observed: those exact ids, that exact total. v15 is **byte-identical for the third
consecutive run**, so no sampling-noise defence exists for any v16 change.

### The 12 regressions — zero new

All 12 carried from 3ac522a *and* 030a5ff. Five closed since 030a5ff (eval_368 `78b672c`;
eval_378/393 `bb30e25`; eval_127/208 the arm swap) and all five are now judge-correct.
**All 12 are v16 clarifications — there is not one row where v16 states a wrong number that v15
stated right.** Classing with the judge as tiebreaker on v15's own answer: **A=3** (extraction
coverage), **B=4** (never-guess correct — the gold is itself a clarification), **E=5** (deferred
patterns). C and D are empty: every output-shape row was closed by `bb30e25`, and the
retrieval-caused class died with the two-arm arm. Judge on v15: **8 wrong, 2 correct, 2
undetermined** — in two-thirds of the "regressions" v16 replaced a confidently wrong compliance
number with a question.

**"No class of regression" — satisfied outright** for the class the clause was written to catch
(zero rows where v16 is wrong and v15 was right, plus byte-zero fact-path divergence). **Not
clean** for a narrower residual class: **eval_280 and eval_323**, where a judge-confirmed *correct*
v15 answer became a clarification.

> **⚠️ CORRECTION (2026-08-08), recorded because the sequencing rationale was built on it.**
> The wiring order was set partly on my claim that headcount extraction "unblocks 3 rows on its
> own including both genuine regressions (eval_280, eval_323)". **Measurement disproved that.**
> Headcount extraction closes eval_280 only in combination with the C4 scope fix, and **it does
> not close eval_323 at all** — eval_323 needs pattern F. **The residual class therefore goes
> from 2 rows to 1 (eval_323), not to 0.** The sequencing decision still stands on its other
> grounds (cheapest item; moves the defective rate; closes eval_280 before wiring rather than
> after), but the file must not carry a claim measurement disproved.

### Judge range — four treatments, sign-stable

| Treatment | v15 | v16 | Δ |
|---|---|---|---|
| Reported (`build_confirmation_report`) | 267/360 = 74.2% | 291/362 = 80.4% | +6.2 |
| Common denominator, decisive in both arms (n=349) | 266/349 = 76.2% | 279/349 = 79.9% | **+3.7** |
| Every clarification = FAIL, undetermined excluded | 267/361 = 74.0% | 291/373 = 78.0% | +4.1 |
| Hard floor — clarifications *and* undetermined FAIL, /384 | 267/384 = 69.5% | 291/384 = 75.8% | +6.2 |

**Honest range +3.7 to +6.2; strictest like-for-like +3.7. No accounting flips the sign** — do not
quote +6.2 flat. Exclusion asymmetry measured precisely: of v16's 30 clarifications, **19 sit
inside the reliable set and are already scored FAIL**; only 11 are excluded outright (v15: 1). The
real gap is **10 rows, down from 14**. Undetermined fell 23 → 11. Of the 17 gains only eval_321 is
judge-wrong (1 in 17, against 5 in 19 last run).

### Two-arm retriever — settled, and the regex "loss" is largely phantom

Judged part 3: two-arm 78.7% vs single-arm 78.8% (**−0.17**), with **4 two-arm-only judge wins
against 11 single-arm-only**. Per-row on the 8 regex-flipped rows: eval_008/034/186 are
judge-**wrong under both arms** (phantom losses); **eval_331 is judge-correct under single-arm and
wrong under two-arm — the regex scored it backwards**; eval_019 is a real loss; eval_187
undetermined→correct; both single-arm wins (eval_127/208) are judge-confirmed. **Three independent
instruments now agree**, and the regex scorer has pointed the wrong way three times on the same
question set. **The raw +1.3 is, if anything, an understatement.**

### ⚠️ THE 15% CLARIFICATION TARGET WAS UNREACHABLE BY CONSTRUCTION — RETIRED, DO NOT REINSTATE

The all-clarification target (≤15% of compute-routed questions), set on 2026-08-08 alongside the
ADR bar, **has a measured floor of 15/102 = 14.7%** and is therefore not a product target with
headroom — it is the floor with a rounding error on top. The founder set it without knowing the
floor and retired it the same day. **Do not reinstate it.**

Why 14.7% is a floor: **15 of the 25 clarifications are questions whose GOLD ANSWER IS ITSELF A
CLARIFICATION.** Answering them at all would require guessing, which is precisely what R8 forbids:

| Bucket | n | ids |
|---|---|---|
| **Gold itself clarifies — correct behaviour, cannot be "fixed"** | **15** | FX 271/272/273/275/276 · missing prior context 299 · non-monetary basis 264/267/270 · pay basis unresolvable 291/292/295 · headcount genuinely absent 277/294/305 |
| Pattern **D** closes | 2 | 293, 296 |
| **Headcount extraction** closes — a NEW item | 3 | 280, 319, 320 |
| Pattern **F** closes | 2 | 323, 329 |
| Neither | 3 | 281 (approximation veto), 326 (residency split), 334 (composition) |

Achievable rate, **measured against the live extraction layer, not estimated**: today 24.5% ·
after D 22.5% · **after D + F 20.6%** · after D + F + headcount extraction 17.6% · after closing
literally every defect **14.7%**.

**REPLACEMENT METRIC — DEFECTIVE CLARIFICATION RATE.** Clarifications where the **gold answers**
rather than clarifies, as a share of compute-routed scored questions. **9.8% today (10/102),
target ≤5%, tracked in every paired run.** It measures product breakage rather than never-guess
behaviour, and unlike the all-clarification rate it can reach zero without violating R8.
After D + F + headcount extraction it is 3/102 = 2.9%.

### 🔎 NEW ITEM — HEADCOUNT EXTRACTION (discovered by measuring, not by assuming)

**Pattern F was assumed to close the multi-part rows. Measurement showed it does not.** Multi-levy
decomposition **already works** — eval_319 emits 2 clarifications, eval_320 emits 4, eval_323
emits 2, one per levy. What blocks them is `parse_count` returning `None` on rows where a
headcount is written in plain Swahili. **The binding constraint is headcount extraction, not the
D/F splitting patterns.** A 579-question survey found **13 real surface misses**, dominated by a
single gap: **the singular people-nouns (`mfanyakazi`, `mtu`, `mtumishi`, `mwajiriwa`) are absent
from `_PEOPLE_NOUN`** — only `kibarua` is there.

Four candidate changes, prototyped in scratch and **ablated over all 579 corpus questions**:

| | change | closes alone | needs |
|---|---|---|---|
| **C1** | singular `mfanyakazi mmoja` → 1, appended *after* the existing patterns | eval_320 | — |
| **C2** | digit + pay-verb (`18 wenye`, `14 wanaopata`) — already in `_COUNT_TOKEN`, absent from `parse_count` | nothing alone | C4 |
| **C3** | `count_transition_ordinal` surfaces: `kufikia N`, `nikafikia watu N` (today only `mfanyakazi wa N`) | nothing — **preparatory for F**, and it strengthens the M4 containment C1/C2 rely on | — |
| **C4** | per-person/aggregate **scope**: `kila mmoja` governs the SALARY, `jumla/wote` governs the ASK — not a conflict when the headcount is known and one amount was parsed | eval_275 copy | — |

**All four together: 4 answers change across 579 questions, 0 regressions** — eval_275 (copy
corrected to the FX question), eval_280, eval_319 and eval_320 all now match gold exactly.
C1+C2+C4 is the load-bearing combination; C3 changes 3 predicates and 0 answers.

**✅ SHIPPED `54b9b29`.** 587-question sweep: **13 rows change a predicate, 4 change an ANSWER, 3
stop being clarifications, 0 regressions.** eval_280 → TZS 1,728,000; eval_319 → SDL 245,000 +
NSSF 1,400,000; eval_320 → SDL TZS 0 + NSSF 80,000 + PAYE 78,000 + WCF 4,000; eval_275 → the FX
question. All four match gold exactly. The other 9 rows recover a count of 1 without changing any
answer and were each checked individually for a newly reachable defect — **none exists**:
eval_260 is held by the wrong-base rejection, and `wcf_applies()` / `nssf_applies()` take no
`employee_count` at all, so a recovered 1 cannot make a threshold-free levy "not applicable".
Only SDL has a count threshold and `applicability(sdl, 1)` correctly returns not-applicable.

R17: **12 adversarial in-scope probes**. **Two I mis-specified and rewrote rather than changing
the code** — hc_07 (I asserted `parse_count` must return `None` for "wafanyakazi 9 na ninaajiri
mfanyakazi wa 10"; it returns 9 *at baseline*, because the veto lives at the **consumer**, not
the parser) and hc_12 (I asserted `None` for "nimeajiri hadi **kufikia** wafanyakazi 11" — a
*completed* hire, so 11 **is** the current headcount). hc_12 exposed a pre-existing asymmetry:
`_SECOND_GROUP` matches `kufikia \d+` but not `kufikia wafanyakazi \d+`. Benign — count and
transition agree — and logged rather than silently relied on. A **test helper** was also wrong,
not the code: `_deterministic(text, required, computation_type)` had its last two arguments
swapped, which makes `required` a string and silently skips the amount field entirely.

Defective clarification rate: **9.8% → 6.9%** (10/102 → 7/102). Target ≤5%.

### Sequence set by the founder (2026-08-08)

**Wiring is approved in principle, gated on the DEFECTIVE clarification rate, not the retired
one.** Order: **headcount extraction → re-measure with a paired run → then wire.** Reasons: it is
the cheapest remaining item, it closes eval_280 (one of the two genuine regressions) before
wiring rather than after, and it moves the defective rate toward ≤5%. **Patterns D and F are held
until after the re-measure** — no stacking onto an unmeasured configuration.

**Next:** ~~a paired re-run~~ **BATCHED (founder, 2026-08-08).** A full paired run is ~3h of GPU
time and C1–C4 alone lands at 6.9%, above the ≤5% target — so no run until D + F are also in.
**One paired run at the end covering C1–C4 + D + F together**, so it measures the configuration
that would actually be wired rather than an intermediate.

## 🔬 D / F / eval_305 — ONE investigation round (2026-08-08, PROPOSAL — nothing implemented)

Remaining defective set after C1–C4 = **7 rows**: eval_281, eval_293, eval_296, eval_323,
eval_326, eval_329, eval_334.

### Pattern D — per-unit rate × per-month quantity

**Root cause.** eval_293 and eval_296 both reach `_amount_field` as *"multiple figures — role
ambiguous"* on exactly two figures. The rate and the quantity are both stated; nothing infers
that one multiplies the other. **Magnitude cannot be the discriminator** — the real rates here
are 1,500/piece and 18,000/day, so a size rule reads 1,500 as a count (this is already recorded
in the `_COUNT_TOKEN` note). **Structural rule:** rate = the figure before `kwa|kila <unit>`;
quantity = the figure adjacent to `<unit> N kwa mwezi`; monthly = rate × quantity, **only when
the quantity is explicitly per MONTH**.

**Reach:** 3 corpus questions (eval_293, eval_294, eval_296) + 1 probe duplicate. 9 further rows
match a rate but have no monthly quantity and **correctly decline** — including eval_291
(bi-weekly, calendar-dependent, gold clarifies), eval_292 (shifts per *day*), and gp_02/os_03
(the two-group twelve-person case).

**R17 — the naive rule produces TWO confident wrong numbers; the guarded form declines both:**
`dv_01` (two rate groups → 600,000 asserted as the payroll, the gp_02 failure mode with a
monthly quantity bolted on) and `dv_06` (two quantities, 3 shifts/day *and* 26 days/month →
650,000 where the truth is 1,950,000). **Guards required:** inherit `_has_second_group` /
`has_multiple_groups`, and decline when more than one rate or more than one monthly quantity is
present.

**Design constraint that must be stated in the code:** D yields **one person's** monthly pay,
never the payroll. It must feed `monthly_salary` / the per-person × headcount path, never
`gross_monthly_payroll` directly — otherwise eval_294 becomes "SDL = 3.5% × 1,200,000" for a
single driver, which the gold explicitly refuses.

### Pattern F is TWO mechanisms, not one

**F1 — per-levy amount anchoring (eval_323).** Multi-levy decomposition already emits one
sub-answer per levy, but every sub-question sees all four figures. **The obvious fix is unsafe:**
anchoring each levy to its nearest plausible amount gets eval_323 right *and breaks eval_327*,
anchoring both WCF and SDL to 300,000 when the correct base is the 4,600,000 group payroll —
a row that answers correctly today. A safe version must (a) gate on `parse_payroll_groups(text)
is None` so a resolvable group construction always wins, and (b) require the amount to be a
**payroll-label genitive inside the levy's own clause** (`SDL ya jumla ya mishahara ya TZS N`).
**Reach: 1 row.**

**F2 — multi-period split (eval_329).** Two named months, one payroll, a headcount either side
of the threshold. `count_transition_ordinal` already supplies the post-transition count (C3).
**Reach: 1 row** + 1 probe (ex_09). The third multi-month hit, eval_160, is a fact-path date
range and a false positive for this shape.

### eval_305 is a 5-row family, not a single row

`kiwango cha <levy> ni asilimia ngapi` — **the rate does not depend on the amount.** eval_111 and
eval_112 carry no figure and already work; eval_305, eval_314 and eval_315 carry one, and every
gold states the rate first and *then* optionally applies it. **Defective-rate impact: 0** (see
the borderline note below) — this is an answer-quality item, not a rate item.

### Does ≤5% actually get reached?

Denominator 102. **The answer depends on one borderline classification, so both readings are
given rather than the flattering one.**

| | eval_305 as *gold-clarifies* (my original call) | eval_305 as *defective* (strict reading) |
|---|---|---|
| today, after C1–C4 | 7/102 = **6.9%** | 8/102 = **7.8%** |
| + D | 5/102 = **4.9%** ✅ *one-row margin* | 6/102 = **5.9%** ❌ |
| + D + F1 | 4/102 = 3.9% | 5/102 = 4.9% ✅ |
| + D + F1 + F2 | 3/102 = **2.9%** ✅ | 4/102 = 3.9% ✅ |
| + eval_305 family | 3/102 = 2.9% | 3/102 = **2.9%** ✅ |

**The borderline:** eval_305's gold both *answers* (3.5%) and *asks* ("Thibitisha idadi ya
wafanyakazi"). I bucketed it as gold-clarifies; the stricter reading is defensible.

**Answer: yes, ≤5% is reachable — but not by D alone under both readings.** D alone clears it
only on the looser reading and only by a single row, so any one new defective clarification
puts it back over. **D + F reaches 2.9%–3.9% under either reading**, with a three-to-four-row
margin. That is the combination to build.

**What remains after all of it — 3 rows, ~2.9%, and worth leaving:**
eval_281 (the approximation veto firing on "hivi"/"kidogo" — narrowing it trades a clarification
for a guessed figure), eval_326 (resident vs non-resident, two individuals — needs a residency
split, D-RESIDENCY-1), eval_334 (base + allowance + one-off bonus — pattern E, blocked on a
`locked_facts` answer about allowance taxability, which is a **regulatory** question, not a code
one). None should be forced to close a metric.

### Recommendation

**Build D and F2. Build F1 only in its narrow gated form. Take the eval_305 family as a
separate small answer-shape item.** D is the load-bearing one and the only one whose absence
keeps the rate above target under both readings. F1 buys one row for the riskiest mechanism in
the set and is the one to drop if anything has to be dropped — but it also closes eval_323, the
**last remaining member of the residual regression class**, which is an argument for keeping it.

### ✅ ALL FOUR SHIPPED — `93e4d84` (2026-08-08)

599-question sweep: **7 rows change, all intended, 0 regressions, 6 clarifications closed.**
eval_293 → PAYE 36,000 · eval_296 → NSSF 46,800 · eval_323 → SDL 266,000 + PAYE 68,000 ·
eval_329 → Januari nil / Februari 105,000 · ex_09 → correct · eval_305 → the rate ·
**eval_314 → already correct and still correct**, its shape now matching a gold that states the
rate before applying it. That last one is a change to a *working* row, flagged as such.

**R17 — 21 probes; three earned their keep and none was reachable from the corpus.**
`dv_01` two rate *groups* → naive D asserts 600,000 as a **twelve**-person employer's payroll
(gp_02's failure mode with a monthly quantity bolted on). `dv_06` two *quantities* → naive D
returns 650,000 where the truth is 1,950,000. `fv_01` **eval_327** → naive F1 pins both WCF and
SDL to 300,000 instead of the 4,600,000 group payroll. All three now decline.

**Two defects of mine, caught by behaviour rather than review.** F2 was first nested *inside*
the crossing veto and could therefore never fire on eval_329, the one row it was written for —
a multi-period question inherently *has* a crossing, and this branch reads both counts instead
of assuming one. And `_CROSSING` written as `(?:{_PEOPLE_NOUN}\s+)?` binds loosely, so only the
last alternative carries the `\s+` and `nikafikia WATU 12` silently stopped matching when the
surface moved out of `routing.py`; ex_09 changing behaviour exposed it. Both fixed at source.

Also removed a duplication C3 had introduced: the threshold-crossing surface now has **one
owner** (`swahili_numbers._CROSSING`) and `routing._COUNT_TRANSITION` delegates to it, with a
test pinning the delegation. Three copies of one safety predicate is the dual-file divergence
CLAUDE.md warns about.

**Defective clarification rate: 7.8% → 2.9%** on the founder's strict reading, against ≤5%.
Verified offline end-to-end. **587 tests pass.**

### ⛔ eval_281 — WON'T FIX BY DESIGN. Do not reopen this chasing a number.

"Mshahara wake ni mkubwa kidogo, unafika TZS 920,000 **hivi**" clarifies because the
approximation veto fires on the hedge. The gold uses 920,000 as stated, so this reads as a
miss — and closing it means **narrowing an approximation veto so the model treats a hedged
figure as exact**. That trades a clarification for a guess, which is the wrong direction under
R8 and the exact trade the never-guess contract exists to refuse. It stays open, and the
defective rate carries it at ~1% forever. A future session finding this row while chasing a
metric should stop here.

eval_326 (residency split, D-RESIDENCY-1) and eval_334 (blocked on a **regulatory** question
about allowance taxability, not a code one) are the other two deliberate residuals.

## ✅ BATCHED PAIRED RUN — RUN, at `1476caa` (2026-08-09)

> **Superseded by the `1476caa` entry at the top of this file.** The run happened, the artifact
> is fetched, sha256-verified and committed to `eval/results/`, and every number was recomputed
> from raw rows. The pre-registration recorded below **hit its total and its direction exactly**
> (9 flips, all FAIL→PASS, raw 314/384; defective rate 3/102), and the pre-registered watch row
> eval_314 held. Kept below for the record of what was predicted before the result was known.

`kaggle/eval_phase_d_paired.py` at HEAD. Retrieval is **unchanged** from 5d0dcb7, so unlike the
last run there is no term that can lose rows — the projection's only uncertainty is model-side
movement on the compute prompts.

**Pre-registered, recorded before the run:** 10 rows change on the 400; 9 were failing and
should now pass; **raw 314/384 vs v15 300/384 = +3.6 pts** (from +1.3 at 5d0dcb7). Defective
clarification rate **3/102 = 2.9%**. The method has two exact calibration points (5d0dcb7 hit
its total *and* its row ids).

**The one row to watch is eval_314** — already passing, shape changed. If it flips to FAIL the
rate branch is over-broad and should be narrowed to rows that were clarifying.

The harness now computes the **defective** rate against ≤5% and reports the all-clarification
rate as context only, with the retired target's 14.7% floor stated inline so it cannot be
reinstated by accident. `GOLD_CLARIFIES` is subtracted rather than the defective rows listed,
which **fails safe**: a row clarifying for the first time counts as defective until adjudicated.

### Logged, not fixed

**eval_305** — "Kiwango cha SDL ni ngapi kwa mtu mwenye mshahara wa TZS 480,000?" wants "3.5%,
and it is not a per-person rate". That is an **answer-shape** item, not copy and not extraction.
Filed with the applicability output-shape family and **taken with D/F**, deliberately not folded
into C1–C4. (The D/F round below found it is one of a **5-row family**, not a single row.)

**`_SECOND_GROUP` / `kufikia` asymmetry (pre-existing, exposed by probe hc_12).**
`_SECOND_GROUP` matches `kufikia \d+` but **not** `kufikia wafanyakazi \d+`, so
eval_329 ("nikaongeza mmoja kufikia 10") makes `parse_count` decline while hc_12
("nimeajiri hadi kufikia wafanyakazi 11") does not. **Benign today** — in the hc_12 shape the
static count and `count_transition_ordinal` agree (both 11), so no consumer can be handed a
stale count — and narrowing it further would cost clarifications on completed hires, where the
count *is* the answer. Deferred deliberately; revisit only if a row appears where the two
signals disagree.

**Diagnostic invalidated by the swapped-argument test helper (part of the record).**
`_deterministic(text, required, computation_type)` had its last two arguments swapped in a
throwaway diagnostic during the **copy-fix investigation** (eval_264 / eval_270 / eval_277 /
eval_305). That makes `required` a *string*, so the amount field is silently never computed and
every row reports `det={}`. **That trace was garbage and should not be cited.** No conclusion
changed: the copy fixes in `f3e0480` were built on the run's actual v16 answers and on the
587-question sweep, not on that trace. The same bug then produced one false test failure in the
C1–C4 round, which is how it was caught; the signature order is now called out in a comment in
`tests/test_headcount_extraction.py`.

### 🅳 DEFERRED — taken up after the current fix cycle closes (set by the founder, 2026-08-08)

Neither is part of the batched paired run. Both are logged here so the cycle can close without
losing them.

---

**D-1 — tokenizer / `fix_mistral_regex`. Supersedes the 2026-07-28 item below (§ *OPEN ITEM —
tokenizer `fix_mistral_regex`*), which scoped it as a warning to look at; this scopes it as a
possible train/serve mismatch.**

The adapter repo emits a warning referencing **Mistral-Small-3.1-24B** while the base is
**`McGill-NLP/AfriqueLlama-8B`**. The asymmetry it points at is **verified in the code, not
assumed** — training and serving load the tokenizer from *different repos*:

| where | line | loads from |
|---|---|---|
| training | `kaggle/train_ddp.py:183` | **`BASE_MODEL`** |
| production | `chike-inference/modal_app.py:218` | **`ADAPTER_REPO`** |
| gate | `kaggle/eval.py:134` | `ADAPTER_REPO` |
| paired harness | `kaggle/eval_phase_d_paired.py:245` | `ADAPTER_REPO` |
| every probe | `gn487a_inversion_probe.py`, `faithfulness_probe.py`, `extraction_stress_test.py`, … | `ADAPTER_REPO` |

Nothing in the repo passes `fix_mistral_regex` anywhere, so the pre-token split is whatever each
repo's `tokenizer.json` specifies. If the two differ, **Swahili segmentation at serve time differs
from segmentation at train time on every answer** — which would sit underneath every gate number
ever collected, not just the recent ones.

**It is path-neutral, so it cannot explain any v15-vs-v16 delta.** Both arms load the same
tokenizer from the same repo in the same process. That is *why* it is deferrable — and equally why
deferring it does not make it smaller. It is a real defect either way.

**Diagnosis is CPU-only and needs no GPU slot:**
1. Round-trip a Swahili sample under both tokenizers, ± `fix_mistral_regex=True`; **diff token
   ids**, not decoded strings — a lossless round-trip proves nothing about the split.
2. Inspect both repos' `tokenizer.json` / `tokenizer_config.json` / `chat_template`.
3. Establish **how the Mistral reference got into the adapter repo** — provenance is the actual
   question; a divergent split is the symptom.

**Founder position: the Mistral reference should not be there.** If the diagnosis shows it is
live-affecting, it touches production and gets **its own change cycle** — not a fold-in.

---

**D-2 — byte-level extraction. A design question to answer, NOT a build to schedule.**

Most extraction defects this cycle were **surface-pattern brittleness**, not logic errors:
`mshahara`/`mishahara`, `wenye` vs the people-noun list, `kufikia wafanyakazi` vs bare `kufikia`,
spelled vs digit counts. Each was fixed by enumerating one more word pattern. The question is
whether byte- or character-level parsing would handle Swahili morphology better than continuing to
enumerate.

**It is not obviously yes, and the assessment has to be honest about three properties the regex
layer currently gives us for free:**
- **Auditable and deterministic** — every answer traces to a named pattern, and a reviewer can
  read why a row matched.
- **Fail-safe in the never-guess direction** — when the parser cannot resolve, it declines and the
  system clarifies. A learned or fuzzy matcher that degrades into a *plausible* parse instead of no
  parse trades clarifications for confident wrong numbers, which is the wrong direction (the same
  reasoning that made **eval_281 a permanent won't-fix**).
- **Validatable by sweep-and-probe** — the 620-row sweep plus R17 adversarial probes is the
  instrument that has caught every confident wrong number this cycle (dv_01, dv_06, fv_01 were all
  found by writing the probe first). Any replacement has to be measurable the same way.

**If determinism cannot be preserved, say so and close the item.** A brittle-but-auditable layer
beats coverage without the guarantee — that conclusion is a legitimate and expected outcome of this
investigation, not a failure to deliver one.

### Also shipped this session

`f3e0480` — two of the four wrong-question clarifications: eval_264 (a **receipt count** is not a
payroll base; `risiti` was missing from `_OBJECT_COUNT` beside invoice/ankara) and eval_270 (an
**aggregate** ask answered with a question about one worker's month). 579-sweep: **exactly 2 rows
changed, zero collateral**; 491 tests pass. eval_275 and eval_305 deliberately **not** fixed there —
275 is a symptom the C4 change removes at source, and 305 needs a **rate**-question answer shape,
which is logged rather than smuggled into a copy commit.

---

## PHASE D RE-RUN (030a5ff) — ADR BAR PASSES; four fixes shipped; single-arm re-run packaged (2026-08-08)

Artifacts: **`eval/results/gate_phase_d_paired_030a5ff.json`** (fetched from HF and
**sha256-verified** `003ff4f7fa3b4081`, `complete: true`, `clone_head == live_head == 030a5ff`)
+ **`..._findings.json`** (the adjudication). **Every number was recomputed from the raw
`v15_results` / `v16_results` / `part3_results` rows, independently of the summary block. All
recomputations matched.**

### Headline

| | 3ac522a | 030a5ff |
|---|---|---|
| ADR bar raw | −6.8 **FAIL** | **+0.5 PASS** |
| ADR bar reliable | −3.7 **FAIL** | **+1.1 PASS** |
| compute raw / reliable | −29.4 / −23.0 | −2.0 / **+4.0** |
| v16 clarifications | 61 (compute 56) | 32 (compute 27) |
| gains / regressions | 11 / 37 | **19 / 17** |

**ADR 0001 §10 is satisfied for the first time.** Pre-registered projection was +7.75 raw pts;
the actual swing was **+7.3**. The projection predated the result and is in the harness
docstring at `030a5ff` — it was not retrofitted.

**The harness is deterministic.** The v15 arm is **byte-identical across both runs (400/400
generations, 0 pass-flips)** and part 3 reproduced exactly. There is no sampling noise term:
all 35 changed v16 rows are attributable to code.

### Adjudication of the 17 regressions — only SIX are real

Classing extended with two new classes. The frontier judge was applied to **v15's** answers,
because a regression is only real if v15 was right. **On 9 of the 17 it was not.**

| Class | n | ids |
|---|---|---|
| A extraction coverage failure | 4 | eval_280, 319, 323, **368** |
| B never-guess CORRECT (gold is itself a clarification) | 5 | eval_271, 281, 291, 294, 295 |
| C v16 correct, scorer false-fail on SHAPE | 2 | eval_378, 393 |
| **D retrieval-caused fact error — NEW CLASS** | 2 | eval_127, 208 |
| E rate × quantity / known deferrals | 4 | eval_293, 296, 329, 334 |

- **Nine are v15 false-passes.** The regex scorer credits v15 for wrong answers that echo the
  question's own digits: **eval_293 answers PAYE = TZS 0 on a 600,000 salary**; **eval_329
  answers TZS 1,925,000 where gold is 0 and 105,000**.
- **Two are v16 false-fails** the judge confirms correct (Class C — both fixed this session).
- **Class D is the only avoidable quality loss**, and it is entirely the two-arm retriever.
  **eval_208 asserts a "kizingiti cha TZS milioni 90" VAT threshold that does not exist** —
  an R2-adjacent fabricated figure. Single-arm answers both correctly.

**"No class of regression even at parity" — SATISFIED, conditional** on removing Class D and
fixing eval_368. Both done this session.

**compute raw −2.0 explained:** exactly 13 gains − 15 regressions in that bucket. 13 of the 15
are clarifications and the judge calls v15 wrong on 9. The same bucket on the reliable
denominator is **+4.0**.

### Judge comparison — a RANGE, and no accounting flips the sign

The exclusion asymmetry is **14 rows, not the 27** the graded counts (379 vs 352) suggest: 18
of v16's 32 clarifications sit *inside* the reliable set and are already scored FAIL.

| treatment | v15 | v16 | Δ |
|---|---|---|---|
| as reported | 267/359 = 74.4% | 291/363 = 80.2% | +5.8 |
| **common denominator — 346 rows decisive in BOTH arms** | 264/346 = 76.3% | 276/346 = 79.8% | **+3.5** |
| clarifications counted FAIL | 267/360 = 74.2% | 291/377 = 77.2% | +3.0 |
| hard floor (clarifications AND undetermined FAIL) | 267/384 = 69.5% | 291/384 = 75.8% | +6.2 |

**Honest range +3.0 to +6.2; strictest like-for-like +3.5. Do not quote +5.8 alone.**
Symmetrically, **5 of the 19 gains are judge-FALSE** (eval_008, 034, 186, 321, 331) — four of
them credited by the two-arm retriever.

### 🚨 The regex scorer pointed the wrong way TWICE on a byte-identical run

| instrument | two-arm | single-arm | Δ |
|---|---|---|---|
| regex raw | 78/90 = 86.7% | 74/90 = 82.2% | **+4.4** |
| judge-augmented, common denominator (n=85) | 67/85 = 78.8% | 67/85 = 78.8% | **0.0** |
| pure judge, both arms graded (n=81) | 53/81 = 65.4% | 60/81 = 74.1% | **−8.6** |

Part 3 reproduced **exactly** from `3ac522a`, so +4.4 was never a sampling fluke — it is a
systematic property of **number-set-intersection scoring applied to a retriever whose entire
job is to inject more numbers into the prompt.** On eval_331 the two instruments disagree on
**direction**. This settles the two-arm question permanently.

### New vs carried

16 of 17 carried. **21 regressions fixed, 0 gains lost, 8 new gains** (eval_251/252/255/256/
262/263/265/266 — all PREREQ-2 Tier 1–2, all judge-confirmed).

**One new, and it was mine: eval_368.** Pattern B added `wa muda` / `wa kudumu` to
`_GROUP_MARKERS`; as bare alternatives they fired on **one** group described as part-time, so
`has_multiple_groups` → True → `parse_count` → None → the applicability route asked for a
headcount that was in the question. **This is the nat_07 class, flagged in the adjudication
before being fixed, not slipped in.**

---

## ✅ The four approved items (IMPLEMENTED 2026-08-08)

### 1. eval_368 — employment type is a split only when BOTH sides are named (`78b672c`)

A real split names both sides, so require both. Blast radius measured by a **561-question
deterministic sweep: exactly 3 questions changed, all three wrong before** — eval_368,
eval_377 (*a single* part-time employee), and eval_225 (`"muda wa siku 30"`, a time period
with no employment sense at all). Only eval_368 changes its answer.
Must-not-break pair pinned by name: **edge_p04** and **ex_10**.
R17: `eval/accuracy_gate/employment_type_probes_008.jsonl` (8 probes).

### 2. 🔴 BLOCKING — single-arm is now the v16 arm; paired re-run packaged (`d0e7390`)

Every paired run so far measured v16 **with** the two-arm retriever. **The ADR bar has never
been measured on the configuration that would ship.** `orch` → `single_arm.retrieve_facts`;
`orch_alt` → `two_arm.retrieve`. Part 3 is **kept and inverted** so the dropped variant is
re-tested at the new HEAD rather than assumed to carry.

**PRE-REGISTERED EXPECTATION, recorded before the run:**
> deterministic **+7** (eval_368; eval_247/371/372/378/379/393) · retrieval **−4** (6 lost, 2
> regained on the 90 measured) · net **+3 → 305/384 vs v15 300/384 = +1.3 pts raw.**

The retrieval term is uncertain **in both directions**: its −4 comes from the same regex
scorer that credited two-arm +4.4 twice while the judge scored it 0.0 / −8.6, so −4 is the
**pessimistic** reading. **100 compute-routed second-arm-eligible questions are outside part 3
and outside this projection entirely.** The 030a5ff projection landed +7.3 against +7.75 —
one calibration point, no more.

**Founder instruction, recorded in the docstring:** *if raw lands slightly negative while the
judge holds, bring the result rather than pre-arguing it — decide against a real number, not a
projected one.*

### 3. Output shape — TZS 0, and polarity (`bb30e25`)

**eval_378** ("SDL inayolipwa ni **ngapi**?") replied `"SDL haihusiki…"` — judge-confirmed
correct, scored FAIL for never stating a figure. Below the threshold the obligation is nil
whatever the payroll is, so say so, and stop asking for a payroll that cannot change the
answer (**eval_379**). No new regulatory fact: this is `SDL_MIN_EMPLOYEES`, already locked.

> **🚨 The first draft of this branch shipped a confident wrong number TWICE, and the
> 569-question sweep caught both — the probes did not.** `gp_02` ("vibarua 8 … na 4 …") is a
> **twelve**-person employer and it answered TZS 0 on the first group's 8; and "wafanyakazi 9
> na ninaajiri mfanyakazi wa 10" answered TZS 0 where SDL **is** due. Two guards added:
> `swahili_numbers.sole_headcount` (decline whenever a second count exists in **any** form —
> `_SECOND_GROUP` only ever caught a *spelled* one) and the **M4 count-transition veto**,
> which now governs this branch too. **Third occurrence of the nat_07 class this cycle.**

**eval_393** ("wafanyakazi 9 **haitakiwi** kulipa SDL, **sivyo?**") replied *"Sawa kabisa …
**Hapana.** SDL haihusiki …"* — two opposite polarity markers agreeing with each other. A
negated premise the verdict **confirms** is agreed with. Gated on **both** the tag predicate
and `applicable is False`, so the **15 false-premise tag questions** (eval_335–350) keep their
correct `"Hapana."` lead. Only 2 of the 17 corpus tag questions carry a negated premise.

### 4. Clarification copy — ask for what is actually missing (`bb30e25`)

eval_291 (TZS 320,000 **per fortnight**) and eval_294 (TZS 80,000 **per trip** × 15) reach the
extractor in the same `role ambiguous` state as a per-person salary and were asked *"is that
per employee or the total?"*. The missing input is the **monthly** figure. **Both still decline
to compute** — converting a rate is pattern D and stays deferred — so a false positive costs a
differently-worded clarification, never a wrong number.

**Measured blast radius for items 3+4 (569-question sweep): 14 corpus questions changed, 0
regressions, +6 on the deterministic path** — eval_247/371/372/378 (judge said CORRECT, scorer
said FAIL for want of a figure), eval_379 (clarification → answer), eval_393 (polarity).
**eval_378 and eval_393 were 2 of the 17 regressions.**

### Tests that asserted the old behaviour

Two pre-existing tests asserted the old wording and **one encoded the old call sequence** — the
zero branch sits *before* slot extraction, so that model call no longer happens on that path.
Both updated with the reason in place, not silenced. **One probe (os_08) was mis-authored**: it
asserted the tag predicate returns False for eval_391 when it correctly returns True, the
safety coming from the second gate. **The probe was rewritten; the code was not.**
456 tests pass.

---

## 📊 CLARIFICATION RATE — a WIRING PRECONDITION alongside the ADR bar (set 2026-08-08)

**Target: ≤ 15% of compute-routed questions.** It was **27/102 = 26.5%** at `030a5ff` and is
predicted at **25/102 = 24.5%** for the next run (eval_368 and eval_379 now answer) — **above
target, known in advance, and not a reason to hold the run.**

Now computed, printed with the clarified ids, and carried in the summary and artifact by
`kaggle/eval_phase_d_paired.py`. **The gate will never surface this on its own:** every
extraction fix converts a clarification into an answer, which the ADR bar rewards only if the
answer is *also* right, so a run can pass the bar while a quarter of numeric questions ask a
question back.

**The case FOR the clarifications is strong and should not be lost in chasing the target.**
Across all 32 at `030a5ff`, the frontier judge says **v15 answered WRONG on 20**, correct on 4,
undetermined on 3, ungraded on 5. Twenty times a clarification replaced a confident wrong
number. **Not every clarification is a defect** — the foreign-currency (eval_271/272/273/275/
276) and prior-context (eval_297/298/299/300) families **should** clarify, which puts a floor
of roughly 9–12% under the rate. Reaching 15% needs patterns D and F **plus** the p04-family
extraction work; adjudicate the list before treating the gap as a work queue.

---

## 🔭 Not fixed, deliberately

- **eval_376** ("sina wafanyakazi kabisa — SDL yangu ni ngapi?") still clarifies. `detect_intent`
  returns `none` because the router requires a figure to take the compute path, and the only
  "figure" here is an implicit zero. **That is a ROUTER change, not an output-shape one**, and
  routing changes are exactly what must not be stacked onto an unmeasured configuration.
  `swahili_numbers.states_no_employees` already exists and is wired for when it is approved.
- **Patterns D (+2) and F (+4)** — held until the bar is measured on the shipped config.
- Unchanged tracked-open items: eval_281 (permanent won't-fix), pattern E (won't-do —
  a `locked_facts` question first), eval_260 + `scoring._YN_NEG` `hai-` verb gap, eval_191
  mislabel, `kaggle/eval.py` payroll guard, `_VAGUE`'s `kiasi cha` over-match, SAFETY-2 /
  D-RESIDENCY-1, tokenizer `fix_mistral_regex`, item 4 hybrid retrieval, eval_280.
- **Outstanding, unrelated:** the Modal token rotation has still not taken effect.

**Next: the founder runs `kaggle/eval_phase_d_paired.py` on Kaggle at this HEAD.**
Secrets `AFRICA_GIANTS` + `OPENROUTER_API_KEY`, GPU + Internet ON.


## 🏁 PHASE D COMPLETE — v16 NOT WIRED; two-arm retriever NOT SHIPPED (2026-08-07)

Artifacts: **`eval/results/gate_phase_d_paired_3ac522a.json`** (raw, fetched from HF and
**sha256-verified** `1e3a962695fa5cfd`, `complete: true`) + **`..._findings.json`** (the
adjudication). **Every number below was recomputed from the raw `v15_results`/`v16_results`/
`part3_results` rows, not read from the script's summary — the independent recomputation
reproduced the summary exactly.**

### The four calls

**(1) v16 is NOT wired. The ADR bar genuinely failed.** raw **−6.8**, reliable **−3.7**;
ADR 0001 §10 requires v16 ≥ v15 on both. **The failure is real, not a scorer artifact:
29 of the 33 clarification-regressions are v16 defects.** Not a close call to be argued away.

**(2) The two-arm retriever is NOT shipped. Settled.** See the Run 2 part 3 section below.

**(3) The judge-augmented "+1.8" is NOT like-for-like — do not quote it.** `judge_gradeable`
excludes clarifications; v15 had 5 and v16 had 61, so **v15 was judged on 379 questions and v16
on 323**, and the 56 excluded are precisely the ones v16 clarified — the questions it did worst
on. Correct framing:
- like-for-like on the 323 both arms were judged on: **v15 67.2% vs v16 72.8% → +5.6 pts**
- counting clarifications as failures (what raw does): **v15 60.4% vs v16 62.0% → +1.6 pts**
- **Honest range: v16 leads by +1.6 to +5.6 pts on judged correctness**, depending entirely on
  whether a clarification counts as a failure. `+1.8` sits inside the band but was derived
  across different question sets. **Cite the range, never the +1.8.**
Mechanism confirmed: judge false-PASS candidates **v15 41 vs v16 30** — the regex scorer credits
v15 for wrong answers more often, which is why raw says −6.8 while judged correctness favours v16.

**(4) The fact path is clean.** **+2.2 raw / +2.3 reliable at n=193.** Wiring carries no
fact-path regression risk — now confirmed at scale (005b said this at n=5, Run 3 at n=21).

### Adjudication of the 33 clarification-regressions

| Class | n | Meaning |
|---|---|---|
| **A — extraction failure** | **22** | information WAS present and sufficient; v16 failed to extract |
| **C — input not needed** | **7** | yes/no, wrong-base or definitional; no salary was ever required |
| **B — v16 correct** | **4** | information genuinely absent |

**But the baseline is false in 16 of the 33:** the judge says v15's answer was WRONG on
eval_242/253/259/269/271/279/281/291/293/294/296/324/327/329/334/399 — v15 computed SDL on a
bank loan, WCF on vehicle value, PAYE on base salary only, `1,500 ÷ 100`, and read *9 machines*
as *9 workers*. **Genuine user-facing losses — v15 judged correct AND v16 clarified — number
NINE, not 37**; seven more are judge-undetermined. On three Class-B cases (eval_291/294/295)
**the gold answer itself asks for clarification**, so v16 matched gold and was scored as failing.

### The 4 non-clarification regressions — adjudicated

- **eval_127** and **eval_208: GENUINE v16 regressions, and BOTH are CAUSED BY THE TWO-ARM
  RETRIEVER.** Under single-arm, v16 answers both correctly. Two-arm invented a *"TZS milioni
  90"* six-month VAT threshold (eval_208) and produced a self-contradictory SDL/PAYE deadline
  answer — *"zinawasilishwa kwa nyakati tofauti"* followed by the same date twice (eval_127).
- **eval_378: scorer artifact.** Both arms judged correct; v16's *"SDL haihusiki: una
  wafanyakazi 8"* is arguably crisper — the regex wanted an explicit TZS 0.
- **eval_393: scorer artifact + a real presentation defect.** Both judged correct, both
  `reliable=False`, but the merged v16 reply opens *"Sawa kabisa"* and then says *"Hapana"* —
  surface polarity self-contradicts. A merge/render issue, not a wrong answer.

**So v16's only two genuine non-clarification regressions in the entire 400 would not exist
under single-arm retrieval.**

### Run 2 part 3 — DON'T SHIP the two-arm retriever (SETTLED)

Recomputed: raw two-arm 78/90 = 86.7% vs single-arm 74/90 = 82.2% (**+4.4**); reliable 58/66 vs
56/65 (**+1.7**). That reverses the earlier lean — **until the judge is applied**:
- **4 of the 6 two-arm-only passes are judged WRONG** (eval_008, eval_034, eval_186, eval_331).
  Only eval_019 and eval_187 are judge-confirmed correct.
- Both single-arm-only passes (eval_127, eval_208) are the confirmed two-arm **harms** above.
- **Harness limitation: the 90 part-3 rows were never judged (0/90)** — the overlay ran on
  res15/res16 only. Fix before any future de-confound run.

Net: **2 confirmed wins, 4 illusory ones, 2 confirmed harms.** Worse than a wash, and under the
approved rule a wash already keeps single-arm. **Three independent measurements have now failed
to demonstrate a benefit** (parts 1–2: 1 recovery vs 86 non-gold appends; Set A: zero rank
changes across 21 critical queries; part 3: net negative once judged). Production keeps
single-arm — the configuration it already runs.

### 🔜 BLOCKING PREREQUISITES for re-running Phase D

**PREREQ-1 — applicability routing (Class C, 7 confirmed). DO THIS FIRST.** Higher severity
*and* the smaller change. A wrong-base or yes/no question must **never** demand a salary. Asking
a user for their payroll when they asked whether their **electricity bill** affects SDL is worse
than a wrong number — **it validates the false premise.** This **absorbs the previously-parked
p04 item** ("natural-levy applicability route, structural"), which now has 7 confirmed instances
instead of 1 constructed example: eval_124 (headcount-timing yes/no), eval_253 (bank loan),
eval_254 (shop market value), eval_258 (office rent), eval_259 (vehicle value), eval_261
(electricity), eval_269 (9 machines).

**PREREQ-2 — extraction coverage (Class A, 22 confirmed).** Sub-patterns: per-person-vs-total
**stated in the question** but not parsed (the largest group); fractional headcounts (*robo ya
24*, *theluthi mbili ya 30*, *robo tatu ya 16*, *nusu ya 14*); rate × quantity (*1,500 kwa
kipande × 400*, *18,000 kwa siku × 26*, *80,000 kwa safari × 15*); multi-component pay (*msingi
+ posho + bonasi*); multi-group and multi-branch payrolls; period conversion (bi-weekly,
commission). IDs enumerated in the findings artifact.

**Contamination note:** eval_191's mislabel (tracked separately) sits inside this denominator.

**Next session resumes at PREREQ-1.**

## ✅ PREREQ-1 — applicability routing + base rejection (IMPLEMENTED 2026-08-07)

**v16 orchestrator only. Production (`pipeline_v15`) is unchanged — no Modal redeploy.**

### Root cause: four mechanisms, not one

`_WRONG_BASE` **fires correctly** on 4 of the 7 Class-C questions. It was neither absent nor
overridden — it was **recorded and then never read**.

| | ids | state | reply before |
|---|---|---|---|
| **M1** copy has no `wrong_base` branch | 253, 254, 258, 259 (+251/252/255/256/260/262) | `detect_wrong_base=True`, reason `wrong_base (non-payroll figure)` | *"how many employees?"* (SDL — the `missing==['employee_count']` branch fires first, so money is never mentioned) or *"tell me the salary"* (WCF/NSSF/PAYE) |
| **M2** wrong_base masked | 261 | `_VAGUE`'s `\bkiasi\b(?!\s+gani)` matches "**kiasi cha** SDL ninachodaiwa" — a definite reference; `global_veto` overwrites the reason | *"how many employees?"* |
| **M3** no pattern for an object COUNT | 269 (+263/265/266) | `detect_wrong_base=False`; small-int guard catches it instead — true observation, wrong consequence | *"how many employees?"* |
| **M4** count transition | 124 | cue `inatakiwa kulipwa` **does** match, but `_COUNT_TRANSITION` vetoes `is_applicability_question` | *"tell me the salary"* |
| **M5** no natural applicability arm | p04 | path 2 requires a money ask, so a naturally-named levy could never reach compute; `inanihusu` also absent from the cues | free fact generation (the 0.5%-vs-3.5% wrong rate) |

**The family is 15 gate questions, not 7.** Class C caught only the 7 that *regressed*;
eval_251/252/255/256/260/262/263/265/266 failed in **both** arms. All 15 clarified, all 15 failed.

### What shipped

- `chike/rules_engine/base_rejection.py` — `reject_base()` returns a `ComputationResult(applicable=False)`
  naming the correct base and rejecting the stated figure. Rates come from `rates.py`; **no new
  regulatory fact is encoded**, only Swahili framing. Correction mandatory, invitation optional
  (`invite=False`) — the failure mode is demanding a salary *in place of* the correction, not
  offering it after; 6 of the 10 golds invite it.
- `rules_engine.sdl_crosses_threshold(ordinal)` — M4. **Raises** below the threshold: the
  never-guess veto is not loosened, it is given the one case it can answer deterministically.
- `swahili_numbers.detect_rejectable_base()` — structural, keyed off `detect_wrong_base` and the
  parsed amounts rather than the Extraction reason STRING, so eval_261's masked reason is
  irrelevant. `_VAGUE`'s over-match is logged for PREREQ-2, untouched.
- `routing`: `+inanihusu/inakuhusu/inatuhusu` cues; `asks_applicability()` split from
  `is_applicability_question()`; `count_transition_ordinal()`; **path 2b** natural applicability.
- `Orchestrator._deterministic_answer()` — body blanked, `working` rendered alone,
  `needs_clarification=False`, no model call.

### Blast radius — 18 changed / 483, +15 / −0

`compute_clarify → base_rejection` 15 · `→ count_transition` 1 · `compute → applicability` 1 ·
`fact → applicability_clarify` 1. The **one** currently-computing question diverted is eval_363,
where `sdl_applies(9)` gives the identical verdict plus a leading "Hapana." the yes/no scorer needs.
Projected **+15 raw on the 400 (+3.75pp)** — closes ~55% of the raw −6.8 gap. **Not sufficient
alone; PREREQ-2 is still required.**

### R17 earned its keep again

The first guard ("wrong_base AND exactly one plausible figure") passed **all 483 corpus questions**
and was still over-broad. Four authored probes caught it: ap_07–ap_10 state a *legitimate payroll*
while a wrong-base WORD sits nearby, and all four were wrongly rejected. Fix: require the **absence
of `mshahara`/`mishahara`** — none of the 11 wrong-base gate questions contains it. Fails safe.
The sweep separately caught **`nahusika na`** substring-matching "i-nahusika na" in eval_100
(a base-SCOPE question that passes today); dropped, with a regression test forbidding re-adding it.
Probes committed as `eval/accuracy_gate/applicability_adversarial_in_scope_017.jsonl`, wired into
`tests/test_applicability_routing.py`.

### Necessary but NOT sufficient for p04

p04 now routes correctly to applicability, then **clarifies for the headcount**, because
`parse_count` does not read `vibarua 8` + `wawili` (nor the spelled-out `tisa`). The 8+2=10
aggregation is **PREREQ-2**. Interim state for SDL natural applicability is an honest redundant
question instead of a free-generated wrong rate — the R8-consistent direction, but p04's gold
still needs PREREQ-2.

### Production isolation proven, not assumed

`pipeline_v15.py` **is** production and imports `routing` for one predicate,
`is_uncomputable_payroll_amount`. Diffed old-vs-new over **500 questions: 0 differences.** It also
holds structurally (path 2b requires no money ask; the guard requires one) — pinned by
`test_path_2b_can_never_reach_the_production_fabrication_guard`.

### Deliberately not done (queued, same decision class)

- **eval_260 accepted as a 1-row miss.** Its *gold* parses as polarity `yes` (`haitumiki` is not in
  `scoring._YN_NEG`, and the gold has no leading "Hapana."), so a correct reply scores FAIL.
  **`_YN_NEG` `hai-` verb gap logged** with eval_191's mislabel and `kaggle/eval.py`'s payroll
  guard — all three move the gate denominator and are not to be reopened piecemeal.
- **`_VAGUE` `kiasi cha` over-match** → PREREQ-2.
- **adv_06** stays on fact: the number-free form of path 2b would divert it to a correct-but-partial
  deterministic yes that ignores the insurance half. Not worth widening for.

## ✅ PREREQ-2 Tiers 1–2 — narrowed false vetoes + anchored figures (IMPLEMENTED 2026-08-07)

**v16 orchestrator only. Production unchanged — no Modal redeploy.**

### The dominant blocker

`_amount_field`'s `if len(amounts) > 1 → LOW ("role ambiguous")` fires before any role
assignment is attempted — **14 of the 22 Class-A questions**. Every downstream capability
(per-person × count, group sums, rate × quantity) is unreachable because the parser bails
first. Tiers 1–2 do **not** relax that rule.

### The 8 patterns (all *narrowings*, or selection where the parser already gave up)

| | defect | fix | reach |
|---|---|---|---|
| **G** | `_ALLOWANCE` matched `pamoja na` in "mwajiri **pamoja na** mfanyakazi" — the NSSF **party** | require a real pay component | 3 hits, 0 computing |
| **K** | `_VAGUE` matched `"kiasi **cha** SDL"` — a definite reference | exempt `kiasi cha` only | 2 hits |
| **A1** | `_APPROX` matched `kama` as *if*/*as* ("**Kama** kawaida", "mimi **kama** mwajiri") | require a following quantity | **39 hits → 3** |
| **H** | `_ANTECEDENT` matched demonstratives modifying a **named** noun ("**ile tozo** ya mafunzo") | strip demonstrative + definite noun | 18 hits, 0 computing |
| **A2** | a hedge the *same sentence* corrects ("wengi sana karibu, **lakini hasa ni 18**") | precision marker overrides the veto | 3 |
| **J** | a payroll-**labelled** figure discarded among several | anchor-select it | 2 |
| **I** | `parse_count` never learned PREREQ-1's informal nouns (`vibarua`) | add them + spelled counts | 2 |

**Result over 516 questions: +10 computing, 0 lost, 0 value changes.** All 8 corpus gains
verified against the gold **figure**, not just the route: eval_242 (160,000), eval_279
(131,250), eval_283 (182,000), eval_284 (38,000), eval_318 (192,500), eval_324 (168,000),
eval_330 (45,000), nat_07 (80,000).

### 🚨 The 516-sweep caught a confident wrong number IN THIS PATCH — the probes did not

The first guard ("wrong_base and exactly one plausible figure") anchored **eval_327**
(*"wafanyakazi 10, **kati yao** 4 wana **mishahara ya TZS 700,000** na 6 wana TZS 300,000"*)
on the **first group's salary** and computed **WCF = 0.5% × 700,000 = TZS 3,500** against a
true payroll of 4,600,000 (**TZS 23,000**) — a wrong figure replacing an honest clarification,
which is the exact failure never-guess exists to prevent. `has_multiple_groups()` now blocks
anchoring *and* `parse_count` whenever several pay groups or periods are named.

Three further self-inflicted defects surfaced the same way: **eval_329** (answered for one of
two periods), **eval_299** (I over-stripped `hesabu`, a genuine dangling reference), and
**`"wafanyakazi kumi na wawili"`** parsing as a second group instead of the compound *twelve*
(caught by the pre-existing `test_spelled_and_digit_counts`).

### 🔑 No single instrument is sufficient — three different ones caught different things

| instrument | caught |
|---|---|
| **adversarial probes (R17)** | bare `hisa` refusing 7 real gate questions; the wrong-base guard rejecting a stated payroll (ap_07–ap_10) |
| **frontier judge** | the two-arm retriever's false passes; 41 v15 / 30 v16 regex false-passes |
| **full-corpus sweep** | **eval_327's confident wrong number**; the `nahusika na` substring collision; the compound-numeral break |

Each found something the others missed. **Run all three; a clean result from one is not a
green light.** (R17 already says a clean sweep isn't evidence — the converse also holds:
a clean probe set isn't either.)

### ⚠️ Approved out-of-scope addition — `routing._NSSF_EMPLOYER_CUES`

**Not one of the eight patterns.** The A1 narrowing made **nat_07** computable, which exposed
a latent **D-NSSF-1** party gap underneath: it would have answered the 20% total
(**TZS 160,000**) where the question asks the employer share (**TZS 80,000**). The
first-person phrasing *"mimi kama mwajiri nachangia"* matched none of the third-person cues.
Added the two-phrase cue (sweep: nat_07 only; `edge_p03` unchanged), **flagged for approval
rather than shipped silently**, and approved on that basis.

**Standing expectation for Tier 3:** every veto narrowed may expose a defect that was
previously unreachable. Each one is a **stop-and-flag, not a silent fix.**

### R17 probes

`eval/accuracy_gate/extraction_adversarial_in_scope_016.jsonl` (16) →
`tests/test_extraction_tiers12.py`. Four first-draft probes were **mis-authored** — three had
no number so they never reached extraction, one named no levy — and reported FAIL against
correct code. Rewritten rather than have their expectations adjusted: a probe that passes for
the wrong reason is worse than no probe.

**386 tests pass** (358 + 28). `is_uncomputable_payroll_amount`, the sole predicate production
imports from `routing`, verified identical across all 516 questions.

### Decided, not deferred

- **eval_281 — PERMANENT WON'T-FIX.** *"unafika TZS 920,000 **hivi**"* carries no correction
  marker; a bare `hivi` after a figure genuinely means "about". Treating it as exact would
  loosen never-guess for **one row**. Not a backlog item.
- **Pattern E (multi-component pay, eval_334) — WON'T DO.** The gold itself hedges
  (*"kama posho na bonasi zinahesabika"*) because whether a transport allowance and a one-off
  bonus are taxable is a **regulatory** question, not a parsing one. Summing them would have
  the engine assert a tax treatment never verified against primary sources. If wanted, it is a
  **locked_facts question first.**

### ✅ Tier 3 pattern C — the fraction grammar (IMPLEMENTED 2026-08-07)

**C CLOSES ZERO GATE QUESTIONS. It is NOT a gate gain.** All four instances still clarify —
their blocker is the multi-figure rule that **pattern B** owns. C is a correctness fix to an
active mis-parse and a prerequisite for 4 of B's 9. `test_c2_is_unused_by_default` asserts by
source inspection that neither `extraction.py` nor `orchestrator.py` calls the resolver, so a
future session cannot quietly wire it and credit C with movement it did not produce.

**Root cause — Swahili has two fraction constructions; `_value_small` implemented one:**

| construction | shape | example | correct | was |
|---|---|---|---|---|
| additive | `<scale> <n> **na** <frac>` | `laki saba na nusu` | 750,000 | ✅ |
| multiplicative | `<frac> [<num>] **ya** <N>` | `theluthi mbili ya 30` | ⅔×30 = 20 | ❌ **2.333** |

The word after a fraction is a **numerator, not an addend**: `theluthi mbili` = two-thirds,
`robo tatu` = three-quarters. Junk appeared only *with* a numerator — a bare `robo`/`nusu`
emits nothing — so only eval_287 and eval_288 carried it.

**C-1 suppresses** (resolving needs the group it modifies = B), applied to **any
fraction-initial run**, not just `ya`-gated, on evidence: `_value` yields junk for *every*
fraction-initial run (`nusu milioni`→0.5, `robo milioni`→0.25), so there is no correct figure
to lose. **The 524-sweep could not distinguish the two variants** — both change the same 2
questions — so the choice rested entirely on probes.

**🔑 The near-miss worth remembering: the rule is defined on the parsed RUN, not by regex.**
A `\b(nusu|robo|theluthi)\s+ya` pattern — the obvious first formulation — matches `nusu ya`
in **nat_05** (*"asilimia tatu na **nusu ya** nini"*) and suppresses a correct **3.5%**,
because the run actually starts at `tatu`. Pinned by
`test_the_nat_05_near_miss_a_regex_rule_would_have_broken`.

**C-2** — `parse_fraction_of_count()`, unused by default, verified against all four golds
including the elliptical second fraction and the `wengine wote` remainder: eval_285 `[6,18]`,
eval_287 `[20,10]`, eval_288 `[12,4]`, eval_289 `[7,7]`. **Never rounds a person** —
`theluthi ya watu 10` is 3.33 and returns no split with a reason.

**Sweep over 524: 4 amount-lists change, 0 branch/value changes. Nothing unmasked.**
**408 tests pass** (+24). Two pre-existing `_real_weights` failures are environment-dependent
and fail identically at HEAD with these changes stashed — deselected, not masked.
R17: 8 probes; **eval_274** (the only *live computing* fraction question, on the additive
grammar) pinned in its own test, not only inside the parametrised loop.

### ✅ Tier 3 pattern B — multi-group payroll + the per-individual shape (IMPLEMENTED 2026-08-07)

**All 9 instances answer with the gold figure.** eval_285 SDL 388,500 · eval_286 NSSF
1,500,000 · eval_287 SDL 665,000 · eval_288 WCF 47,000 · eval_289 NSSF 700,000 · eval_290 SDL
325,500 · eval_325 NSSF 1,380,000 · eval_327 SDL 161,000 **+ WCF 23,000** · eval_399 PAYE
198,400.

**All-or-nothing, because best-effort was measurably dangerous.** A prototype of the obvious
template (`<count> <pay-verb> <amount>`) swept over 524 questions **matched 12 and mis-parsed
6**:

| | naive parse | truth |
|---|---|---|
| eval_304 | 20 × 50,000,000 = **TZS 1 billion** payroll | `mtaji` is capital |
| nat_18 | 2 × 400,000 | 400,000 + 1,100,000 |
| eval_285/287/288/289 | the fraction **base** as the group count | C-2's split |
| ex_08 | only the second branch | both or decline |

Four validations must all pass or it declines: every money figure assigned · a stated total
equals Σ counts · fraction counts come from pattern C only · no wrong-base word. **Five corpus
questions decline** rather than mis-parse. **Magnitude is not the discriminator** —
`MIN_PLAUSIBLE_AMOUNT` is 10,000 but real rates here are 1,500/piece and 18,000/day, so roles
are assigned **structurally**. Gated positionally so eval_092/eval_302 cannot be diverted.

**eval_399 as its own shape.** PAYE bands are progressive, so summing is an arithmetic error,
not a presentation choice: 1,600,000 as one salary = **308,000**, versus the true 10,400 +
188,000 = **198,400**. `compute_paye_each()` lives in the rules engine and needed **no
orchestrator surgery**. **eval_289** needed no decision — `nssf_party` already resolved it.

### ⚠️ Test-mirror finding — the third test this cycle that asserted or masked a defect

`tests/test_extraction_tiers12.py::_branch` reimplements `_answer_compute`'s decision order,
and its docstring claims it *"fails loudly if that order changes."* **It did not.** It simply
lacked the new branch, so it kept reporting `clarify` for ex_07 while the real orchestrator
computed. Only the 532-sweep — which drives the *real* orchestrator — exposed the
disagreement.

**A mirror that claims to fail loudly and silently does not is a weaker guard than none.**
Re-synced. **If a third mirror ever appears, replace the pattern rather than maintain it.**

Running tally of tests that were themselves the defect this cycle:
1. `test_paraphrased_ooc_controls_*` — asserted a known OOC leak should pass.
2. `test_boundary_amount_vs_threshold` — asserted the p04 routing defect as correct.
3. `_branch` mirror — claimed loud failure, drifted silently.

**Probes ex_07/ex_08 moved `clarify` → `compute`, STRENGTHENED not relaxed:** they now assert
the correct **figure** (WCF 23,000, SDL 238,000), so a mis-parse fails on the number rather
than the branch. History preserved in each `guards_against` string.

**433 tests pass** (416 offline + 17 retrieval, two processes — the single-process run hits a
native torch access violation in `test_retrieval.py` from repeated model loads, which
reproduces with these changes stashed).

### 📊 PROJECTION FOR THE PHASE D RE-RUN — recorded BEFORE the result

| | raw gain on the 400 |
|---|---|
| PREREQ-1 | **+15** (measured) |
| Tiers 1–2 | **+7** (measured) |
| C | **0** (stated: correctness fix, not a gate gain) |
| B | **+9** (all scorer-verified) |
| **total** | **≈ +31 → +7.75pp** |

Against a raw gap of **−6.8pp**.

**THIS IS A PROJECTION, NOT A GUARANTEE.** Every figure above is measured on the
*deterministic* extraction/routing path. The paired run measures the **full system** with
model behaviour on top, and **+7.75 against −6.8 is a thin margin — a handful of model-side
losses could erase it.** If the re-run lands short, D (+2) and F (+4) are the next increment,
**not** a redesign. This paragraph is written before the run so the expectation cannot be
retrofitted to the result.

### Next: Tier 3 remainder (D, F) — only if the re-run lands short

`theluthi mbili` parses to **2.333…** and `robo tatu` to **3.25** — an **active mis-parse**
feeding junk into the amount list, not merely a gap. Self-contained, and a prerequisite for 4
of B's 9. **Pattern B's two odd members are output-shape questions, to be decided separately
from the group parse:** eval_399 wants per-person answers (*"PAYE ya kila mmoja"*), eval_289
wants the employer share of the total.

## 🚀 PRODUCTION NOW SERVES `chike/pipeline_v15.py` (deployed 2026-08-07)

The 2026-08-07 redeploy that shipped the SAFETY-1 OOC fix **also carried the Plan A extraction
onto the production serving path for the first time.** `ChikeModel.run()` is now a thin adapter
over `chike.pipeline_v15.answer()`; the only stage it still owns is `_generate`
(tokenize → generate → decode). This was expected — the extraction commit (`d54ec17`) stated
production would pick it up at the next deploy — but it is stated here explicitly because it
changes what "production" means for every future entry.

### VERIFICATION OF RECORD — 20/20 byte-identical against the live pre-extraction endpoint

Artifact: **`eval/results/pipeline_v15_live_byte_identity_d54ec17.json`** (promoted out of
gitignored `scratch/`).

Each of the canonical 20 edge questions was run through BOTH the live production
`web_endpoint` (the pre-extraction inline v15 pipeline) and `chike.pipeline_v15.answer()`
driven over HTTP to `generate_endpoint` on the **same deployment, same v15 weights**,
single-arm `V15Retriever`, RAG index sha-verified identical between `kaggle/` and
`chike-inference/` before the run. **Result: 20/20 byte-identical.** Warm latency 10.6s
(production) vs 11.3s (extracted).

**Why this is the verification of record and not merely a pre-merge check:** it was run before
the merge, but the redeploy has now put that code in front of users, so these 20 rows are the
evidence that **what users hit today is byte-identical to what they hit before**. It closes the
two stages the offline suite structurally cannot reach — the real e5 encode and the real
`apply_chat_template` on the adapter tokenizer. Its offline companion (`tests/test_pipeline_v15.py`)
proves decompose/pool/prompt byte-identical against the git-pinned pre-extraction baseline over
420 questions, and stop-split+clean byte-identical over 400 persisted generations — but no unit
test substitutes for the live pair.

Post-deploy sanity on the fresh containers (SDL rate + 5 adversarial in-scope questions,
9/9 as expected) is consistent with unchanged behaviour.

## ✅ SAFETY-1 — OOC refusal-gate leak CLOSED (2026-08-06)

Run 3 found a **live** refusal-gate hole: *"niliuza **kiwanja** changu cha mwanza nimepata faida
kubwa nalipa kodi gani"* passed the R11 gate on the production endpoint and the model answered
*"Kodi ya faida ya mtaji (Capital Gains Tax) … ni **asilimia 30%**"*. A direct Gate-2 failure on
natural phrasing, on the mechanism ADR R11 calls infrastructure.

**Fix: `ooc_phrases` 53 → 107 (+54), audited not patched.** Additions cover Swahili synonyms,
inflections and colloquial variants across every declared refusal category — capital-gains/land,
import/customs, stamp duty/valuation, mining royalties, EPZ, insurance premium levy, Zanzibar,
transfer pricing, investment/crypto. No new refusal categories were invented.

**The method is the durable part.** The first sweep returned **0 false positives on every
candidate**, which was treated as a WEAK test rather than a green light — the gate corpora barely
contain that vocabulary, so "0 fp" mostly meant "the word never appears". Adding **15 adversarial
in-scope probes** (realistic in-scope questions written to CONTAIN the dangerous vocabulary)
changed the picture immediately:
- bare **`hisa`** would have refused **7 real gate questions** (eval_227 BRELA share transfer,
  eval_173 GN487A shareholding, eval_256 SDL) — the decisive catch;
- bare `kiwanja` refuses premises questions (a plot is where a business SITS) → the capital-gains
  additions are **verb-qualified**, and `uza kiwanja` covers the whole verb family as a substring;
- `nyumba`, `shamba`, `bima`, `madini`, `uwecheza…`/`uwekezaji`, `bandari`, `hati` all confirmed
  dangerous by data, not by argument.
Rejected by sweep: `kodi ya pango` (hits eval_258, an in-scope SDL question). Dropped on
judgement despite 0 fp: `dse`, `znz`, `kampuni mama`, `kodi ya kupangisha`, `kupangisha nyumba`.
Dropped on founder review: `kontena`, `bidhaa kutoka nje` (same reasoning as bare `kiwanja`).

**Final sweep, 54 phrases over 483 questions (400 gate + 15 + 5 + 48 probes + 15 adversarial):
exactly ONE classification change — nat_46, the target — and ZERO in-scope questions newly
refused.**

**Now self-enforcing:** the 15 probes are committed at
`eval/refusal_gate/ooc_adversarial_in_scope_015.jsonl`, each carrying a `guards_against` note,
and `tests/test_classification.py` fails if any future phrase refuses one of them. An over-broad
addition now breaks a test instead of needing someone to remember the audit.

**A prior assumption was refuted and the test inverted.**
`test_paraphrased_ooc_controls_pass_the_phrase_gate_to_the_model` previously ASSERTED that
ro_01 (*"niliuza kiwanja"* — nat_46's own phrasing) should pass the gate, on the rationale that
the **model** would refuse it via the system prompt, and said *"Do NOT fix classify() to catch
these"*. Run 3 showed the model does NOT refuse it. The test is now inverted with that history
recorded in its docstring. The phrase-gate-is-not-semantic point still stands as a **limit** — it
no longer justifies leaving a known leak category open.

## 🟠 OPEN — two Run-3 findings that are NOT classifier gaps (logged, not fixed, 2026-08-06)

**(a) `eval_191` is MISLABELLED in the gate corpus.** *"PAYE ya mfanyakazi wangu mwenye mshahara
wa TZS 800,000 kwa mwezi ni kiasi gani?"* carries `subdomain: out_of_corpus` with gold answer
**TZS 78,000** — a correct, core, in-scope PAYE computation. It surfaced during the SAFETY-1
audit as an "uncaught OOC item"; it is nothing of the kind. **Any attempt to close it with an OOC
phrase would start refusing PAYE questions — the single most common real question there is.**
Correcting the label **moves the gate denominator** (it shifts one question between the in-corpus
and refusal sets), so it is a **scored-number decision of the same class as the `eval.py` payroll
guard and the `scorer_reliability` denominator** — not a data cleanup. Do not change it inside a
measurement cycle. Decide alongside those.

**(b) Bank-loan advice has no declared OOC category.** `edge_p15` (*"nisaidie jinsi ya kupata
mkopo wa benki kwa bizna yangu"*) is genuinely outside what Chike does, but "how to get a bank
loan" is not among the categories the system prompt declares out of scope (capital gains,
import/customs, transfer pricing, stamp duty, mining royalties, Zanzibar tax, investment advice).
Adding loan phrases would **create a new refusal category**, which is a **scope question for the
product, not a bug in the classifier**. Deliberately excluded from the SAFETY-1 audit, which was
scoped to variants of concepts already listed. Needs a product decision: does Chike refuse
financing questions, or answer them within the compliance frame?

## 🔴 SAFETY-2 / D-RESIDENCY-1 — engine-authoritative wrong figure (TRACKED DEFECT, 2026-08-06)

**Logged, not implemented.** Discovered by Run 3 (`nat_16`, `eval/results/edge_probe_natural_048_findings.json`).

**What happened.** *"nimemleta engineer kutoka india **hana residence permit ya kudumu** nampa
milioni 4 kwa mwezi kodi ya mshahara wake ni ngapi"* — routing **succeeded** (`compute[paye]`),
but `chike.routing.paye_resident` did not read *"hana residence permit ya kudumu"* as
non-resident. The rules engine therefore applied the **resident progressive bands** and returned
**TZS 1,028,000** instead of the non-resident flat 15% = **TZS 600,000**. That figure was then
rendered as the authoritative deterministic *working*.

**(a) Why D-FIDELITY-1 structurally cannot catch it.** D-FIDELITY-1 blanks the model body when
it *contradicts* the engine's working. Here the body and the working **agreed** — both were
wrong, because both derived from the same mis-detected input. The guard is a
consistency check between two outputs of one computation; it has no independent notion of
correctness and therefore cannot detect an error upstream of both. **No amount of fidelity
guarding closes this class.** The defect lives in input resolution, not in output fidelity.

**(b) This failure class exists ONLY in v16.** v15 has no rules engine, so it cannot lend an
authoritative frame to a wrong number: its errors are model guesses, presented as model prose.
v16 prints a wrong figure *as a verified calculation*, appended verbatim by `_render`. On this
question v15's answer was off-topic (immigration permits) but asserted **no tax figure at all**.
So on `nat_16` specifically, v16 is **worse than v15** — the only such case found in Run 3, set
against 4 confident wrong numbers v16 removed. Stated plainly because the wiring case must not
be argued on the favourable cases alone.

**(c) Proposed fix approach (NOT implemented).** Extend `_PAYE_NONRESIDENT_CUES` with
residency/permit phrasings — *"hana residence permit"*, *"hana kibali cha ukaazi"*, *"si mkazi
wa kudumu"*, *"yuko kwa muda"*, *"anafanya kazi kwa mkataba wa muda"*, *"amekuja kutoka"* —
i.e. the same lexical-cue extension pattern as the shipped ROUTING-GAP-PAYE fix, with the same
discipline: sweep every candidate over the 400 + all probe sets for false positives BEFORE
implementing, because a false *non-resident* detection is symmetrically dangerous (it would
apply flat 15% to a resident earning below the threshold). A deeper alternative — having the
engine return a *confidence* on residency and clarifying when low — is a real design change and
should not be folded into a cue extension.

**(d) This is an INPUT to the wiring decision, not a blocker to be quietly closed.** It does not
by itself argue against wiring v16: the net compute-path safety change in Run 3 was still
positive (4 wrong numbers removed, 1 correct answer lost, 1 new authoritative error added). But
it establishes that *routing success ≠ safety*, and that v16 carries a failure mode with a worse
**presentation** than anything v15 can produce. Whoever takes the wiring decision must weigh it
explicitly. **Do not close this by fixing the cue list and declaring the class handled** — the
class is "engine authority applied to a mis-resolved input", and the residency cue is one
instance of it.

## 🧭 PHASE D WIRING CYCLE — IN FLIGHT (2026-08-06)

Founder decision: **Stage 0 cancelled** (no users yet → no live traffic to observe → zero
blast radius pre-launch makes flag-gated staging over-engineering). Straight to **Stage 1 =
Phase D as ADR 0001 §10 actually specifies.** Planning premise (an assumption, NOT evidence,
and explicitly not to be reconciled with the 400's 26%): **compute ≈ 50% of eventual traffic.**

**Pre-launch blockers landed first, independent of the wiring outcome:**
- `149938d` — `chike.retrieval` **fails loud** on a missing/corrupt index instead of returning
  `[]`. The default paths are repo-relative `kaggle/`, which do **not** exist inside the Modal
  image; the old graceful-disable turned a wiring mistake into a silent no-facts collapse that
  looks like model failure. + `expected_fact_count` (R15 stale-index guard), `preflight()`,
  `configure()`.
- `fb8d3bc` — **one shared OOC refusal text.** The orchestrator carried its own terser string.
  Both matched `refusal_phrases`, so **the refusal gate could not see the difference** — wiring
  v16 would have silently downgraded every refused user's answer while passing validation.
- `30aa79b` — orchestrator resolves **`stop_strings` from config** instead of the implicit
  module default. Behavioural no-op today; closes a config-only edit reaching production and
  the gate but not v16's clean stage — a latent divergence underneath a measurement run.

**Plan A extraction — SHIPPED (`d54ec17`).** `chike/pipeline_v15.py` (production's sequence,
generation injected) + `chike/decomposition_v15.py` (leaf, **no** ordinal split), imported by
BOTH `modal_app.py` and the Phase D harness. **All three `decompose_query` copies collapsed**
(modal_app, eval.py, and the v16-only `chike/decomposition.py` kept deliberately distinct).
Behaviour proved, not asserted, against `tests/fixtures/v15_inline_baseline_30aa79b.py`
(captured via `git show` from the last pre-extraction commit): decompose/pool/prompt
byte-identical over 420 questions, stop-split+clean byte-identical over 400 persisted
generations, and **20/20 byte-identical live against the production `web_endpoint`** (closing
the two stages tests can't reach offline: the real e5 encode and the real
`apply_chat_template`). The v15 arm cannot inherit v16 powers — guarded by tests that
`decomposition_v15` differs from `decomposition` on **exactly eval_322**, and that
`V15Retriever` never invokes the two-arm hybrid. Suite 273 → 308.

**No Modal redeploy before the wiring decision** — production picks the extraction up whenever
we next deploy.

### 🟠 LAST OPEN R12 GAP — `kaggle/eval.py` has no `is_uncomputable_payroll_amount` guard

Production intercepts a payroll-levy AMOUNT asked with no salary figure **before**
decompose/RAG/generate and returns `PAYROLL_CLARIFICATION` (no model call). **The live gate does
not** — it sends the question to the model. After `d54ec17` this is the **only** remaining
divergence between `eval.py` and production.

**Deliberately NOT fixed inside this measurement cycle (founder call).** Adding it moves the
launch-blocking `GATE PASSED` number — the same class of decision as the `scorer_reliability`
denominator (see the STRUCTURAL GATE FINDING below), and changing the gate's denominator
mid-comparison would corrupt Phase D. **Decide after Phase D lands.** The Phase D v15 arm is
unaffected: it uses `pipeline_v15`, which has the guard.

### Run status

| Run | What | Who | State |
|---|---|---|---|
| 2 parts 1–2 | numeric retrieval A/B, CPU (`kaggle/rag_numeric_ab_run2.py`, `f521768`) | founder (Kaggle) | **run; artifact pending** — see below |
| 1 + 2 part 3 | paired v15-vs-v16 400 + de-confound, GPU (`kaggle/eval_phase_d_paired.py`, `124cbd2`) | founder (Kaggle) | packaged, not yet run |
| 3 | 48-question dual-path natural probe, HTTP | Claude Code | approved, not yet built |

**Run 2 parts 1–2 — founder-reported figures (full artifact not yet pasted into the repo):**
append-only **confirmed** (0 violations, 0 facts lost, Set A ranks identical) → the hybrid is
**safe**. But the second arm fires **197/197** and yields **1 recovery vs 86 dilutions** on the
labelled set → **not a demonstrated fact-path win.** Consequence: **"keep single-arm in
production" is now a live option**, and Run 2 part 3 is the deciding evidence on whether the
two-arm retriever ships at all — not merely a de-confound.

## 🔴🔴 ROUTING-GAP-PAYE — HIGH PRIORITY (2026-07-26) — top open item, above all other tracked gaps

**Discovered by a 20-question real-weights edge probe (v16 live Modal, `scratch/edge20_v16_result.json`).**
Two PAYE amount questions phrased in ordinary language — Q4 *"Mfanyakazi wangu anapata TZS 1,200,000 kila
mwezi, kodi ya serikali inayokatwa ni ngapi?"* and Q5 *"Mfanyakazi wangu si mkazi, analipwa TZS 3,000,000
kwa mwezi, kodi yake ni kiasi gani?"* — **mis-routed to the FACT path** and the model free-computed
**confident WRONG numbers** (Q4: PAYE 128,000, correct 188,000; Q5: 270,000, correct non-resident flat-15%
= 450,000).

**Why this is structurally more serious than any D-* defect fixed this session:** those were "the engine
computed wrong." This is **"the engine never ran at all."** Every never-guess / fidelity protection built
this session (D-NSSF-1 party resolution, D-PAYE-1 non-resident flat rate, D-FIDELITY-1 body-vs-working
suppression) is **contingent on the question first being routed to compute.** This gap breaks that
contingency on the single most common real compliance question there is — *how much tax comes out of my
salary* — phrased the way an actual user asks it. The fidelity guard cannot help because there is no
`ComputationResult` to guard; the fact/RAG model does the arithmetic with no deterministic backstop.

**Ranked HIGHER than every currently-open tracked gap** (D-WCF-3 distractor-coexistence, per-person/tiered
aggregation, applicability-detector/eval_311, eval_326 mixed) because **all of those are confirmed
safe-clarification gaps** (verified again in the same edge probe: Q8 tiered NSSF, Q10 WCF distractor, Q18
mixed all failed SAFE — clarify, no wrong number). ROUTING-GAP-PAYE is a **confirmed unsafe-wrong-answer
gap on natural phrasing** — a different and worse class.

**Mechanism (confirmed):** gap in `chike/routing.py::_natural_levy` cue lists (detect_intent path 2, the
Candidate C natural path). PAYE cues are only `["kodi ya mapato","kodi ya mshahara","mapato ya ajira"]`;
everyday "income tax / tax deducted from salary" phrasings (*kodi ya serikali*, *kodi yake*, *kodi
inayokatwa*, *kodi ya kipato* …) match no cue, and "ya serikali" ≠ the generic "kwa serikali", so
`_natural_levy` returns None → intent `none` → fact. Same lexical-cue mechanism as the original router fix.

**SCOPED below (characterize-before-fix, no code yet); full blast-radius sweep + proposed cue extension +
validation to be reported for review before implementing — same rigor as D-NSSF-1 / D-FIDELITY-1.**

## ✅ PLAIN-SWAHILI EDGE PROBE — Defect A + Defect B SHIPPED + PROD-VERIFIED (2026-07-28)

A 15-question plain-WhatsApp Swahili probe (`eval/accuracy_gate/edge_probe_plain_sw_015.jsonl`,
findings `eval/results/edge_probe_plain_sw_015_findings.json`) surfaced that **all 15 user-facing
answers came back EMPTY** — two stacked, production-code-identical defects:

- **Defect A — `clean_reply` blanked whole answers (`fix 628f6a0`).** `_is_fabricated_block` treated
  an early `?` (from the leading echo below) as a fabricated `Q? A` turn and discarded the first block
  → `''`. Confirmed LIVE on the production `/answer` path (4/4 → `{"reply":""}`). Fix: strip a leading
  echoed-question `?` once at the start of `clean_reply` (anchored `^`, ≤60 chars, capital-after; cannot
  cross `\n\n` so mid-answer `Q? A` detection is untouched). Blast-radius over 400 gate + 15 probe raws:
  **17 recovered, 0 regressed, 0 other**; 27 cleanup tests pass. Also recovered 2 gate rows (eval_321/330)
  whose compute path had masked the blank.
- **Defect B — model prepended a question-echo + leading `?` (`fix 6161cb9`).** Root cause: v15 trained
  on naive-concat with no assistant-turn boundary → on an UNPUNCTUATED question the model completes the
  missing `?` before answering. Fix: `chike.prompting.ensure_terminal_punct` appends `?` when terminal
  punctuation is missing, applied in all 3 prompt builds (build_chat_prompt → orchestrator + eval.py;
  modal_app.py inline primary + fallback). Sweep: **no-op on all 400 gate questions** (already punctuated
  → byte-identical), appends one `?` on the 15 probe questions with answer content unchanged. Verified
  live on the production `/answer` path (4/4 non-empty, no leading `?`). 36 prompting/orchestrator tests pass.
- **CLOSED by Defect B:** the Defect-A `>60-char leading-echo` coupling risk (a long echo could slip past
  A's cap and re-blank). B removes the echo at the source, so this can no longer arise; A remains as
  defense-in-depth.

**Note:** the gate corpus (`5a62c00`) never triggered either defect (0/400) because it is formally phrased —
this is a **coverage gap**, not a contamination of the gate numbers, which stand unchanged.

Recovered ≠ correct: several plain-phrasing answers were still wrong on content. Cycle close-out:

- **item 3 / p02 — SHIPPED (`45a9b48`).** Root cause was the `_PAYROLL_CTX` gate, not the levy cue:
  informal employment phrasing (`nimemuajiri`, `msichana wa kazi`, `nampa`) matched no payroll-context
  word, so PAYE mis-routed to fact. (`laki nane` parses fine to 800,000 — the "400k/16k" was fact-path
  hallucination.) Added informal-employment cues to `_PAYROLL_CTX`; `edge_p02` now routes paye →
  `compute_paye(800000)=TZS 78,000`. Sweep: 1 routing change, **0/400 gate changes**. **v16 orchestrator/
  gate only** (v15 `/answer` unaffected — no redeploy).
- **item 3 / p04 — DEFERRED → v16 hardening backlog: "natural-levy applicability route (structural)".**
  p04 (`…tozo ya mafunzo…inanihusu`) is an applicability ask (`_has_money_ask=False`) on a NATURAL (non-
  explicit) levy; `detect_intent` has no applicability route for that case, so cues alone can't fix it —
  needs its own design + blast-radius analysis when picked up. Its `0.5%`-vs-`3.5%` SDL rate is a
  downstream fact-path symptom of the routing miss.
- **item 3 / p12 — LEFT AS FACT (low priority).** Comparison question (`kama ya watanzania au tofauti`,
  `_has_money_ask=False`); the fact answer is already rate-correct (non-resident 15%). Logged, not fixed.
- **item 4 — OPEN (analysis-only next):** retrieval fragility on colloquial register — Q13/Q14/Q16
  fix-facts and others not retrieved on fresh plain phrasing. Structural (two-arm retrieval on run-on
  colloquial text), NOT another round of per-phrasing fact tuning. Scope options to be reported; no fix
  without approval.

**Probe cycle status:** Defect A ✅ + Defect B ✅ shipped & prod-verified; item 3/p02 ✅ shipped; p04 deferred;
p12 logged; item 4 open. Tokenizer warning (below) scoped after item 3.

## ✅ DUAL-PATH PROBE 005b — Defects A+B REGRESSION-CLEAR + the v16 wiring evidence (2026-07-29, `c1776a9`)

A 5-question plain-Swahili probe on **never-seen phrasing** (`eval/accuracy_gate/edge_probe_plain_sw_005b.jsonl`,
findings `eval/results/edge_probe_plain_sw_005b_findings.json`; runner + raw result in gitignored `scratch/`).
**Findings only — no code changed, nothing redeployed.** Each question ran through BOTH live paths on the
**same Modal deployment / same v15 weights / same 217-fact RAG index**: v15 = production `web_endpoint`
(classify+decompose+RAG+chat-template+clean), v16 = `Orchestrator(LocalAdapter → generate_endpoint)` with the
AfriqueLlama tokenizer for prompt parity. Adjudicated against `scripts/locked_facts.json` + the rules engine.

- **Defect A + Defect B hold — 10/10 non-empty** (both paths, all 5) on fresh UNPUNCTUATED plain-Swahili.
  No `clean_reply` blanking, no leading-echo re-blank. The two shipped fixes are regression-clear on the
  phrasing class that discovered them.
- **v16 ≥ v15, and strictly safer on compute.** 4/5 questions (all fact-routed) came back **byte-identical**
  between the paths. The one compute question (b02, SDL) **diverged decisively**: v15 free-computed a
  **confident WRONG payroll** (3,750,000 for 12 × 350,000; no SDL figure at all), v16 routed `compute[sdl]`
  and **safe-clarified — no wrong number**. This is the concrete case the v16 architecture exists to fix.
- **Dominant residual failure is RETRIEVAL (item 4), shared by BOTH paths and orthogonal to wiring.** b05
  (GN487A fronting, "rafiki yangu mchina… jina langu kwenye leseni") retrieved **top-3 all off-topic trademark
  fees**; the correct facts (`gn487a_license_lending_is_facilitation`, `gn487a_penalty_citizen_facilitator`)
  exist but were never surfaced, so **both** paths gave a generic immigration-ownership answer that never warns
  the user that name-lending is itself an offence (TZS 5M / 3 months). b01 also had a top-3 miss but was
  rescued by general knowledge; b04 had a rank-1 on-topic hit and answered well. **Retrieval quality tracked
  answer quality 1:1** — the strongest evidence yet for the parked item-4 hybrid dense+lexical direction, on a
  high-stakes question.
- **NEW gap logged, NOT fixed — Swahili-numeral slot extraction on the compute path.** b02 proves routing now
  reaches `compute[sdl]`, but the extractor did not resolve fully-specified all-Swahili figures
  (`kumi na wawili`=12, `laki tatu na nusu`=350,000, per-person `kila mmoja`), so the engine's correct
  **147,000** was never delivered — safe-clarify instead. **The compute path's value is gated on extractor
  coverage.** Backlog item; no code this cycle.

**Latency captured (same probe, incidental):** warm v16 ≈ v15 (b02 6.1s/6.4s, b03 6.7s/6.6s, b04 12.0s/11.9s,
b05 9.4s/9.1s); b01 was a cold start (v15 62.4s). Warm parity holds because 4/5 took **one** backend call each.

## 🟠 OPEN ITEM — tokenizer `fix_mistral_regex` / Mistral reference on the production adapter (2026-07-28)

> **SUPERSEDED 2026-08-08 by D-1** (top of file, *DEFERRED — taken up after the current fix cycle
> closes*). Work from **D-1**, not from this entry: the train/serve repo split is now verified in
> code (`train_ddp.py` loads `BASE_MODEL`; production, the gate and every probe load
> `ADAPTER_REPO`), which makes this a possible **train/serve mismatch underneath every gate number**
> rather than the warning-to-look-at scoped here. Kept for the original date and observation.

Loading the adapter tokenizer (`prospAprospA007/africa-giants-adapter-v15`) emits:
*"loading … with an incorrect regex pattern … set `fix_mistral_regex=True` … This will lead to incorrect
tokenization."* — and references **Mistral-Small-3.1-24B**, while the base is meant to be
`McGill-NLP/AfriqueLlama-8B`. "Possibly incorrect tokenization" on a production model is **not minor**.
Scoped AFTER item 3. To investigate: whether tokenization actually diverges (round-trip a Swahili sample
with/without `fix_mistral_regex=True`), whether it affects generation/retrieval, and provenance of the
Mistral tokenizer reference in the adapter repo.

## 🟠 ITEM 4 — colloquial-register retrieval fragility (PARKED; direction set, 2026-07-28)

**Diagnosis CONFIRMED (data).** On plain-WhatsApp run-on queries the dense e5 retriever MISSES the correct
fact (p06/p07/p08: top-3 were off-topic English facts — `trademark fee…`, `employer notification…`), while
a trivial lexical token-overlap arm RECOVERS the correct fact 3/3. Two compounding factors:
- **factor 1 — noise dilution:** greetings/narrative ("mambo naomba kuuliza…", "jamaa wamesema…") pull the
  dense vector off-topic; the domain keywords survive but are a minority of tokens.
- **factor 2 — English-fact attractors:** every dense miss landed on English `"key: value"` facts, whose
  generic-English embeddings spuriously outrank the on-topic Swahili fact for a noisy Swahili query.

**Direction = hybrid dense + lexical (two-arm).** Additive, no model call, no retrain. Complementary
structural cleanup = fact-form normalization (English `key: value` → concise Swahili-first) — this is the
**parked follow-up "E"** (forces a RAG regen; batch with the next `locked_facts.json` change).

**Merge strategy = TBD via a Kaggle spike** (union-then-rerank vs interleave vs weighted; rank-of-correct
across 400 gate + 15 probe). Cannot run locally — e5 load is not viable on this machine (Windows paging
limit). The spike is already written: **`scratch/item4_hybrid_sweep.py`** (adapt to the `regenerate_rag_e5.py`
Kaggle pattern — CPU, Internet, fetch inputs from GitHub). Run it AFTER the v16-wiring decision, because
that decides the target retriever: `chike.retrieval` (v16/gate) vs production `modal_app.py::retrieve_facts`
(v15) — **do not harden v15's retriever separately if v16 replaces that path.**

**Value note:** unlike item 3 (v16-only), item 4 affects real users — production `/answer` is v15 RAG-only,
so retrieval quality is the whole product there. Priority rises once the wiring target is fixed.

## ✅ FACT-ACCURACY (Q13/Q14/Q16) — SHIPPED + GATE-CONFIRMED (2026-07-28; batch `5a62c00`)

Same edge probe surfaced three fact-path fabrications where a correct locked fact (or general rule) exists:
- **Q13 BRELA deregistration** — asserted a company "must finish its term first" (fabricated; voluntary
  deregistration/striking-off exists, no fixed term).
- **Q14 OSHA vs WCF** — answered the wrong agency and fabricated a "2-employee WCF registration threshold"
  (contradicts `wcf_threshold_no_minimum`; OSHA covers all workplaces incl. one employee).
- **Q16 EFD** — "every shop needs EFD regardless of sales" (matches `efd_threshold_tzs_11m` wrong_pattern;
  below TZS 11M may use manual receipts unless VAT-registered).
Individually narrow RAG/fact-correction candidates; picked up via the same primary-source-verification
process as D-VATWH-1. Primary-source verification completed in a claude.ai session (2026-07-27, founder-approved).

**RESOLUTION (all three landed as one batch, live-verified, gate-confirmed):**

*Facts (scripts/locked_facts.json → 244 keys; CONCISE_BILINGUAL_FACTS in precompute_rag_embeddings.py):*
- **Q13** — added `brela_striking_off_non_filing`: non-filing → deemed defunct → Registrar's 30-day notice →
  struck off under Companies Act Cap 212; own-accord strike-off (2019 amendment); restoration via High Court;
  **no fixed term** (companies have no term). Fabrication ("lazima uishe muda kwanza") added to `wrong_patterns`.
  Section numbers kept in metadata only (R.E.2023 renumbers s.400A→s.403).
- **Q14** — added `osha_vs_wcf_roles` + `small_headcount_still_register`: OSHA registers/inspects **all**
  workplaces (s.16 OSH Act 5/2003), does **not** pay compensation; WCF compensates **from employee 1** (0.5%
  levy, no minimum count). Fabricated "2-employee WCF threshold" added to `wrong_patterns`; the short
  high-concentration fact out-ranks the minimum-shareholders distractor.
- **Q16** — kept `efd_threshold_tzs_11m` **pristine** (byte-identical to the deployed 213-index, preserves the
  eval_347 200M-contrast) + added separate `efd_not_every_business`: not every business needs an EFD;
  VAT-registered always; non-VAT ≥ TZS 11M; below 11M & unregistered may use manual receipts. **11M encoded per
  the primary-over-practitioner hierarchy (D-VATWH-1 precedent)** — TRA live pages say 11M; practitioners say 14M.

*Process:* full R15 regeneration cycle (Kaggle e5-base, cache-busted HEAD verify) → **217-fact index**
VERIFICATION PASSED 217/217 with the three verbatim edge questions added to the critical-query set; index
fetched + dual-committed byte-identical to `chike-inference/` + `kaggle/`; Modal redeployed. A methodology
flaw (verification paraphrases too lexically close to fact wording) was caught by a **negative live re-test**
and fixed by switching verification tuples to verbatim edge questions + a local e5 gate
(`scratch/local_rag_gate.py`) with held-out paraphrases. Live re-test #2 confirmed all three FIXED on the
217-index Modal endpoint (`eval/results/factacc_retest_a72c113.json`): Q13 retrieves
`brela_striking_off_non_filing`, Q14 `small_headcount_still_register` (rank 1), Q16 `efd_not_every_business` (rank 1).

*Comprehensive gate — `5a62c00` vs baseline `afef9dd`* (`eval/results/gate_orchestrator_combined_5a62c00.json`,
CHIKE_JUDGE=1, pinned DeepInfra seed=42, majority-of-5):
- **Target bucket UP:** fact_path reliable **85.4% → 87.7%** (111→114/130) raw 86.4%→88.0%. **Both gates still pass.**
- **Judge-augmented** 76.4% → **76.9%**. Net −1 raw / 400 (5 gained, 6 lost).
- **Collateral gain:** OSHA **+3** (eval_177/187/391) from the new OSHA/WCF facts.
- **Known-minor accepted (founder, no further regen):** `eval_355` (efd_compliance) — the deliberately
  adversarial *1,000-below-threshold* trap (turnover 10,999,000) flipped gold "Hapana" → "Ndiyo": the generic
  `efd_not_every_business` now leads retrieval and tips the boundary reasoning (both correct EFD facts are still
  retrieved; it is a generation-boundary flip, not a missing fact). `eval_304` = scorer artifact (afef9dd passed
  by number-overlap luck; neither run answers the structure-choice question). `eval_383`/`eval_208`/`eval_378`
  flips = run-to-run gen/judge noise (correct fee still retrieved rank-2; vat/sdl untouched by any fact change),
  offset by the OSHA/nssf gains.

*Commit trail:* `4912602` → `b4e6722` → `b54eb23` → `f1e3d30` → `68b9cba` → `b7666b6` → `a72c113` (217-index) →
`5a62c00` (live re-test artifact) → close-out. Not blocking; superseded ROUTING-GAP-PAYE priority ordering — done.

### ✅ ROUTING-GAP-PAYE — SHIPPED and GPU-CONFIRMED (2026-07-26 fix `3144a98`; confirmed 2026-07-27)

Approved and SHIPPED. `_LEVY_CUES` PAYE extended with six everyday phrasings (`kodi ya serikali`,
`kodi ya kipato`, `kodi ya ajira`, `kodi inayokatwa`, `kodi ya mfanyakazi`, `kodi yake`). Offline
validation: routing tests **35 passed** (positives for each phrasing incl. edge_04/05; negatives for
property tax / VAT / bare-"kodi" definition); full-400 detect_intent **0 changes** (exact decompose+route
method); full offline suite **272 passed** (was 270).

**GPU confirmation DONE (real Modal, v16 live weights, same method as the discovery probe).** Full 20-edge
re-run at `3144a98`; artifacts persisted: `eval/results/edge20_v16_run1_prefix_67e9e4c.json` (before) and
`eval/results/edge20_v16_run2_3144a98.json` (after).

**Before/after — the two target questions:**
| | edge_04 (resident) | edge_05 (non-resident) |
|---|---|---|
| phrasing | "…kodi ya serikali inayokatwa ni ngapi?" | "…si mkazi… kodi yake ni kiasi gani?" |
| run-1 routing/answer | **fact** → PAYE **128,000** ❌ | **fact** → PAYE **270,000** ❌ |
| run-2 routing | **compute[paye]** ✅ | **compute[paye]** ✅ |
| engine result | `applicable=True amount=188000` resident=True | `applicable=True amount=450000` resident=**False** (read "si mkazi") |
| working | `128,000 + 30%×(1,200,000−1,000,000) = 188,000` | `15% × 3,000,000 = 450,000 (kodi ya mwisho…)` |
| run-2 answer | **188,000** ✅ | **450,000** ✅ (correct flat-15% detection) |

**D-FIDELITY-1: armed, correctly not needed** — both model bodies were faithful to the authoritative
working this decode (edge_04 body computed 188,000 matching the working; edge_05 body stated "asilimia 15"
with no contradictory figure), so the guard passed them through (`raw_generated`==body; nothing blanked).
The guard remains the validated backstop for a contradicting decode; this run simply didn't trigger it.

**Zero regression:** all other 18 questions **byte-identical** run-1↔run-2 (routing AND answer text, greedy
decode); the known-safe clarifications (Q6, Q8 tiered NSSF, Q10 WCF distractor, Q11, Q18 mixed) unchanged.
Only edge_04/edge_05 changed. The single most common real question — "how much tax comes out of my salary,"
phrased naturally — is now on the protected compute path.

**Deferred follow-up (tracked, lower priority):** generalized safety net — *"any in-scope
payroll-context `kodi` + money-ask with no other levy → PAYE fail-safe"* — closes the whole class
rather than the two confirmed instances, but is a real scope-widening that needs its own blast-radius
analysis (same discipline as the natural-path fallback / explicit-levy over-capture / wrong-base term
list, each of which required a dedicated scoped investigation). Not part of this fix.

Original scope preserved below for the record.

### 🔧 ROUTING-GAP-PAYE — original scope (2026-07-26)

**Blast-radius sweep (`chike.routing.detect_intent` over all 400 gate questions + the 20 edge questions).**
"Looks like a levy-amount question (payroll ctx + number + money/derive ask) but routed to FACT": **400-gate
= 0 genuine mis-routes** (3 flagged all correctly fact: eval_240 GN605A avg-wage fact lookup; eval_303
property tax = OOC, intercepted before routing; eval_398 custom 15%/5% split); **20-edge = 2** (edge_04,
edge_05 — both PAYE). The 400-gate is **blind by authoring bias** (its questions name their levy, per the
routing docstring); natural phrasing is only exercised by the edge set.

**PAYE is uniquely exposed.** SDL/NSSF/WCF natural-phrasing amount questions fail SAFE: a generic deduction
word (`makato`/`michango`) → `ambiguous_multi` → compute-clarify, and jargon cues (pensheni→nssf,
ufundi→sdl, fidia→wcf) cover the rest. PAYE's everyday word `kodi` is in **neither** `_LEVY_CUES` (only
"kodi ya mapato"/"kodi ya mshahara") **nor** `_GENERIC_LEVY` ("ya serikali" ≠ "kwa serikali"), so a
`kodi`-phrased PAYE question falls through to fact and the model free-computes a wrong number.

**Mechanism:** gap in `_natural_levy` cue lists (detect_intent path 2 / Candidate C). Same lexical-cue
detector the original router fix used — NOT a distinct problem.

**Proposed fix (lexical-cue extension, same pattern as the router fix):** add everyday PAYE phrasings to the
`_LEVY_CUES` PAYE list — `kodi ya serikali`, `kodi ya kipato`, `kodi ya ajira`, `kodi inayokatwa`, `kodi ya
mfanyakazi`, `kodi yake`. Offline simulation over 400+20: routes **exactly edge_04→paye and edge_05→paye**,
**zero** other routing changes on the 400 (no new false compute-routes). Safety: the OOC classifier runs
BEFORE routing, so property/capital-gains/etc. "kodi" questions are intercepted first — the PAYE cues can
only affect in-scope questions. `kodi yake` is the broadest cue (fires only under path-2's payroll+number+
money-ask guard); flagged for review, tighten if needed.

**Expected post-fix:** edge_04 → paye compute → 188,000 (resident: 128,000 + 30%×200,000); edge_05 →
non-resident flat 15% = 450,000 (`paye_resident` reads "si mkazi"); D-FIDELITY-1 then guards any body
contradiction. **Validation plan:** unit tests in `tests/test_routing.py` (new PAYE phrasings → 'paye';
negatives: "kodi ya majengo"/property, "kodi ya VAT", bare-"kodi" definition not over-routed); full-400
detect_intent no-regression (0 changes, shown); full offline suite green; founder GPU re-run of the 20-edge
(or just Q4/Q5) confirming paye compute + correct figures. **Report before implementing — same rigor as
D-NSSF-1/D-FIDELITY-1.**

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

## 🔦 STRUCTURAL GATE FINDING — the live `GATE PASSED` number does NOT apply `scorer_reliability` (2026-07-26)

**Stated plainly because it changes what "the gate" has actually been measuring:** the production
gate `kaggle/eval.py` — the file that prints `GATE PASSED` and whose `in_corpus` accuracy gates
every product launch — scores **every** in-corpus question raw via `score_question`
(`in_acc = in_pass / len(in_corpus)`) and **never calls `scorer_reliability` at all.** The
`reliable=False` exclusion, the "8 exclusion categories," and the **133-question measurement gap**
that this entire frontier-judge investigation (follow-up #3) has characterized live **only** in the
*analysis* harness `kaggle/eval_orchestrator_combined.py` (which reports reliable-denominator scoring
alongside raw) and in `chike/scoring.py::scorer_reliability`.

**Consequence:** the 133 questions the regex scorer *itself admits it cannot verify robustly* have
**not** been excluded from the live gate — they have been **silently included in the raw pass/fail
number the whole time**, each scored by the mechanism that flags itself as unreliable on exactly
those cases. So the headline gate accuracy (e.g. the v15 first-gate-pass 87.9% in-corpus) rests, for
~a third of its denominator, on verdicts the project's own scorer marks low-confidence. This is not a
regression introduced this session — it is the pre-existing state of the gate, surfaced while tracing
the item-5 integration seam.

**Not being "fixed" reflexively.** Making `eval.py` exclude the 133 would *change the live gate's
denominator and its historical comparability* — a real decision, deliberately deferred (it was option
3 of the item-5 gate-integration fork; founder chose the conservative report-alongside path). Item 5
instead layers the judge as a **transparency overlay** in the analysis harness (raw vs reliable-denom
vs judge-augmented, side by side) so the size and direction of this gap becomes *visible and
quantified* in every run **without** silently moving the launch-blocking number. Whether to later
promote the reliable-denominator (or judge-augmented) number to the actual `GATE PASSED` trigger is a
separate, explicit call, gated on work-item-2 ground truth. **Tracked; do not silently change
`eval.py`'s denominator without a deliberate decision + a re-baseline of the historical gate numbers.**

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

### TRACKED KNOWN LIMITATION — decomposition coverage gap (2026-07-20, backlog, low urgency)
`decompose_query` does not split some period-joined / sentence-initial-`Pia,` clauses: a mixed
compute+fact question phrased as *"...nihesabie SDL. Pia, ada ya BRELA ya mwaka ni ngapi?"* (a
single `?`, second clause joined by "Pia," after a full stop) stays **one** sub-question. It then
funnels entirely into the single compute (SDL) route, and the trailing fact clause **corrupts the
compute extraction** — the gross payroll `milioni 12` was read as **1,000,000 instead of
12,000,000** (the "mwaka"/second-figure context in the un-split clause misleads the deterministic
amount parser). A two-`?` phrasing decomposes correctly and both sources come back right (SDL on
12M = 420,000 + BRELA annual return = 22,000), so this is purely a **decompose-coverage** gap.
Orthogonal to Phase B (route-aware merge) and to the backstop retirement — neither caused it and
neither fixes it. Discovered while running the Stage 1 mixed-compound real-weights test; the test
now uses a decomposing phrasing and notes this inline. **Backlog:** extend `decompose_query` to
split "Pia,"/period-joined clauses (and add a guard so an un-decomposed multi-figure question does
not silently feed a wrong figure to the rules engine). Not blocking; no current production impact
(production run() has no compute path).

**Tracked instance — eval_322 (enumerated compound, 2026-07-24).** *"Nataka kujua mambo matatu:
kwanza kizingiti cha VAT, pili kiwango cha SDL, tatu je nitoe risiti ya EFD kwa muamala wa TZS
5,000?"* — a **`kwanza…pili…tatu` enumeration** whose three parts are all directly answerable
**facts** (VAT threshold 200M/100M; SDL rate 3.5%; EFD required for any amount). It does not
decompose; the "SDL rate" fragment is mis-routed to **compute** and emits a salary/count
clarification, and the VAT-threshold and EFD parts are **dropped entirely**. Same root phenomenon
as the "Pia,"/period-joined gap above — a new *instance*, not a new defect. Found during the
Finding-2 individual verification of the 5239190 run (it was the 1 of 23 "safe never-guess"
clarifications that did NOT hold up). **Per option (b): logged here, no engine change this session.**
Fix would be the same enumerated/period-clause `decompose_query` extension (+ the never-guess
multi-figure guard), with a full 400 no-regression sweep.

## ✅ Ordinal-enumeration decomposition (`_split_ordinal_enumeration`) — SHIPPED (2026-07-24) — router follow-up #2 of 3

**The second of the three tracked follow-ups from the Phase D router investigation.** Preceded
by a full characterization (Steps 1-3, offline, pure string logic) before any code, given the
much broader blast radius — decomposition sits upstream of routing/retrieval/extraction/merge for
all 400 questions.

### Characterization findings (the scope was much smaller than the label suggested)
- **Baseline:** of 400, only **3 decompose** today (eval_318 pass / eval_321 fail / eval_330 pass,
  all via `na pia`/enum); 397 stay whole. Snapshot anchored at `scratch/decomp_baseline_snapshot.json`.
- **The `"Pia,"` period-joined pattern = 0 real gate instances.** A direct search for a sentence-
  boundary `[.!] Pia,/vilevile/aidha` across all 400 returns **zero** — the logged example
  (*"…nihesabie SDL. Pia, ada ya BRELA…"*) was a **constructed** illustration, never an actual gate
  question. Worth stating plainly: **half the originally-scoped problem did not exist in real data.**
  (The 6 `pia` hits are all adverbial "also/too" inside one question, or multi-part via other
  connectors — not the period-joined shape.)
- **The ordinal `kwanza/pili/tatu` pattern = exactly 1 real case (eval_322).** The other raw hit,
  eval_290 (*"watu 3 wa kwanza… wanne wanaofuata… watano wa mwisho… SDL?"*), is a **tiered-payroll
  compute** question — "kwanza" = "the first [group]", not "firstly [question 1]" — a false positive
  that must stay whole.
- eval_322's three parts (VAT threshold / SDL rate / EFD receipt) are **all facts**, and once split
  each routes to `none` (fact) — so **decomposition alone is sufficient**, no compute/extraction change.

### Fix mechanism (decomposition-layer only; pure string logic)
`_split_ordinal_enumeration` fires **only** when BOTH signals are present: an announce phrase
(`_ORDINAL_ANNOUNCE`: `(mambo|maswali|masuala|vitu|mengi) (mawili|matatu|manne|matano|sita|saba|
kadhaa)`) AND a **sequential ordinal run** starting `kwanza`→`pili`[→`tatu`…], each present and
strictly after the previous, matched as whole words (never found inside `matatu`/`wanne`/`watano`).
It splits on the ordinal delimiters and drops the announce preamble (each listed item is self-
contained). Requiring **both** signals is what excludes the bare-`kwanza` tiered-payroll class and
the adverbial-`pia` class. Wired into `decompose_query`'s early-return guard and as a split branch
after the enum branch (fires only when the `?`/connector/enum paths produced nothing usable).

### Validation (exactly the plan)
- **Full-400 before/after decomposition diff vs the snapshot: exactly 1 question changed —
  eval_322** (n=1 → n=3: `['kizingiti cha VAT', 'kiwango cha SDL', 'je nitoe risiti ya EFD kwa
  muamala wa TZS 5,000?']`). The 3 pre-existing splits (eval_318/321/330) are **byte-identical**.
- **All 14 false-positive candidates stay whole (n=1):** eval_290 (tiered payroll), eval_044/180/
  186/206 (adverbial "pia"), eval_345 (comparison ref), eval_051/052/055/058 (single question,
  multiple domain keywords), eval_331 (conditional if-yes-then), eval_171/174/219 (context + one ask).
- The 3 new eval_322 sub-questions all route to `none` (fact), as predicted.
- Unit tests (`tests/test_decomposition.py` 6 → 10): 3-way split; bare-ordinal tiered payroll not
  split; adverbial "pia" not split; requires-both-announce-and-two-ordinals guard.
- **Full offline suite: 208 passed, 0 failed.**

### Scope held
eval_320/eval_319 (compute enumeration — a `levy-list + verb` shape needing compute routing AND an
N-way merge) are **deliberately deferred as a separate, higher-risk pattern** with its own future
investigation, NOT folded in. eval_332 (3-part gn487a) **excluded as a scorer artifact** — the model
already answers all three parts correctly whole, so decomposition would not move its score.

### Gate-number caveat (unchanged discipline)
Routing-quality fix: eval_322 is `pass=False` today and production `run()` has no compute path, so
this **cannot move the reliable-subset number on its own**. It removes the mis-route (SDL fragment →
compute clarification) and the dropped VAT/EFD parts; whether the merged 3-fact answer clears the
overlap scorer is confirmed by **folding into the next scheduled 400-run** — no separate GPU cycle.

**Follow-up #2 of 3 COMPLETE. Remaining: #3 — frontier-judge / semantic scoring (the largest in
scope; directly addresses the MEASUREMENT GAP — ~a third of the 400 scored by a mechanism that
admits it cannot verify its own answers in either direction).**

## 🔎 Frontier-judge scoring — IN PROGRESS (work item 1 of 5 DONE, 2026-07-25) — router follow-up #3 of 3

**Status-check before scoping (confirm before building, same discipline as #1/#2). #3 does NOT
start from zero — a completed, persisted bake-off already exists (2026-07-16). But "validated"
means a feasibility/comparison win, not a precision-measured, wired-in scorer, and it was run on
190 questions, not the current 400.** This entry is the documented baseline for the eventual
dedicated session; NONE of the five work items below has been started.

### Groundwork inventory (two tiers)
- **Scratch (exploratory, local, gitignored):** `nli_regression_190.py` (mDeBERTa),
  `nli_xlmr_190.py` (xlm-roberta-large-xnli), `nli_round2.py` (threshold-tuning + entailment +
  cross-lingual on the 14-example set). All are **contradiction-demotion** experiments (demote a
  regex-PASS→FAIL only when NLI contradiction ≥ 0.70) — NOT full judges.
- **Committed, reusable harnesses (`kaggle/`):** `nli_regression.py` (mDeBERTa, fetch-and-run,
  persists to HF) and **`judge_regression.py` — the real LLM-as-judge** on OpenRouter
  `qwen/qwen3-32b`. Two stages: STAGE 1 = 14 audit examples vs known ground truth
  (`scratch/audit14.json`); STAGE 2 = full 190 non-refusal questions, judge verdict
  (correct/wrong/undetermined) vs the current `score_question`+`scorer_reliability`. Persists
  `judge_regression_qwen3-32b.json` to HF v15. Models actually called across the bake-off:
  `intfloat/multilingual-e5-base`, `mDeBERTa-v3-base-xnli` (280M), `xlm-roberta-large-xnli`
  (560M), `qwen/qwen3-32b`. Data: `audit14.json` (14 hand-labeled) + the **190** first-block v15
  results (`gate_001_results.json` on HF).

### What was actually produced (persisted to HF v15, git_head 8efdd32 — read from saved data)
- **Embeddings REJECTED** (cosine is polarity-blind). **mDeBERTa NLI REJECTED** (5 false-demotions
  @190, high-confidence). **xlm-roberta-large NLI REJECTED, worse** (13 false-demotions @190).
- **qwen3-32b judge "genuine improvement":** STAGE 1 **12/14** vs ground truth (1 harmful
  false-demote, 0 false-promotes, and it **rescued 2 answers regex had wrongly FAILED**); STAGE 2
  **covered all 71 currently-EXCLUDED questions** with a verdict, 13 demote / 6 promote
  **disagreements with regex**, 101 agreements, 0 API errors, **$0.018 / 160s**.

### Precise reading of "already validated earlier this session" (PROGRESS line ~613)
"Validated" = **a completed comparative bake-off proved the frontier-judge is the RIGHT approach**
(beat NLI + embeddings, matched 12/14 ground truth, covered all 71 excluded, ~2 cents). It does
**NOT** mean: (a) a measured precision/recall against a real ground-truth set — only **14** are
adjudicated; STAGE 2's 13/6 are **disagreements with an imperfect regex baseline, explicitly "not
proven errors"**; (b) a production-ready scorer — the 2026-07-16 entry's OWN recommendation says
**"do NOT adopt it as a silent automatic scorer"** until `procedure` over-strictness is
characterized, it is escalated to a larger frontier model, and the 13/6 are adjudicated against
`locked_facts.json`; (c) a settled model — a separate **non-determinism finding** shows qwen3-32b
**flips verdicts even at temp=0** and **misreads Swahili compound numerals** (laki/robo/milioni).

### The scorer seam (confirmed ready, currently untouched)
`chike/scoring.py::scorer_reliability(q, generated)` returns `(reliable, reason)` and is exactly
where the **8 exclusion categories** live; its docstring explicitly names *"a semantic judge
(LLM-as-judge / frontier-model scoring)"* as the intended fix, and `judge_regression.py` already
layers on top of it. **What does NOT exist:** any wiring of a judge verdict back into
`scoring.py` / `run_eval.py` / the gate — `scoring.py` is deliberately unchanged.
(`chike/model_abstraction/frontier_api.py` is a GENERATION-backend stub for routing *compute*
questions to a frontier model — `generate()` raises `NotImplementedError` — NOT the scorer seam.)

### Five genuinely-new work items for #3 (none started)
1. **Scale to 400. ✅ DONE (2026-07-25)** — see the "Work item 1 — census" subsection below. All
   prior judge/NLI work targeted the **190** `gate_001` set; the census now covers the full
   **133/400** MEASUREMENT GAP on the `5239190` baseline **plus** an audit of the 252 reliable
   verdicts.
2. **Real adjudicated ground truth.** Expand beyond 14 hand-labeled examples to a human-adjudicated
   sample across the `reliable=False` categories, to measure the judge's TRUE precision/recall
   (STAGE 2's 13/6 are unadjudicated disagreements).
3. **Characterize the `procedure` over-strictness** (6 of the 13 demotions — the judge's known weakness).
   **✅ DONE (2026-07-25)** — see "Work item 3 — procedure/definition over-strictness characterization"
   below. One narrow deterministic fix shipped (commit `22af4ad`); everything else routed to item 5.
4. **Resolve non-determinism.** ✅ DATA-GATHERING DONE (2026-07-25) — see "Work item 4" below.
   Pinning (seed + single provider) cuts flips but leaves 2 correct↔wrong flips at scale; a subsample
   sufficiency proof (0/780 at N=3, 0/234 at N=5 across all 39 IDs) recommends pinned-provider +
   **majority-of-5** (robust to 4-2, 3-3→undetermined). Wiring the rule is deferred into item 5.
5. **Integration design.** ✅ BUILT (2026-07-26) — see "Work item 5" below. Judge wired as a
   conservative, asymmetric CONFIRMATION overlay: fills the `reliable=False` gap, flags (never
   flips) `reliable=True` disagreements, reports a third "judge-augmented" number alongside
   raw + reliable-denom. `scoring.py` and the live `GATE PASSED` trigger unchanged (report-alongside).

### Work item 5 — judge→scoring integration (BUILT, 2026-07-26) — the last piece of follow-up #3

**Prior-work check first (crash-recovery discipline):** searched scratch/ + eval/results/ + repo-wide
for a "267 reliable=True" judge run the previous session might have left — **none exists.** The only
prior judge pass is the **census** (`eval/results/judge_regression_qwen3-32b_400.json`): single-shot
(N=1), non-pinned, over all 385 non-refusal (252 reliable + 133 excluded), **$0.0407 / 349s @ 8
workers / 7.17s per call / 0 errors** — the actuals the cost model below is grounded on. Reconciled
the "267": real reliable=True is **252**; `400 − 133 = 267` conflates the 15 OOC refusals (separate
refusal gate) into the count.

**Structural finding (documented as its own headline above):** the live gate `kaggle/eval.py` **does
not apply `scorer_reliability` at all** — it scores every in-corpus question raw, so the 133-question
measurement gap has been *silently inside* the live gate number, not excluded. This is why item 5 is a
**transparency overlay**, not a gate-logic change: it makes the gap visible/quantified without moving
the launch-blocking number.

**The four open design questions — resolved (founder-confirmed):**
1. **Adjudicate the `reliable=False` gap? YES** — the judge FILLS it (regex explicitly abstained there).
2. **Confirmation/override on `reliable=True`? Confirmation yes, override NO** — disagreements emit an
   adjudication QUEUE (false-pass / false-fail candidates), never auto-flip. This is exactly how the
   census's disagreements drove real engine fixes this session (D-NSSF-1/D-WCF/D-PAYE), not a per-run flip.
3. **`undetermined` in the denominator?** Never moves a regex-scored question in/out. In the gap-fill:
   `correct`→pass, `wrong`→fail, `undetermined`→**excluded** (+ a conservative `undet=fail` floor is
   also reported, to bracket true accuracy). This kills the "farm undetermined to shrink the denominator"
   exploit — the denominator stays anchored by regex.
4. **When does the judge override regex? NEVER in the live gate number.** It only fills the gap and
   flags disagreements. Promotion to an actual override is gated on **work-item-2 ground truth** — a
   separate, explicit future call.

**What was built (all offline-tested; no `scoring.py`/`eval.py` pass/fail change):**
- **`chike/judge.py`** (new, eval-only leaf module: stdlib + `requests`). The item-4 design made
  reusable — pinned provider (**DeepInfra, seed=42, `allow_fallbacks:false`**) + **majority-of-5**
  (`majority_vote`: strict plurality, any tie→`undetermined`) — plus the item-5 pure aggregation
  `build_confirmation_report` (the three numbers + gap-fill + disagreement queue) and `judge_gradeable`
  (in-corpus, non-clarified; clarifications are deliberate never-guess, excluded like the census's 30).
  **Explicitly EXEMPT from the modal_app↔eval.py dual-file-sync rule** — it is a scorer overlay (like
  `scorer_reliability`), never on the production serving path.
- **Wired into `kaggle/eval_orchestrator_combined.py`** as an OPTIONAL post-scoring pass (runs when
  `OPENROUTER_API_KEY` present and `CHIKE_JUDGE!=0`; the GPU gate runs fully without it). Prints the
  three numbers side-by-side + gap-fill + disagreement queue + provider-pin verification; persists a
  `judge_overlay` block in the artifact. Touches no bucket score, no `scoring.py`, no `GATE PASSED`.
- **`scripts/judge_augmented_local.py`** — local twin (no GPU) over the pinned **5239190** baseline
  (asserts `commit=='5239190'`), the direct successor to the single-shot `judge_regression_400.py`.
  Lets the three-number report be produced now from existing data. Writes
  `eval/results/judge_augmented_5239190.json`.
- **`tests/test_judge.py`** — 15 tests locking the safety invariants (5-1→majority side, 2-2-1 tie→
  undetermined, parser ladder, pin held across 5 calls via injected fake `requests`, gap FILLED but
  reliable=True NEVER flipped, undetermined never moves the trusted denominator, clarifications excluded).
  **Full `tests/` suite: 257 passed** (was 242 + 15 new).

**Cost/scale (grounded in census actuals):** majority-of-5 over the 307 in-corpus non-clarified rows of
the 5239190 baseline = **~1,535 calls ≈ $0.16, ~20–25 min @ 8 workers** (full-400 Kaggle harness path
grades ~all non-refusal ≈ 1,925 calls ≈ $0.20). **Cheap enough for a normal gate cycle** — dwarfed by
the GPU generation step, and OpenRouter-parallel. Caveat: the DeepInfra pin serves from one provider, so
throughput may trail the census's provider-agnostic routing.

**FIRST LIVE RUN — DONE (2026-07-26, `eval/results/judge_augmented_5239190.json`).** Ran
`judge_augmented_local.py` over the pinned 5239190 baseline: 307 in-corpus non-clarified answers ×
majority-of-5, **provider pin held (DeepInfra only), 0 API errors, $0.165, 933s (~15.5 min)** — cost/latency
match the census-grounded projection. **The three numbers:**
- **raw in-corpus 254/384 = 66.1%** (what the live `eval.py` gate computes)
- **reliable-denom 184/251 = 73.3%** (regex, gap excluded)
- **judge-augmented 247/335 = 73.7%** (gap filled; undet excluded) — floor(undet=fail) 73.3%

**Headline finding: the judge-augmented number CONFIRMS the reliable-denominator (73.7% ≈ 73.3%) rather
than diverging.** The 86-question `reliable=False` gap, independently adjudicated by the judge (63 correct /
21 wrong / 2 undetermined), performs about the same as the reliable subset — so the honest reduced-denominator
method (adopted 2026-07-14) was **not** concealing a materially different-performing third of the gate. Raw
(66.1%) sits ~7 points below both because it scores ~49 deliberate clarifications as fails and mis-scores the
unreliable gap — quantifying how much the live raw gate *understates* true in-corpus accuracy. **Disagreement
queue: 27 false-pass + 11 false-fail candidates** (vs the census single-shot's 27+12); majority-of-5 shifted
~5 IDs each way — the expected stabilisation. Notably the two item-4 dangerous-flip cases land exactly as the
design intends: **eval_228 → a tie → `undetermined`** (the honest coin-flip, not the census's unlucky
single-shot verdict), **eval_230 → stable false-fail** (judge says correct). 4 ties total
(eval_034/074/228/360), all correctly parked at `undetermined`.

**Remaining (both founder-gated):** ~~the long-held single comprehensive gate run covering every change
since 5239190~~ **— DONE 2026-07-26, commit `afef9dd`; see the CLOSE-OUT entry below.** Only **work item 2
(real adjudicated ground truth)** stays open — the prerequisite before any promotion of the judge-augmented
number to the live `GATE PASSED` trigger. Its input is now the **fresh 25+7 disagreement queue** from the
afef9dd run (superseding the stale 27+11 from the 5239190 baseline).

## 🏁 CLOSE-OUT — comprehensive confirmation run `afef9dd` (2026-07-26): the entire router-investigation / defect-fix cycle is CLOSED

**This is the closing entry for the whole cycle** — router remediation Phases A–D, all three
router-investigation follow-ups (#1 explicit-levy money-ask guard, #2 ordinal-enumeration decomposition,
#3 frontier-judge scoring), and now the single comprehensive gate run that confirms the accumulated fix
cluster at scale. A fresh 400-question orchestrator regression was run on GPU (founder-executed on Kaggle)
at commit `afef9dd` with the item-5 judge overlay riding along (majority-of-5, pinned DeepInfra seed=42).
It exercises **every change since the `5239190` baseline**: fixed engine (D-NSSF-1 / D-WCF / D-PAYE /
D-DECOMP-1 multi-levy fan-out) + fixed RAG (213 facts) + v15 model + judge overlay. Artifact fetched
independently from HF and committed: `eval/results/gate_orchestrator_combined_afef9dd.json` (commit `0a2db58`).

**Bucket before/after (5239190 → afef9dd), raw AND reliable:**

| Bucket | raw base | raw fresh | Δ | reliable base | reliable fresh | Δ |
|---|---|---|---|---|---|---|
| adversarial_150 | 39.6% | **49.3%** | +9.7 | 54.4% | **62.1%** | **+7.6** |
| compute_type | 31.6% | **40.2%** | +8.6 | 41.2% | **46.9%** | **+5.8** |
| compute_type_genuine | 31.9% | **39.6%** | +7.7 | 40.0% | **45.8%** | +5.8 |
| staged_50 | 74.0% | **80.0%** | +6.0 | 73.2% | **80.0%** | **+6.8** |
| fact_path_190 | 86.7% | 86.4% | −0.3 | 85.0% | **85.4%** | +0.3 (stable) |

Every touched cluster moved up +5.8 to +7.6 pts (reliable); the untouched fact path held flat — exactly
the expected signature of engine/RAG fixes that don't touch the fact answers.

**Fix-cluster verification — each shipped fix confirmed present in the FRESH generation (read from persisted data, not the terminal paste):**

| Case | Fix | Evidence in fresh generation | Verdict |
|---|---|---|---|
| eval_121 (SDL, 8 staff) | applicability threshold | `FAIL→PASS`; *"Hapana… wafanyakazi 10 au zaidi… una wafanyakazi 8"*; judge=correct | ✅ landed |
| eval_318 (multi-levy, 11 staff) | D-DECOMP-1 fan-out | Computes all three: SDL 3.5%×5.5M=192,500; NSSF 20%=1,100,000; VAT threshold crossed | ✅ landed |
| eval_321 (multi-levy, 8 staff) | D-DECOMP-1 fan-out | `FAIL→PASS`; SDL=none(<10) + NSSF 640,000 + WCF 16,000 + OSHA yes — full fan-out | ✅ landed |
| eval_098/100/105/110 (NSSF) | compute/fact | Pass; voluntary membership; full-salary no-cap 200k+200k=400k | ✅ stable |
| eval_115 (GN 605A date) | fact/RAG | Correct: 1 Jan 2026, gazetted 13 Oct 2025 | ✅ stable |

*Known-open follow-ons (correctly NOT counted as regressions):* eval_124 / eval_320 (per-person / tiered
multi-levy) — the model **clarifies** instead of computing, which is the still-tracked **D-DECOMP-2 /
per-person aggregation** work; `reliable=False`, correctly excluded from the denominator.

**Prohibition-inversion continuity check — zero engine-introduced regressions.** Fresh set
`{eval_144, 155, 183, 332, 365, 391}` is a **strict subset** of the baseline's 8
`{144, 155, 183, 332, 343, 355, 365, 391}` — each verified `candidate_inversion=True` at 5239190 (including
eval_391, which was flagged at baseline though not written up by ID). **New in fresh: NONE. Resolved since
baseline: eval_343 + eval_355** (both now pass). All 6 remaining are the known adversarial leading-premise
polarity traps (gold is a counter-intuitive *"Hapana/La"*; model agrees with the surface framing). eval_391
is the genuinely-ambiguous one — its marker *"Ndiyo"* agrees with the leading *"sivyo?"* but its substance
is correct, so the judge scored it **correct** (it sits in the false-fail queue) while the polarity heuristic
flags it — precisely the ambiguity item-4/5 exists to surface.

**Per-question flip analysis (400 common IDs, no set drift): 24 real gains, 1 genuine stochastic loss, 2 false losses.**
24 `FAIL→PASS`, concentrated exactly in the fix clusters (NSSF/SDL/WCF/PAYE compute + adversarial). The 3
`PASS→FAIL`, dissected individually:
- **eval_259** (WCF compute) — baseline "passed" by computing `0.5% × 40,000,000` **on vehicle value** (the
  trap; WCF is on payroll) = a **false pass**. Fresh now correctly **clarifies** (*"nahitaji jumla ya
  mishahara"*). A **real improvement disguised as a raw-number drop.**
- **eval_048** (VAT-WH) — fresh answer is substantively correct, just shorter than gold; regex missed it,
  **judge=correct**, `reliable=False` (excluded). A **scorer artifact, not a regression.**
- **eval_039** (VAT-WH) — the **one genuine loss**: model emitted a self-contradictory answer this decode
  (*"Ndiyo… ni sawa"* then lists 3% vs 6%), judge=wrong. Non-deterministic model decode on a fact path the
  engine fixes don't touch — **not an engine fault.** Net: **24 real gains, 1 stochastic loss, 2 false losses.**

**Judge-augmented / reliable-denominator convergence — now TWICE-CONFIRMED evidence.** The three numbers
(base → fresh): raw 66.1% → **71.6%**, reliable-denom 73.3% → **77.0%**, judge-augmented 73.7% → **76.4%**.
The judge-augmented number lands **within 0.6 pt** of the reliable-denominator (77.0% vs 76.4%) — the same
result as the baseline local run (73.3% vs 73.7%, within 0.4 pt). The 91-question `reliable=False` gap,
independently judged, resolves at **65 correct / 22 wrong / 4 undetermined ≈ 74.7%** — statistically the same
population as the reliable regex set. **Stated plainly as positive evidence, not a coincidence of numbers:
across two independent runs the measurement gap the reduced-denominator method excludes was NEVER hiding a
materially worse-or-better-performing population.** Provider pin held (`providers_served: ['DeepInfra']`),
324 graded, 0 API errors.

**Bottom line:** every fix the cycle built landed and is verifiable in the fresh persisted generations;
+5.8 to +7.6 pts across all three touched buckets; the single real regression is a stochastic decode
artifact on an untouched fact path; no new prohibition inversions; and the judge overlay independently
reconfirms the reliable-denominator method. **The router-investigation / defect-fix cycle is CLOSED.**

**Still held (correctly deferred):** **work item 2 — real adjudicated ground truth** on the **fresh 25+7
disagreement queue** (25 false-pass: eval_027/028/034/066/071/075/106/120/132/145/162/164/171/223/234/235/
268/304/318/330/342/366/367/378/392; 7 false-fail: eval_029/094/131/187/230/233/391). This is the concrete
input for any future promotion of the reliable-denominator or judge-augmented number to the live
`GATE PASSED` trigger — a separate, explicit call. Not started; now has the right, current input.

## ✅ Work item 2 — ROUND 2 adjudication of the afef9dd disagreement queue (DONE, 2026-07-26)

**The fresh 25+7 queue from the `afef9dd` comprehensive run, adjudicated independently** against
`scripts/locked_facts.json` + CLAUDE.md §11 (NOT against the judge's or regex's stated opinion). Full
record: `eval/results/work_item2_round2_adjudication_afef9dd.json` (all 32 rows: question, gold, fresh
generation, regex/judge verdict, my truth C/W/A, root cause, basis). This supersedes the stale
5239190-baseline queue and is the concrete input for any future promotion of the reliable-denominator /
judge-augmented number to the live `GATE PASSED` trigger.

**Confusion matrix (24 clean cases; 8 ambiguous excluded):**

| | judge right | judge wrong |
|---|---|---|
| **regex right** | 0 | 1 (eval_164) |
| **regex wrong** | 23 | 0 |

- **JUDGE 23/24 = 95.8% correct** on the adjudicated disagreement set — consistent with (slightly above)
  the ~93% measured reliability. Single miss: **eval_164** (false-DEMOTE of a correct GN487A penalty
  answer — 10M/6mo/visa-revocation matches gold AND `gn487a_penalty_noncitizen`; the judge invented that
  the reference wanted "deportation"). Second confirmed judge-error data point (after item-1 STAGE-1's 10/14).
- **REGEX 1/24 = 4.2%** — expected: the queue is BY CONSTRUCTION the regex↔judge disagreement set, so in
  each clean case exactly one is wrong; in 23/24 the judge was right and regex wrong.

**Categorized findings:**
- **Confirmed real regex false-POSITIVES: 16** (model truly WRONG): eval_027/028/034/066/071/162/223/235/
  268/304/318/330/342/367/378/392. Root causes: **10 fact** (model/RAG gave a wrong fact where a correct
  locked fact exists — BRELA structures/company, EAC STR, PAYE max & non-resident, NSSF pension, mgeni),
  **4 generation** (hallucination/reasoning: eval_034 invented assumption; eval_268 **fabricated a
  turnover** the user never gave; eval_318 **inverted** the VAT 205M>200M comparison; eval_330 fabricated
  penalties + BRELA misdirect), **2 fidelity** (eval_367/378, see headline). **NONE trace to a new
  deterministic engine/routing defect.**
- **Every shipped engine fix confirmed correctly LANDED in the fresh generation:** eval_330→employee
  45,000 (D-NSSF-1), eval_367→750,000 flat (D-PAYE-1), eval_378→"SDL haihusiki" amount=None (SDL
  threshold), eval_318→SDL 192,500 + NSSF 1,100,000 (D-DECOMP-1 fan-out). The residual errors on those
  same questions are all MODEL-side (fact/generation/fidelity), not engine.
- **Confirmed real regex false-NEGATIVES: 7** (model truly CORRECT): eval_029/094/131/187/230/233/391 —
  all fit the six item-3 sub-patterns (terse-but-correct procedure/definition; institution-answer-no-number;
  number-as-definition; negative-framing polarity). **No new sub-pattern.**
- **Judge errors: 1** (eval_164, above).
- **Genuinely ambiguous/disputed: 8** — eval_075 (own-name reg nuance), eval_106/120/132 (incomplete not
  false), eval_145/171 (different-angle GN487A advice), eval_234 (documented NSSF-deadline inconsistency),
  eval_366 (reach-vs-exceed boundary). Not forced to a verdict.

**NEW-DEFECT DETERMINATION: no new deterministic defect.** All 16 confirmed false-passes are model-side.
The engine/router are correct in every compute case, including the two crash-relevant ones (eval_367/378).

### 🔴 HEADLINE FINDING — D-FIDELITY-1: model body can contradict the authoritative compute working

On a compute question the model can emit a WRONG figure that **leads** the answer, even though the correct
deterministic `ComputationResult.working` is appended right below it (`_render` returns
`f"{body}\n{working}"`, orchestrator.py:341). Two confirmed instances this round:
- **eval_378** (SDL, 8 staff): engine appended correct *"SDL haihusiki: wafanyakazi 8 (chini ya 10)"* (=0);
  model body led with wrong *"SDL = 5,000,000 × 3.5% = 175,000"*.
- **eval_367** (non-resident PAYE): engine appended correct *"15% × 5,000,000 = 750,000"* (D-PAYE-1);
  model body led with wrong *"264,000"* (a bogus progressive-band calc).

This is **not new** (documented in `_validate_and_clean`'s docstring as a deferred fidelity-check follow-up)
but is **not covered** by any D-* fix this session, and is **structurally serious**: it can silently
undermine EVERY engine fix shipped this session by showing the user a wrong number the engine got right.
**Promoted to its own defect item — D-FIDELITY-1 (scoped below).**

### ✅ D-FIDELITY-1 — SHIPPED and GPU-CONFIRMED (2026-07-26) — commit 75421f0

Approved as scoped and SHIPPED. `chike/fidelity.py::body_contradicts_working` +
`_validate_and_clean` blanking (body → `_render` emits the working alone; `raw_text` preserved).
Offline validation: 13/13 detector unit tests (Case A/B/B0 + the 10 benign shapes confirmed never
firing); full suite **270 passed** (was 257); re-render over the saved afef9dd 400 fired on **exactly
eval_367/371/378**, byte-identical on all other 397 rows.

**GPU confirmation run DONE — commit `75421f0`, artifact `eval/results/gate_orchestrator_combined_75421f0.json`**
(fetched independently from HF adapter-v15, verified `commit==75421f0`, 400 rows, 0 empty/ERROR;
judge overlay `providers_served=['DeepInfra']`, seed=42, N=5, 324 graded, **0 API errors**).

**The three target rows — all exactly as scoped (GEN = working alone; RAW retains the wrong body; judge 5/5 correct):**
| row | generated (rendered) | raw_generated (preserved) | pass | judge |
|---|---|---|---|---|
| eval_378 | `SDL haihusiki: …wafanyakazi 8 (chini ya 10)…` (no 175,000) | `SDL = 5,000,000 × 3.5% = 175,000` | True→**False** | correct 5/5 |
| eval_367 | `PAYE (asiye mkazi) = 15% × 5,000,000 = 750,000…` (no 264,000) | `PAYE = 264,000 (15% × 1,760,000)` | **True** (stays) | correct 5/5 |
| eval_371 | `SDL haihusiki: …wafanyakazi 7 (chini ya 10)…` (no 98,000) | `SDL = 2,800,000 × 3.5% = 98,000` | False (stays) | correct 5/5 |

**Only ONE pass/fail flip in all 400: eval_378 (PASS→FAIL).** Zero other flips; `fact_path_190` and
`staged_50` pass counts byte-identical; zero stochastic decode noise this run.

**All bucket movement is eval_378 alone, double-counted.** It is in both bucket C (`compute_type` =
any `compute==True`) and bucket D (`adversarial_150` = `source=='additions_003'`), reliable=True,
genuine — so its single flip drops: compute_type 41→40 (raw) / 23→22 (rel); compute_type_genuine
40→39 / 22→21; adversarial_150 71→70 (raw) / 54→53 (rel). Nothing else moved.

**The literal "v-next ≥ afef9dd per bucket" criterion technically did NOT hold** (compute_type +
adversarial each −1 row, raw and reliable). **The reason is fully understood and is itself evidence of
the fix working, not a regression:** eval_378 went from a false-PASS (regex credited the wrong 175,000)
to a **regex false-FAIL** — the corrected `SDL haihusiki / TZS 0` answer has no numeric key the
number-scorer can match to gold "TZS 0", so regex drops it while the answer is now CORRECT (judge 5/5).
Judge-augmented accuracy flat (76.4%→76.4%); raw/reliable each −1 = eval_378 only. This is exactly the
measurement gap the judge overlay exists to catch — and it caught it.

**Disagreement queue 25+7 → 24+8, fully reconciled:** FP −eval_367 (now regex-pass AND judge-correct →
agree, leaves queue), −eval_378 (→FAIL, migrates to FF), +eval_397; FF +eval_378. eval_371 stays out of
the reliable-only queue (reliable=False → gap-fill, judge=correct). **Zero collateral, zero detector
false-positives:** only the 3 intended bodies were blanked.

**Two follow-ups logged (not urgent, not blocking — tracked, not patched reactively):**
- **SCORER-SEMANTICS-1 — number-scorer should credit "not-applicable / TZS 0" answers.** Concrete
  motivating case: eval_378 gold "TZS 0" is a correct answer that the number-scorer cannot credit when
  the reply says "SDL haihusiki / chini ya 10" (no matching numeric key). Same class as the item-3/item-5
  scorer-semantics gaps; the honest fix is either teach the scorer that gold "TZS 0" is satisfied by a
  not-applicable/zero verdict, or let the judge-augmented number carry it. Explicit, separate decision.
- **JUDGE-NONDET data point — eval_397.** `generated` byte-identical afef9dd↔75421f0 (compute=False, the
  guard never touches it), pass=True both runs; it entered the FP queue only because the judge's
  majority-of-5 verdict shifted **undetermined→wrong** between runs. Pure item-4 judge non-determinism,
  NOT a D-FIDELITY-1 side-effect — logged for whenever judge non-determinism work resumes.

Same characterize-before-fix discipline as decomposition/every structural change this session; original
scope preserved below for the record.

**Mechanism & hook point.** Compute answers merge as `body + '\n' + working` (`orchestrator._render`,
:341), where `working` is the deterministic `ComputationResult.working` and `body` is the model's free
generation. Nothing checks that `body` agrees with the authoritative result. The hook is per-SubAnswer in
`Orchestrator._validate_and_clean` (:319), which already holds both `sub.computation` (structured
`ComputationResult` — has `applicable`, `amount`) and `sub.text` (the isolated model body). Because it runs
per sub-answer, multi-levy fan-out rows are seen one compute at a time — no cross-levy confusion.

**Blast radius (full-400 afef9dd sweep, `scratch/dfidelity_sweep.py` + `dfidelity_detector.py`).** Of 103
compute rows (56 clarified/never-guess skipped), **exactly 3 true body-vs-working contradictions:
eval_367, eval_371, eval_378** (the 2 from the adjudication + eval_371 newly surfaced). 10 further
candidates are BENIGN breakdowns (body faithfully restates the working's figure with intermediate steps /
net-pay extras) and must NOT be touched. **The contradiction class is precise:** it occurs ONLY when the
engine applied a GATING/OVERRIDE rule that moves the answer off the naive `rate×base` (SDL `<10`→not
applicable; PAYE non-resident→flat 15%), and the model recomputed the naive figure anyway — i.e. it
re-derives exactly the *pre-fix* wrong answer, which is why it can silently undermine the session's engine
fixes.

**Detector spec (deterministic; validated EXACT — flags {367,371,378}, 0 false-pos on all 13 candidates):**
- Case A — `computation.applicable is False` (amount None): contradiction iff body contains a naive levy
  compute (`rate% × TZS base = TZS N`) asserting an amount. → covers 371, 378.
- Case B — `computation.amount` is a definite figure: contradiction iff that authoritative amount is
  **ABSENT** from the body while the body asserts some other levy result. (Robust: a faithful body always
  restates the correct figure; checking presence-of-correct is immune to intermediate band-base steps and
  net-pay extras that a naive "extra-number" rule would false-flag on eval_092/191/360/395.) → covers 367.
- Case B0 — amount 0 (within 0% band): contradiction iff body asserts a nonzero `= TZS N`.

**Proposed fix (deterministic, preferred over prompt).** On a detected contradiction, blank `sub.text`
(preserving `raw_text` for offline rescore) so `_render` emits the **authoritative working alone** (already
user-facing Swahili). Deterministic is chosen over prompt-hardening because (a) the model ALREADY receives
the working as a ground-truth "fact" in `_build_compute_prompt` and still ignored it in all 3 cases, so a
prompt can't *guarantee* deference; (b) it matches the architecture's load-bearing invariant *"arithmetic is
NEVER trusted to the model"* (ADR 0001). Prompt hardening is at most a complementary secondary measure.
Gate impact: eval_371 already fails (no change); eval_367/378 are current false-PASSES → corrected to the
right answer, removing a user-facing wrong number with no expected gate-number regression.

**Validation plan (same standard as D-NSSF-1/D-PAYE-1).** (1) Unit tests for the detector across Case
A/B/B0 + the 10 benign shapes (must stay untouched). (2) Offline re-render over the saved afef9dd 400: the
detector must fire on exactly the 3, and re-rendering them working-only must be correct; all other 100
compute rows byte-identical (proves no regression on saved data). (3) Fresh GPU full-400 orchestrator sweep
(founder-executed), require v-next ≥ afef9dd on every bucket. (4) Judge overlay rides along to confirm the 3
move to judge=correct. **Awaiting approval before writing any code.**

### Work item 1 — CENSUS of the 400-question gate (DONE, 2026-07-25)

**Harness:** `scripts/judge_regression_400.py` — a **local** re-point of `kaggle/judge_regression.py`
(the judge is pure OpenRouter `qwen/qwen3-32b`, no GPU, so it runs locally off `OPENROUTER_API_KEY`).
Input is **pinned to the committed** `eval/results/gate_orchestrator_combined_5239190.json` (baseline
archived this session, commit `959283f`); the harness asserts `commit == '5239190'` on load so it
cannot run against a stale baseline. Grades `row['generated']` directly (already `reply.text`); trusts
the stored `reliable`/`pass` fields (they *are* the 5239190 verdicts being characterized).

**Scope decision — CENSUS, not a sample.** `reliable=False` means "the regex scorer has low confidence
in its own verdict," **not** "the system failed to answer" (all 400 produced a real answer; 0 empty, 0
ERROR). So `reliable=True` means *regex is confident, not regex is right* — and this session has
repeatedly found confident-but-wrong regex verdicts. A 40-question spot-check of the 252 reliable
verdicts was rejected on the statistics (at a 3% true error rate — the order of bugs already found — a
clean 40-sample happens **30%** of the time; the 252 population is too small for an efficient middle
sample; the census costs only ~2¢/~3min more). So the judge did two jobs at once: **gap-fill** the 133
excluded **and audit** the 252 reliable.

**Run actuals:** 399 calls (14 audit + 385 non-refusal), **$0.0407**, ~438s total (STAGE 2 349s @ 8
workers), **0 API errors**. Output: `eval/results/judge_regression_qwen3-32b_400.json`.

- **STAGE 1 judge-trust: 10/14** vs hand-truth (down from 12/14 @190: 1 false-demote eval_176, 2
  false-promote eval_093/059, 1 undetermined eval_026). **The judge itself disagrees with hand-truth
  ~1-in-4 — so every candidate below is an adjudication LEAD, not a verdict** (this is exactly why
  work item 2 = real adjudicated ground truth exists).
- **GROUP 1 gap-fill (133 by exclusion reason):** compute_derived_number 48 (25 correct / **21 wrong** /
  2 undet), yes_no_polarity_unverifiable 28 (6 / **21 wrong** / 1), qualitative_number_no_numeric_key 27
  (18 / 7 / 2), yes_no_ground_truth_ambiguous 9 (6/2/1), morphological_overlap_gap 7 (6/1/0),
  year_only_numeric_key 6 (5/1/0), zero_or_not_applicable 6 (2/**4 wrong**/0), year_collision_match 2
  (2/0/0). The gap is **not** uniformly-correct-but-unscorable: ~57/133 read wrong, concentrated in
  compute-derived and polarity-unverifiable.
- **GROUP 2 regex-audit (252 reliable):** **27 false-pass** (regex PASS, judge WRONG) · **12 false-fail**
  (regex FAIL, judge CORRECT) · 17 undetermined · 30 clarified (deliberate, excluded — not bugs) · 166
  agree. Full disagreement IDs in the artifact; this list *is* the deliverable that turns work item 2
  from "audit a sample" into "adjudicate this concrete list."

### Work item 3 — procedure/definition over-strictness characterization (DONE, 2026-07-25)

**Method.** Ran the live `chike/scoring.py` functions against the 10 adjudicated false-fails
(eval_029/074/094/131/134/187/217/230/233/390), pulling each model output from the pinned
`5239190` baseline, to get exact matched-token sets rather than reasoning about the regex by
hand. The 10 resolve to **6 precise mechanisms**, only ONE of which is a cheap, narrow,
deterministic fix in the `'000'`/BUG-7 class; the rest are genuinely semantic → item 5.

**Sub-pattern 1 — spurious numeric key from a numeral-word inside the idiom "moja kwa moja"
(="directly"). ✅ FIXED (commit `22af4ad`).** `extract_numbers` matched `\bmoja\b`→`1` inside
the idiom, injecting a junk key that (a) suppressed the `qualitative_number_no_numeric_key`
exclusion → false FAILs (eval_134, eval_217), and (b) collided with the same idiom in the
model's own answer → coincidental false PASS verifying no content (eval_037). Blanking the
trigram before numeral extraction is **tightening-only** (removes a spurious key, never adds
one — the property that made the `'000'`/BUG-7 fixes safe to ship narrowly). Full-400 sweep:
exactly eval_037/134/217 → `qualitative_number_no_numeric_key`; eval_033 no-op; zero others.
7 new tests (`tests/test_scoring_number_idiom.py`); full suite 242 passed.

**Everything below → item 5's semantic-judge worklist (do NOT regex-patch):**

- **Sub-pattern 2 — answer_type mislabel: entity/enumeration typed `number`.**
  - eval_094 — answer IS the entity "NSSF"; the only numeral (`mbili`="both") is incidental.
    *Candidate one-line gold relabel* `number`→`definition` (would let vocab-overlap score it) —
    but that is a DATA-correctness decision, held to the same verify-and-review standard as every
    other gold change this session, NOT bundled into the scorer fix.
  - eval_074 — answer is "at least two", but the model conveys the count by ENUMERATING BRELA+TIN;
    needs enumeration understanding → semantic.
- **Sub-pattern 3 — terse-but-correct def/proc defeated by surface mismatch. NOT a narrow fix.**
  - 3a punctuation glued to tokens (`(input`, `refund).`, `pembejeo.`) — eval_029. The "obvious"
    fix (strip punctuation off tokens) was SIMULATED across the 400 and **flips 19 verdicts, all
    loosening, direction-indeterminate without per-case review** — exactly the "trade one failure
    mode for another" trap this session already learned to reject (embedding/NLI router). eval_029
    resolves at item 5 as part of an adjudicated batch, not via a blanket patch.
  - 3b synonym substitution (`jedwali`≈`orodha`) + gold padded with proper nouns a good answer need
    not echo (PKF, VELMA, TanzLII) — eval_131. Inherently semantic.
- **Sub-pattern 4 — "no fixed figure applies" (qualitative number).** eval_134/217 — **subsumed by
  the sub-pattern 1 fix** (once the junk key is gone, the existing BUG-1 exclusion fires).
- **Sub-pattern 5 — number answer mislabeled `definition`.** eval_233 ("10 employees" threshold typed
  `definition`; model states the correct `10`, but def-scoring ignores numbers AND bare 2-digit `10`
  is not captured by `extract_numbers` anyway). Relabel insufficient; 2-digit bare capture too risky
  globally → item 5.
- **Sub-pattern 6 — negative-question polarity trap (affirming a negative).** eval_390: gold "Ndiyo,
  haitozwi" vs model "Hapana… hazitozwi VAT" — substantive clauses AGREE ("hazitozwi"), only the
  leading polarity word inverts under negative framing. The documented flat-lexicon gap → semantic/NLI.

**Item-5 adjudication worklist compiled here** (structured input for the integration design):
| lead | sub-pattern | disposition |
|------|-------------|-------------|
| eval_094 | 2 entity-mislabel | candidate gold relabel (verify separately) OR judge |
| eval_074 | 2 enumeration-count | judge (list satisfies "at least two") |
| eval_029 | 3a punct + the **19 punctuation-strip flip candidates** | judge-adjudicate each; NO blanket patch |
| eval_131 | 3b synonym + proper-noun padding | judge |
| eval_233 | 5 number-as-definition | judge (relabel insufficient) |
| eval_390 | 6 negative-polarity trap | judge/NLI (content agrees, polarity word inverts) |

**Scope note.** Legacy `scripts/run_eval.py` and `scripts/build_eval_notebook.py` carry their own
divergent `extract_numbers` (missing even the `'000'`/BUG-7 fixes) — NOT the shared scorer the
400-gate runs, so left untouched. Flagged, not fixed here.

### Work item 4 — judge non-determinism: DATA-GATHERING DONE (2026-07-25); N=5 majority-vote proposed, integration deferred to item 5

**Root causes characterized** (why qwen3-32b flips verdicts even at temp=0 on `judge_regression.py`):
no seed, no provider pin (OpenRouter routes to different backend providers between calls), temp=0
not truly deterministic under batched GPU serving, and a fragile JSON/substring parse fallback.

**Option A (pin `seed=42` + single provider DeepInfra, `allow_fallbacks:false`) — tested at two scales:**
- **14-example STAGE-1 audit set** (`scratch/judge_determinism_optionA*.py/.json`): baseline flip_rate
  4/14, truth-match 13/14; pinned flip_rate **1/14** (75% reduction), truth-match 13/14, 0 false-
  demotes/promotes. The one residual (eval_026) was benign (correct↔undetermined only).
- **39 census disagreement IDs** (`scratch/judge_determinism_scale39.py/.json`, N=6 pinned,
  DeepInfra served all 234 calls, seed=42 — run COMPLETED before a PowerShell crash; result file
  is whole and was recovered, no re-run/duplicate spend): flip_rate **7/39 (18%)**, and crucially
  **2 correct↔wrong (DANGEROUS) flips appear at scale** (eval_228, eval_230) that the 14-set did not
  show. This is the session's recurring "clean at small N, fails at scale" pattern — **pinning
  reduces but does NOT eliminate the safety-relevant flip.**

**Subsample sufficiency proof (all 39 IDs, ref = majority-of-6):** every unstable case is a **5-1
split** (7 unstable all 5-1; other 32 unanimous 6-0). Simulating all C(6,3)=20 and C(6,5)=6
subsamples per ID: **0/780 three-draw and 0/234 five-draw subsamples disagree with the majority-of-6**
— including both dangerous IDs (0/20 each at N=3). Structurally, a 5-1 split *cannot* flip majority-of-3
(minority appears once, needs ≥2 to win). **So majority-of-3 is provably sufficient on all observed
data** — not luck.

**Why N=5 is proposed anyway (final design recommendation):** majority-of-3's safety is *contingent
on instability never exceeding 5-1*. The failure boundary is a **4-2 split**: at N=3 the minority wins
**4/20 = 20%** of subsamples (majority-of-3 flips); at N=5 it is **0%** (2 can't reach 3-of-5). No 4-2
case appeared across 39×6 draws, but that is a thin basis to assert 4-2 never occurs in the full 400.
**Majority-of-5** costs ~1.67× N=3 (~3¢/run at this scale), is robust to both 5-1 AND 4-2, and its only
failure mode — a genuine **3-3** tie — is an honest judge coin-flip that should resolve to
`undetermined` (a clean hook for item-5 integration), not silently pass/fail. Per the session's
no-extrapolation discipline, spend the extra two draws.

**Nature of the 2 dangerous flips (diagnosed — NOT a numeral misread → majority-vote IS the right fix,
no narrower cause to target):**
- **eval_228** (stamp duty on MoA, `brela_registration`): gold is itself a **hedge** ("commonly cited
  TZS 10,000 but not confirmed — confirm TRA"); model gave a **pure refusal** ("outside my knowledge,
  confirm TRA"). The 5-1 (majority=wrong) is the genuine question of whether a refusal *satisfies* a
  hedge-gold or *under-answers* it (dropped the "10,000 commonly cited" surfacing). Census single-shot
  drew the 1/6 "correct" outlier — direct evidence the single-shot census verdict is itself exposed.
- **eval_230** (PAYE personal relief, `paye_compliance`): model gets **core polarity right** ("no
  separate personal relief" — matches gold) but the elaboration is muddled; 5-1 majority=correct, the
  1/6 outlier penalizes the muddle.
- Both are legitimate borderline judgments on qualitative/refusal answers vs non-clean-numeric golds —
  real epistemic borderline-ness, exactly what majority-voting is for. No systematic misread pattern.

**Status:** the DATA-GATHERING half of item 4 is COMPLETE and conclusive. The remaining half — wiring
pinned-provider + majority-of-5 (with 3-3→undetermined) into `judge_regression.py` and the item-5
scorer integration — is deferred to **item 5** (integration design), where the judge becomes a
confirmation layer. No code wired this turn; `judge_regression.py`/`scoring.py` unchanged.

### 🚑 NEW DEFECT surfaced by the census — NSSF employee-deduction is a rules-engine error (NOT scoring, NOT #3)

**Highest-stakes finding, root-caused precisely — do NOT file this under the scorer work.** Four
false-passes (eval_091 gate, eval_274/282/330 additions; plus compute-derived instances) show the
system reporting **double the correct NSSF deduction**. Investigated to ground:

- **It is a rules-engine answer-*selection* error, not a rate-knowledge error and not flat-20% belief.**
  All are **compute-routed**; the figures come from `chike/rules_engine/nssf.py::compute_nssf`, which sets
  `amount = gross × (employer_rate + employee_rate)` = the **20% both-parties total**. The rates are
  correct (`NSSF_EMPLOYER_RATE=NSSF_EMPLOYEE_RATE=0.10`) and the engine explicitly decomposes and prints
  the correct halves ("mwajiri 80,000 + mfanyakazi 80,000"). But all four questions asked *"kiasi gani
  kinakatwa mshahara **wake**"* / *"NSSF **anayokatwa**"* — **how much is deducted from the employee** —
  whose correct answer is the employee's 10% half (80,000 / 75,000 / 64,000 / 45,000, confirmed by every
  gold: *"NSSF ya mfanyakazi ni asilimia 10"*). The engine **computes the correct employee figure but
  returns `total` as the headline `amount`**, so a user asking "how much NSSF comes off my 800k salary?"
  is told **160,000 when the answer is 80,000**. Returning `total` is correct for a "total remittance /
  how much do I as employer pay" framing — the bug is that the engine has **no notion of the question
  sub-framing** (employee deduction vs employer share vs total) and always returns the total.
- **Systematic & deterministic** (engine logic, not sampling) — hits *every* employee-deduction-framed
  NSSF compute, not just these four. **User-facing** (doubles stated payroll deduction), currently
  **hidden by scorer leniency** → higher priority than any scorer fix.
- **Compounded by an independent scorer-leniency bug** (the known number-overlap class): the regex marked
  these PASS because the correct 80,000 appears as an incidental sub-component in the working string.
  Fixing one does **not** fix the other.
- **NOT in scope for follow-up #3** (which is about the scorer). Tracked as its own defect below.

**Separately — eval_259 is a DIFFERENT genuine content error** (not the NSSF pattern): the engine computed
**WCF as 0.5% of vehicle value** (TZS 40M → 200,000) instead of 0.5% of payroll — it took the trap
question's irrelevant figure as the base. Also false-passed (definition-vocabulary overlap). Distinct
root cause.

### NEW TRACKED DEFECTS (rules-engine / scorer — separate from follow-up #3's five items)
- **D-NSSF-1 (user-facing, HIGH): ✅ FIXED (2026-07-25).** `compute_nssf` returned the 20% total as
  `amount` even when the question asked for a single party's share. Scope was **broader than the 4 the
  judge flagged** — the full-400 sweep found **12 single-party questions** (8 employee: eval_091/241/248/
  274/282/296/330/386; 4 employer: eval_090/092/243/289) all wrong-headlined, plus the ~total questions
  that were already correct. Fix (3 parts): (1) `routing.nssf_party(text) → employee|employer|total`,
  pure-lexical with **precise total cues (never bare `jumla`)** so the gross-salary phrase "mshahara wa
  jumla" (eval_090) does not misroute to total, and employer precedence over the incidental "mfanyakazi";
  (2) `compute_nssf(party=…)` selects the headline `amount`/`working`, keeping the 10/10 breakdown for
  transparency — `party='total'` string is **byte-identical to pre-fix**; (3) narrow levy-gated wiring in
  `orchestrator._answer_compute`. **Validation:** 36 routing+engine unit tests (all 12 cases + the two
  traps + total byte-identity); full-400 deterministic sweep = **0 party mismatches, 0 total-working
  diffs**; **full suite 221 passed**. Known-harmless edge: eval_095 (self-employed voluntary, gold 20%)
  detects `employee` but has no salary → clarifies before compute, so party never applies (documented, not
  a regression). **Gate-number caveat holds** — several of the 12 already showed `pass=True` via number-
  overlap masking, so the fix corrects the *advice*, not necessarily the gate integer; confirmation folds
  into the next full 400-run.
- **D-WCF-1 (content, MED): ✅ FIXED (2026-07-25).** WCF was computed on a non-payroll base (vehicle
  value) for eval_259 (*"Magari yangu ya biashara yana thamani ya TZS 40,000,000 … WCF yake?"*) because
  `swahili_numbers._WRONG_BASE` caught `mtaji`/`mapato`/`hisa` but had **no asset/vehicle-value pattern**,
  so the 40M was read as gross payroll. `compute_wcf` itself was correct — this was an **extraction**
  wrong-base gap. Fix: added `thamani ya magari|gari|mali|vifaa|mtambo` + the general `thamani ya \w+`
  prefix to `_WRONG_BASE`. **Validation:** eval_259 now `detect_wrong_base=True` → clarifies (matches
  gold); full-400 sweep of the new pattern = 4 matches, and **0 regressions** — eval_259 is the target;
  eval_256 was *already* caught by the existing `hisa` pattern (unchanged); eval_051 (EFD threshold fact)
  and eval_197 (stamp-duty refusal) are fact/refusal-path so they never invoke `detect_wrong_base`
  (call site is extraction.py:246, compute-path only). New unit test + full suite **222 passed**. A
  legitimate payroll figure is phrased "mshahara wa"/"analipwa", never "thamani ya", so no payroll
  question regresses to an unnecessary clarification.
- **D-WCF-2 (content, MED; one HIGH sub-case): ✅ FIXED (2026-07-25, commit `fd150d1`).** Direct extension of
  D-WCF-1: `_WRONG_BASE` caught asset-value bases (`thamani ya X`) but not **market value, rent, savings,
  utility cost, bank loan, or business cash flow** offered as a payroll base for SDL/NSSF/WCF/PAYE. Full-400
  sweep found **6 cases (2 beyond the 4 flagged): eval_253** (deni la benki), **254** (bei ya soko — the HIGH
  one, was mis-computing `WCF = 0.5% × 25,000,000 = 125,000`), **255** (mzunguko wa fedha/cash flow), **258**
  (kodi ya pango), **260** (akiba), **261** (gharama za umeme). 8 new terms, precision-scoped:
  `gharama za umeme`/`maji` (not broad `gharama za \w+` → would hit `gharama za mishahara`); `\bdeni\b` word
  boundary (catches `deni la benki`, not `madeni`). **Validation:** new unit test (6 caught + exclusions);
  full-400 no-regression sweep **on the real call path** (detect_wrong_base is invoked only from the compute
  path via `extraction.py:246`) = **delta exactly the 6 targets, 0 unexpected, 0 legit-payroll caught**.
  eval_218 confirmed unaffected (intent `none`/fact path, never calls detect_wrong_base — the initial sweep
  phantom-counted it off-path). **Gate caveat:** 5 of 6 already `pass=False`; the fix corrects the advice /
  kills the wrong number, folds into the held eval.py run.
- **D-WCF-3 (content, MED — TRACKED, NOT fixed): the inverse problem.** eval_324 (*"…mishahara TZS 4,800,000
  kwa watu 13, na madeni TZS 2,000,000, na faida TZS 1,000,000 — SDL?"*) states a **legit payroll base**
  (gold wants SDL = 3.5% × 4,800,000 = 168,000) but a distractor `faida`/`madeni` figure fires `_WRONG_BASE`,
  so it clarifies instead of computing. This is **not** a term-addition problem (D-WCF-1/2's shape) — it needs
  logic to suppress the wrong-base veto when an explicit `mishahara/analipwa TZS <amount>` payroll figure is
  present alongside the distractor. Its own investigation; queued, do not fold into D-WCF-2.
- **D-DECOMP-1 (completeness, MED; one HIGH false-pass): ✅ FIXED (2026-07-25, commit `4c7d5e5`).** A compute
  part naming **several levies** ("...SDL na NSSF...", "SDL, NSSF, PAYE na WCF") routed to only the first
  (`_explicit_levy` returns the first match), **silently dropping the rest**. eval_318 was a `pass=True`
  false-pass concealing a dropped NSSF. Fix: `routing.all_explicit_levies(text)` + `orchestrator.
  _fan_out_multi_levy()` expand a multi-levy compute part into one compute per named levy (shared text, own
  extraction + engine). **Full-400 structural sweep:** exactly **6 fan out** (eval_318/319/320/321/323/327,
  measured not assumed); the other **394 are byte-identical at object identity** (`fanned[i] is routed[i]`),
  so single-levy output is provably unchanged. **Phase B invariant re-verified** (fan-out only adds to
  `compute_parts`, never folds into the pooled fact gen) — both existing guards
  (`test_mixed_compute_and_fact_keeps_two_distinct_sources`, `test_multi_compute_parts_are_not_collapsed`)
  re-run and pass. 3 new tests; **full suite 235 passed**. Fixes eval_318 fully; advances 320/321.
  - **Per-person / tiered / conditional aggregation (eval_319/327/323) — SEPARATE follow-on, tracked:** the
    fan-out now computes each named levy, but these three carry a compounding need the fan-out does NOT solve —
    per-person aggregation ("14 × 500,000"), tiered payroll ("4×700k + 6×300k"), conditional headcount ("if I
    add 9 to reach 10"). They now surface that need per-levy instead of silently dropping a levy. Own item.
  - **eval_326 (D-DECOMP-2 — two-employee mixed-residency split): deferred.** "Mfanyakazi ni mkazi analipwa X
    na mwenzake si mkazi analipwa Y — PAYE ya kila mmoja?" No decompose signal fires; it's one PAYE compute
    over two salaries → per-person ambiguity → **safe clarify**. Fixing needs splitting by employee AND applying
    residency per split (intersects D-PAYE-1). Rare (1/400), currently safe (not a wrong number). Queued.
- **D-PAYE-1 (user-facing, HIGH): ✅ FIXED (2026-07-25, commit `0785c7a`).** Same class as D-NSSF-1 —
  the engine already implements the flat-15% non-resident branch (`compute_paye(resident=False)`) but
  nothing upstream ever determined residency, so **every** PAYE compute defaulted to progressive resident
  bands. eval_367 (*"Mfanyakazi asiye mkazi analipwa TZS 5,000,000 … PAYE yake?"*) returned **1,328,000**
  (progressive) instead of the correct **750,000** (15% flat, = gold). Fix: `routing.paye_resident(text)
  → bool`, negated-residency cues (`asiye mkazi`/`si mkazi`/`wasio wakazi`/`non-resident`), **guarded
  against the mixed two-person case** (eval_326: one resident + one non-resident — a scalar flag can't
  express both, so the precise `ni mkazi` cue keeps it resident-default and defers to the decompose/merge
  item); narrow levy-gated wiring in `orchestrator._answer_compute`. **Validation:** full-27 PAYE-compute
  sweep = **25/27 byte-identical** (resident=True, unchanged working), exactly 2 flip (eval_344/367);
  eval_218/392 are `compute=False` so `paye_resident` is never invoked (untouched); 9 new unit tests;
  **full suite 231 passed.** One over-broad cue caught in testing (`mkazi analipwa` matched inside `asiye
  mkazi analipwa`, reverting eval_367 to resident) and narrowed to `ni mkazi` before shipping. **Gate-
  number caveat holds** — offline fix, confirmation folds into the next 400-run.
  - **eval_344 (false-premise yes_no, no amount): ✅ CONFIRMED ALREADY-FIXED (2026-07-25).** When D-PAYE-1
    reasoned this "routes to clarification," it was reading the **5239190 baseline output** — but that
    baseline (2026-07-23) **predates the money-ask guard** (`5d806c6`, 2026-07-24). `git merge-base` confirms
    the guard is not an ancestor of the baseline. Current `detect_intent` routes eval_344 (and its 4 siblings
    eval_099/335/337/342 — the true blast radius of the rate/mechanism-confirmation-yes_no-naming-a-compute-
    levy pattern) to `'none'` (fact/RAG); `tests/test_routing.py:188-243` already lock all of them (15/15
    pass). **No fix needed** — the answer-correctness (does fact/RAG actually refute the false rate) folds
    into the held eval.py run. Lesson: baseline outputs are pre-fix snapshots; always re-test current
    `detect_intent`, don't infer routing from the pinned baseline.
  - **eval_311 (applicability-detector gap, LOWER priority — tracked, queued after decompose/merge):**
    *"Nina mfanyakazi mmoja tu anayelipwa TZS 500,000, je bado nachangia WCF?"* routes to compute `wcf`
    but `is_applicability_question` does not catch "bado nachangia", so it doesn't get the clean
    applicability "Ndiyo — WCF kutoka mfanyakazi wa kwanza" answer. Lower severity than a wrong-number bug
    (a **missed correct answer**, not a confidently-wrong one). Fix later by extending the applicability cue
    set; do NOT fix now.
  - **eval_326 (→ decompose/merge, with eval_318):** two employees of differing residency in one question;
    deferred, guarded to resident-default so the resident half is not wrongly billed 15%.
  - **eval_218 / eval_392 (→ fact/RAG queue):** both `compute=False`. eval_218 is non-resident **rental**
    withholding (a different tax entirely); eval_392 is a yes_no answered wrongly on the fact/generate path
    (needs the non-resident flat-15% fact retrievable). Neither is a compute-wiring bug.
- **D-VATWH-1 (fact-base, HIGH): ✅ RESOLVED (2026-07-25).** The VAT-withholding **base** was internally
  contradictory across the fact base (work item 4): three "CONFIRMED" facts encoded a **VAT-amount** base
  (3%/6% × VAT), while `VAT_withholding_base_disputed` said the base was unresolved and the eval golds
  (eval_034/315) used the **consideration** base — so eval_034/315 were stuck permanently "ambiguous" and
  any future VAT-withholding work risked building on the wrong side. **Resolved by PRIMARY legislation**
  (not practitioner summaries): **Finance Act 2025 (Act No. 11) s.124** inserts VAT Act Cap.148 **s.5(5)** —
  the 18% standard rate is split, the withholding agent withholds **3% (goods) / 6% (services) of the
  supply** and the supplier receives **15% / 12%** respectively (3+15 = 6+12 = 18). The statute's express
  **12% supplier share for services** is decisive: it is impossible under a VAT-amount reading (which would
  leave the supplier ~94% of the VAT). Corroborated by **GN 352K of 30/6/2025** reg 31B + the withholding
  certificate form (signed Minister for Finance, 29 Jun 2025). Both TRA-hosted PDFs were fetched and text-
  extracted locally. **Verdict: consideration base is correct; the eval golds were right all along; the
  model + `vat_withholding_formula_correct` were wrong.** Corrected 5 fact entries (`vat_withholding_goods`,
  `vat_withholding_services`, `vat_withholding_formula_correct`, `VAT_withholding_base_disputed` →
  RESOLVED, `vat_withholding_buyer_remits_directly`), un-inverting `wrong_patterns` that were flagging the
  now-correct consideration answers and adding the VAT-amount error as the new wrong pattern (verified:
  golds not flagged, model errors caught). **No training pairs asserted the wrong formula** — the one
  matching cleaned pair (batch_015) is a *hedge* ("base varies by source, confirm TRA"), now improvable to
  the confirmed formula (optional follow-on). **Two bonus findings** from the primary text: (1) the
  **effective-date** discrepancy is explained — VAT withholding is **1 Jul 2025** (fact base correct); the
  "1 Sep 2025" some secondary sources cite is the *separate* 16% B2C e-payment rate in **s.5(6)**, not the
  withholding. (2) `vat_withholding_certificate_timing` and `vat_withholding_buyer_remits_directly` were
  **already correct** — confirmed by s.90B ("certificate not later than the day VAT becomes payable under
  s.15") and the s.71 amendment (supplier subtracts withheld output tax only with a valid certificate).
  **D-VATWH-1 RAG regeneration ✅ DONE + DEPLOYED (2026-07-25, index commit `afba3a2`).** R15 ran on Kaggle,
  the e5 index was fetched from HF (`prospAprospA007/africa-giants-dataset`), committed byte-identical to BOTH
  `chike-inference/` and `kaggle/` (sha256 verified matching), and **Modal was redeployed** — the corrected
  consideration-base VAT-withholding facts are now live in production. Index is 213 facts (was 211).
  **Remaining:** the `kaggle/eval.py` gate confirmation is intentionally HELD for ONE comprehensive run after
  all of follow-up #3 is complete (not per-change), so gate-number confirmation folds into that single run.
- **D-MODELRAG-A (fact-base GAPs, MED — item (3) Group A): ✅ FACTS ADDED (2026-07-25), RAG regen PENDING.**
  Of the 8 confirmed model/RAG factual-error cases, the 4 traced to a **missing fact** were investigated;
  primary-source verification + two new locked facts drafted and added:
  - **`brela_business_structures`** (eval_071 + eval_304): the model answered "how many business structures"
    with IP categories (it retrieved the adjacent `BRELA COSOTA split` IP fact), and fabricated "register a
    company if 10+ employees". New fact enumerates the 3 legal forms (sole proprietor + partnership = business
    name under Business Names (Registration) Act Cap.213; company under Companies Act Cap.212) and states the
    choice is independent of headcount/capital, distinguishing IP. Verified against the BRELA-hosted Acts
    (Cap.213 s.2 definition; Cap.212) + brela.go.tz.
  - **`wcf_paid_to_fund_not_tra`** (eval_123): the model said WCF is paid to TRA. New fact: WCF paid directly
    to the Fund via portal.wcf.go.tz, NOT TRA (SDL -> TRA); employee does not contribute. Verified against
    wcf.go.tz/pages/contribution + Workers Compensation Act No.20 of 2008.
    **Validation:** both facts' `wrong_patterns` run against all 400 gold + 400 model answers — 0 gold or
    correct-answer false-flags; the only model hit is eval_304's own wrong answer (guard working as intended).
    Patterns kept conservative (they don't try to catch the eval_071/123 model outputs — the corrective
    mechanism is RAG surfacing the new facts after R15, not the training-guard regex). **RAG regeneration
    ✅ DONE + DEPLOYED (index commit `afba3a2`)** — the single R15 run covered D-VATWH-1's 5 corrected facts +
    these 2 new facts (BRELA/WCF) + the concise-EFD embedding fix (Group B, eval_347) = 8 fact changes; index
    now 213 facts, committed byte-identical to both dirs and live on Modal. `kaggle/eval.py` gate confirmation
    HELD for the single comprehensive run after all of follow-up #3.
  - **eval_223 (EAC STR) — EXCLUDED from the active defect/gate queue:** *out of active scope — Tier 1B
    (EAC/STR) not yet started per CLAUDE.md §5, deferred until Tier 1A gate passes and Tier 1B unlocks.* No
    STR fact verified or drafted; pulling Tier 1B content forward to pass one eval question would be working
    backward from a test case rather than respecting the project's tier-staging plan.
  - **Group B (eval_162 mgeni, eval_347 EFD) — probed on Kaggle, split confirmed:**
    - **eval_162 — HALLUCINATION, CLOSED:** the v2 two-arm probe (`kaggle/retrieval_probe_group_b_v2.py`)
      showed the target fact IS recovered (in the top-3 the model saw); the model fabricated the
      citizen-becomes-mgeni criteria anyway. Not fixable at fact-base/retrieval — feeds semantic scoring
      (item 5), like Group C.
    - **eval_347 — RETRIEVAL gap, FIX APPLIED (pending R15):** `efd_threshold_tzs_11m` was English-only
      (`key:value` fallback) while the hijacking competitor `vat_registration_threshold_annual` is a concise
      Swahili fact of the same 200M magnitude and near-identical "Kizingiti cha … mauzo ya" phrasing. v2
      detail: the number-stripped arm DID surface the EFD fact, but only at **s#2** — it lost the single
      append-only promotion slot to `efd_approved_supplier_verification` (s#1) **by one rank**. Fix: a concise
      Swahili-first `CONCISE_BILINGUAL_FACTS['efd_threshold_tzs_11m']` entry (value at front, distinctive
      'kuanza kutumia EFD' tokens, explicit "200M = VAT-registration, si EFD" contrast for eval_347's false
      premise) — same figure, no new claim, same precedent as `gn487a_prohibited_activity_3`/
      `gn487a_marriage_no_exemption`. Guarded by **two verification tuples** in `regenerate_rag_e5.py` (EFD
      query → 11M; VAT-reg query → 200M anti-displacement bracket). Narrow the 200M contrast if the regen gate
      flags displacement (GN487A narrowing precedent). **✅ DEPLOYED in the R15 batch (index commit `afba3a2`);
      the fetched index carries the concise EFD fact AND the VAT-reg fact (displacement sanity passed on
      presence; ranking to be confirmed in the held eval.py run).** Broader idea noted
      but OUT OF SCOPE: the "promote only the first new fact" append rule cost the EFD fact its slot by one
      rank — worth revisiting the merge rule separately, not in this fix.
  - **Group C (eval_047, eval_210) — NO fix (correct):** correct fact exists, indexed, effectively surfaced;
    model appended false detail anyway. Not fixable by fact-base/retrieval — feeds semantic scoring (item 5).
- **D-SCORER-1 (scorer leniency, MED — feeds work item 5):** number-overlap credits a PASS off an
  incidental correct sub-figure while the headline answer is wrong (the NSSF cluster + others among the
  27 false-pass candidates). Adjudicate the 27 list; this is the concrete evidence for the judge-as-
  confirmation-layer integration.

**CAVEAT preserved (also embedded in the artifact JSON):** the judge is **not** ground truth (work item 2).
A judge-vs-regex disagreement is a **candidate** to adjudicate, not an automatic correction; STAGE 1 was
10/14, so a fraction of the 27/12 will be judge errors. The NSSF cluster, however, is unambiguous on
direct inspection of the engine + golds.

**Work-item status:** 1 (census) DONE, 2 (adjudication → 39-candidate confusion matrix) DONE, 3
(procedure over-strictness) DONE, **4 (non-determinism) DATA-GATHERING DONE** (pinned + majority-of-5
proposed; wiring deferred to 5). **Item 5 (integration design) NOT started** — this is now the single
remaining work item: wire pinned-provider + majority-of-5 judge (3-3→undetermined) as a CONFIRMATION
layer over `reliable=False` into `scoring.py`/the gate, using the adjudicated disagreement list.

### Router-investigation follow-up tracker (3 items) — ✅ CYCLE CLOSED (2026-07-26)
**All three follow-ups done; comprehensive confirmation run `afef9dd` closes the entire router-investigation
/ defect-fix cycle (see the 🏁 CLOSE-OUT entry above).** Only work item 2 (real adjudicated ground truth,
founder-gated) remains open, with its fresh 25+7 disagreement queue as input.
- **#1 — generic explicit-levy money-ask guard: ✅ DONE** (commit `5d806c6`).
- **#2 — ordinal-enumeration decomposition (`_split_ordinal_enumeration`): ✅ DONE** (commit `d86b92e`).
- **#3 — frontier-judge / semantic scoring: ✅ DONE** — work item 1 (scale to 400 census) DONE
  (2026-07-25); work item 2 (adjudicate the 39-candidate disagreement list → confusion matrix, judge
  92.9% accurate on 28 clean cases) DONE (2026-07-25); work item 3 (procedure over-strictness) DONE
  (2026-07-25); **work item 4 (non-determinism) DATA-GATHERING DONE (2026-07-25)** — pinned + majority-of-5
  proposed (subsample proof: 0/780 flips at N=3 across 39 IDs, but N=5 chosen for 4-2 robustness), wiring
  deferred to item 5; **work item 5 (judge→scoring integration) BUILT (2026-07-26)** — `chike/judge.py`
  (pinned + majority-of-5 + confirmation-overlay aggregation) wired into `eval_orchestrator_combined.py`
  as a report-alongside overlay + `scripts/judge_augmented_local.py` local twin; `scoring.py`/`GATE PASSED`
  unchanged; 15 new tests, `tests/` 257 passed. From the adjudication defect queue: D-PAYE-1 FIXED,
  D-VATWH-1 (VAT-withholding base) RESOLVED by primary law. **All 5 work items of #3 built and CONFIRMED at
  scale** by the comprehensive `afef9dd` run (2026-07-26): reliable buckets +5.8 to +7.6 pts across all
  touched clusters, judge-augmented (76.4%) reconfirms reliable-denom (77.0%) a second time, zero engine-
  introduced prohibition inversions. Work item 2 (real adjudicated ground truth) is the only open piece —
  the prerequisite before promoting the judge-augmented number to the live gate; its input is now the fresh
  25+7 disagreement queue. Also surfaced a
  STRUCTURAL GATE FINDING (eval.py never applied `scorer_reliability`; see top headline). NEW defects
  D-NSSF-1 / D-WCF-1 / D-PAYE-1 / D-VATWH-1 / D-SCORER-1 (tracked above, separate from #3).

## ✅ Generic explicit-levy money-ask guard — SHIPPED (2026-07-24) — router follow-up #1 of 3

**The first of the three tracked follow-ups from the Phase D router investigation (the
applicability-vs-amount fix `f200a4e` and the natural-path money-ask guard were the earlier two
guards this mirrors).** `chike/routing.py`'s explicit path committed to compute on nothing more
than *a levy name + any digit* (`if explicit and _has_number(ql): return explicit`) — no
money-ask/obligation-cue guard, unlike the natural path (requires `_has_money_ask`) and
`is_applicability_question` (rejects when `_has_money_ask`). So a yes_no/definition/deadline
question that merely NAMES SDL/NSSF/PAYE/WCF and carries an **incidental** number (a rate
'asilimia 3.5', a day 'siku 30'/'tarehe 20', a threshold headcount 'wafanyakazi 4, sivyo?') was
routed to compute and then emitted a needless "give me the salary" clarification instead of just
answering from fact/RAG.

### Fix mechanism (routing-layer only; no model/network/GPU)
Guard Path 1 so it commits to compute only when a computation is actually needed —
`_has_money_ask OR is_applicability_question OR _has_money_magnitude OR _COUNT_TRANSITION OR
_DERIVE_CUE`. The discriminator is a **payroll money magnitude**: `_has_money_magnitude` returns
True for a currency/magnitude token (TZS/shilingi/milioni/elfu/laki/dola/euro/kes) **or** a
parsed amount ≥ `swahili_numbers.MIN_PLAUSIBLE_AMOUNT` (the extraction layer's own payroll-
plausibility floor, so a bare large number like `6,750,000` counts while a rate/day/small-count
does not — keeping routing consistent with how extraction itself decides a figure is real
payroll). A rate/deadline/confirmation whose only number is incidental now falls through to
fact/RAG.

**Empirical necessity of the money-magnitude refinement:** the naive "money-ask OR
applicability" guard was measured **unsafe** — it flips 51 questions and hijacks **6
currently-passing** ones (incl. `eval_318`, an unambiguous genuine compute question). Adding the
money-magnitude keep-condition narrows the blast radius to the intended class only.

### The 12-question flip set (all → fact/RAG; all `pass=False` today, so no reliable-subset loss)
`eval_099, eval_102, eval_127, eval_335, eval_342, eval_343, eval_344, eval_345` (the eight
originally-named) **plus** `eval_095, eval_337, eval_341, eval_348` (four same-class rate/
threshold confirmations surfaced by the 400 sweep). Exactly these 12 flip; every flip goes to
`none`; **0 currently-passing questions affected**; the 35 genuine compute questions the naive
guard would have wrongly hijacked (elliptical asks like `eval_372` "mishahara TZS 1,500,000 →
SDL yake?") are preserved.

### Carve-outs — deliberately NOT flipped (belong to other, already-built mechanisms)
- **`eval_124`** — the count-transition never-guess case (`_COUNT_TRANSITION`, from the
  applicability fix `f200a4e`). Kept on the compute path so its own never-guess clarification
  (not a fact answer) still fires when the headcount is crossing the SDL threshold. Flipping it
  would undo that just-built fix.
- **`eval_263 / eval_265 / eval_266`** — wrong-base traps (`extraction:small_int_as_money`;
  invoice/branch/vehicle counts offered as a payroll base). Their **gold answers themselves ask
  for the payroll figure** ("Nipe mshahara wa mwezi, siyo idadi ya invoice"), so the current
  salary-clarification is already aligned with intent; flipping them to fact/RAG would reintroduce
  exactly the fabricate-on-wrong-base failure the `rc_22`/`eval_380`-class guards exist to prevent.
  A compute-derivation cue (`_DERIVE_CUE`: itakuwaje/naipataje/inahesabiwa…) keeps them on the
  compute path, where extraction clarifies safely (never-guess, R8). These stay on the separately-
  tracked wrong-base track, not blurred into this guard.

### Validation
- New unit tests A1–A5 in `tests/test_routing.py` (named-8 → fact; the four additional → fact;
  genuine-compute regression locks stay on levy; `_has_money_magnitude` truth table; carve-out
  assertions). Routing tests 18 → 23.
- Full 400 routing sweep (offline, `scratch/explicit_guard_final_sweep.py`): exactly the 12-flip
  set, all → `none`, 0 currently-passing hijacked, 4 carve-outs stay compute.
- **Full offline suite: 204 passed, 0 failed.**

### Gate-number caveat (understood and correct)
This is a **routing-quality** fix, not something that moves the reliable-subset number on its own:
all 12 flipped questions are `pass=False` today, and production `run()` has no compute path.
Confirmation that the 12 now answer correctly via fact/RAG (rather than clarifying) is **folded
into the next scheduled 400-run** — no separate GPU cycle spent on it.

**Follow-up #2 of 3 — the `decompose_query` extension (enumerated/period-joined clauses, the
eval_322 / "Pia," gap above) — is next, and is HIGHER RISK: it touches shared infrastructure
affecting all 400 questions, so it needs its own careful, isolated investigation before any fix
is proposed (same discipline the applicability fix and this guard both received).**

## MEASUREMENT GAP — a THIRD of the gate is scored by an admittedly-arbitrary mechanism (2026-07-24) — ELEVATED

**This is a first-order measurement finding, not a caveat.** On the 5239190 combined run
(the current v16 baseline), **133 of 400 results (33.25%) are `reliable=False`** — the harness
itself declares them **unverifiable in either direction**. The weight is not "63 unverifiable
failures": it is that **70 of those 133 are marked PASS and 63 are marked FAIL, and the pass/fail
split across that entire third is arbitrary from the scorer's own standpoint.** A "pass" inside
that third is exactly as unadjudicated as a "fail." Every one of the eight exclusion reasons is a
scorer / ground-truth-structure limitation; **none** is a generation-quality reason (0 truncated /
loop / empty):

| reason | n | meaning |
|---|---|---|
| compute_derived_number | 48 | number-overlap cannot verify a *computed* figure |
| yes_no_polarity_unverifiable | 28 | cannot parse the Swahili yes/no lead |
| qualitative_number_no_numeric_key | 27 | answer is qualitative; no numeric key to match |
| yes_no_ground_truth_ambiguous | 9 | gold polarity itself ambiguous |
| morphological_overlap_gap | 7 | correct answer, tokenizer missed the overlap |
| year_only_numeric_key | 6 | scoring on a stray year token |
| zero_or_not_applicable_answer | 6 | "TZS 0 / not applicable" unverifiable by overlap |
| year_collision_match | 2 | spurious year-token match |

The reliable-subset gates (`fact_path_190_reliable`, etc.) exist *only* to route around this, and
they shrink the measurable base substantially (fact_path drops from n=180 to n=127). **This is
direct evidence that the frontier-judge scoring item is the binding constraint on trusting any
compute/adversarial number — and a third of the fact numbers too — and is NOT deferrable.**
(Supersedes the earlier "130/400" figure from the e9cc68a run; current is 133/400.)

### Copy-quality note (low priority, NOT a defect) — eval_275 / 291 / 292 (2026-07-24)
These three clarify **safely** (no fabricated number) but name a **generic** count/per-person need
instead of the *actual* blocker — foreign currency (eval_275, USD 300) or an irregular pay period
(eval_291 bi-weekly, eval_292 per-shift). `chike/clarification.py` already has `foreign_currency`
and `period` reason-mappers; the miss is that extraction did not surface those blockers into
`clarification_reasons` for these phrasings. Future copy-quality polish only — no code this session.

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
accuracy.** 130/400 results are reliable=False (this is the e9cc68a figure; the current
5239190 baseline is **133/400 = 33.25%** — see the dated "MEASUREMENT GAP" section near the
top for the elevated restatement), and every exclusion reason is a
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
0. **[ELEVATED 2026-07-24] Frontier-judge / semantic scoring — now the BINDING constraint.**
   The 5239190 investigation showed **133/400 (33.25%) are `reliable=False`** with an
   arbitrary pass/fail split (70 pass / 63 fail) across that third, every exclusion reason
   scorer-structural (see "MEASUREMENT GAP" section above). This is no longer a deferrable
   nicety: it caps the trustworthiness of every compute/adversarial number and a third of the
   fact numbers. Promoted above the two items below — they largely *fold into* this workstream.
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
