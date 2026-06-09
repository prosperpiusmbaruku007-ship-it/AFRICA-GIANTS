#!/usr/bin/env python3
"""
Fix 4 confirmed errors in batch_004 (verified against primary sources):
  FIX 1 — WHT director fees non-resident: 20% → 15% (TRA.go.tz confirmed single rate)
  FIX 2 — BRELA name reservation: TZS 20,000 → 50,000 (brela.go.tz fee schedule)
  FIX 3 — BRELA incorporation: TZS 50,000 → 95,000 min (brela.go.tz fee schedule)
  FIX 4 — BRELA foreign branch: TZS 200,000+ → USD 750 + USD 220 (brela.go.tz)
"""
import json, os

BATCH = "datasets/tier1a/raw_sources/raw_pairs_batch_004.jsonl"
LF    = "scripts/locked_facts.json"

pairs = [json.loads(l) for l in open(BATCH, encoding="utf-8") if l.strip()]

changed = []

for p in pairs:
    pid = p["id"]
    modified = False

    # =========================================================
    # FIX 1: WHT director fees — 20% non-resident → 15% for all
    # TRA.go.tz: "Directors Fee (Non full time Directors)" — 15%,
    # no resident/non-resident split.
    # =========================================================

    if "wht_deep_006" in pid:
        # Standard pair: stated 15% resident / 20% non-resident
        p["answer_sw"] = (
            "Kiwango cha WHT kwa ada za mkurugenzi wa Tanzania ni asilimia 15 kwa "
            "wakazi NA wasio wakazi. TRA inatumia kiwango kimoja cha asilimia 15 kwa "
            "ada za mkurugenzi (wasio mkurugenzi wa wakati wote) — hakuna tofauti kati "
            "ya mkazi na asiye mkazi. WHT inakatwa na kampuni kabla ya kulipa mkurugenzi."
        )
        p["answer_en"] = (
            "The WHT rate on director fees (non-full-time directors) in Tanzania is 15% "
            "for both RESIDENTS and NON-RESIDENTS. TRA applies a single rate of 15% — "
            "there is no resident/non-resident split for director fees. WHT is deducted "
            "by the company before paying the director."
        )
        modified = True

    elif "wht_deep_008" in pid:
        # Adversarial pair: question asked "resident director = 20%?"
        # Answer correctly said no, 15%. But then wrongly said 20% for non-residents.
        # Now fix: both resident and non-resident are 15%.
        p["answer_sw"] = (
            "Hapana. Ada za mkurugenzi wa Tanzania mkazi zinatoza WHT ya asilimia 15 "
            "— si asilimia 20. Zaidi ya hayo, kiwango cha asilimia 15 kinatumika pia "
            "kwa wakurugenzi wasio wakazi — TRA inatumia kiwango kimoja cha asilimia 15 "
            "kwa ada za mkurugenzi (wasio mkurugenzi wa wakati wote) bila kujali wakazi "
            "au la. Kiwango cha asilimia 20 kwa ada za mkurugenzi si sahihi."
        )
        p["answer_en"] = (
            "No. Director fees for a Tanzania resident director attract 15% WHT — not 20%. "
            "Furthermore, the 15% rate also applies to non-resident directors — TRA applies "
            "a single rate of 15% for director fees (non-full-time directors) regardless "
            "of residency. A 20% rate for director fees is incorrect."
        )
        modified = True

    elif "wht_deep_023" in pid:
        # Royalties disambiguation pair — mentions director fees 15%/20% in passing
        p["answer_sw"] = p["answer_sw"].replace(
            "ada za mkurugenzi (15% kwa wakazi, 20% kwa wasio wakazi)",
            "ada za mkurugenzi (15% kwa wote — wakazi na wasio wakazi)"
        ).replace(
            "ada za mkurugenzi (15%/20%)",
            "ada za mkurugenzi (15% kwa wote)"
        )
        p["answer_en"] = p["answer_en"].replace(
            "director fees (15% residents, 20% non-residents)",
            "director fees (15% for both residents and non-residents)"
        ).replace(
            "director fees 15%/20%",
            "director fees 15% for all"
        )
        modified = True

    elif "wht_deep_030" in pid:
        # Domestic vs cross-border disambiguation — stated director fees 20% for non-resident
        p["answer_sw"] = p["answer_sw"].replace(
            "ada za mkurugenzi 20%",
            "ada za mkurugenzi 15%"
        ).replace(
            "ada za mkurugenzi asilimia 20",
            "ada za mkurugenzi asilimia 15"
        )
        p["answer_en"] = p["answer_en"].replace(
            "director fees 20%",
            "director fees 15%"
        )
        # Also fix the broader claim about cross-border rates being higher
        p["answer_sw"] = p["answer_sw"].replace(
            "WHT kwa malipo ya NJE (wasio wakazi) ina kiwango cha juu zaidi — ada za usimamizi 15%, ada za mkurugenzi 20%, kodi ya pango 20%.",
            "WHT kwa malipo ya NJE (wasio wakazi) ina kiwango cha juu zaidi kwa baadhi ya aina — ada za usimamizi 15%, ada za mkurugenzi 15% (sawa na wakazi), kodi ya pango 20%."
        )
        p["answer_en"] = p["answer_en"].replace(
            "WHT on CROSS-BORDER (non-resident) payments has higher rates — management fees 15%, director fees 20%, rent 20%.",
            "WHT on CROSS-BORDER (non-resident) payments has higher rates on some items — management fees 15%, director fees 15% (same as residents), rent 20%."
        )
        modified = True

    elif "wht_deep_035" in pid:
        # Adversarial pair: "WHT on director fees is different for residents vs non-residents"
        # Original answer: "No — 15% residents, 20% non-residents."
        # Correct answer: "Yes — 15% for both." So pair_type should change too.
        p["pair_type"] = "standard"
        p["answer_sw"] = (
            "Ndiyo. Ada za mkurugenzi (wasio mkurugenzi wa wakati wote) zinatoza WHT ya "
            "asilimia 15 kwa wakazi NA wasio wakazi — kiwango ni sawa kwa wote. "
            "TRA inatumia kiwango kimoja cha asilimia 15 bila kujali makao ya mkurugenzi. "
            "Hii ni tofauti na ada za usimamizi ambapo wakazi (5%) na wasio wakazi (15%) "
            "wana viwango tofauti."
        )
        p["answer_en"] = (
            "Yes. Director fees (non-full-time directors) attract 15% WHT for both "
            "RESIDENTS and NON-RESIDENTS — the rate is the same for all. TRA applies "
            "a single rate of 15% regardless of director residency. This differs from "
            "management fees where residents (5%) and non-residents (15%) have different rates."
        )
        p["question_sw"] = (
            "WHT kwa ada za mkurugenzi ni sawa kwa wakazi na wasio wakazi — je, ni kweli?"
        )
        p["question_en"] = (
            "WHT on director fees is the same rate for residents and non-residents — "
            "is this true?"
        )
        modified = True

    # =========================================================
    # FIX 2: BRELA name reservation TZS 20,000 → 50,000
    # Source: brela.go.tz/pages/tozo-za-kampuni confirmed TZS 50,000
    # =========================================================

    if "brela_deep_003" in pid:
        p["answer_sw"] = (
            "Gharama ya kuhifadhi jina la kampuni kwa BRELA ni Shilingi 50,000 kwa "
            "kipindi cha siku 30. Wakati huu, jina lililohifadhiwa haliwezi kusajiliwa na "
            "mtu mwingine. Baada ya siku 30, inahitajika kuhifadhi upya au kuendelea na "
            "uanzishwaji wa kampuni. (Chanzo: jedwali la ada la BRELA — brela.go.tz)"
        )
        p["answer_en"] = (
            "The cost of reserving a company name at BRELA is TZS 50,000 for a "
            "30-day period. During this time the reserved name cannot be registered by "
            "anyone else. After 30 days you must re-reserve or proceed with company "
            "incorporation. (Source: BRELA fee schedule — brela.go.tz)"
        )
        modified = True

    # =========================================================
    # FIX 3: BRELA local incorporation TZS 50,000 → TZS 95,000 minimum
    # Source: brela.go.tz — TZS 95,000 for paid-up capital 20,001–1,000,000
    # Scales up to TZS 440,000+ for large paid-up capital
    # =========================================================

    if "brela_deep_004" in pid:
        p["answer_sw"] = p["answer_sw"].replace(
            "wasilisha nyaraka na ada ya Shilingi 50,000 (kampuni ya ndani)",
            "wasilisha nyaraka na ada kuanzia Shilingi 95,000 (kampuni ya ndani, "
            "inategemea mtaji uliowekwa — angalia jedwali la ada la BRELA kwa kiasi halisi)"
        ).replace(
            "(3) wasilisha nyaraka na ada ya Shilingi 50,000 (kampuni ya ndani), ",
            "(3) wasilisha nyaraka na ada kuanzia Shilingi 95,000 (inategemea mtaji — "
            "angalia jedwali la ada la BRELA), "
        )
        p["answer_en"] = p["answer_en"].replace(
            "submit documents and a fee of TZS 50,000 (domestic company)",
            "submit documents and a fee starting from TZS 95,000 (domestic company — "
            "depends on paid-up capital, check BRELA fee schedule for exact amount)"
        ).replace(
            "(3) submit documents and a fee of TZS 50,000 (domestic company), ",
            "(3) submit documents and a fee from TZS 95,000 (depends on paid-up capital "
            "— check BRELA fee schedule), "
        )
        modified = True

    # =========================================================
    # FIX 4: BRELA foreign branch TZS 200,000+ → USD 750 + USD 220
    # Source: brela.go.tz — USD 750 certified copy + USD 220 document filing
    # =========================================================

    if "brela_deep_005" in pid:
        p["answer_sw"] = p["answer_sw"].replace(
            "kulipa ada (karibu Shilingi 200,000+)",
            "kulipa ada ya USD 750 kwa usajili wa hati zilizothibitishwa na USD 220 "
            "kwa ufunguzi wa faili (thibitisha bei za sasa kwenye brela.go.tz)"
        )
        p["answer_en"] = p["answer_en"].replace(
            "paying a fee (approximately TZS 200,000+)",
            "paying a fee of USD 750 (certified copy registration) plus USD 220 "
            "(document filing) — verify current fees at brela.go.tz"
        )
        modified = True

    if modified:
        changed.append(pid)

# Write back
with open(BATCH, "w", encoding="utf-8") as f:
    for p in pairs:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

print(f"Fixed {len(changed)} pairs:")
for pid in changed:
    print(f"  {pid}")

# =========================================================
# Update locked_facts.json — add wht_director_fees entry
# =========================================================

lf = json.load(open(LF, encoding="utf-8"))

lf["wht_director_fees"] = {
    "fact": "WHT on director fees (non-full-time directors) is 15% — a single rate for both residents and non-residents. Source: TRA.go.tz withholding tax page.",
    "primary_source": "https://www.tra.go.tz/page/withholding-tax",
    "verified_date": "2026-06-09",
    "wrong_patterns": [
        "asilimia 20.*mkurugenzi wasio wakazi",
        "mkurugenzi.*asiye mkazi.*asilimia 20",
        "director.*fee.*20%.*non.resident",
        "non.resident.*director.*20%",
        "director fees.*non-resident.*20",
        "20%.*kwa.*mkurugenzi.*wasio wakazi",
    ]
}

with open(LF, "w", encoding="utf-8") as f:
    json.dump(lf, f, ensure_ascii=False, indent=2)

print(f"\nlocked_facts.json: added wht_director_fees entry")
print("Done.")
