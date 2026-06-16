#!/usr/bin/env python3
"""Apply corrections 18-25 from do.md founder review."""
import json, re

FILE = "datasets/tier1a/raw_sources/raw_pairs_batch_009.jsonl"

with open(FILE, encoding="utf-8") as f:
    pairs = [json.loads(l) for l in f if l.strip()]

counts = {f"C{i}": 0 for i in range(18, 26)}

for p in pairs:
    out  = p.get("output", "")
    inst = p.get("instruction", "")
    orig = out

    # ------------------------------------------------------------------ #
    # C18 — EFD price range: remove vendor-specific price claim           #
    # ------------------------------------------------------------------ #
    if "inaweza kuanzia TZS 200,000 hadi zaidi ya TZS 1,000,000 kwa mfumo kamili" in out:
        out = out.replace(
            "inaweza kuanzia TZS 200,000 hadi zaidi ya TZS 1,000,000 kwa mfumo kamili.",
            "inategemea aina ya kifaa na muuzaji aliyeidhinishwa na TRA. "
            "Wasiliana na muuzaji wa EFD moja kwa moja kwa bei za sasa, au angalia "
            "orodha ya wauzaji walioidhinishwa kwenye tra.go.tz."
        )
        counts["C18"] += 1

    # ------------------------------------------------------------------ #
    # C19 — Professional VAT: add RSM source note                        #
    # Pairs: CPA and engineer VAT registration                           #
    # ------------------------------------------------------------------ #
    RSM_NOTE = (
        " RSM Tanzania Tax Guide 2025/26 inathibitisha: mtu aliyeruhusiwa, "
        "kusajiliwa, au kuandikishwa kutoa huduma za kitaaluma lazima asajili "
        "VAT bila kujali kiasi cha mapato. Thibitisha na TRA (tra.go.tz) kwa "
        "orodha kamili ya taaluma zinazolazimishwa."
    )
    if ("WANAWEZA kulazimishwa kusajili VAT" in out or
            "bado anaweza kulazimika kusajili VAT" in out):
        # Add before final Thibitisha
        if "Thibitisha na TRA (tra.go.tz) na NBAA." in out:
            out = out.replace(
                "Thibitisha na TRA (tra.go.tz) na NBAA.",
                RSM_NOTE + " Thibitisha na TRA (tra.go.tz) na NBAA."
            )
        elif "Thibitisha na TRA (tra.go.tz) na IET" in out:
            out = out.replace(
                "Wasiliana na TRA (tra.go.tz) na IET kuthibitisha hali yako maalum. "
                "Kama una shaka, omba TRA uthibitisho wa maandishi.",
                RSM_NOTE + " Wasiliana na TRA (tra.go.tz) na IET kuthibitisha hali "
                "yako maalum. Kama una shaka, omba TRA uthibitisho wa maandishi."
            )
        counts["C19"] += 1

    # ------------------------------------------------------------------ #
    # C20 — Pair 14: remove duplicate visa phrase, keep only last        #
    # ------------------------------------------------------------------ #
    VISA_PHRASE = (
        "kufutwa kwa visa na kibali cha ukaazi kunaweza kutokea kama sehemu ya "
        "adhabu — thibitisha na Idara ya Uhamiaji na wakili wa biashara kwa hali "
        "yako maalum."
    )
    if out.count(VISA_PHRASE) > 1:
        # Remove all but the last occurrence
        parts = out.split(VISA_PHRASE)
        # Rejoin, replacing earlier occurrences with nothing
        # Keep last occurrence: join all but last with empty, then add phrase once
        out = "".join(parts[:-1]).replace(
            "Hata kama korti itatoa faini tu (bila kifungo), ",
            "Hata kama korti itatoa faini tu (bila kifungo), "
        )
        # Clean up the result more carefully
        # The pair should read: Ndiyo → visa kunaweza kutokea (once) → Hii ni sehemu tofauti → muundo → last mention
        # Rebuild cleanly:
        if "Mgeni wa India" in inst:
            out = (
                "Ndiyo — " + VISA_PHRASE + " Hata kama korti itatoa faini tu "
                "(bila kifungo), hii bado inaweza kutokea. Hii ni sehemu tofauti "
                "ya adhabu inayotekelezwa na Idara ya Uhamiaji. Kwa hiyo muundo wa "
                "adhabu: faini AU kifungo (korti huchagua moja), na " + VISA_PHRASE +
                " Thibitisha na Idara ya Uhamiaji."
            )
            # Simpler clean version:
            out = (
                "Ndiyo — " + VISA_PHRASE + " Hii ni hatua tofauti "
                "inayotekelezwa na Idara ya Uhamiaji — tofauti na uamuzi wa korti "
                "wa faini au kifungo. Muundo wa adhabu: korti inaamua faini AU "
                "kifungo; Idara ya Uhamiaji inashughulikia hali ya visa. "
                "Thibitisha na Idara ya Uhamiaji."
            )
        counts["C20"] += 1

    # ------------------------------------------------------------------ #
    # C21 — Pair 20: soften post-prison absolute language                #
    # ------------------------------------------------------------------ #
    if ("lazima ataondoka Tanzania" in out or
            "Hawezi kuendelea na biashara kwa sababu hana haki ya kukaa Tanzania tena" in out):
        out = re.sub(
            r"Kwa hiyo mgeni huyo lazima ataondoka Tanzania[^\.]*\.\s*"
            r"Hawezi kuendelea na biashara kwa sababu hana haki ya kukaa Tanzania tena\.",
            "Kama kufutwa kwa visa kumetokea — mgeni atahitajika kuondoka Tanzania "
            "na hataweza kuendelea na biashara. Thibitisha na Idara ya Uhamiaji "
            "kuhusu hali yako maalum baada ya kutumikia adhabu.",
            out
        )
        counts["C21"] += 1

    # ------------------------------------------------------------------ #
    # C22 — Pair 25: add caveat to TRA reopening process                 #
    # ------------------------------------------------------------------ #
    REOPEN_CAVEAT = (
        "Mchakato halisi wa kufungua tena baada ya closure ya TRA unategemea "
        "aina ya ukiukwaji na maamuzi ya TRA. Wasiliana na TRA (tra.go.tz) "
        "moja kwa moja kwa mwongozo wa kesi yako maalum. "
    )
    if ("Kufungwa kwa biashara na TRA kwa ukiukwaji wa EFD kunahitaji" in out and
            "Mchakato halisi wa kufungua tena" not in out):
        out = out.replace(
            "Wasiliana na TRA mara moja na mshauri wa kodi aliyehitimu. "
            "Thibitisha na TRA (tra.go.tz).",
            "Wasiliana na TRA mara moja na mshauri wa kodi aliyehitimu. "
            + REOPEN_CAVEAT +
            "Thibitisha na TRA (tra.go.tz)."
        )
        counts["C22"] += 1

    # ------------------------------------------------------------------ #
    # C23 — Pair 26: EFD receipt language not confirmed                  #
    # ------------------------------------------------------------------ #
    if "TRA haizuii lugha maalum kwa risiti" in out:
        out = out.replace(
            "Risiti za EFD zinaweza kuwa kwa Kiingereza au Kiswahili — "
            "TRA haizuii lugha maalum kwa risiti.",
            "Risiti za EFD zinaweza kuwa kwa Kiingereza au Kiswahili — "
            "thibitisha na TRA (tra.go.tz) kuhusu mahitaji ya lugha kwa risiti "
            "za EFD, kwani mwongozo rasmi wa TRA utathibitisha kama Kiswahili "
            "au Kiingereza zinakubalika."
        )
        # Also soften the trailing confirmation line
        out = out.replace(
            "Thibitisha na TRA (tra.go.tz) kwa miongozo ya hali ya sasa.",
            "Thibitisha na TRA (tra.go.tz) kwa miongozo ya hali ya sasa ya lugha "
            "inayokubalika kwa risiti za EFD."
        )
        counts["C23"] += 1

    # ------------------------------------------------------------------ #
    # C24 — Pair 28: two offences interpretation caveat                  #
    # ------------------------------------------------------------------ #
    if ("Shughuli mbili tofauti zinazopigwa marufuku zinaweza kuchukuliwa "
            "kama makosa mawili tofauti" in out and
            "hii ni tafsiri ya kisheria" not in out):
        out = out.replace(
            "Shughuli mbili tofauti zinazopigwa marufuku zinaweza kuchukuliwa "
            "kama makosa mawili tofauti — saluni ni kosa moja, ukarabati wa simu "
            "ni kosa lingine.",
            "Shughuli mbili tofauti zinazopigwa marufuku zinaweza kuchukuliwa "
            "kama makosa mawili tofauti — saluni ni kosa moja, ukarabati wa simu "
            "ni kosa lingine. Hata hivyo GN 487A haisemi wazi kama shughuli mbili "
            "zinazokatazwa zinachukua kama kosa moja au mawili — hii ni tafsiri "
            "ya kisheria. Thibitisha na wakili wa biashara na Idara ya Uhamiaji."
        )
        counts["C24"] += 1

    # ------------------------------------------------------------------ #
    # C25 — Pair 4: multi-agency enforcement, not immigration sole       #
    # ------------------------------------------------------------------ #
    if ("Idara ya Uhamiaji (Immigration Services Department) ndiyo mamlaka kuu" in out and
            "Mamlaka za leseni za biashara" not in out):
        out = out.replace(
            "TRA: haihusiki moja kwa moja na GN 487A — wanashughulikia kodi. "
            "BRELA: hawahusiki pia — wanasimamia usajili wa biashara tu. "
            "Kampeni ya Sep–Oct 2025 iliongozwa na Idara ya Uhamiaji. "
            "Thibitisha na Idara ya Uhamiaji.",
            "Utekelezaji wa GN 487A unahusisha taasisi nyingi: Idara ya Uhamiaji "
            "inashughulikia ukamataji, hali ya visa, na hatua za uhamiaji. Polisi "
            "wanashiriki katika ukamataji. Mahakama inatoa hukumu. Mamlaka za "
            "leseni za biashara zimetakiwa kusimamisha kutoa leseni mpya kwa "
            "shughuli zilizokatazwa. TRA na BRELA hawahusiki moja kwa moja katika "
            "adhabu za GN 487A — lakini utekelezaji ni wa pamoja wa taasisi nyingi. "
            "Kampeni ya Sep–Oct 2025 iliongozwa na Idara ya Uhamiaji. "
            "Thibitisha na Idara ya Uhamiaji."
        )
        counts["C25"] += 1

    # ------------------------------------------------------------------ #
    # CLEANUP — Pair 15: "PAMOJA NA kufutwa kwa visa." still hard        #
    # (caught during review, not numbered — fix while here)              #
    # ------------------------------------------------------------------ #
    if "PAMOJA NA kufutwa kwa visa." in out and "kunaweza kutokea" not in out:
        out = out.replace(
            "PAMOJA NA kufutwa kwa visa.",
            "na kufutwa kwa visa na kibali cha ukaazi kunaweza kutokea kama "
            "sehemu ya adhabu — thibitisha na Idara ya Uhamiaji."
        )

    p["output"] = out
    if out != orig and not any(counts[f"C{i}"] > 0 for i in range(18, 26)):
        pass  # cleanup only change, counted implicitly

with open(FILE, "w", encoding="utf-8") as f:
    for p in pairs:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

print("=== CORRECTIONS 18-25 ===")
total = 0
for k, v in sorted(counts.items()):
    print(f"  {k}: {v} pairs")
    total += v
print(f"\nTotal pairs modified: {total}")
print(f"Total pairs in file: {len(pairs)}")
print("Done.")
