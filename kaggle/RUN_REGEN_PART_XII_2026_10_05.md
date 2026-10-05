# R15 REGEN PACKAGE — Part XII reversal + rent_wht_rate (2026-10-05)

Ships **three** corrections staged in the repo and not in the deployed index. This is the one
open item with **live user impact**: until it runs, production serves the reversed citation.

| fact key | change | class |
|---|---|---|
| `act_section_12` (row 101) | `Part XIII (ss.320-328)` → **`PART XII (ss.437-447)`** | wrong string |
| `brela_foreign_late_filing_penalty` (row 171) | `Part XIII, ss.320-328` → **`Part XII, ss.437-447`** | wrong string |
| `rent_wht_rate` | **NOT IN THE INDEX AT ALL** → ask-led `CONCISE_BILINGUAL_FACTS` entry | **absent row** |

`ext_31` (`OSHA_safety_officer_threshold`) was already staged and is carried forward by its
existing third payload gate — it ships in this run too.

---

## ⛔⛔ READ THIS BEFORE ANYTHING ELSE: `rag_fact_count` SEQUENCING

**The index goes 183 → 184 rows.** `kaggle/chike_config.json` carries `"rag_fact_count": 183`,
and `chike-inference/modal_app.py` asserts it against the loaded index and **refuses to serve on
a mismatch** — verified live on 2026-08-24 (HTTP 500, by design).

**`chike_config.json` is fetched from GitHub AT RUNTIME (R14).** So:

> **DO NOT bump `rag_fact_count` to 184 until the same commit that carries the fetched
> `rag_embeddings.npy` + `rag_facts_text.json`. Bumping it while production still holds the
> 183-row index TAKES PRODUCTION DOWN** — the fail-loud contract would do exactly what it is
> built to do, against a healthy index, because the count it was told to expect does not exist
> yet.

It is deliberately **not** bumped in this packaging commit. Step 4 below is where it changes.

---

## Local dry run — ALREADY DONE, and it says SAFE TO RUN

`eval/index_quality/dryrun_regen_2026_10_05.py` → `eval/results/dryrun_regen_2026_10_05.json`

```
prospective index                      184 rows
Part XII guard   (ext_15 verbatim)     RANK 1
rent WHT guard   (ext_44 verbatim)     RANK 1
new row self-retrieves                 True
displacement regressions CAUSED        0
pre-existing failures (also on deployed index)   4
VERDICT                                SAFE TO RUN
```

**This could be run locally, which contradicts a standing note in `regenerate_rag_e5.py`.** Its
header says the e5 weights "do not download on the local Tanzania connection" — true of
**downloading**, not of **loading**. `intfloat/multilingual-e5-base`, the exact model the regen
uses, is already in the local HF cache with complete `model.safetensors`; `HF_HUB_OFFLINE=1`
loads it without touching the network. (R30 applied to our own tooling: a connection property
had become a reason not to verify. The sibling `e5-base-v2` cache **is** incomplete, which is
probably where the belief came from, and it is not the model in use.)

### ⚠️ The baseline arm is why the verdict is SAFE and not DO-NOT-RUN

**The first dry run reported 4 displacement regressions and a DO-NOT-RUN verdict.** Adding a
baseline arm — the same 4 guards against the **currently deployed** 183-row index — showed all
four **already fail there**. They are pre-existing, not caused by this package. `regenerate_rag_e5.py`
already records this exact trap for `nat_37`/`nat_38`; without the arm, a good package would have
been abandoned on four failures it did not cause.

The four pre-existing failures are listed in the artifact and are **not** closed by this run:
*Phone repair activity*, *GN487A marriage no exemption*, *BRELA striking-off (Q13)*,
*OSHA/WCF small-count (Q14)*.

### Why displacement was the thing to measure

`precompute_rag_embeddings.py` holds **two VAT-withholding entries deliberately held back**
because a withholding-flavoured Swahili rewrite pulled `nat_27` (a correct standard-rate row) out
of its own top-3 — three phrasings tried, all three displaced it. `rent_wht_rate`'s new text is
withholding-flavoured too (*kodi ya zuio*, *mkate*, *asilimia 10*), so it sits in that
neighbourhood by construction. It measured clean; that is a measurement, not a presumption.

---

## The gates this package adds

**`EXPECTED_HEAD` bumped `d593d49` → `5e191e0`.** That is the PACKAGING commit -- the first containing all three
of the source fixes, the rent entry, **and the inverted payload gate** — see next.

### The payload gate had to be INVERTED, and this is the entry to remember

The 2026-09-24 gate asserted **`'part xiii' in row`** and refused to upload without it. **It
would have refused to build the corrected index**, demanding the wrong citation as its entry
price. It is the best-built control in the file — keyed not lexical, failing loudly on absence,
written against a real live defect, citing R20 and R21 in its own comment. **None of that helped,
because a control can only be as right as the fact it encodes.**

Two traps inside the inversion:
- **`'part xii'` is a substring of `'part xiii'`**, so the naive `in` form would have been
  vacuous — it passes on the stale text. The gate uses `re.search(r'part\s*xii\b(?!i)')`.
- the file had **no `import re`**. Without it the new gate would have `NameError`'d on Kaggle at
  build time.

### Four payload gates now, four distinct defect classes

| # | key | class |
|---|---|---|
| 1 | `brela_foreign_late_filing_penalty` | wrong string *(inverted today)* |
| 2 | `minimum_turnover_tax` | ambiguous gloss |
| 3 | `OSHA_safety_officer_threshold` | correct text, **never reached** |
| 4 | **`rent_wht_rate`** | **never in the index at all** |

