#!/usr/bin/env python3
"""Generate batch_011 Sections 2-3 — BRELA (30) + EFD (25) = 55 pairs."""
import json, os

OUTPUT_FILE = "datasets/tier1a/raw_sources/raw_pairs_batch_011.jsonl"
CHECKPOINT_DIR = "datasets/tier1a/raw_sources/batch_011_checkpoints"

BRELA_THREE = (
    "BRELA inasajili aina TATU za biashara: "
    "1. Biashara ya jina (sole trader/business name) "
    "2. Ubia (partnership) "
    "3. Kampuni ya hisa (limited company). "
    "Hakuna aina nyingine ya nne au ya tano chini ya Companies Act Tanzania."
)
SOLE_TRADER = (
    "NDIYO — hata mtu anayefanya biashara kwa jina lake mwenyewe lazima asajili kwa BRELA. "
    "Hakuna ubaguzi kwa jina la mmiliki. "
    "Sheria ya biashara Tanzania Bara inamtaka kila mfanyabiashara asajili biashara yake — "
    "iwe jina lako la kwanza, la ukoo, au jina lolote linalofanana na lako."
)
NO_SEP30 = (
    "Hakuna tarehe maalum ya 30 Septemba kwa annual returns za BRELA — "
    "tarehe inategemea tarehe ya usajili wa kampuni yako. "
    "Annual return inapaswa kuwasilishwa ndani ya mwaka wa kifedha wa kampuni. "
    "Thibitisha na BRELA (brela.go.tz) kwa tarehe yako halisi."
)
LATE_FINE = (
    "Faini ya TZS 2,500 kwa kila mwezi wa kuchelewa. "
    "Miaka 2 ya kuchelewa inaweza kusababisha kufutwa orodha. "
    "Kampuni iliyofutwa haiwezi kufanya mikataba mipya kisheria. "
    "Ada ya kuwasilisha annual return kwa wakati ni TZS 22,000 tu — "
    "gharama ya kuchelewa ni kubwa zaidi kuliko ada yenyewe."
)

pairs = []

# ── SECTION 2: BRELA GROUP A — Number of structures (8 pairs) ────────────
pairs.append({
    "instruction": "BRELA inasajili aina ngapi za biashara Tanzania?",
    "output": (
        f"{BRELA_THREE} "
        "Kwa usajili au maswali zaidi, tembelea brela.go.tz."
    )
})
pairs.append({
    "instruction": "Ni aina gani za biashara zinazosajiliwa na BRELA Tanzania Bara?",
    "output": (
        f"{BRELA_THREE} "
        "Kila aina ina mahitaji tofauti ya usajili, ada, na utaratibu wa kuwasilisha taarifa. "
        "Tembelea brela.go.tz kwa maelezo kamili."
    )
})
pairs.append({
    "instruction": "BRELA inasajili biashara ngapi — nimesikia kuna zaidi ya kumi?",
    "output": (
        f"Hapana — {BRELA_THREE} "
        "Nambari 16 au nyingine kubwa inaweza kutoka chanzo kisicho sahihi. "
        "Thibitisha kila wakati na brela.go.tz."
    )
})
pairs.append({
    "instruction": "Tofauti ya biashara ya jina, ubia, na kampuni ya hisa ni nini kwa BRELA?",
    "output": (
        f"{BRELA_THREE} "
        "Biashara ya jina (sole trader): mmiliki mmoja, anahusika kikamilifu kwa madeni. "
        "Ubia (partnership): wamiliki wawili au zaidi, wanashiriki faida na madeni. "
        "Kampuni ya hisa (limited company): chombo huru kisheria, wanahisa wana dhamana ndogo tu."
    )
})
pairs.append({
    "instruction": "Naweza kusajili NGO au taasisi ya elimu BRELA?",
    "output": (
        "NGO na taasisi za elimu hazisajiliwa chini ya Companies Act kupitia BRELA kwa njia ya kawaida — "
        "NGO zinasajiliwa chini ya Societies Act (polisi) au Trustees' Incorporation Act (AG's office). "
        f"BRELA inashughulikia aina TATU peke yake: {BRELA_THREE} "
        "Wasiliana na Ofisi ya Mkurugenzi wa Jamii kwa usajili wa NGO."
    )
})
pairs.append({
    "instruction": "Ninafungua duka la kujua BRELA inasajili nini — orodha yote tafadhali.",
    "output": (
        f"{BRELA_THREE} "
        "Kwa kila aina, BRELA inashughulikia: usajili wa jina, utoaji wa cheti cha usajili, "
        "mabadiliko ya umiliki, kufuta usajili, na taarifa za kila mwaka (annual returns). "
        "Brela.go.tz ina fomu zote na ada rasmi."
    )
})
pairs.append({
    "instruction": "Mwenzangu alisema BRELA ina aina 16 za biashara — ni kweli?",
    "output": (
        f"Hapana, si kweli. {BRELA_THREE} "
        "Nambari ya 16 haikuwa sahihi — inaweza kuwa imetoka kwa chanzo kibaya au uelewa mbaya wa kategoria ndogo za kibiashara. "
        "Chanzo rasmi pekee ni brela.go.tz."
    )
})
pairs.append({
    "instruction": "Nataka kujua — BRELA inasajili ushirika wa kilimo (agricultural cooperative)?",
    "output": (
        "Ushirika wa kilimo (agricultural cooperative) hausajiliwa na BRELA — "
        "unasajiliwa chini ya Cooperatives Act kupitia Msajili wa Vyama vya Ushirika. "
        f"BRELA inashughulikia aina TATU peke yake: {BRELA_THREE} "
        "Kwa ushirika, wasiliana na Ofisi ya Msajili wa Vyama vya Ushirika."
    )
})

