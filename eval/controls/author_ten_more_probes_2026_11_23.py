# -*- coding: utf-8 -*-
"""Authors eval/refusal_gate/ten_more_statements_probes_2026_11_23.jsonl (R17: probes BOTH WAYS; R21: authored by the person who wrote the routes, so a LOWER bound).
`expect` is the topic the question must route to, or "none" = it must reach NO statement route (it goes to its own engine / the model). Gate rows and live specimens are VERBATIM and marked.
    python eval/controls/author_ten_more_probes_2026_11_23.py"""
import io, json, os
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(REPO, "eval", "refusal_gate", "ten_more_statements_probes_2026_11_23.jsonl")

P = []
def add(pid, q, expect, why):
    P.append({"id": pid, "question": q, "expect": expect, "guards_against": why})

# ---- #8 SDL + NSSF + PAYE party composite
T = "sdl_nssf_paye_party"
add("tp_01", "SDL, NSSF na PAYE zinakatwa kwa mfanyakazi?", T, "FOUNDING SPECIMEN (live, b96e8a8): 'Hapana ... MWAJIRI pekee', wrong for NSSF and PAYE.")
add("tp_02", "Nani analipa SDL, NSSF na PAYE?", T, "who-pays form, three levies.")
add("tp_03", "Mfanyakazi anakatwa PAYE, NSSF na SDL kwenye mshahara wake?", T, "employee-deduction form, three levies in another order.")
add("tp_04", "Is SDL, NSSF and PAYE deducted from the employee?", T, "English form.")
add("tp_05", "SDL na NSSF zinakatwa kwa mfanyakazi?", "sdl_nssf_party", "the TWO-levy question must stay on the older route (the composite needs PAYE).")
add("tp_06", "SDL, NSSF na PAYE ni asilimia ngapi?", "levy_rates_three", "EXPECT INVERTED 2026-11-24 (was none: a RATE question about three levies is not a party question.). Now owned by the three-levy RATE statement (founder-approved 2026-11-24).")
add("tp_07", "SDL, NSSF na PAYE zinakatwa kwa mfanyakazi mwenye mshahara wa 800000?", "none", "a figure: the engine / model path, never a party statement.")
add("tp_08", "SDL, NSSF, PAYE na WCF zinakatwa kwa mfanyakazi?", "none", "a FOURTH levy named: the composite does not cover WCF.")
add("tp_09", "SDL, NSSF na PAYE zinalipwa lini?", "levy_deadlines_three", "EXPECT INVERTED 2026-11-24 (was none: a deadline question, not a party question (the PAYE+SDL deadline route needs no NSSF).). Now owned by the three-levy DEADLINE statement (founder-approved 2026-11-24).")
add("tp_10", "SDL, NSSF na PAYE zinalipwa wapi?", "none", "where to pay: model.")

# ---- B1 NSSF party
T = "nssf_party"
add("np_01", "NSSF inakatwa kwa mfanyakazi?", T, "FOUNDING SPECIMEN (live, b96e8a8): 'Ndiyo ... 10% sawa na 20%' (garbled).")
add("np_02", "Nani analipa NSSF?", T, "who-pays form.")
add("np_03", "Mfanyakazi anakatwa NSSF kwenye mshahara wake?", T, "employee deduction form.")
add("np_04", "Is NSSF deducted from the employee?", T, "English form.")
add("np_05", "NSSF inalipwa na mwajiri au mfanyakazi?", T, "either-or payer form.")
add("np_06", "Mgawanyo wa NSSF kati ya mwajiri na mfanyakazi unaweza kubadilishwa?", "nssf_split", "the split-route question stays on the split route.")
add("np_07", "NSSF inakatwa kiasi gani kwa mshahara wa 600000?", "none", "an amount: the engine.")
add("np_08", "NSSF inakatwa asilimia ngapi?", "none", "a rate question.")
add("np_09", "Pensheni ya NSSF inakatwa kodi?", "none", "pension tax: not the party question.")
add("np_10", "NSSF na PAYE zinakatwa kwa mfanyakazi?", "none", "another levy named: the NSSF route declines.")
add("np_11", "Nani analipa NSSF ya hiari?", "none", "voluntary membership is a different question.")
add("np_12", "Mfanyakazi akiacha kazi, NSSF yake inakatwa tena?", "none", "premise about leaving, a different question; flows to the model.")

