"""Generate remaining batch_012 pairs: EFD(20), VAT_REG(20), SDL(20),
   BRELA(20), NSSF(20), OSHA(10), OOC(10) — 120 pairs total."""
import json, glob, os

SYSTEM = ("Jina lako ni Chike, mshauri wa biashara kutoka Africa Giants. "
          "Kauli mbiu yako ni: Fahamu Biashara Yako, Maarifa Yako. "
          "Unajibu maswali kuhusu biashara, kodi, BRELA, TRA, NSSF, OSHA, SDL, PAYE, VAT "
          "kwa Kiswahili na Kiingereza. Kama swali liko nje ya mada yako sema wazi kwamba "
          "halijui na mwelekeze kwa mtaalamu.")

OUT_DIR = "datasets/tier1a/raw_sources/batch_012_checkpoints"

# Build schema-aware dedup index
seen = set()
for fp in sorted(glob.glob("datasets/tier1a/cleaned_pairs/*.jsonl")):
    with open(fp) as f:
        for line in f:
            if line.strip():
                d = json.loads(line)
                if "instruction" in d:
                    key = (d.get("instruction","") + d.get("output",""))[:120].lower().strip()
                else:
                    key = (d.get("question_sw","") + d.get("answer_sw",""))[:120].lower().strip()
                seen.add(key)

# Also absorb already-generated vat_withholding checkpoints
for fp in sorted(glob.glob(f"{OUT_DIR}/ck_vat_withholding_*.jsonl")):
    with open(fp) as f:
        for line in f:
            if line.strip():
                d = json.loads(line)
                key = (d.get("instruction","") + d.get("output",""))[:120].lower().strip()
                seen.add(key)

print(f"Dedup index: {len(seen)} entries")

def p(q, a):
    return {"instruction": q, "input": "", "output": a, "system": SYSTEM}

def dedup_check(pair):
    key = (pair["instruction"] + pair["output"])[:120].lower().strip()
    return key not in seen

def register(pair):
    key = (pair["instruction"] + pair["output"])[:120].lower().strip()
    seen.add(key)

def save_ck(pairs, subdomain, ck_num):
    fname = os.path.join(OUT_DIR, f"ck_{subdomain}_{ck_num:03d}.jsonl")
    with open(fname, "w", encoding="utf-8") as f:
        for pair in pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")
    print(f"[Agent 3] Saved ck_{subdomain}_{ck_num:03d}.jsonl — {len(pairs)} pairs")

# ═══════════════════════════════════════════════════════════════════════════════
# EFD_COMPLIANCE — 20 pairs
# Required keywords: udanganyifu, ukiukwaji, kukosa, ruhusa, maelekezo,
#                    miamala, kutoza, msambazaji, idhini
# ═══════════════════════════════════════════════════════════════════════════════
SD = "efd_compliance"

efd_ck1 = [
p("EFD machine yangu iliharibika. Niendelee kuuza bila kutoa risiti wakati inakarabatiwa?",
  "Hapana. Kuendelea kufanya miamala bila kutoa risiti ya EFD ni ukiukwaji wa sheria ya EFD. Hatua sahihi ni: (1) Ripoti uharibiku kwa msambazaji aliyeidhinishwa na TRA mara moja; (2) Omba ruhusa ya sementara kwa TRA (tra.go.tz) kuendelea na biashara wakati wa ukarabati; (3) Hifadhi rekodi za mauzo yote kwa mkono wakati huo; (4) Malipo ya kodi lazima yafanyike kama kawaida. Kuendelea bila ruhusa ni kosa la kisheria."),

p("EFD machine yangu imeharibika — TRA wanasema niwasiliane na msambazaji. Msambazaji aliyeidhinishwa ni nani?",
  "Msambazaji aliyeidhinishwa (approved supplier) ni kampuni iliyopata idhini rasmi ya TRA kuuza na kushughulikia EFD machines Tanzania. Nunua au karabatia EFD yako kutoka kwa msambazaji aliyeidhinishwa TRA tu — kwa orodha ya sasa ya wasambazaji walioidhinishwa, angalia kwenye tra.go.tz. Msambazaji asiyeidhinishwa hawezi kuwasha (activate) EFD yako kwenye mfumo wa TRA."),

p("Je, kukosa kutoa risiti ya EFD kwa mteja ni udanganyifu wa kodi?",
  "Ndiyo, TRA inaweza kuainisha kukosa kutoa risiti ya EFD kama udanganyifu wa kodi (tax evasion) kwa sababu miamala inayokosekana kwenye mfumo wa EFD haionekani kwa TRA. Hii ni ukiukwaji mkubwa ambao unaweza kusababisha: faini kubwa, uchunguzi wa kodi, au hatua za kisheria. Toa risiti ya EFD kwa kila muamala bila ubaguzi."),

p("Adhabu ya kutotoa risiti ya EFD ni nini?",
  "Adhabu kwa kukosa kutoa risiti ya EFD ni pamoja na: faini ya pesa, kufungwa kwa biashara kwa muda, na uwezekano wa mashtaka ya udanganyifu wa kodi. TRA ina mamlaka ya kufika bila taarifa (surprise inspection) na kukagua miamala. Epuka adhabu hizi kwa kutoa risiti ya EFD kwa kila muamala bila ubaguzi. Kwa kiasi halisi cha faini, thibitisha na TRA kwa maelekezo ya sasa."),

p("Wateja wangu wanakataa risiti ya EFD. Je, lazima nitoe hata hivyo?",
  "Ndiyo, lazima utoe risiti ya EFD kwa kila muamala, hata kama mteja anakataa au haipendi. Wajibu wa kutoa risiti ni wa biashara — si wa mteja kukubali. Kama mteja atakataa, bado rekodi ya muamala lazima ibaki kwenye mfumo wa EFD. TRA haikusamehe kwa msingi wa mteja kukataa. Toa risiti na ieleze mteja umuhimu wake."),

p("TRA inanikagua EFD. Wana mamlaka ya kuangalia rekodi zangu za miamala ya nyuma?",
  "Ndiyo. TRA ina mamlaka kamili ya kukagua rekodi zote za miamala zilizohifadhiwa kwenye mfumo wa EFD, ikiwa ni pamoja na miamala ya miaka ya nyuma. Rekodi za EFD zinapelekwa moja kwa moja kwenye seva za TRA (real-time reporting). Hakikisha miamala yote ya biashara yako imefanywa kupitia EFD na kutoa risiti. Ikiwa kuna kasoro, TRA inaweza kutoa tathmini ya ziada ya kodi (additional assessment)."),

p("Ninataka kununua EFD machine mpya. Ninachagua vipi msambazaji sahihi?",
  "Chagua msambazaji ambaye ana idhini rasmi ya TRA. Hatua: (1) angalia orodha ya wasambazaji walioidhinishwa kwenye tra.go.tz; (2) thibitisha nambari ya idhini ya msambazaji kabla ya kununua; (3) msambazaji aliyeidhinishwa ndiye pekee anayeweza kuomba activation ya EFD yako kwenye mfumo wa TRA. Usinunue kutoka kwa muuzaji asiyejulikana — EFD ya msambazaji asiyeidhinishwa haitawashwa na TRA."),

p("EFD yangu haikutoa risiti kwa muamala mmoja kwa sababu ya tatizo la mfumo. Niripoti wapi?",
  "Ripoti tatizo hilo kwa msambazaji wako aliyeidhinishwa na TRA haraka iwezekanavyo. Msambazaji atawasiliana na TRA kwa niaba yako au akuelekezee TRA moja kwa moja. Hifadhi kumbukumbu ya muamala huo kwa mkono. Kutoa taarifa mapema kunakuonyesha TRA nia njema — kutotoa taarifa kunaweza kuonekana kama kukusudia ukiukwaji."),

p("Kiwango cha VAT kwa malipo ya kielektroniki (B2C) ni ngapi sasa hivi?",
  "Kuanzia 1 Septemba 2025, kiwango cha VAT kwa malipo ya kielektroniki (B2C electronic payments) ni asilimia 16 — tofauti na kiwango cha kawaida cha 18%. Hata hivyo, maelekezo kamili ya utekelezaji bado yanasubiri tangazo rasmi la Kamishna Mkuu wa TRA. Kwa taarifa ya sasa ya utekelezaji, angalia tra.go.tz au wasiliana na TRA moja kwa moja."),

p("Biashara yangu haijafika kizingiti cha TZS 11M — je, ninahitaji EFD?",
  "Kizingiti cha EFD ni mauzo ya TZS 11,000,000 kwa mwaka au zaidi. Biashara zenye mauzo chini ya TZS 11M inaweza kutumia risiti za kawaida. Hata hivyo, biashara ZOTE zilizosajiliwa VAT lazima zitumie EFD, bila kujali kiwango cha mauzo. Kama umesajiliwa VAT, EFD ni ya lazima. Thibitisha hali yako na TRA (tra.go.tz) kwa maelekezo sahihi."),
]

efd_ck1_clean = [x for x in efd_ck1 if dedup_check(x)]
for x in efd_ck1_clean: register(x)
save_ck(efd_ck1_clean, SD, 1)