# ── SECTION 2: BRELA GROUP B — Sole trader own name (8 pairs) ────────────
pairs.append({
    "instruction": "Nafanya biashara ya kuuza nguo kwa jina langu mwenyewe — nihitaji kusajili BRELA?",
    "output": (
        f"{SOLE_TRADER} "
        "Ada ya usajili wa biashara ya jina (business name) ni ndogo — "
        "tembelea brela.go.tz kwa ada na fomu sahihi."
    )
})
pairs.append({
    "instruction": "Mimi ni Mariamu Juma — ninauza chakula kwa jina 'Mariamu Juma Foods'. Lazima BRELA?",
    "output": (
        f"{SOLE_TRADER} "
        "'Mariamu Juma Foods' ni jina la biashara — hata kama linajumuisha jina lako, "
        "lazima lisajiliwe kwa BRELA kama biashara ya jina. "
        "Faida ya usajili: umiliki wa kisheria wa jina hilo."
    )
})
pairs.append({
    "instruction": "Kama ninatumia jina langu halisi tu — kwa mfano 'Hassan Mwakasege' — bado nihitaji BRELA?",
    "output": (
        f"{SOLE_TRADER} "
        "Hata ukitumia jina lako kamili bila nyongeza yoyote, sheria ya Tanzania Bara "
        "inakuhitaji kusajili biashara yako kwa BRELA. "
        "Usajili unakupa haki ya kisheria ya kuingia mikataba na kufungua akaunti ya benki kwa jina la biashara."
    )
})
pairs.append({
    "instruction": "Rafiki yangu alisema sole trader asiohitaji BRELA ni huyo anayetumia jina lake — ukweli ni upi?",
    "output": (
        f"Rafiki yako alikosea. {SOLE_TRADER} "
        "Ukweli: sheria haifanyi ubaguzi wowote kulingana na jina unalotumia. "
        "Kila mfanyabiashara Tanzania Bara anahitaji usajili wa BRELA."
    )
})
pairs.append({
    "instruction": "Ninafanya biashara ndogo nyumbani kwa jina langu — BRELA inanishughulikia au la?",
    "output": (
        f"{SOLE_TRADER} "
        "Biashara za nyumbani (home-based businesses) hazisamehewi — "
        "sheria haitofautishi kati ya biashara ya duka na biashara ya nyumba. "
        "Usajili wa BRELA unahitajika bila kujali mahali pa biashara."
    )
})
pairs.append({
    "instruction": "Mfanyabiashara mmoja asiye na wafanyakazi — bado anahitaji kusajili BRELA?",
    "output": (
        f"{SOLE_TRADER} "
        "Idadi ya wafanyakazi haibadilishi wajibu wa kusajili BRELA. "
        "Hata mfanyabiashara peke yake bila mfanyakazi yeyote lazima asajili biashara yake. "
        "Usajili ndio msingi wa uhalali wa biashara Tanzania."
    )
})
pairs.append({
    "instruction": "Ninafanya kazi ya uhuru (freelance) kwa jina langu — BRELA inajishughulisha nami?",
    "output": (
        f"{SOLE_TRADER} "
        "Wafanyakazi huru (freelancers) wanaofanya biashara Tanzania Bara wanahitaji usajili wa BRELA. "
        "Usajili unakusaidia pia kupata TIN ya biashara na kufungua akaunti ya benki ya biashara."
    )
})
pairs.append({
    "instruction": "Kwa nini mtu anayetumia jina lake mwenyewe bado anahitaji BRELA? Inaonekana kama faida ndogo.",
    "output": (
        f"{SOLE_TRADER} "
        "Faida za vitendo: (1) Unaweza kufungua akaunti ya benki kwa jina la biashara. "
        "(2) Unaweza kuingia mikataba rasmi. "
        "(3) Unalindwa na mtu mwingine kutumia jina lako la biashara. "
        "(4) Wateja wakubwa na serikali wanahitaji cheti cha BRELA. "
        "Usajili ni hatua ya msingi ya biashara halali."
    )
})

