import json

extra = [
    {
        "instruction": "OSHA na WCF zote mbili zinahusu usalama wa wafanyakazi — kwa nini biashara inahitaji zote mbili?",
        "input": "",
        "output": "OSHA na WCF zinahusu usalama wa wafanyakazi lakini kwa njia tofauti: OSHA (regulator): inazuia ajali KABLA hazijatokea — kupitia kanuni za usalama, ukaguzi, na mafunzo. OSHA haihusishi pesa za bima — ni udhibiti wa tabia. WCF (insurance fund): inasaidia BAADA ya ajali kutokea — inalipa fidia kwa mfanyakazi aliyejeruhiwa au familia yake. WCF ni bima ya lazima. Mfano: mfanyakazi anaanguka kwa sababu biashara haikuwa na reli za usalama (ukiukwaji wa OSHA) na anapata maumivu (WCF inalipa fidia). Unahitaji zote mbili: OSHA kuzuia, WCF kulipa kama kutokukuwa kuzuia. Thibitisha na osha.go.tz na wcf.go.tz."
    },
    {
        "instruction": "OSHA inashughulikia pia sekta ya kilimo au ni viwanda tu?",
        "input": "",
        "output": "OSHA inashughulikia MAHALI POTE PA KAZI Tanzania Bara — ikiwa ni pamoja na sekta ya kilimo, viwanda, ofisi, maduka, hospitali, na kadhalika. Hakuna sekta iliyosamehewa na OSHA moja kwa moja. Hata shamba la kilimo lenye wafanyakazi wa kulipwa lina wajibu wa msingi wa OSHA. Hata hivyo, mahitaji yanaweza kutofautiana kulingana na sekta na hatari yake: Sekta za hatari zaidi (ujenzi, migodi, kemikali) zina mahitaji ya ziada. Sekta za hatari ndogo (ofisi) zina mahitaji ya msingi. Thibitisha na osha.go.tz kwa mahitaji maalum ya sekta yako."
    },
    {
        "instruction": "GN 487A na PAYE — je, mgeni anayekiuka GN 487A bado analazimishwa kulipa PAYE?",
        "input": "",
        "output": "Ndiyo — hata biashara inayokiuka GN 487A bado ina wajibu wa kodi. Ukiukwaji wa GN 487A ni kosa la biashara/uhamiaji — hauathiri wajibu wa kodi wa TRA. TRA inaweza kuhitaji: (1) Malipo ya PAYE, VAT, SDL, na kodi nyingine zilizokusanywa wakati biashara ilikuwa ikifanya kazi (hata kama ilikuwa haramu); (2) TRA haitoi msamaha wa kodi kwa sababu biashara ilikuwa haramu. Mgeni anayefungwa kwa GN 487A bado anaweza kukabiliwa na madeni ya kodi ya TRA pamoja na adhabu ya GN 487A. Kwa hivyo mgeni ana tatizo mbili tofauti: GN 487A na kodi za TRA. Thibitisha na Idara ya Uhamiaji na TRA."
    },
    {
        "instruction": "Mtu anayetoa taarifa (whistleblower) kuhusu mgeni anayekiuka GN 487A — ana ulinzi wowote?",
        "input": "",
        "output": "GN 487A haisemi wazi juu ya ulinzi wa whistleblowers. Hata hivyo, Tanzania ina sheria ya jumla ya ulinzi wa whistleblowers katika mazingira fulani. Mtu anayetoa taarifa kuhusu ukiukwaji wa GN 487A kwa Idara ya Uhamiaji au polisi anaweza: (1) Kutoa taarifa kwa siri (anonymous tip) kwa polisi au Idara ya Uhamiaji; (2) Kuthibitisha kwa maandishi kwa Idara ya Uhamiaji. Hata hivyo, ulinzi rasmi wa kisheria dhidi ya kulipizwa kisasi kwa GN 487A peke yake haujabainishwa wazi. Thibitisha na Idara ya Uhamiaji na wakili wa kisheria kwa hali yako maalum."
    },
    {
        "instruction": "Mtu alilalamika NSSF kwa mwajiri wake ambaye hakumlipa — NSSF inafanya nini?",
        "input": "",
        "output": "NSSF ina uwezo wa kuchunguza malalamiko ya wafanyakazi kuhusu mwajiri asiye kulipa michango: (1) NSSF inachunguza rekodi za mwajiri — wanakagua michango iliyowasilishwa dhidi ya wafanyakazi waliopo; (2) Kama uthibitisho unakutwa — NSSF inatoa notisi ya malipo kwa mwajiri; (3) Kama mwajiri halipi — NSSF inaweza kuchukua hatua za kisheria ikiwa ni pamoja na madai ya mahakama; (4) Wakurugenzi wa kampuni wanaweza kushikiliwa kibinafsi. Mfanyakazi ana haki ya: kulalamika moja kwa moja kwa NSSF (nssf.or.tz), kulalamika kwa Mahakama ya Kazi (Labour Court), au kupitia Mkurugenzi wa Kazi (Director of Labour). Thibitisha na nssf.or.tz."
    },
    {
        "instruction": "Biashara ya mgeni imekwishakamatwa na GN 487A — mnunuzi wa biashara (Mtanzania) anaweza kuendelea nayo?",
        "input": "",
        "output": "Hali hii ni ngumu ya kisheria: kama Mtanzania ananunua biashara iliyokuwa ya mgeni na kuendelea nayo WENYEWE (si kwa mgeni kudhibiti), na anaendesha shughuli halali (nje ya orodha ya 15 au yeye mwenyewe kama Mtanzania), GN 487A haihusiki na Mtanzania. Mtanzania anaweza kufanya biashara yoyote katika orodha ya 15. Hata hivyo: (1) Madeni ya zamani ya biashara (kodi, NSSF, n.k.) yanaweza kubaki na biashara; (2) Kama mgeni bado anadhibiti 'nyuma ya pazia' — bado ni ukiukwaji. Thibitisha na wakili wa biashara na Idara ya Uhamiaji kwa hali yako maalum."
    },
    {
        "instruction": "GN 487A na usajili wa TIC (Tanzania Investment Centre) — je, mwekezaji wa kigeni mwenye TIC anaweza kufanya biashara ya rejareja?",
        "input": "",
        "output": "Hapana — usajili wa TIC (Tanzania Investment Centre) unaruhusu wawekezaji wa kigeni kuwekeza katika sekta zilizobainishwa (kama kilimo, viwanda, utalii) kwa masharti maalum. Lakini biashara ya rejareja, saluni, ukarabati wa simu, na shughuli zingine 14 za GN 487A hazijaidhinishwa na TIC kwa wageni — hazipo katika orodha ya sekta zinazoruhusiwa na TIC kwa wawekezaji wa kigeni. GN 487A na TIC ni mifumo miwili tofauti: TIC inasimamia uwekezaji mkubwa katika sekta maalum; GN 487A inazuia shughuli ndogo ndogo kwa wageni wote. Thibitisha na TIC (tic.go.tz) na Idara ya Uhamiaji."
    },
    {
        "instruction": "Nchi mbili zinazo DTA na Tanzania — mgeni kutoka nchi hiyo ana msamaha wa GN 487A?",
        "input": "",
        "output": "Hapana — Double Taxation Agreements (DTA) ni makubaliano ya KODI TU — yanazuia kulipwa kodi mara mbili kwa nchi mbili. Hazina uhusiano wowote na haki za biashara chini ya GN 487A. Mgeni kutoka nchi yenye DTA na Tanzania bado anakabiliwa na GN 487A kikamilifu kwa shughuli zote 15 zilizokatazwa. DTA haizungumzii haki za biashara, uraia, wala kibali cha kufanya shughuli fulani. Kwa hiyo hata mgeni kutoka Uingereza, India, au Marekani (nchi zenye DTA na Tanzania) — bado ana vizuizi vya GN 487A. Thibitisha na Idara ya Uhamiaji."
    },
    {
        "instruction": "Mkanda wa biashara kwenye mtandao (online store) unaomilikiwa na mgeni — GN 487A inasema nini?",
        "input": "",
        "output": "Online store ya rejareja inayomilikiwa na mgeni Tanzania inakabiliwa na GN 487A kwa sababu: (1) Biashara ya rejareja (orodha ya 1) imezuiwa kwa wageni — nje ya mtandao au mtandaoni; (2) GN 487A inazingatia MMILIKI wa biashara, si eneo la biashara au njia ya kuuza. Online store inayofikia wateja wa Tanzania na inayomilikiwa na mgeni anayeishi Tanzania inakiuka GN 487A. Kama mmiliki yuko nje ya Tanzania kabisa na hafikii Tanzania moja kwa moja — hali inaweza kuwa ngumu kisheria. Thibitisha na Idara ya Uhamiaji na wakili wa biashara."
    },
    {
        "instruction": "Biashara imesajiliwa kwa jina la mwanachama wa kwanza wa SACCOS — mgeni anayenufaika ni tatizo la GN 487A?",
        "input": "",
        "output": "Ndiyo — GN 487A inazingatia MNUFAIKA (beneficiary) wa kweli wa biashara, si tu jina katika hati za kisheria. Kama mgeni anatonufaika na biashara, kupokea faida, au kudhibiti maamuzi — hata kama biashara imesajiliwa chini ya jina la mwanachama wa SACCOS au mtu mwingine — hii inaweza kuonekana kama ukiukwaji. Idara ya Uhamiaji na mahakama wanaweza kuchunguza 'beneficial ownership' — nani anafaidika kweli kweli. Hii inaitwa ukiukwaji wa 'substantive' bila kujali 'formal structure'. Thibitisha na wakili wa biashara na Idara ya Uhamiaji."
    },
    {
        "instruction": "PAYE ya mfanyakazi mwenye mshahara wa TZS 300,000 kwa mwezi — inakokotolewa vipi?",
        "input": "",
        "output": "Mfanyakazi mwenye mshahara wa TZS 300,000/mwezi: Band 1 (0%): TZS 270,000 → kodi = TZS 0. Ziada: TZS 300,000 − TZS 270,000 = TZS 30,000. Band 2 (8%): TZS 30,000 × 8% = TZS 2,400. PAYE ya mwezi = TZS 2,400. Hakuna punguzo la kibinafsi (personal relief) tofauti — kizingiti cha 0% (TZS 270,000) NDIYO punguzo la ufanisi. Kwa hivyo mfanyakazi mwenye mshahara wa TZS 300,000 analipa PAYE ya TZS 2,400/mwezi tu — kiasi kidogo kwa sababu ana mshahara mdogo unaopita kidogo mstari wa TZS 270,000. Thibitisha na TRA (tra.go.tz)."
    },
    {
        "instruction": "PAYE ya mfanyakazi mwenye mshahara wa TZS 1,200,000 kwa mwezi — inakokotolewa vipi?",
        "input": "",
        "output": "Mfanyakazi mwenye mshahara TZS 1,200,000/mwezi — hesabu ya PAYE: Band 1 (0%): TZS 270,000 → kodi = TZS 0. Band 2 (8%): TZS 250,000 (yaani TZS 520,000−270,000) × 8% = TZS 20,000. Band 3 (20%): TZS 240,000 (yaani TZS 760,000−520,000) × 20% = TZS 48,000. Band 4 (25%): TZS 240,000 (yaani TZS 1,000,000−760,000) × 25% = TZS 60,000. Band 5 (30%): TZS 200,000 (yaani TZS 1,200,000−1,000,000) × 30% = TZS 60,000. JUMLA ya PAYE = 0 + 20,000 + 48,000 + 60,000 + 60,000 = TZS 188,000/mwezi. Thibitisha na TRA (tra.go.tz)."
    },
    {
        "instruction": "Mgeni ana leseni yote za biashara kutoka Halmashauri — hii inamlinda dhidi ya GN 487A?",
        "input": "",
        "output": "Hapana — leseni ya biashara ya Halmashauri ni idhini ya kufanya biashara katika eneo maalum — si idhini ya kufanya biashara yoyote bila kizuizi. GN 487A ni sheria ya kitaifa inayopita zaidi ya Halmashauri — Halmashauri haiwezi kutoa msamaha wa GN 487A. Hata kama Halmashauri imetoa leseni kwa mgeni kwa duka la rejareja — GN 487A bado inazuia. Leseni ya Halmashauri na GN 487A ni mifumo miwili inayofanya kazi kwa pamoja: lazima uzingatie ZOTE. Kwa hivyo leseni ya Halmashauri haitoshi kulinda dhidi ya GN 487A. Thibitisha na Idara ya Uhamiaji."
    },
    {
        "instruction": "Mfanyakazi wa kigeni mwenye Class B permit anaweza kufanya kazi katika biashara ya rejareja inayomilikiwa na Mtanzania?",
        "input": "",
        "output": "GN 487A inalenga WAMILIKI na WADHIBITI wa biashara — si wafanyakazi wa kawaida. Mgeni mwenye Class B Residence Permit (kwa ajira) anayefanya kazi kama mwajiriwa wa kawaida (si mmiliki) katika biashara inayomilikiwa na Mtanzania — GN 487A haihusiki moja kwa moja na hali yake kama mwajiriwa. Hata hivyo, Class B permit lazima iwe halisi na iidhinishe kazi katika sekta husika, na mwajiri Mtanzania lazima apate idhini ya kuajiri mgeni (immigration quota). Kama hana Class B permit halisi — ni ukiukwaji wa sheria nyingine ya uhamiaji (si GN 487A). Thibitisha na Idara ya Uhamiaji na Wizara ya Kazi."
    },
    {
        "instruction": "NSSF inaweza kukatalia mafao kama mfanyakazi hakuchangia miezi 180?",
        "input": "",
        "output": "Ndiyo — pensheni ya uzeeni ya NSSF inahitaji angalau miezi 180 (miaka 15) ya michango. Kama mfanyakazi ana miezi 100 tu ya michango na aناfikia umri wa kustaafu — hatapata pensheni kamili. Katika hali hiyo, NSSF inaweza: (1) Kulipa kiasi kidogo cha mafao kama lump sum (malipo moja ya wakati mmoja) badala ya pensheni ya kila mwezi — hii inategemea NSSF Act; (2) Kusubiri hadi mfanyakazi anapofikia miezi 180 (kama bado anafanya kazi). Kwa mfanyakazi aliyeachishwa kazi kabla ya miezi 180 — anashauriwa kuwasiliana na NSSF moja kwa moja kwa mwongozo. Thibitisha na nssf.or.tz."
    },
    {
        "instruction": "Wakati mwajiri anakusanya PAYE na hatuitumi TRA — mfanyakazi anapoteza kitu gani?",
        "input": "",
        "output": "Mfanyakazi HUPOTEZA CHOCHOTE kwa upande wa PAYE ikiwa TRA haijapata pesa — kwa sababu PAYE ni kodi ya serikali, si akiba ya mfanyakazi. Hata hivyo, mfanyakazi anapoteza: (1) Ulinzi wa kisheria — kama TRA ilichunguza na kugundua PAYE haijalipwa, mfanyakazi anaweza kukabiliwa na maswali (hata kama pesa alishalipiwa na mwajiri wa kukata); (2) Uthibitisho wa malipo — pay slips zinazonyesha PAYE iliyokatwa lakini TRA haijapata. Mwajiri ndiye ana jukumu la KUTUMA pesa — si mfanyakazi. Mfanyakazi anaweza kulalamika kwa TRA au Mahakama ya Kazi. Thibitisha na TRA (tra.go.tz) na Wizara ya Kazi."
    },
    {
        "instruction": "WCF inafunika magonjwa ya kazini — mfanyakazi anayepata ugonjwa kutokana na kazi anafanyaje?",
        "input": "",
        "output": "Mfanyakazi aliyepata ugonjwa wa kazini (occupational disease) anachukua hatua hizi: (1) Pata utambuzi wa daktari unaothibitisha ugonjwa unatokana na kazi; (2) Mwajiri alazimike kutoa taarifa WCF ndani ya siku 7 za kazi baada ya utambuzi; (3) Daktari wa WCF anakagua na kuthibitisha kama ugonjwa unatokana na hali ya kazi; (4) Kama unathibitishwa — WCF inalipa fidia ya matibabu na/au fidia ya kipato ikiwa mfanyakazi hawezi kufanya kazi. Magonjwa yanayofunikwa ni pamoja na: ugonjwa wa mapafu kutokana na vumbi, poisoning ya kemikali, na magonjwa mengine yanayotambulika ya kazini. Thibitisha na wcf.go.tz."
    },
    {
        "instruction": "Mwajiri hana WCF — mfanyakazi aliyeumia kazini anafanyaje?",
        "input": "",
        "output": "Kama mwajiri hakusajili WCF (ukiukwaji wa sheria), mfanyakazi aliyeumia ana haki za kisheria bado: (1) Anapaswa kutoa taarifa kwa WCF moja kwa moja (WCF inaweza kuchunguza na kumfuatilia mwajiri); (2) WCF ina uwezo wa kudai fidia kutoka kwa mwajiri moja kwa moja hata kama mwajiri hakusajili — mwajiri anaweza kulazimishwa kulipa; (3) Mfanyakazi anaweza kufungua kesi ya kisheria kwa Mahakama ya Kazi dhidi ya mwajiri kwa kutofuata sheria ya WCF. Mwajiri asiyesajili WCF ana hatari ya: madai ya fidia, faini, na mashtaka ya kisheria. Thibitisha na wcf.go.tz na Mahakama ya Kazi."
    },
    {
        "instruction": "PAYE, SDL, NSSF, WCF — vyote vinalipwa tarehe 7 ya mwezi unaofuata?",
        "input": "",
        "output": "Si vyote vina tarehe sawa: PAYE → TRA: tarehe 7 ya mwezi unaofuata (tarehe ngumu — 7th); SDL → TRA: tarehe 7 ya mwezi unaofuata (pamoja na PAYE kwa kawaida); WHT → TRA: siku 7 baada ya mwisho wa mwezi (si tarehe 7 maalum); NSSF: tarehe ya mwisho wa mwezi unaofuata (si lazima 7th — angalia NSSF moja kwa moja); WCF: malipo ya mwezi yanafanywa ndani ya mwezi huo au unaofuata (angalia WCF kwa tarehe halisi); VAT → TRA: tarehe 20 ya mwezi unaofuata. Kwa hivyo ratiba ya malipo ni: 7th (PAYE+SDL+WHT), mwisho wa mwezi (NSSF), 20th (VAT). Thibitisha na TRA (tra.go.tz) na taasisi husika kwa tarehe za sasa."
    },
    {
        "instruction": "Wakala wa mali isiyohamika (real estate agent) anayepata commission — anapaswa kusajili VAT?",
        "input": "",
        "output": "Wakala wa mali isiyohamika anayepokea commission kwa huduma za udalali (brokerage services) anakabiliwa na: (1) Kama mapato ya commission yanazidi TZS 200M/mwaka au TZS 100M/miezi 6 → lazima asajili VAT na atoe tax invoice; (2) Kama ni mwanachama wa taaluma inayolazimishwa (kama Valuers Registration Board) → anaweza kulazimika kusajili VAT hata bila kufika kizingiti. Commission yenyewe si mali isiyohamika — ni huduma ya udalali inayopaswa kulipwa VAT (18%) kama amefika kizingiti. Thibitisha na TRA (tra.go.tz) na Valuers Registration Board Tanzania."
    },
    {
        "instruction": "Mgeni ana biashara ya boda boda 5 zilizosajiliwa kwa jina lake — je, adhabu ya GN 487A ni mara moja au kwa kila boda boda?",
        "input": "",
        "output": "GN 487A inazuia kufanya biashara ya boda boda kwa mgeni. Kwa boda boda 5 zilizosajiliwa kwa jina lake — hii ni biashara moja ya usafirishaji (hata kama vifaa ni 5) au inaweza kuchukuliwa kama vitendo vingi vya ukiukwaji. Kwa kawaida: ikiwa biashara ni moja (kampuni moja ya usafirishaji yenye boda boda 5) — kesi moja ya GN 487A; ikiwa kila boda boda ina usajili tofauti kama biashara tofauti — vinaweza kuwa vitendo tofauti. Korti itaamua — lakini adhabu ya chini ni TZS milioni 10 kwa kila kosa, kufutwa kwa visa ni lazima. Thibitisha na Idara ya Uhamiaji na wakili wa biashara."
    },
    {
        "instruction": "SDL inaanza tarehe gani kwa biashara mpya — siku ya kwanza ya kuajiri wafanyakazi 10 au mwezi unaofuata?",
        "input": "",
        "output": "SDL inaanza MWEZI HULE WA KUFIKIA wafanyakazi 10 au zaidi — si mwezi unaofuata. Kwa biashara mpya: ukiajiri mfanyakazi wa 10 mwezi wa Machi, SDL inaanza Machi hiyo hiyo (mwezi wa kufikia 10). Malipo ya SDL ya Machi yanawasilishwa TRA ifikapo 7 Aprili. Hata kama uliajiri mfanyakazi wa 10 siku ya mwisho ya Machi — SDL ya Machi bado inatakiwa. Hii ni kanuni ya 'mwezi mzima' — sio pro-rated kwa siku za kufanya kazi. Kwa hivyo makampuni mapya yanaelewa kwamba mara wanajiri mfanyakazi wa 10, SDL inaanza mara moja. Thibitisha na TRA (tra.go.tz)."
    },
    {
        "instruction": "Je, OSHA inashughulikia usalama wa wateja wa biashara au wafanyakazi peke yake?",
        "input": "",
        "output": "OSHA (Occupational Safety and Health Authority) inalenga hasa USALAMA WA WAFANYAKAZI katika mazingira ya kazi — si usalama wa wateja wa biashara moja kwa moja. Hata hivyo: (1) Kama mazingira hatarishi ya kazi pia yanaathiri wateja (kama duka lenye nguzo zinazoweza kuanguka), OSHA inaweza kushughulikia; (2) Usalama wa wateja kwa bidhaa na huduma unashughulikiwa na TBS (Tanzania Bureau of Standards) na TMDA (kwa dawa na vifaa vya afya); (3) Ajali za wateja katika eneo la biashara zinaweza kuhusisha wajibu wa kiraia (civil liability) wa mwajiri. Kwa usalama kamili: OSHA (wafanyakazi), TBS/TMDA (bidhaa), na bima ya biashara (wateja). Thibitisha na osha.go.tz."
    }
]

with open("datasets/tier1a/raw_sources/batch_009_checkpoints/checkpoint_006.jsonl", "a", encoding="utf-8") as f:
    for p in extra:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

with open("datasets/tier1a/raw_sources/raw_pairs_batch_009.jsonl", "a", encoding="utf-8") as f:
    for p in extra:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

count6 = sum(1 for l in open("datasets/tier1a/raw_sources/batch_009_checkpoints/checkpoint_006.jsonl", encoding="utf-8") if l.strip())
total = sum(1 for l in open("datasets/tier1a/raw_sources/raw_pairs_batch_009.jsonl", encoding="utf-8") if l.strip())
print(f"Chunk 6: {count6} pairs")
print(f"Main total: {total}")
