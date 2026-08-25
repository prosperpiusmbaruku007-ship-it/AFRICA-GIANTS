#!/usr/bin/env python3
"""
Apply do.md corrections to raw_pairs_batch_009.jsonl
Corrections 1-17 per do.md (corrections 6, 7, 12, 13 have no pair changes)
"""
import json, re

INFILE  = "datasets/tier1a/raw_sources/raw_pairs_batch_009.jsonl"
OUTFILE = "datasets/tier1a/raw_sources/raw_pairs_batch_009.jsonl"

with open(INFILE, encoding="utf-8") as f:
    pairs = [json.loads(l) for l in f if l.strip()]

counts = {f"C{i}": 0 for i in range(1, 18)}

for p in pairs:
    out  = p.get("output", "")
    inst = p.get("instruction", "")

    # ------------------------------------------------------------------ #
    # C1 — GN487A TRANSITIONAL PROVISION                                   #
    # ------------------------------------------------------------------ #
    TRANSITION_FIX = (
        "GN 487A ina masharti ya mpito: wageni waliokuwa na leseni halali "
        "tarehe 28 Julai 2025 katika shughuli zilizokatazwa waliruhusiwa "
        "kuendelea mpaka leseni zao ziishe. Baada ya leseni kuisha, upya "
        "(renewal) haukuruhusiwa na leseni mpya haikuweza kutolewa."
    )
    c1_phrases = [
        ("Hakukuwa na 'kipindi cha mazoea' rasmi kilichotolewa kisheria.",
         TRANSITION_FIX),
        ("Hakukuwa na 'grace period' rasmi iliyotangazwa kisheria katika GN 487A.",
         TRANSITION_FIX),
        ("Hakuna grace period rasmi iliyotangazwa kisheria katika GN 487A.",
         TRANSITION_FIX),
        ("Hakuna kipindi cha mazoea rasmi iliyotangazwa kisheria.",
         TRANSITION_FIX),
        ("wageni waliokuwa na biashara katika orodha ya 15 tangu 28 Julai 2025 "
         "wamekuwa wakikosea sheria — bila kujali kulikuwa na kampeni au la.",
         TRANSITION_FIX + " Thibitisha na Idara ya Uhamiaji."),
    ]
    orig = out
    for wrong, right in c1_phrases:
        if wrong in out:
            out = out.replace(wrong, right)
    if out != orig:
        counts["C1"] += 1

    # ------------------------------------------------------------------ #
    # C2 — EFD THRESHOLD TZS 11M                                           #
    # Add threshold context to EFD pairs that imply all businesses need EFD #
    # ------------------------------------------------------------------ #
    EFD_THRESHOLD_NOTE = (
        " Kumbuka: EFD inahitajika kwa biashara zenye mauzo ya TZS milioni 11 "
        "au zaidi kwa mwaka, au biashara zote zilizosajiliwa VAT bila kujali kiasi. "
        "Biashara zenye mauzo chini ya TZS milioni 11 zinaweza kutumia risiti za "
        "kawaida isipokuwa zimesajiliwa VAT. Thibitisha na TRA tra.go.tz."
    )
    orig = out
    # Only add threshold note to EFD pairs that discuss general EFD obligation
    # without mentioning the TZS 11M threshold
    if ("EFD" in out and "milioni 11" not in out and
            any(ph in out for ph in [
                "KILA muamala wa biashara, bila kujali kiasi",
                "kila biashara iliyolazimika kutumia EFD",
                "biashara zinazohitaji EFD",
                "inahitaji EFD kama zimesajiliwa VAT au iko katika orodha ya TRA",
            ])):
        # Append threshold note before the last "Thibitisha" line
        if "Thibitisha na TRA (tra.go.tz)" in out:
            out = out.replace(
                "Thibitisha na TRA (tra.go.tz).",
                "Thibitisha na TRA (tra.go.tz)." + EFD_THRESHOLD_NOTE,
                1
            )
        elif out.endswith("Thibitisha na TRA (tra.go.tz)."):
            out = out + EFD_THRESHOLD_NOTE
    if out != orig:
        counts["C2"] += 1

    # ------------------------------------------------------------------ #
    # C3 — VISA REVOCATION: soften from "lazima daima" to "kunaweza"      #
    # ------------------------------------------------------------------ #
    VISA_SOFT = (
        "kufutwa kwa visa na kibali cha ukaazi kunaweza kutokea kama sehemu "
        "ya adhabu — thibitisha na Idara ya Uhamiaji na wakili wa biashara "
        "kwa hali yako maalum"
    )
    orig = out
    visa_targets = [
        "kufutwa kwa visa/kibali cha kuingia Tanzania ni lazima daima, bila kujali kama faini au kifungo kimetolewa.",
        "kufutwa kwa visa ni lazima daima, bila kujali aina ya adhabu iliyotolewa.",
        "kufutwa kwa visa ni lazima daima, bila kujali kiasi cha faini iliyolipwa.",
        "kufutwa kwa visa ni lazima daima — haiwezi kusamehewa kwa malipo.",
        "kufutwa kwa visa ni lazima daima bila kujali kiasi cha faini.",
        "kufutwa kwa visa ni lazima daima — kinatekelezwa wakati ule ule wa hukumu ya jinai.",
        "kufutwa kwa visa ni lazima daima na hii inatekelezwa na Idara ya Uhamiaji, si mahakama.",
        "kufutwa kwa visa ni lazima daima.",
        "visa ya mgeni itafutwa.",
        "kufutwa kwa visa ni lazima daima na hakiwezi kupunguzwa wala kusamehewa.",
        "Kufutwa kwa visa ni lazima daima — haiwezi kusamehewa kwa malipo.",
        "PAMOJA NA kufutwa kwa visa lazima daima.",
        "PAMOJA NA kufutwa kwa visa (lazima daima).",
        "na kufutwa kwa visa (lazima daima).",
        "Hata hivyo, kufutwa kwa visa ni lazima daima",
    ]
    for phrase in visa_targets:
        if phrase in out:
            # Replace the full phrase, preserving surrounding context
            out = out.replace(phrase, VISA_SOFT + ".")
    # Also handle the structural "(faini AU kifungo) NA kufutwa kwa visa" pattern
    out = out.replace(
        "Muundo sahihi wa adhabu ni: (faini ya angalau TZS 10M AU kifungo cha hadi miezi 6) NA kufutwa kwa visa.",
        "Muundo wa adhabu ni: faini ya angalau TZS 10M AU kifungo cha hadi miezi 6, na " + VISA_SOFT + "."
    )
    out = out.replace(
        "Muundo sahihi ni: faini AU kifungo (korti huchagua moja) PAMOJA NA kufutwa kwa visa (lazima daima).",
        "Muundo wa adhabu: faini AU kifungo (korti huchagua moja), na " + VISA_SOFT + "."
    )
    # Handle remaining "lazima daima" references in visa context
    out = re.sub(
        r"kufutwa kwa visa(?:[^\.\n]{0,60}?)ni lazima daima",
        VISA_SOFT,
        out
    )
    if out != orig:
        counts["C3"] += 1

    # ------------------------------------------------------------------ #
    # C4 — VAT WITHHOLDING REMITTANCE: 7 days → 20th                      #
    # ------------------------------------------------------------------ #
    VAT_WHT_DEADLINE = (
        "VAT withholding inalipwa TRA tarehe 20 ya mwezi unaofuata — "
        "siku ile ile ya VAT return ya kawaida. Si siku 7. "
        "Thibitisha na TRA tra.go.tz."
    )
    orig = out
    c4_targets = [
        "ndani ya siku 7 baada ya mwisho wa mwezi wa muamala (au kadri TRA inavyoelekeza).",
        "Hii ni tofauti na kuwasilisha VAT return ya kawaida (tarehe 20 ya mwezi unaofuata).\nKwa withholding: tarehe ya mwisho = siku 7 baada ya mwisho wa mwezi.",
        "Kwa withholding: tarehe ya mwisho = siku 7 baada ya mwisho wa mwezi.",
        "ndani ya siku 7 baada ya mwisho wa mwezi wa muamala",
        "siku 7 baada ya mwisho wa mwezi",
    ]
    for phrase in c4_targets:
        if phrase in out:
            out = out.replace(phrase, VAT_WHT_DEADLINE)
    # Rewrite the whole VAT withholding deadline pair output if it contains the wrong deadline
    if "tarehe ya mwisho = siku 7" in out:
        out = re.sub(
            r"tarehe ya mwisho = siku 7[^\n\.]*",
            "tarehe ya mwisho ya kulipa = tarehe 20 ya mwezi unaofuata",
            out
        )
    if out != orig:
        counts["C4"] += 1

    # ------------------------------------------------------------------ #
    # C5 — VAT LATE REGISTRATION PENALTY: remove invented 2.5%            #
    # ------------------------------------------------------------------ #
    VAT_PENALTY_FIX = (
        "Adhabu ya kushindwa kusajili VAT kwa wakati ni faini ya hadi TZS 200,000 "
        "na/au kifungo cha miezi 2 hadi 12, pamoja na riba kwa VAT iliyopaswa "
        "kukusanywa tangu kufika kizingiti. Hakuna asilimia ya 2.5% kwa mwezi "
        "katika Sheria ya VAT. Thibitisha na TRA tra.go.tz."
    )
    orig = out
    if "2.5%" in out and any(kw in out for kw in ["VAT", "kusajili", "kizingiti"]):
        out = re.sub(
            r"Faini ya 2\.5% kwa kila mwezi wa kuchelewa[^;\.]*[;,]?",
            VAT_PENALTY_FIX + " ",
            out
        )
        # Also replace standalone 2.5% penalty references in VAT context
        out = re.sub(
            r"\(3\) Faini ya 2\.5% kwa kila mwezi wa kuchelewa;?",
            f"(3) {VAT_PENALTY_FIX}",
            out
        )
    if out != orig:
        counts["C5"] += 1

    # ------------------------------------------------------------------ #
    # C8 — CLOSING BUSINESS DOES NOT ERASE TAX DEBT                       #
    # (search for any implication that closing cancels debt)               #
    # ------------------------------------------------------------------ #
    CLOSE_TAX_FIX = (
        "Kufunga biashara kunasimamisha shughuli za baadaye lakini hakufuti "
        "wajibu wa kodi uliotokana na kipindi ambacho biashara ilikuwa inafanya kazi. "
        "TRA inaweza kudai PAYE, VAT, SDL, faini, na riba zilizobaki hata baada "
        "ya biashara kufungwa. Thibitisha na TRA tra.go.tz."
    )
    orig = out
    # This is a general principle — only apply if a pair explicitly says
    # closing cancels obligations (unlikely in our batch, but check)
    if any(ph in out for ph in [
        "kufunga biashara kunafuta wajibu",
        "ukifunga biashara hutakuwa na wajibu wa kodi",
        "kufunga biashara kunamaliza",
    ]):
        out = out + " " + CLOSE_TAX_FIX
        counts["C8"] += 1

    # ------------------------------------------------------------------ #
    # C10 — EAC CITIZENS GN487A: add nuance about EAC Protocol            #
    # ------------------------------------------------------------------ #
    EAC_NUANCE = (
        " GN 487A kwa maandishi yake inatumika kwa non-citizens wote bila "
        "kutenganisha raia wa EAC. Hata hivyo, uhusiano wake na haki za "
        "EAC Common Market Protocol (uhuru wa kuanzisha biashara na huduma) "
        "unaweza kuhitaji tafsiri ya kisheria ya kina. "
        "Thibitisha na wakili wa biashara."
    )
    orig = out
    if ("EAC" in out and "Kenya" in (out + inst) and
            "Protocol" not in out and "Common Market" not in out):
        # Add nuance to the end before final "Thibitisha"
        if "Thibitisha na Idara ya Uhamiaji." in out:
            out = out.replace(
                "Thibitisha na Idara ya Uhamiaji.",
                "Thibitisha na Idara ya Uhamiaji." + EAC_NUANCE,
                1
            )
        else:
            out = out + EAC_NUANCE
    if out != orig:
        counts["C10"] += 1

    # ------------------------------------------------------------------ #
    # C11 — NSSF PAYMENT DATE: remove specific inconsistent dates         #
    # ------------------------------------------------------------------ #
    orig = out
    if "tarehe 10 au mwishoni mwa mwezi" in out:
        out = out.replace(
            "Baadhi ya vyanzo vinasema tarehe 10 au mwishoni mwa mwezi — tarehe halisi imetangazwa na NSSF mara kwa mara.",
            "Thibitisha tarehe halisi ya sasa na nssf.go.tz — tarehe inaweza kubadilika."
        )
    if out != orig:
        counts["C11"] += 1

    # ------------------------------------------------------------------ #
    # C14 — PAYE: employee does not LOSE ANYTHING → nuanced               #
    # ------------------------------------------------------------------ #
    PAYE_LOSE_FIX = (
        "PAYE ni wajibu wa mwajiri kuwasilisha TRA — si akiba ya mfanyakazi. "
        "Hata hivyo kama mwajiri alikata PAYE lakini hakuituma TRA, mfanyakazi "
        "anaweza kukabiliwa na matatizo ya rekodi za kodi, uthibitisho wa malipo, "
        "au maswali ya ukaguzi. Mfanyakazi anaweza kulalamika TRA au Mahakama "
        "ya Kazi. Thibitisha na TRA tra.go.tz na Wizara ya Kazi."
    )
    orig = out
    if "HUPOTEZA CHOCHOTE kwa upande wa PAYE" in out:
        out = re.sub(
            r"Mfanyakazi HUPOTEZA CHOCHOTE kwa upande wa PAYE[^\n\.]*\.",
            PAYE_LOSE_FIX,
            out
        )
    if out != orig:
        counts["C14"] += 1

    # ------------------------------------------------------------------ #
    # C15 — GN487A BENEFICIAL OWNERSHIP: not explicit in text             #
    # ------------------------------------------------------------------ #
    BENEFICIAL_FIX = (
        "GN 487A haisemi wazi kuhusu 'beneficial ownership' kama kipimo. "
        "Hata hivyo mamlaka za uhamiaji na mahakama zinaweza kuchunguza "
        "udhibiti wa kweli na mnufaika halisi wa biashara kama sehemu ya "
        "uchunguzi wa ukiukwaji. Thibitisha na wakili wa biashara na "
        "Idara ya Uhamiaji kwa tafsiri ya kisheria ya hali yako maalum."
    )
    orig = out
    if "udhibiti wa kweli na faida, si tu muundo wa kisheria" in out:
        out = out.replace(
            "Sheria inazingatia udhibiti wa kweli na faida, si tu muundo wa kisheria.",
            BENEFICIAL_FIX
        )
        out = out.replace(
            "sheria inazingatia udhibiti wa kweli na faida, si tu muundo wa kisheria.",
            BENEFICIAL_FIX
        )
    if out != orig:
        counts["C15"] += 1

    # ------------------------------------------------------------------ #
    # C16 — ONLINE RETAIL GN487A: add "interpretation" caveat            #
    # ------------------------------------------------------------------ #
    ONLINE_CAVEAT = (
        " GN 487A haisemi wazi 'online store' au biashara za mtandaoni. "
        "Kutumika kwake kwa biashara za mtandaoni ni tafsiri ya kisheria "
        "inayotegemea maamuzi ya mamlaka au mahakama. "
        "Thibitisha na wakili wa biashara na Idara ya Uhamiaji kwa hali yako maalum."
    )
    orig = out
    if ("online" in inst.lower() and "GN 487A" in out and
            "tafsiri ya kisheria" not in out and
            "online store" not in out.lower()):
        # Add caveat before the last Thibitisha
        if out.endswith("Thibitisha na Idara ya Uhamiaji."):
            out = out[:-len("Thibitisha na Idara ya Uhamiaji.")] + ONLINE_CAVEAT
        else:
            out = out + ONLINE_CAVEAT
    # Also fix the specific online store pair
    if "Online store inayofikia wateja wa Tanzania" in out:
        out = out.replace(
            "Online store inayofikia wateja wa Tanzania na inayomilikiwa na mgeni "
            "anayeishi Tanzania inakiuka GN 487A.",
            "Online store inayofikia wateja wa Tanzania na inayomilikiwa na mgeni "
            "anayeishi Tanzania inaweza kukiuka GN 487A — lakini hii ni tafsiri ya "
            "kisheria kwani GN 487A haisemi wazi kuhusu biashara za mtandaoni."
        )
    if out != orig:
        counts["C16"] += 1

    # ------------------------------------------------------------------ #
    # C17 — PAYE BAND CALCULATIONS: verify TZS 1.2M calculation          #
    # ------------------------------------------------------------------ #
    # The pair calculating PAYE for TZS 1,200,000 had correct bands
    # but let's verify the specific numbers used match PWC table
    # Band 2: 270,001-520,000 = 250,000 × 8% = 20,000 ✓
    # Band 3: 520,001-760,000 = 240,000 × 20% = 48,000 ✓
    # Band 4: 760,001-1,000,000 = 240,000 × 25% = 60,000 ✓
    # Band 5: 1,000,001-1,200,000 = 200,000 × 30% = 60,000 ✓
    # Total = 188,000 ✓ — calculation is correct, no change needed
    counts["C17"] = 0  # confirmed correct

    p["output"] = out

# Write corrected file
with open(OUTFILE, "w", encoding="utf-8") as f:
    for p in pairs:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

print("=== CORRECTION COUNTS ===")
total_changed = 0
for k, v in sorted(counts.items()):
    status = "INFORMATIONAL" if k in ("C17",) else ("SKIP" if v == 0 else "APPLIED")
    if v > 0:
        total_changed += v
    print(f"  {k}: {v} pairs changed  [{status}]")
print(f"\nTotal pairs modified: {total_changed}")
print(f"Total pairs in file: {len(pairs)}")
print("Done.")