efd_ck2 = [
p("Risiti za EFD zinatumiaje kupambana na udanganyifu wa kodi Tanzania?",
  "EFD machines zinapeleka taarifa za miamala moja kwa moja kwenye seva za TRA kwa wakati halisi (real-time). Hii inamaanisha TRA wanaona mauzo yako bila kukuomba taarifa za ziada. Mfumo huu unazuia udanganyifu wa kodi kwa sababu biashara haiwezi kuficha miamala. Kupita kwa risiti za EFD, TRA wanaweza kulinganisha mauzo yaliyotangazwa na ya kweli moja kwa moja."),

p("Afisa wa TRA amekuja ofisini bila kupanga — ana mamlaka ya kuangalia EFD yangu moja kwa moja?",
  "Ndiyo. TRA ina mamlaka ya kukagua EFD yako bila taarifa ya awali (surprise inspection). Hii ni sehemu ya utekelezaji wa sheria ya EFD. Afisa ana haki ya kuangalia mfumo wako, kulinganisha rekodi za EFD na vitabu vya hesabu, na kutoa tathmini kama ataona tofauti. Shiriki kikamilifu na umpatie taarifa zote anazoomba — kukataa ni ukiukwaji wa ziada."),

p("Je, ninaweza kutoa risiti ya mkono badala ya EFD kwa wateja wanaotaka haraka?",
  "Hapana. Kama biashara yako iko kwenye kiwango kinachohitaji EFD (mauzo TZS 11M+ au umesajiliwa VAT), lazima utoe risiti ya EFD kwa kila muamala. Risiti za mkono hazikubaliwi kama mbadala wa EFD. Kutoza bila EFD ni ukiukwaji wa sheria hata kama mauzo ni madogo na mteja anataka haraka. Kama EFD haifanyi kazi, ripoti kwa msambazaji na omba ruhusa ya sementara kutoka TRA."),

p("Msambazaji wangu aliyenipa EFD amefilisika. EFD yangu bado inatumika?",
  "EFD yako iliyoanzishwa (activated) tayari kwenye mfumo wa TRA itaendelea kufanya kazi. Tatizo ni matengenezo na msaada wa kiufundi. Wasiliana na TRA (tra.go.tz) kupata maelekezo kuhusu jinsi ya kupata msambazaji mpya aliyeidhinishwa akuchukue. TRA inaweza kukuunganisha na msambazaji mwingine aliyeidhinishwa atakayehudumia EFD yako."),

p("Mfanyakazi wangu alitoa risiti ya EFD lakini kwa kiasi tofauti na muamala halisi — hii ni tatizo?",
  "Ndiyo, hii ni tatizo zito. Kutoza kiasi tofauti kwenye EFD ni ukiukwaji wa sheria na inaweza kuainishwa kama udanganyifu wa kodi. Hatua za haraka: (1) rekebisha mara moja kwa kutoa risiti sahihi ya marekebisho (credit note/debit note); (2) thibitisha mfanyakazi amefunzwa vizuri matumizi ya EFD; (3) hakikisha hesabu za EFD zinaoanisha na vitabu vyako. Kama utakutana na ukaguzi wa TRA, tofauti hizi zitaonekana."),

p("Biashara yangu ya jumla (wholesale) — inahitaji kutoa risiti ya EFD kwa kila muamala wa biashara-kwa-biashara (B2B)?",
  "Ndiyo. Biashara yote — B2C (biashara kwa mtumiaji wa mwisho) na B2B (biashara kwa biashara) — zinazofuata kizingiti cha EFD (TZS 11M+ au zilizosajiliwa VAT) lazima zitoe risiti ya EFD kwa kila muamala. Muamala wa B2B hausamehewi. Kila muamala lazima uingie kwenye mfumo wa EFD na risiti itolewe."),

p("Ninauza online. Je, ninahitaji EFD kwa mauzo ya mtandaoni?",
  "Ndiyo. Biashara za mtandaoni (e-commerce) zinazofuata kizingiti cha EFD (mauzo TZS 11M+ kwa mwaka, au zilizosajiliwa VAT) lazima zitoe risiti ya EFD. TRA imeandaa miongozo (maelekezo) maalum kwa biashara za mtandaoni. Wasiliana na TRA (tra.go.tz) kupata maelekezo sahihi ya jinsi ya kuunganisha mfumo wako wa mauzo ya mtandaoni na EFD."),

p("Adhabu ya kutumia EFD isiyoidhinishwa na TRA ni nini?",
  "Kutumia EFD isiyoidhinishwa au iliyonunuliwa kutoka kwa msambazaji asiye na idhini ya TRA ni ukiukwaji mkubwa. Biashara inaweza kukabiliwa na: kufungwa kwa biashara, faini kubwa, na uwezekano wa mashtaka ya udanganyifu wa kodi. EFD isiyoidhinishwa pia haiwezi kupeleka data kwa TRA — miamala yote itaonekana kama imefichwa. Nunua EFD kutoka msambazaji aliyeidhinishwa TRA pekee."),

p("Nikiwa msambazaji wa EFD nchini Tanzania, ninahitaji nini kupata idhini ya TRA?",
  "Msambazaji wa EFD anahitaji idhini rasmi kutoka TRA. Mchakato wa kupata idhini unajumuisha maombi rasmi kwa TRA, uthibitisho wa ubora wa EFD machine, na makubaliano ya ushirikiano na TRA kuhusu uanzishaji wa mashine na mafunzo. Kwa maelekezo kamili ya utaratibu wa kupata idhini, wasiliana na TRA (tra.go.tz) moja kwa moja — mahitaji yanaweza kubadilika."),

p("EFD machine yangu iliibiwa. Niwasiliane na nani kwanza?",
  "Hatua za haraka: (1) Ripoti wizi kwa polisi na pata nambari ya kesi; (2) Ripoti msambazaji wako aliyeidhinishwa na TRA haraka — waajulishe nambari ya serial ya EFD iliyoibiwa; (3) Wasiliana na TRA (tra.go.tz) kuzuia EFD iliyoibiwa isitumike na mwizi; (4) Omba EFD mbadala haraka ili biashara iendelee. Hifadhi kumbukumbu ya muamala wote uliotokea kabla ya wizi. Kutoa taarifa mapema kulinda biashara yako dhidi ya matumizi mabaya ya EFD iliyoibiwa."),
]

efd_ck2_clean = [x for x in efd_ck2 if dedup_check(x)]
for x in efd_ck2_clean: register(x)
save_ck(efd_ck2_clean, SD, 2)
print(f"[EFD_COMPLIANCE] Total: {len(efd_ck1_clean)+len(efd_ck2_clean)} pairs")

# ═══════════════════════════════════════════════════════════════════════════════
# VAT_REGISTRATION — 20 pairs
# Required keywords: kinachozunguka, anayehitimu, usajilishaji, tangazo,
#                    certificate, pembejeo, mfululizo, wahasibu, kamishna
# ═══════════════════════════════════════════════════════════════════════════════
SD = "vat_registration"

vat_ck1 = [
p("Kipindi kinachozunguka cha miezi 12 maana yake nini kwa usajilishaji wa VAT?",
  "Kipindi kinachozunguka (rolling 12-month period) ni kipindi chochote cha miezi 12 mfululizo, si lazima kuanza Januari. Kama mauzo yako yoyote ya miezi 12 inayozunguka yanafika au kuzidi TZS 200,000,000, lazima usajiliwe VAT. Mfano: mauzo ya Aprili 2025 hadi Machi 2026 yanafika TZS 200M — lazima usajiliwe. Usajilishaji lazima ufanyike ndani ya siku 30 baada ya kuzidi kizingiti."),

p("Kizingiti cha usajilishaji wa VAT Tanzania ni ngapi kwa sasa hivi?",
  "Kizingiti cha usajilishaji wa VAT ni TZS 200,000,000 kwa mwaka (miezi 12 inayozunguka) AU TZS 100,000,000 kwa miezi 6 yoyote mfululizo. Mauzo yoyote yanayozidi kizingiti hiki — kwa kipindi chochote kinachozunguka — yanalazimisha usajilishaji. Kizingiti hiki kilianza kutumika Julai 2024 (Finance Act 2024), kikipandishwa kutoka TZS 100M kwa mwaka."),

p("Biashara yangu ya jumla — ninahesabu vipi kama nifike kizingiti cha VAT kwa miezi 6?",
  "Hesabu mauzo yako ya jumla (kabla ya kodi) kwa miezi 6 mfululizo yoyote — si lazima kuanza Januari. Kama jumla ya miezi 6 mfululizo inazidi TZS 100,000,000, umefika kizingiti na lazima usajiliwe VAT. Ongezeko la mauzo kwenye mfululizo wa miezi — linachozunguka kila mwezi — ndilo kinachoangaliwa. Wasiliana na wahasibu au mshauri wa kodi kukusaidia kuhesabu kwa usahihi."),

p("Ninaweza kusajiliwa VAT hiari (voluntarily) kabla sijafika kizingiti?",
  "Ndiyo. Unaweza kuomba usajilishaji wa hiari wa VAT hata kama mauzo yako hayajafika kizingiti. Hii inakufaa kama unauza kwa biashara zilizosajiliwa VAT — watakuruhusu kudai pembejeo ya VAT (input VAT) kwenye ununuzi wako. Omba kwa Kamishna wa TRA (tra.go.tz). Faida: unaweza kudai pembejeo ya VAT. Hasara: unajibika kwa taratibu zote za VAT, vikiwemo EFD na filing ya kila mwezi."),

p("Wataalamu wa hesabu (wahasibu) na mawakili — lazima wasajiliwe VAT?",
  "Ndiyo, wataalamu wa hesabu (wahasibu), mawakili, na watoa huduma za kitaalamu wanaofanya biashara Tanzania wanalazimika kusajiliwa VAT kama mapato yao yanafika kizingiti. Zaidi ya hayo, TRA inaweza kuwataka wasajiliwe hata kabla ya kizingiti kama aina ya biashara yao inabainishwa. Wasiliana na TRA (tra.go.tz) ili kujua kama kazi yako maalum ina masharti ya ziada."),

p("VAT registration certificate inatoa haki gani kwa biashara yangu?",
  "Certificate ya usajilishaji wa VAT inakupa haki ya: (1) kudai pembejeo ya VAT (input VAT) kwenye ununuzi wako wa biashara — hii inapunguza mzigo wako wa kodi; (2) kuuza kwa biashara zilizosajiliwa VAT ambazo zinahitaji invoice ya VAT; (3) kushiriki katika manunuzi ya serikali yenye masharti ya VAT. Certificate lazima ionekane kwenye mahali panaoonekana kwenye biashara yako."),

p("Niliomba usajilishaji wa VAT miezi 3 iliyopita — sijapata jibu. Nifanye nini?",
  "Fuatilia ombi lako na Kamishna wa TRA (tra.go.tz). Ikiwa umekuwa ukisubiri zaidi ya muda uliowekwa na TRA, ufuatilie rasmi kwa maandishi ukitaja tarehe ya maombi na nambari ya kumbukumbu. Unaweza pia kuwasiliana na ofisi ya TRA karibu nawe. Usisimame biashara — endelea kuhifadhi rekodi za mauzo vizuri hadi upate jibu."),

p("Kama nimesajiliwa VAT, ninalazimika kutoa invoice ya VAT kwa kila muamala?",
  "Ndiyo. Biashara iliyosajiliwa VAT lazima itoe invoice ya VAT (tax invoice) kwa kila muamala wa biashara. Invoice lazima iwe na: nambari ya usajilishaji wa VAT, TIN, maelezo ya bidhaa/huduma, kiasi cha VAT kilichotengwa, na tarehe. Kutoa invoice isiyo na maelezo ya VAT ni ukiukwaji wa sheria ya VAT. Biashara nyingi zinatekeleza hii kupitia mfumo wa EFD."),

p("Nikiwa na biashara mpya, nianzie lini kuomba usajilishaji wa VAT?",
  "Anza kufuatilia mauzo yako ya kila mwezi mara tu biashara inapoanza. Tazama kipindi kinachozunguka cha miezi 12 — mara tu mauzo yanafika au yanakaribia TZS 200M, omba usajilishaji haraka. Usisubiri mpaka umezidi kizingiti kwa muda mrefu — usajilishaji wa kuchelewa unakuletea faini. Wahasibu au mshauri wa kodi wanaweza kukusaidia kufuatilia mauzo na kujua wakati mzuri wa kuomba."),

p("Bidhaa za chakula Tanzania — zinalipiwa VAT au zipo katika kundi la zero-rated au exempt?",
  "Bidhaa nyingi za chakula msingi Tanzania zimewekwa katika kundi la zero-rated (0% VAT) au exempt — si kiwango cha kawaida cha 18%. Hata hivyo, si chakula chote ni zero-rated au exempt — bidhaa zilizosindikwa au za anasa zinaweza kulipiwa 18%. Kwa orodha kamili ya bidhaa zero-rated na exempt, thibitisha na TRA (tra.go.tz) au mshauri wa kodi, kwani orodha inaweza kubadilika kila mwaka na Finance Act."),
]

