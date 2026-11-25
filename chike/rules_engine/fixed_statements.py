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
# 2026-11-23 (founder, next window): ten more model-free statements. Same discipline as every topic above: a CONSTANT (or, for the audit, a HEDGE), whole, no model, excluded from auto-send (`engine:fixed_statement`), R44 (Acts named, no section number).
SDL_NSSF_PAYE_PARTY = "sdl_nssf_paye_party"        # the live "Hapana ... zinakatwa kwa MWAJIRI pekee" wrong reply: SDL employer only; NSSF employee share deducted; PAYE deducted from the employee
NSSF_PARTY = "nssf_party"                          # "NSSF inakatwa kwa mfanyakazi?" -> a garbled "10% sawa na 20%"
BRELA_THREE_FORMS = "brela_three_forms"            # gate rows 071, 301, 304
BRELA_FEE_NO_SHARE_CAPITAL = "brela_fee_no_share_capital"   # gate row 383; portal tier, effective date unknown
GN487A_PENALTIES = "gn487a_penalties"              # gate row 163; read from the gazetted Order itself (edition asserted), not from practitioner alerts
VAT_WITHHOLDING_RATES = "vat_withholding_rates"    # gate rows 044, 048
VAT_PROFESSIONAL_SERVICES = "vat_professional_services"   # gate row 025
BRELA_LATE_ANNUAL_RETURN = "brela_late_annual_return"      # gate row 085, scoped to the penalty
SDL_PAYE_DEADLINE = "sdl_paye_deadline"            # gate row 127
SDL_AUDIT_HEDGE = "sdl_audit_hedge"                # the live reply invented an eight-point audit and "P9 forms": a hedge to TRA, no procedure
# 2026-11-24 (founder, next batch): the SDL base (VETA Act s.14(3): allowances INCLUDED; benefits in kind not named, so asserted neither way), and the two THREE-LEVY statements whose live replies were wrong: the rate question ("PAYE ni asilimia 8 ... 14%")
# and the deadline question ("... michango ya NSSF ... ifikapo tarehe 7").
SDL_BASE = "sdl_base"
LEVY_RATES_THREE = "levy_rates_three"
LEVY_DEADLINES_THREE = "levy_deadlines_three"
VAT_MEDICAL = "vat_medical_services"          # "Daktari ... kusajili VAT?" -> a live "Ndiyo": medical services are an EXEMPT supply on two conditions
# 2026-11-25 (founder, from the live check of build 37cdf9d): MEDICINES / approved medical equipment are VAT-EXEMPT (live: "zero-rated (tozo 0%)"), and the PAYE BASE is employment income (live: "basic salary only"). Both from approved locked facts.
VAT_MEDICINES = "vat_medicines"
PAYE_BASE = "paye_base"


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
    SDL_NSSF_PAYE_PARTY: (
        "sdl_payer",
        "SDL, NSSF na PAYE hazifanani. SDL hulipwa na MWAJIRI pekee: haikatwi kwenye mshahara wa mfanyakazi, na mfanyakazi halipi sehemu yoyote ya SDL. "
        "NSSF: jumla ni asilimia 20 ya mshahara ghafi; mgao wa kawaida ni asilimia 10 mwajiri na asilimia 10 mfanyakazi, na sehemu ya mfanyakazi (asilimia 10) HUKATWA kwenye mshahara wake; mwajiri anaweza kuchagua kubeba sehemu kubwa zaidi, kwa masharti ya Sheria ya NSSF. "
        "PAYE: ni kodi ya mapato ya ajira ya MFANYAKAZI; mwajiri ndiye anayeikata kwenye mshahara wake na kuipeleka TRA (Sheria ya Kodi ya Mapato). Kiasi cha PAYE kinategemea viwango vya kodi vya kila mwezi. Thibitisha na TRA (tra.go.tz) na NSSF (nssf.go.tz).",
        "SDL: locked fact sdl_payer (VETA Act Cap.82 R.E.2023 s.14(2), employer only, nothing deductible). NSSF: NSSF_split_triggers (NSSF Act Cap.50 R.E.2023 s.12; total 20%, usual split 10% + 10%, employee's share deducted; employer may elect to bear more). "
        "PAYE: paye_remittance_deadline (Income Tax Act Cap.332 R.E.2023 s.104 the employer withholds from employment income, s.109(1) pays it to the Commissioner; direct read 2026-11-13, FA2024/25/26 checked). Founding specimen: build b96e8a8 live, "
        "'SDL, NSSF na PAYE zinakatwa kwa mfanyakazi?' -> 'Hapana ... zinakatwa kwa MWAJIRI pekee' (wrong for NSSF's 10% and PAYE). Founder-approved 2026-11-23. R44: Acts named, no section number",
    ),
    NSSF_PARTY: (
        "NSSF_split_triggers",
        "NSSF: jumla ni asilimia 20 ya mshahara ghafi. Mgao wa kawaida ni asilimia 10 mwajiri na asilimia 10 mfanyakazi: sehemu ya mfanyakazi (asilimia 10) HUKATWA kwenye mshahara wake, na mwajiri analipa sehemu yake ya asilimia 10 mwenyewe (haikatwi kwa mfanyakazi). "
        "Mwajiri anaweza kuchagua kubeba sehemu kubwa zaidi, kwa masharti ya Sheria ya NSSF. Thibitisha na NSSF (nssf.go.tz).",
        "The NSSF half of sdl_nssf_party, whole: locked fact NSSF_split_triggers / index row 9 (NSSF Act Cap.50 R.E.2023 s.12; total 20% of gross, usual split 10% + 10%, the employee's share deducted from wages; the employer may elect to bear more). "
        "Founding specimen: build b96e8a8 live, 'NSSF inakatwa kwa mfanyakazi?' -> 'Ndiyo ... asilimia 10 ya mshahara wake, sawa na asilimia 20 ya mshahara wake' (garbled). Founder-approved 2026-11-23. R44: the Act is named, no section number",
    ),
    BRELA_THREE_FORMS: (
        "brela_business_structures",
        "BRELA husajili biashara katika aina TATU kuu za kisheria: (1) mmiliki mmoja (sole proprietor) na (2) ubia (partnership, watu wawili au zaidi) -- zote mbili husajiliwa kama jina la biashara chini ya Sheria ya Majina ya Biashara; (3) kampuni yenye dhima ndogo, inayosajiliwa chini ya Sheria ya Makampuni. "
        "Uchaguzi kati ya jina la biashara na kampuni unategemea muundo wa kisheria na dhima unayotaka, SI idadi ya wafanyakazi wala kiasi cha mtaji: hakuna kizingiti cha wafanyakazi au mtaji kinachokulazimisha kusajili kampuni. "
        "BRELA pia husimamia alama za biashara, hataza na ubunifu wa viwanda (haki miliki), ambavyo si miundo ya biashara. Kama usajili ni lazima kwa shughuli yako, thibitisha na BRELA (brela.go.tz).",
        "Locked fact brela_business_structures (Business Names (Registration) Act Cap.213 s.2: a 'business name' covers firms, individuals and corporations; Companies Act Cap.212; CONFIRMED 2026-07-25; index row 82). 'NOT on the number of employees or the amount of capital' is the fact's own wording. "
        "PAYROLL is deliberately NOT mentioned: the fact says nothing about it, so 'payroll creates no BRELA duty' (the 4bk table's wording) is not claimed. Gate rows eval_071, eval_301, eval_304. Founder-approved 2026-11-23. R44: Acts named, no section number",
    ),
    BRELA_FEE_NO_SHARE_CAPITAL: (
        "company_registration_fee_no_share_capital",
        "Kwa ratiba ya ada ya BRELA iliyochapishwa kwenye tovuti yao (iliyosomwa 2026-10-06), ada ya kusajili kampuni isiyo na mtaji wa hisa ni TZS 500,000. Tarehe ambayo ada hiyo ilianza kutumika HAIJULIKANI: ratiba ilibadilika kati ya 2026-06-30 na 2026-10-06, na hapo awali ilichapishwa TZS 300,000. "
        "Ada za BRELA hubadilika, kwa hiyo thibitisha kiasi cha sasa na BRELA (brela.go.tz).",
        "Locked fact company_registration_fee_no_share_capital: BRELA fee schedule item 2, PORTAL tier (brela.go.tz/pages/tozo-za-kampuni), dated and sha256-pinned capture of 2026-10-06 (8d5543ac...); the 2026-06-30 capture read TZS 300,000. effective_date is EXPLICITLY UNKNOWN (our observation date is not an effective date, "
        "CLAUDE.md Section 11). The Companies Act delegates every fee amount to Minister's regulations, so the statute tier is silent and the regulations are unlocated. Gate row eval_383. Founder-approved 2026-11-23 ('worded with effective date unknown')",
    ),
    GN487A_PENALTIES: (
        "gn487a_penalty_noncitizen",
        "Amri ya GN 487A (Business Licensing (Prohibition of Business Activities for Non-Citizens) Order, 2025, iliyochapishwa 28 Julai 2025) inakataza wasio raia kufanya shughuli 15 zilizoorodheshwa kwenye Jedwali lake. Adhabu, mtu akihukumiwa: "
        "(1) asiye raia anayefanya shughuli iliyokatazwa: faini isiyopungua TZS 10,000,000 au kifungo kisichozidi miezi 6, pamoja na kufutwa kwa visa na kibali cha ukazi; "
        "(2) raia wa Tanzania anayemsaidia asiye raia kufanya shughuli hiyo: faini ya TZS 5,000,000 au kifungo kisichozidi miezi 3. Pande zote mbili zinaadhibiwa. Amri inataja kiwango cha CHINI cha faini kwa asiye raia tu; haitaji kiwango cha juu. Amri haitumii neno 'nominee' (jina la mkopo): inasema 'kusaidia' (assist or aid) asiye raia. "
        "Thibitisha na mwanasheria aliyesajiliwa au mamlaka husika kabla ya kutenda.",
        "READ FROM THE GAZETTED ORDER ITSELF, edition asserted (assert_edition: 'GN No. 487A, published 28/7/2025', sha256 dd147c0d..., data/source_documents/immigration/gn487a_official_gazette.pdf), not from the practitioner alerts the locked facts name. Order para 3(3)(a): a non-citizen 'shall be liable to a fine of not less "
        "than ten million shillings or imprisonment for a term not exceeding six months and revocation of visa and resident permit'; para 3(3)(b): a citizen who 'assists or aids a non-citizen' 'shall be liable to a fine of five million shillings or imprisonment for a term not exceeding three months'; the Schedule lists 15 activities; the Order states a MINIMUM fine for the non-citizen and NO maximum (added after the sweep showed 'is there a maximum?' questions reaching the route). "
        "WORDING POINT: the Order says fine OR imprisonment (not 'and') with revocation added; CLAUDE.md Section 11 writes 'fine + imprisonment + visa revocation' and the locked fact says 'AND/OR': the statement follows the gazette. 'Nominee' is the question's word, not the Order's. Gate row eval_163. Founder-approved 2026-11-23 on condition the Order confirmed the figures (it does)",
    ),
    VAT_WITHHOLDING_RATES: (
        "vat_withholding_services",
        "VAT ya zuio (Sheria ya Fedha 2025, kuanzia 1 Julai 2025): kwa bidhaa ni asilimia 3 na kwa huduma ni asilimia 6, ya thamani ya mauzo isiyojumuisha VAT. Huduma za IT ni huduma, kwa hiyo kiwango chake ni asilimia 6, si 3. "
        "VAT ya kawaida ni asilimia 18: mnunuzi anayehitimu kuwa wakala wa zuio anazuia asilimia 3 (bidhaa) au 6 (huduma) na kuipeleka TRA moja kwa moja, na muuzaji anapokea iliyobaki (asilimia 15 kwa bidhaa, asilimia 12 kwa huduma). Kwa hiyo VAT ya zuio si VAT yote ya muuzaji. "
        "Muuzaji hupewa cheti cha zuio kama ushahidi wa kiasi kilichopelekwa. Thibitisha na TRA (tra.go.tz).",
        "Locked facts vat_withholding_goods / vat_withholding_services / vat_withholding_buyer_remits_directly (Finance Act 2025 (Act No. 11) s.124 amending VAT Act Cap.148 s.5(5), in force 1 Jul 2025; GN 352K of 30/6/2025 reg 31B; TRA VAT page, June 2026). The rates are unchanged by Finance Act 2026 "
        "(s.91(b) adds only the 3:2 value apportionment for a MIXED supply, its own statement vat_withholding_mixed_supply, vetoed off this route). 'IT services are services' is the founder-approved 4bk wording. Who qualifies as a withholding agent is NOT stated (no fact holds it); the certificate's treatment in the supplier's return is not stated. "
        "Gate rows eval_044, eval_048. Founder-approved 2026-11-23. R44: Acts named, no section number",
    ),
    VAT_PROFESSIONAL_SERVICES: (
        "vat_registration_who_must",
        "Watoa huduma za kitaalamu (wenye leseni au wanachama wa chama cha taaluma) lazima wajisajili VAT bila kujali kiasi cha mauzo yao (Sheria ya VAT): kiwango cha TZS 200M kwa miezi 12 au TZS 100M kwa miezi 6 kinawahusu wafanyabiashara wengine, si wao. "
        "Taasisi za Serikali zinazofanya shughuli za kiuchumi pia zinasajiliwa, na Kamishna anaweza kumsajili anayetarajia kuanza biashara mwenye ushahidi. Sheria inaweka kanuni hii bila kutoa sababu katika maandishi tuliyosoma. "
        "Kama huduma yako ni ya kitaalamu kwa maana ya sheria, thibitisha na TRA (tra.go.tz).",
        "Locked fact vat_registration_who_must (VAT Act Cap.148 R.E.2023 s.29(1)-(3); direct read 2026-11-13; FA2025 s.126 adds only extension-of-time subsections); threshold figures from vat_registration_threshold. The question asks WHY (eval_025): the statement states the rule and says the text gives no reason; "
        "it does not invent one. Founder-approved 2026-11-23. R44: the Act is named, no section number",
    ),
    BRELA_LATE_ANNUAL_RETURN: (
        "company_annual_return_deadline",
        "Annual return ya kampuni inatakiwa ndani ya siku 28 baada ya tarehe ya kumbukumbu (maadhimisho ya kuanzishwa kwa kampuni au ya return iliyotangulia); ukichelewa zaidi, kampuni na kila afisa aliye na hatia wanaweza kutozwa faini, na faini ya ziada kwa kuendelea kuchelewa (Sheria ya Makampuni). "
        "Kwa ratiba ya ada ya BRELA iliyochapishwa kwenye tovuti yao (iliyosomwa 2026-10-06): kuchelewa kuwasilisha waraka kunagharimu TZS 2,500 kwa kila mwezi au sehemu ya mwezi kwa kampuni ya ndani, na ada ya kuwasilisha annual return ni TZS 22,000. "
        "Matokeo mengine ya kutowasilisha kwa miaka mingi hayajathibitishwa hapa: thibitisha na BRELA (brela.go.tz).",
        "Locked facts company_annual_return_deadline (Companies Act Cap.212 R.E.2023, annual-return provisions, edition asserted, read 2026-11-17: 28 days from the return date; the company and every officer in default liable to a fine and, for continued failure, a default fine; the AMOUNT of that fine is not stated by the Act text read) "
        "and late_filing_penalty_monthly_fee (BRELA fee schedule, TZS 2,500 per month or part month, local company, unchanged between the 2026-06-30 and 2026-10-06 captures; filing fee TZS 22,000 item 7). SCOPED TO THE PENALTY: the consequences of two years' default (strike-off, winding-up) are NOT constants and are hedged to BRELA. "
        "Foreign companies (Part XII, TZS 70,000) are vetoed off this route. Gate row eval_085. Founder-approved 2026-11-23 (penalty only). R44: the Act is named, no section number",
    ),
    SDL_PAYE_DEADLINE: (
        "sdl_payment_deadline",
        "SDL na PAYE zote mbili zinatakiwa kufikia tarehe 7 ya mwezi unaofuata mwezi wa mishahara -- tarehe ni ileile. SDL: ritani na malipo yake vyote kufikia tarehe 7 (Sheria ya Elimu na Mafunzo ya Ufundi). "
        "PAYE: mwajiri analipa PAYE aliyokata kwa TRA ndani ya siku 7 baada ya mwisho wa mwezi, yaani ifikapo tarehe 7 (Sheria ya Kodi ya Mapato). Ni wajibu mbili tofauti; njia na fomu ya kulipa thibitisha na TRA (tra.go.tz). "
        "NSSF si tarehe 7: michango ya NSSF ni ndani ya mwezi mmoja baada ya mwisho wa mwezi (Sheria ya NSSF).",
        "Locked facts sdl_payment_deadline (VETA Act Cap.82 R.E.2023 s.16(1)-(2), read 2026-09-02, FA2024/25/26 do not touch s.16) and paye_remittance_deadline (Income Tax Act Cap.332 R.E.2023 s.109(1) read with s.104; direct read 2026-11-13, FA2024/25/26 checked: none changes them); the NSSF line is "
        "nssf_payment_deadline (NSSF Act Cap.50 s.14(1)). Two levies, one question (eval_127): the filing statement vetoes another levy, so this is its own composite. The monthly PAYE statement (s.109(2)) is deliberately not stated: the fact records it as awkwardly worded. Founder-approved 2026-11-23. R44: Acts named, no section number",
    ),
    SDL_AUDIT_HEDGE: (
        "sdl_payer",
        "Sina utaratibu uliothibitishwa wa ukaguzi wa SDL wa TRA (hatua zake, nyaraka zinazoombwa au muda wake), kwa hiyo sitaorodhesha hatua nisizozithibitisha. Ninachoweza kuthibitisha ni kanuni zenyewe: SDL hulipwa na mwajiri pekee, ni asilimia 3.5 ya jumla ya mishahara ghafi ya mwezi kwa mwajiri mwenye wafanyakazi 10 au zaidi, "
        "na ritani na malipo ni kufikia tarehe 7 ya mwezi unaofuata (Sheria ya Elimu na Mafunzo ya Ufundi). Kwa utaratibu wa ukaguzi, au kama umepokea notisi kutoka TRA, wasiliana na TRA (tra.go.tz) au mshauri wa kodi aliyesajiliwa.",
        "A HEDGE, not a constant: no source held states how TRA audits SDL, so none is stated. Founding specimen: build b96e8a8 live, 'How does TRA conduct an SDL audit ...?' invented an eight-point audit asking to see 'P9 forms' (a Kenyan term; CLAUDE.md Section 11 / locked fact paye_p9_deadline). "
        "The three rules stated are the locked facts sdl_payer, sdl_rate (3.5%, FA2023) and sdl_payment_deadline. Founder-approved 2026-11-23 ('hedge to TRA, no invented procedure'). R44: the Act is named, no section number",
    ),
    SDL_BASE: (
        "sdl_base_includes_allowances",
        "Msingi wa SDL ni JUMLA YA MISHAHARA GHAFI YA MWEZI ambayo mwajiri anawalipa wafanyakazi wake (asilimia 3.5 ya jumla hiyo). Jumla hiyo inajumuisha mshahara, malipo ya likizo, malipo ya ugonjwa, malipo badala ya likizo, ada (fee), kamisheni, bonasi, kiinua mgongo (gratuity) "
        "na POSHO ZOTE za safari, malazi, burudani au nyinginezo anazolipa mwajiri kuhusiana na ajira (Sheria ya Elimu na Mafunzo ya Ufundi). Kwa hiyo posho ZIMO kwenye msingi wa SDL. "
        "Sheria haitaji wazi faida zisizo za fedha (kama makazi, chakula au gari): kama zinahesabiwa HAIJATHIBITISHWA hapa, kwa hiyo thibitisha na TRA (tra.go.tz).",
        "Locked fact sdl_base_includes_allowances (VETA Act Cap.82 R.E.2023 s.14(2)-(3), direct read 2026-11-24, edition asserted; s.14 unamended by FA2024/25/26). 'includes' is the Act's word and its list names no benefit in kind, so the statement asserts neither that they count nor that they do not. "
        "The 3.5% is locked fact sdl_rate (corrected 2026-11-24 from 'gross cash emoluments'). Founding specimen: live replies 'gross payroll (cash basis) ... si pamoja na posho za fedha' (build b96e8a8). Founder-approved 2026-11-24. R44: the Act is named, no section number",
    ),
    LEVY_RATES_THREE: (
        "sdl_rate",
        "SDL: asilimia 3.5 ya jumla ya mishahara ghafi ya mwezi, hulipwa na mwajiri pekee (mwajiri mwenye wafanyakazi 10 au zaidi). "
        "NSSF: jumla ni asilimia 20 ya mshahara ghafi (mgao wa kawaida: asilimia 10 mwajiri + asilimia 10 mfanyakazi). "
        "PAYE: HAINA kiwango kimoja -- ni mabano yanayopanda kulingana na mshahara wa mwezi wa mfanyakazi. " + _paye_bands_text() + " Thibitisha na TRA (tra.go.tz) na NSSF (nssf.go.tz).",
        "SDL: locked fact sdl_rate (3.5%, FA2023). NSSF: NSSF_split_triggers (NSSF Act Cap.50 R.E.2023 s.12; 20% = 10% + 10% usual split). PAYE: the band table is GENERATED from rates.PAYE_BANDS (the paye_band_table statement's text), so it cannot drift from the engine. "
        "NO summed 'employer share' percentage is stated: the live reply invented '14% (NSSF 10% + SDL 3.5% + PAYE 0.5%)'; PAYE is the EMPLOYEE's tax and has no employer rate. Founding specimen: build b96e8a8 live, 'SDL, NSSF na PAYE ni asilimia ngapi?' -> 'PAYE ni asilimia 8 (0%-270%: ...) ... 14%'. Founder-approved 2026-11-24. R44: Acts named, no section number",
    ),
    LEVY_DEADLINES_THREE: (
        "sdl_payment_deadline",
        "SDL na PAYE zinatakiwa kufikia tarehe 7 ya mwezi unaofuata mwezi wa mishahara: SDL -- ritani na malipo yake vyote tarehe 7 (Sheria ya Elimu na Mafunzo ya Ufundi); PAYE -- mwajiri analipa PAYE aliyokata kwa TRA ndani ya siku 7 baada ya mwisho wa mwezi (Sheria ya Kodi ya Mapato). "
        "NSSF ni TOFAUTI: michango inatakiwa ndani ya mwezi mmoja baada ya mwisho wa mwezi wa mishahara, si tarehe 7 (Sheria ya NSSF); ukichelewa, adhabu ni asilimia 5 ya kiasi ambacho hakijalipwa kwa kila mwezi au sehemu ya mwezi. Thibitisha na TRA (tra.go.tz) na NSSF (nssf.go.tz).",
        "Locked facts sdl_payment_deadline (VETA Act s.16), paye_remittance_deadline (ITA s.109(1) with s.104) and nssf_payment_deadline (NSSF Act Cap.50 s.14(1) one month; s.14(3) 5% per month or part). The three-levy version of sdl_paye_deadline. Founding specimens: build b96e8a8 live, "
        "'SDL na NSSF na PAYE zinalipwa lini?' -> '... ikijumuisha malipo ya PAYE na michango ya NSSF, ifikapo tarehe 7' (NSSF by the 7th: wrong; D-FIDELITY-29 missed it, now widened). Founder-approved 2026-11-24. R44: Acts named, no section number",
    ),
    VAT_MEDICAL: (
        "medical_services_vat_exempt",
        "Huduma za afya (tiba, meno, uuguzi, ukunga, kupona, urekebishaji, macho au zinazofanana) ni MSAMAHA wa VAT, yaani hazitozwi VAT, zinapotolewa (a) na au ndani ya taasisi iliyoidhinishwa na Serikali kwa huduma hizo, NA (b) na, au chini ya usimamizi na udhibiti wa, mtu aliyesajiliwa kuwa na sifa chini ya sheria za Tanzania (au anayetambuliwa kuwa na sifa) (Sheria ya VAT). "
        "Masharti YOTE MAWILI lazima yatimie: huduma inayotolewa nje ya taasisi iliyoidhinishwa, au bila mtaalamu aliyesajiliwa, haipo kwenye msamaha huu. "
        "Sheria ya usajili wa huduma za kitaalamu haisemi wazi kama mtoa huduma wa afya anayetoa huduma zilizosamehewa tu anatakiwa kujisajili VAT: HAIJATHIBITISHWA hapa, kwa hiyo thibitisha na TRA (tra.go.tz) kabla ya kuamua.",
        "Locked fact medical_services_vat_exempt (VAT Act Cap.148 R.E.2023, Schedule made under s.6(1), Part I, item 'Health care' para 1, read directly 2026-11-24, edition asserted; both limbs joined by 'and'; FA2024/25/26 do not touch the item). The registration limb is a HEDGE by construction: s.29(1) carries no exempt-supply carve-out "
        "in its words while s.28(6)(a) excludes non-taxable supplies from the registration turnover, so the Act text does not say whether an exempt-only practitioner must register. Founding specimen: build 84d8621 live, 'Daktari anayetoa huduma za kitaalamu anatakiwa kusajili VAT?' -> 'Ndiyo ... anatakiwa kusajili VAT'. Founder-approved 2026-11-24. R44: the Act is named, no section or item number",
    ),
    VAT_MEDICINES: (
        "medicines_vat_exempt",
        "Dawa muhimu za binadamu na za mifugo, dawa (drugs), vifaa tiba na vifungashio vyake VILIVYOIDHINISHWA na Waziri husika ni MSAMAHA wa VAT, si zero-rated (Sheria ya VAT). Si kila dawa au kifaa: kinahitaji idhini ya Waziri; vifungashio vinahusika tu vikiwa vimeundwa mahsusi kufungia bidhaa za dawa. Msamaha maana yake VAT haitozwi kwenye mauzo hayo; mkopo wa input VAT unatolewa kwa manunuzi yaliyofanywa kwa ajili ya kutoa bidhaa au huduma zinazotozwa VAT (taxable supplies), na kwa matumizi ya sehemu hugawanywa kwa fomula. Zero-rated (0%) ni aina nyingine, kama mauzo ya nje; bidhaa ikiwa na msamaha na zero-rating kwa pamoja inakuwa zero-rated (kwa mfano dawa zinazouzwa nje ya nchi). Thibitisha na TRA.",
        "Locked fact medicines_vat_exempt (VAT Act Cap.148 R.E.2023, Schedule Part I item 7 'Medicine or pharmaceutical products', s.5(3), s.74(1)-(2); read directly 2026-11-24 with the edition asserted; Finance Acts 2024/25/26 do not name the item). The statement IS the fact text and the D-FIDELITY-32 replacement copy (CONSTANT_RESTATEMENTS['medicines_zero_rated']); a test pins that they are one string. Founding specimen: build 37cdf9d live, 'Dawa zinatozwa VAT?' -> 'zero-rated (tozo 0%)'. Founder-approved 2026-11-24b. R44: the Act is named, no section number.",
    ),
    PAYE_BASE: (
        "paye_base_employment_income",
        "PAYE hukatwa kwenye MAPATO YA AJIRA ya mfanyakazi, si mshahara wa msingi pekee (Sheria ya Kodi ya Mapato). Yanajumuisha mshahara, malipo badala ya likizo, ada, kamisheni, bonasi, kiinua mgongo (gratuity) na posho yoyote ya safari, malazi, burudani au nyingine, pamoja na faida zisizo za fedha (benefits in kind) zilizokokotolewa kisheria. Vichache vimeondolewa kisheria, kwa mfano posho inayorudisha tu gharama zilizotumika kikamilifu kuzalisha mapato, na faida ya matumizi ya gari ambapo mwajiri hadai makato wala nafuu kuhusu umiliki, matengenezo au uendeshaji wa gari hilo; orodha kamili iko kwenye Sheria. Thibitisha na TRA.",
        "Locked fact paye_base_employment_income (Income Tax Act Cap.332 R.E.2023 s.7(2)-(3) and s.104(1); read directly 2026-11-24, edition asserted; unamended by Finance Acts 2024/25/26). When the question ALSO names SDL, fixed_statement() appends the SDL limb (locked fact sdl_base_includes_allowances, VETA Act s.14(3)): allowances are in BOTH bases, benefits in kind are quantified and in PAYE and not named for SDL. Founding specimen: build 37cdf9d live, 'Posho ya nyumba inahesabiwa kwenye SDL, na tofauti yake na PAYE ni ipi?' -> 'PAYE inakokotolewa kwa msingi wa mshahara wa msingi pekee'. Founder-approved 2026-11-24b. R44: Acts named, no section number.",
    ),
}

