"""Generate VAT_WITHHOLDING pairs for batch_012 — 30 pairs across 3 checkpoints."""
import json, glob, os

SYSTEM = ("Jina lako ni Chike, mshauri wa biashara kutoka Africa Giants. "
          "Kauli mbiu yako ni: Fahamu Biashara Yako, Maarifa Yako. "
          "Unajibu maswali kuhusu biashara, kodi, BRELA, TRA, NSSF, OSHA, SDL, PAYE, VAT "
          "kwa Kiswahili na Kiingereza. Kama swali liko nje ya mada yako sema wazi kwamba "
          "halijui na mwelekeze kwa mtaalamu.")

OUT_DIR = "datasets/tier1a/raw_sources/batch_012_checkpoints"

# Build dedup index from all existing cleaned_pairs
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

def p(q, a):
    return {"instruction": q, "input": "", "output": a, "system": SYSTEM}

def dedup_check(pair):
    key = (pair["instruction"] + pair["output"])[:120].lower().strip()
    return key not in seen

def save_ck(pairs, subdomain, ck_num):
    fname = os.path.join(OUT_DIR, f"ck_{subdomain}_{ck_num:03d}.jsonl")
    with open(fname, "w", encoding="utf-8") as f:
        for pair in pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")
    print(f"[Agent 3] Saved ck_{subdomain}_{ck_num:03d}.jsonl — {len(pairs)} pairs")

SD = "vat_withholding"