vat_ck1_clean = [x for x in vat_ck1 if dedup_check(x)]
for x in vat_ck1_clean: register(x)
save_ck(vat_ck1_clean, SD, 1)

vat_ck2 = [
p("VAT ya B2C kwa malipo ya kielektroniki ni asilimia ngapi?",
  "Kuanzia Septemba 2025, kiwango cha VAT kwa B2C (biashara kwa mtumiaji wa mwisho) kupitia malipo ya kielektroniki ni asilimia 16. Hii ni tofauti na kiwango cha kawaida cha 18% kwa muamala wa kawaida. Hata hivyo, tangazo kamili la utekelezaji kutoka kwa Kamishna Mkuu wa TRA linangoja kukamilika. Kwa hali ya sasa ya utekelezaji, angalia tra.go.tz au wasiliana na TRA."),

p("Tofauti kati ya bidhaa zero-rated na exempt kwa VAT ni nini?",
  "Zero-rated: bidhaa zinazolipiwa VAT ya 0% — biashara inaweza kudai pembejeo ya VAT (input VAT) kwenye ununuzi. Exempt: bidhaa ambazo haziko ndani ya mfumo wa VAT kabisa — biashara haiwezi kudai pembejeo. Tofauti hii ni muhimu sana kwa biashara zinazonunua vifaa: kama unauza bidhaa exempt pekee, huwezi kudai input VAT. Wasiliana na mshauri wa kodi au TRA kujua kundi la bidhaa zako."),

p("Ninafanya biashara ya import/export. Je, VAT inaathirije biashara yangu?",
  "Biashara ya import/export ina mfumo maalum wa VAT: (1) Bidhaa zinazoingizwa Tanzania (imports) zinatozwa VAT ya 18% bandarini — unaweza kudai pembejeo ya VAT hii kama umesajiliwa; (2) Bidhaa zinazosafirishwa nje ya Tanzania (exports) mara nyingi ni zero-rated — unauza bila VAT lakini unaweza kudai pembejeo. Mchakato huu una utata — thibitisha na wahasibu au TRA (tra.go.tz) kabla kuanzisha."),

p("Nikiwa sijasajiliwa VAT lakini ninatoza wateja VAT kwenye invoice — ni tatizo?",
  "Ndiyo, hii ni tatizo kubwa sana. Kutoza VAT bila kuwa na usajilishaji wa VAT ni kosa la kisheria. TRA inaweza: (1) kuamrisha ulipe faini; (2) kukufanya ulipe kodi yote uliyokusanya bila ruhusa; (3) kufungua kesi dhidi yako. Ikiwa umekusanya VAT bila usajilishaji, acha mara moja na wasiliana na mshauri wa kodi na TRA (tra.go.tz) kukusaidia kurekebisha hali."),

p("Ni nini maana ya kudai pembejeo ya VAT (input VAT claim)?",
  "Pembejeo ya VAT (input VAT) ni VAT unayolipa kwa mauzo unayonunua kwa biashara yako. Kama biashara yako imesajiliwa VAT, unaweza kudai pembejeo hiyo kurudi dhidi ya VAT unayokusanya kutoka kwa wateja (output VAT). Kwa mfano: ulinunua bidhaa na kulipa VAT ya TZS 50,000 (pembejeo) na ukakusanya VAT ya TZS 80,000 kutoka wateja (output) — unalipa TRA TZS 30,000 tu. Hii inapunguza mzigo wako wa kodi."),

p("Ninaweza kusimama usajilishaji wa VAT (deregister) kama mauzo yangu yameshuka?",
  "Ndiyo. Unaweza kuomba kusimamishwa usajilishaji wa VAT (deregistration) kwa Kamishna wa TRA kama mauzo yako yameshuka chini ya kizingiti (TZS 200M kwa mwaka) kwa muda wa kutosha. Mchakato wa kusimama ni rasmi — lazima uombe kwa Kamishna na uweke hoja. Huwezi kusimama mwenyewe bila idhini ya TRA. Pata msaada wa wahasibu au mshauri wa kodi kufanya ombi hili vizuri."),

p("Nilipiwa faini kwa kuchelewa kusajiliwa VAT. Je, faini ni ngapi?",
  "Adhabu kwa kushindwa kusajiliwa VAT kwa wakati ni: faini ya hadi TZS 200,000 NA/AU kifungo cha miezi 2 hadi 12 PAMOJA NA riba kwenye VAT yote iliyostahili kukusanywa na kutolipwa. Kumbuka: kuchelewa kusajiliwa ni tofauti na kuchelewa kulipa VAT — zote mbili zina adhabu. Kama una tatizo la usajilishaji uliochelewa, wasiliana na TRA (tra.go.tz) na mshauri wa kodi haraka."),

p("Je, benki au taasisi ya fedha inahitaji kusajiliwa VAT Tanzania?",
  "Huduma nyingi za benki na taasisi za fedha zipo katika kundi la exempt (isiyostahili VAT). Hata hivyo, benki zinatoa baadhi ya huduma zinazostahili VAT, kama vile huduma za usimamizi au ushauri. Benki zilizofanya mauzo yanayostahili VAT zaidi ya kizingiti cha usajilishaji lazima zisajiliwe VAT. Kwa hali maalum ya taasisi ya fedha, thibitisha na Kamishna wa TRA au wahasibu waliobobea katika sekta ya fedha."),

p("VAT return iwasilishwe lini na itajazaje?",
  "VAT return iwasilishwe ifikapo tarehe 20 ya mwezi unaofuata — kwa mfano, VAT ya Januari iwasilishwe ifikapo tarehe 20 Februari. Return inaweza kuwasilishwa mtandaoni kupitia mfumo wa TRA (iTax au mfumo wa sasa). Kujaza return: taja jumla ya mauzo yaliyostahili VAT, output VAT uliyokusanya, input VAT uliyodai, na tofauti (VAT inayolipwa au kurejeshewe). Msaada wa wahasibu unapendekezwa kwa biashara mpya."),

p("Je, TRA inaweza kunirudishia VAT kama pembejeo yangu inazidi output VAT?",
  "Ndiyo. Kama input VAT yako (unayolipa kwa ununuzi) inazidi output VAT yako (unayokusanya kutoka wateja), una haki ya kudai rejesho (VAT refund) kutoka TRA. Hii mara nyingi inatokea kwa biashara za export (zinazouza zero-rated). Omba rejesho kupitia Kamishna wa TRA kwa mfumo wa iTax. TRA ina muda maalum wa kukushughulikia — thibitisha taratibu za sasa na TRA (tra.go.tz)."),
]

vat_ck2_clean = [x for x in vat_ck2 if dedup_check(x)]
for x in vat_ck2_clean: register(x)
save_ck(vat_ck2_clean, SD, 2)
print(f"[VAT_REGISTRATION] Total: {len(vat_ck1_clean)+len(vat_ck2_clean)} pairs")

# ═══════════════════════════════════════════════════════════════════════════════
# SDL_COMPLIANCE — 20 pairs
# Required keywords: ilifutwa, viwango, mamlaka, januari, sekta, subsekta, GN605A
# ═══════════════════════════════════════════════════════════════════════════════
SD = "sdl_compliance"

