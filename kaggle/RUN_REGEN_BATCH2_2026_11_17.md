# R15 REGEN PACKAGE — batch 2 (2026-11-17): the GN 605A issuer row, stated BY OFFICE

The 215-row index of `a2e6611` is live. This batch changes **ONE served row** (row 213, `gn605a_issuer`) and nothing else in the index: the index stays **215 rows**, no row number moves, no row is added.

| | what |
|---|---|
| REWRITTEN in place (row 213) | `gn605a_issuer` — the row said "iliyotolewa na Serikali" and a live reply then invented *"Waziri wa Kazi, Mawasiliano na Uchukuzi (MHE. George Simbachawene)"*. The Order's OFFICIAL gazette copy (kazi.go.tz, sha256 `1d4145ea…`) carries the signature block **"Minister of State, Prime Minister's Office – Labour, Youth, Employment and Persons with Disability"**, and Labour Institutions Act s.39(1) has "the Minister" (responsible for labour) make the order. The row now states the issuer **by office, with no personal name**: "Waziri anayehusika na masuala ya kazi (Waziri wa Nchi, Ofisi ya Waziri Mkuu: Kazi, Vijana, Ajira na Watu Wenye Ulemavu)". |

Everything else in this batch is **code** (guards, repairs, two model-free statement routes, a probe set) and needs no regen.

## `rag_fact_count` — unchanged (215)

No sequencing hazard this time: the count does not move, so `chike_config.json` stays at 215. What DOES move is the served digest (`EXPECTED_SERVED_SHA256` in `tests/test_inference_health_endpoint.py`, the canonical-JSON-dump digest) — re-derive it from the fetched file, in the same commit as the artifacts.

## Run it

```bash
!git clone https://github.com/prosperpiusmbaruku007-ship-it/AFRICA-GIANTS.git
%cd AFRICA-GIANTS
!git log --oneline -1          # must have EXPECTED_HEAD (see regenerate_rag_e5.py) as an ancestor, or the script aborts
!python kaggle/regenerate_rag_e5.py
```
Expect: `215 facts`, 0–1 self-retrieval failures (the one unchanged failure is `[188]`), all payload gates `[OK]`, every guard `[PASS]` (81), rank gate `PASS`, `correction_sync=CLEAN`.

## Then, in order

1. Fetch both files from the HF dataset repo; verify the text equals `build_fact_texts()` row for row (215) — and that **only row 213 differs** from the served index.
2. **One commit:** both files into **both** `chike-inference/` and `kaggle/`; re-derive `EXPECTED_SERVED_SHA256`; flip `tests/test_check_rag_index_freshness.py` back to FRESH (the TWENTY-FIFTH flip; this batch made the TWENTY-FOURTH, to PENDING).
3. **One R16 window, `chike-inference` ONLY.** The WhatsApp image bakes only `chike-whatsapp/` (`add_local_dir(_HERE, "/root/chike_whatsapp")`), NOT `chike/`, and nothing under `chike-whatsapp/` changes in this batch, so `chike-whatsapp` is NOT redeployed (checked 2026-11-17: `modal_app.py` line 95 bakes `chike/`; `modal_whatsapp.py` line 139 does not). Sequence: `/health` 0 pending, `python scripts/preflight_deploy.py chike-inference/modal_app.py`, stop -> deploy, `/health` build match + served digest.
4. Targeted live verification (R12c, NOT the full gate). The blast radius is enumerated: the two statement routes divert 12 questions of the 8,519 we hold (`eval/results/sweep_d17_routes_2026_11_17.json`, all read by hand), 0 of them in the 400-row gate.
