# Africa Giants — Project Progress

Last updated: 2026-06-19

## Current State
- Live adapter: africa-giants-adapter-v7 (Cerebrium still serving v6 — update pending)
- Live on WhatsApp: +255637809070 via Wappfly
- Dataset: 2,537 pairs across 12 batches
- locked_facts.json: 82 entries

## v7 Gate Results (2026-06-19)
| Subdomain | v6 | v7 | Target | Status |
|---|---|---|---|---|
| brela_registration | 73.3% | 73.3% | >85% | FAIL |
| efd_compliance | 60.0% | 80.0% | >85% | FAIL |
| gn487a | 70.0% | 80.0% | >85% | FAIL |
| nssf_contributions | 84.0% | 88.0% | >85% | PASS |
| osha_registration | 80.0% | 73.3% | >85% | FAIL |
| sdl_compliance | 80.0% | 68.0% | >85% | FAIL |
| vat_registration | 76.7% | 86.7% | >85% | PASS |
| vat_withholding | 75.0% | 80.0% | >85% | FAIL |
| In-corpus | 74.7% | 79.5% | >85% | FAIL |
| Out-of-corpus | 50.0% | 80.0% | >70% | PASS |

Gate: FAILED — in-corpus 79.5% vs 85% threshold.
Refusal gate PASSED for first time in project history.

## Key Findings This Session
- Vocab gap analysis: identified zero-coverage keywords per subdomain
- Scorer bugs fixed: yes_no word boundary, PKF citation strip
- batch_012: 160 surgical vocabulary pairs written, reviewed, approved
- v7 trained at r=64 (fresh weights — v6-lora incompatible with r=64)
- r=64 cannot load from r=16 checkpoint — v8 will also start fresh
- SDL regression: -12% from v6. Root cause: fresh start at r=64 lost v6 SDL gains
- OSHA regression: -6.7% same reason

## Pending Tasks
1. Analyze v7 gate failures per question (gate_001_results.json on HF)
2. Based on failure analysis: write batch_013 targeting SDL, OSHA, BRELA, GN487A
3. Consider 3 epochs for v8 (currently 2) to allow r=64 to converge better
4. Update Cerebrium to serve adapter-v7
5. Fix glob pattern in dataset rebuild script — use *.jsonl not cleaned_pairs_batch_*.jsonl

## Commit History (recent)
- 2713d1e: batch_012 + dataset rebuild
- 13b02d7: locked_facts Agent 2 pre-batch_012
- 8da440d: locked_facts GN605A, OSHA, NSSF, VAT withholding dispute
- cdbbfcc: run_eval.py per-question logging
- e60d07d: run_eval.py yes_no word boundary fix

## HuggingFace Repos
- africa-giants-adapter-v7: LIVE (merged 16bit)
- africa-giants-adapter-v7-lora: LIVE (320MB, r=64)
- africa-giants-adapter-v6: rollback available
- africa-giants-dataset: 2,537 pairs (train 2,283 / val 254)

## Infrastructure
- Cerebrium: serving adapter-v6 (needs update to v7)
- Wappfly: +255637809070
- Kaggle: eval notebook updated for v7 scorer fixes
- GitHub: main branch, all changes pushed

## Scorer Fixes Applied (eval notebook)
- la removed from NO_WORDS in yes_no scorer (word boundary issue)
- Thibitisha na citation strip in definition/procedure scorer
- Both fixes in Kaggle eval notebook Cell 2 only (not in run_eval.py)

## Dataset Naming Convention Issue
Batches 001-008: batch_NNN_cleaned.jsonl
Batches 009-012: cleaned_pairs_batch_NNN.jsonl
Fix: use glob *.jsonl when loading all cleaned pairs