sdl_ck1 = [
p("Amri ya mshahara wa chini ya mwaka 2022 bado inatumika?",
  "Hapana. Amri ya mshahara wa chini ya mwaka 2022 ilifutwa kikamilifu tarehe 31 Desemba 2025. Tangu tarehe 1 Januari 2026, GN605A — Agizo Jipya la Mshahara wa Chini la Sekta Binafsi — ndilo linalotumika. Kutumia viwango vya 2022 baada ya Januari 2026 ni kosa la kisheria. Thibitisha viwango vya sekta yako kwa kupitia GN605A kwenye tanzlii.org au wasiliana na Ofisi ya Kazi."),

p("GN605A ni nini hasa na linianza kutumika?",
  "GN605A ni Amri ya Mshahara wa Chini ya Sekta Binafsi iliyotangazwa rasmi Oktoba 13, 2025. Ilianza kutumika tarehe 1 Januari 2026. Amri hii inabainisha viwango vya mshahara wa chini kwa sekta 16 na subsekta nyingi. Kwa kuwa amri ya 2022 ilifutwa, GN605A ndio mamlaka pekee ya kisheria ya viwango vya mshahara wa chini Tanzania kuanzia Januari 2026."),

p("Sekta yangu ya kilimo (crop/animal) — mshahara wa chini ni ngapi kulingana na GN605A?",
  "Kulingana na GN605A, viwango vilivyothibitishwa kwa sekta ya kilimo (kilimo cha mazao/wanyama) ni TZS 175,000 kwa mwezi — hii ni kiwango cha msingi cha sekta hii. Kiwango hiki kilianza kutumika Januari 2026. Viwango vya sekta ndogo (subsekta) maalum vinaweza kutofautiana — thibitisha viwango vya subsekta yako mahususi kwenye GN605A au kwa Ofisi ya Kazi."),

p("Kiwango cha juu zaidi cha mshahara wa chini Tanzania kwa sekta gani na ni ngapi?",
  "Kulingana na GN605A, kiwango cha juu zaidi kilichothibitishwa ni kwa sekta ya nishati (energy) ya makampuni ya kimataifa — TZS 765,900 kwa mwezi. Kiwango hiki kilianza Januari 2026 baada ya GN605A kubatilisha amri ya 2022 iliyokuwa na viwango vya chini zaidi."),

p("Hoteli ya nyota 5 — mshahara wa chini kwa wafanyakazi ni ngapi kulingana na GN605A?",
  "Kulingana na GN605A, viwango vilivyothibitishwa kwa sekta ya hoteli ni: hoteli za nyota 5 na nyota 4: TZS 375,000 kwa mwezi; baa na mikahawa ya hoteli: TZS 195,000 kwa mwezi. Viwango hivi vilianza Januari 2026. Kama una wasiwasi kuhusu subsekta maalum ya hoteli yako, thibitisha na GN605A yenyewe kupitia tanzlii.org."),

p("Je, GN605A ina kiwango kimoja cha mshahara kwa wafanyakazi wote Tanzania?",
  "Hapana. GN605A haina kiwango kimoja cha wote — ina sekta 16 na subsekta nyingi, kila moja ikiwa na kiwango chake maalum. Viwango vinatofautiana sana kati ya sekta: kutoka TZS 80,000 (wafanyakazi wa nyumbani fulani) hadi TZS 765,900 (nishati ya kimataifa). Kila mwajiri lazima atumie kiwango cha sekta yake — si wastani wa taifa. Thibitisha kiwango cha sekta yako kwa kupitia GN605A kwenye tanzlii.org."),

p("Wafanyakazi wangu wanauliza kuhusu nyongeza ya mshahara wa Januari 2026. Niwaelezeeje?",
  "Elezea hivi: GN605A ilianza kutumika Januari 1, 2026, ikiwa na viwango vipya vya mshahara wa chini kwa sekta zote 16. Viwango vipya vina ongezeko la wastani wa asilimia 33.4 — kutoka TZS 275,060 hadi TZS 358,322 kwa wastani wa taifa. Hata hivyo, kiwango halisi kinategemea sekta na subsekta yako. Angalia GN605A kwa kiwango cha sekta yako maalum, au thibitisha na Ofisi ya Kazi."),

p("Mwajiri anayebaki na viwango vya 2022 baada ya Januari 2026 — anachukuliwa vipi kisheria?",
  "Mwajiri anayebaki na viwango vya amri ya 2022 (iliyofutwa) baada ya Januari 2026 anakiuka GN605A — mamlaka halisi ya kisheria ya sasa. Hii ni ukiukwaji wa Sheria ya Ajira na Mahusiano Kazini. Wafanyakazi wana haki ya kudai malipo yaliyobaki (backpay) tangu Januari 2026. Ofisi ya Kazi (Ministry of Labour) ina mamlaka ya kukagua na kutoza faini. Lipa viwango vya GN605A haraka."),

p("Sekta ya benki za biashara — mshahara wa chini kwa GN605A ni ngapi?",
  "Kulingana na GN605A, viwango vilivyothibitishwa kwa sekta ya benki za biashara (commercial banks) ni TZS 733,000 kwa mwezi. Kiwango hiki kilianza Januari 2026. Ikiwa una wafanyakazi wa benki, hakikisha mshahara wao wa chini hauteremki chini ya kiwango hiki. Kwa subsekta maalum za benki, thibitisha kwenye GN605A yenyewe."),

p("Je, SDL na mshahara wa chini wa GN605A vinaunganika vipi?",
  "Vina uhusiano wa moja kwa moja: mshahara wa chini wa GN605A unabainisha malipo ya chini kabisa kwa wafanyakazi — SDL (Skills Development Levy) ya 3.5% inakokotolewa kutoka jumla ya malipo hayo halisi. Kwa mfano, kama mwajiri analipa mshahara wa TZS 175,000 (kiwango cha kilimo) kwa mfanyakazi, SDL ni 3.5% ya TZS 175,000. Viwango vya GN605A vikiongezeka, msingi wa SDL nao unaongezeka. SDL inatumika kwa wajiri wenye wafanyakazi 10 au zaidi."),
]

sdl_ck1_clean = [x for x in sdl_ck1 if dedup_check(x)]
for x in sdl_ck1_clean: register(x)
save_ck(sdl_ck1_clean, SD, 1)

sdl_ck2 = [
p("Mwajiri wangu analipa chini ya kiwango cha GN605A. Naweza mfanyabiashara wangu nini kisheria?",
  "Ndiyo, una haki. Mwajiri anapaswa kulipa angalau kiwango cha chini cha sekta yako kulingana na GN605A tangu Januari 2026. Hatua unazoweza chukua: (1) toa malalamiko kwa Ofisi ya Kazi ya wilaya yako (Ministry of Labour); (2) omba malipo yaliyobaki (backpay) tangu Januari 2026; (3) unaweza pia kuomba msaada wa Bodi ya Usuluhishi wa Migogoro ya Kazi (CMA). Haki yako inalindwa kisheria."),

p("Kiwango cha chini kabisa cha mshahara Tanzania kwa GN605A ni ngapi?",
  "Kiwango cha chini kabisa kilichothibitishwa katika GN605A ni TZS 80,000 kwa mwezi — hii ni kwa wafanyakazi fulani wa nyumbani (domestic workers). Kiwango cha msingi cha kawaida kwa sekta ambazo hazitajwi wazi ni TZS 175,000 kwa mwezi. Viwango hivi vilianza Januari 2026. Kwa kiwango cha sekta yako maalum, thibitisha kwenye GN605A kupitia tanzlii.org."),

p("Je, ongezeko la mshahara wa GN605A linaathiri PAYE?",
  "Ndiyo. Ongezeko la mishahara kutokana na GN605A linaongeza msingi wa PAYE. Kama ulifanya mahesabu ya PAYE kwa viwango vya zamani (amri ya 2022), lazima uhesabu upya kwa viwango vipya vya GN605A tangu Januari 2026. Mabadiliko makubwa ya mshahara yanaweza kumvusha mfanyakazi kwa mkanda mwingine wa PAYE na kulazimika kulipa kodi zaidi. Fanya ukaguzi wa malipo yako ya PAYE na mshauri wa kodi."),

p("Kampuni yangu ina wafanyakazi katika sekta nyingi — vipi ninabainisha kiwango cha mshahara kwa kila mmoja?",
  "Kila mfanyakazi lazima alipwe kulingana na kiwango cha sekta na subsekta yake maalum kama inavyoainishwa katika GN605A. Huwezi kutumia kiwango kimoja kwa wafanyakazi wote wa sekta tofauti. Hatua: (1) ainisha sekta na subsekta ya kila mfanyakazi kulingana na kazi anayofanya; (2) tazama GN605A kwa kiwango cha sekta hiyo; (3) hakikisha mshahara wake hauteremki chini ya kiwango hicho. Mshauri wa kazi (HR consultant) anaweza kukusaidia."),

p("Je, kampuni za ujenzi zinatumia kiwango gani cha mshahara wa chini?",
  "Kulingana na GN605A, kwa sekta ya ujenzi (construction), viwango vilivyothibitishwa ni pamoja na: Daraja la I (Class I): TZS 515,000 kwa mwezi. Viwango vya madaraja mengine vinaweza kutofautiana — thibitisha kwenye GN605A yenyewe kupitia tanzlii.org kwa kiwango cha daraja la wafanyakazi wako wote wa ujenzi. Viwango hivi vilianza Januari 2026."),

p("Je, makampuni ya mawasiliano (telecom) yana kiwango gani cha mshahara wa chini?",
  "Kulingana na GN605A, kiwango kilichothibitishwa kwa sekta ya mawasiliano (telecommunication) ni TZS 644,000 kwa mwezi. Kiwango hiki kilianza Januari 2026. Makampuni ya mawasiliano yanastahili kulipa angalau kiwango hiki kwa wafanyakazi wao wote wanaofanya kazi katika sekta hiyo. Kwa subsekta maalum za sekta ya mawasiliano, thibitisha kwenye GN605A."),

p("Viwango vya sekta ya uchimbaji madini (mining) ni ngapi kwa GN605A?",
  "Kulingana na GN605A, kiwango kilichothibitishwa kwa sekta ya uchimbaji madini (prospecting/mining) ni TZS 695,000 kwa mwezi. Sekta ya nishati ya kimataifa ina kiwango cha juu zaidi — TZS 765,900. Viwango hivi vilianza Januari 2026 na vinazidi viwango vya amri ya 2022 iliyofutwa. Thibitisha viwango vya subsekta yako maalum ya madini kwenye GN605A."),

p("GN605A ilianza lini na ilifutwa amri gani?",
  "GN605A ilitangazwa rasmi kwenye Gazeti la Serikali tarehe 13 Oktoba 2025. Ilianza kutumika tarehe 1 Januari 2026. Ilifuta kabisa Amri ya Mshahara wa Chini ya Sekta Binafsi ya mwaka 2022 — amri hiyo ya 2022 haina nguvu yoyote ya kisheria tangu tarehe 31 Desemba 2025. Viwango vyote vya mshahara wa sekta binafsi tangu Januari 2026 lazima vitokane na GN605A."),

p("Kama biashara yangu ipo sekta ya viwanda (industrial) — mshahara wa chini ni ngapi?",
  "Kulingana na GN605A, kiwango kilichothibitishwa kwa sekta ya viwanda (industrial) ni TZS 200,000 kwa mwezi. Kiwango hiki kilianza Januari 2026. Ikiwa una wasiwasi kuhusu kama kazi fulani ipo katika sekta ya viwanda au sekta nyingine, thibitisha na GN605A kwenye tanzlii.org au Ofisi ya Kazi ili kuhakikisha unatumia kiwango sahihi cha sekta na subsekta."),

p("SDL 3.5% inakokotolewa kutoka kwa mshahara gani — halisi au kiwango cha chini cha GN605A?",
  "SDL ya 3.5% inakokotolewa kutoka jumla halisi ya malipo ya fedha (gross cash emoluments) unayolipa mfanyakazi — si kutoka kiwango cha chini cha GN605A. Kwa hivyo kama unalipa zaidi ya kiwango cha chini, SDL inakokotolewa kutoka mshahara halisi unaolipwa. SDL inatumika kwa wajiri wenye wafanyakazi 10 au zaidi kwenye Tanzania Bara. Kwa msaada wa mahesabu ya SDL, wasiliana na mshauri wa kodi au TRA (tra.go.tz)."),
]

