#!/usr/bin/env python3
"""Generate batch_011 Sections 4-6 — VAT5%(20) + SDL(20) + VAT_REG(20) = 60 pairs."""
import json, os

OUTPUT_FILE = "datasets/tier1a/raw_sources/raw_pairs_batch_011.jsonl"
CHECKPOINT_DIR = "datasets/tier1a/raw_sources/batch_011_checkpoints"

VAT_THREE = (
    "Tanzania ina viwango VITATU vya VAT peke yake: "
    "(1) Asilimia 18 — kiwango cha kawaida "
    "(2) Asilimia 16 — B2C malipo ya kidijitali (kuanzia 1 Septemba 2025) "
    "(3) Asilimia 0 — mauzo ya nje (zero-rated) "
    "HAKUNA kiwango cha asilimia 5 Tanzania."
)
SDL_FACTS = (
    "SDL (Skills Development Levy) inafanya kazi hivi: "
    "Kiwango: asilimia 3.5 ya mshahara wa jumla wa wafanyakazi wote. "
    "Mlipaji: mwajiri peke yake (si mfanyakazi). "
    "Kizingiti: waajiri wenye wafanyakazi 10 au zaidi tu. "
    "Tarehe ya kulipa: tarehe 7 ya mwezi unaofuata."
)
SDL_VS_WCF = (
    "SDL = asilimia 3.5 → TRA → waajiri wenye wafanyakazi 10 au zaidi. "
    "WCF = asilimia 0.5 → Mamlaka ya WCF → WAAJIRI WOTE (hata mwajiri mwenye mfanyakazi 1). "
    "Tofauti kubwa: WCF haina kizingiti cha idadi ya wafanyakazi — mwajiri yeyote analipa."
)

pairs = []

