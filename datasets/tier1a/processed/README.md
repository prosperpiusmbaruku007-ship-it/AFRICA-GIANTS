---
license: cc-by-nc-4.0
language:
- sw
- en
tags:
- tanzania
- business-compliance
- tax
- legal
- swahili
- instruction-tuning
- sft
---

# Africa Giants — Chike Training Dataset

**Product:** Chike by Africa Giants
**Tagline:** Fahamu Biashara Yako, Maarifa Yako
**Target:** Tanzanian business owners and entrepreneurs
**Language:** Swahili (primary) + English

---

## Dataset Summary

Instruction-tuning dataset for Chike — a Tanzanian business compliance AI assistant.
Covers tax, registration, employment law, and business regulations for Tanzania Mainland.

| Split | Pairs |
|-------|-------|
| Train | 1764 |
| Val   | 196 |
| **Total** | **1960** |

---

## Domains Covered

| Domain | Description |
|--------|-------------|
| VAT | Registration, thresholds, withholding 3%/6%, EFD compliance |
| PAYE | 5-band tax table (0/8/20/25/30%), calculations, deadlines |
| SDL | 3.5% rate, 10-employee threshold, SDL vs WCF disambiguation |
| NSSF | 10%+10% contributions, domestic workers, voluntary membership |
| WCF | 0.5% rate, occupational diseases, injury claims, timelines |
| BRELA | Registration types, annual returns, sole trader vs company |
| OSHA | Workplace registration, safety officers, inspections |
| GN 487A | 15 prohibited activities for non-citizens, penalties, transitional provision |
| EFD | TZS 11M threshold, Z-reports, TIMS, enforcement |
| Out-of-corpus | 50 refusal pairs for topics outside Chike scope |

---

## Key Locked Facts (verified from primary sources)

- **PAYE bands (monthly):** 0% up to TZS 270K | 8% 270K-520K | 20% 520K-760K | 25% 760K-1M | 30% above 1M
- **SDL:** 3.5% gross cash emoluments | 10+ employees | paid to TRA by 7th of following month
- **NSSF:** 10% employer + 10% employee | all employers | late penalty 5%/month
- **WCF:** 0.5% cash emoluments | all employers | accident report within 7 working days
- **VAT standard rate:** 18% (unchanged since 2015)
- **VAT registration:** TZS 200M/12 months or TZS 100M/6 months
- **VAT withholding:** 3% goods / 6% services | effective 1 July 2025 | remit by 20th of following month
- **EFD threshold:** TZS 11M annual turnover | all VAT-registered businesses must use EFD regardless of turnover
- **GN 487A:** effective 28 July 2025 | transitional provision for existing valid licences at that date
- **BRELA annual return:** TZS 22,000 fee | TZS 2,500/month late penalty
- **FALSE — trained to refuse:** TZS 26,000 PAYE personal relief (does not exist in Tanzania); 2.5%/month VAT late penalty (does not exist in VAT Act Cap 148)

---

## Batch History

| Batch | Pairs | Focus |
|-------|-------|-------|
| 001 | 46 | Core compliance seed pairs |
| 002 + 002a + 002b | 343 | PAYE, permits, WHT, stamp duty, BRELA |
| 003 | 300 | GN487A adversarial, SDL, VAT, NSSF deep |
| 004 | 300 | GN605A, OSHA, PAYE adversarial, WHT, WCF, BRELA deep |
| 005 | 300 | Permits, income tax, stamp duty, EFD, compliance costs |
| 006 | 300 | GN487A adversarial, SDL, EAC STR, VAT refunds, PAYE foreign |
| 007 | 13 | Replacements and corrections |
| 008 | 150 | GN487A deep, VAT registration, PAYE adversarial, refusal |
| 009 | 300 | Gap-filling: GN487A AND/OR fix, 50 refusal pairs, EFD, SDL vs WCF, VAT withholding |
| **Total** | **1,960** | after dedup — 92 near-duplicates removed |

---

## Quality Process

Every pair has passed:

1. **Fact-Guardian** — check_locked_facts.py against 63 verified regulatory facts
2. **Cross-AI review** — dual-model review (Gemini + OpenRouter) — 0 consensus flags on batch_009
3. **Dedup check** — 92 near-duplicate fingerprints removed across all batches
4. **Founder review** — 10% human sample per batch with corrections applied
5. **Evidence-based corrections** — 25 corrections applied from primary sources including Bowmans, MAK Africa Legal, PWC Tax Summaries 2025, RSM Tax Guide 2025/26, TRA official, VAT Act Cap 148

---

## Intentionally Out-of-Corpus (refusal training)

Chike is trained to respond "Swali hili liko nje ya maarifa yangu ya sasa" for:
import/customs duty, capital gains tax, cryptocurrency taxation, transfer pricing,
Zanzibar taxes (ZRB jurisdiction), mineral royalties, insurance premium levy,
EPZ/SEZ conditions, property valuation methods.

---

## Format

```json
{"instruction": "Swahili question", "input": "", "output": "Swahili answer"}
```

---

## Target Model

- Base: McGill-NLP/AfriqueLlama-8B
- Adapter: prospAprospA007/africa-giants-adapter-v4 (training pending on Kaggle)
- Method: QLoRA 4-bit, Kaggle T4 GPU

---

## License

CC BY-NC 4.0 — non-commercial use only.
Content reflects Tanzania law and regulations as of June 2026.
Always verify with TRA, BRELA, NSSF, or a qualified adviser before acting.

*Africa Giants — Fahamu Biashara Yako, Maarifa Yako*