# ── SECTION 2: BRELA GROUP C — Annual return deadline (7 pairs) ───────────
pairs.append({
    "instruction": "Annual return ya BRELA inapaswa kuwasilishwa kabla ya tarehe gani kila mwaka?",
    "output": (
        f"{NO_SEP30} "
        "Kanuni ya jumla: wasilisha annual return ndani ya miezi 12 ya mwisho wa mwaka wa biashara wako. "
        "Thibitisha tarehe yako halisi kupitia akaunti yako ya BRELA online."
    )
})
pairs.append({
    "instruction": "Kampuni yangu ilisajiliwa mwezi Machi — annual return yangu inaisha lini?",
    "output": (
        f"{NO_SEP30} "
        "Kwa kampuni iliyosajiliwa mwezi Machi, mwaka wako wa biashara utategemea tarehe ya cheti chako cha usajili. "
        "Ingia brela.go.tz au wasiliana na BRELA moja kwa moja kujua tarehe yako halisi ya kuwasilisha."
    )
})
pairs.append({
    "instruction": "Nimeambiwa annual return ya BRELA inaisha 30 Septemba — ni kweli?",
    "output": (
        f"Hapana, si kweli. {NO_SEP30} "
        "Tarehe ya 30 Septemba haikuwa sahihi — haipo kwenye sheria ya Companies Act ya Tanzania. "
        "Usijaribu na tarehe hii — thibitisha na BRELA kwa tarehe yako maalum."
    )
})
pairs.append({
    "instruction": "BRELA annual return — deadline ni wakati gani wa mwaka?",
    "output": (
        f"{NO_SEP30} "
        "Kila kampuni ina tarehe yake maalum inayohusiana na tarehe ya mwisho wa mwaka wake wa biashara. "
        "Mbinu bora: ingia kwenye mfumo wa BRELA online mara baada ya mwisho wa mwaka wako wa biashara."
    )
})
pairs.append({
    "instruction": "Kampuni yangu ina fiscal year inayoishia Desemba 31 — annual return BRELA inapaswa kuwasilishwa lini?",
    "output": (
        f"{NO_SEP30} "
        "Kwa kampuni zenye fiscal year inayoishia Desemba 31, tarehe ya kuwasilisha annual return "
        "inategemea tarehe ya usajili wako na kanuni za BRELA — si Septemba 30. "
        "Thibitisha na brela.go.tz au ofisi ya BRELA."
    )
})
pairs.append({
    "instruction": "Je, kuna tarehe moja inayotumika kwa kampuni zote za BRELA kwa annual returns?",
    "output": (
        f"Hapana. {NO_SEP30} "
        "Kila kampuni ina tarehe yake binafsi kulingana na tarehe yake ya usajili na mwaka wa biashara. "
        "Mfumo wa BRELA online unakuonyesha tarehe yako maalum ukiingia kwa TIN yako au nambari ya usajili."
    )
})
pairs.append({
    "instruction": "Nilichelewa annual return BRELA kwa miezi 3 — ninapaswa kulipa kiasi gani?",
    "output": (
        f"{LATE_FINE} "
        "Kwa miezi 3: TZS 2,500 × 3 = TZS 7,500 ya faini ya kuchelewa, "
        "pamoja na ada ya kawaida ya kuwasilisha ya TZS 22,000. "
        "Jumla takriban TZS 29,500 kabla ya kuwasilisha. "
        "Thibitisha kiasi halisi na BRELA kwani yanaweza kutumia mwezi wowote wa sehemu kama mwezi kamili."
    )
})

