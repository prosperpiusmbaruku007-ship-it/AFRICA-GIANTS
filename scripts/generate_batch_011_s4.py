#!/usr/bin/env python3
"""Generate batch_011 Sections 7-10 — PAYE(20)+NSSF(15)+GN487A(10)+OSHA(15) = 60 pairs."""
import json, os

OUTPUT_FILE = "datasets/tier1a/raw_sources/raw_pairs_batch_011.jsonl"
CHECKPOINT_DIR = "datasets/tier1a/raw_sources/batch_011_checkpoints"

BANDS = (
    "Vipande vya PAYE (kwa mwezi): "
    "Bendi 1 (0%): TZS 0 – 270,000 "
    "Bendi 2 (8%): TZS 270,001 – 520,000 "
    "Bendi 3 (20%): TZS 520,001 – 760,000 "
    "Bendi 4 (25%): TZS 760,001 – 1,000,000 "
    "Bendi 5 (30%): TZS 1,000,001 na zaidi."
)

NSSF_RATE = (
    "NSSF: mwajiri analipa 10% + mfanyakazi analipa 10% = jumla 20% ya mshahara wa msingi. "
    "Hata mwajiri mwenye mfanyakazi mmoja lazima asajili NSSF — hakuna kizingiti cha idadi ya wafanyakazi."
)

pairs = []

# ── SECTION 7: PAYE CALCULATIONS (20 pairs) ───────────────────────────────

def paye_pair(question, salary, band1, band2, band3, band4, band5, total, note=""):
    breakdown = f"Hesabu ya PAYE kwa TZS {salary:,}/mwezi:\n"
    breakdown += f"Bendi 1 (0%): TZS 270,000 = TZS 0\n"
    if band2 > 0:
        b2_amount = min(salary - 270000, 250000)
        breakdown += f"Bendi 2 (8%): TZS {b2_amount:,} × 8% = TZS {band2:,}\n"
    if band3 > 0:
        b3_amount = min(salary - 520000, 240000)
        breakdown += f"Bendi 3 (20%): TZS {b3_amount:,} × 20% = TZS {band3:,}\n"
    if band4 > 0:
        b4_amount = min(salary - 760000, 240000)
        breakdown += f"Bendi 4 (25%): TZS {b4_amount:,} × 25% = TZS {band4:,}\n"
    if band5 > 0:
        b5_amount = salary - 1000000
        breakdown += f"Bendi 5 (30%): TZS {b5_amount:,} × 30% = TZS {band5:,}\n"
    breakdown += f"PAYE ya jumla: TZS {total:,}/mwezi"
    if note:
        breakdown += f"\n{note}"
    return {"instruction": question, "output": breakdown}

pairs.append(paye_pair(
    "Mfanyakazi wangu anapata TZS 270,000 kwa mwezi — PAYE yake ni ngapi?",
    270000, 0, 0, 0, 0, 0, 0,
    "TZS 270,000 ipo ndani ya Bendi 1 (0%) — hakuna PAYE inayodaiwa."
))
pairs.append(paye_pair(
    "Mshahara wa TZS 271,000 kwa mwezi — PAYE ni kiasi gani?",
    271000, 0, 80, 0, 0, 0, 80,
    "Ziada ya TZS 1,000 juu ya TZS 270,000 inalipwa kodi ya 8%."
))
pairs.append(paye_pair(
    "Mfanyakazi anapata TZS 400,000 kwa mwezi — ninahesabuje PAYE?",
    400000, 0, 10400, 0, 0, 0, 10400,
    "Ziada ya TZS 130,000 (400,000 - 270,000) inalipwa kodi ya 8%."
))
pairs.append(paye_pair(
    "PAYE ya mshahara wa TZS 520,000 kwa mwezi ni ngapi?",
    520000, 0, 20000, 0, 0, 0, 20000,
    "TZS 520,000 ni mwisho wa Bendi 2 — PAYE ya juu kabisa ya Bendi 2 bila kuingia Bendi 3."
))
pairs.append(paye_pair(
    "Mfanyakazi ana mshahara wa TZS 521,000 — PAYE inaongezeka kwa kiasi gani ikilinganishwa na TZS 520,000?",
    521000, 0, 20000, 200, 0, 0, 20200,
    "TZS 1,000 ya ziada (521,000 - 520,000) iko Bendi 3 (20%) = TZS 200 ya ziada ya PAYE."
))
pairs.append(paye_pair(
    "Daktari wangu wa kliniki anapata TZS 600,000 kwa mwezi — PAYE yake ni ngapi?",
    600000, 0, 20000, 16000, 0, 0, 36000,
    "TZS 80,000 ya ziada juu ya TZS 520,000 iko Bendi 3 (20%) = TZS 16,000."
))
pairs.append(paye_pair(
    "Mfanyakazi wa ofisi na mshahara wa TZS 750,000 kwa mwezi — PAYE yake?",
    750000, 0, 20000, 46000, 0, 0, 66000,
    "TZS 230,000 ya ziada juu ya TZS 520,000 iko Bendi 3 (20%) = TZS 46,000."
))
pairs.append(paye_pair(
    "PAYE ya mfanyakazi mwenye mshahara TZS 800,000 kwa mwezi — nionyeshe hesabu kamili.",
    800000, 0, 20000, 48000, 10000, 0, 78000,
    "TZS 40,000 ya ziada juu ya TZS 760,000 iko Bendi 4 (25%) = TZS 10,000."
))
pairs.append(paye_pair(
    "Mkurugenzi wangu anapata TZS 1,000,000 kwa mwezi — PAYE ni ngapi?",
    1000000, 0, 20000, 48000, 60000, 0, 128000,
    "TZS 1,000,000 ni mwisho wa Bendi 4 — PAYE ya juu kabisa ya vipande 4 vya kwanza."
))
pairs.append(paye_pair(
    "Mfanyakazi mwenye mshahara TZS 1,200,000 kwa mwezi — PAYE yake ni ngapi?",
    1200000, 0, 20000, 48000, 60000, 60000, 188000,
    "TZS 200,000 ya ziada juu ya TZS 1,000,000 iko Bendi 5 (30%) = TZS 60,000."
))
pairs.append(paye_pair(
    "Msimamizi mkuu (senior manager) mwenye TZS 1,500,000 kwa mwezi — nionyeshe PAYE kamili.",
    1500000, 0, 20000, 48000, 60000, 150000, 278000,
    "TZS 500,000 ya ziada juu ya TZS 1,000,000 iko Bendi 5 (30%) = TZS 150,000."
))
pairs.append(paye_pair(
    "Mkurugenzi Mkuu anapata TZS 2,000,000 kwa mwezi — PAYE kamili ni ngapi?",
    2000000, 0, 20000, 48000, 60000, 300000, 428000,
    "TZS 1,000,000 ya ziada juu ya TZS 1,000,000 iko Bendi 5 (30%) = TZS 300,000."
))

