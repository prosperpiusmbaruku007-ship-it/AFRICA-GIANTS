# -*- coding: utf-8 -*-
"""Builds eval/fidelity/d17_batch_probes_2026_11_17.jsonl (R17: founding specimens VERBATIM from the live check of build a2e6611; the clean half is the founder's list plus REAL PARTICIPANT PHRASINGS, not only ours -- R33).
    python eval/fidelity/make_d17_probes_2026_11_17.py"""
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
P = []


def add(i, g, q, b, e, why, **kw):
    P.append(dict(id=i, guard=g, question=q, body=b, expect=e, guards_against=why, **kw))


# ---- 1. UNSUPPORTED PERSONAL NAMES (expect strip | clean) -------------------------------------------------------------------------------------------------------------------------------
LIVE_GN = "GN 605A ilitolewa na Waziri wa Kazi, Mawasiliano na Uchukuzi (MHE. George Simbachawene) kwa Tangazo Rasmi la Serikali Na. 605A, tarehe 13 Oktoba 2025. Ilianza kutumika tarehe 1 Januari 2026. Thibitisha na TanzLII.org."
add("d17_nm_01", "names", "GN 605A ilitolewa na nani?", LIVE_GN, "strip", "live, VERBATIM: a minister, a ministry and a person the served row never names")
add("d17_nm_02", "names", "Nani anasimamia serikali?", "Waziri Mkuu Kassim Majaliwa ndiye msimamizi mkuu wa shughuli za Serikali.", "strip", "a name after an office-only title")
add("d17_nm_03", "names", "Nani anakusanya kodi?", "Kodi hukusanywa na Mr. John Smith wa TRA.", "strip", "an English honorific")
add("d17_nm_04", "names", "Nani anasimamia kodi?", "Kamishna Mkuu wa TRA Alphayo Kidata anasimamia ukusanyaji wa kodi.", "strip", "office with 'wa TRA' followed by a name")
add("d17_nm_05", "names", "Nani ni Katibu Mkuu?", "Katibu Mkuu (Juma Hamisi Mwinyi) alitia saini.", "strip", "a name in a parenthesis directly after an office title")
add("d17_nm_06", "names", "Nani alisema hivyo?", "Dkt. Asha Rose Migiro alisema hivyo.", "strip", "an academic honorific + three-part name")
add("d17_nm_07", "names", "Mshahara wa mfanyakazi wa umma ni kiasi gani?", "Rais Samia Suluhu Hassan alitangaza TZS 500,000 kwa mwezi.", "strip", "a President named when no served fact in THIS context names one")
add("d17_nm_10", "names", "Nani anasimamia kodi?", "Kamishna Mkuu wa TRA anasimamia ukusanyaji wa kodi.", "clean", "MUST PASS (founder): an office by title, 'Kamishna Mkuu wa TRA'")
add("d17_nm_11", "names", "Nani anasajili kampuni?", "Wakala wa Usajili wa Biashara na Leseni (BRELA) na Mamlaka ya Mapato Tanzania (TRA) wanahusika.", "clean", "MUST PASS (founder): institutions")
add("d17_nm_12", "names", "Sheria gani inatumika?", "Sheria ya Kodi ya Mapato na Sheria ya Fedha 2025 Kifungu 60 zinatumika.", "clean", "MUST PASS (founder): Acts")
add("d17_nm_13", "names", "Nani anatangaza bajeti?", "Waziri wa Fedha na Mipango anatangaza bajeti kila mwaka.", "clean", "an office with its portfolio")
add("d17_nm_14", "names", "Mheshimiwa Mwigulu Nchemba alisema nini kuhusu kodi?", "Mheshimiwa Mwigulu Nchemba alisema hivyo.", "clean", "a name the ASKER typed is kept")
add("d17_nm_15", "names", "Nani aliitoa?", "Aliitoa Waziri Kassim Majaliwa.", "clean", "a name a SERVED fact carries is kept", supported="Waziri Mkuu Kassim Majaliwa alisaini amri hiyo.")
add("d17_nm_16", "names", "Biashara ya mpakani iko wapi?", "Biashara ya mpakani Tunduma, Dar es Salaam, Dodoma na Arusha inahusika.", "clean", "place names")
add("d17_nm_17", "names", "Fidia inalipwa wapi?", "Mfuko wa Fidia kwa Wafanyakazi (WCF) na Ofisi ya Rais zinahusika; Benki Kuu ya Tanzania pia.", "clean", "funds, offices of state, central bank")
add("d17_nm_18", "names", "Nani anaitoa?", "Rais wa Jamhuri ya Muungano wa Tanzania hutoa tamko.", "clean", "'Rais wa Jamhuri' is an office, not a person")
add("d17_nm_19", "names", "GN 605A ilitolewa na nani?", "GN 605A ilitolewa na Waziri wa Nchi, Ofisi ya Waziri Mkuu (Kazi, Vijana, Ajira na Watu Wenye Ulemavu) chini ya Sheria ya Taasisi za Kazi.", "clean", "the SERVED office string itself must pass untouched (idempotence)")
add("d17_nm_21", "names", "Nani anasimamia WCF?", "Kifungu cha sheria kinahusu majukumu ya Mkurugenzi Mtendaji Mkuu wa WCF kuhusu taarifa za mishahara.", "clean", "PRICED FALSE POSITIVE (a training pair): an office title with Mtendaji/Mkuu is not a person")
add("d17_nm_22", "names", "Nani anakagua hesabu?", "Mkaguzi Mkuu wa Hesabu za Serikali na Katibu Mkuu Kiongozi wanahusika.", "clean", "office titles with Mkuu / Kiongozi")
add("d17_nm_20", "names", "Soko la hisa liko wapi?", "Soko la Hisa la Dar es Salaam na Afrika Mashariki.", "clean", "exchange and region names")