# ---- #1 BRELA three forms
T = "brela_three_forms"
add("bf_01", "BRELA inasajilisha aina kuu ngapi za miundo ya biashara Tanzania?", T, "GATE ROW eval_071, verbatim.")
add("bf_02", "Payroll yetu ni TZS 7,000,000 kwa mwezi, sasa je tunatakiwa kujisajili BRELA?", T, "GATE ROW eval_301, verbatim (a figure: digits are allowed on this route).")
add("bf_03", "Nina wafanyakazi 20 na mtaji wa TZS 50,000,000, je nasajili kampuni au jina la biashara BRELA?", T, "GATE ROW eval_304, verbatim.")
add("bf_04", "Je, kampuni au jina la biashara linafaa kwa ubia wa watu wawili?", T, "company-or-business-name choice.")
add("bf_05", "How many types of business structure does BRELA register?", T, "English form.")
add("bf_06", "Ada ya kusajili jina la biashara BRELA ni shilingi ngapi?", "none", "a FEE question.")
add("bf_07", "Naombaje kusajili kampuni BRELA mtandaoni?", "none", "how-to.")
add("bf_08", "BRELA wanasajili alama ya biashara (trademark) vipi?", "none", "trademarks are IP, not a business form.")
add("bf_09", "Annual return ya kampuni inatakiwa lini BRELA?", "brela_annual_return_deadline", "a deadline question: it must reach the annual-return DEADLINE route and not the forms route (first draft wrote none: a wrong expectation, the older route existed).")
add("bf_10", "Je, BRELA inanitoza kodi nikiwa na wafanyakazi 20?", "none", "a tax word: vetoed.")
add("bf_11", "Ada ya kusajili kampuni isiyo na mtaji wa hisa BRELA ni TZS ngapi?", "brela_fee_no_share_capital", "must reach the fee route, not the forms route.")

# ---- #2 no-share-capital fee
T = "brela_fee_no_share_capital"
add("fc_01", "Ada ya kusajili kampuni isiyo na mtaji wa hisa (no share capital) BRELA ni TZS ngapi?", T, "GATE ROW eval_383, verbatim.")
add("fc_02", "How much does it cost to register a company without share capital?", T, "English form.")
add("fc_03", "Kampuni isiyo na mtaji wa hisa inagharimu kiasi gani kusajili?", T, "natural phrasing.")
add("fc_04", "Ada ya kampuni isiyo na mtaji wa hisa ni TZS 300,000, sivyo?", T, "a premise with the SUPERSEDED figure: the statement must state both dates, so it is routed.")
add("fc_05", "Ada ya kusajili kampuni yenye mtaji wa hisa wa TZS 50,000,000 ni ngapi?", "none", "a company WITH share capital: the engine / model, not this fee.")
add("fc_06", "Ada ya kuhifadhi jina la kampuni isiyo na mtaji wa hisa ni ngapi?", "none", "name reservation fee, a different fee.")
add("fc_07", "Kampuni isiyo na mtaji wa hisa ikichelewa kuwasilisha annual return adhabu ni ngapi?", "brela_late_annual_return", "a penalty, not the registration fee: it must NOT reach the fee route; the late-return statement is correct for any local company (first draft wrote none: a wrong expectation).")
add("fc_08", "Kampuni ya kigeni isiyo na mtaji wa hisa ada ni ngapi?", "none", "foreign company.")

# ---- #3 GN 487A penalties
T = "gn487a_penalties"
add("gn_01", "GN 487A inasema nini kuhusu mpango wa 'jina la mkopo' (nominee) — kwanini unazuiwa?", T, "GATE ROW eval_163, verbatim.")
add("gn_02", "Adhabu ya GN 487A kwa raia wa Tanzania anayemsaidia mgeni kufanya biashara ni nini?", T, "citizen facilitator penalty.")
add("gn_03", "Mgeni akifanya biashara iliyokatazwa na GN 487A, faini ni kiasi gani?", T, "non-citizen penalty.")
add("gn_04", "What is the penalty under GN 487A for a non-citizen?", T, "English form.")
add("gn_05", "Raia wa kigeni akikutwa anaendesha saluni, adhabu ni nini?", T, "non-citizen cue without the GN number.")
add("gn_06", "GN 487A inakataza shughuli zipi?", "none", "the LIST of activities, not the penalties.")
add("gn_07", "GN 487A ilianza kutumika lini?", "none", "a date question.")
add("gn_08", "Raia wa kigeni anahitaji kibali gani kufanya kazi Tanzania?", "none", "work permit: not the penalty.")
add("gn_09", "Nimeajiri raia wa kigeni, GN 487A inaniathiri vipi?", "none", "employing a foreigner: not the penalty statement.")
add("gn_10", "Mgeni mwenye leseni halali kabla ya GN 487A anaendelea hadi lini?", "none", "the transition rule.")

