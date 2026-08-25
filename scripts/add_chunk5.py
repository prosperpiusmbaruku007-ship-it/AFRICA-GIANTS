import json

extra = [
    {
        "instruction": "Kampuni yangu inanunua bidhaa na baadaye inalipa kwa awamu — withholding inatokea lini?",
        "input": "",
        "output": "VAT withholding inatokea wakati malipo yanafanywa — kila awamu ya malipo inachukua 3% (bidhaa) au 6% (huduma) ya kiasi kinacholipwa. Kwa mfano: mlipaji hulipa TZS 1,000,000 mwezi wa kwanza na TZS 500,000 mwezi wa pili: withholding ya mwezi 1 = 3% × 1,000,000 = TZS 30,000; withholding ya mwezi 2 = 3% × 500,000 = TZS 15,000. Kila awamu ina withholding certificate yake. Muuzaji anapokea kila malipo pungufu ya withholding. Thibitisha na TRA (tra.go.tz) kwa mwongozo wa malipo ya awamu."
    },
    {
        "instruction": "Ninalipa kwa muuzaji wa bidhaa TZS 1,000,000 — ni kiasi gani cha pesa anachopata baada ya withholding?",
        "input": "",
        "output": "Kama wewe ni qualifying buyer wa VAT na unanunua bidhaa: Withholding ya VAT = 3% ya bei (kabla ya VAT au ya bei yenye VAT — mwongozo wa TRA unathibitisha) ya TZS 1,000,000. Withholding = 3% × 1,000,000 = TZS 30,000. Muuzaji anapata: TZS 1,000,000 − TZS 30,000 = TZS 970,000. Kiasi kilichokatwa (TZS 30,000) unatuma TRA pamoja na withholding certificate. Muuzaji bado analazimika kuwasilisha VAT return yake — lakini TZS 30,000 tayari ipo TRA kwa niaba yake. Thibitisha na TRA (tra.go.tz) kwa hesabu sahihi."
    },
    {
        "instruction": "Kampuni inayosambaza bidhaa nyingi kwa serikali — inaweza kusajiliwa kama qualifying buyer wenyewe?",
        "input": "",
        "output": "Kampuni ya kibinafsi inayosambaza bidhaa kwa serikali HAIWEZI kujisajilisha mwenyewe kama qualifying buyer. Qualifying buyers ni: (1) Wizara ya Fedha moja kwa moja; (2) Taasisi za serikali zinazoweka mapato yao; (3) Mtu/taasisi iliyoteuliwa na Commissioner General wa TRA kwa tangazo rasmi. Kampuni ya kibinafsi (hata msambazaji mkubwa wa serikali) haijateuliwa moja kwa moja. Hata hivyo, kama kampuni inauza bidhaa kwa wizara — WIZARA (qualifying buyer) ndiyo inayokata withholding, si kampuni ya kibinafsi. Thibitisha na TRA (tra.go.tz)."
    },
    {
        "instruction": "Muuzaji wa VAT anayenunua bidhaa kwa gharama na kuziuza — je, anatumia VAT withholding au output/input VAT?",
        "input": "",
        "output": "Muuzaji wa VAT anafanya kazi na mfumo wa kawaida wa output/input VAT: Output VAT: anapotoza VAT (18%) kwa wateja wake — hii ni 'deni' lake kwa TRA. Input VAT: anapokea VAT (18%) kwenye manunuzi yake — hii ni 'mkopo' wake dhidi ya deni. Kama muuzaji ni qualifying buyer: pia anachukua withholding (3%/6%) kutoka kwa wauzaji wake. Withholding iliyochukuliwa si sawa na input VAT — ni tofauti. Mfumo wa VAT kwa muuzaji: output VAT − input VAT = VAT inayolipwa TRA. Withholding inayochukuliwa inatumwa TRA tofauti. Thibitisha na TRA (tra.go.tz) kwa mwongozo maalum."
    },
    {
        "instruction": "Mzigo wa bidhaa unaoingia Tanzania kutoka nje — withholding ya VAT inatumika?",
        "input": "",
        "output": "VAT withholding (3%/6%) inalenga MAUZO YA NDANI ya Tanzania kati ya qualifying buyer na muuzaji wa Tanzania. Bidhaa zinazoingizwa kutoka nje zinalipa VAT ya forodha (customs VAT) wakati wa kuingia nchini — mfumo tofauti. Withholding ya VAT ya ndani haihusiki na mauzo ya forodha/import. Hata hivyo, baadaye muuzaji wa Tanzania anayezisambaza bidhaa hizo ndani ya nchi — mauzo ya ndani yanaweza kuwa na withholding kwa qualifying buyer. Thibitisha na TRA (tra.go.tz) kwa mwongozo maalum wa bidhaa za kuagiza na VAT."
    },
    {
        "instruction": "VAT withholding inatekelezwa na nani — TRA au qualifying buyer?",
        "input": "",
        "output": "VAT withholding INATEKELEZWA NA QUALIFYING BUYER — si TRA moja kwa moja. Mchakato: (1) Qualifying buyer (kama wizara) anafanya ununuzi wa bidhaa au huduma; (2) Anakata 3% (bidhaa) au 6% (huduma) ya VAT kutoka malipo; (3) Anatuma kiasi kilichokatwa TRA ndani ya muda uliowekwa; (4) Anatoa withholding certificate kwa muuzaji — siku ya muamala. TRA haihusiki moja kwa moja katika kila muamala wa withholding — inategemea qualifying buyer kufanya hii kwa niaba yake. TRA inakagua utiifu baadaye. Thibitisha na TRA (tra.go.tz)."
    },
    {
        "instruction": "VAT standard rate ni 18% — kama bei yangu ni TZS 100,000, VAT ni kiasi gani?",
        "input": "",
        "output": "Kwa bei ya TZS 100,000 na VAT ya 18%: VAT = 18% × TZS 100,000 = TZS 18,000. Bei ya jumla kwa mteja = TZS 100,000 + TZS 18,000 = TZS 118,000. Hii ni jinsi ya kuhesabu VAT kuongeza (VAT-exclusive price). Au kama bei tayari ina VAT (VAT-inclusive): VAT iliyofichwa = bei × 18/118 = TZS 118,000 × 18/118 = TZS 18,000. Matokeo ni sawa. VAT standard rate ya Tanzania ni 18% — imekuwa 18% tangu 2015. Thibitisha na TRA (tra.go.tz)."
    },
    {
        "instruction": "Input VAT yangu ya mwezi ni TZS 2,000,000 na output VAT ni TZS 1,500,000 — nifanye nini?",
        "input": "",
        "output": "Una hali ya VAT refund: output VAT (TZS 1,500,000) ni ndogo kuliko input VAT (TZS 2,000,000). Tofauti ya TZS 500,000 ni refund inayostahiki kutoka TRA. Jinsi ya kufanya: (1) Wasilisha VAT return yako ya kawaida tarehe 20 ya mwezi unaofuata ukionyesha tofauti ya refund; (2) Omba rasmi refund au uomba izidishiwe kwa miezi ijayo; (3) TRA itakagua madai — kuna taratibu za ukaguzi. Biashara za exports (zero-rated) mara nyingi zina input VAT zaidi — refund ni haki ya kawaida ya kisheria. TRA ina muda wa miezi 6 wa kisheria kukusaidia. Thibitisha na TRA (tra.go.tz)."
    },
    {
        "instruction": "Hoteli yangu inatoa huduma za mkutano (conference) — je, huduma hizo zinakata VAT?",
        "input": "",
        "output": "Ndiyo — huduma za mkutano (conference services) kama ukodishaji wa chumba cha mkutano, teknolojia ya mkutano, chakula cha mkutano, na kadhalika ni huduma zinazoweza kuwa na VAT. Kama hoteli imesajiliwa VAT, inatoza 18% VAT kwa huduma zote za mkutano. Wateja wa kampuni wanaoweza kudai input VAT wanapenda kupata tax invoice (risiti ya EFD na VAT) — kwa hivyo toa tax invoice sahihi. Kama mteja ni qualifying buyer — anaweza kukata withholding ya 6% ya VAT. Thibitisha na TRA (tra.go.tz) kuhusu VAT kwa huduma maalum za hoteli yako."
    },
    {
        "instruction": "Ninanunua bidhaa za chakula kutoka Tanzania — je, VAT inakatwa?",
        "input": "",
        "output": "Bidhaa za chakula Tanzania zina matibabu mbalimbali ya VAT kulingana na aina: Zero-rated (0% VAT): mazao ya kilimo ya msingi yasiyosindikwa (nafaka, mboga za mashamba); dawa za dawa; mauzo ya nje ya nchi (exports). Exempt (hazilipwi VAT): baadhi ya bidhaa maalum zilizoorodheshwa na sheria. Standard rate (18% VAT): chakula kilichosindikwa, bidhaa za chakula zilizopakiwa, na chakula kutoka migahawa na hoteli. Kama unanunua mazao mabichi kutoka mkulima si lazima VAT. Ukiwa unanunua chakula kilichosindikwa kutoka kampuni ya VAT — utalipa VAT 18%. Thibitisha na TRA (tra.go.tz) kwa orodha ya bidhaa."
    },
    {
        "instruction": "SDL — mwajiri anawasilisha fomu gani na wapi?",
        "input": "",
        "output": "SDL inawasilishwa kwa TRA pamoja na PAYE katika mfumo mmoja wa malipo ya kodi: Fomu: TRA Form PB/SD (au fomu ya sasa inayotumiwa na TRA — hii inaweza kubadilika); Mfumo: Kupitia portal ya TRA online (IDRAS — Integrated Domestic Revenue Administration System) au ofisi ya TRA ya karibu; Tarehe: 7 ya mwezi unaofuata; Taarifa muhimu: idadi ya wafanyakazi, jumla ya mishahara ya fedha, kiasi cha SDL (3.5% × mishahara). Malipo yanafanywa pia kupitia benki iliyoidhinishwa au mtandao. Kama una TIN, karibu una akaunti ya TRA online. Thibitisha na TRA (tra.go.tz) kwa fomu ya sasa."
    },
    {
        "instruction": "VAT inawasilishwa kwa mfumo gani — kila mwezi au kila mwaka?",
        "input": "",
        "output": "VAT inawasilishwa KILA MWEZI kwa biashara zilizosajiliwa VAT Tanzania. Hakuna chaguo la mwaka — ni kila mwezi bila kukosekana. Mfumo: VAT return ya mwezi uliopita inawasilishwa kabla ya tarehe 20 ya mwezi unaofuata. Kwa mfano: VAT ya Januari → iwasilishwe kabla ya 20 Februari. Hata kama hukufanya biashara yoyote mwezi fulani — bado lazima uwasilishe VAT return ya NIL (zero) kuonyesha TRA biashara ipo. Kutokuwasilisha — hata kwa mwezi wa sifuri — ni kosa la kodi. Thibitisha na TRA (tra.go.tz)."
    },
    {
        "instruction": "VAT inaathiri nani — mwuzaji au mnunuzi?",
        "input": "",
        "output": "Kimsingi VAT ni mzigo wa MNUNUZI (consumer) — analipa VAT juu ya bei ya bidhaa au huduma. Hata hivyo, mwuzaji aliyesajiliwa VAT ndiye MKUSANYAJI (collector) wa VAT kwa niaba ya TRA: Mwuzaji anakusanya VAT (18%) kutoka mnunuzi, anazidisha na input VAT (VAT alipolipa kwa manunuzi yake), na analipa NET VAT kwa TRA. Kwa hivyo: mwuzaji ni wakala wa ukusanyaji wa kodi kwa TRA — pesa si yake. Mnunuzi analipa VAT lakini kama ni biashara aliyosajiliwa VAT, anaweza kudai input VAT credit. Mlipaji wa mwisho wa VAT ni MTUMIAJI WA MWISHO (final consumer) asiyesajiliwa VAT. Thibitisha na TRA (tra.go.tz)."
    },
    {
        "instruction": "Biashara yangu ina mapato ya TZS 190M kwa mwaka. Mwaka ujao ninategemea TZS 210M — nisajili VAT lini?",
        "input": "",
        "output": "Usajili wa VAT unategemea mapato HALISI yaliyofikiwa, si matarajio ya baadaye. Kwa mwaka wa sasa (TZS 190M): chini ya kizingiti cha TZS 200M — bado hujafika, si lazima sasa. Hata hivyo, angalia kizingiti cha miezi 6 (rolling): kama mapato yako yoyote ya miezi 6 mfululizo yanazidi TZS 100M — lazima usajili. TZS 190M ÷ 12 × 6 = TZS 95M kwa wastani — karibu sana na kizingiti. Mwaka ujao ukifika TZS 200M — lazima usajili ndani ya siku 30 baada ya kufika kizingiti. Usajili wa mapema (voluntary) unaweza kufanywa wakati wowote kama unataka faida za VAT. Thibitisha na TRA (tra.go.tz)."
    },
    {
        "instruction": "SDL na NSSF — zinafanana vipi?",
        "input": "",
        "output": "SDL na NSSF zinafanana kwa kuwa zote ni malipo yanayohusiana na wafanyakazi — lakini ni tofauti kabisa: SDL (→ TRA): 3.5% ya mishahara ya fedha; MWAJIRI peke yake; inaenda mfuko wa mafunzo; kizingiti: wafanyakazi 10+. NSSF (→ NSSF Fund): 10% mwajiri + 10% mfanyakazi = 20% jumla; wote wanashiriki; inaenda mfuko wa pensheni; hakuna kizingiti cha idadi ya wafanyakazi. Tofauti muhimu: SDL ni mwajiri peke yake, NSSF ni mwajiri + mfanyakazi. SDL ni kwa waajiri wenye 10+ wafanyakazi; NSSF ni kwa waajiri WOTE. Vyote vinachangia usafi wa biashara lakini kwa madhumuni tofauti kabisa. Thibitisha na TRA na nssf.go.tz."
    },
    {
        "instruction": "Mwajiri anaweza kulipa SDL kabla ya mwisho wa mwezi badala ya tarehe ya 7?",
        "input": "",
        "output": "Ndiyo — mwajiri anaweza kulipa SDL kabla ya tarehe ya 7 ya mwezi unaofuata. Kulipa mapema ni halali kabisa na hakunakiliwa kama tatizo. Faida za kulipa mapema: (1) Unahakikisha hufikwi na muda wa dharura; (2) Unaepuka kuchelewa kutokana na matatizo ya benki au mfumo wa TRA; (3) Unaonyesha ushirikiano mzuri na TRA. Hakuna faida ya ziada ya kifedha kwa kulipa mapema (hakuna riba ya SDL kwa kulipa mapema). Tarehe ya 7 ni kikomo cha juu — si siku ya lazima ya kulipa. Thibitisha na TRA (tra.go.tz) kwa utaratibu wa malipo ya mapema."
    },
    {
        "instruction": "Ninaajiri intern (mwanafunzi wa mafunzo) bila mshahara — je, SDL inaathirika?",
        "input": "",
        "output": "Intern asiyepewa mshahara (bila malipo ya fedha) HAINGII SDL base kwa sababu mbili: (1) SDL inakokotolewa kwa MALIPO YA FEDHA — intern bila mshahara hana malipo; (2) Hali ya intern inaweza pia kumaanisha si mwajiriwa wa kisheria bali mwanafunzi. Hata hivyo, intern mwenye mshahara hata mdogo (posho ya usafiri ya fedha, au malipo yoyote ya pesa) anaingia SDL base na kuhesabiwa katika idadi ya wafanyakazi kwa kizingiti cha 10. Kama intern hana malipo yoyote ya fedha — haathiri SDL wala PAYE. Thibitisha na TRA (tra.go.tz) na Wizara ya Kazi kwa hali ya kisheria ya intern."
    },
    {
        "instruction": "Kampuni ya Tanzania inanunua programu (software license) kutoka kampuni ya nje ya nchi — kuna withholding yoyote?",
        "input": "",
        "output": "Malipo ya software license kwa kampuni ya kigeni yanaweza kuhusisha: (1) WHT (Withholding Tax) ya 15% kwa royalties — software licenses zinaweza kuchukuliwa royalties kisheria; (2) VAT withholding ya 6% kwa huduma — kama programu ni huduma ya kidijitali inayotolewa na mtu anayehitimu. Kwa kampuni ya Tanzania inayolipa kampuni ya kigeni: Ikiwa kampuni ya kigeni ina daftari la TRA — kawaida mfumo wa kawaida wa VAT unatumika. Ikiwa kampuni ya kigeni haina daftari la TRA — unaweza kulazimika kukaa na mfumo wa 'reverse charge' au withholding. Mada hii ni ngumu — thibitisha na TRA (tra.go.tz) na mshauri wa kodi wa kimataifa."
    },
    {
        "instruction": "VAT kwa huduma za ujenzi (construction services) — ni 18% ya kawaida?",
        "input": "",
        "output": "Ndiyo — huduma za ujenzi Tanzania zinalipa VAT ya kawaida ya 18%. Hata hivyo, kuna mambo muhimu ya kuzingatia: Bidhaa za ujenzi (saruji, nondo, matofali) = bidhaa — zinaweza kuwa na withholding ya 3% kwa qualifying buyer. Huduma za ujenzi (kazi ya ujenzi, usanifu, usimamizi) = huduma — withholding ya 6% kwa qualifying buyer. Katika ujenzi mkubwa (government contracts), mara nyingi serikali (qualifying buyer) inakata 6% ya VAT kwenye malipo ya huduma za kontrakta. Kwa hivyo kontrakta anatarajia kupokea malipo pungufu ya 6% withholding. Thibitisha na TRA (tra.go.tz)."
    },
    {
        "instruction": "VAT return inawasilishwa online au ni lazima nifike ofisini TRA?",
        "input": "",
        "output": "VAT return inaweza kuwasilishwa kupitia mifumo miwili: ONLINE (inashauriwa): Kupitia TRA portal ya IDRAS (Integrated Domestic Revenue Administration System) — biashara zinazosajiliwa zina akaunti ya online; Faida: haraka, rekodi zinabaki, hakuna foleni; Malipo yanaweza pia kufanywa online kupitia benki zilizounganishwa. OFISINI: Kwa biashara ndogo au ambazo hazina ufikiaji wa mtandao — zinaweza kwenda ofisi ya TRA ya karibu; Hata hivyo, TRA inazidi kushukiza biashara zote kutumia mfumo wa online. Usajili wa IDRAS unafanywa mara tu unapopata TIN yako. Thibitisha na TRA (tra.go.tz) na IDRAS."
    },
    {
        "instruction": "Nikichanganya mapato ya biashara mbili (mkahawa na duka) — kizingiti cha VAT pia kinachanganywa?",
        "input": "",
        "output": "Ndiyo — kama mmiliki mmoja ana biashara mbili au zaidi, mapato yote yanajumuishwa kwa madhumuni ya kizingiti cha VAT. Kwa mfano: mkahawa = TZS 120M/mwaka; duka = TZS 90M/mwaka. Jumla = TZS 210M — umepita kizingiti cha TZS 200M. Hata kama kila biashara peke yake haijafikia kizingiti, mmiliki mmoja anayefikia TZS 200M kwa jumla lazima asajili VAT. Hata hivyo, kama kila biashara ina TIN tofauti na inafanya kazi kwa uhuru kabisa (tofauti kisheria) — hali inaweza kutofautiana. Thibitisha na TRA (tra.go.tz) kwa hali yako maalum."
    },
    {
        "instruction": "GN 605A inaathiri SDL na VAT — vipi?",
        "input": "",
        "output": "GN 605A (ongezeko la mshahara wa chini, 1 Januari 2026) inaathiri zote kwa njia tofauti: SDL: inaathiriwa moja kwa moja — mishahara inayoongezeka inaongeza SDL base (3.5% ya mishahara). Mfanyakazi aliyepata mshahara mdogo sasa anapata zaidi → SDL inaongezeka. VAT: haihusiani moja kwa moja na mishahara — VAT inategemea mapato ya mauzo ya bidhaa/huduma. Lakini kama mwajiri anapandisha bei za bidhaa/huduma zake kwa wateja kujaza gharama za mishahara → mapato yanaweza kuongezeka → kizingiti cha VAT kinakaribiwa. Kwa muhtasari: GN 605A → mishahara juu → SDL juu (moja kwa moja); VAT inategemea uamuzi wa bei za biashara. Thibitisha na TRA na GN 605A."
    },
    {
        "instruction": "VAT inaweza kusamehewa (waived) kama biashara ina shida ya fedha?",
        "input": "",
        "output": "Hapana — VAT haiwezi kusamehewa kwa sababu ya shida ya fedha za biashara. VAT ni pesa ya wateja (umekusanya kutoka kwao kwa niaba ya TRA) — si pesa yako. Kukusanya VAT na kutolipa TRA ni tofauti na tatizo la fedha la biashara — ni ukwepaji wa kodi. TRA ina haki ya kudai VAT yote iliyokusanywa, faini, na riba bila kujali hali ya biashara. Kama una shida ya kulipa VAT — wasiliana na TRA mapema ili kupanga ratiba ya malipo (TRA ina uwezo wa kupanga awamu za kulipa). Lakini kusamehe VAT yenyewe — hapana. Thibitisha na TRA (tra.go.tz) kwa mazungumzo ya ratiba ya malipo."
    },
    {
        "instruction": "Biashara yangu ilianza Aprili — kizingiti cha TZS 200M kinahesabiwa kutoka Aprili au Januari?",
        "input": "",
        "output": "Kizingiti cha VAT kinahesabiwa kwa kipindi cha MWAKA 12 UNAOENDELEA (rolling 12 months) kutoka tarehe ya biashara kuanza — si lazima mwaka wa kalenda. Kwa biashara iliyoanza Aprili: kipindi cha kwanza cha tathmini ni Aprili hadi Machi ya mwaka unaofuata. Kama unafika TZS 200M kabla ya Machi — lazima usajili ndani ya siku 30 baada ya kufika. Pia angalia kizingiti cha miezi 6: kama katika kipindi chochote cha miezi 6 mfululizo (Aprili-Septemba, au Julai-Desemba) unafika TZS 100M — lazima usajili. Thibitisha na TRA (tra.go.tz) kwa hesabu sahihi ya kipindi chako."
    }
]

with open("datasets/tier1a/raw_sources/batch_009_checkpoints/checkpoint_005.jsonl", "a", encoding="utf-8") as f:
    for p in extra:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

with open("datasets/tier1a/raw_sources/raw_pairs_batch_009.jsonl", "a", encoding="utf-8") as f:
    for p in extra:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

count5 = sum(1 for l in open("datasets/tier1a/raw_sources/batch_009_checkpoints/checkpoint_005.jsonl", encoding="utf-8") if l.strip())
total = sum(1 for l in open("datasets/tier1a/raw_sources/raw_pairs_batch_009.jsonl", encoding="utf-8") if l.strip())
print(f"Chunk 5: {count5} pairs")
print(f"Main total: {total}")