# ---- 2. LICENCE VALIDITY PERIOD (expect flag | clean) ---------------------------------------------------------------------------------------------------------------------------------
LQ = "Leseni ya biashara ya LGA inahuishwa lini?"
add("d17_pd_01", "period", LQ, "Leseni ya biashara ya LGA huisha mwaka wake ndani ya siku 90 tangu tarehe ya kuomba upya. Thibitisha na LGA (lga.go.tz).", "flag", "live, VERBATIM: siku 90")
add("d17_pd_02", "period", "Leseni ya biashara inaisha lini?", "Leseni ya biashara huisha baada ya miezi 6.", "flag", "a six-month validity")
add("d17_pd_03", "period", "Leseni ya duka langu ni halali kwa muda gani?", "Leseni ni halali kwa siku 30 tu.", "flag", "a thirty-day validity")
add("d17_pd_04", "period", "Leseni ya biashara inaisha lini?", "Leseni ya biashara ni halali kwa miezi 12 tangu tarehe ilipotolewa.", "clean", "the correct statement")
add("d17_pd_05", "period", "Leseni ya biashara inaisha lini?", "Leseni ya biashara ni halali kwa mwaka mmoja.", "clean", "the correct period in words")
add("d17_pd_06", "period", "Leseni ya biashara ni halali kwa muda gani?", "Unaweza kulipia ada ya hadi miaka 3 mfululizo; leseni ni halali kwa miezi 12.", "clean", "the three-year prepayment option")
add("d17_pd_07", "period", LQ, "Ukichelewa kuhuisha leseni, adhabu inaanza baada ya siku 30.", "clean", "a late-renewal PENALTY period is a different question")
add("d17_pd_08", "period", LQ, "Kupata leseni mpya kunachukua siku 7 baada ya maombi kukamilika.", "clean", "an application-processing period")
add("d17_pd_09", "period", "Leseni yangu ya biashara ni halali kwa miezi 6, sivyo?", "Hapana, si miezi 6; ni miezi 12 tangu ilipotolewa.", "clean", "the asker's own figure named under negation")
add("d17_pd_10", "period", "Leseni ya biashara inaisha lini?", "Leseni ya biashara ni halali kwa miezi kumi na mbili.", "clean", "twelve in words")