# ── SECTION 4: VAT 5% fix (20 pairs) ─────────────────────────────────────
pairs.append({
    "instruction": "VAT Tanzania ni asilimia ngapi?",
    "output": (
        f"{VAT_THREE} "
        "Kiwango kinachotumika zaidi ni 18% (standard rate). "
        "Kwa bidhaa na huduma zinazouzwa nje ya Tanzania: 0% (zero-rated, unastahili rejareja ya VAT). "
        "Chanzo: TRA (tra.go.tz) na Finance Act 2025."
    )
})
pairs.append({
    "instruction": "VAT ya Tanzania ni 18% au kuna viwango vingine?",
    "output": (
        f"{VAT_THREE} "
        "Kwa manunuzi ya kawaida ya biashara yako: 18%. "
        "Kwa mauzo yako ya nje (exports): 0% — unaweza kudai rejareja ya VAT uliyo nayo. "
        "Kwa malipo ya kidijitali ya B2C kuanzia Sep 2025: 16% — kanuni za utekelezaji zinasubiriwa."
    )
})
pairs.append({
    "instruction": "Chakula cha msingi kina VAT ya asilimia 5 Tanzania?",
    "output": (
        f"Hapana. {VAT_THREE} "
        "Chakula cha msingi (kama nafaka, unga, sukari) kawaida ni exempt (imesamehewa VAT kabisa) "
        "au zero-rated — si 5%. "
        "Thibitisha orodha sahihi ya bidhaa zilizosamehewa VAT na TRA (tra.go.tz)."
    )
})
pairs.append({
    "instruction": "Nimeona bei ya bidhaa ikiwa VAT 5% — je Tanzania ina hii?",
    "output": (
        f"Hapana — Tanzania haina kiwango cha VAT cha asilimia 5. {VAT_THREE} "
        "Kama umeona 5% kwenye risiti au invoice, inaweza kuwa kosa la mfanyabiashara "
        "au bidhaa kutoka nchi nyingine (kama Kenya ina VAT 16% na Uingereza 20%). "
        "Tanzania: 18%, 16% (B2C digital), au 0% (exports/exempt) peke yake."
    )
})
pairs.append({
    "instruction": "Madawa ya hospitali yana VAT ya asilimia 5 au asilimia 0?",
    "output": (
        f"{VAT_THREE} "
        "Madawa mengi ya hospitali (dawa muhimu) yana VAT 0% (zero-rated) au exempted kabisa — "
        "si 5%. Tanzania haina kiwango cha 5% kabisa. "
        "Thibitisha hali ya dawa maalum na orodha ya TRA."
    )
})
pairs.append({
    "instruction": "Bidhaa za kilimo zina VAT ngapi Tanzania — 5%?",
    "output": (
        f"Tanzania haina VAT ya 5%. {VAT_THREE} "
        "Bidhaa nyingi za kilimo (mbolea, mbegu, zana za kilimo) zina VAT 0% (zero-rated) "
        "au zimesamehewa (exempt) — si 5%. "
        "Orodha kamili iko kwenye VAT Act na TRA."
    )
})
pairs.append({
    "instruction": "Tanzania ina VAT ya kawaida na VAT ndogo (reduced rate) kama nchi nyingine?",
    "output": (
        f"Hapana — Tanzania haina 'reduced rate' ya VAT. {VAT_THREE} "
        "Tofauti na nchi kama Kenya (0%, 8%, 16%) au Uingereza (0%, 5%, 20%), "
        "Tanzania ina 18% (standard), 16% (B2C digital tu, Sep 2025), na 0% (exports/exempt). "
        "Hakuna reduced rate ya kati (kama 5% au 8%)."
    )
})
pairs.append({
    "instruction": "Huduma za utalii Tanzania zina VAT ya 5% au ya kawaida?",
    "output": (
        f"{VAT_THREE} "
        "Huduma za utalii zinazotolewa kwa wageni wa nje (foreign tourists) kawaida zinaweza "
        "kustahili zero-rating (0%) kwa mazingira fulani — si 5%. "
        "Thibitisha hali yako maalum ya utalii na TRA (tra.go.tz)."
    )
})
pairs.append({
    "instruction": "Kampuni yangu inauza bidhaa za maziwa — VAT ni 5%?",
    "output": (
        f"Tanzania haina VAT ya 5%. {VAT_THREE} "
        "Bidhaa za maziwa (maziwa ya kawaida, jibini) mara nyingi zimesamehewa VAT (exempt) au zero-rated. "
        "Thibitisha hali ya bidhaa zako maalum na mwanasheria wa kodi au TRA."
    )
})
pairs.append({
    "instruction": "Nimekuwa nikalipa VAT ya asilimia 5 kwa miaka miwili — hii ni sahihi?",
    "output": (
        f"Hapana — {VAT_THREE} "
        "Kama umelipa 5% kwa VAT, inawezekana kumekuwa na kosa katika mfumo wako wa akaunti. "
        "Hatua: (1) Angalia invoices zako na mwongozo wa TRA. "
        "(2) Wasiliana na TRA kujua kama unapaswa kurekebisha malipo ya zamani. "
        "(3) Sahihisha mfumo wako wa akaunti mara moja."
    )
})
pairs.append({
    "instruction": "Ninaulizwa na mteja ninalipe VAT 5% kwake kwa huduma zangu — nifanye nini?",
    "output": (
        f"Mteja huyo ana makosa. {VAT_THREE} "
        "Huduma za kawaida za biashara Tanzania zinastahili VAT ya 18% (standard rate). "
        "Eleza kwa mteja wako kwamba Tanzania haina kiwango cha 5% — "
        "kiwango sahihi ni 18% au 0% (iwapo huduma yako inastahili zero-rating)."
    )
})
pairs.append({
    "instruction": "Nikilinganisha viwango vya VAT Kenya na Tanzania — Tanzania ina viwango vingapi?",
    "output": (
        f"Tanzania: viwango VITATU. {VAT_THREE} "
        "Kenya (kwa ulinganisho): 0%, 8% (bidhaa chache kama petroli), 16% (standard). "
        "Tofauti muhimu: Tanzania HAINA 8% wala 5% — viwango vya Kenya havitumiki Tanzania. "
        "Usijaribu kutumia viwango vya Kenya kwa biashara yako Tanzania."
    )
})
pairs.append({
    "instruction": "Vatimbia yangu imeandika VAT 5% kwenye EFD — ninapaswa kubadilisha vipi?",
    "output": (
        f"{VAT_THREE} "
        "EFD yenye kiwango cha 5% imeprogramiwa vibaya. Hatua: "
        "(1) Wasiliana na msambazaji wako wa EFD haraka. "
        "(2) Omba EFD irekebishwe kuonyesha 18% (au 0% kwa bidhaa zilizosamehewa). "
        "(3) EFD lazima iwe na viwango sahihi — risiti zenye 5% zinaweza kuleta matatizo na TRA."
    )
})
pairs.append({
    "instruction": "Bidhaa za ujenzi (cement, nondo) zina VAT ngapi Tanzania?",
    "output": (
        f"{VAT_THREE} "
        "Bidhaa za ujenzi kama saruji (cement) na nondo mara nyingi zina VAT ya 18% (standard rate). "
        "Baadhi ya nyenzo maalum za ujenzi zinaweza kuwa na hali tofauti — thibitisha na TRA."
    )
})
pairs.append({
    "instruction": "Nikiwasilisha VAT return — ninajaza fomu kwa viwango gani?",
    "output": (
        f"{VAT_THREE} "
        "Kwenye VAT return (Fomu ya TRA): "
        "Standard rated sales: 18% "
        "Zero-rated sales (exports na zingine): 0% "
        "B2C digital services (tangu Sep 2025): 16% "
        "Exempt supplies: zinaonyeshwa tofauti bila kodi. "
        "Hakuna nafasi ya 5% kwenye fomu sahihi ya TRA."
    )
})
pairs.append({
    "instruction": "Kwa nini watu wanasema VAT 5% Tanzania — inakuja wapi nambari hii?",
    "output": (
        f"Nambari ya 5% inaweza kutoka: (1) Makosa ya mtandaoni au vyanzo visivyo sahihi. "
        "(2) Mfumo wa kodi wa nchi nyingine (VAT ya Kenya ilikuwa na 8% kwa vitu fulani). "
        "(3) SDL (Skills Development Levy) ya 3.5% inayoweza kuchanganywa na VAT. "
        f"Ukweli: {VAT_THREE}"
    )
})
pairs.append({
    "instruction": "Mzabuni wangu ameandika invoice yenye VAT 5% — nailipe au nikatae?",
    "output": (
        f"{VAT_THREE} "
        "Invoice yenye VAT 5% ina kosa — mzabuni ametumia kiwango kisichopo Tanzania. "
        "Hatua: (1) Arifu mzabuni kwamba Tanzania haina 5% VAT. "
        "(2) Omba invoice mpya yenye 18% (iwapo bidhaa/huduma inastahili VAT standard). "
        "(3) Usidai input VAT ya 5% kwenye return yako — TRA haitaikubali."
    )
})
pairs.append({
    "instruction": "Kama VAT ni 18%, mbona wakati mwingine ninaona 16% kwenye risiti?",
    "output": (
        f"{VAT_THREE} "
        "16% ni kiwango kipya cha B2C malipo ya kidijitali tangu Septemba 2025 — "
        "lakini linatumika kwa huduma maalum za kidijitali zinazolipwa na watumiaji wa kawaida (B2C). "
        "Kwa biashara nyingi za kawaida: 18% bado ndiyo kiwango sahihi. "
        "Ukiona 16% kwenye risiti ya kawaida ya biashara (si digital/mtandaoni), thibitisha na mzabuni."
    )
})
pairs.append({
    "instruction": "Uelewa wangu: VAT Tanzania ni 5% kwa bidhaa za msingi na 18% kwa bidhaa za anasa. Sahihi?",
    "output": (
        f"Hapana — uelewa huo si sahihi. {VAT_THREE} "
        "Tanzania HAINA reduced rate ya 5% hata kwa bidhaa za msingi. "
        "Bidhaa za msingi zinaweza kuwa zero-rated (0%) au exempt (zimesamehewa kabisa) — "
        "si 5%. Tofauti kati ya 0% na exempt ni muhimu kwa madai ya input VAT."
    )
})
pairs.append({
    "instruction": "Ninafanya biashara ya chakula na vinywaji. VAT yangu ni 5%, 18%, au 0%?",
    "output": (
        f"{VAT_THREE} "
        "Hali ya VAT kwa chakula na vinywaji Tanzania inategemea aina: "
        "Chakula cha msingi (nafaka, unga, sukari): kawaida exempt au 0%. "
        "Vinywaji vya anasa (soda, juisi za kisanduku): kawaida 18%. "
        "Chakula cha mkahawa: kawaida 18% kwa huduma ya chakula. "
        "HAKUNA 5% — thibitisha bidhaa zako maalum na TRA."
    )
})

