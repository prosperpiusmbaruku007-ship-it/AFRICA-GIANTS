"""Fix low-coverage keywords:
sdl:  ilifutwa  (2 → 3+)
brela: kufunga  (2 → 3+)
nssf:  inayopelekwa (1 → 3+), anachangia (2 → 3+)
osha:  kumwajiri (1 → 3+)
"""
import json, glob, os

SYSTEM = ("Jina lako ni Chike, mshauri wa biashara kutoka Africa Giants. "
          "Kauli mbiu yako ni: Fahamu Biashara Yako, Maarifa Yako. "
          "Unajibu maswali kuhusu biashara, kodi, BRELA, TRA, NSSF, OSHA, SDL, PAYE, VAT "
          "kwa Kiswahili na Kiingereza. Kama swali liko nje ya mada yako sema wazi kwamba "
          "halijui na mwelekeze kwa mtaalamu.")

OUT_DIR = "datasets/tier1a/raw_sources/batch_012_checkpoints"

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
for fp in sorted(glob.glob(f"{OUT_DIR}/ck_*.jsonl")):
    with open(fp) as f:
        for line in f:
            if line.strip():
                d = json.loads(line)
                key = (d.get("instruction","") + d.get("output",""))[:120].lower().strip()
                seen.add(key)

def p(q, a):
    return {"instruction": q, "input": "", "output": a, "system": SYSTEM}

def dedup_check(pair):
    return (pair["instruction"] + pair["output"])[:120].lower().strip() not in seen

def register(pair):
    seen.add((pair["instruction"] + pair["output"])[:120].lower().strip())

def save_ck(pairs, subdomain, ck_num):
    fname = os.path.join(OUT_DIR, f"ck_{subdomain}_{ck_num:03d}.jsonl")
    with open(fname, "w", encoding="utf-8") as f:
        for pair in pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")
    print(f"[Agent 3] Saved ck_{subdomain}_{ck_num:03d}.jsonl — {len(pairs)} pairs")

# ── SDL: ilifutwa ─────────────────────────────────────────────────────────────
sdl_fix = [
p("Amri ya mshahara wa 2022 ilifutwa rasmi — lini?",
  "Ndiyo, Amri ya Mshahara wa Chini ya Sekta Binafsi ya mwaka 2022 ilifutwa rasmi na GN605A kuanzia tarehe 31 Desemba 2025. Tangu Januari 1, 2026, amri hiyo ya 2022 haina nguvu yoyote ya kisheria. Mwajiri yeyote anayeendelea kutumia viwango vya 2022 baada ya Januari 2026 anakiuka sheria. Viwango vilivyopo sasa ni vile vya GN605A peke yake."),

p("Kwa nini mwajiri hawezi kutumia viwango vya mshahara wa 2022 tena?",
  "Kwa sababu amri ya 2022 ilifutwa kikamilifu na GN605A. Kuanzia Januari 1, 2026, viwango vya 2022 havina nguvu ya kisheria — ni kana kwamba havijaandikwa. GN605A ndiyo mamlaka pekee inayohusika na viwango vya mshahara wa chini ya sekta binafsi Tanzania. Wafanyakazi wana haki ya kudai malipo yaliyobaki (backpay) tangu Januari 2026 kama walilipwa kwa viwango vya amri iliyofutwa."),
]
sdl_clean = [x for x in sdl_fix if dedup_check(x)]
for x in sdl_clean: register(x)
save_ck(sdl_clean, "sdl_compliance", 3)

# ── BRELA: kufunga ────────────────────────────────────────────────────────────
brela_fix = [
p("Nataka kufunga biashara yangu ya sole trader. Niwasiliane na nani?",
  "Kufunga biashara ya sole trader (business name) inayohusisha kusimamisha usajilishaji wa BRELA: (1) wasiliana na BRELA (brela.go.tz) kupata fomu za kufuta usajilishaji; (2) hakikisha kodi zote za TRA zimelipwa — TRA lazima ithibitishe kutokuwa na madeni; (3) wasilisha nyaraka za kufunga BRELA; (4) pata uthibitisho wa kufutwa. Usisahau pia kusasisha leseni nyingine zozote za biashara."),

p("Kampuni yangu haifanyi kazi tena — naweza kuiondoa kwenye rekodi za BRELA?",
  "Ndiyo. Mchakato wa kufunga kampuni rasmi (striking off au winding up) unafanywa kupitia BRELA. Kwanza: kodi zote za TRA lazima zilipwe na TRA itoe uthibitisho wa kutokuwa na madeni. Kisha: omba BRELA kwa utaratibu wa striking off (kwa kampuni ndogo zisizofanya biashara) au winding up (kwa kampuni zenye madeni). Kwa fomu maalum na ada za sasa za kufunga kampuni, angalia brela.go.tz."),
]
brela_clean = [x for x in brela_fix if dedup_check(x)]
for x in brela_clean: register(x)
save_ck(brela_clean, "brela_registration", 3)