# ── SECTION 2: BRELA GROUP D — Late consequences (7 pairs) ───────────────
pairs.append({
    "instruction": "Nitakayopata kama ninachelewesha annual return ya BRELA kwa mwaka mmoja ni nini?",
    "output": (
        f"{LATE_FINE} "
        "Kwa mwaka mmoja (miezi 12): TZS 2,500 × 12 = TZS 30,000 ya faini, "
        "pamoja na ada ya kawaida ya TZS 22,000. Jumla takriban TZS 52,000. "
        "Kabla ya hapo, wakati wowote — wasilisha sasa kuliko kuendelea kuchelewesha."
    )
})
pairs.append({
    "instruction": "Kampuni yangu haijafanya annual return kwa miaka 3 — inaweza kufutwa BRELA?",
    "output": (
        f"{LATE_FINE} "
        "Miaka 3 ya kukosa annual return ni hali hatari sana. "
        "Kwa miaka 2 na zaidi, BRELA ina mamlaka ya kufuta kampuni kwenye orodha (deregister). "
        "Hatua ya haraka: wasiliana na BRELA moja kwa moja kubadilisha hali ya kampuni yako kabla ya kufutwa."
    )
})
pairs.append({
    "instruction": "Annual return ya BRELA imelipwa — faini ya kuchelewa ni ngapi kwa mwezi?",
    "output": (
        f"{LATE_FINE} "
        "Kiwango: TZS 2,500 kwa kila mwezi au sehemu ya mwezi wa kuchelewa. "
        "Ada ya kawaida ya kuwasilisha ni TZS 22,000 — hii hulipwa pia pamoja na faini."
    )
})
pairs.append({
    "instruction": "Kampuni yaliyofutwa BRELA inaweza kufanya nini kisheria?",
    "output": (
        "Kampuni iliyofutwa orodha (deregistered) na BRELA haina uwezo wa kisheria: "
        "haiwezi kuingia mikataba mipya, haiwezi kufungua akaunti mpya ya benki, "
        "haiwezi kushiriki zabuni za serikali, na haiwezi kwenda mahakamani kama mwombaji. "
        f"{LATE_FINE} "
        "Urejesho wa kampuni uliyofutwa unachukua muda na gharama zaidi ya kuwasilisha kwa wakati."
    )
})
pairs.append({
    "instruction": "Kuna njia ya kupunguza faini ya kuchelewa BRELA?",
    "output": (
        f"{LATE_FINE} "
        "Hakuna orodha ya punguzo rasmi la faini katika kanuni za BRELA. "
        "Njia bora: wasiliana na BRELA moja kwa moja ikieleza hali yako — "
        "wakati mwingine BRELA inaweza kushauriana, lakini hii si haki iliyohakikishwa. "
        "Kuwasilisha mapema ni mkakati pekee wa kuepuka faini."
    )
})
pairs.append({
    "instruction": "Kampuni yangu ilianza 2022 na haijawahi kuwasilisha annual return — hatari gani inanisubiri?",
    "output": (
        f"{LATE_FINE} "
        "Kuanzia 2022 hadi 2026 ni karibu miaka 4 — faini inakusanyika kwa kila mwezi. "
        "Zaidi ya miaka 2 ya kukosa, BRELA ina mamlaka ya kufuta kampuni kwenye orodha. "
        "Wasiliana na BRELA haraka kujua hali ya kampuni yako na jinsi ya kurekebisha."
    )
})
pairs.append({
    "instruction": "Ningependa kujua — nini tofauti kati ya kampuni iliyofutwa (deregistered) na iliyolala (dormant) BRELA?",
    "output": (
        "Tofauti muhimu: "
        "Kampuni iliyolala (dormant): bado ipo kwenye orodha ya BRELA, "
        "lazima bado iwasilishe annual returns (na kodi kwa TRA), lakini haifanyi shughuli za biashara. "
        "Kampuni iliyofutwa (deregistered): imefutwa kabisa kwenye orodha — haina uwezo wowote wa kisheria. "
        f"{LATE_FINE} "
        "Kampuni iliyolala lakini haijafanya annual return bado inakusanya faini ya kuchelewa."
    )
})