# ── SECTION 5: SDL REINFORCEMENT (20 pairs) ───────────────────────────────
# 5 pairs — SDL 3.5% and employer only
pairs.append({
    "instruction": "SDL inahesabiwaje? Ni mwajiri au mfanyakazi analipa?",
    "output": (
        f"{SDL_FACTS} "
        "Mfanyakazi HALIPIWI SDL kwenye mshahara wake — mwajiri ndiye analipa kwa jina lake mwenyewe. "
        "Mfano: wafanyakazi 10 wenye jumla ya mishahara TZS 3,000,000 → SDL = TZS 105,000."
    )
})
pairs.append({
    "instruction": "SDL rate ni asilimia ngapi Tanzania?",
    "output": (
        f"{SDL_FACTS} "
        "Kiwango cha SDL ni 3.5% ya jumla ya mishahara yote. "
        "Hakuna kiwango kingine — si 5%, si 4%, si 3%. Ni 3.5% peke yake. "
        "Chanzo: Finance Act na kanuni za TRA."
    )
})
pairs.append({
    "instruction": "Nimeambiwa SDL ni 5% — sahihi?",
    "output": (
        "Hapana — SDL si 5%. "
        f"{SDL_FACTS} "
        "Kiwango cha 5% haikuwa sahihi — inaweza kuchanganywa na kiwango kingine kama NSSF (10%+10%). "
        "SDL ni 3.5% peke yake, inalipwa na mwajiri tu."
    )
})
pairs.append({
    "instruction": "SDL inalipwa na mwajiri, mfanyakazi, au wote wawili?",
    "output": (
        f"{SDL_FACTS} "
        "SDL inalipwa na MWAJIRI PEKE YAKE — mfanyakazi halipiwi SDL wowote. "
        "Tofauti na NSSF (mwajiri 10% + mfanyakazi 10%) — SDL ni ya upande mmoja tu. "
        "Mwajiri analipa 3.5% ya jumla ya mishahara ya wafanyakazi wake wote kwenye TRA."
    )
})
pairs.append({
    "instruction": "Ninafanya kazi ya biashara ya uhuru — SDL inanishughulikia?",
    "output": (
        f"{SDL_FACTS} "
        "SDL inashughulikia WAAJIRI (employers) — wale wanaomiliki wafanyakazi. "
        "Ukifanya kazi ya uhuru (self-employed/freelancer) na huna wafanyakazi, "
        "si mwajiri na kwa hivyo SDL haikushughulikia. "
        "Lakini ukiwa na wafanyakazi 10+, basi wewe ni mwajiri na SDL inahitajika."
    )
})

