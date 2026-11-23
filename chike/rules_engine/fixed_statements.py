# -*- coding: utf-8 -*-
"""Fixed statutory statements — five questions whose answer is a CONSTANT, stated whole, no model.

WHY THIS EXISTS (2026-11-16). The live check of the 2026-11-13 coverage deploy found five answers wrong with the
correct fact at rank 1 (notice "siku 4" vs 28; severance "+25%"; overtime "25%" vs 1.5x; annual leave a non-answer;
VAT on credit sales "kidogo kidogo"). Rank 1 is the ceiling of retrieval, so no index edit reaches it: the model was
handed the fact and contradicted it. These are CONSTANTS (R19), so the cure is to state the constant without the model.

THE DISCIPLINE, and the reason each text is a whole fact and not a picked limb:
  * Each statement is the verified fact text, ALL limbs. The notice question is the sharpest case: the answer is a
    table (first month 7 days; then 4 for daily/weekly paid; 28 for monthly paid), and the asker rarely says which row
    they are in. Picking one would be a confident answer to a question they did not ask, which is exactly how "siku 4"
    reached a monthly employee. The statement never selects a limb.
  * The text is NOT a second copy that can drift: `tests/test_fixed_statements.py` asserts each statement is a
    substring of the corresponding row of `precompute_rag_embeddings.CONCISE_BILINGUAL_FACTS` (the text the index
    serves) and that every figure in it equals the locked fact's `correct_value`.
  * Nothing here computes an amount. "Severance for 5 years at 500,000" is a derived quantity (R19's Guard B): the
    statement gives the rule and leaves the arithmetic to the reader or the reviewer.

⛔ NOT AUTO-SEND ELIGIBLE (founder's decision, 2026-11-16; CLAUDE.md, the R7 amendment, recorded as a NARROWING).
These answers are model-free, so under `model_calls == 0` they would qualify for the 15-minute unreviewed send. They
must not during the pilot: they go to review like any model answer, but with a CORRECT draft. The exclusion lives in
`handler_core.engine_only_verdict` and fails closed on any route not explicitly allowed.
"""

from .results import ComputationResult, tzs