# ── checkpoint 001 ────────────────────────────────────────────────────────────
ck1 = [
p("VAT withholding agent ni nani hasa? Biashara yangu inaandaa kupeleka zabuni serikalini.",
  "Mnunuzi anayehitimu (qualifying withholding agent) ni mtu au taasisi iliyoteuliwa na TRA kukata sehemu ya VAT ya msambazaji wakati wa malipo. Wanunuzi wanaohitimu mara nyingi ni wizara za serikali, taasisi za umma, benki, na makampuni ya simu yaliyoteuliwa rasmi. Ili kujua kama biashara yako inaweza kuwa withholding agent, wasiliana na TRA moja kwa moja (tra.go.tz)."),

p("Wizara ya Fedha ikiwa inanipa malipo kama msambazaji wa vifaa, itakata nini?",
  "Wizara ya Fedha ni mfano wa withholding agent anayehitimu. Anakata sehemu ya VAT iliyoko kwenye invoice yako kabla ya kukupa malipo kamili. Bidhaa na huduma vina viwango tofauti vya withholding. Kwa hesabu sahihi ya kiasi kinachokatwa, thibitisha na TRA kwa hesabu halisi (tra.go.tz). Serikali itakupa certificate ya withholding inayoonyesha kiasi kilichokatwa."),

p("Je, wizara ya serikali lazima isajiliwe TRA kama withholding agent?",
  "Ndiyo. Wizara na taasisi za serikali zinazofanya manunuzi kutoka wasambazaji waliosailiwa VAT lazima ziwe na hadhi ya withholding agent iliyothibitishwa na TRA. Bila usajilishaji huo, hana ruhusa ya kisheria ya kukata VAT ya msambazaji. Thibitisha na TRA (tra.go.tz) kwa utaratibu sahihi."),

p("Tarehe ya mwisho ya kupeleka VAT iliyokatwa TRA ni lini?",
  "Withholding agent lazima apeleke VAT iliyokatwa TRA ifikapo tarehe 20 ya mwezi unaofuata mwezi wa manunuzi. Kwa mfano, ikiwa ulinunua mwezi Januari, malipo ya withheld VAT yanatakiwa ifikapo tarehe 20 Februari. Tarehe 20 pia ni tarehe ya kuwasilisha VAT return — wajibu hizi mbili zinafanana kwa tarehe."),

p("Certificate ya VAT withholding ni nini na kwa nini inahitajika?",
  "Cheti cha VAT withholding ni hati rasmi inayotolewa na mnunuzi anayehitimu kwa msambazaji, inayothibitisha kiasi cha VAT kilichokatwa. Msambazaji anahitaji certificate hii kama ushahidi wa pembejeo ya VAT (input VAT credit) ambayo anaweza kudai kwenye VAT return yake. Bila certificate, msambazaji hawezi kuthibitisha VAT iliyokatwa kwake."),

p("Ni taarifa gani lazima ionekane kwenye certificate ya VAT withholding?",
  "Certificate ya VAT withholding lazima iwe na: TIN ya mnunuzi anayehitimu, TIN ya msambazaji, nambari ya usajili wa VAT wa msambazaji, maelezo ya bidhaa au huduma iliyonunuliwa, thamani ya bidhaa kabla ya VAT, kiwango cha withholding kilichotumika, na kiasi halisi cha VAT kilichokatwa. Hati hii lazima iandaliwe kwa mfumo ulioidhinishwa na TRA."),

p("Kampuni ya simu iliyoteuliwa na TRA inatoa certificate vipi kwa msambazaji?",
  "Kampuni ya simu kama withholding agent inafanya hivi: inapokea invoice kutoka msambazaji aliyesajiliwa VAT, anakata sehemu ya VAT hiyo kulingana na kiwango kilichowekwa, analipia msambazaji kiasi kilichobakia, kisha anatoa certificate inayoonyesha kiasi alichokata. Certificate lazima itolewe siku ile ile VAT inakuwa payable — si tarehe 20. Tarehe 20 ni kwa ajili ya kupeleka withholding TRA."),

p("Nimepokea malipo kutoka serikalini lakini hawakutoa certificate ya withholding. Nifanye nini?",
  "Omba withholding agent (serikali) akupe certificate haraka. Kisheria, withholding agent lazima atoe certificate si baadaye ya tarehe VAT inakuwa payable. Bila certificate hii, huwezi kudai pembejeo ya VAT kwenye VAT return yako. Kama hawatatoa baada ya kuomba, wasiliana na TRA (tra.go.tz) kutoa malalamiko rasmi."),

p("Je, bidhaa na huduma vina kiwango sawa cha VAT withholding?",
  "Hapana. Bidhaa na huduma vina viwango tofauti vya VAT withholding — kiwango cha bidhaa ni tofauti na kile cha huduma. Kwa hesabu sahihi ya kiasi kinachokatwa kwenye invoice yako, thibitisha na TRA (tra.go.tz) au mshauri wa kodi aliyehitimu. Usitegemee bidhaa na huduma kuwa sawa."),

p("Kama withholding agent, siotoi certificate kwa msambazaji — kuna adhabu?",
  "Ndiyo. Kutotoa certificate ya withholding ni ukiukwaji wa sheria ya VAT. TRA inaweza kuamrisha ulipe faini na riba. Msambazaji pia anaweza kudai fidia kwa sababu hana ushahidi wa pembejeo ya VAT. Lazima utoe certificate si baadaye ya tarehe VAT inakuwa payable. Thibitisha wajibu huu na TRA (tra.go.tz)."),
]

ck1_clean = [pair for pair in ck1 if dedup_check(pair)]
for pair in ck1_clean:
    key = (pair["instruction"] + pair["output"])[:120].lower().strip()
    seen.add(key)
save_ck(ck1_clean, SD, 1)