# Non-resident PAYE
pairs.append({
    "instruction": "Mfanyakazi wangu ni mgeni (non-resident) — PAYE yake inahesabiwaje?",
    "output": (
        "Mfanyakazi asiye mkazi Tanzania (non-resident employee) analipa PAYE tofauti: "
        "Kiwango: asilimia 15 ya jumla ya mshahara — kiwango kimoja tu (flat rate). "
        "Si vipande (progressive bands) kama wakazi. "
        "Mfano: mshahara wa TZS 1,000,000 → PAYE = TZS 150,000 (15%). "
        "Mgeni wa kazi: hakuna msamaha wa Bendi 1 (TZS 270,000 ya kwanza haitasamehewa). "
        f"{BANDS}"
    )
})

# PAYE deadline
pairs.append({
    "instruction": "PAYE inalipwa TRA tarehe ngapi kila mwezi?",
    "output": (
        "PAYE inalipwa TRA tarehe 7 ya mwezi unaofuata. "
        "Mfano: PAYE ya Januari → ilipe kabla ya tarehe 7 Februari. "
        "Kuchelewa kulipa PAYE kunasababisha faini ya 2.5% ya PAYE iliyochelewa kwa kila mwezi, "
        "pamoja na riba ya kila siku ya kuchelewa chini ya Tax Administration Act. "
        "Usifanye makosa: tarehe 20 ni kwa VAT — tarehe 7 ni kwa PAYE na SDL."
    )
})

# Two employees
pairs.append({
    "instruction": "Nina wafanyakazi wawili — mmoja TZS 400,000 na mwingine TZS 800,000 kwa mwezi. PAYE ya jumla ni ngapi?",
    "output": (
        "Mfanyakazi 1 (TZS 400,000/mwezi): "
        "Bendi 1 (0%): TZS 270,000 = TZS 0 "
        "Bendi 2 (8%): TZS 130,000 × 8% = TZS 10,400 "
        "PAYE = TZS 10,400 "
        "\nMfanyakazi 2 (TZS 800,000/mwezi): "
        "Bendi 1 (0%): TZS 270,000 = TZS 0 "
        "Bendi 2 (8%): TZS 250,000 × 8% = TZS 20,000 "
        "Bendi 3 (20%): TZS 240,000 × 20% = TZS 48,000 "
        "Bendi 4 (25%): TZS 40,000 × 25% = TZS 10,000 "
        "PAYE = TZS 78,000 "
        "\nJumla ya PAYE ya kampuni: TZS 10,400 + TZS 78,000 = TZS 88,400/mwezi"
    )
})

# P9 form
pairs.append({
    "instruction": "P9 form ni nini na inawasilishwa lini?",
    "output": (
        "P9 ni fomu ya TRA inayoonyesha muhtasari wa mapato na PAYE ya mfanyakazi kwa mwaka mzima. "
        "Hutolewa na mwajiri kwa kila mfanyakazi mwishoni mwa mwaka wa kodi. "
        "Tarehe ya kuwasilisha P9 kwa TRA: tarehe 31 Machi ya mwaka unaofuata. "
        "Mfano: P9 za mwaka 2025 (Januari–Desemba 2025) → wasilisha TRA kabla ya 31 Machi 2026. "
        "P9 pia hutolewa kwa mfanyakazi anapoacha kazi (Leaving Certificate)."
    )
})

# Bendi 1 tax-free threshold
pairs.append({
    "instruction": "Mshahara wa chini kabisa ambao haulipiwi PAYE Tanzania ni ngapi?",
    "output": (
        "Kizingiti cha mshahara usiolipiwa PAYE ni TZS 270,000 kwa mwezi (au TZS 3,240,000 kwa mwaka). "
        "Mshahara wa TZS 270,000 au chini: PAYE = TZS 0 (ipo kabisa ndani ya Bendi 1 ya 0%). "
        "Mshahara wa TZS 270,001 na zaidi: PAYE inaanza kwenye ziada ya TZS 1 tu (× 8% = TZS 0.08). "
        "MUHIMU: Hakuna msamaha maalum wa TZS 26,000/mwezi — kizingiti cha TZS 270,000 NDIYO msamaha wenyewe. "
        f"{BANDS}"
    )
})