sdl_ck2_clean = [x for x in sdl_ck2 if dedup_check(x)]
for x in sdl_ck2_clean: register(x)
save_ck(sdl_ck2_clean, SD, 2)
print(f"[SDL_COMPLIANCE] Total: {len(sdl_ck1_clean)+len(sdl_ck2_clean)} pairs")

# ═══════════════════════════════════════════════════════════════════════════════
# BRELA_REGISTRATION — 20 pairs
# Required keywords: usajilishaji, kufunga, ushirikiano, certificate, limited, company, trader
# NEVER state specific TZS fees — always direct to brela.go.tz
# ═══════════════════════════════════════════════════════════════════════════════
SD = "brela_registration"

brela_ck1 = [
p("Ninataka kusajili biashara ya sole trader (mfanyabiashara mmoja). Nianze wapi?",
  "Usajilishaji wa sole trader (business name) unafanywa na BRELA. Hatua: (1) angalia upatikanaji wa jina la biashara kwenye mfumo wa ORS (ors.brela.go.tz); (2) hifadhi jina ukilipenda; (3) jaza fomu za usajilishaji wa jina la biashara; (4) lipa ada husika; (5) pokea hati ya usajilishaji. Kwa ada za sasa na fomu maalum, angalia brela.go.tz au mfumo wa ORS — ada zinaweza kubadilika."),

p("Tofauti kati ya sole trader na company limited by shares (kampuni) ni nini?",
  "Sole trader: mfanyabiashara mmoja, hakuna kujitenga kati ya mali ya biashara na mali ya kibinafsi — madeni ya biashara yanaweza kulipwa kutoka mali ya kibinafsi. Company (limited): ni chombo huru cha kisheria — deni la kampuni ni la kampuni tu, si la wanahisa wenyewe (limited liability). Kusajili kampuni ni ngumu zaidi na gharama zaidi, lakini inalinda mali yako ya kibinafsi. Chaguo linategemea ukubwa na hatari za biashara yako."),

p("Kampuni limited by shares Tanzania — mchakato wa usajilishaji ni upi?",
  "Usajilishaji wa kampuni limited by shares kupitia BRELA: (1) angalia na hifadhi jina la kampuni (ORS); (2) andaa Memorandum na Articles of Association; (3) jaza fomu za kuanzisha kampuni; (4) lipa ada za usajilishaji; (5) pokea Certificate of Incorporation. Kwa ada za sasa, hatua kamili, na fomu maalum, angalia brela.go.tz au mfumo wa ORS (ors.brela.go.tz) — usitegemee taarifa za zamani za ada kwani zinaweza kubadilika."),

p("Certificate of Incorporation ni nini na inathibitisha nini?",
  "Certificate of Incorporation ni hati rasmi inayotolewa na BRELA inayothibitisha kwamba kampuni imesajiliwa kisheria na kuanza kuwa chombo huru cha kisheria (legal entity). Hati hii ina: nambari ya usajilishaji wa kampuni, jina rasmi la kampuni, aina ya kampuni, na tarehe ya usajilishaji. Inahitajika kufungua akaunti ya benki, kuingia mikataba, na kwa matumizi mengi ya kisheria. Hifadhi salama."),

p("Je, partnership (ushirikiano) nchini Tanzania inaweza kusajiliwa rasmi?",
  "Ndiyo. Partnership (ushirikiano wa kibiashara) inaweza kusajiliwa BRELA kwa aina mbalimbali — kama business name ya pamoja au kwa njia nyingine. Mbia lazima waandike mkataba wa ushirikiano (partnership deed) ukibainisha majukumu, faida, na hasara. Kwa utaratibu wa sasa wa usajilishaji wa partnership na ada husika, thibitisha na BRELA moja kwa moja (brela.go.tz) — mahitaji yanaweza kubadilika."),

p("Annual return ya BRELA ni nini na hulipwa lini?",
  "Annual return ni taarifa ya mwaka inayowasilishwa BRELA na kila kampuni iliyosajiliwa. Ina taarifa kuhusu wakurugenzi, wanahisa, na anwani ya ofisi. Annual return hulipwa na kuwasilishwa katika mwezi ule ule mwaka wowote ambao kampuni ilisajiliwa — si Desemba pekee. Kwa ada ya sasa ya annual return na taratibu, angalia brela.go.tz au mfumo wa ORS — usitegemee ada zilizopita kwani zinaweza kubadilika."),

p("Kampuni yangu haijalipi annual return kwa miaka miwili — adhabu ni nini?",
  "Kuchelewa kuwasilisha annual return kunasababisha faini ya kila mwezi wa uchelewaji — kwa kampuni za ndani, faini ni kwa kila mwezi au sehemu ya mwezi. Kwa kampuni za kigeni (Section XII), faini ni kwa kiwango cha dola. Adhabu hukusanyika kila mwezi — usiendelee kuchelewa. Kwa kiasi halisi cha faini na ada za sasa, angalia brela.go.tz au ORS — kiasi kinaweza kubadilika. Wasilisha annual return haraka."),

p("Ninaweza kubadilisha jina la kampuni yangu iliyosajiliwa BRELA?",
  "Ndiyo. Unaweza kuomba kubadilisha jina la kampuni kwa BRELA kupitia mchakato rasmi. Hatua: (1) angalia upatikanaji wa jina jipya kwenye ORS; (2) pata idhini ya wanahisa kwa resolution ya mkutano mkuu; (3) jaza fomu za kubadilisha jina na lipa ada husika; (4) BRELA itatoa Certificate of Change of Name. Kwa ada za sasa na fomu maalum, angalia brela.go.tz."),

p("Mbia wangu anataka kutoka kwenye ushirikiano wetu wa biashara. Nifanye nini kisheria?",
  "Kutoka kwa ushirikiano kunahitaji: (1) ukaguzi wa mkataba wa ushirikiano (partnership deed) — mara nyingi unaeleza utaratibu wa kutoka; (2) makubaliano ya kutathmini na kugawana mali ya ushirikiano; (3) kama ushirikiano umesajiliwa BRELA, toa taarifa rasmi ya mabadiliko kwa BRELA; (4) wasiliana na mwanasheria kuhakikisha haki na wajibu wote vinazingatiwa. Usifanye mabadiliko ya kisheria bila msaada wa mwanasheria."),

p("Je, kufungua kampuni Tanzania kama mgeni (non-citizen) ni halali?",
  "Raia wa kigeni anaweza kusajili kampuni Tanzania (kwa mfano, kampuni ya aina Private Limited Company) — hii si shughuli iliyokatazwa na GN487A. GN487A inakataza raia wa kigeni kufanya baadhi ya shughuli za biashara moja kwa moja — kama jumla/rejareja, ukarabati wa simu, n.k. Lakini kuwa mwanahisa au mkurugenzi wa kampuni halisi ni tofauti. Thibitisha hali yako maalum na mwanasheria wa biashara kabla ya kuanza."),
]

brela_ck1_clean = [x for x in brela_ck1 if dedup_check(x)]
for x in brela_ck1_clean: register(x)
save_ck(brela_ck1_clean, SD, 1)