# ── checkpoint 002 ────────────────────────────────────────────────────────────
ck2 = [
p("Kama msambazaji niliyesajiliwa VAT, naweza kudai pembejeo ya VAT (input VAT) baada ya withholding?",
  "Ndiyo. VAT iliyokatwa na mnunuzi anayehitimu inaweza kudaiwa kama pembejeo (input VAT credit) kwenye VAT return yako kwa kutumia certificate ya withholding. Serikali kama mbia wako itakupa certificate inayothibitisha kiasi kilichokatwa. Hati hii ni ushahidi wako rasmi wa pembejeo ya VAT."),

p("Wanaohitimu kama VAT withholding agents Tanzania ni akina nani hasa?",
  "Wanaohitimu kama VAT withholding agents ni pamoja na: wizara za serikali na taasisi za umma, kampuni za bima zilizoteuliwa, benki na taasisi za fedha, makampuni ya simu yaliyoteuliwa, na biashara nyingine zilizopewa hadhi rasmi na TRA. Orodha kamili inapatikana kwenye TRA. Uliza TRA kama una shaka kuhusu mbia wako."),

p("Mbia wangu wa serikali anasema kiwango cha withholding ya huduma ni tofauti na kwa bidhaa — hii ni kweli?",
  "Ndiyo, hii ni kweli. Kiwango cha withholding kwa huduma ni tofauti na kile cha bidhaa. Kwa hesabu sahihi ya kiasi kinachokatwa kwenye invoice yako ya huduma maalum, thibitisha na TRA (tra.go.tz) au wasiliana na mshauri wa kodi aliyehitimu."),

p("Mbia wa serikali anakata VAT yangu. Niandikaje kwenye VAT return yangu?",
  "Kwenye VAT return yako, ripoti VAT iliyokatwa kama pembejeo (input VAT credit). Tumia certificate ya withholding iliyotolewa na serikali (mnunuzi anayehitimu) kama ushahidi. Hakikisha certificate ina TIN yako, maelezo ya bidhaa, kiwango kilichotumika, na kiasi kilichokatwa. Ikiwa certificate haipo, omba kabla ya kuwasilisha return ifikapo tarehe 20."),

p("Biashara yangu ya ujenzi — serikali ni mbia mkubwa wangu. Nieleze mchakato wa VAT withholding.",
  "Mchakato kwa mbia wa serikali katika ujenzi: (1) toa invoice yako ikijumuisha VAT ya 18%; (2) serikali (mnunuzi anayehitimu) itakata sehemu ya VAT; (3) serikali italipa kiasi kilichobakia; (4) serikali itatoa certificate ya withholding inayoonyesha details kamili; (5) tumia certificate kudai pembejeo ya VAT kwenye return yako ifikapo tarehe 20. Kwa hesabu ya kiasi kinachokatwa, thibitisha na TRA (tra.go.tz)."),

p("Kama mnunuzi anayehitimu, nikose kukata VAT — ninakabiliwa na nini?",
  "Kushindwa kukata VAT kama withholding agent ni ukiukwaji wa sheria ya VAT Act. TRA inaweza kukuamrisha kulipa kiasi kilichokosekana pamoja na riba na faini. Lazima uhakikishe mfumo wako wa malipo una withholding procedure sahihi. Wasiliana na TRA (tra.go.tz) au mshauri wa kodi ili ujue wajibu wako kamili."),

p("Msambazaji wangu anasema si lazima nitoe certificate kwa sababu tutawasiliana na TRA moja kwa moja. Ni kweli?",
  "Hapana, hii si kweli. Kisheria, mnunuzi anayehitimu LAZIMA atoe certificate ya withholding kwa msambazaji. Hii si chaguo — ni wajibu wa kisheria wa VAT Act. Msambazaji anahitaji certificate kudai pembejeo ya VAT yake. Kama utatoa hoja hii, utakabiliwa na adhabu. Toa certificate kwa wakati sahihi."),

p("Certificate ya VAT withholding inatakiwa itolewe tarehe gani hasa?",
  "Certificate ya VAT withholding lazima itolewe si baadaye ya tarehe VAT inakuwa payable — kawaida tarehe ya kukamilika kwa muamala (supply date). Hii si tarehe 20 ya mwezi unaofuata. Tarehe 20 ni deadline ya kuwasilisha VAT return na kupeleka VAT iliyokatwa TRA. Hizi ni wajibu mbili tofauti zenye tarehe tofauti."),

p("Wizara inanipa malipo tarehe 15 Januari. VAT iliyokatwa inapelekwa TRA tarehe ngapi?",
  "VAT iliyokatwa na wizara (withholding agent) lazima ipelekezwe TRA ifikapo tarehe 20 Februari — yaani mwezi unaofuata wa manunuzi ya Januari. Hii ni tarehe ya kawaida ya remittance kwa withholding agents wote. Certificate ya withholding lazima ilikuwa imetolewa mapema — si baadaye ya tarehe VAT ilipokuwa payable."),

p("Wanunuzi wanaohitimu wangu hawajui wana jukumu la withholding. Niwasaiduje?",
  "Waambie: wanunuzi wanaohitimu (qualifying buyers) wana wajibu wa kisheria wa kukata VAT. Wizara, benki, na makampuni ya simu yaliyoteuliwa ni mifano. Wajibu wao: (1) kutoa certificate ya withholding kwa kila msambazaji; (2) kupeleka VAT iliyokatwa TRA ifikapo tarehe 20; (3) kuwasilisha VAT return yao wenyewe. Kama hawajui, waelekeze TRA (tra.go.tz) au mshauri wa kodi aliyehitimu."),
]

