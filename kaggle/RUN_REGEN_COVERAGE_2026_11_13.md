# R15 REGEN PACKAGE — three-profile coverage batch (2026-11-13)

Ships **24 new facts** (employer / trader / bookkeeper questions that reached no fact) and **5 rewritten rows**
(rows that existed but did not surface), as **one** regen. The index goes **184 → 208 rows**.

| | rows | what |
|---|---|---|
| NEW, appended after the group passages (rows 184–207) | 24 | PAYE payment date, written particulars (2), notice, severance, annual leave, overtime, hours, maternity (2), paternity, unfair-termination compensation, **domestic-worker minimum wage (GN 605A item 4)**, TIN, individual return, dividend WHT, professional-fee WHT, who must register for VAT, VAT refund (2), VAT on credit sales, record keeping, input VAT on passenger vehicles, late-return penalty |
| REWRITTEN in place (rows 1, 26, 58, 90, 95) | 5 | `paye_penalty_rate`, `provisional_tax_instalments`, `efd_not_every_business` (the row that sat in the top 3 of ~1/3 of unrelated questions), `VAT_zero_rated_vs_exempt_input_VAT`, `efd_tra_closure_authority` |

**No existing row number moves.** New rows are appended after the group passages (`_COVERAGE_NEW_KEYS` in
`scripts/precompute_rag_embeddings.py`) precisely because row numbers are pinned all over this repo (9, 57, the ladder at 181, …).

## ⛔⛔ `rag_fact_count` SEQUENCING — read before anything else

`kaggle/chike_config.json` carries `"rag_fact_count": 184` and `chike-inference/modal_app.py` **refuses to serve** on a mismatch.
**It is deliberately NOT bumped in the packaging commit.** Step 2 below is the one commit that changes it, **together with** the fetched
`rag_embeddings.npy` + `rag_facts_text.json`. Bumping it earlier takes production down.

## Local dry run — ALREADY DONE (`eval/index_quality/measure_coverage_batch_2026_11_13.py`, artifact `eval/results/coverage_batch_final.json`)

```
prospective index                          208 rows (184 + 24)
target questions that need a row           top-3 before 13/76  ->  after 75/76   (the 1 miss is pre-existing: rank 5 before, 7 after)
generic EFD row in the top 3               53 -> 21 of 148 questions
regen guards (committed)                   40 -> 68, 0 regressed, 0 dead anchors, 0 newly ambiguous
self-retrieval failures                    0/184 -> 1/208  (the regen blocks at >=10%)
rank-regression gate (nat_23/nat_33/nat_05) 40 / 14 / 6  vs  38 / 16 / 6 before  -> all within tolerance
payload gates (11)                         all OK
correction-sync                            ok, 0 stale
```
28 NEW retrievability guards are added to `critical_queries` (one per new fact and per rewritten row). Each anchor is a substring no
other row carries, and each was watched to pass locally.

## Run it

```bash
# On Kaggle (GPU not required)
!git clone https://github.com/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS.git
%cd AFRICA-GIANTS
!git log --oneline -1          # must have EXPECTED_HEAD (see regenerate_rag_e5.py) as an ancestor, or the script aborts
!python kaggle/regenerate_rag_e5.py
```
Expect: `208 facts`, `0` (or 1) self-retrieval failures, all payload gates `[OK]`, every new guard `[PASS]`, rank gate `PASS`, `correction_sync=CLEAN`.

## Then, in order (R15 steps 4–6)

1. Fetch `rag_embeddings.npy` + `rag_facts_text.json` from the HF dataset repo.
2. **One commit:** both files into **both** `chike-inference/` and `kaggle/`, `rag_fact_count` **184 → 208**, flip the pending-regen tests
   (`tests/test_check_rag_index_freshness.py` back to `ok is True` / 208 rows) and delete the 24 `pending_r15` pins in
   `scripts/check_facts_index_sync.py`; `tests/test_gate_production_package.py` asserts the count too.
3. Redeploy `chike-inference` per R16 (pre-flight, then `app stop --yes`, then deploy, `PYTHONIOENCODING=utf-8 PYTHONUTF8=1`).
4. Live check that exercises THIS change: a new-fact question (e.g. "Nitapataje TIN?" → the 15-day / 7-day text) and a rewritten-row
   question ("Nikikosa kutoa risiti ya EFD adhabu ni nini?"). **Negative case:** a normal SDL/PAYE question still answers.
5. Re-run `eval/controls/coverage_profiles_2026_11_13.py --label after --compare before` (extended harness + unchanged-route controls).