brela_ck2 = [
p("Kufunga kampuni Tanzania — mchakato ni upi?",
  "Kufunga kampuni rasmi (winding up/striking off) ni mchakato rasmi kupitia BRELA. Aina mbili: (1) Striking off — kampuni ndogo isiyofanya biashara inaweza kuomba kufutwa na BRELA; (2) Winding up — kufunga kampuni yenye madeni au michakato ya kibiashara, inayohitaji mwanasheria. Katika hali zote mbili, lazima kodi zote zilipwe kwanza na TRA ithibitishe kutokuwa na madeni ya kodi. Wasiliana na mwanasheria na BRELA (brela.go.tz) kwa utaratibu kamili."),

p("Ningependa kuhama biashara yangu kutoka sole trader hadi kampuni limited. Nifanye nini?",
  "Huwezi tu 'kubadilisha' sole trader hadi kampuni — lazima usajili kampuni mpya kwa BRELA na kisha uhamishe shughuli za biashara kwenda kampuni. Hatua: (1) sajili kampuni mpya kupitia ORS (ors.brela.go.tz); (2) fungua akaunti ya benki ya kampuni; (3) hamisha mikataba na wateja wa biashara; (4) update usajilishaji wa TRA na kodi; (5) sole trader ya zamani inaweza kubaki au kufungwa. Wasiliana na mshauri wa kodi na mwanasheria kwa uhamisho salama."),

p("TIN ya kampuni yangu — ninaitoa BRELA au TRA?",
  "TIN (Taxpayer Identification Number) inatoka TRA — si BRELA. BRELA inakupa nambari ya usajilishaji wa kampuni (Certificate of Incorporation). Baada ya kupata certificate ya BRELA, unapeleka TRA kupata TIN ya kampuni. Hatua ni tofauti: BRELA kwanza (usajilishaji wa kampuni), kisha TRA (usajilishaji wa kodi). Biashara zote lazima ziwe na TIN kutoka TRA kabla ya kufanya biashara."),

p("Wakurugenzi wa kampuni lazima wabadilishwe vipi kwenye rekodi za BRELA?",
  "Mabadiliko ya wakurugenzi lazima yataarifiwe BRELA ndani ya muda uliowekwa baada ya mabadiliko. Utaratibu: (1) pata idhini ya bodi ya wakurugenzi au wanahisa kwa resolution; (2) jaza fomu za mabadiliko ya wakurugenzi; (3) wasilisha pamoja na nyaraka zinazohitajika na lipa ada husika. Kwa fomu maalum na ada za sasa, angalia brela.go.tz au mfumo wa ORS. Kushindwa kutoa taarifa kunasababisha faini."),

p("Ninataka kusajili biashara ya ushirikiano (partnership) na familia yangu. Ada ni ngapi?",
  "Ada za usajilishaji wa ushirikiano na taratibu maalum zinapatikana brela.go.tz au kwenye mfumo wa ORS (ors.brela.go.tz). Usitegemee nambari za ada zilizotolewa na watu wengine au kwenye tovuti zisizo rasmi — ada za BRELA zinaweza kubadilika kwa amri ya waziri. Tembelea brela.go.tz au piga simu BRELA moja kwa moja kwa ada za leo."),

p("Je, kampuni yangu inaweza kuwa na tawi (branch) katika mji mwingine Tanzania?",
  "Ndiyo. Kampuni iliyosajiliwa Tanzania inaweza kufungua matawi katika miji mingine bila kusajili kampuni mpya. Hata hivyo, matawi lazima yatajwe kwenye rekodi za BRELA na TRA. Kwa makampuni ya kigeni yanayofungua tawi Tanzania, kuna mchakato maalum wa usajilishaji wa kampuni ya kigeni (foreign branch) kupitia BRELA. Thibitisha mahitaji kamili na BRELA (brela.go.tz)."),

p("Je, certificate ya usajilishaji wa biashara lazima ionekane wapi?",
  "Kwa biashara zilizosajiliwa chini ya Business Names Act, certificate ya usajilishaji (au nakala yake iliyoidhinishwa) lazima ionekane mahali panaoonekana wazi kwenye biashara yako — kawaida ukutani wa ofisi au duka. Kwa kampuni, Certificate of Incorporation lazima ihifadhiwe ofisini. Kukosa kuonyesha certificate kunaweza kusababisha adhabu kutoka mamlaka husika."),

p("Ninaweza kusajili biashara yangu online bila kwenda ofisini BRELA?",
  "Ndiyo. BRELA ina mfumo wa usajilishaji mtandaoni (ORS) kwenye ors.brela.go.tz unaokuruhusu kusajili biashara online. Mfumo huu unakuruhusu: kuangalia upatikanaji wa jina, kujaza fomu, kulipa ada online, na kupata nyaraka za usajilishaji kidigitali. Hata hivyo, baadhi ya hatua zinaweza bado kuhitaji ziara ya mwili — thibitisha hali ya sasa ya mfumo wa ORS kwenye brela.go.tz."),

p("Je, kuna tofauti ya ada kati ya kusajili kampuni ya ndani na kampuni ya kigeni (foreign company)?",
  "Ndiyo, ada za usajilishaji wa kampuni ya kigeni (foreign company) ni tofauti na za kampuni za ndani — mara nyingi ni za juu zaidi. Kwa ada za sasa za aina zote za usajilishaji, angalia ratiba rasmi ya ada kwenye brela.go.tz au mfumo wa ORS (ors.brela.go.tz). Usitegemee takwimu za ada zilizotolewa na vyanzo visivyo rasmi kwani zinaweza kuwa za zamani."),

p("Hati gani zinahitajika kusajili kampuni ndogo (Private Limited Company) Tanzania?",
  "Hati za kawaida zinazohitajika ni: (1) Memorandum of Association; (2) Articles of Association; (3) fomu ya maombi ya usajilishaji; (4) nakala za vitambulisho (passport/kitambulisho) vya wakurugenzi na wanahisa; (5) anwani ya ofisi ya usajilishaji. Kwa orodha kamili na ya sasa ya hati zinazohitajika, angalia brela.go.tz au ORS — mahitaji yanaweza kubadilika. Msaada wa mwanasheria au wakala wa usajilishaji unapendekezwa."),
]

brela_ck2_clean = [x for x in brela_ck2 if dedup_check(x)]
for x in brela_ck2_clean: register(x)
save_ck(brela_ck2_clean, SD, 2)
print(f"[BRELA_REGISTRATION] Total: {len(brela_ck1_clean)+len(brela_ck2_clean)} pairs")

# ═══════════════════════════════════════════════════════════════════════════════
# NSSF_CONTRIBUTIONS — 20 pairs
# Required keywords: ifikapo, inayopelekwa, usajilishaji, anachangia, uanachama, adhabu
# ═══════════════════════════════════════════════════════════════════════════════
SD = "nssf_contributions"

nssf_ck1 = [
p("Mwajiri mpya anapaswa kusajili na NSSF lini?",
  "Kila mwajiri lazima asajiliwe NSSF haraka iwezekanavyo baada ya kuanza kuajiri. Usajilishaji wa NSSF lazima ufanyike kabla ya kuanza kulipa mishahara ya kwanza ya wafanyakazi. Kwa tarehe halisi ya mwisho ya usajilishaji na hati zinazohitajika, thibitisha na NSSF (nssf.or.tz) moja kwa moja — mahitaji yanaweza kubadilika. Kuchelewa kusajili kunaweza kusababisha adhabu na malipo ya nyuma."),

p("NSSF inakokotolewa kutoka kwa mshahara gani na ni asilimia ngapi?",
  "NSSF jumla ni asilimia 20 ya mshahara wa jumla (gross wage). Mgawanyo wa kawaida: mwajiri anachangia asilimia 10 na mfanyakazi anachangia asilimia 10. Hata hivyo, kuna mgawanyo mwingine halali: mwajiri asilimia 15 na mfanyakazi asilimia 5; au mwajiri asilimia 20 na mfanyakazi asilimia 0 (mwajiri analipa yote). Chaguo la mgawanyo ni la mwajiri — lakini jumla lazima iwe asilimia 20."),

p("Mwajiri wangu anasema atalipa NSSF yote mwenyewe — hii ni halali?",
  "Ndiyo, hii ni halali. Mwajiri anaweza kulipa NSSF yote (asilimia 20) bila kukata sehemu ya mfanyakazi — hii ni mgawanyo wa 20%+0%. Sheria ya NSSF inaruhusu mgawanyo wa 10+10, 15+5, au 20+0. Mfanyakazi hapigwi marufuku kupata manufaa haya. Hata hivyo, jumla ya asilimia 20 ya mshahara lazima iwasilishwe NSSF bila kujali mgawanyo uliochaguliwa."),

p("Je, mfanyakazi anaweza kukataa mchango wake wa NSSF?",
  "Hapana. Uanachama wa NSSF ni wa lazima kwa wafanyakazi wote wa sekta binafsi Tanzania — si chaguo. Mwajiri lazima asajili mfanyakazi katika NSSF mara tu anapoanza kazi. Mfanyakazi hawezi kuomba kutokuwa mwanachama. Kutowasilisha mchango wa NSSF ni ukiukwaji wa kisheria ambao unaweza kusababisha adhabu kwa mwajiri."),

p("Malipo ya NSSF yanawasilishwa TRA au NSSF moja kwa moja?",
  "Malipo ya NSSF yanawasilishwa moja kwa moja kwa NSSF — si TRA. NSSF ina mfumo wake wa ukusanyaji. Mwajiri anaweza kulipa kupitia benki au mtandaoni kupitia mfumo wa NSSF (nssf.or.tz). Tofauti na PAYE na SDL ambazo zinakwenda TRA, NSSF inakwenda shirika lake la mfuko wa pensheni. Hakikisha unapeleka malipo kwenye akaunti sahihi ya NSSF."),

p("Tarehe ya mwisho ya kupeleka malipo ya NSSF ni lini kila mwezi?",
  "Malipo ya NSSF inayopelekwa lazima ifikapo mwishoni mwa mwezi unaofuata mwezi wa malipo ya mishahara. Kwa mfano, mishahara ya Januari — NSSF inayopelekwa ifikapo mwishoni mwa Februari. Kwa tarehe halisi ya mwisho ya sasa, thibitisha na NSSF (nssf.or.tz) moja kwa moja kwani tarehe inaweza kubadilika."),

p("NSSF haijalipiwa kwa miezi mitatu — adhabu ni nini?",
  "Adhabu ya kutolipa NSSF kwa wakati ni asilimia 5 kwa kila mwezi wa uchelewaji wa malipo. Adhabu hukusanyika kila mwezi — uchelewaji wa miezi mitatu unaweza kuwa na adhabu ya asilimia 15 ya kiasi kilichokosekana. Zaidi ya hayo, NSSF inaweza kufungua kesi dhidi ya mwajiri. Lipa malipo yote pamoja na adhabu haraka iwezekanavyo na wasiliana na NSSF kupanga mpango wa ulipaji kama haiwezekani kulipa mara moja."),

p("Je, mwajiri mdogo mwenye wafanyakazi 3 tu anahitaji kulipa NSSF?",
  "Ndiyo. NSSF inatumika kwa wajiri WOTE wanaomiliki wafanyakazi Tanzania — hakuna kizingiti cha chini cha idadi ya wafanyakazi. Hata mwajiri mwenye mfanyakazi 1 lazima asajili na kulipa NSSF. Tofauti na SDL (ambayo inahitaji wafanyakazi 10+), NSSF inatoka mfanyakazi wa kwanza. Sajili na NSSF mara tu unapoajiri mtu wa kwanza."),

p("Wafanyakazi wa muda (part-time/casual) — lazima walipwe NSSF?",
  "Ndiyo, wafanyakazi wa muda au wa msimu wanaofanya kazi Tanzania kwa malipo wanastahili mchango wa NSSF. Mwajiri lazima aadhimishe wajibu huu. Kwa taratibu maalum za aina tofauti za ajira (casual, contract, part-time), thibitisha na NSSF (nssf.or.tz) — kuna kanuni maalum zinazoweza kutofautiana."),

p("Kampuni yangu ina wafanyakazi wanaolipwa kwa wakati na wanaolipwa kwa kipande — wote wanalipwa NSSF?",
  "Kwa ujumla, wafanyakazi wote wanaoajiriwa na kampuni — iwe wanalipwa kwa wakati au kwa kipande — wana haki ya NSSF. Msingi wa hesabu ni malipo halisi wanayopokea. Kwa hali maalum ya aina tofauti za malipo na jinsi ya kuhesabu NSSF, thibitisha na NSSF (nssf.or.tz) au mshauri wa HR ili kuhakikisha unazingatia sheria vizuri."),
]

nssf_ck1_clean = [x for x in nssf_ck1 if dedup_check(x)]
for x in nssf_ck1_clean: register(x)
save_ck(nssf_ck1_clean, SD, 1)