# ---- 3. LICENCE-AUTHORITY CUE IN REAL PARTICIPANT PHRASINGS (expect repair | clean) ------------------------------------------------------------------------------------------------
BR = "Thibitisha na BRELA (brela.go.tz)."
for i, q in enumerate(["Leseni yangu ya biashara haiishi kila mwaka, inadumu mpaka niifute, sivyo?", "Leseni ya duka langu inaisha lini?", "Naomba kuhuisha leseni ya biashara yetu, nifanyeje?", "Leseni ya mgahawa wangu iko wapi?",
                       "Business license yangu ya duka ilipotea, nifanyeje?", "Licence ya biashara naipata wapi?", "leseni yako ya biashara ina muda gani?", "Leseni za maduka zinatolewa wapi?"], 1):
    add(f"d17_cue_{i:02d}", "licauth", q, "Omba kupitia mfumo wa leseni. " + BR, "repair", "REAL participant phrasing of a business-licence question: a lone BRELA citation must be expanded")
add("d17_cue_09", "licauth", "Leseni ya biashara inaisha lini?", "Ni mwaka. Thibitisha na LGA (lga.go.tz).", "repair", "lga.go.tz has NO DNS record (NXDOMAIN, 2026-11-17): a licence citation to it is replaced")
add("d17_cue_10", "licauth", "Leseni ya biashara inaisha lini?", "Ni mwaka. Thibitisha na MLYWF (mlywf.go.tz).", "repair", "mlywf.go.tz has NO DNS record either")
add("d17_cue_14", "licauth", "Leseni yangu ya biashara nikiipoteza nifanyeje?", "Kupoteza leseni ni tatizo. Thibitisha na halmashauri husika (lga.go.tz).", "repair", "LIVE (build 36a5144), VERBATIM: the body already says halmashauri but cites the host with NO DNS record")
add("d17_cue_15", "licauth", "Leseni yangu ya biashara nikiipoteza nifanyeje?", "Thibitisha na halmashauri husika (LGA).", "clean", "a council citation with no dead host is left alone")
add("d17_cue_16", "licauth", "Nahitaji leseni ya biashara, inagharimu kiasi gani na inaisha lini?", "Ada hutofautiana kulingana na eneo. Thibitisha na halmashauri husika (lga.go.tz).", "repair", "LIVE (build 36a5144): the fee + expiry two-part question on the MODEL path")
add("d17_nm_08", "names", "Nani alisaini GN 605A?", "GN 605A ilisainiwa na Waziri wa Kazi, Mhe. George Simbachawene. Hakuna taarifa kuwa PKF ilisaini.", "strip", "LIVE (build 36a5144), shape: a name introduced by a comma at the end of a clause")
add("d17_nm_09", "names", "Nani alitangaza kima cha chini?", "Kilitangazwa na Waziri wa Kazi, MHE. George Simbachawene, katika Gazeti Rasmi tarehe 13 Oktoba 2025.", "strip", "LIVE (build 36a5144), shape: a name between two commas")
add("d17_cue_11", "licauth", "Leseni ya udereva inaisha lini?", BR, "clean", "a DRIVING licence is not a business licence")
add("d17_cue_12", "licauth", "Leseni ya madini inatolewa wapi?", BR, "clean", "a mining licence is not a business licence")
add("d17_cue_13", "licauth", "Nataka kusajili kampuni, nifanyeje?", BR, "clean", "a company-registration question")