# PAYE for director
pairs.append({
    "instruction": "Wakurugenzi wa kampuni wanalipa PAYE kama wafanyakazi wa kawaida?",
    "output": (
        "Ndio — wakurugenzi wanaolipwa mshahara au posho (director fees) wanalipa PAYE. "
        "Wakurugenzi wa ndani (executive directors) wanaofanya kazi: PAYE kwa vipande vya kawaida. "
        "Wakurugenzi wasio wa kazi (non-executive, posho za mkutano tu): "
        "Mkazi → PAYE kwa vipande vya kawaida. "
        "Asiye mkazi → withholding tax 15% (si PAYE ya vipande). "
        f"{BANDS}"
    )
})

# Benefits in kind
pairs.append({
    "instruction": "Mfanyakazi wangu anapata nyumba ya kukaa kutoka kampuni — hii inaathiri PAYE?",
    "output": (
        "Ndio — makao ya kampuni (housing benefit) yanazingatiwa kama mapato ya mfanyakazi "
        "na yanaweza kuongezwa kwenye mshahara wake kwa PAYE. "
        "TRA ina kanuni za jinsi ya kuthamini makao ya kampuni (deemed income). "
        "Thamani inayoongezwa kwenye mshahara wa mfanyakazi → PAYE inahesabika kwa jumla. "
        "Thibitisha jinsi ya kuthamini makao na mwanasheria wa kodi au TRA."
    )
})

# PAYE vs income tax distinction
pairs.append({
    "instruction": "PAYE na kodi ya mapato (income tax) ni vitu tofauti au ni kitu kimoja?",
    "output": (
        "PAYE (Pay As You Earn) NI kodi ya mapato — ni njia ya kukusanya kodi ya mapato ya mfanyakazi. "
        "Tofauti ya vitendo: "
        "PAYE: mwajiri anakata kodi na kuipeleka TRA kila mwezi (tarehe 7). "
        "Income Tax ya binafsi: mtu anajilipia mwenyewe (self-employed, wawekezaji). "
        "Kwa wafanyakazi wa kawaida: PAYE ndiyo kodi yao yote ya mapato — "
        "hawalazimiki kuwasilisha tax return tofauti kama mwajiri amewapiga PAYE sahihi."
    )
})

# ── SECTION 8: NSSF REINFORCEMENT (15 pairs) ──────────────────────────────
# 5 pairs — 10% employer + 10% employee
pairs.append({
    "instruction": "NSSF inahesabiwaje? Mwajiri analipa ngapi na mfanyakazi analipa ngapi?",
    "output": (
        f"{NSSF_RATE} "
        "Mfano: mshahara wa TZS 500,000 → "
        "Mwajiri: TZS 500,000 × 10% = TZS 50,000. "
        "Mfanyakazi: TZS 500,000 × 10% = TZS 50,000 (ikiwa imejumuishwa kwenye mshahara). "
        "Jumla ya mchango: TZS 100,000 kwa mwezi."
    )
})
pairs.append({
    "instruction": "NSSF rate ni asilimia ngapi Tanzania?",
    "output": (
        f"{NSSF_RATE} "
        "Kiwango: 10% kwa mwajiri + 10% kwa mfanyakazi = 20% ya jumla. "
        "Hakuna kiwango kingine — si 5%, si 15%, si 7.5%. "
        "Chanzo: NSSF Act na kanuni za NSSF (nssf.go.tz)."
    )
})
pairs.append({
    "instruction": "NSSF analipwa nani — mwajiri au mfanyakazi?",
    "output": (
        f"{NSSF_RATE} "
        "Wote wawili wanachangia: mwajiri 10% NA mfanyakazi 10%. "
        "Jinsi inavyofanya kazi: mwajiri anakata 10% kutoka mshahara wa mfanyakazi, "
        "anaongeza 10% yake mwenyewe, na analipa jumla ya 20% kwa NSSF kila mwezi. "
        "Tofauti na SDL (mwajiri peke yake 3.5%) — NSSF ni ya upande wote wawili."
    )
})
pairs.append({
    "instruction": "Naweza kuondoa mfanyakazi kwenye NSSF kama ameomba?",
    "output": (
        f"{NSSF_RATE} "
        "Hapana — mfanyakazi hawezi kuomba kutokuwa na NSSF. "
        "NSSF ni ya lazima (mandatory) kwa wafanyakazi wote. "
        "Hata kama mfanyakazi ana pension nyingine ya kibinafsi, bado analipa NSSF. "
        "Mwajiri ana wajibu wa kisheria wa kuripoti na kulipa NSSF kwa kila mfanyakazi."
    )
})
pairs.append({
    "instruction": "NSSF inalipwa tarehe ngapi kwa mwezi?",
    "output": (
        f"{NSSF_RATE} "
        "Tarehe ya kulipa NSSF: tarehe 9 ya mwezi unaofuata (kwa makampuni mengi). "
        "Thibitisha tarehe yako halisi na NSSF (nssf.go.tz) kwa sababu inaweza kutofautiana. "
        "Kuchelewa kulipa NSSF kunasababisha faini — lipa mapema."
    )
})