# ---- #5 VAT withholding rates
T = "vat_withholding_rates"
add("vw_01", "Je, kiwango cha asilimia 3 cha VAT withholding kinatumika pia kwa ununuzi wa huduma za IT kutoka kwa msambazaji aliyesajiliwa VAT?", T, "GATE ROW eval_044, verbatim.")
add("vw_02", "Maana ya 'VAT withholding si VAT yote' kwa msambazaji ni nini?", T, "GATE ROW eval_048, verbatim.")
add("vw_03", "VAT ya zuio ni asilimia ngapi kwa bidhaa na kwa huduma?", T, "rate, both limbs.")
add("vw_04", "What is the VAT withholding rate on services?", T, "English form.")
add("vw_05", "VAT withholding kwa mauzo ya bidhaa na huduma pamoja inakatwaje?", "vat_withholding_mixed_supply", "the MIXED-supply question stays on its own route.")
add("vw_06", "VAT withholding certificate inatolewa lini?", "none", "the certificate-timing question.")
add("vw_07", "Nani ni wakala wa VAT withholding?", "none", "who is the agent: no fact holds it.")
add("vw_08", "VAT withholding kwenye ankara ya TZS 5,000,000 ni kiasi gani?", "none", "an amount: the engine.")
add("vw_09", "VAT withholding ilianza lini?", "none", "start date: D-FIDELITY-22's constant, not this statement.")
add("vw_10", "VAT withholding na PAYE zinawasilishwa wapi?", "none", "another tax named.")

# ---- #4 professional services
T = "vat_professional_services"
add("vp_01", "Kwa nini fani kama wakili na wahandisi zinahitajika kusajilisha VAT bila kujali mauzo yao?", T, "GATE ROW eval_025, verbatim.")
add("vp_02", "Mhasibu lazima ajisajili VAT hata kama mauzo yake ni madogo?", T, "profession + registration + regardless.")
add("vp_03", "Do lawyers have to register for VAT regardless of turnover?", T, "English form.")
add("vp_04", "Mhandisi anayetoa huduma za kitaalamu anatakiwa kusajili VAT?", T, "engineer, professional service.")
add("vp_10", "Daktari anayetoa huduma za kitaalamu anatakiwa kusajili VAT?", "vat_medical_services", "EXPECT INVERTED 2026-11-24 (was none: A DOCTOR must NOT get the professional-services statement: medical services are an exempt supply (found by reading the sweep; the first draft of this probe expected the statement, which would have been a confident error).). A DOCTOR must still NOT get the professional-services statement; the medical-services statement (exempt on two conditions, registration hedged) is now the intended owner.")
add("vp_11", "Wakili mpya aliyeidhinishwa leo — anaweza kuanza kufanya kazi bila kusajili VAT kwanza?", "none", "a timing / start-practising question the statement does not answer.")
add("vp_05", "Wakili mwenye mauzo ya TZS 30,000,000 anatakiwa kusajili VAT?", "none", "a figure: the registration engine.")
add("vp_06", "Naweza kusajili VAT kwa hiari kama mhasibu?", "vat_voluntary_registration", "voluntary registration: the OLDER voluntary route owns it, not the professional-services statement (first draft wrote none: a wrong expectation).")
add("vp_07", "Wakili akichelewa kusajili VAT adhabu ni nini?", "none", "a penalty.")
add("vp_08", "Wahandisi wanasajili vipi VAT mtandaoni?", "none", "how-to.")
add("vp_09", "Kizingiti cha kusajili VAT ni kiasi gani?", "none", "no profession word: the threshold fact path.")