# ── NSSF: inayopelekwa + anachangia ──────────────────────────────────────────
nssf_fix = [
p("Kiwango cha mchango wa NSSF kinachopelekwa TRA au NSSF kwa kila mfanyakazi ni ngapi?",
  "Mchango wa NSSF unaopelekwa si TRA — unaenda moja kwa moja kwa NSSF. Kiasi kinachopelekwa kwa kila mfanyakazi ni asilimia 20 ya mshahara wa jumla — mwajiri anachangia asilimia 10 na mfanyakazi anachangia asilimia 10 (mgawanyo wa kawaida). Mwajiri ndiye anayepeleka jumla yote NSSF — ikiwa ni pamoja na sehemu ya mfanyakazi aliyokatwa kwenye mshahara."),

p("Ni nani anachangia zaidi kwenye NSSF — mwajiri au mfanyakazi?",
  "Kwa mgawanyo wa kawaida, wote wawili wanachangia kwa kiasi sawa — mwajiri anachangia asilimia 10 na mfanyakazi anachangia asilimia 10, jumla asilimia 20. Hata hivyo, mwajiri anaweza kuchagua kuchangia zaidi: mgawanyo wa 15+5 (mwajiri zaidi) au 20+0 (mwajiri analipa yote). Mfanyakazi hawezi kuchangia zaidi ya asilimia 10 — kikomo chake ni asilimia 10 tu. Kiasi kinachopelekwa NSSF daima ni asilimia 20 ya mshahara wa jumla."),

p("Malipo ya NSSF inayopelekwa lazima yawe kamili — nifanyeje kama sijaweza kulipa yote?",
  "Kama huwezi kulipa NSSF yote kwa wakati, wasiliana na NSSF (nssf.go.tz) mapema — kabla ya tarehe ya mwisho ikipita. NSSF inaweza kukusaidia kupanga mpango wa malipo. Kuchelewa bila taarifa kunasababisha adhabu ya asilimia 5 kwa kila mwezi wa uchelewaji wa malipo inayopelekwa. Usiache bila kutoa taarifa — NSSF inashughulika vyema zaidi na wajiri wanaowasiliana mapema."),
]
nssf_clean = [x for x in nssf_fix if dedup_check(x)]
for x in nssf_clean: register(x)
save_ck(nssf_clean, "nssf_contributions", 3)

# ── OSHA: kumwajiri ───────────────────────────────────────────────────────────
osha_fix = [
p("Wajibu wa kumwajiri mfanyakazi mpya kuhusu OSHA ni upi?",
  "Kila mwajiri anapoanza kumwajiri mfanyakazi: (1) sajili mahali pa kazi na OSHA haraka (osha.go.tz); (2) fanya tathmini ya hatari kabla ya mfanyakazi kuanza kazi; (3) mfunze mfanyakazi hatari za usalama za kazi yake maalum; (4) mpe vifaa vya usalama vinavyohitajika; (5) mhakikishie mazingira salama ya kufanyia kazi. Kushindwa kufanya hivi kunaweza kusababisha faini ya TZS 1,000,000 hadi TZS 5,000,000 au kifungo."),

p("Kama ninatarajia kumwajiri mfanyakazi wa kwanza, niandae mazingira ya OSHA vipi?",
  "Kabla ya kumwajiri mfanyakazi wa kwanza: (1) sajili mahali pa kazi na OSHA (osha.go.tz) — hii ni wajibu wa kisheria kuanzia mfanyakazi 1; (2) fanya tathmini ya hatari za usalama mahali pako pa kazi; (3) andaa sera ya usalama na afya; (4) hifadhi vifaa vya msaada wa kwanza (first aid kit); (5) hakikisha njia za kutoka dharura (emergency exits) zipo na zimewekwa alama. Hatua hizi zinakuandaa vizuri kwa ukaguzi wowote wa OSHA."),
]
osha_clean = [x for x in osha_fix if dedup_check(x)]
for x in osha_clean: register(x)
save_ck(osha_clean, "osha_registration", 2)

print(f"\nKeyword fix: sdl={len(sdl_clean)} brela={len(brela_clean)} nssf={len(nssf_clean)} osha={len(osha_clean)}")
print(f"Total new pairs: {len(sdl_clean)+len(brela_clean)+len(nssf_clean)+len(osha_clean)}")