NOTICE = "notice"
SEVERANCE = "severance"
OVERTIME = "overtime"
ANNUAL_LEAVE = "annual_leave"
VAT_TIME_OF_SUPPLY = "vat_time_of_supply"
# 2026-11-16 (founder): three more constants whose rank-1 fact the model contradicted live -- voluntary VAT registration (an unhedged "Ndiyo"), the WCF accident-reporting
# trigger (counted "from the accident"), and VAT withholding on a mixed supply (the RATE apportioned instead of the VALUE). Same discipline, same exclusion from auto-send.
VAT_VOLUNTARY = "vat_voluntary_registration"
WCF_ACCIDENT = "wcf_accident_reporting"
VAT_WH_MIXED = "vat_withholding_mixed_supply"
# 2026-11-16 (founder, 3a): three more constants. They are answered from facts whose served rows are English-key index rows (disease reporting, NSSF split) or a generated table (PAYE bands), not from a
# CONCISE_BILINGUAL_FACTS row, so they are named in TOPICS_NO_CONCISE_ROW and checked by tests/test_fixed_statements_coverage_batch.py instead of the concise-row figure test.
WCF_DISEASE = "wcf_disease_reporting"
NSSF_SPLIT = "nssf_split"
PAYE_BANDS_TOPIC = "paye_band_table"
# 2026-11-17 (founder, from the live check of build a2e6611): two more constants the model got wrong with the correct row at rank 1 -- the INDIVIDUAL income-tax return deadline (answered with a tax RATE, "asilimia 0%"; the row is rank 1
# before and after the 215-row index) and the business-licence VALIDITY (premise phrasings "...sivyo?" / "si lazima ..." answered "Hapana ... kila mwaka" with no figure; a fabricated "siku 90"). Same discipline, same exclusion from auto-send.
INDIVIDUAL_RETURN = "individual_income_tax_return"
LICENCE_VALIDITY = "business_licence_validity"
# 2026-11-17 (founder, next small batch): the TIN application window (np_14, np_26, s2_08: a premise check answered "Hapana ... hakuna siku maalum za 15" to a RIGHT asker, three times) and the two-part licence FEE + RENEWAL
# question (answered with the fee only, the renewal half silently dropped). Same discipline, same exclusion from auto-send.
TIN_APPLY = "tin_apply_deadline"
LICENCE_FEE_VALIDITY = "business_licence_fee_and_validity"
# 2026-11-18 (founder, after the batch-3 live check): the COMPANY annual-return deadline. The row was at rank 1 and the model still stated "siku 42" / "mwaka wa kalenda unaofuatia" (4az), a different wrong value from the
# ones D-FIDELITY-20 catches, so only a model-free statement reaches it. Same discipline, same exclusion from auto-send.
ANNUAL_RETURN = "brela_annual_return_deadline"
# 2026-11-23 (founder): WHO IS EXEMPT FROM SDL. The live check of build d997d4d answered "Ni waajiri gani hawalipi SDL?" with a FABRICATED list (a wrong Act, an invented "under 18" category, farms "with 10+") and "Shule binafsi inalipa SDL?" with a
# confident WRONG YES (registered educational institutions are exempt), both with the correct row served at rank <= 3. The list is a CONSTANT, so it is stated whole, model-free: the LESSON, recorded in PROGRESS, is that for a constant the model
# contradicts even at rank 1-3 a statement route beats another guard (guards are the backstop, not the fix).
SDL_EXEMPTIONS = "sdl_exemptions"
# 2026-11-23 (founder): WHO PAYS SDL / IS IT DEDUCTED FROM THE EMPLOYEE. The live reply to "Mwajiri au mfanyakazi analipa SDL?" was right on the payer and then invented "Ni adhabu kwa mwajiri kuajiri wafanyakazi wengi bila kusajiliwa"
# (SDL is a levy on payroll, not a penalty). The payer is a CONSTANT (locked fact sdl_payer), so it is stated, model-free, excluded from auto-send, rather than guarded (the standing lesson of PROGRESS 4bh).
SDL_PAYER = "sdl_payer"
# 2026-11-23 (founder): three more SDL statements. The filing statement asserts ONLY what a primary source states (VETA Act s.16 and the live TRA pages read 2026-11-22) and does NOT name a form: the live pages name none (the old cached guide's ITX 300.01.E is unconfirmed as current).
SDL_HOW_TO_FILE_PAY = "sdl_how_to_file_pay"
SDL_EMPLOYEE_PREMISE = "sdl_employee_premise"
SDL_NSSF_PARTY = "sdl_nssf_party"
_SDL_PAYER_TEXT = ("SDL hulipwa na MWAJIRI pekee. Ni tozo (si adhabu) inayotozwa kwa mwajiri kwenye jumla ya mishahara ghafi anayowalipa wafanyakazi wake kila mwezi (Sheria ya Elimu na Mafunzo ya Ufundi). "
                   "Haikatwi kwenye mshahara wa mfanyakazi, na mfanyakazi halipi sehemu yoyote ya SDL.")
_SDL_FILE_PAY_TEXT = ("Ritani ya SDL na malipo yake vyote vinatakiwa kufikia tarehe 7 ya mwezi unaofuata mwezi wa mishahara (Sheria ya Elimu na Mafunzo ya Ufundi). "
                      "Ritani inawasilishwa kwa TRA kupitia IDRAS, na malipo yanafanywa kwa Kamishna wa TRA kwenye Mkoa wa Kodi ambako mwajiri amesajiliwa. "
                      "Jina la fomu na njia ya malipo (benki au namba ya kumbukumbu) havijathibitishwa hapa: thibitisha fomu na njia ya kulipa kwa sasa na TRA (tra.go.tz).")
# 2026-11-22 (founder, preliminary Gate 2 #20): a rate asked for a FUTURE year ("kiwango rasmi cha VAT kitakachotumika 2028/2029"). The honest answer is two limbs held together: the rate of a year whose Finance Act has not been passed is UNKNOWN,
# and the CURRENT rates we hold, each with the instrument it rests on. Same discipline as the rest of this route: model-free, whole, excluded from auto-send. The figures are locked facts vat_standard_rate (18%) and sdl_rate (3.5%, FA2023).
FUTURE_YEAR_RATE = "future_year_rate"