# ---- #6 late annual return
T = "brela_late_annual_return"
add("lr_01", "Kampuni ilishindwa kuwasilisha annual return kwa miaka 2 — matokeo yanayoweza kutokea ni yapi?", T, "GATE ROW eval_085, verbatim.")
add("lr_02", "Annual return ya kampuni yangu imechelewa, adhabu ni nini?", T, "natural phrasing, penalty.")
add("lr_03", "Late annual return penalty BRELA is how much?", T, "English form.")
add("lr_04", "Nikichelewa kuwasilisha annual return BRELA nalipa faini ngapi?", T, "penalty amount ask.")
add("lr_05", "Annual return ya kampuni inatakiwa kuwasilishwa lini BRELA?", "brela_annual_return_deadline", "the DEADLINE question stays on the deadline route (mutual exclusion).")
add("lr_06", "Kampuni ya kigeni ikichelewa annual return adhabu ni nini?", "none", "foreign company: Part XII, a different fee.")
add("lr_07", "Annual return ikichelewa kwa miaka 2, kampuni inafutwa kwenye daftari?", "none", "strike-off is NOT a constant here: model.")
add("lr_08", "Annual return ya kampuni inawasilishwaje mtandaoni?", "none", "how-to.")
add("lr_09", "Wakurugenzi wanafungwa jela kwa kuchelewesha annual return?", "none", "officers' imprisonment: not stated here.")

# ---- #7 SDL and PAYE both by the 7th
T = "sdl_paye_deadline"
add("sp_01", "Je, SDL na PAYE zinalipwa TRA kwa wakati mmoja — siku ya 7 ya mwezi unaofuata?", T, "GATE ROW eval_127, verbatim (carries a '7').")
add("sp_02", "SDL na PAYE zinalipwa lini?", T, "plain deadline form.")
add("sp_03", "SDL and PAYE are due on what date?", T, "English form.")
add("sp_04", "Tarehe ya mwisho ya SDL na PAYE ni ipi?", T, "last-date form.")
add("sp_05", "SDL na NSSF na PAYE zinalipwa lini?", "levy_deadlines_three", "EXPECT INVERTED 2026-11-24 (was none: NSSF is a THIRD levy with a different deadline: the composite declines.). Now owned by the three-levy DEADLINE statement: NSSF is told one month, SDL and PAYE the 7th.")
add("sp_06", "SDL na PAYE zinalipwa wapi?", "none", "where to pay: model.")
add("sp_07", "SDL na PAYE nikichelewa adhabu ni nini?", "none", "a penalty.")
add("sp_08", "SDL inalipwa lini?", "none", "SDL ALONE with a time word: it must NOT reach the SDL+PAYE composite (no PAYE named); it reaches no statement route and that is the contract (first draft wrote sdl_payer by mistake).")
add("sp_09", "SDL na PAYE kwa mshahara wa 1,500,000 zinalipwa lini?", "none", "a figure: the engine.")

# ---- B4 SDL audit hedge
T = "sdl_audit_hedge"
add("au_01", "How does TRA conduct an SDL audit and what do they examine?", T, "FOUNDING SPECIMEN (live, b96e8a8): an invented eight-point audit asking for 'P9 forms'.")
add("au_02", "TRA hukagua SDL vipi?", T, "Swahili form.")
add("au_03", "Ukaguzi wa SDL unafanyikaje?", T, "Swahili form 2.")
add("au_04", "Nitajiandaaje kwa SDL audit ya TRA?", T, "preparation form.")
add("au_05", "Ukaguzi wa SDL kwa mwajiri mwenye wafanyakazi 15 na mshahara wa 6,000,000 unafanyikaje?", "none", "digits: the engine / model.")
add("au_06", "Ukaguzi wa PAYE unafanyikaje?", "none", "another levy's audit: no route.")
add("au_07", "How does an employer calculate the SDL amount payable each month?", "sdl_base", "EXPECT INVERTED 2026-11-24 (was none: calculation, not audit.). Now owned by the SDL BASE statement (the calculation ask is answered with the base and the 3.5%).")
add("au_08", "Pesa za SDL zinakwenda wapi?", "none", "where the money goes, not audit.")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    for r in P:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")
print(len(P), "probes ->", OUT)