# 5 pairs — SDL threshold exactly 10 employees
pairs.append({
    "instruction": "SDL inaanzia kwa wafanyakazi wangapi?",
    "output": (
        f"{SDL_FACTS} "
        "Kizingiti: wafanyakazi 10 au zaidi kwa wakati mmoja. "
        "Wafanyakazi 9: SDL haihitajiki (bado chini ya kizingiti). "
        "Wafanyakazi 10: SDL inahitajika — anza kulipa mara moja."
    )
})
pairs.append({
    "instruction": "Nina wafanyakazi 8 — SDL inahusika nami?",
    "output": (
        f"{SDL_FACTS} "
        "Kwa wafanyakazi 8, bado uko chini ya kizingiti cha 10 — SDL haihitajiki. "
        "Lakini ukiongeza hadi wafanyakazi 10, SDL inahitajika mara moja kwa mwezi huo. "
        "Fuatilia idadi ya wafanyakazi wako kila wakati."
    )
})
pairs.append({
    "instruction": "Nimeambiwa SDL inaanzia kwa wafanyakazi 5 — sahihi?",
    "output": (
        "Hapana — kizingiti si wafanyakazi 5. "
        f"{SDL_FACTS} "
        "Kizingiti sahihi ni wafanyakazi 10 — si 5, si 15, si 20. "
        "Thibitisha na TRA (tra.go.tz) iwapo una shaka."
    )
})
pairs.append({
    "instruction": "Wafanyakazi wa mkataba wa muda mfupi (casual workers) wanahesabiwaje kwa SDL?",
    "output": (
        f"{SDL_FACTS} "
        "Wafanyakazi wa muda mfupi wanaopewa mishahara: mishahara yao inajumuishwa katika "
        "hesabu ya SDL kama wengine. "
        "Kama wafanyakazi wako wote (wa kudumu + wa muda mfupi) wanafikia 10+, SDL inahitajika. "
        "Thibitisha ufafanuzi wa 'mfanyakazi' na TRA kwa hali yako maalum."
    )
})
pairs.append({
    "instruction": "Kampuni yangu ina wafanyakazi 12 wa Dar es Salaam na 6 wa Mwanza — SDL yangu ni ngapi?",
    "output": (
        f"{SDL_FACTS} "
        "Jumla ya wafanyakazi wote: 18 — umepita kizingiti cha 10. SDL inahitajika. "
        "Hesabu: 3.5% × jumla ya mishahara ya wafanyakazi wote 18. "
        "Wafanyakazi kutoka matawi yote wa kampuni moja wanaohesabiwa pamoja kwa kizingiti na hesabu."
    )
})