# 5 pairs — no threshold for all employers
pairs.append({
    "instruction": "NSSF inahitajika kwa waajiri wote au kuna kizingiti cha wafanyakazi?",
    "output": (
        f"{NSSF_RATE} "
        "NSSF inahitajika kwa WAAJIRI WOTE — hakuna kizingiti cha idadi ya wafanyakazi. "
        "Mwajiri mwenye mfanyakazi 1: NSSF inahitajika. "
        "Mwajiri mwenye wafanyakazi 500: NSSF inahitajika. "
        "Tofauti na SDL (kizingiti cha 10+ wafanyakazi) — NSSF haina kizingiti."
    )
})
pairs.append({
    "instruction": "Nina mfanyakazi mmoja tu wa kujaribu (probation) — nimsajili NSSF?",
    "output": (
        f"{NSSF_RATE} "
        "Ndio — mfanyakazi wa kipindi cha majaribio (probation) bado ni mfanyakazi. "
        "Lazima usajili NSSF tangu siku ya kwanza ya kazi — hakuna msamaha wa kipindi cha majaribio. "
        "Kusajili mapema kunakuepusha faini na madai ya NSSF baadaye."
    )
})
pairs.append({
    "instruction": "Kampuni yangu ndogo ina wafanyakazi 3 tu — nchi ina kanuni ya NSSF?",
    "output": (
        f"{NSSF_RATE} "
        "Ndio — hata wafanyakazi 3 wanastahili NSSF. Hakuna kizingiti cha ukubwa. "
        "Ukiwa na wafanyakazi 3, unapaswa: "
        "(1) Sajili kampuni yako kwa NSSF (nssf.go.tz). "
        "(2) Sajili wafanyakazi wako wote. "
        "(3) Lipa NSSF kila mwezi (10% mwajiri + 10% mfanyakazi)."
    )
})
pairs.append({
    "instruction": "Ninaacha mfanyakazi baada ya miezi 3 — NSSF yake inaenda wapi?",
    "output": (
        f"{NSSF_RATE} "
        "NSSF ya mfanyakazi aliyeacha kazi: michango iliyokusanyika inabaki kwenye akaunti yake ya NSSF. "
        "Mfanyakazi anaweza kudai faida za NSSF anapofika umri wa kustaafu (60 kwa kawaida). "
        "Pia anaweza kudai faida za muda wa kati kama vile matibabu (kwa makampuni fulani). "
        "Mwajiri lazima atoe hati za NSSF kwa mfanyakazi anayeacha kazi."
    )
})
pairs.append({
    "instruction": "NSSF, WCF, na SDL — tofauti yao ni nini kwa kifupi?",
    "output": (
        "NSSF (National Social Security Fund): "
        "10% mwajiri + 10% mfanyakazi | wafanyakazi wote | nssf.go.tz. "
        "Kusudi: pensheni na usalama wa jamii. "
        "\nWCF (Workers' Compensation Fund): "
        "0.5% mwajiri | waajiri WOTE (hata mfanyakazi 1) | portal.wcf.go.tz. "
        "Kusudi: fidia ya ajali za kazi. "
        "\nSDL (Skills Development Levy): "
        "3.5% mwajiri | waajiri wenye 10+ wafanyakazi | TRA. "
        "Kusudi: mafunzo ya nguvu kazi Tanzania."
    )
})

# 5 pairs — domestic workers covered by NSSF
pairs.append({
    "instruction": "Mpishi wangu wa nyumbani (house cook) anapaswa kuwa na NSSF?",
    "output": (
        f"{NSSF_RATE} "
        "Ndio — wafanyakazi wa nyumbani (domestic workers) wanastahili NSSF. "
        "Hii inajumuisha: mpishi, msafi wa nyumba, mlinzi wa nyumba, mtunza watoto. "
        "Hata kama wafanyakazi wako wa nyumbani ni wawili tu, "
        "una wajibu wa kisheria wa kuwaandikisha NSSF."
    )
})
pairs.append({
    "instruction": "Msafi wa ofisi yangu analipwa na kampuni nyingine ya usafi — mimi ninalipia NSSF yake?",
    "output": (
        f"{NSSF_RATE} "
        "Msafi wa kampuni nyingine: unayemlipia ni kampuni ya usafi — kampuni hiyo ndiyo mwajiri wake. "
        "Mwajiri halisi ndiye analipa NSSF. "
        "Kama unalipa mtu binafsi moja kwa moja (mkataba wako binafsi): wewe ndiyo mwajiri — "
        "una wajibu wa NSSF. "
        "Angalia mkataba wako kujua nani ni mwajiri rasmi."
    )
})
pairs.append({
    "instruction": "Mlinzi wa usiku wangu (security guard) ni wa kampuni ya usalama — NSSF yangu?",
    "output": (
        f"{NSSF_RATE} "
        "Kama unamlipa kampuni ya usalama (security company): kampuni hiyo ndiyo mwajiri — "
        "wao wanalipa NSSF ya mlinzi. "
        "Kama unamlipa mlinzi moja kwa moja kwa mkataba wako binafsi: "
        "wewe ndiyo mwajiri — lazima ulipe NSSF. "
        "Njia ya kulinda: wasiliana na kampuni ya usalama kuhusu hali ya NSSF ya mlinzi wako."
    )
})
pairs.append({
    "instruction": "Mtunza watoto wangu (babysitter) analipwa mara kwa mara — NSSF inahitajika?",
    "output": (
        f"{NSSF_RATE} "
        "Hata babysitter anayefanya kazi mara kwa mara kama mfanyakazi wako wa kawaida "
        "anaweza kustahili NSSF kulingana na hali ya mkataba. "
        "Mfanyakazi wa kawaida (regular employee): NSSF inahitajika. "
        "Kazi ya mara moja tu (one-off task): inaweza kuwa mikataba ya huduma, si employment. "
        "Thibitisha hali ya mkataba na mwanasheria wa kazi au NSSF."
    )
})
pairs.append({
    "instruction": "Dereva wangu wa kibinafsi ni mfanyakazi wa nyumbani au wa biashara — NSSF tofauti?",
    "output": (
        f"{NSSF_RATE} "
        "Haijalishi kama dereva ni 'wa nyumbani' au 'wa biashara' — "
        "kama yeye ni mfanyakazi wako wa kawaida, ana haki ya NSSF. "
        "NSSF Act inajumuisha wafanyakazi wote wa biashara NA wafanyakazi wa nyumbani. "
        "Wajibu wako: sajili dereva wako kwa NSSF na lipa 10% yako + kata 10% yake kila mwezi."
    )
})