def _paye_bands_text() -> str:
    """The PAYE band table, GENERATED from rates.PAYE_BANDS so the sentence a user reads cannot drift from the engine's table (the BRELA ladder discipline). Numbering follows the served row
    `paye bands monthly 2025 26`: the 0% band is band 1, so the 20% band is band 3. A narration that numbers the bands differently contradicts the served row; stating the table is how this route avoids it."""
    from .rates import PAYE_BANDS, PAYE_NONRESIDENT_RATE
    parts = []
    for i, (lower, rate, base) in enumerate(PAYE_BANDS):
        top = PAYE_BANDS[i + 1][0] if i + 1 < len(PAYE_BANDS) else None
        pct = f"{rate * 100:.0f}%"
        if i == 0:
            parts.append(f"kiwango cha 1: hadi {tzs(top)} = {pct}")
        elif top is None:
            parts.append(f"kiwango cha {i + 1}: zaidi ya {tzs(lower)} = {tzs(base)} + {pct} ya kinachozidi {tzs(lower)}")
        else:
            lead = f"{tzs(base)} + " if base else ""
            parts.append(f"kiwango cha {i + 1}: {tzs(lower + 1)} hadi {tzs(top)} = {lead}{pct} ya kinachozidi {tzs(lower)}")
    return ("Viwango vya PAYE vya kila mwezi (mkazi, 2025/26): " + "; ".join(parts) + ". "
            f"Asiye mkazi analipa {PAYE_NONRESIDENT_RATE * 100:.0f}% tambarare (kodi ya mwisho, si mabano). "
            "Hakuna punguzo la kibinafsi tofauti — kiwango cha 0% cha mwanzo ndicho kisicholipiwa kodi.")