nssf_ck2 = [
p("Mwajiri anaweza kubadilisha mgawanyo wa NSSF kutoka 10+10 hadi 15+5 — ni rahisi?",
  "Ndiyo, mwajiri anaweza kubadilisha mgawanyo wa NSSF kwa kuchagua mgawanyo mpya — 10+10 (kawaida), 15+5, au 20+0 (mwajiri analipa yote). Mabadiliko yanafanywa kwa taarifa kwa NSSF na kwa wafanyakazi. Jumla lazima ibaki asilimia 20. Kwa utaratibu rasmi wa kubadilisha mgawanyo, wasiliana na NSSF (nssf.or.tz) au ofisi ya NSSF karibu nawe."),

p("NSSF inanisaidia vipi wakati wa kustaafu?",
  "NSSF inatoa mafao ya pensheni ukitimia umri wa miaka 60 (55 kwa sekta ya madini) na ukiwa na angalau miezi 180 ya mchango (miaka 15). Mafao yanajumuisha: pensheni ya kila mwezi, mafao ya ulemavu, mafao ya kufiwa. Kwa mafao kamili na jinsi ya kudai, thibitisha na NSSF (nssf.or.tz) — masharti yanaweza kuwa na masharti zaidi kulingana na muda wa uanachama."),

p("Nikiwa na biashara yangu mwenyewe (self-employed), naweza kujisajili NSSF?",
  "Ndiyo. Wajasiriamali wanaojitegemea (self-employed) wanaweza kujisajili NSSF kwa hiari. Hii inakupa mwenyewe ufikiaji wa mafao ya pensheni na ulinzi baadaye. Kwa taratibu za usajilishaji wa kujitegemea na viwango vya mchango, thibitisha na NSSF (nssf.or.tz) moja kwa moja. Usajilishaji huu si wa lazima kwa self-employed, lakini unapendekezwa kwa usalama wa baadaye."),

p("Je, NSSF na PPF (Parastatal Pensions Fund) ni tofauti — wafanyakazi wa sekta gani wanakwenda wapi?",
  "Ndiyo, ni tofauti: NSSF inahudumia wafanyakazi wa sekta binafsi Tanzania. PPF inahudumia wafanyakazi wa mashirika ya umma (parastatal) na serikali. Wafanyakazi wa sekta binafsi wanachangia NSSF — si PPF. Kama mfanyakazi anasogea kati ya sekta binafsi na serikali, anachangia shirika linalolingana na mwajiri wake wa wakati huo. Kwa shaka kuhusu shirika gani, thibitisha na mwajiri wako au NSSF/PPF moja kwa moja."),

p("Mwajiri wangu hakusajili NSSF tangu nilipoingia kazi — nina haki ya kudai chochote?",
  "Ndiyo. Una haki ya kudai mchango wako wote wa NSSF uliokosekana. Hatua: (1) ripoti kwa NSSF (nssf.or.tz) ukitoa ushahidi wa miaka ya kazi (karatasi za mshahara, barua ya ajira, n.k.); (2) NSSF itachunguza na kuamrisha mwajiri wako kulipa mchango wote pamoja na adhabu; (3) unaweza pia wasiliana na Ofisi ya Kazi. Haki yako ya uanachama wa NSSF inalindwa kisheria — usikae kimya."),

p("Malipo ya NSSF yanaingia kwenye akaunti yangu ya NSSF mara moja?",
  "Malipo ya mwajiri yanaingia kwenye akaunti yako ya NSSF baada ya kuthibitishwa — mara nyingi ndani ya siku chache hadi wiki moja baada ya mwajiri kulipa. Unaweza kuangalia akaunti yako na mizania ya mchango kupitia mfumo wa mtandaoni wa NSSF (nssf.or.tz) au ofisi yoyote ya NSSF. Kama malipo hayaonekani kwa muda mrefu, wasiliana na NSSF moja kwa moja."),

p("Je, kampuni inahitaji kutoa slip ya NSSF kwa kila mfanyakazi kila mwezi?",
  "Mwajiri ana wajibu wa kumwarifu mfanyakazi kuhusu mchango wake wa NSSF — mara nyingi hufanywa kupitia pay slip ya kila mwezi inayoonyesha mchango wa mfanyakazi na mwajiri. Ingawa sheria haielezi aina maalum ya taarifa, uwazi katika malipo ya NSSF ni sehemu ya haki za mfanyakazi. Fanya desturi ya kutoa pay slip inayoonyesha NSSF kwa uwazi."),

p("Mwajiri wangu analipa NSSF kwa kiwango cha chini (underpaying). Ninajuaje?",
  "Angalia pay slip yako — thibitisha asilimia 10 au mgawanyo uliokubaliwa unakokotolewa kutoka mshahara wako wa jumla halisi. Kisha thibitisha na rekodi zako za akaunti ya NSSF kwamba kiasi kilichokatwa kweli kweli kimepelekwa NSSF. Kama mwajiri analipa kiasi kidogo kuliko inavyopaswa, ripoti tofauti kwa NSSF (nssf.or.tz) au Ofisi ya Kazi. Underpayment wa NSSF ni ukiukwaji wa kisheria."),

p("NSSF inatoa mafao ya kifo — familia yangu itanufaika vipi?",
  "Ndiyo. NSSF inatoa mafao ya kifo (death benefits) kwa familia ya mwanachama aliyefariki. Mafao yanaweza kujumuisha: malipo ya mkupuo kwa wahusika walioorodheshwa, msaada wa mazishi, na pensheni kwa watoto au mwenzi. Kiasi na masharti ya mafao yanategemea muda wa uanachama na michango iliyolipwa. Kwa maelezo kamili ya mafao ya kifo na jinsi ya kudai, thibitisha na NSSF (nssf.or.tz)."),

p("Je, mchango wa NSSF unaweza kukatwa kutoka pensheni au malipo mengine ya mwisho wa ajira?",
  "Hapana — mchango wa NSSF hautolipiwa pensheni au malipo ya mwisho (end of service benefits). Mchango wa NSSF unakokotolewa kutoka mshahara wa kawaida (gross wages) tu. Malipo ya mwisho wa ajira kama vile gratuity, severance pay, au malipo ya likizo yanajumuishwa au hayajumuishwi kulingana na sheria ya kazi na mkataba — thibitisha hali maalum na mshauri wa HR au Ofisi ya Kazi."),
]

nssf_ck2_clean = [x for x in nssf_ck2 if dedup_check(x)]
for x in nssf_ck2_clean: register(x)
save_ck(nssf_ck2_clean, SD, 2)
print(f"[NSSF_CONTRIBUTIONS] Total: {len(nssf_ck1_clean)+len(nssf_ck2_clean)} pairs")

# ═══════════════════════════════════════════════════════════════════════════════
# OSHA_REGISTRATION — 10 pairs
# Required keywords: kumwajiri, kushindwa, adhabu, kufungwa, ukaguzi, mahali
# Penalties from locked_facts: TZS 1M-5M OR 12 months OR both; TZS 100K/day continuing
# ═══════════════════════════════════════════════════════════════════════════════
SD = "osha_registration"

osha_ck1 = [
p("OSHA inasimamia maeneo yote ya kazi au sekta fulani peke yake?",
  "OSHA inasimamia mahali pote pa kazi Tanzania Bara — hakuna sekta au ukubwa wa biashara unaoweza kusamehewa. Hata biashara ndogo mwenye mfanyakazi 1 analazimika kuzingatia mahitaji ya OSHA. Sheria ya Usalama na Afya Mahali pa Kazi (OHS Act No. 5 of 2003) inatumika kwa wote. Kusajili mahali pa kazi na kupata cheti cha usajilishaji wa OSHA ni wajibu wa kila mwajiri."),

p("Adhabu ya kushindwa kusajili mahali pa kazi na OSHA ni nini?",
  "Kwa kushindwa kusajili mahali pa kazi na OSHA: faini ya TZS 1,000,000 hadi TZS 5,000,000 AU kifungo cha hadi miezi 12 gerezani AU vyote viwili. Kwa makosa yanayoendelea (continuing offence) — kama vile kubaki bila usajilishaji — adhabu ya ziada ya TZS 100,000 kwa kila siku inayoendelea inaweza kutolewa. Adhabu hizi zinatoka OHS Act No. 5 of 2003."),

p("Mwajiri lazima afanye nini ukaguzi wa OSHA anapotembelea biashara?",
  "Wakati wa ukaguzi wa OSHA: (1) karibishe mkaguzi — kukataa ukaguzi ni ukiukwaji wa ziada; (2) toa nyaraka zote zinazohusiana na usalama — cheti cha OSHA, rekodi za tathmini ya hatari, mafunzo ya wafanyakazi; (3) onyesha mkaguzi mahali pote pa kazi anapoomba; (4) jibu maswali ya mkaguzi kwa uaminifu; (5) kama mkaguzi anatoa maelekezo ya kurekebisha, ufuate kwa wakati. Ushirikiano kamili na OSHA ni faida yako mwenyewe."),

p("Je, OSHA inaweza kufunga biashara yangu bila taarifa ya awali?",
  "Ndiyo. OSHA ina mamlaka ya kufunga biashara mara moja (prohibition notice) kama wanaona hatari ya dharura kwa usalama wa wafanyakazi. Kufungwa kunaweza kutokea bila taarifa ya awali kama hali ya hatari ipo. Hatua za kawaida za ukaguzi wa kawaida — ambazo si dharura — mara nyingi hukuja na taarifa na muda wa kurekebisha. Kuzingatia mahitaji yote ya OSHA ndiyo njia pekee ya kuepuka hatua kali."),

p("Nikiwa kumwajiri wafanyakazi, OSHA inataka nini kutoka kwangu mara tu?",
  "Mara tu unapoanza kumwajiri: (1) sajili mahali pako pa kazi na OSHA (osha.go.tz); (2) fanya tathmini ya hatari za usalama mahali pa kazi; (3) andaa sera ya usalama na afya; (4) hakikisha vifaa vya usalama vipo — kinga za moto, msaada wa kwanza, n.k.; (5) mpe mfanyakazi mafunzo ya usalama. Usisalie bila usajilishaji wa OSHA — adhabu zinaanza tangu siku ya kwanza ya ukiukwaji."),

p("Biashara yangu ya duka ndogo mwenye wafanyakazi 2 — inahitaji usajilishaji wa OSHA?",
  "Ndiyo. OSHA inatumika kwa WOTE wanaomiliki mahali pa kazi na wafanyakazi — hakuna kizingiti cha chini cha idadi ya wafanyakazi. Duka lako lenye wafanyakazi 2 linalazimika kuzingatia OHS Act Na. 5 wa 2003. Usajilishaji, tathmini ya hatari, na kuhakikisha usalama ni wajibu wako kama mwajiri. Wasiliana na OSHA (osha.go.tz) kwa hatua za usajilishaji."),

p("Je, mkaguzi wa OSHA anaweza kukuambia kufunga mashine au zana fulani?",
  "Ndiyo. Mkaguzi wa OSHA ana mamlaka ya kutoa amri ya kusimamisha (improvement notice au prohibition notice) kwa mashine, zana, au mchakato wowote unaosababisha hatari kwa usalama. Mashine au eneo linaloweza kusababisha madhara lazima lisimamishwe hadi hatari imeondolewa. Kupinga amri ya OSHA ni kosa zito. Fuata maelekezo ya mkaguzi na ufanye marekebisho yanayohitajika haraka."),

p("Wafanyakazi wangu wanafanya kazi usiku — OSHA ina mahitaji maalum?",
  "Ndiyo. Kazi ya usiku ina mahitaji ya ziada ya usalama — taa ya kutosha, usalama wa mahali pake, na kuhakikisha wafanyakazi wana njia salama za kutoka. OSHA inazingatia mazingira ya kazi usiku wakati wa ukaguzi. Fanya tathmini ya hatari maalum kwa kazi ya usiku na weka hatua za usalama zinazofaa. Thibitisha mahitaji kamili na OSHA (osha.go.tz)."),

p("OSHA inashughulikia malalamiko ya wafanyakazi kuhusu usalama mahali pa kazi?",
  "Ndiyo. Wafanyakazi wanaweza toa malalamiko ya usalama moja kwa moja kwa OSHA (osha.go.tz) — hata bila taarifa ya mwajiri kwanza. Malalamiko yanaweza kusababisha ukaguzi wa ghafla. Kama mwajiri, kushughulikia malalamiko ya usalama kwa uzito na haraka ni bora — kusubiri OSHA ikuje kunaweza kusababisha adhabu kubwa. Anzisha njia ya ndani ya malalamiko ya usalama ili kutatua matatizo mapema."),

p("Adhabu ya kuendelea kufanya kazi bila usajilishaji wa OSHA kwa miezi 3 itakuwa ngapi?",
  "Adhabu ya msingi ni TZS 1,000,000 hadi TZS 5,000,000 — hii ni kwa kosa la awali. Kwa kosa linaloendelea (continuing offence), adhabu ya ziada ya TZS 100,000 kwa kila siku inayoendelea inaweza kutolewa. Kwa miezi 3 ya kukiuka (siku 90 za kazi), adhabu ya ziada inaweza kuwa hadi TZS 9,000,000 — juu ya adhabu ya msingi. Jumla inaweza kufikia zaidi ya TZS 14,000,000. Sajili na OSHA haraka (osha.go.tz)."),
]