Gate 4 asserts presence, ask-alignment, **both qualifiers** (no residency split; withholding-agent
only) and absence of an embedded citation. The two qualifiers *are* the defect the locked fact
exists to prevent, and the first is also the critical-query anchor — dropping it breaks both.

### Two new critical-query guards

```
Part XII foreign-company citation (ext_15 verbatim)   anchor: 'Part XII, ss.437-447'
Rent WHT 10% both parties        (ext_44 verbatim)   anchor: 'hakuna tofauti ya ukaazi kwenye pango'
```

**A retrieval guard and a payload gate fail differently and both are needed.** The payload gate
catches a row whose **text** reverted; the critical query catches a row that is textually right
but no longer **reached** by the question it answers. The 2026-09-05 live defect was the first
kind; `ext_31` was the second. **Neither gate can see the other's failure.**

**Anchor choice, and the near-miss worth recording:** `'ss.437-447'` matches **two** rows
(`act_section_12` and `brela_foreign_late_filing_penalty`), so a guard anchored on it could pass
on the wrong one. `'Part XII, ss.437-447'` — with the comma — is unique, and **it is the citation
under guard rather than a proxy for it.**

Both queries are **verbatim** gate rows. Not cosmetic: for `nat_36` a paraphrased guard phrasing
put its fact at rank 2 and the verbatim eval text at rank 17.

---

## Run it

```bash
# On Kaggle (GPU not required; e5-base is small)
!git clone https://github.com/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS.git
%cd AFRICA-GIANTS
!git log --oneline -1          # MUST contain 5e191e0 as an ancestor, or the script aborts
!python kaggle/regenerate_rag_e5.py
```

The script refuses to upload unless **every** fact self-retrieves at rank 1, **all** critical
queries hit top-3, all four payload gates pass, and the rank-regression gate passes. A
`[STALE-KNOWN-FAIL]` or an orphaned `KNOWN_FAILING` name also blocks.

Expect in the log:
```
[OK] payload gate: brela_foreign_late_filing_penalty carries Part XII, no "Part XIII"/ss.320-328
[OK] payload gate: no row in the built index carries the reversed Part XIII citation
[OK] payload gate: minimum_turnover_tax reworded, ambiguous gloss gone
[OK] payload gate: OSHA_safety_officer_threshold is ask-aligned, uncited, needle intact
[OK] payload gate: rent_wht_rate present, ask-led, both qualifiers intact, uncited
[PASS] Part XII foreign-company citation (ext_15 verbatim, the reversal guard)
[PASS] Rent WHT 10% both parties, no residency split (ext_44 verbatim, new fact)
```

## Then, in order (R15 steps 4–6)

1. Fetch `rag_embeddings.npy` + `rag_facts_text.json` from the HF dataset repo.
2. Commit them to **both** `chike-inference/` and `kaggle/` — **and in the same commit** bump
   `kaggle/chike_config.json` `rag_fact_count` **183 → 184**. Same commit, not before, not after.
3. Redeploy Modal **per R16** — `python -m modal app stop chike-inference --yes`, then deploy with
   `PYTHONIOENCODING=utf-8 PYTHONUTF8=1`. **"✓ App deployed" is not verification**; warm
   containers serve the old index.
4. **Live check that exercises this change specifically** — send `ext_15`'s verbatim question and
   confirm the reply cites **Part XII, ss.437-447** and not Part XIII. Then `ext_44`'s, and
   confirm the 10%/no-residency-split answer, which production has never been able to give.
5. **Negative case:** a normal SDL or PAYE question still answers correctly (the index grew by a
   row; nothing else should move).
6. Re-run the gate.

---

## Attempt 1 (2026-10-05) — BLOCKED BEFORE UPLOAD. Nothing shipped. Fixed; re-run.

Everything substantive passed. **184 facts, 0 self-retrieval failures, all 36 critical queries
including both new guards, 0 known-failing, rank gate 39/17/6, correction-sync clean.** One
failure stopped the save:

```
[AMBIGUOUS] NSSF employer: anchor 'asilimia 10' matches 2 facts [9, 50]
```

**Row 9 = `nssf_employer_rate`, row 50 = `rent_wht_rate`** — confirmed by key against the
prospective build, not inferred from the symptom. The new rent fact states a 10% withholding
rate, so **a correct new fact made an old guard ambiguous with no edit to any guard.**

**The gate did exactly its job.** An ambiguous anchor can pass on a fact it does not mean: that
guard could have certified NSSF's employer share while actually matching the rent rate. Blocking
the upload was right.

Re-anchored on **`'mwajiri analipa asilimia 10'`** — unique in the 184-row build, and it carries
the **party**, which is what the guard is about (the employer-share-vs-20%-total confusion,
D-NSSF-1, is the documented live defect). Anchor as the claim, not a proxy — same principle that
rejected bare `'ss.437-447'` for the Part XII guard.

**`EXPECTED_HEAD` → `5e191e0`.** `498c8d8` is now too low a floor for a second, distinct reason:
a clone there still has the bare `'asilimia 10'` anchor and would reproduce this exact failure.

### What the harness got wrong, and what changed

The dry run checked only the **two anchors this package adds**. The regen blocked on one the
package never touched. It now checks **every committed anchor** (36 guards) against the
prospective build and fails the verdict on any non-benign fault.

> **Inserting a row perturbs its neighbours' ANCHORS as well as their RANKS.** The displacement
> arm already covered ranks; nothing covered anchors. That is the `nat_23` 45→46 property in the
> guard layer — and the shape where a per-change check that only inspects the change is blind by
> construction.

Re-verified after the fix: **SAFE TO RUN** — 0 blocking anchor faults (3 adjudicated-benign
OSHA/WCF), 0 displacement caused, both new guards rank 1, new row self-retrieves.
