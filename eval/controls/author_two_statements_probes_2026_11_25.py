# -*- coding: utf-8 -*-
"""Authors eval/refusal_gate/two_statements_probes_2026_11_25.jsonl: the medicines-VAT and PAYE-base statement routes, probes BOTH ways (R17; R21: a lower bound, authored by the routes' author, so the SWEEP over every held question is the other half).
`expect` is the fixed-statement topic the question must reach, `none` (no fixed statement at all) or `not:<topic>` (it may reach another route but must NOT reach this one).
    python eval/controls/author_two_statements_probes_2026_11_25.py"""
import io
import json
import os

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(REPO, "eval", "refusal_gate", "two_statements_probes_2026_11_25.jsonl")
M, PB = "vat_medicines", "paye_base"
P = []


def add(pid, q, expect, why):
    P.append({"id": pid, "question": q, "expect": expect, "guards_against": why})


# ---- medicines -------------------------------------------------------------------------------------------------------------------------------------------
add("mp_01", "Dawa zinatozwa VAT?", M, "FOUNDING SPECIMEN (live, build 37cdf9d): the model answered 'zero-rated (tozo 0%)'.")
add("mp_02", "Dawa nyingi za binadamu zinatozwa VAT au ni zero-rated?", M, "the zero-rated-or-exempt alternative, in the asker's words.")
add("mp_03", "Are medicines VAT-exempt in Tanzania?", M, "English form.")
add("mp_04", "Vifaa tiba vinatozwa VAT?", M, "medical equipment, the other half of the Schedule item.")
add("mp_05", "Dawa za mifugo zimesamehewa VAT?", M, "veterinary medicine is named by the item.")
add("mp_06", "Dawa ni zero-rated kwa VAT, sivyo?", M, "a PREMISE check: the statement is the whole rule, so it answers a wrong premise too.")
add("mp_07", "Dawa zinazouzwa nje ya nchi zinatozwa VAT?", M, "exports: the statement says an exempt-and-zero-rated supply is zero-rated, which is the right answer here.")
add("mp_08", "Nikinunua dawa naweza kudai input VAT?", M, "input credit: the statement says credit is for taxable supplies only.")
add("mp_09", "What is the VAT rate on medicines for a pharmacy?", M, "a rate ask in English.")
add("mp_10", "Dawa za TZS 5,000,000 nimeuza, VAT ni ngapi?", "none", "a FIGURE: a computation question, not a statement.")
add("mp_11", "Duka la dawa linatakiwa kusajili VAT?", "none", "REGISTRATION of a pharmacy is an exempt-only registration question the Act does not settle: the medicines statement does not answer it.")
add("mp_12", "Daktari anatozwa VAT kwenye dawa anazoagiza?", "vat_health_and_medicines", "EXPECT INVERTED 2026-11-25 (was none: a health word and a medicine word each veto the OTHER single-limb route, so no route owned a doctor-and-medicines question). The combined route vat_health_and_medicines now answers both limbs; the two single-limb routes must still NOT (exclusivity, tested in three_routes_probes hm_05/hm_06).")
add("mp_13", "Bima ya afya na dawa zinatozwa VAT?", "none", "health INSURANCE is another exempt item.")
add("mp_14", "Dawa zinazoingizwa kutoka China zinatozwa VAT na ushuru wa forodha?", "none", "IMPORTS and customs duty: the statement does not cover them.")
add("mp_15", "Faini ya kuchelewa kulipa VAT kwa duka la dawa ni nini?", "none", "a penalty.")
add("mp_16", "Duka la dawa linahitaji leseni ya TMDA na VAT?", "none", "licensing (TMDA) is a different question.")
add("mp_17", "Huduma za afya zinatozwa VAT? Na dawa je?", "vat_health_and_medicines", "EXPECT INVERTED 2026-11-25 (was none: the merged follow-up fell to the fact path and was answered with the medicines limb ONLY, live build ff68073). The combined route vat_health_and_medicines now answers both limbs.")
add("mp_18", "Daktari anayetoa huduma za kitaalamu anatakiwa kusajili VAT?", "vat_medical_services", "a DOCTOR stays on the medical-services route (mutual exclusion).")
add("mp_19", "Mhandisi anatakiwa kusajili VAT bila kujali mauzo?", "vat_professional_services", "an engineer stays on the professional-services route.")
add("mp_20", "VAT ni asilimia ngapi kwa bidhaa za kawaida?", "not:" + M, "no medicine word: the standard-rate question must never reach the medicines statement.")
# ---- PAYE base -------------------------------------------------------------------------------------------------------------------------------------------
add("pp_01", "Posho ya nyumba inahesabiwa kwenye SDL, na tofauti yake na PAYE ni ipi?", PB, "FOUNDING SPECIMEN, the live TWO-LEVY question (build 37cdf9d): 'PAYE ... basic salary only'. Answered by ONE composite statement.")
add("pp_02", "PAYE inakokotolewa kwa mshahara wa msingi tu au pamoja na posho?", PB, "the single-topic form of the same question.")
add("pp_03", "Is PAYE calculated on basic salary only or on allowances too?", PB, "English form.")
add("pp_04", "Bonasi na kamisheni zinaingia kwenye PAYE?", PB, "bonus and commission are named by the Act.")
add("pp_05", "Faida zisizo za fedha (benefits in kind) zinahesabiwa kwenye PAYE?", PB, "benefits in kind: the Act includes them when quantified.")
add("pp_06", "Posho ya safari inakatwa PAYE?", PB, "travel allowance: included unless it solely reimburses expenses.")
add("pp_07", "Mshahara wangu TZS 1,200,000 na posho TZS 200,000, PAYE ni kiasi gani?", "none", "FIGURES: the PAYE engine answers this, never a statement.")
add("pp_08", "PAYE ni asilimia ngapi?", "not:" + PB, "a RATE/BAND question: the band-table statement or the engine, never the base statement.")
add("pp_09", "PAYE inalipwa lini?", "not:" + PB, "a DEADLINE.")
add("pp_10", "Posho ya nyumba inakatwa NSSF na PAYE?", "not:" + PB, "another levy (NSSF) is named: a different question.")
add("pp_11", "Severance inakatwa PAYE?", "not:" + PB, "severance has its own fact (severance_pay_income_tax).")
add("pp_12", "SDL inakokotolewa kwenye nini, posho zinaingia?", "sdl_base", "an SDL-only base question stays on the SDL-base route (mutual exclusion).")
add("pp_13", "Mfanyakazi asiye mkazi PAYE ni ngapi kwenye posho?", "not:" + PB, "non-residents are taxed differently.")
add("pp_14", "Fomu ya PAYE inajazwa wapi na posho zinaingia?", "not:" + PB, "a how-to / where question.")
add("pp_15", "PAYE ya mfanyakazi inakokotolewa vipi hatua kwa hatua?", "not:" + PB, "a METHOD question (the bands), which the base statement does not answer.")
add("pp_16", "Cheti cha PAYE na posho kinatolewa lini?", "not:" + PB, "a certificate and a date.")
add("pp_17", "Mshahara wa msingi ni nini?", "none", "no levy named: a definition question.")
add("pp_18", "Kodi ya mapato ya kampuni inakokotolewa kwa msingi gani?", "not:" + PB, "corporate tax, not PAYE (no PAYE word).")
with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    for r in P:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")
print(len(P), "probes ->", OUT)
