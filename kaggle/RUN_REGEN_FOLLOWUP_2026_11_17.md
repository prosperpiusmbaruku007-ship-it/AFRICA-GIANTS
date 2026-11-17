# R15 REGEN PACKAGE — licence validity corrected, dividend clarified, four new rows (2026-11-17)

Ships, as **one** regen, everything that changes a served index row since the 2026-11-16 follow-up regen. The index goes **211 → 215 rows**.

| | rows | what |
|---|---|---|
| REWRITTEN in place (row 168) | 1 | `business_licence_expiry_30_june` — the served text said **every licence expires on 30 June** (the pre-2014 rule, Cap.208 R.E.2002 s.7). The Business Licensing Act **Cap.101 R.E.2023** s.7(1) makes a licence valid **twelve months from the date of issuance**, with an option to pay for up to three years. The key still says `30_june` and is kept (renaming orphans every anchor); the row is embedded WITHOUT the `key: ` prefix so it no longer opens "business licence expiry 30 june" |
| REWRITTEN in place (row 199) | 1 | `dividend_withholding_rate` — states that 5% / 10% hold for a non-resident payee too, that 15% is not a dividend rate, and that a double-tax treaty may differ (a live reply said "15% kwa wasio wakazi") |
| NEW, appended after the 211 (rows 211–214) | 4 | `corporate_income_tax_return` (six months after the year of income; FA2024 nine-month CAG limb; FA2025 CPA threshold TZS 100M), `business_licence_authority` (councils for Category B, BRELA for Category A — PORTAL tier, the Act delegates to a Gazette order not located), `gn605a_issuer` (the Order, not PKF; the 33.4% rests on press sources), `severance_pay_income_tax` (employment income, ordinary bands, no flat 15%) |

**No existing row number moves.** New rows trail the group passages (`_COVERAGE_NEW_KEYS`), as on 2026-11-13 and 2026-11-16.

## ⛔⛔ `rag_fact_count` SEQUENCING — read before anything else

`kaggle/chike_config.json` carries `"rag_fact_count": 211` and `chike-inference/modal_app.py` **refuses to serve** on a mismatch. It is deliberately **NOT bumped in the packaging commit**;
step 2 below is the one commit that changes it (211 → 215) together with the fetched artifacts.

## Local dry run — ALREADY DONE (`eval/index_quality/dryrun_regen_2026_11_17.py`, artifact `eval/results/dryrun_regen_2026_11_17.json`)

`VERDICT: SAFE TO RUN`. 215 prospective rows; changed rows self-retrieve; **0 displacement regressions caused by this package** over 81 committed guards (the 4 pre-existing failures fail on the
deployed index too); the 8 new guards pass. It also caught one real fault BEFORE Kaggle: the new company-return row shared the anchor `30 Juni ya mwaka unaofuata` with the individual-return guard, so
that guard was re-anchored to `hivyo mwisho ni 30 Juni ya mwaka unaofuata` (regen script and `check_facts_index_sync.py`). The model loads from the local HF cache with `HF_HUB_OFFLINE=1`.

## Run it

```bash
# On Kaggle (GPU not required)
!git clone https://github.com/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS.git
%cd AFRICA-GIANTS
!git log --oneline -1          # must have EXPECTED_HEAD (see regenerate_rag_e5.py) as an ancestor, or the script aborts
!python kaggle/regenerate_rag_e5.py
```
Expect: `215 facts`, 0–1 self-retrieval failures, all payload gates `[OK]`, every guard `[PASS]` (81), rank gate `PASS`, `correction_sync=CLEAN`.

## Then, in order (R15 steps 4–6)

1. Fetch `rag_embeddings.npy` + `rag_facts_text.json` from the HF dataset repo; verify the text equals `build_fact_texts()` row for row (215).
2. **One commit:** both files into **both** `chike-inference/` and `kaggle/`, `rag_fact_count` **211 → 215**, flip the pending-regen tests back (`tests/test_check_rag_index_freshness.py`: the TWENTY-THIRD
   flip back to `ok is True` / 215 rows), delete the four `pending_r15` pins in `scripts/check_facts_index_sync.py`; `tests/test_gate_production_package.py`, `tests/test_inference_health_endpoint.py` and
   `tests/test_modal_index_contract.py` assert the count too.
3. Redeploy `chike-inference` per R16 — **only when `/health` shows 0 pending drafts** (`chike-whatsapp` health), pre-flight (`python scripts/preflight_deploy.py chike-inference/modal_app.py`), then
   `app stop --yes`, then deploy, `PYTHONIOENCODING=utf-8 PYTHONUTF8=1 CHIKE_BUILD=$(git rev-parse --short HEAD)`. **`chike-whatsapp` IS redeployed in the SAME window** (founder's go, 2026-11-17: its licence holding line changed to "Halmashauri ya eneo lako (BRELA kwa leseni za Kundi A)"): pre-flight each, tunables gate, `CHIKE_BUILD`, `/health` build match on both, 0 pending before either stop.
4. Live checks that exercise THIS change, each with a negative case (R16): licence validity ("Leseni ya biashara inaisha lini?" must say twelve months, not 30 June); the premise form ("Leseni yangu ya biashara huisha tarehe 30 Juni, sivyo?");
   a dividend question for a non-resident (5/10%, no 15%); a company return deadline (six months, not 12 / 30 Septemba); severance tax (no flat 15%); "GN 605A ilitolewa na nani?" (no PKF). **Negatives:** the provisional-tax instalment question
   still gives 30 September for an instalment; a non-resident SERVICE-fee question still says 15%; a normal SDL/PAYE question still answers; the five fixed statements still render model-free.
5. Targeted verification per R12c — NOT the full gate: the blast radius is the rows whose subject is licence / dividend / return / severance / GN 605A, enumerated from the sweeps (`eval/results/sweep_licence_expiry_2026_11_17.json`, `eval/results/price_d16_2026_11_17.json`).