# 5 pairs — SDL deadline 7th of following month
pairs.append({
    "instruction": "SDL inalipwa tarehe ngapi?",
    "output": (
        f"{SDL_FACTS} "
        "Tarehe ya kulipa: tarehe 7 ya mwezi unaofuata. "
        "Mfano: SDL ya mwezi Januari inalipwa kabla ya tarehe 7 Februari. "
        "Kuchelewa kulipa SDL kunasababisha faini na riba ya TRA."
    )
})
pairs.append({
    "instruction": "SDL ya mwezi huu — inawasilishwa tarehe 20 au tarehe 7 ya mwezi ujao?",
    "output": (
        f"{SDL_FACTS} "
        "Tarehe sahihi: tarehe 7 ya mwezi unaofuata — si tarehe 20. "
        "Tarehe 20 ni kwa VAT return — usifanye makosa kati ya SDL na VAT deadlines. "
        "SDL: tarehe 7 | VAT return: tarehe 20 | PAYE: tarehe 7."
    )
})
pairs.append({
    "instruction": "Kama tarehe 7 inaangukia Jumapili au likizo — SDL nalipia lini?",
    "output": (
        f"{SDL_FACTS} "
        "Kama tarehe 7 ni siku ya likizo au Jumapili, lipa SDL siku ya kazi inayofuata. "
        "Hata hivyo, usitegemee kanuni hii — lipa mapema ili kuepuka matatizo yoyote. "
        "Mazoea bora: lipa SDL kati ya tarehe 1-5 ya mwezi ili kuwa salama."
    )
})
pairs.append({
    "instruction": "Faini ya kuchelewa SDL ni ngapi?",
    "output": (
        f"{SDL_FACTS} "
        "Faini na riba ya kuchelewa SDL inashughulikiwa na TRA chini ya Tax Administration Act. "
        "TRA inaweza kutoza: faini ya kuchelewa + riba ya kila siku au mwezi wa kuchelewa. "
        "Wasiliana na TRA moja kwa moja kujua kiasi halisi cha faini — "
        "au lipa mapema kuliko kuchelewesha."
    )
})
pairs.append({
    "instruction": "SDL na PAYE — zote zinalipwa tarehe 7?",
    "output": (
        f"{SDL_FACTS} "
        "Ndio — SDL na PAYE zote mbili zinalipwa tarehe 7 ya mwezi unaofuata. "
        "Kumbuka: VAT return ni tarehe 20 (tofauti). "
        "Kalenda ya kodi: tarehe 7 (SDL + PAYE + WCF) | tarehe 20 (VAT return) | "
        "tarehe 9 ya mwezi ujao (NSSF, kwa makampuni fulani — thibitisha na NSSF)."
    )
})

# 5 pairs — SDL vs WCF distinction
pairs.append({
    "instruction": "Tofauti kati ya SDL na WCF ni nini?",
    "output": (
        f"{SDL_VS_WCF} "
        "SDL inakwenda TRA → inatumika kwa mafunzo ya nguvu kazi Tanzania. "
        "WCF inakwenda Mamlaka ya WCF → inatumika kulipa fidia za ajali za kazi."
    )
})
pairs.append({
    "instruction": "Nina mfanyakazi mmoja tu — nilipe SDL au WCF au vyote viwili?",
    "output": (
        f"{SDL_VS_WCF} "
        "Kwa mfanyakazi MMOJA: "
        "SDL: HAPANA — unahi wafanyakazi 10+ kwa SDL. "
        "WCF: NDIYO — hata mwajiri mwenye mfanyakazi 1 lazima asajili na kulipa WCF (0.5%). "
        "Thibitisha usajili wako wa WCF kupitia portal.wcf.go.tz."
    )
})
pairs.append({
    "instruction": "Kampuni yangu ina wafanyakazi 15 — lazima nilipe SDL na WCF au moja tu?",
    "output": (
        f"{SDL_VS_WCF} "
        "Kwa wafanyakazi 15: "
        "SDL: NDIYO (umepita kizingiti cha 10) — 3.5% ya mishahara yote → TRA. "
        "WCF: NDIYO (inatumika kwa wafanyakazi wote) — 0.5% → Mamlaka ya WCF. "
        "Zote mbili zinahitajika — zinawasilishwa kwa mamlaka tofauti."
    )
})
pairs.append({
    "instruction": "SDL na WCF — zote zinalipiwa TRA?",
    "output": (
        f"{SDL_VS_WCF} "
        "Hapana — zinawasilishwa kwa mamlaka tofauti. "
        "SDL → TRA (Tanzania Revenue Authority): tra.go.tz "
        "WCF → Mamlaka ya WCF (Workers' Compensation Fund): portal.wcf.go.tz "
        "Usipeleke WCF kwa TRA au SDL kwa WCF — ni malipo kwa taasisi tofauti kabisa."
    )
})
pairs.append({
    "instruction": "Kizingiti cha wafanyakazi kwa WCF — ni 10 kama SDL au tofauti?",
    "output": (
        f"{SDL_VS_WCF} "
        "WCF haina kizingiti — mwajiri yeyote mwenye mfanyakazi hata mmoja lazima asajili WCF. "
        "SDL ina kizingiti cha wafanyakazi 10+. "
        "Tofauti hii ni muhimu sana — wengi hukosa WCF wakifikiri wanahitaji wafanyakazi 10+ kwanza."
    )
})