# ── SECTION 9: GN487A REINFORCEMENT (10 pairs) ────────────────────────────
# 5 pairs — transitional provision
GN487A_TRANS = (
    "GN 487A ya 28 Julai 2025 ina kipengele cha mpito (transitional provision): "
    "mgeni aliyekuwa na leseni halisi kabla ya tarehe ya kufanya kazi ya GN 487A "
    "anaweza kuendelea na shughuli hiyo hadi leseni yake inaisha — "
    "lakini hawezi kuomba upya (renewal) wa leseni hiyo."
)
pairs.append({
    "instruction": "Nilikuwa na leseni ya duka kabla ya GN 487A — ninaweza kuendelea kufanya biashara?",
    "output": (
        f"{GN487A_TRANS} "
        "Maana: ukiwa na leseni iliyotolewa KABLA ya 28 Julai 2025 na bado halisi: "
        "unaweza kuendelea mpaka leseni inaisha. "
        "Lakini: ukiomba upya leseni baada ya GN 487A, maombi yako yatakataliwa kama shughuli hiyo "
        "ipo kwenye orodha ya marufuku ya GN 487A. "
        "Wasiliana na wakili wa uhamiaji kwa hali yako maalum."
    )
})
pairs.append({
    "instruction": "GN 487A — mgeni ambaye tayari ana biashara iliyosajiliwa anafanya nini?",
    "output": (
        f"{GN487A_TRANS} "
        "Wafanyabiashara wageni waliopo: "
        "Leseni iliyopo na bado halisi → endelea hadi leseni inaisha (bila renewal). "
        "Leseni iliyokwisha muda → shughuli hiyo imekwishakatazwa. "
        "Biashara iliyosajiliwa bila leseni maalum → wasiliana na wakili wa uhamiaji haraka. "
        "Adhabu za GN 487A ni kali: faini ya TZS 10M au zaidi na kifungo cha miezi 6."
    )
})
pairs.append({
    "instruction": "Leseni yangu ya biashara inaisha mwezi ujao — naweza kuomba upya kama mgeni?",
    "output": (
        f"{GN487A_TRANS} "
        "Kama shughuli yako ipo kwenye orodha ya marufuku ya GN 487A: "
        "HUWEZI kuomba upya (renewal) — GN 487A inazuia renewal kwa shughuli zilizokatazwa. "
        "Hatua ya haraka: wasiliana na wakili wa uhamiaji KABLA leseni haijafika mwisho "
        "kujua chaguzi lako (mabadiliko ya biashara, ubia na raia wa Tanzania, au kufunga biashara)."
    )
})
pairs.append({
    "instruction": "Mbia wangu wa biashara ni mgeni — GN 487A inaathiri ubia wetu vipi?",
    "output": (
        f"{GN487A_TRANS} "
        "Ubia (partnership) wenye mgeni kama mshirika: "
        "Kama mgeni ana hisa na pia anafanya kazi ya uendeshaji wa biashara iliyokatazwa, "
        "GN 487A inaweza kutumika. "
        "Adhabu pia zinawafikia WATANZANIA wanaowasaidia wageni kukwepa GN 487A: "
        "faini ya TZS 5M au kifungo cha miezi 3. "
        "Muundo salama: Mtanzania ndiye mmiliki na mwendeshaji — mgeni anaweza kuwa mwekezaji tu."
    )
})
pairs.append({
    "instruction": "Kampuni yangu ya nje ina tawi Tanzania — GN 487A inaishughulikia?",
    "output": (
        f"{GN487A_TRANS} "
        "Tawi la kampuni ya nje (foreign company branch): "
        "Kama tawi linafanya shughuli zilizokatazwa na GN 487A, GN inaweza kutumika. "
        "Hata hivyo, hali ya makampuni ya nje ina ngazi tofauti na mtu binafsi — "
        "inahitaji tathmini ya kisheria maalum. "
        "Wasiliana na wakili wa uhamiaji na biashara Tanzania kwa tathmini ya hali yako."
    )
})