# ── SECTION 3: EFD GROUP A — Threshold TZS 11M (8 pairs) ─────────────────
EFD_THRESHOLD = (
    "EFD inahitajika kwa biashara zenye mauzo ya TZS milioni 11 au zaidi kwa mwaka. "
    "VAT registered businesses ZOTE lazima zitumie EFD bila kujali kiasi cha mauzo."
)
pairs.append({
    "instruction": "Biashara yangu inauzwa TZS 5M kwa mwaka — ninahitaji EFD?",
    "output": (
        f"{EFD_THRESHOLD} "
        "Kwa mauzo ya TZS 5M tu kwa mwaka, haujafika kizingiti cha TZS 11M — "
        "EFD haihitajiki kiautomatiki, isipokuwa umesajiliwa kwa VAT. "
        "Ukisajiliwa VAT kwa hiari, basi EFD inahitajika hata kwa mauzo ya chini ya TZS 11M."
    )
})
pairs.append({
    "instruction": "Kizingiti cha EFD ni TZS 11 milioni kwa mwaka — ni lazima kuwa VAT registered pia?",
    "output": (
        f"{EFD_THRESHOLD} "
        "Jibu: Si lazima kuwa VAT registered kwa EFD peke yake — "
        "ukifika TZS 11M kwa mwaka, TRA inaweza kuhitaji EFD hata kabla ya kizingiti cha VAT (TZS 200M). "
        "Ukifika TZS 200M (au TZS 100M kwa miezi 6), lazima usajili VAT NA utumie EFD."
    )
})
pairs.append({
    "instruction": "EFD mandatory kwa kila biashara au kuna msamaha?",
    "output": (
        f"{EFD_THRESHOLD} "
        "Msamaha: biashara zenye mauzo chini ya TZS 11M kwa mwaka na ambazo hazijasajiliwa VAT "
        "hazihitajiki kiautomatiki. "
        "Lakini: TRA inaweza kuhitaji EFD kwa biashara yoyote inayochukuliwa kwa hatari ya kodi. "
        "Mauzo ya TZS 11M+ au usajili wa VAT → EFD ni lazima."
    )
})
pairs.append({
    "instruction": "Ninaanza biashara — EFD niihitajiwaje?",
    "output": (
        f"{EFD_THRESHOLD} "
        "Mpya wa biashara: "
        "(1) Chini ya TZS 11M kwa mwaka — EFD haihitajiki bado (endelea kufuatilia mauzo yako). "
        "(2) TZS 11M hadi TZS 200M kwa mwaka — EFD inaweza kuhitajika. "
        "(3) TZS 200M+ (au TZS 100M/miezi 6) — lazima usajili VAT na utumie EFD. "
        "Nunua EFD kupitia wasambazaji walioidhinishwa na TRA."
    )
})
pairs.append({
    "instruction": "Nimeambiwa EFD ni kwa wafanyabiashara wa TZS 40M au zaidi — sahihi?",
    "output": (
        f"Hapana, si sahihi. {EFD_THRESHOLD} "
        "Kizingiti sahihi ni TZS milioni 11 — si 40M. "
        "Thibitisha kila wakati na TRA (tra.go.tz) au ofisi ya TRA karibu nawe."
    )
})
pairs.append({
    "instruction": "Kama ninauzwa TZS 12M mwaka — ninunue EFD haraka au ninaweza kusubiri?",
    "output": (
        f"{EFD_THRESHOLD} "
        "Kwa mauzo ya TZS 12M kwa mwaka, umepita kizingiti cha TZS 11M — "
        "EFD inahitajika. Wasiliana na TRA au msambazaji wa EFD mara moja. "
        "Kutowasilisha risiti za EFD baada ya kupitisha kizingiti ni ukiukaji wa sheria ya kodi."
    )
})
pairs.append({
    "instruction": "EFD na VAT — zinahusiana vipi? Mtu asiye na VAT bado anahitaji EFD?",
    "output": (
        f"{EFD_THRESHOLD} "
        "Mahusiano: EFD inaweza kuhitajika KABLA ya usajili wa VAT (kuanzia TZS 11M). "
        "VAT registered → EFD ni lazima bila shaka yoyote. "
        "Si VAT registered + mauzo TZS 11M+ → EFD bado inaweza kuhitajika kwa amri ya TRA. "
        "Usijitegemee kwamba kutokuwa na VAT kunamaanisha huhitaji EFD."
    )
})
pairs.append({
    "instruction": "TRA inaweza kunipiga faini kwa kutokuwa na EFD wakati mauzo yangu yako TZS 15M kwa mwaka?",
    "output": (
        f"{EFD_THRESHOLD} "
        "Ndio — TRA ina mamlaka ya kukupiga faini kwa kutotumia EFD ukiwa umepitisha kizingiti cha TZS 11M. "
        "Faini za EFD zinaweza kuwa nzito: TRA inaweza kupiga faini ya kutoa risiti za uongo "
        "au kutokuwasilisha risiti kabisa. "
        "Nunua na usajili EFD haraka iwezekanavyo ukiwa umepitisha TZS 11M kwa mwaka."
    )
})

