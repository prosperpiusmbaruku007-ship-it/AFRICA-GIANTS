# R15 REGEN PACKAGE — batch 3 (2026-11-17): the company annual-return deadline row

The 215-row index of `e9e429e` is live. This batch ADDS **ONE row** — `company_annual_return_deadline`, appended at index **215** — and changes nothing else in the index: the index goes **215 → 216 rows**, no existing row number moves.

| | what |
|---|---|
| NEW, appended (row 215) | `company_annual_return_deadline` — "Annual return ya BRELA kwa kampuni inapaswa kuwasilishwa lini? Kila mwaka: kila return hutayarishwa hadi tarehe ya maadhimisho ya kuanzishwa kwa kampuni (au ya return iliyotangulia). Ukichelewa zaidi ya siku 28 baada ya tarehe hiyo, kampuni na maafisa wake wanaweza kutozwa faini (Sheria ya Makampuni). Si miezi 12 tangu usajili, na si 30 Septemba." Source: Companies Act Cap.212 **R.E.2023** (running header on every page; sha256 `3bce27e4…`, now DECLARED in `data/source_documents/MANIFEST.json`), s.131(1) and s.131(3) — metadata only, R44. |

**Why the row exists.** The stored gate reply to `eval_072` said "annual return … hasa ndani ya miezi 12 kutoka tarehe ya usajili wake"; the Act says the return is made up to the anniversary of incorporation and is due within **28 days of that return date**. No served row stated it in the asker's vocabulary. The guard D-FIDELITY-20 (code, ships in the same deploy) replaces a wrong answer; this row is what makes the right one retrievable. **Measured BEFORE shipping (step zero, R15):** in the prospective 216-row index the row is **rank 1 for all six phrasings tried**, including `eval_072` verbatim (`eval/results/rank_company_annual_return_2026_11_17.json`).

Everything else in this batch is **code and data** (D-FIDELITY-20 and -21, the narrowed mixed-supply route, the repaired training pair, atomic artifact writes) and needs no regen.

## ⛔⛔ `rag_fact_count` SEQUENCING — read before anything else

`kaggle/chike_config.json` carries `"rag_fact_count": 215` and `chike-inference/modal_app.py` **refuses to serve** on a mismatch. It is deliberately **NOT bumped in the packaging commit**; step 2 below is the ONE commit that changes it (215 → **216**) together with the fetched artifacts. `EXPECTED_FACT_COUNT = 215` in `kaggle/eval_gate_production_2026_10_09.py` and the count asserted in `tests/test_gate_production_package.py`, `tests/test_inference_health_endpoint.py`, `tests/test_modal_index_contract.py` move in the same commit.

## Local dry run — ALREADY DONE (`eval/index_quality/dryrun_regen_2026_11_17_batch3.py`, artifact `eval/results/dryrun_regen_2026_11_17_batch3.json`)

`VERDICT: SAFE TO RUN`. **216 prospective rows**; changed rows self-retrieve; **0 displacement regressions caused by this package** over every committed guard (4 pre-existing failures fail on the deployed index too; 3 anchor faults, 0 blocking, all adjudicated-benign); the two new critical-query anchors (`siku 28 baada ya tarehe hiyo`) each match **exactly one** row. The regen's own payload gates are imported, not re-implemented (the 2026-10-07 lesson).

## Run it

```bash
# On Kaggle (GPU not required)
!git clone https://github.com/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS.git
%cd AFRICA-GIANTS
!git log --oneline -1          # must have EXPECTED_HEAD (see regenerate_rag_e5.py) as an ancestor, or the script aborts
!python kaggle/regenerate_rag_e5.py
```
Expect: **`216 facts`**, 0–1 self-retrieval failures (the one unchanged failure is `[188]`), all payload gates `[OK]`, every guard `[PASS]` (**83**: the 81 + the two new BRELA annual-return guards), rank gate `PASS`, `correction_sync=CLEAN`.

## Then, in order (R15 steps 4–6)

1. Fetch `rag_embeddings.npy` + `rag_facts_text.json` from the HF dataset repo `prospAprospA007/africa-giants-dataset`; verify the text equals `build_fact_texts()` row for row (**216**) and that **the first 215 are IDENTICAL to the served index** (only row 215 is new).
2. **One commit:** both files into **both** `chike-inference/` and `kaggle/`; `rag_fact_count` 215 → 216; re-derive `EXPECTED_SERVED_SHA256` (the digest over `json.dumps(rows, ensure_ascii=False)`, not the file bytes); flip `tests/test_check_rag_index_freshness.py` back to FRESH (the TWENTY-SEVENTH flip; this batch made the TWENTY-SIXTH, to PENDING); delete the `pending_r15` pin for `company_annual_return_deadline` in `scripts/check_facts_index_sync.py` (it becomes `present_elsewhere` with the needle `siku 28 baada ya tarehe hiyo`); `EXPECTED_FACT_COUNT` 216; restore the three test-rewritten result files before committing.
3. **One R16 window, `chike-inference` ONLY** (the WhatsApp image bakes `chike-whatsapp/`, not `chike/`, and nothing under it changes). Sequence: `/health` of `chike-whatsapp` 0 pending → `python scripts/preflight_deploy.py chike-inference/modal_app.py` exit 0 → `app stop --yes` → deploy with `CHIKE_BUILD` → `/health` build == HEAD and the served index digest. **The deploy carries, in one window:** D-FIDELITY-20 and -21, the narrowed mixed-supply route, and the new row.
4. **Targeted live check (R12c, NOT the full gate)**, every item plus negatives: `eval_072` verbatim and two phrasings (the 28-day rule, no "miezi 12"); a TAX annual-return question still routes to the corporate-return statement (negative); `eval_039` verbatim back on its previous path while a COMBINED-sale question still gets the 3:2 statement; `eval_117` says "sekta 16"; `eval_041` read (see the PROGRESS entry: a guard is proposed, not built); and the earlier items (the VAT pair, the stated-average route, the comparison guard) unchanged.