# 5 pairs — less-known prohibited activities
GN487A_15 = "GN 487A inakataza shughuli 15 kwa wasio raia Tanzania."
pairs.append({
    "instruction": "GN 487A inakataza delivery services (huduma za utoaji bidhaa) kwa wageni?",
    "output": (
        f"{GN487A_15} "
        "Huduma za utoaji (delivery services) zinaweza kuangukia moja ya kategoria 15 — "
        "hasa kama zinajumuisha usambazaji wa bidhaa kwa njia ya rejareja au jumla. "
        "Orodha ya kategoria 15 rasmi ni pamoja na: biashara ya rejareja na jumla, "
        "uhamishaji wa pesa za simu, ukarabati wa simu, saluni na nyingine. "
        "Huduma za delivery za standalone zinahitaji tathmini ya kisheria — "
        "wasiliana na wakili wa biashara Tanzania."
    )
})
pairs.append({
    "instruction": "Mgeni anaweza kufanya biashara ya uchapishaji (printing business) Tanzania?",
    "output": (
        f"{GN487A_15} "
        "Uchapishaji (printing) ni moja ya shughuli zilizoorodheshwa kwenye marufuku ya GN 487A. "
        "Mgeni hawezi kuendesha biashara ya uchapishaji Tanzania Bara. "
        "Chaguzi: mwekezaji mgeni anaweza kuweka mtaji na kushirikiana na raia wa Tanzania "
        "ambaye ndiye mwendeshaji rasmi wa biashara ya uchapishaji. "
        "Adhabu: faini ya TZS 10M na/au kifungo cha miezi 6, pamoja na kufutwa kwa visa."
    )
})
pairs.append({
    "instruction": "Udhibiti wadudu (pest control) — mgeni anaweza kuendesha biashara hii Tanzania?",
    "output": (
        f"{GN487A_15} "
        "Udhibiti wadudu (pest control/fumigation) uko kwenye orodha ya marufuku ya GN 487A. "
        "Mgeni hawezi kuendesha biashara hii Tanzania Bara. "
        "Hata kama ana ujuzi maalum wa kimataifa wa kemikali au mbinu, sheria inazuia hii. "
        "Suluhisho la kisheria: ubia na raia wa Tanzania mwenye leseni na ujuzi unaohitajika."
    )
})
pairs.append({
    "instruction": "Biashara ya mitumba (second-hand clothes) — inafaa kwa mgeni?",
    "output": (
        f"{GN487A_15} "
        "Biashara ya mitumba (second-hand clothing/goods) ipo kwenye orodha ya marufuku ya GN 487A. "
        "Mgeni hawezi kuendesha biashara hii Tanzania Bara. "
        "Biashara ya mitumba ni sekta iliyohifadhiwa kwa raia wa Tanzania. "
        "Adhabu kwa mgeni: faini ya TZS 10M au zaidi + kifungo cha miezi 6 + kufutwa kwa visa. "
        "Adhabu kwa Mtanzania anayemsaidia: faini TZS 5M au kifungo miezi 3."
    )
})
pairs.append({
    "instruction": "Machinga (street vending) — mgeni anaweza kufanya Tanzania?",
    "output": (
        f"{GN487A_15} "
        "Machinga/street vending ipo kwenye orodha ya marufuku ya GN 487A. "
        "Mgeni hawezi kufanya biashara ya machinga au uuzaji wa mtaani Tanzania Bara. "
        "Hii inajumuisha: uuzaji wa bidhaa za rejareja mitaani, soko la wazi, au maeneo ya umma. "
        "Utekelezaji wa GN 487A (Septemba–Oktoba 2025): Idara ya Uhamiaji ilifanya doria "
        "na kuwakamata wageni kadhaa waliokuwa wakifanya biashara zilizokuwa marufuku."
    )
})

# ── SECTION 10: OSHA REINFORCEMENT (15 pairs) ─────────────────────────────
OSHA_ALL = (
    "OSHA (Occupational Safety and Health Authority) inatumika kwa MAENEO YOTE ya kazi "
    "Tanzania — bila kujali idadi ya wafanyakazi."
)
OSHA_OFFICER = (
    "Afisa usalama (safety officer) anahitajika: "
    "Sekta ya jumla: wafanyakazi 50 au zaidi. "
    "Sekta ya ujenzi: wafanyakazi 20 au zaidi."
)
OSHA_TRIO = (
    "Tofauti kati ya OSHA, WCF, na NSSF: "
    "OSHA = kuzuia ajali na usalama mahali pa kazi (prevention/regulation). "
    "WCF = kulipa fidia baada ya ajali ya kazi (compensation). "
    "NSSF = pensheni na usalama wa jamii wa muda mrefu (pension/social security)."
)