# ── SECTION 3: EFD GROUP B — Z-report timing (8 pairs) ───────────────────
ZREPORT = (
    "Z-report lazima ipigwe MWISHONI MWA SIKU ya biashara — si asubuhi ya siku inayofuata."
)
pairs.append({
    "instruction": "Z-report ya EFD inapigwa wakati gani — mwisho wa siku au asubuhi ya kesho?",
    "output": (
        f"{ZREPORT} "
        "Z-report inafunga muhtasari wa mauzo ya siku hiyo yote na kuutuma kwa TRA kupitia TIMS (mfumo wa mtandao). "
        "Ukiipiga asubuhi ya kesho: muhtasari wa siku moja utakosekana kwenye rekodi za TRA."
    )
})
pairs.append({
    "instruction": "Nilisahau kupiga Z-report usiku wa jana — sasa nifanye nini?",
    "output": (
        f"{ZREPORT} "
        "Ukisahau: piga Z-report haraka iwezekanavyo asubuhi ya leo, kabla ya mauzo mapya. "
        "Z-report iliyochelewa itabainisha tarehe ya jana — hii inaweza kuonekana na TRA. "
        "Epuka kukosea mara nyingi: weka mwagizo wa kikumbusho ili upige Z-report kila siku."
    )
})
pairs.append({
    "instruction": "Kwa nini Z-report lazima ipigwe mwishoni mwa siku na si kesho asubuhi?",
    "output": (
        f"{ZREPORT} "
        "Sababu ya kisheria: Z-report inafunga data ya mauzo ya siku hiyo kwenye EFD — "
        "ikichelewa, data ya siku hiyo inabaki 'wazi' kwenye EFD, ambayo ni ukiukaji wa kanuni za TIMS. "
        "TRA inaweza kuona vipindi vya Z-report vilivyokosekana au vilivyochelewa kupitia TIMS."
    )
})
pairs.append({
    "instruction": "EFD yangu ilifunga (hung) usiku bila kupiga Z-report — hatua gani?",
    "output": (
        f"{ZREPORT} "
        "Hatua: (1) Washa tena EFD asubuhi ya mapema. "
        "(2) Piga Z-report haraka iwezekanavyo kabla ya mauzo mapya. "
        "(3) Kama EFD hifunguki, wasiliana na msambazaji wako wa EFD mara moja. "
        "(4) Andika rekodi ya mkono (manual record) kwa mauzo yoyote hadi EFD irudi kufanya kazi."
    )
})
pairs.append({
    "instruction": "Z-report na X-report tofauti gani?",
    "output": (
        "X-report: ripoti ya muda (inaweza kupigwa mara nyingi siku moja — inakupa muhtasari wa mauzo bila kufunga siku). "
        "Z-report: ripoti ya kufunga siku — inapigwa MARA MOJA mwishoni mwa siku. "
        f"{ZREPORT} "
        "Baada ya Z-report kupigwa, EFD inaanza upya kwa siku mpya. "
        "X-report haifungi siku — inaweza kupigwa wakati wowote bila athari."
    )
})
pairs.append({
    "instruction": "Ninafanya biashara mpaka usiku wa manane — Z-report nipige saa ngapi hasa?",
    "output": (
        f"{ZREPORT} "
        "Wakati halisi: piga Z-report mwishoni mwa mauzo yako ya siku hiyo. "
        "Ukifanya biashara hadi saa 6 usiku, piga Z-report saa 6 usiku au mara baada ya mauzo ya mwisho. "
        "Usisubiri hadi usiku wa manane ikiwa umekwisha fanya mauzo yako ya mwisho mapema zaidi."
    )
})
pairs.append({
    "instruction": "Je, biashara yangu inaendesha mabadiliko mawili ya wafanyakazi — Z-report moja au mbili?",
    "output": (
        f"{ZREPORT} "
        "Z-report MOJA kwa siku — hata kama una mabadiliko mawili ya wafanyakazi. "
        "X-report unaweza kupiga kati ya mabadiliko ili kupata muhtasari wa kila mabadiliko, "
        "lakini Z-report inafunga siku yote mwishoni mwa biashara."
    )
})
pairs.append({
    "instruction": "Biashara yangu ilifungwa siku moja bila mauzo yoyote — bado ninahitaji kupiga Z-report?",
    "output": (
        f"{ZREPORT} "
        "Hata ukiwa na mauzo ya sufuri (zero), piga Z-report. "
        "Kutoipiga kunaweza kuonekana kwa TRA kwenye TIMS kama siku iliyokosekana. "
        "Z-report ya sufuri (TZS 0 mauzo) ni halali na inakumbatia rekodi za siku hiyo bila shida."
    )
})