# ── SECTION 6: VAT REGISTRATION REINFORCEMENT (20 pairs) ──────────────────
# 5 pairs — TZS 200M/12 months threshold
pairs.append({
    "instruction": "Usajili wa VAT unahitajika lini Tanzania?",
    "output": (
        "Usajili wa VAT ni lazima ukifika kizingiti cha TZS milioni 200 kwa miezi 12 "
        "au TZS milioni 100 kwa miezi 6. "
        "Kizingiti cha TZS 200M/12 miezi: ukipita kiasi hiki katika mwaka wowote, "
        "lazima usajili VAT ndani ya siku 30. "
        "Chanzo: VAT Act na TRA (tra.go.tz)."
    )
})
pairs.append({
    "instruction": "Biashara yangu inauzwa TZS 250M kwa mwaka — lazima nisajili VAT?",
    "output": (
        "Ndio — TZS 250M inazidi kizingiti cha TZS 200M/mwaka. Lazima usajili VAT. "
        "Hatua: (1) Fikia TRA mara moja (au tra.go.tz). "
        "(2) Wasilisha maombi ya usajili wa VAT ndani ya siku 30 ya kupita kizingiti. "
        "(3) Nunua EFD. (4) Anza kutoa risiti za VAT kwa wateja wako. "
        "Kuchelewa kusajili kunasababisha faini za TRA."
    )
})
pairs.append({
    "instruction": "TZS 200M kwa mwaka maana yake ni mauzaji mazuri — kama sijafika, sina wajibu?",
    "output": (
        "Ndio — chini ya TZS 200M/12 miezi na chini ya TZS 100M/6 miezi, "
        "usajili wa VAT si lazima kiautomatiki. "
        "Lakini: unaweza kusajili kwa hiari (voluntary registration) hata chini ya kizingiti "
        "— faida ni unaweza kudai VAT ya manunuzi yako (input VAT). "
        "Pima: je, wateja wako wakubwa wanahitaji invoice ya VAT? Kama ndiyo, usajili ni busara."
    )
})
pairs.append({
    "instruction": "Kizingiti cha VAT ni TZS 200M kwa mwaka au kwa mwezi?",
    "output": (
        "Kizingiti cha kawaida ni TZS 200M kwa MIEZI 12 (mwaka) — si kwa mwezi mmoja. "
        "Pia kuna kizingiti cha muda mfupi: TZS 100M kwa MIEZI 6 (miezi 6 ya mfululizo). "
        "Ukipita TZS 100M katika miezi 6 yoyote, lazima usajili VAT hata kama haujafika TZS 200M kwa mwaka."
    )
})
pairs.append({
    "instruction": "Nilianza biashara mwezi huu — ninahitaji kusajili VAT sasa?",
    "output": (
        "Kwa biashara mpya: usajili wa VAT unahitajika ukipita kizingiti, si mwanzoni. "
        "Fuatilia mauzo yako: "
        "Miezi 6 ya kwanza: ukifika TZS 100M → sajili VAT mara moja. "
        "Mwaka mmoja: ukifika TZS 200M → sajili VAT mara moja. "
        "Pia zingatia: usajili wa hiari (voluntary) unapatikana hata kabla ya kizingiti "
        "iwapo wateja wako wakubwa wanahitaji invoice ya VAT."
    )
})

# 5 pairs — TZS 100M/6 months rolling threshold
pairs.append({
    "instruction": "Kizingiti cha TZS 100M kwa miezi 6 maana yake nini?",
    "output": (
        "Kizingiti cha ziada cha VAT: TZS milioni 100 kwa miezi 6 ya mfululizo. "
        "Maana: ukiuza TZS 100M au zaidi katika kipindi chochote cha miezi 6 (si mwaka), "
        "lazima usajili VAT — hata kama jumla ya mwaka bado chini ya TZS 200M. "
        "Mfano: Julai–Desemba 2025 = TZS 110M → sajili VAT, hata kama Jan–Jun 2025 = TZS 50M."
    )
})
pairs.append({
    "instruction": "Biashara yangu ya uuzaji wa bidhaa za msimu inapata TZS 150M kwa miezi 4 ya msimu — VAT?",
    "output": (
        "TZS 150M kwa miezi 4 inazidi TZS 100M kwa miezi 6 — lazima usajili VAT. "
        "Kizingiti cha TZS 100M/6 miezi kinahusika hata kama kinatokea kwa msimu. "
        "Usidhani unaweza kuepuka VAT kwa sababu mauzo ni ya msimu — "
        "kizingiti kinafanya kazi kwa mauzo halisi ya kipindi chochote cha miezi 6."
    )
})
pairs.append({
    "instruction": "Mauzo yangu yabadilika sana kila mwezi — ninajuaje nimefikia kizingiti cha VAT?",
    "output": (
        "Fuatilia mauzo yako kila mwezi kwa njia mbili: "
        "(1) Jumla ya miezi 12 iliyopita: ukifika TZS 200M → sajili VAT. "
        "(2) Jumla ya miezi 6 yoyote ya mfululizo: ukifika TZS 100M → sajili VAT. "
        "Mbinu: weka jedwali la mauzo yako kila mwezi. "
        "Ukiona mwenendo wa kupanda, jiandae kwa usajili kabla ya kuvuka kizingiti."
    )
})
pairs.append({
    "instruction": "Kampuni yangu ina matawi matatu — kizingiti cha VAT kinahesabu matawi yote pamoja?",
    "output": (
        "Ndio — kwa kampuni moja (legal entity moja), mauzo ya matawi yote yanahesabiwa pamoja "
        "kwa kizingiti cha VAT. "
        "Matawi mawili + makao makuu: mauzo yote yajumuishwe. "
        "Ukifika TZS 200M/12 miezi au TZS 100M/6 miezi kwa jumla, "
        "kampuni nzima lazima isajili VAT — si tawi moja tu."
    )
})
pairs.append({
    "instruction": "Kizingiti cha VAT ni kwa bidhaa tu au huduma pia?",
    "output": (
        "Kizingiti cha VAT (TZS 200M/12 miezi au TZS 100M/6 miezi) kinahusika kwa: "
        "Mauzo ya bidhaa, Utoaji wa huduma, Mchanganyiko wa bidhaa na huduma. "
        "Aina ya biashara haiathiri kizingiti — inathiri tu KIWANGO cha VAT "
        "(18% standard, 16% B2C digital, 0% exports, au exempt). "
        "Mauzo yote yanajumuishwa kufikia kizingiti."
    )
})

