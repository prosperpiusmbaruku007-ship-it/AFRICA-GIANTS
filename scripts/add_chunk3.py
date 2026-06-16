import json

extra = [
    {
        "instruction": "Kampuni iliyofutwa orodha BRELA — direkta wake anaweza kuanzisha kampuni mpya haraka?",
        "input": "",
        "output": "Wakurugenzi wa kampuni iliyofutwa orodha wanaweza kuanzisha kampuni mpya, lakini wanapaswa kuzingatia: (1) Madeni ya kampuni iliyofutwa orodha yanabaki — wadai wanaweza kufuatilia wakurugenzi kibinafsi kwa vitendo vya ulaghai; (2) Madeni ya kodi ya TRA yanaweza kufuatwa hadi kwa wakurugenzi kibinafsi; (3) BRELA inaweza kuuliza historia ya kampuni za awali wakati wa usajili mpya. Kampuni mpya si njia ya kufuta madeni ya kampuni ya zamani. Thibitisha na wakili wa biashara."
    },
    {
        "instruction": "Je, mwanachama mdogo wa kampuni (hisa 5%) anaweza kushikiliwa kwa madeni ya kampuni?",
        "input": "",
        "output": "Kwa kawaida hapana. Hii ndiyo faida ya limited company: wanahisa wanashikiliwa tu kwa kiasi cha hisa walizowekeza. Mwanachama mwenye hisa 5% anashikiliwa tu kwa thamani ya hisa hizo — si kwa madeni yote ya kampuni. Hata hivyo, kama mwanachama huyo ni mkurugenzi pia na alifanya vitendo vya ulaghai au alikuwa na dhamana ya kibinafsi — ndipo anaweza kushikiliwa zaidi. Hii ndiyo sababu limited liability ni faida kubwa ya kampuni ya hisa. Thibitisha na wakili wa biashara."
    },
    {
        "instruction": "Kampuni ya kigeni inayoingia Tanzania — inahitaji nini kutoka BRELA?",
        "input": "",
        "output": "Kampuni ya kigeni inayofanya kazi Tanzania inapaswa kusajili TAWI (branch) kwa BRELA chini ya Sehemu XII ya Companies Act. Ada za tawi la kigeni: USD 750 (nakala iliyothibitishwa ya hati za kampuni mama) + USD 220 (kufungua faili na kusajili hati). Faini ya kuchelewa kwa tawi la kigeni ni USD 25/mwezi. Mbadala: kuanzisha kampuni mpya ya Tanzania (subsidiary) badala ya tawi. Tawi na kampuni ya Tanzania zina mifumo tofauti ya kisheria na kodi. Thibitisha na BRELA.go.tz na wakili wa biashara."
    },
    {
        "instruction": "Patent ya uvumbuzi wangu — BRELA inasimamia au ni ARIPO ya kikanda?",
        "input": "",
        "output": "Tanzania ina chaguo mbili za hataza (patent): (1) BRELA ya Tanzania peke yake — kwa ulinzi wa Tanzania Bara tu; (2) ARIPO (African Regional Intellectual Property Organization) — kwa ulinzi wa nchi nyingi za Afrika Mashariki kwa jibu moja. BRELA ndiyo mamlaka ya ndani ya Tanzania kwa hataza, trademarks, industrial designs, na utility models. COSOTA (tofauti na BRELA) inashughulikia copyrights peke yake. Thibitisha na BRELA (brela.go.tz) au ARIPO kwa ulinzi wa kikanda."
    },
    {
        "instruction": "Trademark iliyosajiliwa BRELA — inalindwa Tanzania Bara tu au Zanzibar pia?",
        "input": "",
        "output": "Trademark iliyosajiliwa BRELA inalinda Tanzania Bara peke yake — BRELA ni mamlaka ya Tanzania Bara tu. Zanzibar ina mfumo wake tofauti wa kisheria. Kwa ulinzi wa kikanda (nchi nyingi), unaweza kutumia ARIPO inayojumuisha Tanzania Bara na nchi nyingine. Kwa biashara inayofanya kazi Zanzibar pia, wasiliana na mamlaka za Zanzibar kuhusu ulinzi wa IP. Thibitisha na BRELA (brela.go.tz)."
    },
    {
        "instruction": "Mgeni mwenye pasipoti mbili (raia wa Tanzania na nchi nyingine) — GN 487A inamhusu?",
        "input": "",
        "output": "Kama mtu ana uraia wa Tanzania (halisi, si wa ulaghai), kisheria yeye ni raia wa Tanzania na GN 487A haihusiki. Hata hivyo, kama ana pasipoti mbili lakini hajaomba na kupata uraia wa Tanzania rasmi — bali anatumia pasipoti ya kigeni tu — bado anachukuliwa kama mgeni kwa madhumuni ya GN 487A. Hali ya uraia mbili (dual nationality) na uhusiano wake na GN 487A inaweza kuwa ngumu kisheria. Thibitisha na Idara ya Uhamiaji na wakili wa biashara."
    },
    {
        "instruction": "GN 487A ina mkakati wa grace period kwa wageni waliokuwa na biashara kabla ya Julai 2025?",
        "input": "",
        "output": "Hakuna grace period rasmi iliyotangazwa kisheria katika GN 487A. Sheria ilianza mara moja tarehe 28 Julai 2025. Kampeni ya utekelezaji ilianza 11 Septemba 2025 — lakini hiyo ilikuwa utekelezaji wa kwanza, si grace period rasmi. Wageni waliokuwa na biashara katika orodha ya 15 tangu 28 Julai 2025 wamekuwa wakikosea sheria — bila kujali kulikuwa na kampeni au la. Thibitisha na Idara ya Uhamiaji."
    },
    {
        "instruction": "Mgeni anasimamia tu (manager) biashara ya Mtanzania — si mmiliki — GN 487A bado inahusika?",
        "input": "",
        "output": "GN 487A inazuia raia wa kigeni kufanya biashara au kuendesha shughuli katika orodha ya 15. Kusimamia biashara kama mkurugenzi mtendaji au meneja mkuu — hata bila umiliki — kunaweza kuchukuliwa kama kufanya biashara kisheria. Idara ya Uhamiaji wanaweza kuchunguza mtu anayedhibiti operesheni halisi ya biashara, si tu jina katika hati. Kama mgeni ni meneja lakini anadhibiti maamuzi yote — hali hii iko katika hatari ya kisheria. Thibitisha na wakili wa biashara na Idara ya Uhamiaji."
    },
    {
        "instruction": "BRELA inaweza kufuta kampuni bila taarifa ya awali?",
        "input": "",
        "output": "BRELA hufuata mchakato wa kisheria kabla ya kufuta orodha kampuni: (1) Kutuma notisi rasmi kwa kampuni (barua au gazeti rasmi); (2) Kutoa muda wa kujibu au kuwasilisha annual returns zilizokosekana; (3) Kama hakuna jibu — kufuta orodha rasmi. Kampuni zinapaswa kuhakikisha BRELA ina anwani sahihi ya mawasiliano — kama anwani imebadilika na kampuni haijapokea notisi, kufutwa kunaweza kutokea bila ujuzi wa kampuni. Thibitisha na BRELA.go.tz mara kwa mara."
    },
    {
        "instruction": "BRELA na leseni ya biashara ya halmashauri — ni vitu viwili tofauti?",
        "input": "",
        "output": "Ndiyo — ni vitu viwili tofauti kabisa. BRELA (Business Registrations and Licensing Agency): inakusajili kisheria kama chombo (kampuni, biashara ya jina) — hii ni usajili wa taifa. LESENI YA BIASHARA ya Halmashauri: inakupa ruhusa ya kufanya biashara katika eneo maalum — inatoka Halmashauri ya Wilaya au Manispaa na inafanyiwa upya kila mwaka. Unahitaji VYOTE VIWILI: BRELA (kitaifa) + Leseni ya Halmashauri (ya ndani). Pia kuhitaji TIN ya TRA, NSSF, WCF, na OSHA. Thibitisha na BRELA.go.tz na Halmashauri yako."
    },
    {
        "instruction": "GN 487A inaathiri pia NGO na mashirika ya kimataifa yanayofanya kazi Tanzania?",
        "input": "",
        "output": "GN 487A inalenga biashara ya kibiashara (commercial activities) katika orodha ya 15. NGO na mashirika ya kimataifa yanayofanya kazi kwa madhumuni ya misaada au maendeleo (si faida) yanafuata mfumo tofauti wa kisheria — NGO Act — si GN 487A moja kwa moja. Hata hivyo, kama NGO inafanya shughuli za kibiashara zinazoingia katika orodha ya 15 kwa faida — hali hiyo inaweza kuchunguzwa. Thibitisha na wakili wa kisheria wa sekta ya NGO na Idara ya Uhamiaji."
    },
    {
        "instruction": "Biashara ya jina la familia — kama baba anafariki, mtoto anaweza kuendelea?",
        "input": "",
        "output": "Biashara ya jina (sole trader) iliyosajiliwa kwa jina la baba inakufa kisheria anapokufa baba — mtoto hawezi kurithi usajili wa BRELA moja kwa moja. Mtoto anahitaji: (1) Kuanzisha usajili mpya wa biashara kwa jina lake au jina jipya; (2) Kuwasilisha hati za urithi (probate) na usajili mpya. Njia nzuri zaidi kwa biashara za familia: kuanzisha kampuni ya hisa — kampuni inaendelea hata mwanachama mmoja akifariki, hisa zinaweza kuhamishwa. Thibitisha na BRELA.go.tz na wakili wa biashara."
    },
    {
        "instruction": "Je, kampuni ya hisa ya Tanzania inaweza kumilikiwa 100% na mgeni?",
        "input": "",
        "output": "Ndiyo — sheria za uwekezaji Tanzania zinamlruhusu mgeni kumiliki hisa 100% katika kampuni nyingi za sekta. Hata hivyo, kuna vikwazo: (1) GN 487A inazuia shughuli katika orodha ya 15 — hata kama kampuni imesajiliwa Tanzania na kumilikiwa 100% na mgeni, kufanya shughuli hizo bado ni marufuku; (2) Sekta fulani (madini, ardhi, media) zina vikwazo vya umiliki wa kigeni; (3) Tanzania Investment Centre (TIC) inasimamia uwekezaji wa kigeni. Kwa sekta zilizoruhusiwa (viwanda, kilimo, utalii), umiliki 100% wa kigeni unawezekana. Thibitisha na TIC (tic.go.tz) na wakili wa biashara."
    },
    {
        "instruction": "Kama kampuni yangu imekuwa dormant (haifanyi biashara) kwa miaka 2 — bado inahitaji annual return BRELA?",
        "input": "",
        "output": "Ndiyo — kampuni iliyosajiliwa BRELA inahitaji kuwasilisha annual returns bila kujali kama inafanya biashara au la (dormant). Annual return inathibitisha kampuni bado ipo hai kisheria na inatoa taarifa za hali ya sasa. Kutokuwasilisha — hata kwa kampuni ya dormant — kunasababisha faini ya TZS 2,500/mwezi na hatimaye kufutwa orodha. Kama kampuni haifanyi kazi na hutaifufua, inashauriwa kuifuta rasmi (voluntary dissolution/winding up) ili kuepuka mkusanyiko wa faini. Thibitisha na BRELA.go.tz."
    },
    {
        "instruction": "Mgeni ana permit ya kufanya kazi (Class B) Tanzania — anaweza kufungua biashara yake mwenyewe?",
        "input": "",
        "output": "Hapana moja kwa moja. Class B Residence Permit ni kwa mtu AJIRIWA na kampuni halisi — si kwa kufanya biashara ya kujitegemea. Kama mgeni mwenye Class B anataka kufungua biashara yake mwenyewe, anahitaji Class A Residence Permit (kwa wawekezaji wa kujitegemea). Zaidi ya hayo, hata na Class A, kama biashara ipo katika orodha ya 15 za GN 487A — bado ni marufuku. Mgeni mwenye Class B anafanya kazi kwa mwajiri — si mwajiri mwenyewe. Thibitisha na Idara ya Uhamiaji na wakili wa biashara."
    },
    {
        "instruction": "BRELA inaweza kusimamisha biashara yangu bila hukumu ya mahakama?",
        "input": "",
        "output": "BRELA ina mamlaka ya kufuta orodha kampuni (deregistration) kwa kutokuwasilisha annual returns — lakini hii si kusimamisha biashara kwa vitendo. Kufutwa orodha kunamaanisha kampuni haipo kisheria — si polisi wanaokuja kufunga duka. Wakati kampuni imefutwa orodha: hawezi kuingia mikataba mipya kisheria; benki inaweza kugandamiza akaunti; wadai wanaweza kupinga shughuli. TRA inaweza kuomba mahakama isimamishe biashara kwa madeni ya kodi. Ili kuepuka hali hizi, wasilisha annual returns kwa wakati. Thibitisha na BRELA.go.tz."
    },
    {
        "instruction": "Nimesajili biashara BRELA lakini sijapata TIN bado — ninaweza kuanza kupokea malipo?",
        "input": "",
        "output": "Kisheria, kuanza kupokea malipo ya biashara bila TIN kunaweza kuwa tatizo la kodi. TIN (Taxpayer Identification Number) ya TRA inahitajika kwa shughuli zote za biashara za kodi — VAT, PAYE, SDL, na malipo ya kodi yoyote. Biashara nyingi za Tanzania zinahitaji TIN kwa: kufungua akaunti ya benki, kutoa invoice rasmi, kusajili EFD, na kuwasilisha marudisho ya kodi. BRELA inakusajili kisheria kama chombo — TRA inakusajili kwa kodi. Omba TIN haraka iwezekanavyo kupitia TRA (tra.go.tz au ofisi ya karibu). Thibitisha na TRA."
    },
    {
        "instruction": "Je, GN 487A inazuia mgeni kufundisha katika shule ya kibinafsi?",
        "input": "",
        "output": "Ufundishaji katika shule ya kibinafsi haujaorodheshwa wazi katika orodha ya 15 za GN 487A. Orodha ya 15 ni: rejareja, jumla, saluni, ukarabati simu, uhamishaji pesa, usafi, ushonaji, upigaji picha, usafirishaji mdogo, delivery, uchapishaji, udhibiti wadudu, mitumba, machinga, na boda boda/bajaj. Hata hivyo, mgeni anayefundisha anahitaji vibali sahihi vya kazi (Class B permit) na idhini ya Wizara ya Elimu. GN 487A peke yake haizuii ufundishaji — lakini sheria nyingine za vibali vya kazi zinatumika. Thibitisha na Wizara ya Elimu na Idara ya Uhamiaji."
    },
    {
        "instruction": "Mgeni ana hisa 49% na Mtanzania ana 51% katika kampuni ya rejareja — GN 487A inasema nini?",
        "input": "",
        "output": "Hali hii ni ya hatari ya kisheria. GN 487A inazuia raia wa kigeni kufanya biashara au kushiriki kwa kiasi kinachohusika katika shughuli 15 zilizokatazwa. Kuwa na hisa 49% katika kampuni ya rejareja kunaweza kuchukuliwa kama ushiriki mkubwa wa biashara. Mgeni ana hisa karibu nusu — anaweza kuchomeka maamuzi na faida. Idara ya Uhamiaji na mahakama wanaweza kuangalia zaidi ya usambazaji wa hisa na kuchunguza udhibiti wa kweli. Hali hii inahitaji mshauri wa kisheria wa biashara na Idara ya Uhamiaji moja kwa moja. Thibitisha na wakili wa biashara."
    }
]

with open("datasets/tier1a/raw_sources/batch_009_checkpoints/checkpoint_003.jsonl", "a", encoding="utf-8") as f:
    for p in extra:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

with open("datasets/tier1a/raw_sources/raw_pairs_batch_009.jsonl", "a", encoding="utf-8") as f:
    for p in extra:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

count3 = sum(1 for l in open("datasets/tier1a/raw_sources/batch_009_checkpoints/checkpoint_003.jsonl", encoding="utf-8") if l.strip())
total = sum(1 for l in open("datasets/tier1a/raw_sources/raw_pairs_batch_009.jsonl", encoding="utf-8") if l.strip())
print(f"Chunk 3: {count3} pairs")
print(f"Main total: {total}")