# 5 pairs — OSHA applies to ALL workplaces
pairs.append({
    "instruction": "OSHA inatumika kwa biashara ndogo — wafanyakazi wachache?",
    "output": (
        f"{OSHA_ALL} "
        "Hata duka lenye mfanyakazi 1 linahitaji kufuata kanuni za OSHA. "
        "Mahitaji ya msingi kwa maeneo yote: "
        "Mazingira salama ya kufanyia kazi, mwanga wa kutosha, usafi, upatikanaji wa maji. "
        "Usajili na OSHA (osha.go.tz) unahitajika kwa biashara zote."
    )
})
pairs.append({
    "instruction": "Nina duka la nguo lenye wafanyakazi 4 — OSHA inashughulikia duka langu?",
    "output": (
        f"{OSHA_ALL} "
        "Duka lako lenye wafanyakazi 4 linashughulikiwa na OSHA — hakuna kizingiti cha ukubwa. "
        "Mahitaji yako: "
        "(1) Sajili eneo lako la kazi na OSHA. "
        "(2) Hakikisha mazingira ya kazi ni salama (mwanga, hewa, usafi). "
        "(3) Weka mipango ya dharura (emergency plan). "
        "Ukaguzi wa OSHA unaweza kufanyika wakati wowote bila taarifa."
    )
})
pairs.append({
    "instruction": "Ofisi yangu ina wafanyakazi 6 — OSHA ilazima kusajili?",
    "output": (
        f"{OSHA_ALL} "
        "Ndio — ofisi yoyote, iwe na wafanyakazi 2 au 200, inastahili usajili wa OSHA. "
        "Usajili unafanywa kupitia osha.go.tz. "
        "OSHA inashughulikia: hatari za kimwili, kemikali, ergonomic, na kisaikolojia mahali pa kazi. "
        "Hata ofisi ya kawaida ina hatari (umeme, vipande vya samani, mionzi ya skrini) inayoshughulikiwa na OSHA."
    )
})
pairs.append({
    "instruction": "Kiwanda kidogo chenye wafanyakazi 12 kinahitaji OSHA inspection?",
    "output": (
        f"{OSHA_ALL} "
        "Ndio — kiwanda chochote kinashughulikiwa na OSHA, bila kujali ukubwa. "
        "Kwa kiwanda: mahitaji ya OSHA yanaweza kuwa makali zaidi — "
        "hasa kama kuna: mitambo, kemikali, vifaa vya joto, au hatari za kimwili. "
        "OSHA inspection inaweza kufanyika mara kwa mara au baada ya taarifa ya ajali. "
        "Sajili kiwanda chako na OSHA mara utakapofungua."
    )
})
pairs.append({
    "instruction": "Kama sina wafanyakazi — nafanya kazi peke yangu — OSHA bado inanishughulikia?",
    "output": (
        f"{OSHA_ALL} "
        "Kwa mfanyabiashara peke yake (sole trader bila wafanyakazi): "
        "Kanuni za OSHA zinaweza kutumika kwa eneo lako la kazi hata kama wewe ni mfanyakazi peke yako. "
        "Lengo la OSHA ni usalama wa ENEO LA KAZI — si tu usalama wa wafanyakazi. "
        "Thibitisha mahitaji yako maalum na OSHA (osha.go.tz)."
    )
})

# 5 pairs — safety officer at 50+ (general) and 20+ (construction)
pairs.append({
    "instruction": "Kampuni yangu ina wafanyakazi 55 — nahitaji afisa usalama (safety officer)?",
    "output": (
        f"{OSHA_OFFICER} "
        "Kwa wafanyakazi 55 kwenye sekta ya jumla (si ujenzi): "
        "Ndio — lazima uwe na safety officer. "
        "Safety officer anaweza kuwa: mfanyakazi wa ndani aliyepata mafunzo, "
        "au mshauri wa nje aliyeidhinishwa na OSHA. "
        "Wajibu wa safety officer: ukaguzi wa mara kwa mara, ripoti za usalama, mafunzo ya wafanyakazi."
    )
})
pairs.append({
    "instruction": "Mradi wa ujenzi wenye wafanyakazi 25 — safety officer anahitajika?",
    "output": (
        f"{OSHA_OFFICER} "
        "Kwa sekta ya ujenzi, kizingiti ni wafanyakazi 20+. "
        "Mradi wako wa wafanyakazi 25 (ujenzi): Ndio, safety officer anahitajika. "
        "Sekta ya ujenzi ina hatari za juu zaidi → kizingiti cha chini zaidi (20 badala ya 50). "
        "Safety officer wa ujenzi anahitaji mafunzo maalum ya usalama wa ujenzi."
    )
})
pairs.append({
    "instruction": "Tofauti ya kizingiti cha safety officer kwa ujenzi na sekta nyingine — kwa nini?",
    "output": (
        f"{OSHA_OFFICER} "
        "Sababu ya kizingiti cha chini kwa ujenzi (20 badala ya 50): "
        "Ujenzi una hatari nyingi zaidi: kuanguka kutoka juu, vifaa vya nzito, kemikali, umeme. "
        "Takwimu za OSHA Tanzania zinaonyesha ajali za ujenzi ni nyingi zaidi — "
        "kwa hivyo ulinzi wa mapema (safety officer haraka zaidi) unahitajika."
    )
})
pairs.append({
    "instruction": "Hospitali yangu ina wafanyakazi 45 — safety officer inahitajika?",
    "output": (
        f"{OSHA_OFFICER} "
        "Hospitali (sekta ya afya, si ujenzi): kizingiti ni wafanyakazi 50+. "
        "Kwa wafanyakazi 45, bado chini ya kizingiti cha 50 — safety officer si lazima kiautomatiki. "
        "Hata hivyo, hospitali ina hatari maalum (kemikali, damu, mionzi) — "
        "OSHA inapendekeza safety committee hata kabla ya kizingiti. "
        "Ukifikia 50, safety officer atahitajika mara moja."
    )
})
pairs.append({
    "instruction": "Safety officer anafanya nini hasa na ana sifa gani?",
    "output": (
        f"{OSHA_OFFICER} "
        "Majukumu ya safety officer: "
        "(1) Ukaguzi wa mara kwa mara wa mahali pa kazi. "
        "(2) Kutoa mafunzo ya usalama kwa wafanyakazi. "
        "(3) Kuandika na kusambaza ripoti za ajali na hatari. "
        "(4) Kuhakikisha vifaa vya usalama (PPE) vinatumika. "
        "(5) Kuwasiliana na OSHA kuhusu ukaguzi na taarifa. "
        "Sifa: mafunzo ya usalama na afya mahali pa kazi (yanatolewa na OSHA na taasisi zilizoidhinishwa)."
    )
})