# ── SECTION 3: EFD GROUP C — Mobile payments (5 pairs) ───────────────────
MOBILE_EFD = (
    "Malipo ya simu (M-Pesa, Tigo Pesa, Airtel Money) yanahitaji risiti ya EFD kama malipo ya kawaida. "
    "Njia ya malipo haiathiri wajibu wa kutoa risiti — kila muamala wa mauzo lazima upate risiti ya EFD."
)
pairs.append({
    "instruction": "Mteja wangu alilipa kwa M-Pesa — nihitaji kutoa risiti ya EFD?",
    "output": (
        f"{MOBILE_EFD} "
        "M-Pesa ni njia ya malipo tu — si msamaha wa risiti. "
        "Piga risiti ya EFD kwa kila mauzo, bila kujali kama mteja alilipa taslimu, M-Pesa, au kadi ya benki."
    )
})
pairs.append({
    "instruction": "Malipo ya Tigo Pesa yanarekodi kwenye akaunti yangu ya simu — hii inatosha badala ya EFD?",
    "output": (
        f"{MOBILE_EFD} "
        "Rekodi ya Tigo Pesa kwenye akaunti yako ya simu haitoshi — "
        "TRA inahitaji risiti ya EFD ambayo inaunganishwa moja kwa moja na TIMS. "
        "Rekodi za simu za pesa hazitumii kama nyaraka za kodi zinazolingana na EFD."
    )
})
pairs.append({
    "instruction": "Ninafanya biashara ya online na watu wanalipa Airtel Money — EFD inahusika?",
    "output": (
        f"{MOBILE_EFD} "
        "Biashara za online hazina msamaha wa EFD. "
        "Kwa biashara za mtandaoni, TRA inaweza kuhitaji EFD ya mtandaoni (online EFD/virtual EFD). "
        "Wasiliana na TRA kujua mfumo unaofaa kwa biashara yako ya mtandaoni."
    )
})
pairs.append({
    "instruction": "Nikiwasilisha risiti ya EFD kwa malipo ya kawaida tu — malipo ya simu ninaweza kuacha?",
    "output": (
        f"{MOBILE_EFD} "
        "Huwezi kuacha malipo ya simu — lazima utoe risiti ya EFD kwa KILA mauzo. "
        "Ukiacha malipo ya simu bila risiti ya EFD, unafanya ukiukaji wa sheria ya kodi, "
        "ambao unaweza kusababisha faini ya TRA."
    )
})
pairs.append({
    "instruction": "Wateja wangu wanalipa kwa njia nyingi — taslimu, M-Pesa, na kadi. EFD inavyofanya kazi kwa kila moja?",
    "output": (
        f"{MOBILE_EFD} "
        "EFD ya kisasa inasaidia kurekodi aina tofauti za malipo: "
        "Taslimu → chagua 'Cash' kwenye EFD. "
        "M-Pesa/Tigo Pesa/Airtel Money → chagua 'Mobile Money'. "
        "Kadi ya benki → chagua 'Card/Electronic'. "
        "Kila aina inapata risiti yake ya EFD inayoonyesha njia ya malipo."
    )
})

