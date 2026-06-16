import json

extra = [
    {
        "instruction": "Niliuza bidhaa leo — risiti ya EFD ninaitoa siku ile ile au siku inayofuata?",
        "input": "",
        "output": "Risiti ya EFD inapaswa kutolewa SIKU ILE ILE ya muamala — si siku inayofuata. Hii ni kanuni ya msingi ya EFD: kila mauzo yanafuatwa na risiti mara moja. Kutoa risiti siku inayofuata kunaweza kuonekana kama kuchelewa kurekodi muamala — ambayo ni tatizo la kodi. Pia: Z-Report inayohitajika mwishoni mwa siku itaonyesha tofauti kati ya muamala wa siku hiyo na risiti zilizotolewa. Kwa biashara inayofanya kazi usiku: risiti ya muamala wa usiku wa mwisho inatoka siku ile ile — si asubuhi. Thibitisha na TRA (tra.go.tz)."
    },
    {
        "instruction": "EFD na TIMS (Tax Invoice Management System) — tofauti ni nini?",
        "input": "",
        "output": "EFD (Electronic Fiscal Device) ni kifaa (hardware) cha kutoa risiti za kodi — kama ECR (Electronic Cash Register) au POS system. TIMS (Tax Invoice Management System) ni mfumo wa kidijitali wa TRA unaopokea data kutoka EFD moja kwa moja kwa wakati halisi — ni backend ya TRA. EFD yako inaunganishwa na TIMS ya TRA — kila risiti unayotoa inaenda TRA mara moja. Hii inamaanisha TRA inajua mauzo yako ya wakati halisi bila ukaguzi wa mwili. Kwa hivyo kukosa kutoa risiti au kutoa risiti bandia ni hatarishi sana kwa sababu rekodi zinaonekana moja kwa moja. Thibitisha na TRA (tra.go.tz)."
    },
    {
        "instruction": "Biashara yangu imefungwa na TRA kwa kukosa risiti za EFD — inafunguliwa vipi?",
        "input": "",
        "output": "Kufungwa kwa biashara na TRA kwa ukiukwaji wa EFD kunahitaji: (1) Kulipa faini zote na adhabu zilizotolewa na TRA; (2) Kuwasilisha maelezo ya jinsi utakavyozingatia sheria ya EFD siku zijazo (compliance plan); (3) Kupata idhini ya TRA ya ufunguzi tena — kwa kawaida kwa barua rasmi; (4) Kuhakikisha EFD inafanya kazi vizuri kabla ya kufungua. Mchakato mzima unaweza kuchukua siku kadhaa hadi wiki. Wakati biashara imefungwa, hakuna mauzo yanayoweza kufanywa kisheria. Wasiliana na TRA mara moja na mshauri wa kodi aliyehitimu. Thibitisha na TRA (tra.go.tz)."
    },
    {
        "instruction": "EFD lazima iwe na QR code kwenye risiti — kwa nini QR code inahitajika?",
        "input": "",
        "output": "QR code kwenye risiti ya EFD (kama EFD ina uwezo huo au TIMS inainua) ina madhumuni makubwa: (1) Inawezesha mteja kuthibitisha risiti ni halali kwa kuiscan na app ya TRA au tovuti — kama risiti si ya kweli QR haithibitishi; (2) Inaunganisha risiti moja kwa moja na database ya TRA — ukaguzi wa haraka; (3) Inazuia risiti bandia — risiti bandia haina QR inayothibitika; (4) Inasaidia mteja kudai VAT input credit kwa uhakika. Biashara zinazotoa risiti za EFD zenye QR code zinasaidia wateja wao kupata input VAT credit haraka. Thibitisha na TRA (tra.go.tz) kuhusu mahitaji ya QR code kwa EFD yako."
    },
    {
        "instruction": "Z-Report lazima ipigwe lini — usiku au asubuhi ya siku inayofuata?",
        "input": "",
        "output": "Z-Report lazima ipigwe MWISHONI MWA SIKU YA BIASHARA — si asubuhi ya siku inayofuata. Z-Report inafanya muhtasari wa mauzo yote ya siku na kufunga siku ya biashara kwenye mfumo wa EFD. Baada ya Z-Report kupigwa, EFD inaanza akaunti mpya ya siku inayofuata. Kama hukupiga Z-Report usiku wa siku moja na ukajaribu kupiga asubuhi ya siku inayofuata kabla ya mauzo ya asubuhi — rekodi zitachanganyika. TRA inakagua wakati wa Z-Reports — kuchelewa kila wakati kunaweza kuuliza maswali. Thibitisha na TRA (tra.go.tz)."
    },
    {
        "instruction": "Ninauza bidhaa kwa serikali — bado ninatoa risiti ya EFD?",
        "input": "",
        "output": "Ndiyo — mauzo kwa serikali, taasisi za umma, na NGO bado yanahitaji risiti ya EFD. EFD haitegemei aina ya mteja — inategemea muamala wa biashara. Hata mauzo ya bidhaa au huduma kwa wizara, halmashauri, shule za serikali, au hospitali za umma yanahitaji: (1) Risiti ya EFD; (2) Tax invoice kama mteja amesajiliwa VAT na anataka kudai input VAT. Kwa mauzo makubwa kwa serikali inaweza pia kuhitajika purchase order na mkataba rasmi — lakini hilo si badala ya EFD. Thibitisha na TRA (tra.go.tz)."
    },
    {
        "instruction": "EFD inaweza kutoa risiti kwa lugha ya Kiingereza au lazima iwe Kiswahili?",
        "input": "",
        "output": "Risiti za EFD zinaweza kuwa kwa Kiingereza au Kiswahili — TRA haizuii lugha maalum kwa risiti. Muhimu zaidi ni: risiti iwe na taarifa zote zinazohitajika (jina la biashara, TIN, TRA registration number, tarehe, kiasi, aina ya bidhaa/huduma, na TRA verification code). Biashara nyingi za Tanzania zinatoa risiti kwa Kiingereza kwa sababu EFD nyingi zina programu ya Kiingereza. Wateja wanaohitaji risiti kwa Kiswahili wanaweza kuomba — lakini sheria hailazimishi lugha maalum. Thibitisha na TRA (tra.go.tz) kwa miongozo ya hali ya sasa."
    },
    {
        "instruction": "EFD inafanya kazi bila umeme — kama umeme unakatika ninafanyaje?",
        "input": "",
        "output": "EFD nyingi (hasa za kisasa) zina betri ya akiba au UPS inayoruhusu kufanya kazi kwa muda bila umeme. Hatua za kufuata wakati umeme unakatika: (1) Tumia betri ya EFD kama ipo — endelea kutoa risiti; (2) Kama EFD haifanyi kazi kabisa — andika rekodi za mikono ya kila muamala; (3) Unapopata umeme — ingiza rekodi za mikono kwenye EFD na unda risiti zilizokosekana (TRA ina mchakato wa 'recovery' transactions); (4) Toa habari TRA kama upotevu wa muda mrefu wa umeme ulikuzuia. Usiendelee na biashara bila rekodi yoyote. Thibitisha na TRA (tra.go.tz) na muuzaji wa EFD wako."
    },
    {
        "instruction": "Wakurugenzi wa kampuni wanaweza kushikiliwa kibinafsi kwa faini za EFD?",
        "input": "",
        "output": "Ndiyo — TRA ina uwezo wa kufuatilia wakurugenzi na maafisa wa kampuni kibinafsi kwa makosa ya makusudi ya kodi, ikiwa ni pamoja na ukiukwaji wa EFD. Hasa: kama kampuni imeendesha biashara kwa makusudi bila EFD au kutoa risiti bandia — wakurugenzi wanaohusika wanaweza kushikiliwa kibinafsi kwa: (1) Madeni ya kodi + faini ya kampuni; (2) Mashtaka ya jinai ya ukwepaji wa kodi. Hata kama kampuni ni ya hisa (limited liability), ulaghai wa kodi na ukwepaji wa makusudi unaweza kuondoa ulinzi wa limited liability. Thibitisha na TRA (tra.go.tz) na mshauri wa kodi."
    },
    {
        "instruction": "EFD — kuna leseni ya kila mwaka au ni ya kudumu baada ya kusajiliwa mara moja?",
        "input": "",
        "output": "EFD inasajiliwa mara moja kwa TRA — si leseni ya kila mwaka. Hata hivyo, TRA inaweza kuhitaji: (1) Usasishaji (update) wa programu ya EFD kila mara inapotolewa na TRA au muuzaji; (2) Uhakika wa mfumo (compliance check) kama TRA inabadilisha mahitaji; (3) Kubadilisha EFD kama toleo la zamani linafutwa msaada. Pia kama EFD inaharibiwa au inaibiwa — inabidi kusajili upya kwa TRA. Malipo ya ziada ya kila mwaka yanaweza kuwa kwa muuzaji wa EFD kwa huduma ya matengenezo — si TRA. Thibitisha na TRA (tra.go.tz) na muuzaji wako wa EFD."
    },
    {
        "instruction": "Ninafungua tawi la biashara yangu katika mji mwingine — ninahitaji EFD mpya au moja inatosha?",
        "input": "",
        "output": "Kwa kawaida, kila eneo la biashara (tawi tofauti) linahitaji EFD yake mwenyewe inayosajiliwa kwa TIN na anwani ya tawi hilo. Tawi moja haliwezi kutumia EFD ya tawi lingine — kwa sababu: (1) EFD imesajiliwa kwa anwani maalum; (2) Rekodi za TIMS zinahusiana na eneo; (3) Wakaguzi wa TRA wanaweza kukagua kila eneo tofauti. Hivyo kwa kila tawi linalofanya mauzo ya bidhaa au huduma zinazohitaji EFD — inahitaji EFD yake mwenyewe iliyosajiliwa na TRA. Thibitisha na TRA (tra.go.tz) na muuzaji wa EFD."
    },
    {
        "instruction": "EFD inahitajika kwa biashara za online peke yake (e-commerce, hakuna duka la mwili)?",
        "input": "",
        "output": "EFD ya kawaida (ya mwili) inalenga biashara za mwili, lakini TRA inasasisha sheria kujumuisha biashara za kidijitali. Kwa biashara za online Tanzania: (1) Kama biashara imesajiliwa Tanzania na ina TIN — miongozo ya EFD inatumika; (2) TRA ina mfumo wa ETS (Electronic Tax Stamps) na TIMS ambao unaweza kutumika kwa mauzo ya kidijitali; (3) Biashara za e-commerce zinaweza kuhitaji invoice ya kielektroniki yenye TRA code badala ya risiti ya kawaida ya EFD. Mfumo wa EFD kwa e-commerce Tanzania uko katika hatua za maendeleo. Wasiliana na TRA (tra.go.tz) kwa mwongozo maalum wa biashara yako ya kidijitali."
    },
    {
        "instruction": "Biashara yangu ina kikosi cha mauzo kinachofanya kazi nje ya ofisi — wanaweza kutumia EFD ya simu?",
        "input": "",
        "output": "TRA imesajilisha EFD za aina mbalimbali ikiwa ni pamoja na mifumo inayoendana na simu za mkononi (mobile POS). Kwa kikosi cha mauzo wa nje: (1) Mifumo ya mobile EFD/POS iliyoidhinishwa na TRA inaweza kutumika; (2) Kila muamala uliowasilishwa lazima utoe risiti ya EFD halali; (3) Mfumo lazima uunganishwe na TIMS ya TRA. Biashara nyingi za deliveries na mauzo ya nyanjani zinatumia mobile POS zilizounganishwa na mfumo wa EFD. Orodha ya EFD zilizoidhinishwa ipo kwenye TRA. Thibitisha na TRA (tra.go.tz) na muuzaji wa EFD kwa suluhisho linalofaa biashara yako."
    },
    {
        "instruction": "Wafanyakazi wa nyumbani (domestic workers) — wanaathiri kizingiti cha SDL?",
        "input": "",
        "output": "Hapana — wafanyakazi wa nyumbani (domestic workers) kama wapishi, walinzi wa nyumbani, na wasaidizi wa familia ambao wanafanya kazi katika kaya ya kibinafsi (si biashara) HAWAINGII katika kizingiti cha SDL. SDL inalenga waajiri wa BIASHARA (commercial employers) — si kaya za kibinafsi. Hata hivyo, waajiri wa kaya za kibinafsi bado wana wajibu mwingine: (1) Kudhibiti kodi ya PAYE kwa wafanyakazi wa nyumbani wenye mapato yanayopita TZS 270,000/mwezi; (2) Kuzingatia GN 605A ya mshahara wa chini kwa sekta ya kazi za nyumbani. Thibitisha na TRA (tra.go.tz) kwa mwongozo maalum."
    },
    {
        "instruction": "Mkurugenzi wa kampuni analipwa ujira wa mkurugenzi (director's fee) — huhesabiwa katika SDL base?",
        "input": "",
        "output": "Ujira wa mkurugenzi (director's fees) unaposwa chini ya SDL unategemea kama mkurugenzi ni mwajiriwa wa kampuni kwa wakati wote au mkurugenzi asiye mwajiriwa. MKURUGENZI MWAJIRIWA (full-time executive director): mshahara wake unaingia SDL base (kama wafanyakazi wengine). MKURUGENZI ASIYE MWAJIRIWA (non-executive director fees): kwa kawaida hukatwa WHT (Withholding Tax) ya 15% — si PAYE, na kwa hivyo haingi SDL base ya kawaida. Hata hivyo, ufafanuzi huu unategemea muundo wa mkataba. Thibitisha na TRA (tra.go.tz) na mshauri wa kodi kwa hali yako maalum."
    },
    {
        "instruction": "SDL na WCF — vinalipwa kwa wakati mmoja au tofauti?",
        "input": "",
        "output": "SDL na WCF vinalipwa wakati tofauti kwa taasisi tofauti: SDL (→ TRA): tarehe ya mwisho ni 7 ya mwezi unaofuata mwezi wa malipo ya wafanyakazi. Inalipwa pamoja na PAYE kwa kawaida katika kujaza fomu ya TRA. WCF (→ WCF Authority): malipo yanaweza kufanywa kwa mwezi, robo ya mwaka, nusu ya mwaka, au mwaka mzima — kwa idhini ya WCF. Kwa kawaida inalipwa mwezi mzima. Zinatumia fomu tofauti, portals tofauti, na taasisi tofauti. Kampuni nyingi zinaweka ratiba maalum: 7th (SDL+PAYE kwa TRA), na tofauti kwa WCF. Thibitisha na TRA (tra.go.tz) na WCF (wcf.go.tz)."
    },
    {
        "instruction": "Biashara yangu ya hoteli — EFD inatumika kwa bili za vyumba tu au chakula pia?",
        "input": "",
        "output": "EFD inatumika kwa KILA MUAMALA wa biashara — bili za vyumba, chakula, vinywaji, laundry, parking, na huduma zozote za ziada. Hakuna msamaha kwa aina fulani ya huduma ndani ya hoteli moja. Hoteli inahitaji kuhakikisha: (1) EFD inatoa risiti kwa kila bili ya chumba; (2) Migahawa na baa ndani ya hoteli zinatoa risiti za EFD kwa chakula na vinywaji; (3) Huduma za ziada (spa, gym, conference) zinatoa risiti pia. Bila shaka, hoteli zinatoa invoice kubwa kwa makampuni na watu binafsi — hizi lazima ziwe tax invoices za EFD. Thibitisha na TRA (tra.go.tz)."
    },
    {
        "instruction": "EFD — ni tofauti gani kati ya ECR na POS system?",
        "input": "",
        "output": "ECR (Electronic Cash Register) na POS (Point of Sale) ni aina mbili tofauti za EFD zilizoidhinishwa na TRA: ECR: kifaa kimoja kilichojitegemea cha kurekodi mauzo na kutoa risiti — rahisi na nafuu, kinafaa kwa biashara ndogo za rejareja. POS System: mfumo mkubwa zaidi unaounganisha kompyuta/tablet na printer — unaweza kushughulikia hesabu ngumu zaidi, akaunti za wateja, inventory. Vyote viwili lazima viwe: (1) Vimeidhinishwa na TRA; (2) Vimesajiliwa kwa TRA kabla ya kutumika; (3) Vimeunganishwa na TIMS (kwa biashara zinazohitajika). Chaguo linategemea ukubwa na aina ya biashara. Thibitisha na TRA (tra.go.tz)."
    },
    {
        "instruction": "SDL ya mfanyakazi wa migodi — kuna kiwango maalum au ni 3.5% ile ile?",
        "input": "",
        "output": "SDL kwa sekta yoyote, ikiwa ni pamoja na migodi na madini, ni 3.5% ya mishahara ya fedha ya wafanyakazi wote — kiwango kimoja kinachotumika kwa sekta zote. Hakuna kiwango maalum cha SDL kwa migodi. Hata hivyo, sekta ya migodi ina mifumo tofauti ya kodi nyingine (kama royalties, ring-fencing taxation, na mikataba maalum ya madini) — lakini SDL ni 3.5% kwa kawaida. Kumbuka: kizingiti cha wafanyakazi 10 bado kinatumika — kampuni ya mgodi yenye wafanyakazi 10 au zaidi inalipa SDL ya 3.5%. Thibitisha na TRA (tra.go.tz)."
    },
    {
        "instruction": "Biashara yangu ina wafanyakazi wa msimu (seasonal) kwa miezi 3 tu — SDL inakokotolewa vipi?",
        "input": "",
        "output": "SDL inakokotolewa KILA MWEZI ambapo biashara ina wafanyakazi 10 au zaidi, bila kujali kama ni wa msimu au wa kudumu. Kwa mfano: kama una wafanyakazi wa msimu 15 kwa miezi 3 (Januari–Machi), SDL inalipwa kwa miezi 3 ile ile tu. Miezi mingine (Aprili–Desemba) ukiwa na chini ya wafanyakazi 10 — hakuna SDL. Kila mwezi unakokotolewa kwa hali ya wafanyakazi na mishahara ya MWEZI HULE — si wastani wa mwaka. Kwa hivyo biashara za msimu zinalipa SDL miezi inayofanya kazi tu. Thibitisha na TRA (tra.go.tz)."
    },
    {
        "instruction": "SDL — kama mfanyakazi ana mshahara wa TZS 100,000 tu (chini ya mshahara wa chini) — bado anahusika katika SDL base?",
        "input": "",
        "output": "Ndiyo — kwa madhumuni ya SDL, mfanyakazi yeyote anayelipwa pesa za fedha (hata chini ya mshahara wa chini wa GN 605A) anahusika katika SDL base. SDL base ni JUMLA ya mishahara ya fedha ya wafanyakazi wote — si tu wale wanaolipwa zaidi ya mshahara wa chini. Hata hivyo, unapaswa kuhakikisha wafanyakazi wote wanalipwa angalau mshahara wa chini wa GN 605A (kuanzia 1 Januari 2026) — vinginevyo unakiuka Sheria ya Kazi, hata kama SDL imekusanywa. Thibitisha na TRA kwa SDL na wizara ya Kazi kwa mshahara wa chini."
    },
    {
        "instruction": "EFD — ninaweza kuuza bidhaa kwa bei ya chini kuliko gharama (bia ya soko) na bado EFD inafanya kazi?",
        "input": "",
        "output": "EFD inasajili muamala kama unavyouingiza — bei ya kuuza, kiasi, na aina ya bidhaa. Haisemi kama bei ni 'ya kawaida' au la. Hata hivyo, TRA inaweza kuangalia biashara inayouza kwa bei za chini sana kwa wakati mrefu — hii inaweza kuonyesha mapato yanayoficha. Maswali yanaweza kutokea kama: mauzo ya chini sana dhidi ya stoo kubwa; faida isiyo na mantiki. EFD yenyewe haizuii uuzaji kwa bei yoyote — lakini rekodi zote za EFD zinajilimbikizia na TRA inaweza kuzichunguza. Hakikisha bei zinazoingia kwenye EFD ni za kweli. Thibitisha na TRA (tra.go.tz)."
    },
    {
        "instruction": "Biashara yangu imebadilisha EFD (machine mpya) — ninahitaji kusajili upya kwa TRA?",
        "input": "",
        "output": "Ndiyo — EFD mpya inahitaji kusajiliwa upya kwa TRA kabla ya kutumika kwa madhumuni ya kodi. TRA lazima ijue kwamba EFD ya zamani imebadilishwa na mpya imewekwa — ili rekodi za TIMS zielewe mabadiliko. Hatua za kufuata: (1) Arifu TRA kwamba EFD ya zamani imeachwa; (2) Wasilisha EFD mpya kwa TRA kwa usajili; (3) Pata nambari ya usajili ya EFD mpya kabla ya kutumika; (4) Hifadhi rekodi za EFD ya zamani — TRA inaweza kuzihitaji kwa ukaguzi. Kutumia EFD mpya bila kusajili kwa TRA ni kosa. Thibitisha na TRA (tra.go.tz) na muuzaji wa EFD."
    },
    {
        "instruction": "SDL — kama mwajiri anasahau kulipa mwezi mmoja, faini ni nini?",
        "input": "",
        "output": "Kushindwa kulipa SDL kwa wakati (7 ya mwezi unaofuata) kunasababisha: (1) Faini ya 2.5% ya kiasi kisicholipwa kwa kila mwezi wa kuchelewa (kama PAYE late penalty); (2) Riba ya kuchelewa — inaongezeka kila mwezi; (3) Hatari ya ukaguzi wa TRA wa miezi ya nyuma. Kwa mfano: SDL ya TZS 175,000 isiyolipwa kwa mwezi 1 — faini inaweza kuwa TZS 4,375 (2.5% × 175,000). Mwezi 2 — faini inaongezeka tena. Kulipa haraka iwezekanavyo kupunguza mkusanyiko wa faini. Thibitisha na TRA (tra.go.tz) kwa hesabu sahihi za faini."
    }
]

with open("datasets/tier1a/raw_sources/batch_009_checkpoints/checkpoint_004.jsonl", "a", encoding="utf-8") as f:
    for p in extra:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

with open("datasets/tier1a/raw_sources/raw_pairs_batch_009.jsonl", "a", encoding="utf-8") as f:
    for p in extra:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

count4 = sum(1 for l in open("datasets/tier1a/raw_sources/batch_009_checkpoints/checkpoint_004.jsonl", encoding="utf-8") if l.strip())
total = sum(1 for l in open("datasets/tier1a/raw_sources/raw_pairs_batch_009.jsonl", encoding="utf-8") if l.strip())
print(f"Chunk 4: {count4} pairs")
print(f"Main total: {total}")