# 5 pairs — voluntary registration benefits
pairs.append({
    "instruction": "Faida ya kusajili VAT kwa hiari (voluntary registration) kabla ya kizingiti ni nini?",
    "output": (
        "Faida za usajili wa hiari wa VAT: "
        "(1) Unaweza kudai input VAT (VAT uliyo nayo kwenye manunuzi ya biashara). "
        "(2) Wateja wako wakubwa (kampuni, serikali) wanaweza kuhitaji invoice ya VAT. "
        "(3) Unaweka heshima ya biashara mbele ya wateja wa kitaasisi. "
        "Hasara: lazima utoe risiti za VAT, uwasilishe VAT return kila mwezi, na utumie EFD. "
        "Pima manufaa dhidi ya mzigo wa uzingatifu (compliance burden)."
    )
})
pairs.append({
    "instruction": "Ninaweza kusajili VAT hata kama mauzo yangu ni TZS 50M tu kwa mwaka?",
    "output": (
        "Ndio — usajili wa hiari wa VAT unaruhusiwa hata chini ya kizingiti. "
        "TRA inakuruhusu kusajili VAT kwa hiari iwapo biashara yako imesajiliwa kisheria. "
        "Faida kuu: unaweza kudai VAT ya manunuzi yako (input VAT) kama rejareja. "
        "Omba usajili wa hiari wa VAT kupitia tra.go.tz au ofisi ya TRA karibu nawe."
    )
})
pairs.append({
    "instruction": "Wateja wangu wa serikali wanahitaji invoice ya VAT — ninahitaji kusajili VAT hata kama sijafika kizingiti?",
    "output": (
        "Ndio — usajili wa hiari wa VAT ni suluhisho lako. "
        "Wateja wa serikali na makampuni makubwa mara nyingi wanahitaji invoice ya VAT — "
        "bila usajili, huwezi kutoa invoice hiyo. "
        "Faida ya ziada: baada ya kusajili, unaweza kudai input VAT kwenye manunuzi yako ya biashara. "
        "Hata kama mauzo yako chini ya TZS 200M, usajili wa hiari ni busara kwa hali yako."
    )
})
pairs.append({
    "instruction": "Input VAT maana yake nini na ninaweza kudai lini?",
    "output": (
        "Input VAT: VAT unayolipa wakati unaponunua bidhaa au huduma kwa biashara yako. "
        "Output VAT: VAT unayokusanya kutoka kwa wateja wako. "
        "Unapaswa kulipa TRA: Output VAT MINUS Input VAT. "
        "Unaweza kudai input VAT ukiwa umesajiliwa VAT na una invoice halisi ya VAT kutoka kwa wazabuni. "
        "Kama output VAT ni ndogo kuliko input VAT: unastahili rejareja ya VAT kutoka TRA."
    )
})
pairs.append({
    "instruction": "Usajili wa VAT — ninafanya wapi na inahitaji nini?",
    "output": (
        "Usajili wa VAT unafanywa kupitia TRA: "
        "(1) Nenda tra.go.tz au ofisi ya TRA iliyo karibu. "
        "(2) Hati zinazohitajika: TIN yako, cheti cha usajili wa BRELA, akaunti ya benki ya biashara, "
        "hati ya utambulisho wa mmiliki/wakurugenzi. "
        "(3) Baada ya usajili: TRA inakupa nambari ya VAT (VAT registration number). "
        "(4) Nunua na usajili EFD. "
        "(5) Anza kutoa invoice za VAT kwa wateja wako na kuwasilisha VAT return kila mwezi tarehe 20."
    )
})