ck2_clean = [pair for pair in ck2 if dedup_check(pair)]
for pair in ck2_clean:
    key = (pair["instruction"] + pair["output"])[:120].lower().strip()
    seen.add(key)
save_ck(ck2_clean, SD, 2)

# ── checkpoint 003 ────────────────────────────────────────────────────────────
ck3 = [
p("Sijui kama mbia wangu ni withholding agent. Nifanye nini?",
  "Angalia: je, mbia wako ni wizara ya serikali, benki, kampuni ya simu, au taasisi ya umma? Hawa mara nyingi ni wanunuzi wanaohitimu kama withholding agents. Kama huna uhakika, uliza TRA moja kwa moja au angalia tra.go.tz. Kujua hili ni muhimu kwa sababu itaathiri jinsi unavyoandaa VAT return yako."),

p("Nimelipa VAT yangu yote TRA lakini serikali pia ilikata. Je, nitalipa mara mbili?",
  "Hapana, hili si tatizo ikiwa umefuata utaratibu. Serikali ilikata VAT kwa niaba yako (withholding). Kiasi hicho hakihitajiki kulipwa tena nawe. Kwenye VAT return yako, ripoti kiasi kilichokatwa kama pembejeo (input VAT) na tumia certificate ya withholding kama ushahidi. TRA itarekebisha hesabu yako. Kama una mashaka, wasiliana na mshauri wa kodi."),

p("Ninasambazo pembejeo za malighafi kwa viwanda. Je, viwanda vikubwa vinaweza kunikata VAT?",
  "Ndiyo, kama viwanda hivyo vimeteuliwa na TRA kama withholding agents, vinaweza kukata VAT yako. Hii inakuathiri kwa cash flow — utalipwa kidogo kuliko invoice yako — lakini certificate ya withholding inakupa haki ya kudai pembejeo ya VAT kwenye return yako. Thibitisha kwa mbia wako mkubwa kama ana hadhi ya withholding agent."),

p("Serikali inaniambia nitoe invoice bila VAT ili kuepuka withholding — hii ni halali?",
  "Hapana, hii si halali kama umesajiliwa VAT. Kama biashara yako imesajiliwa VAT, lazima utoe invoice yenye VAT ya 18%. Serikali kama mbia wako lazima ikata sehemu ya VAT hiyo na kukupa certificate. Kuomba invoice bila VAT ili kuepuka withholding ni ukiukwaji wa sheria ya VAT. Thibitisha na TRA utaratibu sahihi."),

p("Mbia wangu wa serikali anachelewesha kutoa certificate ya withholding — hii inaniathirije?",
  "Delay ya certificate ni tatizo kubwa — huwezi kudai pembejeo ya VAT yako bila certificate. Kisheria, certificate lazima itolewe si baadaye ya tarehe VAT ilipokuwa payable — delay ni ukiukwaji. Omba certificate rasmi kwa maandishi. Kama hawatoi, fika TRA (tra.go.tz) kutoa malalamiko. Huwezi kuwasilisha VAT return kamili bila certificate hii."),

p("Kwa invoice ya TZS 1,000,000 ya bidhaa, serikali itakata kiasi gani cha VAT withholding?",
  "Kiasi kinachofaa kukatwa kinategemea kiwango cha withholding kilichowekwa na TRA kwa bidhaa. Kwa hesabu sahihi, thibitisha na TRA (tra.go.tz) au mshauri wa kodi aliyehitimu. Kumbuka: VAT ya invoice ya TZS 1,000,000 kwa kiwango cha kawaida cha 18% ni TZS 180,000 — sehemu ya hiyo ndiyo inayokatwa kulingana na kiwango cha withholding. Kwa hesabu halisi, thibitisha na TRA kwa hesabu sahihi."),

p("Kama msambazaji mdogo, withholding inanidhuru kiuchumi vipi?",
  "Withholding inaweza kuathiri mtiririko wa fedha (cash flow) kwa sababu unapokea malipo kidogo kuliko invoice yako yote. Hata hivyo, VAT iliyokatwa si hasara — inaweza kudaiwa kama pembejeo kwenye VAT return yako kupitia certificate ya withholding. Tatizo la kweli ni delay ya pesa. Pangilia fedha zako kwa kuzingatia withholding."),

p("Tofauti kati ya VAT withholding na output VAT ya kawaida ni nini?",
  "VAT ya kawaida (output VAT) unalipa mwenyewe TRA baada ya kukusanya kutoka kwa wateja wako. VAT withholding ni ambapo mnunuzi anayehitimu (kama serikali) anakata VAT moja kwa moja kutoka malipo yako kabla ya kukupa pesa na anapeleka TRA kwa niaba yako. Tofauti kuu: withholding inapunguza kiasi unachopokea, lakini certificate inakupa haki ya kudai pembejeo ya VAT hiyo."),

p("Withholding agents wote wanakata kiwango sawa, au kila mmoja ana kiwango chake?",
  "Kiwango cha withholding ni kimoja kwa aina moja ya muamala — bidhaa vina kiwango kimoja na huduma vina kiwango kingine. Withholding agents wote wanaoteuliwa na TRA wanatakiwa kutumia viwango vilivyowekwa — hawana uhuru wa kuweka kiwango chao wenyewe. Kwa hesabu halisi ya kiwango kinachotumika kwenye biashara yako, thibitisha na TRA (tra.go.tz)."),

p("Ninaanzisha biashara ya kusambaza vifaa vya ujenzi na serikali ni mbia wangu mkuu. Niandae vipi?",
  "Jiandae hivi: (1) Sajili VAT kama mauzo yako yanafika kizingiti (TZS 200M/mwaka au TZS 100M/miezi 6); (2) Andaa mfumo wa kuhifadhi certificates za withholding utakazozipata kutoka withholding agents; (3) Panga cash flow yako kwa kuzingatia utalipwa kidogo kuliko invoice; (4) Tumia certificates kudai pembejeo ya VAT kwenye return yako ifikapo tarehe 20; (5) Thibitisha kiwango cha withholding na TRA (tra.go.tz) au mshauri wa kodi aliyehitimu."),
]

ck3_clean = [pair for pair in ck3 if dedup_check(pair)]
for pair in ck3_clean:
    key = (pair["instruction"] + pair["output"])[:120].lower().strip()
    seen.add(key)
save_ck(ck3_clean, SD, 3)

total = len(ck1_clean) + len(ck2_clean) + len(ck3_clean)
print(f"\n[VAT_WITHHOLDING] Total saved: {total} pairs across 3 checkpoints")
print(f"Dedup index now: {len(seen)} entries")