TOPICS = tuple(STATEMENTS)
TOPICS_NO_CONCISE_ROW = frozenset({WCF_DISEASE, NSSF_SPLIT, PAYE_BANDS_TOPIC, LICENCE_VALIDITY, LICENCE_FEE_VALIDITY, FUTURE_YEAR_RATE, SDL_EXEMPTIONS, SDL_PAYER, SDL_HOW_TO_FILE_PAY, SDL_EMPLOYEE_PREMISE, SDL_NSSF_PARTY,
                                   SDL_NSSF_PAYE_PARTY, NSSF_PARTY, BRELA_THREE_FORMS, BRELA_FEE_NO_SHARE_CAPITAL, GN487A_PENALTIES, VAT_WITHHOLDING_RATES, VAT_PROFESSIONAL_SERVICES, BRELA_LATE_ANNUAL_RETURN, SDL_PAYE_DEADLINE, SDL_AUDIT_HEDGE, SDL_BASE, LEVY_RATES_THREE, LEVY_DEADLINES_THREE, VAT_MEDICAL,
                                   VAT_MEDICINES})   # VAT_MEDICINES: the statement states the 0% of zero-rating, the served row (written for retrieval) does not, so the digit check is skipped; the fact text is pinned to the statement by tests/test_two_statements_2026_11_25.py


