# R15 REGEN PACKAGE — four-unanswered-questions follow-up + R44 citation strip (2026-11-16)

Ships, as **one** regen, everything that changes a served index row since the 2026-11-13 coverage regen. The index goes **208 → 210 rows**.

| | rows | what |
|---|---|---|
| NEW, appended after the 208 (rows 208–209) | 2 | `vat_voluntary_registration` (voluntary VAT registration, hedged: the Act names no route, TRA's FAQ says voluntary registration is allowed for unnamed "specific economic activities"), `wht_construction_services` (the 3:2 construction proviso, hedged) |
| REWRITTEN in place (rows 51, 52) | 2 | `wcf_accident_reporting`, `wcf_accident_reporting_deadline` — the served text said "7 working days from date of accident" (row 52) and "7 WORKING days" with no trigger (row 51); both now state the chain and that the clock runs from RECEIPT of notice. `superseded_value` recorded, nothing deleted |
| REWRITTEN in place (CLAUDE.md R44) | 29 | every served Swahili row that carried a consolidated-Act section number (`Kifungu`/`Vifungu` N): the number is gone from the text and lives in `primary_source`. Amending-Act numbers ("2025, Kifungu 8") are kept |

**No existing row number moves.** New rows trail the group passages (`_COVERAGE_NEW_KEYS`), as on 2026-11-13.

## ⛔⛔ `rag_fact_count` SEQUENCING — read before anything else

`kaggle/chike_config.json` carries `"rag_fact_count": 208` and `chike-inference/modal_app.py` **refuses to serve** on a mismatch. It is deliberately
**NOT bumped in the packaging commit**; step 2 below is the one commit that changes it (208 → 210) together with the fetched artifacts.

## Local dry run — ALREADY DONE (`eval/index_quality/measure_followup_2026_11_16.py`, artifact `eval/results/followup_2026_11_16_final.json`)

Numbers are in PROGRESS 4w. Gates replayed locally: 72 committed regen guards (68 + 4 new, each with its own anchor — the phrase "si tangu
tarehe ya ajali" is in BOTH WCF rows, so a shared anchor would have been ambiguous), self-retrieval, the rank-regression gate.

## Run it

```bash
# On Kaggle (GPU not required)
!git clone https://github.com/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS.git
%cd AFRICA-GIANTS
!git log --oneline -1          # must have EXPECTED_HEAD (see regenerate_rag_e5.py) as an ancestor, or the script aborts
!python kaggle/regenerate_rag_e5.py
```
Expect: `210 facts`, 0–1 self-retrieval failures, all payload gates `[OK]`, every guard `[PASS]` (72), rank gate `PASS`, `correction_sync=CLEAN`.

## Then, in order (R15 steps 4–6)

1. Fetch `rag_embeddings.npy` + `rag_facts_text.json` from the HF dataset repo; verify the text equals `build_fact_texts()` row for row (210).
2. **One commit:** both files into **both** `chike-inference/` and `kaggle/`, `rag_fact_count` **208 → 210**, flip the pending-regen tests
   (`tests/test_check_rag_index_freshness.py`: the TWENTIETH flip back to `ok is True` / 210 rows), delete the two `pending_r15` pins in
   `scripts/check_facts_index_sync.py`; `tests/test_gate_production_package.py`, `tests/test_inference_health_endpoint.py` and
   `tests/test_modal_index_contract.py` assert the count too.
3. Redeploy `chike-inference` per R16 — **only when `/health` shows 0 pending drafts**, so no participant waits through the stop (pre-flight,
   then `app stop --yes`, then deploy, `PYTHONIOENCODING=utf-8 PYTHONUTF8=1`). `chike-whatsapp` is NOT redeployed (nothing in it changed).
4. Live checks that exercise THIS change, each with a negative case: "Je naweza kujisajili VAT kwa hiari?" (the hedged row, no invented route);
   "Mfanyakazi ameumia jana nina siku ngapi za kupeleka taarifa ya ajali" (the chain, clock from receipt); a construction-withholding question
   (hedged); a labour question that used to cite "Kifungu 41" (no section number in the reply). **Negative:** a normal SDL/PAYE question still answers,
   and the five fixed statements still render model-free with 0 model calls.
5. Re-run `eval/controls/verify_fixed_statements_deploy_live_2026_11_16.py` (the 34-row ROUTE/FALLTHRU/PRIOR harness) — the statements changed text.