# 5 pairs — professional mandatory registration
pairs.append({
    "instruction": "Mhasibu (CPA) aliyesajiliwa Tanzania anahitaji kusajili VAT hata kama ana wateja wachache?",
    "output": (
        "Ndio — wataalamu walioidhinishwa (CPA, wakili, wahandisi) mara nyingi wanazingatiwa na TRA "
        "kwa VAT bila kujali kizingiti cha mauzo. "
        "Hali ya CPA: TRA inaweza kuhitaji usajili wa VAT kulingana na aina ya huduma na hali ya leseni. "
        "Thibitisha hali yako maalum na TRA — wataalamu wanaosajiliwa wana mwongozo maalum."
    )
})
pairs.append({
    "instruction": "Wakili wa mahakama ana mauzo ya TZS 80M kwa mwaka — anahitaji VAT?",
    "output": (
        "Wataalamu wa kisheria (wakili, mhasibu, daktari) wana hali maalum kwa VAT Tanzania. "
        "TRA inaweza kuhitaji wataalamu walioidhinishwa kusajili VAT bila kujali kizingiti cha TZS 200M — "
        "hii inategemea aina ya leseni na hukumu za TRA kwa sekta yako. "
        "Ufumbuzi: wasiliana na TRA au mwanasheria wa kodi kujua hali yako halisi kama wakili."
    )
})
pairs.append({
    "instruction": "Mhandisi wa ujenzi aliyesajiliwa Engineers Registration Board — VAT inamshughulikia lini?",
    "output": (
        "Wahandisi walioidhinishwa wana hali maalum kwa VAT — TRA inaweza kuhitaji usajili "
        "bila kujali kizingiti cha kawaida cha TZS 200M. "
        "Kanuni ya jumla: wataalamu wote walioidhinishwa waangalie mwongozo maalum wa TRA kwa sekta yao. "
        "Hatua: wasiliana na TRA au mwanasheria wa kodi kujua mahitaji yako kama mhandisi."
    )
})
pairs.append({
    "instruction": "Daktari binafsi aliye na kliniki ndogo — anahitaji kusajili VAT?",
    "output": (
        "Huduma za afya (medical services) nyingi zimesamehewa VAT (exempt) Tanzania. "
        "Hata hivyo, daktari aliyeidhinishwa anapaswa kuthibitisha na TRA: "
        "(1) Je, huduma zake ni exempt au standard rated? "
        "(2) Je, ana wajibu wowote wa usajili kama mtaalamu aliyeidhinishwa? "
        "Thibitisha hali yako maalum na TRA kwa sababu sekta ya afya ina kanuni maalum za VAT."
    )
})
pairs.append({
    "instruction": "Mshauri wa biashara (management consultant) mwenye TZS 120M kwa mwaka — VAT?",
    "output": (
        "TZS 120M/mwaka bado chini ya kizingiti cha TZS 200M/12 miezi — "
        "kwa kanuni ya kawaida, usajili wa VAT si lazima kiautomatiki. "
        "Lakini angalia: je, TZS 120M hiyo ilikuja ndani ya miezi 6? "
        "Kama ndiyo (TZS 100M+/6 miezi), usajili wa VAT unahitajika. "
        "Pia: kama wataalamu wa biashara wana mwongozo maalum wa TRA, thibitisha na TRA."
    )
})

assert len(pairs) == 60, f"Expected 60 pairs, got {len(pairs)}"

# Append to output file
with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
    for pair in pairs:
        f.write(json.dumps(pair, ensure_ascii=False) + '\n')

# Read all pairs so far for checkpoint
all_pairs = []
with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            all_pairs.append(json.loads(line))

# Save checkpoint
ckpt = os.path.join(CHECKPOINT_DIR, "ckpt_165.jsonl")
with open(ckpt, 'w', encoding='utf-8') as f:
    for pair in all_pairs:
        f.write(json.dumps(pair, ensure_ascii=False) + '\n')

print(f"Sections 4-6 complete: {len(pairs)} new pairs saved")
print(f"Total in file: {len(all_pairs)}")
print(f"Checkpoint: {ckpt}")

# Validation
vat5_correct = sum(1 for p in pairs if 'Tanzania ina viwango VITATU vya VAT peke yake' in p['output'])
vat5_error = sum(1 for p in pairs if 'asilimia 5' in p['output'] and 'VAT' in p['output'] and 'HAKUNA' not in p['output'])
sdl_rate = sum(1 for p in pairs if '3.5' in p['output'] and 'SDL' in p['output'])
sdl_vs_wcf = sum(1 for p in pairs if 'SDL = asilimia 3.5' in p['output'] and 'WCF = asilimia 0.5' in p['output'])
print(f"\nValidation:")
print(f"  VAT THREE rates stated: {vat5_correct} (target 20)")
print(f"  VAT 5% errors in output: {vat5_error} (target 0)")
print(f"  SDL 3.5% mentioned: {sdl_rate}")
print(f"  SDL vs WCF distinction: {sdl_vs_wcf} (target 5)")