# ---- 4. TAX WINS OVER LABOUR ON A TAX-ASK; labour wins on a labour ask (expect topic | repaired | unchanged) --------------------------------------------------------------------------------
add("d17_tx_01", "authtopic", "Nikiachishwa kazi nitakatwa kodi gani kwenye malipo ya severance?", "", "tax", "live: severance + 'kodi gani' is a TAX question")
add("d17_tx_02", "authtopic", "Severance inakatwa PAYE?", "", "tax", "severance + PAYE")
add("d17_tx_03", "authtopic", "Severance ni siku ngapi?", "", "labour", "the mirror: a LABOUR ask stays labour")
add("d17_tx_04", "authtopic", "Notisi ya kuacha kazi ni siku ngapi?", "", "labour", "notice is labour")
add("d17_tx_05", "authtopic", "Severance na NSSF zinakatwa kodi gani?", "", "none", "a THIRD topic present: not judged")
add("d17_tx_06", "authrepair", "Nikiachishwa kazi nitakatwa kodi gani kwenye malipo ya severance?", "Malipo yanaweza kuwa sehemu ya mapato ya ajira. Thibitisha na Ofisi ya Kazi (kazi.go.tz).", "repaired", "live: the labour host on a tax question is rewritten to TRA")
add("d17_tx_07", "authrepair", "Nikiachishwa kazi nitakatwa kodi gani kwenye malipo ya severance?", "Malipo yanaweza kuwa sehemu ya mapato ya ajira. Thibitisha na TRA (tra.go.tz).", "unchanged", "the correct TRA citation on a tax question is left alone")
add("d17_tx_08", "authrepair", "Severance ni siku ngapi?", "Siku 7 kwa kila mwaka. Thibitisha na TRA (tra.go.tz).", "repaired", "a tax host on a LABOUR question is rewritten to the labour office")
add("d17_tx_09", "authrepair", "Severance ni siku ngapi?", "Siku 7 kwa kila mwaka. Thibitisha na Ofisi ya Kazi (kazi.go.tz).", "unchanged", "the correct labour citation is left alone")

# ---- 5. GN 605A ISSUER BY OFFICE (expect repair | clean) --------------------------------------------------------------------------------------------------------------------------------
add("d17_gn_01", "gn605a", "GN 605A ilitolewa na nani?", "GN 605A ilitolewa na Waziri wa Kazi, Mawasiliano na Uchukuzi kwa Tangazo Rasmi la Serikali.", "repair", "an issuer verb + a Waziri whose office the Order does not carry")
add("d17_gn_02", "gn605a", "GN 605A ilitolewa na nani?", "GN 605A iliyotolewa na Waziri wa Nchi, Ofisi ya Waziri Mkuu (Kazi, Vijana, Ajira na Watu Wenye Ulemavu) chini ya Sheria ya Taasisi za Kazi.", "clean", "the served office is not rewritten again")
add("d17_gn_04", "gn605a", "GN 605A ilitolewa na nani?", "GN 605A iliyotolewa na Waziri anayehusika na masuala ya kazi (Waziri wa Nchi, Ofisi ya Waziri Mkuu: Kazi, Vijana, Ajira na Watu Wenye Ulemavu) chini ya Sheria ya Taasisi za Kazi.", "clean", "the served ROW's own phrasing (a model that echoes it) is not rewritten into a duplicate")
add("d17_gn_03", "gn605a", "Waziri wa Fedha anasimamia nini?", "Waziri wa Fedha amesaini Amri ya kodi.", "clean", "a Waziri sentence that is not about GN 605A and has no issuer verb")