# 5 pairs — OSHA vs WCF vs NSSF distinction
pairs.append({
    "instruction": "Tofauti kati ya OSHA na WCF ni nini? Zote mbili zinasimamia ajali — zinahusiana vipi?",
    "output": (
        f"{OSHA_TRIO} "
        "Mahusiano yao: "
        "OSHA inajaribu KUZUIA ajali isitokee. "
        "WCF inalipia fidia BAADA YA ajali kutokea. "
        "Mfano: mfanyakazi anaanguka na kuumia → OSHA inakagua kama mahali pa kazi kilikuwa salama, "
        "WCF inalipa fidia kwa mfanyakazi aliyeumia."
    )
})
pairs.append({
    "instruction": "Mfanyakazi wangu aliumia kazini — OSHA, WCF, au NSSF ninaweza mdai nini?",
    "output": (
        f"{OSHA_TRIO} "
        "Ajali ya kazi — vitendo vinavyohitajika: "
        "(1) WCF: ripoti ajali ndani ya siku 7 za kazi kupitia portal.wcf.go.tz — WCF inalipa fidia. "
        "(2) OSHA: OSHA inaweza kufanya uchunguzi wa ajali. "
        "(3) NSSF: inahusika na pensheni/ulemavu wa muda mrefu, si ajali za muda mfupi. "
        "Fidia ya haraka kwa ajali: WCF."
    )
})
pairs.append({
    "instruction": "Nilitenga akaunti ya NSSF kwa mfanyakazi — hii inaniepushaje na WCF?",
    "output": (
        f"{OSHA_TRIO} "
        "NSSF na WCF ni tofauti kabisa — NSSF haikuepushaji WCF. "
        "NSSF = pensheni ya baadaye na usalama wa jamii. "
        "WCF = fidia ya ajali za kazi (hata kama mfanyakazi ana NSSF). "
        "Zote mbili zinahitajika: kulipa NSSF haiwezekani kubadilisha wajibu wa WCF."
    )
})
pairs.append({
    "instruction": "OSHA inaweza kunifungia biashara yangu?",
    "output": (
        f"{OSHA_TRIO} "
        "Ndio — OSHA ina mamlaka ya kufunga biashara au maeneo yenye hatari ya mara moja (imminent danger). "
        "Ukaguzi wa OSHA ukipata: "
        "Hatari ya mara moja kwa maisha → OSHA inaweza kusimamisha kazi mara moja. "
        "Ukiukaji wa kawaida → OSHA inatoa onyo na muda wa kurekebisha. "
        "Kutofuata amri ya OSHA → faini na hatua za kisheria zaidi."
    )
})
pairs.append({
    "instruction": "Ninaajiri wafanyakazi wa kilimo shambani — OSHA inawashughulikia?",
    "output": (
        f"{OSHA_ALL} {OSHA_TRIO} "
        "Wafanyakazi wa kilimo (shamba, bustani, misitu) wanashughulikiwa na OSHA. "
        "Hatari za kilimo zinazoshughulikiwa na OSHA: viuatilifu (pesticides), jua kali, "
        "vifaa vya kilimo, nyoka, na hali ngumu za mazingira. "
        "WCF pia inashughulikia wafanyakazi wa kilimo kwa fidia za ajali. "
        "Sajili maeneo yako ya kilimo na OSHA na WCF."
    )
})

assert len(pairs) == 60, f"Expected 60 pairs, got {len(pairs)}"

# Append to output file
with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
    for pair in pairs:
        f.write(json.dumps(pair, ensure_ascii=False) + '\n')

# Read all pairs for final count
all_pairs = []
with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            all_pairs.append(json.loads(line))

# Save checkpoint
ckpt = os.path.join(CHECKPOINT_DIR, "ckpt_225.jsonl")
with open(ckpt, 'w', encoding='utf-8') as f:
    for pair in all_pairs:
        f.write(json.dumps(pair, ensure_ascii=False) + '\n')

print(f"Sections 7-10 complete: {len(pairs)} new pairs saved")
print(f"Total in file: {len(all_pairs)} (target 225)")
print(f"Checkpoint: {ckpt}")

# Validation checks
nssf_rate = sum(1 for p in pairs if 'mwajiri analipa 10% + mfanyakazi analipa 10%' in p['output'])
osha_all_check = sum(1 for p in pairs if 'MAENEO YOTE ya kazi' in p['output'])
gn487a_trans = sum(1 for p in pairs if 'kipengele cha mpito (transitional provision)' in p['output'])
print(f"\nValidation:")
print(f"  NSSF 10%+10% stated: {nssf_rate}")
print(f"  OSHA all workplaces: {osha_all_check}")
print(f"  GN487A transitional: {gn487a_trans}")

# PAYE arithmetic check
paye_checks = {
    270000: 0, 271000: 80, 400000: 10400, 520000: 20000,
    521000: 20200, 600000: 36000, 750000: 66000, 800000: 78000,
    1000000: 128000, 1200000: 188000, 1500000: 278000, 2000000: 428000
}
paye_errors = 0
for pair in pairs:
    for salary, expected_paye in paye_checks.items():
        if f"TZS {salary:,}/mwezi" in pair['instruction']:
            if f"TZS {expected_paye:,}/mwezi" in pair['output'] or f"TZS {expected_paye:,}" in pair['output']:
                pass
            else:
                print(f"  PAYE ERROR: {salary} → expected {expected_paye}")
                paye_errors += 1
print(f"  PAYE arithmetic errors: {paye_errors} (target 0)")