osha_ck1_clean = [x for x in osha_ck1 if dedup_check(x)]
for x in osha_ck1_clean: register(x)
save_ck(osha_ck1_clean, SD, 1)
print(f"[OSHA_REGISTRATION] Total: {len(osha_ck1_clean)} pairs")

# ═══════════════════════════════════════════════════════════════════════════════
# OUT_OF_CORPUS — 10 pairs
# Required keywords: maarifa, mshauri
# Every output MUST contain one of: nje ya maarifa yangu, swali hili liko nje,
#   sina uhakika, mshauri wa kodi, wasiliana na mshauri
# answer_type: out_of_corpus_refusal
# ═══════════════════════════════════════════════════════════════════════════════
SD = "out_of_corpus"

ooc_ck1 = [
p("Ninaweza kuwekeza kwenye Bitcoin au cryptocurrency Tanzania — ni salama?",
  "Swali hili liko nje ya maarifa yangu ya utaalamu wa biashara na kodi za Tanzania. Suala la kuwekeza kwenye cryptocurrency linahusisha udhibiti wa kifedha ambao unabadilika haraka na una maswali ya kisheria yanayohusisha Benki Kuu ya Tanzania (BoT). Kwa ushauri wa uwekezaji wa fedha, wasiliana na mshauri wa fedha aliyeidhinishwa au Benki Kuu ya Tanzania (bot.go.tz)."),

p("Nataka kununua hisa kwenye soko la hisa la New York (NYSE). Nifanye vipi Tanzania?",
  "Swali hili liko nje ya maarifa yangu. Kununua hisa katika masoko ya kimataifa kama NYSE kunahusisha kanuni za fedha za kimataifa, ruhusa za Benki Kuu ya Tanzania, na sheria za mabadiliko ya fedha. Nje ya maarifa yangu ya ushauri wa kodi na biashara Tanzania. Wasiliana na mshauri wa fedha aliyehitimu au Benki Kuu ya Tanzania (bot.go.tz) kwa mwelekeo sahihi."),

p("Mke wangu anataka kunioa talaka — nifanye nini kisheria?",
  "Sina uhakika ni mshauri sahihi kwa swali hili. Maswali ya talaka na familia ni nje ya maarifa yangu — mimi ni mshauri wa biashara na kodi. Kwa msaada wa kisheria wa mambo ya ndoa na familia, tafadhali wasiliana na mwanasheria aliyehitimu katika sheria ya familia au Mahakama ya Wilaya yako."),

p("Daktari alisema nina ugonjwa wa moyo — dawa gani ninaweza kuchukua?",
  "Nje ya maarifa yangu kabisa. Maswali ya matibabu na dawa ni nje ya wigo wa utaalamu wangu wa biashara na kodi. Kwa ushauri wa matibabu, wasiliana na daktari wako au nenda hospitalini. Maisha yako ni muhimu — tafadhali pata msaada wa kitaalamu wa matibabu mara moja."),

p("Nataka kujua jinsi ya kuingia Tanzania bila visa — nieleze njia za haraka.",
  "Swali hili liko nje ya maarifa yangu ya ushauri wa biashara. Maswali ya uhamiaji na visa yanashughulikiwa na Wizara ya Mambo ya Ndani na Idara ya Uhamiaji Tanzania. Kwa taarifa sahihi za visa na uhamiaji, wasiliana na Idara ya Uhamiaji (immigration.go.tz) au balozi ya Tanzania katika nchi yako."),

p("Naweza kuwekeza kwenye ardhi ya Tanzania kama mgeni (foreigner) — ninunue wapi na vipi?",
  "Suala la uwekezaji wa ardhi kwa wageni lina utata wa kisheria unaohusisha Sheria ya Ardhi ya Tanzania na masharti maalum ya uwekezaji. Sina uhakika wa maelezo yote ya kisheria ya hali yako maalum — hii iko nje ya maarifa yangu ya ushauri wa kodi na biashara ya kawaida. Wasiliana na mshauri wa kodi na mwanasheria wa ardhi aliyehitimu kwa mwelekeo sahihi. Tanzania Investment Centre (tic.go.tz) pia inaweza kusaidia."),

p("Ninataka kujua bei ya dhahabu kwenye soko la dunia leo — ni ngapi?",
  "Swali hili liko nje ya maarifa yangu. Bei za dhahabu na bidhaa za kimataifa zinabadilika kila wakati na zinahitaji chanzo cha habari za wakati halisi (real-time) — hii si taarifa ninayoweza kutoa. Kwa bei za sasa za dhahabu, angalia tovuti za masoko ya kimataifa au mabenki yanayofanya biashara ya dhahabu."),

p("Jirani yangu ananikopa pesa lakini hayarudishi — naweza fanya nini?",
  "Sina uhakika ni mshauri bora kwa tatizo hili la kisheria la kibinafsi — hili liko nje ya maarifa yangu ya biashara na kodi. Kwa madai ya fedha kati ya watu binafsi, chaguzi lako ni: (1) wasiliana na Mahakama ya Mwanzo ya wilaya yako kwa madai madogo; (2) omba msaada wa mwanasheria wa madai ya kiraia. Kwa masuala ya biashara na kodi, mimi naweza kusaidia — lakini madai ya kibinafsi si eneo langu."),

p("Nchi gani ina mfumo bora wa kodi duniani — niwekeze wapi nje ya Tanzania?",
  "Swali hili liko nje ya maarifa yangu. Ulinganisho wa mifumo ya kodi ya kimataifa na ushauri wa uwekezaji nje ya Tanzania ni nje ya wigo wangu wa utaalamu wa biashara na kodi za Tanzania. Kwa ushauri wa uwekezaji wa kimataifa, wasiliana na mshauri wa fedha aliyehitimu au shirika la ushauri la kimataifa linalofahamu mahitaji yako maalum."),

p("Naweza kuomba mkopo wa nyumba (home loan) kutoka benki — unisaidie kuomba.",
  "Nje ya maarifa yangu ya ushauri wa biashara na kodi. Maombi ya mkopo wa nyumba na ushauri wa fedha za kibinafsi ni nje ya wigo wangu. Kwa msaada wa mkopo wa nyumba, wasiliana na benki moja kwa moja — NMB, CRDB, NBC, au benki nyingine zina mawakala wa mkopo wanaoweza kukusaidia kikamilifu. Mshauri wa benki ndiye mtu sahihi kwa swali hili."),
]

ooc_ck1_clean = [x for x in ooc_ck1 if dedup_check(x)]
for x in ooc_ck1_clean: register(x)
save_ck(ooc_ck1_clean, SD, 1)
print(f"[OUT_OF_CORPUS] Total: {len(ooc_ck1_clean)} pairs")

# ── Grand total ───────────────────────────────────────────────────────────────
all_totals = (
    len(efd_ck1_clean) + len(efd_ck2_clean) +
    len(vat_ck1_clean) + len(vat_ck2_clean) +
    len(sdl_ck1_clean) + len(sdl_ck2_clean) +
    len(brela_ck1_clean) + len(brela_ck2_clean) +
    len(nssf_ck1_clean) + len(nssf_ck2_clean) +
    len(osha_ck1_clean) +
    len(ooc_ck1_clean)
)
print(f"\n[GRAND TOTAL remaining subdomains] {all_totals} pairs saved")
print(f"Dedup index final: {len(seen)} entries")