# topic -> (locked-fact key, the statement, citation note). Statement text is lifted from the served concise row with
# the leading question sentence removed (the user has just asked it).
STATEMENTS = {
    NOTICE: (
        "termination_notice_period",
        "Notisi ya kuacha au kuachishwa kazi: mwezi wa kwanza ni siku 7. Baada ya hapo: siku 4 kwa mfanyakazi wa kila siku "
        "au kila wiki, siku 28 kwa wa kila mwezi. Mkataba unaweza kuweka muda mrefu zaidi ikiwa ni sawa kwa mwajiri na "
        "mfanyakazi. Notisi iandikwe ikitaja sababu na tarehe; mwajiri anaweza kulipa mshahara wa kipindi cha notisi "
        "badala yake (ELRA).",
        "ELRA Cap.366, notice of termination (s.41 R.E.2019; TanzLII s.42) — all three limbs stated, none selected",
    ),
    SEVERANCE: (
        "severance_pay",
        "Malipo ya kuachishwa kazi (severance pay): mfanyakazi aliyetimiza miezi 12 mfululizo na akaachishwa anapata "
        "angalau mshahara wa msingi wa siku 7 kwa kila mwaka kamili, hadi miaka 10. Hayalipwi kwa kuachishwa kihalali kwa "
        "utovu wa nidhamu, au anayekataa kazi mbadala bila sababu, au aliyestaafu au mkataba kuisha (ELRA).",
        "ELRA Cap.366, severance pay (s.42 R.E.2019; TanzLII s.43) — a rule, never an amount",
    ),
    OVERTIME: (
        "overtime_pay_rate",
        "Overtime (saa za ziada) inalipwa angalau mara 1.5 ya mshahara wa msingi. Overtime ni kwa makubaliano tu, na "
        "isizidi saa 50 kwa kila wiki 4 (ELRA).",
        "ELRA Cap.366, hours of work (s.19 R.E.2019; TanzLII s.20)",
    ),
    ANNUAL_LEAVE: (
        "annual_leave_days",
        "Likizo ya mwaka ni angalau siku 28 mfululizo kwa kila mzunguko wa likizo (sikukuu zilizo ndani zinahesabiwa), na "
        "mfanyakazi analipwa mshahara wake. Mwajiri apange ichukuliwe ndani ya miezi 6 baada ya mzunguko, au miezi 12 kwa "
        "ridhaa ya mfanyakazi na sababu ya kiutendaji (ELRA).",
        "ELRA Cap.366, annual leave (s.31 R.E.2019; TanzLII s.32)",
    ),
    VAT_TIME_OF_SUPPLY: (
        "vat_credit_sale_timing",
        "VAT inakuwa inadaiwa mapema zaidi kati ya: siku ya kutoa invoice, siku ya kupokea malipo (hata sehemu), au wakati "
        "wa usambazaji. Hivyo ukitoa invoice, VAT inadaiwa hata mteja asipolipa bado. Return ya VAT ni tarehe 20 ya mwezi "
        "unaofuata (Sheria ya VAT).",
        "VAT Act Cap.148 R.E.2023, s.15(a)-(c) and s.70(1) — time of supply is the earliest of the three events",
    ),
    VAT_VOLUNTARY: (
        "vat_voluntary_registration",
        "Njia zilizotajwa wazi na Sheria ya VAT ni: kufikia kiwango (TZS 200M kwa miezi 12 au TZS 100M kwa miezi 6), mtoa huduma za kitaalamu, taasisi ya Serikali, na anayetarajia kuanza biashara mwenye ushahidi (anaweza kuomba wakati wowote; Kamishna ndiye anayeamua). Maandishi ya Sheria hayataji usajili wa hiari kwa mfanyabiashara aliyepo aliye chini ya kiwango, lakini TRA inasema usajili wa hiari unaruhusiwa kwa 'shughuli maalum za kiuchumi' bila kuzitaja -- thibitisha na TRA kabla ya kuomba (Sheria ya VAT; TRA).",
        "VAT Act Cap.148 R.E.2023 s.28, s.29(1)-(3), s.30(2) (ss.29(4)-(6) added by FA2024 s.105 / FA2025 s.126); TRA FAQ tra.go.tz/ajax/faq/57 (2026-11-16): 'Voluntary registration is also allowed for certain specific economic activities' -- Act and FAQ UNRECONCILED, so the statement hedges and names the routes",
    ),
    WCF_ACCIDENT: (
        "wcf_accident_reporting",
        "Mfanyakazi amjulishe mwajiri ndani ya siku 2 za kazi; mwajiri aijulishe WCF ndani ya siku 7 (Kanuni: siku 7 za kazi) tangu apokee taarifa au ajue ajali -- si tangu tarehe ya ajali. Mfanyakazi anaweza kuijulisha WCF mwenyewe ndani ya siku 7 za kazi. Sheria inasema 'siku 7' tu: ripoti mapema (Sheria ya Fidia kwa Wafanyakazi; Kanuni za Fidia kwa Wafanyakazi, 2016).",
        "Workers Compensation Act Cap.263 R.E.2023 s.34(1) ('within seven days after receiving a notice ... or having learned in some other way'); GN 185/2016 Reg.15(1),(2),(4) -- the clock runs from RECEIPT of notice, not from the accident; Act 'seven days' vs Regulation 'seven working days' recorded as unresolved",
    ),
    WCF_DISEASE: (
        "wcf_disease_reporting_deadline",
        "Ugonjwa wa kazini unaripotiwa kwa hatua MBILI, si siku 7 moja kwa moja (Kanuni za Fidia kwa Wafanyakazi, 2016 — GN 185/2016, Kanuni ya 16): (1) mfanyakazi amjulishe mwajiri ndani ya siku 14 za kazi tangu ugonjwa kugunduliwa; "
        "(2) mwajiri aijulishe WCF ndani ya siku 7 za kazi tangu APOKEE taarifa hiyo ya mfanyakazi. Hivyo kutoka utambuzi hadi WCF inaweza kufikia siku 21 za kazi. "
        "Kifo kazini kiripotiwe WCF ndani ya miezi 12, na madai ya fidia yawasilishwe ndani ya miezi 12 tangu ajali au ugonjwa kugunduliwa. Thibitisha na WCF (wcf.go.tz).",
        "Workers Compensation Regulations 2016 (GN 185/2016) Reg.16(1) employee to employer 14 working days of diagnosis; Reg.16(2) employer to WCF 7 working days of RECEIVING that notice; Reg.17(2) death 12 months; Reg.19(1) claim 12 months. "
        "Served as English index row 46 (a Swahili concise row is pending an R15 regen); the gate's eval_239 answered 'siku 14 za kazi tangu kugunduliwa' with row 46 in context",
    ),
    NSSF_SPLIT: (
        "NSSF_split_triggers",
        "Jumla ya NSSF ni asilimia 20 ya mshahara ghafi daima. Mgao wa kawaida ni asilimia 10 mwajiri na asilimia 10 mfanyakazi, lakini si mgawanyo pekee halali: mwajiri anaweza kuchagua kuchangia kiwango kikubwa zaidi, hadi mchango wote, "
        "kwa hiyo 15% + 5% au 20% + 0% ni mifano ya chaguo hilo, si orodha kamili iliyotajwa na sheria. Chaguo hilo lina masharti kwa wanachama fulani (Sheria ya NSSF). Jumla haibadiliki — ni nani anabeba sehemu ndiyo hubadilika. Thibitisha na NSSF (nssf.go.tz).",
        "NSSF Act Cap.50 R.E.2023 s.12(1)-(3) and First Schedule (locked fact NSSF_split_triggers, read 2026-10-05 from two byte-identical routes, sha256 2a820e67...; s.12(2)-(3) re-read 2026-11-16 in the cached R.E.2015 as corroboration, edition flagged). "
        "The Act does not enumerate permitted splits; eval_348 answered 'Ndiyo ... hakuna mgawanyo mwingine' with row 78 in context",
    ),
    PAYE_BANDS_TOPIC: (
        "paye_bands_monthly_2025_26",
        _paye_bands_text(),
        "Income Tax Act Cap.332, First Schedule individual PAYE table, as at FA2026 (rates.PAYE_BANDS, locked facts paye_bands_monthly_2025_26 / paye_all_bands_sequence / paye_nonresident_flat_rate / paye_personal_relief); the text is GENERATED from rates.PAYE_BANDS",
    ),
    VAT_WH_MIXED: (
        "vat_withholding_mixed_supply",
        'VAT ya zuio kwa mauzo yenye bidhaa na huduma pamoja: tangu 1 Julai 2026, thamani inayozuiwa inagawanywa kwa uwiano wa 3:2 kati ya bidhaa na huduma (Sheria ya Fedha 2026). Kiwango cha bidhaa ni 3% na cha huduma ni 6%.',
        "Finance Act 2026 s.91(b) adding VAT Act s.5(7): the taxable VALUE subject to withholding is apportioned 3:2 goods:services, in force 1 July 2026; rates 3% / 6% unchanged (VAT Act s.5(5)); no blended percentage is stated because the Act gives none",
    ),
    INDIVIDUAL_RETURN: (
        "individual_income_tax_return",
        "Kila mtu awasilishe return ndani ya miezi 6 baada ya mwisho wa mwaka wa mapato. Mwaka wa mapato ni mwaka wa kalenda, hivyo mwisho ni 30 Juni ya mwaka unaofuata. "
        "Mkazi asiye na kodi ya kulipa, au mwenye mapato ya ajira tu ambayo PAYE inakatwa, hahitajiki isipokuwa TRA ikiomba (Sheria ya Kodi ya Mapato).",
        "Income Tax Act Cap.332 R.E.2023 s.117(1) six months, s.20(1) calendar year, s.118 exceptions (locked fact individual_income_tax_return). The nine-month limb added by FA2024 s.44 is for 'a person whose financial statement is audited "
        "by the Controller and Auditor General'; an individual business's accounts are not, so it is DELIBERATELY not stated here (checked 2026-11-17: the Act says 'a person', so it is not claimed to be impossible either)",
    ),
    LICENCE_VALIDITY: (
        "business_licence_expiry_30_june",
        "Leseni ya biashara ni halali kwa miezi 12 tangu tarehe ilipotolewa; si tarehe maalum ya kalenda (si 30 Juni, si 31 Machi: sheria ya zamani ilibadilishwa). "
        "Unaweza kulipia ada ya hadi miaka 3 mfululizo (Sheria ya Leseni za Biashara). Leseni za kawaida (kundi B) hutolewa na halmashauri ya eneo lako; leseni za kundi A "
        "(biashara za kitaifa au kimataifa) hutolewa na BRELA (brela.go.tz). Sheria inamwachia Waziri kuteua mamlaka ya leseni kwa tangazo la Gazeti: thibitisha na halmashauri yako.",
        "Business Licensing Act Cap.101 R.E.2023 s.7(1)-(2) validity, s.6(1) appointment of licensing authorities by Gazette order (not located); category split from BRELA Newsletter No.10 (PORTAL tier). Locked facts "
        "business_licence_expiry_30_june and business_licence_authority; Cap.208 R.E.2002 s.7 (30 June) superseded by Act 2 of 2014 s.6",
    ),
    TIN_APPLY: (
        "tin_apply_deadline",
        "Anayeanza biashara aombe Namba ya Mlipakodi (TIN) kwa TRA ndani ya siku 15 tangu aanze biashara, akiwa na ushahidi wa utambulisho. Mtu ana TIN moja tu kwa kodi zote; raia mwenye NIDA hupewa TIN iliyounganishwa na namba yake ya NIDA. "
        "TRA inaweza kutoa TIN ndani ya siku 7 tangu ombi (Sheria ya Usimamizi wa Kodi).",
        "Locked fact tin_apply_deadline (Tax Administration Act Cap.438 R.E.2023: apply within 15 days of starting business; one TIN per person; may be issued within 7 days). The 15 days is the window to APPLY, not a duty to hold a TIN on day one -- "
        "the point np_14 / np_26 / s2_08 got wrong or inverted",
    ),
    ANNUAL_RETURN: (
        "company_annual_return_deadline",
        "Annual return ya kampuni hufanywa kila mwaka: kila return hutayarishwa hadi tarehe ya maadhimisho ya kuanzishwa kwa kampuni (au ya return iliyotangulia). "
        "Ukichelewa zaidi ya siku 28 baada ya tarehe hiyo, kampuni na maafisa wake wanaweza kutozwa faini (Sheria ya Makampuni). Si miezi 12 tangu usajili, na si 30 Septemba. Thibitisha na BRELA (brela.go.tz).",
        "Locked fact company_annual_return_deadline (Companies Act Cap.212 R.E.2023, edition asserted: each return is made up to the anniversary of incorporation or of the previous return date; delivered within 28 days of that date; "
        "the company and every officer in default are liable to a fine). The served row's own wording, whole. No fine AMOUNT is stated (the Act gives none here; the BRELA late-filing fee schedule is a separate fact). "
        "Founding specimens: live replies 'siku 42' and 'mwaka wa kalenda unaofuatia' (PROGRESS 4az)",
    ),
    LICENCE_FEE_VALIDITY: (
        "business_licence_expiry_30_june",
        "Kuhusu ada: ada imepangwa KITAIFA chini ya Sheria ya Leseni za Biashara, na halmashauri hairuhusiwi kutoza zaidi ya ada iliyopangwa. Ada hutegemea aina ya biashara na eneo (jiji/manispaa, wilaya/mji, au kijiji) na kama ni leseni kuu au ya tawi; "
        "uliza halmashauri yako kwa ada ya aina yako. Kuhusu muda: leseni ya biashara ni halali kwa miezi 12 tangu tarehe ilipotolewa; si tarehe maalum ya kalenda (si 30 Juni, si 31 Machi: sheria ya zamani ilibadilishwa). "
        "Unaweza kulipia ada ya hadi miaka 3 mfululizo (Sheria ya Leseni za Biashara). Leseni za kawaida (kundi B) hutolewa na halmashauri ya eneo lako; leseni za kundi A (biashara za kitaifa au kimataifa) hutolewa na BRELA (brela.go.tz). "
        "Sheria inamwachia Waziri kuteua mamlaka ya leseni kwa tangazo la Gazeti: thibitisha na halmashauri yako.",
        "BOTH LIMBS of a two-part question, whole: the fee limb from locked fact business_licence_fee_national_schedule_local_collection (its clause 'leseni hutolewa na kukusanywa na halmashauri' is DROPPED here because the validity limb says Category A is "
        "issued by BRELA and the two must not contradict inside one answer) and the validity statement of business_licence_validity (Cap.101 R.E.2023 s.7(1)-(2); BRELA Newsletter No.10, portal tier). No figure of a FEE is stated: the Schedule varies by trade and area",
    ),
    FUTURE_YEAR_RATE: (
        "vat_standard_rate",
        "Kiwango cha kodi cha mwaka ujao au mwaka wa baadaye hakijulikani bado: viwango hubadilishwa tu na Sheria ya Fedha ya kila mwaka, ambayo hupitishwa Juni na kuanza kutumika 1 Julai, kwa hiyo siwezi kukupa kiwango rasmi cha mwaka ambao "
        "Sheria yake haijatoka. Viwango vya sasa tulivyo navyo: VAT ya kawaida ni asilimia 18 (Sheria ya VAT, haijabadilika tangu 2015); SDL ni asilimia 3.5 ya mishahara ghafi (tangu 1 Julai 2023, Sheria ya Fedha 2023; ilikuwa asilimia 4). "
        "Kwa bajeti, tumia viwango hivi vya sasa kama makadirio tu, na uthibitishe na TRA (tra.go.tz) Sheria ya Fedha ya mwaka husika itakapotoka.",
        "Locked facts vat_standard_rate (18% general rate, VAT Act Cap.148, 'unchanged since 2015'; the 16% B2C e-payment carve-out is deliberately NOT stated here: it is CONFIRMED-SECONDARY) and sdl_rate (3.5% from 1 Jul 2023, Finance Act 2023, was 4%). "
        "The Finance Act is passed in June and commences 1 July: Finance Act 2025 commenced 1 Jul 2025 (locked facts) and the rates of a year whose Act has not been passed are unknowable, which is the point. 'Current' is as held in the locked facts, not a "
        "claim that Finance Act 2026 was read for these two rates. Founding specimen: preliminary Gate 2 #20 (gp_20), 'kiwango rasmi cha VAT kitakachotumika Tanzania mwaka 2028/2029'",
    ),
    SDL_EXEMPTIONS: (
        "sdl_exemption_categories",
        "SDL haitozwi kwa waajiri na taasisi zilizoorodheshwa kisheria (Sheria ya Elimu na Mafunzo ya Ufundi): taasisi au idara ya Serikali inayofadhiliwa kikamilifu kupitia ruzuku ya Serikali; balozi (misheni za kidiplomasia); "
        "Umoja wa Mataifa na mashirika yake; taasisi za kimataifa au za kigeni zinazojihusisha na misaada au msaada wa kiufundi; taasisi za dini, kwa wafanyakazi walioajiriwa tu kuendesha ibada, kutoa mafundisho ya dini au huduma ya afya ya jamii; "
        "mashirika ya hisani (kama yalivyofafanuliwa kisheria); taasisi za elimu zilizosajiliwa (shule za awali, msingi na sekondari, vyuo vya ufundi na elimu, vyuo vikuu na taasisi za elimu ya juu); halmashauri za serikali za mitaa; "
        "wanafunzi wa mafunzo kwa vitendo chini ya mpango wa TaESA; waajiri wa mashambani, kwa wafanyakazi wanaofanya kilimo moja kwa moja tu (si usimamizi wala usindikaji); na mamlaka ya maji na usafi wa mazingira, kwa vibarua wa miradi ya maji. "
        "Waziri wa Fedha pia anaweza kusamehe mtu yeyote kwa tangazo la Gazeti. Mwajiri asiye kwenye orodha hii wala asiyesamehewa kwa Gazeti, mwenye wafanyakazi 10 au zaidi, hutozwa SDL. Thibitisha na TRA (tra.go.tz).",
        "Locked fact sdl_exemption_categories (VETA Act Cap.82 R.E.2023 s.19(1)(a)-(j) and s.19(3); (k) added by Finance Act 2024 s.112; (a) reworded 'through Government subvention' by Finance Act 2026 s.98; Finance Act 2025 has no VETA amendment) and the per-category facts. "
        "Founder-approved text, whole: every category stated, none selected, so it answers a LIST ask and a CATEGORY ask (a school, a religious body, a council) with the same sentence. Household employers are in none of these; whether domestic workers count toward the ten is the "
        "OTHER hedge (sdl_domestic_workers_scope) and that question is vetoed off this route. R44: the Act is named, no section number",
    ),
    SDL_PAYER: (
        "sdl_payer",
        "SDL hulipwa na MWAJIRI pekee. Ni tozo (si adhabu) inayotozwa kwa mwajiri kwenye jumla ya mishahara ghafi anayowalipa wafanyakazi wake kila mwezi (Sheria ya Elimu na Mafunzo ya Ufundi). "
        "Haikatwi kwenye mshahara wa mfanyakazi, na mfanyakazi halipi sehemu yoyote ya SDL. Thibitisha na TRA (tra.go.tz).",
        "Locked fact sdl_payer (VETA Act Cap.82 R.E.2023 s.14(2): the levy is a sum equal to the stated percentage of the total gross monthly emoluments payable BY THE EMPLOYER to his employees; no provision of ss.14-19 makes any part deductible from "
        "employee emoluments; direct read 2026-09-02, edition asserted). 'Si adhabu' is the Act's own word: it is a LEVY (s.14), which is what the live 'Ni adhabu kwa mwajiri ...' invention got wrong. No rate and no headcount threshold are stated here: those "
        "questions are vetoed off this route to the SDL engine / rate statement. R44: the Act is named, no section number. Founding specimen: build a8a0274 live, 'Mwajiri au mfanyakazi analipa SDL?'",
    ),
    SDL_HOW_TO_FILE_PAY: (
        "sdl_how_to_file_pay",
        _SDL_FILE_PAY_TEXT,
        "VETA Act Cap.82 R.E.2023 s.16(1) the employer files with the Commissioner, on or before the seventh day of each month, a return of the total gross monthly emoluments of the preceding month and the levy payable; s.16(2) the levy is paid to the Commissioner on that same date; "
        "s.16 is unamended by Finance Acts 2024, 2025 and 2026 (FA2024 s.112 and FA2026 s.98 amend s.19 only; edition asserted in the manifest). Live TRA pages, fetched 2026-11-22T22:47:49Z (curl, 200): EN /page/skills-development-levy-sdl sha256 f9bad8ad485f4b9d1e788265c7771289a1e1f7c030cf60d1c76389a038222c64 and "
        "SW /sw/page/skills-development-levy-sdl sha256 bc3b31592b49e428924c4fc2f58ccc5b14778193e65b88480d38d6096a888679: the return goes to TRA through IDRAS by the 7th; the EN page says the employer pays 'to the respective Tax Region in which such employer is registered'. "
        "NEITHER page names a form, a control number or a bank, so none is stated here: the older undated cached guide's form ITX 300.01.E is UNCONFIRMED as current (R29 mode 3) and is deliberately omitted. Founder-approved 2026-11-23 (form name NOT asserted). R44: the Act is named, no section number",
    ),
    SDL_EMPLOYEE_PREMISE: (
        "sdl_payer",
        _SDL_PAYER_TEXT + " " + _SDL_FILE_PAY_TEXT,
        "The correction first (locked fact sdl_payer: VETA Act Cap.82 R.E.2023 s.14(2), employer only, nothing deductible from emoluments), then the filing statement (sdl_how_to_file_pay, same sources). It answers a question that PRESUPPOSES the employee pays or is deducted "
        "and asks where/how to pay ('Mfanyakazi analipa SDL wapi?'): build a67462c's live reply agreed with the premise ('Mfanyakazi anachangia SDL ... mwajiri kukata 3.5% ya mishahara') because the where/how veto sent the question to the model. Founder-approved 2026-11-23",
    ),
    SDL_NSSF_PARTY: (
        "sdl_payer",
        "SDL na NSSF hazifanani. SDL hulipwa na MWAJIRI pekee: haikatwi kwenye mshahara wa mfanyakazi, na mfanyakazi halipi sehemu yoyote ya SDL. "
        "NSSF: jumla ni asilimia 20 ya mshahara ghafi; mgao wa kawaida ni asilimia 10 mwajiri na asilimia 10 mfanyakazi, na sehemu ya mfanyakazi (asilimia 10) HUKATWA kwenye mshahara wake. "
        "Mwajiri anaweza kuchagua kubeba sehemu kubwa zaidi ya NSSF, kwa masharti ya Sheria ya NSSF. Thibitisha na TRA (tra.go.tz) na NSSF (nssf.go.tz).",
        "SDL half: locked fact sdl_payer (VETA Act Cap.82 R.E.2023 s.14(2), employer only, nothing deductible). NSSF half: the existing nssf_split statement and locked fact NSSF_split_triggers / index row 9 (NSSF Act Cap.50 R.E.2023 s.12; total 20% of gross, usual split 10% + 10%, "
        "the employee's share deducted from wages; the employer may elect to bear more). Founding specimen: build a67462c live, 'SDL na NSSF zinakatwa kwa mfanyakazi?' -> 'Mfanyakazi hakatiwi chochote katika SDL au NSSF' (wrong for NSSF). Founder-approved 2026-11-23. R44: Acts named, no section number",
    ),
}

TOPICS = tuple(STATEMENTS)
TOPICS_NO_CONCISE_ROW = frozenset({WCF_DISEASE, NSSF_SPLIT, PAYE_BANDS_TOPIC, LICENCE_VALIDITY, LICENCE_FEE_VALIDITY, FUTURE_YEAR_RATE, SDL_EXEMPTIONS, SDL_PAYER, SDL_HOW_TO_FILE_PAY, SDL_EMPLOYEE_PREMISE, SDL_NSSF_PARTY})


def fixed_statement(topic) -> ComputationResult:
    """The whole statement for `topic`. An unknown topic raises: a statement route with no statement must never fall back to
    generation or to a guess (R31: a branch with no extractor is a capability that does not exist)."""
    if topic not in STATEMENTS:
        raise KeyError(f"no fixed statement for topic {topic!r}")
    key, text, note = STATEMENTS[topic]
    return ComputationResult(
        computation="fixed_statement",
        applicable=True,
        amount=None,                      # R19: a constant, never a derived amount.
        working=text,
        inputs={"topic": topic, "fact": key},
        note=note,
    )