# 2026-11-24 (founder, GN 487A premise answers; THIS STATEMENT ONLY): when the question states a figure that CONTRADICTS the Order, the answer opens with an explicit "Hapana" before the correct figures. The Order's figures: a non-citizen -- fine of NOT LESS THAN TZS 10,000,000
# or up to 6 months; a citizen who assists -- fine of TZS 5,000,000 or up to 3 months. NARROW BY CONSTRUCTION (R17): only a figure is judged (never wording), only the amounts and month counts the question states, and an AMBIGUOUS question (the party cannot be told, or a stated figure
# is one the Order contains for the OTHER party only when the party is named) opens with nothing. A question stating no figure, or only correct ones, gets the bare statement.
import re as _re
_G_CITIZEN = _re.compile(r"raia\s+wa\s+tanzania|mtanzania|watanzania|msaidizi|anayemsaidia|anayesaidia|kumsaidia|facilitat|tanzanian|citizen\s+who|helps?\s+a\s+(?:non|foreign)|assists?\s+a\s+(?:non|foreign)", _re.IGNORECASE)
_G_ASSIST = _re.compile(r"anayemsaidia|anayesaidia|kumsaidia|msaidizi|facilitat|helps?\s+a|assists?\s+a|aids?\s+a", _re.IGNORECASE)
_G_NONCITIZEN = _re.compile(r"asiye\s+raia|wasio\s+raia|raia\s+wa\s+kigeni|mgeni|wageni|non-?citizen|foreigner", _re.IGNORECASE)
_G_UPTO = _re.compile(r"hadi|up\s+to|tu(?![a-z])|only|ya\s+juu|maximum", _re.IGNORECASE)