# ── SECTION 3: EFD GROUP D — General compliance (4 pairs) ────────────────
pairs.append({
    "instruction": "EFD yangu iliharibika usiku wa manane — ninaweza kuendelea kuuza bila EFD mpaka kesho?",
    "output": (
        "EFD iliyoharibika ni tatizo la kuhitaji hatua za haraka — si kibali cha kuuza bila risiti. "
        "Hatua: (1) Wasiliana na msambazaji wa EFD wako mara moja kupata msaada wa dharura. "
        "(2) Kama haiwezekani kutengeneza usiku, andika rekodi ya mkono kwa mauzo yote. "
        "(3) Ripoti tatizo kwa TRA haraka iwezekanavyo. "
        "Kuendelea kuuza bila EFD bila taarifa ya TRA ni hatari kisheria."
    )
})
pairs.append({
    "instruction": "Kwa mazoezi ya wafanyakazi wapya, tunaweza kupiga risiti za 'mazoezi' kwenye EFD halisi?",
    "output": (
        "HAPANA — risiti za mazoezi (test receipts) kwenye EFD halisi ni hatari sana. "
        "Kila risiti inayopigwa kwenye EFD halisi inaenda kwenye TIMS ya TRA — "
        "risiti za mazoezi zinaweza kuonekana kama mauzo halisi na kuleta tatizo la kodi. "
        "Kwa mafunzo: tumia EFD ya ziada (dummy device) au omba TRA kwa utaratibu rasmi wa mafunzo."
    )
})
pairs.append({
    "instruction": "TIMS ni nini na inahusiana vipi na EFD yangu?",
    "output": (
        "TIMS (Tanzania Integrated Management System) ni mfumo wa TRA unaounganisha EFD zote Tanzania kwa wakati halisi. "
        "Kila risiti unayopiga kwenye EFD yako inatumwa moja kwa moja kwa TRA kupitia TIMS — "
        "inatosha TRA kuona mauzo yako wakati huo huo. "
        "Faida kwako: ikiwa EFD itaharibika, rekodi za TIMS zinaendelea. "
        "Hatari: kukwepa risiti kunaonekana mara moja kwenye TIMS."
    )
})
pairs.append({
    "instruction": "QR code kwenye risiti ya EFD — wateja wangu wanaweza kuitumia vipi?",
    "output": (
        "QR code kwenye kila risiti ya EFD inaweza kuscanwa na mteja yeyote kwa simu yake. "
        "Inampeleka kwenye portal ya TRA ambayo inathibitisha kwamba risiti hiyo ni halisi — "
        "si bandia. "
        "Faida kwa wateja: wanaweza kuthibitisha kwamba unalipa kodi na kutoa risiti halisi. "
        "Faida kwako kama mfanyabiashara: hujui risiti za bandia zikiwa zimetumika kwa jina lako."
    )
})

assert len(pairs) == 55, f"Expected 55 pairs, got {len(pairs)}"

# Append to output file (Section 1 already written)
with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
    for pair in pairs:
        f.write(json.dumps(pair, ensure_ascii=False) + '\n')

# Read all pairs so far for checkpoint
all_pairs = []
with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            all_pairs.append(json.loads(line))

# Save checkpoint at 100 pairs (after this section brings total to 85, next one will hit 100)
ckpt = os.path.join(CHECKPOINT_DIR, "ckpt_085.jsonl")
with open(ckpt, 'w', encoding='utf-8') as f:
    for pair in all_pairs:
        f.write(json.dumps(pair, ensure_ascii=False) + '\n')

print(f"Sections 2-3 complete: {len(pairs)} new pairs saved")
print(f"Total in file: {len(all_pairs)}")
print(f"Checkpoint: {ckpt}")

# Quick validation for BRELA/EFD mandatories
brela_three = sum(1 for p in pairs if 'BRELA inasajili aina TATU' in p['output'])
sole_trader = sum(1 for p in pairs if 'NDIYO — hata mtu anayefanya biashara kwa jina lake mwenyewe' in p['output'])
no_sep30 = sum(1 for p in pairs if 'Hakuna tarehe maalum ya 30 Septemba' in p['output'])
late_fine = sum(1 for p in pairs if 'Faini ya TZS 2,500 kwa kila mwezi' in p['output'])
efd_thresh = sum(1 for p in pairs if 'EFD inahitajika kwa biashara zenye mauzo ya TZS milioni 11' in p['output'])
zreport = sum(1 for p in pairs if 'Z-report lazima ipigwe MWISHONI MWA SIKU' in p['output'])
mobile = sum(1 for p in pairs if 'Malipo ya simu (M-Pesa, Tigo Pesa, Airtel Money) yanahitaji risiti ya EFD' in p['output'])
print(f"\nMandatory phrase check:")
print(f"  BRELA 3 structures: {brela_three} (target 8)")
print(f"  Sole trader must register: {sole_trader} (target 8)")
print(f"  No Sep 30 deadline: {no_sep30} (target 7)")
print(f"  Late fine TZS 2,500: {late_fine} (target 7)")
print(f"  EFD threshold 11M: {efd_thresh} (target 8)")
print(f"  Z-report end of day: {zreport} (target 8)")
print(f"  Mobile payments need EFD: {mobile} (target 5)")