# ---- 6. THE TWO STATEMENT ROUTES: diverting AND clean (expect route | none) -------------------------------------------------------------------------------------------------------------
for i, (q, w, why) in enumerate([
    ("Return ya kodi ya mapato ya mtu binafsi ni lini?", "individual_income_tax_return", "live specimen: answered with a tax RATE"),
    ("Mwisho wa kuwasilisha return ya kodi ya mapato kwa mtu binafsi ni lini?", "individual_income_tax_return", "the committed regen guard's wording"),
    ("Je, mtu binafsi mwenye biashara anatakiwa kuwasilisha return ya kodi ya mapato lini?", "individual_income_tax_return", "a participant phrasing"),
    ("Nina biashara binafsi na mwaka wangu wa hesabu umeishia tarehe 31 Desemba. Kwa hiyo return ya income tax sihitaji kusubiri miezi 12 mingine, naweza kuwasilisha ndani ya miezi 6, sivyo?", "individual_income_tax_return", "s2_16, a premise phrasing"),
    ("Duka langu ni la mtu binafsi, return ya income tax ni mwezi gani?", "individual_income_tax_return", "a participant phrasing, 'mwezi gani'"),
    ("Leseni ya biashara inaisha lini?", "business_licence_validity", "plain"),
    ("Leseni yangu ya biashara haiishi kila mwaka, inadumu mpaka niifute, sivyo?", "business_licence_validity", "np_13, a premise phrasing"),
    ("Leseni ya biashara yangu niliyoipata mwaka huu bado ni ileile. Si lazima niifanyie upya kabla ya tarehe 30 Juni, ndiyo?", "business_licence_validity", "s2_07, a premise phrasing"),
    ("Leseni ya biashara ya LGA inahuishwa lini?", "business_licence_validity", "live specimen: answered 'siku 90'"),
    ("Leseni ya duka langu inaisha mwezi gani?", "business_licence_validity", "a participant phrasing"),
    ("Leseni ya mgahawa wangu huisha lini?", "business_licence_validity", "a participant trade"),
    ("Leseni ya biashara ni ya mwaka mmoja au miaka mitatu?", "business_licence_validity", "a participant phrasing"),
    ("Business licence yangu inaisha lini?", "business_licence_validity", "code-switched"),
], 1):
    add(f"d17_rt_{i:02d}", "route", q, "", w, why)
for i, (q, why) in enumerate([
    ("Return ya kodi ya mapato ya kampuni ni lini?", "a COMPANY return: its own fact and guard"),
    ("Kampuni yangu ya mtu binafsi return ya kodi ya mapato ni lini?", "a company named: vetoed"),
    ("Return ya VAT ni lini?", "VAT"),
    ("Nimechelewa kuwasilisha return ya kodi ya mapato ya mtu binafsi, adhabu ni nini?", "a PENALTY question"),
    ("Return ya PAYE ya mtu binafsi?", "PAYE"),
    ("Kodi ya mapato ya mtu binafsi ni asilimia ngapi?", "a RATE question has no 'return'"),
    ("Ada ya leseni ya biashara ni kiasi gani?", "a FEE question"),
    ("Leseni ya biashara nipate wapi?", "an application question"),
    ("Leseni ya biashara inahitaji TIN?", "TIN"),
    ("Mgeni anaweza kupata leseni ya biashara?", "a foreigner (GN 487A)"),
    ("Nimechelewa kuhuisha leseni ya biashara, adhabu ni nini?", "a PENALTY question"),
    ("Nahitaji leseni ya biashara na kusajili kampuni, ni hatua gani?", "a process question"),
    ("Leseni ya udereva inaisha lini?", "not a business licence"),
    ("Leseni ya biashara inatolewa na nani?", "the authority question has its own row"),
    ("Leseni ya biashara na EFD zote ni lazima?", "EFD"),
    ("Nahitaji leseni ya biashara, inagharimu kiasi gani na inaisha lini?", "TWO-PART: fee + expiry (a whole-rule statement would silently drop the fee)"),
    ("Leseni ya biashara ya LGA inagharimu kiasi gani na inahuishwa lini?", "TWO-PART"),
    ("How much does an LGA business licence cost and when is it renewed?", "TWO-PART in English"),
    ("leseni yangu ya biashara inahuishwa lini? Na zimamoto wananidai cheti cha usalama, ni lazima?", "TWO-PART: a fire-safety certificate"),
], 1):
    add(f"d17_rn_{i:02d}", "route", q, "", "none", why)

if __name__ == "__main__":
    with io.open(os.path.join(HERE, "d17_batch_probes_2026_11_17.jsonl"), "w", encoding="utf-8") as f:
        for p in P:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(len(P), "probes written")