def _g_amounts(text):
    from .. import swahili_numbers as swn
    return list(swn.parse_amounts(text))


def gn487a_premise_opening(question: str) -> str:
    """'Hapana. ' when the question states a figure that contradicts the Order (party-aware, figures only); '' otherwise. Pure."""
    q = question or ""
    cit, non = bool(_G_CITIZEN.search(q)), bool(_G_NONCITIZEN.search(q))
    amounts = [a for a in _g_amounts(q) if a >= 100_000]
    months = [int(m) for m in _re.findall(r"(\d+)\s*(?:months?|miezi)", q, _re.IGNORECASE)] + [12 * int(m) for m in _re.findall(r"(\d+)\s*(?:years?|miaka|mwaka)", q, _re.IGNORECASE)]
    if not amounts and not months:
        return ""
    ok_amounts, ok_months = set(), set()
    wrong = False
    # an ASSIST cue makes the CITIZEN the subject of the penalty even when a foreigner is named (as the OBJECT of the assisting)
    assist = bool(_G_ASSIST.search(q))
    if (cit and not non) or assist:
        ok_amounts, ok_months = {5_000_000}, {3}
        wrong = any(a not in ok_amounts for a in amounts) or any(m not in ok_months for m in months)
    elif non and not cit:
        wrong = any(a < 10_000_000 for a in amounts) or any(m != 6 for m in months) or (any(a == 10_000_000 for a in amounts) and bool(_G_UPTO.search(q)))
    else:
        # both parties or neither named: a figure that is correct for NEITHER party is wrong whoever it is for
        wrong = any(a not in {5_000_000} and a < 10_000_000 for a in amounts) or any(m not in {3, 6} for m in months)
    return "Hapana -- kiwango ulichotaja hakipo kwenye Amri. " if wrong else ""


