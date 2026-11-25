# R15 REGEN PACKAGE — 2026-11-24b: medicines VAT-exempt, PAYE base, SDL deemed month, WCF base; row 66 revised in place

The 220-row index of Kaggle run `3b8cf2f` is live (`37cdf9d`). This package **ADDS FOUR rows** (appended after row 219, so no existing row number moves) and **REVISES ONE row in place** (66). **220 → 224.**

| | row (0-indexed) | what |
|---|---|---|
| NEW | **220** | `medicines_vat_exempt` — "Dawa zinatozwa VAT: zero-rated au msamaha? MSAMAHA, si zero-rated: dawa muhimu za binadamu na mifugo, vifaa tiba na vifungashio VILIVYOIDHINISHWA na Waziri. Zero-rated ni mauzo ya nje; bidhaa yenye msamaha na zero-rating huwa zero-rated. Thibitisha na TRA." (VAT Act Cap.148 R.E.2023, Schedule Part I item 7; s.5(3); apportionment s.74(1)-(2) quoted in the fact) |
| NEW | **221** | `paye_base_employment_income` — PAYE is on MAPATO YA AJIRA yote (wages, bonus, commission, allowances, quantified benefits in kind), not basic salary only; a reimbursement-only allowance is excluded (ITA Cap.332 R.E.2023 s.7(2)-(3)(d)(e), s.104(1); the motor-vehicle exclusion s.7(3)(e) quoted in the fact) |
| NEW | **222** | `sdl_deemed_month_of_payment` — an amount paid for another month is deemed to belong to the month it is PAID (VETA Act Cap.82 R.E.2023 s.14(3)) |
| NEW | **223** | `wcf_contribution_base` — earnings = basic salary AND fixed monthly allowances, not cash only; 0.5% per WCF (dated capture of wcf.go.tz 2026-11-24T08:31:54Z); monthly; the employer may not deduct it (Workers Compensation Act Cap.263 R.E.2023 s.60(1) quoted; GN 185/2016 regs 3, 13) |
| REVISED in place | 66 | `wcf_threshold_no_minimum` — "0.5% of earnings (basic salary and fixed monthly allowances), paid monthly" (was "gross cash emoluments") |

**Held by the founder, NOT packaged:** `nssf_contribution_base_wages` (the page image of Cap.50 R.E.2023 reads "in respect of **living**", so "posho yoyote" was wrong). It rides the next regen.

## ⛔ `rag_fact_count` SEQUENCING

`kaggle/chike_config.json` carries `"rag_fact_count": 220` and `modal_app.py` refuses to serve on a mismatch. **NOT bumped in the packaging commit**; the landing commit bumps it TOGETHER with the fetched artifacts (220 → 224).

## Local dry run — DONE (`eval/index_quality/dryrun_regen_2026_11_24b.py` → `eval/results/dryrun_regen_2026_11_24b.json`)

`VERDICT: SAFE TO RUN`. **224 prospective rows**; **exactly row 66 differs** from the committed index, plus four appended; all 11 payload gates executed; **0 displacement regressions**; **0 pre-existing failures** (the parser bug of 4bn is fixed); 0 blocking anchor faults (3 adjudicated-benign); **ranks of the four NEW guards: 1, 1, 1, 1.** `check_correction_sync` CLEAN. Stated limit: the PAYE guard's FIRST question (the live two-levy specimen "Posho ya nyumba inahesabiwa kwenye SDL, na tofauti yake na PAYE ni ipi?") ranked **6** — a two-topic question the SDL-base row naturally wins and the decomposer splits; the single-topic form is the guard. A row-66 guard was dropped (it never had one; its self-retrieval is checked).

## Run it

```bash
!git clone https://github.com/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS.git
%cd AFRICA-GIANTS
!git log --oneline -1          # must have EXPECTED_HEAD (see regenerate_rag_e5.py) as an ancestor, or the script aborts
!python kaggle/regenerate_rag_e5.py
```
Expect: **`224 facts`**, 0–1 self-retrieval failures (the known `[188]`), all payload gates `[OK]`, every guard `[PASS]` (**95**: the 91 + the four new), rank gate `PASS`, `correction_sync=CLEAN`. Verify the log line `GitHub main HEAD = <sha>` matches the pushed commit before trusting it.

## Then, in order

1. Fetch `rag_embeddings.npy` + `rag_facts_text.json` from the HF dataset repo; verify the text equals `build_fact_texts()` row for row (**224**) and that rows other than 66 and 220–223 are identical to the served index.
2. **One commit:** both files into **both** `chike-inference/` and `kaggle/`; `rag_fact_count` 220 → 224; re-derive `EXPECTED_SERVED_SHA256`; flip `tests/test_check_rag_index_freshness.py` back to FRESH (thirty-third flip); convert the four `pending_r15` pins in `scripts/check_facts_index_sync.py` to `present_elsewhere`.
3. **One R16 window, `chike-inference` ONLY** (`chike-whatsapp` 0 pending first; `python scripts/preflight_deploy.py` exit 0 BEFORE `app stop`), carrying: the **fragment-merge decomposer** (`7cae857`), **D-FIDELITY-32** (wired, replacement copy = the locked fact `medicines_vat_exempt`), and the new index.
4. **Targeted live check (R12c, not the full gate), every reply read.**

## What does NOT need the regen (already in the packaging commit)

D-FIDELITY-32, the corpus repairs (2 quarantines, 2 pair repairs, 1 shared-answer sentence repair; 0 old answers in the export), the dated WCF capture and manifest entry.