def fixed_statement(topic, question=None) -> ComputationResult:
    """The whole statement for `topic`. An unknown topic raises: a statement route with no statement must never fall back to
    generation or to a guess (R31: a branch with no extractor is a capability that does not exist). `question` is used by ONE topic only
    (gn487a_penalties, see gn487a_premise_opening)."""
    if topic not in STATEMENTS:
        raise KeyError(f"no fixed statement for topic {topic!r}")
    key, text, note = STATEMENTS[topic]
    if topic == GN487A_PENALTIES and question:
        text = gn487a_premise_opening(question) + text
    if topic == PAYE_BASE and question and _re.search(r"(?<![a-z])sdl(?![a-z])|tozo\s+la\s+mafunzo|skills\s+development\s+levy", question, _re.IGNORECASE):
        text += (" Kwa SDL: msingi ni jumla ya mishahara ghafi ya mwezi, na posho zote zimo (Sheria ya Elimu na Mafunzo ya Ufundi); faida zisizo za fedha hazijatajwa kwenye Sheria. "
                 "Kwa hiyo posho zinaingia kwenye PAYE na kwenye SDL; tofauti iko kwenye faida zisizo za fedha: PAYE inazihesabu (zilizokokotolewa kisheria), SDL Sheria haizitaji.")
    return ComputationResult(
        computation="fixed_statement",
        applicable=True,
        amount=None,                      # R19: a constant, never a derived amount.
        working=text,
        inputs={"topic": topic, "fact": key},
        note=note,
    )
